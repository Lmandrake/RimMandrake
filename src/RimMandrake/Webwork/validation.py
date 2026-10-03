"""validation.py -- modcheck suite for RimMandrake: Webwork (mandrake.rm.webwork).

First north-star script (WEBWORK_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/Webwork.md
(`## must be true`, agent-owned, not hashed). Process: design/RimMandrake/debug_process.md section 2.

The mod: RM_Webwork jungle biome, 16 invented plants, 5 invented animals, the owner species RM_Ollathrix (mouth-loom
spit, loom-bound hediff, sun-scald), and the nest + egg economy (a guaranteed nest on every Webwork map, a mineable egg
clutch that the nest wall re-seeds while an ollathrix lives, an inert contraband egg item). Fold-aware: when folded into
mandrake.rm.biomes the mod is active under the composed name 'RimMandrake: Baroque Biomes'; reads here are by def name
and settings type, never by mod name.

CHAINS
  defs_resolve        every def under Defs/ resolves live (parsed from the XML); a control reads notFound.
  settings_roundtrip  every `public static` scalar of RM_WebworkSettings (found by regex): default / write / restore.
  biome_wiring        animalDensity and plantDensity > 0; the 6 roster rows and the nest scatter step on MapCommonBase.
  nest_egg_state      the nest wall carries the relay comp, the clutch mines to the egg, the egg is inert contraband
                      with NO hatcher comp (ban 1), the ollathrix is dormant-capable with the turret comp.
  scald_binding       the sun-scald hediff resolves to the CreatureBehaviors class (hard dependency).
  map_mechanics       nest placement at mapgen, the 20-30 day re-lay, emergent spawn on destroy, sun-scald in sun,
                      loom spit: UNMEASURED, each says what it needs.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = "RM_Webwork"
SETTINGS = "RimMandrake.Webwork.RM_WebworkSettings"
SETTINGS_SRC = os.path.join("Source", "RM_WebworkMod.cs")
CONTROL_ABSENT = "ThingDef/RM_WebworkNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=(?!>)\s*([^;]+);")


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML."""
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
    """{name: type} for every scalar `public static` field of RM_WebworkSettings, read from the C#."""
    src = re.sub(r"//[^\n]*", "", _read(SETTINGS_SRC))
    body = src.split("class RM_WebworkSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(body))


def _biome():
    return ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Webwork_Biome.xml")).getroot().find("BiomeDef")


def static_checks():
    bad = []
    # WEBWORK_HEAT_SHADE_BUILD_1: the biome declares an overhead sun-heat kind (state read lives in the live chain)
    biome_txt = _read(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Webwork_Biome.xml"))
    if 'Class="RimMandrake.CreatureBehaviors.RM_SunHeatExtension"' not in biome_txt or "<heatKind>overhead</heatKind>" not in biome_txt:
        bad.append("RM_Webwork lacks an overhead RM_SunHeatExtension")
    if len(SHIPPED) < 30:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 5:
        return ["settings probe found %d scalar fields, floor 5 (sanity probe failed)" % len(fields)]
    src = _read(SETTINGS_SRC)
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    # a setting no code reads gates nothing (the "screen that lies" trap)
    code = "".join(_read(os.path.join("Source", f)) for f in os.listdir(os.path.join(HERE, "Source"))
                   if f.endswith(".cs") and f != "RM_WebworkMod.cs")
    for n in fields:
        if "RM_WebworkSettings.%s" % n not in code:
            bad.append("settings field %s is read by no other source file (it gates nothing)" % n)
    proj = _read(os.path.join("Source", "RM_Webwork.csproj"))
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(t for t, _n in SHIPPED)
    for need in ("BiomeDef", "ThingDef", "PawnKindDef", "HediffDef", "GenStepDef", "SoundDef", "DamageDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    b = _biome()
    if b is None or b.findtext("defName") != BIOME:
        bad.append("BiomeDef %s not parsed" % BIOME)
    else:
        if not float(b.findtext("animalDensity") or 0) > 0:
            bad.append("animalDensity is 0: the roster is dead content")
        if len(list(b.find("wildAnimals"))) < 6:
            bad.append("wildAnimals has fewer than 6 rows")
        if len(list(b.find("wildPlants"))) < 16:
            bad.append("wildPlants has fewer than 16 rows")
    for cls in ("RM_GenStep_WebworkNest", "RM_CompEggClutchRelay", "RM_CompEmergentSpawnOnDestroy", "RM_BiomeWorker_Webwork"):
        if not any(("class %s" % cls) in _read(os.path.join("Source", f)) for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs")):
            bad.append("class %s not found in Source/" % cls)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "Webwork.md")):
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
    suite = Suite("Webwork")
    suite.toggles = sorted(n for n, ty in settings_fields().items() if ty == "bool")

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
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    def _flat(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k)
                for x in _flat(v):
                    yield x
        elif isinstance(o, (list, tuple)):
            for v in o:
                for x in _flat(v):
                    yield x
        elif o is not None:
            yield str(o)

    def _deep(t, spec, fields):
        """One deep get_defs row's `fields` dict, or None after recording UNMEASURED (tool could not answer)."""
        r = t.bridge_call("jawa/get_defs", defs=spec, fields=fields, deep=True, limit=2)
        if not _live(t):
            return None
        rows = (r or {}).get("defs") or []
        if not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 1 or not rows:
            raise ExpectationFailed("%s did not resolve: %s" % (spec, str(r)[:200]))
        f = rows[0].get("fields") or {}
        if not f:
            _unmeasured(t, "get_defs returned no fields for %s (%s)" % (spec, fields))
            return None
        return f

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
            for i in range(0, len(names), 40):
                r = t.bridge_call("jawa/get_defs", defs=";".join(names[i:i + 40]), fields="defName", limit=60)
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
            with t.component("%s_round_trips" % field, toggle=(field if ty == "bool" else None), beyond_toggle=(ty != "bool")):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) + 1.0)
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
        b = _biome()
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
        with t.component("roster_rows_present", beyond_toggle=True):
            want = [c.tag for c in b.find("wildAnimals")]
            f = _deep(t, "BiomeDef/" + BIOME, "wildAnimals")
            if f is not None:
                blob = "|".join(_flat(f.get("wildAnimals")))
                if not blob:
                    _unmeasured(t, "get_defs did not serialise wildAnimals")
                    return
                missing = [n for n in want if n not in blob]
                if missing:
                    raise ExpectationFailed("biome lacks roster rows the XML ships: %s" % missing)
        with t.component("nest_scatter_step_on_map_common_base", toggle="nestEnabled"):
            r = t.bridge_call("jawa/get_defs", defs="MapGeneratorDef/MapCommonBase", fields="genSteps", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows or "genSteps" not in (rows[0].get("fields") or {}):
                    _unmeasured(t, "get_defs did not serialise MapCommonBase.genSteps: %s" % str(r)[:140])
                    return
                if "RM_WebworkNestScatter" not in "|".join(_flat(rows[0]["fields"]["genSteps"])):
                    raise ExpectationFailed("MapCommonBase.genSteps lacks RM_WebworkNestScatter: the nest patch did not apply")

    @suite.chain("nest_egg_state")
    def nest_egg_state(t):
        with t.component("nest_wall_carries_the_relay_comp", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Webwork_NestWall", "comps")
            if f is not None:
                blob = "|".join(_flat(f.get("comps")))
                if "EggClutchRelay" not in blob:
                    if "comps" not in f or not blob:
                        _unmeasured(t, "get_defs did not serialise comps")
                        return
                    raise ExpectationFailed("the nest wall no longer carries RM_CompProperties_EggClutchRelay: %s" % blob[:200])
        with t.component("clutch_mines_to_the_egg", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Webwork_EggClutch", "building")
            if f is not None:
                blob = "|".join(_flat(f.get("building")))
                if not blob:
                    _unmeasured(t, "get_defs did not serialise the building block")
                    return
                if "RM_OllathrixEgg" not in blob:
                    raise ExpectationFailed("the egg clutch no longer mines to RM_OllathrixEgg: %s" % blob[:200])
        with t.component("egg_is_inert_contraband_with_no_hatcher", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_OllathrixEgg", "tradeability,tradeTags,comps")
            if f is not None:
                if "Hatcher" in "|".join(_flat(f.get("comps"))):
                    raise ExpectationFailed("the egg carries a hatcher comp: ban 1 (inert cargo, it must never hatch)")
                if "RM_Contraband" not in "|".join(_flat(f.get("tradeTags"))):
                    raise ExpectationFailed("the egg lost its RM_Contraband trade tag: %r" % (f.get("tradeTags"),))
                if "Sellable" not in "|".join(_flat(f.get("tradeability"))):
                    raise ExpectationFailed("the egg tradeability is %r, not Sellable" % (f.get("tradeability"),))
        with t.component("ollathrix_is_dormant_capable_with_a_turret_gun", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Ollathrix", "comps")
            if f is not None:
                blob = "|".join(_flat(f.get("comps")))
                if not blob:
                    _unmeasured(t, "get_defs did not serialise comps")
                    return
                for need in ("CanBeDormant", "TurretGun"):
                    if need not in blob:
                        raise ExpectationFailed("RM_Ollathrix lacks a %s comp (ambush burst / loom spit): %s" % (need, blob[:200]))

    @suite.chain("scald_binding")
    def scald_binding(t):
        with t.component("sun_scald_hediff_class_is_the_creature_behaviors_one", beyond_toggle=True):
            f = _deep(t, "HediffDef/RM_Webwork_SunScald", "hediffClass")
            if f is not None:
                if "RM_Hediff_SunScald" not in "|".join(_flat(f.get("hediffClass"))):
                    raise ExpectationFailed("RM_Webwork_SunScald hediffClass is %r, not RM_Hediff_SunScald (mandrake.rm.creaturebehaviors)" % (f.get("hediffClass"),))

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        for name, toggle, why in (
            ("nest_placed_at_mapgen", "nestEnabled",
             "one nest wall and 2-3 clutches exist only on a map GENERATED as RM_Webwork with the toggle on, none with it off; the bridge cannot generate a map"),
            ("clutch_relays_every_20_to_30_days", "eggRelayIntervalMultiplier",
             "the re-lay needs a nest wall, a live ollathrix and 20-30 game days of ticks"),
            ("emergent_spawn_on_destroy", "emergentSpawnEnabled",
             "a 3 percent roll per destruction needs a def that carries the comp (none ships attached yet) and many trials"),
            ("emergent_spawn_chance_scales", "emergentSpawnChanceMultiplier",
             "statistical; no def in this mod carries the comp, so there is nothing to destroy"),
            ("webwork_competes_for_tiles", "generateOnWorldgen",
             "worldgen-affecting and inert on the frozen world (CLAUDE.md: no worldgen feature); no map can exercise it"),
        ):
            with t.component(name, toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)
        for name, why in (
            ("sun_scald_in_open_sun", "a sun-scald hediff on an ollathrix in sunlight needs a spawned ollathrix on a lit map and ticks"),
            ("loom_spit_fires", "the ranged spit needs an awake ollathrix and a hostile target"),
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
