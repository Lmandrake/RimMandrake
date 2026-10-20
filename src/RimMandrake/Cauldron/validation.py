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
  * CAULDRON_MECHANICS_BUILD_1 parts 3/4/6 (gas chain): the vent-gas cloud, its burn and the tap are read as STATE off
    the vent's and the tap's own inspect lines ('Vent gas: N cells, peak P; toxic smoke: T cells; burned: B',
    'Gas tap: ... banked X / 60', 'Delivered D units', 'Scaffold: H / M HP'). The cloud's physical drift is read by the
    `drift` chain (RM_MapComponent_VentGas.CentroidOf). NOT driven: its look, studying the rig (an analysis job the bridge
    cannot order).
  * CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD adds: `ruins` (the mapgen census of a generated Cauldron map: the rig, its
    dressing, Oomo's shrine via the Utinni layer), `works` (the Filter-Works converting vent condensate to a reagent item
    and toxic water to fresh water, with a no-cartridge and a no-power control arm) and `drift` (the daily heading and
    the wind -> chance law, read from the live assembly through jawa/static_call, and a seeded cloud's centroid moving
    along that heading under wind and staying put with the drift off).

Settings fields are `public static` (RimMandrake.Cauldron.RM_CauldronSettings). Every arm that
changes one restores it in a `finally`. `jawa/mod_settings_field` never writes ModSettings.xml.
"""
import contextlib
import glob
import json
import math
import os
import re
import sys
import time

from modcheck import Suite, ExpectationFailed
import helpers as H   # noqa: E402 - modcheck puts its own directory on sys.path

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
    "RM_AssayFlecksExtension",
    # CAULDRON_MECHANICS_BUILD_1 parts 3/4: the vent gas, the gas tap, the ruin kit
    "RM_MapComponent_VentGas", "RM_SectionLayer_VentGas", "RM_CompGasTap", "RM_CompProperties_GasTap",
    "RM_PlaceWorker_OnCauldronVent", "RM_CompCauldronRuinKit", "RM_CompProperties_CauldronRuinKit",
    "RM_ScattererValidator_CauldronRuinSite",
    # RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD: the rhossak's binding
    "RM_CompRhossakGrove", "RM_CompProperties_RhossakGrove"))

BIOME = "RM_Cauldron"
WEATHERS = ("RM_ScatterDusk", "RM_VentBloom", "RM_VapourBank", "RM_Dewfall")
BLOOM, HEDIFF = "RM_VentBloom", "RM_VentMetalLoad"
VEXXISS, SUUSH, ZISSKA, ESKITH = "RM_Vexxiss", "RM_Suush", "RM_Zisska", "RM_Eskith"
NATIVES = (SUUSH, VEXXISS, ZISSKA, ESKITH)             # the biome's own, MayRequire-free wildAnimals rows
RHOSSAK, GALLED = "RM_Rhossak", "RM_GalledRhossak"        # RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD (owner by card 2026-10-19)
RHOSSAK_TETHER = 10                                        # RM_CompProperties_HomeTether.tetherRadius on both defs
THORN, NETTLE = "RM_TwistingThornwood", "RM_RavenNettle"   # RM_TreeMartyr cut (owner, tree tiers sheet 2026-10-18)
LETTER_LABEL = "Vexxiss poisoning water"
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
        "bloom": (-45, 45), "water": (0, 45), "fire": (45, 45), "spawn": (0, -45), "gas": (-85, -85), "works": (85, -85),
        "drift": (85, 85), "rhossak": (-85, 85)}
GAS_TAP, TANK, RIG = "RM_VentGasTap", "RM_LiquidTank", "RM_CorrodedFilterRig"     # CAULDRON_MECHANICS_BUILD_1 parts 3/4
VWORKS, REAGENT, BATTERY = "RM_FilterWorks", "RM_VentReagent", "Battery"          # CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD
COND, TOXICW, FRESHW = "RM_Liquid_VentCondensate", "RM_Liquid_ToxicWater", "RM_Liquid_FreshWater"
SHRINE = "RUT_OomoGrudgingShrine"      # Utinni layer (src/RimUtinni/UtinniPatches), patched into the rig's shrineDefs
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
    wanted = ("ThingDef", "PawnKindDef", "WeatherDef", "HediffDef", "TerrainDef", "BiomeDef", "JobDef", "RecipeDef", "DamageDef",
              "ResearchProjectDef", "GenStepDef")
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


def _remove_pawn(t, pid, raw=False):
    """Take one pawn off the map with NO death: Destroy(Vanish), no corpse, no death action, read back by
    destroyedAfter. LIVE 2026-10-16 (SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES, HARNESS): the old kill was ONE
    jawa/damage Bullet 5000, which lands on ONE body part; on a hand it takes the hand and the pawn lives. The
    vent_exposure_is_local OFF arm's colonists Lu (MissingBodyPart/Hand, health 0.44) and Lili (BloodLoss, 0.6)
    survived it and bled into vexxiss_drinks_vent's first 60-tick wait -- the 'colonist hurt near a vexxiss drink'
    of 2 of 2 runs, before the vexxiss was even spawned. A suush would also detonate on a real death. Falls back to the
    bullet only when the vanish does not read back. -> True when the pawn is gone."""
    call = t.session.call if raw else t.bridge_call     # raw: the _stable teardown, when bridge_call is a no-op
    v = call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish") or {}
    if v.get("destroyedAfter") is True:
        return True
    call("jawa/damage", damageDef="Bullet", amount=5000, thingId=pid, allowColonists=True)
    return False


def _kill_pawns_in(t, rect, raw=False):
    """Remove every living pawn in rect (by id, _remove_pawn: destroy_batch NEVER removes pawns,
    DESTROY_BATCH_NEVER_KILLS_PAWNS_1), except the site's own bystanders, which are settled, never shot; returns the
    count removed."""
    r = (t.session.call if raw else t.bridge_call)("jawa/list_pawns", limit=500, rect=_rs(rect))
    keep = set(getattr(t, "_bystanders", ()) or ())
    n = 0
    for p in ((r or {}).get("pawns") or []):
        if p.get("dead") or not p.get("id") or p["id"] in keep:
            continue
        _remove_pawn(t, p["id"], raw=raw)
        n += 1
    return n


def _kill_kind_near(t, kind, radius=60):
    """Remove every living `kind` pawn within `radius` of the anchor: a stray (a wild native, or one an earlier failed
    chain left behind) drinks the vent first and silences it, which reads as the vent ignoring the test's own animal."""
    x, z = t.anchor
    r = t.bridge_call("jawa/list_pawns", limit=500, rect=_rs((x - radius, z - radius, 2 * radius, 2 * radius)))
    n = 0
    for p in ((r or {}).get("pawns") or []):
        if p.get("dead") or not p.get("id") or p.get("kindDef") != kind:
            continue
        _remove_pawn(t, p["id"])
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
    _open_sky(t, r)
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (SOIL, _rs(r)), layer="top")
    _settle_bystanders(t)
    _clear_wildlife(t)


def _clear_wildlife(t):
    """SITE, LIVE modcheck6 2026-10-16: the map's own wildlife fought (a mink and a toughspike) and then hurt drafted
    site colonist Mullen (BloodLoss), and that hurt stopped the gas chain's safe_advance, so vent_gas_burns_toxic and
    the rest of the chain went UNMEASURED. No Cauldron row reads an animal it did not spawn, and every chain spawns its
    fixtures after _prep, so the factionless animals are removed (no death, no corpse, no detonation) here, as
    Contagion does (helpers.kill_wildlife)."""
    if not _live(t):
        return
    try:
        res = H.kill_wildlife(t.session)
        if res.acted or res.residue:
            _note(t, "mapgen wildlife removed", {"removed": res.acted, "verified": res.verified,
                                                 "residue": res.residue[:8]})
    except Exception as ex:    # upkeep: a failure is evidence, never a verdict
        _note(t, "wildlife not cleared", str(ex)[:200])


