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

if __name__ == "__main__":     # `python3 validation.py <offline scene>` runs without modcheck's driver on sys.path
    for _p in ("modcheck", ""):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils", _p))
from modcheck import Suite, ExpectationFailed
import helpers as H   # noqa: E402 - modcheck puts its own directory on sys.path

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
    "leanFireBias": 0.5, "leanPlantsEnabled": True, "galeDustOverlayEnabled": True,
    "drippingRegrowEnabled": True, "crownMobEnabled": True, "runwayBloomEnabled": True,
    "sweetlineStationsEnabled": True, "sweetlineVisitorsEnabled": True, "sweetlineVisitIntervalDays": 8.0,
    "visslerArmFoodEnabled": True,
    "sweetlineScratchingEnabled": True, "sweetlineCoatReady": 0.8, "sweetlineFeltShare": 0.2,
    "sweetlineTreeMapChance": 0.25, "sweetlineFeltComfortEnabled": True, "sweetlineFeltApparelEnabled": True,
    "fireStampEnabled": True,
    "thornholdDenEnabled": True, "thornholdStandEnabled": True, "rollbugCarrionEnabled": True,
    "rollbugTakesColonyCorpses": True,
    # LEANINGSCRUB_MECHANICS_BUILD_1 parts 6, 5b, 8 (RM_Ripple.cs, RM_CallingPyre.cs, RM_ScrubInjections.cs)
    "rippleEnabled": True, "rippleMaxBodySize": 0.6, "stallHuntEnabled": True, "leanWakesEnabled": True,
    "callingPyreEnabled": True, "callingPyreRadius": 14.0, "callingPyreHerdFactor": 1.0,
    "scrubInjectionsEnabled": True, "scrubRuinsPerMap": 3, "scrubCampsEnabled": True,
    # LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1 (RM_VenomvineForms.cs)
    "rearingEnabled": True, "rearingHours": 2.0, "walkingEnabled": True, "walkingMaxCellsPerMap": 120,
    "hoardEnabled": True, "hoardGrowInHours": 4.0, "hoardKeepsDeadGear": True,
    "quenchEnabled": True, "quenchRecoveryDays": 3.0, "swornSparesMarkedEnabled": True,
    "sheddingEnabled": True, "sheddingLength": 8,
    # the four further forms (RM_VenomvineFourForms.cs; owner card 2026-10-08)
    "stranglerEnabled": True, "stranglerDamageFactor": 1.0, "stranglerAutoTrim": True,
    "weeperEnabled": True, "weeperPollutes": True, "sleeperEnabled": True, "lureEnabled": True,
    # VENOMVINE_BUILD_SCRUB_GROWS_TEETH (RM_VenomvineIslands.cs; owner cards 2026-10-16 Q1 15%, Q3 cap 22%)
    "venomvineIslandsEnabled": True, "venomvineIslandShare": 0.15, "venomvineIslandsMin": 8, "venomvineIslandsMax": 14,
    "venomvineIslandMaxCells": 200, "venomvineIslandRoomsEnabled": True, "venomvineStartClearance": 30.0,
    "venomvineCreepEnabled": True, "venomvineCreepDays": 10.0, "venomvineCreepDownwindShare": 0.75,
    "venomvineCreepCap": 0.22,
    # RM_ShirrelGlide.cs (the shirrel's Gale glide; sc_settings' census found it missing here, 2026-11-16)
    "shirrelGlideEnabled": True,
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

def _remove_pawns_in(call, rect):
    """Vanish every living pawn in rect ('x,z,w,h'): no death, no corpse. jawa/destroy_batch never removes
    pawns and refuses categories=Pawn (DESTROY_BATCH_NEVER_KILLS_PAWNS_1). Returns how many were removed."""
    r = call("jawa/list_pawns", rect=rect, limit=500)
    n = 0
    for p in ((r or {}).get("pawns") or []) if isinstance(r, dict) else []:
        if p.get("dead") or not p.get("id"):
            continue
        # LIVE round 2 2026-10-16: this vanished the site's own colonists standing in the natural pad. A humanlike
        # player pawn is the SITE's (helpers.is_colonist); never remove one. Fixtures are session-tracked and cleaned there.
        if p.get("isPlayer") and p.get("intelligence") == "Humanlike":
            continue
        call("jawa/pawn_force_incapacitate", pawn=p["id"], action="vanish")
        n += 1
    return n


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
    _open_sky(t, r)
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(r)), layer="top")
    _settle_bystanders(t)
    _clear_wildlife(t)


def _clear_wildlife(t):
    """SITE, LIVE round 2 2026-10-16: the map's own wildlife (a kreetle against a ribbonwhip / eopie) fought on the
    site and broke gale_turbine_breakdown. No LeaningScrub row reads an animal it did not spawn, and every chain
    spawns its fixtures after _prep, so factionless animals are removed here (no death, no corpse, no detonation;
    helpers.kill_wildlife), as Contagion and Cauldron do. Also re-run after every clock jump (animals respawn)."""
    if not _live(t):
        return
    try:
        res = H.kill_wildlife(t.session)
        if res.acted or res.residue:
            _note(t, "mapgen wildlife removed", {"removed": res.acted, "verified": res.verified,
                                                 "residue": res.residue[:8]})
    except Exception as ex:    # upkeep: a failure is evidence, never a verdict
        _note(t, "wildlife not cleared", str(ex)[:200])


def _requiet(t):
    """After a clock jump or chain boundary: plants regrow around the drafted bystanders (LIVE round 2: one took a
    venomvine Scratch ~tick 380k inside scratch_drops_coat, after the 5.5-day jump) and wildlife respawns. Ground is
    cleared again, bystanders mended and drafted, wildlife removed. Setup upkeep, never a verdict."""
    _settle_bystanders(t)
    _clear_wildlife(t)


def _open_sky(t, rect, raw=False):
    """Remove every roof over `rect`, right after it was cleared. LIVE modcheck4 2026-10-16 (Autosave-9/10 letters): on
    a mountainous site clear_area takes the natural rock out from under the mountain roof, which is then 'too far from
    any support' and collapses on the first tick after setup: lash colonist Koyo, spawned at (171,80), was 'crushed to
    death' (tick 25916), and at 43626/44106 two collapses near (112,167) crushed the bloom chain's dustflutters and
    crustweevils (bloom_answers_a_walker 'no Flee job seen': the cohort was dead, not deaf). A collapse skips unroofed
    cells (RoofCollapserImmediate.DropRoofInCells checks Roofed), so stripping the roof before any tick defuses it. A
    chain that needs a roof (the gale room) builds its own after this. `raw` calls the session directly (teardown)."""
    if t.session is None:
        return
    try:
        if raw:
            r = t.session.call("jawa/set_roof_batch", ops="None:%s" % _rs(rect))
        else:
            r = t.bridge_call("jawa/set_roof_batch", ops="None:%s" % _rs(rect))
        # the bridge answers a refusal, it does not raise: a strip that did not take is said out loud
        if isinstance(r, dict) and (r.get("success") is False or r.get("cellsFailedVerify")):
            print("ROOFSTRIP roof strip incomplete over %s: %s" % (_rs(rect), str(r)[:300]), file=sys.stderr, flush=True)
    except Exception as ex:    # upkeep, never a verdict: a missed strip shows up as the collapse it was meant to stop
        print("[lscrub] roof strip failed over %s: %s" % (_rs(rect), ex), file=sys.stderr, flush=True)


def _settle_bystanders(t):
    """The site's own colonists, mended and drafted at chain setup (helpers.settle_bystanders). LIVE 2026-10-16 a
    bystander left bleeding by the Contagion suite was downed mid gale chain and the vitals latch stopped the clock.
    No LeaningScrub row reads a site colonist: every row spawns its own actors after this runs."""
    if not _live(t):
        return
    try:
        # Plant AND Filth: LIVE round 2 (2026-10-16) a bystander took a venomvine Scratch ~tick 380k inside
        # scratch_drops_coat, after the 5.5-day jump, with the plants round it already cleared. Leading theory,
        # UNPROVEN (the attacker def was not read): RM_ThornLitter, the filth a shedding stand throws downwind in a
        # Gale, which scratches on contact and which a Plant-only clear leaves in place.
        res = H.settle_bystanders(t.session, ground_categories="Plant,Filth")
        _note(t, "bystanders settled (mended / drafted / residue)",
              [res.evidence.get("removed"), res.evidence.get("drafted"), res.residue])
    except Exception as ex:    # upkeep: a failure is evidence, never a verdict (the vitals latch still guards the row)
        _note(t, "bystanders not settled", str(ex)[:200])


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
    """Flip one field for a block; ALWAYS put back the value it held before (the shipped default when that read
    failed) and re-read it. floor_recovery (2026-11-16): restoring DEFAULTS lost a non-default value a scene captured."""
    was = None
    if _live(t):
        try:
            was = _get_setting(t, field)
        except ExpectationFailed:
            was = None
    if was is not None and not _same(was, DEFAULTS[field]):
        print("[lscrub] SETTING CAPTURED OFF-DEFAULT %s = %r (shipped %r): restored to the captured value"
              % (field, was, DEFAULTS[field]), file=sys.stderr, flush=True)
    try:
        _set(t, field, value)    # inside the try: a set whose read-back failed may still have changed the field
        yield
    finally:
        _restore(t, field, was)


def _restore(t, field, value=None):
    """Put `field` back to `value` (the shipped default when None) and re-read it."""
    if t.session is None:
        return
    want = DEFAULTS[field] if value is None else (_as_bool(value) if isinstance(DEFAULTS[field], bool) else value)
    try:
        r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                           value=str(want))
        got = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not _same((got or {}).get("value"), want):
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
    big list). Long waits run fast (helpers.fast_advance), then step the rest exactly."""
    # LIVE 2026-10-03: under the situational watch the Ultrafast poll below moves the clock outside the budgeted gate
    # (BudgetExceeded 'spent 8721 of cap 948'), so a watched run uses the chunked, budgeted t.wait_ticks for every length.
    if t.session is None or t.upstream_failed or n <= 4000 or getattr(t, "watch", None) is not None:
        return t.wait_ticks(n)
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
            _open_sky(t, _rect(t, PAD_SIZE + 8), raw=True)   # its own guard: the gale room's walls go here, its roof must not fall


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
            missing = [n for n in ("RM_ScrubWind", "RM_ScrubWindFog", "RM_Stall", "RM_Gale") + WINDY_TWINS
                       if not w.get(n)]
            if missing:
                _fail("owned weather(s) absent or zero in the biome table: %s" % missing)
            calm = [n for n in ("Clear", "Fog", "Rain", "RainyThunderstorm", "FoggyRain",
                                "SnowGentle", "SnowHard") + tuple(TWINNED_STOCK) if w.get(n)]
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


# --------------------------------------------------------------------------- chain: windlean

# SCRUB_WIND_BUILD_LEAN_ON_PURPOSE part 3 (owner card 2026-10-20): stock weather -> the Scrub's windy twin.
TWINNED_STOCK = {"Overcast": "RM_ScrubOvercast", "GrayPall": "RM_ScrubGrayPall",
                 "DryThunderstorm": "RM_ScrubDryThunderstorm"}
WINDY_TWINS = tuple(sorted(TWINNED_STOCK.values()))


@suite.chain("windlean")
def windlean_chain(t):
    """SCRUB_WIND_BUILD_LEAN_ON_PURPOSE (biome_bars_sitting_2026-10-20 §5.1-5.3). The lean rows need a Leaning Scrub map
    (the saved site, LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY): on any other map the hook answers UNMEASURED, never PASS. The look is the owner's."""
    with _comp(t, "twins_carry_wind"):
        if _live(t):
            f, _ = _get_defs(t, ";".join("WeatherDef/" + n for n in WINDY_TWINS), "windSpeedOffset,windSpeedFactor")
            calm = {}
            for n in WINDY_TWINS:
                row = f.get(n)
                if not isinstance(row, dict):
                    _unmeasured(t, "twin %s unreadable: %r" % (n, row))
                off, fac = row.get("windSpeedOffset"), row.get("windSpeedFactor")
                if not isinstance(off, (int, float)) or off <= 0 or (isinstance(fac, (int, float)) and fac < 1):
                    calm[n] = (off, fac)
            _note(t, "twin wind", f)
            if calm:
                _fail("a windy twin can fall calm (windSpeedOffset <= 0 or factor < 1): %s" % calm)
    _proof(t, "lean_faces_wind", "RM_PlantLeanProof", "ProofLean", "on", "plant lean (on)", "leanPlantsEnabled")
    _proof(t, "lean_toggle_off_vanilla", "RM_PlantLeanProof", "ProofLean", "off", "plant lean (off)", "leanPlantsEnabled")
    try:
        with _comp(t, "gale_dust_overlay", toggle="galeDustOverlayEnabled"):
            if _live(t):
                _lock_weather(t, "RM_Gale")
                _wait(t, 120)      # the overlay ticks with the weather: give it a few hundred frames under the Gale
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_GaleDustProof",
                              method="ProofGale", args="on")
            if _live(t):
                txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                _note(t, "gale dust overlay", txt[:300])
                if txt.startswith("FAIL"):
                    _fail("gale dust overlay: %s" % txt[:400])
                if not txt.startswith("PASS"):
                    _unmeasured(t, "gale dust overlay did not answer PASS/FAIL: %s" % txt[:200])
                if "PLACEHOLDER" in txt:
                    _note(t, "gale dust art", "PLACEHOLDER: vanilla fog sheet until the queued art is reviewed")
    finally:
        _unlock_weather(t)


# --------------------------------------------------------------------------- chain: the Lean

# LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY (walk lines 39-41). RM_TheLeanProof (RM_TheLeanProof.cs) reads the SHIPPED wind
# on the current map: heading == 90 - sun bearing; a wild non-predator flees a person upwind within leanScentRange
# (through JobGiver_AnimalFlee, the Harmony postfix included) and never one downwind or beyond; fire through the shipped
# Fire.TrySpread lands downwind more than with leanFireEnabled off (300 trials per arm, z >= 3). Every hook answers
# UNMEASURED off a Leaning Scrub map: run on the saved site (test_site_saves.py load leaningscrub).
PADS["lean"] = (-55, 55)     # far from the site colonists at the centre: the scent hook wants no person within 40 cells
LEAN_PAD = 48                # _prep clears 56 square: the probe people stand 8 and leanScentRange + 4 (20) cells out


@suite.chain("lean")
def lean_chain(t):
    """The Lean on a Leaning Scrub map: one wind toward the sun, scent upwind only, fire leaning downwind."""
    _proof(t, "lean_heading_from_sun", "RM_TheLeanProof", "ProofHeading", "", "lean heading")
    _prep(t, "lean", size=LEAN_PAD)
    try:
        x, z = t.anchor
        _proof(t, "lean_scent_upwind_flees", "RM_TheLeanProof", "ProofScent", "on@%d,%d" % (x, z),
               "lean scent (on)", "leanScentEnabled")
        _proof(t, "lean_scent_toggle_off", "RM_TheLeanProof", "ProofScent", "off@%d,%d" % (x, z),
               "lean scent (off)", "leanScentEnabled")
        _proof(t, "lean_fire_downwind", "RM_TheLeanProof", "ProofFire", "on@%d,%d" % (x, z),
               "lean fire (on vs off)", "leanFireEnabled")
    finally:
        _unlock_weather(t)    # _prep locked Clear


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
                # NOT REPRODUCED 2026-10-16 (two runs, jobs sampled, bystanders drafted by _settle_bystanders since
                # ce15acb1cb): Thornhold path 0.0, only Wait_Wander/Wait_MaintainPosture; Shirrel only wander-family.
                # The 10-07 job stays unnamed. Leading UNPROVEN theory: the lean-scent flee (RM_TheLeanPatches.
                # AnimalFlee_Postfix, 24 cells off any humanlike upwind, Stall not exempt) fired on then-undrafted
                # colonists. A recurrence prints the job: check_stall_move.py <run.json> (live_evidence/ holds 10-16).
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
                if res[ids["small"]]["alive"] < 3:
                    _unmeasured(t, "the small animal vanished from list_pawns: %r" % res)
                if res[ids["small"]]["path"] < 3.0:
                    _fail("with stallFreezeEnabled OFF the small animal still moved only %.1f cells "
                          "in 1500 ticks (the toggle does not release it)" % res[ids["small"]]["path"])
        with _comp(t, "stall_master_off_wanders", toggle="modEnabled"):
            if _live(t):
                with _setting(t, "modEnabled", False):
                    res = _path(t, [ids["small"]])
                _note(t, "Stall, modEnabled OFF: path", res)
                if res[ids["small"]]["alive"] < 3:
                    _unmeasured(t, "the small animal vanished from list_pawns: %r" % res)
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
                # The wind path (vanilla WindTurbineUtility.CalculateWindCells, rot North, 5x2): x tx-3..tx+3, z tz+2..tz+11
                # and tz-6..tz-1. Each roofed or blockWind cell takes 20% off, so five zero the output. LIVE 2026-10-16
                # on the Scrub site all three readings were 0.0 W (a 2026-10-07 quicktest map read 4485/3450 W); clear_area
                # removed the things, so the path roof is opened here and the inspect lines are kept as evidence.
                path = "%d,%d,7,10;%d,%d,7,6" % (tx - 3, tz + 2, tx - 3, tz - 6)
                roof0 = t.bridge_call("jawa/get_roof_batch", rects=path)
                if _roofed(roof0):
                    t.bridge_call("jawa/set_roof_batch", ops=";".join("None:" + r for r in path.split(";")))
                    _note(t, "turbine wind path was roofed; roof removed (before / after)",
                          [roof0, t.bridge_call("jawa/get_roof_batch", rects=path)])
                t.bridge_call("jawa/spawn_batch", ops="WindTurbine:%d,%d" % (tx, tz), rot=0)
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
                try:
                    _set(t, "galeTurbineBreakdownMtbDays", 0)     # 0 = never: keep the turbine whole
                    t.wait_ticks(4100)      # the wind ramps into the Gale over the transition
                    on1 = _turbine_output(t, ids["turbine"])
                    with _setting(t, "galeTurbineSurgeEnabled", False):
                        off = _turbine_output(t, ids["turbine"])
                    on2 = _turbine_output(t, ids["turbine"])
                finally:
                    _restore(t, "galeTurbineBreakdownMtbDays")
                _note(t, "turbine output W (on, off, on)", [on1, off, on2])
                if off <= 0:
                    try:    # evidence only: an unreadable inspect must not turn this UNMEASURED into a FAIL
                        _, why = _inspect(t, ids["turbine"])
                    except ExpectationFailed as ex:
                        why = "unreadable: %s" % str(ex)[:120]
                    _unmeasured(t, "turbine produces %.1f W with the surge off (obstructed or "
                                   "unpowered): no baseline; inspect %r" % (off, why))
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

LASH_EXPECTED_HURT = ("Scratch", "RM_VenomvineVenom", "BloodLoss")   # RM_VenomvineScratch (parent Scratch) + its venom


@contextlib.contextmanager
def _expected_lash(col):
    """clockgate.expected_disturbance for the lash victim: a 'hurt' trigger on `col` whose newest hediff is one the
    lash deals. Downed, dead, another pawn or another hediff are not matched (testenv_guards.expected_hurt)."""
    import clockgate
    import testenv_guards as TG
    preds = [TG.expected_hurt([col], h) for h in LASH_EXPECTED_HURT]
    with clockgate.expected_disturbance("twitcher lash on its test colonist (the row's subject)",
                                        lambda trig: any(p(trig) for p in preds)):
        yield

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
                # LIVE 2026-10-16: the strike IS the row ("health 1 -> 0.86; newest hediff BloodLoss"), and the vitals
                # latch stopped the wait as undeclared harm -> UNMEASURED. Declared, bounded to THIS colonist and the
                # lash's own marks (the scratch, its venom, the bleeding it starts); anything else still stops the clock.
                with _expected_lash(ids["col"]):
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
                # LIVE round 2: 0 venom after a flat 1200 ticks with the stand "Ready to harvest" -- the walk to a plant
                # that RM_CompProperties_BodySizeBarrier makes costly (trappedMoveCost 450) plus harvestWork 250 can
                # outlast one fixed window. Bounded wait instead: step 600 ticks, stop at the first venom, give up at
                # 7200, and note the colonist's job each step so a stuck job is evidence, not silence.
                venom, trail = 0, []
                for _step in range(12):
                    t.wait_ticks(600)
                    venom = _stack_total(t, "RM_RawVenom", _rs(rect))
                    trail.append((venom, _jobs(t).get(col)))
                    if venom >= 1:
                        break
                _note(t, "dripping harvest wait trail (venom, colonist job) per 600 ticks", trail)
                standing = _count(t, "RM_DrippingVenomvine", "%d,%d,1,1" % (x, z))
                _, lines = _inspect(t, plant[0]["id"]) if standing else (None, [])
                _note(t, "dripping harvest: venom items / stand standing / inspect",
                      [venom, standing, lines])
                if venom < 1:
                    _unmeasured(t, "no venom was harvested in 7200 ticks (job not done): cannot "
                                   "judge whether the stand survives")
                if standing != 1:
                    _fail("the harvest destroyed the dripping stand (drippingRegrowEnabled is ON "
                          "and the def should regrow it from growth 0.3)")
                pct = re.search(r"(\d+)\s*%\s*grown", " ".join(lines), re.I)   # NOT "Growth rate: 100%" (live 2026-10-23: that line matched and failed a correct 30% stand)
                if not pct:
                    _unmeasured(t, "the surviving stand's inspect carries no 'N% grown' line: %r" % (lines,))
                if int(pct.group(1)) > 60:
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
        _remove_pawns_in(t.bridge_call, _rs(_rect(t, PAD_SIZE + 8)))
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
        # LIVE 2026-10-16 modcheck4: both staged crustweevils and dustflutters (the z-3 row) were absent from EVERY
        # site_state poll in both arms, from the first poll 30 ticks after spawn, while the z+3 row (fuzzrunners,
        # visslers) fled; the same coordinates passed at 08:17 on another map. A species with no living staged animal
        # cannot answer a bloom, so presence is tracked per species and an absent cohort is a SITE result, not a FAIL.
        present = dict((k, False) for k in cohort)
        for _ in range(16):
            t.wait_ticks(30)
            jobs = _jobs(t)
            for k, pids in cohort.items():
                if any(p in jobs for p in pids):
                    present[k] = True
                if any(jobs.get(p) == "Flee" for p in pids):
                    saw[k] = True
        arms = _stack_total(t, "RM_VisslerArm", _rs(_rect(t, PAD_SIZE + 8))) - arms0
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")
        # destroy_batch never removes pawns: without this the OFF arm's cohort is still wandering the pad in the ON arm.
        _remove_pawns_in(t.bridge_call, _rs(_rect(t, PAD_SIZE + 8)))
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(_rect(t))), layer="top")
        _note(t, "bloom trial %s: Flee seen per species / vissler arms shed / cohort present" % tag, [saw, arms, present])
        gone = sorted(k for k, v in present.items() if not v)
        return saw, arms, gone

    def body():
        with _comp(t, "bloom_toggle_off_quiet", toggle="runwayBloomEnabled"):
            if _live(t):
                with _setting(t, "runwayBloomEnabled", False):
                    saw, arms, _gone = trial("OFF")
                # Flee alone is NOT bloom-specific: vanilla wild animals flee an approaching colonist with no
                # bloom at all (LIVE 2026-10-08 acc_biomes: all four species fled with the toggle OFF while
                # RM_MapComponent_RunwayBloom.MapComponentTick returns at its first line). The bloom's own
                # signature is the vissler arm shed, which only RunPending produces.
                if arms:
                    _fail("runwayBloomEnabled OFF but the bloom still fired: %d vissler arms shed (Flee %s)"
                          % (arms, saw))
        with _comp(t, "bloom_answers_a_walker", toggle="runwayBloomEnabled"):
            if _live(t):
                saw, arms, gone = trial("ON")
                if gone:
                    _unmeasured(t, "staged %s never appeared in any job poll (dead or despawned within 30 ticks of "
                                   "spawn): this site cannot show whether they answer a bloom" % gone)
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
                _note(t, "bloom visuals (SWAYING n UNDER n HOLES +n ANSWERED n)", txt)
                # RUNWAYBLOOM_FIX_SWAY_HOLD_OUTLIVES_ROCK: only a surrik that was under the crust leaves a hole; the proof
                # puts the staged one under first (UNDER n). UNDER 0 (sand-swim kit off): the hole count proves nothing.
                if not txt.startswith("SWAYING") or txt.startswith("SWAYING 0"):
                    _fail("no ribbonwhip swaying after a bloom: %s" % txt)
                if " UNDER 0 " in txt:
                    _unmeasured(t, "no surrik under the crust before the bloom (sand-swim kit off?): %s" % txt)
                if "HOLES +0" in txt:
                    _fail("a surrik under the crust broke out without an exit hole: %s" % txt)
                t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")
    _stable(t, body)


# --------------------------------------------------------------------------- chain: stamp

STAMP_DISC = 22     # RM_FireStampProof.DiscClear: radius the proof needs standable, unroofed, pawn- and fire-free
PADS["bystamp"] = (-55, 55)   # bystanders chain: a 46-cell square clear of the site colonists at the centre
PADS["stamp"] = (0, 0)    # the map centre: the 46-cell square overlaps the fuel/spawn pads (chains run in turn, each clears its own)


@suite.chain("stamp")
def stamp_chain(t):
    """Part 5 fire-stamping (RM_FireStamp.cs). The C# proof hook builds the fixture on the pad this chain clears (two
    fires, then six; a far stamper, then a near one), drives the SHIPPED ConvergePass/StampPass and cleans up.
    LIVE 2026-10-16 the hook scanned the map for an ambient clear 22-cell disc and found none on the wooded run map,
    so both rows were UNMEASURED whatever the mod did: the chain now clears a disc-sized pad and names its centre."""
    _prep(t, "stamp", size=2 * STAMP_DISC - 6)      # _prep clears size + 8 = a 46-cell square, the disc's diameter
    try:
        for mode, name in (("on", "stamp_answers_a_blaze"), ("off", "stamp_toggle_off_ignores_fire")):
            with _comp(t, name, toggle="fireStampEnabled"):
                x, z = t.anchor
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FireStampProof",
                                  method="ProofStamp", args="%s@%d,%d" % (mode, x, z))
                if _live(t):
                    txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                    _note(t, "fire stamp proof (%s)" % mode, txt[:300])
                    if txt.startswith("FAIL"):
                        _fail("fire stamp (%s): %s" % (mode, txt[:400]))
                    if not txt.startswith("PASS"):
                        _unmeasured(t, "fire stamp proof did not answer PASS/FAIL: %s" % txt[:200])

    finally:
        _unlock_weather(t)    # _prep locked Clear: never let it leak into the next chain


def _proof(t, name, typ, method, args, label, toggle=None):
    """One C# proof hook row: PASS/FAIL/UNMEASURED read off the hook's own answer."""
    kw = {"toggle": toggle} if toggle else {}
    with _comp(t, name, **kw):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub." + typ, method=method, args=args)
        if _live(t):
            txt = str((r or {}).get("result") or (r or {}).get("value") or r)
            _note(t, label, txt[:300])
            if txt.startswith("FAIL"):
                _fail("%s: %s" % (label, txt[:400]))
            if not txt.startswith("PASS"):
                _unmeasured(t, "%s did not answer PASS/FAIL: %s" % (label, txt[:200]))


# --------------------------------------------------------------------------- chain: ripple

FUZZ_PATCH = 15    # cells square: wider than the pyre's 6-cell ignite radius on every side of its centre


def _fuzz_patch(t):
    """Lay a mature RM_Fuzz patch (ripple cover) on the bloom pad, which the bloom chain leaves bare. The ripple and pyre
    proof hooks look for cover/unroofed fuzz ON THE MAP; LIVE 2026-10-16 the run map held none ("no fuzz cover plant on
    this map", "no unroofed fuzz on this map"), so both rows were UNMEASURED whatever the mod did. The patch is the
    fixture the hooks need, laid by the chain itself so the rows never depend on ambient flora."""
    _prep(t, "bloom")
    if _live(t):
        x, z = t.anchor
        h = FUZZ_PATCH // 2
        t.bridge_call("jawa/set_plants", ops="RM_Fuzz:%d,%d,%d,%d" % (x - h, z - h, FUZZ_PATCH, FUZZ_PATCH), growth=1.0)
        try:    # evidence only: a patch that did not take shows up as the hook's own UNMEASURED, never a PASS
            _note(t, "fuzz patch laid (cells)", _count(t, "RM_Fuzz", _rs((x - h, z - h, FUZZ_PATCH, FUZZ_PATCH))))
        except ExpectationFailed as ex:
            _note(t, "fuzz patch count unreadable", str(ex)[:200])


def _clear_fuzz_patch(t):
    if _live(t):
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")


@suite.chain("ripple")
def ripple_chain(t):
    """Part 6 the ripple (RM_Ripple.cs; owner Q9 "Hiding with a faint shimmer"). RM_RippleProof spawns a small wild
    animal on fuzz, drives the SHIPPED pass in wind and in the Stall (still), reads IsPsychologicallyInvisible."""
    _fuzz_patch(t)
    _proof(t, "ripple_hides_small_creatures", "RM_RippleProof", "ProofRipple", "on", "ripple proof (on)", "rippleEnabled")
    _proof(t, "ripple_toggle_off_nobody_hides", "RM_RippleProof", "ProofRipple", "off", "ripple proof (off)", "rippleEnabled")
    _clear_fuzz_patch(t)


# --------------------------------------------------------------------------- chain: stallhunt

@suite.chain("stallhunt")
def stallhunt_chain(t):
    """Part 1 the stallhawk rises (RM_StallHunt.cs). RM_StallHuntProof forces the Stall, spawns a stall hunter beside
    visible small prey, drives the SHIPPED pass and reads the hunter's JOB (flyer law: no flight is watched)."""
    _proof(t, "stallhawk_hunts_in_the_stall", "RM_StallHuntProof", "ProofStallHunt", "on", "stall hunt (on)", "stallHuntEnabled")
    _proof(t, "stallhawk_toggle_off_idle", "RM_StallHuntProof", "ProofStallHunt", "off", "stall hunt (off)", "stallHuntEnabled")


# --------------------------------------------------------------------------- chain: dens

