#!/usr/bin/env python3
"""Approach B fuzz of the LuminousPigment kernels (LuminousPigment/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the Deepfire light book (lights: floor grid, 3x3
clusters, own-vs-cluster routing, settings rebuild, save/load), the rules (rules: coat caps and latch, status engine,
beauty/cost, mat lifecycle, god tables and anti-pinning, dodge inversion, worn blend, dark test) and the cuisine
(cuisine: steer curve, family rolls, per-pawn cap). The project is built through winbuild.stage_build (dotnet.exe is
Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_luminouspigment_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only lights|rules|cuisine]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "LuminousPigment", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeLuminousPigment.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="LuminousPigmentFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "LuminousPigment", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeLuminousPigment.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
