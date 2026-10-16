#!/usr/bin/env python3
"""Offline proof of the plant draw-order math (GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT).

Owner, 2026-10-16: "if you are more south, you go in front."

Models two printed plant quads as RimWorld 1.6 prints them (Plant.Print -> Printer_Plane.PrintPlane: a square of
side drawSize.x * visualSize centred on the foot + visualSize/2, south edge at y, north edge at y + topBias) and asks,
at every overlapping pixel, which quad is nearer the camera (larger y wins; CutoutPlant writes depth).

  1. VANILLA reproduces the reported bug on measured Rot pairs (different layers, different sizes).
  2. The FIX (constants parsed from RM_PlantDrawOrder.cs, so this cannot drift from the C#) puts the more southern
     foot in front at every overlapping pixel, for random pairs across the measured sizes.
  3. The band never reaches the next layer (Item), including vanilla's snow-overlay lift.
  4. Neighbouring rows stay further apart than the snow lift on maps up to 500 cells, so a snow overlay never
     jumps in front of the next row's plant.
"""
import random
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source" / "RM_PlantDrawOrder.cs"
LAYER = 0.36585367           # Altitudes.LayerSpacing (decompiled 1.6)
SNOW = 0.0003658537          # Plant.Print snow overlay WithYOffset
VANILLA_TILT = 0.1           # Plant.Print topVerticesAltitudeBias

# (layer index, mature visual size) from the 2026-10-04 def dump; drawSize.x is 1 for all of them.
MEASURED = {
    "AB_WitchesOyster": (11, 6.0), "AB_AgaricusDomeCap": (11, 7.0), "AB_LilacBeacon": (11, 3.0),
    "AB_GlowingAgarilux": (15, 4.0), "RM_PaleTree": (15, 6.0), "AB_GiantAgarilux": (17, 6.0),
    "AB_DribblingCap": (17, 12.0), "AB_SlimyPholiota": (17, 5.0), "RM_AgelessCap": (11, 1.6),
}


def constants():
    text = SRC.read_text(encoding="utf-8")
    out = {}
    for name in ("MinLayer", "CommonLayer", "Band", "MaxCarriedOffset"):
        m = re.search(r"public const (?:int|float) " + name + r"\s*=\s*([0-9.]+)f?;", text)
        if not m:
            sys.exit(f"FAIL: constant {name} not found in {SRC}")
        out[name] = float(m.group(1))
    return out


def y_at(z, foot, size, base_y, tilt):
    """Depth of a quad (south edge at foot, side `size`) at world z; None outside it."""
    if z < foot or z > foot + size:
        return None
    return base_y + tilt * (z - foot) / size


def front(a, b, base_a, base_b, tilt_a, tilt_b):
    """Which of two quads (foot, size) is in front where they overlap: 'a', 'b', 'mixed' or None (no overlap)."""
    lo, hi = max(a[0], b[0]), min(a[0] + a[1], b[0] + b[1])
    if lo >= hi:
        return None
    seen = set()
    for i in range(1, 50):
        z = lo + (hi - lo) * i / 50
        ya, yb = y_at(z, *a, base_a, tilt_a), y_at(z, *b, base_b, tilt_b)
        seen.add("a" if ya > yb else "b" if yb > ya else "tie")
    return seen.pop() if len(seen) == 1 else "mixed"


def fixed_base(foot, size, c, map_z):
    """RM_PlantDrawOrder: flat quad at CommonLayer + BandOffset(foot)."""
    t = min(1.0, max(0.0, (foot + 1) / (map_z + 2)))
    return c["CommonLayer"] * LAYER + c["Band"] * (1 - t)


def main():
    c = constants()
    fails = []

    # 1. vanilla reproduces the bug
    # small LowPlant oyster (south) under a BuildingOnTop giant agarilux (north): layer wins, south loses
    south, north = (10.0, MEASURED["AB_WitchesOyster"][1]), (12.0, MEASURED["AB_GiantAgarilux"][1])
    v = front(south, north, 11 * LAYER, 17 * LAYER, VANILLA_TILT, VANILLA_TILT)
    if v != "b":
        fails.append(f"vanilla model did not reproduce the layer bug (got {v})")
    # same layer, different sizes: a small plant standing north of a big one, inside its sprite, draws over it
    south, north = (10.0, MEASURED["AB_DribblingCap"][1]), (14.0, MEASURED["RM_AgelessCap"][1])
    v = front(south, north, 17 * LAYER, 17 * LAYER, VANILLA_TILT, VANILLA_TILT)
    if v not in ("b", "mixed"):
        fails.append(f"vanilla model did not reproduce the size-slope bug (got {v})")

    # 2. the fix: the southern foot wins everywhere, for random pairs
    rng = random.Random(1016)
    sizes = [s for _, s in MEASURED.values()] + [0.5, 0.7, 1.1]
    checked = 0
    for _ in range(20000):
        map_z = rng.choice([75, 200, 250, 325, 500])
        sa, sb = rng.choice(sizes), rng.choice(sizes)
        fa = rng.uniform(0, map_z - 1)
        fb = fa + rng.uniform(0.05, max(sa, sb))
        a, b = (fa, sa), (fb, sb)            # a is the southern one
        r = front(a, b, fixed_base(fa, sa, c, map_z), fixed_base(fb, sb, c, map_z), 0.0, 0.0)
        if r is None:
            continue
        checked += 1
        if r != "a":
            fails.append(f"fix: southern foot {fa:.2f} (size {sa}) lost to {fb:.2f} (size {sb}) on map {map_z}: {r}")
            break
    if checked < 5000:
        fails.append(f"fix: only {checked} overlapping pairs exercised")

    # 3. band stays inside the common layer, snow lift included, and above every participating layer
    top = c["CommonLayer"] * LAYER + c["Band"] + max(SNOW, c["MaxCarriedOffset"])
    if top >= (c["CommonLayer"] + 1) * LAYER:
        fails.append(f"band top {top:.4f} reaches the next layer {(c['CommonLayer'] + 1) * LAYER:.4f}")
    if c["MinLayer"] > c["CommonLayer"]:
        fails.append("MinLayer above CommonLayer")

    # 4. row separation beats the snow lift up to 500-cell maps
    step = c["Band"] / (500 + 2)
    if step <= SNOW:
        fails.append(f"row step {step:.6f} <= snow lift {SNOW} on a 500-cell map")

    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print(f"PASS: vanilla bug reproduced on 2 measured pairs; fix holds on {checked} overlapping random pairs; "
          f"band top {top:.4f} < next layer; row step {step:.5f} > snow {SNOW:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
