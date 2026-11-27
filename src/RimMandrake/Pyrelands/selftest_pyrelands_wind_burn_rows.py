#!/usr/bin/env python3
"""Offline: wind_burn_live.verdict_rows tells a fire that follows the wind from every build that only looks like one.

Five parts, each row printing its worst value, its limit and how many cases it read:
  1. Planted readings. Each wrong game the scene must refuse, as the reading it would give: the wind never set or read back
     wrong, the Fire pace not the shipped default (the old pin left in) or unread, a strip already burning, a fire that walks
     east whatever the wind, one that runs both ways along the axis, a fire that makes two (one past the peak limit), a
     control with an east lean, even spread with the wind on, an unmoved fire; and row C on a line that never lit under the
     black rain (the first live run, 2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN, read C as [0]*8
     and passed it). A peak exactly at the limit must pass.
  2. The numbers the rows rest on, read from their sources: the Fire pace and carry interval from RM_BurnKernel.cs, ember
     grass's hit points and flammability from its def (FIRE_LIFE_MAX's derivation), and wind_burn_live.carry_ticks equal to
     the model's paced carry at every pace 90..260.
  3. The scene's own layout (a 61 x 21 strip of full grass, ringed bare, a 9-cell line lit mid-strip, wind 90 then 270, then
     the wind off, over window_ticks(pace) in 20 samples) driven through pyre_burn_sim.py's model of the shipped carry, whose
     wind step is RM_BurnKernel.WindProbes (the checksum row below; the C# fuzz asserts its side): 40 seeds at the shipped
     Fire pace (the scene's, the deciding reading), 40 at 0.1.0's pace 100 (the second reading the ruling allows), and every
     5 percent of the slider 100..250 on 8 seeds. Every case must pass every row; the fires' longest life must stay within
     FIRE_LIFE_MAX and no lane may hold more fires at once than rows_deep (the two facts the peak limit is built on).
  4. Planted model faults on the same layout at the shipped pace: a carry that walks east whatever the wind (fire that
     ignores the wind), one that lights downwind and upwind (spread along one axis), and vanilla's even spread with the wind
     on (the flood). Each must be refused on every seed.
  5. The bar's wider range, beyond the live layout, at the shipped Fire pace (pyre_burn_sim.DEFAULTS) over that pace's
     window: every 15 degrees of bearing x grass cover 1.0/0.97/0.80/0.70 x 3 seeds on a 69 x 69 field, read the same way
     along the wind's own axis.
The range this covers (RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED, 2026-11-17; the pace and the window,
Conductor ruling 2026-11-27 4:36 AM PST): what the game can vary for fire_walks_with_wind is the bearing (any, held per map),
the grass under the line (full to patchy), the wind switch, the Fire pace (the slider, 100..250, whole percents), the seed
and the time burned (read over the window in which the line walks 0.1.0's 10,000 ticks' worth). Left out: weather (locked
clear here; black rain is row C, a free sky is T_BURN_ECOLOGY), buildings and roofs near the line (the scene's strips hold
none), the C# callers of the kernel (RIMMANDRAKE_NOTE_PYRE_WIND_CALLERS_PROVE_ONLY_LIVE: the live scene decides), and maps
not of the Pyrelands (not promised). The start rows (wind, carries and pace read back) are the game's own: the model holds
what it is given, so parts 3-5 read them as set.

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


def run_reading(asked, wind_on, down, up, outer, lit=9, peak=18, before=0, wind_set=None, probe_wind=None, probe_carries=None,
                pace=W.PACE_DEFAULT, window=None, lane_depth="line"):
    return {"asked": asked, "wind_set": asked if wind_set is None else wind_set,
            "pace": pace, "window_ticks": W.run_window(W.PACE_DEFAULT, wind_on) if window is None else window,
            "probe": "wind=%.1f;carries=%s;carried=0;fires=0" % (asked if probe_wind is None else probe_wind,
                                                                 wind_on if probe_carries is None else probe_carries),
            "carries_wanted": wind_on, "fires_before": before, "lit": lit, "peak_fires": peak,
            "down_cells": down, "up_cells": up, "fires_in_outer_lanes": outer,
            # a wind run's deepest lane: a line rows_deep deep at its pace unless planted; the control does not read it
            "lane_depth": (W.rows_deep(pace) if pace is not None else 1) if lane_depth == "line" and wind_on
            else (None if lane_depth == "line" else lane_depth)}


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
check(len(rows) == 11 and all(ok for _, ok, _ in rows), "the shipped reading passes all %d rows" % len(rows))
START, PACE, CLEAN, F_ROW, R_ROW, PEAK, LANE, OUTER, B_OUT, B_LEAN, C_ROW = (
    idx("start the wind"), idx("start the Fire pace"), idx("start every"), idx("F wind"), idx("R wind"),
    idx("F,R at each of the %d samples no more" % W.SAMPLES), idx("F,R at each of the %d samples no lane" % W.SAMPLES),
    idx("F,R at each of the %d samples no fire" % W.SAMPLES),
    idx("B CONTROL even"), idx("B CONTROL runs"), idx("C "))
# RIMMANDRAKE_SAMPLE_PYRE_NEVER_ROWS_BETWEEN_FIVE_HUNDRED_TICKS: both rows are read from 20 samples, so their names say that
# and never "never": a fire that comes and goes between two samples is not seen
check(all("each of the %d samples" % W.SAMPLES in NAMES[i] and "never" not in NAMES[i] for i in (PEAK, LANE, OUTER)),
      "the peak-fires, lane-depth and outer-lane rows name the sampling they rest on: %r, %r, %r"
      % (NAMES[PEAK], NAMES[LANE], NAMES[OUTER]))
LIM = W.peak_limit(W.PACE_DEFAULT)
check(verdict(f=run_reading(90, True, 10, 0, 0, peak=LIM), r=run_reading(270, True, 10, 0, 0, peak=LIM))[PEAK][1],
      "a peak exactly at the limit (%d at pace %d) passes the peak row" % (LIM, W.PACE_DEFAULT))
DEEP = W.rows_deep(W.PACE_DEFAULT)
check(verdict(f=run_reading(90, True, 10, 0, 0, lane_depth=DEEP), r=run_reading(270, True, 10, 0, 0, lane_depth=DEEP))[LANE][1],
      "a lane exactly %d deep (rows_deep at pace %d) passes the lane row" % (DEEP, W.PACE_DEFAULT))
PLANTED = [
    ("the wind never set: ProbeWind reads the map's own 213", dict(f=run_reading(90, True, 10, 0, 0, probe_wind=213)), START),
    ("SetWindForTest found no component (-1)", dict(r=run_reading(270, True, 10, 0, 0, wind_set=-1)), START),
    ("carries=False with the wind switch on", dict(f=run_reading(90, True, 10, 0, 0, probe_carries=False)), START),
    ("carries=True with the wind switch off", dict(b=run_reading(90, False, 13, 13, 93, probe_carries=True)), START),
    ("a probe that answers nothing", dict(f=dict(GOOD_F, probe=None)), START),
    ("the pace pin left in (pace 100, its window 10,000)",
     dict(f=run_reading(90, True, 10, 0, 0, pace=W.PACE_MIN, window=W.window_ticks(W.PACE_MIN))), PACE),
    ("the shipped pace read over the old 10,000 ticks", dict(r=run_reading(270, True, 10, 0, 0, window=10000)), PACE),
    ("the Fire pace unread (None)", dict(b=run_reading(90, False, 13, 13, 93, peak=173, pace=None)), PACE),
    ("the Fire pace unread on a wind run: no peak limit", dict(f=run_reading(90, True, 10, 0, 0, pace=None)), PEAK),
    ("a strip already burning before it is lit", dict(r=run_reading(270, True, 10, 0, 0, before=4)), CLEAN),
    ("an unmoved fire (down 0, up 0)", dict(f=run_reading(90, True, 0, 0, 0)), F_ROW),
    ("fire runs both ways along the axis (down 8, up 8)", dict(f=run_reading(90, True, 8, 8, 0)), F_ROW),
    ("fire walks east whatever the wind (R down 0, up 10)", dict(r=run_reading(270, True, 0, 10, 0)), R_ROW),
    ("a fire that makes two (peak one past the limit, %d)" % (LIM + 1), dict(f=run_reading(90, True, 10, 0, 0, peak=LIM + 1)), PEAK),
    ("a wind run that never lit (lit 0)", dict(r=run_reading(270, True, 10, 0, 0, lit=0)), PEAK),
    ("a flood under the peak: lanes %d deep, peak %d of %d" % (DEEP + 1, LIM - 6, LIM),
     dict(f=run_reading(90, True, 10, 0, 0, peak=LIM - 6, lane_depth=DEEP + 1)), LANE),
    ("the flood's own reading: lanes 9 deep, peak 54 (model, pace 200)",
     dict(r=run_reading(270, True, 9, 3, 0, peak=54, lane_depth=9)), LANE),
    ("the lanes unread on a wind run (None)", dict(f=run_reading(90, True, 10, 0, 0, lane_depth=None)), LANE),
    ("the Fire pace unread on a wind run: no lane limit", dict(r=run_reading(270, True, 10, 0, 0, pace=None)), LANE),
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


# ---- 2-5. the numbers and the model ---------------------------------------------------------------------------------------------------
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


print("-- 2. the numbers the rows rest on, from their sources")
KP = dict((n, kconst(n)) for n in ("FirePacePercentMin", "FirePacePercentDefault", "FirePacePercentMax", "WindCarryTicks"))
check((W.PACE_MIN, W.PACE_DEFAULT, W.PACE_MAX, W.CARRY_TICKS_010) == (KP["FirePacePercentMin"], KP["FirePacePercentDefault"],
      KP["FirePacePercentMax"], KP["WindCarryTicks"]) and W.SET.get("firePacePercent") == str(KP["FirePacePercentDefault"]),
      "the scene burns at the shipped Fire pace: SET firePacePercent %s, RM_BurnKernel Min/Default/Max %d/%d/%d, carry %d ticks"
      % (W.SET.get("firePacePercent"), KP["FirePacePercentMin"], KP["FirePacePercentDefault"], KP["FirePacePercentMax"],
         KP["WindCarryTicks"]))
DEF = open(os.path.join(HERE, "Defs", "ThingDefs_Plants", "EmberGrass.xml"), encoding="utf-8").read()
hp = re.search(r"<MaxHitPoints>(\d+)</MaxHitPoints>", DEF)
fl = re.search(r"<Flammability>([\d.]+)</Flammability>", DEF)
check(bool(hp and fl) and int(hp.group(1)) == W.EMBER_GRASS_HP and float(fl.group(1)) == W.EMBER_GRASS_FLAMMABILITY
      and W.FIRE_LIFE_MAX == 150 * (1 + math.ceil((W.EMBER_GRASS_HP - 1) / 2.0)),
      "FIRE_LIFE_MAX %d rests on the def: MaxHitPoints %s (want %d), Flammability %s (want %s)"
      % (W.FIRE_LIFE_MAX, hp and hp.group(1), W.EMBER_GRASS_HP, fl and fl.group(1), W.EMBER_GRASS_FLAMMABILITY))
PACES_ALL = range(90, 261)
miss = [pc for pc in PACES_ALL if W.carry_ticks(pc) != M.paced(KP["WindCarryTicks"], pc)]
check(not miss and W.window_ticks(W.PACE_MIN) == W.WINDOW_TICKS_010,
      "wind_burn_live.carry_ticks == the model's paced carry at %d paces (%d differ); window at 0.1.0's pace %d ticks"
      % (len(PACES_ALL), len(miss), W.window_ticks(W.PACE_MIN)))


def model_run(bearing, wind_on, cover=1.0, seed=0, H=W.STRIP_H + 8, Wd=W.STRIP_W + 8, splits=1, mode="carry", pace=None,
              merge=True):
    """The scene in the model: grass inside a 4-cell bare ring, a 9-cell line across the wind through the middle, burned
    W.run_window(pace, wind_on) and read at W.SAMPLES samples as the live script reads them; pace None is the shipped Fire pace
    (pyre_burn_sim.DEFAULTS). -> a reading in wind_burn_live's shape, plus life (the longest any fire burned) and lane_depth
    (the most fires burning at once in one lane along the wind)."""
    pace = M.DEFAULTS["fire_pace"] if pace is None else pace
    rng = np.random.default_rng(1000 + seed)
    plant = np.zeros((H, Wd), np.int8)
    plant[4:H - 4, 4:Wd - 4] = np.where(rng.random((H - 8, Wd - 8)) < cover, 1, 0)
    carried = wind_on and mode != "even"
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, wind=bearing if carried else None, carried=carried, carry_splits=splits, **CARRY, fire_pace=pace,
              carry_merge=merge)
    cx, cz = 4 + W.LINE, H // 2
    before = int((s.size > 0).sum())
    lit = s.light_line(cx, cz, 9, 0.35, angle=bearing + 90)
    r = math.radians(bearing)
    wx, wz = math.sin(r), math.cos(r)
    window = W.run_window(pace, wind_on)
    step = window // W.SAMPLES
    down = up = outer = life = depth = 0
    peak, nxt = lit, step
    prev = s.size > 0
    while s.tick < window:
        s.beat()
        cur = s.size > 0
        died = prev & ~cur
        if died.any():                                 # the last tick it was seen burning, less its birth
            life = max(life, int((s.tick - s.born[died]).max()) - M.BEAT)
        prev = cur
        if s.tick >= nxt:
            nxt += step
            zs, xs = np.nonzero(cur)
            peak = max(peak, len(xs))
            if len(xs):
                al = (xs - cx) * wx + (zs - cz) * wz
                ac = (xs - cx) * wz - (zs - cz) * wx
                down = max(down, int(round(al.max())))
                up = max(up, int(round((-al).max())))
                outer = max(outer, int((np.abs(ac) >= 7.5).sum()))      # the outer three lanes each side of a 21-wide strip
                lanes = np.round(ac).astype(int)
                depth = max(depth, int(np.bincount(lanes - lanes.min()).max()))
    rd = run_reading(bearing, wind_on, down, up, outer, lit=lit, peak=peak, before=before, pace=pace, window=window)
    rd.update(life=life, lane_depth=depth)
    return rd


def scene_pace(pace, seeds):
    """The scene's three runs on each seed at one pace, read through verdict_rows. -> (fails, worst dict, cases)."""
    fails, w = 0, dict(lean=1e9, outer=0, peak=0, b_outer=1e9, b_margin=1e9, life=0, depth=0)
    for sd in seeds:
        f, r, b = model_run(90, True, seed=sd, pace=pace), model_run(270, True, seed=sd, pace=pace), model_run(90, False, seed=sd, pace=pace)
        rows = verdict(f, r, b)
        if pace != W.PACE_DEFAULT:   # the start row asks for the shipped default; a second-reading pace reads every other row
            rows = [x for x in rows if not x[0].startswith("start the Fire pace")]
        fails += not all(ok for _, ok, _ in rows)
        lean = min(f["down_cells"] - f["up_cells"], r["down_cells"] - r["up_cells"])
        w["lean"] = min(w["lean"], lean)
        w["outer"] = max(w["outer"], f["fires_in_outer_lanes"], r["fires_in_outer_lanes"])
        w["peak"] = max(w["peak"], f["peak_fires"], r["peak_fires"])
        w["b_outer"] = min(w["b_outer"], b["fires_in_outer_lanes"])
        w["b_margin"] = min(w["b_margin"], lean - abs(b["down_cells"] - b["up_cells"]))
        w["life"] = max(w["life"], f["life"], r["life"])
        w["depth"] = max(w["depth"], f["lane_depth"], r["lane_depth"])
    return fails, w, len(seeds)


