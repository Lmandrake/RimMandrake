#!/usr/bin/env python3
"""Approach B fuzz of the Webwork kernel (src/RimMandrake/Webwork/Source/Kernel/RM_HoistKernel.cs), no game.

Seeded fuzz with explicit invariants: action sequences on the urraveth skeleton (loads, damage, deconstruction, a watcher, rare ticks,
examines) through the production load / creak / collapse / cascade kernel against an independent cell-set spec (urraveth), the nest wall's
egg-clutch relay timer against a ledger (relay), and gridded tables for the emergent-spawn gate, biome score, margins, outline ring,
rounding and the Mod Settings ranges (tables). Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_webwork_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only urraveth|relay|tables]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Webwork", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeWebwork.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="WebworkFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Webwork", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeWebwork.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
