"""validation_v2.py -- FlowWorks functional script v2 (the running Northstar functional tier).

Plan (authority): design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md
Evidence:         design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md ("INT")
Does NOT replace src/RimMandrake/FlowWorks/validation.py and never edits the walk.

    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py            # tier O, 0 ticks
    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py --mock     # live tier vs in-memory game
    python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live              # loads the clean saved site
    python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map  # the old path: new quicktest map

THE MAP (TESTSITE_SAVES_BUILD_ONE_CALM_MAP, owner by card 2026-10-15: "Clean saved maps"): `--live` LOADS the clean
saved site `calm` (Utils/modcheck/test_site_saves.py, shared with GSS proof_all: 250x250, mild, dry, pristine engine,
no shrine/casket/trigger/hive/ruin/fog/hostile, read back after the load). --fresh-map generates a quicktest map as
before; --current-map runs on whatever map is current; --site-save NAME picks another registered site.
    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py --compare A.json B.json

Tier O (offline): O1 defs, O2 settings defaults, O3 UNBUILT register, O4 geometry, O5/O6 pulse
oracle, O7 scene predictions, O8 schema lint, O9 shared source, O10 pit width, O-NEG (every offline
check O1-O10 mutated in memory and shown able to go red) and
O-LIVE-NEG (a clean --mock run is green, and each of MockBridge.FAULTS turns its live row red).
Live (python.exe, flowworks tier, bridge held): the clean saved site (--fresh-map: a fresh quicktest map, main menu first),
L preflight, site painted by the runner, S state (0 ticks), A/B/C/R flow phases through
jawa/flowworks_pulse (0 ticks, EVERY excavated cell compared with the oracle at EVERY pulse), J
(the only ticks: ordered pawn jobs, which also carry the engine-OFF window, the clamped cadence and
the rain-toggle negative), the rain phase (0 ticks) and the tail (fluid-switch refusal, log budget).
Result JSON beside this script (--live only). This script records nothing itself: modcheck `run`
swaps ModsConfig and records a mod's own validation.py, and northstar_driver `run` records only ITS
OWN live plans through modcheck.status.record_run -- a validation_v2 result is not one of them.

LEARNED, 2026-10-02 (five live runs; each is a check or guard below, not prose only):
  * MOD defect FLOWWORKS_SHARED_SOURCE_STALL_1 (FIXED same day): two channels off ONE source cell
    -> the second-dug channel stalled at its inlet forever, even off a limitless body. Cause: the
    DoPulse component walk (older than the rank pass) marked source cells in pulseVisited, shared
    across components, so the first-seeded component claimed the source and the other had no
    supplying source -> all keys equal -> only its inlet (fed directly by PickDonor) ever filled.
    Fix: RM_StockMath.CollectComponent tracks sources per component (oracle claim_sources=False);
    O9 + the C# SharedSource_* selftests guard it, and claim_sources=True must go red (O-NEG).
    LIMITED-body split rule: components resolve in excavatedCells order, so each pulse the
    earlier-seeded channel's inlet is paid first; an odd stock gives it the extra level (O9: 3/2).
  * The fixed engine (ddb473416) fills a channel FAR END FIRST: [0,0,0,1] -> [1,1,1,1] in n*D pulses,
    every compass direction, identical vectors (E2_*); reproduced on two fresh maps bit-for-bit.
  * A 1-cell pond at shipped recession supplied exactly ONE level, then receded (floor(4/5) = 0
    supported cells): E3b, as measured 2026-10-02. Since LIQUID_RECESSION_TOPOLOGY_1 (keep-last-cell,
    2026-10-09) and the pond volume unify (2 levels a shallow square, RM_Volume.ShallowBedLevels) W2R is a
    4-cell pond (capacity 8): it fills the whole 4-cell run (stock 8 -> 4) and sheds TWO cells (floor(4/2) = 2
    supported). The old P2 strip "had no source"; a painted 1-cell source fixes it.
  * Rain lands on EVERY unroofed excavated cell of the map, so it runs last and is predicted
    map-wide; RainRate needs ticks after weather_set (TransitionTo lerps over ~4000 ticks), so the
    rain-OFF negative rides the job ticks with rainFillPerPulse pinned 1.0.
  * HARNESS: the J window ended when the jobs did; fast colonists (run 5: 7 chunks) left Rain at 0.18
    and E6n UNMEASURED -> J now keeps pulsing after the jobs until the rain-OFF negative is measurable.
  * HARNESS/SITE lessons: start_debug_game_ready from a running colony times out (go to the main
    menu first); wildlife wanders into plots (destroy_bulk nonColonists); a mining-incapable
    colonist makes pawn_stats log a red error and returns 0.1 (re-roll); pawns left to the
    WorkGivers wandered 60 cells away on a Tundra map (order the job; WorkGiver selection is
    UNCOVERED); the E4 OFF window must straddle the scheduled tick or it proves nothing.
  * HARNESS (rerun 1 with jawa/flowworks_job_probe): J_workgiver_selection failed for 2 of 3 fresh
    colonists -- WorkGiver said yes (hasJobOnCell, RM_FillInCanalJob) but Mining sat at priority 0,
    so the giver was not in their normal list. Generator activates only top work types; setting the
    skill after spawn does not. J now sets Mining priority 1; the mock starts every pawn at 0 so
    dropping that call turns the row red. Rerun B: a pawn with the Mining SKILL enabled but the
    Mining WORK TYPE disabled made set_work_priority refuse and the run ABORTED -> re-rolled now
    (mock fault worktype_disabled_once guards it).
LEARNED, 2026-10-18 (day 3 of the big dig, 32/24/5; Transient/fw_scenes/v2_triage_2026-10-18.md):
  * HARNESS (b): the live oracle was still the whole-notch engine after P3 shipped exact-level water; an offline replay
    (mock game exact + P11 shelf, harness unchanged) reproduced day 3's flow rows cell for cell. The oracle, the mock and
    oracle_for now run level_water's exact model; rows that asserted whole-notch pictures read the oracle instead.
  * SITE (a): P11 gives a pond painted mid-game a lake floor (0.5 m shelf) at classification: the site pins
    deepBedsEnabled OFF (open spec question P11_FLOOR_ON_PAINTED_PONDS).
  * LIVE-ONLY, unresolved: on the calm saved site no spawned colonist moved from phase J on and the first 309-tick step
    ran 0 ticks; E4_off now reads UNMEASURED on such a window, E1c judges cadence from the first real pulse, and E9
    prints the collected lines when the log is dead (day 3 lost them).
RULED OUT (guards keep them visible):
  * "P2's [1,0,0,0] means the brigade order regressed" -- RULED OUT: a foreign D=4 cell had
    claimed the shared source (oracle reproduced live exactly; E2s_shared_source_oracle guards it).
  * "north/south channels stall" (an earlier helper's first live run) -- RULED OUT: the cells were
    in the 10-cell sink band; O4 refuses an undeclared band cell; E2_north/E2_south pass.
  * "the old suite's 3->0 fill-in was arithmetic" -- RULED OUT: sink drainage; E7a/E7b now read the
    displacement and the sanctioned overflow directly (sum F + overflowDestroyedTotal).
"""
import json
import math
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_water  # noqa: E402  (the exact-level reference, WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES)

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)                       # src/RimMandrake/FlowWorks
SRC = os.path.join(MOD, "Source")
DEFS = os.path.join(MOD, "Defs")

MAP_W = MAP_H = 250        # the bland save's map size; L5 refuses a different size
SINK_BAND = 10             # GenGrid.NoBuildEdgeWidth (RM_MapComponent_Excavation.IsSinkCell)
PULSE_PIN = 60             # RimMandrakeFlowWorksSettings.PulseIntervalTicks clamp floor
PULSE_SHIPPED = 250

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_RIVER = "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings"

# The toggles this script's scenes rely on, at their shipped defaults. O2 checks them against a C# census of
# every settings class (which must itself equal site_spec.SETTINGS); the census, not this table, is the floor.
BOOL_DEFAULTS = {
    S_FW: dict(depthEngineEnabled=True, digToDepthEnabled=True,
               liquidCorrosionEnabled=True, liquidIgnitionEnabled=True, fillInEnabled=True,
               fillInDisplacementEnabled=True, sourceBudgetEnabled=True, stickyLimitlessEnabled=True,
               recessionEnabled=True, refillEnabled=True, rainFillsExcavationsEnabled=True,
               edgeSinksEnabled=True, superdeepCaptureEnabled=True, superdeepCapturesOwnFaction=False,
               ladderRequiredToExitEnabled=True, ladderPrisonDoorEnabled=True, spikesEnabled=True,
               flowDoorsSealedFromPitEnabled=True, sluiceLetsBigThroughEnabled=True,
               superdeepShootingRuleEnabled=True,
               bottleLoopEnabled=True, bottleDirtyStageEnabled=True, tankLoopEnabled=True,
               liquidDrillingEnabled=True, typedLiquidShoresEnabled=True, swaleEnabled=True,
               trapTriggerEnabled=True, fallDamageEnabled=True, pitRelativeClimbEnabled=True, pitRampsEnabled=True,
               pitExposureEnabled=True, pitDepthDrawOffsetEnabled=True,
               canalFireEnabled=True,      # FLOWWORKS_BUILD_PROGRAM_1 Phase 6
               pitDrowningEnabled=True, poisonFillEnabled=True,      # PIT_FILL_EFFECTS_1
               viscosityEnabled=True, thickCreepEnabled=True, waterFrontCreepEnabled=True, levelBySurfaceEnabled=True, levelSetEnabled=True, levelExactEnabled=True, recedeKeepsLastCell=True, recedeSparesOutflow=True),     # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (2026-10-05)    # rehoused from PitsSettings 2026-10-02
    S_RIVER: dict(riverSteamEnabled=True),
}
FLOAT_DEFAULTS = {"pulseIntervalTicks": 250.0, "flowPerPulse": 1.0, "rainFillPerPulse": 0.1,
                  "minLimitlessBodyCells": 50.0, "pitWidthBodySizeMultiplier": 1.0, "pitClimbAbilityMultiplier": 1.0, "pitSlowClimbFactor": 2.0, "pitRampMaxSpan": 3, "pitLadderSlowness": 2.0,
                  "trapSensitivityMultiplier": 1.0, "fallDamageMultiplier": 1.0,
                  "spikeDamageMultiplier": 1.0, "swaleRateMultiplier": 1.0,
                  "pitTemperatureCoupling": 3.0, "pitResistanceLossMultiplier": 1.0,
                  "pitSinkPerLevel": 0.3,
                  "burnDaysPerNotch": 1.0,     # Phase 6, ruling 7 (one rate: LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD)
                  "fireFrontSpeedMultiplier": 1.0, "sourceFireReach": 3.0,
                  "pitDrowningRateMultiplier": 1.0}
# PIT_LEGACY_CODE_RETIRE_1: every def the building-pit model shipped (26). O1 asserts each is ABSENT.
RETIRED_PIT_DEFS = (["RM_OpenPit_" + n for n in ("Bare", "Spiked", "Oiled", "Poison", "Water", "Oubliette")]
                    + ["RM_PitDigSite_Shallow_" + n for n in ("Bare", "Spiked", "Oiled", "Poison", "Water", "Oubliette")]
                    + ["RM_PitDigSite_Deep_Bare", "RM_PitDigSite_Chasm_Bare", "RM_PitDigSite_CellSingle",
                       "RM_PitDigSite_CellDouble", "RM_PitCell_Single", "RM_PitCell_Double",
                       "RM_PitDigSiteBase", "RM_OpenPitBase", "RM_PitCellBase",
                       "RM_DigPitDeeper", "RM_PinnedInPit", "RM_SuperdeepPit"])


# ============================================================================ the pulse oracle
CARDINAL = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # GenAdj.CardinalDirections: N, E, S, W


def _fluid_ticks_per_tile():
    """FluidDef defName -> ticksPerTile, read from the mod's own FluidDefs (default 60, as FluidDef.cs)."""
    out = {}
    for dp, _, fns in os.walk(os.path.join(MOD, "Defs")):
        for fn in fns:
            if fn.endswith(".xml"):
                t = open(os.path.join(dp, fn), encoding="utf-8").read()
                for m in re.finditer(r"<(?:[\w.]*\.)?FluidDef\b[^>]*>(.*?)</(?:[\w.]*\.)?FluidDef>", t, re.S):
                    dn = re.search(r"<defName>([^<]+)</defName>", m.group(1))
                    tp = re.search(r"<ticksPerTile>(\d+)</ticksPerTile>", m.group(1))
                    if dn:
                        out[dn.group(1)] = int(tp.group(1)) if tp else 60
    return out


_TPT = {}


def viscosity_stride(ticks_per_tile):
    """Port of RM_StockMath.ViscosityStride: ticksPerTile / water's 60, rounded half up, >= 1."""
    if ticks_per_tile <= 60:
        return 1
    return max(1, (ticks_per_tile + 30) // 60)


def _ticks_per_tile(fluid):
    if not _TPT:
        _TPT.update(_fluid_ticks_per_tile() or {"RM_Fluid_Water": 60})
    return _TPT.get(fluid, 60)


# The shipped creep switches (waterFrontCreepEnabled, thickCreepEnabled; both default ON), as PulseOracle kwargs.
CREEP_LIVE = dict(creep_water=True, creep_thick=True, level_surface=True, level_set=True)   # + levelBySurfaceEnabled, levelSetEnabled (default ON)
# WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17, "ruled exactly level" by card): the shipped engine counts
# water in decilitres, one surface per connected body (levelExactEnabled, default ON). The live oracle, the mock game and
# oracle_for are level_water's exact model; the live site follows the game's own setting (phase_site reads it).
# V2 day 3 (2026-10-17, 32/24/5): the live oracle was still the whole-notch model, so every 0-tick flow row compared the
# exact engine with the notch engine (replayed offline: VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG).
LIVE_EXACT = True


def fluid_moves(pulse, fluid):
    """Port of RM_StockMath.FluidMovesThisPulse for a fluid named by defName."""
    if not _TPT:
        _TPT.update(_fluid_ticks_per_tile() or {"RM_Fluid_Water": 60})
    st = viscosity_stride(_TPT.get(fluid, 60))
    return st <= 1 or pulse % st == 0


class PulseOracle(object):
    """A pure-Python port of the depth engine's pulse: RM_MapComponent_Excavation.DoPulse and
    RM_FlowKernel's ResolveComponent / PickDonor / CompareDeepestFirst (cited by method name; line
    numbers drift). Rain (ApplyRain) and recession (RM_LiquidStock.Recede) are modelled when switched
    on; refill/restore are not. Deterministic by construction: recipients sorted (-D, cell index),
    donors scanned N,E,S,W with strict '>'.

    NOT ported (shipped rules no current live scene reaches; the --mock game inherits the gaps):
      * recession's topology filter -- RM_LiquidStock.PickRecedeCell rejects a cell whose removal
        would split the body (RM_StockMath.LocalRemovalKeepsConnected); the oracle picks by
        neighbours / centroid distance / index only;
    A scene that brings that rule into play needs the port first.

    algo="old" is that engine as measured live 2026-10-01 (east/north channels oscillate).
    algo="fixed" (default) is FLOWWORKS_CHANNEL_OSCILLATION_1's fix: a per-component flow order
    gates cell-to-cell gifts and orders recipients (see _downstream). O6 proves it.

    VALIDATED once against live data (INT section 2): given plot D's geometry (5x5 limited pond,
    12-cell D=3 channel running east, stock 125) it reproduces BOTH oscillating F vectors the
    2026-10-01 run recorded at ticks 538,130..539,880, exactly."""

    def __init__(self, w, h, sources, bodies, per=1, budget=True, sink_band=None, algo="fixed",
                 recession=False, claim_sources=None, creep_water=False, creep_thick=False, level_surface=False,
                 level_set=False, head_rule=False, beds=None, level_exact=False):
        self.w, self.h = w, h
        # WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17, ruled exactly level by card): RM_FlowKernel
        # levelExactEnabled. Every dug square holds W decilitres (self.W), every limited pond a whole number of dL
        # (bodies[b]["dl"]), and each connected body is solved to ONE surface: northstar/level_water.py is the reference.
        # F stays the whole-notch view (W // U) for the older readers.
        self.level_exact = level_exact
        self.W = {}
        # POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2 (owner 2026-10-16: "It should slosh around until it levels, pond or canal or
        # otherwise."): RM_FlowKernel.sourceDrawdown / HeadAllows. A limited body whose source cells carry beds (cell -> levels)
        # has drawdown s (RM_PondDepthMath.Drawdown over its undug cells' bed histogram); a source gives a dug cell only while
        # D - F >= s + 1 (s = 0 is today's rule). Default off, so every older scene is the pre-pond engine.
        self.head_rule = head_rule
        self.beds = dict(beds or {})
        # RM_FlowKernel creepWaterEnabled (CANAL_FRONT_FIX_WRONG_END_WETS_FIRST, shipped ON as
        # waterFrontCreepEnabled) / creepEnabled (THICK_LIQUID_CREEP_1, thickCreepEnabled): a NON-source donor that
        # RECEIVED a level this pulse cannot pass it on until the next pulse (water uses the water flag, a viscous
        # fluid, stride > 1, the thick flag). Both default False so the offline INT/O6 bounds (n*D brigade) are the
        # pre-creep engine; the LIVE oracles (oracle_for, the live tier, the mock) pass CREEP_LIVE.
        self.creep_water, self.creep_thick = creep_water, creep_thick
        # RM_FlowKernel levelBySurfaceEnabled (WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND, shipped ON): a donor gives when its
        # surface (F - D; a source 0) stands above the recipient's, a drop of 1 only down the flow order. Default False so
        # the older offline bounds stay the pre-surface engine; the LIVE oracles pass CREEP_LIVE, which carries it.
        self.low = {}
        self.level_surface = level_surface and algo == "fixed"   # the "old" engine predates it (fault mock included)
        # RM_FlowKernel levelSetEnabled (WATER_LEVELSET_SOLVE, shipped ON, needs level_surface): each wet region + dry rim is
        # SOLVED to its flat level (_levelset_regions); a drop of exactly 1 between two dug cells no longer moves in _pick.
        self.level_set = level_set and self.level_surface
        # RM_FlowKernel.TopUpWaterMouths (CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME), on with creep_water. False replays the
        # engine before it (the recorded live E2 vectors of 2026-10-12, O11), whose mouth read dry every other pulse.
        self.mouth_top_up = True
        self.ds, self.dk = {}, {}
        self.received = {}                # cell -> pulse_n it last received a level
        # WATER_SURFACE_REPAIR_LEVEL_OR_BUST (owner 2026-10-17, "a level surface"): the WATER creep hold is on the FRONT only,
        # a cell that was DRY when it took its first level this pulse (RM_FlowKernel.frontStamp); thick liquids keep `received`.
        self.front = {}                   # cell -> pulse_n it went from dry to wet
        # claim_sources=True is the pre-FLOWWORKS_SHARED_SOURCE_STALL_1 component walk (a source cell
        # marked in the visited set SHARED across components, so the first-seeded channel claims it).
        # Default: True for algo="old" (as measured 2026-10-01), False for "fixed" (the shipped fix,
        # RM_StockMath.CollectComponent: sources tracked per component only).
        self.claim_sources = (algo == "old") if claim_sources is None else claim_sources
        # recession (RM_LiquidStock.Recede, run before the flow each pulse): a LIMITED body whose
        # bodies[id] carries "cells" and "capacity" sheds active cells down to floor(stock/perCell),
        # picking fewest 8-way source neighbours, then furthest from the integer centroid, then
        # lowest cell index (RM_StockMath.PrefersCandidate). Refill/Restore are NOT modelled
        # (<0.04 level per pulse at the shipped rates; scenes stay far from floor boundaries).
        self.recession = recession
        self.keep_last = True             # recedeKeepsLastCell (shipped default, PROVISIONAL 2026-10-09)
        self.spare_outflow = True         # recedeSparesOutflow (shipped default, PROVISIONAL 2026-10-09)
        self.receded = set()
        # rain (ApplyRain, first thing in DoPulse): accumulator += rate * perPulse; whole levels
        # go into EVERY unroofed, not-full excavated cell on the map (not just one scene).
        self.rain_on, self.rain_rate, self.rain_per, self.rain_acc = False, 0.0, 0.1, 0.0
        self.roofed = set()
        self.D, self.F = {}, {}
        self.src = dict(sources)          # cell -> body id
        self.bodies = bodies              # id -> {"limitless": bool, "stock": float}
        self.per, self.budget, self.sink_band = per, budget, sink_band
        assert algo in ("old", "fixed")
        self.algo = algo                  # "old" = pre-FLOWWORKS_CHANNEL_OSCILLATION_1 engine
        self.drained = 0
        self.credited = 0                 # units sources paid in (limited AND limitless)
        # LIQUID_BODY_FLUID_IDENTITY_1 + viscosity (2026-10-05): cell -> fluid defName for cells a scene filled
        # with a NAMED fluid (absent = water, which every older scene is). A wet cell refuses a different
        # fluid (PickDonor's no-mix filter); a donor of a viscous fluid gives only every Nth pulse
        # (RM_StockMath.FluidMovesThisPulse over the map's scribed pulseCount, mirrored by pulse_n).
        self.fluid = {}
        self.pulse_n = 0
        self.viscosity = True
        self.key = {}                     # fixed algo: cell -> (dSrc, -dSink), this component

    def idx(self, c):
        return c[1] * self.w + c[0]

    def inb(self, c):
        return 0 <= c[0] < self.w and 0 <= c[1] < self.h

    def exc(self, c):
        return self.D.get(c, 0) > 0

    def is_source(self, c):
        return c in self.src and c not in self.receded and not self.exc(c)

    def drawdown(self, c):
        """RM_PondDepthMath.Drawdown for the body behind source c (0 = limitless, no beds, or the rule off)."""
        if not self.head_rule:
            return 0
        bid = self.src[c]
        b = self.bodies[bid]
        if b["limitless"]:
            return 0
        beds = [self.beds[x] for x, i in self.src.items() if i == bid and not self.exc(x) and x in self.beds]
        if not beds:
            return 0
        mx = max(beds)
        h = [0] * (mx + 1)
        for v in beds:
            h[max(v, 0)] += 1
        for l in range(mx - 1, -1, -1):
            h[l] += h[l + 1]
        levels = int(math.floor(b["stock"] + 1e-4)) if b["stock"] > 0 else 0
        s, above = mx, 0
        if mx <= 0 or levels <= 0:
            return s
        while s > 0 and above + h[s] <= levels:
            above += h[s]
            s -= 1
        return s

    def head_allows(self, src, r):
        """RM_FlowKernel.HeadAllows: s = 0 always gives; else D(r) - F(r) >= s + 1."""
        s = self.drawdown(src)
        return s <= 0 or self.D.get(r, 0) - self.F.get(r, 0) >= s + 1

    def can_supply(self, c):
        if not self.budget:
            return True
        b = self.bodies[self.src[c]]
        return b["limitless"] or b["stock"] >= 1

    def is_sink(self, c):
        if self.sink_band is None or not self.exc(c):
            return False
        x, z = c
        return x < self.sink_band or z < self.sink_band or x >= self.w - self.sink_band or z >= self.h - self.sink_band

    def dig(self, c, levels=1):
        self.D[c] = min(4, self.D.get(c, 0) + levels)
        self.F.setdefault(c, 0)
        self.W.setdefault(c, 0)

    def set_fill(self, c, f):
        if not self.exc(c):
            return False
        self.F[c] = max(0, min(f, self.D[c]))
        self.W[c] = self.F[c] * level_water.U
        return True

    def drained_levels(self):
        """What the sinks took, in notch-levels (exact mode counts decilitres; sinkTransferredTotal is in levels)."""
        return self.drained / float(level_water.U) if self.level_exact else float(self.drained)

    def stock_of(self, bid):
        """A limited body's stock in levels, as the live body report prints it (exact mode: its dL truth / U)."""
        b = self.bodies[bid]
        if self.level_exact and "dl" in b:
            return b["dl"] / float(level_water.U)
        return float(b.get("stock") or 0.0)

    def _pick(self, r, dr):
        best, best_score = None, -1
        for dx, dz in CARDINAL:
            n = (r[0] + dx, r[1] + dz)
            if not self.inb(n):
                continue
            src = self.is_source(n)
            if src:
                if not self.can_supply(n) or not self.head_allows(n, r):
                    continue
                dn = fn = 4
            else:
                dn = self.D.get(n, 0)
                if dn == 0:
                    continue
                fn = self.F[n]
            if fn == 0:
                continue
            fl_n = "RM_Fluid_Water" if src else self.fluid.get(n, "RM_Fluid_Water")
            if self.F.get(r, 0) > 0 and self.fluid.get(r, "RM_Fluid_Water") != fl_n:
                continue                                     # no-mix (owner Q3)
            if self.viscosity and not fluid_moves(self.pulse_n, fl_n):
                continue                                     # viscosity: a viscous donor waits its stride
            if not src and self._held(n, fl_n):
                continue                                     # creep: filled THIS pulse, passes nothing on until the next
            if self.level_surface:
                drop = (fn - dn) - (self.F.get(r, 0) - dr)
                if drop < 1 or (drop == 1 and not src and self.level_set):
                    continue
                if not src and (self.key.get(n) is None or self.key.get(r) is None
                                or (drop == 1 and not self._downstream(n, r, dn, dr))):
                    continue
                score = 1000 if src else (fn - dn + 5) * 10 + dn
            else:
                if dr <= dn and fn < dn:
                    continue
                if self.algo == "fixed" and not src and not self._downstream(n, r, dn, dr):
                    continue
                score = 1000 if src else fn * 10 + dn
            if score > best_score:
                best_score, best = score, n
        return best

    def _downstream(self, n, r, dn, dr):
        """FIXED algo's one new gate (mirrors RM_StockMath.MayFlowBetween, wired in PickDonor;
        keys from ComputeFlowOrder/HopsFrom; recipients sorted by CompareDeepestFirst). A non-source donor n
        may give to r only if r is strictly further along the component's flow order: key =
        (hops from a SUPPLYING source, -hops to a sink), then depth. A brimming donor may
        overflow only to a strictly later key; at an equal key only GRAVITY (deeper r) moves.
        A static strict order is acyclic, so no unit can come back: no period-2 shuttle, and
        the result no longer depends on cell-index order."""
        kn, kr = self.key.get(n), self.key.get(r)
        if kn is None or kr is None:
            return False
        if kn < kr:
            return True
        if kn == kr and self.level_surface and self.low.get(n, 0) != self.low.get(r, 0):
            return self.low.get(n, 0) > self.low.get(r, 0)   # third tier: farther from the deepest bed gives to nearer
        return kn == kr and dr > dn

    def _keys(self, comp):
        """Per component: BFS hops from every supplying source (0 if none supply) and to the
        nearest sink cell (0 if none), through excavated cells only."""
        exc = [c for c in comp if self.exc(c)]
        excset = set(exc)

        def bfs(seeds, seeds_excavated):        # mirrors HopsFrom (multi-seed BFS, hop 0 at seeds)
            dist = {c: 0 for c in seeds} if seeds_excavated else {}
            q, i = list(seeds), 0
            while i < len(q):
                c = q[i]
                i += 1
                for dx, dz in CARDINAL:
                    m = (c[0] + dx, c[1] + dz)
                    if m in excset and m not in dist:
                        dist[m] = dist.get(c, 0) + 1
                        q.append(m)
            return dist

        src = [c for c in comp if self.is_source(c) and self.can_supply(c)]
        snk = [c for c in exc if self.is_sink(c)]
        ds = bfs(src, False)
        dk = bfs(snk, True)
        self.key = {c: (ds.get(c, 0), -dk.get(c, 0)) for c in exc}
        self.ds, self.dk = ds, dk
        # levelBySurfaceEnabled: hops to the component's deepest bed (RM_FlowKernel.lowHops).
        deepest = max((self.D[c] for c in exc), default=0)
        self.low = bfs([c for c in exc if self.D[c] == deepest], True) if self.level_surface else {}

    def set_cell(self, c, d, f):
        """Mirror a live cell the oracle did not drive (a pawn job's result)."""
        if d <= 0:
            self.D.pop(c, None)
            self.F.pop(c, None)
        else:
            self.D[c], self.F[c] = d, max(0, min(f, d))
            self.W[c] = self.F[c] * level_water.U

    def _rain(self):
        if not self.rain_on or not any(self.exc(c) for c in self.D) or self.rain_rate <= 0.01:
            return
        self.rain_acc += self.rain_rate * self.rain_per
        levels = 0
        while self.rain_acc >= 1 and levels < 4:
            self.rain_acc -= 1
            levels += 1
        for c in sorted(self.D, key=self.idx):
            if levels and self.exc(c) and self.F[c] < self.D[c] and c not in self.roofed:
                self.F[c] += min(self.D[c] - self.F[c], levels)

    def _recede(self):
        for bid in sorted(self.bodies):
            b = self.bodies[bid]
            cells = b.get("cells")
            if b.get("limitless") or not cells or not b.get("capacity"):
                continue
            per = float(b["capacity"]) / len(cells)
            sup = max(0, int(b["stock"] // per))
            # LIQUID_RECESSION_TOPOLOGY_1 (RM_StockMath.SupportedCellsKeepingLast, setting recedeKeepsLastCell, shipped ON):
            # a body with any stock left keeps its last wet cell, so a pump or channel can still draw the sub-cell residual
            if self.keep_last and sup == 0 and b["stock"] > 0 and per > 0:
                sup = 1
            cx = sum(c[0] for c in cells) // len(cells)
            cz = sum(c[1] for c in cells) // len(cells)
            rec = b.setdefault("receded", [])
            guard = 0
            while len(cells) - len(rec) > sup and guard < 64:
                guard += 1
                best = None
                for c in cells:
                    if not self.is_source(c):
                        continue
                    nb = sum(1 for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx or dz)
                             and self.inb((c[0] + dx, c[1] + dz)) and self.is_source((c[0] + dx, c[1] + dz)))
                    # POND_RECESSION_STRANDS_CHANNEL_1 (setting recedeSparesOutflow, shipped ON): a cell with a dug
                    # CARDINAL neighbour feeds the flow and recedes after every other cell
                    feeds = self.spare_outflow and any(self.inb(n) and self.exc(n) for n in
                                                       ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)))
                    key = (feeds, nb, -((c[0] - cx) ** 2 + (c[1] - cz) ** 2), self.idx(c))
                    if best is None or key < best[0]:
                        best = (key, c)
                if best is None:
                    break
                rec.append(best[1])
                self.receded.add(best[1])

    def pulse(self):
        if self.level_exact:
            level_water.exact_pulse(self)
            return
        self.pulse_n += 1
        self._rain()
        if self.recession:
            self._recede()
        seen = set()
        # Seeds in CELL-INDEX order (z*width+x) - owner ruling 2026-10-06, RM_FlowKernel.Pulse sorts them. It matters
        # only for a LIMITED body that cannot pay every adjacent inlet in one pulse: the lower-index component is
        # paid first, unit by unit, identically in a session and after a load. (Before that ruling this was DIG
        # order; a live run against a DLL older than the ruling will disagree on exactly that case.)
        for seed in sorted(self.D, key=lambda c: (c[1], c[0])):
            if seed in seen or not self.exc(seed):
                continue
            comp, queue, comp_src = [], [seed], set()
            seen.add(seed)
            while queue:
                c = queue.pop(0)
                comp.append(c)
                if self.is_source(c):
                    continue
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if not self.inb(n):
                        continue
                    if self.exc(n):
                        if n not in seen:
                            seen.add(n)
                            queue.append(n)
                    elif self.is_source(n):
                        claimed = seen if self.claim_sources else comp_src
                        if n not in claimed:
                            claimed.add(n)
                            queue.append(n)
            for c in comp:                                   # sinks drain before the flow
                if self.exc(c) and self.is_sink(c):
                    take = min(self.F[c], self.per)
                    self.F[c] -= take
                    self.drained += take
            if self.algo == "fixed":
                self._keys(comp)
                rec = sorted([c for c in comp if self.exc(c) and self.F[c] < self.D[c]],
                             key=lambda c: (-self.D[c], self.key[c], self.idx(c)))
            else:
                rec = sorted([c for c in comp if self.exc(c) and self.F[c] < self.D[c]],
                             key=lambda c: (-self.D[c], self.idx(c)))
            took = set()
            for r in rec:
                moved = 0
                while moved < self.per and self.F[r] < self.D[r]:
                    d = self._pick(r, self.D[r])
                    if d is None:
                        break
                    if self.is_source(d):
                        b = self.bodies[self.src[d]]
                        if self.budget and not b["limitless"]:
                            if b["stock"] < 1:
                                break
                            b["stock"] -= 1
                        self.credited += 1
                    else:
                        self.F[d] -= 1
                    if self.F[r] == 0:                       # first level claims a dry cell for its fluid
                        self.front[r] = self.pulse_n
                        fl = "RM_Fluid_Water" if self.is_source(d) else self.fluid.get(d, "RM_Fluid_Water")
                        if fl == "RM_Fluid_Water":
                            self.fluid.pop(r, None)
                        else:
                            self.fluid[r] = fl
                    self.F[r] += 1
                    self.received[r] = self.pulse_n
                    moved += 1
                if moved:
                    took.add(r)
            if self.level_set:
                self._levelset_regions(comp)
            elif self.level_surface:
                self._level_regions(comp)
            if self.creep_water and self.mouth_top_up:
                self._top_up_mouths(comp, took)
        for c in [c for c in self.fluid if self.F.get(c, 0) == 0]:   # SyncFluidIdentity: F=0 clears the record
            del self.fluid[c]

    def _top_up_mouths(self, comp, took):
        """RM_FlowKernel.TopUpWaterMouths (CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME): after the pass and the solve, a dug
        cell beside a supplying (water) source that took nothing this pulse and has room takes up to `per` from it, in
        cell-index order; otherwise a brim mouth that passed its unit on read dry every other pulse."""
        for r in sorted((c for c in comp if self.exc(c) and self.F[c] < self.D[c] and c not in took), key=self.idx):
            moved = 0
            while moved < self.per and self.F[r] < self.D[r]:
                d = None
                for dx, dz in CARDINAL:
                    n = (r[0] + dx, r[1] + dz)
                    if not self.inb(n) or not self.is_source(n) or not self.can_supply(n) or not self.head_allows(n, r):
                        continue
                    if self.F.get(r, 0) > 0 and self.fluid.get(r, "RM_Fluid_Water") != "RM_Fluid_Water":
                        continue                                 # no-mix: a source pays water only
                    d = n
                    break
                if d is None:
                    break
                b = self.bodies[self.src[d]]
                if self.budget and not b["limitless"]:
                    if b["stock"] < 1:
                        break
                    b["stock"] -= 1
                self.credited += 1
                if self.F[r] == 0:
                    self.fluid.pop(r, None)
                    self.front[r] = self.pulse_n
                self.F[r] += 1
                self.received[r] = self.pulse_n
                moved += 1

    def _held(self, c, fl):
        if viscosity_stride(_ticks_per_tile(fl)) > 1:
            return self.creep_thick and self.received.get(c) == self.pulse_n
        return self.creep_water and self.front.get(c) == self.pulse_n

    def _level_regions(self, comp):
        """RM_FlowKernel.LevelWetRegions (WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND): per connected wet region of one
        fluid (not held by creep), move a unit from the highest surface to the lowest surface among the region and its
        dug rim while they differ by 2+; each cell gives <= per and takes <= per in this pass, never a region cell's
        last unit (so the region stays connected through wet squares). Donor ties: lowest
        index; taker ties: deepest bed, then lowest index. Regions in order of their lowest cell index."""
        per = self.per
        surf = lambda c: self.F[c] - self.D[c]
        flu = lambda c: self.fluid.get(c, "RM_Fluid_Water")
        gave, got, member = {}, {}, set()
        seeds = sorted((c for c in comp if self.exc(c) and self.F[c] > 0), key=self.idx)
        for seed in seeds:
            if seed in member:
                continue
            fl = flu(seed)
            if self._held(seed, fl):
                continue
            region, i = [seed], 0
            member.add(seed)
            while i < len(region):
                c = region[i]
                i += 1
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if n in member or not self.exc(n) or self.F[n] == 0 or flu(n) != fl or self._held(n, fl):
                        continue
                    member.add(n)
                    region.append(n)
            if self.viscosity and not fluid_moves(self.pulse_n, fl):
                continue
            rim = set()
            for c in region:
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if n in member or not self.exc(n) or self.F[n] >= self.D[n] or (self.F[n] > 0 and flu(n) != fl):
                        continue
                    rim.add(n)
            rset = set(region)
            while True:
                donors = [c for c in region if self.F[c] >= 2 and gave.get(c, 0) < per]   # never its last unit here
                takers = [c for c in list(rset) + sorted(rim, key=self.idx)
                          if self.F[c] < self.D[c] and got.get(c, 0) < per]
                if not donors or not takers:
                    break
                d = min(donors, key=lambda c: (-surf(c), self.idx(c)))
                t = min(takers, key=lambda c: (surf(c), -self.D[c], self.idx(c)))
                if surf(d) - surf(t) < 2:
                    break
                self.F[d] -= 1
                if self.F[t] == 0:
                    if fl == "RM_Fluid_Water":
                        self.fluid.pop(t, None)
                    else:
                        self.fluid[t] = fl
                self.F[t] += 1
                gave[d] = gave.get(d, 0) + 1
                got[t] = got.get(t, 0) + 1

    def _ls_key(self, c, drains):
        """RM_FlowKernel.CellKey: the part-filled band's priority (lowest first)."""
        far = 1 << 20
        wet = 0 if self.F.get(c, 0) > 0 and not self._ls_mouth(c) else 1
        if drains:
            return (self.dk.get(c, far), wet, self.idx(c))
        src = 0 if not self.ds else (far - self.ds[c] if c in self.ds else 2 * far)
        return (self.low.get(c, far), wet, src, self.idx(c))

    def _ls_mouth(self, c):
        """RM_FlowKernel.IsLiveMouth: a dug square beside a supplying source never keeps its unit for being wet, so a fed
        D=1 run passes the unit on and the source refills the mouth (CANAL_INLET_DIAGNOSE_FIRST_CELL_ONLY). The kernel also counts
        a pump/drill inlet (externalInput) as a mouth (FLOWWORKS_PUMP_FIX_D1_CANAL_STALLS); this oracle models no drivers, so
        that clause never applies here and the differential scenes (externalInput null) are unchanged."""
        for dx, dz in CARDINAL:
            n = (c[0] + dx, c[1] + dz)
            if self.inb(n) and self.is_source(n) and self.can_supply(n) and self.head_allows(n, c):
                return True
        return False

    def _levelset_regions(self, comp):
        """RM_FlowKernel.LevelSetWetRegions / SolveRegion / Assign / PickBand (WATER_LEVELSET_SOLVE): per wet region of one
        fluid (not held by creep) plus its DRY dug rim, the region's volume is re-laid at its flat level. Band L (the layer
        between surface -L and -L+1) splits the domain into connected pieces of squares dug >= L; bottom up each piece counts
        the water already at or below its band (trapped behind its sill), top down it fills its deeper pieces (in key order)
        before its own band, and a part-filled band is grown best-first by _ls_key from the piece's best square."""
        compset = set(comp)
        flu = lambda c: self.fluid.get(c, "RM_Fluid_Water")
        member = set()
        seeds = sorted((c for c in comp if self.exc(c) and self.F[c] > 0), key=self.idx)
        for seed in seeds:
            if seed in member or self.F[seed] == 0:
                continue
            fl = flu(seed)
            if self._held(seed, fl):
                continue
            region, i = [seed], 0
            member.add(seed)
            while i < len(region):
                c = region[i]
                i += 1
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if n in member or n not in compset or not self.exc(n):
                        continue
                    if self.F[n] == 0:                 # a one-square dry gap joins the wet squares beyond it
                        for ex, ez in CARDINAL:
                            m = (n[0] + ex, n[1] + ez)
                            if m == c or m in member or m not in compset or not self.exc(m) or self.F[m] == 0 \
                                    or flu(m) != fl or self._held(m, fl):
                                continue
                            member.add(m)
                            region.append(m)
                        continue
                    if flu(n) != fl or self._held(n, fl):
                        continue
                    member.add(n)
                    region.append(n)
            if self.viscosity and not fluid_moves(self.pulse_n, fl):
                continue
            domain = list(region)
            dset = set(region)
            for c in region:
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if n in dset or n not in compset or not self.exc(n) or self.F[n] != 0:
                        continue
                    dset.add(n)
                    domain.append(n)
            # FLOWWORKS_SLUICE_FIX_BELOW_SOURCE_LUCK: the region drains only if a sink is reachable from its own domain
            drains = any(c in self.dk for c in domain)
            volume = sum(self.F[c] for c in region)
            maxband = max(self.D[c] for c in domain)
            comps, comp_of = [], {}             # comp: dict(band, cells, children); comp_of[(band, cell)] = comp index
            for band in range(1, maxband + 1):
                for c0 in domain:
                    if self.D[c0] < band or (band, c0) in comp_of:
                        continue
                    k = len(comps)
                    comps.append(dict(band=band, cells=[c0], children=[]))
                    if band > 1:
                        comps[comp_of[(band - 1, c0)]]["children"].append(k)
                    comp_of[(band, c0)] = k
                    j = 0
                    cells = comps[k]["cells"]
                    while j < len(cells):
                        c = cells[j]
                        j += 1
                        for dx, dz in CARDINAL:
                            n = (c[0] + dx, c[1] + dz)
                            if n in dset and self.D[n] >= band and (band, n) not in comp_of:
                                comp_of[(band, n)] = k
                                cells.append(n)
            for k in range(len(comps) - 1, -1, -1):
                cp = comps[k]
                cp["water"] = sum(1 for c in cp["cells"] if self.F[c] > self.D[c] - cp["band"]) + sum(comps[ch]["water"] for ch in cp["children"])
                cp["cap"] = len(cp["cells"]) + sum(comps[ch]["cap"] for ch in cp["children"])
                cp["key"] = min(self._ls_key(c, drains) for c in cp["cells"])
                cp["children"].sort(key=lambda ch: comps[ch]["key"])
            new = {c: 0 for c in domain}

            def pick(cp, r):
                if r >= len(cp["cells"]):
                    return list(cp["cells"])
                band, k = cp["band"], comp_of[(cp["band"], cp["cells"][0])]
                start = min(cp["cells"], key=lambda c: self._ls_key(c, drains))
                frontier, seen, out, deferred = [(self._ls_key(start, drains), start)], {start}, [], []
                fed = not drains and bool(self.ds)
                while len(out) < r and frontier:
                    frontier.sort()
                    _, c = frontier.pop(0)
                    if fed and self._ls_mouth(c):
                        deferred.append(c)   # LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY: a live mouth is passed through, filled last
                    else:
                        out.append(c)
                    for dx, dz in CARDINAL:
                        n = (c[0] + dx, c[1] + dz)
                        if comp_of.get((band, n)) == k and n not in seen:
                            seen.add(n)
                            frontier.append((self._ls_key(n, drains), n))
                return out + deferred[:max(0, r - len(out))]

            def assign(k, amount):
                cp = comps[k]
                free = amount - sum(comps[ch]["water"] for ch in cp["children"])
                laid = 0
                for ch in cp["children"]:
                    give = max(0, min(free, comps[ch]["cap"] - comps[ch]["water"]))
                    free -= give
                    laid += assign(ch, comps[ch]["water"] + give)
                r = max(0, min(free, len(cp["cells"])))
                if r > 0:
                    for c in pick(cp, r):
                        new[c] += 1
                        laid += 1
                return laid

            laid = sum(assign(k, comps[k]["water"]) for k in range(len(comps)) if comps[k]["band"] == 1)
            if laid != volume:
                continue
            for c in domain:
                if new[c] != self.F[c]:
                    if self.F[c] == 0 and new[c] > 0:
                        if fl == "RM_Fluid_Water":
                            self.fluid.pop(c, None)
                        else:
                            self.fluid[c] = fl
                    self.F[c] = new[c]

    def run(self, cells, pulses):
        out = []
        for _ in range(pulses):
            self.pulse()
            out.append([self.W[c] if self.level_exact else self.F[c] for c in cells])
        return out


