#!/usr/bin/env python3
"""Approach B fuzz of the StructureInjections plan reader and kernel (Source/RimplacePlan.cs, Source/Kernel/RM_PlanKernel.cs), no game.

Seeded fuzz against independent models: well-formed plans read back exactly (every verb, comments, CRLF, unknown verbs), every malformed line
refused with a FormatException naming the line, where a plan lands (anchor / map centre / offset), a RUN walked against random blocked grids,
transmitters-first ordering, the direction / mode / state / faction vocabulary, and the SHIPPED Templates/*.txt plans parsed and counted.
Built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_structureinjections_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only parse|malformed|offset|run|order|tables|templates]

A failing case prints `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

MOD = os.path.join(REPO, "src", "RimMandrake", "StructureInjections", "Source")
SELFTEST = os.path.join(MOD, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeStructureInjections.SelfTest.csproj")
TEMPLATES = os.path.join(REPO, "src", "RimMandrake", "StructureInjections", "Templates")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="StructureInjectionsFuzz", extra_dirs=[os.path.join(MOD, "Kernel"), TEMPLATES])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeStructureInjections.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll, "--plans", winbuild.staged_win(rec, TEMPLATES)]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
