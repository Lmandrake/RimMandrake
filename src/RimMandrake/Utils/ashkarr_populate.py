"""ashkarr_populate.py - author the mutator and landmark layer of THE map.

    python3 src/RimMandrake/Utils/ashkarr_populate.py            # write the two CSVs
    python3 src/RimMandrake/Utils/ashkarr_populate.py --report   # print, write nothing

⛔ THIS IS NOT A GENERATOR. It has no seed, no knobs and no parameters, and it cannot
produce a second planet. Every rule below is a hand-authored decision about Ash'karr,
written down as code so it is reproducible rather than re-typed. Changing a rule changes
THE map; there is no "try N variants".

WHY IT EXISTS. The world bundle was authored with fourteen per-tile columns and none of
them is a mutator or a landmark, so `w9_run.py` painted a planet with no local-map
character and no named places at all. Owner, 2026-08-21: equip them.

WHAT IT WRITES
    world/ASHKARR_WORLDMAP_mutators.csv    tile,mutators   (semicolon-separated defNames)
    world/ASHKARR_WORLDMAP_landmarks.csv   tile,landmark,why

THE TWO PLACEMENT MODES, and why they differ
    MUTATORS are DERIVED. Each rule reads a column the map already carries, so a mutator
    is never an opinion - it is a restatement of authored terrain. That is what makes
    4,831 wrong `Coast` tiles a bug and this pass a fix.
    LANDMARKS are HAND-PLACED, capped, and every one is a named place out of
    `TRANSIENT_worldelements.md` section 7. A named place stops being a place when there
    are 227 of them.

🔴 TWO ENGINE FACTS THIS RELIES ON, both of which the run must re-prove live:
  1. `Tile.AddMutator` does NOT consult `biomeWhitelist` - the whitelist is a WORLDGEN
     constraint, the same way `LandmarkDef.IsValidTile` is. Measured 2026-08-19: on a
     settlement tile `IsValidTile` returned False and `AddLandmark` added it anyway. So
     the shipped `Oasis` mutator, whitelisted to Desert/ExtremeDesert only, is expected
     to take on `ZBiome_DesertOasis` when we place it by hand. ⚠️ EXPECTED, not proven -
     `w9_run.py` reads the count back and the run sheet names it as a decision string.
  2. `AddLandmark` ALSO rolls the def's own `mutatorChances` onto the tile. So landmarks
     must be placed BEFORE the derived mutator pass, or the roll lands on top of ours.

ORDER, and it is not negotiable: clear leftovers -> landmarks -> mutators -> settlements.
Landmarks must precede settlements because `IsValidTile` refuses a settlement tile, and
`AddLandmark` will do it anyway and say nothing. This file keeps them apart by REFUSING
to emit a landmark on or adjacent to a settlement.
"""
import argparse
import csv
import io
import os
import sys

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
SETTS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")
GRAPH = os.path.join(REPO, "world", "world_graph.npz")
OUT_MUT = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_mutators.csv")
OUT_LMK = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_landmarks.csv")

EXPECT_TILES = 21872

# Hilliness is written as RimWorld's enum ordinal, not its label.
MOUNTAINOUS, IMPASSABLE = 4, 5

WATER_BIOMES = {"Ocean", "Lake"}


