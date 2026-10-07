"""validation.py -- first north-star script for RimUtinni: CathedralPass (mandrake.rut.cathedralpass).

CATHEDRAL_MECHANOID_PASS_VERBS_1. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run CathedralPass

INTENDED FUNCTION (About.xml): a clan pawn carrying RUT_CathedralPass is read as non-hostile by faction-13
(Faction.OfMechanoids) machines, on Rust Cathedral maps (RM_RustCathedral / RUT_RustCathedral) only, gated by
the cathedralPassEnabled setting.

WHAT IT PROVES (live, through existing bridge tools):
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field
  * GenHostility.HostileTo lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * the shipped HediffDef is loaded and its scalar fields read back equal to the XML

NOT PROVEN HERE (first pokes for the next live pass -- the item's own verify bar):
  * on a Cathedral-biome quicktest with hostile faction-13 mechs, MANY pass-holders are untargeted and
    non-holders are targeted (one pawn is RNG)
  * the same pawns ARE targeted on a non-Cathedral map (scope holds)
  * revoking (debug action "Revoke pass") returns targeting; no manhunt/raid behaviour introduced
  * war-lab access unchanged with the pass held (the war lab is not a Cathedral-biome map)
  * GM-verb GRANT/REVOKE: not built (CATHEDRAL_REGARD_BLACKBOARD_1 unbuilt)

STATIC (offline): `python3 validation.py` runs modcheck.mod_static over the mod.
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
    suite = Suite("CathedralPass")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_CathedralPass',), min_count=1)
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
