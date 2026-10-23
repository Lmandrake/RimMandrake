#!/usr/bin/env python3
"""DEEP_DRILL_HOME_BIOME_1 L0 selftest of the DeepDrill kernel and shipped table (src/RimMandrake/DeepDrill/Source/Kernel/), no game.

Seeded weighted picks over the 23 deepCommonality carriers of the def dump, filtered by the production kernel against the shipped
Defs/RM_DeepHomeTable.xml: a non-home biome yields only steel, each home biome yields steel plus exactly its deposits, filter off is vanilla.
Built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_deepdrill.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "DeepDrill", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeDeepDrill.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="DeepDrillFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "DeepDrill", "Source", "Kernel"), os.path.join(REPO, "src", "RimMandrake", "DeepDrill", "Defs")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\DeepDrill.SelfTest.dll"
    xml = winbuild.staged_win(rec, os.path.join(REPO, "src", "RimMandrake", "DeepDrill", "Defs")) + "\\RM_DeepHomeTable.xml"
    args = [winbuild.dotnet_exe(), dll, xml]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
