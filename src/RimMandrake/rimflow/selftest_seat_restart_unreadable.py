#!/usr/bin/env python3
"""selftest_seat_restart_unreadable.py — a pid whose reading FAILS is "could not look", never "dead"
(RIMMANDRAKE_READ_UNREADABLE_PID_AS_UNKNOWN_NOT_DEAD_YET; owner 2026-11-17, the four answers).

Every caller that acts on "dead" (kill, adopt a dead Conductor's message, relaunch beside a window, pick the dead window
whose reply is read) is driven with the reading seam `_proc_read` answering "unknown", and must not act; one reading
decides each call (a second read that succeeds never turns the first failure into "gone"). Linux only for the /proc
half; no real seat, game or window is touched: the only process is this test's own `sleep` child.

    python3 src/RimMandrake/rimflow/selftest_seat_restart_unreadable.py      exit 0 = pass
"""
import builtins
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_seat_restart_unreadable_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "claude")
os.environ["RM_SEAT_LOG_DIR"] = os.path.join(TMP, "seat_log")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import seat_restart as SR  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


REAL = SR._proc_read
UNKNOWN = ("unknown", "test: reading failed", None)


def seq(*answers):
    """A reading seam that answers in turn (the last answer repeats)."""
    left = list(answers)

    def read(pid):
        return left.pop(0) if len(left) > 1 else left[0]
    return read


child = subprocess.Popen(["sleep", "60"])
try:
    start = SR.proc_start(child.pid)
    check(start is not None, "a live child has a birth")

    # one reading decides: the first failed, a second would succeed
    SR._proc_read = seq(UNKNOWN, ("ok", "S", start))
    res = SR.kill_pid(child.pid)
    check(res.startswith("refused") and "could not be read" in res,
          "kill_pid with no start: a failed first reading refuses, never 'already gone' (%s)" % res)
    SR._proc_read = seq(UNKNOWN, ("ok", "S", start))
    check(SR.proc_birth(child.pid) == (None, "test: reading failed"), "proc_birth: one reading, its failure named")
    SR._proc_read = REAL

    # _gone: a Conductor window whose reading failed is not adopted as dead
    acts = []
    rs = {"pid": child.pid, "start": start, "session_id": "s1", "state": "claimed"}
    ro = {"birth": lambda pid: (None, "test: reading failed"), "owed": lambda r: ["his message"]}
    SR._gone("CONDUCTOR", {"kind": "conductor", "session_name": "CONDUCTOR", "clone": TMP}, rs, {}, ro, 1000, lambda **k: acts.append(k), "gone")
    check([a["do"] for a in acts] == ["restart_cancel"], "_gone: an unreadable window is cancelled, never adopted (%s)" % acts)
    acts.clear()
    rs = {"pid": child.pid, "start": start, "session_id": "s1", "state": "claimed"}
    ro = {"birth": lambda pid: (None, None), "owed": lambda r: ["his message"]}
    SR._gone("CONDUCTOR", {"kind": "conductor", "session_name": "CONDUCTOR", "clone": TMP}, rs, {"agents": {"sessions": []}}, ro, 1000,
             lambda **k: acts.append(k), "gone")
    check(acts and acts[0]["do"] != "restart_cancel", "_gone control: a window read gone with his message owed is adopted (%s)" % acts)

    # the fallback relaunch: an unreadable old window is skipped AND retried on a later tick
    root = os.path.join(TMP, "root")
    SR.write_killed("BENCH", {"seat": "BENCH", "old_pid": child.pid, "old_start": start, "killed_at": 900}, root)
    st = {"seat_restart": {"BENCH": {"state": "killed", "killed_at": 900, "fallback_at": 950}}}
    launched = []
    res = SR.execute({"do": "restart_fallback", "seat": "BENCH", "argv": ["true"], "killed_at": 900}, {}, st, True, 960,
                     {"root": root, "alive": lambda p: None, "fallback": lambda argv: launched.append(argv) or "launched"})
    check(launched == [] and "could not be read" in res and "fallback_at" not in st["seat_restart"]["BENCH"],
          "fallback: an unreadable old window launches nothing and clears fallback_at for a retry (%s)" % res)
    res = SR.execute({"do": "restart_fallback", "seat": "BENCH", "argv": ["true"], "killed_at": 900}, {}, st, True, 970,
                     {"root": root, "alive": lambda p: True, "fallback": lambda argv: launched.append(argv) or "launched"})
    check(launched == [] and "still alive" in res, "fallback control: a live old window is skipped as alive (%s)" % res)

    # window_alive: an unreadable window is never the dead one whose reply is read
    SR._proc_read = lambda pid: UNKNOWN
    check(SR.window_alive({"pid": child.pid, "procStart": start}) is True, "window_alive: unreadable reads as not dead")
    SR._proc_read = lambda pid: ("gone", None, None)
    check(SR.window_alive({"pid": child.pid, "procStart": start}) is False, "window_alive control: gone reads dead")
    SR._proc_read = REAL
    check(SR.window_alive({"pid": child.pid, "procStart": start}) is True, "window_alive control: the live child reads alive")

    # Linux: no /proc mounted is unknown, not gone (and never a ps fallback in another unit)
    if sys.platform.startswith("linux"):
        real_open, real_exists = builtins.open, os.path.exists

        def no_proc(path, *a, **k):
            if str(path).startswith("/proc/"):
                raise FileNotFoundError(2, "No such file", str(path))
            return real_open(path, *a, **k)
        builtins.open, SR.os.path.exists = no_proc, (lambda p: False if str(p).startswith("/proc/") else real_exists(p))
        try:
            got = SR._proc_read(child.pid)
        finally:
            builtins.open, SR.os.path.exists = real_open, real_exists
        check(got[0] == "unknown", "Linux with no /proc: unknown, not gone (%s)" % (got,))
        check(SR._proc_read(2 ** 22 + 12345)[0] == "gone", "Linux control: a pid that does not exist reads gone")
finally:
    SR._proc_read = REAL
    child.kill()
    child.wait(timeout=5)

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
