#!/usr/bin/env python3
"""Approach B fuzz of the Graffiti kernel (src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs), no game.

Seeded fuzz with explicit invariants: the weighted mark pick (range, monotone in the roll, boundary rolls, frequencies), the meme / skill /
hostility gates, the relation-keyed reaction priority over all flag combinations, scrub protection and the other predicates, the wall-cell
candidate gathering against an oracle, the breach-lure choice. Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_graffiti_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only pick|gates|react|misc|cells|lure]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGraffiti.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GraffitiFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeGraffiti.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
