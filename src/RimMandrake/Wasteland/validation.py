"""validation.py -- modcheck suite for RimMandrake: Wasteland (mandrake.rm.wasteland).

Walk: design/validation_walks/RimMandrake/Wasteland.md (`## must be true`, agent-owned, not hashed).
Item: WASTELAND_FIRST_SCRIPT_1. Process: design/RimMandrake/debug_process.md section 2.

PACKAGING. This dev folder is SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json, wave 2), so a run loads the `wasteland_solo` tier (modset_builder.py: BRIDGE +
mandrake.rm.biomes + the five DLCs) and `northstar_plan.py` expects `mandrake.rm.biomes` active.
`modcheck run Wasteland` appends the dev folder's packageId with no closure and lands on a list without
the biome: drive `northstar_driver/cli.py run --mod Wasteland --plan <northstar_plan.py>` (or
`northstar_driver/live_session.py`, whose exact command is in the live-run sheet).

What the mod is for (every line is sourced; see the walk): About.xml's four ships.
  1. `RM_Wasteland`, a hand-placed BiomeDef (generatesNaturally=false) with this mod's own worker, a
     12-animal and 12-plant roster, no rain, the ash storm and the deadlight halo on its weather list and
     the cinderwire storm deliberately OFF it, and the storm-layer opt-in extension.
  2. The brine-battery archetype: RM_WastelandBrine* terrain, three mineable deposits, the items they
     yield, RM_BrineShock, and the three GenSteps registered on the biome by patch.
  3. The storms (ash storm, Deadlight Halo, Cinderwire Storm: dose, fall, aftermath, warning phase), the
     ambient-dose and radiothermal creatures, the processor animals, the gripper's theft, the Middenshell
     (20-cell body, crawl, wake, procession, trail, carcass).
  4. Waste: the waste cask, the sealed cask bay and the Rite of Tipping.

Derived from the mod's own `Defs/*.xml` and `Source/RM_WastelandMod.cs` at import (never a hand list):
the def groups, the biome rosters, the storm warning texts, the Mod Settings fields and their shipped
defaults. Pinned floors (FLOORS) stop a parse failure from reading as "nothing to check".

SITE. The storm layer, the Middenshell incident and the Rite of Tipping are biome-gated (they read
`map.Biome`), so a run needs a map whose biome IS `RM_Wasteland`. `northstar_site.preflight` builds one
(re-tile a land tile, found a colony on it, generate 150x150, make it current) when the current map is
not already Wasteland. Every biome-gated chain re-reads `jawa/map_info.mapBiome` first and records
UNMEASURED, never PASS, on any other biome. Chains that key on a def (creatures, casks, deposits) run on
whatever map is current.

NOT measurable with the existing bridge tools (named in the walk, never faked here): EMP pulses and
lightning (random cell, random interval), the tentacle grab (random interval), the waste-stockpile lure
and the exit scar (a full 150-cell crossing), the cask-bay processing toggle and reburial (a Command_Toggle
gizmo), the gravship launch refusal (needs an engine; only the Harmony patch is read), a Tipping delivery
(four game days), pollution consumption by processor animals (0.1% per check), the BiomeWorker score and
the biome ranges (inert: generatesNaturally=false), and every visual.

Every bridge call uses only parameters the live tool declares (lint_calls.py). Result shapes MEASURED live
elsewhere: `jawa/list_things` -> countMatched / isCompleteList / things[].id,x,z,stackCount;
`jawa/list_pawns` -> pawns[].id/kindDef/faction/x/z and, with includeHealth, health.hediffs[].def/severity;
`jawa/get_defs` -> foundCount/notFound/defs[].fields/packageId; `jawa/biome_probe` -> biomes[].animals/
plants; `jawa/inspect_string` -> things[].label/inspect[]; `jawa/set_pollution` -> cellsChanged;
`jawa/map_info` -> sizeX/sizeZ/mapBiome/tile/mapId. UNPROVEN until the first live run (a component that
cannot read a shape it needs records UNMEASURED via `_unmeasured`, never PASS): `rimworld/list_messages`
and `jawa/alerts_list` row keys (read through `_flat`), `jawa/room_get.rooms[].temperature`,
`jawa/pawn_flight.pawns[].canEverFly` (measured for LeaningScrub), `jawa/harmony_patches` row keys,
`jawa/get_defs` serialising `baseWeatherCommonalities`/`extraGenSteps`/`modExtensions`/`building`.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.Wasteland.RM_WastelandSettings"
OUR_PACKAGES = ("mandrake.rm.biomes", "mandrake.rm.wasteland")
BIOME = "RM_Wasteland"
PAD = 29                    # fixture pad: PAD x PAD cells around the chain's anchor
PAD_OFFSET = 45             # the pad sits this far from the map centre, clear of the start colonists
ROOM = 7                    # make_empty_room rect: 7x7 outer, 5x5 interior
SHELL = 20                  # the Middenshell's owner-ruled footprint (WASTELAND_MIDDENSHELL_FOOTPRINT_1)
ACTIVE_ON_TIER = ("Ludeon.RimWorld.Odyssey", "Ludeon.RimWorld.Biotech", "Ludeon.RimWorld.Ideology",
                  "Ludeon.RimWorld.Royalty", "Ludeon.RimWorld.Anomaly", "mandrake.rm.biomes")

# ----------------------------------------------------------------------- source parse (import time)

_DEFS = os.path.join(HERE, "Defs")
_ERRORS = []


def _parse_file(path):
    try:
        return ET.parse(path).getroot()
    except Exception as ex:                       # a def file that does not parse is itself a finding
        _ERRORS.append("%s: %s" % (os.path.relpath(path, HERE), ex))
        return None


def _all_defs():
    """[(DefType, defName, element)] for every non-abstract def under Defs/ (all subfolders)."""
    rows = []
    if not os.path.isdir(_DEFS):
        _ERRORS.append("missing Defs/")
        return rows
    for sub in sorted(os.listdir(_DEFS)):
        d = os.path.join(_DEFS, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".xml"):
                continue
            root = _parse_file(os.path.join(d, fn))
            if root is None:
                continue
            for el in root:
                if not isinstance(el.tag, str) or el.get("Abstract", "").lower() == "true":
                    continue
                nm = (el.findtext("defName") or "").strip()
                if nm:
                    rows.append((el.tag, nm, el))
    return rows


_ROWS = _all_defs()
_BY_TYPE = {}
for _t, _n, _e in _ROWS:
    _BY_TYPE.setdefault(_t, []).append(_n)
ALL_DEFNAMES = set(n for _, n, _ in _ROWS)


def _el(deftype, name):
    return next((e for t, n, e in _ROWS if t == deftype and n == name), None)


# The count at authoring (2026-10-01, 79 defs): a shrink must be a deliberate edit of this script.
FLOORS = {"ThingDef": 38, "PawnKindDef": 12, "TerrainDef": 6, "WeatherDef": 3, "SoundDef": 5,
          "GenStepDef": 3, "FleckDef": 2, "IncidentDef": 2, "JobDef": 2, "HediffDef": 1,
          "QuestScriptDef": 1, "LetterDef": 1, "WorkGiverDef": 1, "ThinkTreeDef": 1, "BiomeDef": 1}

_BIOME_EL = _el("BiomeDef", BIOME)


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
BIOME_WEATHER = dict((k, v) for k, v in _roster("baseWeatherCommonalities").items())
BIOME_SCALARS = dict((k, float(_BIOME_EL.findtext(k))) for k in ("animalDensity", "plantDensity")
                     if _BIOME_EL is not None and _BIOME_EL.findtext(k))
PLASMA = "RM_WastelandPlasmaStorm"
ASH = "RM_WastelandAshStorm"
HALO = "RM_WastelandRadiationHalo"


def _phase_text(weather, tag):
    el = _el("WeatherDef", weather)
    if el is None:
        return ""
    for li in el.findall("modExtensions/li"):
        if (li.get("Class") or "").endswith("RM_StormPhaseExtension"):
            return " ".join((li.findtext(tag) or "").split())
    return ""


def _frag(text, n=34):
    """A distinctive prefix of a message text, safe against line wrapping and entity decoding."""
    return " ".join(text.split())[:n]


WARN = {HALO: _frag(_phase_text(HALO, "warningMessage")), PLASMA: _frag(_phase_text(PLASMA, "warningMessage"))}
UNLEASH = {HALO: _frag(_phase_text(HALO, "unleashedMessage")),
           PLASMA: _frag(_phase_text(PLASMA, "unleashedMessage"))}


def _parse_settings():
    """{field: shipped default} read out of RM_WastelandMod.cs (single source, never a hand copy)."""
    out = {}
    path = os.path.join(HERE, "Source", "RM_WastelandMod.cs")
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as ex:
        _ERRORS.append("Source/RM_WastelandMod.cs: %s" % ex)
        return out
    for typ, name, val in re.findall(r"public static (bool|float|int) (\w+) = ([^;]+);", src):
        val = val.strip()
        if typ == "bool":
            out[name] = (val == "true")
        elif typ == "float":
            out[name] = float(val.rstrip("fF"))
        else:
            out[name] = int(val)
    return out


DEFAULTS = _parse_settings()
TOGGLES = sorted(k for k, v in DEFAULTS.items() if isinstance(v, bool))
NUMBERS = sorted(k for k, v in DEFAULTS.items() if not isinstance(v, bool))
BAY_SIZE = (3, 2)           # RM_WasteCaskBay <size>; asserted against the def XML below
_bay = _el("ThingDef", "RM_WasteCaskBay")
if _bay is not None and _bay.findtext("size"):
    try:
        BAY_SIZE = tuple(int(v) for v in _bay.findtext("size").strip("() ").split(","))
    except ValueError:
        _ERRORS.append("RM_WasteCaskBay size unparseable: %r" % _bay.findtext("size"))

DELIVERIES = 3              # RM_TippingQuestExtension.deliveries on RM_Quest_RiteOfTipping (parsed below)
_q = _el("QuestScriptDef", "RM_Quest_RiteOfTipping")
if _q is not None:
    for _li in _q.findall("modExtensions/li"):
        if _li.findtext("deliveries"):
            DELIVERIES = int(_li.findtext("deliveries").strip())

FLORA_PRODUCTS = [(n, (e.findtext("plant/harvestedThingDef") or "").strip())
                  for t, n, e in _ROWS if t == "ThingDef" and (e.findtext("plant/harvestedThingDef") or "").strip()]

suite = Suite("Wasteland")
suite.toggles = list(TOGGLES)

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
        print("[wl] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
              file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, also echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[wl-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]), file=sys.stderr, flush=True)


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


def _has(obj, needle):
    n = needle.lower()
    return any(n in s.lower() for s in _flat(obj))


def _need_parse(t):
    if _ERRORS:
        _fail("the mod's own Defs/Source did not parse: %s" % "; ".join(_ERRORS[:3]))
    if len(DEFAULTS) < 30:
        _fail("settings parse found %d fields, floor 30: a parse failure" % len(DEFAULTS))


def _same(got, want):
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(str(got).replace(",", ".")) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def _get_defs(t, specs, fields="", deep=False):
    """get_defs over `DefType/defName` specs (a STRING, chunked); returns [row,...] and notFound.
    Reads the tool's own success/foundCount/notFound -- never a substring of the payload."""
    rows, missing = [], []
    for i in range(0, len(specs), 40):
        chunk = specs[i:i + 40]
        r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields=fields, deep=bool(deep))
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


def _field(t, spec, name):
    """One field of one def, or UNMEASURED when the tool cannot serialise it. modExtensions is read NON-deep:
    deep=True serialises each extension as a field dict with no class name (measured live 2026-10-07), so
    _has() could never see DuneFieldExtension / WastelandStormBiomeExtension; non-deep returns the class names."""
    rows, missing = _get_defs(t, [spec], fields=name, deep=(name != "modExtensions"))
    if not _live(t):
        return None
    if missing or not rows:
        _fail("%s is not loaded by the game: %r" % (spec, missing))
    val = (rows[0].get("fields") or {}).get(name)
    if val in (None, "(no such field)"):
        _unmeasured(t, "get_defs cannot read %s.%s (got %r)" % (spec, name, val))
    return val


def _things(t, defs, rect, limit=500):
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=limit)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defs)
    if r.get("isCompleteList") is False:
        _fail("list_things(%s) truncated: %r" % (defs, r.get("message")))
    return list(r.get("things") or [])


