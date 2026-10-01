"""validation.py -- modcheck suite for RimMandrake: The Contagion (mandrake.rm.contagion).

Item CONTAGION_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/Contagion.md (`## must be
true` lines, each ending in `-> chain.component` or `-> UNCOVERED: why`). Process:
design/RimMandrake/debug_process.md (a first script = a modcheck Suite + a walk).

PACKAGING. This dev folder is the SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json, wave 0). Drive the `baroque_wave0` tier (northstar_plan.py), never the dev
folder's own packageId.

THE SITE. The Burn, the Bloom clock and the Coalescence only act on a map whose BIOME carries
RM_ContagionSkyExtension. `Map.Biome` is a live passthrough to the tile (decompiled Verse/Map.cs:398,
and jawa/map_info says so), so the chain `site.retile_to_contagion` re-tiles the quicktest map's OWN
tile to RM_Contagion with jawa/world_tile_set + world_commit instead of generating a Contagion map.
Chains that need it begin with `_need_contagion`, which records UNMEASURED (never PASS/FAIL) when the
retile did not land. `site.restore_tile` puts the original biome back. The off-biome chains
(repulsor_clear, spawner) run BEFORE the retile, on the stock quicktest biome, on purpose: the
Repulsor's off-Contagion half is a different code path, and the Unfinished spawner jumps the clock.

TIME. Two chains use jawa/time_set_ticks, which only overwrites the tick counter (nothing is
simulated): the spawner (nextSpawnTick is days away) and the natural Burn schedule. Both rely on the
mod's own comparisons (`TicksGame >= next...`), which is exactly the behaviour under test. The clock
is only ever moved FORWARD, and every chain that jumps ends with the site it needs cleared.

EVERY CHECK CAN FAIL. Each PASS predicate has an arm that goes the other way inside the same chain
(a toggle-off arm that must see nothing, a roofed/armored control that must stay clean, a
zero-damage arm, a frequency arm that must NOT schedule), so a harness that sees nothing records
UNMEASURED or FAIL, never PASS. `selftest_contagion.py` runs the suite against a scripted fake game,
healthy and with each mod behaviour broken in turn, and proves exactly the right component goes red.

NOT DRIVEN HERE (walk lines say UNCOVERED, with the reason): the tells (a Wait job is
indistinguishable from idling; needs a sky-state tool), natural Coalescence formation (statistical,
MTB over ~0.5 day after a 90000-tick Bloom), the install surgeries and grown-limb effects, the
float-menu inject option, biome worldgen placement, the standing Bloom's look, art.

Settings fields are `public static` (RimMandrake.Contagion.RM_ContagionSettings). Every arm that
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

suite = Suite("Contagion")

SETTINGS = "RimMandrake.Contagion.RM_ContagionSettings"
HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = "RM_Contagion"

# Shipped defaults, read off RM_ContagionMod.cs (public static field initialisers).
DEFAULTS = {
    "biomeRarityFactor": 1.0, "genomeOrganGrowingEnabled": True, "unfinishedSpawnerEnabled": True,
    "burnEnabled": True, "burnTellsEnabled": True, "burnFrequency": 1.0, "burnDamageFactor": 1.0,
    "cloudRepulsorEnabled": True, "sunbeamNativeFactor": 6.0, "coalescenceEnabled": True,
    "grownLimbsEnabled": True,
}
# a value different from the default, for the write+read-back round trip
ALT = {"biomeRarityFactor": 0.5, "burnFrequency": 2.0, "burnDamageFactor": 0.5, "sunbeamNativeFactor": 3.0}
suite.toggles = sorted(DEFAULTS)

PADS = {"repulsor": (-45, -45), "spawner": (45, -45), "burn": (0, -45), "uv": (-45, 0),
        "coal": (45, 0), "genome": (0, 45)}
PAD_SIZE = 30
SOIL = "Soil"
REPULSOR, COALESCENCE, SAMPLE = "RM_CloudRepulsor", "RM_Coalescence", "RM_GenomeSample"
HOST, UNFINISHED = "RM_BloodyMess", "RM_TheUnfinished"
BURN_COND, CLEAR_COND = "RM_ContagionBurnCondition", "RM_RepulsorClearSky"
BURN_WEATHER = "RM_ContagionBurn"
UV_NATIVE, ARMORED = "RM_Gnashling", "RM_Scaldhide"      # UV-shy / armored (RM_ContagionSkyExtension)
UV_BIG = "RM_BloodyMess"                                 # a roster native with real hit points
LIMB_POOL = ("RM_UnfinishedClaw", "RM_UnfinishedSpike", "RM_UnfinishedFang", "RM_UnfinishedStump",
             "RM_UnfinishedVestigialWing", "RM_UnfinishedUselessJaw")
LIMB_ITEMS = ("RM_PillarArmItem", "RM_LashItem", "RM_EyeburstItem", "RM_CaudalSpringItem",
              "RM_BellowsItem")
ORGANS = ("Kidney", "Liver", "Lung", "Heart", "RM_GrownLeg", "RM_GrownArm")
STAGE_MASS = (0, 6, 15)                      # RM_Coalescence's RM_CoalescenceExtension.stageMass
SAMPLES_BASE, SAMPLES_PER_STAGE, MASS_PER_SAMPLE, SAMPLES_MAX = 2, 2, 4, 14
JUMP_WIDE, JUMP_FAST, JUMP_OFF = 95000, 70000, 285000          # see chain burn_natural

_STATE = {}    # readings shared between components of ONE run


# --------------------------------------------------------------------------- shipped defs

def _read_defs():
    """{defType: [defName]} for every concrete def in this mod's Defs/, parsed per top-level
    element (never a fixed line number). Comments are stripped first."""
    wanted = ("ThingDef", "PawnKindDef", "WeatherDef", "GameConditionDef", "HediffDef", "JobDef",
              "RecipeDef", "BiomeDef", "AbilityDef", "ThoughtDef", "DamageDef")
    by_type = {}
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<(%s)\b([^>]*)>(.*?)</\1>" % "|".join(wanted), txt, re.S):
            kind, attrs, body = m.group(1), m.group(2), m.group(3)
            if re.search(r'Abstract\s*=\s*"[Tt]rue"', attrs):
                continue
            nm = re.search(r"<defName>([^<]+)</defName>", body)
            if nm and nm.group(1).strip() not in by_type.setdefault(kind, []):
                by_type[kind].append(nm.group(1).strip())
    return by_type


def _roster(kind):
    """Child element NAMES of the biome's <wildAnimals>/<wildPlants> (shorthand form, never <li>)."""
    p = os.path.join(HERE, "Defs", "BiomeDefs", "RM_Contagion.xml")
    with open(p, encoding="utf-8") as fh:
        txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
    m = re.search(r"<%s>(.*?)</%s>" % (kind, kind), txt, re.S)
    return re.findall(r"<([A-Za-z_][A-Za-z0-9_]*)>[0-9.]+</", m.group(1)) if m else []


