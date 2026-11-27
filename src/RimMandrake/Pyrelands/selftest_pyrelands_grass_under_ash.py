#!/usr/bin/env python3
"""sc_grass_seen_under_ash (bar grass_still_seen_under_ash): the scene's offline half decides what it claims.

  1. the pure parts of grass_under_ash_live.py: the window scan stays off the map edge, G and B are disjoint with B's
     cleared border off G, the firebreak ring holds both; grown_cells reads "Mature." only; the regimes' bands; the
     opportunity holds on a valid pair and each of its nine checks goes NOT on its own planted break; error_lines.
  2. grass_under_ash_judge.py: verdict PASS on the right reading and FAIL on each forbidden effect (wrong pick, grass
     hidden in G, grass drawn in B), unusable on a bad answer; prepare puts only A.png and B.png in the blind folder, the
     key outside it, and G lands on both letters over seeds.
  3. the shipped chain on a scripted game: both pairs valid on a good game; UNMEASURED on each planted scene fault
     (a fire in G, grass in B, an ash fall that banks nothing, a fall so fast the light band is overshot); the log check
     FAILs on a planted error line.
  4. the record: validation.py registers the chain, the test table's row names the bar, the chain and its command (scenes.json holds only tree leaves' scenes).

Run: python3 <this file>   exit 0 = every check PASS
"""
import importlib.util
import json
import os
import random
import re
import sys
import tempfile
import types

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


W = load("grass_under_ash_live", "grass_under_ash_live.py")
J = load("grass_under_ash_judge", "grass_under_ash_judge.py")
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "modcheck")]
import validation as V  # noqa: E402

# ---- 1. pure parts
wins = W.scan_windows((250, 250))
check("the scan reads windows", len(wins) > 100, len(wins))
check("every window keeps EDGE cells off the map edge", all(
    x >= W.EDGE and z >= W.EDGE and x + W.WINDOW_W <= 250 - W.EDGE and z + W.FRAME_H <= 250 - W.EDGE for x, z in wins))
check("pick_window takes the densest, ties to the lowest corner", W.pick_window([(5, 40, 40), (9, 60, 20), (9, 50, 30)]) == (50, 30))
check("pick_window with nothing counted is None", W.pick_window([]) is None)
g, b, border, ring = W.frames_of(40, 60)
gc, bc, borc, ringc = (set(W.cells_of(r)) for r in (g, b, border, ring))
check("G and B are the frame size", len(gc) == len(bc) == W.FRAME_W * W.FRAME_H)
check("B's cleared border holds B and no cell of G", bc <= borc and not (gc & borc), (len(bc & borc), len(gc & borc)))
check("G's capture pad (1 cell) does not reach B", not (set(W.cells_of((g[0] - 1, g[1] - 1, g[2] + 2, g[3] + 2))) & bc))
check("the firebreak's inner rect holds both frames", gc <= ringc and bc <= ringc)
rows = [{"defName": W.GRASS, "x": 1, "z": 1, "inspect": ["Mature."]},
        {"defName": W.GRASS, "x": 2, "z": 1, "inspect": ["70% grown"]},
        {"defName": "RM_FE_Plant_Quickgrass", "x": 3, "z": 1, "inspect": ["Mature."]},
        {"defName": W.GRASS, "x": 4, "z": 1, "inspect": []}]
check("grown_cells: only mature ember grass", W.grown_cells(rows, V.plant_growth_of_lines) == {(1, 1)},
      W.grown_cells(rows, V.plant_growth_of_lines))
for reg, d, want in (("light", 0.079, False), ("light", 0.08, True), ("light", 0.399, True), ("light", 0.40, False),
                     ("deep", 0.499, False), ("deep", 0.50, True), ("deep", None, False)):
    check("regime_ok(%s, %r) is %r" % (reg, d, want), W.regime_ok(reg, d) is want)


def frame(rect, depth, grown=None, plants=0, fires=()):
    return W.frame_read(rect, dict((c, depth) for c in W.cells_of(rect)), grown or set(), plants, list(fires))


