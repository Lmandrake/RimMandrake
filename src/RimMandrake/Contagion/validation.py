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
retile did not land. `site.restore_tile` puts the START biome back. The off-biome chains
(repulsor_clear, spawner) run BEFORE the retile, on a stock biome, on purpose: the
Repulsor's off-Contagion half is a different code path, and the Unfinished spawner jumps the clock.

TWO STARTS, ONE SUITE (item CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK). The suite runs whole on either
  - a stock map (a quicktest, or the `calm` saved site): as above; or
  - the saved Contagion site (test_site_saves.py load contagion, RM_TestSite_contagion_v1), already sick.
Only two components need a stock map: repulsor_clear.site_ready_baseline (the Repulsor's other code path)
and site.retile_to_contagion (its control: the map must NOT read Contagion before the retile). Both call
_off_contagion first, which on a sick start re-tiles the map's own tile to OFF_BIOME. That is faithful:
every Contagion code path decides on the live Map.Biome alone (RM_ContagionSky.ExtFor), and RM_SkyKernel.Tick
resets the sky state to Fresh at its first poll off the biome, so the map is then the same as a stock map
that was never retiled. Every other chain is the on-Contagion arm (`_need_contagion`) or biome-blind.
`site_restore` returns the tile to the first biome the run saw (RM_Contagion on the saved site).

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
    "draftprintsEnabled": True, "draftprintProvokeChance": 0.35, "helixContractRewardFactor": 1.0,
    "zhoolHazeEnabled": True, "zhoolHazeDensity": 1.0, "zhoolConversionEnabled": True,
    "zhoolConversionRate": 1.0, "zhoolConvertsCrops": False,
    "touchedEnabled": True, "touchedExposureFactor": 1.0, "touchedMutationRate": 1.0,
    "sunbeamArrestEnabled": True, "mulchDropsEnabled": True,
}
# a value different from the default, for the write+read-back round trip
ALT = {"biomeRarityFactor": 0.5, "burnFrequency": 2.0, "burnDamageFactor": 0.5, "sunbeamNativeFactor": 3.0,
       "zhoolHazeDensity": 2.0, "zhoolConversionRate": 2.0, "touchedExposureFactor": 2.0,
       "touchedMutationRate": 2.0, "draftprintProvokeChance": 0.7, "helixContractRewardFactor": 2.0}
suite.toggles = sorted(DEFAULTS)

PADS = {"repulsor": (-45, -45), "spawner": (45, -45), "burn": (0, -45), "uv": (-45, 0),
        "coal": (45, 0), "genome": (0, 45), "zhool": (-45, 45), "touched": (45, 45)}
PAD_SIZE = 30
SOIL = "Soil"
REPULSOR, COALESCENCE, SAMPLE = "RM_CloudRepulsor", "RM_Coalescence", "RM_GenomeSample"
TOUCHED, MULCH = "RM_ContagionTouched", "RM_ContagionMulch"   # owner N4/Q3/Q4, 2026-10-15
HELIX_FACTION, HELIX_TRADER = "RUT_Jawa_AscendantHelix", "RM_Caravan_HelixCurators"   # owner Q5, 2026-10-15
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
ZHOOL, GRASS, LASHGRASS = "RM_OcularJelly", "Plant_Grass", "RM_Lashgrass"   # CompZhoolHaze: grass -> groundCoverResult
ZHOOL_FILL = 7                               # grass on every cell within +-7 of the zhool (> its 3.9 haze radius)
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


def _harness(msg):
    """A failure of the bench or the site (a fixture that did not stand, a bridge call that failed, a clock that did not move),
    never a finding against the mod: UNMEASURED, and the suite files no finding (review 2026-10-20)."""
    raise ExpectationFailed("UNMEASURED: " + msg)


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


def _ok(r, what, mod=False):
    """A failed bridge reply is the bench's (UNMEASURED). `mod=True` only where the reply IS the claim under test (a settings
    field the mod no longer declares)."""
    if not isinstance(r, dict) or r.get("success") is False:
        (_fail if mod else _harness)("%s failed: %r" % (what, r))
    return r


def _pad(t, name):
    dx, dz = PADS[name]
    ax, az = t._base if hasattr(t, "_base") else t.anchor
    # The driver's anchor was read off the quicktest map and can be far from this map's centre (MEASURED
    # 2026-10-03: base ~(53,50) on a 250x250 map put the burn/uv pads half off-map: "Cell is outside the
    # map"). Re-base on the live map centre; the pads are +-45 and need >= ~100 cells.
    if _live(t):
        try:
            mi = t.bridge_call("jawa/map_info")
            if isinstance(mi, dict) and mi.get("sizeX") and mi.get("sizeZ"):
                ax, az = int(mi["sizeX"]) // 2, int(mi["sizeZ"]) // 2
        except Exception:
            pass
    t._base = (ax, az)
    t.anchor = (ax + dx, az + dz)


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


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _rect(t, size=PAD_SIZE, dx=0, dz=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half + dz, size, size


# SITE, LIVE 2026-10-16 (modcheck round 4): the quicktest tile was Mountainous, so clear_area carved every pad out of
# solid rock (1286 Slate on the repulsor pad) under the mountain's overhead RoofRockThick. Destroying the rock despawns
# the roof holders, the unsupported cells are marked to collapse, and the next tick drops a thick roof on the pad:
# RoofCollapserImmediate deals 99999 Crush to every thing and pawn in the cell (decompiled Verse). That one site defect
# was four FAILs -- the repulsor gone before its inspect read (off_when_setting_off), the Unfinished host crushed before
# it could bud (spawner_buds_unfinished), the whole Burn fixture crushed during order_pawn's 300-tick wait
# (burn_harmless_at_zero_damage: native alive=False), the Coalescence crushed (coalescence_off_absorbs_nothing) -- and
# the touched chain's 'died: Crush' governor stop. A collapse only drops a cell that is STILL roofed when it resolves,
# so the pad is unroofed (before the clear) and nothing is left to drop. The margin covers every cell within the 6.9-cell roof
# support range of the cleared rock. Outdoors is also what the Burn rows assume: under a mountain roof the "open"
# visitor is sheltered. A row that wants a roof (the burn chain's patch) sets its own after _prep.
ROOF_MARGIN = 7


def _prep(t, name, size=PAD_SIZE):
    """Clear the pad, lay plain soil so everything stands on walkable ground, and take the roof off (see ROOF_MARGIN)."""
    _pad(t, name)
    # Unroofed BEFORE the clear: the collapse marked by the clear then finds no roof to drop, whatever ticks follow.
    r = t.bridge_call("jawa/set_roof_batch", ops="None:%s" % _rs(_rect(t, size + 8 + 2 * ROOF_MARGIN)))
    if _live(t):
        if not isinstance(r, dict) or r.get("success") is False or "cellsChanged" not in r \
                or r.get("cellsFailedVerify"):
            _unmeasured(t, "SITE: could not unroof the pad (a collapse would crush the fixture): %r" % (r,))
        _note(t, "pad %s unroofed" % name, {"cellsChanged": r.get("cellsChanged"), "perDef": r.get("perDef")})
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
        _harness("list_things(%s) unreadable (no countMatched / scanned 0): %r" % (defName, r))
    if r.get("isCompleteList") is False:
        _harness("list_things(%s) truncated: %r" % (defName, r.get("countMatched")))
    return list(r.get("things") or [])


def _spawn(t, kind, x, z, faction="none"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _harness("spawn_pawn(%s, %s) returned no pawn: %r" % (kind, faction, r))
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


def _burned_off(row):
    """{'Burn'} when a part on this row was destroyed by a burn: a part burned away outright is a MissingBodyPart whose
    lastInjury is Burn and leaves no Burn hediff (LIVE modcheck7 2026-10-16: the UV-shy native read only
    'MissingBodyPart'). lastInjury is read off list_pawns (jawa companion 2026-10-16); a row without it gives set()."""
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict) and h.get("def") == "MissingBodyPart" and h.get("lastInjury") == "Burn":
            return {"Burn"}
    return set()


def _sev_sum(row, defname):
    """Total severity of every hediff of `defname` on a list_pawns row (an injury def lands as one hediff per hit)."""
    tot = 0.0
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict) and (h.get("def") or h.get("defName") or h.get("hediff")) == defname:
            try:
                tot += float(h.get("severity") or 0)
            except (TypeError, ValueError):
                pass
    return tot


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


def _sev(row, hediff):
    """Summed severity of one hediff def on a row (0.0 when absent)."""
    tot = 0.0
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict) and (h.get("def") or h.get("defName")) == hediff:
            tot += float(h.get("severity") or 0)
    return tot


def _alive(row):
    return row is not None and not row.get("dead")


def _inspect(t, thing_id):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    if not _live(t):
        return None, ""
    rows = (_ok(r, "inspect_string").get("things") or [])
    if not rows:
        # a fixture that is gone (crushed, collapsed, wandered off) leaves nothing to read: the bench's, never a finding
        _harness("inspect_string(%s): the thing is no longer on the map (matched %r of %r examined)"
                 % (thing_id, r.get("matched"), r.get("examined")))
    if rows[0].get("error"):
        _harness("inspect_string(%s) unreadable: %r" % (thing_id, rows[:1]))
    return rows[0].get("label"), "\n".join(str(x) for x in (rows[0].get("inspect") or []))


def _as_bool(v):
    return str(v).strip().lower() == "true"


def _same(got, want):
    if isinstance(want, bool):
        # only a real "true"/"false" read-back counts: a missing value (None, "") is not False
        if str(got).strip().lower() not in ("true", "false"):
            return False
        return _as_bool(got) == want
    try:
        return abs(float(str(got).replace(",", ".")) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def _get_setting(t, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
    if not _live(t):
        return None
    _ok(r, "mod_settings_field(get %s)" % field, mod=True)
    return r.get("value")


def _set(t, field, value):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                      value=str(value))
    if not _live(t):
        return
    _ok(r, "mod_settings_field(set %s=%r)" % (field, value), mod=True)
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


class _patient(object):
    """Raise the bridge client's per-reply socket timeout (the runner's 30 s) for a slow job order or tick
    wait, then restore it. MEASURED live 2026-10-03: ordered_job took 17 s with waitTicks=60 and the NET /
    STOCK / FEED / CULL waits then outran 30 s. A mock session without a real socket is left alone."""
    def __init__(self, t, secs=240.0):
        self.rb = getattr(getattr(t, "session", None), "_rb", None)
        self.secs, self.old = secs, None

    def __enter__(self):
        if self.rb is not None and hasattr(self.rb, "timeout"):
            self.old = self.rb.timeout
            self.rb.timeout = self.secs
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.secs)
        return self

    def __exit__(self, *a):
        if self.old is not None:
            self.rb.timeout = self.old
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.old)
        return False


