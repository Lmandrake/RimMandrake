#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_DRILL_KILL_ON_THROWAWAY_UNIT_ZERO_LIVE_KILLS.

The drill (src/RimMandrake/rimflow/control_kill_drill.py, to be written) starts a throwaway rm-probe-drill-* unit with a
child process in REAL systemd, through launch_unit on a store of its own, runs `pipe stop <unit> --kill` on it, and
prints one line `DRILL PASS <unit> killed in <N> ms; N processes gone; run recorded killed` (or DRILL FAIL with the
cause; DRILL UNMEASURED and exit 3 when systemd cannot be reached). Exit 0 here = the drill ran and passed (1 check)."""
import os
import subprocess
import sys

DRILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "control_kill_drill.py")
if not os.path.isfile(DRILL):
    print("FAIL the drill does not exist: %s" % DRILL)
    sys.exit(1)
r = subprocess.run([sys.executable, DRILL], capture_output=True, text=True, timeout=120)
line = (r.stdout.strip().splitlines() or [""])[-1]
ok = r.returncode == 0 and line.startswith("DRILL PASS ") and "recorded killed" in line
print("%s the kill drill on a real throwaway unit: rc %d, %s" % ("ok  " if ok else "FAIL", r.returncode, line or r.stderr[-200:]))
sys.exit(0 if ok else 1)
