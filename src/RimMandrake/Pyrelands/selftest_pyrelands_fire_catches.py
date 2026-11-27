#!/usr/bin/env python3
"""sc_fire_catches_and_runs (bar fire_catches_and_runs): the scene's offline half decides what it claims.

  1. the pure parts of fire_catches_live.py: the probe's lines parse (a fire no carry reached reads carriedAt -1); head and
     front are read along and across the wind; the front is T_FIRE_PACE_MODEL_OFFLINE's own measure (cross-checked against
     selftest_pyrelands_fire_pace.front_width on the model's burns); the share, the uncarried fires (the spark aside), the
     row pick, the corridor, the opportunity (valid, and each check NOT on its own planted break), the verdict (each row
     False on its own planted fault, None while the same-session pace-100 baseline (off its pace,
     its spark, or headless) or the judge is owed), the end, the capture size.
  2. its numbers against their sources: FlankWidth, HealReach, the Fire pace default and the baseline's
     FirePacePercentMin from RM_BurnKernel.cs (a planted kernel's numbers read back); FRONT_HOURS
     and SHARE_MAX from the decider; the grass defName from the Defs; the probe's methods in FireEcologyHook.cs, its block
     self-contained (fire_catches_take010.py puts it in the 0.1.0 source once); DAY_REACH and HALF_W hold a re-measure of
     the model's day-one burn at the slider's high end.
  3. the shipped chain on a game scripted by the burn model (pyre_burn_sim at the setting's pace; settings stay over a
     reload, the map does not): the pace-100 pass first, then a fresh load and the shipped pass on the same spark cell;
     baseline, stage, burn, log PASS and the verdict owed only the judge; the stored 0.1.0 reading (taken by the chain's
     take mode on the model) is the cross-check only: a stored 999 or 1.0 decides nothing; FAIL on each planted forbidden
     effect (a flood, a fire no carry reached, a spark that never takes, a build that ignores the Fire pace so the head
     is no faster than the pace-100 head, a new error line); UNMEASURED on each planted invalid opportunity (a pawn in
     every corridor, the weather turned).
  4. the record: validation.py registers the chain; the test table's row names the bar, the chain and its command.

Run: python3 <this file>   exit 0 = every check PASS. Each section prints its worst value, its limit and its cases.
"""
import importlib.util
import json
import math
import os
import random
import re
import sys
import tempfile
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(ROOT, "design", "concepts", "Pyrelands")
N = {"run": 0, "bad": 0}


def check(name, ok, detail=""):
    N["run"] += 1
    if not ok:
        N["bad"] += 1
        print("FAIL  %s -- %s" % (name, str(detail)[:300]))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


W = load("fire_catches_live", "fire_catches_live.py")
TK = load("fire_catches_take010", "fire_catches_take010.py")
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "modcheck")]
import pyre_burn_sim as M  # noqa: E402
import selftest_pyrelands_fire_pace as FP  # noqa: E402
import validation as V  # noqa: E402

# ---- 1. pure parts
line = "tick=5000;open=9;stamps=1;fires=13:40:2600|12:40:-1|20:41:-1;burned=12:40|13:40"
r = W.parse_burn(line)
check("parse_burn reads fires with carriedAt (-1 kept) and burned cells", r and r["fires"] == [(13, 40, 2600), (12, 40, -1),
      (20, 41, -1)] and r["burned"] == {(12, 40), (13, 40)} and r["open"] == 9 and r["stamps"], r)
check("parse_burn of an empty burn", W.parse_burn("tick=1;open=5;stamps=1;fires=;burned=") == {
    "tick": 1, "open": 5, "stamps": True, "fires": [], "burned": set()})
check("parse_burn of an error line is None", W.parse_burn("error=no current map") is None)
check("parse_burn of a non-string is None", W.parse_burn(None) is None)
# the carry's geometry (RM_BurnKernel: WindProbes, FlankPlan, HealDirs), east and north
east = W.carry_steps(90, alone=True)
check("carry_steps alone east: the carry's targets, d 1..CARRY_REACH straight or diagonal",
      east == sorted((d, e) for d in range(1, W.CARRY_REACH + 1) for e in (0, d, -d)), east)
full = set(W.carry_steps(90))
check("carry_steps east: a flank or heal lights one cell beside or one back beside the target, never behind the source",
      set(east) <= full and (0, 1) in full and (0, -1) in full and (1, 3) in full and (2, -3) in full
      and all(dx >= 0 for dx, dz in full) and (0, 0) not in full and max(abs(dz) for dx, dz in full) == W.CARRY_REACH + 1,
      sorted(full))
north = W.carry_steps(0, alone=True)
check("carry_steps alone north (bearing 0 = +z) is east turned", sorted((dz, -dx) for dx, dz in north) == east
      or sorted((dz, dx) for dx, dz in north) == east, north)
try:
    W.carry_steps(45)
    check("carry_steps refuses a wind off a compass quarter", False)
except ValueError:
    check("carry_steps refuses a wind off a compass quarter", True)
lane = set((x, 40) for x in range(12, 30))
check("flood follows a lane of fuel from the start", W.flood(lane, (12, 40), 90) == lane)
gap = lane - {(16, 40), (17, 40), (18, 40)}
check("flood stops at a gap wider than CARRY_REACH", W.flood(gap, (12, 40), 90) == set((x, 40) for x in range(12, 16)))
check("flood never steps upwind", W.flood({(12, 40), (11, 40), (10, 40)}, (12, 40), 90) == {(12, 40)})
check("unreached: a burn walked from the spark is all reached", W.unreached(burn_read0 := {
    "fires": [(14, 41, 5)], "burned": {(12, 40), (13, 40)}}, (12, 40), 90) == [], burn_read0)
check("unreached: an upwind stray and a far stray are unreached", W.unreached(
    {"fires": [(10, 40, -1), (40, 40, 3)], "burned": {(12, 40), (13, 40)}}, (12, 40), 90) == [(10, 40), (40, 40)])
check("unreached: the source stamped, the fire it lit at -1 in reach is no stray; one out of reach is",
      W.unreached(r, (12, 40), 90) == [(20, 41)] and W.unreached(
          {"fires": [(13, 40, 2600), (15, 40, -1)], "burned": {(12, 40)}}, (12, 40), 90) == [])
check("ungoverned: -1 at one read only is a fire not yet carried", W.ungoverned(
    [(1, {"fires": [(13, 40, -1)]}), (2, {"fires": [(13, 40, 2600), (15, 40, -1)]})]) == [])
