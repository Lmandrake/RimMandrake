"""validation.py -- modcheck suite for RimMandrake: The Cauldron (mandrake.rm.cauldron).

Item CAULDRON_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/Cauldron.md
(`## must be true` lines, each ending in `-> chain.component` or `-> UNCOVERED: why`).
Process: design/RimMandrake/debug_process.md (a first script = a modcheck Suite + a walk).

PACKAGING. This dev folder is the SOURCE only. The biome ships COMPOSED inside
`mandrake.rm.biomes` (Biomes.compose.json, wave 0 <= compose_wave 2). Drive the `baroque_wave0`
tier (northstar_plan.py), never the dev folder's own packageId: `modcheck run Cauldron` would swap
to a list without the composed biome.

WHAT THE SUITE READS. Every defName this mod ships is parsed from its own Defs/ at import (so a new
def is covered without an edit) and must RESOLVE live: a def whose comp/extension type is missing is
discarded silently by the engine, and only a live get_defs sees that. The mod's Mod Settings
defaults are parsed from RM_CauldronMod.cs at import (single source, never copied). Mechanics are
read as STATE through the bridge (hediffs + severities, terrain cells, letters, jobs, item stacks,
inspect strings); nothing here judges appearance and no component takes a screenshot.

EVERY CHECK CAN FAIL. Each PASS predicate has an arm that goes the other way inside the same chain
(a roofed pawn and a native animal that must stay clean beside an exposed colonist, a toggle-off
arm, a letter cooldown arm that only counts if the poisoning DID repeat, a melee control beside the
shot Suush), so a harness that sees nothing records UNMEASURED, never PASS.
`selftest_cauldron.py` runs the suite against a scripted fake game, healthy and with each mod
behaviour broken in turn, and proves the right component (and only that one) goes red.

NOT DRIVEN HERE (walk lines say UNCOVERED, with the reason):
  * The biome worker's placement score and rarity 0 -> never generates: BiomeWorker.GetScore needs
    a Tile + PlanetTile and no bridge tool calls it (CAULDRON_WORKER_PROBE_1). Only the worker
    class name and settings read/write are checked.
  * Condensate gardens (nettles colonising toxic shores): the spread is 40 random cells per 2500
    ticks over the whole map and only runs on a map whose biome roster names the nettle, so days of
    ticks and a Cauldron-biome map (CAULDRON_CONDENSATE_SWEEP_HOOK_1). Only the wiring is checked.
  * The vexxiss attacking whoever lit a fire: no bridge tool sets Fire.instigator
    (CAULDRON_FIRE_INSTIGATOR_TOOL_1).
  * Wild-vexxiss shearing (60 in-game days, tame-only), toxic-gear resistance to the vent bloom, a
    butchered zisska's real yield (needs a built bench + bill): only the defs are read.
  * Vent flowers (crystal / blood / giant toxic rings, CAULDRON_VENT_ENRICHMENT_HOOKS_1): the spread only runs on
    a map whose biome roster names the plants, and takes days of ticks. Only the wiring is read
    (load.vent_habitat_wired). `ventsEnabled` (worldgen), `ventFalterMessage` (a Messages.Message the bridge
    cannot list) and `ventGardensEnabled` are write/read-back roundtrips only.
  * CAULDRON_ENRICHMENT_VISUALS_1 (dewfall beads, dewfall saturation, assay flecks, vexxiss prints): toggles are
    roundtrips only. Beads need a locked dewfall over unroofed non-home ground for hours (a chain is owed);
    saturation and flecks stay dormant until their art is on disk; prints sit on CreatureBehaviors' track grid,
    which no bridge tool reads (its own validation.py track_grid chain reads only the grid's counters).
  * Vents are spawned by the driver here (jawa/spawn_batch). That mapgen places 4-5 on a new Cauldron map, with
    both temperaments and a recent blowout, is NOT read: it needs a freshly generated Cauldron map.
  * Appearance (dusk light, the vent-bloom overlay, art): visual, left to the judge pass.

Settings fields are `public static` (RimMandrake.Cauldron.RM_CauldronSettings). Every arm that
changes one restores it in a `finally`. `jawa/mod_settings_field` never writes ModSettings.xml.
"""
import contextlib
import glob
import json
import os
import re
import sys
import time

from modcheck import Suite, ExpectationFailed

# The situational runner picks the anchor FARTHEST from colonists (0.2..0.8 of the map), which on a 250 map can be
# (50, 50); the pads below reach 85 cells from it, so spawns landed "Cell is outside the map" (LIVE 2026-10-03). The
# margin makes the runner choose an anchor with that much room on every side.
suite = Suite("Cauldron")
suite.anchor_margin = 100

SETTINGS = "RimMandrake.Cauldron.RM_CauldronSettings"
HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "[cauldron]"


# --------------------------------------------------------------------------- settings (single-sourced)

def _read_defaults():
    """The shipped defaults, parsed from the `public static bool|float x = v;` initialisers in
    RM_CauldronMod.cs (never a second copy that can drift)."""
    out = {}
    with open(os.path.join(HERE, "Source", "RM_CauldronMod.cs"), encoding="utf-8") as fh:
        txt = fh.read()
    for m in re.finditer(r"public\s+static\s+(bool|float)\s+(\w+)\s*=\s*([^;]+);", txt):
        kind, name, val = m.group(1), m.group(2), m.group(3).strip()
        out[name] = (val == "true") if kind == "bool" else float(val.rstrip("fF"))
    return out


DEFAULTS = _read_defaults()
if len(DEFAULTS) < 11:        # a parser that reads nothing must not turn into "all 0 settings ok"
    raise ImportError("parsed only %d Mod Settings fields from RM_CauldronMod.cs" % len(DEFAULTS))
suite.toggles = sorted(k for k, v in DEFAULTS.items() if isinstance(v, bool))

# Classes the mod ships in RimMandrake.Cauldron.dll that the engine must resolve (selftest checks each
# exists in Source/).
NS = "RimMandrake.Cauldron."
TYPES = tuple(NS + n for n in (
    "RM_CauldronSettings", "RM_BiomeWorker_Cauldron", "RM_MapComponent_VentBloomExposure",
    "RM_MapComponent_CondensateGardens", "RM_CompVexxissBehaviour", "RM_CompMetalYield",
    "RM_Building_CauldronVent", "RM_MapComponent_CauldronVents", "RM_JobDriver_VexxissDrinkVent",
    "RM_VentExtension", "RM_AcidDamageExtension", "RM_AcidImmuneExtension",
    # CAULDRON_ENRICHMENT_VISUALS_1
    "RM_MapComponent_CauldronDewfall", "RM_MapComponent_VexxissPrints", "RM_DewfallGraphicExtension",
    "RM_AssayFlecksExtension"))

BIOME = "RM_Cauldron"
WEATHERS = ("RM_ScatterDusk", "RM_VentBloom", "RM_VapourBank", "RM_Dewfall")
BLOOM, HEDIFF = "RM_VentBloom", "RM_VentMetalLoad"
VEXXISS, SUUSH, ZISSKA, ESKITH = "RM_Vexxiss", "RM_Suush", "RM_Zisska", "RM_Eskith"
NATIVES = (SUUSH, VEXXISS, ZISSKA, ESKITH)             # the biome's own, MayRequire-free wildAnimals rows
THORN, MARTYR, NETTLE = "RM_TwistingThornwood", "RM_TreeMartyr", "RM_RavenNettle"
LETTER_LABEL = "Vexxiss poisoning water"
MARTYR_FULL = 6.0                                       # countAtFullGrowth in RM_CauldronFlora.xml
THORN_MIN, THORN_FULL = 2.0, 12.0
BLOOM_INTERVAL = 3451                                   # RM_MapComponent_VentBloomExposure.IntervalTicks
HERBIVORES = ("Deer", "Muffalo", "Elk", "Alpaca", "Hare", "Chicken", "Squirrel", "Ibex", "Caribou",
              "Dromedary", "Elephant", "Megasloth", "Gazelle", "Cow", "Horse", "Donkey",
              "Goat", "Sheep", "Yak", "Camel")

# Pad offsets from the map centre (the driver's anchor); each chain clears its own pad first.
VENT, DRINK_JOB = "RM_CauldronVent", "RM_VexxissDrinkVent"
VEXXITH, VDOOR, ACID = "RM_Vexxith", "RM_VexxithDoor", "AcidBurn"     # VEXXITH_CLOSED_LOOP_BUILD_1
VENT_PLANTS = {"RM_CrystalFlower": "StableRing", "RM_BloodBouquet": "ChronicLeak",
               "RM_GiantToxicFlower": "RecentBlowout"}
PADS = {"vent": (0, -85), "fauna": (-45, -45), "suush": (45, -45), "flora": (-45, 0), "yield": (45, 0),
        "bloom": (-45, 45), "water": (0, 45), "fire": (45, 45), "spawn": (0, -45)}
PAD_SIZE = 24
SOIL = "Soil"

_STATE = {}    # readings shared between components of ONE run


# --------------------------------------------------------------------------- shipped defs

_OVERRIDE = {}      # selftest hook: relative Defs path -> replacement text (never set in a live run)


def _def_text(rel):
    if rel in _OVERRIDE:
        return _OVERRIDE[rel]
    with open(os.path.join(HERE, "Defs", rel), encoding="utf-8") as fh:
        return fh.read()


def _patch_text(rel):
    key = "Patches/" + rel
    if key in _OVERRIDE:
        return _OVERRIDE[key]
    with open(os.path.join(HERE, "Patches", rel), encoding="utf-8") as fh:
        return fh.read()


def _read_defs():
    """({defType: [defName]}, {defName: source folder}) for every concrete def in this mod's Defs/,
    parsed per top-level element (never a fixed line number). Comments are stripped first."""
    wanted = ("ThingDef", "PawnKindDef", "WeatherDef", "HediffDef", "TerrainDef", "BiomeDef", "JobDef", "RecipeDef", "DamageDef")
    by_type, where = {}, {}
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        folder = os.path.basename(os.path.dirname(path))
        for m in re.finditer(r"<(%s)\b([^>]*)>(.*?)</\1>" % "|".join(wanted), txt, re.S):
            kind, attrs, body = m.group(1), m.group(2), m.group(3)
            if re.search(r'Abstract\s*=\s*"[Tt]rue"', attrs):
                continue
            nm = re.search(r"<defName>([^<]+)</defName>", body)
            if not nm:
                continue
            by_type.setdefault(kind, []).append(nm.group(1).strip())
            if kind == "ThingDef":
                where[nm.group(1).strip()] = folder
    return by_type, where


DEFS_BY_TYPE, _FOLDER = _read_defs()
SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_BY_TYPE.items() for n in ns)
FLORA = sorted(n for n, f in _FOLDER.items() if f == "ThingDefs_Plants")
KINDS = DEFS_BY_TYPE.get("PawnKindDef", [])


