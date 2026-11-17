#!/usr/bin/env python3
"""Offline: wind_burn_live.verdict_rows tells a fire that follows the wind from every build that only looks like one.

Four parts, each row printing its worst value, its limit and how many cases it read:
  1. Planted readings. Each wrong game the scene must refuse, as the reading it would give: the wind never set or read back
     wrong, a strip already burning, a fire that walks east whatever the wind, one that runs both ways along the axis, a
     control with an east lean, even spread with the wind on, an unmoved fire; and row C on a line that never lit under the
     black rain (the first live run, 2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN, read C as [0]*8
     and passed it).
  2. The scene's own layout (a 61 x 21 strip of full grass, ringed bare, a 9-cell line lit mid-strip, wind 90 then 270, then
     the wind off) driven through pyre_burn_sim.py's model of the shipped carry, whose wind step is RM_BurnKernel.WindProbes
     (the checksum row below; the C# fuzz asserts its side). Every seed must pass every row.
  3. Planted model faults on the same layout: a carry that walks east whatever the wind, one that lights downwind and
     upwind (spread along one axis), and vanilla's even spread with the wind on. Each must be refused on every seed.
  4. The bar's wider range, beyond the live layout: every 15 degrees of bearing x grass cover 1.0/0.97/0.80/0.70 x 3 seeds on a
     69 x 69 field, read the same way along the wind's own axis.
The range this covers (RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED, 2026-11-17): what the game can vary for
fire_walks_with_wind is the bearing (any, held per map), the grass under the line (full to patchy), the wind switch, the
seed and the time burned (10,000 ticks, as the scene). Left out: weather (locked clear here; black rain is row C, a free sky
is T_BURN_ECOLOGY), buildings and roofs near the line (the scene's strips hold none), the C# callers of the kernel
(RIMMANDRAKE_NOTE_PYRE_WIND_CALLERS_PROVE_ONLY_LIVE: the live scene decides), and maps not of the Pyrelands (not promised).
The start rows (wind and carries read back) are the game's own: the model holds the wind it is given, so parts 2-4 read
them as set.

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_wind_burn_rows.py
"""
import math
import os
import re
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.modules.setdefault("rimbridge_client", types.SimpleNamespace(RimBridge=None, resolve_endpoint=None))
sys.path.insert(0, HERE)
import pyre_burn_sim as M  # noqa: E402
import wind_burn_live as W  # noqa: E402

FUZZ = os.path.join(HERE, "Source", "SelfTest", "Fuzz", "PyrelandsFuzz.cs")
KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_BurnKernel.cs")
bad = 0
total = 0


def check(ok, text):
    global bad, total
    total += 1
    bad += not ok
    print("%-4s %s" % ("ok" if ok else "FAIL", text))


def run_reading(asked, wind_on, down, up, outer, lit=9, peak=18, before=0, wind_set=None, probe_wind=None, probe_carries=None):
    return {"asked": asked, "wind_set": asked if wind_set is None else wind_set,
            "probe": "wind=%.1f;carries=%s;carried=0;fires=0" % (asked if probe_wind is None else probe_wind,
                                                                 wind_on if probe_carries is None else probe_carries),
            "carries_wanted": wind_on, "fires_before": before, "lit": lit, "peak_fires": peak,
            "down_cells": down, "up_cells": up, "fires_in_outer_lanes": outer}


GOOD_F = run_reading(90, True, 10, 0, 0)
GOOD_R = run_reading(270, True, 10, 0, 0)
GOOD_B = run_reading(90, False, 13, 13, 93, peak=173)
GOOD_C = {"fires_before": 0, "lit": 9, "fires_at_0_then_every_250": [9, 6, 2, 0, 0, 0, 0, 0, 0]}


def verdict(f=GOOD_F, r=GOOD_R, b=GOOD_B, c=GOOD_C):
    return W.verdict_rows(f, r, b, c)


NAMES = [n for n, _, _ in verdict()]


def idx(word):
    return next(i for i, n in enumerate(NAMES) if n.startswith(word))


# ---- 1. planted readings --------------------------------------------------------------------------------------------
print("-- 1. planted readings: each wrong game, the row that must refuse it")
rows = verdict()
check(len(rows) == 9 and all(ok for _, ok, _ in rows), "the shipped reading passes all %d rows" % len(rows))
START, CLEAN, F_ROW, R_ROW, PEAK, OUTER, B_OUT, B_LEAN, C_ROW = (idx("start the wind"), idx("start every"), idx("F wind"),
                                                                  idx("R wind"), idx("F,R never"), idx("F,R nothing"),
                                                                  idx("B CONTROL even"), idx("B CONTROL runs"), idx("C "))
