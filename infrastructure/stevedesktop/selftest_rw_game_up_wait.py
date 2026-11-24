#!/usr/bin/env python3
"""rw_game.sh `up --wait` waits long enough for a cold load on SteveDesktop, and the worker's load timeout outlasts it
(RIMMANDRAKE_DISABLE_STEVE_SONIC_STUDIO_DRIVER_SOUND_IS_UNUSED). Measured 2026-11-21: 9 DONE cold loads since 10-31 took
473-574 s (the load phase); the brake canary J20261121T205538Z-b4095c timed out at the old 600 s cap with the game still
reading defs and the machine clean. So the default wait must be at least twice the longest DONE load (1148 s), and the
worker's `sh(cmd, timeout=...)` for `init && up --wait` must exceed that wait (init and Steam come before it). No game is touched."""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SH = os.path.join(ROOT, "infrastructure/stevedesktop/rw_game.sh")
WORKER = os.path.join(ROOT, "infrastructure/stevedesktop/worker.py")
LONGEST_DONE_LOAD_S = 574
fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


up = subprocess.run(["sed", "-n", "/^up() {/,/^}/p", SH], capture_output=True, text=True, check=True).stdout
m = re.search(r'-lt "?\$\{RW_UP_WAIT_S:-(\d+)\}"?', up)
check("up --wait reads its cap from RW_UP_WAIT_S", bool(m))
wait = int(m.group(1)) if m else 600
check("default wait %d s >= 10x the longest DONE cold load (%d s)" % (wait, 10 * LONGEST_DONE_LOAD_S), wait >= 10 * LONGEST_DONE_LOAD_S)
check("the TIMEOUT line names the wait it used", "RW_UP_WAIT_S" in up.split("TIMEOUT", 1)[-1].split("\n", 1)[0])
src = open(WORKER).read()
lm = re.search(r'^LOAD_TIMEOUT_S = (\d+)\b', src, re.M)
check("worker has LOAD_TIMEOUT_S", bool(lm))
wt = int(lm.group(1)) if lm else 0
check("every load in worker.py uses LOAD_TIMEOUT_S", "self.sh(cmd, timeout=LOAD_TIMEOUT_S)" in src
      and not re.search(r'self\.sh\(cmd, timeout=\d+\)', src))
check("worker load timeout %d s > rw_game wait %d s + 120 s for init and Steam" % (wt, wait), wt > wait + 120)
print("\n%d failed" % len(fails))
sys.exit(1 if fails else 0)