check("ungoverned: -1 at two successive reads is a fire the wind does not carry", W.ungoverned(
    [(1, {"fires": [(13, 40, -1)]}), (2, {"fires": [(13, 40, -1)]}), (3, {"fires": []})]) == [(13, 40)])
check("ungoverned: -1 at two reads with one between is not successive", W.ungoverned(
    [(1, {"fires": [(13, 40, -1)]}), (2, {"fires": []}), (3, {"fires": [(13, 40, -1)]})]) == [])
band = set((x, z) for x in range(12, 163) for z in range(30, 51))
check("fuel_walk: an unbroken band walks the reach", W.fuel_walk(band, (12, 40), 90, 150, 30) == 150)
brk = band - set((x, z) for x in (18, 19, 20) for z in range(30, 51))
check("fuel_walk: a firebreak 3 cells wide across the band stops it", W.fuel_walk(brk, (12, 40), 90, 150, 30) == 5)
# live 2026-11-27 z 40: bare ground 4 cells downwind, grass around it to the north; both builds stopped at head 5
patch = band - set((x, z) for x in range(15, 22) for z in range(34, 47))
check("fuel_walk: a bare patch ahead of the spark stops the lone line though grass goes round it",
      W.fuel_walk(patch, (12, 40), 90, 150, 30) <= 3, W.fuel_walk(patch, (12, 40), 90, 150, 30))
check("fuel_walk: no fuel at the spark walks 0", W.fuel_walk(band - {(12, 40)}, (12, 40), 90, 150, 30) == 0)
check("share counts burning or black cells over open ground", abs(W.share(r) - 3 / 9.0) < 1e-9, W.share(r))
check("head along east", abs(W.head({(12, 40), (30, 2)}, (12, 40), 90) - 18) < 1e-9)
check("head along north", abs(W.head({(12, 40), (12, 55)}, (12, 40), 0) - 15) < 1e-9)
check("front_width east: across is z, gaps up to HealReach pass",
      W.front_width([(20, z) for z in (0, 1, 2, 8, 9)], 90) == 10 and W.front_width([(20, z) for z in (0, 1, 2, 9)], 90) == 3)
check("front_width of nothing is 0", W.front_width([], 90) == 0)
rng = random.Random(7)
worst = 0
for case in range(200):                                   # the decider's own measure on random burns, eight compass steps
    bearing = rng.choice([0, 45, 90, 135, 180, 225, 270, 315, 100, 200])
    cells = set((rng.randrange(60), rng.randrange(60)) for _ in range(rng.randrange(1, 40)))
    a = np.zeros((60, 60))
    for x, z in cells:
        a[z, x] = 0.3
    d = abs(W.front_width(cells, bearing) - FP.front_width(a, bearing, 5))
    worst = max(worst, d)
print("[fcr-self] front_width against the decider's: worst difference %d limit 0 cases 200" % worst)
check("front_width is T_FIRE_PACE_MODEL_OFFLINE's front_width on 200 random burns", worst == 0, worst)
check("candidate rows keep HALF_W off the edges", W.candidate_rows((250, 250)) == list(range(30, 220, 10)))
c_ok = {"cells": "100", "open": "95", "ember": "90", "emberAt": "1", "pawns": "0", "buildings": "0", "edge": "237"}
c_lo = dict(c_ok, ember="60")
c_pawn = dict(c_ok, ember="99", pawns="1")
check("pick_row: the most ember grass, no pawn", W.pick_row([(30, c_lo), (40, c_ok), (50, c_pawn)]) == (40, c_ok))
check("pick_row: ties to the lowest row", W.pick_row([(60, c_ok), (40, c_ok)])[0] == 40)
check("pick_row: none clean is None", W.pick_row([(30, c_pawn), (40, None)]) is None)
check("pick_row: walks given, a row short of the reach is passed over", W.pick_row(
    [(40, c_ok), (50, c_lo)], {40: 5, 50: 150}, 150) == (50, c_lo))
check("pick_row: walks given, no row walks is None", W.pick_row([(40, c_ok)], {40: 5}, 150) is None)
check("corridor_rect stays inside the map", W.corridor_rect((12, 20), (250, 250)) == (12, 0, W.DAY_REACH + 1, 51)
      and W.corridor_rect((200, 230), (250, 250)) == (200, 200, 50, 50), W.corridor_rect((12, 20), (250, 250)))
ok, why, orows = W.opportunity(c_ok, ["Clear"] * 24, 150)
check("opportunity: a valid corridor and a clear day hold", ok and len(orows) == 6, why)
for name, corr, wx in (("spark cell holds ember grass", dict(c_ok, emberAt="0"), None),
                       ("corridor ember grass to the edge", c_lo, None),
                       ("pawns in a day's front", dict(c_ok, pawns="2"), None),
                       ("buildings in a day's front", dict(c_ok, buildings="1"), None),
                       ("weather clear at every read", c_ok, ["Clear"] * 5 + ["Rain"])):
    ok, why, orows = W.opportunity(corr, wx or ["Clear"] * 24, 150)
    bad = [x["check"] for x in orows if not x["ok"]]
    check("opportunity: planted %r breaks only its own check" % name, not ok and bad == [name], (bad, why))
check("opportunity of no corridor is invalid", not W.opportunity(None, ["Clear"], 150)[0])
for walk in (5, None):
    ok, why, orows = W.opportunity(c_ok, ["Clear"] * 24, walk)
    bad = [x["check"] for x in orows if not x["ok"]]
    check("opportunity: a walk of %r breaks only the walk check" % walk, not ok and bad == [
        "the plants carry a line a day's reach"], (bad, why))


def burn_read(fires, burned, open_=1000):
    return {"tick": 0, "open": open_, "stamps": True, "fires": list(fires), "burned": set(burned)}


SP = (12, 100)
PMIN = FP.kconst("FirePacePercentMin")   # the 0.1.0 carry clock (Conductor's ruling 2026-11-27 5:28 AM PST), from the C#
BASE = {"head": 49.0, "pace": PMIN, "spark": SP}   # a same-session pace-100 reading
HEAD_ROW = "the day-end head beats the same-session pace-%d head" % PMIN
good = [(1, burn_read([(12, 100, -1), (13, 100, 2)], [SP])),
        (5, burn_read([(30, z, 9) for z in range(95, 108)], [(x, 100) for x in range(12, 30)])),
        (24, burn_read([(90, z, 9) for z in range(90, 110)], [(x, 100) for x in range(12, 90)]))]
