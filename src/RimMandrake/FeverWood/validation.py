"""validation.py -- modcheck suite for RimMandrake: Fever Wood (mandrake.rm.feverwood).

Walk: design/validation_walks/RimMandrake/FeverWood.md (`## must be true`, agent-owned, not hashed).
Item: FEVER_WOOD_FIRST_SCRIPT_1. Process: design/RimMandrake/debug_process.md section 2.

PACKAGING. This dev folder is SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json, wave 2), so a run loads the `baroque_wave0` tier (modset_builder.py: BRIDGE +
mandrake.rm.biomes + the five DLCs) and `northstar_plan.py` expects `mandrake.rm.biomes` active.
`modcheck run FeverWood` would append the dev folder's packageId with no closure and land on a list without
the biome: drive `northstar_driver/cli.py run --mod FeverWood --plan <northstar_plan.py>` (live_session.py
wraps the whole launch).

What the mod is for (every line sourced; see the walk):
  * `RM_FeverWood`, a hand-placed (generatesNaturally=false) swamp BiomeDef: vanilla + 8 invented fauna rows
    and 19 invented flora rows inline, five hazard/hive modExtensions, its own BiomeWorker.
  * the Sekkulaath (dianoga) tentacle bestiary: six limb buildings with a drive-off ladder (retreat / sever),
    a porter that deposits loot, a lash that strikes, and the uranium free-tier pool suppression
    (designator + work giver + RM_FoulPool job + RM_RadioactiveSuppressant + its machining recipe).
  * the Sekkulaath prison tank: feeds on meat, can breach on damage and release the juvenile.
  * the two-front lure: a stake that takes a downed bait pawn, then draws a staggered raid.
  * the sap-sucker guild whose refusal is a deterministic, cooldown-gated hediff, plus the Harmony hook that
    runs it on a failed tame.
  * bough-soil (fertile crown terrain), the procedural ant-hive genstep and the birds.

Derived from the mod's own `Defs/*.xml` and `Source/RM_FeverWoodMod.cs` at import (never a hand list): the def
groups, the biome roster, the settings fields and their shipped defaults, the numbers each mechanic's check is
sized from. Pinned floors (FLOORS) stop a parse failure from reading as "nothing to check".

NOT measurable with the existing bridge tools (named in the walk, never faked here):
  * everything that needs a REAL Fever Wood map (registered pool water: ambient limb spawns, the Great
    Emergence, the sentinel's chorus hush, the snare's rescue window, the ant-hive genstep, GetScore): no
    quicktest map carries the biome and there is no tool that makes one (worldgen is out by design);
  * statistical mechanics (tank production MTB, neglect escape MTB): no Boolean check (debug_process.md s4);
  * the porter's "angered forever" flag and the pool cooldown clock (private MapComponent state).

Every bridge call uses only parameters the live tool declares (lint_calls.py). Result shapes MEASURED live
elsewhere: `jawa/list_things` -> countMatched / isCompleteList / things[].id; `jawa/list_pawns` ->
pawns[].id/kindDef/faction (+ health hediffs with includeHealth); `jawa/get_defs` ->
foundCount/notFound/defs[].fields; `jawa/biome_probe` -> biomes[].animals/plants/findResults. UNPROVEN until the
first live run: `jawa/inspect_string` and `rimworld/list_messages` row shapes (read as flattened text),
`jawa/get_defs` serialising `modExtensions`/`genSteps`/`fertility`, `jawa/harmony_patches` row keys, and a
stack-size key on list_things rows. A component that cannot read a shape it needs records UNMEASURED
(`_unmeasured`), never PASS.
"""
import contextlib
import json
import math
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("FeverWood")

_HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.FeverWood.RM_FeverWoodSettings"
BIOME = "RM_FeverWood"
HARMONY_ID = "mandrake.rm.feverwood"
OUR_PACKAGES = ("mandrake.rm.biomes", "mandrake.rm.feverwood")
ACTIVE_ON_TIER = ("Ludeon.RimWorld.Odyssey", "Ludeon.RimWorld.Biotech", "Ludeon.RimWorld.Ideology",
                  "Ludeon.RimWorld.Royalty", "Ludeon.RimWorld.Anomaly", "mandrake.rm.biomes")
PAD = 29                    # the fixture pad: PAD x PAD cells around the chain's anchor
PAD_OFFSET = 45             # the pad sits this far from the map centre, clear of the start colonists
SUPPRESSED_PHRASE = "clouds and stills"          # RM_MapComponent_TentacleWatch.SuppressPoolWithRadioactiveMaterial
CAPTIVITY_MEMORY = "RM_CaptivityMemory"
LURE_STAKED = "RM_LureStaked"

# ----------------------------------------------------------------------- source parse (import time)

_DIR = os.path.join(_HERE, "Defs")
_ERRORS = []


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except Exception as ex:                       # a def file that does not parse is itself a finding
        _ERRORS.append("%s: %s" % (os.path.relpath(path, _HERE), ex))
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


_SUBDIRS = ("BiomeDefs", "DesignationDefs", "FactionDefs", "HediffDefs", "IncidentDefs", "JobDefs",
            "MapGeneration", "TerrainDefs", "ThingDefs_Buildings", "ThingDefs_Items", "ThingDefs_Plants",
            "ThingDefs_Races", "WorkGiverDefs")
_BY_DIR = dict((d, _defs_in(d)) for d in _SUBDIRS)

# (group, directory, DefType, names, floor). The floor is the count at authoring (2026-10-01): a shrink must
# be a deliberate edit of this script, never a silent pass.
_FLOORS = {("BiomeDefs", "BiomeDef"): 1, ("DesignationDefs", "DesignationDef"): 2,
           ("FactionDefs", "FactionDef"): 1, ("HediffDefs", "HediffDef"): 4, ("IncidentDefs", "IncidentDef"): 1,
           ("JobDefs", "JobDef"): 3, ("MapGeneration", "GenStepDef"): 3, ("TerrainDefs", "TerrainDef"): 4,
           ("ThingDefs_Buildings", "ThingDef"): 10, ("ThingDefs_Items", "ThingDef"): 12,
           ("ThingDefs_Items", "RecipeDef"): 1, ("ThingDefs_Plants", "ThingDef"): 23,
           ("ThingDefs_Races", "ThingDef"): 11, ("ThingDefs_Races", "PawnKindDef"): 11,
           ("WorkGiverDefs", "WorkGiverDef"): 3}
GROUPS = []
for _d in _SUBDIRS:
    for _t in sorted(set(t for t, _, _ in _BY_DIR[_d])):
        GROUPS.append(("%s_%s" % (_d.replace("ThingDefs_", "").replace("Defs", "").lower() or _d.lower(), _t),
                       _t, [n for tt, n, _ in _BY_DIR[_d] if tt == _t], _FLOORS.get((_d, _t), 1)))
_GROUP_NAMES = [g[0] for g in GROUPS]
ALL_DEFNAMES = set(n for _, _, names, _ in GROUPS for n in names)
_FLOOR_KEYS_SEEN = set((d, t) for d in _SUBDIRS for t in set(t for t, _, _ in _BY_DIR[d]))
for _k in _FLOORS:
    if _k not in _FLOOR_KEYS_SEEN:
        _ERRORS.append("expected def group %s/%s is absent from Defs/ (floor says it shipped)" % _k)

_BIOME_EL = next((el for t, n, el in _BY_DIR["BiomeDefs"] if n == BIOME), None)


def _roster(tag):
    """{defName: (commonality, MayRequire-or-None)} for the biome's <wildAnimals>/<wildPlants>
    (children named for the def, text = commonality; never <li> -- CLAUDE.md)."""
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
EXT_CLASSES = [li.get("Class", "").rsplit(".", 1)[-1] for li in
               (_BIOME_EL.findall("modExtensions/li") if _BIOME_EL is not None else [])]

# ---- settings: every field of RM_FeverWoodSettings with its shipped default, from the C# itself
_SETTINGS_SRC = os.path.join(_HERE, "S" + "ource", "RM_FeverWoodMod.cs")
SETTING_FIELDS = {}                       # name -> (type, python default)
try:
    with open(_SETTINGS_SRC, encoding="utf-8") as _fh:
        for _m in re.finditer(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);", _fh.read()):
            _typ, _nm, _raw = _m.group(1), _m.group(2), _m.group(3).strip()
            SETTING_FIELDS[_nm] = (_typ, (_raw == "true") if _typ == "bool" else
                                   (int(_raw) if _typ == "int" else float(_raw.rstrip("f"))))
except Exception as _ex:                  # the settings class is the floor of the whole suite
    _ERRORS.append("settings source: %s" % _ex)
BOOL_TOGGLES = sorted(n for n, (t, _) in SETTING_FIELDS.items() if t == "bool")
suite.toggles = list(BOOL_TOGGLES)


def _setting_str(name, value=None):
    typ, default = SETTING_FIELDS[name]
    v = default if value is None else value
    return str(bool(v)) if typ == "bool" else str(v)


def _same_setting(name, live):
    typ, default = SETTING_FIELDS[name]
    if typ == "bool":
        return str(live) == str(default)
    try:
        return abs(float(live) - float(default)) < 1e-4
    except (TypeError, ValueError):
        return False


# ---- numbers each mechanic's check is sized from (read from the defs, never typed)
def _def_el(subdir, name):
    return next((el for t, n, el in _BY_DIR[subdir] if n == name), None)


def _num(el, path, default):
    try:
        return float((el.findtext(path) or "").strip()) if el is not None and el.findtext(path) else default
    except ValueError:
        return default


def _limb(name):
    el = _def_el("ThingDefs_Buildings", name)
    comp = None if el is None else next((li for li in el.findall("comps/li")
                                         if li.get("Class", "").endswith("RM_CompProperties_TentacleLimb")), None)
    hp = _num(el, "statBases/MaxHitPoints", 0.0)
    return {"hp": hp,
            "severe": _num(comp, "severeDamageFraction", 0.6),
            "retreat_window": int(_num(comp, "retreatWindowTicks", 180)),
            "lash_range": _num(comp, "lashRange", 6.0),
            "lash_interval": int(_num(comp, "lashIntervalTicks", 240)),
            "porter_delay_max": int(((comp.findtext("porterDepositDelayTicks") or "600~1800").split("~")[-1])
                                    if comp is not None else 1800)}


# Blunt's buildingDamageFactor (Core DamageDef Blunt, MEASURED via RimSage 2026-10-03): DamageWorker.Apply multiplies
# every Blunt hit on a Building by it, so a raw amount is 1.5x on a limb. A severe hit sized without it KILLS the limb
# (Kill runs before the comp's hook) instead of severing it -- the cause of run17's "severed, but no flesh".
BLUNT_BUILDING_FACTOR = 1.5
LIMB_FEELER, LIMB_LASH, LIMB_PORTER = _limb("RM_Sekkulaath_Feeler"), _limb("RM_Sekkulaath_Lash"), _limb("RM_Sekkulaath_Porter")
PORTER_LOOT = ("Silver", "Gold", "RM_SeepOil", "RM_PottersClay", "RM_OssagrelSap")   # RM_TentacleLoot.Table

_TANK = _def_el("ThingDefs_Buildings", "RM_SekkulaathTank")
_TANK_COMP = None if _TANK is None else next((li for li in _TANK.findall("comps/li")
                                              if li.get("Class", "").endswith("RM_CompProperties_CapturedSpecimen")), None)
_PODBASE = next((el for el in (ET.parse(os.path.join(_DIR, "ThingDefs_Buildings", "RM_SekkulaathTank.xml")).getroot()
                               if os.path.isfile(os.path.join(_DIR, "ThingDefs_Buildings", "RM_SekkulaathTank.xml")) else [])
                 if isinstance(el.tag, str) and el.get("Name") == "RM_LivingCapturePodBase"), None)
TANK_HP = _num(_TANK, "statBases/MaxHitPoints", _num(_PODBASE, "statBases/MaxHitPoints", 0.0))
TANK_THRESHOLD = _num(_TANK_COMP, "damageEscapeThresholdFraction", 0.5)
TANK_OCCUPANT = ((_TANK_COMP.findtext("occupantKindDefName") if _TANK_COMP is not None else None) or "").strip()