def _wait(t, n):
    """Advance `n` real ticks. Short waits use t.wait_ticks (exact); long waits run Ultrafast and
    poll the real clock, then pause; raises on a stall."""
    # LIVE 2026-10-03: under the situational watch the Ultrafast poll below moves the clock outside the budgeted gate (ClockStall /
    # BudgetExceeded), so a watched run uses the chunked, budgeted t.wait_ticks for every length.
    _support_upkeep(t)
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
                _unmeasured(t, "clock unreadable during a %d-tick wait" % n)
            if now >= target - 400:
                break
            if now > last:
                last, stall = now, time.time()
            elif time.time() - stall > 60:
                # The instrument (the clock) stopped, not the mod: UNMEASURED, never a FAIL (modcheck6 2026-10-16
                # recorded a haze_turns_grass_in_place FAIL off this line).
                _unmeasured(t, "clock stalled at %d during a %d-tick wait (a modal dialog pausing the game?)"
                            % (now, n))
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    now = s._ticks()
    if now is None:
        _unmeasured(t, "clock unreadable after a %d-tick wait" % n)
    if now < target:
        t.wait_ticks(target - now)
        now = s._ticks()
    t._record("_wait(%d) at Ultrafast -> %d real ticks" % (n, now - start), now - start)


def _jump(t, delta):
    """Move the clock FORWARD by `delta` ticks without simulating (jawa/time_set_ticks)."""
    now = t.session._ticks()
    if now is None:
        _unmeasured(t, "clock unreadable before a time jump")
    # Through the SESSION, not t.bridge_call: bridge_call charges the clock move to the watch as an
    # unplanned verb and aborts the chain as clock_runaway (cap 1500; MEASURED 2026-10-03, 90000 and
    # 285000-tick jumps, 9 components UNMEASURED). The jump is the declared design (nothing is simulated),
    # so re-base the clock gate as an EPOCH CHANGE: zero ticks charged, no budget spent.
    # timeException=True: declared forward jump instead of simulating days (ledger records the discontinuity) (safe-advance gate)
    r = t.session.call("jawa/time_set_ticks", ticks=int(now + delta), timeException=True)
    try:
        t._record("time_set_ticks +%d (declared jump)" % delta, r)
    except Exception:
        pass
    _ok(r, "time_set_ticks")
    w = getattr(t, "watch", None)
    if w is not None and getattr(w, "gate", None) is not None:
        after = t.session._ticks()
        if after is not None:
            w.gate.observe(after, epoch_change=True, reason="time_set_ticks declared jump")
    # read the clock back ourselves: a reply without ticksGameAfter must not make a no-op jump look taken
    after = t.session._ticks()
    # unwound by _unjump: count only what the clock really moved, so a jump that did not take is never rewound below where
    # it started (review 2026-10-20)
    if delta > 0 and after is not None and now is not None and after > now:
        _STATE["jumped"] = _STATE.get("jumped", 0) + int(after - now)
    if after is None or after < now + delta - 5:
        _harness("time_set_ticks did not take: clock %r after asking for %d (%r)" % (after, now + delta, r))


def _unjump(t):
    """Put the clock back by whatever this chain jumped (LIVE 2026-10-16: spawner + burn_natural jumped ~730000
    ticks and the later chains (zhool, coalescence) ran at tick 745k with the colony dead). A refused or failed
    rewind is noted, never a verdict. Nothing the later chains read is tick-absolute."""
    back = _STATE.pop("jumped", 0)
    if not back or t.session is None:
        return
    try:
        now = t.session._ticks()
        if now is None:
            raise RuntimeError("clock unreadable")
        t.session.call("jawa/time_set_ticks", ticks=max(int(now) - back, 0), timeException=True)
        w = getattr(t, "watch", None)
        after = t.session._ticks()
        if w is not None and getattr(w, "gate", None) is not None and after is not None:
            w.gate.observe(after, epoch_change=True, reason="time_set_ticks rewind of a declared jump")
        _note(t, "clock rewound after a declared jump", {"back": back, "from": now, "to": after})
    except Exception as ex:                                     # noqa: BLE001 - upkeep, never a verdict
        _note(t, "clock rewind failed", "%s: %s" % (type(ex).__name__, ex))


def _map_biome(t):
    r = t.bridge_call("jawa/map_info")
    if not _live(t):
        return None, None
    _ok(r, "map_info")
    return r.get("mapBiome"), r


# Any vanilla Core biome with no RM_ContagionSkyExtension; Core is always loaded, so it always resolves. Only the
# biome-extension test reads it (the tile's temperature, terrain and mapgen are untouched by a retile).
OFF_BIOME = "AridShrubland"
SKY_POLL = 250                                  # RM_SkyKernel.Interval: the sky resets at its first poll off-biome


def _off_contagion(t):
    """The stock-map precondition of the off-Contagion arm (module doc, TWO STARTS). Records the first biome the run
    saw as start_biome (and the tile); on a map already RM_Contagion re-tiles it to OFF_BIOME and waits one sky poll.
    -> the map's biome now. Callers treat a biome still RM_Contagion as UNMEASURED (the arm has no stock map)."""
    b, info = _map_biome(t)
    if not _live(t):
        return None
    _STATE.setdefault("start_biome", b)
    _STATE.setdefault("tile", info.get("tile"))
    if b != BIOME:
        return b
    tile = info.get("tile")
    if tile is None or info.get("tileValid") is False:
        _unmeasured(t, "SITE: the map is %s and map_info reports no usable tile to take it off: %r" % (BIOME, info))
    _ok(t.bridge_call("jawa/world_tile_set", tiles=str(tile), biome=OFF_BIOME, readBack=1),
        "world_tile_set(off-Contagion)")
    _ok(t.bridge_call("jawa/world_commit", redraw=False, recalcPaths=False), "world_commit")
    b2, _ = _map_biome(t)
    if b2 == BIOME:
        _unmeasured(t, "SITE: re-tiling the saved Contagion site to %s did not take (map still reads %s)"
                       % (OFF_BIOME, BIOME))
    _wait(t, SKY_POLL + 50)
    _note(t, "sick start taken off the Contagion", {"tile": tile, "from": b, "to": b2})
    return b2


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
        _harness("fixture: wanted 1 %s at (%d,%d), found %d" % (REPULSOR, x, z, len(rows)))
    return rows[0]["id"] if rows else None


def _end_conditions(t):
    for name in (BURN_COND, CLEAR_COND):
        if t.session is not None:
            try:
                t.session.call("jawa/game_condition", action="end", condition=name)
            except Exception:
                pass          # 'not active' is a Fail from the tool; nothing to end


def _baseline(t):
    """Everything that could spoil a fixture: storyteller incidents, auto-home, queued incidents; then the
    run's quiet-site profile and the colony's own colonists kept calm and fed (_quiet_site)."""
    t.bridge_call("jawa/site_state", storyteller="off", autoHome="off", clearIncidentQueue=True)
    _quiet_site(t)
    _clear_wildlife(t)


# SITE, LIVE 2026-10-16 (round 4): the map's own mapgen wildlife (shambles, snoruuk, brogg, shiro-traps: the quiet-site
# profile blocks NEW arrivals but leaves mapgen animals) fought and sickened far from every pad, and a shambles downed at
# (244,175) stopped the zhool chain's safe_advance ('downed: the shambles'); the zhool sat at (80,170). No Contagion row
# reads a wild animal it did not spawn, so the map's factionless animals are removed (no death, no corpse) before each
# chain spawns its fixtures. Every fixture animal is spawned AFTER this, and a previous chain's are gone by _stable.
def _clear_wildlife(t):
    if not _live(t):
        return
    try:
        import helpers as H              # noqa: E402
        res = H.kill_wildlife(t.session)
        out = {"removed": res.acted, "verified": res.verified, "residue": res.residue[:8]}
    except Exception as ex:                                     # noqa: BLE001 - site upkeep, never a verdict
        out = {"error": "%s: %s" % (type(ex).__name__, ex)}
    if out.get("removed") or out.get("residue") or out.get("error"):
        _note(t, "mapgen wildlife removed", out)


# SITE, LIVE 2026-10-16 (modcheck run Contagion --policy record, no --situational): with no Watch nobody turned off
# random mental states or fed the quicktest colony, so its own colonists stopped safe_advance three times -- a
# Berserk colonist (colonist_hostile, touched chain), then 'hurt ... Bruise from Human' on another colonist
# (zhool + coalescence chains: the berserker / social fights; Pawn_InteractionsTracker.CheckSocialFightStart is
# gated on DebugSettings.enableRandomMentalStates), and a starving colonist. None of it is the Contagion. The
# fix is the SHARED isolated profile (modcheck/quiet_site.py: storyteller off, random mental states and diseases
# off, wild spawner blocked, threat structures and hostiles cleared) applied once per run when no Watch owns the
# map, plus upkeep before every advance: a colonist's mental state ended and a LOW Food need topped up (only
# below 0.25, bland_world.feed_colonists). Nothing here touches a hediff, the Contagion's things or its settings,
# and every Contagion row reads hediffs/things/inspect lines, never a colonist's mood, food or mental state.
def _quiet_site(t):
    if not _live(t) or getattr(t, "watch", None) is not None:
        return          # a situational Watch already prepared (and restores) a bland map for this chain
    if "quiet" not in _STATE:
        try:
            import quiet_site as QS   # noqa: E402 - modcheck dir is on sys.path wherever suite is importable
            rc = QS.site_profile_receipt(t.session, row="Contagion", suite="isolated",
                                         keep_defs=(COALESCENCE, REPULSOR))
        except Exception as ex:                                 # noqa: BLE001 - recorded, never silent
            rc = {"error": "%s: %s" % (type(ex).__name__, ex)}
        if not rc.get("error"):
            _STATE["quiet"] = rc          # a profile that errored is retried at the next chain, never cached
        rb = dict((c.get("name"), c.get("readBack")) for c in rc.get("controls") or [])
        _note(t, "quiet-site profile (once per run)",
              {"storyteller/mental/disease": rb.get("storyteller_off"), "wildSpawner": rb.get("wild_spawner_off"),
               "problems": rc.get("problems"), "error": rc.get("error")})
    _support_upkeep(t)


def _support_upkeep(t):
    """End any colonist's mental state and top up a LOW Food need. -> what it did (also noted when it acted)."""
    if not _live(t) or getattr(t, "watch", None) is not None:
        return None
    try:
        import helpers as H              # noqa: E402
        import bland_world as BW         # noqa: E402
        ids = [r["id"] for r in H.read_pawns(t.session, health=False) if H.is_colonist(r) and not r.get("dead")]
        calm = H.calm_colonists(t.session, ids)
        fed = BW.feed_colonists(t.session)
    except Exception as ex:                                     # noqa: BLE001 - upkeep, never a verdict
        _note(t, "support upkeep failed", "%s: %s" % (type(ex).__name__, ex))
        return None
    out = {"calmed": calm.acted, "calmResidue": calm.residue, "fed": fed}
    if calm.acted or calm.residue or fed:
        _note(t, "support upkeep", out)
    return out


