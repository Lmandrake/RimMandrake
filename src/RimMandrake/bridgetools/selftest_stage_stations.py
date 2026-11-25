#!/usr/bin/env python3
"""Offline acceptance of the station allocator (src/RimMandrake/Utils/scene_stations.py), item
RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS. Pure: no game. Promises: design/specs/2026-11-23-bridge-v2/boundary.md
§THE STATION ALLOCATOR; each check carries the name of its promise.

Planted faults that must turn this red (seen 2026-11-24, readings in
design/specs/2026-11-23-bridge-v2/live/stage_map/plants.txt): margins left out of the overlap test
(no_two_stations_overlap_margins_included); a pocket stage given to a raid scene (a_pocket_stage_refuses_a_scene_that_fires_an_incident)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

import scene_stations as S  # noqa: E402


def refused(name, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except S.Refused as e:
        assert e.name == name, "refused %s, not %s: %s" % (e.name, name, e)
        return e
    raise AssertionError("not refused (%s wanted)" % name)


def grown(st):
    x, z, w, h = st["rect"]
    m = st["margin"]
    return (x - m, z - m, w + 2 * m, h + 2 * m)


def no_two_stations_overlap_margins_included():
    st = S.Stage("t", "settlement", (60, 60))
    got = [st.give(size=(9, 7), margin=m, scene="s%d" % i) for i, m in enumerate((3, 0, 2, 5, 1, 4))]
    for i, a in enumerate(got):
        for b in got[i + 1:]:
            assert not S._overlap(grown(a), grown(b)), "%s and %s overlap with their margins" % (a, b)
    # a station with no margin next to one with a margin still keeps the other's margin clear
    a, b = got[0], got[1]
    assert not S._overlap(a["rect"], grown(b)) and not S._overlap(b["rect"], grown(a)), (a, b)


def a_request_that_cannot_fit_says_why():
    st = S.Stage("t", "settlement", (30, 30))
    e = refused("NO_ROOM", st.give, size=(40, 5))
    assert "30x30" in e.why and "40x5" in e.why, e.why
    for _ in range(4):           # 28 usable cells: 12 + 4 + 12 fits twice in each direction
        st.give(size=(12, 12), margin=2)
    e = refused("NO_ROOM", st.give, size=(12, 12), margin=2)
    assert "4 given" in e.why and "release" in e.why, e.why


def a_retired_station_is_never_given_again():
    st = S.Stage("t", "settlement", (20, 20))
    a = st.give(size=(16, 16))
    st.retire(a["id"], "a corpse the clean could not remove")
    refused("RETIRED", st.release, a["id"])
    e = refused("NO_ROOM", st.give, size=(16, 16))
    assert "1 retired" in e.why, e.why
    st2 = S.Stage("t", "settlement", (60, 60))
    first = st2.give(size=(10, 10))
    st2.retire(first["id"], "a fire that would not go out")
    for _ in range(5):
        g = st2.give(size=(10, 10))
        assert g["id"] != first["id"] and not S._overlap(g["rect"], first["rect"]), g
    refused("BAD_ARGS", st2.retire, g["id"], "")


def a_station_near_the_edge_is_refused_when_the_plan_asks_distance():
    st = S.Stage("t", "settlement", (50, 50))
    for _ in range(3):
        g = st.give(size=(6, 6), edge=12, margin=1)
        x, z, w, h = g["rect"]
        for d in (x, z, 50 - (x + w), 50 - (z + h)):
            assert d >= 12 + S.EDGE_BAND, "station %s is %d cells from the edge, 12 were asked" % (g["rect"], d)
    e = refused("NO_ROOM", S.Stage("t", "settlement", (30, 30)).give, size=(6, 6), edge=13)
    assert "13 cells from the edge" in e.why, e.why
    near = S.Stage("t", "settlement", (30, 30)).give(size=(6, 6))
    assert near["rect"][0] == S.EDGE_BAND, "with no distance asked the allocator may use the cells by the edge: %s" % (near,)


def a_pocket_stage_refuses_a_scene_that_fires_an_incident():
    p = S.Stage("p", "pocket", (40, 40))
    e = refused("POCKET_CANNOT_SERVE", p.give, size=(8, 8), incident=True, scene="sc_raid")
    assert "incident" in e.why and "settlement" in e.why, e.why
    for need in ("edge", "home", "weather"):
        refused("POCKET_CANNOT_SERVE", p.give, size=(8, 8), **{need: True})
    assert p.stations == [], "a refused request took a station: %s" % p.stations
    ok = p.give(size=(8, 8), scene="sc_stand_still")
    assert ok["kind"] == "pocket" and ok["shared_map"] is False, ok
    assert S.Stage("s", "settlement", (40, 40)).give(size=(8, 8), incident=True, edge=4)["kind"] == "settlement"


def a_colony_station_is_marked_shared_map():
    c = S.Stage("walk", "colony", (100, 100)).give(size=(10, 10), incident=True)
    assert c["shared_map"] is True and c["kind"] == "colony", c
    for kind in ("settlement", "pocket"):
        assert S.Stage("x", kind, (40, 40)).give(size=(5, 5))["shared_map"] is False


def a_released_station_is_given_again_and_retirement_survives_a_reload():
    st = S.Stage("RM_Stage_quick", "settlement", (40, 40))
    a = st.give(size=(10, 10), margin=2)
    b = st.give(size=(10, 10), margin=2)
    st.release(a["id"])
    again = st.give(size=(10, 10), margin=2)
    assert again["id"] == a["id"] and again["rect"] == a["rect"], (a, again)
    st.retire(b["id"], "a reservation that would not clear")
    back = S.Stage.from_json(st.to_json())
    assert back.kind == "settlement" and back.size == (40, 40) and back.name == "RM_Stage_quick"
    refused("RETIRED", back.release, b["id"])
    for _ in range(3):
        g = back.give(size=(10, 10), margin=2)
        assert g["id"] != b["id"] and not S._overlap(grown(g), grown(b)), g
    refused("BAD_STATE", S.Stage.from_json, '{"schema": "other"}')


def a_bad_request_is_refused_by_name():
    refused("UNKNOWN_MAP_KIND", S.Stage, "t", "space", (40, 40))
    refused("BAD_ARGS", S.Stage, "t", "settlement", (2, 40))
    st = S.Stage("t", "settlement", (40, 40))
    refused("BAD_ARGS", st.give, size=(0, 4))
    refused("BAD_ARGS", st.give, size=(4, 4), margin=-1)
    e = refused("BAD_ARGS", st.give, size=(4, 4), margn=2)
    assert "margn" in e.why, e.why
    refused("UNKNOWN_STATION", st.release, "st99")
    assert st.stations == []


CHECKS = (no_two_stations_overlap_margins_included, a_request_that_cannot_fit_says_why, a_retired_station_is_never_given_again,
          a_station_near_the_edge_is_refused_when_the_plan_asks_distance, a_pocket_stage_refuses_a_scene_that_fires_an_incident,
          a_colony_station_is_marked_shared_map, a_released_station_is_given_again_and_retirement_survives_a_reload,
          a_bad_request_is_refused_by_name)


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
    print("selftest_stage_stations: %d checks passed" % passed)
    return int(passed != len(CHECKS))


if __name__ == "__main__":
    raise SystemExit(main())