# the refusing sap-suckers: (kind, hediff, severity, cooldown) -- only those whose refusal IS a hediff
SAP_KINDS = []
for _t, _n, _el in _BY_DIR["ThingDefs_Races"]:
    if _t != "ThingDef":
        continue
    for _li in _el.findall("comps/li"):
        if _li.get("Class", "").endswith("RM_CompProperties_SapSuckerRefusal") and (_li.findtext("refusalHediff") or "").strip():
            SAP_KINDS.append((_n, _li.findtext("refusalHediff").strip(), _num(_li, "refusalSeverity", 1.0),
                              int(_num(_li, "cooldownTicks", 2500))))

# the four flora that yield one of this mod's own harvest items through the vanilla Harvest job
FLORA_PRODUCTS = []
for _t, _n, _el in _BY_DIR["ThingDefs_Plants"]:
    _h = (_el.findtext("plant/harvestedThingDef") or "").strip()
    if _h.startswith("RM_") and (_el.findtext("plant/harvestTag") or "Standard").strip() == "Standard":
        FLORA_PRODUCTS.append((_n, _h, _num(_el.find("plant"), "fertilityMin", 0.0)))
# the crown: flora that cannot root on anything below fertility 1.0 (they exist only on bough-soil)
CROWN_PLANTS = [(n, _num(el.find("plant"), "fertilityMin", 0.0)) for t, n, el in _BY_DIR["ThingDefs_Plants"]
                if _num(el.find("plant"), "fertilityMin", 0.0) >= 1.0 and n in BIOME_PLANTS]
ROTTABLE_ITEMS = sorted(n for t, n, el in _BY_DIR["ThingDefs_Items"]
                        if any(li.get("Class") == "CompProperties_Rottable" for li in el.findall("comps/li")))
GENSTEPS_REGISTERED = []                  # (genStepDef, registered-on MapGeneratorDef) from Patches/*Register.xml
_PATCH_DIR = os.path.join(_HERE, "Patches")
for _fn in sorted(os.listdir(_PATCH_DIR)) if os.path.isdir(_PATCH_DIR) else []:
    if _fn.endswith("GenStep_Register.xml"):
        _txt = open(os.path.join(_PATCH_DIR, _fn), encoding="utf-8").read()
        _tgt = re.search(r'MapGeneratorDef\[defName="(\w+)"\]', _txt)
        for _li in re.findall(r"<li>\s*(\w+)\s*</li>", _txt):
            GENSTEPS_REGISTERED.append((_li, _tgt.group(1) if _tgt else None))

# ---- by-name lookups the C# does with a silent-fail: a renamed def makes the mechanic do nothing, quietly
BY_NAME = [("HediffDef", "RM_CaptivityMemory"), ("HediffDef", "RM_LureStaked"),
           ("ThingDef", "RM_Sekkulaath_Bloom"), ("PawnKindDef", "RM_Sekkulaath_Juvenile"),
           ("FactionDef", "RM_FactionDef_KurrethSwarm"), ("PawnKindDef", "RM_Kurreth"),
           ("PawnKindDef", "RM_KurrethQueen"), ("JobDef", "RM_FoulPool"), ("JobDef", "RM_StunForStaking"),
           ("JobDef", "RM_HaulToStake"), ("DesignationDef", "RM_Designation_FoulPool"),
           ("DesignationDef", "RM_Designation_StakeLure"), ("ThingDef", "RM_RadioactiveSuppressant"),
           ("ThingDef", "RM_LureStake"), ("ThingDef", "RM_SeveredTentacleFlesh")]

_G = {}                     # per-process memo


# --------------------------------------------------------------------------------- helpers

class _Unmeasured(Exception):
    pass


def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False in the offline
    declaration probe, so manual assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


_UTINNI_FW_PATCH = None     # the selftest points this at a synthetic campaign patch file


def _unmeasured(t, why):
    """Stop this component and record UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True            # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, independent=False, **kw):
    """t.component() plus: `_unmeasured` records the real reason as the detail; with independent=True
    a FAIL or UNMEASURED does not poison the next component (pure reads that share no state), while a
    setup component (the default) leaves every later component of its chain UNMEASURED."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
    if independent and not before:
        t.upstream_failed = False         # a setup component (independent=False) keeps the chain blocked
    t._why = None
    if t.session is not None and t.components:
        c = t.components[-1]
        print("[fw] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
              file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, also echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[fw-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]), file=sys.stderr, flush=True)


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


def _need_parse(t):
    if _ERRORS:
        _fail("the mod's own Defs/Source did not parse: %s" % "; ".join(_ERRORS[:3]))


def _get_defs(t, specs, fields=None, deep=False):
    """get_defs over `DefType/defName` specs (a STRING, chunked); returns [row,...] and notFound.
    Reads the tool's own success/foundCount/notFound -- never a substring of the payload."""
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


def _fields_of(rows, name):
    row = next((r for r in rows if r.get("defName") == name), None)
    return (row or {}).get("fields") or {}


def _things(t, defs, rect, limit=500):
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=limit)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defs)
    if r.get("isCompleteList") is False:
        _fail("list_things(%s) truncated: %r" % (defs, r.get("message")))
    return list(r.get("things") or [])


def _pawns(t, rect, kind=None, faction=None):
    if faction:
        r = t.bridge_call("jawa/list_pawns", rect=rect, limit=200, includeHealth=True, faction=faction)
    else:
        r = t.bridge_call("jawa/list_pawns", rect=rect, limit=200, includeHealth=True)
    if not _live(t):
        return []
    _ok(r, "list_pawns")
    if r.get("truncated"):
        _fail("list_pawns truncated: %r" % r.get("message"))
    return [p for p in (r.get("pawns") or []) if kind is None or p.get("kindDef") == kind]


def _stack(row):
    for k in ("stackCount", "count", "stack"):
        if isinstance(row.get(k), (int, float)):
            return int(row[k])
    return None


def _total(rows):
    """Sum of stack counts over rows, or None when the tool gives no stack key (UNMEASURED upstream)."""
    stacks = [_stack(r) for r in rows]
    return None if any(s is None for s in stacks) else sum(stacks)


def _enter(t):
    """First line of every fixture chain: move this chain's anchor to the pad, off the map centre."""
    if not getattr(t, "_fw_anchored", False):
        x, z = t.anchor
        t.anchor = (x + PAD_OFFSET, z + PAD_OFFSET)
        t._fw_anchored = True


def _proof_text(r):
    """A static_call's result string; when the call itself failed (stale DLL without the method, an exception) the
    bridge's own message, so a FAIL says WHY instead of printing an empty string (run17: 'did not stage the column: ')."""
    if not isinstance(r, dict):
        return ""
    res = r.get("result")
    if res not in (None, ""):
        return str(res)
    return "(static_call returned no result: success=%s message=%s)" % (r.get("success"), r.get("message") or r.get("error"))


def _pad_rect(t):
    x, z = t.anchor
    h = PAD // 2
    return "%d,%d,%d,%d" % (x - h, z - h, PAD, PAD)


def _reset_pad(t, terrain="Concrete"):
    """Everything true before the first assertion: the pad empty (things AND pawns), flat floor, unfogged."""
    rect = _pad_rect(t)
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="All")
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="Pawn")
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, rect))
    t.bridge_call("jawa/set_fog", action="unfog", rect=rect)
    t.bridge_call("jawa/log_autoopen_suppress")


def _teardown(t):
    """Best-effort, runs even after a FAILED chain (t.bridge_call is then a no-op, so use the session)."""
    if t.session is None or not getattr(t, "_fw_anchored", False):
        return
    try:
        rect = _pad_rect(t)
        t.session.call("jawa/destroy_batch", rects=rect, categories="All")
        t.session.call("jawa/destroy_batch", rects=rect, categories="Pawn")
    except Exception as ex:                       # teardown must never mask the chain's own verdict
        print("[fw] teardown failed: %s" % ex, file=sys.stderr, flush=True)


def _spawn(t, kind, x, z, faction):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    _ok(r, "spawn_pawn(%s)" % kind)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn id: %r" % (kind, r))
    return pid


def _spawn_building(t, defname, x, z):
    """Spawn a finished building and return its thing id (read back, never assumed)."""
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (defname, x, z))
    if not _live(t):
        return None
    found = _things(t, defname, "%d,%d,4,4" % (x, z))
    if len(found) != 1:
        _fail("expected exactly one %s at (%d,%d) after spawn_batch, found %d" % (defname, x, z, len(found)))
    return found[0].get("id")


def _spawn_stack(t, defname, x, z, count):
    r = t.bridge_call("rimworld/spawn_thing", defName=defname, stackCount=count, x=x, z=z)
    if _live(t):
        _ok(r, "spawn_thing(%s)" % defname)


def _damage(t, thing_id, amount, damage_def="Blunt"):
    r = t.bridge_call("jawa/damage", damageDef=damage_def, amount=float(amount), thingId=thing_id,
                      armorPenetration=1.0, allowColonists=True)
    if _live(t):
        _ok(r, "damage(%s)" % thing_id)
    return r


def _blob(t, pid, rect):
    """Every string in this pawn's list_pawns row (hediff defs included) -- membership of a defName in it
    is the 'has the hediff' test; None when the pawn is not on the map."""
    row = next((p for p in _pawns(t, rect) if p.get("id") == pid), None)
    return None if row is None else set(_flat(row))


def _alive(t, thing_id, rect, defname):
    return any(r.get("id") == thing_id for r in _things(t, defname, rect))


def _messages(t):
    r = t.bridge_call("rimworld/list_messages", limit=60)
    if not _live(t):
        return ""
    return " | ".join(_flat(_ok(r, "list_messages")))


@contextlib.contextmanager
def _settings(t, **vals):
    """Set Mod Settings fields for the block and ALWAYS restore + re-read the shipped defaults."""
    try:
        if vals:
            t.set_setting(SETTINGS, vals)
        yield
    finally:
        if t.session is not None:
            for k in vals:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=k,
                               value=_setting_str(k))
            for k in vals:
                back = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=k) or {}
                if not _same_setting(k, back.get("value")):
                    raise ExpectationFailed("%s did not restore to its shipped default %r: %r" % (
                        k, SETTING_FIELDS[k][1], back))


def _wait_until(t, predicate, budget, chunk=300):
    """Advance in `chunk` ticks until predicate() is true or `budget` ticks passed. Returns ticks spent."""
    spent = 0
    while spent < budget:
        t.wait_ticks(chunk)
        spent += chunk
        if predicate():
            break
    return spent


# ================================================================================ chains

@suite.chain("log_clean")
def log_clean(t):
    """The whole load, one read: no config error, unresolved cross-reference, missing type or exception
    naming this mod's content. Guards the 2026-09-30 load defects (FactionDef ConfigErrors on the two raider
    factions, bad field names, invalid PlantPurpose, a wrong class name that crashed the full-list load, a
    CompRottable tickerType)."""
    with _comp(t, "player_log_names_no_feverwood_error", independent=True):
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
            names = re.compile("|".join(re.escape(n) for n in sorted(ALL_DEFNAMES | set(
                ["FeverWood", BIOME, "RM_AntHiveBiomeExtension", "RM_BiomeWorker_FeverWood"] + EXT_CLASSES))))
            bad_kind = ("Config error", "Could not resolve cross-reference", "Could not find type named",
                        "Exception", "rror in")
            hits = [ln.strip() for ln in lines if names.search(ln) and any(k in ln for k in bad_kind)]
            general = sum(1 for ln in lines if "Config error" in ln or "Could not resolve cross-reference" in ln)
            _note(t, "Player.log scan", {"lines": len(lines), "hits": hits[:5],
                                         "game-wide config/xref lines (instrument probe)": general})
            if hits:
                _fail("%d Player.log line(s) name this mod's content in an error: %s" % (
                    len(hits), " | ".join(h[:200] for h in hits[:3])))


