#!/usr/bin/env python3
"""Approach B fuzz of the ShipVermin kernel (src/RimMandrake/ShipVermin/Source/Kernel/RM_VerminKernel.cs), no game.

Seeded fuzz against independent restatements: a wreck nest's life under random time, setting and respawn sequences (one burst, attempts only
on schedule, timer always forward, refusal order), the weighted species pool and roster rule (a forbidden slot is never picked, as the free kind
or the swapped canon kind), the innate-ability decision, and the chemfuel spray cone geometry. Built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_shipvermin_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only nest|pick|grant|cone]

A failing case is shrunk and printed as `family seed N: message | ops`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

MOD = os.path.join(REPO, "src", "RimMandrake", "ShipVermin", "Source")
SELFTEST = os.path.join(MOD, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeShipVermin.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="ShipVerminFuzz", extra_dirs=[os.path.join(MOD, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeShipVermin.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
