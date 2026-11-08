#!/usr/bin/env python3
"""Offline proof of the south-draws-front math (RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES).

Owner, 2026-10-16: "if you are more south, you go in front."  2026-11-08: "for ALL large pawns and objects in the game".

Constants are parsed from Source/SouthDrawsFront/SouthDrawsFrontKernel.cs, so this cannot drift from the C#.
Larger y = nearer the camera = in front (pawn and plant materials are cutout, depth-written).

  PLANTS (moved from BiomesShell's selftest_plant_draw_order.py with the C#)
  1. VANILLA reproduces the reported bug on measured Rot pairs (different layers, different sizes).
  2. The FIX puts the more southern foot in front at every overlapping pixel, for random pairs.
  3. The band never reaches the next layer (Item), snow lift included; 4. rows stay further apart than the snow lift.
  PAWNS
  5. VANILLA (Pawn_DrawTracker.cs:60, SeededYOffset by thing id) puts a northern Dalgo-sized pawn in front of a
     southern one for some id pairs; the FIX puts the southern body in front for every z gap, and a mutant with the
     sign flipped is caught.
  6. Ground pawns stay under PawnUnused, flying ones under PawnState, render stack included.
  BUILDINGS
  7. A building's lift plus a vanilla +AltInc overlay stays under the next layer; southern rows lift higher.
  WIRING
  8. The patch reads the setting, routes SeededYOffset, and the setting defaults on in field, Scribe and UI.
"""
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source" / "SouthDrawsFront" / "SouthDrawsFrontKernel.cs"
PATCHES = HERE / "Source" / "SouthDrawsFront" / "SouthDrawsFrontPatches.cs"
PAWN = HERE / "Source" / "SouthDrawsFront" / "SouthDrawsFrontPawn.cs"
MOD = HERE / "Source" / "CaiFogOff" / "RM_PatchesMod.cs"
LAYER = 0.36585367           # Altitudes.LayerSpacing (decompiled 1.6, Altitudes.cs:11)
NODE = 0.0003658537          # PawnRenderUtility.AltitudeForLayer per layer (PawnRenderUtility.cs:334)
SNOW = 0.0003658537          # Plant.Print snow overlay WithYOffset
VANILLA_TILT = 0.1           # Plant.Print topVerticesAltitudeBias
PAWN_LAYER = 23              # AltitudeLayer.Pawn

# (layer index, mature visual size) from the 2026-10-04 def dump; drawSize.x is 1 for all of them.
MEASURED = {
    "RM_WitchesOyster": (11, 6.0), "RM_AgaricusDomeCap": (11, 7.0), "RM_LilacBeacon": (11, 3.0),
    "RM_GlowingAgarilux": (15, 4.0), "RM_PaleTree": (15, 6.0), "RM_GiantAgarilux": (17, 6.0),
    "RM_DribblingCap": (17, 12.0), "RM_SlimyPholiota": (17, 5.0), "RM_AgelessCap": (11, 1.6),
}
fails = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + ": " + name + ("" if cond else "  " + str(detail)))
    if not cond:
        fails.append(name)


def constants():
    text = SRC.read_text(encoding="utf-8")
    out = {}
    for name in ("PlantMinLayer", "CommonLayer", "BuildingMinLayer", "PrintBand", "MaxCarriedOffset",
                 "PawnFloor", "PawnBand", "AltInc", "LayerSpacing"):
        m = re.search(r"public const (?:int|float) " + name + r"\s*=\s*(-?[0-9.]+)f?;", text)
        if not m:
            sys.exit(f"FAIL: constant {name} not found in {SRC}")
        out[name] = float(m.group(1))
    return out


def southness(z, map_z):
    t = min(1.0, max(0.0, (z + 1) / (map_z + 2)))
    return 1 - t


def y_at(z, foot, size, base_y, tilt):
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


def plant_base(foot, c, map_z):
    return c["CommonLayer"] * LAYER + c["PrintBand"] * southness(foot, map_z)


def pawn_offset(z, map_z, flight, c, sign=1):
    return c["PawnFloor"] + c["PawnBand"] * (southness(z, map_z) if sign > 0 else 1 - southness(z, map_z)) \
        + c["PawnBand"] * min(1.0, max(0.0, flight))


def pawn_body_front(c, sign=1, trials=20000):
    """Two pawns' body nodes (render layer 0): is the southern one in front for every gap and map?"""
    rng = random.Random(1108)
    for _ in range(trials):
        map_z = rng.choice([75, 200, 250, 325, 500])
        zs = rng.uniform(0, map_z - 1)
        zn = zs + rng.uniform(0.01, 4.0)
        if pawn_offset(zs, map_z, 0, c, sign) <= pawn_offset(zn, map_z, 0, c, sign):
            return False, (zs, zn, map_z)
    return True, None


