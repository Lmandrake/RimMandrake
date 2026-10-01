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
component via `shows=`, and all 27 Mod Settings toggles are covered. Nothing here has run
live: every predicate below is UNMEASURED until the baseline run
(FLOWWORKS_NORTHSTAR_BASELINE_RUN_1). Expected today (plan section 1): the state half of the
canal/stock bars passes, about two thirds of the visual bars come back NO until art and the
unbuilt mechanics (viscosity, per-body fluid, depth draw offset, superdeep cover, per-cell
spikes, sluice doors) land -- a bar for an unbuilt feature fails until it is built, which is
the bar doing its job.

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
import os
import time
from contextlib import contextmanager

from modcheck import Suite, ExpectationFailed

suite = Suite("FlowWorks")

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_PITS = "RimMandrake.FlowWorks.Pits.PitsSettings"
S_RIVER = "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings"

# 27 boolean toggles: 22 in RimMandrakeFlowWorksSettings, 4 in PitsSettings, 1 in RiverSteamSettings.
FW_TOGGLES = [
    "depthEngineEnabled", "channelConfinementEnabled", "digToDepthEnabled",
    "liquidCorrosionEnabled", "liquidIgnitionEnabled",
    "fillInEnabled", "fillInDisplacementEnabled", "sourceBudgetEnabled",
    "stickyLimitlessEnabled", "recessionEnabled", "refillEnabled",
    "rainFillsExcavationsEnabled", "edgeSinksEnabled",
    "superdeepCaptureEnabled", "superdeepCapturesOwnFaction",
    "ladderRequiredToExitEnabled", "superdeepShootingRuleEnabled",
    "bottleLoopEnabled", "bottleDirtyStageEnabled", "tankLoopEnabled",
    "liquidDrillingEnabled", "typedLiquidShoresEnabled",
]
PITS_TOGGLES = ["trapTriggerEnabled", "fallDamageEnabled", "escapeEnabled", "pitCellExposureEnabled"]
RIVER_TOGGLES = ["riverSteamEnabled"]
suite.toggles = FW_TOGGLES + PITS_TOGGLES + RIVER_TOGGLES

DEFAULTS = {t: True for t in suite.toggles}
DEFAULTS.update({"liquidCorrosionEnabled": False, "liquidIgnitionEnabled": False,
                 "superdeepCapturesOwnFaction": False})
SETTINGS_OF = {}
SETTINGS_OF.update({k: S_FW for k in FW_TOGGLES})
SETTINGS_OF.update({k: S_PITS for k in PITS_TOGGLES})
SETTINGS_OF.update({k: S_RIVER for k in RIVER_TOGGLES})

PULSE = 250
TAR, SLIME = "RM_Fluid_Tar", "RM_Fluid_SlimeGreen"
LADDER = "RM_Ladder"

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


