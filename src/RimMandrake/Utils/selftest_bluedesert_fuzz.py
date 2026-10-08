#!/usr/bin/env python3
"""Approach B fuzz of the BlueDesert kernels (BlueDesert/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the blue-ice heat sink with heat/ice conservation against the
vanilla cooler step (cold), the thaw-roll counter and weighted pick (thaw), the vhaulk detonation gate / plant charge / departure /
ablation timeline / ossivel choir (rules), and the murrek reseed plan against an independent oracle (murrek). Built through
winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_bluedesert_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only cold|thaw|rules|murrek]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "BlueDesert", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeBlueDesert.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="BlueDesertFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "BlueDesert", "Source", "Kernel"), os.path.join(REPO, "src", "RimMandrake", "BlueDesert", "Source")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeBlueDesert.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
