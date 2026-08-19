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
# 3. ASH'KARR ITSELF. Everything below is a decision, not a parameter.
# ===========================================================================
def build():
    rng = np.random.default_rng(SEED)
    grid = WorldGrid(SRC)
    geo = worldgeom.Geometry(grid.tiles)
    n, V = grid.tiles, geo.vec
    nbl = [geo.neighbours(t) for t in range(n)]

    # theta: degrees from the substellar point at (0,0). THE planetary coordinate.
    sub = np.array([1.0, 0.0, 0.0])
    th = np.degrees(np.arccos(np.clip(V.dot(sub), -1, 1)))
    # bearing around the substellar point, so features can be placed "on the SE limb"
    bearing = np.degrees(np.arctan2(V[:, 1], V[:, 2]))

    # 🔑 THE ANTI-CIRCLE. Every round thing on the old map came from thresholding a
    # RADIAL quantity - distance from a centre, or angle from the substellar point.
    # So the coordinate itself is warped before anything is thresholded against it,
    # and every hand-placed mass is warped the same way. Nothing on this planet is
    # allowed to be a function of a clean radius.
    warp_a = fbm(V, rng, freq0=4.2, octaves=4)
    warp_b = fbm(V, rng, freq0=8.5, octaves=4)
    warp_c = fbm(V, rng, freq0=15.0, octaves=3)
    lobe = fbm(V, rng, freq0=2.2, octaves=3)     # continent-scale lobes
    lobe2 = fbm(V, rng, freq0=3.6, octaves=3)
    thb = th + 7.0 * warp_a + 3.0 * warp_b + 1.2 * warp_c   # warped "angle from noon"

    def irregular(field, k=0.35, amp=0.55):
        """Threshold a hand-placed mass through the warp, so it lands as a torn
        patch rather than a disc.

        🔴 MULTIPLICATIVE, deliberately. An ADDITIVE warp leaks: warp_a is unit
        variance everywhere, so `blob + 0.22*warp` painted the Shipyards over 6.7% of
        the planet instead of one cluster. Multiplying keeps a mass strictly inside
        its own cap and only tears its edge."""
        w = 1.0 + amp * warp_a + 0.5 * amp * warp_b + 0.25 * amp * warp_c
        return (field * np.clip(w, 0.0, 2.4)) > k

    print("=== 1. relief ===")
    cont = fbm(V, rng, freq0=1.5, octaves=7)              # continental swell
    detail = fbm(V, rng, freq0=6.0, octaves=5)            # dissection
    grain = fbm(V, rng, freq0=16.0, octaves=4)            # meander grain
    ranges = ridged(V, rng, freq0=2.6, octaves=6)         # MANY ranges, not one spine

    # The Anvil: the substellar plateau. High, dead flat, the rain shadow.
    anvil = blob(V, 0, 0, 46, falloff=1.4)

    # Hand-placed massifs. Named, and sited so the big rivers have somewhere to be
    # born NEAR the seas - the docs want rivers short and mountain-fed.
    MASSIFS = [
        # (name,           lat,  lon, radius, height)
        # 🔑 Sited so that the water works. Rain condenses at ALTITUDE, and only on
        # the day side, so a massif on the night face feeds nothing and a sea with no
        # massif upwind of it gets no rivers. The first draft put the biggest peaks
        # in the dark and Sarr'khet came out with no inflow at all.
        ("Kadresh Spine",   42,  -48,  30, 3300),   # ⭐ the Sarr'khet watershed
        ("Thal Ridge",     -28,  -40,  26, 2900),   # ⭐ its southern half
        ("Ubrekk Massif",  -42,   88,  26, 3000),   # ⭐ the Ma'kel watershed
        ("Sorrow Teeth",    28,  100,  22, 2600),   # east limb, northern
        ("Vaal Horns",       8,   36,  16, 1700),   # inner dayside, isolated, dry
        ("The Gray Wall",   58,  150,  20, 1300),   # night-facing, feeds nothing
        ("Kesh Knuckles",  -56,  -16,  17, 1900),   # southern dayside, isolated
    ]
    daylit = np.clip((150.0 - th) / 90.0, 0.30, 1.0)
    elev = (900.0 * cont + 260.0 * detail
            + 620.0 * np.clip(ranges, 0, None) * daylit
            + 700.0 * anvil + 62.0 * grain)
    for name, la, lo, rad, hgt in MASSIFS:
        b = blob(V, la, lo, rad, falloff=1.7)
        elev += hgt * b * (0.55 + 0.75 * np.clip(ranges, 0, 1.6))   # crested, not domed

    print("=== 2. the three seas ===")
    # 🔴 Owner: ~25% water (accept 22-28%), EXACTLY three connected bodies, elongated
    # and torn, near the terminator but NOT a ring, and one out on the night side.
    # Each is built from a great-circle SPINE, so it comes out long instead of round.
    # 🔴 Owner: near the terminator but NOT a ring. So the two big ones are
    # deliberately UNLIKE each other - Sarr'khet is northern and sits inside the
    # terminator on the day side, Ma'kel Reach is southern and sits outside it on the
    # dark side. Neither runs pole to pole, and they do not mirror.
    SEAS = [
        ("Sarr'khet", [(58, -98), (36, -84), (14, -74), (-8, -64), (-24, -50)], 17.4),
        ("Ma'kel Reach", [(-64, 104), (-46, 88), (-24, 86), (-6, 96), (10, 106)], 16.4),
        ("The Black Mirror", [(52, 150), (34, 166), (16, -177)], 14.4),
    ]
    coast_big = fbm(V, rng, freq0=3.0, octaves=4)
    coast_mid = fbm(V, rng, freq0=7.5, octaves=4)
    coast_fine = fbm(V, rng, freq0=16.0, octaves=3)
    sea = np.zeros(n, bool)
    sea_id = np.full(n, -1, np.int8)
    for i, (name, spine, width) in enumerate(SEAS):
        d = arc_dist(V, spine)
        # ⭐ the COASTLINE is the noise, not the distance. Three scales: lobes and
        # gulfs, headlands, then a per-tile bite. A smooth threshold is a disc.
        w = (width * (1.0 + 0.62 * coast_big) + 7.0 * coast_mid + 3.4 * coast_fine)
        m = d < np.clip(w, 1.0, 44.0)
        sea |= m
        sea_id[m & (sea_id < 0)] = i
    # 🔴 EXACTLY three bodies. Noise that tears a coastline also throws islands of
    # water clear of it; anything not one of the three biggest is dry land.
    keep = np.zeros(n, bool)
    for i in range(len(SEAS)):
        m = sea_id == i
        if not m.any():
            continue
        comps = components(m, nbl)
        keep[comps[0]] = True          # the body itself; its splinters are islands
    sea_id[~keep] = -1
    sea = keep

    print("=== 3. hydrology ===")
    # Rain condenses at ALTITUDE and at the terminator seam, and NEVER on the night
    # side, where it is locked as ice. Owner's ruling, 2026-08-17.
    seam = np.exp(-((th - 86.0) / 44.0) ** 2)
    alt = np.clip((elev - 1100.0) / 1800.0, 0, 1.6)
    seaward = np.clip(1.0 - bfs_dist(np.nonzero(sea)[0], nbl, n, cap=40) / 26.0, 0, 1)
    dayside = np.clip((112.0 - th) / 26.0, 0, 1)
    rain_src = (7.0 * alt ** 1.5 * (0.25 + 1.0 * seam) + 1.5 * seam * seaward
                + 0.10 * seaward) * dayside
    rain_src = np.clip(rain_src, 0.02, None)

    elev[sea] = -40.0 - 300.0 * np.clip(-coast_big[sea], 0, 1.4)
    elev[~sea] = np.clip(elev[~sea], 12.0, 3550.0)
    for cycle in range(4):
        filled = fill_depressions(elev, nbl, sea)
        down, acc = flow(filled, nbl, rain_src, sea)
        cut = 46.0 * np.log1p(acc) * np.clip(elev / 900.0, 0.15, 3.0)
        elev[~sea] = np.clip(elev[~sea] - cut[~sea], 12.0, 3550.0)
        print("    erosion pass %d: max cut %.0f m, channels>%d = %d"
              % (cycle + 1, cut.max(), 105, int((acc > 105).sum())))
    filled = fill_depressions(elev, nbl, sea)
    down, acc = flow(filled, nbl, rain_src, sea)

    # channels: enough accumulated flow, on the dayside, and not in the dead centre
    need = 105.0 + 620.0 * np.clip((72.0 - th) / 50.0, 0, 1) ** 1.6
    chan = (acc > need) & (~sea) & (th < 118.0)
    print("    channel tiles %d" % chan.sum())

    # deltas: where a big channel meets the sea, the last few tiles fan out and go salt
    # 🔑 "fan out into salty deltas" - the mouth is not a point. Every trunk that
    # reaches the sea spreads a fan two to three tiles deep along the shore, biased
    # to LOW ground, which is where an alluvial fan actually goes.
    mouths = [int(t) for t in np.nonzero(chan)[0]
              if down[t] >= 0 and sea[down[t]] and acc[t] > 90]
    delta = np.zeros(n, bool)
    for m in mouths:
        reach = 4 if acc[m] > 700 else 3
        front = {m}
        delta[m] = True
        for _ in range(reach):
            nxt = set()
            for t in front:
                for u in nbl[t]:
                    if sea[u] or delta[u]:
                        continue
                    if elev[u] < elev[m] + 190 and th[u] < 128:
                        delta[u] = True
                        nxt.add(u)
            front = nxt
    print("    mouths %d, delta tiles %d" % (len(mouths), delta.sum()))

    print("=== 4. biomes ===")
    riparian = bfs_dist(np.nonzero(chan)[0], nbl, n, cap=9)
    bigriver = bfs_dist(np.nonzero(chan & (acc > 1400))[0], nbl, n, cap=9)
    near_sea = bfs_dist(np.nonzero(sea)[0], nbl, n, cap=9)
    patchy = fbm(V, rng, freq0=7.0, octaves=4)
    patchy2 = fbm(V, rng, freq0=11.0, octaves=3)

    B = ["Desert"] * n
    for t in range(n):
        a, e, r = thb[t], elev[t], riparian[t]
        p, p2 = patchy[t], patchy2[t]
        if sea[t]:
            B[t] = "Ocean"
            continue
        # ---- NIGHT SIDE. 🔴 REBUILT: it was three concentric shells and read as a
        # set of rings round the whole planet. Now the dark is ONE mass - the
        # forsaken crags - and everything else is a lobe or a patch inside it, gated
        # on a continent-scale field so no zone ever closes a circle.
        if a > 108 + 16.0 * lobe[t]:
            B[t] = "AB_RockyCrags"
            gate = lobe[t] + 0.55 * lobe2[t]
            if a < 138 and gate > 0.35 and p > -0.6:
                B[t] = "PoisonForest"            # the Ash Verge: three lobes, not a band
            elif 124 < a < 162 and gate < -0.45 and p2 > -0.4:
                B[t] = "AB_MycoticJungle"        # the Long Dark's fungal quarter
                if p2 > 1.1:
                    B[t] = "BMT_FungalForest"
            if p2 > 1.5 and gate > 0.9:
                B[t] = "HorrorWastes"            # patches only, and rare
            if near_sea[t] < 3 and a > 130:
                B[t] = "AB_PropaneLakes"         # hydrocarbon shore of the Black Mirror
            if a > 150 and p2 > 1.75:
                B[t] = "Glowforest" if p > 0.3 else "BMT_CrystalCaverns"
            if a > 145 and p < -1.5 and p2 < -0.9:
                B[t] = "BMT_EarthenDepths"
        # ---- THE WATER MARGIN: narrow, fierce, and only here
        elif delta[t]:
            # the salt delta: mangrove in the wet channels, swamp in the pools, and
            # bare evaporite where the fan has already died
            B[t] = ("AB_MiasmicMangrove" if p2 > -0.2 else
                    "COMIGO_GreaterSwamp_Tropical" if p > 0.8 else "Wasteland")
        elif r <= 1:
            # 🔑 owner: "coat the rivers in jungles". This is the ONLY green on the
            # planet: a hard line one tile wide, two on a trunk, and nothing beyond.
            B[t] = "AB_FeraliskInfestedJungle"
        elif r <= 2 and bigriver[t] <= 2:
            B[t] = "ZBiome_DesertOasis"
        elif near_sea[t] <= 2:
            B[t] = "AridShrubland" if a > 66 + 10 * lobe[t] else "ZBiome_Badlands"
        # ---- THE DAYSIDE
        elif a < 26:
            B[t] = "ExtremeDesert"
        elif a < 52:
            B[t] = "ExtremeDesert" if p < 0.55 else "Desert"
        elif a < 84 + 9 * lobe[t]:
            B[t] = "Desert" if p < 0.9 else "ZBiome_Badlands"
        else:
            B[t] = "AridShrubland" if p > 0.2 - 0.5 * lobe2[t] else "Desert"
        # dissected highland reads as badlands wherever it is steep
        if B[t] in ("Desert", "AridShrubland") and e > 1500 and p2 > 0.4:
            B[t] = "ZBiome_Badlands"
        # ocular forest: on the peaks, at the river heads, bleeding streams outward
        if e > 2300 and a < 118 and acc[t] > 12 and p2 > 0.2:
            B[t] = "AB_OcularForest"

    # ---- ONE volcanic region: the Hellrim, packed, on the south-east limb.
    # ⭐ ONE volcanic province, and it is a RIFT, not a crater: built off a spine so
    # it comes out long, and every internal band is torn by its own noise so the
    # province does not read as concentric rings.
    hd = arc_dist(V, [(-16, 30), (-32, 44), (-48, 62)])
    hell = np.clip(1.0 - hd / 17.0, 0, 1) ** 1.25
    hf = hell * np.clip(1.0 + 0.55 * warp_a + 0.30 * warp_b, 0, 2.2)
    for t in np.nonzero(hf > 0.14)[0]:
        if sea[t] or th[t] > 112:
            continue
        v = hf[t]
        if v > 0.80 + 0.10 * patchy2[t]:
            B[t] = "AB_PyroclasticConflagration"
        elif v > 0.58 + 0.14 * warp_c[t]:
            B[t] = "LavaField" if patchy2[t] > 0.1 else "Volcano"
        elif v > 0.36 + 0.16 * warp_b[t]:
            B[t] = "Scarlands" if patchy2[t] > 0.5 else "AB_TarPits"
        elif v > 0.20 and patchy2[t] > 0.9:
            B[t] = "AB_TarPits"

    # ---- ONE hand-seeded cluster: the Shipyards.
    ship = blob(V, 20, -34, 11, falloff=1.0)
    for t in np.nonzero(irregular(ship, 0.34, 0.60))[0]:
        if not sea[t]:
            B[t] = "AB_MechanoidIntrusion"
    # ---- the droid ground and the graveyard, as masses not specks
    wd = arc_dist(V, [(4, -26), (-10, -14), (-26, -6)])
    waste = np.clip(1.0 - wd / 15.0, 0, 1) ** 1.2
    for t in np.nonzero(irregular(waste, 0.34, 0.62))[0]:
        if not sea[t] and B[t] in ("Desert", "ExtremeDesert", "ZBiome_Badlands"):
            B[t] = "Wasteland"
    grave = blob(V, 46, 18, 10, falloff=1.2)
    for t in np.nonzero(irregular(grave, 0.45, 0.50))[0]:
        if not sea[t] and th[t] < 100:
            B[t] = "AB_GallatrossGraveyard"
    geys = blob(V, -20, 128, 8, falloff=1.2)
    for t in np.nonzero(irregular(geys, 0.50, 0.45))[0]:
        if not sea[t]:
            B[t] = "IronScruff_PrimordialGeysers"

    B = despeckle(B, nbl, minsize=7)
    # 🔴 Sea spec req 5: water tile <=> elevation <= 0 AND a water biome. Despeckle
    # works on labels alone and will happily drown a two-tile island, so the two
    # representations are forced back into agreement here, elevation winning.
    for t in range(n):
        if sea[t]:
            B[t] = "Ocean"
        elif B[t] == "Ocean":
            B[t] = "ZBiome_Badlands"

    # ---- Ash'karr names itself. The old painter left the planet labelled with the
    # vanilla source world's regions (Josephine's Pride Mountains, Isle Ballerrei...).
    regions = []
    for i, (name, spine, width) in enumerate(SEAS):
        regions.append((name, "sea", np.nonzero(sea_id == i)[0]))
    regions.append(("The Anvil", "waste", np.nonzero((thb < 27) & ~sea)[0]))
    for name, la, lo, rad, hgt in MASSIFS:
        b = blob(V, la, lo, rad, falloff=1.7)
        regions.append((name, "massif", np.nonzero((b > 0.40) & ~sea)[0]))
    regions.append(("The Hellrim", "waste",
                    np.nonzero((hf > 0.30) & ~sea)[0]))
    regions.append(("The Shipyards", "waste", np.nonzero(irregular(ship, 0.34, 0.60) & ~sea)[0]))
    regions.append(("The Rust Flats", "waste", np.nonzero(irregular(waste, 0.34, 0.62) & ~sea)[0]))
    regions.append(("The Gallatross Boneyard", "waste", np.nonzero(irregular(grave, 0.45, 0.50))[0]))
    regions.append(("The Ash Verge", "waste",
                    np.nonzero((thb > 108) & (thb <= 138) & ~sea & (lobe > 0.0))[0]))
    regions.append(("The Long Dark", "waste",
                    np.nonzero((thb > 124) & (thb <= 162) & ~sea & (lobe < 0.0))[0]))
    regions.append(("The Forsaken Crags", "waste",
                    np.nonzero((thb > 152) & ~sea)[0]))
    regions.append(("The Salt Gate", "waste", np.nonzero(delta)[0]))
    regions = [(nm, kd, tl) for nm, kd, tl in regions if len(tl) >= 6]

    return dict(regions=regions, grid=grid, geo=geo, n=n, V=V, th=th, elev=elev, sea=sea, sea_id=sea_id,
                chan=chan, acc=acc, down=down, biome=B, rain_src=rain_src,
                riparian=riparian, delta=delta, nbl=nbl, seas=SEAS, massifs=MASSIFS,
                filled=filled)


def report(w):
    n, nbl, sea = w["n"], w["nbl"], w["sea"]
    comps = components(sea, nbl)
    print("\n--- ACCEPTANCE ---")
    print("water      %d tiles = %.1f%%   (owner: 22-28%%)"
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
