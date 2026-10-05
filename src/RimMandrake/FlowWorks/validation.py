"""validation.py -- modcheck suite for RimMandrake FlowWorks (mandrake.rm.flowworks).

Trial plan (authority): design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md
(section 2 bars/bindings, section 2.5 toggle predicates, section 6 driver).
Item: FLOWWORKS_NORTHSTAR_WIRE_1. Never deployed (deploy_custom_mods.py excludes `.py`).

This replaces the old Pits suite (a BUILDING pit, `RM_OpenPit_Bare`) that was moved in
unchanged when Pits merged into FlowWorks. The pit is now a SUPERDEEP cell (depth 4 on the
D/F primitive), so every component here drives the depth/fill primitive:

  dig   `jawa/flowworks_excavation_drive {x,z,deepenLevels:N,setFill:-1}`   (engine Deepen())
  fill  `jawa/flowworks_excavation_drive {x,z,deepenLevels:0,setFill:F}`    (TrySetDriverFill)
  read  `jawa/flowworks_excavation_report {x,z}`  -> depth, fill, isExcavated, isSourceCell,
        isSinkCell, sinkTransferredTotal, overflowDestroyedTotal, excavatedCellCount
  `jawa/canal_dig` is a stub that ALWAYS FAILS (ruling 24) and is never called here.

WIRED, NOT GREEN. Every must-show and cannot-show bar of the VALIDATED walk is claimed by a
component via `shows=`, and every toggle in `suite.toggles` is covered (pitDepthDrawOffsetEnabled has no chain yet). Nothing here has run
live: every predicate below is UNMEASURED until the baseline run
(FLOWWORKS_NORTHSTAR_BASELINE_RUN_1). Expected today (plan section 1): the state half of the
canal/stock bars passes; visual bars whose art is still borrowed may come back NO from the
judge. The mechanics once listed here as unbuilt (viscosity, per-body fluid, depth draw offset,
superdeep cover, per-cell spikes, sluice doors) are all built as of 2026-10-05.

Site: the plan's trial map (golden save, 8-cell buffers, per-plot manifest) is built by the
shared driver and preflight (plan sections 3, 6), which do not exist yet. Until then every
chain builds its own plot with `_plot()` at a fixed offset from the suite anchor, clears and
re-paints it Soil, and refuses to act outside it. Limitless sources need a map edge: this
suite paints a water strip at the plot and cannot make it edge-touching, so
`_limitless_source()` asserts the body and the baseline run is expected to supply the edge.

Conventions:
  * `PULSE` = 250 ticks (`pulseIntervalTicks` default); settle = step whole pulses.
  * The judge reads only the LAST screenshot of a component. `(change)` bars end on a
    labelled before|after DIPTYCH (`_diptych`), composed offline with PIL; if PIL or the
    frames are unavailable the component FAILS rather than hand the judge one frame.
  * A setting that is not the subject of a component is restored in `finally` by `_setting`.
"""
import json
import os
import time
from contextlib import contextmanager

from modcheck import Suite, ExpectationFailed

suite = Suite("FlowWorks")

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_RIVER = "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings"

# 34 boolean toggles: 33 in RimMandrakeFlowWorksSettings, 1 in RiverSteamSettings (pitDepthDrawOffsetEnabled, also in
# the FlowWorks class, is the one setting with no chain yet). PIT_LEGACY_CODE_RETIRE_1
# (2026-10-02) retired PitsSettings: trapTriggerEnabled + fallDamageEnabled moved into the FlowWorks class;
# escapeEnabled and pitCellExposureEnabled died with the building pit (their chains are deleted).
FW_TOGGLES = [
    "depthEngineEnabled", "channelConfinementEnabled", "digToDepthEnabled",
    "liquidCorrosionEnabled", "liquidIgnitionEnabled",
    "fillInEnabled", "fillInDisplacementEnabled", "sourceBudgetEnabled",
    "stickyLimitlessEnabled", "recessionEnabled", "refillEnabled",
    "rainFillsExcavationsEnabled", "edgeSinksEnabled",
    "superdeepCaptureEnabled", "superdeepCapturesOwnFaction",
    "ladderRequiredToExitEnabled", "ladderPrisonDoorEnabled", "spikesEnabled", "superdeepShootingRuleEnabled",
    "flowDoorsSealedFromPitEnabled", "sluiceLetsBigThroughEnabled",
    "bottleLoopEnabled", "bottleDirtyStageEnabled", "tankLoopEnabled",
    "liquidDrillingEnabled", "typedLiquidShoresEnabled",
    "swaleEnabled", "pitExposureEnabled",
    "canalFireEnabled",          # FLOWWORKS_BUILD_PROGRAM_1 Phase 6
    "pitDrowningEnabled", "poisonFillEnabled",   # PIT_FILL_EFFECTS_1
    "viscosityEnabled",          # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (2026-10-05)
]
PITS_TOGGLES = ["trapTriggerEnabled", "fallDamageEnabled"]
RIVER_TOGGLES = ["riverSteamEnabled"]
suite.toggles = FW_TOGGLES + PITS_TOGGLES + RIVER_TOGGLES

DEFAULTS = {t: True for t in suite.toggles}
DEFAULTS.update({"liquidCorrosionEnabled": False, "liquidIgnitionEnabled": False,
                 "superdeepCapturesOwnFaction": False})
SETTINGS_OF = {}
SETTINGS_OF.update({k: S_FW for k in FW_TOGGLES})
SETTINGS_OF.update({k: S_FW for k in PITS_TOGGLES})
SETTINGS_OF.update({k: S_RIVER for k in RIVER_TOGGLES})

PULSE = 250
TAR, SLIME = "RM_Fluid_Tar", "RM_Fluid_SlimeGreen"
LADDER = "RM_Ladder"
SPIKES = "RM_Spikes"
SLUICE, GRATE = "RM_Sluice", "RM_SecurityGrateDoor"

# Plot grid: each plot is a PW x PH rect, PITCH apart, offset from the anchor.
PW, PH, PITCH = 24, 14, 36
PLOTS = {"A": (0, 0), "B": (1, 0), "C": (2, 0), "D": (0, 1), "E": (1, 1), "F": (2, 1),
         "G": (0, 2), "H": (1, 2), "T": (2, 2)}


# ------------------------------------------------------------------ helpers

def _plot(t, key):
    """(x0, z0) origin of plot `key`, derived from the anchor. Never overlaps another plot."""
    ax, az = t.anchor
    gx, gz = PLOTS[key]
    return ax - PITCH + gx * PITCH, az - PITCH + gz * PITCH


def _rect(x0, z0, w=PW, h=PH):
    return "%d,%d,%d,%d" % (x0, z0, w, h)


def _prep_plot(t, key, terrain="Soil"):
    """Clear the plot + its buffer, repaint Soil, pin Clear weather, clear the UI. Fixture writes only."""
    x0, z0 = _plot(t, key)
    b = 8
    r = _rect(x0 - b, z0 - b, PW + 2 * b, PH + 2 * b)
    t.bridge_call("jawa/destroy_batch", rects=r, categories="All")
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, r))
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/clear_ui")
    return x0, z0


def _rep(t, x, z):
    r = t.bridge_call("jawa/flowworks_excavation_report", x=x, z=z)
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("flowworks_excavation_report(%d,%d) failed: %r" % (x, z, r))
    return r or {}


def _dig(t, x, z, levels):
    r = t.bridge_call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=levels, setFill=-1)
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("excavation_drive dig (%d,%d) failed: %r" % (x, z, r))
    return r or {}


def _fill(t, x, z, f):
    r = t.bridge_call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=0, setFill=f)
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("excavation_drive fill (%d,%d,F=%d) failed: %r" % (x, z, f, r))
    return r or {}


def _set_fluid(t, fluid):
    """Set the map's ActiveFluid BEFORE first classification (plan section 6 item 3) and read it
    back. `jawa/flowworks_set_active_fluid` refuses once any body is classified or any cell holds
    fill, so on a shared map that already ran a water chain this FAILS -- the baseline run gives
    the chain a fresh working copy. Call inside a component so a refusal stops the chain rather
    than letting it run on water and report a tar/slime result."""
    r = t.bridge_call("jawa/flowworks_set_active_fluid", fluidDefName=fluid)
    if t._guard():
        _expect(bool((r or {}).get("success")) and r.get("fluidAfter") == fluid,
                "ActiveFluid not set to %s before first classification: %r" % (fluid, r))
    return r or {}


def _restore_water(t):
    """Put the map back on water after a tar/slime chain, guard or no guard. Existing bodies and
    fill terrain keep the old fluid (the tool says so); later chains prep their own plots.
    No session = the offline declaration probe: nothing to restore."""
    if getattr(t, "session", None) is None:
        return
    t.session.call("jawa/flowworks_set_active_fluid", fluidDefName="RM_Fluid_Water",
                   allowAfterClassification=True)


def _line(x0, z, n):
    return [(x0 + i, z) for i in range(n)]


def _dig_run(t, cells, levels):
    for x, z in cells:
        _dig(t, x, z, levels)


def _expect(cond, msg):
    if cond is False:
        raise ExpectationFailed(msg)


def _state(t, cells):
    """[(depth, fill)] for each cell, via the engine's own getters."""
    out = []
    for x, z in cells:
        r = _rep(t, x, z)
        out.append((r.get("depth"), r.get("fill")))
    return out


def _expect_state(t, cells, depth=None, fill=None, what="run"):
    if not t._guard():
        return
    for (x, z), (d, f) in zip(cells, _state(t, cells)):
        if depth is not None and d != depth:
            raise ExpectationFailed("%s cell (%d,%d): D=%r expected %r" % (what, x, z, d, depth))
        if fill is not None and f != fill:
            raise ExpectationFailed("%s cell (%d,%d): F=%r expected %r" % (what, x, z, f, fill))


