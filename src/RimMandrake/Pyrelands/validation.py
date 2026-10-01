"""validation.py -- modcheck suite for RimMandrake Pyrelands.

Plan: design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md. Walk:
design/validation_walks/RimMandrake/Pyrelands.md (19 must-show bars, 1 cannot-show).

PACKAGING. This dev folder (`src/RimMandrake/Pyrelands`, packageId `mandrake.rm.pyrelands`) is
the SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes` (Biomes.compose.json,
wave 2), so the thing a run must load is `mandrake.rm.biomes` plus `mandrake.rut.patches` (the
fauna roster), `mandrake.rsw.swbestiary` (seven roster keys; the MayRequire on that patch
Operation is inert, so the list must carry it) and `mandrake.rut.pyrelandsmechanics`. The
walk's `list:` line says so. `modcheck run Pyrelands` appends the DEV folder's packageId with
no dependency closure and would land on a list without the biome, so drive the trial's own
tier instead (northstar_plan.py).

Wiring: every must-show bar has exactly one component whose name is the bar id minus `pyre_`
and whose `shows=` claims that bar. The `pyre_cannot_ordinary_rain` cannot-show bar is checked
by the `cannot_ordinary_rain` component. Components that read independent state each get their
OWN chain, because a FAIL inside a chain turns every later component in it UNMEASURED.

Predicates read IMMUTABLE manifests (plan 1.3 / 2.3a): 3 plants and 15 animal kinds. A live
def that differs from the manifest is its own failure, so a patch cannot make an intruder
"allowed". Thresholds marked CALIBRATING (the plan's scale mark) are recorded as evidence and
never gate until the owner rules them.

Every bridge call here uses only the parameters the live tool declares (the bridge refuses an
undeclared one). Result shapes MEASURED live 2026-10-01: `jawa/list_things` reports
`countMatched` and a whole-result `perDef` table even when `limit` truncates the rows;
`jawa/list_pawns` rows carry `faction` (null for wild) and `intelligence`; `jawa/get_def`
puts `terrainPatchMakers` under `extra`; `jawa/get_defs` reads `wildPlants` and
`baseWeatherCommonalities` but CANNOT serialise `wildAnimals` (a non-public List), so the
animal manifest read-back is UNMEASURED by construction. A component that cannot measure
calls `_unmeasured()`, which records UNMEASURED with its reason; it never passes.

Fire hygiene: every fire burns on its own pad, ringed by `RM_FE_FirebreakLine`, and the whole
map is extinguished afterwards, so one chain's fire cannot spread into another chain's census.
Pads sit away from the colonists at the map centre.

Settings fields are `public static` (RimMandrake.Pyrelands.RM_PyrelandsSettings); OFF arms use
`t.set_setting` (jawa/mod_settings_field) and always restore in a `finally`.

Not expressible with current bridge tools: forcing one `WeatherEvent_LightningStrike`
(fulgurite_after_lightning locks DryThunderstorm and counts fulgurite), reading
`MapComponent_BurnLine` directly (burn_line_present counts free-standing Fire, which is exactly
what that component measures), and flyer flight (firehawk_carries_ember reads job state only;
flyers are never live-tested unattended).
"""
import contextlib
import importlib.util
import json
import os
import sys
import time

from modcheck import Suite, ExpectationFailed

suite = Suite("Pyrelands")
suite.toggles = ["fulguriteEnabled", "ashDustingEnabled", "scorchFruitEnabled",
                 "ashfallAccumulationEnabled", "biomeGenerationEnabled"]

SETTINGS = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
SOIL = "RM_FE_Ground_Soil"
FIREBREAK = "RM_FE_FirebreakLine"
TEST_SIZE = 24

# Immutable manifests (plan 1.3). 3 plants; 15 animal kinds.
PLANT_MANIFEST = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass",
                            "RM_FE_Plant_ScorchFruit"])
WILD_PLANTS = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass"])  # ScorchFruit is fire-born
ANIMAL_MANIFEST = frozenset([
    "RUT_FireHawk", "RUT_FurnaceBeast",
    "RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka",
    "RUT_Emberscythe", "RUT_Sytheclaw", "RUT_Barbslinger", "RUT_FireWasp", "RUT_Flamefang",
    "RUT_Ashwallow"])
ASH_RUNGS = ("RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy", "RM_FE_Ash_Deep")
STOCK_GROUND = ("Sand", "Soil", "Gravel", "SoilRich")
ORDINARY_RAIN = ("Rain", "RainyThunderstorm", "FoggyRain")
# Mechanics that must be OFF during the controlled bars (plan 2.3a isolation).
ISOLATION_OFF = ["burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled",
                 "furnaceWorldMigrationEnabled", "burrowOnFireEnabled",
                 "furnaceThermalEnabled", "fulguriteEnabled"]
FIRE_HAWK_JOB = "RM_FireHawkCarryEmber"   # JobDefs/RM_PyrelandsJobs.xml (renamed from RUT_)

# Pads (map is 250x250, colonists stand at the centre). Each fire gets its own pad.
PAD_FIRE_TICK = (60, 60)
PAD_LADDER = (60, 190)
PAD_REGROW = (190, 190)
PAD_FIRE_BORN = (190, 60)
PAD_HARVEST = (125, 95)
PAD_SPOIL = (125, 165)
PAD_HAWK = (60, 125)
PAD_BURROW = (190, 125)
PAD_WARMTH = (95, 160)
PAD_ROOMS = (160, 90)
PAD_PROBE = (225, 225)
FIRE_PADS = (PAD_FIRE_TICK, PAD_LADDER, PAD_REGROW, PAD_FIRE_BORN, PAD_HAWK, PAD_BURROW)

_GEN = {}   # gen-time readings shared between chains of ONE run (chains run in order)


# --------------------------------------------------------------------------- helpers

def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False for the
    offline declaration probe, so manual assertions never trip on its no-op (None) results."""
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
def _comp(t, name, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail
    names the real reason, and the chain is not poisoned for an independent next component."""
    before = t.upstream_failed
    t._why = None
    _on_site(t)
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
        t.upstream_failed = False
    t._why = None
    if t.session is not None:   # progress line (the driver prints only at the very end)
        c = t.components[-1]
        print("[pyre] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _wait(t, n, fast=None):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact, one tick per frame: MEASURED
    ~53 ticks/s, so 7 days would take ~2.2 h). Long waits run the game at Ultrafast and poll the
    real clock, then pause; the overshoot is recorded. Raises on a stalled clock."""
    if t.session is None or t.upstream_failed or (n <= 5000 and not fast):
        return t.wait_ticks(n)
    _on_site(t)
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
                raise ExpectationFailed("clock stalled at %d during a %d-tick wait (a modal "
                                        "dialog pausing the game?)" % (now, n))
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    now = s._ticks()
    if now < target:
        t.wait_ticks(target - now)
        now = s._ticks()
    t._record("_wait(%d) at Ultrafast -> %d real ticks" % (n, now - start), now - start)
    _on_site(t)


def _note(t, label, data):
    """Evidence record. Also echoed to stderr: the results JSON keeps only a ~300-char
    excerpt of a component's evidence, so the numbers would otherwise be lost."""
    t._record(label, data)
    if t.session is not None:
        print("[pyre-note] %s: %s" % (label, json.dumps(data, default=str)[:1500]),
              file=sys.stderr, flush=True)


