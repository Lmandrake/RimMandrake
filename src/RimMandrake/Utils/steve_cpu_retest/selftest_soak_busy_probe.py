#!/usr/bin/env python3
"""selftest_soak_busy_probe.py - the soak's Busy() sees a testq job without WSL
(RIMMANDRAKE_UNBLIND_SOAK_WORKER_PROBE_SYSTEM_SEES_NO_DISTRO).

2026-11-18T01:29:32Z the soak's PROBES line read worker_probe=blind whoami=nt authority\\system: Busy() asked
`wsl.exe ... worker.py status`, and SYSTEM cannot reach the user's runner distro, so only a running RimWorldWin64 could
make the soak wait. The worker already keeps its state on D: (TESTQ_HOME D:\\RimTest\\testq): `current` names the
attempt, and an attempt with no result.json and a state.json under 120 s old is running (worker.attempt_state).
Here Busy() is cut out of steve_cpu_soak.ps1 and run by Windows PowerShell on a temp testq home; Get-Process is stubbed so
a real RimWorld on this machine cannot decide a case. Needs powershell.exe (Archmagi WSL): without it the test says
UNMEASURED and exits 2, never a pass."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PS1 = os.path.join(HERE, "steve_cpu_soak.ps1")
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def winpath(p):
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, check=True).stdout.strip()


def busy(home_win):
    text = open(PS1, encoding="utf-8").read()
    m = re.search(r"^function Busy\(\)\{.*?^  return '' \}", text, re.S | re.M)
    if not m:
        return None, "NO_FUNCTION"
    script = ("function Get-Process { param($Name, $ErrorAction) @() }\n$TestqHome='%s'\n$script:probe='unset'\n%s\n"
              "$w=Busy; Write-Output ('WHY=' + $w + '|PROBE=' + $script:probe)" % (home_win, m.group(0)))
    r = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True,
                       timeout=120)
    out = (r.stdout + r.stderr).replace("\r", "")
    got = re.search(r"WHY=(.*)\|PROBE=(\S*)", out)
    return (got.group(1), got.group(2)) if got else (None, out[-300:])


def main():
    if not os.path.exists(PS):
        print("UNMEASURED: no powershell.exe at %s; this test needs Windows PowerShell" % PS)
        return 2
    root = os.environ.get("SOAK_PROBE_TMP") or "/mnt/d/ClaudeWork/scratch"
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="soak_busy_", dir=root)
    try:
        home = os.path.join(tmp, "testq")
        aid = "J20261119T000000Z-abcdef.a1"
        ad = os.path.join(home, "attempts", aid)
        os.makedirs(ad)
        w = winpath(home)

        why, probe = busy(w)
        check(why == "" and probe == "answered", "no current attempt: not busy, and the probe answered (%r %r)" % (why, probe))

        open(os.path.join(home, "current"), "w").write(aid)
        open(os.path.join(ad, "state.json"), "w").write('{"phase": "run"}')
        why, probe = busy(w)
        check(probe == "answered" and why and "busy" in why and aid in why,
              "a running attempt (fresh heartbeat, no result) makes the soak wait: %r %r" % (why, probe))

        old = time.time() - 600
        os.utime(os.path.join(ad, "state.json"), (old, old))
        why, probe = busy(w)
        check(why == "" and probe == "answered", "an attempt whose heartbeat stopped 10 min ago is dead, not a job: %r" % why)

        os.utime(os.path.join(ad, "state.json"), None)
        open(os.path.join(ad, "result.json"), "w").write("{}")
        why, probe = busy(w)
        check(why == "", "a finished attempt (result.json) is not a job: %r" % why)

        why, probe = busy(winpath(tmp) + "\\no_such_testq_home")
        check(why == "" and probe == "blind", "a testq home that is not there leaves the probe blind, said so: %r %r"
              % (why, probe))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
