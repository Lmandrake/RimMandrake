"""validation_v2.py -- FlowWorks functional script v2 (the running Northstar functional tier).

Plan (authority): design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md
Evidence:         design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md ("INT")
Does NOT replace src/RimMandrake/FlowWorks/validation.py and never edits the walk.

    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py            # tier O, 0 ticks
    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py --mock     # live tier vs in-memory game
    python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map
    python3    src/RimMandrake/FlowWorks/northstar/validation_v2.py --compare A.json B.json

Tier O (offline): O1 defs, O2 settings defaults, O3 UNBUILT register, O4 geometry, O5/O6 pulse
oracle, O7 scene predictions, O8 schema lint, O-NEG (each offline check mutated red) and
O-LIVE-NEG (a clean --mock run is green, and each of MockBridge.FAULTS turns its live row red).
Live (python.exe, flowworks tier, bridge held): a FRESH quicktest map (go_to_main_menu first),
L preflight, site painted by the runner, S state (0 ticks), A/B/C/R flow phases through
jawa/flowworks_pulse (0 ticks, EVERY excavated cell compared with the oracle at EVERY pulse), J
(the only ticks: ordered pawn jobs, which also carry the engine-OFF window, the clamped cadence and
the rain-toggle negative), the rain phase (0 ticks) and the tail (fluid-switch refusal, log budget).
Result JSON beside this script (modcheck `run` swaps ModsConfig and records only a mod's own
validation.py; northstar_driver `run` does not call record_run -- debug_process section 1 item 4).

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
  * A 1-cell pond at shipped recession supplies exactly ONE level, then recedes (floor(4/5) = 0
    supported cells): E3b. The old P2 strip "had no source"; a painted 1-cell source fixes it.
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

# Shipped defaults (O2 cross-checks these against the C# initializers AND Scribe defaults).
BOOL_DEFAULTS = {
    S_FW: dict(depthEngineEnabled=True, digToDepthEnabled=True,
               liquidCorrosionEnabled=False, liquidIgnitionEnabled=False, fillInEnabled=True,
               fillInDisplacementEnabled=True, sourceBudgetEnabled=True, stickyLimitlessEnabled=True,
               recessionEnabled=True, refillEnabled=True, rainFillsExcavationsEnabled=True,
               edgeSinksEnabled=True, superdeepCaptureEnabled=True, superdeepCapturesOwnFaction=False,
               ladderRequiredToExitEnabled=True, ladderPrisonDoorEnabled=True, spikesEnabled=True,
               flowDoorsSealedFromPitEnabled=True, sluiceLetsBigThroughEnabled=True,
               superdeepShootingRuleEnabled=True,
               bottleLoopEnabled=True, bottleDirtyStageEnabled=True, tankLoopEnabled=True,
               liquidDrillingEnabled=True, typedLiquidShoresEnabled=True, swaleEnabled=True,
               trapTriggerEnabled=True, fallDamageEnabled=True,
               pitExposureEnabled=True, pitDepthDrawOffsetEnabled=True,
               canalFireEnabled=True,      # FLOWWORKS_BUILD_PROGRAM_1 Phase 6
               pitDrowningEnabled=True, poisonFillEnabled=True,      # PIT_FILL_EFFECTS_1
               viscosityEnabled=True),     # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (2026-10-05)    # rehoused from PitsSettings 2026-10-02
    S_RIVER: dict(riverSteamEnabled=True),
}
FLOAT_DEFAULTS = {"pulseIntervalTicks": 250.0, "flowPerPulse": 1.0, "rainFillPerPulse": 0.1,
                  "minLimitlessBodyCells": 50.0, "pitWidthBodySizeMultiplier": 1.0,
                  "trapSensitivityMultiplier": 1.0, "fallDamageMultiplier": 1.0,
                  "spikeDamageMultiplier": 1.0, "swaleRateMultiplier": 1.0,
                  "pitTemperatureCoupling": 3.0, "pitResistanceLossMultiplier": 1.0,
                  "pitSinkPerLevel": 0.3,
                  "canalBurnDaysPerLevel": 1.0, "sourceBurnDaysPerLevel": 5.0,     # Phase 6, ruling 7
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


def fluid_moves(pulse, fluid):
    """Port of RM_StockMath.FluidMovesThisPulse for a fluid named by defName."""
    if not _TPT:
        _TPT.update(_fluid_ticks_per_tile() or {"RM_Fluid_Water": 60})
    st = viscosity_stride(_TPT.get(fluid, 60))
    return st <= 1 or pulse % st == 0


class PulseOracle(object):
    """A pure-Python port of RM_MapComponent_Excavation.DoPulse / ResolveComponent / PickDonor /
    CompareDeepestFirst (Source/RM_MapComponent_Excavation.cs l.762-1025), for the depth engine
    only: no rain (weather pinned Clear), no recession/refill (stock.Pulse) -- scenes are chosen
    so neither changes the predicted vector (plan section 3, E-tier). Deterministic by
    construction: recipients sorted (-D, cell index), donors scanned N,E,S,W with strict '>'.

    algo="old" is that engine as measured live 2026-10-01 (east/north channels oscillate).
    algo="fixed" (default) is FLOWWORKS_CHANNEL_OSCILLATION_1's fix: a per-component flow order
    gates cell-to-cell gifts and orders recipients (see _downstream). O6 proves it.

    VALIDATED once against live data (INT section 2): given plot D's geometry (5x5 limited pond,
    12-cell D=3 channel running east, stock 125) it reproduces BOTH oscillating F vectors the
    2026-10-01 run recorded at ticks 538,130..539,880, exactly."""

    def __init__(self, w, h, sources, bodies, per=1, budget=True, sink_band=None, algo="fixed",
                 recession=False, claim_sources=None):
        self.w, self.h = w, h
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

    def set_fill(self, c, f):
        if not self.exc(c):
            return False
        self.F[c] = max(0, min(f, self.D[c]))
        return True

    def _pick(self, r, dr):
        best, best_score = None, -1
        for dx, dz in CARDINAL:
            n = (r[0] + dx, r[1] + dz)
            if not self.inb(n):
                continue
            src = self.is_source(n)
            if src:
                if not self.can_supply(n):
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

    def set_cell(self, c, d, f):
        """Mirror a live cell the oracle did not drive (a pawn job's result)."""
        if d <= 0:
            self.D.pop(c, None)
            self.F.pop(c, None)
        else:
            self.D[c], self.F[c] = d, max(0, min(f, d))

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
                    key = (nb, -((c[0] - cx) ** 2 + (c[1] - cz) ** 2), self.idx(c))
                    if best is None or key < best[0]:
                        best = (key, c)
                if best is None:
                    break
                rec.append(best[1])
                self.receded.add(best[1])

    def pulse(self):
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
                        fl = "RM_Fluid_Water" if self.is_source(d) else self.fluid.get(d, "RM_Fluid_Water")
                        if fl == "RM_Fluid_Water":
                            self.fluid.pop(r, None)
                        else:
                            self.fluid[r] = fl
                    self.F[r] += 1
                    moved += 1
        for c in [c for c in self.fluid if self.F.get(c, 0) == 0]:   # SyncFluidIdentity: F=0 clears the record
            del self.fluid[c]

    def run(self, cells, pulses):
        out = []
        for _ in range(pulses):
            self.pulse()
            out.append([self.F[c] for c in cells])
        return out


def rect_cells(x, z, w, h):
    return [(x + i, z + j) for i in range(w) for j in range(h)]


# ============================================================================ the site (R1/R2)
# Absolute cells on a FRESH 250x250 debug quicktest map (live run 2026-10-02: the v1 golden
# TrialSite does not carry these bodies, and every v2 flow scene runs at 0 ticks through
# jawa/flowworks_pulse, so weather/pawns/time cannot reach it). The runner clears and paints
# each body and scene (+2-cell ring) itself; L5 + the per-scene pre-read enforce R2.
# The centre (+-25 of 125,125) is avoided: the quicktest colonists stand there.
BODIES = {
    "W1": dict(cells=rect_cells(0, 60, 16, 4), limitless=True),       # west edge, 64 cells
    "W2": dict(cells=[(60, 150)], limitless=False, capacity=5),       # E3 budget (recession OFF)
    "W2R": dict(cells=[(70, 150)], limitless=False, capacity=5),      # E3b recession (defaults)
    "W3": dict(cells=[(80, 150), (81, 150)], limitless=False, capacity=10),   # E4 engine
    "W4": dict(cells=rect_cells(0, 200, 10, 4), limitless=False),     # edge, 40 < 50 cells
    "W5": dict(cells=rect_cells(150, 30, 8, 8), limitless=False, capacity=320),  # interior 64
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
    # E3b: a 1-cell pond at SHIPPED recession supplies one level, then recedes (phase A)
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
    # E4: engine OFF/ON under the REAL scheduler, during the job ticks (phase J)
    "E4_engine": dict(cells=_run(80, 149, 4, 0, -1), D=1, body="W3", dir="S", phase="J"),
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
PIT_SPOTS = {"P_walk": (166, 103), "P_walk_ctrl": (172, 103)}     # colonists start 3 cells off the pit
# Live run 2026-10-02 14:40: waitTicks 300 was too short to ENTER a D=4 cell (RM_Channel_Superdeep pathCost
# 300 -> one step costs ~300+ ticks): the walk-in read "arrived False" though the pawn got there later.
PIT_WAIT_IN, PIT_WAIT_OUT = 1200, 600


def edge_distance(c):
    return min(c[0], c[1], MAP_W - 1 - c[0], MAP_H - 1 - c[1])


def body_stock0(b):
    return 0.0 if b["limitless"] else float(b.get("capacity", 5 * len(b["cells"])))


def oracle_for(scene_key, pulses, recession=False):
    """Predicted F vectors for one channel scene in isolation (per pulse)."""
    s = SCENES[scene_key]
    body = BODIES[s["body"]]
    stock = body_stock0(body)
    o = PulseOracle(MAP_W, MAP_H, {c: 0 for c in body["cells"]},
                    {0: {"limitless": body["limitless"], "stock": stock, "capacity": stock,
                         "cells": list(body["cells"])}}, sink_band=SINK_BAND, recession=recession)
    for c in s["cells"]:
        o.dig(c, s["D"])
    return o.run(s["cells"], pulses)


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


def _fill_tier(f, d):                       # mirrors RM_ExcavationDepth.FillTier
    r = float(f) / d
    return 1 if r <= 0.34 else (2 if r <= 0.67 else 3)


def fill_cost_findings(defs):
    """DEPTH_FILL_COST_MATRIX_1 / ruling [E]: at every depth 1-3, every reachable fill (F = 1..D, tier by
    FillTier, terrain by FluidDef.FillTerrainFor) costs strictly more to cross than the same depth dry.
    Named regression: RM_Fill_Water_Half 42 < RM_Channel_Mid 45 (D=2, F=1)."""
    dry = {1: "RM_Channel_Empty", 2: "RM_Channel_Mid", 3: "RM_Channel_Deep"}
    probs, n = [], 0
    for name, b in sorted(defs.items()):
        if not b[0].endswith("FluidDef"):
            continue
        tiers = {1: _field(b[2], "floodTerrain"), 2: _field(b[2], "fillTerrainHalf") or _field(b[2], "floodTerrain"),
                 3: _field(b[2], "fillTerrainBrim") or _field(b[2], "fillTerrainHalf") or _field(b[2], "floodTerrain")}
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


def o1_defs():
    defs = _xml_blocks()
    probs = []
    if "RM_Channel_Empty" not in defs:            # sanity probe: the parser can find a known def
        return Check("O1", False, "parser blind: RM_Channel_Empty not found (%d defs)" % len(defs))
    w = defs.get("RM_Fluid_Water")
    if not w:
        probs.append("RM_Fluid_Water missing")
    else:
        for f, want in (("floodTerrain", "RM_Fill_Water_Trace"), ("volumePerTile", "1"),
                        ("canalCellsPerSourceCell", "5"), ("ticksPerTile", "60")):
            if _field(w[2], f) != want:
                probs.append("RM_Fluid_Water.%s=%r want %r" % (f, _field(w[2], f), want))
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
    spike = sorted(n for n, b in defs.items() if "Things/Building/Security/TrapSpikeArmed" in b[2] and n != "RM_Ladder")
    if spike:
        probs.append("defs on the vanilla TrapSpikeArmed art (only RM_Ladder may, until its art lands): %s" % spike)
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


def o2_settings_defaults():
    probs, seen = [], 0
    srcs = {}
    for root, _, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".cs"):
                srcs[fn] = open(os.path.join(root, fn), encoding="utf-8").read()
    allsrc = "\n".join(srcs.values())
    for typ, fields in BOOL_DEFAULTS.items():
        for f, want in fields.items():
            m1 = re.search(r"public static bool %s\s*=\s*(true|false)" % f, allsrc)
            m2 = re.search(r'Scribe_Values\.Look\(ref %s, "%s", (true|false)\)' % (f, f), allsrc)
            seen += 1
            got = {m1 and m1.group(1), m2 and m2.group(1)}
            if got != {str(want).lower()}:
                probs.append("%s: init/scribe %s want %s" % (f, sorted(map(str, got)), want))
    for f, want in FLOAT_DEFAULTS.items():
        m1 = re.search(r"public static float %s\s*=\s*([\d.]+)f" % f, allsrc)
        if not m1 or float(m1.group(1)) != want:
            probs.append("%s=%s want %s" % (f, m1 and m1.group(1), want))
    if seen != 35:                  # +4 2026-10-05: pitDepthDrawOffset, canalFire, pitDrowning, poisonFill; +viscosity;
        probs.append("toggle census %d != 35" % seen)   # -1 2026-10-06: channelConfinementEnabled retired
    # PIT_LEGACY_CODE_RETIRE_1 northstar: one settings screen; no struggle/escape/exposure toggle survives
    mods = re.findall(r"class \w+ : Mod\b", allsrc)
    if len(mods) != 2:              # RimMandrakeFlowWorksMod + RiverSteamMod (PitsMod retired)
        probs.append("Mod subclasses %s (want 2: FlowWorks + RiverSteam)" % mods)
    dead = re.findall(r"public static \w+ (\w*(?:struggle|escape|Escape|Struggle|pitCellExposure)\w*)\s*=", allsrc)
    if re.search(r"public static bool channelConfinementEnabled\b", allsrc):
        dead.append("channelConfinementEnabled")
    if dead:
        probs.append("retired settings still declared: %s" % dead)
    return Check("O2", not probs, "; ".join(probs) or "%d toggles + %d floats match C#; 2 Mod screens; no "
                 "struggle/escape/exposure setting" % (seen, len(FLOAT_DEFAULTS)))


# UNBUILT register (R9): bar -> (source fact that keeps it UNBUILT, predicate over sources).
def _src_all():
    out = []
    for root, _, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".cs"):
                out.append(open(os.path.join(root, fn), encoding="utf-8").read())
    return "\n".join(out)


