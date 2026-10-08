#!/usr/bin/env python3
"""Approach B fuzz of the JawaIonWeapons kernel (src/RimStarWars/JawaIonWeapons/Source/Kernel/RSW_IonBuildupKernel.cs), no game.

Seeded fuzz with explicit invariants: the body-size barrier and the third-party stat part composed with the engine's own 1/size (size), a pawn
taking ion hits (flesh), machines / droids / shields / vehicles taking the same hits (tiers). Built through winbuild.stage_build (dotnet.exe is
Windows-native), then run. The older game-referencing check of the real StatPart is selftest_stun_scaling.py.

    python3 src/RimMandrake/Utils/selftest_jawaionweapons_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only size|flesh|tiers]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

BASE = os.path.join(REPO, "src", "RimStarWars", "JawaIonWeapons", "Source")
FUZZ = os.path.join(BASE, "FuzzTest")
CSPROJ = os.path.join(FUZZ, "RimStarWarsJawaIonWeapons.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="JawaIonWeaponsFuzzTest", extra_dirs=[os.path.join(BASE, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, FUZZ) + "\\bin\\Release\\net8.0\\RimStarWarsJawaIonWeapons.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
