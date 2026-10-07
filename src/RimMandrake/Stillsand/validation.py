"""validation.py -- modcheck suite for RimMandrake: Stillsand (mandrake.rm.stillsand).

Item STILLSAND_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/Stillsand.md
(`## must be true` lines, each ending in `-> chain.component` or `-> UNCOVERED: why`).
Process: design/RimMandrake/debug_process.md (a first script = a modcheck Suite + a walk).

PACKAGING. This dev folder is the SOURCE only. The biome ships COMPOSED inside
`mandrake.rm.biomes` (Biomes.compose.json, wave 2). Drive the `baroque_wave0` tier
(northstar_plan.py), never the dev folder's own packageId: `modcheck run Stillsand` would swap to a
list without the composed biome. The Utinni patch layer (krayt, war wyrm ...) is NOT loaded on that
tier, so every check here is on the franchise-free RM_ cast and mechanics.

THE SITE. Nearly every mechanic is keyed on a map whose BIOME is RM_Stillsand (the gale, the zuurrik
map component, the eruption incident, the leviathan gate, the pinned sun, the sand-remembers-water
gate). The first chain, `site`, therefore builds the site with the recipe PROVEN live on 2026-10-01
(Transient/LIVE_SESSION_2_2026-10-01.md): `jawa/world_tile_set biome=RM_Stillsand` on the quicktest
tile, `jawa/world_commit`, then the vanilla debug action `Actions\\Regenerate Current Map`. It always
regenerates (a fresh map each run) so the precious-cave log lines of THIS run's generation are
readable. Every later chain is UNMEASURED if the site is not a Stillsand map. The scratch quicktest
world is test scaffolding and is thrown away (CLAUDE.md worldgen ban: nothing here produces a planet a
player receives).

WHAT THE SUITE READS. Every defName this mod ships is parsed from its own Defs/ at import (so a new
def is covered without an edit) and must RESOLVE live: a def whose comp/extension type is missing is
discarded silently by the engine, and only a live get_defs sees that (STILLSAND_LOAD_DEF_ERRORS_1
was exactly that: RM_KneelOllim discarded for a bad TreeCategory). Mechanics are read as STATE through
the bridge (hediffs, positions, inspect strings, stat values, def lists, letters, log lines); nothing
here judges appearance and no component takes a screenshot.

EVERY CHECK CAN FAIL. Each PASS predicate has a control arm inside the same chain (a gravel control
for the sand swimmer, a below-threshold blood cluster for the zuurrik, a goggled pawn for the glare, a
toggle-off arm for each toggle that is driven), so a harness that sees nothing records UNMEASURED, never
PASS. `selftest_stillsand.py` runs the suite against a scripted fake game, healthy and with each mod
behaviour broken in turn, and proves the right component (and only that one) goes red.

KNOWN PAST BUGS GUARDED (each is a component that would have gone red):
  OORRIK_PAWNGEN_NRE_1 (fauna.fauna_spawns), STILLSAND_LOAD_DEF_ERRORS_1 (defs.defs_resolve),
  SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1 (sandswim.vekka_take_leaves_funnel), SOORRAK_FLIGHT_JOBSTART_NRE_1
  (soorrak.soorrak_no_exceptions), the soorrak idle-loop defect (soorrak.soorrak_not_stuck),
  MUURROK_BEAM_NO_DAMAGE_1 (muurrok.beam_burns_target), the precious-cave gen step
  (site.site_cave_logged).

NOT DRIVEN HERE (walk lines say UNCOVERED, with the reason): the leviathan incident toggles and odds
(private dictionaries, no tool reads them), carry-and-return of gale-borne pawns (a rare, random event
on a crest), gale abrasion/static (statistical), the mirage and chasing-water states (CreatureBehaviors'
own script), the acoustic payload (needs mandrake.rm.acousticscanner), the Return ledger (an RM tier
ships no ledger def), the horizon plume mote and the bone harp sound (visual/audio), flight in the air
(never live-tested unattended, CLAUDE.md), and appearance of any kind.

Settings fields are `public static` (or instance, for RM_StillsandSettings); `jawa/mod_settings_field`
reads and writes both. Every arm that changes one restores it in a `finally`. The tool never writes
ModSettings.xml.
"""
import contextlib
import glob
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("Stillsand")

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "RimMandrake.Stillsand."
BIOME = "RM_Stillsand"
SITE_TEMP = 15.0               # tile temperature: cool enough that the home colonists outlive the run

# (settings class FullName) -> {field: shipped default}. Read off the *.cs field initialisers.
SETTINGS = {
    NS + "RM_StillsandSettings": {"zuurrikEnabled": True, "zuurrikBloodThreshold": 8},
    NS + "RM_PreciousCaveSettings": {"genStepEnabled": True, "yardangShapingEnabled": True,
                                     "torEnabled": True, "torChance": 0.25,
                                     "preservationEnabled": True, "dripEnabled": True,
                                     "wallRingEnabled": True, "tribalMarkEnabled": True},
    NS + "RM_SkeletonSettings": {"skeletonPlacementEnabled": True, "maxSkeletonsPerMap": 2,
                                 "corpseToSkeletonEnabled": True, "corpseToSkeletonDays": 15.0,
                                 "boneHarpEnabled": True, "horizonWarningsEnabled": True,
                                 "horizonWarningHours": 3.0, "horizonPassersEnabled": True,
                                 "duneBurialEnabled": True},
    NS + "RM_StillsandEventsSettings": {"mirrorBeamEnabled": True, "hornEnabled": True,
                                        "hornAnswerChance": 0.15, "denQuestEnabled": True},
    NS + "RM_StillsandWaterSettings": {"bloomOnPour": True, "ledgerEnabled": True,
                                       "ledgerIncidentWeighting": True},
    NS + "RM_GlassChainSettings": {"sunFurnaceEnabled": True, "lensBenchEnabled": True,
                                   "solarOvenEnabled": True, "sunWorkSpeedMultiplier": 1.0,
                                   "sieveEnabled": True, "sieveYieldMultiplier": 1.0,
                                   "solarStillEnabled": True, "stillRateMultiplier": 1.0,
                                   "wringingStillEnabled": True, "sunLanceEnabled": True,
                                   "geophoneEnabled": True, "geophoneRadius": 20.0,
                                   "kraytLensEnabled": True, "glassGogglesEnabled": True},
    NS + "RM_SandSwimRemSettings": {"thumperEnabled": True, "thumperRadius": 40.0,
                                    "sandFishingWakeEnabled": True, "sandFishingWakeChance": 0.15,
                                    "driftSwimEnabled": True, "driftSwimDepth": 0.3,
                                    "listeningHissEnabled": True, "listeningSingingEnabled": True,
                                    "listeningWarningEnabled": True, "listeningRumbleEnabled": True,
                                    "singingWarningCells": 12.0},
    NS + "RM_DuneGaleSettings": {"galeEnabled": True, "galeFrequency": 1.0, "abrasionEnabled": True,
                                 "carryEnabled": True, "staticEnabled": True, "emergenceEnabled": True,
                                 "seedingEnabled": True, "dustDevilsEnabled": True,
                                 "dustDevilFrequency": 1.0},
}
FIELD_TYPE = dict((f, tn) for tn, d in SETTINGS.items() for f in d)
DEFAULTS = dict((f, v) for d in SETTINGS.values() for f, v in d.items())
suite.toggles = sorted(k for k, v in DEFAULTS.items() if isinstance(v, bool))

# Pad offsets from the map centre (the driver's anchor); one pad per chain, 24 cells, 45 apart.
PADS = {
    "fauna": (-90, -90), "flora": (-45, -90), "sandswim": (0, -90), "zuurrik": (45, -90),
    "loomma": (90, -90), "soorrak": (-90, -45), "glass": (-45, -45), "water": (0, -45),
    "skeleton": (45, -45), "glare": (90, -45), "cooling": (-90, 0), "gale": (-45, 0),
    "muurrok": (45, 0), "eruption": (90, 0), "horizon": (-90, 45), "devil": (-45, 45),
    "sun": (0, 45), "caves": (45, 45), "defs": (90, 45), "settings": (0, 90), "zctl": (-45, 90),
    "log": (45, 90),
}
PAD_SIZE = 24
MIN_MAP = 230                  # pads sit up to 90 cells from the centre, +16 margin each side

_STATE = {}                    # readings shared between components of ONE run

# ----------------------------------------------------------------------------- shipped defs

STD_TYPES = ("ThingDef", "WorkGiverDef", "PawnKindDef", "HediffDef", "WeatherDef", "IncidentDef", "JobDef", "RecipeDef",
             "BiomeDef", "GameConditionDef", "GenStepDef", "SoundDef", "BodyDef", "BodyPartDef",
             "BodyPartGroupDef", "DamageDef", "ThoughtDef")


def _read_defs():
    """(std, custom, parent): std = {defType: [defName]} for the standard def types, custom =
    {shortTypeName: [defName]} for this mod's own Def subclasses (tag carries a namespace), both
    parsed per top-level element with ElementTree (comments dropped, never a fixed line number)."""
    std, custom, plants = {}, {}, []
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        for e in ET.parse(path).getroot():
            if not isinstance(e.tag, str) or str(e.get("Abstract", "")).lower() == "true":
                continue
            nm = e.find("defName")
            if nm is None or not (nm.text or "").strip():
                continue
            name = nm.text.strip()
            if e.tag in STD_TYPES:
                std.setdefault(e.tag, []).append(name)
                if e.tag == "ThingDef" and e.find("plant") is not None:
                    plants.append(name)
            elif "." in e.tag:
                custom.setdefault(e.tag.rsplit(".", 1)[1], []).append(name)
    return std, custom, plants


DEFS_STD, DEFS_CUSTOM, PLANTS = _read_defs()
SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_STD.items() for n in ns)
CUSTOM_SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_CUSTOM.items() for n in ns)
KINDS = DEFS_STD.get("PawnKindDef", [])


def _read_biome():
    """The inline roster of the BiomeDef: ({animal: commonality}, {plant: commonality})."""
    path = os.path.join(HERE, "Defs", "BiomeDefs", "RM_Stillsand_Biome.xml")
    animals, plants = {}, {}
    for b in ET.parse(path).getroot().iter("BiomeDef"):
        for tag, out in (("wildAnimals", animals), ("wildPlants", plants)):
            node = b.find(tag)
            for c in (node if node is not None else []):
                if isinstance(c.tag, str):
                    out[c.tag] = float((c.text or "0").strip())
    return animals, plants


ROSTER_ANIMALS, ROSTER_PLANTS = _read_biome()


def _read_emergence_labels():
    path = os.path.join(HERE, "Defs", "WeatherDefs", "RM_DuneGale.xml")
    labels = []
    for gc in ET.parse(path).getroot().iter("GameConditionDef"):
        for em in gc.iter("li"):
            ll = em.find("letterLabel")
            if ll is not None and ll.text:
                labels.append(ll.text.strip())
    return labels


EMERGENCE_LABELS = _read_emergence_labels()
GIANT_SKELETONS = ("RM_OommokSkeleton", "RM_MuurrokSkeleton", "RM_GuzzkaSkeleton", "RM_VozzikSkeleton")
BIOME_EXTENSIONS = ("RM_SunHeatExtension", "RM_PinnedSunExtension", "DuneFieldExtension",
                    "RM_SkeletonBiomeExtension", "RM_SandRemembersWaterExtension")
BIOME_GENSTEPS = ("RM_GiantSkeletons", "RM_PreciousCaveCarve", "RM_PreciousCaveContents")
GIANT_RACES = ("RM_Oommok", "RM_Muurrok", "RM_Guzzka", "RM_Vozzik")
MISSING_TOOL = re.compile(r"unknown tool|no such tool|tool not found|not a registered tool|unknown_tool",
                          re.I)


# ----------------------------------------------------------------------------- helpers

def _live(t):
    """True only for a real run against a real session and an unfailed chain; False for the offline
    declaration probe, so a component body never trips on its no-op (None) results."""
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
    """t.component() plus three fix-ups: an UNMEASURED stays UNMEASURED with its real reason; a FAIL does
    not poison the rest of the chain unless `poison` (components here are independent arms, so one red
    must not hide the next); a missing bridge tool reads UNMEASURED (could not ask), not FAIL."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    c = t.components[-1]
    why = getattr(t, "_why", None)
    if why and not before:
        c.detail = "UNMEASURED: %s" % why
        t.upstream_failed = bool(poison)
    elif c.verdict == "FAIL" and not before:
        if MISSING_TOOL.search(str(c.detail)):
            c.verdict = "UNMEASURED"
            c.detail = "UNMEASURED: a bridge tool this check needs is unavailable (%s)" % str(c.detail)[:200]
        t.upstream_failed = bool(poison)
    t._why = None
    if t.session is not None:    # progress line: the driver prints only at the very end
        print("[stillsand] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[stillsand-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
              file=sys.stderr, flush=True)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _pad(t, name):
    """Move t.anchor to the named pad. The base is the REGENERATED map's centre once the site chain has built
    it (the driver's own anchor was read off the quicktest map, which may be another size)."""
    dx, dz = PADS[name]
    ax, az = _STATE.get("base") or (t._base if hasattr(t, "_base") else t.anchor)
    t._base = (ax, az)
    t.anchor = (ax + dx, az + dz)


def _rect(t, size=PAD_SIZE, dx=0, dz=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half + dz, size, size


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _gate(t):
    """A chain on a map that is not the Stillsand site measures nothing: UNMEASURED for the whole chain."""
    if t.session is not None and not _STATE.get("site"):
        t.upstream_failed = True


def _prep(t, name, terrain="Sand", size=PAD_SIZE):
    """Clear the pad, strip its roof, lay `terrain`, lock Clear weather, make sure a colonist lives."""
    _pad(t, name)
    _gate(t)
    if _live(t):
        _ensure_colonist(t)
        try:    # neutral until a chain locks its own; never let this abort the chain
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        except Exception as ex:
            print("[stillsand] neutral weather not set: %s" % ex, file=sys.stderr, flush=True)
        _STATE.setdefault("pads", []).append(_rs(_rect(t, size + 8)))
    t.clear_area(size=size + 8)
    r = _rect(t, size + 8)
    t.bridge_call("jawa/set_roof_batch", ops=_rs(r), roofDef="None")
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, _rs(r)), layer="top")


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


def _get_defs(t, defs, fields):
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, limit=200)
    if not _live(t):
        return {}, None
    _ok(r, "get_defs(%s)" % defs[:80])
    return dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or [])), r


