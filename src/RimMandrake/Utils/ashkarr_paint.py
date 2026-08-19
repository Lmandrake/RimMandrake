#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_paint.py - THE ONE MAP. Hand-authored, once, for Ash'karr.

🔴 THIS IS NOT A GENERATOR. Owner, 2026-08-18: *"We aren't trying to make random
generators that produce alternative planet maps... I just want ONE planetary map that
is as realistic as possible."* Every constant below is a decision about THIS planet,
not a parameter. There is no seed argument and there never will be one: the seed is
frozen at the top so that re-running reproduces the same world, not a different one.
See `design/Jawa/worldbuilding/the_one_map.md`.

THE GEOMETRY, measured not assumed: the tidal lock is a POINT at (lat 0, lon 0), and
temperature falls with angular distance from it (corr -0.98 on both the painted world
and the vanilla source it came from). So `theta` below - degrees from the substellar
point - is the planet's real coordinate. 0 = noon, 90 = terminator, 180 = midnight.

    python3 src/RimMandrake/Utils/ashkarr_paint.py            # build + report
    python3 src/RimMandrake/Utils/ashkarr_paint.py --write    # splice into the save

What it fixes, all five visible in the first worldview.py render of the old painter:
compass-circle seas · comb-toothed rivers · rectangular roads · concentric biome
rings · inherited vanilla region names.
"""
import base64
import csv
import heapq
import json
import math
import os
import re
import struct
import sys
import zlib
from collections import Counter, defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import worldgeom
from worldmap import WorldGrid, WorldObjects, DECODE, load_hash_table, DEFAULT_DUMP

SRC = os.path.join(REPO, "world", "WORLDMAP_sub7b_source.rws")
OUT = os.path.join(REPO, "world", "WORLDMAP_ashkarr_v2.rws")
SEED = 20260818          # frozen. Changing it is building a different planet - don't.

# ---------------------------------------------------------------------------
# 1. spherical noise. Sums of plane waves over the sphere: smooth, band-limited,
#    seamless at the antimeridian and the poles, which a lat/lon noise is not -
#    and lat/lon noise is where the old painter's bullseye came from.
# ---------------------------------------------------------------------------
def waves(V, rng, freq, count):
    d = rng.normal(size=(count, 3))
    d /= np.linalg.norm(d, axis=1)[:, None]
    ph = rng.uniform(0, 2 * math.pi, count)
    return np.sin(freq * V.dot(d.T) + ph).mean(axis=1) * math.sqrt(count) / 2.0


def fbm(V, rng, freq0=1.6, octaves=7, gain=0.52, lac=2.05, count=26):
    out, amp, f = np.zeros(len(V)), 1.0, freq0
    for _ in range(octaves):
        out += amp * waves(V, rng, f, count)
        amp *= gain
        f *= lac
    return out / out.std()


def ridged(V, rng, freq0=2.2, octaves=6, count=20):
    """1 - |noise|, octave by octave. Makes RANGES - long sharp crests with valleys
    between - instead of the smooth blobs plain fbm gives."""
    out, amp, f = np.zeros(len(V)), 1.0, freq0
    for _ in range(octaves):
        out += amp * (1.0 - np.abs(waves(V, rng, f, count)))
        amp *= 0.55
        f *= 2.1
    return (out - out.mean()) / out.std()


def blob(V, lat, lon, radius_deg, falloff=2.0):
    """A soft cap centred on a point. The hand-placed massifs are these."""
    a, b = math.radians(lat), math.radians(lon)
    c = np.array([math.cos(a) * math.cos(b), math.sin(a), math.cos(a) * math.sin(b)])
    ang = np.degrees(np.arccos(np.clip(V.dot(c), -1, 1)))
    t = np.clip(1.0 - ang / radius_deg, 0, 1)
    return t ** falloff


def arc_dist(V, waypoints, samples=240):
    """Angular distance from every tile to a polyline drawn on the globe. The seas and
    the ranges are built from these, which is what makes them ELONGATED rather than
    round - the defect the owner called out."""
    pts = []
    for (la0, lo0), (la1, lo1) in zip(waypoints[:-1], waypoints[1:]):
        a0, b0 = math.radians(la0), math.radians(lo0)
        a1, b1 = math.radians(la1), math.radians(lo1)
        p0 = np.array([math.cos(a0) * math.cos(b0), math.sin(a0), math.cos(a0) * math.sin(b0)])
        p1 = np.array([math.cos(a1) * math.cos(b1), math.sin(a1), math.cos(a1) * math.sin(b1)])
        for t in np.linspace(0, 1, samples // (len(waypoints) - 1)):
            p = p0 * (1 - t) + p1 * t
            pts.append(p / np.linalg.norm(p))
    pts = np.array(pts)
    return np.degrees(np.arccos(np.clip(V.dot(pts.T).max(axis=1), -1, 1)))


# ---------------------------------------------------------------------------
# 2. graph hydrology. Both routines run on the TILE GRAPH, never on a raster -
#    that is the whole reason the rivers come out dendritic instead of combed.
# ---------------------------------------------------------------------------
def fill_depressions(elev, nbl, sea):
    """Priority flood. Every land tile ends with a downhill path to the sea, so no
    river can dead-end in a hole and start drawing circuits looking for a way out."""
    n = len(elev)
    out = np.where(sea, elev, np.inf)
    heap = [(float(out[t]), t) for t in np.nonzero(sea)[0]]
    heapq.heapify(heap)
    done = sea.copy()
    while heap:
        h, t = heapq.heappop(heap)
        if h > out[t]:
            continue
        for u in nbl[t]:
            if done[u]:
                continue
            done[u] = True
            out[u] = max(elev[u], h + 1e-3)
            heapq.heappush(heap, (float(out[u]), u))
    out[~done] = elev[~done]
    return out


def flow(elev, nbl, rain, sea):
    """Steepest-descent routing plus accumulation. Returns (downstream, accum).

    Ties on a filled flat are broken by the FILLED elevation, which is strictly
    increasing away from the outlet - the old painter broke them by heap-pop order
    and drew rectangular circuits."""
    n = len(elev)
    down = np.full(n, -1, dtype=np.int32)
    for t in range(n):
        if sea[t]:
            continue
        best, be = -1, elev[t]
        for u in nbl[t]:
            if elev[u] < be:
                best, be = u, elev[u]
        down[t] = best
    acc = rain.astype(np.float64).copy()
    for t in np.argsort(-elev):
        d = down[t]
        if d >= 0:
            acc[d] += acc[t]
    return down, acc


def bfs_dist(seeds, nbl, n, cap=60):
    d = np.full(n, cap, dtype=np.int32)
    q = deque()
    for s in seeds:
        d[s] = 0
        q.append(s)
    while q:
        t = q.popleft()
        if d[t] >= cap:
            continue
        for u in nbl[t]:
            if d[u] > d[t] + 1:
                d[u] = d[t] + 1
                q.append(u)
    return d


def components(mask, nbl):
    seen = np.zeros(len(mask), bool)
    out = []
    for s in np.nonzero(mask)[0]:
        if seen[s]:
            continue
        q, comp = deque([s]), []
        seen[s] = True
        while q:
            t = q.popleft()
            comp.append(t)
            for u in nbl[t]:
                if mask[u] and not seen[u]:
                    seen[u] = True
                    q.append(u)
        out.append(comp)
    out.sort(key=len, reverse=True)
    return out


def despeckle(labels, nbl, minsize=4):
    """Dissolve patches smaller than minsize into whatever surrounds them. Single-tile
    specks are the tell of a per-tile dice roll; real geography comes in masses."""
    lab = list(labels)
    for name in set(lab):
        mask = np.array([x == name for x in lab])
        for comp in components(mask, nbl):
            if len(comp) >= minsize:
                continue
            ring = Counter()
            for t in comp:
                for u in nbl[t]:
                    if lab[u] != name:
                        ring[lab[u]] += 1
            if ring:
                win = ring.most_common(1)[0][0]
                for t in comp:
                    lab[t] = win
    return lab


# ===========================================================================
# 3. ASH'KARR ITSELF - the gazetteer, in the project's own coordinates.
#
# 🔑 arc  = degrees from the substellar point (lat 0, long 0)
#    bear = degrees around it; 0 -> the GRAY flank (downwind), 180 -> TWILIGHT.
# Identical convention to world_relief.py and paint_ashkarr.py. DO NOT DIVERGE.
# Every position below is the owner's, recovered from those files - the fiction
# already fixes where the Scald and the Fall Line are, so they are an input.
# ===========================================================================
SUB = (0.0, 0.0)

# ---- ranges. A ridge is a LINE, so it inherits the line's shape. ------------
RIDGES = [
    # name, anchors [(arc, bear)...], crest height m, half-width deg
    ("The Scald Spine", None, 1450, 3.2),          # ring - built separately, notched
    ("The Ashteeth",  [(21.5, 116), (23.5, 142), (24.5, 168), (24, 203),
                       (22, 230), (19.5, 254)], 1450, 4.0),   # cradles the Scald
    ("The Fall Line", [(26, 352), (34, 357), (43, 2), (52, 6), (61, 9)], 780, 3.4),
    ("The Dew Horn",  [(58, 148), (64, 162), (67, 178), (63, 196), (57, 210)], 1850, 4.6),
    ("The Ashfall Range", [(56, 338), (63, 352), (66, 8), (61, 24)], 1700, 4.4),
    ("The Twilight Crags", [(104, 210), (110, 186), (108, 160), (114, 134)], 900, 4.0),
    ("The Gray Crags", [(106, 340), (112, 12), (109, 42), (116, 68)], 820, 4.0),
    ("The South Crags", [(118, 250), (127, 272), (131, 300), (124, 322)], 760, 4.0),
]
# ---- basins. Sea level is a threshold on the field, so a coast is a consequence.
BASINS = [
    ("The Scald",       (35, 185), 10.5, -1700),   # ⭐ the one shape ruled ROUND: a crater
    ("The Twilight Sea", (91, 170), 22.0, -1650),  # moldy, on the terminator
    ("The Gray Sea",    (92, 8),   16.5, -1550),   # salt-encrusted, shrinking
    ("The Umbra Trap",  (158, 62), 19.5, -1150),   # no ocean: ammonia flats sit in it
]
TROUGHS = [
    ("The Salt",     [(34, 288), (42, 296), (52, 304), (62, 312), (71, 320)], -430, 5.0),
    ("The Ember Sink", [(36, 96), (46, 88), (57, 80), (68, 74)], -380, 4.6),
    ("The Dew Belt", [(38, 184), (45, 181), (52, 178), (64, 178), (76, 179),
                      (89, 180)], -255, 6.0),
    ("scald_gate",   [(49, 180), (44, 182), (39, 184)], -1250, 3.0),  # the crater breach
]
NIGHT_ARC = 100.0        # past this, liquid water does not exist on this planet


def ab_vec(arc, bear):
    """(arc, bearing) -> unit vector in worldgeom's frame (y is the polar axis)."""
    a, b = np.radians(np.atleast_1d(arc)), np.radians(np.atleast_1d(bear))
    lat = np.arcsin(np.sin(a) * np.sin(b))
    lon = np.arctan2(np.sin(a) * np.cos(b), np.cos(a))
    return np.stack([np.cos(lat) * np.cos(lon), np.sin(lat),
                     np.cos(lat) * np.sin(lon)], axis=1)


