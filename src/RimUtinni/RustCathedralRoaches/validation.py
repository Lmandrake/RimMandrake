"""validation.py -- first north-star script for RimUtinni: RustCathedralRoaches (mandrake.rut.rustcathedralroaches).

RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1 (RUST_CATHEDRAL_MECHANICS_1 s6). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RustCathedralRoaches

INTENDED FUNCTION (About.xml): the land cleaners of the Scarlands and the Rust Cathedral: much smaller organic scar roaches and strangely tough synthetic cathedral roaches, reskinned from the Rim cockroach donor, with their own think tree, hex body and shell.

WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added, so no DLL was rebuilt):
  * races_spawn: both roach kinds spawn
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * every shipped IncidentDef answers a fire_incident dry run (the worker resolves and CanFireNow does not throw)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)

NOT PROVEN HERE (first pokes for the next live pass):
  * the roaches cleaning filth (their think tree's cleaning job) and the synthetic toughness in combat
  * the donor dependency: whether a donor class is still named anywhere

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
    suite = Suite("RustCathedralRoaches")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    @suite.chain("races_spawn")
    def _races(t):
        for kind in ('RUT_CathedralRoach', 'RUT_ScarRoach'):
            with t.component("spawns_%s" % kind, beyond_toggle=True):
                pid = t.spawn_pawn(kind)
                if t._guard() and not pid:
                    raise ExpectationFailed("spawn_pawn(%s) returned no pawn" % kind)

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_CathedralRoach', 'RUT_ScarRoach'), min_count=6)
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