def _on_site(t):
    """Keep the Pyrelands site the CURRENT map. Live 2026-10-01: the settlement-naming dialog
    opens once time runs, and it (or closing it) hops Find.CurrentMap back to the colony map,
    after which every current-map tool silently reads the wrong map."""
    if t.session is None:
        return
    r = t.session.call("jawa/map_info") or {}
    if r.get("mapBiome") == "RM_Pyrelands":
        _GEN.setdefault("site_map", r.get("mapId"))
        return
    try:
        t.session.call("jawa/window_list_close", action="close", typeName="NamePlayer",
                       closeAll=True)
    except Exception:
        pass   # no such dialog open: nothing to close
    site = _GEN.get("site_map", 1)
    t.session.call("jawa/set_current_map", mapId=site)
    r = t.session.call("jawa/map_info") or {}
    t._record("on_site: current map was not the Pyrelands site; restored", r.get("mapId"))
    if r.get("mapBiome") != "RM_Pyrelands":
        raise ExpectationFailed("could not make the Pyrelands site (map %s) current: %r"
                                % (site, r.get("mapBiome")))


def _pad(t, xz):
    _on_site(t)
    t.anchor = xz


def _rect(t, size=TEST_SIZE, dx=0, dz=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half + dz, size, size


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _map_size(t):
    r = t.bridge_call("jawa/map_info") or {}
    return r.get("sizeX", 250), r.get("sizeZ", 250)


def _whole(t):
    sx, sz = _map_size(t)
    return "0,0,%d,%d" % (sx, sz)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _count(t, defName, rect=None):
    """Count of one def over `rect` ('x,z,w,h') or the whole map (None). Raises on an
    unreadable result rather than reading it as zero."""
    kw = {"defName": defName, "limit": 1}
    if rect:
        kw["rect"] = rect
    r = t.bridge_call("jawa/list_things", **kw)
    if not _live(t):
        return 0
    _ok(r, "list_things(%s)" % defName)
    if "countMatched" not in r or not r.get("scanned"):
        _fail("list_things(%s) unreadable (no countMatched / scanned 0): %r" % (defName, r))
    return r["countMatched"]


def _things(t, defName, rect=None, limit=500):
    kw = {"defName": defName, "limit": limit}
    if rect:
        kw["rect"] = rect
    r = t.bridge_call("jawa/list_things", **kw)
    if not _live(t):
        return []
    return list(_ok(r, "list_things(%s)" % defName).get("things") or [])


def _whole_map(t, group):
    """{defName: n} over the whole map for a ThingRequestGroup, from the result-wide `perDef`
    table; refuses an empty scan or a table that does not add up to `countMatched`."""
    r = t.bridge_call("jawa/list_things", group=group, limit=1)
    if not _live(t):
        return {}
    _ok(r, "list_things(group=%s)" % group)
    per = r.get("perDef")
    if not r.get("scanned") or not isinstance(per, dict) or sum(per.values()) != r.get("countMatched"):
        _fail("whole-map %s census unreadable or inconsistent: scanned=%r countMatched=%r perDef=%r"
              % (group, r.get("scanned"), r.get("countMatched"), per))
    return dict(per)


def _fresh_site(t):
    """Refuse a census on a site that is not a fresh map. RM_FE_Ash_Deep is reachable only by
    burning (plan 1.3: the patchmaker lays Trace/Light/Heavy), so deep ash outside this suite's
    own fire pads means the land has burned since generation -- a census then describes that
    fire, not the biome. Live 2026-10-01: run 4's lightning chain burned the whole site."""
    if not _live(t):
        return
    if "fresh" not in _GEN:
        r = t.bridge_call("jawa/get_terrain_batch", rects=_whole(t))
        outside = 0
        for op in ((r or {}).get("ops") or "").split(";"):
            if not op.startswith("RM_FE_Ash_Deep:"):
                continue
            p = [int(v) for v in op.split(":", 1)[1].split(",")]
            w, h = (p[2] if len(p) > 2 else 1), (p[3] if len(p) > 3 else 1)
            for cx in range(p[0], p[0] + w):
                for cz in range(p[1], p[1] + h):
                    if not any(abs(cx - px) <= 18 and abs(cz - pz) <= 18 for (px, pz) in FIRE_PADS):
                        outside += 1
        _GEN["fresh"] = outside
        _note(t, "deep-ash cells outside the suite's fire pads", outside)
    if _GEN["fresh"] > 100:
        _unmeasured(t, "site is not a fresh map: %d RM_FE_Ash_Deep cells outside the suite's fire "
                       "pads (deep ash only comes from burning); a fresh-map census is not "
                       "measurable here -- reload the site" % _GEN["fresh"])


def _ops_counts(ops):
    """jawa/get_terrain_batch `ops` ('Def:x,z,w,h;...') -> {defName: cells}."""
    out = {}
    for op in (ops or "").replace("\n", ";").split(";"):
        if ":" not in op:
            continue
        d, nums = op.split(":", 1)
        p = [int(v) for v in nums.split(",") if v.strip()]
        w = p[2] if len(p) > 2 else 1
        h = p[3] if len(p) > 3 else 1
        out[d.strip()] = out.get(d.strip(), 0) + w * h
    return out


def _terrain(t, rect):
    """{terrainDef: cells} over rect, or {} offline."""
    r = t.bridge_call("jawa/get_terrain_batch", rects=rect)
    if not _live(t):
        return {}
    _ok(r, "get_terrain_batch(%s)" % rect)
    if r.get("cellsRead") != r.get("cellsRequested"):
        _fail("get_terrain_batch(%s) read %r of %r cells" % (rect, r.get("cellsRead"),
                                                            r.get("cellsRequested")))
    return _ops_counts(r.get("ops"))


def _get_defs(t, defs, fields, deep=True):
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, deep=deep)
    if not _live(t):
        return {}
    _ok(r, "get_defs(%s)" % defs)
    if r.get("notFound"):
        _fail("get_defs could not resolve %r" % r.get("notFound"))
    return dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or []))


def _plants(t, plant, rect, growth=1.0):
    t.bridge_call("jawa/set_plants", ops="%s:%s" % (plant, _rs(rect)), growth=growth)


def _firebreak(t, rect, width=4):
    """Ring `rect` with the biome's own non-flammable firebreak terrain and strip its plants."""
    x, z, w, h = rect
    ring = [(x - width, z - width, w + 2 * width, width), (x - width, z + h, w + 2 * width, width),
            (x - width, z, width, h), (x + w, z, width, h)]
    t.bridge_call("jawa/set_terrain_batch", ops=";".join("%s:%s" % (FIREBREAK, _rs(r)) for r in ring),
                  layer="top")
    t.bridge_call("jawa/set_plants", ops=";".join("CLEAR:%s" % _rs(r) for r in ring))


