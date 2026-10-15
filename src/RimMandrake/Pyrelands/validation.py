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

Predicates read IMMUTABLE manifests (plan 1.3 / 2.3a): 3 plants and 16 animal kinds. A live
def that differs from the manifest is its own failure, so a patch cannot make an intruder
"allowed". Thresholds marked CALIBRATING (the plan's scale mark) are recorded as evidence and
never gate until the owner rules them.

Every bridge call here uses only the parameters the live tool declares (the bridge refuses an
undeclared one). Result shapes MEASURED live 2026-10-01: `jawa/list_things` reports
`countMatched` and a whole-result `perDef` table even when `limit` truncates the rows;
`jawa/list_pawns` rows carry `faction` (null for wild) and `intelligence`; `jawa/get_def`
puts `terrainPatchMakers` under `extra`; `jawa/get_defs` reads `wildPlants` and
`baseWeatherCommonalities` but CANNOT serialise `wildAnimals` (a non-public List), so the
animal manifest is read through `jawa/biome_probe` (the resolved roster). A component that cannot measure
calls `_unmeasured()`, which records UNMEASURED with its reason; it never passes.

Fire hygiene: every fire burns on its own pad, ringed by `RM_FE_FirebreakLine`. Pads sit away
from the colonists at the map centre.

Teardown (`@_teardown`): settings fields are `public static`
(RimMandrake.Pyrelands.RM_PyrelandsSettings), flipped through `_set`, which remembers each
field's prior value. Every stateful chain ends by unlocking the weather (and moving it to Clear twice, so no storm
tail ticks on), extinguishing the whole map and restoring those values through the session itself, because t.bridge_call is a no-op once a
component has failed or gone UNMEASURED. A teardown step that does not take is its own FAIL
component (`teardown`), so leaked state can never sit under an all-PASS run.