def rect_cells(x, z, w, h):
    return [(x + i, z + j) for i in range(w) for j in range(h)]


# ============================================================================ the site (R1/R2)
# Absolute cells on a FRESH 250x250 debug quicktest map (live run 2026-10-02: the v1 golden
# TrialSite does not carry these bodies, and every v2 flow scene runs at 0 ticks through
# jawa/flowworks_pulse, so weather/pawns/time cannot reach it). The runner clears and paints
# each body and scene (+2-cell ring) itself; L5 + the per-scene pre-read enforce R2.
# The centre (+-25 of 125,125) is avoided: the quicktest colonists stand there.
def _rm_volume_const(name, default):
    """POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: read a constant from the mod's own RM_Volume.cs so the pond oracle follows
    the yardstick instead of a copy (V2_POND_ROWS_REPAIR_STILL_COUNTS_FIVE). The default is used only if the source is absent."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source", "RM_Volume.cs")
    try:
        with open(src, encoding="utf-8") as f:
            m = re.search(r"public const int %s\s*=\s*(\d+)\s*;" % name, f.read())
        return int(m.group(1)) if m else default
    except OSError:
        return default


# a shallow natural pond square holds ShallowBedLevels notches x volumePerTile (pinned to 1); nothing multiplies it
POND_LEVELS_PER_CELL = _rm_volume_const("ShallowBedLevels", 2)


def pond_capacity(n_cells):
    return float(POND_LEVELS_PER_CELL * n_cells)


BODIES = {
    "W1": dict(cells=rect_cells(0, 60, 16, 4), limitless=True),       # west edge, 64 cells
    "W2": dict(cells=[(60, 150)], limitless=False, capacity=pond_capacity(1)),       # E3 budget (recession OFF)
    "W2R": dict(cells=[(70, 150), (71, 150), (72, 150), (73, 150)], limitless=False, capacity=pond_capacity(4)),   # E3b recession (defaults); 4 cells, capacity 8
    "W3": dict(cells=[(80, 150), (81, 150), (82, 150), (83, 150), (84, 150)], limitless=False, capacity=pond_capacity(5)),   # E4 engine
    "W4": dict(cells=rect_cells(0, 200, 10, 4), limitless=True),      # edge, 40 cells: off-map is limitless however small
    # (LAKE_GROUNDWATER_REFILL_BUILD_WETNESS_CUT, owner card 2026-10-18; the old edge + 50-cell rule only with wetnessCutoffEnabled off)
    "W5": dict(cells=rect_cells(150, 30, 8, 8), limitless=False, capacity=pond_capacity(64)),  # interior 64
    "W6": dict(cells=rect_cells(0, 170, 16, 4), limitless=False, sticky_off=True),
    "W7": dict(cells=rect_cells(0, 180, 16, 4), limitless=True),      # W6's twin, sticky ON
    "W8": dict(cells=rect_cells(0, 220, 16, 4), limitless=True),      # shared-source twin
}


# ============================================================================ the pit-width oracle
# SUPERDEEP_HOLDER_RETIRE_1 (owner Q4, 2026-10-02: "The pit has to be as wide as the creature to hold
# it. Otherwise it gets out."). A Python port of Source/RM_PitTrapMath.cs; the C# SelfTest cases
# PitWidth_* are the authority, O10 re-asserts the item's matrix here so the live predictions use it.
def required_width(body_size, mult=1.0):
    b = body_size * (mult if mult > 0 else 1.0)
    if not b > 0:
        return 1
    return max(1, min(9, int(math.floor(math.sqrt(b) + 0.5))))      # round half AWAY from zero


def pit_width_at(cells, c, w):
    cells = set(cells)
    if c not in cells:
        return False
    return any(all((ox + dx, oz + dz) in cells for dx in range(w) for dz in range(w))
               for ox in range(c[0] - w + 1, c[0] + 1) for oz in range(c[1] - w + 1, c[1] + 1))


def measured_pit_width(cells, c):
    w = 0
    while w < 9 and pit_width_at(cells, c, w + 1):
        w += 1
    return w


def pit_held(cells, c, body_size, ladder=False, captured=True, rule=True, mult=1.0):
    return bool(rule and c in set(cells) and captured and not ladder
                and pit_width_at(cells, c, required_width(body_size, mult)))


def _run(x, z, n, dx, dz):
    return [(x + dx * i, z + dz * i) for i in range(n)]


# phase: the live phase that digs the scene. oracle=False: a pawn job owns the cell (E7/E8),
# so the global oracle never drives it (it is mirrored from a live read before the rain phase).
SCENES = {
    # S-tier, zero ticks (phase S)
    "S1_ladder": dict(cells=[(130, 60), (132, 60), (134, 60), (136, 60)], phase="S"),
    "S2_clamp": dict(cells=[(130, 64), (132, 64)], phase="S"),
    "S4_band": dict(cells=[(130, 9), (130, 11)], sink=True, phase="S"),
    # E2: channel fill vs oracle, every compass direction (phase A)
    "E2_east_A": dict(cells=_run(16, 60, 4, 1, 0), D=1, body="W1", dir="E", phase="A"),
    "E2_east_B": dict(cells=_run(16, 63, 4, 1, 0), D=1, body="W1", dir="E", phase="A"),   # twin of A
    "E2_north": dict(cells=_run(12, 64, 4, 0, 1), D=1, body="W1", dir="N", phase="A"),
    "E2_south": dict(cells=_run(12, 59, 4, 0, -1), D=1, body="W1", dir="S", phase="A"),
    "E2_west": dict(cells=_run(149, 33, 4, -1, 0), D=1, body="W5", dir="W", phase="A"),
    # E2s: TWO channels off ONE source cell (a body corner); both must fill. Until
    # FLOWWORKS_SHARED_SOURCE_STALL_1's fix the first-dug claimed the source and the second stalled
    # at its inlet. The W8 pair is dug in the opposite compass order, so a pass/fail cannot be a
    # direction effect.
    "E2s_shared_E7": dict(cells=_run(16, 183, 4, 1, 0), D=1, body="W7", dir="E", phase="A"),
    "E2s_shared_N7": dict(cells=_run(15, 184, 4, 0, 1), D=1, body="W7", dir="N", phase="A"),
    "E2s_shared_N8": dict(cells=_run(15, 224, 4, 0, 1), D=1, body="W8", dir="N", phase="A"),
    "E2s_shared_E8": dict(cells=_run(16, 223, 4, 1, 0), D=1, body="W8", dir="E", phase="A"),
    # E3b: the 4-cell W2R pond at SHIPPED recession (keep-last-cell) fills the 4-cell run, then sheds two cells (phase A)
    "E3b_recede": dict(cells=_run(70, 149, 4, 0, -1), D=1, body="W2R", dir="S", phase="A"),
    # E5: a prefilled sourceless run crossing into the sink band, and its interior twin (phase A)
    "E5_sink": dict(cells=_run(200, 14, 10, 0, -1), D=1, fill=1, sink=True, phase="A"),
    "E5_inner": dict(cells=_run(210, 29, 10, 0, -1), D=1, fill=1, phase="A"),
    # E3: the cap-5 budget with recession OFF, then the budget-OFF tail (phase B)
    "E3_budget": dict(cells=_run(60, 149, 8, 0, -1), D=1, body="W2", dir="S", phase="B"),
    # E5 toggle: sinks OFF for 2 pulses, then ON (phase C)
    "E5_sink_off": dict(cells=_run(220, 14, 10, 0, -1), D=1, fill=1, sink=True, phase="C"),
    # determinism: a later-dug copy of E2_east_A off W7, compared pulse-for-pulse (phase R)
    "E2_rerun": dict(cells=_run(16, 181, 4, 1, 0), D=1, body="W7", dir="E", phase="R"),
    # E4: engine OFF/ON under the REAL scheduler, during the job ticks (phase J). D=2 (was 1): under exact-level water a
    # D=1 run off the limited 5-square W3 pond levels at 0.56 notch and never shows a whole notch, so "the scheduled pulses
    # moved water" could not be read in F; dug 1 m the run sits in the pond's bottom band and reads F=1 (10 notch-squares
    # over 9 squares of band 2 plus 9 of band 1)
    "E4_engine": dict(cells=_run(80, 149, 4, 0, -1), D=2, body="W3", dir="S", phase="J"),
    # E7/E8: pawn jobs (phase J). E7a: room to displace into; E7b: none -> sanctioned overflow
    "E7a_fillin": dict(cells=[(190, 60), (191, 60), (192, 60)], D=1, fill=[0, 1, 1], phase="J", oracle=False),
    "E7b_overflow": dict(cells=[(195, 60), (196, 60), (197, 60)], D=1, fill=[1, 1, 1], phase="J", oracle=False),
    "E8_dig": dict(cells=[(200, 60)], D=0, phase="J", oracle=False),
    # E6: rain, the LAST mutating phase (rain lands map-wide)
    "E6_open": dict(cells=[(180, 60)], D=1, phase="J"),
    "E6_roofed": dict(cells=[(182, 60)], D=1, roof=(181, 59, 3, 3), phase="J"),
    # P: pits as GRID facts (SUPERDEEP_HOLDER_RETIRE_1), after rain, before the tail. D=4, dry.
    # The width matrix {small, large} x {1x1, 1x5 trench, 2x2}; expected held {T,T,T ; F,F,T}.
    "P_1x1_small": dict(cells=[(130, 100)], D=4, phase="P"),
    "P_1x1_large": dict(cells=[(136, 100)], D=4, phase="P"),
    "P_trench_small": dict(cells=_run(142, 98, 5, 0, 1), D=4, phase="P"),
    "P_trench_large": dict(cells=_run(148, 98, 5, 0, 1), D=4, phase="P"),
    "P_2x2_small": dict(cells=[(154, 100), (155, 100), (154, 101), (155, 101)], D=4, phase="P"),
    "P_2x2_large": dict(cells=[(160, 100), (161, 100), (160, 101), (161, 101)], D=4, phase="P"),
    # walk-in (own-faction capture ON), then a ladder; and the carve-out-OFF control twin
    "P_walk": dict(cells=[(166, 100)], D=4, phase="P"),
    "P_walk_ctrl": dict(cells=[(172, 100)], D=4, phase="P"),
    # X: the promoted bars (2026-10-05), after P, before the tail. Dug D=1 here; phase_X deepens the strip
    # to 1..4 and the race staircases likewise. No body: nothing here is fed, every move is gravity.
    "X_strip": dict(cells=_run(131, 70, 4, 1, 0), D=1, phase="X"),               # D 1,2,3,4; (130,70) is D=0
    "X_two": dict(cells=_run(131, 74, 4, 1, 0) + [(134, 75)] + _run(131, 76, 4, 1, 0), D=1, phase="X"),
    "X_race_tar": dict(cells=_run(131, 79, 4, 1, 0), D=1, phase="X"),
    "X_race_water": dict(cells=_run(131, 82, 4, 1, 0), D=1, phase="X"),
    "X_race_off": dict(cells=_run(131, 85, 4, 1, 0), D=1, phase="X"),
    "X_cover": dict(cells=[(140, 70), (141, 70), (140, 71), (141, 71)], D=4, phase="X"),
    "X_fire": dict(cells=_run(131, 88, 6, 1, 0), D=1, phase="X"),                 # X10: tar run, lit at (136,88)
}
X_WALK = (130, 70)                 # the strip's D=0 end: colonist spawn, hare 0
X_JUNCTION = (134, 75)             # X_two: one dry D=2 cell between the tar row (z74) and the water row (z76)
PAWN_SPOTS = {"E7a_fillin": (191, 62), "E7b_overflow": (196, 62), "E8_dig": (200, 62)}
# P-phase pawns: (scene, the pawn's cell, kind, faction, "small"/"large")
PIT_MATRIX = [("P_1x1_small", (130, 100), "small"), ("P_1x1_large", (136, 100), "large"),
              ("P_trench_small", (142, 100), "small"), ("P_trench_large", (148, 100), "large"),
              ("P_2x2_small", (154, 100), "small"), ("P_2x2_large", (160, 100), "large")]
PIT_KINDS = {"small": "Hare", "large": "Muffalo"}      # wild (faction none): captured; Muffalo adult 2.4 -> W=2
PIT_EXPECT = {"P_1x1_small": True, "P_trench_small": True, "P_2x2_small": True,
              "P_1x1_large": False, "P_trench_large": False, "P_2x2_large": True}
PIT_SPOTS = {"P_walk": (166, 103), "P_walk_ctrl": (172, 103),     # colonists start 3 cells off the pit
             "P_forced": (166, 103)}                            # P3f's colonist: P_walk's spot, launched into its pit
FLYER_LAND_TICKS = 180             # a 3-cell vanilla PawnFlyer hop lands well inside this (PROVISIONAL, first live run)
# Live run 2026-10-02 14:40: waitTicks 300 was too short to ENTER a D=4 cell (RM_Channel_Superdeep pathCost
# 300 -> one step costs ~300+ ticks): the walk-in read "arrived False" though the pawn got there later.
PIT_WAIT_IN, PIT_WAIT_OUT = 1200, 600


def edge_distance(c):
    return min(c[0], c[1], MAP_W - 1 - c[0], MAP_H - 1 - c[1])


def body_stock0(b):
    return 0.0 if b["limitless"] else float(b.get("capacity", pond_capacity(len(b["cells"]))))


def site_beds():
    """The bed of every painted body square, in notches: WaterShallow = RM_Volume.ShallowBedLevels. True only because
    the site pins deepBedsEnabled OFF (phase_site): with it on, P11 records a lake floor (no shore shelf by default since 2026-10-18) for a pond painted mid-game, and these squares no longer hold what the scenes were laid out for."""
    return {c: POND_LEVELS_PER_CELL for b in BODIES.values() for c in b["cells"]}


def oracle_for(scene_key, pulses, recession=False, exact=LIVE_EXACT):
    """Predicted F vectors for one channel scene in isolation (per pulse). exact: the shipped exact-level engine
    (levelExactEnabled); False = the whole-notch engine before WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES."""
    s = SCENES[scene_key]
    body = BODIES[s["body"]]
    stock = body_stock0(body)
    o = PulseOracle(MAP_W, MAP_H, {c: 0 for c in body["cells"]},
                    {0: {"limitless": body["limitless"], "stock": stock, "capacity": stock,
                         "cells": list(body["cells"])}}, sink_band=SINK_BAND, recession=recession,
                    level_exact=exact, beds=site_beds() if exact else None, **CREEP_LIVE)
    for c in s["cells"]:
        o.dig(c, s["D"])
    out = []
    for _ in range(pulses):
        o.pulse()
        out.append([o.F[c] for c in s["cells"]])
    return out


# ============================================================================ tier O (offline)
class Check(object):
    def __init__(self, cid, ok, detail=""):
        self.cid, self.ok, self.detail = cid, ok, detail

    def __repr__(self):
        return "%-4s %-6s %s" % (self.cid, "PASS" if self.ok else "FAIL", self.detail)


def _xml_blocks():
    out = {}
    for root, _, files in os.walk(DEFS):
        for fn in files:
            if fn.endswith(".xml"):
                t = open(os.path.join(root, fn), encoding="utf-8").read()
                for m in re.finditer(r"<([\w.]+)(\s[^>]*)?>\s*(?:<!--.*?-->\s*)*<defName>([^<]+)</defName>(.*?)</\1>", t, re.S):
                    out[m.group(3)] = (m.group(1), m.group(2) or "", m.group(4), fn)
    return out


def _field(block, name):
    m = re.search(r"<%s>(.*?)</%s>" % (name, name), block, re.S)
    return m.group(1).strip() if m else None


VANILLA_PATHCOST = {"WaterShallow": 30}     # RimSage, Core TerrainDef WaterShallow, 2026-10-03


def _path_cost(defs, name, depth=0):
    b = defs.get(name)
    if b is None:
        return VANILLA_PATHCOST.get(name)
    pc = _field(b[2], "pathCost")
    if pc is not None:
        return float(pc)
    m = re.search(r'ParentName="([^"]+)"', b[1])
    return _path_cost(defs, m.group(1), depth + 1) if m and depth < 8 else None


def _fill_tier(f, d):                       # mirrors RM_ExcavationDepth.FillTier: by metres of water, not by fullness
    return 0 if f <= 0 else min(5, 1 + int(f))   # 2 ~0.5 m, 3 ~1 m, 4 ~1.5 m, 5 = 2 m+


def fill_cost_findings(defs):
    """DEPTH_FILL_COST_MATRIX_1 / ruling [E]: at every depth 1-3, every reachable fill (F = 1..D, look by
    FillTier = metres of water, terrain by FluidDef.FillTerrainForLook) costs strictly more to cross than the same depth dry.
    Named regression: RM_Fill_Water_Half 42 < RM_Channel_Mid 45 (D=2, F=1)."""
    dry = {1: "RM_Channel_Empty", 2: "RM_Channel_Mid", 3: "RM_Channel_Deep"}
    probs, n = [], 0
    for name, b in sorted(defs.items()):
        if not b[0].endswith("FluidDef"):
            continue
        tiers = {2: _field(b[2], "floodTerrain"), 3: _field(b[2], "fillTerrainHalf") or _field(b[2], "floodTerrain"),
                 4: _field(b[2], "fillTerrainBrim") or _field(b[2], "fillTerrainHalf") or _field(b[2], "floodTerrain")}
        for d, dn in dry.items():
            dc = _path_cost(defs, dn)
            for f in range(1, d + 1):
                t = tiers[_fill_tier(f, d)]
                c = _path_cost(defs, t) if t else None
                n += 1
                if c is None or dc is None:
                    probs.append("%s D%d F%d: cost unresolved (%s=%r, %s=%r)" % (name, d, f, t, c, dn, dc))
                elif not c > dc:
                    probs.append("%s D%d F%d: %s %g <= dry %s %g" % (name, d, f, t, c, dn, dc))
    if n < 12:
        probs.append("fill-cost census blind: %d (fluid, D, F) rows" % n)
    return probs


def o1_defs(defs=None):
    defs = _xml_blocks() if defs is None else defs
    probs = []
    if "RM_Channel_Empty" not in defs:            # sanity probe: the parser can find a known def
        return Check("O1", False, "parser blind: RM_Channel_Empty not found (%d defs)" % len(defs))
    w = defs.get("RM_Fluid_Water")
    if not w:
        probs.append("RM_Fluid_Water missing")
    else:
        for f, want in (("floodTerrain", "RM_Fill_Water_Trace"), ("volumePerTile", "1"), ("ticksPerTile", "60")):
            if _field(w[2], f) != want:
                probs.append("RM_Fluid_Water.%s=%r want %r" % (f, _field(w[2], f), want))
        # POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: the 5:1 field is gone (a pond square holds its own bed depth)
        if _field(w[2], "canalCellsPerSourceCell") is not None:
            probs.append("RM_Fluid_Water still sets the deleted canalCellsPerSourceCell")
    for name, cost in (("RM_Channel_Empty", "30"), ("RM_Channel_Mid", "45"),
                       ("RM_Channel_Deep", "80"), ("RM_Channel_Superdeep", "300")):
        b = defs.get(name)
        if not b or _field(b[2], "pathCost") != cost:
            probs.append("%s pathCost %r want %s" % (name, b and _field(b[2], "pathCost"), cost))
    # SUPERDEEP_HOLDER_RETIRE_1 INVERTED this row: it was "RM_SuperdeepPit drawerType None (the
    # holder must be invisible)". The holder is retired; a pit is a D=4 cell. RULED OUT, kept as a
    # guard: "a pit needs a Thing to hold a pawn" -- the grid trap rule holds a SPAWNED pawn (P rows).
    raw = "\n".join(open(os.path.join(r, f), encoding="utf-8").read() for r, _, fs in os.walk(DEFS)
                    for f in fs if f.endswith(".xml"))      # abstracts carry Name="", not <defName>
    alive = [n for n in RETIRED_PIT_DEFS if n in defs or ('Name="%s"' % n) in raw]
    if alive:
        probs.append("retired pit defs still defined: %s" % alive)
    spike = sorted(n for n, b in defs.items() if "Things/Building/Security/TrapSpikeArmed" in b[2])
    if spike:
        probs.append("defs on the vanilla TrapSpikeArmed art: %s" % spike)
    if "RM_Channel_Superdeep" not in defs:
        probs.append("sanity probe: RM_Channel_Superdeep (the pit's own terrain) not found")
    lad = defs.get("RM_Ladder")
    if not lad or "PlaceWorker_LadderOnExcavation" not in lad[2]:
        probs.append("RM_Ladder lacks PlaceWorker_LadderOnExcavation")
    for n in ("RM_DigCanal", "RM_FillInCanal", "RM_DigCanalJob", "RM_DigCanalWorkGiver",
              "RM_Fluid_Tar", "RM_Fluid_SlimeGreen", "RM_Ladder"):
        if n not in defs:
            probs.append("missing def " + n)
    probs += fill_cost_findings(defs)
    return Check("O1", not probs, "; ".join(probs) or "%d defs parsed" % len(defs))


def _class_body(text, cls):
    """The brace-matched body of `class <cls>` in a C# source, or None when it is not declared there."""
    m = re.search(r"\bclass %s\b[^{;]*\{" % re.escape(cls), text)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[m.end():i - 1]


TOGGLE_CENSUS_FLOOR = 90            # sanity probe: the C# census must SEE the toggles (111 bools in 6 classes, 2026-10-11)


def settings_census(spec=None):
    """C# census of every boolean Mod Settings field: {type: {field: (initialiser, Scribe default)}} over each
    settings class site_spec.SETTINGS_SOURCES names, read from the class body itself (not a table). Returns
    (census, problems); census is None when it could not be taken (site_spec unimportable, a class unreadable,
    or fewer than TOGGLE_CENSUS_FLOOR toggles seen) -- the caller reports that as unmeasured, never as a pass."""
    try:
        spec = spec or _load_site_spec()
        sources = spec.SETTINGS_SOURCES
    except Exception as ex:                                   # noqa: BLE001
        return None, ["site_spec unavailable: %s" % ex]
    census, probs = {}, []
    for typ, rel in sorted(sources.items()):
        try:
            text = open(os.path.join(SRC, rel), encoding="utf-8").read()
        except OSError as ex:
            probs.append("%s: source unreadable (%s)" % (typ, ex))
            continue
        body = _class_body(text, typ.rsplit(".", 1)[1])
        if body is None:
            probs.append("%s: class not found in %s" % (typ, rel))
            continue
        inits = dict(re.findall(r"public static bool (\w+)\s*=\s*(true|false)\s*;", body))
        scribe = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "[^"]+", (true|false)\)', body))
        if not inits:
            probs.append("%s: census saw 0 toggles (blind?)" % typ)
        census[typ] = {f: (v == "true", None if f not in scribe else scribe[f] == "true") for f, v in inits.items()}
    n = sum(len(v) for v in census.values())
    if probs or n < TOGGLE_CENSUS_FLOOR:
        return None, probs + (["census saw only %d toggles (floor %d)" % (n, TOGGLE_CENSUS_FLOOR)]
                              if n < TOGGLE_CENSUS_FLOOR else [])
    return census, []


def settings_table_gap(table, census):
    """Toggles the C# declares that a settings table (site_spec.SETTINGS shape) does not list, and vice versa."""
    gap = []
    for typ, fields in census.items():
        listed = {f for f, v in (table.get(typ) or {}).items() if isinstance(v, bool)}
        gap += ["%s missing from the table" % f for f in sorted(set(fields) - listed)]
        gap += ["%s listed but not declared in C#" % f for f in sorted(listed - set(fields))]
    return gap


def o2_settings_defaults(spec=None):
    """Every boolean Mod Settings field the C# declares (census of the six settings classes) is in
    site_spec.SETTINGS with the same default, and its initialiser and Scribe default agree; the toggles
    this script's scenes rely on (BOOL_DEFAULTS) agree with that census; FLOAT_DEFAULTS match the C#."""
    probs = []
    try:
        spec = spec or _load_site_spec()
    except Exception as ex:                                   # noqa: BLE001
        return Check("O2", False, "UNMEASURED: site_spec unavailable (%s)" % ex)
    census, cprobs = settings_census(spec)
    if census is None:
        return Check("O2", False, "UNMEASURED: C# toggle census not taken: %s" % "; ".join(cprobs))
    probs += settings_table_gap(spec.SETTINGS, census)
    for typ, fields in sorted(census.items()):
        for f, (init, scribe) in sorted(fields.items()):
            if scribe is None:
                probs.append("%s: no Scribe_Values.Look with a bool default" % f)
            elif init != scribe:
                probs.append("%s: initialiser %s != Scribe default %s" % (f, init, scribe))
            want = (spec.SETTINGS.get(typ) or {}).get(f)
            if isinstance(want, bool) and want != init:
                probs.append("%s: C# %s, site_spec %s" % (f, init, want))
    for typ, fields in BOOL_DEFAULTS.items():
        for f, want in fields.items():
            got = (census.get(typ) or {}).get(f)
            if got is None or got[0] != want:
                probs.append("%s: C# %s want %s (BOOL_DEFAULTS)" % (f, got and got[0], want))
    allsrc = _src_all()
    for f, want in FLOAT_DEFAULTS.items():
        # pitRampMaxSpan (8100177f21) is an int setting: same table, no "f" suffix
        m1 = re.search(r"public static (?:float %s\s*=\s*([\d.]+)f|int %s\s*=\s*(\d+))\s*;" % (f, f), allsrc)
        if m1:
            m1 = (m1.group(1) or m1.group(2), )
        if not m1 or float(m1[0]) != want:
            probs.append("%s=%s want %s" % (f, m1 and m1[0], want))
    # PIT_LEGACY_CODE_RETIRE_1 northstar: one settings screen; no struggle/escape/exposure toggle survives
    mods = re.findall(r"class \w+ : Mod\b", allsrc)
    if len(mods) != 2:              # RimMandrakeFlowWorksMod + RiverSteamMod (PitsMod retired)
        probs.append("Mod subclasses %s (want 2: FlowWorks + RiverSteam)" % mods)
    dead = re.findall(r"public static \w+ (\w*(?:struggle|escape|Escape|Struggle|pitCellExposure)\w*)\s*=", allsrc)
    if re.search(r"public static bool channelConfinementEnabled\b", allsrc):
        dead.append("channelConfinementEnabled")
    if dead:
        probs.append("retired settings still declared: %s" % dead)
    n = sum(len(v) for v in census.values())
    return Check("O2", not probs, "; ".join(probs)[:900] or "%d toggles in %d settings classes (C# census) == site_spec, "
                 "initialiser == Scribe default; %d scene-relied toggles + %d floats match C#; 2 Mod screens; no "
                 "struggle/escape/exposure setting" % (n, len(census), sum(len(v) for v in BOOL_DEFAULTS.values()),
                                                      len(FLOAT_DEFAULTS)))


# UNBUILT register (R9): bar -> (source fact that keeps it UNBUILT, predicate over sources).
def _src_all():
    out = []
    for root, _, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".cs"):
                out.append(open(os.path.join(root, fn), encoding="utf-8").read())
    return "\n".join(out)


UNBUILT = {}
# PROMOTED 2026-10-05 (belt_flowworksC): every bar the register held had a landed feature except viscosity, which
# was then built (RM_StockMath.FluidMovesThisPulse). Each bar is now a LIVE row reading the running game through
# RM_PromotionProofs (static_call); O3 asserts each row still exists, so a bar cannot silently fall out of the run.
PROMOTED = {
    "pawn_height_ladder_legible": "X1_pawn_height_ladder",     # PIT_DEPTH_DRAW_OFFSET_1
    "pawn_lowers_on_deeper_cell": "X2_pawn_lowers_walking_in",
    "pawn_rises_on_shallower_cell": "X3_pawn_rises_walking_out",
    "pit_trapped_reads_as_trapped": "X4_pit_wall_over_head",
    "slime_occupant_below_surface": "X5_slime_occupant_below_surface",
    "fill_fluid_distinct": "X6_two_fluids_distinct",          # LIQUID_BODY_FLUID_IDENTITY_1
    "tar_fill_front_lags_water": "X7_tar_front_lags_water",   # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity
    "pit_covered_invisible": "X8_cover_hides_pit",            # PIT_COVER_FALL_REWIRE_1
    "pit_covered_seam_at_max_zoom": "X9_cover_deck_uniform",
    "ladder_state_legible": "P4b_ladder_raised_strands",      # LADDER_PRISON_DOOR_1
    "canal_burning_reads_as_burning_liquid": "X10_canal_fire",  # Phase 6 fire, promoted from extensions 2026-10-05
    "canal_fire_persists": "X10_canal_fire",
    "canal_spent_after_burn": "X10_canal_fire",
}


_DECLARED = []


def o3_unbuilt_register(emitted=None):
    """Every PROMOTED bar's row is EMITTED by a clean --mock run of the live tier (declared_rows), not merely
    named somewhere in this file; no bar is both promoted and UNBUILT; a landed UNBUILT feature is reported."""
    landed = []
    if UNBUILT:
        s, d = _src_all(), _xml_blocks()
        landed = [bar for bar, (_, pred) in UNBUILT.items() if not pred(s, d)]
    if emitted is None:
        try:
            if not _DECLARED:
                _DECLARED.extend(declared_rows())
            emitted = set(_DECLARED)
        except Exception as ex:                               # noqa: BLE001
            return Check("O3", False, "UNMEASURED: the clean mock run that enumerates live rows crashed: %r" % ex)
    if len(emitted) < 30:                                     # sanity probe: 61 rows on 2026-10-11
        return Check("O3", False, "UNMEASURED: mock run emitted only %d rows (blind?)" % len(emitted))
    lost = [b for b, row in PROMOTED.items() if row not in emitted]
    both = sorted(set(PROMOTED) & set(UNBUILT))
    # A landed feature is a PROMOTION (stage the bar now), reported, not a failure of the mod.
    return Check("O3", not lost and not both, ("promoted bars whose row a clean mock run never emits: %s; " % lost if lost else "")
                 + ("bars both promoted and UNBUILT: %s; " % both if both else "")
                 + "%d UNBUILT bars registered; FEATURE LANDED, stage now: %s; %d promoted to live rows"
                 % (len(UNBUILT) - len(landed), landed or "none", len(PROMOTED)))   # each promoted row seen emitted


