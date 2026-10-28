#!/usr/bin/env python3
"""Old-vs-new reader replay and the 100k commissioning run (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS,
hardened by CONTRACTS_REPLAY_HARDEN_OK_WITHOUT_PROOF).

    python3 src/RimMandrake/contracts/replay.py fixtures        # the fixture corpus: old / new / strict per line
    python3 src/RimMandrake/contracts/replay.py real            # today's real stores, record by record and whole
    python3 src/RimMandrake/contracts/replay.py commission [-n 100000] [--seed 1]
        each writes a JSON report under D:\\ClaudeWork\\rimmandrake\\contracts\\ and prints a summary.
        exit 0 = every record was measured on both sides and every old/new difference matches an entry of
                 fixtures/allowances.json exactly (and, for fixtures, every expectation held);
        exit 1 = an unexplained difference, a missed expectation, or a broken instrument (worker died, short output,
                 a module that did not come from the tree it should have);
        exit 2 = no unexplained difference, but something promised was UNMEASURED (an absent or empty store).

How old and new are run (GPT review contracts #1-#4): two isolated source trees are built under a temp dir -- OLD is
`git archive --base` (default the commit before contracts were wired), NEW is a copy of the working tree -- and the
same record bytes go through replay_worker.py once per tree, each in its own `python -E -P` process that can import
only from its tree. Each worker's first line names the sha256 of every reader module it imported; the parent checks
those against the git blobs at BASE and the files of the working tree, so "which code ran" is proven, not assumed.
Every record's decision (accept / refuse / skip / crash), exception class and result digest are compared; a
difference is allowed only by an allowances.json entry matching family, input class, old/new decision and exception.
STRICT = the strict contract (strict JSON on the BYTES, then contracts.models) in shadow: it decides nothing.
"""
import argparse
import base64
import collections
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)                                   # src/RimMandrake
REPO = os.path.dirname(os.path.dirname(RM))
BASE = "c8d1d12855"                                          # HEAD before the contracts wiring (2026-10-27)
OUT = "/mnt/d/ClaudeWork/rimmandrake/contracts"
WORKER = os.path.join(HERE, "replay_worker.py")
ALLOWANCES = os.path.join(HERE, "fixtures", "allowances.json")
if RM not in sys.path:
    sys.path.append(RM)
from contracts import compat as CC, jsonl as CJ  # noqa: E402
from contracts.fixtures import make_fixtures as FX  # noqa: E402

A, R, S, C = "accept", "refuse", "skip", "crash"
FAMILIES = ("close_evidence", "audits", "verdicts", "tiers_history", "ledger_events", "sessions", "testq_results",
            "testq_orphans")
#: what a tree holds: every python file under src/RimMandrake plus the json the readers load at import
PATHSPECS = (":(glob)src/RimMandrake/**/*.py", ":(glob)src/RimMandrake/rimflow/*.json",
             ":(glob)src/RimMandrake/Utils/testq/*.json")
#: worker module name -> repo path (the header check)
READERS = {"close_evidence": "src/RimMandrake/Utils/close_evidence.py", "audits": "src/RimMandrake/rimflow/audits.py",
           "arbiter_pending": "src/RimMandrake/rimflow/arbiter_pending.py",
           "dispatcher": "src/RimMandrake/rimflow/dispatcher.py", "testq": "src/RimMandrake/Utils/testq/testq.py"}
