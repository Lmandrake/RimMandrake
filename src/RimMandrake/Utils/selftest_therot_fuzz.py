#!/usr/bin/env python3
"""Approach B fuzz of The Rot kernel (RM_TheRotKernel.cs), no game.

Seeded action sequences over the production kernel (the hwelgrue's gut clock and map cap, a hwelgrue holding someone, the gut-mother vat's
clock, the world's one swallowed drive core, the navigator's log, the unjoining draught's sorting, the biome score), with design invariants
checked after every step. Same wrapper shape as selftest_miasma_fuzz.py.

    python3 src/RimMandrake/Utils/selftest_therot_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only gut|swallow|vat|core|log|unjoin|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "TheRot", "Source", "TheRotFuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeTheRot.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="TheRotFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeTheRot.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
