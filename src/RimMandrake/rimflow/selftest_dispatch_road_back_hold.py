#!/usr/bin/env python3
"""selftest_dispatch_road_back_hold: the promises of design/specs/2026-11-25-tick-launches-road-back-hold/boundary.md,
one test per promise, each named as the promise is. A mod whose only non-build exit refusal is the stage record's road
back (clause road_back_items) gets its one holder bundle on the open road-back items from the tick (item
RIMMANDRAKE_LAUNCH_ROAD_BACK_BUNDLE_BY_TICK_READS_BLOCKED: Explosive Knockback 0.2.0 read "blocked (paused): refused
by road_back_items, not build work" at 3:56 PM PST 2026-11-25 with both games free and nothing live). No game, no
network, no real launch; every file is in a temp root.

    python3 src/RimMandrake/rimflow/selftest_dispatch_road_back_hold.py      # "selftest_dispatch_road_back_hold: PASS"
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="dispatch_rbhold_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
os.environ["RM_WORK_BUNDLE_DIR"] = os.path.join(TMP, "_bundles")
os.environ.pop("RM_ROLE_UNIT", None)
import maturation as M  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402
import maturation_dispatch as MD  # noqa: E402
import work_bundle as WB  # noqa: E402

FAILS = []
MOD = "RMod"
NOW = 1795651200.0      # 2026-11-25 ~4:00 PM PST, pinned
CFG = {"advancing": [MOD], "cap_tokens": 3_750_000, "max_live": 4, "launch_tries": 3, "settle_s": 180, "stage_ceiling_tokens": 25_000_000,
       "seat": "BENCH", "model": "opus"}
DRIVER = "RIMMANDRAKE_DRIVE_RMOD_IN_GAME_VISIT_ONE"
RENAME = "RIMMANDRAKE_RENAME_RMOD_DEFS_OPEN_ONE"
LIVE = "RIMMANDRAKE_FIND_RMOD_SCAR_LIVE_ONLY_ONE"
HUNT = "RIMMANDRAKE_HUNT_RMOD_GOOD_UNMOVED_THREE_SIGHTINGS"
WAITED = "RIMMANDRAKE_CHECK_RMOD_WAITED_OFFLINE_ITEM_ONE"
T0 = 1795600000000000000
MOVE_AT = "2026-11-25T09:58:04-08:00"


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def ev(k, event, i, **kw):
    return dict({"seat": "BENCH", "event": event, "id": i, "ts": "2026-11-25T15:%02d:00Z" % k, "tsn": T0 + k}, **kw)


BASE = [ev(1, "file", DRIVER, title="visit 1"),
        ev(2, "file", RENAME, caused_by=DRIVER, needs="deploy", title="rename the scar defs"),
        ev(3, "file", LIVE, caused_by=DRIVER, needs="game-up", title="scar missing one run in three"),
        ev(4, "file", HUNT, caused_by=DRIVER, needs="game-up", title="kind C hunt"),
        ev(5, "wait", HUNT, until="2026-12-02T08:00:00Z", reason="the next in-game visit's long batch")]


def make(name, events):
    """A fresh root with RMod at the offline build, sent back from in_game by the driver's item; these ledger events."""
    root = os.path.join(TMP, name)
    shutil.rmtree(root, ignore_errors=True)
    c = "design/concepts/%s/" % MOD
    put(root, c + "version/VERSION.json", {"version": "0.2.0"})
    put(root, c + "version/stage_record.json", {
        "mod": MOD, "version": "0.2.0", "stage": "offline_build", "since": MOVE_AT,
        "moves": [{"from": "blind_challenge", "to": "in_game", "at": "2026-11-25T06:33:02-08:00"},
                  {"from": "in_game", "to": "offline_build", "at": MOVE_AT, "by": "BENCH", "item": DRIVER,
                   "why": "steward act: road back"}]})
    put(root, c + "journal.md", "# journal\n")
    put(root, "infrastructure/state/ledger/events/BENCH.jsonl", "".join(json.dumps(e) + "\n" for e in events))
    return root


def hold_of(open_ids=(RENAME,), stage6=(LIVE, HUNT), unread=(), waits=None):
    return {"open": [{"id": i, "title": i, "needs": "deploy"} for i in open_ids],
            "stage6": [{"id": i, "title": i, "needs": "game-up"} for i in stage6], "unread": list(unread),
            "at": MOVE_AT, "move_at": M._ts(MOVE_AT) if hasattr(M, "_ts") else None, "waits": dict(waits or {})}


