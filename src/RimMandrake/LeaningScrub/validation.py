"""validation.py -- modcheck suite for RimMandrake: Leaning Scrub (mandrake.rm.leaningscrub).

Item LEANING_SCRUB_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/LeaningScrub.md
(`## must be true` lines, each ending in `-> chain.component` or `-> UNCOVERED: why`).
Process: design/RimMandrake/debug_process.md (a first script = a modcheck Suite + a walk).

PACKAGING. This dev folder is the SOURCE only. The biome ships COMPOSED inside
`mandrake.rm.biomes` (Biomes.compose.json), which also carries the EnvironmentalHazards kit this
mod depends on. Drive the `baroque_wave0` tier (northstar_plan.py), never the dev folder's own
packageId: `modcheck run LeaningScrub` would swap to a list without the composed biome.

WHAT THE SUITE READS. Every defName this mod ships is parsed from its own Defs/ at import (so a
new def is covered without an edit) and must RESOLVE live: a def whose comp/extension type is
missing is discarded silently by the engine, and only a live get_defs sees that. The mechanics
are read as STATE through the bridge (positions, jobs, hediffs, inspect strings, plant counts,
turbine output); nothing here judges appearance and no component takes a screenshot.

EVERY CHECK CAN FAIL. Each PASS predicate has an arm that goes the other way inside the same
chain (a control animal that must move, a roofed pawn that must stay clean, a toggle-off arm,
a poised plant that must NOT strike while the toggle is off), so a harness that sees nothing
records UNMEASURED, never PASS. `selftest_leaningscrub.py` runs the suite against a scripted
fake game, healthy and with each mod behaviour broken in turn, and proves the right component
(and only that one) goes red.

NOT DRIVEN HERE (walk lines say UNCOVERED, with the reason):
  * The Lean (heading lock, scent flee, downwind fire): applies only on a map whose BIOME carries
    RM_LeanExtension, and RM_MapComponent_Lean caches that answer on first use. The baroque_wave0
    quicktest map is not a Scrub map; making one needs the Pyrelands-style site recipe (re-tile a
    scratch-world tile, generate its map) -- LEANING_SCRUB_LEAN_SITE_1.
  * Raid weighting under the Gale: a statistical effect on the storyteller (debug_process.md
    section 4, "performance, intermittent, statistical"); only the patch being ARMED is checked.
  * Venomvine passability on this biome: needs a huge pawn pathing through a thicket (the
    EnvironmentalHazards script owns the barrier); here the toggle is checked read/write only.
  * Flyer flight in the air: never live-tested unattended (CLAUDE.md, three times). Only
    `canEverFly` is read, from `jawa/pawn_flight report`.
  * Appearance (the leaning canopy, the Stall's stillness): visual, left to the judge pass.

Settings fields are `public static` (RimMandrake.LeaningScrub.RM_LeaningScrubSettings). Every arm
that changes one restores it in a `finally`. `jawa/mod_settings_field` never writes ModSettings.xml.
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
# (50, 50); the pads below reach 45 cells from it, so spawns landed "Cell is outside the map" (LIVE 2026-10-03). The
# margin makes the runner choose an anchor with that much room on every side.
suite = Suite("LeaningScrub")
suite.anchor_margin = 60

SETTINGS = "RimMandrake.LeaningScrub.RM_LeaningScrubSettings"
HERE = os.path.dirname(os.path.abspath(__file__))

# Shipped defaults, read off RM_LeaningScrubMod.cs (public static field initialisers).
DEFAULTS = {
    "modEnabled": True, "venomvinePassabilityEnabled": True,
    "stallFreezeEnabled": True, "stallFreezeMaxBodySize": 0.5,
    "galeDeafenEnabled": True, "galeTurbineSurgeEnabled": True, "galeTurbineSurgeFactor": 1.3,
    "galeTurbineBreakdownMtbDays": 3.0, "galeRaidWeightingEnabled": True, "galeRaidWeightFactor": 2.0,
    "twitcherLashEnabled": True, "twitcherLashDamageFactor": 1.0, "twitcherLashRecoveryFactor": 1.0,
    "smotherCraftEnabled": True, "smotherDays": 30.0, "smotherYieldFactor": 1.0,
    "leanEnabled": True, "leanScentEnabled": True, "leanScentRange": 16.0, "leanFireEnabled": True,
    "leanFireBias": 0.5,
    "drippingRegrowEnabled": True, "crownMobEnabled": True, "runwayBloomEnabled": True,
    "sweetlineStationsEnabled": True, "sweetlineVisitorsEnabled": True, "sweetlineVisitIntervalDays": 8.0,
    "visslerArmFoodEnabled": True,
    "sweetlineGuardiansEnabled": True, "sweetlineGuardianMaxPerTree": 3, "sweetlineHarvestDisturbance": 1.0,
    "sweetlineForgivenessDays": 5.0, "sweetlineProximityCharge": False,
    "sweetlineScratchingEnabled": True, "sweetlineCoatReady": 0.8, "sweetlineFeltShare": 0.2,
    "sweetlineTreeMapChance": 0.25, "sweetlineFeltComfortEnabled": True, "sweetlineFeltApparelEnabled": True,
    "fireStampEnabled": True,
    # LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1 (RM_VenomvineForms.cs)
    "rearingEnabled": True, "rearingHours": 2.0, "walkingEnabled": True, "walkingMaxCellsPerMap": 120,
    "hoardEnabled": True, "hoardGrowInHours": 4.0, "hoardKeepsDeadGear": True,
    "quenchEnabled": True, "quenchRecoveryDays": 3.0, "swornSparesMarkedEnabled": True,
    "sheddingEnabled": True, "sheddingLength": 8,
}
suite.toggles = sorted(k for k, v in DEFAULTS.items() if isinstance(v, bool))

# Pad offsets from the map centre (the driver's anchor); each chain clears its own pad first.
PADS = {"stall": (-45, -45), "gale": (0, -45), "lash": (45, -45), "smother": (-45, 0),
        "dripping": (45, 0), "crown": (-45, 45), "bloom": (0, 45), "sweetline": (45, 45),
        "fuel": (0, -20), "spawn": (0, 20)}
PAD_SIZE = 24
SOIL = "Soil"

# The five Harmony rules (RM_WindCalendarPatches, RM_TheLeanPatches): type, method, kind, patch name.
RULES = (
    ("JobGiver_Wander", "TryGiveJob", "prefixes", "RM_WindCalendarPatches.Wander_Prefix"),
    ("CompPowerPlantWind", "get_DesiredPowerOutput", "postfixes", "RM_WindCalendarPatches.WindOutput_Postfix"),
    ("IncidentWorker", "ChanceFactorNow", "postfixes", "RM_WindCalendarPatches.ChanceFactorNow_Postfix"),
    ("JobGiver_AnimalFlee", "TryGiveJob", "postfixes", "RM_TheLeanPatches.AnimalFlee_Postfix"),
    ("Fire", "TrySpread", "prefixes", "RM_TheLeanPatches.TrySpread_Prefix"),
    ("Thing", "get_IngestibleNow", "postfixes", "RM_VisslerArmPatches.IngestibleNow_Postfix"),
)
HARMONY_OWNER = "mandrake.rm.leaningscrub"

# The runway bloom's four answering species (RM_RunwayBloomExtension on each race def).
BLOOM_SPECIES = ("RM_Crustweevil", "RM_Fuzzrunner", "RM_Dustflutter", "RM_Vissler")
STALL_SMALL, STALL_BIG = "RM_Thornhold", "RM_Shirrel"    # baseBodySize 0.4 (< 0.5) and 0.7 (> 0.5)

_STATE = {}    # readings shared between components of ONE run


# --------------------------------------------------------------------------- shipped defs

def _read_defs():
    """{defType: [defName]} and {defName: ParentName} for every concrete def in this mod's Defs/,
    parsed per top-level element (never a fixed line number). Comments are stripped first."""
    wanted = ("ThingDef", "PawnKindDef", "WeatherDef", "HediffDef", "JobDef", "RecipeDef",
              "RulePackDef", "BiomeDef", "ResearchProjectDef")
    by_type, parent = {}, {}
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<(%s)\b([^>]*)>(.*?)</\1>" % "|".join(wanted), txt, re.S):
            kind, attrs, body = m.group(1), m.group(2), m.group(3)
            if re.search(r'Abstract\s*=\s*"[Tt]rue"', attrs):
                continue
            nm = re.search(r"<defName>([^<]+)</defName>", body)
            if not nm:
                continue
            by_type.setdefault(kind, []).append(nm.group(1).strip())
            pn = re.search(r'ParentName\s*=\s*"([^"]+)"', attrs)
            parent[nm.group(1).strip()] = pn.group(1) if pn else None
    return by_type, parent


def _polluted_only():
    """Plant defNames whose <plant><pollution> is PollutedOnly (PlantUtility.CanEverPlantAt rejects them on a
    clean cell, so set_plants answers REJECTED 'terrain or conditions cannot support')."""
    out = set()
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<ThingDef\b[^>]*>(.*?)</ThingDef>", txt, re.S):
            nm = re.search(r"<defName>([^<]+)</defName>", m.group(1))
            if nm and re.search(r"<pollution\b[^>]*>\s*PollutedOnly\s*</pollution>", m.group(1)):
                out.add(nm.group(1).strip())
    return out


DEFS_BY_TYPE, _PARENT = _read_defs()
POLLUTED_ONLY = _polluted_only()          # RM_Grellspine (vanilla grayscrub's rule)
SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_BY_TYPE.items() for n in ns)
PLANTS = [n for n in DEFS_BY_TYPE.get("ThingDef", [])
          if _PARENT.get(n) in ("PlantBase", "PlantBaseNonEdible")]            # not the tree
KINDS = DEFS_BY_TYPE.get("PawnKindDef", [])
FORM_PLANTS = ("RM_RearingVenomvine", "RM_WalkingVenomvine", "RM_HoardVenomvine", "RM_QuenchVenomvine",
               "RM_SwornVenomvine", "RM_SheddingVenomvine")     # LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1
TREE = "RM_SweetlineTree"


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
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail
    names the real reason, and the chain is not poisoned for an independent next component.
    `poison=True` (a site-setup component) keeps the chain failed, so every later component
    of that chain records UNMEASURED instead of running on a half-built site."""
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
        print("[lscrub] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[lscrub-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
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


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _prep(t, name, size=PAD_SIZE):
    """Clear the pad and lay plain soil so everything stands on walkable, plantable ground."""
    _pad(t, name)
    if _live(t):
        try:    # neutral until a chain locks its own; never let this abort the chain
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        except Exception as ex:
            print("[lscrub] neutral weather not set: %s" % ex, file=sys.stderr, flush=True)
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


def _get_defs(t, defs, fields, deep=False):
    # LIVE 2026-10-03: WITHOUT deep=True get_defs answers a list field as class NAMES ("WeatherCommonalityRecord"), so
    # reading baseWeatherCommonalities/wildPlants as dict rows raised AttributeError ('str' has no .get). WITH deep=True
    # a modExtensions entry flattens to its FIELDS ([{}] for the empty marker RM_LeanExtension): read that one shallow.
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, limit=200, deep=bool(deep))
    if not _live(t):
        return {}, None
    _ok(r, "get_defs(%s)" % defs[:80])
    return dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or [])), r


