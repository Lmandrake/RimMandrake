#!/usr/bin/env python3
"""Approach B fuzz of the GelatinousSlime kernels (GelatinousSlime/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the slimification ladder (ladder: rate priority,
stage latch, dissolution, dose, antidote, drench, release, injection), the titanoslime (titan: mass ladder with
hysteresis, growth/reversibility gates, decay, engulf gate, shedding) and the world rules (world: biome score, farm
conversion, chunk shelf life and burst ground, archive payment). The project is built through winbuild.stage_build
(dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_gelatinousslime_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only ladder|titan|world]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "GelatinousSlime", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGelatinousSlime.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GelatinousSlimeFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "GelatinousSlime", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeGelatinousSlime.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
