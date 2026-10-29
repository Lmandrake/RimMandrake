#!/usr/bin/env python3
"""Selftest: BENCH owns all FlowWorks (owner, 2026-10-23). The lane is data
(infrastructure/state/flowworks_lane.json): `acceptance` routes a FlowWorks item to BENCH at every
level and never to FOUNDRY; the shipped pattern file matches the names it must (FlowWorks and GSS, both BENCH's) and not other biomes' work.

    python3 src/RimMandrake/rimflow/selftest_flowworks_lane.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from rimflow import model, priority                                   # noqa: E402
import selftest_built as sb                                           # noqa: E402

PASS, FAIL = [], []
FW = "HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE"
OTHER = "STILLSAND_DUNE_GALE_LIVE_1"


def t_flowworks_acceptance_is_bench_at_every_level():
    evs = (sb.filed("FOUNDRY", FW, 0) + [sb.impl(2, sb.crit(("A1", "L1"), ("A2", "GREEN-FULL")), "FOUNDRY", FW)]
           + sb.filed("FOUNDRY", OTHER, 4) + [sb.impl(6, sb.crit(("A1", "L1")), "FOUNDRY", OTHER)])
    w = model.replay(evs)
    f = {i.id for _, its in priority.acceptance(w, "FOUNDRY") for i in its}
    b = {i.id for _, its in priority.acceptance(w, "BENCH") for i in its}
    # The lane's seat is data (FOUNDRY since the v3 cutover; BENCH again after `v3_cutover.py revert`).
    seat, _ = priority.flowworks_lane()
    want = ({OTHER, FW}, set()) if seat == "FOUNDRY" else ({OTHER}, {FW})
    assert (f, b) == want, (seat, f, b)


def t_shipped_lane_file_matches_flowworks_and_gss_not_others():
    lane = priority.flowworks_lane()
    # The v3 cutover (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY) moves the lane BENCH -> FOUNDRY; its
    # record says which side of it this tree is on, so the test is true both before and after.
    rec = os.path.join(model.ROOT, "infrastructure", "state", "v3_cutover", "record.json")
    want = "FOUNDRY" if os.path.exists(rec) and json.load(open(rec)).get("state") == "applied" else "BENCH"
    assert lane[0] == want and lane[1], (lane, want)
    for n in (FW, "FLOWWORKS_NORTHSTAR_SHIP_1", "PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES",
              "DRAWBRIDGE_CABLES_FIX_STOP_SHORT", "SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING", "POND_PUMP_FIX_LAST_DROP_COUNTS",
              "GSS_CORD_SILENCE_PHANTOM_SPARK", "CORD_GRAPH_TOPOLOGY_REVISION_1", "ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY"):
        assert priority.flowworks_seat(n, lane) == want, n
    for n in (OTHER, "GRAFFITI_V1_LIVE_PROOF_1", "SUMP_MECHANICS_1"):
        assert priority.flowworks_seat(n, lane) is None, n


def t_a_missing_lane_file_degrades_to_no_routing():
    assert priority.flowworks_lane("/nonexistent/flowworks_lane.json")[1] == []


def t_a_bad_lane_file_raises_naming_the_file():
    import tempfile
    for body in ("{not json", "[1, 2]", '{"id_patterns": ["(unclosed"]}', '{"id_patterns": "x"}', '{"id_patterns": [3]}'):
        with tempfile.NamedTemporaryFile("w", suffix="_lane.json", delete=False) as fh:
            fh.write(body)
        try:
            priority.flowworks_lane(fh.name)
        except priority.LaneFileError as e:
            assert fh.name in str(e), (body, str(e))
        else:
            raise AssertionError("no error for " + body)
        finally:
            os.unlink(fh.name)


def t_an_unreadable_lane_file_raises_not_silently_unrouted():
    import tempfile
    with tempfile.TemporaryDirectory() as td:   # a directory where the file should be: exists, cannot be read
        try:
            priority.flowworks_lane(td)
        except priority.LaneFileError as e:
            assert td in str(e), str(e)
        else:
            raise AssertionError("an unreadable lane path silently degraded to no routing")


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except AssertionError as e:
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s" % (fn.__name__, e))
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
