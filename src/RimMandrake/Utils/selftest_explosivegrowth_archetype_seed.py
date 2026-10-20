#!/usr/bin/env python3
"""Offline proof of the ruled archetype seeding (explosive_growth_ruled_spec_2026-10-16.md §4.3, §9) through
src/RimMandrake/ExplosiveGrowth/archetype_seed.py, the same rules RM_ExplosiveGrowthRegistry.Rebuild applies at load.
Each assertion names its ruling. Sanity probes first: the instrument must see rosters, biomes and rows.

    python3 src/RimMandrake/Utils/selftest_explosivegrowth_archetype_seed.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "ExplosiveGrowth"))
import archetype_seed  # noqa: E402


def main():
    fails = []
    sheets, n = archetype_seed.seed(*archetype_seed.load())

    def row(biome, plant):
        for r in sheets.get(biome, {}).get("rows", []):
            if r["plant"] == plant:
                return r
        fails.append("probe: %s is not on the %s sheet (the biome or its wildPlants moved?)" % (plant, biome))
        return None

    def want(biome, plant, field, value, why):
        r = row(biome, plant)
        if r is not None and r[field] != value:
            fails.append("%s %s: %s is %r, want %r (%s)" % (biome, plant, field, r[field], value, why))

    if n["rosters"] < 2 or n["biomes"] < 20:
        fails.append("probe: %d rosters / %d of our biomes read (blind instrument)" % (n["rosters"], n["biomes"]))
    rows = [r for s in sheets.values() for r in s["rows"]]
    kinds = {r["archetype"] for r in rows}
    for k in ("DryNative", "WetNative", "FireAdapted", "Exempt", "Vanilla"):
        if k not in kinds:
            fails.append("probe: no %s row anywhere (a seeding rule went blind)" % k)

    # C1 / WP3: the jungles and Webwork / Contagion seed WET natives, never bursting, few sprouts
    for b in ("RM_Greentide", "RM_Miasma", "RM_FeverWood", "RM_Webwork", "RM_Contagion"):
        if not sheets.get(b, {}).get("wet"):
            fails.append("%s is not a wet biome in the rosters (C1/WP3)" % b)
    want("RM_Greentide", "RM_Veluthar", "archetype", "WetNative", "C1 x4 always")
    want("RM_Greentide", "RM_Veluthar", "ruptureOdds", "0", "§4.2 wet natives never rupture")
    want("RM_Greentide", "RM_Veluthar", "sprouts", "1~2", "C2 a few sprouts")
    want("RM_Webwork", "RM_Kollavane", "archetype", "WetNative", "WP3 Answer is (1)")
    # C3 + tree_burst_design §5 (Q7 "Let Pyrelands grass burst too", 6-9 sprouts kept); C5 fresh ash waters it
    for g in ("RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass"):
        want("RM_Pyrelands", g, "archetype", "FireAdapted", "C5")
        want("RM_Pyrelands", g, "ruptureOdds", "1 in 3", "Q7 Pyrelands grass bursts at the default odds")
        want("RM_Pyrelands", g, "sprouts", "6~9", "C3 spread itself super-fast (Q7 keeps 6-9)")
    # tree_burst_design §2 / §6: size 3.0+ natives are trees (Q2), fungi never (Q9), the greatbole is out (§0);
    # the Rot is a wet biome (Q8) whose plants cycle (their NONE rows came off), Pale Tree / Skulltop stay out ("Immortal wins")
    want("RM_Greentide", "RM_Veluthar", "tree", True, "Q2 size 3.0+ is a tree")
    want("RM_Greentide", "RM_Greatbole", "tree", False, "§0 the greatbole is not part of the tree rules")
    want("RM_TheRot", "RM_Arpeau", "tree", False, "Q9 fungi are never trees")
    want("RM_TheRot", "RM_Arpeau", "fungus", True, "Q9 marked a fungus by the roster")
    want("RM_TheRot", "RM_Dewshrooms", "archetype", "WetNative", "Q8 the Rot follows the wet-biome rulings")
    want("RM_TheRot", "RM_Dewshrooms", "violentTop", "Churn", "Q8 the Rot's NONE rows came off")
    want("RM_TheRot", "RM_PaleTree", "archetype", "DryNative", "Immortal wins: out of the wet-native cycle")
    want("RM_TheRot", "RM_PaleTree", "ruptureOdds", "never cycles", "Immortal wins: never withers or bursts")
    if not sheets.get("RM_TheRot", {}).get("wet"):
        fails.append("RM_TheRot is not a wet biome in the rosters (Q8)")
    trees = [r for r in rows if r.get("tree")]
    if len(trees) < 20:
        fails.append("probe: only %d tree rows (the size read went blind?)" % len(trees))
    # C3 default 1 in 3 for a dry native; exemptions stay exempt (venomvine, Blue Desert trio)
    want("RM_Wasteland", "RM_Scumgrass", "archetype", "DryNative", "§4.1 default archetype")
    want("RM_Wasteland", "RM_Scumgrass", "ruptureOdds", "1 in 3", "C3")
    want("RM_BlueDesert", "RM_Palefloss", "archetype", "Exempt", "bandExemptPlants / exemptPlants")
    # setting A: a non-ours grass in our dry biome is Vanilla (water nearby or x0.1). Was RM_Wasteland
    # Plant_GrayGrass until the owner's 2026-10-19 card cut it; no RM_ biome keeps a non-ours grass row now.
    want("RUT_BlueDesert", "PoisonPlantTallGrass", "archetype", "Vanilla", "C4 setting A")
    # T2: slime-fed rows accept the slimes; nothing else does
    slimey = [r for r in rows if len(r["liquids"]) > 1]
    if not slimey or any(r["violentTop"] != "Slime" for r in slimey):
        fails.append("T2: adapted liquids should sit on the Slime rows only: %r" % [(r["plant"], r["violentTop"]) for r in slimey][:6])
    # OQ-5: a special top keeps its own odds
    sp = [r for r in rows if r["violentTop"] in ("Rupture", "Slime", "Tinder", "Flush")]
    if not sp or any(not r["ruptureOdds"].startswith("own top") for r in sp):
        fails.append("OQ-5: special tops must read 'own top': %r" % [(r["plant"], r["ruptureOdds"]) for r in sp][:6])
    print("archetype seed selftest: %d sheet rows over %d biomes, %d conflicts surfaced" % (len(rows), len(sheets), sum(r["conflict"] for r in rows)))
    for f in fails:
        print("FAIL " + f)
    print("selftest_explosivegrowth_archetype_seed: %s" % ("OK" if not fails else "FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