def _stack_total(t, defName, rect):
    """Total items of a def over `rect` (stack sizes summed): list_things counts THINGS, and a
    shed of 5 wool lands as one stack, so a bare countMatched reads it as 1."""
    return sum(int(w.get("stackCount") or 1) for w in _things(t, defName, rect, limit=500))


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


def _hediffs(row):
    return list(((row or {}).get("health") or {}).get("hediffs") or [])


# What the twitcher lash leaves: RM_CompLash.TryStrike -> victim.TakeDamage(RM_VenomvineScratch), i.e. a part-bound
# injury plus the damage def's additionalHediffs RM_VenomvineVenom. LIVE 2026-10-07: a bare hediff COUNT read an ambient
# Heatstroke and RM_GlareBlind (part null, from the hot quicktest map and CreatureBehaviors' glare) as "the lash struck".
LASH_HEDIFFS = ("RM_VenomvineVenom",)


def _lash_marks(row):
    return len([h for h in _hediffs(row) if isinstance(h, dict)
                and (h.get("part") not in (None, "") or h.get("def") in LASH_HEDIFFS)])


def _has_hediff(row, hediff):
    return hediff in json.dumps(_hediffs(row))


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


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


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
            print("[lscrub] RESTORE FAILED %s -> %r (set returned %r)" % (field, got, r),
                  file=sys.stderr, flush=True)
    except Exception as ex:   # restoring must never mask the verdict that got us here
        print("[lscrub] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)


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
    """Release the lock AND leave the map on vanilla Clear: a released lock keeps the last weather
    until the next natural roll, and a lingering Gale would deafen every later chain's colonists."""
    if t.session is not None:
        try:
            t.session.call("jawa/weather_set", weather="Clear", lockWeather=True)
            t.session.call("jawa/weather_set", unlock=True)
        except Exception as ex:
            print("[lscrub] weather reset failed: %s" % ex, file=sys.stderr, flush=True)


def _wait(t, n):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact; ~53 ticks/s MEASURED live on a
    big list). Long waits run Ultrafast and poll the real clock, then pause; raises on a stall."""
    # LIVE 2026-10-03: under the situational watch the Ultrafast poll below moves the clock outside the budgeted gate
    # (BudgetExceeded 'spent 8721 of cap 948'), so a watched run uses the chunked, budgeted t.wait_ticks for every length.
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
            elif time.time() - stall > 30:
                # LIVE 2026-10-07 (101652Z and 104321Z, both at smother_off_holds_claims): set_time_speed Ultrafast left
                # the clock frozen for 60 s while every stepped rimworld/step_game_ticks wait in the same run advanced
                # normally; no Transient/modcheck result (47 files) records a single successful Ultrafast _wait. Fall back
                # to the stepped wait (exact, ~53 ticks/s) rather than failing the component on a harness clock.
                # RULED OUT: the smother-off arm itself pausing the game -- it only flips a static bool before the wait.
                _note(t, "_wait: Ultrafast did not advance the clock (stuck at %d); stepping instead" % now, n)
                break
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    now = s._ticks()
    if now < target:
        t.wait_ticks(target - now)
        now = s._ticks()
    t._record("_wait(%d) at Ultrafast -> %d real ticks" % (n, now - start), now - start)


def _stable(t, fn):
    """Run a chain body, then ALWAYS release the weather lock and clear the pad's pawns."""
    try:
        fn()
    finally:
        _unlock_weather(t)
        if t.session is not None and getattr(t, "anchor", None):
            try:
                t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)),
                               categories="All")
            except Exception as ex:
                print("[lscrub] pad cleanup failed: %s" % ex, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- chain: defs

@suite.chain("defs")
def defs_chain(t):
    _pad(t, "spawn")
    with _comp(t, "defs_resolve"):
        if _live(t):
            # The parser must see the mod: a broken regex would read "all 0 defs resolve".
            if len(SHIPPED) < 50 or not DEFS_BY_TYPE.get("WeatherDef") or not KINDS:
                _fail("parsed only %d shipped defs from %s (parser broken?)" % (len(SHIPPED), HERE))
            r = t.bridge_call("jawa/get_defs", defs=";".join(SHIPPED), fields="defName", limit=200)
            _ok(r, "get_defs(all shipped)")
            if r.get("notFound"):
                _fail("%d shipped def(s) did not resolve live (silently discarded?): %s"
                      % (len(r["notFound"]), r["notFound"][:12]))
            if r.get("foundCount") != len(SHIPPED):
                _fail("get_defs foundCount %r != %d requested" % (r.get("foundCount"), len(SHIPPED)))
            # Sanity probe: the instrument must be able to say "absent".
            probe = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_LeaningScrub_NoSuchDef_Probe",
                                  fields="defName")
            if "RM_LeaningScrub_NoSuchDef_Probe" not in json.dumps((probe or {}).get("notFound")):
                _fail("sanity probe: an absent def was not reported in notFound: %r" % probe)
            _note(t, "shipped defs resolved", len(SHIPPED))

    with _comp(t, "biome_weather_table"):
        if _live(t):
            f, _ = _get_defs(t, "BiomeDef/RM_LeaningScrub",
                             "baseWeatherCommonalities,animalDensity,wildPlants", deep=True)
            row = dict(f.get("RM_LeaningScrub") or {})
            f2, _ = _get_defs(t, "BiomeDef/RM_LeaningScrub", "modExtensions")
            row["modExtensions"] = (f2.get("RM_LeaningScrub") or {}).get("modExtensions")
            table = row.get("baseWeatherCommonalities")
            if not isinstance(table, list) or not table:
                _unmeasured(t, "post-patch weather table unreadable: %r" % table)
            w = dict((x.get("weather"), x.get("commonality") or 0) for x in table)
            _note(t, "BiomeDef weather table", w)
            missing = [n for n in ("RM_ScrubWind", "RM_ScrubWindFog", "RM_Stall", "RM_Gale")
                       if not w.get(n)]
            if missing:
                _fail("owned weather(s) absent or zero in the biome table: %s" % missing)
            calm = [n for n in ("Clear", "Fog", "Rain", "RainyThunderstorm", "FoggyRain",
                                "SnowGentle", "SnowHard") if w.get(n)]
            if calm:
                _fail("stock weather with commonality > 0 (ban 5: every ordinary day carries wind): %s"
                      % calm)
            _STATE["biome_row"] = row

    with _comp(t, "biome_density_and_flora"):
        if _live(t):
            row = _STATE.get("biome_row")
            if row is None:
                _unmeasured(t, "biome row not read (biome_weather_table did not run)")
            dens = row.get("animalDensity")
            if not isinstance(dens, (int, float)) or dens <= 0:
                _fail("animalDensity %r: <= 0 means the animal roster can never spawn" % dens)
            wp = row.get("wildPlants")
            if not isinstance(wp, list):
                _unmeasured(t, "wildPlants unreadable: %r" % wp)
            keys = set(x.get("plant") for x in wp)
            need = set(["RM_Fuzz", "RM_VenomvineThicket", "RM_DrippingVenomvine", "RM_TwitcherVenomvine",
                        "RM_HollowVenomvine", "RM_CrownVenomvine", "RM_Whipfuzz", "RM_Cruststar"]
                       + list(FORM_PLANTS))
            if need - keys:
                _fail("biome wildPlants lacks %s" % sorted(need - keys))

    with _comp(t, "biome_lean_extension"):
        if _live(t):
            row = _STATE.get("biome_row") or {}
            ext = row.get("modExtensions")
            if not isinstance(ext, list):
                _unmeasured(t, "BiomeDef.modExtensions unreadable: %r" % ext)
            if not any(str(e).endswith("RM_LeanExtension") for e in ext):
                _fail("RM_LeaningScrub carries no RM_LeanExtension (the Lean never applies): %r" % ext)