DEFS_BY_TYPE = _read_defs()
SHIPPED = sorted("%s/%s" % (k, n) for k, ns in DEFS_BY_TYPE.items() for n in ns)
WILD_ANIMALS = _roster("wildAnimals")
WILD_PLANTS = _roster("wildPlants")


# --------------------------------------------------------------------------- helpers

def _live(t):
    """True only for a real run against a real session and an unfailed chain."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component and record it UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, poison=False, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail names
    the real reason, and the chain is not poisoned for an independent next component. `poison=True`
    (a site-setup component) keeps the chain failed so later components record UNMEASURED."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
        t.upstream_failed = bool(poison)
    t._why = None
    if t.session is not None:
        c = t.components[-1]
        print("[contagion] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    t._record(label, data)
    if t.session is not None:
        print("[contagion-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
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


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _rect(t, size=PAD_SIZE, dx=0, dz=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half + dz, size, size


def _prep(t, name, size=PAD_SIZE):
    """Clear the pad and lay plain soil so everything stands on walkable ground."""
    _pad(t, name)
    t.clear_area(size=size + 8)
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(_rect(t, size + 8))), layer="top")


def _things(t, defName, rect=None, limit=300):
    if rect:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=limit, rect=rect)
    else:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=limit)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defName)
    if "countMatched" not in r or not r.get("scanned"):
        _fail("list_things(%s) unreadable (no countMatched / scanned 0): %r" % (defName, r))
    if r.get("isCompleteList") is False:
        _fail("list_things(%s) truncated: %r" % (defName, r.get("countMatched")))
    return list(r.get("things") or [])


def _spawn(t, kind, x, z, faction="none"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s, %s) returned no pawn: %r" % (kind, faction, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _rows(t, rect=None):
    """{id: row} of every pawn, with health. A failed read is never 'no pawns'."""
    if rect:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True, rect=rect)
    else:
        r = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True)
    if not _live(t):
        return {}
    return dict((p.get("id"), p) for p in (_ok(r, "list_pawns").get("pawns") or []))


def _hdefs(row):
    """The set of hediff DEFNAMES on a row. Exact names, never a substring ('Burn' is inside
    'RM_BurnDose'). row['health']['hediffs'] is the nested shape the tool documents."""
    out = set()
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict):
            v = h.get("def") or h.get("defName") or h.get("hediff")
            if v:
                out.add(str(v))
        elif isinstance(h, str):
            out.add(h)
    return out


def _alive(row):
    return row is not None and not row.get("dead")


def _inspect(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return None, ""
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows or rows[0].get("error"):
        _fail("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return rows[0].get("label"), "\n".join(str(x) for x in (rows[0].get("inspect") or []))


def _as_bool(v):
    return str(v).strip().lower() == "true"


def _same(got, want):
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
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
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
        t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                       value=str(DEFAULTS[field]))
        got = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not _same((got or {}).get("value"), DEFAULTS[field]):
            print("[contagion] RESTORE FAILED %s -> %r" % (field, got), file=sys.stderr, flush=True)
    except Exception as ex:
        print("[contagion] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)


@contextlib.contextmanager
def _setting(t, field, value):
    """Flip one field for a block; ALWAYS restore the shipped default."""
    _set(t, field, value)
    try:
        yield
    finally:
        _restore(t, field)


def _names(rows):
    out = []
    for r in rows or []:
        if isinstance(r, dict):
            out.append(str(r.get("def") or r.get("defName") or r.get("condition") or ""))
        else:
            out.append(str(r))
    return out


def _conds(t):
    """(names, rows) of the ACTIVE MAP game conditions, from jawa/site_state. A shape that cannot be
    read is UNMEASURED, never 'no conditions'."""
    r = t.bridge_call("jawa/site_state")
    if not _live(t):
        return [], []
    _ok(r, "site_state")
    c = (r or {}).get("conditions")
    rows = c.get("map") if isinstance(c, dict) else None
    if not isinstance(rows, list):
        _unmeasured(t, "site_state.conditions.map unreadable: %r" % (c,))
    return _names(rows), rows


def _has_cond(t, name):
    return name in _conds(t)[0]


def _weather_now(t):
    r = t.bridge_call("jawa/weather_get")
    if not _live(t):
        return None
    cur = (r or {}).get("weather")
    if isinstance(cur, dict):
        cur = cur.get("current")
    return cur


def _wait(t, n):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact); long waits run Ultrafast and
    poll the real clock, then pause; raises on a stall."""
    if t.session is None or t.upstream_failed or n <= 4000:
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


def _jump(t, delta):
    """Move the clock FORWARD by `delta` ticks without simulating (jawa/time_set_ticks)."""
    now = t.session._ticks()
    if now is None:
        _unmeasured(t, "clock unreadable before a time jump")
    r = t.bridge_call("jawa/time_set_ticks", ticks=int(now + delta))
    _ok(r, "time_set_ticks")
    if (r or {}).get("ticksGameAfter") is not None and r["ticksGameAfter"] < now + delta - 5:
        _fail("time_set_ticks did not take: %r" % r)


def _map_biome(t):
    r = t.bridge_call("jawa/map_info")
    if not _live(t):
        return None, None
    _ok(r, "map_info")
    return r.get("mapBiome"), r


def _need_contagion(t):
    """First component of every Contagion-map chain: the retile must have landed."""
    with _comp(t, "site_is_contagion", poison=True):
        if _live(t):
            b, _ = _map_biome(t)
            if b != BIOME:
                _unmeasured(t, "current map biome is %r, not %s -- site.retile_to_contagion did not "
                               "land, so the Burn/Bloom/Coalescence cannot act here" % (b, BIOME))


def _power_on(t, thing_id):
    r = t.bridge_call("jawa/power_net", thing=thing_id, forcePowerOn=True)
    if not _live(t):
        return
    _ok(r, "power_net")
    if not r.get("powerOnAfter"):
        _unmeasured(t, "could not power the device (powerOnAfter=%r): %r" % (r.get("powerOnAfter"), r))


def _spawn_repulsor(t, x, z):
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (REPULSOR, x, z))
    rows = _things(t, REPULSOR, _rs((x - 3, z - 3, 8, 8)))
    if _live(t) and len(rows) != 1:
        _fail("fixture: wanted 1 %s at (%d,%d), found %d" % (REPULSOR, x, z, len(rows)))
    return rows[0]["id"] if rows else None


