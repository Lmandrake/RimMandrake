#!/usr/bin/env python3
"""Offline lint of the StructureInjections mod (defs/patches vs C#): see lint_mod_defs.py for the checks, plus the kernel guards (engine-free,
compiled into the mod and the fuzz project) and the shipped plan templates (a plan the GenStep cannot read is refused here, not at mapgen).

    python3 src/RimMandrake/Utils/lint_structureinjections_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402
from lint_kernel_guards import kernel_guards  # noqa: E402

VERBS = {"FOOTPRINT": 5, "CLEAR": 6, "FOUNDATION": 4, "TERRAIN": 4, "THING": 6, "RUN": 6, "ROOF": 4, "PAINT": 4, "FLOORCOLOR": 4, "PAWN": 6}
INTS = {"FOOTPRINT": (1, 2, 3, 4), "CLEAR": (1, 2, 3, 4), "FOUNDATION": (1, 2), "TERRAIN": (1, 2), "ROOF": (1, 2), "PAINT": (1, 2), "FLOORCOLOR": (1, 2),
        "THING": (2, 3, 4), "RUN": (1, 2), "PAWN": (2, 3)}


def template_findings(mod_dir):
    errs = []
    tdir = os.path.join(mod_dir, "Templates")
    files = sorted(f for f in os.listdir(tdir) if f.endswith(".txt")) if os.path.isdir(tdir) else []
    if not files:
        return ["ERROR structureinjections-template: Templates has no .txt plans (sanity probe: the folder moved?)"]
    for f in files:
        lines = open(os.path.join(tdir, f), encoding="utf-8-sig").read().splitlines()
        if not lines or not lines[0].startswith("# rimplace flat plan v2"):
            errs.append("ERROR structureinjections-template: %s is not a v2 flat plan" % f)
        foot = 0
        for i, raw in enumerate(lines, 1):
            line = raw.rstrip()
            if not line or line.startswith("#"):
                continue
            p = line.split("\t")
            if p[0] not in VERBS:
                errs.append("ERROR structureinjections-template: %s line %d: unknown directive %s" % (f, i, p[0]))
                continue
            if len(p) < VERBS[p[0]]:
                errs.append("ERROR structureinjections-template: %s line %d: %s has %d fields, wants %d" % (f, i, p[0], len(p), VERBS[p[0]]))
                continue
            for k in INTS[p[0]]:
                try:
                    int(p[k])
                except ValueError:
                    errs.append("ERROR structureinjections-template: %s line %d: field %d of %s is not a number: %r" % (f, i, k, p[0], p[k]))
            if p[0] == "FOOTPRINT":
                foot += 1
            if p[0] == "CLEAR" and p[5] not in ("all", "soft"):
                errs.append("ERROR structureinjections-template: %s line %d: CLEAR mode %r" % (f, i, p[5]))
            if p[0] == "RUN" and p[3] not in ("N", "E", "S", "W"):
                errs.append("ERROR structureinjections-template: %s line %d: RUN direction %r" % (f, i, p[3]))
            if p[0] == "PAWN" and (p[5] not in ("alive", "dead", "dessicated", "skeleton") or p[4] == "player"):
                errs.append("ERROR structureinjections-template: %s line %d: PAWN state/faction %r/%r" % (f, i, p[5], p[4]))
        if foot != 1:
            errs.append("ERROR structureinjections-template: %s has %d FOOTPRINT lines, wants 1" % (f, foot))
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "StructureInjections")
    rc = lint_mod_defs.run("StructureInjections", argv)
    errs = template_findings(mod_dir) + kernel_guards(mod_dir, "StructureInjections.csproj", "SelfTest/RimMandrakeStructureInjections.SelfTest.csproj", "structureinjections-kernel",
                                                        extra_fuzz_includes=('Compile Include="..\\RimplacePlan.cs"',))
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)