def say(pace, fails, w, n, label):
    check(fails == 0 and w["life"] <= W.FIRE_LIFE_MAX and w["depth"] <= W.rows_deep(pace),
          "%s pace %3d window %5d: %d of %d seeds fail | lean %d (>0) | outer %d (limit 0) | peak %d of limit %d (%.1f x 9 lit) "
          "| control outer %d (>0), lean margin %d (>0) | fire life %d of %d | lane depth %d of %d"
          % (label, pace, W.window_ticks(pace), fails, n, w["lean"], w["outer"], w["peak"], W.peak_limit(pace), w["peak"] / 9.0,
             w["b_outer"], w["b_margin"], w["life"], W.FIRE_LIFE_MAX, w["depth"], W.rows_deep(pace)))


SEEDS = range(40)
print("-- 3. the scene's layout through the shipped carry: wind 90, wind 270, wind off")
for pace, label in ((W.PACE_DEFAULT, "deciding, shipped"), (W.PACE_MIN, "second, 0.1.0's ")):
    say(pace, *scene_pace(pace, SEEDS), label=label)
sweep_fail = []
sweep_w = dict(lean=1e9, peak_frac=0.0, life=0, depth_over=0, outer=0)
for pace in range(W.PACE_MIN, W.PACE_MAX + 1, 5):
    fails, w, n = scene_pace(pace, range(8))
    ok = fails == 0 and w["life"] <= W.FIRE_LIFE_MAX and w["depth"] <= W.rows_deep(pace)
    if not ok:
        sweep_fail.append(pace)
    sweep_w["lean"] = min(sweep_w["lean"], w["lean"])
    sweep_w["outer"] = max(sweep_w["outer"], w["outer"])
    sweep_w["peak_frac"] = max(sweep_w["peak_frac"], w["peak"] / float(W.peak_limit(pace)))
    sweep_w["life"] = max(sweep_w["life"], w["life"])
    sweep_w["depth_over"] = max(sweep_w["depth_over"], w["depth"] - W.rows_deep(pace))
