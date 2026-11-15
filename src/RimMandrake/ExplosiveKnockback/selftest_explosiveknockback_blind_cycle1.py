#!/usr/bin/env python3
"""The blind challenge's own tests for Explosive Knockback 0.1.0, cycle 1, consolidated as a formal selftest.
Runs blind lane 1 (game-logic properties, random cases with shrinking, the shipped settings swept; compiled against the
shipped kernel) and the static wiring check of the two Problems cycle 1 fixed (goods fly wild; the gas goods cap is not
rescaled by the weapons' cap scale). Record: design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_1/.
    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blind_cycle1.py     exit 0 = both green"""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CYCLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_1")
out = os.path.join(tempfile.gettempdir(), "ek_blind_cycle1_rows.jsonl")
a = subprocess.run([sys.executable, os.path.join(CYCLE, "lane1", "run_lane1.py"), "--out", out], capture_output=True, text=True)
b = subprocess.run([sys.executable, os.path.join(CYCLE, "lane2", "check_fix_wiring.py")], capture_output=True, text=True)
last = lambda p: ([l for l in (p.stdout + p.stderr).splitlines() if l.strip()] or ["no output"])[-1]
print("lane1:", (a.stdout.splitlines() or ["no output"])[0][:120], "| rc", a.returncode)
print("wiring:", last(b), "| rc", b.returncode)
ok = a.returncode == 0 and b.returncode == 0
print("explosive knockback blind cycle 1: %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