def _stable(t, fn):
    """Run a chain body, then ALWAYS end the conditions it made, restore every setting it may have
    touched, and clear its pad."""
    try:
        fn()
    finally:
        if t.session is not None:
            _end_conditions(t)
            _unjump(t)
            _support_upkeep(t)
            for f in DEFAULTS:
                _restore(t, f)
            try:
                _remove_pawns_in(t.session.call, _rs(_rect(t, PAD_SIZE + 8)))
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
                _harness("parsed only %d shipped defs / %d wildAnimals from %s (parser broken?)"
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
                "baseWeatherCommonalities,wildPlants,animalDensity,modExtensions"),
                deep=True, limit=5)
            _ok(r, "get_defs(biome)")
            row = ((r.get("defs") or [{}])[0].get("fields")) or {}
            table = row.get("baseWeatherCommonalities")
            # get_defs serialises a record list as bare type names unless deep=true (measured live
            # 2026-10-03: ['WeatherCommonalityRecord', ...]); a non-dict row is unreadable, never a crash.
            if not isinstance(table, list) or not table or not all(isinstance(x, dict) for x in table):
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
            # get_defs flattens a modExtension to its FIELDS, class name absent (MEASURED live 2026-10-03:
            # the dump printed only values); the source (Defs/BiomeDefs, Class="RimMandrake.Contagion.
            # RM_ContagionSkyExtension") carries these three fields, so recognise it by them too.
            if "RM_ContagionSkyExtension" not in blob and not all(
                    k in blob for k in ("meanDaysBetweenBurns", "burnDurationTicks", "tellLeadTicks")):
                _fail("the biome does not carry RM_ContagionSkyExtension (the gate for the Burn, "
                      "the Bloom clock and the Coalescence): %s" % blob[:300])
            if "RM_Rattlegrope" not in json.dumps(row.get("wildPlants")):
                _fail("wildPlants lacks RM_Rattlegrope (the Burn's plant tell)")
            _note(t, "biome roster", {"animals": len(WILD_ANIMALS), "plants": len(WILD_PLANTS)})

    with _comp(t, "biome_roster_animals"):
        if _live(t):
            # BiomeDef.wildAnimals is a NON-PUBLIC list: get_defs cannot serialise it even with deep=true
            # (returns "(non-public field ... not serialised)"). Read it only if a future tool can; never
            # substring-match the placeholder string as 'absent'.
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="wildAnimals", deep=True)
            _ok(r, "get_defs(biome wildAnimals)")
            if r.get("foundCount") != 1 or r.get("notFound"):
                _fail("get_defs(%s): foundCount=%r notFound=%r" % (BIOME, r.get("foundCount"), r.get("notFound")))
            wa = (((r.get("defs") or [{}])[0].get("fields")) or {}).get("wildAnimals")
            if not WILD_ANIMALS:
                _fail("the XML roster parsed to 0 wildAnimals: nothing to compare (parser broken?)")
            if isinstance(wa, (list, dict)):
                blob = json.dumps(wa)
                missing = [a for a in WILD_ANIMALS if '"%s"' % a not in blob]   # exact quoted name, never a prefix
                if missing:
                    _fail("wildAnimals lacks %d rostered kind(s): %s" % (len(missing), missing[:8]))
            else:
                # MEASURED live 2026-10-16 (round 2): BiomeDef.wildAnimals is a NON-PUBLIC list, get_defs answers a
                # placeholder string and no supported tool serialises it. What CAN be measured live is that every
                # rostered kind resolves as a PawnKindDef (a roster entry naming a dead def is discarded silently);
                # the roster-vs-live-BiomeDef comparison itself is UNMEASURED BY DESIGN until a tool can read it.
                kr = t.bridge_call("jawa/get_defs", defs=";".join("PawnKindDef/%s" % a for a in WILD_ANIMALS),
                                   fields="defName", limit=500)
                _ok(kr, "get_defs(rostered PawnKindDefs)")
                if kr.get("notFound"):
                    _fail("%d rostered wildAnimals kind(s) do not resolve live as PawnKindDefs: %s"
                          % (len(kr["notFound"]), kr["notFound"][:8]))
                _note(t, "roster kinds resolving live as PawnKindDef", [kr.get("foundCount"), len(WILD_ANIMALS)])
                _unmeasured(t, "UNMEASURED BY DESIGN: BiomeDef.wildAnimals is non-public and not serialisable by "
                               "get_defs (got %r); %d XML-rostered kinds all resolve live as PawnKindDefs, but "
                               "the live BiomeDef roster itself cannot be compared" % (wa, len(WILD_ANIMALS)))

    # Owner Q5 (2026-10-15, by card: "Quests plus a visiting Helix trader"): the Utinni layer hangs RM_Caravan_HelixCurators
    # on the Ascendant Helix (UtinniPatches/Patches/HelixCurators_Contagion.xml). On a list without the campaign layer
    # the faction is absent: UNMEASURED, never a pass.
    with _comp(t, "helix_trader_wired"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="FactionDef/" + HELIX_FACTION, fields="caravanTraderKinds", deep=True)
            _ok(r, "get_defs(Helix faction)")
            if r.get("foundCount") != 1:
                _unmeasured(t, "%s is not loaded (no campaign layer on this list): %r" % (HELIX_FACTION, r.get("notFound")))
            kinds = (((r.get("defs") or [{}])[0].get("fields")) or {}).get("caravanTraderKinds")
            if not isinstance(kinds, list):
                _unmeasured(t, "caravanTraderKinds unreadable: %r" % (kinds,))
            if HELIX_TRADER not in json.dumps(kinds):
                _fail("the Helix caravans do not include %s: %s" % (HELIX_TRADER, json.dumps(kinds)[:300]))

    # Owner Q6 (2026-10-15, "Build the visible sink and shake"): the drawn tells hang on two def fields. The motion itself is
    # arithmetic (SelfTest family "tells") and a LOOK for the owner's visual bar; this row proves only the wiring loaded.
    with _comp(t, "visible_tells_wired"):
        if _live(t):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Rattlegrope;ThingDef/RM_Gawpsack",
                              fields="thingClass,drawerType,race", deep=True, limit=5)
            _ok(r, "get_defs(rattlegrope, gawpsack)")
            rows = dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or []))
            rg, gs = rows.get("RM_Rattlegrope"), rows.get("RM_Gawpsack")
            if rg is None or gs is None:
                _unmeasured(t, "rattlegrope/gawpsack rows unreadable: %r" % (r.get("notFound"),))
            if "RM_Plant_Rattlegrope" not in json.dumps(rg.get("thingClass")):
                _fail("RM_Rattlegrope thingClass is %r, not RM_Plant_Rattlegrope (no drawn shake)" % rg.get("thingClass"))
            if "RealTime" not in json.dumps(rg.get("drawerType")):
                _fail("RM_Rattlegrope drawerType %r has no RealTime: the shake is never drawn" % rg.get("drawerType"))
            race = json.dumps(gs.get("race"))
            if "renderTree" not in race:
                _unmeasured(t, "the gawpsack's race.renderTree is not serialised: %s" % race[:200])
            if "RM_GawpsackSink" not in race:
                _fail("RM_Gawpsack does not use the RM_GawpsackSink render tree (no drawn sink)")

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
                b = _off_contagion(t)        # a sick start (the saved Contagion site) is taken off it first
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
                # "the condition lapsed" is vacuous unless it was holding when the power went: holds_sky_clear may have read
                # UNMEASURED (it does not poison the chain), leaving no condition at all to lapse
                if not _has_cond(t, CLEAR_COND):
                    _unmeasured(t, "no %s condition was holding before the switch-off: nothing could lapse" % CLEAR_COND)
                r = t.bridge_call("jawa/power_net", thing=_STATE["rep_id"], forcePowerOn=False)
                _ok(r, "power_net(off)")
                if r.get("powerOnAfter"):
                    _unmeasured(t, "could not switch the device off: %r" % r)
                _wait(t, 1200)               # holdTicks 750 + the 250 poll
                if _has_cond(t, CLEAR_COND):
                    _fail("the clear-sky condition outlived the device's power by > 1200 ticks "
                          "(it must lapse within holdTicks=750)")
                # the lapse counts only if the device is still there, unpowered (a destroyed one also lapses)
                _, lines = _inspect(t, _STATE["rep_id"])
                if "Unpowered" not in lines:
                    _unmeasured(t, "the repulsor does not read Unpowered after the switch-off: %r" % lines)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: spawner

@suite.chain("spawner")
def spawner(t):
    def body():
        _STATE.pop("dissolved", None)
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
                    # LIVE 2026-10-16: the host was crushed by a roof collapse in the first ticks and this arm PASSED
                    # on an empty rect. "Nothing budded" means something only while the host is there to bud.
                    _need_host(t)
                    n = len(_things_pawns(t, UNFINISHED, _STATE["host_rect"]))
                    if n:
                        _fail("%d Unfinished budded with unfinishedSpawnerEnabled off" % n)

        # poison: with no budded Unfinished (host gone: UNMEASURED) the three rows below have nothing to read
        with _comp(t, "spawner_buds_unfinished", poison=True, toggle="unfinishedSpawnerEnabled"):
            if _live(t):
                _wait(t, 250)                 # toggle is back on; the overdue timer fires at once
                _need_host(t)
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
                if not _alive(_rows(t).get(kid)):
                    _unmeasured(t, "the budded Unfinished is gone before the push: 'dissolved' could not be seen")
                r = t.bridge_call("jawa/pawn_severity_adjust", pawn=kid,
                                  hediff="RM_UnfinishedUnraveling", offset=1.0)
                _ok(r, "pawn_severity_adjust")
                _wait(t, 120)
                row = _rows(t).get(kid)                # whole map: a kid that wandered off is not 'dissolved'
                if _alive(row):
                    _fail("the Unfinished survived being pushed to lethal severity: %r" % (r,))
                corpses = _things(t, "Corpse_" + UNFINISHED)
                if corpses:
                    _fail("a corpse persists (%d): death must dissolve it" % len(corpses))
                _STATE["dissolved"] = True       # the death the mulch row reads really happened (and was ours)

        # Owner Q4 (2026-10-15, plain fertilizer): a dead Unfinished leaves Contagion mulch where it dissolved
        # (DeathActionWorker_RM_VanishToMulch). Reads the same death the component above caused.
        with _comp(t, "unfinished_leaves_mulch", toggle="mulchDropsEnabled"):
            if _live(t):
                if not _STATE.get("dissolved"):
                    _unmeasured(t, "no Unfinished was seen to die here (the dissolve row did not complete): no mulch could be owed")
                heaps = _things(t, MULCH, _STATE["host_rect"])
                if not heaps:
                    _fail("no %s near the dissolved Unfinished" % MULCH)
                _note(t, "mulch heaps", [h.get("stackCount") for h in heaps])
    _stable(t, body)


def _need_host(t):
    """The budding host must be alive INSIDE host_rect (the rect the buds are counted in), or the spawner arms measure
    nothing (UNMEASURED, never PASS/FAIL)."""
    if not _alive(_rows(t, _STATE["host_rect"]).get(_STATE.get("host"))):
        _unmeasured(t, "SITE: the %s host %s is not alive inside %s; nothing could bud there"
                    % (HOST, _STATE.get("host"), _STATE["host_rect"]))