good = (frame(g, 0.15, set(W.cells_of(g)), plants=96), frame(b, 0.15))
ok, why, rows = W.opportunity("light", good[0], good[1], "Clear", 4000)
check("a valid light pair holds every opportunity check", ok is True and all(r["ok"] for r in rows), why)
check("each opportunity line prints worst, limit and cases", all(set(r) >= {"worst", "limit", "cases"} for r in rows))
half = set(W.cells_of(g)[:48])
breaks = {
    "G grown ember grass share": dict(g=frame(g, 0.15, half, plants=48)),
    "G cells with ash": dict(g=frame(g, 0.0, set(W.cells_of(g)), plants=96)),
    "G median depth in the light regime": dict(g=frame(g, 0.45, set(W.cells_of(g)), plants=96)),
    "B plants": dict(b=frame(b, 0.15, plants=3)),
    "B cells with ash": dict(b=frame(b, 0.0)),
    "B median depth in the light regime": dict(b=frame(b, 0.05)),
    "fires in either frame": dict(g=frame(g, 0.15, set(W.cells_of(g)), plants=96, fires=[(g[0], g[1])])),
    "weather at the captures": dict(weather="RM_FE_Weather_AshFall"),
    "ticks of clear before the captures": dict(age=600),
}
for name, kw in breaks.items():
    ok, why, rows = W.opportunity("light", kw.get("g", good[0]), kw.get("b", good[1]), kw.get("weather", "Clear"),
                                  kw.get("age", 4000))
    bad = [r["check"] for r in rows if not r["ok"]]
    check("planted break %r: the opportunity fails on it" % name, ok is False and name in bad, (ok, bad))
ok, why, _r = W.opportunity("deep", frame(g, 0.55, set(W.cells_of(g)), plants=96), frame(b, 0.52), "Clear", 4100)
check("a valid deep pair holds", ok is True, why)
check("error_lines keeps error and exception lines only",
      W.error_lines([{"type": "Error", "text": "e"}, {"type": "Warning", "text": "w"}, {"level": "exception", "text": "x"}])
      == ["e", "x"])

# ---- 2. the judge's half
for gl in "AB":
    bl = "B" if gl == "A" else "A"
    right = {"grass_image": gl, "%s_grass" % gl: True, "%s_grass" % bl: False}
    check("verdict PASS on the right reading (G=%s)" % gl, J.verdict(right, gl)[0] is True)
    for fault, ans in (("wrong pick", dict(right, grass_image=bl)), ("grass hidden in G", dict(right, **{"%s_grass" % gl: False})),
                       ("grass drawn in B", dict(right, **{"%s_grass" % bl: True})), ("neither", dict(right, grass_image="neither"))):
        check("verdict FAILs on %s (G=%s)" % (fault, gl), J.verdict(ans, gl)[0] is False, J.verdict(ans, gl))
check("verdict is unusable on a bad answer", J.verdict({"pick": "A"}, "A")[0] is None)
tmp = tempfile.mkdtemp(prefix="gsua_selftest_")
for nm in ("g.png", "b.png"):
    with open(os.path.join(tmp, nm), "wb") as f:
        f.write(nm.encode())
man = os.path.join(tmp, "manifest.json")
with open(man, "w") as f:
    json.dump({"pairs": [{"regime": "light", "shotG": os.path.join(tmp, "g.png"), "shotB": os.path.join(tmp, "b.png"),
                          "valid": True}]}, f)
letters = set()
for seed in range(8):
    J.prepare(man, rng=random.Random(seed))
    key = json.load(open(os.path.join(tmp, "key_light.json")))
    letters.add(key["G"])
    blind = os.path.join(tmp, "blind_light")
    check("the blind folder holds only A.png and B.png", sorted(os.listdir(blind)) == ["A.png", "B.png"], os.listdir(blind))
    check("G's capture is the keyed letter", open(os.path.join(blind, key["G"] + ".png"), "rb").read() == b"g.png")
check("G lands on both letters over seeds", letters == {"A", "B"}, letters)
ans = os.path.join(tmp, "ans.json")
json.dump({"grass_image": key["G"], "A_grass": key["G"] == "A", "B_grass": key["G"] == "B"}, open(ans, "w"))
check("score exits 0 on the right reading", J.score(man, "light", ans) == 0)
json.dump({"grass_image": "neither", "A_grass": False, "B_grass": False}, open(ans, "w"))
check("score exits 1 when the judge sees no grass (the 2026-11-16 defect)", J.score(man, "light", ans) == 1)