def ab_of(lat_deg, lon_deg):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    arc = np.degrees(np.arccos(np.clip(np.cos(lon) * np.cos(lat), -1, 1)))
    bear = np.degrees(np.arctan2(np.sin(lat), np.cos(lat) * np.sin(lon))) % 360.0
    return arc, bear


def path_dist(V, anchors, samples=40):
    pts = []
    for (a0, b0), (a1, b1) in zip(anchors[:-1], anchors[1:]):
        v0, v1 = ab_vec(a0, b0)[0], ab_vec(a1, b1)[0]
        for t in np.linspace(0, 1, samples, endpoint=False):
            v = v0 * (1 - t) + v1 * t
            pts.append(v / np.linalg.norm(v))
    pts.append(ab_vec(anchors[-1][0], anchors[-1][1])[0])
    return np.degrees(np.arccos(np.clip(V.dot(np.array(pts).T).max(axis=1), -1, 1)))


def point_dist(V, arc, bear):
    c = ab_vec(arc, bear)[0]
    return np.degrees(np.arccos(np.clip(V.dot(c), -1, 1)))


def build():
    rng = np.random.default_rng(SEED)
    grid = WorldGrid(SRC)
    geo = worldgeom.Geometry(grid.tiles)
    n, V = grid.tiles, geo.vec
    nbl = [geo.neighbours(t) for t in range(n)]
    arc, bear = ab_of(geo.lat, geo.lon)
    th = arc

    warp_a = fbm(V, rng, freq0=4.2, octaves=4)
    warp_b = fbm(V, rng, freq0=8.5, octaves=4)
    warp_c = fbm(V, rng, freq0=15.0, octaves=3)
    lobe = fbm(V, rng, freq0=2.2, octaves=3)
    lobe2 = fbm(V, rng, freq0=3.6, octaves=3)
    patchy = fbm(V, rng, freq0=7.0, octaves=4)
    patchy2 = fbm(V, rng, freq0=11.0, octaves=3)
    grain = fbm(V, rng, freq0=16.0, octaves=4)
    # the warped angle: every zone edge is tested against THIS, never against arc,
    # so no band can close a circle round the planet
    thb = arc + 7.0 * warp_a + 3.0 * warp_b + 1.2 * warp_c

    print("=== 1. relief from the authored gazetteer ===")
    cont = fbm(V, rng, freq0=1.5, octaves=7)
    detail = fbm(V, rng, freq0=6.0, octaves=5)
    ranges_n = ridged(V, rng, freq0=2.6, octaves=6)

    elev = 300.0 + 420.0 * cont + 190.0 * detail + 55.0 * grain
    # the substellar plateau: FLAT on top - quartic falloff, not a dome
    anvil = np.clip(1.0 - point_dist(V, 0, 0) / 23.0, 0, 1) ** 4
    elev += 1150.0 * anvil
    elev += 300.0 * np.clip(1.0 - point_dist(V, 180, 0) / 95.0, 0, 1) ** 2   # old crust

    ridge_dist = {}
    for name, anchors, amp, halfw in RIDGES:
        if anchors is None:
            continue
        d = path_dist(V, anchors)
        ridge_dist[name] = d
        prof = np.exp(-(d / (halfw * (1.0 + 0.35 * warp_a))) ** 2)
        elev += amp * prof * (0.55 + 0.65 * np.clip(ranges_n, 0, 1.8))
    # ⭐ The Scald Spine is a RING with a NOTCH. A sealed wall cannot drain or be
    # crossed; the notch is where the Dew Belt gets into the crater.
    ds = point_dist(V, 35, 185)
    ring = np.exp(-((ds - 15.5) / 3.2) ** 2)
    notch = 1.0 - 0.55 * np.clip(np.cos(np.radians(3 * (bear - 185) + 0.9 * 57.3)), 0, 1)
    elev += 2050.0 * ring * notch * (0.7 + 0.6 * np.clip(ranges_n, 0, 1.6))
    ridge_dist["The Scald Spine"] = np.abs(ds - 15.5)

    basin_mask = np.zeros(n, bool)
    for name, (a, b), r, amp in BASINS:
        d = point_dist(V, a, b)
        rr = r * (1.0 + 0.30 * warp_a + 0.16 * warp_b)     # torn, not a disc
        prof = np.clip(1.0 - (d / np.clip(rr, 2, 60)) ** 2, 0, 1)
        elev += amp * prof
        basin_mask |= d < rr * 1.25
    for name, anchors, amp, halfw in TROUGHS:
        d = path_dist(V, anchors)
        elev += amp * np.exp(-(d / (halfw * (1.0 + 0.3 * warp_b))) ** 2)

    print("=== 2. sea level ===")
    # 🔴 Owner 2026-08-18: "There's WAY too much water, so reduce that to a third."
    # 25.8% -> ~8.6%. Water is elevation<0 AND inside an authored basin, so the
    # planet cannot grow seas nobody named.
    sea = (elev < 0) & basin_mask
    keep = np.zeros(n, bool)
    sea_id = np.full(n, -1, np.int8)
    for i, (name, (a, b), r, amp) in enumerate(BASINS):
        if name == "The Umbra Trap":
            continue                     # ammonia, not ocean - it holds no water
        m = sea & (point_dist(V, a, b) < r * 2.0)
        if not m.any():
            continue
        comp = components(m, nbl)[0]
        keep[comp] = True
        sea_id[comp] = i
    sea = keep
    elev[sea] = np.minimum(elev[sea], -25.0)
    elev[~sea] = np.clip(elev[~sea], 12.0, 3800.0)

    print("=== 3. hydrology ===")
    # Owner's ruling 2026-08-17: moist air is dragged off the terminator toward the
    # sun and wrung out climbing the ranges, so a range rains on its TERMINATOR-FACING
    # flank and the substellar plateau is the rain shadow.
    moist = np.exp(-((arc - 96.0) / 40.0) ** 2)          # the source is the seam
    lift = np.zeros(n)
    for t in range(n):
        if arc[t] > NIGHT_ARC + 14:
            continue
        best = 0.0
        for u in nbl[t]:
            if arc[u] > arc[t]:                        # u is further from the sun
                best = max(best, (elev[t] - elev[u]) / 260.0)
        lift[t] = best
    dayside = np.clip((NIGHT_ARC + 12.0 - arc) / 24.0, 0, 1)
    rain_src = np.clip((0.35 + 3.6 * np.clip(lift, 0, 6.0)) * moist * dayside, 0.02, None)

    for cycle in range(4):
        filled = fill_depressions(elev, nbl, sea)
        down, acc = flow(filled, nbl, rain_src, sea)
        cut = 44.0 * np.log1p(acc) * np.clip(elev / 900.0, 0.15, 3.0)
        elev[~sea] = np.clip(elev[~sea] - cut[~sea], 12.0, 3800.0)
    filled = fill_depressions(elev, nbl, sea)
    down, acc = flow(filled, nbl, rain_src, sea)
    need = 60.0 + 520.0 * np.clip((70.0 - arc) / 50.0, 0, 1) ** 1.6
    chan = (acc > need) & (~sea) & (arc < NIGHT_ARC)
    print("    channel tiles %d" % chan.sum())

    mouths = [int(t) for t in np.nonzero(chan)[0]
              if down[t] >= 0 and sea[down[t]] and acc[t] > 90]
    delta = np.zeros(n, bool)
    for m in mouths:
        front, reach = {m}, (4 if acc[m] > 700 else 3)
        delta[m] = True
        for _ in range(reach):
            nxt = set()
            for t in front:
                for u in nbl[t]:
                    if sea[u] or delta[u] or elev[u] > elev[m] + 190:
                        continue
                    delta[u] = True
                    nxt.add(u)
            front = nxt
    print("    mouths %d, delta tiles %d" % (len(mouths), delta.sum()))

    print("=== 4. biomes ===")
    riparian = bfs_dist(np.nonzero(chan)[0], nbl, n, cap=9)
    bigriver = bfs_dist(np.nonzero(chan & (acc > 1400))[0], nbl, n, cap=9)
    near_sea = bfs_dist(np.nonzero(sea)[0], nbl, n, cap=9)
    d_gray = point_dist(V, 92, 8)
    d_twi = point_dist(V, 91, 170)
    d_scald = point_dist(V, 35, 185)
    d_umbra = point_dist(V, 158, 62)
    bear_off = lambda b0: np.abs((bear - b0 + 180) % 360 - 180)
    off_gray, off_twi = bear_off(0.0), bear_off(180.0)

    B = ["Desert"] * n
    for t in range(n):
        a, e, r = thb[t], elev[t], riparian[t]
        p, p2 = patchy[t], patchy2[t]
        if sea[t]:
            B[t] = "Ocean"
            continue
        # ---- the dark, one mass with lobes inside it
        if a > 108 + 16.0 * lobe[t]:
            B[t] = "AB_RockyCrags"
            gate = lobe[t] + 0.55 * lobe2[t]
            if a < 138 and gate > 0.35 and p > -0.6:
                B[t] = "PoisonForest"
            elif 124 < a < 162 and gate < -0.45 and p2 > -0.4:
                B[t] = "BMT_FungalForest" if p2 > 1.1 else "AB_MycoticJungle"
            if p2 > 1.5 and gate > 0.9:
                B[t] = "HorrorWastes"
            if d_umbra[t] < 22 and p > -0.8:
                B[t] = "AB_PropaneLakes"          # The Ammonia Flats
            if a > 150 and p2 > 1.75:
                B[t] = "Glowforest" if p > 0.3 else "BMT_CrystalCaverns"
        # ---- the water margin
        elif delta[t]:
            B[t] = ("AB_MiasmicMangrove" if p2 > -0.2 else
                    "COMIGO_GreaterSwamp_Tropical" if p > 0.8 else "Wasteland")
        elif r <= 1:
            B[t] = "AB_FeraliskInfestedJungle"
        elif r <= 2 and bigriver[t] <= 2:
            B[t] = "ZBiome_DesertOasis"
        # ---- the terminator, arc 78..108: the rot, and the gelatinous
        elif a > 78:
            B[t] = "AridShrubland" if p > -0.2 else "Wasteland"
            if p2 > 0.95 and p > 0.2:
                B[t] = "PoisonForest"
            # 🔴 owner 2026-08-18: "Gelatinous Superorganism should definitely be on
            # the terminator." Patches, never a band.
            if 84 < a < 104 and p2 > 1.25 and lobe2[t] > 0.1:
                B[t] = "AB_GelatinousSuperorganism"
            if near_sea[t] <= 2 and p2 > 0.5:
                B[t] = "AB_TarPits"
        # ---- the Dew Belt: the wet trough running sunward off the Twilight seam
        elif off_twi[t] < 24 and 44 < a < 92:
            B[t] = ("ZBiome_DesertOasis" if p2 > 1.2 else
                    "AridShrubland" if p > -0.3 else "Desert")
        # ---- the Pyrelands: stormy savanna, burning, tar pits interspersed
        elif off_gray[t] < 62 and 50 < a < 86 and (p + 0.5 * lobe[t]) > -0.25:
            B[t] = "ZBiome_Grasslands"
            if p2 > 1.3:
                B[t] = "AB_TarPits"
        # ---- the dayside waste
        elif a < 20:
            B[t] = "ExtremeDesert"
        elif a < 44:
            B[t] = "ExtremeDesert" if p < 0.55 else "Desert"
        elif a < 72:
            B[t] = "Desert" if p < 0.95 else "ZBiome_Badlands"
        else:
            B[t] = "AridShrubland" if p > 0.2 - 0.5 * lobe2[t] else "Desert"
        if B[t] in ("Desert", "AridShrubland") and e > 1500 and p2 > 0.4:
            B[t] = "ZBiome_Badlands"
        if e > 2400 and arc[t] < 118 and acc[t] > 12 and p2 > 0.9:
            B[t] = "AB_OcularForest"     # only on mountain tops, tiny patches

    # ---- THE STORY OVERRIDES, in the owner's own coordinates -----------------
    for t in range(n):
        if sea[t]:
            continue
        a = arc[t] + 3.6 * warp_a[t] + 2.2 * warp_b[t] + 1.4 * warp_c[t]
        # The Rust Cathedral: mechanoids at the substellar point, permanently at war.
        # 🔴 tested against the WARPED arc - against raw arc it is a disc inside a ring.
        if a < 12.5 and bear_off(40.0)[t] < 118 and (patchy[t] + 0.5 * warp_a[t]) > -1.1:
            B[t] = "AB_MechanoidIntrusion"
        elif 12.5 <= a < 17.0 and (patchy2[t] + 0.6 * lobe[t]) > -0.85:
            B[t] = "Scarlands"                       # The Scorch, broken into arcs
        # the Scald rim: volcanics on the ring, high ground only
        elif 10.0 < d_scald[t] < 22.0 and elev[t] > 1150:
            q = patchy2[t] + 0.5 * warp_b[t]
            B[t] = ("Volcano" if q > 0.9 else "LavaField" if q > 0.25
                    else "AB_PyroclasticConflagration" if q > -0.4 else "ZBiome_Badlands")
        # The Salt: evaporite hugging the Gray Sea's downwind coast
        elif d_gray[t] < 26 and bear_off(18.0)[t] < 36 and near_sea[t] < 7:
            B[t] = "Wasteland" if patchy[t] > -0.4 else "ZBiome_Badlands"

    B = despeckle(B, nbl, minsize=7)
    for t in range(n):
        if sea[t]:
            B[t] = "Ocean"
        elif B[t] == "Ocean":
            B[t] = "ZBiome_Badlands"

    # ---- the gazetteer, as world features -----------------------------------
    regions = []
    for i, (name, (a, b), r, amp) in enumerate(BASINS):
        if name == "The Umbra Trap":
            regions.append(("The Ammonia Flats", "waste",
                            np.nonzero((d_umbra < 22) & ~sea)[0]))
        else:
            regions.append((name, "sea", np.nonzero(sea_id == i)[0]))
    regions.append(("The Rust Cathedral", "waste",
                    np.nonzero([x == "AB_MechanoidIntrusion" for x in B])[0]))
    regions.append(("The Scorch", "waste",
                    np.nonzero([x == "Scarlands" for x in B])[0]))
    regions.append(("The Anvil", "waste", np.nonzero((arc < 20) & ~sea)[0]))
    regions.append(("The Dune Sea", "waste",
                    np.nonzero((arc >= 20) & (arc < 40) & ~sea)[0]))
    for name, anchors, amp, halfw in RIDGES:
        d = ridge_dist.get(name)
        if d is None:
            continue
        regions.append((name, "massif", np.nonzero((d < halfw * 1.5) & ~sea)[0]))
    regions.append(("The Dew Belt", "waste",
                    np.nonzero((off_twi < 24) & (arc > 40) & (arc < 92) & ~sea)[0]))
    regions.append(("The Fall Line Barrens", "waste",
                    np.nonzero((off_gray < 20) & (arc > 26) & (arc < 62) & ~sea)[0]))
    regions.append(("The Salt", "waste",
                    np.nonzero((d_gray < 26) & (bear_off(18.0) < 36) & ~sea)[0]))
    regions.append(("The Pyrelands", "waste",
                    np.nonzero([x == "ZBiome_Grasslands" for x in B])[0]))
    regions.append(("The Sunreach", "waste",
                    np.nonzero((arc > 96) & (arc < 124) & (off_gray < 55) & ~sea)[0]))
    regions.append(("The Nightspill", "waste",
                    np.nonzero((arc > 96) & (arc < 124) & (off_twi < 55) & ~sea)[0]))
    regions.append(("The Umbra", "waste", np.nonzero((arc > 152) & ~sea)[0]))
    regions.append(("The Salt Gate", "waste", np.nonzero(delta)[0]))
    regions = [(nm, kd, tl) for nm, kd, tl in regions if len(tl) >= 6]

    return dict(regions=regions, grid=grid, geo=geo, n=n, V=V, th=arc, arc=arc,
                bear=bear, elev=elev, sea=sea, sea_id=sea_id, chan=chan, acc=acc,
                down=down, biome=B, rain_src=rain_src, riparian=riparian,
                delta=delta, nbl=nbl, seas=BASINS, massifs=RIDGES, filled=filled)


