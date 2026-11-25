#!/usr/bin/env python3
"""selftest_maturation_road_back_hold: the promises of design/specs/2026-11-25-road-back-holds-stage-exit/boundary.md,
one test per promise, each named as the promise is. A mod sent back down a road back does not pass the forward exit of
the stage it was sent to while a repair item of that road back is open
(RIMMANDRAKE_HOLD_MOD_AT_ROAD_BACK_STAGE_AND_LET_BUNDLE_BRIEF_START: Explosive Knockback 0.2.0, 2026-11-25 10:00 AM
PST). No game, no network; every file is in a temp root."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="mat_rbhold_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
os.environ.pop("RM_ROLE_UNIT", None)
import maturation as M  # noqa: E402

FAILS = []
MOD = "RMod"
DRIVER = "RIMMANDRAKE_DRIVE_RMOD_IN_GAME_VISIT_ONE"
T0 = 1795600000000000000


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def lines(rows):
    return "".join(json.dumps(r) + "\n" for r in rows)


def ev(k, event, i, **kw):
    return dict({"seat": "BENCH", "event": event, "id": i, "ts": "2026-11-25T15:%02d:00Z" % k, "tsn": T0 + k}, **kw)


def make(name, events, move=None, stage="offline_build"):
    """A fresh root with RMod at `stage`, its newest move `move` (default: in_game -> offline_build by the driver's
    item), and these ledger events on one shard."""
    root = os.path.join(TMP, name)
    shutil.rmtree(root, ignore_errors=True)
    c = "design/concepts/%s/" % MOD
    mv = move if move is not None else {
        "from": "in_game", "to": "offline_build", "at": "2026-11-25T09:58:04-08:00", "by": "BENCH", "item": DRIVER,
        "why": "steward act: road back for RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE and the scar fault"}
    put(root, c + "version/VERSION.json", {"version": "0.2.0"})
    put(root, c + "version/stage_record.json", {
        "mod": MOD, "version": "0.2.0", "stage": stage, "since": "2026-11-25T09:58:04-08:00",
        "moves": [{"from": "blind_challenge", "to": "in_game", "at": "2026-11-25T06:33:02-08:00"}, mv]})
    put(root, c + "journal.md", "# journal\n")
    put(root, "infrastructure/state/ledger/events/BENCH.jsonl", lines(events))
    return root


BASE = [ev(1, "file", DRIVER, title="visit 1"),
        ev(2, "file", "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE", caused_by=DRIVER, needs="deploy", title="rename"),
        ev(3, "file", "RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE", caused_by="SOMETHING_ELSE_ITEM", title="named"),
        ev(4, "file", "RIMMANDRAKE_FIND_RMOD_SCAR_LIVE_ONLY_ONE", caused_by=DRIVER, needs="game-up", title="live")]


def hold_of(root, to="blind_challenge"):
    e = M.evaluate(root, MOD, to)
    ref = [r for r in e["verdict"]["refusals"] if r["clause"] == "road_back_items"]
    passed = [p["clause"] for p in e["verdict"]["passed"]]
    return ref[0] if ref else None, passed


def t_an_open_repair_item_holds_the_stage_exit():
    r, passed = hold_of(make("open", BASE))
    check(r is not None and "road_back_items" not in passed, "an open item of the road back refuses the forward exit",
          passed)
    obs = (r or {}).get("observed") or ""
    check("RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE" in obs, "the refusal names the item filed by the move's item", obs)
    check("RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE" in obs, "the refusal names the item the move's why names", obs)
    root = make("unit", BASE, move={"from": "in_game", "to": "offline_build", "at": "2026-11-25T09:58:04-08:00",
                                    "unit": "rm-detached-bench-test-unit-1", "why": "road back"})
    import detached_helper as DH
    old = DH.read_record
    DH.read_record = lambda u: {"item": DRIVER} if u == "rm-detached-bench-test-unit-1" else None
    try:
        r, _ = hold_of(root)
    finally:
        DH.read_record = old
    check(r is not None and "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE" in (r.get("observed") or ""),
          "a move that names only its run's unit finds the item through the run record", r)


def t_closed_or_dropped_items_do_not_hold():
    done = BASE + [ev(5, "close", "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE"),
                   ev(6, "drop", "RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE")]
    r, passed = hold_of(make("closed", done))
    check(r is None and "road_back_items" in passed, "with each offline item closed or dropped the clause passes", r)
    reopened = done + [ev(7, "live", "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE", result="broken")]
    r, _ = hold_of(make("reopened", reopened))
    check(r is not None and "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE" in (r.get("observed") or ""),
          "a reopened item holds again", r)


def t_a_live_only_item_does_not_hold_an_offline_stage():
    only_live = BASE + [ev(5, "close", "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE"),
                        ev(6, "close", "RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE")]
    r, passed = hold_of(make("live_only", only_live))
    check(r is None and "road_back_items" in passed, "an item that needs the game does not hold an offline stage", r)
    r, _ = hold_of(make("open_names_live", BASE))
    check("RIMMANDRAKE_FIND_RMOD_SCAR_LIVE_ONLY_ONE" in (r or {}).get("observed", "") and "Stage 6" in r["observed"],
          "the refusal names a live-only item as Stage 6 work", r)
    mv = {"from": "pre_human", "to": "in_game", "at": "2026-11-25T09:58:04-08:00", "item": DRIVER, "why": "back"}
    r, _ = hold_of(make("at_six", BASE + [ev(5, "close", "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE"),
                                          ev(6, "close", "RIMMANDRAKE_FIX_RMOD_NAMED_ELSEWHERE_ONE")],
                        move=mv, stage="in_game"), to="pre_human")
    check(r is not None and "RIMMANDRAKE_FIND_RMOD_SCAR_LIVE_ONLY_ONE" in (r.get("observed") or ""),
          "at Stage 6 a live-only item holds", r)


def t_an_item_that_cannot_be_read_holds_and_says_could_not_look():
    root = make("unread", BASE)
    shutil.rmtree(os.path.join(root, "infrastructure/state/ledger/events"))
    r, _ = hold_of(root)
    check(r is not None and "could not look" in (r.get("observed") or ""), "a ledger that cannot be read holds: could "
          "not look", r)
    root = make("unit_unread", BASE, move={"from": "in_game", "to": "offline_build", "unit": "rm-gone-unit",
                                           "at": "2026-11-25T09:58:04-08:00", "why": "road back"})
    import detached_helper as DH
    old = DH.read_record
    DH.read_record = lambda u: None
    try:
        r, _ = hold_of(root)
    finally:
        DH.read_record = old
    check(r is not None and "could not look" in (r.get("observed") or "") and "rm-gone-unit" in r["observed"],
          "a run record that cannot be read for the move's item holds: could not look", r)


def t_a_forward_move_or_another_stage_holds_nothing():
    mv = {"from": "preflight", "to": "offline_build", "at": "2026-11-25T09:58:04-08:00", "item": DRIVER}
    r, passed = hold_of(make("forward", BASE, move=mv))
    check(r is None and "road_back_items" not in passed, "a record that came forward has no road-back clause", passed)
    r, passed = hold_of(make("moved_on", BASE, stage="blind_challenge"), to="in_game")
    check(r is None, "a record no longer at the road back's stage is not held by it", r)
    mv = {"from": "in_game", "to": "offline_build", "at": "2026-11-25T09:58:04-08:00", "why": "a Problem he saw"}
    root = make("hand", BASE, move=mv)
    shutil.rmtree(os.path.join(root, "infrastructure/state/ledger/events"))
    r, passed = hold_of(root)
    check(r is None and "road_back_items" in passed, "a hand road back that names no item reads nothing and holds "
          "nothing", r)


def t_advance_writes_the_item_of_the_run_that_moves():
    import detached_helper as DH
    old, oldenv = DH.read_record, os.environ.get("RM_ROLE_UNIT")
    DH.read_record = lambda u: {"item": "RIMMANDRAKE_MOVE_RMOD_TEST_ITEM_ONE"} if u == "rm-unit-x" else None
    os.environ["RM_ROLE_UNIT"] = "rm-unit-x"
    try:
        check(M.move_item() == "RIMMANDRAKE_MOVE_RMOD_TEST_ITEM_ONE", "move_item reads the run's item", M.move_item())
        os.environ.pop("RM_ROLE_UNIT")
        check(M.move_item() is None, "a hand move has no item", M.move_item())
    finally:
        DH.read_record = old
        if oldenv is not None:
            os.environ["RM_ROLE_UNIT"] = oldenv
    src = open(os.path.join(HERE, "maturation.py"), encoding="utf-8").read()
    check('"item": move_item()' in src, "advance writes the item on each move")


def main():
    try:
        for t in (t_an_open_repair_item_holds_the_stage_exit, t_closed_or_dropped_items_do_not_hold,
                  t_a_live_only_item_does_not_hold_an_offline_stage,
                  t_an_item_that_cannot_be_read_holds_and_says_could_not_look,
                  t_a_forward_move_or_another_stage_holds_nothing, t_advance_writes_the_item_of_the_run_that_moves):
            try:
                t()
            except Exception as e:  # noqa: BLE001  a crash is a FAIL of that test, the others still run
                check(False, "%s raised" % t.__name__, "%s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_maturation_road_back_hold: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
