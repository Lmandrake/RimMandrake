#!/usr/bin/env python3
"""Approach B fuzz of the Jawa Armoury kernels (src/RimStarWars/Armoury/Source/Kernel/RSW_ArmouryKernel.cs), no game.

Seeded fuzz with explicit invariants: the ion / stun workers against a pawn that accumulates hediffs (ion), the bonus mining yield gate, weighted
pick and stack size (yield), the self-buff cooldown clock and the mental-break blocker (gear), the kolto tank over a power / fuel / slider timeline
(kolto), and the jumppack / emergency-heal / mine-defuse decisions with probe order checked (combat). Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run. The older chain check is src/RimStarWars/Armoury/selftest_armoury.py.

    python3 src/RimMandrake/Utils/selftest_armoury_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only ion|yield|gear|kolto|combat]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimStarWars", "Armoury", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimStarWarsArmoury.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="ArmouryFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimStarWars", "Armoury", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimStarWarsArmoury.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