@suite.chain("dens")
def dens_chain(t):
    """THORNHOLD_DECIDE_DEN_AND_STAND ("Stand its ground") and ROLLBUG_DECIDE_CARRION_BALL ("Any corpse in reach"),
    both owner by card 2026-10-26 (RM_ScrubDens.cs). The proofs drive the shipped comp gates and the REAL job giver;
    the 4 h MTB node above the giver and the stand's later chase are not exercised here."""
    _prep(t, "spawn")
    rect = _rect(t)
    x, z = rect[0] + 4, rect[1] + 4

    def call(method, args):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub." + method[0], method=method[1], args=args)
        return str((r or {}).get("result", "")) or "no result: %r" % (r,)

    try:
        ids = {}
        if _live(t):
            t.bridge_call("jawa/set_plants", ops="RM_Venomvine:%d,%d,1,1" % (x, z), growth=1.0)
            ids["thorn"] = _spawn(t, "RM_Thornhold", x + 2, z)
            ids["guest"] = _spawn(t, "Hare", x + 4, z, faction="player")
        den_at = "current|%d,%d" % (x + 2, z)
        with _comp(t, "thornhold_dens_in_venomvine", toggle="thornholdDenEnabled"):
            if _live(t):
                text = call(("RM_CompVineDen", "ProofDen"), den_at)
                _note(t, "thornhold den proof", text)
                if not text.startswith("DEN") or "den=(%d, 0, %d)" % (x, z) not in text:
                    _fail("a wild thornhold 2 cells from a lone venomvine did not den on it: %s" % text)
        with _comp(t, "thornhold_stand_toggle_off_refused", toggle="thornholdStandEnabled"):
            if _live(t):
                with _setting(t, "thornholdStandEnabled", False):
                    text = call(("RM_CompVineDen", "ProofStand"), "%s|%d,%d" % (den_at, x + 4, z))
                _note(t, "stand proof with the stand OFF", text)
                if not text.startswith("REFUSED"):
                    _fail("thornholdStandEnabled OFF but the thornhold still stood: %s" % text)
        with _comp(t, "thornhold_stands_at_den", toggle="thornholdStandEnabled"):
            if _live(t):
                text = call(("RM_CompVineDen", "ProofStand"), "%s|%d,%d" % (den_at, x + 4, z))
                _note(t, "stand proof", text)
                if not text.startswith("STAND") or "state=RM_ThornholdStand" not in text:
                    _fail("a thornhold struck at its den by a pawn did not take RM_ThornholdStand: %s" % text)
                elif ids.get("guest") and ("target=" + ids["guest"]) not in text:
                    _fail("the stand did not name the attacker %s: %s" % (ids["guest"], text))
        # Rollbug: a player-faction hare corpse is the colony's own dead (the gate the setting guards).
        bx, bz = x + 10, z + 6
        if _live(t):
            _remove_pawns_in(t.bridge_call, _rs(rect))    # the standing thornhold must not join in
            ids["bug"] = _spawn(t, "RM_Rollbug", bx, bz)
            ids["meat"] = _spawn(t, "Hare", bx + 5, bz, faction="player")
            _ok(t.bridge_call("jawa/damage", damageDef="Bullet", amount=5000, thingId=ids["meat"],
                              allowColonists=True), "damage(kill)")
        bug_at = "current|%d,%d" % (bx, bz)
        with _comp(t, "rollbug_colony_corpse_toggle_off_refused", toggle="rollbugTakesColonyCorpses"):
            if _live(t):
                with _setting(t, "rollbugTakesColonyCorpses", False):
                    text = call(("RM_CompCarrionLarder", "ProofOrderRoll"), bug_at)
                _note(t, "roll proof with colony corpses OFF", text)
                if not text.startswith("REFUSED"):
                    _fail("rollbugTakesColonyCorpses OFF but the rollbug took the colony's dead hare: %s" % text)
        with _comp(t, "rollbug_rolls_any_corpse", toggle="rollbugCarrionEnabled"):
            if _live(t):
                text = call(("RM_CompCarrionLarder", "ProofOrderRoll"), bug_at)
                _note(t, "roll proof", text)
                if not text.startswith("ORDERED"):
                    _fail("a wild rollbug 5 cells from a fresh corpse was not sent to roll it: %s" % text)
                m = re.search(r"larder=\((\d+), 0, (\d+)\)", text)
                if not m:
                    _unmeasured(t, "roll proof named no larder cell: %s" % text)
                larder = (int(m.group(1)), int(m.group(2)))
                _wait(t, 1500)
                row = _rows(t, rect=_rs(rect)).get(ids["bug"]) or {}
                corpses = _things(t, "Corpse_Hare", _rs(rect))
                _note(t, "rollbug and corpse after the roll", [_xz(row), [_xz(c) for c in corpses]])
                if len(corpses) != 1:
                    _fail("after the roll the pad holds %d hare corpses (expect exactly 1: no loss, no copy)"
                          % len(corpses))
                elif _dist(_xz(corpses[0]), larder) > 3:
                    _fail("the corpse lies at %s, not within the larder's 2 cells of %s" % (_xz(corpses[0]), larder))
        with _comp(t, "rollbug_bites_its_ball", toggle="rollbugCarrionEnabled"):
            if _live(t):
                at = _xz(_rows(t, rect=_rs(rect)).get(ids["bug"]) or {})
                if at is None:
                    _unmeasured(t, "rollbug position unreadable after the roll")
                text = call(("RM_CompCarrionLarder", "ProofBite"), "current|%d,%d" % at)
                _note(t, "bite proof", text)
                if not (text.startswith("ATE") and ("BIT" in text or "FINISHED" in text)):
                    _fail("a starving rollbug at its larder beside its ball did not bite it: %s" % text)
    finally:
        _remove_pawns_in(t.bridge_call, _rs(rect))
        _stable(t, lambda: None)
        _unlock_weather(t)


# --------------------------------------------------------------------------- chain: pyre

PYRE_CROP = "Plant_Potato"     # vanilla crop, Flammability 1: the "fields" the rite torches


def _crop_patch(t):
    """Lay a mature crop patch on the bloom pad for the pyre. NOT the fuzz: the scrub's living flora is fireproof by
    design (arid_shrubland.md ban 9, RM_Fuzz Flammability 0) and LIVE 2026-10-16 the pyre lit 0 fires on a 225-cell
    fuzz patch -- FireUtility.TryStartFireIn refuses a cell with nothing flammable. The rite torches the colony's
    FIELDS, so the fixture is a field."""
    _prep(t, "bloom")
    if _live(t):
        x, z = t.anchor
        h = FUZZ_PATCH // 2
        t.bridge_call("jawa/set_plants", ops="%s:%d,%d,%d,%d" % (PYRE_CROP, x - h, z - h, FUZZ_PATCH, FUZZ_PATCH),
                      growth=1.0)
        try:    # evidence only: a patch that did not take shows up as the hook's own FAIL/UNMEASURED, never a PASS
            _note(t, "crop patch laid (cells)", _count(t, PYRE_CROP, _rs((x - h, z - h, FUZZ_PATCH, FUZZ_PATCH))))
        except ExpectationFailed as ex:
            _note(t, "crop patch count unreadable", str(ex)[:200])


@suite.chain("pyre")
def pyre_chain(t):
    """Part 5b the calling-pyre (RM_CallingPyre.cs; Q7 three beliefs, N3 fire/ritual memes only). Defs gated on the
    memes; the SHIPPED Ignite/CallHerd on a crop patch; the gate refuses with the toggle off."""
    _proof(t, "pyre_beliefs_gated_on_memes", "RM_CallingPyreProof", "ProofPyre", "defs", "pyre defs")
    _crop_patch(t)
    x, z = t.anchor
    _proof(t, "pyre_lights_fields_and_calls_herd", "RM_CallingPyreProof", "ProofPyre", "fire@%d,%d" % (x, z), "pyre fire",
           "callingPyreEnabled")
    _clear_fuzz_patch(t)
    _unlock_weather(t)
    _proof(t, "pyre_toggle_off_refuses", "RM_CallingPyreProof", "ProofPyre", "off", "pyre off", "callingPyreEnabled")


# --------------------------------------------------------------------------- chain: injections

@suite.chain("injections")
def injections_chain(t):
    """Parts 3 + 8 (RM_WindVaporator.xml, RM_ScrubInjections.cs; Q8 plain vaporator from a dead farmstead, Q10 ruins
    plus living camps, N1 scavengers and the new farmers). The vaporator's defs, then the SHIPPED map step run on the
    current map: at least one site and one dead farmstead's vaporator wrecks."""
    _proof(t, "vaporator_learned_from_farmstead", "RM_VaporatorProof", "ProofVaporator", "", "vaporator defs")
    with _comp(t, "map_holds_ruins_and_camps", toggle="scrubInjectionsEnabled"):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_GenStep_ScrubInjections",
                          method="ProofInjections", args="")
        if _live(t):
            txt = str((r or {}).get("result") or (r or {}).get("value") or r)
            _note(t, "injections (PLACED sites=n vaporatorWrecks=+n campPeople=+n)", txt[:300])
            m = re.search(r"sites=(\d+) vaporatorWrecks=\+(-?\d+) campPeople=\+(-?\d+) farmers=(\w+)", txt)
            if not m:
                _unmeasured(t, "injection proof did not answer PLACED: %s" % txt[:200])
            if int(m.group(1)) < 1:
                _unmeasured(t, "no open site on this map for any injection: %s" % txt[:200])
            if int(m.group(2)) < 1:
                _fail("the map step placed no dead farmstead: %s" % txt[:300])
            if m.group(4) == "True" and int(m.group(3)) < 1:
                _fail("the comb holds exist and are at peace but no camp people were placed: %s" % txt[:300])
            # NOTE: the proof leaves its ruins and camp on the map (a disposable test map); later chains see them.


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
    applies on a Scrub map (the saved site, LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY), so the Gale-onset trigger itself is UNCOVERED."""
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


# --------------------------------------------------------------------------- chain: bystanders

def _ids(t, rect=None, **kw):
    """{thing id} for list_things(kw) over `rect`; raises on a truncated or unreadable listing (never an empty set)."""
    q = dict(kw, limit=5000)
    if rect:
        q["rect"] = rect
    r = _ok(t.bridge_call("jawa/list_things", **q), "list_things(%s)" % kw)
    things = r.get("things") or []
    if r.get("isCompleteList") is False or (r.get("countMatched") or 0) > len(things):
        _unmeasured(t, "list_things(%s) truncated: %s of %s" % (kw, len(things), r.get("countMatched")))
    return set(x.get("id") for x in things if x.get("id") is not None)


@suite.chain("bystanders")
def bystanders_chain(t):
    """SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL A1 (749eea3aa): the stamp, pyre and forms proof hooks touch only what they
    made. Before 749eea3aa their cleanup destroyed every fire within 30 cells, the plant on a fixture cell, every steel
    stack within 4 cells and scratched any colonist on sworn thorns anywhere. Each row stages a bystander INSIDE the
    hook's cleanup reach but OUTSIDE the clear disc the hook demands (else the hook rightly answers UNMEASURED), runs the
    hook, and reads the bystander back by id. The game stays paused throughout, so nothing else moves a bystander.
    LIES: forms' FindSpot picks its own cell, so whether a plant stood on it is not known; the row counts every plant on
    the map (paused: only the hook can change the count) and the fixture's venomvines are excluded by def."""
    # stamp: its own pad (LIVE 2026-10-21 the map-centre "stamp" pad held the site's drafted colonists, so DiscClear
    # refused it), 22-cell clear disc; ClearNewFires reaches 30 -> a map fire at 26 cells must survive
    _prep(t, "bystamp", size=2 * STAMP_DISC - 6)
    try:
        with _comp(t, "bystander_fire_survives_stamp"):
            if _live(t):
                x, z = t.anchor
                fx, fz = x + 26, z
                t.bridge_call("jawa/destroy_batch", rects=_rs((fx - 1, fz - 1, 3, 3)), categories="All")
                t.bridge_call("jawa/spawn_batch", ops="Fire:%d,%d" % (fx, fz))
                before = _ids(t, _rs((fx, fz, 1, 1)), defName="Fire")
                _note(t, "bystander fire at (%d,%d) ids" % (fx, fz), sorted(before))
                if not before:
                    _unmeasured(t, "no fire stood at (%d,%d) after spawn_batch: nothing to protect" % (fx, fz))
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FireStampProof",
                                  method="ProofStamp", args="on@%d,%d" % (x, z))
                txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                _note(t, "stamp proof (on) with a bystander fire", txt[:300])
                after = _ids(t, _rs((fx, fz, 1, 1)), defName="Fire")
                if not txt.startswith("PASS"):
                    _unmeasured(t, "stamp proof did not PASS with the bystander present: %s" % txt[:200])
                if not before <= after:
                    _fail("the stamp proof's cleanup destroyed the map's own fire at (%d,%d): %s -> %s" % (fx, fz, sorted(before), sorted(after)))
                t.bridge_call("jawa/destroy_batch", rects=_rs((fx - 1, fz - 1, 3, 3)), categories="All")
    finally:
        _unlock_weather(t)
    # pyre: crop patch on the bloom pad, Ignite radius 6, cleanup 30 -> a map fire 12 cells off must survive
    _crop_patch(t)
    with _comp(t, "bystander_fire_survives_pyre"):
        if _live(t):
            x, z = t.anchor
            fx, fz = x, z + 12
            t.bridge_call("jawa/spawn_batch", ops="Fire:%d,%d" % (fx, fz))
            before = _ids(t, _rs((fx, fz, 1, 1)), defName="Fire")
            if not before:
                _unmeasured(t, "no fire stood at (%d,%d) after spawn_batch: nothing to protect" % (fx, fz))
            r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_CallingPyreProof",
                              method="ProofPyre", args="fire@%d,%d" % (x, z))
            txt = str((r or {}).get("result") or (r or {}).get("value") or r)
            _note(t, "pyre proof (fire) with a bystander fire", txt[:300])
            after = _ids(t, _rs((fx, fz, 1, 1)), defName="Fire")
            if not txt.startswith("PASS"):
                _unmeasured(t, "pyre proof did not PASS with the bystander present: %s" % txt[:200])
            if not before <= after:
                _fail("the pyre proof's cleanup destroyed the map's own fire at (%d,%d)" % (fx, fz))
    _clear_fuzz_patch(t)
    _unlock_weather(t)
    # forms: a steel stack, a colonist standing in unmarked sworn thorns, and every plant on the map
    _prep(t, "sweetline")
    sx, sz = t.anchor
    venom = set(d for _f, d in FORMS)
    with _comp(t, "bystanders_survive_forms"):
        if _live(t):
            t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,50" % (sx - 4, sz))
            t.bridge_call("jawa/set_plants", ops="RM_SwornVenomvine:%d,%d,1,1" % (sx + 4, sz), growth=1.0)
            col = _spawn(t, "Colonist", sx + 4, sz, faction="player")
            steel = _ids(t, _rs((sx - 4, sz, 1, 1)), defName="Steel")
            thorn = _ids(t, _rs((sx + 4, sz, 1, 1)), defName="RM_SwornVenomvine")
            if not steel or not thorn:
                _unmeasured(t, "bystander steel %s / sworn thorn %s did not stand" % (sorted(steel), sorted(thorn)))
            hurt0 = len(_hediffs(_rows(t, health=True).get(col)))
            n0 = _ok(t.bridge_call("jawa/list_things", group="Plant", limit=1), "list_things(Plant)").get("countMatched")
            v0 = sum(_count(t, d) for d in venom)
            answers = {}
            for form in ("rearing", "hoard", "sworn", "quench", "walking", "shedding"):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_VenomvineFormsProof",
                                  method="ProofForm", args="%s|on" % form)
                answers[form] = str((r or {}).get("result") or (r or {}).get("value") or r)[:160]
            _note(t, "forms proofs with bystanders", answers)
            n1 = _ok(t.bridge_call("jawa/list_things", group="Plant", limit=1), "list_things(Plant)").get("countMatched")
            v1 = sum(_count(t, d) for d in venom)
            steel1 = _ids(t, _rs((sx - 4, sz, 1, 1)), defName="Steel")
            hurt1 = len(_hediffs(_rows(t, health=True).get(col)))
            _note(t, "plants (all, venomvine) before -> after; steel ids; colonist hediffs",
                  [n0, v0, n1, v1, sorted(steel), sorted(steel1), hurt0, hurt1])
            if any(not a.startswith("PASS") for a in answers.values()):
                _unmeasured(t, "a forms proof did not PASS with bystanders present: %s" % answers)
            if n0 is None or n1 is None:
                _unmeasured(t, "plant census unreadable: %s -> %s" % (n0, n1))
            bad = []
            if (n1 - v1) < (n0 - v0):
                bad.append("plants other than the fixture's venomvines %d -> %d" % (n0 - v0, n1 - v1))
            if not steel <= steel1:
                bad.append("the bystander steel stack %s is gone (%s)" % (sorted(steel), sorted(steel1)))
            if hurt1 > hurt0:
                bad.append("the colonist on sworn thorns gained hediffs (%d -> %d)" % (hurt0, hurt1))
            if bad:
                _fail("; ".join(bad))
            t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="All")


# --------------------------------------------------------------------------- chain: the four further forms

FOUR = (("strangler", "stranglerEnabled"), ("weeper", "weeperEnabled"), ("sleeper", "sleeperEnabled"), ("lure", "lureEnabled"))


@suite.chain("four_forms")
def four_forms_chain(t):
    """Strangler, Weeper, Sleeper, Lure (RM_VenomvineFourForms.cs). RM_FourFormsProof.ProofForm builds each fixture on the
    current map, drives the SHIPPED comp / sweep with the setting on and then off, reads it back and cleans up. UNCOVERED
    live: that wild animals actually walk to lure fruit (needs a wild herbivore and hunger; watch it with the owner), and
    the strangler's cut-back designation being worked by a colonist."""
    for form, toggle in FOUR:
        for mode, name in (("on", "%s_acts" % form), ("off", "%s_toggle_off" % form)):
            with _comp(t, name, toggle=toggle):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof",
                                  method="ProofForm", args="%s|%s" % (form, mode))
                if _live(t):
                    txt = str((r or {}).get("result") or (r or {}).get("value") or r)
                    _note(t, "%s proof (%s)" % (form, mode), txt[:300])
                    if txt.startswith("FAIL"):
                        _fail("%s (%s): %s" % (form, mode, txt[:400]))
                    if not txt.startswith("PASS"):
                        _unmeasured(t, "%s proof did not answer PASS/FAIL: %s" % (form, txt[:200]))


# --------------------------------------------------------------------------- chain: venomvine islands and creep

@suite.chain("islands")
def islands_chain(t):
    """VENOMVINE_BUILD_SCRUB_GROWS_TEETH (RM_VenomvineIslands.cs; design venomvine_design_2026-10-16.md §10 RULED).
    RM_VenomvineIslandsProof runs the SHIPPED pieces on the current (disposable) map with the RM_LeaningScrub island
    extension: ProofIslands lays the islands (share, start clearance, reach, rooms), ProofCreep plants one grown thicket
    and drives the gated creep pass on / off / at the cap (the runner must be unarmed, under half grown), ProofExempt
    reads that our Explosive Growth exemption roster loaded. Offline: the kernel (count, sizes, growth, gap, reach,
    rooms, runner chance, cap, downwind pick) is table-tested in SelfTest/LeaningScrubIslandCheck.cs.
    Live 2026-11-01 (FOUNDRY, RM_TestSite_leaningscrub_v2): 5/5 PASS. The real-map generation, perf and pathing at
    15% islands are read by northstar/venomvine_islands_live.py (check), not by this chain. Still UNCOVERED here: the
    downwind bias on a leaning map (the proof map does not lean)."""
    _proof(t, "islands_laid_share", "RM_VenomvineIslandsProof", "ProofIslands", "", "islands laid",
           toggle="venomvineIslandsEnabled")
    for mode, name in (("on", "creep_runner_unarmed"), ("off", "creep_toggle_off"), ("cap", "creep_cap_stops")):
        _proof(t, name, "RM_VenomvineIslandsProof", "ProofCreep", mode, "creep (%s)" % mode,
               toggle="venomvineCreepEnabled")
    _proof(t, "growth_exempt_from_explosive_growth", "RM_VenomvineIslandsProof", "ProofExempt", "", "EG exemption")


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
                # timeException=True: jump past the 5-day timer instead of simulating 5 days (safe-advance gate)
                t.bridge_call("jawa/time_set_ticks", ticks=int(cur + 5.5 * 60000), timeException=True)   # past the 5-day timer
                t.wait_ticks(2100)                                    # one Long tick
                _requiet(t)                                           # the jump regrew plants round the bystanders
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
                    # timeException=True: jump past the visit interval instead of simulating 13 days (safe-advance gate)
                    t.bridge_call("jawa/time_set_ticks", ticks=int(t.session._ticks() + 13 * 60000), timeException=True)
                    t.wait_ticks(2100)
                _requiet(t)
                off_v = seen()     # toggle restored, no tick has passed: the line is visible again
                _note(t, "sweetline visits before / after a 13-day jump, visitors OFF", [before_v, off_v])
                ids["visits_seen"] = seen      # before the verdict: the ON arm reads these even when this one fails
                ids["visits_base"] = off_v
                if off_v != before_v:
                    _fail("sweetlineVisitorsEnabled OFF but %d visit(s) were recorded" % (off_v - before_v))
        with _comp(t, "visitors_come_and_leave_marks", toggle="sweetlineVisitorsEnabled"):
            if _live(t):
                tok0 = _stack_total(t, "RM_SweetlineToken", _rs(_rect(t)))
                # timeException=True: jump past the visit interval instead of simulating 13 days (safe-advance gate)
                t.bridge_call("jawa/time_set_ticks", ticks=int(t.session._ticks() + 13 * 60000), timeException=True)
                t.wait_ticks(2100)
                _requiet(t)
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


# --------------------------------------------------------------------------- chain: GPT edge-case fixes, read live
# The 2026-10-16 GPT edge-case consult (design/RimMandrake/gpt_consults/LeaningScrub_edge_cases_2026-10-16.md) found five
# bugs, fixed offline at 2bb6c1d00 and pinned by selftest_leaningscrub_gpt_fixes.py. Each row here is the live A1 of its
# item, read through a C# proof hook that stages its own fixture on this pad and removes it. NOT here:
# SCRUB_BLOOM_FIX_ERUPTOR_FLEES_GROUNDED (its A1 is the eruptor taking off: a flight test, owner present only).

@suite.chain("edge_fixes")
def edge_fixes_chain(t):
    _prep(t, "spawn", size=40)                       # the thin row's islands span 33 cells
    x, z = t.anchor
    try:
        # SCRUB_PYRE_FIX_FIVE_FIRES_FIVE_ISLANDS A1: no stamper creature needed (the clause asks only for a blaze)
        _proof(t, "pyre_thin_line_follows_blaze", "RM_CallingPyreProof", "ProofPyre", "thin@%d,%d" % (x, z - 6),
               "pyre thin line", "callingPyreEnabled")
        # SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY A1: a walker (RM_Crustweevil, Scatter), never the eruptor
        _proof(t, "bloom_spares_manhunter", "RM_MapComponent_RunwayBloom", "ProofManhunter", "manhunter@%d,%d" % (x, z + 10),
               "bloom vs a manhunter", "runwayBloomEnabled")
        # SCRUB_GENSTEP_FIX_TIDIES_THEN_QUITS A1
        _proof(t, "map_step_refuses_pawn_cell", "RM_GenStep_SweetlineTrees", "ProofRefusesPawnCell",
               "cell@%d,%d" % (x + 10, z + 4), "map step on a pawn's cell", "sweetlineStationsEnabled")
        # LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A2: every meat-eating walker on the roster, very hungry beside an arm
        _proof(t, "vissler_arm_draws_meat_eaters", "RM_VisslerArmPatches", "ProofArmScavengers",
               "on@%d,%d" % (x - 10, z + 4), "vissler arm scavengers", "visslerArmFoodEnabled")
        _proof(t, "vissler_arm_off_draws_none", "RM_VisslerArmPatches", "ProofArmScavengers",
               "off@%d,%d" % (x - 10, z + 4), "vissler arm scavengers, toggle off", "visslerArmFoodEnabled")
    finally:
        _unlock_weather(t)


# --------------------------------------------------------------------------- acceptance scenes (scenes.json entries)
# RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT: the Stage 3 entries the test table names `scene_<id>` (sc_<id> in
# design/concepts/LeaningScrub/scenes.json, whose start/action/expect/control/restore each one follows). They run in
# game at Stage 6 and are UNRUN until then; selftest_leaningscrub.py drives each against the fake game, healthy and
# broken. Every scene: designer_stage.py scene-begin with its recovery save BEFORE the first mutation, the save, the
# body, then (even on a throw) settings back by _setting, the save reloaded and its tick checked, and scene-end (an
# owner_review scene saves its end state for him first and calls scene-hold). A failed reload leaves the recovery
# open, which designer_stage refuses further runs on.

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(REPO, "design", "concepts", "LeaningScrub")
# Flight is never live-tested without the owner (CLAUDE.md, three times): an Erupt arm runs only in a joint sitting.
OWNER_PRESENT = os.environ.get("LSCRUB_OWNER_PRESENT") == "1"
ARM = "RM_VisslerArm"
# RM_Vissler's body is vanilla BeetleLike (RM_LeaningScrubFauna.xml): six InsectLeg records and no part named arm. The
# plan binds "arms" to the real body at implementation (plan.md, Vissler regrowth); until the regrowth code picks its
# part, the scene counts the legs. Change this with that code, never alone.
VISSLER_ARM_PART, VISSLER_ARMS = "leg", 6
SEASON_TICKS = 15 * 60000        # plan.md: one 15-day engine season, the agent's reading of "regrows in a season"


def _arm_rot_days():
    """RM_VisslerArm's shipped daysToRotStart (the production boundary, read offline), None when it ships none."""
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<ThingDef\b[^>]*>(.*?)</ThingDef>", txt, re.S):
            if re.search(r"<defName>%s</defName>" % ARM, m.group(1)):
                d = re.search(r"<daysToRotStart>([\d.]+)</daysToRotStart>", m.group(1))
                return float(d.group(1)) if d else None
    return None


ARM_ROT_DAYS = _arm_rot_days()


def _designer_stage(*args):
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "designer_stage.py")]
                       + list(args), capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise ExpectationFailed("designer_stage %s refused: %s" % (args[0], (r.stderr or r.stdout)[-300:]))


SCENE_RECORD = _designer_stage    # the selftest swaps in a recorder: a fake run must not write stage.json


def _game_tick(t):
    r = t.session.call("jawa/get_game_info") if t.session is not None else None
    return (r or {}).get("ticksGame")


def _scene_load(t, name):
    """The recovery reload (floor_recovery swaps it to inject a failed restore)."""
    return t.session.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000)


@contextlib.contextmanager
def _scene(t, sid, hold):
    """scene-begin, recovery save, body, restore (settings by _setting, the save reloaded, its tick read back),
    scene-end; `hold` "owner_review" saves the end state for him and calls scene-hold instead."""
    if not _live(t):
        yield
        return
    name = "lscrub_%s_%d" % (sid, int(time.time()))
    SCENE_RECORD("scene-begin", CONCEPT, "--scene", sid, "--recovery",
                 "rimworld/load_game_ready saveName=%s, then every LeaningScrub setting back to DEFAULTS" % name)
    _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game(%s)" % name)
    tick0 = _game_tick(t)
    try:
        yield
    finally:
        restored = False
        try:
            if hold == "owner_review":
                t.session.call("rimworld/save_game", saveName=name + "_review")
            ld = _scene_load(t, name)
            restored = isinstance(ld, dict) and ld.get("success") is not False and _game_tick(t) == tick0
        except Exception as ex:   # restoring must never mask the verdict that got us here
            print("[lscrub] SCENE RESTORE FAILED %s: %s" % (sid, ex), file=sys.stderr, flush=True)
        if not restored:
            print("[lscrub] SCENE RESTORE FAILED %s: save %s not back at tick %s; the recovery stays open"
                  % (sid, name, tick0), file=sys.stderr, flush=True)
        elif hold == "owner_review":
            SCENE_RECORD("scene-hold", CONCEPT, "--scene", sid, "--until", "the owner has looked at save %s_review" % name)
        else:
            SCENE_RECORD("scene-end", CONCEPT, "--scene", sid)


def _food(t, pid):
    """The pawn's Food need level (jawa/pawn_need list: needs[{need, level, pct}]), None when it has none."""
    r = t.bridge_call("jawa/pawn_need", pawn=pid, action="list")
    for n in (r or {}).get("needs") or []:
        if n.get("need") == "Food":
            return float(n.get("level"))
    return None


def _hungry(t, kind, x, z):
    pid = _spawn(t, kind, x, z)
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=0.05)
    return pid


def _vanish(t, *pids):
    for p in pids:
        if p:
            t.bridge_call("jawa/pawn_force_incapacitate", pawn=p, action="vanish")


def _arm_stacks(t):
    """{arm id: stack} over 80 cells round the pad: a shedding vissler is fleeing, and its arm lands where it stands."""
    return dict((a.get("id"), int(a.get("stackCount") or 1)) for a in _things(t, ARM, _rs(_rect(t, 80)), 500))


def _arm_row(t, aid):
    return next((a for a in _things(t, ARM, _rs(_rect(t, 80)), 500) if a.get("id") == aid), None)


def _disturb(t, cx, cz):
    """One real bloom over (cx, cz): the clock first runs past the bloom cooldown (RM_CoatKernel.CooldownTicks 1250
    within 15 cells), then a fuzz strip is laid along row cz and a colonist WALKS it from 15 cells west to 14 east, and
    the clock runs 480 ticks (answer delay and flee). The walker is removed after."""
    t.wait_ticks(1300)
    t.bridge_call("jawa/set_plants", ops="RM_Fuzz:%d,%d,30,3" % (cx - 15, cz - 1), growth=1.0)
    walker = _spawn(t, "Colonist", cx - 15, cz, faction="player")
    _full(t, walker)
    t.bridge_call("jawa/order_pawn", pawnId=walker, x=cx + 14, z=cz, waitTicks=0, unpause=False)
    for _ in range(16):
        t.wait_ticks(30)
    _vanish(t, walker)


def _at(t, pid, default):
    """(x, z) of a pawn now (it may have fled), else `default`."""
    return _xz(_rows(t).get(pid)) or default


def _missing_arms(t, pid):
    row = _rows(t, health=True).get(pid)
    if row is None:
        return None
    return len([h for h in _hediffs(row) if isinstance(h, dict) and h.get("def") == "MissingBodyPart"
                and VISSLER_ARM_PART in str(h.get("part") or "").lower()])


# --------------------------------------------------------------------------- scene: arm_food