rows = W.verdict(good, SP, 90, BASE, judge=True)
check("verdict: a good day holds every row", all(x["ok"] is True for x in rows) and len(rows) == 7, rows)
check("verdict rows carry worst, limit and cases", all(set(x) == {"check", "ok", "worst", "limit", "cases"} for x in rows))
check("verdict: the head row compares against the same-session pace-%d baseline" % PMIN, HEAD_ROW in [x["check"] for x in rows],
      [x["check"] for x in rows])
fh = [x for x in rows if x["check"].startswith("a front")][0]
check("verdict: the front's hour is the first with FlankWidth across", fh["worst"] == 5, fh)


def only_false(rows, name):
    return [x["check"] for x in rows if x["ok"] is False] == [name]


faults = (("the spark burns at hour 1", [(1, burn_read([], [SP]))] + good[1:], BASE),
          ("a front FlankWidth wide by hour 24", [good[0], (24, burn_read([(90, z, 9) for z in range(95, 104)],
                                                                          [(x, 100) for x in range(12, 90)]))], BASE),
          (HEAD_ROW, good, dict(BASE, head=78.0)),
          ("burning or black share of open ground", good[:2] + [(24, burn_read(good[2][1]["fires"], good[2][1]["burned"],
                                                                                open_=150))], BASE),
          ("fire on a cell no carry reached", good[:2] + [(24, burn_read(good[2][1]["fires"] + [(200, 10, -1)],
                                                                         good[2][1]["burned"]))], BASE),
          ("fire on a cell no carry reached", good[:2] + [(24, burn_read(good[2][1]["fires"] + [(10, 100, 9)],   # upwind,
                                                                         good[2][1]["burned"]))], BASE),  # carried
          ("a fire the wind does not carry", [good[0], (5, burn_read(good[1][1]["fires"] + [(31, 100, -1)], good[1][1]["burned"])),
                                              (24, burn_read(good[2][1]["fires"] + [(31, 100, -1)], good[2][1]["burned"]))],
           BASE))
for name, hourly, reading in faults:
    rows = W.verdict(hourly, SP, 90, reading, judge=True)
    check("verdict: planted fault breaks only %r" % name, only_false(rows, name), [(x["check"], x["ok"]) for x in rows])
rows = W.verdict(good, SP, 90, None, judge=None)
check("verdict: no baseline and no judge leave those two rows None, none False", [x["check"] for x in rows
      if x["ok"] is None] == [HEAD_ROW, "a blind judge reads a walking line"]
      and not [x for x in rows if x["ok"] is False], rows)
check("verdict: the owed baseline names its pass", "pace-%d pass" % PMIN in [x for x in rows if x["ok"] is None][0]["limit"],
      [x for x in rows if x["ok"] is None][0])
# the baseline is the bar's only when it was read at FirePacePercentMin on the same spark: a reading at another pace (the
# shipped one: a baseline that equals what it is compared with) or off another spark is no baseline, never a pass or a fail
worst_off = []
for label, base in (("at the shipped pace", dict(BASE, pace=W.PACE_DEFAULT, head=10.0)), ("with no pace read", dict(BASE, pace=None,
                    head=10.0)), ("off another spark", dict(BASE, spark=(12, 140), head=10.0)),
                    ("with no head", dict(BASE, head=None))):
    rows = W.verdict(good, SP, 90, base, judge=True)
    hr = [x for x in rows if x["check"] == HEAD_ROW]
    worst_off.append((label, hr[0]["ok"] if hr else "absent"))
    check("verdict: a baseline %s leaves the head row None (no verdict), every other row holds" % label,
          hr and hr[0]["ok"] is None and all(x["ok"] is True for x in rows if x["check"] not in (HEAD_ROW,)), (label, hr))
print("[fcr-self] baselines off the bar's (pace %d, same spark): head row %r limit None cases %d" % (PMIN, worst_off,
                                                                                                    len(worst_off)))
rows = W.verdict(good, SP, 90, BASE, judge=False)
check("verdict: a judge who reads no walking line breaks only that row", only_false(rows, "a blind judge reads a walking line"))
check("end at the day", W.end_reached(24, good[0][1], SP, 90, 237) and not W.end_reached(23, good[0][1], SP, 90, 237))
check("end at the edge", W.end_reached(3, burn_read([(248, 100, 9)], []), SP, 90, 237))
worst_px = 0
for rect in ((0, 0, 250, 250), (10, 10, 3, 3), (0, 0, 40, 200), (5, 5, 151, 61)):
    worst_px = max(worst_px, max(rect[2], rect[3]) * W.shot_ppc(rect))
print("[fcr-self] capture long side: worst %d px limit %d cases 4" % (worst_px, W.SHOT_PX))
check("captures stay at or under SHOT_PX", worst_px <= W.SHOT_PX, worst_px)
check("shot_rect pads and clips", W.shot_rect({(0, 0), (10, 4)}, (250, 250)) == (0, 0, 16, 10))
check("error_lines keeps errors and exceptions only", W.error_lines([{"type": "Error", "text": "a"}, {"type": "Warning",
      "text": "b"}, {"level": "exception", "text": "c"}]) == ["a", "c"])

# ---- 2. numbers against their sources
check("FLANK_WIDTH is RM_BurnKernel.FlankWidth", W.FLANK_WIDTH == FP.kconst("FlankWidth"), (W.FLANK_WIDTH, FP.kconst("FlankWidth")))
check("HEAL_REACH is RM_BurnKernel.HealReach", W.HEAL_REACH == FP.kconst("HealReach"), (W.HEAL_REACH, FP.kconst("HealReach")))
check("PACE_DEFAULT is RM_BurnKernel.FirePacePercentDefault", W.PACE_DEFAULT == FP.kconst("FirePacePercentDefault"),
      (W.PACE_DEFAULT, FP.kconst("FirePacePercentDefault")))
check("PACE_MIN is RM_BurnKernel.FirePacePercentMin", getattr(W, "PACE_MIN", None) == FP.kconst("FirePacePercentMin"),
      (getattr(W, "PACE_MIN", None), FP.kconst("FirePacePercentMin")))
# read from the C#, never a copied number: the module's reader follows a planted kernel file
_k = os.path.join(tempfile.mkdtemp(prefix="fcr_kernel_"), "RM_BurnKernel.cs")
with open(_k, "w", encoding="utf-8") as _f:
    _f.write("public const int FirePacePercentMin = 137;\npublic const int FirePacePercentDefault = 211;\n")