def _things_pawns(t, kind, rect):
    """Spawned, living pawns of `kind` in rect (list_pawns rows carry `kind`)."""
    rows = _rows(t, rect)
    return [p for p in rows.values() if p.get("kind") == kind and not p.get("dead")]


# --------------------------------------------------------------------------- chain: site

@suite.chain("site")
def site(t):
    with _comp(t, "retile_to_contagion", poison=True):
        if _live(t):
            _off_contagion(t)                # the control: a sick start reads OFF_BIOME before the retile
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
                _harness("SITE: after world_tile_set(%s) the map's own biome reads %r" % (BIOME, b2))
            _note(t, "retiled", {"tile": tile, "from": b, "to": b2})


# --------------------------------------------------------------------------- chain: burn_forced

def _under_patch(t, px, pz):
    """Inside the burn chain's 8x8 roof patch (x+6, z-4, 8, 8 off the pad anchor)."""
    x, z = t.anchor
    return px is not None and pz is not None and x + 6 <= px < x + 14 and z - 4 <= pz < z + 4


def _on_open_pad(t, px, pz):
    """On the unroofed pad (PAD_SIZE around the anchor) and not under the burn chain's roof patch."""
    x, z = t.anchor
    half = PAD_SIZE // 2
    return (px is not None and pz is not None and x - half <= px < x + half and z - half <= pz < z + half
            and not _under_patch(t, px, pz))


def _job_sample(row):
    """(job def, targetA x, z) from a pawn_census row: what the pawn is doing and where it was sent."""
    j = (row or {}).get("job") or {}
    ta = j.get("targetA") or {}
    return (j.get("def"), ta.get("x"), ta.get("z"))


def _goto_to_patch(t, row):
    """True only for the Burn's dive order: a plain Goto job (RM_GameCondition_ContagionBurn.TryDive; a wander is
    GotoWander, never Goto) whose target cell is under the roof patch."""
    d, tx, tz = _job_sample(row)
    return d == "Goto" and _under_patch(t, tx, tz)


def _open_pawns(t, x, z):
    """The Burn fixture: an open visitor, a roofed visitor, a UV-shy native, an armored native, and a
    roof patch east of the native to dive for. Drafted colonists hold their ground."""
    r = t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,8,8" % (x + 6, z - 4))
    if _live(t) and (not isinstance(r, dict) or r.get("success") is False or r.get("cellsFailedVerify")
                     or (r.get("cellsChanged") or 0) < 64):
        _unmeasured(t, "SITE: the 8x8 roof patch did not land: %r" % (r,))
    out = {}
    out["open"] = t.spawn_pawn("Colonist", hostile=False)
    out["roofed"] = t.spawn_pawn("Colonist", hostile=False)
    out["native"] = _spawn(t, UV_NATIVE, x, z + 4)
    out["armored"] = _spawn(t, ARMORED, x, z - 6)
    return out


@suite.chain("burn_forced")
def burn_forced(t):
    def body():
        _STATE.pop("rows_after", None)
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
                        _harness("fixture: no %s pawn" % k)
                # the roofed colonist stands under the patch; both colonists hold their ground
                rx, rz = x + 9, z
                t.bridge_call("jawa/order_pawn", pawnId=_STATE["burn"]["roofed"], x=rx, z=rz,
                              waitTicks=300)
                for k in ("open", "roofed"):
                    t.bridge_call("jawa/set_draft", pawnId=_STATE["burn"][k], drafted=True)
                _STATE["rep_id"] = _spawn_repulsor(t, x - 8, z + 8)     # left UNPOWERED: the no-Burn control reads first

        with _comp(t, "native_no_dive_without_burn"):
            # CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME: the control for native_dives_for_roof. No Burn is active (the repulsor is
            # unpowered), so nothing may ORDER the native to the patch. The dive is vanilla Goto to a roofed cell
            # (RM_GameCondition_ContagionBurn.TryDive; a wander is GotoWander), so a native merely standing on the patch
            # is allowed and only noted: position alone cannot tell a dive from a wander.
            if _live(t):
                if _has_cond(t, BURN_COND):
                    _unmeasured(t, "a Burn is active: the no-Burn control cannot be taken")
                nid = _STATE["burn"]["native"]
                seen, ordered, onpatch = 0, [], []
                for _ in range(32):                  # 32 x 25 = the same 800 ticks the dive arm samples
                    _wait(t, 25)
                    row = _census(t, nid)
                    if row is None or row.get("dead"):
                        continue
                    seen += 1
                    if _goto_to_patch(t, row):
                        ordered.append(_job_sample(row))
                    if _under_patch(t, row.get("x"), row.get("z")):
                        onpatch.append((row.get("x"), row.get("z")))
                _note(t, "no-Burn control: living samples / samples standing on the patch", [seen, len(onpatch)])
                if seen < 8:
                    _unmeasured(t, "the native was readable alive in only %d of 32 samples: the control proves nothing" % seen)
                if ordered:
                    _fail("with NO Burn the UV-shy native was ordered to the roof patch: %s" % ordered[:3])

        # poison: every row below reads or ends the Burn this one forces; if it could not be raised (UNMEASURED) they would see no
        # Burn at all -- "harmless at zero damage" and "lapses" would pass vacuously, "vanished when burnEnabled went off" would FAIL
        with _comp(t, "repulsor_forces_burn", poison=True, toggle="cloudRepulsorEnabled"):
            if _live(t):
                _power_on(t, _STATE["rep_id"])
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
                if not _alive(rows.get(b["open"])):
                    _unmeasured(t, "the open visitor is not readable alive: 'not harmed' would mean nothing")
                hit = [k for k in ("open", "native") if _hdefs(rows.get(b[k])) & {"RM_BurnDose", "Burn"}]
                if rows.get(b["native"]) is None:
                    _unmeasured(t, "the native's row is absent (no corpses are listed): nothing to read")
                if hit or not _alive(rows.get(b["native"])):
                    _fail("burnDamageFactor=0 still harmed: %s (native alive=%s)"
                          % (hit, _alive(rows.get(b["native"]))))

        with _comp(t, "burn_doses_the_exposed_visitor", toggle="burnDamageFactor"):
            if _live(t):
                b = _STATE["burn"]
                # LIVE 2026-10-08: the native spawned with the fixture walked ~115 cells away during the
                # 3900 harmless ticks (PressureActive is false at burnDamageFactor 0, so nothing kept it
                # near the roof patch), and the dive read found it at (54,174). The dive can only happen
                # once damage is on, so the native it is judged on is spawned beside the patch HERE.
                x, z = t.anchor
                b["native_fixture"] = b["native"]
                b["native"] = _spawn(t, UV_NATIVE, x, z + 4)
                # Same for the armored control: the fixture one wandered too, and off the unroofed pad (a mountain
                # tile keeps its roof there) "spared" would mean sheltered, not armored. Spawned on the open pad here.
                b["armored_fixture"] = b["armored"]
                b["armored"] = _spawn(t, ARMORED, x, z - 6)
                _set(t, "burnDamageFactor", 1)
                track, atrack, nhd, vhd = [], [], set(), set()
                jobs, dive_orders = [], []
                respawns = 0
                for _ in range(32):                  # 32 x 25 = the same 800 ticks, sampling the dive
                    _wait(t, 25)
                    srows = _rows(t)
                    nrow = srows.get(b["native"])
                    # LIVE round 2 2026-10-16: the native's row went absent (it dies fast under the Burn; list_pawns lists
                    # no corpses) before any living sample carried Burn, so both native rows were UNMEASURED. A finer
                    # sample catches the Burn while it lives; if it is lost with none seen, a fresh one is spawned beside
                    # the patch (at most twice). Samples already kept stay: they are living reads.
                    if (nrow is None or not _alive(nrow)) and "Burn" not in nhd and respawns < 2:
                        respawns += 1
                        b["native"] = _spawn(t, UV_NATIVE, x, z + 4)
                        track, jobs, dive_orders = [], [], []
                        continue
                    arow = srows.get(b["armored"]) or {}
                    vhd |= _hdefs(srows.get(b["open"]))                   # the dose on ANY sample, not just the last
                    if nrow is not None and _alive(nrow):                 # only a living sample is a position or a hediff read
                        track.append((nrow.get("x"), nrow.get("z")))
                        crow = _census(t, b["native"])                      # what it is DOING: the dive is a Goto to the patch
                        if crow is not None and not crow.get("dead"):
                            jobs.append(_job_sample(crow))
                            if _goto_to_patch(t, crow):
                                dive_orders.append(_job_sample(crow))
                        nhd |= _hdefs(nrow) | _burned_off(nrow)
                    atrack.append((arow.get("x"), arow.get("z")))
                # LIVE modcheck5 2026-10-16: the UV-shy native died inside the 800 ticks and list_pawns lists no corpses,
                # so the end-of-window row was absent and both native rows went UNMEASURED. What it carried and where it
                # stood while ALIVE is kept, so a Burn and a dive seen before it died are still read.
                b["native_track"], b["armored_track"], b["native_hd_alive"] = track, atrack, nhd
                b["native_jobs"], b["dive_orders"] = jobs, dive_orders
                _note(t, "burn native respawns (lost before a Burn was read)", respawns)
                rows = _rows(t)
                if not _alive(rows.get(b["open"])):
                    _unmeasured(t, "the open visitor is not readable alive after the Burn: 'undosed' would mean nothing")
                if "RM_BurnDose" not in (_hdefs(rows.get(b["open"])) | vhd):
                    # LIVE 2026-10-19b (536-mod list, contagion_v1_AREAFIX): this row FAILED with only the visitor's
                    # end hediffs as evidence ('AS_DuncePassion', 'SEX_Womb'), and its four downstream rows went
                    # UNMEASURED, so nothing said whether the pressure loop ran at all. The same code PASSED on the
                    # 22-mod list 2026-10-17. Offline reading of RM_GameCondition_ContagionBurn.Pressure: a human
                    # visitor is never native (Classify -> Dose), HealthUtility.AdjustSeverity cannot no-op on a
                    # positive offset, and the 800-tick window holds three 250-tick pulses -- so an undosed visitor
                    # means (a) no pulse ran (the Burn condition or its weather was gone: PressureActive false),
                    # (b) the visitor's cell was sheltered (Exposed false: a roof rebuilt over the pad), or (c) a
                    # real mod fault. The row now reads all three before it rules, and names which.
                    vrow = rows.get(b["open"]) or {}
                    vx, vz = vrow.get("x"), vrow.get("z")
                    cond_on, wx = _has_cond(t, BURN_COND), _weather_now(t)
                    vroof, roof_read = None, False
                    if vx is not None and vz is not None:
                        rr = t.bridge_call("jawa/get_roof_batch", rects="%d,%d,1,1" % (vx, vz))
                        roofs = (rr.get("roofs") or []) if isinstance(rr, dict) else []
                        roof_read = bool(roofs)
                        vroof = roofs[0] if roofs else None
                    _, rep_lines = _inspect(t, _STATE["rep_id"])
                    pulsed = "Burn" in nhd
                    diag = {"visitor_at": [vx, vz], "visitor_roof": vroof, "burn_condition": cond_on,
                            "weather": wx, "native_burned_while_alive": pulsed, "repulsor": rep_lines}
                    _note(t, "undosed visitor: what the Burn was doing", diag)
                    if not cond_on or wx != BURN_WEATHER:
                        if "the Burn is forced" in rep_lines:
                            _fail("the powered repulsor says the Burn is forced but the Burn is not holding the sky "
                                  "(condition %s, weather %r): no pressure pulse could dose anyone; %s"
                                  % (cond_on, wx, diag))
                        _unmeasured(t, "SITE: the forced Burn was not holding at the end of the dose window and the "
                                       "repulsor is not forcing it (%s): the visitor was never under pressure" % diag)
                    if not roof_read:
                        # a failed or empty roof read is ignorance, not open sky (review 2026-10-20)
                        _unmeasured(t, "the open visitor's roof could not be read (%s): exposure cannot be judged" % diag)
                    if vroof not in (None, "None"):
                        _unmeasured(t, "SITE: the open visitor's cell (%s,%s) is roofed (%s): it was sheltered, not "
                                       "exposed" % (vx, vz, vroof))
                    _fail("an exposed visitor carries no RM_BurnDose after the Burn pressed on it "
                          "(hediffs: %s; %s)" % (sorted(_hdefs(rows.get(b["open"]))), diag))
                rrow = rows.get(b["roofed"])
                if not _alive(rrow):
                    _unmeasured(t, "the ROOFED control visitor is not readable alive: shelter cannot be judged")
                if not _under_patch(t, rrow.get("x"), rrow.get("z")):
                    _unmeasured(t, "the ROOFED control visitor is not under the roof patch (at %s,%s): shelter cannot "
                                   "be judged" % (rrow.get("x"), rrow.get("z")))
                if "RM_BurnDose" in _hdefs(rows.get(b["roofed"])):
                    _fail("a ROOFED visitor was dosed: shelter must protect")
                _STATE["rows_after"] = rows

        with _comp(t, "burn_hurts_native_spares_armored"):
            if _live(t):
                rows, b = _STATE.get("rows_after"), _STATE["burn"]
                if rows is None:
                    _unmeasured(t, "burn_doses_the_exposed_visitor did not run")
                nat, arm = rows.get(b["native"]), rows.get(b["armored"])
                # A row that is not there at all (crushed, vanished, or killed: list_pawns lists no corpses) proves
                # nothing by itself; the hediffs read on the native while it was still alive (native_hd_alive) are.
                alive_hd = set(b.get("native_hd_alive") or ())
                if not _alive(arm):
                    _unmeasured(t, "armored alive %s: nothing to judge" % _alive(arm))
                if _alive(nat):
                    alive_hd |= _hdefs(nat) | _burned_off(nat)
                elif "Burn" not in alive_hd:
                    _unmeasured(t, "the UV-shy native's row is %s and no living sample carried Burn: its damage cannot "
                                   "be read (living hediffs %s)" % ("absent" if nat is None else "dead", sorted(alive_hd)))
                _note(t, "native alive at the end / Burn seen while alive", [_alive(nat), "Burn" in alive_hd])
                if "Burn" not in alive_hd:
                    _fail("the UV-shy native took no Burn damage under open sky (hediffs: %s)"
                          % sorted(alive_hd))
                apos = list(b.get("armored_track") or []) + [(arm.get("x"), arm.get("z"))]
                if not all(_on_open_pad(t, px, pz) for px, pz in apos):
                    _unmeasured(t, "the armored control left the open pad (positions %s): 'spared' could be shelter"
                                % apos)
                if "Burn" in (_hdefs(arm) | _burned_off(arm)):
                    _fail("the ARMORED native took Burn damage: %s" % sorted(_hdefs(arm)))

        with _comp(t, "native_dives_for_roof"):
            if _live(t):
                rows, b = _STATE.get("rows_after"), _STATE["burn"]
                if rows is None:
                    _unmeasured(t, "burn_doses_the_exposed_visitor did not run")
                nat = rows.get(b["native"])
                x, z = t.anchor

                def _under(px, pz):
                    return px is not None and pz is not None and x + 6 <= px < x + 14 and z - 4 <= pz < z + 4
                # It dives to the patch's nearest edge cell, then may wander out and be re-dived at the
                # next 250-tick pass, so ANY sample under the patch is the dive (it spawned 6 cells out).
                # The track holds living samples only, so a dive seen before the native died still counts.
                # CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME: a position under the patch is NOT a dive (a native wandering onto
                # 8x8 cells passes that). The dive is the Burn's own order, a Goto job whose target is under the patch,
                # read from pawn_census while the native lived; a wander is GotoWander and never matches.
                track = b.get("native_track") or []
                orders = b.get("dive_orders") or []
                jobs = b.get("native_jobs") or []
                onpatch = any(_under(px, pz) for px, pz in track)
                _note(t, "native job samples (def, targetA) / dive orders / samples on the patch",
                      [sorted(set(map(str, jobs)))[:8], len(orders), sum(1 for p in track if _under(*p))])
                if not orders:
                    if not jobs:
                        _unmeasured(t, "the native died before any job of it could be read (living positions %s)" % track)
                    _fail("the UV-shy native was never ordered to the roof patch (no Goto targeting %s; jobs seen %s); "
                          "standing on the patch %s is a wander, not a dive; positions %s"
                          % ((x + 6, z - 4, 8, 8), sorted(set(map(str, jobs)))[:6], onpatch, track))

        with _comp(t, "burn_off_means_no_harm", toggle="burnEnabled"):
            if _live(t):
                x, z = t.anchor
                # LIVE 2026-10-08: the visitor used to be spawned and walked 200 ticks under the forced Burn
                # BEFORE the toggle went off, so a pressure pass dosed it with burnEnabled still ON (severity
                # 0.0117, under one 0.02 pass). The toggle goes off FIRST; the visitor never sees burnEnabled on.
                with _setting(t, "burnEnabled", False):
                    fresh = t.spawn_pawn("Colonist", hostile=False)
                    t.bridge_call("jawa/set_draft", pawnId=fresh, drafted=True)
                    t.bridge_call("jawa/order_pawn", pawnId=fresh, x=x - 12, z=z - 10, waitTicks=200)
                    _wait(t, 800)
                    if not _has_cond(t, BURN_COND):
                        _fail("the forced Burn vanished when burnEnabled went off: the device must "
                              "still hold the storm open")
                    frow = _rows(t).get(fresh)
                    if not _alive(frow):
                        _unmeasured(t, "the fresh visitor is not readable alive: 'not dosed' would mean nothing")
                    fx, fz = frow.get("x"), frow.get("z")
                    if not _on_open_pad(t, fx, fz):
                        _unmeasured(t, "the fresh visitor is not on the open pad (at %s,%s): 'not dosed' could be "
                                       "shelter" % (fx, fz))
                    if "RM_BurnDose" in _hdefs(frow):
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
    try:
        _stable(t, body)
    finally:
        # drafted colonists never eat; the fixture pair must not outlive the chain drafted (they sit on the pad,
        # but a colonist the pad cleanup missed would starve through the later chains' waits)
        b = _STATE.pop("burn", None) or {}
        if t.session is not None:
            for k in ("open", "roofed"):
                if b.get(k):
                    try:
                        t.session.call("jawa/set_draft", pawnId=b[k], drafted=False)
                    except Exception:                           # noqa: BLE001 - already removed
                        pass


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
                        _harness("fixture: no %s" % k)

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