WETNESS_CUTOFF_MIN_CELLS = 600     # RM_StockMath.WetnessCutoffCells at rainfall >= 1500 mm: the smallest cutoff any tile has


def o4_geometry(bodies=None, scenes=None):
    """R1/R2 over the live layout: in bounds, edge rules, disjoint, no unintended contact."""
    bodies = BODIES if bodies is None else bodies
    scenes = SCENES if scenes is None else scenes
    probs, owner = [], {}
    bcell = {}
    for name, b in bodies.items():
        for c in b["cells"]:
            owner.setdefault(c, []).append(name)
            bcell[c] = name
        edge = any(edge_distance(c) == 0 for c in b["cells"])
        # wetness-cutoff rule (RM_StockMath.IsLimitlessByWetness): edge always; inland only at >= the tile's cutoff, never
        # under 600 cells (the wettest anchor), so every inland body here is limited
        big = len(b["cells"]) >= WETNESS_CUTOFF_MIN_CELLS
        want = (edge or big) and not b.get("sticky_off")
        if b["limitless"] != want:
            probs.append("%s declared limitless=%s but edge=%s cells=%d sticky_off=%s" % (
                name, b["limitless"], edge, len(b["cells"]), bool(b.get("sticky_off"))))
    for name, s in scenes.items():
        for c in s["cells"]:
            if not (0 <= c[0] < MAP_W and 0 <= c[1] < MAP_H):
                probs.append("%s cell %s out of bounds" % (name, c))
            owner.setdefault(c, []).append(name)
            if edge_distance(c) < SINK_BAND and not s.get("sink"):
                probs.append("%s cell %s in the sink band but not declared a sink scene" % (name, c))
            for dx, dz in CARDINAL:                       # contact with a body = a source
                m = bcell.get((c[0] + dx, c[1] + dz))
                if m and (m != s.get("body") or c != s["cells"][0]):
                    probs.append("%s cell %s touches body %s (declared %s, inlet %s)" % (name, c, m, s.get("body"), s["cells"][0]))
        if s.get("body") and not any((s["cells"][0][0] + dx, s["cells"][0][1] + dz) in bcell for dx, dz in CARDINAL):
            probs.append("%s inlet %s touches no body" % (name, s["cells"][0]))
    for name, spot in PAWN_SPOTS.items():
        if spot in owner:
            probs.append("pawn spot for %s at %s is owned by %s" % (name, spot, owner[spot]))
    dup = {c: o for c, o in owner.items() if len(o) > 1}
    if dup:
        probs.append("cells shared by scenes/bodies: %s" % list(dup.items())[:4])
    allc = {c: n for n, s in scenes.items() for c in s["cells"]}
    for n, s in scenes.items():
        for c in s["cells"]:
            for dx, dz in CARDINAL:
                m = allc.get((c[0] + dx, c[1] + dz))
                if m and m != n:
                    probs.append("%s touches %s at %s" % (n, m, c))
    return Check("O4", not probs, "; ".join(sorted(set(probs)))[:600] or
                 "%d scenes, %d bodies, all in bounds and disjoint" % (len(scenes), len(bodies)))


def o5_oracle_selftest():
    probs = []
    # (1) the live reproduction (INT section 2) -- plot D geometry, 2026-10-01 run
    px, pz = 167, 204
    o = PulseOracle(250, 250, {c: 0 for c in rect_cells(px, pz, 5, 5)},
                    {0: {"limitless": False, "stock": 125.0}}, algo="old")
    cells = _run(px + 5, pz + 2, 12, 1, 0)
    for c in cells:
        o.dig(c, 3)
    hist = [tuple(v) for v in o.run(cells, 60)]
    live = [(3, 3, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3), (3, 3, 3, 2, 2, 3, 3, 2, 2, 3, 3, 2)]
    if not all(v in hist[-10:] for v in live):
        probs.append("oracle no longer reproduces the measured live oscillation")
    # (2) hand-worked: 3-cell east channel off a limitless source oscillates, south fills
    def chan(dx, dz, n=3, p=12):
        oo = PulseOracle(100, 100, {(50, 50): 0}, {0: {"limitless": True, "stock": 0}}, algo="old")
        cs = _run(50 + dx, 50 + dz, n, dx, dz)
        for c in cs:
            oo.dig(c)
        return oo.run(cs, p)
    e, s = chan(1, 0), chan(0, -1)
    if e[-2:] != [[1, 0, 1], [1, 1, 0]] and e[-2:] != [[1, 1, 0], [1, 0, 1]]:
        probs.append("east 3-cell: %s (hand-worked: period-2 [1,0,1]<->[1,1,0])" % e[-2:])
    if s[-1] != [1, 1, 1]:
        probs.append("south 3-cell final %s want [1,1,1]" % s[-1])
    # (4) budget: W2 (its capacity) -> E3 channel receives exactly that many levels and no more. The VECTOR does
    # not come to rest: a partly filled equal-depth run keeps shuttling units (period 2) after
    # the source is spent -- the same OVERFLOW-clause behaviour as the east/north oscillation
    # (INT section 2). So the check is on the SUM, and E3 asserts the exact oracle vector.
    v = oracle_for("E3_budget", 14, exact=False)
    want = int(BODIES["W2"]["capacity"])
    if any(sum(row) != want for row in v[-4:]):
        probs.append("E3 budget (notch engine): last sums %s (want %d)" % ([sum(r) for r in v[-4:]], want))
    # (5) the same budget through the shipped exact engine: the pond's decilitres plus the run's are its capacity, always
    o, _ = _exact_scene("E3_budget", 14)
    tot = level_water.pond_dl(o, 0) + sum(o.W[c] for c in SCENES["E3_budget"]["cells"])
    if tot != int(want * level_water.U):
        probs.append("E3 budget (exact): pond + run %d dL != capacity %d dL" % (tot, want * level_water.U))
    return Check("O5", not probs, "; ".join(probs) or "live oscillation reproduced; hand cases; budget = W2 capacity "
                 "(notch engine: in the run; exact: pond + run to the dL)")


DIRS = {"E": (1, 0), "N": (0, 1), "W": (-1, 0), "S": (0, -1)}   # E/N: cell index rises away
O6_LENGTHS = (3, 4, 6, 12)


def _o6_channel(algo, d, n, depth=1, pulses=None, limitless=True, stock=0.0, src_cells=None):
    """A depth-`depth` channel of n cells running direction d off a source; returns (oracle, cells, hist)."""
    dx, dz = DIRS[d]
    src = src_cells or [(100, 100)]
    o = PulseOracle(200, 200, {c: 0 for c in src}, {0: {"limitless": limitless, "stock": stock}}, algo=algo)
    x0, z0 = src[0]
    cs = _run(x0 + dx, z0 + dz, n, dx, dz)
    for c in cs:
        o.dig(c, depth)
    return o, cs, o.run(cs, pulses if pulses is not None else 4 * n * depth + 8)


def o6_fill_bound(n, depth):
    """Stated convergence bound (pulses) for an n-cell, depth-D straight channel off one source
    at FlowPerPulse 1. The mouth admits <= 1 level per pulse, so n*D pulses is also the LOWER
    bound; the fixed engine meets it exactly (the brigade carries each level to the far end in
    the pulse it enters). Measured 2026-10-02: n=3,4,6,12 x D=1,3, every direction, = n*D."""
    return n * depth


def _is_fixed_point(o):
    before = dict(o.F)
    stock = [b["stock"] for b in o.bodies.values()]
    o.pulse()
    same = o.F == before and stock == [b["stock"] for b in o.bodies.values()]
    return same


def o6_channel_directions():
    """FLOWWORKS_CHANNEL_OSCILLATION_1 (INT section 2). OLD algo: east/north oscillate, west/south
    fill, and the live 2026-10-01 vectors reproduce. FIXED algo: all four directions fill, with
    IDENTICAL per-pulse vectors (no cell-index dependence), within o6_fill_bound, conserving stock,
    and a partly filled / spent / sink-draining run comes to rest (fixed point)."""
    probs, notes = [], []
    # --- OLD: the defect, as measured
    for n in O6_LENGTHS:
        for d in "ENWS":
            _, cs, h = _o6_channel("old", d, n)
            full = h[-1] == [1] * n
            if d in "EN":
                if full or h[-1] != h[-3] or h[-1] == h[-2]:
                    probs.append("old %s%d should oscillate period 2: %s" % (d, n, h[-2:]))
            elif not full:
                probs.append("old %s%d should fill: %s" % (d, n, h[-1]))
    _, _, h = _o6_channel("old", "E", 3)
    if sorted(map(tuple, h[-2:])) != [(1, 0, 1), (1, 1, 0)]:
        probs.append("old E3 hand vector %s" % h[-2:])
    _, _, h = _o6_channel("old", "E", 6)
    if sorted(map(tuple, h[-2:])) != [(1, 1, 0, 1, 1, 0), (1, 1, 1, 0, 0, 1)]:
        probs.append("old E6 doc vector %s" % h[-2:])
    pond = rect_cells(167, 204, 5, 5)
    live = [(3, 3, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3), (3, 3, 3, 2, 2, 3, 3, 2, 2, 3, 3, 2)]
    for algo in ("old", "fixed"):
        o = PulseOracle(250, 250, {c: 0 for c in pond}, {0: {"limitless": False, "stock": 125.0}}, algo=algo)
        cells = _run(172, 206, 12, 1, 0)
        for c in cells:
            o.dig(c, 3)
        hh = [tuple(v) for v in o.run(cells, 80)]
        stock = o.bodies[0]["stock"]
        if algo == "old":
            if not all(v in hh[-10:] for v in live) or stock != 94:
                probs.append("old plot-D: live vectors/stock 94 not reproduced (stock %s)" % stock)
        else:
            first = next((i + 1 for i, v in enumerate(hh) if v == (3,) * 12), None)
            if first is None or stock != 125 - 36 or not _is_fixed_point(o):
                probs.append("fixed plot-D: final %s stock %s (want all 3, stock 89, at rest)" % (hh[-1], stock))
            else:
                notes.append("plot-D full at pulse %d (bound %d), stock 89" % (first, o6_fill_bound(12, 3)))
    # --- FIXED: every direction fills, identically, within the bound, conserving stock
    worst = -10 ** 9
    for n in O6_LENGTHS:
        for depth in (1, 3):
            hist = {}
            for d in "ENWS":
                o, cs, h = _o6_channel("fixed", d, n, depth)
                hist[d] = h
                first = next((i + 1 for i, v in enumerate(h) if v == [depth] * n), None)
                if first is None:
                    probs.append("fixed %s%d D%d never fills: %s" % (d, n, depth, h[-1]))
                    continue
                worst = max(worst, first - o6_fill_bound(n, depth))
                if first > o6_fill_bound(n, depth):
                    probs.append("fixed %s%d D%d full at pulse %d > bound %d" % (d, n, depth, first, o6_fill_bound(n, depth)))
                if not _is_fixed_point(o):
                    probs.append("fixed %s%d D%d not at rest when full" % (d, n, depth))
                if o.credited != n * depth:
                    probs.append("fixed %s%d D%d credited %d != capacity %d" % (d, n, depth, o.credited, n * depth))
            if len({str(v) for v in hist.values()}) != 1:
                probs.append("fixed n%d D%d: per-pulse vectors differ by direction (cell-index dependence)" % (n, depth))
            # limited stock: conservation every pulse, exact delivery, then rest
            for d in "ENWS":
                cap = n * depth
                stock0 = float(cap // 2 + 1)
                o, cs, _ = _o6_channel("fixed", d, n, depth, pulses=0, limitless=False, stock=stock0)
                for p in range(4 * cap + 8):
                    o.pulse()
                    if sum(o.F[c] for c in cs) + o.bodies[0]["stock"] != stock0:
                        probs.append("fixed %s%d D%d: conservation broken at pulse %d" % (d, n, depth, p + 1))
                        break
                if sum(o.F[c] for c in cs) != stock0 or not _is_fixed_point(o):
                    probs.append("fixed %s%d D%d limited: delivered %d of %d, rest=%s"
                                 % (d, n, depth, sum(o.F[c] for c in cs), stock0, _is_fixed_point(o)))
    # --- FIXED: the "second symptom" (INT section 2) -- a 5-level pond into 8-cell D=1 comes to rest
    for d in "ENWS":
        o, cs, h = _o6_channel("fixed", d, 8, 1, pulses=30, limitless=False, stock=5.0)
        if sum(h[-1]) != 5 or h[-1] != h[-2] or not _is_fixed_point(o):
            probs.append("fixed %s: spent 1-cell pond run not at rest: %s / %s" % (d, h[-2], h[-1]))
    # --- FIXED: a full, sourceless channel breached into the sink band drains (ruling 9), to the
    # same end state the OLD engine reaches: D=1 empties; D=2 keeps its bottom level, because
    # only a BRIMMING cell overflows sideways (unchanged semantics, both algos).
    for d in "ENWS":
        dx, dz = DIRS[d]
        x0, z0 = {"E": (230, 100), "W": (19, 100), "N": (100, 230), "S": (100, 19)}[d]
        for depth in (1, 2):
            ends = {}
            for algo in ("old", "fixed"):
                o = PulseOracle(250, 250, {}, {}, sink_band=SINK_BAND, algo=algo)
                cs = _run(x0 - dx * 12, z0 - dz * 12, 25, dx, dz)   # 12+ interior cells, then the band
                for c in cs:
                    o.dig(c, depth)
                    o.set_fill(c, depth)
                o.run(cs, 200)
                ends[algo] = [o.F[c] for c in cs]
                if algo == "fixed" and not _is_fixed_point(o):
                    probs.append("fixed sink %s D%d not at rest" % (d, depth))
            want = [0] * 25 if depth == 1 else [1 if edge_distance(c) >= SINK_BAND else 0 for c in cs]
            if ends["fixed"] != want or ends["old"] != want:
                probs.append("sink %s D%d: fixed %s old %s want %s" % (d, depth, ends["fixed"], ends["old"], want))
    # --- FIXED: random small networks reach a fixed point and the ledger balances
    import random
    rng = random.Random(1234)
    for trial in range(300):
        W = H = 9
        srcs = {}
        bodies = {}
        for b in range(rng.randint(0, 2)):
            c = (rng.randrange(W), rng.randrange(H))
            srcs[c] = b
            bodies[b] = {"limitless": rng.random() < 0.5, "stock": float(rng.randint(0, 20))}
        o = PulseOracle(W, H, srcs, bodies, per=rng.randint(1, 3),
                        sink_band=rng.choice([None, 1]), algo="fixed")
        for _ in range(rng.randint(3, 30)):
            c = (rng.randrange(W), rng.randrange(H))
            if c in srcs:
                continue
            o.dig(c, rng.randint(1, 4))
            o.set_fill(c, rng.randint(0, 4))
        f0 = sum(o.F.values())
        rest = False
        for p in range(400):
            o.pulse()
            if _is_fixed_point(o):
                rest = True
                break
        total = sum(o.F.values())
        if total != f0 + o.credited - o.drained:
            probs.append("fuzz %d: ledger %d != %d+%d-%d" % (trial, total, f0, o.credited, o.drained))
        if not rest:
            probs.append("fuzz %d: no fixed point in 400 pulses" % trial)
        if len(probs) > 12:
            break
    return Check("O6", not probs, "; ".join(probs[:12]) or
                 "old: E/N oscillate, W/S fill, live reproduced; fixed: ENWS identical & full for n=%s D=1,3 "
                 "within n*D pulses (worst first-full minus bound: %d), stock conserved, spent/partial runs rest, sinks drain, "
                 "300 fuzz nets reach a fixed point; %s" % (list(O6_LENGTHS), worst, "; ".join(notes)))


# ============================================================================ tier O additions
def _exact_scene(scene_key, pulses):
    """One channel scene alone through the shipped exact engine: (oracle, per-pulse W vectors of the scene's cells)."""
    s = SCENES[scene_key]
    body = BODIES[s["body"]]
    stock = body_stock0(body)
    o = PulseOracle(MAP_W, MAP_H, {c: 0 for c in body["cells"]},
                    {0: {"limitless": body["limitless"], "stock": stock, "capacity": stock, "cells": list(body["cells"])}},
                    sink_band=SINK_BAND, recession=True, level_exact=True, beds=site_beds(), **CREEP_LIVE)
    for c in s["cells"]:
        o.dig(c, s["D"])
    out = []
    for _ in range(pulses):
        o.pulse()
        out.append([o.W[c] for c in s["cells"]])
    return o, out


def o7_scene_predictions():
    """Every live flow scene, alone, behaves as the live plan assumes (offline, 0 ticks), through the engine the game
    ships: exact-level water (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, owner 2026-10-17: "a level surface")."""
    probs = []
    U = level_water.U
    for k in ("E2_east_A", "E2_east_B", "E2_north", "E2_south", "E2_rerun"):
        v = oracle_for(k, 8, recession=True)
        # limitless-fed: creep + mouth top-up (CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME): one cell a pulse, full at n = 4
        if v[3] != [1, 1, 1, 1] or v[2] == [1, 1, 1, 1] or v[0] != [1, 0, 0, 0]:
            probs.append("%s: %s" % (k, v[:4]))
    # LIMITED ponds (E2_west off W5, E3b off W2R, E3 off W2): the run and the pond settle at ONE surface, so the pond
    # pays exactly what lies in the run (to the dL), the run is level (1 dL a square) and below the brim, and it rests
    for k, n in (("E2_west", 40), ("E3b_recede", 40), ("E3_budget", 40)):
        o, w = _exact_scene(k, n)
        b = BODIES[SCENES[k]["body"]]
        tot = level_water.pond_dl(o, 0) + sum(w[-1])
        if tot != int(b["capacity"] * U):
            probs.append("%s: pond + run %d dL != capacity %d dL" % (k, tot, b["capacity"] * U))
        if not (0 < min(w[-1]) and max(w[-1]) - min(w[-1]) <= 1 and max(w[-1]) < U) or w[-1] != w[-2]:
            probs.append("%s: run not level at the pond's surface / not at rest: %s" % (k, w[-2:]))
    return Check("O7", not probs, "; ".join(probs) or "E2 limitless-fed x5 full at pulse 4 (water front creep, mouth topped "
                 "up), mouth end first; the limited-pond runs (E2_west, E3b, E3) level with their pond to the dL, below the "
                 "brim, the pond paying exactly what the run holds, then rest")


def o9_shared_source(claim=False):
    """FLOWWORKS_SHARED_SOURCE_STALL_1. Two channels off ONE source cell (perpendicular at a body
    corner, and opposite off a 1-cell source), every orientation, both dig orders. The fixed walk
    (claim=False): both fill to n*D within n*D pulses, identically, and rest; a LIMITED body's stock
    is conserved every pulse, fully delivered, and split by the stated rule -- each pulse the
    channel whose inlet has the LOWER cell index (z*width+x) is paid first, so an odd stock gives it
    the one extra level, whichever was dug first (owner ruling 2026-10-06; RM_FlowKernel.Pulse).
    claim=True is the shipped-until-fix walk and must go red (the second-dug channel stalls)."""
    probs, n = [], 4
    pairs = [("E", "N"), ("N", "W"), ("W", "S"), ("S", "E"), ("E", "W"), ("N", "S")]
    for a, b in pairs:
        for first, second in ((a, b), (b, a)):
            for limitless, stock0 in ((True, 0.0), (False, 5.0)):
                o = PulseOracle(200, 200, {(100, 100): 0}, {0: {"limitless": limitless, "stock": stock0}},
                                algo="fixed", claim_sources=claim)
                runs = {}
                for d in (first, second):
                    dx, dz = DIRS[d]
                    runs[d] = _run(100 + dx, 100 + dz, n, dx, dz)
                    for c in runs[d]:
                        o.dig(c)
                tag = "%s-then-%s %s" % (first, second, "limitless" if limitless else "stock 5")
                hist = {d: [] for d in runs}
                for p in range(4 * n + 8):
                    o.pulse()
                    for d in runs:
                        hist[d].append([o.F[c] for c in runs[d]])
                    tot = sum(o.F.values())
                    if not limitless and tot + o.bodies[0]["stock"] != stock0:
                        probs.append("%s: conservation broken at pulse %d" % (tag, p + 1))
                        break
                if limitless:
                    full = {d: next((i + 1 for i, v in enumerate(h) if v == [1] * n), None) for d, h in hist.items()}
                    if any(f is None or f > o6_fill_bound(n, 1) for f in full.values()):
                        probs.append("%s: first-full %s (bound %d), final %s" % (tag, full, n, {d: h[-1] for d, h in hist.items()}))
                    elif hist[first] != hist[second]:
                        probs.append("%s: the two channels' vectors differ" % tag)
                else:
                    got = {d: sum(hist[d][-1]) for d in runs}
                    low = min(runs, key=lambda d: o.idx(runs[d][0]))
                    high = second if low == first else first
                    if got[low] != 3 or got[high] != 2:
                        probs.append("%s: split %s (rule: lower-index inlet %s gets the odd level, 3/2)" % (tag, got, low))
                if not _is_fixed_point(o):
                    probs.append("%s: not at rest" % tag)
    return Check("O9", not probs, "; ".join(probs[:8]) or
                 "%d pairs x 2 dig orders: limitless -> both full at pulse %d, identical; stock 5 -> conserved, "
                 "split 3/2 to the lower-index inlet, either dig order; all at rest" % (len(pairs), n))


def o8_lint(src=None):
    """Schema lint of every literal bridge call in this file (northstar_driver/lint_calls.py)."""
    try:
        sys.path.insert(0, UTILS)
        from northstar_driver import lint_calls as L
    except Exception as ex:                                  # noqa: BLE001
        return Check("O8", False, "lint_calls unavailable: %s" % ex)
    tools = L.load_tools()
    L.STATS["calls"] = 0                                     # module-global counter: a second lint must not inherit the first's
    src = open(os.path.abspath(__file__), encoding="utf-8").read() if src is None else src
    probs = L.lint_source(src, os.path.basename(__file__), tools)
    # exactly one non-literal call is allowed: RealBridge.call's own transport line
    transport = [p for p in probs if "non-literal tool name" in str(p)]
    probs = [p for p in probs if "non-literal tool name" not in str(p)] + (transport[1:] if len(transport) > 1 else [])
    n = L.STATS.get("calls", 0)
    if n < 90:                                               # sanity probe: the lint must SEE the calls (104 on 2026-10-11)
        return Check("O8", False, "lint saw only %d calls (blind?)" % n)
    return Check("O8", not probs, ("; ".join(map(str, probs[:6])) if probs else "%d bridge calls lint clean" % n))


UTILS = os.path.join(os.path.dirname(MOD), "Utils")      # src/RimMandrake/Utils


def o10_pit_width(held_fn=None):
    """The item's width matrix and edge cases against the Python port (mirrors C# PitWidth_*)."""
    held_fn = held_fn or pit_held
    probs = []
    bands = {0.2: 1, 1.0: 1, 2.24: 1, 2.25: 2, 6.24: 2, 6.25: 3, 12.24: 3}
    for b, w in bands.items():
        if required_width(b) != w:
            probs.append("RequiredWidth(%s)=%s want %s" % (b, required_width(b), w))
    size = {"small": 0.2, "large": 2.4}
    for scene, cell, kind in PIT_MATRIX:
        got = held_fn(SCENES[scene]["cells"], cell, size[kind])
        if got != PIT_EXPECT[scene]:
            probs.append("%s %s held=%s want %s" % (scene, kind, got, PIT_EXPECT[scene]))
    two = [c for c in SCENES["P_2x2_large"]["cells"] if c != (161, 101)]
    if held_fn(two, (160, 100), 2.4):
        probs.append("2x2 with one cell filled in still holds the large pawn")
    diag = [(10, 10), (11, 11), (12, 12)]
    if held_fn(diag, (11, 11), 2.4) or measured_pit_width(diag, (11, 11)) != 1:
        probs.append("diagonal run counted as width")
    if held_fn(SCENES["P_walk"]["cells"], (166, 100), 1.0, ladder=True):
        probs.append("a ladder in the cell still holds")
    return Check("O10", not probs, "; ".join(probs) or "bands %d, matrix {T,T,T;F,F,T}, fill-in releases, diagonal "
                 "and ladder free" % len(bands))


def offline_negative_controls():
    try:
        return _offline_negative_controls()
    except Exception as ex:                      # noqa: BLE001  a crashed control must not read as a pass or a clean fail
        return Check("O-NEG", False, "UNMEASURED: a control crashed: %r" % ex)


def _offline_negative_controls():
    """Each offline check O1-O10 must be ABLE to go red: mutate inputs in memory, expect FAIL."""
    out = []
    defs = dict(_xml_blocks())
    mid = defs["RM_Channel_Mid"]
    defs["RM_Channel_Mid"] = mid[:2] + (mid[2].replace("<pathCost>45</pathCost>", "<pathCost>44</pathCost>"),) + mid[3:]
    out.append(("O1 RM_Channel_Mid pathCost 45 -> 44", o1_defs(defs=defs).ok))
    # O2: a C# toggle the settings table forgot (the old O2 counted only its own 38-row table, so it never saw one)
    spec = _load_site_spec()
    short = dict(spec.SETTINGS)
    short[S_FW] = {k: v for k, v in spec.SETTINGS[S_FW].items() if k != "digFindsEnabled"}
    class _Spec(object):
        SETTINGS, SETTINGS_SOURCES = short, spec.SETTINGS_SOURCES
    out.append(("O2 site_spec.SETTINGS missing a C# toggle (digFindsEnabled)", o2_settings_defaults(spec=_Spec).ok))
    census, _ = settings_census(spec)
    thin = {typ: dict(list(f.items())[:8]) for typ, f in spec.SETTINGS.items()}
    # a census that cannot be taken counts as NOT red: this control did not run, so O-NEG must not pass on it
    out.append(("L2 settings floor: a table holding 8 fields per class (the old n_set >= 31 floor passed it)",
                census is None or not settings_table_gap(thin, census)))
    # O3: the old count could never go red for X10_canal_fire (the PROMOTED table named it 3 times itself)
    if not _DECLARED:
        _DECLARED.extend(declared_rows())
    out.append(("O3 X10_canal_fire row no longer emitted", o3_unbuilt_register(
        emitted=set(_DECLARED) - {"X10_canal_fire"}).ok))
    me = open(os.path.abspath(__file__), encoding="utf-8").read()
    out.append(("O8 a bridge call with an undeclared parameter",
                o8_lint(src=me + '\nB.call("jawa/flowworks_engine_state", noSuchParam=1)\n').ok))
    bad_bodies = dict(BODIES)
    bad_bodies["W5"] = dict(BODIES["W5"], limitless=True)                          # 64-cell inland "limitless"
    out.append(("O4 64-cell inland body declared limitless", o4_geometry(bodies=bad_bodies).ok))
    sc = dict(SCENES)
    sc["X_overlap"] = dict(cells=[SCENES["E2_east_A"]["cells"][1]], phase="A")
    out.append(("O4 overlapping cell", o4_geometry(scenes=sc).ok))
    sc = dict(SCENES)
    sc["X_oob"] = dict(cells=[(260, 30)], phase="A")
    out.append(("O4 out-of-bounds cell", o4_geometry(scenes=sc).ok))
    sc = dict(SCENES)
    sc["X_band"] = dict(cells=[(140, 4)], phase="A")
    out.append(("O4 undeclared sink-band cell", o4_geometry(scenes=sc).ok))
    sc = dict(SCENES)
    sc["X_touch"] = dict(cells=[(16, 62)], phase="A")                              # touches W1, undeclared
    out.append(("O4 cell touching an undeclared body", o4_geometry(scenes=sc).ok))
    saved = dict(FLOAT_DEFAULTS)
    FLOAT_DEFAULTS["rainFillPerPulse"] = 0.2
    try:
        out.append(("O2 changed float default", o2_settings_defaults().ok))
    finally:
        FLOAT_DEFAULTS.clear()
        FLOAT_DEFAULTS.update(saved)
    real = PulseOracle._downstream
    PulseOracle._downstream = lambda self, n, r, dn, dr: True                      # break the fix
    try:
        out.append(("O6 oracle without the flow-order gate", o6_channel_directions().ok))
    finally:
        PulseOracle._downstream = real
    real_pick = PulseOracle._pick
    real_top = PulseOracle._top_up_mouths
    real_exact = level_water.exact_pulse
    PulseOracle._pick = lambda self, r, dr: None                                    # an engine that never flows
    PulseOracle._top_up_mouths = lambda self, comp, took: None                      # (the source tops up no mouth either)
    level_water.exact_pulse = lambda o: None                                        # nor does the exact-level one
    try:
        out.append(("O5 inert engine", o5_oracle_selftest().ok))
        out.append(("O7 inert engine", o7_scene_predictions().ok))
    finally:
        PulseOracle._pick = real_pick
        PulseOracle._top_up_mouths = real_top
        level_water.exact_pulse = real_exact
    out.append(("O9 shared-source walk with the source claimed (pre-fix)", o9_shared_source(claim=True).ok))
    # the retired holder model: any D=4 cell held any pawn
    out.append(("O10 holder model (any D=4 cell holds anything)",
                o10_pit_width(held_fn=lambda cells, c, b, ladder=False, **k: c in set(cells) and not ladder).ok))
    fails = [name for name, ok in out if ok]
    return Check("O-NEG", not fails, ("these did NOT go red: %s" % fails) if fails else
                 "%d in-memory mutations, every one went red" % len(out))


# Recorded live case, v2_20261012e.json (Transient/bench_live_20261012e, 2026-10-12): E2 4-cell D=1 channel off a
# limitless source on the shipped mod (waterFrontCreepEnabled ON), first four pulses' F vectors, first-full pulse 7.
# The pre-creep oracle predicted the brigade (full at pulse 4) and 12 live rows went red on that alone.
# The record shows the mouth dry on pulses 2 and 4: CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME, fixed by the mouth top-up, so
# the record is replayed with the top-up OFF, and the shipped engine is first full at n = 4 (one cell a pulse, no brigade).
O11_LIVE_E2 = [[1, 0, 0, 0], [0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1]]
O11_LIVE_E2_FULL = 7
O11_SHIPPED_FULL = 4


def o11_creep_recorded():
    probs = []
    for d in "ENWS":
        _, _, h = _o6_channel("fixed", d, 4, pulses=12)
        dx, dz = DIRS[d]
        cs = _run(100 + dx, 100 + dz, 4, dx, dz)
        # the record predates the level solve (2732aa5fa), so its vectors are replayed on that engine (level_set off);
        # and before the mouth top-up; shipped (CREEP_LIVE) fills one cell a pulse from the mouth, full at n
        for kw, want_vec in ((dict(CREEP_LIVE, level_set=False), O11_LIVE_E2), (CREEP_LIVE, None)):
            o = PulseOracle(200, 200, {(100, 100): 0}, {0: {"limitless": True, "stock": 0}}, algo="fixed", **kw)
            o.mouth_top_up = want_vec is None
            for c in cs:
                o.dig(c)
            hc = o.run(cs, 12)
            tag = "pre-level-solve" if want_vec else "shipped"
            if want_vec is not None and hc[:4] != want_vec:
                probs.append("%s: %s creep oracle %s != recorded live %s" % (d, tag, hc[:4], want_vec))
            full = next((i + 1 for i, v in enumerate(hc) if v == [1] * 4), None)
            want_full = O11_LIVE_E2_FULL if want_vec else O11_SHIPPED_FULL
            if full != want_full:
                probs.append("%s: %s first full %s != %s" % (d, tag, full, want_full))
            if want_vec is None and hc[:4] != [[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]:
                probs.append("%s: shipped front is not one cell a pulse from a wet mouth: %s" % (d, hc[:4]))
        if next((i + 1 for i, v in enumerate(h) if v == [1] * 4), None) != 4:
            probs.append("%s: creep-off oracle lost the n*D brigade" % d)
    return Check("O11", not probs, "; ".join(probs) or "pre-top-up creep oracle reproduces the recorded live E2 vectors (full at 7); shipped fills one cell a pulse, mouth wet, full at 4; creep off still 4")


def run_offline():
    checks = [o1_defs(), o2_settings_defaults(), o3_unbuilt_register(), o4_geometry(), o5_oracle_selftest(),
              o6_channel_directions(), o7_scene_predictions(), o8_lint(), o9_shared_source(), o10_pit_width(),
              o11_creep_recorded(), offline_negative_controls()]
    for c in checks:
        print(c)
    return checks


# ============================================================================ tier L/S/E (live)
# Run under Windows python.exe from the repo root against a live bridge on the `flowworks` tier.
# Every reading is a STATE read (excavation_rect / flowworks_pulse / body_report / pit_report /
# engine_state / mod_settings_field); nothing is inferred from a screenshot or an absence.
STATUS_OK = ("PASS", "SKIP", "UNCOVERED", "UNBUILT")
# Rows that are RED on the shipped engine because of a filed MOD defect. The mock reproduces the
# shipped semantics, so they are red there too; a fix makes them green and this list shrinks.
KNOWN_MOD_RED = {}   # FLOWWORKS_SHARED_SOURCE_STALL_1 fixed 2026-10-02 (O9 + E2s_shared_source_both_fill)


class Abort(Exception):
    pass


class Live(object):
    def __init__(self, B, progress=None, mock=False):
        self.B, self.progress, self.mock = B, progress, mock
        self.rows, self.steps = [], []
        self.o = None
        self.vec = {}               # scene -> list of per-pulse live vectors (phase A/R)
        self.log_base = 0
        self.ids = {}               # body name -> live body id
        self.jobcells = set()
        self.touched = set()        # (typeName, field) the run changed -> restored in finally
        self.gmism = {}             # phase -> {scene: mismatches} for G_every_cell_vs_oracle

    # ------------------------------------------------------------------ bookkeeping
    def row(self, cid, ok, cls, detail, status=None):
        st = status or ("PASS" if ok else "FAIL")
        r = dict(id=cid, status=st, cls=cls if st in ("FAIL", "UNMEASURED") else "", detail=str(detail)[:1200])
        self.rows.append(r)
        line = "%-22s %-10s %-8s %s" % (cid, st, r["cls"], r["detail"][:300])
        print(line)
        self._log("    " + line)
        return ok

    def _log(self, s):
        if self.progress:
            with open(self.progress, "a", encoding="utf-8") as f:
                f.write(s + "\n")

    def eng(self):
        r = self.B.call("jawa/flowworks_engine_state")
        if not r.get("success"):
            raise Abort("engine_state failed: %r" % r)
        return r

    class _Step(object):
        def __init__(self, live, name, planned, fatal=False):
            self.l, self.name, self.planned, self.fatal = live, name, planned, fatal

        def __enter__(self):
            self.t0, self.n0 = time.time(), self.l.B.n
            self.k0 = self.l.eng().get("ticksGame")
            return self

        def __exit__(self, et, ev, tb):
            try:
                k1 = self.l.eng().get("ticksGame")
            except Exception:                       # noqa: BLE001
                k1 = None
            rec = dict(step=self.name, planned_ticks=self.planned,
                       ticks=(k1 - self.k0) if (k1 is not None and self.k0 is not None) else None,
                       wall_s=round(time.time() - self.t0, 2), calls=self.l.B.n - self.n0,
                       error=("%s: %s" % (et.__name__, ev)) if et else None)
            self.l.steps.append(rec)
            self.l._log("- step %s: ticks %s (planned %s), wall %.1fs, %d calls%s" % (
                rec["step"], rec["ticks"], rec["planned_ticks"], rec["wall_s"],
                rec["calls"], (" ERROR " + rec["error"]) if rec["error"] else ""))
            # Abort, and anything that is not an Exception (KeyboardInterrupt, SystemExit), propagates: a Ctrl-C
            # must stop the run, not be recorded as a step crash while the game keeps being driven
            if et is None or not issubclass(et, Exception) or issubclass(et, Abort):
                return False
            # an unexpected exception inside a step is a HARNESS defect: record, keep going
            self.l.row(self.name + "_crash", False, "HARNESS", "%s: %s" % (et.__name__, ev), status="UNMEASURED")
            if self.fatal:
                # a fatal step (the preflight) guards everything after it: a crash there means the DLL/settings
                # guards never ran, so driving on would drive the game unverified
                raise Abort("%s crashed before its guards ran: %s: %s" % (self.name, et.__name__, ev))
            return True

    def step(self, name, planned, fatal=False):
        return Live._Step(self, name, planned, fatal=fatal)

    # ------------------------------------------------------------------ settings
    def sget(self, typ, f):
        r = self.B.call("jawa/mod_settings_field", typeName=typ, action="get", field=f)
        if not r.get("success"):
            raise Abort("settings get %s failed: %r" % (f, r))
        return r.get("value")

    def sset(self, typ, f, v):
        self.touched.add((typ, f))
        r = self.B.call("jawa/mod_settings_field", typeName=typ, action="set", field=f, value=str(v))
        if not r.get("success") or not _settings_equal(self.sget(typ, f), v):
            raise Abort("settings set %s=%s not read back: %r" % (f, v, r))

    def restore_settings(self):
        bad = []
        for typ, f in sorted(self.touched):
            want = _SETTINGS.get(typ, {}).get(f)
            if want is None:                        # site_spec failed to import: report, never KeyError the restore loop
                bad.append("%s (no shipped default known)" % f)
                continue
            try:
                self.B.call("jawa/mod_settings_field", typeName=typ, action="set", field=f, value=str(want))
                if not _settings_equal(self.sget(typ, f), want):
                    bad.append(f)
            except Exception as ex:                 # noqa: BLE001
                bad.append("%s (%s)" % (f, ex))
        return bad

    # ------------------------------------------------------------------ cells
    def rect(self, x, z, w, h, nonzero=False):
        r = self.B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=nonzero)
        if not r.get("success"):
            raise Abort("excavation_rect %s failed: %r" % ((x, z, w, h), r))
        return {(q["x"], q["z"]): q for q in r.get("rows") or []}, r

    def cells_read(self, cells):
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        m, _ = self.rect(min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1)
        return [m[c] for c in cells]

    def dig(self, c, n, oracle=True):
        r = self.B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1)
        if not r.get("success"):
            raise Abort("dig %s failed: %r" % (c, r))
        if oracle and self.o is not None:
            self.o.dig(c, n)
        return r

    def fill(self, c, f, oracle=True):
        r = self.B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=f)
        if oracle and self.o is not None and r.get("fillSet"):
            self.o.set_fill(c, f)
        return r

    def dig_scene(self, name):
        s = SCENES[name]
        fills = s.get("fill")
        for i, c in enumerate(s["cells"]):
            if s.get("D"):
                self.dig(c, s["D"], oracle=s.get("oracle", True))
            if fills is not None:
                f = fills[i] if isinstance(fills, list) else fills
                if f:
                    self.fill(c, f, oracle=s.get("oracle", True))
            if not s.get("oracle", True):
                self.jobcells.add(c)

    def scene_of(self, c):
        for n, s in SCENES.items():
            if c in s["cells"]:
                return n
        return "?"

    def gmerge(self, phase, mism):
        """Add one L.pulses call's mismatches to G_every_cell_vs_oracle's record for `phase` (every call pulses
        EVERY excavated cell, so every call's divergences count, not only the last call's of the phase)."""
        g = self.gmism.setdefault(phase, {})
        for scene, rows in mism.items():
            g.setdefault(scene, []).extend(rows)

    def pulses(self, n, tag):
        """n pulses at 0 ticks via jawa/flowworks_pulse over EVERY excavated cell; the oracle
        runs the same n pulses; returns (probs, mism, per-scene live vectors, record): probs = contract
        problems, mism = {scene: [(pulse, cell, live F, oracle F)]} for every divergence."""
        r = self.B.call("jawa/flowworks_pulse", count=n, x=0, z=0, w=0, h=0, includeBodies=True)
        if not r.get("success"):
            raise Abort("flowworks_pulse(%d) failed: %r" % (n, str(r)[:400]))
        cells = [(c["x"], c["z"]) for c in r.get("cells") or []]
        pul = r.get("pulses") or []
        probs = []
        if r.get("ticksBefore") != r.get("ticksGame") or r.get("nextPulseTickUntouched") is not True:
            probs.append("ticks/scheduler moved: %s->%s untouched=%s" % (r.get("ticksBefore"), r.get("ticksGame"),
                                                                       r.get("nextPulseTickUntouched")))
        if r.get("gamePaused") is False:
            probs.append("game NOT paused: the real scheduler could also pulse")
        mine = sorted([c for c in self.o.D if self.o.exc(c)] + [c for c in self.jobcells if c not in self.o.D],
                      key=self.o.idx)
        live_set = set(cells)
        if set(mine) - live_set or live_set - set(mine) - self.jobcells:
            probs.append("excavated set differs: oracle-only %s live-only %s" % (
                sorted(set(mine) - live_set)[:4], sorted(live_set - set(mine) - self.jobcells)[:4]))
        cmp = [c for c in cells if c in self.o.D and c not in self.jobcells]
        if pul and [pul[0]["fill"][cells.index(c)] for c in cmp] != [self.o.F[c] for c in cmp]:
            probs.append("pulse-0 vector != oracle state (out of sync before pulsing)")
        per_scene = {}
        mism = {}
        for p in range(1, len(pul)):
            self.o.pulse()
            row = pul[p]["fill"]
            for i, c in enumerate(cells):
                if c in self.jobcells or c not in self.o.D:
                    continue
                if row[i] != self.o.F[c]:
                    mism.setdefault(self.scene_of(c), []).append((p, c, row[i], self.o.F[c]))
        for name, s in SCENES.items():
            if all(c in cells for c in s["cells"]):
                per_scene[name] = [[pul[p]["fill"][cells.index(c)] for c in s["cells"]] for p in range(1, len(pul))]
        if len(pul) != n + 1:
            probs.append("pulsesRun %s != %d" % (r.get("pulsesRun"), n))
        self._log("    pulse[%s] x%d: %d cells, %d mismatching scenes %s" % (tag, n, len(cells), len(mism), sorted(mism)))
        return probs, mism, per_scene, r

    def probe(self, c, kind="dig", pawn=None):
        """jawa/flowworks_job_probe: the designator's and the WorkGiver's own answer for one cell,
        nothing designated or ordered. Returned raw: callers judge success and name failures."""
        if pawn:
            return self.B.call("jawa/flowworks_job_probe", x=c[0], z=c[1], kind=kind, pawnId=pawn)
        return self.B.call("jawa/flowworks_job_probe", x=c[0], z=c[1], kind=kind)

    def body(self, name, classify=True):
        c = BODIES[name]["cells"][0]
        r = self.B.call("jawa/flowworks_body_report", x=c[0], z=c[1], classify=classify)
        if not r.get("success"):
            raise Abort("body_report %s failed: %r" % (name, r))
        return r.get("body") or {}

    @staticmethod
    def body_in(rec, bid):
        bodies = (rec.get("pulses") or [{}])[-1].get("bodies") or []
        return next((b for b in bodies if b.get("id") == bid), {})


