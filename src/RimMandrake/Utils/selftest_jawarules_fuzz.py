#!/usr/bin/env python3
"""Approach B fuzz of the JawaRules kernel (src/RimStarWars/JawaRules/Source/Kernel/RSW_JawaRulesKernel.cs), no game.

Seeded fuzz with explicit invariants: the swim-hood postfix and the always-on fallback hood against a fake render engine (flag masking, headgear
visibility, other gates) so a swimming Jawa keeps its real hood, nothing else changes, and the fallback draws exactly when the real hood will not
(hood); the no-sow / relations / pet-name / pawn-kind-redress gates on evolving pawn populations (rules). Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_jawarules_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only hood|rules]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

BASE = os.path.join(REPO, "src", "RimStarWars", "JawaRules", "Source")
SELFTEST = os.path.join(BASE, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimStarWarsJawaRules.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="JawaRulesFuzzSelfTest", extra_dirs=[os.path.join(BASE, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimStarWarsJawaRules.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
