#!/usr/bin/env python3
"""Planted-defect selftest for lint_rimdefdump_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_rimdefdump_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

D = "Source/DefDumper.cs"
PLANTS = [
    ("the inert-by-default gate removed", D, "if (!File.Exists(marker))", "if (false)", "rimdefdump-structure"),
    ("the marker name changed", D, 'private const string MarkerName = "dump_request.txt";', 'private const string MarkerName = "dump.txt";', "rimdefdump-structure"),
    ("a Harmony patch added", D, "namespace RimMandrake.RimDefDump", "namespace RimMandrake.RimDefDump\n{ class HarmonyPatchStub { } }\nnamespace RimMandrake.RimDefDump", "rimdefdump-structure"),
    ("the packageId changed", "About/About.xml", "mandrake.rm.rimdefdump", "mandrake.rm.defdump", "rimdefdump-structure"),
    ("a source file missing from the csproj", "Source/RimDefDump.csproj", '    <Compile Include="DefReflector.cs" />\n', "", "compile-listed"),
    ("the kernel missing from the mod csproj", "Source/RimDefDump.csproj", '    <Compile Include="Kernel\\RM_DumpKernel.cs" />\n', "", "rimdefdump-kernel"),
    ("the kernel missing from the fuzz project", "Source/SelfTest/RimMandrakeRimDefDump.SelfTest.csproj", '    <Compile Include="..\\Kernel\\RM_DumpKernel.cs" />\n', "", "rimdefdump-kernel"),
    ("the JSON writer missing from the fuzz project", "Source/SelfTest/RimMandrakeRimDefDump.SelfTest.csproj", '    <Compile Include="..\\JsonWriter.cs" />\n', "", "rimdefdump-structure"),
    ("an engine reference inside the kernel", "Source/Kernel/RM_DumpKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "rimdefdump-kernel"),
    ("an engine reference inside the JSON writer", "Source/JsonWriter.cs", "using System;\n", "using System;\nusing Verse;\n", "rimdefdump-structure"),
]

if __name__ == "__main__":
    sys.exit(H.run("RimDefDump", "lint_rimdefdump_defs.py", PLANTS, keep=("About",)))
