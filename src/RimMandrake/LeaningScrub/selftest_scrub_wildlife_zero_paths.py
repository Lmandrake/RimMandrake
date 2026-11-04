#!/usr/bin/env python3
"""SCRUB_WILDLIFE_PROVE_NOBODY_CAME, offline half: every STATIC route by which a fresh RM_LeaningScrub map can be
generated with zero wild animals, measured closed from the sources on disk. The live half (a generated map) is
northstar/wildlife_mapgen_live.py.

The engine (RimWorld 1.6, decompiled WildAnimalSpawner / GenStep_Animals / TileTemperaturesComp):
  GenStep_Animals loops `while (!AnimalEcosystemFull)` and BREAKS on the first SpawnRandomWildAnimalAt that returns
  false, so ONE empty pick means zero animals of every kind. Two ways to get there:
  (a) DesiredAnimalDensity == 0  ->  AnimalEcosystemFull at once. It is
        tile.biome.animalDensity  x  every tile mutator's animalDensityFactor
        x  (commonality of the season-acceptable roster / commonality of the whole roster)
        x  gameConditionManager.AggregateAnimalDensityFactor  x  (Biotech) pollution curve (>= 0.25, never 0)
  (b) the first pick finds no kind: BiomeAt(loc).AllWildAnimals filtered by SeasonAcceptableFor(race)
        (ComfyTemperatureMin < seasonal temp < ComfyTemperatureMax, buffer 0), weighted by CommonalityOfAnimalNow,
        which a Harmony postfix or a tile mutator can zero.
  Seasonal temp = tile.temperature - cos(2 pi (yearPct - winterMid)) x A,  A = SeasonalTempVariationCurve(|lat|/90)
  with the curve (0, 3) (0.1, 4) (1, 28) (Verse.TemperatureTuning).

Checks (each a route; a red names it):
  Z1 density   the BiomeDef's animalDensity > 0
  Z2 roster    every inline wildAnimals row (and every site NATIVE) resolves to a PawnKindDef and its race ThingDef in a
               source folder that Biomes.compose.json composes into mandrake.rm.biomes (or the row's MayRequire names it)
  Z3 season   the open comfy bands of the natives cover EVERY temperature in [t0 - A(LAT_MAX), t0 + A(LAT_MAX)] at
               site_spec.TILE (decided exactly at the band endpoints, not sampled), so route (a)'s share and route (b)'s
               filter stay > 0 all year at every |lat| <= LAT_MAX
  Z4 patches   no XML patch under src/ can remove or re-value the Scrub's life: on RM_LeaningScrub only Add /
               AddModExtension; any other op reaching a BiomeDef (or a whole def through a wildcard) must name exactly
               one other biome by defName equality with no or/|/comparison/function widening it; a patch writing a
               native's comfy band must keep Min < t0 - A and Max > t0 + A
  Z5 code      every C# file under src/ that targets the spawner (typeof/nameof however qualified, member names as
               strings), edits BiomeDef rosters by reflection, writes animalDensity or a density factor is on the
               reviewed list below WITH its fingerprint (whole file; a matched window for big bridge/dump files), and
               names neither RM_LeaningScrub nor a native; a new or changed file is red until someone re-reads it
"""
import glob
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
RM = os.path.join(SRC, "RimMandrake")
BIOME = "RM_LeaningScrub"
BIOME_XML = os.path.join(HERE, "Defs", "BiomeDefs", "RM_LeaningScrub_Biome.xml")
FAILS = []
INFO = {}


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s: %s" % (name, str(detail)[:400]))