def _soil(t, rect):
    """Re-lay the cohort as RM_FE_Ground_Soil: a pad burned by an earlier run sits on deep ash,
    which neither grows grass nor takes fire."""
    t.bridge_call("jawa/set_terrain", x=rect[0], z=rect[1], terrainDef=SOIL, width=rect[2],
                  height=rect[3], layer="top")


def _extinguish(t):
    t.bridge_call("jawa/map_fire", action="extinguish", rect=_whole(t))


def _fire(t, rect, size=1.2):
    r = t.bridge_call("jawa/map_fire", action="start", rect=_rs(rect), fireSize=size)
    if _live(t) and not (r or {}).get("firesStarted"):
        _fail("map_fire started no fire in %s: %r" % (_rs(rect), r))
    return r


def _spawn_wild(t, kind, x, z):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none", count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s, wild) returned no pawn: %r" % (kind, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _pawn_row(t, pid, rect=None, health=False):
    kw = {"limit": 500}
    if health:
        kw["includeHealth"] = True
    if rect:
        kw["rect"] = rect
    r = t.bridge_call("jawa/list_pawns", **kw)
    if not _live(t):
        return None
    for p in (_ok(r, "list_pawns").get("pawns") or []):
        if p.get("id") == pid:
            return p
    return None


def _has_hediff(row, hediff):
    return hediff in json.dumps(((row or {}).get("health") or {}).get("hediffs") or [])


def _job_of(t, pid):
    r = t.bridge_call("jawa/site_state")
    for p in ((r or {}).get("pawns") or []):
        if p.get("id") == pid:
            return p.get("job")
    return None


def _colonist(t):
    r = t.bridge_call("jawa/list_pawns", faction="player", limit=50)
    if not _live(t):
        return None
    for p in (_ok(r, "list_pawns(player)").get("pawns") or []):
        if p.get("intelligence") == "Humanlike" and not p.get("downed") and not p.get("dead"):
            return p
    _fail("no able colonist on the site")


def _need(t, pid, need):
    r = t.bridge_call("jawa/pawn_need", pawn=pid, action="list")
    for n in ((r or {}).get("needs") or []):
        if n.get("need") == need:
            return n.get("level")
    return None


def _set(t, values):
    t.set_setting(SETTINGS, values)


def _isolate(t):
    """Switch the plan 2.3a isolation set OFF; the caller restores via _restore."""
    _set(t, dict((f, False) for f in ISOLATION_OFF))


def _restore(t):
    _set(t, dict((f, True) for f in ISOLATION_OFF))


def _preflight_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight_pyrelands.py")
    spec = importlib.util.spec_from_file_location("pyre_preflight_for_suite", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- gen-time census
# These run FIRST: the plan's census bars are read before any tick or fire of this run.

@suite.chain("mapgen_log")
def mapgen_log(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "mapgen_log_clean", shows=["pyre_mapgen_log_clean"]):
        # jawa/drain_log holds only the last 1000 lines, so it cannot reach back to mapgen.
        # Player.log of this game process covers the whole load + the site; scanned with the
        # same instrument as pre-flight row 3.8.7 (CommonalityOfAnimal, roster xrefs, Pyrelands
        # exceptions; the documented burnedDef config lines are allowed).
        if _live(t):
            pf = _preflight_module()
            from game_paths import LOCALLOW
            path = os.path.join(LOCALLOW, "Player.log")
            if not os.path.isfile(path):
                _unmeasured(t, "no Player.log at %s" % path)
            with open(path, "rb") as fh:
                text = fh.read().decode("utf-8", "replace")
            fatal, xref, exc, allowed = pf.scan_log(text)
            _note(t, "Player.log scan", {"fatal": fatal[:5], "xref": xref[:5], "exc": exc[:5],
                                         "allowedBurnedDef": allowed, "bytes": len(text)})
            bad = fatal + xref + exc
            if bad:
                _fail("log not clean (%d line(s)): %s" % (len(bad), " | ".join(l.strip()[:160] for l in bad[:3])))
            if allowed > pf.LOG_ALLOWED_MAX:
                _fail("%d 'burnedDef is flammable' lines > %d documented" % (allowed, pf.LOG_ALLOWED_MAX))
        t.screenshot()


@suite.chain("plant_census")
def plant_census(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "plant_distribution_correct", shows=["pyre_plant_distribution_correct"]):
        _fresh_site(t)
        live = _get_defs(t, "BiomeDef/RM_Pyrelands", "wildPlants,plantDensity")
        census = _whole_map(t, "Plant")
        if _live(t):
            _GEN["scorchfruit"] = [(p.get("x"), p.get("z")) for p in
                                   _things(t, "RM_FE_Plant_ScorchFruit", limit=500)]
            row = live.get("RM_Pyrelands") or {}
            wp = row.get("wildPlants")
            keys = set(x.get("plant") for x in wp) if isinstance(wp, list) else None
            _note(t, "gen plant census", {"perDef": census, "wildPlants": wp,
                                          "plantDensity": row.get("plantDensity")})
            # Sanity probe (plan bar 1): the census must be able to SEE a foreign plant.
            x, z = PAD_PROBE
            t.bridge_call("jawa/set_plants", ops="Plant_Grass:%d,%d,1,1" % (x, z), growth=1.0)
            seen = _whole_map(t, "Plant").get("Plant_Grass", 0) - census.get("Plant_Grass", 0)
            t.bridge_call("jawa/set_plants", ops="CLEAR:%d,%d,1,1" % (x, z))
            if seen < 1:
                _fail("sanity probe: a spawned Plant_Grass was not counted by the census")
            if keys != set(WILD_PLANTS):
                _fail("live wildPlants %r differs from the immutable manifest %r"
                      % (sorted(keys or []), sorted(WILD_PLANTS)))
            foreign = dict((k, v) for k, v in census.items() if k not in PLANT_MANIFEST)
            e, q = census.get("RM_FE_Plant_EmberGrass", 0), census.get("RM_FE_Plant_Quickgrass", 0)
            _note(t, "CALIBRATING ember:quickgrass ratio (expect ~2.4)",
                  {"ember": e, "quickgrass": q, "ratio": (float(e) / q) if q else None})
            if foreign:
                _fail("foreign plant defs on the site: %r" % foreign)
        t.screenshot()


@suite.chain("animal_census")
def animal_census(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "animal_distribution_correct", shows=["pyre_animal_distribution_correct"]):
        _fresh_site(t)
        live = _get_defs(t, "BiomeDef/RM_Pyrelands", "wildAnimals")
        r = t.bridge_call("jawa/list_pawns", limit=1000)
        if _live(t):
            _ok(r, "list_pawns")
            if r.get("truncated"):
                _fail("wild animal census truncated: %r" % r.get("message"))
            wild = [p for p in (r.get("pawns") or [])
                    if p.get("faction") is None and p.get("intelligence") == "Animal"
                    and not p.get("dead")]
            counts = {}
            for p in wild:
                counts[p.get("kindDef")] = counts.get(p.get("kindDef"), 0) + 1
            ranked = sorted(counts.items(), key=lambda kv: -kv[1])
            _note(t, "wild animal census", {"counts": counts, "total": len(wild)})
            _note(t, "CALIBRATING distinct kinds / Gizka rank",
                  {"distinct": len(counts), "top3": ranked[:3]})
            foreign = dict((k, v) for k, v in counts.items() if k not in ANIMAL_MANIFEST)
            if foreign:
                _fail("foreign wild animal kinds on the site: %r" % foreign)
            if len(wild) < 12:
                _fail("only %d wild animals on the site (need >=12)" % len(wild))
            wa = (live.get("RM_Pyrelands") or {}).get("wildAnimals")
            if not isinstance(wa, list):
                _unmeasured(t, "census clean (%d wild, %d kinds, none foreign) but the live "
                               "wildAnimals read-back the plan requires is not readable: %r"
                            % (len(wild), len(counts), wa))
            keys = set(x.get("animal") for x in wa)
            if keys != set(ANIMAL_MANIFEST):
                _fail("live wildAnimals %r differs from the 15-kind manifest" % sorted(keys))
        t.screenshot()


@suite.chain("grass_cover")
def grass_cover(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "grass_chokes_ground", shows=["pyre_grass_chokes_ground"]):
        _fresh_site(t)
        census = _whole_map(t, "Plant")
        terr = _terrain(t, _whole(t))
        if _live(t):
            fert = _get_defs(t, ";".join("TerrainDef/%s" % d for d in sorted(terr)), "fertility",
                             deep=False)
            plantable = sum(n for d, n in terr.items()
                            if (fert.get(d) or {}).get("fertility", 0) > 0 and d != "RM_FE_Ash_Deep")
            b = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=1)
            built = (b or {}).get("countMatched", 0)
            plantable -= built
            covered = sum(v for k, v in census.items() if k in PLANT_MANIFEST)
            ratio = float(covered) / plantable if plantable else None
            _note(t, "coverage", {"covered": covered, "plantableCells": plantable,
                                  "buildingsExcluded": built, "ratio": ratio,
                                  "roofedCells": "not excluded (no whole-map roof read)"})
            if not plantable:
                _unmeasured(t, "plantable cell count is zero / unreadable: %r" % terr)
            if ratio < 0.85:
                _fail("plant coverage %.3f of %d plantable cells (< 0.85)" % (ratio, plantable))
        t.screenshot()


@suite.chain("ruins")
def ruins(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "ruins_scorched", shows=["pyre_ruins_scorched"]):
        _fresh_site(t)
        ruins_ = _things(t, "RM_FE_ScorchRuins", limit=50)
        if _live(t):
            if not ruins_:
                _unmeasured(t, "this site carries no RM_FE_ScorchRuins and no bridge tool forces "
                               "the genstep; the ruin footprint cannot be read")
            cells = ";".join("%d,%d,5,5" % (r["x"] - 2, r["z"] - 2) for r in ruins_[:10])
            got = _terrain(t, cells)
            _note(t, "ruin footprint terrain", got)
            if not any(a in got for a in ASH_RUNGS):
                _fail("ruin footprint carries no ash terrain: %r" % got)
        t.screenshot()


@suite.chain("burn_line")
def burn_line(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "burn_line_present", shows=["pyre_burn_line_present"]):
        _fresh_site(t)
        # MapComponent_BurnLine.Measure() counts free-standing Fire; no tool reads the component
        # itself, so the same count is taken directly.
        fires = _things(t, "Fire", limit=2000)
        s = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                          field="burnLineEnabled")
        if _live(t):
            _note(t, "free-standing fire at the census", {"fires": len(fires),
                                                          "burnLineEnabled": (s or {}).get("value")})
            if not fires:
                _unmeasured(t, "0 fires on the site, but the site recipe (northstar_site.isolate) "
                               "holds burnLineEnabled OFF through generation and settle, so whether "
                               "a FRESH map shows a burn line is not observable on this fixture")
        t.screenshot()


