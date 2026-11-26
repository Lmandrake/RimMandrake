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
CFG = {"advancing": [PILOT, OTHER], "cap_tokens": 3_750_000, "max_live": 4, "launch_tries": 3, "seat": "BENCH"}
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


# the holder never takes an item a live run is working (RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FIVE: the
# FlowWorks holder was launched under its first road-back item while that item's own fixer ran in <ITEM>.det; the
# launcher refused "clone ... is held: run ... is running in it", and the tick owed a form repair for a wait)
LIVE_HELD = ("refused: clone /pool/clones/%s.det is held: run rm-detached-bench-x-1 is running in it; it ends with a "
             "line in the Conductor log, then its return step gives the clone back: launch again after that"
             % ITEMS[0]["id"])
DEAD_HELD = ("refused: clone /c/X.det is held: run u is recorded running but its unit is gone, so its finish step "
             "never ran; to pass: x finish --unit u, then x return --unit u, then launch again")


class _Patch:
    def __init__(self, *trips):
        self.trips, self.old = trips, []

    def __enter__(self):
        for obj, name, val in self.trips:
            self.old.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

    def __exit__(self, *a):
        for obj, name, val in reversed(self.old):
            setattr(obj, name, val)


def _holder(busy, answer=None):
    """road_back_holder on ITEMS with `busy` {item: unit} live elsewhere; -> (rc, text, unit, item, launched, st)."""
    import maturation as M
    import modledger
    launched = []

    def brief(item, text, model, cap, seat="BENCH", env=None, **k):
        launched.append({"item": item, "text": text})
        return answer or (0, "DETACHED rm-holder", "rm-holder")
    st = {"mods": {PILOT: {}}}
    with _Patch((M, "game_takeable", lambda stage: False),
                (modledger, "resume_plan", lambda root, mod: {"action": "packet", "reconcile": False, "why": "-"}),
                (MD, "ledger_open", lambda *a, **k: {"brief": a[3], "env": {}, "run": "r1", "packet": ""}),
                (MD, "ledger_after", lambda *a, **k: "ledger ok")):
        rc, text, unit, item = MD.road_back_holder(TMP, CFG, st, PILOT, "offline_build", list(ITEMS), None, 15, NOW,
                                                   {"launch_brief": brief, "item_live": lambda i: busy.get(i)})
    return rc, text, unit, item, launched, st


def t_busy_item_left_to_its_run():
    rc, text, unit, item, launched, st = _holder({ITEMS[0]["id"]: "rm-detached-bench-x-1"})
    booked = (st["mods"][PILOT].get("holder_road_back") or [{}])[-1]
    rest = sorted(x["id"] for x in ITEMS[1:])
    import probe_result as PR
    rc2, text2, _, item2, launched2, st2 = _holder({ITEMS[0]["id"]: PR.could_not_look("records unreadable")})
    booked2 = (st2["mods"][PILOT].get("holder_road_back") or [{}])[-1]
    return (rc == 0 and len(launched) == 1 and launched[0]["item"] != ITEMS[0]["id"] and item != ITEMS[0]["id"]
            and ITEMS[0]["id"] in launched[0]["text"] and "rm-detached-bench-x-1" in launched[0]["text"]
            and booked.get("ids") == rest
            and rc2 == 0 and item2 == ITEMS[0]["id"] and "UNMEASURED" in text2 and ITEMS[0]["id"] in text2
            and len(booked2.get("ids") or []) == len(ITEMS)), (rc, item, booked, launched, text2)


def t_all_items_busy_is_a_wait():
    import maturation as M
    rc, text, unit, item, launched, st = _holder({x["id"]: "rm-u-%d" % i for i, x in enumerate(ITEMS)})
    return (rc is None and not launched and M.WAIT_MARK in (text or "") and AUT.wait_refusal(text)
            and not st["mods"][PILOT].get("holder_road_back")), (rc, text, launched, st)


def t_a_clone_held_by_a_live_run_is_a_wait():
    import form_fault as FF
    rc, text, unit, item, launched, st = _holder({}, answer=(2, LIVE_HELD, None))
    return (AUT.wait_refusal(LIVE_HELD) and FF.fault_class(LIVE_HELD) == "wait" and FF.fault_class(DEAD_HELD) == "form"
            and FF.fault_class(LIVE_HELD + " | " + DEAD_HELD.split("is held: ", 1)[1]) == "form"
            and unit is None and not st["mods"][PILOT].get("holder_road_back")), (rc, text, st)


def t_a_wait_row_is_launch_wait():
    row = {"mod": PILOT, "stage": "offline_build", "holder_items": list(ITEMS), "cap": 15}
    st = {"mods": {PILOT: {}}}
    with _Patch((MD, "road_back_holder", lambda *a, **k: (2, LIVE_HELD, None, ITEMS[1]["id"]))):
        MD.execute(TMP, CFG, st, [row], [PILOT], NOW, {"known": lambda: set()})
    return row.get("decision") == "launch_wait" and not row.get("need"), row


def main():
    tests = [t_driver_filed_items_are_read, t_pilot_holder_goes_first, t_holder_spent_hands_to_fixers,
             t_non_pilot_unchanged, t_busy_item_left_to_its_run, t_all_items_busy_is_a_wait,
             t_a_clone_held_by_a_live_run_is_a_wait, t_a_wait_row_is_launch_wait]
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
