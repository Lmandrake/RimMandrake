#!/usr/bin/env python3
"""Approach B fuzz of the EnvironmentalHazards kernels (Source/RM_AxisKernel.cs salinity axis + surge, Source/RM_PoolKernel.cs stranding-pool grid logic), no game.

Seeded action sequences (surge / recede / overwrite / save-load of the salinity grid; detect / tick / terrain-edit of the pools)
over the production kernels, with design invariants checked after every step, plus oracle checks of every grid primitive. Same wrapper shape as selftest_gimmesomeslack.py: the project
is built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_bazaar_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only axis|quant|prim|pool|cooler|held]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "EnvironmentalHazards", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrake.EnvironmentalHazards.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="EnvHazardsFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "EnvironmentalHazards", "Source")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrake.EnvironmentalHazards.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
