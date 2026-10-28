#!/usr/bin/env python3
"""CONDUCTOR_GOODBYE_BUILD_PID_GUARD_SEATS (a): no scheduled `claude -p` quick check beside a live standing window.
A role with `window_name` (Conductor: "AGENT CONDUCTOR") launches nothing while obs["window_live"](name) says a session
by that name is running (the dispatcher's own seat detector: `claude agents --json`, matched by name). Held, not
marked: the slot stays due until slot_late_s. Unreadable = held too. Uses selftest_dispatcher.py's fixtures."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as T  # noqa: E402
from selftest_dispatcher import (D, RL, check, conductor, fresh, ops_status, robs, rdecide, role_acts,  # noqa: E402
                                 at_local)

NAME = "AGENT CONDUCTOR"


def ro(now, live):
    o = robs(ops_status(now))
    o["window_live"] = live
    return o


def test_window_guard():
    now = at_local("08:00")
    c = conductor(window_name=NAME)
    seen = []
    st = fresh()
    a = role_acts(rdecide([c], st, ro(now, lambda n: seen.append(n) or (True, "session abc is busy")), now))
    check(seen == [NAME], "guard asks for the window by its name (%r)" % seen)
    check([x["do"] for x in a] == ["role_hold"] and "conductor window live" in a[0]["why"].lower(),
          "live window: a journaled 'conductor window live' hold, no launch (%r)" % [x["do"] for x in a])
    a = role_acts(rdecide([c], st, ro(now, lambda n: (True, "x")), now + 120))
    check(a == [], "the hold is journaled once, not every tick (%r)" % a)
    a = role_acts(rdecide([c], st, ro(now, lambda n: (False, "")), now + 240))
    check([x["do"] for x in a] == ["role_launch"], "slot not consumed by the hold: window gone, the check launches")
    st = fresh()
    a = role_acts(rdecide([c], st, ro(now, lambda n: (None, "claude agents exit 1")), now))
    check([x["do"] for x in a] == ["role_hold"] and "unmeasured" in a[0]["why"].lower(),
          "window UNMEASURED: held, not launched (%r)" % [x["do"] for x in a])
    st = fresh()
    a = role_acts(rdecide([conductor()], st, ro(now, lambda n: (True, "x")), now))
    check([x["do"] for x in a] == ["role_launch"], "a role without window_name is never guarded")
    st = fresh()
    a = role_acts(rdecide([c], st, robs(ops_status(now)), now))
    check([x["do"] for x in a] == ["role_launch"], "no window_live reader in obs: not guarded (old callers)")


def test_wiring():
    o = D.role_obs(T.sched())
    check(callable(o.get("window_live")), "dispatcher.role_obs supplies window_live")
    D_agents = D.observe_agents
    try:
        D.observe_agents = lambda *a, **k: {"state": "MEASURED", "sessions": [{"name": NAME, "status": "idle"}]}
        live, _ = o["window_live"](NAME)
        check(live is True, "a session named for the window = live")
        live, _ = o["window_live"]("AGENT NOBODY")
        check(live is False, "no such session = not live")
        D.observe_agents = lambda *a, **k: {"state": "UNMEASURED", "why": "boom"}
        live, why = o["window_live"](NAME)
        check(live is None and "boom" in why, "agents unreadable = None with the reason")
    finally:
        D.observe_agents = D_agents
    import json
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    cond = [r for r in sch["roles"] if r.get("name") == "Conductor"][0]
    check(cond.get("window_name") == NAME, "the shipped Conductor role names its window")
    # the Conductor was enabled later, on purpose (1fd2bcd2cf, Dispatcher wave 1); this change enabled nothing else
    check(sch["seat_restart"]["enabled"] is False, "nothing enabled by this change (seat_restart stays off)")


def main():
    for t in (test_window_guard, test_wiring):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(T.FAILS))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
