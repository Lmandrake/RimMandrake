#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_climate.py - give Ash'karr a climate instead of a lookup table.

An independent physical review, 2026-08-22, measured what the eye had missed:

  temp_c reproduced  interp(arc) - 5.5 C/km  with residual sd = 0.029 C.
  An arc ring explained 99.70% of ALL temperature variance, and the three seas left
  ZERO thermal signature - mean residual on the 369 coastal land tiles was +0.0015 C,
  identical to the interior.

That is the compass bullseye `the_one_map.md` bans, relocated out of the biome field
and into the temperature field, where nobody was looking. On a tidally locked world the
seas are the DOMINANT moderator, so it is also the worst possible field to make perfect.

WHAT THIS CHANGES, in order, because each step feeds the next:

  1 ELEVATION   4,485 land tiles - 22.3% of the land - sat at exactly 12 m, in blobs of
                1,376 and 1,250 contiguous tiles. That is a clamp, not terrain. Dithered
                with a smooth field so the floor undulates.
  2 SEA TEMP    208 Ocean tiles were liquid down to -22.1 C. Seawater freezes at -2 C and
                `SeaIce` is blacklisted by ruling, so open water is clamped to >= -2 C:
                the sea is the thing that cannot get colder than that.
  3 LAND TEMP   a maritime term - each land tile is pulled toward the temperature of the
                water near it, damped over ~4 hexes - plus a smooth low-frequency field.
                The seas acquire a thermal signature and the ring stops being exact.
  4 RAINFALL    scaled DOWN by distance from water. ⛔ Never up: the owner's rain rulings
                (RAIN_DRY_THE_LOWLANDS_1) dried this planet on purpose and this must not
                quietly re-wet it. Inland peaks simply stop catching what no sea supplied.
  5 SWAMPINESS  was f(biome) exactly - 8 distinct values whose counts matched biome counts
                one for one. Modulated by water proximity and the smooth field.
  6 COLD FLORA  AridShrubland reached arc 138 at -47 C. Shrubs do not photosynthesise in
                the dark at -47 C; those tiles become AB_RockyCrags. Fungal biomes are
                left alone - they have no such excuse to need.

🔴 DETERMINISTIC AND SEEDLESS, and that is not negotiable. The "noise" is a fixed sum of
sinusoids over the tile's own position on the sphere - smooth, spatially correlated like
real climate, and identical on every run. ⛔ There is no seed parameter and there must
never be one: a knob that could produce a second planet is out of scope even if we would
only ever turn it once (`CLAUDE.md`, ONE MAP NOT A GENERATOR).

    python3 src/RimMandrake/Utils/ashkarr_climate.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_climate.py --apply