PLANTED = [
    ("the wind never set: ProbeWind reads the map's own 213", dict(f=run_reading(90, True, 10, 0, 0, probe_wind=213)), START),
    ("SetWindForTest found no component (-1)", dict(r=run_reading(270, True, 10, 0, 0, wind_set=-1)), START),
    ("carries=False with the wind switch on", dict(f=run_reading(90, True, 10, 0, 0, probe_carries=False)), START),
    ("carries=True with the wind switch off", dict(b=run_reading(90, False, 13, 13, 93, probe_carries=True)), START),
    ("a probe that answers nothing", dict(f=dict(GOOD_F, probe=None)), START),
    ("a strip already burning before it is lit", dict(r=run_reading(270, True, 10, 0, 0, before=4)), CLEAN),
    ("an unmoved fire (down 0, up 0)", dict(f=run_reading(90, True, 0, 0, 0)), F_ROW),
    ("fire runs both ways along the axis (down 8, up 8)", dict(f=run_reading(90, True, 8, 8, 0)), F_ROW),
    ("fire walks east whatever the wind (R down 0, up 10)", dict(r=run_reading(270, True, 0, 10, 0)), R_ROW),
    ("a fire that makes two (peak 30 of 9 lit)", dict(f=run_reading(90, True, 10, 0, 0, peak=30)), PEAK),
    ("even spread with the wind on (outer lanes 31)", dict(f=run_reading(90, True, 13, 13, 31)), OUTER),
    ("a control that never spreads (outer lanes 0)", dict(b=run_reading(90, False, 3, 3, 0)), B_OUT),
    ("a control leaning east like the wind (down 20, up 2)", dict(b=run_reading(90, False, 20, 2, 60)), B_LEAN),
    ("a control that only goes one way (up 0)", dict(b=run_reading(90, False, 12, 0, 60)), B_LEAN),
    ("C never lit under the rain (the old false pass)", dict(c={"fires_before": 0, "lit": 0, "fires_at_0_then_every_250": [0] * 9}), C_ROW),
    ("C reported lit, no fire at tick 0", dict(c={"fires_before": 0, "lit": 9, "fires_at_0_then_every_250": [0] * 9}), C_ROW),
    ("C still burning at the end", dict(c={"fires_before": 0, "lit": 9, "fires_at_0_then_every_250": [9, 9, 8, 8, 7, 7, 6, 5, 3]}), C_ROW),
    ("C out, then relit by the end", dict(c={"fires_before": 0, "lit": 9, "fires_at_0_then_every_250": [9, 3, 0, 0, 0, 0, 0, 1, 2]}), C_ROW),
    ("C strip burning before the rain line", dict(c=dict(GOOD_C, fires_before=3)), CLEAN),
]
for name, kw, want in PLANTED:
    rows = verdict(**kw)
    check(not rows[want][1], "%-52s refused by '%s' (%s)" % (name, NAMES[want], rows[want][2]))


# ---- 2-4. the model ---------------------------------------------------------------------------------------------------
def probe_checksum(reach):
    h = 0
    for b10 in range(0, 3600, 25):
        for r8 in range(8):
            for r2 in (0.25, 0.75):
                for dx, dz in M.wind_probes(b10 / 10.0, r8 / 8.0, r2, reach):
                    h = (h * 31 + (dx + 5) * 11 + (dz + 5)) % 1000000007
    return h


def kconst(name):
    return int(re.search(r"const int %s = (\d+);" % name, open(KERNEL, encoding="utf-8").read()).group(1))


CARRY = dict(carry_ticks=kconst("WindCarryTicks"), carry_reach=kconst("WindCarryReach"))
want = re.search(r"WindProbeChecksum = (\d+)L;", open(FUZZ, encoding="utf-8").read())
got = probe_checksum(CARRY["carry_reach"])
check(bool(want) and int(want.group(1)) == got,
      "the model's wind step is RM_BurnKernel.WindProbes: checksum %d == %s (2,304 bearing x roll cases)"
      % (got, want.group(1) if want else "?"))


def model_run(bearing, wind_on, cover=1.0, seed=0, H=W.STRIP_H + 8, Wd=W.STRIP_W + 8, splits=1, mode="carry"):
    """The scene in the model: grass inside a 4-cell bare ring, a 9-cell line across the wind through the middle, 10,000
    ticks, the fires read every 500 ticks as the live script reads them. -> a reading in wind_burn_live's shape."""
    rng = np.random.default_rng(1000 + seed)
    plant = np.zeros((H, Wd), np.int8)
    plant[4:H - 4, 4:Wd - 4] = np.where(rng.random((H - 8, Wd - 8)) < cover, 1, 0)
    carried = wind_on and mode != "even"
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, wind=bearing if carried else None, carried=carried, carry_splits=splits, **CARRY)
    cx, cz = 4 + W.LINE, H // 2
    before = int((s.size > 0).sum())
    lit = s.light_line(cx, cz, 9, 0.35, angle=bearing + 90)
    r = math.radians(bearing)
    wx, wz = math.sin(r), math.cos(r)
    down = up = outer = 0
    peak, nxt = lit, 500
    while s.tick < 10000:
        s.beat()
        if s.tick >= nxt:
            nxt += 500
            zs, xs = np.nonzero(s.size > 0)
            peak = max(peak, len(xs))
            if len(xs):
                al = (xs - cx) * wx + (zs - cz) * wz
                ac = (xs - cx) * wz - (zs - cz) * wx
                down = max(down, int(round(al.max())))
                up = max(up, int(round((-al).max())))
                outer = max(outer, int((np.abs(ac) >= 7.5).sum()))      # the outer three lanes each side of a 21-wide strip
    return run_reading(bearing, wind_on, down, up, outer, lit=lit, peak=peak, before=before)