def _pawns(t, rect=None, kind=None, health=False):
    if rect and health:
        r = t.bridge_call("jawa/list_pawns", rect=rect, includeHealth=True, limit=300)
    elif rect:
        r = t.bridge_call("jawa/list_pawns", rect=rect, limit=300)
    elif health:
        r = t.bridge_call("jawa/list_pawns", includeHealth=True, limit=300)
    else:
        r = t.bridge_call("jawa/list_pawns", limit=300)
    if not _live(t):
        return []
    _ok(r, "list_pawns")
    if r.get("truncated"):
        _fail("list_pawns truncated: %r" % r.get("message"))
    return [p for p in (r.get("pawns") or []) if kind is None or p.get("kindDef") == kind]


def _hediffs(row):
    return dict((h.get("def"), float(h.get("severity") or 0))
                for h in (((row or {}).get("health") or {}).get("hediffs") or []))


def _hed(t, pid, defname):
    """Severity of `defname` on pawn `pid` (0.0 when absent). UNMEASURED if the pawn cannot be read."""
    rows = [p for p in _pawns(t, health=True) if p.get("id") == pid]
    if _live(t) and not rows:
        _unmeasured(t, "pawn %s is not on the map, so its health cannot be read" % pid)
    return _hediffs(rows[0]).get(defname, 0.0) if rows else 0.0


def _row_def(row):
    return row.get("def") or row.get("defName")


def _stack(row):
    for k in ("stackCount", "count", "stack"):
        if isinstance(row.get(k), (int, float)):
            return int(row[k])
    return None


def _inspect(t, thing_id):
    """The inspect-pane lines of one thing (a pawn id or a thing id), as one lower-case string."""
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return ""
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows or rows[0].get("error"):
        _fail("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return " | ".join(str(x) for x in (rows[0].get("inspect") or []))


def _map_info(t):
    r = t.bridge_call("jawa/map_info")
    if not _live(t):
        return {}
    return _ok(r, "map_info")


def _need_wasteland(t):
    """Biome-gated chains only run on a map whose biome IS RM_Wasteland (see the module docstring)."""
    if not _live(t):
        return {}
    mi = _map_info(t)
    if mi.get("mapBiome") != BIOME:
        _unmeasured(t, "the current map's biome is %r, not %s: this mechanic is biome-gated "
                       "(northstar_site.preflight builds a Wasteland map; its error, if any, is in "
                       "northstar_site.LAST_SITE_ERROR)" % (mi.get("mapBiome"), BIOME))
    return mi


def _set(t, **vals):
    """Flip Mod Settings fields for this session (verified by read-back inside set_setting)."""
    for k, v in vals.items():
        if k not in DEFAULTS:
            _fail("script bug: %s is not a Wasteland setting" % k)
        if isinstance(DEFAULTS[k], int) and not isinstance(DEFAULTS[k], bool):
            v = int(v)                              # an Int32 field refuses "3.0"
        t.set_setting(SETTINGS, {k: v})


def _restore(t, names):
    """Best-effort, runs even after a FAILED chain (t.bridge_call is then a no-op, so use the session)."""
    if t.session is None:
        return
    for k in names:
        try:
            want = DEFAULTS[k]
            t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=k,
                           value=str(want))
        except Exception as ex:
            print("[wl] restore %s failed: %s" % (k, ex), file=sys.stderr, flush=True)


def _enter(t):
    """First line of every fixture chain: move this chain's anchor to the pad, off the map centre."""
    if not getattr(t, "_wl_anchored", False):
        x, z = t.anchor
        t.anchor = (x + PAD_OFFSET, z + PAD_OFFSET)
        t._wl_anchored = True


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _pad_rect(t):
    x, z = t.anchor
    h = PAD // 2
    return "%d,%d,%d,%d" % (x - h, z - h, PAD, PAD)


def _map_rect(t):
    mi = _map_info(t)
    return "0,0,%d,%d" % (mi.get("sizeX") or 0, mi.get("sizeZ") or 0)


def _reset_pad(t, terrain="Soil"):
    """Everything true before the first assertion: the pad empty of THINGS, flat natural floor, unroofed,
    unfogged, no pollution. NOT pawns: jawa/destroy_batch never destroys a pawn whatever `categories` says (its own
    description), so pawns from earlier chains survive -- use jawa/destroy_bulk where a stray pawn would matter."""
    rect = _pad_rect(t)
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="All")
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, rect))
    t.bridge_call("jawa/set_roof_batch", ops=rect, roofDef="None")
    t.bridge_call("jawa/set_fog", action="unfog", rect=rect)
    t.bridge_call("jawa/set_pollution", rect=rect, polluted=False, silent=True)
    t.bridge_call("jawa/log_autoopen_suppress")


def _teardown(t):
    """Best-effort, runs even after a FAILED chain."""
    if t.session is None or not getattr(t, "_wl_anchored", False):
        return
    try:
        rect = _pad_rect(t)
        t.session.call("jawa/destroy_batch", rects=rect, categories="All")
    except Exception as ex:                       # teardown must never mask the chain's own verdict
        print("[wl] teardown failed: %s" % ex, file=sys.stderr, flush=True)


class _patient(object):
    """Raise the bridge client's per-reply socket timeout (the runner's 30 s) for a slow job order, then restore it.
    LIVE 2026-10-08: ordered_job with waitTicks=60 took ~17 s per call here and the gripper steal / brineleech
    Ingest orders outran 30 s ('timed out after 30.0s waiting for the bridge'). Same shape as Contagion's _patient.
    A mock session without a real socket is left alone."""
    def __init__(self, t, secs=240.0):
        self.rb = getattr(getattr(t, "session", None), "_rb", None)
        self.secs, self.old = secs, None

    def __enter__(self):
        if self.rb is not None and hasattr(self.rb, "timeout"):
            self.old = self.rb.timeout
            self.rb.timeout = self.secs
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.secs)
        return self

    def __exit__(self, *a):
        if self.old is not None:
            self.rb.timeout = self.old
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.old)
        return False


def _order(t, **kw):
    """jawa/ordered_job under _patient: the order waits waitTicks server-side and routinely outruns 30 s."""
    with _patient(t):
        return t.bridge_call("jawa/ordered_job", **kw)


def _spawn(t, kind, x, z, faction="none"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    _ok(r, "spawn_pawn(%s)" % kind)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn id: %r" % (kind, r))
    return pid


def _wait_dose(t, n):
    """Wait at least one vanilla toxic dose interval. LIVE 2026-10-08 (acc_biomes): every ToxicBuildup check here
    waited 420-900 ticks, but ToxicUtility.CheckInterval is 3451 and both the storm layer (now % 3451 == 0) and
    RM_CompAmbientDose (default checkIntervalTicks) dose only on that cadence, so a shorter window usually holds no
    dose tick at all and reads 'never applies'. RimSage-confirmed: DoPawnToxicDamage adds ~0.023 per interval."""
    t.wait_ticks(max(n, 3451 + 120))


def _settle(t, pid):
    """A colonist that will not wander off to eat, sleep or fight: needs full, undrafted."""
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=False)


def _spawn_thing(t, defname, x, z, count=1):
    r = t.bridge_call("rimworld/spawn_thing", defName=defname, x=x, z=z, stackCount=count)
    if _live(t):
        _ok(r, "spawn_thing(%s)" % defname)


def _pollution(t, rect, polluted):
    """set_pollution over a rect; returns (cellsChanged, cellsEverPollutable). The CLEAN direction after
    a run is the instrument: it flips exactly the cells the run polluted."""
    r = t.bridge_call("jawa/set_pollution", rect=rect, polluted=bool(polluted), silent=True)
    if not _live(t):
        return 0, 0
    _ok(r, "set_pollution")
    if not isinstance(r.get("cellsChanged"), (int, float)):
        _unmeasured(t, "set_pollution returned no cellsChanged: %r" % r)
    return int(r["cellsChanged"]), int(r.get("cellsEverPollutable") or 0)


def _weather(t, name):
    r = t.bridge_call("jawa/weather_set", weather=name, lockWeather=True)
    if not _live(t):
        return
    _ok(r, "weather_set(%s)" % name)
    got = t.bridge_call("jawa/weather_get")
    cur = (_ok(got, "weather_get").get("weather") or got.get("current"))
    if isinstance(cur, dict):
        cur = cur.get("current")
    if cur != name:
        _fail("weather_set(%s) did not take: the map reads %r (a named storm that cannot be set cannot be tested)" % (name, cur))


def _weather_reset(t):
    if t.session is None:
        return
    try:
        t.session.call("jawa/weather_set", weather="Clear", lockWeather=True)
    except Exception as ex:
        print("[wl] weather reset failed: %s" % ex, file=sys.stderr, flush=True)


def _messages(t):
    """Every string in the live message list, lower-cased, as one blob."""
    r = t.bridge_call("rimworld/list_messages", limit=60)
    if not _live(t):
        return ""
    _ok(r, "list_messages")
    return " | ".join(s.lower() for s in _flat(r))


def _room_temp(t, x, z):
    r = t.bridge_call("jawa/room_get", x=x, z=z, includeOutdoors=False)
    if not _live(t):
        return None
    rooms = (_ok(r, "room_get").get("rooms") or [])
    if not rooms or not isinstance(rooms[0].get("temperature"), (int, float)):
        _unmeasured(t, "room_get(%d,%d) returned no room temperature: %s" % (x, z, str(r)[:200]))
    return float(rooms[0]["temperature"])


def _make_room(t, x, z, sealed=False):
    """A roofed ROOMxROOM room on natural floor; returns its interior rect (x+1, z+1, 5, 5).
    sealed=True walls the door cell too (make_empty_room places doorDef there, so doorDef="Wall"): LIVE 2026-10-08
    the player-faction door let the sloghogs wander out of their polluted room (spawned at 162,169 inside, read at
    170,169 outside -> 'off feed ground') and a colonist out of the smolderback's room, so every in-room read failed."""
    r = t.bridge_call("jawa/make_empty_room", rect=_rs((x, z, ROOM, ROOM)), wallDef="Wall", stuffDef="WoodLog",
                      doorDef=("Wall" if sealed else "Door"), floorDef="Soil", roofDef="RoofConstructed")
    if _live(t):
        _ok(r, "make_empty_room")
        if (r.get("cellsWalled") or 0) < 4 * (ROOM - 1):
            _fail("make_empty_room walled %r cells, expected %d" % (r.get("cellsWalled"), 4 * (ROOM - 1)))
    return (x + 1, z + 1, ROOM - 2, ROOM - 2)


def _first_id(rows, what):
    if not rows or not rows[0].get("id"):
        _fail("no %s found" % what)
    return rows[0]["id"]


# ================================================================================ chains
@suite.chain("log_clean")
def log_clean(t):
    """The whole load, one read: no config error, unresolved cross-reference, missing type or exception
    naming this mod's content (a def with a missing comp/worker type is discarded whole and silently)."""
    with _comp(t, "player_log_names_no_wasteland_error", independent=True):
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
                ["RimMandrake.Wasteland", "RM_WastelandSettings", "RM_WasteCaskBayUtility"]))))
            bad_kind = ("Config error", "Could not resolve cross-reference", "Could not find type named",
                        "Exception", "rror in")
            hits = [ln.strip() for ln in lines if names.search(ln) and any(k in ln for k in bad_kind)]
            general = sum(1 for ln in lines if "Config error" in ln or "Could not resolve cross-reference" in ln)
            _note(t, "Player.log scan", {"lines": len(lines), "hits": hits[:5],
                                         "game-wide config/xref lines (instrument probe)": general})
            if hits:
                _fail("%d Player.log line(s) name this mod's content in an error: %s" % (
                    len(hits), " | ".join(h[:200] for h in hits[:3])))


