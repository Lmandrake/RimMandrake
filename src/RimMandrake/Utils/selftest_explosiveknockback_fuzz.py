#!/usr/bin/env python3
"""Approach B fuzz of the Explosive Knockback kernel (src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs), no game.

Seeded fuzz beside the K-01..K-16 scene checks (selftest_explosiveknockback_kernel.py): throw distance against an oracle and its
monotonicity, the throw line against an integer-rational oracle and its symmetries, the grid walk against an independently written walker
plus structural invariants, the per-explosion cap, config lookup, stun-lock / shield / dedupe / budget / epicentre direction.
Built through winbuild.stage_build (dotnet.exe is Windows-native), then run with --fuzz flags.

    python3 src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only cells|line|resolve|rank|cfg|guard]

A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "ExplosiveKnockback", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeExplosiveKnockback.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="ExplosiveKnockbackFuzzSelfTest")
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeExplosiveKnockback.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll, "--fuzz"]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