@suite.chain("startup_and_def_wiring")
def startup_and_def_wiring(t):
    """Pure reads of what the session has loaded (toggle floor)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "fulgurite_armed_only", toggle="fulguriteEnabled"):
        # The load-time "fulgurite-spawn: armed" line rolls out of drain_log's 1000-line buffer;
        # the Harmony patch itself is the direct proof that the rule is armed.
        r = t.bridge_call("jawa/harmony_patches", typeName="RimWorld.WeatherEvent_LightningStrike",
                          methodName="DoStrike")
        if _live(t):
            posts = [p for m in (_ok(r, "harmony_patches").get("methods") or [])
                     for p in (m.get("postfixes") or [])]
            if not any("Patch_LightningStrike_Fulgurite" in (p.get("patchMethod") or "") for p in posts):
                _fail("no Pyrelands fulgurite postfix on WeatherEvent_LightningStrike.DoStrike: %r" % posts)
        t.screenshot()

    with _comp(t, "biome_def_wiring", toggle="biomeGenerationEnabled"):
        d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
        if _live(t):
            makers = ((_ok(d, "get_def") or {}).get("extra") or {}).get("terrainPatchMakers") or []
            if len(makers) < 1:
                _fail("RM_Pyrelands resolved with no terrainPatchMakers: %r" % d)
            names = [th.get("terrain") for th in ((makers[0] or {}).get("thresholds") or [])]
            if "RM_FE_Ash_Trace" not in names:
                _fail("first terrainPatchMaker lacks RM_FE_Ash_Trace: %r" % names)
        t.screenshot()


@suite.chain("ground_ash_ladder")
def ground_ash_ladder(t):
    """(a) gen-time terrain census of the whole map, then (b) a fixed 20x20 cohort pre-cleared
    to RM_FE_Ground_Soil, grassed and burned 3 times. Isolation set OFF."""
    _pad(t, PAD_LADDER)
    t.clear_area(size=TEST_SIZE)
    burn = _rect(t, 20)
    try:
        with _comp(t, "ground_ash_ladder", shows=["pyre_ground_ash_ladder"]):
            _fresh_site(t)
            gen = _terrain(t, _whole(t))
            if _live(t):
                _note(t, "gen terrain census", gen)
                stock = dict((s, gen[s]) for s in STOCK_GROUND if gen.get(s))
                if stock:
                    _fail("stock ground terrains present on a Pyrelands map: %r" % stock)
                water = sum(n for d, n in gen.items() if "Water" in d)
                land = sum(gen.values()) - water
                fam = sum(n for d, n in gen.items() if d.startswith("RM_FE_Ground_"))
                if land and float(fam) / land < 0.60:
                    _fail("RM_FE_Ground_* is %.2f of land cells (< 0.60)" % (float(fam) / land))
                if sum(1 for a in ASH_RUNGS[:3] if gen.get(a)) < 2:
                    _fail("fewer than 2 of 3 patchmaker ash rungs at gen: %r"
                          % dict((a, gen.get(a, 0)) for a in ASH_RUNGS))
            _isolate(t)
            _firebreak(t, burn)
            t.bridge_call("jawa/set_terrain", x=burn[0], z=burn[1], terrainDef=SOIL, width=20,
                          height=20, layer="top")
            series = []
            for cycle in range(3):
                _plants(t, "RM_FE_Plant_EmberGrass", burn)
                _fire(t, burn)
                # Fire.TryBurnFloor runs only once a Fire has lived TicksToBurnFloor = 7500 ticks
                # (decompiled RimWorld.Fire); extinguishing sooner can never move the ladder.
                _wait(t, 8000)
                _extinguish(t)
                got = _terrain(t, _rs(burn))
                series.append(got)
                if cycle == 0 and _live(t):
                    on_ash = sum(v for k, v in got.items() if k in ASH_RUNGS)
                    if on_ash < 0.5 * 400:
                        _fail("after burn 1, %d of 400 cohort cells on an ash rung (<50%%): %r"
                              % (on_ash, got))
            _note(t, "cohort terrain after each burn", series)
            if _live(t) and not series[-1].get("RM_FE_Ash_Deep"):
                _fail("no RM_FE_Ash_Deep in the cohort after 3 burn cycles: %r" % series)
            t.screenshot(rect=burn)
    finally:
        _extinguish(t)
        _restore(t)


# --------------------------------------------------------------------------- toggle floor

@suite.chain("fire_tick_effects")
def fire_tick_effects(t):
    """One fire on a GRASSED patch of RM_FE_Ground_Soil (fuel is what makes a fire reach
    `TryBurnFloor`; a fuel-less sand fire goes out -- the 2026-09-13 false RED), ringed by a
    firebreak, watched long enough for both fire-tick postfixes to roll."""
    _pad(t, PAD_FIRE_TICK)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x0, z0, w, h = rect
    try:
        _firebreak(t, rect)
        ground = t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=SOIL,
                               width=w, height=h, layer="top")
        # cells already on the target terrain are correct, not unpainted
        if _live(t) and (ground or {}).get("cellsChanged", 0) + (ground or {}).get("cellsAlreadyCorrect", 0) < w * h:
            _fail("set_terrain(%s) over %s did not paint the whole rect: %r" % (SOIL, _rs(rect), ground))
        _plants(t, "RM_FE_Plant_EmberGrass", rect)

        with _comp(t, "ash_dusting", toggle="ashDustingEnabled"):
            _fire(t, rect)
            _wait(t, 2600)
            n = _count(t, "RM_FE_Filth_LooseAsh", _rs(rect))
            if _live(t) and n < 1:
                _fail("expected >=1 RM_FE_Filth_LooseAsh in %s after 2600 ticks of fire, got %d"
                      % (_rs(rect), n))
            t.screenshot(rect=rect)

        with _comp(t, "scorch_fruit_seed", toggle="scorchFruitEnabled"):
            _wait(t, 9000)
            n = _count(t, "RM_FE_Plant_ScorchFruit", _rs(rect))
            whole = _count(t, "RM_FE_Plant_ScorchFruit")
            _note(t, "ScorchFruit in the rect / whole map (cap 40)", {"rect": n, "map": whole})
            if _live(t):
                if n < 1:
                    _fail("expected >=1 RM_FE_Plant_ScorchFruit in %s after ~11,600 ticks of fire, "
                          "got %d" % (_rs(rect), n))
                if n > 40:  # RM_PyrelandsSettings.scorchFruitMapCap shipped default
                    _fail("ScorchFruit count %d exceeds the per-map cap 40" % n)
            t.screenshot(rect=rect)
    finally:
        _extinguish(t)


@suite.chain("ashfall_weather_accumulation")
def ashfall_weather_accumulation(t):
    """Ashfall counted over the WHOLE map from ZERO: deposits land on
    `CellFinder.RandomCell(map)`, so a 24x24 rect expected ~0 hits (the 2026-09-13 false RED)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ashfall_accumulates", toggle="ashfallAccumulationEnabled"):
        _extinguish(t)
        t.bridge_call("jawa/destroy_batch", rects=_whole(t), categories="Filth")
        start = _count(t, "RM_FE_Filth_LooseAsh")
        if _live(t) and start != 0:
            _fail("could not clear ash to zero before the run: %d remain" % start)
        try:
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
            _wait(t, 2600)
            n = _count(t, "RM_FE_Filth_LooseAsh")
        finally:
            t.bridge_call("jawa/weather_set", unlock=True)
        if _live(t) and n < 1:
            _fail("expected >=1 NEW RM_FE_Filth_LooseAsh over the whole map after 2600 ticks "
                  "under RM_FE_Weather_AshFall, got %d" % n)
        t.screenshot()