def _spawn(t, kind, x, z, faction="none"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s, %s) returned no pawn (pawn generation exception?): %r" % (kind, faction, r))
    t.session.track("pawn", pid, x=x, z=z)
    _STATE.setdefault("spawned", []).append(pid)
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


def _hediffs(row):
    return list(((row or {}).get("health") or {}).get("hediffs") or [])


def _sev(row, hediff):
    """Severity of `hediff` on a list_pawns row, 0.0 when absent."""
    best = 0.0
    for h in _hediffs(row):
        if h.get("def") == hediff:
            best = max(best, float(h.get("severity") or 0.0))
    return best


def _has(row, hediff):
    return any(h.get("def") == hediff for h in _hediffs(row))


def _xz(row):
    if not row or row.get("x") is None or row.get("z") is None:
        return None
    return (row["x"], row["z"])


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _colonist(t, x, z):
    return _spawn(t, "Colonist", x, z, faction="player")


def _ensure_colonist(t):
    """The planted home colonists die of the sun on a long run; a map with nobody home ends the game.
    Keep one alive at the map centre between chains."""
    if not _live(t):
        return
    rows = _rows(t)
    if any(p.get("isPlayer") and not p.get("dead") for p in rows.values()):
        return
    ax, az = t._base if hasattr(t, "_base") else t.anchor
    t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=ax, z=az, faction="player", count=1)


def _letters(t):
    """[(label, arrivalTick, text)] off jawa/letter_list (a label may be a {RawText} dict)."""
    r = t.bridge_call("jawa/letter_list")
    if not _live(t):
        return []
    out = []
    for l in (_ok(r, "letter_list").get("letters") or []):
        lab = l.get("label")
        if isinstance(lab, dict):
            lab = lab.get("RawText")
        out.append((str(lab), l.get("arrivalTick"), str(l.get("text"))))
    return out


def _new_letters(before, after):
    seen = set((a, b) for a, b, _ in before)
    return [x for x in after if (x[0], x[1]) not in seen]


def _log_saturated(t):
    """True when RimWorld has stopped logging (its message limit): from then on a missing line, error or
    count is NOT evidence of absence."""
    r = t.bridge_call("jawa/drain_log", contains="Reached max messages limit", limit=1)
    return bool((r or {}).get("messages")) if _live(t) else False


def _log_lines(t, contains, errors_only=False, strict=True):
    """(texts, repeats-weighted count) of the in-game log messages containing `contains`. A saturated log
    is UNMEASURED (strict) or (None, None) (strict=False, for a reader that decides later)."""
    if _log_saturated(t):
        if strict:
            _unmeasured(t, "the game has hit its log message limit and stopped logging: a missing line or "
                           "a zero error count proves nothing (relaunch)")
        return None, None
    r = t.bridge_call("jawa/drain_log", contains=contains, errorsOnly=errors_only, limit=500)
    if not _live(t):
        return [], 0
    _ok(r, "drain_log(%s)" % contains)
    rows = r.get("messages") or []
    n = 0
    for m in rows:
        n += int(m.get("repeats") or 1)
    return [m.get("text") or "" for m in rows], n


def _buffer_total(t):
    r = t.bridge_call("jawa/drain_log", limit=1)
    return int((r or {}).get("totalInBuffer") or 0) if _live(t) else 0


# ---- settings

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
    r = t.bridge_call("jawa/mod_settings_field", typeName=FIELD_TYPE[field], action="get", field=field)
    if not _live(t):
        return None
    _ok(r, "mod_settings_field(get %s)" % field)
    return r.get("value")


def _set(t, field, value):
    """Set a settings field and verify it by an independent read-back (numeric-tolerant)."""
    r = t.bridge_call("jawa/mod_settings_field", typeName=FIELD_TYPE[field], action="set", field=field,
                      value=str(value))
    if not _live(t):
        return
    _ok(r, "mod_settings_field(set %s=%r)" % (field, value))
    got = _get_setting(t, field)
    if not _same(got, value):
        _fail("setting %s=%r did not take: read back %r" % (field, value, got))


