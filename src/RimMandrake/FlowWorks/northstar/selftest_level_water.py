#!/usr/bin/env python3
"""selftest_level_water.py -- the exact-level water reference (northstar/level_water.py) against the ruled numbers.

WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (plan P3). The scenes are S1-S6 of
design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json REDRAWN for level water (owner R3, 2026-10-17: "Redraw
scene S5 with level-water numbers"); the expected figures are the ones design/RimMandrake/flowworks_level_surface_2026-10-17.md
§1 worked by hand (36,000 = 2,000 x [9(h+2) + 10(h+0.5)] -> h = -5/19 m; 4,000 = 2,000 x [(h+2) + 10(h+0.5)] -> h = -5/11 m).
Then property families on random scenes: conservation to the decilitre every pulse, bounds, one surface per body once
still (the R9 bar's offline twin: under 1 cm, here under 1 mm), solve idempotence, a falling pond SPLITTING at a sill and
a rising one MERGING over it.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_level_water.py [--n N]
"""
from __future__ import annotations

import argparse
import copy
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_water as lw  # noqa: E402
import validation_v2 as v  # noqa: E402

U = lw.U
FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def oracle(w, h, sources=None, bodies=None, beds=None, sink_band=None, per=1):
    return v.PulseOracle(w, h, dict(sources or {}), bodies or {}, per=per, budget=True, sink_band=sink_band,
                         algo="fixed", level_exact=True, beds=beds)


def total(o):
    t = sum(o.W[c] for c in o.D if o.exc(c))
    for b in o.bodies.values():
        if not b["limitless"]:
            t += b.get("dl", int(round(b.get("stock", 0) * U)))
    return t


def m(dl):
    return dl * lw.M_PER_UNIT


def worst_gap(o):
    g = lw.oracle_gaps(o)
    return g[0][0] if g else 0.0


def run_still(o, cap=400):
    """Pulse until nothing changes and nothing flows (no source pays, no sink takes: a source feeding a sink is moving
    water, not still water) or `cap` pulses; returns pulses run."""
    def snap():
        return dict(o.W), {b: d.get("dl") for b, d in o.bodies.items()}, o.drained, o.credited
    for k in range(cap):
        before = snap()
        o.pulse()
        if snap() == before:
            return k + 1
    return cap


# ───────────────────────────── the solve itself ─────────────────────────────