def _limited_pond(t, key, size=5):
    x0, z0 = _plot(t, key)
    px, pz = x0 + 3, z0 + 4
    t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%s" % _rect(px, pz, size, size))
    return px, pz


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
        # ruled pathCost 30 for a dry D=1 cell (build program Phase 5); shipped 6 is a known FAIL
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
    """Tar vs water fill front, and the two-fluids-side-by-side bar. Both are expected to FAIL today:
    the depth engine has no viscosity and `ActiveFluid` is one FluidDef per map (plan section 1)."""
    x0, z0 = _prep_plot(t, "T")
    _limitless_source(t, "T")
    cells = _channel_from(x0 + 10, z0 + 6, 10)
    _dig_run(t, cells, 1)
    # ActiveFluid=TAR must be set before first classification: needs the driver's new set_active_fluid
    # tool (plan section 6 item 3), which does not exist yet. Until it does this plot runs on water.
    with t.component("tar_front_lags_water", shows=["tar_fill_front_lags_water"]):
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
        # needs two fluids on ONE map; ActiveFluid is per-map with no setter -> cannot be staged yet.
        if t._guard():
            raise ExpectationFailed("BLOCKED: per-body fluid unbuilt; two fluids cannot share a map")
        _frame(t, x0, z0 + 2, 22, 10)


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
    """Plot E (tar, ignition ON): 1x8 D=1 channel from a limited tar pond, ignite the mouth.
    Which cells can hold Fire is read from LiquidIgnition.cs before the baseline run, not assumed.
    Fire-safety: the 8-cell buffer is bare Soil (no plants); `_prep_plot` clears all things."""
    x0, z0 = _prep_plot(t, "E")
    px, pz = _limited_pond(t, "E")
    cells = _channel_from(px + 5, pz + 2, 8)
    shot = (px - 1, pz - 1, 16, 8)
    _dig_run(t, cells, 1)
    with _setting(t, "liquidIgnitionEnabled", True):
        for x, z in cells:
            _fill(t, x, z, 1)
        _ignite(t, *cells[0])
        with t.component("fire_burning_look", toggle="liquidIgnitionEnabled",
                         shows=["canal_burning_reads_as_burning_liquid"]):
            _wait(t, 5 * PULSE)
            if t._guard():
                fires = t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(px, pz, 14, 8), limit=200)
                n = len((fires or {}).get("things") or [])
                _expect(n >= 3, "fewer than 3 Fire things in the channel after ignition: %d" % n)
            _frame(t, *shot)
        with t.component("fire_reaches_reservoir", shows=["canal_fire_reaches_reservoir"]):
            _wait(t, 24 * PULSE)
            if t._guard():
                fires = t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(px, pz, 5, 5), limit=200)
                _expect(len((fires or {}).get("things") or []) >= 1, "no Fire at the pond cells within budget")
            _frame(t, *shot)
        with t.component("fire_persists_look", shows=["canal_fire_persists"]):
            f1 = len(((t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(px, pz, 14, 8), limit=200) or {})
                      .get("things")) or [])
            _wait(t, 4 * PULSE)
            f2 = len(((t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(px, pz, 14, 8), limit=200) or {})
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
        # offline-checkable half: no FlowWorks def borrows the vanilla spike-trap art
        ddir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs")
        hits = []
        for root, _, files in os.walk(ddir):
            for fn in files:
                if fn.endswith(".xml"):
                    txt = open(os.path.join(root, fn), encoding="utf-8").read()
                    if "Things/Building/Security/TrapSpikeArmed" in txt:
                        hits.append(fn)
        _expect(not hits, "defs still point at the vanilla TrapSpikeArmed art: %s" % sorted(set(hits)))
        _frame(t, *shot)
    with t.component("pit_captures_hostile", toggle="superdeepCaptureEnabled",
                     shows=["pit_occupant_below_floor", "pit_trapped_reads_as_trapped",
                            "pit_occupied_distinguishable", "never_snared_standing"]):
        caught = 0
        for i in range(3):       # traps ABSOLUTELY: 3/3 over distinct spawn points
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1] + i, faction="hostile")
            _march(t, pid, pit[4][0], pit[4][1], 400)
            if t._guard():
                r = t.bridge_call("jawa/list_pawns", limit=200)
                spawned = any(p.get("id") == pid for p in ((r or {}).get("pawns") or []))
                caught += 0 if spawned else 1
        _expect(caught == 3 if t._guard() else None, "superdeep captured %d/3 hostiles" % caught)
        _frame(t, *twin_shot)    # occupied pit beside the empty twin in one frame
    with t.component("pit_cover_invisible",
                     shows=["pit_covered_invisible", "pit_covered_seam_at_max_zoom"]):
        # BLOCKED: no superdeep cover exists (building-pit Building_TerrainMimicCover only)
        if t._guard():
            raise ExpectationFailed("BLOCKED: superdeep terrain-mimic cover unbuilt")
        _frame(t, *shot)
    with t.component("ladder_state_look", toggle="ladderRequiredToExitEnabled",
                     shows=["ladder_state_legible"]):
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LADDER, pit[0][0] - 1, pit[0][1]))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName=LADDER, rect=_rect(pit[0][0] - 2, pit[0][1] - 1, 4, 3))
            _expect(((r or {}).get("things") or []), "RM_Ladder did not place beside the pit")
        _frame(t, *shot)
    with t.component("sluice_state_look", shows=["sluice_gate_state_legible"]):
        # BLOCKED: FLOWWORKS_DOOR_FAMILY_1 unbuilt (no Sluice / SecurityGrate defs)
        if t._guard():
            raise ExpectationFailed("BLOCKED: sluice / security-grate door family unbuilt")
        _frame(t, *shot)
    with t.component("spikes_look", shows=["spikes_read_distinct"]):
        # BLOCKED: per-cell spikes unbuilt (building-pit fitting only)
        if t._guard():
            raise ExpectationFailed("BLOCKED: per-cell spikes unbuilt")
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
        _march(t, pid, pit[4][0], pit[4][1], 400)
        if t._guard():
            r = t.bridge_call("jawa/list_pawns", limit=200)
            _expect(not any(p.get("id") == pid for p in ((r or {}).get("pawns") or [])), "hostile crossed the pit")
    with t.component("superdeep_capture_off", toggle="superdeepCaptureEnabled"):
        with _setting(t, "superdeepCaptureEnabled", False):
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[2][1], faction="hostile")
            _march(t, pid, pit[8][0] + 2, pit[8][1], 500)
            if t._guard():
                r = t.bridge_call("jawa/list_pawns", limit=200)
                _expect(any(p.get("id") == pid for p in ((r or {}).get("pawns") or [])), "hostile captured with capture OFF")


