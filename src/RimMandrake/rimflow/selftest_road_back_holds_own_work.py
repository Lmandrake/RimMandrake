#!/usr/bin/env python3
"""Offline selftest: a run holds a mod's next run only when the run works that mod. One test per promise on
design/specs/2026-11-27-road-back-holds-own-work/boundary.md, each named after it.

    python3 src/RimMandrake/rimflow/selftest_road_back_holds_own_work.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_road_back_holds_own_work.py --only t_x ...  those alone

The case (FlowWorks, 6:15 PM PST 2026-11-27, item RIMMANDRAKE_FIX_REPAIR_RUN_HOLDS_MOD_VISIT_WAITS_GAME_IDLE): the
Conductor filed the pipeline repair RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST (the blind judge's brief)
caused by FlowWorks' blind-cycle-5 judge item. The road back read it as FlowWorks' own work, the tick launched FlowWorks'
holder run on it at stage in_game, and that live holder held in-game visit 14 while ArchBig was free. Each test builds
a throwaway root (one ledger shard) in a temp dir; no game, no launch.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
TMP = tempfile.mkdtemp(prefix="rb_own_work_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation as M              # noqa: E402
import maturation_autonomy as A     # noqa: E402
import maturation_dispatch as MD    # noqa: E402

FAILS = []
MOD = "FlowWorks"
NOW = 1795831000.0
JUDGE = "RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_FIVE_TESTS_FIRST"
CONFIRM = "RIMMANDRAKE_CONFIRM_FLOWWORKS_CYCLE_FIVE_EXIT_MET"
REPAIR = "RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST"
OWN = "RIMMANDRAKE_FIX_FLOWWORKS_TAR_SHEET_FIRE_COMP_MISSING"
CFG = {"advancing": [MOD], "cap_tokens": 3_750_000, "max_live": 4, "launch_tries": 3, "seat": "BENCH"}


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def site(repair_home="pipeline:blind-judge-brief", own=False):
    """-> a temp root whose ledger holds the cycle-5 judge, the repair ticket the Conductor filed caused by it (with
    `repair_home` as its last home, None for none) and, when `own`, a FlowWorks fix caused by the same judge."""
    root = tempfile.mkdtemp(prefix="rb_own_work_site_", dir=TMP)
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(d)
    ev = [{"event": "file", "id": JUDGE, "title": "judge FlowWorks blind cycle 5", "ts": "2026-11-27T10:00:00Z"},
          {"event": "file", "id": CONFIRM, "title": "confirm cycle 5", "ts": "2026-11-28T00:48:00Z"},
          {"event": "file", "id": REPAIR, "caused_by": JUDGE, "kind": "bug", "ts": "2026-11-27T22:23:18Z",
           "title": "A blind judge reads the sealed 'Steward's decisions' section of its brief before lane 1 "
                    "(FlowWorks blind cycle 5)"}]
    if repair_home:
        ev.append({"event": "home", "id": REPAIR, "home": "mod:%s" % MOD, "group": "g", "flag": "f",
                   "ts": "2026-11-27T22:30:00Z"})      # an older home, replaced by the later one: the last one wins
        ev.append({"event": "home", "id": REPAIR, "home": repair_home, "group": "g", "flag": "f",
                   "ts": "2026-11-28T02:30:00Z"})
    if own:
        ev.append({"event": "file", "id": OWN, "caused_by": JUDGE, "kind": "bug", "ts": "2026-11-27T21:00:00Z",
                   "title": "FlowWorks tar sheet fire comp missing"})
    with open(os.path.join(d, "BENCH.jsonl"), "w", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(e) + "\n" for e in ev))
    return root


def state():
    """FlowWorks as at 6:05 PM PST: in_game, its road back opened by the cycle-5 confirm, the judge its last blind run."""
    return {"road_back": {"caused_by": CONFIRM, "at": NOW - 600, "from": "blind_challenge", "had_items": True},
            "blind_auto": [{"cycle": 5, "item": JUDGE, "at": NOW - 40000, "unit": "rm-judge"}]}


def visit_row():
    return {"mod": MOD, "stage": "in_game", "visit": 14, "decision": "launch", "why": "owes in-game visit 14"}


def tick_road_back(root, s, row, reader=None):
    """The dry tick's road-back step for the row (maturation_autonomy.decide's branch before a visit launches)."""
    open_items = reader or (lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw))
    return A._road_back(s, row, open_items, NOW, moved=True)


def holder_step(root, s, row):
    """The dispatch step that runs a pilot's holder on the open road-back items (pilot_holders), on a fixer row."""
    facts = {MOD: {"stage": "in_game", "live_units": []}}
    fx = {"open_items": lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw), "account": lambda: (True, "ok"),
          "pilot": lambda r, m: True}
    return MD.pilot_holders(TMP, CFG, {"mods": {MOD: s}}, facts, [row], [row["mod"]], NOW, fx)