SEEDS = range(40)
print("-- 2. the scene's layout through the shipped carry: wind 90, wind 270, wind off; %d seeds" % len(SEEDS))
fails, worst = 0, dict(lean=1e9, outer=0, peak=0.0, b_outer=1e9, b_margin=1e9)
for sd in SEEDS:
    f, r, b = model_run(90, True, seed=sd), model_run(270, True, seed=sd), model_run(90, False, seed=sd)
    rows = verdict(f, r, b)
    fails += not all(ok for _, ok, _ in rows)
    lean = min(f["down_cells"] - f["up_cells"], r["down_cells"] - r["up_cells"])
    worst["lean"] = min(worst["lean"], lean)
    worst["outer"] = max(worst["outer"], f["fires_in_outer_lanes"], r["fires_in_outer_lanes"])
    worst["peak"] = max(worst["peak"], f["peak_fires"] / f["lit"], r["peak_fires"] / r["lit"])
    worst["b_outer"] = min(worst["b_outer"], b["fires_in_outer_lanes"])
    worst["b_margin"] = min(worst["b_margin"], lean - abs(b["down_cells"] - b["up_cells"]))
check(fails == 0, "every seed passes all 9 rows: %d of %d seeds fail" % (fails, len(SEEDS)))
print("     worst: wind lean (down - up) %d cells, must > 0 | outer-lane fires with the wind %d, must 0 | peak %.1f x lit, "
      "must <= 3 | control outer lanes %d, must > 0 | control lean below the wind's by %d, must > 0"
      % (worst["lean"], worst["outer"], worst["peak"], worst["b_outer"], worst["b_margin"]))

print("-- 3. planted model faults on the same layout: each refused on every seed")
orig = M.wind_probes
FAULTS = [
    ("the carry walks east whatever the wind", lambda b, r1, r2, reach: orig(90.0, r1, r2, reach), 1, "carry"),
    ("the carry lights downwind and upwind (one axis)",
     lambda b, r1, r2, reach: [c for p in orig(b, r1, r2, reach) for c in (p, (-p[0], -p[1]))], 2, "carry"),
    ("vanilla's even spread with the wind on", orig, 1, "even"),
]
for name, probes, splits, mode in FAULTS:
    M.wind_probes = probes
    try:
        caught = 0
        for sd in SEEDS:
            f = model_run(90, True, seed=sd, splits=splits, mode=mode)
            r = model_run(270, True, seed=sd, splits=splits, mode=mode)
            b = model_run(90, False, seed=sd)
            rows = verdict(f, r, b)
            caught += not all(ok for _, ok, _ in rows)
    finally:
        M.wind_probes = orig
    check(caught == len(SEEDS), "%-48s refused on %d of %d seeds" % (name, caught, len(SEEDS)))

print("-- 4. the wider range: every 15 degrees x cover 1.0/0.97/0.80/0.70 x 3 seeds, 69 x 69 field")
n, min_lean, max_up, on_outer, off_outer, worst_case = 0, 1e9, 0, 0, 1e9, ""
for cover in (1.0, 0.97, 0.80, 0.70):
    for bearing in range(0, 360, 15):
        for sd in range(3):
            on = model_run(bearing, True, cover, sd, H=69, Wd=69)
            n += 1
            if on["down_cells"] - on["up_cells"] < min_lean:
                min_lean, worst_case = on["down_cells"] - on["up_cells"], "cover %.2f bearing %d seed %d" % (cover, bearing, sd)
            max_up = max(max_up, on["up_cells"])
            on_outer = max(on_outer, on["fires_in_outer_lanes"])
    for sd in range(3):
        off_outer = min(off_outer, model_run(90, False, cover, sd, H=69, Wd=69)["fires_in_outer_lanes"])
check(min_lean > 0, "the burn runs further downwind than upwind at every bearing: worst lean %d cells (%s), upwind reach at "
      "most %d; must > 0 | %d cases" % (min_lean, worst_case, max_up, n))
check(on_outer < off_outer, "the widest sideways burn with the wind (%d fires in the outer lanes) stays below the narrowest "
      "with it off (%d) | %d wind cases, 12 off" % (on_outer, off_outer, n))

print("%d of %d ok" % (total - bad, total))
sys.exit(1 if bad else 0)
