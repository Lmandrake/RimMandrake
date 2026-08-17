#!/usr/bin/env python3
"""Paint Ash'karr the Sundered onto WORLDMAP_gen.rws.

Every region is a predicate over (arc, bearing, elevation), where

    arc     = acos(cos(long) * cos(lat))   degrees from the substellar point (0,0)
    bearing = atan2(sin(lat), cos(lat) * sin(long))   degrees around that point

Bearing 0 = toward long +90 (the GRAY flank, downwind), 180 = toward long -90
(the TWILIGHT flank, upwind). The superrotating wind runs toward the Gray Sea, which
is why the Sunreach lobe is on the Gray flank and the Nightspill on the Twilight one.

Coordinates come from `world/world_tiles_lada.csv`, exported once by
`jawa/world_tile_export`; the .rws never stores them.

Rulings implemented here live in design/Jawa/worldbuilding/worldgen_interactive_def.md.

    python3 src/RimMandrake/Utils/paint_ashkarr.py [--dry]
"""
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldmap import WorldGrid, WorldObjects, DECODE

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC = os.path.join(REPO, "world", "WORLDMAP_source.rws")
DEST = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
TILES = os.path.join(REPO, "world", "world_tiles_lada.csv")
GAME_SAVES = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
              "RimWorld by Ludeon Studios/Saves")

# Owner's ruled endpoints. Generated world runs +67.9 .. -105.7; we remap onto these.
T_HOT, T_COLD = 80.0, -80.0

random.seed(20260816)


