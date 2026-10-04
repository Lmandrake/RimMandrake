"""validation.py -- first north-star script for RimUtinni: WildsteamEggBounty (mandrake.rut.wildsteameggbounty).

WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1 (WEBWORK_NEST_EGG_ECONOMY_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run WildsteamEggBounty

INTENDED FUNCTION (About.xml): the Wildsteam pay a bounty to destroy eggs, a lower-paying legal outlet beside the smugglers' jackpot (market value x0.5-0.7 as goodwill plus silver), one trade-request QuestScriptDef gated by bountyEnabled.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * RUT_WildsteamEggBounty is loaded
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * the quest being offered by a Wildsteam settlement and paying below the black market

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
    suite = Suite("WildsteamEggBounty")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_WildsteamEggBounty',), min_count=1)
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
