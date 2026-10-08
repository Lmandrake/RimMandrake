#!/usr/bin/env python3
"""Planted-defect selftest for lint_shipvermin_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_shipvermin_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

C = "Defs/ThingDefs_Races/RM_ShipVermin_Cast.xml"
M = "Source/RM_ShipVerminMod.cs"
N = "Source/RM_CompProperties_VerminNest.cs"
PLANTS = [
    ("nest group tag differs from the leech's", N, 'populationGroupTag = "ShipVermin"', 'populationGroupTag = "ShipVerm"', "shipvermin-nest"),
    ("nest hard cap differs from the leech's", N, "populationHardCap = 12", "populationHardCap = 20", "shipvermin-nest"),
    ("leech hard cap differs from the nest's", C, "<populationHardCap>12</populationHardCap>", "<populationHardCap>9</populationHardCap>", "shipvermin-nest"),
    ("roster names a kind this mod does not define", M, '("RM_Gorrud", () => spawnGorrud)', '("RM_Gorrudd", () => spawnGorrud)', "shipvermin-nest"),
    ("comp class typo in a def", C, "RimMandrake.ShipVermin.RM_CompProperties_InnateAbility", "RimMandrake.ShipVermin.RM_CompProperties_InnateAbilit", "class-resolves"),
    ("settings key differs from field", M, 'Scribe_Values.Look(ref spawnRattagh, "spawnRattagh", true);', 'Scribe_Values.Look(ref spawnRattagh, "rattagh", true);', "settings-scribed"),
    ("settings default differs from initialiser", M, 'Scribe_Values.Look(ref wreckSpawnRateMultiplier, "wreckSpawnRateMultiplier", 1f);', 'Scribe_Values.Look(ref wreckSpawnRateMultiplier, "wreckSpawnRateMultiplier", 2f);', "settings-scribed"),
    ("setting never saved", M, '            Scribe_Values.Look(ref fuelSpewEnabled, "fuelSpewEnabled", true);\n', "", "settings-scribed"),
    ("a source file missing from the mod csproj", "Source/RM_ShipVermin.csproj", '    <Compile Include="RM_CompInnateAbility.cs" />\n', "", "compile-listed"),
    ("the kernel missing from the mod csproj", "Source/RM_ShipVermin.csproj", '    <Compile Include="Kernel\\RM_VerminKernel.cs" />\n', "", "shipvermin-kernel"),
    ("the kernel missing from the fuzz project", "Source/SelfTest/RimMandrakeShipVermin.SelfTest.csproj", '    <Compile Include="..\\Kernel\\RM_VerminKernel.cs" />\n', "", "shipvermin-kernel"),
    ("an engine reference inside the kernel", "Source/Kernel/RM_VerminKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "shipvermin-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("ShipVermin", "lint_shipvermin_defs.py", PLANTS))
