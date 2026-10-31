#!/usr/bin/env python3
"""arena_reader_pass.py — an independent reader judges every SCORED hidden check of every vetted survivor task
(ARENA_POOL_FIX_BUNDLED_WRONG_REASON).

A vet proves a hidden check fails at base and passes at the fix. It does not prove the check fails for the reason
the task text gives: a check bundled from a commit that did more than the task says, or one pinned to private names
or source text, fails at base for the wrong reason, and an arm that solves the task as written still fails it. So
a reader that is NOT the builder (GPT through gpt_consult.py, preferred; a fresh `claude -p` Opus call as the
fallback) reads, per task, a PACKET:

    the task text (prompt + criteria), each scored hidden check (type fix_test, as arena_judge.hidden_checks scores
    it) with its body and its failing output tail at base (from the vet cache), and a summary of the fix diff,

and answers two questions per scored check:

    (a) does the check test what the task text asks for, and could a correct solution written from the task text
        alone pass it?
    (b) is it implementation-coupled: private names, source-text anchors, file layout the task text does not name?

and a verdict per check: KEEP / UNSCORE_CHECK (this check is unfair, the task stands on its others) / DROP_TASK (the
task itself cannot be judged fairly), each with a reason. A KEEP is refused when (a) is no or (b) is yes.

    run     read every survivor without a current verdict; one JSON file per task under the results dir (default
            <arena>/judge/reader/verdicts/, judge-only: the packets hold hidden check bodies). Resumable: a task
            whose verdict file matches its packet's sha256 is skipped; a changed packet (re-vet, new body) is
            STALE and read again. `--budget` stops starting new reads after that many seconds; rerun to continue.
            A task whose base tail is not in the vet cache is NOT READY and skipped (never read blind).
    apply   verdicts -> the reader exclusion file arena_trial.py build reads (default arena_trial.
            reader_exclusions_path(): <arena>/judge/reader/exclusions.json, schema arena_reader_exclusions/1):
            a task with a DROP_TASK check, or with no scored check left after its unscores, is in "drop"; a task
            with some UNSCORE_CHECK checks and at least one KEEP is in "unscore" {task: [check path]}. Refuses while
            any survivor has no current verdict, unless --partial (the file then lists them under "pending").
    packet  print one task's packet (what the reader sees).
    status  done / stale / pending / not-ready counts.

Usage:
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py status
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py run [--reader auto|gpt|claude] [--tasks ID ...]
        [--limit N] [--budget 420] [--force] [--results DIR]
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py apply [--out PATH] [--partial] [--results DIR]
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py packet RP_<ITEM>
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402
import arena_trial as T  # noqa: E402

VERDICT_SCHEMA = "arena_reader_verdict/1"
VERDICTS = ("KEEP", "UNSCORE_CHECK", "DROP_TASK")
SCORED_TYPE = "fix_test"                # arena_judge.hidden_checks scores exactly these
TAIL_CHARS = 3000
DIFF_CHARS = 8000
BODY_CHARS = 20000
READER_TIMEOUT = 360
GPT_CONSULT = HERE.parent / "gpt_consult.py"


class ReaderError(Exception):
    pass


# ---------------------------------------------------------------- paths

def results_dir(p=None) -> Path:
    return (p or A.paths())["freeze"].parent / "reader" / "verdicts"


def _write_atomic(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------- packets

def survivors(p=None) -> list[str]:
    """Task ids with a task file AND a judge file holding at least one scored check, minus the committed pool
    exclusions (arena_tasks.load_pool_exclusions, by source item)."""
    p = p or A.paths()
    ex = A.load_pool_exclusions()
    out = []
    for f in sorted(Path(p["tasks"]).glob("*.json")):
        h = Path(p["judge"]) / f.name
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            hid = json.loads(h.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if t.get("source_item") in ex:
            continue
        if any(c.get("type") == SCORED_TYPE for c in hid.get("checks") or []):
            out.append(t["id"])
    return out


def _clip(s, n, tail=False):
    s = s or ""
    if len(s) <= n:
        return s
    return ("[... %d chars cut ...]\n" % (len(s) - n) + s[-n:]) if tail else (s[:n] + "\n[... %d chars cut ...]" % (len(s) - n))


def fix_diff_summary(repo, fix_sha, skip_paths=()) -> str:
    """`git show --stat` of the fix plus its diff outside the hidden check files, clipped to DIFF_CHARS."""
    if not fix_sha:
        return "(no fix sha recorded)"
    def g(*a):
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else "(git %s failed: %s)" % (a[0], r.stderr.strip()[:200])
    stat = g("show", "--stat", "--format=%H%n%s%n", fix_sha)
    excl = [":(exclude)" + s for s in skip_paths]
    diff = g("show", "--format=", "-U2", fix_sha, "--", ".", *excl)
    return stat.rstrip() + "\n\n" + _clip(diff, DIFF_CHARS)


def build_packet(task_id, p=None, repo=None, vet=None) -> dict:
    """The reader's whole input for one task. `vet` {vet key: record} (default: the judge's vet cache)."""
    p = p or A.paths()
    t = json.loads((Path(p["tasks"]) / (task_id + ".json")).read_text(encoding="utf-8"))
    hid = json.loads((Path(p["judge"]) / (task_id + ".json")).read_text(encoding="utf-8"))
    vet = A.read_vet_cache(A.vet_cache_path(p)) if vet is None else vet
    checks, missing = [], []
    for c in hid.get("checks") or []:
        if c.get("type") != SCORED_TYPE:
            continue
        rec = vet.get((c.get("vet") or {}).get("key") or "")
        tail = rec.get("base_tail") if rec else None
        if tail is None:
            missing.append(c["path"])
        checks.append({"path": c["path"], "command": c.get("command"), "body": _clip(c.get("body"), BODY_CHARS),
                       "base_result": (rec or {}).get("base_result"),
                       "base_tail": _clip(tail, TAIL_CHARS, tail=True) if tail is not None else None})
    return {"task": task_id, "prompt": t.get("prompt"), "criteria": t.get("criteria"), "kind": t.get("kind"),
            "fix_diff": fix_diff_summary(repo or A.REPO, hid.get("fix_sha"), [c["path"] for c in checks]),
            "checks": checks, "missing_tails": missing}


def packet_sha(packet: dict) -> str:
    return hashlib.sha256(json.dumps(packet, sort_keys=True).encode("utf-8")).hexdigest()


def render_prompt(packet: dict) -> str:
    paths = [c["path"] for c in packet["checks"]]
    parts = [
        "You are an independent reader auditing a coding benchmark. An agent is given ONLY the TASK TEXT below and "
        "must change a repository so that hidden checks pass. Each hidden check below was taken from the real fix "
        "commit; it fails before the fix and passes after it. Your job: decide whether each check is a FAIR test "
        "of the task text.",
        "", "For EACH check answer:",
        "(a) tests_task: does the check test what the task text asks for? solvable_from_text: could a correct "
        "solution written from the task text alone (without seeing the real fix) pass it?",
        "(b) coupled: is the check implementation-coupled, i.e. does it depend on private function/class/variable "
        "names, exact source text, file layout or other details the task text does not name? List them in "
        "coupled_names.",
        "Then a verdict: KEEP (fair), UNSCORE_CHECK (unfair; the task can still be judged on its other checks), or "
        "DROP_TASK (the task text cannot be judged fairly at all). KEEP is only allowed when tests_task and "
        "solvable_from_text are true and coupled is false. Give a one or two sentence reason.",
        "", "Reply with ONE JSON object and nothing else:",
        '{"checks": [{"path": "<check path>", "tests_task": true|false, "solvable_from_text": true|false, '
        '"coupled": true|false, "coupled_names": ["..."], "verdict": "KEEP|UNSCORE_CHECK|DROP_TASK", '
        '"reason": "..."}]}',
        "with exactly one entry for each of these paths: " + json.dumps(paths),
        "", "=== TASK TEXT (prompt) ===", packet.get("prompt") or "",
        "", "=== TASK CRITERIA ===", packet.get("criteria") or "",
        "", "=== FIX DIFF SUMMARY (the real fix; the agent never sees it) ===", packet["fix_diff"]]
    for i, c in enumerate(packet["checks"]):
        parts += ["", "=== CHECK %d: %s ===" % (i + 1, c["path"]), "command: %s" % (c.get("command") or ""),
                  "--- body ---", c.get("body") or "",
                  "--- output at base (before the fix; result %s), tail ---" % c.get("base_result"),
                  c.get("base_tail") or ""]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- readers

def _extract_json(text: str):
    s = (text or "").strip()
    dec = json.JSONDecoder()
    i = s.find("{")
    while i >= 0:
        try:
            obj, _ = dec.raw_decode(s, i)
            if isinstance(obj, dict) and "checks" in obj:
                return obj
        except ValueError:
            pass
        i = s.find("{", i + 1)
    raise ReaderError("no JSON object with \"checks\" in the reply (%d chars)" % len(s))


def gpt_reader(prompt: str, timeout=READER_TIMEOUT) -> str:
    with tempfile.TemporaryDirectory(prefix="reader_gpt_") as d:
        pf, of = Path(d, "prompt.md"), Path(d, "answer.md")
        pf.write_text(prompt, encoding="utf-8")
        r = subprocess.run([sys.executable, str(GPT_CONSULT), "--prompt-file", str(pf), "--out", str(of),
                            "--lockdown", "--timeout", str(timeout)],
                           capture_output=True, text=True, timeout=timeout + 60)
        if r.returncode != 0 or not of.is_file():
            raise ReaderError("gpt_consult exit %d: %s" % (r.returncode, (r.stderr or "")[-300:]))
        return of.read_text(encoding="utf-8")


def claude_reader(prompt: str, timeout=READER_TIMEOUT) -> str:
    with tempfile.TemporaryDirectory(prefix="reader_claude_") as d:
        r = subprocess.run(["claude", "-p", "--model", "opus", "--tools", "", "--no-session-persistence",
                            "--strict-mcp-config"], input=prompt, capture_output=True, text=True, cwd=d,
                           timeout=timeout)
        if r.returncode != 0 or not r.stdout.strip():
            raise ReaderError("claude -p exit %d: %s" % (r.returncode, (r.stderr or "")[-300:]))
        return r.stdout


def make_reader(kind: str, gpt=None, claude=None):
    """-> callable(prompt) -> (reply text, reader name). auto: GPT, then claude -p on a GPT failure."""
    gpt, claude = gpt or gpt_reader, claude or claude_reader
    if kind == "gpt":
        return lambda pr: (gpt(pr), "gpt")
    if kind == "claude":
        return lambda pr: (claude(pr), "claude-opus")
    if kind != "auto":
        raise ReaderError("unknown reader %r" % kind)

    def auto(pr):
        try:
            return gpt(pr), "gpt"
        except (ReaderError, OSError, subprocess.SubprocessError) as e:
            return claude(pr), "claude-opus (gpt failed: %s)" % str(e)[:120]
    return auto


# ---------------------------------------------------------------- verdicts

def validate_reply(reply: dict, packet: dict) -> list[dict]:
    """The reader's per-check rows, checked against the packet; raises ReaderError (no verdict is written)."""
    want = [c["path"] for c in packet["checks"]]
    rows = reply.get("checks")
    if not isinstance(rows, list):
        raise ReaderError("checks is not a list")
    seen, out = set(), []
    for r in rows:
        if not isinstance(r, dict) or r.get("path") not in want or r["path"] in seen:
            raise ReaderError("unknown or repeated check %r" % (r.get("path") if isinstance(r, dict) else r))
        seen.add(r["path"])
        for k in ("tests_task", "solvable_from_text", "coupled"):
            if not isinstance(r.get(k), bool):
                raise ReaderError("%s: %s is not a bool" % (r["path"], k))
        if r.get("verdict") not in VERDICTS:
            raise ReaderError("%s: verdict %r" % (r["path"], r.get("verdict")))
        if not (isinstance(r.get("reason"), str) and r["reason"].strip()):
            raise ReaderError("%s: no reason" % r["path"])
        if r["verdict"] == "KEEP" and (not r["tests_task"] or not r["solvable_from_text"] or r["coupled"]):
            raise ReaderError("%s: KEEP contradicts its own answers (a)/(b)" % r["path"])
        names = r.get("coupled_names") or []
        out.append({"path": r["path"], "tests_task": r["tests_task"], "solvable_from_text": r["solvable_from_text"],
                    "coupled": r["coupled"], "coupled_names": [str(x) for x in names] if isinstance(names, list) else [],
                    "verdict": r["verdict"], "reason": r["reason"].strip()})
    if seen != set(want):
        raise ReaderError("no verdict for %s" % sorted(set(want) - seen))
    return out


