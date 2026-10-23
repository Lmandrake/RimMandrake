#!/usr/bin/env python3
"""Selftest: BENCH owns all FlowWorks (owner, 2026-10-23). The lane is data
(infrastructure/state/flowworks_lane.json): `acceptance` routes a FlowWorks item to BENCH at every
level and never to FOUNDRY; the shipped pattern file matches the names it must (FlowWorks and GSS, both BENCH's) and not other biomes' work.

    python3 src/RimMandrake/rimflow/selftest_flowworks_lane.py
"""
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
    assert f == {OTHER} and b == {FW}, (f, b)


def t_shipped_lane_file_matches_flowworks_and_gss_not_others():
    lane = priority.flowworks_lane()
    assert lane[0] == "BENCH" and lane[1], lane
    for n in (FW, "FLOWWORKS_NORTHSTAR_SHIP_1", "PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH", "CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES",
              "DRAWBRIDGE_CABLES_FIX_STOP_SHORT", "SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING", "POND_PUMP_FIX_LAST_DROP_COUNTS",
              "GSS_CORD_SILENCE_PHANTOM_SPARK", "CORD_GRAPH_TOPOLOGY_REVISION_1", "ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY"):
        assert priority.flowworks_seat(n, lane) == "BENCH", n
    for n in (OTHER, "GRAFFITI_V1_LIVE_PROOF_1", "SUMP_MECHANICS_1"):
        assert priority.flowworks_seat(n, lane) is None, n


def t_a_missing_lane_file_degrades_to_no_routing():
    assert priority.flowworks_lane("/nonexistent/flowworks_lane.json")[1] == []


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except AssertionError as e:
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s" % (fn.__name__, e))
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