def _engine_src():
    return open(os.path.join(SRC, "RM_MapComponent_Excavation.cs"), encoding="utf-8").read()


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


def o3_unbuilt_register():
    s, d = _src_all(), _xml_blocks()
    landed = [bar for bar, (_, pred) in UNBUILT.items() if not pred(s, d)]
    me = open(os.path.abspath(__file__), encoding="utf-8").read()
    lost = [b for b, row in PROMOTED.items() if me.count('"%s"' % row) < 2]       # the table + a live L.row
    both = sorted(set(PROMOTED) & set(UNBUILT))
    # A landed feature is a PROMOTION (stage the bar now), reported, not a failure of the mod.
    return Check("O3", not lost and not both, ("promoted bars with no live row: %s; " % lost if lost else "")
                 + ("bars both promoted and UNBUILT: %s; " % both if both else "")
                 + "%d UNBUILT bars registered; FEATURE LANDED, stage now: %s; %d promoted to live rows"
                 % (len(UNBUILT) - len(landed), landed or "none", len(PROMOTED)))


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
        big = len(b["cells"]) >= FLOAT_DEFAULTS["minLimitlessBodyCells"]
        want = edge and big and not b.get("sticky_off")
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
    # (3) determinism: identical inputs, identical outputs
    if oracle_for("E2_east_A", 8) != oracle_for("E2_east_A", 8):
        probs.append("oracle non-deterministic")
    # (4) budget: W2 (cap 5) -> E3 channel receives exactly 5 levels and no more. The VECTOR does
    # not come to rest: a partly filled equal-depth run keeps shuttling units (period 2) after
    # the source is spent -- the same OVERFLOW-clause behaviour as the east/north oscillation
    # (INT section 2). So the check is on the SUM, and E3 asserts the exact oracle vector.
    v = oracle_for("E3_budget", 14)
    if any(sum(row) != 5 for row in v[-4:]):
        probs.append("E3 budget: last sums %s (want 5)" % [sum(r) for r in v[-4:]])
    return Check("O5", not probs, "; ".join(probs) or "live oscillation reproduced; hand cases; budget 5")


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
def o7_scene_predictions():
    """Every live flow scene, alone, behaves as the live plan assumes (offline, 0 ticks)."""
    probs = []
    for k in ("E2_east_A", "E2_east_B", "E2_north", "E2_south", "E2_west", "E2_rerun"):
        v = oracle_for(k, 8, recession=True)
        if v[3] != [1, 1, 1, 1] or v[0] != [0, 0, 0, 1]:
            probs.append("%s: %s" % (k, v[:4]))
    v = oracle_for("E3b_recede", 4, recession=True)
    if v[-1] != [0, 0, 0, 1]:
        probs.append("E3b at shipped recession should keep exactly one level at the far end: %s" % v)
    v = oracle_for("E3_budget", 7, recession=False)
    if sum(v[-1]) != 5 or v[-1] != v[-2]:
        probs.append("E3 budget (recession OFF) should deliver 5 and rest: %s" % v[-2:])
    return Check("O7", not probs, "; ".join(probs) or "E2 x6 full at pulse 4, far end first; E3b keeps 1; E3 delivers 5 then rests")


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


