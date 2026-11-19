#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_SEPARATE_CONTROL_OFF_FROM_LAUNCH_FAILED_180_ALARMS.

A role launch refused by a deliberate control OFF (`./pipe off`, a stop order) is a planned stop, not a
failure: execute() must not raise a role:<Role>:launch_failed alarm, must not stamp the blind outcome
launch_failed, and still gives the slot back so it runs once control is ON. Measured 2026-11-18 6:43-7:01 PM PST:
180 journal lines of "launch FAILED: REFUSED by control: OFF" fed incident roles-20261118181951 to the owner's rung.
A real launch failure (systemd-run said no) still alarms. Uses selftest_dispatcher's fixtures."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as T  # noqa: E402
from selftest_dispatcher import D, check, conductor, fresh, obs, ops_status, robs, sched, at_local  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_control_off_")
OFF = "REFUSED by control: OFF (all, act ct_000035 at 2026-11-18 06:43:50 PM PST): stopped (at_easy_spot)"


def _run(out):
    now = at_local("08:00")
    st = fresh()
    sch = sched(roles=[conductor()])
    o = obs()
    o["roles"] = robs(ops_status(now))
    acts = D.decide(sch, st, o, now, True)
    la = [a for a in acts if a["do"] == "role_launch"]
    check(len(la) == 1, "probe: decide reserved one Conductor launch (%s)" % out[:20])
    la[0]["blind"] = {"role": "Conductor", "outcome": "launched"}
    fx = {"role_launch": lambda *a, **k: (False, out, {}), "off": lambda p: None, "paused": lambda: None,
          "lock": lambda: None, "note": lambda i, t: (True, ""), "publish": lambda n: "p", "persist": lambda: None}
    D.execute(acts, sch, st, os.path.join(TMP, "x"), True, now, fx)
    alarmed = any(a.get("kind") == "role:Conductor:launch_failed" for a in acts)
    return st, la[0], alarmed


def main():
    st, a, alarmed = _run(OFF)
    check(not alarmed, "control OFF: no role:Conductor:launch_failed alarm")
    check(a["blind"]["outcome"] != "launch_failed", "control OFF: blind outcome is not launch_failed (got %r)"
          % a["blind"]["outcome"])
    check(not st["roles"]["Conductor"].get("pending_launch") and not st["roles"]["Conductor"].get("runs"),
          "control OFF: nothing launched, reservation given back (the slot runs when control is ON)")
    st, a, alarmed = _run("systemd-run: Failed to start transient scope unit")
    check(alarmed and a["blind"]["outcome"] == "launch_failed", "a real launch failure still alarms launch_failed")
    print("%d failure(s)" % len(T.FAILS))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
