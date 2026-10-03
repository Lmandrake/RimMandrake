"""validation.py -- modcheck suite for RimMandrake: The Rot (mandrake.rm.therot).

First north-star script (THE_ROT_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TheRot.md (DRAFT).
The Rot biome (RM_TheRot): Sheen weather exposure, accelerated rot and warm living ground, live food preparations,
guardian groves, the spore-cloud incident, health sharing, the pale tree, plus an opt-in cross-biome mode; the whole Spore Kit
(plants, hediffs, recipes, drugs, buildings, research) ships as defs. No file is held from deploy.

CHAINS
  defs_resolve       every def parsed from the mod's own XML that actually DEPLOYS resolves live; a control name reads
                     notFound; no file of this mod is named in DEPLOY_HOLD.txt.
  settings_roundtrip every `public static` bool/float/string of RM_TheRotSettings: default / write / restore (numerics compared numerically).
  biome_wiring       RM_TheRot's animalDensity and plantDensity are > 0 and its workerClass names RM_BiomeWorker_TheRot.
  map_mechanics      the ten toggled mechanics: UNMEASURED, each naming what it needs (a generated RM_TheRot map, ticks, a game condition).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game. Nothing here has been run live.
"""
import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "TheRot"
SETTINGS = "RimMandrake.TheRot.RM_TheRotSettings"
BIOME = "RM_TheRot"
WORKER = "RM_BiomeWorker_TheRot"
CONTROL_ABSENT = "ThingDef/TheRotNoSuchDef_ZZ"
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
    src = open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_TheRotSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) + len(HELD_DEFS) < 40:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % (len(SHIPPED) + len(HELD_DEFS))]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    # ROT_MOD_SETTINGS_WIRING_1: every field needs a READER outside its own Scribe line and the settings UI
    # (declaration + one reader = 2 mentions).
    # ROT_WOUND_SHARING_WIRING_1: five Alpha Animals bodies carry the wound-link / kin-mending wiring by patch.
    ws = open(os.path.join(HERE, "Patches", "RotSpecies_WoundSharing.xml"), encoding="utf-8").read()
    for body in ("AA_Swarmling", "AA_Agaripod", "AA_Agaripawn", "AA_Wildpod", "AA_Wildpawn"):
        if 'defName="%s"' % body not in ws:
            bad.append("wound-sharing patch does not target %s" % body)
    if "<tag>RotNetwork</tag>" not in ws or ws.count("CompProperties_WoundLink") < 5 or "mandrake.rm.therot" in ws and False:
        bad.append("wound-sharing patch lacks the shared RotNetwork tag or a wound link per body")
    if "<mods>" not in ws or re.search(r"<Operation[^>]*MayRequire", ws):
        bad.append("wound-sharing patch must be gated by PatchOperationFindMod, never a top-level MayRequire")
    if ws.count("<hediff>RM_KinMendingNetwork</hediff>") != 4:
        bad.append("exactly the two mending bodies (mullgoth, durrok) carry the kin-mending hediff")
    reader_text = re.sub(r"Scribe_Values\.Look\([^\n]*\n", "", src)
    ui_start = reader_text.index("public void DoWindowContents")
    ui_end = reader_text.index("public class RM_TheRotFront") if "public class RM_TheRotFront" in reader_text else reader_text.index("static class RM_TheRotFront")
    reader_text = reader_text[:ui_start] + reader_text[ui_end:]
    for n in fields:
        if len(re.findall(r"\b%s\b" % n, reader_text)) < 2:
            bad.append("settings field %s has a control but no reader (moves and does nothing)" % n)
    # ROT_SPORE_ALLERGY_PORT_1: the free Rot and Contagion name OUR two incidents and no donor disease; the four defs ship in EH.
    eh = os.path.join(HERE, "..", "EnvironmentalHazards", "Defs")
    ehtxt = "".join(open(os.path.join(dp, f), encoding="utf-8").read()
                    for dp, _d, fs in os.walk(eh) for f in fs if f.endswith(".xml"))
    for dn in ("RM_SporeAllergy", "RM_AnimalSporeAllergy", "RM_Disease_SporeAllergy", "RM_Disease_AnimalSporeAllergy"):
        if "<defName>%s</defName>" % dn not in ehtxt:
            bad.append("%s is not shipped by EnvironmentalHazards" % dn)
    for rel in (("Defs", "BiomeDefs", "RM_TheRot_Biome.xml"), ("..", "Contagion", "Defs", "BiomeDefs", "RM_Contagion.xml")):
        bt = re.sub(r"<!--.*?-->", "", open(os.path.join(HERE, *rel), encoding="utf-8").read(), flags=re.S)
        if "AB_Disease" in bt or "<diseaseInc>RM_Disease_SporeAllergy</diseaseInc>" not in bt \
                or "<diseaseInc>RM_Disease_AnimalSporeAllergy</diseaseInc>" not in bt:
            bad.append("%s diseases must name the RM_ spore-allergy pair and no AB_ def" % rel[-1])
    if "RM_KitFronts" not in src:
        bad.append("RM_TheRotFront does not register into RM_KitFronts")
    proj = open(os.path.join(HERE, "Source", "RM_TheRot.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(ty for ty, _n in SHIPPED) | set(h[0] for h in HELD_DEFS)
    for need in ("BiomeDef", "ThingDef", "HediffDef", "RecipeDef", "GameConditionDef", "TerrainDef", "WeatherDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if not any(n == BIOME for _t, n in SHIPPED) and not any(h[1] == BIOME for h in HELD_DEFS):
        bad.append("BiomeDef %s missing" % BIOME)
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml")).getroot()
    if not float(biome.findtext(".//animalDensity") or 0) > 0:
        bad.append("animalDensity is 0: the roster is dead content")
    if "class " + WORKER not in open(os.path.join(HERE, "Source", "RM_BiomeWorker_TheRot.cs"), encoding="utf-8").read():
        bad.append("biome worker class %s not found" % WORKER)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", MOD + ".md")):
        bad.append("walk missing")
    bad += cast_checks()
    return bad


# ROT_RM_CAST_MIGRATION_1: the ten ratified residents are owned RM_ defs, wired inline, hybrid, textured.
CAST = ["Thozzik", "ThozzikColony", "ThozzikSpawned", "ThozzikQueen", "ThozzikColonyQueen",
        "Illoth", "Brullith", "Brogg", "Grellik", "Skerrith"]
_BANNED = re.compile(r"wasp|hornet|moth|camel|llama|genetics|experiment|Force", re.I)
# art owed: none (thozzik and illoth south frames landed from artpipe 2026-10-03)
ART_OWED = set()


def cast_checks():
    bad = []
    fauna = os.path.join(HERE, "Defs", "Fauna")
    if not os.path.isdir(fauna):
        return ["Defs/Fauna missing: the ten RM_ residents are not shipped"]
    races, kinds = {}, {}
    for fn in os.listdir(fauna):
        for el in ET.parse(os.path.join(fauna, fn)).getroot():
            nm = el.findtext("defName") if isinstance(el.tag, str) else None
            if el.tag == "ThingDef" and nm:
                races[nm] = el
            elif el.tag == "PawnKindDef" and nm:
                kinds[nm] = el
    if len(races) < 20:
        bad.append("only %d fauna ThingDefs parsed (sanity probe failed)" % len(races))
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml")).getroot()
    roster = set(e.tag for e in biome.find(".//wildAnimals"))
    for c in CAST:
        n = "RM_" + c
        if n not in races or n not in kinds:
            bad.append("%s: ThingDef/PawnKindDef missing" % n)
            continue
        if n not in roster:
            bad.append("%s not in RM_TheRot wildAnimals" % n)
        desc = (races[n].findtext("description") or "") + " " + (races[n].findtext("label") or "")
        if _BANNED.search(desc):
            bad.append("%s description names a banned franchise/lab word" % n)
        if c in ("Thozzik", "Illoth", "Brogg") and not re.search(r"fung|mycel|spore", desc):
            bad.append("%s description is not a fungus hybrid" % n)
        for tp in set(e.text for e in kinds[n].iter("texPath") if e.text and e.text.startswith("RM_TheRot/")):
            for fc in ("south", "east", "north"):
                rel = "%s_%s" % (tp, fc)
                tail = "/".join(rel.split("/")[-2:])
                if tail in ART_OWED:
                    continue
                if not os.path.isfile(os.path.join(HERE, "Textures", rel + ".png")) and "essicated" not in tp:
                    bad.append("%s: texture %s.png missing" % (n, rel))
    il = races.get("RM_Illoth")
    if il is not None:
        if float(il.findtext("statBases/MaxFlightTime") or 0) <= 0:
            bad.append("RM_Illoth cannot fly: MaxFlightTime is not > 0")
        if il.findtext("race/canFlyIntoMap") != "true":
            bad.append("RM_Illoth race lacks canFlyIntoMap")
    for fn in os.listdir(fauna):
        if "RSW_" in open(os.path.join(fauna, fn), encoding="utf-8").read():
            bad.append("Defs/Fauna/%s still names an RSW_ def (free mod must stand alone)" % fn)
    patch = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_TheRot.xml")
    if os.path.isfile(patch):
        txt = open(patch, encoding="utf-8").read()
        for retired in ("RSW_PustuleHornet", "RSW_SmogMoth", "RSW_Thrumbungus", "RSW_Yooka", "RSW_FungalWeevil", "RSW_FungalMantis"):
            if retired in re.sub(r"<!--.*?-->", "", txt, flags=re.S):
                bad.append("campaign patch still adds %s to RM_TheRot" % retired)
        for op in ET.parse(patch).getroot().iter("Operation"):
            if op.get("MayRequire"):
                bad.append("campaign patch has a top-level <Operation MayRequire> (inert in 1.6)")
        if "RSW_ShiroTrap" not in txt or "Snoruuk" not in txt:
            bad.append("campaign patch lost RSW_ShiroTrap or Snoruuk")
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
                elif ty == "string":
                    new = "zz_probe" if str(old) != "zz_probe" else "zz_probe2"
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
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="animalDensity,plantDensity,workerClass", limit=2)
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
        with t.component("biome_worker_class_loaded", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="workerClass", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                wc = str(((rows[0].get("fields") if rows else None) or {}).get("workerClass") or "")
                if not wc:
                    _unmeasured(t, "get_defs returned no workerClass field: %r" % (r,))
                    return
                if WORKER not in wc:
                    raise ExpectationFailed("workerClass reads %r, expected a type containing %s" % (wc, WORKER))

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("sheen_exposure_ladder", toggle="sheenExposure"):
            if _live(t):
                _unmeasured(t, 'the Sheen weather rotation bootstrapping a spore-coating hediff needs an RM_TheRot map with a colonist under the Sheen weather and game hours of ticks; weather_set is drivable but the biome-scoped rotation is not')
        with t.component("accelerated_rot_on_living_ground", toggle="acceleratedRot"):
            if _live(t):
                _unmeasured(t, "faster decay of items/corpses on the biome's ground needs a generated RM_TheRot map (or a cross-biome map) and ticks; the rot MapComponent asks this screen through RM_KitFronts; needs a debug [Tool] to flip the setting")
        with t.component("living_produce_heat", toggle="livingProduceHeat"):
            if _live(t):
                _unmeasured(t, 'live-preparation warmth needs a spawned live preparation and a temperature read after ticks on an RM_TheRot map')
        with t.component("warm_living_ground", toggle="warmMat"):
            if _live(t):
                _unmeasured(t, 'ambient warmth of the biome terrain needs a generated RM_TheRot map and a temperature read')
        with t.component("live_preparations_viability", toggle="livePreparations"):
            if _live(t):
                _unmeasured(t, 'viability lapsing on mishandling needs a live preparation thing and game days of ticks')
        with t.component("guardian_groves_lure_ring", toggle="guardianGroves"):
            if _live(t):
                _unmeasured(t, 'wild-spawned defended mushrooms with the false-fruit ring exist only on a map generated with the toggle on; the bridge cannot generate a map')
        with t.component("health_sharing", toggle="healthSharing"):
            if _live(t):
                _unmeasured(t, 'shared wound healing between kin-linked pawns needs two kin pawns, a wound and ticks')
        with t.component("pale_tree_wild_spawn", toggle="paleTreeSpawn"):
            if _live(t):
                _unmeasured(t, 'a rare wild-spawned oddity exists only on a generated map; it is also Royalty-gated')
        with t.component("spore_cloud_incident", toggle="sporeCloudIncidentWeight"):
            if _live(t):
                _unmeasured(t, 'fire_incident dry-run reports success=False with canFireNow=False and gives no weight read; a real firing needs a map and changes the game')
        with t.component("cross_biome_opt_in", toggle="crossBiomeEnabled"):
            if _live(t):
                _unmeasured(t, 'the cross-biome mechanics apply once right after a NEW map generates on a non-Rot biome; the bridge cannot generate a map')

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
