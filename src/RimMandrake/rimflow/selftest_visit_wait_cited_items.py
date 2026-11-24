#!/usr/bin/env python3
"""Offline selftest: the road back after an in-game visit also waits on an open item that a failed line of the visit
record names (`filed`), when that item was not filed as caused by the visit or the steward run. One test per promise on
design/specs/2026-11-21-visit-wait-cited-items/boundary.md, each named after it.

    python3 src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py --only t_x ...  those alone

The case (FlowWorks visit 5, 2026-11-21): the driver put its sc_hung_bridge FAIL on GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO,
filed 2026-10-23 with no caused_by. The tick waited only on items caused by the driver or the steward, so visit 6 would
have launched without the fix. Each test builds a throwaway root (a ledger shard and a visit folder) in a temp dir.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M              # noqa: E402
import maturation_autonomy as A     # noqa: E402

FAILS = []
MOD = "FlowWorks"
OLD = "GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO"
DRIVER = "RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_FIVE"
STEWARD = "RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_FIVE_FAILURES_BACK"
OWN = "RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO"
PASSED = "RIMMANDRAKE_OLD_ITEM_NAMED_BY_A_PASS_ROW_ONLY"


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def site(rows, events):
    """-> a temp root holding the ledger events (one BENCH shard) and FlowWorks' visit_5/rows.jsonl."""
    root = tempfile.mkdtemp(prefix="visitcite_")
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(d)
    with open(os.path.join(d, "BENCH.jsonl"), "w", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(e) + "\n" for e in events))
    v = os.path.join(M.mod_dir(root, MOD), M.INGAME_DIR, "visit_5")
    os.makedirs(v)
    if rows is not None:
        with open(os.path.join(v, "rows.jsonl"), "w", encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r) + "\n" for r in rows))
    return root


VISIT5_ROWS = [
    {"test": "sc_fill_front", "verdict": "PASS"},
    {"test": "sc_hole_prison", "verdict": "FAIL", "class": "MOD", "filed": OWN, "superseded_by_rerun": True},
    {"test": "sc_hung_bridge", "verdict": "FAIL", "class": "MOD", "filed": OLD,
     "row": "GRATE_fire_burns_people_above grate 5 vs solid 13"},
    {"test": "sc_old_pass", "verdict": "PASS", "filed": PASSED},
]
EVENTS = [
    {"event": "file", "id": OLD, "title": "grate fire: solid deck burns too", "ts": "2026-10-23T17:10:52Z"},
    {"event": "block", "id": OLD, "ts": "2026-10-29T07:54:14Z"},
    {"event": "file", "id": PASSED, "title": "an old item a PASS row names", "ts": "2026-10-23T17:10:52Z"},
    {"event": "file", "id": DRIVER, "title": "drive visit 5", "ts": "2026-11-21T10:00:00Z"},
    {"event": "file", "id": OWN, "title": "awake prisoner meal", "caused_by": DRIVER, "ts": "2026-11-21T12:00:00Z"},
    {"event": "close", "id": OWN, "ts": "2026-11-21T13:00:00Z"},
    {"event": "file", "id": STEWARD, "title": "route visit 5 back", "ts": "2026-11-21T12:30:00Z"},
]


def opened(root):
    """The road back the tick opens when the visit-5 steward launches (the parent wrote the literal dict)."""
    row = {"mod": MOD, "stage": "in_game", "visit": 5}
    if hasattr(A, "open_road_back"):
        return A.open_road_back(root, row, STEWARD, 100)
    return {"caused_by": STEWARD, "at": 100, "from": "in_game"}


def wait(root, rb):
    s = {"road_back": rb, "ingame_auto": [{"item": DRIVER, "at": 50}]}
    row = {"mod": MOD, "stage": "in_game", "visit": 5}
    open_items = lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw)    # noqa: E731
    got = A._road_back(s, row, open_items, 200, moved=True)
    return got, row, s