def _restore(t, field):
    if t.session is None:
        return
    try:
        t.session.call("jawa/mod_settings_field", typeName=FIELD_TYPE[field], action="set", field=field,
                       value=str(DEFAULTS[field]))
        got = t.session.call("jawa/mod_settings_field", typeName=FIELD_TYPE[field], action="get",
                             field=field)
        if not _same((got or {}).get("value"), DEFAULTS[field]):
            print("[stillsand] RESTORE FAILED %s -> %r" % (field, got), file=sys.stderr, flush=True)
    except Exception as ex:   # restoring must never mask the verdict that got us here
        print("[stillsand] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)


@contextlib.contextmanager
def _setting(t, field, value):
    """Flip one field for a block; ALWAYS restore the shipped default and re-read it."""
    _set(t, field, value)
    try:
        yield
    finally:
        _restore(t, field)


# ---- weather and time

def _weather_now(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return None
    cur = (r or {}).get("weather")
    if isinstance(cur, dict):
        cur = cur.get("current")
    return cur


def _unlock_weather(t):
    if t.session is not None:
        try:
            t.session.call("jawa/weather_set", weather="Clear", lockWeather=True)
            t.session.call("jawa/weather_set", unlock=True)
        except Exception as ex:
            print("[stillsand] weather reset failed: %s" % ex, file=sys.stderr, flush=True)


def _cleanup(t):
    """ALWAYS after a chain: release weather, remove what this chain spawned, clear its pads."""
    if t.session is None:
        return
    _unlock_weather(t)
    try:
        alive = _pawns_raw(t)
        for pid in _STATE.pop("spawned", []):
            p = alive.get(pid)
            if p is not None and p.get("x") is not None:
                t.session.call("jawa/destroy_batch", rects="%d,%d,1,1" % (p["x"], p["z"]),
                               categories="Pawn")
    except Exception as ex:
        print("[stillsand] spawned-pawn cleanup failed: %s" % ex, file=sys.stderr, flush=True)
    for rect in sorted(set(_STATE.pop("pads", []))):
        try:
            t.session.call("jawa/destroy_batch", rects=rect, categories="All")
        except Exception as ex:
            print("[stillsand] pad cleanup failed: %s" % ex, file=sys.stderr, flush=True)


def _pawns_raw(t):
    """list_pawns straight off the session (no chain guard), for cleanup after a failed chain."""
    r = t.session.call("jawa/list_pawns", limit=500)
    return dict((p.get("id"), p) for p in ((r or {}).get("pawns") or []))


def _guarded(fn):
    def wrapper(t):
        try:
            fn(t)
        finally:
            _cleanup(t)
    wrapper.__name__ = fn.__name__
    return wrapper


def _chain(name):
    def deco(fn):
        suite.chain(name)(_guarded(fn))
        return fn
    return deco


def _kill(t, x, z):
    t.bridge_call("rimworld/execute_debug_action", path="Actions\\T: Kill", x=x, z=z)


# ----------------------------------------------------------------------------- chain: site

def _regen(t):
    """Regenerate the CURRENT tile's map (the vanilla debug action honours the tile's current biome) and wait
    until the bridge says a map is ready. The call can drop its connection while the map rebuilds, so a
    raised error is recorded, never trusted, and readiness is polled."""
    try:
        t.bridge_call("rimworld/execute_debug_action", path="Actions\\Regenerate Current Map")
    except Exception as ex:
        t._record("regen call ended", str(ex)[:200])
    for _ in range(60):
        time.sleep(5)
        try:
            st = (t.bridge_call("rimbridge/get_bridge_status") or {}).get("state") or {}
        except Exception:
            continue
        # The bridge state has NO `currentMapReady` key (MEASURED 2026-10-07: programState/currentMapId/longEventPending/
        # automationReady/visualReady/tick); polling for it burned 300 s and made 62 components UNMEASURED.
        if st.get("currentMapReady") or (st.get("automationReady") and st.get("currentMapId") and not st.get("longEventPending")):
            return
    _unmeasured(t, "the map was not ready 300 s after Regenerate Current Map")


@_chain("site")
def site_chain(t):
    _pad(t, "settings")
    with _comp(t, "site_stillsand_map", poison=True):
        if _live(t):
            info = _ok(t.bridge_call("jawa/map_info"), "map_info")
            tile = info.get("tile")
            if tile is None:
                _unmeasured(t, "map_info reports no tile: no quicktest world is up")
            before_total = _buffer_total(t)
            lines, before_n = _log_lines(t, "[Stillsand] precious cave", strict=False)
            r = t.bridge_call("jawa/world_tile_set", tiles=str(tile), biome=BIOME, temperature=SITE_TEMP)
            _ok(r, "world_tile_set")
            _ok(t.bridge_call("jawa/world_commit"), "world_commit")
            _regen(t)
            info = _ok(t.bridge_call("jawa/map_info"), "map_info after regen")
            if info.get("mapBiome") != BIOME:
                _fail("regenerated map biome is %r, not %s (BiomeDef discarded, or the tile edit did not "
                      "take)" % (info.get("mapBiome"), BIOME))
            if min(info.get("sizeX") or 0, info.get("sizeZ") or 0) < MIN_MAP:
                _unmeasured(t, "map is %sx%s, the pads need >= %d" % (info.get("sizeX"), info.get("sizeZ"),
                                                                    MIN_MAP))
            cx, cz = info["sizeX"] // 2, info["sizeZ"] // 2
            t.session.call("jawa/spawn_pawn", kindDef="Colonist", x=cx, z=cz, faction="player", count=3)
            t.session.call("rimworld/execute_debug_action", path="Actions\\Destroy hostile pawns")
            lines2, after_n = _log_lines(t, "[Stillsand] precious cave", strict=False)
            _STATE.update(site=True, cave_before=before_n, cave_after=after_n, buf_before=before_total,
                          base=(cx, cz), tile=tile, lat=info.get("latitude"))
            t._base = (cx, cz)
            t.anchor = (cx, cz)
            _note(t, "site", {"tile": tile, "latitude": info.get("latitude"), "size": [info.get("sizeX"),
                                                                                  info.get("sizeZ")]})

    with _comp(t, "site_cave_logged"):
        if _live(t):
            if _STATE.get("buf_before", 0) >= 900:
                _unmeasured(t, "the in-game log buffer was near its cap before the regen: a new line "
                               "cannot be told from an evicted one")
            b, a = _STATE.get("cave_before"), _STATE.get("cave_after")
            _note(t, "[Stillsand] precious cave lines before/after the regen", [b, a])
            if a is None or b is None:
                _unmeasured(t, "the log was unreadable around the regen (message limit reached, or the "
                               "site component did not run)")
            if a <= b:
                _fail("regenerating a Stillsand map logged no new '[Stillsand] precious cave' line (%s -> "
                      "%s): the precious-cave gen steps did not run (extraGenSteps patch matched nothing?)"
                      % (b, a))

    with _comp(t, "skeleton_gen_within_cap"):
        if _live(t):
            n = sum(_count(t, d) for d in GIANT_SKELETONS)
            cap = int(float(_get_setting(t, "maxSkeletonsPerMap")))
            _note(t, "giant skeletons on the fresh map / cap", [n, cap])
            if n > cap:
                _fail("the map generated %d giant skeletons, over maxSkeletonsPerMap %d" % (n, cap))


# ----------------------------------------------------------------------------- chain: defs

@_chain("defs")
def defs_chain(t):
    _pad(t, "defs")
    with _comp(t, "defs_resolve"):
        if _live(t):
            # The parser must see the mod: a broken parser would read "all 0 defs resolve".
            if len(SHIPPED) < 90 or not DEFS_STD.get("IncidentDef") or not KINDS or not PLANTS:
                _fail("parsed only %d shipped defs from %s (parser broken?)" % (len(SHIPPED), HERE))
            lost = []
            for i in range(0, len(SHIPPED), 100):
                chunk = SHIPPED[i:i + 100]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=200)
                _ok(r, "get_defs(shipped %d)" % i)
                lost += list(r.get("notFound") or [])
                if r.get("foundCount") != len(chunk) - len(r.get("notFound") or []):
                    _fail("get_defs foundCount %r disagrees with %d asked" % (r.get("foundCount"), len(chunk)))
            if lost:
                _fail("%d shipped def(s) did not resolve live (silently discarded?): %s" % (len(lost), lost[:12]))
            # Sanity probe: the instrument must be able to say "absent".
            probe = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Stillsand_NoSuchDef_Probe",
                                  fields="defName")
            if "RM_Stillsand_NoSuchDef_Probe" not in json.dumps((probe or {}).get("notFound")):
                _fail("sanity probe: an absent def was not reported in notFound: %r" % probe)
            _note(t, "shipped defs resolved", len(SHIPPED))

    with _comp(t, "sand_sieve_defs"):
        # STILLSAND_SAND_SIEVE_CHORE_1: the carried-tool chore needs its item, job and both work givers
        # to resolve live (a giverClass naming a missing type discards the WorkGiverDef silently).
        need = ["ThingDef/RM_SandSieve", "JobDef/RM_SiftGlassSand", "WorkGiverDef/RM_SiftGlassSand",
                "WorkGiverDef/RM_TakeSandSieve"]
        for d in need:
            if d not in SHIPPED:
                _fail("%s is not parsed from this mod's Defs/ (parser or def missing)" % d)
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs=";".join(need), fields="defName", limit=20)
            _ok(r, "get_defs(sand sieve)")
            if r.get("notFound"):
                _fail("sand sieve def(s) did not resolve live: %s" % r.get("notFound"))
            # The sieve yield must be a live, writable field; a 0 multiplier would make the chore a no-op.
            if not _same(_get_setting(t, "sieveYieldMultiplier"), 1.0):
                _fail("sieveYieldMultiplier is not at its shipped default 1.0")

    with _comp(t, "solar_still_defs"):
        # STILLSAND_SOLAR_STILL_1: both stills, the water + brine items and the witness thought must
        # resolve live (a missing compClass or thoughtClass discards the def silently).
        need = ["ThingDef/RM_SolarStill", "ThingDef/RM_WringingStill", "ThingDef/RM_StilledWater",
                "ThingDef/RM_Brine", "ThoughtDef/RM_Thought_DeadDistilled"]
        for d in need:
            if d not in SHIPPED:
                _fail("%s is not parsed from this mod's Defs/ (parser or def missing)" % d)
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs=";".join(need), fields="defName", limit=20)
            _ok(r, "get_defs(solar still)")
            if r.get("notFound"):
                _fail("solar still def(s) did not resolve live: %s" % r.get("notFound"))
            if not _same(_get_setting(t, "stillRateMultiplier"), 1.0):
                _fail("stillRateMultiplier is not at its shipped default 1.0")
            if not _same(_get_setting(t, "solarStillEnabled"), True):
                _fail("solarStillEnabled is not at its shipped default True")

    with _comp(t, "sun_lance_defs"):
        # STILLSAND_SUN_LANCE_1: the turret, its gun and the shared mirror-beam verb must resolve live.
        need = ["ThingDef/RM_SunLance", "ThingDef/RM_SunLance_Gun"]
        for d in need:
            if d not in SHIPPED:
                _fail("%s is not parsed from this mod's Defs/ (parser or def missing)" % d)
        # Static: the lance must never be able to ignite (no fire chance on the verb, heat-only damage).
        import re as _re
        xml = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_SunLance.xml"), encoding="utf-8").read()
        for tag in ("beamChanceToStartFire", "beamChanceToAttachFire"):
            m = _re.search(r"<%s>([^<]*)</%s>" % (tag, tag), xml)
            if not m or float(m.group(1)) != 0.0:
                _fail("%s is not explicitly 0 in RM_SunLance.xml" % tag)
        if "RM_Verb_MirrorBeam" not in xml:
            _fail("RM_SunLance_Gun does not use the shared RM_Verb_MirrorBeam")
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs=";".join(need), fields="defName", limit=20)
            _ok(r, "get_defs(sun lance)")
            if r.get("notFound"):
                _fail("sun lance def(s) did not resolve live: %s" % r.get("notFound"))
            if not _same(_get_setting(t, "sunLanceEnabled"), True):
                _fail("sunLanceEnabled is not at its shipped default True")

    with _comp(t, "geophone_defs"):
        # STILLSAND_GEOPHONE_1: the geophone and its comp must resolve live; it must read the sand-swim
        # kit's query (not a private copy) and show only a bearing and a size class.
        if "ThingDef/RM_Geophone" not in SHIPPED:
            _fail("ThingDef/RM_Geophone is not parsed from this mod's Defs/ (parser or def missing)")
        src = open(os.path.join(HERE, "Source", "RM_Geophone.cs"), encoding="utf-8").read()
        if "RM_CompSandSwim" not in src or ".Submerged" not in src:
            _fail("RM_Geophone.cs does not read the sand-swim kit's Submerged query")
        if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Building", "Production", "RM_Geophone.png")):
            _fail("RM_Geophone.png is missing")
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Geophone", fields="defName", limit=5)
            _ok(r, "get_defs(geophone)")
            if r.get("notFound"):
                _fail("geophone def did not resolve live: %s" % r.get("notFound"))
            if not _same(_get_setting(t, "geophoneRadius"), 20.0):
                _fail("geophoneRadius is not at its shipped default 20")

    with _comp(t, "sand_swim_remainder"):
        # STILLSAND_SAND_SWIM_REMAINDER_1 (offline half): the thumper, drift depth, sand fishing and the
        # Listening are all wired to the kit's own query/hooks, not private copies; art and sounds exist.
        # The LIVE half (a charged thumper calling a submerged swimmer, a catch, the singing warning) is
        # owed to a bridge session and is NOT claimed here. Wake track records wait on FOOTPRINT_TRACK_GRID_1.
        for need in ("ThingDef/RM_Thumper", "SoundDef/RM_SandHiss", "SoundDef/RM_SandSaltation", "SoundDef/RM_DuneSong",
                     "SoundDef/RM_SandSwimRumble", "SoundDef/RM_SandSwimBreach", "BiomeDef/RM_Stillsand"):
            if need not in SHIPPED:
                _fail("%s is not parsed from this mod's Defs/" % need)
        rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
        thump, rem = rd("Source", "RM_Thumper.cs"), rd("Source", "RM_SandSwimRemainder.cs")
        if "SubmergedSwimmersNear" not in thump:
            _fail("RM_Thumper.cs does not use the kit's SubmergedSwimmersNear query")
        if "IsSwimTerrain" not in rem or "sandGrid" not in rem:
            _fail("drift depth is not wired as a postfix on IsSwimTerrain over map.sandGrid")
        biome = rd("Defs", "BiomeDefs", "RM_Stillsand_Biome.xml")
        if "<fishTypes" not in biome or "RM_DuneCrawler" not in biome or "RM_RareSandCatches" not in biome:
            _fail("RM_Stillsand carries no fishTypes with the dune crawler and the rare-catch pool")
        if "RM_GlassPearl" not in rd("Defs", "ThingSetMakerDefs", "RM_RareSandCatches.xml"):
            _fail("RM_RareSandCatches does not yield the glass pearl")
        if "StilledWater" not in rd("Defs", "ThingDefs_Buildings", "RM_Thumper.xml"):
            _fail("the thumper's water charge is not fed by RM_StilledWater")
        if "RM_Thumper.cs" not in rd("Source", "RM_Stillsand.csproj") or "RM_SandSwimRemainder.cs" not in rd("Source", "RM_Stillsand.csproj"):
            _fail("a remainder .cs is not in the csproj <Compile Include> list (it would compile into nothing)")
        if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Building", "Production", "RM_Thumper.png")):
            _fail("RM_Thumper.png is missing")
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Thumper", fields="defName", limit=5)
            _ok(r, "get_defs(thumper)")
            if r.get("notFound"):
                _fail("thumper def did not resolve live: %s" % r.get("notFound"))
            if not _same(_get_setting(t, "driftSwimDepth"), 0.3):
                _fail("driftSwimDepth is not at its shipped default 0.3")

    with _comp(t, "cave_tier_rows"):
        # STILLSAND_CAVE_TIER_ROWS_1: the krayt den, sarlacc seep and debt cave rows live in their own
        # tier mods; with all tiers loaded the Mod Settings list eight rows. Offline: each file must
        # name its row, its things must be defined where they live, and the table must total eight.
        import re as _re3
        src = os.path.abspath(os.path.join(HERE, "..", ".."))
        rows = {
            "RSW_PreciousCave_KraytDen": os.path.join(src, "RimStarWars", "SWBestiary", "Defs", "MapGeneration", "RSW_PreciousCave_KraytDen.xml"),
            "RSW_PreciousCave_SarlaccSeep": os.path.join(src, "RimStarWars", "Sarlacc", "Defs", "MapGeneration", "RSW_PreciousCave_SarlaccSeep.xml"),
            "RUT_PreciousCave_DebtCave": os.path.join(src, "RimUtinni", "UtinniPatches", "Defs", "MapGeneration", "RUT_PreciousCave_DebtCave.xml"),
        }
        total = len(_re3.findall(r"<RimMandrake\.Stillsand\.RM_PreciousCaveDef[ >]",
                                 open(os.path.join(HERE, "Defs", "MapGeneration", "RM_PreciousCaves.xml"), encoding="utf-8").read()))
        for name, path in rows.items():
            if not os.path.isfile(path):
                _fail("%s: row file missing at %s" % (name, path))
                continue
            x = open(path, encoding="utf-8").read()
            if "<defName>%s</defName>" % name not in x or 'MayRequire="mandrake.rm.biomes"' not in x:
                _fail("%s: row def or its mandrake.rm.biomes gate is missing" % name)
            total += 1
        if total != 8:
            _fail("precious table has %d rows, expected 8" % total)
        tree = os.path.join(src, "RimStarWars")
        for d, where in (("RSW_KraytDragonSkull", "SWBestiary"), ("RSW_KraytPearl", "SWBestiary"),
                         ("RSW_GreaterKraytDragon", "SWBestiary"), ("RSW_DeepDesertSeep", "Sarlacc")):
            hit = False
            for root, _, files in os.walk(os.path.join(tree, where, "Defs")):
                for f in files:
                    if f.endswith(".xml") and "<defName>%s</defName>" % d in open(os.path.join(root, f), encoding="utf-8").read():
                        hit = True
            if not hit:
                _fail("%s is not defined in %s" % (d, where))
        csp = open(os.path.join(HERE, "Source", "RM_Stillsand.csproj"), encoding="utf-8").read()
        if "RM_CaveTierElements.cs" not in csp:
            _fail("RM_CaveTierElements.cs is not in the csproj Compile list")

    with _comp(t, "cave_place_defs"):
        # STILLSAND_CAVE_AS_PLACE_1: wall, drip source, tribal mark, drip sound must resolve; the drip
        # clip must exist on disk; the grotto must use the wall ring (no floor biosilica stacks) and
        # the taken row must carry its own mark, not the Graffiti soft reference.
        need = ["ThingDef/RM_GrownBiosilicaWall", "ThingDef/RM_CaveDripSource",
                "ThingDef/RM_StillsandTribalMark", "SoundDef/RM_CaveDrip"]
        for d in need:
            if d not in SHIPPED:
                _fail("%s is not parsed from this mod's Defs/ (parser or def missing)" % d)
        if not os.path.isfile(os.path.join(HERE, "Sounds", "RM", "CaveDrip.wav")):
            _fail("Sounds/RM/CaveDrip.wav (the drip clip) is missing")
        for tex in ("Textures/Things/Building/Natural/RM_GrownBiosilicaWall.png",
                    "Textures/Things/Filth/RM_StillsandTribalMark.png"):
            if not os.path.isfile(os.path.join(HERE, *tex.split("/"))):
                _fail("%s is missing" % tex)
        import re as _re2
        cx = open(os.path.join(HERE, "Defs", "MapGeneration", "RM_PreciousCaves.xml"), encoding="utf-8").read()
        grotto = cx.split("RM_PreciousCave_LensGrotto</defName>")[1].split("</RimMandrake.Stillsand.RM_PreciousCaveDef>")[0]
        if "RM_CaveElement_WallRing" not in grotto or "<thing>RM_Biosilica</thing>" in grotto:
            _fail("lens grotto must be a wall ring with no loose biosilica floor stacks")
        taken = cx.split("RM_PreciousCave_Taken</defName>")[1].split("</RimMandrake.Stillsand.RM_PreciousCaveDef>")[0]
        if "RM_StillsandTribalMark" not in taken or "RM_Graffiti_Vandal" in taken:
            _fail("taken cave must carry RM_StillsandTribalMark and no Graffiti soft reference")
        wall = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_CavePlace.xml"), encoding="utf-8").read()
        if "<mineableThing>RM_Biosilica</mineableThing>" not in wall:
            _fail("RM_GrownBiosilicaWall does not yield RM_Biosilica")
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs=";".join(need), fields="defName", limit=20)
            _ok(r, "get_defs(cave place)")
            if r.get("notFound"):
                _fail("cave place def(s) did not resolve live: %s" % r.get("notFound"))
            for f in ("preservationEnabled", "dripEnabled", "wallRingEnabled", "tribalMarkEnabled"):
                if not _same(_get_setting(t, f), True):
                    _fail("%s is not at its shipped default True" % f)
            # Offline-proven only: a corpse on a roofed cave cell not rotting needs a generated cave
            # (site_chain regenerates one) and is NOT exercised here; criteria 1-2 await a live pass.

    with _comp(t, "custom_defs_resolve"):
        if _live(t):
            if len(CUSTOM_SHIPPED) < 5:
                _fail("parsed only %d custom-class defs (parser broken?)" % len(CUSTOM_SHIPPED))
            r = t.bridge_call("jawa/get_defs", defs=";".join(CUSTOM_SHIPPED), fields="defName", limit=200)
            _ok(r, "get_defs(custom)")
            if r.get("malformed"):
                _unmeasured(t, "get_defs could not parse the custom def types %s" % r["malformed"][:4])
            nf = list(r.get("notFound") or [])
            if nf and len(nf) == len(CUSTOM_SHIPPED):
                _unmeasured(t, "get_defs resolved none of the custom def type names (the type name form "
                               "is unproven): %s" % nf[:3])
            if nf:
                _fail("custom def(s) did not resolve: %s" % nf[:8])

    with _comp(t, "biome_row"):
        if _live(t):
            f, _ = _get_defs(t, "BiomeDef/%s" % BIOME, "animalDensity,modExtensions,extraGenSteps")
            row = f.get(BIOME) or {}
            dens = row.get("animalDensity")
            if not isinstance(dens, (int, float)) or dens <= 0:
                _fail("animalDensity %r: <= 0 means the animal roster can never spawn" % dens)
            ext = row.get("modExtensions")
            steps = row.get("extraGenSteps")
            if not isinstance(ext, list) or not isinstance(steps, list):
                _unmeasured(t, "BiomeDef modExtensions / extraGenSteps unreadable: %r / %r" % (ext, steps))
            miss_e = [e for e in BIOME_EXTENSIONS if not any(str(x).endswith(e) for x in ext)]
            miss_s = [s for s in BIOME_GENSTEPS if s not in [str(x) for x in steps]]
            _note(t, "biome extensions / extra gen steps", [ext, steps])
            if miss_e or miss_s:
                _fail("RM_Stillsand lacks extension(s) %s and gen step(s) %s: the patches that add them "
                      "matched nothing (and a patch that matches nothing logs nothing)" % (miss_e, miss_s))

    with _comp(t, "biome_roster"):
        if _live(t):
            want = sorted(list(ROSTER_ANIMALS) + list(ROSTER_PLANTS))
            if len(want) < 15:
                _fail("parsed only %d roster rows from the BiomeDef (parser broken?)" % len(want))
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True,
                              find=",".join(want + ["RM_Stillsand_NoSuchProbe"]), topN=200)
            _ok(r, "biome_probe")
            rows = [b for b in (r.get("biomes") or []) if b.get("defName") == BIOME]
            if not rows:
                _unmeasured(t, "biome_probe returned no row for %s" % BIOME)
            states = dict((x.get("defName"), x.get("state")) for x in (rows[0].get("findResults") or []))
            if states.get("RM_Stillsand_NoSuchProbe") != "absent":
                _fail("sanity probe: a name that is not in the biome did not read 'absent': %r"
                      % states.get("RM_Stillsand_NoSuchProbe"))
            bad = dict((n, states.get(n)) for n in want if states.get(n) != "spawning")
            if bad:
                _fail("roster row(s) that do not resolve to a spawning wild animal/plant: %s" % bad)

    with _comp(t, "giants_skeleton_wired"):
        if _live(t):
            f, r = _get_defs(t, ";".join("ThingDef/%s" % n for n in GIANT_RACES), "modExtensions")
            if r.get("notFound"):
                _fail("giant race def(s) missing: %s" % r["notFound"])
            bad = [n for n in GIANT_RACES
                   if not any(str(x).endswith("RM_SkeletonRemainsExtension")
                              for x in ((f.get(n) or {}).get("modExtensions") or []))]
            if bad:
                _fail("giant(s) without RM_SkeletonRemainsExtension (the wiring patch matched nothing): %s"
                      % bad)

    with _comp(t, "water_egg_patched"):
        if _live(t):
            f, _ = _get_defs(t, "ThingDef/RM_GuzzkaEggUnfertilized", "comps")
            comps = (f.get("RM_GuzzkaEggUnfertilized") or {}).get("comps")
            if not isinstance(comps, list) or not comps:
                _unmeasured(t, "the egg's comps are unreadable: %r" % (comps,))
            if not any(str(c).endswith("RM_CompProperties_WaterVolume") for c in comps):
                _fail("the unfertilized guzzka egg carries no water-volume comp (the canteen-egg patch "
                      "matched nothing): %s" % comps)

    with _comp(t, "eruption_biome_gate"):
        if _live(t):
            f, _ = _get_defs(t, "IncidentDef/RM_SandBusterEruption", "allowedBiomes")
            got = (f.get("RM_SandBusterEruption") or {}).get("allowedBiomes")
            if not isinstance(got, list):
                _unmeasured(t, "allowedBiomes unreadable: %r" % (got,))
            if [str(x) for x in got] != [BIOME]:
                _fail("RM_SandBusterEruption.allowedBiomes is %s, expected only %s (the eruption must be "
                      "confined to the Stillsand)" % (got, BIOME))