def load_spec():
    import importlib.util
    sp = importlib.util.spec_from_file_location("scrub_site_spec_zero", os.path.join(HERE, "site_spec.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def parse(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None


# ---- defs under the composed folders -------------------------------------------------------------------------------
with open(os.path.join(RM, "Biomes.compose.json"), encoding="utf-8") as fh:
    _COMPOSE = json.load(fh)
_WAVE = _COMPOSE.get("compose_wave", 0)
COMPOSED = sorted(e["key"] for e in _COMPOSE.get("entries", ()) if e.get("wave", 99) <= _WAVE)

PAWNKINDS, THINGDEFS = {}, {}        # defName -> (composed key, element)
for key in COMPOSED:
    for path in glob.glob(os.path.join(RM, key, "Defs", "**", "*.xml"), recursive=True):
        root = parse(path)
        if root is None:
            continue
        for d in root:
            n = d.findtext("defName")
            if d.tag == "PawnKindDef" and n:
                PAWNKINDS.setdefault(n, (key, d))
            elif d.tag == "ThingDef":
                if n:
                    THINGDEFS.setdefault(n, (key, d))
                if d.get("Name"):
                    THINGDEFS.setdefault("@" + d.get("Name"), (key, d))

biome_root = parse(BIOME_XML)
bdef = None if biome_root is None else next((b for b in biome_root.iter("BiomeDef") if b.findtext("defName") == BIOME),
                                            None)
check("Z0 biome def", bdef is not None, BIOME_XML)
if bdef is None:
    print("FAIL\n  " + "\n  ".join(FAILS))
    sys.exit(1)

# Z1 ---------------------------------------------------------------------------------------------------------------
dens = float(bdef.findtext("animalDensity") or 0)
INFO["animalDensity"] = dens
check("Z1 density", dens > 0, "animalDensity %s: DesiredAnimalDensity is 0 on every map" % dens)

# Z2 ---------------------------------------------------------------------------------------------------------------
check("Z2 composed", "LeaningScrub" in COMPOSED, "LeaningScrub is not composed into mandrake.rm.biomes: %s" % COMPOSED)
rows = [(c.tag, float(c.text or 0), c.get("MayRequire")) for c in (bdef.find("wildAnimals") if bdef.find("wildAnimals") is not None else [])]
INFO["rows"] = len(rows)
check("Z2 rows", rows and all(w > 0 for _, w, _ in rows), rows)
_OK_REQ = ("", "mandrake.rm.biomes")
_wa = bdef.find("wildAnimals")
check("Z2 gates", (bdef.get("MayRequire") or "").lower() in _OK_REQ
      and ((_wa.get("MayRequire") if _wa is not None else None) or "").lower() in _OK_REQ,
      "the BiomeDef or its wildAnimals container is MayRequire-gated (%s / %s)" % (
          bdef.get("MayRequire"), _wa.get("MayRequire") if _wa is not None else None))
spec = load_spec()
races = {}
for kind, w, may in rows:
    pk = PAWNKINDS.get(kind)
    if may and may.lower() not in ("mandrake.rm.biomes",):
        continue                                  # a row gated on another mod is not a route to the natives
    check("Z2 kind %s" % kind, pk is not None, "no PawnKindDef %s in a composed folder" % kind)
    if pk is None:
        continue
    check("Z2 gate %s" % kind, (pk[1].get("MayRequire") or "").lower() in _OK_REQ, pk[1].get("MayRequire"))
    race = pk[1].findtext("race")
    td = THINGDEFS.get(race)
    check("Z2 race %s" % kind, td is not None, "race %s of %s has no ThingDef in a composed folder" % (race, kind))
    if td is not None:
        check("Z2 race gate %s" % kind, (td[1].get("MayRequire") or "").lower() in _OK_REQ, td[1].get("MayRequire"))
        races[kind] = td[1]
for n in spec.NATIVES:
    check("Z2 native %s" % n, n in races, "site NATIVE %s is not a resolvable inline row" % n)


def stat(el, name, depth=0):
    """statBases value, following ParentName through composed ThingDefs (Core parents carry no comfy band)."""
    if el is None or depth > 8:
        return None
    v = el.findtext("statBases/" + name)
    if v is not None:
        return float(v)
    sb = el.find("statBases")
    if sb is not None and (sb.get("Inherit") or "").lower() == "false":
        return None                               # the game discards the parent's statBases here
    p = el.get("ParentName")
    return stat(THINGDEFS.get("@" + p, (None, None))[1], name, depth + 1) if p else None


# Z3 ---------------------------------------------------------------------------------------------------------------
def amplitude(abs_lat):
    x = abs_lat / 90.0
    pts = [(0.0, 3.0), (0.1, 4.0), (1.0, 28.0)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (max(x, x0) - x0) / (x1 - x0)
    return pts[-1][1]


bands = {}
for n in spec.NATIVES:
    lo, hi = stat(races.get(n), "ComfyTemperatureMin"), stat(races.get(n), "ComfyTemperatureMax")
    if lo is not None and hi is not None:
        bands[n] = (lo, hi)
check("Z3 bands", bands, "no native carries an explicit comfy band; the season gate cannot be measured")
t0 = float(spec.TILE["temperature"])
# Seasonal temp sweeps the CLOSED interval [t0 - A, t0 + A] (A grows with |lat|, so LAT_MAX's interval holds every
# lower latitude's). Bands are OPEN (lo < T < hi), so coverage is decided exactly at the critical points: the interval
# ends, every band endpoint inside it, and the midpoint between each consecutive pair. No sampling gap can hide a hole.
lo_t, hi_t = t0 - amplitude(spec.LAT_MAX), t0 + amplitude(spec.LAT_MAX)
crit = sorted({lo_t, hi_t} | {e for b in bands.values() for e in b if lo_t <= e <= hi_t})
probe = crit + [(a + b) / 2.0 for a, b in zip(crit, crit[1:])]
worst = min(((sum(1 for lo, hi in bands.values() if lo < x < hi), round(x, 3)) for x in probe),
            default=(0, None))
INFO["season"] = {"natives_with_band": len(bands), "min_acceptable": worst[0], "at_temp": worst[1],
                  "range": [round(lo_t, 2), round(hi_t, 2)], "points": len(probe)}
check("Z3 season", worst[0] >= 1, "no native is season-acceptable at %s C (range %.2f..%.2f)" % (worst[1], lo_t, hi_t))

# Z4 ---------------------------------------------------------------------------------------------------------------
# An op on BiomeDef is SAFE only when it is a guard (Conditional/Test/FindMod), an Add (row or mod extension), or scoped by an EQUALITY
# defName to a biome other than RM_LeaningScrub. Anything else that can reach a BiomeDef is red: an unscoped or
# negated/contains() selector, or any non-Add op on RM_LeaningScrub itself (whole-def Replace/Remove included).
ADDS = ("PatchOperationAdd", "PatchOperationAddModExtension")   # add a row / an extension: never removes life
GUARDS = ("PatchOperationConditional", "PatchOperationTest", "PatchOperationFindMod", "PatchOperationSequence")
NATIVE_RX = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(x) for x in spec.NATIVES))
EQ_RX = re.compile(r"""defName\s*=\s*["']([^"']+)["']""")
# The widen-only selector FaunaNorm_Law5_Tolerance.xml generates: ONE named def's band value, with a numeric comparison
# that can only shrink what the selector reaches. Stripped before the scope tests; the value it writes is still judged.
BAND_PRED_RX = re.compile(r'^(/?Defs/ThingDef\[defName="[^"]+"\]/statBases/(ComfyTemperature(?:Min|Max)))'
                          r'\[number\(\.\)\s*[<>]\s*-?\d+(?:\.\d+)?\]$')


def band_scope(xpath):
    """The xpath with a widen-only numeric predicate removed; any other shape comes back unchanged."""
    m = BAND_PRED_RX.match(xpath)
    return m.group(1) if m else xpath


def band_value_bad(val, xpath):
    """What a band patch's <value> breaks: a value outside the seasonal range, or no value for the band it selects
    (a Replace with an empty value deletes the band)."""
    bad = []
    for el in (val.iter() if val is not None else ()):
        try:
            v = float(el.text)
        except (TypeError, ValueError):
            continue
        if (el.tag == "ComfyTemperatureMin" and not v < lo_t) or (el.tag == "ComfyTemperatureMax" and not v > hi_t):
            bad.append("%s=%s" % (el.tag, v))
    selected = re.search(r"ComfyTemperature(?:Min|Max)$", xpath)
    if selected and val is not None and val.find(selected.group(0)) is None:
        bad.append("no %s written" % selected.group(0))
    return bad


_B = '/Defs/ThingDef[defName="RM_Vurra"]/statBases/ComfyTemperatureMax'
check("Z4 form strips widen-only", band_scope(_B + "[number(.) < 61.9]") == _B, band_scope(_B + "[number(.) < 61.9]"))
for _x in (_B + "[number(.) < 61.9 or true()]", _B + "[. < 61.9]",
           '/Defs/ThingDef[defName="RM_Vurra" or defName="RM_Chikka"]/statBases/ComfyTemperatureMax[number(.) < 61.9]',
           '/Defs/ThingDef[defName="RM_Vurra"]/statBases[number(.) < 61.9]',
           '/Defs/*[defName="RM_Vurra"]/statBases/ComfyTemperatureMax[number(.) < 61.9]'):
    check("Z4 form keeps %s" % _x, band_scope(_x) == _x, band_scope(_x))
_v = lambda body: ET.fromstring("<value>%s</value>" % body)
check("Z4 value keeps a wide band", not band_value_bad(_v("<ComfyTemperatureMax>%s</ComfyTemperatureMax>" % (hi_t + 1)), _B))
check("Z4 value red on a narrow band", band_value_bad(_v("<ComfyTemperatureMax>%s</ComfyTemperatureMax>" % (hi_t - 1)), _B))
check("Z4 value red on no band", band_value_bad(_v(""), _B))
check("Z4 value red on the other band", band_value_bad(_v("<ComfyTemperatureMin>-50</ComfyTemperatureMin>"), _B))

patch_hits, patch_seen, comfy_ok = [], 0, 0
for path in glob.glob(os.path.join(SRC, "**", "Patches", "**", "*.xml"), recursive=True):
    root = parse(path)
    if root is None:
        continue
    parents = {c: p for p in root.iter() for c in p}
    for xp in root.iter("xpath"):
        text = (xp.text or "").strip()
        op = parents.get(xp)
        cls = (op.get("Class") if op is not None else "") or ""
        # Could this selector reach the Scrub's life? It names a BiomeDef, a roster/density field or the Scrub; or it
        # is a wildcard selecting WHOLE defs (Defs/*[...], //*[...]), which a Replace/Remove could hit the biome with;
        # or it edits a comfy band (the season gate) on a native or on an unnamed set of defs; or it names a native.
        whole = re.match(r"^/?/?(?:Defs/)?(?:\*|node\(\))(?:\[.*\])?$", text)
        _val = op.find("value") if op is not None else None
        _vtext = ET.tostring(_val, encoding="unicode") if _val is not None else ""
        comfy = ("ComfyTemperature" in text or "ComfyTemperature" in _vtext) and (
            NATIVE_RX.search(text) or len(EQ_RX.findall(text)) != 1)
        if re.search(r"genSteps|GenStepDef|MapGeneratorDef", text) and "Animals" in (text + _vtext) \
                and cls not in ADDS + GUARDS:
            patch_hits.append("%s: %s on the Animals genstep %s" % (os.path.relpath(path, ROOT), cls, text))
            continue
        if not (re.search(r"BiomeDef|wildAnimals|animalDensity|%s" % BIOME, text) or whole or comfy
                or NATIVE_RX.search(text)):
            continue
        rel = os.path.relpath(path, ROOT)
        patch_seen += BIOME in text
        if cls in GUARDS:
            continue
        names = EQ_RX.findall(text)
        # Safe scope = exactly one defName equality and nothing that widens it (or, |, comparisons, functions).
        scope = band_scope(text)
        risky = re.search(r"!=|\bor\b|\||[<>]|\(|\.\.|::|\w//|\]//", scope.replace("text()", "").replace("[", " [")) \
            or len(names) != 1
        if NATIVE_RX.search(text) and cls not in ADDS and not re.search(r"ComfyTemperature(?:Min|Max)$", scope) and (
                re.search(r"(?:statBases|race|\])$", scope) or re.search(r"/statBases/?$|/race(?:/|$)", scope)):
            patch_hits.append("%s: %s on a native's def/statBases/race %s" % (rel, cls, text))
            continue
        if comfy and NATIVE_RX.search(text) and not risky:
            # A band patch on ONE named native is safe when every value it writes keeps that band around the whole
            # seasonal range: each ComfyTemperatureMin < lo_t and each ComfyTemperatureMax > hi_t.
            val = op.find("value") if op is not None else None
            bad = band_value_bad(val, scope)
            if cls not in ADDS + ("PatchOperationReplace",) or val is None or bad:
                patch_hits.append("%s: %s on %s narrows the band %s" % (rel, cls, text, bad or "(no value)"))
            comfy_ok += 1
            continue
        if BIOME in text or comfy:
            if cls not in ADDS or risky or comfy:
                patch_hits.append("%s: %s on %s" % (rel, cls, text))
        elif cls not in ADDS and risky:
            patch_hits.append("%s: unscoped %s %s" % (rel, cls, text))
INFO["patch_hits"], INFO["patch_xpaths_on_scrub"], INFO["native_band_patches"] = len(patch_hits), patch_seen, comfy_ok
check("Z4 sanity", patch_seen >= 1, "the patch scan saw no xpath on %s (WildAnimals_LeaningScrub.xml adds one); the "
      "instrument is blind" % BIOME)
check("Z4 patches", not patch_hits, patch_hits)

# Z5 ---------------------------------------------------------------------------------------------------------------
# path under src/ -> (fingerprint, why it cannot touch RM_LeaningScrub). The fingerprint pins the REVIEWED behaviour:
# sha256 of the WHOLE file (a guard a few lines below the match decides behaviour), except the WINDOWED files: big
# multi-purpose bridge/dump sources where only the lines matching CODE_RX +- WINDOW are pinned. Any change turns Z5 red
# until someone re-reads the file and records the new value (`--fingerprints` prints them). Reviewed 2026-11-02, this item; Warscar and
# TheRot re-read 2026-11-03 (NIGHTLY_COP_FIX_RED_NZZZPC_NAFD: hospice settings and a label; their roster code untouched).
# STATED LIMIT: a WINDOWED file's change outside its windows is not seen (GPT round 4); those four are bridge-tool and
# dump sources that act only when a tool is called, and the live A1 census is the arbiter of a real map in any case.
REVIEWED = {
    "RimMandrake/DivingInteraction/Source/RM_SeabedFloorLife.cs": ("9cce7eeb04e30fd4", "copies a SEA biome's life onto the floor "
        "biome its RM_SeabedAccessExtension names; only biomes carrying RM_SeabedFloorExtension"),
    "RimMandrake/DivingInteraction/Source/RM_SeabedSiteParent.cs": ("825f5ab206a4c090", "seabed site parent's own density field"),
    "RimMandrake/EnvironmentalHazards/Source/EnvironmentalWeatherExtension.cs": ("d8b94d476938224f", "field default 1; "
        "per-condition data"),
    "RimMandrake/EnvironmentalHazards/Source/GameCondition_EnvironmentalWeather.cs": ("13bdd45ce825d1c3", "returns its own def's "
        "factor while that condition runs on a map; no shipped def sets 0"),
    "RimMandrake/GelatinousSlime/Source/Titanoslime.cs": ("32d50651a8e0d2c2", "scales only rows whose animal is the titanoslime kind"),
    "RimMandrake/Greentide/Source/RM_GreentideMod.cs": ("cfe46921dad09e0e", "RM_Greentide only, removes RM_Krannock"),
    "RimMandrake/Pyrelands/Source/RM_PyrelandsGiants.cs": ("a243636a2b2fc529", "RM_Pyrelands only"),
    "RimMandrake/RimDefDump/Source/DefDumper.cs": ("2e01cc23efd3d815", "reads rosters for the dump; writes none"),
    "RimMandrake/Scarlands/Source/Kernel/RM_TetchikGateKernel.cs": ("8fece90db54fd50a", "pure gate arithmetic, comment names the "
        "method"),
    "RimMandrake/Scarlands/Source/RM_WarscarMod.cs": ("04432e3fd8a690cf", "RM_Warscar only, settings-off species"),
    "RimMandrake/Scarlands/Source/RM_WarscarPatches.cs": ("e6a09668741b753e", "CommonalityOfAnimalNow postfix returns at once unless "
        "def is RM_Tetchik"),
    "RimMandrake/TheRot/Source/RM_TheRotMod.cs": ("b4be10c77fcee8f0", "RM_TheRot only, removes RM_Hwelgrue"),
    "RimMandrake/TheSump/Source/RM_KethrelStartup.cs": ("4ad9eba0dbfbf322", "RM_TheSump only, RM_Kethrel rows"),
    "RimMandrake/TileFeatures/Source/RM_TileFeatureApplier.cs": ("480a08ceb14ac4ec", "snapshots/restores TileMutatorDef factors; "
        "site maps have their centre's mutators stripped"),
    "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs": ("6323efc20e495e92", "a bridge tool, acts only when "
        "called"),
    "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTypeInspect.cs": ("edbaedba90fa9862", "comment only"),
    "RimStarWars/SWBestiary/Source/BeastMechanics/RSW_DragonsnakeAlbinoToggle.cs": ("d489359cdee8630a", "removes only the albino "
        "dragonsnake kind from every roster"),
    "RimMandrake/bridgetools/AwarenessSelfTest/Program.cs": ("18152ad6f3d988a1", "offline test of the awareness scope stack; names "
        "the method as a label"),
    "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchAwareness.cs": ("04a0939651ceb996", "void (non-skipping) context prefix on "
        "SpawnRandomWildAnimalAt; the wild-spawner block patches only WildAnimalSpawnerTick (ongoing arrivals, never "
        "mapgen) and only when a tool asks"),
}
_LIFE = (r"(?:CommonalityOfAnimal|CommonalityOfPollutionAnimal|CommonalityOfAnimalNow|SeasonAcceptableFor|AllWildAnimals"
         r"|SpawnRandomWildAnimalAt|AnimalEcosystemFull|DesiredAnimalDensity|DesiredTotalAnimalWeight"
         r"|CurrentTotalAnimalWeight|WildAnimalSpawnerTick|RandomAnimalSpawnCell_MapGen)")
# Patch/reflection TARGET forms only (reads like map.wildAnimalSpawner.AnimalEcosystemFull are not routes): roster fields
# by name, density writes, typeof/nameof of the spawner types however qualified, and life members named as strings or
# through nameof.
CODE_RX = re.compile(r'"(?:wildAnimals|coastalWildAnimals|pollutionWildAnimals|cachedAnimalCommonalities|animalDensity)"'
                     r'|AnimalDensityFactor|animalDensityFactor'
                     r'|\banimalDensity\s*[-+*/]?=(?!=)'
                     r'|\b(?:typeof|nameof)\s*\(\s*(?:[\w.]+\.)?(?:WildAnimalSpawner|GenStep_Animals)\b'
                     r'|\bnameof\s*\([^)]*\banimalDensity\b'
                     r'|"(?:[\w.]+\.)?(?:WildAnimalSpawner|GenStep_Animals)[:"]'
                     r'|"' + _LIFE + r'"|\bnameof\s*\([^)]*\b' + _LIFE + r'\b|\bCommonalityOfAnimalNow\b')
WINDOW = 3
NAMES_RX = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(x) for x in (BIOME,) + tuple(spec.NATIVES)))