def _soil_blacklisted():
    """Plants whose own <terrainBlacklist> names Soil/SoilRich (bare-rock plants such as RM_Sessarix). The flora pad is
    laid in Soil, so set_plants put them on forbidden ground and they never stood (LIVE 2026-10-03)."""
    import glob
    import xml.etree.ElementTree as ET
    out = set()
    for f in glob.glob(os.path.join(HERE, "Defs", "ThingDefs_Plants", "*.xml")):
        for td in ET.parse(f).getroot().iter("ThingDef"):
            bl = [li.text for li in td.findall("./plant/terrainBlacklist/li")]
            if td.findtext("defName") and ("Soil" in bl or "SoilRich" in bl):
                out.add(td.findtext("defName"))
    return out


SOIL_FORBIDDEN = _soil_blacklisted()
ROCK = "Gravel"


# --------------------------------------------------------------------------- helpers

def _roofed(r):
    """True when a jawa/get_roof_batch answer shows a real roof. LIVE 2026-10-03: the tool answers
    {cellsRead, roofs: [distinct roof names, "None" = open sky]} and has NO `roofedCells` key, so every
    `r.get("roofedCells")` test read an open or a sealed room alike as 0 and left the chain UNMEASURED."""
    r = r or {}
    return bool(r.get("roofedCells")) or any(x not in (None, "None") for x in (r.get("roofs") or []))


def _live(t):
    """True only for a real run against a real session and an unfailed chain; False for the
    offline declaration probe, so a component body never trips on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component and record it UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True   # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, poison=False, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail names the
    real reason, and the chain is not poisoned for an independent next component. `poison=True` (a
    site-setup component) keeps the chain failed, so every later component of that chain records
    UNMEASURED instead of running on a half-built site."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
        t.upstream_failed = bool(poison)
    t._why = None
    if t.session is not None:    # progress line: the driver prints only at the very end
        c = t.components[-1]
        print("%s %s %s %s" % (TAG, time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("%s-note %s: %s" % (TAG, label, json.dumps(data, default=str)[:1200]),
              file=sys.stderr, flush=True)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _pad(t, name):
    dx, dz = PADS[name]
    ax, az = t._base if hasattr(t, "_base") else t.anchor
    t._base = (ax, az)
    t.anchor = (ax + dx, az + dz)


def _rect(t, size=PAD_SIZE, dx=0, dz=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half + dz, size, size


def _kill_pawns_in(t, rect):
    """Kill every living pawn in rect. jawa/destroy_batch NEVER removes pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1),
    so each is killed by id with jawa/damage (allowColonists reaches player pawns); returns the count killed."""
    r = t.bridge_call("jawa/list_pawns", limit=500, rect=_rs(rect))
    n = 0
    for p in ((r or {}).get("pawns") or []):
        if p.get("dead") or not p.get("id"):
            continue
        t.bridge_call("jawa/damage", damageDef="Bullet", amount=5000, thingId=p["id"], allowColonists=True)
        n += 1
    return n


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _prep(t, name, size=PAD_SIZE):
    """Clear the pad and lay plain soil so everything stands on walkable, plantable ground."""
    _pad(t, name)
    if _live(t):
        try:    # neutral until a chain locks its own; never let this abort the chain
            t.bridge_call("jawa/weather_set", weather="RM_ScatterDusk", lockWeather=True)
        except Exception as ex:
            print("%s neutral weather not set: %s" % (TAG, ex), file=sys.stderr, flush=True)
    t.clear_area(size=size + 8)
    r = _rect(t, size + 8)
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(r)), layer="top")


def _count(t, defName, rect=None):
    """Count of one def over `rect` or the whole map; raises on an unreadable result (never 0)."""
    if rect:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=1, rect=rect)
    else:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=1)
    if not _live(t):
        return 0
    _ok(r, "list_things(%s)" % defName)
    if "countMatched" not in r or not r.get("scanned"):
        _fail("list_things(%s) unreadable (no countMatched / scanned 0): %r" % (defName, r))
    return r["countMatched"]


def _things(t, defName, rect=None, limit=200):
    if rect:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=limit, rect=rect)
    else:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=limit)
    if not _live(t):
        return []
    return list(_ok(r, "list_things(%s)" % defName).get("things") or [])


def _stack_total(t, defName, rect):
    """Total items of a def over `rect` (stack sizes summed): list_things counts THINGS and a stack
    of 12 steel lands as one."""
    return sum(int(w.get("stackCount") or 1) for w in _things(t, defName, rect, limit=500))


def _get_defs(t, defs, fields, deep=False):
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, deep=deep, limit=200)
    if not _live(t):
        return {}
    _ok(r, "get_defs(%s)" % defs[:80])
    if r.get("notFound"):
        _fail("get_defs could not resolve %r" % r.get("notFound"))
    return dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or []))


def _def_field(row, name):
    """A get_defs field, or UNMEASURED-style None when the tool says '(no such field)'."""
    v = (row or {}).get(name)
    if v is None or (isinstance(v, str) and v.startswith("(")):
        return None
    return v


def _spawn(t, kind, x, z, faction="none"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s, %s) returned no pawn: %r" % (kind, faction, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _rows(t, rect=None, health=False):
    if rect and health:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True, rect=rect)
    elif rect:
        r = t.bridge_call("jawa/list_pawns", limit=500, rect=rect)
    elif health:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True)
    else:
        r = t.bridge_call("jawa/list_pawns", limit=500)
    if not _live(t):
        return {}
    return dict((p.get("id"), p) for p in (_ok(r, "list_pawns").get("pawns") or []))


def _hediff(row, hediff):
    """The first hediff of this def on a list_pawns row (health block is NESTED: row['health']
    ['hediffs'], each {def, severity, ...}), or None."""
    for h in ((row or {}).get("health") or {}).get("hediffs") or []:
        if h.get("def") == hediff:
            return h
    return None


def _full(t, pid):
    for need in ("Food", "Rest"):
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)


def _jobs(t):
    r = t.bridge_call("jawa/site_state")
    if not _live(t):
        return {}
    return dict((p.get("id"), p.get("job")) for p in ((r or {}).get("pawns") or []))


def _inspect(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return None, []
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows or rows[0].get("error"):
        _fail("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return rows[0].get("label"), list(rows[0].get("inspect") or [])


def _xz(row):
    if not row or row.get("x") is None or row.get("z") is None:
        return None
    return (row["x"], row["z"])


def _as_bool(v):
    return str(v).strip().lower() == "true"


def _same(got, want):
    """Settings read-back compare: bools by value, numbers numerically (the tool returns text)."""
    if isinstance(want, bool):
        return _as_bool(got) == want
    try:
        return abs(float(str(got).replace(",", ".")) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def _get_setting(t, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
    if not _live(t):
        return None
    _ok(r, "mod_settings_field(get %s)" % field)
    return r.get("value")


def _set(t, field, value):
    """Set a settings field and verify it by an independent read-back (numeric-tolerant)."""
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                      value=str(value))
    if not _live(t):
        return
    _ok(r, "mod_settings_field(set %s=%r)" % (field, value))
    got = _get_setting(t, field)
    if not _same(got, value):
        _fail("setting %s=%r did not take: read back %r" % (field, value, got))


@contextlib.contextmanager
def _setting(t, field, value):
    """Flip one field for a block; ALWAYS restore the shipped default and re-read it."""
    _set(t, field, value)
    try:
        yield
    finally:
        _restore(t, field)


def _restore(t, field):
    if t.session is None:
        return
    try:
        r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                           value=str(DEFAULTS[field]))
        got = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not _same((got or {}).get("value"), DEFAULTS[field]):
            print("%s RESTORE FAILED %s -> %r (set returned %r)" % (TAG, field, got, r),
                  file=sys.stderr, flush=True)
    except Exception as ex:   # restoring must never mask the verdict that got us here
        print("%s RESTORE FAILED %s: %s" % (TAG, field, ex), file=sys.stderr, flush=True)


def _weather_now(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return None
    cur = (r or {}).get("weather")
    if isinstance(cur, dict):
        cur = cur.get("current")
    return cur


def _lock_weather(t, weather):
    t.bridge_call("jawa/weather_set", weather=weather, lockWeather=True)
    if _live(t):
        got = _weather_now(t)
        if got != weather:
            _unmeasured(t, "could not lock weather %s (read back %r): the site cannot hold the "
                           "condition this check needs" % (weather, got))


def _unlock_weather(t):
    """Release the lock AND leave the map on the biome's standing weather: a released lock keeps the
    last weather until the next natural roll, and a lingering vent bloom would taint every later chain."""
    if t.session is not None:
        try:
            t.session.call("jawa/weather_set", weather="RM_ScatterDusk", lockWeather=True)
            t.session.call("jawa/weather_set", unlock=True)
        except Exception as ex:
            print("%s weather reset failed: %s" % (TAG, ex), file=sys.stderr, flush=True)


def _wait(t, n):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact; ~53 ticks/s MEASURED live on a big
    list). Long waits run Ultrafast and poll the real clock, then pause; raises on a stall."""
    # LIVE 2026-10-03: under the situational watch the Ultrafast poll below moves the clock outside the budgeted gate (ClockStall /
    # BudgetExceeded), so a watched run uses the chunked, budgeted t.wait_ticks for every length.
    if t.session is None or t.upstream_failed or n <= 4000 or getattr(t, "watch", None) is not None:
        return t.wait_ticks(n)
    s = t.session
    start = s._ticks()
    target = start + n
    s.call("rimworld/set_time_speed", speed="Ultrafast")
    last, stall = start, time.time()
    try:
        while True:
            time.sleep(1.0)
            now = s._ticks()
            if now is None:
                raise ExpectationFailed("clock unreadable during a %d-tick wait" % n)
            if now >= target - 400:
                break
            if now > last:
                last, stall = now, time.time()
            elif time.time() - stall > 60:
                raise ExpectationFailed("clock stalled at %d during a %d-tick wait (a modal dialog "
                                        "pausing the game?)" % (now, n))
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    now = s._ticks()
    if now < target:
        t.wait_ticks(target - now)
        now = s._ticks()
    t._record("_wait(%d) at Ultrafast -> %d real ticks" % (n, now - start), now - start)


def _stable(t, fn):
    """Run a chain body, then ALWAYS release the weather lock and clear the pad's pawns and things."""
    try:
        fn()
    finally:
        _unlock_weather(t)
        if t.session is not None and getattr(t, "anchor", None):
            try:
                t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 24)),
                               categories="All")
            except Exception as ex:
                print("%s pad cleanup failed: %s" % (TAG, ex), file=sys.stderr, flush=True)