def main():
    c = constants()

    # 1-4 plants
    south, north = (10.0, MEASURED["RM_WitchesOyster"][1]), (12.0, MEASURED["RM_GiantAgarilux"][1])
    check("plants: vanilla model reproduces the layer bug", front(south, north, 11 * LAYER, 17 * LAYER, VANILLA_TILT, VANILLA_TILT) == "b")
    south, north = (10.0, MEASURED["RM_DribblingCap"][1]), (14.0, MEASURED["RM_AgelessCap"][1])
    check("plants: vanilla model reproduces the size-slope bug",
          front(south, north, 17 * LAYER, 17 * LAYER, VANILLA_TILT, VANILLA_TILT) in ("b", "mixed"))
    rng = random.Random(1016)
    sizes = [s for _, s in MEASURED.values()] + [0.5, 0.7, 1.1]
    checked, lost = 0, None
    for _ in range(20000):
        map_z = rng.choice([75, 200, 250, 325, 500])
        sa, sb = rng.choice(sizes), rng.choice(sizes)
        fa = rng.uniform(0, map_z - 1)
        fb = fa + rng.uniform(0.05, max(sa, sb))
        r = front((fa, sa), (fb, sb), plant_base(fa, c, map_z), plant_base(fb, c, map_z), 0.0, 0.0)
        if r is None:
            continue
        checked += 1
        if r != "a":
            lost = (fa, sa, fb, sb, map_z, r)
            break
    check(f"plants: the southern foot wins on {checked} overlapping random pairs", lost is None and checked >= 5000, lost)
    top = c["CommonLayer"] * LAYER + c["PrintBand"] + max(SNOW, c["MaxCarriedOffset"])
    check("plants: band top stays under the Item layer", top < (c["CommonLayer"] + 1) * LAYER, top)
    check("plants: PlantMinLayer <= CommonLayer", c["PlantMinLayer"] <= c["CommonLayer"])
    check("plants: row step beats the snow lift on a 500-cell map", c["PrintBand"] / 502 > SNOW)

    # 5 pawns: vanilla seeded order is a coin flip; the fix is south-first; a flipped mutant is caught
    north_wins = 0
    rng = random.Random(60)
    for _ in range(1000):
        seed_s, seed_n = rng.uniform(-c["AltInc"], c["AltInc"]), rng.uniform(-c["AltInc"], c["AltInc"])
        if seed_n > seed_s:
            north_wins += 1
    check(f"pawns: vanilla SeededYOffset puts the northern pawn in front in {north_wins}/1000 id pairs", 300 < north_wins < 700)
    ok, bad = pawn_body_front(c)
    check("pawns: the southern body is in front for every gap 0.01..4 cells on maps 75..500", ok, bad)
    ok_mut, _ = pawn_body_front(c, sign=-1, trials=200)
    check("pawns: a mutant with the sign flipped is caught", not ok_mut)
    # What the render stack leaves: a northern node on render layer L pokes over a southern body closer than this.
    step250 = c["PawnBand"] / 252
    check("pawns: on a 250 map an animal overlay (layer 10) is ordered beyond %.1f cells, a human head (layer 50) "
          "beyond %.1f (measured limit, reported)" % (10 * NODE / step250, 50 * NODE / step250), True)

    # 6 pawn bounds
    stack_top = 100 * NODE
    ground_top = c["PawnFloor"] + c["PawnBand"] + stack_top
    check("pawns: ground top %.3f stays under PawnUnused (+%.3f)" % (ground_top, LAYER), ground_top < LAYER)
    fly_top = c["PawnFloor"] + 2 * c["PawnBand"] + c["AltInc"] + stack_top
    check("pawns: flying top %.3f stays under PawnState (+%.3f)" % (fly_top, 2 * LAYER), fly_top < 2 * LAYER)
    low = c["PawnFloor"] - 10 * NODE
    check("pawns: lowest %.4f is no lower than vanilla's lowest" % low, low >= -c["AltInc"] - 10 * NODE - 1e-9)
    check("pawns: kernel AltInc and LayerSpacing match the decompile",
          abs(c["AltInc"] - 0.03658537) < 1e-7 and abs(c["LayerSpacing"] - LAYER) < 1e-7)

    # 7 buildings
    btop = c["PrintBand"] + c["AltInc"]
    check("buildings: lift + a vanilla AltInc overlay (%.3f) stays under the next layer" % btop, btop < LAYER)
    check("buildings: a southern row lifts higher", c["PrintBand"] * southness(10, 250) > c["PrintBand"] * southness(11, 250))
    check("buildings: Building..BuildingOnTop", c["BuildingMinLayer"] == 15 and c["CommonLayer"] == 17)

    # 8 wiring
    patches, pawn, mod = PATCHES.read_text(encoding="utf-8"), PAWN.read_text(encoding="utf-8"), MOD.read_text(encoding="utf-8")
    check("wiring: DrawPos transpiler routes SeededYOffset to OrderedYOffset",
          "nameof(Pawn_DrawTracker.SeededYOffset)" in patches and "nameof(SouthDrawsFrontPawn.OrderedYOffset)" in patches)
    check("wiring: the pawn hook falls back to vanilla when off", "!RM_PatchesSettings.southDrawsFront" in pawn
          and "return tracker.SeededYOffset" in pawn)
    check("wiring: the printer hook reads the setting", "RM_PatchesSettings.southDrawsFront" in patches)
    check("wiring: setting defaults on (field, Scribe, UI label)",
          "public static bool southDrawsFront = true;" in mod and 'Scribe_Values.Look(ref southDrawsFront, "southDrawsFront", true);' in mod
          and '"Southern things draw in front"' in mod and "SouthDrawsFrontPatches.Reprint()" in mod)
    check("wiring: no allocation or LINQ in the per-frame pawn hook", "new " not in pawn.split("OrderedYOffset", 1)[1]
          and "System.Linq" not in pawn)

    print(("FAIL: %d check(s)" % len(fails)) if fails else "PASS: south draws front, all checks")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