@suite.chain("defs_resolve")
def defs_resolve(t):
    """Every def this mod ships resolves in the running game and comes from this mod, not a donor. Expected
    names come from the mod's own XML. A control proves the instrument can say 'not found'."""
    with _comp(t, "resolve_probe_sees_absence", independent=True):
        real = "RM_WasteCask"
        rows, missing = _get_defs(t, ["ThingDef/RM_NoSuchWastelandDef_Control", "ThingDef/%s" % real])
        if _live(t):
            found = [r.get("defName") for r in rows if r.get("found")]
            if missing != ["ThingDef/RM_NoSuchWastelandDef_Control"] or found != [real]:
                _fail("the def probe cannot tell present from absent: found=%r notFound=%r" % (found, missing))

    for deftype in sorted(FLOORS):
        with _comp(t, "defs_resolve_%s" % deftype, independent=True):
            names = _BY_TYPE.get(deftype, [])
            if _live(t):
                _need_parse(t)
                if len(names) < FLOORS[deftype]:
                    _fail("source parse found %d %s defs, floor is %d -- a parse failure or an undeclared "
                          "deletion (edit FLOORS deliberately if the mod shrank)" % (len(names), deftype, FLOORS[deftype]))
            rows, missing = _get_defs(t, ["%s/%s" % (deftype, n) for n in names])
            if _live(t):
                if missing:
                    _fail("%d of %d %s not loaded by the game: %s" % (len(missing), len(names), deftype, missing[:8]))
                wrong = [r.get("defName") for r in rows if r.get("packageId") not in OUR_PACKAGES]
                if wrong:
                    _fail("defs resolve but from another mod (shadowed?): %s" % wrong[:6])


@suite.chain("settings_defaults")
def settings_defaults(t):
    """Every Mod Settings field ships at its source default and the assembly is loaded (a static field read
    through jawa/mod_settings_field). Defaults are parsed from RM_WastelandMod.cs. The effect of each
    toggle is checked by the chain named in the walk, not here."""
    with _comp(t, "settings_source_parse_floor", independent=True):
        if _live(t):
            _need_parse(t)
            if len(TOGGLES) < 23 or len(NUMBERS) < 10:
                _fail("settings parse found %d toggles and %d numbers, floors 23 and 10" % (len(TOGGLES), len(NUMBERS)))
    for field in sorted(DEFAULTS):
        with _comp(t, "default_%s" % field, independent=True,
                   toggle=(field if isinstance(DEFAULTS[field], bool) else None)):
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
            if _live(t):
                _ok(r, "mod_settings_field(get %s)" % field)
                if not _same(r.get("value"), DEFAULTS[field]):
                    _fail("%s reads %r; the shipped default is %r (RM_WastelandMod.cs)" % (field, r.get("value"), DEFAULTS[field]))


@suite.chain("settings_roundtrip")
def settings_roundtrip(t):
    """Every `public static` bool/int/float of RM_WastelandMod.cs (found by regex, so a new field is covered
    unasked): read, write a different value, read it back, restore, read the restore. Numerics compare as
    numbers. The settings class is RimMandrake.Wasteland.RM_WastelandSettings."""
    with _comp(t, "roundtrip_probe_finds_fields", independent=True):
        if len(DEFAULTS) < 1:
            _fail("settings regex found no field (blind probe)")
    for field in sorted(DEFAULTS):
        default = DEFAULTS[field]
        with _comp(t, "%s_round_trips" % field, independent=True,
                   toggle=(field if isinstance(default, bool) else None)):
            if not _live(t):
                continue
            def _get():
                r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
                return (r if isinstance(r, dict) else {}).get("value")
            old = _get()
            if old is None:
                _fail("%s: get returned no value" % field)
            if isinstance(default, bool):
                new = not (str(old).lower() == "true")
            elif isinstance(default, int):
                new = int(float(str(old))) + 1      # an Int32 field refuses "3.0" (LIVE 2026-10-07)
            else:
                new = float(str(old)) + 1.0
            try:
                t.set_setting(SETTINGS, {field: new})
                if not _same(_get(), new):
                    _fail("%s: wrote %r, read %r" % (field, new, _get()))
            finally:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=str(old))
            # `old` is the tool's string ('True'): compare a bool field as a bool, a number as a number
            if not _same(_get(), (str(old).lower() == "true") if isinstance(default, bool) else old):
                _fail("%s did not restore to %r (read %r)" % (field, old, _get()))


@suite.chain("biome_roster")
def biome_roster(t):
    """`RM_Wasteland` as the game resolved it (jawa/biome_probe reads the runtime caches, the only tool that
    can see wildAnimals/wildPlants), compared with the mod's own XML."""
    box = {}
    with _comp(t, "biome_probe_ready"):
        r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True, topN=200,
                          find="RM_Smolderback,RM_NoSuchCreatureControl")
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
            # wildAnimals spawn only while animalDensity > 0 (MEASURED from the engine, CLAUDE.md)
            for k in ("animalDensity", "plantDensity"):
                if not (float(row.get(k) or 0) > 0):
                    _fail("%s is %r: a zero density makes the roster dead content" % (k, row.get(k)))
                if k in BIOME_SCALARS and abs(float(row[k]) - BIOME_SCALARS[k]) > 1e-4:
                    _fail("%s live %r != source %r" % (k, row[k], BIOME_SCALARS[k]))

    for kind, expect in (("animals", BIOME_ANIMALS), ("plants", BIOME_PLANTS)):
        with _comp(t, "wild_%s_wired" % kind, independent=True):
            if _live(t):
                _need_parse(t)
                if len(expect) < (12 if kind == "animals" else 12):
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

    with _comp(t, "probe_states_are_honest_and_no_donor_rows", independent=True):
        # The roster is fully owned (WASTELAND_RULED_CONTENT_1): every row is an RM_ port or vanilla. The two
        # controls prove the three-state probe: a real row is 'spawning', an invented one 'absent'.
        if _live(t):
            f = box["find"]
            if f.get("RM_Smolderback") != "spawning" or f.get("RM_NoSuchCreatureControl") != "absent":
                _fail("biome_probe's find states are not trustworthy: %r" % f)
            donors = sorted(n for n in list(box["animals"]) + list(box["plants"])
                            if n.startswith(("RSW_", "RUT_", "SW_")))
            if donors:
                _fail("franchise-tier rows on the franchise-free RM_ biome (Q12): %s" % donors)

    with _comp(t, "biome_extension_opts_into_the_storm_layer", independent=True):
        ext = _field(t, "BiomeDef/%s" % BIOME, "modExtensions")
        if _live(t):
            if not _has(ext, "WastelandStormBiomeExtension"):
                _fail("RM_WastelandStormBiomeExtension is not among the biome's modExtensions, so "
                      "RM_MapComponent_WastelandStorms returns at once on every Wasteland map: %s" % str(ext)[:300])

    with _comp(t, "cinderwire_storm_is_not_on_the_weather_list", independent=True):
        # terminator-only (sheet 6 ban 7): ABSENT from baseWeatherCommonalities until the gate is designed.
        # The control (Clear must be readable) proves the list was actually read.
        wl = _field(t, "BiomeDef/%s" % BIOME, "baseWeatherCommonalities")
        if _live(t):
            if not _has(wl, "Clear") or not _has(wl, ASH):
                _unmeasured(t, "baseWeatherCommonalities did not serialise Clear and %s (got %s): the list "
                               "cannot be trusted either way" % (ASH, str(wl)[:200]))
            if _has(wl, PLASMA):
                _fail("%s is on the biome's weather list; it is terminator-families-only (wasteland.md sec 6)" % PLASMA)
            if not _has(wl, HALO):
                _fail("%s is not on the weather list" % HALO)

    with _comp(t, "no_rain_of_any_kind", independent=True):
        # owner 2026-09-30 by question card: Rain, RainyThunderstorm and ToxRain all weigh 0.
        wl = _field(t, "BiomeDef/%s" % BIOME, "baseWeatherCommonalities")
        if _live(t):
            pairs = {}
            seq = wl if isinstance(wl, list) else (list(wl.items()) if isinstance(wl, dict) else [])
            for item in seq:
                if isinstance(item, dict):
                    vals = list(item.values())
                    if len(vals) == 2 and isinstance(vals[0], str):
                        pairs[vals[0]] = vals[1]
                    elif len(vals) == 2 and isinstance(vals[1], str):
                        pairs[vals[1]] = vals[0]
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    pairs[str(item[0])] = item[1]
            if "Clear" not in pairs:
                _unmeasured(t, "could not read (weather, commonality) pairs out of %s" % str(wl)[:200])
            rainy = dict((k, v) for k, v in pairs.items() if k in ("Rain", "RainyThunderstorm", "ToxRain"))
            nonzero = dict((k, v) for k, v in rainy.items() if float(v or 0) != 0.0)
            if nonzero:
                _fail("the Wastes have no rain, but the weather list carries %s" % nonzero)
            _note(t, "rain rows read", rainy)


@suite.chain("patches_landed")
def patches_landed(t):
    """A patch that matches nothing logs nothing. Four patch bindings, each read back from the running game.
    Guards the known defect that the MovingDunes binding is dark in the composed mod: its
    PatchOperationFindMod names 'Moving Dunes', a mod that no longer exists once it is folded into
    mandrake.rm.biomes (biomes_compose_sweeps.py finding 3)."""
    with _comp(t, "dune_field_binding_on_the_biome", independent=True):
        ext = _field(t, "BiomeDef/%s" % BIOME, "modExtensions")
        if _live(t) and not _has(ext, "DuneFieldExtension"):
            _fail("RM_Wasteland carries no DuneFieldExtension, so ash never drifts. Patches/"
                  "RM_Wasteland_MovingDunesBinding.xml is wrapped in PatchOperationFindMod 'Moving Dunes', which "
                  "matches nothing once MovingDunes is composed into mandrake.rm.biomes: %s" % str(ext)[:200])

    with _comp(t, "dune_weather_binding_on_the_ash_storm", independent=True):
        ext = _field(t, "WeatherDef/%s" % ASH, "modExtensions")
        if _live(t) and not _has(ext, "DuneWeatherExtension"):
            _fail("%s carries no DuneWeatherExtension (same FindMod 'Moving Dunes' patch): %s" % (ASH, str(ext)[:200]))

    with _comp(t, "dune_material_def_exists", independent=True):
        rows, missing = _get_defs(t, ["RimMandrake.MovingDunes.RM_DuneMaterialDef/RM_Dunes_WastelandAsh"])
        if _live(t) and (missing or not rows):
            _fail("RM_Dunes_WastelandAsh (added by the MovingDunes binding patch) is not in the game: %r" % missing)

    with _comp(t, "brine_scatters_registered_on_the_biome", independent=True):
        steps = _field(t, "BiomeDef/%s" % BIOME, "extraGenSteps")
        if _live(t):
            lacking = [g for g in sorted(_BY_TYPE.get("GenStepDef", [])) if not _has(steps, g)]
            if not _BY_TYPE.get("GenStepDef"):
                _fail("source parse found no GenStepDef")
            if lacking:
                _fail("BiomeDef extraGenSteps lacks %s: RM_WastelandBrine_ScatterRegister.xml matched nothing, so no "
                      "deposit ever scatters on a generated Wasteland map" % lacking)


