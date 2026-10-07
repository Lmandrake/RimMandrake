"""validation.py -- modcheck suite for RimMandrake: The Forge (mandrake.rm.theforge).

First north-star script (THE_FORGE_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TheForge.md
(`## must be true`, agent-owned, not hashed; every line ends in an arrow to the component below that covers it).
Process: design/RimMandrake/debug_process.md section 2. Never deployed (deploy_custom_mods.py excludes `.py`).

PACKAGING. This dev folder is SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json), so a run loads the existing `baroque_wave0` tier (BRIDGE + mandrake.rm.biomes + its
dependencies Alpha Biomes / FlowWorks / Luminous Pigment + the five DLCs) and `northstar_plan.py` expects
`mandrake.rm.biomes` active. `modcheck run TheForge` appends the dev folder's own packageId and lands on a list
without the biome: drive `northstar_driver/cli.py run --mod TheForge --plan <northstar_plan.py>`.

WHAT THE MOD IS FOR (every line is sourced; see the walk): `RM_TheForge`, a biome whose map carries one
GameCondition, `RM_ForgePulse` = `RM_GameCondition_ForgeCycle`, the six-phase fire-and-water GRAND CYCLE
(still heat -> gas wash -> boiling rain + floods -> freeze (lava crusts into temporary basalt/pumice on the 1.6
temp-terrain layer) -> growth (floatstone gardens bloom on the crust) -> glowing cracks -> melt-back that burns what
stands on the crust). Around it: four dormancy natives that keep the mountain's clock (dhokkur, julmox, dhuvvox
seal and wake with the cycle; the dhuvvox also run a visible countdown), the floatstone economy (harvest, spunstone
bonding research hidden until studied, gravship keel braces, the floatstone door and spunstone hull it also unlocks),
the four phase voices, and the Mod Settings (count derived from the C# source, never written here).

HOW THE CYCLE IS DRIVEN AND READ. A real cycle is ~5 in-game days, so this suite steps it with the mod's OWN
`RMTheForge` debug actions (`Forge cycle: advance one phase`, `Forge cycle: report state`, the `Spunstone:`
pair), found by reading the live Actions tree, exactly like the Deepfire suite. The report line is a state read of
the condition's own fields and counters; every phase effect is ALSO read back through an independent bridge tool
(terrain layers, list_things, list_pawns, letter_list, weather_get, inspect_string, research_availability), so a
counter that lies cannot green a phase. No tagged log line is UNMEASURED, never PASS (RimWorld stops logging after
10,000 messages: Transient/bridge_debugaction_noop_report.md).

SETTINGS. `RM_TheForgeSettings` fields are `public static`. `jawa/mod_settings_field` writes the static (read live
by every feature, so a flip takes effect at once) but never calls WriteSettings. Only the keelwork toggle needs
WriteSettings (RM_KeelworkUtility.ApplySetting rewrites the brace's fuelSavingsPercent); that arm opens and
closes the Mod Settings dialog and records UNMEASURED, never PASS, if the dialog does not reach it. Every arm
restores its fields in a `finally` through the raw session (`t.set_setting` is a no-op after a failed chain).
The shared EnvironmentalHazards `environmentalDamageEnabled` is switched OFF for the long Rain windows so the start
colonists are not scalded to death on a quicktest map, and restored after.

DERIVED FROM THE MOD, never a hand list: def groups (Defs/ XML), the biome roster (BiomeDef XML), the Mod Settings
fields and shipped defaults (RM_TheForgeSettings in RM_TheForgeMod.cs), the phase names (enum ForgeCyclePhase), the
plants' maxMeshCount. Floors (GROUPS) stop a parse failure reading as "nothing to check".

NOT measurable with the existing bridge tools (named in the walk, never faked here): the sounds themselves (audio),
the sealed/dormant LOOK (visual), flyer flight (state read only, never unattended live), the real gravship fuel
number (needs a built gravship), the autonomous study loop, the biome worker's score (inert on a hand-painted
world), FORGE_MECHANICS_1's still-scaffolding settings (declared, change nothing).

Every bridge call uses only parameters the live tool declares (lint_calls.py). Result shapes MEASURED live
elsewhere: jawa/get_defs -> foundCount/notFound/defs[].fields; jawa/biome_probe -> biomes[].animals/plants/
findResults; jawa/list_things -> countMatched/isCompleteList/things[].id; jawa/list_pawns -> pawns[].id/kindDef;
jawa/weather_get -> weather.current, conditions[].def/affectsThisMap; jawa/letter_list -> letters[].label;
jawa/inspect_string -> things[].id/inspect[]; execute_debug_action -> effects.logs[].message. UNPROVEN until the
first live run: get_defs serialising comps/modExtensions/terrainPatchMakers under deep, the research
availability key `isHidden`, list_pawns' health block key names for a hediff row, list_messages' row keys, and
get_cell_info's walkability key. A component that cannot read a shape it needs records UNMEASURED (`_unmeasured`).
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("TheForge")

SETTINGS = "RimMandrake.TheForge.RM_TheForgeSettings"
HAZ_SETTINGS = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
# LIVE 2026-10-03: the composed mod registers ~30 settings surfaces under ONE packageId, so open_mod_settings(modId=
# "mandrake.rm.biomes") is refused as "matched multiple loaded mods". The surface is addressed by its handle class
# name (or label "The Forge"): this resolves to exactly one surface.
DIALOG_QUERY = "RM_TheForgeMod"
MOD_ID = "mandrake.rm.biomes"        # the composed mod hosting RM_TheForgeMod: what the settings dialog is keyed by
BIOME = "RM_TheForge"
COND = "RM_ForgePulse"
OUR_PACKAGES = ("mandrake.rm.biomes", "mandrake.rm.theforge")
ACTIVE_ON_TIER = ("Ludeon.RimWorld", "Ludeon.RimWorld.Odyssey", "Ludeon.RimWorld.Biotech",
                  "Ludeon.RimWorld.Ideology", "Ludeon.RimWorld.Royalty", "Ludeon.RimWorld.Anomaly",
                  "mandrake.rm.biomes", "mandrake.rm.flowworks", "mandrake.rm.luminouspigment", "sarg.alphabiomes")
TAG = "[RMTheForgeDebug]"
STILL_PHRASE = "sealed, waiting out the dry"
RUN_PHRASE = "run ends in"

LAVA = 12                  # the LavaDeep square the cycle freezes: LAVA x LAVA cells at the chain anchor
PAD_OFFSET = 30            # the pad sits this far from the map centre, clear of the start colonists
SOIL_DX = 18               # the creature yard (plain soil) starts this far east of the lava square
YARD = 10
MESH_OK = (1, 4, 9, 16, 25)  # RimWorld/Plant.cs: any other maxMeshCount logs an error per mesh print

# ----------------------------------------------------------------------- source parse (import time)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DIR = os.path.join(_HERE, "Defs")
_SRC = os.path.join(_HERE, "Source")
_ERRORS = []


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except Exception as ex:                       # a def file that does not parse is itself a finding
        _ERRORS.append("%s: %s" % (os.path.basename(path), ex))
        return None


def _defs_in(subdir):
    """[(DefType, defName, element)] for every non-abstract def under Defs/<subdir>."""
    rows = []
    d = os.path.join(_DIR, subdir)
    if not os.path.isdir(d):
        _ERRORS.append("missing Defs/%s" % subdir)
        return rows
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".xml"):
            continue
        root = _parse(os.path.join(d, fn))
        if root is None:
            continue
        for el in root:
            if not isinstance(el.tag, str) or el.get("Abstract", "").lower() == "true":
                continue
            nm = (el.findtext("defName") or "").strip()
            if nm:
                rows.append((el.tag, nm, el))
    return rows


_BY_DIR = dict((d, _defs_in(d)) for d in (
    "BiomeDefs", "GameConditionDefs", "HediffDefs", "PawnRenderTreeDefs", "ResearchProjectDefs", "SoundDefs",
    "TerrainDefs", "ThingDefs_Buildings", "ThingDefs_Items", "ThingDefs_Plants", "ThingDefs_Races", "WeatherDefs"))


def _names(subdir, deftype):
    return [n for t, n, _ in _BY_DIR[subdir] if t == deftype]


# (group, DefType, names, floor). The floor is the count at authoring (2026-10-01): a shrink must be a deliberate
# edit of this script, never a silent pass.
GROUPS = [
    ("races", "ThingDef", _names("ThingDefs_Races", "ThingDef"), 5),
    ("pawnkinds", "PawnKindDef", _names("ThingDefs_Races", "PawnKindDef"), 5),
    ("plants", "ThingDef", _names("ThingDefs_Plants", "ThingDef"), 4),
    ("items", "ThingDef", _names("ThingDefs_Items", "ThingDef"), 2),
    ("buildings", "ThingDef", _names("ThingDefs_Buildings", "ThingDef"), 1),
    ("terrain", "TerrainDef", _names("TerrainDefs", "TerrainDef"), 3),
    ("weather", "WeatherDef", _names("WeatherDefs", "WeatherDef"), 3),
    ("conditions", "GameConditionDef", _names("GameConditionDefs", "GameConditionDef"), 1),
    ("hediffs", "HediffDef", _names("HediffDefs", "HediffDef"), 1),
    ("research", "ResearchProjectDef", _names("ResearchProjectDefs", "ResearchProjectDef"), 1),
    ("sounds", "SoundDef", _names("SoundDefs", "SoundDef"), 10),
    ("render_trees", "PawnRenderTreeDef", _names("PawnRenderTreeDefs", "PawnRenderTreeDef"), 1),
    ("biome", "BiomeDef", _names("BiomeDefs", "BiomeDef"), 1),
]
ALL_DEFNAMES = set(n for _, _, names, _ in GROUPS for n in names)
CYCLE_TERRAINS = _names("TerrainDefs", "TerrainDef")
FLYERS = ("RM_Jossur", "RM_FleetFlier")
DORMANT_NATIVES = ("RM_Dhokkur", "RM_Julmox", "RM_Dhuvvox")
PLANT_MESH = dict((n, (el.findtext("plant/maxMeshCount") or "").strip()) for t, n, el in _BY_DIR["ThingDefs_Plants"])

_BIOME_EL = next((el for t, n, el in _BY_DIR["BiomeDefs"] if n == BIOME), None)


def _roster(tag):
    """{defName: (commonality, MayRequire-or-None)} for the biome's <wildAnimals>/<wildPlants> (children named for
    the def, text = commonality; never <li> -- CLAUDE.md)."""
    out = {}
    block = _BIOME_EL.find(tag) if _BIOME_EL is not None else None
    for ch in (block if block is not None else []):
        if not isinstance(ch.tag, str):
            continue
        try:
            out[ch.tag] = (float((ch.text or "").strip()), ch.get("MayRequire"))
        except ValueError:
            _ERRORS.append("%s/%s: commonality %r is not a number" % (tag, ch.tag, ch.text))
    return out


BIOME_ANIMALS = _roster("wildAnimals")
BIOME_PLANTS = _roster("wildPlants")
BIOME_SCALARS = dict((k, float(_BIOME_EL.findtext(k))) for k in ("animalDensity", "plantDensity")
                     if _BIOME_EL is not None and _BIOME_EL.findtext(k))


def _read_cs(name):
    try:
        with open(os.path.join(_SRC, name), encoding="utf-8") as fh:
            return fh.read()
    except Exception as ex:
        _ERRORS.append("%s: %s" % (name, ex))
        return ""


def _read_text(rel):
    """A file under the mod folder (Defs/...), read as text; a failure is recorded like a source-parse error."""
    try:
        with open(os.path.join(_HERE, rel), encoding="utf-8") as fh:
            return fh.read()
    except Exception as ex:
        _ERRORS.append("%s: %s" % (rel, ex))
        return ""


def _settings_defaults():
    """{field: default} for every `public static` field of RM_TheForgeSettings, read from the C# source."""
    text = _read_cs("RM_TheForgeMod.cs")
    cut = text.find("private static Vector2")
    out = {}
    for typ, name, val in re.findall(r"public static (bool|float|int) (\w+) = ([^;]+);", text[:cut if cut > 0 else None]):
        val = val.strip()
        if typ == "bool":
            out[name] = (val == "true")
        else:
            out[name] = float(val.rstrip("fF"))
    return out


SETTINGS_DEFAULTS = _settings_defaults()
# the toggles that CHANGE something today (RM_TheForgeMod.cs header: the other five are scaffolding)
WIRED = ["modEnabled", "weatherPulseEnabled", "grandCycleEnabled", "gasWashEnabled", "cycleFloodingEnabled",
         "lavaFreezeEnabled", "meltBackDestroys", "floatstoneBloomEnabled", "cycleDormancyEnabled",
         "cycleTelegraphLetters", "keelworkEnabled", "keelRingEnabled", "spunstoneStudyEnabled", "forgeVoicesEnabled",
         "forgeVoicesVisualCues", "dhuvvoxClockEnabled", "dhuvvoxRunSoundEnabled", "dhuvvoxSwarmEnabled",
         "plumeFrontsEnabled", "plumeObscureEnabled", "plumeSoakEnabled", "plumeHeatEnabled", "plumeAdaptedExempt",
         "plumeStrength",
         "skyColumnGridEnabled", "skyAshSpiralsEnabled", "skyColumnHuntEnabled", "jossurStoopEnabled", "skyColumnHighlightEnabled",
         "floatstoneDoorEnabled", "spunstoneHullEnabled"]