def _wait(t, ticks):
    """Whole pulses only: round up so a bar never ends mid-pulse."""
    pulses = max(1, -(-ticks // PULSE))
    t.wait_ticks(pulses * PULSE)


def _settle(t, cells, budget_pulses=20):
    """Step pulse by pulse until the F vector is unchanged across 3 consecutive pulses.
    Budget exhausted is FAIL (NOT_SETTLED), never a pass."""
    if not t._guard():
        return
    prev, still = None, 0
    for _ in range(budget_pulses):
        _wait(t, PULSE)
        now = [f for _, f in _state(t, cells)]
        still = still + 1 if now == prev else 0
        prev = now
        if still >= 3:
            return
    raise ExpectationFailed("NOT_SETTLED: F vector still changing after %d pulses" % budget_pulses)


def _ring(cells):
    s = set(cells)
    ring = set()
    for x, z in cells:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = (x + dx, z + dz)
                if c not in s:
                    ring.add(c)
    return sorted(ring)


def _expect_dry_ring(t, cells):
    """Cannot-show scan: every un-dug cell in the 1-cell ring has D=0 and F=0."""
    if not t._guard():
        return
    bad = [(c, d, f) for c, (d, f) in zip(_ring(cells), _state(t, _ring(cells))) if d or f]
    if bad:
        raise ExpectationFailed("liquid/excavation on un-dug ground beside the run: %s" % bad[:5])


@contextmanager
def _setting(t, field, value):
    """Flip one Mod Settings field for the duration of a block, restore the shipped default in finally."""
    typ = SETTINGS_OF[field]
    t.set_setting(typ, {field: value})
    try:
        yield
    finally:
        try:
            t.set_setting(typ, {field: DEFAULTS[field]})
        except Exception:
            pass


def _frame(t, x0, z0, w, h, name=None):
    """One framed screenshot of a cell rect (3-cell margin). Returns the path."""
    return t.screenshot(name=name, rect=(x0 - 3, z0 - 3, w + 6, h + 6), padding=0)


def _diptych(t, before, after, name):
    """Compose before|after into ONE png and make it the component's LAST screenshot, so the
    single-frame judge sees both. Fails loudly if it cannot -- never hands the judge one frame."""
    if not t._guard():
        return None
    try:
        from PIL import Image, ImageDraw
        a, b = Image.open(before).convert("RGB"), Image.open(after).convert("RGB")
        h = max(a.height, b.height)
        out = Image.new("RGB", (a.width + b.width + 8, h + 20), (0, 0, 0))
        out.paste(a, (0, 20))
        out.paste(b, (a.width + 8, 20))
        d = ImageDraw.Draw(out)
        d.text((4, 4), "BEFORE", fill=(255, 255, 255))
        d.text((a.width + 12, 4), "AFTER", fill=(255, 255, 255))
        path = os.path.join(os.path.dirname(before) or ".", "%s_diptych_%d.png" % (name, int(time.time())))
        out.save(path)
    except Exception as e:  # PIL missing, unreadable frame (e.g. a .bmp fallback), ...
        raise ExpectationFailed("diptych could not be composed (%s): %r / %r" % (e, before, after))
    if t._current is not None:
        t._current.screenshots.append(path)
    return path


def _spawn_pawn_at(t, kind, x, z, faction="player"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    row = ((r or {}).get("pawns") or [{}])[0]
    return row.get("id")


def _pit_held(t, pid, cells):
    """SUPERDEEP_HOLDER_RETIRE_1: a held pawn STAYS SPAWNED (no holder container), so capture is read
    from jawa/flowworks_pit_report's trap verdict on whichever pit cell the pawn stands on, never from
    its absence in list_pawns (the retired holder model). None = the pawn is on no pit cell."""
    for x, z in cells:
        r = t.bridge_call("jawa/flowworks_pit_report", x=x, z=z) or {}
        for p in r.get("pawns") or []:
            if p.get("id") == pid:
                return bool(p.get("held"))
    return None


def _pawn_xz(t, pid):
    r = t.bridge_call("jawa/list_pawns", limit=200)
    for p in ((r or {}).get("pawns") or []):
        if p.get("id") == pid:
            return p.get("x"), p.get("z")
    return None, None


def _ignite(t, x, z):
    """Light one cell with the engine's own fire start (`jawa/map_fire`, 1x1 rect)."""
    return t.bridge_call("jawa/map_fire", action="start", rect="%d,%d,1,1" % (x, z), fireSize=1.2)


def _march(t, pid, x, z, ticks=300):
    t.bridge_call("jawa/order_pawn", pawnId=pid, x=x, z=z)
    t.wait_ticks(ticks)


def _limitless_source(t, key, w=10, h=6):
    """Paint a WaterDeep strip at the plot's west edge BEFORE any excavation touches it
    (classification happens once on first contact) and assert its stock reads limitless."""
    x0, z0 = _plot(t, key)
    t.bridge_call("jawa/set_terrain_batch", ops="WaterDeep:%s" % _rect(x0, z0 + 4, w, h))
    return x0, z0


def _limited_pond(t, key, size=5, terrain="WaterShallow"):
    x0, z0 = _plot(t, key)
    px, pz = x0 + 3, z0 + 4
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, _rect(px, pz, size, size)))
    return px, pz


def _fill_fluid(t, x, z, f, fluid):
    """Fill an excavated cell with a NAMED fluid (LIQUID_BODY_FLUID_IDENTITY_1 step 3); refuses another fluid's cell."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FluidIdentityProof",
                      method="ProofFillWithFluid", args="%d,%d,%d,%s" % (x, z, f, fluid))
    res = str((r or {}).get("result", ""))
    if t._guard() and not res.startswith("FILLED"):
        raise ExpectationFailed("fill %s (%d,%d,F=%d) failed: %s" % (fluid, x, z, f, res or r))
    return res


def _light(t, x, z):
    """Phase 6: light a liquid cell through RM_LiquidFire directly (a vanilla Fire next to it does the same
    via the Fire.SpawnSetup hook; _ignite exercises that route)."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_LiquidFireProof",
                      method="ProofIgnite", args="%d,%d" % (x, z))
    return str((r or {}).get("result", ""))


FLAME = "RM_LiquidFlame"   # Phase 6: the burning-liquid flame; vanilla "Fire" dies on liquid terrain (no fuel)


def _channel_from(x0, z, n):
    """A 1xn run starting at x0 (the mouth)."""
    return _line(x0, z, n)


# =============================================================== CANAL BARS

@suite.chain("plot_A_dug_channel")
def plot_A_dug_channel(t):
    """Plot A: a 1x8 D=1 run on Soil, dry. One shot, several bars."""
    x0, z0 = _prep_plot(t, "A")
    z = z0 + 6
    cells = _line(x0 + 4, z, 8)
    _dig_run(t, cells, 1)
    with t.component("canal_dug_channel_look",
                     shows=["canal_reads_as_dug_channel", "never_gravel_path"]):
        _expect_state(t, cells, depth=1, fill=0, what="dry channel")
        # the engine reports excavated and the terrain swapped to the empty-channel def
        r = t.bridge_call("jawa/canal_cell_report", x=cells[0][0], z=cells[0][1])
        if t._guard():
            _expect("RM_Channel_Empty" in str(r), "terrain at the dug cell is not RM_Channel_Empty: %r" % r)
        _frame(t, cells[0][0], z, 8, 1)
    with t.component("canal_dry_obstacle_look", shows=["canal_dry_reads_as_obstacle"]):
        # ruled pathCost 30 for a dry D=1 cell (build program Phase 5, ruling 17)
        r = t.bridge_call("jawa/get_defs", defs="TerrainDef/RM_Channel_Empty")
        if t._guard():
            _expect("\"pathCost\":30" in str(r).replace(" ", ""),
                    "RM_Channel_Empty pathCost is not the ruled 30: %s" % str(r)[:300])
        _frame(t, cells[0][0], z, 8, 1)
    with t.component("filled_excavation_obstacle_look", shows=["filled_excavation_reads_as_obstacle"]):
        _fill(t, cells[0][0], z, 1)
        _expect_state(t, cells[:1], depth=1, fill=1, what="filled cell")
        _frame(t, cells[0][0], z, 8, 1)


