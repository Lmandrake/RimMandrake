#!/usr/bin/env python3
"""Approach B fuzz of the SolarMirrors kernels (SolarMirrors/Source/Kernel/*.cs), no game: see SolarMirrors/Source/SelfTest/SolarMirrorsFuzz.cs for the families.
The project is built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_solarmirrors_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only NAME]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "SolarMirrors", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeSolarMirrors.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SolarMirrorsFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "SolarMirrors", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeSolarMirrors.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