@suite.chain("scene_arm_food")
def scene_arm_food(t):
    """sc_arm_food (arm_food, vissler_arm_food): a naturally shed arm is found, approached and EATEN by a hungry ground
    meat eater (its food rises, the arm is used up), and it rots on real ticks. Controls: a hungry herbivore beside it,
    the food toggle off, and an arm walled off from the eater all leave it uneaten. Rules out: a food-search result
    (ProofArmScavengers) standing in for eating that never completes."""
    _prep(t, "bloom")
    x, z = t.anchor
    arms, state = [], {}

    def eaten_within(eater, ticks):
        """Runs the clock in 250-tick steps until some arm is used up. -> (Ingest seen, {arm id: units eaten}, food
        before, food after). The eater picks its own arm (the nearest), so every arm is watched."""
        s0, f0, ingest = _arm_stacks(t), _food(t, eater), False
        used = {}
        for _ in range(ticks // 250):
            t.wait_ticks(250)
            ingest = ingest or str(_jobs(t).get(eater) or "").startswith("Ingest")
            now = _arm_stacks(t)
            used = dict((i, n - now.get(i, 0)) for i, n in s0.items() if now.get(i, 0) < n)
            if used:
                break
        return ingest, used, f0, _food(t, eater)

    def body():
        with _comp(t, "arm_food_shed_naturally", poison=True):
            if _live(t):
                vs = [_spawn(t, "RM_Vissler", x - 6 + 3 * (j % 4), z - 9 + 2 * (j // 4)) for j in range(8)]
                for _s in range(3):
                    _disturb(t, *_at(t, vs[0], (x, z - 8)))
                    if len(_arm_stacks(t)) >= 2:
                        break
                _remove_pawns_in(t.bridge_call, _rs(_rect(t, PAD_SIZE + 8)))
                arms[:] = sorted(_arm_stacks(t).items())
                _note(t, "arm_food: shed arms (id, stack)", arms)
                if not arms:
                    _unmeasured(t, "no RM_VisslerArm shed by 8 visslers over 3 blooms: the scene needs a natural shed "
                                   "(the bloom's own result is sc_bloom's)")
        eaters = []
        with _comp(t, "arm_food_eater_species", poison=True):
            if _live(t):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_VisslerArmPatches",
                                  method="ProofArmScavengers", args="on@%d,%d" % (x + 6, z + 8))
                m = re.search(r"drawn=\[([^\]]*)\]", str((r or {}).get("result", "")))
                eaters[:] = [k for k in (m.group(1).split(",") if m else []) if k]
                _note(t, "arm_food: roster meat eaters the arm can feed", eaters)
                if not eaters:
                    _unmeasured(t, "no roster meat eater the engine would send to the arm: %r" % r)
        aid = arms[0][0] if arms else None
        with _comp(t, "arm_food_rots_on_real_ticks"):
            if _live(t):
                start = ARM_ROT_DAYS     # the shipped boundary is read offline; live shows the rot ticking
                r0 = t.bridge_call("jawa/comp_read", thing=aid, comp="Rottable", members="RotProgress")
                t.wait_ticks(2500)
                r1 = t.bridge_call("jawa/comp_read", thing=aid, comp="Rottable", members="RotProgress")
                try:
                    p0, p1 = (float(((q or {}).get("values") or {}).get("RotProgress")) for q in (r0, r1))
                except (TypeError, ValueError):
                    _unmeasured(t, "CompRottable.RotProgress unreadable on %s: %r / %r" % (aid, r0, r1))
                state["rot"] = (p0, p1, start)
                _note(t, "arm_food: RotProgress before/after 2500 ticks, daysToRotStart", state["rot"])
                if not p1 > p0:
                    _fail("the arm's rot did not advance over 2500 real ticks (%.0f -> %.0f)" % (p0, p1))
                if not start:
                    _fail("RM_VisslerArm ships no daysToRotStart (Defs/ThingDefs_Items): it never rots")
        with _comp(t, "arm_food_herbivore_leaves_it"):
            if _live(t):
                a = _arm_row(t, aid) or {}
                h = _hungry(t, "Muffalo", a.get("x", x) + 1, a.get("z", z))
                _ingest, used, _f0, _f1 = eaten_within(h, 2000)
                _vanish(t, h)
                if used:
                    _fail("a hungry herbivore (Muffalo) used up vissler arm(s) %s: the arm is meat" % used)
        with _comp(t, "arm_food_toggle_off_uneaten", toggle="visslerArmFoodEnabled"):
            if _live(t):
                a = _arm_row(t, aid) or {}
                with _setting(t, "visslerArmFoodEnabled", False):
                    e = _hungry(t, eaters[0], a.get("x", x) + 3, a.get("z", z))
                    _ingest, used, _f0, _f1 = eaten_within(e, 2000)
                    _vanish(t, e)
                if used:
                    _fail("visslerArmFoodEnabled OFF but a hungry %s used up arm(s) %s" % (eaters[0], used))
        with _comp(t, "arm_food_unreachable_uneaten"):
            if _live(t):
                # the EATER is sealed in, so no arm on the map is reachable (sealing one arm in would leave the others)
                a = _arm_row(t, aid) or {}
                spots = [(a.get("x", x) + dx, a.get("z", z) + dz) for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3), (4, 4))]
                cells = set(_xz(r) for r in _things(t, ARM, _rs(_rect(t, 80)), 500))
                ex, ez = next(((sx, sz) for sx, sz in spots
                               if not any((sx + i, sz + j) in cells for i in (-1, 0, 1) for j in (-1, 0, 1))), spots[-1])
                _ok(t.bridge_call("jawa/make_empty_room", rect="%d,%d,3,3" % (ex - 1, ez - 1), stuffDef="Steel"),
                    "make_empty_room")
                e = _hungry(t, eaters[0], ex, ez)
                _ingest, used, _f0, _f1 = eaten_within(e, 2000)
                _vanish(t, e)
                t.bridge_call("jawa/destroy_batch", rects="%d,%d,3,3" % (ex - 1, ez - 1), categories="All")
                if used:
                    _fail("a %s sealed in a 1-cell room used up arm(s) %s through its walls" % (eaters[0], used))
        with _comp(t, "arm_food_meat_eater_eats_it", toggle="visslerArmFoodEnabled"):
            if _live(t):
                a = _arm_row(t, aid)
                if a is None:
                    _unmeasured(t, "arm %s is gone before the eater arm: a control ate it or it rotted away" % aid)
                e = _hungry(t, eaters[0], a["x"] + 4, a["z"])
                ingest, used, f0, f1 = eaten_within(e, 6000)
                _note(t, "arm_food: %s (Ingest seen, arms used up, food before, after)" % eaters[0], [ingest, used, f0, f1])
                _vanish(t, e)
                if not used:
                    _fail("a hungry %s (food %.2f) did not eat the arm in 6000 ticks (Ingest seen %s)"
                          % (eaters[0], f0 or 0, ingest))
                if not ingest or f1 is None or f0 is None or not f1 > f0:
                    _fail("the arm is gone but no eating was seen (Ingest %s, food %s -> %s)" % (ingest, f0, f1))
    with _scene(t, "sc_arm_food", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: arm_regrowth

@suite.chain("scene_arm_regrowth")
def scene_arm_regrowth(t):
    """sc_arm_regrowth (arm_regrowth, vissler_finite_arm_regrowth): one vissler disturbed again and again loses one arm
    per arm item it sheds and sheds nothing once out of arms (no infinite bait); its missing arms survive a save and
    reload, are still missing just before one 15-day season and regrown at it, and it sheds again after. Control: the
    bloom off sheds nothing. Compression: jawa/time_set_ticks moves the clock to each side of the boundary (the plan's
    compressed season); nothing else is warped."""
    _prep(t, "bloom")
    x, z = t.anchor
    st = {}

    def shed_once(v, strip):
        before, miss0 = sum(_arm_stacks(t).values()), _missing_arms(t, v)
        _disturb(t, *_at(t, v, (x, z)))
        return sum(_arm_stacks(t).values()) - before, (_missing_arms(t, v) or 0) - (miss0 or 0)

    def body():
        with _comp(t, "arm_regrowth_whole_vissler", poison=True):
            if _live(t):
                st["v"] = _spawn(t, "RM_Vissler", x - 4, z - 9)
                m = _missing_arms(t, st["v"])
                if m != 0:
                    _unmeasured(t, "the staged vissler is not whole (missing %r): it cannot show a first loss" % m)
        with _comp(t, "arm_regrowth_off_sheds_nothing", toggle="runwayBloomEnabled"):
            if _live(t):
                with _setting(t, "runwayBloomEnabled", False):
                    items, lost = shed_once(st["v"], 0)
                if items or lost:
                    _fail("runwayBloomEnabled OFF but a disturbance shed %d arm item(s), %d arm(s) lost" % (items, lost))
        with _comp(t, "arm_shed_costs_one_arm_each", poison=True):     # the rest need an exhausted vissler
            if _live(t):
                trail, s = [], 1
                while s <= 2 * VISSLER_ARMS + 4 and (_missing_arms(t, st["v"]) or 0) < VISSLER_ARMS:
                    items, lost = shed_once(st["v"], s)
                    trail.append((items, lost))
                    if items and "first" not in st:
                        st["first"] = _game_tick(t)
                    if items != lost:
                        _note(t, "arm_regrowth: (items, arms lost) per disturbance", trail)
                        _fail("disturbance %d shed %d arm item(s) but the vissler lost %d arm(s): every item must be "
                              "a real arm" % (s, items, lost))
                    s += 1
                _note(t, "arm_regrowth: (items, arms lost) per disturbance", trail)
                if (_missing_arms(t, st["v"]) or 0) < VISSLER_ARMS:
                    _unmeasured(t, "%d disturbances did not exhaust the %d arms (%r)" % (s - 1, VISSLER_ARMS, trail))
        with _comp(t, "arm_exhausted_sheds_nothing"):
            if _live(t):
                for s in range(2):
                    items, _lost = shed_once(st["v"], 20 + s)
                    if items:
                        _fail("a vissler with no arms left shed %d more arm item(s): infinite bait" % items)
        with _comp(t, "arm_missing_survives_reload"):
            if _live(t):
                name = "lscrub_arm_regrowth_mid_%d" % int(time.time())
                _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game(%s)" % name)
                _ok(t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000), "load_game_ready")
                m = _missing_arms(t, st["v"])
                if m != VISSLER_ARMS:
                    _fail("after save and reload the vissler reads %r missing arms, not %d" % (m, VISSLER_ARMS))
        with _comp(t, "arm_still_missing_before_the_season"):
            if _live(t):
                if "first" not in st:
                    _unmeasured(t, "no first shed was seen, so the season boundary is unknown")
                _ok(t.bridge_call("jawa/time_set_ticks", ticks=st["first"] + SEASON_TICKS - 2500), "time_set_ticks")
                t.wait_ticks(250)
                m = _missing_arms(t, st["v"])
                if m != VISSLER_ARMS:
                    _fail("%r arms missing 2500 ticks before the 15-day season ends: an arm regrew early" % m)
        with _comp(t, "arm_regrows_after_one_season"):
            if _live(t):
                _ok(t.bridge_call("jawa/time_set_ticks", ticks=st["first"] + SEASON_TICKS), "time_set_ticks")
                t.wait_ticks(2500)
                m = _missing_arms(t, st["v"])
                st["regrown"] = VISSLER_ARMS - (m if m is not None else VISSLER_ARMS)
                if st["regrown"] < 1:
                    _fail("no arm regrew 2500 ticks past one 15-day season from the first shed (%r missing)" % m)
        with _comp(t, "arm_regrown_sheds_again"):
            if _live(t):
                # one item per arm is arm_shed_costs_one_arm_each's: here the other arms are regrowing on their own
                # timers inside the window, so the loss count cannot be matched item for item
                for s in range(6):
                    items, _lost = shed_once(st["v"], 30 + s)
                    if items:
                        m = _missing_arms(t, st["v"])
                        if m is None or m > VISSLER_ARMS or not m:
                            _fail("after shedding again the vissler reads %r missing arms" % m)
                        break
                else:
                    _fail("a vissler with %d regrown arm(s) shed nothing over 6 disturbances" % st.get("regrown", 0))
    with _scene(t, "sc_arm_regrowth", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: bloom

# Each race's RM_RunwayBloomExtension <response> (Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml).
SURRIK_HOLE = "RM_Filth_SurrikExitHole"     # the Surrik's exitFilth (RM_LeaningScrubFauna.xml)
BLOOM_RESPONSES = {"RM_Crustweevil": "Scatter", "RM_Fuzzrunner": "Bolt", "RM_Ribbonwhip": "Sway",
                   "RM_Surrik": "Surface", "RM_Vissler": "Shed", "RM_Dustflutter": "Erupt"}


@suite.chain("scene_bloom")
def scene_bloom(t):
    """sc_bloom (bloom, runway_bloom): a colonist WALKING through marked cover sets off the bloom: scatterers flee, ribbonwhips sway and are released, only a surrik that was under the
    crust leaves an exit hole, visslers shed a finite number of arms, and an eruptor's take-off waits for the owner.
    Controls: the same walk over bare ground, a stationary colonist in cover, the toggle off, and a manhunter, none
    answering (the manhunter keeps its state). Rules out a direct helper call or an invisible held sway passing."""
    _prep(t, "bloom")
    x, z = t.anchor
    cohort, seen = {}, {}

    def stage(eruptor=False):
        """A fresh cohort; the eruptor (a flyer) only in the owner-present arm."""
        for k in list(cohort):
            _vanish(t, *cohort.pop(k))
        for i, kind in enumerate(sorted(k for k, r in BLOOM_RESPONSES.items() if eruptor or r != "Erupt")):
            n = 4 if kind == "RM_Vissler" else 2
            cohort[kind] = [_spawn(t, kind, x - 12 + 4 * i + (j % 2), z - 1 + 2 * (j // 2)) for j in range(n)]

    def swaying():
        """How many animals the bloom component holds swaying now (its private `swaying` map, read, never driven)."""
        r = t.bridge_call("jawa/map_comp_read", comp="RM_MapComponent_RunwayBloom", members="swaying")
        m = re.search(r"\d+", str(((r or {}).get("values") or {}).get("swaying", "")))
        return int(m.group(0)) if m else None

    def watch(polls=16):
        """-> ({kind: first poll index that saw Flee}, arm items shed) over polls of 30 ticks; the most animals seen
        swaying, the swaying left at the end, the surrik exit holes made and whether a surrik was under the crust
        before go to seen{}."""
        arms0, first = sum(_arm_stacks(t).values()), {}
        holes0 = _count(t, SURRIK_HOLE, _rs(_rect(t, PAD_SIZE + 8)))
        under = [t.bridge_call("jawa/comp_read", thing=p, comp="SandSwim", members="Submerged")
                 for p in cohort.get("RM_Surrik", [])]
        seen["under"] = any("true" in json.dumps((u or {}).get("values") or {}).lower() for u in under)
        seen["sway_max"] = 0
        for i in range(polls):
            t.wait_ticks(30)
            jobs = _jobs(t)
            for k, pids in cohort.items():
                if k not in first and any(jobs.get(p) == "Flee" for p in pids):
                    first[k] = i
            seen["sway_max"] = max(seen["sway_max"], swaying() or 0)
        seen["sway_end"] = swaying()
        seen["holes"] = _count(t, SURRIK_HOLE, _rs(_rect(t, PAD_SIZE + 8))) - holes0
        return first, sum(_arm_stacks(t).values()) - arms0

    def walk(cover, still=False):
        if cover:
            t.bridge_call("jawa/set_plants", ops="RM_Fuzz:%d,%d,30,5" % (x - 15, z - 2), growth=1.0)
        w = _spawn(t, "Colonist", x - 15, z + 1, faction="player")
        _full(t, w)
        if not still:
            t.bridge_call("jawa/order_pawn", pawnId=w, x=x + 14, z=z + 1, waitTicks=0, unpause=False)
        return w

    def body():
        with _comp(t, "bloom_scene_bare_ground_quiet"):
            if _live(t):
                stage()
                w = walk(cover=False)
                first, arms = watch()
                _vanish(t, w)
                if arms:
                    _fail("a walk over BARE ground shed %d vissler arm(s): the bloom answered without cover" % arms)
        with _comp(t, "bloom_scene_stationary_quiet"):
            if _live(t):
                stage()
                w = walk(cover=True, still=True)
                first, arms = watch()
                _vanish(t, w)
                if arms:
                    _fail("a colonist STANDING in cover shed %d vissler arm(s): movement must set the bloom off" % arms)
        with _comp(t, "bloom_scene_toggle_off_quiet", toggle="runwayBloomEnabled"):
            if _live(t):
                stage()
                with _setting(t, "runwayBloomEnabled", False):
                    w = walk(cover=True)
                    first, arms = watch()
                    _vanish(t, w)
                if arms:
                    _fail("runwayBloomEnabled OFF but the walk shed %d vissler arm(s)" % arms)
        # The answer delay itself (delayTicks 15..45, RM_CoatKernel.AnswerTick) is finer than a 30-tick poll can see: the
        # C# SelfTest (LeaningScrubFuzz2) owns it; here the walked bloom, not the delay, is the reading.
        with _comp(t, "bloom_scene_walk_answers"):
            if _live(t):
                stage()
                t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 8)), categories="Item")
                w = walk(cover=True)
                first, arms = watch()
                _vanish(t, w)
                _note(t, "bloom scene: first poll with Flee per species / arms shed", [first, arms])
                silent = sorted(k for k, r in BLOOM_RESPONSES.items() if r in ("Scatter", "Bolt") and k not in first)
                if silent:
                    _fail("no Flee from scatterers %s after a colonist walked through cover" % silent)
                if not 1 <= arms <= len(cohort.get("RM_Vissler", [])) * VISSLER_ARMS:
                    _fail("%d arm item(s) from %d visslers: a shed is finite and real" % (arms, len(cohort["RM_Vissler"])))
        # Read off the WALKED bloom above (ProofVisuals fires its own bloom: a direct call, which this scene rules out).
        with _comp(t, "bloom_scene_sway_released"):
            if _live(t):
                _note(t, "bloom scene sway (most seen, left at the end; swayTicks 180)", [seen.get("sway_max"),
                                                                                         seen.get("sway_end")])
                if not seen.get("sway_max"):
                    _fail("no ribbonwhip held swaying at any poll of the walked bloom")
                if seen.get("sway_end") != 0:
                    _fail("%r animal(s) still swaying 480 ticks after the bloom: the sway is never released"
                          % seen.get("sway_end"))
        with _comp(t, "bloom_scene_exit_hole_only_from_under"):
            if _live(t):
                _note(t, "bloom scene surrik (under the crust before, exit holes made)", [seen.get("under"),
                                                                                         seen.get("holes")])
                if seen.get("under") and not seen.get("holes"):
                    _fail("a surrik under the crust broke out without an exit hole")
                if not seen.get("under") and seen.get("holes"):
                    _fail("%d exit hole(s) from surriks that were not under the crust" % seen["holes"])
                if not seen.get("under"):
                    _unmeasured(t, "no staged surrik was under the crust before the walk (sand-swim kit off?): "
                                   "the hole arm cannot be shown")
        with _comp(t, "bloom_scene_manhunter_keeps_its_state"):
            if _live(t):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_MapComponent_RunwayBloom",
                                  method="ProofManhunter", args="manhunter@%d,%d" % (x, z + 8))
                txt = str((r or {}).get("result", ""))
                if not txt.startswith("PASS"):
                    _fail("bloom vs a manhunter: %s" % txt)
        with _comp(t, "bloom_scene_eruptor_takes_off_owner_present"):
            if _live(t):
                if not OWNER_PRESENT:
                    _unmeasured(t, "an Erupt arm launches a flyer: it runs only with the owner present "
                                   "(LSCRUB_OWNER_PRESENT=1 in a joint sitting; CLAUDE.md flyer rule)")
                stage(eruptor=True)
                w = walk(cover=True)
                watch()
                _vanish(t, w)
                fl = [t.bridge_call("jawa/pawn_flight", pawn=p) for p in cohort.get("RM_Dustflutter", [])]
                flying = [f for f in fl if "flying" in json.dumps(f).lower() and '"flying": true' in json.dumps(f).lower()]
                if not flying:
                    _fail("no dustflutter's flight tracker reads flying after the bloom: %s" % json.dumps(fl)[:300])
    with _scene(t, "sc_bloom", "owner_review"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: cuts

# The cut content (SHRUBLAND_TREE_GUARDIAN_1's bark-wardens; the CombHolds farmer camps; a vaporator drying scar).
CUT_WORDS = re.compile(r"\bguardians?\b|bark[- ]wardens?|farmer camps?|vaporator farmers|drying scar", re.I)
CUT_COMPS = re.compile(r"Guard|Warden|Roost|Rage", re.I)


def _about_text():
    """The mod's About.xml description (the player reads it in the mod list), comments stripped."""
    with open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8") as fh:
        about = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
    return " ".join(re.findall(r"<description>(.*?)</description>", about, re.S))


def _cut_offences(tree_fields, genstep_fields, texts, terrain_before, terrain_after):
    """The cuts checker, a pure function so the scene can show it rejecting injected manifests. -> list of offences."""
    out = []
    comps = json.dumps((tree_fields or {}).get("comps"))
    if CUT_COMPS.search(comps) or CUT_COMPS.search(str((tree_fields or {}).get("thingClass"))):
        out.append("the sweetline tree still carries guardian machinery: %s" % comps[:200])
    ff = (genstep_fields or {}).get("genStep") or {}
    if isinstance(ff, dict) and ff.get("farmerFaction") not in (None, "", "null"):
        out.append("RM_ScrubInjections still names a farmerFaction (%s): farmer camps are built" % ff.get("farmerFaction"))
    for where, txt in sorted(texts.items()):
        m = CUT_WORDS.search(txt or "")
        if m:
            out.append("%s still promises cut content (%r)" % (where, m.group(0)))
    if terrain_before is None or terrain_after is None:
        out.append("the vaporator's ground was not read: a drying scar cannot be ruled out")
    elif terrain_before != terrain_after:
        out.append("the ground around a running vaporator changed: %s -> %s" % (terrain_before[:120], terrain_after[:120]))
    return out


@suite.chain("scene_cuts")
def scene_cuts(t):
    """sc_cuts (cuts, bark_wardens_removed, farmer_camps_removed): no guardian/roost/rage machinery on the sweetline tree,
    no farmerFaction on the map step, no live text promising bark-wardens, farmer camps or a drying scar, and a
    still-shipping vaporator leaves its ground as it found it. The retained tree station must still be there (deleting
    the tree does not pass). Control: the same checker rejects each of three injected manifests (a stale guardian
    promise, an active farmerFaction, a vaporator that dried its ground). The banned CombHolds faction is a hidden
    save-only placeholder (RM_CombHolds.xml) and is not read as gameplay."""
    _prep(t, "fuel")
    x, z = t.anchor
    got = {}

    def body():
        with _comp(t, "cuts_live_manifest", poison=True):
            if _live(t):
                defs, _r = _get_defs(t, ";".join(SHIPPED), "description,label,hidden", deep=False)
                texts = dict(("%s.description" % n, str(f.get("description") or "")) for n, f in defs.items()
                             if not _as_bool(f.get("hidden")))
                texts["About.xml"] = _about_text()
                tree, _r = _get_defs(t, "ThingDef/" + TREE, "comps,thingClass")    # shallow: comps as class names
                gen, _r = _get_defs(t, "GenStepDef/RM_ScrubInjections", "genStep", deep=True)
                got.update(texts=texts, tree=tree.get(TREE), gen=gen.get("RM_ScrubInjections"))
                if not got["tree"] or not got["gen"]:
                    _unmeasured(t, "get_defs did not return %s / RM_ScrubInjections" % TREE)
                if "SweetlineStation" not in json.dumps(got["tree"].get("comps")):
                    _fail("the sweetline tree lost its station comp: deleting retained tree systems does not pass cuts")
        with _comp(t, "cuts_vaporator_ground_kept"):
            if _live(t):
                ring = "%d,%d,9,9" % (x - 4, z - 4)
                b = _ok(t.bridge_call("jawa/get_terrain_batch", rects=ring), "get_terrain_batch").get("ops")
                t.bridge_call("jawa/spawn_batch", ops="RM_WindVaporator:%d,%d" % (x, z), rot=0)
                if not _count(t, "RM_WindVaporator", _rs(_rect(t))):
                    _unmeasured(t, "no RM_WindVaporator on the pad after spawn_batch")
                _wait(t, 6000)
                a = _ok(t.bridge_call("jawa/get_terrain_batch", rects=ring), "get_terrain_batch").get("ops")
                got["terrain"] = (b, a)
                if b != a:
                    _fail("the ground around a running RM_WindVaporator changed over 6000 ticks (a drying scar): "
                          "%s -> %s" % (str(b)[:120], str(a)[:120]))
        with _comp(t, "cuts_no_cut_content"):
            if _live(t):
                b, a = got.get("terrain") or (None, None)
                bad = _cut_offences(got["tree"], got["gen"], got["texts"], b, a)
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "cuts_checker_rejects_injections"):
            if _live(t):
                # each injection alone on a clean manifest, so the live state cannot make a control pass for it
                tree = {"comps": ["RimMandrake.LeaningScrub.RM_CompProperties_SweetlineStation"], "thingClass": "Plant"}
                gen, ground = {"genStep": {"farmerFaction": None}}, "Soil:0,0,9,9"
                clean = (tree, gen, {"About.xml": "A wind-scoured plain."}, ground, ground)
                injected = {
                    "stale guardian promise": (tree, gen, {"About.xml": "Two bark-wardens sleep in it."}, ground, ground),
                    "active farmerFaction": (tree, {"genStep": {"farmerFaction": "RM_Faction_CombHolds"}}, {}, ground,
                                             ground),
                    "drying scar": (tree, gen, {}, ground, ground + ";Sand:4,4"),
                }
                if _cut_offences(*clean):
                    _fail("the cuts checker refuses a clean manifest: %s" % _cut_offences(*clean))
                missed = sorted(k for k, args in injected.items() if not _cut_offences(*args))
                if missed:
                    _fail("the cuts checker passed injected manifest(s) %s: it is blind there" % missed)
    with _scene(t, "sc_cuts", "immediate"):
        _stable(t, body)


# =========================================================================== scenes, batch 2 (Stage 3, 2026-11-16)
# sc_native_cast, sc_pyre_beliefs, sc_pyre_ritual, sc_acoustic_payload, sc_concealment, sc_cane_fuel, sc_colony_walk,
# floor_runtime, sc_settings, floor_persistence (design/concepts/LeaningScrub/scenes.json). Each scene is UNRUN in game
# until Stage 6; each keeps its verdict in a pure checker the scene also shows refusing injected bad readings.


def _count_all(t, defName):
    """countMatched for defName over the whole current map (list_things, limit 1)."""
    r = _ok(t.bridge_call("jawa/list_things", defName=defName, limit=1), "list_things(%s)" % defName)
    if r.get("countMatched") is None:
        _unmeasured(t, "list_things(%s) carries no countMatched" % defName)
    return int(r["countMatched"])


def _map_id(t):
    r = _ok(t.bridge_call("jawa/map_info"), "map_info")
    if r.get("mapId") is None:
        _unmeasured(t, "map_info carries no mapId: the scene could not come back to its own map")
    return r["mapId"]


def _order_goto(t, pid, x, z):
    _ok(t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=x, targetAZ=z, waitTicks=0),
        "ordered_job(Goto %s)" % pid)


def _hidden(row):
    return _has_hediff(row, "RM_RippleHidden")


# --------------------------------------------------------------------------- scene: native_cast

# Three world tiles with no map, set by the Stage 6 runner (LSCRUB_CAST_TILES=a,b,c); the scene sets their biome
# (world_tile_map_generate biome=, test fixtures only) and drops each map after its census.
CAST_TILES = tuple(int(x) for x in os.environ.get("LSCRUB_CAST_TILES", "").split(",") if x.strip().isdigit())
CAST_CONTROL_BIOME = "AridShrubland"     # vanilla: the same-seed control map, carrying none of our rows
CAST_MAP_SIZE = 150


def _roster(row):
    """(plants {def: commonality}, animals {kind: commonality}) from a deep get_defs BiomeDef row."""
    def rows(key, name):
        return dict((x.get(name), float(x.get("commonality") or 0)) for x in (row or {}).get(key) or []
                    if isinstance(x, dict) and x.get(name))
    return rows("wildPlants", "plant"), rows("wildAnimals", "animal")