Not expressible with current bridge tools: forcing one `WeatherEvent_LightningStrike`
(fulgurite_after_lightning locks DryThunderstorm and counts fulgurite), reading
`MapComponent_BurnLine` directly (burn_line_present counts free-standing Fire, which is exactly
what that component measures), and flyer flight (firehawk_carries_ember reads job state only;
flyers are never live-tested unattended).
"""
import contextlib
import functools
import importlib.util
import json
import os
import sys
import time

from modcheck import Suite, Component, ExpectationFailed

suite = Suite("Pyrelands")
suite.toggles = ["fulguriteEnabled", "ashDustingEnabled", "scorchFruitEnabled",
                 "ashfallAccumulationEnabled", "biomeGenerationEnabled",
                 "ullaiEnabled", "ullaiHerdSizeMultiplier", "furnaceBeastGiant",
                 "lightningBreakerEnabled", "breakerPyrelandsOnly", "breakerTripCost", "breakerRecipeCostFactor",
                 "sandShovelEnabled", "sandShovelYieldMultiplier"]

SETTINGS = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
SOIL = "RM_FE_Ground_Soil"
FIREBREAK = "RM_FE_FirebreakLine"
TEST_SIZE = 24

# Immutable manifests (plan 1.3). 3 plants; 16 animal kinds (RM_Ullai added by PYRELANDS_ULLAI_GIANT_BUILD_1;
# PYRELANDS_NORTHSTAR_TRIAL_1 re-measures against it).
PLANT_MANIFEST = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass",
                            "RM_FE_Plant_ScorchFruit"])
WILD_PLANTS = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass"])  # ScorchFruit is fire-born
ANIMAL_MANIFEST = frozenset([
    "RM_FireHawk", "RM_FurnaceBeast",
    "RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka",
    "RM_Emberscythe", "RM_Sytheclaw", "RM_Barbslinger", "RM_FireWasp", "RM_Flamefang",
    "RM_Ashwallow", "RM_Ullai"])
DEEP_ASH = "RM_FE_Ash_Deep"   # the ash field (AshField.xml): the biome's ordinary ground
LEGACY_ASH = ("RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy")   # retired rungs: hidden aliases, re-laid on load
ASH_FIELD = "RimMandrake.Pyrelands.MapComponent_PyrelandsAshField"     # jawa/static_call probes (PyrelandsAshField.cs)
STOCK_GROUND = ("Sand", "Soil", "Gravel", "SoilRich")
ORDINARY_RAIN = ("Rain", "RainyThunderstorm", "FoggyRain")
# Mechanics that must be OFF during the controlled bars (plan 2.3a isolation).
ISOLATION_OFF = ["burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled",
                 "furnaceWorldMigrationEnabled", "burrowOnFireEnabled",
                 "furnaceThermalEnabled", "fulguriteEnabled"]
FIRE_HAWK_JOB = "RM_FireHawkCarryEmber"   # JobDefs/RM_PyrelandsJobs.xml (renamed from RUT_)

# Pads (map is 250x250, colonists stand at the centre). Each fire gets its own pad.
PAD_FIRE_TICK = (60, 60)
PAD_ASH = (60, 190)       # ash_fertility_watered (was the retired ash-ladder pad)
PAD_BURN = (125, 30)      # fresh_burn_bonus
PAD_REGROW = (190, 190)
PAD_FIRE_BORN = (190, 60)
PAD_HARVEST = (125, 95)
PAD_SPOIL = (125, 165)
PAD_HAWK = (60, 125)
PAD_BURROW = (190, 125)
PAD_WARMTH = (95, 160)
PAD_ROOMS = (160, 90)
PAD_PROBE = (225, 225)
PAD_HERD_OLD = (30, 100)   # herd_follows_two_day_old_burn: burn A, backdated two days
PAD_HERD_NEW = (220, 100)  # burn B, fresh: present in the history and NOT the anchor
HERD_SPAWN = (125, 215)    # the wild ullai herd starts ~150 cells from A and ~140 from B
HERD_SIZE = 10
HERD_RACE = "RM_Ullai"
HERD_LAG_TICKS = 2 * 60000      # RM_FollowBurnExtension.lagDays 2 (Defs/ThingDefs_Races/RM_Ullai.xml)
HERD_HISTORY_INTERVAL = 2500    # MapComponent_BurnLine.BurnHistoryIntervalTicks
HERD_STEP_TICKS = 2500          # the one short step the herd walks (Walk urgency covers ~100 cells in it)
HERD_MIN_CLOSE = 0.3            # share of its start distance to A the herd centroid must close in that step
HERD_ANCHOR_TOL = 8             # cells: the recorded centroid of an 8x8 burn sits inside it
BURN_LINE = "RimMandrake.Pyrelands.MapComponent_BurnLine"
FOLLOW_BURN = "RimMandrake.Pyrelands.RM_JobGiver_FollowBurn"
BURN_QUIET_TICKS = 120000      # PyrelandsTuning.StandingBurnQuietTicks (selftest_pyrelands_site pins both to the C#)
BURN_WATCH_TICKS = 60          # PyrelandsTuning.BurnWatchIntervalTicks
BURN_LINE_WAIT_TICKS = BURN_QUIET_TICKS + 6 * BURN_WATCH_TICKS   # quiet window + a few watch intervals
REGROW_OVERRIDE_DAYS = 0.1
REGROW_SHORT_STEP = 1500   # two steps of this, through safe_advance
REGROW_BURN_TICKS = 5000   # kill the grass (~3500-4500 ticks)
FIRE_PADS = (PAD_FIRE_TICK, PAD_ASH, PAD_REGROW, PAD_FIRE_BORN, PAD_HAWK, PAD_BURROW, PAD_BURN, PAD_HERD_OLD, PAD_HERD_NEW)
DEEP_ASH_MIN = 0.85        # pyre_ground_deep_ash: deep ash share of open land on a fresh map (PROVISIONAL, design §2)
WATERED_MIN_GAIN = 0.5     # pyre_ash_fertile_when_watered: watered minus dry FertilityAt (shipped 1.40 vs 0.40)
BURN_BONUS_MIN = 0.3       # pyre_fresh_burn_feeds_the_field: bonus right after a burn (shipped +0.50)
RUIN_SAMPLES = 10
RUIN_ASH_MIN = 0.9    # the sweep lays deep ash on every non-water footprint+rim cell (the 3x3 sample sits inside the rim)
RUIN_FILTH_MIN = 0.3  # share of sampled ruins carrying loose-ash filth in their 3x3 (the visible scorch; 70% per footprint cell)
# BuildingArtificial things that are natural scenery, not ruins (modcheck.bland_world.NATURAL_SCENERY).
RUIN_NOT_A_RUIN = ("SteamGeyser", "VHGE_GasGeyser")

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


# ---- colony vitals (PYRE_SITE_FOOD_REPAIR_COLONY_STARVES; owner 2026-10-13: damage to the test -> RESTART, never FAIL)
FOOD_TOPUP_BELOW = 0.5            # a row starts with Food at or above this (topped to 1.0 otherwise)
STARVING_FOOD = 0.02              # at/below this after a row the colonists are starving: the row ran on a dying colony
NEEDS_ROWS = ("scorchfruit_produces",)   # rows that MEASURE a colonist's Food need: never topped up


def vitals_damage(before, after):
    """Pure. before/after: {pawn id: {"dead": bool, "downed": bool, "food": float|None}}. -> [reason, ...]; empty = intact.
    Damage to the test itself (a colonist that was alive and is dead, newly downed, or starving) means the row's evidence
    is void: it is RESTARTED, not scored."""
    why = []
    for pid, b in sorted(before.items()):
        if b.get("dead"):
            continue
        a = after.get(pid)
        if a is None or a.get("dead"):
            why.append("%s died during the row" % pid)
            continue
        if a.get("downed") and not b.get("downed"):
            why.append("%s was downed during the row" % pid)
        f = a.get("food")
        if f is not None and f <= STARVING_FOOD:
            why.append("%s is starving (Food %.3f)" % (pid, f))
    return why


def _vitals(t, force=False):
    """{pawn id: row} for every player pawn, or None offline. A pawn whose Food cannot be read gets food=None.
    force=True reads even after the component failed (t.upstream_failed): the AFTER read must still happen, else a FAIL
    row crashed the whole run on None (pass 8, 2026-10-13, animal_distribution_correct)."""
    if t.session is None or (t.upstream_failed and not force):
        return None
    r = t.session.call("jawa/list_pawns", faction="player", limit=100) or {}
    out = {}
    for p in r.get("pawns") or []:
        if not p.get("id"):
            continue
        row = {"dead": bool(p.get("dead")), "downed": bool(p.get("downed")), "food": None}
        if not row["dead"]:
            for n in (t.session.call("jawa/pawn_need", pawn=p["id"], action="list") or {}).get("needs") or []:
                if n.get("need") == "Food":
                    row["food"] = n.get("level")
        out[p["id"]] = row
    return out


def _offsite(t):
    """Colonists in the game minus colonists on the current (site) map: rimworld/list_colonists, all maps vs current.
    Pass 8 had 3 of 6 on a leftover quicktest map, dying there while the suite read the site alone. None = unread."""
    try:
        rows = [t.session.call("rimworld/list_colonists", currentMapOnly=c) or {} for c in (False, True)]
        n = [len(r.get("colonists", []) if isinstance(r, dict) else r or []) for r in rows]
        return n[0] - n[1]
    except Exception:                                    # noqa: BLE001 - a note, never a crash
        return None


# ---- heat guard (TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3). r5 2026-10-15: on a 56.7 C fresh site vanilla Heatstroke reached
# 0.65 and downed every colonist inside scorchfruit_spoils_fast (a fruit-rot row: 4.5 days of half-day waits), twice. The
# site is the subject and is never cooled; the guard takes vanilla Heatstroke off the support colonists at row start and
# every testenv_guards.HEAT_CHUNK_TICKS of waiting, so none carries more than one chunk of exposure (< moderate at 65 C,
# selftest_testenv_guards). Rows that read a colonist's needs or felt temperature are exempt (owner 2026-10-13 by card:
# support colonists are protected only in rows not about health/needs/damage/death).
HEAT_GUARD_EXEMPT = NEEDS_ROWS + ("furnacebeast_warmth",)


def _heat_guarded(t):
    """True while a live, unfailed component that may be guarded is running (the offline probe never guards)."""
    row = _GEN.get("row")
    return bool(row) and row not in HEAT_GUARD_EXEMPT and t.session is not None and not t.upstream_failed


def _heat_guard(t, why):
    """One guard pass: clear Heatstroke on player colonists, record what was taken off (BEFORE the repair, by severity)."""
    import testenv_guards  # noqa: E402 - on sys.path via the modcheck package
    r = testenv_guards.clear_heatstroke(t.session)
    _GEN["heat_ticks"] = 0
    if r["cleared"] or r["failed"]:
        _note(t, "heat guard (%s, row %s)" % (why, _GEN.get("row")), r)
        _GEN.setdefault("heat_guard", []).append({"row": _GEN.get("row"), "why": why, "cleared": r["cleared"],
                                                  "failed": r["failed"]})
    return r


def _top_up(t, vitals):
    for pid, row in vitals.items():
        if not row["dead"] and row["food"] is not None and row["food"] < FOOD_TOPUP_BELOW:
            t.session.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
            row["food"] = 1.0


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail
    names the real reason, and the chain is not poisoned for an independent next component."""
    before = t.upstream_failed
    t._why = None
    _on_site(t)
    pre = _vitals(t)
    if pre is not None and name not in NEEDS_ROWS:
        _top_up(t, pre)
    _GEN["row"] = name
    if _heat_guarded(t):
        _heat_guard(t, "row start")
    try:
        with t.component(name, **kw) as tt:
            yield tt
    finally:
        _GEN["row"] = None
    restarted = False
    if pre is not None:
        post = _vitals(t, force=True) or {}
        damage = vitals_damage(pre, post)
        off = _offsite(t)
        if off:     # PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY: colonists the current-map reads cannot see are unwatched
            damage = damage + ["%d colonist(s) live OFF the site map, unfed and unwatched (retire_offsite_colonies)" % off]
        _note(t, "colony vitals after %s" % name, {"colonists": len(post), "offsite": off, "damage": damage})
        if damage and not before:
            c = t.components[-1]
            c.verdict = "UNMEASURED"
            c.detail = "UNMEASURED: RESTART (damage to the test, not a verdict): " + "; ".join(damage)
            _GEN.setdefault("restart", []).append(name)
            # a dead colonist ends the chain (reload the fixture); anything else leaves the next row free to run
            t.upstream_failed = any("died" in d for d in damage)
            restarted = True
    why = getattr(t, "_why", None)
    if why and not before and not restarted:
        t.components[-1].detail = "UNMEASURED: %s" % why
        t.upstream_failed = False
    t._why = None
    if t.session is not None:   # progress line (the driver prints only at the very end)
        c = t.components[-1]
        print("[pyre] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _governed(t):
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    return clockgate.has_safe_advance(t.session)


def _wait(t, n, fast=None):
    """Advance `n` real ticks; inside a heat-guarded row, in steps of at most HEAT_CHUNK_TICKS of exposure with a
    Heatstroke guard pass between them (TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3). Returns what the last step returned."""
    if not _heat_guarded(t):
        return _wait_raw(t, n, fast)
    import testenv_guards  # noqa: E402 - on sys.path via the modcheck package
    r = None
    for step, guard in testenv_guards.heat_steps(n, _GEN.get("heat_ticks", 0)):
        if step:
            r = _wait_raw(t, step, fast)
            _GEN["heat_ticks"] = _GEN.get("heat_ticks", 0) + step
        if guard and _heat_guarded(t):
            _heat_guard(t, "every %d ticks" % testenv_guards.HEAT_CHUNK_TICKS)
    return r


def _wait_raw(t, n, fast=None):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact, one tick per frame: MEASURED
    ~53 ticks/s, so 7 days would take ~2.2 h). Long waits run the game at Ultrafast and poll the
    real clock, then pause; the overshoot is recorded. Raises on a stalled clock."""
    if t.session is None or t.upstream_failed or getattr(t, "watch", None) is not None or (n <= 5000 and not fast) \
            or _governed(t):
        # WATCH_WAIT_WIRE_SMALL_STEPS: with jawa/safe_advance live, EVERY wait is governed chunks (t.wait_ticks ->
        # clockgate.advance_chunk), stopped by the vitals latch; the unwatched Ultrafast path below is the fallback
        # for a companion without it.
        r = t.wait_ticks(n)
        # Re-assert the site AFTER the ticks too: every read that follows a wait is a current-map read, and a
        # hop during the wait (naming dialog, MEASURED 2026-10-11) sent ash/yield/pawn/room reads to the
        # quicktest colony map (room ambient 17.5 C on a 50 C site; 0 ash after 2600 ticks of fire).
        if t.session is not None and not t.upstream_failed:
            _on_site(t)
        return r
    _on_site(t)
    s = t.session
    start = s._ticks()
    if start is None:
        raise ExpectationFailed("clock unreadable before a %d-tick wait" % n)
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


def _name_colony_once(t):
    """jawa/name_colony once per run (== the naming dialogs' OK). An unnamed colony raises
    Dialog_NamePlayerFactionAndSettlement at every TicksGame % 1000 == 200; it force-pauses the clock
    and hops the current map. MEASURED 2026-10-11 ratchet pilot: four "clock stalled at NNN200"
    FAILs and five wrong-map reads, all from this one dialog. Housekeeping, never a verdict."""
    if _GEN.get("named"):
        return
    try:
        r = t.session.call("jawa/name_colony", factionName="Northstar Pyrelands",
                           settlementName="Northstar Pyrelands") or {}
        tiles = [x.get("tile") for x in r.get("settlements") or []] if r.get("success") else None
    except Exception as ex:
        r, tiles = "name_colony raised %s" % type(ex).__name__, None
    _GEN["named"] = tiles          # falsy on failure: the next _on_site tries again
    t._record("name_colony (naming dialog can never be raised)", tiles or str(r)[:200])


def _on_site(t):
    """Keep the Pyrelands site the CURRENT map. Live 2026-10-01: the settlement-naming dialog
    opens once time runs, and it (or closing it) hops Find.CurrentMap back to the colony map,
    after which every current-map tool silently reads the wrong map. _name_colony_once removes
    the cause; this stays as the check."""
    if t.session is None:
        return
    _name_colony_once(t)
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


def _ids_on_map(t, defName):
    """Set of ThingIDs of `defName` anywhere on the map; refuses a truncated listing, so a missing id
    really means the thing is gone."""
    r = t.bridge_call("jawa/list_things", defName=defName, limit=2000)
    if not _live(t):
        return set()
    rows = _ok(r, "list_things(%s)" % defName).get("things")
    if not isinstance(rows, list) or r.get("countMatched") != len(rows):
        _fail("list_things(%s) incomplete: countMatched %r" % (defName, r.get("countMatched")))
    return set(w.get("id") for w in rows)


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
    """Refuse a census on a site that is not a fresh map. Deep ash is now the biome's ordinary ground, so it no longer
    says where fire went; the ash field's per-cell burn stamp does (MapComponent_PyrelandsAshField.CountBurnedOutside:
    cells burned since generation, outside this suite's own fire pads). Live 2026-10-01: run 4's lightning chain burned
    the whole site."""
    if not _live(t):
        return
    if "fresh" not in _GEN:
        pads = ";".join("%d,%d" % p for p in FIRE_PADS)
        r = t.bridge_call("jawa/static_call", type=ASH_FIELD, method="CountBurnedOutside", args="%s|18" % pads)
        try:
            n = int(str((r or {}).get("result")).strip())
        except ValueError:
            n = None
        if not isinstance(r, dict) or r.get("success") is False or n is None or n < 0:
            # an unread map is not a fresh map: nothing is cached, so the next census asks again
            _unmeasured(t, "burn-stamp read failed, so whether the site is fresh is unknown: %s" % str(r)[:200])
        _GEN["fresh"] = n
        _note(t, "burned cells outside the suite's fire pads", n)
    if _GEN["fresh"] > 100:
        _unmeasured(t, "site is not a fresh map: %d cells burned outside the suite's fire pads; a fresh-map census "
                       "is not measurable here -- reload the site" % _GEN["fresh"])


def _probe(t, x, z):
    """FertilityAt at (x, z) through the ash-field postfix, and its parts -> dict, {} offline."""
    r = t.bridge_call("jawa/static_call", type=ASH_FIELD, method="ProbeCell", args="%d,%d" % (x, z))
    if not _live(t):
        return {}
    _ok(r, "ProbeCell(%d,%d)" % (x, z))
    out = {}
    for kv in str(r.get("result") or "").split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v
    if "fertility" not in out:
        _fail("ProbeCell(%d,%d) returned no fertility: %r" % (x, z, r))
    for k in ("fertility", "bonus", "rainAcc"):
        out[k] = float(out.get(k, "nan"))
    out["watered"] = out.get("watered") == "True"
    return out


def ash_census(gen):
    """A whole-map {terrain: cells} -> (deep_share_of_open_land, open_land, detail). Open land = not water, not the
    rough/smooth stone under rock."""
    water = sum(n for d, n in gen.items() if "Water" in d)
    rock = sum(n for d, n in gen.items() if d.endswith("_Rough") or d.endswith("_RoughHewn") or d.endswith("_Smooth"))
    land = sum(gen.values()) - water - rock
    deep = gen.get(DEEP_ASH, 0)
    return (float(deep) / land if land > 0 else None), land, {"deep": deep, "water": water, "rock": rock}


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
    """Plant `rect` and keep the reply: a fire that later refuses every cell is then told apart from a pad that
    never took its grass (2026-10-12 ash-ladder chain, since retired: map_fire refused all 400 cells, set_plants unread)."""
    r = t.bridge_call("jawa/set_plants", ops="%s:%s" % (plant, _rs(rect)), growth=growth)
    _GEN["last_plants"] = {"rect": _rs(rect), "plant": plant,
                           "reply": dict((k, (r or {}).get(k)) for k in ("planted", "rejected", "rejectionReasons",
                                                                         "cellsSkippedByDensity", "message"))}
    return r


def probe_plant(live_keys):
    """The sanity-probe species: the first (sorted) plant of the biome's live wildPlants that is also in the shipped
    allowlist -- terrain the biome itself grows. Never an ordinary vanilla grass. None when there is none."""
    ok = sorted(k for k in (live_keys or ()) if k in WILD_PLANTS)
    return ok[0] if ok else None


def probe_host(probe, census):
    """The roster plant whose standing cell hosts the sanity probe: a DIFFERENT allowlisted def that the census holds.
    2026-10-12c: the fixed pad (225,225) was bare unplantable ground (set_plants rejected EmberGrass there), and a cell
    already holding the probe's own def is replaced 1-for-1 (planted 1, cleared 1) so the census delta reads 0. A cell
    the biome itself grew on is plantable by construction, and replacing another def makes the probe's count rise by 1."""
    hosts = sorted(k for k, n in (census or {}).items() if k != probe and k in WILD_PLANTS and n > 0)
    return hosts[0] if hosts else None


def burn_cleared(pre, after_fire, min_cleared=0.5):
    """(cleared, text) for the regrow row's precondition: did the fire kill the patch? `pre` plants stood before the
    fire, `after_fire` of them (the SAME ThingIDs) still stand after it. 2026-10-12 the patch was 256/256 grassed at day 7
    while the row read 0 new plants: fire left the originals alive and the row could not tell. Cleared means at
    most (1 - min_cleared) of the originals survive; min_cleared is a harness precondition, not a calibration bar."""
    if pre <= 0:
        return False, "no pre-burn plants"
    left = float(after_fire) / pre
    return left <= 1.0 - min_cleared, "%d of %d pre-burn plants still standing after the burn (%.0f%%)" % (
        after_fire, pre, 100 * left)


def _firebreak(t, rect, width=4):
    """Ring `rect` with the biome's own non-flammable firebreak terrain and strip its plants."""
    x, z, w, h = rect
    ring = [(x - width, z - width, w + 2 * width, width), (x - width, z + h, w + 2 * width, width),
            (x - width, z, width, h), (x + w, z, width, h)]
    t.bridge_call("jawa/set_terrain_batch", ops=";".join("%s:%s" % (FIREBREAK, _rs(r)) for r in ring),
                  layer="top")
    t.bridge_call("jawa/set_plants", ops=";".join("CLEAR:%s" % _rs(r) for r in ring))


def _soil(t, rect):
    """Re-lay the cohort as RM_FE_Ground_Soil (an unburned pocket), so a pad an earlier run burned starts the same."""
    t.bridge_call("jawa/set_terrain", x=rect[0], z=rect[1], terrainDef=SOIL, width=rect[2],
                  height=rect[3], layer="top")


def _extinguish(t):
    t.bridge_call("jawa/map_fire", action="extinguish", rect=_whole(t))


def _fire(t, rect, size=1.2):
    r = t.bridge_call("jawa/map_fire", action="start", rect=_rs(rect), fireSize=size)
    rec = ignition_record(_rs(rect), r, _GEN.get("last_plants"))
    _GEN.setdefault("ignitions", []).append(rec)
    if _live(t) and not (r or {}).get("firesStarted"):
        _fail(fire_refusal(_rs(rect), r, _GEN.get("last_plants"), _fuel_census(t, rect),
                           history=_GEN.get("ignitions")))
    return r


def ignition_record(rect, reply, last_plants):
    """One ignition attempt: rect, what map_fire said, and the planting that fed this rect. Kept per attempt so a
    mid-run refusal (2026-10-12 ash-ladder chain, 400/400 refused) explains itself from the attempts before it."""
    lp = last_plants if (last_plants or {}).get("rect") == rect else None
    rp = dict((k, (reply or {}).get(k)) for k in ("firesStarted", "success", "message", "error") if k in (reply or {}))
    return {"rect": rect, "fire": rp or reply, "planting": lp["reply"] if lp else None}


def _fuel_census(t, rect):
    """What sits in `rect` when an ignition is refused: plants, filth and buildings by def (whole-rect perDef)."""
    out = {}
    for group in ("Plant", "Filth", "BuildingArtificial", "BuildingFrame"):
        try:
            g = t.session.call("jawa/list_things", group=group, rect=_rs(rect), limit=1) or {}
            out[group] = g.get("perDef") if g.get("success") is not False else "refused: %s" % str(g)[:120]
        except Exception as ex:   # noqa: BLE001 - diagnostics only, never the verdict
            out[group] = "raised %s" % type(ex).__name__
    return out


def fire_refusal(rect, reply, last_plants, fuel, history=None):
    """The FAIL text for a refused ignition: RimWorld's ChanceToStartFireIn needs fuel (a FlammableNow plant or
    flammable terrain), no Fire already there, no impassable edifice and no filth with allowsFire=false. Says which
    planting fed this rect and what the rect held, so the next reader can tell HARNESS (no grass) from MOD.
    `history` (the per-attempt ignition records so far) is appended whole, so a refusal on cycle 2 shows cycle 1."""
    lp = last_plants if (last_plants or {}).get("rect") == rect else None
    txt = ("map_fire started no fire in %s: %r | planting of this rect: %s | rect holds: %s"
           % (rect, reply, lp["reply"] if lp else "none recorded for this rect", fuel))
    if history:
        txt += " | ignition attempts so far (%d): %s" % (len(history), json.dumps(history, default=str))
    return txt


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


_PRIOR = {}   # setting field -> the value it held before this script first touched it (this run)


def _set(t, values):
    """Flip settings, remembering each field's PRIOR value the first time it is touched so
    _restore can put it back (never assume the prior value was True)."""
    if _live(t):
        for f in values:
            if f not in _PRIOR:
                r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f)
                if not (r or {}).get("success") or (r or {}).get("value") is None:
                    raise ExpectationFailed("cannot read the prior value of %s, so it could not be restored: %r"
                                            % (f, r))
                _PRIOR[f] = r["value"]
    t.set_setting(SETTINGS, values)