WINDOWED = {"RimMandrake/RimDefDump/Source/DefDumper.cs",
            "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs",
            "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTypeInspect.cs",
            "RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchAwareness.cs"}


def fingerprint(body, rel=None):
    import hashlib
    lines = body.splitlines()
    if rel not in WINDOWED:
        return hashlib.sha256("\n".join(ln.rstrip() for ln in lines).encode("utf-8")).hexdigest()[:16]
    keep = sorted({j for i, ln in enumerate(lines) if CODE_RX.search(ln)
                   for j in range(max(0, i - WINDOW), min(len(lines), i + WINDOW + 1))})
    return hashlib.sha256("\n".join(lines[j].strip() for j in keep).encode("utf-8")).hexdigest()[:16]


code_hits, seen, prints = [], set(), {}
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    rel = os.path.relpath(path, SRC).replace(os.sep, "/")
    if "/obj/" in rel or "/bin/" in rel:
        continue
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            body = fh.read()
    except OSError:
        continue
    if not CODE_RX.search(body):
        continue
    seen.add(rel)
    prints[rel] = fingerprint(body, rel)
    if rel not in REVIEWED:
        code_hits.append("unreviewed %s (read it; add it with its fingerprint %s)" % (rel, prints[rel]))
    elif REVIEWED[rel][0] != prints[rel]:
        code_hits.append("%s changed since review (fingerprint %s, reviewed %s): re-read it" % (
            rel, prints[rel], REVIEWED[rel][0]))
    elif NAMES_RX.search(body):
        code_hits.append("%s names %s" % (rel, NAMES_RX.search(body).group(0)))