# --------------------------------------------------------------------------- chain: touched
# Contagion-touched and the Sunbeam arrest (owner 2026-10-15: N4 "Bloom time, stronger in burn, and contact."; Q3 "Stops
# current mutations. No protection if you get exposed again later."). Only the CONTACT source is driven here: a drafted
# colonist stands against a Coalescence (stationary, and set inert with coalescenceEnabled off so it neither absorbs nor
# emits). The Bloom/Burn doses and the mutation roll are arithmetic, fuzzed offline (SelfTest family "touched").

@suite.chain("touched")
def touched(t):
    def body():
        with _comp(t, "touched_site_ready", poison=True):
            _pad(t, "touched")
            if _live(t):
                _baseline(t)
                _prep(t, "touched")
                _set(t, "burnEnabled", False)
                _set(t, "coalescenceEnabled", False)
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (COALESCENCE, x, z))
                if not _things(t, COALESCENCE, _rs(_rect(t))):
                    _harness("fixture: no Coalescence spawned")
                _STATE["touched"] = {"near": _spawn(t, "Colonist", x + 2, z, faction="player")}
                t.bridge_call("jawa/set_draft", pawnId=_STATE["touched"]["near"], drafted=True)

        with _comp(t, "touched_off_doses_nothing", toggle="touchedEnabled"):
            if _live(t):
                x, z = t.anchor
                with _setting(t, "touchedEnabled", False):
                    off = _spawn(t, "Colonist", x - 2, z, faction="player")
                    t.bridge_call("jawa/set_draft", pawnId=off, drafted=True)
                    _wait(t, 1000)
                    row = _rows(t, _rs(_rect(t))).get(off)
                    if not _alive(row):
                        _unmeasured(t, "the toggle-off colonist is not readable alive")
                    if TOUCHED in _hdefs(row):
                        _fail("dosed by contact with touchedEnabled off")
                    t.bridge_call("jawa/pawn_force_incapacitate", pawn=off, action="vanish")

        with _comp(t, "touched_contact_doses", toggle="touchedEnabled"):
            if _live(t):
                # The standing Bloom doses Contagion-touched too (owner N4: "Bloom time ... and contact"), so a dose
                # alone does not prove CONTACT: a drafted control 12 cells off the Coalescence, under the same sky for
                # the same ticks, must end with LESS than the colonist against it.
                x, z = t.anchor
                far = _spawn(t, "Colonist", x - 12, z - 12, faction="player")
                t.bridge_call("jawa/set_draft", pawnId=far, drafted=True)
                _wait(t, 1000)
                rows = _rows(t, _rs(_rect(t)))
                row, frow = rows.get(_STATE["touched"]["near"]), rows.get(far)
                if row is None or not _alive(frow):
                    _unmeasured(t, "the colonist beside the Coalescence / the far control is not readable")
                # contact needs the Coalescence still standing and the colonist still beside it: a drafted pawn can be shoved off,
                # and the Coalescence collapses under any Burn -- either leaves no contact to dose
                if not _things(t, COALESCENCE, _rs(_rect(t))):
                    _unmeasured(t, "the Coalescence is gone from the pad: there was no contact to dose")
                if not _alive(row) or abs((row.get("x") or 0) - x) > 4 or abs((row.get("z") or 0) - z) > 4:
                    _unmeasured(t, "the colonist is no longer beside the Coalescence (at %s,%s, anchor %s,%s)" % (row.get("x"), row.get("z"), x, z))
                if TOUCHED not in _hdefs(row):
                    _fail("1000 ticks against a Coalescence gave no %s: %s" % (TOUCHED, sorted(_hdefs(row))))
                near_sev, far_sev = _sev(row, TOUCHED), _sev(frow, TOUCHED)
                _note(t, "touched severity (contact, far control)", [near_sev, far_sev])
                if not near_sev > far_sev:
                    _fail("contact added nothing: %s %.4f against the Coalescence vs %.4f on the far control"
                          % (TOUCHED, near_sev, far_sev))
                t.bridge_call("jawa/pawn_force_incapacitate", pawn=far, action="vanish")

        with _comp(t, "sunbeam_hit_arrests", toggle="sunbeamArrestEnabled"):
            if _live(t):
                pid = _STATE["touched"]["near"]
                if TOUCHED not in _hdefs(_rows(t, _rs(_rect(t))).get(pid)):
                    _unmeasured(t, "the colonist carries no %s before the hit: nothing to arrest" % TOUCHED)
                # off arm first: with sunbeamArrestEnabled off a landed hit must leave Contagion-touched in place
                with _setting(t, "sunbeamArrestEnabled", False):
                    _ok(t.bridge_call("jawa/damage", damageDef="RM_UVBeam", amount=5, thingId=pid, allowColonists=True),
                        "damage(RM_UVBeam, arrest off)")
                    hd0 = _hdefs(_rows(t, _rs(_rect(t))).get(pid))
                    if "RM_UVSunburn" not in hd0:
                        _unmeasured(t, "the toggle-off Sunbeam hit left no RM_UVSunburn: it did not land (%s)" % sorted(hd0))
                    if TOUCHED not in hd0:
                        _fail("a Sunbeam hit arrested %s with sunbeamArrestEnabled off" % TOUCHED)
                # LIVE modcheck6 2026-10-16: 'RM_UVSunburn present' after this hit was inherited from the OFF arm's hit,
                # so a deflected ON hit (no damage dealt, so rightly no arrest) read as 'landed, did not arrest'. The ON
                # hit lands only if the sunburn GREW.
                # LIVE modcheck8 2026-10-16: a hit can be wholly deflected (sunburn 5.00 -> 5.00), which rightly arrests
                # nothing; up to three hits are tried and the first that lands is the one judged.
                burn0 = burn1 = _sev_sum(_rows(t, _rs(_rect(t))).get(pid), "RM_UVSunburn")
                for _try in range(3):
                    _ok(t.bridge_call("jawa/damage", damageDef="RM_UVBeam", amount=5, thingId=pid, allowColonists=True),
                        "damage(RM_UVBeam)")
                    row = _rows(t, _rs(_rect(t))).get(pid)
                    hd = _hdefs(row)
                    burn1 = _sev_sum(row, "RM_UVSunburn")
                    if burn1 > burn0:
                        break
                if burn1 <= burn0:
                    _unmeasured(t, "the Sunbeam hit added no RM_UVSunburn (%.2f -> %.2f): the hit itself did not land "
                                   "(%s)" % (burn0, burn1, sorted(hd)))
                if TOUCHED in hd:
                    _fail("a Sunbeam hit did not arrest %s" % TOUCHED)
    _stable(t, body)