def _isolate(t):
    """Switch the plan 2.3a isolation set OFF; the caller restores via _restore."""
    _set(t, dict((f, False) for f in ISOLATION_OFF))


def _restore(t):
    """Put every setting this script flipped back to its prior value. Returns the fields that did not
    restore, as [(field, reply)]. Talks to the session directly, so it still runs after upstream_failed."""
    bad = []
    for f, v in list(_PRIOR.items()):
        try:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
            if (r or {}).get("success"):
                del _PRIOR[f]
                continue
            bad.append((f, r))
        except Exception as e:   # noqa: BLE001 - keep restoring the rest
            bad.append((f, repr(e)))
    # _PRIOR keeps the failed fields: clearing it would make the leaked value the next "prior"
    return bad


def _session_call(t, tool, **kw):
    """A teardown call made on the session itself. t.bridge_call is a no-op once a component has failed
    (TestContext._guard), which is exactly when a fire or a locked weather most needs clearing."""
    r = t.session.call(tool, **kw)
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("%s refused: %r" % (tool, r))
    return r


def _tear_down(t, fire, weather):
    """Unlock (and end) the weather, put out every fire, restore every flipped setting -- whatever the chain's
    verdicts. Anything that does not come back is a FAIL component of its own, so a leak into later
    chains can never sit under an all-PASS run."""
    if t.session is None:
        _PRIOR.clear()
        return
    bad = []
    if weather:
        try:
            _session_call(t, "jawa/weather_set", unlock=True)
            # TESTENV_STORM_FIRES_HARDEN_DECOY_BURN (r6 p4): an unlock leaves the locked weather CURRENT, and one transition
            # keeps lastWeather (lightning included) ticking for WeatherManager.TransitionTicks; the fulgurite storm then lit
            # 177 fires that the next chain's burn line read as its burn. Two transitions to Clear end the storm outright.
            for _ in range(2):
                _session_call(t, "jawa/weather_set", weather="Clear")
        except Exception as e:   # noqa: BLE001 - recorded below as a FAIL
            bad.append("weather unlock: %s" % e)
    if fire:
        try:
            mi = _session_call(t, "jawa/map_info")
            _session_call(t, "jawa/map_fire", action="extinguish",
                          rect="0,0,%d,%d" % (mi.get("sizeX", 250), mi.get("sizeZ", 250)))
        except Exception as e:   # noqa: BLE001 - recorded below as a FAIL
            bad.append("extinguish: %s" % e)
    bad.extend("setting %s not restored: %r" % fb for fb in _restore(t))
    bad.extend(_GEN.pop("teardown_bad", []))     # restores a chain ran inside its own component (_restore_terrain)
    if bad:
        c = Component("teardown", None, False)
        c.verdict = "FAIL"
        c.detail = "teardown left state behind for later chains: %s" % "; ".join(str(b) for b in bad)[:600]
        t.components.append(c)
        t._on_finding(c)
        print("[pyre] %s" % c.detail, file=sys.stderr, flush=True)


