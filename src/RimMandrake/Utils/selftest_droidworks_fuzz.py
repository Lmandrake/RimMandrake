#!/usr/bin/env python3
"""Approach B fuzz of the Droidworks kernel (DroidworksKernel.cs), no game.

Seeded action sequences over the production kernel (format-tier recipes, wipes and the unwiped-time idiosyncrasy ladder;
power drain / charger refill / bolt resentment / detonation; data-spike resistance; protocol-droid price shift), with design
invariants checked after every step. Same wrapper shape as selftest_divinginteraction_fuzz.py: the project is built through
winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_droidworks_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only drift|power|spike|trade|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimStarWars", "Droidworks", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimStarWarsDroidworks.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="DroidworksFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimStarWarsDroidworks.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