# --------------------------------------------------------------------------- chain: zhool_haze

@suite.chain("zhool_haze")
def zhool_haze(t):
    """CompZhoolHaze (owner ruling 2026-10-15, phase0_p3_questions Q2 "A"): plants in a zhool's haze turn into the
    Contagion's own flesh-plants, only on our biomes, replaced in place (never deleted without a replacement). The
    off arm runs first on the same fixture and must turn nothing; the on arm runs at the top turning speed so a
    5000-tick wait expects ~8 turned cells (P(none) ~ 3e-4 if the mechanic works)."""
    def body():
        _need_contagion(t)
        with _comp(t, "zhool_site_ready", poison=True):
            _pad(t, "zhool")
            if _live(t):
                _baseline(t)
                _prep(t, "zhool")
                x, z = t.anchor
                ops = ["%s:%d,%d" % (GRASS, x + dx, z + dz)
                       for dx in range(-ZHOOL_FILL, ZHOOL_FILL + 1) for dz in range(-ZHOOL_FILL, ZHOOL_FILL + 1)]
                t.bridge_call("jawa/spawn_batch", ops=";".join(ops))
                _STATE["zrect"] = _rs(_rect(t, PAD_SIZE))
                n = len(_things(t, GRASS, _STATE["zrect"]))
                if n < len(ops) // 2:
                    _harness("fixture: wanted ~%d grass plants, found %d" % (len(ops), n))
                if _things(t, LASHGRASS, _STATE["zrect"]):
                    _harness("fixture: lashgrass already on the cleared pad")
                _STATE["zhool"] = _spawn(t, ZHOOL, x, z)

        with _comp(t, "conversion_off_turns_nothing", toggle="zhoolConversionEnabled"):
            if _live(t):
                with _setting(t, "zhoolConversionRate", 5.0):
                    with _setting(t, "zhoolConversionEnabled", False):
                        _wait(t, 3000)
                        lash = _things(t, LASHGRASS, _STATE["zrect"])
                        # 'nothing turned' means something only while a zhool and grass are there to turn
                        zrow = _rows(t).get(_STATE.get("zhool"))      # map-wide: wandered off vs died
                        zon = _alive(_rows(t, _STATE["zrect"]).get(_STATE.get("zhool")))
                        ngrass = len(_things(t, GRASS, _STATE["zrect"]))
                        # 'nothing turned' means something only while a zhool and grass are there to turn
                        if not zon or not ngrass:
                            _unmeasured(t, "the zhool or its grass is gone from the pad: the off arm saw nothing "
                                           "(zhool on pad %s, map row %s, grass %d)"
                                        % (zon, json.dumps({k: (zrow or {}).get(k) for k in ("x", "z", "dead", "downed")}),
                                           ngrass))
                        if lash:
                            _fail("%d grass turned to lashgrass with zhoolConversionEnabled off" % len(lash))
                _STATE["grass0"] = len(_things(t, GRASS, _STATE["zrect"]))

        with _comp(t, "haze_turns_grass_in_place", toggle="zhoolConversionRate"):
            if _live(t):
                if not _alive(_rows(t, _STATE["zrect"]).get(_STATE.get("zhool"))):
                    _unmeasured(t, "the zhool is not alive on the pad; nothing could turn")
                # LIVE round 2 2026-10-16: the zhool WANDERED off the grass fill (haze radius 3.9 inside a +-7 fill), so
                # "no lashgrass in 5000 ticks" was read at a bound (P(none) ~ 3e-4) that only holds while the haze
                # sits on grass. An animal cannot be pinned (no supported teleport), so the bound is made honest:
                # sample its cell every 250 ticks and count the samples inside the fill (haze fully on grass).
                zx, zz = t.anchor
                inside, samples = 0, []
                with _setting(t, "zhoolConversionRate", 5.0):
                    for _ in range(20):
                        _wait(t, 250)
                        zr = _rows(t).get(_STATE.get("zhool")) or {}
                        px, pz = zr.get("x"), zr.get("z")
                        samples.append((px, pz))
                        if (px is not None and pz is not None and _alive(zr)
                                and abs(px - zx) <= ZHOOL_FILL - 4 and abs(pz - zz) <= ZHOOL_FILL - 4):
                            inside += 1
                _note(t, "zhool samples inside the haze-on-grass core / 20", [inside, samples[:20:4]])
                lash = len(_things(t, LASHGRASS, _STATE["zrect"]))
                grass1 = len(_things(t, GRASS, _STATE["zrect"]))
                if _STATE.get("grass0") is None:
                    _unmeasured(t, "no grass count from the off arm: the replacement check has no baseline")
                lost = _STATE["grass0"] - grass1
                _note(t, "zhool haze: grass before/after, lashgrass after", [_STATE.get("grass0"), grass1, lash])
                if lash < 1 and inside < 10:
                    _unmeasured(t, "no lashgrass, but the zhool stood in the grass core for only %d of 20 samples: "
                                   "the ~3e-4 bound assumes the haze sat on grass for the whole 5000 ticks" % inside)
                if lash < 1:
                    _fail("no grass turned to lashgrass in 5000 ticks at 5x speed with the zhool in the grass core "
                          "%d of 20 samples (expected ~8)" % inside)
                if lost > lash:
                    _fail("%d grass gone but only %d lashgrass stand: plants deleted without a replacement"
                          % (lost, lash))
    _stable(t, body)


# --------------------------------------------------------------------------- chain: coalescence

def _unfinished_emission(trig, known_nums=frozenset()):
    """A safe_advance trigger caused by an emitted manhunter Unfinished (see coalescence_emits_...). `known_nums`: the
    thingIDNumbers of every pawn on the map before the jump; a 'mental Manhunter' trigger carries no def, so only a
    pawn that was NOT there before (an emission) may match it."""
    if trig.get("critical") or trig.get("declared"):
        return False
    k, d = trig.get("kind"), str(trig.get("detail") or "")
    if k == "hostile_arrival":
        return UNFINISHED in d
    if k == "mental":
        return ("Manhunter" in d and trig.get("severity") != "damage"
                and trig.get("subjectId") is not None and trig.get("subjectId") not in known_nums)
    if k == "hurt":
        return ("from " + UNFINISHED) in d
    return False


def _mass_stage(lines):
    m = re.search(r"Stage (\d+), absorbed mass (\d+)", lines)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


