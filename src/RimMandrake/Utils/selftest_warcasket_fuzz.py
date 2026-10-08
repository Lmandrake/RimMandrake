#!/usr/bin/env python3
"""Approach B fuzz of the Warcasket kernel (src/RimMandrake/Warcasket/Source/Kernel/RM_WarcasketKernel.cs), no game.

Seeded fuzz with explicit invariants: a worn suit under changing hazards (integrity), pawns walking in and out of deep water in
different gear (immersion), a half-extracted core dosing by distance and silent in a shielded bay (core), a corpse sealing, stripping
and cracking open (sarcophagus), and decision tables with the closed-form failure odds (tables). Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_warcasket_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only integrity|immersion|core|sarcophagus|tables]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Warcasket", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeWarcasket.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="WarcasketFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Warcasket", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeWarcasket.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
