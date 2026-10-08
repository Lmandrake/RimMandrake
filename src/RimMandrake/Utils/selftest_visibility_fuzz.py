#!/usr/bin/env python3
"""Approach B fuzz of the Visibility kernel (src/RimMandrake/Visibility/Source/Kernel/), no game.

Seeded fuzz with explicit invariants against independent restatements of the rules. Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_visibility_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only band|curve|dial|memory|points]

A failing case is shrunk where possible and printed as `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Visibility", "Source", *"SelfTest/Fuzz".split("/"))
CSPROJ = os.path.join(SELFTEST, "RimMandrakeVisibility.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="VisibilityFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Visibility", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeVisibility.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
