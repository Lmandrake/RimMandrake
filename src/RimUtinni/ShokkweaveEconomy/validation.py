"""validation.py -- first north-star script for RimUtinni: ShokkweaveEconomy (mandrake.rut.shokkweaveeconomy).

SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1 (SHOKKWEAVE_SOLE_SOURCE_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run ShokkweaveEconomy

INTENDED FUNCTION (About.xml): hyperweave IS shokkweave and the Webwork is its only source: Hyperweave renamed (defName unchanged), silk knots and nests scattered on Webwork maps, and the Hutt cartel egg market trader.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * silk_scatter_places_knots / nest_scatter_places_nests on an RUT_Webwork map
  * hyperweave_reads_shokkweave: ThingDef Hyperweave's live label names shokkweave
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * the trader/quest/commonality strip (it lives in the free mod)
  * RUT_Caravan_HuttCartel_EggMarket arriving and stocking eggs

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
    suite = Suite("ShokkweaveEconomy")
    suite.toggles = sorted(mod_static.bool_settings(HERE))
    suite.biome = "RUT_Webwork"

    def _count(t, d):
        r = t.bridge_call("jawa/list_things", defName=d, limit=1)
        if not t._guard():
            return 0
        if not (r or {}).get("success") or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) failed: %r" % (d, r))
        return int(r["countMatched"])

    @suite.chain("silk_scatter")
    def _scatter_0(t):
        with t.component("silk_scatter_places_knots", toggle="scatterEnabled"):
            before = _count(t, "RUT_Webwork_SilkKnot")
            r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_WebworkSilkScatter")
            if t._guard():
                if not (r or {}).get("success"):
                    raise ExpectationFailed("run_genstep(RUT_WebworkSilkScatter) failed: %r" % (r,))
                after = _count(t, "RUT_Webwork_SilkKnot")
                if after <= before:
                    raise ExpectationFailed("RUT_WebworkSilkScatter on a RUT_Webwork map placed no RUT_Webwork_SilkKnot (%d -> %d)" % (before, after))

    @suite.chain("nest_scatter")
    def _scatter_1(t):
        with t.component("nest_scatter_places_nests", toggle="scatterEnabled"):
            before = _count(t, "RUT_Webwork_Nest")
            r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_WebworkNestScatter")
            if t._guard():
                if not (r or {}).get("success"):
                    raise ExpectationFailed("run_genstep(RUT_WebworkNestScatter) failed: %r" % (r,))
                after = _count(t, "RUT_Webwork_Nest")
                if after <= before:
                    raise ExpectationFailed("RUT_WebworkNestScatter on a RUT_Webwork map placed no RUT_Webwork_Nest (%d -> %d)" % (before, after))

    @suite.chain("shokkweave_rename")
    def _rename(t):
        with t.component("hyperweave_reads_shokkweave", beyond_toggle=True):
            rows, missing = shipped_defs._get_defs(t, ["ThingDef/Hyperweave"], ("label",))
            if t._guard():
                row = rows.get("Hyperweave")
                if missing or not row or "shokkweave" not in repr(row).lower():
                    raise ExpectationFailed("Hyperweave does not read as shokkweave: %r missing=%r" % (row, missing))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_Webwork_SilkKnot', 'RUT_Webwork_Nest'), min_count=5)
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