_kc = getattr(W, "kernel_const", None)
check("the baseline pace is read from RM_BurnKernel.cs (a planted kernel's 137 is read as 137)",
      callable(_kc) and _kc("FirePacePercentMin", _k) == 137 and _kc("FirePacePercentDefault", _k) == 211,
      _kc and _kc("FirePacePercentMin", _k))
check("CARRY_REACH is RM_BurnKernel.WindCarryReach", W.CARRY_REACH == FP.kconst("WindCarryReach"),
      (W.CARRY_REACH, FP.kconst("WindCarryReach")))
slow = (FP.kconst("WindCarryTicks") + FP.kconst("WindCarryExtraTicks")) * 100 / float(FP.kconst("FirePacePercentMin"))
print("[fcr-self] a governed fire's latest carry: worst %.0f ticks (pace %d) limit < HOUR %d cases 1" % (
    slow, FP.kconst("FirePacePercentMin"), W.HOUR))
check("ungoverned's two successive hourly reads: every governed fire carries inside an hour, the slider's low end too",
      slow < W.HOUR, slow)
check("FRONT_HOURS and SHARE_MAX are the decider's", (W.FRONT_HOURS, W.SHARE_MAX) == (FP.FRONT_HOURS, FP.SHARE_MAX))
check("SPARK_SIZE is the decider's lit size", W.SPARK_SIZE == FP.LIT_SIZE, (W.SPARK_SIZE, FP.LIT_SIZE))
check("DIRS8 is the model's", W.DIRS8 == M.DIRS8)
defs = "".join(open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
               for dp, _, fs in os.walk(os.path.join(HERE, "Defs")) for f in fs if f.endswith(".xml"))
check("the grass defName is a def", "<defName>%s</defName>" % W.GRASS in defs)
hook = open(os.path.join(HERE, "Source", "FireEcologyHook.cs"), encoding="utf-8").read()
check("the probe's type and methods are in FireEcologyHook.cs", W.PROBE == "RimMandrake.Pyrelands.FireCatchesProbe"
      and "public static class FireCatchesProbe" in hook and "public static string Corridor(string args)" in hook
      and "public static string Burn(string args)" in hook and "namespace RimMandrake.Pyrelands" in hook)
block = TK.probe_block(hook)
check("the probe block is marked and holds the whole class", block and block.count("public static class") == 1
      and "public static string Burn" in block and block.strip().endswith(TK.END), (block or "")[-80:])
tag_like = "namespace RimMandrake.Pyrelands\n{\n    class X { }\n}\n"
merged = TK.inject(tag_like, block)
check("inject puts the block inside the namespace, once", merged and merged.rstrip().endswith("}") and
      merged.index("class FireCatchesProbe") < merged.rstrip().rindex("}") and TK.inject(merged, block) is None)
check("the probe block reads nothing the burn writes (no assignment to a burn field)",
      not re.search(r"\b(SetValue|burnTick\s*\[[^\]]*\]\s*=|\.Destroy\(|TryStartFire)", block or ""))

DAY = W.DAY
worst_al = worst_ac = 0.0
worst_over = -999.0     # the model's day-one head less the fuel_walk of its map: a firebreak the model passes is > 0
worst_stray = 0         # model burn cells no chain of carry steps reaches from its spark
min_walk = 999
cases = 0
for cover in (0.70, 0.97):                      # the model's day-one burn at the slider's high end, east wind (the chain's)
    for blobs in (0, 14):
        for seed in range(3):
            plant, plantable = M.synthetic_map(250, seed, cover=cover, blobs=blobs)
            s = M.Sim(plant, plantable, seed, weather=False, clock=False, keepalive=False, wind=90.0, carried=True,
                      fire_pace=FP.kconst("FirePacePercentMax"))
            zs, xs = np.nonzero(plant[:, :40] == 1)
            k = int(np.argmin((xs - W.SPARK_X) ** 2 + (zs - 125) ** 2))
            x0, z0 = int(xs[k]), int(zs[k])
            s.start(z0, x0, W.SPARK_SIZE)
            while s.tick < DAY:
                s.beat()
            zb, xb = np.nonzero((s.burn >= 0) | (s.size > 0))
            worst_al = max(worst_al, float((xb - x0).max()))
            worst_ac = max(worst_ac, float(np.abs(zb - z0).max()))
            fz, fx = np.nonzero(plant != 0)
            walk = W.fuel_walk(set(zip(fx.tolist(), fz.tolist())), (x0, z0), 90, W.DAY_REACH, W.HALF_W)
            min_walk = min(min_walk, walk)
            worst_over = max(worst_over, float((xb - x0).max()) - walk)
            worst_stray = max(worst_stray, len(W.unreached({"burned": set(zip(xb.tolist(), zb.tolist())), "fires": []},
                                                           (x0, z0), 90)))
            cases += 1
print("[fcr-self] model day-one reach at pace %d: along worst %.1f limit DAY_REACH %d, |across| worst %.1f limit HALF_W %d, "
      "cases %d" % (FP.kconst("FirePacePercentMax"), worst_al, W.DAY_REACH, worst_ac, W.HALF_W, cases))
check("DAY_REACH holds the model's day-one head at the high end", worst_al <= W.DAY_REACH, worst_al)
check("HALF_W holds the model's day-one spread across at the high end", worst_ac <= W.HALF_W, worst_ac)
print("[fcr-self] model burn against fuel_walk: head less walk worst %.1f limit <= 0; unreached cells worst %d limit 0; "
      "walk least %d (the maps' own); cases %d" % (worst_over, worst_stray, min_walk, cases))
check("no model burn passes its map's firebreak (head <= fuel_walk)", worst_over <= 0, worst_over)
# firebreaks carved: live 2026-11-27 z 40 (bare ground 3..9 cells downwind, grass round it; the model on the dumped live
# plants and both builds stop at head 5, fuel_walk reads 5) and a bare band 2 cells wide across the whole corridor. Bare
# and unplantable: the model sprouts grass on plantable bare ground within the day (37 sprouts in a plantable band by hour
# 12), which the stage's planting fills before the burn; fuel_walk is a bound over the ground nothing grows on
worst_cut, cut_walks = -999.0, []
for name, cut in (("patch", lambda x0, z0: (slice(z0 - 6, z0 + 7), slice(x0 + 3, x0 + 10))),
                  ("band", lambda x0, z0: (slice(None), slice(x0 + 40, x0 + 42)))):
    for pace in (FP.kconst("FirePacePercentDefault"), FP.kconst("FirePacePercentMax")):
        plant, plantable = M.synthetic_map(250, 1, cover=0.97, blobs=0)
        x0, z0 = W.SPARK_X, 125
        plant[z0, x0] = 1
        plant[cut(x0, z0)], plantable[cut(x0, z0)] = 0, False
        fz, fx = np.nonzero(plant != 0)
        walk = W.fuel_walk(set(zip(fx.tolist(), fz.tolist())), (x0, z0), 90, W.DAY_REACH, W.HALF_W)
        s = M.Sim(plant, plantable, 1, weather=False, clock=False, keepalive=False, wind=90.0, carried=True, fire_pace=pace)
        s.start(z0, x0, W.SPARK_SIZE)
        while s.tick < DAY:
            s.beat()
        zb, xb = np.nonzero((s.burn >= 0) | (s.size > 0))
        worst_cut = max(worst_cut, float((xb - x0).max()) - walk)
        cut_walks.append((name, pace, walk, int((xb - x0).max())))