# --------------------------------------------------------------------------- chain: patches

@suite.chain("patches")
def patches_chain(t):
    _pad(t, "spawn")
    with _comp(t, "rules_armed", toggle="modEnabled"):
        if _live(t):
            bad = []
            for typ, meth, kind, patch in RULES:
                r = t.bridge_call("jawa/harmony_patches", typeName=typ, methodName=meth)
                _ok(r, "harmony_patches(%s.%s)" % (typ, meth))
                if r.get("harmonyError"):
                    _unmeasured(t, "HarmonyLib introspection unavailable: %r" % r)
                mine = [p for m in (r.get("methods") or []) for p in (m.get(kind) or [])
                        if (p.get("patchMethod") or "").endswith(patch)
                        and p.get("owner") == HARMONY_OWNER]
                if not mine:
                    bad.append("%s.%s lacks %s %s (target not found at startup? see the "
                               "'rule NOT armed' log line)" % (typ, meth, kind[:-2], patch))
            if bad:
                _fail("; ".join(bad))

    with _comp(t, "thicket_smotherable"):
        if _live(t):
            r = t.bridge_call("jawa/get_def", defName="RM_VenomvineThicket", defType="ThingDef")
            _ok(r, "get_def(RM_VenomvineThicket)")
            comps = r.get("comps")
            if not isinstance(comps, list) or not comps:
                _unmeasured(t, "get_def returned no readable comps list: %r" % (comps,))
            names = [c if isinstance(c, str) else (c.get("class") or c.get("compClass") or "")
                     for c in comps]
            if not any(str(n).endswith("RM_CompProperties_Smotherable") or
                       str(n).endswith("RM_CompSmotherable") for n in names):
                _fail("the shared thicket carries no smotherable comp -- the patch matched "
                      "nothing (and logs nothing): %r" % names)

    with _comp(t, "vissler_arm_is_rotting_meat", toggle="visslerArmFoodEnabled"):
        # LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1: the arm is a vanilla ingestible that rots, so hungry
        # predators/scavengers/omnivores find it with the engine's own AI. Whether a given hungry animal
        # walks to it is NOT asserted here (needs a hungry wild animal; unmeasured live by design).
        if _live(t):
            r = t.bridge_call("jawa/get_def", defName="RM_VisslerArm", defType="ThingDef")
            _ok(r, "get_def(RM_VisslerArm)")
            comps = r.get("comps")
            if not isinstance(comps, list) or not comps:
                _unmeasured(t, "get_def returned no readable comps list: %r" % (comps,))
            names = [c if isinstance(c, str) else (c.get("class") or c.get("compClass") or "")
                     for c in comps]
            if not any(str(n).endswith("CompProperties_Rottable") for n in names):
                _fail("RM_VisslerArm carries no rottable comp: %r" % names)

    with _comp(t, "dead_venomvine_fuels_fire"):
        if _live(t):
            _prep(t, "fuel", 12)
            rect = _rect(t, 12)
            x, z = t.anchor
            t.bridge_call("jawa/spawn_batch", ops="Campfire:%d,%d" % (x, z))
            t.bridge_call("jawa/spawn_batch", ops="RM_DeadVenomvine:%d,%d,20" % (x + 3, z))
            camp = _things(t, "Campfire", _rs(rect))
            fuel = _things(t, "RM_DeadVenomvine", _rs(rect))
            if not camp or not fuel:
                _fail("fixture missing: campfire %d, dead venomvine %d" % (len(camp), len(fuel)))
            cid, fid = camp[0]["id"], fuel[0]["id"]
            before = fuel[0].get("stackCount")
            # A spawned Campfire is FULL (initialFuelPercent 1.0, capacity 20, 10 fuel/day). JobDriver_Refuel ends
            # Succeeded at once while CompRefuelable.IsFull, and IsFull = TargetFuelLevel - fuel < 1 -- so the fire must
            # burn MORE than one whole unit (> 6000 ticks) before any fuel is taken.
            # RULED OUT (LIVE 2026-10-07): "the fuel patch does not apply" -- the old 3000-tick wait burned 0.5 fuel; the
            # inspect read "Fuel: 19 / 20" (~19.35 after 3900 ticks), IsFull was true, and ordered_job reported curJob
            # Wait_MaintainPosture instead of Refuel: the job ended on its IsFull end condition before choosing fuel. Core's
            # Campfire comps li (CompProperties_Refuelable/fuelFilter/thingDefs/li=WoodLog) matches the patch xpath.
            t.wait_ticks(10000)          # ~1.67 fuel burned -> ~18.3, read "18" (ToStringDecimalIfSmall rounds >=10)
            _, pre = _inspect(t, cid)
            m = re.search(r"Fuel:\s*([\d.]+)\s*/\s*([\d.]+)", " ".join(pre))
            if not m or float(m.group(2)) - float(m.group(1)) < 2:
                _unmeasured(t, "the campfire is still (nearly) full before the refuel (%s): JobDriver_Refuel would end "
                               "on IsFull and prove nothing about the fuel filter" % pre)
            col = _spawn(t, "Colonist", x - 2, z + 2, faction="player")
            t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="Refuel", targetAId=cid,
                          targetBId=fid, count=10, waitTicks=60)
            t.wait_ticks(900)
            left = _things(t, "RM_DeadVenomvine", _rs(rect))
            after = sum(int(w.get("stackCount") or 0) for w in left)
            _, lines = _inspect(t, cid)
            _note(t, "refuel with dead venomvine", {"stackBefore": before, "stackAfter": after,
                                                    "campfire": lines})
            if before is None:
                _unmeasured(t, "list_things rows carry no stackCount: cannot see fuel consumed")
            if after >= int(before):
                _fail("the colonist did not burn any dead venomvine (stack %s -> %s): the fuel "
                      "patch does not apply to the Campfire's fuel filter" % (before, after))
        _stable(t, lambda: None)


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

    # Toggles whose EFFECT this suite cannot drive (see the module docstring): the field must
    # exist, read its shipped default and be writable, restored afterwards.
    for field in ("venomvinePassabilityEnabled", "galeRaidWeightingEnabled", "leanEnabled",
                  "leanScentEnabled", "leanFireEnabled"):
        with _comp(t, "%s_roundtrip" % field, toggle=field):
            if _live(t):
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s is not at its shipped default" % field)
                with _setting(t, field, not DEFAULTS[field]):
                    pass


# --------------------------------------------------------------------------- chain: fauna & flora