def _terrain(t, rect):
    """{terrainDef: cells} over rect (jawa/get_terrain_batch `ops` 'Def:x,z,w,h;...', MEASURED live by
    Pyrelands), or {} offline. A short read raises, never reads as zero."""
    r = t.bridge_call("jawa/get_terrain_batch", rects=rect)
    if not _live(t):
        return {}
    _ok(r, "get_terrain_batch(%s)" % rect)
    if r.get("cellsRead") != r.get("cellsRequested"):
        _fail("get_terrain_batch(%s) read %r of %r cells" % (rect, r.get("cellsRead"),
                                                            r.get("cellsRequested")))
    out = {}
    for op in (r.get("ops") or "").replace("\n", ";").split(";"):
        if ":" not in op:
            continue
        d, nums = op.split(":", 1)
        p = [int(v) for v in nums.split(",") if v.strip()]
        w = p[2] if len(p) > 2 else 1
        h = p[3] if len(p) > 3 else 1
        out[d.strip()] = out.get(d.strip(), 0) + w * h
    return out


def _toxic_cells(counts):
    return sum(v for k, v in counts.items() if k.startswith("ToxicWater"))


def _next_interval_jump(t, interval=BLOOM_INTERVAL, lead=5):
    """Set the game clock to `lead` ticks before the next multiple of `interval` (the vent bloom's
    exposure tick fires only on those ticks), so one short wait crosses exactly one of them."""
    now = t.session._ticks()
    nxt = (now // interval + 1) * interval
    t.bridge_call("jawa/time_set_ticks", ticks=int(nxt - lead))
    return nxt


def _weather_transition_done(t, tries=4):
    """Let the locked weather finish its transition (the exposure only runs at lerp 1)."""
    t.wait_ticks(4100)
    for _ in range(tries):
        r = t.bridge_call("jawa/site_state")
        tr = (((r or {}).get("weather") or {}).get("transition"))
        if tr is None or float(tr) >= 0.999:
            return tr
        t.wait_ticks(600)
    return None


# --------------------------------------------------------------------------- chain: load

@suite.chain("load")
def load_chain(t):
    _pad(t, "spawn")
    with _comp(t, "defs_resolve"):
        if _live(t):
            # The parser must see the mod: a broken regex would read "all 0 defs resolve".
            if len(SHIPPED) < 28 or not DEFS_BY_TYPE.get("WeatherDef") or not KINDS:
                _fail("parsed only %d shipped defs from %s (parser broken?)" % (len(SHIPPED), HERE))
            r = t.bridge_call("jawa/get_defs", defs=";".join(SHIPPED), fields="defName", limit=200)
            _ok(r, "get_defs(all shipped)")
            if r.get("notFound"):
                _fail("%d shipped def(s) did not resolve live (silently discarded?): %s"
                      % (len(r["notFound"]), r["notFound"][:12]))
            if r.get("foundCount") != len(SHIPPED):
                _fail("get_defs foundCount %r != %d requested" % (r.get("foundCount"), len(SHIPPED)))
            # Sanity probe: the instrument must be able to say "absent".
            probe = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Cauldron_NoSuchDef_Probe",
                                  fields="defName")
            if "RM_Cauldron_NoSuchDef_Probe" not in json.dumps((probe or {}).get("notFound")):
                _fail("sanity probe: an absent def was not reported in notFound: %r" % probe)
            _note(t, "shipped defs resolved", len(SHIPPED))

    with _comp(t, "acid_wiring_shape", toggle="vexxithAcidImmunityEnabled"):
        # VEXXITH_CLOSED_LOOP_BUILD_1: the data the Harmony prefix keys on, parsed from the mod's own XML.
        def _strip(x):
            return re.sub(r"<!--.*?-->", "", x, flags=re.S)
        items = _strip(_def_text("ThingDefs_Items/RM_CauldronItems.xml"))
        door = _strip(_def_text("ThingDefs_Buildings/RM_VexxithDoor.xml"))
        patch = _strip(_patch_text("RM_Cauldron_AcidDamage.xml"))
        vx = re.search(r"<defName>%s</defName>(.*?)</ThingDef>" % VEXXITH, items, flags=re.S)
        bad = []
        if not vx:
            bad.append("control: %s not found in RM_CauldronItems.xml, parser broke" % VEXXITH)
        else:
            b = vx.group(1)
            if NS + "RM_AcidImmuneExtension" not in b:
                bad.append("%s carries no RM_AcidImmuneExtension: nothing made of it is acid-proof" % VEXXITH)
            if "<li>RM_VexxithPlate</li>" not in b or "<li>Metallic</li>" not in b:
                bad.append("%s must be both Metallic (strong general material) and RM_VexxithPlate" % VEXXITH)
        cats = re.search(r"<stuffCategories[^>]*>(.*?)</stuffCategories>", door, flags=re.S)
        if not cats or re.findall(r"<li>([^<]+)</li>", cats.group(1)) != ["RM_VexxithPlate"]:
            bad.append("%s must accept RM_VexxithPlate and nothing else (plate-only)" % VDOOR)
        if 'Inherit="False"' not in door:
            bad.append("%s stuffCategories must not inherit DoorBase's Metallic/Woody/Stony" % VDOOR)
        if not re.search(r'DamageDef\[defName="%s"\]' % ACID, patch) or NS + "RM_AcidDamageExtension" not in patch:
            bad.append("Patches/RM_Cauldron_AcidDamage.xml does not mark %s as acid" % ACID)
        if "PatchOperationConditional" not in patch or 'DamageDef[defName="RM_BloomAcid"]' not in patch:
            bad.append("Patches/RM_Cauldron_AcidDamage.xml does not mark Warscar's RM_BloomAcid (guarded) as acid")
        if bad:
            _fail("; ".join(bad))

    with _comp(t, "flora_expansion_shape", toggle="floraExpansionEnabled"):
        # CAULDRON_FLORA_EXPANSION_BUILD_1: parsed from the mod's own XML, so it needs no live game.
        def _body(rel, name, tag="ThingDef"):
            x = re.sub(r"<!--.*?-->", "", _def_text(rel), flags=re.S)
            m = re.search(r"<defName>%s</defName>(.*?)</%s>" % (name, tag), x, flags=re.S)
            return m.group(1) if m else None
        bad = []
        biome = re.sub(r"<!--.*?-->", "", _def_text("BiomeDefs/RM_Cauldron.xml"), flags=re.S)
        if "<RM_Xithess>" not in biome:
            bad.append("control: an original roster row (RM_Xithess) is missing, parser broke")
        for n in ("RM_Tsevrix", "RM_Ixalith", "RM_Fexxil", "RM_Sessarix", "RM_Kissaveth", "RM_Selvix"):
            b = _body("ThingDefs_Plants/RM_CauldronFloraExpansion.xml", n)
            if b is None:
                bad.append("%s missing" % n)
                continue
            if not re.search(r"<%s>[\d.]+</%s>" % (n, n), biome):
                bad.append("%s not in RM_Cauldron wildPlants (XML element form)" % n)
            if "CompTick" in b:
                bad.append("%s overrides CompTick" % n)
        ix = _body("ThingDefs_Plants/RM_CauldronFloraExpansion.xml", "RM_Ixalith") or ""
        if "<harvestYield>0</harvestYield>" not in ix:
            bad.append("ixalith must have harvestYield 0")
        se = _body("ThingDefs_Plants/RM_CauldronFloraExpansion.xml", "RM_Sessarix") or ""
        if "<harvestedThingDef>Chemfuel</harvestedThingDef>" not in se or "RM_CauldronSoil" not in se or "<li>Soil</li>" not in se:
            bad.append("sessarix must yield Chemfuel and blacklist soil terrains")
        sv = _body("ThingDefs_Plants/RM_CauldronFloraExpansion.xml", "RM_Selvix") or ""
        if "<harvestedThingDef>MedicineHerbal</harvestedThingDef>" not in sv:
            bad.append("selvix must yield MedicineHerbal")
        pulp = _body("ThingDefs_Items/RM_CauldronFloraItems.xml", "RM_TsevrixPulp") or ""
        roast = _body("ThingDefs_Items/RM_CauldronFloraItems.xml", "RM_TsevrixRoasted") or ""
        if "ToxicBuildup" not in pulp or "ToxicBuildup" in roast or not roast:
            bad.append("pulp must carry ToxicBuildup and the roasted product must not (both arms)")
        kv = _body("ThingDefs_Plants/RM_CauldronFloraExpansion.xml", "RM_Kissaveth") or ""
        if "CompProperties_GasOnDamage" not in kv or "RM_CompProperties_GasOnCut" not in kv or "xplo" in kv:
            bad.append("kissaveth needs gas-on-damage and gas-on-cut, and no explosion")
        if bad:
            _fail("; ".join(bad))

    with _comp(t, "fexxil_venom_shape", toggle="fexxilVenomEnabled"):
        fxt = _def_text("ThingDefs_Plants/RM_CauldronFloraExpansion.xml")
        dmg = _def_text("DamageDefs/RM_FexxilScratch.xml")
        if "CompProperties_ContactVenom" not in fxt or "RM_FexxilScratch" not in fxt or "<hediff>ToxicBuildup</hediff>" not in dmg:
            _fail("fexxil must carry ContactVenom with a damage def whose additionalHediffs gives ToxicBuildup")

    with _comp(t, "types_resolve"):
        if _live(t):
            bad = []
            for typ in TYPES:
                r = t.bridge_call("jawa/type_probe", typeName=typ)
                _ok(r, "type_probe(%s)" % typ)
                if r.get("resolved") is not True:
                    bad.append("%s did not resolve" % typ)
                    continue
                if r.get("inAllTypesByIdentity") is not True:
                    bad.append("%s resolved but is not in GenTypes.AllTypes" % typ)
                if r.get("mvidMatchesFile") is False:
                    bad.append("%s: the loaded DLL is not the file on disk (redeployed after launch?)" % typ)
                if "mandrake.rm.biomes" not in (r.get("carryingMods") or []):
                    bad.append("%s is not carried by mandrake.rm.biomes: %r" % (typ, r.get("carryingMods")))
            # Sanity probe: the instrument must be able to say "unresolved".
            probe = t.bridge_call("jawa/type_probe", typeName=NS + "NoSuchType_Probe")
            if (probe or {}).get("resolved") is not False:
                _fail("sanity probe: an absent type resolved or the probe errored: %r" % probe)
            if bad:
                _fail("; ".join(bad))

    with _comp(t, "biome_weather_table"):
        if _live(t):
            f = _get_defs(t, "BiomeDef/%s" % BIOME, "baseWeatherCommonalities", deep=True)
            table = _def_field(f.get(BIOME), "baseWeatherCommonalities")
            if not isinstance(table, list) or not table:
                _unmeasured(t, "post-patch weather table unreadable: %r" % (table,))
            w = {}
            for x in table:
                if not isinstance(x, dict):
                    _unmeasured(t, "weather table rows are not dicts (deep serialise failed): %r" % (x,))
                w[x.get("weather") or x.get("weatherDef")] = x.get("commonality") or 0
            _note(t, "BiomeDef weather table", w)
            missing = [n for n in WEATHERS if not w.get(n)]
            if missing:
                _fail("owned weather(s) absent or zero in the biome table: %s" % missing)
            stock = [n for n in ("Clear", "Fog", "Rain", "RainyThunderstorm", "FoggyRain",
                                 "SnowGentle", "SnowHard") if w.get(n)]
            if stock:
                _fail("stock weather with commonality > 0 (sheet law: never rain, never snow, "
                      "never clear): %s" % stock)
            if w.get(BLOOM, 0) >= w.get("RM_ScatterDusk", 0):
                _fail("the vent bloom (%s) is at least as common as the standing scatter-dusk (%s)"
                      % (w.get(BLOOM), w.get("RM_ScatterDusk")))

    with _comp(t, "biome_roster"):
        if _live(t):
            find = ",".join(list(NATIVES) + list(FLORA))
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME, find=find, plants=True)
            _ok(r, "biome_probe")
            rows = r.get("biomes") or []
            if len(rows) != 1 or rows[0].get("defName") != BIOME:
                _unmeasured(t, "biome_probe returned no row for %s: %r" % (BIOME, [x.get("defName") for x in rows]))
            row = rows[0]
            dens = row.get("animalDensity")
            if not isinstance(dens, (int, float)) or dens <= 0:
                _fail("animalDensity %r: <= 0 means the animal roster can never spawn" % (dens,))
            res = dict((x.get("defName"), x.get("state")) for x in (row.get("findResults") or []))
            if not res:
                _unmeasured(t, "biome_probe findResults empty: %r" % (row.get("findResults"),))
            notspawn = sorted(n for n in list(NATIVES) + list(FLORA) if res.get(n) != "spawning")
            _note(t, "biome roster states", res)
            if notspawn:
                _fail("owned natives/flora not spawning in %s (zeroed/absent): %s" % (BIOME, notspawn))
            # Sanity probe: the instrument must be able to say "absent".
            p = t.bridge_call("jawa/biome_probe", biomes=BIOME, find="RM_Cauldron_NoSuchBeast_Probe")
            pr = (((p or {}).get("biomes") or [{}])[0].get("findResults") or [{}])[0]
            if pr.get("state") != "absent":
                _fail("sanity probe: an absent animal did not read 'absent': %r" % pr)

    with _comp(t, "biome_worker_and_terrain"):
        if _live(t):
            f = _get_defs(t, "BiomeDef/%s" % BIOME, "workerClass", deep=True)
            wc = _def_field(f.get(BIOME), "workerClass")
            if wc is None:
                _unmeasured(t, "BiomeDef.workerClass unreadable")
            if "BiomesPlus" in str(wc) or not str(wc).endswith("RM_BiomeWorker_Cauldron"):
                _fail("workerClass is %r; it must be the mod's own RM_BiomeWorker_Cauldron (a donor "
                      "type here is a hard dependency)" % (wc,))
            r = t.bridge_call("jawa/get_def", defName=BIOME, defType="BiomeDef")
            _ok(r, "get_def(%s)" % BIOME)
            tf = ((r.get("extra") or {}).get("terrainsByFertility"))
            if not isinstance(tf, list) or not tf:
                _unmeasured(t, "get_def extra.terrainsByFertility unreadable: %r" % (tf,))
            names = set(x.get("terrain") for x in tf)
            if names != {"RM_CauldronSoil", "RM_CauldronSoilRich"}:
                _fail("terrainsByFertility names %s, expected exactly the mod's own two soils" % sorted(names))
            soil = _get_defs(t, "TerrainDef/RM_CauldronSoil;TerrainDef/RM_CauldronSoilRich", "fertility")
            lo, hi = (soil.get("RM_CauldronSoil") or {}).get("fertility"), \
                     (soil.get("RM_CauldronSoilRich") or {}).get("fertility")
            if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
                _unmeasured(t, "soil fertility unreadable: %r %r" % (lo, hi))
            if not (0 < lo < 1.0 < hi):
                _fail("soil fertility %r (plain) / %r (rich): plain must be below 1.0 and rich above" % (lo, hi))

    with _comp(t, "nettle_habitat_wired"):
        if _live(t):
            r = t.bridge_call("jawa/get_def", defName=NETTLE, defType="ThingDef")
            _ok(r, "get_def(%s)" % NETTLE)
            ext = (r.get("extra") or {}).get("modExtensions")
            if not isinstance(ext, list):
                _unmeasured(t, "get_def extra.modExtensions unreadable: %r" % (ext,))
            if "RM_CondensateHabitatExtension" not in ext:
                _fail("%s carries no RM_CondensateHabitatExtension (the colonising pass never "
                      "sees it): %r" % (NETTLE, ext))


    with _comp(t, "vent_habitat_wired"):
        if _live(t):
            for plant, hab in sorted(VENT_PLANTS.items()):
                r = t.bridge_call("jawa/get_def", defName=plant, defType="ThingDef")
                _ok(r, "get_def(%s)" % plant)
                ext = (r.get("extra") or {}).get("modExtensions")
                if not isinstance(ext, list):
                    _unmeasured(t, "get_def extra.modExtensions unreadable for %s: %r" % (plant, ext))
                if "RM_CondensateHabitatExtension" not in ext:
                    _fail("%s (vent habitat %s) carries no RM_CondensateHabitatExtension: %r" % (plant, hab, ext))
            r = t.bridge_call("jawa/get_def", defName=VENT, defType="ThingDef")
            _ok(r, "get_def(%s)" % VENT)
            ext = (r.get("extra") or {}).get("modExtensions")
            if not isinstance(ext, list) or "RM_VentExtension" not in ext:
                _fail("%s carries no RM_VentExtension (no weather table, no falter): %r" % (VENT, ext))