"""
import argparse
import collections
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")

SEA_FREEZE = -2.0        # C; seawater does not go below this and stay liquid
MARITIME_HOPS = 5        # how far a sea reaches inland
MARITIME_PULL = 0.55     # how much of the way to the sea's temperature, at the coast
TEMP_FIELD = 2.2         # C, amplitude of the smooth field
ELEV_FIELD = 38.0        # m, amplitude of the floor dither
FLOOR = 12.0             # the clamped elevation being broken up
RAIN_REACH = 9           # hexes; beyond this a sea supplies nothing
COLD_FLORA_LIMIT = -15.0  # C; AridShrubland gives up below this

# fixed directions for the smooth field - four wavelengths, no seed, never changed
_DIRS = [(0.31, 0.77, 0.56), (-0.82, 0.19, 0.54), (0.44, -0.63, 0.64), (-0.28, -0.55, -0.79)]
_FREQ = [2.3, 4.1, 7.7, 13.1]
_AMP = [0.55, 0.26, 0.13, 0.06]


def unit(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def field(lat, lon):
    """smooth, spatially correlated, deterministic; roughly -1..1"""
    p = unit(lat, lon)
    v = 0.0
    for (d, f, a) in zip(_DIRS, _FREQ, _AMP):
        v += a * math.sin(f * (p[0] * d[0] + p[1] * d[1] + p[2] * d[2]) * math.pi)
    return v / sum(_AMP)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {int(r["tile"]): r for r in rows}
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]

    water = {t for t, r in T.items() if r["water"] == "1"}
    land = [t for t in T if t not in water]

    def summarise(tag):
        temps = [float(T[t]["temp_c"]) for t in land]
        arcs = [float(T[t]["arc"]) for t in land]
        elev = [float(T[t]["elev_m"]) for t in land]
        # residual of temp against a pure arc+elev model, the thing the review measured
        buckets = collections.defaultdict(list)
        for t in land:
            buckets[round(float(T[t]["arc"]) / 2)].append(
                float(T[t]["temp_c"]) + 5.5 * float(T[t]["elev_m"]) / 1000.0)
        res = []
        for b, vs in buckets.items():
            m = sum(vs) / len(vs)
            res += [v - m for v in vs]
        sd = (sum(x * x for x in res) / len(res)) ** 0.5
        floor_n = sum(1 for e in elev if abs(e - FLOOR) < 0.5)
        cold_sea = sum(1 for t in water if float(T[t]["temp_c"]) < SEA_FREEZE)
        print("  %-7s residual sd %.3f C | %d land tiles at exactly %.0f m | "
              "%d sea tiles below %.0f C" % (tag, sd, floor_n, FLOOR, cold_sea, SEA_FREEZE))
        return sd

    print("MEASURED")
    before_sd = summarise("before")

    # ── 1. elevation floor ────────────────────────────────────────────────────
    bumped = 0
    for t in land:
        e = float(T[t]["elev_m"])
        if abs(e - FLOOR) < 0.5:
            d = ELEV_FIELD * field(float(T[t]["lat"]), float(T[t]["lon"]))
            T[t]["elev_m"] = "%d" % max(1, round(e + d))
            bumped += 1
    print("\n1 ELEVATION   dithered %d tiles off the %.0f m clamp (+/- %.0f m)"
          % (bumped, FLOOR, ELEV_FIELD))

    # ── 2. sea temperature ────────────────────────────────────────────────────
    warmed = 0
    for t in water:
        if float(T[t]["temp_c"]) < SEA_FREEZE:
            T[t]["temp_c"] = "%.1f" % SEA_FREEZE
            warmed += 1
    print("2 SEA TEMP    %d ocean tiles raised to the %.0f C freezing point" % (warmed, SEA_FREEZE))

    # ── 3. land temperature: maritime + smooth field ──────────────────────────
    dist, near_sea_t = {}, {}
    q = collections.deque()
    for t in water:
        dist[t] = 0
        near_sea_t[t] = float(T[t]["temp_c"])
        q.append(t)
    while q:
        x = q.popleft()
        if dist[x] >= MARITIME_HOPS:
            continue
        for n in nb[x]:
            if n not in dist:
                dist[n] = dist[x] + 1
                near_sea_t[n] = near_sea_t[x]
                q.append(n)
    moved = 0
    for t in land:
        base = float(T[t]["temp_c"])
        v = base + TEMP_FIELD * field(float(T[t]["lat"]), float(T[t]["lon"]))
        d = dist.get(t)
        if d is not None and d <= MARITIME_HOPS:
            pull = MARITIME_PULL * math.exp(-(d - 1) / 2.2)
            v += pull * (near_sea_t[t] - base)
        T[t]["temp_c"] = "%.1f" % v
        if abs(v - base) >= 0.1:
            moved += 1
    print("3 LAND TEMP   %d land tiles moved off the ring (maritime pull %.2f over %d hexes,"
          " field +/-%.1f C)" % (moved, MARITIME_PULL, MARITIME_HOPS, TEMP_FIELD))

    # ── 4. rainfall scaled by how far the sea reaches ─────────────────────────
    dried = 0
    for t in land:
        r = float(T[t]["rain_mm"])
        if r <= 0:
            continue
        d = dist.get(t, 99)
        if d > RAIN_REACH:
            k = 0.25
        else:
            k = 1.0 - 0.75 * (d / RAIN_REACH)
        nv = r * max(0.0, min(1.0, k))
        if nv < r - 0.5:
            T[t]["rain_mm"] = "%d" % round(nv)
            dried += 1
    print("4 RAINFALL    %d wet tiles scaled down by distance from a sea (never up)" % dried)

    # ── 5. swampiness ─────────────────────────────────────────────────────────
    sw = 0
    for t in land:
        s = float(T[t]["swampiness"])
        if s <= 0:
            continue
        d = dist.get(t, 99)
        k = 1.0 + 0.35 * field(float(T[t]["lon"]), float(T[t]["lat"]))
        if d <= 3:
            k += 0.25
        nv = max(0.0, min(1.0, s * k))
        if abs(nv - s) >= 0.01:
            T[t]["swampiness"] = "%.2f" % nv
            sw += 1
    print("5 SWAMPINESS  %d tiles broken off the per-biome lookup" % sw)

    # ── 6. cold flora ─────────────────────────────────────────────────────────
    flipped = 0
    for t in land:
        if T[t]["biome"] == "AridShrubland" and float(T[t]["temp_c"]) < COLD_FLORA_LIMIT:
            T[t]["biome"] = "AB_RockyCrags"
            flipped += 1
    print("6 COLD FLORA  %d AridShrubland tiles below %.0f C handed to AB_RockyCrags"
          % (flipped, COLD_FLORA_LIMIT))

    print("\nMEASURED")
    after_sd = summarise("after")
    print("\n  temperature residual sd: %.3f C -> %.3f C  (the review's headline number)"
          % (before_sd, after_sd))

    if not a.apply:
        print("\nplan only - re-run with --apply")
        return
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\nwritten: %s_tiles.csv" % STEM)


if __name__ == "__main__":
    main()