print("[fcr-self] carved firebreaks: head less walk worst %.1f limit <= 0, (case, pace, walk, head) %r, cases %d" % (
    worst_cut, cut_walks, len(cut_walks)))
check("a carved firebreak stops the model where fuel_walk says (head <= walk < DAY_REACH)", worst_cut <= 0 and all(
    w < W.DAY_REACH for _, _, w, _ in cut_walks), cut_walks)
check("every model burn cell lies a chain of carry steps from the spark (unreached empty)", worst_stray == 0, worst_stray)


# ---- 3. the shipped chain on a game scripted by the burn model
class Game(object):
    """A 250 x 250 synthetic map burned by pyre_burn_sim at `pace`, east wind; the probe's replies read its arrays."""

    def __init__(self, pace=200, seed=1, cover=0.97):
        self.seed, self.cover, self.pace0, self.cuts = seed, cover, pace, []
        self.loads = []          # at each load of the registered site: how many sparks were lit before it
        self.lit_paces = []      # the Fire pace setting at each spark (None: the tag's build has no such setting)
        self.ignore_pace = False  # planted: the build carries at FirePacePercentMin whatever the setting says
        self.plant, self.plantable = M.synthetic_map(250, seed, cover=cover)
        self.sim = self.new_sim(pace)
        self.weather, self.log, self.dud, self.pawn_rows, self.flood_at, self.stray_at, self.rain_at = \
            "Clear", [], False, False, None, None, None
        self.stray, self.shots, self.lit, self.settings = [], [], [], {}
        self.unread_at = None   # the hour from which the probe's Burn answers unreadably (a read cut short)
        self.put_out = []       # cells of the site's own burn that the stage's extinguish blackens at the spark's tick
        self.plant_reads, self.plants_cut = [], False   # jawa/list_things group=Plant: the rects read; an incomplete read
        self.upwind_at = self.ungov_at = None   # planted: a carried fire upwind of the spark; the spark cell burning uncarried
        self.extra = []                         # (x, z, carriedAt) fires those plant

    def new_sim(self, pace):
        return M.Sim(self.plant, self.plantable, self.seed, weather=False, clock=False, keepalive=False, wind=90.0,
                     carried=True, fire_pace=PMIN if self.ignore_pace else pace)

    def pace(self):
        return self.settings.get("firePacePercent", self.pace0)

    def set(self, values):
        """Mod settings are the game's, not the map's: they stay over a reload. The carry clock reads the pace."""
        self.settings.update(values)
        if "firePacePercent" in values and len(self.lit) == (self.loads[-1] if self.loads else 0):   # no spark on this map yet
            self.sim = self.new_sim(self.pace())

    def reload(self):
        """A fresh load of the registered site: the save's own map back (the stage's planting and the burn gone; a
        planted firebreak is the site's, it stays), the clock at the save's."""
        self.loads.append(len(self.lit))
        self.plant, self.plantable = M.synthetic_map(250, self.seed, cover=self.cover)
        self.sim = self.new_sim(self.pace())
        for a in self.cuts:
            self.cut(*a, keep=False)
        self.stray, self.extra, self.weather = [], [], "Clear"

    def cut(self, x0, x1, plantable=False, keep=True):
        """A bare band across the whole map over columns x0..x1-1 (unplantable: a firebreak nothing grows over)."""
        if keep:
            self.cuts.append((x0, x1, plantable))
        for arr in (self.plant, self.sim.plant):
            arr[:, x0:x1] = 0
        self.sim.hp[:, x0:x1] = 0.0
        self.plantable[:, x0:x1] = plantable
        self.sim.plantable[:, x0:x1] = plantable

    @property
    def tick(self):
        return self.sim.tick

    def corridor(self, args):
        x, z, b, ln, hw = (int(v) for v in args.split(","))
        sl = (slice(max(0, z - hw), min(250, z + hw + 1)), slice(x, min(250, x + ln + 1)))
        cells = self.plant[sl].size
        return "cells=%d;open=%d;ember=%d;emberAt=%d;pawns=%d;buildings=0;edge=%d" % (
            cells, int(self.plantable[sl].sum()), int((self.plant[sl] == 1).sum()), int(self.plant[z, x] == 1),
            1 if self.pawn_rows else 0, 249 - x)

    def burn(self, since):
        s = self.sim
        if self.unread_at is not None and s.tick // 2500 >= self.unread_at:
            return "error=planted unreadable"
        zs, xs = np.nonzero(s.size > 0)
        # the C#'s MapComponent_BurnLine.CarriedAt: the tick this cell's fire carried (WindCarriedFire.Carry stamps its
        # source), -1 for a fire that has not carried yet; the model keeps the same stamp (pyre_burn_sim.carried_at)
        fires = ["%d:%d:%d" % (x, z, s.carried_at[z, x]) for z, x in zip(zs, xs)]
        fires += ["%d:%d:-1" % c for c in self.stray]
        fires += ["%d:%d:%d" % c for c in self.extra]
        zb, xb = np.nonzero(s.burn >= since)
        return "tick=%d;open=%d;stamps=1;fires=%s;burned=%s" % (s.tick, int(self.plantable.sum()), "|".join(fires),
                                                                 "|".join("%d:%d" % (x, z) for z, x in zip(zb, xb)))

    def advance(self, n):
        end = self.sim.tick + n
        while self.sim.tick < end:
            self.sim.beat()
        h = self.sim.tick // 2500
        if self.flood_at is not None and h >= self.flood_at:
            self.sim.burn[self.plantable & (self.sim.burn < 0)] = self.sim.tick
        if self.stray_at is not None and h >= self.stray_at:
            self.stray = [(200, 10)]
        if self.rain_at is not None and h >= self.rain_at:
            self.weather = "Rain"
        sz = self.lit[0][1] if self.lit else 125
        self.extra = ([(W.SPARK_X - 2, sz, 9)] if self.upwind_at is not None and h >= self.upwind_at else []) + (
            [(W.SPARK_X, sz, -1)] if self.ungov_at is not None and h >= self.ungov_at else [])


