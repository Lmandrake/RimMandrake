#!/usr/bin/env python3
"""Approach B fuzz of the KineticArms kernel (src/RimMandrake/KineticArms/Source/RM_KineticMath.cs), no game.

Seeded fuzz with explicit invariants: shot geometry (direction, back-step, cone membership against an angle oracle, rotation symmetry of
the cone cells), the whole bolt (centre, cone cells, impact kept), the pulse cannon's charge, ruins loot picks (weights, toggles, edge
rolls, roll-for round trip), looted raider weapons (gate, grenadier split, money) and unit tables. Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run. The hand-written examples are selftest_kineticarms_kernel.py.

    python3 src/RimMandrake/Utils/selftest_kineticarms_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only geometry|bolt|charge|ruins|looted|units]

A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "KineticArms", "Source", "SelfTest", "Fuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeKineticArms.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="KineticArmsFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeKineticArms.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