STORES = {"evidence": "/mnt/d/ClaudeWork/rimmandrake/evidence",
          "audits": "/mnt/d/ClaudeWork/rimmandrake/auditor/audits.jsonl",
          "verdicts": "/mnt/d/ClaudeWork/rimmandrake/arbiter/verdicts.jsonl",
          "cutoff": "/mnt/d/ClaudeWork/rimmandrake/arbiter/cutoff.json",
          "tiers_history": "/mnt/d/ClaudeWork/rimmandrake/arbiter_tiers/tiers_history.jsonl",
          # arbiter_tiers has not run here yet; this is the real history it wrote during review_v3_Y
          "tiers_history_copy": "/mnt/d/ClaudeWork/rimmandrake/review_v3_Y/remeasure_data/tiers_history.jsonl",
          "shards": os.path.join(REPO, "infrastructure", "state", "ledger", "events"),
          "testq": os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"),
          "sessions": "/mnt/d/ClaudeWork/rimmandrake/contracts/agents_capture_2026-10-27.json"}
TESTQ_STATES = ("pending", "running", "done", "cancelled", "orphans")


class InstrumentError(Exception):
    """The replay could not prove what it ran: never a pass, never a fail of the readers."""


def git(*args, **kw):
    return subprocess.run(["git", "-C", REPO] + list(args), check=True, capture_output=True, timeout=120, **kw).stdout


# ------------------------------------------------------------------ trees and workers

def build_old(base, dest):
    os.makedirs(dest)
    tar = git("archive", base, "--", *PATHSPECS)
    subprocess.run(["tar", "-x", "-C", dest], input=tar, check=True, timeout=120)
    return {k: hashlib.sha256(git("show", "%s:%s" % (base, p))).hexdigest() for k, p in READERS.items()}


def build_new(dest, src=None):
    """A copy of the working tree's (or `src` tree's) python + reader json. -> expected module hashes."""
    os.makedirs(dest)
    if src is None:
        names = git("ls-files", "-z", "-c", "-o", "--exclude-standard", "--", *PATHSPECS).split(b"\0")
        root = REPO
    else:
        root = src
        names = []
        for dp, _dn, fns in os.walk(os.path.join(src, "src", "RimMandrake")):
            for fn in fns:
                if fn.endswith((".py", ".json")):
                    names.append(os.path.relpath(os.path.join(dp, fn), src).encode())
    for n in names:
        if not n:
            continue
        rel = n.decode()
        s = os.path.join(root, rel)
        if os.path.isfile(s):                        # a tracked file deleted in the work tree is absent there too
            os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
            shutil.copyfile(s, os.path.join(dest, rel))
    out = {}
    for k, p in READERS.items():
        with open(os.path.join(dest, p), "rb") as f:
            out[k] = hashlib.sha256(f.read()).hexdigest()
    return out