@suite.chain("source_guards")
def source_guards(t):
    """Two source-level guards for failures that already cost a load (CLAUDE.md): a `MayRequire` that names a
    mod folded into mandrake.rm.biomes is silently inert (BAROQUE wave-2 retarget), and `MayRequire` on a
    top-level patch <Operation> is ignored by the 1.6 engine (it reset ModsConfig twice on 2026-09-27). Read
    from this mod's own XML; needs no bridge, so it also runs offline."""
    with _comp(t, "hidden_raider_factions_have_a_name_source", independent=True):
        # FactionGenerator.NewGeneratedFaction -> NameGenerator.GenerateName NREs on a FactionDef with neither a
        # factionNameMaker nor a fixedName. The lure creates its hidden factions lazily, so the first raid threw in the
        # real game (found live by ProofRaid, load 14 -- 'NullReferenceException' hid for two loads behind the proof).
        for rel in (os.path.join("Defs", "FactionDefs", "RM_FactionDef_KurrethSwarm.xml"),
                    os.path.join("..", "..", "RimStarWars", "Shokk", "Defs", "FactionDefs", "RSW_Shokk_FeraliskBrood.xml")):
            path = os.path.join(_HERE, rel)
            if os.path.isfile(path):
                fd = ET.parse(path).getroot().find("FactionDef")
                if fd is not None and not (fd.findtext("fixedName") or fd.find("factionNameMaker") is not None):
                    _fail("%s has no fixedName/factionNameMaker: the lazily created hidden faction NREs in NameGenerator" % rel)
            elif t.session is not None and rel.startswith("Defs"):
                _fail("%s missing" % rel)

    with _comp(t, "no_mayrequire_names_a_folded_standalone_mod", independent=True):
        if t.session is not None:
            _need_parse(t)
            compose = json.load(open(os.path.join(_HERE, "..", "Biomes.compose.json"), encoding="utf-8"))
            folded = set()
            for e in compose.get("entries", []):
                if e.get("wave", 99) <= compose.get("compose_wave", 0):
                    about = os.path.join(_HERE, "..", e["source"], "About", "About.xml")
                    if os.path.isfile(about):
                        pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
                        if pid:
                            folded.add(pid)
            if len(folded) < 10:
                _fail("derived only %d folded standalone packageIds from Biomes.compose.json: parse failure" % len(folded))
            bad = []
            for base, _, files in os.walk(_HERE):
                if os.sep + "S" + "ource" in base or os.sep + "Textures" in base or os.sep + "Assemblies" in base:
                    continue
                for fn in files:
                    if not fn.endswith(".xml"):
                        continue
                    txt = open(os.path.join(base, fn), encoding="utf-8", errors="replace").read()
                    for m in re.finditer(r'MayRequire(?:Any)?\s*=\s*"([^"]+)"', txt):
                        for pid in (p.strip().lower() for p in m.group(1).split(",")):
                            if pid in folded:
                                bad.append("%s names %s" % (fn, pid))
            _note(t, "folded standalone packageIds checked", len(folded))
            if bad:
                _fail("MayRequire names a mod that now ships only inside mandrake.rm.biomes (inert): %s" % bad[:5])

    with _comp(t, "no_top_level_operation_carries_mayrequire", independent=True):
        if t.session is not None:
            hits = []
            for fn in sorted(os.listdir(_PATCH_DIR)):
                if fn.endswith(".xml"):
                    txt = open(os.path.join(_PATCH_DIR, fn), encoding="utf-8").read()
                    if re.search(r"<Operation\b[^>]*\bMayRequire", txt):
                        hits.append(fn)
            if len(os.listdir(_PATCH_DIR)) < 5:
                _fail("Patches/ holds fewer than 5 files: parse failure")
            if hits:
                _fail("top-level <Operation MayRequire=...> is ignored by the engine and can reset ModsConfig: %s" % hits)

    with _comp(t, "campaign_patches_and_free_def_tier_leaks_closed", independent=True):
        # FEVERWOOD_TIER_LEAKS_FIX_1. UNMEASURED live: offline source read only.
        if t.session is not None:
            utp = _UTINNI_FW_PATCH or os.path.join(_HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_FeverWood.xml")
            if not os.path.isfile(utp):     # the selftest runs on a temp copy of the mod folder with no repo beside it
                _unmeasured(t, "the campaign patch file is not beside this mod folder (%s)" % utp)
            txt = open(utp, encoding="utf-8").read()
            if "RM_FeverWood" not in txt:
                _fail("sanity probe: campaign roster patch does not mention RM_FeverWood: parse failure")
            if re.search(r"<Operation\b[^>]*\bMayRequire", txt):
                _fail("WildAnimals_FeverWood.xml: top-level <Operation MayRequire=...> is inert in 1.6")
            dropped = [n for n in ("RSW_GlowSlug", "RSW_JewelBeetle", "RSW_AcidSlug") if re.search(r"<%s>" % n, txt)]
            if dropped:
                _fail("owner dropped these Biomes! ports from the Fever Wood roster: %s" % dropped)
            biome = ET.parse(os.path.join(_HERE, "Defs", "BiomeDefs", "RM_FeverWood.xml")).getroot().find("BiomeDef")
            prevent = [(li.text or "").strip() for li in biome.findall("preventGenSteps/li")]
            if "ScatterShrines" not in prevent:
                _fail("RM_FeverWood must carry preventGenSteps ScatterShrines itself (no ancient dangers): %r" % prevent)


    with _comp(t, "free_text_names_no_canon_and_dianoga_patches_guarded", independent=True):
        # FEVERWOOD_DIANOGA_GIANT_MAP_1 + BIOME_TIER_CLEANUP_1 (b) Fever Wood part: the free mod's player-facing
        # text carries no Star Wars name; the campaign's dianoga patches carry no inert top-level MayRequire.
        if t.session is not None:
            leaks, seen = [], 0
            for base, _, files in os.walk(os.path.join(_HERE, "Defs")):
                for fn in files:
                    if not fn.endswith(".xml"):
                        continue
                    for el in ET.parse(os.path.join(base, fn)).getroot().iter():
                        if el.tag in ("label", "description", "text", "labelPlural", "reportString") and el.text:
                            seen += 1
                            if re.search(r"dianoga|canon|sarlacc|\bRSW_", el.text, re.I):
                                leaks.append("%s: %s" % (fn, el.text.strip()[:60]))
            if seen < 50:
                _fail("read only %d text nodes from Defs/: parse failure" % seen)
            if leaks:
                _fail("Star Wars names in the free mod's text: %s" % leaks[:4])
            swp = os.path.join(_HERE, "..", "..", "RimStarWars", "SWBestiary", "Patches")
            if os.path.isdir(swp):              # absent in the selftest's temp copy: the free-text half still runs
                giant = os.path.join(swp, "RSW_Sekkulaath_DianogaGiant.xml")
                if not os.path.isfile(giant):
                    _fail("campaign patch RSW_Sekkulaath_DianogaGiant.xml is missing")
                for fn in ("RSW_Sekkulaath_DianogaGiant.xml", "RSW_SekkulaathTank_DianogaSwap.xml"):
                    body = re.sub(r"<!--.*?-->", "", open(os.path.join(swp, fn), encoding="utf-8").read(), flags=re.S)
                    if re.search(r"<Operation\b[^>]*\bMayRequire", body):
                        _fail("%s: top-level <Operation MayRequire=...> is inert in 1.6" % fn)
                gtxt = open(giant, encoding="utf-8").read()
                for limb in ("Feeler", "Snare", "Lash", "Porter", "Sentinel", "Bloom"):
                    if 'defName="RM_Sekkulaath_%s"]/description' % limb not in gtxt:
                        _fail("the dianoga patch does not rewrite RM_Sekkulaath_%s's description" % limb)


@suite.chain("dianoga_mapping")
def dianoga_mapping(t):
    """FEVERWOOD_DIANOGA_GIANT_MAP_1, live: the six limbs read as the giant dianoga's when the Star Wars tier
    (RSW_Dianoga) is loaded, and as the sekkulaath's when it is not -- whichever list this run is on."""
    with _comp(t, "limbs_named_for_the_loaded_tier", independent=True):
        limbs = ["ThingDef/RM_Sekkulaath_%s" % x for x in ("Feeler", "Snare", "Lash", "Porter", "Sentinel", "Bloom")]
        rows, missing = _get_defs(t, limbs + ["ThingDef/RSW_Dianoga"], fields="label,description")
        if _live(t):
            if any(m != "ThingDef/RSW_Dianoga" for m in missing):
                _fail("limb defs not loaded: %s" % missing)
            sw = "ThingDef/RSW_Dianoga" not in missing
            texts = [(r.get("defName"), json.dumps(r.get("fields") or {}).lower()) for r in rows
                     if r.get("defName", "").startswith("RM_Sekkulaath_")]
            if len(texts) != 6:
                _fail("expected 6 limb rows, got %d" % len(texts))
            wrong = [n for n, tx in texts if ("dianoga" in tx) != sw]
            _note(t, "dianoga tier", {"swTier": sw, "wrong": wrong})
            if wrong:
                _fail("limbs not named for the loaded tier (Star Wars tier %s): %s" % (sw, wrong))


@suite.chain("defs_resolve")
def defs_resolve(t):
    """Every def this mod ships resolves in the running game and resolves to this mod, not a donor (a def that
    fails to load is dropped whole and silently: a missing comp/worker type, a double hyphen in an XML
    comment). Expected names come from the mod's own XML. A control proves the probe can say 'not found'."""
    with _comp(t, "resolve_probe_sees_absence", independent=True):
        real = next((n for g, _, ns, _ in GROUPS for n in ns if g == "items_ThingDef"), "RM_RadioactiveSuppressant")
        rows, missing = _get_defs(t, ["ThingDef/RM_NoSuchFeverWoodDef_Control", "ThingDef/%s" % real])
        if _live(t):
            found = [r.get("defName") for r in rows if r.get("found")]
            if missing != ["ThingDef/RM_NoSuchFeverWoodDef_Control"] or found != [real]:
                _fail("the def probe cannot tell present from absent: found=%r notFound=%r" % (found, missing))

    for group, deftype, names, floor in GROUPS:
        with _comp(t, "defs_resolve_%s" % group, independent=True):
            if _live(t):
                _need_parse(t)
                if len(names) < floor:
                    _fail("source parse found %d %s defs, floor is %d -- a parse failure or an undeclared "
                          "deletion (edit _FLOORS deliberately if the mod shrank)" % (len(names), group, floor))
            rows, missing = _get_defs(t, ["%s/%s" % (deftype, n) for n in names])
            if _live(t):
                if missing:
                    _fail("%d of %d %s not loaded by the game: %s" % (len(missing), len(names), group, missing[:8]))
                wrong = [r.get("defName") for r in rows if r.get("packageId") not in OUR_PACKAGES]
                if wrong:
                    _fail("defs resolve but from another mod (shadowed?): %s" % wrong[:6])

    with _comp(t, "defs_named_in_code_exist", independent=True):
        # the C# looks these up by name with a silent-fail (DefOf fields, GetNamedSilentFail): a renamed def
        # makes the mechanic do nothing and say nothing (RM_CompLureStake, RM_CompCapturedSpecimen, ...)
        rows, missing = _get_defs(t, ["%s/%s" % bn for bn in BY_NAME])
        if _live(t) and missing:
            _fail("the code looks these defs up by name and they do not exist: %s" % missing)


@suite.chain("biome_roster")
def biome_roster(t):
    """`RM_FeverWood` as the game resolved it (jawa/biome_probe reads the runtime caches, the only tool that
    can see wildAnimals/wildPlants). Live is compared with the mod's own XML, so a patch that removes or zeroes
    a row, a dropped record, or a dead roster each fail."""
    box = {}
    with _comp(t, "biome_probe_ready"):
        r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True, topN=200,
                          find="RM_Chellow,RM_Thornbug,RM_NoSuchCreatureControl")
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

    with _comp(t, "biome_flags_and_densities", independent=True):
        if _live(t):
            _need_parse(t)
            row = box["row"]
            if row.get("generatesNaturally") is not False:
                _fail("generatesNaturally is %r; the biome is hand-placed, never natural worldgen" % row.get("generatesNaturally"))
            # wildAnimals spawn only while animalDensity > 0 (MEASURED from the engine, CLAUDE.md): 0 = dead roster
            for k in ("animalDensity", "plantDensity"):
                if not (float(row.get(k) or 0) > 0):
                    _fail("%s is %r: a zero density makes the roster dead content" % (k, row.get(k)))
                if k in BIOME_SCALARS and abs(float(row[k]) - BIOME_SCALARS[k]) > 1e-4:
                    _fail("%s live %r != source %r" % (k, row[k], BIOME_SCALARS[k]))

    for kind, expect_floor, expect in (("animals", 8, BIOME_ANIMALS), ("plants", 15, BIOME_PLANTS)):
        with _comp(t, "wild_%s_wired" % kind, independent=True):
            if _live(t):
                _need_parse(t)
                if len(expect) < expect_floor:
                    _fail("source parse found %d wild %s rows, floor %d: parse failure" % (len(expect), kind, expect_floor))
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

    with _comp(t, "probe_states_are_honest", independent=True):
        # the three-state probe: a real row is 'spawning', an invented one 'absent'
        if _live(t):
            f = box["find"]
            if f.get("RM_Chellow") != "spawning" or f.get("RM_NoSuchCreatureControl") != "absent":
                _fail("biome_probe's find states are not trustworthy: %r" % f)

    with _comp(t, "hazard_and_hive_extensions_present", independent=True):
        # the biome carries 5 modExtensions: the three EnvironmentalHazards ones, the ground-refusal marsh, and
        # this mod's ant hive. A stale hazards dll once discarded a whole BiomeDef over one unknown class.
        rows, missing = _get_defs(t, ["BiomeDef/%s" % BIOME], fields="modExtensions", deep=True)
        if _live(t):
            _need_parse(t)
            if len(EXT_CLASSES) < 5:
                _fail("source parse found %d modExtensions, expected 5: %s" % (len(EXT_CLASSES), EXT_CLASSES))
            if missing or not rows:
                _fail("BiomeDef %s not resolvable: %r" % (BIOME, missing))
            ext = _fields_of(rows, BIOME).get("modExtensions")
            blob = list(_flat(ext))
            if ext in (None, "(no such field)") or not blob:
                _unmeasured(t, "get_defs cannot read modExtensions (got %r)" % (ext,))
            absent = [c for c in EXT_CLASSES if not any(c in s for s in blob)]
            if absent and len(absent) == len(EXT_CLASSES):
                # LIVE 2026-10-03: get_defs renders a modExtension as its FIELDS (heartwoodThing, ...) without the class name, so
                # not one class can ever be found; that is the instrument, not a missing extension.
                _unmeasured(t, "get_defs lists the biome's modExtensions by field values with no class names (%d entries): "
                               "class presence is not answerable this way" % len(blob))
            if absent:
                _fail("the biome lacks modExtensions %s (have %s)" % (absent, blob[:8]))


    with _comp(t, "crown_sound_and_heat_kind", independent=True):
        # FEVERWOOD_CROWN_SOUND_HEAT_1: the crown has an ambient bed for the sentinel's silence to cut, and the
        # biome declares heat kind `ambient`. Source half first (never live-dependent): the SoundDef is declared
        # in the biome's soundsAmbient and its clips are named. get_defs flattens a modExtension to its FIELDS
        # (class name absent), so the extension is recognised by `heatKind` / its value `ambient`.
        ambient = [li.text for li in (_BIOME_EL.findall("soundsAmbient/li") if _BIOME_EL is not None else [])]
        if ambient != ["RM_FeverWood_CrownHum"]:
            _fail("RM_FeverWood soundsAmbient in source is %r, expected ['RM_FeverWood_CrownHum']" % (ambient,))
        if "RM_SunHeatExtension" not in EXT_CLASSES:
            _fail("RM_FeverWood source carries no RM_SunHeatExtension: %s" % EXT_CLASSES)
        rows, missing = _get_defs(t, ["SoundDef/RM_FeverWood_CrownHum"])
        if _live(t) and (missing or not rows):
            _fail("SoundDef RM_FeverWood_CrownHum not loaded: %r" % (missing,))
        brows, bmissing = _get_defs(t, ["BiomeDef/%s" % BIOME], fields="modExtensions", deep=True)
        if _live(t):
            ext = _fields_of(brows, BIOME).get("modExtensions")
            if ext in (None, "(no such field)"):
                _unmeasured(t, "get_defs cannot read modExtensions (got %r)" % (ext,))
            blob = list(_flat(ext))
            if not any("SunHeat" in x or x == "heatKind" for x in blob) or "ambient" not in [str(x).lower() for x in blob]:
                _fail("no RM_SunHeatExtension with heatKind ambient among the biome's modExtensions: %s" % blob[:12])