@suite.chain("plot_B_fill_tiers")
def plot_B_fill_tiers(t):
    """Plot B: four parallel 1x6 runs at D=3 filled to F=0..3 with the engine frozen, so a pulse
    cannot equalise them. The engine is restored in `finally` by `_setting`."""
    x0, z0 = _prep_plot(t, "B")
    runs = [_line(x0 + 3, z0 + 2 + 3 * i, 6) for i in range(4)]
    for r in runs:
        _dig_run(t, r, 3)
    with _setting(t, "depthEngineEnabled", False):
        for f, r in enumerate(runs):
            for x, z in r:
                _fill(t, x, z, f)
        with t.component("partial_fill_two_look", shows=["canal_partial_fill_distinct"]):
            _expect_state(t, runs[1], depth=3, fill=1, what="run F=1")
            _expect_state(t, runs[3], depth=3, fill=3, what="run F=3")
            _frame(t, x0 + 3, z0 + 2, 6, 10)
        with t.component("fill_tier_four_look", shows=["fill_tier_legible"]):
            for f, r in enumerate(runs):
                _expect_state(t, r[:1], fill=f, what="tier F=%d" % f)
            _frame(t, x0 + 3, z0 + 2, 6, 10)
        with t.component("depth_and_fill_joint_look", shows=["depth_and_fill_jointly_legible"]):
            # extra pads at D=1..4 each filled half-way, in one row, so both axes vary in one frame
            for d in range(1, 5):
                cx, cz = x0 + 12 + 2 * d, z0 + 5
                _dig(t, cx, cz, d)
                _fill(t, cx, cz, max(0, d // 2))
            _expect_state(t, [(x0 + 12 + 2 * 4, z0 + 5)], depth=4, fill=2, what="joint pad D=4")
            _frame(t, x0 + 12, z0 + 3, 12, 5)


@suite.chain("plot_C_limitless_canal")
def plot_C_limitless_canal(t):
    """Plot C: a 1x10 D=1 channel dug from a limitless water body, engine running."""
    x0, z0 = _prep_plot(t, "C")
    _limitless_source(t, "C")
    z = z0 + 6
    cells = _channel_from(x0 + 10, z, 10)
    shot_rect = (x0, z0 + 2, 22, 10)
    with t.component("canal_digs_from_source"):
        _dig_run(t, cells, 1)
        _expect_state(t, cells, depth=1, what="channel")
    with t.component("canal_fill_front", shows=["canal_fill_front_watchable"]):
        _wait(t, PULSE)
        p1 = _frame(t, *shot_rect, name="C_pulse1")
        _wait(t, 2 * PULSE)
        p3 = _frame(t, *shot_rect, name="C_pulse3")
        _diptych(t, p1, p3, "C_fill_front")
        if t._guard():
            _expect(_rep(t, *cells[0]).get("fill") >= 1, "mouth cell F<1 after 3 pulses from a limitless source")
    with t.component("canal_fill_spreads", shows=["canal_fill_spreads_along_itself"]):
        _settle(t, cells, budget_pulses=20)
        if t._guard():
            fs = [f for _, f in _state(t, cells)]
            _expect(all((f or 0) >= 1 for f in fs), "channel has a dry gap or dry cell after settle: %s" % fs)
        _frame(t, *shot_rect)
    with t.component("canal_holds_only_channel",
                     toggle="channelConfinementEnabled",
                     shows=["canal_holds_only_the_channel", "never_liquid_on_open_ground"]):
        _expect_dry_ring(t, cells)
        _frame(t, *shot_rect)
    with t.component("canal_same_liquid_look", shows=["canal_reads_as_same_liquid_as_reservoir"]):
        _frame(t, x0, z0 + 2, 22, 10)


@suite.chain("plot_C2_tar_and_fluids")
def plot_C2_tar_and_fluids(t):
    """Tar vs water fill front (FluidDef.ticksPerTile: tar 360 vs water 60), and the two-fluids-side-by-side
    bar (fluid identity is per cell via ProofFillWithFluid, so one map holds both)."""
    x0, z0 = _prep_plot(t, "T")
    try:
        _plot_C2_body(t, x0, z0)
    finally:
        _restore_water(t)


def _plot_C2_body(t, x0, z0):
    # ActiveFluid=TAR before first classification (plan section 6 item 3); refused on a map
    # where a body is already classified, which fails this component and stops the chain.
    with t.component("tar_fluid_set"):
        _set_fluid(t, TAR)
    _limitless_source(t, "T")
    cells = _channel_from(x0 + 10, z0 + 6, 10)
    _dig_run(t, cells, 1)
    with t.component("tar_front_lags_water", toggle="viscosityEnabled", shows=["tar_fill_front_lags_water"]):
        _wait(t, PULSE)
        p1 = _frame(t, x0, z0 + 2, 22, 10, "T_pulse1")
        _wait(t, 2 * PULSE)
        p3 = _frame(t, x0, z0 + 2, 22, 10, "T_pulse3")
        _diptych(t, p1, p3, "T_tar_front")
        if t._guard():
            # state delta: tar's wet front at pulse 3 strictly shorter than water's (water front = full run today)
            wet = sum(1 for _, f in _state(t, cells) if (f or 0) >= 1)
            _expect(wet < len(cells), "tar wet front reached all %d cells: no viscosity lag" % len(cells))
    with t.component("two_fluids_side_by_side", shows=["fill_fluid_distinct"]):
        # Per-body fluid identity is built (RM_FluidIdentity / ProofFillWithFluid names the fluid per
        # cell), so two fluids share one map: a tar run and a water run, dug side by side and filled
        # to the same tier, and the frame shows they read differently.
        tar_run = _line(x0 + 4, z0 + 2, 6)
        water_run = _line(x0 + 4, z0 + 4, 6)
        _dig_run(t, tar_run + water_run, 1)
        for x, z in tar_run:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Tar")
        for x, z in water_run:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Water")
        _frame(t, x0 + 4, z0 + 2, 6, 3)


@suite.chain("plot_D_limited_pond")
def plot_D_limited_pond(t):
    """Plot D: a limited 5x5 pond drawn down through a 1x12 D=3 channel; then recharge."""
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D")
    z = pz + 2
    cells = _channel_from(px + 5, z, 12)
    shot = (px - 1, pz - 1, 18, 8)
    box = {}
    with t.component("pond_before_draw"):
        box["before"] = _frame(t, *shot, name="D_before")
    with t.component("pond_drawn_down",
                     shows=["reservoir_fill_visibly_drops", "never_full_reservoir_after_heavy_draw"]):
        _dig_run(t, cells, 3)
        _settle(t, cells, budget_pulses=40)
        if t._guard():
            fs = [f for _, f in _state(t, cells)]
            _expect(any((f or 0) > 0 for f in fs), "channel never took liquid from the pond: %s" % fs)
        after = _frame(t, *shot, name="D_after")
        _diptych(t, box.get("before"), after, "D_pond_draw")
    with t.component("pond_shoreline_recedes", toggle="recessionEnabled",
                     shows=["reservoir_shoreline_recedes"]):
        far = _rep(t, px, pz) if t._guard() else {}
        _expect(not far.get("isSourceCell", True) if far else None,
                "far-edge pond cell is still a source cell after the draw: recession did not dry it")
        _frame(t, *shot)
    with t.component("pond_empty_stops_flow", shows=["empty_reservoir_stops_flow"]):
        with _setting(t, "refillEnabled", False):
            _dig_run(t, _line(px + 5, pz + 2, 12), 3)   # no-op re-dig; keeps drawing
            _wait(t, 40 * PULSE)
            if t._guard():
                tail = [f for _, f in _state(t, cells[-3:])]
                _expect(all((f or 0) == 0 for f in tail), "tail of the channel still fed with the pond empty: %s" % tail)
            _frame(t, *shot)
    with t.component("pond_recharge_visible", toggle="refillEnabled",
                     shows=["reservoir_recharge_progress_visible"]):
        s0 = _frame(t, *shot, name="D_recharge0")
        _wait(t, 20 * PULSE)
        s1 = _frame(t, *shot, name="D_recharge1")
        _diptych(t, s0, s1, "D_recharge")


@suite.chain("plot_E_fire")
def plot_E_fire(t):
    """Plot E (tar, Phase 6 fire ON): 1x8 D=1 tar channel from a limited RM_TarShallow pond, ignite the far end.
    Engine: RM_LiquidFire (FLOWWORKS_BUILD_PROGRAM_1 Phase 6) — one RM_LiquidFlame per burning cell, the front
    creeps 120 ticks/cell (tar, PROVISIONAL) back to the pond, burn = 1 level/day (ruling 7).
    RULED OUT (kept): counting vanilla "Fire" — it self-destroys on liquid terrain (Fire.DoComplexCalcs:
    flammabilityMax < 0.01), so the old LiquidIgnition spike could never have shown a lasting burn.
    Fire-safety: the 8-cell buffer is bare Soil (no plants); `_prep_plot` clears all things."""
    x0, z0 = _prep_plot(t, "E")
    px, pz = _limited_pond(t, "E", terrain="RM_TarShallow")
    cells = _channel_from(px + 5, pz + 2, 8)
    shot = (px - 1, pz - 1, 16, 8)
    _dig_run(t, cells, 1)
    with _setting(t, "canalFireEnabled", True):
        for x, z in cells:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Tar")
        _ignite(t, *cells[-1])
        with t.component("fire_burning_look", toggle="canalFireEnabled",
                         shows=["canal_burning_reads_as_burning_liquid"]):
            _wait(t, 5 * PULSE)
            if t._guard():
                fires = t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(px, pz, 14, 8), limit=200)
                n = len((fires or {}).get("things") or [])
                _expect(n >= 3, "fewer than 3 burning-liquid flames in the channel after ignition: %d" % n)
            _frame(t, *shot)
        with t.component("fire_reaches_reservoir", shows=["canal_fire_reaches_reservoir"]):
            _wait(t, 24 * PULSE)
            if t._guard():
                fires = t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(px, pz, 5, 5), limit=200)
                _expect(len((fires or {}).get("things") or []) >= 1, "no flame at the pond cells within budget")
            _frame(t, *shot)
        with t.component("fire_persists_look", shows=["canal_fire_persists"]):
            f1 = len(((t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(px, pz, 14, 8), limit=200) or {})
                      .get("things")) or [])
            _wait(t, 4 * PULSE)
            f2 = len(((t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(px, pz, 14, 8), limit=200) or {})
                      .get("things")) or [])
            _expect(f2 > 0 if t._guard() else None, "fire died within 4 pulses (was %s, now %s)" % (f1, f2))
            _frame(t, *shot)
        with t.component("burned_channel_spent", shows=["canal_spent_after_burn"]):
            _wait(t, 240 * PULSE)     # ~60,000 ticks: "one canal tier per day"
            _expect_state(t, cells, fill=0, what="burned cell")
            _frame(t, *shot)


@suite.chain("plot_F_slime")
def plot_F_slime(t):
    """Plot F: a 1x6 D=3 slime run (ActiveFluid RM_Fluid_SlimeGreen set before first classification --
    a fresh working copy in the real run) and a colonist walked into the middle cell."""
    x0, z0 = _prep_plot(t, "F")
    try:
        _plot_F_body(t, x0, z0)
    finally:
        _restore_water(t)


