#!/usr/bin/env python3
"""Approach B fuzz of LoreStages (src/RimMandrake/LoreStages/Source/), no game.

Unlike the other fuzz wrappers this one drives the PRODUCTION LoreStageApplier on REAL engine defs (BiomeDef / HediffDef / ThingDef from
Assembly-CSharp.dll, net472), because the private description caches it clears exist only there. Seeded random ladders over a small def
space (collisions between ladders on purpose), random stage sequences and an independent oracle; plus the kernel's rung pick, clamp, toggle
and ConfigErrors. Built through winbuild.stage_build, then the exe is run. The hand-written cases are selftest_lore_stages.py.

    python3 src/RimMandrake/Utils/selftest_lorestages_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only choose|ladder|config]

A failing case is printed as `family seed N: step K: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "LoreStages", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeLoreStages.SelfTest.csproj")


def main(argv):
    if not os.path.isdir("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed"):
        print("UNMEASURED, not a pass or a fail: the game's Managed/ assemblies are not reachable on this machine")
        return 2
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="LoreStagesFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    exe = os.path.join(rec["stage"], os.path.relpath(SELFTEST, REPO), "bin", "Release", "net472", "RimMandrakeLoreStages.SelfTest.exe")
    args = [exe]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    if len(args) == 1:
        args.append("--fuzz")
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