# FORGE_DHOKKUR_WAYS_1 (RM_ForgeDhokkurWays.cs): wired in the C#, but NO component of this suite drives them yet, so
# they are neither WIRED (the toggle floor would demand a component) nor scaffolding (they do change something).
UNCOVERED = ["dhokkurWakeEffectsEnabled", "dhokkurPathMemoryEnabled", "dhokkurPassesToPolish", "dhokkurTrailsFade",
             "dhokkurTrailFadeDays", "dhokkurWallShoveEnabled", "dhokkurShoveMode", "dhokkurShoveDamagePct"]
# FORGE_SPUNSTONE_SOURCES_1: the floatstone-only builds spunstone bonding unlocks besides the keel brace.
SPUNSTONE_PARTS = ("RM_FloatstoneDoor", "RM_SpunstoneHull")
SCAFFOLDING = sorted(k for k in SETTINGS_DEFAULTS if k not in WIRED and k not in UNCOVERED)
suite.toggles = list(WIRED)


def _phases():
    m = re.search(r"enum ForgeCyclePhase\s*\{([^}]*)\}", _read_cs("RM_GameCondition_ForgeCycle.cs"))
    return [re.sub(r"\s*=.*", "", p).strip() for p in (m.group(1).split(",") if m else []) if p.strip()]


PHASES = _phases()
CUE_TEXT = {}
for _m in re.finditer(r"case ForgeCyclePhase\.(\w+): return \"([^\"]+)\";", _read_cs("RM_ForgeVoices.cs")):
    CUE_TEXT[_m.group(1)] = _m.group(2)
LETTERS = {"Freeze": "The freeze", "Cracks": "Glowing cracks", "Melt": "The melt", "hiss": "A hiss in the vents"}
REPORT_TOKENS = ("phase", "endsIn", "inBurst", "frozen", "gardensLive", "cycles", "gasIgnitions", "floods",
                 "cellsFrozen", "cellsMelted", "gardensSpawned", "gardensDrifted", "meltDestroyed",
                 "meltPawnsBurned", "meltRelocated")

# --------------------------------------------------------------------------------- helpers


class _Unmeasured(Exception):
    pass


def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False in the offline declaration
    probe, so manual assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    """Stop this component and record UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True            # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, independent=False, **kw):
    """t.component() plus: `_unmeasured` records the real reason as the detail; with independent=True a FAIL or
    UNMEASURED does not poison the next component (pure reads that share no state), while a setup component (the
    default) leaves every later component of its chain UNMEASURED."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
    if independent and not before:
        t.upstream_failed = False
    t._why = None
    if t.session is not None and t.components:
        c = t.components[-1]
        print("[forge] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
              file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, also echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[forge-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]), file=sys.stderr, flush=True)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _flat(obj):
    """Every string / number / bool anywhere inside a JSON-ish value, as strings."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            for x in _flat(v):
                yield x
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for x in _flat(v):
                yield x
    elif obj is not None:
        yield str(obj)


def _find_key(obj, key):
    """Every value stored under `key` anywhere inside a JSON-ish value."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            for x in _find_key(v, key):
                yield x
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for x in _find_key(v, key):
                yield x


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _need_parse(t):
    if _ERRORS:
        _fail("the mod's own sources did not parse: %s" % "; ".join(_ERRORS[:3]))
    if len(PHASES) != 7 or len(SETTINGS_DEFAULTS) < 20 or not CUE_TEXT:
        _fail("source parse is short (phases %d, settings %d, cues %d): a parse failure, not a mod fact"
              % (len(PHASES), len(SETTINGS_DEFAULTS), len(CUE_TEXT)))


def _get_defs(t, specs, fields=None, deep=False):
    """get_defs over `DefType/defName` specs (a STRING, chunked); returns [row,...] and notFound. Reads the tool's
    own success/foundCount/notFound -- never a substring of the payload."""
    rows, missing = [], []
    for i in range(0, len(specs), 40):
        chunk = specs[i:i + 40]
        r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields=fields or "", deep=bool(deep))
        if not _live(t):
            return [], []
        _ok(r, "get_defs(%d defs)" % len(chunk))
        if r.get("requested") not in (None, len(chunk)):
            _fail("get_defs asked for %d, tool says it handled %r" % (len(chunk), r.get("requested")))
        rows.extend(r.get("defs") or [])
        missing.extend(r.get("notFound") or [])
        if (r.get("foundCount") is not None
                and r.get("foundCount") + len(r.get("notFound") or []) != len(chunk)):
            _fail("get_defs foundCount %r + notFound %r != %d requested" % (
                r.get("foundCount"), len(r.get("notFound") or []), len(chunk)))
    return rows, missing


def _one_def(t, spec, fields, deep=False):
    """The `fields` map of one def, FAILING if it did not resolve."""
    rows, missing = _get_defs(t, [spec], fields=fields, deep=deep)
    if not _live(t):
        return {}
    if missing or len(rows) != 1 or not rows[0].get("found", True):
        _fail("%s did not resolve: notFound=%r" % (spec, missing))
    return rows[0].get("fields") or {}


def _things(t, defs, rect, limit=500):
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=limit)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defs)
    if r.get("isCompleteList") is False:
        _fail("list_things(%s) truncated: %r" % (defs, r.get("message")))
    return list(r.get("things") or [])


def _stack(row):
    for k in ("stackCount", "count", "stack"):
        if isinstance(row.get(k), (int, float)):
            return int(row[k])
    return 1


def _pawns(t, rect, kind=None, health=False):
    r = t.bridge_call("jawa/list_pawns", rect=rect, limit=200, includeHealth=bool(health))
    if not _live(t):
        return []
    _ok(r, "list_pawns")
    if r.get("truncated"):
        _fail("list_pawns truncated: %r" % r.get("message"))
    return [p for p in (r.get("pawns") or []) if kind is None or p.get("kindDef") == kind]


# --------------------------------------------------------------------------------- the site

def _enter(t):
    """First line of every fixture chain: move this chain's anchor to the pad, off the map centre."""
    if not getattr(t, "_forge_anchored", False):
        x, z = t.anchor
        t.anchor = (x + PAD_OFFSET, z + PAD_OFFSET)
        t._forge_anchored = True


def _lava(t):
    x, z = t.anchor
    return (x, z, LAVA, LAVA)


def _yard(t):
    x, z = t.anchor
    return (x + LAVA + SOIL_DX - LAVA, z, YARD, YARD)


def _pad(t):
    """Bounding rect of lava + yard + the relocation margin (a melt moves survivors up to 8 cells)."""
    x, z = t.anchor
    return (x - 10, z - 10, LAVA + SOIL_DX + YARD + 14, LAVA + 20)


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _ticks(t):
    r = t.bridge_call("jawa/time_clock")
    if not _live(t):
        return 0
    v = _ok(r, "time_clock").get("ticksGame")
    if v is None:
        _unmeasured(t, "time_clock has no ticksGame: %s" % str(r)[:120])
    return int(v)


def _layers(t, rect):
    r = t.bridge_call("jawa/get_terrain_layers", rect=_rs(rect), limit=3000)
    if not _live(t):
        return []
    _ok(r, "get_terrain_layers")
    if r.get("truncated"):
        _fail("get_terrain_layers truncated at %r of %r cells" % (r.get("returned"), r.get("cellsMatchingFilter")))
    return list(r.get("cells") or [])


def _census(cells, key):
    out = {}
    for c in cells:
        out[c.get(key)] = out.get(c.get(key), 0) + 1
    return out


def _reset_pad(t):
    """Everything true before the first assertion: the pad empty (things and pawns), plain soil with one LAVA x LAVA
    square of LavaDeep (the terrain the freeze crusts), unfogged. Lava is permanent top terrain, so the square comes
    back after every melt and a chain can run another pass on it."""
    rect = _rs(_pad(t))
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="All")
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="Pawn")
    t.bridge_call("jawa/set_terrain_batch", ops="Soil:%s" % rect)
    t.bridge_call("jawa/set_terrain_batch", ops="LavaDeep:%s" % _rs(_lava(t)))
    t.bridge_call("jawa/set_fog", action="unfog", rect=rect)
    t.bridge_call("jawa/log_autoopen_suppress")
    if _live(t):
        cells = _layers(t, _lava(t))
        tops, temps = _census(cells, "top"), _census(cells, "temp")
        if tops.get("LavaDeep") != LAVA * LAVA:
            _fail("the lava square did not take LavaDeep: top terrain census %r" % tops)
        if any(k for k in temps if k):
            _fail("precondition: temp terrain already on the lava square %r (a previous run's crust on a reused "
                  "map; run on a FRESH quicktest game)" % temps)


def _teardown(t):
    """Best-effort, runs even after a FAILED chain (t.bridge_call is then a no-op, so use the session)."""
    if t.session is None or not getattr(t, "_forge_anchored", False):
        return
    try:
        rect = _rs(_pad(t))
        t.session.call("jawa/destroy_batch", rects=rect, categories="All")
        t.session.call("jawa/destroy_batch", rects=rect, categories="Pawn")
    except Exception as ex:                       # teardown must never mask the chain's own verdict
        print("[forge] teardown failed: %s" % ex, file=sys.stderr, flush=True)


# ------------------------------------------------------------------------------------ settings arms

def _raw_get(t, field, type_name=SETTINGS):
    r = t.session.call("jawa/mod_settings_field", typeName=type_name, action="get", field=field)
    return (r or {}).get("value")


def _raw_set(t, field, value, type_name=SETTINGS):
    return t.session.call("jawa/mod_settings_field", typeName=type_name, action="set", field=field, value=str(value))


@contextlib.contextmanager
def _settings(t, type_name=SETTINGS, **kv):
    """Set `kv` for the body and ALWAYS restore the previous raw values, even after a failed chain."""
    old = {}
    if t.session is not None:
        for f in kv:
            old[f] = _raw_get(t, f, type_name)
    try:
        if _live(t):
            for f, v in kv.items():
                r = _raw_set(t, f, v, type_name) or {}
                if not r.get("success"):
                    _fail("mod_settings_field(set %s=%s) failed: %s" % (f, v, json.dumps(r, default=str)[:200]))
                back = _raw_get(t, f, type_name)
                if str(back) != str(v):
                    _fail("setting %s did not take: wrote %r, read %r" % (f, v, back))
        yield
    finally:
        if t.session is not None:
            for f, v in old.items():
                try:
                    _raw_set(t, f, v, type_name)
                except Exception:
                    pass


def _apply(t):
    """Make RM_TheForgeMod.WriteSettings run, the way a player does: open the Mod Settings dialog and close it."""
    if not _live(t):
        return
    r = t.bridge_call("rimworld/open_mod_settings", modId=DIALOG_QUERY, replaceExisting=True) or {}
    if not r.get("success", False):
        _unmeasured(t, "cannot open the Mod Settings dialog for %s: %s" % (MOD_ID, json.dumps(r, default=str)[:200]))
    t.bridge_call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)


def _apply_safely(t):
    if t.session is None:
        return
    try:
        t.session.call("rimworld/open_mod_settings", modId=DIALOG_QUERY, replaceExisting=True)
        t.session.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    except Exception:
        pass


# ------------------------------------------------------------------------------ the mod's debug actions

_ACTIONS = {}
_PREFIXES = ("Forge cycle:", "Spunstone:", "Forge plumes:")


def _find_actions(t):
    if _ACTIONS or not _live(t):
        return _ACTIONS
    r = t.bridge_call("rimworld/list_debug_action_children", path="Actions") or {}
    kids = r.get("children") or []
    found = {}
    for c in kids:
        label = c.get("label") or ""
        if label == "RMTheForge" or (c.get("path") or "").endswith("\\RMTheForge"):
            sub = t.bridge_call("rimworld/list_debug_action_children", path=c.get("path")) or {}
            found = dict(((l.get("label") or ""), l.get("path")) for l in sub.get("children") or [])
            break
    if not found:     # 1.6 flattens mod categories: "T: <label>" leaves directly under Actions
        found = dict(((c.get("label") or ""), c.get("path")) for c in kids
                     if any(p in (c.get("label") or c.get("path") or "") for p in _PREFIXES))
    if not found:
        _unmeasured(t, "no RMTheForge debug actions in the live Actions tree (mod not loaded, or the tree did not "
                       "enumerate: success=%r children=%d)" % (r.get("success"), len(kids)))
    _ACTIONS.update(found)
    return _ACTIONS


def _tokens(line):
    out = {}
    for k, v in re.findall(r"(\w+)=(-?[A-Za-z0-9_.]+)", line):
        if k == "phase":
            out[k] = v
        elif k in ("inBurst", "projectHidden", "revealed", "canStart"):
            out[k] = (v == "True")
        else:
            try:
                out[k] = int(v)
            except ValueError:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
    return out


