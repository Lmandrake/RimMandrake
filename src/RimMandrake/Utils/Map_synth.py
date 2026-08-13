#!/usr/bin/env python3
"""
Map_synth.py  —  synthesize plausible player-style base maps  (practice input)
==============================================================================

WHY THIS EXISTS
---------------
The task was to download a variety of *player map images* to practice on. In
this session that's blocked three ways: WebSearch isn't supported on this model,
direct web fetch is egress-blocked (only an institutional host is allowlisted), and the
project's usual fallback (the Fetcher manual-retrieval system) isn't mounted
here. Rather than stall, this script FABRICATES a small variety of plausible,
lightly-built maps to serve as the improver agent's practice substrate. Each is
saved as a semantic terrain grid (mapkit.GameMap JSON) + a rendered PNG in
../src/RimMandrake/mapsynth/.

These are honest stand-ins, NOT real downloaded saves. They are biased toward
the campaign's "mostly desert, volcanic, rare water" world (biome_terrain_palette
.md) and kept sparse on structures — exactly the "few existing structures" input
requested — so the improver has room to work.

Deterministic (seeded) so runs are reproducible.

USAGE
-----
  python3 Map_synth.py [--out ../player_maps] [--size 120] [--scale 4]
"""

import os
import sys
import math
import random
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapkit import GameMap, render  # noqa: E402


# ---- lightweight value-noise (no numpy dependency needed) -----------------
def value_noise(w, h, freq, seed):
    """Smooth 2D value noise in [0,1] via bilinear-interpolated random grid."""
    rnd = random.Random(seed)
    gw, gh = max(2, int(w * freq)) + 2, max(2, int(h * freq)) + 2
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]

    def smooth(t):
        return t * t * (3 - 2 * t)

    out = [[0.0] * w for _ in range(h)]
    for z in range(h):
        fy = z / w * gw * (w / w)  # keep aspect roughly square
        fy = z * (gh - 2) / max(1, h)
        y0 = int(fy)
        ty = smooth(fy - y0)
        for x in range(w):
            fx = x * (gw - 2) / max(1, w)
            x0 = int(fx)
            tx = smooth(fx - x0)
            v00 = g[y0][x0]
            v10 = g[y0][x0 + 1]
            v01 = g[y0 + 1][x0]
            v11 = g[y0 + 1][x0 + 1]
            a = v00 + (v10 - v00) * tx
            b = v01 + (v11 - v01) * tx
            out[z][x] = a + (b - a) * ty
    return out


def octave_noise(w, h, seed, octaves=4, base_freq=0.04):
    acc = [[0.0] * w for _ in range(h)]
    amp, freq, norm = 1.0, base_freq, 0.0
    for o in range(octaves):
        n = value_noise(w, h, freq, seed + o * 101)
        for z in range(h):
            for x in range(w):
                acc[z][x] += n[z][x] * amp
        norm += amp
        amp *= 0.5
        freq *= 2.0
    for z in range(h):
        for x in range(w):
            acc[z][x] /= norm
    return acc


def ridge(w, h, seed):
    """Distance-to-a-smooth-meandering-centerline field (for rivers/roads).

    The centerline is a sum of two fixed-frequency sines (continuous in x), so
    the resulting band is unbroken — earlier per-column random frequencies made
    it dash apart.
    """
    rnd = random.Random(seed)
    phase1 = rnd.uniform(0, math.tau)
    phase2 = rnd.uniform(0, math.tau)
    f1 = rnd.uniform(0.8, 1.4)
    f2 = rnd.uniform(2.0, 3.2)
    amp1 = h * rnd.uniform(0.14, 0.20)
    amp2 = h * rnd.uniform(0.03, 0.06)
    ymid = h * rnd.uniform(0.40, 0.60)
    field = [[1.0] * w for _ in range(h)]
    for x in range(w):
        t = x / w * math.tau
        cy = (ymid
              + amp1 * math.sin(phase1 + t * f1)
              + amp2 * math.sin(phase2 + t * f2))
        for z in range(h):
            field[z][x] = abs(z - cy)
    return field


# ---------------------------------------------------------------------------
# MAP RECIPES  — each returns a GameMap. Kept structure-light on purpose.
# ---------------------------------------------------------------------------
def map_desert_flats(w, h, seed=1):
    """Open desert with dune fields + a couple rock outcrops. Very few builds."""
    gm = GameMap(w, h, fill="Sand", name="desert_flats")
    n = octave_noise(w, h, seed, octaves=4, base_freq=0.05)
    rock = octave_noise(w, h, seed + 7, octaves=3, base_freq=0.06)
    for z in range(h):
        for x in range(w):
            v = n[z][x]
            if v > 0.62:
                gm.set(x, z, "SoftSand")
            elif v < 0.33:
                gm.set(x, z, "Gravel")
            if rock[z][x] > 0.80:
                gm.set(x, z, "AB_ForsakenRock")
    # a tiny abandoned shack (few walls) so it's not utterly empty
    bx, bz = int(w * 0.72), int(h * 0.30)
    for dx in range(4):
        gm.add_feature("structure", bx + dx, bz, "ancient wall")
        gm.add_feature("structure", bx + dx, bz + 3, "ancient wall")
    gm.meta["blurb"] = "Open desert basin, dune fields NW, rock scatter, one ruined shack SE."
    return gm


