#!/usr/bin/env python3
# selftest-timeout: 600   (dotnet.exe build + run through winbuild.run_interop)
"""Scenario test of RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES at the pawn caller: the real SouthDrawsFrontPawn.cs
against a fake Verse whose DrawPos is vanilla's line (Scenario/SouthDrawsFront/). Built through winbuild.stage_build
(dotnet.exe is Windows-native), then run; exit 0 = every scenario holds.

    python3 src/RimMandrake/MandrakePatches/selftest_south_draws_front_scenarios.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCEN = os.path.join(HERE, "Scenario", "SouthDrawsFront")
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import winbuild  # noqa: E402


def main():
    rc, rec = winbuild.stage_build(os.path.join(SCEN, "SouthDrawsFrontScenario.csproj"), stage_name="SouthDrawsFrontScenario",
                                   extra_dirs=[os.path.join(HERE, "Source", "SouthDrawsFront")])
    if rc:
        print("FAIL: scenario build failed")
        return rc
    dll = winbuild.staged_win(rec, SCEN) + "\\bin\\Release\\net8.0\\SouthDrawsFrontScenario.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main())