def facts(hold=None, others=("road_back_items",), live=()):
    return {MOD: {"mod": MOD, "stage": "offline_build", "version": "0.2.0", "owed": "blocked",
                  "other_refusals": list(others), "build_refusals": [], "hand_steps": [], "refused_bars": [],
                  "bars_total": 4, "walk_bars": [], "live_units": list(live), "last_end": NOW - 3600,
                  "observed": {"road_back_items": "road back in_game -> offline_build"},
                  "road_back_hold": hold if hold is not None else hold_of()}}


def tick(fs, st=None, pilot=True, pilot_why=None):
    """decide, then the pilot holder layer, as _tick runs them (the autonomy layer leaves a blocked row alone)."""
    st = st if st is not None else {"mods": {}}
    rows, launches = MD.decide(CFG, st, fs, NOW, (True, "ok"))
    fx = {"account": lambda: (True, "ok"), "pilot": lambda root, mod: pilot,
          "open_items": lambda ids, **kw: []}
    if pilot_why:
        fx["pilot_why"] = pilot_why
    rows, launches = MD.pilot_holders(TMP, CFG, st, fs, rows, launches, NOW, fx)
    return rows[0], launches, st


def ids_of(row):
    return sorted(str(x.get("id") if isinstance(x, dict) else x) for x in row.get("holder_items") or [])


def t_a_road_back_only_refusal_launches_the_holder():
    row, launches, _ = tick(facts())
    check(row.get("decision") == "launch" and MOD in launches and ids_of(row) == [RENAME],
          "exit refused only by road_back_items, one open item that needs deploy, ledger ready, nothing live: one "
          "holder launch on the open road-back items", row)
    root = make("whole", BASE)      # the same from the stage record and the ledger, through build_facts
    f = M.build_facts(root, MOD)
    rb = f.get("road_back_hold") or {}
    check([x["id"] for x in rb.get("open") or []] == [RENAME] and sorted(x["id"] for x in rb.get("stage6") or [])
          == sorted([LIVE, HUNT]) and not rb.get("unread"),
          "build_facts carries the stage record's road-back hold: its open items and its Stage 6 items", rb)
    check(HUNT in (rb.get("waits") or {}) and "2026-12-02" in str(rb["waits"][HUNT]),
          "build_facts names each road-back item on a dated wait with its date", rb.get("waits"))
    f.update(live_units=[], last_end=NOW - 3600)
    row, launches, _ = tick({MOD: f})
    check(row.get("decision") == "launch" and ids_of(row) == [RENAME],
          "the tick over build_facts launches the holder on the open road-back items", row)


def t_a_hold_among_the_refusals_reads_held():
    row, launches, _ = tick(facts(others=("hold", "road_back_items")))
    check(row.get("decision") == "held" and MOD not in launches and not row.get("holder_items"),
          "a Conductor hold beside the road back reads held and launches nothing", row)
    row, launches, _ = tick(facts(others=("version_matches", "road_back_items")))
    check(row.get("decision") == "blocked" and MOD not in launches,
          "another non-build refusal beside the road back stays blocked", row)


def t_an_unread_road_back_says_could_not_look():
    row, launches, _ = tick(facts(hold=hold_of(unread=("the ledger (OSError: gone)",))))
    check(row.get("decision") == "blind" and "could not look" in str(row.get("why")) and MOD not in launches,
          "a road back that could not be read launches nothing and says could not look", row)
    fs = facts()
    fs[MOD].pop("road_back_hold")
    row, launches, _ = tick(fs)
    check(row.get("decision") == "blind" and "could not look" in str(row.get("why")) and MOD not in launches,
          "a road_back_items refusal with no hold reading launches nothing and says could not look", row)


def t_a_spent_holder_on_the_same_set_launches_nothing():
    st = {"mods": {MOD: {"holder_road_back": [{"at": NOW - 1800, "ids": [RENAME], "item": RENAME,
                                               "unit": "rm-holder-1", "stage": "offline_build"}]}}}
    row, launches, _ = tick(facts(), st)
    check(row.get("decision") == "holder_spent" and MOD not in launches,
          "a holder that ended with the same open set still open launches no second run", row)
    st = {"mods": {MOD: {"holder_road_back": [{"at": M._ts(MOVE_AT) - 60, "ids": [RENAME], "item": RENAME,
                                               "unit": "rm-holder-0", "stage": "in_game"}]}}}
    row, launches, _ = tick(facts(), st)
    check(row.get("decision") == "launch" and MOD in launches,
          "a holder run from before this road back opened does not spend it", row)