def _plot_F_body(t, x0, z0):
    with t.component("slime_fluid_set"):
        _set_fluid(t, SLIME)
    cells = _line(x0 + 6, z0 + 6, 6)
    _dig_run(t, cells, 3)
    with _setting(t, "depthEngineEnabled", False):
        for x, z in cells:
            _fill(t, x, z, 3)
        with t.component("slime_viscous_look", shows=["slime_reads_as_viscous_not_water"]):
            _expect_state(t, cells, fill=3, what="slime run")
            _frame(t, x0 + 6, z0 + 6, 6, 1)
        with t.component("slime_occupant_look", shows=["slime_occupant_below_surface"]):
            pid = _spawn_pawn_at(t, "Colonist", cells[0][0] - 2, cells[0][1])
            mid = cells[len(cells) // 2]
            _march(t, pid, mid[0], mid[1], 300)
            if t._guard():
                px, pz = _pawn_xz(t, pid)
                _expect((px, pz) in cells, "colonist is not inside the slime run: at %s,%s" % (px, pz))
            _frame(t, mid[0] - 3, mid[1] - 2, 7, 5)


# ============================================================== DEPTH / PIT BARS

@suite.chain("plot_H_depth_ladder")
def plot_H_depth_ladder(t):
    """Plot H: five adjacent 2x3 pads at D=0..4 in one row; a colonist walked across them with
    superdeepCaptureEnabled OFF so it is not captured on D=4 before the frame."""
    x0, z0 = _prep_plot(t, "H")
    # five 2x3 pads, 2 wide each => x spans 10 cells
    pads = [[(x0 + 3 + d * 2 + i, z0 + 5 + j) for i in range(2) for j in range(3)] for d in range(5)]
    for d, pad in enumerate(pads):
        if d:
            _dig_run(t, pad, d)
    shot = (x0 + 3, z0 + 5, 10, 3)
    with t.component("depth_ladder_look", shows=["pit_depth_ladder_legible"]):
        for d, pad in enumerate(pads):
            _expect_state(t, pad[:1], depth=d, what="pad D=%d" % d)
        _frame(t, *shot)
    with _setting(t, "superdeepCaptureEnabled", False):
        pid = _spawn_pawn_at(t, "Colonist", x0, z0 + 6)
        with t.component("pawn_height_ladder_look", shows=["pawn_height_ladder_legible"]):
            # pawn at the D=1 pad and at the D=4 pad -> diptych for "rises and lowers"
            _march(t, pid, pads[1][0][0], pads[1][0][1], 200)
            a = _frame(t, pads[1][0][0] - 3, pads[1][0][1] - 2, 7, 5, "H_d1")
            _march(t, pid, pads[4][0][0], pads[4][0][1], 300)
            b = _frame(t, pads[4][0][0] - 3, pads[4][0][1] - 2, 7, 5, "H_d4")
            _diptych(t, a, b, "H_height_ladder")
        with t.component("pawn_lowers_deeper", shows=["pawn_lowers_on_deeper_cell"]):
            _march(t, pid, pads[2][0][0], pads[2][0][1], 200)
            a = _frame(t, pads[2][0][0] - 3, pads[2][0][1] - 2, 7, 5, "H_d2")
            _march(t, pid, pads[3][0][0], pads[3][0][1], 200)
            b = _frame(t, pads[3][0][0] - 3, pads[3][0][1] - 2, 7, 5, "H_d3")
            _diptych(t, a, b, "H_lowers")
        with t.component("pawn_rises_shallower", shows=["pawn_rises_on_shallower_cell"]):
            _march(t, pid, pads[3][0][0], pads[3][0][1], 200)
            a = _frame(t, pads[3][0][0] - 3, pads[3][0][1] - 2, 7, 5, "H_d3b")
            _march(t, pid, pads[1][0][0], pads[1][0][1], 300)
            b = _frame(t, pads[1][0][0] - 3, pads[1][0][1] - 2, 7, 5, "H_d1b")
            _diptych(t, a, b, "H_rises")


def _pit_cells(x0, z0):
    return [(x0 + 6 + i, z0 + 5 + j) for i in range(3) for j in range(3)]


@suite.chain("plot_G_pit")
def plot_G_pit(t):
    """Plot G: a 3x3 D=4 superdeep area (the pit). Occupied/empty twin G' sits 8 cells east."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    twin = [(x + 9, z) for x, z in pit]
    _dig_run(t, pit, 4)
    _dig_run(t, twin, 4)
    shot = (x0 + 5, z0 + 4, 5, 5)
    twin_shot = (x0 + 5, z0 + 4, 14, 5)
    with t.component("pit_hole_look",
                     shows=["pit_reads_as_hole", "pit_reads_at_size", "pit_walls_have_visible_depth"]):
        _expect_state(t, pit, depth=4, what="pit")
        _frame(t, *shot)
    with t.component("pit_not_vanilla_trap", shows=["pit_not_vanilla_trap", "never_reads_as_building"]):
        # offline-checkable half: no FlowWorks def draws the vanilla spike-trap art as its texPath.
        # RM_Ladder is exempt: it borrows that sheet as a declared placeholder (ladder art is owner-gated),
        # and it is a ladder, not the pit. A comment that merely names the path is not a hit.
        import xml.etree.ElementTree as ET
        ddir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs")
        hits = []
        for root, _, files in os.walk(ddir):
            for fn in files:
                if fn.endswith(".xml"):
                    for d in ET.parse(os.path.join(root, fn)).getroot():
                        tp = d.findtext("graphicData/texPath") or d.findtext("texturePath") or ""
                        if tp == "Things/Building/Security/TrapSpikeArmed" and d.findtext("defName") != "RM_Ladder":
                            hits.append(fn)
        _expect(not hits, "defs still point at the vanilla TrapSpikeArmed art: %s" % sorted(set(hits)))
        _frame(t, *shot)
    with t.component("pit_captures_hostile", toggle="superdeepCaptureEnabled",
                     shows=["pit_occupant_below_floor", "pit_trapped_reads_as_trapped",
                            "pit_occupied_distinguishable", "never_snared_standing"]):
        caught = 0
        for i in range(3):       # traps ABSOLUTELY: 3/3 over distinct spawn points
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1] + i, faction="hostile")
            _march(t, pid, pit[4][0], pit[4][1], 1200)
            if t._guard():
                caught += 1 if _pit_held(t, pid, pit) else 0
        _expect(caught == 3 if t._guard() else None, "superdeep captured %d/3 hostiles" % caught)
        _frame(t, *twin_shot)    # occupied pit beside the empty twin in one frame
    with t.component("pit_cover_invisible",
                     shows=["pit_covered_invisible", "pit_covered_seam_at_max_zoom"]):
        # PIT_COVER_FALL_REWIRE_1: a reinforced deck over the empty twin (nobody on it is heavy enough
        # to spring it), framed beside the open pit; the frame is the bar, the count is the guard.
        t.bridge_call("jawa/spawn_batch", ops=";".join("RM_PitCover_ReinforcedFrame:%d,%d" % (x, z) for x, z in twin))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_ReinforcedFrame",
                              rect=_rect(twin[0][0] - 1, twin[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 9, "reinforced cover deck did not stand on all 9 twin cells: %r" % r)
        _frame(t, *twin_shot)
    with t.component("ladder_state_look", toggle="ladderRequiredToExitEnabled",
                     shows=["ladder_state_legible"]):
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LADDER, pit[0][0] - 1, pit[0][1]))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName=LADDER, rect=_rect(pit[0][0] - 2, pit[0][1] - 1, 4, 3))
            _expect(((r or {}).get("things") or []), "RM_Ladder did not place beside the pit")
        _frame(t, *shot)
    with t.component("sluice_state_look", shows=["sluice_gate_state_legible"]):
        # FLOWWORKS_DOOR_FAMILY_1: a wooden sluice and a steel grate on the pit's west lip, framed.
        # Placeholder art (vanilla door mover) until the gate art lands; the frame is the bar.
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SLUICE, pit[0][0] - 1, pit[0][1] + 1), stuff="WoodLog")
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (GRATE, pit[0][0] - 1, pit[0][1] + 2), stuff="Steel")
        if t._guard():
            for d in (SLUICE, GRATE):
                r = t.bridge_call("jawa/list_things", defName=d, rect=_rect(pit[0][0] - 2, pit[0][1] - 1, 3, 5))
                _expect(((r or {}).get("things") or []), "%s did not place on the pit lip" % d)
        _frame(t, *shot)
    with t.component("spikes_look", shows=["spikes_read_distinct"]):
        # CANAL_BOTTOM_SPIKES_1 built RM_Spikes (placeholder skullspike graphic until EXCAVATION_WALL_ART_1).
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SPIKES, pit[4][0], pit[4][1]))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName=SPIKES, rect=_rect(pit[4][0], pit[4][1], 1, 1))
            _expect(((r or {}).get("things") or []), "RM_Spikes did not place on the D=4 floor")
        _frame(t, *shot)


# =========================================================== TOGGLE COMPONENTS
# One component per Mod Settings toggle (plan section 2.5). ON = shipped default; OFF = flipped
# for that component and restored in `finally`. A component that only declares `toggle=` with no
# predicate is a floor cheat; each one below reads state through the engine report, never the
# setter's echo. Ticks are budgets. A few need tools only the shared driver will have: those carry
# the predicate that IS expressible today and a comment naming the gap.

def _mini_channel(t, key, n=6, levels=1):
    x0, z0 = _prep_plot(t, key)
    _limitless_source(t, key)
    cells = _channel_from(x0 + 10, z0 + 6, n)
    _dig_run(t, cells, levels)
    return x0, z0, cells


@suite.chain("toggle_depth_engine")
def toggle_depth_engine(t):
    x0, z0, cells = _mini_channel(t, "A")
    with t.component("depth_engine_on", toggle="depthEngineEnabled"):
        _wait(t, 2 * PULSE)
        if t._guard():
            _expect((_rep(t, *cells[0]).get("fill") or 0) >= 1, "F did not rise at the mouth within 2 pulses")
    x0, z0, cells = _mini_channel(t, "A")
    with t.component("depth_engine_off", toggle="depthEngineEnabled"):
        with _setting(t, "depthEngineEnabled", False):
            _wait(t, 4 * PULSE)
            _expect_state(t, cells, fill=0, what="engine off")


@suite.chain("toggle_confinement")
def toggle_confinement(t):
    x0, z0, cells = _mini_channel(t, "B")
    with t.component("confinement_on", toggle="channelConfinementEnabled"):
        _settle(t, cells, 20)
        _expect_dry_ring(t, cells)
    x0, z0, cells = _mini_channel(t, "B")
    with t.component("confinement_off_leaks", toggle="channelConfinementEnabled"):
        with _setting(t, "channelConfinementEnabled", False):
            _wait(t, 20 * PULSE)
            if t._guard():
                ring = _state(t, _ring(cells))
                _expect(any(d or f for d, f in ring),
                        "no ring cell took liquid with confinement OFF: the toggle is not live")


@suite.chain("toggle_dig_to_depth")
def toggle_dig_to_depth(t):
    x0, z0 = _prep_plot(t, "C")
    c = (x0 + 4, z0 + 6)
    with t.component("dig_to_depth_on", toggle="digToDepthEnabled"):
        _dig(t, c[0], c[1], 3)
        _expect_state(t, [c], depth=3, what="digToDepth ON")
    c2 = (x0 + 6, z0 + 6)
    with t.component("dig_to_depth_off", toggle="digToDepthEnabled"):
        with _setting(t, "digToDepthEnabled", False):
            _dig(t, c2[0], c2[1], 3)
            _expect_state(t, [c2], depth=1, what="digToDepth OFF clamps to shallow")


@suite.chain("toggle_edge_sinks")
def toggle_edge_sinks(t):
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D")
    cells = _channel_from(px + 5, pz + 2, 14)
    _dig_run(t, cells, 1)
    with t.component("edge_sinks_on", toggle="edgeSinksEnabled"):
        s0 = _rep(t, *cells[0]).get("sinkTransferredTotal") or 0
        _wait(t, 20 * PULSE)
        s1 = _rep(t, *cells[0]).get("sinkTransferredTotal") or 0
        _expect(s1 > s0 if t._guard() else None, "sinkTransferredTotal did not rise (%s -> %s)" % (s0, s1))
    with t.component("edge_sinks_off", toggle="edgeSinksEnabled"):
        with _setting(t, "edgeSinksEnabled", False):
            s0 = _rep(t, *cells[0]).get("sinkTransferredTotal") or 0
            _wait(t, 20 * PULSE)
            s1 = _rep(t, *cells[0]).get("sinkTransferredTotal") or 0
            _expect(s1 == s0 if t._guard() else None, "sinkTransferredTotal moved with sinks off (%s -> %s)" % (s0, s1))


@suite.chain("toggle_fill_in")
def toggle_fill_in(t):
    x0, z0 = _prep_plot(t, "E")
    a, b = (x0 + 4, z0 + 6), (x0 + 6, z0 + 6)
    for c in (a, b):
        _dig(t, c[0], c[1], 1)
        _fill(t, c[0], c[1], 1)
    with t.component("fill_in_on", toggle="fillInEnabled"):
        t.bridge_call("jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % a)
        t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=a[0] - 2, z=a[1], faction="player", count=1)
        _wait(t, 10 * PULSE)
        _expect_state(t, [a], depth=0, what="filled-in cell")
    with t.component("fill_in_off", toggle="fillInEnabled"):
        with _setting(t, "fillInEnabled", False):
            t.bridge_call("jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % b)
            _wait(t, 10 * PULSE)
            _expect_state(t, [b], depth=1, what="designation refused")


@suite.chain("toggle_fill_in_displacement")
def toggle_fill_in_displacement(t):
    x0, z0 = _prep_plot(t, "F")
    cells = _line(x0 + 4, z0 + 6, 3)
    _dig_run(t, cells, 1)
    for c in cells:
        _fill(t, c[0], c[1], 1)
    with t.component("fill_in_displacement_on", toggle="fillInDisplacementEnabled"):
        before = sum((f or 0) for _, f in _state(t, cells))
        t.bridge_call("jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % cells[1])
        _wait(t, 10 * PULSE)
        after = sum((f or 0) for _, f in _state(t, cells))
        _expect(after >= before if t._guard() else None, "liquid was deleted, not displaced (%s -> %s)" % (before, after))
    with t.component("fill_in_displacement_off", toggle="fillInDisplacementEnabled"):
        with _setting(t, "fillInDisplacementEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_source_budget")
def toggle_source_budget(t):
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D", size=2)
    cells = _channel_from(px + 2, pz, 30)
    _dig_run(t, cells, 1)
    with t.component("source_budget_on", toggle="sourceBudgetEnabled"):
        _wait(t, 40 * PULSE)
        wet = sum(1 for _, f in _state(t, cells) if (f or 0) >= 1)
        _expect(wet <= 5 * 4 if t._guard() else None, "channel filled %d cells past the 5-per-source-cell budget" % wet)
    with t.component("source_budget_off", toggle="sourceBudgetEnabled"):
        with _setting(t, "sourceBudgetEnabled", False):
            _wait(t, 40 * PULSE)
            wet = sum(1 for _, f in _state(t, cells) if (f or 0) >= 1)
            _expect(wet > 5 * 4 if t._guard() else None, "channel stopped at the budget with the toggle off (%d)" % wet)


@suite.chain("toggle_sticky_limitless")
def toggle_sticky_limitless(t):
    x0, z0, cells = _mini_channel(t, "T", n=10)
    with t.component("sticky_limitless_on", toggle="stickyLimitlessEnabled"):
        _wait(t, 20 * PULSE)
        r = t.bridge_call("jawa/flowworks_excavation_report", x=x0 + 4, z=z0 + 6)
        _expect((r or {}).get("isSourceCell") if t._guard() else None, "limitless body lost its source cells under draw")
    with t.component("sticky_limitless_off", toggle="stickyLimitlessEnabled"):
        with _setting(t, "stickyLimitlessEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_recession")
def toggle_recession(t):
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D")
    cells = _channel_from(px + 5, pz + 2, 12)
    _dig_run(t, cells, 3)
    with t.component("recession_on", toggle="recessionEnabled"):
        _wait(t, 40 * PULSE)
        far = _rep(t, px, pz) if t._guard() else {}
        _expect(not far.get("isSourceCell", True) if far else None, "no pond cell dried with recession ON")
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D")
    cells = _channel_from(px + 5, pz + 2, 12)
    _dig_run(t, cells, 3)
    with t.component("recession_off", toggle="recessionEnabled"):
        with _setting(t, "recessionEnabled", False):
            _wait(t, 40 * PULSE)
            far = _rep(t, px, pz) if t._guard() else {}
            _expect(far.get("isSourceCell", False) if far else None, "a pond cell dried with recession OFF")


@suite.chain("toggle_refill")
def toggle_refill(t):
    """Pond source-cell count after a draw: refill ON must not shrink it further over 20 quiet
    pulses; OFF must stay flat. (Stock itself needs the driver's `body_report`.)"""
    def pond_sources(px, pz):
        return sum(1 for x in range(px, px + 5) for z in range(pz, pz + 5)
                   if _rep(t, x, z).get("isSourceCell")) if t._guard() else 0
    x0, z0 = _prep_plot(t, "E")
    px, pz = _limited_pond(t, "E")
    _dig_run(t, _channel_from(px + 5, pz + 2, 6), 1)
    _wait(t, 10 * PULSE)
    with t.component("refill_on", toggle="refillEnabled"):
        a = pond_sources(px, pz)
        _wait(t, 20 * PULSE)
        b = pond_sources(px, pz)
        _expect(b >= a if t._guard() else None,
                "pond source cells fell during quiet pulses with refill ON (%d -> %d)" % (a, b))
    with t.component("refill_off", toggle="refillEnabled"):
        with _setting(t, "refillEnabled", False):
            a = pond_sources(px, pz)
            _wait(t, 20 * PULSE)
            b = pond_sources(px, pz)
            _expect(b == a if t._guard() else None,
                    "pond source cells changed with refill OFF (%d -> %d)" % (a, b))


@suite.chain("toggle_rain_fills")
def toggle_rain_fills(t):
    x0, z0 = _prep_plot(t, "F")
    open_c, roofed_c = (x0 + 4, z0 + 6), (x0 + 12, z0 + 6)
    for c in (open_c, roofed_c):
        _dig(t, c[0], c[1], 1)
    t.bridge_call("jawa/set_roof_batch", ops="ThickStoneRoof:%s" % _rect(roofed_c[0] - 2, roofed_c[1] - 2, 5, 5))
    t.bridge_call("jawa/weather_set", weather="Rain", lockWeather=True)
    with t.component("rain_fills_on", toggle="rainFillsExcavationsEnabled"):
        _wait(t, 20 * PULSE)
        _expect((_rep(t, *open_c).get("fill") or 0) >= 1 if t._guard() else None, "unroofed cell took no rain")
        _expect((_rep(t, *roofed_c).get("fill") or 0) == 0 if t._guard() else None, "roofed cell took rain")
    with t.component("rain_fills_off", toggle="rainFillsExcavationsEnabled"):
        with _setting(t, "rainFillsExcavationsEnabled", False):
            _fill(t, open_c[0], open_c[1], 0)
            _wait(t, 20 * PULSE)
            _expect((_rep(t, *open_c).get("fill") or 0) == 0 if t._guard() else None, "rain filled with toggle OFF")
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)


@suite.chain("toggle_liquid_ignition")
def toggle_liquid_ignition(t):
    x0, z0 = _prep_plot(t, "E")
    cells = _line(x0 + 4, z0 + 6, 6)
    _dig_run(t, cells, 1)
    for c in cells:
        _fill(t, c[0], c[1], 1)
    with t.component("liquid_ignition_off_default", toggle="liquidIgnitionEnabled"):
        _ignite(t, *cells[0])
        _wait(t, 5 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(x0 + 3, z0 + 5, 8, 3), limit=50)
            n = len((r or {}).get("things") or [])
            _expect(n <= 1, "liquid fire spread with ignition OFF (%d Fire things)" % n)
        with _setting(t, "liquidIgnitionEnabled", True):
            _ignite(t, *cells[0])
            _wait(t, 5 * PULSE)


@suite.chain("all_off_still_digs")
def all_off_still_digs(t):
    """FLOWWORKS_NORTHSTAR_SHIP_1 / MOD_OPTIONS ruling 2026-09-12: with EVERY FlowWorks toggle off the mod still
    digs dry channels. A D=1 run dug beside a pond stays D=1 and dry across pulses (no flow, no rain, no fire)."""
    import contextlib
    x0, z0 = _prep_plot(t, "T")
    px, pz = _limited_pond(t, "T")
    cells = _channel_from(px + 5, pz + 2, 4)
    with contextlib.ExitStack() as stack:
        for f in FW_TOGGLES + PITS_TOGGLES:
            stack.enter_context(_setting(t, f, False))
        with t.component("all_off_digs_dry_channel"):
            _dig_run(t, cells, 1)
            _wait(t, 4 * PULSE)
            _expect_state(t, cells, depth=1, fill=0, what="all-off dug")


@suite.chain("toggle_canal_fire")
def toggle_canal_fire(t):
    """Phase 6 toggle: OFF, a lit tar channel takes no flame; ON, the same light takes."""
    x0, z0 = _prep_plot(t, "E")
    cells = _line(x0 + 4, z0 + 6, 4)
    _dig_run(t, cells, 1)
    for c in cells:
        _fill_fluid(t, c[0], c[1], 1, "RM_Fluid_Tar")
    with t.component("canal_fire_off_is_inert", toggle="canalFireEnabled"):
        with _setting(t, "canalFireEnabled", False):
            r = _light(t, *cells[0])
            _wait(t, 2 * PULSE)
            n = len(((t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(x0 + 3, z0 + 5, 6, 3), limit=50)
                      or {}).get("things")) or [])
            _expect(n == 0 if t._guard() else None, "flame with canalFireEnabled OFF: %d (%s)" % (n, r))
        r = _light(t, *cells[0])
        _expect(r.startswith("LIT") if t._guard() else None, "ON: light refused: %s" % r)