def t_failed_line_on_old_item_holds_the_next_visit():
    """The visit-5 case: every item caused by the driver or steward is closed; the old item the FAIL line names is open.
    The road back holds and its fixer goes to the old item; the road back does not close."""
    root = site(VISIT5_ROWS, EVENTS)
    try:
        got, row, s = wait(root, opened(root))
        check(got is True, "failed-line-on-old-item-holds-the-next-visit: _road_back decides the row", got)
        check(row.get("fix_item") == OLD, "failed-line-on-old-item-holds-the-next-visit: the fixer goes to %s" % OLD,
              row.get("fix_item"))
        check("road_back" in s, "failed-line-on-old-item-holds-the-next-visit: the road back stays open")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_closed_cited_item_holds_nothing():
    """Once the old item is closed (or superseded), the road back of a moved mod closes: the next visit goes."""
    for ev in ("close", "supersede"):
        root = site(VISIT5_ROWS, EVENTS + [{"event": ev, "id": OLD, "ts": "2026-11-22T04:30:53Z"}])
        try:
            got, row, s = wait(root, opened(root))
            check(got is False and "road_back" not in s,
                  "closed-cited-item-holds-nothing: %s old item, the road back closes" % ev, (got, row.get("why")))
        finally:
            shutil.rmtree(root, ignore_errors=True)


def t_only_failed_lines_are_cited():
    """A PASS row's `filed` is no wait; a FAIL or UNMEASURED row's is, as a string or a list of names."""
    rows = [{"test": "a", "verdict": "PASS", "filed": PASSED},
            {"test": "b", "verdict": "UNMEASURED", "filed": [OLD, "not an item name"]}]
    root = site(rows, [])
    try:
        got = M.visit_cited_items(root, MOD, 5) if hasattr(M, "visit_cited_items") else None
        check(got == [OLD], "only-failed-lines-are-cited: one UNMEASURED line's list gives [%s]" % OLD, got)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_owner_named_item_is_cited():
    """Pyrelands visit 5 (2026-11-22): a failed row named its old item only in `owner`, never in `filed`, and the road
    back left it out. A failed row's `owner` is cited like its `filed`; a PASS row's `owner` is not."""
    rows = [{"test": "a", "verdict": "PASS", "owner": PASSED},
            {"test": "b", "verdict": "UNMEASURED", "class": "HARNESS", "owner": OLD},
            {"test": "c", "verdict": "UNMEASURED", "owner": "BENCH", "filed": OWN}]
    root = site(rows, [])
    try:
        got = M.visit_cited_items(root, MOD, 5)
        check(got == [OLD, OWN], "owner-named-item-is-cited: a failed row's owner is cited, a PASS row's is not, "
              "a seat name is not an item", got)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_unreadable_visit_record_is_said():
    """No rows.jsonl at the steward's launch: the road back records why it cites nothing (never a silent [])."""
    root = site(None, EVENTS)
    try:
        rb = opened(root)
        check(rb.get("cited") is None and "rows.jsonl" in str(rb.get("cited_unread") or ""),
              "unreadable-visit-record-is-said: cited_unread names rows.jsonl", rb)
        check(rb.get("caused_by") == STEWARD and rb.get("from") == "in_game",
              "unreadable-visit-record-is-said: the road back still opens on the steward item", rb)
    finally:
        shutil.rmtree(root, ignore_errors=True)


HIS = "RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE"
MINE = "RIMMANDRAKE_FIX_A_PLAIN_ITEM_STILL_OPEN_AFTER_ITS_FIXER"
HIS_EVENTS = [
    {"event": "file", "id": DRIVER, "title": "drive visit 5", "ts": "2026-11-22T10:00:00Z"},
    {"event": "file", "id": STEWARD, "title": "route visit 5 back", "ts": "2026-11-22T12:30:00Z"},
    {"event": "file", "id": HIS, "title": "ullai herd reads as grey rubble", "caused_by": DRIVER, "needs": "owner",
     "ts": "2026-11-22T14:44:26Z"},
    {"event": "needs", "id": HIS, "to": "owner", "ts": "2026-11-22T23:07:51Z"},
]
HIS_ROWS = [{"test": "sc_ullai", "verdict": "PASS"}, {"test": "sc_sprayer", "verdict": "FAIL", "class": "SITE"}]


