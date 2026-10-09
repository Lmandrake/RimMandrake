#!/usr/bin/env python3
"""Planted-defect selftest for lint_nightsideice_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_nightsideice_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

F = "Defs/Fauna/RM_Shivven.xml"
C = "Defs/ThingDefs_Buildings/RM_BreachCrack.xml"
M = "Source/RM_NightsideIceMod.cs"
K = "Source/Kernel/RM_NightsideIceKernel.cs"
PLANTS = [
    ("type typo in the shivven comp Class=", F, 'Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek"', 'Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeeker"', "class-resolves"),
    ("field typo under the shivven comp", F, '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek" />', '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek"><legCell>8</legCell></li>', "fields-match"),
    ("leg of zero cells", F, '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek" />', '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek"><legCells>0</legCells></li>', "ni-shivven"),
    ("search budget of zero", F, '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek" />', '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek"><searchCellBudget>0</searchCellBudget></li>', "ni-shivven"),
    ("shivven loses its heat-seek comp", F, '<li Class="RimMandrake.NightsideIce.RM_CompProperties_ShivvenHeatSeek" />', "", "ni-shivven"),
    ("shivven loses the sand-swim extension", F, 'Class="RimMandrake.CreatureBehaviors.RM_SandSwimExtension"', 'Class="RimMandrake.CreatureBehaviors.RM_SandSwimExtensio"', "class-resolves"),
    ("crack building class wrong", C, "RimMandrake.NightsideIce.RM_Building_BreachCrack", "RimMandrake.NightsideIce.RM_Building_BreachCrak", "ni-crack"),
    ("crack cannot be hurt", C, "<MaxHitPoints>220</MaxHitPoints>", "", "ni-crack"),
    ("crack walls the base off", C, "<passability>Standable</passability>", "<passability>Impassable</passability>", "ni-crack"),
    ("crack def renamed", C, "<defName>RM_BreachCrack</defName>", "<defName>RM_BreachCrak</defName>", "ni-names"),
    ("settings key differs from field", M, 'Scribe_Values.Look(ref heatDialScale, "heatDialScale", 150f);', 'Scribe_Values.Look(ref heatDialScale, "heatScale", 150f);', "settings-scribed"),
    ("settings default differs from initialiser", M, 'Scribe_Values.Look(ref shivvenSenseRange, "shivvenSenseRange", 60f);', 'Scribe_Values.Look(ref shivvenSenseRange, "shivvenSenseRange", 50f);', "settings-scribed"),
    ("slider range excludes the default", M, "list.Slider(heatDialScale, 25f, 600f)", "list.Slider(heatDialScale, 200f, 600f)", "ni-settings"),
    ("text promises one a day again", M, "(x1: a full dial averages one about every three days)", "(x1: a full dial averages one a day)", "ni-text"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "ni-kernel"),
    ("csproj drops the kernel", "Source/RM_NightsideIce.csproj", '<Compile Include="Kernel\\RM_NightsideIceKernel.cs" />', "", "ni-kernel"),
    ("shivven stops using the path kernel", "Source/RM_Shivven.cs", "RM_NightsideIceKernel.IcePath(", "IcePathX(", "ni-kernel"),
    ("crack stops using the warning kernel", "Source/RM_BreachCracks.cs", "RM_NightsideIceKernel.CrackLook(", "CrackLookX(", "ni-kernel"),
    ("heat dial stops using the target kernel", "Source/RM_HeatDial.cs", "RM_NightsideIceKernel.Target(", "TargetX(", "ni-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("NightsideIce", "lint_nightsideice_defs.py", PLANTS))