# --------------------------------------------------------------------------- weather

@suite.chain("ashfall_drifts")
def ashfall_drifts(t):
    _pad(t, PAD_PROBE)
    try:
        with _comp(t, "ashfall_darkens_drifts", shows=["pyre_ashfall_darkens_drifts"]):
            _extinguish(t)
            t.bridge_call("jawa/destroy_batch", rects=_whole(t), categories="Filth")
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
            _wait(t, 4000)
            series = []
            for _ in range(4):
                series.append(_count(t, "RM_FE_Filth_LooseAsh"))
                _wait(t, 2500)
            _note(t, "whole-map LooseAsh at t=0/2500/5000/7500 after settle", series)
            if _live(t):
                if any(b < a for a, b in zip(series, series[1:])) or series[-1] < 20:
                    _fail("ash series %r not monotone or < 20 at the end" % series)
            t.screenshot()
    finally:
        t.bridge_call("jawa/weather_set", unlock=True)


def _weather_pair(t, name, other, fields):
    defs = _get_defs(t, "WeatherDef/%s;WeatherDef/%s" % (name, other), ",".join(fields))
    if _live(t):
        a, b = defs.get(name) or {}, defs.get(other) or {}
        _note(t, "def fields", {name: a, other: b})
        if not a or not b:
            _fail("get_defs returned no fields for %s / %s" % (name, other))
        if all(a.get(f) == b.get(f) for f in fields):
            _fail("%s and %s differ in none of %r" % (name, other, fields))
    try:
        t.bridge_call("jawa/weather_set", weather=name, lockWeather=True)
        _wait(t, 5000)
        t.screenshot()
    finally:
        t.bridge_call("jawa/weather_set", unlock=True)


@suite.chain("cinderfall")
def cinderfall(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "cinderfall_distinct", shows=["pyre_cinderfall_distinct"]):
        _weather_pair(t, "RM_FE_Weather_Cinderfall", "RM_FE_Weather_AshFall",
                      ("overlayClasses", "skyColorsDay", "skyColorsNightMid", "windSpeedFactor"))


@suite.chain("blackrain")
def blackrain(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "blackrain_reads", shows=["pyre_blackrain_reads"]):
        _weather_pair(t, "RM_FE_BlackRain", "Rain",
                      ("overlayClasses", "skyColorsDay", "skyColorsNightMid"))


@suite.chain("no_ordinary_rain")
def no_ordinary_rain(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "cannot_ordinary_rain", shows=["pyre_cannot_ordinary_rain"]):
        d = _get_defs(t, "BiomeDef/RM_Pyrelands", "baseWeatherCommonalities")
        if _live(t):
            table = (d.get("RM_Pyrelands") or {}).get("baseWeatherCommonalities")
            if not isinstance(table, list) or not table:
                _fail("post-patch weather table unreadable: %r" % table)
            _note(t, "post-patch baseWeatherCommonalities", table)
            rain = [w for w in table if w.get("weather") in ORDINARY_RAIN and (w.get("commonality") or 0) > 0]
            if rain:
                _fail("post-patch weather table holds ordinary rain: %r" % rain)


