#!/usr/bin/env python3
"""Planted-defect selftest for lint_proximityhatch_defs.py: clean on the real tree, then one planted break at a time (in memory, nothing
written) must be caught with the expected ERROR kind. A lint that cannot fail proves nothing.

    python3 src/RimMandrake/Utils/selftest_proximityhatch_lint.py
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_proximityhatch_defs as L  # noqa: E402

BRAIN = "RimStarWars/BrainWorms/Defs/ThingDefs_Items/Items_BrainWormEggs.xml"
PATCH = "RimStarWars/SWBestiary/Patches/ProximityHatch/RSW_ProtovermesEgg_ProximityHatch.xml"
GUZ = "RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Guzzka.xml"
SETTINGS = "RimMandrake/ProximityHatch/Source/RM_ProximityHatchMod.cs"
KERNEL = "RimMandrake/ProximityHatch/Source/Kernel/RM_ProximityHatchKernel.cs"
COMP = "RimMandrake/ProximityHatch/Source/CompProximityHatch.cs"
PROPS = "RimMandrake/ProximityHatch/Source/CompProperties_ProximityHatch.cs"
CSPROJ = "RimMandrake/ProximityHatch/Source/RimMandrake_ProximityHatch.csproj"
PLANTS = [
    ("field typo", "xml", BRAIN, "<triggerRadius>2</triggerRadius>", "<triggerRadus>2</triggerRadus>", "ph-fields"),
    ("radius zero", "xml", BRAIN, "<triggerRadius>2</triggerRadius>", "<triggerRadius>0</triggerRadius>", "ph-fields"),
    ("radius word", "xml", GUZ, "<triggerRadius>2.2</triggerRadius>", "<triggerRadius>two</triggerRadius>", "ph-fields"),
    ("radius huge", "xml", GUZ, "<triggerRadius>2.2</triggerRadius>", "<triggerRadius>90</triggerRadius>", "ph-fields"),
    ("interval zero", "xml", BRAIN, "<scanIntervalTicks>60</scanIntervalTicks>", "<scanIntervalTicks>0</scanIntervalTicks>", "ph-fields"),
    ("hatcher comp renamed on the egg", "xml", BRAIN, '<li Class="CompProperties_Hatcher">', '<li Class="CompProperties_Hatchr">', "ph-hatcher"),
    ("patch targets an egg with no hatcher", "xml", PATCH, 'defName="RSW_ProtovermesEggFertilized"', 'defName="RSW_NoSuchEgg"', "ph-hatcher"),
    ("patch loses its FindMod gate", "xml", PATCH, "RimMandrake: Proximity Hatch", "Some Other Mod", "ph-gate"),
    ("def drops MayRequire", "xml", GUZ, 'CompProperties_ProximityHatch" MayRequire="mandrake.rm.proximityhatch">', 'CompProperties_ProximityHatch">', "ph-gate"),
    ("two proximity comps on one egg", "xml", GUZ, '      <li Class="RimMandrake.ProximityHatch.CompProperties_ProximityHatch" MayRequire="mandrake.rm.proximityhatch">\n        <triggerRadius>2.2</triggerRadius>',
     '      <li Class="RimMandrake.ProximityHatch.CompProperties_ProximityHatch" MayRequire="mandrake.rm.proximityhatch"><triggerRadius>1</triggerRadius></li>\n      <li Class="RimMandrake.ProximityHatch.CompProperties_ProximityHatch" MayRequire="mandrake.rm.proximityhatch">\n        <triggerRadius>2.2</triggerRadius>', "ph-once"),
    ("kernel imports Verse", "cs", KERNEL, "using System;", "using System;\nusing Verse;", "ph-kernel"),
    ("csproj drops the kernel", "csproj", CSPROJ, '<Compile Include="Kernel\\RM_ProximityHatchKernel.cs" />', "", "ph-kernel"),
    ("comp stops calling the kernel", "cs", COMP, "RM_ProximityHatchKernel.PickNearest(", "PickNearestX(", "ph-kernel"),
    ("setting never Scribed", "cs", SETTINGS, 'Scribe_Values.Look(ref aggroEnabled, "aggroEnabled", true);', "", "ph-settings"),
    ("scribe key differs", "cs", SETTINGS, '"radiusMultiplier"', '"radiusMult"', "ph-settings"),
    ("scribe default differs", "cs", SETTINGS, 'Scribe_Values.Look(ref scanIntervalMultiplier, "scanIntervalMultiplier", 1f);', 'Scribe_Values.Look(ref scanIntervalMultiplier, "scanIntervalMultiplier", 2f);', "ph-settings"),
    ("slider excludes the default", "cs", SETTINGS, "list.Slider(radiusMultiplier, 0.25f, 3f)", "list.Slider(radiusMultiplier, 1.5f, 3f)", "ph-settings"),
    ("props field renamed (consumers now name an unknown field)", "cs", PROPS, "public float triggerRadius = 4f;", "public float radius = 4f;", "ph-fields"),
]


def main():
    inp = L.collect()
    errs, counts = L.check(inp)
    bad = 0
    ok = not errs and counts["consumers"] >= 4
    print(("ok   " if ok else "FAIL ") + "real tree is clean (%s)" % counts + ("" if ok else " " + "; ".join(errs[:2])))
    bad += not ok
    for label, store, rel, old, new, want in PLANTS:
        i2 = copy.deepcopy(inp)
        d = i2[store]
        if rel not in d or old not in d[rel]:
            print("FAIL %s: pattern not found in %s" % (label, rel))
            bad += 1
            continue
        d[rel] = d[rel].replace(old, new, 1)
        got, _ = L.check(i2)
        hit = any(e.startswith("ERROR " + want) for e in got)
        print(("ok   " if hit else "FAIL ") + label + ("" if hit else " | wanted %s, got %s" % (want, got[:2])))
        bad += not hit
    print("proximityhatch lint planted-defect selftest: %d/%d ok" % (len(PLANTS) + 1 - bad, len(PLANTS) + 1))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