# --------------------------------------------------------------------------- chain: weather

@suite.chain("weather")
def weather_chain(t):
    _pad(t, "spawn")
    with _comp(t, "weather_defs_laws"):
        if _live(t):
            f = _get_defs(t, ";".join("WeatherDef/%s" % w for w in WEATHERS),
                          "rainRate,snowRate,sandRate,windSpeedFactor,doToxicBuildup,isBad")
            bad = []
            for w in WEATHERS:
                row = f.get(w) or {}
                for k in ("rainRate", "snowRate", "windSpeedFactor"):
                    if not isinstance(row.get(k), (int, float)):
                        _unmeasured(t, "%s.%s unreadable: %r" % (w, k, row.get(k)))
                for k in ("rainRate", "snowRate", "sandRate"):
                    if k == "sandRate" and not isinstance(row.get(k), (int, float)):
                        continue            # not a field of this game version: nothing to hold at zero
                    if row[k] != 0:
                        bad.append("%s.%s=%r (this biome never rains, snows or storms sand)" % (w, k, row[k]))
                if row["windSpeedFactor"] < 0.5:
                    bad.append("%s.windSpeedFactor=%r (no calm: every weather carries wind)" % (w, row["windSpeedFactor"]))
            vb, sd = f.get(BLOOM) or {}, f.get("RM_ScatterDusk") or {}
            if vb.get("doToxicBuildup") is not False:
                bad.append("%s.doToxicBuildup=%r (the bloom's only tax is RM_VentMetalLoad; vanilla "
                           "toxic buildup on top would tax twice)" % (BLOOM, vb.get("doToxicBuildup")))
            if vb.get("isBad") is not True:
                bad.append("%s.isBad=%r (it is the biome's hazard)" % (BLOOM, vb.get("isBad")))
            if sd.get("isBad") is not False:
                bad.append("RM_ScatterDusk.isBad=%r (it is the standing state)" % (sd.get("isBad"),))
            if bad:
                _fail("; ".join(bad))

    def body():
        with _comp(t, "weathers_selectable"):
            if _live(t):
                got = {}
                for w in WEATHERS:
                    _ok(t.bridge_call("jawa/weather_set", weather=w, lockWeather=True), "weather_set(%s)" % w)
                    got[w] = _weather_now(t)
                    if got[w] is None:
                        _unmeasured(t, "weather_get returned no current weather after setting %s" % w)
                _note(t, "weather read-back per lock", got)
                wrong = [w for w in WEATHERS if got[w] != w]
                if wrong:
                    _fail("weather(s) that cannot be set/read back as themselves: %s" % wrong)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: settings

@suite.chain("settings")
def settings_chain(t):
    _pad(t, "spawn")
    with _comp(t, "defaults"):
        if _live(t):
            bad = {}
            for field, want in sorted(DEFAULTS.items()):
                got = _get_setting(t, field)
                if not _same(got, want):
                    bad[field] = got
            if bad:
                _fail("settings not at shipped defaults (or field missing): %s" % bad)
            # Sanity probe: reading a nonexistent field must fail loudly, not return a default.
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                              field="noSuchFieldProbe")
            if (r or {}).get("success") is not False:
                _fail("sanity probe: reading a nonexistent settings field did not fail: %r" % r)

    # Settings whose EFFECT this suite cannot drive (see the module docstring): the field must exist,
    # read its shipped default and be writable, restored afterwards.
    # CAULDRON_VENT_ENRICHMENT_HOOKS_1: ventsEnabled is worldgen (a new Cauldron map is needed to see it),
    # ventFalterMessage is a Messages.Message the bridge cannot list, ventGardensEnabled only acts on a map whose
    # biome roster names the flowers (a Cauldron-biome map) and takes days of ticks.
    # vexxithDoorEnabled acts at startup (restart to apply), which a live session cannot cross.
    for field in ("vexxissAttacksIgniter", "condensateGardensEnabled", "ventsEnabled", "ventFalterMessage",
                  "ventGardensEnabled", "vexxithDoorEnabled",
                  # CAULDRON_ENRICHMENT_VISUALS_1: beads need hours of locked dewfall on unroofed non-home ground;
                  # saturation and flecks are dormant until their art is installed (and are appearance anyway);
                  # prints live on CreatureBehaviors' grid, which no bridge tool reads.
                  "dewfallBeadsEnabled", "dewfallSaturationEnabled", "assayFlecksEnabled", "vexxissPrintsEnabled"):
        with _comp(t, "%s_roundtrip" % field, toggle=field):
            if _live(t):
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s is not at its shipped default" % field)
                with _setting(t, field, not DEFAULTS[field]):
                    pass
    with _comp(t, "biomeRarityFactor_roundtrip"):
        if _live(t):
            if not _same(_get_setting(t, "biomeRarityFactor"), DEFAULTS["biomeRarityFactor"]):
                _fail("biomeRarityFactor is not at its shipped default")
            with _setting(t, "biomeRarityFactor", 0.0):
                pass


# --------------------------------------------------------------------------- chain: items and defs read as state