@suite.chain("flyer_state")
def flyer_state(t):
    """The Grimewing flies in the fiction, so it flies in the game: `Pawn_FlightTracker.CanEverFly` is a
    stat read (MaxFlightTime > 0), checked with a state read only (never a live flight, CLAUDE.md). The
    grounded control proves the read can say False."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_flyer"):
            _reset_pad(t)
            x, z = t.anchor
            box["fly"] = _spawn(t, "RM_Grimewing", x, z, "none")
            box["walk"] = _spawn(t, "RM_Scumslider", x + 4, z, "none")

        with _comp(t, "grimewing_can_ever_fly", independent=True):
            r = t.bridge_call("jawa/pawn_flight", action="report", pawn=box.get("fly"))
            if _live(t):
                rows = _ok(r, "pawn_flight").get("pawns") or []
                if not rows or "canEverFly" not in rows[0]:
                    _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
                if rows[0]["canEverFly"] is not True:
                    _fail("RM_Grimewing canEverFly is %r (maxFlightTimeStat %r): MaxFlightTime must be > 0" % (
                        rows[0]["canEverFly"], rows[0].get("maxFlightTimeStat")))

        with _comp(t, "ground_creature_cannot_fly_control", independent=True):
            r = t.bridge_call("jawa/pawn_flight", action="report", pawn=box.get("walk"))
            if _live(t):
                rows = _ok(r, "pawn_flight").get("pawns") or []
                if not rows or "canEverFly" not in rows[0]:
                    _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
                if rows[0]["canEverFly"] is not False:
                    _fail("RM_Scumslider canEverFly is %r: the flight read cannot tell a walker from a flyer" % rows[0]["canEverFly"])
    finally:
        _teardown(t)

# ----------------------------------------------------------------------------- the storms

def _msg_count(blob, frag):
    return blob.count(frag.lower()) if frag else 0


def _storm_site(t, box):
    """A Wasteland map, a clean pad, a settled colonist under open sky, no pollution anywhere."""
    _need_wasteland(t)
    _reset_pad(t)
    box["whole"] = _map_rect(t)
    _pollution(t, box["whole"], False)
    x, z = t.anchor
    box["c"] = _spawn(t, "Colonist", x, z, "player")
    if _live(t):
        _settle(t, box["c"])
        box["cinder0"] = len(_things(t, "RM_Cinderfelt", box["whole"]))
        if _hed(t, box["c"], "ToxicBuildup") > 0:
            _fail("precondition: the fresh colonist already carries ToxicBuildup")


@suite.chain("storm_ash_on")
def storm_ash_on(t):
    """The ash storm (RM_MapComponent_WastelandStorms): under open sky it doses a pawn with the vanilla toxic
    buildup, lays pollution on random unroofed cells as it blows, and when it ends germinates the cinderfelt
    on part of that fresh fall. Needs a map whose biome opted in (RM_WastelandStormBiomeExtension)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_ash"):
            _storm_site(t, box)
            _weather(t, ASH)

        with _comp(t, "ash_storm_doses_an_unroofed_pawn", independent=True, toggle="stormDoseEnabled"):
            _wait_dose(t, 600)
            if _live(t):
                sev = _hed(t, box["c"], "ToxicBuildup")
                _note(t, "ToxicBuildup after 600 ticks of ash storm", sev)
                if not sev > 0:
                    _fail("an unroofed colonist took no ToxicBuildup in 600 ticks of %s (airborneToxicFactor 1.0): "
                          "the storm layer is not running on this map" % ASH)

        with _comp(t, "ash_fall_pollutes_the_ground", independent=True, toggle="ashFallPollutionEnabled"):
            t.wait_ticks(2400)
            n, ever = _pollution(t, box["whole"], False)      # cleaning flips exactly the cells the fall polluted
            if _live(t):
                _note(t, "cells polluted by 3000 ticks of ash fall", {"cellsChanged": n, "everPollutable": ever})
                if ever == 0:
                    _unmeasured(t, "no cell on this map is pollutable (cellsEverPollutable 0), so fall cannot be read")
                if n <= 0:
                    _fail("3000 ticks of %s polluted no cell (fallCellsPerDay 900, ~16 expected): ashFallPollutionEnabled "
                          "is on" % ASH)

        with _comp(t, "ash_storm_end_germinates_cinderfelt", independent=True, toggle="cinderfeltGerminationEnabled"):
            _weather(t, "Clear")
            t.wait_ticks(700)                  # past the next 250-tick fall check, which notices the weather ended
            if _live(t):
                after = len(_things(t, "RM_Cinderfelt", box["whole"]))
                _note(t, "RM_Cinderfelt before/after", [box["cinder0"], after])
                if not after > box["cinder0"]:
                    _fail("no cinderfelt germinated after the storm ended (%d before, %d after; ~16 fall cells x 35%% "
                          "should seed several)" % (box["cinder0"], after))
    finally:
        _weather_reset(t)
        _teardown(t)


@suite.chain("storm_ash_off")
def storm_ash_off(t):
    """The three storm-layer toggles OFF: the same ash storm doses nobody, pollutes nothing and seeds
    nothing. storm_ash_on is the control that the same site CAN show each effect."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_ash_off"):
            _storm_site(t, box)
            _set(t, stormDoseEnabled=False, ashFallPollutionEnabled=False, cinderfeltGerminationEnabled=False)
            _weather(t, ASH)

        with _comp(t, "dose_off_means_no_buildup", independent=True, toggle="stormDoseEnabled"):
            _wait_dose(t, 600)
            if _live(t):
                sev = _hed(t, box["c"], "ToxicBuildup")
                if sev > 0:
                    _fail("ToxicBuildup %.3f after 600 ticks of ash storm with stormDoseEnabled=false" % sev)

        with _comp(t, "fall_off_means_no_pollution", independent=True, toggle="ashFallPollutionEnabled"):
            t.wait_ticks(1800)
            n, ever = _pollution(t, box["whole"], False)
            if _live(t):
                if ever == 0:
                    _unmeasured(t, "no cell on this map is pollutable")
                if n != 0:
                    _fail("%d cells polluted by 2400 ticks of ash fall with ashFallPollutionEnabled=false and "
                          "cinderfeltGerminationEnabled=false" % n)

        with _comp(t, "germination_off_means_no_cinderfelt", independent=True, toggle="cinderfeltGerminationEnabled"):
            _weather(t, "Clear")
            t.wait_ticks(700)
            if _live(t):
                after = len(_things(t, "RM_Cinderfelt", box["whole"]))
                if after > box["cinder0"]:
                    _fail("cinderfelt count rose %d -> %d with cinderfeltGerminationEnabled=false" % (box["cinder0"], after))
    finally:
        _restore(t, ["stormDoseEnabled", "ashFallPollutionEnabled", "cinderfeltGerminationEnabled"])
        _weather_reset(t)
        _teardown(t)


def _named_storm_chain(weather, label):
    def chain(t):
        _enter(t)
        box = {}
        try:
            with _comp(t, "site_ready_%s" % label):
                _storm_site(t, box)
                if _live(t) and not (WARN[weather] and UNLEASH[weather]):
                    _fail("source parse found no warning/unleashed message on %s" % weather)
                _set(t, namedStormWarningFactor=0.25)           # 2500 -> 625 ticks of warning
                box["before"] = _messages(t)
                _weather(t, weather)

            with _comp(t, "warning_message_arrives", independent=True, toggle="namedStormPhasesEnabled"):
                t.wait_ticks(40)
                if _live(t):
                    blob = _messages(t)
                    if _msg_count(blob, WARN[weather]) <= _msg_count(box["before"], WARN[weather]):
                        _fail("no new warning message starting %r after the storm began" % WARN[weather])

            with _comp(t, "dose_is_held_during_the_warning", independent=True, toggle="namedStormPhasesEnabled"):
                t.wait_ticks(420)                                # tick ~460, inside the 625-tick warning
                if _live(t):
                    sev = _hed(t, box["c"], "ToxicBuildup")
                    if sev > 0:
                        _fail("ToxicBuildup %.3f at tick ~460, inside the warning: IsHolding is not holding the storm "
                              "layer's dose" % sev)

            with _comp(t, "unleashed_message_arrives", independent=True, toggle="namedStormPhasesEnabled"):
                t.wait_ticks(200)                                # tick ~660, past 625
                if _live(t):
                    blob = _messages(t)
                    if _msg_count(blob, UNLEASH[weather]) <= _msg_count(box["before"], UNLEASH[weather]):
                        _fail("no new message starting %r after the warning ended" % UNLEASH[weather])

            with _comp(t, "dose_begins_after_the_warning", independent=True, toggle="stormDoseEnabled"):
                _wait_dose(t, 450)
                if _live(t):
                    sev = _hed(t, box["c"], "ToxicBuildup")
                    if not sev > 0:
                        _fail("no ToxicBuildup 1100 ticks into %s, 475 after the warning ended" % weather)
        finally:
            _restore(t, ["namedStormWarningFactor"])
            _weather_reset(t)
            _teardown(t)
    chain.__doc__ = ("%s: a quiet warning phase (message), the storm layer's dose held until it ends, then the "
                     "unleashed message and the dose (RM_MapComponent_StormPhases). Warning shortened to 25%% by "
                     "namedStormWarningFactor, restored in finally." % weather)
    return chain


suite.chain("named_storm_halo")(_named_storm_chain(HALO, "halo"))
suite.chain("named_storm_cinderwire")(_named_storm_chain(PLASMA, "cinderwire"))


@suite.chain("named_storm_phases_off")
def named_storm_phases_off(t):
    """namedStormPhasesEnabled=false: the deadlight halo strikes at once, with no warning message and no hold."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_phases_off"):
            _storm_site(t, box)
            _set(t, namedStormPhasesEnabled=False)
            box["before"] = _messages(t)
            _weather(t, HALO)

        with _comp(t, "no_warning_message_when_off", independent=True, toggle="namedStormPhasesEnabled"):
            t.wait_ticks(40)
            if _live(t):
                blob = _messages(t)
                if _msg_count(blob, WARN[HALO]) > _msg_count(box["before"], WARN[HALO]):
                    _fail("a warning message %r appeared with namedStormPhasesEnabled=false" % WARN[HALO])

        with _comp(t, "dose_starts_at_once_when_off", independent=True, toggle="namedStormPhasesEnabled"):
            _wait_dose(t, 420)
            if _live(t):
                sev = _hed(t, box["c"], "ToxicBuildup")
                if not sev > 0:
                    _fail("no ToxicBuildup 460 ticks into the halo with namedStormPhasesEnabled=false: the warning "
                          "hold is still holding the dose")
    finally:
        _restore(t, ["namedStormPhasesEnabled"])
        _weather_reset(t)
        _teardown(t)


# ------------------------------------------------------------------------ ambient dose and heat