def _act(t, label):
    """Run one RMTheForge debug action; return its tagged log line parsed into {token: value} plus `_line`. A missing
    action FAILS; a result with no tagged line is UNMEASURED (the log cap); the probe returns {}."""
    if not _live(t):
        return {}
    acts = _find_actions(t)
    path = next((p for l, p in acts.items() if label.lower() in l.lower()), None)
    if not path:
        _fail("no RMTheForge debug action matching %r (have %d)" % (label, len(acts)))
    r = t.bridge_call("rimworld/execute_debug_action", path=path) or {}
    logs = [str(m.get("message") if isinstance(m, dict) else m) for m in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        i = line.find(TAG)
        if i >= 0:
            d = _tokens(line[i + len(TAG):])
            d["_line"] = line[i:]
            return d
    _unmeasured(t, "debug action %r logged no %s line (log cap reached after a long session? relaunch and rerun) "
                   "raw: %s" % (label, TAG, json.dumps(r, default=str)[:300]))


def _report(t):
    """The cycle condition's state. FAILS when no ForgeCycle condition is on the map; UNMEASURED when the report
    line lacks a token (the C# DebugStateReport changed: a harness defect)."""
    d = _act(t, "Forge cycle: report state")
    if not _live(t):
        return {}
    if "no RM_GameCondition_ForgeCycle" in d.get("_line", ""):
        _fail("no RM_GameCondition_ForgeCycle is active on the current map: %s" % d["_line"])
    miss = [k for k in REPORT_TOKENS if k not in d]
    if miss:
        _unmeasured(t, "report line lacks %s: RM_GameCondition_ForgeCycle.DebugStateReport changed? %s" % (miss, d["_line"]))
    return d


def _advance(t):
    d = _act(t, "Forge cycle: advance one phase")
    if _live(t):
        if "no RM_GameCondition_ForgeCycle" in d.get("_line", ""):
            _fail("advance: no RM_GameCondition_ForgeCycle is active on the current map")
        if "phase" not in d:
            _unmeasured(t, "advance line carries no phase token: %s" % d.get("_line"))
    return d


def _to_phase(t, target, limit=9):
    """Advance until the cycle reports `target`; returns the report."""
    for _ in range(limit):
        rep = _report(t)
        if not _live(t) or rep.get("phase") == target:
            return rep
        _advance(t)
    rep = _report(t)
    if _live(t) and rep.get("phase") != target:
        _fail("could not reach phase %s in %d advances; at %s" % (target, limit, rep.get("phase")))
    return rep


# ------------------------------------------------------------------------------ the cycle condition

def _cond_present(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return False
    _ok(r, "weather_get")
    return any(c.get("def") == COND and c.get("affectsThisMap") is not False for c in (r.get("conditions") or []))


def _drop_weather_locks(t):
    """SITE: other suites on a shared map leave PERMANENT `jawa/weather_set lockWeather=True` Clear locks
    (Greentide, Pyrelands, Stillsand ... lock per site build and several never unlock), and
    WeatherDecider.ForcedWeather takes the LAST forcing condition, so a lock can outrank the pulse's boiling rain.
    Each unlock ends one lock (it leaves the list on the next tick), so loop until none is in force."""
    for _ in range(40):
        r = t.bridge_call("jawa/weather_set", unlock=True)
        if not _live(t) or not isinstance(r, dict) or not r.get("lockInForce"):
            return
        t.wait_ticks(2)
    _fail("SITE: weather locks still in force after 40 unlocks")


def _start_cycle(t):
    """A FRESH RM_ForgePulse on the current map (ends any running one first)."""
    if not _live(t):
        return
    _drop_weather_locks(t)
    if _cond_present(t):
        t.bridge_call("jawa/game_condition", action="end", condition=COND)
        t.wait_ticks(120)
        if _cond_present(t):
            _fail("RM_ForgePulse did not end after jawa/game_condition end")
    r = t.bridge_call("jawa/game_condition", action="start", condition=COND, permanent=True)
    _ok(r, "game_condition(start RM_ForgePulse)")
    if not _cond_present(t):
        _fail("RM_ForgePulse is not among the active conditions after start: %s" % str(r)[:200])


def _end_cycle_safely(t):
    if t.session is None:
        return
    try:
        t.session.call("jawa/game_condition", action="end", condition=COND)
    except Exception:
        pass


def _wind_down(t):
    """Finish whatever cycle is running, then end it. Ending a condition does NOT melt a standing crust (the temp
    terrain stays on the map), so every chain that ran the cycle winds it down in its `finally`, through the raw
    session (t.bridge_call is a no-op after a failed chain)."""
    if t.session is None:
        return
    try:
        adv = next((p for l, p in _ACTIONS.items() if "advance one phase" in l.lower()), None)
        rep = next((p for l, p in _ACTIONS.items() if "report state" in l.lower()), None)

        def line(path):
            r = t.session.call("rimworld/execute_debug_action", path=path) or {}
            for m in ((r.get("effects") or {}).get("logs") or []):
                msg = str(m.get("message") if isinstance(m, dict) else m)
                if TAG in msg:
                    return msg
            return ""
        if adv and rep:
            for _ in range(9):
                msg = line(rep)
                tok = _tokens(msg)
                if not msg or "no RM_GameCondition" in msg:
                    break
                if tok.get("frozen") == 0 and tok.get("phase") == "StillHeat":
                    break
                line(adv)
    except Exception as ex:
        print("[forge] wind-down failed: %s" % ex, file=sys.stderr, flush=True)
    _end_cycle_safely(t)
    try:
        # The gas wash lights unroofed plants anywhere on the map; left burning they abort the NEXT chain as
        # `fire_on_map` (LIVE 2026-10-04: voices 23 fires, dormancy 3).
        info = t.session.call("jawa/map_info") or {}
        n = int(info.get("sizeX", 250))
        t.session.call("jawa/map_fire", action="extinguish", rect="0,0,%d,%d" % (n, int(info.get("sizeZ", n))))
    except Exception as ex:
        print("[forge] wind-down extinguish failed: %s" % ex, file=sys.stderr, flush=True)


def _weather(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return None
    _ok(r, "weather_get")
    cur = (r.get("weather") or {})
    return cur.get("current") if isinstance(cur, dict) else cur


def _lbl(l):
    """A letter label off jawa/letter_list is a TaggedString dict {"RawText": ...}, not a str (LIVE 2026-10-03:
    a dict used as a key raised TypeError: unhashable type)."""
    v = l.get("label")
    return v.get("RawText") if isinstance(v, dict) else v


def _letters(t):
    """{label: count} of every letter on the stack."""
    r = t.bridge_call("jawa/letter_list")
    if not _live(t):
        return {}
    _ok(r, "letter_list")
    out = {}
    for l in r.get("letters") or []:
        out[_lbl(l)] = out.get(_lbl(l), 0) + 1
    return out


def _inspect(t, ids):
    """{thingId: [inspect lines]} for the given thing ids; a thing missing from the answer FAILS."""
    r = t.bridge_call("jawa/inspect_string", thingIds=",".join(ids), limit=len(ids) + 5)
    if not _live(t):
        return {}
    _ok(r, "inspect_string")
    rows = dict((x.get("id"), x) for x in (r.get("things") or []))
    out = {}
    for i in ids:
        if i not in rows:
            _unmeasured(t, "inspect_string did not return thing %s (a pawn is not in listerThings? %s)" % (i, str(r)[:160]))
        if rows[i].get("error"):
            _fail("inspect_string threw building %s's string: %s" % (i, rows[i]["error"]))
        out[i] = [str(s).lower() for s in (rows[i].get("inspect") or [])]
    return out


def _has(lines, phrase):
    return any(phrase in s for s in lines)


def _spawn_wild(t, kind, x, z):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none", count=1)
    if not _live(t):
        return None
    _ok(r, "spawn_pawn(%s)" % kind)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn id: %r" % (kind, r))
    return pid


def _jump(t, delta):
    """Move the game clock forward by `delta` ticks (time only moves forward) and read it back."""
    if not _live(t):
        return 0
    now = _ticks(t)
    target = now + int(delta)
    t.bridge_call("jawa/time_set_ticks", ticks=target)
    got = _ticks(t)
    if got < target:
        _fail("time_set_ticks to %d left the clock at %d" % (target, got))
    return got


# ================================================================================= chains

@suite.chain("log_clean")
def log_clean(t):
    """The whole load, one read: no config error, unresolved cross-reference, missing type or exception naming this
    mod's content. Guards the known load defects of this mod's neighbourhood: a dangling cross-reference discarding
    a def whole (LOAD_ERRORS_DEF_FIELDS_1), and the `plant.MaxMeshCount that is a perfect square` flood that used up
    RimWorld's 10,000-message log cap and silenced every debug action (BRIDGE_MOD_DEBUGACTIONS_NOOP_1)."""
    with _comp(t, "player_log_names_no_forge_error", independent=True):
        if _live(t):
            _need_parse(t)
            from game_paths import PLAYER_LOG
            if not os.path.isfile(PLAYER_LOG):
                _unmeasured(t, "no Player.log at %s" % PLAYER_LOG)
            with open(PLAYER_LOG, "rb") as fh:
                text = fh.read().decode("utf-8", "replace")
            lines = text.splitlines()
            if "Bridge token" not in text and "RimBridge" not in text:
                _unmeasured(t, "Player.log (%d lines) does not look like a bridged live session" % len(lines))
            names = re.compile("|".join(re.escape(n) for n in sorted(
                ALL_DEFNAMES | set(["TheForge", COND, BIOME, "RM_ForgeCycleExtension", "RM_GameCondition_ForgeCycle",
                                    "RM_CompForgeCycleDormancy", "RM_TheForgeBiomeRanges"]))))
            bad_kind = ("Config error", "Could not resolve cross-reference", "Could not find type named",
                        "Exception", "rror in", "must have plant.MaxMeshCount")
            hits = [ln.strip() for ln in lines if names.search(ln) and any(k in ln for k in bad_kind)]
            capped = [ln for ln in lines if "Reached max messages limit" in ln]
            general = sum(1 for ln in lines if "Config error" in ln or "Could not resolve cross-reference" in ln)
            _note(t, "Player.log scan", {"lines": len(lines), "hits": hits[:5], "log cap reached": len(capped),
                                         "game-wide config/xref lines (instrument probe)": general})
            if hits:
                _fail("%d Player.log line(s) name this mod's content in an error: %s" % (
                    len(hits), " | ".join(h[:200] for h in hits[:3])))
            if capped:
                _unmeasured(t, "the log hit RimWorld's 10,000-message cap (every debug action will be silent): "
                               "relaunch before the cycle chains")


@suite.chain("defs_resolve")
def defs_resolve(t):
    """Every def this mod ships resolves in the running game (a def that fails to load is dropped whole and silently:
    a missing comp/worker type, a dangling cross-reference). Expected names come from the mod's own XML. A control
    proves the instrument can say 'not found'."""
    with _comp(t, "resolve_probe_sees_absence", independent=True):
        real = (GROUPS[3][2] or ["RM_Floatstone"])[0]
        rows, missing = _get_defs(t, ["ThingDef/RM_NoSuchForgeDef_Control", "ThingDef/%s" % real])
        if _live(t):
            found = [r.get("defName") for r in rows if r.get("found")]
            if missing != ["ThingDef/RM_NoSuchForgeDef_Control"] or found != [real]:
                _fail("the def probe cannot tell present from absent: found=%r notFound=%r" % (found, missing))

    for group, deftype, names, floor in GROUPS:
        with _comp(t, "defs_resolve_%s" % group, independent=True):
            if _live(t):
                _need_parse(t)
                if len(names) < floor:
                    _fail("source parse found %d %s defs, floor is %d -- a parse failure or an undeclared deletion "
                          "(edit GROUPS deliberately if the mod shrank)" % (len(names), group, floor))
            rows, missing = _get_defs(t, ["%s/%s" % (deftype, n) for n in names])
            if _live(t):
                if missing:
                    _fail("%d of %d %s not loaded by the game: %s" % (len(missing), len(names), group, missing[:8]))
                wrong = [r.get("defName") for r in rows if r.get("packageId") not in OUR_PACKAGES]
                if wrong:
                    _fail("defs resolve but from another mod (shadowed?): %s" % wrong[:6])

    with _comp(t, "plants_mesh_count_is_perfect_square", independent=True):
        # RimWorld/Plant.cs prints an error per mesh print for any other count: 8,994 of them used up the log cap
        # (BRIDGE_MOD_DEBUGACTIONS_NOOP_1) and also offsets extra meshes by whole cells. Read from the XML.
        if _live(t):
            _need_parse(t)
            bad = dict((n, v) for n, v in PLANT_MESH.items() if v and int(v) not in MESH_OK)
            if len(PLANT_MESH) < 4:
                _fail("source parse found %d plants" % len(PLANT_MESH))
            if bad:
                _fail("plant.maxMeshCount must be 1/4/9/16/25, got %s" % bad)

    with _comp(t, "cycle_terrains_are_temporary", independent=True):
        # RM_ForgeCycleExtension.ConfigErrors: the crust lives on the temp-terrain layer, so every def must say so.
        rows, missing = _get_defs(t, ["TerrainDef/%s" % n for n in CYCLE_TERRAINS], fields="temporary,walkable")
        if _live(t):
            _need_parse(t)
            if missing or len(rows) != len(CYCLE_TERRAINS) or len(CYCLE_TERRAINS) < 3:
                _fail("crust terrains not resolvable: %r" % missing)
            notemp = [r.get("defName") for r in rows if str((r.get("fields") or {}).get("temporary")) != "True"]
            if notemp:
                _fail("not temporary (SetTempTerrain would refuse them): %s" % notemp)

    with _comp(t, "scald_damage_def_resolves", independent=True):
        # RM_ForgePulse's scaldDamageDef is RUT_Scald (a TerminalBiomes def): a null scald def makes the burst weather
        # harmless with no error, because DoScaldDamageTick returns on a null def.
        rows, missing = _get_defs(t, ["DamageDef/RUT_Scald"])
        if _live(t):
            if missing or not rows:
                _fail("DamageDef RUT_Scald does not resolve on this tier: the boiling rain scalds nobody: %r" % missing)


@suite.chain("def_wiring")
def def_wiring(t):
    """Def fields that wire one def to another and fail without a log line when they are wrong."""
    with _comp(t, "native_dormancy_comps_wired", independent=True):
        # jobDormancy is what HOLDS a dormant pawn asleep (the comp's own header); the Forge comp must name its
        # rain/flash flags. Read deep because comps are objects.
        if _live(t):
            _need_parse(t)
        for kind in DORMANT_NATIVES:
            f = _one_def(t, "ThingDef/%s" % kind, "comps", deep=True)
            if _live(t):
                comps = f.get("comps")
                if not isinstance(comps, (dict, list)):
                    _unmeasured(t, "get_defs cannot serialise ThingDef.comps (got %r)" % (comps,))
                jd = list(_find_key(comps, "jobDormancy"))
                rain = list(_find_key(comps, "awakeDuringRain"))
                if not jd or str(jd[0]).lower() != "true":
                    _fail("%s: CompProperties_CanBeDormant.jobDormancy is %r; without it the pawn is never held asleep" % (kind, jd))
                if not rain:
                    _fail("%s: no CompProperties_ForgeCycleDormancy (awakeDuringRain) among its comps" % kind)

    with _comp(t, "flyers_carry_flight_stat", independent=True):
        # 1.6 flight is a STAT: CanEverFly = MaxFlightTime > 0 (CLAUDE.md flyer law). A state read of the def only:
        # no unattended flight is ever driven (ruled three times).
        for kind in FLYERS:
            f = _one_def(t, "ThingDef/%s" % kind, "statBases", deep=True)
            if _live(t):
                sb = f.get("statBases")
                if not isinstance(sb, (dict, list)):
                    _unmeasured(t, "get_defs cannot serialise statBases (got %r)" % (sb,))
                vals = [_num(x) for x in _find_key(sb, "value")]
                blob = list(_flat(sb))
                if "MaxFlightTime" not in blob:
                    _fail("%s has no MaxFlightTime stat: it cannot fly" % kind)
                nums = [v for v in vals if v is not None]
                if not nums:
                    _unmeasured(t, "statBases carries MaxFlightTime but no readable value: %s" % blob[:12])
                if not any(v > 0 for v in nums):
                    _fail("%s: MaxFlightTime reads %r; CanEverFly needs it above 0, so it cannot fly" % (kind, nums))

    with _comp(t, "floatstone_only_from_gardens", independent=True):
        # generateCommonality 0: nothing but harvesting a garden produces it (the item's header).
        f = _one_def(t, "ThingDef/RM_Floatstone", "generateCommonality,tradeability")
        if _live(t):
            gc = _num(f.get("generateCommonality"))
            if gc is None:
                _unmeasured(t, "generateCommonality unreadable: %r" % (f.get("generateCommonality"),))
            if gc != 0.0:
                _fail("RM_Floatstone.generateCommonality is %r; it must be 0 so only gardens make it" % gc)

    with _comp(t, "keel_brace_needs_spunstone_research", independent=True):
        f = _one_def(t, "ThingDef/RM_FloatstoneKeelBrace", "researchPrerequisites")
        if _live(t):
            pre = f.get("researchPrerequisites")
            if not isinstance(pre, list):
                _unmeasured(t, "researchPrerequisites unreadable: %r" % (pre,))
            if "RM_SpunstoneBonding" not in pre:
                _fail("the keel brace is not gated by RM_SpunstoneBonding: %r" % pre)

    with _comp(t, "spunstone_parts_need_spunstone_research", independent=True):
        # FORGE_SPUNSTONE_SOURCES_1 (owner ruling 2026-10-03): the door and hull are unlocked by spunstone bonding.
        for name in SPUNSTONE_PARTS:
            f = _one_def(t, "ThingDef/%s" % name, "researchPrerequisites")
            if _live(t):
                pre = f.get("researchPrerequisites")
                if not isinstance(pre, list):
                    _unmeasured(t, "%s.researchPrerequisites unreadable: %r" % (name, pre))
                if "RM_SpunstoneBonding" not in pre:
                    _fail("%s is not gated by RM_SpunstoneBonding: %r" % (name, pre))

    with _comp(t, "engine_links_keel_brace", independent=True):
        # RM_TheForge_KeelBraceLink.xml is a PatchOperationConditional: a patch that matches nothing logs nothing,
        # so the brace would build and never link.
        f = _one_def(t, "ThingDef/GravEngine", "comps", deep=True)
        if _live(t):
            comps = f.get("comps")
            if not isinstance(comps, (dict, list)):
                _unmeasured(t, "get_defs cannot serialise GravEngine.comps (got %r)" % (comps,))
            lf = list(_find_key(comps, "linkableFacilities"))
            if not lf:
                _unmeasured(t, "no linkableFacilities readable on GravEngine (Odyssey absent, or shape): %s" % str(comps)[:200])
            if "RM_FloatstoneKeelBrace" not in set(_flat(lf)):
                _fail("GravEngine's linkableFacilities lacks RM_FloatstoneKeelBrace: the patch matched nothing: %s"
                      % sorted(set(_flat(lf)))[:10])


@suite.chain("biome_wiring")
def biome_wiring(t):
    """`RM_TheForge` as the game resolved it (jawa/biome_probe reads the runtime caches, the only tool that can see
    wildAnimals/wildPlants). Live is compared with the mod's own XML, so a patch that removes or zeroes a row, a
    dropped record, or a dead roster each fail."""
    box = {}
    with _comp(t, "biome_probe_ready"):
        r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True, topN=200,
                          find="RM_Dhuvvox,RM_NoSuchCreatureControl")
        if _live(t):
            _ok(r, "biome_probe")
            rows = r.get("biomes") or []
            if len(rows) != 1 or rows[0].get("defName") != BIOME:
                _fail("biome_probe did not return exactly %s: %s" % (BIOME, str(r)[:300]))
            box["row"] = rows[0]
            box["animals"] = dict((a.get("defName"), a.get("commonality")) for a in (rows[0].get("animals") or []))
            box["plants"] = dict((p.get("defName"), p.get("commonality")) for p in (rows[0].get("plants") or []))
            box["find"] = dict((f.get("defName"), f.get("state")) for f in (rows[0].get("findResults") or []))
            if rows[0].get("wildAnimalCount") != rows[0].get("animalsListed") or \
                    rows[0].get("wildPlantCount") != rows[0].get("plantsListed"):
                _fail("biome_probe lists were capped (animals %r/%r, plants %r/%r)" % (
                    rows[0].get("animalsListed"), rows[0].get("wildAnimalCount"),
                    rows[0].get("plantsListed"), rows[0].get("wildPlantCount")))

    with _comp(t, "biome_densities_live", independent=True):
        # wildAnimals spawn only while animalDensity > 0 (MEASURED from the engine, CLAUDE.md): 0 = dead roster
        if _live(t):
            _need_parse(t)
            row = box["row"]
            for k in ("animalDensity", "plantDensity"):
                if not (float(row.get(k) or 0) > 0):
                    _fail("%s is %r: a zero density makes the roster dead content" % (k, row.get(k)))
                if k in BIOME_SCALARS and abs(float(row[k]) - BIOME_SCALARS[k]) > 1e-4:
                    _fail("%s live %r != source %r" % (k, row[k], BIOME_SCALARS[k]))

    for kind, expect in (("animals", BIOME_ANIMALS), ("plants", BIOME_PLANTS)):
        with _comp(t, "wild_%s_wired" % kind, independent=True):
            if _live(t):
                _need_parse(t)
                if len(expect) < 8:
                    _fail("source parse found %d wild %s rows: parse failure" % (len(expect), kind))
                missing, skewed, skipped = [], [], []
                for name, (c, req) in sorted(expect.items()):
                    if req and req not in ACTIVE_ON_TIER:
                        skipped.append("%s (needs %s)" % (name, req))
                        continue
                    live = box[kind].get(name)
                    if live is None:
                        missing.append(name)
                    elif abs(float(live) - c) > 1e-3:
                        skewed.append("%s live %.3f != source %.3f" % (name, float(live), c))
                _note(t, "wild %s rows not asserted (their donor mod is not on this tier)" % kind, skipped)
                if missing or skewed:
                    _fail("wild %s drift: missing %s; commonality %s" % (kind, missing, skewed))

    with _comp(t, "natives_spawn_and_probe_is_honest", independent=True):
        # The two controls prove the three-state probe: a real row is 'spawning', an invented one 'absent'.
        if _live(t):
            f = box["find"]
            if f.get("RM_Dhuvvox") != "spawning" or f.get("RM_NoSuchCreatureControl") != "absent":
                _fail("biome_probe's find states are not trustworthy / a native is not spawning: %r" % f)

    with _comp(t, "biome_map_condition_is_forge_pulse", independent=True):
        # RM_ForgePulse reaches a map ONLY through the biome's biomeMapConditions.
        f = _one_def(t, "BiomeDef/%s" % BIOME, "biomeMapConditions")
        if _live(t):
            bmc = f.get("biomeMapConditions")
            if not isinstance(bmc, list):
                _unmeasured(t, "biomeMapConditions unreadable: %r" % (bmc,))
            if COND not in bmc:
                _fail("biomeMapConditions is %r: the grand cycle never starts on a Forge map" % bmc)

    with _comp(t, "biome_declares_ambient_heat", independent=True):
        # SOLAR_HEAT_EXPOSURE_1: the Forge's heat is ambient (steam/volcanic), where shade does nothing.
        f = _one_def(t, "BiomeDef/%s" % BIOME, "modExtensions", deep=True)
        if _live(t):
            ext = f.get("modExtensions")
            if ext in (None, "(no such field)") or not isinstance(ext, (dict, list)):
                _unmeasured(t, "get_defs cannot read modExtensions (got %r)" % (ext,))
            kinds = [str(x).lower() for x in _find_key(ext, "heatKind")]
            if not kinds:
                _fail("no RM_SunHeatExtension on the biome (MayRequire mandrake.rm.biomes matched nothing?): %s"
                      % list(_flat(ext))[:8])
            if kinds[0] != "ambient":
                _fail("heatKind is %r; the Forge's heat is ambient" % kinds)

    with _comp(t, "biome_lava_patchmakers", independent=True):
        # FORGE_LAVA_TERRAIN_1: the open lava the freeze crusts is laid by the biome's terrainPatchMakers.
        f = _one_def(t, "BiomeDef/%s" % BIOME, "terrainPatchMakers", deep=True)
        if _live(t):
            pm = f.get("terrainPatchMakers")
            if not isinstance(pm, (dict, list)):
                _unmeasured(t, "get_defs cannot serialise terrainPatchMakers (got %r)" % (pm,))
            if "LavaDeep" not in set(_flat(pm)):
                _fail("terrainPatchMakers has no LavaDeep: a Forge map generates no lava for the cycle to freeze: %s"
                      % sorted(set(_flat(pm)))[:10])


@suite.chain("settings")
def settings(t):
    """The Mod Settings screen: every field, each at its shipped default (read from the C# source), the assembly loaded,
    and the five FORGE_MECHANICS_1 scaffolding fields present but inert."""
    with _comp(t, "settings_at_shipped_defaults", independent=True, toggle="modEnabled"):
        if _live(t):
            _need_parse(t)
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="list")
        if _live(t):
            _ok(r, "mod_settings_field(list)")
            live = dict((f.get("name"), f.get("value")) for f in (r.get("fields") or []))
            if len(live) < len(SETTINGS_DEFAULTS):
                _fail("settings class lists %d fields, source declares %d: %s" % (
                    len(live), len(SETTINGS_DEFAULTS), sorted(set(SETTINGS_DEFAULTS) - set(live))))
            wrong = {}
            for k, want in SETTINGS_DEFAULTS.items():
                got = live.get(k)
                if isinstance(want, bool):
                    if str(got).lower() != str(want).lower():
                        wrong[k] = got
                elif _num(got) is None or abs(_num(got) - want) > 1e-6:
                    wrong[k] = got
            if wrong:
                _fail("settings not at shipped defaults (a previous run left them?): %s" % wrong)

    with _comp(t, "scaffolding_settings_declared_and_inert", independent=True):
        # tibannaTapRate, vaporColumnImmunity, towerScatterCount, dieOffRingDensity, ventWorkSpeedBonus change nothing
        # yet (the mod's own header). They must still exist and sit at defaults so the screen is honest; nothing
        # here pretends they have an effect.
        if _live(t):
            _need_parse(t)
            if sorted(SCAFFOLDING) != sorted(["tibannaTapRate", "vaporColumnImmunity", "towerScatterCount",
                                              "dieOffRingDensity", "ventWorkSpeedBonus"]):
                _fail("the scaffolding set changed (%s): a field was wired or added; extend this script" % SCAFFOLDING)


# ---------------------------------------------------------------- the grand cycle, default settings

def _declare_cycle_events(t):
    """The grand cycle's OWN telegraph letters (Glowing cracks = ThreatBig, The melt = ThreatSmall) and the gas
    wash's fires are the feature under test, not surprises. LIVE 2026-10-03 the watch read the letters as a raid
    (`raid_arrived`) and the wash's 17 fires as `fire_on_map`, which aborted every later component."""
    for lab in ("Glowing cracks", "The melt", "The freeze", LETTERS["hiss"]):
        t.expect("letter", {"label_contains": lab})
    t.expect("fire", lambda e: True)


@suite.chain("cycle_walk")
def cycle_walk(t):
    """One full grand cycle on a LavaDeep square, stepped with the mod's debug action and read back through
    independent tools. Order: start -> still heat -> gas wash -> rain (+floods) -> freeze -> growth -> cracks ->
    melt -> still heat. Everything on the pad is removed by teardown; the shared hazard scald is off for the long
    Rain windows (restored in finally)."""
    _enter(t)
    _declare_cycle_events(t)
    box = {}
    try:
        with _settings(t, HAZ_SETTINGS, environmentalDamageEnabled=False):
            with _comp(t, "site_ready_cycle"):
                _reset_pad(t)
                # flammable ground for the gas wash (it lights unroofed plants only)
                x, z = t.anchor
                t.bridge_call("jawa/set_plants", ops="Plant_Grass:%d,%d,16,4" % (x - 10, z + LAVA + 2), growth=1.0)
                _start_cycle(t)
                t.wait_ticks(130)

            with _comp(t, "cycle_starts_in_still_heat"):
                rep = _report(t)
                if _live(t):
                    box["base"] = rep
                    if rep["phase"] != "StillHeat" or not rep["endsIn"] > 0:
                        _fail("fresh cycle should sit in StillHeat with time left: %s" % rep["_line"])
                    if rep["cycles"] != 0 or rep["frozen"] != 0:
                        _fail("fresh cycle should have 0 cycles and 0 crust: %s" % rep["_line"])

            with _comp(t, "gas_wash_ignites", toggle="gasWashEnabled"):
                _advance(t)
                t.wait_ticks(130)
                rep = _report(t)
                if _live(t):
                    if rep["phase"] != "GasWash":
                        _fail("advance from StillHeat should enter GasWash, got %s" % rep["phase"])
                    if rep["gasIgnitions"] - box["base"]["gasIgnitions"] < 1:
                        _fail("the gas wash lit no ground: gasIgnitions %d -> %d (a wave needs an unroofed flammable "
                              "plant on the map)" % (box["base"]["gasIgnitions"], rep["gasIgnitions"]))
                    box["gas"] = rep["gasIgnitions"]

            with _comp(t, "rain_forces_boiling_weather_and_floods", toggle="cycleFloodingEnabled"):
                _advance(t)
                t.wait_ticks(130)
                rep0 = _report(t)
                w = _weather(t)
                if _live(t):
                    if rep0["phase"] != "Rain" or not rep0["inBurst"]:
                        _fail("Rain phase should be a forced burst: %s" % rep0["_line"])
                    if w != "RM_BoilingRain":
                        _fail("weather during Rain is %r, expected RM_BoilingRain" % w)
                t.wait_ticks(1400)         # the first release is due 0.5 h (1250 ticks) into the phase
                rep = _report(t)
                if _live(t):
                    box["rain_left"] = rep["endsIn"]
                if _live(t) and rep["floods"] - box["base"]["floods"] < 1:
                    _fail("no FlowWorks flood was released in the first 1500 ticks of the Rain: floods %d -> %d"
                          % (box["base"]["floods"], rep["floods"]))

            with _comp(t, "rain_erupts_dhuvvox_swarm", toggle="dhuvvoxSwarmEnabled"):
                # FORGE_CYCLE_MECHANICS_1 mass eruption: entering the Rain spawns the swarm (PROVISIONAL 60).
                rep = _report(t)
                if _live(t):
                    if "swarmErupted" not in rep:
                        _unmeasured(t, "report line has no swarm tokens: the deployed TheForge DLL predates the swarm")
                    erupted = rep["swarmErupted"] - (box["base"].get("swarmErupted") or 0)
                    if rep["swarmLive"] < 1 or erupted < 1:
                        _fail("the Rain woke no dhuvvox swarm: %s" % rep["_line"])

            with _comp(t, "freeze_crusts_lava", toggle="lavaFreezeEnabled"):
                _advance(t)                # into Freeze
                # A debug advance leaves the Rain's forced burst running (6-9 h), and the burst weather outranks the
                # freeze's steam; a natural cycle enters Freeze exactly when the burst ends. Move the clock to just
                # past the burst's end (the Freeze phase is >= 10 h long, so it is not crossed).
                if _live(t):
                    _jump(t, box["rain_left"] + 30)
                t.wait_ticks(130)
                w = _weather(t)
                _advance(t)                # FinishPhaseWork completes the whole freeze, then Growth
                cells = _layers(t, _lava(t))
                rep = _report(t)
                if _live(t):
                    if w != "Fog":
                        _fail("weather during the freeze is %r, expected Fog (RM_ForgePulse.freezeWeather)" % w)
                    tops, temps = _census(cells, "top"), _census(cells, "temp")
                    crust = sum(v for k, v in temps.items() if k in ("RM_BasaltShingle", "RM_PumiceRubble"))
                    if crust != LAVA * LAVA:
                        _fail("the freeze crusted %d of %d lava cells (temp census %r)" % (crust, LAVA * LAVA, temps))
                    if tops.get("LavaDeep") != LAVA * LAVA:
                        _fail("the lava under the crust was touched: top census %r" % tops)
                    if rep["phase"] != "Growth" or rep["frozen"] != LAVA * LAVA or rep["cellsFrozen"] < LAVA * LAVA:
                        _fail("report disagrees with the terrain read: %s" % rep["_line"])

            with _comp(t, "rain_end_reseals_swarm_with_signs", toggle="dhuvvoxSwarmEnabled"):
                # The rain is over: every surviving swarm member burrowed back (ash scar + one counted message).
                rep = _report(t)
                if _live(t):
                    if "swarmResealed" not in rep:
                        _unmeasured(t, "report line has no swarm tokens: the deployed TheForge DLL predates the swarm")
                    if rep["swarmLive"] != 0 or rep["swarmResealed"] - (box["base"].get("swarmResealed") or 0) < 1:
                        _fail("the swarm did not reseal when the rain ended: %s" % rep["_line"])

            with _comp(t, "crust_is_walkable", independent=True):
                x, z = t.anchor
                r = t.bridge_call("rimworld/get_cell_info", x=x + 5, z=z + 5)
                if _live(t):
                    _ok(r, "get_cell_info")
                    walk = list(_find_key(r, "walkable")) + list(_find_key(r, "passable"))
                    if not walk:
                        _unmeasured(t, "get_cell_info reports no walkability key: %s" % str(r)[:240])
                    if str(walk[0]).lower() != "true":
                        _fail("a frozen LavaDeep cell is not walkable (the whole point of the freeze): %s" % str(r)[:240])

            with _comp(t, "growth_blooms_floatstone", toggle="floatstoneBloomEnabled"):
                t.wait_ticks(130)          # DoPhaseWork seeds the gardens on the next 60-tick interval
                rep = _report(t)
                gardens = _things(t, "RM_FloatstoneGarden", _rs(_lava(t)))
                if _live(t):
                    if rep["phase"] != "Growth":
                        _fail("expected Growth, at %s" % rep["phase"])
                    if not 1 <= len(gardens) <= 10:
                        _fail("expected 1-10 floatstone gardens on the crust, found %d" % len(gardens))
                    if rep["gardensLive"] != len(gardens) or rep["gardensSpawned"] != len(gardens):
                        _fail("report says %d live / %d spawned, the map holds %d" % (
                            rep["gardensLive"], rep["gardensSpawned"], len(gardens)))
                    box["gardens"] = len(gardens)

            with _comp(t, "cracks_drift_gardens_and_glow", toggle="floatstoneBloomEnabled"):
                x, z = t.anchor
                # melt bait, placed while the crust still stands and the crust still holds them
                t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,20" % (x + 1, z + 1))
                box["rat"] = _spawn_wild(t, "Rat", x + 2, z + 8)
                _advance(t)                # into Cracks: gardens tear free
                rep = _report(t)
                left = _things(t, "RM_FloatstoneGarden", _rs(_lava(t)))
                if _live(t):
                    if rep["phase"] != "Cracks":
                        _fail("expected Cracks, at %s" % rep["phase"])
                    if left:
                        _fail("%d unharvested gardens still stand after the cracks began" % len(left))
                    if rep["gardensDrifted"] != box["gardens"]:
                        _fail("%d gardens bloomed but gardensDrifted is %d (a garden vanished unannounced)" % (
                            box["gardens"], rep["gardensDrifted"]))
                _advance(t)                # FinishPhaseWork: every crust cell becomes glowing cracks, then Melt
                cells = _layers(t, _lava(t))
                if _live(t):
                    temps = _census(cells, "temp")
                    if temps.get("RM_GlowingCrackCrust") != LAVA * LAVA:
                        _fail("expected all %d crust cells to glow, temp census %r" % (LAVA * LAVA, temps))

            with _comp(t, "melt_restores_lava_and_counts_losses", toggle="meltBackDestroys"):
                rep0 = _report(t)
                _advance(t)                # leaves Melt: the remaining crust melts in one batch, the cycle closes
                rep = _report(t)
                cells = _layers(t, _lava(t))
                steel = _things(t, "Steel", _rs(_pad(t)))
                pawns = _pawns(t, _rs(_pad(t)), "Rat")
                if _live(t):
                    if rep0["phase"] != "Melt":
                        _fail("expected Melt before the last advance, at %s" % rep0["phase"])
                    temps, tops = _census(cells, "temp"), _census(cells, "top")
                    if any(k for k in temps) or tops.get("LavaDeep") != LAVA * LAVA:
                        _fail("after the melt the lava should be bare again: temp %r top %r" % (temps, tops))
                    if rep["phase"] != "StillHeat" or rep["frozen"] != 0 or rep["cycles"] != 1:
                        _fail("the cycle did not close cleanly: %s" % rep["_line"])
                    if steel:
                        _fail("%d steel stack(s) survived the melt on the crust (meltBackDestroys is on)" % len(steel))
                    if rep["meltDestroyed"] < 1:
                        _fail("the steel is gone but meltDestroyed is %d: a loss vanished unannounced" % rep["meltDestroyed"])
                    alive = [p for p in pawns if p.get("id") == box["rat"] and not p.get("dead")]
                    if alive or rep["meltPawnsBurned"] < 1:
                        _fail("the rat on the crust was not burned (burned counter %d, still alive %s)" % (
                            rep["meltPawnsBurned"], bool(alive)))

            with _comp(t, "telegraph_letters_sent", independent=True, toggle="cycleTelegraphLetters"):
                labels = _letters(t)
                if _live(t):
                    for ph in ("Freeze", "Cracks", "Melt"):
                        if not labels.get(LETTERS[ph]):
                            _fail("no %r letter on the stack after a full cycle: %s" % (LETTERS[ph], sorted(labels)))
                    box["letters"] = dict(labels)
    finally:
        _wind_down(t)
        _teardown(t)


# ----------------------------------------------------------- the grand cycle, one toggle at a time

@suite.chain("cycle_arms")
def cycle_arms(t):
    """Each cycle toggle OFF, one pass each: the feature it names is gone and nothing else is. Every arm is independent
    (a failed arm does not hide the next) and begins by walking the cycle back to still heat, so it never inherits the
    previous arm's phase. Every arm restores its field in a finally; the pad's lava is permanent so every pass reuses it."""
    _enter(t)
    _declare_cycle_events(t)
    try:
        with _settings(t, HAZ_SETTINGS, environmentalDamageEnabled=False):
            with _comp(t, "site_ready_arms"):
                _reset_pad(t)
                x, z = t.anchor
                t.bridge_call("jawa/set_plants", ops="Plant_Grass:%d,%d,16,4" % (x - 10, z + LAVA + 2), growth=1.0)
                _start_cycle(t)
                t.wait_ticks(130)
                rep = _report(t)
                if _live(t) and rep["phase"] != "StillHeat":
                    _fail("arms need a fresh StillHeat: %s" % rep["_line"])

            with _comp(t, "gas_wash_off_no_ignitions", independent=True, toggle="gasWashEnabled"):
                _to_phase(t, "StillHeat")
                before = _report(t)
                with _settings(t, gasWashEnabled=False):
                    _advance(t)
                    t.wait_ticks(300)
                    rep = _report(t)
                if _live(t):
                    if rep["phase"] != "GasWash":
                        _fail("expected GasWash, at %s" % rep["phase"])
                    if rep["gasIgnitions"] != before["gasIgnitions"]:
                        _fail("gasWashEnabled=false but the wash still lit %d cells" % (rep["gasIgnitions"] - before["gasIgnitions"]))

            with _comp(t, "flooding_off_no_floods", independent=True, toggle="cycleFloodingEnabled"):
                _to_phase(t, "StillHeat")
                with _settings(t, cycleFloodingEnabled=False):
                    _to_phase(t, "Rain")
                    before = _report(t)
                    t.wait_ticks(1600)
                    rep = _report(t)
                if _live(t):
                    if rep["phase"] != "Rain":
                        _fail("expected Rain, at %s" % rep["phase"])
                    if rep["floods"] != before["floods"]:
                        _fail("cycleFloodingEnabled=false but %d flood(s) were released" % (rep["floods"] - before["floods"]))

            with _comp(t, "freeze_off_closes_cycle_early", independent=True, toggle="lavaFreezeEnabled"):
                _to_phase(t, "StillHeat")
                cycles0 = _report(t)["cycles"] if _live(t) else 0
                with _settings(t, lavaFreezeEnabled=False):
                    _to_phase(t, "Freeze")
                    _advance(t)            # nothing crusted: the cycle closes early
                    rep = _report(t)
                    temps = _census(_layers(t, _lava(t)), "temp")
                if _live(t):
                    if any(k for k in temps):
                        _fail("lavaFreezeEnabled=false but the lava crusted: %r" % temps)
                    if rep["phase"] != "StillHeat" or rep["cycles"] != cycles0:
                        _fail("with no crust the cycle should close early at StillHeat without counting a cycle: %s" % rep["_line"])

            with _comp(t, "bloom_off_no_gardens", independent=True, toggle="floatstoneBloomEnabled"):
                _to_phase(t, "StillHeat")
                _to_phase(t, "Freeze")
                with _settings(t, floatstoneBloomEnabled=False):
                    _advance(t)            # freeze finishes, Growth
                    t.wait_ticks(130)
                    rep = _report(t)
                    gardens = _things(t, "RM_FloatstoneGarden", _rs(_lava(t)))
                if _live(t):
                    if rep["phase"] != "Growth" or rep["frozen"] != LAVA * LAVA:
                        _fail("expected Growth on a full crust: %s" % rep["_line"])
                    if gardens:
                        _fail("floatstoneBloomEnabled=false but %d gardens bloomed" % len(gardens))

            with _comp(t, "melt_gentle_spares_pawn_and_items", independent=True, toggle="meltBackDestroys"):
                _to_phase(t, "StillHeat")
                _to_phase(t, "Growth")
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,20" % (x + 1, z + 1))
                rat = _spawn_wild(t, "Rat", x + 2, z + 8)
                before = _report(t)
                with _settings(t, meltBackDestroys=False):
                    _to_phase(t, "StillHeat")          # Cracks, Melt, close
                    rep = _report(t)
                    steel = _things(t, "Steel", _rs(_pad(t)))
                    pawns = _pawns(t, _rs(_pad(t)), "Rat")
                if _live(t):
                    if not steel:
                        _fail("meltBackDestroys=false but the steel is gone from the pad margin")
                    if rep["meltDestroyed"] != before["meltDestroyed"]:
                        _fail("meltBackDestroys=false but %d thing(s) were destroyed" % (rep["meltDestroyed"] - before["meltDestroyed"]))
                    if rep["meltPawnsBurned"] != before["meltPawnsBurned"]:
                        _fail("meltBackDestroys=false but the pawn was burned")
                    if not [p for p in pawns if p.get("id") == rat and not p.get("dead")]:
                        _fail("meltBackDestroys=false but the rat did not survive the melt")
                    if rep["meltRelocated"] <= before["meltRelocated"]:
                        _fail("gentle melt should RELOCATE survivors off the lava (meltRelocated %d -> %d)" % (
                            before["meltRelocated"], rep["meltRelocated"]))

            with _comp(t, "cycle_off_melts_back_gently", independent=True, toggle="grandCycleEnabled"):
                _to_phase(t, "StillHeat")
                _to_phase(t, "Growth")
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,20" % (x + 3, z + 3))
                before = _report(t)
                with _settings(t, grandCycleEnabled=False):
                    t.wait_ticks(200)       # crust left standing melts back at once, harming nothing
                    rep = _report(t)
                    temps = _census(_layers(t, _lava(t)), "temp")
                    steel = _things(t, "Steel", _rs(_pad(t)))
                if _live(t):
                    if any(k for k in temps):
                        _fail("grandCycleEnabled=false but crust still stands: %r" % temps)
                    if rep["meltDestroyed"] != before["meltDestroyed"] or not steel:
                        _fail("the switched-off cycle's melt-back harmed something (destroyed %d -> %d, steel left %d)" % (
                            before["meltDestroyed"], rep["meltDestroyed"], len(steel)))
                    if rep["phase"] != "Growth":
                        _fail("a switched-off cycle must not advance: phase %s" % rep["phase"])

            with _comp(t, "telegraph_off_sends_no_letters", independent=True, toggle="cycleTelegraphLetters"):
                _to_phase(t, "StillHeat")
                _to_phase(t, "Rain")
                base = _letters(t)
                with _settings(t, cycleTelegraphLetters=False):
                    _to_phase(t, "StillHeat")          # Freeze, Growth, Cracks, Melt letters would all fire here
                    now = _letters(t)
                if _live(t):
                    grew = dict((k, now.get(k, 0) - base.get(k, 0)) for k in LETTERS.values() if now.get(k, 0) != base.get(k, 0))
                    if grew:
                        _fail("cycleTelegraphLetters=false but letters arrived: %s" % grew)

            for name, field in (("cycle_gate_off_pulse_toggle_never_starts", "weatherPulseEnabled"),
                                ("cycle_gate_off_grand_cycle_toggle_never_starts", "grandCycleEnabled"),
                                ("cycle_gate_off_master_toggle_never_starts", "modEnabled")):
                with _comp(t, name, independent=True, toggle=field):
                    # the cycle rides the pulse: with the pulse gate, the cycle toggle or the master switch off, no
                    # phase ever starts (phaseEndTick stays -1). A fresh condition per arm.
                    with _settings(t, **{field: False}):
                        _start_cycle(t)
                        t.wait_ticks(200)
                        t0 = _ticks(t)
                        rep = _report(t)
                        if _live(t) and _ticks(t) != t0:
                            _unmeasured(t, "the clock moved between two reads: the game is not paused")
                        if _live(t) and t0 + rep["endsIn"] != -1:
                            _fail("%s=false but the cycle started a phase: %s" % (field, rep["_line"]))
                    # control inside the same component: back on, a fresh condition starts
                    _start_cycle(t)
                    t.wait_ticks(200)
                    rep = _report(t)
                    if _live(t) and not rep["endsIn"] > 0:
                        _fail("with %s back on the cycle still did not start: %s" % (field, rep["_line"]))
    finally:
        _wind_down(t)
        _teardown(t)


@suite.chain("still_heat_hiss")
def still_heat_hiss(t):
    """The hiss letter lands 1.5 h before the gas wash, and only while the gas wash is on (RM_GameCondition_ForgeCycle
    DoPhaseWork, StillHeat)."""
    _enter(t)
    _declare_cycle_events(t)
    try:
        with _comp(t, "site_ready_hiss"):
            _reset_pad(t)
            _start_cycle(t)
            t.wait_ticks(130)
            rep = _report(t)
            if _live(t):
                if rep["phase"] != "StillHeat":
                    _fail("need a fresh StillHeat: %s" % rep["_line"])
                if _letters(t).get(LETTERS["hiss"]):
                    _fail("precondition: a hiss letter is already on the stack")
        with _comp(t, "hiss_not_sent_with_gas_wash_off", toggle="gasWashEnabled"):
            rep = _report(t)
            with _settings(t, gasWashEnabled=False):
                _jump(t, (rep["endsIn"] if _live(t) else 0) - 3000)     # inside the 3,750-tick lead
                t.wait_ticks(130)
                got = _letters(t).get(LETTERS["hiss"], 0)
            if _live(t) and got:
                _fail("gasWashEnabled=false but the hiss letter arrived")
        with _comp(t, "hiss_letter_sent_before_gas_wash", toggle="gasWashEnabled"):
            t.wait_ticks(130)
            got = _letters(t).get(LETTERS["hiss"], 0)
            if _live(t) and got != 1:
                _fail("expected exactly one hiss letter inside the lead window, found %d" % got)
    finally:
        _wind_down(t)
        _teardown(t)


# ----------------------------------------------------------------------------------- the creatures

@suite.chain("dormancy")
def dormancy(t):
    """The dhokkur, julmox and dhuvvox keep the mountain's clock: sealed in the dry (inspect string), awake in the
    rain, the dhuvvox countdown and slowing, the dhokkur sealed again in the dry growth while the julmox and dhuvvox
    stay awake in the flash window. Wild pawns on a plain soil yard; the cycle is stepped with the debug action."""
    _enter(t)
    _declare_cycle_events(t)
    box = {"A": {}, "B": {}}
    try:
        with _settings(t, HAZ_SETTINGS, environmentalDamageEnabled=False):
            with _comp(t, "site_ready_dormancy"):
                _reset_pad(t)
                if _live(t):
                    # a debug-stepped Growth leaves its flash window (up to 66 h) and a stepped Rain its burst open,
                    # and the julmox and dhuvvox stay awake inside one: end the old cycle and move the clock past both
                    if _cond_present(t):
                        t.bridge_call("jawa/game_condition", action="end", condition=COND)
                        t.wait_ticks(120)
                    _jump(t, 170000)
                _start_cycle(t)
                t.wait_ticks(130)
                rep = _report(t)
                if _live(t) and (rep["phase"] != "StillHeat" or rep["inBurst"]):
                    _unmeasured(t, "need a StillHeat with no random burst running: %s" % rep["_line"])
                yx, yz, _, _ = _yard(t)
                for i, kind in enumerate(DORMANT_NATIVES):
                    box["A"][kind] = _spawn_wild(t, kind, yx + 1 + 2 * i, yz + 1)
                t.wait_ticks(600)          # first dormancy check seals a fresh pawn (no minimum-awake wait)

            with _comp(t, "natives_seal_in_still_heat", independent=True, toggle="cycleDormancyEnabled"):
                ins = _inspect(t, list(box["A"].values()))
                if _live(t):
                    awake = [k for k, i in box["A"].items() if not _has(ins[i], STILL_PHRASE)]
                    if awake:
                        _fail("not sealed in the dry still heat (inspect string lacks %r): %s" % (STILL_PHRASE, awake))

            with _comp(t, "dormancy_off_clears_sealed_line", independent=True, toggle="cycleDormancyEnabled"):
                # The comp's inspect string is null with the toggle off (RM_CompForgeCycleDormancy.CompInspectStringExtra), so
                # the line disappearing proves the toggle is read, NOT that the pawns woke: no bridge tool reads a pawn's
                # dormant state or job (walk: UNCOVERED, FORGE_PAWN_DORMANT_STATE_TOOL_1).
                with _settings(t, cycleDormancyEnabled=False):
                    t.wait_ticks(300)
                    ins = _inspect(t, list(box["A"].values()))
                if _live(t):
                    sealed = [k for k, i in box["A"].items() if _has(ins[i], STILL_PHRASE)]
                    if sealed:
                        _fail("cycleDormancyEnabled=false but the sealed line is still shown: %s" % sealed)

            with _comp(t, "fresh_natives_seal"):
                yx, yz, _, _ = _yard(t)
                for i, kind in enumerate(DORMANT_NATIVES):
                    box["B"][kind] = _spawn_wild(t, kind, yx + 1 + 2 * i, yz + 6)
                t.wait_ticks(600)
                ins = _inspect(t, list(box["B"].values()))
                rep = _report(t)
                if _live(t):
                    if rep["inBurst"]:
                        _unmeasured(t, "a random burst began while the fresh batch was sealing: %s" % rep["_line"])
                    awake = [k for k, i in box["B"].items() if not _has(ins[i], STILL_PHRASE)]
                    if awake:
                        _fail("a fresh batch did not seal in still heat: %s" % awake)

            with _comp(t, "rain_wakes_all_natives", toggle="cycleDormancyEnabled"):
                _advance(t)
                _advance(t)                # Rain
                t.wait_ticks(300)
                rep = _report(t)
                ins = _inspect(t, list(box["B"].values()))
                if _live(t):
                    if rep["phase"] != "Rain":
                        _fail("expected Rain, at %s" % rep["phase"])
                    still = [k for k, i in box["B"].items() if _has(ins[i], STILL_PHRASE)]
                    if still:
                        _fail("still sealed in the boiling rain: %s" % still)
                    box["rain_tick"] = _ticks(t)

            with _comp(t, "dhuvvox_clock_shows_countdown_and_slows", toggle="dhuvvoxClockEnabled"):
                dv = box["B"]["RM_Dhuvvox"]
                ins = _inspect(t, [dv])
                if _live(t) and not _has(ins[dv], RUN_PHRASE):
                    _fail("an awake dhuvvox shows no countdown: %s" % ins[dv])
                # the flash window opened when the burst began (5,000 ticks); jump to 400 ticks before its end
                rain_start = box.get("rain_tick", 0) - 300       # the Rain began 300 ticks before this read
                if _live(t):
                    _jump(t, max(1, rain_start + 5000 - 400 - _ticks(t)))
                t.wait_ticks(300)
                ins = _inspect(t, [dv])
                pawns = _pawns(t, _rs(_pad(t)), "RM_Dhuvvox", health=True)
                if _live(t):
                    row = next((p for p in pawns if p.get("id") == dv), None)
                    if row is None:
                        _fail("the dhuvvox is gone from the pad")
                    if "RM_DhuvvoxRunSlowing" not in set(_flat((row or {}).get("health"))):
                        _fail("no RM_DhuvvoxRunSlowing hediff inside the run's final quarter-hour: %s" % str((row or {}).get("health"))[:300])
                    if not _has(ins[dv], "slowing"):
                        _fail("inspect string lacks the 'Slowing.' line: %s" % ins[dv])

            with _comp(t, "clock_off_removes_slowing", toggle="dhuvvoxClockEnabled"):
                dv = box["B"]["RM_Dhuvvox"]
                with _settings(t, dhuvvoxClockEnabled=False):
                    t.wait_ticks(300)
                    ins = _inspect(t, [dv])
                    pawns = _pawns(t, _rs(_pad(t)), "RM_Dhuvvox", health=True)
                if _live(t):
                    row = next((p for p in pawns if p.get("id") == dv), None)
                    if row is not None and "RM_DhuvvoxRunSlowing" in set(_flat(row.get("health"))):
                        _fail("dhuvvoxClockEnabled=false but the slowing hediff is still on")
                    if _has(ins[dv], RUN_PHRASE):
                        _fail("dhuvvoxClockEnabled=false but the countdown still shows: %s" % ins[dv])

            with _comp(t, "dry_growth_seals_dhokkur_only"):
                # Freeze, Growth (the lava square freezes, so Growth exists), then past the burst's end and the
                # dhokkur's 2 h minimum-awake wait: the dhokkur seals (rain only); the julmox and dhuvvox, which also
                # wake in the flash window, stay awake.
                _to_phase(t, "Growth")
                _jump(t, 23000)
                t.wait_ticks(400)
                rep = _report(t)
                ins = _inspect(t, list(box["B"].values()))
                if _live(t):
                    if rep["phase"] != "Growth" or rep["inBurst"]:
                        _unmeasured(t, "need Growth with the burst over: %s" % rep["_line"])
                    if not _has(ins[box["B"]["RM_Dhokkur"]], STILL_PHRASE):
                        _fail("the dhokkur did not seal again in the dry growth phase")
                    for kind in ("RM_Julmox", "RM_Dhuvvox"):
                        if _has(ins[box["B"][kind]], STILL_PHRASE):
                            _fail("%s sealed during the flash window (awakeDuringFlashWindow)" % kind)
    finally:
        _wind_down(t)
        _teardown(t)


# --------------------------------------------------------------------------------- the voices

@suite.chain("voices")
def voices(t):
    """The four voices have a visual cue (a message naming the phase's sound) that ships OFF by default. The sounds
    themselves are audio and never judged here. Cues play only for the player's current map and only while the voices
    toggle is on."""
    _enter(t)
    _declare_cycle_events(t)
    haz = contextlib.ExitStack()
    try:
        # LIVE 2026-10-06: entering the Rain scalded all three colonists (RUT_Scald) and the watch aborted the cue
        # check as a surprise. The scald is cycle_walk's subject, not this chain's: hazard damage off, as there.
        haz.enter_context(_settings(t, HAZ_SETTINGS, environmentalDamageEnabled=False))
        with _comp(t, "site_ready_voices"):
            _reset_pad(t)
            _start_cycle(t)
            t.wait_ticks(130)
            rep = _report(t)
            if _live(t) and rep["phase"] != "StillHeat":
                _fail("need a fresh StillHeat: %s" % rep["_line"])
        with _comp(t, "voices_off_no_cue", toggle="forgeVoicesEnabled"):
            r0 = t.bridge_call("rimworld/list_messages", limit=200)
            with _settings(t, forgeVoicesEnabled=False, forgeVoicesVisualCues=True):
                _advance(t)
                t.wait_ticks(130)
                r = t.bridge_call("rimworld/list_messages", limit=200)
                if _live(t):
                    _ok(r, "list_messages")
                    seen = lambda x: sum(1 for s_ in _flat(x) if CUE_TEXT["GasWash"] in s_)
                    if seen(r) > seen(r0):
                        _fail("forgeVoicesEnabled=false but the gas-wash cue still appeared")
        with _comp(t, "visual_cue_message_names_phase", toggle="forgeVoicesVisualCues"):
            r0 = t.bridge_call("rimworld/list_messages", limit=200)
            with _settings(t, forgeVoicesEnabled=True, forgeVoicesVisualCues=True):
                _advance(t)                # Rain
                t.wait_ticks(130)
                r = t.bridge_call("rimworld/list_messages", limit=200)
                if _live(t):
                    _ok(r, "list_messages")
                    blob = list(_flat(r))
                    if not blob:
                        _unmeasured(t, "list_messages returned nothing at all (shape?): %s" % str(r)[:200])
                    before = sum(1 for s_ in _flat(r0) if CUE_TEXT["Rain"] in s_)
                    if sum(1 for s_ in blob if CUE_TEXT["Rain"] in s_) <= before:
                        _fail("no %r message after entering Rain with visual cues on (the voices' visual fallback)" % CUE_TEXT["Rain"])
    finally:
        _wind_down(t)
        _teardown(t)
        haz.close()


# --------------------------------------------------------------------------- spunstone & floatstone

@suite.chain("spunstone")
def spunstone(t):
    """Spunstone bonding is hidden until colonists have studied enough floatstone gardens (a Harmony postfix on
    ResearchProjectDef.IsHidden). The study loop itself needs researchers and mature gardens; this chain drives the
    mod's own `Spunstone: reveal now` and proves the hidden/visible/toggle states around it. Needs a FRESH game."""
    with _comp(t, "project_hidden_until_studied", toggle="spunstoneStudyEnabled"):
        r = t.bridge_call("jawa/research_availability", project="RM_SpunstoneBonding")
        if _live(t):
            _ok(r, "research_availability")
            if "isHidden" not in r:
                _unmeasured(t, "research_availability has no isHidden key: %s" % str(r)[:240])
            if r.get("isFinished"):
                _unmeasured(t, "RM_SpunstoneBonding is already finished: run on a FRESH game")
            rep = _act(t, "Spunstone: report knowledge")
            if rep.get("revealed"):
                _unmeasured(t, "spunstone is already revealed in this game: run on a FRESH game (%s)" % rep["_line"])
            if r.get("isHidden") is not True:
                _fail("RM_SpunstoneBonding is visible before any study (the Harmony postfix is not hiding it): %s" % str(r)[:240])

    with _comp(t, "study_toggle_off_shows_project", toggle="spunstoneStudyEnabled"):
        with _settings(t, spunstoneStudyEnabled=False):
            r = t.bridge_call("jawa/research_availability", project="RM_SpunstoneBonding")
            if _live(t):
                _ok(r, "research_availability")
                if r.get("isHidden") is not False:
                    _fail("spunstoneStudyEnabled=false but the project is still hidden: %s" % str(r)[:240])

    with _comp(t, "reveal_opens_project", toggle="spunstoneStudyEnabled"):
        _act(t, "Spunstone: reveal now")
        rep = _act(t, "Spunstone: report knowledge")
        r = t.bridge_call("jawa/research_availability", project="RM_SpunstoneBonding")
        letters = _letters(t)
        if _live(t):
            _ok(r, "research_availability")
            if not rep.get("revealed") or rep.get("projectHidden") is not False:
                _fail("reveal did not stick: %s" % rep["_line"])
            if r.get("isHidden") is not False:
                _fail("revealed but research_availability still says hidden: %s" % str(r)[:240])
            if not letters.get("Spunstone bonding"):
                _fail("no 'Spunstone bonding' letter after the reveal")


@suite.chain("floatstone_harvest")
def floatstone_harvest(t):
    """A mature floatstone garden yields RM_Floatstone when harvested (plant.harvestedThingDef)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_harvest"):
            _reset_pad(t)
            yx, yz, _, _ = _yard(t)
            t.bridge_call("jawa/set_plants", ops="RM_FloatstoneGarden:%d,%d,2,1" % (yx + 1, yz + 1), growth=1.0)
            r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=yx + 6, z=yz + 1, faction="player", count=1)
            if _live(t):
                _ok(r, "spawn_pawn(Colonist)")
                box["h"] = ((r.get("pawns") or [{}])[0]).get("id")
                if not box["h"]:
                    _fail("no handler id: %r" % r)
                t.bridge_call("jawa/pawn_need", pawn=box["h"], action="need", need="Food", level=1.0)
                t.bridge_call("jawa/pawn_need", pawn=box["h"], action="need", need="Rest", level=1.0)
                t.bridge_call("jawa/set_draft", pawnId=box["h"], drafted=False)
                gardens = _things(t, "RM_FloatstoneGarden", _rs(_yard(t)))
                if not gardens:
                    _fail("set_plants placed no floatstone garden (affordance/temperature rejected the cell?)")
                if _things(t, "RM_Floatstone", _rs(_pad(t))):
                    _fail("precondition: floatstone already on the pad")
                box["g"] = [g.get("id") for g in gardens]
        with _comp(t, "floatstone_garden_yields_floatstone"):
            for gid in box.get("g") or []:
                t.bridge_call("jawa/ordered_job", pawnId=box["h"], jobDef="Harvest", targetAId=gid, queue=True, waitTicks=60)
            t.wait_ticks(2500)
            if _live(t):
                made = _things(t, "RM_Floatstone", _rs(_pad(t)))
                _note(t, "RM_Floatstone stacks", [_stack(m) for m in made])
                if not made:
                    _fail("no RM_Floatstone after a forced harvest of %d mature garden(s)" % len(box["g"]))
    finally:
        _teardown(t)


@suite.chain("keelwork")
def keelwork(t):
    """Keel braces cut a gravship's fuel: the brace is a gravship facility whose fuelSavingsPercent the keelwork toggle
    rewrites (RM_KeelworkUtility.ApplySetting, run on WriteSettings). The real fuel-per-tile number needs a built
    gravship (not measurable here, see the walk). Reads the def through get_defs."""
    def savings(t):
        f = _one_def(t, "ThingDef/RM_FloatstoneKeelBrace", "comps", deep=True)
        if not _live(t):
            return None
        comps = f.get("comps")
        if not isinstance(comps, (dict, list)):
            _unmeasured(t, "get_defs cannot serialise the brace's comps (got %r)" % (comps,))
        vals = [_num(v) for v in _find_key(comps, "fuelSavingsPercent")]
        vals = [v for v in vals if v is not None]
        if not vals:
            _unmeasured(t, "no fuelSavingsPercent readable on the brace's comps: %s" % str(comps)[:240])
        return vals[0]

    with _comp(t, "keel_default_saving", independent=True, toggle="keelworkEnabled"):
        v = savings(t)
        if _live(t) and abs(v - 0.05) > 1e-6:
            _fail("brace fuelSavingsPercent is %r, shipped 0.05 (5%% per brace)" % v)

    with _comp(t, "keel_off_zeroes_saving", toggle="keelworkEnabled"):
        try:
            with _settings(t, keelworkEnabled=False):
                _apply(t)                  # WriteSettings -> ApplySetting
                v = savings(t)
                if _live(t) and abs(v) > 1e-9:
                    if abs(v - 0.05) > 1e-6:
                        _fail("keelworkEnabled=false and a dialog close left the brace saving at %r: neither the "
                              "shipped 0.05 nor 0" % v)
                    _unmeasured(t, "after keelworkEnabled=false and a dialog close the brace still saves 0.05: either "
                                   "ApplySetting is broken (mod) or the dialog did not reach RM_TheForgeMod.WriteSettings "
                                   "(harness; the composed mod hosts many Mod classes): inspect before classifying")
        finally:
            _apply_safely(t)
        v = savings(t)
        if _live(t) and abs(v - 0.05) > 1e-6:
            _fail("after restoring keelworkEnabled and a dialog close the brace saving is %r, not 0.05" % v)


    with _comp(t, "keel_ring_wired", independent=True, toggle="keelRingEnabled"):
        # the launch ring: a Harmony prefix on GravshipUtility.GenerateGravship (RM_Patch_KeelRing). Source-level proof
        # only; a real launch needs a built gravship (UNCOVERED in the walk: FORGE_KEEL_GRAVSHIP_SITE_1).
        src = _read_cs("RM_ForgeKeelwork.cs")
        need = ('typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship)', "keelRingEnabled", "RM_ForgeVoice_KeelRing")
        for n in need:
            if n not in src:
                _fail("RM_ForgeKeelwork.cs lacks %r: the launch ring is not wired" % n)
        if "RM_ForgeVoice_KeelRing" not in ALL_DEFNAMES:
            _fail("the RM_ForgeVoice_KeelRing SoundDef is not shipped in Defs/SoundDefs")

    with _comp(t, "dhuvvox_scuttle_wired", independent=True, toggle="dhuvvoxRunSoundEnabled"):
        # FORGE_DHUVVOX_SWARM_REMAINDER_1: source-level proof; the audio itself is UNMEASURED (no bridge tool hears).
        src = _read_cs("RM_CompForgeCycleDormancy.cs")
        for n in ("dhuvvoxRunSoundEnabled", "runSoundSlowFactor", "Props.runSound"):
            if n not in src:
                _fail("RM_CompForgeCycleDormancy.cs lacks %r: the scuttle is not wired" % n)
        if "RM_DhuvvoxScuttle" not in ALL_DEFNAMES:
            _fail("the RM_DhuvvoxScuttle SoundDef is not shipped in Defs/SoundDefs")

    with _comp(t, "spunstone_parts_source_floatstone_only_and_gated", independent=True,
               toggle="floatstoneDoorEnabled"):
        # SOURCE claim (no bridge tool reads a designator list or a stuff-category restriction): both parts accept
        # floatstone alone, are airtight outright (stone stuff is not), and each has a startup gate on its toggle.
        xml = _read_text(os.path.join("Defs", "ThingDefs_Buildings", "RM_SpunstoneParts.xml"))
        items = _read_text(os.path.join("Defs", "ThingDefs_Items", "RM_TheForgeItems.xml"))
        cat = _read_text(os.path.join("Defs", "StuffCategoryDefs", "RM_SpunstoneWeave.xml"))
        gate = _read_cs("RM_ForgeSpunstoneParts.cs")
        prj = _read_cs("RM_TheForge.csproj")
        checks = (
            ("<defName>RM_SpunstoneWeave</defName>" in cat, "the RM_SpunstoneWeave StuffCategoryDef is not shipped"),
            ("<li>RM_SpunstoneWeave</li>" in items, "RM_Floatstone does not carry RM_SpunstoneWeave: nothing can build the parts"),
            (xml.count('<stuffCategories Inherit="False">') == 2 and xml.count("<li>RM_SpunstoneWeave</li>") >= 2,
             "a spunstone part is not restricted to floatstone"),
            ("<isAirtight>true</isAirtight>" in xml, "the floatstone door is not airtight (stone stuff is not)"),
            ('"RM_FloatstoneDoor", RM_TheForgeSettings.Active(RM_TheForgeSettings.floatstoneDoorEnabled)' in gate,
             "the floatstone door's architect-menu gate is not keyed on floatstoneDoorEnabled"),
            ("designationCategory = null" in gate and "AllResolvedDesignators.RemoveAll" in gate,
             "the gate does not remove the designator"),
            ('Compile Include="RM_ForgeSpunstoneParts.cs"' in prj, "the csproj does not compile RM_ForgeSpunstoneParts.cs (a silent no-op)"),
        )
        if _live(t) or t.session is None:
            for ok, msg in checks:
                if not ok:
                    _fail(msg)
    with _comp(t, "spunstone_hull_gate_keyed_on_toggle", independent=True, toggle="spunstoneHullEnabled"):
        gate = _read_cs("RM_ForgeSpunstoneParts.cs")
        if (_live(t) or t.session is None) and \
                '"RM_SpunstoneHull", RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneHullEnabled)' not in gate:
            _fail("the spunstone hull's architect-menu gate is not keyed on spunstoneHullEnabled")
        if _live(t):
            _note(t, "spunstone parts UNMEASURED", "door speed and airtightness in play, and the menu gate after a restart: "
                  "no bridge tool reads them; the defs resolving is checked in defs_resolve")


@suite.chain("plume_fronts")
def plume_fronts(t):
    """FORGE_WHITE_PLUME_FRONTS_1: moving quench-steam fronts off the new crust. LIVE here: a front forms and moves
    (debug report), soaks the ground (Filth_Water puddle counter), and the two off-switches hold. NOT readable through
    any bridge tool, so named and never faked: the BlindSmoke gas density and its effect on a shot, a pawn's
    AmbientTemperature rise and the resulting heatstroke rate, and the adapted exemption in play. Those components
    check only that the SOURCE carries the wiring (a source claim, labelled as such); behaviour is UNMEASURED live."""
    _enter(t)
    _declare_cycle_events(t)
    box = {}

    def plumes(t):
        return _act(t, "Forge plumes: report")

    try:
        with _settings(t, HAZ_SETTINGS, environmentalDamageEnabled=False):
            with _comp(t, "site_ready_plume"):
                _reset_pad(t)
                _start_cycle(t)
                t.wait_ticks(130)
                _to_phase(t, "Freeze")
                t.wait_ticks(300)
                rep = _report(t)
                if _live(t) and not rep["frozen"] > 0:
                    _unmeasured(t, "no crust to launch a front from (frozen=0): %s" % rep["_line"])

            with _comp(t, "plume_front_spawns_and_lives", toggle="plumeFrontsEnabled"):
                _act(t, "Forge plumes: spawn a front")
                t.wait_ticks(120)
                d = plumes(t)
                if _live(t):
                    box["after_spawn"] = d
                    if d.get("plumeSpawned", 0) < 1 or d.get("plumeLive", 0) < 1:
                        _fail("a spawned front is not live two seconds later: %s" % d["_line"])
                    if not d.get("plumeCells", 0) > 0:
                        _fail("a live front covers no cells: %s" % d["_line"])

            with _comp(t, "plume_soaks_ground", toggle="plumeSoakEnabled"):
                t.wait_ticks(300)
                d = plumes(t)
                if _live(t):
                    box["soaked"] = d.get("plumePuddles", 0)
                    if box["soaked"] <= 0:
                        _fail("a front crossed crust for 7 s and left no Filth_Water puddle: %s" % d["_line"])

            with _comp(t, "soak_off_adds_no_puddles", toggle="plumeSoakEnabled"):
                with _settings(t, plumeSoakEnabled=False):
                    before = plumes(t)
                    t.wait_ticks(300)
                    after = plumes(t)
                    if _live(t) and after.get("plumePuddles", 0) != before.get("plumePuddles", 0):
                        _fail("plumeSoakEnabled=false but puddles grew %s -> %s" % (
                            before.get("plumePuddles"), after.get("plumePuddles")))

            with _comp(t, "fronts_off_clears_fronts", toggle="plumeFrontsEnabled"):
                with _settings(t, plumeFrontsEnabled=False):
                    _act(t, "Forge plumes: spawn a front")
                    t.wait_ticks(60)
                    d = plumes(t)
                    if _live(t) and d.get("plumeLive", 0) != 0:
                        _fail("plumeFrontsEnabled=false but fronts are still live: %s" % d["_line"])
    finally:
        _wind_down(t)
        _teardown(t)

    src = _read_cs("RM_ForgePlumeFronts.cs")
    prj = _read_cs("RM_TheForge.csproj")
    cyc = _read_cs("RM_GameCondition_ForgeCycle.cs")

    def need(cond, msg):
        if _live(t) or t.session is None:
            if not cond:
                _fail(msg)

    with _comp(t, "plume_source_launches_from_new_crust", independent=True, toggle="plumeFrontsEnabled"):
        need("NoteCrusted(c)" in cyc, "FreezeBatch does not call NoteCrusted: no front can ever form")
        need('Compile Include="RM_ForgePlumeFronts.cs"' in prj, "the csproj does not compile RM_ForgePlumeFronts.cs (a silent no-op)")
    with _comp(t, "plume_source_obscures_with_blind_smoke", independent=True, toggle="plumeObscureEnabled"):
        need("GasType.BlindSmoke" in src and "plumeObscureEnabled" in src, "no BlindSmoke gas laid under plumeObscureEnabled")
    with _comp(t, "plume_source_heat_is_ambient_temperature", independent=True, toggle="plumeHeatEnabled"):
        need("Thing.AmbientTemperature" in src or "nameof(Thing.AmbientTemperature)" in src, "no AmbientTemperature postfix")
        need("plumeHeatEnabled" in src, "the heat postfix is not gated on plumeHeatEnabled")
        need("AddHediff" not in src and "HediffDef" not in src, "a plume must feed vanilla heat, not add or write a hediff")
    with _comp(t, "plume_source_exempts_vapour_adapted", independent=True, toggle="plumeAdaptedExempt"):
        need("RM_CompVaporDrifter" in src and "plumeAdaptedExempt" in src, "the vapour-adapted exemption is not wired")
    with _comp(t, "plume_source_strength_scales", independent=True, toggle="plumeStrength"):
        need(src.count("plumeStrength") >= 2, "plumeStrength is not read by both the gas and the heat offset")
    if _live(t):
        _note(t, "plume UNMEASURED", "BlindSmoke density/accuracy, AmbientTemperature offset and heatstroke rate, adapted "
              "exemption in play: no bridge tool reads them")


@suite.chain("sky_pastures")
def sky_pastures(t):
    """FORGE_SKY_PASTURES_1: the vapour-column grid haze, ash spirals, column-aware hunting, the jossur stoop and the
    flier-selected highlight. NOTHING here is readable through a bridge tool (a section mesh, a fleck, a prey score, a
    flight state and a per-frame outline are all engine-internal and the flyer rule forbids a live flight hunt), so each
    component is a SOURCE claim, labelled as such, and the behaviour is recorded UNMEASURED live. Component names say
    what the source must carry; none claims the game was observed."""
    _enter(t)
    src = _read_cs("RM_ForgeSkyPastures.cs")
    prj = _read_cs("RM_TheForge.csproj")
    mod = _read_cs("RM_TheForgeMod.cs")
    dbg = _read_cs("RM_ForgeCycleDebugActions.cs")
    defs = _read_text(os.path.join("Defs", "ThingDefs_Races", "RM_TheForgeNatives.xml"))
    flag = _read_text(os.path.join("Defs", "MapMeshFlagDefs", "RM_SkyColumns.xml"))

    def need(cond, msg):
        if _live(t) or t.session is None:
            if not cond:
                _fail(msg)

    with _comp(t, "sky_source_grid_is_a_dirty_safe_section_layer", independent=True, toggle="skyColumnGridEnabled"):
        need("class SectionLayer_RM_SkyColumns : SectionLayer" in src, "no SectionLayer for the grid")
        need("relevantChangeTypes = (ulong)RM_TheForgeDefOf.RM_SkyColumns" in src, "the layer does not listen to its own flag")
        need("<defName>RM_SkyColumns</defName>" in flag and "RM_SkyColumns" in _read_cs("RM_TheForgeDefOf.cs"),
             "the MapMeshFlagDef or its DefOf is missing")
        need("catch (System.NullReferenceException)" in src and "SectionAt(loc) == null" in src,
             "dirtying does not guard the not-yet-built section slots (the MessyConduit first-load trap)")
        need("skyColumnGridEnabled" in src, "the grid is not gated on skyColumnGridEnabled")
        need('Compile Include="RM_ForgeSkyPastures.cs"' in prj, "the csproj does not compile RM_ForgeSkyPastures.cs (a silent no-op)")
    with _comp(t, "sky_source_spirals_are_cosmetic_flecks", independent=True, toggle="skyAshSpiralsEnabled"):
        need("FleckMaker.ThrowDustPuffThick" in src and "skyAshSpiralsEnabled" in src, "no ash flecks under skyAshSpiralsEnabled")
        need("CurrentViewRect" in src, "spirals are not limited to the camera view")
    with _comp(t, "sky_source_hunt_scores_columns", independent=True, toggle="skyColumnHuntEnabled"):
        need("nameof(FoodUtility.GetPreyScoreFor)" in src and "skyColumnHuntEnabled" in src, "no gated prey-score postfix")
        need("InColumn(prey.Position)" in src, "the prey score does not read the column field")
    with _comp(t, "sky_source_jossur_stoop_uses_flight_stats", independent=True, toggle="jossurStoopEnabled"):
        need("flight.StartFlying()" in src and "CanFlyNow" in src and "jossurStoopEnabled" in src, "the stoop is not a gated stock StartFlying")
        need("RimMandrake.TheForge.CompProperties_JossurStoop" in defs, "the jossur def does not carry the stoop comp")
        need("<MaxFlightTime>20</MaxFlightTime>" in defs, "the jossur lost its MaxFlightTime stat")
    with _comp(t, "sky_source_highlight_is_selection_only", independent=True, toggle="skyColumnHighlightEnabled"):
        need("GenDraw.DrawFieldEdges" in src and "skyColumnHighlightEnabled" in src, "no gated field-edge outline")
        need("SingleSelectedThing" in src and "MapComponentUpdate" in src, "the outline is not tied to the current selection")
    with _comp(t, "sky_source_debug_report_exists", independent=True):
        need("Forge sky: report" in dbg, "no sky report debug action")
    if _live(t):
        _note(t, "sky UNMEASURED", "the haze mesh, ash spirals, prey-score effect, a stoop in play and the outline: no bridge "
              "tool reads them and flyer flight is never live-hunted; run 'Forge sky: report' by hand for the counters")


# Chain order = registration order, kept explicit: the dormancy chain runs after every chain that steps a cycle, because
# it must move the clock past the stale flash window / burst those leave behind (see its site_ready).
_ORDER = ["log_clean", "defs_resolve", "def_wiring", "biome_wiring", "settings", "spunstone", "keelwork",
          "cycle_walk", "cycle_arms", "still_heat_hiss", "voices", "dormancy", "floatstone_harvest", "plume_fronts", "sky_pastures"]
suite.chains.sort(key=lambda c: _ORDER.index(c[0]))