def t_solve_basics():
    N = lw.Node
    # nine flat 2 m squares (D=4), 26 notches of water: 1.444 m everywhere (the S6 pond's numbers, as dug squares)
    nodes = [N("c", i, 4 * U if i < 6 else (2 * U if i == 6 else 0), D=4) for i in range(9)]   # live today: 6 full
    edges = {i: [(j, 4) for j in range(9) if j != i and (abs(j - i) == 3 or (j // 3 == i // 3 and abs(j - i) == 1))]
             for i in range(9)}
    new = lw.solve(nodes, edges)
    depths = sorted(set(round(m(x), 3) for x in new))
    check("solve: 26 notches over a flat 3x3, D=4 -> every square 1.444 m", depths == [1.444], str(depths))
    check("solve: ... to within 1 dL per square", max(new) - min(new) <= 1, str(new))
    check("solve: conserves", sum(new) == 26 * U)
    # a sill: two D=4 pits joined by a D=1 square; all water in pit A below the sill stays trapped
    nodes = [N("c", 0, 3 * U, D=4), N("c", 1, 0, D=1), N("c", 2, 0, D=4)]
    edges = {0: [(1, 1)], 1: [(0, 1), (2, 1)], 2: [(1, 1)]}
    new = lw.solve(nodes, edges)
    check("solve: water below a sill stays trapped (3 notches in a 4-deep pit)", new == [3 * U, 0, 0], str(new))
    nodes = [N("c", 0, 4 * U, D=4), N("c", 1, 0, D=1), N("c", 2, 0, D=4)]
    new = lw.solve(nodes, edges)
    check("solve: a brim-full pit spills its top 0.5 m over a 0.5 m sill into the dry pit (it stood above the sill floor)",
          new == [3 * U, 0, U], str(new))
    nodes = [N("c", 0, 4 * U, D=4), N("c", 1, U // 2, D=1), N("c", 2, 0, D=4)]
    new = lw.solve(nodes, edges)
    check("solve: ... and the water on the sill goes the same way: both pits end level below the sill floor",
          new == [3 * U, 0, 3 * U // 2], str(new))
    # pond + canal: the S5-A numbers straight from the solve
    h = lw.histogram([4] * 9)
    nodes = [N("c", i, 0, D=1) for i in range(10)] + [N("p", 100, 36 * U, H=h)]
    edges = {i: [] for i in range(11)}
    for i in range(9):
        edges[i].append((i + 1, 1))
        edges[i + 1].append((i, 1))
    edges[0].append((10, 1))
    edges[10].append((0, 1))
    new = lw.solve(nodes, edges)
    canal = [round(m(x), 3) for x in new[:10]]
    surf = lw.pond_surface_height(h, new[10])
    check("solve: full 3x3 2 m pond + ten 0.5 m squares -> every canal square 0.237 m",
          canal == [0.237] * 10, str(canal))
    check("solve: ... and the pond's surface 0.263 m below ground (1.737 m deep)",
          abs(m(surf) + 5.0 / 19) < 1e-4, "%.5f" % m(surf))
    # idempotence: a solved state re-solves to itself
    for seed in range(300):
        r = random.Random(seed)
        n = r.randint(1, 12)
        nodes = [N("c", i, 0, D=r.randint(1, 4)) for i in range(n)]
        for nd in nodes:
            nd.water = r.randint(0, nd.D * U)
        edges = {}
        for i in range(n):
            for j in range(i + 1, n):
                if r.random() < 0.3:
                    cap = min(nodes[i].D, nodes[j].D)
                    edges.setdefault(i, []).append((j, cap))
                    edges.setdefault(j, []).append((i, cap))
        a = lw.solve(nodes, edges)
        for nd, x in zip(nodes, a):
            nd.water = x
        b = lw.solve(nodes, edges)
        if a != b:
            check("solve: idempotent on random graphs", False, "seed %d %s -> %s" % (seed, a, b))
            return
        if any(x < 0 or x > nd.D * U for nd, x in zip(nodes, a)):
            check("solve: bounds on random graphs", False, "seed %d %s" % (seed, a))
            return
    check("solve: idempotent and in bounds on 300 random graphs", True)


# ───────────────────────────── the scenes, redrawn for level water ─────────────────────────────

def row(x0, z, n):
    return [(x0 + i, z) for i in range(n)]


def s1():
    """S1: a limitless lake, an 8-square 0.5 m canal dug dry: full end to end by pulse 10; the wet run unbroken from the
    mouth at every pulse; a wet square never dries."""
    lake = {(x, z): 0 for x in range(0, 8) for z in range(0, 3)}
    o = oracle(20, 3, lake, {0: {"limitless": True, "stock": 0.0}})
    canal = row(8, 1, 8)
    for c in canal:
        o.dig(c, 1)
    unbroken, never_dry, full_by = True, True, None
    wet_seen = set()
    for p in range(1, 31):
        o.pulse()
        wet = [o.W[c] > 0 for c in canal]
        k = wet.index(False) if False in wet else len(wet)
        if any(wet[k:]):
            unbroken = False
        if any(c in wet_seen and o.W[c] == 0 for c in canal):
            never_dry = False
        wet_seen |= {c for c in canal if o.W[c] > 0}
        if full_by is None and all(o.W[c] == U for c in canal):
            full_by = p
    check("S1.a all 8 canal squares hold 0.5 m by pulse 10", full_by is not None and full_by <= 10, "full at %s" % full_by)
    check("S1.b the wet run is unbroken from the mouth at every pulse", unbroken)
    check("S1.c a wet canal square never goes dry", never_dry)


def s2():
    lake = {(x, z): 0 for x in range(0, 8) for z in range(0, 4)}
    o = oracle(20, 4, lake, {0: {"limitless": True, "stock": 0.0}})
    pond = [(8, 1), (9, 1), (8, 2), (9, 2)]
    trench = row(10, 2, 6)
    for c in pond:
        o.dig(c, 4)
    for c in trench:
        o.dig(c, 1)
    for _ in range(30):
        o.pulse()
    check("S2.a all 4 dug pond squares hold 2 m by pulse 30", all(o.W[c] == 4 * U for c in pond), str([o.W[c] for c in pond]))
    check("S2.b all 6 trench squares hold 0.5 m by pulse 30", all(o.W[c] == U for c in trench), str([o.W[c] for c in trench]))
    snap = dict(o.W)
    for _ in range(30):
        o.pulse()
    check("S2.d settled: nothing changes for the next 30 pulses", snap == o.W)


def s4():
    lake = {(x, z): 0 for x in range(0, 8) for z in range(0, 3)}
    o = oracle(20, 3, lake, {0: {"limitless": True, "stock": 0.0}})
    canal = row(8, 1, 8)
    for c in canal:
        o.dig(c, 1)
    gate = canal[3]
    o.sealed = {gate}
    for _ in range(20):
        o.pulse()
    up, down = canal[:3], canal[4:]
    check("S4.a/b shut: the 3 upstream squares hold 0.5 m, the 4 downstream stay dry",
          all(o.W[c] == U for c in up) and all(o.W[c] == 0 for c in down + [gate]))
    o.sealed = set()
    for _ in range(20):
        o.pulse()
    check("S4.c opened: all downstream squares hold 0.5 m", all(o.W[c] == U for c in down))
    o.sealed = {gate}
    for _ in range(40):
        o.pulse()
    check("S4.d shut again: the upstream squares stay full", all(o.W[c] == U for c in up))


def s5_pond(n_pond, stock_levels, canal_len=10, canal_d=1):
    """A 3x3 (or 1-square) enclosed 2 m pond and a dry canal dug off its east side, by gravity, settled."""
    if n_pond == 9:
        src = {(x, z): 0 for x in (1, 2, 3) for z in (1, 2, 3)}
        mouth_z = 2
    else:
        src = {(1, 2): 0}
        mouth_z = 2
    beds = {c: 4 for c in src}
    o = oracle(20, 5, src, {0: {"limitless": False, "stock": float(stock_levels)}}, beds=beds)
    x0 = max(x for x, _ in src) + 1
    canal = row(x0, mouth_z, canal_len)
    for c in canal:
        o.dig(c, canal_d)
    t0 = total(o)
    ok_cons = True
    for _ in range(200):
        o.pulse()
        if total(o) != t0:
            ok_cons = False
    return o, canal, t0, ok_cons


def s5():
    o, canal, t0, cons = s5_pond(9, 36)
    depths = [round(m(o.W[c]), 3) for c in canal]
    h = lw.pond_hist(o, 0)
    surf = m(lw.pond_surface_height(h, o.bodies[0]["dl"]))
    check("S5.A 3x3 2 m pond (36,000 L) + ten 0.5 m squares: all ten wet at 0.237 m", depths == [0.237] * 10, str(depths))
    check("S5.A ... the pond stands 1.737 m deep (surface 0.263 m down)", abs(surf + 5.0 / 19) < 1e-3, "%.4f" % surf)
    check("S5.A ... litres conserved to the decilitre at every pulse", cons)
    check("S5.A ... one surface: worst body gap under 1 mm", worst_gap(o) < 0.001, "%.5f m" % worst_gap(o))
    o, canal, t0, cons = s5_pond(1, 4)
    depths = [round(m(o.W[c]), 4) for c in canal]
    check("S5.B one 2 m pond square (4,000 L) + ten 0.5 m squares: all ten wet at 4.5 cm",
          all(abs(d - 0.0455) < 0.0006 for d in depths), str(depths))
    check("S5.B ... litres conserved to the decilitre", cons and total(o) == t0)
    check("S5.B ... worst body gap under 1 mm", worst_gap(o) < 0.001, "%.5f m" % worst_gap(o))
    # E: a 6x6 basin, 1 m deep, 8,000 L authored as four centre squares at 1 m: levels to 0.111 m everywhere
    o = oracle(8, 8)
    basin = [(x, z) for x in range(1, 7) for z in range(1, 7)]
    for c in basin:
        o.dig(c, 2)
    for c in [(3, 3), (4, 3), (3, 4), (4, 4)]:
        o.set_fill(c, 2)
    run_still(o)
    d = sorted(set(round(m(o.W[c]), 3) for c in basin))
    check("S5.E 6x6 1 m basin, 8,000 L: one flat 0.111 m sheet", d == [0.111], str(d))
    check("S5.E ... 8,000 L kept", sum(o.W[c] for c in basin) == 8 * U)
    # F: one 2 m pond square beside one dry 2 m dug square: they level at 1 m each
    o, canal, t0, cons = s5_pond(1, 4, canal_len=1, canal_d=4)
    check("S5.F one 2 m pond square + one dry 2 m square: 1 m of water each",
          o.W[canal[0]] == 2 * U and o.bodies[0]["dl"] == 2 * U, "%d / %d" % (o.W[canal[0]], o.bodies[0]["dl"]))
    # the 26,000 L pond with the canal floored 0.5 m down: no flow (its surface is below the canal floor)
    o, canal, t0, cons = s5_pond(9, 26)
    check("S5 control: a 26,000 L 3x3 pond (surface 0.56 m down) feeds no 0.5 m canal",
          all(o.W[c] == 0 for c in canal) and o.bodies[0]["dl"] == 26 * U)


def s6():
    # the drawn-down pond alone: nine squares at 1.44 m
    h = lw.histogram([4] * 9)
    d = sorted(set(round(m(lw.pond_square_water(4, h, 26 * U)), 3) for _ in range(9)))
    check("S6 pond: a flat 3x3 2 m pond holding 26,000 L shows nine squares at 1.444 m", d == [1.444], str(d))
    # save and reload mid-flow: a deep copy at pulse 4 continues identically
    src = {(x, z): 0 for x in (1, 2, 3) for z in (1, 2, 3)}
    beds = {c: 4 for c in src}
    o = oracle(20, 5, src, {0: {"limitless": False, "stock": 36.0}}, beds=beds)
    for c in row(4, 2, 10):
        o.dig(c, 1)
    for _ in range(4):
        o.pulse()
    o2 = copy.deepcopy(o)
    t_save = total(o2)
    for _ in range(26):
        o.pulse()
        o2.pulse()
    check("S6.a/b reload: the copy holds the same litres at the save", t_save == total(o))
    check("S6.c reload: run 2 ends in the same settled state, square for square", o.W == o2.W and
          o.bodies[0]["dl"] == o2.bodies[0]["dl"])


# ───────────────────────────── split and merge ─────────────────────────────

def t_split_merge():
    # rising: a fed 1 m channel, a 0.5 m sill, then a dry 1 m channel: the far side wets only once water tops the sill
    lake = {(0, 1): 0}
    o = oracle(12, 3, lake, {0: {"limitless": True, "stock": 0.0}})
    left, sill, right = row(1, 1, 4), (5, 1), row(6, 1, 4)
    for c in left + right:
        o.dig(c, 2)
    o.dig(sill, 1)
    order_ok, merged = True, False
    for _ in range(60):
        o.pulse()
        if any(o.W[c] > 0 for c in right) and any(o.W[c] < U for c in left):
            order_ok = False      # the far basin wet while the near one was still below the sill's floor
        if all(o.W[c] == 2 * U for c in left + right) and o.W[sill] == U:
            merged = True
    check("merge: a rising body tops the sill before the far basin wets, then fills it (one body)", order_ok and merged)
    # falling: one level body over the sill, drained from the right by a sink band, splits; the left keeps 0.5 m
    o = oracle(12, 3, sink_band=None)
    for c in left + right:
        o.dig(c, 2)
    o.dig(sill, 1)
    for c in left + right:
        o.set_fill(c, 2)
    o.set_fill(sill, 1)
    t0 = total(o)
    o.sink_band = 1           # the x >= 11 / x < 1 band: drains the right channel's far end only
    o.dig((10, 1), 2)
    o.dig((11, 1), 2)
    drained0 = o.drained
    split_ok = True
    for _ in range(120):
        o.pulse()
        if any(o.W[c] < U for c in left):
            split_ok = False      # the left basin lost water below the sill floor
    lw_left = sorted(set(o.W[c] for c in left))
    check("split: a falling body splits at the sill; the near basin keeps its 0.5 m below the sill floor",
          split_ok and lw_left == [U] and o.W[sill] == 0, "%s sill %d" % (lw_left, o.W[sill]))
    check("split: the right basin drains away to the sink", all(o.W[c] == 0 for c in right))
    check("split: litres accounted (kept + drained = start)", total(o) + (o.drained - drained0) == t0)


# ───────────────────────────── property fuzz ─────────────────────────────

def fuzz(n):
    bad = []
    still = 0
    for seed in range(n):
        r = random.Random(7000 + seed)
        w, h = r.randint(3, 10), r.randint(3, 10)
        nb = r.randint(0, 3)
        src, bodies, beds = {}, {}, {}
        for b in range(nb):
            lim = r.random() < 0.25
            x0, z0 = r.randrange(w), r.randrange(h)
            for x in range(x0, min(w, x0 + r.randint(1, 3))):
                for z in range(z0, min(h, z0 + r.randint(1, 3))):
                    src.setdefault((x, z), b)
            bodies[b] = {"limitless": lim, "stock": 0.0}
        for c in src:
            beds[c] = r.choice([2, 4, 4, 6])
        for b in bodies:
            cap = sum(beds[c] for c, i in src.items() if i == b)
            bodies[b]["stock"] = float(r.randint(0, cap))
        o = oracle(w, h, src, bodies, beds, sink_band=r.choice([None, None, 1]))
        for _ in range(r.randint(1, w * h // 2)):
            c = (r.randrange(w), r.randrange(h))
            if c not in src:
                o.dig(c, r.randint(1, 4))
        for c in list(o.D):
            if r.random() < 0.3:
                o.set_fill(c, r.randint(0, o.D[c]))
        t0 = total(o)
        limitless = any(b["limitless"] for b in bodies.values())
        for p in range(80):
            try:
                o.pulse()
            except AssertionError as ex:
                bad.append("seed %d pulse %d: %s" % (seed, p, ex))
                break
            if any(o.W[c] < 0 or o.W[c] > o.D[c] * U for c in o.D):
                bad.append("seed %d pulse %d: bounds" % (seed, p))
                break
            t = total(o) + o.drained - o.credited
            if t != t0:
                bad.append("seed %d pulse %d: total %d != %d" % (seed, p, t, t0))
                break
        else:
            if run_still(o, 600) < 600:
                still += 1
                g = worst_gap(o)
                if g >= 0.001:
                    bad.append("seed %d: still water, worst body gap %.4f m" % (seed, g))
            elif not limitless and o.sink_band is None:
                bad.append("seed %d: never settled (no source, no sink)" % seed)
    check("fuzz: %d random scenes: conservation to the dL and bounds every pulse; one surface (< 1 mm) in all %d that "
          "came to rest (the rest feed a sink from a source: moving water)" % (n, still), not bad and still > n // 2,
          "; ".join(bad[:5]) or "only %d came to rest" % still)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    a = ap.parse_args()
    print("U = %d dL per notch per square (read from RM_Volume.cs)" % U)
    t_solve_basics()
    s1()
    s2()
    s4()
    s5()
    s6()
    t_split_merge()
    fuzz(a.n)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