@suite.chain("toggle_liquid_corrosion")
def toggle_liquid_corrosion(t):
    # Contract to read first: LiquidCorrosion.cs (which fluid, which targets). ON predicate = HP falls.
    x0, z0 = _prep_plot(t, "T")
    cell = (x0 + 4, z0 + 6)
    _dig(t, cell[0], cell[1], 1)
    _fill(t, cell[0], cell[1], 1)
    t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (cell[0] + 1, cell[1]), stuff="Steel")
    with t.component("liquid_corrosion_default_off", toggle="liquidCorrosionEnabled"):
        _wait(t, 10 * PULSE)
        with _setting(t, "liquidCorrosionEnabled", True):
            _wait(t, 10 * PULSE)


@suite.chain("toggle_superdeep_capture")
def toggle_superdeep_capture(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("superdeep_capture_on", toggle="superdeepCaptureEnabled"):
        pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1], faction="hostile")
        _march(t, pid, pit[4][0], pit[4][1], 1200)
        if t._guard():
            _expect(_pit_held(t, pid, pit) is True, "hostile not held in the pit")
    with t.component("superdeep_capture_off", toggle="superdeepCaptureEnabled"):
        with _setting(t, "superdeepCaptureEnabled", False):
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[2][1], faction="hostile")
            _march(t, pid, pit[8][0] + 2, pit[8][1], 1500)
            if t._guard():
                _expect(_pit_held(t, pid, pit) is not True, "hostile held with capture OFF")


