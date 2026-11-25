#!/usr/bin/env python3
"""Offline acceptance of stamp again (src/RimMandrake/Utils/scene_repeats.py), item RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST.
Pure: no game. Promises: design/specs/2026-11-23-bridge-v2/boundary.md §STAMP AGAIN; each check carries the name of its promise.
It uses the real station allocator (scene_stations.py) and the real verdict ledger (rimflow/scene_verdicts.py).

Planted faults that must turn this red (seen 2026-11-25, readings in design/specs/2026-11-23-bridge-v2/live/stamp_again/plants.txt):
the reset digest compares the station only, not the mods (a_dirty_mod_state_changes_the_reset_digest_and_stops_the_repeat); copies
written without their cluster id (copies_side_by_side_are_one_cluster_that_keeps_its_distance); opportunities counted as launches
(launches_opportunities_and_exposures_are_counted_apart); the cross-talk test without the margin (cross_talk_between_two_copies_is_a_breach)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.join(os.path.dirname(HERE), "rimflow")
for p in (HERE, RIMFLOW):
    if p not in sys.path:
        sys.path.insert(0, p)

import scene_repeats as R  # noqa: E402
import scene_stations as ST  # noqa: E402
import scene_verdicts as V  # noqa: E402

MODS = [{"mod": "RimMandrake.FlowWorks", "digest": "q0:p0", "proven": True, "why": None},
        {"mod": "RimMandrake.Pits", "digest": None, "why": "no digest hook"}]
B = {"kind": "live", "stage": "6", "test_kind": "B", "budget": 20,
     "tag_evidence": {"spoils": "the rescuer's own choice of patient", "tried": "one patient only; calm profile",
                      "why_not_enough": "the choice is the mod's decision and stays random by design"}}
MARK = {"overlay": "none", "tainted": False, "arm": "reference", "build_kind": "RELEASE", "map_kind": "settlement"}


def refused(name, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except R.Refused as e:
        assert e.name == name, "refused %s, not %s: %s" % (e.name, name, e)
        return e
    raise AssertionError("not refused (%s wanted)" % name)


def block(rect, things=(("pawn", 1, 1, {"kind": "Colonist", "spawned": "True"}), ("thing", 3, 2, {"def": "Bed"})), left=(), rows=None):
    """A readBack block as JawaBenchStageReadBack.Reply gives it, for things placed relative to the station's corner."""
    ox, oz = rect[0], rect[1]
    made = [{"op": op, "id": "Thing_%d" % (ox * 1000 + i), "x": ox + dx, "z": oz + dz, "got": dict(got, cell="(%d, 0, %d)" % (ox + dx, oz + dz))}
            for i, (op, dx, dz, got) in enumerate(things)]
    lf = [{"def": d, "id": "Thing_9", "x": ox + dx, "z": oz + dz, "why": "corpse", "blocking": True} for d, dx, dz in left]
    return {"tool": "jawa/spawn_pawn", "ok": True, "made": made, "rows": len(made) if rows is None else rows, "rowsWrong": 0,
            "left": lf, "leftBlocking": len(lf), "leftKept": 0, "digest": "companion-%d" % ox}


def series(**kw):
    return R.Series("sc_rescue", claim="claim1", build="b1", plan="plan1", **kw)


def each_stamp_is_a_fresh_launch_of_one_plan():
    s = series()
    mods = R.mod_digests(MODS)
    assert mods == {"RimMandrake.FlowWorks": "q0:p0", "RimMandrake.Pits": R.NO_HOOK}, mods
    rect = (10, 10, 9, 9)
    a = s.stamp(R.station_digest([block(rect)], rect), mods, rect)
    b = s.stamp(R.station_digest([block(rect)], rect), mods, rect)
    r = s.stamp(R.station_digest([block(rect)], rect), mods, rect, replay_of="x.1")
    for l, out in ((a, "o"), (b, "o"), (r, "o")):
        s.ended(l, outcome="SUCCESS", opportunity=True, exposures=1, receipt="rc%d" % l["launch"])
    assert (a["how"], b["how"], r["how"]) == (R.STAMP, R.STAMP, R.REPLAY), (a["how"], r["how"])
    assert a["plan"] == b["plan"] == "plan1" and a["launch"] != b["launch"]
    assert r["sample"] is False and a["sample"] and b["sample"], "a replay is never a sample"
    lines = s.ledger_lines({n: MARK for n in (1, 2, 3)})
    assert len({l["run"] for l in lines}) == 3 and all(l["plan"] == "plan1" for l in lines), lines
    assert s.counts()["samples"] == 2 and s.counts()["launches"] == 3, s.counts()