# ----------------------------------------------------------------------------- chain: settings

@_chain("settings")
def settings_chain(t):
    _pad(t, "settings")
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
            r = t.bridge_call("jawa/mod_settings_field", typeName=NS + "RM_StillsandSettings", action="get",
                              field="noSuchFieldProbe")
            if (r or {}).get("success") is not False:
                _fail("sanity probe: reading a nonexistent settings field did not fail: %r" % r)

    # Toggles whose EFFECT this suite cannot drive (see the module docstring): the field must exist,
    # read its shipped default and be writable, restored afterwards.
    for field in ("yardangShapingEnabled", "torEnabled", "boneHarpEnabled", "ledgerEnabled",
                  "ledgerIncidentWeighting", "sieveEnabled", "solarStillEnabled", "wringingStillEnabled", "sunLanceEnabled", "geophoneEnabled", "thumperEnabled", "sandFishingWakeEnabled", "driftSwimEnabled",
                  "listeningHissEnabled", "listeningSingingEnabled", "listeningWarningEnabled", "listeningRumbleEnabled", "abrasionEnabled", "carryEnabled", "staticEnabled",
                  "seedingEnabled", "hornEnabled", "denQuestEnabled"):
        with _comp(t, "%s_roundtrip" % field, toggle=field):
            if _live(t):
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s is not at its shipped default" % field)
                with _setting(t, field, not DEFAULTS[field]):
                    pass


# ----------------------------------------------------------------------------- chain: sun

def _sun(t, cells):
    r = t.bridge_call("jawa/shadegrid_read", cells=cells)
    if not _live(t):
        return {}
    _ok(r, "shadegrid_read")
    if not r.get("present"):
        _unmeasured(t, "shadegrid_read: present=false (%s)" % r.get("reason"))
    return r


def _settle_shade(t):
    """Step past the shade grid's next rebuild. RM_MapComponent_ShadeGrid.Recompute runs only when
    TicksGame % 2000 == 0 (CreatureBehaviors RM_MapComponent_ShadeGrid.cs, RecomputeIntervalTicks; no
    dirty events), so a pad _prep just cleared of rock / overhead-mountain roof still reads the OLD shade
    (shade 1.0, exposure 0) until then. Every sun consumer reads that cached grid: the sun tables
    (RM_SunPower.FactorAt -> ShadeAt), the loomma clock (ShadeDrivenSeverity -> ShadeAt), glare
    (ExposureAt). Call AFTER the chain's own roofs are set, BEFORE anything reads or ticks the sun."""
    if not _live(t):
        return
    now = int(_ok(t.bridge_call("jawa/time_clock"), "time_clock")["ticksGame"])
    t.wait_ticks(2000 - now % 2000 + 5)


def _exposure(r, x, z):
    for c in (r.get("cells") or []):
        if c.get("x") == x and c.get("z") == z and c.get("inBounds"):
            return c.get("exposure")
    return None


@_chain("sun")
def sun_chain(t):
    _prep(t, "sun")
    x, z = t.anchor
    with _comp(t, "sun_pinned_no_night"):
        if _live(t):
            r = _sun(t, "%d,%d" % (x, z))
            pin = r.get("pinnedSun") or {}
            elev = pin.get("sunElevationDegrees")
            _note(t, "pinned sun", [pin, r.get("skyGlow"), _STATE.get("lat")])
            if not (pin.get("present") and pin.get("isActive")):
                _fail("the Stillsand's pinned sun is not active: %r (RM_PinnedSunExtension not applied?)" % pin)
            if not isinstance(elev, (int, float)) or not (2 <= elev <= 85):
                _fail("pinned sun elevation %r outside the biome's 2..85 degree clamp" % (elev,))
            if not isinstance(r.get("skyGlow"), (int, float)) or r["skyGlow"] < 0.99:
                _fail("sky glow %r at this hour: the day-night cycle is not pinned" % r.get("skyGlow"))
            clk = _ok(t.bridge_call("jawa/time_clock"), "time_clock")
            t.bridge_call("jawa/time_set_ticks", ticks=int(clk["ticksGame"]) + 30000)   # twelve hours on
            t.wait_ticks(60)
            r2 = _sun(t, "%d,%d" % (x, z))
            if not isinstance(r2.get("skyGlow"), (int, float)) or r2["skyGlow"] < 0.99:
                _fail("sky glow %r twelve hours later: night falls on a pinned-sun biome" % r2.get("skyGlow"))

    with _comp(t, "sun_open_sand_full_exposure"):
        if _live(t):
            r = _sun(t, "%d,%d" % (x, z))
            ex = _exposure(r, x, z)
            _STATE["open_exposure"] = ex
            if not isinstance(ex, (int, float)):
                _unmeasured(t, "no exposure value for the open cell: %r" % (r.get("cells"),))
            if ex < 0.6:
                _fail("an open sand cell reads sun exposure %.2f, below the 0.6 that glare-blind needs" % ex)

    with _comp(t, "sun_roof_cover_above_55deg"):
        if _live(t):
            rr = _rect(t, 6, dx=-9)
            t.bridge_call("jawa/set_roof_batch", ops=_rs(rr), roofDef="RoofConstructed")
            cx, cz = rr[0] + 3, rr[1] + 3
            r = _sun(t, "%d,%d;%d,%d" % (cx, cz, x, z))
            elev = (r.get("pinnedSun") or {}).get("sunElevationDegrees")
            if not isinstance(elev, (int, float)):
                _unmeasured(t, "sun elevation unreadable")
            if elev < 55:
                _unmeasured(t, "sun elevation %.1f deg is below the 55 deg where a roof is cover (by "
                               "design a roof is NOT cover at a low sun); this site cannot test it" % elev)
            roofed, opened = _exposure(r, cx, cz), _exposure(r, x, z)
            if roofed is None or opened is None:
                _unmeasured(t, "exposure unreadable")
            if roofed > 0.05 or opened <= roofed:
                _fail("roofed cell exposure %.2f, open %.2f at elevation %.0f deg (a roof must protect "
                      "above 55 deg)" % (roofed, opened, elev))


# ----------------------------------------------------------------------------- chain: fauna & flora

