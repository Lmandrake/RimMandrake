#!/usr/bin/env python3
"""Planted-defect selftest for lint_oasismaker_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_oasismaker_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

D = "Defs/ThingDefs_Buildings/RM_OasisMaker.xml"
S = "Source/RM_OasisMakerSettings.cs"
K = "Source/Kernel/RM_OasisKernel.cs"
KEYED = "Languages/English/Keyed/RM_OasisMakerKeyed.xml"
PLANTS = [
    ("type typo in the comp Class=", D, 'Class="RimMandrake.OasisMaker.CompProperties_OasisMaker"', 'Class="RimMandrake.OasisMaker.CompProperties_OasisMakr"', "class-resolves"),
    ("place worker named wrongly", D, "<li>RimMandrake.OasisMaker.RM_PlaceWorker_OasisMaker</li>", "<li>RimMandrake.OasisMaker.RM_PlaceWorker_OasisMakr</li>", "ERROR"),
    ("rotatable machine", D, "<rotatable>false</rotatable>", "<rotatable>true</rotatable>", "om-def"),
    ("ticker not rare", D, "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>", "om-def"),
    ("comp dropped from the def", D, '<li Class="RimMandrake.OasisMaker.CompProperties_OasisMaker" />', "", "om-def"),
    ("keyed refusal string missing", KEYED, "<RM_OasisMaker_NeedsRock>needs more standing rock nearby</RM_OasisMaker_NeedsRock>", "", "om-keyed"),
    ("keyed refusal string empty", KEYED, "needs more shaded ground nearby", "", "om-keyed"),
    ("settings key differs from field", S, 'Scribe_Values.Look(ref attuningDays, "attuningDays", 2);', 'Scribe_Values.Look(ref attuningDays, "attuneDays", 2);', "settings-scribed"),
    ("settings default differs from initialiser", S, 'Scribe_Values.Look(ref baseRingDays, "baseRingDays", 3f);', 'Scribe_Values.Look(ref baseRingDays, "baseRingDays", 4f);', "settings-scribed"),
    ("default outside its slider", S, "public static int attuningDays = 2;", "public static int attuningDays = 20;", "om-settings"),
    ("excellent not above the floor", S, "public static int shadeScoreExcellent = 30;", "public static int shadeScoreExcellent = 8;", "om-settings"),
    ("min cap above max cap", S, "public static int minRadiusCap = 6;", "public static int minRadiusCap = 8;\n        public static int maxRadiusCapX = 0;", "om-settings"),
    ("floor beyond the scoring square", S, "public static int rockScoreFloor = 15;", "public static int rockScoreFloor = 500;", "om-settings"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "om-kernel"),
    ("csproj drops the kernel", "Source/RM_OasisMaker.csproj", '<Compile Include="Kernel\\RM_OasisKernel.cs" />', "", "om-kernel"),
    ("comp stops using the state kernel", "Source/RM_CompOasisMaker.cs", "RM_OasisKernel.Step(", "StepX(", "om-kernel"),
    ("scorer stops using the score kernel", "Source/RM_OasisPlacementScorer.cs", "RM_OasisKernel.ScoreAt(", "ScoreAtX(", "om-kernel"),
    ("place worker stops using the verdict kernel", "Source/RM_PlaceWorker_OasisMaker.cs", "RM_OasisKernel.Verdict(", "VerdictX(", "om-kernel"),
    ("a ladder rung is not a Core terrain", K, '"Mud", "Marsh", "WaterShallow" }', '"Mud", "Bog", "WaterShallow" }', "om-def"),
    ("a string promises shade from two cells off", "Source/RM_CompOasisMaker.cs", "Dormant. It is waiting for cold stone and shade.", "Dormant. It needs shade from two cells away.", "om-text"),
]

if __name__ == "__main__":
    sys.exit(H.run("OasisMaker", "lint_oasismaker_defs.py", PLANTS, keep=("Languages",)))
