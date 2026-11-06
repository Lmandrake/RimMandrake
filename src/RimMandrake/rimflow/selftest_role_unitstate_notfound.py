#!/usr/bin/env python3
"""selftest_role_unitstate_notfound.py — a collected or never-created unit is ABSENT, not "unknown" forever.

ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE (GPT full-file review g2 of role_launch.py): `systemctl show` failing for
a unit/scope systemd has no record of (collected by --collect, or never created because a pre-step failed) read
"unknown", and supervise_roles keeps "unknown" busy forever (re-stopping it, blocking later launches). The fix tells
a confirmed LoadState=not-found apart from a query failure, and retires the run only when unit AND scope are
confirmed absent/terminal and the marker scan finds no survivor.

Cases (faked systemctl runner and obs; no systemd, no process, no state file):
  probe       nonzero show + stderr "not found"/"not loaded" -> not-found; nonzero show + LoadState=not-found -> not-found
  failure     nonzero show with an unrelated error, a timeout, an invalid name, a blind LoadState -> unknown
  unchanged   a normal ActiveState is passed through
  retire      unit not-found + scope not-found + marker scan [] -> the run leaves `running`, role not busy
  guarded     not-found but scope still active / marker scan sees a pid / scan blind / query failure -> kept busy
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def fake(show, load=None):
    """-> a runner: `show` answers the ActiveState query, `load` the LoadState query; each (rc, out, err) or an
    exception to raise."""
    def run(argv, **kw):
        ans = load if "LoadState" in argv else show
        if isinstance(ans, BaseException):
            raise ans
        if ans is None:
            return subprocess.CompletedProcess(argv, 1, "", "")
        return subprocess.CompletedProcess(argv, *ans)
    return run


def test_probe():
    us = RL.unit_state
    check(us("u", fake((1, "", "Failed to get properties: Unit u.service not found.\n"))) == "not-found",
          "nonzero show, stderr 'not found' -> not-found")
    check(us("u", fake((1, "", "Unit claude-seat-x-1.scope not loaded.\n"))) == "not-found",
          "nonzero show, stderr 'not loaded' -> not-found")
    check(us("u", fake((1, "", "bus hiccup"), (0, "not-found\n", ""))) == "not-found",
          "nonzero show, LoadState=not-found -> not-found")
    check(us("u", fake((0, "", ""), (0, "not-found\n", ""))) == "not-found",
          "empty show, LoadState=not-found -> not-found")


def test_failure():
    us = RL.unit_state
    check(us("u", fake((1, "", "Failed to connect to bus: No medium found"), (1, "", "bus"))) == "unknown",
          "bus failure on both queries -> unknown")
    check(us("u", fake((1, "", "Unit name bad@@ is not valid."), (1, "", "not valid"))) == "unknown",
          "invalid unit name -> unknown, never absence")
    check(us("u", fake(subprocess.TimeoutExpired(["systemctl"], 30))) == "unknown", "show times out -> unknown")
    check(us("u", fake((1, "", "x"), subprocess.TimeoutExpired(["systemctl"], 30))) == "unknown",
          "LoadState probe times out -> unknown")
    check(us("u", fake((1, "", "x"), (0, "loaded\n", ""))) == "unknown",
          "failed show but unit loaded -> unknown (a query failure, not absence)")
    check(us("u", fake((3, "active", ""), (3, "not-found", ""))) == "unknown",
          "nonzero LoadState probe is not evidence -> unknown")


def test_unchanged():
    for st in ("active", "inactive", "failed", "activating"):
        check(RL.unit_state("u", fake((0, " %s \n" % st, ""))) == st, "ActiveState %s passed through" % st)
    check("not-found" in RL.TERMINAL, "not-found is terminal")


def run_state(unit_states, procs):
    st = {"roles": {"Operations": {"runs": [{
        "state": "running", "unit": "rm-role-ops-1", "scope": "claude-seat-OPS-rm-role-ops-1.scope",
        "marker": "rm-role-ops-1", "at": 1000, "mode": "slot", "budget": 100, "out": "/nonexistent/out.json"}]}}}
    acts = []
    obs = {"unit_state": lambda u: unit_states[u], "procs": procs, "result": lambda run: None}
    busy = RL.supervise_roles({"roles": []}, st, obs, 1100, lambda **a: acts.append(a))
    return busy, st["roles"]["Operations"]["runs"][0]["state"], acts


def test_retire_and_guarded():
    U, S = "rm-role-ops-1", "claude-seat-OPS-rm-role-ops-1.scope"
    busy, state, acts = run_state({U: "not-found", S: "not-found"}, lambda m, **k: [])
    check("Operations" not in busy and state != "running" and any(a.get("do") == "role_done" for a in acts),
          "unit+scope not-found, scan empty -> retired (%s, busy=%s)" % (state, sorted(busy)))
    busy, state, _ = run_state({U: "not-found", S: "inactive"}, lambda m, **k: [])
    check("Operations" not in busy and state != "running", "unit not-found, scope inactive, scan empty -> retired")
    for label, us, procs in (
            ("scope still active", {U: "not-found", S: "active"}, lambda m, **k: []),
            ("marker scan sees a survivor", {U: "not-found", S: "not-found"}, lambda m, **k: [4242]),
            ("marker scan blind", {U: "not-found", S: "not-found"}, lambda m, **k: None),
            ("unit query failed", {U: "unknown", S: "not-found"}, lambda m, **k: []),
            ("scope query failed", {U: "not-found", S: "unknown"}, lambda m, **k: [])):
        busy, state, acts = run_state(us, procs)
        check("Operations" in busy and state == "running" and not any(a.get("do") == "role_done" for a in acts),
              "%s -> kept busy and running" % label)


if __name__ == "__main__":
    test_probe()
    test_failure()
    test_unchanged()
    test_retire_and_guarded()
    print("FAIL %d" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