if "--fingerprints" in sys.argv:
    print(json.dumps(prints, indent=1, sort_keys=True))
    sys.exit(0)
INFO["code_files"] = len(seen)
check("Z5 code", not code_hits, code_hits)
check("Z5 sanity", len(seen) >= 5, "the code scan saw %d files; the instrument is blind" % len(seen))
stale = sorted(set(REVIEWED) - seen)
check("Z5 stale list", not stale, "reviewed entries no longer matching (drop them): %s" % stale)

# L: the live A1 script's pure half (northstar/wildlife_mapgen_live.py) on list_pawns rows of the real shape ---------
sys.path.insert(0, os.path.join(HERE, "northstar"))
import wildlife_mapgen_live as L  # noqa: E402
_A = {"faction": None, "isPlayer": False, "dead": False, "isMechanoid": False, "intelligence": "Animal"}
_rows = [dict(_A, kind="RM_Vurra"),
         dict(_A, kind="RM_Vurra", dead=True),
         dict(_A, kind="Colonist", faction="PlayerColony", isPlayer=True, intelligence="Humanlike"),
         dict(_A, kind="Drifter", intelligence="Humanlike"),
         dict(_A, kind="Tribal", intelligence="ToolUser"),
         dict(_A, kind="Mech", isMechanoid=True, intelligence="ToolUser"),
         dict(_A, kind="Tame", faction="PlayerColony", isPlayer=True),
         {}, {"kind": "NoFields"}, dict(_A, kind="NoDead", dead=None), dict(_A, kind=None)]