def _settings_equal(got, want):
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(got) - float(want)) < 1e-4
    except (TypeError, ValueError):
        return False


def _vc():
    """Utils/validation_core: log_alive / log_revive (the Verse.Log 10,000-message cap guard)."""
    if UTILS not in sys.path:
        sys.path.insert(0, UTILS)
    import validation_core  # noqa: E402
    return validation_core


def _keyed(key):
    """The English text of a FlowWorks Keyed string, read from the mod's own Languages folder. P4b compares the ladder's
    inspect line against this, not a hard-coded prefix: the 2026-10-16 wall-ladder rewording (5dbe8bdae2) turned the old
    `ladder_up`/`ladder_down` prefix test into a HARNESS FAIL while every behavioural half was right."""
    import xml.etree.ElementTree as ET
    kdir = os.path.join(MOD, "Languages", "English", "Keyed")
    for fn in sorted(os.listdir(kdir)):
        if fn.endswith(".xml"):
            el = ET.parse(os.path.join(kdir, fn)).getroot().find(key)
            if el is not None:
                return (el.text or "").strip()
    raise KeyError("Keyed string %s not in %s" % (key, kdir))


def _load_site_spec():
    sys.path.insert(0, HERE)
    import site_spec as S          # noqa: E402
    return S


try:
    _SETTINGS = _load_site_spec().SETTINGS
    # bookkeeping fields the mod itself flips (hoseSettingsImported: the one-time import of Gimme Some Slack's old hose
    # settings, hose port 2026-10-11), not player settings: never drift, never reset (a reset would re-import stale values)
    _INTERNAL = tuple(getattr(_load_site_spec(), "INTERNAL_FLAGS", ()))
except Exception:                  # noqa: BLE001 - offline use without modcheck paths still works
    _SETTINGS, _INTERNAL = {}, ()

LOG_MARKERS = ("FlowWorks", "RimMandrake.FlowWorks", "mandrake.rm.flowworks", "RM_MapComponent_Excavation")


def _clip(x, z, w, h):
    x0, z0, x1, z1 = max(0, x), max(0, z), min(MAP_W, x + w), min(MAP_H, z + h)
    return (x0, z0, x1 - x0, z1 - z0)


def _bbox(cells, ring):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    return _clip(min(xs) - ring, min(zs) - ring, max(xs) - min(xs) + 1 + 2 * ring, max(zs) - min(zs) + 1 + 2 * ring)


def site_rects():
    rs = [_bbox(b["cells"], 2) for b in BODIES.values()] + [_bbox(s["cells"], 2) for s in SCENES.values()]
    rs += [_bbox([spot], 1) for spot in list(PAWN_SPOTS.values()) + list(PIT_SPOTS.values())]
    return sorted(set(rs))


# ---------------------------------------------------------------------------- phase L
def _fold(L, cid, parts):
    """ONE row over several harness sub-checks (densified 2026-10-05, GSS lesson: harness rows are not
    mechanism rows). parts: (name, ok, cls, detail) with ok None = could not ask. The row FAILs whenever any
    part would have (class of the first failing part), is UNMEASURED if a part could not be asked, and its
    detail names every failing part -- so no detection is lost, only lines to read."""
    bad = [p for p in parts if p[1] is False]
    unm = [p for p in parts if p[1] is None]
    det = "; ".join("%s: %s" % (p[0], p[3]) for p in (bad or unm or parts))
    if bad:
        return L.row(cid, False, bad[0][2], det)
    if unm:
        return L.row(cid, False, "HARNESS", det, status="UNMEASURED")
    return L.row(cid, True, "", det)


def phase_L(L, args):
    """L1 fresh map (loaded, paused, 250x250, pristine engine, dry), L2 tier live (log clean, this DLL, shipped
    settings), L3 the four channel defs' live path costs (a MOD row: the obstacle bars), E1a shipped cadence."""
    B = L.B
    with L.step("L_preflight", 0, fatal=True):
        ui = B.call("rimworld/get_ui_state")
        e1 = L.eng()
        if not args.mock:
            time.sleep(1.0)
        e2 = L.eng()
        mi = B.call("jawa/map_info")
        e = L.eng()
        w = B.call("jawa/weather_get")
        rate = ((w.get("weather") or {}).get("rainRate"))
        size_ok = mi.get("sizeX") == MAP_W and mi.get("sizeZ") == MAP_H
        # P11 (LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP) forms every natural body AT MAP LOAD to record its floor, so a fresh
        # quicktest map with any lake has bodyCount > 0 before anything is touched (MEASURED 2026-10-18: 21, 28 on four
        # fresh maps; --fresh-map aborted every time). Pristine = nothing dug; the bodies are printed, not required to be 0.
        pristine = e.get("excavatedCellCount") == 0 and e.get("superdeepCellCount") == 0
        dry = rate is not None and rate <= 0.01
        _fold(L, "L1_fresh_map", [
            ("loaded_paused", ui.get("programState") == "Playing" and e1.get("ticksGame") is not None and e1.get("ticksGame") == e2.get("ticksGame"), "SITE",
             "programState %s, ticksGame %s -> %s over 1 s" % (ui.get("programState"), e1.get("ticksGame"), e2.get("ticksGame"))),
            ("map_250", size_ok, "SITE", "map %sx%s biome %s" % (mi.get("sizeX"), mi.get("sizeZ"), mi.get("mapBiome"))),
            ("pristine", pristine, "SITE", "excavated %s bodies %s superdeep %s activeFluidRaw %s" % (
                e.get("excavatedCellCount"), e.get("bodyCount"), e.get("superdeepCellCount"), e.get("activeFluidRaw"))),
            ("dry", dry, "SITE", "weather %s rainRate %s" % ((w.get("weather") or {}).get("current"), rate))])
        if not size_ok:
            raise Abort("map size")
        if not pristine:
            raise Abort("site not pristine -- start a fresh quicktest map (--fresh-map)")
        if not dry:
            raise Abort("raining at start: every 0-tick vector would carry rain")
        # Verse.Log drops everything after 10,000 messages until cleared: reset it, or E9 reads a silent journal
        L.log_revive = _vc().log_revive(B)
        # log gate + sanity probe (the journal must hold the RimBridge start line)
        lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
        logs = lg.get("logs") or []
        L.log_base = max([x.get("Sequence", 0) for x in logs] or [0])
        L.tap = _vc().tap_start(B)       # the journal is a 1,000-entry ring of every level: keep warn+ as they pass
        # the [RimBridge] start line proved the journal reads; on the full list it scrolls out of the 1,000-entry ring within
        # minutes, so the log_revive sentinel (a fresh warning read back) is accepted as the same proof
        bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs) or bool((L.log_revive or {}).get("alive"))
        fw_err = [x.get("Message", "")[:160] for x in logs if (x.get("Level") or "").lower() in ("error", "exception")
                  and any(m in (x.get("Message", "") + x.get("StackTrace", "")) for m in LOG_MARKERS)]
        log_part = ("log_clean", None, "HARNESS", "sanity probe failed: no [RimBridge] line in %d entries" % len(logs)) \
            if not bridge_line else ("log_clean", not fw_err, "MOD", fw_err or "no FlowWorks error in %d warn+ entries "
                                     "(base seq %d)" % (len(logs), L.log_base))
        tp = B.call("jawa/type_probe", typeName="RimMandrake.FlowWorks.RM_MapComponent_Excavation")
        want = _sha256(os.path.join(MOD, "Assemblies", "RimMandrakeFlowWorks.dll"))
        asm_part = ("assembly_identity", tp.get("assemblyFileSha256") == want and tp.get("mvidMatchesFile") is True,
                    "HARNESS", "loaded %s sha %s mvidMatchesFile %s; repo sha %s" % (
                        tp.get("assemblyLocation"), (tp.get("assemblyFileSha256") or "")[:12], tp.get("mvidMatchesFile"), want[:12]))
        drift = []
        # 2026-10-11 first full-list run: L2 read hoseSettingsImported=True (ship False) as drift on an install that had
        # imported its old hose settings -- true on every upgraded install, so L2 could never pass there
        for typ, fields in sorted(_SETTINGS.items()):
            for f, want_v in sorted(fields.items()):
                if f in _INTERNAL:
                    continue
                v = L.sget(typ, f)
                if not _settings_equal(v, want_v):
                    drift.append("%s=%s (ship %s)" % (f, v, want_v))
        n_set = sum(len(v) for v in _SETTINGS.values())
        census, cprobs = settings_census()
        gap = settings_table_gap(_SETTINGS, census) if census is not None else None
        if drift and args.reset_settings:
            for typ, fields in _SETTINGS.items():
                for f, want_v in fields.items():
                    if f not in _INTERNAL:
                        L.touched.add((typ, f))
            unreset = L.restore_settings()
            if unreset:
                raise Abort("settings reset did not take: %s" % unreset[:6])
            set_part = ("settings_default", False, "HARNESS", "drift RESET by --reset-settings: %s" % drift[:6])
        else:
            # the floor is the C# census (every declared toggle must have been read), not a fixed count
            set_part = ("settings_default", False if drift else (None if gap is None else not gap), "HARNESS",
                        drift[:6] if drift else "C# toggle census not taken: %s" % cprobs if gap is None else
                        "settings table misses C# toggles: %s" % gap[:6] if gap else
                        "%d settings read (every C# toggle among them), all shipped defaults" % n_set)
        _fold(L, "L2_tier_live", [log_part, asm_part, set_part])
        if asm_part[1] is False:
            raise Abort("stale DLL: the running assembly is not the repo's -- redeploy and relaunch before any run")
        if drift and not args.reset_settings:
            raise Abort("settings drift")
        gd = B.call("jawa/get_defs", defs="TerrainDef/RM_Channel_Empty;TerrainDef/RM_Channel_Mid;"
                    "TerrainDef/RM_Channel_Deep;TerrainDef/RM_Channel_Superdeep", fields="pathCost")
        got = {d.get("defName"): (d.get("fields") or {}).get("pathCost") for d in gd.get("defs") or [] if d.get("found")}
        exp = {"RM_Channel_Empty": 30, "RM_Channel_Mid": 45, "RM_Channel_Deep": 80, "RM_Channel_Superdeep": 300}
        L.row("L3_defs_live", gd.get("foundCount") == 4 and not gd.get("notFound") and got == exp, "MOD",
              "live pathCost %s (want %s)" % (got, exp))
        L.row("E1a_cadence_shipped", e.get("pulseIntervalTicks") == PULSE_SHIPPED and
              0 < e.get("nextPulseTick") - e.get("ticksGame") <= PULSE_SHIPPED, "MOD",
              "pulseIntervalTicks %s, nextPulseTick %s at tick %s" % (e.get("pulseIntervalTicks"), e.get("nextPulseTick"),
                                                                    e.get("ticksGame")))


def _sha256(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------------------- site
def phase_site(L, args):
    B = L.B
    with L.step("SITE_paint", 0):
        B.call("jawa/name_colony")
        rects = site_rects()
        # wildlife wanders into plots (run 4: a hare at (201,5) refused the site) -- the plan's recipe
        # removes every non-colonist first; colonists that stand in a plot still refuse.
        db = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        L._log("    destroy_bulk nonColonists: %s" % db.get("matchedCount"))
        pw = B.call("jawa/list_pawns", limit=500)
        inside = [(p.get("id") or p.get("thingId"), p.get("position") or (p.get("x"), p.get("z"))) for p in pw.get("pawns") or []
                  if _in_any(_pos(p), rects)]
        # an unread pawn list is not "no pawn in the plots" (full read 2026-10-19: a failed list_pawns read "0 pawns, none in")
        pawn_part = ("no_pawn_in_plots", None, "HARNESS", "list_pawns unreadable: %s" % str(pw)[:200]) \
            if not (pw.get("success") and isinstance(pw.get("pawns"), list)) else \
            ("no_pawn_in_plots", not inside, "SITE", inside or "%d pawns, none in %d plot rects" % (
                len(pw.get("pawns") or []), len(rects)))
        if inside:
            _fold(L, "L4_site_ready", [pawn_part])
            raise Abort("a pawn stands in a plot rect")
        # SITE (VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG, day 3 2026-10-17): since P11 a LIMITED still body records a lake
        # floor when it is first classified, with a 0.5 m shore shelf on its outer ring, so a pond painted mid-game holds a
        # third to a half of what the scenes were laid out for (S3 read caps 1/4/5/56/100 for 2/8/10/80/128). Whether a
        # floor should form on water painted mid-game is an open spec question (P11_FLOOR_ON_PAINTED_PONDS); this site is
        # about flow, not lake floors (their own proofs: lake_floor_stage.py, SelfTest Lake_floor*), so it runs with the
        # floor generator off and its ponds keep the terrain rule (WaterShallow = ShallowBedLevels). Restored at the end.
        L.sset(S_FW, "deepBedsEnabled", False)
        for r in rects:
            c = B.call("jawa/clear_area", rect="%d,%d,%d,%d" % r, dryRun=False)
            if not c.get("success"):
                raise Abort("clear_area %s: %r" % (r, c))
        soil = B.call("jawa/set_terrain_batch", ops=";".join("Soil:%d,%d,%d,%d" % r for r in rects))
        water = B.call("jawa/set_terrain_batch", ops=";".join("WaterShallow:%d,%d,%d,%d" % _bbox(b["cells"], 0)
                                                             for b in BODIES.values()))
        roof = B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % SCENES["E6_roofed"]["roof"])
        ok = soil.get("success") and water.get("success") and roof.get("success")
        bad = []
        for name, b in BODIES.items():
            m, _ = L.rect(*_bbox(b["cells"], 1))
            src = {c for c, q in m.items() if q.get("isSource")}
            if src != set(b["cells"]):
                bad.append("%s sources %d != %d cells (+%s -%s)" % (name, len(src), len(b["cells"]),
                                                                   sorted(src - set(b["cells"]))[:3], sorted(set(b["cells"]) - src)[:3]))
        for name, s in SCENES.items():
            m, _ = L.rect(*_bbox(s["cells"], 0))
            for c in s["cells"]:
                q = m[c]
                if q["d"] or q["f"] or q["isSource"] or q.get("terrain") != "Soil":
                    bad.append("%s %s not fresh Soil: %s" % (name, c, {k: q.get(k) for k in ("d", "f", "isSource", "terrain")}))
        _fold(L, "L4_site_ready", [pawn_part, (
            "painted_readback", ok and not bad, "SITE", bad[:5] or "%d rects cleared+Soil, %d bodies painted, "
            "every scene cell fresh Soil, every body exactly its sources" % (len(rects), len(BODIES)))])
        if bad:
            raise Abort("site readback")
        # the global oracle: every body as authored, every scene cell undug
        src = {c: n for n, b in BODIES.items() for c in b["cells"]}
        bodies = {n: dict(limitless=b["limitless"], stock=body_stock0(b), capacity=body_stock0(b) or None,
                          cells=list(b["cells"])) for n, b in BODIES.items()}
        # the oracle is the engine the GAME runs: exact-level water when levelExactEnabled is on (shipped)
        L.exact = _settings_equal(L.sget(S_FW, "levelExactEnabled"), True)
        L.o = PulseOracle(MAP_W, MAP_H, src, bodies, sink_band=SINK_BAND, algo="fixed", recession=True,
                          level_exact=L.exact, beds=site_beds() if L.exact else None, **CREEP_LIVE)


def _pos(p):
    q = p.get("position") or {}
    return (q.get("x", p.get("x")), q.get("z", p.get("z")))


def _in_any(c, rects):
    return c[0] is not None and any(r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3] for r in rects)


# ---------------------------------------------------------------------------- phase S (0 ticks)
def phase_S(L, args):
    # The colonist dig cap is a Mod Setting, 2 m shipped (DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL; machines dig deeper).
    # Phase S's ladder rows (S1n, S6) prove the cap at 2 m, the four-depth ladder they were written for, with machine
    # digging OFF so the bridge dig (the designation cap) stops at 2 m too; restored after (restore_settings also
    # covers it). The 8 m rows (the 4/7/7/4 square) are P10's.
    L.sset(S_FW, "maxDigDepth", 4.0)
    L.sset(S_FW, "machineDigEnabled", False)
    try:
        _phase_S_body(L, args)
    finally:
        L.sset(S_FW, "maxDigDepth", 4.0)
        L.sset(S_FW, "machineDigEnabled", True)


def _phase_S_body(L, args):
    B = L.B
    with L.step("S_state", 0):
        e0 = L.eng()
        cells = SCENES["S1_ladder"]["cells"]
        for d, c in enumerate(cells, 1):
            L.dig(c, d)
        got = L.cells_read(cells)
        e1 = L.eng()
        ter = [q.get("terrain") for q in got]
        want_t = ["RM_Channel_Empty", "RM_Channel_Mid", "RM_Channel_Deep", "RM_Channel_Superdeep"]
        L.row("S1_dig_ladder", [q["d"] for q in got] == [1, 2, 3, 4] and ter == want_t
              and e1.get("excavatedCellCount") - e0.get("excavatedCellCount") == 4
              and e1.get("superdeepCellCount") - e0.get("superdeepCellCount") == 1, "MOD",
              "D %s terrain %s excavated +%s superdeep +%s" % ([q["d"] for q in got], ter,
                                                             e1.get("excavatedCellCount") - e0.get("excavatedCellCount"),
                                                             e1.get("superdeepCellCount") - e0.get("superdeepCellCount")))
        r = L.dig(cells[3], 1)
        L.row("S1n_superdeep_is_max", r.get("depth") == 4, "MOD", "deepen D=4 once more -> %s" % r.get("depth"))
        p4 = B.call("jawa/flowworks_pit_report", x=cells[3][0], z=cells[3][1])
        p3 = B.call("jawa/flowworks_pit_report", x=cells[2][0], z=cells[2][1])
        # SUPERDEEP_HOLDER_RETIRE_1 INVERTED S1p (was "S1p_holder_at_D4_only": a hidden RM_SuperdeepPit on
        # every D=4 cell). Digging creates no Thing: the D=4 cell is a grid fact, read back as such.
        if not (p4.get("success") and p3.get("success") and "legacyHolders" in p4):
            L.row("S1p_pit_is_grid_only", False, "HARNESS", "pit_report not the grid reader: %r / %r" % (
                {k: p4.get(k) for k in ("success", "message", "holderPresent")}, p3.get("message")), status="UNMEASURED")
        else:
            L.row("S1p_pit_is_grid_only", p4.get("isSuperdeep") is True and p4.get("pitWidth") == 1
                  and p4.get("legacyHolders") == [] and p3.get("isSuperdeep") is False and p3.get("pitWidth") == 0
                  and p3.get("legacyHolders") == [], "MOD",
                  "D4 cell: isSuperdeep %s width %s holders %s; D3 cell: isSuperdeep %s width %s holders %s" % (
                      p4.get("isSuperdeep"), p4.get("pitWidth"), p4.get("legacyHolders"), p3.get("isSuperdeep"),
                      p3.get("pitWidth"), p3.get("legacyHolders")))
        a, b = SCENES["S2_clamp"]["cells"]
        L.dig(a, 2)
        ra = L.fill(a, 9)
        rb = L.fill(b, 1)
        L.row("S2_fill_clamp", ra.get("fill") == 2 and rb.get("fillSet") is False and rb.get("fill") == 0, "MOD",
              "setFill 9 on D=2 -> F=%s; setFill 1 on undug -> fillSet=%s F=%s" % (ra.get("fill"), rb.get("fillSet"), rb.get("fill")))
        got = {}
        for k in ("W1", "W8", "W2", "W2R", "W3", "W4", "W5"):
            got[k] = L.body(k)
            L.ids[k] = got[k].get("id")
        if not got["W1"].get("limitless"):
            L.row("S3_classification", False, "HARNESS", "sanity probe: W1 (edge, 64) not limitless %r" % got["W1"],
                  status="UNMEASURED")
        else:
            bad = ["%s (edge) not limitless: %r" % (k, got[k]) for k in ("W8", "W4") if got[k].get("limitless") is not True]
            for k in ("W2", "W2R", "W3", "W5"):
                want_c = float(BODIES[k].get("capacity", pond_capacity(len(BODIES[k]["cells"]))))
                g = got[k]
                if g.get("limitless") is not False or abs((g.get("capacity") or 0) - want_c) > 1e-3 \
                        or abs((g.get("stock") or 0) - want_c) > 1e-3 or g.get("cellCount") != len(BODIES[k]["cells"]):
                    bad.append("%s %r (want limited cap %s)" % (k, g, want_c))
            L.row("S3_classification", not bad, "MOD", bad or "W1, W8, W4 (edge, 40) limitless; limited at %d levels a shallow "
                  "square (RM_Volume.ShallowBedLevels): W2 %g, W2R %g, W3 %g, W5 (interior,64) %g" % (
                      POND_LEVELS_PER_CELL, BODIES["W2"]["capacity"], BODIES["W2R"]["capacity"], BODIES["W3"]["capacity"],
                      BODIES["W5"]["capacity"]))
        band, inner = SCENES["S4_band"]["cells"]
        L.dig(band, 1)
        L.dig(inner, 1)
        qb, qi = L.cells_read([band, inner])
        L.row("S4_sink_band", qb.get("isSink") is True and qi.get("isSink") is False, "MOD",
              "isSink at edge distance %d: %s; at %d: %s" % (edge_distance(band), qb.get("isSink"), edge_distance(inner),
                                                          qi.get("isSink")))
        L.sset(S_FW, "stickyLimitlessEnabled", False)
        try:
            off = L.body("W6")
        finally:
            L.sset(S_FW, "stickyLimitlessEnabled", True)
        on = L.body("W7")
        L.ids["W6"], L.ids["W7"] = off.get("id"), on.get("id")
        L.row("S5_sticky_limitless", off.get("limitless") is False and on.get("limitless") is True, "MOD",
              "W6 (sticky OFF) limitless=%s; twin W7 (ON) limitless=%s" % (off.get("limitless"), on.get("limitless")))
        # the oracle learns what the live classification says (S3 asserted it matches the layout)
        for k, g in list(got.items()) + [("W6", off), ("W7", on)]:
            if g.get("id") is not None:
                L.o.bodies[k]["id"] = g["id"]          # the kernel breaks pond ties by body id (level_water.pond_key)
            if g.get("limitless") is not None:
                L.o.bodies[k]["limitless"] = bool(g["limitless"])
                if not g["limitless"]:
                    L.o.bodies[k]["stock"] = float(g.get("stock") or 0)
                    L.o.bodies[k]["capacity"] = float(g.get("capacity") or 0)
        # S6 (was UNCOVERED until jawa/flowworks_job_probe, 2026-10-02): designate_batch bypasses
        # Designator_DigCanal.CanDesignateCell, so ask the designator itself. D=1 deepens with the
        # toggle ON and is refused OFF; D=4 is refused either way (at the 2 m cap phase_S sets); undug soil is accepted even OFF
        # (the toggle gates DEEPENING only -- the control that makes "refused OFF" mean something).
        undug = SCENES["S2_clamp"]["cells"][1]
        # SITE (belt live 2026-10-22, --fresh-map): every S6 probe cell read fogged and the row went UNMEASURED; the probe
        # cells are unfogged first (the designator refuses fog; the row asks about the depth gate, not discovery)
        for c_ in (cells[0], cells[3], undug):
            L.B.call("jawa/set_fog", action="unfog", rect="%d,%d,3,3" % (c_[0] - 1, c_[1] - 1))
        on1, on4 = L.probe(cells[0]), L.probe(cells[3])
        L.sset(S_FW, "digToDepthEnabled", False)
        try:
            off1, off0 = L.probe(cells[0]), L.probe(undug)
        finally:
            L.sset(S_FW, "digToDepthEnabled", True)
        got6 = [on1, on4, off1, off0]
        if not all(g.get("success") for g in got6):
            L.row("S6_digToDepth_gate", False, "HARNESS", "flowworks_job_probe failed: %s" % [
                g.get("message") or g.get("error") for g in got6 if not g.get("success")][:2], status="UNMEASURED")
        elif any(g.get("fogged") for g in got6):
            L.row("S6_digToDepth_gate", False, "SITE", "probe cell fogged (designator refuses fog): %s" % [
                (g["cell"], g["fogged"]) for g in got6], status="UNMEASURED")
        else:
            acc = lambda g: (g.get("designator") or {}).get("accepted")          # noqa: E731
            why = lambda g: (g.get("designator") or {}).get("reason") or ""      # noqa: E731
            L.row("S6_digToDepth_gate", acc(on1) is True and acc(on4) is False and "deepest digging goes" in why(on4)
                  and acc(off1) is False and "Deepening" in why(off1) and acc(off0) is True, "MOD",
                  "Designator_DigCanal: D1 ON %s; D4 %s (%s); D1 OFF %s (%s); undug soil OFF %s" % (
                      acc(on1), acc(on4), why(on4)[:40], acc(off1), why(off1)[:50], acc(off0)))
        s, d = (_src_all(), _xml_blocks()) if UNBUILT else (None, None)
        for bar, (fact, pred) in sorted(UNBUILT.items()):
            L.row("U_" + bar, bool(pred(s, d)), "PROMOTE", ("UNBUILT: %s" % fact) if pred(s, d) else
                  "FEATURE LANDED (source fact flipped): stage a real scene", status="UNBUILT" if pred(s, d) else "FAIL")


