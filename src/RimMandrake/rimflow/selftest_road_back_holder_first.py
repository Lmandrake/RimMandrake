#!/usr/bin/env python3
"""selftest_road_back_holder_first: the promises of design/specs/2026-11-20-road-back-holder-first/boundary.md, one test
per promise, each named as the promise is. The road back reads the items the in-game driver or blind judge filed itself,
and a pilot mod's holder runs once on all of them before any one-fixer-per-item run (item
RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION; report context-kept-not-reloaded, change 4). No game, no
network, no real launch."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="holder_first_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation_autonomy as AUT  # noqa: E402
import maturation_dispatch as MD  # noqa: E402

PILOT, OTHER = "FlowWorks", "Pyrelands"
NOW = 1795170000.0
CFG = {"advancing": [PILOT, OTHER], "cap_usd": 15, "max_live": 4, "launch_tries": 3, "seat": "BENCH"}
DRIVER = "RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO"
STEWARD = "RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK"
ITEMS = [{"id": "RIMMANDRAKE_FIX_FLOWWORKS_%s" % w, "needs": "offline"} for w in ("GEYSER_ONE", "SOURCE_TWO",
                                                                                   "RESET_THREE", "SPARE_FOUR")]


def state(holder_ran=False):
    s = {"road_back": {"caused_by": STEWARD, "at": NOW - 600, "from": "in_game"},
         "steward": {"0.1.0|in_game|exit_not_met|2": {"item": STEWARD, "unit": "rm-s", "at": NOW - 600}},
         "ingame_auto": [{"visit": 1, "item": "RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_ONE", "at": NOW - 90000},
                         {"visit": 2, "item": DRIVER, "at": NOW - 9000, "unit": "rm-d"}]}
    if holder_ran:
        s["holder_road_back"] = [{"at": NOW - 300, "unit": "rm-holder-1", "item": ITEMS[0]["id"],
                                  "ids": sorted(x["id"] for x in ITEMS)}]
    return s


def holders(rows, st, pilot=(PILOT,)):
    facts = {m: {"stage": "in_game", "live_units": []} for m in (PILOT, OTHER)}
    fx = {"open_items": lambda ids: list(ITEMS), "account": lambda: (True, "ok"),
          "pilot": lambda root, mod: mod in pilot}
    return MD.pilot_holders(TMP, CFG, st, facts, rows, [r["mod"] for r in rows], NOW, fx)


def fixer_row(mod):
    return {"mod": mod, "stage": "in_game", "decision": "fixer", "aut": "fixer", "fix_item": ITEMS[0]["id"],
            "why": "road-back item gets one fixer run"}


def t_driver_filed_items_are_read():
    s = state()
    ids = AUT._road_back_ids(s, s["road_back"])
    blind = {"road_back": {"caused_by": "RIMMANDRAKE_ROUTE_X_CYCLE_TWO_FAILURES_BACK", "at": NOW - 600,
                           "from": "blind_challenge"},
             "blind_auto": [{"cycle": 2, "item": "RIMMANDRAKE_CHALLENGE_X_BLIND_CYCLE_TWO", "at": NOW - 5000}]}
    bids = AUT._road_back_ids(blind, blind["road_back"])
    return (STEWARD in ids and DRIVER in ids and "RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_ONE" not in ids
            and "RIMMANDRAKE_CHALLENGE_X_BLIND_CYCLE_TWO" in bids), (ids, bids)


def t_pilot_holder_goes_first():
    st = {"mods": {PILOT: state()}}
    rs, la = holders([fixer_row(PILOT)], st)
    r = rs[0]
    return (PILOT in la and r.get("decision") == "launch" and not r.get("aut")
            and sorted(x["id"] for x in r.get("holder_items") or []) == sorted(x["id"] for x in ITEMS)), r


def t_holder_spent_hands_to_fixers():
    st = {"mods": {PILOT: state(holder_ran=True)}}
    rs, _ = holders([fixer_row(PILOT)], st)
    spent, _ = holders([dict(fixer_row(PILOT), decision="fixer_spent", aut=None)], {"mods": {PILOT: state(True)}})
    return (rs[0].get("decision") == "fixer" and rs[0].get("aut") == "fixer" and not rs[0].get("holder_items")
            and spent[0].get("decision") == "holder_spent"), (rs[0], spent[0].get("decision"))


def t_non_pilot_unchanged():
    st = {"mods": {OTHER: state()}}
    rs, _ = holders([fixer_row(OTHER)], st, pilot=())
    return rs[0].get("decision") == "fixer" and rs[0].get("aut") == "fixer", rs[0]


def main():
    tests = [t_driver_filed_items_are_read, t_pilot_holder_goes_first, t_holder_spent_hands_to_fixers,
             t_non_pilot_unchanged]
    fails = []
    for fn in tests:
        try:
            good, got = fn()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure by name, never a pass
            good, got = False, "%s: %s" % (type(e).__name__, e)
        print("%s  %s%s" % ("PASS" if good else "FAIL", fn.__name__[2:].replace("_", "-"),
                            "" if good else "  got: %r" % (got,)))
        if not good:
            fails.append(fn.__name__)
    if fails:
        print("FAIL selftest_road_back_holder_first: %d of %d red" % (len(fails), len(tests)))
        return 1
    print("PASS selftest_road_back_holder_first: %d tests" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
