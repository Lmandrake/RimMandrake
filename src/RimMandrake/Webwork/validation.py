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


def _base_port_findings():
    bad = []
    txt = lambda rel: re.sub(r"<!--.*?-->", "", _read(rel), flags=re.S)
    st = txt(os.path.join("Defs", "ThingDefs_Buildings", "RM_WebworkStructures.xml"))
    for n in ("Anchor", "Web", "Gutter"):
        m = re.search(r"<defName>RM_Webwork_%s</defName>(.*?)</ThingDef>" % n, st, flags=re.S)
        if not m:
            bad.append("RM_Webwork_%s not defined" % n)
        else:
            if "<Hyperweave>" not in m.group(1) or "RM_CompProperties_SenseWebNode" not in m.group(1):
                bad.append("RM_Webwork_%s needs a thrixweave killedLeavings and a sense-web comp" % n)
            if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Building", "Natural", "RM_Webwork_%s.png" % n)):
                bad.append("RM_Webwork_%s has no texture" % n)
    if "RM_Webwork_Slick" not in txt(os.path.join("Defs", "HediffDefs", "RM_WebworkSlick.xml")):
        bad.append("RM_Webwork_Slick hediff missing")
    biome = txt(os.path.join("Defs", "BiomeDefs", "RM_Webwork_Biome.xml"))
    ext = re.search(r"RM_FrontCreepExtension\">(.*?)</spawnDensity>", biome, flags=re.S)
    if not ext or any("<li>RM_Webwork_%s</li>" % n not in ext.group(1) for n in ("Anchor", "Web", "Gutter")):
        bad.append("RM_Webwork lacks RM_FrontCreepExtension naming the three RM_ structures")
    ren = txt(os.path.join("Patches", "RM_Thrixweave_Rename.xml"))
    if "<label>thrixweave</label>" not in ren:
        bad.append("Hyperweave is not renamed thrixweave")
    oll = txt(os.path.join("Defs", "ThingDefs_Races", "RM_Ollathrix.xml"))
    if not re.search(r"<butcherProducts>\s*<Hyperweave>\d+</Hyperweave>", oll):
        bad.append("RM_Ollathrix has no thrixweave butcher yield")
    # the retired campaign names must be gone repo-wide, with a probe that the search can see anything
    root = os.path.normpath(os.path.join(HERE, "..", ".."))
    gone = re.compile(r"RUT_Webwork_(Anchor|Web|Gutter|Slick)\b")
    probe, hits = 0, []
    for dp, _d, files in os.walk(root):
        if "__pycache__" in dp or os.sep + "Textures" in dp or os.sep + "Assemblies" in dp:
            continue
        for fn in files:
            if fn.endswith((".xml", ".cs", ".py")):
                try:
                    body = open(os.path.join(dp, fn), encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    continue
                if "RM_Webwork_NestWall" in body:
                    probe += 1
                if gone.search(body) and fn != "validation.py":
                    hits.append(os.path.relpath(os.path.join(dp, fn), root))
    if probe == 0:
        bad.append("sanity probe: RM_Webwork_NestWall found in no source file (the walk cannot see)")
    if hits:
        bad.append("retired RUT_Webwork_Anchor/Web/Gutter/Slick still named in: %s" % sorted(hits)[:6])
    return bad


def _traction_lance_findings():
    """WEBWORK_TRACTION_LANCE_BUILD_1, offline half: one pull, two buildings, two doors, fabric tether."""
    bad = []
    rm = os.path.normpath(os.path.join(HERE, ".."))
    pull_cls = "RimMandrake.CreatureBehaviors.RM_CompProperties_TetherPull"
    lance = _read(os.path.join("Defs", "ThingDefs_Buildings", "RM_TractionLance.xml"))
    cap_p = os.path.join(rm, "TheSump", "Defs", "ThingDefs_Buildings", "RM_CapstanTurret.xml")
    cap = open(cap_p, encoding="utf-8").read() if os.path.isfile(cap_p) else ""
    if pull_cls not in lance:
        bad.append("RM_TractionLance does not carry the shared RM_CompTetherPull")
    if pull_cls not in cap:
        bad.append("RM_CapstanTurret does not carry the shared RM_CompTetherPull")
    for f in ("Cloth", "DevilstrandCloth", "Hyperweave"):
        if "<stuff>%s</stuff>" % f not in lance:
            bad.append("RM_TractionLance has no tether factor for %s" % f)
    if "<li>Fabric</li>" not in lance or "RM_Research_TractionLance" not in lance:
        bad.append("RM_TractionLance is not fabric-stuffed or not gated on RM_Research_TractionLance")
    # One pull implementation: the forced-move call (Notify_Teleported in a reel) lives only in RM_CompTetherPull.
    # Sanity probe: the search must find the shared class itself, or it is blind.
    pull_sites, saw_shared = [], False
    for mod in ("CreatureBehaviors", "TheSump", "Webwork"):
        src = os.path.join(rm, mod, "Source")
        for dp, _d, files in os.walk(src):
            for fn in files:
                if not fn.endswith(".cs"):
                    continue
                txt = open(os.path.join(dp, fn), encoding="utf-8").read()
                if "Notify_Teleported(" in txt and ("ReelStep" in txt or "TryRope" in txt):
                    if fn == "RM_CompTetherPull.cs":
                        saw_shared = True
                    else:
                        pull_sites.append(fn)
    if not saw_shared:
        bad.append("sanity probe: the pull search did not find RM_CompTetherPull.cs (the check is blind)")
    if pull_sites:
        bad.append("a second pull implementation exists: %s" % sorted(pull_sites))
    junction = _read(os.path.join("Defs", "ThingDefs_Items", "RM_GutterJunction.xml"))
    if "RM_CompProperties_AnalyzableGrantResearch" not in junction or "RM_Research_TractionLance" not in junction:
        bad.append("RM_GutterJunction does not grant RM_Research_TractionLance")
    structures = _read(os.path.join("Defs", "ThingDefs_Buildings", "RM_WebworkStructures.xml"))
    if "<specimen>RM_GutterJunction</specimen>" not in structures or "<alwaysDeconstructible>true</alwaysDeconstructible>" not in structures:
        bad.append("RM_Webwork_Gutter cannot be cut out into an RM_GutterJunction")
    dj_p = os.path.join(rm, "TheSump", "Defs", "ThingDefs_Items", "RUT_PreservedDrawJoint.xml")
    if os.path.isfile(dj_p) and "RM_Research_TractionLance" not in open(dj_p, encoding="utf-8").read():
        bad.append("the Sump draw-joint does not grant RM_Research_TractionLance")
    return bad


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
    # WEBWORK_BASE_PORT_BUILD_1: structures, front extension, thrixweave rename, butcher yield (parsed from the XML)
    bad.extend(_base_port_findings())
    bad.extend(_traction_lance_findings())
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
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
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
            # LIVE 2026-10-03: get_defs renders a BiomeAnimalRecord without the animal's name (the live roster was complete and the
            # check still read 6 rows missing); jawa/biome_probe lists the resolved roster by defName.
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, limit=100)
            if _live(t):
                brows = (((r or {}).get("biomes") or [{}])[0].get("animals") or []) if isinstance(r, dict) else []
                names = set(a.get("defName") for a in brows)
                if not names:
                    _unmeasured(t, "biome_probe returned no roster for %s: %s" % (BIOME, str(r)[:140]))
                    return
                missing = [n for n in want if n not in names]
                if missing:
                    raise ExpectationFailed("biome lacks roster rows the XML ships: %s (live roster: %s)" % (missing, sorted(names)))
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
                # LIVE 2026-10-03: a substring over the whole comps dump matched CompRottable's own field name `disableIfHatcher`;
                # only a comp CLASS named Hatcher is a hatcher.
                classes = [str(c.get("compClass")) for c in (f.get("comps") or []) if isinstance(c, dict)]
                if any("Hatcher" in c for c in classes):
                    raise ExpectationFailed("the egg carries a hatcher comp: ban 1 (inert cargo, it must never hatch)")
                if "RM_Contraband" not in "|".join(_flat(f.get("tradeTags"))):
                    raise ExpectationFailed("the egg lost its RM_Contraband trade tag: %r" % (f.get("tradeTags"),))
                # LIVE 2026-10-03: reads 'All' (Buyable|Sellable) on the campaign list, where the RUT patch replaces the
                # def's explicit Sellable; both let the player sell it, which is the property under test.
                if "|".join(_flat(f.get("tradeability"))) not in ("Sellable", "All"):
                    raise ExpectationFailed("the egg tradeability is %r, not Sellable or All" % (f.get("tradeability"),))
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

    @suite.chain("thrixweave_and_front")
    def thrixweave_and_front(t):
        """WEBWORK_BASE_PORT_BUILD_1: state reads. Free tier only (the campaign layer repaints the label to shokkweave)."""
        with t.component("hyperweave_reads_thrixweave", beyond_toggle=True):
            f = _deep(t, "ThingDef/Hyperweave", "label")
            if f is not None and "thrixweave" not in "|".join(_flat(f.get("label"))).lower():
                raise ExpectationFailed("Hyperweave label reads %r, expected thrixweave (free tier)" % (f.get("label"),))
        with t.component("trader_strip_applied", toggle="thrixweaveTraderStripEnabled"):
            f = _deep(t, "ThingDef/Hyperweave", "tradeability")
            if f is not None and "Sellable" not in "|".join(_flat(f.get("tradeability"))):
                raise ExpectationFailed("Hyperweave tradeability reads %r with the strip on, expected Sellable" % (f.get("tradeability"),))
        with t.component("front_creep_extension_on_biome", toggle="frontCreepEnabled"):
            f = _deep(t, "BiomeDef/" + BIOME, "modExtensions")
            # LIVE 2026-10-03: get_defs renders a modExtension as its fields without the class name; the front-creep extension is the
            # one carrying frontThingDefNames.
            exts = [e for e in (f.get("modExtensions") or []) if isinstance(e, dict)] if f is not None else []
            if f is not None and not any("frontThingDefNames" in e for e in exts):
                raise ExpectationFailed("RM_Webwork carries no RM_FrontCreepExtension with the toggle on: %r" % (f.get("modExtensions"),))
        with t.component("structures_resolve", beyond_toggle=True):
            for n in ("Anchor", "Web", "Gutter"):
                f = _deep(t, "ThingDef/RM_Webwork_" + n, "killedLeavings")
                if f is not None and "Hyperweave" not in "|".join(_flat(f.get("killedLeavings"))):
                    raise ExpectationFailed("RM_Webwork_%s yields no Hyperweave on kill: %r" % (n, f.get("killedLeavings")))

    @suite.chain("scald_binding")
    def scald_binding(t):
        with t.component("sun_scald_hediff_class_is_the_creature_behaviors_one", beyond_toggle=True):
            f = _deep(t, "HediffDef/RM_Webwork_SunScald", "hediffClass")
            if f is not None:
                if "RM_Hediff_SunScald" not in "|".join(_flat(f.get("hediffClass"))):
                    raise ExpectationFailed("RM_Webwork_SunScald hediffClass is %r, not RM_Hediff_SunScald (mandrake.rm.creaturebehaviors)" % (f.get("hediffClass"),))

    def _wp(t, method, args):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Webwork.RM_WebworkProof", method=method, args=args)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    def _num(text, key):
        import re as _re
        m = _re.search(key + r" ([\d.\-]+)", text)
        return float(m.group(1)) if m else None

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        """WEBWORK_COVERAGE_GAPS_1. Runs on the CURRENT map through RM_WebworkProof (static_call); each proof sets
        its settings for the call and restores them. Not proven here: the GenStep firing inside real mapgen
        (static: it is in the biome's genSteps, biome_wiring), sun-scald, loom spit, front creep."""
        with t.component("nest_placed_by_the_genstep", toggle="nestEnabled"):
            text = _wp(t, "ProofNest", "true")
            if _live(t):
                if not text.startswith("NEST"):
                    _unmeasured(t, "ProofNest gave no answer: %r" % text[:160]); return
                if "biomeGateRefuses False" in text:
                    raise ExpectationFailed("the nest GenStep placed a nest on a non-Webwork map: %s" % text)
                walls = text.split("walls ")[1].split(" |")[0].split("->")
                if not (_num(text, "placed") or 0) >= 1 or int(walls[1]) != int(walls[0]) + 1:
                    raise ExpectationFailed("the nest placement did not lay one wall and >= 1 clutch: %s" % text)
            off = _wp(t, "ProofNest", "false")
            if _live(t) and not ("placed -1" in off and off.split("walls ")[1].split(" |")[0].split("->")[0] == off.split("walls ")[1].split(" |")[0].split("->")[1]):
                raise ExpectationFailed("nestEnabled off still placed a nest: %s" % off)
        with t.component("clutch_relays_every_20_to_30_days", toggle="eggRelayIntervalMultiplier", beyond_toggle=True):
            text = _wp(t, "ProofRelay", "true|1")
            if _live(t):
                if not text.startswith("RELAY"):
                    _unmeasured(t, "ProofRelay gave no answer: %r" % text[:160]); return
                d = _num(text, "intervalDays")
                if d is None or not (20.0 <= d <= 30.0):
                    raise ExpectationFailed("relay interval at multiplier 1 is not 20-30 days: %s" % text)
                if not text.endswith("0->1") and not text.endswith("0->2"):
                    raise ExpectationFailed("a due nest with a living mother and no clutch did not re-lay 1-2: %s" % text)
            half = _wp(t, "ProofRelay", "true|0.5")
            if _live(t):
                d = _num(half, "intervalDays")
                if d is None or not (10.0 <= d <= 15.0):
                    raise ExpectationFailed("eggRelayIntervalMultiplier 0.5 did not halve the interval: %s" % half)
        with t.component("dying_nest_without_mother_relays_nothing", beyond_toggle=True):
            text = _wp(t, "ProofRelay", "false|1")
            if _live(t) and not ("mother False" in text and text.endswith("0->0")):
                raise ExpectationFailed("a nest with no living ollathrix re-laid: %s" % text)
        with t.component("emergent_spawn_on_destroy", toggle="emergentSpawnEnabled"):
            text = _wp(t, "ProofEmergent", "true|1|1|Vanish")
            if _live(t):
                if not text.startswith("EMERGENT"):
                    _unmeasured(t, "ProofEmergent gave no answer: %r" % text[:160]); return
                if "spawned 1" not in text or "manhunter True" not in text:
                    raise ExpectationFailed("a sure harvest (chance 1) did not spawn one manhunter ollathrix: %s" % text)
            for args, why in (("false|1|1|Vanish", "emergentSpawnEnabled off"), ("true|1|1|KillFinalize", "a combat kill (not a harvest)")):
                text = _wp(t, "ProofEmergent", args)
                if _live(t) and "spawned 0" not in text:
                    raise ExpectationFailed("%s still spawned: %s" % (why, text))
        with t.component("emergent_spawn_chance_scales", toggle="emergentSpawnChanceMultiplier", beyond_toggle=True):
            text = _wp(t, "ProofEmergent", "true|0.5|2|Vanish")
            if _live(t) and "spawned 1" not in text:
                raise ExpectationFailed("chance 0.5 x multiplier 2 (= 1) did not spawn: %s" % text)
            text = _wp(t, "ProofEmergent", "true|1|0|Vanish")
            if _live(t) and "spawned 0" not in text:
                raise ExpectationFailed("multiplier 0 still spawned: %s" % text)
        with t.component("webwork_competes_for_tiles", toggle="generateOnWorldgen"):
            if _live(t):
                _unmeasured(t, "worldgen-affecting and inert on the frozen world (CLAUDE.md: no worldgen feature); no map can exercise it")
        for name, why in (
            ("sun_scald_in_open_sun", "RM_Hediff_SunScald lives in mandrake.rm.creaturebehaviors: its proof belongs there (an ollathrix in lit sun, ticks)"),
            ("loom_spit_fires", "the ranged spit needs an awake ollathrix and a hostile target"),
            ("front_creep_advances", "frontCreepEnabled is consumed by CreatureBehaviors' front-creep, not Webwork C#; proof belongs there"),
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