def task_verdict(rows: list[dict]) -> tuple[str, str, list]:
    """-> (task verdict, reason, [unscored paths]). DROP_TASK if any check says so or no scored check is kept."""
    drops = [r for r in rows if r["verdict"] == "DROP_TASK"]
    un = [r["path"] for r in rows if r["verdict"] == "UNSCORE_CHECK"]
    if drops:
        return "DROP_TASK", "; ".join("%s: %s" % (r["path"], r["reason"]) for r in drops), []
    if un and len(un) == len(rows):
        return "DROP_TASK", "no scored check left (all %d unscored)" % len(un), []
    if un:
        return "UNSCORE_CHECK", "%d of %d checks unscored" % (len(un), len(rows)), un
    return "KEEP", "every scored check kept", []


def read_verdict(path: Path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("schema") == VERDICT_SCHEMA else None


def state(p=None, results=None, repo=None, vet=None) -> dict:
    """{task: (status, packet, verdict-or-None)}; status done / stale / pending / not_ready."""
    p = p or A.paths()
    results = Path(results or results_dir(p))
    vet = A.read_vet_cache(A.vet_cache_path(p)) if vet is None else vet
    out = {}
    for tid in survivors(p):
        pk = build_packet(tid, p, repo, vet)
        v = read_verdict(results / (tid + ".json"))
        if pk["missing_tails"]:
            st = "not_ready"
        elif v is None:
            st = "pending"
        elif v.get("packet_sha256") != packet_sha(pk):
            st = "stale"
        else:
            st = "done"
        out[tid] = (st, pk, v)
    return out


def run(reader, p=None, results=None, repo=None, tasks=None, limit=None, budget=None, force=False, vet=None,
        log=print) -> dict:
    """Read every task that is not done; -> counts. `reader` callable(prompt) -> (text, name)."""
    p = p or A.paths()
    results = Path(results or results_dir(p))
    st = state(p, results, repo, vet)
    if tasks:
        unknown = sorted(set(tasks) - set(st))
        if unknown:
            raise ReaderError("not survivors: %s" % unknown)
    counts = {"read": 0, "skipped_done": 0, "not_ready": 0, "errors": 0, "left": 0}
    t0 = time.monotonic()
    for tid in sorted(st):
        if tasks and tid not in tasks:
            continue
        s, pk, _ = st[tid]
        if s == "not_ready":
            counts["not_ready"] += 1
            continue
        if s == "done" and not force:
            counts["skipped_done"] += 1
            continue
        if (limit is not None and counts["read"] + counts["errors"] >= limit) or \
                (budget is not None and time.monotonic() - t0 > budget):
            counts["left"] += 1
            continue
        try:
            text, name = reader(render_prompt(pk))
            rows = validate_reply(_extract_json(text), pk)
        except (ReaderError, OSError, subprocess.SubprocessError) as e:
            counts["errors"] += 1
            log("ERROR %s: %s" % (tid, e))
            continue
        tv, why, un = task_verdict(rows)
        _write_atomic(results / (tid + ".json"), {
            "schema": VERDICT_SCHEMA, "task": tid, "packet_sha256": packet_sha(pk), "reader": name,
            "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "checks": rows, "task_verdict": tv, "reason": why, "unscore": un})
        counts["read"] += 1
        log("%-13s %s (%s)" % (tv, tid, name))
    return counts


def apply(p=None, results=None, out=None, partial=False, repo=None, vet=None) -> dict:
    """Verdicts -> the reader exclusion document (written to `out`, default arena_trial.reader_exclusions_path)."""
    p = p or A.paths()
    st = state(p, results, repo, vet)
    pending = sorted(t for t, (s, _, _) in st.items() if s != "done")
    if pending and not partial:
        raise ReaderError("%d survivor(s) have no current verdict (pending/stale/not ready), e.g. %s; run first or "
                          "pass --partial" % (len(pending), pending[:5]))
    drop, unscore, keep = {}, {}, []
    for tid, (s, _, v) in sorted(st.items()):
        if s != "done":
            continue
        tv, why, un = task_verdict(v["checks"])        # recomputed: the file's own summary is not trusted
        if tv == "DROP_TASK":
            drop[tid] = "reader: " + why
        elif tv == "UNSCORE_CHECK":
            unscore[tid] = un
        else:
            keep.append(tid)
    doc = {"schema": T.READER_SCHEMA, "drop": drop, "unscore": unscore, "keep": keep, "pending": pending,
           "made_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "verdicts": str(Path(results or results_dir(p)))}
    _write_atomic(Path(out or T.reader_exclusions_path(p)), doc)
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "apply", "status", "packet"):
        s = sub.add_parser(name)
        s.add_argument("--results", help="verdicts dir (default <arena>/judge/reader/verdicts)")
        if name == "run":
            s.add_argument("--reader", default="auto", choices=("auto", "gpt", "claude"))
            s.add_argument("--tasks", nargs="+")
            s.add_argument("--limit", type=int)
            s.add_argument("--budget", type=float, default=420.0, help="start no new read after this many seconds")
            s.add_argument("--force", action="store_true", help="re-read tasks already done")
        if name == "apply":
            s.add_argument("--out", help="exclusion file (default arena_trial.reader_exclusions_path())")
            s.add_argument("--partial", action="store_true")
        if name == "packet":
            s.add_argument("task")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "run":
            print(json.dumps(run(make_reader(a.reader), results=a.results, tasks=a.tasks, limit=a.limit,
                                 budget=a.budget, force=a.force)))
        elif a.cmd == "apply":
            d = apply(results=a.results, out=a.out, partial=a.partial)
            print(json.dumps({k: len(d[k]) for k in ("drop", "unscore", "keep", "pending")}))
        elif a.cmd == "status":
            c = {}
            for s, _, _ in state(results=a.results).values():
                c[s] = c.get(s, 0) + 1
            print(json.dumps(c))
        else:
            print(render_prompt(build_packet(a.task)))
    except (ReaderError, A.ArenaError, OSError, ValueError) as e:
        print("arena_reader_pass: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