# ---- 3. the shipped chain on a scripted game
class Game(object):
    """Ember grass everywhere it is planted, a SandGrid that banks `rate` a cell per hour of ash fall, a clock."""

    def __init__(self, rate=0.06):
        self.rate, self.tick, self.weather, self.depth, self.grass, self.fires, self.log = rate, 0, "Clear", {}, {}, set(), []
        self.hour = 3.0

    def ash(self, rect):
        if rect == "all":
            cells = [(x, z) for x in range(250) for z in range(250)]
        else:
            x, z, w, h = (int(v) for v in rect.split(","))
            cells = W.cells_of((x, z, w, h))
        ds = [self.depth.get(c, 0.0) for c in cells]
        return {"cells": len(cells), "ashed": sum(1 for d in ds if d >= 0.03), "depthSum": sum(ds), "weather": self.weather}

    def advance(self, n):
        if self.weather == V.ASHFALL:
            for c in list(self.depth) + [c for c in self.grass]:
                pass
            for x in range(30, 90):
                for z in range(20, 40):
                    self.depth[(x, z)] = self.depth.get((x, z), 0.0) + self.rate * n / 2500.0
        self.tick += n
        self.hour = (self.hour + n / 2500.0) % 24


def in_rect(c, rect):
    x, z, w, h = rect
    return x <= c[0] < x + w and z <= c[1] < z + h


def parse_rect(s):
    return tuple(int(v) for v in s.split(","))


def run(game, env=None):
    out = {"verdicts": {}, "notes": [], "shots": []}

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
                out.setdefault("why", {})[self.name] = ev.args[1]
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
            elif tool == "jawa/set_plants":
                for op in p["ops"].split(";"):
                    what, _, r = op.partition(":")
                    rect = parse_rect(r)
                    if what == "CLEAR":
                        game.grass = dict((c, v) for c, v in game.grass.items() if not in_rect(c, rect))
            elif tool == "jawa/inspect_string":
                rect = parse_rect(p["rect"])
                return {"things": [{"defName": W.GRASS, "x": c[0], "z": c[1], "inspect": ["Mature."]}
                                   for c in game.grass if in_rect(c, rect)]}
            elif tool == "jawa/list_things" and p.get("group") == "Plant":
                rect = parse_rect(p["rect"])
                return {"countMatched": sum(1 for c in game.grass if in_rect(c, rect))}
            elif tool == "jawa/map_fire" and p.get("action") == "start":
                game.fires |= set(W.cells_of(parse_rect(p["rect"])))
            elif tool == "jawa/static_call" and p.get("method") == "ClearAsh":
                game.depth = {}
            return {"success": True}

    def plants(t, what, rect, growth=1.0):
        for c in W.cells_of(rect):
            game.grass[c] = growth

    def count(t, d, rect=None):
        x, z, w, h = parse_rect(rect)
        return 150 if (x, z) == (34, 20) else 60       # the carpet's densest window

    def noon(t, lo=10, hi=14):
        if not lo <= game.hour < hi:
            game.advance(int(((lo + 0.5 - game.hour) % 24) * 2500))
        return game.hour

    def stop(v):
        def f(*a):
            raise Stop(v, a[-1])
        return f

    def shot(t, rect, name):
        out["shots"].append((name, tuple(rect)))
        return "D:\\fake\\%s.png" % name

    def things(t, d, rect=None, limit=0):
        r = parse_rect(rect)
        return [{"x": c[0], "z": c[1]} for c in game.fires if in_rect(c, r)] if d == "Fire" else []

    chains = {}
    ns = types.SimpleNamespace(
        _teardown=lambda **k: (lambda fn: fn), _comp=lambda t, n, **k: Comp(n), _live=lambda t: True,
        _independent=lambda t: None, _load_registered_site=lambda t: (1, None), _on_site=lambda t: None,
        _note=lambda t, n, v: out["notes"].append((n, v)), _wait=lambda t, n: game.advance(n),
        _extinguish=lambda t: game.fires.clear(), _ash=lambda t, r=None: game.ash(r or "all"), _count=count,
        _map_size=lambda t: (250, 250), _firebreak=lambda t, r, width=4: None, _plants=plants, _things=things,
        fire_cells=V.fire_cells, plant_growth_of_lines=V.plant_growth_of_lines, _ten_noon_hour=noon, _r6_shot=shot,
        _rs=V._rs, _log_mark=lambda t: "m", _log_since=lambda t, m: game.log, _unmeasured=stop("UNMEASURED"),
        _fail=stop("FAIL"), _GEN={}, ASHFALL=V.ASHFALL, ASH_SAND=V.ASH_SAND)
    W.register(types.SimpleNamespace(chain=lambda n: (lambda fn: chains.setdefault(n, fn))), ns)
    keep = dict((k, os.environ.get(k)) for k in (W.PLANT_ENV, W.OUT_ENV))
    for k in keep:
        os.environ.pop(k, None)
    os.environ[W.OUT_ENV] = tempfile.mkdtemp(prefix="gsua_chain_")
    os.environ.update(env or {})
    try:
        chains["grass_seen_under_ash"](T())
    finally:
        for k in keep:
            os.environ.pop(k, None)
            if keep[k] is not None:
                os.environ[k] = keep[k]
    out["manifest"] = os.path.join(os.environ.get(W.OUT_ENV) or keep.get(W.OUT_ENV) or "", "manifest.json")
    return out