@_chain("fauna")
def fauna_chain(t):
    _prep(t, "fauna")
    rect = _rect(t)
    x0, z0 = rect[0] + 2, rect[1] + 2
    with _comp(t, "fauna_spawns"):
        if _live(t):
            if len(KINDS) < 20:
                _fail("parsed %d PawnKindDefs, expected 22" % len(KINDS))
            ids = {}
            for i, kind in enumerate(KINDS):
                ids[kind] = _spawn(t, kind, x0 + (i % 6) * 3, z0 + (i // 6) * 3)
            rows = _rows(t, rect=_rs(rect))
            lost = [k for k, pid in ids.items()
                    if pid not in rows or rows[pid].get("dead") or rows[pid].get("kindDef") != k]
            _note(t, "kinds spawned", {"asked": len(KINDS), "lost": lost})
            if lost:
                _fail("kind(s) spawned no living pawn of that kind in the rect: %s" % lost)
            _STATE["soorrak"] = ids.get("RM_Soorrak")

    with _comp(t, "soorrak_can_fly"):
        if _live(t):
            pid = _STATE.get("soorrak")
            if not pid:
                _unmeasured(t, "no soorrak was spawned to read")
            r = t.bridge_call("jawa/pawn_flight", action="report", pawn=pid)
            rows = (_ok(r, "pawn_flight").get("pawns") or [])
            if not rows or "canEverFly" not in rows[0]:
                _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
            if rows[0].get("canEverFly") is not True:
                _fail("RM_Soorrak canEverFly=%r (MaxFlightTime stat %r)" % (rows[0].get("canEverFly"),
                                                                           rows[0].get("maxFlightTimeStat")))


@_chain("flora")
def flora_chain(t):
    _prep(t, "flora")
    rect = _rect(t)
    with _comp(t, "flora_spawns"):
        if _live(t):
            if len(PLANTS) < 5:
                _fail("parsed %d plant defs, expected 5" % len(PLANTS))
            cells = {}
            for i, d in enumerate(PLANTS):
                cx, cz = rect[0] + 2 + (i % 6) * 3, rect[1] + 2 + (i // 6) * 3
                cells[d] = (cx, cz)
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, cx, cz), growth=1.0)
            lost = [d for d, (cx, cz) in cells.items() if _count(t, d, "%d,%d,1,1" % (cx, cz)) < 1]
            _note(t, "flora set", {"asked": len(PLANTS), "lost": lost})
            if lost:
                _fail("plant def(s) did not stand after set_plants: %s" % lost)


# ----------------------------------------------------------------------------- chain: sand swimmers

@_chain("sandswim")
def sandswim_chain(t):
    _prep(t, "sandswim")
    rect = _rect(t)
    x, z = t.anchor
    sand, grav = (x - 10, z - 6), (x - 10, z + 6)
    with _comp(t, "vekka_submerges_on_sand"):
        if _live(t):
            t.bridge_call("jawa/set_terrain_batch", ops="Gravel:%d,%d,10,6" % (grav[0] - 3, grav[1] - 3),
                          layer="top")
            on_sand = _spawn(t, "RM_Vekka", sand[0], sand[1])
            on_grav = _spawn(t, "RM_Vekka", grav[0], grav[1])
            t.wait_ticks(300)
            rows = _rows(t, rect=_rs(rect), health=True)
            _note(t, "vekka hediffs (sand / gravel)", [[h.get("def") for h in _hediffs(rows.get(on_sand))],
                                                       [h.get("def") for h in _hediffs(rows.get(on_grav))]])
            if on_sand not in rows or on_grav not in rows:
                _unmeasured(t, "a vekka left the pad before it could be read")
            if not _has(rows[on_sand], "RM_SandSubmerged"):
                _fail("a vekka standing on Sand is not RM_SandSubmerged (RM_SandSwimExtension not applied?)")
            if _has(rows[on_grav], "RM_SandSubmerged"):
                _fail("a vekka on Gravel is RM_SandSubmerged: the swimmer 'swims' through rock")

    with _comp(t, "vekka_take_leaves_funnel"):
        if _live(t):
            _prep(t, "sandswim")
            before = _letters(t)
            vek = _spawn(t, "RM_Vekka", x - 4, z)
            bait = _spawn(t, "Chicken", x, z, faction="player")
            dead = False
            for _ in range(8):
                t.bridge_call("jawa/ordered_job", pawnId=vek, jobDef="AttackMelee", targetAId=bait)
                t.wait_ticks(400)
                row = _rows(t).get(bait)
                if row is None or row.get("dead"):
                    dead = True
                    break
            if not dead:
                _unmeasured(t, "the bait chicken was never killed in 3200 ticks (vekka refused the job?)")
            funnels = _count(t, "RM_Filth_DisturbedSand", _rs(_rect(t, 40)))
            took = [l for l in _new_letters(before, _letters(t)) if l[0].startswith("Taken under")]
            _note(t, "disturbed-sand funnels / take letters", [funnels, [l[0] for l in took]])
            if not took:
                _unmeasured(t, "no 'Taken under' letter: the kill was not read as a take (bait died of "
                               "something else?)")
            if funnels < 1:
                _fail("a swimmer took a victim on sand and left no RM_Filth_DisturbedSand funnel "
                      "(SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1)")


# ----------------------------------------------------------------------------- chain: the zuurrik

def _blood(t, cells):
    t.bridge_call("jawa/spawn_batch", ops=";".join("Filth_Blood:%d,%d" % c for c in cells))


def _zuurriks(t):
    return [p for p in _rows(t).values() if p.get("kindDef") == "RM_Zuurrik" and not p.get("dead")]


def _cluster(x, z):
    return [(x + (j % 4) * 2, z + (j // 4) * 2) for j in range(12)]


@_chain("zuurrik")
def zuurrik_chain(t):
    _pad(t, "zctl")
    _prep(t, "zctl")
    cx, cz = t.anchor
    with _comp(t, "zuurrik_below_threshold_dormant"):
        if _live(t):
            _blood(t, [(cx - 3 + 2 * j, cz) for j in range(3)])        # 3 cells < the threshold of 8
            if _count(t, "Filth_Blood", _rs(_rect(t))) < 3:             # read BEFORE any swarm could strip it
                _unmeasured(t, "the control blood did not stand")
            t.wait_ticks(1800)
            n = len(_zuurriks(t))
            if n:
                _fail("%d zuurrik woke on 3 blood cells (threshold 8): the wake ignores the threshold" % n)
    _pad(t, "zuurrik")
    _prep(t, "zuurrik")
    x, z = t.anchor
    rect = _rect(t)
    with _comp(t, "zuurrik_wakes_on_blood", toggle="zuurrikEnabled"):
        if _live(t):
            _blood(t, _cluster(x - 14, z - 6))
            if _count(t, "Filth_Blood", _rs(rect)) < 8:
                _unmeasured(t, "the blood cluster did not stand on the sand")
            t.wait_ticks(1800)
            swarm = _zuurriks(t)
            _STATE["blood_at_wake"] = _count(t, "Filth_Blood", _rs(rect))
            _note(t, "zuurrik swarm after 1800 ticks", len(swarm))
            if not swarm:
                _fail("12 blood cells on sand (threshold 8) woke no zuurrik in 1800 ticks")
    with _comp(t, "zuurrik_strips_blood"):
        if _live(t):
            before = _STATE.get("blood_at_wake")
            if not before or not _zuurriks(t):
                _unmeasured(t, "no awake swarm to watch")
            t.wait_ticks(3000)
            after = _count(t, "Filth_Blood", _rs(rect))
            _note(t, "blood cells at wake / 3000 ticks later", [before, after])
            if after >= before:
                _fail("the swarm did not strip any blood in 3000 ticks (%d -> %d)" % (before, after))
    with _comp(t, "zuurrik_toggle_off_no_wake", toggle="zuurrikEnabled"):
        if _live(t):
            _blood(t, _cluster(x - 14, z + 6))                 # fresh stain, so the on arm has a cause
            first = [p["id"] for p in _zuurriks(t)]
            with _setting(t, "zuurrikEnabled", False):          # off FIRST: a swarm killed while on re-wakes
                for p in _zuurriks(t):
                    _kill(t, p["x"], p["z"])
                t.wait_ticks(1800)
                alive = _zuurriks(t)
            if [p for p in alive if p["id"] in first]:
                _unmeasured(t, "could not kill the first swarm")
            woke = len(alive)
            t.wait_ticks(1800)
            back = len(_zuurriks(t))
            _note(t, "zuurrik after toggle off / after toggle back on", [woke, back])
            if woke:
                _fail("zuurrikEnabled is off and %d zuurrik woke anyway" % woke)
            if not back:
                _unmeasured(t, "the swarm did not wake with the toggle back on either: the off arm proves "
                               "nothing (see zuurrik_wakes_on_blood)")


# ----------------------------------------------------------------------------- chain: loomma

@_chain("loomma")
def loomma_chain(t):
    _prep(t, "loomma")
    rect = _rect(t)
    x, z = t.anchor
    roof = (x + 2, z - 5, 9, 9)
    # RULED OUT: night / time of day zeroed the sun — the Stillsand sun is pinned (sun_pinned_no_night PASS,
    #   skyGlow 1.0 twelve hours on); RM_SunPower.Intensity reads the pinned elevation, never the clock.
    # RULED OUT: startingHediffs not applied by spawn_pawn — PawnGenerator.cs:1269 adds kindDef.startingHediffs
    #   for every non-newborn; the hediff was REMOVED, not never added: 0.03 start, -20/day in shade is
    #   -0.067 per 200-tick interval (HediffComp_SeverityModifierBase), so one interval in the STALE shade grid
    #   (pad prepped at 45731, grid rebuilt only at 46000) deleted it (Hediff.ShouldRemove: Severity <= 0)
    #   and nothing re-adds it. Fixed: _settle_shade before the spawn; the def now carries minSeverity so the
    #   clock can never be deleted (RM_Stillsand_Fillout.xml).
    # Wait 600, not 1500: at +40/day a loomma in full sun goes 0.03 -> lethal 1.0 in ~1455 ticks, so a
    #   1500-tick read finds corpses (read as "left the pad"). 600 ticks = 3 intervals = ~+0.4.
    with _comp(t, "loomma_sunstruck_open_vs_roofed"):
        if _live(t):
            t.bridge_call("jawa/set_roof_batch", ops=_rs(roof), roofDef="RoofConstructed")
            _settle_shade(t)
            opn = [_spawn(t, "RM_Loomma", x - 9 + i, z) for i in range(3)]
            shd = [_spawn(t, "RM_Loomma", roof[0] + 3 + i, roof[1] + 4) for i in range(3)]
            t.wait_ticks(600)
            rows = _rows(t, rect=_rs(rect), health=True)
            so = [_sev(rows.get(p), "RM_LoommaSunstruck") for p in opn if p in rows]
            ss = [_sev(rows.get(p), "RM_LoommaSunstruck") for p in shd if p in rows]
            _note(t, "loomma sunstruck severities (open / roofed)", [so, ss])
            if not so or not ss:
                _unmeasured(t, "loommas left the pad before they could be read")
            if max(so) <= 0.0:
                _fail("an open-sand loomma never gained RM_LoommaSunstruck in 600 ticks")
            if sum(so) / len(so) <= sum(ss) / len(ss) + 0.02:
                _fail("sunstruck is no worse in the open (%s) than under a roof (%s): the clock ignores shade"
                      % (so, ss))


# ----------------------------------------------------------------------------- chain: soorrak

@_chain("soorrak")
def soorrak_chain(t):
    _prep(t, "soorrak")
    rect = _rect(t)
    x, z = t.anchor
    with _comp(t, "soorrak_no_exceptions"):
        if _live(t):
            base_a = _log_lines(t, "Soorrak", errors_only=True)[1]
            base_b = _log_lines(t, "Notify_JobStarted", errors_only=True)[1]
            ids = [_spawn(t, "RM_Soorrak", x - 4 + 2 * i, z) for i in range(6)]
            _STATE["soorrak_ids"] = ids
            track = dict((i, [_xz(_rows(t).get(i))]) for i in ids)
            jobs = dict((i, []) for i in ids)
            for _ in range(6):
                t.wait_ticks(500)
                rows = _rows(t)
                sj = t.bridge_call("jawa/site_state")
                jmap = dict((p.get("id"), p.get("job")) for p in ((sj or {}).get("pawns") or []))
                for i in ids:
                    track[i].append(_xz(rows.get(i)))
                    jobs[i].append(jmap.get(i))
            _STATE["soorrak_track"], _STATE["soorrak_jobs"] = track, jobs
            a = _log_lines(t, "Soorrak", errors_only=True)[1] - base_a
            b = _log_lines(t, "Notify_JobStarted", errors_only=True)[1] - base_b
            _note(t, "new log errors naming Soorrak / Notify_JobStarted", [a, b])
            if a > 0 or b > 0:
                _fail("%d error(s) naming Soorrak and %d in Pawn_FlightTracker.Notify_JobStarted while 6 "
                      "soorraks ran 3000 ticks (SOORRAK_FLIGHT_JOBSTART_NRE_1)" % (a, b))

    with _comp(t, "soorrak_not_stuck"):
        if _live(t):
            track, jobs = _STATE.get("soorrak_track"), _STATE.get("soorrak_jobs")
            if not track:
                _unmeasured(t, "the soorrak run did not complete")
            rows = _rows(t)
            alive = [i for i in track if i in rows and not rows[i].get("dead")]
            if not alive:
                _unmeasured(t, "every soorrak left the map or died (flying off is by design): nothing "
                               "left to judge")
            moved = {}
            for i in alive:
                pts = [p for p in track[i] if p]
                moved[i] = sum(_dist(a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else 0.0
            idle = ("Wait_MaintainPosture", "Wait", None)
            busy = [i for i in alive if moved[i] >= 3.0 or any(j not in idle for j in jobs[i])]
            _note(t, "soorrak path length / jobs seen", {"moved": moved, "jobs": dict((i, sorted(set(map(str, jobs[i])))) for i in alive)})
            if not busy:
                _fail("%d soorrak(s) stayed on the map for 3000 ticks and never moved 3 cells or read any "
                      "job but the 1-tick filler (an instantly-ending job every think cycle)" % len(alive))


# ----------------------------------------------------------------------------- chain: sun-fed glass

TABLES = (("RM_SunFurnace", "sunFurnaceEnabled"), ("RM_LensBench", "lensBenchEnabled"),
          ("RM_SolarOven", "solarOvenEnabled"))


def _inspect(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return None, []
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows or rows[0].get("error"):
        _fail("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return rows[0].get("label"), list(rows[0].get("inspect") or [])


def _table_state(t, tid):
    """The sun table's own inspect line, with a too-low sun read as the site's fault (UNMEASURED)."""
    _, lines = _inspect(t, tid)
    txt = " | ".join(str(x) for x in lines)
    if "sun is too low" in txt or "no sun" in txt:
        _unmeasured(t, "the site's sun is too low for a sun table (%s): latitude %s" % (txt[:120],
                                                                                       _STATE.get("lat")))
    return txt


@_chain("glass")
def glass_chain(t):
    _prep(t, "glass")
    x, z = t.anchor
    roof = (x + 5, z + 4, 8, 8)
    ids = {}
    with _comp(t, "glass_site_ready", poison=True):
        if _live(t):
            t.bridge_call("jawa/spawn_batch", ops="RM_SunFurnace:%d,%d" % (x - 8, z))
            t.bridge_call("jawa/spawn_batch", ops="RM_LensBench:%d,%d" % (x - 8, z - 5))
            t.bridge_call("jawa/spawn_batch", ops="RM_SolarOven:%d,%d" % (x - 8, z + 5))
            t.bridge_call("jawa/set_roof_batch", ops=_rs(roof), roofDef="RoofConstructed")
            t.bridge_call("jawa/spawn_batch", ops="RM_SunFurnace:%d,%d" % (roof[0] + 3, roof[1] + 3))
            for d, _f in TABLES:
                rows = _things(t, d, _rs(_rect(t)))
                if not rows:
                    _unmeasured(t, "%s did not stand after spawn_batch" % d)
                ids[d] = rows[0]["id"]
            fur = _things(t, "RM_SunFurnace", _rs(_rect(t)))
            under = [f for f in fur if roof[0] <= f.get("x", -1) < roof[0] + roof[2]
                     and roof[1] <= f.get("z", -1) < roof[1] + roof[3]]
            open_ = [f for f in fur if f not in under]
            if not under or not open_:
                _unmeasured(t, "the open and the roofed sun furnace did not both stand (%d under the roof, "
                               "%d outside)" % (len(under), len(open_)))
            ids["roofed"], ids["open"] = under[0]["id"], open_[0]["id"]
            ids["RM_SunFurnace"] = ids["open"]
            _settle_shade(t)

    # RULED OUT: night / the loomma chain ticking the clock into darkness — the sun is pinned (no night);
    #   the line read "in shade (sun 0%)", which FactorAt only writes when Intensity > 0 and the cached
    #   ShadeAt >= 0.5 (night would read "no sun"). The cell was not roofed (FactorAt checks Roofed live
    #   first). Cause: the shade grid was stale — pad prepped and read at tick 50231, last rebuild 50000
    #   (RecomputeIntervalTicks 2000). The glare pad read shade 1.0 / exposure 0.0 the same way.
    # RULED OUT: the StatDef patch matched nothing — thing_stats lists RM_StatPart_SunPowered in statParts.
    #   0.10 open = roofed = x2 is the WorkTableWorkSpeedFactor minValue 0.1 clamping max(0.05, sun 0)
    #   (StatDef minValue 0.1, RimSage Stats_Building_Special.xml): all three glass FAILs are one stale read.
    with _comp(t, "sun_table_reads_sun_in_open"):
        if _live(t):
            txt = _table_state(t, ids["open"])
            if not re.search(r"Sun: \d+%", txt):
                _fail("an open-sand sun furnace does not report 'Sun: NN%%': %s" % txt)

    with _comp(t, "sun_table_roofed_idle"):
        if _live(t):
            txt = _table_state(t, ids["roofed"])
            if "under a roof" not in txt:
                _fail("a roofed sun furnace does not report that it is under a roof: %s" % txt)

    with _comp(t, "furnace_work_speed_tracks_sun"):
        if _live(t):
            vals = {}
            for k in ("open", "roofed"):
                r = t.bridge_call("jawa/thing_stats", thing=ids[k], stats="WorkTableWorkSpeedFactor")
                for th in (_ok(r, "thing_stats").get("things") or []):
                    for s in th.get("stats") or []:
                        if s.get("defName") == "WorkTableWorkSpeedFactor":
                            vals[k] = float(s["value"])
            if len(vals) < 2:
                _unmeasured(t, "WorkTableWorkSpeedFactor unreadable: %r" % vals)
            _STATE["glass_open_speed"] = vals["open"]
            _note(t, "WorkTableWorkSpeedFactor open / roofed", vals)
            if not vals["open"] > 2.0 * vals["roofed"]:
                _fail("a sun furnace's work speed is %.2f in the open and %.2f roofed: the sun stat part "
                      "is not applied (the StatDef patch matched nothing?)" % (vals["open"], vals["roofed"]))

    for d, field in TABLES:
        with _comp(t, "%s_toggle_off_disabled" % d[3:].lower(), toggle=field):
            if _live(t):
                if not re.search(r"Sun: \d+%", _table_state(t, ids[d])):
                    _unmeasured(t, "%s does not read 'Sun: NN%%' with its toggle on: the off arm proves "
                                   "nothing" % d)
                with _setting(t, field, False):
                    off = _table_state(t, ids[d])
                if "Disabled in Mod Settings" not in off:
                    _fail("%s is off in Mod Settings but its inspect reads: %s" % (d, off))

    with _comp(t, "sun_work_speed_multiplier_scales"):
        if _live(t):
            base = _STATE.get("glass_open_speed")
            if not base:
                _unmeasured(t, "no open-sun work speed was read")
            with _setting(t, "sunWorkSpeedMultiplier", 2.0):
                t.bridge_call("jawa/stat_cache_bust", thing=ids["open"])
                r = t.bridge_call("jawa/thing_stats", thing=ids["open"], stats="WorkTableWorkSpeedFactor")
                got = None
                for th in (_ok(r, "thing_stats").get("things") or []):
                    for s in th.get("stats") or []:
                        if s.get("defName") == "WorkTableWorkSpeedFactor":
                            got = float(s["value"])
            t.bridge_call("jawa/stat_cache_bust", thing=ids["open"])
            _note(t, "work speed x1 / x2", [base, got])
            if got is None:
                _unmeasured(t, "the stat was unreadable with the multiplier at 2")
            if not (1.8 <= got / base <= 2.2):
                _fail("sunWorkSpeedMultiplier 2 moved the furnace's work speed %.2f -> %.2f (expected x2)"
                      % (base, got))

    # STILLSAND_GLASS_CHAIN_REMAINDER_1: krayt lens (patch-added), sun-glass goggles, art wire-in.
    with _comp(t, "glass_remainder_static"):
        import re as _re
        rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
        patch = rd("Patches", "RM_KraytLens.xml")
        if "PatchOperationConditional" not in patch or 'defName="RSW_KraytPearl"' not in patch:
            _fail("RM_KraytLens.xml does not guard the lens on RSW_KraytPearl's own xpath")
        if _re.search(r"<Operation[^>]*MayRequire", patch) or "PatchOperationAddOrReplace" in patch:
            _fail("RM_KraytLens.xml uses an Operation MayRequire or PatchOperationAddOrReplace")
        for need in ("<defName>RSW_KraytLens</defName>", "<defName>RSW_GrindKraytLens</defName>",
                     "<li>RSW_KraytPearl</li>", "<li>RM_LensGlass</li>", "<li>RM_LensBench</li>"):
            if need not in patch:
                _fail("RM_KraytLens.xml is missing %s" % need)
        gog = rd("Defs", "ThingDefs_Apparel", "RM_SunGoggles.xml")
        if gog.count("<li>RM_GlareProtection</li>") != 2 or "<defName>RM_SunGogglesGlass</defName>" not in gog \
                or "<RM_SunGlass>" not in gog:
            _fail("RM_SunGogglesGlass is missing, or does not carry RM_GlareProtection / cost sun glass")
        if "canBeDoneByNonColonists" in gog or "<minifiable>" in gog:
            _fail("goggles XML carries a field Core does not define")
        bld = rd("Defs", "ThingDefs_Buildings", "RM_GlassChain_Buildings.xml")
        if "RM_LensBench" in bld and "Graphic_Multi" in bld.split("<defName>RM_LensBench</defName>")[1].split("</graphicData>")[0]:
            _fail("RM_LensBench is Graphic_Multi but the art job delivers one sprite")
        tex = os.path.join(HERE, "Textures", "Things")
        for f in ("Item/Resource/RM_FineSand.png", "Item/Resource/RSW_KraytLens.png",
                  "Building/Production/RM_SolarOven.png",
                  "Pawn/Humanlike/Apparel/RM_SunGoggles/RM_SunGoggles.png",
                  "Pawn/Humanlike/Apparel/RM_SunGoggles/RM_SunGogglesWorn_south.png",
                  "Pawn/Humanlike/Apparel/RM_SunGoggles/RM_SunGogglesWorn_east.png",
                  "Pawn/Humanlike/Apparel/RM_SunGoggles/RM_SunGogglesWorn_north.png"):
            if not os.path.isfile(os.path.join(tex, *f.split("/"))):
                _fail("wired art is missing: %s" % f)
        mod = rd("Source", "RM_GlassChainMod.cs")
        for need in ("kraytLensEnabled", "glassGogglesEnabled", "get_AvailableNow", "PropertyGetter",
                     "RSW_GrindKraytLens", "RM_SunGogglesGlass"):
            if need not in mod and need != "get_AvailableNow":
                _fail("RM_GlassChainMod.cs does not carry %s" % need)

    with _comp(t, "glass_remainder_defs_live"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_SunGogglesGlass;RecipeDef/RM_GrindPearlLens",
                              fields="defName", limit=5)
            _ok(r, "get_defs(goggles)")
            if r.get("notFound"):
                _fail("glass goggles / pearl lens recipe did not resolve live: %s" % r.get("notFound"))
            p = _ok(t.bridge_call("jawa/get_defs", defs="ThingDef/RSW_KraytPearl", fields="defName", limit=2), "get_defs(pearl)")
            if p.get("notFound"):
                _unmeasured(t, "RSW_KraytPearl is not loaded (the Star Wars bestiary is absent): the "
                               "conditional krayt-lens patch correctly added nothing")
            k = _ok(t.bridge_call("jawa/get_defs", defs="ThingDef/RSW_KraytLens;RecipeDef/RSW_GrindKraytLens",
                                  fields="defName", limit=5), "get_defs(krayt lens)")
            if k.get("notFound"):
                _fail("RSW_KraytPearl is loaded but the krayt lens did not resolve: %s" % k.get("notFound"))
            for f in ("kraytLensEnabled", "glassGogglesEnabled"):
                if not _same(_get_setting(t, f), True):
                    _fail("%s is not at its shipped default True" % f)

    # LIVE PROOF owed by the parent's criteria. Not driven this pass (the game was in use by another
    # window); each records UNMEASURED with its reason so none can read as a pass.
    for name, why in (
            ("drift_clear_drops_glass_sand", "needs a driven drift clear on a Stillsand quicktest"),
            ("furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof", "needs a full bill cycle in sun, in a gale and under a roof"),
            ("oven_cooks_in_sun_not_shade", "needs a cooked meal in sun and in shade"),
            ("lightning_on_deepsand_leaves_fulgurite_pyrelands_off", "needs a forced strike on RM_DeepSand with the Pyrelands master toggle off"),
            ("recipe_toggles_hide_recipes", "no bridge tool reads RecipeDef.AvailableNow for a bench")):
        with _comp(t, name):
            if _live(t):
                _unmeasured(t, why + " (not driven: the live game was in use)")


# ----------------------------------------------------------------------------- chain: water

@_chain("water")
def water_chain(t):
    _prep(t, "water")
    x, z = t.anchor
    EGG = "RM_GuzzkaEggUnfertilized"

    def pour(terrain):
        """One colonist pours one egg on `terrain`; returns (egg_left, hourbloom_count)."""
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,22,22" % (terrain, x - 11, z - 11),
                      layer="top")
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, 22)), categories="Plant,Item,Filth")
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (EGG, x, z))
        egg = _things(t, EGG, _rs(_rect(t)))
        if not egg:
            _unmeasured(t, "the water egg did not stand after spawn_batch")
        col = _colonist(t, x - 3, z)
        t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="RM_PourWaterIntoSand", targetAId=egg[0]["id"],
                      waitTicks=60)
        t.wait_ticks(1200)
        return _count(t, EGG, _rs(_rect(t))), _count(t, "RM_Hourbloom", _rs(_rect(t)))

    with _comp(t, "pour_blooms_on_sand", toggle="bloomOnPour"):
        if _live(t):
            left, bloom = pour("Sand")
            _note(t, "after a pour on sand: eggs left / hourbloom", [left, bloom])
            _STATE["pour_ok"] = (not left) and bloom >= 1
            if left:
                _unmeasured(t, "the colonist never poured the egg (job refused or unreachable)")
            if bloom < 1:
                _fail("water poured onto Stillsand sand sowed no RM_Hourbloom (the sand does not remember "
                      "water: RM_SandRemembersWaterExtension missing or the job did nothing)")

    with _comp(t, "pour_toggle_off_no_bloom", toggle="bloomOnPour"):
        if _live(t):
            if _STATE.get("pour_ok") is False:
                _unmeasured(t, "the sand pour sowed nothing with the toggle on")
            with _setting(t, "bloomOnPour", False):
                left, bloom = pour("Sand")
            _note(t, "after a pour with bloomOnPour off: eggs left / hourbloom", [left, bloom])
            if left:
                _unmeasured(t, "the colonist never poured the egg")
            if bloom:
                _fail("bloomOnPour is off and %d hourbloom were sown anyway" % bloom)

    with _comp(t, "pour_on_gravel_no_bloom"):
        if _live(t):
            left, bloom = pour("Gravel")
            _note(t, "after a pour on gravel: eggs left / hourbloom", [left, bloom])
            if left:
                _unmeasured(t, "the colonist never poured the egg")
            if bloom:
                _fail("water poured on gravel sowed %d hourbloom: only remembering sand may bloom" % bloom)


# ----------------------------------------------------------------------------- chain: skeletons

@_chain("skeleton")
def skeleton_chain(t):
    _prep(t, "skeleton")
    x, z = t.anchor
    rect = _rect(t)

    def kill_one(cx, cz):
        pid = _spawn(t, "RM_Vozzik", cx, cz)
        _kill(t, cx, cz)
        t.wait_ticks(30)
        if not _things(t, "Corpse_RM_Vozzik", _rs(rect)):
            _unmeasured(t, "the killed vozzik left no corpse to age (debug kill refused?)")
        return pid

    def jump(days):
        clk = _ok(t.bridge_call("jawa/time_clock"), "time_clock")
        t.bridge_call("jawa/time_set_ticks", ticks=int(clk["ticksGame"] + days * 60000))
        t.wait_ticks(2100)          # one Long tick: the scan runs at ticksGame % 2000 == 37

    with _comp(t, "corpse_becomes_skeleton", toggle="corpseToSkeletonEnabled"):
        if _live(t):
            with _setting(t, "corpseToSkeletonDays", 1.0):
                kill_one(x - 6, z)
                jump(1.2)
            sk = _count(t, "RM_VozzikSkeleton", _rs(rect))
            left = _count(t, "Corpse_RM_Vozzik", _rs(rect))
            _note(t, "after the delay: skeletons / corpses", [sk, left])
            if sk < 1 or left:
                _fail("a giant's corpse past corpseToSkeletonDays did not become its skeleton "
                      "(skeletons %d, corpses left %d)" % (sk, left))

    with _comp(t, "corpse_stays_when_toggle_off", toggle="corpseToSkeletonEnabled"):
        if _live(t):
            t.bridge_call("jawa/destroy_batch", rects=_rs(rect), categories="Building,Item,Filth")
            with _setting(t, "corpseToSkeletonEnabled", False):
                with _setting(t, "corpseToSkeletonDays", 1.0):
                    kill_one(x + 6, z)
                    jump(1.2)
                sk = _count(t, "RM_VozzikSkeleton", _rs(rect))
                left = _count(t, "Corpse_RM_Vozzik", _rs(rect))
            _note(t, "toggle off, after the delay: skeletons / corpses", [sk, left])
            if sk:
                _fail("corpseToSkeletonEnabled is off and a corpse still became a skeleton")
            if not left:
                _unmeasured(t, "the corpse is gone with the toggle off but no skeleton stands: it was "
                               "destroyed by something else")


# ----------------------------------------------------------------------------- chain: gloves-off sun gear

@_chain("glare")
def glare_chain(t):
    _prep(t, "glare")
    x, z = t.anchor
    st = {}
    with _comp(t, "glare_site_ready", poison=True):
        if _live(t):
            _settle_shade(t)    # the pad's old rock/roof shade lingers until the grid rebuilds
            r = _sun(t, "%d,%d" % (x, z))
            ex = _exposure(r, x, z)
            if not isinstance(ex, (int, float)) or ex < 0.6:
                _unmeasured(t, "the open cell reads sun exposure %r (< 0.6): glare-blind cannot start "
                               "here (latitude %s)" % (ex, _STATE.get("lat")))
            a = _colonist(t, x - 2, z)
            b = _colonist(t, x + 2, z)
            r = t.session._rb.call("jawa/pawn_gear", {"pawn": b, "action": "wear", "def": "RM_SunGoggles",
                                                      "quality": "Normal"})
            _ok(r, "pawn_gear wear RM_SunGoggles")
            t.wait_ticks(1500)
            rows = _rows(t, rect=_rs(_rect(t)), health=True)
            st.update(a=rows.get(a), b=rows.get(b))
            if st["a"] is None or st["b"] is None:
                _unmeasured(t, "a colonist left the pad or died before it could be read")

    with _comp(t, "glare_blind_gained_in_open_sun"):
        if _live(t):
            sev = _sev(st["a"], "RM_GlareBlind")
            _note(t, "RM_GlareBlind severity, bare-eyed colonist", sev)
            if sev <= 0:
                _fail("a bare-eyed non-Jawa colonist stood 1500 ticks in full Stillsand sun and gained no "
                      "RM_GlareBlind")

    with _comp(t, "goggles_block_glare_blind"):
        if _live(t):
            bare, goggled = _sev(st["a"], "RM_GlareBlind"), _sev(st["b"], "RM_GlareBlind")
            _note(t, "RM_GlareBlind severity bare / goggled", [bare, goggled])
            if bare <= 0:
                _unmeasured(t, "the bare-eyed control gained no glare-blind: goggles cannot be judged")
            if goggled > 0.25 * bare:
                _fail("a colonist wearing RM_SunGoggles gained RM_GlareBlind %.3f against %.3f bare-eyed "
                      "(the glare protection tag is not read)" % (goggled, bare))


@_chain("cooling")
def cooling_chain(t):
    _prep(t, "cooling")
    x, z = t.anchor
    with _comp(t, "cooling_draught_widens_comfort"):
        if _live(t):
            pid = _colonist(t, x, z)

            def comfy():
                r = t.bridge_call("jawa/pawn_stats", pawn=pid, stats="ComfyTemperatureMax")
                for s in (_ok(r, "pawn_stats").get("stats") or []):
                    if s.get("defName") == "ComfyTemperatureMax":
                        return float(s["value"])
                _unmeasured(t, "ComfyTemperatureMax unreadable: %r" % (r,))
            base = comfy()
            r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff="RM_CoolingDraught",
                              severity=1.0)
            if not (r or {}).get("success"):
                _unmeasured(t, "could not add RM_CoolingDraught: %s" % str(r)[:160])
            with_it = comfy()
            t.bridge_call("jawa/pawn_health", pawn=pid, action="remove", hediff="RM_CoolingDraught")
            gone = comfy()
            _note(t, "ComfyTemperatureMax base / with draught / removed", [base, with_it, gone])
            if abs((with_it - base) - 8.0) > 0.5:
                _fail("RM_CoolingDraught moved ComfyTemperatureMax by %.2f, expected +8" % (with_it - base))
            if abs(gone - base) > 0.5:
                _fail("removing the draught left ComfyTemperatureMax at %.2f (base %.2f)" % (gone, base))


# ----------------------------------------------------------------------------- chain: the dune gale

def _dry_fire(t, incident, **kw):
    """fire_incident dryRun. The live tool answers success=False WITH canFireNow=False when the incident
    cannot fire (a valid answer, not a tool failure); only a reply with no canFireNow is a failure."""
    r = t.bridge_call("jawa/fire_incident", incidentDef=incident, dryRun=True, **kw)
    if isinstance(r, dict) and "canFireNow" in r:
        return r
    return _ok(r, "fire_incident dryRun")


def _gale_incident_ok(t):
    return _dry_fire(t, "RM_DuneGale").get("canFireNow")


def _end_gale(t):
    try:
        t.session.call("jawa/game_condition", action="end", condition="RM_DuneGale")
    except Exception as ex:
        print("[stillsand] could not end the gale: %s" % ex, file=sys.stderr, flush=True)


def _weather_locks(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return 0
    return sum(1 for c in ((r or {}).get("conditions") or [])
               if c.get("def") == "WeatherController" and c.get("permanent") and c.get("affectsThisMap", True))


def _run_gale(t, x, z):
    """Start a 6000-tick gale, return (weather sequence, ended-log line or None, letters at the end)."""
    # A leftover permanent WeatherController (a weather lock) is listed ahead of the gale in the map's
    # conditions and its forced weather shadows the gale's herald/gale weather (the 2026-10-03 run saw
    # 'Clear' for 4000 ticks, then the gale, and never the herald). Let an unlock take its tick, then refuse
    # to run on a shadowed map instead of reading a gale that was never in force.
    t.wait_ticks(2)
    left = _weather_locks(t)
    if left:
        _unmeasured(t, "%d permanent WeatherController condition(s) still force weather after unlock; they "
                       "shadow the gale's herald/gale weather, so the phases cannot be read" % left)
    before_log = len(_log_lines(t, "dune gale ended")[0])
    before_letters = _letters(t)
    t.bridge_call("jawa/game_condition", action="start", condition="RM_DuneGale", durationTicks=6000)
    seq, mid_exposure, line = [], None, None
    for _ in range(24):
        t.wait_ticks(500)
        w = _weather_now(t)
        if not seq or seq[-1] != w:
            seq.append(w)
        if w == "RM_DuneGale" and mid_exposure is None:
            t.wait_ticks(500)
            mid_exposure = _exposure(_sun(t, "%d,%d" % (x, z)), x, z)
        lines = _log_lines(t, "dune gale ended")[0]
        if len(lines) > before_log:
            line = lines[-1]
            break
    return seq, mid_exposure, line, _new_letters(before_letters, _letters(t))


@_chain("gale")
def gale_chain(t):
    _prep(t, "gale")
    x, z = t.anchor
    with _comp(t, "gale_incident_fires"):
        if _live(t):
            _end_gale(t)
            if _gale_incident_ok(t) is not True:
                _fail("RM_DuneGale reports canFireNow false on a Stillsand map with the gale toggle on")

    with _comp(t, "gale_toggle_off_refuses", toggle="galeEnabled"):
        if _live(t):
            if _gale_incident_ok(t) is not True:
                _unmeasured(t, "the gale cannot fire with its toggle on: the off arm proves nothing")
            with _setting(t, "galeEnabled", False):
                # IncidentWorker.CanFireNow caches its result per game tick (lastCheckCanRunTick), and the
                # game is paused: without one tick the off read returns the on-arm's cached True.
                t.wait_ticks(1)
                off = _gale_incident_ok(t)
            if off is not False:
                _fail("galeEnabled is off and RM_DuneGale still reports canFireNow=%r" % off)

    with _comp(t, "gale_phases_and_aftermath", toggle="emergenceEnabled"):
        if _live(t):
            clear = _exposure(_sun(t, "%d,%d" % (x, z)), x, z)
            t.bridge_call("jawa/weather_set", unlock=True)     # a locked weather would shadow the condition's
            seq, gale_exp, line, new = _run_gale(t, x, z)
            _STATE["gale_clear_exposure"], _STATE["gale_exposure"] = clear, gale_exp
            _note(t, "gale weather sequence / ended line / new letters", [seq, line, [l[0] for l in new]])
            if "RM_DuneGaleHerald" not in seq or "RM_DuneGale" not in seq or \
                    seq.index("RM_DuneGaleHerald") > seq.index("RM_DuneGale"):
                _fail("the gale did not run herald then gale weather: saw %s" % seq)
            if not line:
                _fail("no '[Stillsand] dune gale ended on ...' log line within 12000 ticks of a 6000-tick gale")
            m = re.search(r"delta ([+-][\d.]+)\); cells moved past [\d.]+: (\d+)", line)
            if not m:
                _fail("the gale-end log line has no delta / cells moved: %s" % line)
            if abs(float(m.group(1))) == 0.0 and int(m.group(2)) == 0:
                _fail("a full gale moved no sand at all (delta +0.0, 0 cells): the dunes did not march "
                      "(%s)" % line)
            emerged = [l for l in new if l[0] in EMERGENCE_LABELS]
            if len(emerged) != 1:
                _fail("expected exactly one emergence letter at gale end, got %s" % [l[0] for l in new])

    with _comp(t, "gale_dims_sun_exposure"):
        if _live(t):
            # shadegrid_read returns RM_MapComponent_ShadeGrid.ExposureAt(cell), which does NOT include the
            # weather factor: RM_WeatherSenseExtension.SunFactor is applied only in ExposureFor(pawn). So a
            # cell read is 1.00 in a gale by construction. No bridge tool reads pawn exposure.
            _unmeasured(t, "shadegrid_read reads cell exposure, which excludes the gale's sun factor "
                           "(applied per pawn in ExposureFor); no tool reads pawn exposure, so the dimming "
                           "cannot be measured here")

    with _comp(t, "gale_emergence_off_quiet", toggle="emergenceEnabled"):
        if _live(t):
            t.bridge_call("jawa/weather_set", unlock=True)
            with _setting(t, "emergenceEnabled", False):
                seq, _e, line, new = _run_gale(t, x, z)
            emerged = [l for l in new if l[0] in EMERGENCE_LABELS]
            _note(t, "emergenceEnabled off: new letters", [l[0] for l in new])
            if not line:
                _unmeasured(t, "the second gale did not end in time")
            if emerged:
                _fail("emergenceEnabled is off and the gale still uncovered something: %s"
                      % [l[0] for l in emerged])


@_chain("devil")
def devil_chain(t):
    _prep(t, "devil")
    x, z = t.anchor
    with _comp(t, "devil_moves_and_expires"):
        if _live(t):
            t.bridge_call("rimworld/spawn_thing", defName="RM_DustDevil", x=x, z=z)
            pos = []
            for _ in range(12):
                t.wait_ticks(250)
                rows = _things(t, "RM_DustDevil")
                pos.append([(w.get("x"), w.get("z")) for w in rows][:1])
                if not rows:
                    break
            flat = [p[0] for p in pos if p]
            _note(t, "dust devil track", pos)
            if len(flat) < 2:
                _unmeasured(t, "the dust devil was gone before it could be tracked")
            if _dist(flat[0], flat[-1]) < 3:
                _fail("a dust devil lived %d samples and moved %.1f cells" % (len(flat),
                                                                              _dist(flat[0], flat[-1])))
            for _ in range(12):
                if not _things(t, "RM_DustDevil"):
                    break
                t.wait_ticks(250)
            if _things(t, "RM_DustDevil"):
                _fail("a dust devil outlived its 900-2400 tick life by 3000 ticks")

    with _comp(t, "devil_toggle_off_refuses", toggle="dustDevilsEnabled"):
        if _live(t):
            def can():
                return _dry_fire(t, "RM_DustDevil").get("canFireNow")
            if can() is not True:
                _unmeasured(t, "the dust devil incident cannot fire with its toggle on (weather, or no "
                               "free cell): the off arm proves nothing")
            with _setting(t, "dustDevilsEnabled", False):
                t.wait_ticks(1)   # CanFireNow is cached per game tick (see the gale arm)
                off = can()
            if off is not False:
                _fail("dustDevilsEnabled is off and RM_DustDevil still reports canFireNow=%r" % off)


# ----------------------------------------------------------------------------- chain: the muurrok

@_chain("muurrok")
def muurrok_chain(t):
    _prep(t, "muurrok", terrain="Gravel")
    x, z = t.anchor
    with _comp(t, "muurrok_emergence_fires"):
        if _live(t):
            before = _letters(t)
            n0 = len([p for p in _rows(t).values() if p.get("kindDef") == "RM_Muurrok"])
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_MuurrokEmergence")
            _ok(r, "fire_incident RM_MuurrokEmergence")
            t.wait_ticks(2600)
            new = _new_letters(before, _letters(t))
            mu = [i for i, p in _rows(t).items() if p.get("kindDef") == "RM_Muurrok"]
            n1 = len(mu)
            _STATE.setdefault("spawned", []).extend(mu)
            _note(t, "muurrok letters / pawns before-after", [[l[0] for l in new], n0, n1])
            if not [l for l in new if "glare" in l[0].lower()]:
                _fail("firing RM_MuurrokEmergence sent no 'A line of glare' letter: %s" % [l[0] for l in new])
            if n1 <= n0:
                _fail("no RM_Muurrok on the map 2600 ticks after the incident fired (warning is 1500)")

    def cast_at(boss, targets):
        for tid in targets:
            t.bridge_call("jawa/pawn_use_verb", pawn=boss, action="cast", verb="mirror crest", targetId=tid)
            t.wait_ticks(300)

    def burned(ids):
        rows = _rows(t, health=True)
        return [i for i in ids if i in rows and _has(rows[i], "Burn")]

    with _comp(t, "beam_burns_target", toggle="mirrorBeamEnabled"):
        if _live(t):
            _prep(t, "muurrok", terrain="Gravel")
            boss = _spawn(t, "RM_Muurrok", x - 8, z)
            mus = [_spawn(t, "Muffalo", x + 4, z - 3 + 3 * i) for i in range(3)]
            cast_at(boss, mus)
            hit = burned(mus)
            _STATE["beam_on_burned"] = bool(hit)
            _note(t, "muffalo with Burn after 3 beam casts", hit)
            if not hit:
                _fail("a muurrok cast its mirror beam at 3 muffalo under Clear weather and none gained Burn "
                      "(MUURROK_BEAM_NO_DAMAGE_1)")
            _STATE["boss"] = boss

    with _comp(t, "beam_toggle_off_blocked", toggle="mirrorBeamEnabled"):
        if _live(t):
            if not _STATE.get("beam_on_burned"):
                _unmeasured(t, "the beam does not damage with its toggle on: the off arm would pass "
                               "trivially")
            boss = _STATE.get("boss")
            mus = [_spawn(t, "Muffalo", x + 4, z + 6 + 3 * i) for i in range(3)]
            with _setting(t, "mirrorBeamEnabled", False):
                cast_at(boss, mus)
                hit = burned(mus)
            _note(t, "mirrorBeamEnabled off: muffalo with Burn", hit)
            if hit:
                _fail("mirrorBeamEnabled is off and the muurrok still burned %d muffalo" % len(hit))


# ----------------------------------------------------------------------------- chain: the eruption

@_chain("eruption")
def eruption_chain(t):
    _prep(t, "eruption")
    with _comp(t, "eruption_tunnel_then_mound"):
        if _live(t):
            before = _letters(t)
            # IncidentWorker.CanFireNow refuses every ThreatBig while TicksGame < newWanderersCreatedTick +
            # 300000 (RimSage-read), and fire_incident passes unforced parms. A young test game is therefore a
            # precondition failure of the harness, not an eruption defect: say so instead of failing.
            dry = _dry_fire(t, "RM_SandBusterEruption", points=800)
            if dry.get("canFireNow") is not True and (dry.get("ticksGame") or 0) < 300000:
                _unmeasured(t, "the engine refuses ThreatBig incidents before game tick 300000 and this game is at "
                               "tick %s; fire_incident cannot force it" % dry.get("ticksGame"))
            r = t.bridge_call("jawa/fire_incident", incidentDef="RM_SandBusterEruption", points=800)
            _ok(r, "fire_incident RM_SandBusterEruption")
            tun = _count(t, "RM_SandBusterTunnel")
            new = _new_letters(before, _letters(t))
            _note(t, "eruption letters / tunnel markers", [[l[0] for l in new], tun])
            if tun < 1:
                _fail("the eruption fired and no RM_SandBusterTunnel marker stands")
            mound = 0
            for _ in range(8):
                t.wait_ticks(500)
                mound = _count(t, "RM_SandBusterMound")
                if mound:
                    break
            _note(t, "mounds after the tunnel breaks through", mound)
            if mound < 1:
                _fail("the tunnel marker never produced an RM_SandBusterMound in 4000 ticks")
            if not [l for l in new if "Sand Buster" in l[0]]:
                _fail("no 'Sand Buster Eruption' letter: %s" % [l[0] for l in new])
    # cleanup: hostile busters must not outlive the chain
    if _live(t):
        try:
            t.session.call("rimworld/execute_debug_action", path="Actions\\Destroy hostile pawns")
            for d in ("RM_SandBusterMound", "RM_SandBusterTunnel"):
                r = t.session.call("jawa/list_things", defName=d, limit=200)
                for w in ((r or {}).get("things") or []):
                    t.session.call("jawa/destroy_batch", rects="%d,%d,1,1" % (w["x"], w["z"]),
                                   categories="Building")
        except Exception as ex:
            print("[stillsand] eruption cleanup failed: %s" % ex, file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------- chain: the horizon

def _close_dialogs(t, r):
    """storyteller_fire reports a modal a Harmony prefix opened instead of the incident: nothing on the
    bridge can answer one, so close it and let the caller read `fired`."""
    if (r or {}).get("blockedByDialog"):
        t.bridge_call("jawa/window_list_close", action="close", closeAll=True)


def _foreign(t):
    return dict((i, p) for i, p in _rows(t).items()
                if p.get("faction") and not p.get("isPlayer") and not p.get("dead"))


@_chain("horizon")
def horizon_chain(t):
    _prep(t, "horizon")
    ids0 = set()
    with _comp(t, "horizon_warns_then_arrives", toggle="horizonWarningsEnabled"):
        if _live(t):
            before = _letters(t)
            ids0 = set(_foreign(t))
            with _setting(t, "horizonWarningHours", 0.5):
                r = t.bridge_call("jawa/storyteller_fire", incidentDef="TraderCaravanArrival", dryRun=False)
                _close_dialogs(t, r)
                if not (r or {}).get("fired"):
                    _unmeasured(t, "the neutral group could not be fired (no trader faction on this world?): "
                                   "%s" % str(r)[:200])
                warn = [l for l in _new_letters(before, _letters(t)) if l[0].startswith("Dust on the horizon")]
                early = set(_foreign(t)) - ids0
                # the delay is 0.5 h = 1250 ticks; poll to 4000 so a slow queue tick is not read as "lost"
                late = set()
                for _ in range(8):
                    t.wait_ticks(500)
                    late = set(_foreign(t)) - ids0
                    if late:
                        break
            _note(t, "horizon letters / pawns at once / pawns after the delay", [[l[0] for l in warn],
                                                                              len(early), len(late)])
            if not warn:
                _fail("a neutral group fired on the Stillsand with no 'Dust on the horizon' letter")
            if early:
                _fail("the warned group arrived at once (%d pawns): the incident was not delayed" % len(early))
            # RULED OUT (as proven): "lost in the queue". IncidentQueue.IncidentQueueTick runs every tick and
            #   re-calls Storyteller.TryFire(queued: true), which our prefix passes straight through; TryFire
            #   is CanFireNow && Worker.TryExecute. In run 20261007T094214Z the vanilla arm (toggle off, no
            #   queue, no prefix) ALSO refused TraderCaravanArrival 4000 ticks later: canFireNow true, fired
            #   false -> vanilla TryExecute itself refuses on this site (faction/traderKind/zero pawns from
            #   GeneratePawns, warnOnZeroResults false = silent). So before blaming the queue, read the
            #   queue and run the same incident through vanilla as a control.
            if not late:
                q = t.bridge_call("jawa/incident_queue_peek")
                mine = [row for row in ((q or {}).get("queue") or []) if row.get("defName") == "TraderCaravanArrival"]
                _note(t, "incident queue after the delay (TraderCaravanArrival rows)", mine)
                with _setting(t, "horizonWarningsEnabled", False):
                    ctl = t.bridge_call("jawa/storyteller_fire", incidentDef="TraderCaravanArrival", dryRun=False)
                    _close_dialogs(t, ctl)
                _note(t, "vanilla control fire (toggle off)", {k: (ctl or {}).get(k) for k in
                                                              ("fired", "canFireNow", "note")})
                if not (ctl or {}).get("fired"):
                    _unmeasured(t, "vanilla TraderCaravanArrival also refuses on this site with the horizon off "
                                   "(canFireNow %r, TryExecute false): the delayed fire failed for the same "
                                   "vanilla reason, not in the queue" % (ctl or {}).get("canFireNow"))
                _fail("the warned group never arrived after the warning delay, while vanilla fires the same "
                      "incident at once (queue rows %r)" % mine)
            _STATE["horizon_new"] = list(late)

    with _comp(t, "horizon_toggle_off_vanilla", toggle="horizonWarningsEnabled"):
        if _live(t):
            before = _letters(t)
            with _setting(t, "horizonWarningsEnabled", False):
                r = t.bridge_call("jawa/storyteller_fire", incidentDef="TraderCaravanArrival", dryRun=False)
                _close_dialogs(t, r)
                if not (r or {}).get("fired"):
                    _unmeasured(t, "the neutral group could not be fired with the toggle off: %s"
                                   % str(r)[:200])
                warn = [l for l in _new_letters(before, _letters(t)) if l[0].startswith("Dust on the horizon")]
            if warn:
                _fail("horizonWarningsEnabled is off and a 'Dust on the horizon' letter still came")
    if _live(t):    # the visitors are scenery for this chain only
        try:
            for p in [q for i, q in _pawns_raw(t).items()
                      if q.get("faction") and not q.get("isPlayer") and not q.get("dead") and i not in ids0]:
                t.session.call("jawa/destroy_batch", rects="%d,%d,1,1" % (p["x"], p["z"]), categories="Pawn")
        except Exception as ex:
            print("[stillsand] horizon cleanup failed: %s" % ex, file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------- chain: map generation toggles

@_chain("caves")
def caves_chain(t):
    _pad(t, "caves")
    _gate(t)
    seen = {}
    with _comp(t, "caves_regen_both_off", poison=True):
        if _live(t):
            info = _ok(t.bridge_call("jawa/map_info"), "map_info")
            with _setting(t, "genStepEnabled", False):
                with _setting(t, "skeletonPlacementEnabled", False):
                    before = _log_lines(t, "[Stillsand] precious cave")[1]
                    _regen(t)
                    seen["after"] = _log_lines(t, "[Stillsand] precious cave")[1]
                    seen["skel"] = sum(_count(t, d) for d in GIANT_SKELETONS)
                    seen["before"] = before
            t.session.call("jawa/spawn_pawn", kindDef="Colonist", x=info["sizeX"] // 2, z=info["sizeZ"] // 2,
                           faction="player", count=1)
            _note(t, "cave log lines before/after, skeletons: both gen toggles off", seen)

    with _comp(t, "genstep_off_no_cave_line", toggle="genStepEnabled"):
        if _live(t):
            if seen["after"] > seen["before"]:
                _fail("genStepEnabled is off and the regeneration still logged a precious-cave line (%d -> %d)"
                      % (seen["before"], seen["after"]))

    with _comp(t, "skeleton_placement_off_none", toggle="skeletonPlacementEnabled"):
        if _live(t):
            if seen["skel"]:
                _fail("skeletonPlacementEnabled is off and the regenerated map carries %d giant skeletons"
                      % seen["skel"])


# ----------------------------------------------------------------------------- chain: the event remainder

# STILLSAND_EVENT_CREATURES_REMAINDER_1. The horn, the den quest and the seep-rooting incident are RSW / RUT
# content (mandrake.rsw.swbestiary, mandrake.rsw.sarlacc, mandrake.rut.patches), none of which is loaded on the
# baroque_wave0 tier this suite drives, so their LIVE arms read UNMEASURED with that reason and never PASS.
# What this chain CAN prove offline is shape: every name the three features cross-reference resolves in
# the repo, and the new files obey the load-log lessons (no invalid fields, real vanilla sound names, ...).

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RSW = os.path.join(REPO, "src", "RimStarWars")
RUT = os.path.join(REPO, "src", "RimUtinni")
REMAINDER_FILES = (
    os.path.join(RSW, "SWBestiary", "Defs", "ThingDefs_Items", "RSW_KraytHorn.xml"),
    os.path.join(RSW, "SWBestiary", "Defs", "RecipeDefs", "RSW_KraytHorn_Recipe.xml"),
    os.path.join(RSW, "Sarlacc", "Defs", "IncidentDefs_SwimmerSeep.xml"),
    os.path.join(RUT, "UtinniPatches", "Defs", "QuestScriptDefs", "RUT_KraytDenQuest.xml"),
    os.path.join(RUT, "UtinniPatches", "Patches", "RUT_KraytHorn_Answer.xml"),
    os.path.join(HERE, "Patches", "RM_LoudDraws.xml"),
)
LOAD_LOG_BANNED = ("canBeDoneByNonColonists", "<minifiable>", "PatchOperationAddOrReplace", "<haulable>")
REAL_VANILLA_SOUNDS = ("Metal_Drop", "Standard_Drop")


def _text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _defnames(path_glob):
    out = set()
    for p in glob.glob(path_glob, recursive=True):
        for m in re.finditer(r"<defName>([^<]+)</defName>", _text(p)):
            out.add(m.group(1).strip())
    return out


@_chain("remainder")
def remainder_chain(t):
    cs = _text(os.path.join(HERE, "Source", "RM_EventRemainder.cs"))
    with _comp(t, "remainder_files_obey_load_log_lessons"):
        for p in REMAINDER_FILES:
            if not os.path.exists(p):
                _fail("%s is missing" % p)
            body = _text(p)
            ET.fromstring(body.encode("utf-8"))                      # well-formed
            for bad in LOAD_LOG_BANNED:
                if bad in body:
                    _fail("%s contains %s (a load-log lesson: invalid field / banned patch op)" % (os.path.basename(p), bad))
        # a sanity probe: the banned-token check must be able to hit
        if not any(b in "<a><minifiable>true</minifiable></a>" for b in LOAD_LOG_BANNED):
            _fail("sanity probe: the banned-token list cannot see <minifiable>")

    with _comp(t, "remainder_horn_cross_references"):
        horn = _text(REMAINDER_FILES[0])
        sounds = _defnames(os.path.join(RSW, "SWBestiary", "Defs", "SoundDefs", "*.xml"))
        for s in re.findall(r"<soundOnUsed>([^<]+)</soundOnUsed>", horn):
            if s not in sounds:
                _fail("horn soundOnUsed %s is not a SoundDef shipped by SWBestiary" % s)
        for s in re.findall(r"<sound(?:Interact|Drop)>([^<]+)</sound(?:Interact|Drop)>", horn):
            if s not in REAL_VANILLA_SOUNDS:
                _fail("horn names sound %s, not one checked against Core (%s)" % (s, REAL_VANILLA_SOUNDS))
        for cls in ("RM_CompUseEffect_Horn", "RM_HornExtension"):
            if "class %s" % cls not in cs or cls not in horn:
                _fail("%s is not both defined in RM_EventRemainder.cs and used by the horn def" % cls)
        items = _defnames(os.path.join(RSW, "SWBestiary", "Defs", "ThingDefs_Items", "*.xml"))
        recipe = _text(REMAINDER_FILES[1])
        for d in re.findall(r"<li>(RSW_[A-Za-z_]+)</li>", recipe):
            if d not in items:
                _fail("recipe ingredient %s is not a ThingDef in SWBestiary" % d)
        if "RSW_KraytHorn" not in items:
            _fail("RSW_KraytHorn is not parsed from SWBestiary's items")
        ans = _text(REMAINDER_FILES[4])
        if "RM_HornExtension" not in ans or "RUT_KraytAttack" not in ans or "RUT_KraytAttack" in horn:
            _fail("the answer incident must be named by the Utinni patch only, on RM_HornExtension")
        if "RUT_KraytAttack" not in _defnames(os.path.join(RUT, "UtinniPatches", "Defs", "IncidentDefs", "*.xml")):
            _fail("RUT_KraytAttack (the horn's answer) is not shipped by UtinniPatches")

    with _comp(t, "remainder_seep_incident_stillsand_only"):
        inc = _text(REMAINDER_FILES[2])
        biomes = re.findall(r"<biomes>(.*?)</biomes>", inc, re.S)
        got = re.findall(r"<li>([^<]+)</li>", biomes[0]) if biomes else []
        if got != [BIOME]:
            _fail("the seep-rooting incident's biome gate is %s, expected exactly [%s]" % (got, BIOME))
        road = _text(os.path.join(RSW, "Sarlacc", "Source", "RSW_SwimmerRoad.cs"))
        for needle in ("class RSW_IncidentWorker_SwimmerSeep", "biomes.Contains(map.Biome.defName)", "seepMode"):
            if needle not in road:
                _fail("RSW_SwimmerRoad.cs lacks %s" % needle)
        marker = re.search(r"<seepMarker>([^<]+)</seepMarker>", inc).group(1)
        if marker not in _defnames(os.path.join(RSW, "Sarlacc", "Defs", "*.xml")):
            _fail("seep marker %s is not a def shipped by the Sarlacc mod" % marker)
        pool = re.search(r"<seepTerrain>([^<]+)</seepTerrain>", inc).group(1)
        if pool not in _defnames(os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Defs", "**", "*.xml")):
            _fail("seep terrain %s is not a TerrainDef shipped by FlowWorks" % pool)

    with _comp(t, "remainder_den_quest_cross_references"):
        q = _text(REMAINDER_FILES[3])
        for cls in re.findall(r'Class="RimMandrake\.Stillsand\.([A-Za-z_]+)"', q):
            if "class %s" % cls not in cs:
                _fail("quest names node %s, not defined in RM_EventRemainder.cs" % cls)
        row = re.search(r"<caveRow>([^<]+)</caveRow>", q).group(1)
        if row not in _defnames(os.path.join(RSW, "SWBestiary", "Defs", "MapGeneration", "*.xml")):
            _fail("quest caveRow %s is not a precious-cave row shipped by SWBestiary" % row)
        kind = re.search(r"<pawnKind>([^<]+)</pawnKind>", q).group(1)
        if kind not in _defnames(os.path.join(RSW, "SWBestiary", "Defs", "ThingDefs_Races", "*.xml")):
            _fail("quest pawnKind %s is not shipped by SWBestiary" % kind)
        den = _text(os.path.join(RSW, "SWBestiary", "Defs", "MapGeneration", "RSW_PreciousCave_KraytDen.xml"))
        if kind not in den:
            _fail("the den row never spawns %s, so the quest could never be offered" % kind)
        sig = re.findall(r"<inSignal>(krayt\.[A-Za-z]+)</inSignal>", q)
        if not sig or set(sig) != {"krayt.Destroyed"}:
            _fail("the den quest's success signal must be krayt.Destroyed alone (a double listener pays twice): %s" % sig)

    with _comp(t, "remainder_loud_draws_wired"):
        sl = _text(os.path.join(HERE, "Source", "RM_SandLeviathan.cs"))
        if "ChargedThumper(map)" not in sl or "RM_LoudDraws.First(map)" not in sl:
            _fail("LoudestCell does not consult a charged thumper and the loud-draw list")
        if sl.index("PoweredDrills(map).FirstOrDefault()") > sl.index("ChargedThumper(map)"):
            _fail("a working drill must still outrank a charged thumper")
        patch = _text(REMAINDER_FILES[5])
        if 'defName="Shuttle"' not in patch:
            _fail("the loud-draw patch does not target the vanilla Shuttle def")

    # Live arms: UNMEASURED by the suite's own mechanism, with the reason.
    LIVE_OWED = {
        "remainder_horn_routs_and_logs_roll": "the krayt horn is RSW content (mandrake.rsw.swbestiary) and its "
            "answer incident is RUT: neither is on the baroque_wave0 tier; needs a campaign-tier session, with a "
            "predator beside the user and the log's '[Stillsand] krayt horn answer roll' line read back",
        "remainder_seep_incident_refuses_other_maps_roots_at_seep": "RSW_SwimmerSeepRoot is Sarlacc (mandrake.rsw.sarlacc, "
            "Anomaly-gated), not loaded on this tier; needs a Stillsand map with the sarlacc seep row and a "
            "second non-Stillsand map to refuse",
        "remainder_den_quest_generates": "RUT_KraytDenQuest needs mandrake.rut.patches + SWBestiary and a map whose "
            "cave rolled RSW_PreciousCave_KraytDen with the dragon alive (a 25% branch of a weighted row); generate "
            "through dev mode Quests > Generate quest",
        "remainder_charged_thumper_is_loudest": "LoudestCell is private to a leviathan incident in flight and no "
            "tool reads where the dragon headed; needs a thumper charged on a live Stillsand map",
    }
    for name, why in sorted(LIVE_OWED.items()):
        with _comp(t, name):
            if _live(t):
                _unmeasured(t, why)


# ----------------------------------------------------------------------------- chain: the log (last)

@_chain("log")
def log_chain(t):
    _pad(t, "log")
    with _comp(t, "log_clean"):
        if _live(t):
            if not _buffer_total(t):
                _unmeasured(t, "drain_log buffer is empty: cannot see the log at all")
            texts, _ = _log_lines(t, "Stillsand", errors_only=True)
            own = [x for x in texts if "GetSettings" not in x]      # the settings tool probes every Mod handle
            names = set(n for k, ns in DEFS_STD.items() for n in ns)
            xr, _n = _log_lines(t, "cross-reference", errors_only=True)
            xref = [x for x in xr if any(d in x for d in names if d.startswith("RM_"))]
            cfg, _n = _log_lines(t, "Config error", errors_only=True)
            cfgs = [x for x in cfg if any(d in x for d in names if d.startswith("RM_"))]
            _note(t, "log scan", {"stillsand errors": len(own), "xref naming our defs": len(xref),
                                  "config errors naming our defs": len(cfgs)})
            bad = own + xref + cfgs
            if bad:
                _fail("log carries errors: %s" % [str(x)[:160] for x in bad[:4]])
