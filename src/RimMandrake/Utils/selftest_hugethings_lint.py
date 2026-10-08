#!/usr/bin/env python3
"""Planted-defect selftest for lint_hugethings_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_hugethings_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

B = "Defs/ThingDefs/RM_HugeTrunkBlocker.xml"
S = "Source/RM_HugeThingsSettings.cs"
PLANTS = [
    ("blocker passable", B, "<passability>Impassable</passability>", "<passability>PassThroughOnly</passability>", "ht-blocker"),
    ("blocker drawn", B, "<drawerType>None</drawerType>", "<drawerType>RealtimeOnly</drawerType>", "ht-blocker"),
    ("blocker selectable", B, "<selectable>false</selectable>", "<selectable>true</selectable>", "ht-blocker"),
    ("blocker flammable", B, "<Flammability>0</Flammability>", "<Flammability>1</Flammability>", "ht-blocker"),
    ("blocker never ticks", B, "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>", "ht-blocker"),
    ("blocker class typo", B, "RimMandrake.HugeThings.Building_TrunkBlocker", "RimMandrake.HugeThings.Building_TrunkBlocke", "class-resolves"),
    ("settings ceiling no longer the kernel's", S, "MaxTrunkScale = RM_FootprintKernel.MaxTrunkScale;", "MaxTrunkScale = 2f;", "ht-clamp"),
    ("pawn slider ceiling above the clamp", S, "list.Slider(pawnHitboxScale, 0.5f, MaxTrunkScale)", "list.Slider(pawnHitboxScale, 0.5f, 3f)", "ht-clamp"),
    ("extension default drifted", "Source/Extensions.cs", "public float hitboxFraction = 0.6f;", "public float hitboxFraction = 0.9f;", "ht-defaults"),
    ("kernel imports Unity", "Source/Kernel/RM_FootprintKernel.cs", "using System;", "using System;\nusing UnityEngine;", "ht-kernel-pure"),
    ("fuzz project compiled into the mod", "Source/RM_HugeThings.csproj", '<Compile Remove="SelfTest\\**" />', "", "ht-csproj"),
    ("settings key differs from field", S, 'Scribe_Values.Look(ref plantTrunkScale, "plantTrunkScale", 1f)', 'Scribe_Values.Look(ref plantTrunkScale, "trunkScale", 1f)', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("HugeThings", "lint_hugethings_defs.py", PLANTS))
