#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_landmarks.py - repair and extend Ash'karr's landmarks.

Two jobs, because the second must not multiply the first.

  REPAIR   Every LandmarkDef declares `mutatorChances` entries marked
           `required: true`. Ten of the sixteen landmarks already on the map sat on
           tiles that did not carry theirs - `AncientHeatVent` x3 on tiles with NO
           mutators at all, `AncientQuarry` missing three. Landmarks stamped straight
           into a generated world through the bridge do not go through the worldgen
           path that would have applied them, so the bundle has to carry them.

  EXTEND   16 landmarks on 21,872 tiles, six of them the same Oasis, against 113
           LandmarkDefs installed. The rules below are hand-written per landmark:
           where it may go, how many, and why. Nothing is scattered at random.

    python3 src/RimMandrake/Utils/ashkarr_landmarks.py              # plan only
    python3 src/RimMandrake/Utils/ashkarr_landmarks.py --apply

🔑 Placement is deterministic. Candidates are ranked by a stable key and spaced by a
minimum hex separation, so re-running produces the same map - there is no seed here
and there must not be one. This authors ONE planet; it is not a generator.
"""
import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")
MEASURE = os.path.expanduser("~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py")

# ── the rules ──────────────────────────────────────────────────────────────────
# (landmark, how many, minimum hex spacing, predicate over a tile dict, why)
# `t` carries: elev, rain, temp, arc, water, biome, region, hill, river, coast
RULES = [
    # the deep desert - the Jawas' own country
    ("Dunes",              8, 6, lambda t: t["biome"] in ("Desert", "ExtremeDesert") and t["hill"] <= 2 and t["arc"] < 75,
     "the Dune Sea proper - open sand a caravan crosses for days"),
    ("VEE_PebbleDunes",    4, 8, lambda t: t["biome"] == "ExtremeDesert" and t["hill"] <= 2,
     "gravel desert, harder going than sand"),
    ("VEE_QuicksandDunes", 3, 10, lambda t: t["biome"] in ("Desert", "ExtremeDesert") and t["hill"] <= 1,
     "a sink that swallows a sandcrawler"),
    ("VEE_RedDesert",      3, 10, lambda t: t["biome"] == "ExtremeDesert" and t["temp"] > 45,
     "iron sand on the hot side"),
    ("VEE_DustBowl",       3, 10, lambda t: t["biome"] in ("Desert", "AridShrubland") and t["rain"] < 60,
     "ground that was farmed once and is not any more"),

    # where water was, or nearly is
    ("DryLake",            5, 8, lambda t: t["biome"] in ("ExtremeDesert", "Wasteland", "ZBiome_Badlands") and t["hill"] <= 2 and t["elev"] < 400,
     "a playa - the salt flat a river dies in"),
    ("VEE_SaltPlains",     4, 9, lambda t: t["biome"] in ("Wasteland", "ExtremeDesert") and t["elev"] < 250,
     "salt pan, and the reason the Salt is named that"),
    ("VEE_DryRiver",       5, 7, lambda t: t["biome"] in ("Desert", "ExtremeDesert", "ZBiome_Badlands") and not t["river"] and t["hill"] <= 3,
     "a watercourse that runs once a decade"),
    ("VEE_RelictDelta",    2, 12, lambda t: t["river"] and t["elev"] <= 40,
     "where the inland rivers spread out and stop"),
    ("VEE_AlluvialFan",    3, 9, lambda t: t["river"] and 40 < t["elev"] < 500,
     "the spoil a mountain stream drops when the slope runs out"),
    ("Oasis",              4, 12, lambda t: t["biome"] in ("Desert", "ExtremeDesert", "ZBiome_DesertOasis") and t["rain"] > 0,
     "the Hutt wells - water is the currency here"),
    ("VEE_StagnantRivulet", 3, 8, lambda t: t["river"] and t["temp"] > 30 and t["elev"] < 300,
     "standing water, and everything that breeds in it"),

    # rock, and the crags that cover a fifth of the planet
    ("Cliffs",             6, 7, lambda t: t["biome"] == "AB_RockyCrags" and t["hill"] >= 4,
     "the crags break in walls, not slopes"),
    ("VEE_RockRidge",      5, 8, lambda t: t["biome"] == "AB_RockyCrags" and t["hill"] >= 3,
     "a spine of standing rock"),
    ("VEE_SerpentineCanyons", 4, 9, lambda t: t["biome"] in ("AB_RockyCrags", "ZBiome_Badlands") and t["hill"] >= 3,
     "slot canyons - cover, ambush, and a way through"),
    ("VEE_JaggedRocks",    4, 8, lambda t: t["biome"] == "AB_RockyCrags" and t["hill"] >= 4,
     "ground that cuts boots"),
    ("Plateau",            3, 12, lambda t: t["elev"] > 900 and t["hill"] <= 3,
     "high flat ground, and you can see everything from it"),
    ("VEE_WindBlownPlateau", 2, 14, lambda t: t["elev"] > 1100 and t["hill"] <= 3,
     "nothing grows up here and the wind never stops"),
    ("Valley",             4, 9, lambda t: t["hill"] >= 4 and t["elev"] > 500,
     "the way through a range, and everyone uses it"),
    ("Basin",              3, 11, lambda t: t["hill"] <= 2 and t["elev"] < 200 and t["biome"] != "Ocean",
     "a bowl that collects what little falls"),
    ("Cavern",             4, 9, lambda t: t["hill"] >= 4,
     "a mountain you can get inside"),
    ("Chasm",              3, 11, lambda t: t["hill"] >= 4 and t["biome"] in ("AB_RockyCrags", "ZBiome_Badlands"),
     "a crack too wide to jump and too deep to see"),
    ("VEE_StoneForest",    2, 14, lambda t: t["biome"] == "AB_RockyCrags" and t["hill"] >= 3,
     "wind-cut pillars, a landscape that looks made"),
    ("Hollow",             3, 10, lambda t: t["hill"] >= 3 and t["elev"] > 300,
     "shelter, if you get there before dark"),

    # the volcanic province
    ("LavaFlow",           3, 6, lambda t: t["biome"] in ("LavaField", "Volcano", "AB_PyroclasticConflagration"),
     "the Scald rim is still live"),
    ("VEE_ResurgentCaldera", 2, 4, lambda t: t["biome"] in ("Volcano", "AB_PyroclasticConflagration"),
     "a crater that is not finished"),
    ("HotSprings",         3, 8, lambda t: t["temp"] > 20 and t["elev"] > 300 and t["biome"] in ("Volcano", "LavaField", "AB_PyroclasticConflagration", "ZBiome_Badlands"),
     "geothermal water - the one warm bath on this planet"),
    ("AB_MagmaticQuagmire", 2, 3, lambda t: t["biome"] in ("LavaField", "AB_PyroclasticConflagration"),
     "ground that is not quite solid"),

    # the strange biomes the mod stack gives us and we barely use
    ("AB_PropaneLakes",    5, 8, lambda t: t["biome"] == "AB_PropaneLakes",
     "554 tiles of it and not one landmark until now"),
    ("AB_TarLakes",        3, 6, lambda t: t["biome"] == "AB_TarPits",
     "the tar pits, and what is preserved in them"),
    ("AB_MutagenicSprings", 2, 6, lambda t: t["biome"] in ("AB_OcularForest", "AB_MycoticJungle"),
     "the ocular ground - do not drink it"),
    ("AB_QuicksandPits",   3, 9, lambda t: t["biome"] in ("AB_MiasmicMangrove", "AB_MycoticJungle"),
     "soft ground under the fungus"),
    ("AB_HealingSprings",  2, 14, lambda t: t["biome"] in ("AB_MycoticJungle", "BMT_FungalForest") and t["rain"] > 10,
     "rare, and worth a pilgrimage"),
    ("VEE_Cenotes",        3, 10, lambda t: t["biome"] in ("AB_MycoticJungle", "AB_FeraliskInfestedJungle") and t["hill"] >= 2,
     "a roof that fell into the water table"),
    ("VEE_FleshPits",      2, 12, lambda t: t["biome"] == "AB_GelatinousSuperorganism",
     "the superorganism, where it surfaces"),
    ("VEE_SulfuricLake",   2, 10, lambda t: t["biome"] in ("Scarlands", "AB_PyroclasticConflagration", "ZBiome_Badlands") and t["temp"] > 25,
     "yellow water, and the smell reaches a day out"),
    ("ToxicLake",          2, 12, lambda t: t["biome"] in ("Wasteland", "Scarlands"),
     "left over from whatever happened here"),
    ("VEE_Mangrove",       2, 6, lambda t: t["biome"] == "AB_MiasmicMangrove",
     "the mangrove has 65 tiles and deserves a named one"),

    # the coasts - three seas and almost nothing on them
    ("Bay",                4, 8, lambda t: t["coast"] and t["arc"] < 110,
     "a harbour the Deepwater Compact could actually use"),
    ("Peninsula",          3, 10, lambda t: t["coast"],
     "land reaching into the water"),
    ("CoastalIsland",      3, 9, lambda t: t["coast"],
     "offshore, and hard to raid"),
    ("Archipelago",        2, 14, lambda t: t["coast"] and t["arc"] < 110,
     "a scatter of rock in the shallows"),
    ("VEE_GravelBeach",    3, 9, lambda t: t["coast"],
     "shingle, not sand - the shore of a cold sea"),
    ("VEE_LittoralDunes",  2, 12, lambda t: t["coast"] and t["biome"] in ("Desert", "ExtremeDesert"),
     "where the Dune Sea meets the other kind"),

    # the night side, which has nothing on it at all
    ("IceDunes",           4, 8, lambda t: t["arc"] > 120 and t["temp"] < -20,
     "wind-driven ice, the night side's answer to the Dune Sea"),
    ("Crevasse",           4, 9, lambda t: t["arc"] > 115 and t["temp"] < -15 and t["hill"] >= 3,
     "a split in the cap, and it does not show until you are on it"),
    ("VEE_IceSpires",      3, 10, lambda t: t["arc"] > 130 and t["elev"] > 800,
     "the Ammonia Flats stand in towers"),
    ("VEE_PermafrostBasin", 3, 10, lambda t: t["arc"] > 120 and t["hill"] <= 2,
     "frozen ground that never thaws, however deep you dig"),
    ("VEE_GlacialMoraine", 3, 10, lambda t: t["arc"] > 115 and t["elev"] > 400,
     "the rubble a glacier left when it stopped"),
    ("FrozenRuins",        3, 12, lambda t: t["arc"] > 120 and t["temp"] < -25,
     "somebody lived out here once - scavenging ground"),
    ("Iceberg",            2, 6, lambda t: t["coast"] and t["temp"] < -5,
     "calved off the nightside cap and drifting"),

    # the terminator - the only comfortable band on the planet
    ("VEE_TemperateGrasslands", 3, 10, lambda t: t["biome"] == "ZBiome_Grasslands",
     "the Dew Belt - the strip that is merely difficult"),
    ("VEE_Moor",           2, 5, lambda t: t["biome"] in ("ZBiome_Grasslands", "PoisonForest") and t["rain"] > 300,
     "wet ground on the twilight side"),
    # ⛔ Wetland is IMPOSSIBLE on Ash'karr and is deliberately not in this table.
    # Measured 2026-08-22: all 413 tiles with rain > 300 mm are hilliness 4 (397) or 5
    # (16). There is no flat wet ground anywhere on the planet - the rain-drying passes
    # left every millimetre on the high country. That is the planet's character, not a
    # gap, so a "Wetland" here would be a lie about it. Same reasoning killed a forced
    # patch of it: forcing something the terrain forbids is worse than leaving it out.

    # what the ancients left - a scavenger clan's whole economy
    ("Ruins",              6, 8, lambda t: t["hill"] <= 4 and t["biome"] not in ("Ocean", "Lake"),
     "scavenging ground, and the reason the clan is here"),
    ("AncientGarrison",    3, 12, lambda t: t["hill"] <= 3 and t["biome"] not in ("Ocean", "Lake") and t["arc"] < 110,
     "somebody defended this once"),
    ("AncientWarehouse",   3, 12, lambda t: t["hill"] <= 3 and t["biome"] not in ("Ocean", "Lake"),
     "sealed, and worth the trip"),
    ("AncientChemfuelRefinery", 2, 14, lambda t: t["biome"] in ("Wasteland", "ZBiome_Badlands", "Scarlands"),
     "chemfuel is what a sandcrawler runs on"),
    ("TerraformingScar",   2, 16, lambda t: t["biome"] in ("Wasteland", "Scarlands", "ZBiome_Badlands"),
     "somebody tried to fix this planet and failed"),
    ("AbandonedColonyTribal", 2, 8, lambda t: t["biome"] in ("AridShrubland", "Desert") and t["rain"] > 10,
     "a tribe that did not make it through a dry decade"),
    ("VEE_AbandonedFarmland", 2, 14, lambda t: t["biome"] in ("AridShrubland", "ZBiome_Grasslands"),
     "furrows still visible from the air"),
    ("VEE_MeteorCrater",   3, 12, lambda t: t["hill"] <= 3 and t["biome"] not in ("Ocean", "Lake"),
     "nothing on this world stops a rock"),
    ("sw_DeadSarlacc",     1, 20, lambda t: t["biome"] in ("Desert", "ExtremeDesert") and t["hill"] <= 2,
     "the second sarlacc, and it is dead - somebody killed it"),
]


# ── forced patches ─────────────────────────────────────────────────────────────
# (landmark, patch size in tiles, predicate, why). Spacing does NOT apply.
FORCE_PATCH = [
    ("AB_MagmaticQuagmire", 3,
     lambda t: t["biome"] in ("LavaField", "AB_PyroclasticConflagration", "Volcano"),
     "a patch of ground that is not quite solid, on the Scald rim - owner asked for it by name"),
]


HILL_ENUM = {"Undefined": None, "Flat": 1, "SmallHills": 2, "LargeHills": 3,
             "Mountainous": 4, "Impassable": 5}


def mutator_defs():
    """the constraint fields of every TileMutatorDef, for the legality gate below"""
    out = subprocess.run(["python3", MEASURE, "--rows", "500", "sql",
                          "SELECT def_name || '\t' || json FROM defs WHERE def_type='TileMutatorDef'"],
                         capture_output=True, text=True).stdout
    D = {}
    for line in out.split("\n"):
        if "\t{" not in line:
            continue
        try:
            f = json.loads(line[line.index("\t{") + 1:])["fields"]
        except Exception:
            continue
        D[f["defName"]] = {k: f.get(k) for k in
                           ("biomeWhitelist", "biomeBlacklist", "minHilliness",
                            "maxHilliness", "coastSidesRange", "canSpawnOnRiver")}
    return D


def mutators_legal(reqs, t, T, MD, coast_n, river_t):
    """🔴 THE GATE THAT WAS MISSING. A LandmarkDef's own placement rule says nothing about
    the TILE MUTATORS it drags along, and each of those has its own biomeWhitelist,
    hilliness bounds, coastSidesRange and canSpawnOnRiver. Without this, 276 of 497
    landmarks were placed on ground their required mutator forbids (measured 2026-08-22) -
    and it imports silently, because TileMutatorDef.IsValidTile is not called on the
    direct-set path the bridge uses.
    ⇒ Some landmarks are simply IMPOSSIBLE on this planet and that is the correct answer:
    IceDunes and Crevasse need SeaIce/IceSheet/GlacialPlain, and Ash'karr has no ice
    biome at all. A rule that places none of them is right, not broken."""
    d = T[t]
    for m in reqs:
        c = MD.get(m)
        if c is None:
            continue
        wl, bl = c.get("biomeWhitelist"), c.get("biomeBlacklist")
        if wl and d["biome"] not in wl:
            return False
        if bl and d["biome"] in bl:
            return False
        lo, hi = HILL_ENUM.get(c.get("minHilliness")), HILL_ENUM.get(c.get("maxHilliness"))
        if (lo is not None and d["hill"] < lo) or (hi is not None and d["hill"] > hi):
            return False
        cs = c.get("coastSidesRange") or {}
        cmin, cmax = cs.get("min", -1), cs.get("max", -1)
        if cmin >= 0 and not (cmin <= coast_n[t] <= cmax):
            return False
        if c.get("canSpawnOnRiver") is False and t in river_t:
            return False
    return True


def landmark_defs():
    out = subprocess.run(["python3", MEASURE, "--rows", "200", "sql",
                          "SELECT def_name || '\t' || json FROM defs WHERE def_type='LandmarkDef'"],
                         capture_output=True, text=True).stdout
    LD = {}
    for line in out.split("\n"):
        if "\t{" not in line:
            continue
        try:
            d = json.loads(line[line.index("\t{") + 1:])
        except Exception:
            continue
        f = d["fields"]
        LD[f["defName"]] = [m["mutator"] for m in f.get("mutatorChances", []) if m.get("required")]
    return LD


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--density", type=float, default=2.5,
                    help="scales every rule's count and tightens spacing. Owner asked for "
                         "DENSE on 2026-08-22; 1.0 reproduces the first, sparser pass.")
    a = ap.parse_args()

    LD = landmark_defs()
    if not LD:
        sys.exit("REFUSED: could not read LandmarkDefs from the def dump")

    tiles = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {}
    for r in tiles:
        T[int(r["tile"])] = dict(
            elev=float(r["elev_m"]), rain=float(r["rain_mm"]), temp=float(r["temp_c"]),
            arc=float(r["arc"]), water=int(r["water"]), biome=r["biome"],
            region=r["region"], hill=int(r["hilliness"]), river=float(r["river_flow"]) > 0)
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    for t, d in T.items():
        d["coast"] = d["water"] == 0 and any(T[n]["water"] == 1 for n in nb[t])

    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in re.split(r"[;|,]", r["mutators"]) if x.strip()] for r in mrows}
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    taken = {int(r["tile"]) for r in lrows}
    settlements = {int(r["tile"]) for r in
                   csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8"))}

    # ── REPAIR ────────────────────────────────────────────────────────────────
    repaired = 0
    for r in lrows:
        t = int(r["tile"])
        miss = [m for m in LD.get(r["landmark"], []) if m not in MU.get(t, [])]
        if miss:
            repaired += 1
            print("  REPAIR tile %-6d %-26s + %s" % (t, r["landmark"], ",".join(miss)))
            MU.setdefault(t, []).extend(miss)
    print("  repaired %d of %d existing landmarks\n" % (repaired, len(lrows)))

    # ── EXTEND ────────────────────────────────────────────────────────────────
    MD = mutator_defs()
    water_t = {t for t, d in T.items() if d["water"] == 1}
    coast_n = {t: sum(1 for n in nb[t] if n in water_t) for t in T}
    _links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))[1:]
    river_t = {int(x) for k, p_, q_, d_ in _links if k == "river" for x in (p_, q_)}
    placed, by_rule = [], []

    # ── FORCED PATCHES ────────────────────────────────────────────────────────
    # Rules whose biome is small enough that ordinary spacing starves them. The owner
    # asked for AB_MagmaticQuagmire by name, 2026-08-22 - "a little patch would do" -
    # so it is placed as a CONTIGUOUS patch with the spacing guard switched off.
    # 🔑 THESE RUN FIRST. Run last, they are leftovers: at --density 2.5 the ordinary
    # rules had claimed every qualifying tile and a "forced" patch found nowhere to go,
    # which is the opposite of forced.
    for name, size, pred, why in FORCE_PATCH:
        if name not in LD:
            print("  SKIP  %-26s no such LandmarkDef" % name)
            continue
        cand = [t for t, d in T.items()
                if t not in taken and t not in settlements and d["water"] == 0 and pred(d)
                and mutators_legal(LD[name], t, T, MD, coast_n, river_t)]
        if not cand:
            print("  FORCE %-26s  no tile matches at all - not placed" % name)
            continue
        cand.sort(key=lambda t: (-sum(1 for n in nb[t] if n in set(cand)), -T[t]["elev"], t))
        seed = cand[0]
        patch, pool = [seed], set(cand)
        frontier = [seed]
        while len(patch) < size and frontier:
            nxt = []
            for x in frontier:
                for n in nb[x]:
                    if n in pool and n not in patch and len(patch) < size:
                        patch.append(n)
                        nxt.append(n)
            frontier = nxt
        for t in patch:
            taken.add(t)
            placed.append({"tile": str(t), "landmark": name, "why": why})
            for m in LD[name]:
                MU.setdefault(t, [])
                if m not in MU[t]:
                    MU[t].append(m)
        print("  FORCE %-26s %2d tiles, contiguous patch at %d" % (name, len(patch), seed))

    for name, want0, spacing0, pred, why in RULES:
        want = max(1, int(round(want0 * a.density)))
        spacing = max(3, int(round(spacing0 / max(1.0, a.density ** 0.5))))
        if name not in LD:
            print("  SKIP  %-26s no such LandmarkDef in this mod set" % name)
            continue
        cand = [t for t, d in T.items()
                if t not in taken and t not in settlements and d["water"] == 0 and pred(d)
                and mutators_legal(LD[name], t, T, MD, coast_n, river_t)]
        if not cand:
            print("  place %-26s  0   <- IMPOSSIBLE here: no tile satisfies its required "
                  "mutators" % name)
            by_rule.append((name, 0, want))
            continue
        # deterministic: rank by a stable key, never a random draw
        cand.sort(key=lambda t: (-T[t]["elev"], t))
        chosen = []
        for t in cand:
            if len(chosen) >= want:
                break
            far = True
            for u in taken:
                # cheap hex-distance guard: breadth-limited, spacing is small
                if u == t:
                    far = False
                    break
            if not far:
                continue
            if any(_hops(t, u, nb, spacing) for u in chosen):
                continue
            # 🔑 the guard against OTHER rules' landmarks has to scale with density too.
            # A flat 3-hop floor starved every small-biome rule at --density 2.5 on
            # 2026-08-22: LavaFlow, Iceberg and the quagmire all came back 0 because
            # 400 landmarks were already within 3 hops of everything.
            if any(_hops(t, u, nb, max(2, spacing // 2)) for u in taken):
                continue
            chosen.append(t)
            taken.add(t)
        for t in chosen:
            placed.append({"tile": str(t), "landmark": name, "why": why})
            for m in LD[name]:
                MU.setdefault(t, [])
                if m not in MU[t]:
                    MU[t].append(m)
        by_rule.append((name, len(chosen), want))
        flag = "" if len(chosen) == want else "   <- only %d of %d fit" % (len(chosen), want)
        print("  place %-26s %2d%s" % (name, len(chosen), flag))

    short = [(n, g, w) for n, g, w in by_rule if g < w]
    print("\n%d landmarks placed across %d rules; %d rules could not fill"
          % (len(placed), len(by_rule), len(short)))
    print("total on the map: %d -> %d" % (len(lrows), len(lrows) + len(placed)))
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    with open(STEM + "_landmarks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tile", "landmark", "why"])
        w.writeheader()
        w.writerows(lrows + placed)
    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    print("written: %s_landmarks.csv and %s_mutators.csv" % (STEM, STEM))


def _hops(a, b, nb, limit):
    """True if b is within `limit` hexes of a."""
    if a == b:
        return True
    seen, frontier = {a}, [a]
    for _ in range(limit):
        nxt = []
        for x in frontier:
            for n in nb[x]:
                if n in seen:
                    continue
                if n == b:
                    return True
                seen.add(n)
                nxt.append(n)
        frontier = nxt
    return False


if __name__ == "__main__":
    main()