@suite.chain("smolderback_room")
def smolderback_room(t):
    """The Smolderback is a living furnace that doses its room (RM_CompAmbientDose, doseRoomWhenIndoors) and
    pushes heat (RM_CompRadiothermalHeat). Room A holds the creature and a colonist; room B, 14 cells away,
    holds only a colonist and is the control for both the dose and the heat."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_smolderback"):
            _reset_pad(t)
            x, z = t.anchor
            ia = _make_room(t, x - 10, z - 3, sealed=True)
            ib = _make_room(t, x + 4, z - 3, sealed=True)
            box["ia"], box["ib"] = ia, ib
            box["sb"] = _spawn(t, "RM_Smolderback", ia[0] + 2, ia[1] + 2, "none")
            box["ca"] = _spawn(t, "Colonist", ia[0] + 3, ia[1] + 3, "player")
            box["cb"] = _spawn(t, "Colonist", ib[0] + 2, ib[1] + 2, "player")
            if _live(t):
                _settle(t, box["ca"])
                _settle(t, box["cb"])
                if _room_temp(t, ib[0] + 1, ib[1] + 1) >= 24.0:
                    _unmeasured(t, "the control room is already %s C, at or past the heat pusher's 26 C cap, so a "
                                   "heating effect cannot be told from none" % _room_temp(t, ib[0] + 1, ib[1] + 1))
            _wait_dose(t, 900)

        with _comp(t, "smolderback_doses_its_own_room", independent=True, toggle="ambientDoseEnabled"):
            if _live(t):
                sev = _hed(t, box["ca"], "ToxicBuildup")
                _note(t, "ToxicBuildup in the smolderback's room after 900 ticks", sev)
                if not sev > 0:
                    _fail("the colonist sharing a sealed room with a smolderback took no ToxicBuildup in 900 ticks "
                          "(toxicFactor 0.35, doseRoomWhenIndoors)")

        with _comp(t, "dose_stays_in_its_room", independent=True, toggle="ambientDoseEnabled"):
            if _live(t):
                sev = _hed(t, box["cb"], "ToxicBuildup")
                if sev > 0:
                    _fail("the colonist in the OTHER room, 14 cells away, took ToxicBuildup %.3f: the dose is not "
                          "room-limited" % sev)

        with _comp(t, "smolderback_heats_its_own_room", independent=True, toggle="radiothermalHeatEnabled"):
            ta = _room_temp(t, box["ia"][0] + 1, box["ia"][1] + 1)
            tb = _room_temp(t, box["ib"][0] + 1, box["ib"][1] + 1)
            if _live(t):
                box["ta0"] = ta
                _note(t, "room temperature with / without the smolderback", [ta, tb])
                if not ta - tb >= 1.0:
                    _fail("the smolderback's room is %.1f C against the control's %.1f C after 900 ticks (heatPerSecond "
                          "12 into a 25-cell room should be several degrees)" % (ta, tb))

        with _comp(t, "dose_off_stops_dosing", independent=True, toggle="ambientDoseEnabled"):
            t.bridge_call("jawa/pawn_health", pawn=box.get("ca"), action="remove", hediff="ToxicBuildup")
            _set(t, ambientDoseEnabled=False)
            _wait_dose(t, 700)
            if _live(t):
                sev = _hed(t, box["ca"], "ToxicBuildup")
                if sev > 0:
                    _fail("ToxicBuildup %.3f returned within 700 ticks with ambientDoseEnabled=false" % sev)

        with _comp(t, "heat_off_stops_heating", independent=True, toggle="radiothermalHeatEnabled"):
            before = _room_temp(t, box["ia"][0] + 1, box["ia"][1] + 1)          # read NOW: earlier arms ran on
            _set(t, radiothermalHeatEnabled=False)
            t.wait_ticks(900)
            ta1 = _room_temp(t, box["ia"][0] + 1, box["ia"][1] + 1)
            if _live(t):
                if ta1 > before + 0.3:
                    _fail("the room kept warming (%.1f -> %.1f C) with radiothermalHeatEnabled=false" % (before, ta1))

        with _comp(t, "master_switch_off_stops_dosing", independent=True, toggle="wastelandEnabled"):
            # the master switch ANDs into every per-feature gate; the first component above is its control (the
            # same creature in the same room DID dose with it on)
            _restore(t, ["ambientDoseEnabled"])
            t.bridge_call("jawa/pawn_health", pawn=box.get("ca"), action="remove", hediff="ToxicBuildup")
            _set(t, wastelandEnabled=False)
            _wait_dose(t, 700)
            if _live(t):
                sev = _hed(t, box["ca"], "ToxicBuildup")
                if sev > 0:
                    _fail("ToxicBuildup %.3f returned within 700 ticks with wastelandEnabled=false (the master switch)" % sev)
    finally:
        _restore(t, ["ambientDoseEnabled", "radiothermalHeatEnabled", "wastelandEnabled"])
        _teardown(t)


# ------------------------------------------------------------------------------ processors

@suite.chain("processor_animals")
def processor_animals(t):
    """The sloghog (bezoars) and the sootgrazer (soot bricks) are processor animals (RM_CompProcessorGatherable,
    a CompMilkable): full rate on polluted ground and 35% off it (the inspect pane says so), a forced gather
    places the product, and processorGatherEnabled=false takes the growth off the pane. Room P is polluted,
    room C is clean."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_processors"):
            _reset_pad(t)
            x, z = t.anchor
            ip = _make_room(t, x - 10, z - 3, sealed=True)
            ic = _make_room(t, x + 4, z - 3, sealed=True)
            n, ever = _pollution(t, _rs(ip), True)
            _pollution(t, _rs(ic), False)
            if _live(t) and (ever == 0 or n == 0):
                _unmeasured(t, "the room floor is not pollutable (changed %d, ever %d), so feed ground cannot be made" % (n, ever))
            box["hog_p"] = _spawn(t, "RM_Sloghog", ip[0] + 1, ip[1] + 1, "player")
            box["graz_p"] = _spawn(t, "RM_Sootgrazer", ip[0] + 3, ip[1] + 3, "player")
            box["hog_c"] = _spawn(t, "RM_Sloghog", ic[0] + 2, ic[1] + 2, "player")
            box["h"] = _spawn(t, "Colonist", x - 1, z + 8, "player")
            if _live(t):
                _settle(t, box["h"])
            t.wait_ticks(700)                   # onFeed is re-derived every 250 ticks (starts true)

        with _comp(t, "polluted_ground_is_feed_ground", independent=True):
            s = _inspect(t, box.get("hog_p"))
            if _live(t):
                if "bezoar growth" not in s.lower():
                    _fail("the sloghog's inspect pane shows no 'Bezoar growth' (comp inactive or def comp dropped): %s" % s[:200])
                if "off feed ground" in s.lower():
                    _fail("a sloghog standing on polluted ground reads 'off feed ground: slow': %s" % s[:200])

        with _comp(t, "clean_ground_is_slow_ground", independent=True):
            s = _inspect(t, box.get("hog_c"))
            if _live(t) and "off feed ground" not in s.lower():
                _fail("a sloghog on clean ground does not read 'off feed ground: slow' (the feed-ground gate is "
                      "not gating): %s" % s[:200])

        with _comp(t, "sootgrazer_is_a_soot_brick_press_on_polluted_ground", independent=True):
            s = _inspect(t, box.get("graz_p"))
            if _live(t):
                if "soot brick press" not in s.lower():
                    _fail("the sootgrazer's inspect pane shows no 'Soot brick press': %s" % s[:200])
                if "off feed ground" in s.lower():
                    _fail("a sootgrazer on polluted ground reads 'off feed ground: slow': %s" % s[:200])

        for label, key, product in (("sloghog", "hog_p", "RM_ContaminantBezoar"), ("sootgrazer", "graz_p", "RM_SootBrick")):
            with _comp(t, "gather_places_%s" % product, independent=True):
                whole = _map_rect(t)
                before = len(_things(t, product, whole))
                r = t.bridge_call("jawa/animal_resource_force", pawn=box.get(key), mode="gatherable",
                                  targetFullness=1.0, gatherNow=True, doer=box.get("h"))
                if _live(t):
                    _ok(r, "animal_resource_force(%s)" % label)
                    gt = r.get("gathered") or r.get("gatheredThing") or {}   # the tool's key is "gathered" (LIVE 2026-10-08)
                    if gt.get("resourcePlacedOnMap") is None:
                        _unmeasured(t, "animal_resource_force could not resolve the resource def: %r" % gt)
                    after = len(_things(t, product, whole))
                    if gt.get("resourcePlacedOnMap") is not True or after <= before:
                        _fail("a full %s gathered but no %s was placed on the map (placed flag %r, count %d -> %d): %r"
                              % (label, product, gt.get("resourcePlacedOnMap"), before, after, gt))

        with _comp(t, "gather_off_hides_the_growth_pane", toggle="processorGatherEnabled"):
            _set(t, processorGatherEnabled=False)
            s = _inspect(t, box.get("hog_p"))
            if _live(t) and "bezoar growth" in s.lower():
                _fail("the sloghog still shows 'Bezoar growth' with processorGatherEnabled=false (Active ignores the "
                      "toggle): %s" % s[:200])
    finally:
        _restore(t, ["processorGatherEnabled"])
        _teardown(t)


# --------------------------------------------------------------------------------- the gripper

@suite.chain("gripper")
def gripper(t):
    """The wild gripper always carries something (RM_CompGripperThief), swaps its scrap for anything worth more
    (RM_JobDriver_GripperSteal), drops its haul when hurt, and never steals once tamed. Each toggle's OFF arm
    spawns a fresh gripper and reads its inspect pane."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_gripper"):
            _reset_pad(t)
            x, z = t.anchor
            box["x"], box["z"] = x, z
            box["g1"] = _spawn(t, "RM_Gripper", x, z, "none")
            _spawn_thing(t, "Gold", x + 4, z, 5)

        with _comp(t, "wild_gripper_spawns_carrying_scrap", independent=True, toggle="gripperSpawnsCarrying"):
            s = _inspect(t, box.get("g1"))
            if _live(t):
                if "gripping:" not in s.lower():
                    _fail("a freshly spawned wild gripper holds nothing (startingJunkChance 1): %s" % s[:200])
                _note(t, "gripper's starting haul", s[:120])

        with _comp(t, "steal_swaps_scrap_for_gold", independent=True, toggle="gripperTheftEnabled"):
            gold = _things(t, "Gold", _pad_rect(t))
            if _live(t) and not gold:
                _fail("precondition: no Gold stack on the pad")
            r = _order(t, pawnId=box.get("g1"), jobDef="RM_GripperSteal",
                              targetAId=(gold[0].get("id") if gold else None), count=5, waitTicks=60, timeoutSeconds=60)
            if _live(t) and not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
                _unmeasured(t, "ordered_job did not start RM_GripperSteal on the animal: %r" % r)
            t.wait_ticks(500)
            s = _inspect(t, box.get("g1"))
            if _live(t) and "gold" not in s.lower():
                _fail("after a forced steal job the gripper's pane does not show gold: %s" % s[:200])

        with _comp(t, "hurt_gripper_drops_its_haul", independent=True):
            # dropOnHarmChance 0.5 per damaging hit: ten one-point hits miss every time with probability 0.1%
            for _ in range(10):
                t.bridge_call("jawa/damage", thingId=box.get("g1"), damageDef="Blunt", amount=1)
            if _live(t):
                rows = [p for p in _pawns(t) if p.get("id") == box.get("g1")]
                if not rows:
                    _unmeasured(t, "the gripper died under ten 1-point hits, so a drop cannot be read from its pane")
                s = _inspect(t, box.get("g1"))
                if "gripping:" in s.lower():
                    _fail("ten damaging hits (50%% drop chance each) and the gripper still holds: %s" % s[:200])

        with _comp(t, "theft_off_gripper_spawns_empty_handed", independent=True, toggle="gripperTheftEnabled"):
            _set(t, gripperTheftEnabled=False)
            g = _spawn(t, "RM_Gripper", box["x"] + 8, box["z"] + 6, "none")
            s = _inspect(t, g)
            if _live(t) and "gripping:" in s.lower():
                _fail("a gripper spawned carrying with gripperTheftEnabled=false: %s" % s[:200])
            _restore(t, ["gripperTheftEnabled"])

        with _comp(t, "spawns_carrying_off_gripper_spawns_empty_handed", independent=True, toggle="gripperSpawnsCarrying"):
            _set(t, gripperSpawnsCarrying=False)
            g = _spawn(t, "RM_Gripper", box["x"] - 8, box["z"] + 6, "none")
            s = _inspect(t, g)
            if _live(t) and "gripping:" in s.lower():
                _fail("a gripper spawned carrying with gripperSpawnsCarrying=false: %s" % s[:200])
            _restore(t, ["gripperSpawnsCarrying"])

        with _comp(t, "tamed_gripper_never_steals", independent=True, toggle="gripperTheftEnabled"):
            # The wild grippers above outlive _teardown (jawa/destroy_batch never destroys a pawn) and would steal
            # this Gold themselves, muddying the "still lying there" read. Remove every wild animal first.
            t.bridge_call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
            _spawn_thing(t, "Gold", box["x"] + 4, box["z"] - 6, 5)
            g = _spawn(t, "RM_Gripper", box["x"], box["z"] - 6, "player")
            gold_rect = "%d,%d,3,3" % (box["x"] + 3, box["z"] - 7)
            gold = _things(t, "Gold", gold_rect)
            if _live(t) and not gold:
                _fail("precondition: the second Gold stack is missing")
            r = _order(t, pawnId=g, jobDef="RM_GripperSteal",
                              targetAId=(gold[0].get("id") if gold else None), count=5, waitTicks=60, timeoutSeconds=60)
            # RM_JobDriver_GripperSteal carries a job-wide FailOn(pawn.Faction != null), so on a tamed gripper the
            # order is ACCEPTED and ends at once (LIVE 2026-10-08: accepted True, afterJobDef GotoWander, success
            # False). That is the property under test, not a refused order. Only a non-accepted order is UNMEASURED;
            # the wild control (steal_swaps_scrap_for_gold) proves the same order runs on a factionless gripper.
            if _live(t) and (r or {}).get("accepted") is not True:
                _unmeasured(t, "ordered_job did not accept the steal order on the tamed gripper: %r" % r)
            _note(t, "tamed gripper's job after the order", {k: (r or {}).get(k) for k in
                                                             ("success", "accepted", "afterJobDef", "nowRunningRequested")})
            t.wait_ticks(500)
            s = _inspect(t, g)
            if _live(t) and "gold" in s.lower():
                _fail("a TAMED gripper stole (FailOn faction != null should end the job): %s" % s[:200])
            # evidence only: a leftover colonist may legitimately haul the Gold, so its absence is not a verdict
            _note(t, "Gold still beside the tamed gripper", [_stack(m) for m in _things(t, "Gold", gold_rect)])
    finally:
        _restore(t, ["gripperTheftEnabled", "gripperSpawnsCarrying"])
        _teardown(t)


# ------------------------------------------------------------------------------------ flora

@suite.chain("flora_harvest")
def flora_harvest(t):
    """The wasteland flora that name a harvested item yield it when a handler harvests a grown plant
    (plant.harvestedThingDef, read from the mod's own flora XML): one row of full-grown plants per species,
    one handler with hauling off, a forced Harvest on each in turn, the product read the moment its plant is cut."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_flora"):
            _reset_pad(t, terrain="Soil")
            x, z = t.anchor
            if _live(t):
                _need_parse(t)
                if len(FLORA_PRODUCTS) < 4:
                    _fail("source parse found %d plants with a harvestedThingDef, expected 4" % len(FLORA_PRODUCTS))
            box["handler"] = _spawn(t, "Colonist", x - 10, z, "player")
            if _live(t):
                _settle(t, box["handler"])
            # JobDriver_PlantWork rolls Rand.Value > PlantHarvestYield per harvest when harvestFailable (RimSage 1.6).
            # Bushes and ground plants (PlantBase) are failable, so Plants 20 takes the roll out of the verdict; trees
            # (TreeBase: RM_VaultRoot, RM_Pusberry) inherit harvestFailable=false and never roll at all.
            t.bridge_call("jawa/set_pawn_skill", pawn=box.get("handler"), skill="Plants", level=20)
            # The handler must not haul the yield away before it is read.
            t.bridge_call("jawa/set_work_priority", pawnId=box.get("handler"), workType="Hauling", priority=0)
            # LIVE 2026-10-08 (x2): RawBerries never arrived from a grown RM_Pusberry while the other three yielded.
            # Cause in the FIXTURE: jawa/destroy_batch never destroys a pawn, so the gripper chain's wild grippers
            # (theft back ON after its restore) and the map's wild animals were still on the pad, and the four
            # harvests were queued and read once after 4000 ticks. The berries (second in the queue) lay longest:
            # stealable, edible and haulable. Clear every non-colonist, then harvest and read ONE plant at a time.
            t.bridge_call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
            box["plants"] = {}
            for i, (plant, product) in enumerate(FLORA_PRODUCTS):
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (plant, x + 2 * i, z + 4), growth=1.0)
            if _live(t):
                for plant, product in FLORA_PRODUCTS:
                    rows = _things(t, plant, _pad_rect(t))
                    if not rows:
                        _fail("set_plants placed no %s" % plant)
                    box["plants"][plant] = rows[0].get("id")
                    if _things(t, product, _pad_rect(t)):
                        _fail("precondition: %s already lying on the pad" % product)

        for plant, product in FLORA_PRODUCTS:
            with _comp(t, "harvest_yields_%s_from_%s" % (product, plant), independent=True):
                _order(t, pawnId=box.get("handler"), jobDef="Harvest",
                       targetAId=box.get("plants", {}).get(plant), waitTicks=60)
                gone = False
                for _ in range(16):                   # <= 4000 ticks; stop as soon as the plant is cut
                    t.wait_ticks(250)
                    if not _live(t) or not _things(t, plant, _pad_rect(t)):
                        gone = True
                        break
                if _live(t):
                    made = _things(t, product, _pad_rect(t))
                    _note(t, "%s stacks" % product, [_stack(m) for m in made])
                    if not gone:
                        _unmeasured(t, "the handler never finished harvesting the %s in 4000 ticks" % plant)
                    if not made:
                        _fail("no %s right after a forced harvest cut a grown %s (harvestedThingDef is wired in the "
                              "def; the yield never arrived)" % (product, plant))
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- the brine battery

