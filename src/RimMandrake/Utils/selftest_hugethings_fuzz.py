#!/usr/bin/env python3
"""Approach B fuzz of the Huge Things kernel (src/RimMandrake/HugeThings/Source/Kernel/RM_FootprintKernel.cs), no game.

Seeded fuzz with explicit invariants: footprint arithmetic, trunk and click rects, the MaxRect re-link cover, pawn hitboxes, the
trunk-blocker reconcile plan over random worlds and a growth-and-settings lifecycle. Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run. The older selftest_hugethings_footprint.py pins the shipped per-species table.

    python3 src/RimMandrake/Utils/selftest_hugethings_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only math|trunk|pawn|plan|units]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "HugeThings", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeHugeThings.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="HugeThingsFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "HugeThings", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeHugeThings.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
