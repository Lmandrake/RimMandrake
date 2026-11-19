#!/usr/bin/env python3
"""selftest_clone_tests_leave_no_tmp.py — selftests that make git repos leave nothing in their TMPDIR when run directly
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18, of the scratch cleaner's 3,836
waiting clones: 2,236 were selftest_alpha_biomes_census.py's (5 a run), about 850 selftest_seat_restart_held.py's
(7 a run) and 116 selftest_seat_restart.py's. Each repo needs a bundle before the cleaner may delete it.

Runs each listed test once with a fresh, empty TMPDIR and reads what is left. A test that fails is a failed row here
too: it must leave nothing either way, but its own verdict is its own selftest's business."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TESTS = ["src/RimMandrake/Utils/selftest_alpha_biomes_census.py",
         "src/RimMandrake/rimflow/selftest_seat_restart_held.py",
         "src/RimMandrake/rimflow/selftest_seat_restart.py"]
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


for t in TESTS:
    base = tempfile.mkdtemp(prefix="leakcheck_")
    try:
        try:
            p = subprocess.run([sys.executable, os.path.join(REPO, t)], cwd=REPO, env=dict(os.environ, TMPDIR=base),
                               capture_output=True, text=True, timeout=420, stdin=subprocess.DEVNULL)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = None
        ok(rc == 0, "%s passes (rc %r)" % (os.path.basename(t), rc))
        rest = sorted(os.listdir(base))
        ok(rest == [], "%s leaves its TMPDIR empty (%d left, e.g. %s)" % (os.path.basename(t), len(rest), rest[:3]))
    finally:
        shutil.rmtree(base, ignore_errors=True)

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