@suite.chain("fauna")
def fauna_chain(t):
    _prep(t, "spawn")
    rect = _rect(t)
    x0, z0 = rect[0] + 2, rect[1] + 2
    try:
        with _comp(t, "fauna_spawns"):
            if _live(t):
                ids = {}
                for i, kind in enumerate(KINDS):
                    ids[kind] = _spawn(t, kind, x0 + (i % 6) * 3, z0 + (i // 6) * 3)
                rows = _rows(t, rect=_rs(rect))
                lost = [k for k, pid in ids.items()
                        if pid not in rows or rows[pid].get("dead")
                        or rows[pid].get("kindDef") != k]
                _note(t, "wild kinds spawned", {"asked": len(KINDS), "lost": lost})
                if len(KINDS) < 13:
                    _fail("parsed %d PawnKindDefs, expected 13" % len(KINDS))
                if lost:
                    _fail("kind(s) spawned no living pawn of that kind in the rect: %s" % lost)
        with _comp(t, "dustflutter_can_fly"):
            if _live(t):
                flut = [pid for pid, p in _rows(t, rect=_rs(rect)).items()
                        if p.get("kindDef") == "RM_Dustflutter"]
                if not flut:
                    _unmeasured(t, "no dustflutter on the pad to read")
                r = t.bridge_call("jawa/pawn_flight", action="report", pawn=flut[0])
                rows = (_ok(r, "pawn_flight").get("pawns") or [])
                if not rows or "canEverFly" not in rows[0]:
                    _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
                if rows[0].get("canEverFly") is not True:
                    _fail("RM_Dustflutter canEverFly=%r (MaxFlightTime stat %r): the runway bloom "
                          "and crown mob cannot launch it" % (rows[0].get("canEverFly"),
                                                             rows[0].get("maxFlightTimeStat")))
    finally:
        _stable(t, lambda: None)


@suite.chain("flora")
def flora_chain(t):
    _prep(t, "spawn")
    rect = _rect(t)
    try:
        with _comp(t, "flora_spawns"):
            if _live(t):
                if len(PLANTS) < 18:
                    _fail("parsed %d plant defs, expected 18" % len(PLANTS))
                cells = {}
                # LIVE 2026-10-07: RM_Grellspine came back "REJECTED 1: terrain or conditions cannot support" -- its
                # <pollution>PollutedOnly</pollution> makes PlantUtility.CanEverPlantAt refuse every CLEAN cell, so the
                # pad's plain soil could never hold it. A PollutedOnly plant gets its own cell polluted first.
                # RULED OUT: soil fertility (Soil 1.0 >= fertilityMin 0.05), map temperature (min/max growth -22..62),
                # the plant dying after spawn (set_plants itself reported planted 0, rejected 1 for that def only).
                for i, d in enumerate(PLANTS):
                    cx, cz = rect[0] + 2 + (i % 6) * 3, rect[1] + 2 + (i // 6) * 3
                    cells[d] = (cx, cz)
                    if d in POLLUTED_ONLY:
                        p = t.bridge_call("jawa/set_pollution", rect="%d,%d,1,1" % (cx, cz), polluted=True)
                        if _live(t) and not (_ok(p, "set_pollution").get("cellsEverPollutable")):
                            _unmeasured(t, "cell %d,%d cannot be polluted for PollutedOnly %s: %r" % (cx, cz, d, p))
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, cx, cz), growth=1.0)
                lost = [d for d, (cx, cz) in cells.items()
                        if _count(t, d, "%d,%d,1,1" % (cx, cz)) < 1]
                _note(t, "flora set", {"asked": len(PLANTS), "lost": lost})
                if lost:
                    _fail("plant def(s) did not stand after set_plants: %s" % lost)
    finally:
        _stable(t, lambda: None)
        if t.session is not None and POLLUTED_ONLY:
            try:    # leave the shared spawn pad clean for whoever uses it next
                t.session.call("jawa/set_pollution", rect=_rs(_rect(t, PAD_SIZE + 8)), polluted=False)
            except Exception as ex:
                print("[lscrub] pollution cleanup failed: %s" % ex, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- chain: the Stall

def _path(t, ids, steps=6, step=250):
    """Per-pawn path length over steps*step ticks, from list_pawns x/z, plus the job def seen at each
    sample (jawa/site_state) so a move can be attributed to wandering or to something else."""
    pos = dict((i, [_xz(r)]) for i, r in _rows(t).items() if i in ids)
    jobs = dict((i, []) for i in ids)
    j0 = _jobs(t)
    for i in ids:
        jobs[i].append(j0.get(i))
    for _ in range(steps):
        t.wait_ticks(step)
        rows = _rows(t)
        jn = _jobs(t)
        for i in ids:
            pos.setdefault(i, []).append(_xz(rows.get(i)))
            jobs[i].append(jn.get(i))
    out = {}
    for i in ids:
        pts = [p for p in pos.get(i, []) if p]
        out[i] = {"alive": len(pts), "samples": len(pos.get(i, [])),
                  "path": sum(_dist(a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else 0.0,
                  "jobs": jobs[i]}
    return out


_WANDER_JOBS = ("GotoWander", "Wait_Wander", None)


def _full(t, pid):
    for need in ("Food", "Rest"):
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)


@suite.chain("stall")
def stall_chain(t):
    _prep(t, "stall")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "stall_freezes_small", toggle="stallFreezeEnabled"):
            if _live(t):
                _lock_weather(t, "RM_Stall")
                ids["small"] = _spawn(t, STALL_SMALL, x - 3, z)
                ids["big"] = _spawn(t, STALL_BIG, x + 3, z)
                for p in ids.values():
                    _full(t, p)
                # LIVE 2026-10-07 (twice, 101652Z and 104321Z): BOTH animals moved the SAME vector, to the SAME cells in
                # both runs ((77,80)->(89,92)->(90,95) and (83,80)->(94,92)), all in the first 250 ticks, then BOTH held
                # still -- the 0.7 control included -- for >= 1000 ticks. A shared, deterministic, non-wander move: the
                # freeze (RM_WindCalendarPatches.Wander_Prefix) replaces ONLY JobGiver_Wander's answer by design, so a
                # higher think-node job (flee, seek-safe-temperature, ...) is out of its scope, and the old path-only
                # predicate counted it as a wander. The job def at each sample now says which kind of move it was.
                # RULED OUT: juvenile control frozen by size -- list_pawns read bodySize 0.4 / 0.7 (both adult).
                # RULED OUT: weather not locked -- weather_get read current RM_Stall right after the lock.
                # RULED OUT: the crown mob / fire stamp pulling them -- those move only RM_Dustflutter / stamper-extension
                # races (RM_VenomvineRooms.cs:134, RM_FireStamp.cs:61).
                res = _path(t, list(ids.values()), steps=12, step=125)
                _note(t, "Stall: path lengths (cells) and sampled jobs over 1500 ticks", res)
                small, big = res[ids["small"]], res[ids["big"]]
                if big["alive"] < 3 or small["alive"] < 3:
                    _unmeasured(t, "a test animal vanished from list_pawns: %r" % res)
                if "GotoWander" in small["jobs"]:
                    _fail("%s (body 0.4 < 0.5) was handed a GotoWander job in the Stall (jobs %s); the freeze should "
                          "answer Wait_Wander" % (STALL_SMALL, small["jobs"]))
                if big["path"] < 3.0 and "GotoWander" not in big["jobs"]:
                    _unmeasured(t, "the larger control animal (%s, body 0.7) neither moved nor wandered (path %.1f, "
                                   "jobs %s): cannot tell frozen from stuck" % (STALL_BIG, big["path"], big["jobs"]))
                other = sorted(set(j for j in small["jobs"] if j not in _WANDER_JOBS))
                if small["path"] > 1.5 and not other:
                    _fail("%s (body 0.4 < 0.5) moved %.1f cells in the Stall with only wander-family jobs %s; it "
                          "should hold still (control %s moved %.1f)"
                          % (STALL_SMALL, small["path"], small["jobs"], STALL_BIG, big["path"]))
                if small["path"] > 1.5:
                    _note(t, "Stall: the small animal's move came from non-wander job(s), outside the freeze", other)
        with _comp(t, "stall_toggle_off_wanders", toggle="stallFreezeEnabled"):
            if _live(t):
                with _setting(t, "stallFreezeEnabled", False):
                    res = _path(t, [ids["small"]])
                _note(t, "Stall, stallFreezeEnabled OFF: path", res)
                if res[ids["small"]]["path"] < 3.0:
                    _fail("with stallFreezeEnabled OFF the small animal still moved only %.1f cells "
                          "in 1500 ticks (the toggle does not release it)" % res[ids["small"]]["path"])
        with _comp(t, "stall_master_off_wanders", toggle="modEnabled"):
            if _live(t):
                with _setting(t, "modEnabled", False):
                    res = _path(t, [ids["small"]])
                _note(t, "Stall, modEnabled OFF: path", res)
                if res[ids["small"]]["path"] < 3.0:
                    _fail("with modEnabled OFF the small animal moved only %.1f cells in 1500 ticks "
                          "(the master switch does not gate the freeze)" % res[ids["small"]]["path"])
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the Gale

_POWER = re.compile(r"power output[^0-9\-]*(-?[\d.,]+)", re.I)


def _turbine_output(t, tid):
    t.wait_ticks(5)
    _, lines = _inspect(t, tid)
    m = _POWER.search(" ".join(lines))
    if not m:
        _unmeasured(t, "turbine inspect text has no 'Power output' line: %r" % lines)
    return float(m.group(1).replace(",", ""))


@suite.chain("gale")
def gale_chain(t):
    _prep(t, "gale")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "gale_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_Gale")
                room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,9,9" % (x - 11, z - 4),
                                     stuffDef="Steel")
                _ok(room, "make_empty_room")
                ids["out"] = _spawn(t, "Colonist", x + 6, z + 8, faction="player")
                ids["in"] = _spawn(t, "Colonist", x - 7, z, faction="player")
                for p in (ids["out"], ids["in"]):
                    t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
                roof = t.bridge_call("jawa/get_roof_batch", rects="%d,%d,7,7" % (x - 10, z - 3))
                if not _roofed(roof):
                    _unmeasured(t, "the sealed room is not roofed (get_roof_batch %r): cannot tell "
                                   "outdoors from indoors" % roof)
        with _comp(t, "gale_deafens_outdoors", toggle="galeDeafenEnabled"):
            if _live(t):
                t.wait_ticks(600)
                rows = _rows(t, health=True)
                outside, inside = rows.get(ids["out"]), rows.get(ids["in"])
                if not outside or not inside:
                    _unmeasured(t, "test colonist missing from list_pawns")
                if not _has_hediff(outside, "RM_GaleDeafened"):
                    _fail("outdoor colonist carries no RM_GaleDeafened after 600 ticks of Gale: %s"
                          % _hediffs(outside))
        with _comp(t, "gale_spares_roofed", toggle="galeDeafenEnabled"):
            if _live(t):
                rows = _rows(t, health=True)
                if _has_hediff(rows.get(ids["in"]), "RM_GaleDeafened"):
                    _fail("the roofed colonist was deafened too (the effect ignores the roof)")
        with _comp(t, "gale_deafen_toggle_off", toggle="galeDeafenEnabled"):
            if _live(t):
                t.bridge_call("jawa/pawn_health", pawn=ids["out"], action="remove",
                              hediff="RM_GaleDeafened")
                if _has_hediff(_rows(t, health=True).get(ids["out"]), "RM_GaleDeafened"):
                    _unmeasured(t, "could not remove RM_GaleDeafened to start the OFF arm")
                with _setting(t, "galeDeafenEnabled", False):
                    t.wait_ticks(600)
                    rows = _rows(t, health=True)
                if _has_hediff(rows.get(ids["out"]), "RM_GaleDeafened"):
                    _fail("galeDeafenEnabled OFF but the outdoor colonist was deafened again")
        # A turbine for the surge / breakdown arms, with open ground around it.
        with _comp(t, "gale_turbine_surge", toggle="galeTurbineSurgeEnabled"):
            if _live(t):
                tx, tz = x + 4, z - 6
                t.bridge_call("jawa/spawn_batch", ops="WindTurbine:%d,%d" % (tx, tz))
                turb = _things(t, "WindTurbine", _rs(_rect(t)))
                if not turb:
                    _unmeasured(t, "no WindTurbine on the pad after spawn_batch")
                ids["turbine"] = turb[0]["id"]
                # LIVE 2026-10-07: spawn_batch leaves the turbine faction null, and RM_MapComponent_WindCalendar.
                # RollTurbineBreakdowns walks map.listerBuildings.allBuildingsColonist only -- so a factionless turbine
                # was never rolled and gale_turbine_breakdown read "no breakdown" at a 0.01-day mean. Make it the colony's.
                # RULED OUT: the roll never firing -- MTB 0.01 d = 600 ticks over a 2500-tick check is ~98% per roll.
                own = t.bridge_call("jawa/set_thing_props", thing=ids["turbine"], faction="PlayerColony")
                if _live(t) and "faction" not in json.dumps((own or {}).get("changed")):
                    _unmeasured(t, "set_thing_props could not make the turbine player-owned: %r" % (own,))
                _set(t, "galeTurbineBreakdownMtbDays", 0)     # 0 = never: keep the turbine whole
                try:
                    t.wait_ticks(4100)       # the wind ramps into the Gale over the transition
                    on1 = _turbine_output(t, ids["turbine"])
                    with _setting(t, "galeTurbineSurgeEnabled", False):
                        off = _turbine_output(t, ids["turbine"])
                    on2 = _turbine_output(t, ids["turbine"])
                finally:
                    _restore(t, "galeTurbineBreakdownMtbDays")
                _note(t, "turbine output W (on, off, on)", [on1, off, on2])
                if off <= 0:
                    _unmeasured(t, "turbine produces %.1f W with the surge off (obstructed or "
                                   "unpowered): no baseline" % off)
                ratio = (on1 + on2) / 2.0 / off
                if not 1.2 <= ratio <= 1.4:
                    _fail("Gale turbine output ratio surge-on/off = %.3f, expected ~%.2f (%s)"
                          % (ratio, DEFAULTS["galeTurbineSurgeFactor"], [on1, off, on2]))
        with _comp(t, "gale_turbine_breakdown", toggle="galeTurbineSurgeEnabled"):
            if _live(t):
                _, before = _inspect(t, ids["turbine"])
                if re.search(r"broken down", " ".join(before), re.I):
                    _unmeasured(t, "the turbine was already broken down before the arm began")
                with _setting(t, "galeTurbineBreakdownMtbDays", 0.01):
                    t.wait_ticks(5200)       # two 2500-tick rolls at a 600-tick mean
                    _, after = _inspect(t, ids["turbine"])
                if not re.search(r"broken down", " ".join(after), re.I):
                    _fail("no breakdown on a running turbine after two rolls at a 0.01-day mean "
                          "in the Gale: %s" % after)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the lash

