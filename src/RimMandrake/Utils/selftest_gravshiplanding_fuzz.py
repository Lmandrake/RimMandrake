#!/usr/bin/env python3
"""Approach B fuzz of the Gravship Landing kernel (src/RimMandrake/GravshipLanding/Source/Kernel/RM_LandingKernel.cs), no game.

Seeded fuzz of the root walk against a model of the engine's FloodUnfog (one flood per fogged unroofed component, sealed roofed rooms stay
fogged, idempotent, never refogs) plus the gate tables. Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_gravshiplanding_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only gate|world|units]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "GravshipLanding", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGravshipLanding.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GravshipLandingFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "GravshipLanding", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeGravshipLanding.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