def _open_sky(t, rect, raw=False):
    """Remove every roof over `rect`, right after it was cleared. LIVE modcheck4 2026-10-16 (Autosave-6 letters): the
    site map is mountainous, clear_area's destroy_batch takes the natural rock out from under RoofRockThick, the roof
    is left 'too far from any support', and on the FIRST tick after setup it collapses: the yield colonist spawned at
    (170,131) was 'crushed to death' (Roof collapse letter, tick 801), and the gas pad at (40,40) sits under thick
    roof whose collapse leaves CollapsedRocks (a Full-fillage edifice) on the vent, where GasGrid.GasCanMoveTo refuses
    every cell, so the vent emits nothing (vent_gas_emits FAIL 'cells 0 peak 0'). A collapse skips unroofed cells
    (RoofCollapserImmediate.DropRoofInCells checks Roofed), so stripping the roof before any tick defuses it. A chain
    that needs a roof (the bloom room) builds its own after this. `raw` calls the session directly (the _stable
    teardown runs after a chain may have failed, when t.bridge_call is a no-op)."""
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
        print("%s roof strip failed over %s: %s" % (TAG, _rs(rect), ex), file=sys.stderr, flush=True)


def _settle_bystanders(t):
    """The site's own colonists, mended and drafted at chain setup (helpers.settle_bystanders), as LeaningScrub does.
    LIVE modcheck4 2026-10-16: site colonist Per was hurt (arm lost) and later downed mid-chain, and the vitals latch
    ended the water and vents chains UNMEASURED. No Cauldron row reads a site colonist: every row spawns its own."""
    if not _live(t):
        return
    try:
        res = H.settle_bystanders(t.session)
        t._bystanders = list(res.evidence.get("bystanders") or [])     # _kill_pawns_in never shoots these
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


def _mend_pawn(t, pid):
    """Make ONE test pawn unhurt and fed, by exact id: remove every INJURY_DEFS hediff, refill needs. LIVE 2026-10-20
    (Cauldron run 19c, HARNESS): the yield colonist was hurt (Crack/Clavicle) and the vitals latch stopped safe_advance
    at 60 ticks, so harvest_pays_metal, yield_factor_scales and yield_toggle_off were UNMEASURED. Same removal route as
    helpers.settle_bystanders (jawa/pawn_health remove), applied to the fixture itself before each wait. Upkeep, never
    a verdict: returns the list of removed hediffs, [] when none or unreadable."""
    if not _live(t):
        return []
    removed = []
    try:
        row = _rows(t, health=True).get(pid) or {}
        for h in (row.get("health") or {}).get("hediffs") or []:
            if h.get("def") not in H.INJURY_DEFS:
                continue
            r = t.bridge_call("jawa/pawn_health", pawn=pid, action="remove", hediff=h["def"], bodyPart=h.get("part") or "")
            if not (r or {}).get("success") and h.get("part"):
                t.bridge_call("jawa/pawn_health", pawn=pid, action="remove", hediff=h["def"])
            removed.append((h["def"], h.get("part")))
        _full(t, pid)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Joy", level=1.0)
        if removed:
            _note(t, "test pawn mended", removed)
    except Exception as ex:    # upkeep: a failure is evidence, never a verdict
        _note(t, "test pawn not mended", str(ex)[:200])
    return removed


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
    try:
        _set(t, field, value)       # inside the try: a failed read-back still restores the shipped default
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
            _note(t, "RESTORE FAILED %s" % field, {"got": got, "set": r})
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
            elif time.time() - stall > 30:
                # LeaningScrub LIVE 2026-10-07: Ultrafast left the clock frozen while stepped waits advanced normally.
                # Step the rest (exact) rather than failing the component on a harness clock.
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
    """Run a chain body, then ALWAYS release the weather lock and clear the pad's pawns and things."""
    try:
        fn()
    finally:
        _unlock_weather(t)
        if t.session is not None and getattr(t, "anchor", None):
            try:    # pawns first, by id (destroy_batch never removes them); then their corpses with the things
                _kill_pawns_in(t, _rect(t, PAD_SIZE + 24), raw=True)
                t.session.call("jawa/destroy_batch", rects=_rs(_rect(t, PAD_SIZE + 24)),
                               categories="All")
            except Exception as ex:
                print("%s pad cleanup failed: %s" % (TAG, ex), file=sys.stderr, flush=True)
            _open_sky(t, _rect(t, PAD_SIZE + 24), raw=True)   # its own guard: the teardown takes rock and the bloom room's walls


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
    # timeException=True: bloom exposure tick only fires on interval multiples; a short clock set avoids a long run (safe-advance gate)
    t.bridge_call("jawa/time_set_ticks", ticks=int(nxt - lead), timeException=True)
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


# --------------------------------------------------------------------------- chain: ruins at mapgen (read-only, FIRST after load)
# CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD. Runs before any chain clears a pad: the census is of the map AS GENERATED
# (the registered saved site IS a freshly generated RM_Cauldron map, prep_site.py step 5). A map that is not a Cauldron
# map is UNMEASURED: RM_ScattererValidator_CauldronRuinSite refuses every other biome by design.

def _static(t, typ, method, args):
    """jawa/static_call result as text; a refused call is UNMEASURED (could not ask), never a number."""
    r = t.bridge_call("jawa/static_call", type=typ, method=method, args=args)
    if not _live(t):
        return ""
    if not isinstance(r, dict) or r.get("success") is False:
        _unmeasured(t, "static_call %s.%s(%s) refused: %r" % (typ, method, args, r))
    return str(r.get("result"))


def _mapgen_rigs(t):
    """The corroded filter rigs on a map that must be a freshly generated Cauldron map; UNMEASURED otherwise."""
    mi = t.bridge_call("jawa/map_info") or {}
    if _live(t) and mi.get("mapBiome") != BIOME:
        _unmeasured(t, "the map's biome is %r, not %s: the ruin scatterer refuses every other biome by design" %
                    (mi.get("mapBiome"), BIOME))
    return _things(t, RIG)


