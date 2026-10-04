"""validation.py -- first north-star script for RimUtinni: FungalSoilTrade (mandrake.rut.fungalsoiltrade).

FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1 (FUNGAL_SOIL_TRADE_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run FungalSoilTrade

INTENDED FUNCTION (About.xml): the Rot's mycelial mat is dug for RUT_FungalSoil, a capped per-map sellable resource (mineable knots scattered only on Rot maps, no regrowth); digging feeds a fungal-distress meter that pulses and can summon a colossus; a trade-request quest buys the soil.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * scatter_places_knots: RUT_FungalSoilScatter run on an RM_TheRot map places RUT_MineableFungalGround
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * the distress meter rising when a knot is mined (Mineable.DestroyMined postfix) and its pulse/colossus
  * the scatter refusing a non-Rot map (needs a second biome in one run)
  * RUT_FungalSoilTradeRequest being offered and completing

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
    suite = Suite("FungalSoilTrade")
    suite.toggles = sorted(mod_static.bool_settings(HERE))
    suite.biome = "RM_TheRot"

    def _count(t, d):
        r = t.bridge_call("jawa/list_things", defName=d, limit=1)
        if not t._guard():
            return 0
        if not (r or {}).get("success") or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) failed: %r" % (d, r))
        return int(r["countMatched"])

    @suite.chain("fungal_scatter")
    def _scatter_0(t):
        with t.component("scatter_places_knots", toggle="scatterEnabled"):
            before = _count(t, "RUT_MineableFungalGround")
            r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_FungalSoilScatter")
            if t._guard():
                if not (r or {}).get("success"):
                    raise ExpectationFailed("run_genstep(RUT_FungalSoilScatter) failed: %r" % (r,))
                after = _count(t, "RUT_MineableFungalGround")
                if after <= before:
                    raise ExpectationFailed("RUT_FungalSoilScatter on a RM_TheRot map placed no RUT_MineableFungalGround (%d -> %d)" % (before, after))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_FungalSoil', 'RUT_MineableFungalGround'), min_count=4)
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
