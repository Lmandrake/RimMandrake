#!/usr/bin/env python3
"""SithLine offline selftest (SANGUOPHAGE_KEPT_UNREACHABLE_1): the production kernel RSW_SithLineKernel.cs, built into a
plain net8.0 exe through winbuild.stage_build (dotnet.exe is Windows-native) and run; then the mod's STATIC checks
(validation.py). No game.

    python3 src/RimStarWars/SithLine/selftest_sithline.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)
import winbuild  # noqa: E402

SELFTEST = os.path.join(HERE, "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RSW_SithLine.SelfTest.csproj")


def main():
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SithLineSelfTest")
    if rc:
        print("FAIL selftest build")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RSW_SithLine.SelfTest.dll"
    k = subprocess.run([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev").returncode
    s = subprocess.run([sys.executable, os.path.join(HERE, "validation.py")]).returncode
    print("sithline selftest: kernel %s, static %s" % ("ok" if k == 0 else "FAIL", "ok" if s == 0 else "FAIL"))
    return 1 if (k or s) else 0


if __name__ == "__main__":
    sys.exit(main())