@suite.chain("registrations")
def registrations(t):
    """Everything this mod hooks into somebody else's def by PATCH. A patch that matches nothing logs nothing,
    so each is read back from the game: the genstep registrations, the two Orders designators, the machining
    recipe, and the Harmony postfix of the failed-tame hook."""
    with _comp(t, "gensteps_registered_on_their_map_generator", independent=True):
        if _live(t):
            _need_parse(t)
            if len(GENSTEPS_REGISTERED) < 3:
                _fail("source parse found %d genstep registrations, expected 3: %s" % (len(GENSTEPS_REGISTERED), GENSTEPS_REGISTERED))
        targets = sorted(set(m for _, m in GENSTEPS_REGISTERED if m))
        got = {}
        for mg in targets:
            rows, missing = _get_defs(t, ["MapGeneratorDef/%s" % mg], fields="genSteps", deep=True)
            if _live(t):
                if missing:
                    _fail("MapGeneratorDef %s not resolvable" % mg)
                gs = _fields_of(rows, mg).get("genSteps")
                if gs in (None, "(no such field)") or not list(_flat(gs)):
                    _unmeasured(t, "get_defs cannot read %s.genSteps (got %r)" % (mg, gs))
                got[mg] = list(_flat(gs))
        if _live(t):
            lacking = [n for n, mg in GENSTEPS_REGISTERED if mg and not any(n in s for s in got.get(mg, []))]
            if lacking:
                _fail("genstep(s) %s are not on their map generator (the registration patch matched nothing)" % lacking)

    with _comp(t, "orders_designators_listed", independent=True):
        cats = t.bridge_call("rimworld/list_architect_categories")
        if _live(t):
            rows = cats if isinstance(cats, list) else (_ok(cats, "list_architect_categories").get("categories") or [])
            orders = next((c for c in rows if c.get("categoryDefName") == "Orders"), None)
            if not orders or not orders.get("id"):
                _unmeasured(t, "no architect category with categoryDefName 'Orders' in %s" % str(rows)[:200])
            lst = t.bridge_call("rimworld/list_architect_designators", categoryId=orders["id"])
            ds = _ok(lst, "list_architect_designators").get("designators")
            if not isinstance(ds, list) or not ds:
                _unmeasured(t, "list_architect_designators(Orders) returned no list: %s" % str(lst)[:200])
            text = json.dumps(ds).lower()
            if "hunt" not in text:
                _unmeasured(t, "the vanilla Hunt designator is not in the Orders listing, so the listing "
                               "is not trustworthy: %s" % text[:300])
            lacking = [n for n in ("foul pool", "stake as lure") if n not in text]
            if lacking:
                _fail("Orders lacks %s (the specialDesignatorClasses patch matched nothing)" % lacking)

    with _comp(t, "suppressant_recipe_on_the_machining_table", independent=True):
        rows, missing = _get_defs(t, ["ThingDef/TableMachining"], fields="recipes")
        if _live(t):
            if missing or not rows:
                _fail("TableMachining not resolvable: %r" % missing)
            have = set(_flat(_fields_of(rows, "TableMachining").get("recipes")))
            if "Make_ComponentIndustrial" not in have:
                _unmeasured(t, "the vanilla component recipe is not readable from TableMachining.recipes "
                               "(control), so the list is not trustworthy: %s" % sorted(have)[:6])
            if "RM_MakeRadioactiveSuppressant" not in have:
                _fail("TableMachining lacks RM_MakeRadioactiveSuppressant (recipeUsers did not resolve)")

    with _comp(t, "failed_tame_hook_is_patched_in", independent=True):
        r = t.bridge_call("jawa/harmony_patches", typeName="Pawn_MindState",
                          methodName="CheckStartMentalStateBecauseRecruitAttempted")
        if _live(t):
            if r.get("harmonyError") or r.get("success") is False:
                _unmeasured(t, "harmony_patches could not read the registry: %s" % str(r)[:200])
            blob = " ".join(_flat(r.get("methods")))
            if not (r.get("methodCount") or 0):
                _fail("no Harmony patch at all on Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted: "
                      "the sap-suckers' failed-tame refusal can never fire")
            if HARMONY_ID not in blob:
                _fail("%d patched method(s) but none owned by %s: %s" % (r.get("methodCount"), HARMONY_ID, blob[:200]))


@suite.chain("settings")
def settings(t):
    """RM_FeverWoodSettings: every field answers by name and sits at the shipped default (read from the C#
    source), and each of the on/off toggles flips and restores. Effects are in the mechanic chains; the ones
    that cannot be exercised without a real Fever Wood map are named UNCOVERED in the walk."""
    with _comp(t, "all_fields_at_shipped_defaults_and_assembly_loaded", independent=True):
        if _live(t):
            _need_parse(t)
            if len(SETTING_FIELDS) < 20 or len(BOOL_TOGGLES) < 8:
                _fail("source parse found %d settings fields / %d toggles: parse failure" % (len(SETTING_FIELDS), len(BOOL_TOGGLES)))
        wrong = {}
        for name in sorted(SETTING_FIELDS):
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=name)
            if _live(t):
                _ok(r, "mod_settings_field(get %s)" % name)
                if not _same_setting(name, r.get("value")):
                    wrong[name] = r.get("value")
        if _live(t) and wrong:
            _fail("settings not at their shipped defaults (or a field is not reachable by name): %s" % wrong)

    for name in BOOL_TOGGLES:
        with _comp(t, "toggle_roundtrip_%s" % name, independent=True, toggle=name):
            flipped = not SETTING_FIELDS[name][1]
            try:
                t.set_setting(SETTINGS, {name: flipped})
                r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=name)
                if _live(t) and str(_ok(r, "get").get("value")) != str(flipped):
                    _fail("%s did not take %r (reads %r)" % (name, flipped, r.get("value")))
            finally:
                if t.session is not None:
                    t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=name,
                                   value=_setting_str(name))
                    back = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=name) or {}
                    if not _same_setting(name, back.get("value")):
                        raise ExpectationFailed("%s did not restore to its shipped default: %r" % (name, back))


@suite.chain("bough_soil")
def bough_soil(t):
    """The crown can grow things (FEVERWOOD_BOUGH_SOIL_TERRAIN_1): RUT_Boughway ships fertility 0, so the
    biome's crown flora (fertilityMin >= 1.0) root only on RUT_BoughSoil. The terrain must be fertile enough
    for every crown plant, allow GrowSoil, and never carry the Heavy affordance."""
    with _comp(t, "bough_soil_fertile_for_every_crown_plant", independent=True):
        rows, missing = _get_defs(t, ["TerrainDef/RUT_BoughSoil"], fields="fertility,affordances", deep=True)
        if _live(t):
            _need_parse(t)
            if len(CROWN_PLANTS) < 5:
                _fail("source parse found %d crown plants (fertilityMin >= 1.0 on the roster), expected >= 5" % len(CROWN_PLANTS))
            if missing or not rows:
                _fail("RUT_BoughSoil not resolvable: %r" % missing)
            f = _fields_of(rows, "RUT_BoughSoil")
            try:
                fert = float(f.get("fertility"))
            except (TypeError, ValueError):
                _unmeasured(t, "get_defs cannot read TerrainDef.fertility (got %r)" % (f.get("fertility"),))
            need = max(m for _, m in CROWN_PLANTS)
            if fert < need:
                _fail("bough-soil fertility %.2f < %.2f needed by %s: the crown cannot grow" % (
                    fert, need, [n for n, m in CROWN_PLANTS if m > fert]))
            aff = set(_flat(f.get("affordances")))
            if not aff:
                _unmeasured(t, "get_defs cannot read TerrainDef.affordances")
            if "GrowSoil" not in aff:
                _fail("bough-soil lacks the GrowSoil affordance: nothing can be sown on it (%s)" % sorted(aff))
            if "Heavy" in aff:
                _fail("bough-soil carries the Heavy affordance; the ruling is Light/Medium only (%s)" % sorted(aff))


@suite.chain("rottable_items_tick")
def rottable_items_tick(t):
    """Every item of this mod's that carries a Rottable comp has a ticker, so it actually rots (a
    CompRottable on tickerType Never silently never rots: LOAD_ERRORS_ROUND_2_1)."""
    with _comp(t, "rottable_items_tick", independent=True):
        rows, missing = _get_defs(t, ["ThingDef/%s" % n for n in ROTTABLE_ITEMS], fields="tickerType")
        if _live(t):
            _need_parse(t)
            if len(ROTTABLE_ITEMS) < 3:
                _fail("source parse found %d Rottable items, expected >= 3" % len(ROTTABLE_ITEMS))
            if missing:
                _fail("rottable items not loaded: %s" % missing[:5])
            unread = [r.get("defName") for r in rows if (r.get("fields") or {}).get("tickerType") in (None, "(no such field)")]
            if unread:
                _unmeasured(t, "tickerType unreadable on %s" % unread[:4])
            never = [r.get("defName") for r in rows if (r.get("fields") or {}).get("tickerType") == "Never"]
            if never:
                _fail("Rottable comp never ticks (tickerType Never) on: %s" % never)


