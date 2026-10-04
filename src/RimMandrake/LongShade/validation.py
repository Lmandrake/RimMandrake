"""validation.py -- modcheck suite for RimMandrake: Long Shade (mandrake.rm.longshade).

First north-star script (LONG_SHADE_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/LongShade.md.
A dayside desert biome (RM_LongShade) with 22 native creatures, 5 native plants, the vorrel cycle plant, two map
generation steps (Crawler Road, Sun Graves), the Shipfall Commons think tree and a Harmony rim gate for the dewfringe.
Fold-aware: when folded into mandrake.rm.biomes the mod is active under the composed name 'RimMandrake: Baroque Biomes';
every read here is by def name / Harmony id, never by mod name.

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip every `public static` bool the C# declares (RM_LongShadeSettings): default / write / restore.
  biome_wiring       RM_LongShade's animalDensity and plantDensity are > 0 (animalDensity 0 would make the whole roster dead
                     content) and both gen steps resolve.
  dewfringe_gate     the Harmony postfix on WildPlantSpawner.CalculatePlantsWhichCanGrowAt is attached by this mod.
  map_mechanics      Crawler Road, Sun Graves, Shipfall Commons, mirrak ambush: UNMEASURED (each says what it needs).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.LongShade.RM_LongShadeSettings"
HARMONY_ID = "mandrake.rm.longshade"
BIOME = "RM_LongShade"
CONTROL_ABSENT = "ThingDef/RM_LongShadeNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML (never a hand list)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_LongShadeSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_LongShadeMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_LongShadeSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) < 10:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_LongShadeMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RM_LongShade.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("BiomeDef", "GenStepDef", "ThingDef", "PawnKindDef", "HediffDef", "RecipeDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if (("BiomeDef", BIOME)) not in SHIPPED:
        bad.append("BiomeDef %s missing" % BIOME)
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_LongShade.xml")).getroot()
    if not float(biome.findtext(".//animalDensity") or 0) > 0:
        bad.append("animalDensity is 0: the roster is dead content")
    gs = ET.parse(os.path.join(HERE, "Defs", "MapGeneration", "RM_LongShade_GenSteps.xml")).getroot()
    mapgen = open(os.path.join(HERE, "Source", "RM_LongShadeMapgen.cs"), encoding="utf-8").read()
    for g in gs.iter("genStep"):
        cls = g.get("Class", "").split(".")[-1]
        if "class %s" % cls not in mapgen:
            bad.append("gen step class %s not found in RM_LongShadeMapgen.cs" % cls)
    if "WildPlantSpawner" not in open(os.path.join(HERE, "Source", "RM_Patch_DewfringeWildSpawnGate.cs"), encoding="utf-8").read():
        bad.append("dewfringe gate no longer patches WildPlantSpawner")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "LongShade.md")):
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
    suite = Suite("LongShade")
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
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
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
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
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

    @suite.chain("biome_wiring")
    def biome_wiring(t):
        with t.component("animal_and_plant_density_positive", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="animalDensity,plantDensity", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read %s: %r" % (BIOME, r))
                f = rows[0].get("fields") or {}
                try:
                    ad, pd = float(f.get("animalDensity")), float(f.get("plantDensity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return numeric densities: %r" % (f,))
                    return
                if not ad > 0:
                    raise ExpectationFailed("animalDensity %s: the roster would never spawn" % ad)
                if not pd > 0:
                    raise ExpectationFailed("plantDensity %s: the flora would never spawn" % pd)
        with t.component("gen_steps_resolve", beyond_toggle=True):
            names = ["GenStepDef/%s" % n for ty, n in SHIPPED if ty == "GenStepDef"]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t) and (not isinstance(r, dict) or r.get("notFound") or int(r.get("foundCount", 0)) != len(names)):
                raise ExpectationFailed("gen steps did not resolve: %r" % r)

    @suite.chain("dewfringe_gate")
    def dewfringe_gate(t):
        with t.component("rim_gate_postfix_attached", toggle="dewfringeShadeLineGateEnabled"):
            r = t.bridge_call("jawa/harmony_patches", typeName="WildPlantSpawner", methodName="CalculatePlantsWhichCanGrowAt")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                    return
                owners = []
                for m in (r.get("methods") or []):
                    owners.extend(p.get("owner") for p in (m.get("postfixes") or []))
                if HARMONY_ID not in owners:
                    raise ExpectationFailed("WildPlantSpawner.CalculatePlantsWhichCanGrowAt carries no postfix from %s (owners: %s)"
                                            % (HARMONY_ID, sorted(set(o for o in owners if o))[:8]))
        with t.component("rim_only_growth_on_a_long_shade_map", toggle="modEnabled"):
            if _live(t):
                _unmeasured(t, "wild dewfringe appearing only on shade-boundary cells needs a generated RM_LongShade map "
                               "with shade patches (CreatureBehaviors shade grid)")

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        for name, toggle, why in (
            ("crawler_road_laid_at_mapgen", "crawlerRoadEnabled",
             "a line of wrecks across the widest shade gap exists only on a map GENERATED as RM_LongShade with the toggle on, "
             "and none with it off; the bridge cannot generate a map"),
            ("sun_graves_laid_at_mapgen", "sunGravesEnabled",
             "sun-grave corpses with their load exist only on a generated RM_LongShade map; needs map generation"),
            ("shipfall_commons_draws_wildlife", "shipfallCommonsEnabled",
             "wildlife gathering round a landed gravship in rungs, and scattering when a pilot takes the console, needs a "
             "landed gravship on an RM_LongShade map (gravship_land) and game days of ticks"),
        ):
            with t.component(name, toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)
        with t.component("mirrak_false_shade_ambush", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "the mirrak ambush is a CreatureBehaviors mechanism switched on that mod's screen; it needs a live "
                               "shade patch, a mirrak and a passing pawn")
        with t.component("vorrel_cycle", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "the vorrel's seasonal cycle plant, items, recipe and thought need game days; defs resolve in defs_resolve")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