def _cast_offences(roster, density, maps, control):
    """The native-cast checker, pure. roster (plants, animals) {def: commonality}; density the biome's animalDensity;
    maps [{"plants": {def: n}, "animals": {kind: n}}] one per fresh Scrub map; control {"plants": {def: n}, "listed":
    defs the control biome rosters itself}. Zero counts of rare species are recorded, never offences. -> offences."""
    plants, animals = roster
    out = []
    if not plants:
        out.append("the biome rosters no wild plant")
    if animals and not density:
        out.append("animalDensity is unset (0) with %d rostered animals: no animal ever spawns" % len(animals))
    if len(maps) < 3:
        out.append("%d fresh map(s) censused, the scene needs three" % len(maps))
    for i, m in enumerate(maps):
        if not sum((m.get("plants") or {}).get(d, 0) for d in plants):
            out.append("fresh map %d grew none of the rostered plants" % (i + 1))
    ws = sorted(plants.values())
    common = [d for d, w in plants.items() if ws and w >= ws[len(ws) // 2] and w > 0]
    absent = sorted(d for d in common if not any((m.get("plants") or {}).get(d) for m in maps))
    if absent:
        out.append("common rostered plant(s) absent from every fresh map: %s" % absent)
    if animals and density and maps and not any(sum((m.get("animals") or {}).get(k, 0) for k in animals) for m in maps):
        out.append("no rostered animal on any fresh map")
    if control is None:
        out.append("no same-seed control map was censused")
    else:
        leak = sorted(d for d in plants if d not in control.get("listed", ()) and (control.get("plants") or {}).get(d))
        if leak:
            out.append("the control biome (which rosters none of them) grew %s: the census does not see the roster" % leak)
    return out


def _census_fresh(t, tile, biome, home, plants, animals):
    """Generate a fresh map on `tile` as `biome`, count every rostered plant and wild animal, drop it, come home."""
    r = _ok(t.bridge_call("jawa/world_tile_map_generate", tile=tile, biome=biome, sizeX=CAST_MAP_SIZE,
                          sizeZ=CAST_MAP_SIZE), "world_tile_map_generate(%s, %s)" % (tile, biome))
    if r.get("wasAlreadyGenerated"):
        _unmeasured(t, "tile %s already carried a map: not a fresh map" % tile)
    mid, idx = r.get("mapId"), r.get("mapIndex")      # set_current_map takes the uniqueID, map_drop the Index
    try:
        _ok(t.bridge_call("jawa/set_current_map", mapId=mid), "set_current_map(%s)" % mid)
        cp = dict((d, _count_all(t, d)) for d in sorted(plants))
        ca = {}
        for p in _rows(t).values():
            if p.get("faction") is None and p.get("kindDef") in animals and not p.get("dead"):
                ca[p["kindDef"]] = ca.get(p["kindDef"], 0) + 1
    finally:
        t.bridge_call("jawa/set_current_map", mapId=home)
        _ok(t.bridge_call("jawa/map_drop", mapIndex=idx, notifyPlayer=False), "map_drop(index %s)" % idx)
    return {"tile": tile, "biome": biome, "plants": cp, "animals": ca}


@suite.chain("scene_native_cast")
def scene_native_cast(t):
    """sc_native_cast (native_cast, biome_cast): before any planting or clearing, the effective roster (patch-added rows
    included: get_defs reads the live def) generates on three FRESH Scrub maps: native plants on every map, the common
    half of the plant roster seen, a rostered animal when animalDensity > 0. Zero counts of rare species are recorded,
    never marked proven. Control: the same first tile regenerated as vanilla AridShrubland grows none of our exclusive
    rows (rules out a census that counts what the roster never placed). Not driven here: the view of every race,
    life stage and facing, which is the owner's Stage 8 look; the product/egg/harvest manifest, decided by its own
    bars' scenes. Runner: set LSCRUB_CAST_TILES to three map-free world tiles."""
    _pad(t, "spawn")
    got = {}

    def body():
        with _comp(t, "cast_roster_frozen", poison=True):
            if _live(t):
                rows, _r = _get_defs(t, "BiomeDef/RM_LeaningScrub", "wildPlants,wildAnimals,animalDensity", deep=True)
                row = rows.get("RM_LeaningScrub")
                if not row:
                    _unmeasured(t, "get_defs returned no RM_LeaningScrub row")
                ctl, _r = _get_defs(t, "BiomeDef/" + CAST_CONTROL_BIOME, "wildPlants", deep=True)
                got.update(roster=_roster(row), density=float(row.get("animalDensity") or 0),
                           listed=set(_roster(ctl.get(CAST_CONTROL_BIOME) or {})[0]))
                _note(t, "effective roster", {"plants": got["roster"][0], "animals": got["roster"][1],
                                              "animalDensity": got["density"]})
                if not got["roster"][0]:
                    _fail("RM_LeaningScrub rosters no wild plant (wildPlants read as %r)" % (row.get("wildPlants"),))
        with _comp(t, "cast_fresh_maps_census"):
            if _live(t):
                if len(CAST_TILES) < 3:
                    _unmeasured(t, "name three map-free world tiles: LSCRUB_CAST_TILES=a,b,c")
                home = _map_id(t)
                plants, animals = got["roster"]
                got["maps"] = [_census_fresh(t, tile, "RM_LeaningScrub", home, plants, animals) for tile in CAST_TILES[:3]]
                got["control"] = _census_fresh(t, CAST_TILES[0], CAST_CONTROL_BIOME, home, plants, animals)
                got["control"]["listed"] = got["listed"]
                for m in got["maps"] + [got["control"]]:
                    _note(t, "census tile %s as %s" % (m["tile"], m["biome"]), {"plants": m["plants"], "animals": m["animals"]})
        with _comp(t, "cast_roster_generates"):
            if _live(t):
                if "maps" not in got:
                    _unmeasured(t, "no census was taken")
                bad = _cast_offences(got["roster"], got["density"], got["maps"], got.get("control"))
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "cast_checker_rejects_injections"):
            if _live(t):
                roster = ({"RM_Fuzz": 1.0, "RM_Salvessa": 0.5, "RM_Rare": 0.01}, {"RM_Surrik": 1.0})
                m = {"plants": {"RM_Fuzz": 40, "RM_Salvessa": 3, "RM_Rare": 0}, "animals": {"RM_Surrik": 2}}
                ctl = {"plants": {"RM_Fuzz": 0}, "listed": set()}
                if _cast_offences(roster, 1.0, [m, m, m], ctl):
                    _fail("the cast checker refuses a clean census: %s" % _cast_offences(roster, 1.0, [m, m, m], ctl))
                bare = {"plants": {}, "animals": {}}
                injected = {"an empty map": (roster, 1.0, [m, m, bare], ctl),
                            "animalDensity unset": (roster, 0.0, [m, m, m], ctl),
                            "a common plant never seen": (roster, 1.0, [dict(m, plants={"RM_Fuzz": 9})] * 3, ctl),
                            "the control grows our rows": (roster, 1.0, [m, m, m], {"plants": {"RM_Fuzz": 40}, "listed": set()}),
                            "two maps only": (roster, 1.0, [m, m], ctl)}
                missed = sorted(k for k, a in injected.items() if not _cast_offences(*a))
                if missed:
                    _fail("the cast checker passed injected census(es) %s: it is blind there" % missed)
    with _scene(t, "sc_native_cast", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scenes: pyre_beliefs, pyre_ritual

PYRE_XML = os.path.join(HERE, "Defs", "Ideology", "RM_CallingPyre.xml")


def _pyre_shipped():
    """["DefType/defName"] of every concrete def RM_CallingPyre.xml ships, comments stripped."""
    with open(PYRE_XML, encoding="utf-8") as fh:
        txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
    out = []
    for m in re.finditer(r"<(\w+Def)\b([^>]*)>(.*?)</\1>", txt, re.S):
        nm = re.search(r"<defName>([^<]+)</defName>", m.group(3))
        if nm and not re.search(r'Abstract\s*=\s*"[Tt]rue"', m.group(2)):
            out.append("%s/%s" % (m.group(1), nm.group(1).strip()))
    return out


def _is_ritual_def(w):
    typ, name = w.split("/", 1)
    return "Ritual" in typ or "Ritual" in name or typ == "ThoughtDef" and re.search(r"_(Terrible|Poor|Good|Great)$", name)


def _pyre_record(t, wanted, label):
    """The characterization record: which shipped defs resolve live. A shipped def absent live was discarded by the
    engine (a missing type or a broken parent): that, and only that, is a FAIL; the rest is recorded."""
    defs, r = _get_defs(t, ";".join(wanted), "label", deep=False)
    gone = set(str(n).split("/")[-1] for n in (r or {}).get("notFound") or [])
    present = sorted(w for w in wanted if w.split("/", 1)[1] in defs and w.split("/", 1)[1] not in gone)
    missing = sorted(set(wanted) - set(present))
    _note(t, label, {"present": present, "missing": missing, "callingPyreEnabled": _get_setting(t, "callingPyreEnabled")})
    if missing:
        _fail("%s: shipped in RM_CallingPyre.xml but absent from the running game: %s" % (label, missing))


@suite.chain("scene_pyre_beliefs")
def scene_pyre_beliefs(t):
    """sc_pyre_beliefs (exploration; a capability deferred under OWNER:1794835478275153823): a characterization record
    of the belief half of the calling pyre as it ships -- which precepts, thoughts and history events resolve, the gate
    hook's own answer and the toggle. No acceptance result follows; nothing deferred is implemented or required."""
    _pad(t, "spawn")

    def body():
        with _comp(t, "pyre_beliefs_characterized"):
            if _live(t):
                _pyre_record(t, [w for w in _pyre_shipped() if not _is_ritual_def(w)], "pyre beliefs as shipped")
                r = t.bridge_call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_CallingPyreProof",
                                  method="ProofPyre", args="defs")
                _note(t, "pyre gate hook (record only)", str((r or {}).get("result") or r)[:300])
    with _scene(t, "sc_pyre_beliefs", "immediate"):
        _stable(t, body)


@suite.chain("scene_pyre_ritual")
def scene_pyre_ritual(t):
    """sc_pyre_ritual (exploration; deferred under OWNER:1794835478275153823): a characterization record of the ritual
    half (precept, pattern, behaviour, outcome and its memories) as it ships. Reads only: starting the rite waits for a
    separately authorized sitting. No acceptance result follows."""
    _pad(t, "spawn")

    def body():
        with _comp(t, "pyre_ritual_characterized"):
            if _live(t):
                _pyre_record(t, [w for w in _pyre_shipped() if _is_ritual_def(w)], "pyre ritual as shipped")
    with _scene(t, "sc_pyre_ritual", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: acoustic_payload

SCANNER_PKG = "mandrake.rm.acousticscanner"
SCANNER_SETTINGS = "RimMandrake.AcousticScanner.RM_AcousticScannerSettings"
SOUNDER = "RM_AcousticSounder"          # src/RimMandrake/AcousticScanner/validation.py
PULSE_LABEL = "Sound the ground"
PAYLOAD_XML = os.path.join(HERE, "Patches", "RM_AcousticPayload_LeaningScrub.xml")


def _payload():
    """(quietText, [{label, reading, pawnRaces, thingDefs}]) parsed from the shipped payload patch."""
    import xml.etree.ElementTree as ET
    ext = ET.parse(PAYLOAD_XML).getroot().find(".//value/li")
    targets = []
    for li in ext.find("targets"):
        targets.append(dict(label=li.findtext("label"), reading=li.findtext("reading"),
                            pawnRaces=[x.text for x in li.findall("pawnRaces/li")],
                            thingDefs=[x.text for x in li.findall("thingDefs/li")]))
    return ext.findtext("quietText"), targets


def _reading_offences(staged, text, quiet, targets):
    """The acoustic checker, pure: `staged` the target label staged alone (None for the empty site), `text` the reading
    letter's body. The staged target's reading is there and no other target's is; the empty site reads quiet."""
    if not text:
        return ["no reading letter text"]
    out = []
    for tg in targets:
        heard = tg["reading"] in text
        if tg["label"] == staged and not heard:
            out.append("staged %r alone but the reading lacks its line" % staged)
        elif tg["label"] != staged and heard and (tg["pawnRaces"] or tg["thingDefs"]):   # a cave is the map's own
            out.append("%r read without being staged" % tg["label"])
    if staged is None and quiet not in text:
        out.append("the empty site does not read quiet")
    return out


def _pulse_text(t, sid):
    """Fire the sounder's gizmo as a player would and return the newest 'Sounding reading' letter's text."""
    x, z = t.anchor
    t.bridge_call("rimworld/set_god_mode", enabled=True)
    try:
        t.bridge_call("rimworld/click_cell", x=x, z=z)
        giz = (t.bridge_call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
        g = next((q for q in giz if (q.get("label") or "").startswith(PULSE_LABEL)), None)
        if g is None:
            _unmeasured(t, "no %r gizmo on the selected sounder: %r" % (PULSE_LABEL, [q.get("label") for q in giz]))
        _ok(t.bridge_call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id")), "execute_gizmo")
    finally:
        t.bridge_call("rimworld/set_god_mode", enabled=False)
        t.bridge_call("rimworld/clear_selection")
    t.wait_ticks(10)
    lets = [x for x in (t.bridge_call("rimworld/list_letters") or {}).get("letters") or []
            if str(x.get("label") or "").startswith("Sounding reading")]
    return str(lets[-1].get("text") or "") if lets else ""


@suite.chain("scene_acoustic_payload")
def scene_acoustic_payload(t):
    """sc_acoustic_payload (acoustic_payload): with the Acoustic Scanner in the composition, real pulses over three
    isolated targets (a buried surrik, a sweetline tree, a hollow venomvine) each read that target's banded line and no
    other; the matched empty site reads the biome's quiet text. Without the scanner the biome carries no payload
    extension and the log holds no unresolved AcousticScanner type. One run sees one composition; the other arm runs in
    the other. Not staged: the hidden-cave target ('void in the rock'), which needs a map with hidden caves."""
    _prep(t, "spawn")
    x, z = t.anchor
    quiet, targets = _payload()
    got = {}

    def body():
        with _comp(t, "acoustic_composition", poison=True):
            if _live(t):
                rm = _ok(t.bridge_call("jawa/running_mods", assembly="", details=False), "running_mods")
                ids = [str(i).lower() for i in rm.get("packageIds") or []]
                if not ids:
                    _unmeasured(t, "running_mods listed no packageIds")
                got["scanner"] = SCANNER_PKG in ids
                _note(t, "composition", {"scanner": got["scanner"], "mods": len(ids)})
        with _comp(t, "acoustic_payload_attached"):
            if _live(t):
                rows, _r = _get_defs(t, "BiomeDef/RM_LeaningScrub", "modExtensions")
                exts = json.dumps((rows.get("RM_LeaningScrub") or {}).get("modExtensions"))
                has = "RM_AcousticPayloadExtension" in exts
                if got["scanner"] and not has:
                    _fail("the scanner is loaded but RM_LeaningScrub carries no RM_AcousticPayloadExtension: %s" % exts[:200])
                if not got["scanner"]:
                    if has:
                        _fail("no scanner in the composition, yet the biome carries its payload extension")
                    r = t.bridge_call("jawa/drain_log", contains="AcousticScanner", errorsOnly=True, limit=20)
                    bad = [m.get("text") for m in (_ok(r, "drain_log").get("messages") or [])]
                    if bad:
                        _fail("scanner absent and the log names its types: %s" % [str(b)[:120] for b in bad[:3]])
        with _comp(t, "acoustic_pulses_read_their_target"):
            if _live(t):
                if not got["scanner"]:
                    _unmeasured(t, "the scanner is not in this composition: the pulse arm runs in a scanner-present one")
                _scanner_site(t, x, z, got)
                stage = {"something under the root crust": lambda: _spawn(t, "RM_Surrik", x + 10, z),
                         "sweetline tree": lambda: t.bridge_call("jawa/set_plants", ops="%s:%d,%d" % (TREE, x + 10, z), growth=1.0),
                         "hollow venomvine": lambda: t.bridge_call("jawa/set_plants", ops="RM_HollowVenomvine:%d,%d" % (x + 10, z),
                                                                   growth=1.0)}
                bad = {}
                for label, put in sorted(stage.items()):
                    _isolate(t, x, z)
                    put()
                    t.wait_ticks(5)
                    txt = _pulse_text(t, got["sid"])
                    _note(t, "reading over %s" % label, txt[:300])
                    bad.update(dict((label, b) for b in _reading_offences(label, txt, quiet, targets)))
                if bad:
                    _fail("; ".join("%s: %s" % kv for kv in sorted(bad.items()))[:600])
        with _comp(t, "acoustic_empty_site_quiet"):
            if _live(t):
                if not got.get("sid"):
                    _unmeasured(t, "no sounder was staged (the pulse arm did not run)")
                _isolate(t, x, z)
                txt = _pulse_text(t, got["sid"])
                _note(t, "reading over the empty site", txt[:300])
                bad = _reading_offences(None, txt, quiet, targets)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "acoustic_checker_rejects_injections"):
            if _live(t):
                lab = targets[0]["label"]
                good = "intro\n%s\n" % targets[0]["reading"]
                if _reading_offences(lab, good, quiet, targets) or _reading_offences(None, quiet, quiet, targets):
                    _fail("the acoustic checker refuses clean readings")
                injected = {"strings only, no pulse": (lab, "", quiet, targets),
                            "target missing from its reading": (lab, quiet, quiet, targets),
                            "another target heard": (lab, good + targets[1]["reading"], quiet, targets),
                            "empty site not quiet": (None, targets[1]["reading"], quiet, targets)}
                missed = sorted(k for k, a in injected.items() if not _reading_offences(*a))
                if missed:
                    _fail("the acoustic checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_acoustic_payload", "immediate"):
        try:
            _stable(t, body)
        finally:
            for f, v in SCANNER_RESTORE:
                if got.get("scanner_settings"):
                    t.bridge_call("jawa/mod_settings_field", typeName=SCANNER_SETTINGS, action="set", field=f, value=str(v))


# the scanner's shipped values (AcousticScanner validation.py DEFAULTS), put back after the scene
SCANNER_RESTORE = (("requireLandedShip", True), ("cooldownHours", 24.0), ("rangeCells", 60.0))


def _isolate(t, x, z):
    """Only the sounder stays: the target plot is cleared and every pawn on the pad vanished (a surrik wanders)."""
    t.bridge_call("jawa/destroy_batch", rects="%d,%d,5,5" % (x + 8, z - 2), categories="All")
    _remove_pawns_in(t.bridge_call, _rs(_rect(t, PAD_SIZE + 8)))


def _scanner_site(t, x, z, got):
    """A powered, player-owned sounder at the pad centre; no landed ship, no cooldown and a 14-cell range (so the map's
    own sweetlines and hollows beyond the cleared pad stay out of the reading) for the scene; all restored."""
    got["scanner_settings"] = True
    for f, v in (("requireLandedShip", False), ("cooldownHours", 0.0), ("rangeCells", 14.0)):
        _ok(t.bridge_call("jawa/mod_settings_field", typeName=SCANNER_SETTINGS, action="set", field=f, value=str(v)),
            "scanner setting %s" % f)
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SOUNDER, x, z))
    s = _things(t, SOUNDER, _rs(_rect(t)))
    if not s:
        _unmeasured(t, "the sounder did not spawn on the pad")
    got["sid"] = s[0]["id"]
    t.bridge_call("jawa/set_thing_props", thing=got["sid"], faction="Player")
    t.bridge_call("jawa/power_net", thing=got["sid"], forcePowerOn=True)


# --------------------------------------------------------------------------- scene: concealment

RIPPLE_SMALL, RIPPLE_GALE_ONLY = "RM_Ribbonwhip", "RM_Shirrel"   # baseBodySize 0.25 (<= 0.6) and 0.7 (<= 0.6 x 2 in Gale)


@suite.chain("scene_concealment")
def scene_concealment(t):
    """sc_concealment (concealment): a small wild animal standing on fuzz is hidden (RM_RippleHidden) in ordinary
    wind while its twin on the bare lane is not; in the Stall it is hidden standing and seen the moment it moves; the
    Gale doubles the size it can hide (a shirrel hides only then); a manhunting one is never hidden; rippleEnabled off
    hides nobody. State reads only: the shimmer is the owner's Stage 8 look. Rules out a hediff that passes while wildlife
    stays hidden off cover or in a mental state."""
    _fuzz_patch(t)
    x, z = t.anchor
    bare = (x + FUZZ_PATCH // 2 + 4, z)

    def hid(pid):
        return _hidden(_rows(t, health=True).get(pid) or {})

    def on_fuzz(pid):
        px, pz = _xz(_rows(t).get(pid)) or (10 ** 6, 0)
        return abs(px - x) <= FUZZ_PATCH // 2 and abs(pz - z) <= FUZZ_PATCH // 2

    def body():
        ids = {}
        with _comp(t, "concealment_hides_on_cover", toggle="rippleEnabled"):
            if _live(t):
                ids["cover"] = _spawn(t, RIPPLE_SMALL, x, z)
                ids["bare"] = _spawn(t, RIPPLE_SMALL, *bare)
                _lock_weather(t, "RM_ScrubWind")
                t.wait_ticks(240)
                if not hid(ids["cover"]):
                    _fail("a %s standing on fuzz in ordinary wind is not hidden" % RIPPLE_SMALL)
        with _comp(t, "concealment_bare_lane_visible"):
            if _live(t):
                if hid(ids["bare"]):
                    _fail("a %s on bare ground (no cover plant) is hidden" % RIPPLE_SMALL)
        with _comp(t, "concealment_stall_move_reveals"):
            if _live(t):
                _lock_weather(t, "RM_Stall")
                t.wait_ticks(120)
                if not hid(ids["cover"]):
                    _unmeasured(t, "the still animal is not hidden in the Stall: nothing for movement to reveal")
                _order_goto(t, ids["cover"], x, z - FUZZ_PATCH // 2 + 1)   # a long walk across the fuzz, read mid-way
                t.wait_ticks(70)          # past one ripple pass (CheckInterval 60), well short of arrival
                if hid(ids["cover"]):
                    _fail("a %s moving in the Stall stays hidden" % RIPPLE_SMALL)
        with _comp(t, "concealment_gale_extends_size"):
            if _live(t):
                _lock_weather(t, "RM_ScrubWind")
                ids["big"] = _spawn(t, RIPPLE_GALE_ONLY, x - 3, z)
                with _setting(t, "shirrelGlideEnabled", False):    # a shirrel glides on the Gale: no unattended flight
                    t.wait_ticks(120)
                    calm = hid(ids["big"])
                    _lock_weather(t, "RM_Gale")
                    t.wait_ticks(120)
                    gale = hid(ids["big"])
                    _lock_weather(t, "RM_ScrubWind")
                _note(t, "shirrel hidden", {"wind": calm, "gale": gale})
                if calm or not gale:
                    _fail("a %s (bigger than rippleMaxBodySize, within twice it) hidden in wind=%s, in the Gale=%s: "
                          "the Gale should be the only time it hides" % (RIPPLE_GALE_ONLY, calm, gale))
        with _comp(t, "concealment_mental_state_not_hidden"):
            if _live(t):
                _lock_weather(t, "RM_ScrubWind")
                ids["mad"] = _spawn(t, RIPPLE_SMALL, x + 3, z)
                _ok(t.bridge_call("jawa/pawn_mental", pawn=ids["mad"], action="start", state="Manhunter"),
                    "pawn_mental(start Manhunter)")
                t.wait_ticks(120)
                if not on_fuzz(ids["mad"]):
                    _unmeasured(t, "the manhunter left the fuzz before the read: nothing tested")
                if hid(ids["mad"]):
                    _fail("a manhunting %s on fuzz is hidden: it could not be shot back" % RIPPLE_SMALL)
        with _comp(t, "concealment_toggle_off_nobody_hidden", toggle="rippleEnabled"):
            if _live(t):
                ids["ctl"] = _spawn(t, RIPPLE_SMALL, x - 2, z + 2)
                t.wait_ticks(120)
                if not hid(ids["ctl"]):
                    _unmeasured(t, "the control animal was not hidden before the toggle: nothing for it to switch off")
                with _setting(t, "rippleEnabled", False):
                    t.wait_ticks(120)
                    still = [k for k in ("ctl", "cover") if hid(ids[k])]
                    if still:
                        _fail("rippleEnabled off but %s still hidden" % still)
    with _scene(t, "sc_concealment", "immediate"):
        try:
            _stable(t, body)
        finally:
            _clear_fuzz_patch(t)


# --------------------------------------------------------------------------- scene: cane_fuel

CANE, WOOD = "RM_DeadVenomvine", "WoodLog"


def _fuel(t, tid):
    r = _ok(t.bridge_call("jawa/thing_refuel", thingId=tid, amount=0), "thing_refuel(%s)" % tid)
    if r.get("fuelAfter") is None:
        _unmeasured(t, "thing_refuel(%s) carries no fuelAfter" % tid)
    return float(r["fuelAfter"])


def _fuel_offences(arms):
    """The cane-fuel checker, pure. arms {"cane"|"wood"|"wood2": {"per_item": fuel per item burned, "rate": fuel per
    1000 ticks, "rise": room temperature rise}}. Cane pays more burn per equal count and heats harder per tick; the two
    matched wood arms read alike (the control). Ratios are recorded as tuning, never a bar."""
    out = []
    c, w, w2 = arms.get("cane") or {}, arms.get("wood") or {}, arms.get("wood2") or {}
    if not c.get("per_item") or not w.get("per_item"):
        return ["an arm burned no fuel item, so no per-item credit was measured"]
    if c["per_item"] <= w["per_item"] * 1.1:
        out.append("cane pays %.2f fuel per item against wood's %.2f: no longer burn per equal count"
                   % (c["per_item"], w["per_item"]))
    if c.get("rate") and w.get("rate") and c["rate"] > w["rate"] * 1.1:
        out.append("cane credit burns down faster (%.2f against %.2f per 1000 ticks)" % (c["rate"], w["rate"]))
    if c.get("rise") is not None and w.get("rise") is not None and c["rise"] <= w["rise"] + 0.3:
        out.append("the cane fire's room warmed %.1f C against wood's %.1f C: no heat bonus" % (c["rise"], w["rise"]))
    if w2.get("per_item") and abs(w2["per_item"] - w["per_item"]) > 0.05 * w["per_item"]:
        out.append("two matched wood fires disagree (%.2f vs %.2f per item): the meter is biased"
                   % (w["per_item"], w2["per_item"]))
    return out


@suite.chain("scene_cane_fuel")
def scene_cane_fuel(t):
    """sc_cane_fuel (cane_fuel, premium_dead_cane): three matched campfires burn half a day down, then a colonist refuels
    each through the real Refuel job: one with dead venomvine, two with wood logs (the control pair); then each fire is
    walled and roofed in where it stands (a 5x5 room at ambient). Read: fuel credited per item burned, burn-down rate, the room's temperature rise, and the cane
    fire's credit across a save and reload mid-burn. Cane must pay more burn per equal count, heat harder and keep its
    credit across the reload; the two wood fires must read alike. The 2x / 1.25x numbers are agent tuning, recorded,
    never a bar. A stove or generator pair is not staged; the campfire is the wood-filter consumer every colony has."""
    _prep(t, "fuel", 24)
    x, z = t.anchor
    rooms = {"cane": (x - 11, z - 4), "wood": (x - 1, z - 4), "wood2": (x + 9, z - 4)}
    fuel_of = {"cane": CANE, "wood": WOOD, "wood2": WOOD}
    arms, ids = {}, {}

    def body():
        with _comp(t, "cane_fires_staged", poison=True):
            if _live(t):
                for arm, (rx, rz) in sorted(rooms.items()):
                    t.bridge_call("jawa/spawn_batch", ops="Campfire:%d,%d" % (rx + 3, rz + 3))
                    fire = _things(t, "Campfire", "%d,%d,7,7" % (rx, rz))
                    if not fire:
                        _unmeasured(t, "no campfire in the %s room" % arm)
                    ids[arm] = fire[0]["id"]
                _wait(t, 30000)            # half a day: each fire burns ~5 of 20 and the Refuel job will take items
        with _comp(t, "cane_accepted_by_wood_filter"):
            if _live(t):
                for arm, (rx, rz) in sorted(rooms.items()):
                    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,10" % (fuel_of[arm], rx + 1, rz + 1))
                    stack = _things(t, fuel_of[arm], "%d,%d,7,7" % (rx, rz))
                    if not stack:
                        _unmeasured(t, "no %s stack spawned in the %s plot" % (fuel_of[arm], arm))
                    col = _spawn(t, "Colonist", rx + 5, rz + 5, faction="player")
                    _full(t, col)
                    f0, s0 = _fuel(t, ids[arm]), sum(int(s.get("stackCount") or 0) for s in stack)
                    t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="Refuel", targetAId=ids[arm],
                                  targetBId=stack[0]["id"], count=10, waitTicks=60)
                    t.wait_ticks(900)
                    f1 = _fuel(t, ids[arm])
                    s1 = sum(int(s.get("stackCount") or 0) for s in _things(t, fuel_of[arm], "%d,%d,7,7" % (rx, rz)))
                    arms[arm] = {"per_item": (f1 - f0) / (s0 - s1) if s0 > s1 else 0.0, "burned": s0 - s1, "fuel": f1}
                    _vanish(t, col)
                _note(t, "refuel per arm", arms)
                if not arms["cane"]["burned"]:
                    _fail("the colonist burned no dead venomvine in the campfire (fuel filter refuses it)")
        with _comp(t, "cane_more_burn_per_item"):
            if _live(t):
                bad = [b for b in _fuel_offences(dict((k, {"per_item": v.get("per_item")}) for k, v in arms.items()))
                       if "per equal count" in b or "burned no" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "cane_heat_rate_higher"):
            if _live(t):
                for rx, rz in rooms.values():      # walls and roof round each burning fire now: the rooms start at ambient
                    ring = ";".join("Wall:%d,%d" % (rx + i, rz + j) for i in range(7) for j in range(7) if i in (0, 6) or j in (0, 6))
                    t.bridge_call("jawa/spawn_batch", ops=ring, stuff="Steel")
                    t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,5,5" % (rx + 1, rz + 1))
                t0 = dict((a, _temp(t, rx + 1, rz + 5)) for a, (rx, rz) in rooms.items())
                f0 = dict((a, _fuel(t, ids[a])) for a in rooms)
                t.wait_ticks(1000)
                for a, (rx, rz) in rooms.items():
                    if a not in arms:
                        _unmeasured(t, "the %s arm was never refuelled" % a)
                    arms[a]["rise"] = _temp(t, rx + 1, rz + 5) - t0[a]
                    arms[a]["rate"] = f0[a] - _fuel(t, ids[a])
                _note(t, "heat and burn rate per arm", arms)
                if arms["wood"]["rise"] <= 0.2:
                    _unmeasured(t, "the wood room did not warm (%.2f C): no heat signal to compare" % arms["wood"]["rise"])
                bad = [b for b in _fuel_offences(arms) if "heat" in b or "faster" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "cane_credit_survives_reload"):
            if _live(t):
                before = _fuel(t, ids["cane"])
                name = "lscrub_cane_mid_%d" % int(time.time())
                _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game")
                _ok(t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000), "load_game_ready")
                after = _fuel(t, ids["cane"])
                _note(t, "cane fire across reload", {"before": before, "after": after})
                if abs(after - before) > 0.01:
                    _fail("the cane fire's credit changed across a save and reload: %.3f -> %.3f" % (before, after))
        with _comp(t, "cane_wood_control_alike"):
            if _live(t):
                bad = [b for b in _fuel_offences(arms) if "biased" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "cane_checker_rejects_injections"):
            if _live(t):
                good = {"cane": {"per_item": 2.0, "rate": 1.0, "rise": 6.0}, "wood": {"per_item": 1.0, "rate": 1.0, "rise": 4.0},
                        "wood2": {"per_item": 1.0}}
                if _fuel_offences(good):
                    _fail("the fuel checker refuses a clean reading: %s" % _fuel_offences(good))
                injected = {"premium multiplier one": dict(good, cane=dict(good["cane"], per_item=1.0)),
                            "heat factor one": dict(good, cane=dict(good["cane"], rise=4.0)),
                            "cane burns faster": dict(good, cane=dict(good["cane"], rate=2.0)),
                            "biased meter": dict(good, wood2={"per_item": 1.5}),
                            "nothing burned": dict(good, cane={"per_item": 0.0})}
                missed = sorted(k for k, a in injected.items() if not _fuel_offences(a))
                if missed:
                    _fail("the fuel checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_cane_fuel", "immediate"):
        _stable(t, body)


def _temp(t, x, z):
    r = _ok(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (x, z)), "cell_temperature(%d,%d)" % (x, z))
    v = r.get("temperature", r.get("celsius"))
    if v is None:
        _unmeasured(t, "cell_temperature(%d,%d) carries no temperature: %r" % (x, z, r))
    return float(v)


# --------------------------------------------------------------------------- scene: colony_walk

COLONY_SIZE = 40


def _walk_offences(trips, census_before, census_after, hurt):
    """The colony-walk checker, pure. trips [{"order", "out", "back", "fuel_gain"}]; the census {pawn id: True} before
    the save and after the reload; hurt [pawn ids dead, downed or marked]. -> offences."""
    out = []
    for tr in trips:
        if not tr.get("out") or not tr.get("back"):
            out.append("order %s: the expedition did not reach its spot and come home" % tr.get("order"))
        if not tr.get("fuel_gain") or tr["fuel_gain"] <= 0:
            out.append("order %s: the fuel run burned nothing" % tr.get("order"))
    if sorted(census_before or {}) != sorted(census_after or {}):
        out.append("the reloaded colony is not the saved one (%d pawns -> %d, ids differ)"
                   % (len(census_before or {}), len(census_after or {})))
    if len(census_before or {}) < COLONY_SIZE:
        out.append("only %d of %d colonists stood at the save" % (len(census_before or {}), COLONY_SIZE))
    if hurt:
        out.append("colonists hurt, downed or dead on ordinary work: %s" % sorted(hurt)[:6])
    return out