def t_a_live_run_on_the_mod_is_a_wait():
    row, launches, _ = tick(facts(live=("rm-detached-bench-x-1",)))
    check(row.get("decision") == "live" and MOD not in launches, "a live run on the mod is a wait", row)


def t_an_item_on_a_dated_wait_is_left_out():
    w = {WAITED: "until 2026-12-02T08:00:00Z: the next visit"}
    row, launches, _ = tick(facts(hold=hold_of(open_ids=(RENAME, WAITED), waits=w)))
    check(row.get("decision") == "launch" and ids_of(row) == [RENAME],
          "an open item on a dated wait is left out of the holder's items", row)
    row, launches, _ = tick(facts(hold=hold_of(open_ids=(WAITED,), waits=w)))
    check(row.get("decision") == "road_back_wait" and MOD not in launches and WAITED in str(row.get("waits_on"))
          and "2026-12-02" in str(row.get("waits_on")),
          "an item on a dated wait alone launches no run, and the line names what the mod waits on", row)
    check("road_back_wait" in AUT.WAIT, "road_back_wait is a named wait (its class is wait, never a pause)")
    check("not build work" not in str(row.get("why")), "the wait's line is not the old 'not build work'", row)


def t_a_non_pilot_names_the_hand_route():
    row, launches, _ = tick(facts(), pilot=False)
    check(MOD not in launches and "./pipe bundle %s" % MOD in str(row.get("why")) + str(row.get("need")),
          "a mod that is not a ledger pilot launches nothing and its line names the hand bundle", row)
    check("not a ledger pilot" in str(row.get("why")), "its line says it is not a ledger pilot", row.get("why"))
    no = "RMod's mod ledger is not ready (modledger_backfill_accept.py: FAIL 2 of 7)"
    row, launches, _ = tick(facts(), pilot=False, pilot_why=lambda root, mod: no)
    check(MOD not in launches and no in str(row.get("why")) and no in str(row.get("need")),
          "a pilot whose mod ledger is not ready launches nothing and its line names the readiness failure", row)


def t_a_road_back_item_with_no_home_is_a_bundle_member():
    items = {RENAME: {"id": RENAME, "state": "proposed", "home": None, "caused_by": DRIVER},
             "RIMMANDRAKE_FIX_RMOD_HOMED_ONE": {"id": "RIMMANDRAKE_FIX_RMOD_HOMED_ONE", "state": "proposed",
                                                "home": {"home": "mod:%s" % MOD}},
             DRIVER: {"id": DRIVER, "state": "done", "home": None}}

    def reading(it):
        return {"mod": MOD} if (it.get("home") or {}).get("home") == "mod:%s" % MOD else {"mod": None}
    system, ids, why = WB.resolve(MOD, items, [MOD], reading, road_back=lambda mod: [RENAME])
    check(system == "mod:%s" % MOD and RENAME in ids and "RIMMANDRAKE_FIX_RMOD_HOMED_ONE" in ids,
          "`./pipe bundle <Mod>` takes the open road-back items of the mod beside its homed tickets", (system, ids))
    system, ids, why = WB.resolve(MOD, items, [MOD], reading, road_back=lambda mod: [DRIVER])
    check(DRIVER not in ids, "a road-back item that is closed is no member", ids)

    def blind(mod):
        raise OSError("ledger gone")
    system, ids, why = WB.resolve(MOD, items, [MOD], reading, road_back=blind)
    check(system == "mod:%s" % MOD and "could not look" in why and "RIMMANDRAKE_FIX_RMOD_HOMED_ONE" in ids,
          "a road back that cannot be read keeps the homed tickets and says could not look", (ids, why))
    rc, rec = WB.holder_bundle(MOD, RENAME, [RENAME], [], NOW)
    check(rc == 0 and RENAME in rec["members"], "the tick's holder bundle holds the homeless road-back item", rec)


def main():
    try:
        for t in (t_a_road_back_only_refusal_launches_the_holder, t_a_hold_among_the_refusals_reads_held,
                  t_an_unread_road_back_says_could_not_look, t_a_spent_holder_on_the_same_set_launches_nothing,
                  t_a_live_run_on_the_mod_is_a_wait, t_an_item_on_a_dated_wait_is_left_out,
                  t_a_non_pilot_names_the_hand_route, t_a_road_back_item_with_no_home_is_a_bundle_member):
            try:
                t()
            except Exception as e:  # noqa: BLE001  a crash is a FAIL of that test, the others still run
                import traceback
                check(False, "%s raised" % t.__name__, "%s: %s %s" % (type(e).__name__, e,
                                                                      traceback.format_exc()[-600:]))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_dispatch_road_back_hold: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