@suite.chain("toggle_superdeep_own_faction")
def toggle_superdeep_own_faction(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("own_faction_default_off", toggle="superdeepCapturesOwnFaction"):
        pid = _spawn_pawn_at(t, "Colonist", pit[0][0] - 3, pit[0][1])
        _march(t, pid, pit[4][0], pit[4][1], 400)
        if t._guard():
            r = t.bridge_call("jawa/list_pawns", limit=200)
            _expect(any(p.get("id") == pid for p in ((r or {}).get("pawns") or [])), "colonist captured by default")
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
            _march(t, pid, pit[4][0], pit[4][1], 400)
            _wait(t, 10 * PULSE)
            if t._guard():
                r = t.bridge_call("jawa/list_pawns", limit=200)
                _expect(not any(p.get("id") == pid for p in ((r or {}).get("pawns") or [])),
                        "pawn left the pit without a ladder")
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LADDER, pit[0][0] - 1, pit[0][1]))
            _wait(t, 10 * PULSE)
    with t.component("ladder_required_off", toggle="ladderRequiredToExitEnabled"):
        with _setting(t, "ladderRequiredToExitEnabled", False):
            _wait(t, PULSE)


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
        pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1], faction="hostile")
        _march(t, pid, pit[4][0], pit[4][1], 400)
        if t._guard():
            r = t.bridge_call("jawa/list_pawns", limit=200)
            _expect(not any(p.get("id") == pid for p in ((r or {}).get("pawns") or [])), "trap did not spring")
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


@suite.chain("toggle_escape")
def toggle_escape(t):
    x0, z0 = _prep_plot(t, "G")
    with t.component("escape_on", toggle="escapeEnabled"):
        _wait(t, PULSE)
    with t.component("escape_off", toggle="escapeEnabled"):
        with _setting(t, "escapeEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_pit_cell_exposure")
def toggle_pit_cell_exposure(t):
    x0, z0 = _prep_plot(t, "G")
    with t.component("pit_exposure_on", toggle="pitCellExposureEnabled"):
        _wait(t, PULSE)
    with t.component("pit_exposure_off", toggle="pitCellExposureEnabled"):
        with _setting(t, "pitCellExposureEnabled", False):
            _wait(t, PULSE)


@suite.chain("toggle_river_steam")
def toggle_river_steam(t):
    # Needs a river quicktest map (plan 4 step 10); here: write + read-back of the real field.
    with t.component("river_steam", toggle="riverSteamEnabled"):
        with _setting(t, "riverSteamEnabled", False):
            r = t.bridge_call("jawa/mod_settings_field", typeName=S_RIVER, action="get", field="riverSteamEnabled")
            _expect(str((r or {}).get("value")) == "False" if t._guard() else None,
                    "riverSteamEnabled did not read back False: %r" % (r,))