def _teardown(fire=False, weather=False):
    """Chain decorator: the chain's fires, weather lock and settings are cleared even after a FAIL or an
    UNMEASURED (which turn every t.bridge_call in the chain into a no-op)."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(t):
            try:
                return fn(t)
            finally:
                _tear_down(t, fire, weather)
        return wrapper
    return deco


def _independent(t):
    """Start a component that reads its own state, so an earlier component's FAIL or UNMEASURED does
    not turn it UNMEASURED. The environment still ends the chain: a surprise abort, or a map the runner
    could not make bland (it sets upstream_failed before the chain starts)."""
    last = t.components[-1] if t.components else None
    bland = t.watch is None or getattr(t.watch, "bland", True)
    if last is not None and last.surprises is None and bland:
        t.upstream_failed = False
        t.upstream_reason = "upstream failed -- this chain's state is meaningless"


SAND_FAMILY = ("RM_FE_Ground_Sand", "Sand", "SoftSand", "RM_DeepSand")   # FireEcologyHook.SandTerrainDefNames


def biome_probe_animals(r, biome):
    """jawa/biome_probe reply -> ({animal defName: commonality}, None), or (None, why) when the read cannot be
    trusted: refused, biome missing, or a listed set smaller than the resolved count (a capped list must never
    read as a short roster)."""
    if not isinstance(r, dict) or r.get("success") is False:
        return None, "biome_probe refused: %s" % str(r)[:200]
    rows = [b for b in (r.get("biomes") or []) if b.get("defName") == biome]
    if len(rows) != 1:
        return None, "biome_probe returned %d rows for %s" % (len(rows), biome)
    b = rows[0]
    animals = b.get("animals")
    if not isinstance(animals, list):
        return None, "biome_probe row has no animals list: %s" % str(b)[:200]
    if b.get("wildAnimalCount") != len(animals):
        return None, "biome_probe listed %d of %r resolved animals (capped)" % (len(animals), b.get("wildAnimalCount"))
    return dict((a.get("defName"), a.get("commonality")) for a in animals), None


def fulgurite_expected(strikes, sand_frac, chance):
    """Expected new fulgurite, never more than the truth. Patch_LightningStrike_Fulgurite rolls ONCE per
    strike (one Rand.Chance(fulguriteChance), one TryPlaceThing) and only on sand-family ground. A strike
    lands on a uniformly random standable unroofed cell (WeatherEvent_LightningStrike.DoStrike), so the
    sand strikes are a Poisson thinning of ALL strikes with probability >= sand_frac (sand over every
    non-water cell; rock and roofs only shrink the real support). That holds whichever strikes lit a
    fire: a sand strike that lit nothing is still in the total, and bare sand lighting fewer fires only
    makes `strikes` smaller. `strikes` is a floor on all strikes (windows that held any fire, with every
    other igniter isolated), so strikes x sand_frac x chance cannot exceed the true expectation."""
    return strikes * sand_frac * chance


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
        # exceptions; the burnedDef allowlist is retired, so any such line refuses).
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
                _fail("%d 'burnedDef is flammable' lines (the allowlist is retired; every burnedDef is non-flammable "
                      "deep ash)" % allowed)
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
            # Sanity probe (plan bar 1): the census must be able to SEE a plant it did not generate. The probe plants
            # a species the biome's own terrain accepts (2026-10-12: Plant_Grass is REJECTED on Pyrelands ground, so the
            # row failed with a 0-anima census); the row then measures the allowlist, not the probe.
            probe = probe_plant(keys)
            if probe is None:
                _fail("sanity probe: no roster plant to probe with (live wildPlants %r)" % sorted(keys or []))
            host = probe_host(probe, census)
            spot = _things(t, host, limit=1) if host else []
            if not spot:
                _unmeasured(t, "sanity probe: no standing roster plant other than %s to host the probe (census %r)"
                            % (probe, census))
            x, z = spot[0].get("x"), spot[0].get("z")
            pr = t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (probe, x, z), growth=1.0)
            seen = _whole_map(t, "Plant").get(probe, 0) - census.get(probe, 0)
            t.bridge_call("jawa/set_plants", ops="CLEAR:%d,%d,1,1" % (x, z))
            if seen < 1:
                _fail("sanity probe: a spawned %s was not counted by the census (set_plants reply %r)"
                      % (probe, dict((k, (pr or {}).get(k)) for k in ("planted", "rejected", "rejectionReasons",
                                                                      "message"))))
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
        # jawa/get_defs cannot serialise BiomeDef.wildAnimals (a non-public List: UNMEASURED by construction on
        # 2026-10-12); jawa/biome_probe reads the RESOLVED set (AllWildAnimals + CommonalityOfAnimal) instead.
        probe = t.bridge_call("jawa/biome_probe", biomes="RM_Pyrelands", animals=True, plants=False, topN=200)
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
            wa, why = biome_probe_animals(probe, "RM_Pyrelands")
            if wa is None:
                _unmeasured(t, "census clean (%d wild, %d kinds, none foreign) but the live "
                               "wildAnimals read-back the plan requires is not readable: %s"
                            % (len(wild), len(counts), why))
            _note(t, "live resolved wildAnimals (biome_probe)", wa)
            keys = set(wa)
            if keys != set(ANIMAL_MANIFEST):
                _fail("live wildAnimals %r differs from the %d-kind manifest" % (sorted(keys), len(ANIMAL_MANIFEST)))
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
                            if (fert.get(d) or {}).get("fertility", 0) > 0)
            b = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=1)
            built = (b or {}).get("countMatched", 0)
            plantable -= built
            covered = sum(v for k, v in census.items() if k in PLANT_MANIFEST)
            ratio = float(covered) / plantable if plantable > 0 else None
            _note(t, "coverage", {"covered": covered, "plantableCells": plantable,
                                  "buildingsExcluded": built, "ratio": ratio,
                                  "roofedCells": "not excluded (no whole-map roof read)"})
            if plantable <= 0:
                _unmeasured(t, "plantable cell count is zero / unreadable: %r" % terr)
            if ratio < 0.85:
                _fail("plant coverage %.3f of %d plantable cells (< 0.85)" % (ratio, plantable))
        t.screenshot()


@suite.chain("ruins")
def ruins(t):
    """Ruins are found as what they ARE on the map -- unowned artificial buildings (walls, doors,
    the ruin's own floors' structures) -- and their footprint is read for what GenStep_ScorchPyrelandsRuins
    lays (deep ash on the footprint and rim, loose-ash filth over it). The earlier probe listed
    things named `RM_FE_ScorchRuins`, which is the GENSTEP def, never a Thing, so it read UNMEASURED on
    every site by construction (2026-10-11 pilot: the map carried 600+ cells of ruin floors)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ruins_scorched", shows=["pyre_ruins_scorched"]):
        _fresh_site(t)
        r = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=2000)
        if _live(t):
            _ok(r, "list_things(group=BuildingArtificial)")
            rows = [x for x in r.get("things") or []
                    if (x.get("factionName") or x.get("faction")) in (None, "", "None")
                    and x.get("def") not in RUIN_NOT_A_RUIN and x.get("x") is not None]
            _note(t, "unowned artificial buildings (ruins)", {"n": len(rows), "complete": r.get("isCompleteList"),
                                                              "defs": sorted(set(x.get("def") for x in rows))[:20]})
            if not rows:
                if r.get("isCompleteList") is False:
                    _unmeasured(t, "ruin census truncated and empty: %r" % str(r)[:200])
                _unmeasured(t, "this site generated no ruins (0 unowned artificial buildings of %s scanned); "
                               "the bar needs a site with a ruin" % r.get("scanned"))
            sx, sz = _map_size(t)
            picks = [x for x in rows if 1 <= x["x"] < sx - 1 and 1 <= x["z"] < sz - 1]
            picks = picks[::max(1, len(picks) // RUIN_SAMPLES)][:RUIN_SAMPLES]
            if not picks:
                _unmeasured(t, "every ruin building sits on the map edge; no 3x3 footprint sample fits")
            _note(t, "ruin samples (def @ cell): junk from other gensteps vs ScatterRuinsSimple walls",
                  [(x.get("def"), x["x"], x["z"]) for x in picks])
            got = _terrain(t, ";".join("%d,%d,3,3" % (x["x"] - 1, x["z"] - 1) for x in picks))
            frac = sum(v for k, v in got.items() if k == DEEP_ASH or "Water" in k) / float(max(1, sum(got.values())))
            filthy = sum(1 for x in picks if _count(t, "RM_FE_Filth_LooseAsh", "%d,%d,3,3" % (x["x"] - 1, x["z"] - 1)) > 0)
            _note(t, "ruin footprint terrain + loose ash (3x3 at %d sampled ruin buildings)" % len(picks),
                  {"terrain": got, "deepAshFraction": round(frac, 3), "ruinsWithLooseAsh": filthy})
            # Deep ash is ~85% of the map, so terrain alone barely marks a ruin; the genstep lays deep ash on EVERY
            # footprint cell (ruin floors included) and loose-ash filth on ~70% of them, which is the visible scorch.
            if frac < RUIN_ASH_MIN:
                _fail("ruin footprints are %.0f%% deep ash, want >= %.0f%%: %r" % (100 * frac, 100 * RUIN_ASH_MIN, got))
            # The site builder now sets the season BEFORE the map is generated (PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST),
            # so loose ash (6~9 day lifetime, absolute growTick) is minutes old here and 2-of-10 is a genstep finding.
            # A fixture built before that change still carries the old 6-10 day gap: rebuild it, do not excuse it.
            if filthy < RUIN_FILTH_MIN * len(picks):
                _fail("%d of %d sampled ruins carry loose ash, want >= %.0f%%" % (filthy, len(picks), 100 * RUIN_FILTH_MIN))
        t.screenshot()


@suite.chain("burn_line")
@_teardown(fire=True)
def burn_line(t):
    """LONG SPLIT ONLY (~10 min at ~200 ticks/s): run as --chains embergrass_regrow,burn_line, skip in the main run.
    The fixture holds burnLineEnabled OFF, so a census alone is UNMEASURED. The arm: burnLineEnabled ON, extinguish the
    map, wait StandingBurnQuietTicks + a few BurnWatchIntervalTicks, count free-standing Fire. MapComponent_BurnLine
    .TryReseedStandingBurn must have lit one smoulder (parent == null). Then extinguish; _teardown restores settings."""
    _pad(t, PAD_PROBE)
    with _comp(t, "burn_line_present", shows=["pyre_burn_line_present"]):
        _fresh_site(t)
        s = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                          field="burnLineEnabled")
        before = len(_things(t, "Fire", limit=2000))
        _set(t, {"burnLineEnabled": True})
        _extinguish(t)
        _wait(t, BURN_LINE_WAIT_TICKS)
        fires = [f for f in _things(t, "Fire", limit=2000) if not f.get("parent")]
        _note(t, "burn line quiet-arm (free-standing Fire after the quiet window)",
              {"fixtureBurnLineEnabled": (s or {}).get("value"), "firesBeforeArm": before,
               "waitTicks": BURN_LINE_WAIT_TICKS, "freeStandingFires": len(fires)})
        if _live(t) and not fires:
            _fail("burnLineEnabled ON, map extinguished, %d ticks (> StandingBurnQuietTicks %d) and no free-standing "
                  "Fire: the standing burn did not reseed" % (BURN_LINE_WAIT_TICKS, BURN_QUIET_TICKS))
        t.screenshot()
        _extinguish(t)


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

    _independent(t)
    with _comp(t, "biome_def_wiring", toggle="biomeGenerationEnabled"):
        d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
        if _live(t):
            makers = ((_ok(d, "get_def") or {}).get("extra") or {}).get("terrainPatchMakers") or []
            if len(makers) < 1:
                _fail("RM_Pyrelands resolved with no terrainPatchMakers: %r" % d)
            names = [th.get("terrain") for th in ((makers[0] or {}).get("thresholds") or [])]
            if "RM_FE_Ground_Soil" not in names:
                _fail("first terrainPatchMaker (unburned pockets) lacks RM_FE_Ground_Soil: %r" % names)
            every = [th.get("terrain") for m in makers for th in ((m or {}).get("thresholds") or [])]
            if any(a in every for a in LEGACY_ASH):
                _fail("a retired ash rung is still painted by a patchmaker: %r" % every)
        t.screenshot()


@suite.chain("ground_deep_ash")
def ground_deep_ash(t):
    """Gen-time terrain census of the whole map (pyre_ground_deep_ash): deep ash >= DEEP_ASH_MIN of open land, no stock
    vanilla ground, no retired rung, unburned pockets present, standing water ringed with richer ground."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ground_deep_ash", shows=["pyre_ground_deep_ash"]):
        _fresh_site(t)
        gen = _terrain(t, _whole(t))
        if _live(t):
            share, land, detail = ash_census(gen)
            pockets = dict((d, gen.get(d, 0)) for d in ("RM_FE_Ground_Soil", "RM_FE_Ground_Gravel", "RM_FE_Ground_Sand"))
            ring = dict((d, gen.get(d, 0)) for d in ("RM_FE_Ground_SoilRich", "Mud", "WaterShallow"))
            _note(t, "gen terrain census", {"terrain": gen, "deepShareOfOpenLand": share, "openLand": land,
                                            "pockets": pockets, "waterRing": ring, **detail})
            stock = dict((s_, gen[s_]) for s_ in STOCK_GROUND if gen.get(s_))
            if stock:
                _fail("stock ground terrains present on a Pyrelands map: %r" % stock)
            legacy = dict((a_, gen[a_]) for a_ in LEGACY_ASH if gen.get(a_))
            if legacy:
                _fail("retired ash rungs on the map (the load re-lay missed them): %r" % legacy)
            if share is None:
                _unmeasured(t, "no open land read: %r" % gen)
            if share < DEEP_ASH_MIN:
                _fail("deep ash is %.3f of %d open-land cells (< %.2f)" % (share, land, DEEP_ASH_MIN))
            if not any(pockets.values()):
                _fail("no unburned pocket (soil / gravel / sand) at all: %r" % pockets)
            if ring["WaterShallow"] and not (ring["RM_FE_Ground_SoilRich"] or ring["Mud"]):
                _fail("standing water with no rich-soil / mud ring: %r" % ring)
        t.screenshot()


ASH_STRIP_W, ASH_STRIP_H = 12, 3
WATER_FAMILY = ("Mud", "Riverbank")   # plus any def named *Water* / *Marsh* (TerrainDef.IsWater): what the ash sweep counts


def is_water_family(name):
    """A terrain the ash-field sweep marks its radius around (PyrelandsAshField.Sweep: IsWater, Mud, Riverbank)."""
    return bool(name) and (name in WATER_FAMILY or "Water" in name or "Marsh" in name)


def ash_halo(x0, z0, radius):
    """Every cell whose water would mark some cell of the 12x3 strip at (x0, z0) watered: the strip grown by the radius."""
    return (x0 - radius, z0 - radius, ASH_STRIP_W + 2 * radius, ASH_STRIP_H + 2 * radius)


def ash_strip_origins(anchor, size=TEST_SIZE, step=3):
    """Strip origins inside the cleared pad, the anchor first, then nearest first."""
    ax, az = anchor
    half = size // 2
    out = [(x, z) for x in range(ax - half, ax + 1, step) for z in range(az - half, az + half - ASH_STRIP_H + 1, step)]
    out.sort(key=lambda o: (o != (ax, az), abs(o[0] - ax) + abs(o[1] - az), o))
    if (ax, az) not in out:
        out.insert(0, (ax, az))
    return out


def pick_ash_strip(anchor, radius, wet_in):
    """PYRE_ASH_CONTROL_DIAGNOSE_DRY_READS_WET: the first strip origin whose halo holds no natural water, mud or riverbank.
    wet_in(rect string) -> the water-family defs in it. -> (origin or None, [(rejected origin, wet defs), ...]). Site r3
    (2026-10-14) had a pond 2 cells south of the old fixed strip's far end, so the dry control read watered 2/2."""
    rejected = []
    for o in ash_strip_origins(anchor):
        wet = wet_in(_rs(ash_halo(o[0], o[1], radius)))
        if not wet:
            return o, rejected
        rejected.append((o, wet))
    return None, rejected


@suite.chain("ash_fertility_watered")
@_teardown()
def ash_fertility_watered(t):
    """pyre_ash_fertile_when_watered, a STATE read of FertilityAt (the postfix every grower reads): a deep-ash strip with
    one WaterShallow cell at its west end; after a full watering sweep (8 x 250 ticks) the cell beside the water reads the
    watered value and a cell 8 away reads dry. The strip is placed where no natural water, mud or riverbank lies within the
    sweep's radius of it (pick_ash_strip), so the far cell is a real dry control. The FlowWorks-channel route shares this
    read but is not staged here (it needs a dug, filled channel); its cell rule is the one ExplosiveGrowth's soak already
    uses (_Shared/FlowWorksIrrigation)."""
    _pad(t, PAD_ASH)
    t.clear_area(size=TEST_SIZE)
    with _comp(t, "ash_fertile_when_watered", shows=["pyre_ash_fertile_when_watered"]):
        _isolate(t)
        x0, z0 = t.anchor
        if _live(t):
            radius = int(float(_live_setting(t, "ashNaturalWaterRadius")))
            origin, rejected = pick_ash_strip(t.anchor, radius,
                                              lambda rect: sorted(d for d in _terrain(t, rect) if is_water_family(d)))
            _note(t, "ash strip placement (natural water within the sweep radius %d rejects an origin)" % radius,
                  {"origin": origin, "rejected": rejected[:6], "nRejected": len(rejected)})
            if origin is None:
                _unmeasured(t, "no strip origin in the %dx%d pad at %r is clear of natural water within radius %d: %r"
                            % (TEST_SIZE, TEST_SIZE, PAD_ASH, radius, rejected[:4]))
            x0, z0 = origin
        t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=DEEP_ASH, width=ASH_STRIP_W, height=ASH_STRIP_H, layer="top")
        dry0 = _probe(t, x0 + 1, z0 + 1)
        far0 = _probe(t, x0 + 9, z0 + 1)
        t.bridge_call("jawa/set_terrain", x=x0, z=z0 + 1, terrainDef="WaterShallow", width=1, height=1, layer="top")
        _wait(t, 2600)
        wet = _probe(t, x0 + 1, z0 + 1)
        dry = _probe(t, x0 + 9, z0 + 1)
        _note(t, "FertilityAt: beside water vs 8 cells away (and both cells before the water)",
              {"origin": [x0, z0], "before": dry0, "farBefore": far0, "beside": wet, "far": dry})
        if _live(t):
            if dry0.get("terrain") != DEEP_ASH or dry.get("terrain") != DEEP_ASH:
                _fail("the probe cells are not deep ash: %r / %r" % (dry0.get("terrain"), dry.get("terrain")))
            if dry0["watered"] or far0["watered"] or dry["watered"]:
                _unmeasured(t, "the dry control reads watered with no natural water within the radius (a Black Rain, or a "
                               "watered mark under a day old): before %r / far %r" % (far0, dry))
            if not wet["watered"]:
                _fail("the cell beside WaterShallow is not watered after a full sweep: %r" % wet)
            if wet["fertility"] - dry["fertility"] < WATERED_MIN_GAIN:
                _fail("watered %.2f vs dry %.2f: gain < %.2f" % (wet["fertility"], dry["fertility"], WATERED_MIN_GAIN))
        t.screenshot()


@suite.chain("fresh_burn_bonus")
@_teardown(fire=True, weather=True)
def fresh_burn_bonus(t):
    """LONG SPLIT (~100k ticks). pyre_fresh_burn_feeds_the_field, a STATE read of FertilityAt on a burned deep-ash cell:
    before the burn, right after it, +1 day (the linear decay; the design's +3 days costs another 120k ticks for a point
    the kernel selftest already pins), then after ~15 h of forced RM_FE_BlackRain (rain budget 12 h at rate 1.1: the bonus
    must be gone, and the Black Rain must have watered the field). The fire burning on DEEP ASH is also the live proof of
    the widened fire-tick gate (the stamp fires only through it)."""
    _pad(t, PAD_BURN)
    t.clear_area(size=TEST_SIZE)
    burn = _rect(t, 10)
    cx, cz = burn[0] + 5, burn[1] + 5
    with _comp(t, "fresh_burn_feeds_the_field", shows=["pyre_fresh_burn_feeds_the_field"]):
        _isolate(t)
        _firebreak(t, burn)
        t.bridge_call("jawa/set_terrain", x=burn[0], z=burn[1], terrainDef=DEEP_ASH, width=10, height=10, layer="top")
        _plants(t, "RM_FE_Plant_EmberGrass", burn)
        before = _probe(t, cx, cz)
        _GEN["ignitions"] = []
        _fire(t, burn)
        _wait(t, REGROW_BURN_TICKS)
        _extinguish(t)
        after = _probe(t, cx, cz)
        _wait(t, 60000)
        day1 = _probe(t, cx, cz)
        t.bridge_call("jawa/weather_set", weather="RM_FE_BlackRain", lockWeather=True)
        _wait(t, 37500)
        rained = _probe(t, cx, cz)
        series = {"before": before, "afterBurn": after, "day1": day1, "afterBlackRain15h": rained,
                  "ignition": (_GEN.get("ignitions") or [None])[-1]}
        _note(t, "FertilityAt on the burned cell", series)
        if _live(t):
            if before.get("bonus", 0) > 0.001:
                _unmeasured(t, "the cell carried a burn bonus before the test burn: %r" % before)
            if after.get("burnTick", "-1") in ("-1", None):
                _fail("no burn stamp on the burned deep-ash cell: the fire-tick gate refused deep ash? %r" % after)
            if after["bonus"] < BURN_BONUS_MIN or after["fertility"] - before["fertility"] < BURN_BONUS_MIN:
                _fail("right after the burn: bonus %.2f, fertility %.2f -> %.2f (want >= +%.2f)"
                      % (after["bonus"], before["fertility"], after["fertility"], BURN_BONUS_MIN))
            if not (0 < day1["bonus"] < after["bonus"]):
                _fail("the bonus did not fade over a day: %.3f -> %.3f" % (after["bonus"], day1["bonus"]))
            if rained["bonus"] > 0.01:
                _fail("~15 h of Black Rain left a burn bonus of %.3f (rain budget 12 h)" % rained["bonus"])
            if not rained["watered"]:
                _fail("Black Rain did not water the field: %r" % rained)
        t.screenshot(rect=burn)