def map_river_valley(w, h, seed=2):
    """Desert cut by a shallow river; fertile banks. No player base."""
    gm = GameMap(w, h, fill="Sand", name="river_valley")
    n = octave_noise(w, h, seed, octaves=4, base_freq=0.05)
    rfield = ridge(w, h, seed + 3)
    for z in range(h):
        for x in range(w):
            d = rfield[z][x]
            if d < 1.2:
                gm.set(x, z, "WaterMovingChestDeep")
            elif d < 2.6:
                gm.set(x, z, "WaterMovingShallow")
            elif d < 4.5:
                gm.set(x, z, "SoilRich" if n[z][x] > 0.5 else "Soil")
            elif d < 6.5:
                gm.set(x, z, "Soil" if n[z][x] > 0.55 else "Sand")
            else:
                if n[z][x] > 0.66:
                    gm.set(x, z, "SoftSand")
                elif n[z][x] < 0.30:
                    gm.set(x, z, "Gravel")
    gm.meta["blurb"] = "A rare river crosses the map; narrow fertile banks; dry beyond."
    return gm


def map_volcanic_shelf(w, h, seed=3):
    """Volcanic terrain: obsidian/lava flats with a lava tongue. Hostile, empty."""
    gm = GameMap(w, h, fill="AB_VolcanicGravel", name="volcanic_shelf")
    n = octave_noise(w, h, seed, octaves=4, base_freq=0.055)
    lava = ridge(w, h, seed + 5)
    for z in range(h):
        for x in range(w):
            v = n[z][x]
            if v > 0.60:
                gm.set(x, z, "AB_SolidifiedLava")
            elif v < 0.32:
                gm.set(x, z, "AB_Obsidian")
            d = lava[z][x]
            if d < 1.4:
                gm.set(x, z, "AB_LiquidLava")
            elif d < 2.6:
                gm.set(x, z, "AB_SolidifiedLava")
    gm.meta["blurb"] = "Cooling lava shelf; a live lava tongue; obsidian pans. No structures."
    return gm


def map_coastal_mesa(w, h, seed=4):
    """A saltwater coast on one edge + a mountain (rock) mass on another."""
    gm = GameMap(w, h, fill="Sand", name="coastal_mesa")
    n = octave_noise(w, h, seed, octaves=4, base_freq=0.05)
    mtn = octave_noise(w, h, seed + 9, octaves=3, base_freq=0.045)
    for z in range(h):
        for x in range(w):
            # ocean along the west edge, depth by distance from x=0
            if x < w * 0.18:
                depth = (w * 0.18 - x) / (w * 0.18)
                if depth > 0.55:
                    gm.set(x, z, "WaterOceanDeep")
                else:
                    gm.set(x, z, "WaterOceanShallow")
                continue
            # mountain mass NE corner
            m = mtn[z][x] + 0.4 * (x / w) + 0.3 * (z / h)
            if m > 1.05:
                gm.set(x, z, "RockFace")
            elif m > 0.92:
                gm.set(x, z, "RockRubble")
            else:
                v = n[z][x]
                if v > 0.63:
                    gm.set(x, z, "SoftSand")
                elif v < 0.34:
                    gm.set(x, z, "Gravel")
    gm.meta["blurb"] = "Saltwater coast (W), a rock massif (NE). Sandy interior, unbuilt."
    return gm


RECIPES = {
    "desert_flats": map_desert_flats,
    "river_valley": map_river_valley,
    "volcanic_shelf": map_volcanic_shelf,
    "coastal_mesa": map_coastal_mesa,
}


def main():
    ap = argparse.ArgumentParser(description="synthesize player-style base maps")
    ap.add_argument("--out", default=None)
    ap.add_argument("--size", type=int, default=120)
    ap.add_argument("--scale", type=int, default=4)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(here))),
                       "src", "RimMandrake", "mapsynth")
    os.makedirs(out, exist_ok=True)

    made = []
    for i, (nm, fn) in enumerate(RECIPES.items(), 1):
        gm = fn(args.size, args.size, seed=i * 13 + 1)
        jpath = os.path.join(out, "%s.map.json" % nm)
        ppath = os.path.join(out, "%s.png" % nm)
        gm.save_json(jpath)
        render(gm, ppath, scale=args.scale,
               title="PLAYER MAP (synth): %s — %s" % (nm, gm.meta.get("blurb", "")))
        made.append((nm, jpath, ppath, gm.meta.get("blurb", "")))
        print("built %-16s  %dx%d  -> %s" % (nm, gm.w, gm.h,
                                             os.path.basename(ppath)))

    # a README so the provenance of these is unambiguous
    with open(os.path.join(out, "README.md"), "w") as fh:
        fh.write("# player_maps/ — practice base maps\n\n")
        fh.write("These are **synthesized** plausible player-style maps, not "
                 "downloaded saves (web access was blocked in the authoring "
                 "session). Each is a semantic terrain grid "
                 "(`*.map.json`, loadable by `mapkit.GameMap`) plus a rendered "
                 "PNG. Biased toward the campaign's mostly-desert/volcanic world "
                 "and kept structure-light so the improver agent has room to "
                 "work.\n\n")
        for nm, _, ppath, blurb in made:
            fh.write("- **%s** — %s\n" % (nm, blurb))
    print("\nwrote %d maps + README to %s" % (len(made), out))


if __name__ == "__main__":
    main()
