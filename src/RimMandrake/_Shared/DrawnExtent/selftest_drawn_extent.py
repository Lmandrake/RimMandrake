#!/usr/bin/env python3
"""DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS gate: one ruler for a plant's drawn size, two mods.

1. DrawnExtentKernel.cs is source-linked (<Compile Include=...DrawnExtent\\DrawnExtentKernel.cs>) into Huge Things'
   mod csproj, Huge Things' fuzz csproj and Sun & Shade's csproj. Sun & Shade's csproj is
   src/RimMandrake/SunAndShade/Source/*.csproj once SUNSHADE_MIGRATE_MOVE_NOT_CHANGE creates it; until then the sun and
   shade code lives in CreatureBehaviors, so that csproj carries the link (the migration moves it with the files).
2. Every top-level type in the shared file is `internal` (two DLLs carry a copy; neither may export the type name).
3. No other .cs under src/ re-implements the drawn quad (the bottom-anchoring line is the fingerprint).
Sanity probes: a planted re-implementation and a planted public type must both be caught."""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(os.path.dirname(HERE))          # src/RimMandrake
SRC = os.path.dirname(RM)                            # src
KERNEL = os.path.join(HERE, "DrawnExtentKernel.cs")
LINK = re.compile(r'<Compile\s+Include="[^"]*_Shared\\DrawnExtent\\DrawnExtentKernel\.cs"')
ANCHOR = re.compile(r"if\s*\(\s*\w+\s*-\s*\w+\s*/\s*2f?\s*<\s*\w+\s*\)\s*\w+\s*=\s*\w+\s*\+\s*\w+\s*/\s*2f?\s*;")
DECL = re.compile(r"^\s*(public|internal)\s+(sealed |static |readonly |abstract |partial )*(class|struct|enum|interface)\s+(\w+)")


def links(csproj):
    return bool(LINK.search(open(csproj, encoding="utf-8").read()))


def public_top_level(text):
    bad, depth = [], 0
    for line in text.split("\n"):
        m = DECL.match(line)
        if m and depth <= 1 and m.group(1) == "public":
            bad.append(m.group(4))
        code = re.sub(r'"(\\.|[^"\\])*"', '""', line.split("//")[0])
        depth += code.count("{") - code.count("}")
    return bad


def reimplements(text):
    return any(ANCHOR.search(line.split("//")[0]) for line in text.split("\n"))


def main():
    probs = []
    sunshade = sorted(glob.glob(os.path.join(RM, "SunAndShade", "Source", "*.csproj")))
    homes = {
        "Huge Things": os.path.join(RM, "HugeThings", "Source", "RM_HugeThings.csproj"),
        "Huge Things fuzz": os.path.join(RM, "HugeThings", "Source", "SelfTest", "RimMandrakeHugeThings.SelfTest.csproj"),
        "Sun & Shade": sunshade[0] if sunshade else os.path.join(RM, "CreatureBehaviors", "Source", "RM_CreatureBehaviors.csproj"),
    }
    for who, p in homes.items():
        if not os.path.isfile(p):
            probs.append("%s: csproj missing: %s" % (who, os.path.relpath(p, SRC)))
        elif not links(p):
            probs.append("%s: %s does not source-link DrawnExtentKernel.cs" % (who, os.path.relpath(p, SRC)))
    kernel = open(KERNEL, encoding="utf-8").read()
    probs += ["DrawnExtentKernel.cs: public top-level type %s" % b for b in public_top_level(kernel)]
    if not reimplements(kernel):
        probs.append("sanity: the detector does not see the anchoring line in the shared kernel itself")
    others, scanned = [], 0
    for f in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        if os.path.abspath(f) == KERNEL or "/obj/" in f.replace("\\", "/"):
            continue
        scanned += 1
        if reimplements(open(f, encoding="utf-8", errors="replace").read()):
            others.append(os.path.relpath(f, SRC))
    probs += ["re-implements the drawn quad (use DrawnExtent.Quad): %s" % o for o in sorted(others)]
    if not reimplements("    if (cz - visual / 2f < rootZ) cz = rootZ + visual / 2f;\n"):
        probs.append("sanity: a planted re-implementation was not caught")
    if public_top_level("namespace X\n{\n    public struct Planted\n    {\n    }\n}\n") != ["Planted"]:
        probs.append("sanity: a planted public type was not caught")
    if scanned < 100:
        probs.append("sanity: only %d .cs files scanned under src/ -- the glob is blind" % scanned)
    print("drawn extent one ruler: %s -- %d homes linked, %d .cs scanned, Sun & Shade home %s"
          % ("PASS" if not probs else "FAIL", sum(1 for p in homes.values() if os.path.isfile(p) and links(p)), scanned,
             os.path.relpath(homes["Sun & Shade"], SRC)))
    for p in probs:
        print("  " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
