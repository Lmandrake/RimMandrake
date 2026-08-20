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
import os as _os
import sys as _sys

if _os.environ.get("PYTHONHASHSEED") != "0":
    # 🔴 THE MAP IS FROZEN, and Python unfreezes it by default. String-hash
    # randomisation reorders any set/dict of names, and several passes here are
    # order-dependent. Pinning it is not a parameter: it has exactly one legal
    # value, and the alternative is a different planet every run.
    _os.execve(_sys.executable, [_sys.executable] + _sys.argv,
               dict(_os.environ, PYTHONHASHSEED="0"))

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

TILES = 21872            # the engine's own grid at subdivisions 7; geometry only
BUNDLE = os.path.join(REPO, "world", "ASHKARR_WORLDMAP")

# 🔴 THE SAVEGAME IS NOT INVOLVED. Owner, 2026-08-18: "Please don't write to the
# savegame file anymore" and "DO NOT use the rivers, roads, and settlements in the
# current savegame. YOU decide where they go by the lore."
# So this file does not open a .rws at all - not to read and not to write. The only
# thing taken from the engine is the TILE GEOMETRY (world/world_tiles_sub7b.csv and
# world/world_neighbors_sub7b.csv, dumped from a live game), because tile positions
# exist nowhere else. Every biome, elevation, river, road and settlement below is
# derived here from the design docs.
SEED = 20260818          # frozen. Changing it is building a different planet - don't.

# ---------------------------------------------------------------------------
# ⭐ THE PLAYER'S HOME. Sited 2026-08-19; the docs had only "the habitable ring
# is ~34-57 degrees of arc" and left it open. This is the whole decision:
#
#   THE SETDOWN, in the Fall Line Barrens, on the GRAY (downwind) flank -
#   arc 56.9, bearing 358.8, ExtremeDesert, 276 m, 38.6 C, 18 mm of rain,
#   and the nearest standing water is 26 degrees away.
#
# Why here and nowhere else:
#   - It is the OUTER EDGE of the habitable ring, so everything the clan needs
#     lies OUTWARD toward the terminator and everything that will kill them lies
#     sunward. The campaign has a direction built into the ground.
#   - The Jawa Trade Moot's anchor, The Ore Moot - the mine the sandcrawlers were
#     stolen from - is 5.3 deg away. Kin are one caravan out, not zero.
#   - The Junkers' worked-out mining fields (The Claim Jump 10.4, Tailings End
#     12.1, The Slagfield 15.1) are the second ring. The gravship needs a
#     thruster, a fuel tank and a pilot console; that is where they come from.
#   - The Empire's Ashgarrison is 16.2 deg away - close enough to be a presence,
#     far enough not to be a garrison next door.
#   - ExtremeDesert with no river, no oasis and no coast within 26 deg. Water is
#     the campaign's pressure, not a resource on the map, exactly as the water
#     doctrine has it. It is also the harshest ground a colony can actually hold.
#   - The Fall Line is the range that wrecks fall along; the clan lives in its
#     barrens. That is where a dead gravship was found and woken.
# Resolved by LAT/LON, not by tile number, so it survives a geometry rebuild.
HOME_LATLON = (-1.0282, 56.8669)
HOME_NAME = "The Setdown"

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