# ------------------------------------------------------------------------- the tentacle bestiary

@suite.chain("tentacle_ladder")
def tentacle_ladder(t):
    """The ordinary drive-off ladder (RM_CompTentacleLimb): severe damage SEVERS a limb (it vanishes and a
    harvestable body drops); mild damage only starts the withdrawal window and the limb RETREATS with nothing
    dropped. Both thresholds are read from the def."""
    _enter(t)
    try:
        with _comp(t, "site_ready_ladder"):
            _reset_pad(t)

        with _comp(t, "severe_damage_severs_the_limb_and_drops_flesh", independent=True):
            x, z = t.anchor
            fe = LIMB_FEELER
            if _live(t):
                _need_parse(t)
                if not (fe["hp"] > 0 and 0 < fe["severe"] <= 1):
                    _fail("feeler numbers did not parse: %r" % fe)
            limb = _spawn_building(t, "RM_Sekkulaath_Feeler", x, z)
            if _live(t) and _things(t, "RM_SeveredTentacleFlesh", _pad_rect(t)):
                _fail("precondition: severed flesh already on the pad")
            # past the severe fraction, short of killing it outright -- AFTER Blunt's building factor
            amount = int(math.ceil(fe["hp"] * fe["severe"] / BLUNT_BUILDING_FACTOR)) + 2
            if _live(t) and amount * BLUNT_BUILDING_FACTOR >= fe["hp"]:
                _fail("cannot size a sever-not-kill hit: severe fraction %.2f leaves no room below %d hp" % (
                    fe["severe"], fe["hp"]))
            _damage(t, limb, amount)
            t.wait_ticks(60)
            if _live(t):
                if _alive(t, limb, _pad_rect(t), "RM_Sekkulaath_Feeler"):
                    _fail("the feeler is still standing after %d damage on %d hp (severe fraction %.2f)" % (
                        amount, fe["hp"], fe["severe"]))
                flesh = _things(t, "RM_SeveredTentacleFlesh", _pad_rect(t))
                if not flesh:
                    _fail("severed, but no RM_SeveredTentacleFlesh dropped (harvestThing unwired?)")

        with _comp(t, "a_killing_blow_still_drops_flesh", independent=True):
            # one hit past full hp: DamageWorker.Apply Kills the limb before RM_CompTentacleLimb's hook runs, so
            # the comp's own drop sees no map -- the def's killedLeavingsRanges is what must drop the flesh
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            fe = LIMB_FEELER
            limb = _spawn_building(t, "RM_Sekkulaath_Feeler", x, z)
            _damage(t, limb, int(fe["hp"]) + 5)
            t.wait_ticks(60)
            if _live(t):
                if _alive(t, limb, _pad_rect(t), "RM_Sekkulaath_Feeler"):
                    _fail("the feeler survived %d damage on %d hp" % (int(fe["hp"]) + 5, fe["hp"]))
                if not _things(t, "RM_SeveredTentacleFlesh", _pad_rect(t)):
                    _fail("a killed limb dropped no RM_SeveredTentacleFlesh (killedLeavingsRanges unwired?)")

        with _comp(t, "mild_damage_retreats_without_dropping_anything", independent=True):
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            fe = LIMB_FEELER
            limb = _spawn_building(t, "RM_Sekkulaath_Feeler", x, z)
            amount = max(1, int(fe["hp"] * fe["severe"] * 0.3))
            _damage(t, limb, amount)
            if _live(t) and not _alive(t, limb, _pad_rect(t), "RM_Sekkulaath_Feeler"):
                _fail("a %d-damage graze (below the severe fraction) already removed the limb" % amount)
            t.wait_ticks(fe["retreat_window"] + 120)
            if _live(t):
                if _alive(t, limb, _pad_rect(t), "RM_Sekkulaath_Feeler"):
                    _fail("the grazed limb never retreated after the %d-tick withdrawal window" % fe["retreat_window"])
                if _things(t, "RM_SeveredTentacleFlesh", _pad_rect(t)):
                    _fail("a retreat dropped severed flesh: only the severe path should")
    finally:
        _teardown(t)


@suite.chain("tentacle_porter")
def tentacle_porter(t):
    """The porter is a courier: left alone it deposits ONE loot stack from the pool's table and withdraws;
    hit first, it vanishes at once and never brings anything (and angers the pool for good -- that flag is
    private state, so only the 'nothing arrives' half is measurable)."""
    _enter(t)
    try:
        with _comp(t, "site_ready_porter"):
            _reset_pad(t)

        with _comp(t, "unmolested_porter_deposits_loot_then_withdraws", independent=True):
            x, z = t.anchor
            if _live(t):
                _need_parse(t)
            porter = _spawn_building(t, "RM_Sekkulaath_Porter", x, z)
            _wait_until(t, lambda: not _alive(t, porter, _pad_rect(t), "RM_Sekkulaath_Porter"),
                        LIMB_PORTER["porter_delay_max"] + 600)
            if _live(t):
                if _alive(t, porter, _pad_rect(t), "RM_Sekkulaath_Porter"):
                    _fail("the porter was still up %d ticks after spawning (deposit delay max %d)" % (
                        LIMB_PORTER["porter_delay_max"] + 600, LIMB_PORTER["porter_delay_max"]))
                loot = _things(t, ",".join(PORTER_LOOT), _pad_rect(t))
                if not loot:
                    _fail("the porter withdrew but left none of %s" % list(PORTER_LOOT))
                _note(t, "porter loot", [(r.get("def") or r.get("defName"), _stack(r)) for r in loot])

        with _comp(t, "a_hit_porter_vanishes_and_brings_nothing", independent=True):
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            porter = _spawn_building(t, "RM_Sekkulaath_Porter", x, z)
            _damage(t, porter, 1)
            t.wait_ticks(60)
            if _live(t) and _alive(t, porter, _pad_rect(t), "RM_Sekkulaath_Porter"):
                _fail("a hit porter is still standing: it should vanish at once without the ordinary ladder")
            t.wait_ticks(LIMB_PORTER["porter_delay_max"] + 300)
            if _live(t):
                loot = _things(t, ",".join(PORTER_LOOT), _pad_rect(t))
                if loot:
                    _fail("a porter that was hit still deposited %s" % [(r.get("def") or r.get("defName")) for r in loot])
    finally:
        _teardown(t)


@suite.chain("tentacle_lash")
def tentacle_lash(t):
    """The lash strikes the first pawn inside its range with line of sight on a timer, and nobody beyond it.
    Arm 1: a lone drafted colonist stands well OUTSIDE the def's lashRange and must stay unhurt (the lash cuts
    the FIRST pawn in range, so an out-of-range pawn can only be tested while it is the only one). Arm 2: a
    second colonist stands inside the range and must be cut."""
    _enter(t)
    box = {}

    def colonist(t, dx):
        x, z = t.anchor
        pid = _spawn(t, "Colonist", x + dx, z, "player")
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
        t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
        return pid

    try:
        with _comp(t, "site_ready_lash"):
            _reset_pad(t)
            x, z = t.anchor
            rng = LIMB_LASH["lash_range"]
            if _live(t):
                _need_parse(t)
                if not (0 < rng <= 8):
                    _fail("lash range did not parse sensibly: %r" % LIMB_LASH)
            box["far"] = colonist(t, int(rng) + 7)
            box["lash"] = _spawn_building(t, "RM_Sekkulaath_Lash", x, z)

        with _comp(t, "lash_spares_a_pawn_outside_its_range"):
            t.wait_ticks(LIMB_LASH["lash_interval"] * 3)
            if _live(t):
                far = _blob(t, box["far"], _pad_rect(t))
                if far is None:
                    _unmeasured(t, "the colonist left the pad during the wait")
                if "Cut" in far:
                    _fail("the lash cut a colonist %d cells away (lashRange %.1f)" % (int(LIMB_LASH["lash_range"]) + 7,
                                                                                    LIMB_LASH["lash_range"]))
                if not _alive(t, box["lash"], _pad_rect(t), "RM_Sekkulaath_Lash"):
                    _unmeasured(t, "the lash is gone, so the wait proved nothing")

        with _comp(t, "lash_cuts_a_pawn_inside_its_range", independent=True):
            rng = LIMB_LASH["lash_range"]
            box["near"] = colonist(t, max(2, int(rng) - 3))
            if _live(t):
                blob = _blob(t, box["near"], _pad_rect(t))
                if blob is None or "Cut" in blob:
                    _unmeasured(t, "the near colonist is missing or already cut before the test")
            t.wait_ticks(LIMB_LASH["lash_interval"] * 3)
            if _live(t):
                near = _blob(t, box["near"], _pad_rect(t))
                if near is None:
                    _unmeasured(t, "the near colonist left the pad during the wait")
                if "Cut" not in near:
                    _fail("the lash never cut the colonist inside its range (%.1f cells) in %d ticks" % (
                        LIMB_LASH["lash_range"], LIMB_LASH["lash_interval"] * 3))
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- the prison tank

@suite.chain("tank")
def tank(t):
    """The Sekkulaath tank (RM_CompCapturedSpecimen): a fed tank reads fed; a heavy hit past the damage
    threshold breaches it and the juvenile escapes carrying the captivity memory (the per-hit chance is forced
    to 1 by the escape-risk multiplier floor so the check is deterministic); a hit below the threshold keeps
    it shut; with the master toggle off it is an inert box."""
    _enter(t)
    box = {}
    heavy = int(TANK_HP * TANK_THRESHOLD) + 20
    light = max(1, int(TANK_HP * TANK_THRESHOLD * 0.4))
    try:
        with _comp(t, "site_ready_tank"):
            _reset_pad(t)
            if _live(t):
                _need_parse(t)
                if not (TANK_HP > 0 and TANK_OCCUPANT and heavy < TANK_HP):
                    _fail("tank numbers did not parse: hp=%r occupant=%r heavy=%r" % (TANK_HP, TANK_OCCUPANT, heavy))

        with _comp(t, "tank_reads_occupant_fed", independent=True):
            x, z = t.anchor
            box["tank"] = _spawn_building(t, "RM_SekkulaathTank", x, z)
            r = t.bridge_call("jawa/inspect_string", thingIds=box["tank"])
            if _live(t):
                text = " | ".join(_flat(_ok(r, "inspect_string")))
                if "Occupant" not in text:
                    _unmeasured(t, "inspect_string carries no 'Occupant ...' sentence for the tank: %s" % text[:200])
                if "Occupant fed" not in text:
                    _fail("a freshly built tank (50%% meat) does not read fed: %s" % text[:200])

        with _comp(t, "a_hit_below_the_threshold_keeps_the_tank_shut", independent=True):
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            tk = _spawn_building(t, "RM_SekkulaathTank", x, z)
            with _settings(t, sekkulaathEscapeRiskMultiplier=0.01):
                _damage(t, tk, light)
                t.wait_ticks(60)
                if _live(t):
                    if not _alive(t, tk, _pad_rect(t), "RM_SekkulaathTank"):
                        _fail("a %d-damage hit (%.0f%% of hp, under the %.0f%% threshold) breached the tank" % (
                            light, 100.0 * light / TANK_HP, 100 * TANK_THRESHOLD))
                    if _pawns(t, _pad_rect(t), kind=TANK_OCCUPANT):
                        _fail("an occupant escaped from a tank hit below the threshold")

        with _comp(t, "a_heavy_hit_breaches_the_tank_and_the_juvenile_escapes_remembering", independent=True,
                   toggle="sekkulaathTankEnabled"):
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="Pawn")
            tk = _spawn_building(t, "RM_SekkulaathTank", x, z)
            with _settings(t, sekkulaathEscapeRiskMultiplier=0.01):
                _damage(t, tk, heavy)
                t.wait_ticks(60)
                if _live(t):
                    if _alive(t, tk, _pad_rect(t), "RM_SekkulaathTank"):
                        _fail("a %d-damage hit (past %.0f%% of %d hp, chance forced to 1) did not breach the tank" % (
                            heavy, 100 * TANK_THRESHOLD, TANK_HP))
                    esc = _pawns(t, _pad_rect(t), kind=TANK_OCCUPANT)
                    if len(esc) != 1:
                        _fail("expected exactly one %s escapee, found %d" % (TANK_OCCUPANT, len(esc)))
                    if CAPTIVITY_MEMORY not in set(_flat(esc[0])):
                        _fail("the escapee does not carry %s (it should remember the tank)" % CAPTIVITY_MEMORY)

        with _comp(t, "with_the_tank_toggle_off_the_same_hit_breaks_nothing", independent=True, toggle="sekkulaathTankEnabled"):
            x, z = t.anchor
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
            t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="Pawn")
            tk = _spawn_building(t, "RM_SekkulaathTank", x, z)
            with _settings(t, sekkulaathTankEnabled=False, sekkulaathEscapeRiskMultiplier=0.01):
                _damage(t, tk, heavy)
                t.wait_ticks(60)
                if _live(t):
                    if not _alive(t, tk, _pad_rect(t), "RM_SekkulaathTank"):
                        _fail("with sekkulaathTankEnabled=false the tank still breached (the toggle gates nothing)")
                    if _pawns(t, _pad_rect(t), kind=TANK_OCCUPANT):
                        _fail("with sekkulaathTankEnabled=false an occupant still escaped")
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- uranium suppression