@suite.chain("ambient_ash_drift")
@_teardown(weather=True)
def ambient_ash_drift(t):
    """Owner 2026-10-12: "a LOT of free-flying ash blowing around like snow". The live RM_Pyrelands weather table (after
    the ambient-ash settings were written) must make RM_FE_Weather_AshDrift the commonest weather; then it is forced for
    a screenshot (flakes in the air is an eyes check, not decided here)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ash_drift_common", toggle="ambientAshEnabled"):
        r = t.bridge_call("jawa/static_call", type=ASH_FIELD, method="WeatherShares")
        if _live(t):
            _ok(r, "WeatherShares")
            table = {}
            for kv in str(r.get("result") or "").split(";"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    table[k] = float(v)
            _note(t, "live RM_Pyrelands weather commonalities", table)
            if not table:
                _fail("no weather table read: %r" % r)
            top = max(table, key=table.get)
            if top != "RM_FE_Weather_AshDrift" or table.get(top, 0) <= 0:
                _fail("the commonest weather is %s (%r), not RM_FE_Weather_AshDrift" % (top, table))
        t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshDrift", lockWeather=True)
        _wait(t, 3000)
        t.screenshot()


# --------------------------------------------------------------------------- toggle floor

@suite.chain("fire_tick_effects")
@_teardown(fire=True)
def fire_tick_effects(t):
    """One fire on a GRASSED patch of RM_FE_Ash_Deep -- the biome's ordinary ground, so this is the live proof that the
    fire-tick gate admits deep ash (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED; before it, dusting and fruit stopped there) --
    ringed by a firebreak, watched long enough for both fire-tick postfixes to roll. Fuel is what keeps a fire alive; a
    fuel-less sand fire goes out (the 2026-09-13 false RED)."""
    _pad(t, PAD_FIRE_TICK)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x0, z0, w, h = rect
    _firebreak(t, rect)
    ground = t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=DEEP_ASH,
                           width=w, height=h, layer="top")
    # cells already on the target terrain are correct, not unpainted
    if _live(t) and (ground or {}).get("cellsChanged", 0) + (ground or {}).get("cellsAlreadyCorrect", 0) < w * h:
        _fail("set_terrain(%s) over %s did not paint the whole rect: %r" % (DEEP_ASH, _rs(rect), ground))
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
            if whole > 40:  # RM_PyrelandsSettings.scorchFruitMapCap shipped default; the cap is per MAP
                _fail("ScorchFruit count %d on the map exceeds the per-map cap 40" % whole)
        t.screenshot(rect=rect)
    # hand the next chain an empty fruit budget (the cap is per MAP, shared with scorchfruit_fire_born)
    _clear_scorchfruit(t)


def _clear_scorchfruit(t):
    """ScorchFruit shares ONE per-map cap (scorchFruitMapCap 40) across every chain that burns a pad, so a chain
    that leaves its fruit standing starves the next (fire_tick_effects left 35 and scorchfruit_fire_born found 0,
    2026-10-12). Each fire-pad chain therefore starts with the map's fruit budget empty: destroy the plants (only
    the Plant category) around every fire pad, where this suite's own fires -- the only fire-born source on the
    site -- seed the fruit."""
    for (px, pz) in FIRE_PADS:
        t.bridge_call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (px - 20, pz - 20, 40, 40), categories="Plant")
    left = _count(t, "RM_FE_Plant_ScorchFruit")
    _note(t, "ScorchFruit left on the map after the cap-budget clear", left)


@suite.chain("ashfall_weather_accumulation")
@_teardown(weather=True)
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
@_teardown(weather=True)
def ashfall_drifts(t):
    _pad(t, PAD_PROBE)
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


def _weather_pair(t, name, other, fields):
    defs = _get_defs(t, "WeatherDef/%s;WeatherDef/%s" % (name, other), ",".join(fields))
    if _live(t):
        a, b = defs.get(name) or {}, defs.get(other) or {}
        _note(t, "def fields", {name: a, other: b})
        if not a or not b:
            _fail("get_defs returned no fields for %s / %s" % (name, other))
        if all(a.get(f) == b.get(f) for f in fields):
            _fail("%s and %s differ in none of %r" % (name, other, fields))
    t.bridge_call("jawa/weather_set", weather=name, lockWeather=True)   # unlocked by the chain's teardown
    _wait(t, 5000)
    t.screenshot()


@suite.chain("cinderfall")
@_teardown(weather=True)
def cinderfall(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "cinderfall_distinct", shows=["pyre_cinderfall_distinct"]):
        _weather_pair(t, "RM_FE_Weather_Cinderfall", "RM_FE_Weather_AshFall",
                      ("overlayClasses", "skyColorsDay", "skyColorsNightMid", "windSpeedFactor"))


@suite.chain("blackrain")
@_teardown(weather=True)
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
@_teardown(fire=True)
def scorchfruit_fire_born(t):
    _pad(t, PAD_FIRE_BORN)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    with _comp(t, "scorchfruit_fire_born", shows=["pyre_scorchfruit_fire_born"]):
        _isolate(t)
        _clear_scorchfruit(t)   # earlier chains' fruit must not eat this cohort's share of the map cap
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


@suite.chain("scorchfruit_produces")
@_teardown()
def scorchfruit_produces(t):
    """Attributable harvest and ingest (plan 2.3a): ripe plants, forced harvest, the yield made
    by that harvest, a forced ingest, and the food delta across that ingest only."""
    _pad(t, PAD_HARVEST)
    t.clear_area(size=12)
    rect = _rect(t, 6)
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


@suite.chain("scorchfruit_spoils")
@_teardown()
def scorchfruit_spoils(t):
    """Rot read from the item's own inspect text (CompRottable), sampled every half day, with a
    vanilla reference food beside it. [O] yield daysToRotStart 4, plant 1.1."""
    _pad(t, PAD_SPOIL)
    t.clear_area(size=12)
    x, z = t.anchor
    with _comp(t, "scorchfruit_spoils_fast", shows=["pyre_scorchfruit_spoils_fast"]):
        _isolate(t)
        # Plan 2.3a: the stack sits in a fenced cell no pawn can reach. In the open a wild
        # grazer ate it at day 2 (runs 5 and 6, steel ring included). A sealed room (player
        # door: animals cannot open it) held three stacks untouched (probe 2026-10-01).
        # Unrefrigerated: the room tracks the site's own ~45-58 C.
        # doorDef=Wall: NO door. The 2026-10-12 run lost the stack by day 0.5 with whole-map yield 0 (eaten, not
        # hauled) right after scorchfruit_produces left its colonists hungry: a player door keeps animals out but
        # lets colonists in. Nothing needs to enter this room.
        room = t.bridge_call("jawa/make_empty_room", rect="%d,%d,11,9" % (x - 5, z - 3),
                             stuffDef="Steel", doorDef="Wall")
        if _live(t):
            _ok(room, "make_empty_room")
        t.bridge_call("jawa/spawn_batch", ops="RM_FE_ScorchFruitYield:%d,%d,10;Meat_Human:%d,%d,10"
                      % (x, z, x + 2, z))
        _plants(t, "RM_FE_Plant_ScorchFruit", (x - 3, z + 3, 3, 1))
        yid = [y.get("id") for y in _things(t, "RM_FE_ScorchFruitYield", "%d,%d,1,1" % (x, z))]
        if _live(t) and not yid:
            _fail("the spawned RM_FE_ScorchFruitYield stack was not found at %d,%d" % (x, z))
        samples, plant_at_1_5 = [], None
        for half_day in range(1, 10):          # 0.5 .. 4.5 days
            _wait(t, 30000)
            if not _live(t):
                break
            # Presence and rot are read separately: a refused or empty inspect read is NOT a
            # destroyed stack, and only list_things can say the stack is gone.
            near = _things(t, "RM_FE_ScorchFruitYield", "%d,%d,5,5" % (x - 2, z - 2))
            present = bool(_ids_on_map(t, "RM_FE_ScorchFruitYield") & set(yid))
            r = t.bridge_call("jawa/inspect_string", thingIds=",".join(yid))
            read_ok = isinstance(r, dict) and r.get("success") is not False and isinstance(r.get("things"), list)
            rows = r["things"] if read_ok else []
            ref = t.bridge_call("jawa/inspect_string", defName="Meat_Human",
                                rect="%d,%d,1,1" % (x + 2, z))
            samples.append({"day": half_day / 2.0, "present": present, "inspectRead": read_ok,
                            "yieldOnMap": _count(t, "RM_FE_ScorchFruitYield"),
                            "near": [(w.get("id"), w.get("x"), w.get("z"), w.get("stackCount")) for w in near],
                            "yield": [" ".join(w.get("inspect") or []) for w in rows],
                            "ref": [" ".join(w.get("inspect") or []) for w in ((ref or {}).get("things") or [])]})
            if half_day == 3:
                plant_at_1_5 = _count(t, "RM_FE_Plant_ScorchFruit", "%d,%d,3,1" % (x - 3, z + 3))
            if spoil_sampling_done(samples):
                break   # gone before its timer: the verdict is already UNMEASURED; 4 more days of waiting buy nothing
        _note(t, "rot samples", samples)
        if _live(t):
            gone_early = [s for s in samples if s["day"] < 3.0 and not s["present"]]
            if gone_early:
                g = gone_early[0]
                _note(t, "log around the disappearance",
                      [m.get("text", "")[:200] for m in
                       ((t.bridge_call("jawa/drain_log", limit=30) or {}).get("messages") or [])])
                _unmeasured(t, "the sealed-room yield stack vanished by day %.1f, before its "
                               "spoil timer ran out (whole-map ScorchFruitYield stacks then: %s); "
                               "something removed it, so rot is unproven this run"
                            % (g["day"], g.get("yieldOnMap")))
            last = samples[-1]
            if last["present"]:
                if not last["inspectRead"] or not last["yield"]:
                    _unmeasured(t, "the yield stack is still on the map at day 4.5 but its inspect text "
                                   "could not be read, so whether it rotted is unknown")
                if not any("rot" in s.lower() or "spoiled" in s.lower() for s in last["yield"]):
                    _fail("RM_FE_ScorchFruitYield neither rotted nor destroyed by day 4.5: %r" % last["yield"])
            if plant_at_1_5:
                _fail("%d unharvested ScorchFruit plant(s) still standing at day 1.5" % plant_at_1_5)
        t.screenshot()


def spoil_sampling_done(samples):
    """True once a sample before day 3 finds the stack gone: the verdict can only be UNMEASURED from there, and
    the remaining half-day waits cost up to 240,000 ticks (~20 min at the measured ~200 ticks/s Ultrafast)."""
    return any(sm["day"] < 3.0 and not sm["present"] for sm in samples)


# --------------------------------------------------------------------------- the fire cast

@suite.chain("firehawk")
@_teardown(fire=True)
def firehawk(t):
    _pad(t, PAD_HAWK)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    with _comp(t, "firehawk_carries_ember", shows=["pyre_firehawk_carries_ember"]):
        _set(t, {"burnLineEnabled": True, "fireHawkSpreadEnabled": True})
        _firebreak(t, rect)
        _soil(t, rect)
        _plants(t, "RM_FE_Plant_EmberGrass", rect)
        _fire(t, (x - 2, z - 2, 4, 4), size=0.5)
        hawk = _spawn_wild(t, "RM_FireHawk", x + 8, z)
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


@suite.chain("furnace_warmth")
@_teardown()
def furnace_warmth(t):
    _pad(t, PAD_WARMTH)
    t.clear_area(size=12)
    x, z = t.anchor
    with _comp(t, "furnacebeast_warmth", shows=["pyre_furnacebeast_warmth"]):
        _set(t, {"furnaceThermalEnabled": True})
        # CompFurnaceWarmthAura: radius = 4.9 x sqrt(baseBodySize / 3.2) x Lerp(0.35, 1, charge) (giant: x1.37); a fresh beast's charge is
        # 0, so its aura reaches 1.7 cells, and a wild beast wanders off a colonist walking after
        # it (run 7: 6-10 cells apart in 7 of 8 samples). Both stand in a 2x1 pen (a 4x3
        # make_empty_room), so they are never more than 1 cell apart.
        pen = t.bridge_call("jawa/make_empty_room", rect="%d,%d,4,3" % (x - 1, z - 1),
                            stuffDef="Steel")
        if _live(t):
            _ok(pen, "make_empty_room")
        bid = _spawn_wild(t, "RM_FurnaceBeast", x, z)
        r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x + 1, z=z, faction="player",
                          count=1)
        col = (((r or {}).get("pawns") or [{}])[0]).get("id")
        if col:
            t.session.track("pawn", col, x=x + 1, z=z)
        samples = []
        for _ in range(4 if _live(t) else 0):
            _wait(t, 90)
            near = _pawn_row(t, col, health=True) or {}
            b = _pawn_row(t, bid) or {}
            d = None
            if b.get("x") is not None and near.get("x") is not None:
                d = ((b["x"] - near["x"]) ** 2 + (b["z"] - near["z"]) ** 2) ** 0.5
            samples.append({"beast": (b.get("x"), b.get("z")),
                            "colonist": (near.get("x"), near.get("z")),
                            "dist": d, "warm": _has_hediff(near, "RM_FurnaceWarmth")})
        _note(t, "colonist-to-beast distance / warmth samples (pen)", samples)
        if _live(t):
            if not col:
                _fail("could not spawn the test colonist: %r" % r)
            # PYRELANDS_FURNACE_WARMTH_AMBIENT_1: one kind of heat. The old comfort-range hediff is retired, so
            # standing beside the beast must never grant it; the warmth is a felt-temperature offset
            # (FurnaceWarmthField.OffsetFor), whose falloff maths the offline selftest proves.
            if any(sm["warm"] for sm in samples):
                _fail("colonist beside the furnace-beast gained RM_FurnaceWarmth: the hediff was retired")
            _unmeasured(t, "the felt-temperature offset needs a debug [Tool] reading Thing.AmbientTemperature "
                           "(FurnaceWarmthField.OffsetFor) on a pawn; none exists yet, and no hediff is the control")
        t.screenshot()


@suite.chain("furnace_room")
@_teardown()
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
        # Steel, and doorDef=Wall (no door): 2026-10-12 control room B was set to 10 C and read 46.8 C 250 ticks
        # later while A climbed 10 -> 17.5 -- B behaved as if open to the 47 C outdoors. A door a pawn can open is
        # the one opening the default room has; with none, both rooms differ only by the beast.
        for r in (a, b):
            t.bridge_call("jawa/make_empty_room", rect=_rs(r), stuffDef="Steel", doorDef="Wall")
        bid = _spawn_wild(t, "RM_FurnaceBeast", ca[0], ca[1])
        _wait(t, 600)

        def tv(r):
            return (r or {}).get("temperature", (r or {}).get("temp"))
        rooms = [t.bridge_call("jawa/room_get", x=c[0], z=c[1]) for c in (ca, cb)]
        beast = _pawn_row(t, bid) or {}
        amb = [tv(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % c)) for c in (ca, cb)]
        heat = [t.bridge_call("jawa/room_heat", x=c[0], z=c[1], mode="set", value=10.0)
                for c in (ca, cb)]
        if _live(t):
            _note(t, "room_heat set 10 C (A, B)", heat)
        series = []
        for _ in range(10):
            _wait(t, 250)
            series.append([tv(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % c))
                           for c in (ca, cb)])
        after = [t.bridge_call("jawa/room_get", x=c[0], z=c[1]) for c in (ca, cb)]
        if _live(t):
            _note(t, "rooms after the series (A, B)", [dict((k, v) for k, v in (r or {}).items()
                                                            if k not in ("operation", "state")) for r in after])
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
@_teardown(fire=True)
def burrowers(t):
    _pad(t, PAD_BURROW)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    with _comp(t, "burrowers_dive", shows=["pyre_burrowers_dive"]):
        _set(t, {"burrowOnFireEnabled": True})
        _firebreak(t, rect)
        _soil(t, rect)
        _plants(t, "RM_FE_Plant_EmberGrass", rect)
        g = _spawn_wild(t, "RM_Ashwallow", x + 5, z)
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


# --------------------------------------------------------------------------- long waits last

@suite.chain("embergrass_regrow")
@_teardown(fire=True)
def embergrass_regrow(t):
    """Fixed 20x20 cohort, pre-laid to RM_FE_Ash_Deep (the real ground), grassed, burned, then a COMPRESSED regrow window (override, see below).
    Counts only plants spawned AFTER the burn (ThingID not in the pre-burn set)."""
    _pad(t, PAD_REGROW)
    t.clear_area(size=TEST_SIZE)
    regrow = _rect(t, 20)
    inner = _rs((regrow[0] + 2, regrow[1] + 2, 16, 16))   # minus the 2-cell edge band
    with _comp(t, "embergrass_regrows", shows=["pyre_embergrass_regrows"]):
        _isolate(t)
        _firebreak(t, regrow)
        t.bridge_call("jawa/set_terrain", x=regrow[0], z=regrow[1], terrainDef=DEEP_ASH, width=20,
                      height=20, layer="top")
        _plants(t, "RM_FE_Plant_EmberGrass", regrow)
        pre_ids = set(p.get("id") for p in _things(t, "RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass",
                                                   inner, limit=2000))
        _fire(t, regrow)
        # 5000, not 3000: EmberGrass stands in fire ~3500 ticks (live timeline 2026-10-12c: 398 -> 387 at 3500 -> 27 at
        # 4000 -> 15 at 4500).
        _wait(t, REGROW_BURN_TICKS)
        _extinguish(t)
        # Precondition: the burn must actually have killed the patch. Count the ORIGINAL plants (pre-burn ThingIDs) still
        # standing; a patch the fire left alive can never show "new" plants (2026-10-12: 256/256 grassed at day 7, row 0).
        standing = len([p for p in _things(t, "RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass", inner, limit=2000)
                        if p.get("id") in pre_ids])
        _note(t, "regrow burn check (original plants still standing after the fire)",
              {"pre": len(pre_ids), "standingAfterBurn": standing})
        if _live(t):
            cleared, burn_txt = burn_cleared(len(pre_ids), standing)
            if not cleared:
                _unmeasured(t, "the burn did not clear the patch, so regrowth cannot be read: " + burn_txt)

        def new_count():
            return len([p for p in _things(t, "RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass",
                                           inner, limit=2000) if p.get("id") not in pre_ids])
        # PYRE_REGROW_BUILD_A_WEEK_IN_MINUTES: COMPRESSED. The shipped regrow pace is wildPlantRegrowDays 9; the
        # override 0.1 runs the spawner 90x faster, so REGROW_SHORT_STEP*2 ticks stand in for ~4.5 shipped days.
        # The override is flipped AFTER the burn check (it only paces new spawns) and restored + read back below.
        _set(t, {"wildPlantRegrowDaysOverride": REGROW_OVERRIDE_DAYS})
        d0 = new_count()
        _wait(t, REGROW_SHORT_STEP)
        d3 = new_count()
        live_ovr = (_get_defs(t, "BiomeDef/RM_Pyrelands", "wildPlantRegrowDays").get("RM_Pyrelands") or {}).get(
            "wildPlantRegrowDays")
        _wait(t, REGROW_SHORT_STEP)
        d7 = new_count()
        temp = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % t.anchor)
        pre = len(pre_ids)
        bad = _restore(t)
        shipped = _live_setting(t, "wildPlantRegrowDaysOverride")
        _wait(t, 300)   # the enforcer re-asserts on 250-tick boundaries
        live_after = (_get_defs(t, "BiomeDef/RM_Pyrelands", "wildPlantRegrowDays").get("RM_Pyrelands") or {}).get(
            "wildPlantRegrowDays")
        _note(t, "COMPRESSED regrow (override %s days vs shipped 9; ~90x). Shipped constant read back after restore"
              % REGROW_OVERRIDE_DAYS,
              {"pre": pre, "afterBurn": d0, "step1": d3, "step2": d7, "stepTicks": REGROW_SHORT_STEP,
               "step1Frac": (float(d3) / pre) if pre else None,
               "step2Frac": (float(d7) / pre) if pre else None, "temp": temp,
               "overrideReadBack": shipped, "biomeRegrowDaysDuringOverride": live_ovr,
               "biomeRegrowDaysAfterRestore": live_after, "restoreFailures": [str(x) for x in bad]})
        if _live(t):
            if pre <= 0:
                _fail("regrow cohort had no pre-burn plants")
            def _num(v):
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return None
            if bad or _num(shipped) != 0.0:
                _fail("regrow override did not restore to the shipped 0: readback %r, failures %r" % (shipped, bad))
            if _num(live_ovr) is None or abs(_num(live_ovr) - REGROW_OVERRIDE_DAYS) > 1e-4:
                _fail("override did not reach the live biome: wildPlantRegrowDays %r, wanted %r"
                      % (live_ovr, REGROW_OVERRIDE_DAYS))
            if _num(live_after) is None or abs(_num(live_after) - 9.0) > 1e-4:
                _fail("shipped biome wildPlantRegrowDays 9 not restored: live %r" % (live_after,))
            if d7 <= d0:
                _fail("no new plants appeared during the COMPRESSED regrow window: afterBurn=%d step2=%d" % (d0, d7))
            _unmeasured(t, "COMPRESSED (override %s days, 2x%d ticks): new roster plants in the burned 16x16 cohort "
                           "pre=%d afterBurn=%d step1=%d step2=%d; shipped 7-day fractions stay INFERRED/CALIBRATING "
                           "(plan targets 25%%/60%%); override restored to %r"
                        % (REGROW_OVERRIDE_DAYS, REGROW_SHORT_STEP, pre, d0, d3, d7, shipped))
        t.screenshot(rect=regrow)


def _stack_total(t, defName):
    """Items of `defName` on the map, summed over stackCount: a fulgurite placed Near merges into an
    existing stack (stackLimit 25) and adds no thing. Refuses a truncated listing."""
    r = t.bridge_call("jawa/list_things", defName=defName, limit=2000)
    if not _live(t):
        return 0
    rows = _ok(r, "list_things(%s)" % defName).get("things")
    if not isinstance(rows, list) or r.get("countMatched") != len(rows) or \
            any(not isinstance(w.get("stackCount"), int) for w in rows):
        _fail("list_things(%s) incomplete or without stackCount: countMatched %r, %r rows"
              % (defName, r.get("countMatched"), len(rows) if isinstance(rows, list) else rows))
    return sum(w["stackCount"] for w in rows)


def _live_setting(t, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
    if not _live(t):
        return None
    if not (r or {}).get("success") or r.get("value") is None:
        _fail("cannot read %s.%s: %r" % (SETTINGS, field, r))
    return r["value"]


SAND_PATCH_MIN_FRAC = 0.4      # fulgurite needs enough sand that strikes x fraction x chance can reach fulgurite_expected's bar
SAND_PATCH_TERRAIN = "Sand"    # vanilla sand: in SAND_FAMILY, and not behind the Pyrelands mechanics gate
SAND_RESTORE_BATCH = 200


def sand_patch_rect(map_x, map_z):
    """The block laid when the site has too little sand: the west half of the map (a lightning strike lands on a random
    cell, so the patch has to be a large share of the land for 20 windows to reach it). Pure."""
    return (0, 0, max(1, map_x // 2), map_z)


def sand_patch_needed(sand_cells, land_cells, min_frac=SAND_PATCH_MIN_FRAC):
    """True when the site's sand-family share of land is below min_frac (PYRE_FULGURITE_BUILD_NO_SAND_TO_STRIKE: site r3 had
    0 of 61978). Pure."""
    return land_cells > 0 and float(sand_cells) / land_cells < min_frac


def split_restore_ops(ops, batch=SAND_RESTORE_BATCH):
    """'Def:x,z,w,h;...' (get_terrain_batch's reply) -> lists of at most `batch` ops joined for set_terrain_batch. Pure."""
    items = [o.strip() for o in (ops or "").replace("\n", ";").split(";") if ":" in o]
    return [";".join(items[i:i + batch]) for i in range(0, len(items), batch)]


def _lay_sand_patch(t):
    """Snapshot the patch rect's terrain, then paint it sand. Returns (rect_string, snapshot_ops) for _restore_terrain."""
    mx, mz = _map_size(t)
    rect = _rs(sand_patch_rect(mx, mz))
    snap = t.bridge_call("jawa/get_terrain_batch", rects=rect)
    _ok(snap, "get_terrain_batch(%s) before the sand patch" % rect)
    if snap.get("cellsRead") != snap.get("cellsRequested") or not snap.get("ops"):
        _fail("sand patch: could not snapshot %s to restore it (%r of %r cells)" % (
            rect, snap.get("cellsRead"), snap.get("cellsRequested")))
    t.bridge_call("jawa/set_terrain", x=0, z=0, terrainDef=SAND_PATCH_TERRAIN, width=mx // 2, height=mz, layer="top")
    return rect, snap["ops"]


def _restore_terrain(t, laid):
    """Put the snapshotted terrain back. Runs in a finally, so it talks to the SESSION: t.bridge_call is a no-op once
    the component has failed or gone UNMEASURED, which left half the map sand for every later chain. A restore that
    does not take is reported by the chain's _tear_down as a teardown FAIL (never from inside the open component)."""
    rect, ops = laid
    sess = getattr(t, "session", None)
    call = sess.call if sess is not None else t.bridge_call
    bad = []
    for chunk in split_restore_ops(ops):
        try:
            r = call("jawa/set_terrain_batch", ops=chunk, layer="top")
            if sess is not None and (not isinstance(r, dict) or r.get("success") is False):
                bad.append("sand patch %s restore refused: %r" % (rect, str(r)[:160]))
        except Exception as e:   # noqa: BLE001 - keep restoring the rest; recorded as a FAIL
            bad.append("sand patch %s restore raised %s" % (rect, e))
    if sess is not None and bad:
        _GEN.setdefault("teardown_bad", []).extend(bad)


@suite.chain("fulgurite")
@_teardown(fire=True, weather=True)
def fulgurite(t):
    """No tool forces one strike: lock DryThunderstorm and count fulgurite from before to after.
    Lightning lights fires, so this runs after every fire-sensitive chain and the map is extinguished
    after."""
    _pad(t, PAD_PROBE)
    with _comp(t, "fulgurite_after_lightning", shows=["pyre_fulgurite_after_lightning"]):
        # Every other igniter OFF, so each fire seen below is a strike's (the burn line and the
        # fire-hawk light their own fires and would read as strikes).
        _isolate(t)
        _set(t, {"fulguriteEnabled": True})
        chance = _live_setting(t, "fulguriteChance")
        before = _stack_total(t, "RM_FE_Fulgurite")
        terr = _terrain(t, _whole(t))
        # FulguriteMayRoll: RM_FE_ sand rolls only while the Pyrelands mechanics gate is on; when the
        # gate cannot be read, that sand is left out (a smaller expectation, never a false FAIL).
        g = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.PyrelandsMechanicsGate", method="get_On")
        gate_on = str((g or {}).get("result")) == "True" if isinstance(g, dict) else False
        sand = sum(v for k, v in terr.items()
                   if k in SAND_FAMILY and (gate_on or not k.startswith("RM_FE_")))
        land = sum(v for k, v in terr.items() if "Water" not in k)
        laid = None
        if _live(t) and sand_patch_needed(sand, land):
            # PYRE_FULGURITE_BUILD_NO_SAND_TO_STRIKE: site r3 had 0 sand cells, so no strike could reach sand and the row was
            # UNMEASURED. Lay a sand patch (snapshotted, restored in the finally below) and take the chance to 100% so the
            # bar can be met; the row then proves "a strike on sand yields fulgurite", the chance itself is a Settings value.
            laid = _lay_sand_patch(t)
            _set(t, {"fulguriteChance": 1.0})
            chance = _live_setting(t, "fulguriteChance")
            terr = _terrain(t, _whole(t))
            sand = sum(v for k, v in terr.items()
                       if k in SAND_FAMILY and (gate_on or not k.startswith("RM_FE_")))
            land = sum(v for k, v in terr.items() if "Water" not in k)
        sand_frac = float(sand) / land if land else 0.0
        _note(t, "sand-family cells (fulgurite needs sand)",
              {"cells": sand, "nonWaterCells": land, "frac": sand_frac, "gateOn": gate_on, "gateRead": g,
               "fulguriteChance": chance, "sandPatchLaid": laid[0] if laid else None})
        try:
            _fulgurite_windows(t, before, sand_frac, chance)
        finally:
            if laid is not None:
                _restore_terrain(t, laid)
        t.screenshot()


def _fulgurite_windows(t, before, sand_frac, chance):
    _extinguish(t)
    t.bridge_call("jawa/weather_set", weather="DryThunderstorm", lockWeather=True)
    # Lightning lights the grass: extinguish every ~1,000 ticks so a strike cannot grow into
    # a map-wide burn (run 4 burned the whole site to deep ash this way). A window that holds any
    # fire saw at least one strike; counting fires or fire clusters instead would count one strike
    # many times (sparks, and a burning animal that runs carries its fire across the map).
    strikes, per_check = 0, []
    for _ in range(20):
        _wait(t, 1000, fast=True)
        n_fire = _count(t, "Fire")
        per_check.append(n_fire)
        if n_fire:
            strikes += 1
        _extinguish(t)
    after = _stack_total(t, "RM_FE_Fulgurite")
    _note(t, "fulgurite across 20 windows of DryThunderstorm",
          {"before": before, "after": after, "windowsWithFire": strikes, "firesPerWindow": per_check})
    if _live(t):
        try:
            chance = float(chance)
        except (TypeError, ValueError):
            _fail("fulguriteChance read back non-numeric: %r" % (chance,))
        expect = fulgurite_expected(strikes, sand_frac, chance)
        if after - before < 1 and expect < 3:   # P(zero | working) = e^-expect, so < 3 is too weak to FAIL on
            _unmeasured(t, "expected >= %.2f fulgurite (%d windows with fire x sand fraction %.4f x chance %.2f): "
                           "too few strikes can reach sand to test the bar" % (expect, strikes, sand_frac, chance))
        if after - before < 1:
            _fail("no new RM_FE_Fulgurite after 20 windows of locked DryThunderstorm (%d -> %d; %d "
                  "windows with fire, expected >= %.2f)" % (before, after, strikes, expect))


def parse_kv(text):
    """"a=1;b=x,y" -> {"a": "1", "b": "x,y"} (the static_call probes' reply shape)."""
    out = {}
    for kv in str(text or "").split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def xz_of(v):
    """"x,z" -> (x, z) as floats, anything else -> None."""
    try:
        x, z = str(v).split(",")
        return float(x), float(z)
    except (TypeError, ValueError):
        return None


def _dist(p, q):
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5


def herd_verdict(start, end, a, b, min_close=HERD_MIN_CLOSE):
    """PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER, the motion half: the herd centroid closed at least min_close of its start
    distance to A (the two-day-old burn) and closed on A more than on B (the fresh one). -> (ok, why)."""
    if start is None or end is None:
        return False, "herd centroid unread: start %r end %r" % (start, end)
    a0, a1, b0, b1 = _dist(start, a), _dist(end, a), _dist(start, b), _dist(end, b)
    why = "centroid %r -> %r: to A %.1f -> %.1f, to B %.1f -> %.1f" % (start, end, a0, a1, b0, b1)
    if a1 > a0 * (1.0 - min_close):
        return False, why + " (closed %.0f%% of the way to A, < %.0f%%)" % (100.0 * (a0 - a1) / a0 if a0 else 0.0, 100 * min_close)
    if (a0 - a1) <= (b0 - b1):
        return False, why + " (closed on the fresh burn B at least as much as on A)"
    return True, why


def _burn_history(t, ticks_ago=HERD_LAG_TICKS):
    r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="ProbeBurnHistory", args=str(ticks_ago))
    if not _live(t):
        return {}
    kv = parse_kv(_ok(r, "ProbeBurnHistory").get("result"))
    if "samples" not in kv:
        _fail("ProbeBurnHistory unreadable: %r" % r)
    return kv


def _probe_herd(t, issue):
    r = t.bridge_call("jawa/static_call", type=FOLLOW_BURN, method="ProbeHerd", args="%s|%s" % (HERD_RACE, str(issue).lower()))
    if not _live(t):
        return {}
    kv = parse_kv(_ok(r, "ProbeHerd").get("result"))
    if "n" not in kv:
        _fail("ProbeHerd unreadable: %r" % r)
    return kv


CALM_SETTLE_TICKS = 60   # one burn-line watch interval after the extinguish: a strike still due would show as Fire


def _calm_sky(t):
    """TESTENV_STORM_FIRES_HARDEN_DECOY_BURN (r6 p4, 2026-10-15): fulgurite_after_lightning (same fixture, run just before)
    left its DryThunderstorm current after the unlock, and the storm's fires (177 burning, centre 176,141) became the burn
    line's newest sample instead of burn B at (220,100): herd_follows_two_day_old_burn read UNMEASURED; alone on a fresh
    reload it PASSed. A row that reads the burn line's history needs a sky that lights nothing but the row's own burns:
    testenv_guards.calm_sky locks Clear, ends the storm tail, puts out every fire and reads back zero stray Fire. A sky
    that will not calm is a SITE fault (UNMEASURED), never a decoy burn read as the mod's answer. Weather is not what this
    row measures (it lights its own burns A and B), so the calm changes nothing the row reads."""
    import testenv_guards  # noqa: E402 - on sys.path via the modcheck package
    r = testenv_guards.calm_sky(t.session, _map_size(t), settle=lambda: _wait(t, CALM_SETTLE_TICKS))
    _note(t, "sky calmed before the burns (weather Clear x2, map extinguished, stray Fire read back)", r)
    if not r.get("verified"):
        _unmeasured(t, "SITE: the sky would not calm before the burns, so a stray fire could be read as burn A or B: %s"
                       % (r.get("error"),))
    return r


def _herd_burn(t, pad, label, size=8):
    """Burn an 8x8 grassed deep-ash patch at `pad` (firebreak-ringed) until the burn line records a sample there."""
    x, z = pad
    rect = (x - size // 2, z - size // 2, size, size)
    _firebreak(t, rect)
    t.bridge_call("jawa/set_terrain", x=rect[0], z=rect[1], terrainDef=DEEP_ASH, width=size, height=size, layer="top")
    _plants(t, "RM_FE_Plant_EmberGrass", rect)
    _fire(t, rect)
    for _ in range(4):   # a sample lands at most HERD_HISTORY_INTERVAL after the previous one; the watch runs every 60 ticks
        _wait(t, 900)
        h = _burn_history(t)
        newest = xz_of(h.get("newest"))
        if not _live(t) or (newest is not None and _dist(newest, pad) <= HERD_ANCHOR_TOL):
            _note(t, "burn history after burn %s" % label, h)
            return h
    _unmeasured(t, "the burn line recorded no sample at burn %s %r within 3600 ticks: %r" % (label, pad, h))


def herd_follows_drive(t):
    """herd_follows_two_day_old_burn, COMPRESSED (design/RimMandrake/debug_process.md "Long-duration properties"): two in-game
    days are never stepped. Decomposed and read in pieces:
      1 anchor (MEASURED): burn A recorded, the burn history BACKDATED by the two-day lag (MapComponent_BurnLine.
        BackdateBurnHistory), burn B recorded fresh; BurnCenterAgo(2 days) must answer A, with B in the history too.
      2 decision (MEASURED): RM_JobGiver_FollowBurn.ProbeHerd reads the giver's own decision for every wild ullai with the
        chance roll set aside: all far from A must go to A; issue=true starts those jobs.
      3 motion (MEASURED): one short step (HERD_STEP_TICKS); the herd centroid closes on A (herd_verdict).
      4 cadence (INFERRED): the giver's chance roll (chancePerCheck 0.04 a think) is skipped; that the herd reaches A by
        itself within two days is inferred from 1-3 plus that cadence, never stepped."""
    if not _live(t):
        return
    _set(t, dict([(f, False) for f in ISOLATION_OFF if f != "burnLineEnabled"] + [("burnLineEnabled", True)]))
    # the calm's Clear lock ends with this row: ullai_and_giant's teardown does not touch the weather, and a lock left
    # behind would sit under every later chain on this fixture
    try:
        _calm_sky(t)
        _herd_burn(t, PAD_HERD_OLD, "A")
        _extinguish(t)
        _wait(t, 120)   # the watch sees no fire, so no sample of A lands after the backdate
        r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="BackdateBurnHistory",
                          args=str(HERD_LAG_TICKS + HERD_HISTORY_INTERVAL))
        shifted = _ok(r, "BackdateBurnHistory").get("result")
        _note(t, "burn history samples backdated by the two-day lag", shifted)
        h = _herd_burn(t, PAD_HERD_NEW, "B")
        _extinguish(t)
        ago = xz_of(h.get("ago"))
        if ago is None or _dist(ago, PAD_HERD_OLD) > HERD_ANCHOR_TOL:
            _fail("BurnCenterAgo(2 days) is %r, not burn A %r (burn B %r is the newest sample %r)"
                  % (h.get("ago"), PAD_HERD_OLD, PAD_HERD_NEW, h.get("newest")))
        hx, hz = HERD_SPAWN
        for i in range(HERD_SIZE):
            _spawn_wild(t, HERD_RACE, hx + (i % 5) - 2, hz + (i // 5) * 2 - 1)
        d = _probe_herd(t, issue=True)
        _note(t, "the giver's decision per wild ullai (chance roll set aside) and the jobs it started", d)
        n = int(d.get("n", 0))
        if n < HERD_SIZE:
            _fail("ProbeHerd saw %d wild %s, %d were spawned: %r" % (n, HERD_RACE, HERD_SIZE, d))
        anchor = xz_of(d.get("anchor"))
        if anchor is None or _dist(anchor, PAD_HERD_OLD) > HERD_ANCHOR_TOL:
            _fail("the giver's anchor is %r, not burn A %r" % (d.get("anchor"), PAD_HERD_OLD))
        if int(d.get("goAnchor", 0)) != n:
            _fail("only %s of %d wild ullai ~150 cells from A decided to go to it: %r" % (d.get("goAnchor"), n, d))
        if int(d.get("issued", 0)) < 0.8 * n:
            _fail("the giver found a target cell for only %s of %d: %r" % (d.get("issued"), n, d))
        start = (float(d["cx"]), float(d["cz"]))
        _wait(t, HERD_STEP_TICKS)
        e = _probe_herd(t, issue=False)
        end = (float(e.get("cx", -1)), float(e.get("cz", -1))) if int(e.get("n", 0)) > 0 else None
        ok, why = herd_verdict(start, end, PAD_HERD_OLD, PAD_HERD_NEW)
        _note(t, "herd motion over %d ticks (INFERRED beyond it: the 0.04 chance cadence brings the herd unforced within two "
                 "days; never stepped)" % HERD_STEP_TICKS, {"start": d, "end": e, "verdict": why})
        if not ok:
            _fail("the herd did not close on the two-day-old burn: " + why)
        t.screenshot()
    finally:
        try:
            _session_call(t, "jawa/weather_set", unlock=True)
        except Exception as e:   # noqa: BLE001 - recorded, never masks the row's own verdict
            _GEN.setdefault("teardown_bad", []).append("herd row weather unlock: %s" % e)


@suite.chain("ullai_and_giant")
@_teardown(fire=True)
def ullai_and_giant(t):
    """PYRELANDS_ULLAI_GIANT_BUILD_1: the ullai herd follows the burn; the furnace-beast is a giant (offline reads +
    live def resolution). Learned 2026-10-03: ash terrain never reverts (now: deep ash is everywhere), so a terrain
    target alone reads every burn ever; the herd reads MapComponent_BurnLine's hourly burn-centre history instead."""
    import os
    import xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    _pad(t, PAD_PROBE)
    with _comp(t, "ullai_wired", toggle="ullaiEnabled"):
        root = ET.parse(os.path.join(here, "Defs", "ThingDefs_Races", "RM_Ullai.xml")).getroot()
        thing = [d for d in root.findall("ThingDef") if d.findtext("defName") == "RM_Ullai"]
        kind = [d for d in root.findall("PawnKindDef") if d.findtext("defName") == "RM_Ullai"]
        if not thing or not kind:   # sanity probe: the instrument reads both defs
            _fail("RM_Ullai ThingDef/PawnKindDef not read")
        terr = [li.text for li in thing[0].iter("li") if li.text and li.text.startswith("RM_FE_Ash_")]
        if terr != [DEEP_ASH]:
            _fail("follow-burn terrains %r are not [%s] (the ash rungs are retired)" % (terr, DEEP_ASH))
        if kind[0].findtext("wildGroupSize") != "8~20" or thing[0].findtext("race/baseBodySize") != "1.8":
            _fail("ullai herd size / body size drifted from the ruling (8~20, bs 1.8)")
        biome = ET.parse(os.path.join(here, "Defs", "BiomeDefs", "Pyrelands.xml")).getroot()
        wa = [b.find("wildAnimals") for b in biome.findall("BiomeDef") if b.findtext("defName") == "RM_Pyrelands"]
        if not wa or wa[0].find("RM_Ullai") is None or wa[0].findtext("RM_FurnaceBeast") != "0.04":
            _fail("RM_Pyrelands roster lacks RM_Ullai or the furnace-beast is not at 0.04")
        tex = os.path.join(here, "Textures", "Things", "Pawn", "Animal", "Pyrelands")
        missing = [f for f in ("Ullai/Ullai_%s.png", "FurnaceBeast/FurnaceBeast_Giant_%s.png")
                   for d in ("south", "east", "north") if not os.path.isfile(os.path.join(tex, f % d))]
        if missing:
            _fail("art facings missing: %r" % missing)
        t.screenshot()
    _independent(t)
    with _comp(t, "giant_furnace_beast", toggle="furnaceBeastGiant"):
        root = ET.parse(os.path.join(here, "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")).getroot()
        fb = [d for d in root.findall("ThingDef") if d.findtext("defName") == "RM_FurnaceBeast"]
        if not fb or fb[0].findtext("race/baseBodySize") != "6":
            _fail("RM_FurnaceBeast is not bs 6 in XML")
        live = _get_defs(t, "ThingDef/RM_Ullai;PawnKindDef/RM_Ullai;ThingDef/RM_FurnaceBeast", "race")
        if _live(t) and len(live) < 2:
            _fail("ullai / furnace-beast defs missing live: %r" % sorted(live))
        t.screenshot()
    _independent(t)
    with _comp(t, "herd_follows_two_day_old_burn"):
        herd_follows_drive(t)


@suite.chain("sand_shovel")
def sand_shovel(t):
    """PYRELANDS_SAND_TERRAIN_YIELD_1 (RM_TerrainDig.cs). The choice: a 'Shovel sand' DIG ORDER (Orders tab, Mining
    work), not a terrain clear-yield -- vanilla has no clear action on natural terrain. RM_FE_Ground_Sand carries
    RM_TerrainDigYieldExtension: 5 glass sand per cell, the cell becomes RM_FE_Ground_Gravel (a finite deposit).
    ProofShovel lays one sand cell on the current map and completes the dig. Not proven here: a miner choosing the
    order (WorkGiver) -- first poke: designate sand on a Pyrelands map with a colonist assigned to Mining."""
    import xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    with t.component("sand_carries_the_dig_yield", beyond_toggle=True):
        root = ET.parse(os.path.join(here, "Defs", "TerrainDefs", "ScorchableGround.xml")).getroot()
        sand = [d for d in root if d.findtext("defName") == "RM_FE_Ground_Sand"]
        if len(sand) != 1:
            _fail("RM_FE_Ground_Sand not found once (sanity probe)")
        ext = sand[0].find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_TerrainDigYieldExtension']")
        if ext is None or ext.findtext("yield") != "RM_GlassSand" or ext.findtext("leaves") != "RM_FE_Ground_Gravel":
            _fail("sand does not dig to RM_GlassSand leaving gravel")
        patch = ET.parse(os.path.join(here, "Patches", "RM_ShovelSand_Orders.xml")).getroot()
        if "RimMandrake.Pyrelands.Designator_RM_ShovelTerrain" not in [li.text for li in patch.iter("li")]:
            _fail("the designator is not added to the Orders tab")
    _independent(t)
    with t.component("shovel_yields_glass_sand_and_leaves_gravel", toggle="sandShovelEnabled"):
        if t.session is None:
            t.upstream_reason = "UNMEASURED: no bridge session"
            t.upstream_failed = True
            return
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.RM_TerrainDigProof", method="ProofShovel")
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        if not text.startswith("SHOVEL"):
            t.upstream_reason = "UNMEASURED: ProofShovel gave no answer: %r" % text[:160]
            t.upstream_failed = True
            return
        for want in ("accepts True", "offRefuses True", "yield RM_GlassSand x5", "terrain RM_FE_Ground_Gravel", "orderGone True"):
            if want not in text:
                _fail("shovel proof missing %r: %s" % (want, text))


@suite.chain("lightning_breaker")
@_teardown(fire=True)
def lightning_breaker(t):
    """PYRELANDS_LIGHTNING_BREAKER_BUILD_1 (RM_LightningBreaker.cs). Live proofs need no Pyrelands site: ProofTrip
    builds battery-conduit-breaker-conduit-battery on the current map and forces a short circuit on A's side.
    The three components read independent state, so each starts clean (_independent)."""
    import re
    import xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    # No clear_area: ProofTrip finds its own free 9x4 near the centre, and the default anchor IS the centre, where the
    # colonists stand (destroy_batch "All" would take them).
    proof = "RimMandrake.Pyrelands.RM_LightningBreakerProof"
    project = "RM_LightningBreakers"

    def need_session(what):
        if t.session is None:
            raise ExpectationFailed("UNMEASURED: no bridge session for %s" % what)

    def call(method, arg):
        need_session(method)
        r = t.bridge_call("jawa/static_call", type=proof, method=method, args=arg)
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("UNMEASURED: static_call %s refused: %s" % (method, str(r)[:200]))
        text = str(r.get("result", ""))
        if text.startswith("UNMEASURED"):
            raise ExpectationFailed("UNMEASURED: %s" % text)
        return text

    def can_start(only):
        """jawa/research_availability with breakerPyrelandsOnly forced to `only` (restored by the teardown)."""
        _set(t, {"breakerPyrelandsOnly": only})
        r = _ok(t.bridge_call("jawa/research_availability", project=project), "research_availability")
        snap = r.get("result") or {}
        if not isinstance(r.get("canStartNow"), bool) or not isinstance(snap.get("progress"), (int, float)):
            _fail("research_availability(%s) unreadable: %s" % (project, str(r)[:200]))
        return r["canStartNow"], snap

    with t.component("metal_and_sand_at_the_forge", beyond_toggle=True):
        root = ET.parse(os.path.join(here, "Defs", "LightningBreaker", "RM_LightningBreaker.xml")).getroot()
        defs = {(d.tag, d.findtext("defName")): d for d in root}
        if len(defs) != 4:   # sanity probe: research, core, recipe, building
            _fail("read %s" % sorted(defs))
        recipe = defs[("RecipeDef", "RM_Make_LightningBreakerCore")]
        users = [li.text for li in recipe.findall("recipeUsers/li")]
        ings = [li.findtext("filter/thingDefs/li") for li in recipe.findall("ingredients/li")]
        if not set(users) & {"FueledSmithy", "ElectricSmithy"} or sorted(ings) != ["RM_GlassSand", "Steel"]:
            _fail("recipe is not metal and sand at the smithy: users %r ingredients %r" % (users, ings))
        b = defs[("ThingDef", "RM_LightningBreaker")]
        if b.findtext("thingClass") != "RimMandrake.Pyrelands.RM_LightningBreaker" or \
                b.find("comps/li[@Class='CompProperties_Power']/transmitsPower") is None:
            _fail("breaker is not a power-transmitting RM_LightningBreaker")
    _independent(t)
    with t.component("research_only_in_the_pyrelands", toggle="breakerPyrelandsOnly"):
        root = ET.parse(os.path.join(here, "Defs", "LightningBreaker", "RM_LightningBreaker.xml")).getroot()
        rp = [d for d in root.findall("ResearchProjectDef") if d.findtext("defName") == project]
        if len(rp) != 1:
            _fail("ResearchProjectDef %s not read once (sanity probe): %d" % (project, len(rp)))
        if rp[0].find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_PyrelandsOnlyResearch']") is None:
            _fail("the research carries no Pyrelands-only gate")
        with open(os.path.join(here, "Source", "RM_LightningBreaker.cs"), encoding="utf-8") as f:
            src = f.read()
        if "PropertyGetter(typeof(ResearchProjectDef), nameof(ResearchProjectDef.CanStartNow))" not in src:
            _fail("CanStartNow is not gated")
        # The live gate is read as the DIFFERENCE it makes: CanStartNow with the setting off (vanilla's own
        # verdict) against CanStartNow with it on. A project vanilla already refuses (no bench, prerequisites)
        # or one already begun (the gate exempts progress > 0) cannot show the gate at all.
        need_session("the live research gate")
        m = re.match(r"GATE canStart=(\w+) holdsPyrelands=(True|False) gated=(\w+)", call("ProofGate", project))
        if not m:
            _fail("ProofGate answer unparsed")
        if m.group(3) != "True":
            _fail("the live ResearchProjectDef carries no RM_PyrelandsOnlyResearch: gated=%s" % m.group(3))
        holds = m.group(2) == "True"
        ungated, snap = can_start(False)
        gated, _ = can_start(True)
        _note(t, "research gate", {"holdsPyrelands": holds, "canStartUngated": ungated, "canStartGated": gated,
                                   "project": snap})
        if snap.get("isFinished") or snap["progress"] > 0:
            raise ExpectationFailed("UNMEASURED: %s is finished or begun (progress %r), which the gate exempts "
                                    "by design" % (project, snap["progress"]))
        if not ungated:
            raise ExpectationFailed("UNMEASURED: vanilla already refuses %s here (bench, prerequisites, "
                                    "techprints), so the gate's own refusal cannot be seen" % project)
        if gated != holds:
            _fail("with breakerPyrelandsOnly on, %s can start=%s while the player holds a Pyrelands home=%s"
                  % (project, gated, holds))
    _independent(t)
    with t.component("short_circuit_trips_and_spares_the_far_side", toggle="lightningBreakerEnabled"):
        need_session("ProofTrip")
        _set(t, {"lightningBreakerEnabled": True})   # this component's own state; restored by the teardown
        text = call("ProofTrip", "x")
        m = re.search(r"oneNetBefore=True tripped=True storedA=(\d+) storedB=(\d+) splitAfter=True", text)
        if not m or int(m.group(1)) > 1 or int(m.group(2)) < 500:
            _fail("trip: %s" % text[:240])
        t.screenshot()
