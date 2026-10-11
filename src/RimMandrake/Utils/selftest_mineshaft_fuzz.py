#!/usr/bin/env python3
"""Approach B fuzz of the Mine Shaft kernel (src/RimMandrake/MineShaft/Source/Kernel/RM_MineShaftKernel.cs), no game.

Seeded fuzz with explicit invariants: source eligibility (truth table), the policy ban, the multiplier clamp, work ticks
(monotone in hit points, floored, finite for adversarial input), yield (chunks fixed at 1, capped, >= 1), the one-bill-per-product
source order (a total order: antisymmetric, transitive) and the vein rule. Built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_mineshaft_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only source|ban|work|yield|order|vein]

A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "MineShaft", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeMineShaft.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="MineShaftFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "MineShaft", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeMineShaft.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
