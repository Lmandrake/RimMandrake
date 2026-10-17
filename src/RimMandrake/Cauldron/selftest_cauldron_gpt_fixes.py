#!/usr/bin/env python3
"""Source/XML pins for the Cauldron fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/Cauldron_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by reverting the line by hand, 2026-10-16). The gas-kernel fixes
(CAULDRON_GAS_FIX_SEALED_CORNER_LEAK, CAULDRON_GAS_FIX_INT_WRAP_LATENT) are behaviour rows in
Source/SelfTest/CauldronFuzz.cs GasUnits, run by src/RimMandrake/Utils/selftest_cauldron_fuzz.py.

    python3 src/RimMandrake/Cauldron/selftest_cauldron_gpt_fixes.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def main():
    items = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_CauldronFloraItems.xml")).getroot()
    defs = {d.findtext("defName"): d for d in items.findall("ThingDef")}
    roasted, pulp = defs.get("RM_TsevrixRoasted"), defs.get("RM_TsevrixPulp")
    check("sanity: both tsevrix defs found", roasted is not None and pulp is not None)
    # CAULDRON_ROAST_FIX_RAW_FOOD_MOOD_STAYS: an explicit empty tasteThought clears the inherited AteRawFood
    tt = roasted.find("ingestible/tasteThought") if roasted is not None else None
    check("CAULDRON_ROAST_FIX_RAW_FOOD_MOOD_STAYS: roasted tsevrix sets an empty tasteThought",
          tt is not None and not (tt.text or "").strip(), None if tt is None else tt.text)
    # CAULDRON_PULP_FIX_CAMPFIRE_PROMISE_UNKEPT: no campfire promise while the recipe is stove-only
    recipe = read(os.path.join("Defs", "RecipeDefs", "RM_TsevrixRoast.xml"))
    check("sanity: roast recipe is stove-only", "FueledStove" in recipe and "Campfire" not in recipe)
    desc = (pulp.findtext("description") or "") if pulp is not None else ""
    check("CAULDRON_PULP_FIX_CAMPFIRE_PROMISE_UNKEPT: pulp description promises no campfire",
          "stove" in desc and "campfire" not in desc.lower(), desc)

    gardens = read(os.path.join("Source", "RM_CondensateGardens.cs"))
    tp = method_body(gardens, "private bool TryPlant(")
    check("sanity: TryPlant found", "GetPlant(map)" in tp)
    # CAULDRON_GARDEN_FIX_EDGE_OFF_MAP_STEP: bounds check before any map lookup
    ib, gp = tp.find("InBounds(map)"), tp.find("GetPlant(map)")
    check("CAULDRON_GARDEN_FIX_EDGE_OFF_MAP_STEP: TryPlant checks InBounds before GetPlant", 0 < ib < gp, (ib, gp))

    vents = read(os.path.join("Source", "RM_CauldronVents.cs"))
    mc = vents[vents.find("class RM_MapComponent_CauldronVents"):]
    expose = method_body(mc, "public override void ExposeData()")
    check("sanity: vent map component ExposeData found", "rmVentsGenerated" in expose)
    # CAULDRON_HUSH_FIX_COUNT_FORGETS_ON_LOAD
    check("CAULDRON_HUSH_FIX_COUNT_FORGETS_ON_LOAD: hushedThisFalter scribed",
          re.search(r'Scribe_Values\.Look\(ref hushedThisFalter, "rmVentHushed", 0\);', expose) is not None)
    # CAULDRON_TOGGLE_FIX_JOBS_FINISH_ANYWAY (B3 half; A7 melee half skipped by the grading)
    drv = vents[vents.find("class RM_JobDriver_VexxissDrinkVent"):]
    toils = method_body(drv, "protected override IEnumerable<Toil> MakeNewToils()")
    fo, goto = toils.find("this.FailOn(() => !RM_CauldronSettings.vexxissDrinksVentsEnabled)"), toils.find("Toils_Goto.GotoThing")
    check("CAULDRON_TOGGLE_FIX_JOBS_FINISH_ANYWAY: drink job fails on the setting for the walk too",
          0 < fo < goto, (fo, goto))

    kernel = read(os.path.join("Source", "Kernel", "RM_VentGasKernel.cs"))
    check("CAULDRON_GAS_FIX_INT_WRAP_LATENT: Add sums in long", "(long)Density[i] + amount" in kernel)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