def flow(elev, nbl, rain, sea, evap=None):
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
        if d < 0:
            continue
        # 🔑 A DESERT RIVER LOSES WATER AS IT GOES. Without this every stream that
        # starts anywhere arrives somewhere, and the map fills with rivers that no
        # climate could feed. With it, a branch that leaves the wet ground dies -
        # which is what a salt pan IS.
        carry = acc[t] if evap is None else max(0.0, acc[t] - evap[t])
        acc[d] += carry
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
    # 🔴 sorted(), not set(). Dissolving speck A changes what B's specks see, so the
    # ORDER of the biome names decides the outcome - and a bare set of strings
    # iterates differently in every Python process. That alone made three rebuilds
    # of this "frozen" map produce three different planets (2026-08-19).
    for name in sorted(set(lab)):
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
                # ties break on the NAME, never on insertion order.
                win = min(ring.items(), key=lambda kv: (-kv[1], kv[0]))[0]
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
# ⭐ Each basin carries a WATER LEVEL, and the Scald's is high.
# 🔴 Owner: "some rivers really should be emitted out of the Scald... it was supposed
# to be a major source of water." A lake below sea level cannot emit anything - water
# runs into it and stops. So the Scald is a PERCHED crater lake: its surface stands at
# +1150 m, 1.1 km above the desert outside its wall, and it SPILLS through the one
# notch in the Spine. That is what makes it the head of the planet's largest river
# instead of its drain.
BASINS = [
    # name, (arc, bear), radius, floor amp, water level m, is it a sink
    ("The Scald",       (35, 185), 10.5, -1500, None,   False),   # level = auto
    ("The Twilight Sea", (91, 170), 22.0, -1650,    0.0, True),
    ("The Gray Sea",    (92, 8),   16.5, -1550,    0.0, True),
    ("The Umbra Trap",  (158, 62), 19.5, -1150,  -900.0, False),   # ammonia, not water
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
    geo = worldgeom.Geometry(TILES)
    n, V = TILES, geo.vec
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
    basin_of = np.full(n, -1, np.int8)
    for i, (name, (a, b), r, amp, level, sink) in enumerate(BASINS):
        d = point_dist(V, a, b)
        rr = r * (1.0 + 0.30 * warp_a + 0.16 * warp_b)     # torn, not a disc
        prof = np.clip(1.0 - (d / np.clip(rr, 2, 60)) ** 2, 0, 1)
        elev += amp * prof
        inside = d < rr * 1.25
        basin_mask |= inside
        basin_of[inside & (basin_of < 0)] = i
    for name, anchors, amp, halfw in TROUGHS:
        d = path_dist(V, anchors)
        elev += amp * np.exp(-(d / (halfw * (1.0 + 0.3 * warp_b))) ** 2)
    # the Scald floor is lifted bodily so the lake can perch: the crater is high
    # ground with a hole in it, not a pit in the lowlands
    elev[basin_of == 0] += 150.0

    print("=== 2. sea level ===")
    # 🔴 Owner 2026-08-18: "There's WAY too much water, so reduce that to a third."
    # 25.8% -> ~8.6%. Water is elevation<0 AND inside an authored basin, so the
    # planet cannot grow seas nobody named.
    keep = np.zeros(n, bool)
    sea_id = np.full(n, -1, np.int8)
    sink = np.zeros(n, bool)
    levels = {}
    for i, (name, (a, b), r, amp, level, is_sink) in enumerate(BASINS):
        if level is None:
            # fill the crater to 68% of its own depth: a real lake with a real shore,
            # and a rim still standing above it everywhere but the notch
            core = elev[(basin_of == i)]
            level = float(np.percentile(core, 68))
        levels[i] = level
        if level < -100:
            continue                     # the Umbra Trap holds ammonia, not water
        m = (basin_of == i) & (elev < level)
        if not m.any():
            continue
        comp = components(m, nbl)[0]     # one body per basin; splinters are dry
        keep[comp] = True
        sea_id[comp] = i
        if is_sink:
            sink[comp] = True
    sea = keep
    for i in levels:
        m = sea & (sea_id == i)
        elev[m] = levels[i] - 30.0
    elev[~sea] = np.clip(elev[~sea], 12.0, 3800.0)

    print("=== 3. hydrology ===")
    # Owner's ruling 2026-08-17: moist air is dragged off the terminator toward the
    # sun and wrung out climbing the ranges, so a range rains on its TERMINATOR-FACING
    # flank and the substellar plateau is the rain shadow.
    # 🔴 Owner, 2026-08-18: "some rivers really should be emitted out of the Scald...
    # it was supposed to be a major source of water and the dominant region of
    # terrestrial-type foliage along its rivers."
    # The mechanism: the Scald is a hot lake in the hottest place on the planet, so it
    # evaporates hard; the vapour has nowhere to go but up the Spine that rings it, and
    # rains out on the ring. Rivers therefore radiate OUT over the Spine as well as
    # draining in - the crater is a pump, not a sink.
    d_scald_pt = point_dist(V, 35, 185)
    scald_plume = np.exp(-((d_scald_pt - 15.0) / 11.0) ** 2)
    moist = 0.42 * np.exp(-((arc - 96.0) / 34.0) ** 2) + 1.9 * scald_plume
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
    rain_src = np.clip((0.35 + 3.6 * np.clip(lift, 0, 6.0)) * moist * dayside
                       + 2.6 * scald_plume, 0.02, None)

    # ⭐ THE LAKE IS A SOURCE. Every drop the Scald's catchment collects leaves through
    # the one notch, so the outflow carries the whole crater - the largest river on
    # Ash'karr starts at a lake 1.1 km above the desert it crosses.
    # evaporation per tile: brutal in the deep waste, mild in the crater basin and on
    # the seam. This is what kills a branch in open desert.
    # 🔴 Owner 2026-08-19: "The rivers shouldn't connect the basins, they should peter
    # out into salt flats." So evaporation is set high enough to kill even the Scald's
    # 32,000-unit trunk before it can reach the Twilight or the Grey Sea. The crater
    # basin itself keeps a low loss, which is why its own valleys stay green.
    evap = (900.0 * np.clip(1.0 - moist / 1.2, 0.05, 1.0)
            * np.clip((110.0 - arc) / 60.0, 0.25, 1.6))
    evap[d_scald_pt < 22] *= 0.16
    scald_water = sea & (sea_id == 0)
    # 🔴 Owner 2026-08-19: the Scald's river must be MASSIVE and the driving river
    # system of the world. The lake's catchment is the whole crater plus its own
    # surface, and all of it leaves through one notch.
    rain_src[scald_water] += 260.0
    for cycle in range(4):
        filled = fill_depressions(elev, nbl, sink)
        filled = np.where((filled - elev) > 70.0, elev, filled)
        down, acc = flow(filled, nbl, rain_src, sink, evap)
        cut = 44.0 * np.log1p(acc) * np.clip(elev / 900.0, 0.15, 3.0)
        erodible = ~sea
        elev[erodible] = np.clip(elev[erodible] - cut[erodible], 12.0, 3800.0)
    filled = fill_depressions(elev, nbl, sink)
    down, acc = flow(filled, nbl, rain_src, sink)
    outs = [acc[u] for t in np.nonzero(scald_water)[0] for u in nbl[t]
            if not scald_water[u]]
    print("    Scald: lake %d tiles at %.0f m, outflow trunk carries %.0f"
          % (scald_water.sum(), elev[scald_water].mean() if scald_water.any() else 0,
             max(outs) if outs else 0))
    need = 60.0 + 520.0 * np.clip((70.0 - arc) / 50.0, 0, 1) ** 1.6
    need = np.where(d_scald_pt < 46.0, 60.0, need)   # the Scald basin is wet
    chan = (acc > need) & (~sea) & (arc < NIGHT_ARC + 8)
    print("    channel tiles %d" % chan.sum())

    # 🔴 Owner: "each branch ending in dead salt plains or tiny hyper saline pools."
    # A terminus is a channel tile whose downstream neighbour is NOT a channel and NOT
    # the sea - the river simply stops being a river there.
    terminus = np.zeros(n, bool)
    for t in np.nonzero(chan)[0]:
        d = down[t]
        # 🔴 reaching a sea counts as a terminus too: the owner ruled that rivers do
        # not connect the basins, so the last reach dies on the flat instead of
        # emptying into one.
        if d < 0 or not chan[d] or sink[d] or acc[t] <= evap[t]:
            terminus[t] = True
    saltpan = np.zeros(n, bool)
    pool = np.zeros(n, bool)
    for t in np.nonzero(terminus)[0]:
        front = {int(t)}
        saltpan[t] = True
        for step in range(3 if acc[t] > 400 else 2):
            nxt = set()
            for x in front:
                for u in nbl[x]:
                    if sea[u] or saltpan[u] or elev[u] > elev[t] + 90:
                        continue
                    saltpan[u] = True
                    nxt.add(u)
            front = nxt
        if acc[t] > 700:                 # a big branch leaves standing brine behind
            pool[t] = True
    print("    termini %d, salt plain %d tiles, hypersaline pools %d"
          % (terminus.sum(), saltpan.sum(), pool.sum()))

    # a big river that dies leaves a marsh fan before the salt takes over
    mouths = [int(t) for t in np.nonzero(terminus)[0] if acc[t] > 600]
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
    riparian = bfs_dist(np.nonzero(chan)[0], nbl, n, cap=12)
    # 🔑 THE BANDS SCALE WITH THE RIVER. A creek gets one tile of green; the
    # Scald's trunk gets a corridor. Flat bands ate the vast desert.
    midriver = bfs_dist(np.nonzero(chan & (acc > 900))[0], nbl, n, cap=12)
    bigriver = bfs_dist(np.nonzero(chan & (acc > 5000))[0], nbl, n, cap=14)
    near_sea = bfs_dist(np.nonzero(sea)[0], nbl, n, cap=9)
    d_gray = point_dist(V, 92, 8)
    d_twi = point_dist(V, 91, 170)
    d_scald = d_scald_pt
    d_umbra = point_dist(V, 158, 62)
    bear_off = lambda b0: np.abs((bear - b0 + 180) % 360 - 180)
    off_gray, off_twi = bear_off(0.0), bear_off(180.0)

    B = ["Desert"] * n
    for t in range(n):
        a, e, r = thb[t], elev[t], riparian[t]
        p, p2 = patchy[t], patchy2[t]
        if sea[t]:
            B[t] = "Lake" if sea_id[t] == 0 else "Ocean"
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
        elif pool[t]:
            B[t] = "Lake"                     # a tiny hypersaline pool
        elif saltpan[t] and r > 1:
            B[t] = "Wasteland" if p > -0.5 else "ZBiome_Badlands"   # dead salt plain
        elif delta[t]:
            B[t] = ("AB_MiasmicMangrove" if p2 > -0.2 else
                    "COMIGO_GreaterSwamp_Tropical" if p > 0.8 else "Wasteland")
        elif r <= 1:
            # 🔑 owner 2026-08-18: the TERRESTRIAL foliage belongs to the Scald and its
            # rivers. The meridian gets mycoid and poison forest instead - so the two
            # kinds of green mean different things and you can tell where you are by
            # what is growing.
            # ⭐ THE RIPARIAN ZONATION, ruled by the owner 2026-08-19:
            #   on the river   VICIOUS JUNGLE
            #   bracketing it  lesser jungle and marsh
            #   then           the PYRELANDS (stormy savanna)
            #   then           desert
            # Meridian rivers substitute mycoid and poison forest for the jungle, so
            # the two greens still mean different things.
            B[t] = ("AB_MycoticJungle" if a > 82 and p > -0.4 else
                    "PoisonForest" if a > 82 else "AB_FeraliskInfestedJungle")
        elif r <= 2 or midriver[t] <= 2:
            B[t] = ("AB_MiasmicMangrove" if p2 > 1.1 else
                    "COMIGO_GreaterSwamp_Tropical" if p2 > 0.5 and a < 78 else
                    "PoisonForest" if a > 86 else "ZBiome_DesertOasis")
        elif a < 74 and (midriver[t] <= 2 or bigriver[t] <= 4):
            B[t] = "ZBiome_Grasslands"        # the Pyrelands bracket the green
            if p2 > 1.45:
                B[t] = "AB_TarPits"
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
        # ---- the dayside waste
        # 🔴 Owner 2026-08-19: "Make the grassland into more desert, and make more
        # extreme desert." The waste is the planet's default state; green is the
        # exception and has to be paid for by a river.
        elif a < 30:
            B[t] = "ExtremeDesert"
        elif a < 56:
            B[t] = "ExtremeDesert" if p < 0.85 else "Desert"
        elif a < 78:
            B[t] = ("ZBiome_Badlands" if p > 1.15 else
                    "ExtremeDesert" if p < -0.55 else "Desert")
        else:
            B[t] = "AridShrubland" if p > 0.65 - 0.5 * lobe2[t] else "Desert"
        if B[t] in ("Desert", "AridShrubland") and e > 1500 and p2 > 0.4:
            B[t] = "ZBiome_Badlands"
        # ⭐ `worldgen_interactive_def.md`: "ONLY at the tops of mountains, in tiny
        # patches"; `desert_world_design.md`: "always placed on or adjacent to
        # Mountainous terrain, and configured to BLEED small rivers outward - the
        # eye-biome as a strange highland spring feeding the lowlands." So it sits on
        # the peaks that are river SOURCES, and the streams leave it carrying spores.
        if e > 2350 and arc[t] < 124 and acc[t] > 8 and p2 > 0.75:
            B[t] = "AB_OcularForest"

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
            B[t] = "Lake" if sea_id[t] == 0 else "Ocean"
        elif B[t] in ("Ocean", "Lake"):
            B[t] = "ZBiome_Badlands"

    # ---- the gazetteer, as world features -----------------------------------
    regions = []
    for i, (name, (a, b), r, amp, level, is_sink) in enumerate(BASINS):
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

    return dict(regions=regions, geo=geo, n=n, V=V, th=arc, arc=arc,
                d_scald=d_scald_pt, d_twilight=d_twi, d_gray=d_gray, thb=thb,
                sink=sink,
                bear=bear, elev=elev, sea=sea, sea_id=sea_id, chan=chan, acc=acc,
                down=down, biome=B, rain_src=rain_src, riparian=riparian,
                delta=delta, nbl=nbl, seas=BASINS, massifs=RIDGES, filled=filled)


def temperature_curve(th, elev):
    """Owner's ruled endpoints: +70 C at the substellar point, +14 C at the
    terminator, -80 C in deep night, minus an altitude lapse of 5.5 C/km."""
    return np.interp(th, [0, 30, 60, 90, 120, 150, 180],
                     [70.0, 58.0, 38.0, 14.0, -22.0, -58.0, -80.0]) \
        - np.clip(elev, 0, None) / 1000.0 * 5.5


# the ratified faction labels (name_ashkarr_factions.py), and the slot each one
# occupies in the source save's faction list
FACTION_LABEL = {
    "Empire": "The Galactic Empire", "OutlanderCivil": "Homestead Defense League",
    "TribeCivil": "Deep Desert Tribes", "AM_EnemyPirate": "Blackstar Company",
    "Jawa_HuttCartel": "Hutt Cartel", "Jawa_FreeDroidEnclaves": "Free Droid Enclaves",
    "Jawa_WildsteamClan": "Wildsteam Clan", "Jawa_DeepwaterCompact": "Deepwater Compact",
    "Jawa_GeonosianFoundryHive": "Geonosian Foundry Hive",
    "Jawa_AscendantHelix": "Ascendant Helix", "Jawa_IndigenousTribes": "Jawa Trade Moot",
    "Jawa_Junkers": "the Junkers", "Mechanoid": "the Forgotten Arsenal",
}


# ---------------------------------------------------------------------------
# HILLINESS and SWAMPINESS. Both are per-tile state the engine stores and NEVER
# recomputes - if we do not write them, hilliness stays 0/Undefined. Neither is a
# function of elevation in vanilla (Terrain rolls them from their own noise), so on
# a hand-authored planet they are ours to decide. These two functions are that
# decision; they used to live in the renderer, which was the wrong place.
# ---------------------------------------------------------------------------
HILLINESS = {"Flat": 1, "SmallHills": 2, "LargeHills": 3, "Mountainous": 4,
             "Impassable": 5}


def hilliness(w, reg):
    """Roughness is LOCAL RELIEF - the drop between a tile and its neighbours - not
    height. A 2 km plateau is flat to stand on; a 400 m escarpment is not."""
    n, elev, sea, nbl = w["n"], w["elev"], w["sea"], w["nbl"]
    rel = np.zeros(n)
    for t in range(n):
        vals = [elev[t]] + [elev[u] for u in nbl[t]]
        rel[t] = max(vals) - min(vals)

    # 🔑 Calibrated against THIS planet's relief, not against a guess. Land relief
    # runs p50=132 p80=231 p90=325 p95=439, so the old 190/430/780 cuts made 73% of
    # the planet Flat - a pancake with eight named ranges on it. These cuts give
    # Flat 36 / SmallHills 38 / LargeHills 19 / Mountainous 7, which is a desert
    # world with real bones: vast plains AND broken country.
    out = np.where(rel < 110, 1, np.where(rel < 210, 2, np.where(rel < 380, 3, 4)))

    # ⭐ The crags are DEFINED as broken ground, and their relief alone (p50 = 140)
    # would print most of them Flat. Biome floors the roughness; relief only raises it.
    crag = np.array([b in ("AB_RockyCrags", "ZBiome_Badlands") for b in w["biome"]])
    out = np.where(crag & (out < 2), 2, out)
    out = np.where(crag & (rel > 170) & (out < 3), 3, out)
    out = np.where(sea, 1, out)           # water is Flat; the engine expects that

    # 🔴 IMPASSABLE EXISTS ON THIS PLANET IN EXACTLY ONE PLACE: the Scald Spine crest,
    # outside the Gate - 53 tiles. It makes the Spine genuinely expensive to cross and
    # bends traffic toward the Scald Gate, which is the lore's one breach.
    # ⚠️ It does NOT seal the crater and this file will not pretend it does: the ring
    # is broken, and manufacturing a contiguous wall would be inventing terrain to
    # serve a sentence. Everywhere else Impassable is banned - this is a caravan game
    # whose distances are the story, and stray impassable tiles just break routes.
    gate = point_dist(w["geo"].vec, 49.0, 180.0) < 9.0
    spine = np.array([reg.get(t) == "The Scald Spine" for t in range(n)])
    out = np.where(spine & (elev > 900) & ~gate & ~sea, 5, out)
    return out.astype(np.uint8)


# Swampiness drives how much marsh and standing water a landing map gets. On Ash'karr
# that is a property of the GREEN, and the green is a property of the rivers - the
# desert has none of it and the salt pans least of all.
SWAMPINESS = {
    "AB_MiasmicMangrove": 0.85, "COMIGO_GreaterSwamp_Tropical": 0.80,
    "AB_FeraliskInfestedJungle": 0.45, "AB_MycoticJungle": 0.40,
    "PoisonForest": 0.35, "ZBiome_DesertOasis": 0.20, "AB_PropaneLakes": 0.30,
    "BMT_FungalForest": 0.25, "ZBiome_Grasslands": 0.05,
}


def swampiness(w):
    out = np.zeros(w["n"])
    for t, b in enumerate(w["biome"]):
        out[t] = 0.0 if w["sea"][t] else SWAMPINESS.get(b, 0.0)
    return out


def write_bundle(w):
    """⭐ THE MAP, as data. Four files, all committed, all readable without RimWorld."""
    import csv as _csv
    import json as _json
    import ashkarr_settle

    site = ashkarr_settle.Site(w)
    plan = ashkarr_settle.PLAN(site)
    sites = ashkarr_settle.place(w, plan)
    placed = [x for x in sites if x["tile"] is not None]
    starved = [x for x in sites if x["tile"] is None]
    edges, links = ashkarr_settle.roads(w, sites, {"StoneRoad": 1, "DirtRoad": 2})
    print("settlements %d placed, %d starved   roads %d links, %d tiles"
          % (len(placed), len(starved), links, len(edges)))
    for x in starved:
        print("   🔴 STARVED  %-30s %s" % (x["name"], x["why"]))

    geo, n = w["geo"], w["n"]
    temp = temperature_curve(w["arc"], w["elev"])
    rain = np.clip(18.0 + 1650.0 * np.clip(w["rain_src"] / 2.6, 0, 1) ** 2.2, 12, 4800)
    rain[w["sea"]] = 90
    reg = {}
    for name, kind, tiles in w["regions"]:
        for t in tiles:
            reg.setdefault(int(t), name)

    # ⭐ The player's home, resolved from the authored lat/lon (see HOME_LATLON).
    hla, hlo = math.radians(HOME_LATLON[0]), math.radians(HOME_LATLON[1])
    hv = np.array([math.cos(hla) * math.cos(hlo), math.sin(hla),      # y is the pole,
                   math.cos(hla) * math.sin(hlo)])                    # per worldgeom
    home = int(np.argmax(geo.vec @ hv))
    if w["biome"][home] != "ExtremeDesert" or w["sea"][home]:
        raise SystemExit("🔴 THE SETDOWN moved: tile %d is now %s. The home site is a "
                         "decision, not an output - re-site it deliberately."
                         % (home, w["biome"][home]))
    print("home       t%d %s  %s %dm  arc %.1f"
          % (home, HOME_NAME, w["biome"][home], round(w["elev"][home]), w["arc"][home]))

    hilly, swamp = hilliness(w, reg), swampiness(w)

    with open(BUNDLE + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        wr = _csv.writer(fh)
        wr.writerow(["tile", "lat", "lon", "arc", "bearing", "elev_m", "temp_c",
                     "rain_mm", "biome", "water", "river_flow", "region",
                     "hilliness", "swampiness"])
        for t in range(n):
            wr.writerow([t, round(float(geo.lat[t]), 4), round(float(geo.lon[t]), 4),
                         round(float(w["arc"][t]), 2), round(float(w["bear"][t]), 2),
                         int(round(w["elev"][t])), round(float(temp[t]), 1),
                         int(round(rain[t])), w["biome"][t], int(bool(w["sea"][t])),
                         int(w["acc"][t]) if w["chan"][t] else 0, reg.get(t, ""),
                         int(hilly[t]), round(float(swamp[t]), 3)])

    with open(BUNDLE + "_settlements.csv", "w", newline="", encoding="utf-8") as fh:
        wr = _csv.writer(fh)
        wr.writerow(["id", "faction_def", "faction", "name", "tile", "lat", "lon",
                     "arc", "biome", "why"])
        for i, x in enumerate(placed):
            t = x["tile"]
            wr.writerow([i, x["faction"], FACTION_LABEL.get(x["faction"], x["faction"]),
                         x["name"], t, round(float(geo.lat[t]), 3),
                         round(float(geo.lon[t]), 3), round(float(w["arc"][t]), 1),
                         w["biome"][t], x["why"]])

    with open(BUNDLE + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        wr = _csv.writer(fh)
        wr.writerow(["kind", "a", "b", "def"])
        for t in np.nonzero(w["chan"])[0]:
            d = w["down"][t]
            if d < 0 or not (w["chan"][d] or w["sea"][d]):
                continue
            a = w["acc"][t]
            wr.writerow(["river", int(t), int(d),
                         "HugeRiver" if a > 3000 else "LargeRiver" if a > 1200
                         else "River" if a > 300 else "Creek"])
        for a, b, g in edges:
            wr.writerow(["road", a, b, "StoneRoad" if g == 1 else "DirtRoad"])

    meta = {"planet": "Ash'karr — The Sundered", "tiles": n, "substellar": [0.0, 0.0],
            "water_pct": round(100.0 * float(w["sea"].sum()) / n, 2),
            "regions": [r[0] for r in w["regions"]],
            "factions": sorted({x["faction"] for x in placed}),
            "faction_labels": FACTION_LABEL,
            "settlements": len(placed), "starved": [x["name"] for x in starved],
            "startingTile": home, "start": {"tile": home, "name": HOME_NAME,
                                            "lat": round(float(geo.lat[home]), 4),
                                            "lon": round(float(geo.lon[home]), 4),
                                            "arc": round(float(w["arc"][home]), 1),
                                            "bearing": round(float(w["bear"][home]), 1),
                                            "biome": w["biome"][home],
                                            "elev_m": int(round(w["elev"][home])),
                                            "temp_c": round(float(temp[home]), 1),
                                            "rain_mm": int(round(rain[home]))}}
    with open(BUNDLE + "_meta.json", "w", encoding="utf-8") as fh:
        _json.dump(meta, fh, indent=1, ensure_ascii=False)
    print("bundle -> %s_{tiles,settlements,links,meta}.*" % BUNDLE)


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
    write_bundle(w)