# ---------------------------------------------------------------------------- phase A (0 ticks)
def phase_A(L, args):
    with L.step("A_flow_defaults", 0):
        for k in ("E2_east_A", "E2_east_B", "E2_north", "E2_south", "E2_west", "E2s_shared_E7", "E2s_shared_N7",
                  "E2s_shared_N8", "E2s_shared_E8", "E3b_recede", "E5_sink", "E5_inner"):
            L.dig_scene(k)
        pre = L.cells_read(SCENES["E5_sink"]["cells"])
        probe = ("sanity_probe", [q["f"] for q in pre] == [1] * 10, "HARNESS",
                 "rect read of the prefilled E5_sink run: %s (must see a known F=1)" % [q["f"] for q in pre])
        if not probe[1]:
            _fold(L, "A0_instrument", [probe])
            raise Abort("instrument blind")
        sink0, drained0 = L.eng().get("sinkTransferredTotal"), L.o.drained_levels()
        probs, mism, vec, rec = L.pulses(8, "A")
        _fold(L, "A0_instrument", [probe, ("pulse_contract", not probs, "HARNESS",
                                           probs or "8 pulses, 0 ticks, scheduler untouched, paused")])
        L.vec.update(vec)
        # the per-direction E2_east_A/B/north/south/west rows and E2s_shared_source_oracle were each "scene == oracle
        # at every pulse": G_every_cell_vs_oracle fails whenever any of them would, naming the scene (cut 2026-10-05)
        L.gmerge("A", mism)
        # both twins must have been READ: per_scene drops a scene with any cell missing, and None == None is no reading
        L.row("E2_twins_identical", vec.get("E2_east_A") is not None and vec.get("E2_east_A") == vec.get("E2_east_B"), "MOD",
              "A %s / B %s" % (vec.get("E2_east_A", [])[:4], vec.get("E2_east_B", [])[:4]))
        full = {k: next((p + 1 for p, v in enumerate(vec.get(k, [])) if v == [1] * 4), None)
                for k in ("E2_east_A", "E2_north", "E2_south", "E2_west")}
        # shipped waterFrontCreepEnabled: the front advances one cell per pulse from the mouth (no brigade), so a
        # 4-cell D=1 channel is first full at n = 4 now the source tops the mouth up in the pulse it passes its unit on
        # (CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME; the live vectors of 2026-10-12e read 2n-1 = 7, the blink, before it)
        # Exact-level water (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, owner 2026-10-17): a channel off a LIMITLESS body fills
        # to the brim, one square a pulse from the mouth; a channel off a LIMITED pond (E2_west, W5) settles at the pond's
        # ONE surface, below the brim, so its first-full pulse is None by the ruling, not by a stall. Each direction's
        # want is its own oracle's; the limitless three must also agree with each other (the oscillation guard).
        want = {k: next((p + 1 for p, v in enumerate(oracle_for(k, 12, exact=L.exact)) if v == [1] * 4), None)
                for k in full}
        lim3 = [want[k] for k in ("E2_east_A", "E2_north", "E2_south")]
        L.row("E2_channels_fill_every_direction", None not in lim3 and len(set(lim3)) == 1 and full == want
              and "E2_west" not in mism, "MOD",
              "first-full pulse by direction %s (oracle %s; limitless-fed fill at n, the limited W5 pond's channel levels "
              "with its surface; FLOWWORKS_CHANNEL_OSCILLATION_1 regression guard)" % (full, want))
        ring_bad = []
        for k in ("E2_east_A", "E2_north", "E2_south", "E2_west"):
            m, _ = L.rect(*_bbox(SCENES[k]["cells"], 1))
            for c, q in m.items():
                if c in SCENES[k]["cells"] or q.get("isSource") or c in L.o.D:
                    continue
                if q["d"] or q["f"] or q.get("terrain") != "Soil":
                    ring_bad.append((k, c, q["d"], q["f"], q.get("terrain")))
        L.row("E2_dry_ring", not ring_bad, "MOD", ring_bad[:4] or "every non-channel, non-body ring cell undug, F=0, Soil")
        bid = L.ids.get("W2R")
        brec = Live.body_in(rec, bid)
        e3b = vec.get("E3b_recede", [[]])[-1]
        # keep-last-cell (LIQUID_RECESSION_TOPOLOGY_1, shipped ON) made a 1-cell pond never recede while stock > 0, so W2R is
        # a 4-cell pond (2 levels a shallow square since the pond volume unify). Derived from the yardstick: W2R pays the 4-cell
        # run (D=1 each), keeps stock cap-4, and keeps floor(stock/perCell) cells (keep-last-cell: at least one while stock > 0);
        # the rest recede. Recession OFF sheds none (the no_recession fault)
        w2r = BODIES["W2R"]
        if L.exact:
            # POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (owner 2026-10-16: "It should slosh around until it levels, pond or canal or
            # otherwise.") + exact level: the still W2R pond and its run share ONE surface; the pond sheds no squares (the
            # picture shallows instead), its stock is the oracle's (refill adds < 0.01 a pulse: tolerance 0.05) and it paid
            want_stock, want_rec = L.o.stock_of("W2R"), 0
            want_vec = [L.o.F[c] for c in SCENES["E3b_recede"]["cells"]]
        else:
            want_stock = w2r["capacity"] - 4.0
            per_cell = w2r["capacity"] / len(w2r["cells"])
            kept = max(int((want_stock + 1e-6) // per_cell), 1 if want_stock > 0 else 0)
            want_rec = len(w2r["cells"]) - kept
            want_vec = [1, 1, 1, 1]
        got_stock = brec.get("stock") if brec.get("stock") is not None else -9
        L.row("E3b_recession_shipped", "E3b_recede" not in mism and e3b == want_vec and brec.get("recededCount") == want_rec
              and abs(got_stock - want_stock) < 0.05 and got_stock < w2r["capacity"] - 0.5, "MOD",
              "final %s (oracle %s), W2R %s (oracle stock %.4f, receded %s)" % (
                  e3b, want_vec, {k: brec.get(k) for k in ("stock", "recededCount", "activeCellCount")}, want_stock, want_rec))
        sink1 = L.eng().get("sinkTransferredTotal")
        L.row("E5_sink_drains", "E5_sink" not in mism and abs((sink1 - sink0) - (L.o.drained_levels() - drained0)) < 1e-3
              and (L.o.drained_levels() - drained0) > 0, "MOD", mism.get("E5_sink", "")[:3] or
              "band run drained per oracle: sinkTransferredTotal +%s (oracle +%s); final %s" % (
                  sink1 - sink0, L.o.drained_levels() - drained0, vec.get("E5_sink", [[]])[-1]))
        L.row("E5_inner_holds", "E5_inner" not in mism and vec.get("E5_inner", [[]])[-1] == [1] * 10, "MOD",
              "interior prefilled twin final %s" % vec.get("E5_inner", [[]])[-1])
        sh = {k: vec.get(k, [[]])[-1] for k in ("E2s_shared_E7", "E2s_shared_N7", "E2s_shared_N8", "E2s_shared_E8")}
        full_all = all(v == [1] * 4 for v in sh.values())
        L.row("E2s_shared_source_both_fill", full_all, "MOD", "all four shared-source channels full: %s" % sh if full_all
              else "two channels off ONE source cell after 8 pulses: %s -- the second-dug channel stalls at its inlet "
              "(FLOWWORKS_SHARED_SOURCE_STALL_1)" % sh)


# ---------------------------------------------------------------------------- phase B (0 ticks)
def phase_B(L, args):
    with L.step("B_budget", 0):
        L.sset(S_FW, "recessionEnabled", False)
        L.o.recession = False
        try:
            L.dig_scene("E3_budget")
            probs, mism, vec, rec = L.pulses(10, "B")
            L.gmerge("B", mism)
            b = Live.body_in(rec, L.ids.get("W2"))
            v = vec.get("E3_budget", [[]])
            cap2 = BODIES["W2"]["capacity"]
            got2 = b.get("stock") if b.get("stock") is not None else 9
            if L.exact:
                # exact level: the 1-square W2 pond and its 8-square run share one surface (the pond keeps the bottom
                # notch of its own square, the rest lies level over all nine), so the run never shows a whole notch: the
                # budget reads in the pond's stock (= the oracle's, refill < 0.01 a pulse) and in the run's F vector
                spent = abs(got2 - L.o.stock_of("W2")) < 0.05 and got2 < cap2 - 0.5
            else:
                spent = sum(v[-1]) == int(cap2) and got2 < 1
            L.row("E3_budget_exhaustion", not probs and "E3_budget" not in mism and spent and v[-1] == v[-2], "MOD",
                  (probs, mism.get("E3_budget", "")[:3]) if (probs or mism) else
                  "cap-%g pond paid into its run (%s), then rested; stock %s (oracle %.4f)" % (
                      cap2, v[-1], b.get("stock"), L.o.stock_of("W2")))
            L.sset(S_FW, "sourceBudgetEnabled", False)
            L.o.budget = False
            try:
                probs, mism, vec, rec = L.pulses(10, "B-off")
                v2 = vec.get("E3_budget", [[]])
                L.row("E3n_budget_off_supplies", not probs and "E3_budget" not in mism and sum(v2[-1]) > int(BODIES["W2"]["capacity"]), "MOD",
                      (probs, mism.get("E3_budget", "")[:3]) if (probs or mism) else
                      "budget OFF: a spent pond supplies again (%s -> %s)" % (v[-1], v2[-1]))
                L.gmerge("B", mism)
            finally:
                L.sset(S_FW, "sourceBudgetEnabled", True)
                L.o.budget = True
        finally:
            L.sset(S_FW, "recessionEnabled", True)
            L.o.recession = True


# ---------------------------------------------------------------------------- phase C (0 ticks)
def phase_C(L, args):
    with L.step("C_sink_toggle", 0):
        L.sset(S_FW, "edgeSinksEnabled", False)
        L.o.sink_band = None
        try:
            L.dig_scene("E5_sink_off")
            q = L.cells_read(SCENES["E5_sink_off"]["cells"])
            s0 = L.eng().get("sinkTransferredTotal")
            probs, mism, vec, rec = L.pulses(2, "C-off")
            L.gmerge("C", mism)
            s1 = L.eng().get("sinkTransferredTotal")
            L.row("E5n_sinks_off", not probs and "E5_sink_off" not in mism and vec.get("E5_sink_off", [[]])[-1] == [1] * 10
                  and s0 is not None and s1 == s0 and not any(x.get("isSink") for x in q), "MOD",   # None == None is no reading
                  "sinks OFF: run %s, total %s->%s, isSink any=%s" % (vec.get("E5_sink_off", [[]])[-1], s0, s1,
                                                                    any(x.get("isSink") for x in q)))
        finally:
            L.sset(S_FW, "edgeSinksEnabled", True)
            L.o.sink_band = SINK_BAND
        d0, s0 = L.o.drained_levels(), L.eng().get("sinkTransferredTotal")
        probs, mism, vec, rec = L.pulses(3, "C-on")
        s1 = L.eng().get("sinkTransferredTotal")
        L.row("E5_sinks_back_on", not probs and "E5_sink_off" not in mism and abs((s1 - s0) - (L.o.drained_levels() - d0)) < 1e-3
              and L.o.drained_levels() > d0, "MOD", "sinks ON again: %s, total +%s (oracle +%s)" % (
                  vec.get("E5_sink_off", [[]])[-1], s1 - s0, L.o.drained_levels() - d0))
        L.gmerge("C", mism)


# ---------------------------------------------------------------------------- phase R (0 ticks)
def phase_R(L, args):
    with L.step("R_determinism_rerun", 0):
        L.dig_scene("E2_rerun")
        probs, mism, vec, rec = L.pulses(8, "R")
        a, r = L.vec.get("E2_east_A"), vec.get("E2_rerun")
        L.row("E2_rerun_determinism", not probs and a is not None and a == r and "E2_rerun" not in mism, "MOD",
              "E2_east_A (phase A) %s vs E2_rerun (dug later, other body) %s" % ((a or [])[:4], (r or [])[:4]))
        L.gmerge("R", mism)
        # ONE row for the four 0-tick phases (was A/B/C/R_global_vs_oracle + five per-direction E2 rows + the
        # shared-source oracle row): every excavated cell == the oracle at every pulse, failing scenes named
        bad = {ph: {k: v[:2] for k, v in m.items()} for ph, m in sorted(L.gmism.items()) if m}
        L.row("G_every_cell_vs_oracle", not bad and sorted(L.gmism) == ["A", "B", "C", "R"], "MOD",
              bad or "every excavated cell == oracle at every pulse in phases %s (E2 east A/B, north, south, west, "
              "shared-source pairs, budget, sinks, rerun)" % sorted(L.gmism))


# ---------------------------------------------------------------------------- phase J (the ONLY ticks)
def _snapshot(L):
    out = {}
    for name, s in SCENES.items():
        if not s.get("oracle", True) or not any(c in L.o.D for c in s["cells"]):
            continue
        for c, q in zip(s["cells"], L.cells_read(s["cells"])):
            out[c] = (q["d"], q["f"])
    return out


def phase_J(L, args):
    """Pawn jobs (E7 fill-in, E8 dig) are the only things that need the clock. The same ticks
    also carry E4 (engine OFF then ON under the REAL scheduler), E1b (cadence at the pinned,
    clamped pulse) and E6n (rain falling with rainFillsExcavations OFF fills nothing)."""
    B = L.B
    with L.step("J_jobs_scheduler", None) as st:
        for k in ("E4_engine", "E6_open", "E6_roofed", "E7a_fillin", "E7b_overflow", "E8_dig"):
            L.dig_scene(k)
        pawns, rejected = {}, []
        for k, spot in sorted(PAWN_SPOTS.items()):
            # Live run 2 (2026-10-02) drew a colonist INCAPABLE of mining: set_pawn_skill reported
            # disabled, pawn_stats then logged a red "disabled stat MiningSpeed" error (ours, not the
            # mod's) and returned 0.1, so the cap ballooned and the job ran 3,540 ticks. Re-roll
            # until the skill is enabled; never read MiningSpeed off a disabled pawn.
            for dx in (0, 1, -1, 2, -2):
                r = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=spot[0] + dx, z=spot[1], count=1)
                if not r.get("success"):
                    raise Abort("spawn colonist for %s: %r" % (k, r))
                pid = r["pawns"][0]["id"]
                sk = B.call("jawa/set_pawn_skill", pawn=pid, skill="Mining", level=20)
                if (sk.get("before") or {}).get("disabled") or not sk.get("readBackMatches", True):
                    rejected.append(pid)
                    continue
                # Rerun 1 (2026-10-02, the first run with jawa/flowworks_job_probe): two of three job
                # colonists had Mining at priority 0 -- the generator activates only the pawn's top
                # work types, and set_pawn_skill afterwards does not re-run that -- so the WorkGiver
                # was not in their normal giver list and would never have chosen the job unprompted
                # (likely also why run 3's colonists wandered off). HARNESS: switch Mining on.
                # Rerun B (same day): a pawn whose Mining SKILL read enabled had the Mining WORK TYPE
                # disabled (set_work_priority refused) -> the run aborted. Re-roll, like a disabled skill.
                wp = B.call("jawa/set_work_priority", pawnId=pid, workType="Mining", priority=1)
                if not wp.get("success"):
                    rejected.append(pid)
                    continue
                ms = B.call("jawa/pawn_stats", pawn=pid, stats="MiningSpeed")
                pawns[k] = (pid, float(((ms.get("stats") or [{}])[0]).get("value") or 0))
                break
            if k not in pawns:
                raise Abort("no mining-capable colonist in 5 rolls for %s" % k)
        speed = min(v[1] for v in pawns.values())
        L._log("    job pawns %s (rejected, mining disabled: %s)" % (pawns, rejected))
        # caps from the JobDriver work amounts: dig 3200 (WorkToDeepen(0)); fill-in D=1 -> 1600
        cap = int(math.ceil(3200.0 / max(speed, 0.1) * 1.3)) + 240
        cap = min(cap, args.max_job_ticks)
        e8, e7a, e7b = SCENES["E8_dig"]["cells"][0], SCENES["E7a_fillin"]["cells"][1], SCENES["E7b_overflow"]["cells"][1]
        for c, des in ((e8, "RM_DigCanal"), (e7a, "RM_FillInCanal"), (e7b, "RM_FillInCanal")):
            r = B.call("jawa/designate_batch", action="add", designation=des, rect="%d,%d,1,1" % c)
            if not (r.get("success") and r.get("totalNow", 0) >= 1):
                raise Abort("designate %s at %s: %r" % (des, c, r))
        # Live run 3 (2026-10-02, Tundra): left to the WorkGivers, all three colonists walked ~60 cells
        # away and never took the jobs within the cap (4 rows UNMEASURED); in run 2 one job took
        # 3,540 ticks. So the job is ORDERED (TryTakeOrderedJob with the exact JobDef the WorkGiver
        # builds, on the designated cell) -- the JobDriver + designation path is exercised; the
        # WorkGiver's own selection stays UNCOVERED (owed HasJobOnCell probe, same as S6).
        # J_workgiver_selection (was UNCOVERED until jawa/flowworks_job_probe, 2026-10-02): BEFORE any
        # order, ask WorkGiver_DigCanal / WorkGiver_FillInCanal whether they would hand each job pawn
        # its designated cell unprompted (forced=false), and -- the negative control -- that the dig
        # giver offers nothing on an excavated but UNdesignated cell. The pawn's walk to the job stays
        # untimed on purpose (AI noise); this is the selection decision itself.
        sel, bad = [], []
        neg_cell = SCENES["E4_engine"]["cells"][0]
        for k, c, kind, jd in (("E8_dig", e8, "dig", "RM_DigCanalJob"), ("E7a_fillin", e7a, "fillin", "RM_FillInCanalJob"),
                               ("E7b_overflow", e7b, "fillin", "RM_FillInCanalJob")):
            g = L.probe(c, kind=kind, pawn=pawns[k][0])
            wg, pw = g.get("workGiver") or {}, g.get("pawn") or {}
            good = (g.get("success") and g.get("designationPresent") is True and wg.get("shouldSkip") is False
                    and wg.get("cellInPotentialWorkCells") is True and wg.get("hasJobOnCell") is True
                    and wg.get("jobDef") == jd and wg.get("designationDeletedByWorkGiver") is False
                    and pw.get("workTypeDisabled") is False and pw.get("giverInNormalList") is True)
            sel.append("%s:%s/%s skip=%s cell=%s has=%s prio=%s" % (k, kind, wg.get("jobDef"), wg.get("shouldSkip"),
                                                               wg.get("cellInPotentialWorkCells"), wg.get("hasJobOnCell"),
                                                               pw.get("priority")))
            if not good:
                bad.append((k, g.get("message") or {"wg": wg, "pawn": pw, "des": g.get("designationPresent")}))
        gn = L.probe(neg_cell, kind="dig", pawn=pawns["E8_dig"][0])
        wgn = gn.get("workGiver") or {}
        neg_ok = gn.get("success") and gn.get("designationPresent") is False and wgn.get("hasJobOnCell") is False \
            and wgn.get("cellInPotentialWorkCells") is False
        if not neg_ok:
            bad.append(("negative control: undesignated %s" % (neg_cell,), gn.get("message") or wgn))
        if any("no tool" in str(b[1]) or "Unknown" in str(b[1]) for b in bad):
            L.row("J_workgiver_selection", False, "HARNESS", "flowworks_job_probe unavailable: %s" % bad[:1], status="UNMEASURED")
        else:
            L.row("J_workgiver_selection", not bad, "MOD", bad[:3] or "%s; undesignated dug cell -> no job" % "; ".join(sel))
        orders = []
        for k, c, jd in (("E8_dig", e8, "RM_DigCanalJob"), ("E7a_fillin", e7a, "RM_FillInCanalJob"),
                         ("E7b_overflow", e7b, "RM_FillInCanalJob")):
            o = B.call("jawa/ordered_job", pawnId=pawns[k][0], jobDef=jd, targetAX=c[0], targetAZ=c[1], waitTicks=0)
            orders.append((k, o.get("accepted"), o.get("note") or o.get("error") or o.get("message")))
        if not L.row("J_orders_accepted", all(x[1] for x in orders), "HARNESS", orders):
            raise Abort("ordered jobs refused")
        sum7 = {k: sum(q["f"] for q in L.cells_read(SCENES[k]["cells"])) for k in ("E7a_fillin", "E7b_overflow")}
        w = B.call("jawa/weather_set", weather="Rain", lockWeather=True)
        L.sset(S_FW, "rainFillsExcavationsEnabled", False)
        # pin rain to the UI maximum: at the shipped 0.1 a rising Rain rate adds < 1 level over the
        # job window, so "toggle OFF -> nothing gained" would hold for an engine that ignores the
        # toggle too (caught by the mock fault rain_toggle_ignored, 2026-10-02)
        L.sset(S_FW, "rainFillPerPulse", 1.0)
        L.o.rain_on = False
        e0 = L.eng()
        ov0 = e0.get("overflowDestroyedTotal")
        snap0 = _snapshot(L)
        # --- E4 OFF half: the real scheduler must not pulse
        L.sset(S_FW, "depthEngineLiveForTests", True)   # the switch applies on reload (owner 2026-10-22); the harness reads it live
        L.sset(S_FW, "depthEngineEnabled", False)
        eo = L.eng()
        n0 = eo.get("nextPulseTick")
        # the OFF window must STRADDLE the scheduled tick, or an engine that ignores the toggle
        # would pass too (it would simply not be due yet). The jobs progress meanwhile: free.
        off_ticks = max(0, n0 - eo.get("ticksGame")) + PULSE_PIN
        st_off = B.call("rimworld/step_game_ticks", ticks=off_ticks, pauseFirst=True, timeoutMs=300000)
        e1 = L.eng()
        snap1 = _snapshot(L)
        moved = sorted(c for c in snap0 if snap0[c] != snap1.get(c))
        ran_off = e1.get("ticksGame") - e0.get("ticksGame")
        if not e1.get("ticksGame") > n0:
            # Live day 3 (2026-10-17): this step advanced 0 ticks, so the OFF window never reached the due tick and the row
            # read FAIL "OFF for 0 ticks" on an engine that was never tested. A window short of the due tick proves nothing
            # (the plan's E4 contract): HARNESS, with the step tool's own reply for the next driver.
            L.row("E4_engine_off", False, "HARNESS", "the OFF step never passed the due tick %s: %s ticks ran of %s asked; "
                  "step_game_ticks replied %s" % (n0, ran_off, off_ticks, str(st_off)[:300]), status="UNMEASURED")
        else:
            L.row("E4_engine_off", e1.get("nextPulseTick") == n0 and not moved,
                  "MOD", "OFF for %s ticks, past the due tick %s: nextPulseTick %s->%s, cells moved %s" % (
                      ran_off, n0, n0, e1.get("nextPulseTick"), moved[:4]))
        L.sset(S_FW, "depthEngineEnabled", True)
        L.sset(S_FW, "depthEngineLiveForTests", False)
        # --- E1b: pin below the clamp floor; the engine must clamp to 60
        L.sset(S_FW, "pulseIntervalTicks", 30.0)
        e2 = L.eng()
        L.row("E1b_pulse_clamp", e2.get("pulseIntervalTicks") == PULSE_PIN, "MOD",
              "pulseIntervalTicks set 30 -> engine reads %s (clamp floor %d)" % (e2.get("pulseIntervalTicks"), PULSE_PIN))
        hist, chunks, done = [], 0, {}
        t_start = e2.get("ticksGame")
        # full read 2026-10-19: the loop ended only on "jobs done" or "ran >= cap", so a step that runs 0 ticks (the day-3
        # symptom, E4_off above) spun it forever. Bounded by chunk count, and 3 chunks in a row with no tick end it.
        max_chunks, stalled, last_t = args.max_job_ticks // PULSE_PIN + 10, 0, t_start
        while chunks < max_chunks and stalled < 3:
            B.call("rimworld/step_game_ticks", ticks=PULSE_PIN, pauseFirst=True, timeoutMs=120000)
            chunks += 1
            e = L.eng()
            hist.append((e.get("ticksGame"), e.get("nextPulseTick")))
            stalled = stalled + 1 if e.get("ticksGame") == last_t else 0
            last_t = e.get("ticksGame")
            q8, q7a, q7b = L.cells_read([e8, e7a, e7b])
            done = {"E8": q8["d"] == 1, "E7a": q7a["d"] == 0, "E7b": q7b["d"] == 0}
            ran = e.get("ticksGame") - t_start
            if all(done.values()):
                # Live run 5 (2026-10-02): fast colonists finished in 7 chunks, Rain had only lerped
                # to 0.18 and E6n went UNMEASURED. So once the jobs are done, keep pulsing until the
                # rain-OFF negative is measurable (same estimate as E6n below) or the hard job cap.
                wr_now = (B.call("jawa/weather_get").get("weather") or {}).get("rainRate") or 0.0
                if 0.5 * wr_now * chunks >= 1.5 or ran >= args.max_job_ticks:
                    break
            elif ran >= cap:
                break
        spent = hist[-1][0] - t_start
        # A scheduled pulse is a move of nextPulseTick (one per 60-tick chunk at the pinned cadence: a chunk cannot hold two).
        # Normally the first chunk fires at once (nextPulseTick was frozen in the past by the OFF window); when the OFF step
        # did not reach the due tick (day 3) the 250-cadence schedule is still pending and the first chunks hold no pulse.
        # So the cadence is judged from the first real pulse on, and the oracle replays exactly the pulses that ran.
        nprev = [e2.get("nextPulseTick")] + [h[1] for h in hist[:-1]]
        fired = [i for i, (h, p0) in enumerate(zip(hist, nprev)) if h[1] != p0]
        live_pulses = len(fired)
        first = fired[0] if fired else len(hist)
        gaps = [b[1] - a[1] for a, b in zip(hist[first:], hist[first + 1:])]
        lead = [n - t for t, n in hist[first:]]
        # the clock must have run for the scheduler to be asked at all: under two pinned cadences of ticks is UNMEASURED
        clock_ran = spent >= 2 * PULSE_PIN
        clock_note = "the clock did not run: %s ticks over %d chunks of %d (stalled %d)" % (spent, chunks, PULSE_PIN, stalled)
        if not clock_ran:
            L.row("E1c_cadence_real_scheduler", False, "HARNESS", clock_note, status="UNMEASURED")
        else:
            L.row("E1c_cadence_real_scheduler", bool(fired) and all(g == PULSE_PIN for g in gaps)
                  and all(0 < x <= PULSE_PIN for x in lead) and len(hist) - first >= 2, "MOD",
                  "%d chunks of %d ticks, first pulse in chunk %s: nextPulseTick advances %s, lead %s" % (
                      chunks, PULSE_PIN, first + 1 if fired else None, sorted(set(gaps)), sorted(set(lead))))
        for _ in range(live_pulses):
            L.o.pulse()
        snap2 = _snapshot(L)
        diff = sorted((c, snap2.get(c), (L.o.D.get(c, 0), L.o.F.get(c, 0))) for c in snap2
                      if snap2[c] != (L.o.D.get(c, 0), L.o.F.get(c, 0)))
        e4 = [snap2[c][1] for c in SCENES["E4_engine"]["cells"]]
        if not clock_ran:
            L.row("E4_engine_on_scheduled", False, "HARNESS", clock_note, status="UNMEASURED")
        else:
            L.row("E4_engine_on_scheduled", not diff and sum(e4) > 0, "MOD", diff[:4] or
                  "after %d real scheduled pulses every oracle cell == oracle; E4 channel %s" % (live_pulses, e4))
        wr = (B.call("jawa/weather_get").get("weather") or {}).get("rainRate") or 0.0
        would = 0.5 * wr * live_pulses * 1.0     # levels the rain WOULD have added (rate rose ~linearly)
        if wr <= 0.01 or would < 1.5:
            L.row("E6n_rain_toggle_off", False, "HARNESS", "rain too light to test: rate %s over %d pulses would add "
                  "~%.2f levels (< 1.5)" % (wr, live_pulses, would), status="UNMEASURED")
        else:
            L.row("E6n_rain_toggle_off", not diff, "MOD", "rain fell (rate now %.3f) with rainFillsExcavations OFF over %d "
                  "pulses: no cell gained" % (wr, live_pulses) if not diff else diff[:4])
        # --- E7/E8: the jobs
        e3 = L.eng()
        jobs_info = {}
        if not all(done.values()):
            for k, (pid, _) in pawns.items():
                g = B.call("jawa/pawn_get", pawn=pid, limit=1)
                pp = (g.get("pawns") or [{}])[0]
                jobs_info[k] = {x: pp.get(x) for x in ("position", "curJob", "job", "jobDef", "drafted", "downed")}
        q7 = {k: L.cells_read(SCENES[k]["cells"]) for k in ("E7a_fillin", "E7b_overflow")}
        dov = (e3.get("overflowDestroyedTotal") or 0) - (ov0 or 0)
        # full read 2026-10-19: dig_scene's prefill is not checked, so an E7a run left dry (0,0,0) "conserved" 0 -> 0 and
        # PASSed with nothing displaced. The prefill read before the order must be the scene's own.
        pre_bad = {k: (sum7[k], sum(SCENES[k]["fill"])) for k in sum7 if sum7[k] != sum(SCENES[k]["fill"])}
        if pre_bad:
            for k in ("E7a_fillin", "E7b_overflow"):
                L.row("E7a_fillin_displaces" if k == "E7a_fillin" else "E7b_overflow_sanctioned", False, "HARNESS",
                      "precondition: prefilled sum F %s, scene asks %s (the fill write did not take)" % pre_bad.get(
                          k, (sum7[k], sum(SCENES[k]["fill"]))), status="UNMEASURED")
        elif done.get("E7a"):
            s_after = sum(q["f"] for q in q7["E7a_fillin"])
            mid = q7["E7a_fillin"][1]
            L.row("E7a_fillin_displaces", s_after == sum7["E7a_fillin"] and mid.get("terrain") == "Soil" and not mid["isExcavated"],
                  "MOD", "sum F %s -> %s (conserved), middle D=%s terrain %s, vector %s" % (
                      sum7["E7a_fillin"], s_after, mid["d"], mid.get("terrain"), [q["f"] for q in q7["E7a_fillin"]]))
        else:
            L.row("E7a_fillin_displaces", False, "UNRESOLVED", "job not done in %d ticks (cap %d): %s" % (spent, cap, jobs_info),
                  status="UNMEASURED")
        if pre_bad:
            pass                                # E7b's UNMEASURED row was written with E7a's above
        elif done.get("E7b"):
            s_after = sum(q["f"] for q in q7["E7b_overflow"])
            L.row("E7b_overflow_sanctioned", s_after == sum7["E7b_overflow"] - 1 and abs(dov - 1) < 1e-3, "MOD",
                  "no room: sum F %s -> %s, overflowDestroyedTotal +%s (want +1)" % (sum7["E7b_overflow"], s_after, dov))
        else:
            L.row("E7b_overflow_sanctioned", False, "UNRESOLVED", "job not done (%s)" % jobs_info, status="UNMEASURED")
        if done.get("E8"):
            q = L.cells_read([e8])[0]
            L.row("E8_player_dig", q["d"] == 1 and q.get("terrain") == "RM_Channel_Empty", "MOD",
                  "designated cell dug by a colonist: D=%s terrain %s after %d ticks (cap %d, MiningSpeed %.2f)" % (
                      q["d"], q.get("terrain"), spent, cap, speed))
        else:
            L.row("E8_player_dig", False, "UNRESOLVED", "job not done in %d ticks: %s" % (spent, jobs_info), status="UNMEASURED")
        # mirror the job cells into the oracle so the rain phase predicts them too
        for k in ("E7a_fillin", "E7b_overflow", "E8_dig"):
            for c, q in zip(SCENES[k]["cells"], L.cells_read(SCENES[k]["cells"])):
                L.o.set_cell(c, q["d"], q["f"])
        L.jobcells = set()
        st.planned = "<= %d (job cap)" % cap


# ---------------------------------------------------------------------------- phase E6 rain (0 ticks)
def phase_rain(L, args):
    B = L.B
    with L.step("E6_rain", 0):
        L.sset(S_FW, "rainFillPerPulse", 1.0)
        L.sset(S_FW, "rainFillsExcavationsEnabled", True)
        w = B.call("jawa/weather_get")
        rate = (w.get("weather") or {}).get("rainRate") or 0.0
        acc = L.eng().get("rainAccumulator") or 0.0
        exc = [c for c in L.o.D if L.o.exc(c)]
        rr = B.call("jawa/get_roof_batch", rects=";".join("%d,%d,1,1" % c for c in sorted(exc, key=L.o.idx)))
        roofed = set()
        for op in (rr.get("ops") or "").split(";"):
            if ":" in op:
                rdef, xyz = op.split(":", 1)
                x, z, ww, hh = [int(v) for v in xyz.split(",")]
                if rdef.strip() not in ("None", "Clear"):
                    roofed.update((x + i, z + j) for i in range(ww) for j in range(hh))
        o_open, o_roof = SCENES["E6_open"]["cells"][0], SCENES["E6_roofed"]["cells"][0]
        if not (rr.get("success") and isinstance(rr.get("ops"), str)):     # an unread roof is not a SITE fault
            L.row("E6_roof_readback", False, "HARNESS", "get_roof_batch unreadable: %s" % str(rr)[:200], status="UNMEASURED")
            return
        if not L.row("E6_roof_readback", o_roof in roofed and o_open not in roofed, "SITE",
                     "roofed excavated cells %s" % sorted(roofed)[:6]):
            return
        if rate <= 0.01:
            L.row("E6_rain_fills_unroofed", False, "HARNESS", "rainRate %s <= 0.01" % rate, status="UNMEASURED")
            return
        k = 1
        while k <= 30 and (acc + k * rate < 1.0 + 0.02 or abs((acc + k * rate) - round(acc + k * rate)) < 0.02):
            k += 1
        if k > 30:
            L.row("E6_rain_fills_unroofed", False, "HARNESS", "rate %s needs %d pulses" % (rate, k), status="UNMEASURED")
            return
        L.o.rain_on, L.o.rain_rate, L.o.rain_per, L.o.rain_acc, L.o.roofed = True, rate, 1.0, acc, roofed
        probs, mism, vec, rec = L.pulses(k, "rain")
        fo, fr = L.cells_read([o_open, o_roof])
        L.row("E6_rain_fills_unroofed", not probs and fo["f"] >= 1 and fr["f"] == 0 and not mism, "MOD",
              (probs, {n: x[:2] for n, x in mism.items()}) if (probs or mism) else
              "rate %.3f x %d pulses: unroofed F=%s, roofed twin F=%s, every excavated cell == oracle" % (
                  rate, k, fo["f"], fr["f"]))


# ---------------------------------------------------------------------------- tail (0 ticks)
# ---------------------------------------------------------------------------- phase P (pits; ticks)
# SUPERDEEP_HOLDER_RETIRE_1. A pit is a D=4 cell; a pawn in it STAYS SPAWNED and is held by the grid
# trap rule (Source/Superdeep/RM_SuperdeepTrap.cs). Runs after rain (the last oracle compare) so the
# pawns and pits it leaves cannot disturb a flow row. Every reading is jawa/flowworks_pit_report: the
# trap verdict plus REAL Reachability.CanReach / CanReachMapEdge with the pawn's own TraverseParms.
# RULED OUT (2026-10-02, kept as rows): "a pit needs a Thing to hold a pawn" (S1p inverted, O1);
# "a held pawn is one that is absent from the map" (old S7: spawned=false in a container) -> P1 asserts
# spawned=true; "any D=4 cell holds anything" (the holder model) -> P1's large rows and O10's NEG.
def _pit_pawn(rep, pid):
    for p in rep.get("pawns") or []:
        if p.get("id") == pid:
            return p
    return None


def _order_row(o, pid):
    """The pawn's row of a jawa/order_pawn result, carrying the call's top-level ticksElapsed (if that is 0 the game
    never ticked and nothing in the row means anything -- JawaBenchTerrainTools.OrderPawn)."""
    for p in o.get("pawns") or []:
        if p.get("id") == pid:
            return dict(p, ticksElapsed=o.get("ticksElapsed"))
    return {}


def _order_measured(row):
    """An order that can be evidence of a refusal: the pawn got it (orderAccepted) and the game ticked."""
    return row.get("orderAccepted") is True and (row.get("ticksElapsed") or 0) > 0


def _orders_unmeasured(**rows):
    """None when every named order was taken and the game ticked; else the reason (full read 2026-10-19: P4/P4f/P5n/X2-X4
    read "arrived False" off an order that never ran as a MOD FAIL; only P3 guarded it)."""
    bad = ["%s (orderAccepted %s, ticksElapsed %s)" % (k, r.get("orderAccepted"), r.get("ticksElapsed"))
           for k, r in sorted(rows.items()) if not _order_measured(r)]
    return ("order not measurable: " + "; ".join(bad)) if bad else None


def phase_P(L, args):
    B = L.B
    with L.step("P_pits", None):
        # FLOWWORKS_PIT_PAWN_ROWS_RED_1 (2026-10-05): P measures the trap and the ladder in DRY pits, with
        # nothing hostile about. phase_rain leaves rain filling excavations, and since PIT_FILL_EFFECTS_1 a
        # non-swimmer drowns at D=4 F>0 (as designed), so the P_walk colonist drowned before P4 could order it
        # out. And Anomaly fleshbeasts from the storyteller killed the control colonist while it wandered,
        # undrafted, through P3/P4's ~2,400 ticks. Both rows read FAIL on a working mod.
        L.sset(S_FW, "rainFillsExcavationsEnabled", False)
        L.o.rain_on = False
        B.call("jawa/weather_set", weather="Clear")
        B.call("jawa/incident_queue_clear")
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        for k in sorted(k for k, sc in SCENES.items() if sc.get("phase") == "P"):
            L.dig_scene(k)
        ids = {}
        for scene, cell, kind in PIT_MATRIX:
            r = B.call("jawa/spawn_pawn", kindDef=PIT_KINDS[kind], faction="none", x=cell[0], z=cell[1], count=1)
            if not r.get("success"):
                raise Abort("spawn %s for %s: %r" % (PIT_KINDS[kind], scene, r))
            ids[scene] = r["pawns"][0]["id"]
            if kind == "large":           # a juvenile muffalo is under BodySize 2.25 -> W=1, not a large pawn
                B.call("jawa/set_pawn_age", pawn=ids[scene], biologicalYears=8.0)
        got, bad, unm = [], [], []
        for scene, cell, kind in PIT_MATRIX:
            rp = B.call("jawa/flowworks_pit_report", x=cell[0], z=cell[1])
            pw = _pit_pawn(rp, ids[scene])
            if not rp.get("success") or pw is None:
                unm.append("%s: pawn %s not on its cell (%s)" % (scene, ids[scene], rp.get("message")))
                continue
            want_w = 2 if kind == "large" else 1
            if pw.get("requiredWidth") != want_w:
                unm.append("%s: %s BodySize %s -> W %s, not a %s pawn" % (scene, pw.get("def"), pw.get("bodySize"),
                                                                        pw.get("requiredWidth"), kind))
                continue
            pred = pit_held(SCENES[scene]["cells"], cell, float(pw.get("bodySize") or 0))
            held = pw.get("held")
            reach_ok = (pw.get("lipReachable") == 0 and pw.get("canReachMapEdge") is False) if held else \
                (pw.get("lipReachable") or 0) > 0
            got.append("%s %s=%s(reach %s/%s)" % (scene[2:], kind, held, pw.get("lipReachable"), pw.get("lipCells")))
            if not (held == PIT_EXPECT[scene] == pred and reach_ok and pw.get("spawned") is True and not pw.get("dead")):
                bad.append("%s held %s want %s (oracle %s) spawned %s dead %s lip %s/%s edge %s" % (
                    scene, held, PIT_EXPECT[scene], pred, pw.get("spawned"), pw.get("dead"), pw.get("lipReachable"),
                    pw.get("lipCells"), pw.get("canReachMapEdge")))
        if unm:
            L.row("P1_width_matrix", False, "SITE", unm[:4], status="UNMEASURED")
        else:
            L.row("P1_width_matrix", not bad, "MOD", bad[:4] or "held {T,T,T;F,F,T} as owner Q4 rules; all "
                  "spawned; held -> 0 lip cells reachable + no map edge: %s" % "; ".join(got))
        # P2: filling in one cell of the 2x2 breaks the large pawn's square -> it is released, live
        big = ids["P_2x2_large"]
        f = B.call("jawa/flowworks_excavation_drive", x=161, z=101, deepenLevels=0, setFill=-1, fillInLevels=1)
        if L.o is not None and f.get("success"):
            L.o.set_cell((161, 101), int(f.get("depth") or 0), 0)
        rp = B.call("jawa/flowworks_pit_report", x=160, z=100)
        pw = _pit_pawn(rp, big) or {}
        # a refused fill-in drive or an unread pit report is "could not ask", not a MOD FAIL (full read 2026-10-19)
        if not f.get("success") or not rp.get("success") or not pw:
            L.row("P2_fillin_releases_large", False, "HARNESS", "fill-in drive %s / pit_report %s / large pawn found %s: %s" % (
                f.get("success"), rp.get("success"), bool(pw), str(f if not f.get("success") else rp)[:200]), status="UNMEASURED")
        else:
            L.row("P2_fillin_releases_large", f.get("depth") == 3 and pw.get("held") is False
                  and (pw.get("lipReachable") or 0) > 0 and rp.get("pitWidth") == 1, "MOD",
                  "fill-in (161,101) -> D %s; large at (160,100): width %s held %s lip %s/%s" % (
                      f.get("depth"), rp.get("pitWidth"), pw.get("held"), pw.get("lipReachable"), pw.get("lipCells")))
        # FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner, 2026-10-06): "You can't fall in by careless colonist pathing.
        # Only if they get blown/forced in do they fall." RM_PitPathing refuses a walk into a LADDERLESS open D=4
        # cell, so: P3 = the refusal itself (own-faction capture ON, the pawn still stays out); P4 = the colonist
        # climbs DOWN a lowered ladder (no fall), is not held, and walks out. The forced-fall half of the old P3
        # (descent event, fall damage) is P3f/P4f (FLOWWORKS_FORCED_PIT_FALL_ROW_1): a vanilla PawnFlyer landing
        # driven by RM_PromotionProofs.ProofForcedFlyer.
        col = {}

        def spawn_col(k):           # each colonist spawned just before its own row, so none idles undrafted
            spot = PIT_SPOTS[k]
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=spot[0], z=spot[1], count=1)
            if not r.get("success"):
                raise Abort("spawn colonist for %s: %r" % (k, r))
            col[k] = r["pawns"][0]["id"]
            return col[k]

        def alive(rep, pid):        # a dead or downed pawn is not evidence about the trap: say so in the row
            pw = _pit_pawn(rep, pid)
            return "pawn %s fill %s" % ("off-cell" if pw is None else "dead" if pw.get("dead") else
                                        "downed" if pw.get("downed") else "ok", rep.get("fillRaw"))
        a, wc = spawn_col("P_walk"), SCENES["P_walk"]["cells"][0]
        L.sset(S_FW, "superdeepCapturesOwnFaction", True)
        try:
            d0 = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1]).get("descentCount") or 0
            # P3: NO ladder in the pit. Ordering the drafted colonist in is refused; it never enters.
            o_in = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1], waitTicks=PIT_WAIT_IN, draft=True), a)
            r_in = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pw = _pit_pawn(r_in, a)
            rec = [d for d in r_in.get("recentDescents") or [] if d.startswith(a + "@")]
            end = o_in.get("end") or {}
            # "arrived False" is only a refusal if the order was taken and the game ticked: a pawn that never got the
            # order, or a 0-tick wait, also never arrives (UNMEASURED, not PASS)
            p3_unm = None if _order_measured(o_in) else "order not measurable: orderAccepted %s, ticksElapsed %s" % (
                o_in.get("orderAccepted"), o_in.get("ticksElapsed"))
            if p3_unm:
                L.row("P3_walk_in_held", False, "HARNESS", p3_unm, status="UNMEASURED")
            else:
                L.row("P3_walk_in_held", o_in.get("arrived") is False and pw is None and not rec
                      and (end.get("x"), end.get("z")) != wc and (r_in.get("descentCount") or 0) == d0
                      and r_in.get("hasLadder") is False, "MOD",
                      "ladderless D=4 (FLOWWORKS_PIT_FALL_ONLY_FORCED_1: pathing never drops a colonist in), capture ON: "
                      "ordered in (accepted, %s ticks) -> arrived %s, moved %s, in the pit cell %s, own descents %d "
                      "(map-wide %s->%s), ended %s, hasLadder %s" % (
                          o_in.get("ticksElapsed"), o_in.get("arrived"), o_in.get("moved"), pw is not None, len(rec), d0,
                          r_in.get("descentCount"), (end.get("x"), end.get("z")), r_in.get("hasLadder")))
            # P3f (FLOWWORKS_FORCED_PIT_FALL_ROW_1): the FORCED entry P3 no longer covers. A second colonist is
            # first ordered in (the control: refused, exactly as P3), then launched as a vanilla PawnFlyer onto the
            # same ladderless D=4 cell (ProofForcedFlyer: PawnFlyer.MakeFlyer + GenSpawn.Spawn, as JumpUtility does,
            # so the landing runs PawnFlyer.RespawnPawn -> RM_Patch_PawnFlyer_LandInPit). It must end on the cell,
            # take exactly ONE own descent with fall damage > 0, and be held (a forced own colonist is a jumper).
            # P4f reads the same pawn after P4's ladder is lowered: held until a ladder is built, then free.
            fp = spawn_col("P_forced")
            o_fc = _order_row(B.call("jawa/order_pawn", pawnId=fp, x=wc[0], z=wc[1], waitTicks=PIT_WAIT_IN, draft=True), fp)
            r_fc = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            ctrl_ok = _order_measured(o_fc) and o_fc.get("arrived") is False and _pit_pawn(r_fc, fp) is None
            df = r_fc.get("descentCount") or 0
            ok_f, lf, tf = _proof(B, "ProofForcedFlyer", "%s,%d,%d" % (fp, wc[0], wc[1]))
            tk_land0 = L.eng().get("ticksGame")
            st_land = B.call("rimworld/step_game_ticks", ticks=FLYER_LAND_TICKS, pauseFirst=True, timeoutMs=120000)
            tk_land = (L.eng().get("ticksGame") or 0) - (tk_land0 or 0)
            r_f = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pf = _pit_pawn(r_f, fp)
            rec_f = [d for d in r_f.get("recentDescents") or [] if d.startswith(fp + "@")]
            falls = [float(d.rsplit("fall=", 1)[1]) for d in rec_f if "fall=" in d]
            # def=PawnFlyer_Stun: a THROW. A DLL that still launches the unstunned ThingDefOf.PawnFlyer makes a deliberate
            # jump, which lands safely by design (pitJumpLandsSafe, owner 2026-10-18) -- the 2026-10-19 "own descents 0"
            # red on DLL ccf36a9af7 was that, not the trap (FLOWWORKS_V2_DIAGNOSE_THREE_NEW_REDS)
            forced_measured = ok_f and lf.get("launched") == "True" and lf.get("def") == "PawnFlyer_Stun"
            # pass-2 review: a control order that was never taken (or a 0-tick wait) and an unstepped landing window are
            # "could not ask", not a MOD FAIL (P3 already reads its own order this way)
            p3f_unm = None if forced_measured else \
                "ProofForcedFlyer did not launch a thrown flyer (stale DLL? want def=PawnFlyer_Stun): %s" % tf
            if not p3f_unm and not _order_measured(o_fc):
                p3f_unm = "control order not measurable: orderAccepted %s, ticksElapsed %s" % (
                    o_fc.get("orderAccepted"), o_fc.get("ticksElapsed"))
            if not p3f_unm and (st_land.get("success") is False or tk_land < FLYER_LAND_TICKS // 2):
                # full read 2026-10-19: a success reply that ran 0 ticks (the day-3 symptom) left the flyer in the air
                p3f_unm = "landing window not stepped: %s of %d ticks ran; step_game_ticks replied %s" % (
                    tk_land, FLYER_LAND_TICKS, str(st_land)[:200])
            if p3f_unm:
                L.row("P3f_forced_entry_falls", False, "HARNESS", p3f_unm, status="UNMEASURED")
            else:
                L.row("P3f_forced_entry_falls", ctrl_ok and lf.get("depth") == "4" and pf is not None
                      and pf.get("spawned") is True and not pf.get("dead") and len(rec_f) == 1 and falls and falls[0] > 0
                      and (r_f.get("descentCount") or 0) == df + 1 and pf.get("held") is True
                      and pf.get("lipReachable") == 0 and r_f.get("hasLadder") is False, "MOD",
                      "control (walk in: accepted %s, %s ticks) refused %s; flyer %s->%s D %s; in cell %s, own descents %d fall %s (map-wide %s->%s), "
                      "held %s lip %s/%s hasLadder %s; %s" % (
                          o_fc.get("orderAccepted"), o_fc.get("ticksElapsed"), ctrl_ok, lf.get("from"), lf.get("to"),
                          lf.get("depth"), pf is not None, len(rec_f), falls,
                          df, r_f.get("descentCount"), (pf or {}).get("held"), (pf or {}).get("lipReachable"),
                          (pf or {}).get("lipCells"), r_f.get("hasLadder"), alive(r_f, fp)))
            # P4: a lowered ladder in the pit cell -> the same colonist climbs down (no fall), is not held, walks out.
            sb = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % wc)
            ok_rd, lrd, _ = _proof(B, "ProofLadder", "%d,%d,lower" % wc)    # lowered: the state the row is about
            # P4f is read HERE, before P4's colonist goes down: the P3f pawn still stands in this 1-cell pit, and a drafted
            # Goto onto a cell a standing pawn holds ends at the lip (vanilla pawn blocking, measured live 2026-10-11 on
            # the full list: second colonist ended at (165,100) while the first stood in the pit; in once it was empty).
            # So the freed forced pawn walks out first (the order is evidence too: freed means it can leave).
            r_ff = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            o_ff_out = _order_row(B.call("jawa/order_pawn", pawnId=fp, x=wc[0] - 1, z=wc[1] + 4, waitTicks=PIT_WAIT_OUT,
                                         draft=True), fp)
            o_l_in = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1], waitTicks=PIT_WAIT_IN, draft=True), a)
            r_l = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pl = _pit_pawn(r_l, a) or {}
            rec_l = [d for d in r_l.get("recentDescents") or [] if d.startswith(a + "@")]
            o_l = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1] + 3, waitTicks=PIT_WAIT_OUT, draft=True), a)
            p4_unm = _orders_unmeasured(climb_down=o_l_in, walk_out=o_l)
            if not p4_unm and not sb.get("success"):      # no ladder spawned: a setup refusal, not a mod verdict
                p4_unm = "ladder not spawned: %s" % str(sb)[:200]
            if p4_unm:
                L.row("P4_ladder_frees", False, "HARNESS", p4_unm, status="UNMEASURED")
            else:
                L.row("P4_ladder_frees", ok_rd and lrd.get("raised") == "False" and r_l.get("hasLadder") is True
                      and o_l_in.get("arrived") is True and pl.get("spawned") is True and not rec_l and pl.get("held") is False
                      and (pl.get("lipReachable") or 0) > 0 and o_l.get("arrived") is True, "MOD",
                      "ladder spawned %s lowered %s hasLadder %s; climbed down: arrived %s, falls %d, held %s lip %s/%s; "
                      "ordered out: arrived %s; %s" % (
                          sb.get("success"), lrd.get("raised") == "False", r_l.get("hasLadder"), o_l_in.get("arrived"),
                          len(rec_l), pl.get("held"), pl.get("lipReachable"), pl.get("lipCells"), o_l.get("arrived"),
                          alive(r_l, a)))
            # P4f: the P3f pawn, forced in and held, is freed by the same lowered ladder (and took no second fall).
            pff = _pit_pawn(r_ff, fp) or {}
            rec_ff = [d for d in r_l.get("recentDescents") or [] if d.startswith(fp + "@")]
            # P4f needs P3f's state: the forced pawn in the pit AND held before the ladder. A pawn that was never held
            # "freed by the ladder" is a vacuous PASS; one that never landed in the pit is P3f's finding, not P4f's.
            if p3f_unm:
                L.row("P4f_ladder_frees_forced", False, "HARNESS", "P3f unmeasured: %s" % p3f_unm, status="UNMEASURED")
            elif pf is None or pf.get("held") is not True:
                L.row("P4f_ladder_frees_forced", False, "SITE", "precondition: the forced pawn was not held in the pit "
                      "before the ladder (in cell %s, held %s): see P3f" % (pf is not None, (pf or {}).get("held")),
                      status="UNMEASURED")
            elif _orders_unmeasured(walk_out=o_ff_out):
                L.row("P4f_ladder_frees_forced", False, "HARNESS", _orders_unmeasured(walk_out=o_ff_out), status="UNMEASURED")
            else:
                L.row("P4f_ladder_frees_forced", ok_rd and r_ff.get("hasLadder") is True and pff.get("spawned") is True
                      and pff.get("held") is False and (pff.get("lipReachable") or 0) > 0 and len(rec_ff) == 1
                      and o_ff_out.get("arrived") is True, "MOD",
                      "ladder lowered %s: forced pawn in cell %s held %s lip %s/%s own descents %d, walked out %s; %s" % (
                          ok_rd, bool(pff), pff.get("held"), pff.get("lipReachable"), pff.get("lipCells"), len(rec_ff),
                          o_ff_out.get("arrived"), alive(r_ff, fp)))
            # P4b (ladder_state_legible, promoted 2026-10-05): the colonist climbs back down, the ladder is RAISED
            # from outside (RM_CompLadder.raised, the gizmo's own field) -> held, cannot reach the lip, and the
            # inspect line says so; LOWERED again -> free. Owner Q1: raised, nobody climbs, own people included.
            o_back = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1], waitTicks=PIT_WAIT_IN, draft=True), a)
            ok_r, lr, _ = _proof(B, "ProofLadder", "%d,%d,raise" % wc)
            r_up = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pu = _pit_pawn(r_up, a) or {}
            o_up = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1] + 3, waitTicks=PIT_WAIT_OUT, draft=True), a)
            ok_l, ll, _ = _proof(B, "ProofLadder", "%d,%d,lower" % wc)
            r_dn = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pd = _pit_pawn(r_dn, a) or {}
            if not (ok_r and ok_l) or o_back.get("arrived") is not True:
                L.row("P4b_ladder_raised_strands", False, "HARNESS", "ladder proof %s/%s (%s / %s); back in %s; %s" % (
                    ok_r, ok_l, lr, ll, o_back.get("arrived"), alive(r_up, a)), status="UNMEASURED")
            else:
                # ProofLadder writes the inspect line with spaces as underscores (one kv token)
                lad_up = tuple(_keyed(k).replace(" ", "_") for k in ("RMFlow_LadderRaisedInspect",))
                lad_dn = tuple(_keyed(k).replace(" ", "_") for k in ("RMFlow_LadderLoweredInspect", "RMFlow_LadderLoweredPrisonInspect"))
                L.row("P4b_ladder_raised_strands", lr.get("raised") == "True" and lr.get("inspect", "") in lad_up
                      and pu.get("held") is True and pu.get("lipReachable") == 0 and o_up.get("canReach") is False
                      and ll.get("raised") == "False" and ll.get("inspect", "") in lad_dn and pd.get("held") is False
                      and (pd.get("lipReachable") or 0) > 0, "MOD",
                      "raised %s (%s): held %s lip %s/%s, ordered out canReach %s | lowered %s (%s): held %s lip %s/%s; %s" % (
                          lr.get("raised"), lr.get("inspect"), pu.get("held"), pu.get("lipReachable"), pu.get("lipCells"),
                          o_up.get("canReach"), ll.get("raised"), ll.get("inspect"), pd.get("held"), pd.get("lipReachable"),
                          pd.get("lipCells"), alive(r_dn, a)))
        finally:
            L.sset(S_FW, "superdeepCapturesOwnFaction", False)
        b, cc = spawn_col("P_walk_ctrl"), SCENES["P_walk_ctrl"]["cells"][0]
        # P5n: pathing needs a lowered ladder to enter a pit at all (FLOWWORKS_PIT_FALL_ONLY_FORCED_1), so the
        # control climbs down one; the carve-out is read from the pawn's own captured/held flags.
        sbc = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % cc)
        _proof(B, "ProofLadder", "%d,%d,lower" % cc)
        d1 = B.call("jawa/flowworks_pit_report", x=cc[0], z=cc[1]).get("descentCount") or 0
        o_in = _order_row(B.call("jawa/order_pawn", pawnId=b, x=cc[0], z=cc[1], waitTicks=PIT_WAIT_IN, draft=True), b)
        r_c = B.call("jawa/flowworks_pit_report", x=cc[0], z=cc[1])
        pc = _pit_pawn(r_c, b) or {}
        o_out = _order_row(B.call("jawa/order_pawn", pawnId=b, x=cc[0], z=cc[1] + 3, waitTicks=PIT_WAIT_OUT, draft=True), b)
        p5_unm = _orders_unmeasured(climb_down=o_in, walk_out=o_out)
        if not p5_unm and not sbc.get("success"):
            p5_unm = "ladder not spawned: %s" % str(sbc)[:200]
        if p5_unm:
            L.row("P5n_own_faction_carveout", False, "HARNESS", p5_unm, status="UNMEASURED")
        else:
            L.row("P5n_own_faction_carveout", o_in.get("arrived") is True and pc.get("captured") is False
                  and pc.get("held") is False and not [d for d in r_c.get("recentDescents") or [] if d.startswith(b + "@")]
                  and o_out.get("arrived") is True,
                  "MOD", "carve-out ON (shipped), ladder %s: colonist in %s captured %s held %s descents %s->%s; out %s; %s" % (
                      sbc.get("success"), o_in.get("arrived"), pc.get("captured"), pc.get("held"), d1, r_c.get("descentCount"),
                      o_out.get("arrived"), alive(r_c, b)))
        for pid in col.values():
            B.call("jawa/set_pawn_faction", pawn=pid, faction="none")
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)