@suite.chain("scene_colony_walk")
def scene_colony_walk(t):
    """sc_colony_walk (colony_walk): forty fed colonists on the pad do ordinary deliberate work in two orders --
    order A an expedition out and home, then a dead-cane fuel run; save mid-way and reload that exact save (no actor is
    restaged); order B the fuel run first, then the expedition, by the SAME pawns. Both orders complete, the reloaded
    colony is the saved one, nobody is hurt. The claim, felt bank and wind-power parts of the walk are decided by their
    own scenes (smother, sweetline, gale); this scene is their ordinary-life frame."""
    _prep(t, "spawn", 24)
    x, z = t.anchor
    r = _rect(t)
    st = {"trips": []}

    def trip(order, who):
        _order_goto(t, who, x + 9, z + 9)
        t.wait_ticks(600)
        out = _dist(_xz(_rows(t).get(who)) or (0, 0), (x + 9, z + 9)) <= 2
        _order_goto(t, who, x - 9, z - 9)
        t.wait_ticks(600)
        back = _dist(_xz(_rows(t).get(who)) or (0, 0), (x - 9, z - 9)) <= 2
        return out, back

    def fuel_run(who):
        fire = st["fire"]
        f0 = _fuel(t, fire)
        stack = _things(t, CANE, _rs(r))
        if not stack:
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,10" % (CANE, x + 2, z - 9))
            stack = _things(t, CANE, _rs(r))
        t.bridge_call("jawa/ordered_job", pawnId=who, jobDef="Refuel", targetAId=fire, targetBId=stack[0]["id"],
                      count=10, waitTicks=60)
        t.wait_ticks(900)
        return _fuel(t, fire) - f0

    def body():
        with _comp(t, "walk_colony_staged", poison=True):
            if _live(t):
                st["pawns"] = [_spawn(t, "Colonist", r[0] + 1 + i % 8, r[1] + 1 + i // 8, faction="player")
                               for i in range(COLONY_SIZE)]
                for p in st["pawns"]:
                    _full(t, p)
                t.bridge_call("jawa/spawn_batch", ops="Campfire:%d,%d" % (x, z - 9))
                fire = _things(t, "Campfire", _rs(r))
                if not fire:
                    _unmeasured(t, "no campfire on the pad")
                st["fire"] = fire[0]["id"]
                _wait(t, 30000)            # the fire burns down so a Refuel job takes fuel
        with _comp(t, "walk_order_a_trip_then_fuel"):
            if _live(t):
                who = st["pawns"][0]
                out, back = trip("A", who)
                st["trips"].append({"order": "A", "out": out, "back": back, "fuel_gain": fuel_run(who)})
                bad = [b for b in _walk_offences(st["trips"][-1:], {}, {}, []) if "order" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "walk_save_reload_resumes"):
            if _live(t):
                rows = _rows(t)       # whole map: forty colonists wander off the pad over a day
                st["before"] = dict((pid, True) for pid in st["pawns"] if pid in rows and not rows[pid].get("dead"))
                name = "lscrub_walk_mid_%d" % int(time.time())
                _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game")
                _ok(t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000), "load_game_ready")
                rows = _rows(t)
                st["after"] = dict((pid, True) for pid in st["pawns"] if pid in rows and not rows[pid].get("dead"))
                bad = [b for b in _walk_offences([], st["before"], st["after"], []) if "reloaded" in b or "colonists" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "walk_order_b_fuel_then_trip"):
            if _live(t):
                who = st["pawns"][1]
                _wait(t, 15000)           # order A's run left the fire near full: the Refuel job ends at once on IsFull
                gain = fuel_run(who)
                out, back = trip("B", who)
                st["trips"].append({"order": "B", "out": out, "back": back, "fuel_gain": gain})
                bad = [b for b in _walk_offences(st["trips"][-1:], st["before"], st["before"], []) if "order" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "walk_nobody_hurt"):
            if _live(t):
                rows = _rows(t, health=True)
                hurt = [pid for pid in st["pawns"] if pid not in rows or rows[pid].get("dead") or rows[pid].get("downed")
                        or _lash_marks(rows[pid])]
                bad = [b for b in _walk_offences([], st["before"], st["before"], hurt) if "hurt" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "walk_checker_rejects_injections"):
            if _live(t):
                ids = dict((i, True) for i in range(COLONY_SIZE))
                ok_trip = [{"order": "A", "out": True, "back": True, "fuel_gain": 2.0}]
                if _walk_offences(ok_trip, ids, ids, []):
                    _fail("the walk checker refuses a clean walk: %s" % _walk_offences(ok_trip, ids, ids, []))
                injected = {"stranded expedition": ([dict(ok_trip[0], back=False)], ids, ids, []),
                            "fuel run burned nothing": ([dict(ok_trip[0], fuel_gain=0.0)], ids, ids, []),
                            "restaged after load": (ok_trip, ids, dict((i + 100, True) for i in ids), []),
                            "colonist downed": (ok_trip, ids, ids, [3])}
                missed = sorted(k for k, a in injected.items() if not _walk_offences(*a))
                if missed:
                    _fail("the walk checker passed injected walk(s) %s: it is blind there" % missed)
    with _scene(t, "sc_colony_walk", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: floor_runtime

OUR_PACKAGES = ("mandrake.rm.leaningscrub", "mandrake.rm.biomes")    # the dev folder, and the composed biome it ships in


def _ours(window):
    return [c for c in (window or {}).get("components") or [] if str(c.get("packageId") or "").lower() in OUR_PACKAGES]


def _runtime_refusals(idle, busy):
    """The runtime checker, pure: each window a map_comp_timing answer. Refuses a window with no ticks, degraded
    coverage, none of our components, or our components doing no work (zero calls; calls count ticks, so they say the
    counter is connected, not how much load there was). Timings are advisory: reported, never judged here."""
    out = []
    for name, w in (("idle", idle), ("busy", busy)):
        if not w or not w.get("ticksElapsed"):
            out.append("%s window: no ticks elapsed" % name)
            continue
        if w.get("coverage") != "ok":
            out.append("%s window: timer coverage %s" % (name, w.get("coverage")))
        ours = _ours(w)
        if not ours:
            out.append("%s window: none of our MapComponents was timed" % name)
        elif not sum(int(c.get("calls") or 0) for c in ours):
            out.append("%s window: our MapComponents made no calls (the work counter is disconnected)" % name)
    return out


def _timed(t, ticks):
    t.bridge_call("rimworld/set_time_speed", speed="3")
    try:
        return _ok(t.bridge_call("jawa/map_comp_timing", ticks=ticks, maxSeconds=300, top=60), "map_comp_timing")
    finally:
        t.bridge_call("rimworld/set_time_speed", speed="0")


@suite.chain("scene_floor_runtime")
def scene_floor_runtime(t):
    """floor_runtime (colony_walk): our MapComponents' production timers over an idle window and a busy one (armed
    venomvine across the pad, small wildlife on fuzz, eight wind turbines, forty colonists), each with its work counter
    (calls) and TickManager.MeanTickTime. The verdict refuses missing or disconnected counters and an empty load; the
    timing distributions are inherited advisory numbers, reported in notes. A cold-load median of three is a separately
    authorized measurement."""
    _prep(t, "spawn", 24)
    x, z = t.anchor
    r = _rect(t)
    win = {}

    def body():
        with _comp(t, "runtime_idle_window"):
            if _live(t):
                win["idle"] = _timed(t, 1200)
                win["idle_perf"] = t.bridge_call("jawa/time_perf")
                _note(t, "idle", {"ours": _ours(win["idle"]), "meanTickTime": (win["idle_perf"] or {}).get("meanTickTime")})
        with _comp(t, "runtime_busy_window"):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="RM_VenomvineThicket:%d,%d,%d,8" % (r[0], r[1], r[2]), growth=1.0)
                t.bridge_call("jawa/set_plants", ops="RM_Fuzz:%d,%d,%d,8" % (r[0], r[1] + 9, r[2]), growth=1.0)
                for i in range(20):
                    _spawn(t, RIPPLE_SMALL, r[0] + i, r[1] + 12)
                for i in range(8):
                    t.bridge_call("jawa/spawn_batch", ops="WindTurbine:%d,%d" % (r[0] + 2 + 3 * i, r[1] + 20))
                for i in range(COLONY_SIZE):
                    _full(t, _spawn(t, "Colonist", r[0] + i % 20, r[1] + 17 + i // 20, faction="player"))
                win["busy"] = _timed(t, 1200)
                win["busy_perf"] = t.bridge_call("jawa/time_perf")
                _note(t, "busy", {"ours": _ours(win["busy"]), "meanTickTime": (win["busy_perf"] or {}).get("meanTickTime")})
        with _comp(t, "runtime_work_counted"):
            if _live(t):
                bad = _runtime_refusals(win.get("idle"), win.get("busy"))
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "runtime_checker_refuses_missing_work"):
            if _live(t):
                ok = {"ticksElapsed": 1200, "coverage": "ok", "components": [{"packageId": OUR_PACKAGES[0], "calls": 40}]}
                busy = dict(ok, components=[{"packageId": OUR_PACKAGES[0], "calls": 80}])
                if _runtime_refusals(ok, busy):
                    _fail("the runtime checker refuses clean windows: %s" % _runtime_refusals(ok, busy))
                injected = {"counter disconnected": (ok, dict(ok, components=[{"packageId": OUR_PACKAGES[0], "calls": 0}])),
                            "empty map (none of ours)": (ok, dict(ok, components=[])),
                            "paused game": (ok, dict(busy, ticksElapsed=0)),
                            "degraded timers": (ok, dict(busy, coverage="degraded"))}
                missed = sorted(k for k, a in injected.items() if not _runtime_refusals(*a))
                if missed:
                    _fail("the runtime checker passed injected window(s) %s: it is blind there" % missed)
    with _scene(t, "floor_runtime", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: settings

SETTINGS_CS = os.path.join(HERE, "Source", "RM_LeaningScrubMod.cs")


def _cs_settings():
    """{field: (type, initialiser)} of every public static bool/float/int in RM_LeaningScrubSettings, the fields it
    serializes (Scribe_Values.Look) and the names its settings window names. -> (fields, scribed, in_ui)."""
    with open(SETTINGS_CS, encoding="utf-8") as fh:
        src = re.sub(r"//[^\n]*|/\*.*?\*/", "", fh.read(), flags=re.S)
    fields = dict((n, (ty, v.strip())) for ty, n, v in re.findall(r"public static (bool|float|int) (\w+)\s*=\s*([^;]+);", src))
    scribed = set(re.findall(r"Scribe_Values\.Look\(ref (\w+)", src))
    ui = src[src.index("DoWindowContents"):] if "DoWindowContents" in src else ""
    return fields, scribed, set(re.findall(r'"(\w+)"', ui)) | set(re.findall(r"nameof\((?:\w+\.)?(\w+)\)", ui))


def _cs_value(ty, v):
    if ty == "bool":
        return v == "true"
    return float(v.rstrip("fF")) if ty == "float" else int(v)


def _census_offences(fields, scribed, ui, defaults):
    """The settings census checker, pure. -> offences: a source field the suite's DEFAULTS lacks (or holds at another
    value), a DEFAULTS entry the source lacks, a field never serialized, a field the settings window never shows."""
    out = []
    for n, (ty, v) in sorted(fields.items()):
        if n not in defaults:
            out.append("%s ships in the source but not in the suite's DEFAULTS" % n)
        elif not _same(str(defaults[n]), _cs_value(ty, v)):
            out.append("%s: source default %s, DEFAULTS %r" % (n, v, defaults[n]))
        if n not in scribed:
            out.append("%s is never serialized (no Scribe_Values.Look)" % n)
        if n not in ui:
            out.append("%s has no control in the settings window" % n)
    out += ["%s is in DEFAULTS but not in the source" % n for n in sorted(set(defaults) - set(fields))]
    return out


@suite.chain("scene_settings")
def scene_settings(t):
    """sc_settings (colony_walk, settings): the census of every setting (source initialiser, serialization, window
    control, the suite's DEFAULTS, the live value); each toggle off and back on, read back; then every switch off
    together, master gate included, for 6000 ticks of ordinary colony life with a small animal on fuzz: colonists
    unharmed, nobody hidden; then the saved configuration back and its effect returns on a fresh animal. No flyer is
    staged (flight is never live-tested unattended; vanilla flight is not ours to gate).
    Not driven here: writing ModSettings.xml through the real window and reloading it (jawa/mod_settings_field never
    writes the file and rimworld/update_mod_settings cannot reach static fields); actual flight (the owner's scene)."""
    _fuzz_patch(t)
    x, z = t.anchor
    fields, scribed, ui = _cs_settings()
    toggles = sorted(n for n, (ty, _v) in fields.items() if ty == "bool")

    def body():
        ids = {}
        with _comp(t, "settings_census"):
            if _live(t):
                bad = _census_offences(fields, scribed, ui, DEFAULTS)
                live = dict((n, _get_setting(t, n)) for n in sorted(fields))
                bad += ["%s reads %r live, ships %s" % (n, live[n], fields[n][1]) for n in sorted(fields)
                        if not _same(live[n], _cs_value(*fields[n]))]
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "settings_each_toggle_off_and_on"):
            if _live(t):
                stuck = []
                for n in toggles:
                    for want in (False, True):
                        t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=n, value=str(want))
                        if not _same(_get_setting(t, n), want):
                            stuck.append("%s->%s" % (n, want))
                    _restore(t, n)
                if stuck:
                    _fail("toggle(s) that did not read back: %s" % stuck[:10])
        with _comp(t, "settings_all_off_quiet"):
            if _live(t):
                ids["small"] = _spawn(t, RIPPLE_SMALL, x, z)
                ids["cols"] = [_spawn(t, "Colonist", x - 4 + i, z - 5, faction="player") for i in range(3)]
                for c in ids["cols"]:
                    _full(t, c)
                try:
                    for n in toggles:
                        _set(t, n, False)
                    _wait(t, 6000)
                    rows = _rows(t, health=True)
                    bad = []
                    if _hidden(rows.get(ids["small"]) or {}):
                        bad.append("a small animal on fuzz is hidden with every switch off")
                    bad += ["colonist %s %s" % (c, "dead" if (rows.get(c) or {}).get("dead") else "downed or marked")
                            for c in ids["cols"] if c not in rows or rows[c].get("dead") or rows[c].get("downed")
                            or _lash_marks(rows[c])]
                    if bad:
                        _fail("; ".join(bad))
                finally:
                    for n in toggles:
                        _restore(t, n)
        with _comp(t, "settings_reenabled_effect_returns"):
            if _live(t):
                ids["fresh"] = _spawn(t, RIPPLE_SMALL, x + 1, z + 1)
                t.wait_ticks(120)
                if not _hidden(_rows(t, health=True).get(ids["fresh"]) or {}):
                    _fail("the saved configuration is back but the ripple did not return (a small animal on fuzz is "
                          "still seen)")
        with _comp(t, "settings_checker_rejects_injections"):
            if _live(t):
                f = {"aEnabled": ("bool", "true"), "bSize": ("float", "0.5f")}
                if _census_offences(f, {"aEnabled", "bSize"}, {"aEnabled", "bSize"}, {"aEnabled": True, "bSize": 0.5}):
                    _fail("the census checker refuses a clean census")
                injected = {"field missing from DEFAULTS": (f, set(f), set(f), {"aEnabled": True}),
                            "default drift": (f, set(f), set(f), {"aEnabled": False, "bSize": 0.5}),
                            "never serialized": (f, {"aEnabled"}, set(f), {"aEnabled": True, "bSize": 0.5}),
                            "no window control": (f, set(f), {"bSize"}, {"aEnabled": True, "bSize": 0.5}),
                            "stale DEFAULTS entry": (f, set(f), set(f), {"aEnabled": True, "bSize": 0.5, "gone": True})}
                missed = sorted(k for k, a in injected.items() if not _census_offences(*a))
                if missed:
                    _fail("the census checker passed injected census(es) %s: it is blind there" % missed)
    with _scene(t, "sc_settings", "immediate"):
        try:
            _stable(t, body)
        finally:
            _clear_fuzz_patch(t)


# --------------------------------------------------------------------------- scene: floor_persistence

def _saves_dir():
    from game_paths import LOCALLOW     # the one path seam (selftest_one_path_seam.py)
    return os.path.join(LOCALLOW, "Saves")


def _save_bytes(name):
    p = os.path.join(_saves_dir(), name + ".rws")
    return os.path.getsize(p) if os.path.exists(p) else None


def _persist_offences(cycles):
    """The persistence checker, pure. cycles [{"bytes": save size, "census": {def or pawn id: count}, "ids": [thing
    ids]}] -- the state before cycle 1, then after each reload. -> offences: identities or counts that change across a
    reload, a duplicate id, an unreadable save size, and save bytes that grow on every cycle (a retained-state leak)."""
    out = []
    if len(cycles) < 4:
        return ["%d readings; the scene needs the start plus three cycles" % len(cycles)]
    base = cycles[0]
    for i, c in enumerate(cycles[1:], 1):
        if c.get("census") != base.get("census"):
            out.append("cycle %d: the census changed across save/reload: %s -> %s"
                       % (i, json.dumps(base.get("census"))[:120], json.dumps(c.get("census"))[:120]))
        ids = c.get("ids") or []
        if len(ids) != len(set(ids)):
            out.append("cycle %d: a duplicated thing id after reload" % i)
    sizes = [c.get("bytes") for c in cycles[1:]]
    if any(s is None for s in sizes):
        out.append("a save's size was unreadable: %s" % sizes)
    elif all(b > a * 1.005 for a, b in zip(sizes, sizes[1:])):
        out.append("the save grows on every cycle with an unchanged census: %s" % sizes)
    return out


@suite.chain("scene_floor_persistence")
def scene_floor_persistence(t):
    """floor_persistence (colony_walk): a mid-journey colony (colonists, a fuzz patch, a burning dead-cane fire) saved
    and reloaded three times: identities and counts persist, no id duplicates, and the save does not grow cycle on
    cycle. Not driven here: the 30 compressed production lifecycle cycles and texture memory (no profiler bridge tool),
    and adding the mod to a prior unmodded save (no such fixture is staged by this suite)."""
    _fuzz_patch(t)
    x, z = t.anchor
    rect = _rs(_rect(t, PAD_SIZE + 8))
    cycles = []

    def census():
        ids, counts = [], {}
        for d in ("RM_Fuzz", "Campfire", CANE):
            for th in _things(t, d, rect, 2000):
                ids.append(th.get("id"))
                counts[d] = counts.get(d, 0) + int(th.get("stackCount") or 1)
        for pid, p in _rows(t, rect=rect).items():
            ids.append(pid)
            counts[pid] = bool(p.get("dead"))
        return counts, ids

    def body():
        with _comp(t, "persist_three_cycles"):
            if _live(t):
                for i in range(2):
                    _full(t, _spawn(t, "Colonist", x - 3 + i, z - 3, faction="player"))
                t.bridge_call("jawa/spawn_batch", ops="Campfire:%d,%d" % (x + 3, z + 3))
                t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,5" % (CANE, x + 5, z + 3))
                counts, ids = census()
                cycles.append({"bytes": None, "census": counts, "ids": ids})
                for i in range(3):
                    name = "lscrub_persist_%d_%d" % (i, int(time.time()))
                    _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game(%s)" % name)
                    size = _save_bytes(name)
                    _ok(t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000), "load_game_ready")
                    counts, ids = census()
                    cycles.append({"bytes": size, "census": counts, "ids": ids})
                _note(t, "cycles", [{"bytes": c["bytes"], "things": len(c["ids"])} for c in cycles])
                bad = [b for b in _persist_offences(cycles) if "grows" not in b and "unreadable" not in b]
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "persist_no_growth"):
            if _live(t):
                if any(c["bytes"] is None for c in cycles[1:]):
                    _unmeasured(t, "save sizes unreadable under %s" % _saves_dir())
                bad = [b for b in _persist_offences(cycles) if "grows" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "persist_checker_detects_leaks"):
            if _live(t):
                c0 = {"bytes": None, "census": {"RM_Fuzz": 4}, "ids": ["a", "b"]}
                ok = [c0] + [dict(c0, bytes=1000)] * 3
                if _persist_offences(ok):
                    _fail("the persistence checker refuses clean cycles: %s" % _persist_offences(ok))
                injected = {"retained-state leak": [c0] + [dict(c0, bytes=b) for b in (1000, 1100, 1200)],
                            "duplicated claim": [c0] + [dict(c0, bytes=1000, ids=["a", "a"])] * 3,
                            "lost thing": [c0] + [dict(c0, bytes=1000, census={"RM_Fuzz": 3})] * 3,
                            "two cycles only": ok[:3]}
                missed = sorted(k for k, a in injected.items() if not _persist_offences(a))
                if missed:
                    _fail("the persistence checker passed injected cycle(s) %s: it is blind there" % missed)
    with _scene(t, "floor_persistence", "immediate"):
        try:
            _stable(t, body)
        finally:
            _clear_fuzz_patch(t)


# =========================================================================== scenes, batch 3 (Stage 3, 2026-11-16)
# sc_crown, sc_cruststar, sc_creep, sc_removed_save_preservation, floor_payload, floor_recovery
# (design/concepts/LeaningScrub/scenes.json). Each scene is UNRUN in game until Stage 6; each keeps its verdict in a pure
# checker the scene also shows refusing injected bad readings.


def _growth(t, tid):
    """A plant's growth (0..1) off vanilla Plant.GetInspectString's "<N>% grown" line; list_things carries no growth."""
    _label, lines = _inspect(t, tid)
    for ln in lines:
        m = re.match(r"\s*(\d+)% grown", str(ln))
        if m:
            return int(m.group(1)) / 100.0
        if re.match(r"\s*Mature\b", str(ln)):     # vanilla prints "Mature." instead of "100% grown" (LIVE: the twitcher stand, lash chain)
            return 1.0
    _unmeasured(t, "inspect_string(%s) carries no '%% grown' or 'Mature' line: %s" % (tid, lines[:3]))


def _vec2(text):
    """(x, z) off a Unity Vector2 rendered as text, e.g. "(0.71, -0.71)"; None when unreadable."""
    nums = re.findall(r"-?\d+(?:\.\d+)?", str(text or ""))
    return (float(nums[0]), float(nums[1])) if len(nums) >= 2 else None


def _resolves(t, want):
    """The subset of `want` ("Type/defName") the running game resolves, read off get_defs' notFound (an empty answer
    with no notFound list is UNMEASURED, never "all found")."""
    if not want:
        return set()
    r = _ok(t.bridge_call("jawa/get_defs", defs=";".join(want), fields="label", limit=500), "get_defs(%d defs)" % len(want))
    if r.get("notFound") is None:
        _unmeasured(t, "get_defs answered no notFound list: resolution unreadable")
    gone = set(str(n) for n in r["notFound"])
    return set(w for w in want if w not in gone and w.split("/", 1)[1] not in gone)


# --------------------------------------------------------------------------- scene: crown

def _crown_ext():
    """(maxMobbers, settleRadius) of RM_CrownVenomvine's RM_StallMobExtension, read off the def."""
    with open(os.path.join(HERE, "Defs", "ThingDefs_Plants", "RM_LeaningScrubVenomvineForms.xml"), encoding="utf-8") as fh:
        txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
    m = re.search(r"<defName>RM_CrownVenomvine</defName>.*?RM_StallMobExtension\">(.*?)</li>", txt, re.S)
    return (int(re.search(r"<maxMobbers>(\d+)</maxMobbers>", m.group(1)).group(1)),
            float(re.search(r"<settleRadius>([\d.]+)</settleRadius>", m.group(1)).group(1)))


CROWN_CAP, CROWN_SETTLE = _crown_ext()
CROWN_NEAR = CROWN_SETTLE + 1     # RM_MapComponent_CrownMob's settleSq is (settleRadius + 1)^2


def _crown_sample(rows, jobs, stand, busy=None):
    """One read of the cohort: flutters within CROWN_NEAR of the stand (held), flutters on a Goto elsewhere (in transit;
    the mob's TrySendToStand gives a plain Goto), and where the busy flutter is."""
    held, transit = [], []
    for pid, r in rows.items():
        if r.get("kindDef") != "RM_Dustflutter" or r.get("dead") or pid == busy:
            continue
        xz = _xz(r)
        if xz and _dist(xz, stand) <= CROWN_NEAR:
            held.append(pid)
        elif jobs.get(pid) == "Goto":
            transit.append(pid)
    return {"held": sorted(held), "transit": sorted(transit), "busy_at": _xz(rows.get(busy)) if busy else None}


def _crown_cap_offences(samples, cap):
    over = [(i, len(s["held"]) + len(s["transit"])) for i, s in enumerate(samples)
            if len(s["held"]) + len(s["transit"]) > cap]
    return ["residents plus in-transit flutters passed the cap of %d: %s (sample, count)" % (cap, over[:4])] if over else []


def _crown_arrival_offences(samples):
    first = {}
    for i, s in enumerate(samples):
        for p in s["transit"]:
            first.setdefault(p, i)
    arrived = sorted(p for p, i in first.items() if any(p in s["held"] for s in samples[i + 1:]))
    return [] if len(arrived) >= 2 else ["%d attributed crown arrival(s) (a flutter seen on its way, then at the stand); "
                                         "nearby wanderers do not count" % len(arrived)]


def _crown_busy_offences(samples, goal):
    if any(s.get("busy_at") and _dist(s["busy_at"], goal) <= 2 for s in samples):
        return []
    return ["the busy flutter never reached its own goal %s: the mob took it off its job" % (goal,)]


def _crown_control_offences(samples):
    drawn = sorted(set(p for s in samples for p in s["transit"]))
    return ["crown-directed gathering with the mob off: %s on a Goto" % drawn[:6]] if drawn else []


@suite.chain("scene_crown")
def scene_crown(t):
    """sc_crown (crown, crown_mob): a crown stand in the Stall, CROWN_CAP + 6 idle wild dustflutters inside its draw
    radius and one busy flutter on an ordered walk away from it. Arrivals are attributed (seen on the mob's Goto, then at
    the stand); residents plus flutters in transit never pass the cap, before or after a save/reload taken while flutters
    are on their way; the busy flutter reaches its own goal. Control: the same cohort with crownMobEnabled off sends
    nobody (wanderers near the stand are not gathering). The mob launches flyers (RM_Flight.TryLaunch), so the scene
    runs only with the owner present (LSCRUB_OWNER_PRESENT=1; CLAUDE.md flyer rule) and holds its end state for him."""
    _prep(t, "crown")
    x, z = t.anchor
    stand = (x, z)
    goal = (x - 12, z - 10)
    got = {"samples": [], "reload": []}

    def cohort():
        ids = []
        for i in range(CROWN_CAP + 6):
            p = _spawn(t, "RM_Dustflutter", x + 10 + i % 6, z - 9 + 3 * (i // 6))
            _full(t, p)
            ids.append(p)
        return ids

    def sample(n, busy=None, into=None):
        for _ in range(n):
            t.wait_ticks(250)
            s = _crown_sample(_rows(t), _jobs(t), stand, busy)
            into.append(s)
        return into

    def body():
        with _comp(t, "crown_scene_flight_attended", poison=True):
            if _live(t) and not OWNER_PRESENT:
                _unmeasured(t, "the crown mob launches dustflutters into flight: the scene runs only with the owner "
                               "present (LSCRUB_OWNER_PRESENT=1 in a joint sitting; CLAUDE.md flyer rule)")
        with _comp(t, "crown_scene_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_Stall")
                t.bridge_call("jawa/set_plants", ops="RM_CrownVenomvine:%d,%d,1,1" % stand, growth=1.0)
                if not _count(t, "RM_CrownVenomvine", "%d,%d,1,1" % stand):
                    _unmeasured(t, "the crown stand did not stand after set_plants")
        with _comp(t, "crown_scene_toggle_off_quiet", toggle="crownMobEnabled"):
            if _live(t):
                with _setting(t, "crownMobEnabled", False):
                    cohort()
                    off = sample(6, into=[])
                _remove_pawns_in(t.bridge_call, _rs(_rect(t, PAD_SIZE + 8)))
                _note(t, "crown off", [(len(s["held"]), len(s["transit"])) for s in off])
                bad = _crown_control_offences(off)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "crown_scene_arrivals_attributed", toggle="crownMobEnabled"):
            if _live(t):
                cohort()
                busy = _spawn(t, "RM_Dustflutter", x - 12, z)
                _full(t, busy)
                _order_goto(t, busy, goal[0], goal[1])
                got["busy"] = busy
                sample(2, busy, got["samples"])
                if got["samples"][-1]["transit"]:
                    got["save"] = "lscrub_crown_en_route_%d" % int(time.time())
                    _ok(t.bridge_call("rimworld/save_game", saveName=got["save"]), "save_game(%s)" % got["save"])
                sample(6, busy, got["samples"])
                _note(t, "crown on", [(len(s["held"]), len(s["transit"])) for s in got["samples"]])
                bad = _crown_arrival_offences(got["samples"])
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "crown_scene_busy_job_intact"):
            if _live(t):
                bad = _crown_busy_offences(got["samples"], goal)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "crown_scene_cap_held_across_reload"):
            if _live(t):
                if not got.get("save"):
                    _unmeasured(t, "no flutter was in transit at the save point: the reload arm has nobody en route")
                _ok(t.bridge_call("rimworld/load_game_ready", saveName=got["save"], timeoutMs=240000), "load_game_ready")
                sample(4, got.get("busy"), got["reload"])
                _note(t, "crown after reload", [(len(s["held"]), len(s["transit"])) for s in got["reload"]])
                bad = _crown_cap_offences(got["samples"] + got["reload"], CROWN_CAP)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "crown_scene_checker_rejects_injections"):
            if _live(t):
                s = lambda h, tr, b=None: {"held": h, "transit": tr, "busy_at": b}
                ok = [s([], ["a", "b"], (0, 0)), s(["a", "b"], [], goal)]
                if _crown_cap_offences(ok, 2) or _crown_arrival_offences(ok) or _crown_busy_offences(ok, goal):
                    _fail("the crown checker refuses a clean run")
                injected = {
                    "second wave over the cap": _crown_cap_offences(ok + [s(["a", "b"], ["c"])], 2),
                    "nearby wanderers counted as gathering": _crown_arrival_offences([s(["a", "b"], [])]),
                    "resident later sent counted as arrival": _crown_arrival_offences([s(["a", "b"], []), s([], ["a", "b"])]),
                    "busy flutter hijacked": _crown_busy_offences([s(["a"], [], (0, 0))], goal),
                    "control drew a flutter": _crown_control_offences([s([], ["a"])]),
                }
                missed = sorted(k for k, v in injected.items() if not v)
                if missed:
                    _fail("the crown checker passed injected run(s) %s: it is blind there" % missed)
    with _scene(t, "sc_crown", "owner_review" if OWNER_PRESENT else "immediate"):    # no hold for a scene that never ran
        _stable(t, body)


# --------------------------------------------------------------------------- scene: cruststar

CRUST, WEEVIL, CRUST_ALT = "RM_Cruststar", "RM_Crustweevil", "Plant_Grass"   # Plant_Grass: the equal everyday graze


def _graze_offences(start, samples):
    """The grazing checker, pure. start/samples {"food": need level, "crust": summed cruststar growth, "alt": summed
    grass growth}. -> offences: no cruststar debit; a debit with no nutrition gained; the alternative eaten instead.
    Mere ingestibility is never evidence: only a debit the weevil's food agrees with is."""
    if not samples:
        return ["no sample was read"]
    debit = [i for i, s in enumerate(samples) if s["crust"] < start["crust"] - 0.2]
    out = []
    if not debit:
        alt = any(s["alt"] < start["alt"] - 0.2 for s in samples)
        out.append("no cruststar was grazed in %d samples%s" % (len(samples), " (it grazed the grass instead)" if alt else ""))
    elif max(s["food"] for s in samples[debit[0]:]) < start["food"] + 0.1:
        out.append("the cruststar was debited (%.2f -> %.2f) but the weevil's food did not rise (%.2f -> %.2f)"
                   % (start["crust"], samples[debit[0]]["crust"], start["food"], samples[-1]["food"]))
    return out


