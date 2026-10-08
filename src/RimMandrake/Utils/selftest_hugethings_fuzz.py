#!/usr/bin/env python3
"""Approach B fuzz of the Huge Things footprint kernel (HugeThings/Source/Kernel/RM_HugeFootprintKernel.cs), no game.

Seeded random plants (root, drawSize, visualSizeRange, growth, jitter, flip, Mod Settings multiplier, a random mask shaped like
measure_huge_plant_masks.py's) against the production kernel: selection holds every blocked cell and the whole picture, blocked
cells stay inside the picture, full growth reproduces the measured mask (mirrored when flipped), growth is monotonic for a solid
base, every seed replays identically. Same wrapper shape as selftest_therot_fuzz.py.

    python3 src/RimMandrake/Utils/selftest_hugethings_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only any|full|boundary|symmetry|determinism]

A failing case prints as `FAIL family seed N: message`; --fuzz-seed N replays it.
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
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="HugeThingsFuzzSelfTest")
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