@suite.chain("lash")
def lash_chain(t):
    _prep(t, "lash")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "lash_site_ready", poison=True):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="RM_TwitcherVenomvine:%d,%d,1,1" % (x, z),
                              growth=1.0)
                plant = _things(t, "RM_TwitcherVenomvine", "%d,%d,1,1" % (x, z))
                if not plant:
                    _unmeasured(t, "the twitcher stand did not stand after set_plants")
                ids["plant"] = plant[0]["id"]
                ids["col"] = _spawn(t, "Colonist", x + 1, z, faction="player")
                t.bridge_call("jawa/set_draft", pawnId=ids["col"], drafted=True)
                _full(t, ids["col"])
        with _comp(t, "lash_toggle_off_quiet", toggle="twitcherLashEnabled"):
            if _live(t):
                # RULED OUT (LIVE 2026-10-07): "the lash ignores its toggle" -- the 2 hediffs gained were Heatstroke and
                # RM_GlareBlind, both part-less ambient conditions; the stand's inspect read "Mature." (no lash state).
                n0 = _lash_marks(_rows(t, health=True).get(ids["col"]))
                with _setting(t, "twitcherLashEnabled", False):
                    t.wait_ticks(300)
                    row1 = _rows(t, health=True).get(ids["col"])
                    n1 = _lash_marks(row1)
                    _, lines = _inspect(t, ids["plant"])
                _note(t, "lash OFF: colonist hediffs after 300 ticks", _hediffs(row1))
                if n1 != n0:
                    _fail("twitcherLashEnabled OFF but the colonist next to the stand gained %d lash "
                          "mark(s) (injury / venom): %s" % (n1 - n0, _hediffs(row1)))
                if re.search(r"poised|spent", " ".join(lines), re.I):
                    _fail("twitcherLashEnabled OFF but the stand still reports a lash state: %s" % lines)
        with _comp(t, "lash_strikes_once", toggle="twitcherLashEnabled"):
            if _live(t):
                _, lines = _inspect(t, ids["plant"])
                if "Poised to strike" not in " ".join(lines):
                    _unmeasured(t, "the stand is not poised before the arm: %s" % lines)
                n0 = _lash_marks(_rows(t, health=True).get(ids["col"]))
                t.wait_ticks(120)
                n1 = _lash_marks(_rows(t, health=True).get(ids["col"]))
                _, lines1 = _inspect(t, ids["plant"])
                t.wait_ticks(600)
                n2 = _lash_marks(_rows(t, health=True).get(ids["col"]))
                _note(t, "lash: hediffs before / after strike / after the hour's first 600 ticks",
                      [n0, n1, n2])
                if n1 <= n0:
                    _fail("a poised twitcher next to a colonist did not strike in 120 ticks "
                          "(hediffs %d -> %d)" % (n0, n1))
                if "Spent" not in " ".join(lines1):
                    _fail("after striking the stand does not read as spent: %s" % lines1)
                if n2 != n1:
                    _fail("the spent stand struck again within 600 ticks (hediffs %d -> %d); it "
                          "should droop for an hour" % (n1, n2))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: smother-craft

