#!/usr/bin/env python3
"""Approach B fuzz of the Inhabited kernels (InhabitedCustodyKernel.cs, InhabitedFateKernel.cs), no game.

Seeded action sequences over the production kernels: who holds whom (displaced pool, rosters, the map; nobody held by nothing),
cast instantiation, visit / fate / recall / stock collection, the fate-cause decision, the daily routine. Invariants are checked
after every step. Same wrapper shape as selftest_divinginteraction_fuzz.py: built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_inhabited_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only pool|place|cause|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Inhabited", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeInhabited.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="InhabitedFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeInhabited.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
