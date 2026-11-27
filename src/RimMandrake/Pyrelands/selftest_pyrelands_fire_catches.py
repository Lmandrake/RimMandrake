#!/usr/bin/env python3
"""sc_fire_catches_and_runs (bar fire_catches_and_runs): the scene's offline half decides what it claims.

  1. the pure parts of fire_catches_live.py: the probe's lines parse (a fire no carry reached reads carriedAt -1); head and
     front are read along and across the wind; the front is T_FIRE_PACE_MODEL_OFFLINE's own measure (cross-checked against
     selftest_pyrelands_fire_pace.front_width on the model's burns); the share, the uncarried fires (the spark aside), the
     row pick, the corridor, the opportunity (valid, and each check NOT on its own planted break), the verdict (each row
     False on its own planted fault, None while the 0.1.0 reading or the judge is owed), the end, the capture size.
  2. its numbers against their sources: FlankWidth, HealReach and the Fire pace default from RM_BurnKernel.cs; FRONT_HOURS
     and SHARE_MAX from the decider; the grass defName from the Defs; the probe's methods in FireEcologyHook.cs, its block
     self-contained (fire_catches_take010.py puts it in the 0.1.0 source once); DAY_REACH and HALF_W hold a re-measure of
     the model's day-one burn at the slider's high end.
  3. the shipped chain on a game scripted by the burn model (pyre_burn_sim at the shipped pace): stage, burn, log PASS and
     the verdict owed only the judge and the 0.1.0 reading; with a 0.1.0 reading taken by the chain itself on the model at
     0.1.0's pace, the head row holds; FAIL on each planted forbidden effect (a flood, a fire no carry reached, a spark
     that never takes, a head no faster than 0.1.0, a new error line); UNMEASURED on each planted invalid opportunity (a
     pawn in every corridor, the weather turned).
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
check("uncarried: the spark's own cell aside, a -1 fire is one", W.uncarried(r, (12, 40)) == [(20, 41)], W.uncarried(r, (12, 40)))
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
check("corridor_rect stays inside the map", W.corridor_rect((12, 20), (250, 250)) == (12, 0, W.DAY_REACH + 1, 51)
      and W.corridor_rect((200, 230), (250, 250)) == (200, 200, 50, 50), W.corridor_rect((12, 20), (250, 250)))
ok, why, orows = W.opportunity(c_ok, ["Clear"] * 24)
check("opportunity: a valid corridor and a clear day hold", ok and len(orows) == 5, why)
for name, corr, wx in (("spark cell holds ember grass", dict(c_ok, emberAt="0"), None),
                       ("corridor ember grass to the edge", c_lo, None),
                       ("pawns in a day's front", dict(c_ok, pawns="2"), None),
                       ("buildings in a day's front", dict(c_ok, buildings="1"), None),
                       ("weather clear at every read", c_ok, ["Clear"] * 5 + ["Rain"])):
    ok, why, orows = W.opportunity(corr, wx or ["Clear"] * 24)
    bad = [x["check"] for x in orows if not x["ok"]]
    check("opportunity: planted %r breaks only its own check" % name, not ok and bad == [name], (bad, why))
check("opportunity of no corridor is invalid", not W.opportunity(None, ["Clear"])[0])


def burn_read(fires, burned, open_=1000):
    return {"tick": 0, "open": open_, "stamps": True, "fires": list(fires), "burned": set(burned)}


SP = (12, 100)
good = [(1, burn_read([(12, 100, -1), (13, 100, 2)], [SP])),
        (5, burn_read([(30, z, 9) for z in range(95, 108)], [(x, 100) for x in range(12, 30)])),
        (24, burn_read([(90, z, 9) for z in range(90, 110)], [(x, 100) for x in range(12, 90)]))]
rows = W.verdict(good, SP, 90, {"head": 49.0}, judge=True)
check("verdict: a good day holds every row", all(x["ok"] is True for x in rows) and len(rows) == 6, rows)
check("verdict rows carry worst, limit and cases", all(set(x) == {"check", "ok", "worst", "limit", "cases"} for x in rows))
fh = [x for x in rows if x["check"].startswith("a front")][0]
check("verdict: the front's hour is the first with FlankWidth across", fh["worst"] == 5, fh)


def only_false(rows, name):
    return [x["check"] for x in rows if x["ok"] is False] == [name]


faults = (("the spark burns at hour 1", [(1, burn_read([], [SP]))] + good[1:], {"head": 49.0}),
          ("a front FlankWidth wide by hour 24", [good[0], (24, burn_read([(90, z, 9) for z in range(95, 104)],
                                                                          [(x, 100) for x in range(12, 90)]))], {"head": 49.0}),
          ("the day-end head beats 0.1.0's", good, {"head": 78.0}),
          ("burning or black share of open ground", good[:2] + [(24, burn_read(good[2][1]["fires"], good[2][1]["burned"],
                                                                                open_=150))], {"head": 49.0}),
          ("fire on a cell no carry reached", good[:2] + [(24, burn_read(good[2][1]["fires"] + [(200, 10, -1)],
                                                                         good[2][1]["burned"]))], {"head": 49.0}))
for name, hourly, reading in faults:
    rows = W.verdict(hourly, SP, 90, reading, judge=True)
    check("verdict: planted fault breaks only %r" % name, only_false(rows, name), [(x["check"], x["ok"]) for x in rows])
rows = W.verdict(good, SP, 90, None, judge=None)
check("verdict: no 0.1.0 reading and no judge leave those two rows None, none False", [x["check"] for x in rows
      if x["ok"] is None] == ["the day-end head beats 0.1.0's", "a blind judge reads a walking line"]
      and not [x for x in rows if x["ok"] is False], rows)
check("verdict: the owed reading names its take", W.TAKE_ENV in [x for x in rows if x["ok"] is None][0]["limit"])
rows = W.verdict(good, SP, 90, {"head": 49.0}, judge=False)
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
            cases += 1
print("[fcr-self] model day-one reach at pace %d: along worst %.1f limit DAY_REACH %d, |across| worst %.1f limit HALF_W %d, "
      "cases %d" % (FP.kconst("FirePacePercentMax"), worst_al, W.DAY_REACH, worst_ac, W.HALF_W, cases))
check("DAY_REACH holds the model's day-one head at the high end", worst_al <= W.DAY_REACH, worst_al)
check("HALF_W holds the model's day-one spread across at the high end", worst_ac <= W.HALF_W, worst_ac)


# ---- 3. the shipped chain on a game scripted by the burn model
class Game(object):
    """A 250 x 250 synthetic map burned by pyre_burn_sim at `pace`, east wind; the probe's replies read its arrays."""

    def __init__(self, pace=200, seed=1, cover=0.97):
        self.plant, self.plantable = M.synthetic_map(250, seed, cover=cover)
        self.sim = M.Sim(self.plant, self.plantable, seed, weather=False, clock=False, keepalive=False, wind=90.0,
                         carried=True, fire_pace=pace)
        self.weather, self.log, self.dud, self.pawn_rows, self.flood_at, self.stray_at, self.rain_at = \
            "Clear", [], False, False, None, None, None
        self.stray, self.shots, self.lit, self.settings = [], [], [], {}
        self.unread_at = None   # the hour from which the probe's Burn answers unreadably (a read cut short)

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
        fires = ["%d:%d:%d" % (x, z, s.born[z, x]) for z, x in zip(zs, xs)]   # with carried on, every fire but the spark is a carry's
        fires += ["%d:%d:-1" % c for c in self.stray]
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
            elif tool == "jawa/static_call" and p.get("method") == "SetWindForTest":
                return {"success": True, "result": int(p["args"])}
            elif tool == "jawa/map_fire" and p.get("action") == "start":
                x, z, w, h = (int(v) for v in p["rect"].split(","))
                game.lit.append((x, z, p.get("fireSize")))
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
        _independent=lambda t: None, _load_registered_site=lambda t: (1, None), _on_site=lambda t: None,
        _note=lambda t, n, v: out["notes"].append((n, v)), _wait=lambda t, n: game.advance(n),
        _extinguish=lambda t: None, _ash=lambda t, r=None: {"weather": game.weather}, _map_size=lambda t: (250, 250),
        _plants=plants, _rs=V._rs, _log_mark=lambda t: "m", _log_since=lambda t, m: game.log,
        _set=lambda t, v: game.settings.update(v), _unmeasured=stop("UNMEASURED"), _fail=stop("FAIL"))
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
check("... every mechanical row holds, the head beats the 0.1.0 reading", rows and all(rw["ok"] is True for k, rw in rows.items()
      if k != "a blind judge reads a walking line"), rows)