@suite.chain("ruins")
def ruins_chain(t):
    """CAULDRON_MECHANICS_BUILD_1 part 4/6 at mapgen: the ruin set-piece (one corroded filter rig per Cauldron map),
    its dressing, and Oomo's grudging shrine patched into the kit by the Utinni layer. Reads only."""
    with _comp(t, "ruin_rig_at_mapgen", toggle="ruinKitEnabled"):
        if _live(t):
            rigs = _mapgen_rigs(t)
            _note(t, "rigs on the generated map", [(r.get("x"), r.get("z")) for r in rigs])
            # LIES: 0 is also what a map with no dry open unroofed 7x7 reads (warnOnFail false), and a rig inside an
            # earlier run's cleared pad is gone; a registered saved site loaded fresh has neither (count it on a 2nd map).
            if not rigs:
                _fail("a generated RM_Cauldron map holds no %s: RM_CauldronRuinScatter did not place its set-piece" % RIG)
            _STATE["rigs"] = [(r["x"], r["z"]) for r in rigs]
    with _comp(t, "ruin_site_dressed_at_mapgen"):
        if _live(t):
            rigs = _STATE.get("rigs")
            if not rigs:
                _unmeasured(t, "no rig read by ruin_rig_at_mapgen")
            bad = []
            for rx, rz in rigs:
                rect = _rs((rx - 7, rz - 7, 15, 15))
                tanks = _things(t, TANK, rect)
                pipes = _count(t, "AncientPipe", rect)
                toxic = 0
                for tk in tanks:
                    _l, lines = _inspect(t, tk["id"])
                    if "toxic water" in " | ".join(str(x) for x in lines).lower():
                        toxic += 1
                # the interaction cell (rig pos + (0,-1)) and the ring around it stay open: a piece on it makes the
                # rig unstudiable, and studying it is the only road to the Filter-Works research
                blockers = [tk for tk in tanks if rx - 2 <= tk["x"] <= rx + 1 and rz - 3 <= tk["z"] <= rz]
                for d in ("AncientPipe", "AncientStorageCylinder", "ChunkSlagSteel"):
                    blockers += _things(t, d, _rs((rx - 1, rz - 2, 3, 3)))
                _note(t, "dressing at rig (%d,%d): tanks / toxic tanks / pipes / blockers" % (rx, rz),
                      [len(tanks), toxic, pipes, len(blockers)])
                if len(tanks) < 1 or pipes < 1:
                    bad.append("rig (%d,%d) undressed: tanks %d, pipes %d" % (rx, rz, len(tanks), pipes))
                elif toxic < 1:
                    bad.append("rig (%d,%d): %d tank(s) but none holds toxic water" % (rx, rz, len(tanks)))
                if blockers:
                    bad.append("rig (%d,%d): %d piece(s) on its interaction cell ring" % (rx, rz, len(blockers)))
            if bad:
                _fail("; ".join(bad))
    with _comp(t, "oomo_shrine_at_mapgen"):
        if _live(t):
            rigs = _STATE.get("rigs")
            if not rigs:
                _unmeasured(t, "no rig read by ruin_rig_at_mapgen")
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % SHRINE, fields="defName", limit=5)
            if (r or {}).get("notFound") or not (r or {}).get("foundCount"):
                _unmeasured(t, "%s does not resolve: the Utinni patch layer is not on this tier (the RM tier names no god by ruling)" % SHRINE)
            missing = []
            for rx, rz in rigs:
                n = _count(t, SHRINE, _rs((rx - 7, rz - 7, 15, 15)))
                if n < 1:
                    missing.append((rx, rz))
                else:
                    sh = _things(t, SHRINE, _rs((rx - 7, rz - 7, 15, 15)))
                    if sh:
                        _l, lines = _inspect(t, sh[0]["id"])
                        _note(t, "shrine inspect (usability is INFERRED from the def: Natural meditation focus 0.12)", lines)
            if missing:
                _fail("%s resolves but no shrine stands within 7 cells of rig(s) %s: the Utinni patch (Cauldron_OomoShrine.xml) "
                      "did not reach the kit's shrineDefs, or the placement found no free cell" % (SHRINE, missing))


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
                  "dewfallBeadsEnabled", "dewfallSaturationEnabled", "assayFlecksEnabled", "vexxissPrintsEnabled",
                  # CAULDRON_MECHANICS_BUILD_1: ventGasDrifts' OFF arm is driven by drift.gas_cloud_moves_along_heading
                  # (this roundtrip only proves the field persists); the toxic-smoke
                  # OFF arm is masked by the ON arm's vanilla tox residue unless the suite waits it out (the ON arm is
                  # gas.vent_gas_burns_toxic); the ruin kit is worldgen (a fresh Cauldron map).
                  "ventGasDrifts", "ventGasToxicSmoke", "ruinKitEnabled",
                  # RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD: a sprout needs a SLEEPING rhossak and a 3 h mean wait; a grove needs three awake
                  # rhossak held together for 24 unbroken in-game hours. Both are owed live rows (ledger note), not driven here.
                  "rhossakSproutEnabled", "rhossakGroveEnabled"):
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
                cells, answers = {}, {}
                for i, d in enumerate(FLORA):
                    cx, cz = rect[0] + 2 + (i % 4) * 3, rect[1] + 2 + (i // 4) * 3 + 8
                    cells[d] = (cx, cz)
                    if d in SOIL_FORBIDDEN:
                        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,1,1" % (ROCK, cx, cz), layer="top")
                    answers[d] = t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, cx, cz), growth=1.0)
                lost = [d for d, (cx, cz) in cells.items() if _count(t, d, "%d,%d,1,1" % (cx, cz)) < 1]
                # A lost def carries its own set_plants answer (planted / rejected + reason) and what stands on its cell,
                # so 'refused by the cell' (SITE: a leftover on the pad) and 'planted then gone' (MOD) are told apart.
                why = {}
                for d in lost:
                    cx, cz = cells[d]
                    a = answers.get(d) or {}
                    on = t.bridge_call("jawa/list_things", limit=10, rect="%d,%d,1,1" % (cx, cz))
                    why[d] = {"planted": a.get("planted"), "rejected": a.get("rejected"), "reasons": a.get("reasons"),
                              "errors": a.get("errors"), "cell": [cx, cz],
                              "onCell": [th.get("def") for th in ((on or {}).get("things") or [])]}
                _note(t, "flora set", {"asked": len(FLORA), "lost": lost, "why": why})
                if lost:
                    _fail("plant def(s) did not stand after set_plants: %s (%s)" % (lost, json.dumps(why)[:600]))
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
    _mend_pawn(t, col)      # an unhurt harvester: a hurt one stops safe_advance and the row goes UNMEASURED
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
        _mend_pawn(t, col)
    got = _stack_total(t, "WoodLog", _rs(rect)) - before
    if got < 1 and _live(t):
        # LIVE modcheck5 2026-10-16: 'no wood in 5000 ticks' with nothing else read. Evidence for the next round: is the
        # tree still standing, what is the harvester doing, and where is it (a haul off the pad vs a job never done).
        try:    # evidence only: a failed read must not turn the caller's UNMEASURED into a FAIL
            rows = _rows(t)
            _note(t, "harvest gave no wood: tree still standing / harvester job / harvester at",
                  [bool(_things(t, THORN, "%d,%d,1,1" % (x, z))), _jobs(t).get(col),
                   [(rows.get(col) or {}).get(k) for k in ("x", "z", "drafted", "downed")]])
        except Exception as ex:
            _note(t, "harvest evidence unread", str(ex)[:200])
    return got


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
                    t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (THORN, x - 4 + i * 4, z - 6), growth=1.0)
                trees = sorted(_things(t, THORN, _rs(rect)), key=lambda w: w.get("x", 0))
                if len(trees) != 3:
                    _unmeasured(t, "expected 3 twisting thornwoods after set_plants, read %d" % len(trees))
                ids["trees"] = trees
                ids["col"] = _spawn(t, "Colonist", x, z + 6, faction="player")
                _full(t, ids["col"])
                if _stack_total(t, "Steel", _rs(rect)) != 0:
                    _unmeasured(t, "steel already on the pad before any harvest")
        with _comp(t, "harvest_pays_metal", toggle="metalYieldEnabled"):
            if _live(t):
                wood = _harvest_one(t, ids["col"], ids["trees"][0], rect)
                steel = _stack_total(t, "Steel", _rs(rect))
                _note(t, "thornwood harvest 1 (factor 1.0): wood / steel", [wood, steel])
                if wood < 1:
                    _unmeasured(t, "no wood from the first harvest in 5000 ticks (job not done): "
                                   "cannot judge the metal beside it")
                if not (THORN_FULL - 1 <= steel <= THORN_FULL + 1):
                    _fail("a full-grown twisting thornwood paid %d steel beside %d wood, expected ~%d"
                          % (steel, wood, THORN_FULL))
                ids["steel1"] = steel
        with _comp(t, "yield_factor_scales", toggle="metalYieldFactor"):
            if _live(t):
                if "steel1" not in ids:
                    _unmeasured(t, "no factor-1.0 baseline (harvest_pays_metal did not pay)")
                with _setting(t, "metalYieldFactor", 2.0):
                    wood = _harvest_one(t, ids["col"], ids["trees"][1], rect)
                steel2 = _stack_total(t, "Steel", _rs(rect)) - ids["steel1"]
                _note(t, "thornwood harvest 2 (factor 2.0): wood / steel", [wood, steel2])
                if wood < 1:
                    _unmeasured(t, "no wood from the second harvest in 5000 ticks")
                if not (2 * THORN_FULL - 2 <= steel2 <= 2 * THORN_FULL + 2):
                    _fail("metalYieldFactor 2.0 paid %d steel from a full twisting thornwood, expected ~%d "
                          "(factor 1.0 paid %d)" % (steel2, 2 * THORN_FULL, ids["steel1"]))
                ids["steel_total"] = ids["steel1"] + steel2
        with _comp(t, "yield_toggle_off", toggle="metalYieldEnabled"):
            if _live(t):
                if "steel_total" not in ids:
                    _unmeasured(t, "no steel baseline from the earlier harvests")
                with _setting(t, "metalYieldEnabled", False):
                    wood = _harvest_one(t, ids["col"], ids["trees"][2], rect)
                steel3 = _stack_total(t, "Steel", _rs(rect)) - ids["steel_total"]
                _note(t, "thornwood harvest 3 (metalYieldEnabled OFF): wood / steel", [wood, steel3])
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
    # The biome's OWN natives are asked first. LIVE 2026-10-16 (SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES, HARNESS):
    # asked only the stock herbivores, the picker read [None, "Deer"] on the RM_Cauldron site, because no stock
    # herbivore is on RM_Cauldron's roster, and bloom_spares_natives went UNMEASURED. The row spawns its own pair, so
    # the site's wildlife census is beside the point. Zisska first: a plain grazer (the suush detonates on death, the
    # vexxiss drinks vents and beats fires, the eskith hushes in a falter).
    pref = (ZISSKA, ESKITH, VEXXISS, SUUSH)
    r = t.bridge_call("jawa/biome_probe", biomes=biome, find=",".join(pref + HERBIVORES))
    rows = (r or {}).get("biomes") or []
    if not rows:
        return None, None
    states = dict((x.get("defName"), x.get("state")) for x in (rows[0].get("findResults") or []))
    native = [k for k in pref + HERBIVORES if states.get(k) == "spawning"]
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
                # SEAL the room: make_empty_room always cuts a door, and a drafted pawn left waiting is auto-undrafted
                # by vanilla AutoUndrafter after 10000 ticks (this chain's transition wait + clock jump reach that),
                # after which the indoor colonist walks out and is honestly exposed (bloom_spares_roofed FAIL,
                # LIVE 2026-10-16). The door becomes a wall; the colonist's own cell is re-read at the verdict.
                door = (room or {}).get("doorAt") or {}
                if door.get("x") is not None:
                    t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (door["x"], door["z"]), categories="All")
                    t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (door["x"], door["z"]), stuff="Steel")
                if _live(t) and (door.get("x") is None or _count(t, "Door", "%d,%d,9,9" % (x - 11, z - 4)) != 0
                                 or _count(t, "Wall", "%d,%d,1,1" % (door["x"], door["z"])) != 1):
                    _unmeasured(t, "could not seal the roofed room (door %r still open): an indoor colonist "
                                   "can walk out" % (door,))
                ids["out"] = _spawn(t, "Colonist", x + 6, z + 8, faction="player")
                ids["in"] = _spawn(t, "Colonist", x - 7, z, faction="player")
                for p in (ids["out"], ids["in"]):
                    _full(t, p)
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
                at = _xz(row)
                _note(t, "indoor colonist cell at the verdict", at)
                if at is None or not (x - 10 <= at[0] <= x - 4 and z - 3 <= at[1] <= z + 3):
                    _unmeasured(t, "the indoor colonist is not inside the sealed room at the verdict (%r): "
                                   "its exposure says nothing about the roof" % (at,))
                if not _roofed(t.bridge_call("jawa/get_roof_batch", rects="%d,%d,1,1" % at)):
                    _unmeasured(t, "the indoor colonist's own cell %r reads unroofed" % (at,))
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
                # a leftover load (toggle_off's removal failing) would add to the factor-2 tick and read as ratio ~3
                t.bridge_call("jawa/pawn_health", pawn=ids["out"], action="remove", hediff=HEDIFF)
                if _hediff(_rows(t, health=True).get(ids["out"]), HEDIFF) is not None:
                    _unmeasured(t, "could not clear %s before the factor-2.0 tick: the ratio would be cumulative" % HEDIFF)
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
                again = {}
                for attempt in range(3):
                    # re-read where the vexxiss stands NOW (it wanders) and re-lay clean water under it each attempt,
                    # so the poison tick (every 60 ticks, own cell must be WaterShallow) is reached twice
                    row = _rows(t).get(ids["A"])
                    if row is None or not _xz(row):
                        _unmeasured(t, "vexxiss A is gone, cannot re-lay water under it")
                    vx, vz = _xz(row)
                    around = "%d,%d,7,7" % (vx - 3, vz - 3)
                    t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%s" % around, layer="top")
                    t.wait_ticks(120)       # clean water UNDER the same vexxiss: it must poison again
                    again = _terrain(t, around)
                    if _toxic_cells(again) >= 1:
                        break
                    _note(t, "re-laid water attempt %d: vexxiss at / terrain" % (attempt + 1), [(vx, vz), again])
                if _toxic_cells(again) < 1:
                    _unmeasured(t, "the vexxiss did not poison the re-laid water in 3 attempts, so the warn path was "
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
                _kill_kind_near(t, VEXXISS)       # a stray vexxiss would drink this vent silent before the drink rows
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
        with _comp(t, "fauna_hush_in_falter", toggle="faunaHushEnabled"):
            # CAULDRON_MECHANICS_BUILD_1 part 1: while the vents falter, wild natives hold still (Wait_MaintainPosture).
            if _live(t):
                def falter_job(on):
                    _lock_weather(t, "RM_ScatterDusk")
                    if _transition_done(t) is None:
                        _unmeasured(t, "the weather never settled on scatter-dusk")
                    with _setting(t, "faunaHushEnabled", on):
                        pid = _spawn(t, ESKITH, x + 6, z + 6)
                        _full(t, pid)
                        _lock_weather(t, BLOOM)
                        t.wait_ticks(480)
                        _o, st = vent()
                        jobs = _jobs(t)
                        if pid not in jobs:
                            _unmeasured(t, "the spawned eskith %s is not on the map" % pid)
                        job = jobs.get(pid)
                        kill_pawns()
                    return st, job
                st1, job1 = falter_job(True)
                _note(t, "ON: vent state / eskith job in the falter", [st1, job1])
                if st1 != "faltering":
                    _unmeasured(t, "the vents were not faltering when the eskith was read (%r)" % st1)
                if job1 != "Wait_MaintainPosture":
                    _fail("the vents falter but a wild eskith is not holding still (job %r)" % job1)
                st2, job2 = falter_job(False)
                _note(t, "OFF: vent state / eskith job in the falter", [st2, job2])
                if st2 != "faltering":
                    _unmeasured(t, "OFF arm: the vents were not faltering (%r)" % st2)
                if job2 == "Wait_MaintainPosture":
                    _fail("faunaHushEnabled OFF but the eskith still holds still in the falter")
                _lock_weather(t, "RM_ScatterDusk")
                _transition_done(t)
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
                _kill_kind_near(t, VEXXISS)
                _lock_weather(t, "RM_ScatterDusk")
                t.wait_ticks(60)
                ids["v1"] = _spawn(t, VEXXISS, x + 9, z)
                _full(t, ids["v1"])
                seen = took_job(ids["v1"])
                _note(t, "wild vexxiss took %s" % DRINK_JOB, seen)
                if not seen:
                    _fail("a wild vexxiss 9 cells from a breathing vent never took %s in 1800 ticks (toggle ON)" % DRINK_JOB)
                # The job is seen from its first toil (the walk to the vent); suppression starts only once it drinks.
                # LIVE modcheck5 2026-10-16: one read 300 ticks after the job was seen found no suppression. Poll up to
                # 1500 ticks, recording where the vexxiss is and what it does, so a slow walk and a drink that suppresses
                # nothing are told apart.
                trail, drunk = [], False
                for _ in range(10):
                    t.wait_ticks(150)
                    _o, st = vent()
                    vr = _rows(t).get(ids["v1"]) or {}
                    trail.append([_jobs(t).get(ids["v1"]), vr.get("x"), vr.get("z"), st])
                    if "drunk" in _STATE.get("vent_text", "") or st == "silenced":
                        drunk = True
                        break
                _note(t, "vexxiss job / x / z / vent state per 150 ticks", trail)
                if not drunk:
                    _fail("the vexxiss took %s but the vent shows no suppression after 1500 ticks: %r (vent at %d,%d)"
                          % (DRINK_JOB, _STATE.get("vent_text"), x, z))
                kill_pawns()
                if vent()[1] == "silenced":    # a silenced vent is drunk by nobody: the OFF arm would pass for nothing
                    _unmeasured(t, "OFF arm: the vent is already silenced, so no drink job is a meaningful 'no'")
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


# --------------------------------------------------------------------------- chain: the vent gas (part 3/4)

def _gas_read(t, vid):
    """The vent's gas line as a dict: cells, peak, tox, burned, capped. Unreadable is UNMEASURED, never a number."""
    _label, lines = _inspect(t, vid)
    if not _live(t):
        return {}
    txt = " | ".join(str(l) for l in lines)
    if "Vent gas: capped by a gas tap" in txt:
        return {"capped": True}
    m = re.search(r"Vent gas:\s*(\d+) cells, peak (\d+); toxic smoke:\s*(\d+) cells; burned:\s*(\d+)", txt)
    if not m:
        _unmeasured(t, "the vent's inspect lines carry no 'Vent gas' line: %r" % lines)
    return {"capped": False, "cells": int(m.group(1)), "peak": int(m.group(2)), "tox": int(m.group(3)),
            "burned": int(m.group(4))}


def _tap_read(t, tid):
    """(banked, delivered, hp) from the gas tap's inspect lines."""
    _label, lines = _inspect(t, tid)
    if not _live(t):
        return None, None, None
    txt = " | ".join(str(l) for l in lines)
    b = re.search(r"condensate banked\s*([0-9.]+)", txt)
    d = re.search(r"Delivered\s*(\d+) units", txt)
    h = re.search(r"Scaffold:\s*(\d+)\s*/", txt)
    if not b or not d or not h:
        _unmeasured(t, "the gas tap's inspect lines carry no banked / delivered / HP: %r" % lines)
    return float(b.group(1)), int(d.group(1)), int(h.group(1))


@suite.chain("gas")
def gas_chain(t):
    """CAULDRON_MECHANICS_BUILD_1 part 3/4/5: the new vent-gas type, its burn into vanilla tox gas, the gas-tap scaffold, a
    vexxiss prying at it, and the corroded ruin kit dressing its site. State reads only (inspect lines, thing counts)."""
    _prep(t, "gas")
    x, z = t.anchor
    ids = {}

    def gas():
        return _gas_read(t, ids["vent"])

    def body():
        with _comp(t, "gas_site_ready", poison=True):
            if _live(t):
                _lock_weather(t, "RM_ScatterDusk")
                _kill_kind_near(t, VEXXISS)
                _ok(t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,1" % (VENT, x, z)), "spawn_batch(vent)")
                rows = _things(t, VENT, _rs(_rect(t)))
                if not rows:
                    _unmeasured(t, "the spawned %s is not on the map" % VENT)
                ids["vent"] = rows[0]["id"]
                _wait(t, 1500)
                _note(t, "vent gas after 1500 ticks", gas())
        with _comp(t, "vent_gas_emits", toggle="ventGasEnabled"):
            if _live(t):
                g = gas()
                if g.get("capped"):
                    _unmeasured(t, "the fresh vent reads capped")
                if g["cells"] <= 0 or g["peak"] <= 0:
                    # SITE before MOD: a gas-tight edifice on the vent (CollapsedRocks from a roof collapse, modcheck4)
                    # makes GasGrid.GasCanMoveTo refuse every vent cell, so AddGas rightly adds nothing.
                    rocks = _things(t, "CollapsedRocks", "%d,%d,2,2" % (x, z))
                    if rocks:
                        _unmeasured(t, "CollapsedRocks stand on the vent (%d): gas cannot enter those cells, so this "
                                       "site cannot show emission" % len(rocks))
                    _fail("a breathing vent made no gas in 1500 ticks: %r" % g)
                # isolation guard: unburned vent gas is its own type, never vanilla tox gas
                if g["tox"] != 0:
                    _fail("vanilla tox gas around a vent that never burned (%d cells): the new type leaks into the old" % g["tox"])
                with _setting(t, "ventGasEnabled", False):
                    _wait(t, 1500)
                    g_off = gas()
                _note(t, "ON / OFF arm", [g, g_off])
                if g_off["peak"] >= g["peak"]:
                    _fail("ventGasEnabled OFF but the cloud kept its peak (%d -> %d)" % (g["peak"], g_off["peak"]))
        with _comp(t, "vent_gas_burns_toxic", toggle="ventGasIgnites"):
            if _live(t):
                _wait(t, 1500)                                   # let the cloud rebuild after the OFF arm
                g0 = gas()
                if g0["peak"] < 24:
                    _unmeasured(t, "the cloud is too thin to ignite (peak %d)" % g0["peak"])
                # One fire cell for both arms, directly under the vent's bottom row (x, z-1): its 8 neighbours include
                # two vent cells, where the emission lands. ON arm first (the positive control), then OFF at the same
                # cell once the cloud has rebuilt. `burned` is map-wide; nothing else burns on this pad.
                fx, fz = x, z - 1

                def light(ticks):
                    _ok(t.bridge_call("jawa/spawn_batch", ops="WoodLog:%d,%d,10" % (fx, fz)), "spawn_batch(wood)")
                    r = t.bridge_call("jawa/map_fire", action="start", rect="%d,%d,1,1" % (fx, fz), fireSize=1.0)
                    if not (r or {}).get("firesStarted"):
                        _unmeasured(t, "map_fire lit nothing beside the vent: %r" % r)
                    # LIVE modcheck5 2026-10-16: the burn's tox gas is a small puff (4 thin cells -> ~16 density each)
                    # that vanilla diffuses and dissipates; one read 600 ticks later found it gone (round 1 caught 3 cells
                    # left). So the window is read every 60 ticks and `tox` is the most smoke seen at any read.
                    after, tox_max, step = None, 0, 60
                    for _ in range(max(1, ticks // step)):
                        _wait(t, step)
                        after = gas()
                        if after.get("capped"):
                            _unmeasured(t, "the vent reads capped during the burn window: no gas line to read")
                        tox_max = max(tox_max, after.get("tox") or 0)
                    after = dict(after, tox=tox_max)
                    t.bridge_call("jawa/map_fire", action="extinguish", rect=_rs(_rect(t)))
                    return after

                g1 = gas()
                g2 = light(600)
                _note(t, "ON arm: before / after the fire", [g1, g2])
                if g2["burned"] <= g1["burned"]:
                    _fail("a fire for 600 ticks under a thick cloud (peak %d) burned no gas" % g1["peak"])
                if g2["tox"] <= 0:
                    _fail("the gas burned (%d cells) but left no tox gas: no toxic smoke" % (g2["burned"] - g1["burned"]))
                _wait(t, 1500)                                   # the cloud rebuilds
                with _setting(t, "ventGasIgnites", False):
                    g3 = gas()
                    if g3["peak"] < 24:
                        _unmeasured(t, "OFF arm: the cloud did not rebuild (peak %d)" % g3["peak"])
                    g4 = light(600)
                _note(t, "OFF arm: burned before / after", [g3["burned"], g4["burned"]])
                if g4["burned"] != g3["burned"]:
                    _fail("ventGasIgnites OFF but the gas still burned (%d -> %d)" % (g3["burned"], g4["burned"]))
        with _comp(t, "gas_tap_caps_and_banks", toggle="gasTapBanksCondensate"):
            if _live(t):
                _ok(t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,1;%s:%d,%d,1" % (GAS_TAP, x, z, TANK, x + 2, z)),
                    "spawn_batch(tap, tank)")
                rows = _things(t, GAS_TAP, _rs(_rect(t)))
                if not rows:
                    _unmeasured(t, "the spawned %s is not on the map" % GAS_TAP)
                ids["tap"] = rows[0]["id"]
                if not gas().get("capped"):
                    _fail("a gas tap stands on the vent but the vent does not read capped")
                _wait(t, 9000)
                b1, d1, _h = _tap_read(t, ids["tap"])
                _note(t, "tap banked / delivered after 9000 ticks", [b1, d1])
                if b1 + d1 <= 0.05:
                    _fail("a tapped breathing vent banked nothing in 9000 ticks")
                # d1 >= 1 also proves RM_Liquid_VentCondensate resolved (the tank only accepts a real LiquidDef); the def
                # census cannot, since LiquidDef is a FlowWorks type the bridge's get_defs does not address.
                if d1 < 1:
                    _fail("the tap banked %.2f but delivered nothing to the tank touching it" % b1)
                with _setting(t, "gasTapBanksCondensate", False):
                    b2, d2, _h = _tap_read(t, ids["tap"])
                    _wait(t, 3000)
                    b3, d3, _h = _tap_read(t, ids["tap"])
                _note(t, "OFF arm: banked+delivered before / after", [b2 + d2, b3 + d3])
                if b3 + d3 > b2 + d2 + 0.01:
                    _fail("gasTapBanksCondensate OFF but the tap still banked (%.2f -> %.2f)" % (b2 + d2, b3 + d3))
        with _comp(t, "vexxiss_pries_tap", toggle="vexxissPriesTaps"):
            if _live(t):
                _kill_kind_near(t, VEXXISS)
                if "tap" not in ids:
                    _unmeasured(t, "no tap from the previous component")
                _b, _d, h0 = _tap_read(t, ids["tap"])
                pid = _spawn(t, VEXXISS, x + 8, z)
                _full(t, pid)
                drank = False
                for _ in range(16):
                    t.wait_ticks(150)
                    if _jobs(t).get(pid) == DRINK_JOB:
                        drank = True
                        break
                if not drank:
                    _unmeasured(t, "the vexxiss never took %s at the capped vent" % DRINK_JOB)
                _wait(t, 900)
                _b, _d, h1 = _tap_read(t, ids["tap"])
                _kill_pawns_in(t, _rect(t, PAD_SIZE + 8))
                _note(t, "tap HP before / after a drink", [h0, h1])
                if h1 >= h0:
                    _fail("a vexxiss drank at the capped vent and the scaffold took no damage (%d -> %d)" % (h0, h1))
                with _setting(t, "vexxissPriesTaps", False):
                    pid2 = _spawn(t, VEXXISS, x + 8, z)
                    _full(t, pid2)
                    seen = False
                    for _ in range(16):
                        t.wait_ticks(150)
                        if _jobs(t).get(pid2) == DRINK_JOB:
                            seen = True
                            break
                    _wait(t, 900)
                    _b, _d, h2 = _tap_read(t, ids["tap"])
                    _kill_pawns_in(t, _rect(t, PAD_SIZE + 8))
                _note(t, "OFF arm: drank / HP before / after", [seen, h1, h2])
                if not seen:
                    _unmeasured(t, "OFF arm: the vexxiss never drank, so nothing was tested")
                if h2 < h1:
                    _fail("vexxissPriesTaps OFF but the scaffold still took damage (%d -> %d)" % (h1, h2))
        with _comp(t, "ruin_kit_dresses"):
            if _live(t):
                rx, rz = x - 8, z - 8
                before = _count(t, TANK, _rs((rx - 6, rz - 6, 14, 14)))
                _ok(t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,1" % (RIG, rx, rz)), "spawn_batch(rig)")
                t.wait_ticks(5)
                if not _things(t, RIG, _rs((rx - 1, rz - 1, 4, 4))):
                    _unmeasured(t, "the spawned %s is not on the map" % RIG)
                tanks = _count(t, TANK, _rs((rx - 6, rz - 6, 14, 14))) - before
                pipes = _count(t, "AncientPipe", _rs((rx - 6, rz - 6, 14, 14)))
                _note(t, "ruin pieces beside the rig: tanks / pipes", [tanks, pipes])
                if tanks < 1 or pipes < 1:
                    _fail("the corroded filter rig did not dress its site (tanks %d, pipes %d)" % (tanks, pipes))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the Filter-Works converting
# CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD. The works is FlowWorks' CompLiquidConverter: it needs power, a cartridge, a tank
# of its input TOUCHING it and (for water) a tank to take the product; vent condensate (8000 units = 800 L) comes out as ONE
# RM_VentReagent item dropped beside it. Decided by STATE: item stacks, the tanks' and the works' own inspect lines.
# Geometry (works 3x3 at (X,Z); a 2x2 tank's position is its bottom-left cell): battery (X,Z+2) touches the north edge,
# input tank (X+2,Z) the east edge, output tank (X-3,Z) the west edge.

FLOWPROOFS = "RimMandrake.FlowWorks.RM_NorthstarProofs"
COND_BATCH = 8000        # RM_Liquid_VentCondensate refine step: inputLitres 800 x 10 units/litre (Defs/LiquidDefs)
RARE = 250


def _w_tank(t, x, z, liquid, units):
    """ProofTank: set a Store tank's contents (units 0 = empty); UNMEASURED on REFUSED, FAIL when the tank cannot hold a batch."""
    out = _static(t, FLOWPROOFS, "ProofTank", "%d,%d;Store;%s;%d" % (x, z, liquid, units))
    if not _live(t):
        return out
    if out.startswith("REFUSED"):
        m = re.search(r"capacity (\d+)", out)
        if m and units > int(m.group(1)) >= 0 and liquid == COND:
            if int(m.group(1)) < COND_BATCH:
                _fail("the input tank's capacity %s is below one condensate batch (%d units): the works could never run" % (m.group(1), COND_BATCH))
            return _w_tank(t, x, z, liquid, int(m.group(1)))
        _unmeasured(t, "ProofTank refused: %s" % out)
    return out


def _w_status(t, wid):
    """(status line, 'Processed ... in, ... out' line) from the works' inspect."""
    _l, lines = _inspect(t, wid)
    ls = [str(x) for x in lines]
    proc = [x for x in ls if x.startswith("Processed")]
    # HARNESS LESSON (A5, live 2026-10-19c): the inspect string leads with VANILLA's CompPowerTrader line "Power needed: 350 W" (shown
    # whenever the works is on the grid) and the Refuelable line; the converter's own status ("Out of fuel", "No power", "Idle",
    # "Turning ...") comes after. Taking lines[0] read the power draw as the status and failed A5 although the works was fine.
    stat = [x for x in ls if not x.startswith(("Processed", "Pending", "Power needed", "Filter cartridge", "Cartridge"))]
    return (stat[0] if stat else ""), (proc[0] if proc else "")


def _w_hold(t, tid):
    """The tank's own 'Holding: ...' / 'Empty' line."""
    _l, lines = _inspect(t, tid)
    for x in lines:
        if str(x).startswith("Holding") or str(x).startswith("Empty"):
            return str(x)
    return " | ".join(str(x) for x in lines)


@suite.chain("works")
def works_chain(t):
    _prep(t, "works")
    x, z = t.anchor
    ids = {}
    pos = {"in": (x + 2, z), "out": (x - 3, z)}

    def reagent():
        return _stack_total(t, REAGENT, _rs(_rect(t)))

    def poll(pred, limit, step=500):
        """(value, ticks) once pred() is truthy, ticking `step` at a time up to `limit`."""
        waited = 0
        v = pred()
        while not v and waited < limit:
            _wait(t, step)
            waited += step
            v = pred()
        return v, waited

    def body():
        with _comp(t, "works_site_ready", poison=True):
            if _live(t):
                _ok(t.bridge_call("jawa/build_batch", faction="player", wipeExisting=False,
                                  ops="%s:%d,%d;%s:%d,%d;%s:%d,%d;%s:%d,%d" % (
                                      VWORKS, x, z, BATTERY, x, z + 2, TANK, pos["in"][0], pos["in"][1],
                                      TANK, pos["out"][0], pos["out"][1])), "build_batch(works site)")
                t.wait_ticks(5)
                rect = _rs(_rect(t))
                w = _things(t, VWORKS, rect)
                b = _things(t, BATTERY, rect)
                tanks = dict((tk["x"], tk) for tk in _things(t, TANK, rect))
                if not w or not b or pos["in"][0] not in tanks or pos["out"][0] not in tanks:
                    _unmeasured(t, "the works site did not stand: works %d battery %d tanks at x %s" % (len(w), len(b), sorted(tanks)))
                ids.update(works=w[0]["id"], batt=b[0]["id"], tin=tanks[pos["in"][0]]["id"], tout=tanks[pos["out"][0]]["id"])
                _ok(t.bridge_call("jawa/battery_set", thing=ids["batt"], mode="setPct", value=1.0), "battery_set(1.0)")
                _w_tank(t, pos["in"][0], pos["in"][1], COND, 16000)
                _w_tank(t, pos["out"][0], pos["out"][1], FRESHW, 0)
                # the powered works says something other than 'No power'/'Idle' once vanilla's power net has switched it on
                # (~100-170 ticks on the full list, proof_hose._powered); wait for it and record how long
                def powered():
                    st = _w_status(t, ids["works"])[0]
                    return bool(st) and st != "Idle" and "No power" not in st
                got, waited = poll(powered, 1500, step=250)
                _note(t, "works powered: status after ticks", [_w_status(t, ids["works"])[0], waited])
                if not got:
                    _unmeasured(t, "the works never left 'No power'/'Idle' in 1500 ticks (status %r): power never reached it"
                                % (_w_status(t, ids["works"])[0],))
        with _comp(t, "works_refines_condensate"):
            if _live(t):
                tin_txt0 = _w_hold(t, ids["tin"])
                if "ondensate" not in tin_txt0:
                    _unmeasured(t, "the input tank does not read as holding vent condensate: %r" % tin_txt0)
                s0, p0 = _w_status(t, ids["works"])
                # control arm: powered, no cartridge -> nothing may come out (a harness that sees nothing must not pass)
                _wait(t, 3 * RARE)
                if reagent() != 0 or _w_hold(t, ids["tin"]) != tin_txt0 or _w_status(t, ids["works"])[1] != p0 \
                        or "Out of fuel" not in _w_status(t, ids["works"])[0]:
                    _fail("the works ran, or does not say 'Out of fuel', with no cartridge (reagent %d, status %r)"
                          % (reagent(), _w_status(t, ids["works"])[0]))
                r = _ok(t.bridge_call("jawa/thing_refuel", thingId=ids["works"], amount=5), "thing_refuel(works)")
                if not r.get("hasFuel"):
                    _unmeasured(t, "thing_refuel did not leave the works fuelled: %r" % r)
                # budget = 16000 L/day x 10 = 160000 units/day over 240 rare ticks = 666 units per 250 ticks: a batch of
                # 8000 accrues in 12 rare ticks (~3000 ticks); poll to 7000
                made, waited = poll(reagent, 7000)
                s1, p1 = _w_status(t, ids["works"])
                tin_txt1 = _w_hold(t, ids["tin"])
                _note(t, "refine: reagent / ticks to first / status / totals / input tank", [made, waited, s1, p1, tin_txt1])
                if not made:
                    _fail("a powered, fuelled works with a condensate tank touching it made no %s in %d ticks (status %r, totals %r)"
                          % (REAGENT, waited, s1, p1))
                if tin_txt1 == tin_txt0 or p1 == p0:
                    _fail("reagent appeared (%d) but the input tank (%r -> %r) or the works' totals (%r -> %r) did not move"
                          % (made, tin_txt0, tin_txt1, p0, p1))
        with _comp(t, "works_filters_toxic_water"):
            if _live(t):
                _w_tank(t, pos["in"][0], pos["in"][1], TOXICW, 6000)
                _w_tank(t, pos["out"][0], pos["out"][1], FRESHW, 0)
                r0 = reagent()
                out0 = _w_hold(t, ids["tout"])

                def fresh():
                    h = _w_hold(t, ids["tout"]).lower()
                    return "fresh water" in h and not h.startswith("empty")
                got, waited = poll(fresh, 6000)
                tin_h, tout_h = _w_hold(t, ids["tin"]), _w_hold(t, ids["tout"])
                _note(t, "toxic -> fresh: ticks / input / output / status", [waited, tin_h, tout_h, _w_status(t, ids["works"])[0]])
                if not got:
                    _fail("toxic water in the touching tank came out as no fresh water in the product tank after %d ticks (output %r, status %r)"
                          % (waited, tout_h, _w_status(t, ids["works"])[0]))
                if reagent() != r0:
                    _fail("a toxic-water run dropped vent reagent (%d -> %d): the wrong recipe ran" % (r0, reagent()))
        with _comp(t, "works_stops_without_power"):
            if _live(t):
                _ok(t.bridge_call("jawa/battery_set", thing=ids["batt"], mode="setPct", value=0.0), "battery_set(0)")
                _wait(t, 3 * RARE)                              # flush: a batch already due may still land on the first rare tick
                # a powered works would turn this input (4000 units per batch, 666 accrued per rare tick) within 6 rare ticks
                _w_tank(t, pos["in"][0], pos["in"][1], TOXICW, 6000)
                _w_tank(t, pos["out"][0], pos["out"][1], FRESHW, 0)
                before = (_w_hold(t, ids["tout"]), _w_status(t, ids["works"])[1])
                _wait(t, 7 * RARE)
                after = (_w_hold(t, ids["tout"]), _w_status(t, ids["works"])[1])
                status = _w_status(t, ids["works"])[0]
                _note(t, "unpowered: output tank / totals before, after; status", [before, after, status])
                if after != before:
                    _fail("an unpowered works kept converting (%r -> %r, status %r)" % (before, after, status))
                if "No power" not in status:
                    _unmeasured(t, "nothing moved but the works does not say why (status %r): cannot tell no power from no work" % status)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the gas drift
# The law is read from the LIVE assembly through jawa/static_call (pure public statics): the daily heading and the wind ->
# chance law. The MOVEMENT is read too (gas_cloud_moves_along_heading): RM_MapComponent_VentGas.CentroidOf is the one read of
# the vent-gas grid's density (total + density-weighted centroid in a window), with SeedCloud / ClearOf as its fixtures.

KERNEL = "RimMandrake.Cauldron.RM_VentGasKernel"
HEADING_PERIOD = 60000


def _py_heading(ticks, seed):
    """Offline port of RM_VentGasKernel.Heading (uint arithmetic); selftest compares it with the C# source constants."""
    day = (ticks if ticks > 0 else 0) // HEADING_PERIOD
    h = ((day * 2654435761) & 0xFFFFFFFF) ^ (seed & 0xFFFFFFFF)
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    return h % 8


def _heading(t, ticks, seed):
    out = _static(t, KERNEL, "Heading", "%d|%d" % (ticks, seed))
    if not _live(t):
        return 0
    try:
        return int(out.strip())
    except ValueError:
        _unmeasured(t, "Heading(%d,%d) answered %r, not an integer" % (ticks, seed, out))


@suite.chain("drift")
def drift_chain(t):
    with _comp(t, "gas_heading_is_daily_and_map_seeded"):
        if _live(t):
            seed = 17
            days = list(range(0, 24))
            live = [_heading(t, d * HEADING_PERIOD, seed) for d in days]
            ends = [_heading(t, d * HEADING_PERIOD + HEADING_PERIOD - 1, seed) for d in days[:6]]
            other = [_heading(t, d * HEADING_PERIOD, seed + 7919) for d in days]
            _note(t, "headings day 0..23 (seed 17) / other seed", [live, other])
            if any(h < 0 or h > 7 for h in live):
                _fail("a heading outside 0..7: %r" % live)
            if live[:6] != ends:
                _fail("the heading changed inside a day: day starts %r vs day ends %r" % (live[:6], ends))
            if len(set(live)) < 3:
                _fail("the heading never turns (days 0..23 -> %r): the cloud would always drift one way" % sorted(set(live)))
            if live == other:
                _fail("two maps (seed 17 and 7936) share one heading calendar: the heading is not map-seeded")
            want = [_py_heading(d * HEADING_PERIOD, seed) for d in days]
            if live != want:
                _fail("the live Heading differs from the offline port: live %r vs port %r" % (live, want))
    with _comp(t, "gas_drift_chance_follows_wind", toggle="ventGasDrifts"):
        if _live(t):
            got = []
            for w in (-1.0, 0.0, 0.5, 1.0, 2.0, 9.0):
                out = _static(t, KERNEL, "DriftChance", "%s" % w)
                try:
                    got.append((w, float(out.strip())))
                except ValueError:
                    _unmeasured(t, "DriftChance(%s) answered %r" % (w, out))
            _note(t, "DriftChance(wind)", got)
            vals = dict(got)
            if vals[-1.0] != 0.0 or vals[0.0] != 0.0:
                _fail("calm air must not drift: %r" % got)
            if not (0.0 < vals[0.5] < vals[1.0] <= vals[2.0]):
                _fail("a stronger wind must drift at least as often, and a breeze must drift: %r" % got)
            if vals[9.0] > 0.75 + 1e-6 or vals[9.0] < vals[2.0]:
                _fail("the chance must cap at 0.75, never fall: %r" % got)
    _cloud_row(t)


GASCOMP = "RimMandrake.Cauldron.RM_MapComponent_VentGas"
HEAD_DX = (0, 1, 1, 1, 0, -1, -1, -1)        # RM_VentGasKernel.HeadingDx / HeadingDz (selftest checks the C# source)
HEAD_DZ = (1, 1, 0, -1, -1, -1, 0, 1)
CLOUD_SEED_R, CLOUD_SEED_AMT = 4, 255         # 49 cells at full density: ~12k units, thick enough to diffuse and drift
CLOUD_WIN = 20                                # the readout window's half-width, inside the pad's cleared 48x48
CLOUD_TICKS, CLOUD_STEP = 1500, 250
CLOUD_MIN_TOTAL = 1000                        # less than this in the window: no cloud to follow (UNMEASURED)
CLOUD_CALM_TOL = 1.5                          # cells a cloud may wander with the drift off (dissipation is random)
CLOUD_MIN_MOVE = 1.0                          # cells the wind arm must out-travel the calm arm by
CLOUD_MIN_CHANCE = 0.15                       # below this a 1500-tick window cannot show a cell of drift
CLOUD_COS = 0.7071                            # within 45 degrees of the heading


def _cloud(t, x, z):
    """CentroidOf as a dict of floats; unreadable is UNMEASURED, never a number."""
    out = _static(t, GASCOMP, "CentroidOf", "current|%d,%d|%d" % (x, z, CLOUD_WIN))
    if not _live(t):
        return {}
    if out.startswith("REFUSED"):
        _unmeasured(t, "CentroidOf refused: %s" % out)
    try:
        return dict((k, float(v)) for k, v in (kv.split("=", 1) for kv in out.split()))
    except ValueError:
        _unmeasured(t, "CentroidOf answered %r, not k=v numbers" % out)


def _cloud_arm(t, x, z):
    """A fresh cloud at (x, z), followed for CLOUD_TICKS: [first sample, ..., last]."""
    _static(t, GASCOMP, "ClearOf", "current")
    seed = _static(t, GASCOMP, "SeedCloud", "current|%d,%d|%d|%d" % (x, z, CLOUD_SEED_R, CLOUD_SEED_AMT))
    if not _live(t):
        return []
    if seed.startswith("REFUSED"):
        _unmeasured(t, "SeedCloud refused: %s" % seed)
    samples = [_cloud(t, x, z)]
    if samples[0]["total"] < CLOUD_MIN_TOTAL:
        _unmeasured(t, "the seeded cloud holds %d units (seed %r): walls on the pad refused it, no cloud to follow"
                    % (samples[0]["total"], seed))
    for _ in range(CLOUD_TICKS // CLOUD_STEP):
        _wait(t, CLOUD_STEP)
        samples.append(_cloud(t, x, z))
    if samples[-1]["total"] < CLOUD_MIN_TOTAL // 4 or samples[-1]["cx"] < 0:
        _unmeasured(t, "the cloud thinned to %d units by the last read: no centroid to compare" % samples[-1]["total"])
    return samples


def _moved(a, b):
    return b["cx"] - a["cx"], b["cz"] - a["cz"]


def _cloud_row(t):
    """drift.gas_cloud_moves_along_heading: the cloud itself, not the law. Two arms on the same cleared pad, each from a
    fresh seeded cloud with emission off (no vent can feed the window): CALM (ventGasDrifts off -- every shipped weather
    carries wind, windSpeedFactor >= 0.5, so 'calm air' is the drift law's own zero) must stay put; WIND (shipped default)
    must out-travel the calm arm along the map's live heading. Subtracting the calm arm cancels the site's own asymmetry
    (a wall or rock edge biases diffusion the same way in both arms).
    PROVE  CentroidOf every 250 ticks over 1500, per arm.
    EXPECT calm |d| <= 1.5 cells; wind - calm >= 1.0 cell, within 45 degrees of (HeadingDx, HeadingDz)[heading].
    LIES   a window too small (gas leaving it drags the centroid back): 20-cell half-width vs a ~15-cell cloud; a heading
           that turns mid-arm (day boundary): UNMEASURED; wind too light to show a cell: UNMEASURED."""
    _prep(t, "drift", size=40)
    x, z = t.anchor

    def body():
        with _comp(t, "gas_cloud_moves_along_heading", toggle="ventGasDrifts"):
            if not _live(t):
                return
            with _setting(t, "ventGasEnabled", False):
                with _setting(t, "ventGasDrifts", False):
                    calm = _cloud_arm(t, x, z)
                wind = _cloud_arm(t, x, z)
                _static(t, GASCOMP, "ClearOf", "current")
            dc = _moved(calm[0], calm[-1])
            dw = _moved(wind[0], wind[-1])
            heads = sorted(set(int(s["heading"]) for s in wind))
            chance = min(s["chance"] for s in wind)
            _note(t, "cloud calm / wind (total, cx, cz, heading, chance)",
                  [[(int(s["total"]), round(s["cx"], 2), round(s["cz"], 2), int(s["heading"]), s["chance"]) for s in arm]
                   for arm in (calm, wind)])
            if any(s["chance"] != 0.0 for s in calm):
                _fail("ventGasDrifts OFF but the tick's drift chance reads %r" % [s["chance"] for s in calm])
            if math.hypot(*dc) > CLOUD_CALM_TOL:
                _fail("with the drift off the cloud still travelled %.2f cells (%.2f, %.2f): it moves without wind"
                      % (math.hypot(*dc), dc[0], dc[1]))
            if len(heads) != 1:
                _unmeasured(t, "the heading turned during the wind arm (%r): a day boundary fell in the window" % heads)
            if chance < CLOUD_MIN_CHANCE:
                _unmeasured(t, "the wind is too light (drift chance %.3f, wind %.3f): 1500 ticks cannot show a cell of drift"
                            % (chance, wind[0]["wind"]))
            rx, rz = dw[0] - dc[0], dw[1] - dc[1]
            mag = math.hypot(rx, rz)
            h = heads[0]
            hx, hz = HEAD_DX[h], HEAD_DZ[h]
            cos = (rx * hx + rz * hz) / (mag * math.hypot(hx, hz)) if mag > 0 else -1.0
            _note(t, "cloud drift vs heading", {"heading": h, "dir": (hx, hz), "wind_minus_calm": (round(rx, 2), round(rz, 2)),
                                                "cells": round(mag, 2), "cos": round(cos, 3), "chance": chance})
            if mag < CLOUD_MIN_MOVE:
                _fail("under wind (chance %.2f) the cloud out-travelled the calm arm by only %.2f cells: it does not drift"
                      % (chance, mag))
            if cos < CLOUD_COS:
                _fail("the cloud drifted (%.2f, %.2f) but the heading is %d (%d, %d): cos %.2f, it goes the wrong way"
                      % (rx, rz, h, hx, hz, cos))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: the rhossak (RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD)
# Owner by card 2026-10-19: "Make them animals and make them bind." A rhossak binds to the nearest twisting thornwood and
# stays near it (RM_CompRhossakGrove points our RM_CompHomeTether at the tree); its inspect pane says which tree, or
# "Unbound". The donor dryads this replaces walked straight off a tree-less map, so "still near its tree after 5000
# ticks" is the row that would have caught them.

def _rhossak_bind_line(t, pid):
    _, lines = _inspect(t, pid)
    return next((l for l in lines if l.startswith("Bound to") or l.startswith("Unbound")), None)


@suite.chain("rhossak")
def rhossak_chain(t):
    _prep(t, "rhossak")
    x, z = t.anchor
    ids = {}

    def body():
        with _comp(t, "rhossak_binds_to_thornwood", toggle="rhossakBindEnabled"):
            if _live(t):
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (THORN, x, z), growth=1.0)
                if _count(t, THORN, "%d,%d,1,1" % (x, z)) < 1:
                    _unmeasured(t, "no thornwood stood at the pad centre after set_plants")
                ids[RHOSSAK] = _spawn(t, RHOSSAK, x + 7, z - 3)
                ids[GALLED] = _spawn(t, GALLED, x + 7, z + 3)
                t.wait_ticks(600)
                got = dict((k, _rhossak_bind_line(t, pid)) for k, pid in ids.items())
                _note(t, "bind lines", got)
                bad = dict((k, v) for k, v in got.items()
                           if not (v or "").startswith("Bound to") or "thornwood" not in (v or "").lower())
                if bad:
                    _fail("rhossak not bound to the thornwood 600 ticks after spawning beside it: %s" % bad)
        with _comp(t, "rhossak_stays_by_its_tree"):
            if _live(t):
                if len(ids) < 2:
                    _unmeasured(t, "no rhossak from the bind row to follow")
                t.wait_ticks(5000)
                rows = _rows(t)
                far = {}
                for k, pid in ids.items():
                    row = rows.get(pid)
                    if not row or row.get("dead"):
                        _unmeasured(t, "%s is dead or gone (a predator or the site, not the tether): %r" % (k, row))
                    d = max(abs(row["x"] - x), abs(row["z"] - z))
                    if d > RHOSSAK_TETHER + 4:
                        far[k] = d
                _note(t, "cells from the tree after 5000 ticks (tether %d)" % RHOSSAK_TETHER, far)
                if far:
                    _fail("rhossak wandered off its tree: %s cells away" % far)
        with _comp(t, "rhossak_bind_off_unbinds", toggle="rhossakBindEnabled"):
            if _live(t):
                if RHOSSAK not in ids:
                    _unmeasured(t, "no rhossak from the bind row")
                with _setting(t, "rhossakBindEnabled", False):
                    t.wait_ticks(600)
                    line = _rhossak_bind_line(t, ids[RHOSSAK])
                    if line is not None:
                        _fail("rhossakBindEnabled off but the inspect pane still reads %r" % line)
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
