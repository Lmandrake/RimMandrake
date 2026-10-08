#!/usr/bin/env python3
"""Approach B fuzz of the TitanicCreatures kernel (src/RimMandrake/TitanicCreatures/Source/Kernel/), no game.

Seeded fuzz with explicit invariants against independent restatements of the rules. Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_titaniccreatures_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only tier|yield|crush|pool]

A failing case is shrunk where possible and printed as `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "TitanicCreatures", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeTitanicCreatures.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="TitanicCreaturesFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "TitanicCreatures", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeTitanicCreatures.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