@suite.chain("brine_deposits")
def brine_deposits(t):
    """The brine-battery archetype: the deposit GenSteps place their deposit on RM_WastelandBrineShallow
    terrain, each deposit mines to its item, and the raw brineleech (RM_Drazz) gives RM_BrineShock when eaten."""
    _enter(t)
    box = {}
    deposits = (("RM_ScatterWastelandBrineTekk", "RM_BrineDeposit_Tekk", "RM_Tekk"),
                ("RM_ScatterWastelandBrineDrazz", "RM_BrineDeposit_Drazz", "RM_Drazz"),
                ("RM_ScatterWastelandBrinePlate", "RM_BrineDeposit_BrinePlate", "RM_BrinePlate"))
    try:
        with _comp(t, "site_ready_brine"):
            _reset_pad(t)
            x, z = t.anchor
            patch = (x - 3, z - 3, 9, 3)
            t.bridge_call("jawa/set_terrain_batch", ops="RM_WastelandBrineShallow:%s" % _rs(patch))
            if _live(t):
                got = t.bridge_call("jawa/get_terrain_batch", rects=_rs(patch))
                _ok(got, "get_terrain_batch")
                if "RM_WastelandBrineShallow" not in str(got):
                    _fail("the brine patch did not take RM_WastelandBrineShallow terrain: %s" % str(got)[:200])

        for i, (gen, building, item) in enumerate(deposits):
            with _comp(t, "scatter_places_%s" % building, independent=True, toggle="brineDepositsEnabled"):
                x, z = t.anchor
                cell = "%d,%d" % (x - 2 + 3 * i, z - 2)
                r = t.bridge_call("jawa/scatter_at", genStepDef=gen, at=cell)
                if _live(t):
                    _ok(r, "scatter_at(%s)" % gen)
                    if r.get("threw"):
                        _fail("%s threw: %s" % (gen, r.get("threw")))
                    if not _things(t, building, _pad_rect(t)):
                        _fail("%s ran at %s on brine terrain and left no %s" % (gen, cell, building))

        for gen, building, item in deposits:
            with _comp(t, "%s_mines_to_%s" % (building, item), independent=True):
                spec = "ThingDef/%s" % building
                b = _field(t, spec, "building")
                if _live(t):
                    blob = list(_flat(b))
                    if item not in blob:
                        _fail("%s.building does not name mineableThing %s: %s" % (building, item, blob[:12]))

        with _comp(t, "raw_brineleech_gives_brine_shock", independent=True):
            x, z = t.anchor
            who = _spawn(t, "Colonist", x, z + 8, "player")
            if _live(t):
                _settle(t, who)
            _spawn_thing(t, "RM_Drazz", x + 1, z + 8, 1)
            food = _things(t, "RM_Drazz", "%d,%d,3,3" % (x, z + 7))
            if _live(t) and not food:
                _fail("precondition: no RM_Drazz on the floor")
            r = _order(t, pawnId=who, jobDef="Ingest",
                              targetAId=(food[0].get("id") if food else None), count=1, waitTicks=60, timeoutSeconds=60)
            if _live(t) and not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
                _unmeasured(t, "ordered_job did not start Ingest on RM_Drazz: %r" % r)
            t.wait_ticks(600)
            if _live(t):
                sev = _hed(t, who, "RM_BrineShock")
                if not sev > 0:
                    _fail("eating raw RM_Drazz gave no RM_BrineShock (IngestionOutcomeDoer_GiveHediff)")
    finally:
        _teardown(t)


# ------------------------------------------------------------------------- casks and the bay

def _cask_pad(t, box):
    """A clean pad with a clean pollution slate and the rects the cask chains read."""
    _reset_pad(t)
    x, z = t.anchor
    box["x"], box["z"] = x, z
    for key, dx in (("ra", -8), ("rb", 4), ("rc", 14)):
        box[key] = (x + dx - 4, z - 4, 9, 9) if key != "rc" else (x - 4, z + 6, 9, 9)


def _dose(s):
    m = re.search(r"stored dose:\s*([0-9]+\.?[0-9]*)", s.lower())
    return float(m.group(1)) if m else None


@suite.chain("cask_leaks")
def cask_leaks(t):
    """The waste cask (RM_CompWasteCask): intact it is inert; breached below half its hit points it leaks tox
    gas and pollution, drains its stored dose, and is never silent (message, alert, inspect line). With
    caskLeaksEnabled=false it is inert. Cask A intact, cask B breached, cask D breached with leaks off."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_casks"):
            _cask_pad(t, box)
            x, z = box["x"], box["z"]
            for rect in (box["ra"], box["rb"], box["rc"]):
                _pollution(t, _rs(rect), False)
            _spawn_thing(t, "RM_WasteCask", x - 8, z, 1)
            _spawn_thing(t, "RM_WasteCask", x + 8, z, 1)
            if _live(t):
                a = _things(t, "RM_WasteCask", _rs(box["ra"]))
                b = _things(t, "RM_WasteCask", _rs(box["rb"]))
                box["a"], box["b"] = _first_id(a, "cask A"), _first_id(b, "cask B")
                box["dose0"] = _dose(_inspect(t, box["b"]))
                if box["dose0"] is None:
                    _unmeasured(t, "the cask's inspect pane shows no 'Stored dose'")
            t.bridge_call("jawa/set_thing_props", thing=box.get("b"), hitPoints=30)
            t.wait_ticks(700)                  # CompTickRare every 250 ticks: at least two leak checks

        with _comp(t, "intact_cask_is_inert", independent=True):
            s = _inspect(t, box.get("a"))
            n, ever = _pollution(t, _rs(box["ra"]), False)
            if _live(t):
                if "leaking" in s.lower():
                    _fail("an intact waste cask reads LEAKING: %s" % s[:200])
                if n:
                    _fail("%d cells polluted around the intact cask" % n)

        with _comp(t, "breached_cask_leaks_loudly", independent=True, toggle="caskLeaksEnabled"):
            s = _inspect(t, box.get("b"))
            n, ever = _pollution(t, _rs(box["rb"]), False)
            msgs = _messages(t)
            al = t.bridge_call("jawa/alerts_list")
            if _live(t):
                if "leaking" not in s.lower():
                    _fail("a cask at 30 of 100 hit points does not read LEAKING: %s" % s[:200])
                if ever == 0:
                    _unmeasured(t, "no cell around the cask is pollutable")
                if n <= 0:
                    _fail("a breached cask polluted no cell in 700 ticks (leakPollutionCells 3)")
                _note(t, "leak message still on the live list", ("breached" in msgs or "leaking" in msgs))
                if not _has(al, "waste leaking"):
                    _fail("the 'Waste leaking' alert is not active: %s" % str(al)[:200])

        with _comp(t, "leaking_drains_the_stored_dose", independent=True):
            d = _dose(_inspect(t, box.get("b")))
            if _live(t):
                if d is None:
                    _unmeasured(t, "no 'Stored dose' on the cask pane")
                if not d < box["dose0"]:
                    _fail("stored dose %.2f did not fall from %.2f while leaking (dosePerLeak 0.05 per pulse)" % (d, box["dose0"]))

        with _comp(t, "leaks_off_makes_a_breached_cask_inert", independent=True, toggle="caskLeaksEnabled"):
            _set(t, caskLeaksEnabled=False)
            _spawn_thing(t, "RM_WasteCask", box["x"], box["z"] + 10, 1)
            d_rows = _things(t, "RM_WasteCask", _rs(box["rc"]))
            if _live(t):
                box["d"] = _first_id(d_rows, "cask D")
            t.bridge_call("jawa/set_thing_props", thing=box.get("d"), hitPoints=30)
            t.wait_ticks(700)
            s = _inspect(t, box.get("d"))
            n, ever = _pollution(t, _rs(box["rc"]), False)
            if _live(t):
                box["d_text"] = s
                if "leaking" in s.lower():
                    _fail("a breached cask reads LEAKING with caskLeaksEnabled=false: %s" % s[:200])
                if n:
                    _fail("%d cells polluted by a breached cask with caskLeaksEnabled=false" % n)

        with _comp(t, "breached_cask_text_does_not_claim_a_bay_that_is_not_there", independent=True):
            # RM_CompWasteCask.CompInspectStringExtra says 'Breached, but held by a sealed cask bay.' whenever
            # Breached && !Leaking, which includes leaks switched OFF with no bay anywhere (read off the source,
            # 2026-10-01). Red until the text tests Bay != null.
            if _live(t):
                s = box.get("d_text")
                if not s:
                    _unmeasured(t, "cask D's pane was never read (leaks_off_makes_a_breached_cask_inert did not get that far)")
                if "held by a sealed cask bay" in s.lower():
                    _fail("a breached cask with NO bay reads 'held by a sealed cask bay': %s" % s[:200])
    finally:
        _restore(t, ["caskLeaksEnabled"])
        _teardown(t)


@suite.chain("cask_bay")
def cask_bay(t):
    """The sealed cask bay (RM_CompWasteContainment): its readout shows capacity, seal integrity, heat, stored
    dose and launch safety; it holds a breached cask without leaking while its seals hold; with the bay itself
    shot up it leaks visibly; unpowered it says so, and power clears that."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_bay"):
            _cask_pad(t, box)
            x, z = box["x"], box["z"]
            _pollution(t, _rs((x - 8, z - 8, 17, 17)), False)
            _spawn_thing(t, "RM_WasteCaskBay", x, z, 1)
            _spawn_thing(t, "RM_WasteCask", x, z, 1)
            if _live(t):
                box["bay"] = _first_id(_things(t, "RM_WasteCaskBay", _pad_rect(t)), "sealed cask bay")
                box["cask"] = _first_id(_things(t, "RM_WasteCask", _pad_rect(t)), "waste cask on the bay")

        with _comp(t, "bay_readout_shows_capacity_integrity_and_launch_safety", independent=True):
            s = _inspect(t, box.get("bay")).lower()
            if _live(t):
                want = BAY_SIZE[0] * BAY_SIZE[1] * DEFAULTS["caskBayPerCell"]
                for needle in ("casks: 1 / %d" % want, "seal integrity: 100%", "internal heat", "stored dose",
                               "launch safety: not aboard a gravship"):
                    if needle not in s:
                        _fail("the bay's readout lacks %r (capacity is size %s x caskBayPerCell %s = %d): %s" % (
                            needle, BAY_SIZE, DEFAULTS["caskBayPerCell"], want, s[:300]))

        with _comp(t, "bay_holds_a_breached_cask_without_leaking", independent=True):
            t.bridge_call("jawa/set_thing_props", thing=box.get("cask"), hitPoints=30)
            t.wait_ticks(700)
            s = _inspect(t, box.get("cask"))
            n, ever = _pollution(t, _rs((box["x"] - 8, box["z"] - 8, 17, 17)), False)
            if _live(t):
                if "held by a sealed cask bay" not in s.lower():
                    _fail("a breached cask in an intact bay does not read held: %s" % s[:200])
                if n:
                    _fail("%d cells polluted around an intact bay holding a breached cask" % n)

        with _comp(t, "shot_up_bay_leaks_loudly", independent=True, toggle="caskLeaksEnabled"):
            t.bridge_call("jawa/set_thing_props", thing=box.get("bay"), hitPoints=80)    # 80 of 350
            t.wait_ticks(700)
            s = _inspect(t, box.get("bay"))
            n, ever = _pollution(t, _rs((box["x"] - 8, box["z"] - 8, 17, 17)), False)
            al = t.bridge_call("jawa/alerts_list")
            if _live(t):
                if "leaking" not in s.lower():
                    _fail("a bay at 23%% hit points does not read LEAKING: %s" % s[:300])
                if ever == 0:
                    _unmeasured(t, "no cell around the bay is pollutable")
                if n <= 0:
                    _fail("a leaking bay polluted no cell in 700 ticks (leakPollutionCells 6)")
                if not _has(al, "waste leaking"):
                    _fail("the 'Waste leaking' alert is not active: %s" % str(al)[:200])

        with _comp(t, "unpowered_bay_says_so_and_power_clears_it", independent=True):
            s0 = _inspect(t, box.get("bay")).lower()
            if _live(t) and "no power" not in s0:
                _fail("an unconnected bay does not say NO POWER: %s" % s0[:300])
            r = t.bridge_call("jawa/power_net", thing=box.get("bay"), forcePowerOn=True)
            if _live(t) and (r or {}).get("success") is False:
                _unmeasured(t, "power_net could not force the bay on: %r" % r)
            t.wait_ticks(300)
            s1 = _inspect(t, box.get("bay")).lower()
            if _live(t) and "no power" in s1:
                _fail("the bay still says NO POWER after power_net forcePowerOn: %s" % s1[:300])

    finally:
        _teardown(t)