@suite.chain("coalescence")
def coalescence(t):
    def body():
        _STATE.pop("monstrous", None)
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
                    _harness("fixture: wanted 1 %s, found %d" % (COALESCENCE, len(rows)))
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
                    # >= 5 absorb passes (the on arm needs one to order the walk and a later one to eat), still far
                    # under passiveGrowthTicks 6000
                    _wait(t, 1500)
                    if not _things(t, COALESCENCE, _rs(_rect(t, 24))):
                        # the thing is GONE. A Burn collapses a Coalescence regardless of the toggle
                        # (Building_RM_Coalescence.Tick), and leaves monstrous samples; an idle toggle-off
                        # Coalescence must never just vanish.
                        samples = _things(t, SAMPLE, _rs(_rect(t, 24)))
                        if samples or _has_cond(t, BURN_COND):
                            _unmeasured(t, "harness: a Burn collapsed the Coalescence during the arm "
                                           "(burn condition %s, %d sample(s) left)"
                                        % (_has_cond(t, BURN_COND), len(samples)))
                        _fail("the Coalescence vanished with coalescenceEnabled off and no Burn collapse "
                              "(no samples, no Burn condition)")
                    # the Coalescence's own mass is the read: an absorbed Unfinished moves it. A candidate that is merely GONE
                    # (its lifespan ran out, it wandered off the map) with the mass untouched absorbed nothing and proves
                    # nothing either: UNMEASURED, never a FAIL (review 2026-10-20)
                    sm = _mass_stage(_inspect(t, _STATE["coal"])[1])
                    if sm != (1, 0):
                        _fail("mass moved with coalescenceEnabled off: %s" % (sm,))
                    if not _alive(_rows(t).get(kid)):
                        _unmeasured(t, "the off arm's Unfinished is gone with the Coalescence's mass untouched: no candidate "
                                       "stood to be absorbed, so 'absorbs nothing' was not tested")
                # the off arm's Unfinished would otherwise be absorbed in the next arm and pad its mass count
                t.bridge_call("jawa/pawn_force_incapacitate", pawn=kid, action="vanish")
                t.bridge_call("jawa/destroy_batch", rects=_rs(_rect(t, 24)), categories="Item")

        with _comp(t, "coalescence_absorbs_and_grows_a_stage", toggle="coalescenceEnabled"):
            if _live(t):
                x, z = _STATE["coal_xz"]
                kids = [_spawn(t, UNFINISHED, x + 3, z + i - 3) for i in range(6)]
                # LIVE 2026-10-08: a fixed 600-tick wait read mass 5 with 2 of 6 still alive, both parked INSIDE
                # the absorb ring at (x+2, z-2) and (x+2, z+2). Absorb runs once per 250-tick pass: one pass
                # orders the walk, a LATER pass eats whoever has arrived, and an Unfinished (impaired Moving,
                # Walk urgency) can miss a pass. Poll pass by pass until the six are gone. The cap keeps the
                # whole arm under passiveGrowthTicks (6000), so passive growth cannot stand in for absorption.
                left = list(kids)
                for _ in range(10):
                    _wait(t, 250)
                    rows = _rows(t)
                    left = [k for k in kids if _alive(rows.get(k))]
                    if not left:
                        break
                stage, mass = _mass_stage(_inspect(t, _STATE["coal"])[1])
                _note(t, "after absorbing 6", {"left": len(left), "stage": stage, "mass": mass})
                if mass is None:
                    _unmeasured(t, "Coalescence inspect line unreadable")
                if mass < STAGE_MASS[1] or stage < 2:
                    # LIVE 2026-10-19b (536-mod list, contagion_v1_AREAFIX): Stage 1, mass 1, 5 of 6 still alive after
                    # ten passes -- the old message said "absorbed 6", which was the harness's assumption, not a read.
                    # The same code PASSED on the 22-mod list 2026-10-17. Building_RM_Coalescence.Absorb skips an
                    # Unfinished that is Downed, has a Faction, or is InMentalState, eats only one standing in the
                    # 1-cell ring round the 3x3 body, and otherwise orders a Walk Goto to the nearest ring cell. So
                    # the survivors' own state decides MOD vs FIXTURE: each is read (cell, downed, faction, mental,
                    # Moving, job) and a survivor Absorb is DESIGNED to skip is a fixture fault, not the mod's.
                    cx, cz = _STATE["coal_xz"]
                    rows = _rows(t)
                    who = []
                    for k in left:
                        r = rows.get(k) or {}
                        c = _census(t, k) or {}
                        mv = ((r.get("health") or {}).get("capacities") or {}).get("Moving")
                        who.append({"id": k, "at": [r.get("x"), r.get("z")],
                                    "inRing": (r.get("x") is not None and abs(r["x"] - cx) <= 2 and abs(r["z"] - cz) <= 2),
                                    "downed": r.get("downed"), "faction": r.get("faction"),
                                    "mental": c.get("inMentalState"), "moving": mv, "job": list(_job_sample(c))})
                    _note(t, "unabsorbed Unfinished", who)
                    skipped = [w for w in who if w["downed"] or w["faction"] or w["mental"]]
                    if who and len(skipped) == len(who):
                        _unmeasured(t, "FIXTURE: every surviving Unfinished is one Absorb skips by design (downed, "
                                       "factioned or in a mental state): %s" % who)
                    _fail("after %d passes the Coalescence reads Stage %s, mass %s (want Stage >= 2 at mass >= %d); "
                          "%d of 6 Unfinished still alive and walkable: %s"
                          % (10, stage, mass, STAGE_MASS[1], len(left), [w for w in who if w not in skipped]))

        with _comp(t, "coalescence_emits_manhunters_and_grows_on_its_own"):
            if _live(t):
                _, before = _inspect(t, _STATE["coal"])
                known = set(p["id"] for p in _things_pawns(t, UNFINISHED, None))
                before_nums = frozenset(n for n in (_idnum(i) for i in _rows(t)) if n is not None)
                _jump(t, 7000)              # passive growth is 1 mass / 6000 ticks; emit every 3000 (stage 2)
                # The arm's OWN product stops safe_advance by design: an emitted manhunter Unfinished is a
                # hostile_arrival / 'turned hostile' / mental Manhunter trigger, and it bites whoever it reaches.
                # Declared for this wait only; any other trigger (a colonist turned hostile, a death, a hurt
                # from anything else) still stops the clock.
                import clockgate   # noqa: E402
                with clockgate.expected_disturbance("Coalescence emits manhunter Unfinished",
                                                    lambda trig: _unfinished_emission(trig, before_nums)):
                    _wait(t, 400)
                stage, mass = _mass_stage(_inspect(t, _STATE["coal"])[1])
                m0 = _mass_stage(before)[1]
                if m0 is None:
                    _unmeasured(t, "Coalescence mass unreadable before the jump: %r" % before)
                if mass is None:
                    _unmeasured(t, "Coalescence mass unreadable after the jump (no Stage line): growth cannot be judged")
                if mass <= m0:
                    _fail("no passive growth over 7000 ticks (passiveGrowthTicks 6000) (mass %s -> %s)" % (m0, mass))
                # LIVE 2026-10-08: jawa/pawn_get carries no mental-state field at all, so the old
                # '"Manhunter" in json.dumps(pawn_get)' test could never pass; and a manhunter runs at
                # the nearest human, out of a 24-cell rect. Read jawa/pawn_mental.currentState for
                # every Unfinished on the WHOLE map that was not there before the jump.
                new = [p for p in _things_pawns(t, UNFINISHED, None) if p["id"] not in known]
                states, unread = {}, []
                for p in new:
                    d = t.bridge_call("jawa/pawn_mental", pawn=p["id"], action="list", limit=1)
                    if not isinstance(d, dict) or d.get("success") is False:
                        unread.append(p["id"])          # a failed mental read is ignorance, not "not a manhunter"
                    states[p["id"]] = ((d or {}).get("currentState"), p.get("hostile"), p.get("downed"),
                                       (p.get("x"), p.get("z")))
                _note(t, "Unfinished new since the jump", states)
                mad = [k for k, v in states.items() if v[0] in ("Manhunter", "ManhunterPermanent")]
                # Read, then removed: the emitted manhunters are this arm's own product, and left alive they maul the
                # next arm's colonist (Vanish: no death, no corpse, no acid burst).
                for k in states:
                    t.bridge_call("jawa/pawn_force_incapacitate", pawn=k, action="vanish")
                if not new:
                    _fail("no Unfinished emitted at all after 7000 ticks (stage %s; emit interval 3000)" % stage)
                if not mad and unread:
                    _unmeasured(t, "pawn_mental could not be read for %s: manhunter status unknown (%s)" % (unread, states))
                if not mad:
                    _fail("%d Unfinished emitted after 7000 ticks but none is a manhunter: %s" % (len(new), states))

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
                for s in got:
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
        _harness("could not put the sample in the colonist's pack: %r" % r)


def _census(t, pid):
    """One pawn's jawa/pawn_census row (job{def,...}, x, z, downed, dead, inMentalState), or None if unreadable."""
    r = t.bridge_call("jawa/pawn_census", ids=str(pid))
    if not isinstance(r, dict) or r.get("success") is False:
        return None
    rows = r.get("pawns") or []
    return rows[0] if rows else None


def _job(row):
    return ((row or {}).get("job") or {}).get("def")


def _idnum(pid):
    m = re.search(r"(\d+)$", str(pid or ""))
    return int(m.group(1)) if m else None


def _on_bed(c, bed):
    """The patient stands ON the bed's sleeping slot: a single bed's slot is its Position (the cell list_things reports).
    LIVE 2026-10-16 (round 4): the old test, 'within 1 cell', read a patient still WALKING to the bed, diagonal to it at
    (122,173) vs (121,174), as lying in it; do_bill_now then refused (UsableForBillsAfterFueling false, the patient was
    not in bed) and extraction_surgery_yields_sample went UNMEASURED. pawn_census carries no in-bed field, so the cell
    is the read."""
    try:
        return int(c["x"]) == int(bed["x"]) and int(c["z"]) == int(bed["z"])
    except (KeyError, TypeError, ValueError):
        return False


def _lay_in_bed(t, patient, bed, ceiling=600, step=60):
    """SITE for the surgery: the bill-giver is the PATIENT and Pawn.UsableForBillsAfterFueling holds only while it lies
    in a bed. LIVE 2026-10-16: a fresh, rested patient ordered to LayDown was overridden (CheckForJobOverride every 211
    ticks) and went for a walk, so the first surgery broke off mid-job and the second could not start. So the patient
    is made TIRED first (Rest 0.1: the GetRest node then keeps choosing the same bed), ordered down, and READ lying
    there before the bill is worked. -> (ticks waited, census row) or (None, last census row)."""
    t.bridge_call("jawa/pawn_need", pawn=patient, action="need", need="Rest", level=0.1)
    waited, c = 0, None
    while True:
        c = _census(t, patient)
        if _job(c) == "LayDown" and _on_bed(c, bed):
            return waited, c
        if waited >= ceiling:
            return None, c
        if _job(c) != "LayDown":
            t.bridge_call("jawa/ordered_job", pawnId=patient, jobDef="LayDown", targetAId=bed["id"],
                          waitTicks=0, timeoutSeconds=30)
        _wait(t, step)
        waited += step


SURGERY_STEP, SURGERY_CEILING = 250, 2500