def o8_lint():
    """Schema lint of every literal bridge call in this file (northstar_driver/lint_calls.py)."""
    try:
        sys.path.insert(0, UTILS)
        from northstar_driver import lint_calls as L
    except Exception as ex:                                  # noqa: BLE001
        return Check("O8", False, "lint_calls unavailable: %s" % ex)
    tools = L.load_tools()
    probs = L.lint_source(open(os.path.abspath(__file__), encoding="utf-8").read(), os.path.basename(__file__), tools)
    # exactly one non-literal call is allowed: RealBridge.call's own transport line
    transport = [p for p in probs if "non-literal tool name" in str(p)]
    probs = [p for p in probs if "non-literal tool name" not in str(p)] + (transport[1:] if len(transport) > 1 else [])
    n = L.STATS.get("calls", 0)
    if n < 35:                                               # sanity probe: the lint must SEE the calls (39 on 2026-10-02)
        return Check("O8", False, "lint saw only %d calls (blind?)" % n)
    return Check("O8", not probs, ("; ".join(map(str, probs[:6])) if probs else "%d bridge calls lint clean" % n))


UTILS = os.path.join(os.path.dirname(os.path.dirname(MOD)), "Utils")


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
    """Each offline check must be ABLE to go red: mutate inputs in memory, expect FAIL."""
    out = []
    bad_bodies = dict(BODIES)
    bad_bodies["W4"] = dict(BODIES["W4"], limitless=True)                          # 40-cell edge "limitless"
    out.append(("O4 40-cell edge body declared limitless", o4_geometry(bodies=bad_bodies).ok))
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
    PulseOracle._pick = lambda self, r, dr: None                                    # an engine that never flows
    try:
        out.append(("O5 inert engine", o5_oracle_selftest().ok))
        out.append(("O7 inert engine", o7_scene_predictions().ok))
    finally:
        PulseOracle._pick = real_pick
    out.append(("O9 shared-source walk with the source claimed (pre-fix)", o9_shared_source(claim=True).ok))
    # the retired holder model: any D=4 cell held any pawn
    out.append(("O10 holder model (any D=4 cell holds anything)",
                o10_pit_width(held_fn=lambda cells, c, b, ladder=False, **k: c in set(cells) and not ladder).ok))
    fails = [name for name, ok in out if ok]
    return Check("O-NEG", not fails, ("these did NOT go red: %s" % fails) if fails else
                 "%d in-memory mutations, every one went red" % len(out))


def run_offline():
    checks = [o1_defs(), o2_settings_defaults(), o3_unbuilt_register(), o4_geometry(), o5_oracle_selftest(),
              o6_channel_directions(), o7_scene_predictions(), o8_lint(), o9_shared_source(), o10_pit_width(),
              offline_negative_controls()]
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
        def __init__(self, live, name, planned):
            self.l, self.name, self.planned = live, name, planned

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
                rec["step"], rec["ticks"], rec["planned"] if "planned" in rec else self.planned, rec["wall_s"],
                rec["calls"], (" ERROR " + rec["error"]) if rec["error"] else ""))
            if et is Abort or et is None:
                return False
            # an unexpected exception inside a step is a HARNESS defect: record, keep going
            self.l.row(self.name + "_crash", False, "HARNESS", "%s: %s" % (et.__name__, ev), status="UNMEASURED")
            return True

    def step(self, name, planned):
        return Live._Step(self, name, planned)

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

    def pulses(self, n, tag):
        """n pulses at 0 ticks via jawa/flowworks_pulse over EVERY excavated cell; the oracle
        runs the same n pulses; returns (ok, per-scene live vectors, record)."""
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


def _load_site_spec():
    sys.path.insert(0, HERE)
    import site_spec as S          # noqa: E402
    return S


try:
    _SETTINGS = _load_site_spec().SETTINGS
