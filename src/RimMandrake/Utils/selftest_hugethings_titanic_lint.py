#!/usr/bin/env python3
"""Planted-defect selftest for lint_hugethings_titanic_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_hugethings_titanic_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

T = "Defs/TitanicTierDefs/RM_TitanicTierDef.xml"
C = "Defs/CrushRuleDefs/RM_CrushRules.xml"
PLANTS = [
    ("tier floors out of order", T, "<t2MinBodySize>8</t2MinBodySize>", "<t2MinBodySize>3</t2MinBodySize>", "tc-ladder"),
    ("XML floor drifts from the C# fallback", T, "<t3MinBodySize>20</t3MinBodySize>", "<t3MinBodySize>24</t3MinBodySize>", "differ from the shipped XML"),
    ("t1 zero", T, "<t1MinBodySize>4</t1MinBodySize>", "<t1MinBodySize>0</t1MinBodySize>", "tc-ladder"),
    ("rule with both thing and category", C, "<thing>Wall</thing>", "<thing>Wall</thing><category>Buildings</category>", "exactly one"),
    ("rule with neither", C, "<thing>Wall</thing>", "", "exactly one"),
    ("duplicate target", C, "<category>Plants</category>", "<category>Buildings</category>", "same category"),
    ("minTier typo", C, "<minTier>T2</minTier>", "<minTier>T4</minTier>", "minTier"),
    ("crushable typo", C, "<crushable>true</crushable>", "<crushable>yes</crushable>", "crushable"),
    ("chunks become crushable", C, "<crushable>false</crushable>", "<crushable>true</crushable>", "Chunks row"),
    ("translation key missing", "Languages/English/Keyed/RM_TitanicCreatures.xml", "<RM_TitanicCorpseSite_Remaining>", "<RM_TitanicCorpseSite_Remainin>", "RM_TitanicCorpseSite_Remaining"),
    ("kernel imports Verse", "Source/Kernel/RM_TitanicKernel.cs", "using System;", "using System;\nusing Verse;", "tc-kernel"),
    ("kernel day length drifts", "Source/Kernel/RM_TitanicKernel.cs", "TicksPerDay = 60000;", "TicksPerDay = 24000;", "TicksPerDay"),
    ("crush damages inverted", "Source/Kernel/RM_TitanicKernel.cs", "CrushDamageLight = 20f;", "CrushDamageLight = 90f;", "light < heavy"),
    ("SelfTest leaks into the mod assembly", "Source/RM_HugeThings.csproj", "<EnableDefaultCompileItems>false</EnableDefaultCompileItems>", "", "SelfTest"),
    ("DefOf names a missing job", "Source/Titanic/RM_TitanicCreaturesDefOf.cs", "public static JobDef RM_HarvestTitanicCorpse;", "public static JobDef RM_HarvestTitanicCorps;", "DefOf"),
    ("job driver class typo", "Defs/JobDefs/RM_JobDefs.xml", "JobDriver_HarvestTitanicCorpse</driverClass>", "JobDriver_HarvestTitanicCorps</driverClass>", "class-resolves"),
    ("custom-tier default drifts from the XML", "Source/RM_HugeThingsSettings.cs", "tierT2MinBodySize = 8f;", "tierT2MinBodySize = 9f;", "custom-tier defaults"),
    ("smash tier default out of range", "Source/RM_HugeThingsSettings.cs", "giantPlantSmashMinTier = 3;", "giantPlantSmashMinTier = 5;", "giantPlantSmashMinTier"),
    ("trunk becomes crushable", C, "<thing>RM_HugeTrunkBlocker</thing>\n    <crushable>false</crushable>", "<thing>RM_HugeTrunkBlocker</thing>\n    <crushable>true</crushable>", "RM_HugeTrunkBlocker row"),
    ("settings Scribe default drifts", "Source/RM_HugeThingsSettings.cs", '"wakeFilthTrailChance", 0.35f)', '"wakeFilthTrailChance", 0.5f)', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("HugeThings", "lint_hugethings_titanic_defs.py", PLANTS, keep=("Languages",)))