def _end_conditions(t):
    for name in (BURN_COND, CLEAR_COND):
        if t.session is not None:
            try:
                t.session.call("jawa/game_condition", action="end", condition=name)
            except Exception:
                pass          # 'not active' is a Fail from the tool; nothing to end


def _baseline(t):
    """Everything that could spoil a fixture: storyteller incidents, auto-home, queued incidents."""
    t.bridge_call("jawa/site_state", storyteller="off", autoHome="off", clearIncidentQueue=True)


def _stable(t, fn):
    """Run a chain body, then ALWAYS end the conditions it made, restore every setting it may have
    touched, and clear its pad."""
    try:
        fn()
    finally:
        if t.session is not None:
            _end_conditions(t)
            for f in DEFAULTS:
                _restore(t, f)
            try:
                t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)),
                               categories="All")
            except Exception as ex:
                print("[contagion] pad cleanup failed: %s" % ex, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- chain: defs

@suite.chain("defs")
def defs_chain(t):
    with _comp(t, "defs_resolve"):
        if _live(t):
            # The parser must see the mod: a broken regex would read "all 0 defs resolve".
            if len(SHIPPED) < 60 or not DEFS_BY_TYPE.get("WeatherDef") or not WILD_ANIMALS:
                _fail("parsed only %d shipped defs / %d wildAnimals from %s (parser broken?)"
                      % (len(SHIPPED), len(WILD_ANIMALS), HERE))
            r = t.bridge_call("jawa/get_defs", defs=";".join(SHIPPED), fields="defName", limit=500)
            _ok(r, "get_defs(all shipped)")
            if r.get("notFound"):
                _fail("%d shipped def(s) did not resolve live (silently discarded?): %s"
                      % (len(r["notFound"]), r["notFound"][:12]))
            if r.get("foundCount") != len(SHIPPED):
                _fail("get_defs foundCount %r != %d requested" % (r.get("foundCount"), len(SHIPPED)))
            probe = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Contagion_NoSuchDef_Probe",
                                  fields="defName")
            if "RM_Contagion_NoSuchDef_Probe" not in json.dumps((probe or {}).get("notFound")):
                _fail("sanity probe: an absent def was not reported in notFound: %r" % probe)
            _note(t, "shipped defs resolved", len(SHIPPED))

    with _comp(t, "biome_table_and_roster"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields=(
                "baseWeatherCommonalities,wildAnimals,wildPlants,animalDensity,modExtensions"),
                limit=5)
            _ok(r, "get_defs(biome)")
            row = ((r.get("defs") or [{}])[0].get("fields")) or {}
            table = row.get("baseWeatherCommonalities")
            if not isinstance(table, list) or not table:
                _unmeasured(t, "biome weather table unreadable: %r" % (table,))
            w = dict((x.get("weather"), x.get("commonality") or 0) for x in table)
            if not w.get("RM_ContagionBloom"):
                _fail("the standing Bloom has no commonality in the biome table: %r" % w)
            if w.get(BURN_WEATHER):
                _fail("the Burn weather has commonality %r: it must be reachable ONLY through the "
                      "Burn condition, never rolled by vanilla weather" % w.get(BURN_WEATHER))
            dens = row.get("animalDensity")
            if not isinstance(dens, (int, float)) or dens <= 0:
                _fail("animalDensity %r: <= 0 means the animal roster can never spawn" % (dens,))
            blob = json.dumps(row)
            if "RM_ContagionSkyExtension" not in blob:
                _fail("the biome does not carry RM_ContagionSkyExtension (the gate for the Burn, "
                      "the Bloom clock and the Coalescence): %s" % blob[:300])
            missing = [a for a in WILD_ANIMALS if a not in json.dumps(row.get("wildAnimals"))]
            if missing:
                _fail("wildAnimals lacks %d rostered kind(s): %s" % (len(missing), missing[:8]))
            if "RM_Rattlegrope" not in json.dumps(row.get("wildPlants")):
                _fail("wildPlants lacks RM_Rattlegrope (the Burn's plant tell)")
            _note(t, "biome roster", {"animals": len(WILD_ANIMALS), "plants": len(WILD_PLANTS)})

    with _comp(t, "organ_patch_comps"):
        if _live(t):
            for organ in ("Kidney", "Liver", "Lung", "Heart"):
                r = t.bridge_call("jawa/get_def", defName=organ, defType="ThingDef")
                _ok(r, "get_def(%s)" % organ)
                comps = r.get("comps")
                if not isinstance(comps, list) or not comps:
                    _unmeasured(t, "get_def(%s) returned no readable comps list: %r" % (organ, comps))
                names = [c if isinstance(c, str) else (c.get("class") or c.get("compClass") or "")
                         for c in comps]
                if not any(str(n).endswith("CompProperties_GenomeMatched") for n in names):
                    _fail("%s carries no CompProperties_GenomeMatched -- OrganGenomeComps.xml "
                          "matched nothing (and logs nothing): %r" % (organ, names))


# --------------------------------------------------------------------------- chain: settings

@suite.chain("settings")
def settings_chain(t):
    with _comp(t, "defaults"):
        if _live(t):
            wrong = {}
            for field, want in sorted(DEFAULTS.items()):
                v = _get_setting(t, field)
                if not _same(v, want):
                    wrong[field] = v
            if wrong:
                _fail("settings not at shipped defaults (or missing): %s" % wrong)
            bogus = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                                  field="noSuchField_probe")
            if (bogus or {}).get("success") is not False:
                _fail("sanity probe: a nonexistent field did not fail loudly: %r" % bogus)


def _roundtrip(field):
    def body(t):
        with _comp(t, "%s_roundtrip" % field, toggle=field):
            if _live(t):
                want = ALT.get(field, not DEFAULTS[field])
                try:
                    _set(t, field, want)
                finally:
                    _restore(t, field)
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s did not restore to its shipped default" % field)
    return body


for _f in sorted(DEFAULTS):
    suite.chain("settings_%s" % _f)(_roundtrip(_f))


# --------------------------------------------------------------------------- chain: repulsor_clear