# ---------------------------------------------------------------------------- phase X (promoted bars; ticks)
# 2026-10-05 (belt_flowworksC): the ten bars the UNBUILT register held, each a state read of the running game.
# Every reading is RimMandrake.FlowWorks.RM_PromotionProofs through jawa/static_call (one string arg, one
# "KEY k=v ..." line back), so a stale DLL fails as "Type not found", never as a quiet pass.
PROOF_TYPE = "RimMandrake.FlowWorks.RM_PromotionProofs"
FLUIDID_TYPE = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
SINK_PER_LEVEL = FLOAT_DEFAULTS["pitSinkPerLevel"]
FEET_TO_HEAD = 1.0                 # RM_PitDrawMath.HumanlikeFeetToHeadTop (PROVISIONAL)
TAR, WATER, SLIME = "RM_Fluid_Tar", "RM_Fluid_Water", "RM_Fluid_SlimeGreen"


def _proof(B, method, arg, typ=PROOF_TYPE):
    r = B.call("jawa/static_call", type=typ, method=method, args=arg)
    txt = str(r.get("result") or r.get("message") or r.get("error") or "")
    kv = dict(t.split("=", 1) for t in txt.split()[1:] if "=" in t)
    return r.get("success") is True and not txt.startswith("REFUSED"), kv, txt


def _fill_fluid(L, c, f, fluid):
    ok, _, txt = _proof(L.B, "ProofFillWithFluid", "%d,%d,%d,%s" % (c[0], c[1], f, fluid), typ=FLUIDID_TYPE)
    ok = ok and txt.startswith("FILLED")
    if ok and L.o is not None:
        L.o.set_fill(c, f)
        if fluid == WATER:
            L.o.fluid.pop(c, None)
        else:
            L.o.fluid[c] = fluid
    return ok, txt


def _fluid_row(L, cells):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    ok, kv, txt = _proof(L.B, "ProofFluidRow", "%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
    out = {}
    for tok in (txt.split(" ", 3)[3] if ok and txt.count(" ") >= 3 else "").split(";"):
        if ":" in tok:
            xz, rest = tok.split(":", 1)
            x, z = map(int, xz.split(","))
            d, f, fl, ter = rest.split("/", 3)
            out[(x, z)] = dict(d=int(d), f=int(f), fluid=fl, terrain=ter)
    return ok, out, kv


NSP_TYPE = "RimMandrake.FlowWorks.RM_NorthstarProofs"
_LITRES = re.compile(r"\(([\d,]+) L\)")


def _litres(L, c):
    """Litres in a dug square (RM_NorthstarProofs.ProofReadout, P8's readout: '... Water 0.47 m (940 L)'); None = no read."""
    ok, _, txt = _proof(L.B, "ProofReadout", "%d,%d" % c, typ=NSP_TYPE)
    m = _LITRES.search(txt) if ok else None
    return int(m.group(1).replace(",", "")) if m else None


def _x_two_oracle(exact, tar_row, water_row, pulse0=0):
    """X_two alone after phase X's 3 + 9 pulses: the tar row (D=1, one notch each), the water row (D=1, one notch each)
    and the dry D=2 junction between them, through the engine the game runs (exact or whole-notch). pulse0 = the map's
    scribed pulse count before the first of them: tar moves only on pulses that are a multiple of its stride
    (RM_StockMath.FluidMovesThisPulse over PulseCount), so the race at the junction depends on it (full read 2026-10-19:
    the oracle started at 0, right only when the map's count happened to sit on a stride boundary)."""
    o = PulseOracle(MAP_W, MAP_H, {}, {}, algo="fixed", level_exact=exact, **CREEP_LIVE)
    o.pulse_n = pulse0
    for c in tar_row + water_row:
        o.dig(c, 1)
        o.set_fill(c, 1)
    for c in tar_row:
        o.fluid[c] = TAR
    o.dig(X_JUNCTION, 2)
    for _ in range(12):
        o.pulse()
    return o


def _sink_ok(kv, depth):
    try:
        sink, dz = float(kv["sink"]), float(kv["drawDz"])
    except (KeyError, ValueError):
        return False
    return (kv.get("depth") == str(depth) and abs(sink - SINK_PER_LEVEL * depth) < 1e-3 and abs(dz + sink) < 0.05)


def _xpulse(L, n):
    r = L.B.call("jawa/flowworks_pulse", count=n, x=0, z=0, w=0, h=0, includeBodies=False)
    if not r.get("success"):
        raise Abort("flowworks_pulse(%d) in phase X failed: %r" % (n, str(r)[:300]))


def _level_at(rows, cells):
    """(index of the one wet cell, total fill, fluids seen) over a staircase."""
    wet = [i for i, c in enumerate(cells) if rows.get(c, {}).get("f", 0) > 0]
    return (wet[0] if len(wet) == 1 else wet), sum(rows.get(c, {}).get("f", 0) for c in cells), \
        sorted({rows[c]["fluid"] for c in cells if c in rows and rows[c]["f"] > 0})


def phase_X(L, args):
    B = L.B
    with L.step("X_promoted", None):
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        for k in sorted(k for k, sc in SCENES.items() if sc.get("phase") == "X"):
            L.dig_scene(k)
        strip = SCENES["X_strip"]["cells"]
        for i, c in enumerate(strip):              # D=1 dug -> 1,2,3,4 (the race staircases the same)
            for k in ("X_race_tar", "X_race_water", "X_race_off"):
                if i:
                    L.dig(SCENES[k]["cells"][i], i)
            if i:
                L.dig(c, i)
        L.dig(X_JUNCTION, 1)                       # X_two's junction is D=2: both rows give to it by gravity

        # The south-row sink clamp is ON by default since 2026-10-15 (b5c8547e8b, owner by card) and caps every pawn on a
        # south-row pit cell at 0.5; the X strip is one row, so X1-X5 read 0.5 at D2..D4 (L1 2026-10-15: 5 FAIL, HARNESS).
        # These rows measure the sink by depth, so they run with the clamp OFF; restore_settings puts the default back.
        L.sset(S_FW, "pitSinkClampEnabled", False)
        # X1 pawn_height_ladder_legible: a hare on D=0..4, read at 0 ticks through the REAL DrawPos.
        hares, got = [], []
        for d, c in enumerate([X_WALK] + strip):
            r = B.call("jawa/spawn_pawn", kindDef="Hare", faction="none", x=c[0], z=c[1], count=1)
            if not r.get("success"):
                raise Abort("spawn hare on %s: %r" % (c, r))
            hares.append((d, r["pawns"][0]["id"]))
        bad, ok_all = [], True
        for d, pid in hares:
            ok, kv, txt = _proof(B, "ProofPawnSink", pid)
            ok_all &= ok
            got.append("D%s %s/%s" % (kv.get("depth"), kv.get("sink"), kv.get("drawDz")))
            if not _sink_ok(kv, d):
                bad.append("D%d: %s" % (d, txt[:120]))
        if not ok_all:
            L.row("X1_pawn_height_ladder", False, "HARNESS", "ProofPawnSink unreadable: %s" % got, status="UNMEASURED")
        else:
            L.row("X1_pawn_height_ladder", not bad, "MOD", bad[:3] or "sink/drawDz by depth (0.3/level PROVISIONAL, "
                  "strictly deeper each step): %s" % "; ".join(got))
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

        # X2/X3/X4: a colonist WALKS the strip D0 -> D4 (own faction: the carve-out, no capture) and back.
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=X_WALK[0], z=X_WALK[1], count=1)
        if not r.get("success"):
            raise Abort("spawn colonist for X: %r" % r)
        col = r["pawns"][0]["id"]
        # The strip's D=4 end carries a lowered ladder: pathing refuses a ladderless open pit (FLOWWORKS_PIT_FALL_ONLY_FORCED_1),
        # so the colonist climbs down it. The sink/wall numbers are read exactly as before.
        sb_x = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % tuple(strip[-1]))
        _proof(B, "ProofLadder", "%d,%d,lower" % tuple(strip[-1]))
        okk0, k0, _ = _proof(B, "ProofPawnSink", col)
        o_in = _order_row(B.call("jawa/order_pawn", pawnId=col, x=strip[-1][0], z=strip[-1][1], waitTicks=PIT_WAIT_IN, draft=True), col)
        ok4, k4, t4 = _proof(B, "ProofPawnSink", col)
        o_out = _order_row(B.call("jawa/order_pawn", pawnId=col, x=X_WALK[0], z=X_WALK[1], waitTicks=PIT_WAIT_IN, draft=True), col)
        ok0, k1, t1 = _proof(B, "ProofPawnSink", col)
        # full read 2026-10-19: an unread sink or an order that never ran is "could not ask", not a MOD FAIL
        x_unm = ("ladder not spawned: %s" % str(sb_x)[:200] if not sb_x.get("success") else None) or \
            _orders_unmeasured(walk_in=o_in, walk_out=o_out) or (
            None if (okk0 and ok4 and ok0) else "ProofPawnSink unreadable: %s / %s / %s" % (okk0, t4[:80], t1[:80]))
        if x_unm:
            for rid in ("X2_pawn_lowers_walking_in", "X3_pawn_rises_walking_out", "X4_pit_wall_over_head"):
                L.row(rid, False, "HARNESS", x_unm, status="UNMEASURED")
        else:
            L.row("X2_pawn_lowers_walking_in", o_in.get("arrived") is True and _sink_ok(k0, 0) and _sink_ok(k4, 4), "MOD",
                  "walked D0->D4 arrived %s: sink %s -> %s (drawDz %s)" % (o_in.get("arrived"), k0.get("sink"), k4.get("sink"),
                                                                        k4.get("drawDz")))
            L.row("X3_pawn_rises_walking_out", o_out.get("arrived") is True and _sink_ok(k4, 4) and _sink_ok(k1, 0), "MOD",
                  "walked D4->D0 arrived %s: sink %s -> %s (drawDz %s)" % (o_out.get("arrived"), k4.get("sink"), k1.get("sink"),
                                                                        k1.get("drawDz")))
            try:
                wall = float(k4.get("sink")) / FEET_TO_HEAD
            except (TypeError, ValueError):
                wall = None
            L.row("X4_pit_wall_over_head", _sink_ok(k4, 4) and wall is not None and wall >= 1.2 - 1e-6
                  and abs(float(k4.get("wallOverHead") or 0) - wall) < 1e-3, "MOD",
                  "colonist on D=4 drawn %s cells down; wall over crown %s x a person's height (owner: walls 20%% above "
                  "the head, >= 1.2)" % (k4.get("sink"), k4.get("wallOverHead")))
        B.call("jawa/set_pawn_faction", pawn=col, faction="none")
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

        # X5 slime_occupant_below_surface: slime in the D=4 cell does not lift its occupant.
        okf, tf = _fill_fluid(L, strip[-1], 2, SLIME)
        r = B.call("jawa/spawn_pawn", kindDef="Hare", faction="none", x=strip[-1][0], z=strip[-1][1], count=1)
        ok5, k5, t5 = _proof(B, "ProofPawnSink", r["pawns"][0]["id"]) if r.get("success") else (False, {}, r)
        if not (okf and ok5):
            L.row("X5_slime_occupant_below_surface", False, "HARNESS", "fill %s (%s); sink %s" % (okf, tf, t5), status="UNMEASURED")
        else:
            L.row("X5_slime_occupant_below_surface", _sink_ok(k5, 4) and k5.get("fluid") == SLIME and k5.get("fill") == "2",
                  "MOD", "D=4 cell holding %s F=%s: occupant drawn %s down (dry D=4: %.2f), drawDz %s" % (
                      k5.get("fluid"), k5.get("fill"), k5.get("sink"), 4 * SINK_PER_LEVEL, k5.get("drawDz")))
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

        # X6 fill_fluid_distinct + X7 tar_fill_front_lags_water (+ X7n the toggle): named fluids, gravity only.
        two = SCENES["X_two"]["cells"]
        tar_row, water_row = [c for c in two if c[1] == 74], [c for c in two if c[1] == 76]
        fills = [_fill_fluid(L, c, 1, TAR) for c in tar_row] + [_fill_fluid(L, c, 1, WATER) for c in water_row]
        rt, rw, ro = (SCENES[k]["cells"] for k in ("X_race_tar", "X_race_water", "X_race_off"))
        fills += [_fill_fluid(L, rt[0], 1, TAR), _fill_fluid(L, rw[0], 1, WATER)]
        if not all(f[0] for f in fills):
            L.row("X6_two_fluids_distinct", False, "HARNESS", "ProofFillWithFluid: %s" % [f[1] for f in fills if not f[0]][:3],
                  status="UNMEASURED")
            return
        _xpulse(L, 3)
        ok3, race3, kv3 = _fluid_row(L, rt + rw)
        _xpulse(L, 9)
        okr, rows, kv = _fluid_row(L, two + rt + rw)
        t3, w3 = _level_at(race3, rt), _level_at(race3, rw)
        t12, w12 = _level_at(rows, rt), _level_at(rows, rw)
        # full read 2026-10-19: an unread ProofFluidRow left {} and X6/X7 FAILed as MOD on no reading
        if not (ok3 and okr and race3 and rows):
            for rid in ("X7_tar_front_lags_water", "X6_two_fluids_distinct"):
                L.row(rid, False, "HARNESS", "ProofFluidRow unreadable: after 3 pulses %s (%d cells), after 12 %s (%d cells): %s"
                      % (ok3, len(race3), okr, len(rows), kv or kv3), status="UNMEASURED")
        else:
            L.row("X7_tar_front_lags_water", okr and w3[0] == 3 and t3[0] in (0, 1) and t12[0] == 2 and w12[0] == 3
                  and t12[1] == w12[1] == 1 and t12[2] == [TAR] and w12[2] == [WATER], "MOD",
                  "gravity staircase D1..D4, one level each: after 3 pulses water at step %s, tar at %s; after 12 water %s, "
                  "tar %s (stride 6 PROVISIONAL = 360/60 ticksPerTile); levels %s/%s; pulse %s viscosity %s" % (
                      w3[0], t3[0], w12[0], t12[0], w12[1], t12[1], kv.get("pulse"), kv.get("viscosity")))
            # the levels each row should show after the 3 + 9 pulses, and WHICH fluid reached the dry D=2 junction first, from
            # the engine the game runs started at the map's own pulse count (full read 2026-10-19: the row asserted "water
            # first" always; tar's stride phase decides it, and on a loaded save either can win -- no-mix is the bar)
            try:
                pulse0 = int(kv3.get("pulse")) - 3          # ProofFluidRow prints the map's PulseCount after the first 3
            except (TypeError, ValueError):
                pulse0 = None
            xo = _x_two_oracle(getattr(L, "exact", LIVE_EXACT), tar_row, water_row, pulse0=pulse0 or 0)
            allc = tar_row + water_row + [X_JUNCTION]
            fl_of = lambda c: (rows[c]["fluid"] if rows.get(c, {}).get("f") else None)          # noqa: E731
            want_fl = lambda c: ((xo.fluid.get(c, WATER)) if xo.F.get(c, 0) else None)          # noqa: E731
            cell_bad = [(c, rows.get(c, {}).get("f"), fl_of(c), xo.F.get(c, 0), want_fl(c)) for c in allc
                        if (rows.get(c, {}).get("f"), fl_of(c)) != (xo.F.get(c, 0), want_fl(c))]
            # no-mix: every wet cell of a row holds that row's fluid; the junction holds the one that reached it
            wrong = [c for c in tar_row if fl_of(c) not in (None, TAR)] + [c for c in water_row if fl_of(c) not in (None, WATER)]
            tt = {rows[c]["terrain"] for c in allc if fl_of(c) == TAR}
            wt = {rows[c]["terrain"] for c in allc if fl_of(c) == WATER}
            j = rows.get(X_JUNCTION, {})
            want_j = xo.F[X_JUNCTION]
            L.row("X6_two_fluids_distinct", pulse0 is not None and okr and not wrong and not cell_bad
                  and want_j > 0 and len(tt) == 1 and len(wt) == 1
                  and not (tt & wt) and not any(t.startswith("RM_Channel") for t in tt | wt), "MOD",
                  "tar drawn %s | water drawn %s | junction %s F=%s (oracle %s F=%s: first to reach it fills it; the other "
                  "refused, no-mix) | cells off the oracle %s | wrong-fluid cells %s | map pulse count before %s" % (
                      sorted(tt), sorted(wt), j.get("fluid"), j.get("f"), want_fl(X_JUNCTION), want_j, cell_bad[:3],
                      wrong[:3], pulse0))
        okf, tf = _fill_fluid(L, ro[0], 1, TAR)      # filled only now: ON it would still sit at step 0..1
        L.sset(S_FW, "viscosityEnabled", False)
        try:
            _xpulse(L, 3)
            okn, roff, kvo = _fluid_row(L, ro)
        finally:
            L.sset(S_FW, "viscosityEnabled", True)
        toff = _level_at(roff, ro)
        if not (okn and roff):
            L.row("X7n_viscosity_off", False, "HARNESS", "ProofFluidRow unreadable (%s, %d cells)" % (okn, len(roff)),
                  status="UNMEASURED")
        else:
            L.row("X7n_viscosity_off", okf and toff[0] == 3 and toff[2] == [TAR] and kvo.get("viscosity") == "False", "MOD",
                  "viscosityEnabled OFF: a tar staircase moved like water, step %s after 3 pulses (levels %s, %s)" % (
                      toff[0], toff[1], toff[2]))

        # X8/X9 pit_covered_invisible + seam: a 2x2 woven-scrap deck over a D=4 pit.
        cov = SCENES["X_cover"]["cells"]
        # X8b PIT_COVER_FIX_OCCUPANT_STAYS_BELOW: a colonist already down in the pit at cov[0] when the lid is laid
        occ = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=cov[0][0], z=cov[0][1], count=1)
        sb = B.call("jawa/spawn_batch", ops=";".join("RM_PitCover_WovenScrap:%d,%d" % c for c in cov))
        reads = [_proof(B, "ProofCover", "%d,%d" % c) for c in cov]
        if not sb.get("success") or not all(r[0] for r in reads):
            L.row("X8_cover_hides_pit", False, "HARNESS", "spawn %s; %s" % (sb.get("success"), [r[2] for r in reads][:2]),
                  status="UNMEASURED")
            return
        kvs = [r[1] for r in reads]
        hide = [k for k in kvs if not (k.get("present") == k.get("covered") == "True" and k.get("sprung") == "False"
                                       and k.get("depth") == "4" and k.get("matOk") == "True"
                                       and k.get("printed") == k.get("around") != k.get("cellTerrain"))]
        L.row("X8_cover_hides_pit", not hide, "MOD", hide[:2] or "4 deck cells over D=4 (%s) print %s, the "
              "surrounding surface; gives way: %s" % (kvs[0].get("cellTerrain"), kvs[0].get("printed"), kvs[0].get("inspect")))
        printed = {k.get("printed") for k in kvs}
        around = {k.get("around") for k in kvs}
        L.row("X9_cover_deck_uniform", len(printed) == 1 and None not in printed and printed == around, "MOD",
              "deck prints %s; ring terrain %s (one surface: no seam between deck cells or at the lip; the frame is "
              "still the judge's)" % (sorted(printed), sorted(around)))
        _x8b_cover_occupant(L, cov[0], occ)
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        _x10_canal_fire(L)


FIRE_TYPE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
FLAME, ASH = "RM_LiquidFlame", "Filth_Ash"
FIRE_FAST_BURN_DAYS = 0.02         # burnDaysPerNotch for X10 only: 1,200 ticks per level instead of a day


def _things_at(B, def_name, cells):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    r = B.call("jawa/list_things", defName=def_name, rect="%d,%d,%d,%d" % (min(xs) - 1, min(zs) - 1, max(xs) - min(xs) + 3,
                                                                          max(zs) - min(zs) + 3), limit=200)
    if not r.get("success"):
        return None
    if (r.get("countMatched") or 0) > len(r.get("things") or []):      # a truncated list is not "no more flames"
        return None
    pos = [t.get("position") or t for t in (r.get("things") or [])]    # top-level x/z, or nested under "position"
    cells_ = {(p.get("x"), p.get("z")) for p in pos}
    return None if any(None in c for c in cells_) else cells_          # a thing with no readable cell is no reading