# ---------------------------------------------------------------------------
#  THE HAND-PLACED LANDMARKS - TRANSIENT_worldelements.md section 7, capped at 16.
#
#  `anchor` is either a settlement NAME (resolved to that settlement's tile, then
#  stepped one tile off it, because a landmark may not share a settlement tile) or an
#  explicit tile id. `pick` names the rule that chooses among candidate tiles when the
#  anchor is a region rather than a point.
#
#  ⛔ Never an ice landmark - there is no ice on this planet.
#  ⚠️ The salt pans are deliberately ABSENT: `DryLake` / `VEE_SaltPlains` may not be
#     legal on `Wasteland` and the census says verify before placing. Nothing is placed
#     on an unverified legality, because a landmark that cannot fire logs NOTHING.
# ---------------------------------------------------------------------------
#  `min_hill` is the fourth field: the lowest hilliness ordinal that still reads as the
#  thing being named. A `Valley` is a NOTCH, so it needs relief around it; an
#  `AbandonedColonyOutlander` does not care.
HAND_PLACED = [
    # (landmarkDef,               anchor,                            why,                                                                min_hill)
    ("AbandonedColonyOutlander", ("tile", 2476),                     "The Setdown - where the dead gravship was found",                   0),
    ("AncientQuarry",            ("settlement", "The Ore Moot"),     "the mine the sandcrawlers were stolen from",                        3),
    ("Valley",                   ("settlement", "Oxalate Watch"),    "The Scald Gate - the one breach in the Spine",                      4),
    ("sw_Sarlacc",               ("settlement", "Sarlacc Ground"),   "the sarlacc the town is named for",                                 0),
    ("AncientLaunchSite",        ("biome", "AB_MechanoidIntrusion"), "The Rust Cathedral - mechanoid ground, permanently at war",          0),
    ("LavaCrater",               ("biome", "Volcano"),               "the Scald rim volcanics - the one volcanic province",                0),
    ("LavaLake",                 ("biome", "LavaField"),             "the Scald rim volcanics",                                           0),
    ("AncientHeatVent",          ("hottest", 3),                     "a heat plume on the hottest world",                                 0),
    ("Oasis",                    ("oasis", 6),                       "the Hutt wells - six named, not 227",                               0),
]


