#!/usr/bin/env python3
"""Approach B fuzz of the Acoustic Scanner kernel (src/RimMandrake/AcousticScanner/Source/Kernel/RM_AcousticKernel.cs), no game.

Seeded fuzz with explicit invariants: pulse banding against an independent spec (bands inside the map at full block size, every hit
covered, order- and weight-scale-independent), the CanPulse decision table exhaustively, cooldown and overlay lifecycles, the
landed-ship test. Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_acousticscanner_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only band|gate|clock|ship|units]

A failing case is shrunk and printed as `family seed N: message | detail`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "AcousticScanner", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeAcousticScanner.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="AcousticScannerFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "AcousticScanner", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeAcousticScanner.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
