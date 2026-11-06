#!/usr/bin/env python3
"""Selftest for await_lifecycle.py (READYWAITS_UNIFY_ONE_HELPER). Offline; a fake bridge and a fake clock.

    python3 src/RimMandrake/Utils/selftest_await_lifecycle.py

Covers the four acceptance cases of build_spec.md §2 T8 (loading, menu, missing map, timeout) plus the start-once
rule, a dropping bridge and the MCP envelope. Falsification: each case also asserts the WRONG answer is not given
(a missing map never reads ready, a menu without start never calls start).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import await_lifecycle as A  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class Fake(object):
    """Scripted bridge: `phases` is a list of (programState, mapCount) per poll; the last repeats.
    A programState of Exception raises. start_debug_game_ready switches to `after_start`."""

    def __init__(self, phases, after_start=None, envelope=False):
        self.phases, self.after_start, self.envelope = list(phases), after_start, envelope
        self.i, self.calls, self.now = 0, [], 0.0

    def cur(self):
        return self.phases[min(self.i, len(self.phases) - 1)]

    def wrap(self, d):
        return {"content": [{"text": json.dumps(d)}]} if self.envelope else d

    def __call__(self, tool, **p):
        self.calls.append(tool)
        ps, n = self.cur()
        if tool == "rimworld/get_ui_state":
            if ps is Exception:
                raise IOError("bridge dropped")
            return self.wrap({"programState": ps, "hasCurrentGame": ps == "Playing"})
        if tool == "rimworld/get_game_info":
            self.i += 1
            return self.wrap({"mapCount": n})
        if tool == "rimworld/start_debug_game_ready":
            self.phases, self.i = list(self.after_start), 0
            return {"success": True}
        raise AssertionError("unexpected tool " + tool)

    def clock(self):
        return self.now

    def sleep(self, s):
        self.now += s
        if self.cur()[0] != "Playing":
            self.i += 1


def run(fake, state="map_ready", deadline_s=10, start=False):
    return A.await_lifecycle(fake, state, deadline_s=deadline_s, start=start, poll_s=1.0,
                             clock=fake.clock, sleep=fake.sleep)


# loading -> map up
f = Fake([("MapInitializing", None)] * 3 + [("Playing", 1)])
r = run(f)
check("loading then a map reads ready", r.ok and r.phase == "map_ready" and r.polls == 4, repr(r))
check("loading waits on the wall clock, 3 polls of 1 s", r.waited_s == 3.0, repr(r))
check("a wait never starts a game unasked", "rimworld/start_debug_game_ready" not in f.calls)

# menu: no start -> timeout naming the menu; start -> started exactly once, then ready
f = Fake([("Entry", None)])
r = run(f, deadline_s=5)
check("menu without start times out, saying menu", not r.ok and r.phase == "menu" and "main menu" in r.reason,
      repr(r))
check("menu without start never calls start", "rimworld/start_debug_game_ready" not in f.calls)
f = Fake([("Entry", None)], after_start=[("MapInitializing", None), ("Playing", 1)])
r = run(f, start=True)
check("menu with start=True starts and reaches map_ready", r.ok and r.started, repr(r))
check("start is called once", f.calls.count("rimworld/start_debug_game_ready") == 1, str(f.calls))
f = Fake([("Entry", None)], after_start=[("Entry", None)])
r = run(f, start=True, deadline_s=4)
check("a start that lands back at the menu is not retried", not r.ok and r.phase == "menu"
      and f.calls.count("rimworld/start_debug_game_ready") == 1, repr(r))
f = Fake([("Entry", None)])
r = run(f, state="menu", start=True)
check("menu is a state one can wait for, and start is ignored for it", r.ok and not r.started, repr(r))

# missing map: Playing with mapCount 0 never reads map_ready, but does read playing
f = Fake([("Playing", 0)])
r = run(f, deadline_s=3)
check("a game with no map is not map_ready", not r.ok and r.phase == "missing_map" and "no map" in r.reason,
      repr(r))
f = Fake([("Playing", 0)])
r = run(f, state="playing")
check("a game with no map IS playing", r.ok and r.phase == "missing_map", repr(r))
f = Fake([("Playing", None)])
r = run(f, deadline_s=2)
check("an absent mapCount is not a map", not r.ok and r.phase == "missing_map", repr(r))

# timeout while loading; result never raises
f = Fake([("MapInitializing", None)])
r = run(f, deadline_s=7)
check("loading past the deadline times out, saying loading", not r.ok and r.phase == "loading"
      and "still loading" in r.reason and r.waited_s >= 7, repr(r))
check("a timed-out result is falsy", not bool(r))

# a dropping bridge is waited through; an always-dead one times out as unreachable
f = Fake([(Exception, None), (Exception, None), ("Playing", 2)])
r = run(f)
check("bridge drops while loading are polled through", r.ok and r.polls == 3, repr(r))
f = Fake([(Exception, None)])
r = run(f, deadline_s=2)
check("a bridge that never answers times out as unreachable", not r.ok and r.phase == "unreachable", repr(r))

# MCP envelope
f = Fake([("Playing", 1)], envelope=True)
check("an MCP content envelope is opened", run(f).ok)

# bad state
try:
    run(Fake([("Playing", 1)]), state="ready")
    check("an unknown state is refused", False)
except ValueError:
    check("an unknown state is refused", True)

# settle=True (READYWAITS_MIGRATE_REMAINING_52_COPIES): a map with a long event pending is not ready until it clears
class Seq(object):
    """Playing with one map throughout; bridge status and map ids follow scripted per-poll lists (the last repeats)."""

    def __init__(self, status=None, mapids=None, ui=None):
        self.status, self.mapids, self.ui = status or [{}], mapids or [None], ui or ["Playing"]
        self.n, self.now, self.calls = 0, 0.0, []

    def _at(self, xs):
        return xs[min(self.n, len(xs) - 1)]

    def __call__(self, tool, **p):
        self.calls.append(tool)
        if tool == "rimworld/get_ui_state":
            return {"programState": self._at(self.ui)}
        if tool == "rimworld/get_game_info":
            return {"mapCount": 1}
        if tool == "rimbridge/get_bridge_status":
            return {"state": self._at(self.status)}
        if tool == "jawa/map_info":
            return {"mapId": self._at(self.mapids)}
        raise AssertionError("unexpected tool " + tool)

    def clock(self):
        return self.now

    def sleep(self, s):
        self.now += s
        self.n += 1


def run2(f, **kw):
    kw.setdefault("deadline_s", 10)
    return A.await_lifecycle(f, "map_ready", poll_s=1.0, clock=f.clock, sleep=f.sleep, **kw)


f = Seq(status=[{"automationReady": True, "longEventPending": True}] * 2 + [{"automationReady": True}])
r = run2(f, settle=True)
check("settle waits out a pending long event", r.ok and r.polls == 3, repr(r))
f = Seq(status=[{"automationReady": True, "longEventPending": True}])
r = run2(f)
check("without settle the status is never asked", r.ok and "rimbridge/get_bridge_status" not in f.calls, repr(r))
f = Seq(status=[{"automationReady": False}])
r = run2(f, settle=True, deadline_s=3)
check("a never-settled bridge times out as settling", not r.ok and r.phase == "settling", repr(r))
f = Seq(status=[{"automationReady": False}])
r = A.await_lifecycle(f, "playing", deadline_s=3, poll_s=1.0, clock=f.clock, sleep=f.sleep, settle=True)
check("settle does not apply to a playing wait", r.ok, repr(r))

# new_map_of: the old map id (or none) is not ready; a new id is
f = Seq(mapids=["m1", None, "m1", "m2"])
r = run2(f, new_map_of="m1")
check("new_map_of waits for a NEW mapId", r.ok and r.polls == 4, repr(r))
f = Seq(mapids=["m1"])
r = run2(f, new_map_of="m1", deadline_s=4)
check("the old map past the deadline times out as old_map", not r.ok and r.phase == "old_map"
      and "old one" in r.reason, repr(r))

# await_leaving: after load_game the old map stays Playing for a while
f = Seq(ui=["Playing", "Playing", "MapInitializing"])
r = A.await_leaving(f, "playing", deadline_s=10, poll_s=1.0, clock=f.clock, sleep=f.sleep)
check("await_leaving sees the game leave Playing", r.ok and r.polls == 3 and r.phase == "loading", repr(r))
f = Seq(ui=["Playing"])
r = A.await_leaving(f, "playing", deadline_s=3, poll_s=1.0, clock=f.clock, sleep=f.sleep)
check("await_leaving times out when the game stays", not r.ok and "still" in r.reason, repr(r))
f = Seq(ui=["Entry"])
r = A.await_leaving(f, "menu", deadline_s=3, poll_s=1.0, clock=f.clock, sleep=f.sleep)
check("await_leaving(menu) holds while at the menu", not r.ok and r.phase == "menu", repr(r))

print("RESULT %s (%d failures)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
