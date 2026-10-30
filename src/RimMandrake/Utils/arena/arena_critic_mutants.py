#!/usr/bin/env python3
"""Paired-mutant calibration of a critic against a baseline reviewer
(CRITIC_CALIB_FIX_PLANTED_NOT_DETECTABLE, CRITIC_CALIB_FIX_MISS_IGNORES_REASON,
CRITIC_CALIB_MEASURE_AGAINST_TESTER_BASELINE; parent ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST).

WHY. The census-planted set (arena_critic_calib.py) scored a reject as a catch whatever it said, and its planted
defects were mostly not findable from the diff plus offline tests. Here every defect is planted BY CONSTRUCTION:

THE SET (fixtures/critic_mutant_set.json, built by `build` from fixtures/critic_mutants.json). Each mutant is one
known-good candidate of the shipped calibration set (an unmutated "original": tier A or a clean tier B, never one the
adjudication marked bad) with ONE realistic defect injected into a file of its own diff (inverted guard, wrong
variable, dropped statement, off-by-one, swallowed error, wrong default ...), recorded as an exact find/replace and a
written defect description. The mutated head is a deterministic commit object in the repo (fixed author, dates and
message, parent = the original head, no ref): `build` re-creates it and refuses if the sha moved. The originals are
copied verbatim (same cid) as the paired good controls.

OFFLINE PROOF (`proofs`): the original's and the mutant's trees are materialised exactly as a critic sees them and the
selftests the change touches are run in the critic sandbox. detect=test when one passes on the original and fails on
the mutant; otherwise detect=read (findable only by reading the diff against the spec).

RUNS (`run`): the same Critic interface and runner as arena_critic_calib (fingerprinted, resumable). `--seed-from` a
run of the SAME critic fingerprint on the shipped set copies its verdicts on the originals (they are the same
candidates, byte for byte) instead of paying for them again; each seeded record says so.

SCORING. A reject of a mutant counts as a CATCH only if its reasons identify the injected defect, judged by a blind
Opus matcher (`match`, no tools, sandboxed): it sees the reviewer's write-up (no verdict, no reviewer name, no role)
and a shuffled list of defect descriptions - the true one plus a decoy from a different candidate - and says which
the write-up identifies. Rejects of originals are matched against their mutants' defects too (control). The decoy hit
rate is the matcher's false-match rate; above MATCH_FP_MAX the reason-matched numbers are UNMEASURED.

  discrimination = P(catch | mutant) - P(reject | original)       (reason-matched; verdict-only reported alongside)
  decision      = discrimination(critic) - discrimination(baseline), on candidates both judged validly
95% intervals are percentile bootstraps clustered by ORIGINAL (a resampled original brings all its mutants), paired
across reviewers for the difference. Numbers are MEASURED only from fingerprinted runs on this set's sha.

CLI: build [--write] | proofs [--budget S] | run --critic SPEC --run ID [--seed-from RUN] [--concurrency N]
     [--budget S] | match --runs A,B [--budget S] | score --critic-run A --baseline-run B [--json]
Evidence: <arena root>/calibration/critic/mutants/ (proofs.jsonl, match.jsonl, score.json); runs beside the others.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import random
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_critic_calib as C  # noqa: E402
import arena_judge as J  # noqa: E402

A = C.A
SPEC_PATH = HERE / "fixtures" / "critic_mutants.json"
SET_PATH = HERE / "fixtures" / "critic_mutant_set.json"
COMMIT_ENV = {"GIT_AUTHOR_NAME": "candidate", "GIT_AUTHOR_EMAIL": "candidate@invalid",
              "GIT_AUTHOR_DATE": "2026-10-30T00:00:00+0000", "GIT_COMMITTER_NAME": "candidate",
              "GIT_COMMITTER_EMAIL": "candidate@invalid", "GIT_COMMITTER_DATE": "2026-10-30T00:00:00+0000"}
PROOF_TIMEOUT = 180
MATCH_TIMEOUT = 300
MATCH_FP_MAX = 0.10      # decoy hit rate above this: the matcher cannot tell defects apart; reason scores UNMEASURED
BOOT = 10000
BOOT_SEED = "critic-mutants-boot-v1"
WRITEUP_MAX = 12000     # chars of write-up the matcher sees (the END is kept: findings precede the verdict)


def evidence_root() -> Path:
    return C.calib_root() / "mutants"


# ---------------------------------------------------------------- building the set

def mutate_text(text: str, m: dict) -> str:
    """Exactly the recorded edit: refuses unless `find` occurs the recorded number of times (default once)."""
    find = m["find"]
    if not find:
        raise A.ArenaError("%s: empty find" % m["mid"])
    n = text.count(find)
    want = m.get("occurrences", 1)
    if n != want:
        raise A.ArenaError("%s: %r occurs %d times in %s, the fixture says %d" % (m["mid"], find[:60], n, m["path"], want))
    nth = m.get("nth", 1)
    i = -1
    for _ in range(nth):
        i = text.index(find, i + 1)
    return text[:i] + m["replace"] + text[i + len(find):]


def _git(repo: Path, *args, env=None, inp: bytes | None = None) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], input=inp, capture_output=True, env=env, timeout=120)
    if r.returncode:
        raise A.ArenaError("git %s: %s" % (args[0], r.stderr.decode("utf-8", "replace").strip()[:300]))
    return r.stdout.decode("utf-8", "replace")


def make_commit(repo: Path, head: str, path: str, data: bytes) -> str:
    """A commit object = `head` with `path` replaced by `data`; deterministic (fixed identity and dates), no ref."""
    mode = _git(repo, "ls-tree", head, "--", path).split()
    if not mode:
        raise A.ArenaError("%s is not in %s" % (path, head[:10]))
    with tempfile.TemporaryDirectory(prefix="mutidx-") as td:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(td) / "index"), **COMMIT_ENV)
        _git(repo, "read-tree", head, env=env)
        blob = _git(repo, "hash-object", "-w", "--stdin", env=env, inp=data).strip()
        _git(repo, "update-index", "--cacheinfo", "%s,%s,%s" % (mode[0], blob, path), env=env)
        tree = _git(repo, "write-tree", env=env).strip()
        return _git(repo, "commit-tree", tree, "-p", head, "-m", "candidate", env=env).strip()


def set_hash(cands: list) -> str:
    return hashlib.sha256(json.dumps(cands, sort_keys=True).encode()).hexdigest()


def build(spec: dict, base_set: dict, repo: Path = A.REPO, adj: dict | None = None) -> dict:
    by = {c["cid"]: c for c in base_set["candidates"]}
    bad = {cid for cid, f in ((adj or {}).get("findings") or {}).items()
           if (f.get("finding") if isinstance(f, dict) else f) in ("true_defect", "bad_candidate")}
    origs, muts, seen = {}, [], set()
    for m in spec["mutants"]:
        if m["mid"] in seen:
            raise A.ArenaError("duplicate mutant id %s" % m["mid"])
        seen.add(m["mid"])
        o = by.get(m["orig"])
        if o is None or o.get("role") != "good" or o["cid"] in bad:
            raise A.ArenaError("%s: original %s is not a clean good candidate of the shipped set" % (m["mid"], m["orig"]))
        text = _git(repo, "show", "%s:%s" % (o["head"], m["path"]))
        if m["path"] not in C.text_area(repo, o)[0]:
            raise A.ArenaError("%s: %s is not a text file of the original's own diff (in its area)" % (m["mid"], m["path"]))
        new = mutate_text(text, m)
        sha = make_commit(repo, o["head"], m["path"], new.encode("utf-8"))
        c = dict(o)
        for k in ("defect", "grade", "rework", "rework_items"):
            c.pop(k, None)
        c.update(cid=C._cid(spec["seed"], m["mid"]), head=sha, role="mutant", pair=o["cid"], mid=m["mid"],
                 mutant_kind=m["kind"], mutant_defect=m["defect"], mutant_path=m["path"])
        muts.append(c)
        origs[o["cid"]] = o
    cands = sorted(list(origs.values()), key=lambda c: c["cid"]) + muts
    return {"built_from": {"spec": spec_hash(spec), "base_set_sha256": base_set["set_sha256"]},
            "candidates": cands, "set_sha256": set_hash(cands)}


def J_changed(repo: Path, c: dict) -> set:
    return set(_git(repo, "diff", "--name-only", c["base"], c["head"]).split("\n")) - {""}


def spec_hash(spec: dict) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()


def load_mutant_set(path: Path = SET_PATH) -> dict:
    return C.load_set(path)


def pairs(doc: dict) -> dict:
    """original cid -> [mutant candidates]"""
    out: dict = {}
    for c in doc["candidates"]:
        if c.get("role") == "mutant":
            out.setdefault(c["pair"], []).append(c)
    return out


# ---------------------------------------------------------------- offline proofs

def proof_tests(repo: Path, orig: dict, mut: dict) -> list:
    """Selftests the change touches plus the mutated file's own sibling selftest, as present in the tree."""
    ch = J_changed(repo, orig)
    tests = sorted(p for p in ch if Path(p).name.startswith("selftest_") and p.endswith(".py"))
    p = Path(mut["mutant_path"])
    sib = str(p.parent / ("selftest_%s.py" % p.stem))
    if p.suffix == ".py" and sib not in tests and _git_ok(repo, "cat-file", "-e", "%s:%s" % (orig["head"], sib)):
        tests.append(sib)
    return tests


