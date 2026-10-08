#!/usr/bin/env python3
"""Approach B fuzz of the Stillsand kernels (Stillsand/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the sand-leviathan visit lifecycle (leviathan: classify, rumble,
arrival fallback, the fed / fire / bored / hard-ground dive machine with exact off-sand lifetimes, hunt gates, wettest-body appraisal,
entry-cell preference, odds), the water-debt ledger (ledger: exact dyadic debt / band / goodwill / opening-throttle spec and the
incident weight), the dune gale (gale: wind step, carry walk against a wall grid, exit / return edges, walk-in, the carried-pawn
book, the emergence filter) and sun-fed work (sun: factor table, work speed, the solar still's clock, corpse yield, thumper beat and
call selection, mirror-beam sun and damage), plus exhaustive truth tables (units). The project is built through
winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_stillsand_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only leviathan|ledger|gale|sun|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Stillsand", "Source", "SelfTest", "Fuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeStillsand.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="StillsandFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "Stillsand", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeStillsand.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
