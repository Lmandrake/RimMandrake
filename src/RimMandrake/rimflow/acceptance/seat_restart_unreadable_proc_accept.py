#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_READ_UNREADABLE_PID_AS_UNKNOWN_NOT_DEAD_YET.

seat_restart._proc_stat (55722bc0f9) now falls back to `ps` whenever /proc/<pid>/stat cannot be opened. On Linux that
mixes units: a pid whose birth was saved in /proc clock ticks is re-read in epoch seconds, so proc_alive(pid, saved)
reads False for a process that is running. And when neither /proc nor ps can be read (ps timing out), the answer is
None, which proc_alive also spells "not alive". Measured 2026-11-18 on c32e228e91 with a live `sleep` child: ticks
64169956 -> epoch 1795026013 with /proc unreadable, alive False; None with ps timing out too. "Could not look" is not
"dead" (owner, 2026-11-17): a caller that kills, reconciles or relaunches must be able to tell them apart.

Passes when, for a LIVE child, neither unreadable case makes proc_alive answer False (True, None or a named raise are
all honest answers; False is the one that is not).

    python3 src/RimMandrake/rimflow/acceptance/seat_restart_unreadable_proc_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS 2 of 2 unreadable readings are not called dead`. Linux only (needs /proc).
The builder does not edit this file.
"""
import builtins
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import seat_restart as SR  # noqa: E402

if not os.path.isdir("/proc/self"):
    print("UNMEASURED: no /proc on %s; this test needs Linux" % sys.platform)
    sys.exit(2)
child = subprocess.Popen(["sleep", "60"])
real_open, real_run, bad = builtins.open, SR.subprocess.run, []
try:
    saved = SR.proc_start(child.pid)

    def deny(path, *a, **k):
        if str(path).startswith("/proc/%d/" % child.pid):
            raise PermissionError(13, "Permission denied", str(path))
        return real_open(path, *a, **k)

    def ps_times_out(*a, **k):
        if a and list(a[0][:1]) == ["ps"]:
            raise subprocess.TimeoutExpired("ps", 10)
        return real_run(*a, **k)

    for case, patch_run in (("/proc unreadable, ps answers", None), ("/proc unreadable, ps times out", ps_times_out)):
        builtins.open = deny
        if patch_run:
            SR.subprocess.run = patch_run
        try:
            got = SR.proc_alive(child.pid, saved)
        except Exception as e:  # noqa: BLE001
            got = "raised %s" % type(e).__name__
        finally:
            builtins.open, SR.subprocess.run = real_open, real_run
        ok = got is not False
        print("%s %s: proc_alive(live child) -> %r" % ("PASS" if ok else "FAIL", case, got))
        if not ok:
            bad.append(case)
finally:
    builtins.open, SR.subprocess.run = real_open, real_run
    child.kill()
    child.wait(timeout=5)
print("PASS 2 of 2 unreadable readings are not called dead" if not bad else
      "FAIL a live process read as dead when its reading was unreadable: %s" % "; ".join(bad))
sys.exit(1 if bad else 0)
