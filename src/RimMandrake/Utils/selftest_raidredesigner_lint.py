#!/usr/bin/env python3
"""Planted-defect selftest for lint_raidredesigner_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_raidredesigner_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

S = "Source/RaidRedesignerSettings.cs"
PLANTS = [
    ("settings key differs from field", S, 'Scribe_Values.Look(ref maxLivingEntries, "maxLivingEntries", 24);', 'Scribe_Values.Look(ref maxLivingEntries, "maxEntries", 24);', "settings-scribed"),
    ("settings default differs from initialiser", S, 'Scribe_Values.Look(ref maxLivingEntries, "maxLivingEntries", 24);', 'Scribe_Values.Look(ref maxLivingEntries, "maxLivingEntries", 12);', "settings-scribed"),
    ("setting never saved", S, '            Scribe_Values.Look(ref pinEncounteredPawns, "pinEncounteredPawns", true);\n', "", "settings-scribed"),
    ("setting Scribed twice", S, 'Scribe_Values.Look(ref pinEncounteredPawns, "pinEncounteredPawns", true);', 'Scribe_Values.Look(ref pinEncounteredPawns, "pinEncounteredPawns", true);\n            Scribe_Values.Look(ref pinEncounteredPawns, "pinEncounteredPawns", true);', "settings-scribed"),
    ("a source file missing from the mod csproj", "Source/RM_RaidRedesigner.csproj", '    <Compile Include="WorldPawnPinning.cs" />\n', "", "compile-listed"),
    ("csproj lists a file that does not exist", "Source/RM_RaidRedesigner.csproj", '<Compile Include="RoleTag.cs" />', '<Compile Include="RoleTag.cs" />\n    <Compile Include="RoleTagg.cs" />', "compile-listed"),
    ("the kernel missing from the mod csproj", "Source/RM_RaidRedesigner.csproj", '    <Compile Include="Kernel\\RM_RosterKernel.cs" />\n', "", "raidredesigner-kernel"),
    ("the kernel missing from the fuzz project", "Source/SelfTest/RimMandrakeRaidRedesigner.SelfTest.csproj", '    <Compile Include="..\\Kernel\\RM_RosterKernel.cs" />\n', "", "raidredesigner-kernel"),
    ("RoleTag missing from the fuzz project", "Source/SelfTest/RimMandrakeRaidRedesigner.SelfTest.csproj", '    <Compile Include="..\\RoleTag.cs" />\n', "", "raidredesigner-kernel"),
    ("an engine reference inside the kernel", "Source/Kernel/RM_RosterKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "raidredesigner-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("RaidRedesigner", "lint_raidredesigner_defs.py", PLANTS))
