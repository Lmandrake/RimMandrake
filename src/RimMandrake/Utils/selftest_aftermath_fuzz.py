#!/usr/bin/env python3
"""Approach B fuzz of the Aftermath kernel (src/RimMandrake/Aftermath/Source/Kernel/RM_AftermathKernel.cs), no game.

Seeded fuzz with explicit invariants: the outcome classifier over every small raid, raid scripts (walk-in, drop-pod, flee, die) polled like the
battle recorder polls (never closes with a raider on the map or still to arrive), prisoner clocks across several maps, the queue discipline.
Built through winbuild.stage_build (dotnet.exe is Windows-native), then run. The older selftest_aftermath.py checks the Def-shaped wrappers.

    python3 src/RimMandrake/Utils/selftest_aftermath_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only classify|battle|prison|queue|units]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Aftermath", "Source", "SelfTestFuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeAftermath.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="AftermathFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Aftermath", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeAftermath.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
