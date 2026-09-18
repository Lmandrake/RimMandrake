#!/usr/bin/env python3
"""selftest_run_selftests.py — the suite harness's own classifier.

`run_one` sorts a non-zero child into UNMEASURED ("could not run here") or
FAIL ("something is wrong"). Getting that backwards in the FAIL direction only
makes noise; getting it backwards in the UNMEASURED direction hides a real
failure behind a green-looking summary, so the guard that separates them is
asserted here rather than trusted.

Fixtures are written to a temp dir and run through the real `run_one`.
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from run_selftests import UNMEASURED_PHRASE, run_one  # noqa: E402

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


CASES = (
    ("passes.py", "print('ok')\n", "PASS",
     "a child that exits 0 is a PASS"),

    ("unmeasured.py",
     f"print('dotnet.exe not found — {UNMEASURED_PHRASE}')\nraise SystemExit(1)\n",
     "UNMEASURED",
     "a non-zero child carrying the phrase could not run and is NOT a failure"),

    # The guard. A child that skips one check for want of a toolchain and then
    # genuinely fails another must read FAIL — the phrase must never launder a
    # real failure in the same file.
    ("mixed.py",
     f"print('dotnet.exe not found — {UNMEASURED_PHRASE}')\n"
     "print('FAIL something that really is broken')\nraise SystemExit(1)\n",
     "FAIL",
     "the phrase does NOT mask a real FAIL in the same output"),

    ("plain_fail.py", "print('assertion blew up')\nraise SystemExit(1)\n", "FAIL",
     "a non-zero child with no phrase is a FAIL"),

    # Exit code alone is not the signal: a child may print the phrase while
    # succeeding (selftest_codebase_health.py does exactly this, as a test
    # ABOUT unmeasured semantics), and it must stay a PASS.
    ("phrase_but_green.py", f"print('this test is about {UNMEASURED_PHRASE}')\n", "PASS",
     "a child that PASSES while quoting the phrase is still a PASS"),
)

with tempfile.TemporaryDirectory() as tmp:
    for name, body, want, what in CASES:
        p = Path(tmp) / name
        p.write_text(body)
        _, status, _, _ = run_one(p)
        eq(status, want, what)

if FAILS:
    print("FAIL selftest_run_selftests.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_run_selftests.py — UNMEASURED/FAIL classification, "
      "and the guard that stops an unmeasured child masking a real failure")
