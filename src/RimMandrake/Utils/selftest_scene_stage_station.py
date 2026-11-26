#!/usr/bin/env python3
"""Selftest of s.stage(station=dict(...)): a scene draws its station from the stage map's allocator
(RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS). The fake game (scene_fake.py); no game, no bridge. Promises:
design/specs/2026-11-23-scene-library/boundary.md §Stations; the allocator's own: selftest_stage_stations.py.
A fake proves what this Python does, never what the game does."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene                      # noqa: E402
import scene_fake as F            # noqa: E402
import scene_stations as ST       # noqa: E402

STAGE = "RM_Stage_quicktest"


def must(ok, what):
    if not ok:
        raise AssertionError(what)


def refused(name, fn, *a, **kw):
    try:
        got = fn(*a, **kw)
    except scene.Refused as e:
        must(e.name == name, "refused %s, want %s: %s" % (e.name, name, e))
        return e
    raise AssertionError("%s was not refused: %r" % (name, got))


def world(kind="settlement", size=(60, 60)):
    scene.LAUNCH.update(mode="script", commit=None, script=None, plant=None)
    g = F.FakeGame(run_until=True)
    g.saves.append(STAGE)
    g.map_size = size
    W = F.FakeWorld(g)
    W.stage_made(STAGE, ST.Stage(STAGE, kind, size).to_json())
    scene.WORLD = W
    return W


def live(W):
    return ST.Stage.from_json(W.stage_state("archmagi.b"))


def a_station_request_draws_a_clean_station_and_positions_are_relative():
    W = world()
    with scene.open("ArchSmall", needs={"map": STAGE}) as s:
        must("its stations are all clean" in " ".join(s.opened[2]["did"]), "%s" % s.opened[2])
        a = s.stage(cast={"digger": dict(kind="Colonist", at=(2, 3))}, station=dict(size=(10, 8), margin=2))
        b = s.stage(things={"lamp": dict(thing="WallLamp", at=(0, 0))}, station=dict(size=(10, 8), margin=2))
        st = live(W)
        given = [x for x in st.stations if x["state"] == "given"]
        must(len(given) == 2, "%s" % st.stations)
        r0, r1 = (tuple(x["rect"]) for x in given)
        must(W.game.cleaned[:2] == ["%d,%d,%d,%d" % r0, "%d,%d,%d,%d" % r1], "the stations were not cleaned before staging: %s" % W.game.cleaned)
        must(a.digger.cell == (r0[0] + 2, r0[1] + 3) and b.lamp.cell == (r1[0], r1[1]), "%s %s %s" % (a, b, given))
        must(not ST._overlap(ST._grow(r0, 2), ST._grow(r1, 2)), "%s %s" % (r0, r1))
    st = live(W)
    must(all(x["state"] == "free" for x in st.stations), "close did not release the stations: %s" % st.stations)
    must(W.game.cleaned[-2:] == ["%d,%d,%d,%d" % r0, "%d,%d,%d,%d" % r1], "close did not clean the stations: %s" % W.game.cleaned)


def a_station_whose_clean_leaves_a_thing_is_retired_and_another_is_given():
    W = world(size=(40, 40))
    first = ST.Stage(STAGE, "settlement", (40, 40)).give(size=(10, 10))["rect"]
    W.game.dirty["%d,%d,%d,%d" % first] = ["Corpse_Human7"]
    with scene.open("ArchSmall", needs={"map": STAGE}) as s:
        c = s.stage(cast={"x": dict(kind="Colonist", at=(0, 0))}, station=dict(size=(10, 10)))
        must(c.x.cell != (first[0], first[1]), "the dirty station was used: %s" % c)
        must(any("retired station st1" in d for d in c.receipt.did), "%s" % c.receipt.did)
    st = live(W)
    must([x["state"] for x in st.stations] == ["retired", "free"] and "Corpse_Human7" in st.stations[0]["why"], "%s" % st.stations)


def a_pocket_stage_refuses_a_raid_scene_before_any_change():
    W = world(kind="pocket")
    with scene.open("ArchSmall", needs={"map": STAGE}) as s:
        refused("POCKET_CANNOT_SERVE", s.stage, cast={"d": dict(kind="Colonist", at=(1, 1))}, station=dict(size=(8, 8), incident=True))
        must(W.game.cleaned == [] and live(W).stations == [], "a refused request changed the stage: %s %s" % (W.game.cleaned, live(W).stations))
        refused("OUTSIDE_STATION", s.stage, cast={"d": dict(kind="Colonist", at=(9, 1))}, station=dict(size=(8, 8)))
        must(live(W).stations == [], "a plan refused for its cells took a station: %s" % live(W).stations)


def a_colony_station_says_shared_map_on_its_receipt():
    world(kind="colony", size=(100, 100))
    with scene.open("ArchSmall", needs={"map": STAGE}) as s:
        c = s.stage(cast={"d": dict(kind="Colonist", at=(1, 1))}, station=dict(size=(8, 8), incident=True))
        must(any(x.startswith("shared map") for x in c.receipt.could_not_look), "%s" % c.receipt.could_not_look)


def a_map_that_is_not_a_made_stage_is_refused_no_stage():
    W = world()
    with scene.open("ArchSmall", needs={"map": "fresh:quicktest"}) as s:
        e = refused("NO_STAGE", s.stage, cast={"d": dict(kind="Colonist", at=(1, 1))}, station=dict(size=(8, 8)))
        must("stage_map.py make" in e.repair, e.repair)
        s.stage(cast={"d": dict(kind="Colonist", at=(1, 1))}, station=(5, 5, 8, 8))     # a rect still works on any map
    W.stage_save("archmagi.b", ST.Stage(STAGE, "settlement", (80, 80)).to_json())
    with scene.open("ArchSmall") as s:
        refused("STAGE_STALE", s.stage, cast={"d": dict(kind="Colonist", at=(1, 1))}, station=dict(size=(8, 8)))


def a_pawn_on_a_station_is_vanished_and_a_pawn_not_cast_is_a_breach():
    W = world(size=(40, 40))
    first = ST.Stage(STAGE, "settlement", (40, 40)).give(size=(10, 10))["rect"]
    W.game.pawns_on["%d,%d,%d,%d" % first] = [{"id": "Human3", "kind": "Colonist"}]      # left by an earlier scene
    with scene.open("ArchSmall", needs={"map": STAGE}) as s:
        c = s.stage(cast={"x": dict(kind="Colonist", at=(0, 0))}, station=dict(size=(10, 10)))
        must(W.game.vanished == ["Human3"], "the pawn on the station was not vanished: %s" % W.game.vanished)
        must(not [d for d in c.receipt.did if d.startswith("BREACH")], "%s" % c.receipt.did)
        W.game.pawns_on[None] = [{"id": c.x.id, "kind": "Colonist"}, {"id": "Muffalo9", "kind": "Muffalo", "faction": None, "position": "70,0,8"}]
        c2 = s.stage(things={"lamp": dict(thing="WallLamp", at=(0, 0))}, station=dict(size=(10, 10)))
        breach = [d for d in c2.receipt.did if d.startswith("BREACH")]
        must(len(breach) == 1 and "Muffalo9" in breach[0], "a wild animal on the stage was not a breach: %s" % c2.receipt.did)
    must(any("BREACH: Muffalo9" in x for x in s.closed_report.did), "the close did not name the breach: %s" % s.closed_report.did)


def a_station_loses_its_roof_before_anything_is_staged():
    """The clean destroys the rock under a mountain roof and leaves that roof unsupported: on the first tick it collapses,
    kills every thing on the station and crushes what the scene staged (RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE:
    24 staged IEDs went off at once and each blast's scar died under the rock)."""
    for station, needs in (((5, 5, 8, 8), "fresh:quicktest"), (dict(size=(10, 8)), STAGE)):
        W = world()
        with scene.open("ArchSmall", needs={"map": needs}) as s:
            n = len(W.game.log)
            c = s.stage(cast={"d": dict(kind="Colonist", at=(1, 1))}, station=station)
            log = W.game.log[n:]
            tools = [t for t, _a in log]
            rect = "%d,%d,%d,%d" % (station if isinstance(station, tuple) else tuple(next(x["rect"] for x in live(W).stations if x["state"] == "given")))
            must(("jawa/set_roof_batch", {"ops": "None:" + rect}) in log, "the station %s kept its roof: %s" % (rect, tools))
            i = tools.index("jawa/set_roof_batch")
            must(tools.index("jawa/destroy_batch") < i < tools.index("jawa/spawn_pawn"), "the roof came off out of order: %s" % tools)
            must(any("roof" in d for d in c.receipt.did), "the receipt does not say the roof came off: %s" % c.receipt.did)
    W = world()
    real = W.game._do
    W.game._do = lambda tool, a: ({"success": False, "cellsFailedVerify": 3, "message": "3 FAILED VERIFY"}
                                  if tool == "jawa/set_roof_batch" else real(tool, a))
    with scene.open("ArchSmall", needs={"map": "fresh:quicktest"}) as s:
        try:
            s.stage(cast={"d": dict(kind="Colonist", at=(1, 1))}, station=(5, 5, 8, 8))
        except scene.Fault as e:
            must(e.name == "NO_CLEAN_STATION" and "roof" in str(e), "%s" % e)
        else:
            raise AssertionError("a roof that stayed on the station staged silently")


CHECKS = (a_station_loses_its_roof_before_anything_is_staged,
          a_pawn_on_a_station_is_vanished_and_a_pawn_not_cast_is_a_breach, a_station_request_draws_a_clean_station_and_positions_are_relative,
          a_station_whose_clean_leaves_a_thing_is_retired_and_another_is_given,
          a_pocket_stage_refuses_a_raid_scene_before_any_change, a_colony_station_says_shared_map_on_its_receipt,
          a_map_that_is_not_a_made_stage_is_refused_no_stage)


def main():
    passed = 0
    for check in CHECKS:
        try:
            check()
        except Exception as e:  # noqa: BLE001 - a crash of a check is its failure, named
            print("FAIL %s: %s: %s" % (check.__name__, type(e).__name__, e))
        else:
            passed += 1
            print("PASS %s" % check.__name__)
    print("selftest_scene_stage_station: %d checks passed" % passed)
    return int(passed != len(CHECKS))


if __name__ == "__main__":
    raise SystemExit(main())
