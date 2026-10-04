"""validation.py -- modcheck suite for RimMandrake: Blue Desert (mandrake.rm.bluedesert).

Item BLUE_DESERT_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/BlueDesert.md (every
`## must be true` line ends in `-> chain.component` or `-> UNCOVERED: why`). Process:
design/RimMandrake/debug_process.md (a first script = a modcheck Suite + a walk).

PACKAGING. This dev folder is the SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json, wave 2 <= compose_wave 2), so the live tier is `baroque_wave0` and the packageId a
run must find active is `mandrake.rm.biomes`. `modcheck run BlueDesert` would swap to a list without the
composed biome: never use it. Run through the northstar driver (northstar_plan.py).

WHAT THE SUITE READS. Every defName this mod ships is parsed from its own Defs/ at import (so a new def is
covered without an edit) and must RESOLVE live: a def whose comp/extension type is missing is discarded
silently by the engine, and only a live get_defs sees that. Mechanics are read as STATE through the bridge
(positions, hediffs, things, temperatures, inspect text). Nothing here judges appearance and no component
takes a screenshot.

EVERY CHECK CAN FAIL. Each predicate has an arm that goes the other way inside the same chain (a control
kill that must NOT detonate, a control plant that must survive, a control room that must stay warm, a
toggle-off arm), so a harness that sees nothing records UNMEASURED, never PASS.
`selftest_bluedesert.py` runs the suite against a scripted fake game, healthy and with each mod behaviour
broken in turn, and proves the right component (and only that one) goes red.

THE SITE IS NOT A BLUE DESERT. The quicktest map the baroque_wave0 tier starts on is an ordinary map. Every
mechanic this suite drives is keyed on a def, a weather or a setting, NOT on the map's biome, so it is
drivable here. Three things are keyed on the biome and are NOT driven (walk lines say UNCOVERED, with the
reason): the ablation incident (IncidentDef.allowedBiomes), murrek re-seeding (RM_MurrekDrift.IsBlueDesert)
and the biome's own Haze carrier (biomeMapConditions). Making a real Blue Desert site needs the
Pyrelands-style re-tile recipe: follow-up BLUE_DESERT_SITE_1.

EXPECTED RED ON THE FIRST RUN (read the source, not guessed): `krissek_off_quiet`. The Mod Settings text
says "Native detonations off: both natives die like an ordinary animal", but KrissekCharge (and the other
eight non-vhaulk charge hediffs) carry the VANILLA HediffCompProperties_ExplodeOnDeath, which does not read
RM_BlueDesertSettings, so only the death-action worker and the dorrak hump-kill honour the toggle.
This check reads the quantity the player would see (does the killer's neighbour burn), so it goes red for
the reported reason. It is a MOD finding, not a script defect.

NOT DRIVEN HERE (UNCOVERED with the reason in the walk):
  * ablation incident, murrek re-seed, biome Haze carrier: need a Blue Desert map (BLUE_DESERT_SITE_1).
  * crack cue / burner halo VFX / ablation sounds: audio and effecters have no state read (visual/audio).
  * the thaw roll is statistical: the ON arm mines 48 blocks (16 rolls, a false RED needs 0.65^16 = 0.1%).
  * the kill-by-damage cold wax route and EMP/ion on non-vhaulk natives: no extra fixture value.
  * flyer flight in the air: never live-tested unattended (CLAUDE.md, three times); only canEverFly is read.

Settings fields are `public static` (RimMandrake.BlueDesert.RM_BlueDesertSettings). Every arm that changes
one restores it in a `finally`. `jawa/mod_settings_field` never writes ModSettings.xml; the one component
that needs the WriteSettings path (weather_apply) opens and closes the real Mod Settings dialog.
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
# (50, 50); the pads below reach 50 cells from it, so spawns landed "Cell is outside the map" (LIVE 2026-10-03). The
# margin makes the runner choose an anchor with that much room on every side.
suite = Suite("BlueDesert")
suite.anchor_margin = 65

SETTINGS = "RimMandrake.BlueDesert.RM_BlueDesertSettings"
HERE = os.path.dirname(os.path.abspath(__file__))
MOD_IDS = ("mandrake.rm.biomes", "mandrake.rm.bluedesert")      # open_mod_settings candidates, in order

# Shipped defaults, read off RM_BlueDesertMod.cs (public static field initialisers). The selftest
# re-reads the C# and fails if this table drifts from it.
DEFAULTS = {
    "masterEnabled": True, "nativeDetonationsEnabled": True, "floraChainReactionsEnabled": True,
    "floraExpansionEnabled": True,
    "coldWaxWarmReactiveEnabled": True, "butaneGutEnabled": True, "burnerHaloEnabled": True,
    "warmDetonationThresholdC": 5.0, "vhaulkHeatGateEnabled": True, "vhaulkEmpTrapEnabled": True,
    "ruledWeathersEnabled": True, "hazeExposureEnabled": True, "thawRollEnabled": True,
    "crackCueEnabled": True, "murrekReseedEnabled": True, "coldSinkEnabled": True,
    "coldSinkCapacityFactor": 1.0, "ablationSalvageEnabled": True, "ablationPaceFactor": 1.0,
    "vhaulkRoadEnabled": True, "vhaulkRoadDaysFactor": 1.0, "vhaulkDepartsEnabled": True,
    "vhaulkStayDaysFactor": 1.0, "ossivelChoirEnabled": True, "virrSongEnabled": True,
}
suite.toggles = sorted(DEFAULTS)

# Pad centres, as offsets from the map centre (the driver's anchor). Each chain clears its own pad first.
PADS = {"spawn": (0, 0), "fauna": (-50, -50), "flora": (-50, 0), "flora2": (-50, 50), "hump": (0, -50),
        "krissek": (0, 50), "vhaulk": (50, 0), "haze": (50, -50), "wax": (50, 50), "rack": (-25, -25),
        "thaw": (-25, 25), "road": (25, -25), "butane": (25, 25)}
PAD_SIZE = 24
ICE = "Ice"

RULED_WEATHERS = ("RM_Haze", "RM_IceSandDrift", "RM_IceFog")
STOCK_ZEROED = ("Fog", "Rain", "DryThunderstorm", "RainyThunderstorm", "FoggyRain", "SnowGentle", "SnowHard")
HAZE_CARRIER = "RM_BlueDesertHazeCarrier"
HAZE_FILM = "RM_HazeFilm"
THAW_DEBRIS = ("Steel", "ChunkSlagSteel", "ComponentIndustrial", "Plasteel")
BLAST_DAMAGE_DEFS = ("Flame", "Cut", "EMP")

_STATE = {}    # readings shared between components of ONE run


# --------------------------------------------------------------------------- shipped defs

def _read_defs():
    """({defType: [defName]}, {defName: ParentName}, {kind: charge hediff}) for every concrete def in this
    mod's Defs/, parsed per top-level element (never a fixed line number). Comments are stripped first."""
    wanted = ("ThingDef", "PawnKindDef", "WeatherDef", "HediffDef", "JobDef", "RecipeDef", "BiomeDef",
              "TerrainDef", "GameConditionDef", "IncidentDef", "SoundDef", "EffecterDef")
    by_type, parent, charge = {}, {}, {}
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
            name = nm.group(1).strip()
            by_type.setdefault(kind, []).append(name)
            pn = re.search(r'ParentName\s*=\s*"([^"]+)"', attrs)
            parent[name] = pn.group(1) if pn else None
            if kind == "PawnKindDef":
                sh = re.search(r"<startingHediffs>\s*<li>\s*<def>([^<]+)</def>", body)
                if sh:
                    charge[name] = sh.group(1).strip()
    return by_type, parent, charge


DEFS_BY_TYPE, _PARENT, CHARGE_OF = _read_defs()
SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_BY_TYPE.items() for n in ns)
NATIVES = sorted(CHARGE_OF)                       # the ten hydrocarbon natives, from their own kinds
FLORA = [n for n in DEFS_BY_TYPE.get("ThingDef", []) if _PARENT.get(n) == "PlantBase"]


def _xml_text(rel):
    with open(os.path.join(HERE, "Defs", rel), encoding="utf-8") as fh:
        return re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)


def _departure_label():
    m = re.search(r"<departureLetterLabel>([^<]+)</departureLetterLabel>",
                  _xml_text(os.path.join("ThingDefs_Races", "RM_BlueDesertFauna.xml")))
    return m.group(1).strip() if m else None


DEPARTURE_LABEL = _departure_label()


# --------------------------------------------------------------------------- helpers

def _roofed(r):
    """True when a jawa/get_roof_batch answer shows a real roof. LIVE 2026-10-03: the tool answers
    {cellsRead, roofs: [distinct roof names, "None" = open sky]} and has NO `roofedCells` key, so every
    `r.get("roofedCells")` test read an open or a sealed room alike as 0 and left the chain UNMEASURED."""
    r = r or {}
    return bool(r.get("roofedCells")) or any(x not in (None, "None") for x in (r.get("roofs") or []))


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
        print("[bdesert] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[bdesert-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
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


def _prep(t, name, size=PAD_SIZE, terrain=ICE):
    """Clear the pad and lay `terrain` (default vanilla Ice, the biome's own ground) so everything stands
    on walkable, plantable ground. The weather is parked on Clear first."""
    _pad(t, name)
    if _live(t):
        try:    # neutral until a chain locks its own; never let this abort the chain
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        except Exception as ex:
            print("[bdesert] neutral weather not set: %s" % ex, file=sys.stderr, flush=True)
    t.clear_area(size=size + 8)
    r = _rect(t, size + 8)
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


def _stack_total(t, defName, rect):
    """Total items of a def over `rect` (stack sizes summed): list_things counts THINGS."""
    return sum(int(w.get("stackCount") or 1) for w in _things(t, defName, rect, limit=500))


def _get_defs(t, defs, fields, deep=False):
    # LIVE 2026-10-03: without deep=True a list-of-record field (baseWeatherCommonalities) reads as class NAMES.
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, limit=200, deep=bool(deep))
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
        _fail("spawn_pawn(%s, %s) returned no pawn: %r" % (kind, faction, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _rows(t, rect=None, health=False, corpses=False, whole=False):
    """{pawnId: row}. Health rows are NESTED: row['health']['hediffs'] (MEASURED, list_pawns doc). Without a
    rect the read is limited to the current pad (+8 cells): a quicktest map holds dozens of wild animals and a
    health read of every one is slow. `whole=True` reads the whole map."""
    if rect is None and not whole:
        rect = _rs(_rect(t, PAD_SIZE + 8))
    if rect:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=health, includeCorpses=corpses,
                          rect=rect)
    else:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=health, includeCorpses=corpses)
    if not _live(t):
        return {}
    return dict((p.get("id"), p) for p in (_ok(r, "list_pawns").get("pawns") or []))


