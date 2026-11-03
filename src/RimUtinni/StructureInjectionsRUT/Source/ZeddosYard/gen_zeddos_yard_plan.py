#!/usr/bin/env python3
"""gen_zeddos_yard_plan.py - PLAYER_START_SITE_1: write Templates/zeddos_yard.txt, the
rimplace flat plan (v2) of Zeddo's Salvage Yard, the formal player start at tile 17007.

    python3 src/RimUtinni/StructureInjectionsRUT/Source/ZeddosYard/gen_zeddos_yard_plan.py [--check]

--check regenerates in memory and exits 1 if the committed plan differs (the selftest's first bar).

WHAT THE PLAN IS (owner card 2026-09-08, "Zeddo's Yard"; Scenario_Utinni's crawl, "The Hutts keep a
mountain of the galaxy's discards out here"):
  * a LANDING CLEARING at the footprint's centre, CLEAR all, nothing placed inside it. Its size is
    the item's own constraint from GRAVSHIP_LANDING_FOG_REVEAL_1: the v2 Utinni ring hull is 92 x 86,
    plus a 2-cell margin each side = 96 x 90; the clearing is CLEAR_W x CLEAR_H, larger than that, and
    a further LANE-cell empty band surrounds it. This GenStep runs at order 400, before Odyssey's
    GenStep_ReserveGravshipArea (600), so the landing picker's overlap-cost minimisation sees the
    yard and picks the empty middle instead of landing in the junk.
  * RUINED SHIPS, the real skyline: piles of hauled hull junk (vanilla/DLC wreck buildings + steel
    slag) in a ring band around the clearing, broken by four cardinal haul lanes to the map edge.
    Hutt cranes stand in two of the piles: it is a yard, worked, not a crash site.
  * OLD MEGASTRUCTURES, the injected skyline: two broken arcs of AncientMegastructure ground with
    fortified-wall stubs, older than the yard, which is piled against them.

Only base-game and DLC defs (every DLC is assumed - owner 2026-09-19): GenStep_RimplacePlan logs an
error for a ThingDef that does not load, and a RUT mod must not depend on an RSW or RM content mod
for its scenery. Deterministic: one seeded Random, so the plan is a pure function of this file.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, "..", ".."))
PLAN = os.path.join(MOD, "Templates", "zeddos_yard.txt")

SEED = 17007
W = H = 170                     # footprint; fits a 250 map (centre +-85) and the 325 home map
HULL_W, HULL_H, MARGIN = 92, 86, 2
CLEAR_W, CLEAR_H = 100, 94      # >= HULL + 2*MARGIN = 96 x 90
LANE = 3                        # empty band around the clearing
HAUL_LANE = 8                   # width of the four cardinal lanes through the junk ring
EDGE = 2                        # nothing within this many cells of the footprint edge

# defName -> (size x, size z). Sizes read off the 2026-11-02 def dump (packageId ludeon.*).
SHIP_PALETTE = [  # (defName, weight)
    ("ShipChunk", 3), ("ShipChunk_Mech", 2), ("AncientDropshipEngine", 2), ("AncientJetEngine", 2),
    ("AncientLargeRustedEngineBlock", 2), ("AncientRustedEngineBlock", 3), ("AncientPodCar", 2),
    ("AncientOpenContainer", 1), ("AncientMediumContainer", 1), ("AncientSmallContainer", 2),
]
# Deconstructible salvage is CAPPED: a vanilla ShipChunk costs 11 components + 40 steel and deconstructs
# for a share of that, so an uncapped yard hands the player hundreds of components on day one. The
# crawl's yard is picked over ("too dead to be worth cutting up"); its bulk is non-deconstructible
# ancient wreckage. Beyond the cap a pick falls through to the next palette draw.
CAPS = {"ShipChunk": 14, "ShipChunk_Mech": 8, "AncientPallet_SteelSlag": 6}
SIZES = {
    "ShipChunk": (2, 2), "ShipChunk_Mech": (2, 2), "AncientDropshipEngine": (3, 2), "AncientJetEngine": (3, 2),
    "AncientLargeRustedEngineBlock": (2, 1), "AncientRustedEngineBlock": (1, 1), "AncientPodCar": (3, 2),
    "AncientOpenContainer": (4, 2), "AncientMediumContainer": (2, 4), "AncientSmallContainer": (2, 2),
    "AncientRustedDropship": (6, 5), "AncientCraneBase": (5, 5), "AncientCraneColumn": (2, 2),
    "AncientCraneArm": (2, 1), "AncientPallet_SteelSlag": (2, 2), "AncientFortifiedWall": (1, 1),
    "ChunkSlagSteel": (1, 1), "Steel": (1, 1),
}
SHIP_DEFS = {d for d, _ in SHIP_PALETTE} | {"AncientRustedDropship"}
MEGA_TERRAIN = "AncientMegastructure"
MEGA_WALL = "AncientFortifiedWall"
ITEM_DEFS = {"ChunkSlagSteel"}


def clearing_rect():
    """(x, z, w, h) of the landing clearing, centred on the footprint."""
    return ((W - CLEAR_W) // 2, (H - CLEAR_H) // 2, CLEAR_W, CLEAR_H)


def occupied(defname, x, z, rot=0):
    """Cells a thing covers at centre (x, z), as GenAdj.OccupiedRect(center, rot, size): size swapped
    for a horizontal rot, then AdjustForRotation steps the centre back one cell on an even axis
    (rot 1: z; rot 2: x and z; rot 3: x), then low corner = centre - (size-1)/2."""
    sx, sz = SIZES[defname]
    if (sx, sz) != (1, 1):
        if rot in (1, 3):
            sx, sz = sz, sx
        if rot == 1 and sz % 2 == 0:
            z -= 1
        elif rot == 2:
            x -= 1 if sx % 2 == 0 else 0
            z -= 1 if sz % 2 == 0 else 0
        elif rot == 3 and sx % 2 == 0:
            x -= 1
    x0 = x - (sx - 1) // 2
    z0 = z - (sz - 1) // 2
    return [(x0 + i, z0 + j) for i in range(sx) for j in range(sz)]


def _in_haul_lane(x, z):
    cx, cz = W // 2, H // 2
    return abs(x - cx) < HAUL_LANE // 2 + 1 or abs(z - cz) < HAUL_LANE // 2 + 1


def _keepout():
    """Cells no thing may cover: the clearing plus its LANE band."""
    x0, z0, w, h = clearing_rect()
    return set((x, z) for x in range(x0 - LANE, x0 + w + LANE) for z in range(z0 - LANE, z0 + h + LANE))


def layout():
    """-> dict(things=[(def, x, z, rot)], terrain=[(x, z, def)]). Pure function of SEED."""
    rnd = random.Random(SEED)
    keep = _keepout()
    used = set()
    things = []
    terrain = {}
    cx, cz = W // 2, H // 2

    def fits(cells, allow_lane=False):
        for (x, z) in cells:
            if x < EDGE or z < EDGE or x >= W - EDGE or z >= H - EDGE:
                return False
            if (x, z) in keep or (x, z) in used:
                return False
            if not allow_lane and _in_haul_lane(x, z):
                return False
        return True

    def place(defname, x, z, rot=0):
        if defname in CAPS and sum(1 for t in things if t[0] == defname) >= CAPS[defname]:
            return False
        cells = occupied(defname, x, z, rot)
        if not fits(cells):
            return False
        used.update(cells)
        things.append((defname, x, z, rot))
        return True

    # 1. megastructure arcs first: the yard is piled against them. Ring about the footprint centre,
    #    radius 74..78, two arcs (NE and SW) with deterministic breaks. Terrain only under no thing.
    arcs = [(15, 105), (195, 255)]
    for a0, a1 in arcs:
        for deg10 in range(a0 * 10, a1 * 10):
            a = math.radians(deg10 / 10.0)
            if int(deg10 / 10) % 23 in (7, 8, 9):          # broken spans
                continue
            for r in range(74, 79):
                x = int(round(cx + r * math.cos(a)))
                z = int(round(cz + r * math.sin(a)))
                if EDGE <= x < W - EDGE and EDGE <= z < H - EDGE and (x, z) not in keep:
                    terrain[(x, z)] = MEGA_TERRAIN
        # wall stubs on the arc's outer lip, every ~9 degrees, 2-4 cells long, radially
        for deg in range(a0 + 4, a1, 9):
            a = math.radians(deg)
            for r in range(76, 76 + rnd.randint(2, 4)):
                x = int(round(cx + r * math.cos(a)))
                z = int(round(cz + r * math.sin(a)))
                if fits([(x, z)], allow_lane=True):
                    used.add((x, z))
                    things.append((MEGA_WALL, x, z, 0))

    # 2. the junk ring: piles along the square band midway between the keep-out and the footprint
    #    edge (the band is ~30 cells wide on every side), walked as a perimeter with jitter.
    defs, weights = zip(*SHIP_PALETTE)
    x0, z0, w, h = clearing_rect()
    lo = (EDGE + x0 - LANE) // 2                           # midline of the west/south band
    hi = W - 1 - lo                                        # and of the east/north band (square footprint)
    side = hi - lo
    piles = []
    n = 40
    for k in range(n):
        t = 4.0 * side * (k + rnd.uniform(-0.2, 0.2)) / n
        t %= 4.0 * side
        s_, off = divmod(t, side)
        off = int(off)
        px, pz = [(lo + off, lo), (hi, lo + off), (hi - off, hi), (lo, hi - off)][int(s_)]
        piles.append((px + rnd.randint(-3, 3), pz + rnd.randint(-3, 3)))

    def place_near(defname, px, pz, spread, rot=0, tries=12):
        for _ in range(tries):
            if place(defname, px + rnd.randint(-spread, spread), pz + rnd.randint(-spread, spread), rot):
                return True
        return False

    for i, (px, pz) in enumerate(piles):
        if i in (6, 26):                                   # two worked piles carry a Hutt crane
            for _ in range(12):
                bx, bz = px + rnd.randint(-4, 4), pz + rnd.randint(-4, 4)
                if fits(occupied("AncientCraneBase", bx, bz) + occupied("AncientCraneColumn", bx + 4, bz)
                        + occupied("AncientCraneArm", bx + 4, bz + 2)):
                    place("AncientCraneBase", bx, bz)
                    place("AncientCraneColumn", bx + 4, bz)
                    place("AncientCraneArm", bx + 4, bz + 2)
                    break
        if i % 4 == 2:                                     # the big hulls: one pile in four
            place_near("AncientRustedDropship", px, pz, 4, rnd.choice((0, 2)))
        for _ in range(rnd.randint(14, 22)):
            d = rnd.choices(defs, weights)[0]
            rot = rnd.choice((0, 1, 2, 3)) if SIZES[d][0] == SIZES[d][1] else rnd.choice((0, 2))
            place_near(d, px, pz, 6, rot, tries=4)
        if i % 4 == 1:
            place_near("AncientPallet_SteelSlag", px, pz, 5)
        for _ in range(rnd.randint(3, 6)):                 # slag spilled round the pile
            place_near("ChunkSlagSteel", px, pz, 9, tries=2)

    return {"things": things, "terrain": sorted((x, z, d) for (x, z), d in terrain.items())}


def render():
    lay = layout()
    cx0, cz0, cw, ch = clearing_rect()
    out = ["# rimplace flat plan v2",
           "# template  zeddos_yard (generated by Source/ZeddosYard/gen_zeddos_yard_plan.py; PLAYER_START_SITE_1)",
           "# min_rect  %dx%d   baked at %dx%d" % (W, H, W, H),
           "# clearing  %d,%d,%d,%d   (hull %dx%d + %d margin; nothing placed inside)" % (cx0, cz0, cw, ch, HULL_W, HULL_H, MARGIN),
           "FOOTPRINT\t0\t0\t%d\t%d" % (W, H),
           "CLEAR\t0\t0\t%d\t%d\tall" % (W, H),
           "CLEAR\t%d\t%d\t%d\t%d\tall" % (cx0, cz0, cw, ch)]
    for x, z, d in lay["terrain"]:
        out.append("TERRAIN\t%d\t%d\t%s" % (x, z, d))
    for d, x, z, rot in lay["things"]:
        out.append("THING\t%s\t%d\t%d\t%d\t-" % (d, x, z, rot))
    return "\n".join(out) + "\n"


def main(argv):
    text = render()
    if "--check" in argv:
        have = open(PLAN, encoding="utf-8").read() if os.path.exists(PLAN) else ""
        if have != text:
            print("STALE: %s differs from the generator's output; rerun without --check" % PLAN)
            return 1
        print("OK: %s matches the generator" % PLAN)
        return 0
    with open(PLAN, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote %s (%d lines)" % (PLAN, text.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