@suite.chain("smother")
def smother_chain(t):
    _prep(t, "smother")
    x, z = t.anchor
    ids = {}

    def banked(stand):
        _, lines = _inspect(t, stand)
        return "Smothered under a blanket" in " ".join(lines), lines

    def body():
        with _comp(t, "smother_site_ready", poison=True):
            if _live(t):
                for dz in (0, 4):
                    t.bridge_call("jawa/set_plants",
                                  ops="RM_HollowVenomvine:%d,%d,1,1" % (x + 4, z + dz), growth=1.0)
                stands = sorted(_things(t, "RM_HollowVenomvine", _rs(_rect(t))),
                                key=lambda w: w.get("z"))
                if len(stands) != 2:
                    _unmeasured(t, "expected 2 venomvine stands, found %d" % len(stands))
                ids["stands"] = [w["id"] for w in stands]
                t.bridge_call("jawa/spawn_batch", ops="RM_SmotherBlanket:%d,%d,2" % (x - 2, z))
                blanket = _things(t, "RM_SmotherBlanket", _rs(_rect(t)))
                if not blanket:
                    _unmeasured(t, "no RM_SmotherBlanket on the pad after spawn_batch")
                ids["blanket"] = blanket[0]["id"]
                ids["col"] = _spawn(t, "Colonist", x - 4, z + 2, faction="player")
                _full(t, ids["col"])
                _set(t, "smotherDays", 0.1)   # 6000 ticks; the shipped 30 days is not observable
        with _comp(t, "smother_claims_stands", toggle="smotherCraftEnabled"):
            if _live(t):
                for sid in ids["stands"]:
                    t.bridge_call("jawa/ordered_job", pawnId=ids["col"], jobDef="RM_SmotherVenomvine",
                                  targetAId=sid, targetBId=ids["blanket"], count=1, waitTicks=60)
                    got, lines = False, []
                    for _ in range(12):
                        t.wait_ticks(250)
                        got, lines = banked(sid)
                        if got:
                            break
                    if not got:
                        _fail("the smother job did not bank a claim on stand %s within 3000 ticks: %s"
                              % (sid, lines))
                left = sum(int(w.get("stackCount") or 0)
                           for w in _things(t, "RM_SmotherBlanket", _rs(_rect(t))))
                if left != 0:
                    _fail("%d blanket(s) remain after two claims were banked; each claim should "
                          "consume one" % left)
        try:
            with _comp(t, "smother_off_holds_claims", toggle="smotherCraftEnabled"):
                if _live(t):
                    _set(t, "smotherCraftEnabled", False)
                    _wait(t, 9000)               # claim = 6000 ticks, banked within ~1500
                    alive = [_count(t, "RM_HollowVenomvine", "%d,%d,1,1" % (x + 4, z + dz))
                             for dz in (0, 4)]
                    _, lines = _inspect(t, ids["stands"][0]) if alive[0] else (None, [])
                    _note(t, "feature OFF, claim due: stands alive / inspect", [alive, lines])
                    if alive != [1, 1]:
                        _fail("smotherCraftEnabled OFF but a due claim matured anyway "
                              "(stands standing: %s)" % alive)
                    if alive[0] and "ready to fall" not in " ".join(lines):
                        _fail("claim is held but does not read as due after >6000 ticks (claim time "
                              "does not follow smotherDays?): %s" % lines)
            with _comp(t, "smother_matures_to_dead_wood", toggle="smotherCraftEnabled"):
                if _live(t):
                    _set(t, "smotherCraftEnabled", True)
                    t.wait_ticks(2700)
                    alive = [_count(t, "RM_HollowVenomvine", "%d,%d,1,1" % (x + 4, z + dz))
                             for dz in (0, 4)]
                    wood = sum(int(w.get("stackCount") or 0)
                               for w in _things(t, "RM_DeadVenomvine", _rs(_rect(t))))
                    _note(t, "feature back ON: stands alive / dead venomvine", [alive, wood])
                    if alive != [0, 0]:
                        _fail("matured claims left stands standing: %s" % alive)
                    if wood < 20:
                        _fail("two matured stands yielded only %d dead venomvine (expect ~2 x 40)" % wood)
        finally:
            _restore(t, "smotherCraftEnabled")
            _restore(t, "smotherDays")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: dripping

@suite.chain("dripping")
def dripping_chain(t):
    _prep(t, "dripping")
    x, z = t.anchor
    rect = _rect(t)

    def body():
        with _comp(t, "dripping_survives_harvest", toggle="drippingRegrowEnabled"):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="RM_DrippingVenomvine:%d,%d,1,1" % (x, z),
                              growth=1.0)
                plant = _things(t, "RM_DrippingVenomvine", "%d,%d,1,1" % (x, z))
                if not plant:
                    _unmeasured(t, "the dripping stand did not stand after set_plants")
                col = _spawn(t, "Colonist", x - 3, z, faction="player")
                _full(t, col)
                t.bridge_call("jawa/designate_batch", action="add", designation="HarvestPlant",
                              rect="%d,%d,1,1" % (x, z))
                t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="Harvest",
                              targetAId=plant[0]["id"], queue=True, waitTicks=60)
                t.wait_ticks(1200)
                venom = _stack_total(t, "RM_RawVenom", _rs(rect))
                standing = _count(t, "RM_DrippingVenomvine", "%d,%d,1,1" % (x, z))
                _, lines = _inspect(t, plant[0]["id"]) if standing else (None, [])
                _note(t, "dripping harvest: venom items / stand standing / inspect",
                      [venom, standing, lines])
                if venom < 1:
                    _unmeasured(t, "no venom was harvested in 1200 ticks (job not done): cannot "
                                   "judge whether the stand survives")
                if standing != 1:
                    _fail("the harvest destroyed the dripping stand (drippingRegrowEnabled is ON "
                          "and the def should regrow it from growth 0.3)")
                pct = re.search(r"growth[^0-9]*(\d+)\s*%", " ".join(lines), re.I)
                if pct and int(pct.group(1)) > 60:
                    _fail("harvested stand reads %s%% grown; it should drop back to ~30%%" % pct.group(1))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: crown mob

@suite.chain("crown")
def crown_chain(t):
    _prep(t, "crown")
    x, z = t.anchor
    near = 6.0

    def trial(tag):
        ids = [_spawn(t, "RM_Dustflutter", x + 16 + i, z + 4 - 4 * i) for i in range(3)]
        for p in ids:
            _full(t, p)
        # LIVE 2026-10-07 (both runs): in BOTH arms the dustflutters ended 23-70 cells off (spawned ~16 away), i.e. they
        # roamed far whatever the toggle. RM_MapComponent_CrownMob only claims an IDLE mobber (job null / Wait_Wander /
        # GotoWander / Wait, RM_VenomvineRooms.cs:158-163) every 250 ticks, so a flutter held in another job (a flee, as
        # the stall chain's shared move also suggests) is outside the mechanism. Sample the jobs so the verdict can say so.
        jobs = dict((p, []) for p in ids)
        for _ in range(6):
            t.wait_ticks(250)
            jn = _jobs(t)
            for p in ids:
                jobs[p].append(jn.get(p))
        rows = _rows(t)
        pos = [_xz(rows.get(p)) for p in ids]
        alive = [p for p in pos if p]
        dists = [_dist(p, (x, z)) for p in alive]
        _note(t, "crown trial %s: dustflutter distances to the stand / sampled jobs" % tag, [dists, jobs])
        if len(alive) < 2:
            _unmeasured(t, "%d of 3 dustflutters survived to be measured" % len(alive))
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="Pawn")
        _STATE["crown_jobs"] = jobs
        return dists

    def body():
        with _comp(t, "crown_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_Stall")
                t.bridge_call("jawa/set_plants", ops="RM_CrownVenomvine:%d,%d,1,1" % (x, z),
                              growth=1.0)
                if not _count(t, "RM_CrownVenomvine", "%d,%d,1,1" % (x, z)):
                    _unmeasured(t, "the crown stand did not stand after set_plants")
        with _comp(t, "crown_toggle_off_stays_away", toggle="crownMobEnabled"):
            if _live(t):
                with _setting(t, "crownMobEnabled", False):
                    d = trial("OFF")
                if any(v <= near for v in d):
                    _fail("crownMobEnabled OFF but a dustflutter sits within %.0f cells of the "
                          "crown stand: %s" % (near, d))
        with _comp(t, "crown_mob_gathers", toggle="crownMobEnabled"):
            if _live(t):
                d = trial("ON")
                around = [v for v in d if v <= near]
                idle = ("Wait_Wander", "GotoWander", "Wait", "Goto", None)   # Goto = already sent to the stand
                seen = [j for js in (_STATE.get("crown_jobs") or {}).values() for j in js]
                if len(around) < 2 and seen and not any(j in idle for j in seen):
                    _unmeasured(t, "no dustflutter was ever idle (sampled jobs %s): the crown mob claims only idle "
                                   "mobbers, so this site cannot show the draw" % sorted(set(seen)))
                if len(around) < 2:
                    _fail("only %d of %d dustflutters gathered within %.0f cells of a crown "
                          "stand in the Stall after 1500 ticks: %s" % (len(around), len(d), near, d))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: runway bloom