def _hediffs(row):
    return list(((row or {}).get("health") or {}).get("hediffs") or [])


def _hediff(row, name):
    """The first hediff row whose `def` is exactly `name`, else None."""
    for h in _hediffs(row):
        if isinstance(h, dict) and h.get("def") == name:
            return h
    return None


def _burned(row):
    """True when the pawn is dead or carries a Burn injury: the fingerprint of a Flame explosion."""
    if not row:
        return None
    return bool(row.get("dead")) or _hediff(row, "Burn") is not None


def _inspect(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return None, []
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows or rows[0].get("error"):
        _fail("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return rows[0].get("label"), list(rows[0].get("inspect") or [])


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
            print("[bdesert] RESTORE FAILED %s -> %r (set returned %r)" % (field, got, r),
                  file=sys.stderr, flush=True)
    except Exception as ex:   # restoring must never mask the verdict that got us here
        print("[bdesert] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)


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
    """Release the lock AND leave the map on vanilla Clear."""
    if t.session is not None:
        try:
            t.session.call("jawa/weather_set", weather="Clear", lockWeather=True)
            t.session.call("jawa/weather_set", unlock=True)
        except Exception as ex:
            print("[bdesert] weather reset failed: %s" % ex, file=sys.stderr, flush=True)


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


def _stable(t, fn, fire=False):
    """Run a chain body, then ALWAYS release the weather lock and clear the pad. `fire=True` for chains whose own
    blast/wick ignites the map (flame radius, burning wax): the fires are that chain's own act, declared expected and
    extinguished at the end so the next chain starts clean (live 2026-10-03: krissek_blast 26 fires, vhaulk_gates,
    cold_wax 23 -> fire_on_map surprise made every later component UNMEASURED)."""
    if fire:
        t.expect("fire", lambda e: True)
    try:
        fn()
    finally:
        if fire and t.session is not None:
            try:
                t.session.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
            except Exception as ex:
                print("[bdesert] extinguish failed: %s" % ex, file=sys.stderr, flush=True)
        _unlock_weather(t)
        if t.session is not None and getattr(t, "anchor", None):
            try:
                t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")
            except Exception as ex:
                print("[bdesert] pad cleanup failed: %s" % ex, file=sys.stderr, flush=True)


def _comp_names(r):
    comps = (r or {}).get("comps")
    if not isinstance(comps, list):
        return None
    return [c if isinstance(c, str) else (c.get("class") or c.get("compClass") or "") for c in comps]


def _cell_temp(t, x, z):
    r = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (x, z))
    if not _live(t):
        return None
    if not isinstance(r, dict) or r.get("success") is False or r.get("temperature") is None:
        _unmeasured(t, "cell_temperature(%d,%d) unreadable: %r" % (x, z, r))
    return float(r["temperature"])


def _damage(t, pid, ddef, amount, part=None):
    """One TakeDamage on a pawn or thing. `part` names a BodyPartDef (else the engine rolls one)."""
    if part:
        r = t.bridge_call("jawa/damage", damageDef=ddef, amount=amount, thingId=pid, bodyPart=part,
                          allowColonists=True)
    else:
        r = t.bridge_call("jawa/damage", damageDef=ddef, amount=amount, thingId=pid, allowColonists=True)
    if _live(t) and not (isinstance(r, dict) and r.get("success")):
        _unmeasured(t, "jawa/damage(%s %s on %s) refused: %r" % (ddef, amount, pid, r))
    return r


def _scrub(t, ids):
    """Kill the named pawns (kinetic damage, never a blast) so corpses can be cleared and a burning
    survivor cannot ignite the next trial's fresh pawns. Failures here are logged, not raised."""
    if t.session is None:
        return
    for pid in ids:
        try:
            t.session.call("jawa/damage", damageDef="Cut", amount=99999, thingId=pid, bodyPart="Brain",
                           allowColonists=True)
        except Exception as ex:
            print("[bdesert] scrub %s: %s" % (pid, ex), file=sys.stderr, flush=True)
    try:
        t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 28)), categories="All")
    except Exception as ex:
        print("[bdesert] scrub clear: %s" % ex, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- chain: defs

@suite.chain("defs")
def defs_chain(t):
    _pad(t, "spawn")
    with _comp(t, "defs_resolve"):
        if _live(t):
            # The parser must see the mod: a broken regex would read "all 0 defs resolve".
            if len(SHIPPED) < 60 or len(NATIVES) != 10 or not DEFS_BY_TYPE.get("WeatherDef") or len(FLORA) != 8:
                _fail("parsed only %d shipped defs / %d natives / %d flora from %s (parser broken?)"
                      % (len(SHIPPED), len(NATIVES), len(FLORA), HERE))
            r = t.bridge_call("jawa/get_defs", defs=";".join(SHIPPED), fields="defName", limit=200)
            _ok(r, "get_defs(all shipped)")
            if r.get("notFound"):
                _fail("%d shipped def(s) did not resolve live (silently discarded?): %s"
                      % (len(r["notFound"]), r["notFound"][:12]))
            if r.get("foundCount") != len(SHIPPED):
                _fail("get_defs foundCount %r != %d requested" % (r.get("foundCount"), len(SHIPPED)))
            # Sanity probe: the instrument must be able to say "absent".
            probe = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_BlueDesert_NoSuchDef_Probe",
                                  fields="defName")
            if "RM_BlueDesert_NoSuchDef_Probe" not in json.dumps((probe or {}).get("notFound")):
                _fail("sanity probe: an absent def was not reported in notFound: %r" % probe)
            _note(t, "shipped defs resolved", len(SHIPPED))

    with _comp(t, "flora_expansion_shape", toggle="floraExpansionEnabled"):
        # BLUEDESERT_FLORA_EXPANSION_BUILD_1: parsed from the mod's own XML, so it needs no live game.
        txt = _xml_text("ThingDefs_Plants/RM_BlueDesertFlora.xml")
        itxt = _xml_text("ThingDefs_Items/RM_FloraExpansionItems.xml")
        biome = _xml_text("BiomeDefs/RM_BlueDesert.xml")
        bad = []
        for n in ("RM_Qeshra", "RM_Kethevar", "RM_Lisqueth", "RM_Vashpuk"):
            m = re.search(r"<defName>%s</defName>(.*?)</ThingDef>" % n, txt, flags=re.S)
            if not m:
                bad.append("%s missing" % n)
                continue
            body = m.group(1)
            if "sowTags" in body:
                bad.append("%s is sowable" % n)
            if "PlantCharge" not in body:
                bad.append("%s has no PlantCharge" % n)
            hp = re.search(r"<MaxHitPoints>(\d+)</MaxHitPoints>", body)
            if not hp or int(hp.group(1)) > 40:
                bad.append("%s MaxHitPoints > 40" % n)
            if not re.search(r"<%s>[\d.]+</%s>" % (n, n), biome):
                bad.append("%s not in RM_BlueDesert wildPlants (XML element form)" % n)
        if "CompGlower" not in txt and "CompProperties_Glower" not in txt:
            bad.append("lisqueth has no glower")
        if "harvestAfterGrowth" not in txt:
            bad.append("vashpuk does not regrow")
        roe = re.search(r"<defName>RM_QeshraRoe</defName>(.*?)</ThingDef>", itxt, flags=re.S)
        lace = re.search(r"<defName>RM_CharLace</defName>(.*?)</ThingDef>", itxt, flags=re.S)
        if not roe or not all(c in roe.group(1) for c in ("CompProperties_Explosive", "CompProperties_TemperatureRuinable", "RM_CompRuinedDetonator")):
            bad.append("RM_QeshraRoe lacks the three cold-wax comps")
        if not lace or "CompProperties_Explosive" in lace.group(1):
            bad.append("RM_CharLace missing or carries CompExplosive")
        if bad:
            _fail("; ".join(bad))

    with _comp(t, "biome_weather_table"):
        if _live(t):
            f, _ = _get_defs(t, "BiomeDef/RM_BlueDesert", "baseWeatherCommonalities,biomeMapConditions", deep=True)
            row = f.get("RM_BlueDesert") or {}
            table = row.get("baseWeatherCommonalities")
            if not isinstance(table, list) or not table:
                _unmeasured(t, "post-patch weather table unreadable: %r" % (table,))
            w = dict((x.get("weather"), x.get("commonality") or 0) for x in table)
            _note(t, "BiomeDef weather table", w)
            missing = [n for n in ("Clear",) + RULED_WEATHERS if not w.get(n)]
            if missing:
                _fail("Clear / ruled weather(s) absent or zero in the biome table: %s" % missing)
            stock = [n for n in STOCK_ZEROED if w.get(n)]
            if stock:
                _fail("stock weather with commonality > 0 (the biome is dry, cold and still): %s" % stock)
            _STATE["biome_row"] = row

    with _comp(t, "biome_carrier_condition"):
        if _live(t):
            row = _STATE.get("biome_row")
            if row is None:
                _unmeasured(t, "biome row not read (biome_weather_table did not run)")
            conds = row.get("biomeMapConditions")
            if not isinstance(conds, list):
                _unmeasured(t, "BiomeDef.biomeMapConditions unreadable: %r" % (conds,))
            if HAZE_CARRIER not in [str(c) for c in conds]:
                _fail("RM_BlueDesert does not carry the Haze carrier condition (no film on a real map): %r"
                      % (conds,))

    with _comp(t, "biome_roster_and_density"):
        if _live(t):
            plants = [n for n in FLORA]
            r = t.bridge_call("jawa/biome_probe", biomes="RM_BlueDesert",
                              find=",".join(NATIVES + plants + ["AA_Thunderbeast"]),
                              animals=True, plants=True, limit=1, topN=60)
            _ok(r, "biome_probe")
            rows = r.get("biomes") or []
            if len(rows) != 1 or not isinstance(rows[0].get("findResults"), list):
                _unmeasured(t, "biome_probe returned no findResults for RM_BlueDesert: %r" % (r,))
            b = rows[0]
            state = dict((x.get("defName"), x.get("state")) for x in b["findResults"])
            bad = dict((n, state.get(n)) for n in NATIVES + plants if state.get(n) != "spawning")
            # AA_Thunderbeast is MayRequire sarg.alphaanimals: its state follows the mod list, so it is
            # recorded as evidence and never gates.
            _note(t, "biome roster states (AA_Thunderbeast follows the mod list)", state)
            dens = b.get("animalDensity")
            if not isinstance(dens, (int, float)) or dens <= 0:
                _fail("animalDensity %r: <= 0 means the animal roster can never spawn" % (dens,))
            pdens = b.get("plantDensity")
            if not isinstance(pdens, (int, float)) or pdens <= 0:
                _fail("plantDensity %r: <= 0 means no flora spawns" % (pdens,))
            if bad:
                _fail("roster row(s) not spawning in RM_BlueDesert (state per name): %s" % bad)

    with _comp(t, "charge_comps_wired"):
        if _live(t):
            bad = []
            want = {"RM_BlueIceMineable": "BlueIceThaw", "RM_ColdWax": "RuinedDetonator",
                    "RM_ColdSinkRack": "ColdSink"}
            for d in sorted(want) + FLORA:
                r = t.bridge_call("jawa/get_def", defName=d, defType="ThingDef")
                _ok(r, "get_def(%s)" % d)
                names = [str(n) for n in (_comp_names(r) or [])]
                if not names:
                    _unmeasured(t, "get_def(%s) returned no readable comps list: %r" % (d, r))
                need = want.get(d, "PlantCharge")
                if not any(need in n for n in names):
                    if d == "RM_ColdWax" and any(n in ("CompProperties", "Verse.CompProperties") for n in names):
                        # LIVE 2026-10-03: get_def lists the wax's detonator as the generic "CompProperties" (its
                        # compClass is not in the name), so the def cannot answer. A SPAWNED wax can: jawa/comp_read
                        # resolves a comp by a substring of its TYPE name on the live thing.
                        x, z = t.anchor
                        t.bridge_call("jawa/spawn_batch", ops="RM_ColdWax:%d,%d,1" % (x, z))
                        cr = t.bridge_call("jawa/comp_read", thing="RM_ColdWax", comp="RuinedDetonator")
                        t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="All")
                        if isinstance(cr, dict) and cr.get("success") and "RuinedDetonator" in str(cr.get("compType")):
                            continue
                        bad.append("RM_ColdWax carries no live RuinedDetonator comp (comp_read: %s)"
                                   % (str((cr or {}).get("message") or cr)[:200],))
                        continue
                    bad.append("%s has no %s comp: %s" % (d, need, names))
            if bad:
                _fail("; ".join(bad))

    with _comp(t, "rack_needs_no_power"):
        if _live(t):
            r = t.bridge_call("jawa/get_def", defName="RM_ColdSinkRack", defType="ThingDef")
            _ok(r, "get_def(RM_ColdSinkRack)")
            names = _comp_names(r)
            if not names:
                _unmeasured(t, "get_def(RM_ColdSinkRack) returned no readable comps list: %r" % (r,))
            powered = [n for n in names if "Power" in str(n)]
            if powered:
                _fail("the blue-ice rack carries a power comp (it must work in a blackout): %s" % powered)

    with _comp(t, "ablation_and_murrek_wired"):
        if _live(t):
            f, _ = _get_defs(t, "IncidentDef/RM_AblationSalvage_Wreckage;IncidentDef/RM_AblationSalvage_Metal;"
                                "IncidentDef/RM_AblationSalvage_Fallen", "allowedBiomes")
            bad = [n for n, row in sorted(f.items())
                   if "RM_BlueDesert" not in [str(b) for b in (row.get("allowedBiomes") or [])]]
            if len(f) != 3:
                _unmeasured(t, "could not read all three salvage incidents: %s" % sorted(f))
            if bad:
                _fail("salvage incident(s) not restricted to RM_BlueDesert (allowedBiomes): %s" % bad)
            w, _ = _get_defs(t, "WeatherDef/RM_IceSandDrift", "modExtensions")
            ext = (w.get("RM_IceSandDrift") or {}).get("modExtensions")
            if not isinstance(ext, list):
                _unmeasured(t, "WeatherDef.modExtensions unreadable: %r" % (ext,))
            if not any(str(e).endswith("RM_MurrekReseedExtension") for e in ext):
                _fail("RM_IceSandDrift carries no RM_MurrekReseedExtension (murrek never re-seed): %r" % ext)


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
    for field in ("burnerHaloEnabled", "crackCueEnabled", "murrekReseedEnabled", "ablationSalvageEnabled",
                  "ablationPaceFactor", "vhaulkRoadDaysFactor", "vhaulkStayDaysFactor"):
        with _comp(t, "%s_roundtrip" % field, toggle=field):
            if _live(t):
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s is not at its shipped default" % field)
                flipped = (not DEFAULTS[field]) if isinstance(DEFAULTS[field], bool) else DEFAULTS[field] * 2
                with _setting(t, field, flipped):
                    pass


