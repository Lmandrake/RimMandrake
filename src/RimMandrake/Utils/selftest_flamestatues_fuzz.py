#!/usr/bin/env python3
"""Approach B fuzz of the Flame Statues kernel (src/RimMandrake/FlameStatues/Source/Kernel/RM_FlameKernel.cs), no game.

Seeded fuzz with explicit invariants: the quality-to-size table, the burning / shown / lit predicates exhaustively, the fleck cadence
(each point exactly once per interval), the frame and jitter picks inside their arrays for adversarial ticks and ids, the fuel-use
multiplier and the never-run-out refill over a burn lifecycle. Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_flamestatues_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only quality|gate|fleck|frame|fuel]

A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "FlameStatues", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeFlameStatues.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="FlameStatuesFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "FlameStatues", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeFlameStatues.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
