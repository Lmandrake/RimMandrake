#!/usr/bin/env python3
"""selftest_fault_monitor_route.py - fault_monitor.ps tries a second route only when direct ssh gave no answer and
STEVE_FALLBACK_SSH names one (RIMMANDRAKE_ROUTE_SOAK_READ_VIA_TAILNET_DESKTOP_SEES_NOTHING). subprocess.run is faked: no ssh runs."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fault_monitor as F

fails = []
def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok: fails.append(what)

class R:
    def __init__(s, rc, out=""): s.returncode, s.stdout = rc, out

def run_with(answers, env):
    seen = []
    def fake(argv, **kw):
        seen.append(argv[0])
        a = answers[min(len(seen) - 1, len(answers) - 1)]
        if isinstance(a, Exception): raise a
        return a
    subprocess.run = fake
    os.environ.pop("STEVE_FALLBACK_SSH", None)
    if env: os.environ["STEVE_FALLBACK_SSH"] = env
    return F.ps("1", timeout=5), seen

(rc, out), seen = run_with([R(255), R(0, "FROM_FALLBACK")], "route-cmd arg")
check((rc, out) == (0, "FROM_FALLBACK") and seen == ["ssh", "route-cmd"], "direct down, fallback set: the fallback answers")
(rc, out), seen = run_with([R(255), R(0, "x")], "")
check(rc is None and seen == ["ssh"], "direct down, nothing configured: rc None (could not look), no guessed route")
(rc, out), seen = run_with([R(255), R(255)], "route-cmd")
check(rc is None and len(seen) == 2, "both routes down: rc None, never a reading")
(rc, out), seen = run_with([R(0, "DIRECT")], "route-cmd")
check((rc, out) == (0, "DIRECT") and seen == ["ssh"], "direct answers: the fallback is not tried")
(rc, out), seen = run_with([subprocess.TimeoutExpired("ssh", 5), R(0, "FB")], "route-cmd")
check((rc, out) == (0, "FB"), "a direct timeout also falls back")
print("%d FAIL" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
