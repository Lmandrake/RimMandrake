#!/usr/bin/env python3
"""arena_answer_check: ONE plain check that the answers live where an arm cannot read them.

Owner 2026-10-30: "Just keep secrets in a store it can't access and be done with it". Threat model: non-adversarial
models; no attack probe here (that is arm_sandbox.probe). For each answer store this picks a real file the HARNESS can
read (fixes, hidden checks, item prose, the harness event token, transcripts, notes), then runs one plain python
inside arm_sandbox.wrap (the exact sandbox every arm gets, net="none") that tries to open each one, and prints a
pass/fail table. A store with no file today is UNMEASURED, never a pass. A control file in the arm's own scratch
must be readable inside, or the whole check is void (an instrument that sees nothing passes everything).

  python3 src/RimMandrake/Utils/arena/arena_answer_check.py            # table; exit 0 only when every row passes
  python3 src/RimMandrake/Utils/arena/arena_answer_check.py --json      # (1 on FAIL/VOID, 2 when some UNMEASURED)

On the gate (ARENA_ANSWER_CHECK_FIX_STALE_ROWS_UNGATED): every run writes its result to <arena>/judge/answer_check.json
(record_path, judge-only) with a fingerprint of the task and judge files it ran against. `arena_tasks.py freeze` and
`refreeze` call gate() and REFUSE unless that record exists, matches the CURRENT task/judge files and target list (a
census since the check makes it stale: rerun this after every census), has a readable control, no FAIL/VOID row and
a MEASURED judge-hidden row. The judge-hidden row reads arena_tasks' own judge dir (the census writes there), not the
replay root.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arm_sandbox as AS  # noqa: E402
import arena_replay as R  # noqa: E402

SCHEMA = "arena_answer_check/1"
COVERED = {"bench", "foundry", "store.git", "mirror.git", "arena", "retired-trees"}   # rows of their own below
MUST_MEASURE = {"judge hidden checks"}   # the census writes it: UNMEASURED there means the check ran too early

READER = r'''
import json, os, sys
out = {}
for p in json.loads(sys.argv[1]):
    try:
        if os.path.isdir(p):
            os.listdir(p)
        else:
            with open(p, "rb") as f:
                f.read(1)
        out[p] = "readable"
    except OSError as e:
        out[p] = type(e).__name__
print("ANSWER_CHECK " + json.dumps(out))
'''


def _first(*patterns):
    """The first existing path among the glob patterns (sorted), else the first pattern itself (will be UNMEASURED)."""
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    return patterns[0]


def _token_path():
    import arena_eventlog as E
    return str(E.token_path({}))


def _tasks_paths():
    import arena_tasks as T
    return T.paths()


def targets():
    """(store, what, path): one real file per answer store, the harness side of each must be readable."""
    home = str(AS._home())
    arena = str(R.arena_root())
    tp = _tasks_paths()
    rm = AS.RM_ROOT
    mirror = "/mnt/d/Luke/dev/RimMandrake"
    t = [
        ("fixes", "retired pre-rewrite clone (refs/arena/old)", _first(R.RETIRED_TREES + "/*/packed-refs",
                                                                       R.RETIRED_TREES + "/*/HEAD")),
        ("fixes", "live clone bench", rm + "/bench/.git/HEAD"),
        ("fixes", "live clone foundry", rm + "/foundry/.git/HEAD"),
        ("fixes", "store.git", rm + "/store.git/HEAD"),
        ("fixes", "mirror.git", rm + "/mirror.git/HEAD"),
        ("fixes", "D:\\ mirror", mirror + "/CLAUDE.md"),
        ("fixes", "arena private mirror", _first(str(R.private_dir()) + "/*/HEAD", str(R.private_dir()))),
        ("hidden tests", "judge hidden checks", _first(str(tp["judge"]) + "/*.json")),
        ("hidden tests", "freeze authority", str(tp["freeze"])),
        ("hidden tests", "judge records (diff, prompt, verdict)", _first(arena + "/judge/*/verdict.json",
                                                                         arena + "/judge/*/diff.patch")),
        ("item prose", "bench items", _first(rm + "/bench/infrastructure/state/items/*.md")),
        ("item prose", "foundry items", _first(rm + "/foundry/infrastructure/state/items/*.md")),
        ("item prose", "D:\\ mirror items", _first(mirror + "/infrastructure/state/items/*.md")),
        ("item prose", "ledger shards", _first(rm + "/foundry/infrastructure/state/ledger/events/*.jsonl")),
        ("event token", "arena harness event token", _token_path()),
        ("transcripts", "~/.claude/projects", _first(home + "/.claude/projects/*/*.jsonl", home + "/.claude/projects")),
        ("notes", "D:\\ClaudeWork", AS.CLAUDEWORK),
    ]
    try:                                         # every other store beside the clones (arena-vet, dispatch, scratch...)
        sib = sorted(x for x in os.listdir(rm) if x not in COVERED and not x.startswith("."))
    except OSError:
        sib = []
    for x in sib:
        t.append(("sibling", "rm/" + x, _first(rm + "/" + x + "/.git/HEAD", rm + "/" + x + "/HEAD", rm + "/" + x)))
    return t


def record_path(p=None) -> Path:
    return (p or _tasks_paths())["freeze"].parent / "answer_check.json"


def fingerprint(p=None) -> str:
    """sha256 over every task and judge-hidden file (name + content): a census that changes either moves it."""
    p = p or _tasks_paths()
    h = hashlib.sha256()
    for d in (p["tasks"], p["judge"]):
        for f in (sorted(Path(d).glob("*.json")) if Path(d).is_dir() else []):
            h.update(("%s/%s\0" % (Path(d).name, f.name)).encode() + hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def targets_sha(rows) -> str:
    return hashlib.sha256(json.dumps([[r["store"], r["what"], r["path"]] for r in rows]).encode()).hexdigest()


def record(rows, control_ok, p=None, now=None) -> Path:
    rp = record_path(p)
    rp.parent.mkdir(parents=True, exist_ok=True)
    doc = {"schema": SCHEMA, "ts": now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "fingerprint": fingerprint(p), "targets_sha256": targets_sha(rows), "control_ok": control_ok, "rows": rows}
    tmp = rp.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, rp)
    return rp


def gate(p=None) -> list:
    """-> the reasons a freeze must refuse ([] = the answer check is current and passing). Never raises."""
    rp = record_path(p)
    rerun = "; rerun `python3 src/RimMandrake/Utils/arena/arena_answer_check.py` (after the census, before freeze)"
    try:
        doc = json.loads(rp.read_text())
    except FileNotFoundError:
        return ["no answer check on record (%s)%s" % (rp, rerun)]
    except (OSError, ValueError) as e:
        return ["answer check record %s unreadable (%s)%s" % (rp, e, rerun)]
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or not isinstance(doc.get("rows"), list):
        return ["answer check record %s has the wrong schema%s" % (rp, rerun)]
    bad = []
    try:
        if doc.get("fingerprint") != fingerprint(p):
            bad.append("answer check of %s is STALE: task/judge files changed since (a census ran after it)" % doc.get("ts"))
        if doc.get("targets_sha256") != targets_sha([{"store": s, "what": w, "path": x} for s, w, x in targets()]):
            bad.append("answer check of %s is STALE: the answer stores it probed are not today's" % doc.get("ts"))
    except Exception as e:                       # noqa: BLE001 - an unmeasurable freshness is a refusal
        bad.append("answer check freshness unmeasurable (%s: %s)" % (type(e).__name__, e))
    if doc.get("control_ok") is not True:
        bad.append("answer check control was not readable inside: the check was VOID")
    for r in doc["rows"]:
        res = r.get("result") if isinstance(r, dict) else None
        if res in ("FAIL", "VOID") or (res != "PASS" and r.get("what") in MUST_MEASURE):
            bad.append("answer check row %s / %s: %s (%s)" % (r.get("store"), r.get("what"), res, r.get("path")))
    if not any(isinstance(r, dict) and r.get("what") in MUST_MEASURE for r in doc["rows"]):
        bad.append("answer check record has no judge-hidden row")
    return bad + [rerun[2:]] if bad else []


def run(env=None, _drop=()):
    """Returns (rows, control_ok). rows: dicts store/what/path/host/inside/result. `_drop`: selftest mutation only."""
    rows = [{"store": s, "what": w, "path": p} for s, w, p in targets()]
    for r in rows:
        r["host"] = os.access(r["path"], os.R_OK)
    tmp = Path(tempfile.mkdtemp(prefix="arena_answer_check_"))
    try:
        ctl = tmp / "control.txt"
        ctl.write_text("control\n")
        probe = [r["path"] for r in rows] + [str(ctl)]
        argv, e = AS.wrap([AS.PY, "-I", "-c", READER, json.dumps(probe)], dict(os.environ if env is None else env),
                          cwd=str(tmp), rw=[str(tmp)], home=str(tmp / "home"), net="none", _drop=_drop,
                          _preflight=not _drop)
        cp = subprocess.run(argv, env=e, capture_output=True, text=True, errors="replace", timeout=120)
        seen = None
        for line in cp.stdout.splitlines():
            if line.startswith("ANSWER_CHECK "):
                seen = json.loads(line[len("ANSWER_CHECK "):])
        if seen is None:
            raise RuntimeError("the sandboxed reader did not run (rc %s): %s" % (cp.returncode,
                                                                                (cp.stdout + cp.stderr)[-400:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    control_ok = seen.get(str(ctl)) == "readable"
    for r in rows:
        r["inside"] = seen.get(r["path"], "missing")
        if not control_ok:
            r["result"] = "VOID"
        elif not r["host"]:
            r["result"] = "UNMEASURED"          # nothing there to steal today; not a pass
        else:
            r["result"] = "FAIL" if r["inside"] == "readable" else "PASS"
    return rows, control_ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows, control_ok = run()
    rp = record(rows, control_ok)
    if a.json:
        print(json.dumps({"control_ok": control_ok, "rows": rows}, indent=1))
    else:
        print("%-12s  %-42s  %-10s  %s" % ("store", "what", "result", "path (inside the arm sandbox)"))
        for r in rows:
            print("%-12s  %-42s  %-10s  %s (%s)" % (r["store"], r["what"], r["result"], r["path"], r["inside"]))
        print("control (arm's own scratch readable inside): %s" % ("ok" if control_ok else "NOT READABLE: check void"))
    bad = [r for r in rows if r["result"] in ("FAIL", "VOID")]
    un = [r for r in rows if r["result"] == "UNMEASURED"]
    print("%s: %d pass, %d fail, %d unmeasured (no file there today) of %d"
          % ("FAIL" if bad else "UNMEASURED" if un else "PASS", sum(r["result"] == "PASS" for r in rows), len(bad),
             len(un), len(rows)))
    print("recorded %s; freeze gate: %s" % (rp, "; ".join(gate()) or "open"))
    return 1 if bad else 2 if un else 0


if __name__ == "__main__":
    sys.exit(main())
