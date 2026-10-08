#!/usr/bin/env python3
"""Offline lint of the RimDefDump mod: a tooling mod with zero Defs, zero settings and no gameplay, so the generic compile-listed check plus
the structure it must keep is the whole job: INERT BY DEFAULT (the marker-file gate), no Harmony, no defs, the kernel and the JSON writer
engine-free and wired into the fuzz project.

    python3 src/RimMandrake/Utils/lint_rimdefdump_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402
from lint_kernel_guards import kernel_guards  # noqa: E402


def structure_findings(mod_dir):
    errs = []
    src = os.path.join(mod_dir, "Source")
    dumper = open(os.path.join(src, "DefDumper.cs"), encoding="utf-8-sig").read()
    if "dump_request.txt" not in dumper:
        errs.append("ERROR rimdefdump-structure: DefDumper no longer reads dump_request.txt (the mod must be INERT unless that marker exists)")
    if not re.search(r"if\s*\(\s*!File\.Exists\(marker\)\s*\)", dumper):
        errs.append("ERROR rimdefdump-structure: no File.Exists test on the request marker (probe: the inert-by-default gate moved?)")
    for fn in os.listdir(src):
        if fn.endswith(".cs"):
            t = open(os.path.join(src, fn), encoding="utf-8-sig").read()
            if re.search(r"\bHarmony\b|HarmonyPatch|new Harmony\(", t):
                errs.append("ERROR rimdefdump-structure: %s uses Harmony; this mod adds no patches" % fn)
    if os.path.isdir(os.path.join(mod_dir, "Defs")) and any(f.endswith(".xml") for _, _, fs in os.walk(os.path.join(mod_dir, "Defs")) for f in fs):
        errs.append("ERROR rimdefdump-structure: the mod ships Defs; it must add none")
    jw = open(os.path.join(src, "JsonWriter.cs"), encoding="utf-8-sig").read()
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine)\b", jw, re.M):
        errs.append("ERROR rimdefdump-structure: JsonWriter.cs references the engine (the fuzz build cannot compile it)")
    proj = open(os.path.join(src, "SelfTest", "RimMandrakeRimDefDump.SelfTest.csproj"), encoding="utf-8-sig").read() if os.path.exists(os.path.join(src, "SelfTest", "RimMandrakeRimDefDump.SelfTest.csproj")) else ""
    if 'Compile Include="..\\JsonWriter.cs"' not in proj:
        errs.append("ERROR rimdefdump-structure: JsonWriter.cs is not in the fuzz project")
    about = open(os.path.join(mod_dir, "About", "About.xml"), encoding="utf-8-sig").read()
    if "mandrake.rm.rimdefdump" not in about:
        errs.append("ERROR rimdefdump-structure: About.xml packageId is not mandrake.rm.rimdefdump")
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "RimDefDump")
    rc = lint_mod_defs.run("RimDefDump", argv, require_xml=False, require_settings=False)
    errs = structure_findings(mod_dir) + kernel_guards(mod_dir, "RimDefDump.csproj", "SelfTest/RimMandrakeRimDefDump.SelfTest.csproj", "rimdefdump-kernel")
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)
