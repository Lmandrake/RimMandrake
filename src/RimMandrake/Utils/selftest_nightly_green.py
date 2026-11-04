#!/usr/bin/env python3
"""Selftest for nightly_green.py: only whole, consecutive, recent GREEN sweeps count."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nightly_green as G  # noqa: E402

fails = 0


def check(name, cond):
    global fails
    print(("ok   " if cond else "FAIL ") + name)
    fails += 0 if cond else 1


def night(day, result="GREEN", fail=0, crash=0, total=1018, hour=11):
    return ("\n=== 2026-11-%02dT%02d:00:00Z nightly\nsome tail\nPASS %d/%d  FAIL %d/%d  UNMEASURED 2/%d  CRASH %d/%d  SKIPPED 0/%d  (wall 1.0s)\n"
            "RESULT: %s (green = FAIL 0 and CRASH 0)\nexit 0\n" % (day, hour, total - fail - crash, total, fail, total, total, crash, total, total, result))


NOW = G.known_reds.epoch("2026-11-06T12:00:00Z")


def verdict(text, want=2, now=NOW):
    return G.judge(G.read_nights(text), want, now)


check("two consecutive greens pass", verdict(night(4) + night(5) + night(6)) == [])
check("red before the last two does not matter", verdict(night(4, "RED", 3) + night(5) + night(6)) == [])
check("a red newest refuses", verdict(night(5) + night(6, "RED", 1)))
check("a red older night inside the window refuses", verdict(night(5, "RED", 0, 2) + night(6)))
check("one green alone refuses", verdict(night(6)))
check("empty log refuses", verdict(""))
check("GREEN word with a nonzero FAIL count refuses", verdict(night(5, "GREEN", 1) + night(6)))
check("a barely-run green refuses", verdict(night(5, total=12) + night(6, total=12)))
check("a stale pair refuses", verdict(night(3) + night(4)))
check("a missing night between greens refuses", verdict(night(3) + night(6)))
check("a sweep with no RESULT is not a night", G.read_nights(night(5) + "\n=== 2026-11-06T11:00:00Z nightly\nhalf a sweep\n")[-1]["at"].startswith("2026-11-05"))
check("no counts line refuses", verdict("\n=== 2026-11-05T11:00:00Z nightly\nRESULT: GREEN\n" + night(6)))

# the real script, end to end on a planted log; and on a missing log, which is no answer
with tempfile.TemporaryDirectory() as td:
    log = Path(td, "n.log")
    now_utc = time.gmtime()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", now_utc)
    prev = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 86400))
    body = "\n=== %s nightly\nPASS 1000/1000  FAIL 0/1000  UNMEASURED 0/1000  CRASH 0/1000  SKIPPED 0/1000\nRESULT: GREEN (x)\n"
    log.write_text(body % prev + body % stamp)
    argv = [sys.executable, str(HERE / "nightly_green.py"), "--log"]
    env = dict(os.environ)
    check("script exits 0 on two fresh greens", subprocess.run(argv + [str(log)], env=env, capture_output=True).returncode == 0)
    log.write_text(body % prev + (body % stamp).replace("FAIL 0/1000", "FAIL 1/1000").replace("GREEN", "RED"))
    check("script exits 1 on a red newest", subprocess.run(argv + [str(log)], env=env, capture_output=True).returncode == 1)
    p = subprocess.run(argv + [str(Path(td, "absent"))], env=env, capture_output=True, text=True)
    check("script exits 1 and says UNMEASURED on a missing log", p.returncode == 1 and "UNMEASURED" in p.stdout)

print("RESULT:", "FAIL" if fails else "PASS")
sys.exit(1 if fails else 0)