@suite.chain("items")
def items_chain(t):
    _pad(t, "spawn")
    with _comp(t, "suush_and_vexxiss_comps"):
        if _live(t):
            def comps(defName):
                r = t.bridge_call("jawa/get_def", defName=defName, defType="ThingDef")
                _ok(r, "get_def(%s)" % defName)
                cs = r.get("comps")
                if not isinstance(cs, list):
                    _unmeasured(t, "get_def(%s) returned no readable comps list: %r" % (defName, cs))
                return r, [c.get("class") if isinstance(c, dict) else str(c) for c in cs]
            sr, sc = comps(SUUSH)
            vr, vc = comps(VEXXISS)
            _note(t, "comps", {SUUSH: sc, VEXXISS: vc})
            if "CompProperties_Explosive" not in sc:
                _fail("%s carries no CompProperties_Explosive (it detonates when shot): %s" % (SUUSH, sc))
            if "CompProperties_Explosive" in vc:
                _fail("%s carries CompProperties_Explosive: owner ruling, NO explosion alive or dead "
                      "(\"too many exploding giant beasts\")" % VEXXISS)
            for need in ("RM_CompProperties_VexxissBehaviour", "CompProperties_Shearable"):
                if need not in vc:
                    _fail("%s lacks %s: %s" % (VEXXISS, need, vc))
            shear = [c for c in (vr.get("comps") or []) if isinstance(c, dict)
                     and c.get("class") == "CompProperties_Shearable"]
            wool = ((shear[0].get("fields") or {}).get("woolDef")) if shear else None
            if wool != "RM_Vexxith":
                _fail("%s shears %r, expected RM_Vexxith" % (VEXXISS, wool))
            mft = (sr.get("statBases") or {}).get("MaxFlightTime")
            if not isinstance(mft, (int, float)):
                _unmeasured(t, "%s statBases carries no MaxFlightTime: %r" % (SUUSH, sr.get("statBases")))
            if mft <= 0:
                _fail("%s MaxFlightTime=%r: it cannot float" % (SUUSH, mft))

    with _comp(t, "zisska_yields_and_toxic_meat"):
        if _live(t):
            f = _get_defs(t, "ThingDef/%s" % ZISSKA, "butcherProducts,race", deep=True)
            row = f.get(ZISSKA) or {}
            bp = _def_field(row, "butcherProducts")
            race = _def_field(row, "race")
            if not isinstance(bp, list) or not isinstance(race, dict):
                _unmeasured(t, "butcherProducts/race unreadable: %r / %r" % (bp, race))
            steel = sum(int(x.get("count") or 0) for x in bp
                        if isinstance(x, dict) and x.get("thingDef") == "Steel")
            if steel < 1:
                _fail("%s butchers into no steel (the concentrated metal): %r" % (ZISSKA, bp))
            if race.get("specificMeatDef") != "RM_ZisskaMeat":
                _fail("%s meat is %r, expected RM_ZisskaMeat" % (ZISSKA, race.get("specificMeatDef")))
            m = _get_defs(t, "ThingDef/RM_ZisskaMeat", "ingestible", deep=True).get("RM_ZisskaMeat") or {}
            ing = _def_field(m, "ingestible")
            docs = (ing or {}).get("outcomeDoers") if isinstance(ing, dict) else None
            if not isinstance(docs, list):
                _unmeasured(t, "RM_ZisskaMeat ingestible.outcomeDoers unreadable: %r" % (ing,))
            if not any(isinstance(d, dict) and d.get("hediffDef") == "ToxicBuildup" for d in docs):
                _fail("RM_ZisskaMeat gives no ToxicBuildup when eaten (the toxic prized meat): %r" % docs)


# --------------------------------------------------------------------------- chain: vexxith ignores acid

def _acid_hit(t, x, z, want_def):
    """AcidBurn at one cell; (hpBefore, hpAfter) of the `want_def` row, UNMEASURED when unreadable."""
    r = t.bridge_call("jawa/damage", damageDef=ACID, amount=20.0, x=x, z=z)
    _ok(r, "damage(%s at %d,%d)" % (ACID, x, z))
    rows = [w for w in (r.get("results") or []) if isinstance(w, dict) and w.get("def") == want_def]
    if not rows or rows[0].get("hitPointsBefore") is None or rows[0].get("hitPointsAfter") is None:
        _unmeasured(t, "damage at %d,%d returned no readable %s row: %r" % (x, z, want_def, r))
    return rows[0]["hitPointsBefore"], rows[0]["hitPointsAfter"]


@suite.chain("acid")
def acid_chain(t):
    """VEXXITH_CLOSED_LOOP_BUILD_1: a vexxith wall and the vexxith door take no AcidBurn; a steel wall
    beside them does (the control), and with the toggle off the vexxith wall burns too."""
    _prep(t, "spawn")
    x, z = t.anchor
    cells = {"vwall": (x - 4, z, "Wall", VEXXITH), "vdoor": (x, z, VDOOR, VEXXITH),
             "swall": (x + 4, z, "Wall", "Steel"), "vwall2": (x - 4, z + 4, "Wall", VEXXITH)}

    def body():
        with _comp(t, "acid_site_ready", poison=True):
            if _live(t):
                for key, (cx, cz, d, stuff) in sorted(cells.items()):
                    r = _ok(t.bridge_call("jawa/build_batch", ops="%s:%d,%d" % (d, cx, cz), stuff=stuff,
                                          readBack=2), "build_batch %s/%s" % (d, stuff))
                    back = [w for w in (r.get("things") or []) if isinstance(w, dict)]
                    if r.get("survived") != 1 or not back or back[0].get("stuff") != stuff:
                        _unmeasured(t, "%s of %s did not stand: %r" % (d, stuff, r))
        with _comp(t, "vexxith_acid_proof", toggle="vexxithAcidImmunityEnabled"):
            if _live(t):
                got = dict((k, _acid_hit(t, cx, cz, d)) for k, (cx, cz, d, _) in sorted(cells.items())
                           if k != "vwall2")
                _note(t, "AcidBurn 20: hp before/after", got)
                if not got["swall"][1] < got["swall"][0]:
                    _unmeasured(t, "control: AcidBurn did not hurt a steel wall %r, so it proves nothing"
                                   % (got["swall"],))
                for k in ("vwall", "vdoor"):
                    if got[k][1] != got[k][0]:
                        _fail("%s lost hit points to acid: %r (it must be acid-proof)" % (k, got[k]))
        with _comp(t, "vexxith_acid_toggle_off", toggle="vexxithAcidImmunityEnabled"):
            if _live(t):
                cx, cz, d, _ = cells["vwall2"]
                with _setting(t, "vexxithAcidImmunityEnabled", False):
                    before, after = _acid_hit(t, cx, cz, d)
                _note(t, "AcidBurn 20 with the toggle OFF: vexxith wall hp before/after", [before, after])
                if not after < before:
                    _fail("vexxithAcidImmunityEnabled OFF but the vexxith wall still ignored acid (%r -> %r)"
                          % (before, after))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: fauna

@suite.chain("fauna")
def fauna_chain(t):
    _prep(t, "fauna")
    rect = _rect(t)
    x0, z0 = rect[0] + 3, rect[1] + 3
    try:
        with _comp(t, "fauna_spawns"):
            if _live(t):
                if len(KINDS) < 5:
                    _fail("parsed %d PawnKindDefs, expected 5" % len(KINDS))
                ids = {}
                for i, kind in enumerate(KINDS):
                    ids[kind] = _spawn(t, kind, x0 + (i % 4) * 5, z0 + (i // 4) * 5)
                rows = _rows(t, rect=_rs(rect))
                lost = [k for k, pid in ids.items()
                        if pid not in rows or rows[pid].get("dead") or rows[pid].get("kindDef") != k]
                _note(t, "wild kinds spawned", {"asked": len(KINDS), "lost": lost})
                if lost:
                    _fail("kind(s) spawned no living pawn of that kind in the rect: %s" % lost)
        with _comp(t, "suush_can_fly"):
            if _live(t):
                su = [pid for pid, p in _rows(t, rect=_rs(rect)).items() if p.get("kindDef") == SUUSH]
                if not su:
                    _unmeasured(t, "no suush on the pad to read")
                r = t.bridge_call("jawa/pawn_flight", action="report", pawn=su[0])
                rows = (_ok(r, "pawn_flight").get("pawns") or [])
                if not rows or "canEverFly" not in rows[0]:
                    _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
                if rows[0].get("canEverFly") is not True:
                    _fail("%s canEverFly=%r (MaxFlightTime stat %r): it cannot drift"
                          % (SUUSH, rows[0].get("canEverFly"), rows[0].get("maxFlightTimeStat")))
    finally:
        _stable(t, lambda: None)


# --------------------------------------------------------------------------- chain: the Suush

@suite.chain("suush")
def suush_chain(t):
    _prep(t, "suush")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "suush_ignores_melee"):
            if _live(t):
                # LIVE 2026-10-03: a WILD suush is a flier that flees damage and leaves the map, so "row is None" after 400 ticks
                # could not tell "detonated" from "flew away". A player-faction animal stays put, so absence means it died.
                ids["melee"] = _spawn(t, SUUSH, x - 8, z, "player")
                t.bridge_call("jawa/damage", damageDef="Cut", amount=2, thingId=ids["melee"], allowColonists=True)
                t.wait_ticks(400)
                row = _rows(t).get(ids["melee"])
                if not row or row.get("dead"):
                    _fail("a suush hit by a Cut (melee) detonated or died: only Bullet/Bomb start "
                          "the wick, melee must not (%r)" % (row,))
        with _comp(t, "suush_detonates_when_shot"):
            if _live(t):
                if ids.get("melee") not in _rows(t):
                    _unmeasured(t, "the melee control suush is gone, cannot attribute the shot suush")
                ids["shot"] = _spawn(t, SUUSH, x + 8, z, "player")
                # LIVE 2026-10-03: jawa/damage SKIPS player-faction pawns unless allowColonists=True, so the first runs hit nothing.
                # And a Pawn's Thing.HitPoints is ~0, so before requiredDamageTypeToExplode=Bullet any damage (Cut 1, Stun 1)
                # detonated a fresh suush; the Bullet shot below goes up on purpose, so declare its fires.
                t.expect("fire", lambda e: True)
                t.bridge_call("jawa/damage", damageDef="Bullet", amount=2, thingId=ids["shot"], allowColonists=True)
                t.wait_ticks(400)
                rows = _rows(t)
                _note(t, "shot suush row / melee control still there", [rows.get(ids["shot"]), ids["melee"] in rows])
                if ids["melee"] not in rows:
                    _unmeasured(t, "the control suush vanished too (blast reach or something else)")
                if ids["shot"] in rows and not rows[ids["shot"]].get("dead"):
                    _fail("a suush hit by a Bullet is still alive 400 ticks later: startWickOnDamageTaken "
                          "did not fire")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: flora

def _assay_grade(lines):
    m = re.search(r"Assay grade:\s*(\w+)", " ".join(lines))
    return m.group(1).lower() if m else None


def _assay_steel(lines):
    m = re.search(r"~\s*([\d.]+)\s*steel", " ".join(lines), re.I)
    return float(m.group(1)) if m else None


@suite.chain("flora")
def flora_chain(t):
    _prep(t, "flora")
    x, z = t.anchor
    rect = _rect(t)
    ids = {}

    def body():
        with _comp(t, "flora_spawns"):
            if _live(t):
                if len(FLORA) < 11:
                    _fail("parsed %d plant defs, expected 11" % len(FLORA))
                cells = {}
                for i, d in enumerate(FLORA):
                    cx, cz = rect[0] + 2 + (i % 4) * 3, rect[1] + 2 + (i // 4) * 3 + 8
                    cells[d] = (cx, cz)
                    if d in SOIL_FORBIDDEN:
                        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,1,1" % (ROCK, cx, cz), layer="top")
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, cx, cz), growth=1.0)
                lost = [d for d, (cx, cz) in cells.items() if _count(t, d, "%d,%d,1,1" % (cx, cz)) < 1]
                _note(t, "flora set", {"asked": len(FLORA), "lost": lost})
                if lost:
                    _fail("plant def(s) did not stand after set_plants: %s" % lost)
        # Three thornwoods at three growths for the assay line (harvestMinGrowth 0.2).
        with _comp(t, "assay_grades", toggle="assayGradeEnabled"):
            if _live(t):
                want = (("unripe", 0.1), ("fair", 0.6), ("lode", 1.0))
                got = {}
                for i, (grade, growth) in enumerate(want):
                    cx, cz = x - 6 + i * 3, z - 8
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (THORN, cx, cz), growth=growth)
                    th = _things(t, THORN, "%d,%d,1,1" % (cx, cz))
                    if not th:
                        _unmeasured(t, "no thornwood at growth %s after set_plants" % growth)
                    ids[grade] = th[0]["id"]
                    _, lines = _inspect(t, th[0]["id"])
                    got[grade] = _assay_grade(lines)
                    if grade == "lode":
                        ids["lode_steel"] = _assay_steel(lines)
                _note(t, "assay grades read per growth 0.1/0.6/1.0", got)
                if None in got.values():
                    _fail("a thornwood inspect carries no 'Assay grade' line: %r" % got)
                wrong = dict((g, got[g]) for g, _ in want if got[g] != g)
                if wrong:
                    _fail("assay grade wrong for growth (expected: read): %s" % wrong)
                if ids.get("lode_steel") is None or abs(ids["lode_steel"] - THORN_FULL) > 1.0:
                    _fail("a full-grown thornwood promises ~%r steel, expected ~%d"
                          % (ids.get("lode_steel"), THORN_FULL))
        with _comp(t, "assay_toggle_off", toggle="assayGradeEnabled"):
            if _live(t):
                if "lode" not in ids:
                    _unmeasured(t, "no full-grown thornwood read (assay_grades did not run)")
                with _setting(t, "assayGradeEnabled", False):
                    _, lines = _inspect(t, ids["lode"])
                if _assay_grade(lines) is not None:
                    _fail("assayGradeEnabled OFF but the tree still reads an assay line: %s" % lines)
        with _comp(t, "assay_factor_scales", toggle="metalYieldFactor"):
            if _live(t):
                if "lode" not in ids:
                    _unmeasured(t, "no full-grown thornwood read (assay_grades did not run)")
                with _setting(t, "metalYieldFactor", 2.0):
                    _, lines = _inspect(t, ids["lode"])
                    doubled = _assay_steel(lines)
                if doubled is None or abs(doubled - 2 * THORN_FULL) > 2.0:
                    _fail("metalYieldFactor 2.0 promises ~%r steel from a full thornwood, expected ~%d "
                          "(1.0 reads ~%d)" % (doubled, 2 * THORN_FULL, THORN_FULL))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the metal yield

