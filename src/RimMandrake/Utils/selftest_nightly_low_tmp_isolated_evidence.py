#!/usr/bin/env python3
"""NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ: the isolated-evidence selftests must not depend on free space under /tmp.

Replays the failing night offline: each test runs with shutil.disk_usage reading 1.8 GB free, which made
`isolated_evidence.py --run` exit 2 and the test die on the journal it never wrote. Sanity probe first: the same
forced reading must trip the real guard, or this proof could not see the condition.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.join(os.path.dirname(HERE), "rimflow")
TESTS = ["selftest_isolated_evidence.py", "selftest_isolated_evidence_mut.py"]
LOW = "import shutil, types; shutil.disk_usage = lambda r: types.SimpleNamespace(free=int(1.8 * 1024 ** 3)); "
PROBE = LOW + ("import sys; sys.path.insert(0, %r); from rimflow import isolated_evidence as ie; "
               "print(shutil.disk_usage('/').free < ie.MIN_FREE)" % os.path.dirname(RIMFLOW))
RUN = LOW + "import runpy, sys; sys.argv = [sys.argv[1]]; runpy.run_path(sys.argv[0], run_name='__main__')"

probe = subprocess.run([sys.executable, "-c", PROBE], capture_output=True, text=True, timeout=120)
bad = [] if probe.stdout.strip() == "True" else ["probe: forced reading does not trip the floor: " + probe.stdout + probe.stderr[-300:]]
for t in TESTS:
    p = subprocess.run([sys.executable, "-c", RUN, os.path.join(RIMFLOW, t)], capture_output=True, text=True, timeout=300)
    print("%s rc %d under a forced 1.8 GB free" % (t, p.returncode))
    if p.returncode != 0:
        bad.append("%s rc %d: %s" % (t, p.returncode, (p.stdout + p.stderr)[-600:]))
for b in bad:
    print("FAIL", b)
print("RESULT:", "FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
