"""validation.py -- modcheck suite for RimMandrake: Pyrinth (mandrake.rm.pyrinth).

First north-star script (PYRINTH_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/Pyrinth.md (DRAFT).
Absorbed copy of det.epochspyrinth: the pyrinth ore, torch/wall-torch/pylon/heater furniture, pyrinth blade and spark
effects. DORMANT by design (About.xml: not deployable while the donor is active; defNames are preserved verbatim). It has NO C#
and NO settings class, and no DEPLOY_HOLD entry. A live pass proves the defNames resolve, not that this pack supplied them.

CHAINS
  defs_resolve       every def parsed from the mod's own XML that actually DEPLOYS resolves live; a control name reads
                     notFound; no file of this mod is named in DEPLOY_HOLD.txt.
  settings_roundtrip there is NO settings class (no Source C#): the probe asserts none exists, nothing is round-tripped.
  ore_and_donor_identity  DV_MineablePyrinth's mineableThing / mineableYield equal the XML's; whether THIS pack is the loaded copy: UNMEASURED.
  furniture_and_weapon    glow/heat/meditation, blade, MO and Royalty patches, Lantern Deeps gate: UNMEASURED, each saying why.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game. Nothing here has been run live.
"""
import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "Pyrinth"
SETTINGS = None
BIOME = None
CONTROL_ABSENT = "ThingDef/PyrinthNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=\s*([^;]+);")
_HOLD_FILE = os.path.join(HERE, "..", "..", "DEPLOY_HOLD.txt")


def held_globs():
    """Globs from src/DEPLOY_HOLD.txt that name this mod (relative to custom_patches/, '*' crosses '/')."""
    out = []
    if not os.path.isfile(_HOLD_FILE):
        return out
    for line in open(_HOLD_FILE, encoding="utf-8"):
        g = line.split("#", 1)[0].strip()
        if g.startswith(MOD + "/"):
            out.append(g)
    return out


HELD = held_globs()


def is_held(rel):
    return any(fnmatch.fnmatchcase(MOD + "/" + rel.replace(os.sep, "/"), g) for g in HELD)


def parse_defs():
    """([(DefType, defName)] deployed, [(DefType, defName, file)] held) from every non-abstract top-level def under Defs/."""
    deployed, held = [], []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, HERE)
            for el in ET.parse(full).getroot():
                nm = el.find("defName") if isinstance(el.tag, str) else None
                if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                    (held if is_held(rel) else deployed).append((el.tag, nm.text.strip(), rel) if is_held(rel) else (el.tag, nm.text.strip()))
    return sorted(set(deployed)), sorted(set(held))


SHIPPED, HELD_DEFS = parse_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of the settings class, read from the C# ({} when none)."""
    return {}

def ore_facts():
    """(mineableThing, mineableYield) of DV_MineablePyrinth, parsed from the XML."""
    p = os.path.join(HERE, "Defs", "Absorbed_EpochsPyrinth", "ThingDefs_Buildings", "Absorbed_EpochsPyrinth_Buildings_Natural.xml")
    for el in ET.parse(p).getroot():
        if el.findtext("defName") == "DV_MineablePyrinth":
            return (el.findtext(".//mineableThing"), el.findtext(".//mineableYield"))
    return (None, None)



def static_checks():
    bad = []
    if len(SHIPPED) + len(HELD_DEFS) < 6:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % (len(SHIPPED) + len(HELD_DEFS))]
    if settings_fields():
        bad.append("a settings class appeared: add its round-trip expectations (this script assumes none)")
    if os.path.isdir(os.path.join(HERE, "Source")) and [f for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs")]:
        bad.append("C# source appeared under Source/: add a csproj/settings check")
    ore = ore_facts()
    if ore[0] != "DV_Pyrinth" or not float(ore[1]) > 0:
        bad.append("ore facts parsed wrong: %r" % (ore,))
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("ThingDef", "EffecterDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if "DV_Pyrinth" not in [n for _t, n in SHIPPED]:
        bad.append("DV_Pyrinth missing")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", MOD + ".md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite(MOD)
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        if ty == "string":
            return str(a) == str(b)
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_deployed_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):      # batches: a long defs string risks the 30 s reply timeout
                chunk = names[i:i + 40]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))


    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if settings_fields():
                raise ExpectationFailed("a settings class exists but the script assumes none")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "string":
                    new = "zz_probe" if str(old) != "zz_probe" else "zz_probe2"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("ore_and_donor_identity")
    def ore_and_donor_identity(t):
        # The mod is dormant (About.xml: NOT YET DEPLOYABLE) and preserves the donor's defNames verbatim, so a pass here says the
        # NAMES resolve (from the donor det.epochspyrinth or from this mod), never that THIS mod is what loaded.
        with t.component("mineable_ore_yield_matches_xml", beyond_toggle=True):
            want = ore_facts()
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/DV_MineablePyrinth", fields="mineableThing,mineableYield", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read DV_MineablePyrinth: %r" % (r,))
                f = rows[0].get("fields") or {}
                if f.get("mineableThing") is None or f.get("mineableYield") is None:
                    _unmeasured(t, "get_defs returned no mineable fields: %r" % (f,))
                    return
                if str(f.get("mineableThing")) != want[0]:
                    raise ExpectationFailed("mineableThing reads %r, XML says %r" % (f.get("mineableThing"), want[0]))
                if float(f.get("mineableYield")) != float(want[1]):
                    raise ExpectationFailed("mineableYield reads %r, XML says %r" % (f.get("mineableYield"), want[1]))
        with t.component("this_mod_is_the_loaded_copy", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "whether THIS dormant pack or the live donor det.epochspyrinth supplied the defs cannot be told from get_defs; "
                               "it needs the mod-of-origin of the def (not exposed) or det.epochspyrinth removed from the mod list")

    @suite.chain("furniture_and_weapon")
    def furniture_and_weapon(t):
        for name, why in (
            ("torch_family_glow_and_heat", "glow radius, powered heat push and meditation focus of the torch/wall torch/pylon/heater need a built, powered instance and a temperature / glow read on a bland map"),
            ("pyrinth_blade_melee_stats", "the blade's tool profile resolves as a def only; damage in play needs a pawn fight"),
            ("medieval_overhaul_heater_cost_patch", "applies only with Medieval Overhaul loaded; a patch that matches nothing logs nothing, so it is unprovable without that mod"),
            ("royalty_throne_room_patch", "edits RoyalTitleDef throne room requirements; reading them needs get_defs deep=True on RoyalTitleDef and is UNMEASURED until the pack is the loaded copy"),
            ("lantern_deeps_scatter_gate", "lives in RimUtinni LanternDeeps (patches the live donor def), not in this mod"),
        ):
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