def _harvest_one(t, col, tree, rect):
    """Designate and order a harvest of one tree, then wait until its wood lands (<= 5 x 1000 ticks).
    Returns wood gained. The designation makes the plant harvestable-by-order; the direct job makes it
    immediate."""
    before = _stack_total(t, "WoodLog", _rs(rect))
    x, z = tree["x"], tree["z"]
    t.bridge_call("jawa/designate_batch", action="add", designation="HarvestPlant", rect="%d,%d,1,1" % (x, z))
    r = t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="Harvest", targetAId=tree["id"],
                      queue=False, waitTicks=60)
    # queue=False interrupts a wandering colonist (GoForWalk on the second harvest, 2026-10-08 live: queued behind the
    # walk it never started). A job the bridge ACCEPTED is enough; the wood landing below is the real proof.
    if not (isinstance(r, dict) and (r.get("success") is not False or r.get("accepted"))):
        _fail("ordered_job(Harvest) failed: %r" % (r,))
    for _ in range(5):
        t.wait_ticks(1000)
        if _stack_total(t, "WoodLog", _rs(rect)) > before:
            break
    return _stack_total(t, "WoodLog", _rs(rect)) - before


@suite.chain("yield")
def yield_chain(t):
    _prep(t, "yield")
    x, z = t.anchor
    rect = _rect(t)
    ids = {}

    def body():
        with _comp(t, "yield_site_ready", poison=True):
            if _live(t):
                for i in range(3):
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (MARTYR, x - 4 + i * 4, z - 6), growth=1.0)
                trees = sorted(_things(t, MARTYR, _rs(rect)), key=lambda w: w.get("x", 0))
                if len(trees) != 3:
                    _unmeasured(t, "expected 3 martyr trees after set_plants, read %d" % len(trees))
                ids["trees"] = trees
                ids["col"] = _spawn(t, "Colonist", x, z + 6, faction="player")
                _full(t, ids["col"])
                if _stack_total(t, "Steel", _rs(rect)) != 0:
                    _unmeasured(t, "steel already on the pad before any harvest")
        with _comp(t, "harvest_pays_metal", toggle="metalYieldEnabled"):
            if _live(t):
                wood = _harvest_one(t, ids["col"], ids["trees"][0], rect)
                steel = _stack_total(t, "Steel", _rs(rect))
                _note(t, "martyr harvest 1 (factor 1.0): wood / steel", [wood, steel])
                if wood < 1:
                    _unmeasured(t, "no wood from the first harvest in 5000 ticks (job not done): "
                                   "cannot judge the metal beside it")
                if not (MARTYR_FULL - 1 <= steel <= MARTYR_FULL + 1):
                    _fail("a full-grown martyr tree paid %d steel beside %d wood, expected ~%d"
                          % (steel, wood, MARTYR_FULL))
                ids["steel1"] = steel
        with _comp(t, "yield_factor_scales", toggle="metalYieldFactor"):
            if _live(t):
                if "steel1" not in ids:
                    _unmeasured(t, "no factor-1.0 baseline (harvest_pays_metal did not pay)")
                with _setting(t, "metalYieldFactor", 2.0):
                    wood = _harvest_one(t, ids["col"], ids["trees"][1], rect)
                steel2 = _stack_total(t, "Steel", _rs(rect)) - ids["steel1"]
                _note(t, "martyr harvest 2 (factor 2.0): wood / steel", [wood, steel2])
                if wood < 1:
                    _unmeasured(t, "no wood from the second harvest in 5000 ticks")
                if not (2 * MARTYR_FULL - 2 <= steel2 <= 2 * MARTYR_FULL + 2):
                    _fail("metalYieldFactor 2.0 paid %d steel from a full martyr tree, expected ~%d "
                          "(factor 1.0 paid %d)" % (steel2, 2 * MARTYR_FULL, ids["steel1"]))
                ids["steel_total"] = ids["steel1"] + steel2
        with _comp(t, "yield_toggle_off", toggle="metalYieldEnabled"):
            if _live(t):
                if "steel_total" not in ids:
                    _unmeasured(t, "no steel baseline from the earlier harvests")
                with _setting(t, "metalYieldEnabled", False):
                    wood = _harvest_one(t, ids["col"], ids["trees"][2], rect)
                steel3 = _stack_total(t, "Steel", _rs(rect)) - ids["steel_total"]
                _note(t, "martyr harvest 3 (metalYieldEnabled OFF): wood / steel", [wood, steel3])
                if wood < 1:
                    _unmeasured(t, "no wood from the third harvest in 5000 ticks")
                if steel3 != 0:
                    _fail("metalYieldEnabled OFF but the harvest still paid %d steel" % steel3)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the vent bloom

def _pick_animals(t):
    """(native, nonnative) kind defNames for THIS map's biome, from the stock herbivores, read off the
    biome's resolved roster (biome_probe). None, None when this map offers no clean pair."""
    mi = t.bridge_call("jawa/map_info")
    if not _live(t):
        return None, None
    biome = (mi or {}).get("mapBiome")
    if not biome:
        return None, None
    r = t.bridge_call("jawa/biome_probe", biomes=biome, find=",".join(HERBIVORES))
    rows = (r or {}).get("biomes") or []
    if not rows:
        return None, None
    states = dict((x.get("defName"), x.get("state")) for x in (rows[0].get("findResults") or []))
    native = [k for k in HERBIVORES if states.get(k) == "spawning"]
    non = [k for k in HERBIVORES if states.get(k) == "absent"]
    return (native[0] if native else None), (non[0] if non else None)