check("... the Fire pace set is the shipped default and wind carries on", g.settings == dict(W.HOLD_OFF, windCarriesFireEnabled=True,
      firePacePercent=W.PACE_DEFAULT), g.settings)
check("... the biome's other fire sources held off, the burn line on (one spark; live 2026-11-27 read foreign fires)",
      all(g.settings.get(k) is False for k in ("fireClockEnabled", "fireHawkSpreadEnabled", "scorchFruitEnabled"))
      and g.settings.get("burnLineEnabled") is True and all(g0.settings.get(k) == v for k, v in W.HOLD_OFF.items()),
      (g.settings, g0.settings))
check("... one spark, one cell, at SPARK_SIZE", g.lit == [(W.SPARK_X, g.lit[0][1], W.SPARK_SIZE)] if g.lit else False, g.lit)
check("... captures named by hour, each at or under SHOT_PX", g.shots and all(max(s[1][2], s[1][3]) * s[2] <= W.SHOT_PX
      for s in g.shots) and [s[0] for s in g.shots][0] == "fcr_h01", g.shots)
x2 = run(Game(pace=200), reading=None)
check("no 0.1.0 reading: the verdict UNMEASURED, owed the reading and the judge", x2["verdicts"].get("fire_catches_verdict") ==
      "UNMEASURED" and "0.1.0" in x2["why"].get("fire_catches_verdict", ""), x2["why"])
fast = os.path.join(tempfile.mkdtemp(prefix="fcr_fast_"), "r.json")
y = run(Game(pace=250), env={W.TAKE_ENV: "1"}, reading=fast)
x3 = run(Game(pace=200), reading=fast)
check("a head no faster than the reading FAILs the verdict", x3["verdicts"].get("fire_catches_verdict") == "FAIL"
      and "0.1.0" in x3["why"].get("fire_catches_verdict", ""), (x3["why"], W.load_reading(fast)))
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