@suite.chain("repulsor_clear")
def repulsor_clear(t):
    """Off the Contagion, on the stock quicktest biome: the Repulsor's other code path."""
    def body():
        with _comp(t, "site_ready_baseline", poison=True):
            _pad(t, "repulsor")
            if _live(t):
                b, _ = _map_biome(t)
                if b == BIOME:
                    _unmeasured(t, "the map is already %s: the off-Contagion arm needs a stock biome" % BIOME)
                _baseline(t)
                _prep(t, "repulsor")
                x, z = t.anchor
                _STATE["rep_id"] = _spawn_repulsor(t, x, z)
                _power_on(t, _STATE["rep_id"])
                _STATE["rep_biome"] = b

        with _comp(t, "off_when_setting_off", toggle="cloudRepulsorEnabled"):
            if _live(t):
                with _setting(t, "cloudRepulsorEnabled", False):
                    _wait(t, 3300)
                    if _has_cond(t, CLEAR_COND):
                        _fail("the repulsor held the sky with cloudRepulsorEnabled off")
                    _, lines = _inspect(t, _STATE["rep_id"])
                    if "Disabled in Mod Settings" not in lines:
                        _fail("inspect string does not say it is disabled: %r" % lines)

        with _comp(t, "holds_sky_clear", toggle="cloudRepulsorEnabled"):
            if _live(t):
                t.bridge_call("jawa/weather_set", weather="Rain")
                _power_on(t, _STATE["rep_id"])
                _wait(t, 3300)               # 2500 warm-up + one 250-tick re-assert, with margin
                if not _has_cond(t, CLEAR_COND):
                    _fail("a warm, powered repulsor registered no %s condition" % CLEAR_COND)
                if _has_cond(t, BURN_COND):
                    _fail("the repulsor forced a Burn on a non-Contagion map")
                _, lines = _inspect(t, _STATE["rep_id"])
                if "Holding the sky clear" not in lines:
                    _fail("inspect string does not say it holds the sky clear: %r" % lines)
                _note(t, "weather after the condition registered (vanilla's forcing, not ours)",
                      _weather_now(t))

        with _comp(t, "lapses_without_power"):
            if _live(t):
                r = t.bridge_call("jawa/power_net", thing=_STATE["rep_id"], forcePowerOn=False)
                _ok(r, "power_net(off)")
                if r.get("powerOnAfter"):
                    _unmeasured(t, "could not switch the device off: %r" % r)
                _wait(t, 1200)               # holdTicks 750 + the 250 poll
                if _has_cond(t, CLEAR_COND):
                    _fail("the clear-sky condition outlived the device's power by > 1200 ticks "
                          "(it must lapse within holdTicks=750)")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: spawner

@suite.chain("spawner")
def spawner(t):
    def body():
        with _comp(t, "site_ready_spawner", poison=True):
            _pad(t, "spawner")
            if _live(t):
                _baseline(t)
                _prep(t, "spawner")
                x, z = t.anchor
                _STATE["host"] = _spawn(t, HOST, x, z)
                _STATE["host_rect"] = _rs(_rect(t, 24))

        with _comp(t, "spawner_off_buds_nothing", toggle="unfinishedSpawnerEnabled"):
            if _live(t):
                with _setting(t, "unfinishedSpawnerEnabled", False):
                    _jump(t, 90000)           # past nextSpawnTick (0.6-1.4 days) either way
                    _wait(t, 200)
                    n = len(_things_pawns(t, UNFINISHED, _STATE["host_rect"]))
                    if n:
                        _fail("%d Unfinished budded with unfinishedSpawnerEnabled off" % n)

        with _comp(t, "spawner_buds_unfinished", toggle="unfinishedSpawnerEnabled"):
            if _live(t):
                _wait(t, 250)                 # toggle is back on; the overdue timer fires at once
                kids = _things_pawns(t, UNFINISHED, _STATE["host_rect"])
                if not 1 <= len(kids) <= 3:
                    _fail("expected 1..3 (maxNearby) Unfinished budded by the host, found %d" % len(kids))
                _STATE["kid"] = kids[0]["id"]

        with _comp(t, "unfinished_rolls_limbs_and_lifespan"):
            if _live(t):
                row = _rows(t, _STATE["host_rect"]).get(_STATE.get("kid"))
                if row is None:
                    _unmeasured(t, "the budded Unfinished is not readable")
                hd = _hdefs(row)
                limbs = hd & set(LIMB_POOL)
                if not 1 <= len(limbs) <= 3:
                    _fail("expected 1-3 rolled limb hediffs from the pool, found %s (all: %s)"
                          % (sorted(limbs), sorted(hd)))
                if "RM_UnfinishedUnraveling" not in hd:
                    _fail("no RM_UnfinishedUnraveling lifespan hediff: %s" % sorted(hd))

        with _comp(t, "unfinished_dissolves_on_death"):
            if _live(t):
                kid = _STATE.get("kid")
                r = t.bridge_call("jawa/pawn_severity_adjust", pawn=kid,
                                  hediff="RM_UnfinishedUnraveling", offset=1.0)
                _ok(r, "pawn_severity_adjust")
                _wait(t, 120)
                row = _rows(t, _STATE["host_rect"]).get(kid)
                if _alive(row):
                    _fail("the Unfinished survived being pushed to lethal severity: %r" % (r,))
                corpses = _things(t, "Corpse_" + UNFINISHED, _STATE["host_rect"])
                if corpses:
                    _fail("a corpse persists (%d): death must dissolve it" % len(corpses))
    _stable(t, body)


def _things_pawns(t, kind, rect):
    """Spawned, living pawns of `kind` in rect (list_pawns rows carry `kind`)."""
    rows = _rows(t, rect)
    return [p for p in rows.values() if p.get("kind") == kind and not p.get("dead")]


# --------------------------------------------------------------------------- chain: site

@suite.chain("site")
def site(t):
    with _comp(t, "retile_to_contagion", poison=True):
        if _live(t):
            b, info = _map_biome(t)
            tile = info.get("tile")
            if tile is None or info.get("tileValid") is False:
                _unmeasured(t, "map_info reports no usable world tile: %r" % (info,))
            _STATE["tile"], _STATE["orig_biome"] = tile, b
            if b == BIOME:
                _unmeasured(t, "the map was already %s; the control for 'the retile did it' is gone" % BIOME)
            r = t.bridge_call("jawa/world_tile_set", tiles=str(tile), biome=BIOME, readBack=1)
            _ok(r, "world_tile_set")
            _ok(t.bridge_call("jawa/world_commit", redraw=False, recalcPaths=False), "world_commit")
            b2, _ = _map_biome(t)
            if b2 != BIOME:
                _fail("after world_tile_set(%s) the map's own biome reads %r" % (BIOME, b2))
            _note(t, "retiled", {"tile": tile, "from": b, "to": b2})


# --------------------------------------------------------------------------- chain: burn_forced

def _open_pawns(t, x, z):
    """The Burn fixture: an open visitor, a roofed visitor, a UV-shy native, an armored native, and a
    roof patch east of the native to dive for. Drafted colonists hold their ground."""
    t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,8,8" % (x + 6, z - 4))
    out = {}
    out["open"] = t.spawn_pawn("Colonist", hostile=False)
    out["roofed"] = t.spawn_pawn("Colonist", hostile=False)
    out["native"] = _spawn(t, UV_NATIVE, x, z + 4)
    out["armored"] = _spawn(t, ARMORED, x, z - 6)
    return out