# --------------------------------------------------------------------------- scorch-fruit

@suite.chain("scorchfruit_fire_born")
def scorchfruit_fire_born(t):
    _pad(t, PAD_FIRE_BORN)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    try:
        with _comp(t, "scorchfruit_fire_born", shows=["pyre_scorchfruit_fire_born"]):
            _isolate(t)
            # Burn half first: a burned cohort with no fruit fails the bar whatever the census.
            _firebreak(t, rect)
            _soil(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            _fire(t, rect)
            _wait(t, 11600)
            n = _count(t, "RM_FE_Plant_ScorchFruit", _rs(rect))
            _note(t, "ScorchFruit inside the burned cohort", n)
            if _live(t):
                if n < 1:
                    _fail("no ScorchFruit spawned inside the burned cohort %s" % _rs(rect))
                gen = _GEN.get("scorchfruit")
                if gen is None:
                    _unmeasured(t, "%d ScorchFruit in the burned cohort, but the fresh-site census "
                                   "(plant_census) did not run, so 'never on unburned land' is "
                                   "unmeasured" % n)
                # The site's only fires are this suite's pads (the site recipe isolates every
                # natural igniter), so a ScorchFruit outside every fire pad grew on unburned land.
                wild = [c for c in gen if not any(abs(c[0] - px) <= 18 and abs(c[1] - pz) <= 18
                                                  for (px, pz) in FIRE_PADS)]
                _note(t, "gen ScorchFruit positions", {"all": gen, "outsideFirePads": wild})
                if wild:
                    _fail("ScorchFruit on unburned land (outside every fire pad) at the census: %r"
                          % wild)
            t.screenshot(rect=rect)
    finally:
        _extinguish(t)
        _restore(t)


@suite.chain("scorchfruit_produces")
def scorchfruit_produces(t):
    """Attributable harvest and ingest (plan 2.3a): ripe plants, forced harvest, the yield made
    by that harvest, a forced ingest, and the food delta across that ingest only."""
    _pad(t, PAD_HARVEST)
    t.clear_area(size=12)
    rect = _rect(t, 6)
    try:
        with _comp(t, "scorchfruit_produces", shows=["pyre_scorchfruit_produces"]):
            _isolate(t)
            before = set(x.get("id") for x in _things(t, "RM_FE_ScorchFruitYield", limit=500))
            _plants(t, "RM_FE_Plant_ScorchFruit", (rect[0], rect[1], 5, 2))
            plants = _things(t, "RM_FE_Plant_ScorchFruit", _rs(rect), limit=20)
            # The chain builds its own harvester (spec 1b): the site's own colonists are not part
            # of this bar and may be busy, hurt or gone.
            cid = t.spawn_pawn("Colonist", beyond=[(rect[0] - 4, rect[1]), (rect[0] - 4, rect[1])])
            if _live(t):
                if not cid:
                    _fail("could not spawn a harvester colonist")
                if not plants:
                    _fail("set_plants placed no RM_FE_Plant_ScorchFruit in %s" % _rs(rect))
                t.bridge_call("jawa/designate_batch", action="add", designation="HarvestPlant",
                              rect=_rs(rect))
                for p in plants[:3]:
                    t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Harvest",
                                  targetAId=p["id"], queue=True, waitTicks=60)
                _wait(t, 2500)
                made = [x for x in _things(t, "RM_FE_ScorchFruitYield", limit=500)
                        if x.get("id") not in before]
                _note(t, "yield made by the harvest", made)
                if not made:
                    _fail("no new RM_FE_ScorchFruitYield after a forced harvest of %d plant(s)"
                          % len(plants[:3]))
                t.bridge_call("jawa/pawn_need", pawn=cid, action="need", need="Food", level=0.2)
                f0 = _need(t, cid, "Food")
                job = t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Ingest",
                                    targetAId=made[0]["id"], count=1, waitTicks=60)
                levels = []
                for _ in range(10):        # the game is paused: ticks must be run for the ingest
                    _wait(t, 150)
                    levels.append(_need(t, cid, "Food"))
                left = [x.get("id") for x in _things(t, "RM_FE_ScorchFruitYield", limit=500)]
                _note(t, "food across the ingest", {"before": f0, "after": levels, "pawn": cid,
                                                    "orderedJob": job, "yieldConsumed":
                                                    made[0]["id"] not in left or None})
                if f0 is None or None in levels:
                    _unmeasured(t, "food need unreadable: %r -> %r" % (f0, levels))
                if max(levels) <= f0:
                    _fail("food never rose above %.3f across 1500 ticks after the ordered ingest: %r"
                          % (f0, levels))
            t.screenshot(rect=rect)
    finally:
        _restore(t)


@suite.chain("scorchfruit_spoils")
def scorchfruit_spoils(t):
    """Rot read from the item's own inspect text (CompRottable), sampled every half day, with a
    vanilla reference food beside it. [O] yield daysToRotStart 4, plant 1.1."""
    _pad(t, PAD_SPOIL)
    t.clear_area(size=12)
    x, z = t.anchor
    try:
        with _comp(t, "scorchfruit_spoils_fast", shows=["pyre_scorchfruit_spoils_fast"]):
            _isolate(t)
            # Plan 2.3a: the stack sits in a fenced cell no pawn can reach. In the open a wild
            # grazer ate it at day 2 (runs 5 and 6, steel ring included). A sealed room (player
            # door: animals cannot open it) held three stacks untouched (probe 2026-10-01).
            # Unrefrigerated: the room tracks the site's own ~45-58 C.
            room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,11,9" % (x - 5, z - 3),
                                 stuffDef="Steel")
            if _live(t):
                _ok(room, "make_empty_room")
            t.bridge_call("jawa/spawn_batch", ops="RM_FE_ScorchFruitYield:%d,%d,10;Meat_Human:%d,%d,10"
                          % (x, z, x + 2, z))
            _plants(t, "RM_FE_Plant_ScorchFruit", (x - 3, z + 3, 3, 1))
            yid = [y.get("id") for y in _things(t, "RM_FE_ScorchFruitYield", "%d,%d,1,1" % (x, z))]
            samples, plant_at_1_5 = [], None
            for half_day in range(1, 10):          # 0.5 .. 4.5 days
                _wait(t, 30000)
                if not _live(t):
                    break
                r = t.bridge_call("jawa/inspect_string", thingIds=",".join(yid)) if yid else None
                rows = (r or {}).get("things") or []
                ref = t.bridge_call("jawa/inspect_string", defName="Meat_Human",
                                    rect="%d,%d,1,1" % (x + 2, z))
                samples.append({"day": half_day / 2.0,
                                "yieldOnMap": _count(t, "RM_FE_ScorchFruitYield"),
                                "near": [(w.get("id"), w.get("x"), w.get("z"), w.get("stackCount"))
                                         for w in _things(t, "RM_FE_ScorchFruitYield",
                                                          "%d,%d,5,5" % (x - 2, z - 2))],
                                "yield": [" ".join(w.get("inspect") or []) for w in rows],
                                "ref": [" ".join(w.get("inspect") or []) for w in ((ref or {}).get("things") or [])]})
                if half_day == 3:
                    plant_at_1_5 = _count(t, "RM_FE_Plant_ScorchFruit", "%d,%d,3,1" % (x - 3, z + 3))
            _note(t, "rot samples", samples)
            if _live(t):
                if not yid:
                    _fail("the spawned RM_FE_ScorchFruitYield stack was not found at %d,%d" % (x, z))
                last = samples[-1]["yield"] if samples else []
                rotted = (not last) or any("rot" in s.lower() or "spoiled" in s.lower() for s in last)
                if not rotted:
                    _fail("RM_FE_ScorchFruitYield neither rotted nor destroyed by day 4.5: %r" % last)
                gone_early = [s for s in samples if s["day"] < 3.0 and not s["yield"]]
                if gone_early:
                    _unmeasured(t, "the yield stack vanished at day %.1f, before it could rot "
                                   "(eaten or hauled?); rot unproven" % gone_early[0]["day"])
                if plant_at_1_5:
                    _fail("%d unharvested ScorchFruit plant(s) still standing at day 1.5" % plant_at_1_5)
            t.screenshot()
    finally:
        _restore(t)