# --------------------------------------------------------------------------- chain: fauna & flora

@suite.chain("fauna")
def fauna_chain(t):
    _prep(t, "fauna")
    rect = _rect(t)
    x0, z0 = rect[0] + 3, rect[1] + 4

    def body():
        ids = {}
        with _comp(t, "natives_spawn_charged"):
            if _live(t):
                for i, kind in enumerate(NATIVES):
                    ids[kind] = _spawn(t, kind, x0 + (i % 5) * 4, z0 + (i // 5) * 9)
                rows = _rows(t, health=True)
                bad = []
                for kind, pid in ids.items():
                    row = rows.get(pid)
                    if not row or row.get("kindDef") != kind or row.get("dead"):
                        bad.append("%s: no living pawn of that kind" % kind)
                    elif _hediff(row, CHARGE_OF[kind]) is None:
                        bad.append("%s: no %s hediff at spawn (the charge that makes it detonate)"
                                   % (kind, CHARGE_OF[kind]))
                _note(t, "natives spawned", {"asked": len(NATIVES), "bad": bad})
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "vrisk_can_fly"):
            if _live(t):
                pid = ids.get("RM_Vrisk")
                if not pid:
                    _unmeasured(t, "no vrisk on the pad to read")
                r = t.bridge_call("jawa/pawn_flight", action="report", pawn=pid)
                rows = (_ok(r, "pawn_flight").get("pawns") or [])
                if not rows or "canEverFly" not in rows[0]:
                    _unmeasured(t, "pawn_flight report carries no canEverFly: %r" % (rows[:1],))
                if rows[0].get("canEverFly") is not True:
                    _fail("RM_Vrisk canEverFly=%r (MaxFlightTime stat %r): the vrisk is described as a "
                          "flier" % (rows[0].get("canEverFly"), rows[0].get("maxFlightTimeStat")))
    _stable(t, body)


@suite.chain("flora")
def flora_chain(t):
    _prep(t, "flora")
    rect = _rect(t)

    def body():
        with _comp(t, "flora_spawns"):
            if _live(t):
                cells, why = {}, {}
                for i, d in enumerate(FLORA):
                    cx, cz = rect[0] + 3 + i * 4, rect[1] + 6
                    cells[d] = (cx, cz)
                    r = t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, cx, cz), growth=1.0)
                    if isinstance(r, dict) and r.get("rejectionReasons"):
                        why[d] = r.get("rejectionReasons")
                lost = [d for d, (cx, cz) in cells.items() if _count(t, d, "%d,%d,1,1" % (cx, cz)) < 1]
                # BLUEDESERT_FLORA_PLANT_REFUSAL_1: set_plants refuses on PlantUtility.CanEverPlantAt, whose
                # temperature gate reads Tile.MinTemperature - a lazy cache RimWorld never invalidates, so a
                # retile to -5 C can leave the warm bland tile's min standing (all 8 have maxGrowthTemperature -1).
                # Record the tool's own reasons and the tile's cached-vs-expected min/max beside the verdict.
                cache = None
                if lost:
                    tile = (t.bridge_call("jawa/map_info") or {}).get("tile")
                    if tile is not None:
                        cache = t.bridge_call("jawa/world_cache_audit", tiles=str(tile), includeTemps=True, limit=5)
                _note(t, "flora set", {"asked": len(FLORA), "lost": lost, "rejectionReasons": why,
                                       "tileTempCache": cache})
                if lost:
                    _fail("plant def(s) did not stand after set_plants: %s (reasons %r)" % (lost, why))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: flora detonation

def _row_of_plants(t, defn, x, z, n):
    """n plants in a straight row, one cell apart, growth 1; returns their thing rows (read back)."""
    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,%d,1" % (defn, x, z, n), growth=1.0)
    if not _live(t):
        return []
    return sorted(_things(t, defn, "%d,%d,%d,1" % (x, z, n)), key=lambda w: (w.get("position") or {}).get("x", 0))


@suite.chain("flora_chain")
def flora_chain_reaction(t):
    """A plant killed by DAMAGE detonates (radius 1.1, 40 flame) and kills its neighbours in turn; the same
    kill with the toggle off, or the master off, leaves the row standing."""
    _prep(t, "flora2")
    x, z = t.anchor
    plant = "RM_Palefloss"

    def run_row(label):
        row = _row_of_plants(t, plant, x - 4, z, 5)
        if _live(t) and len(row) != 5:
            _unmeasured(t, "%s: only %d of 5 palefloss stand in the row after set_plants" % (label, len(row)))
        if _live(t):
            _damage(t, row[0]["id"], "Cut", 999)
            t.wait_ticks(300)
            left = _count(t, plant, "%d,%d,5,1" % (x - 4, z))
            _note(t, "%s: plants left of 5 after the first is cut down" % label, left)
            t.bridge_call("jawa/destroy_batch", rects="%d,%d,7,3" % (x - 5, z - 1), categories="All")
            return left
        return None

    def body():
        with _comp(t, "plant_death_chains", toggle="floraChainReactionsEnabled"):
            left = run_row("chain ON")
            if _live(t) and left > 1:
                _fail("killing one palefloss by damage left %d of 5 standing: its neighbours were not "
                      "taken by the blast (no chain)" % left)
        with _comp(t, "plant_death_toggle_off_no_chain", toggle="floraChainReactionsEnabled"):
            if _live(t):
                with _setting(t, "floraChainReactionsEnabled", False):
                    left = run_row("chain OFF")
                if left != 4:
                    _fail("floraChainReactionsEnabled OFF but %d of 5 plants stand (expected exactly the 4 "
                          "neighbours): the blast still goes off" % left)
        with _comp(t, "plant_death_master_off_no_chain", toggle="masterEnabled"):
            if _live(t):
                with _setting(t, "masterEnabled", False):
                    left = run_row("master OFF")
                if left != 4:
                    _fail("masterEnabled OFF but %d of 5 plants stand (expected 4): the master switch does "
                          "not gate the flora blast" % left)
    _stable(t, body)