def _git_ok(repo: Path, *args) -> bool:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True).returncode == 0


def run_in_sandbox(argv: list, work: Path, tree: Path, timeout: int) -> tuple:
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(work / "home"), "LANG": "C.UTF-8", "TERM": "dumb"}
    (work / "home").mkdir(exist_ok=True)
    proc = subprocess.Popen(C.sandbox_argv(argv, work, tree), cwd="/", stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, _ = proc.communicate()
        rc = 124
    return rc, out.decode("utf-8", "replace")[-600:]


def prove_one(doc_by: dict, mut: dict, repo: Path = A.REPO, deadline: float | None = None) -> dict:
    orig = doc_by[mut["pair"]]
    rec = {"cid": mut["cid"], "mid": mut["mid"], "tests": [], "detect": "read", "heads": [orig["head"], mut["head"]]}
    tests = proof_tests(repo, orig, mut)
    if not tests:
        rec["why"] = "no selftest touches the change"
        return rec
    work = C.work_base() / ("proof-" + secrets.token_hex(6))
    work.mkdir(parents=True, mode=0o700)
    try:
        trees = {}
        for role, c in (("orig", orig), ("mut", mut)):
            text, _ = C.text_area(repo, c)
            trees[role] = J.materialise(repo, c["head"], [], work / role,
                                        tree_paths=C.critic_tree_files(repo, c["head"], text))
        for t in tests:
            row = {"test": t}
            for role in ("orig", "mut"):
                left = PROOF_TIMEOUT if deadline is None else min(PROOF_TIMEOUT, deadline - time.time())
                if left < 30:
                    raise A.ArenaError("budget spent")       # an error record is retried by the next pass
                rc, tail = run_in_sandbox(["python3", t], work, trees[role], int(left))
                if rc == 124 and left < PROOF_TIMEOUT:
                    raise A.ArenaError("budget spent mid-test")
                row[role + "_rc"], row[role + "_tail"] = rc, tail[-300:]
            rec["tests"].append(row)
            if row["orig_rc"] == 0 and row["mut_rc"] not in (0, 124):
                rec["detect"] = "test"
    except Exception as e:                                   # noqa: BLE001 -- a proof that cannot run is recorded
        rec["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return rec


def proofs(doc: dict, budget_s: float, concurrency: int = 4, repo: Path = A.REPO) -> dict:
    out = evidence_root() / "proofs.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set(latest(C.read_results(out), doc))
    by = {c["cid"]: c for c in doc["candidates"]}
    todo = [c for c in doc["candidates"] if c.get("role") == "mutant" and c["cid"] not in done]
    t_end = time.time() + budget_s
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = {}
        for c in todo:
            futs[ex.submit(_timed_prove, by, c, repo, t_end)] = c
        for f in cf.as_completed(futs):
            rec = f.result()
            if rec is None:
                continue
            rec["set_sha256"] = doc["set_sha256"]
            with open(out, "a") as fh:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    allr = latest(C.read_results(out), doc)
    return {"proved": len(allr), "of": len(todo) + len(done),
            "detect_test": sum(1 for r in allr.values() if r["detect"] == "test"), "file": str(out)}


def _timed_prove(by, c, repo, t_end):
    if time.time() > t_end - 60:
        return None
    return prove_one(by, c, repo, t_end)


def latest(recs: list, doc: dict) -> dict:
    """cid -> its proof: made on this set, or on exactly this mutant's and its original's heads (a proof depends on
    nothing else, so it survives a rebuild that added other mutants)."""
    by = {c["cid"]: c for c in doc["candidates"]}
    out = {}
    for r in recs:
        c = by.get(r.get("cid"))
        if c is None or c.get("role") != "mutant" or "error" in r:
            continue
        if r.get("set_sha256") == doc["set_sha256"] or r.get("heads") == [by[c["pair"]]["head"], c["head"]]:
            out[r["cid"]] = r
    return out


# ---------------------------------------------------------------- runs (with seeded originals)

def seed(doc: dict, critic, run_id: str, from_run: str, from_set: dict, root: Path | None = None) -> dict:
    """Copy `from_run`'s valid verdicts into run `run_id` for every candidate of this set that is BYTE-IDENTICAL in
    `from_set`, only if `from_run` was made on `from_set` (its recorded sha, which must also be from_set's own content
    hash) by a critic with THIS critic's fingerprint. `from_set` is the shipped base set (originals) or an earlier build
    of this mutant set (git show <sha>:...critic_mutant_set.json), whose unchanged mutants then carry over."""
    root = root or C.calib_root()
    src = json.loads((root / from_run / "run.json").read_text())
    fp = C.critic_fingerprint(critic)
    if src.get("critic_fingerprint") != fp:
        raise SystemExit("seed refused: %s was made by fingerprint %s, this critic is %s"
                         % (from_run, str(src.get("critic_fingerprint"))[:12], fp[:12]))
    if set_hash(from_set["candidates"]) != from_set["set_sha256"]:
        raise SystemExit("seed refused: the seed set's recorded sha does not match its content")
    if src.get("set_sha256") != from_set["set_sha256"]:
        raise SystemExit("seed refused: %s was made on set %s, not the seed set %s"
                         % (from_run, str(src.get("set_sha256"))[:12], from_set["set_sha256"][:12]))
    d = root / run_id
    d.mkdir(parents=True, exist_ok=True)
    meta = d / "run.json"
    if not meta.exists():
        meta.write_text(json.dumps({"run": run_id, "critic": critic.name, "critic_fingerprint": fp,
                                    "set_sha256": doc["set_sha256"], "seeded_from": [from_run],
                                    "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    else:
        prev = json.loads(meta.read_text())
        if prev.get("critic_fingerprint") != fp or prev.get("set_sha256") != doc["set_sha256"]:
            raise SystemExit("seed refused: run %s belongs to another critic or set" % run_id)
    have = {r["cid"] for r in C.read_results(d / "results.jsonl")}
    from_by = {c["cid"]: c for c in from_set["candidates"]}
    valid = {}
    for r in C.read_results(root / from_run / "results.jsonl"):
        if r["verdict"] in J.VERDICTS:
            valid[r["cid"]] = r
    n = 0
    with open(d / "results.jsonl", "a") as fh:
        for c in doc["candidates"]:
            if c["cid"] in have or c["cid"] not in valid or from_by.get(c["cid"]) != c:
                continue                     # absent there, or changed since: this run must judge it itself
            r = dict(valid[c["cid"]])
            m = dict(r.get("meta") or {})
            m["seeded_from"] = list(m.get("seeded_from") or []) if isinstance(m.get("seeded_from"), list) else (
                [m["seeded_from"]] if m.get("seeded_from") else [])
            m["seeded_from"].append(from_run)
            r["meta"] = m
            fh.write(json.dumps(r, sort_keys=True) + "\n")
            n += 1
    return {"seeded": n, "from": from_run}


# ---------------------------------------------------------------- the blind reason matcher

MATCH_PROMPT = """You compare a code reviewer's write-up with a list of specific software defects.

For each numbered defect, decide whether the write-up IDENTIFIES that defect: it points at the same code change (the
same file and the same faulty condition, statement, value or name) or unmistakably describes the same wrong behaviour
that this change causes. Naming only the same file or the same general area, or a different problem nearby, is NOT
identifying it. The write-up may use other words and may describe the consequence differently. Judge only from the
text; do not guess what the reviewer meant to say.

=== WRITE-UP ===
{writeup}

=== DEFECTS ===
{defects}

Answer with exactly one JSON object and nothing after it: {{"identified": [list of the numbers identified, possibly
empty]}}
"""


def writeup_of(rec: dict) -> str:
    """The reviewer's own words, without the verdict token, the reviewer's name or anything else about the run."""
    parts = [str(x) for x in (rec.get("reasons") or []) if x]
    full = (rec.get("meta") or {}).get("answer")
    if full:                                    # a reviewer that keeps its whole answer (the tester): use all of it
        parts = []
    tail = str(full or (rec.get("meta") or {}).get("answer_tail") or "")
    if tail and not any(p and p[-200:] in tail for p in parts):
        parts.append(tail)
    elif tail:
        parts = [tail] + [p for p in parts if p[-200:] not in tail]
    text = "\n".join(parts)
    text = "\n".join(ln for ln in text.splitlines() if not ln.strip().upper().startswith(("VERDICT", "**VERDICT")))
    text = text.replace('"verdict": "reject"', "").replace('"verdict": "accept"', "")
    return text[-WRITEUP_MAX:]


def match_jobs(doc: dict, runs: dict) -> list:
    """One job per valid reject: a mutant's true defect + a decoy; an original's mutants' defects + a decoy."""
    mts = [c for c in doc["candidates"] if c.get("role") == "mutant"]
    pr = pairs(doc)
    jobs = []
    for run_id, recs in runs.items():
        for cid, r in recs.items():
            if r["verdict"] != "reject":
                continue
            c = next(x for x in doc["candidates"] if x["cid"] == cid)
            if c.get("role") == "mutant":
                truths, home = [c], c["pair"]
            else:
                truths, home = pr.get(cid, []), cid
                if not truths:
                    continue
            rng = random.Random("%s|%s|decoy" % (run_id, cid))
            decoy = rng.choice([m for m in mts if m["pair"] != home])
            items = [("true", m["mid"], m["mutant_defect"]) for m in truths] + [("decoy", decoy["mid"], decoy["mutant_defect"])]
            random.Random("%s|%s|order" % (run_id, cid)).shuffle(items)
            w = writeup_of(r)
            key = hashlib.sha256(json.dumps([run_id, cid, w, items]).encode()).hexdigest()[:16]
            jobs.append({"key": key, "run": run_id, "cid": cid, "role": c.get("role"), "items": items, "writeup": w})
    return jobs


def parse_identified(text: str, n: int) -> list | None:
    dec = json.JSONDecoder()
    found = None
    i = 0
    while True:
        i = text.find("{", i)
        if i < 0:
            break
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict) and "identified" in obj:
            if found is not None and obj != found:
                return None
            found = obj
        i = end
    if found is None or not isinstance(found["identified"], list):
        return None
    out = []
    for x in found["identified"]:
        if isinstance(x, bool) or not isinstance(x, int) or not 1 <= x <= n:
            return None
        out.append(x)
    return sorted(set(out))


def opus_call(prompt: str, timeout: int, model: str = "opus", max_usd: float = 2.0) -> tuple:
    """No tools, fresh HOME, sandboxed: the matcher sees the prompt and nothing else."""
    work = C.work_base() / ("match-" + secrets.token_hex(6))
    (work / "home" / ".claude").mkdir(parents=True, mode=0o700)
    try:
        cred = Path.home() / ".claude" / ".credentials.json"
        if cred.exists():
            shutil.copy2(cred, work / "home" / ".claude" / ".credentials.json")
        argv = [shutil.which("claude") or "claude", "-p", "--model", model, "--output-format", "json", "--tools", "",
                "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
                "--max-budget-usd", str(max_usd)]
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin:" + str(Path.home() / ".local" / "bin"),
               "HOME": str(work / "home"), "LANG": "C.UTF-8", "USER": os.environ.get("USER", "u"), "TERM": "dumb"}
        proc = subprocess.Popen(C.sandbox_argv(argv, work, work), cwd="/", stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
        try:
            out, _ = proc.communicate(prompt.encode("utf-8"), timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
            return None, {"rc": 124}
        try:
            d = json.loads(out.decode("utf-8", "replace"))
        except ValueError:
            return None, {"rc": proc.returncode}
        return d.get("result") or "", {"rc": proc.returncode, "cost_usd": d.get("total_cost_usd"),
                                       "is_error": d.get("is_error")}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def match_one(job: dict, call=opus_call) -> dict:
    defects = "\n".join("%d. %s" % (i + 1, it[2]) for i, it in enumerate(job["items"]))
    text, meta = call(MATCH_PROMPT.format(writeup=job["writeup"], defects=defects), MATCH_TIMEOUT)
    ids = parse_identified(text or "", len(job["items"])) if text is not None and not meta.get("is_error") else None
    rec = {k: job[k] for k in ("key", "run", "cid", "role")}
    rec["items"] = [[it[0], it[1]] for it in job["items"]]
    rec["meta"] = meta
    if ids is None:
        rec["valid"] = False
    else:
        rec["valid"] = True
        rec["identified"] = [job["items"][i - 1][1] for i in ids]
        rec["true_hit"] = [it[1] for i, it in enumerate(job["items"]) if it[0] == "true" and (i + 1) in ids]
        rec["decoy_hit"] = any(it[0] == "decoy" and (i + 1) in ids for i, it in enumerate(job["items"]))
    return rec


def run_records(run_id: str, doc: dict, root: Path | None = None) -> dict:
    """cid -> the decisive record: the last valid verdict, else the last record (invalid)."""
    d = (root or C.calib_root()) / run_id
    meta = json.loads((d / "run.json").read_text())
    if meta.get("set_sha256") != doc["set_sha256"]:
        raise SystemExit("run %s was made on set %s, not the mutant set %s" % (run_id, meta.get("set_sha256", "")[:12],
                                                                              doc["set_sha256"][:12]))
    out: dict = {}
    for r in C.read_results(d / "results.jsonl"):
        if r["verdict"] in J.VERDICTS or out.get(r["cid"], {}).get("verdict") not in J.VERDICTS:
            out[r["cid"]] = r
    return out


def match(doc: dict, run_ids: list, budget_s: float, concurrency: int = 8, call=opus_call,
          out: Path | None = None) -> dict:
    out = out or evidence_root() / "match.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    have = {r["key"] for r in C.read_results(out) if r.get("valid")}
    jobs = [j for j in match_jobs(doc, {r: run_records(r, doc) for r in run_ids}) if j["key"] not in have]
    t_end = time.time() + budget_s
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(lambda j: None if time.time() > t_end - MATCH_TIMEOUT - 20 else match_one(j, call), j)
                for j in jobs]
        for f in cf.as_completed(futs):
            rec = f.result()
            if rec is not None:
                with open(out, "a") as fh:
                    fh.write(json.dumps(rec, sort_keys=True) + "\n")
    left = [j for j in match_jobs(doc, {r: run_records(r, doc) for r in run_ids})
            if j["key"] not in {r["key"] for r in C.read_results(out) if r.get("valid")}]
    return {"jobs_left": len(left), "file": str(out)}


# ---------------------------------------------------------------- scoring

def reviewer_table(doc: dict, recs: dict, matches: dict) -> dict:
    """original cid -> {"orig": verdict, "orig_match": bool|None, "muts": [(mid, verdict, matched|None)]}.
    verdict None = no valid verdict; matched None = a reject whose match is missing/invalid."""
    tab = {}
    for o, ms in pairs(doc).items():
        ro = recs.get(o)
        vo = ro["verdict"] if ro and ro["verdict"] in J.VERDICTS else None
        mo = matches.get(o)
        row = {"orig": vo, "orig_match": (bool(mo["true_hit"]) if mo else None) if vo == "reject" else False,
               "muts": []}
        for m in ms:
            r = recs.get(m["cid"])
            v = r["verdict"] if r and r["verdict"] in J.VERDICTS else None
            mm = matches.get(m["cid"])
            hit = (bool(mm["true_hit"]) if mm else None) if v == "reject" else False
            row["muts"].append((m["mid"], v, hit))
        tab[o] = row
    return tab


def _disc(tab: dict, keys: list, mode: str) -> float | None:
    """mode verdict: P(reject|mut) - P(reject|orig); reason: P(reject & match|mut) - P(reject|orig).
    Only mutants whose own verdict AND whose original's verdict are valid (and, in reason mode, matched) count."""
    cm = nm = co = no = 0
    for k in keys:
        row = tab[k]
        if row["orig"] is None:
            continue
        used = False
        for _mid, v, hit in row["muts"]:
            if v is None or (mode == "reason" and hit is None):
                continue
            nm += 1
            cm += (v == "reject") if mode == "verdict" else (v == "reject" and hit)
            used = True
        if used:
            no += 1
            co += row["orig"] == "reject"
    if not nm or not no:
        return None
    return cm / nm - co / no


def _rates(tab: dict, mode: str) -> dict:
    keys = list(tab)
    cm = nm = co = no = 0
    for k in keys:
        row = tab[k]
        if row["orig"] is None:
            continue
        ok = [(v, hit) for _m, v, hit in row["muts"] if v is not None and not (mode == "reason" and hit is None)]
        if not ok:
            continue
        no += 1
        co += row["orig"] == "reject"
        nm += len(ok)
        cm += sum((v == "reject") if mode == "verdict" else (v == "reject" and hit) for v, hit in ok)
    return {"catch": [cm, nm], "false_reject": [co, no]}


def boot(tabs: list, keys: list, mode: str, reps: int = BOOT, seed: str = BOOT_SEED) -> list:
    """Percentile 95% interval of disc(tabs[0]) (one table) or disc(tabs[0]) - disc(tabs[1]) (paired), resampling
    originals with replacement; a resample where a term is undefined is dropped (counted)."""
    rng = random.Random(seed + mode + str(len(tabs)))
    vals = []
    for _ in range(reps):
        ks = [rng.choice(keys) for _ in keys]
        exp = []
        for t in tabs:
            tt = {}
            for i, k in enumerate(ks):
                tt["%s#%d" % (k, i)] = t[k]
            exp.append(_disc(tt, list(tt), mode))
        if any(x is None for x in exp):
            continue
        vals.append(exp[0] if len(exp) == 1 else exp[0] - exp[1])
    if not vals:
        return [None, None, 0]
    vals.sort()
    return [round(vals[int(0.025 * (len(vals) - 1))], 3), round(vals[int(0.975 * (len(vals) - 1))], 3), len(vals)]


def restrict(tab: dict, other: dict) -> dict:
    """Keep only verdicts valid in BOTH tables (paired comparison on the same candidates)."""
    out = {}
    for k, row in tab.items():
        o = other[k]
        orig = row["orig"] if (row["orig"] is not None and o["orig"] is not None) else None
        muts = []
        for (mid, v, hit), (_m2, v2, hit2) in zip(row["muts"], o["muts"]):
            ok = v is not None and v2 is not None
            muts.append((mid, v if ok else None, hit if ok and hit2 is not None else (None if ok else hit)))
        out[k] = {"orig": orig, "orig_match": row["orig_match"], "muts": muts}
    return out


def score(doc: dict, runs: dict, match_recs: list, proofs_by: dict, reps: int = BOOT) -> dict:
    """runs: {"critic": (run_id, recs, fingerprint), "baseline": (...)}"""
    mrec = {}
    for r in match_recs:
        if r.get("valid"):
            mrec[(r["run"], r["cid"])] = r
    n_mut = sum(1 for c in doc["candidates"] if c.get("role") == "mutant")
    n_orig = len(pairs(doc))
    out = {"set_sha256": doc["set_sha256"], "mutants": n_mut, "originals": n_orig,
           "kinds": sorted({c["mutant_kind"] for c in doc["candidates"] if c.get("role") == "mutant"}),
           "detect": {"test": sum(1 for p in proofs_by.values() if p["detect"] == "test"),
                      "read": sum(1 for p in proofs_by.values() if p["detect"] == "read"),
                      "unproved": n_mut - len(proofs_by)},
           "reviewers": {}}
    tabs = {}
    for role, (run_id, recs, fp) in runs.items():
        matches = {cid: r for (rr, cid), r in mrec.items() if rr == run_id}
        tab = reviewer_table(doc, recs, matches)
        tabs[role] = tab
        jobs = [r for (rr, _c), r in mrec.items() if rr == run_id]
        invalid = sum(1 for c in doc["candidates"]
                      if not (recs.get(c["cid"]) and recs[c["cid"]]["verdict"] in J.VERDICTS))
        unmatched = sum(1 for row in tab.values() for _m, v, hit in row["muts"] if v == "reject" and hit is None)
        seeded = sum(1 for r in recs.values() if (r.get("meta") or {}).get("seeded_from"))
        blk = {"run": run_id, "critic_fingerprint": fp, "invalid": invalid, "candidates": len(doc["candidates"]),
               "seeded_originals": seeded, "rejects_without_valid_match": unmatched,
               "matcher_decoy_hits": [sum(1 for j in jobs if j["decoy_hit"]), len(jobs)],
               "orig_rejects_naming_paired_defect": sum(1 for row in tab.values() if row["orig"] == "reject"
                                                        and row["orig_match"])}
        for mode in ("verdict", "reason"):
            r = _rates(tab, mode)
            d = _disc(tab, list(tab), mode)
            blk[mode] = {"catch": r["catch"], "false_reject": r["false_reject"],
                         "discrimination": None if d is None else round(d, 3),
                         "ci95": boot([tab], list(tab), mode, reps)[:2]}
        by_detect = {}
        for det in ("test", "read"):
            hits = [(v, hit) for row in tab.values() for mid, v, hit in row["muts"] if v is not None
                    and (proofs_by.get(mid) or {}).get("detect", "read") == det]
            by_detect[det] = {"verdict_catch": [sum(v == "reject" for v, _h in hits), len(hits)],
                              "reason_catch": [sum(v == "reject" and bool(h) for v, h in hits), len(hits)]}
        blk["by_detect"] = by_detect
        kind_of = {c["mid"]: c["mutant_kind"] for c in doc["candidates"] if c.get("role") == "mutant"}
        by_kind: dict = {}
        for row in tab.values():
            for mid, v, hit in row["muts"]:
                if v is None:
                    continue
                k = by_kind.setdefault(kind_of[mid], {"verdict_catch": [0, 0], "reason_catch": [0, 0]})
                k["verdict_catch"][0] += v == "reject"
                k["reason_catch"][0] += v == "reject" and bool(hit)
                k["verdict_catch"][1] += 1
                k["reason_catch"][1] += 1
        blk["by_kind"] = dict(sorted(by_kind.items()))
        out["reviewers"][role] = blk
    if set(tabs) == {"critic", "baseline"}:
        a, b = restrict(tabs["critic"], tabs["baseline"]), restrict(tabs["baseline"], tabs["critic"])
        out["paired"] = {}
        for mode in ("verdict", "reason"):
            da, db = _disc(a, list(a), mode), _disc(b, list(b), mode)
            out["paired"][mode] = {"critic": da if da is None else round(da, 3),
                                   "baseline": db if db is None else round(db, 3),
                                   "difference": None if da is None or db is None else round(da - db, 3),
                                   "ci95": boot([a, b], list(a), mode, reps)[:2]}
    out["verdict"] = decision(out)
    return out


def decision(sc: dict) -> dict:
    why = []
    for role, blk in sc["reviewers"].items():
        if blk["invalid"] > C.MAX_INVALID_FRAC * blk["candidates"]:
            why.append("%s: %d/%d invalid" % (role, blk["invalid"], blk["candidates"]))
        k, n = blk["matcher_decoy_hits"]
        if n and k / n > MATCH_FP_MAX:
            why.append("%s: matcher decoy hits %d/%d" % (role, k, n))
        if blk["rejects_without_valid_match"]:
            why.append("%s: %d mutant rejects without a valid match" % (role, blk["rejects_without_valid_match"]))
    if why:
        return {"grade": "UNMEASURED", "why": why}
    p = (sc.get("paired") or {}).get("reason")
    if not p or p["ci95"][0] is None:
        return {"grade": "UNMEASURED", "why": ["no paired comparison"]}
    lo, hi = p["ci95"]
    if lo > 0:
        call = "critic discriminates better than the baseline"
    elif hi < 0:
        call = "critic discriminates worse than the baseline"
    else:
        call = "not distinguishable at this n (interval spans 0)"
    return {"grade": "MEASURED", "call": call}


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build")
    b.add_argument("--write", action="store_true")
    p = sp.add_parser("proofs")
    p.add_argument("--budget", type=float, default=480)
    p.add_argument("--concurrency", type=int, default=4)
    r = sp.add_parser("run")
    r.add_argument("--critic", required=True)
    r.add_argument("--run", required=True)
    r.add_argument("--seed-from", action="append", default=[],
                   help="RUN or RUN=SETFILE (default set: the shipped base set); repeatable")
    r.add_argument("--concurrency", type=int, default=8)
    r.add_argument("--max", type=int)
    r.add_argument("--budget", type=float, default=480)
    m = sp.add_parser("match")
    m.add_argument("--runs", required=True)
    m.add_argument("--budget", type=float, default=480)
    m.add_argument("--concurrency", type=int, default=8)
    s = sp.add_parser("score")
    s.add_argument("--critic-run", required=True)
    s.add_argument("--baseline-run", required=True)
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    base = C.load_set()
    if a.cmd == "build":
        adj = json.loads(C.ADJ_PATH.read_text())
        doc = build(json.loads(SPEC_PATH.read_text()), base, adj=adj)
        if SET_PATH.exists():
            old = json.loads(SET_PATH.read_text())
            if old["set_sha256"] != doc["set_sha256"]:
                print("REBUILT SET DIFFERS from the shipped one (%s -> %s)" % (old["set_sha256"][:12], doc["set_sha256"][:12]))
                if not a.write:
                    return 1
        if a.write:
            SET_PATH.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        print(json.dumps({"set_sha256": doc["set_sha256"], "candidates": len(doc["candidates"]),
                          "mutants": sum(1 for c in doc["candidates"] if c.get("role") == "mutant")}))
        return 0
    doc = load_mutant_set()
    if a.cmd == "proofs":
        print(json.dumps(proofs(doc, a.budget, a.concurrency)))
        return 0
    if a.cmd == "run":
        critic = C.load_critic(a.critic)
        for sf in a.seed_from:
            rid, _, setf = sf.partition("=")
            print(json.dumps(seed(doc, critic, a.run, rid, json.loads(Path(setf).read_text()) if setf else base)))
        print(json.dumps(C.run(doc, critic, a.run, a.concurrency, a.max, budget_s=a.budget)))
        return 0
    if a.cmd == "match":
        print(json.dumps(match(doc, a.runs.split(","), a.budget, a.concurrency)))
        return 0
    runs = {}
    for role, rid in (("critic", a.critic_run), ("baseline", a.baseline_run)):
        meta = json.loads((C.calib_root() / rid / "run.json").read_text())
        runs[role] = (rid, run_records(rid, doc), meta.get("critic_fingerprint"))
    pr = latest(C.read_results(evidence_root() / "proofs.jsonl"), doc)
    proofs_by = {r["mid"]: r for r in pr.values()}
    sc = score(doc, runs, C.read_results(evidence_root() / "match.jsonl"), proofs_by)
    (evidence_root() / "score.json").write_text(json.dumps(sc, indent=1) + "\n")
    if a.json:
        print(json.dumps(sc, indent=1))
        return 0
    print("set %s: %d mutants on %d originals; detect test %d / read %d / unproved %d" % (
        sc["set_sha256"][:12], sc["mutants"], sc["originals"], sc["detect"]["test"], sc["detect"]["read"],
        sc["detect"]["unproved"]))
    for role, blk in sc["reviewers"].items():
        print("== %s (%s) invalid %d/%d, seeded originals %d, decoy hits %s" % (
            role, blk["run"], blk["invalid"], blk["candidates"], blk["seeded_originals"], blk["matcher_decoy_hits"]))
        for mode in ("verdict", "reason"):
            x = blk[mode]
            print("  %-7s catch %d/%d  false-reject %d/%d  discrimination %s  95%% %s" % (
                mode, x["catch"][0], x["catch"][1], x["false_reject"][0], x["false_reject"][1], x["discrimination"],
                x["ci95"]))
    for mode, x in (sc.get("paired") or {}).items():
        print("paired %-7s critic %s  baseline %s  difference %s  95%% %s" % (mode, x["critic"], x["baseline"],
                                                                          x["difference"], x["ci95"]))
    print("verdict:", json.dumps(sc["verdict"]))
    print("score:", evidence_root() / "score.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
