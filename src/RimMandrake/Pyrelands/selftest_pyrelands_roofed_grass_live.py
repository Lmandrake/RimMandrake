#!/usr/bin/env python3
"""Offline test of roofed_grass_live.py (sc_roofed_grass_declines, bar roofed_grass_declines_visibly). No game.

  1. the pure helpers: the shipped numbers read from the defs, the keyed lines, the geometry (rings, door, lamps, gap, all
     inside the cleared rect), the phases' clock (the cut ends before any dead grass can crumble).
  2. a Monte Carlo of the patch over a Python twin of RM_RoofWitherKernel (consecutive ids as one set_plants batch gives,
     and random ids; random long-tick phases): the worst hourly share and the narrowest death window at A's size and at
     MIN_PATCH, each printed with its limit and its cases.
  3. the chain itself, run against a fake game that ticks the same twin (each plant's long tick at its own phase, the map's
     kill one tick after the lethal step, remains on the cell, dead grass crumbling on its own clock, a colonist's cuts):
     the clean game reads PASS in every component, and each planted fault turns its own component red.
  4. the record: validation.py registers the chain; the test table's row names the bar, the chain and its command.
The twin is the C# kernel's rule rewritten (Source/Kernel/RM_RoofWitherKernel.cs); T_ROOF_WITHER_OFFLINE tests the C# itself.
"""
import importlib.util
import json
import math
import os
import random
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(ROOT, "design", "concepts", "Pyrelands")
N = {"run": 0, "bad": 0}


def check(name, ok, detail=""):
    N["run"] += 1
    if not ok:
        N["bad"] += 1
        print("FAIL  %s -- %s" % (name, str(detail)[:400]))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "modcheck")]
import validation as V  # noqa: E402

R = load("roofed_grass_live", "roofed_grass_live.py")
L = R.LONG
M32 = 0xFFFFFFFF


# ---- the kernel's twin (RM_RoofWitherKernel.cs)
def spread_u(i, x, z):
    h = (i * 0x9E3779B1) & M32
    h ^= (x * 0x85EBCA77 + 0x27D4EB2F) & M32
    h = ((h << 13) | (h >> 19)) & M32
    h ^= (z * 0xC2B2AE3D + 0x165667B1) & M32
    h ^= h >> 16
    h = (h * 0x7FEB352D) & M32
    h ^= h >> 15
    h = (h * 0x846CA68B) & M32
    h ^= h >> 16
    return h / 4294967296.0


def death_ticks(i, x, z, w):
    w = max(w, L)
    return max(L, int(round(w * (R.SPREAD_LO + (R.SPREAD_HI - R.SPREAD_LO) * spread_u(i, x, z)))))


