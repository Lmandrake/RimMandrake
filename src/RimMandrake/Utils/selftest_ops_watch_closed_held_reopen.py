#!/usr/bin/env python3
"""selftest_ops_watch_closed_held_reopen.py -- SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM: a PENDING alarm whose item has
closed is never re-armed as a reopen on a pass with no crossed reading (a compose pass drops a carried reading:
crossed None), so a light beat (file_held) cannot file it on the pre-close night.

The fixture lives in selftest_alarm_stale_night_reopen.py (test_znpqoq_instance, the ninth instance, beside the other
eight of the same class). This runs that file and requires its ninth-instance lines to PASS and the file to be green,
so a run that silently drops the instance cannot read as a pass."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEED = ("found closed at 14:49:55Z with no reading this pass: not re-armed (the ninth instance)",)

r = subprocess.run([sys.executable, str(HERE / "selftest_alarm_stale_night_reopen.py")] + sys.argv[1:],
                   capture_output=True, text=True, timeout=300)
out = r.stdout.splitlines()
fails = []
for need in NEED:
    if not any(line.startswith("PASS ") and need in line for line in out):
        fails.append("no PASS line for: %s" % need)
if r.returncode != 0:
    fails.append("selftest_alarm_stale_night_reopen.py exit %d: %s" % (
        r.returncode, "; ".join(l for l in out if l.startswith("FAIL"))[:600] or r.stderr[-400:]))
for f in fails:
    print("FAIL " + f)
print("%s: %d failure(s)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
