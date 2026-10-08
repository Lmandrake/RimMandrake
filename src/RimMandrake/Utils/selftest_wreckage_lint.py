#!/usr/bin/env python3
"""Planted-defect selftest for lint_wreckage_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_wreckage_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

W = "Defs/RM_WreckWeatheringDefs/RM_WreckWeatherings.xml"
S = "Defs/ThingSetMakerDefs/RM_SalvageLoot.xml"
F = "Defs/ThingDefs_Buildings/RM_WreckFamilies.xml"
K = "Source/Kernel/RM_WreckageKernel.cs"
PLANTS = [
    ("yield factor above 1.5", W, "<yieldFactor>0.75</yieldFactor>", "<yieldFactor>3</yieldFactor>", "yieldFactor"),
    ("yield factor zero", W, "<yieldFactor>0.75</yieldFactor>", "<yieldFactor>0</yieldFactor>", "yieldFactor"),
    ("tier shift out of range", W, "<lootTierShift>-2</lootTierShift>", "<lootTierShift>-3</lootTierShift>", "lootTierShift"),
    ("hazard without a dose", W, "<salvageHediffSeverity>0.12</salvageHediffSeverity>", "", "salvageHediff and salvageHediffSeverity"),
    ("rare table for Sealed missing", S, "<defName>RM_SalvageLoot_Sealed_Rare</defName>", "<defName>RM_SalvageLoot_Sealed_Rar</defName>", "RM_SalvageLoot_Sealed_Rare"),
    ("loot table for Sealed missing", S, "<defName>RM_SalvageLoot_Sealed</defName>", "<defName>RM_SalvageLoot_Seald</defName>", "RM_SalvageLoot_Sealed"),
    ("family loses its loot comp", F, 'Class="RimMandrake.Wreckage.RM_CompProperties_SalvageLoot"', 'Class="RimMandrake.Wreckage.RM_CompProperties_SalvageLoo"', "wr-resolve"),
    ("family tier typo lands on a missing table", F, "<lootTier>Carapace</lootTier>", "<lootTier>Carapac</lootTier>", "wr-resolve"),
    ("wreck list has a dead row", "Defs/RM_WreckListDefs/RM_WreckLists.xml", "<ShipChunk>1</ShipChunk>", "<ShipChunk>0</ShipChunk>", "dead row"),
    ("wreck list names a missing def", "Defs/RM_WreckListDefs/RM_WreckLists.xml", "<ShipChunk_Mech>1</ShipChunk_Mech>", "<ShipChunk_Mec>1</ShipChunk_Mec>", "wr-lists"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "wr-kernel"),
    ("kernel missing from the csproj", "Source/RM_Wreckage.csproj", '<Compile Include="Kernel\\RM_WreckageKernel.cs" />', "", "wr-kernel"),
    ("hand copy of the tier ladder", "Source/RM_WreckWeathering.cs", "return RM_WreckageKernel.ShiftTier(tier, shift);", 'return shift == 0 ? tier : (tier == "Scrap" ? "Hull" : "Sealed");\n            int rank = 0; return rank == 0 ? "Hull" : tier;', "tier ladder"),
    ("settings Scribe default drifts", "Source/RM_WreckageMod.cs", '"lootGenerosity", 1f)', '"lootGenerosity", 2f)', "settings-scribed"),
    ("job/translation key missing", "Languages/English/Keyed/RM_Wreckage.xml", "<RM_Wreckage_InspectNothingInside>", "<RM_Wreckage_InspectNothingInsid>", "RM_Wreckage_InspectNothingInside"),
    ("per-tier label missing", "Languages/English/Keyed/RM_Wreckage.xml", "<RM_Wreckage_Tier_Sealed>", "<RM_Wreckage_Tier_Seald>", "RM_Wreckage_Tier_Sealed"),
]

if __name__ == "__main__":
    sys.exit(H.run("Wreckage", "lint_wreckage_defs.py", PLANTS, keep=("Languages",)))