n_sweep = len(range(W.PACE_MIN, W.PACE_MAX + 1, 5))
check(not sweep_fail, "every 5 percent of the slider %d..%d x 8 seeds: failing paces %s | lean %d (>0) | outer %d (limit 0) | "
      "peak at most %.2f of its limit | fire life %d of %d | lane depth at most %+d of rows_deep | %d paces, %d cases"
      % (W.PACE_MIN, W.PACE_MAX, sweep_fail, sweep_w["lean"], sweep_w["outer"], sweep_w["peak_frac"], sweep_w["life"],
         W.FIRE_LIFE_MAX, sweep_w["depth_over"], n_sweep, n_sweep * 8))

print("-- 4. planted model faults on the same layout at the shipped pace %d: each refused on every seed" % W.PACE_DEFAULT)
orig = M.wind_probes
# The one-axis fault lights each probe and its opposite. With the kernel's merge (a probe holding a fire ends the carry)
# its upwind arm meets its own parent still burning at the shipped pace (carry 600 ticks, fire life up to 2,100): it walks
# down 5-8, up 1-3 on 10 of 10 seeds, a wind line, so it plants no fault there. Merge off, it walks both ways (down 9-14,
# up 9-15) and floods (peak 276-399 of limit 60-75) at paces 100, 200 and 250: the fault it names.
FAULTS = [
    ("the carry walks east whatever the wind", lambda b, r1, r2, reach: orig(90.0, r1, r2, reach), 1, "carry", True),
    ("the carry lights downwind and upwind (one axis)",
     lambda b, r1, r2, reach: [c for p in orig(b, r1, r2, reach) for c in (p, (-p[0], -p[1]))], 2, "carry", False),
    ("vanilla's even spread with the wind on", orig, 1, "even", True),
]
for name, probes, splits, mode, merge in FAULTS:
    M.wind_probes = probes
    try:
        caught = 0
        for sd in SEEDS:
            f = model_run(90, True, seed=sd, splits=splits, mode=mode, merge=merge)
            r = model_run(270, True, seed=sd, splits=splits, mode=mode, merge=merge)
            b = model_run(90, False, seed=sd)
            rows = verdict(f, r, b)
            caught += not all(ok for _, ok, _ in rows)
    finally:
        M.wind_probes = orig
    check(caught == len(SEEDS), "%-48s refused on %d of %d seeds" % (name, caught, len(SEEDS)))

print("-- 5. the wider range at the shipped pace %d over its window %d (the wind-off control over %d): every 15 degrees x "
      "cover 1.0/0.97/0.80/0.70 x 3 seeds, 69 x 69 field" % (M.DEFAULTS["fire_pace"], W.run_window(M.DEFAULTS["fire_pace"], True),
                                                            W.run_window(M.DEFAULTS["fire_pace"], False)))
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
