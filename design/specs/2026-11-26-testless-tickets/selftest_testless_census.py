#!/usr/bin/env python3
"""selftest_testless_census.py - testless_census.classify gives each ticket one state and marks a hole only where no
route and no act ends the state. Offline: planted tickets and a planted env; no ledger read except the last check.
Item RIMMANDRAKE_PROVE_TESTLESS_TICKETS_ROUTE_HE_WAS_TOLD_NONE."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import testless_census as T  # noqa: E402

FAILS = []


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class X(object):
    def __init__(self, iid, kind="task", **kw):
        self.id, self.kind, self.wait_until, self.blocked_kind, self.blocked_lift_at = iid, kind, None, None, None
        self.blocked_reason = None
        self.__dict__.update(kw)


def env(**kw):
    e = {"system": lambda x: "pipeline:ops", "park": lambda x: None, "refusal": lambda x: None, "off": lambda x: None,
         "shape_due": lambda x: None, "admitted": {"Pyrelands", "FlowWorks", "Cauldron", "Gimme"}, "held": lambda m: None,
         "on": lambda m: True, "pilots": {"FlowWorks"}, "road_back": lambda m: ["ITEM_A_B_C"], "rests": {"Gimme"},
         "classes": {"pipeline": "on", "game": "off", "machine": "on", "mod": "on"}}
    e.update(kw)
    return e


def st(x, **kw):
    v = T.classify(x, env(**kw))
    return v["state"], v["hole"]


def main():
    chk(st(X("A_B_C", "owed")) == ("NOT WORK", False), "a ticket of kind owed is not work, not a hole")
    chk(st(X("A_B_C")) == ("ON A ROUTE", False), "a pipeline ticket of an on class is on the onboarding route")
    chk(st(X("A_B_C"), system=lambda x: "game:art") == ("CLASS OFF", False), "a game ticket is CLASS OFF while game is off")
    chk(st(X("A_B_C"), system=lambda x: "item:A_B_C") == ("NO HOME", True), "an old ticket with no home is a hole")
    chk(st(X("A_B_C"), system=lambda x: "item:A_B_C", shape_due=lambda x: "filed 3 h ago") == ("ON A ROUTE", False),
        "a ticket with no home that Shape will take is on a route")
    chk(st(X("A_B_C"), system=lambda x: "cause:P") == ("NO HOME", True), "cause: is no home either")
    chk(st(X("A_B_C"), system=lambda x: "weird:x") == ("NO ROUTE", True), "a class with no setting is NO ROUTE")
    chk(st(X("A_B_C"), system=lambda x: None) == ("COULD NOT LOOK", False), "an unreadable home is COULD NOT LOOK, not a state")
    m = lambda n: (lambda x: "mod:" + n)  # noqa: E731
    chk(st(X("A_B_C"), system=m("Abyss")) == ("MOD NOT ADMITTED", False), "a mod with no stage record is MOD NOT ADMITTED")
    chk(st(X("A_B_C"), system=m("Cauldron"), held=lambda mo: "HELD BY OWNER") == ("MOD HELD", False), "a held mod is MOD HELD")
    chk(st(X("A_B_C"), system=m("Cauldron"), on=lambda mo: False) == ("MOD HELD", False), "a mod not ON is MOD HELD")
    chk(st(X("A_B_C"), system=m("FlowWorks")) == ("ON A ROUTE", False), "a pilot mod with an open road back is on its holder run")
    chk(st(X("A_B_C"), system=m("FlowWorks"), road_back=lambda mo: []) == ("NO ROUTE", True),
        "a pilot mod with no road back and no rest is a hole")
    chk(st(X("A_B_C"), system=m("Pyrelands")) == ("NO ROUTE", True), "an ON mod that is not a ledger pilot is a hole")
    chk(st(X("A_B_C"), system=m("Gimme")) == ("NO ROUTE", False), "a resting mod is NO ROUTE but no hole: the owed view lists it")
    chk(st(X("A_B_C"), system=m("FlowWorks"), road_back=lambda mo: None)[0] == "COULD NOT LOOK", "an unread road back is not a state")
    chk(st(X("A_B_C"), park=lambda x: ("dated wait", "until 2026-12-01")) == ("PARKED", False), "a dated wait is a park with an end")
    chk(st(X("A_B_C"), park=lambda x: ("block: other", None)) == ("PARKED", True), "a block of no kind and no end is a hole")
    v = T.classify(X("A_B_C"), env(system=lambda x: "item:A_B_C", park=lambda x: ("dated wait", "until 2026-12-01")))
    chk(v["then"]["state"] == "NO HOME" and v["then"]["hole"], "a park keeps the hole under it: then is NO HOME")
    v = T.classify(X("A_B_C"), env(system=lambda x: "item:A_B_C", off=lambda x: "HELD BY OWNER (mod:Cauldron)"))
    chk(v["state"] == "MOD HELD" and v["then"]["state"] == "NO HOME", "a hold keeps the hole under it too")
    # park_of: the end condition of each kind of block
    now = 1000.0
    ep = lambda s: float(s)  # noqa: E731
    chk(T.park_of(X("A", wait_until="2000"), [], False, now, ep) == ("dated wait", "until 2000"), "park_of: a wait ahead")
    chk(T.park_of(X("A", wait_until="10"), [], False, now, ep) is None, "park_of: a wait that has passed is no park")
    chk(T.park_of(X("A"), ["B"], True, now, ep)[0] == "block on an open item", "park_of: a block on an open item")
    chk(T.park_of(X("A", blocked_kind="owner"), [], True, now, ep)[1] is not None, "park_of: an owner block ends by his act")
    chk(T.park_of(X("A", blocked_kind="external"), [], True, now, ep)[1] is None, "park_of: external with no reason has no end")
    chk(T.park_of(X("A"), [], True, now, ep) == ("block: other", None), "park_of: a block of no kind has no end")
    chk(T.park_of(X("A"), [], False, now, ep) is None, "park_of: no block, no wait: no park")
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