@suite.chain("scene_cruststar")
def scene_cruststar(t):
    """sc_cruststar (cruststar, cruststar_grazing_ecology): a hungry native crustweevil between a mature cruststar
    patch and an equal grass patch chooses the lichen: the cruststar is debited, the weevil's food rises with it, and
    the debited cruststar recovers on its own. Control: a hungry weevil walled away from the patch leaves it untouched
    (unrelated meals are not evidence). Grazing is not built in C# today (RM_Cruststar is PlantBaseNonEdible with
    Nutrition 0, RM_LeaningScrubFuzzFlora.xml), so this scene is expected red at Stage 6 until it is."""
    _prep(t, "dripping")
    x, z = t.anchor
    patch, alt = (x + 4, z - 1, 3, 3), (x - 6, z - 1, 3, 3)
    got = {}

    def resource(rect, d):
        return sum(_growth(t, th.get("id")) for th in _things(t, d, _rs(rect), 50))

    def read(pid):
        return {"food": _food(t, pid), "crust": resource(patch, CRUST), "alt": resource(alt, CRUST_ALT)}

    def body():
        with _comp(t, "cruststar_scene_site", poison=True):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,%d,%d" % ((CRUST,) + patch), growth=1.0)
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,%d,%d" % ((CRUST_ALT,) + alt), growth=1.0)
                if not _count(t, CRUST, _rs(patch)) or not _count(t, CRUST_ALT, _rs(alt)):
                    _unmeasured(t, "the cruststar or the grass patch did not stand after set_plants")
        with _comp(t, "cruststar_scene_unreachable_untouched"):
            if _live(t):
                t.bridge_call("jawa/make_empty_room", rect="%d,%d,5,5" % (x - 2, z + 8))
                walled = _hungry(t, WEEVIL, x, z + 10)
                c0 = resource(patch, CRUST)
                t.wait_ticks(3000)
                c1 = resource(patch, CRUST)
                _vanish(t, walled)
                if c1 < c0 - 0.2:
                    _fail("a crustweevil walled away from the patch debited the cruststar (%.2f -> %.2f)" % (c0, c1))
        with _comp(t, "cruststar_scene_grazed_and_fed"):
            if _live(t):
                pid = _hungry(t, WEEVIL, x, z)
                got["pid"], got["start"], got["samples"] = pid, read(pid), []
                for _ in range(24):
                    t.wait_ticks(250)
                    got["samples"].append(read(pid))
                    s = got["samples"][-1]
                    if s["crust"] < got["start"]["crust"] - 0.2 and s["food"] >= got["start"]["food"] + 0.1:
                        break
                _note(t, "cruststar graze", {"start": got["start"], "last": got["samples"][-1]})
                bad = _graze_offences(got["start"], got["samples"])
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "cruststar_scene_resource_recovers"):
            if _live(t):
                after = got["samples"][-1]["crust"]
                if after >= got["start"]["crust"] - 0.2:
                    _unmeasured(t, "no debit to recover from (the grazing component says why)")
                _vanish(t, got["pid"])
                t.wait_ticks(6000)
                now = resource(patch, CRUST)
                _note(t, "cruststar recovery", {"debited": after, "6000 ticks later": now})
                if now <= after:
                    _fail("the grazed cruststar did not recover over 6000 ticks (%.2f -> %.2f)" % (after, now))
        with _comp(t, "cruststar_scene_checker_rejects_injections"):
            if _live(t):
                st = {"food": 0.05, "crust": 9.0, "alt": 9.0}
                ok = [{"food": 0.05, "crust": 9.0, "alt": 9.0}, {"food": 0.6, "crust": 8.2, "alt": 9.0}]
                if _graze_offences(st, ok):
                    _fail("the grazing checker refuses a clean graze: %s" % _graze_offences(st, ok))
                injected = {"ate the grass instead": [{"food": 0.6, "crust": 9.0, "alt": 8.0}],
                            "debit without nutrition": [{"food": 0.05, "crust": 8.0, "alt": 9.0}],
                            "edible but never grazed": [{"food": 0.05, "crust": 9.0, "alt": 9.0}] * 3}
                missed = sorted(k for k, v in injected.items() if not _graze_offences(st, v))
                if missed:
                    _fail("the grazing checker passed injected graze(s) %s: it is blind there" % missed)
    with _scene(t, "sc_cruststar", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: creep

THICKET = "RM_VenomvineThicket"
CREEP_SWEEP = 15000          # RM_MapComponent_VenomvineCreep.SweepTicks; its tick runs at (TicksGame + uniqueID*1777) % it
CREEP_DX = (1, 1, 0, -1, -1, -1, 0, 1)
CREEP_DZ = (0, 1, 1, 1, 0, -1, -1, -1)
# Emitter B's eight neighbours, one protection each (RM_VenomvineIslandsUtil.NaturalFree): roof, building, zone, floor
# and tree. A sown plant is not staged (no bridge tool sows); NaturalFree's `p.sown` refusal is offline only.
CREEP_GUARDS = ("roof", "wall", "zone", "floor", "tree", "roof", "wall", "floor")
EG_ROSTER = "RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef/RM_LeaningScrub_VenomvineExempt"
VINE_CLOCK_OWN = (THICKET, "RM_DrippingVenomvine", "RM_TwitcherVenomvine", "RM_HollowVenomvine",
                  "RM_CrownVenomvine") + FORM_PLANTS


def _creep_offences(emitters, runners, guarded, downwind):
    """The creep checker, pure. emitters [(x, z)]; runners {(x, z): growth} new thicket cells after the sweeps;
    guarded {(x, z): thicket count now} on protected cells; downwind (dx, dz). -> offences: no runner; a runner not
    beside an emitter or armed (growth >= 0.5); a protected cell taken; runners no more downwind than a uniform pick."""
    out = []
    if not runners:
        return ["no runner after the compressed sweeps"]
    for c, g in sorted(runners.items()):
        if not any(max(abs(c[0] - e[0]), abs(c[1] - e[1])) == 1 for e in emitters):
            out.append("runner at %s is not beside an emitter" % (c,))
        if g >= 0.5:
            out.append("runner at %s is armed at growth %.2f (a runner starts young)" % (c, g))
    taken = sorted(c for c, n in guarded.items() if n)
    if taken:
        out.append("venomvine took protected cell(s) %s" % taken[:6])
    if downwind is None or not any(downwind):
        out.append("no downwind vector to judge the runners' lean against")
        return out
    dot = lambda c, e: (c[0] - e[0]) * downwind[0] + (c[1] - e[1]) * downwind[1]
    uniform = len([1 for dx, dz in zip(CREEP_DX, CREEP_DZ) if dx * downwind[0] + dz * downwind[1] > 0]) / 8.0
    near = lambda c: min(emitters, key=lambda e: _dist(c, e))
    share = len([c for c in runners if dot(c, near(c)) > 0]) / float(len(runners))
    if share <= uniform:
        out.append("runners lean downwind no more than a uniform pick (%.2f <= %.2f)" % (share, uniform))
    return out


def _eg_offences(exempt, band, own=VINE_CLOCK_OWN):
    """Both Explosive Growth paths (soak and everyday band) must leave every venomvine on its own clock."""
    out = []
    for name, roster in (("exemptPlants (soak)", exempt), ("bandExemptPlants (band)", band)):
        if roster is None:
            out.append("%s unreadable" % name)
            continue
        miss = sorted(set(own) - set(roster))
        if miss:
            out.append("%s lacks %s" % (name, miss[:6]))
    return out


@suite.chain("scene_creep")
def scene_creep(t):
    """sc_creep (creep, vine_creep, vine_growth_exemption): six mature thicket emitters on natural soil and one more
    ringed by protected cells (roof, wall, stockpile zone, plank floor, tree). The runner interval is compressed
    (venomvineCreepDays 0.01, so a sweep's runner chance is ~1) and the clock is moved to three ticks short of the
    map's own creep sweep, which then runs on its real tick: runners are young (under half grown, unarmed), beside an
    emitter, lean downwind more than a uniform pick, and never take a protected cell. Controls, counted map-wide and
    only after the on arm reached the test emitters: creep off lays nothing; the cap set to today's share lays nothing. Explosive Growth: the live roster def lists every venomvine in both
    exemption paths (soak and band), so the vine keeps its own clock. Not driven here: a real soak/band growth pass
    (RM_ExplosiveGrowthAPI.Soak takes a Map, which jawa/static_call cannot pass), Explosive Growth absent (an
    integration-absent list), a smothered emitter, a sown neighbour, and half-growth contact (the vine_contact scene's)."""
    _prep(t, "smother")
    x, z = t.anchor
    emitters = [(x - 10 + 4 * k, z - 6) for k in range(6)]
    guarded_at = (x, z + 6)
    guard_cells = [(guarded_at[0] + dx, guarded_at[1] + dz) for dx, dz in zip(CREEP_DX, CREEP_DZ)]
    got = {}

    def thickets():
        return dict(((int(th.get("x")), int(th.get("z"))), th.get("id")) for th in _things(t, THICKET, _rs(_rect(t)), 500))

    def sweep():
        mid, now = _map_id(t), _game_tick(t)
        nxt = now + (CREEP_SWEEP - (now + int(mid) * 1777) % CREEP_SWEEP)
        _ok(t.bridge_call("jawa/time_set_ticks", ticks=int(nxt - 3), timeException=True,
                          why="sc_creep: compress the six-hour creep sweep"), "time_set_ticks")
        t.wait_ticks(6)

    def creep_state():
        r = _ok(t.bridge_call("jawa/map_comp_read", comp="RM_MapComponent_VenomvineCreep",
                              members="Applies,openCells,vineCells"), "map_comp_read(VenomvineCreep)")
        return r.get("values") or {}

    def body():
        with _comp(t, "creep_scene_site", poison=True):
            if _live(t):
                for e in emitters + [guarded_at]:
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % ((THICKET,) + e), growth=1.0)
                for (cx, cz), g in zip(guard_cells, CREEP_GUARDS):
                    if g == "roof":
                        t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,1,1" % (cx, cz))
                    elif g == "wall":
                        t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (cx, cz), stuff="Steel")
                    elif g == "zone":
                        t.bridge_call("jawa/map_zones", action="createZone", zoneType="stockpile", rect="%d,%d,1,1" % (cx, cz))
                    elif g == "floor":
                        t.bridge_call("jawa/set_terrain_batch", ops="WoodPlankFloor:%d,%d,1,1" % (cx, cz), layer="top")
                    else:
                        t.bridge_call("jawa/set_plants", ops="Plant_TreeOak:%d,%d,1,1" % (cx, cz), growth=1.0)
                have = thickets()
                if any(e not in have for e in emitters + [guarded_at]):
                    _unmeasured(t, "an emitter did not stand after set_plants: %s" % sorted(have)[:8])
                if not _as_bool(creep_state().get("Applies")):
                    _unmeasured(t, "RM_MapComponent_VenomvineCreep.Applies is false: not a Leaning Scrub map")
                got["wind"] = _vec2(_ok(t.bridge_call("jawa/map_comp_read", comp="RM_MapComponent_Lean",
                                                      members="Downwind"), "map_comp_read(Lean)").get("values", {}).get("Downwind"))
                got["before"] = set(thickets())
        with _comp(t, "creep_scene_runners_young_downwind", toggle="venomvineCreepEnabled"):
            if _live(t):
                n0 = _count_all(t, THICKET)
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", 1.0):
                    sweep()
                    sweep()
                now = thickets()
                runners = dict((c, _growth(t, now[c])) for c in sorted(set(now) - got["before"]) if c not in guard_cells)
                guarded = dict((c, 1 if c in now else 0) for c in guard_cells)
                got["runners"] = runners
                if not runners and _count_all(t, THICKET) > n0:
                    _unmeasured(t, "the sweeps laid runners elsewhere on the map but none beside the test emitters (a "
                                   "sweep spends maxRunnersPerSweep on stands in list order): SITE, not the mod")
                _note(t, "creep runners", {"runners": sorted(runners.items())[:12], "downwind": got.get("wind")})
                if got.get("wind") is None or not any(got["wind"]):
                    _unmeasured(t, "RM_MapComponent_Lean.Downwind unreadable or zero: the lean cannot be judged")
                bad = [b for b in _creep_offences(emitters, runners, guarded, got["wind"]) if "protected" not in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "creep_scene_protected_cells_kept"):
            if _live(t):
                now = thickets()
                taken = sorted(c for c in guard_cells if c in now)
                if taken:
                    _fail("venomvine took protected cell(s) %s (%s)" % (
                        taken, [CREEP_GUARDS[guard_cells.index(c)] for c in taken]))
        with _comp(t, "creep_scene_toggle_off_quiet", toggle="venomvineCreepEnabled"):
            if _live(t):
                if not got.get("runners"):
                    _unmeasured(t, "no sweep reached the test emitters with creep on: an off arm laying nothing proves nothing")
                n0 = _count_all(t, THICKET)          # the whole map: a sweep spends its runners in list order
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", 1.0), \
                        _setting(t, "venomvineCreepEnabled", False):
                    sweep()
                n1 = _count_all(t, THICKET)
                if n1 > n0:
                    _fail("venomvineCreepEnabled OFF but the sweep laid %d runner(s) on the map" % (n1 - n0))
        with _comp(t, "creep_scene_cap_stops", toggle="venomvineCreepEnabled"):
            if _live(t):
                st = creep_state()
                try:
                    open_cells, vine = int(st.get("openCells")), int(st.get("vineCells"))
                except (TypeError, ValueError):
                    open_cells, vine = 0, 0
                if open_cells <= 0 or not got.get("runners"):
                    _unmeasured(t, "openCells unread (%r) or no runner seen with creep on: a cap arm laying nothing "
                                   "proves nothing" % st)
                n0 = _count_all(t, THICKET)
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", vine / float(open_cells)):
                    sweep()
                n1 = _count_all(t, THICKET)
                if n1 > n0:
                    _fail("the cap was set to today's share (%d of %d) but the sweep laid %d runner(s) on the map"
                          % (vine, open_cells, n1 - n0))
        with _comp(t, "creep_scene_explosive_growth_exempt"):
            if _live(t):
                rows, _r = _get_defs(t, EG_ROSTER, "exemptPlants,bandExemptPlants")
                row = rows.get("RM_LeaningScrub_VenomvineExempt")
                if row is None:
                    _fail("the venomvine exemption roster RM_LeaningScrub_VenomvineExempt did not load")
                as_list = lambda v: v if isinstance(v, list) else None
                bad = _eg_offences(as_list(row.get("exemptPlants")), as_list(row.get("bandExemptPlants")))
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "creep_scene_checker_rejects_injections"):
            if _live(t):
                em, wind = [(0, 0)], (1.0, 0.0)
                ok = {(1, 0): 0.05, (1, 1): 0.05}
                if _creep_offences(em, ok, {(0, 5): 0}, wind) or _eg_offences(VINE_CLOCK_OWN, VINE_CLOCK_OWN):
                    _fail("the creep checker refuses a clean sweep")
                injected = {"runner armed": _creep_offences(em, {(1, 0): 0.6}, {}, wind),
                            "existing plant counted as runner": _creep_offences(em, {(5, 5): 0.05}, {}, wind),
                            "protected cell taken": _creep_offences(em, ok, {(0, 5): 1}, wind),
                            "upwind runners": _creep_offences(em, {(-1, 0): 0.05, (-1, 1): 0.05}, {}, wind),
                            "no runner": _creep_offences(em, {}, {}, wind),
                            "band path not exempt": _eg_offences(VINE_CLOCK_OWN, VINE_CLOCK_OWN[1:])}
                missed = sorted(k for k, v in injected.items() if not v)
                if missed:
                    _fail("the creep checker passed injected sweep(s) %s: it is blind there" % missed)
    with _scene(t, "sc_creep", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: removed_save_preservation

def _def_blocks(root=None):
    """[(tag, defName, body, file)] for every concrete top-level def in this mod's Defs/ (any def type)."""
    out = []
    for path in sorted(glob.glob(os.path.join(root or HERE, "Defs", "**", "*.xml"), recursive=True)):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        body = re.search(r"<Defs>(.*)</Defs>", txt, re.S)
        for m in re.finditer(r"<([\w.]+)\b([^>]*)>(.*?)</\1>", body.group(1) if body else "", re.S):
            nm = re.search(r"<defName>([^<]+)</defName>", m.group(3))
            if nm and not re.search(r'Abstract\s*=\s*"[Tt]rue"', m.group(2)):
                out.append((m.group(1), nm.group(1).strip(), m.group(3), os.path.relpath(path, HERE)))
    return out


def _source_files():
    """Every shipped .cs under Source/ (Kernel/ included; the SelfTest/ harness is not shipped)."""
    return sorted(p for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True)
                  if "SelfTest" not in os.path.relpath(p, HERE).split(os.sep))


ALIAS_TYPE = "RimMandrake.EnvironmentalHazards.RM_DefAliasDef"
ALIAS_CONTROL = ALIAS_TYPE + "/RM_PlantTierReconcileAliases"   # the kit's own alias def: proves the type spelling resolves
LEGACY_SOURCE = re.compile(r"BackCompatibility|RM_DefAlias|LoadSaveMode\.PostLoadInit[^\n]*(?:old|legacy)|legacy import|"
                           r"historical name|old[- ]name", re.I)


def _save_manifest():
    """What this mod ships that could be save-only preservation: alias registrations, hidden factions nothing else in our
    Defs names (save-only tombstones), and source lines matching a legacy-import pattern; plus the current products
    (egg defs a race lays) that must stay."""
    blocks = _def_blocks()
    aliases = sorted("%s/%s" % (tag, n) for tag, n, _b, _f in blocks if tag.endswith("RM_DefAliasDef"))
    tombs = sorted("FactionDef/%s" % n for tag, n, b, f in blocks if tag == "FactionDef" and "<hidden>true</hidden>" in b
                   and not any(">%s<" % n in ob for _t, _n, ob, of in blocks if of != f))     # named only by its own file
    eggs = sorted("ThingDef/%s" % n for tag, n, _b, _f in blocks if tag == "ThingDef" and "Egg" in n
                  and any("<eggFertilizedDef>%s<" % n in b or "<eggUnfertilizedDef>%s<" % n in b for _t, _n, b, _f in blocks))
    legacy = []
    for path in _source_files():
        with open(path, encoding="utf-8-sig") as fh:
            for i, ln in enumerate(fh, 1):
                if LEGACY_SOURCE.search(ln) and not ln.strip().startswith("//"):
                    legacy.append("%s:%d" % (os.path.basename(path), i))
    return {"aliases": aliases, "tombstones": tombs, "products": eggs, "legacy": legacy}


def _preservation_offences(live_aliases, live_tombs, legacy, products_found, products):
    """The removal checker, pure. live_aliases / live_tombs: alias or tombstone defs that RESOLVE in the running game;
    legacy: source lines of a legacy-import branch; products_found: current product defs that resolve. -> offences."""
    out = []
    if live_aliases:
        out.append("Scrub-owned alias registration(s) still ship: %s" % live_aliases[:4])
    if live_tombs:
        out.append("save-only tombstone(s) still ship: %s" % live_tombs[:4])
    if legacy:
        out.append("legacy import / old-name conversion in the source: %s" % legacy[:4])
    lost = sorted(set(products) - set(products_found))
    if lost:
        out.append("current product def(s) deleted along with their aliases: %s" % lost[:4])
    if not products:
        out.append("no current product def was named: the deletion arm sees nothing")
    return out


