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


CHECKS = (a_station_request_draws_a_clean_station_and_positions_are_relative,
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
