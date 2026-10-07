"""validation.py -- first north-star script for RimUtinni: PyrelandsMechanics (mandrake.rut.pyrelandsmechanics).

PYRELANDS_MECHANICS_FIRST_SCRIPT_1 (PYRELANDS_MECHANICS_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run PyrelandsMechanics

INTENDED FUNCTION (About.xml): the campaign third of the Pyrelands igniter kit, the part that names the Deep Desert Tribes: arson justice (an arson debt that brings a fire raid), the flame-harvest incident, and the fire rite whose group harvests flame under RUT_RiteHarvest.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * RUT_FlameHarvest and RUT_FireRaid answer a dry run
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * arson debt accumulating past arsonDebtRaidThreshold and firing RUT_FireRaid
  * RUT_FlameHarvest needing flameHarvestMinFires fires; the rite group's RUT_RiteHarvest duty

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
    suite = Suite("PyrelandsMechanics")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_FlameHarvest', 'RUT_FireRaid'), min_count=3)

    @suite.chain("unproven_bars")
    def unproven_bars(t):
        """The two bars the first live pass could not prove, recorded as UNMEASURED rows (never PASS) so a run's
        sheet names them (PYRELANDS_MECHANICS_FIRST_SCRIPT_1 A3). Each reason is why no existing bridge tool reaches it."""
        for name, why in (
            ("arson_debt_past_threshold_fires_fireraid",
             "no bridge tool reads or writes the arson debt tally (WorldComponent state) and the dry-run fire_incident only "
             "proves RUT_FireRaid's worker resolves; needs a proof hook that sets debt past arsonDebtRaidThreshold and reads back the queued raid"),
            ("flameharvest_needs_flameHarvestMinFires",
             "no tool lists burning fires per map for a threshold sweep; the dry run proves CanFireNow does not throw but not "
             "that it refuses below flameHarvestMinFires; needs a fixture that lights N and N+1 fires and a CanFireNow read-back"),
        ):
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: " + why
            with t.component(name):
                pass
            t.upstream_failed = False
            t.upstream_reason = ""
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