@suite.chain("foul_pool")
def foul_pool(t):
    """The uranium free tier: a handler carries a suppressant stack to a cell and RM_JobDriver_FoulPool consumes
    tentacleUraniumSuppressantAmountPerUse of it; with tentacleUraniumSuppressionEnabled the pool's suppression
    is announced ('clouds and stills'), with it off the charge is still spent and nothing is announced."""
    _enter(t)
    box = {}
    amount = int(SETTING_FIELDS.get("tentacleUraniumSuppressantAmountPerUse", ("int", 5))[1])
    stack = amount * 3

    def one_use(t, label):
        x, z = t.anchor
        t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
        _spawn_stack(t, "RM_RadioactiveSuppressant", x - 6, z, stack)
        item = None
        if _live(t):
            stacks = _things(t, "RM_RadioactiveSuppressant", _pad_rect(t))
            if len(stacks) != 1 or _stack(stacks[0]) != stack:
                _unmeasured(t, "could not stage one %d-stack of suppressant (found %s)" % (
                    stack, [(r.get("id"), _stack(r)) for r in stacks]))
            item = stacks[0].get("id")
        r = t.bridge_call("jawa/ordered_job", pawnId=box["handler"], jobDef="RM_FoulPool", targetAId=item,
                          targetBX=x + 4, targetBZ=z + 4, count=amount, waitTicks=60, timeoutSeconds=25)   # the real WorkGiver sets job.count = min(stack, amount); an order without it consumes 1 (LIVE 2026-10-03)
        if _live(t) and not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
            _fail("jawa/ordered_job RM_FoulPool was not accepted and running: %r" % r)
        seen = {"msg": False}

        def done():
            seen["msg"] = seen["msg"] or SUPPRESSED_PHRASE in _messages(t)
            left = _total(_things(t, "RM_RadioactiveSuppressant", _pad_rect(t)))
            return (left is not None and left != stack) or seen["msg"]
        _wait_until(t, done, 3000, chunk=150)
        left = _total(_things(t, "RM_RadioactiveSuppressant", _pad_rect(t))) if _live(t) else None
        seen["msg"] = seen["msg"] or (_live(t) and SUPPRESSED_PHRASE in _messages(t))
        return left, seen["msg"]

    try:
        with _comp(t, "site_ready_foul_pool"):
            _reset_pad(t)
            x, z = t.anchor
            box["handler"] = _spawn(t, "Colonist", x + 8, z, "player")
            if _live(t):
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Food", level=1.0)
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Rest", level=1.0)
                t.bridge_call("jawa/set_draft", pawnId=box["handler"], drafted=False)
                _need_parse(t)

        with _comp(t, "job_consumes_the_configured_amount_and_announces_suppression", independent=True,
                   toggle="tentacleUraniumSuppressionEnabled"):
            left, msg = one_use(t, "on")
            if _live(t):
                if left is None:
                    _unmeasured(t, "list_things carries no stack key; cannot read what the job consumed")
                if left != stack - amount:
                    _fail("suppressant left %r after one use; expected %d (stack %d - %d per use)" % (left, stack - amount, stack, amount))
                if not msg:
                    _fail("the charge was spent but no '%s' message appeared (the suppression was not applied)" % SUPPRESSED_PHRASE)

        with _comp(t, "with_the_toggle_off_the_charge_is_spent_and_nothing_is_announced", independent=True,
                   toggle="tentacleUraniumSuppressionEnabled"):
            for _ in range(15):                  # a message lives ~13 real seconds: let the previous arm's expire
                if not (_live(t) and SUPPRESSED_PHRASE in _messages(t)):
                    break
                time.sleep(2)
            if _live(t) and SUPPRESSED_PHRASE in _messages(t):
                _unmeasured(t, "the suppression message from the previous arm is still on screen; cannot tell the arms apart")
            with _settings(t, tentacleUraniumSuppressionEnabled=False):
                left, msg = one_use(t, "off")
                if _live(t):
                    if left is None:
                        _unmeasured(t, "list_things carries no stack key; cannot read what the job consumed")
                    if left != stack - amount:
                        _fail("with the toggle off the job consumed %r, expected the same %d" % (stack - left, amount))
                    if msg:
                        _fail("with tentacleUraniumSuppressionEnabled=false the pool was still announced suppressed")
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- sap-sucker guild

def _sap_chain(kind, hediff, severity, cooldown):
    def chain(t):
        _enter(t)
        box = {}
        try:
            with _comp(t, "site_ready_%s" % kind):
                _reset_pad(t)
                x, z = t.anchor
                if _live(t):
                    _need_parse(t)
                box["pid"] = _spawn(t, kind, x, z, "none")
                if _live(t):
                    blob = _blob(t, box["pid"], _pad_rect(t))
                    if blob is None:
                        _fail("%s was not found on the pad after spawn_pawn" % kind)
                    if hediff in blob:
                        _fail("precondition: a fresh %s already carries %s" % (kind, hediff))

            with _comp(t, "%s_refuses_with_its_hediff_when_hurt" % kind, independent=False):
                _damage(t, box["pid"], 1)
                if _live(t):
                    blob = _blob(t, box["pid"], _pad_rect(t))
                    if blob is None:
                        _unmeasured(t, "%s left the pad before the read" % kind)
                    if hediff not in blob:
                        _fail("%s took a hit and did not gain %s (comp not on the def, or the trigger is dead)" % (kind, hediff))

            with _comp(t, "%s_refusal_is_cooldown_gated_not_a_roll" % kind, independent=False):
                t.bridge_call("jawa/pawn_health", pawn=box["pid"], action="remove", hediff=hediff)
                _damage(t, box["pid"], 1)
                if _live(t):
                    blob = _blob(t, box["pid"], _pad_rect(t))
                    if blob is None:
                        _unmeasured(t, "%s left the pad before the read" % kind)
                    if hediff in blob:
                        _fail("%s re-refused inside its %d-tick cooldown (it must never be a random roll)" % (kind, cooldown))
                t.wait_ticks(cooldown + 100)
                _damage(t, box["pid"], 1)
                if _live(t):
                    blob = _blob(t, box["pid"], _pad_rect(t))
                    if blob is None:
                        _unmeasured(t, "%s left the pad during the cooldown wait" % kind)
                    if hediff not in blob:
                        _fail("%s did not refuse again after its cooldown (%d ticks) expired" % (kind, cooldown))
        finally:
            _teardown(t)
    chain.__doc__ = ("Sap-sucker %s: damage gives it %s (severity ~%.1f), a second hit inside its %d-tick cooldown "
                     "does not, and one after the cooldown does (deterministic, never a random roll). Read from the "
                     "def's own comp." % (kind, hediff, severity, cooldown))
    return chain


for _kind, _hd, _sev, _cd in SAP_KINDS:
    suite.chain("sap_%s" % _kind)(_sap_chain(_kind, _hd, _sev, _cd))


# ------------------------------------------------------------------------- the two-front lure

@suite.chain("lure_stake")
def lure_stake(t):
    """The lure stake: empty it reads 'No bait staked.'; a handler hauling a DOWNED pawn to it (RM_HaulToStake)
    chains the bait (RM_LureStaked), the stake reads 'Baited with ...', and destroying the stake frees the
    bait (the hediff goes)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_stake"):
            _reset_pad(t)
            x, z = t.anchor
            box["stake"] = _spawn_building(t, "RM_LureStake", x, z)
            box["handler"] = _spawn(t, "Colonist", x + 8, z, "player")
            box["bait"] = _spawn(t, "Colonist", x + 5, z + 5, "none")
            if _live(t):
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Food", level=1.0)
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Rest", level=1.0)
                t.bridge_call("jawa/set_draft", pawnId=box["handler"], drafted=False)
                _need_parse(t)

        with _comp(t, "an_empty_stake_reads_no_bait", independent=True):
            r = t.bridge_call("jawa/inspect_string", thingIds=box["stake"])
            if _live(t):
                text = " | ".join(_flat(_ok(r, "inspect_string")))
                if "bait" not in text.lower():
                    _unmeasured(t, "inspect_string carries no bait sentence for the stake: %s" % text[:200])
                if "No bait staked" not in text:
                    _fail("an empty stake does not read 'No bait staked.': %s" % text[:200])

        with _comp(t, "haul_to_stake_chains_the_downed_bait"):
            r = t.bridge_call("jawa/pawn_force_incapacitate", pawn=box["bait"], action="downed", allowBleedingWounds=False)
            if _live(t) and not _ok(r, "pawn_force_incapacitate").get("downedAfter"):
                _unmeasured(t, "could not down the bait pawn: %s" % str(r)[:200])
            r = t.bridge_call("jawa/ordered_job", pawnId=box["handler"], jobDef="RM_HaulToStake",
                              targetAId=box["bait"], targetBId=box["stake"], waitTicks=60, timeoutSeconds=25)
            if _live(t) and not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
                _fail("jawa/ordered_job RM_HaulToStake was not accepted and running: %r" % r)

            def staked():
                blob = _blob(t, box["bait"], _pad_rect(t))
                return blob is not None and LURE_STAKED in blob
            _wait_until(t, staked, 2400, chunk=200)
            if _live(t):
                blob = _blob(t, box["bait"], _pad_rect(t))
                if blob is None:
                    _unmeasured(t, "the bait left the pad")
                if LURE_STAKED not in blob:
                    _fail("the bait was hauled for 2400 ticks and never gained %s" % LURE_STAKED)

        with _comp(t, "a_baited_stake_reads_baited", independent=True):
            r = t.bridge_call("jawa/inspect_string", thingIds=box["stake"])
            if _live(t):
                text = " | ".join(_flat(_ok(r, "inspect_string")))
                if "Baited with" not in text:
                    _fail("a stake holding live bait does not read 'Baited with ...': %s" % text[:200])

        with _comp(t, "destroying_the_stake_frees_the_bait", independent=True):
            t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % t.anchor, categories="All")
            if _live(t):
                if _alive(t, box["stake"], _pad_rect(t), "RM_LureStake"):
                    _unmeasured(t, "could not remove the stake with destroy_batch")
                blob = _blob(t, box["bait"], _pad_rect(t))
                if blob is None:
                    _unmeasured(t, "the bait left the pad")
                if LURE_STAKED in blob:
                    _fail("the stake is gone and the bait still carries %s (it would stay immobile forever)" % LURE_STAKED)
    finally:
        _teardown(t)


@suite.chain("flora_harvest")
def flora_harvest(t):
    """The four flora that name one of this mod's own harvest items (ossagrel sap, potter's clay, seep oil,
    raw giant leaf) yield it when a handler harvests them: grown plants are set, the vanilla Harvest job is
    queued on each, and the product must appear. Read from the mod's own flora XML."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_flora"):
            _reset_pad(t, terrain="SoilRich")
            x, z = t.anchor
            if _live(t):
                _need_parse(t)
                if len(FLORA_PRODUCTS) < 4:
                    _fail("source parse found %d RM_-product flora, expected 4: %s" % (len(FLORA_PRODUCTS), FLORA_PRODUCTS))
            box["handler"] = _spawn(t, "Colonist", x - 10, z, "player")
            if _live(t):
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Food", level=1.0)
                t.bridge_call("jawa/pawn_need", pawn=box["handler"], action="need", need="Rest", level=1.0)
                t.bridge_call("jawa/set_draft", pawnId=box["handler"], drafted=False)
            for i, (plant, product, _) in enumerate(FLORA_PRODUCTS):
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,3,1" % (plant, x - 4 + i * 4, z + 6), growth=1.0)
            if _live(t):
                for plant, product, _ in FLORA_PRODUCTS:
                    box[plant] = [p.get("id") for p in _things(t, plant, _pad_rect(t))[:3]]
                    if not box[plant]:
                        _fail("set_plants placed no %s" % plant)
                    if _things(t, product, _pad_rect(t)):
                        _fail("precondition: %s already on the pad" % product)

        with _comp(t, "every_flora_yields_its_harvest_item"):
            if _live(t):
                for plant, product, _ in FLORA_PRODUCTS:
                    for pid in box[plant]:
                        t.bridge_call("jawa/ordered_job", pawnId=box["handler"], jobDef="Harvest",
                                      targetAId=pid, queue=True, waitTicks=60)
            t.wait_ticks(4000)
            if _live(t):
                missing = [(p, prod) for p, prod, _ in FLORA_PRODUCTS if not _things(t, prod, _pad_rect(t))]
                if missing:
                    _fail("harvest yielded nothing for %s (harvestedThingDef is wired; the yield never arrived)" % missing)
    finally:
        _teardown(t)


