#!/usr/bin/env python3
"""Approach B fuzz of CreatureBehaviors, no game: the moving-shade layer
(CreatureBehaviors/Source/RM_MovingShadeLayer.cs + RM_MovingShadeMath.cs) and the sand swimmer's surface/submerge
machine (RM_SandSwimKernel.cs). Seeded action sequences over the PRODUCTION kernels the mod calls, with explicit
invariants and an incremental-vs-fresh oracle for the shade grid. Same wrapper shape as selftest_bazaar_fuzz.py:
built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_creaturebehaviors_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only shade|bounds|swim]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "CreatureBehaviors", "Source", "SelfTestFuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeCreatureBehaviors.Fuzz.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="CreatureBehaviorsFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "CreatureBehaviors", "Source")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeCreatureBehaviors.Fuzz.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