@suite.chain("launch_check_patch")
def launch_check_patch(t):
    """The sealed bay's gravship launch refusal is a Harmony postfix on Building_GravEngine.CanLaunch (the
    method has no extension point). The refusal itself needs a gravship; the patch being installed is what a
    bridge read can prove (jawa/harmony_patches)."""
    with _comp(t, "can_launch_postfix_is_installed", independent=True, toggle="caskLaunchCheckEnabled"):
        r = t.bridge_call("jawa/harmony_patches", typeName="RimWorld.Building_GravEngine", methodName="CanLaunch")
        if _live(t):
            _ok(r, "harmony_patches")
            if not _has(r, "CanLaunch"):
                _unmeasured(t, "harmony_patches returned nothing readable for Building_GravEngine.CanLaunch: %s" % str(r)[:200])
            if not (_has(r, "mandrake.rm.wasteland") or _has(r, "RM_WasteCaskBayUtility")):
                _fail("no Wasteland postfix on Building_GravEngine.CanLaunch: a waste cask bay can launch unsafe: %s" % str(r)[:300])


# ----------------------------------------------------------------------------- the Middenshell

TRAIL = "RM_Filth_MiddenshellFootprint,RM_Filth_MiddenshellFlakes"


def _wipe_map(t):
    """The site is a scratch map we own: everything but pawns off it, so a 20-wide body has room and the
    carcass of one test cannot block the next."""
    whole = _map_rect(t)
    t.bridge_call("jawa/destroy_batch", rects=whole, categories="All")
    return whole


def _steps(s):
    m = re.search(r"steps taken:\s*(\d+)", s.lower())
    return int(m.group(1)) if m else None


def _eaten(s):
    m = re.search(r"things eaten:\s*(\d+)", s.lower())
    return int(m.group(1)) if m else None


def _footprint(t, pane):
    """(minx, minz, maxx, maxz) read off the body's inspect pane, 'Footprint: 20x20 cells (a,b to c,d)'."""
    m = re.search(r"footprint:\s*\d+x\d+ cells \((\d+),(\d+) to (\d+),(\d+)\)", pane.lower())
    if not m:
        _unmeasured(t, "the Middenshell's inspect pane has no parseable 'Footprint' line: %s" % pane[:200])
    return tuple(int(v) for v in m.groups())


def _shell_row(t, whole):
    rows = _things(t, "RM_Middenshell", whole, limit=10)
    return rows[0] if rows else None


@suite.chain("middenshell_body")
def middenshell_body(t):
    """The Middenshell (Building_Middenshell): a 20x20 body that crawls, flattens buildings and swallows items in
    its path, leaves a trail, doses people beside it, stands still when switched off, and on death hardens
    into a quarry of seams. A scratch map; the body is spawned directly (the incident chain tests arrival).
    It is spawned with middenshellEnabled=false so it cannot move before the fixture is laid, and the ring of
    bait around it covers all four headings (it turns at random, 4%% per step)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_middenshell"):
            _need_wasteland(t)
            box["whole"] = _wipe_map(t)
            mi = _map_info(t)
            _set(t, middenshellStepTicks=60, middenshellEnabled=False)
            cx = (mi.get("sizeX") or 150) // 2 - 40
            cz = (mi.get("sizeZ") or 150) // 2 - 40
            box["c"] = (cx, cz)
            _spawn_thing(t, "RM_Middenshell", cx, cz, 1)
            if _live(t):
                row = _shell_row(t, box["whole"])
                if row is None:
                    _fail("rimworld/spawn_thing placed no RM_Middenshell at (%d,%d)" % (cx, cz))
                box["id"] = row["id"]
            box["s0"] = _inspect(t, box.get("id"))

        with _comp(t, "middenshell_is_twenty_cells_wide", independent=True):
            if _live(t):
                box["fp"] = _footprint(t, box["s0"])
                if (box["fp"][2] - box["fp"][0] + 1, box["fp"][3] - box["fp"][1] + 1) != (SHELL, SHELL):
                    _fail("the Middenshell's footprint is %r; the owner ruled %dx%d (a report, never a shrink)" % (
                        box["fp"], SHELL, SHELL))

        with _comp(t, "wake_flattens_buildings_and_swallows_items", independent=True):
            if _live(t):
                if "fp" not in box:
                    _unmeasured(t, "no footprint, so the cells around the body are unknown")
                minx, minz, maxx, maxz = box["fp"]
                mx, mz = (minx + maxx) // 2, (minz + maxz) // 2
                bait = ((mx, maxz + 1, mx + 3, maxz + 1), (mx, minz - 1, mx + 3, minz - 1),
                        (maxx + 1, mz, maxx + 1, mz + 3), (minx - 1, mz, minx - 1, mz + 3))
                for sx, sz, wx, wz in bait:
                    _spawn_thing(t, "Steel", sx, sz, 20)
                    t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (wx, wz), stuff="Steel")
                box["ring"] = "%d,%d,%d,%d" % (minx - 2, minz - 2, SHELL + 4, SHELL + 4)
                box["bait"] = len(_things(t, "Steel,Wall", box["ring"]))
                if box["bait"] < 8:
                    _fail("precondition: only %d of 8 bait things stand around the body" % box["bait"])
            _restore(t, ["middenshellEnabled"])
            t.wait_ticks(200)
            if _live(t):
                s = _inspect(t, box["id"])
                left = _things(t, "Steel,Wall", box["ring"])
                _note(t, "after 200 ticks", {"inspect": s[-120:], "bait before": box["bait"], "bait left": len(left)})
                if _steps(s) is None or _steps(s) < 3:
                    _fail("the body took %r steps in 200 ticks at 60 ticks per step: it is not crawling" % _steps(s))
                if len(left) >= box["bait"]:
                    _fail("the body crawled %d steps but none of the %d Steel and Wall baits around it was crushed or "
                          "swallowed (CrushCells)" % (_steps(s), box["bait"]))
                if not (_eaten(s) or 0) >= 1:
                    _fail("'Things eaten' is %r after a Steel stack was swallowed" % _eaten(s))

        with _comp(t, "crawl_leaves_trail_filth", independent=True, toggle="middenshellTrailEnabled"):
            t.wait_ticks(400)
            if _live(t):
                n = len(_things(t, TRAIL, box["whole"]))
                box["trail1"] = n
                if n <= 0:
                    _fail("no footprint or flake filth after ~10 steps (12%% / 8%% per trailing cell per step)")

        with _comp(t, "trail_off_leaves_no_new_filth", independent=True, toggle="middenshellTrailEnabled"):
            _set(t, middenshellTrailEnabled=False)
            t.wait_ticks(400)
            if _live(t):
                n = len(_things(t, TRAIL, box["whole"]))
                if n > box.get("trail1", n):
                    _fail("trail filth rose %d -> %d with middenshellTrailEnabled=false" % (box.get("trail1"), n))
            _restore(t, ["middenshellTrailEnabled"])

        with _comp(t, "off_stands_still_and_on_resumes", independent=True, toggle="middenshellEnabled"):
            s0 = _steps(_inspect(t, box.get("id")))
            _set(t, middenshellEnabled=False)
            t.wait_ticks(400)
            s1 = _steps(_inspect(t, box.get("id")))
            if _live(t):
                if None in (s0, s1):
                    _unmeasured(t, "no 'Steps taken' on the pane: %r" % [s0, s1])
                if s1 != s0:
                    _fail("the body took %d steps with middenshellEnabled=false" % (s1 - s0))

        with _comp(t, "ambient_aura_doses_a_pawn_beside_it", independent=True, toggle="ambientDoseEnabled"):
            # the body is still (middenshellEnabled=false from the previous component), so the footprint is current
            fp = _footprint(t, _inspect(t, box.get("id"))) if _live(t) else (0, 0, 0, 0)
            who = _spawn(t, "Colonist", fp[0] - 3, (fp[1] + fp[3]) // 2, "player")
            if _live(t):
                _settle(t, who)
            _wait_dose(t, 500)
            if _live(t):
                sev = _hed(t, who, "ToxicBuildup")
                if not sev > 0:
                    _fail("a colonist 3 cells from the body took no ToxicBuildup in 500 ticks (aura radius 8, "
                          "toxicFactor 1.2)")

        with _comp(t, "on_again_resumes_the_crawl", independent=True, toggle="middenshellEnabled"):
            s1 = _steps(_inspect(t, box.get("id")))
            _restore(t, ["middenshellEnabled"])
            t.wait_ticks(400)
            s2 = _steps(_inspect(t, box.get("id")))
            if _live(t):
                if None in (s1, s2):
                    _unmeasured(t, "no 'Steps taken' on the pane: %r" % [s1, s2])
                if not s2 > s1:
                    _fail("the body did not resume after the toggle came back on (%d -> %d): the OFF arm proved "
                          "nothing" % (s1, s2))

        with _comp(t, "killed_body_hardens_into_a_quarry", independent=True):
            row = _shell_row(t, box["whole"]) if _live(t) else None
            r = t.bridge_call("jawa/damage", thingId=(row or {}).get("id"), damageDef="Blunt", amount=40000)
            t.wait_ticks(120)
            if _live(t):
                _ok(r, "damage(middenshell)")
                seams = _things(t, "RM_MiddenshellSeam,RM_MiddenshellVitrifiedSeam", box["whole"], limit=500)
                _note(t, "carcass seams", len(seams))
                if _shell_row(t, box["whole"]) is not None:
                    _fail("the body survived 40000 damage (30000 hit points)")
                if len(seams) < 50:
                    _fail("a 20x20 body died and left %d seams (an ellipse of ~190 cells expected)" % len(seams))
    finally:
        _restore(t, ["middenshellStepTicks", "middenshellEnabled", "middenshellTrailEnabled"])
        if t.session is not None:
            try:
                t.session.call("jawa/destroy_batch", rects=_map_rect_safe(t), categories="All")
            except Exception as ex:
                print("[wl] map wipe failed: %s" % ex, file=sys.stderr, flush=True)
        _teardown(t)


def _map_rect_safe(t):
    mi = t.session.call("jawa/map_info") or {}
    return "0,0,%d,%d" % (mi.get("sizeX") or 0, mi.get("sizeZ") or 0)


@suite.chain("middenshell_procession")
def middenshell_procession(t):
    """The incident and the Procession (RM_IncidentWorker_MiddenshellArrives, RM_MapComponent_MiddenshellProcession):
    it can fire only on a Wasteland map with the toggle on, announces itself with a letter and creeping loose
    metal, arrives hours later already crossing toward an edge, and with the procession switched off arrives
    at once without a route. Omen shortened to 1 hour by middenshellOmenHours, restored in finally."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_procession"):
            _need_wasteland(t)
            box["whole"] = _wipe_map(t)
            mi = _map_info(t)
            _set(t, middenshellOmenHours=1, middenshellStepTicks=60)
            cx, cz = (mi.get("sizeX") or 150) // 2 + 20, (mi.get("sizeZ") or 150) // 2 + 20
            box["steel"] = (cx, cz)
            _spawn_thing(t, "Steel", cx, cz, 30)
            if _live(t):
                rows = _things(t, "Steel", "%d,%d,1,1" % (cx, cz))
                box["steel_id"] = _first_id(rows, "the loose Steel stack")

        with _comp(t, "incident_can_fire_on_a_wasteland_map", independent=True):
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives", dryRun=True)
            if _live(t):
                if not (r or {}).get("success"):
                    _fail("RM_MiddenshellArrives cannot fire on a Wasteland map with everything at defaults: %s" % str(r)[:300])

        with _comp(t, "incident_is_blocked_when_the_body_is_switched_off", independent=True, toggle="middenshellEnabled"):
            _set(t, middenshellEnabled=False)
            # IncidentWorker.CanFireNow memoises its CanFireNowSub answer per game tick
            # (lastCheckCanRunTick), and the ON arm above asked at this same paused tick, so
            # without a tick the OFF ask is served the cached True (2026-10-08 acc_biomes FAIL).
            t.wait_ticks(2)
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives", dryRun=True)
            _restore(t, ["middenshellEnabled"])
            if _live(t) and (r or {}).get("success"):
                _fail("the incident can still fire with middenshellEnabled=false: %s" % str(r)[:300])

        with _comp(t, "omen_letter_and_creeping_metal", independent=True, toggle="middenshellProcessionEnabled"):
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives")
            if _live(t):
                _ok(r, "fire_incident")
                if r.get("blockedByDialog"):
                    _unmeasured(t, "a modal swallowed the incident: %s" % str(r)[:200])
                if _shell_row(t, box["whole"]) is not None:
                    _fail("the body was on the map at once although the procession is on (omen first, arrival hours later)")
            t.wait_ticks(500)
            letters = t.bridge_call("jawa/letter_list")
            if _live(t):
                if not _has(letters, "middenshell procession"):
                    _fail("no 'Middenshell procession' omen letter: %s" % str(letters)[:300])
                _note(t, "omen letter names the edge", _has(letters, "creeping toward"))
                rows = _things(t, "Steel", "%d,%d,13,13" % (box["steel"][0] - 6, box["steel"][1] - 6))
                mine = [r2 for r2 in rows if r2.get("id") == box.get("steel_id")]
                if not mine:
                    _fail("the loose Steel stack is no longer within 6 cells of where it lay (swallowed or lost)")
                if (mine[0].get("x"), mine[0].get("z")) == box["steel"]:
                    _fail("loose metal did not creep one cell toward the arrival edge after 500 ticks of omen")

        with _comp(t, "body_arrives_already_crossing", independent=True, toggle="middenshellProcessionEnabled"):
            t.wait_ticks(2200)                    # omen 1 hour = 2500 ticks from the fire; 500 already waited
            if _live(t):
                row = _shell_row(t, box["whole"])
                if row is None:
                    _fail("no Middenshell on the map 2700 ticks after the omen began (omen is 2500 ticks)")
                s = _inspect(t, row["id"])
                if "procession: crossing toward the" not in s.lower():
                    _fail("the arrived body is not in a procession: %s" % s[-200:])
                box["shell"] = row["id"]

        with _comp(t, "procession_trail_is_laid_and_trail_off_stops_it", independent=True, toggle="middenshellTrailEnabled"):
            t.wait_ticks(500)
            n1 = len(_things(t, TRAIL, box["whole"])) if _live(t) else 0
            _set(t, middenshellTrailEnabled=False)
            t.wait_ticks(400)
            n2 = len(_things(t, TRAIL, box["whole"])) if _live(t) else 0
            _restore(t, ["middenshellTrailEnabled"])
            if _live(t):
                if n1 <= 0:
                    _fail("the crossing body left no footprint or flake filth in 500 ticks")
                if n2 > n1:
                    _fail("trail filth rose %d -> %d with middenshellTrailEnabled=false" % (n1, n2))

        with _comp(t, "procession_off_arrives_at_once_without_a_route", independent=True, toggle="middenshellProcessionEnabled"):
            t.bridge_call("jawa/destroy_batch", rects=box["whole"], categories="All")
            _set(t, middenshellProcessionEnabled=False)
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives")
            if _live(t):
                _ok(r, "fire_incident(procession off)")
                row = _shell_row(t, box["whole"])
                if row is None:
                    _fail("with the procession off the body should arrive at once, but the map has none")
                s = _inspect(t, row["id"])
                if "procession:" in s.lower():
                    _fail("the body is in a procession with middenshellProcessionEnabled=false: %s" % s[-200:])
    finally:
        _restore(t, ["middenshellOmenHours", "middenshellStepTicks", "middenshellProcessionEnabled",
                     "middenshellTrailEnabled", "middenshellEnabled"])
        if t.session is not None:
            try:
                t.session.call("jawa/destroy_batch", rects=_map_rect_safe(t), categories="All")
            except Exception as ex:
                print("[wl] map wipe failed: %s" % ex, file=sys.stderr, flush=True)
        _teardown(t)