def load_tiles():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    rows = []
    with io.open(TILES, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    if len(rows) != EXPECT_TILES:
        sys.exit("tiles CSV has %d rows, expected %d" % (len(rows), EXPECT_TILES))
    return rows


def load_settlements():
    out = {}
    with io.open(SETTS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[r["name"]] = int(r["tile"])
    return out


def neighbours(graph):
    """idx[t] holds up to 6 neighbour ids; `keep` masks the padding (pentagons have 5)."""
    z = np.load(graph)
    return z["idx"], z["keep"]


# ---------------------------------------------------------------------------
#  MUTATORS - derived, never chosen
# ---------------------------------------------------------------------------
def derive_mutators(rows, idx, keep):
    """Three rules. Each reads a column the map already carries.

    ⚠️ `Coast` is the whole reason this pass exists: the world carried 5,233 of them,
    4,831 on non-water-adjacent tiles and 2,116 of those deep inland, because they were
    placed for the ORIGINAL sea layout and the repaint moved the water. They are cleared
    and recomputed here rather than patched.
    """
    is_water = np.zeros(len(rows), dtype=bool)
    for t, r in enumerate(rows):
        is_water[t] = (r["biome"] in WATER_BIOMES) or (r["water"] == "1")

    out = {}

    # 1. Coast - a LAND tile with at least one water neighbour.
    coast = 0
    for t in range(len(rows)):
        if is_water[t]:
            continue
        n = idx[t][keep[t]]
        if is_water[n].any():
            out.setdefault(t, []).append("Coast")
            coast += 1

    # 2. Mountain - hilliness at the top two ordinals.
    mountain = 0
    for t, r in enumerate(rows):
        try:
            h = int(r["hilliness"])
        except (TypeError, ValueError):
            continue
        if h >= MOUNTAINOUS:
            out.setdefault(t, []).append("Mountain")
            mountain += 1

    # 3. Oasis - the painted oasis biome, inside the def's own temperature gate.
    #    ⚠️ The 227 span 16-62 C, so the gate genuinely excludes a few; that is the def's
    #    rule and we honour it rather than forcing every tile.
    oasis = 0
    for t, r in enumerate(rows):
        if r["biome"] != "ZBiome_DesertOasis":
            continue
        try:
            temp = float(r["temp_c"])
        except (TypeError, ValueError):
            continue
        if 20.0 <= temp <= 60.0:
            out.setdefault(t, []).append("Oasis")
            oasis += 1

    counts = {"Coast": coast, "Mountain": mountain, "Oasis": oasis}

    # ---- the second wave, added 2026-08-21 on the owner's call ----------------
    # Same discipline: every rule reads a column already authored, so nothing here is a
    # placement opinion. ⛔ `Marshy`, `Wetland` and `WetClimate` are NOT here even though
    # the swampiness column would support them - the census ruled them out for a planet
    # with no seasons and no rain, and inventory beats a clever derivation.

    def num(r, k):
        try:
            return float(r[k] or 0)
        except (TypeError, ValueError):
            return 0.0

    elev = [num(r, "elev_m") for r in rows]

    def add(name, pred):
        n = 0
        for t, r in enumerate(rows):
            if pred(t, r):
                out.setdefault(t, []).append(name)
                n += 1
        counts[name] = n

    # The Dune Sea: the flat, rainless heart of the dayside. The census flagged a
    # duplication risk against the REGION named "The Dune Sea" — but a region label is a
    # name on the globe and a mutator is terrain on the local map. Different layers.
    add("Dunes", lambda t, r: r["biome"] == "ExtremeDesert"
        and int(r["hilliness"] or 0) == 1 and num(r, "rain_mm") < 60)

    # The arid belt either side of it — sand in patches rather than an ocean of it.
    add("Sandy", lambda t, r: r["biome"] in ("Desert", "AridShrubland")
        and int(r["hilliness"] or 0) <= 2)

    # The nightside floor is rock, and rock at relief has caves in it.
    add("Caves", lambda t, r: r["biome"] == "AB_RockyCrags" and int(r["hilliness"] or 0) >= 3)

    # A tile the river actually runs through. ⚠️ The link layer puts the river on the
    # GLOBE; this is what makes it show up on the local map when a colony lands there.
    add("River", lambda t, r: num(r, "river_flow") > 0)

    # A mouth: a river tile touching the sea. There are exactly two on this planet.
    add("RiverDelta", lambda t, r: num(r, "river_flow") > 0 and is_water[idx[t][keep[t]]].any())

    # Relief steep enough to read as a face rather than a slope.
    add("Cliffs", lambda t, r: (not is_water[t]) and len(idx[t][keep[t]])
        and max(abs(elev[int(n)] - elev[t]) for n in idx[t][keep[t]]) > 700.0)

    # The one volcanic province, and the ground that borders it.
    add("LavaFlow", lambda t, r: r["biome"] == "AB_PyroclasticConflagration")
    volcanic = {t for t, r in enumerate(rows)
                if r["biome"] in ("Volcano", "LavaField", "AB_PyroclasticConflagration")}
    add("HotSprings", lambda t, r: t not in volcanic and (not is_water[t])
        and any(int(n) in volcanic for n in idx[t][keep[t]]))

    return out, counts


# ---------------------------------------------------------------------------
#  LANDMARKS - hand-placed, and refused rather than nudged
# ---------------------------------------------------------------------------
def resolve_landmarks(rows, setts, idx, keep):
    settlement_tiles = set(setts.values())
    adjacent = set()
    for t in settlement_tiles:
        for n in idx[t][keep[t]]:
            adjacent.add(int(n))
    forbidden = settlement_tiles | adjacent

    placed = {}      # tile -> (def, why)
    refusals = []

    def hill(t):
        try:
            return int(rows[t]["hilliness"])
        except (TypeError, ValueError):
            return 0

    def legal(t, min_hill=0):
        """Can a landmark sit here at all?

        🔴 `IsValidTile` refuses IMPASSABLE hilliness, and `AddLandmark` will place it
        regardless — which is how the first pass put `LavaCrater` and `LavaLake` on two
        of the planet's 42 impassable tiles, where no player can ever reach them. Both
        volcanic biomes have passable tiles (Volcano 7, LavaField 8); there was never a
        need to use an impassable one.
        """
        if t in forbidden or t in placed:
            return False
        r = rows[t]
        if r["water"] == "1" or r["biome"] in WATER_BIOMES:
            return False
        if hill(t) >= IMPASSABLE:
            return False
        return hill(t) >= min_hill

    def claim(tile, ldef, why):
        if tile is None:
            refusals.append((ldef, why, "no candidate tile"))
            return False
        if tile in forbidden:
            refusals.append((ldef, why, "tile %d is a settlement or adjacent to one" % tile))
            return False
        if tile in placed:
            refusals.append((ldef, why, "tile %d already holds %s" % (tile, placed[tile][0])))
            return False
        placed[tile] = (ldef, why)
        return True

    def step_off(tile, min_hill=0):
        """The nearest tile to an anchor that a landmark may legally occupy.

        ⚠️ NOT one step. `IsValidTile` refuses a settlement tile AND every tile adjacent
        to one, so the census's "one tile adjacent" is not actually placeable - the first
        legal ring is two out. This walks outward until it finds one, so a named place
        stays as close to the thing it is named for as the engine permits.

        Within a ring it takes the HILLIEST legal tile, so a `Valley` lands in relief
        rather than on whatever the neighbour list happened to enumerate first. The first
        pass had no such preference and put The Scald Gate's valley on an oasis.
        """
        seen = {tile}
        frontier = [tile]
        for _ in range(5):
            nxt, ring = [], []
            for cur in frontier:
                for n in idx[cur][keep[cur]]:
                    n = int(n)
                    if n in seen:
                        continue
                    seen.add(n)
                    nxt.append(n)
                    if legal(n, min_hill):
                        ring.append(n)
            if ring:
                return max(ring, key=hill)
            frontier = nxt
        return None

    for ldef, (kind, arg), why, min_hill in HAND_PLACED:
        if kind == "tile":
            claim(int(arg) if legal(int(arg), min_hill) else None, ldef, why)

        elif kind == "settlement":
            anchor = setts.get(arg)
            if anchor is None:
                refusals.append((ldef, why, "no settlement named %r" % arg))
                continue
            claim(step_off(anchor, min_hill), ldef, why)

        elif kind == "biome":
            # the middle legal tile of that biome, so a named place does not land in
            # somebody's back garden — and never an impassable one
            cands = [t for t, r in enumerate(rows) if r["biome"] == arg and legal(t, min_hill)]
            if not cands:
                refusals.append((ldef, why, "no LEGAL tile carries biome %s" % arg))
                continue
            claim(sorted(cands)[len(cands) // 2], ldef, why)

        elif kind == "hottest":
            order = sorted(range(len(rows)), key=lambda t: -float(rows[t]["temp_c"] or -999))
            n = 0
            for t in order:
                if n >= int(arg):
                    break
                if legal(t, min_hill) and claim(t, ldef, why):
                    n += 1

        elif kind == "oasis":
            # ⚠️ Inside the Oasis def's own 20–60 °C gate. The LandmarkDef FORCES its
            # mutator (`req:Oasis`), and that mutator carries the temperature range — so
            # a named well on a 18.5 °C tile is a landmark whose whole point cannot fire.
            cands = [t for t, r in enumerate(rows)
                     if r["biome"] == "ZBiome_DesertOasis"
                     and 20.0 <= float(r["temp_c"] or -999) <= 60.0
                     and legal(t, min_hill)]
            # spread them: take every k-th so six named wells are not six neighbours
            k = max(1, len(cands) // int(arg))
            n = 0
            for t in cands[::k]:
                if n >= int(arg):
                    break
                if claim(t, ldef, why):
                    n += 1

    return placed, refusals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print the summary, write nothing")
    a = ap.parse_args()

    rows = load_tiles()
    setts = load_settlements()
    idx, keep = neighbours(GRAPH)

    placed, refusals = resolve_landmarks(rows, setts, idx, keep)
    muts, counts = derive_mutators(rows, idx, keep)

    print("mutators   %d tiles carry at least one" % len(muts))
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("             %-10s %d" % (name, n))
    print("landmarks  %d placed, cap 16" % len(placed))
    for t, (ldef, why) in sorted(placed.items()):
        print("             %-26s tile %-6d %s" % (ldef, t, why))
    if refusals:
        print("refused    %d" % len(refusals))
        for ldef, why, reason in refusals:
            print("             %-26s %s" % (ldef, reason))

    if a.report:
        return 0

    with io.open(OUT_MUT, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["tile", "mutators"])
        for t in sorted(muts):
            wr.writerow([t, ";".join(muts[t])])
    with io.open(OUT_LMK, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["tile", "landmark", "why"])
        for t in sorted(placed):
            wr.writerow([t, placed[t][0], placed[t][1]])
    print("\nwrote %s\n      %s" % (OUT_MUT, OUT_LMK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
