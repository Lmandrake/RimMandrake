#!/usr/bin/env python3
"""selftest_enact_vacuity_mutants.py: the enact selftests' NEGATIVE checks bite (ENACT_STALE_LANE_FIX_VACUOUS_CHECKS).

A check like `not any(i["row"] == "RM_Foo" for i in P["install"])` or `not retired` passes just as well when the
code under test is broken as when it works, if what it inspects is empty for an unrelated reason. selftest_enact_stale_lane
had 4+3 such checks at HEAD after the 2026-10-26 newest-mark-wins rule. The 2026-11-05 audit of the other 13 enact selftests
(ENACT_SELFTEST_VACUITY_AUDIT.md) found every empty-collection negative paired with a positive, and three gaps where the
pairing proved the fixture but not the negative itself. This test closes them by MUTATION: each case rewrites one line of
the module under test in memory, runs the real selftest against it, and requires that selftest to print the named
FAIL line. The unmutated run must pass. A mutation anchor that is no longer in the source fails the case by name, so a
refactor cannot quietly turn a mutant into a no-op.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (test, module, anchor (must occur exactly once), replacement, FAIL text the mutated run must print, what it proves)
CASES = [
    ("selftest_enact_apply_whole_pick.py", "enact",
     'elif rt.get("gate") and not any((rt["row"], lt) in ok_picks for lt in rt["gate"]):',
     'elif False:',
     "FAIL folder pick refused: variant lands, folder does not shed",
     "`not retired` sees L.retire: with the folder gate gone the refused pick's folder sheds and the check fails"),
    ("selftest_enact.py", "enact",
     'for this row; re-confirm it on the current sheet")\n            continue',
     'for this row; re-confirm it on the current sheet")',
     "FAIL a stale row after a catch row is still a CONFLICT",
     "the `not any(install RM_Foo)` half bites: a stale row that is flagged but still processed installs and fails"),
    ("selftest_enact_selfpurge.py", "ingest",
     'shas = sorted({s for s in cols[dec].values() if s} - xed)',
     'shas = sorted({s for s in cols[dec].values() if s})',
     "FAIL ingest's keep RM_Beet/",
     "the keep loop's check runs on RM_Beet: a keep that names its own ✕'d facing fails it"),
]

RUNNER = r"""
import importlib.util, runpy, sys
here, mod, test, anchor, repl = sys.argv[1:6]
sys.path.insert(0, here)
src = open(f"{here}/{mod}.py", encoding="utf-8").read()
n = src.count(anchor)
if n != 1:
    print(f"MUTANT-ANCHOR {n} occurrences of the anchor in {mod}.py (need exactly 1)")
    sys.exit(97)
spec = importlib.util.spec_from_loader(mod, loader=None, origin=f"{here}/{mod}.py")
m = importlib.util.module_from_spec(spec)
m.__file__ = f"{here}/{mod}.py"
sys.modules[mod] = m
exec(compile(src.replace(anchor, repl), m.__file__, "exec"), m.__dict__)
sys.argv = [f"{here}/{test}"]
runpy.run_path(f"{here}/{test}", run_name="__main__")
"""

FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run(args, timeout=300):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=str(HERE))
    return p.returncode, p.stdout + p.stderr


def main():
    for test, mod, anchor, repl, want, proves in CASES:
        rc0, out0 = run([sys.executable, str(HERE / test)])
        check(rc0 == 0, f"{test} passes on the real {mod}.py (exit {rc0})")
        rc, out = run([sys.executable, "-c", RUNNER, str(HERE), mod, test, anchor, repl])
        if rc == 97:
            check(False, f"{test}: mutation anchor gone from {mod}.py — rewrite the case ({out.strip()[:200]})")
            continue
        check(rc != 0 and any(ln.startswith(want) for ln in out.splitlines()),
              f"{test} under the {mod}.py mutant prints '{want}' (exit {rc}): {proves}")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
