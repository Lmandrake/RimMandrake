#!/usr/bin/env python3
"""Offline: wind_burn_live.verdict_rows never passes row C on a line that did not light under the black rain.

The first live run (2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN) read C as [0]*8 from the first
sample and passed it without knowing the line had lit. Each case below is (C reading, expected row C verdict).
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.modules.setdefault("rimbridge_client", types.SimpleNamespace(RimBridge=None, resolve_endpoint=None))
sys.path.insert(0, HERE)
import wind_burn_live as W  # noqa: E402

A = {"lit": 9, "peak_fires": 18, "east_cells": 10, "fires_in_outer_lanes": 0}
B = {"lit": 9, "peak_fires": 63, "east_cells": 10, "fires_in_outer_lanes": 31}
CASES = [
    ("lit, burning at 0, out by the end", {"lit": 9, "fires_at_0_then_every_250": [9, 6, 2, 0, 0, 0, 0, 0, 0]}, True),
    ("never lit (the old false pass)", {"lit": 0, "fires_at_0_then_every_250": [0] * 9}, False),
    ("reported lit but no fire at tick 0", {"lit": 9, "fires_at_0_then_every_250": [0] * 9}, False),
    ("lit and still burning at the end", {"lit": 9, "fires_at_0_then_every_250": [9, 9, 8, 8, 7, 7, 6, 5, 3]}, False),
    ("lit, out, then relit by the end", {"lit": 9, "fires_at_0_then_every_250": [9, 3, 0, 0, 0, 0, 0, 1, 2]}, False),
]
bad = 0
for name, c, want in CASES:
    rows = W.verdict_rows(A, B, c)
    got = rows[4][1]
    ok = bool(got) == want
    bad += not ok
    print("%-4s C %-38s -> %s (want %s)" % ("ok" if ok else "FAIL", name, bool(got), want))
rows = W.verdict_rows(A, B, CASES[0][1])
ok = len(rows) == 5 and all(r[1] for r in rows)
bad += not ok
print("%-4s the first live run's A and B with a lit C give 5 ok rows" % ("ok" if ok else "FAIL"))
print("%d of %d ok" % (len(CASES) + 1 - bad, len(CASES) + 1))
sys.exit(1 if bad else 0)