@suite.chain("bloom")
def bloom_chain(t):
    _prep(t, "bloom")
    x, z = t.anchor

    def trial(tag):
        """One walker through fuzz past one staged cohort of each answering species; returns
        {kind: saw Flee} and the number of vissler arms that appeared."""
        t.bridge_call("jawa/set_plants", ops="RM_Fuzz:%d,%d,30,5" % (x - 15, z - 2), growth=1.0)
        cohort = {}
        for i, kind in enumerate(BLOOM_SPECIES):
            n = 8 if kind == "RM_Vissler" else 2
            cohort[kind] = [_spawn(t, kind, x - 12 + 2 * (j % 4), z - 3 + (i % 2) * 6 + 2 * (j // 4))
                            for j in range(n)]
        arms0 = _stack_total(t, "RM_VisslerArm", _rs(_rect(t, PAD_SIZE + 8)))
        walker = _spawn(t, "Colonist", x - 15, z, faction="player")
        _full(t, walker)
        # LIVE 2026-10-07 (both runs): order_pawn waitTicks=60 unpauses to Normal and waits on the REAL clock with a 30 s
        # wall-clock ceiling; the clock did not move at Normal (same session as the smother chain's Ultrafast stall) and
        # the client's own 30.0 s timeout fired first -> RimBridgeError. Issue the order without waiting; the stepped
        # wait_ticks below advances the game. RULED OUT: the bloom OFF arm hanging the game -- the timeout is at the
        # order, before any bloom tick could run.
        t.bridge_call("jawa/order_pawn", pawnId=walker, x=x + 14, z=z, waitTicks=0, unpause=False)
        saw = dict((k, False) for k in cohort)
        for _ in range(16):
            t.wait_ticks(30)
            jobs = _jobs(t)
            for k, pids in cohort.items():
                if any(jobs.get(p) == "Flee" for p in pids):
                    saw[k] = True
        arms = _stack_total(t, "RM_VisslerArm", _rs(_rect(t, PAD_SIZE + 8))) - arms0
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(_rect(t))), layer="top")
        _note(t, "bloom trial %s: Flee seen per species / vissler arms shed" % tag, [saw, arms])
        return saw, arms

    def body():
        with _comp(t, "bloom_toggle_off_quiet", toggle="runwayBloomEnabled"):
            if _live(t):
                with _setting(t, "runwayBloomEnabled", False):
                    saw, arms = trial("OFF")
                # Flee alone is NOT bloom-specific: vanilla wild animals flee an approaching colonist with no
                # bloom at all (LIVE 2026-10-08 acc_biomes: all four species fled with the toggle OFF while
                # RM_MapComponent_RunwayBloom.MapComponentTick returns at its first line). The bloom's own
                # signature is the vissler arm shed, which only RunPending produces.
                if arms:
                    _fail("runwayBloomEnabled OFF but the bloom still fired: %d vissler arms shed (Flee %s)"
                          % (arms, saw))
        with _comp(t, "bloom_answers_a_walker", toggle="runwayBloomEnabled"):
            if _live(t):
                saw, arms = trial("ON")
                silent = sorted(k for k, v in saw.items() if not v)
                if silent:
                    _fail("no Flee job seen for %s after a colonist walked through the canopy "
                          "(responding species must flee)" % silent)
                if arms < 1:
                    _fail("no RM_VisslerArm shed by 8 visslers (shedChance 0.5 each)")
        # LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1: ribbonwhips sway in place, the surrik leaves an exit hole.
        with _comp(t, "bloom_sway_and_exit_hole", toggle="runwayBloomEnabled"):
            if _live(t):
                _spawn(t, "RM_Ribbonwhip", x - 4, z - 2)
                _spawn(t, "RM_Surrik", x - 3, z + 2)
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_MapComponent_RunwayBloom",
                                  method="ProofVisuals", args="current")
                txt = str((r or {}).get("result", ""))
                _note(t, "bloom visuals (SWAYING n HOLES +n ANSWERED n)", txt)
                if not txt.startswith("SWAYING") or txt.startswith("SWAYING 0") or "HOLES +0" in txt:
                    _fail("no ribbonwhip swaying or no surrik exit hole after a bloom: %s" % txt)
                t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: stamp

@suite.chain("stamp")
def stamp_chain(t):
    """Part 5 fire-stamping (RM_FireStamp.cs). The C# proof hook builds the fixture on the current map (two
    fires, then six; a far stamper, then a near one), drives the SHIPPED ConvergePass/StampPass and cleans up."""
    for mode, name in (("on", "stamp_answers_a_blaze"), ("off", "stamp_toggle_off_ignores_fire")):
        with _comp(t, name, toggle="fireStampEnabled"):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FireStampProof",
                              method="ProofStamp", args=mode)
            if _live(t):
                txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                _note(t, "fire stamp proof (%s)" % mode, txt[:300])
                if txt.startswith("FAIL"):
                    _fail("fire stamp (%s): %s" % (mode, txt[:400]))
                if not txt.startswith("PASS"):
                    _unmeasured(t, "fire stamp proof did not answer PASS/FAIL: %s" % txt[:200])


# --------------------------------------------------------------------------- chain: the six further forms

# LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1: form key (the proof hook's) -> its plant def.
FORMS = (("rearing", "RM_RearingVenomvine"), ("walking", "RM_WalkingVenomvine"),
         ("hoard", "RM_HoardVenomvine"), ("quench", "RM_QuenchVenomvine"),
         ("sworn", "RM_SwornVenomvine"), ("shedding", "RM_SheddingVenomvine"))
FORM_TOGGLES = {"rearing": "rearingEnabled", "walking": "walkingEnabled", "hoard": "hoardEnabled",
                "quench": "quenchEnabled", "sworn": "swornSparesMarkedEnabled", "shedding": "sheddingEnabled"}


@suite.chain("forms")
def forms_chain(t):
    """The six further venomvine forms (RM_VenomvineForms.cs). RM_VenomvineFormsProof.ProofForm builds each
    fixture on the current map (a stand, a colonist, a fire, a pile of steel), drives the SHIPPED pass
    (SweepRearing / SweepThorns / SweepHoard / SweepQuench / Walk / Shed) with the setting on and then off,
    reads the state, and cleans up. Walk and Shed are driven with a fixed downwind heading: the Lean only
    applies on a Scrub map (see LEANING_SCRUB_LEAN_SITE_1), so the Gale-onset trigger itself is UNCOVERED."""
    for form, _plant in FORMS:
        for mode, name in (("on", "%s_acts" % form), ("off", "%s_toggle_off" % form)):
            with _comp(t, name, toggle=FORM_TOGGLES[form]):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_VenomvineFormsProof",
                                  method="ProofForm", args="%s|%s" % (form, mode))
                if _live(t):
                    txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                    _note(t, "%s proof (%s)" % (form, mode), txt[:300])
                    if txt.startswith("FAIL"):
                        _fail("%s (%s): %s" % (form, mode, txt[:400]))
                    if not txt.startswith("PASS"):
                        _unmeasured(t, "%s proof did not answer PASS/FAIL: %s" % (form, txt[:200]))


# --------------------------------------------------------------------------- chain: sweetline (last: jumps the clock)

