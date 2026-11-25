"""validation.py -- modcheck suite for RimMandrake Pyrelands.

Plan: design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md. Walk:
design/validation_walks/RimMandrake/Pyrelands.md (19 must-show bars, 1 cannot-show).

PACKAGING. This dev folder (`src/RimMandrake/Pyrelands`, packageId `mandrake.rm.pyrelands`) is
the SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes` (Biomes.compose.json,
wave 2), so the thing a run must load is `mandrake.rm.biomes` plus `mandrake.rut.patches` (the
fauna roster) and `mandrake.rsw.swbestiary` (seven roster keys; the MayRequire on that patch
Operation is inert, so the list must carry it). The Tribes mod `mandrake.rut.pyrelandsmechanics`
stays OFF the list (version 0.1.0 is the biome alone; the pyrelands tier forbids it). `modcheck run Pyrelands` appends the DEV folder's packageId with
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

Fire hygiene: every fire burns on its own pad, ringed by a vanilla floor (concrete). Pads sit away
from the colonists at the map centre.

Teardown (`@_teardown`): settings fields are `public static`
(RimMandrake.Pyrelands.RM_PyrelandsSettings), flipped through `_set`, which remembers each
field's prior value. Every stateful chain ends by unlocking the weather (and moving it to Clear twice, so no storm
tail ticks on), extinguishing the whole map and restoring those values through the session itself, because t.bridge_call is a no-op once a
component has failed or gone UNMEASURED. A teardown step that does not take is its own FAIL
component (`teardown`), so leaked state can never sit under an all-PASS run.

Not expressible with current bridge tools: forcing one `WeatherEvent_LightningStrike`
(a lightning strike cannot be forced), reading
`MapComponent_BurnLine` directly (burn_line_present counts free-standing Fire, which is exactly
what that component measures), and flyer flight (firehawk_carries_ember reads job state only;
flyers are never live-tested unattended).
"""
import contextlib
import functools
import importlib.util
import json
import os
import re
import sys
import time

from modcheck import Suite, Component, ExpectationFailed

suite = Suite("Pyrelands")
suite.toggles = ["ashDustingEnabled", "scorchFruitEnabled",
                 "ashfallAccumulationEnabled", "biomeGenerationEnabled",
                 "ullaiEnabled", "ullaiHerdSizeMultiplier", "furnaceBeastGiant",
                 "sandShovelEnabled", "sandShovelYieldMultiplier"]

SETTINGS = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
SOIL = "RM_FE_Ground_Soil"
FIREBREAK = "Concrete"
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
ASH_FIELD = "RimMandrake.Pyrelands.MapComponent_PyrelandsAshField"     # jawa/static_call probes (PyrelandsAshField.cs)
# Ash on the ground is Odyssey's sand depth since 2026-11-08 (owner by card, "Rebuild ash on vanilla sand?" -> "Yes"), not a
# thing: list_things cannot see it. PyrelandsAsh.ProbeAsh reads it, ClearAsh zeroes it (Source/PyrelandsAshSand.cs).
ASH_SAND = "RimMandrake.Pyrelands.PyrelandsAsh"
STOCK_GROUND = ("Sand", "Soil", "Gravel", "SoilRich")
ORDINARY_RAIN = ("Rain", "RainyThunderstorm", "FoggyRain")
# Mechanics that must be OFF during the controlled bars (plan 2.3a isolation).
ISOLATION_OFF = ["burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled",
                 "burrowOnFireEnabled",
                 "furnaceThermalEnabled"]
FIRE_HAWK_JOB = "RM_FireHawkCarryEmber"   # JobDefs/RM_PyrelandsJobs.xml (renamed from RUT_)
EMBER_DRIVER = "RimMandrake.Pyrelands.JobDriver_RUT_FireHawkCarryEmber"   # ProbeFlight: the flight-tracker state read

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
PAD_DOME = (60, 60)        # heat_dome: no ground fire on this pad, so only the heat hit can dome the ashwallow
PAD_ROOMS = (160, 90)
PAD_PROBE = (225, 225)
PAD_HERD_OLD = (30, 100)   # herd_follows_two_day_old_burn: burn A, backdated two days
PAD_HERD_NEW = (220, 100)  # burn B, fresh: present in the history and NOT the anchor
PAD_SLEEP = (220, 160)     # furnace_sleep: a beast asleep in grass lights it (owner card 2026-11-08 01:01)
HERD_SPAWN = (125, 215)    # the wild ullai herd starts ~150 cells from A and ~140 from B
HERD_SIZE = 10
HERD_RACE = "RM_Ullai"
HERD_LAG_TICKS = 2 * 60000      # RM_FollowBurnExtension.lagDays 2 (Defs/ThingDefs_Races/RM_Ullai.xml)
HERD_HISTORY_INTERVAL = 2500    # MapComponent_BurnLine.BurnHistoryIntervalTicks
HERD_PACE_SAMPLE_TICKS = 1000   # the herd's first stretch, read per ullai: its pace on deep ash, measured on the site
HERD_PACE_MARGIN = 2.0          # the centroid lags the walkers: one with no reachable cell, a RM_ShadeDash at noon (visit 1)
HERD_STEP_MAX_TICKS = 15000     # the paced window's ceiling (a quarter day); a pace that needs more is a verdict, never a clip
HERD_STEP_ROUND = 250           # the window is rounded up to this
HERD_MIN_CLOSE = 0.3            # share of its start distance to A the herd centroid must close in that step
HERD_ANCHOR_TOL = 8             # cells: the recorded centroid of an 8x8 burn sits inside it
BURN_LINE = "RimMandrake.Pyrelands.MapComponent_BurnLine"
FOLLOW_BURN = "RimMandrake.Pyrelands.RM_JobGiver_FollowBurn"
BURN_QUIET_TICKS = 120000      # PyrelandsTuning.StandingBurnQuietTicks (selftest_pyrelands_site pins both to the C#)
BURN_WATCH_TICKS = 60          # PyrelandsTuning.BurnWatchIntervalTicks
BURN_RETRY_TICKS = 2500        # PyrelandsTuning.StandingBurnRetryTicks
BURN_STAGED_WAIT_TICKS = 6 * BURN_WATCH_TICKS + 4 * BURN_RETRY_TICKS   # after _stage_quiet: the watch intervals and four reseed retries
COMMON_GRAZERS = ("RM_Ullai", "RM_Ashwallow", "RSW_Nuna", "RSW_Iriaz", "RSW_Gizka")
BIG_PREDATORS = ("RM_Flamefang", "RM_Barbslinger", "RM_Emberscythe", "RM_Sytheclaw", "RSW_Anooba", "RSW_Orray", "RSW_Dalgo")
REGROW_SAMPLE_DAYS = (3, 7)
REGROW_FIRST_DAYS_FRAC = 0.25
# Ceiling (Conductor, 2026-11-07: "too-fast can never fail it"): a scar already more than half green at day 3 was largely green
# well before "about a week". Map q measured 56% two days after its burn, which read as grass on dark soil, not a burn.
REGROW_FIRST_DAYS_MAX = 0.55
REGROW_WEEK_FRAC = 0.6
REGROW_BURN_TICKS = 5000   # kill the grass (~3500-4500 ticks)
FIRE_PADS = (PAD_FIRE_TICK, PAD_ASH, PAD_REGROW, PAD_FIRE_BORN, PAD_HAWK, PAD_BURROW, PAD_BURN, PAD_HERD_OLD, PAD_HERD_NEW,
             PAD_SLEEP)
DEEP_ASH_MIN = 0.85        # pyre_ground_deep_ash: deep ash share of open land on a fresh map (PROVISIONAL, design §2)
WATERED_MIN_GAIN = 0.5     # pyre_ash_fertile_when_watered: watered minus dry FertilityAt (shipped 1.40 vs 0.70)
BURN_BONUS_MIN = 0.3       # pyre_fresh_burn_feeds_the_field: bonus right after a burn (shipped +0.50)
RUIN_SAMPLES = 10
RUIN_ASH_MIN = 0.9    # the sweep lays deep ash or chars the floor on every non-water footprint+rim cell (3x3 sits inside)
RUIN_FILTH_MIN = 0.3  # share of sampled ruins carrying ash in their 3x3
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


def _hediff_rows(row):
    """Pure. A vitals row's hediffs as {(def, part): (severity, text)}; None when the read carried no health."""
    hs = (row or {}).get("hediffs")
    if hs is None:
        return None
    out = {}
    for h in hs:
        if not isinstance(h, dict) or not h.get("def"):
            continue
        sev = h.get("severity")
        sev = float(sev) if isinstance(sev, (int, float)) else None
        text = str(h.get("def")) + ("" if sev is None else " %.2f" % sev)
        if h.get("part"):
            text += " on " + str(h.get("part"))
        if h.get("lastInjury"):
            text += " (by %s)" % h.get("lastInjury")
        out[(h.get("def"), h.get("part"))] = (sev, text)
    return out


def harm_cause(b, a):
    """Pure. -> ' (cause ...)': what the AFTER read shows that the BEFORE read did not, for a pawn the row downed or
    killed. HARNESS_REPAIR_CAUSE_F6CADE57_2: a RESTART that named no cause left MOD, SITE and HARNESS undecidable from
    the sighting. New or worse hediffs first, by severity; then the pawn's mental state. UNREAD when no health was read."""
    if a is None:
        return " (cause UNREAD: the pawn is on no list, corpses included)"
    after, before = _hediff_rows(a), _hediff_rows(b)
    if after is None:
        return " (cause UNREAD: the vitals read carried no health)"
    before = before or {}
    worse = [(sev or 0.0, text) for k, (sev, text) in after.items()
             if k not in before or (sev or 0.0) > (before[k][0] or 0.0) + 1e-6]
    worse.sort(key=lambda x: -x[0])
    parts = ["new or worse: " + (", ".join(t for _, t in worse[:5]) if worse else "none")]
    if not worse and after:
        parts.append("hediffs: " + ", ".join(t for _, t in sorted(after.values(), key=lambda x: -(x[0] or 0.0))[:5]))
    if isinstance(a.get("bleed"), (int, float)) and a["bleed"] > 0:
        parts.append("bleeding %.2f" % a["bleed"])
    if a.get("mental"):
        parts.append("mental state: %s" % a.get("mental"))
    return " (cause read: %s)" % "; ".join(parts)


def vitals_damage(before, after):
    """Pure. before/after: {pawn id: {"dead": bool, "downed": bool, "food": float|None, "hediffs": [...]|absent,
    "mental": str|None}}. -> [reason, ...]; empty = intact.
    Damage to the test itself (a colonist that was alive and is dead, newly downed, or starving) means the row's evidence
    is void: it is RESTARTED, not scored. A death or a fall carries harm_cause(): what the health read says did it."""
    why = []
    for pid, b in sorted(before.items()):
        if b.get("dead"):
            continue
        a = after.get(pid)
        if a is None or a.get("dead"):
            why.append("%s died during the row%s" % (pid, harm_cause(b, a)))
            continue
        if a.get("downed") and not b.get("downed"):
            why.append("%s was downed during the row%s" % (pid, harm_cause(b, a)))
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
    # includeHealth + includeCorpses: a downed or dead colonist's hediffs name what did it (harm_cause); a corpse is a
    # dead row, never an absent one.
    r = t.session.call("jawa/list_pawns", faction="player", includeHealth=True, includeCorpses=True, limit=100) or {}
    out = {}
    for p in r.get("pawns") or []:
        if not p.get("id"):
            continue
        row = {"dead": bool(p.get("dead")), "downed": bool(p.get("downed")), "food": None,
               "mental": p.get("mentalState")}
        health = p.get("health")
        if isinstance(health, dict) and isinstance(health.get("hediffs"), list):
            row["hediffs"] = health["hediffs"]
            row["bleed"] = health.get("bleedRate")
        if not row["dead"]:
            for n in (t.session.call("jawa/pawn_need", pawn=p["id"], action="list") or {}).get("needs") or []:
                if n.get("need") == "Food":
                    row["food"] = n.get("level")
        out[p["id"]] = row
    return out


def _hostiles_seen(t):
    """One line: the hostile pawns on the current map when a row damaged the colony (def and mental state), so a RESTART
    names an attacker if there was one. 'hostiles UNREAD' when the call fails: never 'none'."""
    try:
        r = t.session.call("jawa/list_pawns", faction="hostile", limit=20) or {}
    except Exception as e:                               # noqa: BLE001 - a note, never a crash
        return "hostiles UNREAD (%s)" % type(e).__name__
    if not isinstance(r, dict) or r.get("success") is False or not isinstance(r.get("pawns"), list):
        return "hostiles UNREAD (%r)" % (str(r)[:80],)
    rows = [p for p in r["pawns"] if not p.get("dead")]
    if not rows:
        return "hostiles on the map: none"
    return "hostiles on the map: " + ", ".join("%s%s" % (p.get("def") or p.get("id"),
                                                         "(%s)" % p["mentalState"] if p.get("mentalState") else "")
                                               for p in rows[:6])


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


def _subject_row(t, pid):
    """The pawn's list_pawns row with health, corpses included, so a dead subject reads dead rather than absent (an absent
    row read as 'the hediff is gone' would pass a patient the venom killed). None only when it is on no list."""
    r = t.bridge_call("jawa/list_pawns", includeHealth=True, includeCorpses=True, limit=500)
    if not _live(t):
        return None
    for p in (_ok(r, "list_pawns").get("pawns") or []):
        if p.get("id") == pid:
            return p
    return None


def _retire_venom_patients(t):
    """The ids of every living colonist that carries the venom (the earlier rows' patients). They stay where they are:
    killing them first (visit 3, a 5000-damage shot) downed one instead, and the wait-out's own bite then never landed
    in 6030 ticks. The wait-out reads them as no subjects of its own (_GEN["not_subjects"])."""
    r = t.bridge_call("jawa/list_pawns", includeHealth=True, limit=500)
    if not _live(t):
        return []
    return [p["id"] for p in (_ok(r, "list_pawns").get("pawns") or [])
            if p.get("isPlayer") and not p.get("dead") and _has_hediff(p, VENOM)]


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail
    names the real reason, and the chain is not poisoned for an independent next component."""
    before = t.upstream_failed
    t._why = None
    _r6_log_calls(t)
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
        measured = _GEN.pop("measured_death", None)
        if measured:   # the row's own subject: its death or fall is what the row measures, not damage to the test
            damage = [d for d in damage if not d.startswith(measured + " ")]
        for other in _GEN.pop("not_subjects", None) or []:   # pawns retired before the row, not part of it
            damage = [d for d in damage if not d.startswith(other + " ")]
        if damage:   # who else stood on the map: a mad animal reads hostile (list_pawns hostile = HostileTo(player))
            damage = damage + [_hostiles_seen(t)]
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
    real clock (helpers.fast_advance), then pause; the overshoot is recorded, a stall is stepped."""
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
    import helpers as H   # noqa: E402 - modcheck puts its own directory on sys.path
    # MODCHECK_ULTRAFAST_CLOCK_STALL_1: rimworld/set_time_speed left the game PAUSED (no Ultrafast wait in 47 modcheck
    # results ever moved the clock); helpers.fast_advance drives rimworld/play_for, then pauses. A refused or stalled
    # fast run is recorded and the rest is stepped exactly below.
    start, now, why = H.fast_advance(s, n)
    if start is None:
        raise ExpectationFailed("clock unreadable before a %d-tick wait" % n)
    target = start + n
    if why:
        t._record("_wait(%d): fast run stopped (%s); stepping the rest" % (n, why), now)
    now = s._ticks()
    if now is None:
        raise ExpectationFailed("clock unreadable after a %d-tick wait" % n)
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
    if r.get("mapBiome") == "RM_Pyrelands":
        return
    # PYRELANDS_SITE_DIAGNOSE_WRONG_BIOME_TWICE (3 testq jobs, map 1 read RM_TheRot / AridShrubland): the site was never
    # recorded and map 1 is not it. Ask the game which loaded map IS Pyrelands (set_current_map refuses an unknown id
    # and lists loadedMaps) instead of assuming map 1; with none loaded the run could not ask -> UNMEASURED SITE.
    probe = t.session.call("jawa/set_current_map", mapId=-1) or {}
    # the refusal carries the list under `details` (JawaBenchMapInfoTools.cs Fail); the top-level read saw [] on every
    # SteveDesktop job of 2026-11-13 while map 1 existed
    loaded = probe.get("loadedMaps") or (probe.get("details") or {}).get("loadedMaps") or []
    pyre = [m.get("mapId") for m in loaded if m.get("biome") == "RM_Pyrelands"]
    if pyre:
        t.session.call("jawa/set_current_map", mapId=pyre[0])
        r = t.session.call("jawa/map_info") or {}
        t._record("on_site: found the Pyrelands site among loaded maps", {"mapId": pyre[0], "loaded": loaded})
        if r.get("mapBiome") == "RM_Pyrelands":
            _GEN["site_map"] = pyre[0]
            return
    # RIMMANDRAKE_LOAD_PYRELANDS_SITE_IN_TESTQ_CHAINS_RAN_BOREAL: no Pyrelands map is loaded at all (a testq job on a
    # foreign BorealForest map, 2026-11-13, six chains UNMEASURED SITE): load the registered site once per run
    if not _GEN.get("site_load_tried"):
        _GEN["site_load_tried"] = True
        mid, _GEN["site_load_why"] = _load_registered_site(t)
        if mid is not None:
            _GEN["site_map"] = mid
            return
    loaded_why = _GEN.get("site_load_why")      # every later chain of the run names the same failed load
    raise ExpectationFailed("UNMEASURED SITE: could not make a Pyrelands site current (tried map %s, read %r; "
                            "loadedMaps %r)%s" % (site, r.get("mapBiome"), loaded,
                                                  "; the registered site load: %s" % loaded_why if loaded_why else ""))


def _site_registry():
    """test_site_saves.json (Utils/modcheck): what each site save is, where it was built and how it loads."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils", "modcheck", "test_site_saves.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _northstar_site():
    """Pyrelands/northstar_site.py, the site's own loader (test_site_saves.load_site refuses Pyrelands and points here)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "northstar_site.py")
    spec = importlib.util.spec_from_file_location("pyre_northstar_site_for_suite", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_registered_site(t):
    """Load the registered Pyrelands site save (test_site_saves.json `pyrelands`) through northstar_site.reload_fixture:
    main menu, load_game, settle (name the colony, site current, queue cleared, 1500 ticks). -> (mapId, None) when a
    RM_Pyrelands map is current after it, else (None, why)."""
    try:
        entry = (_site_registry() or {}).get("pyrelands") or {}
    except (OSError, ValueError) as ex:
        return None, "test_site_saves.json unreadable (%s: %s)" % (type(ex).__name__, ex)
    if not entry.get("save") or entry.get("tile") is None:
        return None, "no registered pyrelands site (save and tile) in test_site_saves.json"
    try:
        # ignore_mods: a registered site is a fixture whose header is not the running list's (SteveDesktop has no
        # owlchemist.cherrypicker; test_site_saves.load_site loads its sites the same way); the RM_Pyrelands read-back
        # below verifies it (RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE)
        mi = _northstar_site().reload_fixture(t.session, entry["save"], entry["tile"], map_id=entry.get("mapId"),
                                              ignore_mods=True)
    except Exception as ex:  # noqa: BLE001 - a load that fails is the reason the row is UNMEASURED, said in it
        return None, "loading %s failed: %s: %s" % (entry["save"], type(ex).__name__, str(ex)[:240])
    t._record("on_site: loaded the registered site %s" % entry["save"], mi)
    if (mi or {}).get("mapBiome") != "RM_Pyrelands":
        return None, "%s loaded but the current map is %r, not RM_Pyrelands" % (entry["save"], (mi or {}).get("mapBiome"))
    return mi.get("mapId"), None


SAVE_LOAD_BUDGET_S = 420    # a site save's load on the 18-mod tier lands in about 10 s; the ceiling is reload_fixture's own


def _load_site_save(t, name):
    """Load a save this run took on the site (ashground_noon, skies_noon, ...) and wait until its map is current.

    A raw rimworld/load_game answers "queued": the old map stays Playing for seconds, and loading over a live game can
    NRE in the teardown (northstar_site.reload_fixture). MEASURED 2026-11-20 visit 2: ash_fall_vs_clear_by_hour read
    its three colonists "died during the row" and the next chain found loadedMaps [] after two raw loads. So: main
    menu, load, await map_ready (await_lifecycle), name the colony, make the site current, clear the queue and re-apply
    the quiet profile (a load resets the storyteller). No settle ticks: the saved clock hour is what the rows compare."""
    if t.session is None or t.upstream_failed or not callable(getattr(t.session, "call", None)):
        # offline declaration, a failed chain (bridge_call is then a no-op) or a selftest's fake session
        return t.bridge_call("rimworld/load_game", saveName=name)
    utils = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
    if utils not in sys.path:
        sys.path.append(utils)
    from await_lifecycle import await_lifecycle  # noqa: E402
    s = t.session
    if await_lifecycle(s.call, "menu", 1.0).ok is False:
        try:
            s.call("rimworld/go_to_main_menu")
        except Exception:  # noqa: BLE001 - the menu wait below judges it
            pass
        lc = await_lifecycle(s.call, "menu", 180.0)
        if not lc.ok:
            _unmeasured(t, "could not reach the main menu to load %s: %s" % (name, lc.reason))
    r = t.bridge_call("rimworld/load_game", saveName=name) or {}
    if r.get("success") is False:
        _unmeasured(t, "rimworld/load_game %s refused: %s" % (name, str(r)[:200]))
    lc = await_lifecycle(s.call, "map_ready", SAVE_LOAD_BUDGET_S, settle=True)
    if not lc.ok:
        _unmeasured(t, "load of %s did not land within %ds: %s" % (name, SAVE_LOAD_BUDGET_S, lc.reason))
    _GEN["named"] = None
    _on_site(t)
    s.call("jawa/incident_queue_clear")
    try:
        _northstar_site()._QS().site_profile_receipt(s, "pyrelands_load_%s" % name)
    except Exception as ex:  # noqa: BLE001 - the profile is housekeeping; its failure is recorded, never a verdict
        t._record("quiet profile after load of %s raised %s" % (name, type(ex).__name__), str(ex)[:200])
    t._record("loaded %s and its map is current" % name, s.call("jawa/map_info"))


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


# --------------------------------------------------------------------------- framing a capture on its subject
# RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT: every capture names its rect. A capture with no rect jumps the camera
# to the anchor at whatever zoom the last call left; every chain below anchors on PAD_PROBE, so on visit 2 (2026-11-20) 20
# captures were one east-edge frame with no subject in it (no furnace-beast, no herd), and judge_cli.py judges a component's
# LAST capture as the picture of each bar its shows= claims. selftest_pyrelands_frames_subject.py holds this rule.
FRAME_PAD = 3       # cells of ground around a subject, so the subject's edge is not the frame's edge (our choice)
FRAME_MIN = 12      # the smallest side: the 12x12 cell shots of this file (burrow, dome) read one pawn plainly (visit 2)
FRAME_CLUSTER = 24  # the window a scattered subject (fires, wild animals, ruins) is framed in: one TEST_SIZE pad
SKY_FRAME = 2 * TEST_SIZE   # a sky capture: a pad and the same again of open ground, so the sky has land to dim (our choice)


def frame_rect(cells, map_size, pad=FRAME_PAD, min_side=FRAME_MIN):
    """Pure. Cells [(x, z), ...] -> (x, z, w, h): their bounding box grown by `pad`, at least `min_side` a side, inside the
    map. None for no readable cell: a subject that is not on the map is never framed as if it were."""
    pts = [(int(round(float(c[0]))), int(round(float(c[1])))) for c in cells or ()
           if c is not None and c[0] is not None and c[1] is not None]
    if not pts:
        return None
    sx, sz = map_size
    x0, x1 = min(p[0] for p in pts) - pad, max(p[0] for p in pts) + pad + 1
    z0, z1 = min(p[1] for p in pts) - pad, max(p[1] for p in pts) + pad + 1
    w, h = x1 - x0, z1 - z0
    if w < min_side:
        x0, w = x0 - (min_side - w) // 2, min_side
    if h < min_side:
        z0, h = z0 - (min_side - h) // 2, min_side
    return inside_map((x0, z0, w, h), map_size)


def inside_map(rect, map_size):
    """Pure. (x, z, w, h) -> the same size slid back inside the map; a side longer than the map is the whole map's side."""
    x, z, w, h = rect
    sx, sz = map_size
    w, h = min(w, sx), min(h, sz)
    return max(0, min(x, sx - w)), max(0, min(z, sz - h)), w, h


def densest_cluster(cells, side):
    """Pure. -> the cells in the busiest side x side window of a grid laid from (0, 0); a tie goes to the lowest window
    (z, then x). [] for no readable cell."""
    bins = {}
    for c in cells or ():
        if c is None or c[0] is None or c[1] is None:
            continue
        x, z = int(round(float(c[0]))), int(round(float(c[1])))
        bins.setdefault((z // side, x // side), []).append((x, z))
    if not bins:
        return []
    best = min(bins, key=lambda k: (-len(bins[k]), k))
    return bins[best]


def _whole_rect(t):
    sx, sz = _map_size(t)
    return 0, 0, sx, sz


def _frame(t, cells, cluster=None):
    """The rect of `cells` (their densest `cluster` window first, when given) on this map; the whole map when none is
    readable (offline, or a subject the state read already failed on)."""
    size = _map_size(t)
    if cluster:
        cells = densest_cluster(cells, cluster)
    return frame_rect(cells, size) or (0, 0, size[0], size[1])


def _sky_rect(t):
    """A sky capture: SKY_FRAME square on the anchor, inside the map."""
    x, z = t.anchor
    return inside_map((x - SKY_FRAME // 2, z - SKY_FRAME // 2, SKY_FRAME, SKY_FRAME), _map_size(t))


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


def _ash(t, rect=None):
    """The ash (sand depth) over `rect` ('x,z,w,h') or the whole map -> {cells, ashed, deep, depthSum, max, ashMap, ...};
    ashed = cells at the visible depth (0.03) or deeper. {} offline. Raises on an unreadable result."""
    r = t.bridge_call("jawa/static_call", type=ASH_SAND, method="ProbeAsh", args=rect or "all")
    if not _live(t):
        return {}
    _ok(r, "ProbeAsh(%s)" % (rect or "all"))
    out = {}
    for part in str(r.get("result") or "").split(";"):
        k, _, v = part.partition("=")
        try:
            out[k] = float(v) if "." in v else int(v)
        except ValueError:
            out[k] = v
    if "ashed" not in out or not out.get("cells"):
        _fail("ProbeAsh(%s) unreadable: %r" % (rect or "all", r))
    return out


def _clear_ash(t):
    """Every cell of the current map to no ash (PyrelandsAsh.ClearAsh); the cleared count, or None offline."""
    r = t.bridge_call("jawa/static_call", type=ASH_SAND, method="ClearAsh")
    return (r or {}).get("result") if _live(t) else None


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
    for k in ("fertility", "bonus", "base", "wateredFertility"):
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


def _charred(t, rect):
    """PyrelandsAsh.ProbeCharred over `rect` ('x,z,w,h') -> {cells, floors, charred}: built floors and those carrying the
    RM_FE_Charred paint (the ruin genstep's CharFloor). {} offline. Raises on an unreadable result."""
    r = t.bridge_call("jawa/static_call", type=ASH_SAND, method="ProbeCharred", args=rect)
    if not _live(t):
        return {}
    _ok(r, "ProbeCharred(%s)" % rect)
    out = {}
    for part in str(r.get("result") or "").split(";"):
        k, _, v = part.partition("=")
        if v.isdigit():
            out[k] = int(v)
    if "charred" not in out or not out.get("cells"):
        _unmeasured(t, "ProbeCharred(%s) unreadable (is this Pyrelands DLL deployed?): %r" % (rect, r))
    return out


def ruin_scorched_share(terrain, charred):
    """Share of ruin-sample cells that read scorched: deep ash, water (never ashed), or a floor the genstep kept and painted
    RM_FE_Charred. `terrain` {def: cells} over the samples, `charred` the charred-floor cells among them. None on no cells."""
    total = sum(terrain.values())
    if total <= 0:
        return None
    ash = sum(v for k, v in terrain.items() if k == DEEP_ASH or "Water" in k)
    return float(min(total, ash + charred)) / total


def _terrain(t, rect):
    """{terrainDef: cells} over rect, or {} offline."""
    r = t.bridge_call("jawa/get_terrain_batch", rects=rect)
    if not _live(t):
        return {}
    _ok(r, "get_terrain_batch(%s)" % rect)
    want = _rect_union_cells(rect)
    if r.get("cellsRead") != (want if want is not None else r.get("cellsRequested")):
        _fail("get_terrain_batch(%s) read %r of %r distinct cells (%r requested)" % (rect, r.get("cellsRead"), want,
                                                                                   r.get("cellsRequested")))
    return _ops_counts(r.get("ops"))


def _rect_union_cells(rects):
    """Distinct cells in 'x,z,w,h;...' (out-of-map cells included, so a rect off the map still reads short), or None
    when a part does not parse. get_terrain_batch reads a cell twice-requested once (overlapping rects are legal), so its
    cellsRead is the union, never the summed areas (HARNESS, Pyrelands visit 5, 2026-11-22: two ruin samples 1 cell apart
    overlapped by 2 cells and sc_ruins failed 'read 88 of 90 cells' on a site where every cell was read)."""
    cells = set()
    for part in str(rects or "").split(";"):
        if not part.strip():
            continue
        try:
            x, z, w, h = [int(v) for v in part.split(",")]
        except ValueError:
            return None
        cells.update((x + i, z + j) for i in range(w) for j in range(h))
    return len(cells)


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
    """Ring `rect` with a non-flammable vanilla floor and strip its plants."""
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


def _open_ground(t, rect, margin=0, soil=None):
    """Make `rect` (grown by `margin`) open ground whatever the map put there, then read it back: every thing destroyed
    (natural rock, a ruin's walls and furniture, plants), the roof taken off, `soil` (default: the whole cleared rect)
    re-laid as SOIL. UNMEASURED, never a verdict, when a thing, a roof or another terrain is left.
    SITE (Pyrelands visit 6, 2026-11-22, ArchSmall, site tile 38): the pads are fixed cells. scorchfruit_off_burn_bears_none
    fell on solid marble (144 Marble rocks under a rock roof; _soil did not take and every cell refused ember grass), and
    the firefoam pad held an ancient shrine (a grand stele, 11 walls, an urn, a door). Both rows read FAIL on 'map_fire
    started no fire', a fault of the scene, not of the mod."""
    x, z, w, h = rect
    big = (x - margin, z - margin, w + 2 * margin, h + 2 * margin)
    soil = soil or big
    t.bridge_call("jawa/destroy_batch", rects=_rs(big), categories="All")
    t.bridge_call("jawa/set_roof_batch", ops="None:%s" % _rs(big))
    _soil(t, soil)
    if not _live(t):
        return
    ex = t.bridge_call("jawa/export_things", rect=_rs(big), includePawns=False, includeItems=True, limit=5000)
    left = [str(th.get("def")) for th in (ex or {}).get("things") or []] if isinstance(ex, dict) else None
    terr = _terrain(t, _rs(soil))
    ci = t.bridge_call("rimworld/get_cells_info", x=big[0], z=big[1], width=big[2], height=big[3])
    roofed = [c for c in (ci or {}).get("cells") or [] if c.get("roof")]
    bad = []
    if left is None:
        bad.append("export_things unreadable: %r" % str(ex)[:160])
    elif left:
        bad.append("%d thing(s) still stand: %r" % (len(left), sorted(set(left))[:8]))
    if set(terr) != {SOIL}:
        bad.append("terrain %r, not all %s" % (terr, SOIL))
    if roofed:
        bad.append("%d cell(s) still roofed" % len(roofed))
    _note(t, "open ground %s (margin %d)" % (_rs(rect), margin), {"left": left, "terrain": terr, "roofed": len(roofed)})
    if bad:
        _unmeasured(t, "SITE: %s could not be made open ground: %s" % (_rs(big), "; ".join(bad)))


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


class _NoGame(RuntimeError):
    """A teardown call refused because no game is loaded (state.hasCurrentGame False): nothing map-bound exists to
    leak into a later chain (RIMMANDRAKE_CLASS_PYRE_TEARDOWN_NO_GAME_UNMEASURED_FOUR_RINGS)."""


def _session_call(t, tool, **kw):
    """A teardown call made on the session itself. t.bridge_call is a no-op once a component has failed
    (TestContext._guard), which is exactly when a fire or a locked weather most needs clearing."""
    r = t.session.call(tool, **kw)
    if not isinstance(r, dict) or r.get("success") is False:
        if isinstance(r, dict) and (r.get("state") or {}).get("hasCurrentGame") is False:
            raise _NoGame("%s refused with no game loaded: %r" % (tool, r))
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
            # keeps lastWeather (lightning included) ticking for WeatherManager.TransitionTicks; a storm then lit
            # 177 fires that the next chain's burn line read as its burn. Two transitions to Clear end the storm outright.
            for _ in range(2):
                _session_call(t, "jawa/weather_set", weather="Clear")
        except _NoGame as e:     # no game: no fire and no locked weather can carry into a later chain
            print("[pyre] teardown weather unlock skipped: %s" % e, file=sys.stderr, flush=True)
        except Exception as e:   # noqa: BLE001 - recorded below as a FAIL
            bad.append("weather unlock: %s" % e)
    if fire:
        try:
            mi = _session_call(t, "jawa/map_info")
            _session_call(t, "jawa/map_fire", action="extinguish",
                          rect="0,0,%d,%d" % (mi.get("sizeX", 250), mi.get("sizeZ", 250)))
        except _NoGame as e:     # no game: no fire and no locked weather can carry into a later chain
            print("[pyre] teardown extinguish skipped: %s" % e, file=sys.stderr, flush=True)
        except Exception as e:   # noqa: BLE001 - recorded below as a FAIL
            bad.append("extinguish: %s" % e)
    bad.extend("setting %s not restored: %r" % fb for fb in _restore(t))
    bad.extend(_GEN.pop("teardown_bad", []))     # restores a chain ran inside its own component 
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


PLANT_EAT_FIRST_ENV = "PYRE_PLANT_EAT_FIRST_GATE_OFF"   # planted state for fire_sense_hungry_eats_first: the mod's insert off


@contextlib.contextmanager
def _unfed(t):
    """The harness's feeder off for a row that is about hunger. HARNESS (visit 8, 2026-11-24; visit 2's F9, once): t.feed topped
    H's Food from 0.08 to 1.0 in the first chunk, so H beat the fire and never ate, and the mod read as broken."""
    prior = [(o, o.feed) for o in (t, getattr(t, "watch", None)) if o is not None and hasattr(o, "feed")]
    try:
        for o, _v in prior:
            o.feed = False
        yield
    finally:
        for o, v in prior:
            o.feed = v


def _wildlife_shielded(fn):
    """A chain whose days read ground, not animals, runs inside _wildlife_shield (visit 8: a wild barbslinger downing a
    fire-hawk stopped fresh_burn_bonus on day 1)."""
    @functools.wraps(fn)
    def wrapper(t):
        with _wildlife_shield(t):
            return fn(t)
    return wrapper


def _independent(t):
    """Start a component that reads its own state, so an earlier component's FAIL or UNMEASURED does
    not turn it UNMEASURED. The environment still ends the chain: a surprise abort, or a map the runner
    could not make bland (it sets upstream_failed before the chain starts)."""
    last = t.components[-1] if t.components else None
    bland = t.watch is None or getattr(t.watch, "bland", True)
    if last is not None and last.surprises is None and bland:
        t.upstream_failed = False
        t.upstream_reason = "upstream failed -- this chain's state is meaningless"



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
        t.screenshot(rect=_whole_rect(t))   # the subject is the fresh map itself


PLANT_FRUIT_UNBURNED_ENV = "PYRE_PLANT_SCORCHFRUIT_UNBURNED"


def _far_from_pads(t):
    """A cell more than 18 cells (in x or z) from every FIRE_PADS centre and 5 from the map edge, nearest the map centre."""
    sx, sz = _map_size(t)
    best = None
    for x in range(5, sx - 5, 5):
        for z in range(5, sz - 5, 5):
            if all(abs(x - px) > 18 or abs(z - pz) > 18 for (px, pz) in FIRE_PADS):
                d = (x - sx // 2) ** 2 + (z - sz // 2) ** 2
                if best is None or d < best[0]:
                    best = (d, (x, z))
    return best[1] if best else (5, 5)


@suite.chain("plant_census")
def plant_census(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "plant_distribution_correct", shows=["pyre_plant_distribution_correct"]):
        _fresh_site(t)
        live = _get_defs(t, "BiomeDef/RM_Pyrelands", "wildPlants,plantDensity")
        census = _whole_map(t, "Plant")
        if _live(t) and os.environ.get(PLANT_FRUIT_UNBURNED_ENV) == "1":
            # planted state for sc_scorchfruit's 'never on unburned land': one fruit on unburned ground, far from every pad
            cell = _far_from_pads(t)
            _plants(t, "RM_FE_Plant_ScorchFruit", (cell[0], cell[1], 1, 1))
            _note(t, "PLANTED FAULT: %s=1, one ScorchFruit set at %r, outside every fire pad" % (PLANT_FRUIT_UNBURNED_ENV,
                                                                                               cell), _GEN["last_plants"])
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
        t.screenshot(rect=_whole_rect(t))   # the subject is the fresh map itself
    _ten_plant_census(t)


@suite.chain("animal_census")
def animal_census(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "animal_distribution_correct", shows=["pyre_animal_distribution_correct"]):
        _fresh_site(t)
        # jawa/get_defs cannot serialise BiomeDef.wildAnimals (a non-public List: UNMEASURED by construction on
        # 2026-10-12); jawa/biome_probe reads the RESOLVED set (AllWildAnimals + CommonalityOfAnimal) instead.
        probe = t.bridge_call("jawa/biome_probe", biomes="RM_Pyrelands", animals=True, plants=False, topN=200)
        r = t.bridge_call("jawa/list_pawns", limit=1000)
        wild = []
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
            grazers = sum(v for k, v in counts.items() if k in COMMON_GRAZERS)
            big = sum(v for k, v in counts.items() if k in BIG_PREDATORS)
            _note(t, "small common grazers against big predators", {"grazers": grazers, "bigPredators": big})
            if grazers <= big:
                _fail("the big predators (%d) are not outnumbered by the small grazers (%d): %r" % (big, grazers, counts))
            wa, why = biome_probe_animals(probe, "RM_Pyrelands")
            if wa is None:
                _unmeasured(t, "census clean (%d wild, %d kinds, none foreign) but the live "
                               "wildAnimals read-back the plan requires is not readable: %s"
                            % (len(wild), len(counts), why))
            _note(t, "live resolved wildAnimals (biome_probe)", wa)
            keys = set(wa)
            if keys != set(ANIMAL_MANIFEST):
                _fail("live wildAnimals %r differs from the %d-kind manifest" % (sorted(keys), len(ANIMAL_MANIFEST)))
        # the subject: the wild animals where they stand thickest (a whole 250-cell map shows no species)
        t.screenshot(rect=_frame(t, [(p.get("x"), p.get("z")) for p in wild], cluster=FRAME_CLUSTER))



def cover_ratio(census, terr, fert, built):
    """Pure. The grass cover census of one map -> (covered, plantable, ratio): roster plants (PLANT_MANIFEST) over the
    cells whose top terrain has fertility > 0, less the artificial buildings. grass_cover and the plantDensity-1.0 foil
    (density_foil_verdict) both count through this one function, so the foil is read by the same census."""
    plantable = sum(n for d, n in (terr or {}).items() if ((fert or {}).get(d) or {}).get("fertility", 0) > 0)
    plantable -= built or 0
    covered = sum(v for k, v in (census or {}).items() if k in PLANT_MANIFEST)
    return covered, plantable, (float(covered) / plantable if plantable > 0 else None)

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
            b = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=1)
            built = (b or {}).get("countMatched", 0)
            covered, plantable, ratio = cover_ratio(census, terr, fert, built)
            dens = (_get_defs(t, "BiomeDef/RM_Pyrelands", "plantDensity", deep=False).get("RM_Pyrelands") or {})
            _GEN["grass_census"] = {"mutationsBefore": list(_GEN.get("mutations") or []), "ratio": ratio,
                                    "covered": covered, "plantable": plantable,
                                    "plantDensity": dens.get("plantDensity")}   # sc_grass_regreens reads it
            _note(t, "coverage", {"covered": covered, "plantableCells": plantable,
                                  "buildingsExcluded": built, "ratio": ratio,
                                  "roofedCells": "not excluded (no whole-map roof read)"})
            if plantable <= 0:
                _unmeasured(t, "plantable cell count is zero / unreadable: %r" % terr)
            if ratio < 0.85:
                _fail("plant coverage %.3f of %d plantable cells (< 0.85)" % (ratio, plantable))
        t.screenshot(rect=_whole_rect(t))   # the subject is the fresh map itself


PLANT_RUIN_SOIL_ENV = "PYRE_PLANT_RUIN_FOOTPRINT_SOIL"   # planted state for sc_ruins: the sampled footprints laid unburned soil


@suite.chain("ruins")
def ruins(t):
    """Ruins are found as what they ARE on the map -- unowned artificial buildings (walls, doors,
    the ruin's own floors' structures) -- and their footprint is read for what GenStep_ScorchPyrelandsRuins
    lays (deep ash on the footprint and rim, a built floor kept and painted charred, ash on the ground over it). The earlier probe listed
    things named `RM_FE_ScorchRuins`, which is the GENSTEP def, never a Thing, so it read UNMEASURED on
    every site by construction (2026-10-11 pilot: the map carried 600+ cells of ruin floors)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ruins_scorched", shows=["pyre_ruins_scorched"]):
        _fresh_site(t)
        r = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=2000)
        rows = []
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
            rects = ["%d,%d,3,3" % (x["x"] - 1, x["z"] - 1) for x in picks]
            if os.environ.get(PLANT_RUIN_SOIL_ENV) == "1":   # planted state: the sampled footprints re-laid as unburned soil
                t.bridge_call("jawa/set_terrain_batch", ops=";".join("%s:%s" % (SOIL, rc) for rc in rects), layer="top")
                _note(t, "PLANTED FAULT: %s=1, the %d sampled ruin footprints re-laid %s" % (PLANT_RUIN_SOIL_ENV, len(rects),
                                                                                          SOIL), rects)
            got = _terrain(t, ";".join(rects))
            floors = [_charred(t, rc) for rc in rects]
            charred = sum(f.get("charred", 0) for f in floors)
            frac = ruin_scorched_share(got, charred) or 0.0
            filthy = sum(1 for rc in rects if _ash(t, rc).get("ashed", 0) > 0)
            _note(t, "ruin footprint terrain + ash on the ground (3x3 at %d sampled ruin buildings)" % len(picks),
                  {"terrain": got, "floors": sum(f.get("floors", 0) for f in floors), "charredFloors": charred,
                   "scorchedFraction": round(frac, 3), "ruinsWithAsh": filthy})
            # Deep ash is ~85% of the map, so terrain alone barely marks a ruin. The genstep lays deep ash on every footprint
            # cell EXCEPT a built floor, which it keeps and paints RM_FE_Charred (CharFloor, since the 2026-11-08 merge: "the
            # ruin floors look clean"); either one is the scorch. Ash (sand depth 0.25) lies on ~70% of the cells on top.
            if frac < RUIN_ASH_MIN:
                _fail("ruin footprints are %.0f%% deep ash or charred floor, want >= %.0f%%: %r, %d charred floor cells"
                      % (100 * frac, 100 * RUIN_ASH_MIN, got, charred))
            # The site builder now sets the season BEFORE the map is generated (PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST),
            # so loose ash (6~9 day lifetime, absolute growTick) is minutes old here and 2-of-10 is a genstep finding.
            # A fixture built before that change still carries the old 6-10 day gap: rebuild it, do not excuse it.
            if filthy < RUIN_FILTH_MIN * len(picks):
                _fail("%d of %d sampled ruins carry ash on the ground, want >= %.0f%%" % (filthy, len(picks), 100 * RUIN_FILTH_MIN))
        # the subject: one ruin, its walls at their thickest (visit 2's walk save: the densest cluster reads as a ruin)
        t.screenshot(rect=_frame(t, [(x.get("x"), x.get("z")) for x in rows], cluster=FRAME_CLUSTER))
    _ten_ruins(t)


@suite.chain("burn_line")
@_teardown(fire=True)
def burn_line(t):
    """LONG SPLIT ONLY (the burned-share read plays eight game days): run as --chains embergrass_regrow,burn_line, skip in the
    main run.
    The fixture holds burnLineEnabled OFF, so a census alone is UNMEASURED. The arm: burnLineEnabled ON, extinguish the
    map, put the burn line's own quiet counter just short of StandingBurnQuietTicks (_stage_quiet), wait a few watch
    intervals and reseed retries, count free-standing Fire. MapComponent_BurnLine
    .TryReseedStandingBurn must have lit one smoulder (parent == null). Then extinguish; _teardown restores settings."""
    _burn_line_present(t)
    with _wildlife_shield(t):
        _r6_burn_line(t)


def _burn_line_present(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "burn_line_present", shows=["pyre_burn_line_present"]):
        _fresh_site(t)
        s = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                          field="burnLineEnabled")
        before = len(_things(t, "Fire", limit=2000))
        _set(t, {"burnLineEnabled": True})
        _extinguish(t)
        _stage_quiet(t)
        _wait(t, BURN_STAGED_WAIT_TICKS)
        fires = [f for f in _things(t, "Fire", limit=2000) if not f.get("parent")]
        _note(t, "burn line quiet-arm (free-standing Fire after the quiet window)",
              {"fixtureBurnLineEnabled": (s or {}).get("value"), "firesBeforeArm": before,
               "waitTicks": BURN_STAGED_WAIT_TICKS, "freeStandingFires": len(fires)})
        if _live(t) and not fires:
            _fail("burnLineEnabled ON, map extinguished, the quiet counter put just short of StandingBurnQuietTicks %d, %d "
                  "ticks on and no free-standing Fire: the standing burn did not reseed" % (BURN_QUIET_TICKS, BURN_STAGED_WAIT_TICKS))
        t.screenshot(rect=_frame(t, [(f.get("x"), f.get("z")) for f in fires], cluster=FRAME_CLUSTER))   # the front
        # The walk does not start from this reseed: it puts the map out and re-arms the opening front (visit 2's 0 fires at
        # every hour were its reader, blind to the bridge's x/z rows, not this front; RIMMANDRAKE_REORDER_PYRE_BURN_WALK_
        # BEFORE_ITS_FRONT_DIES). _teardown puts the map out at the chain's end.


def _stage_quiet(t):
    """The map is out: let the burn line's watch see it, then put its saved quiet counter (MapComponent_BurnLine.
    ticksSinceAnyFire) two watch intervals short of StandingBurnQuietTicks, so KeepTheBurnAlive acts next. Where the toggle is
    off the counter is never read: what must not happen is a relight."""
    _wait(t, 2 * BURN_WATCH_TICKS)
    want = BURN_QUIET_TICKS - 2 * BURN_WATCH_TICKS
    r = t.bridge_call("jawa/map_comp_set", comp="MapComponent_BurnLine", member="ticksSinceAnyFire", value=str(want))
    if _live(t) and str((r or {}).get("after")) != str(want):
        _unmeasured(t, "the quiet counter could not be staged at %d: %r" % (want, r))


OPENING_WAIT_TICKS = 6 * BURN_WATCH_TICKS   # PYRE_OPENING_FRONT: lit on the first watch interval; a few for slack
OPENING_WINDOW = 2500                       # PyrelandsTuning.OpeningFrontWindowTicks


def old_save_opening_verdict(kv, window=OPENING_WINDOW, rearmed=False):
    """The A4 old-save read of one ProbeOpeningFront reply -> (verdict, why): "UNMEASURED" (not an old save), "FAIL" or
    "PASS". LIES: a map inside its first `window` ticks is a FRESH map; a re-arm earlier in this session leaves lit > 0 on
    any map; and a fixture built after the opening front shipped lit its own front at birth (litTick within the window
    of the map's birth tick, now - mapAge; visit 1: litTick 372539 = birth, lit 5), so an earlier chain that aged it past
    the window does not make it an old save. A front lit later than that window is the old-save defect and fails."""
    if "done" not in kv or not str(kv.get("mapAge") or "").lstrip("-").isdigit():
        return "UNMEASURED", "ProbeOpeningFront unreadable (stale FireEcologyHook.dll?): %r" % (kv,)
    age = int(kv["mapAge"])
    if age <= window:
        return "UNMEASURED", "SITE: the map is %d ticks old (window %d): a fresh map, not a loaded old save" % (age, window)
    if rearmed:
        return "UNMEASURED", "HARNESS: RearmOpeningFront already ran this session; reload the fixture for the old-save read"
    lit_tick, now = str(kv.get("litTick") or ""), str(kv.get("now") or "")
    if lit_tick.isdigit() and now.isdigit():
        born = int(now) - age
        if 0 <= int(lit_tick) - born <= window:
            return "UNMEASURED", ("SITE: the map lit its own opening front at birth (litTick %s, born %d, window %d): "
                                  "a fixture built after the front shipped, not a loaded old save" % (lit_tick, born, window))
    if kv.get("done") != "True" or kv.get("lit") != "0" or kv.get("litTick") != "-1":
        return "FAIL", "a loaded save past its window lit (or still owes) an opening front: %r" % (kv,)
    return "PASS", "done=True, lit=0, litTick=-1 on a map %d ticks old" % age


@suite.chain("opening_front")
@_teardown(fire=True)
def opening_front(t):
    """PYRE_OPENING_FRONT (owner, by card, 2026-10-22: "GPT review Q7 → Pyrelands fresh map starts with a smouldering front").
    The arrival half of pyre_burn_line_present, read without a fresh worldgen: fireClockEnabled ON, the map extinguished,
    MapComponent_BurnLine.RearmOpeningFront (the map counts as fresh, its window starting now), a few watch intervals, then
    ProbeOpeningFront must say done with lit > 0 and the map must hold free-standing Fire again. Evidence only (shows=[]):
    burn_line_present stays the one component of that bar. The arrival on a TRULY fresh map is the walk's own look.
    The A4 old-save half runs FIRST, before the re-arm: a loaded fixture (saved before 05033a3f7, or later with the front
    long done) must read done=True, lit=0 and never light it - the saved flag defaults TRUE, so a pre-change save carries no
    key and loads as done.
    Lessons from runs go here."""
    _pad(t, PAD_PROBE)
    with _comp(t, "opening_front_old_save_inert", shows=[]):
        r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="ProbeOpeningFront")
        kv = parse_kv((_ok(r, "ProbeOpeningFront") or {}).get("result")) if _live(t) else {}
        _note(t, "opening front on the loaded save, before any re-arm", {"probe": kv})
        if _live(t):
            verdict, why = old_save_opening_verdict(
                kv, OPENING_WINDOW, rearmed=getattr(t.session, "_pyre_opening_rearmed", False))
            if verdict == "UNMEASURED":
                _unmeasured(t, why if kv else "%s: %r" % (why, r))
            if verdict == "FAIL":
                _fail(why)
    with _comp(t, "opening_front", shows=[]):
        _set(t, {"fireClockEnabled": True})
        _extinguish(t)
        if t.session is not None:
            t.session._pyre_opening_rearmed = True
        r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="RearmOpeningFront")
        if _live(t) and str((_ok(r, "RearmOpeningFront") or {}).get("result")).strip() != "1":
            _unmeasured(t, "RearmOpeningFront refused (is this Pyrelands DLL deployed, is the current map Pyrelands?): %r" % r)
        _wait(t, OPENING_WAIT_TICKS)
        r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="ProbeOpeningFront")
        kv = parse_kv((_ok(r, "ProbeOpeningFront") or {}).get("result")) if _live(t) else {}
        fires = [f for f in _things(t, "Fire", limit=2000) if not f.get("parent")]
        _note(t, "opening front after a re-arm", {"probe": kv, "waitTicks": OPENING_WAIT_TICKS,
                                                  "freeStandingFires": len(fires)})
        if _live(t):
            if "done" not in kv:
                _fail("ProbeOpeningFront unreadable: %r" % r)
            if not str(kv.get("lit") or "").isdigit():
                _fail("ProbeOpeningFront lit is not a count: %r" % r)
            if kv.get("done") != "True" or int(kv["lit"]) <= 0:
                _fail("re-armed, fire clock ON, %d ticks and the opening front did not light: %r" % (OPENING_WAIT_TICKS, kv))
            if not fires:
                _fail("the opening front reports %s cells lit but no free-standing Fire is on the map" % kv.get("lit"))
        t.screenshot(rect=_frame(t, [(f.get("x"), f.get("z")) for f in fires], cluster=FRAME_CLUSTER))   # the front
        _extinguish(t)


@suite.chain("startup_and_def_wiring")
def startup_and_def_wiring(t):
    """Pure reads of what the session has loaded (toggle floor)."""
    _pad(t, PAD_PROBE)
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
        # no capture: a def read has no subject on the map, and this row claims no bar a judge reads


@suite.chain("ground_deep_ash")
@_teardown(fire=True, weather=True)
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
            if share is None:
                _unmeasured(t, "no open land read: %r" % gen)
            if share < DEEP_ASH_MIN:
                _fail("deep ash is %.3f of %d open-land cells (< %.2f)" % (share, land, DEEP_ASH_MIN))
            if not any(pockets.values()):
                _fail("no unburned pocket (soil / gravel / sand) at all: %r" % pockets)
            if ring["WaterShallow"] and not (ring["RM_FE_Ground_SoilRich"] or ring["Mud"]):
                _fail("standing water with no rich-soil / mud ring: %r" % ring)
        t.screenshot(rect=_whole_rect(t))   # the subject is the fresh map itself
    _ten_ground_deep_ash(t)
    _r6_ground_deep_ash(t)


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
        # the subject: the deep-ash strip, its watered cell and its dry far cell
        t.screenshot(rect=frame_rect([(x0, z0), (x0 + ASH_STRIP_W - 1, z0 + ASH_STRIP_H - 1)], _map_size(t)))
    _ten_ash_fertility_watered(t)


@suite.chain("fresh_burn_bonus")
@_teardown(fire=True, weather=True)
@_wildlife_shielded
def fresh_burn_bonus(t):
    """LONG SPLIT (~100k ticks). pyre_fresh_burn_feeds_the_field, a STATE read of FertilityAt on a burned deep-ash cell:
    before the burn, right after it, +1 day (the linear decay; the design's +3 days costs another 120k ticks for a point
    the kernel selftest already pins), then after ~15 h of forced RM_FE_BlackRain: the bonus must still be on its own clock
    and the Black Rain must have watered the field, so burned-and-rained beats burned alone and rained alone. The fire burning on DEEP ASH is also the live proof of
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
            if not rained["watered"]:
                _fail("Black Rain did not water the field: %r" % rained)
            if not (0 < rained["bonus"] < day1["bonus"]):
                _fail("~15 h of Black Rain moved the bonus off its clock: day1 %.3f, rained %.3f" % (day1["bonus"], rained["bonus"]))
            if rained["fertility"] < rained["wateredFertility"] + rained["bonus"] - 0.01:
                _fail("the bonus did not stack on the watered lift: %r" % rained)
        t.screenshot(rect=burn)
    _r6_fresh_burn_bonus(t)


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
        t.screenshot(rect=_sky_rect(t))


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
        n = _ash(t, _rs(rect)).get("ashed", 0)
        if _live(t) and n < 1:
            _fail("expected >=1 ashed cell (sand depth >= 0.03) in %s after 2600 ticks of fire, got %d"
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
    site -- seed the fruit.
    PYRE_FIREBORN_DIAGNOSE_TWENTYONE_RETURN (L1 2026-10-15): in the full A order 21 fruit stood OFF every pad after this
    clear (0 at the clear before the weather chains) and scorchfruit_fire_born's cohort got none; alone it passed. A fire
    that is not a pad's (a stray from the unlocked weather between chains) seeds fruit where the pad rects never reach
    and keeps eating the per-map cap while the cohort burns. So every fire on the map is put out first, and every
    ScorchFruit left anywhere is destroyed by its own cell, not only around the pads."""
    _extinguish(t)
    for (px, pz) in FIRE_PADS:
        t.bridge_call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (px - 20, pz - 20, 40, 40), categories="Plant")
    stray = [x for x in _things(t, "RM_FE_Plant_ScorchFruit") if x.get("x") is not None and x.get("z") is not None]
    if stray:
        _note(t, "ScorchFruit off every fire pad, destroyed by cell", [(x["x"], x["z"]) for x in stray][:60])
        t.bridge_call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % (x["x"], x["z"]) for x in stray), categories="Plant")
    left = _count(t, "RM_FE_Plant_ScorchFruit")
    _note(t, "ScorchFruit left on the map after the cap-budget clear", left)


@suite.chain("ashfall_weather_accumulation")
@_teardown(weather=True)
def ashfall_weather_accumulation(t):
    """Ash fall counted over the WHOLE map from ZERO. Since 2026-11-08 it is vanilla sand fall (sandRate 1.2, heavy snow's
    pace), so every open cell gains depth on each visit; 2600 ticks is ~1.5 visits, a dusting where it has landed."""
    _pad(t, PAD_PROBE)
    with _comp(t, "ashfall_accumulates", toggle="ashfallAccumulationEnabled"):
        _extinguish(t)
        _clear_ash(t)
        start = _ash(t).get("ashed", 0)
        if _live(t) and start != 0:
            _fail("could not clear ash to zero before the run: %d cells remain" % start)
        try:
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
            _wait(t, 2600)
            got = _ash(t)
        finally:
            t.bridge_call("jawa/weather_set", unlock=True)
        n = got.get("ashed", 0)
        _note(t, "whole-map ash after 2600 ticks of ash fall", got)
        if _live(t) and n < 1:
            _fail("expected >=1 NEW ashed cell over the whole map after 2600 ticks "
                  "under RM_FE_Weather_AshFall, got %d (%r)" % (n, got))
        t.screenshot(rect=_sky_rect(t))


# --------------------------------------------------------------------------- weather

@suite.chain("ashfall_drifts")
@_teardown(weather=True)
def ashfall_drifts(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "ashfall_darkens_drifts", shows=["pyre_ashfall_darkens_drifts"]):
        _extinguish(t)
        _clear_ash(t)
        t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
        _wait(t, 4000)
        series, cells = [], []
        for _ in range(4):
            a = _ash(t)
            series.append(a.get("depthSum", 0.0))
            cells.append(a.get("ashed", 0))
            _wait(t, 2500)
        _note(t, "whole-map ash depth sum / ashed cells at t=0/2500/5000/7500 after settle", {"depthSum": series, "ashed": cells})
        if _live(t):
            if any(b < a for a, b in zip(series, series[1:])) or cells[-1] < 20:
                _fail("ash depth series %r not monotone, or %r ashed cells < 20 at the end" % (series, cells))
        t.screenshot(rect=_sky_rect(t))


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
    t.screenshot(rect=_sky_rect(t))


# ---- sc_three_skies clauses (RIMMANDRAKE_ROW_SKY_CLAUSES_ONCE_READ_BY_HAND; visit 1 read them by hand, three_skies.py)
# One row per clause. Each row first reads the def that carries the clause's mechanism (sky_clause_defs, pure, proven
# offline against the shipped XML and a mutant per clause), then the live effect (a pure verdict per clause).
CINDERFALL, ASHFALL, BLACKRAIN = "RM_FE_Weather_Cinderfall", "RM_FE_Weather_AshFall", "RM_FE_BlackRain"
STRIKE_EVENT = "WeatherEvent_LightningStrike"   # GenExplosion Flame at the strike cell: the storm's only fire-starter
DOUSE_FIELDS = ("blackRainDousingEnabled", "blackRainDousing")   # Patch_FireTick_BlackRainDouses: vanilla rain alone loses to grass
SKY_SETTLE_TICKS = 4500     # a locked weather blended in (visit 1: the first reads after a switch carried the last sky)
SKY_WINDOWS, SKY_WINDOW_TICKS = 10, 1000
# cinderfall_lightning counts STRIKES, not fires (RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW). A fire count
# is wrong both ways: a strike on a fogged cell or bare sand lights nothing, and one strike's fire spreads to 31 in a window
# (visit 2). Visits 1 and 2 each read one fire in ash fall's first window, with no lightning maker on the def. The prior sky
# cannot strike then: WeatherManager.TransitionTicks is 4000 and SKY_SETTLE_TICKS is 4500, so the cinderfall weight is 0
# before the window opens (vanilla WeatherManagerTick). jawa/health_profile counts the calls of this one method. The
# WeatherEventHandler calls FireEvent once for each strike event, at the time it adds the event.
STRIKE_METHOD = "RimWorld.WeatherEvent_LightningStrike:FireEvent"
STRIKE_PROFILE_MINUTES = 60     # the profiler's own maximum: it must expire (its law). A leg is ten 1000-tick windows,
                                # about 3.2 min at the measured ~53 ticks/s. A leg that outlives the profiler reads UNMEASURED.
# Planted fault for this row: the "ash fall" leg runs under this sky (DryThunderstorm: a vanilla strike maker, one strike per
# 1200 ticks on average), so the row must read FAIL. Unset: the real AshFall.
PLANT_ASHFALL_STRIKE_ENV = "PYRE_PLANT_ASHFALL_STRIKE"
FIRE_ROWS_KEPT = 5              # fire rows named per leg in the note: enough to name a cause, not a dump
WASH_TICKS, WASH_DEPTH, WASH_MIN_SHARE = 2500, 0.5, 0.10
FIRE_PAD_OUT = (PAD_PROBE[0], PAD_PROBE[1] - 30)   # the fires-out pad, off the wash patch at PAD_PROBE
FIRE_OUT_POLLS, FIRE_OUT_STEP = 12, 250


def sky_defs_from_xml(texts):
    """Pure. WeatherDef XML texts -> {defName: {"rainRate": float, "events": [eventClass, ...]}}."""
    import xml.etree.ElementTree as ET
    out = {}
    for text in texts:
        for wd in ET.fromstring(text).iter("WeatherDef"):
            name = (wd.findtext("defName") or "").strip()
            try:
                rate = float(wd.findtext("rainRate") or 0)
            except ValueError:
                rate = None
            out[name] = {"rainRate": rate,
                         "events": [(li.findtext("eventClass") or "").strip() for li in wd.findall("eventMakers/li")]}
    return out


def sky_defs_from_live(fields):
    """Pure. _get_defs reply ({defName: {field: value}}) -> the sky_defs_from_xml shape. An eventMakers field the bridge
    did not serialise reads events None (unread), never an empty list."""
    out = {}
    for name, f in (fields or {}).items():
        ev = f.get("eventMakers")
        try:
            rate = float(f.get("rainRate"))
        except (TypeError, ValueError):
            rate = None
        out[name] = {"rainRate": rate,
                     "events": None if ev is None else sorted(set(re.findall(r"WeatherEvent_\w+", json.dumps(ev))))}
    return out


def sky_clause_defs(defs, settings=None, douse_def=BLACKRAIN):
    """Pure. -> {clause: (ok, why)}; ok None = the def could not be read. Each clause's mechanism, and nothing more:
    lightning   cinderfall makes WeatherEvent_LightningStrike and ash fall makes none
    ash_wash    black rain's rainRate > 0 (RM_FireEcoKernel.OutdoorSandWear washes 0.25 x rainRate a visit)
    fires_out   the dousing hook keys on black rain's defName (`douse_def`, RM_FireEcoKernel.BlackRainDefName) and
                `settings` (DOUSE_FIELDS) have it on with an Extinguish > 0: vanilla rain alone loses to an ember-grass fire
                (visit 1, RIMMANDRAKE_FIX_BLACK_RAIN_LOSES_TO_EMBER_GRASS_FIRE)"""
    c, a, b = (defs.get(n) or {} for n in (CINDERFALL, ASHFALL, BLACKRAIN))
    out = {}
    if c.get("events") is None or a.get("events") is None:
        out["lightning"] = (None, "eventMakers unread: %r / %r" % (c.get("events"), a.get("events")))
    else:
        out["lightning"] = (STRIKE_EVENT in c["events"] and STRIKE_EVENT not in a["events"],
                            "cinderfall %r, ash fall %r" % (c["events"], a["events"]))
    rate = b.get("rainRate")
    out["ash_wash"] = (None if rate is None else rate > 0, "black rain rainRate %r" % rate)
    on, amount = ((settings or {}).get(f) for f in DOUSE_FIELDS)
    why = "dousing hook keys on %r, %s=%r, %s=%r" % (douse_def, DOUSE_FIELDS[0], on, DOUSE_FIELDS[1], amount)
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = None
    if on is None or amount is None:
        out["fires_out"] = (None, why)
    else:
        out["fires_out"] = (douse_def == BLACKRAIN and str(on).lower() == "true" and amount > 0, why)
    return out


def strike_deltas(cumulative):
    """Pure. The strike-call counter read after each window (cumulative, None = unread) -> strikes in each window. A window
    whose read, or the read before it, is None is None. A counter that went down (a profiler restart) is None too."""
    out, last = [], 0
    for c in cumulative or []:
        out.append(None if c is None or last is None or c < last else c - last)
        last = c
    return out


def lightning_verdict(cinder, ashfall, cinder_fires=None, ash_fires=None):
    """Pure. Lightning strikes per window under each settled sky (calls of STRIKE_METHOD) -> (ok, why): some under
    cinderfall, none under ash fall. ok None = a window was not read: UNMEASURED, never a fail or a pass.
    The fire counts are evidence only. A window under ash fall with fires and no strike names those fires as not lightning."""
    if not cinder or not ashfall or None in cinder or None in ashfall:
        return None, "unread windows: strikes under cinderfall %r, ash fall %r" % (cinder, ashfall)
    ok = sum(cinder) > 0 and sum(ashfall) == 0
    why = "strikes per %d ticks: cinderfall %r (total %d), ash fall %r (total %d); worst ash-fall window %d, limit 0; %d windows read" % (
        SKY_WINDOW_TICKS, cinder, sum(cinder), ashfall, sum(ashfall), max(ashfall), len(cinder) + len(ashfall))
    if cinder_fires is not None or ash_fires is not None:
        why += "; new fires per window (evidence only): cinderfall %r, ash fall %r" % (cinder_fires, ash_fires)
    unlit = [i + 1 for i, (s, f) in enumerate(zip(ashfall, ash_fires or [])) if f and not s]
    if unlit:
        why += "; ash-fall window(s) %r had fire and no strike: not lightning" % unlit
    return ok, why


def wash_verdict(clear, rain, min_share=WASH_MIN_SHARE):
    """Pure. (depthSum before, after) on the same patch over the same ticks, under clear sky and under black rain ->
    (ok, why): black rain takes at least twice the clear sky's loss, and at least `min_share` of the patch."""
    if None in tuple(clear) + tuple(rain) or not rain[0]:
        return False, "unread or bare patch: clear %r, rain %r" % (clear, rain)
    lc, lr = clear[0] - clear[1], rain[0] - rain[1]
    ok = lr >= 2 * max(lc, 0.0) and lr >= min_share * rain[0]
    return ok, "depthSum loss: clear %.2f (%r), black rain %.2f (%r); needs >= 2x clear and >= %.0f%% of %.2f" % (
        lc, clear, lr, rain, 100 * min_share, rain[0])


def fires_out_verdict(clear, rain):
    """Pure. Fire counts on the same pad at the same ticks after ignition -> (ok, why): some read has the black-rain pad
    out while the clear-sky pad still burns."""
    if not clear or not rain or len(clear) != len(rain) or None in clear or None in rain:
        return False, "unread series: clear %r, rain %r" % (clear, rain)
    at = [i for i, (c, r) in enumerate(zip(clear, rain)) if r == 0 and c > 0]
    return bool(at), "fires every %d ticks: clear %r, black rain %r; black rain out while clear burns at %r" % (
        FIRE_OUT_STEP, clear, rain, [(i + 1) * FIRE_OUT_STEP for i in at])


def _sky_def_leg(t, clause):
    if not _live(t):
        return
    names = ";".join("WeatherDef/%s" % n for n in (CINDERFALL, ASHFALL, BLACKRAIN))
    settings = {}
    for f in DOUSE_FIELDS:
        r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f)
        settings[f] = (r or {}).get("value") if (r or {}).get("success") else None
    ok, why = sky_clause_defs(sky_defs_from_live(_get_defs(t, names, "rainRate,eventMakers")), settings)[clause]
    _note(t, "%s mechanism on the live def" % clause, why)
    if ok is False:
        _fail("the def no longer carries the %s mechanism: %s" % (clause, why))


def _sky(t, weather):
    """Lock `weather`, let it blend in, put out whatever the switch left burning."""
    t.bridge_call("jawa/weather_set", weather=weather, lockWeather=True)
    _wait(t, SKY_SETTLE_TICKS)
    _extinguish(t)


def _strike_profile_start(t):
    """Start the strike counter. -> None when it runs, else why it cannot count (the row then reads UNMEASURED)."""
    r = t.bridge_call("jawa/health_profile", action="start", methods=STRIKE_METHOD, minutes=STRIKE_PROFILE_MINUTES)
    if not _live(t):
        return None
    prof = (r or {}).get("profile") or {}
    if not isinstance(r, dict) or r.get("success") is False:
        return "jawa/health_profile start refused: %r" % (r,)
    if prof.get("refused") or STRIKE_METHOD not in [m.get("method") for m in prof.get("methods") or []]:
        return "%s did not resolve in the running game: %r" % (STRIKE_METHOD, prof.get("refused"))
    return None


def _strike_calls(t):
    """The strike counter now, or None when it cannot be read (not running: expired, stopped, disabled after a fault)."""
    r = t.bridge_call("jawa/health_profile", action="status")
    if not _live(t):
        return None
    prof = (r or {}).get("profile") or {}
    if not isinstance(r, dict) or r.get("success") is False or prof.get("status") != "running":
        return None
    row = [m for m in prof.get("methods") or [] if m.get("method") == STRIKE_METHOD]
    return row[0].get("calls") if row and isinstance(row[0].get("calls"), int) else None


def _sky_windows(t):
    """Ten windows under the settled sky -> (strikes per window, new fires per window, the first fire rows, profiler error).
    Each window's fires are put out, so the next window counts only new ones."""
    why = _strike_profile_start(t)
    cumulative, fires, rows = [], [], []
    for _ in range(SKY_WINDOWS):
        _wait(t, SKY_WINDOW_TICKS)
        # a start that failed counts nothing: a status read then shows an earlier profile, or a zero that was never counted
        cumulative.append(None if why else _strike_calls(t))
        n = _count(t, "Fire")
        fires.append(n)
        if n:
            if len(rows) < FIRE_ROWS_KEPT:
                rows += [dict(r, window=len(fires)) if isinstance(r, dict) else {"row": r, "window": len(fires)}
                         for r in _things(t, "Fire", limit=FIRE_ROWS_KEPT - len(rows))]
            _extinguish(t)
    t.bridge_call("jawa/health_profile", action="stop")
    return strike_deltas(cumulative), fires, rows, why


def _sky_lightning(t):
    _independent(t)
    with _comp(t, "cinderfall_lightning", beyond_toggle=True):
        _sky_def_leg(t, "lightning")
        _isolate(t)     # no burn line, fire hawk or furnace beast fire: the fire rows in the note stay few enough to read
        ash_sky = os.environ.get(PLANT_ASHFALL_STRIKE_ENV) or ASHFALL
        if ash_sky != ASHFALL:
            _note(t, "PLANTED FAULT: the ash-fall leg runs under %s" % ash_sky, PLANT_ASHFALL_STRIKE_ENV)
        got = {}
        for key, w in ((ASHFALL, ash_sky), (CINDERFALL, CINDERFALL)):
            _sky(t, w)
            got[key] = _sky_windows(t)
        if _live(t):
            for key in (ASHFALL, CINDERFALL):
                if got[key][2]:
                    _note(t, "lightning: fires under %s (first %d rows, window = 1..%d)" % (key, FIRE_ROWS_KEPT, SKY_WINDOWS),
                          got[key][2])
            ok, why = lightning_verdict(got[CINDERFALL][0], got[ASHFALL][0], got[CINDERFALL][1], got[ASHFALL][1])
            _note(t, "lightning: strikes (%s calls) per window under each sky" % STRIKE_METHOD, why)
            if ok is None:
                _unmeasured(t, "%s; profiler: ash fall %s, cinderfall %s" % (
                    why, got[ASHFALL][3] or "ran", got[CINDERFALL][3] or "ran"))
            if not ok:
                _fail(why)


def _depth(t, rect):
    return _ash(t, rect).get("depthSum") if _live(t) else None


def _sky_wash(t):
    _independent(t)
    with _comp(t, "blackrain_washes_ash", beyond_toggle=True):
        _sky_def_leg(t, "ash_wash")
        _extinguish(t)
        rect = _rs(_rect(t, size=30))
        got = {}
        for w in ("Clear", BLACKRAIN):
            _sky(t, w)
            t.bridge_call("jawa/static_call", type=ASH_SAND, method="LayAsh", args="%s|%s" % (rect, WASH_DEPTH))
            a = _depth(t, rect)
            _wait(t, WASH_TICKS)
            got[w] = (a, _depth(t, rect))
        if _live(t):
            ok, why = wash_verdict(got["Clear"], got[BLACKRAIN])
            _note(t, "ash wash on %s over %d ticks" % (rect, WASH_TICKS), why)
            if not ok:
                _fail(why)


def _sky_fires_out(t):
    _independent(t)
    with _comp(t, "blackrain_fires_out", toggle="blackRainDousingEnabled"):
        _sky_def_leg(t, "fires_out")
        _pad(t, FIRE_PAD_OUT)
        rect = _rect(t, size=8)
        got = {}
        for w in ("Clear", BLACKRAIN):
            _sky(t, w)
            t.clear_area(size=16)
            t.bridge_call("jawa/set_terrain", x=rect[0], z=rect[1], terrainDef=DEEP_ASH, width=8, height=8, layer="top")
            _firebreak(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            _fire(t, rect)
            got[w] = []
            for _ in range(FIRE_OUT_POLLS):
                _wait(t, FIRE_OUT_STEP)
                got[w].append(_count(t, "Fire", _rs(_rect(t, size=16))) if _live(t) else None)
            _extinguish(t)
        _pad(t, PAD_PROBE)
        if _live(t):
            ok, why = fires_out_verdict(got["Clear"], got[BLACKRAIN])
            _note(t, "fires out on an 8x8 ember-grass pad", why)
            if not ok:
                _fail(why)


@suite.chain("cinderfall")
@_teardown(fire=True, weather=True)
def cinderfall(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "cinderfall_distinct", shows=["pyre_cinderfall_distinct"]):
        _weather_pair(t, "RM_FE_Weather_Cinderfall", "RM_FE_Weather_AshFall",
                      ("overlayClasses", "skyColorsDay", "skyColorsNightMid", "windSpeedFactor"))
    _sky_lightning(t)
    _ten_cinderfall(t)


@suite.chain("blackrain")
@_teardown(fire=True, weather=True)
def blackrain(t):
    _pad(t, PAD_PROBE)
    with _comp(t, "blackrain_reads", shows=["pyre_blackrain_reads"]):
        _weather_pair(t, "RM_FE_BlackRain", "Rain",
                      ("overlayClasses", "skyColorsDay", "skyColorsNightMid"))
    _sky_wash(t)
    _sky_fires_out(t)


SMOOTH_MAX_TICK_US = 50000.0    # a colony tick this long is a visible hitch at normal speed


@suite.chain("soaked_map_stays_smooth")
@_teardown(fire=True)
def soaked_map_stays_smooth(t):
    """Owner, 2026-11-07: "VERY FAST, then pause". The Explosive Growth pass stepped and popped a whole rain-soaked map on
    one tick (about 1 s, every 250 ticks). Hold black rain until grass pops, then read the slowest single tick of that pass."""
    tick = "RimMandrake.ExplosiveGrowth.RM_MapComponent_ExplosiveGrowth:MapComponentTick"
    fire = "RimMandrake.ExplosiveGrowth.RM_TopResolver:Fire"
    with _comp(t, "soaked_map_stays_smooth", beyond_toggle=True):
        _fresh_site(t)
        t.bridge_call("jawa/weather_set", weather="RM_FE_BlackRain", lockWeather=True)
        _wait(t, 8000)
        t.bridge_call("jawa/health_profile", action="start", methods=tick + ";" + fire, minutes=10)
        _wait(t, 6000)
        got = t.bridge_call("jawa/health_profile", action="status") or {}
        t.bridge_call("jawa/health_profile", action="stop")
        if _live(t):
            rows = {m.get("method"): m for m in (got.get("profile") or {}).get("methods") or []}
            _note(t, "Explosive Growth pass under black rain", rows)
            pops, row = (rows.get(fire) or {}).get("calls") or 0, rows.get(tick)
            if not row or not pops:
                _unmeasured(t, "no grass popped in the window, so the pass was not under load: %r" % rows)
            worst = float(str(row.get("maxUs")).split()[0])
            if worst > SMOOTH_MAX_TICK_US:
                _fail("slowest Explosive Growth tick %.0f us over %.0f us with %d pops" % (worst, SMOOTH_MAX_TICK_US, pops))


@suite.chain("no_ordinary_rain")
@_teardown(weather=True)
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
        # the judge reads this claim's LAST capture; without one the cannot-show bar is UNMEASURED by construction
        t.screenshot(rect=_sky_rect(t))
    _r6_no_ordinary_rain(t)


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
    _r6_scorchfruit_fire_born(t)


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
            # The first order must interrupt: queued behind a sleeper it never starts. A colonist's harvest can fail
            # (PlantHarvestYield 0.7) and one pod takes ~1100 ticks, so three pods need ~3500.
            for i, p in enumerate(plants[:3]):
                t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Harvest",
                              targetAId=p["id"], queue=i > 0, waitTicks=0)
            _wait(t, 3600)
            gone = [p["id"] for p in plants[:3]
                    if p["id"] not in set(x.get("id") for x in _things(t, "RM_FE_Plant_ScorchFruit", _rs(rect), limit=20))]
            _note(t, "pods taken by the harvest", gone)
            if not gone:
                _fail("a harvest left every pod standing: it would regrow and be picked again")
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
        t.screenshot(rect=inside_map((x - 5 - FRAME_PAD, z - 3 - FRAME_PAD, 11 + 2 * FRAME_PAD, 9 + 2 * FRAME_PAD),
                                     _map_size(t)))   # the sealed room: the yield stack and its reference meat


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
        flight = None
        for _ in range(100):          # every 60 ticks: a sortie is short and was missable at 300
            _wait(t, 60)
            j = _job_of(t, hawk)
            seen.append((j, _count(t, "Fire", _rs(rect))))
            if j == FIRE_HAWK_JOB:
                # FIREHAWK_EMBER_FIX_WALKS_ITS_TWIG: a STATE read of the flight tracker (never a picture, never a watched
                # flight). The JobDef now carries tryStartFlying/ifFlyingKeepFlying, so the sortie's job.flying is True.
                r = t.bridge_call("jawa/static_call", type=EMBER_DRIVER, method="ProbeFlight", args=hawk)
                flight = (r or {}).get("result") if (r or {}).get("success") else r
                break
        _note(t, "fire-hawk job samples", seen)
        _note(t, "fire-hawk flight state during the ember job", flight)
        if _live(t) and isinstance(flight, str) and "job=" + FIRE_HAWK_JOB in flight and "jobFlying=False" in flight:
            if "cooldown=0" in flight:
                _fail("the ember sortie was WALKED: job.flying False with no flight cooldown (%s)" % flight)
            _unmeasured(t, "ember job not flying, but the hawk is on flight cooldown, so vanilla may have refused the take-off: %s" % flight)
        if _live(t) and FIRE_HAWK_JOB in [s_[0] for s_ in seen] and not isinstance(flight, str):
            _unmeasured(t, "the ember job was seen but ProbeFlight gave no readable flight state: %r" % (flight,))
        if _live(t) and not any(s_[1] for s_ in seen):
            _unmeasured(t, "no fire was alive beside the hawk at any sample: %r" % seen)
        if _live(t) and FIRE_HAWK_JOB not in [s_[0] for s_ in seen]:
            _fail("no %s job in 100 samples over 6000 ticks beside a live fire (job state read only)"
                  % FIRE_HAWK_JOB)
        # no capture here: the hawk was read flying=True during this sortie, and a flyer is never captured in flight
        # (owner: "For the third time, do not do live testing of flyers without a human present."; Pyrelands visit 3)
    _ten_firehawk(t)


WARMTH_FIELD = "RimMandrake.Pyrelands.FurnaceWarmthField"   # jawa/static_call target (CompFurnaceWarmthAura.cs)
FAR_WARMTH_CELLS = 11


@suite.chain("furnace_warmth")
@_teardown()
def furnace_warmth(t):
    _pad(t, PAD_WARMTH)
    t.clear_area(size=12)
    x, z = t.anchor
    with _comp(t, "furnacebeast_warmth", shows=["pyre_furnacebeast_warmth"]):
        _set(t, {"furnaceThermalEnabled": True})
        # CompFurnaceWarmthAura: radius = 4.9 x sqrt(baseBodySize / 3.2) x Lerp(0.35, 1, charge) (giant bs 9: x1.68); a fresh beast's charge is
        # 0, so its aura reaches 2.9 cells, and a wild beast wanders off a colonist walking after
        # it (run 7: 6-10 cells apart in 7 of 8 samples). Both stand in a 2x1 pen (a 4x3
        # make_empty_room), so they are never more than 1 cell apart.
        pen = t.bridge_call("jawa/make_empty_room", rect="%d,%d,4,3" % (x - 1, z - 1),
                            stuffDef="Steel")
        if _live(t):
            _ok(pen, "make_empty_room")
        # FURNACE_AURA_FIX_WARMS_THROUGH_WALLS: the aura is the OPEN-FIELD half, so the pen is unroofed (a room with open
        # roof uses the outdoor temperature); the enclosed arm below re-roofs it and expects no aura.
        t.bridge_call("jawa/set_roof_batch", ops="%d,%d,4,3" % (x - 1, z - 1), roofDef="None")
        bid = _spawn_wild(t, "RM_FurnaceBeast", x, z)
        r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x + 1, z=z, faction="player",
                          count=1)
        col = (((r or {}).get("pawns") or [{}])[0]).get("id")
        if col:
            t.session.track("pawn", col, x=x + 1, z=z)
        # the control: a second colonist 10+ cells off, outside every radius (max 4.9 x 1.68 = 8.2 cells at full charge)
        rf = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x + FAR_WARMTH_CELLS, z=z, faction="player",
                           count=1)
        far = (((rf or {}).get("pawns") or [{}])[0]).get("id")
        if far:
            t.session.track("pawn", far, x=x + FAR_WARMTH_CELLS, z=z)
        # L1 2026-10-15 (HARNESS): an undrafted colonist wandered out of the pen (1.0 -> 2.8 cells, behind its wall) in the
        # 360 sampled ticks and OffsetFor read 0; drafted, both stay on their cells (beside / FAR_WARMTH_CELLS off).
        for pid in (col, far):
            if pid:
                t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
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
        # STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY: the state half of the bar. FurnaceWarmthField.OffsetFor(Pawn) by ThingID
        # (jawa/static_call resolves Thing/Pawn args), with jawa/thing_ambient_temp recorded beside it: its delta
        # (pawn.AmbientTemperature - cell temperature) is every AmbientTemperature postfix, ours included.
        offs = {}
        for who, pid in (("beside", col), ("away", far)):
            if not pid:
                continue
            r = t.bridge_call("jawa/static_call", type=WARMTH_FIELD, method="OffsetFor", args=pid)
            # FURNACE_WARMTH_FIX_NO_SIGN_TO_READ: the readable warmth status is the recipient's inspect line (WarmthSign).
            sg = t.bridge_call("jawa/static_call", type=WARMTH_FIELD, method="WarmthSign", args=pid)
            amb = t.bridge_call("jawa/thing_ambient_temp", thing=pid)
            row = _pawn_row(t, pid) or {}
            b = _pawn_row(t, bid) or {}
            d = None
            if b.get("x") is not None and row.get("x") is not None:
                d = ((b["x"] - row["x"]) ** 2 + (b["z"] - row["z"]) ** 2) ** 0.5
            offs[who] = {"id": pid, "dist": d, "offset": (r or {}).get("result"), "staticCall": r if not (r or {}).get("success") else None,
                         "sign": ((sg or {}).get("result") or "") if (sg or {}).get("success") else None,   # the bridge drops an empty result
                         "ambient": (amb or {}).get("ambient"), "cellTemp": (amb or {}).get("cellTemp"),
                         "delta": (amb or {}).get("delta")}
        _note(t, "FurnaceWarmthField.OffsetFor beside / away (C)", offs)
        if _live(t):
            if not far:
                _fail("could not spawn the control colonist: %r" % rf)
            for who in ("beside", "away"):
                o = offs.get(who) or {}
                if o.get("offset") is None:
                    _unmeasured(t, "static_call OffsetFor(%s) refused - is the widened companion deployed? %r"
                                % (who, o.get("staticCall")))
            beside, away = float(offs["beside"]["offset"]), float(offs["away"]["offset"])
            if offs["away"]["dist"] is not None and offs["away"]["dist"] < FAR_WARMTH_CELLS - 1:
                _unmeasured(t, "the control colonist wandered within %.1f cells of the beast" % offs["away"]["dist"])
            if beside <= 0.0:
                _fail("colonist beside the penned furnace-beast felt no warmth: OffsetFor = %r (dist %r)"
                      % (beside, offs["beside"]["dist"]))
            if away != 0.0:
                _fail("colonist %r cells from the furnace-beast felt warmth %r: the field leaks past its radius"
                      % (offs["away"]["dist"], away))
            sign_b, sign_a = offs["beside"].get("sign"), offs["away"].get("sign")
            if sign_b is None or sign_a is None:
                _unmeasured(t, "static_call WarmthSign refused - is the sign build deployed? beside %r away %r" % (sign_b, sign_a))
            if beside >= 0.5 and "furnace-beast" not in sign_b:
                _fail("colonist beside the furnace-beast (offset %r) shows no readable warmth sign: WarmthSign = %r" % (beside, sign_b))
            if sign_a:
                _fail("colonist out of range shows a warmth sign %r" % sign_a)
            # Enclosed arm: roof the pen. Inside an enclosed room the vanilla heat pusher warms the room, so the aura must
            # not stack on it (OffsetFor == 0 for the same colonist at the same distance).
            t.bridge_call("jawa/set_roof_batch", ops="%d,%d,4,3" % (x - 1, z - 1), roofDef="RoofConstructed")
            _wait(t, 2)
            r = t.bridge_call("jawa/static_call", type=WARMTH_FIELD, method="OffsetFor", args=col)
            enclosed = (r or {}).get("result") if (r or {}).get("success") else None
            _note(t, "OffsetFor beside, pen roofed (enclosed room)", enclosed)
            if enclosed is None:
                _unmeasured(t, "static_call OffsetFor (enclosed arm) refused: %r" % r)
            if float(enclosed) != 0.0:
                _fail("colonist in a roofed pen beside the furnace-beast still felt the aura %r: it stacks on the room's heat pusher"
                      % enclosed)
            # thing_ambient_temp's delta is recorded, never graded: the sun-heat (CreatureBehaviors), forge-plume and
            # solar-mirror mods postfix the same getter, and the pen is walled while the control stands in the open.
        # the subject: the beast and the colonist in the pen, and the control colonist FAR_WARMTH_CELLS off
        t.screenshot(rect=frame_rect([(x - 1, z - 1), (x + 2, z + 1), (x + FAR_WARMTH_CELLS, z)], _map_size(t)))


# Owner card 2026-11-08 01:01 "heat with no cap": a closed pen settles at the weather plus this (PyrelandsTuning.
# FurnaceRoomAboveOutdoorC, pinned by selftest_pyrelands_site): a 75 C oven at a 50 C site, heatstroke over hours.
FURNACE_ROOM_ABOVE_C = 25.0
FURNACE_ROOM_MIN_OVER = 10.0   # "clearly hotter": the 5x5 inside reaches the ceiling in ~2,600 of the series' 12,600 ticks
FURNACE_ROOM_SLACK = 8.0       # over the ceiling: with no ceiling at all the same room runs to ~+64 C


def room_heat_verdict(end, above=FURNACE_ROOM_ABOVE_C, min_over=FURNACE_ROOM_MIN_OVER, slack=FURNACE_ROOM_SLACK):
    """pyre_furnacebeast_heats_room on the last (beast room, control room) read -> (ok, why): the beast room is clearly
    hotter than the control, which stands at the weather, and the outdoor-relative ceiling held."""
    if not end or None in end:
        return False, "temperature unread at the end of the series: %r" % (end,)
    over = end[0] - end[1]
    if over < min_over:
        return False, "beast room is not clearly hotter than the matched control (%+.1f C, under %+.0f)" % (over, min_over)
    if over > above + slack:
        return False, "beast room ran %+.1f C over the control: the %+.0f C ceiling did not hold" % (over, above)
    return True, "beast room %+.1f C over the control (ceiling %+.0f C)" % (over, above)


@suite.chain("furnace_room")
@_teardown()
def furnace_room(t):
    """Two matched 7x7 rooms at the site's own temperature, one holding a furnace-beast. Owner card 2026-11-08 01:01
    ("heat with no cap"): the beast room climbs past the weather to the ceiling, FURNACE_ROOM_ABOVE_C over it, so it
    must read clearly hotter than the control and no more than the ceiling plus slack over it (room_heat_verdict)."""
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
        series = []
        for _ in range(12):
            _wait(t, 1000)
            series.append([tv(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % c))
                           for c in (ca, cb)])
        after = [t.bridge_call("jawa/room_get", x=c[0], z=c[1]) for c in (ca, cb)]
        if _live(t):
            _note(t, "rooms after the series (A, B)", [dict((k, v) for k, v in (r or {}).items()
                                                            if k not in ("operation", "state")) for r in after])
            inside = (beast.get("x") is not None and a[0] < beast["x"] < a[0] + 6
                      and a[1] < beast["z"] < a[1] + 6)
            _note(t, "room temperatures", {"ambient": amb, "series": series,
                                           "beastAt": (beast.get("x"), beast.get("z")),
                                           "beastInsideRoomA": inside,
                                           "roomsFound": [(r or {}).get("roomsFound") for r in rooms]})
            if not all((r or {}).get("roomsFound") for r in rooms):
                _fail("make_empty_room did not produce two enclosed rooms: %r" % rooms)
            if not inside:
                _unmeasured(t, "spawn_pawn scattered the beast out of room A (at %r)"
                            % ((beast.get("x"), beast.get("z")),))
            # Both rooms stay at the map's own temperature: the first version chilled them to 10 C, under the pusher's old
            # 24 C cap, and so passed while the beast heated nothing at the biome's real 50 C.
            end = series[-1]
            if None in end:
                _unmeasured(t, "no temperature read at the end of the series: %r" % (series,))
            ok, why = room_heat_verdict(end)
            if not ok:
                _fail("%s: %r" % (why, series))
        t.screenshot(rect=(a[0], a[1], 18, 7))


# Owner card 2026-11-08 01:01 "it ignites grass it sleeps in" (pyre_furnacebeast_sleep_ignites).
FURNACE_BED = "RimMandrake.Pyrelands.CompFurnaceBedIgnition"   # ProbeSleep: the sleeper's state read
SLEEP_GRACE_TICKS = 1250     # PyrelandsTuning.FurnaceSleepIgnitionGraceTicks (these three pinned by selftest_pyrelands_site)
SLEEP_MTB_TICKS = 3750       # PyrelandsTuning.FurnaceSleepIgnitionMtbTicks: with the grace, ~2 h of sleep on average
SLEEP_POLL_TICKS = 250       # PyrelandsTuning.FurnaceSleepIgnitionCheckTicks: one poll per roll
SLEEP_FAIL_ROLL_TICKS = 5 * SLEEP_MTB_TICKS      # ~7.5 h rolling on grass with no fire FAILS (a working roll: e^-5, 0.7%)
SLEEP_CONTROL_ROLL_TICKS = 3 * SLEEP_MTB_TICKS   # the bare-ground span: a roll that ignored the plant lights it 95% of runs
SLEEP_WAIT_TICKS = 30000     # the row's ceiling: the grace, the FAIL span and one re-sleep
SLEEP_REORDERS = 4           # LayDown re-orders per beast (it woke, or lay down off its plot)


def _kv_int(v, default=-1):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _slept_through(prev, cur):
    """Two ProbeSleep polls asleep on one cell with the rest clock still running: it lay there the whole interval."""
    return (prev.get("awake") == "False" and cur.get("awake") == "False" and prev.get("cell") == cur.get("cell")
            and _kv_int(cur.get("restingTicks")) > _kv_int(prev.get("restingTicks")) >= 0)


def sleep_ignition_verdict(a, b, step=SLEEP_POLL_TICKS, grace=SLEEP_GRACE_TICKS, fail_roll=SLEEP_FAIL_ROLL_TICKS,
                           control_roll=SLEEP_CONTROL_ROLL_TICKS):
    """pyre_furnacebeast_sleep_ignites over the two sleepers' polls (ProbeSleep fields plus 'fire', the Fire count within
    2 cells of the sleeper) -> (verdict, why, spans), verdict 'PASS', 'FAIL' or None (keep polling). a lies in grass,
    b (the control) on bare ground. An interval counts only when the beast slept through it past the grace: on a
    flammable plant for a, on a plantless cell for b. A fire, or the sleep roll's own record (litAfterTicks), appearing
    beside b over such an interval FAILS; a PASSES once its sleep roll's record stands with a Fire seen beside it by the
    next poll and b has slept control_roll ticks; a FAILS after fail_roll ticks of rolling with no light."""
    roll_b = 0
    for prev, cur in zip(b, b[1:]):
        if not _slept_through(prev, cur) or prev.get("plant") != "none":
            continue
        if cur.get("litAfterTicks") != prev.get("litAfterTicks") and _kv_int(cur.get("litAfterTicks")) >= 0:
            return "FAIL", "the sleep roll lit the bare-ground control at cell %s (%r)" % (cur.get("cell"), cur), {"rollB": roll_b}
        if cur.get("fire", 0) > 0 and not prev.get("fire", 0):
            return "FAIL", "fire beside the control asleep on bare ground at cell %s (%r)" % (cur.get("cell"), cur), {"rollB": roll_b}
        if _kv_int(prev.get("restingTicks")) >= grace:
            roll_b += step
    roll_a = 0
    for prev, cur in zip(a, a[1:]):
        if _slept_through(prev, cur) and prev.get("flammablePlant") == "True" and _kv_int(prev.get("restingTicks")) >= grace:
            roll_a += step
    lit = next((i for i, s in enumerate(a) if _kv_int(s.get("litAfterTicks")) >= 0), None)
    spans = {"rollA": roll_a, "rollB": roll_b, "litAfterTicks": _kv_int(a[lit].get("litAfterTicks")) if lit is not None else None}
    if lit is not None:
        seen = [s.get("fire", 0) for s in a[lit:lit + 2]]
        if not any(seen):
            if len(seen) < 2:
                return None, "lit after %s ticks asleep, fire not yet read" % spans["litAfterTicks"], spans
            return "FAIL", "the sleep roll lit the grass (after %s ticks asleep) but no Fire stood beside the beast by the next poll" \
                   % spans["litAfterTicks"], spans
        if roll_b >= control_roll:
            return "PASS", "grass caught after %s ticks (%.1f h) asleep; the control slept %d ticks on bare ground, no fire" \
                   % (spans["litAfterTicks"], spans["litAfterTicks"] / 2500.0, roll_b), spans
        return None, "lit; the control has slept %d of %d ticks" % (roll_b, control_roll), spans
    if roll_a >= fail_roll:
        return "FAIL", "the beast slept %d ticks (%.1f h) past the grace on a flammable plant and never lit it" \
               % (roll_a, roll_a / 2500.0), spans
    return None, "rolled %d of %d ticks on grass, the control %d of %d on bare ground" % (roll_a, fail_roll, roll_b, control_roll), spans


@suite.chain("furnace_sleep")
@_teardown(fire=True, weather=True)
def furnace_sleep(t):
    """Owner card 2026-11-08 01:01: a furnace-beast asleep on a cell holding grass (any flammable plant) sets it alight,
    after ~2 h of sleep on average, never at once and never on a cell with no plant. Two wild beasts are laid down on a
    concrete pad: A on a 5x5 of ember grass, B (the control) on a 5x5 of bare RM_FE_Ground_Soil, which burns
    (Flammability 0.6), so a roll that ignored the plant would light it. Every SLEEP_POLL_TICKS both are read with
    CompFurnaceBedIgnition.ProbeSleep and the Fire within 2 cells of each is counted; sleep_ignition_verdict grades.
    The wake-up smoulder (any ground, 18%) is the older, separate roll: a fire beside a woken B is put out before it
    lies down again, and only the sleep roll's own record can pass A. Weather locked Clear: rain would put a small
    grass fire out before a poll saw it.
    Lessons from runs go here."""
    _pad(t, PAD_SLEEP)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    plots = {"A": (x - 8, z - 2, 5, 5), "B": (x + 3, z - 2, 5, 5)}
    beds = dict((k, (r[0] + 2, r[1] + 2)) for k, r in plots.items())
    # shows=[] until pyre_furnacebeast_sleep_ignites is a bar of the walk's north star (an orphan shows= id refuses the
    # run, floor.orphan_shows); this component then claims it.
    with _comp(t, "furnacebeast_sleep_ignites", shows=[]):
        _set(t, {"furnaceThermalEnabled": True})
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        # All concrete but the two plots, 6 cells apart: A's fire cannot reach B, nor the site's own grass.
        t.bridge_call("jawa/set_terrain", x=rect[0], z=rect[1], terrainDef=FIREBREAK, width=rect[2], height=rect[3],
                      layer="top")
        t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % _rs(rect))
        for r in plots.values():
            _soil(t, r)
        _plants(t, "RM_FE_Plant_EmberGrass", plots["A"])
        planted = _GEN.get("last_plants")
        ids = dict((k, _spawn_wild(t, "RM_FurnaceBeast", c[0], c[1])) for k, c in beds.items())
        orders = dict((k, []) for k in beds)

        def lay_down(k):
            t.bridge_call("jawa/pawn_need", pawn=ids[k], action="need", need="Food", level=1.0)
            t.bridge_call("jawa/pawn_need", pawn=ids[k], action="need", need="Rest", level=0.05)
            r = t.bridge_call("jawa/ordered_job", pawnId=ids[k], jobDef="LayDown", targetAX=beds[k][0],
                              targetAZ=beds[k][1], waitTicks=0)
            orders[k].append(dict((f, (r or {}).get(f)) for f in ("success", "accepted", "afterJobDef", "message")))

        def probe(k, tick):
            r = t.bridge_call("jawa/static_call", type=FURNACE_BED, method="ProbeSleep", args=ids[k])
            if not _live(t):
                return {}
            if not (r or {}).get("success"):
                _unmeasured(t, "static_call ProbeSleep refused - is the sleep-ignition build deployed? %r" % r)
            kv = parse_kv(r.get("result"))
            c = xz_of(kv.get("cell"))
            if kv.get("spawned") != "true" or c is None:
                _unmeasured(t, "furnace-beast %s is not on the map: %r" % (k, kv))
            kv["fire"] = _count(t, "Fire", "%d,%d,5,5" % (c[0] - 2, c[1] - 2))
            kv["tick"] = tick
            return kv

        for k in beds:
            lay_down(k)
        samples = dict((k, []) for k in beds)
        verdict, why, spans, waited = None, "", {}, 0
        while waited < SLEEP_WAIT_TICKS:
            _wait(t, SLEEP_POLL_TICKS)
            waited += SLEEP_POLL_TICKS
            for k in beds:
                samples[k].append(probe(k, waited))
            if not _live(t):
                break
            verdict, why, spans = sleep_ignition_verdict(samples["A"], samples["B"])
            if verdict:
                break
            for k in beds:
                sm = samples[k][-1]
                if len(orders[k]) > SLEEP_REORDERS:
                    continue
                if k == "A":
                    stray = _kv_int(sm.get("litAfterTicks")) < 0 and sm.get("awake") == "False" and sm.get("flammablePlant") != "True"
                else:
                    stray = spans.get("rollB", 0) < SLEEP_CONTROL_ROLL_TICKS and sm.get("awake") == "False" and sm.get("plant") != "none"
                woke = sm.get("job") != "LayDown" and (k == "B" or _kv_int(sm.get("litAfterTicks")) < 0)
                if not (stray or woke):
                    continue
                if k == "B" and sm.get("fire"):   # the wake-up smoulder, not this row's roll: put out before it lies down
                    t.bridge_call("jawa/map_fire", action="extinguish", rect=_rs((plots["B"][0] - 3, plots["B"][1] - 3, 11, 11)))
                lay_down(k)
        _note(t, "grass plot planting (A)", planted)
        _note(t, "LayDown orders", orders)
        _note(t, "sleeper polls (tick, awake, job, restingTicks, cell, plant, litAfterTicks, fire within 2)",
              dict((k, [(s.get("tick"), s.get("awake"), s.get("job"), s.get("restingTicks"), s.get("cell"), s.get("plant"),
                         s.get("litAfterTicks"), s.get("fire")) for s in v]) for k, v in samples.items()))
        if _live(t):
            _note(t, "sleep ignition spans (ticks)", spans)
            if verdict == "FAIL":
                _fail(why)
            if verdict != "PASS":
                _unmeasured(t, "no verdict in %d ticks: %s" % (waited, why))
        t.screenshot(rect=(plots["A"][0] - 1, plots["A"][1] - 1, 18, 7))
    _ten_furnace_sleep(t)


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


# ---- burrow diagnostic chain (TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED, TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL) ----
# PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE's probe, formerly a scratch copy appended to an out-of-repo validation.py: a wild
# ashwallow's job sampled every 10 ticks after a fire is lit beside it (`near`), or 16 cells off (`ctrl`). REGISTERED ONLY
# when PYRE_BURROW_DIAG=1, so a normal suite run never pays for it. Driven by diag/burrow_trials.sh, which reloads the site
# fixture before EVERY trial: repeat trials on one map are warm (the first fire leaves a standing-burn window, so only
# trial 1 was a cold dive), and ~8000 ticks of repeats at 52 C cooked 2 of 3 support colonists. Run one trial per
# reload (BURROW_NEAR=1 BURROW_CTRL=0, the script's defaults); the row is heat-guarded like every other non-needs row.
def _diag_env(name, default):
    return int(os.environ.get(name, default))


@_teardown(fire=True)
def burrowers_diag(t):
    _pad(t, PAD_BURROW)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    out_path = os.environ.get("BURROW_DIAG_OUT")
    out = {"anchor": [x, z], "rect": rect, "trials": []}
    with _comp(t, "burrowers_dive_diag", shows=[]):
        _set(t, {"burrowOnFireEnabled": True})
        _firebreak(t, rect)
        plan = ([("near", x + 5)] * _diag_env("BURROW_NEAR", "1")
                + [("ctrl", x + 16)] * _diag_env("BURROW_CTRL", "0"))
        for i, (kind, gx) in enumerate(plan):
            _extinguish(t)
            if _live(t):
                import northstar_driver.site as _site
                _site.despawn_pawns_in(t.session, (x - 30, z - 30, 60, 60))
            _wait(t, _diag_env("BURROW_QUIET", "130"))
            _soil(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            g = _spawn_wild(t, "RM_Ashwallow", gx, z)
            gi = t.bridge_call("rimworld/get_game_info") or {}
            _fire(t, (x - 3, z - 3, 6, 6))
            samples = []
            seen = None
            for k in range(_diag_env("BURROW_SAMPLES", "30")):
                _wait(t, 10)
                j = _job_of(t, g)
                samples.append(j)
                if seen is None and j and "Burrow" in str(j):
                    seen = (k + 1) * 10
            row = _pawn_row(t, g, health=True)
            tr = {"i": i, "grazerId": g, "fireTick": gi.get("ticksGame"), "kind": kind, "grazerX": gx,
                  "jobs": samples, "burrowedAt": seen, "burrowedHediffEnd": _has_hediff(row, "RM_Burrowed"),
                  "firstFlee": next(((k + 1) * 10 for k, j in enumerate(samples) if j and "Flee" in str(j)), None),
                  "pos": [(row or {}).get("x"), (row or {}).get("z")]}
            out["trials"].append(tr)
            if t.session is not None:
                print("[diag] " + json.dumps(tr), flush=True)
            if out_path:
                with open(out_path, "w") as f:
                    json.dump(out, f, indent=1, default=str)
        _extinguish(t)
        _note(t, "burrow diag", out)


if os.environ.get("PYRE_BURROW_DIAG") == "1":
    suite.chain("burrowers_diag")(burrowers_diag)


BURROW_REACTION = "RimMandrake.Pyrelands.RM_BurrowHeatReaction"   # ProbeDome(Pawn) via jawa/static_call
DOME_HOLD_TICKS = 600      # PyrelandsTuning.BurrowHeatHoldTicks


def _dome_probe(t, pid):
    r = t.bridge_call("jawa/static_call", type=BURROW_REACTION, method="ProbeDome", args=pid or "")
    if not _live(t):
        return {}
    if not (r or {}).get("success"):
        _unmeasured(t, "static_call ProbeDome refused (widened companion + this Pyrelands DLL deployed?): %s" % str(r)[:200])
    return parse_kv(r.get("result"))


@suite.chain("heat_dome")
@_teardown()
def heat_dome(t):
    """ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE (owner card: assume the dome stance when heat-attacked). A heat hit (Burn:
    armorCategory Heat, and unlike Flame it attaches no fire, so no ground fire ever exists on the pad) must dome the
    ashwallow at once; it surfaces once the hold runs out with no fire near; with the dome toggle off a hit does nothing."""
    _pad(t, PAD_DOME)
    t.clear_area(size=12)
    x, z = t.anchor
    g = None   # bound before the first component: a failed spawn must not crash the toggle-off component below
    with _comp(t, "ashwallow_domes_on_heat_hit", toggle="burrowDomeOnHeatHit"):
        _set(t, {"burrowOnFireEnabled": True, "burrowDomeOnHeatHit": True})
        g = _spawn_wild(t, "RM_Ashwallow", x, z)
        _wait(t, 30)
        before = _dome_probe(t, g)
        hit = t.bridge_call("jawa/damage", damageDef="Burn", amount=2.0, thingId=g)
        _wait(t, 5)
        domed = _dome_probe(t, g)
        _wait(t, 60)
        # bodyGraphic is the graphic of the LAST draw, and an off-screen pawn is not drawn: frame it first.
        t.screenshot(rect=(x - 6, z - 6, 12, 12))
        drawn = _dome_probe(t, g)
        _wait(t, DOME_HOLD_TICKS + 300)
        after = _dome_probe(t, g)
        row = _pawn_row(t, g, health=True)
        _note(t, "dome probe before / 5 ticks after the Burn hit / +60 / after the hold",
              {"before": before, "hit": (hit or {}).get("results", hit), "domed": domed, "drawn": drawn, "after": after})
        if _live(t):
            if before.get("fireNear") == "True" or before.get("burrowed") == "True":
                _unmeasured(t, "the pad was not quiet before the hit: %r" % before)
            if domed.get("burrowed") != "True" or domed.get("job") != "RM_Burrow":
                _fail("a Burn hit with no fire near did not dome the ashwallow: %r" % domed)
            if int(domed.get("heatHoldUntil", -1)) < int(domed.get("now", 0)):
                _fail("domed, but the heat hold is not running: %r" % domed)
            if domed.get("domeArt") == "True" and drawn.get("bodyGraphic") != domed.get("domeTexPath"):
                _fail("the dome art is installed but the body still draws %r while burrowed" % drawn.get("bodyGraphic"))
            if after.get("burrowed") == "True" and after.get("fireNear") != "True":
                _fail("still domed %d ticks after the hold ran out with no fire near: %r" % (DOME_HOLD_TICKS + 300, after))
            if not row or row.get("dead") or row.get("downed"):
                _fail("the ashwallow did not come through a 2-point Burn: %r" % row)
            if domed.get("domeArt") != "True":
                _note(t, "dome pose art", "not installed at %s: behaviour proven, the pose draws the standing body"
                      % domed.get("domeTexPath"))
    with _comp(t, "ashwallow_heat_dome_toggle_off", toggle="burrowDomeOnHeatHit"):
        _set(t, {"burrowDomeOnHeatHit": False})
        t.bridge_call("jawa/damage", damageDef="Burn", amount=2.0, thingId=g)
        _wait(t, 5)
        off = _dome_probe(t, g)
        _note(t, "dome probe 5 ticks after a Burn hit with the toggle off", off)
        _set(t, {"burrowDomeOnHeatHit": True})
        if _live(t) and off.get("burrowed") == "True" and off.get("fireNear") != "True":
            _fail("burrowDomeOnHeatHit off, yet a Burn hit with no fire near domed the ashwallow: %r" % off)
        t.screenshot(rect=(x - 6, z - 6, 12, 12))
    _r6_heat_dome(t)


# --------------------------------------------------------------------------- long waits last

@suite.chain("embergrass_regrow")
@_teardown(fire=True)
@_wildlife_shielded
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
        # The real clock at the shipped settings: a compressed override cannot stand in here, because the bursts, not the
        # spawner, carry the scar (measured: 9 regrow days filled a scar as fast as 3).
        d0 = new_count()
        fracs = []
        for days in REGROW_SAMPLE_DAYS:
            _wait(t, int(days * 60000) - (fracs[-1][0] * 60000 if fracs else 0))
            fracs.append((days, (float(new_count()) / len(pre_ids)) if pre_ids else None))
        temp = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % t.anchor)
        _note(t, "regrow on the real clock", {"pre": len(pre_ids), "afterBurn": d0, "fractions": fracs, "temp": temp})
        if _live(t):
            if not pre_ids:
                _fail("regrow cohort had no pre-burn plants")
            if not fracs[0][1] or fracs[0][1] < REGROW_FIRST_DAYS_FRAC:
                _fail("not visibly re-greening within a few days: %r" % (fracs,))
            if fracs[0][1] > REGROW_FIRST_DAYS_MAX:
                _fail("re-greens too fast: over %.0f%% green by day %s, so it is largely green long before about a week: %r"
                      % (REGROW_FIRST_DAYS_MAX * 100, fracs[0][0], fracs))
            if not fracs[-1][1] or fracs[-1][1] < REGROW_WEEK_FRAC:
                _fail("not largely green again within about a week: %r" % (fracs,))
        t.screenshot(rect=regrow)
    _ten_embergrass_regrow(t)
    _r6_embergrass_regrow(t)


def _live_setting(t, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
    if not _live(t):
        return None
    if not (r or {}).get("success") or r.get("value") is None:
        _fail("cannot read %s.%s: %r" % (SETTINGS, field, r))
    return r["value"]


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


def herd_pace(before, after, ticks):
    """RIMMANDRAKE_PACE_HERD_WINDOW_FROM_MEASURED_SAND_SPEED: one ullai's pace on the site, in cells per tick: the median
    straight-line displacement over `ticks` of every ullai read at both ends ({id: (x, z)}). The median is the walker's
    pace when a few are held back (no reachable cell) or dash for shade. -> (pace or None, why); None when nothing was read
    at both ends or no ullai moved, never a guessed pace. Visit 1 (2026-11-15) measured ~19 cells per 1,000 ticks on deep ash
    (Odyssey sand depth since 2026-11-08); the old fixed step assumed ~100 cells per 2,500."""
    both = sorted(k for k in before if k in after)
    if not both or not ticks:
        return None, "ullai read at both ends of the pace sample: %d of %d" % (len(both), len(before))
    d = sorted(_dist(before[k], after[k]) for k in both)
    n = len(d)
    med = d[n // 2] if n % 2 else (d[n // 2 - 1] + d[n // 2]) / 2.0
    why = "%d ullai over %d ticks: cells moved %s, median %.1f" % (n, ticks, [round(x, 1) for x in d], med)
    if med <= 0:
        return None, why + " (no ullai walked)"
    return med / float(ticks), why + " -> %.4f cells/tick" % (med / float(ticks))


def herd_window(a0, pace, min_close=HERD_MIN_CLOSE, margin=HERD_PACE_MARGIN, cap=HERD_STEP_MAX_TICKS):
    """The motion window in ticks: closing min_close of a0 (the centroid's start distance to A) at the measured `pace`,
    times the margin, rounded up to HERD_STEP_ROUND. -> (ticks or None, why); None for an unread or zero pace, and for a
    pace too slow to close within `cap` (never a clipped window)."""
    if not pace or pace <= 0:
        return None, "no measured pace (%r)" % (pace,)
    need = min_close * a0 / pace
    w = int(-(-need * margin // HERD_STEP_ROUND) * HERD_STEP_ROUND)
    why = "close %.0f%% of %.1f cells at %.4f cells/tick: %.0f ticks x %.1f margin -> %d" % (
        100 * min_close, a0, pace, need, margin, w)
    if w > cap:
        return None, why + " > the %d-tick ceiling" % cap
    return w, why


def _herd_positions(t, ids):
    """{id: (x, z)} of the spawned herd, from one site_state read (every spawned pawn on the map)."""
    r = t.bridge_call("jawa/site_state")
    if not _live(t):
        return {}
    want, out = set(ids), {}
    for p in ((r or {}).get("pawns") or []):
        if p.get("id") in want and p.get("x") is not None and p.get("z") is not None:
            out[p["id"]] = (float(p["x"]), float(p["z"]))
    return out


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
    """TESTENV_STORM_FIRES_HARDEN_DECOY_BURN (r6 p4, 2026-10-15): a storm chain run just before
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
      3 motion (MEASURED): the herd's first HERD_PACE_SAMPLE_TICKS give one ullai's pace on deep ash (herd_pace); the
        window is sized from it (herd_window, RIMMANDRAKE_PACE_HERD_WINDOW_FROM_MEASURED_SAND_SPEED: a fixed 2,500 ticks
        assumed ~100 cells, the sand walks ~48); the herd centroid closes on A over the window (herd_verdict).
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
        ids = [_spawn_wild(t, HERD_RACE, hx + (i % 5) - 2, hz + (i // 5) * 2 - 1) for i in range(HERD_SIZE)]
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
        p0 = _herd_positions(t, ids)
        _wait(t, HERD_PACE_SAMPLE_TICKS)
        p1 = _herd_positions(t, ids)
        if not _live(t):
            return
        if len(p0) < HERD_SIZE // 2 or len(p1) < HERD_SIZE // 2:
            _unmeasured(t, "the ullai pace: site_state read %d then %d of %d spawned ullai" % (len(p0), len(p1), HERD_SIZE))
        pace, pwhy = herd_pace(p0, p1, HERD_PACE_SAMPLE_TICKS)
        if pace is None:
            _fail("the ullai pace on deep ash is unmeasurable with jobs issued to A: " + pwhy)
        window, wwhy = herd_window(_dist(start, PAD_HERD_OLD), pace)
        _note(t, "the ullai pace on deep ash, measured on the site, and the motion window it sizes",
              {"pace": pwhy, "window": wwhy})
        if window is None:
            _fail("the ullai pace on deep ash is too slow for the herd to close on A: %s; %s" % (pwhy, wwhy))
        _wait(t, max(0, window - HERD_PACE_SAMPLE_TICKS))
        e = _probe_herd(t, issue=False)
        end = (float(e.get("cx", -1)), float(e.get("cz", -1))) if int(e.get("n", 0)) > 0 else None
        ok, why = herd_verdict(start, end, PAD_HERD_OLD, PAD_HERD_NEW)
        _note(t, "herd motion over the paced %d ticks (INFERRED beyond it: the 0.04 chance cadence brings the herd unforced "
                 "within two days; never stepped)" % window, {"start": d, "end": e, "pace": pwhy, "verdict": why})
        if not ok:
            _fail("the herd did not close on the two-day-old burn: " + why)
        # the subject: the herd where it stands now, and burn A it walks to
        t.screenshot(rect=frame_rect(list(_herd_positions(t, ids).values()) + [PAD_HERD_OLD], _map_size(t)))
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
        # no capture: an XML read has no subject on the map, and this row claims no bar a judge reads
    _independent(t)
    with _comp(t, "giant_furnace_beast", toggle="furnaceBeastGiant"):
        root = ET.parse(os.path.join(here, "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")).getroot()
        fb = [d for d in root.findall("ThingDef") if d.findtext("defName") == "RM_FurnaceBeast"]
        if not fb or fb[0].findtext("race/baseBodySize") != "9":
            _fail("RM_FurnaceBeast is not bs 9 in XML")
        live = _get_defs(t, "ThingDef/RM_Ullai;PawnKindDef/RM_Ullai;ThingDef/RM_FurnaceBeast", "race")
        if _live(t) and len(live) < 2:
            _fail("ullai / furnace-beast defs missing live: %r" % sorted(live))
        # no capture: no furnace-beast stands on the map in this row (visit 2: its frame showed none); the giant's look
        # is sc_furnace_giant's, which spawns one
    _independent(t)
    with _comp(t, "herd_follows_two_day_old_burn"):
        herd_follows_drive(t)
    _r6_ullai_and_giant(t)


# --------------------------------------------------------------------------- GPT pre-release hunt: PLAUSIBLE findings

GPT_TRIAGE = "Transient/release_push_2026-10-15/gpt_Pyrelands/TRIAGE.md"


def _save_world_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag", "save_world_check.py")
    spec = importlib.util.spec_from_file_location("pyre_save_world_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _unproven(t, name, why):
    """A PLAUSIBLE finding no existing tool reaches yet: recorded UNMEASURED (never PASS) with the exact procedure, so the
    run sheet names it (same shape as PyrelandsMechanics' unproven_bars)."""
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    with t.component(name, beyond_toggle=True):
        pass
    t.upstream_failed = False
    t.upstream_reason = ""


@suite.chain("gpt_hunt_plausible")
@_teardown(fire=True)
def gpt_hunt_plausible(t):
    """The PLAUSIBLE rows of the 2026-10-15 GPT hunt (GPT_TRIAGE). Each row's name says what a PASS means; a FAIL confirms
    the finding. FURNACE_CARAVAN_DIAGNOSE_HEARTH_GOES_COLD has NO row: the owner ruled caravan warmth out of scope
    ("Bah. Reverse decision. Drop the caravan warmth portion.", 2026-10-15)."""
    # Leftover furnace herds (the world migration was cut 2026-10-23) + TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS: an OFFLINE read
    # of the start save's world (diag/save_world_check.py). 2026-10-15 on CANONICAL_ASHKARR_START_2026-09-12.rws: no seeder
    # component, 0 herds, 1 TribeCivil faction. Re-run on the freeze candidate after the final paint.
    w = None
    with _comp(t, "save_holds_no_furnace_herds", beyond_toggle=True):
        herd = ("UNMEASURED", "not read (offline declaration probe)")
        try:
            if _live(t):
                sw = _save_world_module()
                sp = sw.default_save()
                if not sp:
                    _unmeasured(t, "the canonical start save was not found in the Saves folder")
                w = sw.read_world(sp)
                herd, tribes = sw.verdicts(w)
                w["_tribes"] = tribes
                _note(t, "start-save world read (seeder latch, herds, TribeCivil)", w)
        except (ExpectationFailed, _Unmeasured):
            raise
        except Exception as ex:   # noqa: BLE001 - a reader crash is ignorance, never a pass
            _unmeasured(t, "save_world_check raised %s: %s" % (type(ex).__name__, ex))
        if _live(t) and herd[0] == "FAIL":
            _fail(herd[1])
        if _live(t) and herd[0] == "UNMEASURED":
            _unmeasured(t, herd[1])
    _independent(t)
    with _comp(t, "tribes_lookup_one_faction", beyond_toggle=True):
        tribes = (w or {}).get("_tribes") or ("UNMEASURED", "no world read")
        if _live(t) and tribes[0] == "FAIL":
            _fail(tribes[1])
        if _live(t) and tribes[0] == "UNMEASURED":
            _unmeasured(t, tribes[1])
    _independent(t)

    # FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT (CONFIRMED and fixed 2026-10-15): vanilla Soil/Sand/Gravel are scorchable ground,
    # so the fire-tick hook now also needs the map's biome to opt in (FireEcologyBiomeGate: the Pyrelands, or the cross-biome
    # setting). A validation map is a Pyrelands map, where a Soil burn fruits by design, so the gate is measured by static_call
    # against the real TemperateForest / RM_Pyrelands BiomeDefs and the current map's cached answer; the offline fuzz drives
    # the same composition through the fire-tick gates (forest fire, cross-biome off/on).
    with _comp(t, "fire_ecology_gated_by_biome", beyond_toggle=True):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.FireEcologyBiomeGate", method="ProofForestGate")
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        _note(t, "ProofForestGate", text or r)
        if _live(t):
            if not text.startswith("FORESTGATE"):
                _unmeasured(t, "ProofForestGate gave no answer (is the build with the probe deployed?): %r" % text[:200])
            want = ("forestOff False", "forestEverywhere True", "forestListed True", "forestOtherListed False",
                    "pyrelandsOff True", "mapCacheFollows True")
            bad = [w for w in want if w not in text]
            if bad:
                _fail("fire ecology is not confined to the Pyrelands unless cross-biome opts a biome in (expected %s): %s"
                      % (", ".join(bad), text))
    _independent(t)

    # FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE: vanilla's default TargetingParameters has canTargetFires=false and
    # canTargetLocations=false, so the sprayer's Verb_Shoot must set both (fixed 2026-10-15, the incendiary launcher's
    # shape). Read from the def; the live confirm is draft a colonist holding RM_FE_FirefoamSprayer and target a
    # free-standing fire and an empty cell.
    with _comp(t, "firefoam_can_aim_at_fire", beyond_toggle=True):
        import xml.etree.ElementTree as ET
        root = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs", "ThingDefs_Sprayer",
                                     "FirefoamSprayer.xml")).getroot()
        verbs = [li for d in root for li in d.findall("verbs/li") if (li.findtext("verbClass") or "") == "Verb_Shoot"]
        if not verbs:
            if _live(t):
                _unmeasured(t, "no Verb_Shoot found in FirefoamSprayer.xml (the read is blind)")
            verbs = [ET.Element("li")]
        tp = verbs[0].find("targetParams")
        fires = tp is not None and (tp.findtext("canTargetFires") or "").strip().lower() == "true"
        cells = tp is not None and (tp.findtext("canTargetLocations") or "").strip().lower() == "true"
        _note(t, "sprayer verb targetParams", {"canTargetFires": fires, "canTargetLocations": cells})
        if _live(t) and not (fires and cells):
            _fail("the firefoam sprayer's verb cannot target %s (no targetParams; vanilla defaults are false)"
                  % " or ".join(x for x, ok in (("a fire", fires), ("open ground", cells)) if not ok))
        if _live(t):
            # Live: a throwaway colonist holding the sprayer asks the targeter's own questions of a fire and an open cell.
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.RM_FirefoamAimProof", method="ProofAim")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            _note(t, "ProofAim", text or r)
            if not text.startswith("FIREFOAM"):
                _unmeasured(t, "ProofAim gave no answer (is the build with the probe deployed?): %r" % text[:200])
            if "control fire False cell False" not in text:
                _unmeasured(t, "the vanilla-default control did not refuse, so the probe cannot see a no: %r" % text[:200])
            if not text.startswith("FIREFOAM fire True | cell True | validFire True | validCell True | hitFire True | hitCell True"):
                _fail("a colonist holding the sprayer cannot aim at a fire or open ground: %s" % text[:200])
    _independent(t)

    # SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS: designate, build a wall on the cell, ask the work giver (ProofShovelUnderWall).
    with _comp(t, "shovel_refuses_under_wall", toggle="sandShovelEnabled"):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.RM_TerrainDigProof", method="ProofShovelUnderWall")
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        _note(t, "ProofShovelUnderWall", text or r)
        if _live(t):
            if not text.startswith("UNDERWALL"):
                _unmeasured(t, "ProofShovelUnderWall gave no answer (is the build with the probe deployed?): %r" % text[:200])
            if "hasJobBeforeWall False" in text:
                _unmeasured(t, "the designated sand cell had no job even before the wall (the probe cannot see): %s" % text)
            if "hasJobUnderWall True" in text:
                _fail("CONFIRMED: a shovel order under a wall is still a job (the dig would swap terrain under it): %s" % text)
            if "hasJobBeforeWall True" not in text or "hasJobUnderWall False" not in text:
                _unmeasured(t, "ProofShovelUnderWall answer lacks hasJobBeforeWall True / hasJobUnderWall False: %s" % text[:200])
    _independent(t)

    # ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES: ProofMixedPatch stages a mixed grid on this map and reads the real candidate method and spawner.
    with _comp(t, "allowlist_mixed_patch_keeps_grass", beyond_toggle=True):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Pyrelands.RM_WildPlantAllowlistProof", method="ProofMixedPatch")
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        _note(t, "ProofMixedPatch", text or r)
        if _live(t):
            if not text.startswith("MIXEDPATCH"):
                _unmeasured(t, "ProofMixedPatch gave no answer (is the build with the probe deployed, on a Pyrelands map?): %r" % text[:200])
            nums = dict(re.findall(r"(\w+) (\d+)", text))
            if int(nums.get("cells", 0)) < 10 or not int(nums.get("rawForeign", 0)):
                _unmeasured(t, "the probe cannot see: too few open cells or no foreign candidates: %s" % text)
            if int(nums.get("rawGrass", 0)):
                _unmeasured(t, "vanilla already offered our grass on a foreign cell, so nothing here tests the supply: %s" % text)
            for key in ("afterEmpty", "afterForeign", "nativeSupplied", "caveGrass", "grownForeign"):
                if int(nums.get(key, -1)) != 0:
                    _fail("mixed patch: %s is not 0: %s" % (key, text))
            if int(nums.get("saturated", 0)) >= int(nums.get("cells", 0)):
                _unmeasured(t, "every sampled cell read saturated, so the spawner could not have grown anything: %s" % text)
            if not int(nums.get("grown", 0)):
                _fail("CONFIRMED: no native grass grew on the mixed cells: %s" % text)
    _independent(t)

    for name, why in (
        ("big_burn_tick_cost",
         "FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: CALIBRATING evidence, never a gate. Burn a 250x250 standing grass burn with 20+ "
         "RM_Ashwallow burrowed, and read ticks per second with src/RimMandrake/Pyrelands/tick_rate_probe.py against the same "
         "map unburned; record both. The two code costs it names were fixed offline 2026-11-02 (fire-tick postfix closure-free; "
         "burrow emergence scan once per BurrowEmergeCheckIntervalTicks, disc-bounded): src/RimMandrake/Utils/selftest_pyrelands_burn_cost.py"),
        ("rite_harvest_route_avoids_fire",
         "RITE_HARVEST_FIX_PICKS_PAST_FULL (3-3, PLAUSIBLE): the target-cell check refuses a burning pod but the route uses "
         "TraverseParms.For(pawn) at Deadly danger; send a fire rite (PyrelandsFireRiteHook) across a lit 3-cell line with "
         "pods behind it and sample harvester positions every 60 ticks: any harvester ON a Fire cell confirms it"),
        ("ash_field_activates_after_init",
         "ASH_FIELD_FIX_FORGETS_THE_WATER (9, PLAUSIBLE): `active` latches at FinalizeInit (biome or any ash-field terrain) or "
         "on a burn stamp only. On a NON-Pyrelands quicktest map with no ash, lay RM_FE_Ash_Deep beside water, wait 2000 "
         "ticks, read MapComponent_PyrelandsAshField.ProbeCell: active=False and watered=False confirm it"),
    ):
        _unproven(t, name, why + " (" + GPT_TRIAGE + ")")


@suite.chain("sand_shovel")
def sand_shovel(t):
    """PYRELANDS_SAND_TERRAIN_YIELD_1 (RM_TerrainDig.cs). The choice: a 'Shovel sand' DIG ORDER (Orders tab, Mining
    work), not a terrain clear-yield -- vanilla has no clear action on natural terrain. RM_FE_Ground_Sand carries
    RM_TerrainDigYieldExtension: 5 glass sand per cell, the cell becomes RM_FE_Ground_Gravel (a finite deposit).
    ProofShovel lays one sand cell on the current map and completes the dig. Not proven here: a miner choosing the
    order (WorkGiver) -- first poke: designate sand on a Pyrelands map with a colonist assigned to Mining.
    The def half (the dig-yield extension, the Orders-tab patch) is offline, in selftest_pyrelands_defs_offline.py: read
    on disk inside this live chain it passed on an empty game (RIMMANDRAKE_UNMEASURE_SAND_SHOVEL_ROW_PASSING_ON_EMPTY_MAP)."""
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


# --------------------------------------------------------------------------- Stage 3 scene entries (Pyrelands 0.1.0)
# Built offline 2026-11-14 by the Stage 3 reconcile (RIMMANDRAKE_ADVANCE_PYRELANDS_OFFLINE_BESIDE_THE_PILOT) from
# design/concepts/Pyrelands/scenes.json; UNRUN until Stage 6. Each chain's docstring names its scene, its control and
# what it does NOT automate.

PAD_VENOM = (30, 225)      # flamefang_venom
PAD_RITE = (30, 30)        # rite_hook_alone
PAD_SPRAY = (225, 30)      # firefoam_sprayer
VENOM = "RM_FlamefangVenom"
RITE_HOOK = "RimMandrake.Pyrelands.PyrelandsFireRiteHook"
BURN_LINE = "RimMandrake.Pyrelands.MapComponent_BurnLine"
VENOM_HOURS = 6
PLAIN_BITER = "Fox_Fennec"   # control: a vanilla predator of like size whose bite carries no venom


def _spawn_colonist(t, x, z):
    r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(Colonist) returned no pawn: %r" % r)
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def hediff_severity(row, hediff):
    """The highest severity of `hediff` in a list_pawns(includeHealth) row, None if absent or unreadable. Pure."""
    best = None
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict) and hediff in (h.get("def"), h.get("defName"), h.get("hediff")):
            s = h.get("severity")
            if isinstance(s, (int, float)) and (best is None or s > best):
                best = float(s)
    return best


def venom_never_read(series):
    """Pure. True when no hourly reading holds venom at all: the rises row then has no patient to read, and is
    UNMEASURED, never a FAIL against the mod. HARNESS (Pyrelands visit 6, 2026-11-22, ArchSmall): the flamefang never bit
    (the bite row UNMEASURED), and venom_rises_untreated read [None] * 7 and failed 'fewer than 3 readable severities'.
    A bite with no venom is the bite row's own FAIL."""
    return not [s for s in series or () if s is not None]


def venom_rises(series, min_rise=0.02):
    """Hourly venom severities -> (ok, why). Rising = the last reading clearly above the first and no reading
    falls more than noise. Untreated venom climbs +0.35/day (RM_FlamefangVenom), ~0.087 over six hours. Pure."""
    vals = [s for s in series if s is not None]
    if len(vals) < 3:
        return False, "fewer than 3 readable severities: %r" % (series,)
    if vals[-1] - vals[0] < min_rise:
        return False, "severity %.3f -> %.3f over %d readings: not rising" % (vals[0], vals[-1], len(vals))
    if any(b < a - 0.005 for a, b in zip(vals, vals[1:])):
        return False, "severity fell between hourly readings: %r" % (vals,)
    return True, "%.3f -> %.3f" % (vals[0], vals[-1])


# The bite rows HURT their own test colonist on purpose: the vitals latch's default kinds stop on that very bite ("hurt",
# and "downed" from the bleeding over six hours), which read the row UNMEASURED before it could ask (visit 1, 2026-11-15).
# Every other kind still stops the advance (death included). Used by the flamefang_venom chain and the firefoam harvest
# window (_harvest_through_fire), whose rows measure a burn.
BITE_STOP_ON = "death,colonist_hostile,hostile_arrival,threat_structure,modal_stuck,colony_loss,starving,mental," \
               "clock_discontinuity,specimen_lost,coverage,cancel"


# The venom wait-out's ten days: a venom death is what that row measures (its subject's) or expects (the earlier rows'
# untended patients, visit 3: one died 660 ticks into day 1 and stopped the advance), so death leaves the list too.
WAIT_OUT_STOP_ON = BITE_STOP_ON.replace("death,", "")


def _bite_wait(t, n, stop_on=None):
    """_wait for the bite rows: governed safe_advance chunks with BITE_STOP_ON (or `stop_on`), then the site re-asserted."""
    if not _live(t) or t.upstream_failed:
        return _wait(t, n)
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    if not clockgate.has_safe_advance(t.session):
        return _wait(t, n)
    # HARNESS (visit 6, 2026-11-22, ArchSmall, 55.8 C): this path never ran the heat guard that _wait runs, and three ten-day
    # wait-outs lost a site colonist by day 3-4; exposure is now carried and guarded as in _wait
    import testenv_guards  # noqa: E402 - on sys.path via the modcheck package
    guarded = _heat_guarded(t)
    for part, guard in (testenv_guards.heat_steps(n, _GEN.get("heat_ticks", 0)) if guarded else [(n, False)]):
        left = part
        while left > 0:
            step = min(left, clockgate.SAFE_CHUNK_MAX)
            clockgate.advance_chunk(t.session, step, stop_on=stop_on or BITE_STOP_ON)
            left -= step
        if guarded:
            _GEN["heat_ticks"] = _GEN.get("heat_ticks", 0) + part
            if guard and _heat_guarded(t):
                _heat_guard(t, "every %d ticks" % testenv_guards.HEAT_CHUNK_TICKS)
    _on_site(t)


# ---- the venom chain's feeding (RIMMANDRAKE_FEED_PYRE_VENOM_FIXTURES_HUNGER_STOPS_WAITOUT). Every venom patient is drafted
# by _bite_until and stays drafted, and a drafted pawn never eats. Pyrelands visit 4 (2026-11-22, game a): the wait-out's
# own subject reached Food category Starving inside its second day and the governor stopped the row (UNMEASURED), though
# it was topped up each day: a day (60000 ticks) is longer than a full human lasts without eating. Vanilla Need_Food (read
# in RimSage): the fall is BaseHungerRate 2.6666667e-05 x hungerRateFactor x baseHungerRate per tick, times
# HungerMultiplier 1 while Fed, 0.5 while Hungry (below FoodLevelPercentageWantEat 0.3 x 0.8 = 0.24) and 0.25 while
# UrgentlyHungry (below 0.3 x 0.4 = 0.12); Starving is level 0. Times a pawn factor: traits, hediffs, Biotech metabolism
# (GeneTuning: x2.25 at -5) and MaxNutrition. A human spawns at 0.8 (Need_Food.SetInitialLevel).
FOOD_FALL_PER_TICK = 2.6666667e-05
FOOD_HUNGRY, FOOD_URGENT = 0.24, 0.12


def ticks_to_starving(level, factor=1.0):
    """Pure. Ticks for a human that does not eat to fall from Food `level` to Starving (0), its hunger rate x `factor`.
    ticks_to_starving(1.0) = 55500: below one 60000-tick day."""
    r = FOOD_FALL_PER_TICK * factor
    lv, ticks = max(0.0, float(level)), 0.0
    for floor, mult in ((FOOD_HUNGRY, 1.0), (FOOD_URGENT, 0.5), (0.0, 0.25)):
        if lv > floor:
            ticks += (lv - floor) / (r * mult)
            lv = floor
    return ticks


# Each venom-chain wait feeds every player pawn to 1.0 at least once per FEED_EVERY ticks. 15000 (6 h) holds for a pawn
# factor up to ticks_to_starving(1.0) / 15000 = 3.7, and from the spawn level 0.8 up to 3.2; metabolism -5 alone is 2.25.
# The cost: one list_pawns and two pawn_need calls a pawn per feed, 40 feeds in the ten-day wait-out.
FEED_EVERY = 15000
FEED_TO = 1.0


def _feed_all(t):
    """Every living player pawn whose Food reads below FEED_TO is set to FEED_TO. -> the ids fed (offline: [])."""
    v = _vitals(t, force=True) if _live(t) and hasattr(t.session, "call") else None
    fed = []
    for pid, row in sorted((v or {}).items()):
        if not row["dead"] and row["food"] is not None and row["food"] < FEED_TO:
            t.session.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=FEED_TO)
            row["food"] = FEED_TO
            fed.append(pid)
    return fed


def _venom_wait(t, n, stop_on=None):
    """_bite_wait for the venom chain, with every player pawn fed at least once per FEED_EVERY ticks of the clock (the
    count carries across calls in _GEN["venom_unfed"], so a 90-tick poll costs no extra call). Feeding reads no row of
    this chain: each reads the venom hediff, never a need."""
    left = n
    while left > 0:
        if _GEN.get("venom_unfed", FEED_EVERY) >= FEED_EVERY:
            _feed_all(t)
            _GEN["venom_unfed"] = 0
        step = min(left, FEED_EVERY - _GEN["venom_unfed"])
        _bite_wait(t, step, stop_on=stop_on)
        _GEN["venom_unfed"] += step
        left -= step


def _beside(row, x, z):
    """Pure. The cell beside the pawn's live position in its list_pawns row; (x + 1, z) when the row has none."""
    px, pz = (row or {}).get("x"), (row or {}).get("z")
    if isinstance(px, int) and isinstance(pz, int) and px >= 0 and pz >= 0:
        return px + 1, pz
    return x + 1, z


# The latch's poll: below RM_Flamefang's melee cooldown (venom-fangs and head both 1.65 s = 99 ticks,
# RM_PyrelandsPortedFauna.xml), so the window in which the first venom bite lands holds no second attack, and the biter
# is gone before the clock moves again: ONE bite per patient. At 250 (visit 2) two or three bites stacked 0.2 venom each
# (RM_FlamefangVenomBite severityPerDamageDealt 0.02 x power 10) unequally on the two patients of one comparison.
BITE_POLL_TICKS = 90


def _hediff_defs(row):
    return [h.get("def") for h in (((row or {}).get("health") or {}).get("hediffs") or []) if isinstance(h, dict)]


def _new_wounds(before, row, keep):
    """Hediff defs in `row` beyond the multiset `before`, `keep` excluded -> [def, ...] (one entry per extra copy)."""
    left = list(before)
    out = []
    for d in _hediff_defs(row):
        if d in left:
            left.remove(d)
        elif d != keep:
            out.append(d)
    return out


def _bite_until(t, victim, biter_kind, x, z, hediff=None, max_ticks=6000, clear_wounds=False):
    """Spawn `biter_kind` beside `victim`, manhunter, and run ticks until the victim carries `hediff` (or any injury
    when hediff is None). -> the victim row read at the bite (before any wound is cleared), or None.
    - The victim is DRAFTED with fire-at-will OFF: undrafted, a fresh colonist FleeAndCowers to the map edge and is never
      bitten (visit 1, 2026-11-15); drafted with a gun and fire-at-will on, it shoots the biter dead first.
    - A drafted pawn still melees an adjacent hostile (JobDriver_Wait.CheckForAutoAttack: fire-at-will gates only the
      ranged branch), so a biter that dies before the bite is replaced at once, inside the same max_ticks.
    - The biter is removed by jawa/kill_hostiles (Pawn.Kill, certain) the moment the bite reads, and its absence is read
      back. The old `jawa/damage Cut 500` hit one random part, left the flamefang alive and manhunting when that part was
      not vital, and it kept attacking: visit 2's wait-out colonist died of BloodLoss (2026-11-21).
    - clear_wounds: after the bite, every hediff the bite added except `hediff` is removed (the bite wound, its bleeding),
      so a long untended venom read is not a blood-loss read, and no earlier patient bleeds out on the map during the
      ten-day wait-out (the governor stops the clock on any colonist's death). The venom is left exactly as the bite
      gave it; the returned row is read before the clearing, so a row that asks "was there a wound" still sees it.
      Offline: selftest_pyrelands_venom_staging.py."""
    if not _live(t):   # the declaration probe: the same tools, no clock
        t.bridge_call("jawa/set_draft", pawnId=victim, drafted=True, fireAtWill=False)
        bid = _spawn_wild(t, biter_kind, x + 1, z)
        t.bridge_call("jawa/pawn_mental", pawn=bid, action="start", state="ManhunterPermanent")
        t.bridge_call("jawa/kill_hostiles", pawnDef=biter_kind, destroyCorpses=True)
        return None
    _ok(t.bridge_call("jawa/set_draft", pawnId=victim, drafted=True, fireAtWill=False), "set_draft(%s)" % victim)
    row = _pawn_row(t, victim, health=True)
    before = _hediff_defs(row)
    biters, bid, landed, ran = [], None, False, 0
    while ran < max_ticks:
        if bid is None:
            # beside the victim where it STANDS (visit 4: an undrafted patient had fled from the last row's biter, and its
            # own biter, spawned on its planned cell, went for the nearer drafted patient and bit it again and again)
            bx, bz = _beside(row, x, z)
            bid = _spawn_wild(t, biter_kind, bx, bz)
            # HARNESS (visit 6, 2026-11-22, ArchSmall): undeclared, the wait-out's own biter stopped the advance as a
            # 'hostile_arrival' 60 ticks in; the biter is this test's own pawn (selftest_pyrelands_venom_staging.py)
            if bid and hasattr(t, "_declare_fixture"):
                t._declare_fixture(bid, biter_kind)
            biters.append(bid)
            m = t.bridge_call("jawa/pawn_mental", pawn=bid, action="start", state="ManhunterPermanent")
            if not (m or {}).get("success"):
                _unmeasured(t, "pawn_mental refused ManhunterPermanent on the %s %s: %r" % (biter_kind, bid, m))
        _venom_wait(t, BITE_POLL_TICKS)
        ran += BITE_POLL_TICKS
        rows = dict((p.get("id"), p) for p in (_ok(t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True),
                                                    "list_pawns").get("pawns") or []))
        row = rows.get(victim)
        hs = ((row or {}).get("health") or {}).get("hediffs") or []
        if (hediff and _has_hediff(row, hediff)) or (not hediff and hs):
            landed = True
            break
        b = rows.get(bid)
        if b is None or b.get("dead"):
            bid = None          # the victim killed it before a bite landed: a fresh biter, same clock
    k = t.bridge_call("jawa/kill_hostiles", pawnDef=biter_kind, destroyCorpses=True)
    left = [p.get("id") for p in (_ok(t.bridge_call("jawa/list_pawns", limit=500), "list_pawns").get("pawns") or [])
            if p.get("id") in biters and not p.get("dead")]
    _note(t, "biters of %s" % victim, {"spawned": biters, "landed": landed, "ticks": ran, "killed": (k or {}).get("killed"),
                                       "left": left})
    if left:
        _unmeasured(t, "the %s biter(s) %r survived jawa/kill_hostiles: %r" % (biter_kind, left, k))
    if clear_wounds and landed:
        for d in _new_wounds(before, row, hediff):
            t.bridge_call("jawa/pawn_health", pawn=victim, action="remove", hediff=d)
        after = _pawn_row(t, victim, health=True)
        rest = _new_wounds(before, after, hediff)
        if rest:
            _unmeasured(t, "the bite's wounds %r could not be cleared from %s" % (rest, victim))
        if hediff and not _has_hediff(after, hediff):
            _unmeasured(t, "clearing the bite's wounds took %s off %s too" % (hediff, victim))
    return row


@suite.chain("flamefang_venom")
def flamefang_venom(t):
    """Scene sc_flamefang_venom (bar flamefang_bite_carries_venom). A clean colonist, a manhunting RM_Flamefang beside
    it: once a bite connects RM_FlamefangVenom is present and its severity rises hour by hour for six hours, untreated.
    Control: a fresh colonist bitten by a vanilla predator of like size (Fox_Fennec) carries a wound and no venom.
    The tended half (severity falls when tended) is decided offline by selftest_pyrelands_defs_offline.py."""
    _pad(t, PAD_VENOM)
    x, z = PAD_VENOM
    _GEN["venom_unfed"] = FEED_EVERY    # the chain's first wait feeds every pawn (_venom_wait)
    with _comp(t, "flamefang_bite_injects_venom"):
        cid = _spawn_colonist(t, x, z)
        row = _pawn_row(t, cid, health=True)
        if _live(t) and (_has_hediff(row, VENOM) or _has_hediff(row, "ToxicBuildup")):
            _unmeasured(t, "the test colonist already carries venom or toxic buildup: %r" % row.get("health"))
        row = _bite_until(t, cid, "RM_Flamefang", x, z, hediff=VENOM, clear_wounds=True)
        if _live(t):
            _note(t, "colonist health after the flamefang", (row or {}).get("health"))
            if not any(h for h in (((row or {}).get("health") or {}).get("hediffs") or []) if "Heatstroke" not in str(h)):
                _unmeasured(t, "the RM_Flamefang never bit in 6000 ticks (no injury at all), so the venom could not be asked")
            if not _has_hediff(row, VENOM):
                _fail("no %s after 6000 ticks beside a manhunting RM_Flamefang" % VENOM)
    with _comp(t, "venom_rises_untreated"):
        series = []
        for _ in range(VENOM_HOURS + 1):
            series.append(hediff_severity(_pawn_row(t, cid, health=True), VENOM))
            _venom_wait(t, 2500)
        if _live(t):
            _note(t, "venom severity each hour", series)
            if venom_never_read(series):
                _unmeasured(t, "no hour read any %s on the bite row's colonist: that row's bite was not answered, so "
                               "whether venom rises untreated could not be asked" % VENOM)
            ok, why = venom_rises(series)
            if not ok:
                _fail(why)
    _independent(t)
    cid2 = None
    with _comp(t, "plain_bite_carries_no_venom"):
        cid2 = _spawn_colonist(t, x + 6, z)
        row = _bite_until(t, cid2, PLAIN_BITER, x + 6, z, clear_wounds=True)
        if _live(t):
            hs = ((row or {}).get("health") or {}).get("hediffs") or []
            _note(t, "control colonist health", hs)
            if not hs:
                _unmeasured(t, "the %s never bit in 6000 ticks: the control saw no bite" % PLAIN_BITER)
            if _has_hediff(row, VENOM):
                _fail("a %s bite carried %s: the venom is not the flamefang's own" % (PLAIN_BITER, VENOM))
    # SITE (visit 4, 2026-11-21, game a): the control's two fennec scratches (6.17 each, after the fauna normalization)
    # bled on untended, and it died of blood loss inside the next row, which then read RESTART and stopped the chain. Its
    # reading is taken above, so it is healed here and is no bystander to bleed out in the rows after it.
    # And it stays drafted after _bite_until (no sleep, no meals of its own): in visit 4's rerun it was downed inside the
    # wait-out's days and voided that row too. Undrafted here; the wait-out also counts it among the chain's earlier
    # fixtures, which are not its subjects (_GEN["venom_fixtures"]).
    if _live(t) and cid2:
        t.bridge_call("jawa/pawn_health", pawn=cid2, action="healAll", confirmDestructive=True)
        t.bridge_call("jawa/set_draft", pawnId=cid2, drafted=False)
        _GEN.setdefault("venom_fixtures", []).append(cid2)
    _ten_flamefang_venom(t)


def _log_mark(t):
    """jawa/drain_log does NOT drain: it returns the newest `limit` lines of the whole Verse.Log buffer every call (visit 1,
    2026-11-15: a 'drain' before a beat and a read after it returned the game-load banner, read as a rite-hook line). And the
    buffer is capped at 1000 lines, so on the full list its size stops growing and a count cannot window it (the walk read
    mark 1000, total 1000: blind). So the mark is a sentinel warning line; _log_since(t, mark) returns the lines after it.
    None offline."""
    if not _live(t):
        return None
    token = "pyre log mark %d" % int(time.time() * 1000)
    _ok(t.bridge_call("jawa/static_call", type="Verse.Log", method="Warning", args=token), "Log.Warning(mark)")
    return token


def _log_since(t, mark, limit=1000):
    """Lines (dicts) logged after the _log_mark sentinel. UNMEASURED when the sentinel is not among the newest `limit`
    lines: logging stopped (Verse.Log's 10,000-message cap) or the window overflowed the buffer."""
    r = t.bridge_call("jawa/drain_log", limit=limit) or {}
    if not _live(t):
        return []
    msgs = r.get("messages") or []
    at = [i for i, m in enumerate(msgs) if mark and mark in str(m.get("text", ""))]
    if not at:
        _unmeasured(t, "log window unknown: the mark %r is not in the newest %d lines (buffer %r): logging stopped or the "
                       "window overflowed" % (mark, len(msgs), r.get("totalInBuffer")))
    return msgs[at[-1] + 1:]


def rite_offers(before, after):
    """ProbeHook lines before and after one forced fire-clock beat -> offers counted. Pure."""
    a, b = parse_kv(before), parse_kv(after)
    try:
        return int(b.get("offers", "-1")) - int(a.get("offers", "-1"))
    except ValueError:
        return None


@suite.chain("rite_hook_alone")
@_teardown(fire=True)
def rite_hook_alone(t):
    """Scene sc_rite_hook_alone (bar fire_rite_hook_silent_alone). On a list without mandrake.rut.pyrelandsmechanics the
    rite hook is null; a forced fire-clock beat (MapComponent_BurnLine.ForceFrontDue) runs and the log holds nothing
    from the rite hook. Control: a test listener on PyrelandsFireRiteHook counts one offer per forced beat, so the
    hook is offered and its silence is not a front that never fires."""
    _pad(t, PAD_RITE)
    with _comp(t, "rite_hook_silent_alone", toggle="fireClockEnabled"):
        hook = t.bridge_call("jawa/static_call", type=RITE_HOOK, method="ProbeHook")
        if _live(t):
            h = parse_kv(str((hook or {}).get("result", "")))
            _note(t, "rite hook before the beat", h)
            if h.get("hook") != "null":
                _unmeasured(t, "the rite hook is filled (%s): PyrelandsMechanics is on this list, so the scene's start "
                               "(loaded without it) does not hold" % h.get("hook"))
        mark = _log_mark(t)
        forced = t.bridge_call("jawa/static_call", type=BURN_LINE, method="ForceFrontDue")
        _wait(t, 4 * BURN_WATCH_TICKS)
        msgs = [m.get("text", "") for m in _log_since(t, mark)]
        if _live(t):
            if str((forced or {}).get("result")) != "1":
                _unmeasured(t, "ForceFrontDue found no burn-line component: %r" % forced)
            rite = [m[:200] for m in msgs if re.search(r"\brites?\b|FireRite|RiteHook", m, re.I)]
            _note(t, "log lines over the beat", {"lines": len(msgs), "rite": rite})
            if rite:
                _fail("the log holds rite-hook lines on a list without the Tribes: %r" % rite[:3])
    _independent(t)
    with _comp(t, "rite_hook_offered_each_beat", toggle="fireClockEnabled"):
        att = t.bridge_call("jawa/static_call", type=RITE_HOOK, method="AttachTestListener")
        try:
            before = str((att or {}).get("result", ""))
            if _live(t) and "refused" in before:
                _unmeasured(t, "the listener was refused: %s" % before)
            for _ in range(2):
                t.bridge_call("jawa/static_call", type=BURN_LINE, method="ForceFrontDue")
                _wait(t, 4 * BURN_WATCH_TICKS)
            after = str((t.bridge_call("jawa/static_call", type=RITE_HOOK, method="ProbeHook") or {}).get("result", ""))
        finally:
            if t.session is not None:   # the offline declaration probe has no session
                _session_call(t, "jawa/static_call", type=RITE_HOOK, method="DetachTestListener")
        if _live(t):
            n = rite_offers(before, after)
            _note(t, "offers over two forced beats", {"before": before, "after": after, "offers": n})
            if n != 2:
                _fail("the listener counted %r offers over two forced beats, want 2" % n)


SPRAYER = "RM_FE_FirefoamSprayer"
FRUIT_PLANT = "RM_FE_Plant_ScorchFruit"


def burn_injuries(row):
    """Burn hediffs in a list_pawns(includeHealth) row. Pure."""
    return [h for h in (((row or {}).get("health") or {}).get("hediffs") or [])
            if isinstance(h, dict) and "Burn" in str(h.get("def") or h.get("defName") or h.get("hediff") or "")]


FRUIT_RING = 3   # the fire ring's thickness round the 3x3 fruit in the 9x9 burn: nothing clear is left beside the fruit
# The harvester's Plants level, the same in both rows. PlantWorkSpeed is 0.08 + 0.115 per Plants level, floor 0.1
# (StatDef PlantWorkSpeed), so one pod's 150 harvestWork (ScorchFruit.xml) takes 1500 ticks at level 0 and about 120 at
# level 10. SITE (visit 5, 2026-11-22, all five firefoam runs): the spawned colonists took one pod per 750 to 1500 ticks,
# fire or no fire (run_firefoam_sprayer.log: the control took a pod at tick 1250 with 52 ring fires, the sprayer colonist
# at 2000 with 9). The grass ring's fires fall at 1250 to 1500 ticks (the same five logs), so an unpinned slow harvester
# picks from cold ground and reads as "waited the fire out". At level 10 three pods take about 370 ticks of work after
# the walk in, inside the ring's measured life. The number is a fact of the stat, not a bar.
FRUIT_HARVESTER_PLANTS = 10


def fruit_cells(x, z):
    """The 3x3 scorch-fruit square of the 9x9 burn at (x, z) -> set of (x, z). Pure."""
    return set((x + 3 + i, z + 3 + j) for i in range(3) for j in range(3))


def ring_cells(x, z, k=FRUIT_RING):
    """The ring's cells: its four edges, as _stage_burning_fruit lights them -> set of (x, z). Pure."""
    out = set()
    for ex, ez, w, h in ring_edges(x, z, k):
        out.update((ex + i, ez + j) for i in range(w) for j in range(h))
    return out


def ring_edges(x, z, k=FRUIT_RING):
    """The ring's four edge rects (x, z, w, h): bottom, top, west, east. Pure."""
    return ((x, z, 9, k), (x, z + 9 - k, 9, k), (x, z + k, k, 9 - 2 * k), (x + 9 - k, z + k, k, 9 - 2 * k))


def beside_fruit(x, z):
    """The 16 cells one step (8-way) from the fruit square: the only cells a harvester can stand on to reach the fruit
    from outside, since every path from outside into the fruit passes through one of them. Pure."""
    f = fruit_cells(x, z)
    box = set((x + 2 + i, z + 2 + j) for i in range(5) for j in range(5))
    return box - f


def cold_beside(fires, x, z):
    """Cells beside the fruit that hold no free-standing fire -> sorted list. fires: (x, z) cells (fire_cells). Pure.
    The pathfinder prices a burning cell +1000 (PathGrid.CalculatedCostAt), so a harvester always picks a cold one."""
    lit = set(tuple(c) for c in fires or ())
    return sorted(beside_fruit(x, z) - lit)


def west_gap_cells(x, z, k=FRUIT_RING):
    """The cells beside the fruit that the planted west gap leaves cold: those inside the west edge rect. Pure."""
    ex, ez, w, h = ring_edges(x, z, k)[2]
    return set(c for c in beside_fruit(x, z) if ex <= c[0] < ex + w and ez <= c[1] < ez + h)


def ring_staging_verdict(cold, x, z, west_gap=False, k=FRUIT_RING):
    """-> (ok, why) for the staged burn, from the cold cells beside the fruit after the relight. The scene's start
    (scenes.json sc_firefoam_sprayer) asserts fire on every path to the fruit; a cell beside it with no fire breaks that.
    Planted (west_gap): the west edge's cells beside the fruit must be cold and every other one lit. Pure."""
    cold = set(tuple(c) for c in cold or ())
    west = west_gap_cells(x, z, k)
    want = west if west_gap else set()
    if cold == want:
        return True, ("the west gap is open as planted: %s" % sorted(want)) if west_gap else \
            "all %d cells beside the fruit burn" % len(beside_fruit(x, z))
    if west_gap and not want <= cold:
        return False, "the planted west gap did not take: %s beside the fruit still burn" % sorted(want - cold)
    return False, "%d cell(s) beside the fruit hold no fire after the relight: %s" % (len(cold - want),
                                                                                     sorted(cold - want))


def _fire_cells_in(t, rect):
    """Free-standing Fire cells in `rect` -> [(x, z)]; UNMEASURED when a row has no cell (a blind count is not 0)."""
    cells, unplaced = fire_cells(_things(t, "Fire", rect, limit=500))
    if unplaced:
        _unmeasured(t, "list_things gave %d Fire row(s) with no cell in %s: %r" % (len(unplaced), rect, unplaced[:2]))
    return cells


def _stage_burning_fruit(t, x, z, west_gap=False):
    """A 9x9 grass burn, ripe scorch-fruit in its 3x3 centre, a fire ring on every path in.
    -> (fruit ids, fire count in the 9x9, staging record {cold, relit, verdict, why}).
    west_gap: the planted state of the control (PLANT_RING_GAP_ENV): the west edge, the colonist's side, has its fuel
    cut and is never lit, so the fruit is reachable without crossing fire and no fire can spread into that edge.
    The caller reads record["verdict"]: False means the scene failed its own start, and the row is UNMEASURED."""
    rect = "%d,%d,9,9" % (x, z)
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    # Filth that refuses fire (firefoam: ChanceToStartFireIn returns 0 on filth whose allowsFire is false) or an earlier
    # run's leavings would leave cold cells. SITE (visit 5, 2026-11-22): the sprayer row's foam lay on the control's west
    # ring. Both rows start on clean ground.
    t.bridge_call("jawa/destroy_batch", rects="%d,%d,11,11" % (x - 1, z - 1), categories="Filth")
    left_foam = _count(t, FOAM_FILTH, rect)
    if _live(t) and left_foam:
        _unmeasured(t, "%d %s cells still on the burn after the filth clear" % (left_foam, FOAM_FILTH))
    _plants(t, "RM_FE_Plant_EmberGrass", (x, z, 9, 9))
    _plants(t, FRUIT_PLANT, (x + 3, z + 3, 3, 3))
    k = FRUIT_RING
    west = ring_edges(x, z, k)[2]
    if west_gap:
        # planted: no fuel on the west edge, so a fire cannot spread in (visit 5 planted run: an unlit grass edge took
        # the fire 1250 ticks later and burned the colonist standing in it, so the planted control read PASS by chance)
        t.bridge_call("jawa/destroy_batch", rects=_rs(west), categories="Plant")
    # the ring: all four edges. SITE (visit 2, 2026-11-20): only the bottom strip (x, z, 9, 2) was lit, and the control
    # colonist walked in from the open side and took the fruit unburned.
    # SITE (visit 5, 2026-11-22, ArchBig; visits 3 and 4 the same): a 2-cell ring is crossed in about 25 ticks, and vanilla
    # Fire tries to ignite a pawn in its cell only at its 150-tick DoComplexCalcs, so a bare colonist crossed it unburned and
    # harvested from the clear interior beside it. The ring is FRUIT_RING cells thick, so the only cells beside the fruit
    # are burning ring cells: to harvest, the colonist must stand in fire through the harvest work.
    for edge in ring_edges(x, z, k):
        if west_gap and edge == west:
            continue
        _fire(t, edge)
    # SITE (visit 5, 2026-11-22): one map_fire per edge lit only 41 to 54 of the 72 ring cells, and every harvester stood
    # on an unlit cell beside the fruit. FireUtility.TryStartFireIn has no random roll: a refused cell has
    # ChanceToStartFireIn 0 (nothing flammable on it, or fire-refusing filth), so lighting it again changes nothing.
    # Each cold cell beside the fruit gets its fuel again and one more light; what still refuses is named, with the
    # planting reply that says why.
    rec = {"relit": [], "cold": []}
    if _live(t):
        gap_cells = west_gap_cells(x, z, k) if west_gap else set()
        for cx, cz in cold_beside(_fire_cells_in(t, rect), x, z):
            if (cx, cz) in gap_cells:
                continue
            cell = (cx, cz, 1, 1)
            pr = _plants(t, "RM_FE_Plant_EmberGrass", cell)
            fr = t.bridge_call("jawa/map_fire", action="start", rect=_rs(cell), fireSize=1.2)
            rec["relit"].append({"cell": [cx, cz], "planting": _GEN.get("last_plants", {}).get("reply"),
                                 "firesStarted": (fr or {}).get("firesStarted"), "plantReply": bool(pr)})
    _wait(t, 250)
    fruit = [p.get("id") for p in _things(t, FRUIT_PLANT, "%d,%d,3,3" % (x + 3, z + 3), limit=20)]
    if not _live(t):
        return fruit, 0, dict(rec, verdict=True, why="offline")
    fires = _fire_cells_in(t, rect)
    rec["cold"] = [list(c) for c in cold_beside(fires, x, z)]
    rec["verdict"], rec["why"] = ring_staging_verdict(rec["cold"], x, z, west_gap=west_gap)
    return fruit, len(fires), rec


PLANT_RING_GAP_ENV = "PYRE_PLANT_RING_GAP"   # planted state for the repaired control row: the ring open on one side
HARVEST_SAMPLE_TICKS = 250      # one sample per ring-fire read: a 2-cell grass ring burns out inside the 3000-tick window


def _harvest_sample(t, cid, fruit, x, z, ring, tick):
    """One timeline sample of the harvest window at `tick`: fires in the ring and beside the fruit, the fruit left and
    taken, the colonist's cell, job and burns, the yield stacks by the burn."""
    left = [p.get("id") for p in _things(t, FRUIT_PLANT, "%d,%d,3,3" % (x + 3, z + 3), limit=20)]
    row = _pawn_row(t, cid, health=True) or {}
    cx, cz = row.get("x"), row.get("z")
    # "taken" is only "gone from the 3x3". "atFruit" is the colonist beside the fruit or on it (x+2..x+6: with a 3-cell
    # ring the cells beside the fruit are the ring's inner cells, which is where a harvester stands). A harvest is a
    # fruit taken with the colonist at the fruit, or a yield stack appearing by the burn.
    at_fruit = isinstance(cx, int) and isinstance(cz, int) and x + 2 <= cx <= x + 6 and z + 2 <= cz <= z + 6
    fires = _fire_cells_in(t, ring)
    return {"tick": tick, "fires": len(fires), "besideFires": len(beside_fruit(x, z) & set(fires)),
            "fruitLeft": len(left), "taken": [f for f in fruit[:3] if f not in left], "cell": [cx, cz],
            "atFruit": at_fruit, "yield": _count(t, "RM_FE_ScorchFruitYield", "%d,%d,15,15" % (x - 3, z - 3)),
            "job": _job_of(t, cid), "burns": len(burn_injuries(row))}


def _harvest_through_fire(t, cid, fruit, ticks=3000, ring=None):
    """Order the harvest, then advance `ticks` in HARVEST_SAMPLE_TICKS steps; with `ring` ('x,z,w,h' of the burn) a
    sample at tick 0, before the order, then one per step (_harvest_sample) -> the timeline (list of dicts), [] offline.
    The tick-0 sample is the yield baseline: the sprayer row's own yield stacks lie in the same 15x15 for the control.
    HARNESS (Pyrelands visit 3, 2026-11-21): the control colonist took 3 fruit unburned after one flat 3000-tick wait, and
    nothing said whether the ring was still burning when it walked in."""
    x, z = (int(v) for v in ring.split(",")[:2]) if ring else (0, 0)
    out = [_harvest_sample(t, cid, fruit, x, z, ring, 0)] if ring and _live(t) else []
    for i, fid in enumerate(fruit[:3]):
        t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Harvest", targetAId=fid, queue=i > 0, waitTicks=0)
    if not ring:
        _wait(t, ticks)
        return []
    done = 0
    while done < ticks:
        step = min(HARVEST_SAMPLE_TICKS, ticks - done)
        # a burn is what this row measures (the sprayer row's "no burn injury", the control's "or comes back burned"),
        # so the advance does not stop on it: the bite rows' stop list (every other kind still stops it). Visit 3: the
        # default latch stopped both sampled runs at tick 240 on the sprayer colonist's hand burn, reading UNMEASURED.
        _bite_wait(t, step)
        done += step
        if _live(t):
            out.append(_harvest_sample(t, cid, fruit, x, z, ring, done))
    return out


def _pin_harvester(t, cid):
    """Set the harvester's Plants to FRUIT_HARVESTER_PLANTS, so both rows harvest at one known speed. -> the
    set_pawn_skill reply (its `before` is the colonist's own level, kept as evidence); UNMEASURED when it cannot."""
    r = t.bridge_call("jawa/set_pawn_skill", pawn=cid, skill="Plants", level=FRUIT_HARVESTER_PLANTS)
    if _live(t) and not ((r or {}).get("success") and (r or {}).get("readBackMatches", True)):
        _unmeasured(t, "the harvester's Plants could not be set to %d, so its harvest speed is unknown: %r"
                    % (FRUIT_HARVESTER_PLANTS, r))
    return r


FOAM_FILTH = "Filth_FireFoam"   # what RM_FE_Bullet_FirefoamSplash leaves (vanilla firefoam filth)


def harvested_while_burning(timeline):
    """The first sample at which the colonist was at the fruit (beside it or on it), or a yield stack had appeared
    beside the burn, while the ring still held fire; or None. The control's test: reaching the fruit unburned through a
    burning ring means the fire did not stop it. Pure."""
    y0 = (timeline[0].get("yield") or 0) if timeline else 0
    for smp in timeline or []:
        at = smp.get("atFruit", smp.get("inside"))   # "inside" is the field's name in visit-5 and older timelines
        if (smp.get("fires") or 0) > 0 and (at or (smp.get("yield") or 0) > y0):
            return smp
    return None


def taken_while_burning(timeline):
    """The first sample at which a fruit was harvested while the ring still held fire, or None. Harvested: a fruit gone
    from the 3x3 with the colonist at the fruit, or a yield stack more than at the first sample. The sprayer row's test:
    the bar is a harvest from inside a live burn, so a fruit taken from cold ground after the ring burned out is not it
    (visit 5, 2026-11-22: the sprayer colonist's first fruit went at tick 2000 with 0 fires left, and the row read PASS).
    Pure."""
    y_prev = (timeline[0].get("yield") or 0) if timeline else 0
    n_prev = 0
    for smp in timeline or []:
        at = smp.get("atFruit", smp.get("inside"))
        n, y = len(smp.get("taken") or ()), smp.get("yield") or 0
        # a harvest is judged at the sample where it is first seen: "taken" and "yield" only grow
        if (smp.get("fires") or 0) > 0 and ((n > n_prev and at) or y > y_prev):
            return smp
        n_prev, y_prev = max(n_prev, n), max(y_prev, y)
    return None


@suite.chain("firefoam_sprayer")
@_teardown(fire=True, weather=True)
def firefoam_sprayer(t):
    """Scene sc_firefoam_sprayer (bar firefoam_sprayer_reaches_the_fruit). Firefoam researched; a colonist holding the
    firefoam sprayer is ordered to harvest ripe scorch-fruit standing inside a live burn: the fruit is taken and the
    colonist comes back with no burn injury. Control: the same burn and fruit, a colonist without the sprayer refuses
    the path or comes back burned. NOT automated: whether the colonist foams on its own, unordered (the sprayer's aim
    is proven by firefoam_aim_live_proof.py; if the colonist will not foam unordered this row says so as a FAIL)."""
    x, z = PAD_SPRAY
    _pad(t, PAD_SPRAY)
    with _comp(t, "sprayer_reaches_the_fruit"):
        _open_ground(t, (x, z, 9, 9), margin=5, soil=(x, z, 9, 9))   # SITE (visit 6): the pad held a ruin
        t.bridge_call("jawa/research_finish_project", project="Firefoam")
        fruit, fires, staged = _stage_burning_fruit(t, x, z)
        if _live(t):
            _note(t, "sprayer burn staging", staged)
            if not fruit or not fires:
                _unmeasured(t, "staging failed: %d fruit, %d fire cells" % (len(fruit), fires or 0))
            if not staged.get("verdict"):
                _unmeasured(t, "staging failed: %s; relit %r" % (staged.get("why"), staged.get("relit")))
        cid = _spawn_colonist(t, x - 3, z + 4)
        _note(t, "sprayer harvester Plants", (_pin_harvester(t, cid) or {}).get("before"))
        spr = t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,1" % (SPRAYER, x - 3, z + 4))
        gun = [g.get("id") for g in _things(t, SPRAYER, "%d,%d,1,1" % (x - 3, z + 4), limit=5)]
        if gun:
            t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Equip", targetAId=gun[0], waitTicks=120)
        timeline = _harvest_through_fire(t, cid, fruit, ring="%d,%d,9,9" % (x, z))
        left = set(p.get("id") for p in _things(t, FRUIT_PLANT, "%d,%d,3,3" % (x + 3, z + 3), limit=20))
        row = _pawn_row(t, cid, health=True)
        foam = _count(t, FOAM_FILTH, "%d,%d,9,9" % (x, z))
        if _live(t):
            _note(t, "sprayer run timeline (every %d ticks)" % HARVEST_SAMPLE_TICKS, timeline)
            _note(t, "firefoam on the burn after the sprayer run (%s cells)" % FOAM_FILTH, foam)
            if not foam:
                _fail("the colonist carrying the sprayer laid no firefoam on the burn (%s 0 in the 9x9): it did not foam "
                      "a way through; jobs seen %r" % (FOAM_FILTH, sorted(set(str(s_.get("job")) for s_ in timeline))))
            _note(t, "sprayer run", {"spawned": spr, "gun": gun, "fruit": fruit, "left": sorted(left),
                                     "burns": burn_injuries(row)})
            if not gun:
                _unmeasured(t, "no %s spawned beside the colonist" % SPRAYER)
            if not [f for f in fruit if f not in left]:
                _fail("the colonist with the sprayer took none of the burning fruit")
            if burn_injuries(row):
                _fail("the colonist with the sprayer came back burned: %r" % burn_injuries(row))
            if not taken_while_burning(timeline):
                last = (timeline or [{}])[-1]
                _fail("the colonist with the sprayer took no fruit while the ring still burned (fires per sample %r): a "
                      "fruit taken from cold ground is not a harvest from inside a live burn"
                      % [(s_.get("tick"), s_.get("fires"), len(s_.get("taken") or ())) for s_ in timeline][:14]
                      if timeline else "no samples, last %r" % last)
        _extinguish(t)
    _independent(t)
    with _comp(t, "without_sprayer_fire_stops_or_burns"):
        gap = os.environ.get(PLANT_RING_GAP_ENV) == "1"
        if gap:
            _note(t, "PLANTED FAULT", "%s=1: the control's ring is open on the west, the colonist's side: that edge's fuel is cut and it is never lit"
                  % PLANT_RING_GAP_ENV)
        # the sprayer row's foam is cleared by the staging (both rows start on clean ground)
        _open_ground(t, (x, z, 9, 9), margin=5, soil=(x, z, 9, 9))
        fruit, fires, staged = _stage_burning_fruit(t, x, z, west_gap=gap)
        if _live(t):
            _note(t, "control burn staging", staged)
            if not staged.get("verdict"):
                _unmeasured(t, "staging failed: %s; relit %r" % (staged.get("why"), staged.get("relit")))
        cid = _spawn_colonist(t, x - 3, z + 4)
        _note(t, "control harvester Plants", (_pin_harvester(t, cid) or {}).get("before"))
        timeline = _harvest_through_fire(t, cid, fruit, ring="%d,%d,9,9" % (x, z))
        left = set(p.get("id") for p in _things(t, FRUIT_PLANT, "%d,%d,3,3" % (x + 3, z + 3), limit=20))
        row = _pawn_row(t, cid, health=True)
        if _live(t):
            took = [f for f in fruit if f not in left]
            _note(t, "control run timeline (every %d ticks)" % HARVEST_SAMPLE_TICKS, timeline)
            _note(t, "control run", {"fruit": fruit, "took": took, "fires": fires, "burns": burn_injuries(row)})
            if not fires:
                _unmeasured(t, "the control burn did not light")
            if not timeline:
                _unmeasured(t, "the harvest window was not sampled, so when the fruit was taken is unknown")
            # the fire stops the colonist when no fruit is taken while the ring still burns; a fruit taken from cold
            # ground after the ring burned out is not a path through fire
            hot = harvested_while_burning(timeline)
            if hot and not burn_injuries(row):
                _fail("without the sprayer the colonist reached the fruit unburned while %d fires still burned in the ring "
                      "(tick %d, cell %r, yield %r): the fruit was reachable without crossing fire, so the sprayer row "
                      "proves nothing" % (hot.get("fires"), hot.get("tick"), hot.get("cell"), hot.get("yield")))


WALK_DAYS = 7          # each half of the two-week walk
# a planted run of a later walk part (PYRE_PLANT_GATE_IGNORED) needs no two weeks: its verdict reads only that part.
# Never set on a real run: both week parts then read UNMEASURED, so a real sc_walk can never pass with it.
WALK_PARTS_ONLY_ENV = "PYRE_WALK_PARTS_ONLY"
WALK_SAVE = "pyre_walk"


WALK_CREATURES = ("RM_FurnaceBeast", "RM_Ullai")
# Probe fields a correct reload does not keep: `now` is the tick the probe ran, and the burn line's `burning`/`center`
# are a cache the next 60-tick watch rebuilds (0 and `invalid` at load; visit_1 findings §RIMMANDRAKE_FIX_WALK_DIGEST_
# COMPARES_A_TICK_STAMP, measured 2026-11-15).
WALK_UNSAVED_FIELDS = ("now", "burning", "center")


def strip_probe_fields(line, drop=WALK_UNSAVED_FIELDS):
    """A `k=v;k=v` probe line without the `drop` keys, order kept. Pure."""
    return ";".join(f for f in str(line or "").split(";") if f and f.split("=", 1)[0] not in drop)


def pawn_kind_counts(rows, kinds):
    """Living pawns per kindDef in `kinds` from list_pawns rows (0 when absent). Pure."""
    out = dict((k, 0) for k in kinds)
    for p in rows or []:
        k = p.get("kindDef")
        if k in out and not p.get("dead"):
            out[k] += 1
    return out


def walk_digest(t):
    """The walk's state digest: counts that a correct save/reload keeps. -> dict, {} offline. Creatures come from
    list_pawns: list_things defName=RM_Ullai counts 0 with six ullai on the map (measured 2026-11-15)."""
    d = {}
    for k in ("Fire", FRUIT_PLANT, "RM_FE_ScorchFruitYield"):
        d[k] = _count(t, k)
    r = t.bridge_call("jawa/list_pawns", limit=1000)
    if _live(t):
        _ok(r, "list_pawns")
        if r.get("truncated"):
            _fail("walk digest creature census truncated: %r" % r.get("message"))
        d.update(pawn_kind_counts(r.get("pawns"), WALK_CREATURES))
    r = t.bridge_call("jawa/static_call", type=ASH_FIELD, method="ProbeRegrowth")
    raw = str((r or {}).get("result", ""))
    d["regrowth"] = strip_probe_fields(raw)[:400]
    # the bins are whole days since each cell's burn stamp at the probe's `now`: read at another tick, a stamp near a day
    # boundary moves to the next bin with no state lost (visit 5, his full list: '2=234' and '3=274' before the reload,
    # '2=233' and '3=275' after, every other bin and column equal). `now` is kept beside the digest, never compared.
    d["_regrowthNow"] = dict(kv.split("=", 1) for kv in raw.split(";") if "=" in kv).get("now")
    r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="ProbeBurnHistory", args="0")
    d["burnHistory"] = strip_probe_fields((r or {}).get("result", ""))[:400]
    return d if _live(t) else {}


def regrowth_totals(line):
    """'d=cells/grassy/half;...' -> (cells, grassy, half) summed over every day bin, or None when no bin parses. Pure."""
    tot, seen = [0, 0, 0], False
    for part in str(line or "").split(";"):
        k, _, v = part.partition("=")
        nums = v.split("/")
        if k.strip().isdigit() and len(nums) == 3 and all(n.strip().isdigit() for n in nums):
            tot = [a + int(n) for a, n in zip(tot, nums)]
            seen = True
    return tuple(tot) if seen else None


def digests_match(a, b):
    """Two walk digests equal on every key both carry (keys starting '_' are context, never compared), and both non-empty.
    The regrowth day bins are compared bin by bin when both were read at the same tick; read at different ticks, their
    totals (cells, grassy, half grown) must be equal instead, since the bins shift with the clock alone. Pure."""
    keys = set(k for k in set(a) & set(b) if not str(k).startswith("_"))
    if not keys:
        return False
    for k in keys:
        if k == "regrowth" and a.get("_regrowthNow") != b.get("_regrowthNow"):
            ta, tb = regrowth_totals(a[k]), regrowth_totals(b[k])
            if ta is None or ta != tb:
                return False
        elif a[k] != b[k]:
            return False
    return True


# ---- the walk's shield (RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS). On his 315-mod list (visit 2, 2026-11-21) a hostile
# that ARRIVED from another mod ("arrived: Human VRESaurids_TownGuard_Saurid (humanlike)", quiet storyteller) stopped the
# two-week walk: 8 of 8 parts UNMEASURED. Two weeks on the full list meet such arrivals; none is Pyrelands's. Inside the walk a
# foreign arrival is vanished (no death, no corpse: helpers.kill_hostiles' route), read back and noted, and the advance
# resumes. Everything else still stops the walk: the biome's own cast, a hostile present at arm, a pawn that turned hostile,
# any harm to a colonist, a removal that cannot be read back. selftest_pyrelands_walk_shield.py holds this.
WALK_SHIELD = "walk: a foreign hostile arrived from the full list, vanished"


def walk_foreign_arrival(trig):
    """Pure. A vitals trigger the walk's shield may take: a hostile that ARRIVED (detail "arrived: <race> <kind> (<cls>)"),
    of no def of the biome's own cast, neither critical nor declared."""
    if not isinstance(trig, dict) or trig.get("kind") != "hostile_arrival" or trig.get("critical") or trig.get("declared"):
        return False
    d = str(trig.get("detail") or "")
    if not d.startswith("arrived: "):
        return False
    return not any(w in ANIMAL_MANIFEST for w in d[len("arrived: "):].split()[:2])


def _walk_vanish_arrivals(session, r):
    """clockgate repair: vanish every foreign arrival of the stop `r` by thingIDNumber, then read back that none is left.
    -> {"ok", "removed", "left", "ids"}; a pawn listing that fails is not ok (could not look: the stop stands)."""
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    want = set(n for n in (clockgate._thing_number(x.get("subjectId"))
                           for x in [r.get("stopBy") or {}] + list(r.get("triggers") or []) if walk_foreign_arrival(x))
               if n is not None)

    def alive():
        q = session.call("jawa/list_pawns", limit=2000) or {}
        if q.get("success") is False or "pawns" not in q:
            return None
        return dict((clockgate._thing_number(p.get("id")), p.get("id")) for p in q["pawns"]
                    if not p.get("dead") and clockgate._thing_number(p.get("id")) in want)
    if not want:
        return {"ok": False, "why": "no subject id on the arrival"}
    found = alive()
    if found is None:
        return {"ok": False, "why": "jawa/list_pawns failed before the removal"}
    for pid in found.values():
        session.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
    left = alive()
    if left is None:
        return {"ok": False, "why": "jawa/list_pawns failed after the removal", "removed": sorted(found.values())}
    return {"ok": not left, "removed": sorted(found.values()), "left": sorted(left.values()), "ids": sorted(want)}


WALK_WILDLIFE = "walk: harm to a pawn not the player's, or a colonist's panic flight, read back"
WALK_WILDLIFE_KINDS = ("hurt", "downed", "mental", "death", "starving")   # visit 5 walk 2: three starving fire-wasps rode with a downing
WALK_PANIC_STATES = ("PanicFlee", "PanicFleeFire")   # a colonist running from fire: no harm, the biome's ordinary day


def walk_wildlife_harm(trig):
    """Pure. A vitals trigger the walk may resume past once the repair has read it back: harm to a pawn or a mental state,
    neither critical nor declared. HARNESS (visit 5, 2026-11-22, ArchBig, his full list): one walk met a wild nuna downed
    by a predator, a fire-wasp bitten and downed, a visiting OutlanderCivil villager downed (bitten, dehydrated, starving),
    and colonists in PanicFlee/PanicFleeFire; each stopped two weeks of walk on its first day. None is harm to the player's
    colonists. The repair, not this predicate, decides."""
    return (isinstance(trig, dict) and trig.get("kind") in WALK_WILDLIFE_KINDS and not trig.get("critical")
            and not trig.get("declared") and trig.get("subjectId") is not None)


def walk_ordinary_ok(trig, pawn):
    """Pure. One matched trigger and its subject's list_pawns row (None when not listed): ok for a pawn that is not the
    player's (wildlife, the biome's cast, visitors), or a colonist's panic flight; never a colonist's harm, never a subject
    that cannot be read (a dead pawn is not listed, so a colonist's death, never 'info', stands)."""
    # a wild death riding along (visit 8: a flamefang burned to death beside a nuna's downing): the companion marks a death
    # 'info' only when the dead pawn is no colonist on a map and not critical (JawaBenchVitalsCore.DeathSeverity)
    if pawn is None and trig.get("kind") == "death" and trig.get("severity") == "info" and not trig.get("critical"):
        return True
    if pawn is None or not isinstance(pawn.get("isPlayer"), bool):   # a row that does not say whose pawn it is: refuse
        return False
    if trig.get("kind") == "mental" and any(("mental state %s" % m) == str(trig.get("detail") or "").strip()
                                            for m in WALK_PANIC_STATES):
        return True
    return not pawn.get("isPlayer") and (pawn.get("faction") or "") != "PlayerColony"


def _walk_wildlife_check(session, r):
    """clockgate repair: every matched trigger of the stop `r` must pass walk_ordinary_ok on its subject's list_pawns row;
    nothing is changed. -> {"ok", "taken", "refused"}; a failed listing is not ok, so the stop stands."""
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    trigs = [x for x in [r.get("stopBy") or {}] + list(r.get("triggers") or []) if walk_wildlife_harm(x)]
    if not trigs:
        return {"ok": False, "why": "no subject id on the harm"}
    q = session.call("jawa/list_pawns", limit=2000) or {}
    if q.get("success") is False or "pawns" not in q:
        return {"ok": False, "why": "jawa/list_pawns failed"}
    rows = dict((clockgate._thing_number(p.get("id")), p) for p in q["pawns"])
    taken, refused = [], []
    for x in trigs:
        p = rows.get(clockgate._thing_number(x.get("subjectId")))
        (taken if walk_ordinary_ok(x, p) else refused).append("%s %s: %s" % (x.get("kind"), x.get("subject"), x.get("detail")))
    return {"ok": not refused, "taken": taken, "refused": refused}


@contextlib.contextmanager
def _walk_shield(t):
    """Every advance inside resumes past a foreign arrival after its removal (clockgate.expected_disturbance with a repair);
    each removal is noted on the run's evidence when the walk ends."""
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    n0 = len(clockgate.BENIGN_STOPS)
    try:
        with clockgate.expected_disturbance(WALK_SHIELD, walk_foreign_arrival, repair=_walk_vanish_arrivals):
            with clockgate.expected_disturbance(WALK_WILDLIFE, walk_wildlife_harm, repair=_walk_wildlife_check):
                yield
    finally:
        got = [b for b in clockgate.BENIGN_STOPS[n0:] if b.get("why") == "expected: " + WALK_SHIELD]
        if got and t.session is not None:
            _note(t, "walk shield: foreign hostile arrivals vanished", got)
        wl = [b for b in clockgate.BENIGN_STOPS[n0:] if b.get("why") == "expected: " + WALK_WILDLIFE]
        if wl and t.session is not None:
            _note(t, "walk shield: harm to pawns not the player's, or colonist panic flight, resumed past", wl)


BURN_WILDLIFE = "burn line: harm to a wild animal or another faction's pawn, read back"


def burn_wildlife_harm(trig):
    """Pure. walk_wildlife_harm without any mental state: the burn line's days read the burned share of the ground, and a
    wild animal bitten, downed, starved or killed by another moves no ground. A manhunter or a colonist's state still stops."""
    return walk_wildlife_harm(trig) and trig.get("kind") != "mental"


@contextlib.contextmanager
def _wildlife_shield(t):
    """Visit 8 (2026-11-23): a barbslinger downed a fire wasp on day 4 of burn_line's eight days and safe_advance's stop
    spoiled burn_line_burned_share. A stop whose every subject list_pawns reads as not the player's resumes, noted."""
    import clockgate  # noqa: E402 - on sys.path via the modcheck package
    n0 = len(clockgate.BENIGN_STOPS)
    try:
        with clockgate.expected_disturbance(BURN_WILDLIFE, burn_wildlife_harm, repair=_walk_wildlife_check):
            yield
    finally:
        got = [b for b in clockgate.BENIGN_STOPS[n0:] if b.get("why") == "expected: " + BURN_WILDLIFE]
        if got and t.session is not None:
            _note(t, "burn line shield: harm to pawns not the player's, resumed past", got)


def _walk_steady_colonists(t):
    """SITE (visit 8, 2026-11-24, his full list): a generated colonist brought GR_FeatherdustAddiction and a heart artery
    blockage from other mods and went down twice in the third week, so the later parts could not be read. The walk's colonists
    start with no ailment they were generated with; whatever they take afterwards is the walk's, and still stops it."""
    r = t.bridge_call("jawa/list_pawns", limit=1000)
    if not _live(t):
        return
    got = {}
    for q in _ok(r, "the colonist listing").get("pawns") or []:
        if q.get("intelligence") == "Humanlike" and q.get("isPlayer") and not q.get("dead"):
            h = t.bridge_call("jawa/pawn_health", pawn=q["id"], action="healAll", confirmDestructive=True)
            got[q["id"]] = (h or {}).get("removed") if (h or {}).get("success") else "refused: %r" % (h or {}).get("message")
    _note(t, "walk: ailments the colonists were generated with, taken off", got)


@suite.chain("walk_season")
@_teardown(fire=True)
def walk_season(t):
    """Scene sc_walk (bar walk_season_on_the_pyre; FULL list, two weeks; Stage 6 only, hold owner_review). Saves
    pre_walk, plays WALK_DAYS, saves mid-way while the front walks, takes a digest, reloads, and the digest after the
    reload equals the one before; control: a reload of pre_walk gives a different digest. Then WALK_DAYS more: the
    second pass yields fruit again; the mechanics switched off and on leave no fire behind; the log holds no error.
    Runs only when PYRE_WALK=1 is in the environment (two game weeks; never in an ordinary suite run). NOT automated:
    the harvest from a scar, the sowing on a fresh burn and on watered ash, and the shelter with a furnace-beast
    through ash fall (the colony's own work over the two weeks; his Stage 8 walk reads them). Every walk save is kept."""
    with _walk_shield(t):
        _walk_steady_colonists(t)
        with _comp(t, "walk_reload_keeps_the_state"):
            if os.environ.get("PYRE_WALK") != "1":
                _unmeasured(t, "the two-week walk runs only with PYRE_WALK=1 (full list, Stage 6)")
            if os.environ.get(WALK_PARTS_ONLY_ENV) == "1" or os.environ.get(WALK_ONE_ENV):
                _unmeasured(t, "%s=1: the two weeks are skipped in a planted run of the walk's later parts" % WALK_PARTS_ONLY_ENV)
            t.bridge_call("rimworld/save_game", saveName=WALK_SAVE + "_pre")
            _wait(t, WALK_DAYS * 60000)
            t.bridge_call("rimworld/save_game", saveName=WALK_SAVE + "_mid")
            mid = walk_digest(t)
            _load_site_save(t, WALK_SAVE + "_mid")
            again = walk_digest(t)
            _load_site_save(t, WALK_SAVE + "_pre")
            pre = walk_digest(t)
            _load_site_save(t, WALK_SAVE + "_mid")
            if _live(t):
                _note(t, "walk digests", {"pre": pre, "mid": mid, "midReloaded": again})
                if digests_match(pre, mid):
                    _unmeasured(t, "the pre-walk and mid-walk digests are equal: the walk changed nothing a reload could lose")
                if not digests_match(mid, again):
                    _fail("the digest after the reload differs from the one before: %r vs %r" % (mid, again))
        with _comp(t, "walk_second_pass_and_switches"):
            if os.environ.get(WALK_PARTS_ONLY_ENV) == "1" or os.environ.get(WALK_ONE_ENV):
                _unmeasured(t, "%s=1: the two weeks are skipped in a planted run of the walk's later parts" % WALK_PARTS_ONLY_ENV)
            _wait(t, WALK_DAYS * 60000)
            fruit_born = _count(t, FRUIT_PLANT) or 0
            mark = _log_mark(t)
            _set(t, {"pyrelandsEnabled": False})
            _extinguish(t)
            _wait(t, 2500)
            fires_off = _count(t, "Fire") or 0
            _set(t, {"pyrelandsEnabled": True})
            _wait(t, 2500)
            errs = [m.get("text", "")[:200] for m in _log_since(t, mark)
                    if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception")]
            t.bridge_call("rimworld/save_game", saveName=WALK_SAVE + "_end")
            if _live(t):
                _note(t, "second half", {"fruitStanding": fruit_born, "firesWithMechanicsOff": fires_off, "errors": errs[:5]})
                if not fruit_born:
                    _fail("no scorch-fruit stood after the second week: the second pass yielded none")
                if fires_off:
                    _fail("%d fire cells burned with the mechanics off after an extinguish" % fires_off)
                if errs:
                    _fail("the log holds %d error line(s) over the switch: %r" % (len(errs), errs[:2]))
        _ten_walk_season(t)
        _r6_walk_season(t)
        _walk_bed_part(t)


# ---- RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED: the owed parts of twelve scenes ----
# Each existing chain ends with `_ten_<chain>(t)`; foreign_arrivals and fire_sense are new chains. A read no bridge tool
# can make is recorded `_unmeasured(...)` with its reason, never invented. Every part is independent of the chain's own
# rows (`_independent`), so a FAIL above does not hide it. Offline (the declaration probe) every bridge call is a no-op.
TEN_DAY = 60000
TEN_WET_STEP = 10000
TEN_HOUR = 2500
TEN_PAD_SENSE = (30, 160)      # fire_sense: free of every other pad (nearest PAD_HERD_OLD, 60 cells)
TEN_PAD_ROOF = (95, 30)        # walk_season's roofed room on ember grass
TEN_PAD_BED = (190, 160)       # furnace_sleep's beast A2 and the muffalo
TEN_PAD_WET = (95, 95)         # ash_fertility_watered's wet and dry potato strips
TEN_PAD_GRASS = (160, 225)     # embergrass_regrow's three sown patches
TEN_PAD_HAWK_FIRE = (30, 60)   # firehawk: the far burn; the second hawk starts TEN_HAWK_OFFSET cells east of it
TEN_HAWK_REACH = 54            # CompFireHawkSpread scanRadius (JobGiver_RUT_FireHawkSeekBurn: seeks only beyond 0.9 * 54)
TEN_HAWK_OFFSET = 100          # > 0.9 * 54 = 48.6 and <= SightRange 180: the seek band. SITE (visit 5, 2026-11-22, ArchBig):
                               # at 60 the spawned hawk's first GotoWander walked 58 -> 54 cells toward the plot inside one
                               # job, so its next think was already in carry reach and the seek never had a decision to take
TEN_GATE = "RimMandrake.Pyrelands.PyrelandsMechanicsGate"
TEN_SAFE_CLEAR = 3             # PyrelandsFireSense.SafeClear (a walking pawn)
TEN_STEP_JOB = "RM_PyreStepAwayFromFire"
TEN_SEEK_JOB = "RM_FireHawkSeekBurn"
PLANT_FARHAWK_NO_SEEK_ENV = "PYRE_PLANT_FARHAWK_NO_SEEK"   # planted state: fireHawkSpreadEnabled off for the seek row
TEN_NATIVE = ("HerdMigration", "ManhunterPack")
TEN_TILE_SCAN = 60000          # world tiles scanned (200 a read) for a vanilla control tile
TEN_CONTROL_SIZE = 100
TEN_WATER_RING = ("Mud", "RM_FE_Ground_SoilRich")   # GenStep_PyrelandsStandingWater's shore ring
TEN_CROP = "Plant_Potato"


def _ten_glow(t, xz):
    """jawa/glow_at on one cell -> {hour, skyGlow, groundGlow}, None offline."""
    r = t.bridge_call("jawa/glow_at", cells="%d,%d" % tuple(xz))
    if not _live(t):
        return None
    _ok(r, "glow_at(%r)" % (xz,))
    cell = (r.get("cells") or [{}])[0]
    return {"hour": r.get("hour"), "skyGlow": r.get("skyGlow"), "groundGlow": cell.get("groundGlow")}


def _ten_hour(t):
    g = _ten_glow(t, (1, 1))
    h = (g or {}).get("hour")
    return float(h) if isinstance(h, (int, float)) else None


def _ten_noon_hour(t, lo=10, hi=14):
    """Run the clock into [lo, hi) and assert it there (the capture hour); UNMEASURED when the clock is unreadable."""
    if not _live(t):
        return None
    h = _ten_hour(t)
    if h is None:
        _unmeasured(t, "glow_at returned no hour, so the %dh-%dh capture window cannot be asserted" % (lo, hi))
    if not lo <= h < hi:
        _wait(t, int(((lo + 0.5 - h) % 24) * TEN_HOUR))
        h = _ten_hour(t)
    if h is None or not lo <= h < hi:
        _fail("the clock reads %r after the run to %dh, outside the %dh-%dh capture window" % (h, lo, lo, hi))
    return h


def _ten_wild_kinds(t):
    """{kindDef: n} of the wild animals (no faction) on the current map; {} offline."""
    r = t.bridge_call("jawa/list_pawns", limit=1000)
    if not _live(t):
        return {}
    _ok(r, "list_pawns")
    if r.get("truncated"):
        _fail("wild animal census truncated: %r" % r.get("message"))
    out = {}
    for p in r.get("pawns") or []:
        if p.get("faction") is None and p.get("intelligence") == "Animal" and not p.get("dead"):
            out[p.get("kindDef")] = out.get(p.get("kindDef"), 0) + 1
    return out


def _ten_static(t, type_, method, args=None):
    kw = {"type": type_, "method": method}
    if args is not None:
        kw["args"] = args
    r = t.bridge_call("jawa/static_call", **kw)
    if not _live(t):
        return None
    _ok(r, "static_call %s.%s" % (type_, method))
    return str(r.get("result"))


def _ten_gate_on(t):
    """PyrelandsMechanicsGate.On (the pyrelandsEnabled setting AND the shell's Pyrelands roster toggle) -> bool or None."""
    v = _ten_static(t, TEN_GATE, "get_On")
    return None if v is None else v.strip().lower() == "true"


ROSTER_TYPE = "RimMandrake.Biomes.RM_BiomesSettings"   # PyrelandsMechanicsGate.ShellType
ROSTER_KEY = "Pyrelands"                               # PyrelandsMechanicsGate.RosterKey


def _ten_roster_set(t, on):
    """The Baroque Biomes roster toggle, RM_BiomesSettings.enabled["Pyrelands"] (an instance dictionary entry; an absent
    key reads on), written through jawa/mod_settings_field key= (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN).
    Back on is written as True, which RM_BiomesSettings.Enabled reads the same as absent. -> the reply."""
    r = t.bridge_call("jawa/mod_settings_field", typeName=ROSTER_TYPE, action="set", field="enabled", key=ROSTER_KEY,
                      value="true" if on else "false")
    if _live(t) and not (r or {}).get("success"):
        _unmeasured(t, "the roster toggle write was refused: %r" % (r,))
    return r


def _ten_roster_on(t):
    """RM_BiomesSettings.Enabled("Pyrelands") read back (PyrelandsMechanicsGate.ShellOn reads the same) -> bool or None."""
    v = _ten_static(t, ROSTER_TYPE, "Enabled", ROSTER_KEY)
    return None if v is None else v.strip().lower() == "true"


def _ten_control_map_tile(t, biome):
    """A land tile the world ALREADY carries as `biome` (flat or small hills, no world object on it), or None. Read
    only: no tile's biome is written (no worldgen of any kind)."""
    for start in range(0, TEN_TILE_SCAN, 200):
        r = t.bridge_call("jawa/world_tile_get", range="%d-%d" % (start, start + 199), limit=200)
        rows = (r or {}).get("tiles") or []
        if not rows:
            return None
        cands = [w.get("tile") for w in rows if w.get("biome") == biome and not w.get("waterCovered")
                 and w.get("hilliness") in ("Flat", "SmallHills")]
        if not cands:
            continue
        objs = t.bridge_call("jawa/world_objects_get", tiles=",".join(str(c) for c in cands), limit=200)
        taken = set(o.get("tile") for o in ((objs or {}).get("objects") or []))
        for c in cands:
            if c not in taken:
                return c
    return None


def _ten_control_map(t, biome, size=TEN_CONTROL_SIZE):
    """A vanilla `biome` map beside the site, generated on a tile that already is `biome` (never world_tile_map_generate's
    biome= write). Leaves it CURRENT, hostiles killed; -> (mapId, tile, site mapId). The caller reads it at once (no
    ticks: no keeper colonist, so nothing culls it) and drops it with _ten_control_map_drop in a finally."""
    if not _live(t):
        return None
    site = (t.bridge_call("jawa/map_info") or {}).get("mapId")
    tile = _ten_control_map_tile(t, biome)
    if tile is None:
        _unmeasured(t, "no free flat %s land tile among the first %d world tiles for the vanilla control map"
                    % (biome, TEN_TILE_SCAN))
    r = _ok(t.bridge_call("jawa/world_tile_map_generate", tile=tile, sizeX=size, sizeZ=size),
            "world_tile_map_generate(%s)" % tile)
    ctl = (r.get("mapId"), tile, site)
    objs = (t.bridge_call("jawa/world_objects_get", tiles=str(tile), limit=10) or {}).get("objects") or []
    ids = ",".join(str(o.get("id")) for o in objs if o.get("id") is not None)
    if ids:
        t.bridge_call("jawa/world_objects_set", ids=ids, faction="PlayerColony")
    t.bridge_call("jawa/set_current_map", mapId=ctl[0])
    t.bridge_call("jawa/kill_hostiles", mapId=ctl[0])
    got = (t.bridge_call("jawa/map_info") or {}).get("mapBiome")
    if got != biome:
        _ten_control_map_drop(t, ctl)
        _unmeasured(t, "the control map on tile %s reads mapBiome %r, not %s" % (tile, got, biome))
    return ctl


def _ten_control_map_drop(t, ctl):
    """Drop the control map (current) and its settlement; the site is current again."""
    if not _live(t) or not ctl:
        return
    mid, tile, site = ctl
    if (t.bridge_call("jawa/map_info") or {}).get("mapId") == mid:
        t.bridge_call("jawa/map_drop", mapIndex=-1, notifyPlayer=False)
    objs = (t.bridge_call("jawa/world_objects_get", tiles=str(tile), limit=10) or {}).get("objects") or []
    ids = ",".join(str(o.get("id")) for o in objs if o.get("id") is not None)
    if ids:
        t.bridge_call("jawa/world_objects_remove", ids=ids)
    if site is not None:
        t.bridge_call("jawa/set_current_map", mapId=site)
    _on_site(t)


def _ten_foreign_arrivals_disallowed():
    """The fixed-species incidents Patches/RM_Pyrelands_NoForeignArrivals.xml refuses on the site."""
    return ("AnimaTreeSpawn", "FarmAnimalsWanderIn", "GauranlenPodSpawn", "HarbingerTreeSpawn", "PoluxTreeSpawn",
            "ThrumboPasses")


def _ten_foreign_arrivals_dry_runs(t, defs):
    """fire_incident(dryRun=True) per def -> {def: canFireNow}. The dry-run reply's success IS canFire, so it is read
    raw, never through _ok."""
    out = {}
    for d in defs:
        r = t.bridge_call("jawa/fire_incident", incidentDef=d, dryRun=True)
        out[d] = (r or {}).get("canFireNow")
    return out


@suite.chain("foreign_arrivals")
@_teardown(fire=True)
def foreign_arrivals(t):
    """Scene sc_foreign_arrivals (gap g1). On the site every disallowed fixed-species incident (_ten_foreign_arrivals_disallowed()) is refused
    (canFireNow False on a dry run) and the wild census holds no species outside ANIMAL_MANIFEST; the native herd
    migration and a manhunter pack fire and bring only roster species. Control: a vanilla AridShrubland map beside the
    site, where at least one of the same incidents can fire. Live half: scenes.json live_command (UNRUN here)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "foreign_incidents_refused"):
        before = _ten_wild_kinds(t)
        dry = _ten_foreign_arrivals_dry_runs(t, _ten_foreign_arrivals_disallowed())
        if _live(t):
            _note(t, "disallowed incidents, canFireNow on the site", dry)
            foreign = sorted(k for k in before if k not in ANIMAL_MANIFEST)
            if foreign:
                _fail("wild animals outside ANIMAL_MANIFEST on the site: %r" % foreign)
            if any(v is None for v in dry.values()):
                _unmeasured(t, "fire_incident dry run unread for %r" % sorted(k for k, v in dry.items() if v is None))
            if any(dry.values()):
                _fail("disallowed incidents can fire on the site: %r" % sorted(k for k, v in dry.items() if v))
    _independent(t)
    with _comp(t, "native_herds_only_roster"):
        got = {}
        for inc in TEN_NATIVE:
            pre = _ten_wild_kinds(t)
            r = t.bridge_call("jawa/fire_incident", incidentDef=inc, dryRun=False, forced=True)
            _wait(t, 600)
            post = _ten_wild_kinds(t)
            new = dict((k, post.get(k, 0) - pre.get(k, 0)) for k in post if post.get(k, 0) > pre.get(k, 0))
            got[inc] = {"fired": (r or {}).get("fired"), "canFireNow": (r or {}).get("canFireNow"), "new": new}
            if inc == "ManhunterPack":
                t.bridge_call("jawa/kill_hostiles")
        if _live(t):
            _note(t, "native incidents and the species they brought", got)
            if not any(v["fired"] for v in got.values()):
                _unmeasured(t, "neither HerdMigration nor ManhunterPack fired: %r" % got)
            stray = sorted(set(k for v in got.values() for k in v["new"] if k not in ANIMAL_MANIFEST))
            if stray:
                _fail("native incidents brought species outside ANIMAL_MANIFEST: %r" % stray)
    _independent(t)
    with _comp(t, "vanilla_control_can_fire"):
        ctl = _ten_control_map(t, "AridShrubland")
        try:
            dry = _ten_foreign_arrivals_dry_runs(t, _ten_foreign_arrivals_disallowed())
        finally:
            _ten_control_map_drop(t, ctl)
        if _live(t):
            _note(t, "disallowed incidents, canFireNow on the vanilla AridShrubland control", dry)
            if not any(dry.values()):
                _unmeasured(t, "no disallowed incident can fire even on the vanilla control (their own gates: season, "
                               "DLC, cooldown), so the site's refusal is not told apart: %r" % dry)


def _ten_lit_plot(t, rect):
    """Soil, ember grass, a ring of concrete, then fire on `rect`."""
    _firebreak(t, rect)
    _soil(t, rect)
    _plants(t, "RM_FE_Plant_EmberGrass", rect)
    return _fire(t, rect)


def _ten_pos(t, pid):
    row = _pawn_row(t, pid)
    return (row.get("x"), row.get("z")) if row else None


def _ten_clear_of(pos, rect):
    """Euclidean distance from `pos` to the nearest cell of `rect`."""
    x, z, w, h = rect
    return min(((pos[0] - cx) ** 2 + (pos[1] - cz) ** 2) ** 0.5 for cx in range(x, x + w) for cz in range(z, z + h))


def _ten_jobs(t, pid, polls, step):
    """The distinct jobs `pid` held, in order, over `polls` reads `step` ticks apart."""
    seq = []
    for _ in range(polls):
        _wait(t, step)
        j = _job_of(t, pid)
        if j and (not seq or seq[-1] != j):
            seq.append(j)
    return seq


@suite.chain("fire_sense")
@_teardown(fire=True, weather=True)
def fire_sense(t):
    """Scene sc_fire_sense (round-5 g2). P, beside a test-lit Fire with Firefighter off, takes RM_PyreStepAwayFromFire and
    ends at least SafeClear (3) cells from the fire; H, urgently hungry (UrgentlyHungry: Food 0.08) with Firefighter on
    and a home-area fire 15 cells off, eats (Ingest) before it beats fire (BeatFire). Control: PyrelandsMechanicsGate
    off (pyrelandsEnabled False) and P beside a fire takes no step-away. The shell's Pyrelands roster toggle has no bridge
    setter: UNMEASURED. Live half: scenes.json live_command (UNRUN here)."""
    _pad(t, TEN_PAD_SENSE)
    t.clear_area(size=TEST_SIZE)
    x, z = t.anchor
    with _comp(t, "fire_sense_gate_on"):
        info = t.bridge_call("jawa/map_info") or {}
        on = _ten_gate_on(t)
        if _live(t):
            if info.get("mapBiome") != "RM_Pyrelands":
                _unmeasured(t, "the current map is %r, not RM_Pyrelands" % info.get("mapBiome"))
            if on is not True:
                _fail("PyrelandsMechanicsGate.get_On reads %r on the site" % on)
    _independent(t)
    with _comp(t, "fire_sense_steps_away"):
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        plot = (x - 1, z - 1, 3, 3)
        p = _spawn_colonist(t, x + 2, z)
        t.bridge_call("jawa/set_work_priority", pawnId=p, workType="Firefighter", priority=0)
        _ten_lit_plot(t, plot)
        seq = _ten_jobs(t, p, 20, 30)
        pos = _ten_pos(t, p)
        if _live(t):
            clear = _ten_clear_of(pos, plot) if pos else None
            _note(t, "P beside the fire: jobs, end cell, distance to the plot (SafeClear %d)" % TEN_SAFE_CLEAR,
                  {"jobs": seq, "end": pos, "clear": clear})
            if TEN_STEP_JOB not in seq:
                _fail("P beside a lit Fire never took %s: %r" % (TEN_STEP_JOB, seq))
            if clear is None or clear < TEN_SAFE_CLEAR:
                _fail("P ended %r cells from the fire, under SafeClear %d" % (clear, TEN_SAFE_CLEAR))
        _extinguish(t)
    _independent(t)
    with _unfed(t), _comp(t, "fire_sense_hungry_eats_first"):
        planted = os.environ.get(PLANT_EAT_FIRST_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: pyrelandsEnabled off for this row, so the core order stands (fire before food)" % PLANT_EAT_FIRST_ENV)
            _set(t, {"pyrelandsEnabled": False})
        h = _spawn_colonist(t, x - 8, z + 6)
        t.bridge_call("jawa/set_work_priority", pawnId=h, workType="Firefighter", priority=1)
        t.bridge_call("jawa/paint_area", area="home", ops=_rs(_rect(t)), value=True)
        t.bridge_call("jawa/spawn_batch", ops="MealSimple:%d,%d,1" % (x + 2, z + 6))
        t.bridge_call("jawa/pawn_need", pawn=h, action="need", need="Food", level=0.08)   # UrgentlyHungry
        _ten_lit_plot(t, (x + 6, z + 5, 2, 2))
        food = _need(t, h, "Food")
        seq = _ten_jobs(t, h, 50, 60)
        if planted:
            _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            _note(t, "H urgently hungry, a fire on the home area: Food at the start, jobs in order", [food, seq])
            if food is None or food > 0.12:
                _unmeasured(t, "H was not urgently hungry at the start (Food %r): no opportunity" % food)
            if "Ingest" not in seq:
                _fail("urgently hungry H never ate (no Ingest) with a fire burning: %r" % seq)
            if "BeatFire" in seq and seq.index("BeatFire") < seq.index("Ingest"):
                _fail("H beat fire (BeatFire) before eating (Ingest) while urgently hungry: %r" % seq)
        _extinguish(t)
    _independent(t)
    with _comp(t, "fire_sense_gate_off_control"):
        _set(t, {"pyrelandsEnabled": False})
        on = _ten_gate_on(t)
        q = _spawn_colonist(t, x + 2, z - 8)
        t.bridge_call("jawa/set_work_priority", pawnId=q, workType="Firefighter", priority=0)
        _ten_lit_plot(t, (x - 1, z - 9, 3, 3))
        seq = _ten_jobs(t, q, 20, 30)
        _extinguish(t)
        _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            _note(t, "gate off: PyrelandsMechanicsGate.On and the jobs beside the fire", {"on": on, "jobs": seq})
            if on is not False:
                _fail("pyrelandsEnabled False left PyrelandsMechanicsGate.get_On %r" % on)
            if TEN_STEP_JOB in seq:
                _fail("with the gate off P still took %s: %r" % (TEN_STEP_JOB, seq))
    _independent(t)
    with _comp(t, "fire_sense_roster_toggle_off"):
        _ten_roster_set(t, False)
        try:
            roster, on = _ten_roster_on(t), _ten_gate_on(t)
            q = _spawn_colonist(t, x + 6, z - 8)
            t.bridge_call("jawa/set_work_priority", pawnId=q, workType="Firefighter", priority=0)
            _ten_lit_plot(t, (x + 3, z - 9, 3, 3))
            seq = _ten_jobs(t, q, 20, 30)
            _extinguish(t)
        finally:
            _ten_roster_set(t, True)
        if _live(t):
            _note(t, "roster toggle off: RM_BiomesSettings.Enabled, PyrelandsMechanicsGate.On and the jobs beside the fire",
                  {"roster": roster, "on": on, "jobs": seq})
            if roster is not False:
                _fail("RM_BiomesSettings.enabled[Pyrelands] = False left Enabled(\"Pyrelands\") %r" % roster)
            if on is not False:
                _fail("the roster toggle off left PyrelandsMechanicsGate.get_On %r" % on)
            if TEN_STEP_JOB in seq:
                _fail("with the roster toggle off P still took %s: %r" % (TEN_STEP_JOB, seq))


def _ten_plant_census(t):
    """sc_populations: the firecast counts (RM_FireHawk >= 2, RM_Ashwallow >= 8); a day of wild-plant spawning with
    wildPlantAllowlistEnabled on, censusing plants outside PLANT_MANIFEST (none may appear).
    Removed controls (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, polish.md): the allowlist-off day (no donor
    plant is in a minimal list's wild-plant pass, and T_ALLOWLIST decides the shipped Postfix over every candidate
    combination offline) and the same-seed gate-off map (the bar asks at least two fire-hawks and eight ashwallows, which
    firecast_counts decides; the top-up's exact shortfall is not a bar)."""
    _independent(t)
    with _comp(t, "firecast_counts"):
        kinds = _ten_wild_kinds(t)
        if _live(t):
            _note(t, "firecast counts", {"RM_FireHawk": kinds.get("RM_FireHawk", 0),
                                         "RM_Ashwallow": kinds.get("RM_Ashwallow", 0)})
            if kinds.get("RM_FireHawk", 0) < 2:
                _fail("RM_FireHawk %d on the site, the scene asks >= 2" % kinds.get("RM_FireHawk", 0))
            if kinds.get("RM_Ashwallow", 0) < 8:
                _fail("RM_Ashwallow %d on the site, the scene asks >= 8" % kinds.get("RM_Ashwallow", 0))
    _independent(t)
    with _comp(t, "wild_plant_allowlist_day"):
        _set(t, {"wildPlantAllowlistEnabled": True})
        pre = _whole_map(t, "Plant")
        _wait(t, TEN_DAY)
        post = _whole_map(t, "Plant")
        foreign = dict((k, post[k] - pre.get(k, 0)) for k in (post or {})
                       if k not in PLANT_MANIFEST and post[k] > pre.get(k, 0))
        if _live(t):
            _note(t, "plants outside PLANT_MANIFEST that appeared in a day with the allowlist on", foreign)
            if foreign:
                _fail("with wildPlantAllowlistEnabled on, foreign plants appeared: %r" % foreign)


PLANT_GATE_IGNORED_ENV = "PYRE_PLANT_GATE_IGNORED"   # planted state for walk_gate_off_then_on: the master switch left on


PLANT_ROSTER_IGNORED_ENV = "PYRE_PLANT_ROSTER_IGNORED"   # planted state for walk_roster_toggle: the toggle left on
WALK_ONE_ENV = "PYRE_WALK_ONE"   # a planted run of one later walk part: its name; the others read UNMEASURED by name


def _walk_one(t, name):
    one = os.environ.get(WALK_ONE_ENV)
    if one and one != name:
        _unmeasured(t, "%s=%s: this part is not in that run" % (WALK_ONE_ENV, one))


def _ten_walk_season(t):
    """sc_walk (PYRE_WALK=1 only): the gate off a day then on; a roofed room on ember grass withers; fire-cast thirst
    (RM_Thirst, no RM_Dehydration); no colonist burned (Burn) or starved (Malnutrition)."""
    walk = os.environ.get("PYRE_WALK") == "1"
    _independent(t)
    with _comp(t, "walk_gate_off_then_on"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_gate_off_then_on")
        planted = os.environ.get(PLANT_GATE_IGNORED_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: pyrelandsEnabled is left on, as if the switch did nothing" % PLANT_GATE_IGNORED_ENV)
        _set(t, {"pyrelandsEnabled": planted})
        # HARNESS (visit 5, 2026-11-22, his full list): the day started with the walk's own 30 fires still burning, and
        # vanilla spread on the grass carpet made 928 by the day's end: a fire then cannot tell a new front from spread.
        # The day starts from an extinguished map, so any fire after it was lit in the day.
        _extinguish(t)
        off = _ten_gate_on(t)
        a0, f0 = _depth(t, None), _count(t, "Fire")
        _wait(t, WALK_OFF_SPELL_TICKS)   # visit 8: in one day a quiet map relights nothing, so an ignored gate read PASS
        a1, f1 = _depth(t, None), _count(t, "Fire")
        _set(t, {"pyrelandsEnabled": True})
        on = _ten_gate_on(t)
        _wait(t, TEN_DAY)
        a2 = _depth(t, None)
        if _live(t):
            _note(t, "PyrelandsMechanicsGate off a day, then on a day: ash depthSum, fires",
                  {"off": off, "on": on, "ash": [a0, a1, a2], "fires": [f0, f1]})
            if (off is not False and not planted) or on is not True:
                _fail("PyrelandsMechanicsGate.get_On read %r off / %r on" % (off, on))
            if f1:
                _fail("%d fires burning after a day with the gate off" % f1)
            if a1 is not None and a0 is not None and a1 > a0 + 1e-6:
                _fail("ash gained %.3f with the gate off" % (a1 - a0))
    _independent(t)
    with _comp(t, "walk_roster_toggle"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_roster_toggle")
        planted = os.environ.get(PLANT_ROSTER_IGNORED_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: the roster toggle is left on, as if it did nothing" % PLANT_ROSTER_IGNORED_ENV)
        _ten_roster_set(t, planted)
        try:
            _extinguish(t)   # as the gate-off day: a fire after the day was lit in it, never the walk's spread
            roster, off = _ten_roster_on(t), _ten_gate_on(t)
            a0, f0 = _depth(t, None), _count(t, "Fire")
            _wait(t, WALK_OFF_SPELL_TICKS)   # as the gate's off spell
            a1, f1 = _depth(t, None), _count(t, "Fire")
        finally:
            _ten_roster_set(t, True)
        on = _ten_gate_on(t)
        _wait(t, TEN_DAY)
        a2 = _depth(t, None)
        if _live(t):
            _note(t, "roster toggle off a day, then on a day: Enabled(Pyrelands), the gate, ash depthSum, fires",
                  {"roster": roster, "off": off, "on": on, "ash": [a0, a1, a2], "fires": [f0, f1]})
            if ((roster is not False or off is not False) and not planted) or on is not True:
                _fail("roster toggle off read Enabled %r / gate %r, back on the gate %r" % (roster, off, on))
            if f1:
                _fail("%d fires burning after a day with the roster toggle off" % f1)
            if a1 is not None and a0 is not None and a1 > a0 + 1e-6:
                _fail("ash gained %.3f with the roster toggle off" % (a1 - a0))
    _independent(t)
    with _comp(t, "walk_roofed_grass_withers"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_roofed_grass_withers")
        _pad(t, TEN_PAD_ROOF)
        x, z = t.anchor
        room = (x - 4, z - 4, 9, 9)
        inner = (x - 3, z - 3, 7, 7)
        t.bridge_call("jawa/make_empty_room", rect=_rs(room), stuffDef="Steel", doorDef="Wall", floorDef=SOIL,
                      roofDef="RoofConstructed")
        t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % _rs(inner))
        _plants(t, "RM_FE_Plant_EmberGrass", inner)
        n0 = _count(t, "RM_FE_Plant_EmberGrass", _rs(inner))
        _wait(t, 3 * TEN_DAY)
        n1 = _count(t, "RM_FE_Plant_EmberGrass", _rs(inner))
        if _live(t):
            _note(t, "ember grass under a roof, 3 days", [n0, n1])
            if not n0:
                _unmeasured(t, "no ember grass took inside the roofed room")
            if n1 >= n0:
                _fail("roofed ember grass did not wither in 3 days: %r -> %r" % (n0, n1))
    _independent(t)
    with _comp(t, "walk_firecast_thirst_and_colonists"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_firecast_thirst_and_colonists")
        thirst, bad = {}, []
        for _ in range(4):
            r = t.bridge_call("jawa/list_pawns", limit=1000, includeHealth=True)
            for p in ((r or {}).get("pawns") or []):
                if p.get("dead"):
                    continue
                if p.get("intelligence") == "Animal" and p.get("kindDef") in ANIMAL_MANIFEST:
                    thirst[p.get("id")] = _need(t, p.get("id"), "RM_Thirst")
                    if _has_hediff(p, "RM_Dehydration"):
                        bad.append((p.get("id"), "RM_Dehydration"))
                if p.get("intelligence") == "Humanlike" and p.get("faction") == "Player":
                    for hd in ("Burn", "Malnutrition"):
                        if _has_hediff(p, hd):
                            bad.append((p.get("id"), hd))
            _wait(t, TEN_DAY // 4)
        if _live(t):
            _note(t, "fire-cast RM_Thirst levels", thirst)
            if not any(v is not None for v in thirst.values()):
                _fail("no fire-cast animal carries an RM_Thirst need")
            if bad:
                _fail("over a day: %r" % sorted(set(bad)))


def _ten_ground_deep_ash(t):
    """sc_ash_ground: at noon (asserted) save ashground_noon; AshFall locked, light (glow_at skyGlow) and ProbeAsh each
    hour; reload ashground_noon, Clear over the same hours; ash-fall light below and ash gain above at every hour.
    Shore ring: every land cell beside standing water reads Mud or RM_FE_Ground_SoilRich."""
    _independent(t)
    with _comp(t, "ash_fall_vs_clear_by_hour"):
        _ten_noon_hour(t)
        t.bridge_call("rimworld/save_game", saveName="ashground_noon")
        runs = {}
        for w in (ASHFALL, "Clear"):
            _load_site_save(t, "ashground_noon")
            _on_site(t)
            t.bridge_call("jawa/weather_set", weather=w, lockWeather=True)
            rows = []
            a0 = _ash(t).get("depthSum")
            for _ in range(4):
                _wait(t, TEN_HOUR)
                gr = t.bridge_call("jawa/glow_at", cells="%d,%d" % tuple(t.anchor)) or {}
                g = {"hour": gr.get("hour"), "skyGlow": gr.get("skyGlow")}
                a = _ash(t).get("depthSum")
                rows.append({"hour": g.get("hour"), "skyGlow": g.get("skyGlow"),
                             "gain": None if a is None or a0 is None else a - a0})
            runs[w] = rows
        t.bridge_call("jawa/weather_set", unlock=True)
        if _live(t):
            _note(t, "ash fall vs clear from ashground_noon, hour by hour", runs)
            for af, cl in zip(runs[ASHFALL], runs["Clear"]):
                if af["hour"] != cl["hour"]:
                    _fail("the two runs read different clock hours: %r / %r" % (af["hour"], cl["hour"]))
                if not af["skyGlow"] < cl["skyGlow"]:
                    _fail("at hour %r ash-fall light %r is not below clear %r" % (af["hour"], af["skyGlow"], cl["skyGlow"]))
                if not af["gain"] > cl["gain"]:
                    _fail("at hour %r ash-fall gain %r is not above clear %r" % (af["hour"], af["gain"], cl["gain"]))
    _independent(t)
    with _comp(t, "shore_ring"):
        r = t.bridge_call("jawa/get_terrain_batch", rects=_whole(t))
        if _live(t):
            _ok(r, "get_terrain_batch(whole map)")
            cells = {}
            for op in str(r.get("ops") or "").split(";"):
                d, _, rr = op.partition(":")
                try:
                    ox, oz, ow, oh = (int(v) for v in rr.split(","))
                except ValueError:
                    continue
                for cx in range(ox, ox + ow):
                    for cz in range(oz, oz + oh):
                        cells[(cx, cz)] = d
            # standing water only: is_water_family also holds Mud (the ash sweep's radius), and a mud relic with no water
            # beside it rings nothing (MEASURED 2026-11-20 visit 2: 0 water cells, 8 'shore' cells beside mud failed)
            water = set(c for c, d in cells.items() if is_standing_water(d))
            if not water:
                _unmeasured(t, "this map rolled no standing water, so there is no shore ring to read")
            ring = {}
            for (cx, cz) in water:
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        n = (cx + dx, cz + dz)
                        if n in cells and n not in water:
                            ring[n] = cells[n]
            off = dict((c, d) for c, d in ring.items() if d not in TEN_WATER_RING)
            tally = {}
            for d in ring.values():
                tally[d] = tally.get(d, 0) + 1
            _note(t, "shore ring terrain (Mud / RM_FE_Ground_SoilRich expected)", tally)
            if off:
                _fail("%d of %d shore-ring cells are neither Mud nor RM_FE_Ground_SoilRich: %r"
                      % (len(off), len(ring), sorted(off.items())[:8]))


def _ten_cinderfall(t):
    """sc_three_skies: each sky (AshFall, Cinderfall, BlackRain, Rain) from a reload of skies_noon, the capture hour
    asserted 10h-14h, a screenshot each; then two equal LayAsh patches from reloads, Clear vs BlackRain, wash_verdict."""
    _independent(t)
    with _comp(t, "three_skies_from_noon"):
        _ten_noon_hour(t)
        t.bridge_call("rimworld/save_game", saveName="skies_noon")
        hours = {}
        for w in (ASHFALL, CINDERFALL, BLACKRAIN, "Rain"):
            _load_site_save(t, "skies_noon")
            _on_site(t)
            _ten_noon_hour(t)
            _sky(t, w)
            hours[w] = _ten_hour(t)
            if _live(t) and not (hours[w] is not None and 10 <= hours[w] < 14):
                _fail("the %s capture hour %r is outside 10h-14h" % (w, hours[w]))
            t.screenshot(name="sky_%s" % w, rect=_sky_rect(t))
        _note(t, "capture hours per sky", hours)
    _independent(t)
    with _comp(t, "blackrain_wash_vs_clear_patch"):
        rect = _rs(_rect(t, size=12))
        got = {}
        for w in ("Clear", BLACKRAIN):
            _load_site_save(t, "skies_noon")
            _on_site(t)
            _sky(t, w)
            t.bridge_call("jawa/static_call", type=ASH_SAND, method="LayAsh", args="%s|%s" % (rect, WASH_DEPTH))
            a = _depth(t, rect)
            _wait(t, WASH_TICKS)
            got[w] = (a, _depth(t, rect))
        t.bridge_call("jawa/weather_set", unlock=True)
        if _live(t):
            ok, why = wash_verdict(got["Clear"], got[BLACKRAIN])
            _note(t, "equal patches from skies_noon: clear vs black rain", why)
            if not ok:
                _fail(why)


def plant_growth_of_lines(lines):
    """Pure. One plant's inspect-pane lines -> its growth 0-1, or None when no line states it. The game's English key
    PercentGrowth is '{0} grown' ('70% grown'); a mature plant reads 'Mature.' (1.0). HARNESS, Pyrelands visit 4,
    2026-11-21: the reader looked for 'Growth: N%', a line the game never writes, and read None for every patch on every
    day of visit 3 (RIMMANDRAKE_READ_PYRE_REGROW_GROWTH_NONE_ON_ALL_SIX_DAYS; live lines in visit_4/evidence/
    script_inspect_probe.log)."""
    for ln in lines or []:
        m = re.search(r"(\d+(?:\.\d+)?)%\s*grown", str(ln))
        if m:
            return float(m.group(1)) / 100.0
        if str(ln).strip().rstrip(".").lower() == "mature":
            return 1.0
    return None


REGROW_STEP_TICKS = 4000     # two long ticks: each plant grows exactly twice
REGROW_BURST_TICKS = 2000    # the mature patches are watched this much longer
REGROW_CHARGE_HOURS = 1      # ExplosiveGrowth chargeHours for the row (shipped 6): mature to burst in 2,500 ticks
REGROW_DROP_TOL = 0.01       # a plant's growth fell: a restart, a graze or a swap
REGROW_PATCHES = ("dry", "watered", "vanilla", "matureDry", "matureWet")


def regrow_step_verdict(got):
    """Pure. sc_grass_regreens growth part, one staged growth step. got: {"before", "after", "last": {patch: {plantId:
    growth}}, "growDays": {def: days}}; "before" at the sowing, "after" REGROW_STEP_TICKS later, "last" REGROW_BURST_TICKS
    after that. -> (True/False/None, why, {"gain", "emberVanillaGain", "fell"}).
    Dry ember grass gains at least its own vanilla share (Plant_Grass's gain on the same dry ash, scaled by growDays); watered
    gains more than dry; a plant whose growth falls burst: never on the dry, vanilla or mature-dry patch, and on the soaked
    mature patch at least once (the control: without it the read cannot see a burst). A patch that does not hold the same
    plants at every read is UNMEASURED: a plant taken or brought in reads like a burst (visit 9)."""
    d = {"gain": {}, "emberVanillaGain": None, "fell": {}}
    reads = [(got or {}).get(k) or {} for k in ("before", "after", "last")]
    if any(not r.get(k) for r in reads for k in REGROW_PATCHES):
        return None, "a patch was unread: %r" % ([{k: len(r.get(k) or {}) for k in REGROW_PATCHES} for r in reads],), d
    before, after, last = reads
    moved = [k for k in REGROW_PATCHES if set(before[k]) != set(after[k]) or set(after[k]) != set(last[k])]
    if moved:
        return None, "plants left or came into %r, so a fall is not a burst" % (moved,), d
    gd = (got or {}).get("growDays") or {}
    eg, vg = gd.get("RM_FE_Plant_EmberGrass"), gd.get("Plant_Grass")
    if not eg or not vg:
        return None, "growDays unread: %r" % (gd,), d
    for k in REGROW_PATCHES:
        d["fell"][k] = sum(1 for i in before[k] if after[k][i] < before[k][i] - REGROW_DROP_TOL
                           or last[k][i] < after[k][i] - REGROW_DROP_TOL)
    off = [k for k in REGROW_PATCHES if k != "matureWet" and d["fell"][k] and k != "watered"]
    for k in ("dry", "watered", "vanilla"):
        d["gain"][k] = sum(after[k][i] - before[k][i] for i in before[k]) / len(before[k])
    if off:
        return False, "growth fell (a burst) off the watered cells: %r" % (dict((k, d["fell"][k]) for k in off),), d
    if d["gain"]["vanilla"] <= 0:
        return None, "the vanilla grass did not grow in the step (night, heat or dark), so there is no rate to hold: %r" % (d["gain"],), d
    d["emberVanillaGain"] = d["gain"]["vanilla"] * vg / eg
    if d["gain"]["dry"] < d["emberVanillaGain"]:
        return False, "dry ember grass gained %.4f in the step, below its vanilla rate's %.4f" % (
            d["gain"]["dry"], d["emberVanillaGain"]), d
    if not d["gain"]["watered"] > d["gain"]["dry"]:
        return False, "watered ember grass did not outgrow the dry patch: %.4f vs %.4f" % (d["gain"]["watered"], d["gain"]["dry"]), d
    if not d["fell"]["matureWet"]:
        return None, "no soaked mature plant burst, so the read cannot show a burst: 'none on dry' is not shown", d
    return True, "dry %.4f >= vanilla rate %.4f, watered %.4f, bursts %r" % (
        d["gain"]["dry"], d["emberVanillaGain"], d["gain"]["watered"], d["fell"]), d


def _jump_clock(t, ticks, why):
    """Age every absolute-tick stamp by `ticks` without simulating (jawa/time_set_ticks); reads the clock back."""
    now = _r6_tick(t)
    if not _live(t):
        return
    r = t.bridge_call("jawa/time_set_ticks", ticks=now + int(ticks), timeException=True, why=why)
    _ok(r, "time_set_ticks")
    after = _r6_tick(t)
    if after != now + int(ticks):
        _unmeasured(t, "the clock did not jump: %r -> %r, asked %r" % (now, after, now + int(ticks)))


def _ten_embergrass_regrow_read(t, rect):
    """{plant id: Growth} of every plant in `rect` (jawa/thing_read, exact), {} when unread."""
    r = t.bridge_call("jawa/thing_read", rect=_rs(rect), defName="RM_FE_Plant_EmberGrass,Plant_Grass", members="Growth")
    if not _live(t) or not (r or {}).get("success") or (r or {}).get("truncated"):
        return {}
    vals = dict((row.get("id"), _ten_num((row.get("values") or {}).get("Growth"))) for row in r.get("rows") or [])
    return vals if vals and all(v is not None for v in vals.values()) else {}


def _ten_embergrass_regrow(t):
    """sc_grass_regreens, the growth of sown patches, one staged growth step (it played 12 game days until visit 9). Five 4x4
    deep-ash patches burned together, then the clock jumped past 7 days (no fresh-burn bonus, ExplosiveGrowth's fresh ash
    spent); a WaterShallow column beside one. Sown at 5%: ember grass dry and watered, Plant_Grass dry; sown mature: ember
    grass dry, and ember grass soaked (ExplosiveGrowthAPI.Soak, the control that shows a burst). From about 9h,
    REGROW_STEP_TICKS of growth and REGROW_BURST_TICKS more; regrow_step_verdict decides on each plant's exact growth. A steel
    ring keeps grazers out (visit 9: the row had none, and plants came and went from the patches; a hungry nuna set beside
    them eats one, graze_stage.py); a wild pawn inside when it closes is removed."""
    _independent(t)
    with _comp(t, "regrow_dry_watered_vanilla"):
        _pad(t, TEN_PAD_GRASS)
        _isolate(t)
        t.clear_area(size=TEST_SIZE)
        x, z = t.anchor
        patches = {"dry": (x - 9, z - 2, 4, 4), "watered": (x - 2, z - 2, 4, 4), "vanilla": (x + 5, z - 2, 4, 4),
                   "matureDry": (x - 9, z - 8, 4, 4), "matureWet": (x + 5, z - 8, 4, 4)}
        yard = (x - 9, z - 8, 18, 10)
        _firebreak(t, yard, width=2)
        if os.environ.get(PLANT_REGROW_NO_RING_ENV) == "1":
            _note(t, "PLANTED STATE", "%s=1: no ring round the patches" % PLANT_REGROW_NO_RING_ENV)
        else:
            ring = [(cx, cz) for cx in range(yard[0] - 1, yard[0] + yard[2] + 1)
                    for cz in range(yard[1] - 1, yard[1] + yard[3] + 1)
                    if cx in (yard[0] - 1, yard[0] + yard[2]) or cz in (yard[1] - 1, yard[1] + yard[3])]
            t.bridge_call("jawa/build_batch", ops=";".join("Wall:%d,%d" % c for c in ring), stuff="Steel")
            for pw in (t.bridge_call("jawa/list_pawns", rect=_rs(yard), limit=100) or {}).get("pawns") or []:
                if pw.get("id") and not pw.get("isPlayer"):
                    t.bridge_call("jawa/pawn_force_incapacitate", pawn=pw["id"], action="vanish")
        # the ground between the patches is bare: the biome's carpet must not bring fire to a patch, or a plant into it
        t.bridge_call("jawa/set_terrain", x=yard[0], z=yard[1], terrainDef=FIREBREAK, width=yard[2], height=yard[3], layer="top")
        t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % _rs(yard))
        for k, r in patches.items():
            t.bridge_call("jawa/set_terrain", x=r[0], z=r[1], terrainDef=DEEP_ASH, width=r[2], height=r[3], layer="top")
            _plants(t, "RM_FE_Plant_EmberGrass", r)
            _fire(t, r)
        _wait(t, 2 * TEN_HOUR)
        _extinguish(t)
        h = _ten_hour(t)
        if _live(t) and h is None:
            _unmeasured(t, "glow_at gave no clock hour, so the step cannot be put in daylight")
        # past 7 days (the freshBurnDays bonus and ashFlushDays are spent), and to 8h, so the step runs 9h to 11h
        _jump_clock(t, 8 * TEN_DAY + int(((8.0 - (h or 8.0)) % 24) * TEN_HOUR), "the sown patches' burn is a week old")
        t.bridge_call("jawa/set_terrain", x=x - 3, z=z - 2, terrainDef="WaterShallow", width=1, height=4, layer="top")
        _wait(t, 2600)                     # a full watering sweep
        cells = dict((k, _probe(t, patches[k][0] + 1, patches[k][1] + 1)) for k in patches)
        t.set_setting(EG_SETTINGS, {"chargeHours": REGROW_CHARGE_HOURS})
        planted = os.environ.get(PLANT_REGROW_WET_OFF_ENV) == "1"
        if planted:   # after the staging read, so the patch still reads watered: the field's water then does nothing
            _note(t, "PLANTED FAULT", "%s=1: ashWaterFertilityEnabled off from the sowing on, as if water did nothing"
                  % PLANT_REGROW_WET_OFF_ENV)
            _set(t, {"ashWaterFertilityEnabled": False})
        try:
            for k, r in patches.items():
                t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % _rs(r))
                _plants(t, "Plant_Grass" if k == "vanilla" else "RM_FE_Plant_EmberGrass", r,
                        growth=1.0 if k.startswith("mature") else 0.05)
            soak = patches["matureWet"] if os.environ.get(PLANT_REGROW_SOAK_DRY_ENV) != "1" else patches["matureDry"]
            if soak is patches["matureDry"]:
                _note(t, "PLANTED FAULT", "%s=1: the dry mature patch is the one soaked, so bursts land off it" % PLANT_REGROW_SOAK_DRY_ENV)
            for cx in range(soak[0], soak[0] + soak[2]):
                for cz in range(soak[1], soak[1] + soak[3]):
                    t.bridge_call("jawa/static_call", type="RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI", method="Soak",
                                  args="current|%d,%d|%d" % (cx, cz, 4 * TEN_HOUR))
            defs = _get_defs(t, "ThingDef/RM_FE_Plant_EmberGrass;ThingDef/Plant_Grass", "plant")
            reads = [dict((k, _ten_embergrass_regrow_read(t, r)) for k, r in patches.items())]
            for wait in (REGROW_STEP_TICKS, REGROW_BURST_TICKS):
                _wait(t, wait)
                reads.append(dict((k, _ten_embergrass_regrow_read(t, r)) for k, r in patches.items()))
        finally:
            t.set_setting(EG_SETTINGS, {"chargeHours": EG_CHARGE_HOURS})
            if planted:
                _set(t, {"ashWaterFertilityEnabled": True})
        if _live(t):
            _note(t, "patch cells a week after the burn (burnTick, watered, bonus)", cells)
            dry = [k for k in ("dry", "vanilla", "matureDry") if cells[k].get("watered")]
            if dry or not cells["watered"].get("watered"):
                _unmeasured(t, "the patches are not dry/watered as staged: %r" % cells)
            if any(str(c.get("ashField")) != "True" for c in cells.values()):
                _unmeasured(t, "a patch is not ash-field ground (the scene asks for deep ash): %r" % cells)
            if any(float(c.get("bonus") or 0) > 0 for c in cells.values()):
                _unmeasured(t, "a patch still carries the fresh-burn bonus after the jump: %r" % cells)
            if any(str(c.get("burnTick")) in ("-1", "None") for c in cells.values()):
                _unmeasured(t, "a patch was never burned (burnTick -1): %r" % cells)
            gd = dict((d, float(((f.get("plant") or {}).get("growDays")) or 0)) for d, f in defs.items())
            got = {"before": reads[0], "after": reads[1], "last": reads[2], "growDays": gd}
            ok, why, detail = regrow_step_verdict(got)
            _note(t, "one growth step of %d ticks, then %d more" % (REGROW_STEP_TICKS, REGROW_BURST_TICKS),
                  dict(detail, why=why, plants=dict((k, len(v)) for k, v in reads[0].items()), growDays=gd))
            if ok is None:
                _unmeasured(t, why)
            if not ok:
                _fail(why)
        t.screenshot(rect=(x - 10, z - 9, 20, 12))


EG_SETTINGS = "RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings"
EG_CHARGE_HOURS = 6          # ExplosiveGrowthSettings.chargeHours as shipped (selftest_pyrelands_regrow_rates pins it to the C#)
PLANT_REGROW_WET_OFF_ENV = "PYRE_PLANT_REGROW_WET_ROOTS_OFF"
PLANT_REGROW_NO_RING_ENV = "PYRE_PLANT_REGROW_NO_RING"   # planted state: grazers may reach the patches
PLANT_REGROW_SOAK_DRY_ENV = "PYRE_PLANT_REGROW_SOAK_DRY"   # planted state: bursts land on the patch that must show none
PLANT_VENOM_TEND_WRONG_ENV = "PYRE_PLANT_VENOM_TEND_WRONG_PATIENT"   # planted state: the tend lands on the untended patient   # planted state: the ash field's water switched off at sowing


@suite.chain("regrow_growth")
@_teardown(fire=True)
@_wildlife_shielded
def regrow_growth(t):
    """sc_grass_regreens' sown-patch row alone (the embergrass_regrow chain runs it too)."""
    _ten_embergrass_regrow(t)


def _ten_furnace_sleep(t):
    """sc_furnace_bed: beast A2 (RM_FurnaceBeast) asleep on its ember-grass plot, a Muffalo asleep on a like plot; per poll
    ProbeSleep and a Fire count on each sleeper's own cell (x,z,1,1); the muffalo's plot is lit once A2's burns. Health
    (health=True) before and after: A2 takes no burns, the muffalo does."""
    _independent(t)
    with _comp(t, "bed_fire_beast_vs_muffalo"):
        _pad(t, TEN_PAD_BED)
        t.clear_area(size=TEST_SIZE)
        x, z = t.anchor
        plots = {"A2": (x - 8, z - 2, 5, 5), "muffalo": (x + 3, z - 2, 5, 5)}
        beds = dict((k, (r[0] + 2, r[1] + 2)) for k, r in plots.items())
        _set(t, {"furnaceThermalEnabled": True})
        _firebreak(t, (x - 8, z - 2, 16, 5))
        for r in plots.values():
            _soil(t, r)
            _plants(t, "RM_FE_Plant_EmberGrass", r)
        ids = {"A2": _spawn_wild(t, "RM_FurnaceBeast", *beds["A2"]), "muffalo": _spawn_wild(t, "Muffalo", *beds["muffalo"])}
        before = dict((k, _pawn_row(t, pid, health=True)) for k, pid in ids.items())
        for k, pid in ids.items():
            t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
            t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=0.05)
            t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="LayDown", targetAX=beds[k][0], targetAZ=beds[k][1],
                          waitTicks=0)
        polls, lit = [], False
        for i in range(SLEEP_WAIT_TICKS // SLEEP_POLL_TICKS):
            _wait(t, SLEEP_POLL_TICKS)
            row = {"tick": (i + 1) * SLEEP_POLL_TICKS}
            for k, pid in ids.items():
                kv = parse_kv(_ten_static(t, FURNACE_BED, "ProbeSleep", pid) or "")
                c = xz_of(kv.get("cell")) or beds[k]
                row[k] = {"awake": kv.get("awake"), "cell": kv.get("cell"),
                          "fireOnOwnCell": _count(t, "Fire", "%d,%d,1,1" % tuple(c))}
            polls.append(row)
            if not lit and _count(t, "Fire", _rs(plots["A2"])):
                _fire(t, plots["muffalo"])
                lit = True
            if lit and len(polls) > 1 and not _count(t, "Fire", "%d,%d,16,5" % (x - 8, z - 2)):
                break
        _extinguish(t)
        after = dict((k, _pawn_row(t, pid, health=True)) for k, pid in ids.items())
        if _live(t):
            _note(t, "per poll: ProbeSleep and the Fire on each sleeper's own cell (1,1)", polls[-24:])
            if not lit:
                _unmeasured(t, "A2's plot never lit in %d ticks asleep" % SLEEP_WAIT_TICKS)
            new = dict((k, len(burn_injuries(after[k])) - len(burn_injuries(before[k]))) for k in ids)
            _note(t, "new burn injuries, A2 vs muffalo", new)
            if new["A2"] > 0:
                _fail("the furnace-beast A2 took %d burn injuries in its own bed fire" % new["A2"])
            if new["muffalo"] <= 0:
                _fail("the Muffalo in a like bed fire took no burns (the control did not bite)")


def tended_rises_less(tended, untended):
    """Hourly venom severities of the tended and the untended patient, read 0 at the tend order -> (ok, why). Pure.
    In every hour after the tend order the tended venom rose less than the untended venom did in the same hour: "rises
    more slowly at every hourly read". The hourly rise, not the level: two bites never carry one dose (armour and a part's
    hit points cap the damage that RM_FlamefangVenomBite scales) and the patients are bitten at different ticks, so the
    levels differ by the bite, not by the tend. Per hour, not since read 0: a tend that stopped working after its first
    hour would keep a cumulative lead. Scripted
    (selftest_pyrelands_venom_staging.py): the level comparison FAILED a working tend and PASSED a tend that did nothing,
    on unequal doses."""
    if len(tended) < 2 or len(tended) != len(untended):
        return False, "fewer than 2 paired reads: %r / %r" % (tended, untended)
    rises = [(tended[i] - tended[i - 1], untended[i] - untended[i - 1]) for i in range(1, len(tended))]
    bad = [i + 1 for i, (a, b) in enumerate(rises) if not a < b]
    if bad:
        return False, "the tended venom rose no less than the untended in hour(s) %r: hourly rises %r (tended %r, " \
                      "untended %r)" % (bad, [(round(a, 4), round(b, 4)) for a, b in rises], tended, untended)
    return True, "smallest margin %.4f" % min(b - a for a, b in rises)


def _ten_flamefang_venom(t):
    """sc_flamefang_venom: two colonists bitten once each (VENOM); a doctor tends one (TendPatient); severity every hour
    for six hours, the tended venom's rise in each hour below the untended's (tended_rises_less); the untended venom read daily until the hediff goes. The
    immunity read is removed (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, polish.md): the bar reads the venom
    hediff and its severity, not immunity."""
    x, z = PAD_VENOM
    _independent(t)
    # HARNESS (visit 6, 2026-11-22, ArchSmall): the first row's patient, untended, was downed by its venom during this row
    # and the row read RESTART (twice); like the wait-out, the earlier envenomed patients are not this row's subjects
    _GEN["not_subjects"] = _retire_venom_patients(t)
    with _comp(t, "venom_tended_vs_untended"):
        # SITE (visit 4, 2026-11-22): both patients were spawned before either bite, so the second, undrafted, fled from
        # the first one's biter, and the first (drafted, standing) took the second one's biter again and again: venom 0.67
        # at the tend against one bite's ~0.1, and in the planted run it bled out of the untended bites (RESTART). Each
        # patient is now spawned just before its own bite, and drafted at once by _bite_until.
        pts = {}
        for k, pz in (("tended", z), ("untended", z - 8)):
            pts[k] = pid = _spawn_colonist(t, x + 10, pz)
            row = _bite_until(t, pid, "RM_Flamefang", x + 10, pz, hediff=VENOM, clear_wounds=True)
            if _live(t) and not _has_hediff(row, VENOM):
                _unmeasured(t, "the %s patient was never envenomed: %r" % (k, (row or {}).get("health")))
        doc = _spawn_colonist(t, x + 12, z)
        _GEN.setdefault("venom_fixtures", []).extend([pts["tended"], pts["untended"], doc])
        wrong = os.environ.get(PLANT_VENOM_TEND_WRONG_ENV) == "1"
        if wrong:
            _note(t, "PLANTED FAULT", "%s=1: the doctor tends the untended patient, as if the tend did nothing for the "
                  "tended one" % PLANT_VENOM_TEND_WRONG_ENV)
        r = t.bridge_call("jawa/ordered_job", pawnId=doc, jobDef="TendPatient",
                          targetAId=pts["untended" if wrong else "tended"])
        # HARNESS (Pyrelands visit 4, 2026-11-21): the doctor walks over and tends inside the first hour, so that hour's rise
        # was mostly untended (0.0152 = 13 untended updates) and the row failed it, though the bar compares 'every hour from
        # the tend onwards'. The hourly series starts once the doctor's TendPatient job has run and ended.
        tend_seen, tend_wait = False, 0
        while _live(t) and tend_wait < TEN_HOUR:
            j = _job_of(t, doc)
            if j == "TendPatient":
                tend_seen = True
            elif tend_seen:
                break
            _venom_wait(t, 30)
            tend_wait += 30
        series = {"tended": [], "untended": []}
        for _ in range(VENOM_HOURS + 1):
            for k, pid in pts.items():
                series[k].append(hediff_severity(_pawn_row(t, pid, health=True), VENOM))
            _venom_wait(t, TEN_HOUR)
        if _live(t):
            _note(t, "venom severity each hour, tended vs untended", {"order": r, "series": series,
                                                                         "tendSeen": tend_seen, "tendEndedAfterTicks": tend_wait})
            if not (r or {}).get("success"):
                _unmeasured(t, "the TendPatient order was refused: %r" % r)
            if not tend_seen:
                _unmeasured(t, "the doctor's TendPatient job was never seen in the hour after the order (polled every 30 "
                               "ticks), so 'from the tend onwards' has no start: %r" % r)
            if any(v is None for k in series for v in series[k]):
                _unmeasured(t, "venom severity unread: %r" % series)
            ok, why = tended_rises_less(series["tended"], series["untended"])
            if not ok:
                _fail(why)
    _independent(t)
    # SITE (Pyrelands visit 3, 2026-11-21): the earlier rows' envenomed patients stay on the map untended through this
    # row's ten days; one died of the venom and two were downed, which voided the row (RESTART). They are not its
    # subject, so their fate is left out of its damage reading.
    retired = _retire_venom_patients(t)
    # SITE (Pyrelands visit 4): the earlier rows' other colonists (the plain-bite control, the tended pair, the doctor)
    # are this chain's fixtures too, drafted or bitten for their own rows; a bystander's fate is not the wait-out's answer.
    fixtures = [p_ for p_ in _GEN.pop("venom_fixtures", None) or [] if p_ and p_ not in retired]
    _GEN["not_subjects"] = list(retired) + fixtures
    with _comp(t, "venom_wait_out"):
        if _live(t):
            _note(t, "earlier venom patients on the map, not this row's subjects", retired)
        cid = _spawn_colonist(t, x + 10, z + 8)
        row = _bite_until(t, cid, "RM_Flamefang", x + 10, z + 8, hediff=VENOM, clear_wounds=True)
        # the subject's own death by the venom is this row's answer (a FAIL), not damage to the test
        _GEN["measured_death"] = cid
        days, died = [], None
        for day in range(10):
            sub = _subject_row(t, cid)
            if _live(t) and (sub is None or sub.get("dead")):
                died = day
                break
            s = hediff_severity(sub, VENOM)
            days.append(s)
            if _live(t) and s is None:
                break
            # ten days on the site: every pawn, the drafted subject included, is fed each FEED_EVERY ticks (visit 3: a
            # bystander starved; visit 4: the subject itself, fed only once a day, reached Starving inside day 2)
            _venom_wait(t, TEN_DAY, stop_on=WAIT_OUT_STOP_ON)
        if _live(t):
            _note(t, "untended venom severity each day until it goes (immunity unread)", {"days": days, "diedOnDay": died})
            if not _has_hediff(row, VENOM):
                _unmeasured(t, "the wait-out colonist was never envenomed")
            if died is not None:
                _fail("the untended colonist died of %s by day %d (severity each day %r): the venom killed before "
                      "immunity completed" % (VENOM, died, days))
            if days[-1] is not None:
                _fail("the venom was still present after 10 days: %r" % days)


def _ten_ash_fertility_watered(t):
    """sc_ash_watered: a wet and a dry deep-ash strip of Plant_Potato; the cell temperature above the crop's
    maxOptimalGrowthTemperature asserted (else UNMEASURED); five inspect reads 10,000 ticks apart (the factor is a state read:
    what varies it is the hour's temperature, so one day samples it; it was five days until visit 9), the wet-roots line on wet only;
    control: ashWaterFertilityEnabled off drops it. Each read also takes every crop's Plant.GrowthRateFactor_Temperature
    (jawa/thing_read runs the patched getter, RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN) and vanilla's
    PlantUtility.GrowthRateFactorFor_Temperature at the dry strip's cell temperature; growth_rate_factor_temperature
    judges them."""
    wet_line = "Wet ash keeps its roots"   # Languages: the wet-roots inspect line (PyrelandsWetRoots)
    _GEN.pop("wet_roots_reads", None)
    _independent(t)
    with _comp(t, "wet_roots_cool_the_crop"):
        _pad(t, TEN_PAD_WET)
        t.clear_area(size=TEST_SIZE)
        x, z = t.anchor
        radius = int(float(_live_setting(t, "ashNaturalWaterRadius") or 0)) if _live(t) else 4
        if _live(t) and radius + 8 > TEST_SIZE // 2:
            _unmeasured(t, "ashNaturalWaterRadius %d leaves no dry strip inside the pad" % radius)
        wet = (x - 6, z - 1, 3, 2)
        dry = (x - 6 + radius + 6, z - 1, 3, 2)
        for r in (wet, dry):
            t.bridge_call("jawa/set_terrain", x=r[0], z=r[1], terrainDef=DEEP_ASH, width=r[2], height=r[3], layer="top")
        t.bridge_call("jawa/set_terrain", x=wet[0] - 1, z=wet[1], terrainDef="WaterShallow", width=1, height=2, layer="top")
        _wait(t, 2600)
        for r in (wet, dry):
            _plants(t, TEN_CROP, r, growth=0.3)
        crop = _get_defs(t, "ThingDef/%s" % TEN_CROP, "plant").get(TEN_CROP) or {}
        top = (crop.get("plant") or {}).get("maxOptimalGrowthTemperature")
        reads = []
        for _ in range(5):
            tr = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (wet[0], wet[1])) or {}
            temp = tr.get("temperature", tr.get("temp"))
            lines = {}
            for k, r in (("wet", wet), ("dry", dry)):
                got = t.bridge_call("jawa/inspect_string", rect=_rs(r), limit=10) or {}
                lines[k] = any(wet_line in str(ln) for row in got.get("things") or [] for ln in row.get("inspect") or [])
            fac = dict((k, _ten_temp_factors(t, r)) for k, r in (("wet", wet), ("dry", dry)))
            dr = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (dry[0], dry[1])) or {}
            dry_temp = dr.get("temperature", dr.get("temp"))
            van = (_ten_static(t, "RimWorld.PlantUtility", "GrowthRateFactorFor_Temperature", "%s|%r" % (TEN_CROP, dry_temp))
                   if isinstance(dry_temp, (int, float)) else None)
            reads.append({"temp": temp, "wetLine": lines["wet"], "dryLine": lines["dry"], "wetFactor": fac["wet"],
                          "dryFactor": fac["dry"], "dryTemp": dry_temp, "vanillaDry": _ten_num(van)})
            _GEN["wet_roots_reads"] = {"reads": reads, "top": top}
            _wait(t, TEN_WET_STEP)
        if _live(t):
            _note(t, "each read: cell temperature vs %s maxOptimalGrowthTemperature %r, the wet-roots line" % (TEN_CROP, top),
                  reads)
            if not isinstance(top, (int, float)):
                _unmeasured(t, "%s maxOptimalGrowthTemperature unread: %r" % (TEN_CROP, crop))
            hot = [rd for rd in reads if isinstance(rd["temp"], (int, float)) and rd["temp"] > top]
            if not hot:
                _unmeasured(t, "the cell never read above %s's maxOptimalGrowthTemperature %.1f (no tool heats an "
                               "outdoor cell): %r" % (TEN_CROP, top, [rd["temp"] for rd in reads]))
            if any(rd["dryLine"] for rd in reads):
                _fail("the dry strip shows '%s': %r" % (wet_line, reads))
            if not all(rd["wetLine"] for rd in hot):
                _fail("a hot day's wet strip lacks '%s': %r" % (wet_line, reads))
        _set(t, {"ashWaterFertilityEnabled": False})
        got = t.bridge_call("jawa/inspect_string", rect=_rs(wet), limit=10) or {}
        off = any(wet_line in str(ln) for row in got.get("things") or [] for ln in row.get("inspect") or [])
        _set(t, {"ashWaterFertilityEnabled": True})
        if _live(t) and off:
            _fail("with ashWaterFertilityEnabled off the wet strip still shows '%s'" % wet_line)
    _independent(t)
    with _comp(t, "growth_rate_factor_temperature"):
        got = _GEN.get("wet_roots_reads")
        if _live(t):
            _note(t, "each read: GrowthRateFactor_Temperature: wet / dry strip and vanilla's at the dry cell", got)
            ok, why = growth_factor_verdict(got)
            if ok is None:
                _unmeasured(t, why)
            if not ok:
                _fail(why)


GROWTH_FACTOR_TOL = 1e-4   # the dry strip's factor and vanilla's are the same function of the same temperature; this only
                           # absorbs the text rendering of two floats (Convert.ToString, round-trip digits)


def _ten_num(v):
    """A rendered number -> float, or None for anything that is not one (an ERR text, None)."""
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def _ten_temp_factors(t, rect):
    """Plant.GrowthRateFactor_Temperature of every TEN_CROP in `rect` (jawa/thing_read; the patched getter runs) ->
    [float], or None when the read failed or any value is unreadable (never a partial list)."""
    r = t.bridge_call("jawa/thing_read", rect=_rs(rect), defName=TEN_CROP, members="GrowthRateFactor_Temperature")
    if not (r or {}).get("success") or (r or {}).get("truncated"):
        return None
    vals = [_ten_num((row.get("values") or {}).get("GrowthRateFactor_Temperature")) for row in r.get("rows") or []]
    return vals if vals and all(v is not None for v in vals) else None


def growth_factor_verdict(got):
    """The sc_ash_watered factor bar on the daily reads -> (True, None) | (False, why) | (None, why: could not see).
    Every day: each dry-strip factor equals vanilla's at the dry cell (wet roots leaves dry ash alone) and the weakest
    wet-strip factor is at least the strongest dry one; on each hot day (cell above maxOptimalGrowthTemperature, where
    PyrelandsWetRoots.CooledFactor acts) the strongest wet factor is above the strongest dry one. At least one hot day.
    Strongest, not weakest, on the hot day: the 3-wide wet strip reaches past ashNaturalWaterRadius (default 2) from its
    water column, so its far column is dry ash and reads the dry factor by design."""
    if not got or not got.get("reads"):
        return None, "wet_roots_cool_the_crop did not reach its daily reads, so no factor was read"
    reads, top = got["reads"], got.get("top")
    if not isinstance(top, (int, float)):
        return None, "maxOptimalGrowthTemperature unread: %r" % (top,)
    blind = [i for i, rd in enumerate(reads) if not rd.get("wetFactor") or not rd.get("dryFactor")
             or rd.get("vanillaDry") is None or not isinstance(rd.get("temp"), (int, float))]
    if blind:
        return None, "the factors were unreadable on day(s) %r: %r" % (blind, [reads[i] for i in blind])
    hot = [rd for rd in reads if rd["temp"] > top]
    if not hot:
        return None, "the cell never read above maxOptimalGrowthTemperature %.1f: %r" % (top, [rd["temp"] for rd in reads])
    for i, rd in enumerate(reads):
        off = [f for f in rd["dryFactor"] if abs(f - rd["vanillaDry"]) > GROWTH_FACTOR_TOL]
        if off:
            return False, "day %d: dry-strip factor(s) %r differ from vanilla's %.4f at %.1f C" % (
                i, off, rd["vanillaDry"], rd["dryTemp"])
        if min(rd["wetFactor"]) < max(rd["dryFactor"]) - GROWTH_FACTOR_TOL:
            return False, "day %d: the watered strip's factor %r is below the dry strip's %r" % (
                i, rd["wetFactor"], rd["dryFactor"])
        if rd["temp"] > top and not max(rd["wetFactor"]) > max(rd["dryFactor"]) + GROWTH_FACTOR_TOL:
            return False, "hot day %d (%.1f C > %.1f): the watered strip's factor %r is not above the dry strip's %r" % (
                i, rd["temp"], top, rd["wetFactor"], rd["dryFactor"])
    return True, None


def _ten_firehawk(t):
    """sc_firehawk: a second RM_FireHawk spawned 60 cells from a burning plot (beyond 0.9 x scanRadius 54, inside
    SightRange 180) takes RM_FireHawkSeekBurn and closes; control: fireHawkSpreadEnabled off, a third hawk at the same
    offset never seeks. The giver reads distance only (no line-of-sight test), so 'visible' is the distance band."""
    def watch(hawk, plot):
        # HARNESS (visit 2, 2026-11-20): a flyer closes 49 cells inside one 250-tick gap, so a seek that starts and hands
        # over to the carry within it was never sampled (dist 60 -> 11 at the first read). 25 polls 10 ticks apart first,
        # then the same 60 polls 250 apart as before.
        # SITE (visit 4, 2026-11-21, game a, 2 of 2 runs): the fire-hawks the chain's first row and the map itself leave
        # alive carried embers off the plot and lit fires nearer the far hawk than the seek band, so it took
        # RM_FireHawkCarryEmber from one of them and never the seek. Every fire outside the plot is counted at each read,
        # with its nearest distance to the watched hawk: a missing seek beside such a fire is the site's, not the mod's.
        seq, dist, strays = [], [], []
        acted = False   # the hawk has taken a carry or a seek: a fire after that is its own drop, never a rival to the plot
        for i in range(85):
            _wait(t, 10 if i < 25 else 250)
            if not _count(t, "Fire", _rs(plot)):
                _plants(t, "RM_FE_Plant_EmberGrass", plot)
                t.bridge_call("jawa/map_fire", action="start", rect=_rs(plot), fireSize=1.2)
            j = _job_of(t, hawk)
            if j and (not seq or seq[-1] != j):
                seq.append(j)
            before = not acted
            acted = acted or j in (TEN_SEEK_JOB, "RM_FireHawkCarryEmber")
            pos = _ten_pos(t, hawk)
            if pos:
                dist.append(round(_ten_clear_of(pos, plot), 1))
            px, pz, pw, ph = plot
            out = [c for c in _r6_fires(t) if not (px <= c[0] < px + pw and pz <= c[1] < pz + ph)]
            if out and pos:
                strays.append({"read": i, "fires": len(out), "beforeAct": before, "nearest": round(min(
                    ((c[0] - pos[0]) ** 2 + (c[1] - pos[1]) ** 2) ** 0.5 for c in out), 1)})
        return seq, dist, strays

    def lone_hawks():
        """Kill every living RM_FireHawk on the map (the first row's and the map's own) before a far-hawk row; -> count."""
        r = t.bridge_call("jawa/list_pawns", limit=1000)
        if not _live(t):
            return 0
        ids = [q.get("id") for q in (_ok(r, "list_pawns").get("pawns") or [])
               if q.get("kindDef") == "RM_FireHawk" and not q.get("dead") and q.get("id")]
        for pid in ids:
            t.bridge_call("jawa/damage", damageDef="Bullet", amount=5000, thingId=pid, allowColonists=False)
        return len(ids)

    fx, fz = TEN_PAD_HAWK_FIRE
    plot = (fx - 2, fz - 2, 5, 5)
    _independent(t)
    with _comp(t, "far_hawk_seeks_the_burn"):
        # SITE (visit 2, 2026-11-20): the chain's earlier rows leave fires burning, and one within the hawk's scanRadius
        # gave it RM_FireHawkCarryEmber (then the sortie cooldown) instead of the seek; the plot must be the only fire
        planted = os.environ.get(PLANT_FARHAWK_NO_SEEK_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: fireHawkSpreadEnabled off for this row, as if the hawk never sought"
                  % PLANT_FARHAWK_NO_SEEK_ENV)
        killed = lone_hawks()
        _extinguish(t)
        _set(t, {"burnLineEnabled": True, "fireHawkSpreadEnabled": not planted})
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        _ten_lit_plot(t, plot)
        hawk = _spawn_wild(t, "RM_FireHawk", fx + TEN_HAWK_OFFSET, fz)
        # SITE (visit 8, 2026-11-23): a thirsty hawk's RM_DrinkFromTerrain flew it to water inside the ember reach of the
        # burn, so the carry took over and the seek band was never tried. It starts watered and fed.
        for need in ("RM_Thirst", "Food"):
            t.bridge_call("jawa/pawn_need", pawn=hawk, action="need", need=need, level=1.0)
        seq, dist, strays = watch(hawk, plot)
        if planted:
            _set(t, {"fireHawkSpreadEnabled": True})
        if _live(t):
            _note(t, "far hawk (start %d cells; seek band > %.1f): jobs, distance to the burn; other hawks killed first; "
                  "fires outside the plot" % (TEN_HAWK_OFFSET, 0.9 * TEN_HAWK_REACH),
                  {"jobs": seq, "dist": dist, "otherHawksKilled": killed, "strays": strays[:20]})
            if TEN_SEEK_JOB not in seq:
                # HARNESS (visit 5, 2026-11-22): only a fire seen before the hawk's first carry or seek can have taken
                # the plot's place; the fires after it were the hawk's own drops and read UNMEASURED in error
                near = [r_ for r_ in strays if r_["nearest"] <= 0.9 * TEN_HAWK_REACH and r_.get("beforeAct", True)]
                if near:
                    _unmeasured(t, "the hawk never took %s, but a fire outside the plot burned %.1f cells from it (inside "
                                   "the seek band's floor %.1f), so the plot was not the only fire: %r"
                                % (TEN_SEEK_JOB, min(r_["nearest"] for r_ in near), 0.9 * TEN_HAWK_REACH, near[:5]))
                _fail("the hawk %d cells off never took %s: %r" % (TEN_HAWK_OFFSET, TEN_SEEK_JOB, seq))
            if not dist or min(dist) >= dist[0] - 10:
                _fail("the seeking hawk did not close on the burn: %r" % dist)
    _independent(t)
    with _comp(t, "far_hawk_spread_off_control"):
        lone_hawks()
        _extinguish(t)
        _set(t, {"fireHawkSpreadEnabled": False})
        _ten_lit_plot(t, plot)
        hawk = _spawn_wild(t, "RM_FireHawk", fx + TEN_HAWK_OFFSET, fz + 6)
        seq, dist, _strays = watch(hawk, plot)
        _extinguish(t)
        _set(t, {"fireHawkSpreadEnabled": True})
        if _live(t):
            _note(t, "fireHawkSpreadEnabled off: jobs, distance", {"jobs": seq, "dist": dist})
            if TEN_SEEK_JOB in seq:
                _fail("with fireHawkSpreadEnabled off the hawk still took %s" % TEN_SEEK_JOB)


def _ten_ruins_charred_walls(t):
    """The unowned Wall cells from the complete BuildingArtificial census, then a read-only paint census of those cells
    (jawa/paint_building with no colorDef) -> (wall count, charred count). Pyrelands visit 3, 2026-11-21: a whole-map
    export_things stops at its 2000-row limit inside the ember-grass carpet (plants first), never read `truncated`, and
    reported 'no unowned walls' on a site whose census listed 453 unowned ruin buildings, Walls among them."""
    r = t.bridge_call("jawa/list_things", group="BuildingArtificial", limit=5000)
    if not _live(t):
        return 0, 0
    _ok(r, "list_things(group=BuildingArtificial)")
    if r.get("isCompleteList") is False:
        _unmeasured(t, "the BuildingArtificial census is truncated (%s rows): unowned walls may be missed"
                       % len(r.get("things") or []))
    cells = sorted({(x["x"], x["z"]) for x in r.get("things") or []
                    if x.get("def") == "Wall" and x.get("x") is not None
                    and (x.get("factionName") or x.get("faction")) in (None, "", "None")})
    if not cells:
        return 0, 0
    c = t.bridge_call("jawa/paint_building", cells=";".join("%d,%d" % xz for xz in cells))
    _ok(c, "paint_building census")
    if c.get("mode") != "census":
        _unmeasured(t, "paint_building did not answer as a census: %r" % str(c)[:200])
    rows = [x for x in c.get("census") or [] if x.get("def") == "Wall"]
    walls = sum(int(x.get("count") or 0) for x in rows)
    charred = sum(int(x.get("count") or 0) for x in rows if x.get("color") == "RM_FE_Charred")
    _note(t, "paint census of the unowned wall cells", {"cells": len(cells), "census": rows[:8]})
    return walls, charred


def _ten_ruins(t):
    """sc_ruins: the ruin walls carry RM_FE_Charred paint (FireEcologyHook's ChangePaint), read through export_things'
    paint field. The vanilla TemperateForest control map is removed (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN,
    polish.md): RM_FE_Charred is this mod's own paint, so no vanilla ruin can carry it, and the bar is about Pyrelands
    ruins only."""
    _independent(t)
    with _comp(t, "ruin_walls_charred_paint"):
        walls, charred = _ten_ruins_charred_walls(t)
        if _live(t):
            _note(t, "unowned walls on the site, painted RM_FE_Charred", {"walls": walls, "charred": charred})
            if not walls:
                _unmeasured(t, "this site has no unowned walls (no ruin) to read the paint of")
            if not charred:
                _fail("none of %d ruin walls carries RM_FE_Charred paint" % walls)


# ---- RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN: the owed parts of the round-6 gap scenes ----
# Each existing chain ends with `_r6_<chain>(t)`; furnace_hide_bank, roof_withers and herd_thirst are new chains. As with the
# _ten_ parts: a read no bridge tool can make is `_unmeasured(...)` with its reason, every part is `_independent`, and
# offline (the declaration probe) every bridge call is a no-op. Selftest: selftest_pyrelands_round6_parts.py.
R6_PLAY_PPC = 64                 # play zoom (px per cell on the PNG, play_zoom.py), as Graffiti's PLAY_PPC
R6_HALF_DAY = 30000
R6_FRONT_HOURS = 8               # sc_burn_line_walks: one capture per game hour (24 until visit 9: the moving centre shows in 8)
R6_FRONT_SAVE_HOUR = 4           # the kept walking-front save is made at this capture
R6_FRONT_MIN_SHIFT = 3.0         # cells the front's centroid must move over the day (a walking line, not one standing blaze)
R6_FRONT_CROP = 30               # largest side of the capture rect around the front
R6_HOUR_TOL = 0.6                # a capture's clock hour may sit this far from its expected hour
R6_SHARE_DAYS = 4                # sc_burn_line_walks' "a few days": the visit-1 walk saves' flood took 78% of the map in 4
                                 # (T_BURN_ECOLOGY); the model's slowest wind-off flood crosses half only on day 4 (325 map)
R6_SHARE_MOST = 0.5              # the leaf's "never most of the map": more than half of the open plantable ground is most
R6_SHARE_PAD_RADIUS = 18         # the suite's own fire pads are left out, as _fresh_site leaves them (CountBurnedOutside)
R6_SHARE_SAVE = "burn_line_share_start"   # the start both arms of the share read begin from (same seed, same front)
R6_ASH_EPS = 1e-3
R6_PAD_ASH_DRAW = (190, 95)      # sc_ash_ground's ten ash-laden ember-grass cells (free of every other pad)
R6_PAD_COMPOUND = (160, 30)      # sc_burn_compounds' three pads (PAD_BURN 35 cells west, PAD_SPRAY 65 east)
R6_PAD_WITHER = (95, 125)        # roof_withers' two walled patches
R6_COMPOUND_DAYS = 7
R6_DRY_FRESH, R6_WET_OLD, R6_WET_FRESH = 1.2, 1.4, 1.9   # sc_burn_compounds' "about" fertilities (evidence only)
R6_WITHER_HOURS = 48
R6_WITHER_GONE_BY = 36
R6_BANK_HOURS = 12
R6_BANK_FROM_HOUR = 6
R6_BANK_MARGIN = 5.0             # room A at least this far above room B from R6_BANK_FROM_HOUR
R6_BANK_CEILING = 21.5           # RM_FurnaceHideBank heatPushMaxTemperature 21, plus a reading's slack
R6_BANK_COST = 60                # RM_FurnaceHideBank costList RM_FurnaceHide
R6_THIRST_HOURS = 72
R6_ARRIVAL_HOURS = 168
R6_THIRST_RATIO = 1.0 / 3        # the ullai's fall at most a third of the muffalo's
R6_DRINK_CELLS = 2
R6_HERD_RADIUS = 10              # MapComponent_PyrelandsHerdThirst.HerdRadius
R6_HERD_STAGGER_TICKS = 2600     # one CheckIntervalTicks (2500) and a little: spawned animals are staggered first
R6_HERD_THIRST = "MapComponent_PyrelandsHerdThirst"   # jawa/map_comp_read matches a substring of the SHORT type name; a namespaced name never matches (visit 2)
R6_ROSTER_MIN = 9                # inv_animal_roster's nine native kinds: fewer is a blind read
R6_CENSUS_MUTATORS = ("jawa/set_plants", "jawa/spawn_pawn", "jawa/spawn_batch", "jawa/set_terrain",
                      "jawa/set_terrain_batch", "jawa/spawn_fill_area", "rimworld/spawn_thing")
R6_WITHER_LINE = "Withering: it needs open sky."   # Languages/English/Keyed/Pyrelands.xml RM_WithersUnderRoof


def _r6_log_calls(t):
    """Record every mutating bridge call this run makes (R6_CENSUS_MUTATORS) in _GEN["mutations"], once per context: the
    script's own call log, read by sc_grass_regreens' census-first check."""
    if getattr(t, "_r6_logged", False) or not hasattr(t, "bridge_call"):
        return
    orig = t.bridge_call

    def logged(tool, **kw):
        # live calls only (HARNESS, Pyrelands visit 4, 2026-11-21): the driver's offline declaration pass walks every chain
        # with no session first, and its 338 no-op calls were logged as mutations made before grass_cover's live census
        if tool in R6_CENSUS_MUTATORS and _live(t):
            _GEN.setdefault("mutations", []).append(tool)
        return orig(tool, **kw)
    t.bridge_call = logged
    t._r6_logged = True


def _r6_incidents(t):
    """The storyteller's pending incident queue -> [def names], None offline or unread."""
    r = t.bridge_call("jawa/incident_queue_peek")
    if not _live(t) or not isinstance(r, dict) or r.get("success") is False:
        return None
    rows = r.get("queue") or r.get("incidents") or r.get("queued") or []
    return sorted(str(q.get("def") or q.get("incidentDef") or q.get("defName") or q) for q in rows)


def _r6_guard(t):
    """Colony vitals and the pending incidents, recorded together (the script audit's guard around a long wait)."""
    return {"vitals": _vitals(t), "incidents": _r6_incidents(t)}


def _r6_guard_changes(before, after):
    """Pure. -> [reason]: a colonist lost, newly downed or starving (vitals_damage), or a pending incident added."""
    why = vitals_damage((before or {}).get("vitals") or {}, (after or {}).get("vitals") or {})
    b, a = (before or {}).get("incidents"), (after or {}).get("incidents")
    if b is not None and a is not None:
        new = sorted(set(a) - set(b))
        if new:
            why.append("pending incidents added: %r" % new)
    return why


def padded_inside(rect, map_size, pad=1):
    """Pure. (x, z, w, h) moved so that it, grown by `pad` cells each side, lies inside the map. HARNESS (visit 3): the
    burn front reached the map's west edge, the capture's 1-cell padding asked for x = -1 and the hour read UNMEASURED."""
    x, z, w, h = inside_map((rect[0] - pad, rect[1] - pad, rect[2] + 2 * pad, rect[3] + 2 * pad), map_size)
    return x + pad, z + pad, max(1, w - 2 * pad), max(1, h - 2 * pad)


def front_crop(cells, crop=None):
    """Pure. Fire cells -> (x, z, w, h): the capture rect of the burn front, at most `crop` (R6_FRONT_CROP) a side, laid
    on the densest crop x crop window of the fires, so the rect holds fire. HARNESS (Pyrelands visit 6, 2026-11-22,
    ArchSmall): the rect was laid from the bounding box's min corner (min x of one fire, min z of another), and 10 of the
    24 hourly captures, the last one included, showed grass with no front while 48 to 111 fires burned. Presumed cause
    (the run kept no fire cells): fires off the front (the run read 12 to 21) put that corner far from it.
    selftest_pyrelands_frames_subject.py holds the rule. None for no readable cell."""
    crop = crop or R6_FRONT_CROP
    busy = densest_cluster(cells, crop)
    if not busy:
        return None
    x0, z0 = min(c[0] for c in busy), min(c[1] for c in busy)
    w = min(crop, max(c[0] for c in busy) - x0 + 1)
    d = min(crop, max(c[1] for c in busy) - z0 + 1)
    return x0, z0, max(w, 4), max(d, 4)


def _r6_shot(t, rect, name):
    """A capture of `rect` at play zoom; its path, None offline."""
    if _live(t):
        rect = padded_inside(rect, _map_size(t))
    return t.screenshot(name=name, rect=tuple(rect), ppc=R6_PLAY_PPC)


def fire_cells(rows):
    """Pure. jawa/list_things Fire rows -> ([(x, z)] of the fires, [rows with no readable cell]). The bridge's row
    (JawaBenchTerrainTools.ThingListRow) carries x and z at its top level, and no position or parent; a dict or list
    `position` is read too. A row with a truthy parent (an attached fire) is not the burn line. A row with no cell is
    returned, never dropped: visit 2's reader looked for `position` first, dropped every row and read 0 fires at all 24
    hours on a burning map (RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES)."""
    cells, unplaced = [], []
    for f in rows or []:
        if not isinstance(f, dict):
            unplaced.append(f)
            continue
        if f.get("parent"):
            continue
        x, z, p = f.get("x"), f.get("z"), f.get("position")
        if (x is None or z is None) and isinstance(p, dict):
            x, z = p.get("x"), p.get("z")
        if (x is None or z is None) and isinstance(p, (list, tuple)) and len(p) >= 2:
            x, z = p[0], p[-1]
        try:
            cells.append((int(x), int(z)))
        except (TypeError, ValueError):
            unplaced.append(f)
    return cells, unplaced


def _r6_fires(t):
    """Free-standing Fire cells on the map -> [(x, z)]; UNMEASURED when a row has no cell (a blind count is not 0)."""
    cells, unplaced = fire_cells(_things(t, "Fire", limit=2000))
    if unplaced:
        _unmeasured(t, "list_things gave %d Fire row(s) with no cell, so the fire count would read blind: %r"
                    % (len(unplaced), unplaced[:2]))
    return cells


def front_walks(rows, min_shift=R6_FRONT_MIN_SHIFT):
    """Pure. rows: [{hour, fires, cx, cz}] one per capture. -> (True/False/None, why): every hour holds fire and the
    fire's centroid moved at least `min_shift` cells from its first to its farthest reading; None with no rows."""
    if not rows:
        return None, "no hourly reads"
    dark = [r["hour"] for r in rows if not r.get("fires")]
    if dark:
        return False, "no fire at hour(s) %r: the front did not walk every hour watched" % dark
    c0 = (rows[0]["cx"], rows[0]["cz"])
    shift = max(_dist(c0, (r["cx"], r["cz"])) for r in rows)
    if shift < min_shift:
        return False, "the front's centroid moved at most %.1f cells over the day (< %.1f)" % (shift, min_shift)
    return True, "fire every hour; the centroid moved up to %.1f cells" % shift


def open_ground_outside(cells, fert, pads, radius):
    """Pure. {(x, z): terrain} and {terrain: fertility} -> how many cells are open plantable ground (fertility > 0; water
    and rock read 0) outside `radius` (Chebyshev) of every pad: the denominator CountBurnedOutside's numerator matches. A
    terrain with no fertility read is not counted as ground."""
    n = 0
    for (x, z), d in cells.items():
        if (fert.get(d) or 0) <= 0:
            continue
        if any(abs(x - px) <= radius and abs(z - pz) <= radius for px, pz in pads):
            continue
        n += 1
    return n


def burned_share_verdict(on, off, most=R6_SHARE_MOST):
    """Pure. on, off: the burned share of open plantable ground at the start and at each day end (day 0..N), wind carrying
    fire and the same start save with windCarriesFireEnabled off (vanilla's even spread). -> (True/False/None, why).
    False: the wind-on map is most of the way burned at any day end (a flood), or its trail never grew. None: unread, or
    the wind-off control never reached most of the map, so this seed cannot show the read telling a line from a flood.
    The limit is the leaf's own word ("never most of the map"), held against a control that must cross it."""
    if not on or not off or len(on) != len(off) or any(v is None for v in list(on) + list(off)):
        return None, "share reads missing or uneven (on %r, off %r)" % (on, off)
    days = len(on) - 1
    worst = max(range(len(on)), key=lambda i: on[i])
    if on[worst] > most:
        return False, ("wind on: %.2f of the open ground burned by day %d (> %.2f, most of the map): a flood; the wind-off "
                       "control read %.2f" % (on[worst], worst, most, off[-1]))
    if on[-1] <= on[0]:
        return False, "wind on: the burned share stayed %.3f over %d days: no scorched trail grew" % (on[0], days)
    if off[-1] <= most:
        return None, ("the wind-off control burned only %.2f of the open ground in %d days (<= %.2f): no flood on this seed, "
                      "so the read cannot show it tells the line from one" % (off[-1], days, most))
    return True, ("wind on: at most %.2f of the open ground burned (day %d) over %d days, limit %.2f; wind off: %.2f, a flood"
                  % (on[worst], worst, days, most, off[-1]))


def _r6_share_ground(t):
    """sc_burn_line_walks' denominator: open plantable ground outside the suite's fire pads, from the whole map's terrain
    and each terrain's fertility. None offline."""
    cells = _r6_terrain_cells(t, _whole(t))
    if not _live(t):
        return None
    terr = sorted(set(cells.values()))
    fert = _get_defs(t, ";".join("TerrainDef/%s" % d for d in terr), "fertility", deep=False) if terr else {}
    return open_ground_outside(cells, dict((d, (fert.get(d) or {}).get("fertility")) for d in terr), FIRE_PADS,
                               R6_SHARE_PAD_RADIUS)


def _r6_burned_share(t, ground):
    """Cells burned since generation outside the fire pads (the ash field's burn stamp), over `ground` -> share, None
    offline or unread. A stamp on a non-plantable cell (a ruin floor) only raises it: a flood cannot hide in it."""
    pads = ";".join("%d,%d" % p for p in FIRE_PADS)
    r = t.bridge_call("jawa/static_call", type=ASH_FIELD, method="CountBurnedOutside",
                      args="%s|%d" % (pads, R6_SHARE_PAD_RADIUS))
    if not _live(t) or not ground:
        return None
    try:
        n = int(str((r or {}).get("result")).strip())
    except ValueError:
        return None
    return float(n) / ground if n >= 0 else None


def _r6_tick(t):
    """The game clock (TicksGame), None offline or unread."""
    return t.session._ticks() if _live(t) and t.session is not None else None


def _r6_share_days(t, ground, arm, t0, first=1):
    """Play to the end of days `first`..R6_SHARE_DAYS counted from tick `t0` (the start save's clock, so an hourly watch
    cut short cannot shorten the window), reading the burned share and a whole-map capture at each day end -> ([share],
    [capture]). A day end the clock cannot place reads None."""
    sx, sz = _map_size(t)
    shares, shots = [], []
    for d in range(first, R6_SHARE_DAYS + 1):
        now = _r6_tick(t)
        if t0 is None or now is None:
            _wait(t, TEN_DAY)
            shares.append(None)
            shots.append(None)
            continue
        if t0 + d * TEN_DAY > now:
            _wait(t, t0 + d * TEN_DAY - now)
        shares.append(_r6_burned_share(t, ground))
        shots.append(t.screenshot(name="burn_share_%s_day_%d" % (arm, d), rect=(0, 0, sx, sz)))
    return shares, shots


def _r6_burn_line(t, share=True):
    """sc_burn_line_walks: the walk watches a fresh map's opening front, as the scenario says. The site is an aged fixture
    whose own front was lit at its birth and is long out (visit 2), so the map is extinguished (burn_line_present's reseed
    included), fireClockEnabled set, and MapComponent_BurnLine.RearmOpeningFront lays yesterday's fire and lights its arc
    by the mod's own arrival path (no test fire); ProbeOpeningFront must then say lit by that re-arm (litTick at or after
    it), else the row is UNMEASURED before a day is spent. Then vitals and pending incidents
    recorded; R6_FRONT_HOURS hourly captures at play zoom of the front's box, each capture's clock hour asserted; one save while the
    front walks (burn_line_walking, kept for his review); front_walks decides; the guard read again at the end.
    The flood read (burn_line_burned_share): the burned share of open plantable ground at the start and at each day end
    over R6_SHARE_DAYS, a whole-map capture with each; then the start save (R6_SHARE_SAVE) reloaded with
    windCarriesFireEnabled off, the same days read the same way; burned_share_verdict decides (a moving centre and a
    front-cropped capture cannot tell a line from a flood: a flood also burns and moves).
    Control: the same day with burnLineEnabled off and the map extinguished lights no free-standing Fire."""
    _independent(t)
    with _comp(t, "burn_line_walks_hourly"):
        _set(t, {"burnLineEnabled": True, "fireClockEnabled": True})
        _extinguish(t)
        rearm_tick = _r6_tick(t)
        if t.session is not None:
            t.session._pyre_opening_rearmed = True   # opening_front's old-save read is UNMEASURED after this in a session
        r = t.bridge_call("jawa/static_call", type=BURN_LINE, method="RearmOpeningFront")
        if _live(t) and str((_ok(r, "RearmOpeningFront") or {}).get("result")).strip() != "1":
            _unmeasured(t, "RearmOpeningFront refused (is this Pyrelands DLL deployed, is the current map Pyrelands?): %r" % r)
        _wait(t, OPENING_WAIT_TICKS)
        kv = parse_kv(_ten_static(t, BURN_LINE, "ProbeOpeningFront") or "")
        if _live(t):
            lit, lit_tick = str(kv.get("lit") or ""), str(kv.get("litTick") or "")
            if kv.get("done") != "True" or not lit.isdigit() or int(lit) <= 0 or not lit_tick.lstrip("-").isdigit() \
                    or rearm_tick is None or int(lit_tick) < rearm_tick:
                _unmeasured(t, "the re-armed opening front did not light (re-armed at tick %r, ProbeOpeningFront %r): no "
                               "fresh front to watch" % (rearm_tick, kv))
        guard0 = _r6_guard(t)
        try:   # the share's reads are burn_line_burned_share's to judge; their failure is not the front's
            ground, err = _r6_share_ground(t), None
        except ExpectationFailed as ex:
            ground, err = None, str(ex)
        share0 = _r6_burned_share(t, ground)
        tick0 = _r6_tick(t)
        start = t.bridge_call("rimworld/save_game", saveName=R6_SHARE_SAVE)
        _GEN["burn_share"] = {"ground": ground, "share0": share0, "start": start, "tick0": tick0, "error": err}
        h0 = _ten_hour(t)
        rows, shots, saved = [], [], None
        for i in range(R6_FRONT_HOURS):
            _wait(t, TEN_HOUR)
            h = _ten_hour(t)
            cells = _r6_fires(t)
            row = {"hour": h, "fires": len(cells), "cx": None, "cz": None}
            if cells:
                row["cx"] = sum(c[0] for c in cells) / float(len(cells))
                row["cz"] = sum(c[1] for c in cells) / float(len(cells))
                shots.append(_r6_shot(t, front_crop(cells), "burn_line_hour_%02d" % i))
                if i >= R6_FRONT_SAVE_HOUR and saved is None:
                    saved = t.bridge_call("rimworld/save_game", saveName="burn_line_walking")
            rows.append(row)
            if i == 1 and os.environ.get(PLANT_FRONT_OUT_ENV) == "1":
                _note(t, "PLANTED FAULT", "%s=1: the map is put out after the second capture" % PLANT_FRONT_OUT_ENV)
                _extinguish(t)
        guard1 = _r6_guard(t)
        if _live(t):
            _note(t, "front by the hour (captures at %d px/cell)" % R6_PLAY_PPC,
                  {"opening": kv, "startHour": h0, "rows": rows, "shots": shots, "save": saved})
            if h0 is None or any(r["hour"] is None for r in rows):
                _unmeasured(t, "glow_at gave no clock hour at a capture, so its hour cannot be asserted")
            for i, r in enumerate(rows):
                want = (h0 + i + 1) % 24
                if min(abs(r["hour"] - want), 24 - abs(r["hour"] - want)) > R6_HOUR_TOL:
                    _fail("capture %d read hour %.2f, expected %.2f" % (i, r["hour"], want))
            if not saved or not saved.get("success", True):
                _fail("no burn_line_walking save was made while the front walked: %r" % saved)
            ok, why = front_walks(rows)
            if not ok:
                _fail(why)
            dmg = _r6_guard_changes(guard0, guard1)
            if dmg:
                _fail("the watch changed the colony: %r" % dmg)
    if not share:
        return
    _independent(t)
    with _comp(t, "burn_line_burned_share"):
        st = _GEN.get("burn_share") or {}
        ground = st.get("ground")
        if _live(t):   # refuse before seven game days are spent on a read that cannot be judged
            if not ground:
                _unmeasured(t, "no open plantable ground read on the site: %s" % (st.get("error") or "terrain or fertility unread"))
            if st.get("share0") is None or st.get("tick0") is None:
                _unmeasured(t, "the start's burned share or clock was not read (share %r, tick %r)"
                            % (st.get("share0"), st.get("tick0")))
            if not isinstance(st.get("start"), dict) or not st["start"].get("success", True):
                _unmeasured(t, "no %s save was made at the start, so the wind-off control has no same seed: %r"
                            % (R6_SHARE_SAVE, st.get("start")))
        # day 1 is the hourly watch above; the day ends are counted from the start save's clock
        on_rest, on_shots = _r6_share_days(t, ground, "on", st.get("tick0"))
        on = [st.get("share0")] + on_rest
        _load_site_save(t, R6_SHARE_SAVE)
        _on_site(t)
        _set(t, {"windCarriesFireEnabled": False})
        try:
            off_rest, off_shots = _r6_share_days(t, ground, "off", _r6_tick(t))
        finally:
            _set(t, {"windCarriesFireEnabled": True})
        off = [st.get("share0")] + off_rest
        if _live(t):
            ok, why = burned_share_verdict(on, off)
            _note(t, "burned share of open plantable ground by day end (wind on, then the same start wind off)",
                  {"groundCells": ground, "days": R6_SHARE_DAYS, "limit": R6_SHARE_MOST, "on": on, "off": off,
                   "worstOn": max(v for v in on if v is not None) if any(v is not None for v in on) else None,
                   "casesRead": sum(1 for v in on + off if v is not None), "startSave": st.get("start"),
                   "captures": {"on": on_shots, "off": off_shots}, "verdict": why})
            if ok is None:
                _unmeasured(t, why)
            if ok is False:
                _fail(why)
    _burn_line_off_control(t)


PLANT_FRONT_OUT_ENV = "PYRE_PLANT_FRONT_OUT"   # planted state: the front goes out while it is watched
PLANT_BURNLINE_TOGGLE_IGNORED_ENV = "PYRE_PLANT_BURNLINE_TOGGLE_IGNORED"   # planted state: the toggle left on
# the other fire sources this control holds off, so that a fire after the window can only be the burn line's own relight
# (KeepTheBurnAlive). burnLineEnabled and fireClockEnabled are independent switches (MapComponent_BurnLine, MOD_OPTIONS_
# RETROFIT_1): visit 3's control switched off the burn line alone, the fire clock lit its fronts, and 161 fires read FAIL.
# furnaceThermalEnabled: SITE (visit 9, 2026-11-24): the site's two furnace-beasts set the grass they sleep in alight, which the
# control read as a burn line that relit (34 fires; off_control_source.py: the first fire one cell from a beast).
OFF_CONTROL_HOLDS = ("fireClockEnabled", "fireHawkSpreadEnabled", "furnaceThermalEnabled")
# HARNESS (visit 4, 2026-11-21): the quiet window plus a few watch intervals fits ONE reseed attempt (KeepAlive retries
# every StandingBurnRetryTicks 2500, the lawful-cell search takes 40 random tries), so a planted run whose one attempt
# found no cell read 0 fires and the control could not fail (visit 3). Four more retries; with the toggle off nothing else
# lights, so the longer window only makes the PASS stricter. Visit 4's probe (burnLineEnabled on, the other sources held
# off) read 1-2 burn-line fires at every sample from the window's end to 15000 ticks past it.
OFF_CONTROL_WAIT_TICKS = BURN_STAGED_WAIT_TICKS   # it played the 120,000-tick quiet window until visit 9
# The walk's off spells (gate, roster, R8 master) stage no quiet counter: each must play the whole quiet window plus the
# watch intervals and four reseed retries, or an ignored switch relights nothing in the spell and reads PASS (visit 8).
WALK_OFF_SPELL_TICKS = BURN_QUIET_TICKS + BURN_STAGED_WAIT_TICKS


def _burn_line_off_control(t):
    _independent(t)
    with _comp(t, "burn_line_off_control"):
        planted = os.environ.get(PLANT_BURNLINE_TOGGLE_IGNORED_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: burnLineEnabled is left on, as if the switch did nothing"
                  % PLANT_BURNLINE_TOGGLE_IGNORED_ENV)
        prior = dict((k, _live_setting(t, k)) for k in OFF_CONTROL_HOLDS) if _live(t) else {}
        _set(t, dict([("burnLineEnabled", planted)] + [(k, False) for k in OFF_CONTROL_HOLDS]))
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        try:
            _extinguish(t)
            _stage_quiet(t)
            _wait(t, OFF_CONTROL_WAIT_TICKS)
            n = len(_r6_fires(t))
        finally:
            _set(t, dict([("burnLineEnabled", True)] + [(k, str(v) == "True") for k, v in prior.items()]))
            t.bridge_call("jawa/weather_set", unlock=True)
        if _live(t):
            _note(t, "burnLineEnabled %s, fire clock, hawk spread and furnace-beast bed fire held off, weather Clear, map extinguished: "
                  "free-standing Fire after the window" % planted, n)
            if n:
                _fail("%d free-standing fires after the window with burnLineEnabled %s and every other fire source held "
                      "off: the burn line relit what was put out" % (n, planted))


@suite.chain("burn_line_walk")
@_teardown(fire=True)
def burn_line_walk(t):
    """The burn line's relight and the front's hourly watch, without the eight-day burned share (the burn_line chain runs all)."""
    _burn_line_present(t)
    with _wildlife_shield(t):
        _r6_burn_line(t, share=False)


@suite.chain("burn_line_off_control")
def burn_line_off_control_alone(t):
    """The burn line's off-control alone (its planted reading without the 24-hour walk; the burn_line chain runs it too)."""
    _burn_line_off_control(t)


def _r6_terrain_cells(t, rect):
    """{(x, z): terrain def} over `rect` from get_terrain_batch's run-length ops; {} offline."""
    r = t.bridge_call("jawa/get_terrain_batch", rects=rect)
    if not _live(t):
        return {}
    _ok(r, "get_terrain_batch(%s)" % rect)
    return _r6_ops_cells(r.get("ops"))


def _r6_ops_cells(ops):
    """Pure. Run-length ops ('Def:x,z,w,h;...', get_terrain_batch / get_roof_batch) -> {(x, z): def}."""
    cells = {}
    for op in str(ops or "").replace("\n", ";").split(";"):
        d, _, rr = op.partition(":")
        try:
            ox, oz, ow, oh = (int(v) for v in rr.split(","))
        except ValueError:
            continue
        for cx in range(ox, ox + ow):
            for cz in range(oz, oz + oh):
                cells[(cx, cz)] = d.strip()
    return cells


def is_standing_water(name):
    """A shore's water: any def named *Water* / *Marsh*. Not is_water_family: that also holds Mud and Riverbank (the ash
    sweep's radius), and a mud relic with no water beside it rings nothing (MEASURED 2026-11-20 visit 2: 0 water cells,
    the water assert passed on 372 mud cells)."""
    return bool(name) and ("Water" in name or "Marsh" in name)


def _r6_shore_ring(cells):
    """Pure. {(x, z): terrain} -> (standing-water cells, {land cell next to water: terrain})."""
    water = set(c for c, d in cells.items() if is_standing_water(d))
    ring = {}
    for (cx, cz) in water:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                n = (cx + dx, cz + dz)
                if n in cells and n not in water:
                    ring[n] = cells[n]
    return water, ring


def _r6_ash_run(t, weather, hours, settings):
    """From ashground_noon: `settings` flipped, `weather` locked, ProbeAsh depthSum gain each hour -> [gain]."""
    _load_site_save(t, "ashground_noon")
    _on_site(t)
    _set(t, settings)
    t.bridge_call("jawa/weather_set", weather=weather, lockWeather=True)
    a0 = _ash(t).get("depthSum")
    gains = []
    for _ in range(hours):
        _wait(t, TEN_HOUR)
        a = _ash(t).get("depthSum")
        gains.append(None if a is None or a0 is None else a - a0)
    t.bridge_call("jawa/weather_set", unlock=True)
    return gains


def _r6_ground_deep_ash(t):
    """sc_ash_ground (g4, g6, g7): water asserted on the site before the other reads (none: regenerate the fixture on the
    next seed, never a pass); a vanilla AridShrubland control map's shore read (no rich-soil ring); from ashground_noon the ash fall with
    ashfallAccumulationEnabled off banks no more than clear weather, and a clear half-day with ambientAshEnabled off banks
    none; at noon a play-zoom capture pair of ten ash-laden ember-grass cells, as they lie and after ClearAsh. The same-seed
    gate-off regeneration is removed (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, polish.md): sc_ash_ground
    left the test table (no bar needs it)."""
    _independent(t)
    with _comp(t, "ash_ground_water_asserted"):
        cells = _r6_terrain_cells(t, _whole(t))
        water, ring = _r6_shore_ring(cells)
        if _live(t):
            _note(t, "site water cells and shore ring size", {"water": len(water), "ring": len(ring)})
            if not water:
                _unmeasured(t, "the site rolled no standing water: regenerate the fixture on the next seed (the scene "
                               "never passes a map with none)")
    _independent(t)
    with _comp(t, "ash_ground_vanilla_shore"):
        ctl = _ten_control_map(t, "AridShrubland")
        try:
            cells = _r6_terrain_cells(t, "0,0,%d,%d" % (TEN_CONTROL_SIZE, TEN_CONTROL_SIZE))
            ash = _ash(t) if _live(t) else {}
        except ExpectationFailed:
            ash = {"unread": True}
        finally:
            _ten_control_map_drop(t, ctl)
        water, ring = _r6_shore_ring(cells)
        if _live(t):
            tally = {}
            for d in ring.values():
                tally[d] = tally.get(d, 0) + 1
            _note(t, "vanilla AridShrubland control: shore ring terrain, deep ash", {"ring": tally, "ash": ash,
                                                                                    "deepAsh": sum(1 for d in cells.values() if d == DEEP_ASH)})
            if not water:
                _unmeasured(t, "the vanilla control map rolled no water, so its shore cannot be read")
            if tally.get("RM_FE_Ground_SoilRich"):
                _fail("the vanilla control's shore carries RM_FE_Ground_SoilRich (%d cells)" % tally["RM_FE_Ground_SoilRich"])
            if ring and all(d in TEN_WATER_RING for d in ring.values()):
                _fail("every vanilla shore cell reads the Pyrelands ring terrain: %r" % tally)
            if any(d == DEEP_ASH for d in cells.values()):
                _fail("deep ash on the vanilla control map")
    _independent(t)
    with _comp(t, "ash_fall_accumulation_off"):
        _ten_noon_hour(t)
        t.bridge_call("rimworld/save_game", saveName="ashground_noon")
        clear = _r6_ash_run(t, "Clear", 4, {"ashfallAccumulationEnabled": True})
        off = _r6_ash_run(t, ASHFALL, 4, {"ashfallAccumulationEnabled": False})
        _set(t, {"ashfallAccumulationEnabled": True})
        if _live(t):
            _note(t, "ProbeAsh gain by hour: clear vs ash fall with accumulation off", {"clear": clear, "off": off})
            if None in clear or None in off:
                _unmeasured(t, "ProbeAsh unread at an hour: %r / %r" % (clear, off))
            if off[-1] > clear[-1] + R6_ASH_EPS:
                _fail("with ashfallAccumulationEnabled off the ash fall banked %.3f, clear weather %.3f" % (off[-1], clear[-1]))
    _independent(t)
    with _comp(t, "ambient_ash_off_half_day"):
        hours = R6_HALF_DAY // TEN_HOUR
        off = _r6_ash_run(t, "Clear", hours, {"ambientAshEnabled": False})
        _set(t, {"ambientAshEnabled": True})
        if _live(t):
            _note(t, "clear half-day with ambientAshEnabled off: ProbeAsh gain by hour", off)
            if None in off:
                _unmeasured(t, "ProbeAsh unread at an hour: %r" % off)
            if off[-1] > R6_ASH_EPS:
                _fail("with ambientAshEnabled off a clear half-day banked %.3f ash" % off[-1])
    _independent(t)
    with _comp(t, "ash_drawing_capture_pair"):
        _load_site_save(t, "ashground_noon")
        _on_site(t)
        _pad(t, R6_PAD_ASH_DRAW)
        x, z = t.anchor
        strip = (x - 5, z, 10, 1)
        _plants(t, "RM_FE_Plant_EmberGrass", strip)
        t.bridge_call("jawa/static_call", type=ASH_SAND, method="LayAsh", args="%s|%s" % (_rs(strip), WASH_DEPTH))
        h = _ten_noon_hour(t)
        depth = [(_ash(t, "%d,%d,1,1" % (x - 5 + i, z)).get("depthSum")) for i in range(10)]
        grass = _count(t, "RM_FE_Plant_EmberGrass", _rs(strip))
        lie = _r6_shot(t, (x - 7, z - 2, 14, 5), "ash_as_they_lie")
        _clear_ash(t)            # PyrelandsAsh.ClearAsh: the sand-grid depth of every cell
        cleared = (_ash(t, _rs(strip)).get("depthSum"))
        bare = _r6_shot(t, (x - 7, z - 2, 14, 5), "ash_cleared")
        if _live(t):
            _note(t, "capture pair for a judge (unlabelled at the sitting)",
                  {"hour": h, "depth": depth, "emberGrass": grass, "asTheyLie": lie, "cleared": bare,
                   "depthAfterClear": cleared})
            if grass < 10:
                _unmeasured(t, "only %d of the ten cells carry ember grass" % grass)
            if any(d is None or d <= 0 for d in depth):
                _fail("a cell of the ten reads no ash depth before the capture: %r" % depth)
            if cleared:
                _fail("ClearAsh left %.3f ash depth on the ten cells" % cleared)
            if not lie or not bare:
                _fail("the capture pair is incomplete: %r / %r" % (lie, bare))


def _r6_fresh_burn_bonus(t):
    """sc_burn_compounds (g14): three deep-ash pads (A fresh burn under a roof, kept dry; B fresh burn in the open; C old
    ash, never burned this run, in the open); vitals and pending incidents read before the seven-day wait; black rain
    over the open pads for half a day; ProbeCell on each while it rains (wet fresh above wet old above dry fresh), with
    freshBurnBonusEnabled off for one read (wet fresh then equals wet old); daily to day 7, the bonus gone; the guard at
    day 7 unchanged and no fire off the three pads."""
    _independent(t)
    with _comp(t, "burn_compounds_with_black_rain"):
        _pad(t, R6_PAD_COMPOUND)
        t.clear_area(size=TEST_SIZE)
        x, z = t.anchor
        pads = {"A": (x - 9, z - 2, 4, 4), "B": (x - 2, z - 2, 4, 4), "C": (x + 5, z - 2, 4, 4)}
        _firebreak(t, (x - 9, z - 2, 18, 4))
        for k, r in pads.items():
            t.bridge_call("jawa/set_terrain", x=r[0], z=r[1], terrainDef=DEEP_ASH, width=4, height=4, layer="top")
        t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % _rs(pads["A"]))
        for k in ("A", "B"):
            _plants(t, "RM_FE_Plant_EmberGrass", pads[k])
            _fire(t, pads[k])
        _wait(t, REGROW_BURN_TICKS)
        _extinguish(t)
        cell = dict((k, (r[0] + 1, r[1] + 1)) for k, r in pads.items())
        guard0 = _r6_guard(t)
        t.bridge_call("jawa/weather_set", weather="RM_FE_BlackRain", lockWeather=True)
        _wait(t, R6_HALF_DAY // 2)
        wet = dict((k, _probe(t, *c)) for k, c in cell.items())
        _set(t, {"freshBurnBonusEnabled": False})
        off = dict((k, _probe(t, *cell[k])) for k in ("B", "C"))
        _set(t, {"freshBurnBonusEnabled": True})
        _wait(t, R6_HALF_DAY // 2)
        t.bridge_call("jawa/weather_set", unlock=True)
        days = []
        for d in range(1, R6_COMPOUND_DAYS + 1):
            _wait(t, TEN_DAY - (R6_HALF_DAY if d == 1 else 0))
            days.append(dict((k, _probe(t, *c).get("bonus")) for k, c in cell.items()))
        guard7 = _r6_guard(t)
        fires = [c for c in _r6_fires(t) if not any(r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3]
                                                    for r in pads.values())]
        if _live(t):
            _note(t, "while black rain falls (about %.1f / %.1f / %.1f dry fresh / wet old / wet fresh)"
                  % (R6_DRY_FRESH, R6_WET_OLD, R6_WET_FRESH), {"wet": wet, "bonusOff": off})
            _note(t, "bonus by day to day %d; guard before / at day %d" % (R6_COMPOUND_DAYS, R6_COMPOUND_DAYS),
                  {"days": days, "before": guard0, "day7": guard7, "firesOffPads": fires[:10]})
            if wet["A"].get("watered") or not wet["B"].get("watered") or not wet["C"].get("watered"):
                _unmeasured(t, "the pads are not dry / wet as staged: %r" % dict((k, v.get("watered")) for k, v in wet.items()))
            if str(wet["C"].get("burnTick")) not in ("-1", "None") and float(wet["C"].get("bonus") or 0) > 0:
                _unmeasured(t, "the old-ash pad C still carries a fresh-burn bonus: %r" % wet["C"])
            fa, fb, fc = wet["A"]["fertility"], wet["B"]["fertility"], wet["C"]["fertility"]
            if not fb > fc > fa:
                _fail("not wet fresh > wet old > dry fresh while it rains: %.2f / %.2f / %.2f" % (fb, fc, fa))
            if abs(off["B"]["fertility"] - off["C"]["fertility"]) > 0.01:
                _fail("with freshBurnBonusEnabled off wet fresh %.2f differs from wet old %.2f"
                      % (off["B"]["fertility"], off["C"]["fertility"]))
            last = days[-1]
            if any(float(last[k] or 0) > 0.01 for k in ("A", "B")):
                _fail("the burn bonus is not gone by day %d: %r" % (R6_COMPOUND_DAYS, last))
            dmg = _r6_guard_changes(guard0, guard7)
            if dmg or fires:
                _fail("the seven-day wait changed the colony or lit fire off the pads: %r, %r" % (dmg, fires[:5]))
        t.bridge_call("jawa/set_roof_batch", ops="None:%s" % _rs(pads["A"]))


def weather_name(w):
    """jawa/weather_get's `weather` is a dict ({current, last, curWeatherAge, ...}); the def name in force is `current`.
    HARNESS (Pyrelands visit 3, 2026-11-21): the row compared the dict itself with "RM_FE_BlackRain" and failed on a black
    rain reading, and its "never Rain an hour later" half could not see Rain at all. Pure."""
    return w.get("current") if isinstance(w, dict) else w


PLANT_NO_RAIN_GATE_OFF_ENV = "PYRE_PLANT_NO_RAIN_GATE_OFF"   # planted state for the repaired row: the mechanics off


def _r6_forced_rain_roll(t):
    """Lock Rain (jawa/weather_set lockWeather: a GameCondition_ForceWeather whose weather IS Rain), then make
    WeatherDecider roll now, twice (jawa/weather_roll_next: StartNextWeather -> ChooseNextWeather, the method
    PyrelandsNoOrdinaryRain postfixes; the map re-rolls the same way every 4000 ticks while the forced weather differs
    from the current one). weather_set's own TransitionTo(Rain) bypasses the decider, so the verdict reads the ROLLS, not
    the weather right after the lock. Under a tutorial storyteller ChooseNextWeather returns Clear before it reads the
    forced weather (TutorSystem.TutorialMode && ClearWeatherAllowed; visit 1 rain_postfix.py met it on the quiet profile's
    Tutor), so the storyteller is Phoebe for the rolls only: no tick passes while it is swapped, so no incident can fire.
    Then an hour with the storyteller back. The prior lock (or none) is put back. -> the readings."""
    w0 = t.bridge_call("jawa/weather_get") or {}
    # weather_get's conditions[] names the def, not the forced weather: a lock in force is taken to hold the weather now
    prior = [weather_name(w0.get("weather")) for c in w0.get("conditions") or [] if c.get("def") == "WeatherController"][:1]
    teller = ((t.bridge_call("jawa/storyteller_swap") or {}).get("before") or {}).get("storytellerDef")
    out = {"before": w0.get("weather"), "priorLock": prior, "storyteller": teller}
    try:
        t.bridge_call("jawa/storyteller_swap", storytellerDef="Phoebe")
        lock = t.bridge_call("jawa/weather_set", weather="Rain", lockWeather=True) or {}
        rolls = [t.bridge_call("jawa/weather_roll_next") or {} for _ in range(2)]
        out.update({"lock": {"success": lock.get("success"), "after": lock.get("after"), "lockInForce": lock.get("lockInForce")},
                    "lockedTo": [r.get("lockedTo") for r in rolls],
                    "rolled": [(r.get("after") or {}).get("weather") for r in rolls]})
    finally:
        if teller:
            t.bridge_call("jawa/storyteller_swap", storytellerDef=teller)
    out["now"] = weather_name((t.bridge_call("jawa/weather_get") or {}).get("weather"))
    _wait(t, TEN_HOUR)
    out["hourLater"] = weather_name((t.bridge_call("jawa/weather_get") or {}).get("weather"))
    if prior and prior[0]:
        t.bridge_call("jawa/weather_set", weather=prior[0], lockWeather=True)
    else:
        t.bridge_call("jawa/weather_set", unlock=True)
    return out


def _r6_forced_rain_blind(t, run):
    """UNMEASURED when the reading cannot show the decider choosing under a forced Rain (the instrument, never the mod)."""
    if not run.get("storyteller"):
        _unmeasured(t, "the storyteller was not read, so it could not be swapped off a tutorial one and back: %r" % run)
    if not (run.get("lock") or {}).get("success") or not (run.get("lock") or {}).get("lockInForce"):
        _unmeasured(t, "the Rain lock was not registered: %r" % run.get("lock"))
    if any(lt != "Rain" for lt in run.get("lockedTo") or [None]):
        _unmeasured(t, "the decider's forced weather read %r at the rolls, not Rain" % run.get("lockedTo"))


def _r6_no_ordinary_rain(t):
    """sc_no_rain (g8): under a forced Rain (GameCondition_ForceWeather, jawa/weather_set lockWeather) the weather the
    decider gives the site is black rain, never Rain (_r6_forced_rain_roll). Control: the same roll on the same site with
    the Mod enabled master (pyrelandsEnabled) off gives Rain, so the lock does force the roll and the swap is
    PyrelandsNoOrdinaryRain's (RM_FireEcoKernel.RainBecomesBlackRain is gated on PyrelandsMechanicsGate.On). It replaces
    the vanilla TemperateForest control map, which the scratch world had no tile for
    (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN)."""
    _independent(t)
    with _comp(t, "forced_rain_becomes_black_rain"):
        planted = os.environ.get(PLANT_NO_RAIN_GATE_OFF_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: pyrelandsEnabled off for this row, so the decider's ordinary Rain stands"
                  % PLANT_NO_RAIN_GATE_OFF_ENV)
            _set(t, {"pyrelandsEnabled": False})
        try:
            site = _r6_forced_rain_roll(t)
        finally:
            if planted:
                _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            _note(t, "forced Rain on the site, rolled by WeatherDecider", site)
            _r6_forced_rain_blind(t, site)
            if "Rain" in (site.get("rolled") or []) + [site.get("now"), site.get("hourLater")]:
                _fail("under a forced-Rain condition the site's weather is Rain: %r" % site)
            if any(w != BLACKRAIN for w in site.get("rolled") or [None]) or site.get("now") != BLACKRAIN:
                _fail("under a forced-Rain condition the decider gave the site %r (now %r), not %s"
                      % (site.get("rolled"), site.get("now"), BLACKRAIN))
    _independent(t)
    with _comp(t, "forced_rain_gate_off_control"):
        _set(t, {"pyrelandsEnabled": False})
        try:
            gate = _ten_gate_on(t)
            ctl = _r6_forced_rain_roll(t)
        finally:
            _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            _note(t, "forced Rain on the site with pyrelandsEnabled off (the gate-off control)", dict(ctl, gate=gate))
            if gate is not False:
                _unmeasured(t, "pyrelandsEnabled False left PyrelandsMechanicsGate.get_On %r" % gate)
            _r6_forced_rain_blind(t, ctl)
            if any(w != "Rain" for w in ctl.get("rolled") or [None]):
                _fail("with the mechanics off the forced-Rain roll gave %r, not Rain: the lock does not force the roll"
                      % ctl.get("rolled"))


PLANT_OFFBURN_TOGGLE_IGNORED_ENV = "PYRE_PLANT_OFFBURN_TOGGLE_IGNORED"   # planted state for scorchfruit_off_burn_bears_none


def _r6_scorchfruit_fire_born(t):
    """sc_scorchfruit (g4): a second fresh burn of the same ground with scorchFruitEnabled off reads 0 scorch-fruit during
    and after it."""
    _independent(t)
    with _comp(t, "scorchfruit_off_burn_bears_none"):
        _pad(t, PAD_FIRE_BORN)
        x, z = t.anchor
        rect = (x - 6, z + TEST_SIZE // 2 + 6, 12, 12)
        _clear_scorchfruit(t)
        planted = os.environ.get(PLANT_OFFBURN_TOGGLE_IGNORED_ENV) == "1"
        if planted:
            _note(t, "PLANTED FAULT", "%s=1: scorchFruitEnabled is left on, as if the switch did nothing"
                  % PLANT_OFFBURN_TOGGLE_IGNORED_ENV)
        _set(t, {"scorchFruitEnabled": planted})
        _open_ground(t, rect, margin=4)   # SITE (visit 6): this rect lies outside the cleared pad, on whatever the map holds
        _firebreak(t, rect)
        _soil(t, rect)
        _plants(t, "RM_FE_Plant_EmberGrass", rect)
        _fire(t, rect)
        _wait(t, 3000)
        during = _count(t, FRUIT_PLANT, _rs(rect))
        _wait(t, 8600)
        _extinguish(t)
        after = _count(t, FRUIT_PLANT, _rs(rect))
        _set(t, {"scorchFruitEnabled": True})
        if _live(t):
            _note(t, "scorch-fruit on a burn with scorchFruitEnabled off: during / after", [during, after])
            if during or after:
                _fail("scorchFruitEnabled off, yet the burn bore %d / %d scorch-fruit" % (during, after))
        t.screenshot(rect=rect)


def _r6_heat_dome(t):
    """sc_heat_dome (g9): a fresh ashwallow struck once with Burn; at +60 on screen at play zoom ProbeDome's bodyGraphic
    reads the race's domeTexPath (domeArt installed) and a capture is taken; once surfaced (after DOME_HOLD_TICKS) the
    bodyGraphic reads the standing body, differs from the dome path, and a second capture is taken, for a judge."""
    _independent(t)
    with _comp(t, "dome_body_graphic_pair"):
        _set(t, {"burrowOnFireEnabled": True, "burrowDomeOnHeatHit": True})
        x, z = PAD_DOME[0] + 4, PAD_DOME[1] + 4
        g = _spawn_wild(t, "RM_Ashwallow", x, z)
        _wait(t, 30)
        fires = _count(t, "Fire", "%d,%d,12,12" % (x - 6, z - 6))
        t.bridge_call("jawa/damage", damageDef="Burn", amount=2.0, thingId=g)
        _wait(t, 60)
        domed_shot = _r6_shot(t, (x - 3, z - 3, 6, 6), "ashwallow_domed")
        domed = _dome_probe(t, g)
        _wait(t, DOME_HOLD_TICKS + 300)
        up_shot = _r6_shot(t, (x - 3, z - 3, 6, 6), "ashwallow_standing")
        up = _dome_probe(t, g)
        if _live(t):
            _note(t, "bodyGraphic at +60 and after surfacing, with the captures",
                  {"domed": domed, "standing": up, "shots": [domed_shot, up_shot]})
            if fires:
                _unmeasured(t, "%d fires near the dome pad before the hit" % fires)
            if domed.get("domeArt") != "True":
                _fail("no dome art installed at %r" % domed.get("domeTexPath"))
            if domed.get("burrowed") != "True" or domed.get("bodyGraphic") != domed.get("domeTexPath"):
                _fail("at +60 the body draws %r, not the domeTexPath %r" % (domed.get("bodyGraphic"), domed.get("domeTexPath")))
            if up.get("burrowed") == "True" or not up.get("bodyGraphic") or up.get("bodyGraphic") == domed.get("domeTexPath"):
                _fail("after the hold the body still draws the dome or nothing: %r" % up)
            if not domed_shot or not up_shot:
                _fail("the capture pair is incomplete: %r / %r" % (domed_shot, up_shot))


def _r6_floats(v):
    return [float(m) for m in re.findall(r"-?\d+(?:\.\d+)?", str(v))]


def giant_margin(sizes, beast="RM_FurnaceBeast", ratio=2.0):
    """Pure. sizes {kind: (bodySize, adult drawSize)} -> (ok, why): the beast's body size at least `ratio` times every other
    kind's and its adult draw size above each of theirs."""
    if beast not in sizes:
        return False, "%s not among the sizes read" % beast
    bs, draw = sizes[beast]
    low = sorted(k for k, (b, _) in sizes.items() if k != beast and bs < ratio * b)
    if low:
        return False, "%s body size %.2f is under %.0fx of %r" % (beast, bs, ratio, low)
    big = sorted(k for k, (_, d) in sizes.items() if k != beast and draw <= d)
    if big:
        return False, "%s adult draw size %.2f is not above %r" % (beast, draw, big)
    return True, "body size %.2f over %d kinds, adult draw %.2f above each" % (bs, len(sizes) - 1, draw)


def _r6_ullai_and_giant(t):
    """sc_furnace_giant (g10): furnaceBeastGiant on at load; every resolved RM_Pyrelands roster kind (biome_probe, the
    patch-added cast included, at least R6_ROSTER_MIN kinds or the read is blind) read live: race baseBodySize and the
    last life stage's drawSize; giant_margin over every other kind (relational only: no bar pins a size, owner 2026-11-16,
    bar_rule). The classic-restore control is removed (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, polish.md):
    the giant switch's off state is a Mod Settings check (inv_settings_gate, T_SETTINGS_SWEEP_OFFLINE), not the giant bar."""
    _independent(t)
    with _comp(t, "giant_margin_over_roster"):
        on = _live_setting(t, "furnaceBeastGiant")
        probe = t.bridge_call("jawa/biome_probe", biomes="RM_Pyrelands", animals=True, plants=False, topN=200)
        sizes, why = {}, None
        if _live(t):
            roster, why = biome_probe_animals(probe, "RM_Pyrelands")
            if roster is None:
                _unmeasured(t, why)
            if len(roster) < R6_ROSTER_MIN:
                _unmeasured(t, "biome_probe resolved %d roster kinds, under the %d native kinds: a blind read"
                            % (len(roster), R6_ROSTER_MIN))
            kinds = _get_defs(t, ";".join("PawnKindDef/%s" % k for k in sorted(roster)), "race", deep=False)
            stages = _get_defs(t, ";".join("PawnKindDef/%s" % k for k in sorted(roster)), "lifeStages")
            races = dict((k, str((kinds.get(k) or {}).get("race") or k).split("/")[-1].strip()) for k in roster)
            bodies = _get_defs(t, ";".join("ThingDef/%s" % r for r in sorted(set(races.values()))), "race")
            for k in roster:
                b = _r6_floats(((bodies.get(races[k]) or {}).get("race") or {}).get("baseBodySize")
                               if isinstance((bodies.get(races[k]) or {}).get("race"), dict) else None)
                ls = (stages.get(k) or {}).get("lifeStages") or []
                draws = [(_r6_floats((s.get("bodyGraphicData") or {}).get("drawSize")) or [None])[0]
                         for s in ls if isinstance(s, dict)]
                sizes[k] = (b[0] if b else None, draws[-1] if draws else None, draws)
            _note(t, "live roster sizes (bodySize, adult drawSize, by life stage)", {"giantSwitch": on, "sizes": sizes})
            if str(on).lower() != "true":
                _unmeasured(t, "furnaceBeastGiant reads %r at load" % on)
            blind = sorted(k for k, v in sizes.items() if v[0] is None or v[1] is None)
            if blind:
                _unmeasured(t, "body or draw size unread for %r" % blind)
            ok, why = giant_margin(dict((k, (v[0], v[1])) for k, v in sizes.items()))
            if not ok:
                _fail(why)



FOIL_BIOME = "RM_Pyrelands"
FOIL_DENSITY = 1.0   # the value Map Designer caps plantDensity to (RM_PyrelandsDensityEnforcer.cs header, bisected 2026-09-18)
# The foil must read cover at least this far below the site. Danger guarded: regeneration noise read as the density
# enforcer's effect. Evidence (visit 6, 2026-11-22, ArchSmall): the same seed regenerated at the site's own density read
# 0.0002 below the site and passed a strictly-below check; the shipped 1.0 foil read 0.494 below. 0.05 is 250 times that
# noise and a tenth of the real margin.
FOIL_MIN_MARGIN = 0.05
# planted state for plant_density_one_control_map: the foil is generated at the site's own enforced plantDensity, so it
# regenerates the site itself (same seed, same density) and its cover share cannot read below the site's: the part must
# read FAIL. Its reading beside the row also shows whether the same seed reproduces the site.
PLANT_FOIL_AT_SITE_ENV = "PYRE_PLANT_FOIL_AT_SITE_DENSITY"


def foil_override(density):
    return "BiomeDef/%s.plantDensity=%s" % (FOIL_BIOME, density)


def density_foil_verdict(gc, r, fert, density=FOIL_DENSITY):
    """Pure. sc_grass_regreens' plantDensity-1.0 control. gc: grass_cover's site census record (_GEN["grass_census"]);
    r: the jawa/map_seed_foil reply; fert: {terrainDef: {"fertility": f}} for the foil's terrain defs ->
    (ok, why, reading). ok is True when the foil's cover share is strictly below the site's (the bar: the enforced
    map is thicker than the same seed at plantDensity 1.0), False when it is not, None when the read cannot decide:
    no site census, a failed or blind foil call, a foil that is not the site's seed, tile biome or generator, an
    override not held through generation or not restored, a tick or map left behind on the site."""
    reading = {"site": None, "foil": None}
    if not isinstance(gc, dict) or not isinstance(gc.get("ratio"), (int, float)):
        return None, "no site cover census from grass_cover earlier in this run (%r)" % (gc,), reading
    reading["site"] = {"ratio": gc["ratio"], "covered": gc.get("covered"), "plantable": gc.get("plantable"),
                       "plantDensity": gc.get("plantDensity")}
    if not isinstance(r, dict) or r.get("success") is not True:
        return None, "the foil call failed or the tool is absent: %s" % str(r)[:300], reading
    foil, site = r.get("foil"), r.get("site") or {}
    if not isinstance(foil, dict):
        return None, "the foil reply has no foil record: %s" % str(r)[:300], reading
    if foil.get("seedEqual") is not True or foil.get("tileHash") != site.get("tileHash"):
        return None, "the foil is not the site's seed: tileHash %r vs site %r" % (foil.get("tileHash"),
                                                                                site.get("tileHash")), reading
    if foil.get("biome") != FOIL_BIOME or site.get("biome") != FOIL_BIOME:
        return None, "the foil or the site is not %s: %r / %r" % (FOIL_BIOME, foil.get("biome"), site.get("biome")), reading
    if foil.get("generatorDef") != site.get("generatorDef") or (foil.get("sizeX"), foil.get("sizeZ")) != (
            site.get("sizeX"), site.get("sizeZ")):
        return None, "the foil's generator or size differs from the site's: %r" % ({"foil": [foil.get(k) for k in (
            "generatorDef", "sizeX", "sizeZ")], "site": [site.get(k) for k in ("generatorDef", "sizeX", "sizeZ")]},), reading
    ovs = [o for o in (r.get("overrides") or []) if isinstance(o, dict) and o.get("target") == "BiomeDef/" + FOIL_BIOME
           and o.get("field") == "plantDensity"]
    if len(ovs) != 1:
        return None, "the reply does not show the plantDensity override: %r" % (r.get("overrides"),), reading
    o = ovs[0]
    if not isinstance(o.get("heldAfterGeneration"), (int, float)) or abs(o["heldAfterGeneration"] - density) > 1e-6:
        return None, "plantDensity was not held at %s through generation: read %r after it" % (
            density, o.get("heldAfterGeneration")), reading
    if o.get("restored") != o.get("before") or o.get("before") != gc.get("plantDensity"):
        return None, "plantDensity not put back, or not the census's value: before %r, restored %r, census %r" % (
            o.get("before"), o.get("restored"), gc.get("plantDensity")), reading
    if r.get("mapCountAfter") != r.get("mapCountBefore") or r.get("currentMapRestored") is not True \
            or r.get("ticksAfter") != r.get("ticksBefore"):
        return None, "the site was touched: maps %r -> %r, current restored %r, ticks %r -> %r" % (
            r.get("mapCountBefore"), r.get("mapCountAfter"), r.get("currentMapRestored"), r.get("ticksBefore"),
            r.get("ticksAfter")), reading
    per, terr = foil.get("perDef"), foil.get("terrain")
    if not isinstance(per, dict) or not isinstance(terr, dict) or not terr or sum(per.values()) != foil.get("countMatched"):
        return None, "the foil census is unreadable or does not add up: countMatched %r, perDef %r" % (
            foil.get("countMatched"), str(per)[:200]), reading
    if sum(terr.values()) + (foil.get("terrainNull") or 0) != foil.get("cells"):
        return None, "the foil terrain read %r of %r cells" % (sum(terr.values()), foil.get("cells")), reading
    blind = sorted(d for d in terr if not isinstance(((fert or {}).get(d) or {}).get("fertility"), (int, float)))
    if blind:
        return None, "fertility unread for the foil's terrain %r" % blind, reading
    covered, plantable, ratio = cover_ratio(per, terr, fert, foil.get("built"))
    reading["foil"] = {"ratio": ratio, "covered": covered, "plantable": plantable, "plantDensity": density,
                       "seed": foil.get("seed"), "pawnsToWorld": foil.get("pawnsToWorld")}
    if ratio is None:
        return None, "the foil has no plantable cell (%r)" % plantable, reading
    reading["margin"] = gc["ratio"] - ratio
    if gc["ratio"] - ratio >= FOIL_MIN_MARGIN:
        return True, "foil cover %.3f (%d/%d) below site %.3f by %.3f (>= %.2f) at plantDensity %r" % (
            ratio, covered, plantable, gc["ratio"], gc["ratio"] - ratio, FOIL_MIN_MARGIN, gc.get("plantDensity")), reading
    return False, "the plantDensity-%s foil reads cover %.3f (%d/%d), not %.2f below the enforced site's %.3f: the " \
                  "density enforcer's map is not clearly thicker than the same seed at %s" % (
                      density, ratio, covered, plantable, FOIL_MIN_MARGIN, gc["ratio"], density), reading

def _r6_embergrass_regrow(t):
    """sc_grass_regreens (g15): grass_cover's census ran with no sow, spawn or set_terrain call before it (the script's own
    call log, _r6_log_calls: _GEN["grass_census"]["mutationsBefore"] empty), on at least 0.85 of open plantable cells, and
    the live RM_Pyrelands plantDensity was read at the census; then the same-seed, same-tile foil generated with
    plantDensity held at 1.0 (jawa/map_seed_foil, one main-thread call, dropped before it returns) reads a lower cover
    share by the same census (density_foil_verdict)."""
    _independent(t)
    with _comp(t, "grass_census_first"):
        gc = _GEN.get("grass_census")
        if _live(t):
            _note(t, "grass_cover census record", gc)
            if gc is None:
                _unmeasured(t, "grass_cover did not run earlier in this run, so no census-first record exists")
            if gc.get("mutationsBefore"):
                _fail("the grass census ran after %d mutating calls: %r" % (len(gc["mutationsBefore"]),
                                                                              sorted(set(gc["mutationsBefore"]))))
            if not isinstance(gc.get("plantDensity"), (int, float)):
                _fail("the live RM_Pyrelands plantDensity was not read at the census: %r" % gc.get("plantDensity"))
            if gc.get("ratio") is None or gc["ratio"] < 0.85:
                _fail("the census read plants on %r of open plantable cells (< 0.85)" % gc.get("ratio"))
    _independent(t)
    with _comp(t, "plant_density_one_control_map"):
        gc = _GEN.get("grass_census")
        density = FOIL_DENSITY
        if os.environ.get(PLANT_FOIL_AT_SITE_ENV) == "1" and isinstance((gc or {}).get("plantDensity"), (int, float)):
            density = gc["plantDensity"]   # planted state: the foil at the site's own density
            _note(t, "PLANTED FAULT: %s=1, the foil generated at the site's plantDensity %r" % (PLANT_FOIL_AT_SITE_ENV,
                                                                                            density), None)
        r = t.bridge_call("jawa/map_seed_foil", overrides=foil_override(density), censusGroup="Plant",
                          builtGroup="BuildingArtificial")
        if _live(t):
            terr = (((r or {}).get("foil") or {}).get("terrain")) if isinstance(r, dict) else None
            fert = (_get_defs(t, ";".join("TerrainDef/%s" % d for d in sorted(terr)), "fertility", deep=False)
                    if isinstance(terr, dict) and terr else {})
            ok, why, reading = density_foil_verdict(gc, r, fert, density)
            _note(t, "plantDensity-1.0 same-seed foil against the enforced site", reading)
            if ok is None:
                _unmeasured(t, why)
            if not ok:
                _fail(why)


def _r6_beds_lit(t):
    """Furnace-beasts whose own cell holds fire now (ProbeSleep fireOnCell) -> (lit count, beasts read)."""
    r = t.bridge_call("jawa/list_pawns", limit=1000)
    ids = [p.get("id") for p in ((r or {}).get("pawns") or []) if p.get("kindDef") == "RM_FurnaceBeast" and not p.get("dead")]
    lit = 0
    for pid in ids:
        kv = parse_kv(_ten_static(t, FURNACE_BED, "ProbeSleep", pid) or "")
        lit += kv.get("fireOnCell") == "True"
    return lit, len(ids)


R8_MASTER_HOURS = WALK_OFF_SPELL_TICKS // TEN_HOUR + 1   # the standing burn relights only after two quiet days
PLANT_MASTER_ENV = "PYRE_PLANT_MASTER"   # planted states for walk_master_off_then_on: "left_on" or "left_off"


def _r6_master_spell(t, on):
    """R8_MASTER_HOURS with pyrelandsEnabled `on`: hourly fires, bed fires and ProbeAsh depthSum, and the burn history. The on
    spell ends four hours after its first fire. HARNESS (visit 8, tier rehearsal): one day on cannot hold the relight
    (StandingBurnQuietTicks is two days), and a day's net ash is all decay (272 -> 50 with no fire)."""
    _set(t, {"pyrelandsEnabled": on})
    ash, fires, beds = [_ash(t).get("depthSum")], [], []
    for h in range(R8_MASTER_HOURS + (5 if on else 0)):
        if h >= R8_MASTER_HOURS and not any(fires):
            break   # nothing relit in the window: no ash to wait for
        _wait(t, TEN_HOUR)
        fires.append(len(_r6_fires(t)))
        beds.append(_r6_beds_lit(t)[0])
        ash.append(_ash(t).get("depthSum"))
        if on and _live(t) and sum(1 for f in fires if f) >= 5:
            break
    hist = _ten_static(t, BURN_LINE, "ProbeBurnHistory", "0")
    return {"fires": fires, "beds": beds, "ash": ash, "history": hist}


def master_spells_verdict(off, on, eps=R6_ASH_EPS):
    """walk_master_off_then_on over the two spells of _r6_master_spell -> (ok, why); ok None is undecided. Pure. Off: no fire,
    no bed fire and no hour in which the ash rises. On: a front, and an hour in which the ash rises. An hour's rise, never a
    net: the ash decays by more each hour than a young front lays in a day."""
    if None in off["ash"] or None in on["ash"] or not off["fires"] or not on["fires"]:
        return None, "an ash or fire read is missing"
    rise = [max(b - a for a, b in zip(x["ash"], x["ash"][1:])) for x in (off, on)]
    if any(off["fires"]) or any(off["beds"]):
        return False, "with pyrelandsEnabled off: fires %r, bed fires %r" % (off["fires"], off["beds"])
    if rise[0] > eps:
        return False, "with pyrelandsEnabled off the ash rose %.3f in an hour" % rise[0]
    if not any(on["fires"]):
        return False, "back on, no front walked over %d hours" % len(on["fires"])
    if rise[1] <= eps:
        return False, "back on, no ash was laid in any hour: the best hour read %.3f" % rise[1]
    return True, "off: nothing over %d h; on: the first fire in hour %d, the best hour's ash +%.3f" % (
        len(off["fires"]), 1 + next(i for i, f in enumerate(on["fires"]) if f), rise[1])


PLANT_BED_MASTER_ENV = "PYRE_PLANT_BED_MASTER"   # planted states for walk_master_bed_fire_resumes: "left_off" or "left_on"
R8_PAD_WALK_BED = (95, 225)    # the walk's own bed pad: free of every other pad (nearest PAD_VENOM and TEN_PAD_GRASS, 65 cells)


def walk_bed_resume_verdict(off, on, step=SLEEP_POLL_TICKS, grace=SLEEP_GRACE_TICKS,
                            off_roll=SLEEP_CONTROL_ROLL_TICKS, fail_roll=SLEEP_FAIL_ROLL_TICKS):
    """walk_master_bed_fire_resumes over one sleeper's polls (ProbeSleep fields plus 'fire', the Fire count within 2 cells),
    master off then on -> (verdict, why, spans), verdict 'PASS', 'FAIL' or None (not decided). Pure. Restarts of sleep pay
    the grace again; the span is counted here and not by restingTicks, which the master off stops. Off: any fire or sleep
    light FAILS, and off_roll ticks asleep on grass past the grace are owed. On: the sleep roll's own record with a Fire by
    the next poll PASSES; fail_roll ticks past the grace with no light FAIL."""
    def rolled(polls):
        tot, run = 0, 0
        for prev, cur in zip(polls, polls[1:]):
            ok = (prev.get("awake") == "False" and cur.get("awake") == "False" and prev.get("cell") == cur.get("cell")
                  and prev.get("flammablePlant") == "True")
            run = run + step if ok else 0
            tot += step if run > grace else 0
        return tot

    def lit(polls):
        return next((i for i, p in enumerate(polls) if _kv_int(p.get("litAfterTicks")) >= 0), None)
    first = lit(on)
    spans = {"offRolled": rolled(off), "onRolled": rolled(on[:first + 1] if first is not None else on), "onLitPoll": first}
    if lit(off) is not None or any(p.get("fire", 0) for p in off):
        return "FAIL", "master off: the bed was alight (%r)" % next(
            p for p in off if p.get("fire", 0) or _kv_int(p.get("litAfterTicks")) >= 0), spans
    if spans["offRolled"] < off_roll:
        return None, "master off: slept %d of %d ticks on grass past the grace" % (spans["offRolled"], off_roll), spans
    if first is not None:
        seen = [p.get("fire", 0) for p in on[first:first + 2]]
        if any(seen):
            return "PASS", "master on: the bed caught after %s ticks asleep; off, %d ticks and no fire" % (
                on[first].get("litAfterTicks"), spans["offRolled"]), spans
        if len(seen) < 2:
            return None, "master on: lit, fire not yet read", spans
        return "FAIL", "master on: the sleep roll lit but no Fire stood by the next poll", spans
    if spans["onRolled"] >= fail_roll:
        return "FAIL", "master back on: %d ticks asleep on grass past the grace and the bed never caught" % spans["onRolled"], spans
    return None, "master on: slept %d of %d ticks on grass past the grace" % (spans["onRolled"], fail_roll), spans


def _walk_bed_fire_resumes(t):
    """SITE repair (visit 8, 2026-11-23): the part read whichever furnace-beast slept on grass over the on-day, and none did
    in two full-list walks (visit 5), so it was UNMEASURED by design. Now one wild beast is laid on a 5x5 of ember grass on a
    concrete pad: master off first (walk_bed_resume_verdict's control span, no fire), then on (the sleep roll lights it).
    Planted: PYRE_PLANT_BED_MASTER=left_off|left_on, a master that does not resume / does not stop; each must FAIL."""
    plant = os.environ.get(PLANT_BED_MASTER_ENV) or ""
    if plant:
        _note(t, "PLANTED FAULT", "%s=%s" % (PLANT_BED_MASTER_ENV, plant))
    _extinguish(t)
    _pad(t, R8_PAD_WALK_BED)
    t.clear_area(size=TEST_SIZE)
    x, z = t.anchor
    pad, plot = (x - 6, z - 6, 13, 13), (x - 2, z - 2, 5, 5)
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/set_terrain", x=pad[0], z=pad[1], terrainDef=FIREBREAK, width=pad[2], height=pad[3], layer="top")
    t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % _rs(pad))
    _soil(t, plot)
    _plants(t, "RM_FE_Plant_EmberGrass", plot)
    _set(t, {"pyrelandsEnabled": plant == "left_on"})   # furnaceThermalEnabled stands at its shipped on
    pid = _spawn_wild(t, "RM_FurnaceBeast", x, z)
    polls, orders = {"off": [], "on": []}, []

    def lay_down():
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=0.05)
        r = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="LayDown", targetAX=x, targetAZ=z, waitTicks=0)
        orders.append(dict((f, (r or {}).get(f)) for f in ("success", "accepted", "afterJobDef", "message")))

    def phase(name):
        lay_down()
        asked = 1
        for i in range(SLEEP_WAIT_TICKS // SLEEP_POLL_TICKS):
            _wait(t, SLEEP_POLL_TICKS)
            if not _live(t):
                return
            kv = parse_kv(_ten_static(t, FURNACE_BED, "ProbeSleep", pid) or "")
            c = xz_of(kv.get("cell"))
            if kv.get("spawned") != "true" or c is None:
                _unmeasured(t, "the staged furnace-beast is not on the map: %r" % kv)
            kv["fire"] = _count(t, "Fire", "%d,%d,5,5" % (c[0] - 2, c[1] - 2)) or 0
            kv["tick"] = (i + 1) * SLEEP_POLL_TICKS
            polls[name].append(kv)
            verdict, _why, spans = walk_bed_resume_verdict(polls["off"], polls["on"])
            if verdict or (name == "off" and spans["offRolled"] >= SLEEP_CONTROL_ROLL_TICKS):
                return
            off_bed = kv.get("awake") != "False" and kv.get("job") != "LayDown" or kv.get("flammablePlant") != "True"
            if off_bed and _kv_int(kv.get("litAfterTicks")) < 0 and not kv["fire"] and asked <= SLEEP_REORDERS:
                _plants(t, "RM_FE_Plant_EmberGrass", plot)
                lay_down()
                asked += 1
    try:
        phase("off")
        _set(t, {"pyrelandsEnabled": plant != "left_off"})
        phase("on")
    finally:
        _set(t, {"pyrelandsEnabled": True})
    verdict, why, spans = walk_bed_resume_verdict(polls["off"], polls["on"])
    if _live(t):
        _note(t, "bed fire, master off then on: spans, orders, polls (tick, awake, job, cell, plant, litAfterTicks, fire)",
              {"spans": spans, "orders": orders, "why": why,
               "polls": dict((k, [(p.get("tick"), p.get("awake"), p.get("job"), p.get("cell"), p.get("plant"),
                                   p.get("litAfterTicks"), p.get("fire")) for p in v]) for k, v in polls.items())})
    t.screenshot(rect=(pad[0], pad[1], pad[2], pad[3]))
    if _live(t):
        if verdict == "FAIL":
            _fail(why)
        if verdict != "PASS":
            _unmeasured(t, why)


def _walk_bed_part(t):
    walk = os.environ.get("PYRE_WALK") == "1"
    _independent(t)
    with _comp(t, "walk_master_bed_fire_resumes"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_master_bed_fire_resumes")
        _walk_bed_fire_resumes(t)


def _r6_walk_season(t):
    """sc_walk (g4; PYRE_WALK=1 only): the Mod enabled master (pyrelandsEnabled) off for the standing burn's relight window, the map
    extinguished first: no fire, no ash laid (ProbeAsh), no bed fire (ProbeSleep fireOnCell on every furnace-beast); then on:
    the front walks again and ash is laid (master_spells_verdict). The bed fire's resumption has its own staged part
    (_walk_bed_fire_resumes). Planted: PYRE_PLANT_MASTER=left_on|left_off, a master that does not stop / does not resume."""
    walk = os.environ.get("PYRE_WALK") == "1"
    _independent(t)
    with _comp(t, "walk_master_off_then_on"):
        if not walk:
            _unmeasured(t, "the walk parts run only with PYRE_WALK=1 (full list, Stage 6)")
        _walk_one(t, "walk_master_off_then_on")
        plant = os.environ.get(PLANT_MASTER_ENV) or ""
        if plant:
            _note(t, "PLANTED FAULT", "%s=%s" % (PLANT_MASTER_ENV, plant))
        _extinguish(t)
        off = _r6_master_spell(t, plant == "left_on")
        on = _r6_master_spell(t, plant != "left_off")
        _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            ok, why = master_spells_verdict(off, on)
            _note(t, "pyrelandsEnabled off, then on: hourly fires, bed fires, ash depthSum", {"off": off, "on": on, "why": why})
            if ok is None:
                _unmeasured(t, why)
            if not ok:
                _fail(why)


# ---- new chains ----

def _r6_tick_on(t, ctl, n):
    """Advance `n` ticks and keep the control map `ctl` current (_wait would hop back to the site)."""
    if not _live(t):
        return
    t.wait_ticks(n)
    t.bridge_call("jawa/set_current_map", mapId=ctl[0])


def _r6_temp(t, xz):
    r = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % tuple(xz)) or {}
    return r.get("temperature", r.get("temp")), r.get("outdoorTemp")


def _r6_stack(t, defName):
    return sum(int(r.get("stackCount") or 1) for r in _things(t, defName, limit=200))


@suite.chain("furnace_hide_bank")
@_teardown(fire=True)
def furnace_hide_bank(t):
    """Scene sc_furnace_hide_bank (g1). On a vanilla Tundra (else IceSheet) map below 0 C outdoors: a furnace-beast corpse
    butchered at a ButcherSpot by a colonist (ButcherCorpseFlesh, DoBillsButcherFlesh) yields RM_FurnaceHide; two twin
    closed 5x5 rooms, walls only (no thing with CompHeatPusher, CompRefuelable or CompPowerTrader), within 1 C; the bank
    is placed in room A with build_batch and its costList's 60 hide is set aside out of play (split_stack: the script
    places it, no colonist hauls); its def carries no fuel or power comp; both rooms read hourly for 12 h: A at least
    R6_BANK_MARGIN above B from hour 6, never above R6_BANK_CEILING. Live half: scenes.json live_command (UNRUN here)."""
    _pad(t, PAD_PROBE)
    with _comp(t, "furnace_hide_bank_warms_a_room"):
        ctl = None
        for biome in ("Tundra", "IceSheet"):
            ctl = _ten_control_map(t, biome)
            if not _live(t):
                break
            out = _r6_temp(t, (10, 10))[1]
            if isinstance(out, (int, float)) and out < 0:
                break
            _ten_control_map_drop(t, ctl)
            ctl = None
        if _live(t) and ctl is None:
            _unmeasured(t, "no Tundra or IceSheet control map read below 0 C outdoors")
        try:
            cx = cz = TEN_CONTROL_SIZE // 2
            rooms = {"A": (cx - 8, cz - 3, 7, 7), "B": (cx + 1, cz - 3, 7, 7)}       # 5x5 inside, walls only
            for r in rooms.values():
                t.bridge_call("jawa/make_empty_room", rect=_rs(r), stuffDef="Steel", doorDef="Wall", floorDef="Concrete",
                              roofDef="RoofConstructed")
            inside = dict((k, (r[0] + 3, r[1] + 3)) for k, r in rooms.items())
            built = {}
            for k, r in rooms.items():   # buildings inside the walls: none may push heat, burn fuel or draw power
                g = t.bridge_call("jawa/list_things", group="BuildingArtificial", rect="%d,%d,5,5" % (r[0] + 1, r[1] + 1),
                                  limit=1) or {}
                built[k] = sorted((g.get("perDef") or {}).keys())
            cook = _spawn_colonist(t, cx - 2, cz - 8)
            t.bridge_call("jawa/set_work_priority", pawnId=cook, workType="Cooking", priority=1)
            spot = t.bridge_call("jawa/build_batch", ops="ButcherSpot:%d,%d" % (cx + 2, cz - 8)) or {}
            giver = ((spot.get("things") or spot.get("built") or [{}])[0]).get("id")
            beast = _spawn_wild(t, "RM_FurnaceBeast", cx + 4, cz - 8)
            t.bridge_call("jawa/damage", damageDef="Cut", amount=5000.0, thingId=beast)
            race = [c.get("def") for c in _things(t, "Corpse_RM_FurnaceBeast", limit=5)]
            t.bridge_call("jawa/bill_add", giverId=giver, recipe="ButcherCorpseFlesh", repeatMode="RepeatCount", repeatCount=1)
            order = t.bridge_call("jawa/do_bill_now", pawnId=cook, billGiverId=giver, workGiverDef="DoBillsButcherFlesh",
                                  waitTicks=0, timeoutSeconds=30)
            hide, spent = 0, 0
            while _live(t) and spent < 8000 and not hide:
                _r6_tick_on(t, ctl, 500)
                spent += 500
                hide = _r6_stack(t, "RM_FurnaceHide")
            comps = _get_defs(t, "ThingDef/RM_FurnaceHideBank", "comps", deep=True).get("RM_FurnaceHideBank") or {}
            cost = _get_defs(t, "ThingDef/RM_FurnaceHideBank", "costList").get("RM_FurnaceHideBank") or {}
            if _live(t) and hide >= R6_BANK_COST:
                stack = (_things(t, "RM_FurnaceHide", limit=5) or [{}])[0].get("id")
                t.bridge_call("jawa/split_stack", thing=stack, count=R6_BANK_COST, at="%d,%d" % (2, 2))
            t.bridge_call("jawa/build_batch", ops="RM_FurnaceHideBank:%d,%d" % inside["A"])
            t0 = dict((k, _r6_temp(t, c)[0]) for k, c in inside.items())
            series = []
            for h in range(1, R6_BANK_HOURS + 1):
                _r6_tick_on(t, ctl, TEN_HOUR)
                row = dict((k, _r6_temp(t, c)[0]) for k, c in inside.items())
                row["hour"], row["outdoor"] = h, _r6_temp(t, (2, TEN_CONTROL_SIZE - 3))[1]
                series.append(row)
        finally:
            _ten_control_map_drop(t, ctl)
        if _live(t):
            ctext = json.dumps(comps, default=str)
            _note(t, "butcher, bank and rooms", {"corpse": race, "order": order, "hide": hide, "built": built,
                                                 "costList": cost, "comps": ctext[:600], "start": t0, "hourly": series})
            if not race:
                _unmeasured(t, "no RM_FurnaceBeast corpse lay at the butcher spot after the kill")
            if built.get("A") or built.get("B"):
                _fail("the rooms hold more than walls before the bank: %r" % built)
            if not all(isinstance(v, (int, float)) for v in t0.values()) or abs(t0["A"] - t0["B"]) > 1 or t0["A"] >= 21:
                _unmeasured(t, "the twin rooms do not start within 1 C of each other below 21 C: %r" % t0)
            if not hide:
                _fail("butchering the furnace-beast yielded no RM_FurnaceHide: %r" % order)
            if hide < R6_BANK_COST:
                _unmeasured(t, "the butcher gave %d RM_FurnaceHide, under the costList's %d" % (hide, R6_BANK_COST))
            for bad in ("CompProperties_Refuelable", "CompProperties_Power", "CompRefuelable", "CompPowerTrader"):
                if bad in ctext:
                    _fail("RM_FurnaceHideBank carries %s" % bad)
            for row in series:
                if None in (row["A"], row["B"]):
                    _unmeasured(t, "a room temperature was unread at hour %d" % row["hour"])
                if row["A"] > R6_BANK_CEILING:
                    _fail("room A read %.1f C at hour %d, above %.1f" % (row["A"], row["hour"], R6_BANK_CEILING))
                if row["hour"] >= R6_BANK_FROM_HOUR and row["A"] - row["B"] < R6_BANK_MARGIN:
                    _fail("at hour %d room A %.1f C is not %.0f C above room B %.1f C"
                          % (row["hour"], row["A"], R6_BANK_MARGIN, row["B"]))


def _r6_hp(rows):
    return dict((r.get("id"), r.get("hitPoints")) for r in rows)


def _r6_roof_withers_pair(t, x, z, label):
    """Two walled 5x5 ember-grass patches 3 cells apart on deep ash, a roof on A only; hourly for R6_WITHER_HOURS: live
    counts, hit points, the wither line on A, fire within 20 cells. -> dict."""
    a, b = (x - 7, z - 2, 5, 5), (x + 1, z - 2, 5, 5)
    t.clear_area(size=TEST_SIZE)
    for r in (a, b):
        t.bridge_call("jawa/set_terrain", x=r[0], z=r[1], terrainDef=DEEP_ASH, width=5, height=5, layer="top")
        _plants(t, "RM_FE_Plant_EmberGrass", r)
        ring = [(cx, r[1] - 1) for cx in range(r[0] - 1, r[0] + 6)] + [(cx, r[1] + 5) for cx in range(r[0] - 1, r[0] + 6)] \
            + [(r[0] - 1, cz) for cz in range(r[1], r[1] + 5)] + [(r[0] + 5, cz) for cz in range(r[1], r[1] + 5)]
        t.bridge_call("jawa/build_batch", ops=";".join("Wall:%d,%d" % c for c in ring), stuff="Steel")   # grazers kept out
    t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % _rs(a))
    roof = str((t.bridge_call("jawa/get_roof_batch", rects="%s;%s" % (_rs(a), _rs(b))) or {}).get("ops") or "")
    rc = _r6_ops_cells(roof)
    inside = lambda r: [(cx, cz) for cx in range(r[0], r[0] + 5) for cz in range(r[1], r[1] + 5)]  # noqa: E731
    roofed = {"A": sum(1 for c in inside(a) if rc.get(c) == "RoofConstructed"),
              "B": sum(1 for c in inside(b) if rc.get(c) not in (None, "", "None"))}
    start = dict((k, _things(t, "RM_FE_Plant_EmberGrass", _rs(r))) for k, r in (("A", a), ("B", b)))
    near = (x - 27, z - 22, 54, 45)
    hours = []
    for h in range(1, R6_WITHER_HOURS + 1):
        _wait(t, TEN_HOUR)
        ra, rb = _things(t, "RM_FE_Plant_EmberGrass", _rs(a)), _things(t, "RM_FE_Plant_EmberGrass", _rs(b))
        ins = t.bridge_call("jawa/inspect_string", rect=_rs(a), limit=30) or {}
        line = any(R6_WITHER_LINE in str(ln) for row in ins.get("things") or [] for ln in row.get("inspect") or [])
        hours.append({"hour": h, "A": len(ra), "B": len(rb), "hpA": sum(int(v or 0) for v in _r6_hp(ra).values()),
                      "line": line, "fire": _count(t, "Fire", _rs(near))})
    t.bridge_call("jawa/set_roof_batch", ops="None:%s" % _rs(a))
    return {"label": label, "roofOps": roof, "roofed": roofed, "startA": len(start["A"]), "startB": len(start["B"]),
            "hpA0": sum(int(v or 0) for v in _r6_hp(start["A"]).values()), "hours": hours}


@suite.chain("roof_withers")
@_teardown(fire=True, weather=True)
def roof_withers(t):
    """Scene sc_roof_withers (g5). PyrelandsMechanicsGate on (asserted), weather locked Clear, no fire within 20 cells;
    two walled 5x5 mature ember-grass patches on deep ash 3 cells apart, a roof on A only (asserted from get_roof_batch);
    hourly for 48 h: A's plants lose hit points, show RM_WithersUnderRoof's line and are all gone by hour 36; B keeps every
    plant; no fire at any read. Then the same pair again with the gate off (pyrelandsEnabled False), and again with the
    shell's roster toggle off (_ten_roster_set): neither patch loses a plant. Live half: scenes.json live_command (UNRUN here)."""
    _pad(t, R6_PAD_WITHER)
    x, z = t.anchor
    with _comp(t, "roofed_ember_grass_withers"):
        on = _ten_gate_on(t)
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        _extinguish(t)
        run = _r6_roof_withers_pair(t, x, z, "gate on")
        if _live(t):
            _note(t, "roofed A vs open B, hourly", run)
            hs = run["hours"]
            if on is not True:
                _unmeasured(t, "PyrelandsMechanicsGate.get_On reads %r on the site" % on)
            if run["roofed"]["A"] < 25 or run["roofed"]["B"]:
                _unmeasured(t, "the roof is not on every A cell and no B cell: %r" % run["roofOps"])
            if not run["startA"] or not run["startB"]:
                _unmeasured(t, "a patch took no ember grass: A %d, B %d" % (run["startA"], run["startB"]))
            if any(r["fire"] for r in hs):
                _unmeasured(t, "fire within 20 cells at hour(s) %r" % [r["hour"] for r in hs if r["fire"]])
            if not hs[0]["hpA"] < run["hpA0"]:
                _fail("A's plants lost no hit points in the first hour: %r -> %r" % (run["hpA0"], hs[0]["hpA"]))
            if not any(r["line"] for r in hs[:6]):
                _fail("the roofed plants never showed '%s'" % R6_WITHER_LINE)
            if hs[R6_WITHER_GONE_BY - 1]["A"]:
                _fail("%d roofed plants still stand at hour %d" % (hs[R6_WITHER_GONE_BY - 1]["A"], R6_WITHER_GONE_BY))
            if any(r["B"] < run["startB"] for r in hs):
                _fail("the open patch B lost plants: %r" % [r["B"] for r in hs])
    _independent(t)
    with _comp(t, "gate_off_kills_nothing"):
        _set(t, {"pyrelandsEnabled": False})
        off = _ten_gate_on(t)
        run = _r6_roof_withers_pair(t, x, z + 10, "gate off")
        _set(t, {"pyrelandsEnabled": True})
        if _live(t):
            _note(t, "gate off: roofed A vs open B, hourly", run)
            if off is not False:
                _fail("pyrelandsEnabled False left PyrelandsMechanicsGate.get_On %r" % off)
            hs = run["hours"]
            if any(r["A"] < run["startA"] or r["B"] < run["startB"] for r in hs):
                _fail("with the gate off a patch lost plants: A %r, B %r" % ([r["A"] for r in hs], [r["B"] for r in hs]))
    _independent(t)
    with _comp(t, "roof_withers_roster_toggle_off"):
        _ten_roster_set(t, False)
        try:
            roster, off = _ten_roster_on(t), _ten_gate_on(t)
            run = _r6_roof_withers_pair(t, x, z - 10, "roster toggle off")
        finally:
            _ten_roster_set(t, True)
        if _live(t):
            _note(t, "roster toggle off: roofed A vs open B, hourly", dict(run, roster=roster, gate=off))
            if roster is not False or off is not False:
                _fail("the roster toggle off read Enabled %r, PyrelandsMechanicsGate.get_On %r" % (roster, off))
            hs = run["hours"]
            if any(r["A"] < run["startA"] or r["B"] < run["startB"] for r in hs):
                _fail("with the roster toggle off a patch lost plants: A %r, B %r"
                      % ([r["A"] for r in hs], [r["B"] for r in hs]))


def herds_of(animals, radius=R6_HERD_RADIUS):
    """Pure. animals [(id, kind, x, z)] -> [[id, ...]]: same-kind animals linked within `radius` cells
    (MapComponent_PyrelandsHerdThirst's herd), each herd sorted, herds by first id."""
    left = list(animals)
    out = []
    while left:
        seed = left.pop(0)
        herd, frontier = [seed], [seed]
        while frontier:
            a = frontier.pop()
            near = [b for b in left if b[1] == a[1] and _dist((a[2], a[3]), (b[2], b[3])) <= radius]
            for b in near:
                left.remove(b)
            herd += near
            frontier += near
        out.append(sorted(h[0] for h in herd))
    return sorted(out)


def arrival_overlaps(arrivals):
    """Pure. {herd: [hours at the water]} -> sorted hours two or more herds share; None when no herd arrived at all."""
    if not any(arrivals.values()):
        return None
    seen = {}
    for hours in arrivals.values():
        for h in set(hours):
            seen[h] = seen.get(h, 0) + 1
    return sorted(h for h, n in seen.items() if n > 1)


def one_herd_level(levels, tol=0.05, unstaggered=0.8, band=0.003):
    """Pure. RM_Thirst of one spawned herd read just after MapComponent_PyrelandsHerdThirst's stagger -> (True|False|None,
    why). True: every animal reads one level within `tol` and the level is not FlowWorks' InitialLevel 0.8 (within
    `band`). The stagger draws Rand(0.22, 1), so a real stagger lands in that band about 0.8% of the time (a false FAIL
    that odd). None: an animal is unreadable. Visit 2, 2026-11-21: the old read of every native herd failed a correct mod,
    because herds_of links animals transitively days after the stagger and so merges two staggered herds."""
    if not levels or any(v is None for v in levels):
        return None, "an animal's RM_Thirst is unreadable: %r" % (levels,)
    if max(levels) - min(levels) > tol:
        return False, "one herd holds levels %.3f apart: %r" % (max(levels) - min(levels), levels)
    if all(abs(v - unstaggered) <= band for v in levels):
        return False, "the herd still reads FlowWorks' starting level %.1f: never staggered: %r" % (unstaggered, levels)
    return True, "one level %.3f" % (sum(levels) / len(levels))


def thirst_fall_rates(series):
    """Pure. {kind: [[level per pawn] per hour]} -> {kind: mean RM_Thirst fall per live pawn-hour, None with no live
    pair}. A pair counts only when both readings exist (a dead or despawned pawn reads None); a rise (a drink) adds a
    zero fall. Visit 2, 2026-11-21: the control muffalo died by game hour 5 on the 50 C site, so a 72 h SUM compared
    the ullai's three days with the muffalo's few hours and failed a correct mod."""
    out = {}
    for kind, rows in series.items():
        total, pairs = 0.0, 0
        for prev, cur in zip(rows, rows[1:]):
            for a, b in zip(prev, cur):
                if a is not None and b is not None:
                    total += max(0.0, a - b)
                    pairs += 1
        out[kind] = total / pairs if pairs else None
    return out


@suite.chain("herd_thirst")
@_teardown(fire=True)
def herd_thirst(t):
    """Scene sc_herd_thirst (g5). FlowWorks' RM_Thirst resolves, PyrelandsMechanicsGate on, MapComponent_PyrelandsHerdThirst
    present; every wild native herd's RM_Thirst at the first read (herds_of: same kind within 10 cells); 4 RM_Ullai (with
    RM_ThirstGrassWateredExtension) and 4 Muffalo (without) spawned equidistant from one water cell, staggered once and
    then set to one level; RM_Thirst hourly for 72 h (the ullai fall at most R6_THIRST_RATIO of the muffalo's); each wild
    herd's arrivals within R6_DRINK_CELLS of water by the hour over 168 h (arrival_overlaps: none shared; none at all is
    UNMEASURED); no native dehydrates; vitals and incidents unchanged. The toggle-off same-seed map is removed
    (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, polish.md): sc_herd_thirst decides no bar in the test table."""
    _pad(t, PAD_PROBE)
    with _comp(t, "natives_thirst_slow_and_staggered"):
        need = t.bridge_call("jawa/get_defs", defs="NeedDef/RM_Thirst", fields="label")
        on = _ten_gate_on(t)
        mc = t.bridge_call("jawa/map_comp_read", comp=R6_HERD_THIRST)
        # jawa/get_def lists modExtension TYPE names (extra.modExtensions); get_defs' deep field dump carries only the
        # fields, so a class-name search in it never matched (visit 2, 2026-11-21: FAIL on a ullai that had it)
        ext = dict((d, ((t.bridge_call("jawa/get_def", defName=d) or {}).get("extra") or {}).get("modExtensions") or [])
                   for d in ("RM_Ullai", "Muffalo"))
        if _live(t):
            if (need or {}).get("notFound") or not (need or {}).get("defs"):
                _unmeasured(t, "RM_Thirst does not resolve: FlowWorks is not on this list")
            if on is not True:
                _unmeasured(t, "PyrelandsMechanicsGate.get_On reads %r" % on)
            if not (mc or {}).get("success", False):
                _fail("MapComponent_PyrelandsHerdThirst is not on the site: %r" % mc)
            u, m = ext.get("RM_Ullai") or [], ext.get("Muffalo") or []
            if "RM_ThirstGrassWateredExtension" not in u or "RM_ThirstGrassWateredExtension" in m:
                _fail("the extension is not on RM_Ullai alone: ullai %r / muffalo %r" % (u, m))
        guard0 = _r6_guard(t)
        cells = _r6_terrain_cells(t, _whole(t))
        water = sorted(c for c, d in cells.items() if is_water_family(d))
        if _live(t) and not water:
            _unmeasured(t, "the site rolled no standing water for a herd to visit")
        wx, wz = water[len(water) // 2] if water else t.anchor
        tests = {"RM_Ullai": [_spawn_wild(t, "RM_Ullai", wx - 12, wz + i) for i in range(4)],
                 "Muffalo": [_spawn_wild(t, "Muffalo", wx + 12, wz + i) for i in range(4)]}
        _wait(t, R6_HERD_STAGGER_TICKS)
        staggered = [_need(t, pid, "RM_Thirst") for pid in tests["RM_Ullai"]]
        for ids in tests.values():
            for pid in ids:
                t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.8)
        test_ids = set(i for ids in tests.values() for i in ids)
        r = t.bridge_call("jawa/list_pawns", limit=1000, includeHealth=True)
        wild = [(p.get("id"), p.get("kindDef"), p.get("x"), p.get("z")) for p in ((r or {}).get("pawns") or [])
                if p.get("faction") is None and p.get("kindDef") in ANIMAL_MANIFEST and p.get("id") not in test_ids]
        herds = herds_of(wild)
        start = dict((h[0], [_need(t, pid, "RM_Thirst") for pid in h]) for h in herds)
        wset = set(water)
        series = dict((k, []) for k in tests)
        arrivals = dict((h[0], []) for h in herds)
        dehydrated = set()
        for hour in range(1, R6_ARRIVAL_HOURS + 1):
            _wait(t, TEN_HOUR)
            if hour <= R6_THIRST_HOURS:
                for k, ids in tests.items():
                    series[k].append([_need(t, pid, "RM_Thirst") for pid in ids])
            rows = dict((p.get("id"), p) for p in ((t.bridge_call("jawa/list_pawns", limit=1000, includeHealth=True)
                                                    or {}).get("pawns") or []))
            for h in herds:
                for pid in h:
                    p = rows.get(pid) or {}
                    if _has_hediff(p, "RM_Dehydration"):
                        dehydrated.add(pid)
                    if p.get("x") is not None and any(_dist((p["x"], p["z"]), w) <= R6_DRINK_CELLS for w in wset
                                                      if abs(w[0] - p["x"]) <= R6_DRINK_CELLS):
                        arrivals[h[0]].append(hour)
                        break
        guard1 = _r6_guard(t)
        if _live(t):
            falls = thirst_fall_rates(series)   # per live pawn-hour: the control herd may die on the site
            overlap = arrival_overlaps(arrivals)
            _note(t, "herd thirst", {"herds": len(herds), "startLevels": start, "falls": falls,
                                     "arrivalHours": arrivals, "overlap": overlap, "dehydrated": sorted(dehydrated),
                                     "guard": [guard0, guard1]})
            if not falls["Muffalo"]:
                _unmeasured(t, "the muffalo's RM_Thirst never fell over a live hour (dead before the first read, or "
                               "never thirsty): %r" % (falls,))
            if falls["RM_Ullai"] is None:
                _unmeasured(t, "no ullai lived through an hour of the watch")
            if falls["RM_Ullai"] > R6_THIRST_RATIO * falls["Muffalo"]:
                _fail("the ullai's RM_Thirst fell %.5f an hour, over a third of the muffalo's %.5f" % (
                    falls["RM_Ullai"], falls["Muffalo"]))
            levels = [round(sum(v) / len(v), 2) for v in start.values() if v and None not in v]
            if len(herds) > 1 and len(set(levels)) < 2:
                _fail("the wild herds start at one shared RM_Thirst level: %r" % levels)
            one, why = one_herd_level(staggered)
            _note(t, "spawned ullai herd after the stagger", {"levels": staggered, "verdict": one, "why": why})
            if one is None:
                _unmeasured(t, why)
            if one is False:
                _fail("the spawned ullai herd: %s" % why)
            if dehydrated:
                _fail("natives dehydrated: %r" % sorted(dehydrated))
            dmg = _r6_guard_changes(guard0, guard1)
            if dmg:
                _fail("the week changed the colony: %r" % dmg)
            if overlap is None:
                _unmeasured(t, "no wild herd reached the water over %d hours" % R6_ARRIVAL_HOURS)
            if overlap:
                _fail("two herds at the water in the same hour: %r" % overlap[:10])


# Fire-hawk hunt rewards and the map-wide ember carry: live chains built WITH their items (owner 2026-11-13), kept in their own
# file so this one is not a merge point; register() adds them to this suite with this module's helpers.
def _register_firehawk_rewards():
    import types
    # walk_small_live.py: the two small scenes that replaced the two-week walk. It is loaded here, not by a line of its own:
    # a new module-level statement touches every check of this file (rerun_relation, 2026-11-24)
    for name in ("firehawk_rewards_live", "walk_small_live"):
        spec = importlib.util.spec_from_file_location(
            "pyrelands_" + name, os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.register(suite, types.SimpleNamespace(**globals()))


_register_firehawk_rewards()