def his_wait(rows, events, fixed, cited_unread=False):
    """-> (_road_back's answer, row, state) on the Pyrelands visit-5 shape: FIXED holds the items whose fixer ran."""
    root = site(rows, events)
    try:
        rb = opened(root)
        if cited_unread:
            rb.pop("cited", None)
            rb["cited_unread"] = "rows.jsonl cannot be read"
        s = {"road_back": rb, "ingame_auto": [{"item": DRIVER, "at": 50}],
             "fixers": {i: {"item": i, "unit": "u-" + i} for i in fixed}}
        row = {"mod": MOD, "stage": "in_game", "visit": 5, "decision": "launch"}
        open_items = lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw)    # noqa: E731
        return A._road_back(s, row, open_items, 200, moved=True), row, s
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_spent_owner_item_does_not_hold_the_visit():
    """Pyrelands visit 5 (2026-11-22): the one open item waits for his art pick, its fixer ran, no failed line cites it:
    the next visit is not held, the road back stays open, and the row names the item as his."""
    got, row, s = his_wait(HIS_ROWS, HIS_EVENTS, [HIS])
    check(got is False and row.get("decision") == "launch",
          "spent-owner-item-does-not-hold-the-visit: the row is not decided (no fixer_spent)", (got, row.get("decision")))
    check("road_back" in s, "spent-owner-item-does-not-hold-the-visit: the road back stays open")
    check(row.get("owner_items") == [HIS], "spent-owner-item-does-not-hold-the-visit: owner_items lists it",
          row.get("owner_items"))


def t_cited_owner_item_still_holds():
    """The planted fault: the same owner item, cited by a failed line (a bar the visit decides rests on it), or a visit
    record that could not be read, still holds the next visit."""
    rows = HIS_ROWS + [{"test": "sc_ullai_look", "verdict": "FAIL", "class": "MOD", "filed": HIS}]
    got, row, s = his_wait(rows, HIS_EVENTS, [HIS])
    check(got is True and row.get("decision") == "fixer_spent",
          "cited-owner-item-still-holds: a cited owner item holds as fixer_spent", (got, row.get("decision")))
    got, row, s = his_wait(HIS_ROWS, HIS_EVENTS, [HIS], cited_unread=True)
    check(got is True and row.get("decision") == "fixer_spent",
          "cited-owner-item-still-holds: an unread visit record holds", (got, row.get("decision")))


def t_owner_item_gets_its_fixer_first():
    """An owner item that has not had its fixer run gets it (the judge's look comes before his pick)."""
    got, row, s = his_wait(HIS_ROWS, HIS_EVENTS, [])
    check(got is True and row.get("fix_item") == HIS and row.get("aut") == "fixer",
          "owner-item-gets-its-fixer-first: the fixer goes to the owner item", (got, row.get("fix_item")))


def t_other_spent_item_still_holds():
    """A spent item that is not his still holds; its why names it alone, and the owner item is listed apart."""
    ev = HIS_EVENTS + [{"event": "file", "id": MINE, "title": "a plain item", "caused_by": DRIVER,
                        "ts": "2026-11-22T15:00:00Z"}]
    got, row, s = his_wait(HIS_ROWS, ev, [HIS, MINE])
    check(got is True and row.get("decision") == "fixer_spent", "other-spent-item-still-holds: fixer_spent",
          (got, row.get("decision")))
    check(MINE in str(row.get("why")) and HIS not in str(row.get("why")) and row.get("owner_items") == [HIS],
          "other-spent-item-still-holds: the why names only the plain item, owner_items the owner item",
          (row.get("why"), row.get("owner_items")))


RAID_ITEM = "RIMMANDRAKE_TRACE_A_RAIDER_WHO_LEFT_THE_DRAINED_MOAT"
RAID_EVENTS = [
    {"event": "file", "id": DRIVER, "title": "drive visit 5", "ts": "2026-11-22T10:00:00Z"},
    {"event": "file", "id": STEWARD, "title": "route visit 5 back", "ts": "2026-11-22T12:30:00Z"},
    {"event": "file", "id": RAID_ITEM, "title": "a held raider left the moat", "caused_by": DRIVER, "needs": "bridge",
     "ts": "2026-11-22T14:44:26Z"},
]
RAID_ROWS = [{"test": "sc_moat_raid", "verdict": "FAIL", "class": "MOD", "filed": RAID_ITEM},
             {"test": "sc_fill", "verdict": "PASS"}]


