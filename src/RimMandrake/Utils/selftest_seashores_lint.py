#!/usr/bin/env python3
"""Planted-defect selftest for lint_seashores_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_seashores_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

M = "Defs/TileMutatorDefs/RM_SeaCoast.xml"
S = "Source/RM_SeaShoresSettings.cs"
PLANTS = [
    ("worker class typo", M, "RimMandrake.SeaShores.RM_TileMutatorWorker_SeaCoast</workerClass>", "RimMandrake.SeaShores.RM_TileMutatorWorker_SeaCoas</workerClass>", "class-resolves"),
    ("Coast category dropped", M, "<li>Coast</li>", "<li>Lakeshore</li>", "seashores-mutator"),
    ("genOrder differs from vanilla", M, "<genOrder>100</genOrder>", "<genOrder>90</genOrder>", "seashores-mutator"),
    ("priority above vanilla", M, "<priority>0</priority>", "<priority>5</priority>", "seashores-mutator"),
    ("coastSidesRange set", M, "<priority>0</priority>", "<priority>0</priority><coastSidesRange>1~3</coastSidesRange>", "seashores-mutator"),
    ("defName duplicated", M, "</TileMutatorDef>", "</TileMutatorDef><TileMutatorDef><defName>RM_SeaCoast</defName><workerClass>RimMandrake.SeaShores.RM_TileMutatorWorker_SeaCoast</workerClass></TileMutatorDef>", "defname-unique"),
    ("settings key differs from field", S, 'Scribe_Values.Look(ref seaCatchTables, "seaCatchTables", true);', 'Scribe_Values.Look(ref seaCatchTables, "catchTables", true);', "settings-scribed"),
    ("settings default differs from initialiser", S, 'Scribe_Values.Look(ref generateSeaShores, "generateSeaShores", true);', 'Scribe_Values.Look(ref generateSeaShores, "generateSeaShores", false);', "settings-scribed"),
    ("setting never saved", S, '            Scribe_Values.Look(ref healFrozenWorldOnLoad, "healFrozenWorldOnLoad", true);\n', "", "settings-scribed"),
    ("a source file missing from the mod csproj", "Source/RM_SeaShores.csproj", '    <Compile Include="RM_SeaShoresHarmony.cs" />\n', "", "compile-listed"),
    ("the kernel missing from the mod csproj", "Source/RM_SeaShores.csproj", '    <Compile Include="Kernel\\RM_SeaKernel.cs" />\n', "", "seashores-kernel"),
    ("the kernel missing from the fuzz project", "Source/SelfTest/Fuzz/RimMandrakeSeaShores.Fuzz.csproj", '    <Compile Include="..\\..\\Kernel\\RM_SeaKernel.cs" />\n', "", "seashores-kernel"),
    ("an engine reference inside the kernel", "Source/Kernel/RM_SeaKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "seashores-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("SeaShores", "lint_seashores_defs.py", PLANTS))