def damage_due(mx, t, d):
    if t <= 0 or mx <= 0:
        return 0
    if t >= d:
        return mx
    return min(mx - 1, max(1, (mx * t + d - 1) // d))


def stage(t, d):
    if t <= 0:
        return 0
    if t >= d:
        return 3
    return 1 if t < 0.5 * d else 2


# ---- 1. the pure helpers
nums = R.shipped_numbers()
ember = open(R.EMBER_XML, encoding="utf-8").read()
check("witherTicks: the def sets none, so the class default (60000) is the shipped number",
      nums["witherTicks"] == 60000 and "<witherTicks>" not in ember, nums)
check("crumbleTicks read from DeadGrass.xml (120000)", nums["crumbleTicks"] == 120000
      and nums["sources"]["crumbleTicks"] == "DeadGrass.xml", nums)
check("the grass's remains are the dead grass", nums["remainsDef"] == R.DEAD and nums["grassHp"] == 28, nums)
fake_def = os.path.join(os.environ.get("TMPDIR", "/tmp"), "rgd_ember_planted.xml")
with open(fake_def, "w", encoding="utf-8") as f:
    f.write(ember.replace("<remainsDef>", "<witherTicks>12345</witherTicks><remainsDef>", 1))
check("planted: a def's witherTicks wins over the class default", R.shipped_numbers(ember=fake_def)["witherTicks"] == 12345)
os.remove(fake_def)
keyed = R.keyed_lines()
check("the two keyed lines read", all(keyed) and keyed[0] != keyed[1], keyed)
check("stage_of_lines", (R.stage_of_lines([keyed[1]], keyed), R.stage_of_lines(["x", keyed[0]], keyed),
                         R.stage_of_lines(["Growth 100%"], keyed), R.stage_of_lines(None, keyed)) == (2, 1, 0, 0))
g = R.geometry(V.R6_PAD_WITHER)
a_cells, b_cells = set(R.cells_of(g["A"])), set(R.cells_of(g["B"]))
walls = set(g["ringA"]) | set(g["ringB"]) | {g["door"]}
sx, sz, sw, sh = g["scene"]
in_scene = lambda c: sx <= c[0] < sx + sw and sz <= c[1] < sz + sh  # noqa: E731
check("geometry: A 12x16 and B 5x5, disjoint, walls off both", len(a_cells) == 192 and len(b_cells) == 25
      and not (a_cells & b_cells) and not (walls & (a_cells | b_cells)), g["A"])
check("geometry: the door is in A's west ring, lamps and subject inside A, the subject on no lamp",
      g["door"][0] == g["A"][0] - 1 and g["A"][1] <= g["door"][1] < g["A"][1] + R.A_H
      and set(g["lamps"]) <= a_cells and g["subject"] in a_cells and g["subject"] not in g["lamps"]
      and len(g["plantCells"]) == 188)
check("geometry: the gap between the rings is %d cells" % R.GAP, g["B"][0] - 1 - (g["A"][0] + R.A_W) - 1 == R.GAP)
check("geometry: every A cell within 6 of a wall (roof support 6.9)", max(min(c[0] - g["A"][0] + 1, g["A"][0] + R.A_W - c[0],
                                                                         c[1] - g["A"][1] + 1, g["A"][1] + R.A_H - c[1])
                                                                     for c in a_cells) <= 6)
check("geometry: everything (walls, spawn, exit) inside the cleared rect; spawn and exit outside A's ring",
      all(in_scene(c) for c in walls | a_cells | b_cells | {g["spawn"], g["exit"]})
      and g["spawn"][0] < g["door"][0] and g["exit"][0] < g["door"][0])
pl = R.plan(nums["witherTicks"], nums["crumbleTicks"])
print("[rgd-st] plan: %r" % pl)
check("plan: the cut ends before the earliest crumble", pl["cutBeforeCrumble"] and pl["cutEnd"] < pl["earliestCrumble"], pl)
check("plan: the wither reads reach past the death deadline", pl["witherReads"] * R.HOUR >= pl["deathDeadline"], pl)
check("plan: the crumble reads reach past the crumble deadline from the latest possible start",
      pl["cutEnd"] + pl["crumbleReads"] * R.CRUMBLE_READ >= pl["deathDeadline"] + R.HOUR + pl["crumbleSpan"], pl)
check("planted: a crumbleTicks too short for the cut is refused", not R.plan(60000, 20000)["cutBeforeCrumble"])
check("percentile nearest-rank", R.percentile([1, 2, 3, 4, 5], 0.5) == 3 and R.percentile([], 0.5) is None)
check("lit_share", R.lit_share({"cells": [{"x": 1, "z": 1, "groundGlow": 0.5}, {"x": 2, "z": 1, "groundGlow": 0.1}]},
                               [(1, 1), (2, 1), (3, 1)]) == 1 / 3.0)
check("error_lines", R.error_lines([{"type": "Error", "text": "x"}, {"level": "warning", "text": "y"}]) == ["x"])


# ---- 2. the Monte Carlo: the hourly share and the window of a patch roofed at once
def patch_deaths(n, rng, consecutive):
    base = rng.randrange(1000, 10 ** 6)
    cells = [(80 + k % 12, 117 + k // 12) for k in range(n)]
    out = []
    for k, (x, z) in enumerate(cells):
        i = base + k if consecutive else rng.randrange(1, 2 ** 31 - 1)
        d = death_ticks(i, x, z, nums["witherTicks"])
        q = rng.randint(1, L)                      # the first roofed long tick
        # the k-th roofed long tick (k >= 1) at q + (k - 1) L carries roofedTicks k L; lethal at the first k L >= d
        kk = int(math.ceil(d / float(L)))
        out.append(q + (kk - 1) * L + 1)           # + 1: the map's kill on the next tick
    return out


def hourly(deaths, n):
    reads = {}
    for t in deaths:
        h = int(math.ceil(t / float(R.HOUR)))
        reads[h] = reads.get(h, 0) + 1
    ts = sorted(int(math.ceil(t / float(R.HOUR))) * R.HOUR for t in deaths)
    return max(reads.values()) / float(n), R.percentile(ts, 0.95) - R.percentile(ts, 0.05)


rng = random.Random(20261127)
for n in (187, R.MIN_PATCH):
    worst_share, worst_win, cases = 0.0, 10 ** 9, 0
    for trial in range(400):
        for consec in (True, False):
            s, w = hourly(patch_deaths(n, rng, consec), n)
            worst_share, worst_win, cases = max(worst_share, s), min(worst_win, w), cases + 1
    print("[rgd-st] MC patch %d: worst hourly share=%.3f limit<=%.2f; narrowest window=%d limit>=%d; cases=%d"
          % (n, worst_share, R.SHARE_MAX, worst_win, R.WINDOW_MIN_TICKS, cases))
    check("MC patch %d: worst hourly share within SHARE_MAX" % n, worst_share <= R.SHARE_MAX, worst_share)
    check("MC patch %d: narrowest window at least WINDOW_MIN_TICKS" % n, worst_win >= R.WINDOW_MIN_TICKS, worst_win)
smallest = None
for n in range(R.MIN_PATCH, 40, -1):
    if any(hourly(patch_deaths(n, rng, c), n)[0] > R.SHARE_MAX for _ in range(200) for c in (True, False)):
        smallest = n + 1
        break
print("[rgd-st] MC: the smallest patch with no hourly share over %.2f in 400 trials each: %s (MIN_PATCH %d)"
      % (R.SHARE_MAX, smallest, R.MIN_PATCH))
check("MIN_PATCH sits at or above the MC's smallest safe patch", smallest is not None and R.MIN_PATCH >= smallest, smallest)
pd = patch_deaths(187, random.Random(1), True)
check("twin: no death before the plan's earliest, none past its deadline", min(pd) > pl["earliestDeath"]
      and max(pd) <= pl["deathDeadline"], (min(pd), max(pd)))


# ---- 3. the chain against a fake game
class Stop(Exception):
    pass


class Game(object):
    """Ticks the twin. fault: one of FAULTS (each spoils one promise)."""

    def __init__(self, fault=None, seed=7):
        self.fault, self.rng = fault, random.Random(seed)
        self.clock, self.next_id = 500000, 40000
        self.things, self.roof, self.kills, self.cut_orders, self.notes = {}, set(), [], [], []
        self.calibrated, self.shot_rects = False, []
        self.walls, self.doors, self.noroof, self.walls_at = set(), set(), set(), None

    def spawn(self, d, x, z, hp=None):
        self.next_id += 1
        mx = 28 if d == R.GRASS else (20 if d == R.DEAD else 100)
        self.things[self.next_id] = {"def": d, "x": x, "z": z, "hp": hp or mx, "mx": mx, "phase": self.rng.randrange(L),
                                     "rt": 0, "dealt": 0, "look": 0, "age": 0}
        return self.next_id

    def tid(self, i):
        return "%s%d" % (self.things[i]["def"], i)

    def num(self, s):
        return int(re.search(r"(\d+)$", str(s)).group(1))

    def in_rect(self, th, rect):
        x, z, w, h = (int(v) for v in str(rect).split(","))
        return x <= th["x"] < x + w and z <= th["z"] < z + h

    def long_tick(self, i):
        th = self.things[i]
        if th["def"] == R.GRASS:
            w = nums["witherTicks"]
            d = death_ticks(i, th["x"], th["z"], w)
            if self.fault == "one_clock":
                d = w
            if (th["x"], th["z"]) not in self.roof:
                th["rt"] = max(0, th["rt"] - L)
                th["look"] = stage(th["rt"], d) if th["rt"] else 0
                return
            th["rt"] += L
            due = damage_due(th["mx"], th["rt"], d)
            owed = max(0, due - th["dealt"])
            th["dealt"] = max(th["dealt"], due)
            if due >= th["mx"] or (owed > 0 and owed >= th["hp"] and self.fault != "subject_lives"):
                self.kills.append(i)
                return
            th["hp"] -= min(owed, th["hp"] - 1)
            th["look"] = stage(th["rt"], d)
        elif th["def"] == R.DEAD:
            c = nums["crumbleTicks"] // 10 if self.fault == "early_crumble" else nums["crumbleTicks"]
            th["age"] += L
            d = death_ticks(i, th["x"], th["z"], c)
            due = damage_due(th["mx"], th["age"], d)
            owed = max(0, due - th["dealt"])
            th["dealt"] = max(th["dealt"], due)
            if due >= th["mx"] or (owed > 0 and owed >= th["hp"]):
                del self.things[i]
                return
            th["hp"] -= owed

    def advance(self, n):
        for _ in range(int(n)):
            self.clock += 1
            for i in self.kills:
                th = self.things.pop(i, None)
                if th and self.fault != "no_remains":
                    self.spawn(R.DEAD, th["x"], th["z"])
            self.kills = []
            for i in [k for k, th in self.things.items() if (self.clock + th["phase"]) % L == 0]:
                if i in self.things and i not in self.kills:
                    self.long_tick(i)
        if self.walls and self.clock - self.walls_at >= AUTOROOF_TICKS:
            self.auto_roof()
        for i in self.cut_orders:
            if self.fault != "cut_fails":
                self.things.pop(i, None)
        self.cut_orders = []

    def auto_roof(self):
        # vanilla AutoBuildRoofAreaSetter (Verse, rw16 decompile): a room closed by player walls (a door closes it too) goes
        # into the build-roof area, cell by cell unless NoRoof; the colonists then build it (ArchSmall 2026-11-27: B's
        # doorless ring and its 16 inner edge cells roofed within 5000 ticks). The twin roofs every enclosed cell.
        xs, zs = [c[0] for c in self.walls], [c[1] for c in self.walls]
        x0, x1, z0, z1 = min(xs) - 1, max(xs) + 1, min(zs) - 1, max(zs) + 1
        shut = self.walls | self.doors
        out, todo = set(), [(x0, z0)]
        while todo:
            c = todo.pop()
            if c in out or c in shut or not (x0 <= c[0] <= x1 and z0 <= c[1] <= z1):
                continue
            out.add(c)
            todo.extend([(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)])
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if (x, z) not in out and (x, z) not in self.noroof:
                    self.roof.add((x, z))

    def lines(self, i):
        th = self.things[i]
        if th["def"] == R.DEAD:
            return ["Deteriorates in 1 day."]
        if th["def"] != R.GRASS or self.fault == "no_line":
            return []
        roofed = (th["x"], th["z"]) in self.roof
        look = th["look"]
        if self.fault == "stage_falls" and look == 2 and self.clock % 2 == 0:
            look = 1
        if self.fault == "b_wilts" and not roofed:
            return [keyed[0]]
        if look == 2:
            return [keyed[1]]
        return [keyed[0]] if look == 1 or roofed else []

    def call(self, tool, **kw):
        if tool == "jawa/list_things":
            rows = [(i, th) for i, th in sorted(self.things.items()) if th["def"] == kw.get("defName")
                    and (not kw.get("rect") or self.in_rect(th, kw["rect"]))]
            if self.fault == "hp_rises" and self.clock % 3 == 0:
                for i, th in rows:
                    if th["def"] == R.GRASS and th["hp"] < th["mx"]:
                        th["hp"] += 1
            return {"countMatched": len(rows), "scanned": len(self.things) + 1,
                    "things": [{"id": self.tid(i), "x": th["x"], "z": th["z"], "hitPoints": th["hp"]}
                               for i, th in rows[:kw.get("limit", 500)]]}
        if tool == "jawa/inspect_string":
            return {"things": [{"id": self.tid(i), "defName": th["def"], "x": th["x"], "z": th["z"], "inspect": self.lines(i)}
                               for i, th in sorted(self.things.items()) if self.in_rect(th, kw["rect"])]}
        if tool == "jawa/set_roof_batch":
            d, _, rect = kw["ops"].partition(":")
            x, z, w, h = (int(v) for v in rect.split(","))
            for c in R.cells_of((x, z, w, h)):
                (self.roof.add if d == "RoofConstructed" else self.roof.discard)(c)
            return {}
        if tool == "jawa/get_roof_batch":
            x, z, w, h = (int(v) for v in kw["rects"].split(","))
            return {"ops": ";".join("%s:%d,%d,1,1" % ("RoofConstructed" if c in self.roof else "None", c[0], c[1])
                                    for c in R.cells_of((x, z, w, h)))}
        if tool == "jawa/build_batch":
            for op in kw["ops"].split(";"):
                d, _, xz = op.partition(":")
                (self.walls if d == "Wall" else self.doors).add(tuple(int(v) for v in xz.split(",")[:2]))
            self.walls_at = self.clock
            return {}
        if tool == "jawa/paint_area":
            for rect in kw["ops"].split(";"):
                cells = R.cells_of(tuple(int(v) for v in rect.split(",")))
                if kw["area"] == "noroof":
                    (self.noroof.update if kw.get("value", True) else self.noroof.difference_update)(cells)
            return {"success": True}
        if tool == "jawa/spawn_batch":
            for op in kw["ops"].split(";"):
                d, _, xz = op.partition(":")
                x, z = (int(v) for v in xz.split(",")[:2])
                self.spawn(d, x, z)
            return {}
        if tool == "jawa/set_plants":
            d, _, rect = kw["ops"].partition(":")
            taken = set((th["x"], th["z"]) for th in self.things.values())
            for c in R.cells_of(tuple(int(v) for v in rect.split(","))):
                if c not in taken:
                    self.spawn(d, c[0], c[1])
            return {"planted": 1}
        if tool == "jawa/damage":
            self.things[self.num(kw["thingId"])]["hp"] -= int(kw["amount"])
            return {}
        if tool == "jawa/destroy_batch":
            for i in [k for k, th in self.things.items() if th["def"] == R.GRASS and self.in_rect(th, kw["rects"])]:
                del self.things[i]
            return {}
        if tool == "jawa/glow_at":
            glow = 0.0 if self.fault == "dark" else 0.8
            return {"hour": 12, "cells": [{"x": c[0], "z": c[1], "groundGlow": glow}
                                          for c in R.cells_of(tuple(int(v) for v in kw["rect"].split(",")))]}
        if tool == "jawa/ordered_job":
            if kw.get("jobDef") == "CutPlant":
                self.cut_orders.append(self.num(kw["targetAId"]))
            return {"accepted": True}
        return {}


FAULTS = {"one_clock": "roofed_grass_withers_unevenly", "no_remains": "roofed_grass_withers_unevenly",
          "no_line": "roofed_grass_withers_unevenly", "stage_falls": "roofed_grass_withers_unevenly",
          "hp_rises": "roofed_grass_withers_unevenly", "b_wilts": "roofed_grass_withers_unevenly",
          "subject_lives": "roofed_grass_one_hp_dies_next_long_tick", "cut_fails": "dead_grass_can_be_cut",
          "early_crumble": "dead_grass_crumbles_unevenly", "dark": "roofed_grass_captures_lit",
          "error_line": "roofed_grass_no_error_line"}


AUTOROOF_TICKS = 2500   # measured, ArchSmall 2026-11-27: B unroofed at the 2500-tick read, 9 cells roofed at 5000, 16 at 7500
PROBE_FITS = 10   # the twin's screen, cells: under A's 12 x 16, so an unprobed first capture of A is refused (the live
#                   refusal was the smoke scene's 50 x 50; how small a screen can get is not measured, so the twin is strict)


def run(game, env=None):
    verdicts, calls = {}, []

    class Comp(object):
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, et, ev, tb):
            if et is None:
                verdicts[self.name] = "PASS"
                return True
            if et is Stop:
                verdicts[self.name] = ev.args[0]
                return True
            verdicts[self.name] = "CRASH %s: %s" % (et.__name__, ev)
            return True

    class Session(object):
        def _ticks(self):
            return game.clock

    class T(object):
        session, upstream_failed, anchor = Session(), False, None

        def bridge_call(self, tool, **kw):
            calls.append(tool)
            return game.call(tool, **kw)

        def spawn_pawn(self, kind, hostile=False, beyond=None):
            return "Colonist1"

        def screenshot(self, name=None, rect=None, ppc=None):
            # play_zoom.shoot's refusal: its first rect is probed at the zoom the last call left, and a rect over
            # PROBE_FITS cells does not fit there (ArchSmall 2026-11-27: the smoke scene's 50 x 50 sky refused)
            if not game.calibrated and max(rect[2], rect[3]) > PROBE_FITS:
                stop("UNMEASURED")("play-zoom calibration: rect %r does not fit the viewport" % (rect,))
            game.calibrated = True
            game.shot_rects.append(tuple(rect))
            return "/fake/%s.png" % name

    def stop(v):
        def f(*a):
            raise Stop(v, a[-1])
        return f

    def things(t, d, rect=None, limit=500):
        return list(game.call("jawa/list_things", defName=d, rect=rect, limit=limit)["things"])

    def pad(t, xz):
        t.anchor = xz

    ns = types.SimpleNamespace(
        _teardown=lambda **k: (lambda fn: fn), _comp=lambda t, n, **k: Comp(n), _live=lambda t: True,
        _independent=lambda t: None, _unmeasured=stop("UNMEASURED"), _fail=stop("FAIL"),
        _wait=lambda t, n, fast=None: game.advance(n), _note=lambda t, k, v: game.notes.append((k, v)),
        _load_registered_site=lambda t: (1, ""), _pad=pad, _rs=V._rs, _r6_ops_cells=V._r6_ops_cells,
        R6_PAD_WITHER=V.R6_PAD_WITHER, _ten_gate_on=lambda t: True, _extinguish=lambda t: None,
        _open_ground=lambda t, rect, margin=0, soil=None: None, _things=things,
        _count=lambda t, d, rect=None: game.call("jawa/list_things", defName=d, rect=rect)["countMatched"],
        _plants=lambda t, p, rect, growth=1.0: game.call("jawa/set_plants", ops="%s:%s" % (p, V._rs(rect))),
        _r6_shot=lambda t, rect, name: t.screenshot(name=name, rect=tuple(rect), ppc=V.R6_PLAY_PPC),
        R6_PLAY_PPC=V.R6_PLAY_PPC, _log_mark=lambda t: 0,
        _log_since=lambda t, m, limit=1000: ([{"type": "Error", "text": "planted"}] if game.fault == "error_line"
                                             else [{"type": "Message", "text": "ok"}]))
    chains = {}
    R.register(types.SimpleNamespace(chain=lambda n: (lambda fn: chains.setdefault(n, fn))), ns)
    saved = dict((k, os.environ.get(k)) for k in (R.PLANT_ENV, R.OUT_ENV))
    os.environ[R.OUT_ENV] = os.path.join(os.environ.get("TMPDIR", "/tmp"), "rgd_selftest")
    if env:
        os.environ[R.PLANT_ENV] = env
    else:
        os.environ.pop(R.PLANT_ENV, None)
    try:
        chains["roofed_grass_declines"](T())
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return verdicts, calls


clean, calls = run(Game())
print("[rgd-st] clean run: %r" % clean)
check("clean game: all seven components PASS", len(clean) == 7 and all(v == "PASS" for v in clean.values()), clean)
check("clean game: the chain read the roof, the inspect lines, the glow and ordered the cut",
      all(x in calls for x in ("jawa/get_roof_batch", "jawa/inspect_string", "jawa/glow_at", "jawa/ordered_job")))
for fault, comp in sorted(FAULTS.items()):
    v, _ = run(Game(fault))
    others = dict((k, x) for k, x in v.items() if k != comp and x != "PASS")
    print("[rgd-st] planted %s: %s=%s, other reds %r" % (fault, comp, v.get(comp), others))
    check("planted %s turns %s red (FAIL or UNMEASURED)" % (fault, comp), v.get(comp) in ("FAIL", "UNMEASURED"), v)
    check("planted %s: no component crashes" % fault, not any(str(x).startswith("CRASH") for x in v.values()), v)
gm = Game()
v, _ = run(gm)
print("[rgd-st] zoom probe: first capture rect %r (limit <= %d cells), %d captures" % (
    gm.shot_rects[0] if gm.shot_rects else None, PROBE_FITS, len(gm.shot_rects)))
check("the first capture is the small zoom probe at A's middle, A's captures follow it",
      gm.shot_rects and gm.shot_rects[0][2:] == (R.CAL_CELLS, R.CAL_CELLS) and len(gm.shot_rects) > 1
      and all(max(r[2:]) > PROBE_FITS for r in gm.shot_rects[1:]) and v.get("roofed_grass_stage") == "PASS", (gm.shot_rects, v))
real_cal = R.CAL_CELLS
R.CAL_CELLS = 0   # the planted fault: the pre-repair scene, A's capture first
try:
    v, _ = run(Game())
finally:
    R.CAL_CELLS = real_cal
print("[rgd-st] planted no zoom probe: stage %r" % v.get("roofed_grass_stage"))
check("planted no zoom probe: the stage reads UNMEASURED (the smoke scene's live reading)",
      v.get("roofed_grass_stage") == "UNMEASURED", v)
real_nr = R.NOROOF_B
R.NOROOF_B = False   # the planted fault: the pre-repair scene, B's ring left to the auto-roof
try:
    gm = Game()
    v, _ = run(gm)
finally:
    R.NOROOF_B = real_nr
print("[rgd-st] planted no no-roof area on B: withers_unevenly %r, B cells roofed %d" % (
    v.get("roofed_grass_withers_unevenly"), len([c for c in gm.roof if c in R.cells_of(R.geometry(V.R6_PAD_WITHER)["B"])])))
check("planted no no-roof area on B: the auto-roof roofs B and withers_unevenly reads UNMEASURED (the live reading)",
      v.get("roofed_grass_withers_unevenly") == "UNMEASURED", v)
gm = Game()
v, _ = run(gm)
nb = len([c for c in gm.roof if c in R.cells_of(R.geometry(V.R6_PAD_WITHER)["B"])])
print("[rgd-st] repaired: B cells roofed at the end %d (limit 0), B no-roof cells %d" % (nb, len(gm.noroof)))
check("repaired: the no-roof area keeps B unroofed through the auto-roof", nb == 0 and v.get("roofed_grass_withers_unevenly") == "PASS", v)
def tint_two_args(src):
    """Pure. The colorTwo argument of every GetColoredVersion call in RM_RoofWitherLook (CompWithersUnderRoof.cs)."""
    body = src[src.index("class RM_RoofWitherLook"):]
    body = body[:body.index("class RM_Plant_WithersUnderRoof")]
    out = []
    for m in re.finditer(r"GetColoredVersion\(", body):
        depth, i, args, cur = 1, m.end(), [], ""
        while depth:
            ch = body[i]
            depth += {"(": 1, ")": -1}.get(ch, 0)
            if ch == "," and depth == 1:
                args.append(cur.strip()); cur = ""
            elif depth:
                cur += ch
            i += 1
        args.append(cur.strip())
        out.append(args[2] if len(args) > 2 else "")
    two_vars = dict(re.findall(r"Color\s+(\w+)\s*=\s*([^;]+);", body))
    return [two_vars.get(x, x) for x in out]


# Verse.Graphic_Random.GetColoredVersion (rw16 decompile): newColorTwo != Color.white -> Log.ErrorOnce("Cannot use
# Graphic_Random.GetColoredVersion with a non-white colorTwo."), and the colorTwo is dropped. Ember grass is Graphic_Random
# (EmberGrass.xml), so a tinted colorTwo is a red error line on every save that roofs grass (ArchSmall 2026-11-27, the
# first wilting long tick of sc_roofed_grass_declines' planted run).
twos = tint_two_args(open(R.COMP_CS, encoding="utf-8").read())
bad = [x for x in twos if not ("Color.white" in x and "Graphic_Random" in x)]
print("[rgd-st] tint colorTwo args: %r; not white for a Graphic_Random: %d (limit 0) of %d calls" % (twos, len(bad), len(twos)))
check("the wither tint passes Color.white as colorTwo to a Graphic_Random (it logs an error otherwise)", twos and not bad, twos)
assert tint_two_args("class RM_RoofWitherLook { x = g.GetColoredVersion(g.Shader, g.color * t, g.colorTwo * t); } "
                     "class RM_Plant_WithersUnderRoof") == ["g.colorTwo * t"]
check("the probe rect lies at the middle of A", R.calibration_rect((81, 117, 12, 16)) == (84, 122, 6, 6))
v, _ = run(Game(), env="mass_kill")
print("[rgd-st] planted scene %s=mass_kill: %r" % (R.PLANT_ENV, v))
check("the live twin's planted mass_kill fails the wither", v.get("roofed_grass_withers_unevenly") == "FAIL", v)

# ---- 4. the record
check("validation.py registers roofed_grass_declines", any(
    k == "roofed_grass_declines" or (isinstance(k, tuple) and k[0] == "roofed_grass_declines") for k in V.suite.chains))
tt = json.load(open(os.path.join(CONCEPT, "version", "test_table.json"), encoding="utf-8"))
row = (tt["tests"].get("sc_roofed_grass_declines") or {}) if isinstance(tt.get("tests"), dict) else {}
check("the table's row is the bar's and its entry is the registered chain",
      row.get("for_bar") == "roofed_grass_declines_visibly" and row.get("entry") == "roofed_grass_declines"
      and str(row.get("file", "")).endswith("Pyrelands/validation.py"), {k: row.get(k) for k in ("for_bar", "file", "entry")})
check("the table's command names the chain", re.search(r"--chains roofed_grass_declines\b", str(row.get("command"))), row)

print("%s: %d checks, %d failed" % (os.path.basename(__file__), N["run"], N["bad"]))
sys.exit(1 if N["bad"] else 0)