def copies_side_by_side_are_one_cluster_that_keeps_its_distance():
    s = series(distance=5)
    stage = ST.Stage("t", "settlement", (80, 80))
    c = s.cluster()
    mods = R.mod_digests(MODS)
    got = []
    for i in range(6):
        st = stage.give(scene="sc_rescue", **s.station_request((9, 9)))
        rect = st["rect"]
        got.append(rect)
        l = s.stamp(R.station_digest([block(rect)], rect), mods, rect, cluster=c)   # equal digests: relative to the corner
        s.ended(l, outcome="SUCCESS" if i else "RANDOM MISS", opportunity=True, exposures=1, receipt="rc%d" % i)
    for i, a in enumerate(got):
        for b in got[i + 1:]:
            gap = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            assert gap >= 5, "copies %s and %s stand %d cells apart, not 5" % (a, b, gap)
    lines = s.ledger_lines({n: MARK for n in range(1, 7)})
    assert all(l.get("cluster") == c for l in lines), "every copy carries its cluster id"
    sm = V.summary(B, [dict(l, rec="run") for l in lines], "sc_rescue")
    assert sm["counted"] == 1, "six copies of one cluster are one sample for the verdict ledger, not %s" % sm["counted"]
    assert s.counts()["samples"] == 1 and s.counts()["launches"] == 6, s.counts()


def a_map_wide_scene_is_refused_copies():
    s = series(map_wide=True)
    e = refused("MAP_WIDE_NO_COPIES", s.cluster)
    assert "one at a time" in e.why, e.why
    rect = (5, 5, 9, 9)
    s.stamp(R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)    # one at a time is served
    refused("UNKNOWN_CLUSTER", s.stamp, ("d", None), {}, rect, cluster="nope")


def a_dirty_mod_state_changes_the_reset_digest_and_stops_the_repeat():
    s = series()
    rect = (10, 10, 9, 9)
    s.stamp(R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)
    dirty = [dict(MODS[0], digest="q3:p1"), MODS[1]]              # a cache left full on purpose by the last run
    try:
        s.stamp(R.station_digest([block(rect)], rect), R.mod_digests(dirty), rect)
    except R.Stop as e:
        assert e.name == "RESET_DIGEST_DIFFERS", e.name
        assert ("mod RimMandrake.FlowWorks", "q0:p0", "q3:p1") in e.diffs, e.diffs
    else:
        raise AssertionError("a dirty mod digest did not stop the repeat")
    refused("STOPPED", s.stamp, R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)
    assert s.counts() == dict(s.counts(), launches=2, samples=0, stopped=True), s.counts()
    # a thing that the clean left on the station changes the station digest the same way
    t = series()
    t.stamp(R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)
    e = refused("RESET_DIGEST_DIFFERS", t.stamp, R.station_digest([block(rect, left=(("Corpse_Human", 2, 2),))], rect), R.mod_digests(MODS), rect)
    assert e.diffs[0][0] == "station", e.diffs


def an_unverifiable_reset_is_never_equal():
    rect = (10, 10, 9, 9)
    for bad in ({"mod": "RimMandrake.FlowWorks", "digest": "q0:p0", "proven": False, "why": None},
                {"mod": "RimMandrake.FlowWorks", "digest": None, "proven": True, "why": "the hook threw NullReferenceException: x"}):
        s = series()
        s.stamp(R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)
        e = refused("RESET_UNVERIFIED", s.stamp, R.station_digest([block(rect)], rect), R.mod_digests([bad, MODS[1]]), rect)
        assert e.diffs == [("mod RimMandrake.FlowWorks", "q0:p0", None)], e.diffs
    # a block that made more rows than it lists cannot be digested: the station is unread, never equal
    dig, why = R.station_digest([block(rect, rows=60)], rect)
    assert dig is None and "60" in why, (dig, why)
    s = series()
    refused("RESET_UNVERIFIED", s.stamp, (dig, why), R.mod_digests(MODS), rect)
    # a mod with no digest hook is listed on every launch and stops nothing
    s = series()
    for _ in range(3):
        l = s.stamp(R.station_digest([block(rect)], rect), R.mod_digests(MODS), rect)
    assert l["start"]["mods"]["RimMandrake.Pits"] == R.NO_HOOK


