#!/usr/bin/env python3
"""arena_answer_check: ONE plain check that the answers live where an arm cannot read them.

Owner 2026-10-30: "Just keep secrets in a store it can't access and be done with it". Threat model: non-adversarial
models; no attack probe here (that is arm_sandbox.probe). For each answer store this picks a real file the HARNESS can
read (fixes, hidden checks, item prose, the harness event token, transcripts, notes), then runs one plain python
inside arm_sandbox.wrap (the exact sandbox every arm gets, net="none") that tries to open each one, and prints a
pass/fail table. A store with no file today is UNMEASURED, never a pass. A control file in the arm's own scratch
must be readable inside, or the whole check is void (an instrument that sees nothing passes everything).

  python3 src/RimMandrake/Utils/arena/arena_answer_check.py            # table; exit 0 only when every row passes
  python3 src/RimMandrake/Utils/arena/arena_answer_check.py --json
"""
from __future__ import annotations

import argparse
import glob
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


def targets():
    """(store, what, path): one real file per answer store, the harness side of each must be readable."""
    home = str(AS._home())
    arena = str(R.arena_root())
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
        ("hidden tests", "judge hidden checks", _first(arena + "/judge/hidden/*.json")),
        ("hidden tests", "judge records (diff, prompt, verdict)", _first(arena + "/judge/*/verdict.json",
                                                                         arena + "/judge/*/diff.patch")),
        ("item prose", "bench items", _first(rm + "/bench/infrastructure/state/items/*.md")),
        ("item prose", "foundry items", _first(rm + "/foundry/infrastructure/state/items/*.md")),
        ("item prose", "D:\\ mirror items", _first(mirror + "/infrastructure/state/items/*.md")),
        ("item prose", "ledger", rm + "/foundry/infrastructure/state/ledger/events.jsonl"),
        ("event token", "arena harness event token", _token_path()),
        ("transcripts", "~/.claude/projects", _first(home + "/.claude/projects/*/*.jsonl", home + "/.claude/projects")),
        ("notes", "D:\\ClaudeWork", AS.CLAUDEWORK),
    ]
    return t


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
          % ("PASS" if not bad else "FAIL", sum(r["result"] == "PASS" for r in rows), len(bad), len(un), len(rows)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