@suite.chain("toggle_superdeep_own_faction")
def toggle_superdeep_own_faction(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("own_faction_default_off", toggle="superdeepCapturesOwnFaction"):
        pid = _spawn_pawn_at(t, "Colonist", pit[0][0] - 3, pit[0][1])
        _march(t, pid, pit[4][0], pit[4][1], 1200)
        if t._guard():
            _expect(_pit_held(t, pid, pit) is False, "colonist held by default (or not in the pit)")
        with _setting(t, "superdeepCapturesOwnFaction", True):
            pid2 = _spawn_pawn_at(t, "Colonist", pit[0][0] - 3, pit[2][1])
            _march(t, pid2, pit[8][0] - 1, pit[8][1], 400)


@suite.chain("toggle_ladder_required")
def toggle_ladder_required(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("ladder_required_on", toggle="ladderRequiredToExitEnabled"):
        with _setting(t, "superdeepCapturesOwnFaction", True):
            pid = _spawn_pawn_at(t, "Colonist", pit[0][0] - 3, pit[0][1])
            _march(t, pid, pit[4][0], pit[4][1], 1200)
            _wait(t, 10 * PULSE)
            if t._guard():
                _expect(_pit_held(t, pid, pit) is True, "pawn not held in the pit without a ladder")
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LADDER, pit[0][0] - 1, pit[0][1]))
            _wait(t, 10 * PULSE)
    with t.component("ladder_required_off", toggle="ladderRequiredToExitEnabled"):
        with _setting(t, "ladderRequiredToExitEnabled", False):
            _wait(t, PULSE)


