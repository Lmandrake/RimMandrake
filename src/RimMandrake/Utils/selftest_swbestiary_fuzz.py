#!/usr/bin/env python3
"""Approach B fuzz of the SWBestiary kernels (Livestock/Kernel/RSW_LivestockKernel.cs, BeastMechanics/Kernel/RSW_BeastKernel.cs,
JawaIkee/Kernel/RSW_IkeeKernel.cs under src/RimStarWars/SWBestiary/Source), no game.

Seeded fuzz with explicit invariants: the onnik's kiln ledger (kiln), the moornak's join timer / ledger / unsettled hediff / release (grief),
the ferroclaw's bites until the item is gone (eat), the scrap bird's eligibility, nearest nest and nest cells on random maps (hoard), the
norphea's toxin need (toxin), the fuel-spew cone against a brute-force angle test (spew), and the ability / ikee tables (ikee). Built through
winbuild.stage_build (dotnet.exe is Windows-native), then run. The older chain check is src/RimStarWars/SWBestiary/selftest_swbestiary.py.

    python3 src/RimMandrake/Utils/selftest_swbestiary_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only kiln|grief|eat|hoard|toxin|spew|ikee]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

BASE = os.path.join(REPO, "src", "RimStarWars", "SWBestiary", "Source")
SELFTEST = os.path.join(BASE, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimStarWarsSWBestiary.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SWBestiaryFuzzSelfTest",
                                   extra_dirs=[os.path.join(BASE, d, "Kernel") for d in ("Livestock", "BeastMechanics", "JawaIkee")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimStarWarsSWBestiary.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