@suite.chain("burn_forced")
def burn_forced(t):
    def body():
        _need_contagion(t)
        with _comp(t, "burn_site_ready", poison=True):
            _pad(t, "burn")
            if _live(t):
                _baseline(t)
                _prep(t, "burn")
                x, z = t.anchor
                if _has_cond(t, BURN_COND):
                    _unmeasured(t, "a Burn is already active: the control (no Burn before the "
                                   "repulsor) cannot be taken")
                _set(t, "burnDamageFactor", 0)      # arm A first: Burn weather, zero harm
                _STATE["burn"] = _open_pawns(t, x, z)
                for k in ("open", "roofed", "native", "armored"):
                    if not _STATE["burn"][k]:
                        _fail("fixture: no %s pawn" % k)
                # the roofed colonist stands under the patch; both colonists hold their ground
                rx, rz = x + 9, z
                t.bridge_call("jawa/order_pawn", pawnId=_STATE["burn"]["roofed"], x=rx, z=rz,
                              waitTicks=300)
                for k in ("open", "roofed"):
                    t.bridge_call("jawa/set_draft", pawnId=_STATE["burn"][k], drafted=True)
                _STATE["rep_id"] = _spawn_repulsor(t, x - 8, z + 8)
                _power_on(t, _STATE["rep_id"])

        with _comp(t, "repulsor_forces_burn", toggle="cloudRepulsorEnabled"):
            if _live(t):
                _wait(t, 3300)
                if not _has_cond(t, BURN_COND):
                    _fail("a warm, powered repulsor on a Contagion map did not force the Burn")
                _, lines = _inspect(t, _STATE["rep_id"])
                if "the Burn is forced" not in lines:
                    _fail("inspect string does not say the Burn is forced: %r" % lines)
                seen = None
                for _ in range(10):                  # the sky closes over: transition ~600 ticks
                    seen = _weather_now(t)
                    if seen == BURN_WEATHER:
                        break
                    _wait(t, 250)
                if seen != BURN_WEATHER:
                    _fail("the Burn condition is active but the weather is %r, not %s" % (seen, BURN_WEATHER))

        with _comp(t, "burn_harmless_at_zero_damage", toggle="burnDamageFactor"):
            if _live(t):
                _wait(t, 600)                        # at least two 250-tick pressure passes
                rows = _rows(t)
                b = _STATE["burn"]
                hit = [k for k in ("open", "native") if _hdefs(rows.get(b[k])) & {"RM_BurnDose", "Burn"}]
                if hit or not _alive(rows.get(b["native"])):
                    _fail("burnDamageFactor=0 still harmed: %s (native alive=%s)"
                          % (hit, _alive(rows.get(b["native"]))))

        with _comp(t, "burn_doses_the_exposed_visitor", toggle="burnDamageFactor"):
            if _live(t):
                _set(t, "burnDamageFactor", 1)
                _wait(t, 800)
                rows = _rows(t)
                b = _STATE["burn"]
                if "RM_BurnDose" not in _hdefs(rows.get(b["open"])):
                    _fail("an exposed visitor carries no RM_BurnDose after the Burn pressed on it "
                          "(hediffs: %s)" % sorted(_hdefs(rows.get(b["open"]))))
                if "RM_BurnDose" in _hdefs(rows.get(b["roofed"])):
                    _fail("a ROOFED visitor was dosed: shelter must protect")
                _STATE["rows_after"] = rows

        with _comp(t, "burn_hurts_native_spares_armored"):
            if _live(t):
                rows, b = _STATE.get("rows_after"), _STATE["burn"]
                if rows is None:
                    _unmeasured(t, "burn_doses_the_exposed_visitor did not run")
                nat, arm = rows.get(b["native"]), rows.get(b["armored"])
                if not (not _alive(nat) or "Burn" in _hdefs(nat)):
                    _fail("the UV-shy native took no Burn damage under open sky (hediffs: %s)"
                          % sorted(_hdefs(nat)))
                if "Burn" in _hdefs(arm):
                    _fail("the ARMORED native took Burn damage: %s" % sorted(_hdefs(arm)))

        with _comp(t, "native_dives_for_roof"):
            if _live(t):
                rows, b = _STATE.get("rows_after"), _STATE["burn"]
                if rows is None:
                    _unmeasured(t, "burn_doses_the_exposed_visitor did not run")
                nat = rows.get(b["native"])
                if nat is None or not _alive(nat):
                    _unmeasured(t, "the native died before its dive could be read")
                x, z = t.anchor
                inside = x + 6 <= nat.get("x", -1) < x + 14 and z - 4 <= nat.get("z", -1) < z + 4
                if not inside:
                    _fail("the UV-shy native is at (%s,%s), not under the roof patch %s"
                          % (nat.get("x"), nat.get("z"), (x + 6, z - 4, 8, 8)))

        with _comp(t, "burn_off_means_no_harm", toggle="burnEnabled"):
            if _live(t):
                x, z = t.anchor
                fresh = t.spawn_pawn("Colonist", hostile=False)
                t.bridge_call("jawa/set_draft", pawnId=fresh, drafted=True)
                t.bridge_call("jawa/order_pawn", pawnId=fresh, x=x - 12, z=z - 10, waitTicks=200)
                with _setting(t, "burnEnabled", False):
                    _wait(t, 800)
                    if not _has_cond(t, BURN_COND):
                        _fail("the forced Burn vanished when burnEnabled went off: the device must "
                              "still hold the storm open")
                    if "RM_BurnDose" in _hdefs(_rows(t).get(fresh)):
                        _fail("a fresh exposed visitor was dosed with burnEnabled off")

        with _comp(t, "repulsor_off_lapses_burn", toggle="cloudRepulsorEnabled"):
            if _live(t):
                with _setting(t, "cloudRepulsorEnabled", False):
                    _wait(t, 1200)
                    if _has_cond(t, BURN_COND):
                        _fail("the forced Burn outlived cloudRepulsorEnabled=false by > 1200 ticks")
                    _, lines = _inspect(t, _STATE["rep_id"])
                    if "Disabled in Mod Settings" not in lines:
                        _fail("inspect string does not say it is disabled: %r" % lines)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: burn_natural

