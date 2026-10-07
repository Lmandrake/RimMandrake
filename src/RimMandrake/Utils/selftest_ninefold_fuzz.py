#!/usr/bin/env python3
"""Approach B fuzz of the Ninefold satiation engine kernel (Ninefold/Source/RM_NinefoldKernel.cs), no game.

Seeded action sequences (events, hourly mood walk + rooted erosion, launches, landings, violent deaths, first-contact triggers and the one-a-day queue) over the production
kernel, with design invariants checked after every step. Same wrapper shape as selftest_gimmesomeslack.py: the project
is built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_ninefold_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only seq|band|rank|mood]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Ninefold", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeNinefold.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="NinefoldFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Ninefold", "Source")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeNinefold.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