# --------------------------------------------------------------------------- the fire cast

@suite.chain("firehawk")
def firehawk(t):
    _pad(t, PAD_HAWK)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    try:
        with _comp(t, "firehawk_carries_ember", shows=["pyre_firehawk_carries_ember"]):
            _set(t, {"burnLineEnabled": True, "fireHawkSpreadEnabled": True})
            _firebreak(t, rect)
            _soil(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            _fire(t, (x - 2, z - 2, 4, 4), size=0.5)
            hawk = _spawn_wild(t, "RUT_FireHawk", x + 8, z)
            seen = []
            for _ in range(100):          # every 60 ticks: a sortie is short and was missable at 300
                _wait(t, 60)
                j = _job_of(t, hawk)
                seen.append((j, _count(t, "Fire", _rs(rect))))
                if j == FIRE_HAWK_JOB:
                    break
            _note(t, "fire-hawk job samples", seen)
            if _live(t) and not any(s_[1] for s_ in seen):
                _unmeasured(t, "no fire was alive beside the hawk at any sample: %r" % seen)
            if _live(t) and FIRE_HAWK_JOB not in [s_[0] for s_ in seen]:
                _fail("no %s job in 100 samples over 6000 ticks beside a live fire (job state read only)"
                      % FIRE_HAWK_JOB)
            t.screenshot(rect=rect)
    finally:
        _extinguish(t)


@suite.chain("furnace_warmth")
def furnace_warmth(t):
    _pad(t, PAD_WARMTH)
    t.clear_area(size=12)
    x, z = t.anchor
    with _comp(t, "furnacebeast_warmth", shows=["pyre_furnacebeast_warmth"]):
        _set(t, {"furnaceThermalEnabled": True})
        bid = _spawn_wild(t, "RUT_FurnaceBeast", x, z)
        # CompFurnaceWarmthAura: radius = 4.9 x Lerp(0.35, 1, charge); a fresh beast's charge is
        # 0, so its aura reaches 1.7 cells. The colonist stands adjacent (x+1).
        col = t.spawn_pawn("Colonist", beyond=[(x - 2, z), (x - 2, z)])
        samples, near = [], None
        for _ in range(8 if _live(t) else 0):
            b = _pawn_row(t, bid) or {}
            if b.get("x") is not None:
                t.bridge_call("jawa/order_pawn", pawnId=col, x=b["x"] + 1, z=b["z"], waitTicks=60)
            _wait(t, 90)
            near = _pawn_row(t, col, health=True) or {}
            b = _pawn_row(t, bid) or {}
            d = None
            if b.get("x") is not None and near.get("x") is not None:
                d = ((b["x"] - near["x"]) ** 2 + (b["z"] - near["z"]) ** 2) ** 0.5
            samples.append({"dist": d, "warm": _has_hediff(near, "RM_FurnaceWarmth")})
            if samples[-1]["warm"]:
                break
        _note(t, "colonist-to-beast distance / warmth samples", samples)
        if _live(t):
            if not any(sm["warm"] for sm in samples):
                close = [sm for sm in samples if sm["dist"] is not None and sm["dist"] <= 1.7]
                if not close:
                    _unmeasured(t, "the colonist never got within the uncharged aura (1.7 cells) "
                                   "of the beast: %r" % samples)
                _fail("colonist within %.1f cells of the furnace-beast never gained RM_FurnaceWarmth"
                      % min(sm["dist"] for sm in close))
        t.bridge_call("jawa/order_pawn", pawnId=col, x=x + 25, z=z, waitTicks=900)
        _wait(t, 600)
        away = _pawn_row(t, col, health=True)
        if _live(t):
            _note(t, "after walking away", {"x": (away or {}).get("x"), "z": (away or {}).get("z")})
            if _has_hediff(away, "RM_FurnaceWarmth"):
                _fail("RM_FurnaceWarmth still present after the colonist walked 25 cells away")
        t.screenshot()


@suite.chain("furnace_room")
def furnace_room(t):
    """Two matched 7x7 rooms. The gating arm starts both at 10 C (below the pusher's 24 C cap,
    where the beast is designed to heat); the ambient arm at the site's own heat is recorded."""
    _pad(t, PAD_ROOMS)
    t.clear_area(size=TEST_SIZE)
    x, z = t.anchor
    a, b = (x - 9, z - 3, 7, 7), (x + 2, z - 3, 7, 7)
    ca, cb = (a[0] + 3, a[1] + 3), (b[0] + 3, b[1] + 3)
    with _comp(t, "furnacebeast_heats_room", shows=["pyre_furnacebeast_heats_room"]):
        _set(t, {"furnaceThermalEnabled": True})
        for r in (a, b):
            t.bridge_call("jawa/make_empty_room", rect=_rs(r))
        bid = _spawn_wild(t, "RUT_FurnaceBeast", ca[0], ca[1])
        _wait(t, 600)

        def tv(r):
            return (r or {}).get("temperature", (r or {}).get("temp"))
        rooms = [t.bridge_call("jawa/room_get", x=c[0], z=c[1]) for c in (ca, cb)]
        beast = _pawn_row(t, bid) or {}
        amb = [tv(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % c)) for c in (ca, cb)]
        for c in (ca, cb):
            t.bridge_call("jawa/room_heat", x=c[0], z=c[1], mode="set", value=10.0)
        series = []
        for _ in range(10):
            _wait(t, 250)
            series.append([tv(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % c))
                           for c in (ca, cb)])
        if _live(t):
            inside = (beast.get("x") is not None and a[0] < beast["x"] < a[0] + 6
                      and a[1] < beast["z"] < a[1] + 6)
            _note(t, "room temperatures", {"ambient": amb, "coldStartSeries": series,
                                           "beastAt": (beast.get("x"), beast.get("z")),
                                           "beastInsideRoomA": inside,
                                           "roomsFound": [(r or {}).get("roomsFound") for r in rooms]})
            if not all((r or {}).get("roomsFound") for r in rooms):
                _fail("make_empty_room did not produce two enclosed rooms: %r" % rooms)
            if not inside:
                _unmeasured(t, "spawn_pawn scattered the beast out of room A (at %r)"
                            % ((beast.get("x"), beast.get("z")),))
            cold = [sa - sb for sa, sb in series if None not in (sa, sb) and sb < 24.0]
            if not cold:
                _unmeasured(t, "the control room never sat below the pusher's 24 C cap: %r" % series)
            if sum(cold) / len(cold) <= 0.5:
                _fail("beast room is not warmer than the matched control while below 24 C: "
                      "mean delta %.2f C over %r" % (sum(cold) / len(cold), series))
        t.screenshot(rect=(a[0], a[1], 18, 7))


