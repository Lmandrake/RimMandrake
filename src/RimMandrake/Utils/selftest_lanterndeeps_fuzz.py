#!/usr/bin/env python3
"""Approach B fuzz of the LanternDeeps kernels (RM_DeepCollapseKernel.cs, RM_SipperLedgerKernel.cs), no game.

Seeded action sequences over the production kernels: the Deep's collapse-warning state machine (mark / hold / resolve / release / forced
falls / save+load / warnings switched off) and the Sipper glow-radius ledger against the aurora's own writes. Invariants are checked after
every step. Same wrapper shape as selftest_divinginteraction_fuzz.py: built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_lanterndeeps_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only collapse|sipper|units]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "LanternDeeps", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeLanternDeeps.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="LanternDeepsFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeLanternDeeps.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