def _x8b_cover_occupant(L, c, occ):
    """PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (owner card 2026-10-21 "Stays below, hidden"): the colonist spawned in the pit at c
    before the lid was laid stays below it 300 ticks later: still on c, beneath, held, sealed (the 2x2 deck covers the whole
    pit), off the lid's load, not drawn, and the lid's inspect line names her."""
    B = L.B
    if not occ.get("success"):
        L.row("X8b_cover_occupant_stays_below", False, "HARNESS", "spawn colonist in the pit: %r" % (str(occ)[:200],),
              status="UNMEASURED")
        return
    B.call("rimworld/step_game_ticks", ticks=300, pauseFirst=True, timeoutMs=60000)
    ok, kv, txt = _proof(B, "ProofBeneath", "%d,%d" % c)
    okc, kc, _ = _proof(B, "ProofCover", "%d,%d" % c)
    if not ok or "beneath" not in kv:
        L.row("X8b_cover_occupant_stays_below", False, "HARNESS", "ProofBeneath unreadable: %s" % txt[:200],
              status="UNMEASURED")
        return
    inspect = kc.get("inspect", "") if okc else ""
    good = (kv.get("pawn") not in (None, "none") and kv.get("covered") == "True" and kv.get("beneath") == "True"
            and kv.get("held") == "True" and kv.get("trapped") == "True" and kv.get("onLoad") == "False"
            and kv.get("hidden") == "True" and "Below,_hidden:" in inspect)
    L.row("X8b_cover_occupant_stays_below", good, "MOD",
          "%s | lid inspect %s (want: still on %d,%d, beneath/held/trapped True, onLoad False, hidden, named under the lid; "
          "a pawn popped up reads pawn=none here or beneath=False)" % (txt, inspect[:160], c[0], c[1]))


def _x10_canal_fire(L):
    """X10 (promoted 2026-10-05 from the extension plot_E_fire): a 1x6 D=1 tar run lit at its far end by
    RM_LiquidFireProof.ProofIgnite (the engine's IgniteNow, same queue a vanilla Fire or a bomb feeds).
    canal_burning: the creeping front (tar 120 ticks/cell) puts a flame on >= 3 run cells and on NO cell off the run;
    canal_fire_persists: still alight 250 ticks later; canal_spent: with burnDaysPerNotch cut to 0.02 for this
    row only (a rate knob, restored in finally) every cell burns to F=0, >= 3 of the 6 are left ashed, nothing alight.
    canal_fire_reaches_reservoir stays in the extension (it needs a tar BODY; the core map's bodies are water)."""
    B = L.B
    run = SCENES["X_fire"]["cells"]
    fills = [_fill_fluid(L, c, 1, TAR) for c in run]
    if not all(f[0] for f in fills):
        L.row("X10_canal_fire", False, "HARNESS", "ProofFillWithFluid: %s" % [f[1] for f in fills if not f[0]][:2],
              status="UNMEASURED")
        return
    # Live 2026-10-05 19:12: unlocked weather turned to rain mid-row and rain (rainDousesLiquidFireEnabled, ON by
    # default) doused one cell before it burned dry -> "F>0 left (134,88)" on a working mod. Pin Clear, locked.
    # Live 19:32 (run 3): even pinned Clear, the rain a weather TRANSITION leaves behind kept refilling and dousing
    # the run (2 of 6 cells burned out in 4,000 ticks). Rain is not this row's subject: both rain couplings OFF for
    # the row (restored in finally; fire_rain in extensions proves the douse on its own).
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    L.sset(S_FW, "rainFillsExcavationsEnabled", False)
    L.sset(S_FW, "rainDousesLiquidFireEnabled", False)
    L.sset(S_FW, "burnDaysPerNotch", FIRE_FAST_BURN_DAYS)
    try:
        ok, _, lit = _proof(B, "ProofIgnite", "%d,%d" % run[-1], typ=FIRE_TYPE)
        if not (ok and lit.startswith("LIT")):
            # full read 2026-10-19: only the mod's own REFUSED answer is a MOD finding; a static_call that could not run
            # (stale DLL, "Type not found") was scored MOD FAIL "refused the light"
            if lit.startswith("REFUSED"):
                L.row("X10_canal_fire", False, "MOD", "a lit tar cell refused the light: %s" % lit[:200])
            else:
                L.row("X10_canal_fire", False, "HARNESS", "ProofIgnite did not run: %s" % lit[:200], status="UNMEASURED")
            return
        # pass 2 (2026-10-19): 850 of 1000 ran with the bridge default timeout; every other step here passes one
        tk0 = L.eng().get("ticksGame")
        B.call("rimworld/step_game_ticks", ticks=750, pauseFirst=True, timeoutMs=120000)
        burn1 = _things_at(B, FLAME, run)
        B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True, timeoutMs=120000)
        burn2 = _things_at(B, FLAME, run)
        tk_burn = (L.eng().get("ticksGame") or 0) - (tk0 or 0)
        if tk_burn < 900:                  # the day-3 symptom: steps that report success and run 0 ticks
            L.row("X10_canal_fire", False, "HARNESS", "the clock did not run: %s of 1000 ticks after the light" % tk_burn,
                  status="UNMEASURED")
            return
        # 6000, not 3000: a burned-out cell takes a level back from its neighbour by flow (tar, stride 6), which
        # relights it and stretches the burn (live 19:53: 5 of 6 spent at 4,000 ticks, the last still alight)
        trace = []                 # (ticks, nextPulseTick, engine pulse interval, F vector): why a burn stalls
        # Live day 3 (2026-10-17): the loop stopped at the first all-F=0 read and 2 cells were still alight. Since P4 a
        # square burns in decilitres and since P3 its F is the whole-notch view, so F=0 is NOT spent: the last part-notch
        # (a sheet) still burns. Spent = F 0, 0 L in every square (ProofReadout) and no flame, or the 6,000-tick cap.
        lit = []
        for _ in range(6):
            B.call("rimworld/step_game_ticks", ticks=1000, pauseFirst=True, timeoutMs=120000)
            e = B.call("jawa/flowworks_engine_state")
            _, fr, _ = _fluid_row(L, run)
            fv = [fr.get(c, {}).get("f") for c in run]
            lit = [_litres(L, c) for c in run]
            trace.append((e.get("ticksGame"), e.get("nextPulseTick"), e.get("pulseIntervalTicks"), "".join(str(f) for f in fv),
                          lit))
            if not any(fv) and not any(lit) and not _things_at(B, FLAME, run):
                break
        burn3 = _things_at(B, FLAME, run)
        ash = _things_at(B, ASH, run)
        ok_rows, rows, _ = _fluid_row(L, run)
        _, _, rep = _proof(B, "ProofReport", " ", typ=FIRE_TYPE)    # " ": static_call reads "" as ZERO args
    finally:
        L.sset(S_FW, "burnDaysPerNotch", 1.0)
        L.sset(S_FW, "rainDousesLiquidFireEnabled", True)
        L.sset(S_FW, "rainFillsExcavationsEnabled", True)
    if None in (burn1, burn2, burn3, ash):        # an unread flame list is not "no flames" (burn3 None read as "none alight")
        L.row("X10_canal_fire", False, "HARNESS", "list_things unreadable: flames %s/%s/%s ash %s" % tuple(
            "?" if x is None else len(x) for x in (burn1, burn2, burn3, ash)), status="UNMEASURED")
        return
    if not (ok_rows and rows):                    # an unread row is not "F>0 left" (full read 2026-10-19)
        L.row("X10_canal_fire", False, "HARNESS", "ProofFluidRow unreadable at the spent read", status="UNMEASURED")
        return
    off_run = sorted((burn1 | burn2) - set(run))
    left = [c for c in run if rows.get(c, {}).get("f", 1) != 0]
    if None in lit:
        L.row("X10_canal_fire", False, "HARNESS", "ProofReadout unreadable on the run (litres %s): 'spent' needs the "
              "decilitres, not F" % lit, status="UNMEASURED")
        return
    left += [c for c, v in zip(run, lit) if v and c not in left]
    ran_total = ((trace[-1][0] if trace else None) or 0) - (tk0 or 0)
    if left and ran_total < 6000 and len(trace) >= 6:     # the cap loop ran its 6 chunks but the clock did not: not "unspent"
        L.row("X10_canal_fire", False, "HARNESS", "the burn window was short: %s ticks ran of ~7000 (F>0 left %s)" % (
            ran_total, left[:3]), status="UNMEASURED")
        return
    parts = [("burning >=3 run cells", len(burn1 & set(run)) >= 3), ("no flame off the run", not off_run),
             ("persists 250 ticks", len(burn2 & set(run)) >= 1), ("spent: all F=0 and 0 L", not left),
             ("spent: ashed", len(ash & set(run)) >= 3), ("spent: none alight", not burn3)]
    L.row("X10_canal_fire", all(p[1] for p in parts), "MOD",
          "%s | flames %d -> %d -> %d, off-run %s, ash %d, F>0 left %s | %s | trace %s" % (
              ", ".join("%s %s" % (n, "ok" if v else "FAIL") for n, v in parts), len(burn1), len(burn2), len(burn3),
              off_run[:3], len(ash & set(run)), left[:3], rep[:120], trace))


def phase_tail(L, args):
    B = L.B
    with L.step("T0_E9_tail", 0):
        r = B.call("jawa/flowworks_set_active_fluid", fluidDefName="RM_Fluid_Tar")
        e = L.eng()
        if r.get("success"):           # it switched: put the map back to water before anything else
            B.call("jawa/flowworks_set_active_fluid", fluidDefName="RM_Fluid_Water", allowAfterClassification=True)
        L.row("T0n_fluid_switch_refused", r.get("success") is False and e.get("activeFluidRaw") == "RM_Fluid_Water", "MOD",
              "set_active_fluid Tar after classification+fill: success=%s, activeFluidRaw %s" % (
                  r.get("success"), e.get("activeFluidRaw")))
        tap = getattr(L, "tap", None)
        if tap is not None:
            logs = tap.since(L.log_base)
        else:
            lg = B.call("rimbridge/list_logs", afterSequence=L.log_base, limit=500, minimumLevel="warning")
            logs = lg.get("logs") or []
        txt = lambda x: (x.get("Message") or "") + " " + (x.get("StackTrace") or "")  # noqa: E731
        errs = [(x.get("Level"), x.get("RepeatCount"), (x.get("Message") or "")[:200]) for x in logs
                if (x.get("Level") or "").lower() in ("error", "exception") and any(m in txt(x) for m in LOG_MARKERS)]
        other = [(x.get("Level"), (x.get("Message") or "")[:120]) for x in logs if (x.get("Level") or "").lower() in ("error", "exception")]
        unbal = [x.get("Message", "")[:200] for x in logs if "does not balance" in txt(x)]
        exc_n = sum(int(x.get("RepeatCount") or 1) for x in logs if "conservation exception" in txt(x))
        alive = _vc().log_alive(B, "E9")
        if tap is not None and tap.lost:
            L.row("E9_log_budget", False, "HARNESS", "%d journal entries scrolled out of RimBridge's 1,000-entry ring between "
                  "two polls (%d polls; gaps %s): the budget did not see the whole run" % (tap.lost, tap.polls, tap.gaps[:6]),
                  status="UNMEASURED")
        elif not alive["alive"]:
            # Live day 3 (2026-10-17): 2,123 warn+ lines were collected and none was shown, and Player.log was overwritten by
            # two relaunches before anyone read it, so the run's one clue to "no pawn moved" was lost. The budget cannot be
            # judged on a dead log, but what WAS collected is evidence: the most frequent distinct lines go in the row.
            top = {}
            for x in logs:
                k = ((x.get("Level") or "?"), (x.get("Message") or "")[:160])
                top[k] = top.get(k, 0) + int(x.get("RepeatCount") or 1)
            worst = sorted(top.items(), key=lambda kv: -kv[1])[:5]
            L._log("    E9 collected warn+ lines (most frequent first): %s" % worst)
            L.row("E9_log_budget", False, "HARNESS", "logging is dead (Verse.Log message cap?): the sentinel warning never "
                  "reached the journal (revive at L2: %s); %d warn+ lines since base; most frequent %s" % (
                      getattr(L, "log_revive", None), len(logs), [(n, lv, m[:110]) for (lv, m), n in worst]),
                  status="UNMEASURED")
        elif exc_n < 1:
            L.row("E9_log_budget", False, "HARNESS", "sanity probe: E7b's expected 'conservation exception' warning not "
                  "seen (%d warn+ lines since base)" % len(logs), status="UNMEASURED")
        else:
            L.row("E9_log_budget", not errs and not unbal and exc_n == 1, "MOD",
                  (errs, unbal, exc_n) if (errs or unbal or exc_n != 1) else
                  "0 FlowWorks errors, 0 ledger imbalances, exactly 1 sanctioned conservation exception; %d other "
                  "error lines %s" % (len(other), other[:3]))