COMPS = ("grass_under_ash_stage", "grass_under_ash_light_pair", "grass_under_ash_deep_pair", "grass_under_ash_no_error_line")
x = run(Game())
check("the chain on a good game: every component PASS", all(x["verdicts"].get(c) == "PASS" for c in COMPS), x["verdicts"])
check("the chain takes one capture of each frame per pair", [s[0] for s in x["shots"]] ==
      ["gsua_light_G", "gsua_light_B", "gsua_deep_G", "gsua_deep_B"], x["shots"])
check("the captures frame the picked window", x["shots"] and x["shots"][0][1] == (34, 20, W.FRAME_W, W.FRAME_H), x["shots"][:1])
for plant, comp in (("fire_in_g", "grass_under_ash_light_pair"), ("grass_in_b", "grass_under_ash_light_pair")):
    y = run(Game(), {W.PLANT_ENV: plant})
    check("planted %s: the %s is UNMEASURED" % (plant, comp), y["verdicts"].get(comp) == "UNMEASURED", y["verdicts"])
y = run(Game(rate=0.0))
check("an ash fall that banks nothing: both pairs UNMEASURED", y["verdicts"].get("grass_under_ash_light_pair") == "UNMEASURED"
      and y["verdicts"].get("grass_under_ash_deep_pair") == "UNMEASURED", y["verdicts"])
y = run(Game(rate=0.5))
check("a fall that overshoots the light band: the light pair UNMEASURED, the deep pair valid",
      y["verdicts"].get("grass_under_ash_light_pair") == "UNMEASURED"
      and y["verdicts"].get("grass_under_ash_deep_pair") == "PASS", y["verdicts"])
gm = Game()
gm.log = [{"type": "Error", "text": "planted"}]
y = run(gm)
check("a new error line FAILs the log component", y["verdicts"].get("grass_under_ash_no_error_line") == "FAIL", y["verdicts"])

# ---- 4. the record
check("validation.py registers grass_seen_under_ash", any(
    getattr(k, "name", None) == "grass_seen_under_ash" or k == "grass_seen_under_ash"
    or (isinstance(k, tuple) and k[0] == "grass_seen_under_ash") for k in V.suite.chains))
# scenes.json lists the 0.1.0 tree's scenes: designer_stage's scene gate refuses a requirement that is not a tree leaf, and
# grass_still_seen_under_ash is a 0.2.0 bar (VERSION.json bars_new). The test table's row is this check's record.
check("scenes.json does not carry sc_grass_seen_under_ash (its bar is no tree leaf)", "sc_grass_seen_under_ash" not in
      [s.get("id") for s in json.load(open(os.path.join(CONCEPT, "scenes.json"), encoding="utf-8"))["scenes"]], None)
tt = json.load(open(os.path.join(CONCEPT, "version", "test_table.json"), encoding="utf-8"))
row = (tt["tests"].get("sc_grass_seen_under_ash") or {}) if isinstance(tt.get("tests"), dict) else {}
check("the table's row is the bar's and its entry is the registered chain", row.get("for_bar") == "grass_still_seen_under_ash"
      and row.get("entry") == "grass_seen_under_ash" and str(row.get("file", "")).endswith("Pyrelands/validation.py"),
      {k: row.get(k) for k in ("for_bar", "file", "entry")})
cmd = str((tt["tests"].get("sc_grass_seen_under_ash") or {}).get("command") if isinstance(tt.get("tests"), dict) else "")
check("the table's command names the chain", re.search(r"--chains grass_seen_under_ash\b", cmd) is not None, cmd)

print("%s: %d checks, %d failed" % (os.path.basename(__file__), N["run"], N["bad"]))
sys.exit(1 if N["bad"] else 0)