def t_a_ticket_homed_off_the_mod_holds_no_stage_of_it():
    """Case 1: the repair ticket, homed pipeline:, caused by the mod's judge item: the road back reads no item, decides
    nothing, and the owed visit stays the row's launch; the holder step runs no holder on it."""
    root = site()
    try:
        got = M.ledger_items_caused_by(root, [JUDGE])
        check([x.get("home") for x in got if x["id"] == REPAIR] == ["pipeline:blind-judge-brief"],
              "a-ticket-homed-off-the-mod-holds-no-stage-of-it: the open item carries its last ledger home", got)
        s, row = state(), visit_row()
        held = tick_road_back(root, s, row)
        check(held is False and row.get("decision") == "launch" and not row.get("fix_item"),
              "a-ticket-homed-off-the-mod-holds-no-stage-of-it: the dry tick keeps visit 14 the launch", (held, row))
        frow = {"mod": MOD, "stage": "in_game", "decision": "fixer", "aut": "fixer", "fix_item": REPAIR, "why": "x"}
        rows, la = holder_step(root, state(), frow)
        check(not rows[0].get("holder_items") and rows[0].get("decision") != "launch",
              "a-ticket-homed-off-the-mod-holds-no-stage-of-it: no holder run of the mod on it", rows[0])
        for h in ("mod:MandrakePatches", "machine:SteveDesktop", "game:game-up", "fix:FlowWorks"):
            r2 = site(h)
            s2, row2 = state(), visit_row()
            check(tick_road_back(r2, s2, row2) is False and row2["decision"] == "launch",
                  "a-ticket-homed-off-the-mod-holds-no-stage-of-it: home %s holds no visit" % h, row2)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_the_mods_own_work_still_holds_its_next_run():
    """Case 2: an item homed mod:FlowWorks, or with no home (no reading: the mod's, as before), still takes its fixer
    before the visit; and a live run that the mod's pipeline launched on the mod is live on it, so nothing launches."""
    for home in ("mod:%s" % MOD, None, "unplaced"):
        root = site(home)
        try:
            s, row = state(), visit_row()
            held = tick_road_back(root, s, row)
            check(held is True and row.get("fix_item") == REPAIR and row.get("decision") == "fixer",
                  "the-mods-own-work-still-holds-its-next-run: home %s takes the fixer before the visit" % home, row)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    root = site(own=True)
    try:
        s, row = state(), visit_row()
        held = tick_road_back(root, s, row)
        check(held is True and row.get("fix_item") == OWN,
              "the-mods-own-work-still-holds-its-next-run: the mod's own item beside a pipeline one holds", row)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    old = MD.MN.gather
    try:
        MD.MN.gather = lambda r, live=True: {"mods": [{"name": MOD, "runs": [
            {"unit": "rm-holder-flowworks", "live": True}, {"unit": "rm-ended", "live": False}]}]}
        got = MD.live_units_on(TMP, MOD)
        check(got == ["rm-holder-flowworks"],
              "the-mods-own-work-still-holds-its-next-run: a live run on the mod is live on it", got)
    finally:
        MD.MN.gather = old


def t_could_not_look_launches_nothing():
    """Case 3: run records or the ledger cannot be read: the gate reads could not look and launches nothing."""
    old = MD.MN.gather
    try:
        def boom(r, live=True):
            raise OSError("records unreadable")
        MD.MN.gather = boom
        got = MD.live_units_on(TMP, MOD)
        check(isinstance(got, str) and got.startswith(MD.UNM),
              "could-not-look-launches-nothing: unreadable run records read UNMEASURED, never []", got)
        MD.MN.gather = lambda r, live=True: {"mods": [{"name": MOD, "runs": MD.UNM}]}
        got = MD.live_units_on(TMP, MOD)
        check(got == MD.UNM, "could-not-look-launches-nothing: a mod whose runs read UNMEASURED is UNMEASURED", got)
    finally:
        MD.MN.gather = old
    s, row = state(), visit_row()
    held = tick_road_back(TMP, s, row, reader=lambda ids, **kw: None)
    check(held is True and row.get("decision") == "blind",
          "could-not-look-launches-nothing: an unreadable ledger makes the road back blind, no visit", row)


def main(argv):
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    for t in (t_a_ticket_homed_off_the_mod_holds_no_stage_of_it, t_the_mods_own_work_still_holds_its_next_run,
              t_could_not_look_launches_nothing):
        if only is None or t.__name__ in only:
            t()
    shutil.rmtree(TMP, ignore_errors=True)
    print("%s selftest_road_back_holds_own_work: %d failing check(s)" % ("PASS" if not FAILS else "FAILED", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