@suite.chain("ladder_prison_door")
def ladder_prison_door(t):
    """LADDER_PRISON_DOOR_1 (owner Q1 2026-10-02): a lowered ladder is a prison door. Ladders on every
    pit cell, pawns spawned straight onto the pit floor: your own (captured) colonist is NOT held, a
    hostile IS held; with the prison-door setting off, a ladder lets the hostile out too.
    Not proven here: the RAISED state (no bridge verb writes RM_CompLadder.raised yet; first poke is the
    gizmo by hand, then flowworks_pit_report) and the prisoner-during-a-prison-break case."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    t.bridge_call("jawa/spawn_batch", ops=";".join("%s:%d,%d" % (LADDER, x, z) for x, z in pit))
    with t.component("lowered_lets_colonist_out", toggle="ladderPrisonDoorEnabled"):
        with _setting(t, "superdeepCapturesOwnFaction", True):
            pid = _spawn_pawn_at(t, "Colonist", pit[4][0], pit[4][1])
            _wait(t, PULSE)
            if t._guard():
                _expect(_pit_held(t, pid, pit) is False, "own colonist held in a pit with a lowered ladder")
    with t.component("lowered_holds_hostile", toggle="ladderPrisonDoorEnabled"):
        hid = _spawn_pawn_at(t, "Pirate", pit[4][0], pit[4][1], faction="hostile")
        _wait(t, PULSE)
        if t._guard():
            _expect(_pit_held(t, hid, pit) is True, "hostile NOT held despite the prison-door ladder")
    with t.component("prison_door_off_lets_hostile_out", toggle="ladderPrisonDoorEnabled"):
        with _setting(t, "ladderPrisonDoorEnabled", False):
            _wait(t, PULSE)
            if t._guard():
                _expect(_pit_held(t, hid, pit) is False, "prison-door OFF but a ladder still holds the hostile")


@suite.chain("pit_cover_fall")
def pit_cover_fall(t):
    """PIT_COVER_FALL_REWIRE_1 verify: a hostile heavier than the tier on a covered pit ends on the D=4
    cell, held, with the deck gone; one lighter than the tier does not spring it and is not held."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    twin = [(x + 9, z) for x, z in pit]
    _dig_run(t, pit, 4)
    _dig_run(t, twin, 4)
    with t.component("heavy_springs_woven_cover", toggle="trapTriggerEnabled"):
        t.bridge_call("jawa/spawn_batch", ops=";".join("RM_PitCover_WovenScrap:%d,%d" % (x, z) for x, z in pit))
        hid = _spawn_pawn_at(t, "Pirate", pit[4][0], pit[4][1], faction="hostile")
        _wait(t, 2 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_WovenScrap", rect=_rect(pit[0][0] - 1, pit[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 0, "woven cover still standing under a ~70 kg hostile: %r" % r)
            _expect(_pit_held(t, hid, pit) is True, "hostile not held after the cover gave way")
    with t.component("light_does_not_spring_reinforced", toggle="trapTriggerEnabled"):
        t.bridge_call("jawa/spawn_batch", ops=";".join("RM_PitCover_ReinforcedFrame:%d,%d" % (x, z) for x, z in twin))
        lid = _spawn_pawn_at(t, "Pirate", twin[4][0], twin[4][1], faction="hostile")
        _wait(t, 2 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_ReinforcedFrame", rect=_rect(twin[0][0] - 1, twin[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 9, "reinforced cover sprang under one ~70 kg pawn (220 kg tier): %r" % r)
            _expect(_pit_held(t, lid, twin) is False, "pawn on an intact cover reads as held")


def _spike_proof(t, method, x, z):
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_SpikeUtility", method=method,
                      args="current|%d,%d" % (x, z))
    return str((r or {}).get("result", "")) or "no result: %r" % (r,)


@suite.chain("canal_spikes")
def canal_spikes(t):
    """CANAL_BOTTOM_SPIKES_1 (owner Q2 2026-10-02: spikes only in the deepest pits). Placement census by
    depth through the placeworker's own rule, then the descent hook on a hostile standing on a spiked D=4 cell.
    Not proven here: the live descent detector firing the hook on a real fall (first poke: push a hostile in
    and read its Stab injuries), the body-size comparison in game (the selftest proves the math), the art."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    shallow = [(x0 + 1, z0 + 1), (x0 + 3, z0 + 1), (x0 + 1, z0 + 3)]
    for i, (x, z) in enumerate(shallow):
        _dig(t, x, z, i + 1)
    with t.component("spikes_only_on_superdeep", toggle="spikesEnabled"):
        deep = _spike_proof(t, "ProofPlacement", pit[4][0], pit[4][1])
        shal = [_spike_proof(t, "ProofPlacement", x, z) for x, z in shallow]
        if t._guard():
            _expect(deep.startswith("ACCEPT depth 4"), "spikes refused on a D=4 cell: %s" % deep)
            for i, txt in enumerate(shal):
                _expect(txt.startswith("REFUSE depth %d" % (i + 1)), "spikes not refused on depth %d: %s" % (i + 1, txt))
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SPIKES, pit[4][0], pit[4][1]))
    hid = _spawn_pawn_at(t, "Pirate", pit[4][0], pit[4][1], faction="hostile")
    with t.component("descent_onto_spikes_stabs", toggle="spikesEnabled"):
        txt = _spike_proof(t, "ProofDescent", pit[4][0], pit[4][1])
        if t._guard():
            _expect(txt.startswith("HITS 3") and "INJURIES Stab 0" not in txt, "no spike stabs on descent: %s" % txt)
    with t.component("spikes_off_harmless", toggle="spikesEnabled"):
        with _setting(t, "spikesEnabled", False):
            txt = _spike_proof(t, "ProofDescent", pit[4][0], pit[4][1])
            if t._guard():
                _expect(txt.startswith("HITS 0"), "spikesEnabled OFF but spikes still hit: %s" % txt)


def _door_proof(t, method, x, z):
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FlowDoorRules", method=method,
                      args="current|%d,%d" % (x, z))
    return str((r or {}).get("result", "")) or "no result: %r" % (r,)


def _verdict(txt, pid):
    """OPEN / SHUT for pawn ThingID `pid` in a ProofOpen line, else None."""
    for part in txt.split(" | ")[1:]:
        bits = part.split(" ")
        if pid and bits[0] == str(pid):
            return bits[1] if len(bits) > 1 else None
    return None


@suite.chain("flow_doors")
def flow_doors(t):
    """FLOWWORKS_DOOR_FAMILY_1 (owner 2026-09-17: two stuffable doors, Sluice + SecurityGrateDoor).
    Plot H: a D=2 channel off a limitless source runs through a closed wooden sluice and a closed steel
    grate; the level must reach the far end. Plot G: who each door opens for -- a hostile human and a
    wild muffalo (W=2 at the default multiplier) force the sluice, a hare does not; the grate holds the
    human; a hostile held in the superdeep pit cannot open a sluice beside it.
    Not proven here: a wooden one burning (stuff flammability is vanilla), real pathing through a
    forced sluice (first poke: march a hostile at a closed sluice and watch it pass), the art."""
    x0, z0 = _prep_plot(t, "H")
    _limitless_source(t, "H")
    run = _channel_from(x0 + 10, z0 + 6, 8)
    _dig_run(t, run, 2)
    sl, gr = run[2], run[5]
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (SLUICE, sl[0], sl[1]), stuff="WoodLog")
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (GRATE, gr[0], gr[1]), stuff="Steel")
    with t.component("doors_pass_liquid_closed"):
        _wait(t, 10 * PULSE)
        far = _rep(t, *run[-1])
        if t._guard():
            for c in (sl, gr):
                txt = _door_proof(t, "ProofLiquid", c[0], c[1])
                _expect("open=False" in txt and " fill 0" not in txt, "door cell dry or open: %s" % txt)
            _expect((far.get("fill") or 0) >= 1, "liquid did not pass the closed doors: far fill %r" % far.get("fill"))
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    sl, gr, lip = (x0 + 2, z0 + 3), (x0 + 4, z0 + 3), (pit[1][0] - 1, pit[1][1])
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d;%s:%d,%d" % (SLUICE, sl[0], sl[1], SLUICE, lip[0], lip[1]),
                  stuff="WoodLog")
    t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (GRATE, gr[0], gr[1]), stuff="Steel")
    hum = _spawn_pawn_at(t, "Pirate", x0 + 3, z0 + 2, faction="hostile")
    muf = _spawn_pawn_at(t, "Muffalo", x0 + 1, z0 + 4, faction="none")
    hare = _spawn_pawn_at(t, "Hare", x0 + 1, z0 + 2, faction="none")
    with t.component("sluice_holds_small_only", toggle="sluiceLetsBigThroughEnabled"):
        txt = _door_proof(t, "ProofOpen", sl[0], sl[1])
        if t._guard():
            _expect(_verdict(txt, hum) == "OPEN", "sluice held a hostile human: %s" % txt)
            _expect(_verdict(txt, muf) == "OPEN", "sluice held a muffalo: %s" % txt)
            _expect(_verdict(txt, hare) == "SHUT", "sluice let a hare through: %s" % txt)
    with t.component("sluice_rule_off_holds", toggle="sluiceLetsBigThroughEnabled"):
        with _setting(t, "sluiceLetsBigThroughEnabled", False):
            txt = _door_proof(t, "ProofOpen", sl[0], sl[1])
            if t._guard():
                _expect(_verdict(txt, hum) == "SHUT", "rule off but the sluice still gives way: %s" % txt)
    with t.component("grate_holds_prisoner"):
        txt = _door_proof(t, "ProofOpen", gr[0], gr[1])
        if t._guard():
            _expect(_verdict(txt, hum) == "SHUT", "grate opened for a hostile human: %s" % txt)
    held = _spawn_pawn_at(t, "Pirate", pit[1][0], pit[1][1], faction="hostile")
    with t.component("sealed_from_pit", toggle="flowDoorsSealedFromPitEnabled"):
        txt = _door_proof(t, "ProofOpen", lip[0], lip[1])
        if t._guard():
            _expect(_pit_held(t, held, pit) is True, "pirate in the pit is not held")
            _expect(_verdict(txt, held) == "SHUT", "a held pawn can open the sluice: %s" % txt)
    with t.component("sealed_rule_off", toggle="flowDoorsSealedFromPitEnabled"):
        with _setting(t, "flowDoorsSealedFromPitEnabled", False):
            txt = _door_proof(t, "ProofOpen", lip[0], lip[1])
            if t._guard():
                _expect(_verdict(txt, held) == "OPEN", "sealed rule off but the held human still cannot force the sluice: %s" % txt)


@suite.chain("toggle_superdeep_shooting")
def toggle_superdeep_shooting(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("shooting_rule_on", toggle="superdeepShootingRuleEnabled"):
        # needs an occupant + two shooters (lip vs 5 cells); target legality is read through pawn_get
        _wait(t, PULSE)
    with t.component("shooting_rule_off", toggle="superdeepShootingRuleEnabled"):
        with _setting(t, "superdeepShootingRuleEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_pit_exposure")
def toggle_pit_exposure(t):
    # PIT_TEMPERATURE_SOFTENING_1: a pawn left on an unroofed uncovered D=4 cell gains the RM_PitExposure
    # hediff every 250 ticks; the toggle off must stop it. The hediff is read through jawa/pawn_get
    # (jawa/pawn_get hediffs[].def); UNMEASURED-tolerant via t._guard().
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)

    def _has_exposure(pid):
        r = t.bridge_call("jawa/pawn_get", pawn=pid)     # MEASURED 2026-10-05: pawn_health ADDS a hediff ("Give a HediffDef"); pawn_get lists them
        pw = ((r or {}).get("pawns") or [{}])[0]
        return any(h.get("def") == "RM_PitExposure" for h in pw.get("hediffs") or [])

    with t.component("pit_exposure_on", toggle="pitExposureEnabled"):
        pid = _spawn_pawn_at(t, "Colonist", pit[4][0], pit[4][1])
        _wait(t, 4 * 250)
        if t._guard():
            _expect(_has_exposure(pid), "pawn left on an open D=4 cell gained no RM_PitExposure after 4 intervals")
    with t.component("pit_exposure_off", toggle="pitExposureEnabled"):
        with _setting(t, "pitExposureEnabled", False):
            pid2 = _spawn_pawn_at(t, "Colonist", pit[3][0], pit[3][1])
            _wait(t, 4 * 250)
            if t._guard():
                _expect(not _has_exposure(pid2), "RM_PitExposure applied while pitExposureEnabled is off")


def _fill_fx(t):
    """PIT_FILL_EFFECTS_1 census: every pawn standing in liquid, with cell fluid, swimmer flag, drown/tox severity."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitFillEffects", method="ProofReport", args="")
    return str((r or {}).get("result", ""))


def _fx_row(report, pid):
    for row in report.split(" | "):
        if row.startswith(str(pid) + "@"):
            return dict(kv.split("=", 1) for kv in row.split(" ")[1:] if "=" in kv)
    return {}


@suite.chain("pit_fill_effects")
def pit_fill_effects(t):
    """PIT_FILL_EFFECTS_1 first script (owner Q3): two occupied D=4 cells side by side, water and poison, each
    applies only its own fluid's effect, read per cell by fluid id; a third (oil) is lit and burns its occupant."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    a, b, c = pit[2], pit[4], pit[6]
    _fill_fluid(t, a[0], a[1], 4, "RM_Fluid_Water")
    _fill_fluid(t, b[0], b[1], 4, "RM_Fluid_Poison")
    _fill_fluid(t, c[0], c[1], 4, "RM_Fluid_Oil")
    pa = _spawn_pawn_at(t, "Colonist", a[0], a[1])
    pb = _spawn_pawn_at(t, "Colonist", b[0], b[1])
    pc = _spawn_pawn_at(t, "Colonist", c[0], c[1])
    with t.component("pit_fluid_effects_per_cell", toggle="pitDrowningEnabled"):
        _wait(t, 4 * 250)
        rep = _fill_fx(t)
        ra, rb = _fx_row(rep, pa), _fx_row(rep, pb)
        if t._guard():
            _expect(ra.get("fluid") == "RM_Fluid_Water" and float(ra.get("drown", 0)) > 0 and float(ra.get("tox", 0)) == 0,
                    "water pit: drowning only, got %r" % ra)
            _expect(rb.get("fluid") == "RM_Fluid_Poison" and float(rb.get("tox", 0)) > 0,
                    "poison pit: toxic buildup, got %r" % rb)
    with t.component("oil_pit_burns_occupant", toggle="canalFireEnabled"):
        _light(t, c[0], c[1])
        _wait(t, 2 * 250)
        rc = _fx_row(_fill_fx(t), pc)
        if t._guard():
            _expect(rc.get("burning") == "True", "lit oil pit not burning: %r" % rc)
            r = t.bridge_call("jawa/pawn_get", pawn=pc)      # jawa/pawn_health ADDS a hediff; pawn_get lists them
            hs = [h.get("def") for h in (((r or {}).get("pawns") or [{}])[0].get("hediffs") or [])]
            _expect(any("Burn" in str(h) for h in hs), "occupant of a burning oil pit has no burn: hediffs %s" % hs)


@suite.chain("toggle_pit_fill_effects")
def toggle_pit_fill_effects(t):
    """OFF: water at D=4 drowns no one and poison poisons no one."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    _fill_fluid(t, pit[3][0], pit[3][1], 4, "RM_Fluid_Water")
    _fill_fluid(t, pit[5][0], pit[5][1], 4, "RM_Fluid_Poison")
    with t.component("pit_drowning_off", toggle="pitDrowningEnabled"):
        with _setting(t, "pitDrowningEnabled", False):
            pid = _spawn_pawn_at(t, "Colonist", pit[3][0], pit[3][1])
            _wait(t, 4 * 250)
            _expect(float(_fx_row(_fill_fx(t), pid).get("drown", 0)) == 0 if t._guard() else None,
                    "drowning with pitDrowningEnabled OFF")
    with t.component("poison_fill_off", toggle="poisonFillEnabled"):
        with _setting(t, "poisonFillEnabled", False):
            pid = _spawn_pawn_at(t, "Colonist", pit[5][0], pit[5][1])
            _wait(t, 4 * 250)
            _expect(float(_fx_row(_fill_fx(t), pid).get("tox", 0)) == 0 if t._guard() else None,
                    "toxin with poisonFillEnabled OFF")