def run(game, env=None, reading=None):
    out = {"verdicts": {}, "notes": [], "why": {}}

    class Stop(Exception):
        pass

    class Comp(object):
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, et, ev, tb):
            if et is None:
                out["verdicts"][self.name] = "PASS"
            elif et is Stop:
                out["verdicts"][self.name] = ev.args[0]
                out["why"][self.name] = ev.args[1]
                return True
            return False

    class Session(object):
        def _ticks(self):
            return game.tick

    class T(object):
        session, upstream_failed = Session(), False

        def bridge_call(self, tool, **p):
            if tool == "jawa/weather_set":
                game.weather = p["weather"]
            elif tool == "jawa/static_call" and p.get("type") == W.PROBE:
                return {"success": True, "result": getattr(game, {"Corridor": "corridor", "Burn": "burn"}[p["method"]])(
                    p["args"] if p["method"] == "Corridor" else int(p["args"]))}
            elif tool == "jawa/list_things" and p.get("group") == "Plant":
                x, z, w, h = (int(v) for v in p["rect"].split(","))
                zs, xs = np.nonzero(game.sim.plant[z:z + h, x:x + w] != 0)
                th = [{"def": W.GRASS if game.sim.plant[z + a, x + b] == 1 else "Plant_Grass", "x": x + int(b), "z": z + int(a)}
                      for a, b in zip(zs, xs)]
                game.plant_reads.append(tuple((x, z, w, h)))
                full = len(th) <= int(p.get("limit") or 0) and not game.plants_cut
                return {"success": True, "things": th[:int(p.get("limit") or 0)], "countMatched": len(th),
                        "isCompleteList": full}
            elif tool == "jawa/static_call" and p.get("method") == "SetWindForTest":
                return {"success": True, "result": int(p["args"])}
            elif tool == "jawa/mod_settings_field" and p.get("action") == "get":
                return {"success": True, "value": game.settings.get(p.get("field"))}
            elif tool == "jawa/map_fire" and p.get("action") == "start":
                x, z, w, h = (int(v) for v in p["rect"].split(","))
                game.lit.append((x, z, p.get("fireSize")))
                game.lit_paces.append(game.settings.get("firePacePercent"))
                if not game.dud:
                    game.sim.start(z, x, p["fireSize"])
            return {"success": True}

        def screenshot(self, name=None, rect=None, ppc=None):
            game.shots.append((name, rect, ppc))
            return "D:\\fake\\%s.png" % name

    def plants(t, what, rect, growth=1.0):
        x, z, w, h = rect
        sl = (slice(z, z + h), slice(x, x + w))
        grow = game.plantable[sl] & (game.plant[sl] != 1)   # set_plants: ember grass on the plantable cells only
        for arr in (game.plant, game.sim.plant):
            arr[sl] = np.where(grow, 1, arr[sl])
        game.sim.hp[sl] = np.where(grow, M.HP[1], game.sim.hp[sl])

    def stop(v):
        def f(*a):
            raise Stop(v, a[-1])
        return f

    chains = {}
    ns = types.SimpleNamespace(
        _teardown=lambda **k: (lambda fn: fn), _comp=lambda t, n, **k: Comp(n), _live=lambda t: True,
        _independent=lambda t: None, _load_registered_site=lambda t: (game.reload(), (1, None))[1], _on_site=lambda t: None,
        _note=lambda t, n, v: out["notes"].append((n, v)), _wait=lambda t, n: game.advance(n),
        _extinguish=lambda t: [game.sim.burn.__setitem__((z, x), game.tick) for x, z in game.put_out], _ash=lambda t, r=None: {"weather": game.weather}, _map_size=lambda t: (250, 250),
        _plants=plants, _rs=V._rs, _log_mark=lambda t: "m", _log_since=lambda t, m: game.log,
        _set=lambda t, v: game.set(v), SETTINGS=V.SETTINGS, _unmeasured=stop("UNMEASURED"), _fail=stop("FAIL"))
    W.register(types.SimpleNamespace(chain=lambda n: (lambda fn: chains.setdefault(n, fn))), ns)
    keep = dict((k, os.environ.get(k)) for k in (W.TAKE_ENV, W.OUT_ENV))
    keep_reading = W.READING_010
    for k in keep:
        os.environ.pop(k, None)
    tmp = tempfile.mkdtemp(prefix="fcr_chain_")
    os.environ[W.OUT_ENV] = tmp
    os.environ.update(env or {})
    W.READING_010 = reading or os.path.join(tmp, "no_reading.json")
    try:
        chains["fire_catches_and_runs"](T())
    finally:
        W.READING_010 = keep_reading
        for k in keep:
            os.environ.pop(k, None)
            if keep[k] is not None:
                os.environ[k] = keep[k]
    m = os.path.join(tmp, "manifest.json")
    out["manifest"] = json.load(open(m, encoding="utf-8")) if os.path.exists(m) else None
    return out


COMPS = ("fire_catches_stage", "fire_catches_burn", "fire_catches_verdict", "fire_catches_no_error_line")
reading = os.path.join(tempfile.mkdtemp(prefix="fcr_010_"), "fire_catches_010_reading.json")
g0 = Game(pace=100)
y0 = run(g0, env={W.TAKE_ENV: "1"}, reading=reading)
r010 = W.load_reading(reading)
check("take mode on the model at 0.1.0's pace: writes the reading, sets no Fire pace, judges nothing",
      r010 and r010.get("head") and "firePacePercent" not in g0.settings and all(y0["verdicts"].get(c) == "PASS" for c in COMPS),
      (r010, g0.settings, y0["verdicts"], y0["why"]))
g1 = Game(pace=100)
g1.put_out = [(183, 180), (183, 181)]   # live 2026-11-27, the 0.1.0 take: the site's standing burn, put out at the stage
r1 = os.path.join(tempfile.mkdtemp(prefix="fcr_put_"), "r.json")
y1 = run(g1, env={W.TAKE_ENV: "1"}, reading=r1)
print("[fcr-self] the site's burn put out at the spark's tick: head %s against %s clean (limit equal) cases=1"
      % ((W.load_reading(r1) or {}).get("head"), (r010 or {}).get("head")))