@suite.chain("burn_natural")
def burn_natural(t):
    """The natural schedule (meanDaysBetweenBurns 3, each gap x[0.5,1.5], divided by burnFrequency)
    cannot be waited for. The mod compares TicksGame to nextBurnTick, so the clock is jumped:
      frequency 0.1  -> gap >= 900000 ticks: a +95000 and then a +285000 jump must NOT bring a Burn
                        (frequency 1 would have fired by 270000, so an ignored setting is caught);
      frequency 4    -> gap <= 67500 ticks:  a +70000 jump MUST bring one;
      burnEnabled off -> the schedule is cleared: a +285000 jump (past the longest gap at frequency 1)
                        must NOT bring one."""
    def body():
        _need_contagion(t)
        with _comp(t, "natural_site_ready", poison=True):
            _pad(t, "burn")
            if _live(t):
                _baseline(t)
                _end_conditions(t)
                _prep(t, "burn")
                _set(t, "burnEnabled", False)
                _wait(t, 600)               # a pass with burnEnabled off clears nextBurnTick
                if _has_cond(t, BURN_COND):
                    _unmeasured(t, "a Burn is still active after ending it")

        with _comp(t, "burn_off_never_schedules", toggle="burnEnabled"):
            if _live(t):
                # 285000 is past the LONGEST possible gap (frequency 1: 270000), so a schedule that
                # ignored burnEnabled, whenever it was rolled, would have fired by now.
                _jump(t, JUMP_OFF)
                _wait(t, 600)
                if _has_cond(t, BURN_COND):
                    _fail("a Burn arrived with burnEnabled off")

        with _comp(t, "slow_frequency_defers_burn", toggle="burnFrequency"):
            if _live(t):
                _set(t, "burnFrequency", 0.1)
                _set(t, "burnEnabled", True)
                _wait(t, 600)               # first pass rolls the gap at frequency 0.1
                _jump(t, JUMP_WIDE)
                _wait(t, 600)
                if _has_cond(t, BURN_COND):
                    _fail("a Burn arrived inside 95000 ticks at burnFrequency=0.1 (min gap 900000)")
                _jump(t, JUMP_OFF - JUMP_WIDE)   # 285000 in all: past the LONGEST gap at frequency 1 (270000)
                _wait(t, 600)
                if _has_cond(t, BURN_COND):
                    _fail("a Burn arrived inside 285000 ticks at burnFrequency=0.1: the setting is "
                          "ignored (frequency 1 would already have fired)")
                _set(t, "burnEnabled", False)
                _wait(t, 600)               # clears the slow roll

        with _comp(t, "natural_burn_arrives_on_schedule", toggle="burnFrequency"):
            if _live(t):
                _set(t, "burnFrequency", 4)
                _set(t, "burnEnabled", True)
                _wait(t, 600)               # rolls a gap of 22500..67500 ticks
                _jump(t, JUMP_FAST)
                _wait(t, 600)
                names, rows = _conds(t)
                if BURN_COND not in names:
                    _fail("no Burn after a +%d tick jump at burnFrequency=4 (gap <= 67500)" % JUMP_FAST)
                _note(t, "natural burn condition row", [r for r in rows if BURN_COND in json.dumps(r)])
    _stable(t, body)


# --------------------------------------------------------------------------- chain: uv

@suite.chain("uv")
def uv(t):
    def body():
        _need_contagion(t)
        with _comp(t, "uv_site_ready", poison=True):
            _pad(t, "uv")
            if _live(t):
                _baseline(t)
                _prep(t, "uv")
                _set(t, "burnEnabled", False)
                x, z = t.anchor
                _STATE["uv"] = {"native6": _spawn(t, UV_BIG, x - 6, z), "native1": _spawn(t, UV_BIG, x, z),
                                "person": t.spawn_pawn("Colonist", hostile=False)}
                for k, v in _STATE["uv"].items():
                    if not v:
                        _fail("fixture: no %s" % k)

        with _comp(t, "uv_native_multiplier", toggle="sunbeamNativeFactor"):
            if _live(t):
                u = _STATE["uv"]

                def hit(pid, factor):
                    with _setting(t, "sunbeamNativeFactor", factor):
                        _ok(t.bridge_call("jawa/damage", damageDef="RM_UVBeam", amount=5, thingId=pid,
                                          allowColonists=True), "damage(RM_UVBeam)")
                hit(u["native6"], 6)
                hit(u["native1"], 1)
                hit(u["person"], 6)
                rows = _rows(t)

                def sev(pid):
                    tot = 0.0
                    for h in (((rows.get(pid) or {}).get("health") or {}).get("hediffs") or []):
                        if isinstance(h, dict) and (h.get("def") or h.get("defName")) == "RM_UVSunburn":
                            tot += float(h.get("severity") or 0)
                    return tot
                s6, s1, sp = sev(u["native6"]), sev(u["native1"]), sev(u["person"])
                _note(t, "UV sunburn severity (native@6x, native@1x, person@6x)", [s6, s1, sp])
                if min(s6, s1, sp) <= 0:
                    _unmeasured(t, "no RM_UVSunburn severity read back (%r): cannot compare" % [s6, s1, sp])
                if not s6 >= 3 * s1:
                    _fail("a native hit at 6x took %.2f vs %.2f at 1x (want >= 3x)" % (s6, s1))
                if not s6 >= 3 * sp:
                    _fail("a native took %.2f vs a PERSON %.2f from the same beam at 6x (people must "
                          "not get the native multiplier)" % (s6, sp))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: coalescence

def _mass_stage(lines):
    m = re.search(r"Stage (\d+), absorbed mass (\d+)", lines)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