@suite.chain("scene_removed_save_preservation")
def scene_removed_save_preservation(t):
    """sc_removed_save_preservation (cuts, save_aliases): no Scrub-owned alias registration (RM_DefAliasDef), no
    save-only tombstone (a hidden faction nothing names) and no legacy-import branch ships, read off the RUNNING game's
    def database and our source; the current egg products the absorbed layers still lay keep resolving. The alias type
    is proven readable on the kit's own alias def first, so a mis-spelled type cannot pass as "removed". Today the
    aliases (RM_SWBRehome_Aliases.xml, RM_Chikka_Aliases.xml) and the hidden RM_Faction_CombHolds still ship: a product
    removal gap, so this scene is expected red at Stage 6 until they are removed. No old save is loaded: there is no
    pre-release save preservation to rescue."""
    _prep(t, "spawn")
    man = _save_manifest()
    got = {}

    def body():
        with _comp(t, "saves_scene_alias_type_readable", poison=True):
            if _live(t):
                if ALIAS_CONTROL not in _resolves(t, [ALIAS_CONTROL]):
                    _unmeasured(t, "get_defs could not read the kit's own alias def %s: an absent Scrub alias would "
                                   "prove nothing" % ALIAS_CONTROL)
        with _comp(t, "saves_scene_no_preservation_ships"):
            if _live(t):
                want = man["aliases"] + man["tombstones"]
                live = _resolves(t, want)
                got["live_aliases"] = sorted(a for a in man["aliases"] if a in live)
                got["live_tombs"] = sorted(a for a in man["tombstones"] if a in live)
                _note(t, "preservation manifest", dict(man, live_aliases=got["live_aliases"], live_tombs=got["live_tombs"]))
                bad = _preservation_offences(got["live_aliases"], got["live_tombs"], man["legacy"], man["products"],
                                             man["products"])
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "saves_scene_current_products_kept"):
            if _live(t):
                found = sorted(_resolves(t, man["products"]))
                bad = [b for b in _preservation_offences([], [], [], found, man["products"])]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "saves_scene_checker_rejects_injections"):
            if _live(t):
                prod = ["ThingDef/RM_XEgg"]
                if _preservation_offences([], [], [], prod, prod):
                    _fail("the removal checker refuses a clean manifest")
                injected = {"old-name alias row": _preservation_offences(["X/RM_OldAliases"], [], [], prod, prod),
                            "old-start-only conversion branch": _preservation_offences([], [], ["RM_X.cs:12"], prod, prod),
                            "save-only tombstone": _preservation_offences([], ["FactionDef/RM_Gone"], [], prod, prod),
                            "current egg deleted": _preservation_offences([], [], [], [], prod)}
                missed = sorted(k for k, v in injected.items() if not v)
                if LEGACY_SOURCE.search("Scribe_Values.Look(ref x, \"smother\")"):
                    missed.append("an ordinary current-schema Scribe read as legacy")
                if missed:
                    _fail("the removal checker passed injected manifest(s) %s: it is blind there" % missed)
    with _scene(t, "sc_removed_save_preservation", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: floor_payload

DLC_PACKAGES = ("ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
                "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
WORLDGEN_SOURCE = re.compile(r":\s*WorldGenStep\b|WorldGenerator|WorldGenStepDef|WorldGrid\b.*\bbiome\b\s*=|"
                             r"\[HarmonyPatch\(typeof\(World", re.I)
MULTIPLAYER_TEXT = re.compile(r"\bmultiplayer\b|\bco-?op\b", re.I)


def _about_deps():
    with open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8") as fh:
        txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
    deps = re.search(r"<modDependencies>(.*?)</modDependencies>", txt, re.S)
    return sorted(set(p.strip().lower() for p in re.findall(r"<packageId>([^<]+)</packageId>", deps.group(1) if deps else "")))


def _composed_folds():
    """Package ids the composed Baroque Biomes (mandrake.rm.biomes) carries inside it (Biomes.compose.json entries)."""
    with open(os.path.join(REPO, "src", "RimMandrake", "Biomes.compose.json"), encoding="utf-8") as fh:
        return sorted("mandrake.rm.%s" % e["source"].lower() for e in json.load(fh).get("entries") or [] if e.get("source"))


def _payload_manifest():
    """The offline half of the payload: dependencies, def types, def names, namespaces, worldgen and multiplayer hits."""
    blocks = _def_blocks()
    src = {}
    for path in _source_files():
        with open(path, encoding="utf-8-sig") as fh:
            src[os.path.relpath(path, os.path.join(HERE, "Source"))] = fh.read()
    return {"deps": _about_deps(), "folds": _composed_folds(),
            "worldgen": sorted(["Defs:%s/%s" % (tag, n) for tag, n, _b, _f in blocks if tag == "WorldGenStepDef"]
                               + ["%s:%d" % (f, s[:m.start()].count("\n") + 1) for f, s in src.items()
                                  for m in WORLDGEN_SOURCE.finditer(re.sub(r"//[^\n]*", "", s))]),
            "names": sorted(n for _tag, n, _b, _f in blocks if not re.match(r"(RM|RSW|RUT)_", n)),
            "namespaces": sorted(set(ns for s in src.values() for ns in re.findall(r"^namespace ([\w.]+)", s, re.M)
                                     if not ns.startswith("RimMandrake"))),
            "texts": {}}


def _payload_offences(m, running, missing_defs):
    """The payload checker, pure. m _payload_manifest(); running the live package ids; missing_defs shipped defs the
    running game lacks. -> offences: a DLC or dependency not running (folded-in kit packages count through the composed
    biome), a shipped def missing, a worldgen hook, a name outside the three tiers, a multiplayer or cut-content promise.
    Zero naturally allocated Scrub tiles is expected (the planet is painted once, at the end) and is never read."""
    out = []
    run = set(p.lower() for p in running)
    if not run & set(OUR_PACKAGES):
        out.append("neither %s is running" % (OUR_PACKAGES,))
    out += ["DLC %s is not running (all DLC are assumed)" % d for d in DLC_PACKAGES if d not in run]
    folded = set(m["folds"]) if "mandrake.rm.biomes" in run else set()
    out += ["dependency %s is not running" % d for d in m["deps"] if d not in run and d not in folded]
    if missing_defs:
        out.append("shipped def(s) missing from the running game: %s" % missing_defs[:4])
    if m["worldgen"]:
        out.append("worldgen hook(s) ship: %s" % m["worldgen"][:4])
    if m["names"] or m["namespaces"]:
        out.append("names outside the three tiers: %s %s" % (m["names"][:4], m["namespaces"][:2]))
    for where, txt in sorted(m["texts"].items()):
        hit = MULTIPLAYER_TEXT.search(txt or "") or CUT_WORDS.search(txt or "")
        if hit:
            out.append("%s promises %r" % (where, hit.group(0)))
    return out


@suite.chain("scene_floor_payload")
def scene_floor_payload(t):
    """floor_payload (native_cast, cuts): the effective running package list (every DLC, our package or the composed
    biome, each About.xml dependency running or folded into the composed biome), every shipped def resolving in the
    running game, no worldgen hook in Defs or source, three-tier names, and no live text (hidden placeholders excluded)
    promising multiplayer or cut content.
    Base effects are observed, not trusted to a clean log: the biome resolves with its lean extension and weather table.
    Zero naturally allocated Scrub tiles is expected and never read (CLAUDE.md, paint once at the end)."""
    _prep(t, "spawn")
    man = _payload_manifest()

    def body():
        with _comp(t, "payload_running_list_and_defs"):
            if _live(t):
                mods = _ok(t.bridge_call("jawa/running_mods"), "running_mods").get("packageIds") or []
                missing = sorted(set(SHIPPED) - _resolves(t, SHIPPED))
                _note(t, "payload", {"running": len(mods), "missing": missing[:8], "worldgen": man["worldgen"]})
                bad = [b for b in _payload_offences(man, mods, missing) if "promises" not in b]
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "payload_base_effects_present"):
            if _live(t):
                rows, _r = _get_defs(t, "BiomeDef/RM_LeaningScrub", "modExtensions,baseWeatherCommonalities")
                row = rows.get("RM_LeaningScrub") or {}
                if "RM_LeanExtension" not in json.dumps(row.get("modExtensions")):
                    _fail("RM_LeaningScrub resolves without its RM_LeanExtension: the base effect is absent")
                if not row.get("baseWeatherCommonalities"):
                    _fail("RM_LeaningScrub resolves with no weather table")
        with _comp(t, "payload_text_promises_nothing_cut"):
            if _live(t):
                defs, _r = _get_defs(t, ";".join(SHIPPED), "description,label,hidden", deep=False)
                man["texts"] = dict(("%s.description" % n, str(f.get("description") or "")) for n, f in defs.items()
                                    if not _as_bool(f.get("hidden")))     # live text, hidden placeholders excluded
                man["texts"]["About.xml"] = _about_text()
                if len(man["texts"]) < 2:
                    _unmeasured(t, "get_defs returned no description: the text cannot be read")
                bad = [b for b in _payload_offences(man, list(DLC_PACKAGES) + [OUR_PACKAGES[0]] + man["deps"], [])
                       if "promises" in b]
                if bad:
                    _fail("; ".join(bad)[:600])
        with _comp(t, "payload_checker_rejects_injections"):
            if _live(t):
                clean = {"deps": ["mandrake.rm.environmentalhazards"], "folds": ["mandrake.rm.environmentalhazards"],
                         "worldgen": [], "names": [], "namespaces": [], "texts": {"About.xml": "A wind-scoured plain."}}
                run = list(DLC_PACKAGES) + ["mandrake.rm.biomes"]
                if _payload_offences(clean, run, []):
                    _fail("the payload checker refuses a clean payload: %s" % _payload_offences(clean, run, []))
                injected = {"missing dependency": (dict(clean, deps=["brrainz.harmony"]), run, []),
                            "stale guardian promise": (dict(clean, texts={"About.xml": "Bark-wardens guard it."}), run, []),
                            "worldgen hook": (dict(clean, worldgen=["RM_X.cs:4"]), run, []),
                            "missing DLC": (clean, run[:-2] + ["mandrake.rm.biomes"], []),
                            "absent effect behind a clean load": (clean, run, ["ThingDef/RM_Fuzz"])}
                missed = sorted(k for k, a in injected.items() if not _payload_offences(*a))
                if missed:
                    _fail("the payload checker passed injected payload(s) %s: it is blind there" % missed)
    with _scene(t, "floor_payload", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: floor_recovery

RECOVERY_KIND = "RM_Fuzzrunner"     # the same-def bystanders and the fixture
RECOVERY_SETTING = "sweetlineVisitIntervalDays"   # a non-boolean setting the scene moves off its default (8)


def _recovery_offences(before, after, records):
    """The recovery checker, pure. before/after {"tick", "bystanders": [ids], "fixtures": [ids], "settings": {f: v}};
    records the SCENE_RECORD verbs the probe emitted. -> offences: the captured state did not return (tick, a bystander
    lost, a fixture left, a setting off its value) while the scene was closed; a failed restore that recorded scene-end."""
    out = []
    restored = (after.get("tick") == before.get("tick") and set(before["bystanders"]) <= set(after["bystanders"])
                and not set(after.get("fixtures") or []) and after.get("settings") == before.get("settings"))
    if "scene-begin" not in records:
        out.append("the probe never opened a recovery (no scene-begin)")
    if not restored:
        why = []
        if after.get("tick") != before.get("tick"):
            why.append("tick %s -> %s" % (before.get("tick"), after.get("tick")))
        lost = sorted(set(before["bystanders"]) - set(after["bystanders"]))
        if lost:
            why.append("bystander(s) %s lost" % lost[:4])
        if after.get("fixtures"):
            why.append("fixture(s) %s left" % after["fixtures"][:4])
        if after.get("settings") != before.get("settings"):
            why.append("settings %s -> %s" % (before.get("settings"), after.get("settings")))
        if "scene-end" in records:
            out.append("the state did not return (%s) but the recovery was closed (scene-end)" % "; ".join(why))
        elif "scene-hold" not in records:
            out.append("the state did not return (%s); the recovery stays open, blocking further runs" % "; ".join(why))
    elif "scene-end" not in records and "scene-hold" not in records:
        out.append("the state returned but the recovery was left open (no scene-end)")
    return out


def _log_window(msgs, start, end):
    """The log-window checker, pure. msgs: jawa/drain_log rows (the whole Log.Messages buffer, oldest first: the tool
    keeps no cursor); start/end: the sentinels written around the scene. -> ("UNMEASURED", why) when a sentinel is not
    in the buffer (a dead tap, or the buffer rolled past the start), ("FAIL", texts) for LeaningScrub errors between
    them, ("PASS", None) otherwise. Messages before the start belong to earlier chains and are never judged."""
    texts = [str(m.get("text") or "") for m in msgs or []]
    i = next((k for k, x in enumerate(texts) if start in x), None)
    j = next((k for k, x in enumerate(texts) if end in x), None)
    if i is None or j is None or j < i:
        return "UNMEASURED", "a log sentinel is not in the buffer (start %s, end %s): the window cannot be read" % (i, j)
    errs = [texts[k] for k in range(i + 1, j) if str(msgs[k].get("type")) in ("Error", "Exception") and
            "LeaningScrub" in texts[k]]
    return ("FAIL", errs) if errs else ("PASS", None)


class _ProbeBoom(Exception):
    pass


@suite.chain("scene_floor_recovery")
def scene_floor_recovery(t):
    """floor_recovery (cuts): the scene harness itself. Same-def bystanders inside and outside the pad and a setting
    moved off its default are captured; a probe scene (the real _scene) mutates the pad (a fixture of the bystanders'
    def, the setting moved again through _setting) and then raises, once after staging and once with its restore made to fail. After the
    first, the exact captured state is back and the recovery closed; after the second the recovery stays open and no
    scene-end is recorded (the probe's records are kept, not written to stage.json). A log sentinel must reach the tap
    before a clean window counts; attributable LeaningScrub errors in the window fail it."""
    _prep(t, "fuel")
    x, z = t.anchor
    got = {}

    def digest():
        rows = _rows(t)
        return {"tick": _game_tick(t), "bystanders": sorted(p for p in got["bystanders"] if p in rows),
                "fixtures": sorted(p for p in got.get("fixtures", []) if p in rows),
                "settings": {RECOVERY_SETTING: str(_get_setting(t, RECOVERY_SETTING))}}

    def probe(fail_restore):
        records, real, load = [], SCENE_RECORD, _scene_load
        globals()["SCENE_RECORD"] = lambda *a: records.append(a[0])
        if fail_restore:
            globals()["_scene_load"] = lambda _t, _n: {"success": False, "message": "injected restore failure"}
        try:
            with _scene(t, "floor_recovery_probe", "immediate"):
                got["fixtures"] = [_spawn(t, RECOVERY_KIND, x + 2, z + 2)]
                with _setting(t, RECOVERY_SETTING, 13.0):      # the harness's own way to move a setting
                    raise _ProbeBoom("injected exception after staging")
        except _ProbeBoom:
            pass
        finally:
            globals()["SCENE_RECORD"], globals()["_scene_load"] = real, load
        return records

    def mark(what):
        got[what] = "LSCRUB_RECOVERY_%s_%d" % (what.upper(), int(time.time() * 1000))
        t.bridge_call("jawa/static_call", type="Verse.Log", method="Warning", args=got[what])

    def body():
        with _comp(t, "recovery_exact_state_returns"):
            if _live(t):
                mark("start")
                got["bystanders"] = [_spawn(t, RECOVERY_KIND, x - 3, z), _spawn(t, RECOVERY_KIND, x + 30, z)]
                _set(t, RECOVERY_SETTING, 11.0)
                before = digest()
                records = probe(False)
                after = digest()
                _note(t, "recovery", {"before": before, "after": after, "records": records})
                bad = _recovery_offences(before, after, records)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "recovery_failed_restore_stays_open"):
            if _live(t):
                before = digest()
                records = probe(True)
                after = digest()
                if "scene-end" in records:
                    _fail("the probe's restore was made to fail but the recovery was closed (scene-end): %s" % records)
                if "scene-begin" not in records:
                    _fail("the probe never opened a recovery (no scene-begin): %s" % records)
                got["leftover"] = after.get("fixtures")
                _note(t, "failed restore", {"before": before, "after": after, "records": records})
                for p in after.get("fixtures") or []:     # the open recovery's fixture, by its recorded id only
                    _vanish(t, p)
        with _comp(t, "recovery_log_window_clean"):
            if _live(t):
                mark("end")
                msgs = _ok(t.bridge_call("jawa/drain_log", limit=5000), "drain_log").get("messages") or []
                verdict, why = _log_window(msgs, got.get("start") or "(no start sentinel)", got["end"])
                if verdict == "UNMEASURED":
                    _unmeasured(t, why)
                if verdict == "FAIL":
                    _fail("attributable LeaningScrub error(s) in the window: %s" % [str(e)[:160] for e in why[:3]])
        with _comp(t, "recovery_checker_rejects_injections"):
            if _live(t):
                b = {"tick": 5, "bystanders": ["a", "b"], "fixtures": [], "settings": {"f": "0.7"}}
                ok = ["scene-begin", "scene-end"]
                if _recovery_offences(b, dict(b), ok):
                    _fail("the recovery checker refuses a clean restore: %s" % _recovery_offences(b, dict(b), ok))
                injected = {"bystander destroyed": _recovery_offences(b, dict(b, bystanders=["a"]), ok),
                            "clock not restored": _recovery_offences(b, dict(b, tick=9), ok),
                            "setting left moved": _recovery_offences(b, dict(b, settings={"f": "0.9"}), ok),
                            "fixture left behind": _recovery_offences(b, dict(b, fixtures=["x"]), ok),
                            "omitted restore": _recovery_offences(b, dict(b, tick=9), ["scene-begin"]),
                            "no recovery opened": _recovery_offences(b, dict(b), ["scene-end"]),
                            "restored but left open": _recovery_offences(b, dict(b), ["scene-begin"]),
                            "dead log sentinel": [1] if _log_window([], "S", "E")[0] != "PASS" else [],
                            "error inside the window": [1] if _log_window(
                                [{"text": "S"}, {"type": "Error", "text": "[RM LeaningScrub] x"}, {"text": "E"}], "S", "E")[0]
                                == "FAIL" else [],
                            "earlier chain's error judged": [1] if _log_window(      # correct = not judged
                                [{"type": "Error", "text": "[RM LeaningScrub] x"}, {"text": "S"}, {"text": "E"}], "S", "E")[0]
                                == "PASS" else []}
                missed = sorted(k for k, v in injected.items() if not v)
                # an omitted restore with the recovery left open is the CORRECT outcome, so it must read as open, not pass
                if "omitted restore" not in missed and "stays open" not in " ".join(injected["omitted restore"]):
                    missed.append("omitted restore not named as an open recovery")
                if missed:
                    _fail("the recovery checker passed injected run(s) %s: it is blind there" % missed)
    with _scene(t, "floor_recovery", "immediate"):
        try:
            _stable(t, body)
        finally:
            _restore(t, RECOVERY_SETTING)        # unguarded: a failed component must not leave the setting moved


# --------------------------------------------------------------------------- scenes batch 4: fire, dripping, felt, routes
# RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_NINETY_FIVE_BARS_LEFT: sc_fire_bias, ix_fire_accountability, sc_dripping,
# sc_felt_comfort, sc_home_routes and ix_route_growth (live; UNRUN in game until Stage 6) and sc_economy_observer
# (offline: the accounting observer run on its fixtures). Contracts: design/concepts/LeaningScrub/scenes.json. Each live
# scene keeps its verdict in a pure checker that a `*_checker_rejects_injections` row proves can fail.

PADS["firebias"] = (40, 0)      # 32-cell pads: 40 + (32 + 8) / 2 = 60, inside the suite's anchor margin
PADS["fireacct"] = (-40, 0)
PADS["felt"] = (0, 40)
PADS["routes"] = (0, 0)
LEAN_DX = (0, 1, 1, 1, 0, -1, -1, -1)    # RM_LeanKernel.NeighbourDx / NeighbourDz
LEAN_DZ = (1, 1, 0, -1, -1, -1, 0, 1)
FIRE_ALIGNMENT = 0.3                      # RM_LeanKernel.FireAlignment: a neighbour above this counts as downwind
FIRE_GRID, FIRE_STEP, FIRE_ROUNDS = 4, 7, 4   # 16 beds a round, 4 rounds: 64 spread opportunities per arm
FIRE_WINDOW = 300                         # ticks a lit bed is watched for its first neighbour ignitions
GRASS = "Plant_Grass"


def _downwind_offsets(wind):
    """The neighbour offsets RM_LeanKernel.DownwindNeighbours calls downwind of a fire for this Downwind vector."""
    out = set()
    for dx, dz in zip(LEAN_DX, LEAN_DZ):
        if (dx * wind[0] + dz * wind[1]) / ((dx * dx + dz * dz) ** 0.5) > FIRE_ALIGNMENT:
            out.add((dx, dz))
    return out


def _fire_bias_offences(arms, n_down, bias):
    """The fire-bias checker, pure. arms {"on"|"off": {"down", "hits", "beds"}}: first-step neighbour ignitions landing
    downwind, all of them, and the beds that spread at all; n_down of the 8 neighbours lie downwind; `bias` is the
    leanFireBias the on arm ran. The thresholds follow RM_TheLeanProof.ProofFire, each arm judged against vanilla's
    uniform share p0 = n_down / 8 (so a broken control cannot hide or fake the lift): the on share clears the floor
    halfway to the production expectation bias + (1 - bias) * p0 at z >= 3 over p0, and the control (bias 0) stays
    within 4 standard errors of p0. -> offences."""
    out = []
    p0 = n_down / 8.0
    on, off = arms.get("on") or {}, arms.get("off") or {}
    for k, a in (("on", on), ("off", off)):
        if a.get("hits", 0) < 30 or a.get("beds", 0) < 8:
            out.append("%s arm: %d neighbour ignitions from %d beds, a lucky few fires (need >= 30 from >= 8 beds)"
                       % (k, a.get("hits", 0), a.get("beds", 0)))
    if out:
        return out
    pon, poff = float(on["down"]) / on["hits"], float(off["down"]) / off["hits"]
    if abs(poff - p0) > 4 * (p0 * (1 - p0) / off["hits"]) ** 0.5 + 1e-9:
        out.append("control (bias 0) lands %.3f downwind against vanilla's uniform %.3f: the directional adjustment "
                   "did not disappear" % (poff, p0))
    pexp = bias + (1 - bias) * p0
    se = (pon * (1 - pon) / on["hits"] + p0 * (1 - p0) / on["hits"]) ** 0.5
    z = (pon - p0) / se if se > 0 else (99.0 if pon > p0 else 0.0)
    floor = p0 + 0.5 * (pexp - p0)
    if pon < floor or z < 3.0:
        out.append("fire does not favour downwind cells: on %d/%d (%.3f) against vanilla %.3f (control read %.3f), "
                   "expected %.3f, floor %.3f, z %.2f" % (on["down"], on["hits"], pon, p0, poff, pexp, floor, z))
    return out


def _fire_cells(t, rect):
    return set((f.get("x"), f.get("z")) for f in _things(t, "Fire", _rs(rect), 500))


def _lean_wind(t):
    return _vec2(_ok(t.bridge_call("jawa/map_comp_read", comp="RM_MapComponent_Lean", members="Downwind"),
                     "map_comp_read(Lean)").get("values", {}).get("Downwind"))


@suite.chain("scene_fire_bias")
def scene_fire_bias(t):
    """sc_fire_bias (downwind_fire): 16 isolated 3x3 grass beds a round on a cleared pad, each centre lit through
    jawa/map_fire (RimWorld's own TryStartFireIn), the stampers switched off and no quench form staged; per bed the
    FIRST neighbour cells to catch are read off the Fire things every 30 ticks. Four rounds per arm give 64 production
    spread opportunities: the on arm at the shipped leanFireBias, the control at bias 0 on the same geometry, fuel and
    bed order. The bridge reaches no Rand seed, so the count (and the bed spread) is the protection against a lucky fire,
    not a fixed seed. RM_TheLeanProof.ProofFire stays the C# lean chain's row; this scene watches real fires."""
    _prep(t, "firebias", 32)
    x0, z0 = _rect(t, 32)[:2]
    beds = [(x0 + 3 + i * FIRE_STEP, z0 + 3 + j * FIRE_STEP) for i in range(FIRE_GRID) for j in range(FIRE_GRID)]
    got = {}

    def bed_round():
        """One round: beds laid and lit, watched FIRE_WINDOW ticks, then put out and cleared. -> {bed: first offsets}"""
        t.bridge_call("jawa/set_plants", ops=";".join("%s:%d,%d,3,3" % (GRASS, bx - 1, bz - 1) for bx, bz in beds),
                      growth=1.0)
        for bx, bz in beds:
            t.bridge_call("jawa/map_fire", action="start", rect="%d,%d,1,1" % (bx, bz), fireSize=0.5)
        first = {}
        for _ in range(FIRE_WINDOW // 30):
            t.wait_ticks(30)
            cells = _fire_cells(t, _rect(t, 32))
            for b in beds:
                if b not in first:
                    lit = set((dx, dz) for dx, dz in zip(LEAN_DX, LEAN_DZ) if (b[0] + dx, b[1] + dz) in cells)
                    if lit:
                        first[b] = lit
        t.bridge_call("jawa/map_fire", action="extinguish", rect=_rs(_rect(t, 32)))
        t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, 32)), categories="All")
        return first

    def arm(name):
        down = hits = 0
        spread = set()
        for r in range(FIRE_ROUNDS):
            for b, lit in bed_round().items():
                spread.add((r, b))
                hits += len(lit)
                down += len(lit & got["down"])
        got["arms"][name] = {"down": down, "hits": hits, "beds": len(spread)}

    def body():
        with _comp(t, "fire_bias_beds_staged", poison=True):
            if _live(t):
                got["wind"] = _lean_wind(t)
                if not got["wind"] or not any(got["wind"]):
                    _unmeasured(t, "RM_MapComponent_Lean.Downwind unreadable or zero: no heading to judge against")
                got["down"] = _downwind_offsets(got["wind"])
                got["bias"] = float(_get_setting(t, "leanFireBias"))
                got["arms"] = {}
                if not got["down"] or got["bias"] <= 0:
                    _unmeasured(t, "%d downwind neighbours at bias %s promise no lift" % (len(got["down"]), got["bias"]))
        with _comp(t, "fire_bias_downwind_lift", toggle="leanFireEnabled"):
            if _live(t):
                with _setting(t, "fireStampEnabled", False), _setting(t, "leanFireEnabled", True):
                    arm("on")
                    with _setting(t, "leanFireBias", 0.0):
                        arm("off")
                _note(t, "fire bias arms (first neighbour ignitions)", dict(got["arms"], wind=got["wind"],
                                                                           downwind=sorted(got["down"])))
                bad = [b for b in _fire_bias_offences(got["arms"], len(got["down"]), got["bias"])
                       if "favour" in b or "on arm" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "fire_bias_control_plain"):
            if _live(t):
                bad = [b for b in _fire_bias_offences(got["arms"], len(got["down"]), got["bias"])
                       if "did not disappear" in b or "off arm" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "fire_bias_checker_rejects_injections"):
            if _live(t):
                good = {"on": {"down": 88, "hits": 128, "beds": 60}, "off": {"down": 48, "hits": 128, "beds": 60}}
                if _fire_bias_offences(good, 3, 0.5):
                    _fail("the fire checker refuses a clean reading: %s" % _fire_bias_offences(good, 3, 0.5))
                injected = {"no lift": dict(good, on={"down": 48, "hits": 128, "beds": 60}),
                            "lucky single fire": dict(good, on={"down": 8, "hits": 8, "beds": 1}),
                            "control keeps the lean": dict(good, off={"down": 88, "hits": 128, "beds": 60}),
                            "control never spread": dict(good, off={"down": 0, "hits": 0, "beds": 0})}
                missed = sorted(k for k, a in injected.items() if not _fire_bias_offences(a, 3, 0.5))
                if missed:
                    _fail("the fire checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_fire_bias", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: ix_fire_accountability

STAMPER = "RSW_ShrublandGiant"     # the thunderstep: RM_FireStamperExtension is patch-added (RSW_ShrublandGiant_FireStamper.xml)
STAMP_REACH = 6.0                  # cells: a stamper this close to the blaze has answered it (RM_BlazeKernel.StampRadius scale)
PURSUIT_REACH = 3.0                # cells: a stamper this close to a pawn after contact broke is pursuing it


def _accountability_offences(w, u):
    """The fire-accountability checker, pure. w (the witnessed lighter's blaze) {"spread_downwind", "stampers_at_blaze",
    "maker_pursued", "innocent_pursued", "pursuit_after_reload", "unrelated_visited"}; u (the unwitnessed control blaze)
    {"stampers_at_blaze", "anyone_pursued"}. -> offences."""
    out = []
    if not w.get("spread_downwind"):
        out.append("the lit fire never spread downwind")
    if not w.get("stampers_at_blaze"):
        out.append("the herd never answered the witnessed blaze")
    if not w.get("maker_pursued"):
        out.append("the witnessed maker was not pursued")
    if w.get("innocent_pursued"):
        out.append("blanket blame: the innocent bystander was pursued")
    if w.get("maker_pursued") and not w.get("pursuit_after_reload"):
        out.append("the pursuit did not survive a save and reload")
    if w.get("unrelated_visited"):
        out.append("the herd left the blaze to clean up an unrelated fire")
    if not u.get("stampers_at_blaze"):
        out.append("the unwitnessed control blaze drew no stampers")
    if u.get("anyone_pursued"):
        out.append("an unwitnessed blaze produced a maker pursuit")
    return out


def _near(rows, pid, pos, reach):
    return any(_xz(r) and _dist(_xz(r), pos) <= reach for k, r in rows.items() if k == pid)


@suite.chain("scene_ix_fire_accountability")
def scene_ix_fire_accountability(t):
    """ix_fire_accountability (fire_bias + stamping + maker, together on one live map): a colonist lights an open grass
    field through the real Ignite job (the maker) with a second colonist (the innocent) beside it and three thunderstep
    stampers 20 cells off; the fire spreads downwind, the herd comes and stamps, then the maker walks 40 cells away and
    the innocent stays. A save and reload falls mid-pursuit. The control lights a second field with jawa/map_fire (no
    lighter, no trail) with one colonist near it. A one-cell fire 30 cells off is the unrelated fire. The maker relation
    is read as the stampers' movement (no bridge tool reads a pursuit target). The shared witness/violator service
    (plan.md, SCRUB_PROVE_WIND_FIRE_AND_RITUAL) is not built yet, so maker pursuit is expected red at Stage 6 until it
    is. Needs the composed list (the thunderstep comes from UtinniPatches). Hold: owner_review."""
    _prep(t, "fireacct", 32)
    x, z = t.anchor
    field, ctrl, unrelated = (x - 12, z - 4, 9, 9), (x + 4, z - 14, 7, 7), (x + 14, z + 14)
    got = {"w": {}, "u": {}}

    def stampers():
        return dict((k, r) for k, r in _rows(t).items() if r.get("kindDef") == STAMPER)

    def body():
        with _comp(t, "accountability_staged", poison=True):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="%s:%s;%s:%s;%s:%d,%d,1,1" % (GRASS, _rs(field), GRASS, _rs(ctrl),
                                                                                  GRASS, unrelated[0], unrelated[1]),
                              growth=1.0)
                t.bridge_call("jawa/map_fire", action="start", rect="%d,%d,1,1" % unrelated, fireSize=0.1)
                got["maker"] = _spawn(t, "Colonist", field[0] - 2, field[1] + 4, faction="player")
                got["innocent"] = _spawn(t, "Colonist", field[0] - 3, field[1] + 6, faction="player")
                for p in (got["maker"], got["innocent"]):
                    _full(t, p)
                got["herd"] = [_spawn(t, STAMPER, x - 8 + 2 * i, z + 14) for i in range(3)]
                got["wind"] = _lean_wind(t)
                if not got["wind"] or not any(got["wind"]):
                    _unmeasured(t, "RM_MapComponent_Lean.Downwind unreadable or zero")
                if len(stampers()) < 3:
                    _unmeasured(t, "%s did not stand (the thunderstep ships in the composed list only)" % STAMPER)
        with _comp(t, "accountability_blaze_answered", toggle="fireStampEnabled"):
            if _live(t):
                lit_at = (field[0] + 4, field[1] + 4)
                grass = _things(t, GRASS, "%d,%d,1,1" % lit_at)
                if not grass:
                    _unmeasured(t, "no grass at the lighting cell %s" % (lit_at,))
                _ok(t.bridge_call("jawa/ordered_job", pawnId=got["maker"], jobDef="Ignite", targetAId=grass[0]["id"],
                                  waitTicks=60), "ordered_job(Ignite)")
                fires = set()
                for _ in range(10):
                    t.wait_ticks(60)
                    fires = _fire_cells(t, _rect(t, 32))
                    if fires:
                        break
                if not fires:
                    _unmeasured(t, "the Ignite job lit nothing in 600 ticks")
                got["lit_at"] = lit_at
                cells = set(fires)
                for _ in range(10):      # the union: the herd may stamp a cell before a later read sees it
                    t.wait_ticks(60)
                    cells |= _fire_cells(t, field)
                got["w"]["spread_downwind"] = len([c for c in cells if (c[0] - lit_at[0]) * got["wind"][0]
                                                   + (c[1] - lit_at[1]) * got["wind"][1] > 0.5])
                for _ in range(10):
                    t.wait_ticks(300)
                    rows = stampers()
                    if any(_xz(r) and _dist(_xz(r), lit_at) <= STAMP_REACH + 4 for r in rows.values()):
                        break
                rows = stampers()
                got["w"]["stampers_at_blaze"] = len([1 for r in rows.values()
                                                     if _xz(r) and _dist(_xz(r), lit_at) <= STAMP_REACH + 4])
                got["w"]["unrelated_visited"] = any(_xz(r) and _dist(_xz(r), unrelated) <= STAMP_REACH
                                                    for r in rows.values())
                _note(t, "witnessed blaze", got["w"])
                bad = [b for b in _accountability_offences(got["w"], {"stampers_at_blaze": 1})
                       if "spread" in b or "answered" in b or "unrelated" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "accountability_maker_not_innocent"):
            if _live(t):
                _order_goto(t, got["maker"], x - 12, z + 40)
                track = []
                for _ in range(8):
                    t.wait_ticks(300)
                    rows = _rows(t)
                    m, i = _xz(rows.get(got["maker"])), _xz(rows.get(got["innocent"]))
                    track.append({"maker": m, "innocent": i, "herd": [_xz(rows.get(h)) for h in got["herd"]]})
                    if m and any(_xz(rows.get(h)) and _dist(_xz(rows.get(h)), m) <= PURSUIT_REACH for h in got["herd"]):
                        got["w"]["maker_pursued"] = True
                    if i and any(_xz(rows.get(h)) and _dist(_xz(rows.get(h)), i) <= PURSUIT_REACH for h in got["herd"]):
                        got["w"]["innocent_pursued"] = True
                name = "lscrub_ixfire_mid_%d" % int(time.time())
                _ok(t.bridge_call("rimworld/save_game", saveName=name), "save_game")
                _ok(t.bridge_call("rimworld/load_game_ready", saveName=name, timeoutMs=240000), "load_game_ready")
                m0 = _xz(_rows(t).get(got["maker"]))
                if not m0:
                    _unmeasured(t, "the maker is not on the map after the reload")
                _order_goto(t, got["maker"], m0[0] + 10, m0[1])     # a pursuer standing still beside him proves nothing
                for _ in range(4):
                    t.wait_ticks(300)
                rows = _rows(t)
                m = _xz(rows.get(got["maker"]))
                if not m or _dist(m, m0) < 5:
                    _unmeasured(t, "the maker did not move after the reload (%s -> %s): pursuit cannot be told from "
                                   "standing" % (m0, m))
                got["w"]["pursuit_after_reload"] = any(_xz(rows.get(h)) and _dist(_xz(rows.get(h)), m) <= PURSUIT_REACH
                                                       for h in got["herd"])
                _note(t, "maker / innocent track (every 300 ticks)", track[-4:])
                bad = [b for b in _accountability_offences(got["w"], {"stampers_at_blaze": 1})
                       if "maker" in b or "blame" in b or "reload" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "accountability_unwitnessed_no_pursuit"):
            if _live(t):
                t.bridge_call("jawa/map_fire", action="extinguish", rect=_rs(field))    # the control blaze stands alone
                watcher = _spawn(t, "Colonist", ctrl[0] - 3, ctrl[1] + 3, faction="player")
                _full(t, watcher)
                cpos = (ctrl[0] + 3, ctrl[1] + 3)
                t.bridge_call("jawa/map_fire", action="start", rect=_rs(ctrl), fireSize=1.0)
                for _ in range(10):
                    t.wait_ticks(300)
                    rows = stampers()
                    got["u"]["stampers_at_blaze"] = len([1 for r in rows.values()
                                                         if _xz(r) and _dist(_xz(r), cpos) <= STAMP_REACH + 4])
                    allr = _rows(t)
                    if _xz(allr.get(watcher)) and any(_xz(r) and _dist(_xz(r), _xz(allr[watcher])) <= 1.5
                                                      for r in rows.values()):
                        got["u"]["anyone_pursued"] = True
                _note(t, "unwitnessed control blaze", got["u"])
                bad = [b for b in _accountability_offences({"spread_downwind": 1, "stampers_at_blaze": 1,
                                                            "maker_pursued": True, "pursuit_after_reload": True},
                                                           got["u"]) if "unwitnessed" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "accountability_checker_rejects_injections"):
            if _live(t):
                gw = {"spread_downwind": 6, "stampers_at_blaze": 2, "maker_pursued": True, "innocent_pursued": False,
                      "pursuit_after_reload": True, "unrelated_visited": False}
                gu = {"stampers_at_blaze": 2, "anyone_pursued": False}
                if _accountability_offences(gw, gu):
                    _fail("the accountability checker refuses a clean reading: %s" % _accountability_offences(gw, gu))
                injected = {"nearest pawn blamed": (dict(gw, innocent_pursued=True), gu),
                            "maker never pursued": (dict(gw, maker_pursued=False), gu),
                            "pursuit lost on reload": (dict(gw, pursuit_after_reload=False), gu),
                            "blaze destination counts as maker knowledge": (gw, dict(gu, anyone_pursued=True)),
                            "unrelated fire cleaned": (dict(gw, unrelated_visited=True), gu),
                            "no downwind spread": (dict(gw, spread_downwind=0), gu)}
                missed = sorted(k for k, (a, b) in injected.items() if not _accountability_offences(a, b))
                if missed:
                    _fail("the accountability checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "ix_fire_accountability", "owner_review"):
        try:
            _stable(t, body)
        finally:
            t.bridge_call("jawa/map_fire", action="extinguish", rect=_rs(_rect(t, 40)))


# --------------------------------------------------------------------------- scene: dripping

DRIP, VENOM = "RM_DrippingVenomvine", "RM_RawVenom"
# A clean-start arm is a session the operator launched with drippingRegrowEnabled SAVED to this value and no settings
# write since ("false" | "true"); unset, the startup row is UNMEASURED with that recipe. A save reload is never startup.
DRIP_STARTUP = os.environ.get("LSCRUB_DRIP_STARTUP", "").strip().lower()
DRIP_RESET_MAX = 0.6       # a regrowing stand drops back to harvestAfterGrowth 0.3; above this it was not reset
DRIP_REGROW_BUDGET = 6000  # ticks the scene waits for a regrown stand to be harvestable again


def _drip_offences(rows):
    """The dripping checker, pure. rows {arm: {"enabled", "applied_by" ("startup" | "write"), "job_done", "venom",
    "same_stand", "growth_after", "second_venom"}}; arms named startup_* must carry applied_by "startup" (a later
    settings write cannot stand in for the first harvest's evidence). -> offences."""
    out = []
    for arm, r in sorted(rows.items()):
        if arm.startswith("startup") and r.get("applied_by") != "startup":
            out.append("%s: applied by %s, not at startup: a later write cannot repair the first harvest's evidence"
                       % (arm, r.get("applied_by")))
        if not r.get("job_done") or not r.get("venom"):
            out.append("%s: the harvest job did not complete with venom delivered (%s venom)" % (arm, r.get("venom")))
            continue
        if r.get("enabled"):
            if not r.get("same_stand"):
                out.append("%s: regrowth on but the harvested stand is gone" % arm)
            elif r.get("growth_after") is None or r["growth_after"] > DRIP_RESET_MAX:
                out.append("%s: the retained stand was not reset (%s grown after harvest)" % (arm, r.get("growth_after")))
            if "second_venom" in r and not r["second_venom"]:
                out.append("%s: the same stand gave no second harvest" % arm)
        elif r.get("same_stand"):
            out.append("%s: regrowth off but the stand outlived its harvest (not vanilla one-shot)" % arm)
    return out


@suite.chain("scene_dripping")
def scene_dripping(t):
    """sc_dripping (dripping_harvest): a mature dripping stand, a fed colonist, no raw venom on the pad. Rows: the
    clean-start arm (LSCRUB_DRIP_STARTUP; first harvest before any settings write, checked against the def's live
    harvestAfterGrowth); then the WriteSettings path, which is drippingRegrowEnabled set plus RM_RegrowingHarvest.Apply
    (exactly what RM_LeaningScrubMod.WriteSettings runs), on: harvest, venom, same stand reset, save and reload, a
    second harvest of that stand; off: vanilla one-shot. The second harvest needs the stand harvestable again inside
    DRIP_REGROW_BUDGET ticks; growDays 12 does not get there and no bridge tool sets an existing plant's growth in
    place, so live that row is UNMEASURED until a compression hook exists (named in the item note)."""
    _prep(t, "dripping")
    x, z = t.anchor
    rows = {}

    def harvest(at):
        """Order the real Harvest job on the stand at `at`; -> (stand id, venom delivered, job done)."""
        plant = _things(t, DRIP, "%d,%d,1,1" % at)
        if not plant:
            _unmeasured(t, "no dripping stand at %s to harvest" % (at,))
        col = _spawn(t, "Colonist", at[0] - 3, at[1], faction="player")
        _full(t, col)
        v0 = _stack_total(t, VENOM, _rs(_rect(t)))
        t.bridge_call("jawa/designate_batch", action="add", designation="HarvestPlant", rect="%d,%d,1,1" % at)
        t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="Harvest", targetAId=plant[0]["id"], queue=True,
                      waitTicks=60)
        venom = 0
        for _ in range(12):
            t.wait_ticks(600)
            venom = _stack_total(t, VENOM, _rs(_rect(t))) - v0
            if venom >= 1:
                break
        done = venom >= 1 and _jobs(t).get(col) != "Harvest"
        _vanish(t, col)
        return plant[0]["id"], venom, done

    def arm(name, at, enabled, applied_by, second=False):
        t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (DRIP, at[0], at[1]), growth=1.0)
        sid, venom, done = harvest(at)
        stand = _things(t, DRIP, "%d,%d,1,1" % at)
        same = bool(stand) and stand[0].get("id") == sid
        r = {"enabled": enabled, "applied_by": applied_by, "job_done": done, "venom": venom, "same_stand": same,
             "growth_after": _growth(t, sid) if same else None}
        if second and same:
            name_s = "lscrub_drip_mid_%d" % int(time.time())
            _ok(t.bridge_call("rimworld/save_game", saveName=name_s), "save_game")
            _ok(t.bridge_call("rimworld/load_game_ready", saveName=name_s, timeoutMs=240000), "load_game_ready")
            after = _things(t, DRIP, "%d,%d,1,1" % at)
            if not after or after[0].get("id") != sid:
                r["same_stand"] = False
            else:
                waited = 0
                while waited < DRIP_REGROW_BUDGET and (_growth(t, sid) or 0) < 0.99:
                    t.wait_ticks(1000)
                    waited += 1000
                if (_growth(t, sid) or 0) < 0.99:
                    rows[name] = r
                    _unmeasured(t, "the reset stand is %s grown after %d ticks: not harvestable again inside the budget "
                                   "(no in-place growth hook)" % (_growth(t, sid), waited))
                sid2, v2, done2 = harvest(at)
                r["second_venom"] = v2 if (done2 and sid2 == sid) else 0
        rows[name] = r
        _note(t, "dripping arm %s" % name, r)

    def body():
        with _comp(t, "dripping_scene_startup_apply", toggle="drippingRegrowEnabled"):
            if _live(t):
                if DRIP_STARTUP not in ("false", "true"):
                    _unmeasured(t, "not a clean-start arm: launch with drippingRegrowEnabled saved false (then true), "
                                   "no settings write, LSCRUB_DRIP_STARTUP=<saved value>, and run this scene first")
                saved = DRIP_STARTUP == "true"
                if _as_bool(_get_setting(t, "drippingRegrowEnabled")) != saved:
                    _unmeasured(t, "drippingRegrowEnabled reads %r, not the declared saved %s: not a clean start"
                                   % (_get_setting(t, "drippingRegrowEnabled"), saved))
                arm("startup_%s" % DRIP_STARTUP, (x - 6, z), saved, "startup")
                bad = [b for b in _drip_offences({k: v for k, v in rows.items() if k.startswith("startup")})]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "dripping_scene_write_on_regrows", toggle="drippingRegrowEnabled"):
            if _live(t):
                with _setting(t, "drippingRegrowEnabled", True):
                    _apply_regrow(t)
                    arm("write_on", (x, z), True, "write", second=True)
                _apply_regrow(t)
                bad = _drip_offences({"write_on": rows["write_on"]})
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "dripping_scene_write_off_one_shot", toggle="drippingRegrowEnabled"):
            if _live(t):
                with _setting(t, "drippingRegrowEnabled", False):
                    _apply_regrow(t)
                    arm("write_off", (x + 6, z), False, "write")
                _apply_regrow(t)
                bad = _drip_offences({"write_off": rows["write_off"]})
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "dripping_checker_rejects_injections"):
            if _live(t):
                on = {"enabled": True, "applied_by": "write", "job_done": True, "venom": 3, "same_stand": True,
                      "growth_after": 0.3, "second_venom": 3}
                off = {"enabled": False, "applied_by": "write", "job_done": True, "venom": 3, "same_stand": False}
                st = dict(off, applied_by="startup")
                good = {"write_on": on, "write_off": off, "startup_false": st}
                if _drip_offences(good):
                    _fail("the dripping checker refuses a clean reading: %s" % _drip_offences(good))
                injected = {"startup Apply omitted": dict(good, startup_false=dict(st, same_stand=True, growth_after=0.3)),
                            "startup evidence from a write": dict(good, startup_false=dict(st, applied_by="write")),
                            "canceled harvest passes regrowth": dict(good, write_on=dict(on, job_done=False, venom=0)),
                            "stand not reset": dict(good, write_on=dict(on, growth_after=1.0)),
                            "no second harvest": dict(good, write_on=dict(on, second_venom=0)),
                            "off still regrows": dict(good, write_off=dict(off, same_stand=True))}
                missed = sorted(k for k, a in injected.items() if not _drip_offences(a))
                if missed:
                    _fail("the dripping checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_dripping", "immediate"):
        try:
            _stable(t, body)
        finally:
            _apply_regrow(t)     # the restored setting must reach the def too, or the next scene harvests a stale def


