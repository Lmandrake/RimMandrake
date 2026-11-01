#!/usr/bin/env python3
"""BESKAR_ARMORER_QUEST_1 L3 offline: beskar mass, melt count x0.8, smelt ceil(n/3)+1 slag, the bill gate and the route gates.

Compiles Source/Kernel/ArmorerKernel.cs into a console selftest through winbuild.stage_build and runs it.

    python3 src/RimMandrake/Utils/selftest_beskar_armorer.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SRC = os.path.join(REPO, "src", "RimUtinni", "BeskarArmorer", "Source")
SELFTEST = os.path.join(os.path.dirname(SRC), "SelfTest")
CSPROJ = os.path.join(SELFTEST, "BeskarArmorer.SelfTest.csproj")


def main():
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="BeskarArmorerSelfTest", extra_dirs=[os.path.join(SRC, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\BeskarArmorer.SelfTest.dll"
    r = subprocess.run([winbuild.dotnet_exe(), dll], cwd="/mnt/c", capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[-2000:])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