check("planted the site's own burn put out at the spark's tick, 171 cells downwind: the 0.1.0 head is the spark's alone",
      (W.load_reading(r1) or {}).get("head") == (r010 or {}).get("head"), (W.load_reading(r1), r010, y1["why"]))
g = Game(pace=200)
x = run(g, reading=reading)
rows = dict((rw["check"], rw) for rw in (x["manifest"] or {}).get("rows", []))
print("[fcr-self] model chain: 0.1.0 head %s, shipped head %s, front at hour %s, share worst %s limit %s, uncarried %s, "
      "hours %s" % ((r010 or {}).get("head"), (x["manifest"] or {}).get("head"),
                    rows.get("a front FlankWidth wide by hour 24", {}).get("worst"),
                    rows.get("burning or black share of open ground", {}).get("worst"), W.SHARE_MAX,
                    rows.get("fire on a cell no carry reached", {}).get("worst"), (x["manifest"] or {}).get("hours")))
check("the chain on the model at the shipped pace: stage, burn and log PASS", all(x["verdicts"].get(c) == "PASS" for c in
      ("fire_catches_stage", "fire_catches_burn", "fire_catches_no_error_line")), (x["verdicts"], x["why"]))
check("... the verdict owed only the judge (UNMEASURED, never FAIL)", x["verdicts"].get("fire_catches_verdict") == "UNMEASURED"
      and "judge" in x["why"].get("fire_catches_verdict", "") and "0.1.0" not in x["why"].get("fire_catches_verdict", ""),
      x["why"])
check("... every mechanical row holds, the head beats the same-session pace-100 head", rows and all(rw["ok"] is True for k, rw in rows.items()
      if k != "a blind judge reads a walking line"), rows)
check("... the Fire pace set is the shipped default and wind carries on", g.settings == dict(W.HOLD_OFF, windCarriesFireEnabled=True,
      firePacePercent=W.PACE_DEFAULT), g.settings)
check("... the biome's other fire sources held off, the burn line on (one spark; live 2026-11-27 read foreign fires)",
      all(g.settings.get(k) is False for k in ("fireClockEnabled", "fireHawkSpreadEnabled", "scorchFruitEnabled"))
      and g.settings.get("burnLineEnabled") is True and all(g0.settings.get(k) == v for k, v in W.HOLD_OFF.items()),
      (g.settings, g0.settings))
covered = set((x0 + i, z0 + j) for x0, z0, w, h in g.plant_reads for i in range(w) for j in range(h))
check("... the stage reads every plant from the spark column a day's reach on, every map row, in FUEL_ROWS reads",
      covered >= set((x, z) for x in range(W.SPARK_X, W.SPARK_X + W.DAY_REACH + 1) for z in range(250))
      and max(h for _, _, _, h in g.plant_reads) <= W.FUEL_ROWS, g.plant_reads[:6])
check("... the stage's fuel_walk is the map's: a day's reach", (x["manifest"] or {}).get("walk") == W.DAY_REACH,
      (x["manifest"] or {}).get("walk"))
check("... one spark a pass, one cell, at SPARK_SIZE, the same cell both passes", len(g.lit) == 2
      and g.lit == [(W.SPARK_X, g.lit[0][1], W.SPARK_SIZE)] * 2, g.lit)
check("... captures named by hour, each at or under SHOT_PX", g.shots and all(max(s[1][2], s[1][3]) * s[2] <= W.SHOT_PX
      for s in g.shots) and [s[0] for s in g.shots][0] == "fcr_h01", g.shots)
# the baseline (Conductor's ruling 2026-11-27 5:28 AM PST): the same chain run reads the head at FirePacePercentMin (the
# 0.1.0 carry clock) on a fresh load of the same site, in the same session, then at the shipped pace; the verdict compares
# those two; the stored 0.1.0 reading is only the cross-check of pace 100 against the 0.1.0 build
man = x["manifest"] or {}
base = man.get("baseline") or {}
print("[fcr-self] model chain: baseline (pace %s) head %s, shipped head %s, margin %s limit > 0 cases 1; loads %r, paces at "
      "the sparks %r" % (base.get("pace"), base.get("head"), man.get("head"), None if base.get("head") is None or
                         man.get("head") is None else round(man["head"] - base["head"], 1), g.loads, g.lit_paces))
check("... the chain lit the pace-%d spark first, then the shipped one (the setting at each spark)" % PMIN,
      g.lit_paces == [PMIN, W.PACE_DEFAULT], g.lit_paces)
check("... a fresh load of the site before each pass, the second after the baseline's spark (one session, no stop)",
      g.loads == [0, 1], g.loads)
check("... the baseline component PASS, its reading the game's pace read back, the shipped spark's cell",
      x["verdicts"].get("fire_catches_baseline") == "PASS" and base.get("pace") == PMIN and base.get("head")
      and tuple(base.get("spark") or ()) == tuple(man.get("spark") or ()), (x["verdicts"], x["why"], base))
cc = man.get("cross_check") or {}
check("... the cross-check records the pace-%d head, the stored 0.1.0 head and their difference" % PMIN,
      cc.get("measured") is True and cc.get("pace_min_head") == base.get("head") and cc.get("head_010") == (r010 or {}).get("head")
      and cc.get("diff") == round(base["head"] - r010["head"], 1), cc)
x2 = run(Game(pace=200), reading=None)
cc2 = (x2["manifest"] or {}).get("cross_check") or {}
check("no stored 0.1.0 reading: the verdict still owed only the judge, the cross-check says not measured",
      x2["verdicts"].get("fire_catches_verdict") == "UNMEASURED" and "judge" in x2["why"].get("fire_catches_verdict", "")
      and "0.1.0" not in x2["why"].get("fire_catches_verdict", "") and cc2.get("measured") is False
      and "not measured" in str(cc2.get("why")), (x2["why"], cc2))
high = os.path.join(tempfile.mkdtemp(prefix="fcr_high_"), "r.json")
W.write_json(high, {"head": 999.0, "spark": [W.SPARK_X, 125], "tag": "planted"})
x3 = run(Game(pace=200), reading=high)
check("a stored 0.1.0 head of 999 decides nothing: the head row holds on the same-session baseline",
      x3["verdicts"].get("fire_catches_verdict") == "UNMEASURED" and "judge" in x3["why"].get("fire_catches_verdict", ""),
      x3["why"])
