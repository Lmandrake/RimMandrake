#!/usr/bin/env python3
"""Planted-defect selftest for lint_feverwood_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_feverwood_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

PLANTS = [
    ("type typo in a comp Class=", "Defs/ThingDefs_Buildings/RM_SekkulaathTank.xml", 'Class="RimMandrake.FeverWood.RM_CompProperties_CapturedSpecimen"', 'Class="RimMandrake.FeverWood.RM_CompProperties_CapturedSpecimn"', "class-resolves"),
    ("field typo under a comp", "Defs/ThingDefs_Buildings/RM_SekkulaathTank.xml", "<neglectEscapeMtbDays>4</neglectEscapeMtbDays>", "<neglectEscapeMtbDay>4</neglectEscapeMtbDay>", "fields-match"),
    ("damage threshold above 1", "Defs/ThingDefs_Buildings/RM_SekkulaathTank.xml", "<damageEscapeThresholdFraction>0.5<", "<damageEscapeThresholdFraction>1.5<", "feverwood-tank"),
    ("per-hit chance below 0", "Defs/ThingDefs_Buildings/RM_SekkulaathTank.xml", "<damageEscapeChancePerHit>0.35<", "<damageEscapeChancePerHit>-0.1<", "feverwood-tank"),
    ("product mtbDays of 0", "Defs/ThingDefs_Buildings/RM_SekkulaathTank.xml", "<mtbDays>3</mtbDays>", "<mtbDays>0</mtbDays>", "feverwood-tank"),
    ("gift weight negative", "Defs/Misc/RM_DeepGiftLoot.xml", "<weight>30</weight>", "<weight>-30</weight>", "feverwood-gift"),
    ("gift thing listed twice", "Defs/Misc/RM_DeepGiftLoot.xml", "<thing>AIPersonaCore</thing>", "<thing>ShipChunk</thing>", "listed twice"),
    ("gift names an undefined RM_ thing", "Defs/Misc/RM_DeepGiftLoot.xml", "<thing>ShipChunk</thing>", "<thing>RM_NoSuchRelic</thing>", "defined by no RimMandrake mod"),
    ("foul job driver swapped", "Defs/JobDefs/RM_FoulPool.xml", "RM_JobDriver_FoulPool", "RM_JobDriver_HaulToStake", "feverwood-foul"),
    ("trader stockChance of 3", "Patches/RM_FeverWood_YoungCaskTraders.xml", '<li Class="RimMandrake.FeverWood.RM_StockGenerator_DeepYoung" />', '<li Class="RimMandrake.FeverWood.RM_StockGenerator_DeepYoung"><stockChance>3</stockChance></li>', "feverwood-trader"),
    ("settings key differs from field", "Source/RM_FeverWoodMod.cs", 'Scribe_Values.Look(ref tentacleAmbientMtbHours, "tentacleAmbientMtbHours"', 'Scribe_Values.Look(ref tentacleAmbientMtbHours, "tentacleAmbientMtb"', "settings-scribed"),
    ("settings default differs from initialiser", "Source/RM_FeverWoodMod.cs", '"tentacleAmbientMtbHours", 6f)', '"tentacleAmbientMtbHours", 8f)', "settings-scribed"),
    ("slider range excludes the default", "Source/RM_FeverWoodMod.cs", "list.Slider(tentacleAmbientMtbHours, 1f, 24f)", "list.Slider(tentacleAmbientMtbHours, 8f, 24f)", "settings-range"),
    ("a source file missing from the csproj", "Source/RM_FeverWood.csproj", '<Compile Include="Kernel\\RM_PoolKernel.cs" />', "", "compile-listed"),
    ("a kernel file dropped from the csproj list but still on disk (tank)", "Source/RM_FeverWood.csproj", '<Compile Include="Kernel\\RM_TankKernel.cs" />', "", "compile-listed"),
]

if __name__ == "__main__":
    sys.exit(H.run("FeverWood", "lint_feverwood_defs.py", PLANTS))