@suite.chain("bloom")
def bloom_chain(t):
    _prep(t, "bloom")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "bloom_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, BLOOM)
                room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,9,9" % (x - 11, z - 4), stuffDef="Steel")
                _ok(room, "make_empty_room")
                ids["out"] = _spawn(t, "Colonist", x + 6, z + 8, faction="player")
                ids["in"] = _spawn(t, "Colonist", x - 7, z, faction="player")
                for p in (ids["out"], ids["in"]):
                    t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
                roof = t.bridge_call("jawa/get_roof_batch", rects="%d,%d,7,7" % (x - 10, z - 3))
                if not _roofed(roof):
                    _unmeasured(t, "the sealed room is not roofed (get_roof_batch %r): cannot tell "
                                   "outdoors from indoors" % roof)
                native, non = _pick_animals(t)
                _note(t, "map-biome native / non-native herbivore picked", [native, non])
                if native:
                    ids["native"] = _spawn(t, native, x + 10, z - 8)
                if non:
                    ids["non"] = _spawn(t, non, x + 14, z + 4)
                tr = _weather_transition_done(t)
                _note(t, "weather transition factor after the wait", tr)
                _next_interval_jump(t)
                t.wait_ticks(40)
        with _comp(t, "bloom_loads_exposed", toggle="ventBloomExposureEnabled"):
            if _live(t):
                rows = _rows(t, health=True)
                h = _hediff(rows.get(ids["out"]), HEDIFF)
                _note(t, "outdoor colonist hediff", h)
                if rows.get(ids["out"]) is None:
                    _unmeasured(t, "outdoor colonist missing from list_pawns")
                if h is None:
                    _fail("an outdoor, unroofed colonist under %s carries no %s after an exposure tick" % (BLOOM, HEDIFF))
                if not (h.get("severity") or 0) > 0:
                    _fail("%s present but severity %r" % (HEDIFF, h.get("severity")))
                ids["sev1"] = h["severity"]
        with _comp(t, "bloom_no_double_tax"):
            if _live(t):
                if ids.get("sev1") is None:
                    _unmeasured(t, "no exposed colonist reading (bloom_loads_exposed did not pass)")
                rows = _rows(t, health=True)
                if _hediff(rows.get(ids["out"]), "ToxicBuildup") is not None:
                    _fail("the exposed colonist also carries vanilla ToxicBuildup: the bloom taxes twice")
        with _comp(t, "bloom_spares_roofed", toggle="ventBloomExposureEnabled"):
            if _live(t):
                if ids.get("sev1") is None:
                    _unmeasured(t, "no exposed control colonist reading (the exposure tick may not have run)")
                row = _rows(t, health=True).get(ids["in"])
                if row is None:
                    _unmeasured(t, "roofed colonist missing from list_pawns")
                if _hediff(row, HEDIFF) is not None:
                    _fail("the colonist inside the roofed room also gained %s (the roof is ignored)" % HEDIFF)
        with _comp(t, "bloom_spares_natives"):
            if _live(t):
                if "native" not in ids or "non" not in ids:
                    _unmeasured(t, "this map's biome offers no native/non-native herbivore pair to compare")
                rows = _rows(t, health=True)
                nat, non = rows.get(ids["native"]), rows.get(ids["non"])
                if nat is None or non is None:
                    _unmeasured(t, "an animal of the pair is missing from list_pawns")
                if _hediff(non, HEDIFF) is None:
                    _unmeasured(t, "the non-native control animal was not exposed either (flesh/outdoors "
                                   "control failed), so a clean native proves nothing")
                if _hediff(nat, HEDIFF) is not None:
                    _fail("a native animal of the map biome (%s) gained %s; natives have lived in this "
                          "breath all their lives" % (nat.get("kindDef"), HEDIFF))
        with _comp(t, "bloom_toggle_off", toggle="ventBloomExposureEnabled"):
            if _live(t):
                t.bridge_call("jawa/pawn_health", pawn=ids["out"], action="remove", hediff=HEDIFF)
                if _hediff(_rows(t, health=True).get(ids["out"]), HEDIFF) is not None:
                    _unmeasured(t, "could not remove %s to start the OFF arm" % HEDIFF)
                with _setting(t, "ventBloomExposureEnabled", False):
                    _next_interval_jump(t)
                    t.wait_ticks(40)
                    row = _rows(t, health=True).get(ids["out"])
                if _hediff(row, HEDIFF) is not None:
                    _fail("ventBloomExposureEnabled OFF but the outdoor colonist gained %s" % HEDIFF)
        with _comp(t, "bloom_factor_scales", toggle="ventBloomExposureFactor"):
            if _live(t):
                if ids.get("sev1") is None:
                    _unmeasured(t, "no baseline severity at factor 1.0")
                with _setting(t, "ventBloomExposureFactor", 2.0):
                    _next_interval_jump(t)
                    t.wait_ticks(40)
                    h = _hediff(_rows(t, health=True).get(ids["out"]), HEDIFF)
                if h is None:
                    _fail("no %s at factor 2.0 after an exposure tick" % HEDIFF)
                ratio = h["severity"] / ids["sev1"]
                _note(t, "severity at factor 2.0 vs 1.0 (ratio)", [h["severity"], ids["sev1"], ratio])
                if not 1.7 <= ratio <= 2.3:
                    _fail("ventBloomExposureFactor 2.0 changed one exposure tick's severity by x%.2f, "
                          "expected ~x2 (%r vs %r)" % (ratio, h["severity"], ids["sev1"]))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the vexxiss and water

def _pond(t, x, z, size=8):
    t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,%d,%d" % (x, z, size, size), layer="top")


def _letters(t):
    r = t.bridge_call("jawa/letter_list")
    if not _live(t):
        return 0
    rows = _ok(r, "letter_list").get("letters")
    if not isinstance(rows, list):
        _fail("letter_list returned no letters list: %r" % r)
    return len([l for l in rows if LETTER_LABEL in str(l.get("label") or "")])


@suite.chain("water")
def water_chain(t):
    _prep(t, "water", 40)
    x, z = t.anchor
    ids = {}
    ponds = {"A": (x - 16, z - 4), "B": (x - 4, z - 4), "C": (x + 8, z - 4)}      # 8x8 each, on soil

    def wade(tag, ticks=300):
        """A fresh pond and a fresh vexxiss standing in its middle, then `ticks` of wading."""
        px, pz = ponds[tag]
        _pond(t, px, pz)
        ids[tag] = _spawn(t, VEXXISS, px + 4, pz + 4)
        t.wait_ticks(ticks)
        return _terrain(t, "%d,%d,8,8" % (px, pz))

    def body():
        with _comp(t, "water_site_ready", poison=True):
            if _live(t):
                ids["col"] = _spawn(t, "Colonist", x, z + 14, faction="player")
                for tag, (px, pz) in ponds.items():
                    _pond(t, px, pz)
                    base = _terrain(t, "%d,%d,8,8" % (px, pz))
                    if base.get("WaterShallow") != 64 or _toxic_cells(base):
                        _unmeasured(t, "pond %s did not read as 64 clean WaterShallow cells: %r" % (tag, base))
                if _letters(t) != 0:
                    _unmeasured(t, "a '%s' letter is already on the stack before the vexxiss wades" % LETTER_LABEL)
        with _comp(t, "water_poison_on", toggle="vexxissPoisonsWater"):
            if _live(t):
                after = wade("A")
                _note(t, "pond A terrain after 300 ticks of a vexxiss wading", after)
                if _toxic_cells(after) < 1:
                    _fail("a vexxiss stood in WaterShallow for 300 ticks and no cell turned to ToxicWater*: %r" % after)
                row = _rows(t).get(ids["A"])
                if row is None or row.get("dead"):
                    _unmeasured(t, "the wading vexxiss is gone, cannot attribute the poisoning")
        with _comp(t, "water_letter_arrives", toggle="vexxissWaterLetter"):
            if _live(t):
                if _toxic_cells(_terrain(t, "%d,%d,8,8" % ponds["A"])) < 1:
                    _unmeasured(t, "no poisoning happened (water_poison_on), so no letter can be owed")
                n = _letters(t)
                if n != 1:
                    _fail("expected exactly one '%s' letter after the first poisoning, read %d" % (LETTER_LABEL, n))
        with _comp(t, "water_letter_cooldown", toggle="vexxissWaterLetter"):
            if _live(t):
                row = _rows(t).get(ids["A"])
                if row is None or not _xz(row):
                    _unmeasured(t, "vexxiss A is gone, cannot re-lay water under it")
                vx, vz = _xz(row)
                around = "%d,%d,7,7" % (vx - 3, vz - 3)
                t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%s" % around, layer="top")
                t.wait_ticks(300)           # clean water UNDER the same vexxiss: it must poison again
                again = _terrain(t, around)
                if _toxic_cells(again) < 1:
                    _unmeasured(t, "the vexxiss did not poison the re-laid water, so the warn path was "
                                   "never reached a second time (%r)" % again)
                n = _letters(t)
                if n != 1:
                    _fail("a second poisoning within the same day raised a second letter (%d '%s' "
                          "letters): the per-animal day cooldown is not holding" % (n, LETTER_LABEL))
        with _comp(t, "water_letter_toggle_off", toggle="vexxissWaterLetter"):
            if _live(t):
                before = _letters(t)
                with _setting(t, "vexxissWaterLetter", False):
                    after = wade("B")
                if _toxic_cells(after) < 1:
                    _unmeasured(t, "vexxiss B poisoned no water, so the letter path was never reached: %r" % after)
                n = _letters(t)
                if n != before:
                    _fail("vexxissWaterLetter OFF but a new '%s' letter arrived (%d -> %d)" % (LETTER_LABEL, before, n))
        with _comp(t, "water_poison_toggle_off", toggle="vexxissPoisonsWater"):
            if _live(t):
                with _setting(t, "vexxissPoisonsWater", False):
                    after = wade("C")
                px, pz = ponds["C"]
                row = _rows(t).get(ids["C"])
                if row is None or row.get("dead") or not _xz(row):
                    _unmeasured(t, "vexxiss C is gone, cannot say it waded")
                vx, vz = _xz(row)
                if not (px - 1 <= vx <= px + 9 and pz - 1 <= vz <= pz + 9):
                    _unmeasured(t, "vexxiss C left its pond (%r), so it never waded" % ((vx, vz),))
                if _toxic_cells(after) != 0:
                    _fail("vexxissPoisonsWater OFF but %d cell(s) turned toxic: %r" % (_toxic_cells(after), after))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the vexxiss fire warden

@suite.chain("fire")
def fire_chain(t):
    _prep(t, "fire")
    t.expect("fire", lambda e: True)      # this chain lights its own fire on the wood (map_fire start): its own act
    x, z = t.anchor
    ids = {}
    fuel = "%d,%d,3,3" % (x + 2, z - 1)

    def seen_beatfire(pid, polls=14, step=50):
        """Poll site_state: did this pawn's job ever read BeatFire while a fire stood?"""
        seen, fires_seen = False, 0
        for _ in range(polls):
            t.wait_ticks(step)
            if _count(t, "Fire", "%d,%d,16,16" % (x - 4, z - 7)) > 0:
                fires_seen += 1
            if _jobs(t).get(pid) == "BeatFire":
                seen = True
                break
        return seen, fires_seen

    def light():
        t.bridge_call("jawa/spawn_batch",      # one op per cell: 'Def:x,z,count' (count = stack size)
                      ops=";".join("WoodLog:%d,%d,60" % (x + 2 + i, z - 1 + j) for i in range(3) for j in range(3)))
        r = t.bridge_call("jawa/map_fire", action="start", rect=fuel, fireSize=1.5)
        _ok(r, "map_fire")
        if not r.get("firesStarted"):
            _unmeasured(t, "map_fire started no fire on the wood (cells refused): %r" % r)

    def body():
        with _comp(t, "fire_warden_beats_fire", toggle="vexxissFireWardenEnabled"):
            if _live(t):
                ids["a"] = _spawn(t, VEXXISS, x - 6, z)
                _full(t, ids["a"])
                light()
                seen, fires_seen = seen_beatfire(ids["a"], polls=18)
                _note(t, "vexxiss job BeatFire seen / fire polls with a fire standing", [seen, fires_seen])
                if not fires_seen:
                    _unmeasured(t, "no Fire thing was standing during the window")
                if not seen:
                    _fail("a vexxiss 6 cells from a standing fire never took a BeatFire job in 900 ticks "
                          "(fire warden toggle is ON)")
        with _comp(t, "fire_warden_toggle_off", toggle="vexxissFireWardenEnabled"):
            if _live(t):
                t.bridge_call("jawa/map_fire", action="extinguish", rect="%d,%d,16,16" % (x - 4, z - 7))
                _kill_pawns_in(t, _rect(t, PAD_SIZE + 8))
                with _setting(t, "vexxissFireWardenEnabled", False):
                    ids["b"] = _spawn(t, VEXXISS, x - 6, z)
                    _full(t, ids["b"])
                    light()
                    seen, fires_seen = seen_beatfire(ids["b"], polls=18)
                _note(t, "OFF arm: BeatFire seen / fire polls", [seen, fires_seen])
                if not fires_seen:
                    _unmeasured(t, "no Fire thing was standing during the OFF window")
                if seen:
                    _fail("vexxissFireWardenEnabled OFF but the vexxiss still took a BeatFire job")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: vents