def a_fresh_process_comparison_falls_due_and_a_difference_joins_the_not_reset_list():
    s = series(fresh_every_count=3)
    rect = (10, 10, 9, 9)
    st, mods = R.station_digest([block(rect)], rect), R.mod_digests(MODS)
    for _ in range(3):
        assert not s.fresh_due()
        s.stamp(st, mods, rect)
    assert s.fresh_due(), "three launches since the last comparison: a fresh process is due"
    assert s.fresh(st, mods, "ArchSmall, process started 01:10") == [] and not s.fresh_due() and not s.stopped
    for _ in range(4):
        l = s.stamp(st, mods, rect)
    assert l["fresh_overdue"] is True and l["launch"] == 7, "launch 7 ran past its due comparison and says so"
    added = s.fresh(st, R.mod_digests([dict(MODS[0], digest="q0:p0:sub0"), MODS[1]]), "ArchSmall, process started 02:00")
    assert len(added) == 1 and "RimMandrake.FlowWorks" in added[0] and "q0:p0:sub0" in added[0], added
    assert s.not_reset == added and s.stopped["name"] == "STAMP_NOT_FRESH", s.stopped
    refused("STOPPED", s.stamp, st, mods, rect)


def launches_opportunities_and_exposures_are_counted_apart():
    s = series()
    rect = (10, 10, 9, 9)
    st, mods = R.station_digest([block(rect)], rect), R.mod_digests(MODS)
    plays = [("SUCCESS", True, 4), ("RANDOM MISS", True, 1), ("ENVIRONMENT FAULT", False, 0), ("SUCCESS", True, 2)]
    for outcome, opp, exp in plays:
        s.ended(s.stamp(st, mods, rect), outcome=outcome, opportunity=opp, exposures=exp, receipt="r")
    s.stamp(st, mods, rect)                                         # launched, never ended (the run died)
    c = s.counts()
    assert (c["launches"], c["opportunities"], c["exposures"]) == (5, 3, 7), c
    lines = s.ledger_lines({n: MARK for n in range(1, 6)})
    assert [l["opportunity"] for l in lines] == [True, True, False, True] and [l["exposures"] for l in lines] == [4, 1, 0, 2], lines
    refused("BAD_ARGS", s.ended, s.launches[-1], outcome="SUCCESS", opportunity=True, exposures=-1)


def cross_talk_between_two_copies_is_a_breach():
    s = series(distance=4)
    c = s.cluster()
    a_rect, b_rect = (10, 10, 9, 9), (23, 10, 9, 9)
    mods = R.mod_digests(MODS)
    a = s.stamp(R.station_digest([block(a_rect)], a_rect), mods, a_rect, cluster=c)
    b = s.stamp(R.station_digest([block(b_rect)], b_rect), mods, b_rect, cluster=c)
    s.ended(a, outcome="SUCCESS", opportunity=True, exposures=1, receipt="ra", cells={"rescuer": [(12, 12), (21, 12)]})
    s.ended(b, outcome="SUCCESS", opportunity=True, exposures=1, receipt="rb", cells={"rescuer": [(25, 12)]})
    out = s.crosstalk(c)
    assert len(out) == 1 and "launch 1" in out[0] and "launch 2" in out[0], "(21, 12) is in launch 2's margin of 2: %s" % out
    lines = s.ledger_lines({1: MARK, 2: MARK})
    assert all(l["outcome"] == "UNRESOLVED" and "cross-talk" in l["spoiled_by"] for l in lines), lines
    t = series(distance=4)
    c = t.cluster()
    a = t.stamp(R.station_digest([block(a_rect)], a_rect), mods, a_rect, cluster=c)
    t.ended(a, outcome="SUCCESS", opportunity=True, receipt="ra", cells={"rescuer": [(12, 12), (20, 12)]})
    b = t.stamp(R.station_digest([block(b_rect)], b_rect), mods, b_rect, cluster=c)
    t.ended(b, outcome="SUCCESS", opportunity=True, receipt="rb", cells={"rescuer": [(25, 12)]})
    assert t.crosstalk(c) == [], "a rescuer that stays outside the other copy's margin is no breach"


CHECKS = [each_stamp_is_a_fresh_launch_of_one_plan, copies_side_by_side_are_one_cluster_that_keeps_its_distance,
          a_map_wide_scene_is_refused_copies, a_dirty_mod_state_changes_the_reset_digest_and_stops_the_repeat,
          an_unverifiable_reset_is_never_equal, a_fresh_process_comparison_falls_due_and_a_difference_joins_the_not_reset_list,
          launches_opportunities_and_exposures_are_counted_apart, cross_talk_between_two_copies_is_a_breach]


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
    print("selftest_scene_repeats: %d checks passed" % passed)
    return int(passed != len(CHECKS))


if __name__ == "__main__":
    raise SystemExit(main())