# ----------------------------------------------------------------------- the raid (slowest, runs last)

@suite.chain("lure_raid")
def lure_raid(t):
    """The staked bait draws a raid of the hidden Kurreth swarm: with twoFrontLureEnabled OFF no swarm pawn
    appears over the whole window; with it ON (raid MTB forced to the floor, ~1.2 h) one does. A statistical
    mechanic made near-certain by a long window (about 6 hourly rolls at ~0.56 each: a ~0.7% false-RED chance,
    named in the walk) -- the OFF arm runs FIRST so the later raid cannot contaminate it."""
    _enter(t)
    box = {}
    window = 15000
    swarm = "RM_FactionDef_KurrethSwarm"

    def arm(t):
        x, z = t.anchor
        t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="All")
        t.bridge_call("jawa/destroy_batch", rects=_pad_rect(t), categories="Pawn")
        stake = _spawn_building(t, "RM_LureStake", x, z)
        bait = _spawn(t, "Colonist", x + 5, z + 5, "none")
        handler = _spawn(t, "Colonist", x + 8, z, "player")
        t.bridge_call("jawa/pawn_need", pawn=handler, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=handler, action="need", need="Rest", level=1.0)
        t.bridge_call("jawa/pawn_force_incapacitate", pawn=bait, action="downed", allowBleedingWounds=False)
        t.bridge_call("jawa/ordered_job", pawnId=handler, jobDef="RM_HaulToStake", targetAId=bait,
                      targetBId=stake, waitTicks=60, timeoutSeconds=25)

        def staked():
            blob = _blob(t, bait, _pad_rect(t))
            return blob is not None and LURE_STAKED in blob
        _wait_until(t, staked, 2400, chunk=200)
        if _live(t) and not staked():
            _unmeasured(t, "could not stake a bait for the raid arm")

    def swarm_pawns(t):
        r = t.bridge_call("jawa/list_pawns", faction=swarm, limit=200)
        if not _live(t):
            return []
        return list(_ok(r, "list_pawns(%s)" % swarm).get("pawns") or [])

    try:
        with _comp(t, "site_ready_raid"):
            _reset_pad(t)
            if _live(t):
                _need_parse(t)
                if swarm_pawns(t):
                    _unmeasured(t, "precondition: %d %s pawn(s) already on the map" % (len(swarm_pawns(t)), swarm))

        with _comp(t, "with_the_lure_toggle_off_no_raid_comes", independent=True, toggle="twoFrontLureEnabled"):
            with _settings(t, twoFrontLureEnabled=False, twoFrontLureRaidMtbHours=1):
                arm(t)
                t.wait_ticks(window)
                if _live(t) and swarm_pawns(t):
                    _fail("twoFrontLureEnabled=false and a swarm raid still came (%d pawns)" % len(swarm_pawns(t)))

        with _comp(t, "a_staked_lure_draws_the_swarm", independent=True, toggle="twoFrontLureEnabled"):
            with _settings(t, twoFrontLureEnabled=True, twoFrontLureRaidMtbHours=1, twoFrontLureSecondWaveChance=0):
                arm(t)
                _wait_until(t, lambda: bool(swarm_pawns(t)), window, chunk=1000)
                if _live(t):
                    got = swarm_pawns(t)
                    _note(t, "swarm pawns", [(p.get("kindDef"), p.get("faction")) for p in got[:6]])
                    if not got:
                        _fail("no %s pawn appeared in %d ticks with live bait staked and the raid MTB at its floor "
                              "(a ~0.7%% chance it is just unlucky: rerun once before believing it)" % (swarm, window))
    finally:
        if t.session is not None:
            try:
                for p in (t.session.call("jawa/list_pawns", faction=swarm, limit=200) or {}).get("pawns") or []:
                    t.session.call("jawa/damage", damageDef="Bullet", amount=9999.0, thingId=p.get("id"),
                                   armorPenetration=1.0, allowColonists=False)
            except Exception as ex:
                print("[fw] raid teardown failed: %s" % ex, file=sys.stderr, flush=True)
        _teardown(t)


# ------------------------------------------------------------------------- hive rally

CB_SETTINGS = "RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings"
HIVE_RALLY = "RM_HiveRally"


def _census(t, ids):
    r = t.bridge_call("jawa/pawn_census", ids=",".join(i for i in ids if i))
    if not _live(t):
        return {}
    return {p.get("id"): p for p in (_ok(r, "pawn_census").get("pawns") or [])}


@suite.chain("hive_rally")
def hive_rally(t):
    """REACTION_MECHANISM_GENERALISE_1 step 3: three wild kurreth in a line 6 cells apart (one hop each, the
    hop reach is 9) and a colonist 4 cells from the first, in its sight. The first notices, rings, and the
    alarm hops down the line: all three end in RM_HiveRally aimed at that colonist, and the alarm message is
    posted. With CreatureBehaviors' reactionDetectionEnabled OFF the same layout rallies nobody. Asleep
    sentries notice nothing BY DESIGN, so an all-asleep line reads UNMEASURED, never FAIL."""
    _enter(t)

    def layout(t):
        _reset_pad(t)
        x, z = t.anchor
        ants = [_spawn(t, "RM_Kurreth", x + dx, z, "none") for dx in (0, 6, 12)]
        col = _spawn(t, "Colonist", x - 4, z, "player")
        return ants, col

    try:
        with _comp(t, "a_seen_intruder_rallies_the_whole_line"):
            ants, col = layout(t)
            t.wait_ticks(400)
            if _live(t):
                rows = _census(t, ants)
                states = [((rows.get(a) or {}).get("mentalState") or {}) for a in ants]
                _note(t, "hive states", states)
                if not any(s.get("def") == HIVE_RALLY for s in states):
                    jobs = [(((rows.get(a) or {}).get("job") or {}).get("def")) for a in ants]
                    if all(j == "LayDown" for j in jobs):
                        _unmeasured(t, "every kurreth was asleep (a sleeping sentry notices nothing by design)")
                    _fail("no kurreth rallied with a colonist 4 cells from the first sentry: %r jobs=%r" % (states, jobs))
                bad = [s for s in states if s.get("def") != HIVE_RALLY]
                if bad:
                    _fail("the alarm did not hop down the line (6-cell gaps, 9-cell reach): %r" % states)
                if any(str(s.get("causedByPawn") or "").replace("Thing_", "") != str(col).replace("Thing_", "")
                       for s in states):
                    _fail("a rallied kurreth is not aimed at the intruder %s: %r" % (col, states))
                if "kurreth hive has noticed" not in _messages(t):
                    _fail("no alarm message posted (the hive must telegraph)")

        with _comp(t, "with_detection_off_the_same_layout_rallies_nobody", independent=True):
            t.set_setting(CB_SETTINGS, {"reactionDetectionEnabled": False})
            try:
                ants, col = layout(t)
                t.wait_ticks(400)
                if _live(t):
                    rows = _census(t, ants)
                    rallied = [a for a in ants if ((rows.get(a) or {}).get("mentalState") or {}).get("def") == HIVE_RALLY]
                    if rallied:
                        _fail("reactionDetectionEnabled=false and %d kurreth still rallied on sight" % len(rallied))
            finally:
                if t.session is not None:
                    t.session.call("jawa/mod_settings_field", typeName=CB_SETTINGS, action="set",
                                   field="reactionDetectionEnabled", value="True")
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- hive parasite

@suite.chain("hive_parasite")
def hive_parasite(t):
    """FEVERWOOD_HIVE_PARASITE_CHAMBER_1: a hungry glomvar 3 cells from a calm wild kurreth kills it, the
    hive's alarm never rings (the glomvar is unseen by it), and a colonist 12 cells off is left alone (it is no
    predator of anything but the hive). With antHiveParasiteChamberEnabled OFF the same hungry glomvar leaves
    the kurreth alive."""
    _enter(t)
    window = 2500

    def layout(t):
        _reset_pad(t)
        x, z = t.anchor
        g = _spawn(t, "RM_Glomvar", x, z, "none")
        k = _spawn(t, "RM_Kurreth", x + 3, z, "none")
        c = _spawn(t, "Colonist", x - 12, z, "player")
        t.bridge_call("jawa/pawn_need", pawn=g, action="need", need="Food", level=0.1)
        return g, k, c

    def alive(t, pid):
        row = _census(t, [pid]).get(pid)
        return row is not None and not row.get("dead") and not row.get("downed")

    try:
        with _comp(t, "a_hungry_glomvar_eats_a_kurreth_unseen_and_ignores_the_colonist",
                   toggle="antHiveParasiteChamberEnabled"):
            g, k, c = layout(t)
            phrase = "kurreth hive has noticed"
            before = _messages(t).count(phrase)      # a count delta: earlier chains' alarms never count here
            t.wait_ticks(window)
            if _live(t):
                if alive(t, k):
                    _fail("a hungry glomvar 3 cells from a calm kurreth left it standing after %d ticks" % window)
                if not alive(t, c):
                    _fail("the colonist 12 cells off is down or dead: the glomvar must hunt nothing but the hive")
                if _messages(t).count(phrase) > before:
                    _fail("the kurreth alarm rang: the hive must not perceive the glomvar")

        with _comp(t, "with_the_parasite_toggle_off_the_kurreth_lives", independent=True,
                   toggle="antHiveParasiteChamberEnabled"):
            with _settings(t, antHiveParasiteChamberEnabled=False):
                g, k, c = layout(t)
                t.wait_ticks(window)
                if _live(t) and not alive(t, k):
                    _fail("antHiveParasiteChamberEnabled=false and the glomvar still killed the kurreth")
    finally:
        _teardown(t)


def _clear_ant_raid(t):
    """After a chain that stages the kurreth column (RM_KurrethTheftProof.ProofRaid spawns its ants at the MAP EDGE, far
    outside the pad that _teardown clears): kill every swarm pawn. Left alive they bit colonists in the NEXT suites'
    chains (load 13: kurreth bites in Greentide's mire/swallow chains = surprise taints). Best-effort, never masks a verdict."""
    if t.session is None:
        return
    try:
        for p in (t.session.call("jawa/list_pawns", faction="RM_FactionDef_KurrethSwarm", limit=200) or {}).get("pawns") or []:
            t.session.call("jawa/damage", damageDef="Bullet", amount=9999.0, thingId=p.get("id"),
                           armorPenetration=1.0, allowColonists=False)
    except Exception as ex:                                    # noqa: BLE001
        print("[fw] ant raid cleanup failed: %s" % ex, file=sys.stderr, flush=True)


def _with_ant_raid_cleanup(fn):
    import functools

    @functools.wraps(fn)
    def run(t):
        try:
            return fn(t)
        finally:
            _clear_ant_raid(t)
    return run


