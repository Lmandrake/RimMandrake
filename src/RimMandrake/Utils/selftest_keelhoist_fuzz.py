#!/usr/bin/env python3
"""Approach B fuzz of the KeelHoist kernel (src/RimMandrake/KeelHoist/Source/Kernel/RM_HoistKernel.cs), no game.

Seeded fuzz with explicit invariants: hoist action sequences through the production schedule / tick loop / arrival plan against an
independent ledger (transit), the chance-chute lifecycle and house edge (chute), pricing / silver stacks / cycle time (market) and every
decision table exhaustively (gates). Built through winbuild.stage_build (dotnet.exe is Windows-native), then run. The older static
gate / formula check is src/RimMandrake/KeelHoist/selftest_keelhoist.py.

    python3 src/RimMandrake/Utils/selftest_keelhoist_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only transit|chute|market|gates]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "KeelHoist", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeKeelHoist.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="KeelHoistFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "KeelHoist", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeKeelHoist.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