@suite.chain("sweetline")
def sweetline_chain(t):
    _prep(t, "sweetline")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "sweetline_site_ready", poison=True):
            if _live(t):
                f, _ = _get_defs(t, "ThingDef/%s" % TREE, "label")
                ids["label"] = (f.get(TREE) or {}).get("label")
                if not ids["label"]:
                    _unmeasured(t, "could not read the tree's def label")
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (TREE, x, z), growth=1.0)
                tree = _things(t, TREE, "%d,%d,1,1" % (x, z))
                if not tree:
                    _unmeasured(t, "the sweetline tree did not stand after set_plants")
                ids["tree"] = tree[0]["id"]
        # SHRUBLAND_TREE_GUARDIAN_1: a newly spawned tree roosts 2-3 sleeping bark-wardens (owner card
        # 2026-10-03: visible, asleep against the trunk, "Roosting in the crown of <tree>" when selected).
        # Not yet proven here (first pokes, in order): a colonist harvesting the tree -> "stirring" then
        # "restless" messages then RM_RoostDefence on the wardens at ~60% of the work; the colonist walking
        # 19 cells off -> recovery and re-roost once the bar drains under 30%; Hunt on a sleeper (UNMEASURED).
        with _comp(t, "guardians_roost_on_spawn", toggle="sweetlineGuardiansEnabled"):
            if _live(t):
                # a warden is a PAWN: jawa/list_things does not list pawns (list_pawns carries kindDef), so the first live
                # run read 0 wardens whether or not any roosted (2026-10-03)
                wardens = [w for w in _rows(t, "%d,%d,9,9" % (x - 4, z - 4)).values() if w.get("kindDef") == "RM_Barkwarden"]
                _note(t, "bark-wardens within 4 of a fresh sweetline tree", [w.get("id") for w in wardens])
                if not 2 <= len(wardens) <= 3:
                    _fail("a freshly spawned sweetline tree roosts %d bark-wardens (expect 2-3)" % len(wardens))
                for w in wardens:
                    _, wl = _inspect(t, w["id"])
                    if not re.search(r"Roosting in the crown of ", " ".join(wl)):
                        _fail("bark-warden %s is not roosting: inspect %s" % (w.get("id"), wl))
                _, tl = _inspect(t, ids["tree"])
                if not re.search(r"Bark-wardens roost here \((2|3)\)\. Calm\.", " ".join(tl)):
                    _fail("tree inspect carries no calm roost line: %s" % tl)
        with _comp(t, "station_named_and_timed", toggle="sweetlineStationsEnabled"):
            if _live(t):
                label, lines = _inspect(t, ids["tree"])
                _note(t, "sweetline label / inspect", [label, lines])
                suffix = " (%s)" % ids["label"]
                if not (label and label.endswith(suffix) and len(label) > len(suffix)):
                    _fail("tree label %r carries no generated name before '(%s)'" % (label, ids["label"]))
                if not re.search(r"Loose .*(falls in|ready to fall)", " ".join(lines)):
                    _fail("no wool-timer line in the tree's inspect text: %s" % lines)
        with _comp(t, "station_toggle_off_plain", toggle="sweetlineStationsEnabled"):
            if _live(t):
                with _setting(t, "sweetlineStationsEnabled", False):
                    label, lines = _inspect(t, ids["tree"])
                if label != ids["label"] or re.search(r"Loose ", " ".join(lines)):
                    _fail("sweetlineStationsEnabled OFF but the tree still shows its station: "
                          "label %r, inspect %s" % (label, lines))
        with _comp(t, "station_sheds_wool", toggle="sweetlineStationsEnabled"):
            if _live(t):
                before = _stack_total(t, "RM_SweetlineWool", _rs(_rect(t)))
                cur = t.session._ticks()
                t.bridge_call("jawa/time_set_ticks", ticks=int(cur + 5.5 * 60000))   # past the 5-day timer
                t.wait_ticks(2100)                                    # one Long tick
                after = _stack_total(t, "RM_SweetlineWool", _rs(_rect(t)))
                # LIVE 2026-10-07 (both runs): 0 felt, the tree mature ("Ready to harvest", timer 14 h / 3.7 d before the
                # jump). The timer line now says which half broke: still "ready to fall" = RM_CompSweetlineStation.
                # CompTickLong never ran its shed in the 2100 ticks; "falls in ~5 days" = it ran and reset the timer, so
                # the felt went somewhere this count does not see; tree gone = it died across the jump.
                # RULED OUT: Plant.TickLong skipping comps -- decompiled Plant.TickLong calls base.TickLong (comps) and
                # TickList buckets every Long thing once per 2000 consecutive ticks, jump or not.
                standing = _things(t, TREE, "%d,%d,1,1" % (x, z))
                _, tl = _inspect(t, ids["tree"]) if standing else (None, ["<tree gone>"])
                _note(t, "sweetline wool beside the tree before / after a 5.5-day jump; tree inspect after",
                      [before, after, tl])
                if after - before < 5:
                    _fail("a mature sweetline tree shed %d sweetline felt after its 5-day timer passed "
                          "(expect 5); tree after the wait: %s" % (after - before, tl))
        # SWEETLINE_SCRATCHING_TREE_BUILD_1: a coated animal rubs its coat off at the trunk. The proof
        # (RM_SweetlineScratching.ProofOrderScratch via jawa/static_call) sets the sheep's coat and asks the
        # REAL job giver, so the giver's whole gate is exercised; the ~6 h MTB node above it is not.
        # Not yet proven here: a wild muffalo's coat growing (wild-coat patch), a pen keeping a herd from
        # an outside tree, the felt store paid out by a harvest.
        def order_scratch(cell):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_SweetlineScratching",
                              method="ProofOrderScratch", args="current|%d,%d|1" % cell)
            return str((r or {}).get("result", "")) or "no result: %r" % (r,)
        with _comp(t, "scratch_toggle_off_refused", toggle="sweetlineScratchingEnabled"):
            if _live(t):
                _spawn(t, "Sheep", x + 3, z + 3, faction="player")
                with _setting(t, "sweetlineScratchingEnabled", False):
                    text = order_scratch((x + 3, z + 3))
                _note(t, "scratch proof with scratching OFF", text)
                if not text.startswith("REFUSED"):
                    _fail("sweetlineScratchingEnabled OFF but a full-coated sheep was sent to scratch: %s" % text)
        with _comp(t, "scratch_drops_coat", toggle="sweetlineScratchingEnabled"):
            if _live(t):
                wool0 = _stack_total(t, "WoolSheep", _rs(_rect(t)))
                text = order_scratch((x + 3, z + 3))
                if not text.startswith("ORDERED"):
                    _fail("a tame full-coated sheep 4 cells from a calm sweetline tree was not sent: %s" % text)
                t.wait_ticks(1500)                                   # walk + 600 ticks of rubbing
                wool1 = _stack_total(t, "WoolSheep", _rs(_rect(t)))
                _, lines = _inspect(t, ids["tree"])
                _note(t, "sheep wool at the trunk before / after one rub; tree inspect", [wool0, wool1, lines])
                if wool1 - wool0 < 20:
                    _fail("one full sheep coat rubbed off left %d wool at the trunk (expect ~36 of 45 at "
                          "the 20%% felt share)" % (wool1 - wool0))
                if not re.search(r"Felted into the bark: \d+", " ".join(lines)):
                    _fail("no felt-store line on the tree after a rub: %s" % lines)
        with _comp(t, "visitors_toggle_off_quiet", toggle="sweetlineVisitorsEnabled"):
            if _live(t):
                def seen():
                    _, lines = _inspect(t, ids["tree"])
                    m = re.search(r"Visitors remembered: (\d+) camps, (\d+) pilgrims", " ".join(lines))
                    return (int(m.group(1)) + int(m.group(2))) if m else 0
                before_v = seen()
                with _setting(t, "sweetlineVisitorsEnabled", False):
                    t.bridge_call("jawa/time_set_ticks", ticks=int(t.session._ticks() + 13 * 60000))
                    t.wait_ticks(2100)
                off_v = seen()     # toggle restored, no tick has passed: the line is visible again
                _note(t, "sweetline visits before / after a 13-day jump, visitors OFF", [before_v, off_v])
                if off_v != before_v:
                    _fail("sweetlineVisitorsEnabled OFF but %d visit(s) were recorded" % (off_v - before_v))
                ids["visits_seen"] = seen
                ids["visits_base"] = off_v
        with _comp(t, "visitors_come_and_leave_marks", toggle="sweetlineVisitorsEnabled"):
            if _live(t):
                tok0 = _stack_total(t, "RM_SweetlineToken", _rs(_rect(t)))
                t.bridge_call("jawa/time_set_ticks", ticks=int(t.session._ticks() + 13 * 60000))
                t.wait_ticks(2100)
                got = ids["visits_seen"]() - ids["visits_base"]
                tok1 = _stack_total(t, "RM_SweetlineToken", _rs(_rect(t)))
                _note(t, "sweetline visits recorded / tokens before-after, visitors ON", [got, tok0, tok1])
                if got < 1:
                    _fail("no visit recorded after a 13-day jump with visitors ON (needs a home map, "
                          "a mature tree and sweetlineStationsEnabled)")
                if tok1 > tok0 + 3:
                    _fail("a single visit left %d tokens (cap is 3 near the tree)" % (tok1 - tok0))
        # SWEETLINE_TREE_MAP_STEP_1: the real map step, run on the current map with its chance forced
        # (RM_GenStep_SweetlineTrees.ProofMapStep). Trees land >= 40 cells from any standing one, so off
        # this chain's pad. Not proven here: a freshly GENERATED Leaning Scrub map carrying them (the
        # extraGenSteps wiring) -- first poke: generate a Leaning Scrub quicktest with the chance at 100%.
        def map_step(chance):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_GenStep_SweetlineTrees",
                              method="ProofMapStep", args="current|%s" % chance)
            return str((r or {}).get("result", "")) or "no result: %r" % (r,)
        # SWEETLINE_FELT_COMFORT_BUILD_1: the Comfort stat part, read through the real stat pipeline on an
        # armchair made of felt vs cloth. Not proven here: the +2 apparel thought (needs a dressed colonist).
        def comfort_delta():
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_SweetlineFeltProof",
                              method="ProofComfortDelta", args="Armchair")
            return str((r or {}).get("result", "")) or "no result: %r" % (r,)
        with _comp(t, "felt_comfort_toggle_off_plain", toggle="sweetlineFeltComfortEnabled"):
            if _live(t):
                with _setting(t, "sweetlineFeltComfortEnabled", False):
                    text = comfort_delta()
                _note(t, "felt armchair comfort delta, setting OFF", text)
                if text != "DELTA 0.00":
                    _fail("sweetlineFeltComfortEnabled OFF but a felt armchair still differs from cloth: %s" % text)
        with _comp(t, "felt_furniture_comfort", toggle="sweetlineFeltComfortEnabled"):
            if _live(t):
                text = comfort_delta()
                _note(t, "felt armchair comfort delta", text)
                if text != "DELTA 0.10":
                    _fail("a felt armchair's comfort is not cloth +0.10: %s" % text)
        with _comp(t, "map_step_chance_zero_plants_none", toggle="sweetlineStationsEnabled"):
            if _live(t):
                text = map_step(0)
                _note(t, "map step at chance 0", text)
                if text != "PLANTED 0":
                    _fail("the sweetline map step at chance 0 still planted: %s" % text)
        with _comp(t, "map_step_plants_one_or_two", toggle="sweetlineStationsEnabled"):
            if _live(t):
                text = map_step(1)
                _note(t, "map step at chance 1", text)
                m = re.match(r"PLANTED (\d+)$", text)
                if not m or not 1 <= int(m.group(1)) <= 2:
                    _fail("the sweetline map step at chance 1 planted %s (expect 1-2 trees)" % text)
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
            r = t.bridge_call("jawa/drain_log", contains="LeaningScrub", errorsOnly=True, limit=50)
            msgs = (_ok(r, "drain_log").get("messages") or [])
            bad = [m.get("text") for m in msgs]
            owned = set(DEFS_BY_TYPE.get("WeatherDef", []) + KINDS + PLANTS + [TREE])
            r2 = t.bridge_call("jawa/drain_log", contains="cross-reference", errorsOnly=True, limit=100)
            xref = [m.get("text") for m in ((r2 or {}).get("messages") or [])
                    if any(d in (m.get("text") or "") for d in owned)]
            _note(t, "log scan", {"leaningscrub errors": len(bad), "xref naming our defs": len(xref),
                                  "bufferLines": buf.get("totalInBuffer")})
            if bad or xref:
                _fail("log carries errors: %s" % [str(x)[:160] for x in (bad + xref)[:4]])