@suite.chain("flora_warm")
def flora_warm(t):
    """Warm detonation: ambient above `warmDetonationThresholdC` on two consecutive long ticks kills the
    plant. Three arms on the same three plants: threshold ABOVE ambient (alive), toggle OFF (alive), then
    the real arm (dead). The site's ambient is read, never assumed: at <= 5 C the threshold is lowered to
    ambient - 3 for the test arms (the mechanism compares ambient with the threshold, whatever its value)."""
    _prep(t, "flora")
    x, z = t.anchor
    wait = 4300      # two 2000-tick long ticks plus slack

    def body():
        arms = {}
        with _comp(t, "warm_site_ready", poison=True):
            if _live(t):
                amb = _cell_temp(t, x, z)
                low = round(min(5.0, amb - 3.0), 2)
                arms["amb"], arms["low"], arms["high"] = amb, low, round(amb + 8.0, 2)
                t.bridge_call("jawa/set_plants", ops="RM_Palefloss:%d,%d,1,1;RM_Palefloss:%d,%d,1,1;"
                              "RM_Palefloss:%d,%d,1,1" % (x - 6, z, x, z, x + 6, z), growth=1.0)
                n = _count(t, "RM_Palefloss", "%d,%d,15,1" % (x - 7, z))
                _note(t, "warm arms", arms)
                if n != 3:
                    _unmeasured(t, "only %d of 3 palefloss stand on the warm pad" % n)
        with _comp(t, "warm_threshold_above_keeps_plants", toggle="warmDetonationThresholdC"):
            if _live(t):
                with _setting(t, "warmDetonationThresholdC", arms["high"]):
                    _wait(t, wait)
                alive = _count(t, "RM_Palefloss", "%d,%d,15,1" % (x - 7, z))
                if alive != 3:
                    _fail("threshold %.1f C above the %.1f C ambient yet only %d of 3 plants live after %d "
                          "ticks (they should not detonate)" % (arms["high"], arms["amb"], alive, wait))
        with _comp(t, "warm_toggle_off_keeps_plants", toggle="floraChainReactionsEnabled"):
            if _live(t):
                with _setting(t, "warmDetonationThresholdC", arms["low"]):
                    with _setting(t, "floraChainReactionsEnabled", False):
                        _wait(t, wait)
                alive = _count(t, "RM_Palefloss", "%d,%d,15,1" % (x - 7, z))
                if alive != 3:
                    _fail("floraChainReactionsEnabled OFF but only %d of 3 plants live after %d warm ticks"
                          % (alive, wait))
        with _comp(t, "warm_detonates_plants"):
            if _live(t):
                with _setting(t, "warmDetonationThresholdC", arms["low"]):
                    _wait(t, wait)
                alive = _count(t, "RM_Palefloss", "%d,%d,15,1" % (x - 7, z))
                _note(t, "plants alive after the real arm", alive)
                if alive != 0:
                    _fail("%d of 3 plants survived %d ticks at %.1f C ambient with the threshold at %.1f C"
                          % (alive, wait, arms["amb"], arms["low"]))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: dorrak hump

@suite.chain("dorrak_hump")
def dorrak_hump(t):
    """The dorrak's gut is its Hump: destroying the hump kills it outright; destroying a leg does not; with
    native detonations off the hump is an ordinary part."""
    _prep(t, "hump")
    x, z = t.anchor

    def hit_until_missing(pid, part, label):
        """Hit `part` with escalating Cut damage until the part is missing or the pawn is dead (max 6)."""
        for amount in (60, 120, 240, 480, 960, 1920):
            _damage(t, pid, "Cut", amount, part)
            t.wait_ticks(30)
            row = _rows(t, health=True, corpses=True).get(pid)
            if not row:
                _unmeasured(t, "%s vanished from list_pawns after a hit" % label)
            gone = any(h.get("def") == "MissingBodyPart" and h.get("part") == part for h in _hediffs(row))
            if row.get("dead") or gone:
                return row, gone
        return row, False

    def body():
        ids = {}
        with _comp(t, "dorrak_site_ready", poison=True):
            if _live(t):
                for key, dx in (("hump_on", -9), ("leg_on", 0), ("hump_off", 9)):
                    ids[key] = _spawn(t, "RM_Dorrak", x + dx, z)
        with _comp(t, "hump_hit_kills", toggle="nativeDetonationsEnabled"):
            if _live(t):
                row, gone = hit_until_missing(ids["hump_on"], "Hump", "dorrak(hump,on)")
                _note(t, "hump hit, native detonations ON", {"hump_missing": gone, "dead": row.get("dead")})
                if not gone:
                    _unmeasured(t, "the hump was never destroyed by up to 1920 Cut damage: cannot judge")
                if not row.get("dead"):
                    _fail("the dorrak's Hump was destroyed and it is still alive: the 'wrong place' gut-kill "
                          "does not fire")
        with _comp(t, "leg_hit_does_not_kill"):
            if _live(t):
                row, gone = hit_until_missing(ids["leg_on"], "Leg", "dorrak(leg,on)")
                _note(t, "leg hit control", {"leg_missing": gone, "dead": row.get("dead")})
                if not gone:
                    _unmeasured(t, "the leg was never destroyed: cannot judge the control")
                if row.get("dead"):
                    _fail("destroying a LEG killed the dorrak: the hump-kill is not specific to the hump "
                          "(or the control hit overflowed into a vital part)")
        with _comp(t, "hump_toggle_off_ordinary_part", toggle="nativeDetonationsEnabled"):
            if _live(t):
                with _setting(t, "nativeDetonationsEnabled", False):
                    row, gone = hit_until_missing(ids["hump_off"], "Hump", "dorrak(hump,off)")
                _note(t, "hump hit, native detonations OFF", {"hump_missing": gone, "dead": row.get("dead")})
                if not gone:
                    _unmeasured(t, "the hump was never destroyed with the toggle off: cannot judge")
                if row.get("dead"):
                    _fail("nativeDetonationsEnabled OFF but destroying the Hump still killed the dorrak")
    _stable(t, body, fire=True)


# --------------------------------------------------------------------------- chain: krissek blast

@suite.chain("krissek_blast")
def krissek_blast(t):
    """The krissek 'goes, all at once, and the field goes with it'. A witness 2 cells away burns; a control
    8 cells away does not. With native detonations off it must die like an ordinary animal."""
    _prep(t, "krissek")
    x, z = t.anchor

    def trial():
        k = _spawn(t, "RM_Krissek", x - 6, z)
        near = _spawn(t, "Colonist", x - 4, z, faction="player")
        far = _spawn(t, "Colonist", x + 5, z, faction="player")
        for p in (near, far):
            t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
        _damage(t, k, "Cut", 9999, "Brain")
        t.wait_ticks(150)
        rows = _rows(t, health=True, corpses=True)
        out = {"krissek_dead": bool((rows.get(k) or {}).get("dead")), "near": _burned(rows.get(near)),
               "far": _burned(rows.get(far))}
        _scrub(t, [k, near, far])
        return out

    def body():
        with _comp(t, "krissek_death_blasts", toggle="nativeDetonationsEnabled"):
            if _live(t):
                res = trial()
                _note(t, "krissek death, detonations ON", res)
                if not res["krissek_dead"]:
                    _unmeasured(t, "the krissek did not die of 9999 Cut to the brain: %r" % res)
                if res["far"]:
                    _fail("the control colonist 5+ cells outside the 2.9-cell blast burned: %r" % res)
                if not res["near"]:
                    _fail("a colonist 2 cells from a dying krissek did not burn: no death blast: %r" % res)
        with _comp(t, "krissek_off_quiet", toggle="nativeDetonationsEnabled"):
            if _live(t):
                with _setting(t, "nativeDetonationsEnabled", False):
                    res = trial()
                _note(t, "krissek death, detonations OFF", res)
                if not res["krissek_dead"]:
                    _unmeasured(t, "the krissek did not die with the toggle off: %r" % res)
                if res["near"]:
                    _fail("nativeDetonationsEnabled OFF but a colonist 2 cells from the dying krissek still "
                          "burned: the krissek does not die like an ordinary animal (its RM_KrissekCharge "
                          "hediff carries the vanilla ExplodeOnDeath, which ignores the setting): %r" % res)
    _stable(t, body, fire=True)


# --------------------------------------------------------------------------- chain: vhaulk gates

@suite.chain("vhaulk_gates")
def vhaulk_gates(t):
    """The vhaulk's cistern (radius 15, 40 flame) detonates ONLY on a heat-family kill or an EMP hit on the
    living animal. Each trial: the vhaulk at x-8, a witness 6 cells away, a control 17 cells away."""
    _prep(t, "vhaulk")
    x, z = t.anchor

    def trial(ddef, amount, part):
        v = _spawn(t, "RM_Vhaulk", x - 8, z)
        wit = _spawn(t, "Colonist", x - 2, z, faction="player")
        far = _spawn(t, "Colonist", x + 9, z, faction="player")
        for p in (wit, far):
            t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
        hit = _damage(t, v, ddef, amount, part)
        t.wait_ticks(180)
        rows = _rows(t, health=True, corpses=True)
        # LIVE 2026-10-03: a detonation DESTROYS the corpses in the blast (no list_pawns row at all), so a missing row read as
        # "did not die"/"unknown". The damage call itself reports `dead`; a witness whose row is gone while the far control
        # still stands was destroyed by the blast (burned); both gone is unreadable.
        hit_dead = any(bool(r.get("dead")) for r in ((hit or {}).get("results") or []) if isinstance(r, dict))
        witness = _burned(rows.get(wit))
        if witness is None and rows.get(far):
            witness = True
        out = {"vhaulk_dead": hit_dead or bool((rows.get(v) or {}).get("dead")), "witness": witness,
               "control": _burned(rows.get(far))}
        return out, [v, wit, far]

    def comp_trial(name, ddef, amount, part, expect_blast, settings, toggle=None, expect_dead=True):
        with _comp(t, name, toggle=toggle):
            if not _live(t):
                return
            ids = []
            try:
                with contextlib.ExitStack() as st:
                    for field, value in settings:
                        st.enter_context(_setting(t, field, value))
                    res, ids = trial(ddef, amount, part)
                _note(t, "%s: %s %s" % (name, ddef, amount), res)
                if expect_dead and not res["vhaulk_dead"]:
                    _unmeasured(t, "the vhaulk did not die of %s %s: %r" % (ddef, amount, res))
                if res["control"]:
                    _fail("the control colonist 17 cells away burned (the blast is radius 15): %r" % res)
                if bool(res["witness"]) != expect_blast:
                    _fail("%s %s: expected %s but the witness 6 cells away %s: %r"
                          % (ddef, amount, "a blast" if expect_blast else "NO blast",
                             "burned" if res["witness"] else "did not burn", res))
            finally:
                _scrub(t, ids)

    def body():
        comp_trial("heat_kill_detonates", "Flame", 9999, "Brain", True, ())
        comp_trial("kinetic_kill_does_not", "Cut", 9999, "Brain", False, ())
        comp_trial("emp_on_living_detonates", "EMP", 100, None, True, (), expect_dead=False)
        comp_trial("heat_gate_off_any_death_detonates", "Cut", 9999, "Brain", True,
                   (("vhaulkHeatGateEnabled", False),), toggle="vhaulkHeatGateEnabled")
        comp_trial("emp_trap_off_is_ordinary_damage", "EMP", 100, None, False,
                   (("vhaulkEmpTrapEnabled", False),), toggle="vhaulkEmpTrapEnabled", expect_dead=False)
        comp_trial("native_toggle_off_no_blast", "Flame", 9999, "Brain", False,
                   (("nativeDetonationsEnabled", False),), toggle="nativeDetonationsEnabled")
        comp_trial("master_off_no_blast", "Flame", 9999, "Brain", False,
                   (("masterEnabled", False),), toggle="masterEnabled")
    _stable(t, body, fire=True)