@suite.chain("burrowers")
def burrowers(t):
    _pad(t, PAD_BURROW)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    try:
        with _comp(t, "burrowers_dive", shows=["pyre_burrowers_dive"]):
            _set(t, {"burrowOnFireEnabled": True})
            _firebreak(t, rect)
            _soil(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            g = _spawn_wild(t, "RUT_Ashwallow", x + 5, z)
            _fire(t, (x - 3, z - 3, 6, 6))
            seen = False
            jobs = []
            for _ in range(15):
                _wait(t, 100)
                row = _pawn_row(t, g, health=True)
                jobs.append(_job_of(t, g))
                if _has_hediff(row, "RM_Burrowed"):
                    seen = True
                    break
            _note(t, "burrower job samples", jobs)
            if _live(t) and not seen:
                _fail("burrow-on-fire grazer never showed RM_Burrowed over 1500 ticks beside a fire")
            _wait(t, 2500)
            _extinguish(t)
            after = _pawn_row(t, g, health=True)
            if _live(t):
                _note(t, "grazer after the fire", after)
                if not after or after.get("dead") or after.get("downed"):
                    _fail("grazer did not come through the fire intact: %r" % after)
            t.screenshot(rect=rect)
    finally:
        _extinguish(t)


# --------------------------------------------------------------------------- long waits last

@suite.chain("embergrass_regrow")
def embergrass_regrow(t):
    """Fixed 20x20 cohort, pre-cleared to RM_FE_Ground_Soil, grassed, burned, then 7 days.
    Counts only plants spawned AFTER the burn (ThingID not in the pre-burn set)."""
    _pad(t, PAD_REGROW)
    t.clear_area(size=TEST_SIZE)
    regrow = _rect(t, 20)
    inner = _rs((regrow[0] + 2, regrow[1] + 2, 16, 16))   # minus the 2-cell edge band
    try:
        with _comp(t, "embergrass_regrows", shows=["pyre_embergrass_regrows"]):
            _isolate(t)
            _firebreak(t, regrow)
            t.bridge_call("jawa/set_terrain", x=regrow[0], z=regrow[1], terrainDef=SOIL, width=20,
                          height=20, layer="top")
            _plants(t, "RM_FE_Plant_EmberGrass", regrow)
            pre_ids = set(p.get("id") for p in _things(t, "RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass",
                                                       inner, limit=2000))
            _fire(t, regrow)
            _wait(t, 3000)
            _extinguish(t)

            def new_count():
                return len([p for p in _things(t, "RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass",
                                               inner, limit=2000) if p.get("id") not in pre_ids])
            d0 = new_count()
            _wait(t, 3 * 60000)
            d3 = new_count()
            _wait(t, 4 * 60000)
            d7 = new_count()
            temp = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % t.anchor)
            pre = len(pre_ids)
            _note(t, "CALIBRATING regrow (>=25%% by day 3, >=60%% by day 7)",
                  {"pre": pre, "afterBurn": d0, "day3": d3, "day7": d7,
                   "day3Frac": (float(d3) / pre) if pre else None,
                   "day7Frac": (float(d7) / pre) if pre else None, "temp": temp})
            if _live(t):
                if pre <= 0:
                    _fail("regrow cohort had no pre-burn plants")
                # Plan bar 5: >=25% by day 3 / >=60% by day 7 is CALIBRATING (never gates until
                # the owner rules it), so the state half cannot decide this bar either way.
                _unmeasured(t, "CALIBRATING, unruled: new roster plants in the burned 16x16 cohort "
                               "pre=%d afterBurn=%d day3=%d day7=%d (plan targets 25%%/60%%)"
                            % (pre, d0, d3, d7))
            t.screenshot(rect=regrow)
    finally:
        _extinguish(t)
        _restore(t)


@suite.chain("fulgurite")
def fulgurite(t):
    """No tool forces one strike: lock DryThunderstorm and count fulgurite from before to after.
    Lightning lights fires, so this runs last and the map is extinguished after."""
    _pad(t, PAD_PROBE)
    try:
        with _comp(t, "fulgurite_after_lightning", shows=["pyre_fulgurite_after_lightning"]):
            _set(t, {"fulguriteEnabled": True})
            before = _count(t, "RM_FE_Fulgurite")
            terr = _terrain(t, _whole(t))
            sand = sum(v for k, v in terr.items()
                       if k in ("RM_FE_Ground_Sand", "Sand", "SoftSand", "RM_DeepSand"))
            sand_frac = float(sand) / max(1, sum(terr.values()))
            _note(t, "sand-family cells (fulgurite needs sand)", {"cells": sand, "frac": sand_frac})
            t.bridge_call("jawa/weather_set", weather="DryThunderstorm", lockWeather=True)
            # Lightning lights the grass: extinguish every 1,000 ticks so a strike cannot grow into
            # a map-wide burn (run 4 burned the whole site to deep ash this way).
            fires = 0
            for _ in range(20):
                _wait(t, 1000, fast=True)
                fires += _count(t, "Fire")
                _extinguish(t)
            after = _count(t, "RM_FE_Fulgurite")
            _note(t, "fulgurite across 20000 ticks of DryThunderstorm",
                  {"before": before, "after": after, "firesBurning": fires})
            # Strikes land on random cells and no tool forces one onto sand; each fire found is
            # at most one strike, so this is the expected fulgurite count at fulguriteChance 0.35.
            expect = fires * sand_frac * 0.35 if _live(t) else 0
            if _live(t) and after - before < 1 and expect < 1:
                _unmeasured(t, "expected %.2f fulgurite (%d fires found x %.4f sand fraction x 0.35): "
                               "too few strikes can reach sand to test the bar" % (expect, fires, sand_frac))
            if _live(t) and after - before < 1:
                _fail("no new RM_FE_Fulgurite after 20000 ticks of locked DryThunderstorm "
                      "(%d -> %d; %d fires found across the 20 checks, i.e. strikes landed)" % (before, after, fires))
            t.screenshot()
    finally:
        t.bridge_call("jawa/weather_set", unlock=True)
        _extinguish(t)