check("L wild_rows", L.wild_rows(_rows) == ["RM_Vurra"], L.wild_rows(_rows))
# the REAL row shape (list_pawns, live 2026-11-02, a wild RM_Durrok): no faction key at all
_live = {"id": "RM_Durrok37089", "name": "Durrok", "kind": "RM_Durrok", "kindDef": "RM_Durrok", "def": "RM_Durrok",
         "hasGenes": False, "uniqueXenotype": False, "isPlayer": False, "hostile": False, "x": 77, "z": 221,
         "spawned": True, "dead": False, "downed": False, "stunned": False, "stunTicksLeft": 0, "fleshType": "Normal",
         "isMechanoid": False, "isFlesh": True, "intelligence": "Animal", "bodySize": 1.4}
check("L wild_rows live shape", L.wild_rows([_live]) == ["RM_Durrok"], L.wild_rows([_live]))
check("L wild_rows owned live shape", L.wild_rows([dict(_live, faction="PlayerColony", factionName="x")]) == [])
check("L wild_rows factionName only", L.wild_rows([dict(_live, factionName="Pirates")]) == [])
check("L verdict blind count", L.verdict(0, {"RM_Fuzzrunner": 6}, 1, {})[0] is False and
      "blind" in L.verdict(0, {"RM_Fuzzrunner": 6}, 1, {})[1])
check("L wild_rows empty", L.wild_rows([]) == [] and L.wild_rows(None) == [])
check("L verdict pass", L.verdict(20, {"RM_Vurra": 3}, 1, {})[0] is True)
check("L verdict zero wild", L.verdict(0, {"RM_Vurra": 0}, 1, {"tileInfo": {"pollution": 1.0}})[0] is False)
check("L verdict names inputs", "pollution" in L.verdict(0, {}, 1, {"tileInfo": {"pollution": 1.0}})[1])
check("L verdict natives short", L.verdict(5, {"RM_Vurra": 0}, 1, {})[0] is False)

print(json.dumps(INFO, sort_keys=True))
if FAILS:
    print("FAIL (%d)\n  %s" % (len(FAILS), "\n  ".join(FAILS)))
    sys.exit(1)
print("PASS: no static route zeroes %s's wildlife (Z1-Z5)" % BIOME)