def _vent_read(t, vid):
    """(output multiplier, state word) from the vent's own inspect lines ('Vent output: 0.80x',
    'Vent state: recovering, 12%'). Unreadable lines are UNMEASURED, never a number."""
    _label, lines = _inspect(t, vid)
    if not _live(t):
        return None, None
    txt = " | ".join(str(l) for l in lines)
    m = re.search(r"Vent output:\s*([0-9.]+)x", txt)
    s = re.search(r"Vent state:\s*([a-z]+)", txt)
    if not m or not s:
        _unmeasured(t, "the vent's inspect lines carry no 'Vent output' / 'Vent state': %r" % lines)
    _STATE["vent_text"] = txt
    return float(m.group(1)), s.group(1)


def _transition_done(t):
    r = t.bridge_call("jawa/site_state")
    tr = (((r or {}).get("weather") or {}).get("transition"))
    if tr is None or float(tr) < 0.999:
        tr = _weather_transition_done(t)
    return tr


@suite.chain("vents")
def vents_chain(t):
    """CAULDRON_VENT_ENRICHMENT_HOOKS_1: the vent and what hangs on it. State reads only (inspect lines,
    hediff severities, the vexxiss's job); the falter's hush is a number, never a sound or a screenshot."""
    _prep(t, "vent")
    x, z = t.anchor
    ids = {}

    def kill_pawns():
        _kill_pawns_in(t, _rect(t, PAD_SIZE + 8))

    def vent():
        return _vent_read(t, ids["vent"])

    def exposure_reading():
        near = _spawn(t, "Colonist", x + 4, z, faction="player")
        far = _spawn(t, "Colonist", x + 15, z + 15, faction="player")
        for p in (near, far):
            t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
        _next_interval_jump(t)
        t.wait_ticks(40)
        rows = _rows(t, health=True)
        sev = []
        for p in (near, far):
            h = _hediff(rows.get(p), HEDIFF)
            sev.append(float((h or {}).get("severity") or 0))
        kill_pawns()
        return sev

    def took_job(pid, polls=12):
        for _ in range(polls):
            t.wait_ticks(150)
            if _jobs(t).get(pid) == DRINK_JOB:
                return True
        return False

    def body():
        with _comp(t, "vents_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_ScatterDusk")
                _ok(t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,1" % (VENT, x, z)), "spawn_batch(vent)")
                rows = _things(t, VENT, _rs(_rect(t)))
                if not rows:
                    _unmeasured(t, "the spawned %s is not on the map (spawn_batch refused a 2x2 natural building?)" % VENT)
                ids["vent"] = rows[0]["id"]
                out, st = vent()
                _note(t, "fresh vent output / state", [out, st])
        with _comp(t, "vent_weather_multiplier", toggle="ventWeatherEnabled"):
            if _live(t):
                o0, _s = vent()
                if not 0.95 <= o0 <= 1.05:
                    _fail("a vent under scatter-dusk reads output %.2fx, expected 1.00x" % o0)
                _lock_weather(t, "RM_VapourBank")
                t.wait_ticks(60)
                o1, _s = vent()
                _note(t, "vent output scatter-dusk / vapour bank", [o0, o1])
                if not 0.7 <= o1 <= 0.9:
                    _fail("a vent under vapour bank reads output %.2fx, expected 0.80x" % o1)
                with _setting(t, "ventWeatherEnabled", False):
                    o2, _s = vent()
                if abs(o2 - 1.0) > 0.05:
                    _fail("ventWeatherEnabled OFF but the vent still follows the weather (%.2fx under vapour bank)" % o2)
        with _comp(t, "vent_falter_precedes_bloom"):
            if _live(t):
                _lock_weather(t, BLOOM)
                t.wait_ticks(120)
                o1, s1 = vent()
                _note(t, "vent output / state just after the bloom is chosen", [o1, s1])
                if s1 != "faltering" or o1 > 0.2:
                    _fail("the weather turned to %s but the vent is not hushed (state %r, output %.2fx)" % (BLOOM, s1, o1))
                tr = _transition_done(t)
                if tr is None or float(tr) < 0.999:
                    _unmeasured(t, "the bloom transition did not finish (factor %r)" % tr)
                o2, s2 = vent()
                _note(t, "vent output / state once the bloom has arrived", [o2, s2])
                if s2 == "faltering" or not 2.2 <= o2 <= 2.8:
                    _fail("the bloom has arrived but the vent reads %r at %.2fx (expected raised output, ~2.5x)" % (s2, o2))
        with _comp(t, "vent_exposure_is_local", toggle="ventLocalExposureEnabled"):
            if _live(t):
                _lock_weather(t, BLOOM)
                tr = _transition_done(t)
                if tr is None or float(tr) < 0.999:
                    _unmeasured(t, "the bloom is not at full strength (factor %r): no exposure tick will run" % tr)
                near, far = exposure_reading()
                _note(t, "metal load next to the vent / 21 cells away", [near, far])
                if near <= 0 or far <= 0:
                    _unmeasured(t, "an exposed colonist took no load at all (near %r, far %r): the tick may not have run" % (near, far))
                if near < far * 1.2:
                    _fail("metal load %.4f beside the vent vs %.4f far from it: the bloom is not strongest near vents" % (near, far))
                with _setting(t, "ventLocalExposureEnabled", False):
                    near2, far2 = exposure_reading()
                _note(t, "OFF arm: near / far", [near2, far2])
                if near2 <= 0 or far2 <= 0:
                    _unmeasured(t, "OFF arm: an exposed colonist took no load (%r, %r)" % (near2, far2))
                if abs(near2 - far2) > 0.1 * max(near2, far2):
                    _fail("ventLocalExposureEnabled OFF but near %.4f vs far %.4f still differ" % (near2, far2))
        with _comp(t, "vexxiss_drinks_vent", toggle="vexxissDrinksVentsEnabled"):
            if _live(t):
                _lock_weather(t, "RM_ScatterDusk")
                t.wait_ticks(60)
                ids["v1"] = _spawn(t, VEXXISS, x + 9, z)
                _full(t, ids["v1"])
                seen = took_job(ids["v1"])
                _note(t, "wild vexxiss took %s" % DRINK_JOB, seen)
                if not seen:
                    _fail("a wild vexxiss 9 cells from a breathing vent never took %s in 1800 ticks (toggle ON)" % DRINK_JOB)
                t.wait_ticks(300)
                _o, st = vent()
                if "drunk" not in _STATE.get("vent_text", "") and st != "silenced":
                    _fail("the vexxiss drank but the vent shows no suppression: %r" % _STATE.get("vent_text"))
                kill_pawns()
                with _setting(t, "vexxissDrinksVentsEnabled", False):
                    ids["v2"] = _spawn(t, VEXXISS, x + 9, z)
                    _full(t, ids["v2"])
                    seen_off = took_job(ids["v2"])
                    kill_pawns()
                _note(t, "OFF arm: took the drink job", seen_off)
                if seen_off:
                    _fail("vexxissDrinksVentsEnabled OFF but a vexxiss still took %s" % DRINK_JOB)
        with _comp(t, "vent_silences_and_recovers"):
            if _live(t):
                with _setting(t, "ventSilenceDays", 0.05):          # 3000 ticks of silence
                    pid = _spawn(t, VEXXISS, x + 9, z)
                    silenced = False
                    for _ in range(45):
                        _wait(t, 1000)
                        _full(t, pid)
                        o, st = vent()
                        if st == "silenced":
                            silenced = True
                            break
                    _note(t, "vent silenced by a drinking vexxiss", [silenced, o, st])
                    if not silenced:
                        _fail("a wild vexxiss drank for 45000 ticks and the vent never fell silent")
                    if o > 0.01:
                        _fail("a silenced vent still reads output %.2fx" % o)
                    kill_pawns()                                    # stop it drinking the recovery back down
                recovering = None
                for _ in range(10):
                    _wait(t, 1000)
                    o, st = vent()
                    if st == "recovering":
                        recovering = o
                        break
                if recovering is None:
                    _fail("the silenced vent never began to recover within 10000 ticks (last %r at %.2fx)" % (st, o))
                _wait(t, 3000)
                o_b, st_b = vent()
                _note(t, "recovery output first / 3000 ticks later", [recovering, o_b])
                if not (0 < o_b < 0.9) or o_b <= recovering:
                    _fail("the vent is not visibly recovering: %.3fx then %.3fx" % (recovering, o_b))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the log (last)

@suite.chain("log")
def log_chain(t):
    _pad(t, "spawn")
    with _comp(t, "log_clean"):
        if _live(t):
            buf = t.bridge_call("jawa/drain_log", limit=1)
            if not (buf or {}).get("totalInBuffer"):
                _unmeasured(t, "drain_log buffer is empty: cannot see the log at all")
            owned = set(n for ns in DEFS_BY_TYPE.values() for n in ns)
            bad = []
            for needle in ("Cauldron", "Config error", "cross-reference"):
                r = t.bridge_call("jawa/drain_log", contains=needle, errorsOnly=True, limit=100)
                for m in ((_ok(r, "drain_log(%s)" % needle)).get("messages") or []):
                    text = m.get("text") or ""
                    if text.startswith("Tried to destroy non-destroyable thing"):
                        # the vents are indestructible on purpose (destroyable false, like a geyser) and this suite's own
                        # pad clean-up (destroy_batch over the vents chain's rect) asks the engine to destroy them, which
                        # logs this. The harness caused it; not a defect in the mod (LIVE 2026-10-03, both runs).
                        continue
                    if needle == "Cauldron" or any(d in text for d in owned):
                        bad.append(text)
            _note(t, "log scan", {"errors naming the mod or one of its defs": len(bad),
                                  "bufferLines": buf.get("totalInBuffer")})
            if bad:
                _fail("log carries errors: %s" % [str(x)[:160] for x in bad[:4]])
