"""validation.py -- modcheck suite for RimMandrake: Nightside Ice (mandrake.rm.nightsideice).

First north-star script (NIGHTSIDE_ICE_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/NightsideIce.md.
The mod ships exactly one def: BiomeDef RM_NightsideIce, a deliberately near-empty dirty-ice biome (no plants, no liquid water,
Clear weather only, six imported landform animals at tiny commonality) plus a master-switch settings class that gates nothing yet.
Fold-aware: folded into mandrake.rm.biomes it is active under 'RimMandrake: Baroque Biomes'; every read is by def name.

CHAINS
  defs_resolve    BiomeDef/RM_NightsideIce (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip  the one `public static` field (masterEnabled) of RM_NightsideIceSettings: default / write / restore.
  biome_doctrine  the sheet's hard bans read back from the running biome: animalDensity > 0 (0 makes the roster dead content),
                  plantDensity 0, no rivers, roads allowed, no farming camps, extreme biome, worker BiomeWorker_IceSheet,
                  and Clear as the only weather with weight.
  biome_roster    jawa/biome_probe: no wild plants at all; every animal row present live carries the XML commonality; a
                  control name reads absent. Rows whose donor mod is not loaded on the tier are noted, never asserted.
  map_mechanics   a generated nightside-ice map (all-Ice terrain, no ponds, margin events): UNMEASURED.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.NightsideIce.RM_NightsideIceSettings"
BIOME = "RM_NightsideIce"
CONTROL_ABSENT = "BiomeDef/RM_NightsideIceNoSuchDef_ZZ"
CONTROL_ANIMAL = "RM_NightsideIceNoSuchCreature_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
BIOME_XML = os.path.join(HERE, "Defs", "BiomeDefs", "RM_NightsideIce.xml")


def shipped_defs():
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


def biome_node():
    return next(el for el in ET.parse(BIOME_XML).getroot() if el.findtext("defName") == BIOME)


def _kids(node, tag):
    el = node.find(tag)
    return list(el) if el is not None else []


def source_facts():
    """The biome as its own XML says it: scalars, wildAnimals {name: (commonality, mayRequire)}, weather {name: weight}."""
    b = biome_node()
    facts = {}
    for k in ("animalDensity", "plantDensity"):
        facts[k] = float(b.findtext(k))
    for k in ("allowRoads", "allowRivers", "allowFarmingCamps", "isExtremeBiome"):
        facts[k] = (b.findtext(k) or "").strip().lower() == "true"
    facts["workerClass"] = (b.findtext("workerClass") or "").strip()
    facts["animals"] = dict((c.tag, (float(c.text), c.get("MayRequire"))) for c in _kids(b, "wildAnimals") if isinstance(c.tag, str))
    facts["weather"] = dict((c.tag, float(c.text)) for c in _kids(b, "baseWeatherCommonalities") if isinstance(c.tag, str))
    facts["has_wild_plants"] = b.find("wildPlants") is not None
    return facts


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_NightsideIceMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_NightsideIceSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if (("BiomeDef", BIOME)) not in SHIPPED:
        return ["BiomeDef %s not parsed from Defs/ (sanity probe failed): %r" % (BIOME, SHIPPED[:3])]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_NightsideIceMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RM_NightsideIce.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    f = source_facts()
    if not f["animals"]:
        bad.append("no wildAnimals rows parsed (sanity probe failed)")
    if not f["animalDensity"] > 0:
        bad.append("animalDensity is 0: the roster is dead content")
    if f["plantDensity"] != 0 or f["has_wild_plants"]:
        bad.append("the sheet bans plants: plantDensity must be 0 and no wildPlants block")
    if f["allowRivers"]:
        bad.append("allowRivers true: the sheet bans liquid water")
    if not f["allowRoads"]:
        bad.append("allowRoads false: owner ruling 2026-09-07, every biome allows roads")
    if f["workerClass"] != "BiomeWorker_IceSheet":
        bad.append("workerClass is %r, not the vanilla BiomeWorker_IceSheet" % f["workerClass"])
    w = f["weather"]
    if not w or w.get("Clear", 0) <= 0 or [k for k, v in w.items() if k != "Clear" and v != 0]:
        bad.append("weather table is not Clear-only: %r" % w)
    if b_has(biome_node(), "terrainPatchMakers") or b_has(biome_node(), "fishTypes"):
        bad.append("terrainPatchMakers/fishTypes present: the sheet bans liquid water")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "NightsideIce.md")):
        bad.append("walk missing")
    return bad


def b_has(node, tag):
    return node.find(tag) is not None


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("NightsideIce")
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

    def _row(t, fields, deep=False):
        r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields=fields, limit=2, deep=deep)
        rows = (r or {}).get("defs") or []
        if not isinstance(r, dict) or r.get("success") is False or not rows:
            raise ExpectationFailed("could not read BiomeDef %s: %r" % (BIOME, r))
        return rows[0].get("fields") or {}

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
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%r of %d defs resolved; notFound=%r" % (r.get("foundCount"), len(names), r.get("notFound")))

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

    @suite.chain("biome_doctrine")
    def biome_doctrine(t):
        facts = source_facts()
        with t.component("flags_and_worker_match_the_sheet", beyond_toggle=True):
            if _live(t):
                f = _row(t, "animalDensity,plantDensity,allowRoads,allowRivers,allowFarmingCamps,isExtremeBiome,workerClass")
                try:
                    ad, pd = float(f.get("animalDensity")), float(f.get("plantDensity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs returned non-numeric densities: %r" % (f,))
                    return
                if not ad > 0:
                    raise ExpectationFailed("animalDensity %s: the six-animal roster would never spawn" % ad)
                if pd != 0:
                    raise ExpectationFailed("plantDensity %s: the sheet bans plants (no photosynthesis)" % pd)
                for k in ("allowRoads", "allowRivers", "allowFarmingCamps", "isExtremeBiome"):
                    if str(f.get(k)).lower() != str(facts[k]).lower():
                        raise ExpectationFailed("%s live %r != source %r" % (k, f.get(k), facts[k]))
                if facts["workerClass"] not in str(f.get("workerClass")):
                    raise ExpectationFailed("workerClass live %r != %s" % (f.get("workerClass"), facts["workerClass"]))
        with t.component("only_clear_weather_has_weight", beyond_toggle=True):
            if _live(t):
                f = _row(t, "baseWeatherCommonalities", deep=True)
                wl = f.get("baseWeatherCommonalities")
                pairs = {}
                if isinstance(wl, dict):
                    pairs = dict((str(k), v) for k, v in wl.items())
                elif isinstance(wl, list):
                    for item in wl:
                        if isinstance(item, dict):
                            vals = list(item.values())
                            if len(vals) == 2 and isinstance(vals[0], str):
                                pairs[vals[0]] = vals[1]
                        elif isinstance(item, (list, tuple)) and len(item) == 2:
                            pairs[str(item[0])] = item[1]
                if "Clear" not in pairs:
                    _unmeasured(t, "could not read (weather, commonality) pairs out of %s" % str(wl)[:200])
                    return
                try:
                    wet = dict((k, v) for k, v in pairs.items() if k != "Clear" and float(v or 0) != 0.0)
                except (TypeError, ValueError):
                    _unmeasured(t, "non-numeric weather weights: %s" % str(pairs)[:200])
                    return
                if wet or not float(pairs["Clear"]) > 0:
                    raise ExpectationFailed("the interior is Clear only (no precipitation, no wind), but live weights are %s" % pairs)

    @suite.chain("biome_roster")
    def biome_roster(t):
        facts = source_facts()
        box = {}
        with t.component("biome_probe_ready", beyond_toggle=True):
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True, topN=200, find=CONTROL_ANIMAL)
            if _live(t):
                rows = (r or {}).get("biomes") or []
                if not isinstance(r, dict) or r.get("success") is False or len(rows) != 1 or rows[0].get("defName") != BIOME:
                    raise ExpectationFailed("biome_probe did not return exactly %s: %s" % (BIOME, str(r)[:300]))
                row = rows[0]
                if row.get("wildAnimalCount") != row.get("animalsListed") or row.get("wildPlantCount") != row.get("plantsListed"):
                    raise ExpectationFailed("biome_probe lists were capped: %s" % str(row)[:300])
                box["row"] = row
                found = dict((f.get("defName"), f.get("state")) for f in (row.get("findResults") or []))
                if found.get(CONTROL_ANIMAL) != "absent":
                    raise ExpectationFailed("the probe cannot say absent for a control creature: %r" % found)
        with t.component("no_wild_plants", beyond_toggle=True):
            if _live(t) and box:
                n = box["row"].get("wildPlantCount")
                if n != 0:
                    raise ExpectationFailed("wildPlantCount %r: the sheet bans every plant on the ice" % n)
        with t.component("animal_rows_carry_source_commonality", beyond_toggle=True):
            if _live(t) and box:
                live = dict((a.get("defName"), a.get("commonality")) for a in (box["row"].get("animals") or []))
                skewed, absent = [], []
                for name, (c, req) in sorted(facts["animals"].items()):
                    if name in live:
                        if abs(float(live[name]) - c) > 1e-4:
                            skewed.append("%s live %s != source %s" % (name, live[name], c))
                    elif req is None:
                        absent.append(name)       # no donor gate: it must be there
                extra = sorted(n for n in live if n not in facts["animals"])
                gated_missing = sorted(n for n, (_c, req) in facts["animals"].items() if req and n not in live)
                if skewed or absent:
                    raise ExpectationFailed("roster drift: commonality %s; ungated rows missing %s" % (skewed, absent))
                if not live and not gated_missing:
                    raise ExpectationFailed("no animal rows live and none gated: the roster is empty")
                # rows from patches (Utinni layer) may be extra; they are not this mod's to fail

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("generated_map_is_all_ice_without_water", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "an all-Ice terrain map with no ponds and Clear-only weather exists only on a map GENERATED "
                               "as RM_NightsideIce; the bridge cannot generate a map")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
