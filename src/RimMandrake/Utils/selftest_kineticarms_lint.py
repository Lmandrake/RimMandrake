#!/usr/bin/env python3
"""Planted-defect selftest for lint_kineticarms_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_kineticarms_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

W = "Defs/ThingDefs/RM_KineticArms_Weapons.xml"
B = "Defs/ThingDefs/RM_KineticArms_Buildings.xml"
D = "Defs/DamageDefs/RM_KineticArms_Damages.xml"
M = "Source/RM_KineticArmsMod.cs"
K = "Source/RM_KineticMath.cs"
PLANTS = [
    ("type typo in the bolt extension Class=", W, 'Class="RimMandrake.KineticArms.RM_KineticBoltExtension">\n        <coneDegrees>60', 'Class="RimMandrake.KineticArms.RM_KineticBoltExtensio">\n        <coneDegrees>60', "class-resolves"),
    ("field typo under the bolt extension", W, "<coneDegrees>60</coneDegrees>", "<coneDegree>60</coneDegree>", "fields-match"),
    ("cone zero", B, "<coneDegrees>90</coneDegrees>", "<coneDegrees>0</coneDegrees>", "ka-cone"),
    ("cone past a half turn", W, "<coneDegrees>100</coneDegrees>", "<coneDegrees>270</coneDegrees>", "ka-cone"),
    ("cone not a number", W, "<coneDegrees>60</coneDegrees>", "<coneDegrees>sixty</coneDegrees>", "ka-cone"),
    ("palm thump throws nothing", D, "<force>2.5</force><maxThrowCells>5</maxThrowCells><impactFactor>0</impactFactor>", "<force>0</force><maxThrowCells>5</maxThrowCells><impactFactor>0</impactFactor>", "ka-forces"),
    ("slam charge cannot throw a cell", D, "<force>2.2</force><maxThrowCells>7</maxThrowCells>", "<force>2.2</force><maxThrowCells>0</maxThrowCells>", "ka-forces"),
    ("weapon table names a missing def", M, '"RM_Gun_RepulsorRifle")', '"RM_Gun_RepulsorRifl")', "ka-weapons"),
    ("weapon toggle not a setting", M, '("enableKickerMine", "Kicker mine"', '("enableKickerMin", "Kicker mine"', "ka-weapons"),
    ("ninth weapon, no ruins weight", M, '("enableGravRam", "Grav-ram", "RM_Gun_GravRam"),', '("enableGravRam", "Grav-ram", "RM_Gun_GravRam"),\n            ("enableKickerMine", "Dup", "RM_KickerMine"),', "ka-weapons"),
    ("ruins weight dropped", K, "{ 30f, 20f, 15f, 10f, 12f, 15f, 5f, 3f }", "{ 30f, 20f, 15f, 10f, 12f, 15f, 5f }", "ka-weapons"),
    ("looted row names a missing def", "Source/RM_LootedKineticWeapons.cs", '"RM_Gun_SlamLauncher", false)', '"RM_Gun_SlamLaunchr", false)', "ka-carried"),
    ("looted toggle not a setting", "Source/RM_LootedKineticWeapons.cs", '("enableRepulsorRifle", "RM_Gun_RepulsorRifle", false)', '("enableRepulsor", "RM_Gun_RepulsorRifle", false)', "ka-carried"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "ka-kernel"),
    ("csproj drops the kernel", "Source/RimMandrake_KineticArms.csproj", '<Compile Include="RM_KineticMath.cs" />', "", "compile-listed"),
    ("pulse cannon stops using Recharge", "Source/RM_Building_PulseCannon.cs", "RM_KineticMath.Recharge(", "RechargeX(", "ka-kernel"),
    ("settings key differs from field", M, 'Scribe_Values.Look(ref pulseCapacity, "pulseCapacity", 4);', 'Scribe_Values.Look(ref pulseCapacity, "pulseCap", 4);', "settings-scribed"),
    ("settings default differs from initialiser", M, 'Scribe_Values.Look(ref pulseRechargeSeconds, "pulseRechargeSeconds", 20f);', 'Scribe_Values.Look(ref pulseRechargeSeconds, "pulseRechargeSeconds", 25f);', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("KineticArms", "lint_kineticarms_defs.py", PLANTS))