@suite.chain("coalescence")
def coalescence(t):
    def body():
        _need_contagion(t)
        with _comp(t, "coalescence_site_ready", poison=True):
            _pad(t, "coal")
            if _live(t):
                _baseline(t)
                _end_conditions(t)
                _prep(t, "coal")
                _set(t, "burnEnabled", False)       # the clock jumps below must not schedule a Burn
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (COALESCENCE, x, z))
                rows = _things(t, COALESCENCE, _rs(_rect(t, 24)))
                if len(rows) != 1:
                    _fail("fixture: wanted 1 %s, found %d" % (COALESCENCE, len(rows)))
                _STATE["coal"] = rows[0]["id"]
                _STATE["coal_xz"] = (x, z)
                _, lines = _inspect(t, _STATE["coal"])
                if _mass_stage(lines) != (1, 0):
                    _fail("a fresh Coalescence should read Stage 1, mass 0: %r" % lines)

        with _comp(t, "coalescence_off_absorbs_nothing", toggle="coalescenceEnabled"):
            if _live(t):
                x, z = _STATE["coal_xz"]
                with _setting(t, "coalescenceEnabled", False):
                    kid = _spawn(t, UNFINISHED, x + 3, z)
                    _wait(t, 400)
                    if not _alive(_rows(t).get(kid)):
                        _fail("the Coalescence absorbed an Unfinished with coalescenceEnabled off")
                    if _mass_stage(_inspect(t, _STATE["coal"])[1]) != (1, 0):
                        _fail("mass moved with coalescenceEnabled off")
                t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, 24)), categories="Item")

        with _comp(t, "coalescence_absorbs_and_grows_a_stage", toggle="coalescenceEnabled"):
            if _live(t):
                x, z = _STATE["coal_xz"]
                kids = [_spawn(t, UNFINISHED, x + 3, z + i - 3) for i in range(6)]
                _wait(t, 600)
                rows = _rows(t)
                left = [k for k in kids if _alive(rows.get(k))]
                stage, mass = _mass_stage(_inspect(t, _STATE["coal"])[1])
                _note(t, "after absorbing 6", {"left": len(left), "stage": stage, "mass": mass})
                if mass is None:
                    _unmeasured(t, "Coalescence inspect line unreadable")
                if mass < STAGE_MASS[1] or stage < 2:
                    _fail("absorbed 6 Unfinished but the Coalescence reads Stage %s, mass %s "
                          "(want Stage >= 2 at mass >= %d); %d of 6 still alive"
                          % (stage, mass, STAGE_MASS[1], len(left)))

        with _comp(t, "coalescence_emits_manhunters_and_grows_on_its_own"):
            if _live(t):
                _, before = _inspect(t, _STATE["coal"])
                _jump(t, 7000)              # passive growth is 1 mass / 6000 ticks; emit every 3000 (stage 2)
                _wait(t, 400)
                stage, mass = _mass_stage(_inspect(t, _STATE["coal"])[1])
                m0 = _mass_stage(before)[1]
                if mass is None or mass <= m0:
                    _fail("no passive growth over 7000 ticks (passiveGrowthTicks 6000) (mass %s -> %s)" % (m0, mass))
                x, z = _STATE["coal_xz"]
                mad = []
                for p in _things_pawns(t, UNFINISHED, _rs(_rect(t, 24))):
                    d = t.bridge_call("jawa/pawn_get", pawn=p["id"])
                    if "Manhunter" in json.dumps(d):
                        mad.append(p["id"])
                if not mad:
                    _fail("no manhunter Unfinished emitted after 7000 ticks")

        with _comp(t, "burn_collapses_it_into_monstrous_samples"):
            if _live(t):
                stage, mass = _mass_stage(_inspect(t, _STATE["coal"])[1])
                if mass is None:
                    _unmeasured(t, "mass unreadable before the Burn")
                want = min(SAMPLES_MAX, SAMPLES_BASE + SAMPLES_PER_STAGE * (stage - 1)
                           + mass // MASS_PER_SAMPLE)
                _ok(t.bridge_call("jawa/game_condition", action="start", condition=BURN_COND,
                                  durationTicks=2000), "game_condition(start Burn)")
                _wait(t, 400)
                if _things(t, COALESCENCE, _rs(_rect(t, 24))):
                    _fail("the Coalescence survived a Burn")
                got = _things(t, SAMPLE, _rs(_rect(t, 28)))
                if len(got) != want:
                    _fail("collapse at stage %d mass %d should spill %d samples, found %d"
                          % (stage, mass, want, len(got)))
                bad = []
                for s in got[:3]:
                    if "Monstrous" not in _inspect(t, s["id"])[1]:
                        bad.append(s["id"])
                if bad:
                    _fail("spilled samples are not Monstrous grade: %s" % bad)
                _STATE["monstrous"] = [s["id"] for s in got]
        _monstrous_components(t)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: genome

def _give(t, pawn, sample_id):
    r = t.bridge_call("jawa/inventory_transfer", pawn=pawn, mode="add", thing=sample_id)
    if _live(t) and not (_ok(r, "inventory_transfer").get("movedCount") or 0) >= 1:
        _fail("could not put the sample in the colonist's pack: %r" % r)


def _inject(t, doer, host):
    r = t.bridge_call("jawa/ordered_job", pawnId=doer, jobDef="RM_InjectGenomeSample",
                      targetAId=host, waitTicks=600, timeoutSeconds=60)
    if _live(t):
        if not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
            _fail("RM_InjectGenomeSample was not accepted and running: %r" % r)
        t.wait_ticks(600)


def _batch_snapshot(t, rect):
    """{thingId: def} of every organ / grown-limb item in rect (so a batch is counted as the NEW ones;
    never destroy_batch Items, which would also eat a sample still waiting to be injected)."""
    out = {}
    for d in ORGANS + LIMB_ITEMS:
        for th in _things(t, d, rect):
            out[th["id"]] = d
    return out


def _finish_gestation(t, host, rect):
    """Push the host's gestation to completion; returns the NEW organ/limb items it produced."""
    before = _batch_snapshot(t, rect)
    _ok(t.bridge_call("jawa/pawn_severity_adjust", pawn=host, hediff="RM_AmoebaGestation",
                      offset=0.999), "pawn_severity_adjust(gestation)")
    _wait(t, 150)
    after = _batch_snapshot(t, rect)
    return [d for i, d in after.items() if i not in before]


@suite.chain("genome")
def genome(t):
    def body():
        _need_contagion(t)
        with _comp(t, "genome_site_ready", poison=True):
            _pad(t, "genome")
            if _live(t):
                _baseline(t)
                _end_conditions(t)
                _prep(t, "genome")
                _set(t, "burnEnabled", False)
                x, z = t.anchor
                _STATE["g"] = {"doer": t.spawn_pawn("Colonist", hostile=False),
                               "patient": t.spawn_pawn("Colonist", hostile=False),
                               "rect": _rs(_rect(t, 24))}
                if not (_STATE["g"]["doer"] and _STATE["g"]["patient"]):
                    _fail("fixture: colonists not spawned")

        with _comp(t, "extraction_surgery_yields_sample", toggle="genomeOrganGrowingEnabled"):
            if _live(t):
                g = _STATE["g"]
                t.bridge_call("jawa/set_pawn_skill", pawn=g["doer"], skill="Medicine", level=20)
                made = None
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="Bed:%d,%d" % (x - 4, z + 4), stuff="WoodLog")
                for attempt in range(3):     # surgery can fail on skill; three completed tries
                    t.bridge_call("jawa/bill_add", giverId=g["patient"], recipe="RM_ExtractGenomeSample",
                                  repeatMode="repeatcount", repeatCount=1)
                    r = t.bridge_call("jawa/do_bill_now", billGiverId=g["patient"], pawnId=g["doer"],
                                      workGiverDef="DoBillsMedicalHumanOperation", waitTicks=2500, timeoutSeconds=90)
                    if (r or {}).get("jobOnThingReturnedNull"):
                        _unmeasured(t, "the surgery job could not start: %r" % r)
                    _wait(t, 1500)
                    got = _things(t, SAMPLE, g["rect"])
                    if got:
                        made = got[0]
                        break
                if not made:
                    _fail("three completed extraction surgeries produced no genome sample")
                _, lines = _inspect(t, made["id"])
                if "Genome source:" not in lines:
                    _fail("the sample does not record its source colonist: %r" % lines)
                _STATE["g"]["sample"] = made["id"]

        with _comp(t, "inject_starts_gestation"):
            if _live(t):
                g = _STATE["g"]
                x, z = t.anchor
                if not g.get("sample"):
                    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SAMPLE, x + 2, z))
                    got = _things(t, SAMPLE, g["rect"])
                    if not got:
                        _fail("fixture: no genome sample to inject")
                    g["sample"] = got[0]["id"]
                g["host"] = _spawn(t, HOST, x + 4, z + 3)
                _give(t, g["doer"], g["sample"])
                _inject(t, g["doer"], g["host"])
                row = _rows(t).get(g["host"])
                if "RM_AmoebaGestation" not in _hdefs(row):
                    _fail("the host carries no RM_AmoebaGestation after the inject job (hediffs: %s)"
                          % sorted(_hdefs(row)))
                if _things(t, SAMPLE, g["rect"]):
                    _fail("a sample is still lying around after being injected")

        with _comp(t, "gestation_dies_producing_one_organ_batch"):
            if _live(t):
                g = _STATE["g"]
                new = _finish_gestation(t, g["host"], g["rect"])
                if _alive(_rows(t).get(g["host"])):
                    _fail("the host survived completing its gestation (it is consumed)")
                if not 2 <= len(new) <= 4:
                    _fail("expected a batch of 2-4 organs/limbs, found %d: %s" % (len(new), new))
                if any(d in LIMB_ITEMS for d in new):
                    _fail("a normal sample produced a monstrous limb")
    _stable(t, body)