# ------------------------------------------------------------------------------ the Rite of Tipping

@suite.chain("rite_of_tipping")
def rite_of_tipping(t):
    """The Rite of Tipping: the tipping pad reads unlicensed until a contract exists, firing the quest on a
    Wasteland map makes an Ongoing contract and the pad reads licensed, and tippingEnabled=false refuses the
    offer. Deliveries come every four game days (UNCOVERED, see the walk)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_tipping"):
            _need_wasteland(t)
            _reset_pad(t)
            x, z = t.anchor
            _spawn_thing(t, "RM_WasteTippingPad", x, z, 1)
            if _live(t):
                box["pad"] = _first_id(_things(t, "RM_WasteTippingPad", _pad_rect(t)), "tipping pad")

        with _comp(t, "pad_reads_unlicensed_without_a_contract", independent=True):
            s = _inspect(t, box.get("pad"))
            if _live(t) and "unlicensed" not in s.lower():
                _fail("the pad does not read unlicensed before any contract: %s" % s[:200])

        with _comp(t, "quest_fires_and_is_ongoing", independent=True, toggle="tippingEnabled"):
            r = t.bridge_call("jawa/fire_quest", questDef="RM_Quest_RiteOfTipping", accept=True)
            if _live(t):
                if not (r or {}).get("success"):
                    _unmeasured(t, "fire_quest could not make the contract (QuestNode_RM_TippingContract.TestRunInt needs a "
                                   "non-hostile humanlike faction on this world): %s" % str(r)[:300])
                box["fired"] = True
            ql = t.bridge_call("jawa/quest_lifecycle", action="list")
            if _live(t):
                rows = (_ok(ql, "quest_lifecycle(list)").get("quests") or [])
                mine = [q for q in rows if "tipping" in json.dumps(q).lower()]
                if not mine or not any(q.get("state") == "Ongoing" for q in mine):
                    _fail("no Ongoing Rite of Tipping quest after accepting it: %s" % str(rows)[:300])

        with _comp(t, "pad_reads_licensed_with_a_contract", independent=True):
            if _live(t) and not box.get("fired"):
                _unmeasured(t, "no contract was created, so a licensed pad cannot be read")
            s = _inspect(t, box.get("pad"))
            if _live(t):
                want = "0 of %d" % DELIVERIES
                if "licensed tipping pad (" not in s.lower() or want not in s.lower():
                    _fail("the pad does not read licensed with %r deliveries after the contract started: %s" % (want, s[:200]))

        with _comp(t, "tipping_off_refuses_the_offer", independent=True, toggle="tippingEnabled"):
            if _live(t) and not box.get("fired"):
                _unmeasured(t, "the ON arm never produced a contract, so a refusal proves nothing")
            # jawa/fire_quest -> QuestUtility.GenerateQuestAndMakeAvailable -> QuestGen.Generate runs
            # RunInt and never TestRun, so it makes the contract whatever the toggle says. The
            # player's only route is the RM_RiteOfTipping incident (IncidentWorker_GiveQuest), whose
            # CanFireNowSub asks QuestScriptDef.CanRun -> root.TestRun -> our TestRunInt. Ask THAT,
            # with an ON control first (earliestDay 8 / minRefireDays can refuse it on their own).
            # Both CanFireNow and CanRun memoise per tick, so a tick separates the two asks.
            t.wait_ticks(2)
            # forced=True: skip earliestDay 8 / minRefireDays 30 (a fresh test map is day ~1, LIVE 2026-10-08 the ON
            # control read canFireNow=False for that alone) and ask only CanFireNowSub -> CanRun -> TestRunInt.
            # Needs the JawaBench build carrying fire_incident's `forced` parameter.
            on = t.bridge_call("jawa/fire_incident", incidentDef="RM_RiteOfTipping", dryRun=True, forced=True)
            if _live(t) and not (on or {}).get("canFireNow"):
                _unmeasured(t, "RM_RiteOfTipping cannot fire even forced with tippingEnabled=true, so an OFF refusal "
                               "proves nothing (if the reply has no 'forced' key the deployed JawaBench predates the "
                               "parameter: build.py --gm --apply at a shutdown): %s" % str(on)[:300])
            _set(t, tippingEnabled=False)
            t.wait_ticks(2)
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_RiteOfTipping", dryRun=True, forced=True)
            if _live(t) and (r or {}).get("canFireNow"):
                _fail("RM_RiteOfTipping can still offer the contract with tippingEnabled=false (TestRunInt must refuse): %s"
                      % str(r)[:300])
    finally:
        _restore(t, ["tippingEnabled"])
        _teardown(t)


def static_checks():
    """Offline structural checks (no game): the parse floors, sanity probes, the csproj, the walk."""
    bad = list(_ERRORS)
    for ty, n in FLOORS.items():
        if len(_BY_TYPE.get(ty, [])) < n:
            bad.append("only %d %s parsed, floor %d (blind parse)" % (len(_BY_TYPE.get(ty, [])), ty, n))
    if len(DEFAULTS) < 30:
        bad.append("settings regex found %d fields, floor 30" % len(DEFAULTS))
    proj = open(os.path.join(HERE, "Source", "RM_Wasteland.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    if _BIOME_EL is None or not BIOME_ANIMALS:
        bad.append("biome roster not parsed")
    if not BIOME_SCALARS.get("animalDensity", 0) > 0:
        bad.append("animalDensity is 0: the roster would be dead content")
    walk = os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "Wasteland.md")
    if not os.path.isfile(walk):
        bad.append("walk missing")
    return bad


if __name__ == "__main__":
    _problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not _problems else "FAIL"))
    for _p in _problems:
        print("  - " + _p)
    sys.exit(1 if _problems else 0)
