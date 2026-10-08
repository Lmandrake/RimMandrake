#!/usr/bin/env python3
"""Planted-defect selftest for lint_longshade_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_longshade_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

B = "Defs/BiomeDefs/RM_LongShade.xml"
M = "Defs/ThingDefs_Buildings/RM_LongShade_Middens.xml"
F = "Defs/ThingDefs_Races/RM_LongShade_Fauna.xml"
K = "Source/Kernel/RM_LongShadeKernel.cs"
P = "Source/RM_Patch_DewfringeWildSpawnGate.cs"
C = "Source/RM_ShipfallCommons.cs"
MOD = "Source/RM_LongShadeMod.cs"
PLANTS = [
    ("type typo in the commons extension Class=", B, 'Class="RimMandrake.LongShade.RM_ShipfallCommonsExtension"', 'Class="RimMandrake.LongShade.RM_ShipfallCommonsExtensio"', "class-resolves"),
    ("field typo under the commons extension", B, "<pullChance>0.3</pullChance>", "<pullChanc>0.3</pullChanc>", "fields-match"),
    ("rungs out of order", B, "<afterHours>8</afterHours>", "<afterHours>40</afterHours>", "ls-ladder"),
    ("rung race undefined", B, "<li>RM_Pirrik</li>", "<li>RM_Pirrikk</li>", "ls-ladder"),
    ("pull chance above 1", B, "<pullChance>0.3</pullChance>", "<pullChance>1.3</pullChance>", "ls-ladder"),
    ("commons radius zero", B, "<radius>8</radius>", "<radius>0</radius>", "ls-ladder"),
    ("commons min shade zero", B, "<minShade>0.5</minShade>", "<minShade>0</minShade>", "ls-ladder"),
    ("dewfringe patch loses its arming attribute", P, "    [StaticConstructorOnStartup]\n    public static class RM_Patch_DewfringeWildSpawnGate", "    public static class RM_Patch_DewfringeWildSpawnGate", "ls-armed"),
    ("commons cache key not dropped on leave", C, "                commonsKey.Invalidate();      // an emptied list must never be served as \"fresh\" when the ship lands again\n", "", "ls-cache"),
    ("heap gains nothing per tend", M, "<tendGain>0.1</tendGain>", "<tendGain>0</tendGain>", "ls-midden"),
    ("heap holds no layers", M, "<maxLayers>4</maxLayers>", "<maxLayers>0</maxLayers>", "ls-midden"),
    ("start layers above the cap", M, "<startLayers>1</startLayers>", "<startLayers>9</startLayers>", "ls-midden"),
    ("search takes no time", M, "<searchTicks>900</searchTicks>", "<searchTicks>0</searchTicks>", "ls-midden"),
    ("a yield that can never roll", M, "<thing>Silver</thing><count>5~20</count><weight>1</weight>", "<thing>Silver</thing><count>5~20</count><weight>0</weight>", "ls-midden"),
    ("a yield count reversed", M, "<count>4~12</count>", "<count>12~4</count>", "ls-midden"),
    ("builder race undefined", M, "<li>RM_Vrekka</li>", "<li>RM_Vrekkaa</li>", "ls-midden"),
    ("oreclaw names a variant texture that does not exist", F, "<alternateGraphics>\n\t\t\t<li>\n\t\t\t\t<texPath>Things/Pawn/Animal/RM_Groundrunner/RM_Groundrunner</texPath>\n\t\t\t</li>",
     "<alternateGraphics>\n\t\t\t<li>\n\t\t\t\t<texPath>Things/Pawn/Animal/RM_Groundrunner/RM_Groundrunner2</texPath>\n\t\t\t</li>", "texpath-resolves"),
    ("great devourer dessicated art that does not exist", F, "<dessicatedBodyGraphicData>\n\t\t\t\t\t<texPath>Things/Pawn/Animal/RM_GreatDevourer/RM_GreatDevourer</texPath>",
     "<dessicatedBodyGraphicData>\n\t\t\t\t\t<texPath>Things/Pawn/Animal/RM_GreatDevourer/RM_Dessicated_GreatDevourer</texPath>", "texpath-resolves"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "ls-kernel"),
    ("csproj drops the kernel", "Source/RM_LongShade.csproj", '<Compile Include="Kernel\\RM_LongShadeKernel.cs" />', "", "ls-kernel"),
    ("midden comp stops using the tend kernel", "Source/RM_LongShadeMiddens.cs", "RM_LongShadeKernel.Tend(", "TendX(", "ls-kernel"),
    ("map generation stops using the island kernel", "Source/RM_LongShadeMapgen.cs", "RM_LongShadeKernel.Islands(", "IslandsX(", "ls-kernel"),
    ("commons stop using the ladder kernel", C, "RM_LongShadeKernel.OpenStages(", "OpenStagesX(", "ls-kernel"),
    ("dewfringe stops using the rim kernel", P, "RM_LongShadeKernel.OnRim(", "OnRimX(", "ls-kernel"),
    ("settings key differs from field", MOD, 'Scribe_Values.Look(ref crawlerRoadEnabled, "crawlerRoadEnabled", true);', 'Scribe_Values.Look(ref crawlerRoadEnabled, "crawlerRoad", true);', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("LongShade", "lint_longshade_defs.py", PLANTS, keep=("Textures",)))
