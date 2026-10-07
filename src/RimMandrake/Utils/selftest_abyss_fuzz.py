#!/usr/bin/env python3
"""Approach B fuzz of the Abyss kernels (RM_AbyssKernel.cs, RM_AbyssStateKernel.cs), no game.

Seeded action sequences over the production kernels (Dark darkness + murk hysteresis, lamps shared by the Dark and the krizzak,
fold-lamp lanes on walled grids, cryptid rings/exchange/phantoms, hidden-ship cover + probe schedule, gust controller + gharrek
feeding, storm-call timers, soundscape scheduler, summ sunburn, biome score), with design invariants checked after every step.
The existing BroodSelfTest (RM_BroodWakeLogic.cs) is a separate project and is not run here.

    python3 src/RimMandrake/Utils/selftest_abyss_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only dark|lamp|lane|cryptid|cover|gust|storm|sound|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Abyss", "Source", "AbyssFuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeAbyss.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="AbyssFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeAbyss.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
