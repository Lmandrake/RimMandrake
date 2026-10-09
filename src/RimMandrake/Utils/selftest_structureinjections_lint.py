#!/usr/bin/env python3
"""Planted-defect selftest for lint_structureinjections_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_structureinjections_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

D = "Defs/GenStepDefs_Batch1.xml"
S = "Source/RM_StructureInjectionsMod.cs"
T = "Templates/signal_mast.txt"
PLANTS = [
    ("genstep class typo", D, 'Class="RimMandrake.StructureInjections.GenStep_RimplacePlan"', 'Class="RimMandrake.StructureInjections.GenStep_RimplacePla"', "class-resolves"),
    ("genstep field typo", D, "<planFile>Templates/signal_mast.txt</planFile>", "<planFil>Templates/signal_mast.txt</planFil>", "fields-match"),
    ("genstep defName duplicated", D, "</GenStepDef>", "</GenStepDef><GenStepDef><defName>RM_GenStep_SignalMast</defName></GenStepDef>", "defname-unique"),
    ("a source file missing from the mod csproj", "Source/StructureInjections.csproj", '    <Compile Include="GenStep_Whisper_NoOp.cs" />\n', "", "compile-listed"),
    ("the kernel missing from the mod csproj", "Source/StructureInjections.csproj", '    <Compile Include="Kernel\\RM_PlanKernel.cs" />\n', "", "structureinjections-kernel"),
    ("the kernel missing from the fuzz project", "Source/SelfTest/RimMandrakeStructureInjections.SelfTest.csproj", '    <Compile Include="..\\Kernel\\RM_PlanKernel.cs" />\n', "", "structureinjections-kernel"),
    ("the plan reader missing from the fuzz project", "Source/SelfTest/RimMandrakeStructureInjections.SelfTest.csproj", '    <Compile Include="..\\RimplacePlan.cs" />\n', "", "structureinjections-kernel"),
    ("an engine reference inside the kernel", "Source/Kernel/RM_PlanKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "structureinjections-kernel"),
    ("plan with a short line", T, "FOOTPRINT\t0\t0\t19\t10", "FOOTPRINT\t0\t0\t19", "structureinjections-template"),
    ("plan with a non-number cell", T, "TERRAIN\t1\t1\tStrawMatting", "TERRAIN\tone\t1\tStrawMatting", "structureinjections-template"),
    ("plan with an unknown clear mode", T, "CLEAR\t0\t0\t19\t10\tall", "CLEAR\t0\t0\t19\t10\tmost", "structureinjections-template"),
    ("plan with an unknown directive", T, "FOOTPRINT\t0\t0\t19\t10", "FOOTPRINT\t0\t0\t19\t10\nWALL\t1\t1\tx", "structureinjections-template"),
    ("plan with no header", T, "# rimplace flat plan v2", "# plan", "structureinjections-template"),
]

if __name__ == "__main__":
    sys.exit(H.run("StructureInjections", "lint_structureinjections_defs.py", PLANTS))
