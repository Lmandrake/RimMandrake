#!/usr/bin/env python3
"""Approach B fuzz of the RaidRedesigner roster kernel (src/RimMandrake/RaidRedesigner/Source/Kernel/RM_RosterKernel.cs), no game.

Seeded random Record / death / lost-pawn sweep / cap-change sequences through the production RecordEncounter flow, compared after every step
with an independent model of the design's 1.4 rules (one living entry per pawn, Captain-only role upgrade, scaled and clamped scores, cap
enforced after a new entry's own deltas, lowest-notability-then-stalest victims, dead entries immortal and frozen), plus the score / sweep /
summary tables. Built through winbuild.stage_build (dotnet.exe is Windows-native), then run. The older static + mirror proof is
src/RimMandrake/RaidRedesigner/selftest_raidredesigner_proofs.py.

    python3 src/RimMandrake/Utils/selftest_raidredesigner_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only roster|tables]

A failing case is shrunk and printed as `roster seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

MOD = os.path.join(REPO, "src", "RimMandrake", "RaidRedesigner", "Source")
SELFTEST = os.path.join(MOD, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeRaidRedesigner.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="RaidRedesignerFuzz", extra_dirs=[os.path.join(MOD, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeRaidRedesigner.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