low = os.path.join(tempfile.mkdtemp(prefix="fcr_low_"), "r.json")
W.write_json(low, {"head": 1.0, "spark": [W.SPARK_X, 125], "tag": "planted"})
gi = Game(pace=200)
gi.ignore_pace = True
x4 = run(gi, reading=low)
r4 = [rw for rw in (x4["manifest"] or {}).get("rows", []) if rw["ok"] is False]
print("[fcr-self] planted a build that carries at pace %d whatever the setting: head %s vs baseline %s, rows NOT %r cases 1" % (
    PMIN, (x4["manifest"] or {}).get("head"), ((x4["manifest"] or {}).get("baseline") or {}).get("head"),
    [rw["check"] for rw in r4]))
check("planted a build that ignores the Fire pace (a stored 0.1.0 head of 1.0 beside it): the verdict FAILs on the head row",
      x4["verdicts"].get("fire_catches_verdict") == "FAIL" and [rw["check"] for rw in r4] == [HEAD_ROW], (x4["why"], r4))
for label, setup, comp, want in (
        ("a flood at hour 6", lambda gm: setattr(gm, "flood_at", 6), "fire_catches_verdict", "FAIL"),
        ("a fire no carry reached at hour 3", lambda gm: setattr(gm, "stray_at", 3), "fire_catches_verdict", "FAIL"),
        ("a spark that never takes", lambda gm: setattr(gm, "dud", True), "fire_catches_verdict", "FAIL"),
        ("a new error line", lambda gm: gm.log.append({"type": "Error", "text": "planted"}), "fire_catches_no_error_line",
         "FAIL"),
        ("a pawn in every corridor", lambda gm: setattr(gm, "pawn_rows", True), "fire_catches_stage", "UNMEASURED"),
        ("the weather turned at hour 5", lambda gm: setattr(gm, "rain_at", 5), "fire_catches_verdict", "UNMEASURED")):
    gm = Game(pace=200)
    setup(gm)
    y = run(gm, reading=reading)
    check("planted %s: the %s is %s" % (label, comp, want), y["verdicts"].get(comp) == want, (y["verdicts"], y["why"]))
gm = Game(pace=200)
gm.unread_at = 3
y = run(gm, reading=reading)
check("planted a burn cut short at hour 3: the verdict is UNMEASURED (no verdict on a partial burn)",
      y["verdicts"].get("fire_catches_burn") == "UNMEASURED" and y["verdicts"].get("fire_catches_verdict") == "UNMEASURED"
      and "before its end" in y["why"].get("fire_catches_verdict", ""), (y["verdicts"], y["why"]))
cut = os.path.join(tempfile.mkdtemp(prefix="fcr_cut_"), "r.json")
gm = Game(pace=100)
gm.unread_at = 3
y = run(gm, env={W.TAKE_ENV: "1"}, reading=cut)
check("planted a take cut short at hour 3: no 0.1.0 reading is written (live 2026-11-27 wrote head 224 from hour 1)",
      not os.path.exists(cut) and y["verdicts"].get("fire_catches_verdict") == "UNMEASURED", (y["verdicts"], y["why"]))
gm = Game(pace=200, cover=0.40)
y = run(gm, reading=reading)
check("thin grass on every row: the stage grows the corridor and the opportunity is valid", y["manifest"] and
      y["manifest"]["planted"] and y["manifest"]["valid"], (y["manifest"] or {}).get("why"))
for label, setup, name in (("a carried fire upwind of the spark", lambda gm: setattr(gm, "upwind_at", 4),
                            "fire on a cell no carry reached"),
                           ("the spark cell burning uncarried from hour 3", lambda gm: setattr(gm, "ungov_at", 3),
                            "a fire the wind does not carry")):
    gm = Game(pace=200)
    setup(gm)
    y = run(gm, reading=reading)
    rows = (y["manifest"] or {}).get("rows") or []
    check("planted %s: the verdict FAILs on that row alone" % label, y["verdicts"].get("fire_catches_verdict") == "FAIL"
          and [rw["check"] for rw in rows if rw["ok"] is False] == [name], ([(rw["check"], rw["ok"]) for rw in rows], y["why"]))
gm = Game(pace=200)
gm.cut(W.SPARK_X + 40, W.SPARK_X + 42)
y = run(gm, reading=reading)
check("planted a firebreak across every row (bare, unplantable, 2 cells): the stage is UNMEASURED, a firebreak, no burn",
      y["verdicts"].get("fire_catches_stage") == "UNMEASURED" and "firebreak" in y["why"].get("fire_catches_stage", "")
      and not gm.lit, (y["verdicts"], y["why"], gm.lit))
gm = Game(pace=200)
gm.cut(W.SPARK_X + 40, W.SPARK_X + 42, plantable=True)
y = run(gm, reading=reading)
check("planted a bare plantable band across every row: the stage grows it over and the opportunity is valid", y["manifest"]
      and y["manifest"]["planted"] and y["manifest"]["valid"] and y["manifest"]["walk"] == W.DAY_REACH,
      (y["verdicts"], y["why"], (y["manifest"] or {}).get("walk")))
gm = Game(pace=200)
gm.plants_cut = True
y = run(gm, reading=reading)
check("planted an incomplete plant read: the stage is UNMEASURED and lights nothing", y["verdicts"].get("fire_catches_stage")
      == "UNMEASURED" and "plants unreadable" in y["why"].get("fire_catches_stage", "") and not gm.lit, (y["verdicts"], y["why"]))

# ---- 4. the record
check("validation.py registers fire_catches_and_runs", any(
    getattr(k, "name", None) == "fire_catches_and_runs" or k == "fire_catches_and_runs"
    or (isinstance(k, tuple) and k[0] == "fire_catches_and_runs") for k in V.suite.chains))
tt = json.load(open(os.path.join(CONCEPT, "version", "test_table.json"), encoding="utf-8"))
row = (tt["tests"].get("sc_fire_catches_and_runs") or {}) if isinstance(tt.get("tests"), dict) else {}
check("the table's row is the bar's and its entry is the registered chain", row.get("for_bar") == "fire_catches_and_runs"
      and row.get("entry") == "fire_catches_and_runs" and str(row.get("file", "")).endswith("Pyrelands/validation.py"),
      {k: row.get(k) for k in ("for_bar", "file", "entry")})
check("the table's command names the chain", re.search(r"--chains fire_catches_and_runs\b", str(row.get("command"))) is not None,
      row.get("command"))
check("the chain's docstring carries the table's command", str(row.get("command")) in (W.__doc__ or ""), row.get("command"))

print("%s: %d checks, %d failed" % (os.path.basename(__file__), N["run"], N["bad"]))
sys.exit(1 if N["bad"] else 0)
