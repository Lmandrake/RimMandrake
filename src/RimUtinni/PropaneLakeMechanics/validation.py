"""validation.py -- first north-star script for RimUtinni: PropaneLakeMechanics (mandrake.rut.propanelakemechanics).

PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1 (PROPANE_LAKE_PIPE_MECHANICS_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run PropaneLakeMechanics

INTENDED FUNCTION (About.xml): the propane lake's pipe/vent/saturation ladder: RUT_GasVent self-igniting puffs that deplete only while a RUT_VentPump pumps (pulling the pump releases a map-wide flammable cloud); a map gas-saturation meter; deflagration when a shot is fired into saturated air; pipes, valves, pumps; a saturation heist raid.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * Verb_LaunchProjectile.TryCastShot carries the deflagration patch
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * vent puffs igniting and depletion starting only with an adjacent pump
  * removing a live pump triggering the release; saturation clearing by wind
  * a shot into saturated air deflagrating; RUT_SaturationHeistRaid firing

STATIC (offline): `python3 validation.py` runs modcheck.mod_static over the mod -- every Defs/Patches XML parses, no
inert top-level `<Operation MayRequire>`, every Source/*.cs is in the csproj, a ModSettings class exists and every
Scribed setting has a control.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from modcheck import mod_static  # noqa: E402


def static_checks():
    return mod_static.static_findings(HERE)


def _build_suite():
    from modcheck import Suite, ExpectationFailed, shipped_defs  # noqa: F401
    suite = Suite("PropaneLakeMechanics")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_GasVent', 'RUT_VentPump'), min_count=7)
    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL (%d)" % len(problems)))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