# ============================================================================ the in-memory game (--mock)
class MockBridge(object):
    """A FlowWorks map in memory: PulseOracle as the engine, plus terrain, bodies, settings,
    weather, the scheduler, a log journal and pawn jobs. It lets the live runner be rehearsed
    at 0 game ticks AND be shown red: each FAULT breaks one mechanism the way a MOD defect
    would, and selftest_live_mock() asserts the named row goes non-PASS. Not a model of
    RimWorld beyond what the runner reads."""
    FAULTS = {   # fault -> rows that must NOT pass
        "oscillate": ["G_every_cell_vs_oracle", "E2_channels_fill_every_direction"],
        "pond_sheds_squares": ["E3b_recession_shipped"],
        "lake_floor_on_site": ["S3_classification"],      # the site's deepBedsEnabled pin is lost: painted ponds get a P11 shelf   # the pre-POND_DEPTH whole-square recession is back on a still pond
        "budget_ignored": ["E3_budget_exhaustion"],
        "roof_ignored": ["E6_rain_fills_unroofed"],
        "sink_toggle_ignored": ["E5n_sinks_off"],
        "engine_toggle_ignored": ["E4_engine_off"],
        "fillin_leak": ["E7a_fillin_displaces"],
        "flowworks_error": ["E9_log_budget"],
        "dll_stale": ["L2_tier_live"],
        "no_clamp": ["E1b_pulse_clamp"],
        "sticky_ignored": ["S5_sticky_limitless"],
        "clamp_broken": ["S2_fill_clamp"],
        "dig_never": ["E8_player_dig"],
        "fluid_switch_allowed": ["T0n_fluid_switch_refused"],
        "settings_drift": ["L2_tier_live"],
        "rain_toggle_ignored": ["E6n_rain_toggle_off"],
        "deepen_gate_ignored": ["S6_digToDepth_gate"],
        "workgiver_blind": ["J_workgiver_selection"],
        "workgiver_greedy": ["J_workgiver_selection"],
        "worktype_disabled_once": [],    # no row may go red: the run must re-roll the pawn, not abort
        "pit_holder_spawned": ["S1p_pit_is_grid_only"],                # the retired holder Thing is back
        "pit_holds_any": ["P1_width_matrix", "P2_fillin_releases_large"],   # width rule ignored
        "pit_no_veto": ["P1_width_matrix", "P3_walk_in_held"],         # held pawn can still reach / walk out
        "pit_no_fall": ["P3f_forced_entry_falls"],                     # a forced landing takes no descent / no damage
        "pit_forced_stays_held": ["P4f_ladder_frees_forced"],          # the ladder does not free a forced-in pawn
        "pit_carveout_ignored": ["P5n_own_faction_carveout"],          # own colonists captured anyway
        # phase X (promoted 2026-10-05): each breaks one landed feature the way a MOD defect would
        "ladder_raise_ignored": ["P4b_ladder_raised_strands"],         # RM_CompLadder.raised not read by the trap
        "sink_flat": ["X1_pawn_height_ladder", "X2_pawn_lowers_walking_in", "X3_pawn_rises_walking_out",
                      "X4_pit_wall_over_head", "X5_slime_occupant_below_surface"],   # draw-offset patch not applied
        "slime_lifts": ["X5_slime_occupant_below_surface"],            # fill raises the occupant
        "viscosity_ignored": ["X7_tar_front_lags_water"],              # tar flows at water's pace
        "viscosity_toggle_ignored": ["X7n_viscosity_off"],             # OFF still slows tar
        "fluids_look_same": ["X6_two_fluids_distinct"],                # one fill terrain for every fluid
        "cover_shows_hole": ["X8_cover_hides_pit", "X9_cover_deck_uniform"],   # cover prints the pit
        "cover_lifts_occupant": ["X8b_cover_occupant_stays_below"],    # a lid laid over a pit occupant lifts her onto it
        "fire_never_spreads": ["X10_canal_fire"],                     # the front never leaves the lit cell
        "fire_never_burns": ["X10_canal_fire"],                       # a burning cell never spends its liquid
        "fire_no_ash": ["X10_canal_fire"],                            # a spent cell is not left scorched
        # harness negatives (2026-10-11 code review): each is a reading the runner once turned into a PASS or a crash
        "flame_list_late_blind": ["X10_canal_fire"],                   # list_things fails at the spent read: not "none alight"
        "order_ignored_pit": ["P3_walk_in_held", "P3f_forced_entry_falls"],   # an order into the pit never taken, 0 ticks
        # pass-2 harness review (2026-10-19): P3f folded an unmeasurable control into a MOD FAIL; P4f PASSed a forced pawn
        # that was never held ("freed" from nothing). FAULT_STATUS pins the exact status each must now read.
        "forced_control_unmeasured": ["P3f_forced_entry_falls"],      # P3f's control order is never taken (0 ticks)
        "forced_lands_free": ["P3f_forced_entry_falls", "P4f_ladder_frees_forced"],   # the forced pawn lands unheld
        "transient_B_divergence": ["G_every_cell_vs_oracle"],          # a non-E3 cell diverges mid phase B's 10 pulses
        "engine_lost_late": ["ABORT"],                                 # engine_state dies in the tail: rows must survive
        # 2026-10-11 re-review: each once read as PASS (or drove on) with no reading behind it
        "preflight_crash": ["ABORT"],                  # type_probe reply unreadable: the preflight must abort, not drive on
        "pulse_drops_twins": ["E2_twins_identical"],   # flowworks_pulse omits both E2 twins: None == None is no reading
        "cover_no_printed": ["X9_cover_deck_uniform"],  # ProofCover without printed=/around=: {None} == {None}
        # full read 2026-10-19 (each once read PASS on no reading, scored MOD on no reading, or hung the run)
        "prefill_refused": ["E7a_fillin_displaces", "E7b_overflow_sanctioned"],   # E7's prefill never written: E7a 0 -> 0 PASSed
        "ticks_frozen": ["E1c_cadence_real_scheduler", "E4_engine_on_scheduled", "P3f_forced_entry_falls", "P4_ladder_frees",
                         "P5n_own_faction_carveout", "X2_pawn_lowers_walking_in", "X10_canal_fire"],   # steps run 0 ticks (day 3)
        "ignite_type_missing": ["X10_canal_fire"],      # ProofIgnite's type absent (stale DLL): was MOD "refused the light"
        "fluid_row_blind": ["X6_two_fluids_distinct", "X7_tar_front_lags_water", "X7n_viscosity_off", "X10_canal_fire"],
        "list_pawns_blind": ["L4_site_ready"],          # list_pawns fails: was "0 pawns, none in the plots"
        "roof_read_blind": ["E6_roof_readback"],        # get_roof_batch fails: was a SITE FAIL
        "save_pulse_count": [],     # no row may go red: the map's own PulseCount (a loaded save) only shifts the tar stride
    }
    FAULT_STATUS = {"forced_control_unmeasured": {"P3f_forced_entry_falls": "UNMEASURED"},
                    "forced_lands_free": {"P3f_forced_entry_falls": "FAIL", "P4f_ladder_frees_forced": "UNMEASURED"},
                    "prefill_refused": {"E7a_fillin_displaces": "UNMEASURED", "E7b_overflow_sanctioned": "UNMEASURED"},
                    "ticks_frozen": {r: "UNMEASURED" for r in (
                        "E1c_cadence_real_scheduler", "E4_engine_off", "E4_engine_on_scheduled", "P3f_forced_entry_falls",
                        "P4_ladder_frees", "P5n_own_faction_carveout", "X2_pawn_lowers_walking_in",
                        "X3_pawn_rises_walking_out", "X4_pit_wall_over_head", "X10_canal_fire")},
                    "ignite_type_missing": {"X10_canal_fire": "UNMEASURED"},
                    "fluid_row_blind": {"X6_two_fluids_distinct": "UNMEASURED", "X7_tar_front_lags_water": "UNMEASURED",
                                        "X7n_viscosity_off": "UNMEASURED", "X10_canal_fire": "UNMEASURED"},
                    "list_pawns_blind": {"L4_site_ready": "UNMEASURED"},
                    "roof_read_blind": {"E6_roof_readback": "UNMEASURED"},
                    "save_pulse_count": {"X6_two_fluids_distinct": "PASS", "X7_tar_front_lags_water": "PASS"}}
    ABORTING = ("settings_drift", "dll_stale", "engine_lost_late", "preflight_crash")   # faults whose run aborts BY DESIGN

    def __init__(self, faults=()):
        self.faults = set(faults)
        self.n = 0
        self.tick = 1
        self.settings = {t: dict(f) for t, f in _SETTINGS.items()}
        if "settings_drift" in self.faults:
            self.settings[S_FW]["flowPerPulse"] = 2.0
        self.terrain = {}
        self.roof = set()
        # the shipped engine: exact-level water (levelExactEnabled); "oscillate" replays the pre-fix notch engine
        exact = LIVE_EXACT and "oscillate" not in self.faults
        self.o = PulseOracle(MAP_W, MAP_H, {}, {}, sink_band=SINK_BAND,
                             algo="old" if "oscillate" in self.faults else "fixed", recession=True,
                             level_exact=exact, **CREEP_LIVE)
        if "save_pulse_count" in self.faults:     # a loaded save carries its own scribed PulseCount, not 0
            self.o.pulse_n = 1
        self.next_pulse = self.tick + PULSE_SHIPPED
        self.weather, self.weather_age = "Clear", 0
        self.logs = [dict(Sequence=1, Level="warning", Message="[RimBridge] STARTUP_TIMING mock", RepeatCount=1)]
        self.jobs = {}            # cell -> [kind, work_left]
        self.prio = {}            # pawn id -> Mining priority (0 until set_work_priority)
        self.fluid = "RM_Fluid_Water"
        self.classified = {}      # cell -> body name
        self.body_seq = 0
        self.sink_total = 0.0
        self.overflow = 0.0
        self.pawns = []
        self.fill_written = False
        self.mp = {}              # pit model: pawn id -> dict(kind, pos, faction, bs, drafted)
        self.ladders = set()
        self.raised = set()       # ladders whose RM_CompLadder.raised is set (ProofLadder)
        self.covers = set()       # cells holding a pit cover (spawn_batch RM_PitCover_*)
        self.beneath = set()      # pawn ids a lid was laid over (PIT_COVER_FIX_OCCUPANT_STAYS_BELOW)
        self.descents = []
        self.landed_free = set()  # fault forced_lands_free: forced pawns the trap does not hold
        self.spawned_at = {}
        self.jumpers = set()      # own colonists forced in (RM_SuperdeepTrap.OnForcedDescent -> AddJumper)
        self.fire, self.fire_pend, self.ash = {}, {}, set()   # X10 fire model: cell -> burn acc / due tick; ashed cells
        self.flame_lists = 0      # RM_LiquidFlame list_things calls (flame_list_late_blind)
        self.engine_lost = False  # engine_lost_late: set by the tail's set_active_fluid call

    # ---- pit model (SUPERDEEP_HOLDER_RETIRE_1): the grid trap rule over the oracle's D map
    PIT_BS = {"Hare": 0.2, "Muffalo": 2.4, "Colonist": 1.0}

    def d4(self, c):
        return self.o.D.get(c, 0) >= 4

    def pit_cells(self):
        return [c for c, d in self.o.D.items() if d >= 4]

    def captured(self, p):
        return p["faction"] != "player" or p.get("id") in self.jumpers or (self.S("superdeepCapturesOwnFaction")
                                            and "pit_carveout_ignored" not in self.faults) \
            or "pit_carveout_ignored" in self.faults

    def held(self, p, c=None):
        c = p["pos"] if c is None else c
        cells = self.pit_cells()
        bs = 0.0 if "pit_holds_any" in self.faults else p["bs"]
        lad = c in self.ladders and (c not in self.raised or "ladder_raise_ignored" in self.faults)
        if p.get("id") in self.jumpers and "pit_forced_stays_held" in self.faults:
            lad = False
        if p.get("id") in self.landed_free:
            return False
        return pit_held(cells, c, bs, ladder=lad, captured=self.captured(p),
                        rule=self.S("superdeepCaptureEnabled") and self.S("ladderRequiredToExitEnabled"))

    def comp4(self, c):
        seen, q = {c}, [c]
        while q:
            cur = q.pop()
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (cur[0] + dx, cur[1] + dz)
                    if n not in seen and self.d4(n):
                        seen.add(n)
                        q.append(n)
        return seen

    def trapped(self, p):
        if "pit_no_veto" in self.faults or not self.held(p):
            return False
        return all(self.held(p, c) for c in self.comp4(p["pos"]))

    def t_jawa_flowworks_pit_report(self, x, z):
        c = (x, z)
        comp = self.comp4(c) if self.d4(c) else set()
        lip = {(a[0] + dx, a[1] + dz) for a in comp for dx in (-1, 0, 1) for dz in (-1, 0, 1)} - comp
        rows = []
        for pid, p in self.mp.items():
            if p["pos"] != c:
                continue
            tr = self.trapped(p)
            rows.append(dict(id=pid, def_=p["kind"], spawned=True, dead=False, downed=False, bodySize=p["bs"],
                             requiredWidth=required_width(p["bs"]), captured=self.captured(p), jumper=False,
                             held=self.held(p),
                             lipCells=len(lip), lipReachable=0 if tr else len(lip), canReachMapEdge=not tr))
        return dict(success=True, cell=dict(x=x, z=z), depthRaw=self.o.D.get(c, 0), fillRaw=self.o.F.get(c, 0),
                    isSuperdeep=self.d4(c), pitWidth=measured_pit_width(self.pit_cells(), c) if self.d4(c) else 0,
                    hasLadder=c in self.ladders, hasSpikes=None, room=None, pawns=rows,
                    legacyHolders=[dict(id="X", def_="RM_SuperdeepPit")] if ("pit_holder_spawned" in self.faults and self.d4(c)) else [],
                    descentCount=len(self.descents), recentDescents=list(self.descents[-32:]))

    def t_jawa_set_pawn_age(self, pawn=None, biologicalYears=-1.0, **kw):
        return dict(success=pawn in self.mp)

    def t_jawa_set_pawn_faction(self, pawn=None, faction=None, **kw):
        if pawn in self.mp:
            self.mp[pawn]["faction"] = faction
        return dict(success=pawn in self.mp)

    def t_jawa_spawn_batch(self, ops, **kw):
        for op in ops.split(";"):
            d, xy = op.split(":")
            x, z = map(int, xy.split(",")[:2])
            if d == "RM_Ladder":
                self.ladders.add((x, z))
            elif d.startswith("RM_PitCover_"):
                self.covers.add((x, z))
                if "cover_lifts_occupant" not in self.faults:      # PIT_COVER_FIX_OCCUPANT_STAYS_BELOW
                    self.beneath.update(self.spawned_at.get((x, z), []))
        return dict(success=True, thingsPlaced=1)

    def t_jawa_order_pawn(self, pawnId, x=-1, z=-1, waitTicks=300, draft=True, **kw):
        p = self.mp[pawnId]
        dest, start = (x, z), p["pos"]
        forced = self.spawned_at.get(tuple(PIT_SPOTS["P_forced"]), [])[1:2]      # the 2nd colonist on that spot
        if ("order_ignored_pit" in self.faults or ("forced_control_unmeasured" in self.faults and pawnId in forced)) \
                and self.d4(dest):
            return dict(success=False, ticksElapsed=0, pawns=[dict(
                id=pawnId, start=dict(x=start[0], z=start[1]), end=dict(x=start[0], z=start[1]),
                arrived=False, moved=False, canReach=True, orderAccepted=False)])
        if "ticks_frozen" in self.faults:          # the order is taken but the game never ticks: nobody moves
            return dict(success=False, ticksElapsed=0, pawns=[dict(
                id=pawnId, start=dict(x=start[0], z=start[1]), end=dict(x=start[0], z=start[1]),
                arrived=False, moved=False, canReach=True, orderAccepted=True)])
        tr = self.trapped(p)
        can = not (tr and dest not in self.comp4(start))
        # RM_PitPathing (FLOWWORKS_PIT_FALL_ONLY_FORCED_1): no way down into an open D=4 cell but a usable ladder in its pit
        lad = self.d4(dest) and any(c in self.ladders and (c not in self.raised or "ladder_raise_ignored" in self.faults)
                                    for c in self.comp4(dest))
        if self.d4(dest) and not self.d4(start) and not lad and "pit_no_veto" not in self.faults:
            can = False
        if can:
            if self.d4(dest) and not self.d4(start) and not lad and self.captured(p) and "pit_no_fall" not in self.faults \
                    and self.S("superdeepCaptureEnabled"):
                self.descents.append("%s@%d,%d t=%d fall=4.8" % (pawnId, x, z, self.tick))
            p["pos"] = dest
        self.tick += 60
        return dict(success=p["pos"] == dest, ticksElapsed=60, pawns=[dict(
            id=pawnId, start=dict(x=start[0], z=start[1]), end=dict(x=p["pos"][0], z=p["pos"][1]),
            arrived=p["pos"] == dest, moved=p["pos"] != start, canReach=can, orderAccepted=True)])

    # ---- helpers
    def S(self, f):
        return self.settings[S_FW][f]

    def water(self, c):
        return self.terrain.get(c) == "WaterShallow" and c not in self.o.receded

    def rain_rate(self):
        return min(1.0, self.weather_age / 4000.0) if self.weather == "Rain" else 0.0

    def sync(self):
        o = self.o
        o.budget = self.S("sourceBudgetEnabled") and "budget_ignored" not in self.faults
        o.recession = self.S("recessionEnabled")
        o.sink_band = SINK_BAND if (self.S("edgeSinksEnabled") or "sink_toggle_ignored" in self.faults) else None
        o.rain_on = self.S("rainFillsExcavationsEnabled") or "rain_toggle_ignored" in self.faults
        o.rain_per, o.rain_rate = float(self.S("rainFillPerPulse")), self.rain_rate()
        o.roofed = set() if "roof_ignored" in self.faults else set(self.roof)
        o.viscosity = ("viscosity_ignored" not in self.faults) and (
            self.S("viscosityEnabled") or "viscosity_toggle_ignored" in self.faults)

    def do_pulse(self):
        self.sync()
        d0 = self.o.drained_levels()
        self.o.pulse()
        self.sink_total += self.o.drained_levels() - d0

    def interval(self):
        v = int(round(float(self.S("pulseIntervalTicks"))))
        return v if "no_clamp" in self.faults else max(60, v)

    def classify(self, c):
        if c in self.classified:
            return self.classified[c]
        if not self.water(c):
            return None
        seen, q = {c}, [c]
        while q:
            a = q.pop()
            for dx, dz in CARDINAL:
                n = (a[0] + dx, a[1] + dz)
                if n not in seen and self.o.inb(n) and self.water(n):
                    seen.add(n)
                    q.append(n)
        self.body_seq += 1
        name = "B%d" % self.body_seq
        edge = any(edge_distance(x) == 0 for x in seen)
        sticky = self.S("stickyLimitlessEnabled") or "sticky_ignored" in self.faults
        # RM_LiquidStock: wetnessCutoffEnabled ON (shipped) = IsLimitlessByWetness (edge always; inland at the tile's cutoff,
        # never under WETNESS_CUTOFF_MIN_CELLS); OFF = the older edge + minLimitlessBodyCells rule
        if self.settings[S_FW].get("wetnessCutoffEnabled", True):
            lim = sticky and (edge or len(seen) >= WETNESS_CUTOFF_MIN_CELLS)
        else:
            lim = sticky and edge and len(seen) >= 50
        # beds: WaterShallow = ShallowBedLevels; with deepBedsEnabled ON a LIMITED pond records the P11 lake floor at
        # classification, modelled here as a 0.5 m outer ring (the shelf day 3 measured live: caps 1/4/5/56/100; the shelf
        # default is off since 2026-10-18, so with deepBedsEnabled on and lakeShoreShelfMetres 0 this model is unmeasured)
        shelf = not lim and ((self.S("deepBedsEnabled") and (self.settings[S_FW].get("lakeShoreShelfMetres") or 0) > 0)
                             or "lake_floor_on_site" in self.faults)
        beds = {}
        for x in seen:
            ring = any((x[0] + dx, x[1] + dz) not in seen for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            beds[x] = 1 if (shelf and ring) else POND_LEVELS_PER_CELL
        self.o.beds.update(beds)
        cap = float(sum(beds.values()))
        self.o.bodies[name] = dict(limitless=lim, stock=0.0 if lim else cap, capacity=None if lim else cap,
                                   cells=sorted(seen, key=self.o.idx), id=self.body_seq)
        for x in seen:
            self.classified[x] = name
            self.o.src[x] = name
        return name

    def body_rec(self, name):
        b = self.o.bodies[name]
        rec = b.get("receded", [])
        if "pond_sheds_squares" in self.faults and not b["limitless"] and b.get("capacity"):
            per = float(b["capacity"]) / len(b["cells"])
            rec = b["cells"][:len(b["cells"]) - max(1, int(self.o.stock_of(name) // per))]
        return dict(id=b["id"], limitless=b["limitless"], stock=self.o.stock_of(name) if not b["limitless"] else 0.0,
                    capacity=b["capacity"] or 0.0, cellCount=len(b["cells"]), recededCount=len(rec),
                    activeCellCount=len(b["cells"]) - len(rec), truncated=False)

    def terrain_of(self, c):
        d = self.o.D.get(c, 0)
        if d:
            return ["RM_Channel_Empty", "RM_Channel_Mid", "RM_Channel_Deep", "RM_Channel_Superdeep"][d - 1]
        if c in self.o.receded:
            return "Soil"
        return self.terrain.get(c, "Sand")

    def is_sink(self, c):
        return self.o.exc(c) and edge_distance(c) < SINK_BAND and (
            self.S("edgeSinksEnabled") or "sink_toggle_ignored" in self.faults)

    def put(self, c, f):
        """Write a whole-notch fill: F and, for the exact engine, its decilitres (W = F x U), as the game's drive tool does."""
        self.o.F[c] = f
        self.o.W[c] = f * level_water.U

    def fill_in(self, c):
        """RM_MapComponent_Excavation.FillIn (CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED): one level shallower, the water above
        the new floor displaced in dL into the cardinal neighbours' room, the rest a sanctioned overflow."""
        U = level_water.U
        if not self.o.level_exact:          # the notch engine keeps F only: derive the dL view from it first
            for x in [c] + [(c[0] + dx, c[1] + dz) for dx, dz in CARDINAL]:
                if x in self.o.F:
                    self.o.W[x] = self.o.F[x] * U
        d, w = self.o.D.get(c, 0), self.o.W.get(c, self.o.F.get(c, 0) * U)
        nd = d - 1
        disp = max(0, w - max(nd, 0) * U)
        if nd <= 0:
            self.o.D.pop(c, None)
            self.o.F.pop(c, None)
            self.o.W.pop(c, None)
        else:
            self.o.D[c] = nd
            self.o.W[c] = w - disp
            self.o.F[c] = self.o.W[c] // U
        if disp and "fillin_leak" not in self.faults:
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                if disp and self.o.exc(n):
                    room = self.o.D[n] * U - self.o.W.get(n, 0)
                    give = min(room, disp)
                    if give > 0:
                        self.o.W[n] = self.o.W.get(n, 0) + give
                        self.o.F[n] = self.o.W[n] // U
                        disp -= give
            if disp:
                self.overflow += disp / float(U)
                self.log("warning", "[RimMandrake.FlowWorks] conservation exception: %.1f fill-units overflowed" % (disp / float(U)))

    def log(self, level, msg):
        self.logs.append(dict(Sequence=len(self.logs) + 1, Level=level, Message=msg, RepeatCount=1))

    # ---- the bridge surface the runner uses
    def call(self, tool, **kw):
        self.n += 1
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        if fn is None:
            return {"success": False, "error": "mock: no tool " + tool}
        return fn(**kw)

    def t_rimworld_get_ui_state(self):
        return dict(success=True, programState="Playing")

    def t_rimworld_go_to_main_menu(self):
        return dict(success=True)

    def t_rimworld_start_debug_game_ready(self, **kw):
        self.__init__(self.faults)
        return dict(success=True)

    def t_jawa_running_mods(self, assembly=None, details=True):
        return dict(success=True, count=3, packageIds=["ludeon.rimworld", "brrainz.harmony", "mandrake.rm.flowworks"],
                    assembly=dict(name=assembly, matchCount=1, matches=[dict(sha256="0" * 64)]))

    def t_jawa_map_info(self):
        return dict(success=True, sizeX=MAP_W, sizeZ=MAP_H, mapBiome="MockDesert")

    def t_jawa_name_colony(self):
        return dict(success=True)

    def t_rimbridge_list_logs(self, limit=50, minimumLevel="warning", afterSequence=0):
        return dict(logs=[x for x in self.logs if x["Sequence"] > afterSequence][::-1][:limit])

    def t_jawa_type_probe(self, typeName):
        if "preflight_crash" in self.faults:
            return None                                   # a reply the preflight cannot read (tp.get -> AttributeError)
        sha = _sha256(os.path.join(MOD, "Assemblies", "RimMandrakeFlowWorks.dll"))
        return dict(success=True, assemblyFileSha256=("0" * 64) if "dll_stale" in self.faults else sha,
                    mvidMatchesFile=True, assemblyLocation="mock")

    def t_jawa_get_defs(self, defs, fields=None):
        pc = {"RM_Channel_Empty": 30, "RM_Channel_Mid": 45, "RM_Channel_Deep": 80, "RM_Channel_Superdeep": 300}
        out = [dict(defName=d.split("/")[1], found=True, fields=dict(pathCost=pc[d.split("/")[1]])) for d in defs.split(";")]
        return dict(success=True, foundCount=len(out), notFound=[], defs=out)

    def t_jawa_mod_settings_field(self, typeName, action="get", field=None, value=None):
        if action == "set":
            cur = self.settings[typeName][field]
            self.settings[typeName][field] = (str(value).lower() == "true") if isinstance(cur, bool) else float(value)
        return dict(success=True, value=str(self.settings[typeName][field]))

    def t_jawa_flowworks_engine_state(self):
        if self.engine_lost:
            return dict(success=False, error="mock: no current map")
        return dict(success=True, ticksGame=self.tick, nextPulseTick=self.next_pulse, pulseIntervalTicks=self.interval(),
                    ticksUntilNextPulse=self.next_pulse - self.tick, depthEngineEnabled=self.S("depthEngineEnabled"),
                    excavatedCellCount=sum(1 for c in self.o.D if self.o.exc(c)),
                    superdeepCellCount=sum(1 for c in self.o.D if self.o.D[c] == 4),
                    bodyCount=len(self.o.bodies), activeFluidRaw=self.fluid if self.classified or self.fill_written else None,
                    sinkTransferredTotal=self.sink_total, overflowDestroyedTotal=self.overflow,
                    rainAccumulator=self.o.rain_acc)

    def t_jawa_weather_get(self):
        return dict(success=True, weather=dict(current=self.weather, rainRate=self.rain_rate()))

    def t_jawa_weather_set(self, weather=None, lockWeather=False, unlock=False):
        if weather and weather != self.weather:
            self.weather, self.weather_age = weather, 0
        return dict(success=True)

    def t_jawa_list_pawns(self, limit=500, **kw):
        if "list_pawns_blind" in self.faults:
            return dict(success=False, error="mock: list_pawns failed")
        return dict(success=True, pawns=[dict(id="P%d" % i, position=dict(x=125 + i, z=125)) for i in range(3)] + self.pawns)

    def t_jawa_destroy_bulk(self, filter=None, dryRun=True):
        gone = [k for k, p in self.mp.items() if p["faction"] != "player"] if filter == "nonColonists" else []
        if not dryRun:
            for k in gone:
                self.mp.pop(k)
        return dict(success=True, matchedCount=len(gone))

    def t_jawa_clear_area(self, rect, dryRun=True):
        x, z, w, h = map(int, rect.split(","))
        if not dryRun:
            for i in range(w):
                for j in range(h):
                    self.roof.discard((x + i, z + j))
        return dict(success=True)

    def _ops(self, ops):
        for op in ops.split(";"):
            d, xyz = op.split(":")
            x, z, w, h = map(int, xyz.split(","))
            yield d, [(x + i, z + j) for i in range(w) for j in range(h)]

    def t_jawa_set_terrain_batch(self, ops, **kw):
        for d, cells in self._ops(ops):
            for c in cells:
                self.terrain[c] = d
        return dict(success=True)

    def t_jawa_set_roof_batch(self, ops, **kw):
        for d, cells in self._ops(ops):
            for c in cells:
                (self.roof.discard if d in ("None", "Clear") else self.roof.add)(c)
        return dict(success=True)

    def t_jawa_get_roof_batch(self, rects):
        if "roof_read_blind" in self.faults:
            return dict(success=False, error="mock: get_roof_batch failed")
        ops = []
        for r in rects.split(";"):
            x, z, w, h = map(int, r.split(","))
            for i in range(w):
                for j in range(h):
                    ops.append("%s:%d,%d,1,1" % ("RoofConstructed" if (x + i, z + j) in self.roof else "None", x + i, z + j))
        return dict(success=True, ops=";".join(ops))

    def t_jawa_flowworks_excavation_rect(self, x, z, w, h, onlyNonZero=False, **kw):
        rows = []
        for j in range(h):
            for i in range(w):
                c = (x + i, z + j)
                d, f = self.o.D.get(c, 0), self.o.F.get(c, 0)
                src = self.water(c) and not d
                rows.append(dict(x=c[0], z=c[1], d=d, f=f, isExcavated=d > 0, isSource=src, isSink=self.is_sink(c),
                                 terrain=self.terrain_of(c)))
        return dict(success=True, rows=rows)

    def t_jawa_flowworks_excavation_drive(self, x, z, deepenLevels=0, setFill=-1, fillInLevels=0):
        c = (x, z)
        for _ in range(fillInLevels):
            self.fill_in(c)
        if fillInLevels:
            return dict(success=True, depth=self.o.D.get(c, 0), fill=self.o.F.get(c, 0), fillSet=False)
        if deepenLevels:
            self.o.dig(c, deepenLevels)
        fill_set = False
        if "prefill_refused" in self.faults and c in set(SCENES["E7a_fillin"]["cells"] + SCENES["E7b_overflow"]["cells"]):
            setFill = -1                            # the write never takes (fillSet false), as a refusing engine would
        if setFill >= 0 and self.o.exc(c):
            self.put(c, setFill if "clamp_broken" in self.faults else min(setFill, self.o.D[c]))
            fill_set = True
            self.fill_written = True
        return dict(success=True, depth=self.o.D.get(c, 0), fill=self.o.F.get(c, 0), fillSet=fill_set)

    def t_jawa_flowworks_body_report(self, x, z, classify=True):
        name = self.classify((x, z)) if classify else self.classified.get((x, z))
        return dict(success=True, body=self.body_rec(name) if name else None)

    def t_jawa_flowworks_job_probe(self, x, z, kind="dig", pawnId=None, forced=False):
        """The mod's designator + WorkGiver logic (Designator_DigCanal.CanDesignateCell,
        WorkGiver_*Canal.HasJobOnCell) over the mock's cells and designations."""
        c = (x, z)
        d = self.o.D.get(c, 0)
        des = {"dig": "RM_DigCanal", "fillin": "RM_FillInCanal"}[kind]
        present = (self.jobs.get(c) or [None])[0] == des
        if kind == "dig":
            if d >= 4:
                acc, why = False, "Already 2 m deep: the deepest digging goes (2 m, set in this mod's settings)."  # mirrors Designator_DigCanal (6f6eb1d262; phase S runs at the 2 m cap)
            elif d and not self.S("digToDepthEnabled") and "deepen_gate_ignored" not in self.faults:
                acc, why = False, "Deepening is switched off in this mod's settings."
            else:
                acc, why = True, None
        else:
            acc, why = (d > 0), (None if d > 0 else "Nothing to fill in.")
        wg = pw = None
        if pawnId:
            has = (present and "workgiver_blind" not in self.faults) or ("workgiver_greedy" in self.faults and d > 0)
            cells = [k for k, j in self.jobs.items() if j[0] == des]
            wg = dict(def_="mock", shouldSkip=not cells, cellInPotentialWorkCells=(c in cells) or
                      ("workgiver_greedy" in self.faults and d > 0), hasJobOnCell=has,
                      jobDef=(des + "Job") if has else None, designationDeletedByWorkGiver=False, designationRestored=False)
            pr = self.prio.get(pawnId, 0)      # a fresh colonist's Mining may be OFF (rerun 1, 2026-10-02)
            pw = dict(id=pawnId, workType="Mining", workTypeDisabled=False, workActive=pr > 0, priority=pr,
                      giverInNormalList=pr > 0, missingCapacity=None, canReach=True)
        return dict(success=True, kind=kind, cell=dict(x=x, z=z), fogged=False, terrain=self.terrain_of(c),
                    designationPresent=present, designator=dict(accepted=acc, reason=why), workGiver=wg, pawn=pw,
                    ticksGame=self.tick)

    def t_jawa_flowworks_pulse(self, count=1, x=0, z=0, w=0, h=0, includeBodies=True, ignoreEngineToggle=False):
        if not self.S("depthEngineEnabled") and not ignoreEngineToggle:
            return dict(success=False, refused=True)
        cells = sorted((c for c in self.o.D if self.o.exc(c)), key=self.o.idx)
        if "pulse_drops_twins" in self.faults:
            twins = set(SCENES["E2_east_A"]["cells"]) | set(SCENES["E2_east_B"]["cells"])
            cells = [c for c in cells if c not in twins]
        snap = lambda p: dict(pulse=p, fill=[self.o.F.get(c, 0) for c in cells], depth=[self.o.D.get(c, 0) for c in cells],  # noqa: E731
                              bodies=[self.body_rec(n) for n in self.o.bodies])
        pulses = [snap(0)]
        for p in range(1, count + 1):
            self.do_pulse()
            pulses.append(snap(p))
        if "transient_B_divergence" in self.faults and count == 10:     # phase B's window only
            c = SCENES["E2_east_A"]["cells"][0]
            if c in cells:
                i = cells.index(c)
                pulses[3]["fill"][i] = pulses[3]["fill"][i] + 1                  # one read, one pulse, then back
        return dict(success=True, cells=[dict(x=c[0], z=c[1]) for c in cells], pulses=pulses, pulsesRun=count,
                    ticksBefore=self.tick, ticksGame=self.tick, nextPulseTickUntouched=True, gamePaused=True)

    def t_jawa_spawn_pawn(self, kindDef, faction, x, z, count=1):
        pid = "M%d" % len(self.pawns)
        self.pawns.append(dict(id=pid, position=dict(x=x, z=z)))
        self.mp[pid] = dict(id=pid, kind=kindDef, pos=(x, z), faction=faction, bs=self.PIT_BS.get(kindDef, 1.0))
        self.spawned_at.setdefault((x, z), []).append(pid)
        return dict(success=True, pawns=[dict(id=pid)])

    def t_jawa_set_pawn_skill(self, **kw):
        return dict(success=True, before=dict(disabled=False), readBackMatches=True)

    def t_jawa_set_work_priority(self, pawnId=None, workType=None, priority=3):
        if "worktype_disabled_once" in self.faults and pawnId == "M0":
            return dict(success=False, message="SetPriority silently refuses: 'Mining' is DISABLED for this pawn")
        self.prio[pawnId] = priority
        return dict(success=True, readBack=priority, manualPrioritiesOn=True)

    def t_jawa_pawn_stats(self, **kw):
        return dict(success=True, stats=[dict(defName="MiningSpeed", value=1.95)])

    def t_jawa_ordered_job(self, **kw):
        return dict(success=False, accepted=True, note="mock: queued")

    def t_jawa_pawn_get(self, **kw):
        return dict(success=True, pawns=[dict(position=None, curJob=None)])

    def t_jawa_designate_batch(self, action, designation, rect):
        x, z, _, _ = map(int, rect.split(","))
        if not ("dig_never" in self.faults and designation == "RM_DigCanal"):
            self.jobs[(x, z)] = [designation, 3200 / 1.95 if designation == "RM_DigCanal" else 1600 / 1.95]
        return dict(success=True, totalNow=1)

    def t_rimworld_step_game_ticks(self, ticks=1, pauseFirst=True, timeoutMs=0):
        if "flowworks_error" in self.faults and not any(x["Level"] == "error" for x in self.logs):
            self.log("error", "Exception in RimMandrake.FlowWorks.RM_MapComponent_Excavation.MapComponentTick")
        if "ticks_frozen" in self.faults:          # day 3: the step replies success and runs 0 ticks
            return dict(success=True)
        for _ in range(ticks):
            self.tick += 1
            self.weather_age += 1
            for c, j in list(self.jobs.items()):
                j[1] -= 1
                if j[1] <= 0:
                    del self.jobs[c]
                    if j[0] == "RM_DigCanal":
                        self.o.dig(c, 1)
                    else:
                        self.fill_in(c)
            if self.tick % 30 == 0:
                self.fire_tick()
            if (self.S("depthEngineEnabled") or "engine_toggle_ignored" in self.faults) and self.tick >= self.next_pulse:
                self.next_pulse = self.tick + self.interval()
                self.fire_burn(self.interval())
                self.do_pulse()
        return dict(success=True)

    # ---- X10 fire model (RM_LiquidFire, CreepingFuse tar 120 ticks/cell; burn = burnDaysPerNotch per notch)
    BURNABLE = ("RM_Fluid_Tar", "RM_Fluid_Oil")

    def burnable(self, c):
        # LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (P4): BurnableFluidAt sees a sheet: exact-level, any decilitre burns
        wet = self.o.W.get(c, 0) > 0 if self.o.level_exact else self.o.F.get(c, 0) > 0
        return self.o.exc(c) and wet and self.o.fluid.get(c) in self.BURNABLE

    def fire_tick(self):
        if not self.S("canalFireEnabled"):
            self.fire.clear(), self.fire_pend.clear()
            return
        for c, due in sorted(self.fire_pend.items()):
            if due <= self.tick:
                del self.fire_pend[c]
                if self.burnable(c) and c not in self.fire:
                    self.fire[c] = 0
        for c in list(self.fire):
            if not self.burnable(c):
                del self.fire[c]
                continue
            if "fire_never_spreads" in self.faults:
                continue
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + d[0], c[1] + d[1])
                if self.burnable(n) and n not in self.fire and n not in self.fire_pend:
                    self.fire_pend[n] = self.tick + 120

    def fire_burn(self, pulse_ticks):
        if "fire_never_burns" in self.faults:
            return
        per = max(1, int(round(60000 * max(0.01, float(self.S("burnDaysPerNotch"))))))
        if self.o.level_exact:
            # P4: a canal square burns RM_FireMath.DlDue decilitres a pulse (a notch per burnDaysPerNotch); its whole-notch
            # view F reaches 0 while the last part-notch still burns, and it is spent (ashed, unlit) only at 0 dL
            due = max(1, level_water.U * pulse_ticks // per)
            for c in list(self.fire):
                w = max(0, self.o.W.get(c, 0) - due)
                self.o.W[c], self.o.F[c] = w, w // level_water.U
                if w == 0:
                    del self.fire[c]
                    if "fire_no_ash" not in self.faults:
                        self.ash.add(c)
            return
        for c in list(self.fire):
            self.fire[c] += pulse_ticks
            while self.fire.get(c, 0) >= per:
                self.fire[c] -= per
                self.put(c, max(0, self.o.F.get(c, 0) - 1))
                if self.o.F[c] == 0:
                    del self.fire[c]
                    if "fire_no_ash" not in self.faults:
                        self.ash.add(c)

    def t_jawa_list_things(self, defName=None, rect=None, limit=200, **kw):
        x, z, w, h = map(int, rect.split(","))
        if defName == "RM_LiquidFlame":
            self.flame_lists += 1
            if "flame_list_late_blind" in self.faults and self.flame_lists >= 3:
                return dict(success=False, error="mock: list_things failed")
        src = {"RM_LiquidFlame": set(self.fire), "Filth_Ash": self.ash}.get(defName, set())
        hit = sorted(c for c in src if x <= c[0] < x + w and z <= c[1] < z + h)
        return dict(success=True, countMatched=len(hit), things=[dict(id="T%d_%d" % c, position=dict(x=c[0], z=c[1]))
                                                                 for c in hit[:limit]])

    # ---- phase X: jawa/static_call over RM_PromotionProofs / RM_FluidIdentityProof (2026-10-05)
    def _fill_terrain(self, c):
        fl = self.o.fluid.get(c, "RM_Fluid_Water")
        if "fluids_look_same" in self.faults:
            fl = "RM_Fluid_Water"
        return "RM_Fill_%s_Brim" % fl.replace("RM_Fluid_", "")

    def t_jawa_static_call(self, type, method, args=""):
        if type == "Verse.Log":         # the log-cap guard (validation_core.log_alive / log_revive)
            if method == "Warning" and "log_dead" not in self.faults:
                self.log("warning", args)
            return dict(success=True, result="null")
        o = self.o
        res = None
        if method == "ProofFillWithFluid":
            x, z, f, fl = args.split(",")
            c, f = (int(x), int(z)), int(f)
            if not o.exc(c) or (o.F.get(c, 0) > 0 and o.fluid.get(c, "RM_Fluid_Water") != fl):
                res = "REFUSED: %s not excavated or holds another fluid" % (c,)
            else:
                self.put(c, min(f, o.D[c]))
                if fl == "RM_Fluid_Water":
                    o.fluid.pop(c, None)
                else:
                    o.fluid[c] = fl
                self.fill_written = True
                res = "FILLED %s F=%d fluid=%s" % (c, o.F[c], fl)
        elif method == "ProofPawnSink":
            p = self.mp.get(args)
            if p is None:
                res = "REFUSED: no spawned pawn " + args
            else:
                c = p["pos"]
                d, f = o.D.get(c, 0), o.F.get(c, 0)
                sink = 0.0 if "sink_flat" in self.faults else SINK_PER_LEVEL * d
                if "slime_lifts" in self.faults:
                    sink = max(0.0, sink - SINK_PER_LEVEL * f)
                res = "SINK id=%s cell=%d,%d depth=%d fill=%d fluid=%s sink=%.3f drawDz=%.3f moving=False wallOverHead=%.3f" % (
                    args, c[0], c[1], d, f, (o.fluid.get(c, "RM_Fluid_Water") if f else "none"), sink, -sink,
                    SINK_PER_LEVEL * d / FEET_TO_HEAD)
        elif method == "ProofLadder":
            x, z, op = args.split(",")
            c = (int(x), int(z))
            if c not in self.ladders:
                res = "LADDER cell=%s present=False raised=None inspect=none" % args
            else:
                (self.raised.add if op == "raise" else self.raised.discard if op == "lower" else (lambda _: None))(c)
                up = c in self.raised
                res = "LADDER cell=%d,%d present=True raised=%s inspect=%s" % (
                    c[0], c[1], up, _keyed("RMFlow_LadderRaisedInspect" if up else "RMFlow_LadderLoweredInspect").replace(" ", "_"))
        elif method == "ProofForcedFlyer":
            pid, x, z = args.split(",")
            p, c = self.mp.get(pid), (int(x), int(z))
            if p is None:
                res = "REFUSED: no spawned pawn " + pid
            else:
                start = p["pos"]
                p["pos"] = c
                if self.d4(c) and not self.d4(start) and self.S("superdeepCaptureEnabled"):
                    if p["faction"] == "player":
                        self.jumpers.add(pid)
                    if "forced_lands_free" in self.faults:
                        self.landed_free.add(pid)
                    if "pit_no_fall" not in self.faults:
                        self.descents.append("%s@%d,%d t=%d fall=4.8" % (pid, c[0], c[1], self.tick))
                res = "FLYER id=%s from=%d,%d to=%d,%d depth=%d launched=True def=PawnFlyer_Stun" % (
                    pid, start[0], start[1], c[0], c[1], o.D.get(c, 0))
        elif method == "ProofCover":
            x, z = map(int, args.split(","))
            c = (x, z)
            ring = [self.terrain_of((x + dx, z + dz)) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                    if (dx or dz) and not o.exc((x + dx, z + dz))]
            around = max(sorted(set(ring)), key=ring.count) if ring else "none"
            printed = self.terrain_of(c) if "cover_shows_hole" in self.faults else around
            under = [pid for pid in self.spawned_at.get(c, []) if pid in self.beneath]
            res = "COVER cell=%d,%d present=%s covered=%s sprung=False depth=%d cellTerrain=%s printed=%s matOk=True around=%s inspect=Gives_way_under_40_kg%s" % (
                x, z, c in self.covers, c in self.covers, o.D.get(c, 0), self.terrain_of(c), printed, around,
                ("/Below,_hidden:_" + ",_".join(under) + ".") if under else "")
            if "cover_no_printed" in self.faults:          # an older/changed ProofCover format: no printed=/around=
                res = re.sub(r" (printed|around)=\S+", "", res)
        elif method == "ProofBeneath":
            x, z = map(int, args.split(","))
            c = (x, z)
            here = self.spawned_at.get(c, [])
            b = bool(here) and here[0] in self.beneath
            res = "BENEATH cell=%d,%d pawn=%s beneath=%s held=%s trapped=%s onLoad=%s hidden=%s covered=%s" % (
                x, z, here[0] if here else "none", b, b, b, not b, b, c in self.covers)
        elif method == "ProofIgnite" and "ignite_type_missing" in self.faults:
            return dict(success=False, message="Type not found: %s" % type)
        elif method == "ProofIgnite":
            x, z = map(int, args.split(","))
            c = (x, z)
            if not self.S("canalFireEnabled") or not self.burnable(c):
                res = "REFUSED: fire off or nothing burnable at %s" % (c,)
            else:
                self.fire_pend[c] = self.tick
                self.fire_tick()
                res = "LIT (%d, 0, %d) | FIRE burning %d | front pending %d | burned levels 0" % (
                    x, z, len(self.fire), len(self.fire_pend))
        elif method == "ProofReport" and type.endswith("RM_LiquidFireProof"):
            res = "FIRE burning %d | front pending %d | burned levels %d" % (len(self.fire), len(self.fire_pend), len(self.ash))
        elif method == "ProofReadout":
            x, z = map(int, args.split(","))
            c = (x, z)
            w = o.W.get(c, 0) if o.level_exact else o.F.get(c, 0) * level_water.U
            res = "OK Hole %.1f m \u00b7 Water %.2f m (%s L)" % (0.5 * o.D.get(c, 0), w * level_water.M_PER_UNIT,
                                                                format(int(round(w / 10.0)), ","))
        elif method == "ProofFluidRow" and "fluid_row_blind" in self.faults:
            return dict(success=False, message="mock: ProofFluidRow threw")
        elif method == "ProofFluidRow":
            x, z, w, h = map(int, args.split(","))
            toks = []
            for j in range(h):
                for i in range(w):
                    c = (x + i, z + j)
                    f = o.F.get(c, 0)
                    toks.append("%d,%d:%d/%d/%s/%s" % (c[0], c[1], o.D.get(c, 0), f,
                                                     (o.fluid.get(c, "RM_Fluid_Water") if f else "none"),
                                                     self._fill_terrain(c) if f else self.terrain_of(c)))
            res = "ROW pulse=%d viscosity=%s %s;" % (o.pulse_n, self.S("viscosityEnabled"), ";".join(toks))
        if res is None:
            return dict(success=False, message="mock: no static %s.%s" % (type, method))
        return dict(success=True, method=method, result=res)

    def t_jawa_flowworks_set_active_fluid(self, fluidDefName, allowAfterClassification=False):
        if "engine_lost_late" in self.faults:
            self.engine_lost = True
        if (self.classified or self.fill_written) and not allowAfterClassification and "fluid_switch_allowed" not in self.faults:
            return dict(success=False, refused=True)
        self.fluid = fluidDefName
        return dict(success=True)

    def finish(self):
        pass


# ============================================================================ runner
class RealBridge(object):
    def __init__(self):
        sys.path.insert(0, UTILS)
        import rimbridge_client as rb          # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()
        self.n = 0

    def call(self, tool, **kw):
        self.n += 1
        r = self.S.call(tool, kw) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:                 # noqa: BLE001
                pass
        _vc().tap_after(tool)                 # poll the journal tap after a tick step (validation_core.LogTap)
        return r if isinstance(r, dict) else {"success": False, "raw": r}


FROZEN_BIOMES = ("IceSheet", "SeaIce")   # temp-layer ice the site painter cannot clear (run 6)
PHASES = ("L", "site", "S", "A", "B", "C", "R", "J", "rain", "P", "X", "tail")


def abort_class(msg):
    """SITE when the abort names the map's own state (not pristine, a pawn standing in a plot); else HARNESS.
    A bare "pawn" substring also matched "spawn colonist ..." (a harness failure) -- match the phrases exactly."""
    return "SITE" if ("pristine" in msg or "a pawn stands" in msg) else "HARNESS"


def run_live(args, B=None):
    B = B or (MockBridge(args.fault or []) if args.mock else RealBridge())
    L = Live(B, progress=None if args.mock else args.progress, mock=args.mock)
    t0 = time.time()
    load = None
    site_save = getattr(args, "site_save", None)
    if site_save and not args.mock and not args.fresh_map and not getattr(args, "current_map", False):
        sys.path.insert(0, os.path.join(UTILS, "modcheck"))
        import test_site_saves as TSS  # noqa: E402
        ts = time.time()
        site = TSS.load_site(B.call, site_save)
        load = dict(siteSave=site_save, save=site.get("save"), verified=site.get("verified"), problems=site.get("problems"),
                    load_s=site.get("load_s"), ready_s=site.get("ready_s"), wall_s=round(time.time() - ts, 1))
        L._log("- clean saved site: %s" % load)
        if not site.get("verified"):
            L.row("L0_fresh_map", False, "SITE", load)
    elif args.fresh_map:
        ts = time.time()
        # from inside a running colony start_debug_game_ready does NOT start a fresh one (it times
        # out waiting for the entry scene, 280 s lost on 2026-10-02): go to the main menu first,
        # and judge by programState + a pristine engine, never by the call's own success.
        # Live run 6 (2026-10-02) drew an IceSheet map: map gen leaves ThinIce on the TEMP terrain
        # layer over painted Soil (get_terrain_layers temp=ThinIce, base Soil), set_terrain_batch
        # writes the base layer only and set_terrain_layer cannot clear temp ("Give a TerrainDef"),
        # so the site readback (now L4_site_ready) refused. The engine renders fill on the temp layer too. -> re-roll such maps.
        rolls = []
        for _roll in range(4):
            m = B.call("rimworld/go_to_main_menu")
            r = B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
            st = None
            for _ in range(120):
                st = B.call("rimworld/get_ui_state").get("programState")
                if st == "Playing" and B.call("jawa/map_info").get("success"):
                    break
                if not args.mock:
                    time.sleep(2.0)
            biome = B.call("jawa/map_info").get("mapBiome")
            rolls.append(biome)
            if biome not in FROZEN_BIOMES:
                break
        load = dict(menu=m.get("success"), start=r.get("success"), programState=st, biomes=rolls,
                    wall_s=round(time.time() - ts, 1))
        L._log("- fresh quicktest map: %s" % load)
        if st != "Playing":
            L.row("L0_fresh_map", False, "SITE", load)
        elif not args.mock:
            # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: calm the fresh map (hostiles, hives) as proof_hose does
            import validation_core as _VC   # noqa: E402
            load["site_calm"] = _VC.site_calm(B)
            L._log("- site_calm: %s" % load["site_calm"])
    # The recording contract (`modcheck record`, Utils/modcheck/record.py): the mod hash the run
    # was made AT and the mod list it ran ON, both read now, so a later record can refuse a stale
    # or off-tier result instead of trusting it.
    env = dict(running=None, running_sha256=None, assembly_sha256=None, assembly_matches=None)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False)
    if rm.get("success"):
        import hashlib
        env["running"] = [p.lower() for p in rm.get("packageIds") or []]
        env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
        ms = (rm.get("assembly") or {}).get("matches") or []
        env["assembly_matches"] = len(ms)
        env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
    try:
        sys.path.insert(0, os.path.join(UTILS, "modcheck"))
        import status as _mc_status    # noqa: E402
        mod_hash = _mc_status.mod_hash(MOD)
    except Exception as ex:            # noqa: BLE001 - recorded as absent; record then refuses
        mod_hash = None
        L._log("- mod_hash unavailable: %s" % ex)
    ticks0 = None
    aborted = None
    fns = dict(L=phase_L, site=phase_site, S=phase_S, A=phase_A, B=phase_B, C=phase_C, R=phase_R, J=phase_J,
               rain=phase_rain, P=phase_P, X=phase_X, tail=phase_tail)
    try:
        ticks0 = L.eng().get("ticksGame")
        for ph in PHASES:
            fns[ph](L, args)
    except Abort as ex:
        aborted = str(ex)
        L.row("ABORT", False, abort_class(aborted), aborted)
    finally:
        bad = L.restore_settings()
        L.row("Z_settings_restored", not bad, "HARNESS", bad or "%d touched settings back to shipped defaults" % len(L.touched))
        if load and "site_calm" in load:   # site_calm opened a settings transaction (storyteller, breaks, wild spawner)
            load["site_calm_restore"] = _vc().site_calm_restore(B)
        B.call("jawa/weather_set", weather="Clear", unlock=True)
        if args.mock:
            B.finish()
    try:
        ticks1 = L.eng().get("ticksGame")
    except Abort as ex:                # the engine/map is gone (often why the run aborted): keep every collected row
        ticks1 = None
        L._log("- final engine_state unreadable: %s" % ex)
    res = dict(script="validation_v2", mod="FlowWorks", mod_hash=mod_hash, env=env,
               mode="mock" if args.mock else "live", faults=list(args.fault or []),
               started=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)), wall_s=round(time.time() - t0, 1),
               ticks_spent=(ticks1 - ticks0) if (ticks0 is not None and ticks1 is not None) else None,
               fresh_map=load, calls=B.n, aborted=aborted, steps=L.steps, rows=L.rows,
               plan_budget=dict(v2_target_ticks="1,000-2,000 (plan section 10, with flowworks_pulse)",
                                v2_without_pulse_tool="3,000-7,300", old_suite=112921),
               summary={st: sum(1 for r in L.rows if r["status"] == st) for st in
                        ("PASS", "FAIL", "UNMEASURED", "UNCOVERED", "UNBUILT", "SKIP")})
    res["green"] = all(r["status"] in STATUS_OK for r in L.rows) and not aborted
    return res


def declared_rows():
    """Every row id a `--live --fresh-map` run emits, enumerated offline by a clean --mock run of the same tier (the
    walk's `checkout:` header names this file; modcheck/required_checks.py calls this; NORTHSTAR_RESULTS_JOIN_1)."""
    class A(object):
        mock, fresh_map, reset_settings, progress, max_job_ticks = True, True, False, None, 4000
        fault = []
    with open(os.devnull, "w") as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            return [r["id"] for r in run_live(A)["rows"]]
        finally:
            sys.stdout = so


def selftest_live_mock():
    """The negative-control harness for the LIVE tier: a clean mock run is green, and every
    fault makes its named row(s) go non-PASS."""
    class A(object):
        mock, fresh_map, reset_settings, progress, max_job_ticks = True, False, False, None, 6000
        fault = []
    probs = []
    res = run_live(A)
    notok = [(r["id"], r["status"], r["detail"][:160]) for r in res["rows"]
             if r["status"] not in STATUS_OK and r["id"] not in KNOWN_MOD_RED]
    known = [r["id"] for r in res["rows"] if r["id"] in KNOWN_MOD_RED and r["status"] == "PASS"]
    if known:
        probs.append("known MOD defect rows PASS in the shipped-semantics mock (oracle drifted?): %s" % known)
    if notok:
        probs.append("clean mock run not green: %s" % notok[:4])
    # the ABORT class: a harness spawn failure is not a SITE defect ("spawn" contains "pawn")
    for msg, want in (("spawn colonist for E8: {}", "HARNESS"), ("spawn hare on (1, 2): {}", "HARNESS"),
                      ("a pawn stands in a plot rect", "SITE"), ("site not pristine -- start a fresh map", "SITE")):
        if abort_class(msg) != want:
            probs.append("abort_class(%r) = %s, want %s" % (msg, abort_class(msg), want))
    for fault, rows in sorted(MockBridge.FAULTS.items()):
        a = A()
        a.fault = [fault]
        try:
            r = run_live(a)
        except Exception as ex:                                   # noqa: BLE001 - a crash loses every row: red
            probs.append("fault %s crashed run_live: %r" % (fault, ex))
            continue
        st = {x["id"]: x["status"] for x in r["rows"]}
        # the named rows must be non-PASS whether or not the run aborted (an aborted run's rows are still read)
        if any(st.get(row) in ("PASS", None) for row in rows):
            probs.append("fault %s: rows %s stayed %s%s" % (fault, rows, [st.get(x) for x in rows],
                                                          " (run aborted: %s)" % r["aborted"] if r["aborted"] else ""))
        for row_, want_st in MockBridge.FAULT_STATUS.get(fault, {}).items():
            if st.get(row_) != want_st:
                probs.append("fault %s: %s read %s, want %s" % (fault, row_, st.get(row_), want_st))
        # these faults abort by design (settings_drift/dll_stale via L2, engine_lost_late in the tail,
        # preflight_crash because an unverified DLL must never be driven); any other abort is a harness defect
        if r["aborted"] and fault not in MockBridge.ABORTING:
            probs.append("fault %s aborted the run instead of failing its row: %s" % (fault, r["aborted"]))
    return Check("O-LIVE-NEG", not probs, "; ".join(probs)[:900] or
                 "clean mock run green (%d rows, %d ticks); all %d faults turned their rows red"
                 % (len(res["rows"]), res["ticks_spent"] or 0, len(MockBridge.FAULTS)))


ZERO_TICK_PREFIXES = ("S1", "S2", "S3", "S4", "S5", "A", "E2", "E3", "E5", "G_")


def compare_runs(pa, pb):
    """Determinism across runs (plan section 4.3): two live runs on two fresh maps must agree on
    every 0-tick row bit-for-bit (stock floats aside: refill adds ~1e-3 per pulse).
    MEASURED 2026-10-02: runs 074022 (Tundra) and 074420 -> 31 rows, 0 differ."""
    a, b = json.load(open(pa, encoding="utf-8")), json.load(open(pb, encoding="utf-8"))
    norm = lambda d: re.sub(r"stock[^,}]*?[\d.]+", "stock~", d)  # noqa: E731
    ra, rb = {r["id"]: r for r in a["rows"]}, {r["id"]: r for r in b["rows"]}
    ids = [i for i in ra if i.startswith(ZERO_TICK_PREFIXES) and i in rb]
    # a zero-tick row only one run emitted (the other aborted or skipped it) is a difference, never dropped from the compare
    lone = sorted(i for i in set(ra) ^ set(rb) if i.startswith(ZERO_TICK_PREFIXES))
    diff = [i for i in ids if (ra[i]["status"], norm(ra[i]["detail"])) != (rb[i]["status"], norm(rb[i]["detail"]))] + lone
    if len(ids) < 20:
        return False, "only %d comparable rows (sanity floor 20)" % len(ids)
    return not diff, "%d zero-tick rows compared, %d differ %s (in one run only: %s)" % (
        len(ids), len(diff), diff[:6], lone[:6])


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="tier O only (default)")
    ap.add_argument("--live", action="store_true", help="run L/S/E against the bridge (python.exe)")
    ap.add_argument("--mock", action="store_true", help="run the live tier against the in-memory game")
    ap.add_argument("--fault", action="append", help="mock fault to inject (see MockBridge.FAULTS)")
    ap.add_argument("--fresh-map", action="store_true", help="start a new debug quicktest map first (instead of the saved site)")
    ap.add_argument("--current-map", action="store_true", help="run on the current map (no load, no new map)")
    ap.add_argument("--site-save", default="calm", help="the clean saved site --live loads (test_site_saves.py; default calm)")
    ap.add_argument("--reset-settings", action="store_true", help="reset drifted Mod Settings instead of refusing")
    ap.add_argument("--max-job-ticks", type=int, default=4000)
    ap.add_argument("--progress", default=None, help="append per-step progress here")
    ap.add_argument("--out", default=None, help="result JSON (default: beside this script)")
    ap.add_argument("--compare", nargs=2, metavar="RESULT_JSON", help="determinism across runs: diff the 0-tick rows")
    a = ap.parse_args(argv)
    if a.compare:
        ok, msg = compare_runs(*a.compare)
        print(("SAME: " if ok else "DIFFER: ") + msg)
        return 0 if ok else 1
    if not (a.live or a.mock):
        checks = run_offline()
        checks.append(selftest_live_mock())
        print(checks[-1])
        return 0 if all(c.ok for c in checks) else 1
    res = run_live(a)
    if a.live:
        out = a.out or os.path.join(HERE, "validation_v2_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        print("result -> %s" % out)
    print("%s: %s  ticks %s  wall %ss  calls %d  %s" % ("LIVE" if a.live else "MOCK", "GREEN" if res["green"] else "NOT GREEN",
                                                       res["ticks_spent"], res["wall_s"], res["calls"], res["summary"]))
    return 0 if res["green"] else 1


if __name__ == "__main__":
    sys.exit(main())