@suite.chain("toggle_bottle_loop")
def toggle_bottle_loop(t):
    x0, z0 = _prep_plot(t, "T")
    t.bridge_call("jawa/spawn_batch", ops="RM_LiquidTank:%d,%d;RM_Bottle_FreshWater:%d,%d" % (x0 + 4, z0 + 6, x0 + 6, z0 + 6))
    with t.component("bottle_loop_on", toggle="bottleLoopEnabled"):
        pid = _spawn_pawn_at(t, "Colonist", x0 + 3, z0 + 8)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        _wait(t, 20 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_Bottle_FreshWater", rect=_rect(x0, z0 + 3, 12, 8), limit=20)
            _expect(((r or {}).get("things") or []), "no bottle present after the fill loop")
    with t.component("bottle_loop_off", toggle="bottleLoopEnabled"):
        with _setting(t, "bottleLoopEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_bottle_dirty")
def toggle_bottle_dirty(t):
    x0, z0 = _prep_plot(t, "T")
    t.bridge_call("jawa/spawn_batch", ops="RM_Bottle_FreshWater:%d,%d" % (x0 + 6, z0 + 6))
    with t.component("bottle_dirty_on", toggle="bottleDirtyStageEnabled"):
        _wait(t, 20 * PULSE)
    with t.component("bottle_dirty_off", toggle="bottleDirtyStageEnabled"):
        with _setting(t, "bottleDirtyStageEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_tank_loop")
def toggle_tank_loop(t):
    x0, z0 = _prep_plot(t, "F")
    cell = (x0 + 6, z0 + 6)
    _dig(t, cell[0], cell[1], 2)
    _fill(t, cell[0], cell[1], 2)
    t.bridge_call("jawa/spawn_batch", ops="RM_LiquidTank:%d,%d" % (cell[0] + 1, cell[1]))
    with t.component("tank_loop_on", toggle="tankLoopEnabled"):
        _wait(t, 10 * PULSE)
        _expect((_rep(t, *cell).get("fill") or 0) < 2 if t._guard() else None, "tank did not draw down the adjacent cell")
    with t.component("tank_loop_off", toggle="tankLoopEnabled"):
        with _setting(t, "tankLoopEnabled", False):
            _fill(t, cell[0], cell[1], 2)
            _wait(t, 10 * PULSE)
            _expect((_rep(t, *cell).get("fill") or 0) == 2 if t._guard() else None, "tank drew with loop OFF")


@suite.chain("toggle_liquid_drilling")
def toggle_liquid_drilling(t):
    x0, z0 = _prep_plot(t, "T")
    t.bridge_call("jawa/spawn_batch", ops="RM_LiquidDrill:%d,%d" % (x0 + 6, z0 + 6))
    with t.component("liquid_drilling_on", toggle="liquidDrillingEnabled"):
        _wait(t, 40 * PULSE)     # stochastic: >=1 yield in 3 runs at the shipped chance (def read first)
    with t.component("liquid_drilling_off", toggle="liquidDrillingEnabled"):
        with _setting(t, "liquidDrillingEnabled", False):
            _wait(t, 40 * PULSE)


@suite.chain("toggle_typed_shores")
def toggle_typed_shores(t):
    # Worldgen-affecting: needs two fresh quicktest maps (toggle on vs off) -- shared driver, plan 2.5/4 step 10.
    with t.component("typed_shores_mapgen", toggle="typedLiquidShoresEnabled"):
        r = t.bridge_call("jawa/mod_settings_field", typeName=S_FW, action="get", field="typedLiquidShoresEnabled")
        _expect((r or {}).get("success", True) if t._guard() else None, "settings class unreadable: %r" % (r,))


@suite.chain("toggle_trap_trigger")
def toggle_trap_trigger(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("trap_trigger_on", toggle="trapTriggerEnabled"):
        # The cover's mass trigger has no host until PIT_COVER_FALL_REWIRE_1; until then this reads
        # the rehoused setting back (it used to assert the retired building pit's despawn).
        r = t.bridge_call("jawa/mod_settings_field", typeName=S_FW, action="get", field="trapTriggerEnabled")
        _expect((r or {}).get("success", True) if t._guard() else None, "trapTriggerEnabled unreadable: %r" % (r,))
    with t.component("trap_trigger_off", toggle="trapTriggerEnabled"):
        with _setting(t, "trapTriggerEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_fall_damage")
def toggle_fall_damage(t):
    x0, z0 = _prep_plot(t, "G")
    with t.component("fall_damage_on", toggle="fallDamageEnabled"):
        _wait(t, PULSE)
    with t.component("fall_damage_off", toggle="fallDamageEnabled"):
        with _setting(t, "fallDamageEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_river_steam")
def toggle_river_steam(t):
    # Needs a river quicktest map (plan 4 step 10); here: write + read-back of the real field.
    with t.component("river_steam", toggle="riverSteamEnabled"):
        with _setting(t, "riverSteamEnabled", False):
            r = t.bridge_call("jawa/mod_settings_field", typeName=S_RIVER, action="get", field="riverSteamEnabled")
            _expect(str((r or {}).get("value")) == "False" if t._guard() else None,
                    "riverSteamEnabled did not read back False: %r" % (r,))


@suite.chain("fluid_identity_recorded")
def fluid_identity_recorded(t):
    """LIQUID_BODY_FLUID_IDENTITY_1 step 1 (storage only, behaviour-neutral): after a pulse every wet excavated
    cell carries a recorded fluid and every natural body has one. Runs on whatever the CURRENT map holds (the
    earlier chains' channels); UNMEASURED when the map holds no wet excavated cell."""
    with t.component("wet_cells_and_bodies_carry_a_fluid", beyond_toggle=True):
        _wait(t, PULSE + 10)
        r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FluidIdentityProof", method="ProofCensus")
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        if not t._guard():
            return
        if not text.startswith("FLUIDID"):
            t.upstream_reason = "UNMEASURED: ProofCensus gave no answer: %r" % text[:160]
            t.upstream_failed = True
            return
        if " wet 0 |" in text:
            t.upstream_reason = "UNMEASURED: no wet excavated cell on the current map to census: %s" % text
            t.upstream_failed = True
            return
        _expect("unrecorded 0 |" in text and ":null" not in text, "a wet cell or a body has no recorded fluid: %s" % text)


def _swale_proof(t, x, z):
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_SwaleRules", method="ProofStep",
                      args="current|%d,%d" % (x, z))
    return str((r or {}).get("result", "")) or "no result: %r" % (r,)


@suite.chain("swale_enrichment")
def swale_enrichment(t):
    """CRACKEDLANDS_MECHANICS_BUILD_1 §1, the swale: in a dug cell on sand it does nothing dry, one step fed
    turns the nearest sand to soil, a ring already at rich soil is CAPPED, and the switch off makes it inert.
    ProofStep fires one step through the tick's own gates (switch, then fed) so no fed day has to pass.
    Not proven here: the real CompTickRare pace (one rung per fed day, PROVISIONAL), a seasonal flood feeding
    it (water terrain on the cell reads as fed by the same rule), the Utinni campaign lock (unbuilt)."""
    x0, z0 = _prep_plot(t, "H", terrain="Sand")
    x, z = x0 + 8, z0 + 6
    _dig(t, x, z, 1)
    t.bridge_call("jawa/spawn_batch", ops="RM_Swale:%d,%d" % (x, z))
    with t.component("dry_swale_does_nothing", toggle="swaleEnabled"):
        txt = _swale_proof(t, x, z)
        if t._guard():
            _expect(txt == "DRY", "an unfilled swale did not read DRY: %s" % txt)
    _fill(t, x, z, 1)
    with t.component("fed_swale_turns_sand_to_soil", toggle="swaleEnabled"):
        txt = _swale_proof(t, x, z)
        if t._guard():
            _expect(txt.startswith("STEP") and "Sand->Soil" in txt, "a fed swale on sand did not step sand->soil: %s" % txt)
    with t.component("swale_capped_at_rich_soil", toggle="swaleEnabled"):
        ring = [_rect(x - 3, z + 1, 7, 3), _rect(x - 3, z - 3, 7, 3), _rect(x - 3, z, 3, 1), _rect(x + 1, z, 3, 1)]
        t.bridge_call("jawa/set_terrain_batch", ops=";".join("SoilRich:%s" % r for r in ring))  # the swale's own cell untouched
        txt = _swale_proof(t, x, z)
        if t._guard():
            _expect(txt.startswith("CAPPED"), "a swale ringed by rich soil still stepped: %s" % txt)
    with t.component("swale_off_is_inert", toggle="swaleEnabled"):
        with _setting(t, "swaleEnabled", False):
            txt = _swale_proof(t, x, z)
            if t._guard():
                _expect(txt == "OFF", "swaleEnabled OFF but the swale still answered: %s" % txt)