def _apply_regrow(t):
    """RM_RegrowingHarvest.Apply: what WriteSettings runs after a settings write (jawa/mod_settings_field alone moves
    the static field, never the def's harvestAfterGrowth)."""
    if t.session is None:
        return
    r = t.session.call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_RegrowingHarvest", method="Apply", args="")
    if not isinstance(r, dict) or r.get("success") is False:
        print("[lscrub] RM_RegrowingHarvest.Apply failed: %r" % (r,), file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- scene: felt_comfort

FELT, FELT_THOUGHT, SEAT = "RM_SweetlineWool", "RM_SweetlineFeltApparel", "Armchair"
FELT_GARMENTS = ("Apparel_BasicShirt", "Apparel_Pants")


def _felt_offset():
    """RM_SweetlineWool's shipped RM_StuffComfortExtension.comfortOffset (read offline; the class default 0.10 when the
    def sets none), None when the def ships no extension."""
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<ThingDef\b[^>]*>(.*?)</ThingDef>", txt, re.S):
            if re.search(r"<defName>%s</defName>" % FELT, m.group(1)):
                if "RM_StuffComfortExtension" not in m.group(1):
                    return None
                d = re.search(r"<comfortOffset>([\d.]+)</comfortOffset>", m.group(1))
                return float(d.group(1)) if d else 0.10
    return None


FELT_OFFSET = _felt_offset()


def _felt_offences(r, offset):
    """The felt checker, pure. r {"seat_delta", "felt_explained", "cloth_explained", "thoughts" {0|1|2 garments: count},
    "off_furniture": {"seat_delta", "thoughts_2"}, "off_apparel": {"seat_delta", "thoughts_2"}}. -> offences."""
    out = []
    if r.get("seat_delta") is None or abs(r["seat_delta"] - offset) > 0.005:
        out.append("a felt seat's comfort is cloth %+.2f, not the configured +%.2f" % (r.get("seat_delta") or 0, offset))
    if not r.get("felt_explained") or r.get("cloth_explained"):
        out.append("the comfort explanation does not name felt on the felt seat alone")
    th = r.get("thoughts") or {}
    if th.get(1) != 1 or th.get(2) != 1:
        out.append("felt apparel thoughts one/two garments = %s/%s, not one each" % (th.get(1), th.get(2)))
    if th.get(0):
        out.append("the felt thought outlived the last felt garment (%s)" % th.get(0))
    of, oa = r.get("off_furniture") or {}, r.get("off_apparel") or {}
    if of.get("seat_delta") is None or abs(of["seat_delta"]) > 0.005 or of.get("thoughts_2") != 1:
        out.append("furniture toggle off: seat delta %s, thoughts %s (want 0 and the apparel thought kept)"
                   % (of.get("seat_delta"), of.get("thoughts_2")))
    if oa.get("thoughts_2") or oa.get("seat_delta") is None or abs(oa["seat_delta"] - offset) > 0.005:
        out.append("apparel toggle off: thoughts %s, seat delta %s (want none and the seat kept)"
                   % (oa.get("thoughts_2"), oa.get("seat_delta")))
    return out


@suite.chain("scene_felt_comfort")
def scene_felt_comfort(t):
    """sc_felt_comfort (felt_comfort): two armchairs of the same quality, one sweetline felt and one cloth, read through
    jawa/stat_explain (the value and the info card's own breakdown); a colonist stripped of apparel puts on a felt shirt,
    then felt trousers, through the real Wear job, and takes both off through RemoveApparel; jawa/pawn_thoughts counts
    the felt thought at zero, one and two garments. Controls: each toggle off alone (sweetlineFeltComfortEnabled,
    sweetlineFeltApparelEnabled) removes only its own effect, the thought never multiplies."""
    _prep(t, "felt", 16)
    x, z = t.anchor
    r = {"thoughts": {}}
    got = {}

    def seat_delta():
        t.bridge_call("jawa/stat_cache_bust")
        vals, expl = {}, {}
        for k in ("felt", "cloth"):
            e = _ok(t.bridge_call("jawa/stat_explain", subject=got[k], stats="Comfort"), "stat_explain(%s)" % k)
            row = (e.get("stats") or [{}])[0]
            if row.get("value") is None:
                _unmeasured(t, "stat_explain(%s) carries no Comfort value: %r" % (k, e))
            vals[k], expl[k] = float(row["value"]), str(row.get("explanation") or "")
        return round(vals["felt"] - vals["cloth"], 4), expl

    def felt_thoughts():
        th = _ok(t.bridge_call("jawa/pawn_thoughts", pawn=got["col"]), "pawn_thoughts")
        return len([1 for x_ in (th.get("thoughts") or []) if x_.get("def") == FELT_THOUGHT])

    def wear(defn, i):
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (defn, x + 2 + i, z), stuff=FELT)
        ap = _things(t, defn, "%d,%d,1,1" % (x + 2 + i, z))
        if not ap:
            _unmeasured(t, "no felt %s stood after spawn_batch" % defn)
        got.setdefault("worn", []).append(ap[0]["id"])
        _ok(t.bridge_call("jawa/ordered_job", pawnId=got["col"], jobDef="Wear", targetAId=ap[0]["id"], waitTicks=60),
            "ordered_job(Wear %s)" % defn)
        t.wait_ticks(600)

    def body():
        with _comp(t, "felt_scene_staged", poison=True):
            if _live(t):
                if FELT_OFFSET is None:
                    _fail("RM_SweetlineWool ships no RM_StuffComfortExtension: no configured offset to observe")
                for k, stuff, dx in (("felt", FELT, -3), ("cloth", "Cloth", 3)):
                    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SEAT, x + dx, z - 4), stuff=stuff)
                    seat = _things(t, SEAT, "%d,%d,1,1" % (x + dx, z - 4))
                    if not seat:
                        _unmeasured(t, "no %s armchair stood" % k)
                    got[k] = seat[0]["id"]
                    t.bridge_call("jawa/set_thing_props", thing=got[k], quality="Normal")
                got["col"] = _spawn(t, "Colonist", x, z + 2, faction="player")
                _full(t, got["col"])
                t.bridge_call("jawa/pawn_gear", pawn=got["col"], action="clear", clearWhat="apparel")
        with _comp(t, "felt_scene_seat_offset", toggle="sweetlineFeltComfortEnabled"):
            if _live(t):
                r["seat_delta"], expl = seat_delta()
                r["felt_explained"] = "+%.2f" % FELT_OFFSET in expl["felt"]
                r["cloth_explained"] = "+%.2f" % FELT_OFFSET in expl["cloth"]
                _note(t, "felt vs cloth armchair", {"delta": r["seat_delta"], "felt": expl["felt"][-200:]})
                bad = [b for b in _felt_offences(r, FELT_OFFSET) if "seat's comfort" in b or "explanation" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "felt_scene_single_thought", toggle="sweetlineFeltApparelEnabled"):
            if _live(t):
                for i, g in enumerate(FELT_GARMENTS):
                    wear(g, i)
                    r["thoughts"][i + 1] = felt_thoughts()
                with _setting(t, "sweetlineFeltComfortEnabled", False):
                    r["off_furniture"] = {"seat_delta": seat_delta()[0], "thoughts_2": felt_thoughts()}
                with _setting(t, "sweetlineFeltApparelEnabled", False):
                    r["off_apparel"] = {"seat_delta": seat_delta()[0], "thoughts_2": felt_thoughts()}
                for aid in got["worn"]:
                    t.bridge_call("jawa/ordered_job", pawnId=got["col"], jobDef="RemoveApparel", targetAId=aid,
                                  waitTicks=60)
                    t.wait_ticks(400)
                r["thoughts"][0] = felt_thoughts()
                _note(t, "felt thoughts by garment count / controls", {"thoughts": r["thoughts"],
                                                                        "off_furniture": r["off_furniture"],
                                                                        "off_apparel": r["off_apparel"]})
                bad = [b for b in _felt_offences(r, FELT_OFFSET) if "apparel thoughts" in b or "outlived" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "felt_scene_toggles_independent"):
            if _live(t):
                bad = [b for b in _felt_offences(r, FELT_OFFSET) if "toggle off" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "felt_checker_rejects_injections"):
            if _live(t):
                good = {"seat_delta": 0.10, "felt_explained": True, "cloth_explained": False,
                        "thoughts": {0: 0, 1: 1, 2: 1}, "off_furniture": {"seat_delta": 0.0, "thoughts_2": 1},
                        "off_apparel": {"seat_delta": 0.10, "thoughts_2": 0}}
                if _felt_offences(good, 0.10):
                    _fail("the felt checker refuses a clean reading: %s" % _felt_offences(good, 0.10))
                injected = {"higher quality passes as material": dict(good, seat_delta=0.25),
                            "stacked thoughts": dict(good, thoughts={0: 0, 1: 1, 2: 2}),
                            "thought outlives felt": dict(good, thoughts={0: 1, 1: 1, 2: 1}),
                            "furniture toggle kills apparel": dict(good, off_furniture={"seat_delta": 0.0, "thoughts_2": 0}),
                            "apparel toggle ignored": dict(good, off_apparel={"seat_delta": 0.10, "thoughts_2": 1}),
                            "cloth explained as felt": dict(good, cloth_explained=True)}
                missed = sorted(k for k, a in injected.items() if not _felt_offences(a, 0.10))
                if missed:
                    _fail("the felt checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_felt_comfort", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scenes: home_routes, ix_route_growth

WALKER = "RM_WalkingVenomvine"
ROUTE_SIZE = 40           # the pad: _prep clears 48 square
ROUTE_DELIVERIES = 20     # the reference fixture's routine deliveries (scenes.json sc_home_routes)
ROUTE_CREW = COLONY_SIZE  # 40 fed colonists, as the contract's start names
ROUTE_SAMPLE = 250        # ticks between job / position samples
GALE = "RM_Gale"


def _route_geometry(x, z):
    """The route site round anchor (x, z), pure (the selftest's fake reads the same cells). West to east: the source
    pile, two 3-cell-wide routes 12 cells apart (A developed: floored, roofed and zoned; B dirt, kept by cutting),
    the stockpile at the east end; emitters (mature thicket and walking stands) along the west edge of a wilderness
    band north of B, upwind of everything when the wind blows east."""
    w = ROUTE_SIZE // 2
    a = [(cx, cz) for cx in range(x - w + 6, x + w - 6) for cz in range(z - 8, z - 5)]
    b = [(cx, cz) for cx in range(x - w + 6, x + w - 6) for cz in range(z + 4, z + 7)]
    wild = [(cx, cz) for cx in range(x - w + 6, x + w - 6) for cz in range(z + 9, z + 15)]
    return {"source": (x - w + 2, z - 3, 4, 4), "stock": (x + w - 6, z - 3, 4, 4), "a": a, "b": b, "wild": wild,
            "a_rect": (x - w + 6, z - 8, 2 * w - 12, 3), "b_rect": (x - w + 6, z + 4, 2 * w - 12, 3),
            "emit_thicket": [(x - w + 3, cz) for cz in range(z + 3, z + 15, 2)],
            "emit_walker": [(x - w + 4, cz) for cz in range(z + 4, z + 15, 3)],
            "detour_block": (x, z - 8, 1, 3), "inject_block": (x + 4, z + 5)}


def _route_offences(r):
    """The home-routes checker, pure. r {"requested", "deliveries", "developed_invaded" [cells], "maintained",
    "dirt_invaded" [cells], "wild_growth", "cut_samples", "busy_samples", "other_samples", "blocked" [cells]} ->
    offences. Endpoints are never enough: a blocked route cell is reported whatever arrived at the stockpile."""
    out = []
    if r.get("developed_invaded"):
        out.append("growth invaded developed ground (zone/floor/roof): %s" % sorted(r["developed_invaded"])[:6])
    if r.get("maintained") and r.get("dirt_invaded"):
        out.append("the maintained dirt route was invaded: %s" % sorted(r["dirt_invaded"])[:6])
    if r.get("blocked"):
        out.append("route blocked at %s: work there waits, whatever reached the stockpile" % sorted(r["blocked"])[:4])
    if not r.get("blocked") and r.get("deliveries", 0) < r.get("requested", ROUTE_DELIVERIES):
        out.append("routine deliveries incomplete: %d of %d" % (r.get("deliveries", 0), r.get("requested", ROUTE_DELIVERIES)))
    if r.get("busy_samples") and r.get("cut_samples", 0) >= r["busy_samples"]:
        out.append("upkeep consumed all labour (%d of %d busy samples cutting)" % (r["cut_samples"], r["busy_samples"]))
    if r.get("maintained") and not r.get("other_samples"):
        out.append("no independent research/crafting work ran beside the upkeep")
    if not r.get("wild_growth"):
        out.append("unmaintained wilderness never grew: the growers were not active, nothing was tested")
    return out


def _route_growth_offences(r):
    """The ix_route_growth checker, pure. r {"unauthorized" [(pawn, cell)], "developed_invaded" [cells],
    "closed_deliveries", "closed_waiting", "reopened_deliveries", "after_cancel" [cells], "lane_blocked_by_growth"}
    -> offences."""
    out = []
    if r.get("unauthorized"):
        out.append("automatic work entered the hazard without an order: %s" % sorted(r["unauthorized"])[:4])
    if r.get("developed_invaded"):
        out.append("a grower invaded developed ground: %s" % sorted(r["developed_invaded"])[:6])
    if not r.get("closed_deliveries") and not r.get("closed_waiting"):
        out.append("with the safe route closed, supplies neither continued nor visibly waited")
    if not r.get("reopened_deliveries"):
        out.append("supplies never resumed after the detour reopened")
    if r.get("after_cancel"):
        out.append("the canceled expedition walked on into the hazard: %s" % sorted(r["after_cancel"])[:4])
    if not r.get("lane_blocked_by_growth"):
        out.append("withheld lane maintenance: natural growth never reached the lane, the control proves nothing")
    return out


def _vine_cells(t, rect):
    return set((v.get("x"), v.get("z")) for d in (THICKET, WALKER) for v in _things(t, d, _rs(rect), 500))


def _route_site(t, g, crew):
    """Lay the route site: floors, roof and zone on route A, the stockpile, the source pile, the emitters, a research
    bench and `crew` fed colonists at the east end. -> [colonist ids]."""
    t.bridge_call("jawa/set_terrain_batch", ops="WoodPlankFloor:%s" % _rs(g["a_rect"]))
    t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % _rs(g["a_rect"]))
    t.bridge_call("jawa/map_zones", action="createZone", zoneType="stockpile", rect=_rs(g["a_rect"]))
    t.bridge_call("jawa/map_zones", action="createZone", zoneType="stockpile", rect=_rs(g["stock"]))
    t.bridge_call("jawa/map_zones", action="paintArea", area="Home", rect=_rs(_rect(t, ROUTE_SIZE)), value=True)
    sx, sz = g["source"][:2]
    t.bridge_call("jawa/spawn_batch", ops=";".join("WoodLog:%d,%d,1" % (sx + i % 4, sz + i // 4 % 4)
                                                   for i in range(ROUTE_DELIVERIES)))
    t.bridge_call("jawa/set_plants", ops=";".join("%s:%d,%d,1,1" % (THICKET, cx, cz) for cx, cz in g["emit_thicket"]),
                  growth=1.0)
    t.bridge_call("jawa/set_plants", ops=";".join("%s:%d,%d,1,1" % (WALKER, cx, cz) for cx, cz in g["emit_walker"]),
                  growth=1.0)
    t.bridge_call("jawa/spawn_batch", ops="SimpleResearchBench:%d,%d" % (g["stock"][0], g["stock"][1] - 4), stuff="WoodLog")
    crew_ids = []
    for i in range(crew):
        pid = _spawn(t, "Colonist", g["stock"][0] + i % 6, g["stock"][1] + 5 + i // 6 % 4, faction="player")
        _full(t, pid)
        crew_ids.append(pid)
    return crew_ids


def _route_phase(t, g, crew, ticks, cut=False, gale=False, ordered=None):
    """Run `ticks` of colony time in ROUTE_SAMPLE steps. `cut`: designate CutPlant over route B each step (the
    maintenance); `gale`: lock RM_Gale for the first half (one onset). -> {"cut", "busy", "other", "hazard" [(pawn,
    cell)]} sampled from jawa/site_state jobs and list_pawns positions against the vine cells."""
    s = {"cut": 0, "busy": 0, "other": 0, "hazard": []}
    if gale:
        _lock_weather(t, GALE)
    for k in range(max(1, ticks // ROUTE_SAMPLE)):
        if gale and k == ticks // ROUTE_SAMPLE // 2:
            _lock_weather(t, "Clear")
        if cut:
            t.bridge_call("jawa/designate_batch", action="add", designation="CutPlant", rect=_rs(g["b_rect"]))
        t.wait_ticks(ROUTE_SAMPLE)
        jobs = _jobs(t)
        vine = _vine_cells(t, _rect(t, ROUTE_SIZE + 8))
        rows = _rows(t, _rs(_rect(t, ROUTE_SIZE + 8)))
        for pid in crew:
            j = jobs.get(pid)
            if j and j not in _WANDER_JOBS:
                s["busy"] += 1
                s["cut"] += j == "CutPlant"
                s["other"] += j in ("Research", "DoBill")
            c = _xz(rows.get(pid))
            if c in vine and pid != ordered:
                s["hazard"].append((pid, c))
    return s


def _route_readings(t, g):
    vine = _vine_cells(t, _rect(t, ROUTE_SIZE + 8))
    walls = set((w.get("x"), w.get("z")) for w in _things(t, "Wall", _rs(_rect(t, ROUTE_SIZE + 8)), 200))
    return {"deliveries": _stack_total(t, "WoodLog", _rs(g["stock"])), "developed_invaded": sorted(vine & set(g["a"])),
            "dirt_invaded": sorted(vine & set(g["b"])), "wild_growth": len(vine & set(g["wild"])),
            "blocked": sorted((walls | vine) & set(g["b"]))}


@suite.chain("scene_home_routes")
def scene_home_routes(t):
    """sc_home_routes (dependable_home_routes): a developed home round two maintained 3-cell routes (A floored, roofed
    and zoned; B plain dirt kept by CutPlant designations), 20 single wood logs to haul from the west source to the east
    stockpile, a research bench, 40 fed colonists, active creep emitters and walking stands upwind in a wilderness band.
    Creep is compressed (venomvineCreepDays 0.01, the cap at 1) and the wind brings two Gale onsets. Labour, deliveries
    and invaded cells are read; the upkeep percentage is recorded, never claimed. Control: maintenance withheld and one
    wall injected into route B; the checker must then report the invaded or blocked route, not pass on the stockpile.
    The walking form's destination test (RM_VenomvineForms.cs Walk: no plant, no edifice, CanEverPlantAt) does not
    exclude zoned or roofed soil as creep's NaturalFree does, so the developed-ground row may be red at Stage 6."""
    _prep(t, "routes", ROUTE_SIZE)
    x, z = t.anchor
    g = _route_geometry(x, z)
    got = {}

    def body():
        with _comp(t, "routes_site_staged", poison=True):
            if _live(t):
                got["crew"] = _route_site(t, g, ROUTE_CREW)
                if len(_things(t, WALKER, _rs(_rect(t, ROUTE_SIZE + 8)))) < len(g["emit_walker"]):
                    _unmeasured(t, "the walking stands did not stand after set_plants")
                got["wind"] = _lean_wind(t)
                if not got["wind"] or got["wind"][0] <= 0:
                    _unmeasured(t, "the wind %s does not blow east across the site: the emitters are not upwind"
                                   % (got["wind"],))
        with _comp(t, "routes_maintained_carry_work", toggle="venomvineCreepEnabled"):
            if _live(t):
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", 1.0):
                    s1 = _route_phase(t, g, got["crew"], 6000, cut=True, gale=True)
                    s2 = _route_phase(t, g, got["crew"], 6000, cut=True, gale=True)
                r = dict(_route_readings(t, g), requested=ROUTE_DELIVERIES, maintained=True,
                         cut_samples=s1["cut"] + s2["cut"], busy_samples=s1["busy"] + s2["busy"],
                         other_samples=s1["other"] + s2["other"])
                got["maintained"] = r
                _note(t, "maintained routes", r)
                bad = _route_offences(r)
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "routes_withheld_reported"):
            if _live(t):
                ix, iz = g["inject_block"]
                t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (ix, iz), stuff="WoodLog")
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", 1.0):
                    _route_phase(t, g, got["crew"], 6000, cut=False, gale=True)
                r = dict(_route_readings(t, g), requested=ROUTE_DELIVERIES, maintained=False)
                _note(t, "withheld maintenance, one wall injected", r)
                if not r["blocked"]:
                    _fail("the injected wall and withheld upkeep left route B reading clear: the checker cannot see a "
                          "blocked route")
                if not [b for b in _route_offences(r) if "blocked" in b]:
                    _fail("the checker accepted a blocked route from its endpoints: %s" % r)
        with _comp(t, "routes_checker_rejects_injections"):
            if _live(t):
                good = {"requested": 20, "deliveries": 20, "developed_invaded": [], "maintained": True,
                        "dirt_invaded": [], "wild_growth": 9, "cut_samples": 30, "busy_samples": 400,
                        "other_samples": 40, "blocked": []}
                if _route_offences(good):
                    _fail("the routes checker refuses a clean reading: %s" % _route_offences(good))
                injected = {"walking invades a zone": dict(good, developed_invaded=[(1, 2)]),
                            "one cleared path while B invaded": dict(good, dirt_invaded=[(3, 4)]),
                            "upkeep eats all labour": dict(good, cut_samples=400),
                            "blocked accepted from endpoints": dict(good, blocked=[(5, 6)]),
                            "deliveries short": dict(good, deliveries=12),
                            "growers idle": dict(good, wild_growth=0)}
                missed = sorted(k for k, a in injected.items() if not _route_offences(a))
                if missed:
                    _fail("the routes checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "sc_home_routes", "immediate"):
        _stable(t, body)


@suite.chain("scene_ix_route_growth")
def scene_ix_route_growth(t):
    """ix_route_growth (home_routes + ordered_travel + creep + walking on one map): the home_routes site with its natural
    corridor and real work queue, compressed creep and two Gale onsets. Phases: normal work with route B kept; the
    safe route A closed by a wall across it and route B's upkeep withheld (supplies must continue or visibly wait,
    never cross the vine); route A reopened (supplies resume); an ordered expedition across the wilderness band,
    canceled through jawa/stop_job half way (the canceled pawn must not walk on into the hazard). Every sample checks
    each colonist's cell against the vine cells; only the ordered expedition pawn, during its order, may stand in one."""
    _prep(t, "routes", ROUTE_SIZE)
    x, z = t.anchor
    g = _route_geometry(x, z)
    got = {"r": {"unauthorized": [], "after_cancel": []}}
    r = got["r"]

    def body():
        with _comp(t, "ixroutes_site_staged", poison=True):
            if _live(t):
                got["crew"] = _route_site(t, g, ROUTE_CREW)
                got["wind"] = _lean_wind(t)
                if not got["wind"] or got["wind"][0] <= 0:
                    _unmeasured(t, "the wind %s does not blow east across the site" % (got["wind"],))
        with _comp(t, "ixroutes_only_authorized_in_hazard", toggle="venomvineCreepEnabled"):
            if _live(t):
                with _setting(t, "venomvineCreepDays", 0.01), _setting(t, "venomvineCreepCap", 1.0):
                    s = _route_phase(t, g, got["crew"], 6000, cut=True, gale=True)
                    r["unauthorized"] += s["hazard"]
                    sx, sz = g["source"][:2]
                    t.bridge_call("jawa/spawn_batch", ops=";".join("WoodLog:%d,%d,1" % (sx + i % 4, sz + i // 4 % 4)
                                                                   for i in range(ROUTE_DELIVERIES)))
                    d0 = _stack_total(t, "WoodLog", _rs(g["stock"]))
                    bx, bz = g["detour_block"][:2]
                    t.bridge_call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (bx, bz + k) for k in range(3)),
                                  stuff="WoodLog")
                    s = _route_phase(t, g, got["crew"], 6000, cut=False, gale=True)
                    r["unauthorized"] += s["hazard"]
                    d1 = _stack_total(t, "WoodLog", _rs(g["stock"]))
                    r["closed_deliveries"] = d1 - d0
                    r["closed_waiting"] = _stack_total(t, "WoodLog", _rs(g["source"])) > 0
                    r["lane_blocked_by_growth"] = bool(_vine_cells(t, _rect(t, ROUTE_SIZE + 8)) & set(g["b"]))
                    t.bridge_call("jawa/destroy_batch", rects=_rs(g["detour_block"]), categories="Building")
                    s = _route_phase(t, g, got["crew"], 6000, cut=True)
                    r["unauthorized"] += s["hazard"]
                    r["reopened_deliveries"] = _stack_total(t, "WoodLog", _rs(g["stock"])) - d1
                r["developed_invaded"] = sorted(_vine_cells(t, _rect(t, ROUTE_SIZE + 8)) & set(g["a"]))
                _note(t, "route growth phases", dict(r, unauthorized=r["unauthorized"][:6]))
                bad = [b for b in _route_growth_offences(r) if "canceled" not in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "ixroutes_cancel_stops_expedition"):
            if _live(t):
                exp = got["crew"][0]
                wild_vine = sorted(_vine_cells(t, _rect(t, ROUTE_SIZE + 8)) & set(g["wild"]))
                if not wild_vine:
                    _unmeasured(t, "no vine stood in the wilderness band: the expedition would cross no hazard")
                wx, wz = wild_vine[len(wild_vine) // 2]
                _order_goto(t, exp, wx, wz)
                t.wait_ticks(120)
                _ok(t.bridge_call("jawa/stop_job", pawnId=exp), "stop_job(%s)" % exp)
                for _ in range(6):
                    t.wait_ticks(ROUTE_SAMPLE)
                    c = _xz(_rows(t, _rs(_rect(t, ROUTE_SIZE + 8))).get(exp))
                    if c in _vine_cells(t, _rect(t, ROUTE_SIZE + 8)):
                        r["after_cancel"].append(c)
                _note(t, "canceled expedition cells in the vine", r["after_cancel"])
                bad = [b for b in _route_growth_offences(r) if "canceled" in b]
                if bad:
                    _fail("; ".join(bad))
        with _comp(t, "ixroutes_checker_rejects_injections"):
            if _live(t):
                good = {"unauthorized": [], "developed_invaded": [], "closed_deliveries": 0, "closed_waiting": True,
                        "reopened_deliveries": 6, "after_cancel": [], "lane_blocked_by_growth": True}
                if _route_growth_offences(good):
                    _fail("the route-growth checker refuses a clean reading: %s" % _route_growth_offences(good))
                injected = {"automatic crossing": dict(good, unauthorized=[("P1", (1, 1))]),
                            "grower on developed ground": dict(good, developed_invaded=[(2, 2)]),
                            "silent stall": dict(good, closed_waiting=False),
                            "never resumed": dict(good, reopened_deliveries=0),
                            "cancel ignored": dict(good, after_cancel=[(3, 3)]),
                            "control never grew": dict(good, lane_blocked_by_growth=False)}
                missed = sorted(k for k, a in injected.items() if not _route_growth_offences(a))
                if missed:
                    _fail("the route-growth checker passed injected reading(s) %s: it is blind there" % missed)
    with _scene(t, "ix_route_growth", "immediate"):
        _stable(t, body)


# --------------------------------------------------------------------------- scene: economy_observer (offline)

def _economy_offences(before, after, events, reload=False):
    """The economy observer, pure: accounts ONCE for every held object between two snapshots. A snapshot is
    {"tick", "objects": [{"id", "def", "count", "owner", "due", "fraction", "fields": [saved field names]}]}; events
    [{"kind": "consume" | "produce" | "pay", "id", "count"}] are the production events read between them (a payout is
    a produce with its own payout id). `reload`: the second snapshot is the first one saved and loaded. It never
    writes; it names each mismatch. -> offences."""
    out = []
    for name, snap in (("before", before), ("after", after)):
        ids = [o["id"] for o in snap.get("objects") or []]
        for i in sorted(set(i for i in ids if ids.count(i) > 1)):
            out.append("duplicate object %s in the %s snapshot" % (i, name))
    paid = [e["id"] for e in events if e.get("kind") == "pay"]
    for i in sorted(set(i for i in paid if paid.count(i) > 1)):
        out.append("payout %s paid twice" % i)
    b = dict((o["id"], o) for o in before.get("objects") or [])
    a = dict((o["id"], o) for o in after.get("objects") or [])
    flow = {}
    for e in events:
        if e.get("id") not in b and e.get("kind") == "consume":
            out.append("event consumes %s, which no snapshot held" % e.get("id"))
        sign = -1 if e.get("kind") == "consume" else 1
        flow[e.get("id")] = flow.get(e.get("id"), 0) + sign * float(e.get("count", 0))
    for i, o in sorted(b.items()):
        want = float(o.get("count", 0)) + flow.get(i, 0)
        if i not in a:
            if abs(want) > 1e-6:
                out.append("%s (%s) missing: %g unaccounted" % (i, o.get("def"), want))
            continue
        n = a[i]
        if abs(float(n.get("count", 0)) - want) > 1e-6:
            out.append("%s count %g, accounted %g" % (i, float(n.get("count", 0)), want))
        if n.get("owner") != o.get("owner"):
            out.append("%s changed owner %s -> %s with no event" % (i, o.get("owner"), n.get("owner")))
        for f in ("due", "fraction"):
            if o.get(f) is not None and n.get(f) is None:
                out.append("%s lost its saved %s field" % (i, f))
            elif o.get(f) is not None and abs(float(n[f]) - float(o[f])) > 1e-6:
                out.append("%s %s moved %s -> %s (a clock or fraction write)" % (i, f, o[f], n[f]))
        lost = sorted(set(o.get("fields") or []) - set(n.get("fields") or []))
        if lost:
            out.append("%s dropped saved field(s) %s" % (i, lost))
    produced = set(e.get("id") for e in events if e.get("kind") in ("produce", "pay"))
    for i in sorted(set(a) - set(b)):
        if i not in produced:
            out.append("%s (%s) appeared with no production event (a replacement hides a loss)" % (i, a[i].get("def")))
    if reload and after.get("tick") != before.get("tick"):
        out.append("the clock moved across a save and reload: %s -> %s" % (before.get("tick"), after.get("tick")))
    if not reload and (after.get("tick") or 0) < (before.get("tick") or 0):
        out.append("the clock ran backwards: %s -> %s" % (before.get("tick"), after.get("tick")))
    return out


def _economy_fixture():
    """A clean stream over the held kinds the scene names: a smother claim (due tick), a sweetline coat (fraction), a
    vissler arm stack and the felt bank (fraction). Between the snapshots one arm is eaten and the coat pays one felt
    (payout W1); the reload copy is identical."""
    before = {"tick": 120000, "objects": [
        {"id": "Claim_H1", "def": "RM_HollowVenomvine", "count": 1, "owner": "Colony", "due": 240000, "fraction": None,
         "fields": ["claimTick", "dueTick", "blanket"]},
        {"id": "Coat_T1", "def": "RM_SweetlineTree", "count": 1, "owner": None, "due": None, "fraction": 0.85,
         "fields": ["coat"]},
        {"id": "Arm_7", "def": "RM_VisslerArm", "count": 3, "owner": None, "due": None, "fraction": None,
         "fields": ["stackCount"]},
        {"id": "Bank_M", "def": "RM_SweetlineFeltBank", "count": 1, "owner": "Colony", "due": None, "fraction": 2.5,
         "fields": ["banked"]}]}
    after = {"tick": 126000, "objects": [dict(o) for o in before["objects"]]}
    after["objects"][2] = dict(after["objects"][2], count=2)
    after["objects"].append({"id": "W1", "def": "RM_SweetlineWool", "count": 1, "owner": None, "due": None,
                             "fraction": None, "fields": ["stackCount"]})
    events = [{"kind": "consume", "id": "Arm_7", "count": 1}, {"kind": "pay", "id": "W1", "count": 1}]
    return before, after, events


@suite.chain("scene_economy_observer", offline=True, inputs=[])
def scene_economy_observer(t):
    """sc_economy_observer (economy_observer): the observation instrument, offline. The observer accounts once for
    resources consumed, held and paid, and for time, between two snapshots and the production events between them; it
    never writes. Run on the clean fixture it must account with no offence; run on each corrupted stream the plan names
    (a deleted saved claim field, a duplicated payout, a duplicated object, a reset clock, a replacement item, a swapped
    owner, a clock moved across reload) it must name that mismatch. Command:
    `python3 src/RimMandrake/LeaningScrub/validation.py scene_economy_observer` (exit 0 = every row PASS)."""
    before, after, events = _economy_fixture()
    with _comp(t, "economy_observer_accounts_once"):
        bad = _economy_offences(before, after, events) + _economy_offences(before, dict(before), [], reload=True)
        if bad:
            _fail("the observer refuses a clean stream: %s" % bad)
    with _comp(t, "economy_observer_rejects_corruption"):
        def edit(i, **kw):
            a = {"tick": after["tick"], "objects": [dict(o) for o in after["objects"]]}
            a["objects"][i] = dict(a["objects"][i], **kw)
            return a
        dup = {"tick": after["tick"], "objects": after["objects"] + [dict(after["objects"][1])]}
        swap = {"tick": after["tick"], "objects": [dict(o, id="Arm_8") if o["id"] == "Arm_7" else o
                                                   for o in after["objects"]]}
        cases = {"deleted claim field": ((before, edit(0, due=None), events, False), "lost its saved due"),
                 "dropped saved field": ((before, edit(0, fields=["claimTick"]), events, False), "dropped saved field"),
                 "duplicated payout": ((before, after, events + [dict(events[1])], False), "paid twice"),
                 "duplicated object": ((before, dup, events, False), "duplicate object"),
                 "reset clock": ((before, edit(0, due=126000 + 120000), events, False), "due moved"),
                 "replacement item": ((before, swap, events, False), "appeared with no production event"),
                 "swapped owner": ((before, edit(3, owner="Visitors"), events, False), "changed owner"),
                 "clock moved across reload": ((before, dict(before, tick=before["tick"] + 1), [], True), "across a save"),
                 "lost fraction": ((before, edit(1, fraction=None), events, False), "lost its saved fraction")}
        blind = []
        for name, (args, token) in sorted(cases.items()):
            got = _economy_offences(*args)
            if not any(token in g for g in got):
                blind.append("%s (named %s)" % (name, got[:2]))
        _note(t, "economy observer corruption cases", {"cases": len(cases), "blind": blind})
        if blind:
            _fail("the observer passed corrupted stream(s): %s" % blind)


def _run_offline(name):
    """`python3 validation.py <offline scene>`: run one offline chain with no game; exit 0 when every row PASSes."""
    from suite import TestContext
    fn = dict(suite.chains).get(name)
    if fn is None or name not in suite.offline_chains:
        print("no offline chain %r (offline: %s)" % (name, sorted(suite.offline_chains)), file=sys.stderr)
        return 2
    t = TestContext(None, anchor=(0, 0))
    fn(t)
    for c in t.components:
        print("%s.%s %s %s" % (name, c.name, c.verdict, c.detail or ""))
    return 0 if t.components and all(c.verdict == "PASS" for c in t.components) else 1


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
            xref = [m.get("text") for m in (_ok(r2, "drain_log(cross-reference)").get("messages") or [])
                    if any(d in (m.get("text") or "") for d in owned)]
            _note(t, "log scan", {"leaningscrub errors": len(bad), "xref naming our defs": len(xref),
                                  "bufferLines": buf.get("totalInBuffer")})
            if bad or xref:
                _fail("log carries errors: %s" % [str(x)[:160] for x in (bad + xref)[:4]])


if __name__ == "__main__":
    sys.exit(_run_offline(sys.argv[1] if len(sys.argv) > 1 else "scene_economy_observer"))