def raid_wait(rows, fixed, paused=True, tag=True):
    """-> (_road_back's answer, row, state) on FlowWorks visit 9's shape: RAID_ITEM open, caused by the driver and cited
    by the raid scene's failed row."""
    root = site(rows, RAID_EVENTS)
    try:
        tt = {"tests": {"sc_moat_raid": dict({"kind": "live_minimal", "stage": "6"},
                                             **({"stages_raid": "six raiders at a moat"} if tag else {})),
                        "sc_fill": {"kind": "live_minimal", "stage": "6"}}}
        d = os.path.join(M.mod_dir(root, MOD), "version")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "test_table.json"), "w", encoding="utf-8") as fh:
            json.dump(tt, fh)
        sw = os.path.join(root, "raid_pause.json")
        with open(sw, "w", encoding="utf-8") as fh:
            json.dump({"paused": paused, "why": "t", "allow": [], "chains": {}}, fh)
        s = {"road_back": opened(root), "ingame_auto": [{"item": DRIVER, "at": 50}],
             "fixers": {i: {"item": i, "unit": "u-" + i} for i in fixed}}
        row = {"mod": MOD, "stage": "in_game", "visit": 5, "decision": "launch"}
        open_items = lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw)    # noqa: E731
        return A._road_back(s, row, open_items, 200, moved=True,
                            paused_items=lambda ids: M.paused_scene_items(root, MOD, ids, path=sw)), row, s
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_paused_scene_item_does_not_hold_the_visit():
    """FlowWorks visit 9 (2026-11-23): the one open item is cited by a paused raid scene's failed row alone; once its
    fixer ran, the next visit is not held, and the row names the item."""
    got, row, s = raid_wait(RAID_ROWS, [RAID_ITEM])
    check(got is False and row.get("decision") == "launch",
          "paused-scene-item-does-not-hold-the-visit: the row is not decided (no fixer_spent)", (got, row.get("decision")))
    check("road_back" in s and row.get("paused_raid_items") == [RAID_ITEM],
          "paused-scene-item-does-not-hold-the-visit: the road back stays open and the row lists the item",
          row.get("paused_raid_items"))
    got, row, s = raid_wait(RAID_ROWS, [])
    check(got is True and row.get("fix_item") == RAID_ITEM,
          "paused-scene-item-does-not-hold-the-visit: it gets its one fixer run first", (got, row.get("fix_item")))


def t_paused_scene_item_holds_when_not_paused():
    """The planted faults: the pause lifted, the scene untagged, or the item also cited by a failed row of a scene that
    runs: it holds as fixer_spent."""
    for what, rows, kw in (("the pause is lifted", RAID_ROWS, {"paused": False}),
                           ("the scene has no tag", RAID_ROWS, {"tag": False}),
                           ("a scene that runs cites it too", RAID_ROWS + [
                               {"test": "sc_fill", "verdict": "FAIL", "class": "MOD", "owner": RAID_ITEM}], {})):
        got, row, s = raid_wait(rows, [RAID_ITEM], **kw)
        check(got is True and row.get("decision") == "fixer_spent",
              "paused-scene-item-holds-when-not-paused: %s" % what, (got, row.get("decision")))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_failed_line_on_old_item_holds_the_next_visit, t_closed_cited_item_holds_nothing,
              t_only_failed_lines_are_cited, t_owner_named_item_is_cited, t_unreadable_visit_record_is_said,
              t_spent_owner_item_does_not_hold_the_visit, t_cited_owner_item_still_holds,
              t_owner_item_gets_its_fixer_first, t_other_spent_item_still_holds,
              t_paused_scene_item_does_not_hold_the_visit, t_paused_scene_item_holds_when_not_paused):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001  a test that raises is a FAIL with its cause
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_visit_wait_cited_items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
