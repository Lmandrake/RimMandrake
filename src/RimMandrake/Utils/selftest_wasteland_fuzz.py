#!/usr/bin/env python3
"""Approach B fuzz of the Wasteland kernels (Wasteland/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the waste cask and sealed cask bay (cask), the
named-storm phase machine and storm layer (storm), the Rite of Tipping contract (tipping) and the ambient dose /
gripper / processor arithmetic (dose). The project is built through winbuild.stage_build (dotnet.exe is
Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_wasteland_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only cask|storm|tipping|dose]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Wasteland", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeWasteland.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="WastelandFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Wasteland", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeWasteland.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
