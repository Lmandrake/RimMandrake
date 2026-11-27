"""Offline test of the colonist 'Set fire to ...' order (RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS): the
real Source/LightOrder/LightOrderRule.cs driven by Scenario/LightOrder/Scenarios.cs (the spec's scenes, then all 2^13 fact
combinations against a rule table). Built through winbuild.stage_build (dotnet.exe is Windows-native), then run; exit 0 =
every case holds. The wiring around the rule (setting, menu, job, FlowWorks guard) is checked by selftest_mandrakepatches.py.

    python3 src/RimMandrake/MandrakePatches/selftest_light_order.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCEN = os.path.join(HERE, "Scenario", "LightOrder")
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import winbuild  # noqa: E402


def main():
    rc, rec = winbuild.stage_build(os.path.join(SCEN, "LightOrderScenario.csproj"), stage_name="LightOrderScenario",
                                   extra_dirs=[os.path.join(HERE, "Source", "LightOrder")])
    if rc:
        print("FAIL: light-order scenario build failed")
        return rc
    dll = winbuild.staged_win(rec, SCEN) + "\\bin\\Release\\net8.0\\LightOrderScenario.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main())