@suite.chain("ant_theft")
@_with_ant_raid_cleanup
def ant_theft(t):
    """FEVERWOOD_ANT_THEFT_RAIDBACK_1 part A: the kurreth lure wave steals. Source read: the lure routes the
    kurreth faction to RM_LordJob_KurrethTheft behind antTheftEnabled (the old plain assault is the off-route
    only) and the theft toil finds downed victims through RM_HaulVictimAIUtility. Live: a 6-ant column under the
    theft LordJob against 3 tamed thornbugs on the CURRENT map (RM_KurrethTheftProof.ProofRaid); after the window
    no thornbug corpse, at least one theft recorded, held alive by the kurreth faction, and the column letter
    sent. NOT proven here: the raid-back (part B, its own item), the trail by eye, and the off arm (a plain
    assault may still kill a thornbug; asserting 'never removed' needs a long window -- first poke: set
    antTheftEnabled false, ProofRaid, step 6000, ProofState thefts=0)."""
    with _comp(t, "lure_routes_kurreth_to_the_theft_lordjob", independent=True):
        if t.session is not None:
            src = os.path.join(_HERE, "S" + "ource")
            lure = open(os.path.join(src, "RM_MapComponent_TwoFrontLure.cs"), encoding="utf-8").read()
            theft = open(os.path.join(src, "RM_KurrethTheft.cs"), encoding="utf-8").read()
            if not re.search(r"AntFactionDefName\s*&&\s*RM_FeverWoodSettings\.antTheftEnabled\s*\?\s*new RM_LordJob_KurrethTheft\(\)",
                             lure):
                _fail("the lure does not route the kurreth faction to RM_LordJob_KurrethTheft behind antTheftEnabled")
            if lure.count("new LordJob_AssaultColony(") != 1:
                _fail("expected exactly one plain-assault route (the off/brood branch) in the lure")
            for needle in ("RM_HaulVictimAIUtility.TryFindGoodHaulVictim", "requireManipulation: false",
                           "PawnLostCondition.ExitedMap", "Filth_Slime", "LetterStack.ReceiveLetter"):
                if needle not in theft:
                    _fail("RM_KurrethTheft.cs lacks %s" % needle)
            jd = open(os.path.join(_HERE, "Defs", "JobDefs", "RM_FeverWood_KurrethTheftJobDefs.xml"), encoding="utf-8").read()
            for d in ("RM_KurrethStun", "RM_KurrethCarryOff"):
                if "<defName>%s</defName>" % d not in jd:
                    _fail("JobDef %s missing" % d)

    def proof(t, method):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.FeverWood.RM_KurrethTheftProof", method=method,
                          args="current")
        return _proof_text(r)

    with _comp(t, "a_kurreth_column_carries_thornbugs_off_alive", toggle="antTheftEnabled"):
        raid = proof(t, "ProofRaid")
        if _live(t) and not raid.startswith("RAID"):
            _fail("ProofRaid did not stage the column: %s" % raid)
        t.wait_ticks(6000)
        state = proof(t, "ProofState")
        _note(t, "ant theft state", state)
        if _live(t):
            nums = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)\b", state))
            if nums.get("thornbugCorpses", 1) != 0:
                _fail("a thornbug died in the theft raid: %s" % state)
            if nums.get("thefts", 0) < 1 or nums.get("heldByKurreth", 0) < 1:
                _fail("no thornbug was carried off and held alive: %s" % state)
            if nums.get("letters", 0) < 1:
                _fail("no 'Carried off' letter was sent: %s" % state)


@suite.chain("kurreth_column")
@_with_ant_raid_cleanup
def kurreth_column(t):
    """FEVERWOOD_KURRETH_COLUMN_RAIDBACK_1 (part B of the ant theft). Offline: RM_Quest_KurrethColumn is code-fired only
    (weight 0, isRootSpecial, autoAccept) around the C# node, the site part and the bound hediff exist, the theft letter
    starts the quest, and both timers are read from Mod Settings. Live on the CURRENT map: a theft raid
    (RM_KurrethTheftProof.ProofRaid, step) leaves an open column quest with an unspawned-map site holding the stolen
    ids (RM_KurrethColumnProof.ProofQuest), and forcing the column deadline moves it on (ProofHive: into the hive
    when the map has one, else the lost letter) -- never left in Column. NOT proven here: entering the camp, the
    guards, cutting an animal free and walking it home (first poke: after ProofQuest, send a caravan to the site,
    walk a colonist to a bound thornbug once the guards are dead, read ProofQuest bound=0 then quest ends)."""
    with _comp(t, "column_quest_wired", independent=True):
        if t.session is not None:
            q = ET.parse(os.path.join(_HERE, "Defs", "QuestScriptDefs", "RM_Quest_KurrethColumn.xml")).getroot()
            qd = q.find("QuestScriptDef[defName='RM_Quest_KurrethColumn']")
            if qd is None:
                _fail("QuestScriptDef RM_Quest_KurrethColumn missing")
            if qd.findtext("rootSelectionWeight") != "0" or qd.findtext("isRootSpecial") != "true" or qd.findtext("autoAccept") != "true":
                _fail("the column quest must be code-fired only and auto-accepted")
            nodes = [li.get("Class", "") for li in qd.findall("root/nodes/li")]
            if "RimMandrake.FeverWood.RM_QuestNode_KurrethColumn" not in nodes or nodes.count("QuestNode_End") != 2:
                _fail("the column quest needs its C# node and two ends, got %r" % nodes)
            for sub, name in (("SitePartDefs", "RM_KurrethColumnCamp"), ("HediffDefs", "RM_Hediff_KurrethBound")):
                if not os.path.isfile(os.path.join(_HERE, "Defs", sub, name + ".xml")):
                    _fail("missing %s/%s.xml" % (sub, name))
            src = os.path.join(_HERE, "S" + "ource")
            col = open(os.path.join(src, "RM_KurrethColumn.cs"), encoding="utf-8").read()
            theft = open(os.path.join(src, "RM_KurrethTheft.cs"), encoding="utf-8").read()
            proj = open(os.path.join(src, "RM_FeverWood.csproj"), encoding="utf-8").read()
            if "RM_KurrethColumnUtility.TryStartColumnQuest(" not in theft:
                _fail("the theft letter does not start the column quest")
            if '<Compile Include="RM_KurrethColumn.cs" />' not in proj:
                _fail("RM_KurrethColumn.cs is not compiled (EnableDefaultCompileItems is off)")
            for needle in ("RM_FeverWoodSettings.kurrethColumnEnabled", "RM_FeverWoodSettings.kurrethColumnDays",
                           "RM_FeverWoodSettings.kurrethHiveHoldDays", "RemoveKidnappedPawn", "QueenRoom"):
                if needle not in col:
                    _fail("RM_KurrethColumn.cs lacks %s" % needle)

    def proof(t, typ, method):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.FeverWood." + typ, method=method, args="current")
        return _proof_text(r)

    def nums(text):
        return dict((k, v) for k, v in re.findall(r"(\w+)=([\w.,-]*)", text))

    with _comp(t, "a_theft_opens_a_column_camp_holding_the_animals", toggle="kurrethColumnEnabled"):
        raid = proof(t, "RM_KurrethTheftProof", "ProofRaid")
        if _live(t) and not raid.startswith("RAID"):
            _fail("ProofRaid did not stage the column: %s" % raid)
        t.wait_ticks(6000)
        q = nums(proof(t, "RM_KurrethColumnProof", "ProofQuest"))
        _note(t, "column quest", q)
        if _live(t):
            if q.get("quest") != "1" or q.get("site") != "1" or q.get("phase") != "Column":
                _fail("no open column quest with a camp site after the theft: %r" % q)
            if int(q.get("held", "0") or 0) < 1 or not q.get("victimIds"):
                _fail("the column quest holds no stolen animal: %r" % q)

    with _comp(t, "an_unreached_column_moves_on_and_says_so", toggle="kurrethColumnEnabled"):
        h = nums(proof(t, "RM_KurrethColumnProof", "ProofHive"))
        _note(t, "column after deadline", h)
        if _live(t) and h.get("phase") not in ("Hive", "Done"):
            _fail("the column stayed put past its deadline: %r" % h)


@suite.chain("oil_boil")
def oil_boil(t):
    """FEVERWOOD_OIL_BOIL_WEATHER_1. Offline: the weather and condition defs exist, RM_FeverWood rolls the oil boil
    and still has Rain 0, the gate is the weather's temperatureRange written from Mod Settings. Live on the CURRENT
    map (RM_OilBoilProof): the gate's answer, seepril yield doubled under the condition, and a spark in a hazed
    ground cell flashes fire and ends the condition. NOT proven here: a shot from a boughway cell staying cold, a
    melee hit staying cold, the pool-edge wake (needs a registered pool: no quicktest carries one) -- first poke on a
    Fever Wood map: ProofSpark beside a pool, then count RM_Sekkulaath_* within the cluster."""
    with _comp(t, "weather_and_condition_wired", independent=True):
        if t.session is not None:
            wx = ET.parse(os.path.join(_HERE, "Defs", "WeatherDefs", "RM_FeverWood_OilBoil.xml")).getroot()
            if wx.find("WeatherDef[defName='RM_FeverWood_OilBoil']") is None:
                _fail("WeatherDef RM_FeverWood_OilBoil missing")
            if "RM_WeatherOverlay_OilBoilHaze" not in ET.tostring(wx, encoding="unicode"):
                _fail("the oil boil weather lacks its haze overlay")
            cx = ET.parse(os.path.join(_HERE, "Defs", "GameConditionDefs", "RM_OilBoilCondition.xml")).getroot()
            if (cx.findtext("GameConditionDef/conditionClass") or "").strip() != "RimMandrake.FeverWood.RM_GameCondition_OilBoil":
                _fail("RM_OilBoilCondition does not use RM_GameCondition_OilBoil")
            weathers = _BIOME_EL.find("baseWeatherCommonalities") if _BIOME_EL is not None else None
            names = dict((ch.tag, (ch.text or "").strip()) for ch in (weathers if weathers is not None else []) if isinstance(ch.tag, str))
            if len(names) < 4:
                _fail("read only %d weather rows from RM_FeverWood: parse failure" % len(names))
            if float(names.get("RM_FeverWood_OilBoil", 0) or 0) <= 0:
                _fail("RM_FeverWood does not roll RM_FeverWood_OilBoil")
            if names.get("Rain") != "0":
                _fail("RM_FeverWood Rain must stay 0, reads %r" % names.get("Rain"))
            src = open(os.path.join(_HERE, "S" + "ource", "RM_OilBoil.cs"), encoding="utf-8").read()
            for needle in ("w.temperatureRange = new FloatRange(RM_FeverWoodSettings.oilBoilMinTempC",
                           "oilBoilCommonalityMultiplier", "oilBoilYieldMultiplier", "oilBoilFlashRadius",
                           "oilBoilWakesDeep", "ForceEmergenceNear", "RaisedTerrain", "IsWater"):
                if needle not in src:
                    _fail("RM_OilBoil.cs lacks %s" % needle)
            if not os.path.isfile(os.path.join(_HERE, "Textures", "Weather", "RM_FeverWood_OilBoilHaze.png")):
                _fail("haze overlay texture missing")

    def proof(t, method):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.FeverWood.RM_OilBoilProof", method=method, args="current")
        return _proof_text(r)

    def nums(text):
        return dict((k, v) for k, v in re.findall(r"(\w+)=([\w.-]+)", text))

    with _comp(t, "gate_follows_the_temperature_setting", independent=True, toggle="oilBoilEnabled"):
        g = nums(proof(t, "ProofGate"))
        if _live(t):
            try:
                want = g.get("enabled") == "True" and float(g["temp"]) >= float(g["min"])
            except (KeyError, ValueError):
                _fail("ProofGate unreadable: %r" % g)
            if (g.get("canOccur") == "True") != want:
                _fail("gate says canOccur=%s at %s C against min %s" % (g.get("canOccur"), g.get("temp"), g.get("min")))

    with _comp(t, "seepril_yield_doubles_while_boiling", independent=True):
        y = nums(proof(t, "ProofYield"))
        if _live(t):
            try:
                off, on = int(y["yieldOff"]), int(y["yieldOn"])
            except (KeyError, ValueError):
                _fail("ProofYield unreadable: %r" % y)
            want = int(round(off * float(SETTING_FIELDS["oilBoilYieldMultiplier"][1])))
            if off <= 0 or on != want:
                _fail("seepril yield %d off, %d on; expected %d" % (off, on, want))

    with _comp(t, "a_spark_in_the_haze_flashes_and_burns_it_off", independent=True):
        s = nums(proof(t, "ProofSpark"))
        if _live(t):
            if s.get("flashed") != "True" or s.get("conditionEnded") != "True":
                _fail("spark did not flash and end the condition: %r" % s)
            if int(s.get("firesAfter", 0)) <= int(s.get("firesBefore", 0)):
                _fail("the flash started no fire: %r" % s)
