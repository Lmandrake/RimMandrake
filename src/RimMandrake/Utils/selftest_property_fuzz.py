#!/usr/bin/env python3
"""Approach B fuzz of the Property kernel (src/RimMandrake/Property/Source/Kernel/RM_HoistKernel.cs), no game.

Seeded fuzz with explicit invariants: a world of pawns, things, factions and silver (events through the production spine / authorization /
claim ordering / decay, menus built and clicked with money conserved, loot, gifts, the foreign-claim wipe) against a brute-force spec of
who owns what (ledger); a faction's witness record (suspicion); fees, prices, silver removal, recognizability, the pocket pick (tables).
Built through winbuild.stage_build (dotnet.exe is Windows-native), then run. The older net472 check of ClaimantRef equality against the
game assemblies is selftest_property_fabric.py.

    python3 src/RimMandrake/Utils/selftest_property_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only ledger|suspicion|tables]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "RimProperty", "Source", "SelfTest", "Fuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeProperty.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="PropertyFuzz",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "RimProperty", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeProperty.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