def report(w):
    n, nbl, sea = w["n"], w["nbl"], w["sea"]
    comps = components(sea, nbl)
    print("\n--- ACCEPTANCE ---")
    print("water      %d tiles = %.1f%%   (owner 2026-08-18: about 8.6%%)"
          % (sea.sum(), 100.0 * sea.sum() / n))
    print("bodies     %d  sizes %s   (owner: exactly 3)"
          % (len(comps), [len(c) for c in comps[:6]]))
    for i, c in enumerate(comps[:4]):
        m = np.zeros(n, bool)
        m[c] = True
        per = sum(1 for t in c for u in nbl[t] if not m[u])
        lat = float(np.mean(w["geo"].lat[c]))
        thm = float(np.mean(w["th"][c]))
        print("   body %d  %5d tiles  perim^2/area %6.1f  (circle 12.6, owner >=25)"
              "  mean theta %.0f deg" % (i, len(c), per * per / len(c), thm))
    print("channels   %d tiles, %d flowing to a sea"
          % (w["chan"].sum(),
             sum(1 for t in np.nonzero(w["chan"])[0]
                 if w["down"][t] >= 0 and sea[w["down"][t]])))
    cen = Counter(w["biome"])
    print("biomes     %d distinct" % len(cen))
    for b, c in cen.most_common(14):
        print("   %-32s %5d  %5.2f%%" % (b, c, 100.0 * c / n))


if __name__ == "__main__":
    w = build()
    report(w)
    if "--write" in sys.argv:
        import ashkarr_write
        ashkarr_write.write(w, OUT, w["regions"])