# --------------------------------------------------------------------------- chain: haze

@suite.chain("haze")
def haze_chain(t):
    """The Haze carrier: an unroofed colonist in RM_Haze weather under the carrier condition takes the
    RM_HazeFilm and its severity climbs; a roofed one does not climb; a native never takes it; with the
    toggle off a new arrival takes none. (The condition is started by hand: the site is not a Blue Desert.)"""
    _prep(t, "haze")
    x, z = t.anchor
    # The carrier first applies the film 2500 ticks after the condition starts (damageIntervalTicks), then
    # the exposure comp climbs 0.6/day in 200-tick steps: >= 0.01 needs ~1000 ticks more. 3700 reads it.
    wait, wait_new = 3700, 2700

    def condition_active():
        r = t.bridge_call("jawa/weather_get")
        return any(c.get("def") == HAZE_CARRIER for c in ((r or {}).get("conditions") or []))

    def body():
        ids = {}
        with _comp(t, "haze_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_Haze")
                room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,7,7" % (x - 11, z - 3), stuffDef="Steel")
                _ok(room, "make_empty_room")
                ids["out"] = _spawn(t, "Colonist", x + 6, z + 6, faction="player")
                ids["in"] = _spawn(t, "Colonist", x - 8, z, faction="player")
                ids["native"] = _spawn(t, "RM_Vekkit", x + 8, z - 6)
                for p in (ids["out"], ids["in"]):
                    t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)
                roof = t.bridge_call("jawa/get_roof_batch", rects="%d,%d,5,5" % (x - 10, z - 2))
                if not _roofed(roof):
                    _unmeasured(t, "the sealed room is not roofed (get_roof_batch %r): cannot tell outdoors "
                                   "from indoors" % (roof,))
                r = t.bridge_call("jawa/game_condition", action="start", condition=HAZE_CARRIER,
                                  durationTicks=60000)
                _ok(r, "game_condition(start %s)" % HAZE_CARRIER)
                if not condition_active():
                    _unmeasured(t, "the carrier condition is not in weather_get.conditions after start")
        with _comp(t, "haze_film_on_outdoor_colonist", toggle="hazeExposureEnabled"):
            if _live(t):
                t.wait_ticks(wait)
                rows = _rows(t, health=True)
                out, inn = rows.get(ids["out"]), rows.get(ids["in"])
                if not out or not inn:
                    _unmeasured(t, "test colonist missing from list_pawns")
                f_out = _hediff(out, HAZE_FILM)
                f_in = _hediff(inn, HAZE_FILM)
                _note(t, "haze film severity (outdoor, roofed)", [f_out and f_out.get("severity"),
                                                              f_in and f_in.get("severity")])
                if f_out is None:
                    _fail("the unroofed colonist carries no %s after %d ticks of Haze under the carrier"
                          % (HAZE_FILM, wait))
                # LIVE 2026-10-03: severity read 0.0073 at 3700 ticks (a fixed 0.01 line is a timing guess, not the property).
                # The property is "it climbs while exposed": read again 800 ticks later and require a real rise.
                s1 = f_out.get("severity")
                if not isinstance(s1, (int, float)):
                    _unmeasured(t, "the film carries no numeric severity: %r" % (f_out,))
                t.wait_ticks(800)
                f_out2 = _hediff(_rows(t, health=True).get(ids["out"]), HAZE_FILM)
                s2 = (f_out2 or {}).get("severity")
                _note(t, "haze film severity after 800 more ticks", [s1, s2])
                if not isinstance(s2, (int, float)) or s2 < s1 + 0.002:
                    _fail("the unroofed colonist's film did not climb under continued exposure (severity %r -> %r over "
                          "800 ticks)" % (s1, s2))
                if f_in is not None and f_in.get("severity", 0) >= 0.003:
                    _fail("the ROOFED colonist's film climbed (severity %r): the exposure ignores the roof"
                          % (f_in.get("severity"),))
        with _comp(t, "haze_spares_natives"):
            if _live(t):
                row = _rows(t, health=True).get(ids["native"])
                if not row:
                    _unmeasured(t, "the vekkit left list_pawns")
                if _hediff(row, HAZE_FILM) is not None:
                    _fail("a vekkit (an immune native) carries %s" % HAZE_FILM)
        with _comp(t, "haze_toggle_off_new_arrival_clean", toggle="hazeExposureEnabled"):
            if _live(t):
                with _setting(t, "hazeExposureEnabled", False):
                    newcomer = _spawn(t, "Colonist", x + 4, z + 8, faction="player")
                    t.bridge_call("jawa/set_draft", pawnId=newcomer, drafted=True)
                    t.wait_ticks(wait_new)
                    row = _rows(t, health=True).get(newcomer)
                if not row:
                    _unmeasured(t, "the new colonist left list_pawns")
                if _hediff(row, HAZE_FILM) is not None:
                    _fail("hazeExposureEnabled OFF but a colonist who arrived afterwards took %s" % HAZE_FILM)
    try:
        _stable(t, body)
    finally:
        if t.session is not None:
            try:
                t.session.call("jawa/game_condition", action="end", condition=HAZE_CARRIER)
            except Exception as ex:
                print("[bdesert] could not end the carrier condition: %s" % ex, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- chain: butane gut

@suite.chain("butane")
def butane_chain(t):
    """A water-based grazer that eats the flora takes RM_ButaneGut; a native does not; with the toggle off
    nobody does. Each grazer is told to Ingest one palefloss (ordered job)."""
    _prep(t, "butane")
    x, z = t.anchor

    def feed(kind, dx):
        a = _spawn(t, kind, x + dx, z - 3)
        t.bridge_call("jawa/set_plants", ops="RM_Palefloss:%d,%d,1,1" % (x + dx, z), growth=1.0)
        plant = _things(t, "RM_Palefloss", "%d,%d,1,1" % (x + dx, z))
        if _live(t) and not plant:
            _unmeasured(t, "no palefloss stands at (%d,%d) for the %s to eat" % (x + dx, z, kind))
        t.bridge_call("jawa/pawn_need", pawn=a, action="need", need="Food", level=0.2)
        r = t.bridge_call("jawa/ordered_job", pawnId=a, jobDef="Ingest", targetAId=plant[0]["id"] if plant else None,
                          waitTicks=60, timeoutSeconds=25)
        if _live(t) and not (isinstance(r, dict) and r.get("accepted")):
            _unmeasured(t, "the bridge could not order the %s to Ingest the plant: %r" % (kind, r))
        t.wait_ticks(900)
        row = _rows(t, health=True).get(a)
        eaten = bool(plant) and _count(t, "RM_Palefloss", "%d,%d,1,1" % (x + dx, z)) == 0
        return row, eaten

    def body():
        with _comp(t, "foreign_grazer_takes_butane_gut", toggle="butaneGutEnabled"):
            if _live(t):
                row, eaten = feed("Muffalo", -8)
                _note(t, "foreign grazer", {"plant_eaten": eaten, "gut": _hediff(row, "RM_ButaneGut")})
                if not eaten:
                    _unmeasured(t, "the muffalo did not finish eating the plant in 900 ticks")
                if _hediff(row, "RM_ButaneGut") is None:
                    _fail("a muffalo ate palefloss and carries no RM_ButaneGut")
        with _comp(t, "native_grazer_exempt"):
            if _live(t):
                row, eaten = feed("RM_Dorrak", 0)
                _note(t, "native grazer", {"plant_eaten": eaten, "gut": _hediff(row, "RM_ButaneGut")})
                if not eaten:
                    _unmeasured(t, "the dorrak did not finish eating the plant in 900 ticks")
                if _hediff(row, "RM_ButaneGut") is not None:
                    _fail("a dorrak (a native, exempt in code) took RM_ButaneGut from its own flora")
        with _comp(t, "butane_toggle_off_clean", toggle="butaneGutEnabled"):
            if _live(t):
                with _setting(t, "butaneGutEnabled", False):
                    row, eaten = feed("Muffalo", 8)
                if not eaten:
                    _unmeasured(t, "the second muffalo did not finish eating the plant in 900 ticks")
                if _hediff(row, "RM_ButaneGut") is not None:
                    _fail("butaneGutEnabled OFF but a muffalo that ate palefloss took RM_ButaneGut")
    _stable(t, body, fire=True)


# --------------------------------------------------------------------------- chain: cold wax

@suite.chain("cold_wax")
def cold_wax(t):
    """Cold wax ruined by warmth starts its own wick (RM_CompRuinedDetonator -> CompExplosive.StartWick).
    The OFF arm runs FIRST and is its own control: it waits until the wax reads 'Ruined' and proves it is
    still there; the ON arm must then lose the wax."""
    _prep(t, "wax")
    x, z = t.anchor

    def run_arm(label, expect_gone):
        t.bridge_call("jawa/destroy_batch", rects="%d,%d,9,9" % (x - 4, z - 4), categories="All")
        room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,9,9" % (x - 4, z - 4), stuffDef="Steel")
        _ok(room, "make_empty_room")
        t.bridge_call("jawa/spawn_batch", ops="RM_ColdWax:%d,%d,5" % (x, z))
        wax = _things(t, "RM_ColdWax", "%d,%d,1,1" % (x, z))
        if _live(t) and not wax:
            _unmeasured(t, "%s: the cold wax did not spawn" % label)
        ruined_seen = False
        for _ in range(9):
            t.bridge_call("jawa/room_heat", x=x, z=z, mode="set", value=35.0)
            t.wait_ticks(500)
            if not _live(t):
                break
            left = _count(t, "RM_ColdWax", "%d,%d,1,1" % (x, z))
            if left == 0:
                return "gone", ruined_seen
            _, lines = _inspect(t, wax[0]["id"])
            if any("ruined" in str(l).lower() for l in lines):
                ruined_seen = True
                break
        if not _live(t):
            return None, None
        # ruined (or out of budget): give a wick (70~150 ticks) time to burn out, keeping the room hot
        t.bridge_call("jawa/room_heat", x=x, z=z, mode="set", value=35.0)
        t.wait_ticks(500)
        return ("gone" if _count(t, "RM_ColdWax", "%d,%d,1,1" % (x, z)) == 0 else "stands"), ruined_seen

    def body():
        with _comp(t, "wax_toggle_off_ruined_but_inert", toggle="coldWaxWarmReactiveEnabled"):
            if _live(t):
                with _setting(t, "coldWaxWarmReactiveEnabled", False):
                    end, ruined = run_arm("OFF", False)
                _note(t, "cold wax, warm-reactive OFF", {"end": end, "ruined_seen": ruined})
                if end == "gone":
                    # nothing but the ruin-to-wick route removes the wax, and it can burn out between two
                    # 500-tick polls, so "gone" is the defect itself, ruined seen or not
                    _fail("coldWaxWarmReactiveEnabled OFF: the wax is gone (it detonated anyway; ruined seen: %s)"
                          % ruined)
                if not ruined:
                    _unmeasured(t, "the wax never read 'Ruined' in ~4500 ticks at 35 C: cannot tell a control "
                                   "from a wax that is simply not ruining")
        with _comp(t, "wax_ruined_wicks_and_goes", toggle="coldWaxWarmReactiveEnabled"):
            if _live(t):
                end, ruined = run_arm("ON", True)
                _note(t, "cold wax, warm-reactive ON", {"end": end, "ruined_seen": ruined})
                if end != "gone":
                    _fail("warm-ruined cold wax with the mechanic ON is still standing (%s): the ruined "
                          "signal does not start the wick" % ("ruined seen" if ruined else "never ruined"))
    _stable(t, body, fire=True)


# --------------------------------------------------------------------------- chain: cold rack

_COLD_HELD = re.compile(r"cold held:\s*([\d.,]+)\s*h", re.I)


def _cold_held(t, rack_id):
    _, lines = _inspect(t, rack_id)
    m = _COLD_HELD.search(" ".join(str(l) for l in lines))
    if not m:
        _unmeasured(t, "rack inspect text has no 'Cold held: N h' line: %r" % (lines,))
    return float(m.group(1).replace(",", "."))


@suite.chain("cold_rack")
def cold_rack(t):
    """The blue-ice rack, no power: loaded with ice it pulls a warm sealed room down while an empty rack in
    an identical room does not; the ice is spent and melts into cans; with coldSinkEnabled off the same
    warm room is left alone. The capacity slider is set to its minimum (x0.25) so a drip fits in the run."""
    _prep(t, "rack")
    x, z = t.anchor
    a_rect, b_rect = (x - 11, z - 3, 7, 7), (x + 4, z - 3, 7, 7)
    ca, cb = (x - 8, z), (x + 7, z)
    ids = {}

    def body():
        with _comp(t, "rack_site_ready", poison=True):
            if _live(t):
                _set(t, "coldSinkCapacityFactor", 0.25)
                for r in (a_rect, b_rect):
                    _ok(t.bridge_call("jawa/make_empty_room", rect=_rs(r), stuffDef="Steel"), "make_empty_room")
                t.bridge_call("jawa/spawn_batch", ops="RM_ColdSinkRack:%d,%d;RM_ColdSinkRack:%d,%d" % (ca + cb))
                t.bridge_call("jawa/spawn_batch", ops="RM_BlueIce:%d,%d,30" % (ca[0] - 1, ca[1] + 1))
                racks = sorted(_things(t, "RM_ColdSinkRack", _rs(_rect(t))), key=lambda w: (w.get("position") or {}).get("x", 0))
                ice = _things(t, "RM_BlueIce", _rs(a_rect))
                if len(racks) != 2 or not ice:
                    _unmeasured(t, "fixture missing: %d racks, %d ice stacks" % (len(racks), len(ice)))
                ids["a"], ids["b"], ids["ice"] = racks[0]["id"], racks[1]["id"], ice[0]["id"]
                for rid in (ids["a"], ids["b"]):     # a bare spawn_batch building may carry no faction; Refuel wants ours
                    _note(t, "set_thing_props faction", t.bridge_call("jawa/set_thing_props", thing=rid,
                                                                      faction="PlayerColony"))
                ids["col"] = _spawn(t, "Colonist", ca[0] + 1, ca[1] + 2, faction="player")
                row = _rows(t).get(ids["col"]) or {}
                if not (a_rect[0] < (row.get("x") or -1) < a_rect[0] + 6 and a_rect[1] < (row.get("z") or -1) < a_rect[1] + 6):
                    _unmeasured(t, "the colonist was scattered out of room A: %r" % ((row.get("x"), row.get("z")),))
                r = t.bridge_call("jawa/ordered_job", pawnId=ids["col"], jobDef="Refuel", targetAId=ids["a"],
                                  targetBId=ids["ice"], count=30, waitTicks=60, timeoutSeconds=25)
                if not (isinstance(r, dict) and r.get("accepted")):
                    _unmeasured(t, "the Refuel order was not accepted: %r" % (r,))
                t.wait_ticks(900)
                ids["held0"] = _cold_held(t, ids["a"])
                if ids["held0"] <= 0:
                    _unmeasured(t, "rack A holds no cold after the refuel job (held %r)" % ids["held0"])
                for c in (ca, cb):
                    t.bridge_call("jawa/room_heat", x=c[0], z=c[1], mode="set", value=28.0)
        with _comp(t, "rack_cools_loaded_room_only", toggle="coldSinkCapacityFactor"):
            if _live(t):
                t.wait_ticks(1500)
                ta, tb = _cell_temp(t, ca[0], ca[1]), _cell_temp(t, cb[0], cb[1])
                _note(t, "room temperatures after 1500 ticks (A loaded, B empty)", [ta, tb])
                if tb - ta < 3.0:
                    _fail("the loaded room is only %.1f C cooler than the empty control (A %.1f, B %.1f): the "
                          "rack does not cool the room" % (tb - ta, ta, tb))
        with _comp(t, "rack_spends_ice_and_drips"):
            if _live(t):
                t.wait_ticks(2100)
                held = _cold_held(t, ids["a"])
                cans = _stack_total(t, "RM_BlueIceMeltwaterCan", _rs(_rect(t)))
                _note(t, "after 3600 ticks", {"held_h": held, "held0_h": ids["held0"], "cans": cans})
                if held >= ids["held0"] - 0.01:
                    _fail("rack A's cold store did not run down (%.2f h -> %.2f h): no ice is spent" %
                          (ids["held0"], held))
                if cans < 3:
                    _fail("no meltwater cans after the rack spent its ice (cans %d): the drip never happens"
                          % cans)
                ids["held1"] = held
        with _comp(t, "rack_toggle_off_leaves_room_alone", toggle="coldSinkEnabled"):
            if _live(t):
                with _setting(t, "coldSinkEnabled", False):
                    for c in (ca, cb):
                        t.bridge_call("jawa/room_heat", x=c[0], z=c[1], mode="set", value=28.0)
                    t.wait_ticks(1500)
                    ta, tb = _cell_temp(t, ca[0], ca[1]), _cell_temp(t, cb[0], cb[1])
                    held = _cold_held(t, ids["a"])
                _note(t, "coldSinkEnabled OFF: temperatures and cold held", [ta, tb, held])
                if abs(ta - tb) > 3.0:
                    _fail("coldSinkEnabled OFF but room A still differs from the empty control by %.1f C" %
                          abs(ta - tb))
                if held < ids["held1"] - 0.01:
                    _fail("coldSinkEnabled OFF but the rack's ice kept being spent (%.2f h -> %.2f h)" %
                          (ids["held1"], held))
    try:
        _stable(t, body)
    finally:
        _restore(t, "coldSinkCapacityFactor")


# --------------------------------------------------------------------------- chain: thaw (quarry)

def _pillars(t, x0, z0, cols, rows):
    ops = ";".join("RM_BlueIceMineable:%d,%d" % (x0 + 2 * c, z0 + 2 * r) for r in range(rows) for c in range(cols))
    t.bridge_call("jawa/spawn_batch", ops=ops)
    return cols * rows


@suite.chain("thaw")
def thaw_chain(t):
    """Blue-ice quarrying: every third block mined rolls 35% for a fallen-debris find. The OFF arm (24
    blocks, thawRollEnabled off) must yield NO debris; the ON arm (48 blocks, 16 rolls: a false RED needs
    0.65^16 = 0.1%) must yield some. Both arms must also yield blue ice (15 per block)."""
    _prep(t, "thaw")
    x, z = t.anchor
    rect = _rect(t)

    def quarry(cols, rows, miners, wait):
        """Place cols*rows pillars, queue them across `miners` colonists, wait, return (mined, ice, debris)."""
        n = _pillars(t, x - 9, z - 6, cols, rows)
        stones = _things(t, "RM_BlueIceMineable", _rs(rect), limit=500)
        if _live(t) and len(stones) != n:
            _unmeasured(t, "only %d of %d blue-ice blocks stand after spawn_batch" % (len(stones), n))
        pawns = []
        if _live(t):
            for i in range(miners):
                pid = _spawn(t, "Colonist", x - 11, z - 6 + 3 * i, faction="player")
                t.bridge_call("jawa/set_pawn_skill", pawn=pid, skill="Mining", level=15)
                t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
                t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
                pawns.append(pid)
            for st in stones:      # JobDriver_Mine fails a cell that carries no Mine designation
                pos = st.get("position") or {}
                t.bridge_call("jawa/designate_batch", action="add", designation="Mine",
                              rect="%d,%d,1,1" % (pos.get("x", -1), pos.get("z", -1)))
            for i, st in enumerate(stones):
                r = t.bridge_call("jawa/ordered_job", pawnId=pawns[i % miners], jobDef="Mine",
                                  targetAId=st["id"], queue=True, waitTicks=0)  # waitTicks>0 on a paused clock burns the whole tool timeout (~17 s each; 72 orders = 20 min, LIVE 2026-10-03)
                if i < miners and not (isinstance(r, dict) and r.get("accepted")):
                    _unmeasured(t, "the first Mine order to miner %d was refused: %r" % (i, r))
        _wait(t, wait)
        if not _live(t):
            return 0, 0, 0
        left = _count(t, "RM_BlueIceMineable", _rs(rect))
        ice = _stack_total(t, "RM_BlueIce", _rs(rect))
        deb = sum(_stack_total(t, d, _rs(rect)) for d in THAW_DEBRIS)
        return n - left, ice, deb

    def body():
        with _comp(t, "thaw_toggle_off_mines_cleanly", toggle="thawRollEnabled"):
            if _live(t):
                with _setting(t, "thawRollEnabled", False):
                    mined, ice, deb = quarry(6, 4, 4, 3200)
                _note(t, "quarry, roll OFF", {"mined": mined, "ice": ice, "debris": deb})
                if mined < 12:
                    _unmeasured(t, "only %d of 24 blocks were mined in 3200 ticks: miners too slow/idle" % mined)
                if ice < 10 * mined:
                    _fail("%d blocks mined but only %d blue ice came out (15 per block expected)" % (mined, ice))
                if deb:
                    _fail("thawRollEnabled OFF but %d fallen-debris item(s) appeared: blue ice must mine "
                          "cleanly" % deb)
        with _comp(t, "thaw_roll_finds_debris", toggle="thawRollEnabled"):
            if _live(t):
                _prep(t, "thaw")
                mined, ice, deb = quarry(8, 6, 4, 6200)
                _note(t, "quarry, roll ON", {"mined": mined, "ice": ice, "debris": deb})
                if mined < 36:
                    _unmeasured(t, "only %d of 48 blocks were mined (need >= 36 = 12 rolls for a 99.4%% "
                                   "reading): miners too slow" % mined)
                if ice < 10 * mined:
                    _fail("%d blocks mined but only %d blue ice came out" % (mined, ice))
                if not deb:
                    _fail("%d blocks mined (%d rolls at 35%%) and not one debris find: the thaw roll does not "
                          "fire (0.65^%d = %.2f%% by chance)" % (mined, mined // 3, mined // 3,
                                                                 100 * 0.65 ** (mined // 3)))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: vhaulk road

def _growth_pct(t, plant_id):
    _, lines = _inspect(t, plant_id)
    m = re.search(r"growth[^0-9]*([\d.]+)\s*%", " ".join(str(l) for l in lines), re.I)
    if not m:
        _unmeasured(t, "plant inspect text has no 'Growth N%%' line: %r" % (lines,))
    return float(m.group(1))


@suite.chain("vhaulk_road")
def vhaulk_road(t):
    """A walking vhaulk presses a temporary rime road (RM_RimeRoad, temp-terrain layer) and crops the
    flora it passes down to growth 0.08. With vhaulkRoadEnabled off it walks like any animal."""
    _prep(t, "road")
    x, z = t.anchor

    def walk(row_z, label):
        """Spawn a vhaulk at the west end of row `row_z`, walk it east; plants on the path and one control."""
        v = _spawn(t, "RM_Vhaulk", x - 10, row_z)
        t.bridge_call("jawa/set_plants", ops="RM_Palefloss:%d,%d,1,1;RM_Palefloss:%d,%d,1,1;RM_Palefloss:%d,%d,1,1"
                      % (x - 2, row_z, x + 3, row_z, x, row_z + 7), growth=1.0)
        on_path = _things(t, "RM_Palefloss", "%d,%d,1,1" % (x - 2, row_z)) + \
            _things(t, "RM_Palefloss", "%d,%d,1,1" % (x + 3, row_z))
        control = _things(t, "RM_Palefloss", "%d,%d,1,1" % (x, row_z + 7))
        if _live(t) and (len(on_path) != 2 or len(control) != 1):
            _unmeasured(t, "%s: path plants %d/2, control plants %d/1 stand" % (label, len(on_path), len(control)))
        r = t.bridge_call("jawa/ordered_job", pawnId=v, jobDef="Goto", targetAX=x + 10, targetAZ=row_z,
                          waitTicks=60, timeoutSeconds=25)
        if _live(t) and not (isinstance(r, dict) and r.get("accepted")):
            _unmeasured(t, "%s: the bridge could not order the wild vhaulk to walk: %r" % (label, r))
        t.wait_ticks(1500)
        if not _live(t):
            return None
        lr = t.bridge_call("jawa/get_terrain_layers", rect="%d,%d,25,5" % (x - 12, row_z - 2), limit=400)
        cells = _ok(lr, "get_terrain_layers").get("cells") or []
        if not cells:
            _unmeasured(t, "%s: get_terrain_layers returned no cells" % label)
        road = sum(1 for c in cells if "RM_RimeRoad" in str(c.get("temp")))
        # RULED OUT in the walk: "laying the road kills the flora under it" (TerrainGrid vanishes plants on a
        # terrain change, the charge comp only fires on KillFinalize). Guard: the path plants must still stand.
        standing = sum(_count(t, "RM_Palefloss", "%d,%d,1,1" % (px, row_z)) for px in (x - 2, x + 3))
        if standing != 2:
            _fail("%s: only %d of 2 path plants still stand after the walk: the road/crop destroyed flora "
                  "(and a destroyed plant is a candidate detonation)" % (label, standing))
        crop = [_growth_pct(t, p["id"]) for p in on_path]
        ctrl = _growth_pct(t, control[0]["id"])
        pos = (_rows(t).get(v) or {})
        return {"road_cells": road, "path_growth": crop, "control_growth": ctrl, "vhaulk_x": pos.get("x")}

    def body():
        with _comp(t, "road_laid_and_flora_cropped", toggle="vhaulkRoadEnabled"):
            res = walk(z - 4, "road ON")
            if _live(t):
                _note(t, "vhaulk walk, road ON", res)
                if (res["vhaulk_x"] or 0) < x:
                    _unmeasured(t, "the vhaulk barely moved (x %r): cannot judge a road" % (res["vhaulk_x"],))
                if res["road_cells"] < 12:
                    _fail("a vhaulk walked 20 cells and only %d cells of RM_RimeRoad lie behind it" % res["road_cells"])
                if res["control_growth"] < 90:
                    _unmeasured(t, "the control plant is not at full growth (%r%%)" % res["control_growth"])
                if any(g > 20 for g in res["path_growth"]):
                    _fail("flora on the vhaulk's path was not cropped (growth %s%%, expected <= 8%%)" % res["path_growth"])
        with _comp(t, "road_toggle_off_walks_clean", toggle="vhaulkRoadEnabled"):
            if _live(t):
                with _setting(t, "vhaulkRoadEnabled", False):
                    res = walk(z + 6, "road OFF")
                _note(t, "vhaulk walk, road OFF", res)
                if (res["vhaulk_x"] or 0) < x:
                    _unmeasured(t, "the vhaulk barely moved (x %r): cannot judge" % (res["vhaulk_x"],))
                if res["road_cells"]:
                    _fail("vhaulkRoadEnabled OFF but %d cells of road were laid" % res["road_cells"])
                if any(g < 90 for g in res["path_growth"]):
                    _fail("vhaulkRoadEnabled OFF but path flora was cropped (growth %s%%)" % res["path_growth"])
    _stable(t, body)


# --------------------------------------------------------------------------- chain: weather apply

def _cfg_dir():
    return os.environ.get("BLUEDESERT_CONFIG_DIR") or os.path.join(
        os.path.expanduser("~"), "AppData", "LocalLow", "Ludeon Studios", "RimWorld by Ludeon Studios", "Config")


def _cfg_mtime():
    files = glob.glob(os.path.join(_cfg_dir(), "Mod_*RM_BlueDesertMod.xml"))
    return max(os.path.getmtime(f) for f in files) if files else None


def _weather_table(t):
    f, _ = _get_defs(t, "BiomeDef/RM_BlueDesert", "baseWeatherCommonalities", deep=True)
    table = (f.get("RM_BlueDesert") or {}).get("baseWeatherCommonalities")
    if not isinstance(table, list) or not table:
        _unmeasured(t, "weather table unreadable: %r" % (table,))
    return dict((x.get("weather"), x.get("commonality") or 0) for x in table)


def _apply_dialog(t, mod_id):
    """Open then close the Mod Settings page for `mod_id`, so Mod.WriteSettings runs, as a player does."""
    r = t.session.call("rimworld/open_mod_settings", modId=mod_id, replaceExisting=True)
    ok = bool((r or {}).get("success"))
    t.session.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    return ok


@suite.chain("weather_apply")
def weather_apply(t):
    """ruledWeathersEnabled only reaches the biome's weather table when the settings dialog closes
    (WriteSettings -> RM_BlueDesertWeatherTable.Apply). Off: the three ruled weathers read 0 and Clear is
    untouched; back on: the authored values return. If the dialog never wrote this mod's settings file the
    component is UNMEASURED, never a pass and never a mod fail."""
    _pad(t, "spawn")

    def body():
        with _comp(t, "ruled_weathers_toggle_applies", toggle="ruledWeathersEnabled"):
            if not _live(t):
                return
            before = _weather_table(t)
            if not all(before.get(w) for w in RULED_WEATHERS):
                _fail("the ruled weathers are not at their authored values before the test: %s"
                      % dict((w, before.get(w)) for w in RULED_WEATHERS))
            applied = None
            used = [None]
            try:
                _set(t, "ruledWeathersEnabled", False)
                for mod_id in MOD_IDS:
                    mt0 = _cfg_mtime()
                    opened = _apply_dialog(t, mod_id)
                    off = _weather_table(t)
                    wrote = (_cfg_mtime() or 0) > (mt0 or 0)
                    if not any(off.get(w) for w in RULED_WEATHERS):
                        applied = (mod_id, off)
                        used[0] = mod_id
                        break
                    if wrote:
                        _fail("the Mod Settings dialog for %s wrote the Blue Desert settings but the ruled "
                              "weathers still read %s: WriteSettings does not apply the toggle"
                              % (mod_id, dict((w, off.get(w)) for w in RULED_WEATHERS)))
                    _note(t, "dialog %s opened=%s wrote_config=%s" % (mod_id, opened, wrote), None)
                if applied is None:
                    _unmeasured(t, "no Mod Settings dialog (%s) wrote the Blue Desert settings file: the "
                                   "WriteSettings path is unreachable from the bridge" % ", ".join(MOD_IDS))
                mod_id, off = applied
                if off.get("Clear") != before.get("Clear"):
                    _fail("turning the ruled weathers off also changed Clear (%r -> %r)"
                          % (before.get("Clear"), off.get("Clear")))
            finally:
                _restore(t, "ruledWeathersEnabled")
                for mod_id in ([used[0]] if used[0] else MOD_IDS):
                    try:
                        _apply_dialog(t, mod_id)
                    except Exception as ex:
                        print("[bdesert] restore apply failed: %s" % ex, file=sys.stderr, flush=True)
            after = _weather_table(t)
            if any(after.get(w) != before.get(w) for w in RULED_WEATHERS):
                _fail("the ruled weathers did not return to their authored values after the toggle went back "
                      "on: before %s after %s" % (dict((w, before.get(w)) for w in RULED_WEATHERS),
                                                  dict((w, after.get(w)) for w in RULED_WEATHERS)))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: ablation gate

@suite.chain("ablation_gate")
def ablation_gate(t):
    _pad(t, "spawn")
    with _comp(t, "ablation_only_in_blue_desert"):
        if _live(t):
            info = t.bridge_call("jawa/map_info")
            biome = (info or {}).get("mapBiome")
            if not biome:
                _unmeasured(t, "map_info carries no mapBiome: %r" % (info,))
            if biome == "RM_BlueDesert":
                _unmeasured(t, "the site IS a Blue Desert map: this negative gate cannot be read here")
            bad = []
            for inc in ("RM_AblationSalvage_Wreckage", "RM_AblationSalvage_Metal", "RM_AblationSalvage_Fallen"):
                r = t.bridge_call("jawa/fire_incident", incidentDef=inc, dryRun=True)
                if not isinstance(r, dict) or "canFireNow" not in r:
                    _unmeasured(t, "fire_incident dryRun carries no canFireNow for %s: %r" % (inc, r))
                if r["canFireNow"]:
                    bad.append(inc)
            _note(t, "dry-run canFireNow on a %s map" % biome, {"fires_here": bad})
            if bad:
                _fail("salvage incident(s) can fire on a %s map (they are the Blue Desert's alone): %s"
                      % (biome, bad))


# --------------------------------------------------------------------------- chain: soundscape

SOUND_PROOF = "RimMandrake.BlueDesert.RM_BlueDesertSoundProof"


def _proof(t, method, mode, label):
    """Run one C# proof hook (spawns, drives the SHIPPED Rescan on a synthetic clock, cleans up) and map
    its PASS/FAIL/UNMEASURED answer onto the component."""
    r = t.bridge_call("jawa/static_call", type=SOUND_PROOF, method=method, args=mode)
    if not _live(t):
        return
    text = str((r or {}).get("result") or (r or {}).get("value") or r)
    _note(t, label, {"answer": text[:300]})
    if text.startswith("FAIL"):
        _fail("%s: %s" % (label, text[:400]))
    if not text.startswith("PASS"):
        _unmeasured(t, "%s: proof did not answer PASS/FAIL: %s" % (label, text[:200]))


@suite.chain("soundscape")
def soundscape(t):
    """BLUEDESERT_MECHANICS_BUILD_1 §5 (RM_BlueDesertSoundscape.cs). The sound itself has no state read;
    what is read is the STATE that drives it: a pack of ossivels sings, a big pawn near them silences the
    choir, the silence outlasts the intruder by the hold, and a virr in wind sings with a pitch that climbs
    with growth. Each toggle-off arm must stay silent."""
    _pad(t, "spawn")
    with _comp(t, "choir_sings_and_falls_silent", toggle="ossivelChoirEnabled"):
        _proof(t, "ProofChoir", "on", "choir on")
    with _comp(t, "choir_toggle_off_silent", toggle="ossivelChoirEnabled"):
        _proof(t, "ProofChoir", "off", "choir off")
    try:
        with _comp(t, "virr_sings_in_wind_pitch_climbs", toggle="virrSongEnabled"):
            _lock_weather(t, "RM_IceSandDrift")
            _wait(t, 600)
            _proof(t, "ProofVirr", "on", "virr on")
        with _comp(t, "virr_toggle_off_silent", toggle="virrSongEnabled"):
            _proof(t, "ProofVirr", "off", "virr off")
    finally:
        _unlock_weather(t)


# --------------------------------------------------------------------------- chain: vhaulk departs

@suite.chain("vhaulk_departs")
def vhaulk_departs(t):
    """A wild vhaulk walks off the map after its stay (x0.1 here: 12000-30000 ticks) with a letter, and
    never silently despawns. The SLOWEST component in the suite; it runs last."""
    _pad(t, "spawn")

    def body():
        with _comp(t, "vhaulk_walks_off_with_a_letter", toggle="vhaulkDepartsEnabled"):
            if not _live(t):
                return
            info = t.bridge_call("jawa/map_info")
            sx, sz = (info or {}).get("sizeX"), (info or {}).get("sizeZ")
            if not sx or not sz:
                _unmeasured(t, "map_info has no size: %r" % (info,))
            if not DEPARTURE_LABEL:
                _unmeasured(t, "the departure letter label could not be parsed from the fauna def")
            before = len((t.bridge_call("jawa/letter_list") or {}).get("letters") or [])
            with _setting(t, "vhaulkStayDaysFactor", 0.01):     # the code clamps this to 0.1 (x2-5 days)
                v = _spawn(t, "RM_Vhaulk", 6, sz // 2)
                gone = False
                for _ in range(7):
                    _wait(t, 6000)
                    if v not in _rows(t, whole=True):
                        gone = True
                        break
            letters = (t.bridge_call("jawa/letter_list") or {}).get("letters") or []
            labels = [(l.get("label") or {}).get("RawText") if isinstance(l.get("label"), dict) else l.get("label") for l in letters]
            _note(t, "after the wait", {"gone": gone, "letters_before": before, "labels": labels[-6:]})
            if not gone:
                _fail("the vhaulk was still on the map after 42000 ticks with the stay factor at its floor "
                      "(max stay 0.5 day = 30000 ticks plus the walk): it never walks off")
            if DEPARTURE_LABEL not in labels:
                _fail("the vhaulk left the map but no '%s' letter arrived (labels: %s): a silent departure"
                      % (DEPARTURE_LABEL, labels[-6:]))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: log

@suite.chain("log")
def log_chain(t):
    _pad(t, "spawn")
    with _comp(t, "log_clean"):
        if _live(t):
            buf = t.bridge_call("jawa/drain_log", limit=1)
            if not (buf or {}).get("totalInBuffer"):
                _unmeasured(t, "drain_log buffer is empty: cannot see the log at all")
            r = t.bridge_call("jawa/drain_log", contains="BlueDesert", errorsOnly=True, limit=50)
            bad = [m.get("text") for m in (_ok(r, "drain_log").get("messages") or [])]
            owned = set(n for ns in DEFS_BY_TYPE.values() for n in ns)
            r2 = t.bridge_call("jawa/drain_log", contains="cross-reference", errorsOnly=True, limit=100)
            xref = [m.get("text") for m in ((r2 or {}).get("messages") or [])
                    if any(d in (m.get("text") or "") for d in owned)]
            r3 = t.bridge_call("jawa/drain_log", contains="RimMandrake.BlueDesert", errorsOnly=True, limit=20)
            cfg = [m.get("text") for m in ((r3 or {}).get("messages") or [])]
            # LOAD_ERRORS_FAUNA_FLORA_1 (044381748) fixed Config errors on this mod's creatures and plants
            # (tool linkedBodyPartsGroup the BodyDef lacks; Nutrition 0 on an edible plant): a Config error
            # naming one of our defs is the regression guard for that whole class.
            r4 = t.bridge_call("jawa/drain_log", contains="Config error", errorsOnly=True, limit=200)
            conf = [m.get("text") for m in ((r4 or {}).get("messages") or [])
                    if any(d in (m.get("text") or "") for d in owned)]
            _note(t, "log scan", {"bluedesert errors": len(bad), "xref naming our defs": len(xref),
                                  "RimMandrake.BlueDesert errors": len(cfg), "config errors naming our defs": len(conf),
                                  "bufferLines": buf.get("totalInBuffer")})
            if bad or xref or cfg or conf:
                _fail("log carries errors: %s" % [str(x)[:160] for x in (bad + xref + cfg + conf)[:4]])


# ---------------------------------------------------------------------------------------------- static

def static_checks():
    """Offline checks, no game: shipped defs parse, the DEFAULTS table matches the C# (>=1 field found, or the
    probe is blind), every field is Scribed, and the walk exists with a coverage arrow on every line.
    The deeper offline proof is selftest_bluedesert.py (a scripted fake game per broken behaviour)."""
    bad = []
    src = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_BlueDesertMod.cs"), encoding="utf-8").read())
    found = {m.group(2): (m.group(1), m.group(3).strip())
             for m in re.finditer(r"public\s+static\s+(bool|float|int)\s+(\w+)\s*=\s*([^;]+);", src)
             if m.group(2) != "settings"}
    if not found:
        return ["settings regex found 0 static fields in RM_BlueDesertMod.cs: the probe is blind"]
    for f, (kind, raw) in found.items():
        if f not in DEFAULTS:
            bad.append("C# settings field %s is not in DEFAULTS" % f)
            continue
        want = (raw == "true") if kind == "bool" else float(raw.rstrip("f"))
        if want != DEFAULTS[f]:
            bad.append("default drift on %s: C# %s vs script %r" % (f, raw, DEFAULTS[f]))
        if '"%s"' % f not in src:
            bad.append("settings field %s is not Scribed" % f)
    for f in DEFAULTS:
        if f not in found:
            bad.append("DEFAULTS field %s is gone from the C#" % f)
    if not SHIPPED or not NATIVES or not FLORA:
        bad.append("def parser found nothing (defs %d natives %d flora %d): the probe is blind"
                   % (len(SHIPPED), len(NATIVES), len(FLORA)))
    csproj = open(os.path.join(HERE, "Source", "RM_BlueDesert.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Include="%s"' % fn not in csproj:
            bad.append("%s is not a <Compile Include> in the csproj" % fn)
    sc = open(os.path.join(HERE, "Source", "RM_BlueDesertSoundscape.cs"), encoding="utf-8").read()
    for need in ("public static string ProofChoir(string mode)", "public static string ProofVirr(string mode)",
                 "RM_BlueDesertSettings.ossivelChoirEnabled", "RM_BlueDesertSettings.virrSongEnabled",
                 '"RitualSustainer_Christian"', '"Ambient_Wind_Desolate"', "info.pitchFactor = VirrPitch"):
        if need not in sc:
            bad.append("soundscape: %s missing from RM_BlueDesertSoundscape.cs" % need)
    weathers = _xml_text("WeatherDefs/RM_BlueDesertWeathers.xml")
    if "<eruptSound>FleshbeastDigging_End</eruptSound>" not in weathers:
        bad.append("murrek eruption sound (eruptSound FleshbeastDigging_End) is not wired on RM_IceSandDrift")
    walk = os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "BlueDesert.md")
    if not os.path.exists(walk):
        bad.append("walk design/validation_walks/RimMandrake/BlueDesert.md is missing")
    else:
        w = open(walk, encoding="utf-8").read().split("## must be true", 1)[-1].split("\n## ", 1)[0]
        for ln in w.splitlines():
            if ln.startswith("- ") and "→" not in ln:
                bad.append("walk line has no coverage arrow: %s" % ln[:70])
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
