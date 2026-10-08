#!/usr/bin/env python3
"""Approach B fuzz of the Pyrelands kernels (Pyrelands/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the burn-line map component and fire-front clock with the Tribes'
FireRaid (arson debt) and FlameHarvest (minimum fires) incidents on top (burn), the furnace-beast thermal charge, world-herd cycle,
nearest-tile search and bed-ignition clock (furnace), the lightning-breaker section flood-fill against a union-find spec (breaker),
the biome score, ash fall and fire-ecology gates (eco), and the tuning-file relationships (units). The tuning numbers are read from
Pyrelands/Source/PyrelandsTuning.cs itself, so the fuzz cannot drift from what ships. The project is built through
winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_pyrelands_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only burn|furnace|breaker|eco|units]

A failing case is shrunk (burn) and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

PYR = os.path.join(REPO, "src", "RimMandrake", "Pyrelands", "Source")
SELFTEST = os.path.join(PYR, "SelfTest", "Fuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakePyrelands.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="PyrelandsFuzzSelfTest", extra_dirs=[os.path.join(PYR, "Kernel"), PYR])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakePyrelands.Fuzz.dll"
    tuning = winbuild.staged_win(rec, PYR) + "\\PyrelandsTuning.cs"
    args = [winbuild.dotnet_exe(), dll, "--tuning", tuning]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