def _monstrous_components(t):
    """Runs INSIDE the coalescence chain, on its pad, because the Monstrous samples lie there and the
    chain's cleanup would destroy them. The colonist and the two hosts are spawned beside them."""
    with _comp(t, "monstrous_fixture", poison=True):
        if _live(t):
            need = _STATE.get("monstrous") or []
            if len(need) < 2:
                _unmeasured(t, "the collapse left %d Monstrous samples (need 2)" % len(need))
            _end_conditions(t)
            x, z = t.anchor
            _STATE["m"] = {"doer": t.spawn_pawn("Colonist", hostile=False), "rect": _rs(_rect(t, 28)),
                           "samples": need[:2], "x": x, "z": z}
            if not _STATE["m"]["doer"]:
                _fail("fixture: no colonist")

    with _comp(t, "monstrous_gestation_grows_one_limb", toggle="grownLimbsEnabled"):
        if _live(t):
            m = _STATE["m"]
            if not _sample_alive(t, m["samples"][0]):
                _unmeasured(t, "the first Monstrous sample no longer exists")
            host = _spawn(t, HOST, m["x"] + 8, m["z"])
            _give(t, m["doer"], m["samples"][0])
            _inject(t, m["doer"], host)
            if "RM_AmoebaGestation" not in _hdefs(_rows(t).get(host)):
                _fail("no gestation after injecting a Monstrous sample")
            new = _finish_gestation(t, host, m["rect"])
            limbs = [d for d in new if d in LIMB_ITEMS]
            organs = [d for d in new if d in ORGANS]
            if len(limbs) != 1 or organs:
                _fail("a Monstrous sample should grow exactly 1 grown limb and no organs; found "
                      "%d limb(s), %d organ(s)" % (len(limbs), len(organs)))

    with _comp(t, "grown_limbs_off_grows_organs", toggle="grownLimbsEnabled"):
        if _live(t):
            m = _STATE["m"]
            if not _sample_alive(t, m["samples"][1]):
                _unmeasured(t, "the second Monstrous sample no longer exists")
            with _setting(t, "grownLimbsEnabled", False):
                host = _spawn(t, HOST, m["x"] + 8, m["z"] + 4)
                _give(t, m["doer"], m["samples"][1])
                _inject(t, m["doer"], host)
                new = _finish_gestation(t, host, m["rect"])
                limbs = [d for d in new if d in LIMB_ITEMS]
                organs = [d for d in new if d in ORGANS]
                if limbs or not 2 <= len(organs) <= 4:
                    _fail("with grownLimbsEnabled off a Monstrous sample should grow the normal "
                          "organ batch (2-4); found %d limb(s), %d organ(s)" % (len(limbs), len(organs)))


def _sample_alive(t, sid):
    r = t.bridge_call("jawa/inspect_string", thingIds=sid)
    rows = (r or {}).get("things") or []
    return bool(rows) and not rows[0].get("error")


# --------------------------------------------------------------------------- chain: log

@suite.chain("log")
def log_chain(t):
    with _comp(t, "log_clean"):
        if _live(t):
            buf = t.bridge_call("jawa/drain_log", limit=1)
            if not (buf or {}).get("totalInBuffer"):
                _unmeasured(t, "drain_log buffer is empty: cannot see the log at all")
            r = t.bridge_call("jawa/drain_log", contains="Contagion", errorsOnly=True, limit=50)
            bad = [m.get("text") for m in (_ok(r, "drain_log").get("messages") or [])]
            owned = set(n for ns in DEFS_BY_TYPE.values() for n in ns)
            r2 = t.bridge_call("jawa/drain_log", contains="cross-reference", errorsOnly=True, limit=100)
            xref = [m.get("text") for m in ((r2 or {}).get("messages") or [])
                    if any(d in (m.get("text") or "") for d in owned)]
            _note(t, "log scan", {"contagion errors": len(bad), "xref naming our defs": len(xref),
                                  "bufferLines": buf.get("totalInBuffer")})
            if bad or xref:
                _fail("log carries errors: %s" % [str(x)[:160] for x in (bad + xref)[:4]])


# --------------------------------------------------------------------------- chain: site_restore (last)

@suite.chain("site_restore")
def site_restore(t):
    with _comp(t, "restore_tile"):
        if _live(t):
            tile, orig = _STATE.get("tile"), _STATE.get("orig_biome")
            if tile is None or not orig:
                _unmeasured(t, "no retile was recorded; nothing to restore")
            _ok(t.bridge_call("jawa/world_tile_set", tiles=str(tile), biome=orig, readBack=1),
                "world_tile_set(restore)")
            _ok(t.bridge_call("jawa/world_commit", redraw=False, recalcPaths=False), "world_commit")
            if _map_biome(t)[0] != orig:
                _fail("the map's biome did not return to %s" % orig)