except Exception:                  # noqa: BLE001 - offline use without modcheck paths still works
    _SETTINGS = {}

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
    with L.step("L_preflight", 0):
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
        pristine = e.get("excavatedCellCount") == 0 and e.get("bodyCount") == 0 and e.get("superdeepCellCount") == 0
        dry = rate is not None and rate <= 0.01
        _fold(L, "L1_fresh_map", [
            ("loaded_paused", ui.get("programState") == "Playing" and e1.get("ticksGame") == e2.get("ticksGame"), "SITE",
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
        # log gate + sanity probe (the journal must hold the RimBridge start line)
        lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
        logs = lg.get("logs") or []
        L.log_base = max([x.get("Sequence", 0) for x in logs] or [0])
        bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs)
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
        for typ, fields in sorted(_SETTINGS.items()):
            for f, want_v in sorted(fields.items()):
                v = L.sget(typ, f)
                if not _settings_equal(v, want_v):
                    drift.append("%s=%s (ship %s)" % (f, v, want_v))
        n_set = sum(len(v) for v in _SETTINGS.values())
        if drift and args.reset_settings:
            for typ, fields in _SETTINGS.items():
                for f, want_v in fields.items():
                    L.touched.add((typ, f))
            L.restore_settings()
            set_part = ("settings_default", False, "HARNESS", "drift RESET by --reset-settings: %s" % drift[:6])
        else:
            set_part = ("settings_default", not drift and n_set >= 31, "HARNESS",
                        drift[:6] or "%d settings read, all shipped defaults" % n_set)
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
        pawn_part = ("no_pawn_in_plots", not inside, "SITE", inside or "%d pawns, none in %d plot rects" % (
            len(pw.get("pawns") or []), len(rects)))
        if inside:
            _fold(L, "L4_site_ready", [pawn_part])
            raise Abort("a pawn stands in a plot rect")
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
        L.o = PulseOracle(MAP_W, MAP_H, src, bodies, sink_band=SINK_BAND, algo="fixed", recession=True)


def _pos(p):
    q = p.get("position") or {}
    return (q.get("x", p.get("x")), q.get("z", p.get("z")))


def _in_any(c, rects):
    return c[0] is not None and any(r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3] for r in rects)


# ---------------------------------------------------------------------------- phase S (0 ticks)
def phase_S(L, args):
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
            bad = [] if got["W8"].get("limitless") is True else ["W8 (edge, 64) not limitless: %r" % got["W8"]]
            for k in ("W2", "W2R", "W3", "W4", "W5"):
                want_c = float(BODIES[k].get("capacity", 5 * len(BODIES[k]["cells"])))
                g = got[k]
                if g.get("limitless") is not False or abs((g.get("capacity") or 0) - want_c) > 1e-3 \
                        or abs((g.get("stock") or 0) - want_c) > 1e-3 or g.get("cellCount") != len(BODIES[k]["cells"]):
                    bad.append("%s %r (want limited cap %s)" % (k, g, want_c))
            L.row("S3_classification", not bad, "MOD", bad or "W1, W8 limitless; W2/W2R 5, W3 10, W4 (edge,40) 200, "
                  "W5 (interior,64) 320 all LIMITED")
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
            if g.get("limitless") is not None:
                L.o.bodies[k]["limitless"] = bool(g["limitless"])
                if not g["limitless"]:
                    L.o.bodies[k]["stock"] = float(g.get("stock") or 0)
                    L.o.bodies[k]["capacity"] = float(g.get("capacity") or 0)
        # S6 (was UNCOVERED until jawa/flowworks_job_probe, 2026-10-02): designate_batch bypasses
        # Designator_DigCanal.CanDesignateCell, so ask the designator itself. D=1 deepens with the
        # toggle ON and is refused OFF; D=4 is refused either way; undug soil is accepted even OFF
        # (the toggle gates DEEPENING only -- the control that makes "refused OFF" mean something).
        undug = SCENES["S2_clamp"]["cells"][1]
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
            L.row("S6_digToDepth_gate", acc(on1) is True and acc(on4) is False and "SUPERDEEP" in why(on4)
                  and acc(off1) is False and "Deepening" in why(off1) and acc(off0) is True, "MOD",
                  "Designator_DigCanal: D1 ON %s; D4 %s (%s); D1 OFF %s (%s); undug soil OFF %s" % (
                      acc(on1), acc(on4), why(on4)[:40], acc(off1), why(off1)[:50], acc(off0)))
        s, d = _src_all(), _xml_blocks()
        for bar, (fact, pred) in sorted(UNBUILT.items()):
            L.row("U_" + bar, True, "PROMOTE", ("UNBUILT: %s" % fact) if pred(s, d) else
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
        sink0, drained0 = L.eng().get("sinkTransferredTotal"), L.o.drained
        probs, mism, vec, rec = L.pulses(8, "A")
        _fold(L, "A0_instrument", [probe, ("pulse_contract", not probs, "HARNESS",
                                           probs or "8 pulses, 0 ticks, scheduler untouched, paused")])
        L.vec.update(vec)
        # the per-direction E2_east_A/B/north/south/west rows and E2s_shared_source_oracle were each "scene == oracle
        # at every pulse": G_every_cell_vs_oracle fails whenever any of them would, naming the scene (cut 2026-10-05)
        L.gmism["A"] = mism
        L.row("E2_twins_identical", vec.get("E2_east_A") == vec.get("E2_east_B"), "MOD",
              "A %s / B %s" % (vec.get("E2_east_A", [])[:4], vec.get("E2_east_B", [])[:4]))
        full = {k: next((p + 1 for p, v in enumerate(vec.get(k, [])) if v == [1] * 4), None)
                for k in ("E2_east_A", "E2_north", "E2_south", "E2_west")}
        L.row("E2_channels_fill_every_direction", all(v == 4 for v in full.values()), "MOD",
              "first-full pulse by direction %s (bound n*D = 4; FLOWWORKS_CHANNEL_OSCILLATION_1 regression guard)" % full)
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
        L.row("E3b_recession_shipped", "E3b_recede" not in mism and sum(e3b) == 1 and brec.get("recededCount") == 1
              and abs((brec.get("stock") if brec.get("stock") is not None else -9) - 4.0) < 0.05, "MOD",
              "final %s, W2R %s" % (e3b, {k: brec.get(k) for k in ("stock", "recededCount", "activeCellCount")}))
        sink1 = L.eng().get("sinkTransferredTotal")
        L.row("E5_sink_drains", "E5_sink" not in mism and abs((sink1 - sink0) - (L.o.drained - drained0)) < 1e-3
              and (L.o.drained - drained0) > 0, "MOD", mism.get("E5_sink", "")[:3] or
              "band run drained per oracle: sinkTransferredTotal +%s (oracle +%s); final %s" % (
                  sink1 - sink0, L.o.drained - drained0, vec.get("E5_sink", [[]])[-1]))
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
            probs, mism, vec, rec = L.pulses(7, "B")
            b = Live.body_in(rec, L.ids.get("W2"))
            v = vec.get("E3_budget", [[]])
            L.row("E3_budget_exhaustion", not probs and "E3_budget" not in mism and sum(v[-1]) == 5 and v[-1] == v[-2]
                  and (b.get("stock") if b.get("stock") is not None else 9) < 1, "MOD",
                  (probs, mism.get("E3_budget", "")[:3]) if (probs or mism) else
                  "cap-5 pond delivered exactly 5 (%s), then rested; stock %s" % (v[-1], b.get("stock")))
            L.sset(S_FW, "sourceBudgetEnabled", False)
            L.o.budget = False
            try:
                probs, mism, vec, rec = L.pulses(2, "B-off")
                v2 = vec.get("E3_budget", [[]])
                L.row("E3n_budget_off_supplies", not probs and "E3_budget" not in mism and sum(v2[-1]) > 5, "MOD",
                      (probs, mism.get("E3_budget", "")[:3]) if (probs or mism) else
                      "budget OFF: a spent pond supplies again (%s -> %s)" % (v[-1], v2[-1]))
                L.gmism["B"] = mism
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
            s1 = L.eng().get("sinkTransferredTotal")
            L.row("E5n_sinks_off", not probs and "E5_sink_off" not in mism and vec.get("E5_sink_off", [[]])[-1] == [1] * 10
                  and s1 == s0 and not any(x.get("isSink") for x in q), "MOD",
                  "sinks OFF: run %s, total %s->%s, isSink any=%s" % (vec.get("E5_sink_off", [[]])[-1], s0, s1,
                                                                    any(x.get("isSink") for x in q)))
        finally:
            L.sset(S_FW, "edgeSinksEnabled", True)
            L.o.sink_band = SINK_BAND
        d0, s0 = L.o.drained, L.eng().get("sinkTransferredTotal")
        probs, mism, vec, rec = L.pulses(3, "C-on")
        s1 = L.eng().get("sinkTransferredTotal")
        L.row("E5_sinks_back_on", not probs and "E5_sink_off" not in mism and abs((s1 - s0) - (L.o.drained - d0)) < 1e-3
              and L.o.drained > d0, "MOD", "sinks ON again: %s, total +%s (oracle +%s)" % (
                  vec.get("E5_sink_off", [[]])[-1], s1 - s0, L.o.drained - d0))
        L.gmism["C"] = mism


# ---------------------------------------------------------------------------- phase R (0 ticks)
def phase_R(L, args):
    with L.step("R_determinism_rerun", 0):
        L.dig_scene("E2_rerun")
        probs, mism, vec, rec = L.pulses(8, "R")
        a, r = L.vec.get("E2_east_A"), vec.get("E2_rerun")
        L.row("E2_rerun_determinism", not probs and a is not None and a == r and "E2_rerun" not in mism, "MOD",
              "E2_east_A (phase A) %s vs E2_rerun (dug later, other body) %s" % ((a or [])[:4], (r or [])[:4]))
        L.gmism["R"] = mism
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
        L.sset(S_FW, "depthEngineEnabled", False)
        eo = L.eng()
        n0 = eo.get("nextPulseTick")
        # the OFF window must STRADDLE the scheduled tick, or an engine that ignores the toggle
        # would pass too (it would simply not be due yet). The jobs progress meanwhile: free.
        off_ticks = max(0, n0 - eo.get("ticksGame")) + PULSE_PIN
        B.call("rimworld/step_game_ticks", ticks=off_ticks, pauseFirst=True, timeoutMs=300000)
        e1 = L.eng()
        snap1 = _snapshot(L)
        moved = sorted(c for c in snap0 if snap0[c] != snap1.get(c))
        L.row("E4_engine_off", e1.get("nextPulseTick") == n0 and not moved and e1.get("ticksGame") > n0,
              "MOD", "OFF for %s ticks, past the due tick %s: nextPulseTick %s->%s, cells moved %s" % (
                  e1.get("ticksGame") - e0.get("ticksGame"), n0, n0, e1.get("nextPulseTick"), moved[:4]))
        L.sset(S_FW, "depthEngineEnabled", True)
        # --- E1b: pin below the clamp floor; the engine must clamp to 60
        L.sset(S_FW, "pulseIntervalTicks", 30.0)
        e2 = L.eng()
        L.row("E1b_pulse_clamp", e2.get("pulseIntervalTicks") == PULSE_PIN, "MOD",
              "pulseIntervalTicks set 30 -> engine reads %s (clamp floor %d)" % (e2.get("pulseIntervalTicks"), PULSE_PIN))
        hist, chunks, done = [], 0, {}
        t_start = e2.get("ticksGame")
        while True:
            B.call("rimworld/step_game_ticks", ticks=PULSE_PIN, pauseFirst=True, timeoutMs=120000)
            chunks += 1
            e = L.eng()
            hist.append((e.get("ticksGame"), e.get("nextPulseTick")))
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
        gaps = [b[1] - a[1] for a, b in zip(hist, hist[1:])]
        lead = [n - t for t, n in hist]
        L.row("E1c_cadence_real_scheduler", all(g == PULSE_PIN for g in gaps) and all(0 < x <= PULSE_PIN for x in lead)
              and chunks >= 2, "MOD", "%d chunks of %d ticks: nextPulseTick advances %s, lead %s" % (
                  chunks, PULSE_PIN, sorted(set(gaps)), sorted(set(lead))))
        # one scheduled pulse per 60-tick chunk (the first fires at once: nextPulseTick was frozen in the past)
        for _ in range(chunks):
            L.o.pulse()
        snap2 = _snapshot(L)
        diff = sorted((c, snap2.get(c), (L.o.D.get(c, 0), L.o.F.get(c, 0))) for c in snap2
                      if snap2[c] != (L.o.D.get(c, 0), L.o.F.get(c, 0)))
        e4 = [snap2[c][1] for c in SCENES["E4_engine"]["cells"]]
        L.row("E4_engine_on_scheduled", not diff and sum(e4) > 0, "MOD", diff[:4] or
              "after %d real scheduled pulses every oracle cell == oracle; E4 channel %s" % (chunks, e4))
        wr = (B.call("jawa/weather_get").get("weather") or {}).get("rainRate") or 0.0
        would = 0.5 * wr * chunks * 1.0          # levels the rain WOULD have added (rate rose ~linearly)
        if wr <= 0.01 or would < 1.5:
            L.row("E6n_rain_toggle_off", False, "HARNESS", "rain too light to test: rate %s over %d pulses would add "
                  "~%.2f levels (< 1.5)" % (wr, chunks, would), status="UNMEASURED")
        else:
            L.row("E6n_rain_toggle_off", not diff, "MOD", "rain fell (rate now %.3f) with rainFillsExcavations OFF over %d "
                  "pulses: no cell gained" % (wr, chunks) if not diff else diff[:4])
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
        if done.get("E7a"):
            s_after = sum(q["f"] for q in q7["E7a_fillin"])
            mid = q7["E7a_fillin"][1]
            L.row("E7a_fillin_displaces", s_after == sum7["E7a_fillin"] and mid.get("terrain") == "Soil" and not mid["isExcavated"],
                  "MOD", "sum F %s -> %s (conserved), middle D=%s terrain %s, vector %s" % (
                      sum7["E7a_fillin"], s_after, mid["d"], mid.get("terrain"), [q["f"] for q in q7["E7a_fillin"]]))
        else:
            L.row("E7a_fillin_displaces", False, "UNRESOLVED", "job not done in %d ticks (cap %d): %s" % (spent, cap, jobs_info),
                  status="UNMEASURED")
        if done.get("E7b"):
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
        if not L.row("E6_roof_readback", o_roof in roofed and o_open not in roofed, "SITE",
                     "roofed excavated cells %s" % sorted(roofed)[:6]):
            return
        if rate <= 0.01:
            L.row("E6_rain_fills_unroofed", False, "HARNESS", "rainRate %s <= 0.01" % rate, status="UNMEASURED")
            return
        k = 1
        while acc + k * rate < 1.0 + 0.02 or abs((acc + k * rate) - round(acc + k * rate)) < 0.02:
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
    for p in o.get("pawns") or []:
        if p.get("id") == pid:
            return p
    return {}


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
        L.row("P2_fillin_releases_large", f.get("success") and f.get("depth") == 3 and pw.get("held") is False
              and (pw.get("lipReachable") or 0) > 0 and rp.get("pitWidth") == 1, "MOD",
              "fill-in (161,101) -> D %s; large at (160,100): width %s held %s lip %s/%s" % (
                  f.get("depth"), rp.get("pitWidth"), pw.get("held"), pw.get("lipReachable"), pw.get("lipCells")))
        # FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner, 2026-10-06): "You can't fall in by careless colonist pathing.
        # Only if they get blown/forced in do they fall." RM_PitPathing refuses a walk into a LADDERLESS open D=4
        # cell, so: P3 = the refusal itself (own-faction capture ON, the pawn still stays out); P4 = the colonist
        # climbs DOWN a lowered ladder (no fall), is not held, and walks out. No bridge call forces a pawn into a
        # pit (no teleport/knockback tool), so the forced-fall half of the old P3 (descent event, fall damage) is
        # covered by no row here; a forced-entry row needs a driver (flyer landing / explosive knockback).
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
            L.row("P3_walk_in_held", o_in.get("arrived") is False and pw is None and not rec
                  and (end.get("x"), end.get("z")) != wc and (r_in.get("descentCount") or 0) == d0
                  and r_in.get("hasLadder") is False, "MOD",
                  "ladderless D=4 (FLOWWORKS_PIT_FALL_ONLY_FORCED_1: pathing never drops a colonist in), capture ON: "
                  "ordered in -> arrived %s, in the pit cell %s, own descents %d (map-wide %s->%s), ended %s, hasLadder %s" % (
                      o_in.get("arrived"), pw is not None, len(rec), d0, r_in.get("descentCount"),
                      (end.get("x"), end.get("z")), r_in.get("hasLadder")))
            # P4: a lowered ladder in the pit cell -> the same colonist climbs down (no fall), is not held, walks out.
            sb = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % wc)
            ok_rd, lrd, _ = _proof(B, "ProofLadder", "%d,%d,lower" % wc)    # lowered: the state the row is about
            o_l_in = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1], waitTicks=PIT_WAIT_IN, draft=True), a)
            r_l = B.call("jawa/flowworks_pit_report", x=wc[0], z=wc[1])
            pl = _pit_pawn(r_l, a) or {}
            rec_l = [d for d in r_l.get("recentDescents") or [] if d.startswith(a + "@")]
            o_l = _order_row(B.call("jawa/order_pawn", pawnId=a, x=wc[0], z=wc[1] + 3, waitTicks=PIT_WAIT_OUT, draft=True), a)
            L.row("P4_ladder_frees", ok_rd and lrd.get("raised") == "False" and r_l.get("hasLadder") is True
                  and o_l_in.get("arrived") is True and pl.get("spawned") is True and not rec_l and pl.get("held") is False
                  and (pl.get("lipReachable") or 0) > 0 and o_l.get("arrived") is True, "MOD",
                  "ladder spawned %s lowered %s hasLadder %s; climbed down: arrived %s, falls %d, held %s lip %s/%s; "
                  "ordered out: arrived %s; %s" % (
                      sb.get("success"), lrd.get("raised") == "False", r_l.get("hasLadder"), o_l_in.get("arrived"),
                      len(rec_l), pl.get("held"), pl.get("lipReachable"), pl.get("lipCells"), o_l.get("arrived"),
                      alive(r_l, a)))
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
                L.row("P4b_ladder_raised_strands", lr.get("raised") == "True" and lr.get("inspect", "").lower().startswith("ladder_up")
                      and pu.get("held") is True and pu.get("lipReachable") == 0 and o_up.get("canReach") is False
                      and ll.get("raised") == "False" and ll.get("inspect", "").lower().startswith("ladder_down") and pd.get("held") is False
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
        B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % tuple(strip[-1]))
        _proof(B, "ProofLadder", "%d,%d,lower" % tuple(strip[-1]))
        _, k0, _ = _proof(B, "ProofPawnSink", col)
        o_in = _order_row(B.call("jawa/order_pawn", pawnId=col, x=strip[-1][0], z=strip[-1][1], waitTicks=PIT_WAIT_IN, draft=True), col)
        ok4, k4, t4 = _proof(B, "ProofPawnSink", col)
        o_out = _order_row(B.call("jawa/order_pawn", pawnId=col, x=X_WALK[0], z=X_WALK[1], waitTicks=PIT_WAIT_IN, draft=True), col)
        ok0, k1, t1 = _proof(B, "ProofPawnSink", col)
        L.row("X2_pawn_lowers_walking_in", ok4 and o_in.get("arrived") is True and _sink_ok(k0, 0) and _sink_ok(k4, 4), "MOD",
              "walked D0->D4 arrived %s: sink %s -> %s (drawDz %s) %s" % (o_in.get("arrived"), k0.get("sink"), k4.get("sink"),
                                                                       k4.get("drawDz"), "" if ok4 else t4))
        L.row("X3_pawn_rises_walking_out", ok0 and o_out.get("arrived") is True and _sink_ok(k4, 4) and _sink_ok(k1, 0), "MOD",
              "walked D4->D0 arrived %s: sink %s -> %s (drawDz %s) %s" % (o_out.get("arrived"), k4.get("sink"), k1.get("sink"),
                                                                       k1.get("drawDz"), "" if ok0 else t1))
        try:
            wall = float(k4.get("sink")) / FEET_TO_HEAD
        except (TypeError, ValueError):
            wall = None
        L.row("X4_pit_wall_over_head", ok4 and _sink_ok(k4, 4) and wall is not None and wall >= 1.2 - 1e-6
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
        _, race3, kv3 = _fluid_row(L, rt + rw)
        _xpulse(L, 9)
        okr, rows, kv = _fluid_row(L, two + rt + rw)
        t3, w3 = _level_at(race3, rt), _level_at(race3, rw)
        t12, w12 = _level_at(rows, rt), _level_at(rows, rw)
        L.row("X7_tar_front_lags_water", okr and w3[0] == 3 and t3[0] in (0, 1) and t12[0] == 2 and w12[0] == 3
              and t12[1] == w12[1] == 1 and t12[2] == [TAR] and w12[2] == [WATER], "MOD",
              "gravity staircase D1..D4, one level each: after 3 pulses water at step %s, tar at %s; after 12 water %s, "
              "tar %s (stride 6 PROVISIONAL = 360/60 ticksPerTile); levels %s/%s; pulse %s viscosity %s" % (
                  w3[0], t3[0], w12[0], t12[0], w12[1], t12[1], kv.get("pulse"), kv.get("viscosity")))
        tar_f = sum(rows.get(c, {}).get("f", 0) for c in tar_row)
        wat_f = sum(rows.get(c, {}).get("f", 0) for c in water_row) + rows.get(X_JUNCTION, {}).get("f", 0)
        wrong = [c for c in tar_row if rows.get(c, {}).get("f") and rows[c]["fluid"] != TAR] + \
                [c for c in water_row + [X_JUNCTION] if rows.get(c, {}).get("f") and rows[c]["fluid"] != WATER]
        tt = {rows[c]["terrain"] for c in tar_row if rows.get(c, {}).get("f")}
        wt = {rows[c]["terrain"] for c in water_row if rows.get(c, {}).get("f")}
        j = rows.get(X_JUNCTION, {})
        L.row("X6_two_fluids_distinct", okr and not wrong and tar_f == 4 and wat_f == 4 and j.get("fluid") == WATER
              and j.get("f") == 1 and len(tt) == 1 and len(wt) == 1 and not (tt & wt)
              and not any(t.startswith("RM_Channel") for t in tt | wt), "MOD",
              "tar row %s levels drawn %s | water row+junction %s levels drawn %s | junction %s F=%s (water reached it "
              "first, one level by gravity; tar refused: no-mix) | wrong-fluid cells %s" % (tar_f, sorted(tt), wat_f, sorted(wt), j.get("fluid"),
                                                                       j.get("f"), wrong[:3]))
        okf, tf = _fill_fluid(L, ro[0], 1, TAR)      # filled only now: ON it would still sit at step 0..1
        L.sset(S_FW, "viscosityEnabled", False)
        try:
            _xpulse(L, 3)
            _, roff, kvo = _fluid_row(L, ro)
        finally:
            L.sset(S_FW, "viscosityEnabled", True)
        toff = _level_at(roff, ro)
        L.row("X7n_viscosity_off", okf and toff[0] == 3 and toff[2] == [TAR] and kvo.get("viscosity") == "False", "MOD",
              "viscosityEnabled OFF: a tar staircase moved like water, step %s after 3 pulses (levels %s, %s)" % (
                  toff[0], toff[1], toff[2]))

        # X8/X9 pit_covered_invisible + seam: a 2x2 woven-scrap deck over a D=4 pit.
        cov = SCENES["X_cover"]["cells"]
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
        L.row("X9_cover_deck_uniform", len(printed) == 1 and printed == around, "MOD",
              "deck prints %s; ring terrain %s (one surface: no seam between deck cells or at the lip; the frame is "
              "still the judge's)" % (sorted(printed), sorted(around)))
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        _x10_canal_fire(L)


FIRE_TYPE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
FLAME, ASH = "RM_LiquidFlame", "Filth_Ash"
FIRE_FAST_BURN_DAYS = 0.02         # canalBurnDaysPerLevel for X10 only: 1,200 ticks per level instead of a day


def _things_at(B, def_name, cells):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    r = B.call("jawa/list_things", defName=def_name, rect="%d,%d,%d,%d" % (min(xs) - 1, min(zs) - 1, max(xs) - min(xs) + 3,
                                                                          max(zs) - min(zs) + 3), limit=200)
    pos = [t.get("position") or t for t in (r.get("things") or [])]    # live nests x/z under "position"
    return {(p.get("x"), p.get("z")) for p in pos} if r.get("success") else None


def _x10_canal_fire(L):
    """X10 (promoted 2026-10-05 from the extension plot_E_fire): a 1x6 D=1 tar run lit at its far end by
    RM_LiquidFireProof.ProofIgnite (the engine's IgniteNow, same queue a vanilla Fire or a bomb feeds).
    canal_burning: the creeping front (tar 120 ticks/cell) puts a flame on >= 3 run cells and on NO cell off the run;
    canal_fire_persists: still alight 250 ticks later; canal_spent: with canalBurnDaysPerLevel cut to 0.02 for this
    row only (a rate knob, restored in finally) every cell burns to F=0 and is left ashed, nothing alight.
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
    L.sset(S_FW, "canalBurnDaysPerLevel", FIRE_FAST_BURN_DAYS)
    try:
        ok, _, lit = _proof(B, "ProofIgnite", "%d,%d" % run[-1], typ=FIRE_TYPE)
        if not (ok and lit.startswith("LIT")):
            L.row("X10_canal_fire", False, "MOD", "a lit tar cell refused the light: %s" % lit[:200])
            return
        B.call("rimworld/step_game_ticks", ticks=750)
        burn1 = _things_at(B, FLAME, run)
        B.call("rimworld/step_game_ticks", ticks=250)
        burn2 = _things_at(B, FLAME, run)
        # 6000, not 3000: a burned-out cell takes a level back from its neighbour by flow (tar, stride 6), which
        # relights it and stretches the burn (live 19:53: 5 of 6 spent at 4,000 ticks, the last still alight)
        trace = []                 # (ticks, nextPulseTick, engine pulse interval, F vector): why a burn stalls
        for _ in range(6):
            B.call("rimworld/step_game_ticks", ticks=1000)
            e = B.call("jawa/flowworks_engine_state")
            _, fr, _ = _fluid_row(L, run)
            fv = [fr.get(c, {}).get("f") for c in run]
            trace.append((e.get("ticksGame"), e.get("nextPulseTick"), e.get("pulseIntervalTicks"), "".join(str(f) for f in fv)))
            if not any(fv):
                break
        burn3 = _things_at(B, FLAME, run)
        ash = _things_at(B, ASH, run)
        _, rows, _ = _fluid_row(L, run)
        _, _, rep = _proof(B, "ProofReport", " ", typ=FIRE_TYPE)    # " ": static_call reads "" as ZERO args
    finally:
        L.sset(S_FW, "canalBurnDaysPerLevel", 1.0)
        L.sset(S_FW, "rainDousesLiquidFireEnabled", True)
        L.sset(S_FW, "rainFillsExcavationsEnabled", True)
    if burn1 is None or ash is None:
        L.row("X10_canal_fire", False, "HARNESS", "list_things unreadable", status="UNMEASURED")
        return
    off_run = sorted((burn1 | burn2) - set(run))
    left = [c for c in run if rows.get(c, {}).get("f", 1) != 0]
    parts = [("burning >=3 run cells", len(burn1 & set(run)) >= 3), ("no flame off the run", not off_run),
             ("persists 250 ticks", len(burn2 & set(run)) >= 1), ("spent: all F=0", not left),
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
        lg = B.call("rimbridge/list_logs", afterSequence=L.log_base, limit=500, minimumLevel="warning")
        logs = lg.get("logs") or []
        txt = lambda x: (x.get("Message") or "") + " " + (x.get("StackTrace") or "")  # noqa: E731
        errs = [(x.get("Level"), x.get("RepeatCount"), (x.get("Message") or "")[:200]) for x in logs
                if (x.get("Level") or "").lower() in ("error", "exception") and any(m in txt(x) for m in LOG_MARKERS)]
        other = [(x.get("Level"), (x.get("Message") or "")[:120]) for x in logs if (x.get("Level") or "").lower() in ("error", "exception")]
        unbal = [x.get("Message", "")[:200] for x in logs if "does not balance" in txt(x)]
        exc_n = sum(int(x.get("RepeatCount") or 1) for x in logs if "conservation exception" in txt(x))
        if exc_n < 1:
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
        "no_recession": ["E3b_recession_shipped"],
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
        "pit_no_fall": [],      # forced-fall event: no bridge call forces a pawn in, so no live row reads it (see phase_P)
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
        "fire_never_spreads": ["X10_canal_fire"],                     # the front never leaves the lit cell
        "fire_never_burns": ["X10_canal_fire"],                       # a burning cell never spends its liquid
        "fire_no_ash": ["X10_canal_fire"],                            # a spent cell is not left scorched
    }

    def __init__(self, faults=()):
        self.faults = set(faults)
        self.n = 0
        self.tick = 1
        self.settings = {t: dict(f) for t, f in _SETTINGS.items()}
        if "settings_drift" in self.faults:
            self.settings[S_FW]["flowPerPulse"] = 2.0
        self.terrain = {}
        self.roof = set()
        self.o = PulseOracle(MAP_W, MAP_H, {}, {}, sink_band=SINK_BAND,
                             algo="old" if "oscillate" in self.faults else "fixed", recession=True)
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
        self.descents = []
        self.fire, self.fire_pend, self.ash = {}, {}, set()   # X10 fire model: cell -> burn acc / due tick; ashed cells

    # ---- pit model (SUPERDEEP_HOLDER_RETIRE_1): the grid trap rule over the oracle's D map
    PIT_BS = {"Hare": 0.2, "Muffalo": 2.4, "Colonist": 1.0}

    def d4(self, c):
        return self.o.D.get(c, 0) >= 4

    def pit_cells(self):
        return [c for c, d in self.o.D.items() if d >= 4]

    def captured(self, p):
        return p["faction"] != "player" or (self.S("superdeepCapturesOwnFaction")
                                            and "pit_carveout_ignored" not in self.faults) \
            or "pit_carveout_ignored" in self.faults

    def held(self, p, c=None):
        c = p["pos"] if c is None else c
        cells = self.pit_cells()
        bs = 0.0 if "pit_holds_any" in self.faults else p["bs"]
        lad = c in self.ladders and (c not in self.raised or "ladder_raise_ignored" in self.faults)
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
                             held=self.held(p) if "pit_holds_any" not in self.faults else self.held(p),
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
        return dict(success=True, thingsPlaced=1)

    def t_jawa_order_pawn(self, pawnId, x=-1, z=-1, waitTicks=300, draft=True, **kw):
        p = self.mp[pawnId]
        dest, start = (x, z), p["pos"]
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
            arrived=p["pos"] == dest, canReach=can, orderAccepted=True)])

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
        o.recession = self.S("recessionEnabled") and "no_recession" not in self.faults
        o.sink_band = SINK_BAND if (self.S("edgeSinksEnabled") or "sink_toggle_ignored" in self.faults) else None
        o.rain_on = self.S("rainFillsExcavationsEnabled") or "rain_toggle_ignored" in self.faults
        o.rain_per, o.rain_rate = float(self.S("rainFillPerPulse")), self.rain_rate()
        o.roofed = set() if "roof_ignored" in self.faults else set(self.roof)
        o.viscosity = ("viscosity_ignored" not in self.faults) and (
            self.S("viscosityEnabled") or "viscosity_toggle_ignored" in self.faults)

    def do_pulse(self):
        self.sync()
        d0 = self.o.drained
        self.o.pulse()
        self.sink_total += self.o.drained - d0

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
        lim = sticky and edge and len(seen) >= 50
        cap = 5.0 * len(seen)
        self.o.bodies[name] = dict(limitless=lim, stock=0.0 if lim else cap, capacity=None if lim else cap,
                                   cells=sorted(seen, key=self.o.idx), id=self.body_seq)
        for x in seen:
            self.classified[x] = name
            self.o.src[x] = name
        return name

    def body_rec(self, name):
        b = self.o.bodies[name]
        rec = b.get("receded", [])
        return dict(id=b["id"], limitless=b["limitless"], stock=b["stock"] if not b["limitless"] else 0.0,
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

    def fill_in(self, c):
        d, f = self.o.D.get(c, 0), self.o.F.get(c, 0)
        nd = d - 1
        disp = max(0, f - nd)
        if nd <= 0:
            self.o.D.pop(c, None)
            self.o.F.pop(c, None)
        else:
            self.o.D[c], self.o.F[c] = nd, f - disp
        if disp and "fillin_leak" not in self.faults:
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                while disp and self.o.exc(n) and self.o.F[n] < self.o.D[n]:
                    self.o.F[n] += 1
                    disp -= 1
            if disp:
                self.overflow += disp
                self.log("warning", "[RimMandrake.FlowWorks] conservation exception: %.1f fill-units overflowed" % disp)

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
        if setFill >= 0 and self.o.exc(c):
            self.o.F[c] = setFill if "clamp_broken" in self.faults else min(setFill, self.o.D[c])
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
                acc, why = False, "Already SUPERDEEP — this is as far down as digging goes."
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
        snap = lambda p: dict(pulse=p, fill=[self.o.F.get(c, 0) for c in cells], depth=[self.o.D.get(c, 0) for c in cells],  # noqa: E731
                              bodies=[self.body_rec(n) for n in self.o.bodies])
        pulses = [snap(0)]
        for p in range(1, count + 1):
            self.do_pulse()
            pulses.append(snap(p))
        return dict(success=True, cells=[dict(x=c[0], z=c[1]) for c in cells], pulses=pulses, pulsesRun=count,
                    ticksBefore=self.tick, ticksGame=self.tick, nextPulseTickUntouched=True, gamePaused=True)

    def t_jawa_spawn_pawn(self, kindDef, faction, x, z, count=1):
        pid = "M%d" % len(self.pawns)
        self.pawns.append(dict(id=pid, position=dict(x=x, z=z)))
        self.mp[pid] = dict(kind=kindDef, pos=(x, z), faction=faction, bs=self.PIT_BS.get(kindDef, 1.0))
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

    # ---- X10 fire model (RM_LiquidFire, CreepingFuse tar 120 ticks/cell; burn = canalBurnDaysPerLevel per level)
    BURNABLE = ("RM_Fluid_Tar", "RM_Fluid_Oil")

    def burnable(self, c):
        return self.o.exc(c) and self.o.F.get(c, 0) > 0 and self.o.fluid.get(c) in self.BURNABLE

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
        per = max(1, int(round(60000 * max(0.01, float(self.S("canalBurnDaysPerLevel"))))))
        for c in list(self.fire):
            self.fire[c] += pulse_ticks
            while self.fire.get(c, 0) >= per:
                self.fire[c] -= per
                self.o.F[c] = max(0, self.o.F.get(c, 0) - 1)
                if self.o.F[c] == 0:
                    del self.fire[c]
                    if "fire_no_ash" not in self.faults:
                        self.ash.add(c)

    def t_jawa_list_things(self, defName=None, rect=None, limit=200, **kw):
        x, z, w, h = map(int, rect.split(","))
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
        o = self.o
        res = None
        if method == "ProofFillWithFluid":
            x, z, f, fl = args.split(",")
            c, f = (int(x), int(z)), int(f)
            if not o.exc(c) or (o.F.get(c, 0) > 0 and o.fluid.get(c, "RM_Fluid_Water") != fl):
                res = "REFUSED: %s not excavated or holds another fluid" % (c,)
            else:
                o.F[c] = min(f, o.D[c])
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
                    c[0], c[1], up, "Ladder_up:_nobody_can_climb_down_or_out." if up else "Ladder_down:_anyone_can_climb.")
        elif method == "ProofCover":
            x, z = map(int, args.split(","))
            c = (x, z)
            ring = [self.terrain_of((x + dx, z + dz)) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                    if (dx or dz) and not o.exc((x + dx, z + dz))]
            around = max(sorted(set(ring)), key=ring.count) if ring else "none"
            printed = self.terrain_of(c) if "cover_shows_hole" in self.faults else around
            res = "COVER cell=%d,%d present=%s covered=%s sprung=False depth=%d cellTerrain=%s printed=%s matOk=True around=%s inspect=Gives_way_under_40_kg" % (
                x, z, c in self.covers, c in self.covers, o.D.get(c, 0), self.terrain_of(c), printed, around)
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
        return r if isinstance(r, dict) else {"success": False, "raw": r}


FROZEN_BIOMES = ("IceSheet", "SeaIce")   # temp-layer ice the site painter cannot clear (run 6)
PHASES = ("L", "site", "S", "A", "B", "C", "R", "J", "rain", "P", "X", "tail")


def run_live(args, B=None, quiet=False):
    B = B or (MockBridge(args.fault or []) if args.mock else RealBridge())
    L = Live(B, progress=None if args.mock else args.progress, mock=args.mock)
    t0 = time.time()
    load = None
    if args.fresh_map:
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
        L.row("ABORT", False, "SITE" if "pristine" in aborted or "pawn" in aborted else "HARNESS", aborted)
    finally:
        bad = L.restore_settings()
        L.row("Z_settings_restored", not bad, "HARNESS", bad or "%d touched settings back to shipped defaults" % len(L.touched))
        B.call("jawa/weather_set", weather="Clear", unlock=True)
        if args.mock:
            B.finish()
            if aborted is None and any(r["id"] == "E9_log_budget" for r in L.rows):
                pass
    ticks1 = L.eng().get("ticksGame")
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
            return [r["id"] for r in run_live(A, quiet=True)["rows"]]
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
    for fault, rows in sorted(MockBridge.FAULTS.items()):
        a = A()
        a.fault = [fault]
        r = run_live(a)
        st = {x["id"]: x["status"] for x in r["rows"]}
        if any(st.get(row) in ("PASS", None) for row in rows) and not r["aborted"]:
            probs.append("fault %s: rows %s stayed %s" % (fault, rows, [st.get(x) for x in rows]))
        elif r["aborted"] and fault not in ("settings_drift", "dll_stale"):   # both fold L2 red, then abort by design (d07fd3b37)
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
    diff = [i for i in ids if (ra[i]["status"], norm(ra[i]["detail"])) != (rb[i]["status"], norm(rb[i]["detail"]))]
    if len(ids) < 20:
        return False, "only %d comparable rows (sanity floor 20)" % len(ids)
    return not diff, "%d zero-tick rows compared, %d differ %s" % (len(ids), len(diff), diff[:6])


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="tier O only (default)")
    ap.add_argument("--live", action="store_true", help="run L/S/E against the bridge (python.exe)")
    ap.add_argument("--mock", action="store_true", help="run the live tier against the in-memory game")
    ap.add_argument("--fault", action="append", help="mock fault to inject (see MockBridge.FAULTS)")
    ap.add_argument("--fresh-map", action="store_true", help="start a new debug quicktest map first")
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