def _surgery_done(t, g):
    """Advance until a genome sample lies in the rect, or the doctor's DoBill ended. The extraction costs its patient
    blood by design (and a failed surgery cuts it), so a 'hurt' stop on THAT patient is a declared disturbance
    (clockgate.expected_disturbance); anyone else hurt still stops the clock. -> the samples found ([] if none).
    Records in g['completed'] how many tries ended with the patient still lying in its bed (a try that ended because
    the patient got up is not a completed surgery)."""
    import clockgate   # noqa: E402 - modcheck dir is on sys.path wherever suite is importable
    pnum = _idnum(g["patient"])
    pred = (lambda trig: trig.get("kind") == "hurt" and pnum is not None and trig.get("subjectId") == pnum)
    # A try counts as COMPLETED only if the doctor was SEEN in DoBill, then seen out of it (a readable census), with the
    # patient still lying in the bed: an unreadable census or a doctor that never started is not a surgery that ran.
    waited, ended, seen = 0, False, False
    with clockgate.expected_disturbance("extraction surgery bleeds its own patient", pred):
        while waited < SURGERY_CEILING:
            _wait(t, SURGERY_STEP)
            waited += SURGERY_STEP
            got = _things(t, SAMPLE, g["rect"])
            if got:
                return got
            d = _census(t, g["doer"])
            if d is None:
                break
            if _job(d) == "DoBill":
                seen = True
            else:
                ended = seen
                break
    c = _census(t, g["patient"])
    # What the ended try actually did (LIVE modcheck5 2026-10-16: three 'completed' tries, no sample, nothing else read):
    # the patient's BloodLoss and its bill stack say whether ApplyOnPawn ran (Bill_Medical deletes the bill on completion),
    # a map-wide sample count catches one placed outside the pad, and the doer's census says why DoBill ended.
    hd = sorted(_hdefs(_rows(t).get(g["patient"])))
    br = t.bridge_call("jawa/bill_list", thingId=g["patient"])
    bills = [b.get("recipeDefName") for b in ((br or {}).get("bills") or [])] if isinstance(br, dict) else br
    try:
        on_map = [(s.get("x"), s.get("z")) for s in _things(t, SAMPLE)]
    except Exception as ex:    # evidence only
        on_map = "unread: %s" % ex
    if ended and _job(c) == "LayDown":
        g["completed"] = g.get("completed", 0) + 1
        g.setdefault("evidence", []).append({"bloodLoss": "BloodLoss" in hd, "bills": bills, "samplesOnMap": on_map})
    _note(t, "surgery try ended without a sample", {"ticks": waited, "doBillEnded": ended, "patient": c,
                                                    "patientHediffs": hd, "patientBills": bills,
                                                    "samplesOnMap": on_map, "doer": _census(t, g["doer"])})
    return []


INJECT_STEP, INJECT_CEILING = 150, 3000


def _inject(t, doer, host):
    """Order the inject job, then WAIT ON ITS OUTCOME, not a flat window: advance in INJECT_STEP chunks until the host
    carries RM_AmoebaGestation, or the doer's job is no longer RM_InjectGenomeSample (it ended: the caller's gestation
    check is then the verdict), up to INJECT_CEILING. Still running at the ceiling, or a doer that could not act
    (dead/downed/mental/unreadable), is UNMEASURED, never a FAIL.
    LIVE 2026-10-16: a flat 600-tick window read 'no gestation' with the doer 2 cells from the host -- the walk from
    wherever the failed surgery left the doer, a wandering host and the 180-tick inject toil outran it (HARNESS)."""
    # waitTicks=0: the game is paused between calls, so the tool's own wait ran no ticks at all and only burned
    # wall time (LIVE 2026-10-16: 205 s, pausedDuringWait true). The read-back is immediate; the clock moves below.
    with _patient(t):
        r = t.bridge_call("jawa/ordered_job", pawnId=doer, jobDef="RM_InjectGenomeSample",
                          targetAId=host, waitTicks=0, timeoutSeconds=30)
    if not _live(t):
        return
    if not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
        _harness("RM_InjectGenomeSample was not accepted and running: %r" % r)
    waited, c, reorders = 0, None, 0
    while waited < INJECT_CEILING:
        _wait(t, INJECT_STEP)
        waited += INJECT_STEP
        if "RM_AmoebaGestation" in _hdefs(_rows(t).get(host)):
            _note(t, "inject: gestation read after", {"ticks": waited})
            return
        c = _census(t, doer)
        if c is None or c.get("dead") or c.get("downed") or c.get("inMentalState"):
            _unmeasured(t, "the injecting colonist could not act (census %s) after %d ticks" % (json.dumps(c)[:300], waited))
        if _job(c) != "RM_InjectGenomeSample":
            _note(t, "inject: the job ended", {"ticks": waited, "doerJobNow": _job(c), "at": (c.get("x"), c.get("z"))})
            if not _alive(_rows(t).get(host)):
                _unmeasured(t, "the host is gone or dead after %d ticks; the inject could not finish" % waited)
            if reorders >= 1:
                return            # ordered twice, ended twice, no gestation: the caller's check is the verdict
            # One re-order before concluding: an interrupted doer is not a verdict. A job that spends the sample
            # without a gestation cannot be re-ordered into one (FailOn: no sample in the pack), so a real defect
            # still ends here as a FAIL.
            reorders += 1
            r = t.bridge_call("jawa/ordered_job", pawnId=doer, jobDef="RM_InjectGenomeSample",
                              targetAId=host, waitTicks=0, timeoutSeconds=30)
            _note(t, "inject: re-ordered once", {"accepted": (r or {}).get("accepted"),
                                                 "running": (r or {}).get("nowRunningRequested")})
    _unmeasured(t, "the inject job was still running after %d ticks (doer at %s, job %s): the window, not the mod"
                % (waited, (c or {}).get("x"), json.dumps((c or {}).get("job"))[:200]))


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
                    _harness("fixture: colonists not spawned")

        with _comp(t, "extraction_surgery_yields_sample", toggle="genomeOrganGrowingEnabled"):
            if _live(t):
                g = _STATE["g"]
                t.bridge_call("jawa/set_pawn_skill", pawn=g["doer"], skill="Medicine", level=20)
                made = None
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="Bed:%d,%d" % (x - 4, z + 4), stuff="WoodLog")
                # A surgery's bill-giver is the PATIENT, and Pawn.UsableForBillsAfterFueling is true only
                # while the patient is IN a bed (the tool words it "the giver needs fuel"; MEASURED live
                # 2026-10-03: a bed existed but the patient stood beside it, so JobOnThing returned null
                # on all three tries). Lay the patient down on the bed first.
                beds = _things(t, "Bed", g["rect"])
                if not beds:
                    _unmeasured(t, "fixture: the Bed did not spawn for the surgery")
                bed = beds[0]
                for attempt in range(3):     # surgery can fail on skill; three completed tries
                    # A surgery bill is a Bill_Medical (jawa/bill_add makes one for a surgery on a pawn since
                    # 2026-10-16; before, it made a Bill_Production that never ran ApplyOnPawn), with no repeat fields.
                    bl = t.bridge_call("jawa/bill_list", thingId=g["patient"])
                    if not any(b.get("recipeDefName") == "RM_ExtractGenomeSample" for b in ((bl or {}).get("bills") or [])):
                        ba = t.bridge_call("jawa/bill_add", giverId=g["patient"], recipe="RM_ExtractGenomeSample")
                        if (ba or {}).get("billClass") != "Bill_Medical":
                            _unmeasured(t, "HARNESS: bill_add did not make a Bill_Medical for the surgery: %s"
                                        % json.dumps(ba, default=str)[:300])
                    inbed, c = _lay_in_bed(t, g["patient"], bed)
                    if inbed is None:
                        _unmeasured(t, "SITE: the patient never lay in the bed at (%s,%s) (census %s)"
                                    % (bed.get("x"), bed.get("z"), json.dumps(c, default=str)[:300]))
                    # waitTicks=0: the game is paused between calls, so a server-side wait ran no ticks and only burned
                    # wall time (LIVE 2026-10-16: 90 s per try, pausedDuringWait true). The clock moves in _surgery_done.
                    with _patient(t):
                        r = t.bridge_call("jawa/do_bill_now", billGiverId=g["patient"], pawnId=g["doer"],
                                          workGiverDef="DoBillsMedicalHumanOperation", waitTicks=0, timeoutSeconds=30)
                    if (r or {}).get("jobOnThingReturnedNull") or (isinstance(r, dict) and r.get("success") is False):
                        _unmeasured(t, "the surgery job could not start (patient not in a bed / giver "
                                       "unusable): %s" % json.dumps((r or {}).get("details"), default=str)[:300])
                    got = _surgery_done(t, g)
                    if got:
                        made = got[0]
                        break
                if not made:
                    if not g.get("completed"):
                        _unmeasured(t, "none of the three surgery tries ran to its end with the patient in bed")
                    _fail("%d completed extraction surgery tries produced no genome sample (per try: %s)"
                          % (g["completed"], json.dumps(g.get("evidence"), default=str)[:500]))
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
                        _harness("fixture: no genome sample to inject")
                    g["sample"] = got[0]["id"]
                g["host"] = _spawn(t, HOST, x + 4, z + 3)
                _give(t, g["doer"], g["sample"])
                _inject(t, g["doer"], g["host"])
                row = _rows(t).get(g["host"])
                if not _alive(row):
                    _unmeasured(t, "the host is not readable alive after the inject job: %s" % json.dumps(row)[:200])
                if "RM_AmoebaGestation" not in _hdefs(row):
                    _fail("the host carries no RM_AmoebaGestation after the inject job (hediffs: %s)"
                          % sorted(_hdefs(row)))
                if _things(t, SAMPLE, g["rect"]):
                    _fail("a sample is still lying around after being injected")

        with _comp(t, "gestation_dies_producing_one_organ_batch"):
            if _live(t):
                g = _STATE["g"]
                # the inject row may have stopped UNMEASURED before a host stood (no key) or with the host dead: nothing to finish
                if not g.get("host") or not _alive(_rows(t).get(g["host"])):
                    _unmeasured(t, "no living gestation host (the inject row did not leave one): there is nothing to complete")
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
                _harness("fixture: no colonist")

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
                # _finish_gestation's severity push can CREATE the hediff, so the inject must be seen to start it
                if "RM_AmoebaGestation" not in _hdefs(_rows(t).get(host)):
                    _unmeasured(t, "no gestation after injecting the second Monstrous sample: the toggle arm has "
                                   "nothing to grow")
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
            r2 = _ok(t.bridge_call("jawa/drain_log", contains="cross-reference", errorsOnly=True, limit=100),
                     "drain_log(cross-reference)")
            if len(r2.get("messages") or []) >= 100:
                # the owned-def filter runs after the cap: a full page may hide ours behind other mods' errors
                _unmeasured(t, "the cross-reference page is full (100): ours could lie past it")
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
            # the START biome: RM_Contagion on the saved Contagion site, the stock biome on a stock map
            tile, orig = _STATE.get("tile"), _STATE.get("start_biome") or _STATE.get("orig_biome")
            if tile is None or not orig:
                _unmeasured(t, "no retile was recorded; nothing to restore")
            _ok(t.bridge_call("jawa/world_tile_set", tiles=str(tile), biome=orig, readBack=1),
                "world_tile_set(restore)")
            _ok(t.bridge_call("jawa/world_commit", redraw=False, recalcPaths=False), "world_commit")
            if _map_biome(t)[0] != orig:
                _harness("SITE: the map's biome did not return to %s" % orig)
    if t.session is not None and "quiet" in _STATE:
        # put back what the quiet-site profile changed (debug + difficulty statics, the wild-spawner block)
        try:
            import quiet_site as QS   # noqa: E402
            prob = QS.restore_attached(t.session)
        except Exception as ex:                                 # noqa: BLE001
            prob = "%s: %s" % (type(ex).__name__, ex)
        _STATE.pop("quiet", None)
        print("[contagion-note] quiet-site restore: %s" % (prob or "ok"), file=sys.stderr, flush=True)