def angdiff(a, b):
    """Smallest absolute difference between two bearings, degrees."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def lobe(arc, bear, arc0, bear0, arc_r, bear_r):
    """Smooth 0..1 falloff of an elliptical lobe centred on (arc0, bear0)."""
    da = (arc - arc0) / arc_r
    db = angdiff(bear, bear0) / bear_r
    d = math.hypot(da, db)
    return max(0.0, 1.0 - d * d)


def sphere_dist(arc1, bear1, arc2, bear2):
    """Angular distance between two points given as (arc from substellar, bearing)."""
    a1, a2 = math.radians(arc1), math.radians(arc2)
    return math.degrees(math.acos(max(-1.0, min(1.0,
        math.cos(a1) * math.cos(a2)
        + math.sin(a1) * math.sin(a2) * math.cos(math.radians(bear1 - bear2))))))


def wobble(x, terms):
    """Sum of sinusoids - what stops a coastline looking like a rectangle."""
    return sum(a * math.sin(k * math.radians(x) + ph) for a, k, ph in terms)


# Each sea is a SCALAR FIELD thresholded at zero, not a bearing window. The
# harmonics give bays, peninsulas, headlands and the odd offshore island.
TWILIGHT = dict(arc=91.0, bear=170.0, r=20.0,
                bt=[(0.26, 3, 0.7), (0.17, 5, 2.4), (0.11, 7, 4.1), (0.07, 11, 1.2)],
                at=[(0.30, 2, 1.9), (0.18, 4, 0.3)])
GRAY = dict(arc=92.0, bear=8.0, r=14.0,
            bt=[(0.30, 3, 2.2), (0.18, 6, 0.9), (0.12, 9, 3.3)],
            at=[(0.26, 3, 0.6), (0.16, 5, 2.8)])
SCALD_S = dict(arc=35.0, bear=185.0, r=9.5,
               bt=[(0.16, 4, 1.4), (0.10, 7, 3.0)], at=[(0.10, 3, 2.1)])


def sea_field(arc, bear, s):
    """> 0 inside the water, 1.0 at the centre, 0 exactly on the coast."""
    d = sphere_dist(arc, bear, s["arc"], s["bear"])
    r = s["r"] * (1.0 + wobble(bear, s["bt"]) + wobble(arc * 3.0, s["at"]))
    return 1.0 - d / max(2.0, r)


def load_geometry():
    rows = {}
    for r in csv.DictReader(open(TILES)):
        lat = math.radians(float(r["lat"]))
        lon = math.radians(float(r["long"]))
        arc = math.degrees(math.acos(max(-1.0, min(1.0, math.cos(lon) * math.cos(lat)))))
        bear = math.degrees(math.atan2(math.sin(lat), math.cos(lat) * math.sin(lon))) % 360.0
        rows[int(r["tile"])] = (arc, bear)
    return rows


# ---------------------------------------------------------------- the regions
# Each returns a name or None. First match wins, so order is the priority order.

SCALD_ARC, SCALD_BEAR, SCALD_R = 35.0, 185.0, 9.0      # crater sea, Twilight flank
RIM_R = 13.5                                           # its mountain rim
CATHEDRAL_ARC = 11.0                                    # the Rust Cathedral mass


def region_of(t, arc, bear, elev, n1, n2):
    """n1/n2 are per-tile noise in -1..1, used to fray every border."""
    if sea_field(arc, bear, SCALD_S) > 0.0:
        return "scald_sea"
    if sphere_dist(arc, bear, SCALD_S["arc"], SCALD_S["bear"]) < SCALD_S["r"] + 4.2 + 1.5 * n1:
        return "scald_rim"
    ft = sea_field(arc, bear, TWILIGHT)
    fg = sea_field(arc, bear, GRAY)
    if ft > 0.0:
        return "twilight_sea"
    if fg > 0.0:
        return "gray_sea"

    # the volcanic range cradling the western half of the subsolar desert,
    # joining the Scald rim: bulk lies BETWEEN the deep desert and the water.
    if 18.0 < arc < 38.0 and angdiff(bear, 185.0) < 66.0 + 8 * n2:
        return "volcanic_range"

    # substellar plateau: flat, high, part machine
    if arc < 20.0 + 2.0 * n1:
        if arc < CATHEDRAL_ARC + 2.5 * n2 and angdiff(bear, 40.0) < 118.0:
            return "cathedral"
        if arc < CATHEDRAL_ARC + 3.0 + 2.5 * n2:
            return "scorch_ring"
        return "plateau"

    # the Fall Line - debris belt downwind of the plateau, Gray flank
    if 24.0 < arc < 62.0 and angdiff(bear, 0.0) < 17.0 + 5 * n2:
        return "fall_line"

    # the Dew Belt - low trough from the Twilight terminator running sunward
    if 52.0 < arc < 92.0 and angdiff(bear, 178.0) < 21.0 + 6 * n1:
        return "dew_belt"

    # The Salt - evaporite flats hugging the Gray Sea's own coast, downwind
    if -0.5 < fg <= 0.0 and angdiff(bear, 18.0) < 36.0:
        return "the_salt"
    if 78.0 < arc < 103.0:
        return "terminator"

    if arc < 40.0:
        return "deep_desert"
    if arc < 58.0:
        return "liveable_ring"
    if arc < 78.0:
        return "outer_dayside"

    # nightside
    if arc < 113.0:
        return "glow_band"             # between the crags and the dark terminator
    if arc > 150.0 and n1 > 0.35:
        return "propane_core"
    if arc > 128.0 and n2 > 0.72:
        return "frozen_sea"
    return "crags"


# biome per region; a list means a weighted scatter
BIOME = {
    "scald_sea":      ["Ocean"],
    "scald_rim":      ["Volcano", "LavaField", "ZBiome_Badlands", "Wasteland"],
    "volcanic_range": ["Volcano", "AB_PyroclasticConflagration", "AB_GallatrossGraveyard",
                       "LavaField", "Wasteland"],
    "cathedral":      ["AB_MechanoidIntrusion"],
    "scorch_ring":    ["Scarlands"],
    "plateau":        ["ExtremeDesert"],
    "fall_line":      ["Wasteland", "ZBiome_Badlands", "Scarlands"],
    "dew_belt":       ["AridShrubland", "Desert", "ZBiome_DesertOasis"],
    "twilight_sea":   ["Ocean"],
    "gray_sea":       ["Ocean"],
    "the_salt":       ["ZBiome_Badlands", "Wasteland"],
    "terminator":     ["PoisonForest", "AB_MycoticJungle", "BMT_FungalForest",
                       "HorrorWastes", "AB_GelatinousSuperorganism", "AB_TarPits",
                       "AB_FeraliskInfestedJungle", "AridShrubland"],
    "deep_desert":    ["ExtremeDesert", "Desert"],
    "liveable_ring":  ["AridShrubland", "Desert"],
    "outer_dayside":  ["AridShrubland", "Wasteland", "Desert"],
    "glow_band":      ["Glowforest", "AB_RockyCrags"],
    "crags":          ["AB_RockyCrags"],
    "propane_core":   ["AB_PropaneLakes"],
    "frozen_sea":     ["SeaIce"],
}
WEIGHT = {
    "scald_rim":      [5, 2, 2, 1],
    "volcanic_range": [5, 3, 2, 2, 3],
    "fall_line":      [6, 3, 1],
    "dew_belt":       [7, 4, 1],
    "the_salt":       [3, 2],
    "terminator":     [3, 3, 2, 2, 2, 1, 1, 17],
    "deep_desert":    [3, 2],
    "liveable_ring":  [6, 2],
    "outer_dayside":  [5, 2, 2],
    "glow_band":      [2, 3],
}
WATER = {"scald_sea", "twilight_sea", "gray_sea", "frozen_sea"}

# 🔴 These ship ONLY a Forest/ worldmap texture set in ReGrowth's BiomesKit pack -
# no Hills/. Give one of them hilliness above flat and BiomesKit finds no material
# and the tile renders MAGENTA. Measured 2026-08-16 off the texture folders.
FLAT_ONLY = {"AB_TarPits", "AB_IdyllicMeadows", "AB_MiasmicMangrove"}

# elevation metres (base, jitter) and hilliness enum per region
# pollution 0..1. Ancient machinery leaks; nothing else on this planet does.
# CALIBRATED: the pristine world's own max is exactly 65535 and its 5% non-zero
# fraction matches its `pollution 0.05` generator setting.
POLL_FULL = 65535.0
POLLUTION = {
    "cathedral":      (0.55, 0.95),
    "scorch_ring":    (0.30, 0.70),
    "fall_line":      (0.08, 0.35),
    "volcanic_range": (0.05, 0.22),
    "the_salt":       (0.04, 0.14),
}
DIRTY_BIOMES = {"PoisonForest": (0.15, 0.45), "AB_TarPits": (0.20, 0.55),
                "HorrorWastes": (0.10, 0.40), "Scarlands": (0.25, 0.60)}

RELIEF = {
    "plateau":        (1450, 90, 1),
    "cathedral":      (1520, 70, 1),
    "scorch_ring":    (1400, 110, 2),
    "scald_sea":      (-350, 0, 0),
    "twilight_sea":   (-350, 0, 0),
    "gray_sea":       (-350, 0, 0),
    "frozen_sea":     (-350, 0, 0),
    "scald_rim":      (2150, 620, 5),
    "volcanic_range": (1950, 700, 5),
    "dew_belt":       (-60, 120, 1),
    "the_salt":       (40, 60, 1),
    "fall_line":      (420, 200, 2),
    "deep_desert":    (600, 260, 2),
    "liveable_ring":  (520, 300, 2),
    "outer_dayside":  (500, 320, 3),
    "terminator":     (380, 300, 3),
    "glow_band":      (430, 260, 3),
    "crags":          (560, 380, 3),
    "propane_core":   (180, 140, 2),
}


def main():
    dry = "--dry" in sys.argv
    geo = load_geometry()
    g = WorldGrid(SRC)
    n = len(g.biome_names())
    assert n == len(geo), "tile count mismatch: save %d, csv %d" % (n, len(geo))

    enc_t = DECODE["tileTemperature"][1]
    enc_r = DECODE["tileRainfall"][1]
    enc_e = DECODE["tileElevation"][1]
    t_arr = g.arrays["tileTemperature"]
    r_arr = g.arrays["tileRainfall"]
    e_arr = g.arrays["tileElevation"]
    h_arr = g.arrays["tileHilliness"]
    p_arr = g.arrays["tilePollution"]
    b_arr = g.arrays["tileBiome"]
    hash_by_biome = g.hash_by_biome

    # generated extremes, so the remap hits the owner's ruled endpoints exactly
    occupied = set()
    wo = WorldObjects(SRC)
    for st in wo.settlements():
        occupied.add(int(str(st.get("tile")).split(",")[0]))
    for k in wo.landmarks():
        tv = k.get("tile") if isinstance(k, dict) else k
        occupied.add(int(str(tv).split(",")[0]))

    temps0 = [g.get("tileTemperature", t) for t in range(n)]
    hot0, cold0 = max(temps0), min(temps0)

    counts = {}
    for t in range(n):
        arc, bear = geo[t]
        n1 = random.uniform(-1, 1)
        n2 = random.uniform(-1, 1)
        reg = region_of(t, arc, bear, g.get("tileElevation", t), n1, n2)
        counts[reg] = counts.get(reg, 0) + 1

        # ---- biome
        opts = BIOME[reg]
        w = WEIGHT.get(reg)
        pick = random.choices(opts, weights=w)[0] if w else opts[0]
        # Ocular forest lives ONLY on mountain tops, in tiny patches
        base_elev, jit, hill = RELIEF[reg]
        elev = base_elev + (random.uniform(-1, 1) * jit if jit else 0)
        if elev > 2400 and random.random() < 0.16:
            pick = "AB_OcularForest"
        b_arr[t] = hash_by_biome[pick]

        # ---- temperature: keep the engine's natural variation, remap the ends,
        #      then add the two lobes and the Dew Belt's trough.
        c = temps0[t]
        c = c * (T_HOT / hot0) if c > 0 else c * (T_COLD / cold0)
        c += 26.0 * lobe(arc, bear, 104.0, 4.0, 26.0, 46.0)     # Sunreach, downwind
        c -= 24.0 * lobe(arc, bear, 74.0, 196.0, 24.0, 40.0)    # Nightspill, upwind
        if reg == "dew_belt":
            c -= 9.0
        if reg in ("scald_rim", "volcanic_range") or elev > 1900:
            c -= 5.5
        c += random.uniform(-1.6, 1.6)
        t_arr[t] = enc_t(max(-95.0, min(92.0, c)))

        # ---- rainfall: it essentially never rains on this planet
        if reg in WATER:
            mm = random.uniform(60, 140)
        elif elev > 1900 and arc < 80.0:
            mm = random.uniform(700, 1500)      # violent rain, dayside peaks only
        elif reg == "dew_belt":
            mm = random.uniform(180, 330)       # fog and dew, not rain
        elif reg == "terminator":
            mm = random.uniform(120, 380)
        elif arc < 80.0:
            mm = random.uniform(0, 35)          # the dayside never rains
        else:
            mm = random.uniform(0, 60)          # nightside: too dry, too cold
        r_arr[t] = enc_r(mm)

        # ---- relief
        e_arr[t] = enc_e(elev)
        hh = hill
        if reg == "crags" and arc > 150:
            hh = max(1, hill - 1)               # worn smooth at the antistellar core
        if elev > 2200:
            hh = 5
        hh = max(0, min(5, hh + (1 if random.random() < 0.18 else 0)))
        if pick in FLAT_ONLY:
            hh = min(hh, 1)
        h_arr[t] = hh

        lo_hi = POLLUTION.get(reg) or DIRTY_BIOMES.get(pick)
        p_arr[t] = int(round(random.uniform(*lo_hi) * POLL_FULL)) if lo_hi else 0

    print("region                tiles")
    for k in sorted(counts, key=lambda x: -counts[x]):
        print("  %-20s %6d  %5.1f%%" % (k, counts[k], 100.0 * counts[k] / n))

    tt = sorted(g.get("tileTemperature", i) for i in range(n))
    water = sum(1 for i in range(n) if g.biome_names()[i] in ("Ocean", "SeaIce"))
    print("\ntemp  min %.1f  p10 %.1f  med %.1f  p90 %.1f  max %.1f C"
          % (tt[0], tt[n//10], tt[n//2], tt[9*n//10], tt[-1]))
    print("water %d tiles (%.1f%%)" % (water, 100.0*water/n))

    if dry:
        print("\n--dry: nothing written")
        return
    g.write(DEST)
    print("\nwrote", DEST)
    for name in ("WORLDMAP_gen.rws",):
        dest = os.path.join(GAME_SAVES, name)
        with open(DEST, "rb") as a, open(dest, "wb") as b:
            b.write(a.read())
        print("deployed", dest)


if __name__ == "__main__":
    main()