def run_sides(trees, jobs, work, chunks=4, timeout=480):
    """Run every job through both trees, `chunks` worker processes per tree, all at once.
    trees: {"old": (tree, expected module hashes), "new": (...)}. -> {"old": [result...], "new": [...]} in job order.
    Raises InstrumentError on a dead worker, a timeout, a short or reordered output, or a module hash mismatch."""
    n = len(jobs)
    size = max(1, -(-n // chunks))
    procs = []
    for side, (tree, _mods) in trees.items():
        for k in range(0, max(n, 1), size):
            d = os.path.join(work, "%s_%d" % (side, k // size))
            os.makedirs(d)
            inp, outp = os.path.join(d, "in.jsonl"), os.path.join(d, "out.jsonl")
            with open(inp, "w", encoding="utf-8") as f:
                for j in jobs[k:k + size]:
                    f.write(json.dumps(j) + "\n")
            tmp = os.path.join(d, "tmp")
            os.makedirs(tmp)
            log = open(os.path.join(d, "worker.log"), "wb")
            p = subprocess.Popen([sys.executable, "-E", "-P", WORKER, "--tree", tree, "--input", inp, "--output",
                                  outp, "--tmp", tmp], cwd=tmp, stdout=log, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL)
            procs.append((side, k, min(size, n - k), outp, p, log, d))
    deadline = time.time() + timeout
    for side, k, cnt, outp, p, log, d in procs:
        try:
            p.wait(timeout=max(1, deadline - time.time()))
        except subprocess.TimeoutExpired:
            for q in procs:
                q[4].kill()
            raise InstrumentError("worker %s chunk %d timed out after %ds (%s)" % (side, k, timeout, d))
        finally:
            log.close()
    res = {"old": [None] * n, "new": [None] * n}
    for side, k, cnt, outp, p, log, d in procs:
        if p.returncode != 0:
            with open(os.path.join(d, "worker.log"), "rb") as f:
                tail = f.read()[-400:].decode("utf-8", "replace")
            raise InstrumentError("worker %s chunk %d exited %s: %s" % (side, k, p.returncode, tail))
        with open(outp, encoding="utf-8") as f:
            lines = [json.loads(x) for x in f]
        if not lines or lines[0].get("i") != -1:
            raise InstrumentError("worker %s chunk %d wrote no module header" % (side, k))
        want = trees[side][1]
        if lines[0]["modules"] != want:
            bad = sorted(m for m in want if lines[0]["modules"].get(m) != want[m])
            raise InstrumentError("worker %s ran readers that are not the %s tree's: %s" % (side, side, bad))
        body = lines[1:]
        if len(body) != cnt or [r["i"] for r in body] != [j["i"] for j in jobs[k:k + cnt]]:
            raise InstrumentError("worker %s chunk %d: %d results for %d jobs (or out of order)"
                                  % (side, k, len(body), cnt))
        res[side][k:k + cnt] = body
    return res


def make_trees(tmp, base, new_tree=None):
    o, n = os.path.join(tmp, "old_tree"), os.path.join(tmp, "new_tree")
    trees = {"old": (o, build_old(base, o)), "new": (n, build_new(n, new_tree))}
    if trees["old"][1] == trees["new"][1]:
        raise InstrumentError("old and new trees hold identical readers: nothing to compare (wrong --base?)")
    return trees


# ------------------------------------------------------------------ classification

def load_allowances(path=ALLOWANCES):
    with open(path, encoding="utf-8") as f:
        return {a["id"]: a for a in json.load(f)["allow"]}


def input_class(family, raw):
    """The class of input a record is, computed from its bytes alone (what an allowance is scoped to)."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "not_utf8"
    r = CJ.decode(text, need_object=family != "sessions")
    if not r.ok:
        return r.code
    if family == "ledger_events":
        ts = r.value.get("ts")
        if ts and not isinstance(ts, str):
            return "ts_nonstr"
        if isinstance(ts, str) and ts and not CC.iso_ts_ok(ts):
            return "ts_not_iso"
    if family == "audits":
        sha = r.value.get("sha")
        if isinstance(sha, str) and sha.endswith("\n"):
            return "sha_trailing_newline"
    if family in ("testq_results", "testq_orphans") and _tagged_malformed(r.value):
        return "tagged_malformed"
    return "ok"


def _tagged_malformed(res):
    """A testq result that carries the testq.result/1 tag but breaks testq's own validate_result rule (loaded from
    Utils/testq/schema.py by path: no sys.path change, nothing new in testq.py)."""
    import importlib.util
    if not isinstance(res, dict) or res.get("schema") != "testq.result/1":
        return False
    sp = importlib.util.spec_from_file_location(
        "_testq_schema_for_replay", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "Utils", "testq", "schema.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    try:
        m.validate_result(res)
    except Exception:
        return True
    return False


def compare(allow, family, cls, o, n):
    """-> None (old and new agree exactly), an allowance id, or "UNEXPLAINED"."""
    if (o["d"], o["exc"], o["out"]) == (n["d"], n["exc"], n["out"]):
        return None
    for aid, a in allow.items():
        if (a["family"], a["input_class"], a["old"], a["old_exc"], a["new"], a["new_exc"]) == \
                (family, cls, o["d"], o["exc"], n["d"], n["exc"]):
            return aid
    return "UNEXPLAINED"


_CM = None


def strict(family, raw):
    """-> (accept|refuse|skip, reason): strict JSON on the record's BYTES (duplicate keys, non-finite numbers, bytes
    that are not UTF-8 all refuse), then the pydantic contract. Shadow only."""
    global _CM
    if _CM is None:
        from contracts import models
        _CM = models
    CM = _CM
    r = CJ.decode(bytes(raw), strict=True, need_object=family != "sessions")
    if not r.ok:
        return (S, r.code) if r.code == CJ.BLANK else (R, r.code)
    v = r.value
    if family == "close_evidence":
        kind, e = CM.close_evidence_kind(v)
        return (R, "; ".join(e[:2])) if kind == "fault" else (A, kind)
    model = {"audits": CM.AuditRecord, "verdicts": CM.ArbiterVerdict, "tiers_history": CM.TiersHistoryRow,
             "ledger_events": CM.LedgerEventMin, "testq_results": CM.TestqResult,
             "testq_orphans": CM.TestqResult}.get(family)
    if family == "sessions":
        e = CM.sessions_problems(v)
    elif model is None:
        raise KeyError(family)
    else:
        e = CM.errors(model, v)
    return (R, "; ".join(e[:2])) if e else (A, "")


def job(i, family, raw, **kw):
    return dict({"i": i, "family": family, "b64": base64.b64encode(raw).decode("ascii")}, **kw)


def judge_all(trees, work, recs, allow, chunks=4, timeout=480):
    """recs: [(family, raw bytes, extra job keys)] -> [row] with old/new/strict/diff per record."""
    jobs = [job(i, f, raw, **kw) for i, (f, raw, kw) in enumerate(recs)]
    res = run_sides(trees, jobs, work, chunks, timeout)
    rows = []
    for (f, raw, _kw), o, n in zip(recs, res["old"], res["new"]):
        cls = input_class(f, raw)
        st, sw = strict(f, raw)
        rows.append({"family": f, "class": cls, "old": o["d"], "new": n["d"], "old_exc": o["exc"],
                     "new_exc": n["exc"], "same_out": o["out"] == n["out"], "diff": compare(allow, f, cls, o, n),
                     "strict": st, "strict_why": sw, "old_why": o["why"], "new_why": n["why"]})
    return rows


# ------------------------------------------------------------------ fixtures

def run_fixtures(trees, work, allow, chunks=2):
    recs, exps = [], []
    for fam in FAMILIES:
        for k, (raw, e) in enumerate(FX.load_bytes(fam), 1):
            recs.append((fam, raw, {}))
            exps.append((k, e))
    rows = judge_all(trees, work, recs, allow, chunks)
    misses = []
    for row, (k, e) in zip(rows, exps):
        row.update(n=k, fixture_class=e["class"], where=e["where"], why=e["why"], allow=e.get("allow", ""))
        tag = "%s#%d %s" % (row["family"], k, e["class"])
        for key in ("old", "new", "strict"):
            if row[key] != e[key]:
                misses.append("%s: %s %s, expected %s" % (tag, key, row[key], e[key]))
        if (row["diff"] or "") != row["allow"]:
            misses.append("%s: old/new difference %r, fixture names %r" % (tag, row["diff"], row["allow"]))
    unexplained = [r for r in rows if r["diff"] == "UNEXPLAINED"]
    return {"lines": len(rows), "families": collections.Counter(r["family"] for r in rows),
            "expectation_misses": misses, "unexplained": unexplained,
            "allowed_diffs": collections.Counter(r["diff"] for r in rows if r["diff"] not in (None, "UNEXPLAINED")),
            "rows": rows}


# ------------------------------------------------------------------ real stores

def snapshot(dest):
    """Copy every live store into `dest` first, so both sides read the same bytes (a store written mid-run cannot make
    the sides differ). -> {store: path or None (absent)}."""
    snap = {}
    ev = os.path.join(dest, "evidence")
    if os.path.isdir(STORES["evidence"]):
        shutil.copytree(STORES["evidence"], ev, ignore=shutil.ignore_patterns("*.lock"))
        snap["evidence"] = ev
    for k in ("audits", "verdicts", "cutoff"):
        if os.path.isfile(STORES[k]):
            snap[k] = shutil.copyfile(STORES[k], os.path.join(dest, os.path.basename(STORES[k])))
    th = STORES["tiers_history"] if os.path.isfile(STORES["tiers_history"]) else STORES["tiers_history_copy"]
    if os.path.isfile(th):
        snap["tiers_history"] = shutil.copyfile(th, os.path.join(dest, "tiers_history.jsonl"))
        snap["tiers_history_source"] = th
    clone = os.path.join(dest, "clone")
    sh = os.path.join(clone, "infrastructure", "state", "ledger", "events")
    shutil.copytree(STORES["shards"], sh, ignore=lambda d, fs: [f for f in fs if not f.endswith(".jsonl")])
    snap["clone"] = clone
    q = os.path.join(dest, "testq")
    for st in TESTQ_STATES:
        s = os.path.join(STORES["testq"], st)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(q, st), ignore=lambda d, fs: [f for f in fs if not f.endswith(".json")])
        else:
            os.makedirs(os.path.join(q, st))
    snap["testq"] = q
    if os.path.isfile(STORES["sessions"]):
        snap["sessions"] = STORES["sessions"]
    return snap


def lines_of(path):
    with open(path, "rb") as f:
        parts = f.read().split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return parts


def real_records(snap):
    """-> ([(family, raw, extra)], {family: source note}) -- every real record of every store."""
    recs, src = [], collections.defaultdict(list)
    if "evidence" in snap:
        for fn in sorted(os.listdir(snap["evidence"])):
            if fn.endswith(".jsonl"):
                for b in lines_of(os.path.join(snap["evidence"], fn)):
                    recs.append(("close_evidence", b, {}))
                src["close_evidence"].append(fn)
    for fam, key in (("audits", "audits"), ("verdicts", "verdicts"), ("tiers_history", "tiers_history")):
        if key in snap:
            recs += [(fam, b, {}) for b in lines_of(snap[key])]
            src[fam].append(snap.get(key + "_source", STORES[key]))
    sh = os.path.join(snap["clone"], "infrastructure", "state", "ledger", "events")
    for fn in sorted(os.listdir(sh)):
        recs += [("ledger_events", b, {"seat": fn[:-6]}) for b in lines_of(os.path.join(sh, fn))]
        src["ledger_events"].append(fn)
    for st in ("done", "orphans"):
        d = os.path.join(snap["testq"], st)
        for fn in sorted(os.listdir(d)):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                doc = json.load(f)
            r = doc.get("result", doc) if st == "done" else doc
            if r is None:
                continue
            raw = json.dumps(r, ensure_ascii=False).encode("utf-8")
            recs += [("testq_results", raw, {}), ("testq_orphans", raw, {})]
        src["testq_results"].append("%s/%s" % (STORES["testq"], st))
        src["testq_orphans"].append("%s/%s" % (STORES["testq"], st))
    if "sessions" in snap:
        with open(snap["sessions"], "rb") as f:
            recs.append(("sessions", f.read().replace(b"\n", b" ").strip(), {}))
        src["sessions"].append(snap["sessions"])
    return recs, src


def whole_jobs(snap):
    w = [("close_evidence_read_all", snap.get("evidence")), ("audits_read", snap.get("audits")),
         ("tiers_read_jsonl", snap.get("tiers_history"))]
    if "verdicts" in snap:
        w.append(("verdicts_read_stores", [snap["verdicts"], snap.get("tiers_history", "/nonexistent"),
                                           snap.get("cutoff", "/nonexistent")]))
    else:
        w.append(("verdicts_read_stores", None))
    sh = os.path.join(snap["clone"], "infrastructure", "state", "ledger", "events")
    for fn in sorted(os.listdir(sh)):
        w.append(("seat_events_since", [snap["clone"], fn[:-6], ""]))
    for st in TESTQ_STATES:
        w.append(("testq_records", [snap["testq"], st]))
    return w


def run_real(trees, work, allow, chunks=4):
    snapdir = os.path.join(work, "snap")
    os.makedirs(snapdir)
    snap = snapshot(snapdir)
    rep = {"snapshot": {k: v for k, v in snap.items()}}
    # 1. the instrument canary: the fixture corpus must come out exactly as expected first
    fx = run_fixtures(trees, os.path.join(work, "canary"), allow, chunks=2)
    rep["canary"] = {"lines": fx["lines"], "expectation_misses": fx["expectation_misses"]}
    # 2. every real record through both sides
    recs, src = real_records(snap)
    rows = judge_all(trees, os.path.join(work, "records"), recs, allow, chunks)
    fams = {}
    for fam in FAMILIES:
        rs = [r for r in rows if r["family"] == fam]
        diffs = [r for r in rs if r["diff"]]
        fams[fam] = {
            "state": "MEASURED" if rs else "UNMEASURED",
            "source": src.get(fam) or "absent or empty", "records": len(rs),
            "decisions_old": collections.Counter(r["old"] for r in rs),
            "decisions_new": collections.Counter(r["new"] for r in rs),
            "identical": sum(1 for r in rs if not r["diff"]),
            "allowed_diffs": collections.Counter(r["diff"] for r in diffs if r["diff"] != "UNEXPLAINED"),
            "unexplained": [dict(r, raw=recs[i][1][:300].decode("utf-8", "replace")) for i, r in enumerate(rows)
                            if r["family"] == fam and r["diff"] == "UNEXPLAINED"][:50],
            "unexplained_count": sum(1 for r in diffs if r["diff"] == "UNEXPLAINED"),
            "strict": collections.Counter(r["strict"] for r in rs),
            "strict_refusals": collections.Counter(r["strict_why"][:160] for r in rs
                                                   if r["strict"] == R).most_common(15),
            "allowed_examples": [{"class": r["class"], "allow": r["diff"],
                                  "raw": recs[i][1][:200].decode("utf-8", "replace")}
                                 for i, r in enumerate(rows) if r["family"] == fam and r["diff"]
                                 and r["diff"] != "UNEXPLAINED"][:10]}
    rep["records"] = fams
    # 3. whole-store reads (the readers' own loops over the snapshot), decision + exception + digest
    wj = whole_jobs(snap)
    present = [(i, w, a) for i, (w, a) in enumerate(wj) if a is not None]
    res = run_sides(trees, [{"i": i, "whole": w, "arg": a} for i, w, a in present], os.path.join(work, "whole"),
                    chunks=1)
    whole = []
    for (i, w, a), o, n in zip(present, res["old"], res["new"]):
        same = (o["d"], o["exc"], o["out"]) == (n["d"], n["exc"], n["out"])
        whole.append({"read": w, "arg": a, "old": o, "new": n, "identical": same})
    for w, a in wj:
        if a is None:
            whole.append({"read": w, "arg": None, "identical": None, "state": "UNMEASURED (store absent)"})
    rep["whole"] = whole
    unexplained = sum(v["unexplained_count"] for v in fams.values()) + sum(1 for x in whole if x["identical"] is False)
    unmeasured = [f for f, v in fams.items() if v["state"] == "UNMEASURED"] + \
                 [x["read"] for x in whole if x["identical"] is None]
    rep["verdict"] = {"unexplained": unexplained, "unmeasured": unmeasured,
                      "canary_misses": len(fx["expectation_misses"])}
    return rep


# ------------------------------------------------------------------ 100k commissioning

def _mutate(rng, raw):
    """-> (mutated bytes, mutation name). Damage the way the reviews saw it, at the byte level and the JSON level."""
    k = rng.randrange(11)
    if k == 0 or not raw:
        return raw, "none"
    if k == 1:
        return raw[: rng.randrange(len(raw))], "truncate"
    if k == 2:
        i = rng.randrange(len(raw))
        return raw[:i] + rng.choice((b'"', b"{", b"]", b",", "\ufffd".encode(), b"A")) + raw[i + 1:], "char_flip"
    if k == 3:
        i = rng.randrange(len(raw))
        return raw[:i] + rng.choice((b"\xff", b"\xc3", b"\xed\xa0\x80", b"\x80")) + raw[i:], "bad_bytes"
    if k == 4:
        return rng.choice((b"\xef\xbb\xbf" + raw, raw + b"\r")), "bom_or_cr"
    if k == 5 and raw.endswith(b"}"):
        return raw[:-1] + rng.choice((b', "ts": "2026-10-27T12:00:00Z"}', b', "seat": "OWNER"}', b', "x": 1e999}',
                                      b', "x": NaN}')), "dup_key_or_nonfinite"
    try:
        d = json.loads(raw)
    except (ValueError, RecursionError):
        return raw, "none"
    if not isinstance(d, dict) or not d:
        return raw, "none"
    key = rng.choice(sorted(d))
    if k == 6:
        d.pop(key)
        return json.dumps(d).encode(), "drop_field"
    if k in (7, 8):
        d[key] = rng.choice((None, 0, 1.5, True, False, [], {}, "", "x" * 3, [None], 10 ** 30, -1))
        return json.dumps(d).encode(), "retype_field"
    if k == 9:
        return json.dumps(d).encode() + json.dumps(d).encode(), "two_objects_glued"
    return json.dumps([d]).encode(), "wrap_list"


def commission_pool():
    pool = {fam: [b for b, e in FX.load_bytes(fam) if b != FX.DEEP_LINE.encode()] for fam in FAMILIES}
    ev = STORES["evidence"]
    for fn in sorted(os.listdir(ev)) if os.path.isdir(ev) else []:
        if fn.endswith(".jsonl"):
            pool["close_evidence"] += [b for b in lines_of(os.path.join(ev, fn)) if b.strip()]
    th = STORES["tiers_history_copy"]
    if os.path.isfile(th):
        pool["tiers_history"] += lines_of(th)[:400]
    sh = os.path.join(STORES["shards"], "BENCH.jsonl")
    if os.path.isfile(sh):
        pool["ledger_events"] += lines_of(sh)[-400:]
    q = os.path.join(STORES["testq"], "done")
    for fn in sorted(os.listdir(q))[:60] if os.path.isdir(q) else []:
        with open(os.path.join(q, fn), encoding="utf-8") as f:
            r = json.load(f).get("result")
        if r is not None:
            raw = json.dumps(r).encode()
            pool["testq_results"].append(raw)
            pool["testq_orphans"].append(raw)
    return pool


def commission(trees, work, allow, n, seed, chunks=6, timeout=500):
    rng = random.Random(seed)
    pool = commission_pool()
    recs, muts = [], []
    for i in range(n):
        fam = FAMILIES[i % len(FAMILIES)]
        raw, mut = _mutate(rng, rng.choice(pool[fam]))
        raw = raw.replace(b"\n", b" ")
        if i % 4999 == 0:
            raw, mut = FX.DEEP_LINE.encode(), "deep"
        recs.append((fam, raw, {}))
        muts.append(mut)
    t0 = time.time()
    rows = judge_all(trees, work, recs, allow, chunks, timeout)
    dt = time.time() - t0
    acct = collections.Counter((r["family"], "new=" + r["new"], "strict=" + r["strict"]) for r in rows)
    diffs = collections.Counter()
    examples = {}
    for r, m, (_f, raw, _k) in zip(rows, muts, recs):
        if r["diff"]:
            key = (r["family"], r["class"], r["old"], r["old_exc"] or "", r["new"], r["new_exc"] or "", r["diff"])
            diffs[key] += 1
            examples.setdefault(key, (m, raw[:200].decode("utf-8", "replace")))
    unexplained = [k for k in diffs if k[-1] == "UNEXPLAINED"]
    return {"n": n, "seed": seed, "seconds": round(dt, 1), "accounted": len(rows),
            "families": collections.Counter(r["family"] for r in rows),
            "mutations": collections.Counter(muts),
            "identical": sum(1 for r in rows if not r["diff"]),
            "outcomes": {"|".join(k): v for k, v in sorted(acct.items())},
            "old_new_diffs": [{"family": k[0], "input_class": k[1], "old": k[2], "old_exc": k[3], "new": k[4],
                               "new_exc": k[5], "allowance": k[6], "count": v, "example_mutation": examples[k][0],
                               "example": examples[k][1]} for k, v in sorted(diffs.items())],
            "unexplained_kinds": len(unexplained),
            "unexplained_records": sum(diffs[k] for k in unexplained)}


# ------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=("fixtures", "real", "commission"))
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--new-tree", help="use this source tree as NEW instead of the working tree (selftest canary)")
    ap.add_argument("--allowances", default=ALLOWANCES)
    ap.add_argument("-n", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    allow = load_allowances(a.allowances)
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="contracts_replay_")
    try:
        trees = make_trees(tmp, a.base, a.new_tree)
        work = os.path.join(tmp, "work")
        os.makedirs(work)
        if a.what == "fixtures":
            rep = run_fixtures(trees, work, allow)
            code = 1 if rep["expectation_misses"] or rep["unexplained"] else 0
            summary = "fixtures: %d lines, %d expectation misses, %d allowed old/new diffs, %d unexplained" % (
                rep["lines"], len(rep["expectation_misses"]), sum(rep["allowed_diffs"].values()),
                len(rep["unexplained"]))
        elif a.what == "real":
            rep = run_real(trees, work, allow)
            v = rep["verdict"]
            code = 1 if v["unexplained"] or v["canary_misses"] else 2 if v["unmeasured"] else 0
            nrec = sum(f["records"] for f in rep["records"].values())
            nid = sum(f["identical"] for f in rep["records"].values())
            nal = sum(sum(f["allowed_diffs"].values()) for f in rep["records"].values())
            summary = ("real: %d records (%d identical, %d allowed diffs, %d unexplained); %d whole-store reads "
                       "(%d identical); canary misses %d; UNMEASURED: %s" % (
                           nrec, nid, nal, v["unexplained"], sum(1 for x in rep["whole"] if x["identical"] is not None),
                           sum(1 for x in rep["whole"] if x["identical"]), v["canary_misses"],
                           ", ".join(v["unmeasured"]) or "none"))
        else:
            rep = commission(trees, work, allow, a.n, a.seed)
            code = 1 if rep["accounted"] != a.n or rep["unexplained_records"] else 0
            summary = "commission: %d records, %d accounted, %d identical, %d allowed diffs, %d unexplained, %.1fs" % (
                a.n, rep["accounted"], rep["identical"],
                sum(d["count"] for d in rep["old_new_diffs"] if d["allowance"] != "UNEXPLAINED"),
                rep["unexplained_records"], rep["seconds"])
    except InstrumentError as e:
        rep, code, summary = {"instrument_error": str(e)}, 1, "%s: INSTRUMENT ERROR: %s" % (a.what, e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rep["base"], rep["new_tree"], rep["wall_seconds"] = a.base, a.new_tree or "working tree", round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "replay_%s_%s.json" % (a.what, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, default=str)
    word = {0: "OK", 1: "FAIL", 2: "UNMEASURED, not a pass or a fail"}[code]
    print("%s -> %s %s" % (summary, path, word))
    return code


if __name__ == "__main__":
    sys.exit(main())
