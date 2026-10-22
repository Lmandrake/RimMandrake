"""northstar/extensions.py -- FlowWorks EXTENSION suite: everything the core proof does not run by default.

Split out of validation.py on 2026-10-05 (owner: "separate the extension tests for flow works as we did for gimme
some slack"; lessons: design/RimMandrake/northstar_densification_lessons.md). The CORE proof is
northstar/validation_v2.py --live --fresh-map (one session, one fresh map, every mechanism row, one log budget);
validation.py wires its rows to the north-star bars and toggles. What lives HERE:

  * VISUAL TRIAL (plot_A..plot_H chains): staged plots on the golden trial site (prep_site.py + preflight_flowworks.py
    live), each ending on the screenshot / before|after diptych the single-frame judge reads. The state half of these
    plots is proven by the core rows; the look is judged on the human review sheet (human_review.py).
  * OPTIONAL FEATURES (toggle_* and feature chains): fire/ignition/corrosion, fill-in toggles,
    recession/refill, capture/ladder OFF sides, prison door, cover fall, spikes, sluice/grate doors, shooting rule,
    exposure, depth draw, pit fill effects, bottles/tanks/drilling, typed shores, trap trigger, fall damage, river
    steam, fluid identity census, swale.

Seven toggle chains were DELETED here because a core row fails whenever they would, on BOTH sides of the switch:
depthEngine (E4_engine_off/E4_engine_on_scheduled), digToDepth (S6), edgeSinks (E5_sink_drains/E5n/E5_sinks_back_on),
sourceBudget (E3_budget_exhaustion/E3n), stickyLimitless (S5), rainFills (E6_rain_fills_unroofed/E6n), own-faction
capture (P4b ON / P5n default OFF). git is provenance.

Run on request only (never by the core proof):
    python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live [--chains a,b]   # bridge held
    python3    src/RimMandrake/FlowWorks/northstar/selftest_extensions.py                    # offline, 0 ticks
validation.py still DECLARES every component here (toggle + shows) so the modcheck floor counts them, and a
situational `modcheck` re-run executes them exactly as before the split.

Conventions (unchanged from the suite they came from):
  dig   `jawa/flowworks_excavation_drive {x,z,deepenLevels:N,setFill:-1}`   (engine Deepen())
  fill  `jawa/flowworks_excavation_drive {x,z,deepenLevels:0,setFill:F}`    (TrySetDriverFill)
  read  `jawa/flowworks_excavation_report {x,z}`; `jawa/canal_dig` is a stub that ALWAYS FAILS and is never called.
  * `PULSE` = 250 ticks; settle = step whole pulses. The judge reads only the LAST screenshot of a component;
    `(change)` bars end on a labelled before|after DIPTYCH (`_diptych`) or FAIL.
  * A setting that is not the subject of a component is restored in `finally` by `_setting`.
  * Each chain builds its own plot with `_plot()` at a fixed offset from the suite anchor.
"""
import os
import time
from contextlib import contextmanager

from modcheck import Suite, ExpectationFailed

suite = Suite("FlowWorksExtensions")

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_RIVER = "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings"

# Boolean toggles: all in RimMandrakeFlowWorksSettings except 1 in RiverSteamSettings. Each is covered by a component
# here, by a core row (validation.ROW_TOGGLES), or named in validation.EXTENSION_TOGGLES_OWED
# (pitDepthDrawOffsetEnabled: toggle_pit_depth_draw, 2026-10-05). PIT_LEGACY_CODE_RETIRE_1
# (2026-10-02) retired PitsSettings: trapTriggerEnabled + fallDamageEnabled moved into the FlowWorks class;
# escapeEnabled and pitCellExposureEnabled died with the building pit (their chains are deleted).
FW_TOGGLES = [
    "depthEngineEnabled", "digToDepthEnabled", "machineDigEnabled",   # machineDig: DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (owed)
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
    "pitDepthDrawOffsetEnabled",  # PIT_DEPTH_DRAW_OFFSET_1: toggle_pit_depth_draw existed, the name was missing here
    "canalFireEnabled",          # FLOWWORKS_BUILD_PROGRAM_1 Phase 6
    "pitDrowningEnabled", "poisonFillEnabled",   # PIT_FILL_EFFECTS_1
    "viscosityEnabled",          # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (2026-10-05)
    # 2026-10-05 build pass (belt_fwbuild): chains fire_explosion/fire_foam/fire_rain, pit_prison_room, liquid_pump, bottle_revert,
    # wall_faces, dig_finds
    "explosionIgnitesLiquidEnabled", "foamSmothersLiquidFireEnabled", "rainDousesLiquidFireEnabled",
    "superdeepRoomsEnabled", "captureDownEnabled", "wardenFromLipEnabled",
    "liquidPumpEnabled", "bottleRevertEnabled", "excavationWallFacesEnabled",
    "digFindsEnabled", "digFindsLocalOnly", "digFindLetterEnabled",
    "liquidHeatPushEnabled",     # LIQUID_HEAT_PUSH_1 (2026-10-08): chain liquid_heat (DRAFT)
    "chemfuelInfernoEnabled", "astrofuelDetonationEnabled",   # CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: chain fuel_moat
    "slimeSlipEnabled",          # SLIME_CROSSING_BUILD_SLIPPERY_SLOPE: chain slime_slip
]
PITS_TOGGLES = ["trapTriggerEnabled", "fallDamageEnabled"]
RIVER_TOGGLES = ["riverSteamEnabled"]
S_MACH = "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings"
MACH_TOGGLES = ["universalPipesEnabled", "liquidWorksRuinsEnabled", "liquidWorksRuinStockEnabled",
                "industrialWorksBuildAnywhere", "pipeAdaptersEnabled"]       # liquid machinery pass (3e473f37c)
suite.toggles = FW_TOGGLES + PITS_TOGGLES + RIVER_TOGGLES + MACH_TOGGLES

# hose port step 4 (G5.10): owning class and shipped default of every toggle come from the ONE typed registry
# (settings_registry.py, built from site_spec.SETTINGS + the C# Scribe keys), not from a hand table here
import settings_registry as REG  # noqa: E402
DEFAULTS = REG.defaults(suite.toggles)
SETTINGS_OF = REG.settings_of(suite.toggles)

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
    _sweep_earlier_chains(t)
    x0, z0 = _plot(t, key)
    b = 8
    r = _rect(x0 - b, z0 - b, PW + 2 * b, PH + 2 * b)
    # Excavation is ENGINE state, not a Thing or terrain: destroy_batch + Soil leave an earlier chain's (or an earlier
    # run's, on the same map) cuts in place (MEASURED 2026-10-06: three chains FAILed on a re-used map). Fill them in.
    rs = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                       args="%d;%d;%d;%d" % (x0 - b, z0 - b, PW + 2 * b, PH + 2 * b))
    res = str((rs or {}).get("result", ""))
    if t._guard() and not (res.startswith("RESET") and res.endswith("left=0")):
        raise ExpectationFailed("plot %s excavation reset failed: %s" % (key, res or rs))
    t.bridge_call("jawa/destroy_batch", rects=r, categories="All")
    _stage(t, "jawa/set_terrain_batch", ops="%s:%s" % (terrain, r))
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/clear_ui")
    return x0, z0


def _stage(t, tool, **kw):
    """A fixture-staging bridge call (spawn / build / designate / paint) whose refusal is UNMEASURED. An unchecked staging
    call made every 'cover gone', 'not held', 'D=1 held' and 'nothing wet' check below it pass vacuously on a plot that
    was never built. Only an explicit success=False (or no reply while the guard is up) counts as a refusal."""
    r = t.bridge_call(tool, **kw)
    if t._guard() and (not isinstance(r, dict) or r.get("success") is False):
        raise ExpectationFailed("UNMEASURED: staging %s was refused, so the plot under test does not exist: %r"
                                % (tool, str(r)[:200]))
    return r


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


def _expect_body_fluid(t, x, z, fluid):
    """The natural body at (x,z) is a FRESH body of `fluid`. Since LIQUID_BODY_FLUID_IDENTITY_1 a body takes its fluid
    from its own terrain (RM_LiquidStock.FormBody: RM_FluidIdentity.FluidOfTerrain), never from the map's ActiveFluid,
    so a tar/slime plot paints that liquid's terrain and needs no ActiveFluid switch.
    RULED OUT (2026-10-11 live, EXT_FLUID_SET_REPAIR_ASKED_TOO_LATE): setting ActiveFluid first --
    `jawa/flowworks_set_active_fluid` refuses once any body is classified, which on a shared map is always (the golden
    site classifies 4 at prep), so plot_C2 and plot_F FAILed at *_fluid_set on every full run.
    Classifies via flowworks_body_report (sticky, ruling 16): a body that did not form on this call is an earlier
    chain's or run's, so its fluid says nothing about this plot -> UNMEASURED."""
    if not t._guard():
        return
    r = t.bridge_call("jawa/flowworks_body_report", x=x, z=z, classify=True) or {}
    body = r.get("body") or {}
    if not r.get("success") or not r.get("classified") or body.get("id") is None:
        raise ExpectationFailed("UNMEASURED: no body classified at (%d,%d): %r" % (x, z, r))
    if not r.get("formedByThisCall"):
        raise ExpectationFailed("UNMEASURED: the body at (%d,%d) was classified before this plot (sticky): %r" % (x, z, body))
    c = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FluidIdentityProof", method="ProofCensus")
    census = str((c or {}).get("result", ""))
    if "| bodies [" not in census:
        raise ExpectationFailed("UNMEASURED: fluid census did not answer: %r" % (c,))
    got = dict(e.split(":", 1) for e in census.rsplit("| bodies [", 1)[1].rstrip("]").split(",") if ":" in e)
    _expect(got.get(str(body["id"])) == fluid, "body %s at (%d,%d) is %r, expected %s" % (
        body["id"], x, z, got.get(str(body["id"])), fluid))


def _line(x0, z, n):
    return [(x0 + i, z) for i in range(n)]


def _dig_run(t, cells, levels):
    for x, z in cells:
        _dig(t, x, z, levels)


def _expect(cond, msg):
    """None = the offline declaration probe (`... if t._guard() else None`): nothing to check. Any other FALSY value
    fails: `cond is False` alone let an empty list (list_things found nothing) PASS four placement checks."""
    if cond is not None and not cond:
        raise ExpectationFailed(msg)


@contextmanager
def _owed(t, name, why):
    """A component with NO predicate yet: it records UNMEASURED ("owed: <why>"), never PASS, and declares no `toggle=`,
    so the toggle floor does not count it as coverage (an owed toggle is named in validation.py
    EXTENSION_TOGGLES_OWED). The chain carries on: the guard is restored after the block."""
    was, reason = t.upstream_failed, t.upstream_reason
    with t.component(name):
        if t._guard():
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: owed, no predicate yet: %s" % why
        yield
    t.upstream_failed, t.upstream_reason = was, reason


@contextmanager
def _unmeasured_if(t, why, name, **kw):
    """A REAL component (it keeps its toggle=/beyond_toggle= declaration) that this map cannot measure: with `why` set
    it records UNMEASURED ("not on this map: <why>") and the chain carries on, guard restored, like `_owed`; with `why`
    None it is an ordinary component."""
    if why is None:
        with t.component(name, **kw):
            yield
        return
    was, reason = t.upstream_failed, t.upstream_reason
    with t.component(name, **kw):
        if t._guard():
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: not on this map: %s" % why
        yield
    t.upstream_failed, t.upstream_reason = was, reason


def _def_field(r, field):
    """One field of the FIRST def in a jawa/get_defs reply, as the tool typed it; None when absent."""
    return (((r or {}).get("defs") or [{}])[0].get("fields") or {}).get(field)


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


def _expect_dry_ring(t, cells, skip=()):
    """Cannot-show scan: every un-dug cell in the 1-cell ring has D=0 and F=0. `skip`: the painted source the run
    is fed from (natural liquid reads D=4 F=4 by design, and the mouth's ring touches it)."""
    if not t._guard():
        return
    ring = [c for c in _ring(cells) if c not in set(skip)]
    bad = [(c, d, f) for c, (d, f) in zip(ring, _state(t, ring)) if d or f]
    if bad:
        raise ExpectationFailed("liquid/excavation on un-dug ground beside the run: %s" % bad[:5])


RESTORE_FAILED = []     # [(field, why)]: a setting a `finally` could not put back (it would leak into every later chain)


def _restore(t, typ, field, default):
    """Put a flipped setting back. Never raises (it runs in `finally`), but a refusal or an exception is PRINTED and kept in
    RESTORE_FAILED, not swallowed: a setting left flipped corrupts every later chain (MEASURED 2026-10-06)."""
    if getattr(t, "session", None) is None:      # the offline declaration probe: nothing was flipped
        return
    try:
        r = t.session.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(default))
        bad = None if isinstance(r, dict) and r.get("success") is not False else "refused: %r" % (r,)
    except Exception as e:  # noqa: BLE001
        bad = "raised %r" % (e,)
    if bad:
        RESTORE_FAILED.append((field, bad))
        print("SETTING NOT RESTORED: %s %s -- later chains run with it flipped" % (field, bad))


@contextmanager
def _setting(t, field, value):
    """Flip one Mod Settings field for the duration of a block, restore the shipped default in finally."""
    typ = SETTINGS_OF[field]
    t.set_setting(typ, {field: value})
    try:
        yield
    finally:
        # NOT t.set_setting: it is a no-op once the chain's guard is down, so a component that FAILED inside this block
        # left the setting flipped for every later chain (MEASURED 2026-10-06: superdeepCaptureEnabled stuck False ->
        # capture-down "NotHeld", sluice "held=False", pit occupants walking out: four FAILs in other chains).
        _restore(t, typ, field, DEFAULTS[field])


@contextmanager
def _setting_in(t, typ, field, value):
    """_setting for ANY registry switch (not only suite.toggles): flip it for the block, restore its shipped default."""
    t.set_setting(typ, {field: value})
    try:
        yield
    finally:
        _restore(t, typ, field, REG.BY_KEY[field]["default"])


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


_SPAWNED = []      # (chain token, pawn id): what each chain spawned, vanished when the NEXT chain starts
_TOKENS = [0]


def _chain_token(t):
    """A per-TestContext token (not id(t): a collected context's id is reused by the next one)."""
    tok = getattr(t, "_ext_chain_token", None)
    if tok is None:
        _TOKENS[0] += 1
        tok = _TOKENS[0]
        try:
            t._ext_chain_token = tok
        except AttributeError:
            pass
    return tok


def _sweep_earlier_chains(t):
    """Vanish every pawn an EARLIER chain spawned (no death, no corpse). MEASURED 2026-10-06 (B batch, 29 chains): a
    chain's leftover colonists wandered into later chains' pits and read as colonist_damaged "Blunt by nobody" (the
    mod's own fall damage), frostbite at night and fist fights with leftover prisoners -- 35 components UNMEASURED,
    0 FAIL. The bland map's restore heals injuries; it does not remove the pawns that keep collecting them."""
    keep = []
    for owner, pid in _SPAWNED:
        if owner == _chain_token(t):
            keep.append((owner, pid))
        elif pid:
            t.bridge_call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
    _SPAWNED[:] = keep


def _spawn_pawn_at(t, kind, x, z, faction="player"):
    _sweep_earlier_chains(t)
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    row = ((r or {}).get("pawns") or [{}])[0]
    _SPAWNED.append((_chain_token(t), row.get("id")))
    if t._guard() and not row.get("id"):
        # a pawn that never spawned makes every `is not True` / "cover intact" check below pass vacuously
        raise ExpectationFailed("UNMEASURED: spawn_pawn %s at (%d,%d) returned no id: %r" % (kind, x, z, r))
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


def _march(t, pid, x, z, ticks=300):
    t.bridge_call("jawa/order_pawn", pawnId=pid, x=x, z=z)
    t.wait_ticks(ticks)


FLYER_LAND_TICKS = 180     # validation_v2.FLYER_LAND_TICKS: a short vanilla PawnFlyer hop lands well inside this


def _force_into(t, pid, x, z):
    """FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner, 2026-10-06): "You can't fall in by careless colonist pathing. Only if
    they get blown/forced in do they fall. Enemies can fall if the pit is concealed or they are forced/blown in."
    RM_PitPathing refuses a walk into an OPEN ladderless D=4 cell, so a pawn is put INTO an open pit only by force:
    RM_PromotionProofs.ProofForcedFlyer throws it (vanilla PawnFlyer_Stun; an unstunned PawnFlyer is a jump and lands
    safely by pitJumpLandsSafe) onto (x,z), the landing running through
    PawnFlyer.RespawnPawn -> RM_Patch_PawnFlyer_LandInPit (validation_v2 P3f's route). A launch that did not happen
    is UNMEASURED, never a capture verdict.
    RULED OUT (2026-10-11 live, PIT_CHAINS_REPAIR_STALE_SINCE_RULING): `_march` into an uncovered pit -- the path veto
    (790fd4e8d) keeps every walker out, so pit_captures_hostile read 0/3 and two toggle chains FAILed on the ruling."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofForcedFlyer",
                      args="%s,%d,%d" % (pid, x, z))
    res = str((r or {}).get("result", ""))
    if t._guard() and ("launched=True" not in res.split() or "def=PawnFlyer_Stun" not in res.split()):
        raise ExpectationFailed("UNMEASURED: ProofForcedFlyer did not throw %s onto (%d,%d) (stale DLL? want def=PawnFlyer_Stun): %s"
                                % (pid, x, z, res or r))
    t.wait_ticks(FLYER_LAND_TICKS)
    return res


def _limitless_source(t, key, w=10, h=6, terrain="WaterDeep"):
    """Paint a deep-liquid strip at the plot's west edge BEFORE any excavation touches it
    (classification happens once on first contact). `terrain` names the liquid (the body's fluid is its terrain's).
    Mid-map, so the body is LIMITED (~5 units/cell), never limitless: limitless needs map-edge contact (ruling 16)."""
    x0, z0 = _plot(t, key)
    _stage(t, "jawa/set_terrain_batch", ops="%s:%s" % (terrain, _rect(x0, z0 + 4, w, h)))
    return x0, z0


def _limited_pond(t, key, size=5, terrain="WaterShallow", dz=4):
    """A size x size pond at (x0+3, z0+dz). A pond's body stays classified for the life of the map (ruling 16; the
    plot reset resets excavation, not bodies), so two chains that pond the SAME cells share one body: give each
    pond its own rows (`dz`) WITH A DRY ROW BETWEEN PONDS -- classification joins any 8-adjacent cell of an earlier
    body, even one repainted Soil -- and gate on `_expect_fresh_pond`."""
    x0, z0 = _plot(t, key)
    px, pz = x0 + 3, z0 + dz
    _stage(t, "jawa/set_terrain_batch", ops="%s:%s" % (terrain, _rect(px, pz, size, size)))
    return px, pz


def _expect_fresh_pond(t, px, pz, size=5):
    """Classify the pond NOW and require a body formed by this call (not an earlier chain's sticky one); UNMEASURED
    otherwise -- an inherited, drained body made toggle_recession watch a draw that could not happen."""
    if not t._guard():
        return {}
    r = t.bridge_call("jawa/flowworks_body_report", x=px + size // 2, z=pz + size // 2, classify=True) or {}
    if not r.get("formedByThisCall"):
        raise ExpectationFailed("UNMEASURED: the pond at (%d,%d) is an earlier body (sticky), not this chain's: %r"
                                % (px, pz, r))
    return r


def _fill_fluid(t, x, z, f, fluid):
    """Fill an excavated cell with a NAMED fluid (LIQUID_BODY_FLUID_IDENTITY_1 step 3); refuses another fluid's cell."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FluidIdentityProof",
                      method="ProofFillWithFluid", args="%d,%d,%d,%s" % (x, z, f, fluid))
    res = str((r or {}).get("result", ""))
    if t._guard() and not res.startswith("FILLED"):
        raise ExpectationFailed("fill %s (%d,%d,F=%d) failed: %s" % (fluid, x, z, f, res or r))
    return res


def _light(t, x, z):
    """Phase 6: light a liquid cell through RM_LiquidFire directly. "LIT ..." when it took. (A vanilla Fire next to a
    flammable fill does the same via the Fire.SpawnSetup hook, but `jawa/map_fire` cannot start one on bare canal fill
    terrain: it has no Flammability -- see plot_E_fire's RULED OUT.)"""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_LiquidFireProof",
                      method="ProofIgnite", args="%d,%d" % (x, z))
    return str((r or {}).get("result", ""))


FLAME = "RM_LiquidFlame"   # Phase 6: the burning-liquid flame; vanilla "Fire" dies on liquid terrain (no fuel)


def _channel_from(x0, z, n):
    """A 1xn run starting at x0 (the mouth)."""
    return _line(x0, z, n)


TAR_TICKS_PER_TILE = 360   # RM_Fluid_Tar's FluidDef.ticksPerTile (validation_v2 X7: stride 6 PROVISIONAL = 360/60)


def _pulses_for_one_move(ticks_per_tile, floor=3):
    """Pulses a window needs so a donor of this fluid gives at least once. Mirrors RM_StockMath.ViscosityStride: a
    viscous fluid gives only on pulses whose count is a multiple of its stride (tar 6), so a 3-pulse window holds a
    giving pulse only half the time -- the 2026-10-11 tar_front_lags_water 0/10 FAIL proved nothing about the mod."""
    stride = 1 if ticks_per_tile <= 60 else max(1, (ticks_per_tile + 30) // 60)
    return max(floor, stride)


def _engine(t):
    """jawa/flowworks_engine_state (read-only): depthEngineEnabled, nextPulseTick, pulseIntervalTicks. {} offline."""
    if not t._guard():
        return {}
    return t.bridge_call("jawa/flowworks_engine_state") or {}


def _body_stock(t, x, z):
    """The stock of the body behind source cell (x,z), never forming one (classify=False). None = no reading."""
    if not t._guard():
        return None
    r = t.bridge_call("jawa/flowworks_body_report", x=x, z=z, classify=False) or {}
    st = (r.get("body") or {}).get("stock")
    return float(st) if r.get("success") and st is not None else None


def _source_feed_verdict(e0, e1, stock0, stock1, wet):
    """CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY: decide a dry mouth beside a stocked source from readings, not a guess.
    e0/e1 = jawa/flowworks_engine_state before/after the window; stock0/1 = the source body's stock; wet = the mouth
    (or channel) took liquid. Returns (verdict, why): "PASS", "UNMEASURED" (no pulse ran: not the feed's fault -- an
    engine left off by an earlier chain, or a nextPulseTick stranded ahead of the clock), or "FAIL" (pulses ran and
    the source still did not feed: the mod's source-feed path, with the numbers)."""
    if wet:
        return "PASS", ""
    if not e0.get("success") or not e1.get("success"):
        return "UNMEASURED", "engine_state unreadable (%r / %r): cannot tell a stalled engine from a dead feed" % (e0, e1)
    if not e0.get("depthEngineEnabled") or not e1.get("depthEngineEnabled"):
        return "UNMEASURED", ("depth engine OFF across the window (before %s, after %s): a setting leaked from an earlier "
                              "chain, nothing could pour" % (e0.get("depthEngineEnabled"), e1.get("depthEngineEnabled")))
    n0, n1 = e0.get("nextPulseTick"), e1.get("nextPulseTick")
    step = e1.get("pulseIntervalTicks") or 0
    if n0 is None or n1 is None or n1 == n0:
        return "UNMEASURED", ("no pulse fired in the window: nextPulseTick %s -> %s (tick %s -> %s); the schedule, not "
                              "the feed" % (n0, n1, e0.get("ticksGame"), e1.get("ticksGame")))
    fired = (n1 - n0) // step if step and n0 >= 0 else "?"
    moved = "" if stock0 is None or stock1 is None else (
        "; source stock %s -> %s (%s)" % (stock0, stock1,
                                          "debited, yet the channel is dry: the liquid went elsewhere" if stock1 < stock0
                                          else "never debited: the source refused every pulse"))
    return "FAIL", "~%s pulse(s) fired (nextPulseTick %s -> %s, engine on) and the channel stayed dry%s" % (
        fired, n0, n1, moved)


def _expect_source_fed(t, e0, stock0, src_xz, wet, what):
    """Raise per _source_feed_verdict (UNMEASURED prefix for a stalled engine); no-op offline or when wet."""
    if not t._guard() or wet:
        return
    verdict, why = _source_feed_verdict(e0, _engine(t), stock0, _body_stock(t, *src_xz), wet)
    if verdict == "UNMEASURED":
        raise ExpectationFailed("UNMEASURED: %s: %s" % (what, why))
    if verdict == "FAIL":
        raise ExpectationFailed("%s: %s" % (what, why))


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
            _expect((r or {}).get("terrain") == "RM_Channel_Empty", "terrain at the dug cell is not RM_Channel_Empty: %r" % r)
        _frame(t, cells[0][0], z, 8, 1)
    with t.component("canal_dry_obstacle_look", shows=["canal_dry_reads_as_obstacle"]):
        # ruled pathCost 30 for a dry D=1 cell (build program Phase 5, ruling 17)
        r = t.bridge_call("jawa/get_defs", defs="TerrainDef/RM_Channel_Empty")
        if t._guard():
            # the def's own pathCost field, as a number: a substring probe over the whole reply also matched 300-309
            # and any other 30 in the dump
            pc = _def_field(r, "pathCost")
            _expect(pc == 30, "RM_Channel_Empty pathCost is %r, not the ruled 30: %s" % (pc, str(r)[:300]))
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
    """Plot C: a 1x10 D=1 channel dug from a painted (limited, mid-map) deep-water body, engine running."""
    x0, z0 = _prep_plot(t, "C")
    _limitless_source(t, "C")
    z = z0 + 6
    cells = _channel_from(x0 + 10, z, 10)
    shot_rect = (x0, z0 + 2, 22, 10)
    with t.component("canal_digs_from_source"):
        _dig_run(t, cells, 1)
        _expect_state(t, cells, depth=1, what="channel")
    with t.component("canal_fill_front", shows=["canal_fill_front_watchable"]):
        # 2026-10-11 live (EXT_LIQUID_REDS_HUNT_FIVE_AT_ONCE): mouth F=0 after 3 pulses with NO reading of the source,
        # so MOD and SITE could not be told apart. The strip is mid-map, so its body is LIMITED (ruling 16 needs edge
        # contact), not limitless as this chain was named for -- but a 60-cell body still holds ~300. Read it first:
        # a source that is not a source, or holds nothing, is UNMEASURED/SITE; a stocked source the mouth never drew
        # from is the mod's source-feed path (FAIL, with the stock in the message).
        # The engine state and the stock are read either side of the window: _source_feed_verdict tells a stalled
        # schedule (UNMEASURED) from a source that never fed (FAIL).
        src, stock0, e0 = {}, None, {}
        if t._guard():
            src = t.bridge_call("jawa/flowworks_body_report", x=x0 + 9, z=z, classify=True) or {}
            stock0 = (src.get("body") or {}).get("stock")
            if not src.get("success") or not src.get("isSourceCell") or stock0 is None or stock0 <= 0:
                raise ExpectationFailed("UNMEASURED: the painted source at (%d,%d) is not a stocked source: %r"
                                        % (x0 + 9, z, src))
            e0 = _engine(t)
        _wait(t, PULSE)
        p1 = _frame(t, *shot_rect, name="C_pulse1")
        _wait(t, 2 * PULSE)
        p3 = _frame(t, *shot_rect, name="C_pulse3")
        _diptych(t, p1, p3, "C_fill_front")
        if t._guard():
            # CANAL_FRONT_FIX_WRONG_END_WETS_FIRST (owner 2026-10-12, by card): the wet front must advance outward from the
            # mouth like a flood front. Water used to race the whole run in one pulse and wet the far end first (the old
            # accept-far-end-first bar is reverted). Kernel: creepWaterEnabled, one cell per pulse. Bar: the mouth is wet,
            # the front has not run past ~one cell per pulse (3 pulses, +1 slack for window jitter), and every level the
            # body paid is in the channel.
            fs = [f or 0 for _, f in _state(t, cells)]
            wet = (fs[0] if fs else 0) >= 1
            _expect_source_fed(t, e0, stock0, (x0 + 9, z), wet, "mouth cell F<1 after 3 pulses from a stocked source")
            far = max([i for i, f in enumerate(fs) if f >= 1], default=-1)
            _expect(far <= 3, "wet front ran %d cells from the mouth in 3 pulses (cap 3 + 1 slack): far end wetted first? %s"
                    % (far, fs))
            stock1 = _body_stock(t, x0 + 9, z)
            if stock0 is not None and stock1 is not None:
                # the body pays 1 unit per level (water); refill after the first debit adds a fraction (< 1 in 3 pulses)
                _expect(abs((stock0 - stock1) - sum(fs)) < 1.0,
                        "source paid %.3f but the channel holds %d levels %s: a debit that landed nowhere"
                        % (stock0 - stock1, sum(fs), fs))
    with t.component("canal_fill_spreads", shows=["canal_fill_spreads_along_itself"]):
        _settle(t, cells, budget_pulses=20)
        if t._guard():
            fs = [f for _, f in _state(t, cells)]
            _expect(all((f or 0) >= 1 for f in fs), "channel has a dry gap or dry cell after settle: %s" % fs)
        _frame(t, *shot_rect)
    with t.component("canal_holds_only_channel",
                     shows=["canal_holds_only_the_channel", "never_liquid_on_open_ground"]):
        # the mouth's ring touches the painted source strip (x0..x0+9, z0+4..z0+9), which reads D=4 F=4 by design
        _expect_dry_ring(t, cells, skip=[(x0 + 9, z + dz) for dz in (-1, 0, 1)])
        _frame(t, *shot_rect)
    with t.component("canal_same_liquid_look", shows=["canal_reads_as_same_liquid_as_reservoir"]):
        _frame(t, x0, z0 + 2, 22, 10)


@suite.chain("plot_C2_tar_and_fluids")
def plot_C2_tar_and_fluids(t):
    """Tar vs water fill front (FluidDef.ticksPerTile: tar 360 vs water 60), and the two-fluids-side-by-side
    bar (fluid identity is per cell via ProofFillWithFluid, so one map holds both)."""
    x0, z0 = _prep_plot(t, "T")
    _plot_C2_body(t, x0, z0)


def _expect_tar_lag(t, cells):
    """State delta: tar's wet front at pulse 3 is strictly shorter than water's (water front = full run today) AND
    non-empty: a channel that took no liquid at all (wet 0) used to PASS as "viscosity lag"."""
    if not t._guard():
        return
    wet = sum(1 for _, f in _state(t, cells) if (f or 0) >= 1)
    _expect(wet >= 1, "tar channel took no liquid at all: no front to compare (%d/%d wet)" % (wet, len(cells)))
    _expect(wet < len(cells), "tar wet front reached all %d cells: no viscosity lag" % len(cells))


def _plot_C2_body(t, x0, z0):
    # The source is TAR terrain, so its body is tar (per-body fluid identity); read back before the channel is dug.
    _limitless_source(t, "T", terrain="RM_TarDeep")
    with t.component("tar_fluid_set"):
        _expect_body_fluid(t, x0 + 9, z0 + 6, TAR)
    cells = _channel_from(x0 + 10, z0 + 6, 10)
    _dig_run(t, cells, 1)
    with t.component("tar_front_lags_water", toggle="viscosityEnabled", shows=["tar_fill_front_lags_water"]):
        # One full viscosity stride (6 pulses for tar), not 3: tar gives only on every 6th pulse, so 3 pulses held a
        # giving pulse half the time and "0/10 wet" was a coin toss (validation_v2 X7 accepts tar 0 at pulse 3).
        e0 = _engine(t)
        stock0 = _body_stock(t, x0 + 9, z0 + 6)
        _wait(t, PULSE)
        p1 = _frame(t, x0, z0 + 2, 22, 10, "T_pulse1")
        _wait(t, (_pulses_for_one_move(TAR_TICKS_PER_TILE) - 1) * PULSE)
        p3 = _frame(t, x0, z0 + 2, 22, 10, "T_pulse3")
        _diptych(t, p1, p3, "T_tar_front")
        if t._guard():
            wet = any((f or 0) >= 1 for _, f in _state(t, cells))
            _expect_source_fed(t, e0, stock0, (x0 + 9, z0 + 6), wet,
                               "tar channel took no liquid in one full viscosity stride")
        _expect_tar_lag(t, cells)
    with t.component("two_fluids_side_by_side", shows=["fill_fluid_distinct"]):
        # Per-body fluid identity is built (RM_FluidIdentity / ProofFillWithFluid names the fluid per
        # cell), so two fluids share one map: a tar run and a water run, dug side by side and filled
        # to the same tier, and the frame shows they read differently.
        tar_run = _line(x0 + 4, z0 + 0, 6)      # both runs SOUTH of the tar strip (z0+4..z0+9), never on it
        water_run = _line(x0 + 4, z0 + 2, 6)
        _dig_run(t, tar_run + water_run, 1)
        for x, z in tar_run:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Tar")
        for x, z in water_run:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Water")
        _frame(t, x0 + 4, z0, 6, 3)


@suite.chain("plot_D_limited_pond")
def plot_D_limited_pond(t):
    """Plot D: a limited 5x5 pond drawn down through a 1x12 D=3 channel; then recharge."""
    x0, z0 = _prep_plot(t, "D")
    _plot_D_body(t, x0, z0)


POND_FRACTION = 0.2   # the pond is staged at a fifth of its capacity (the deleted budget slider's old job)


def _pond_stock(t, px, pz, size=5):
    """The pond body's stock read at its centre (classify=False: never forms a body), or raise UNMEASURED."""
    cx, cz = px + size // 2, pz + size // 2
    r = t.bridge_call("jawa/flowworks_body_report", x=cx, z=cz, classify=False) or {}
    st = (r.get("body") or {}).get("stock")
    if not r.get("success") or st is None:
        raise ExpectationFailed("UNMEASURED: no pond body at (%d,%d) to read: %r" % (cx, cz, r))
    return float(st)


def _plot_D_body(t, x0, z0):
    px, pz = _limited_pond(t, "D", dz=10)    # rows 10-14: toggle_recession ponds rows 4-8 and 0-2; rows 3 and 9 stay dry
    z = pz + 2
    cells = _channel_from(px + 5, z, 12)
    shot = (px - 1, pz - 1, 18, 8)
    box = {}
    with t.component("pond_before_draw"):
        # a SMALL pond: 25 cells x at most 4 notches = 100 notches at capacity, staged at 0.2 of it = 20 or less < the 36 the
        # D=3 channel holds, so the draw really empties it. LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD deleted the pond budget slider
        # that used to size it (D4): the pond is classified at the shipped settings, then its stock is SET to 0.2 of capacity
        # by RM_NorthstarProofs.ProofSetBodyFraction. A body that did not form on this call is sticky from an earlier run on
        # this map: UNMEASURED.
        if t._guard():
            r = t.bridge_call("jawa/flowworks_body_report", x=px + 2, z=pz + 2, classify=True) or {}
            if not r.get("formedByThisCall") or (r.get("body") or {}).get("limitless") is not False:
                raise ExpectationFailed("UNMEASURED: the pond did not form fresh and limited: %r" % (r,))
            rs = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofSetBodyFraction",
                               args="%d;%d;%s" % (px + 2, pz + 2, POND_FRACTION))
            res = str((rs or {}).get("result", ""))
            if not res.startswith("SET"):
                raise ExpectationFailed("UNMEASURED: could not stage the pond at %s of capacity: %s" % (POND_FRACTION, res or rs))
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
        # RULED OUT (2026-10-11 live, EXT_LIQUID_REDS_HUNT_FIVE_AT_ONCE): a "no-op re-dig" with deepenLevels=3 -- the
        # drive ADDS levels, so it cut D=3 -> D=4 and the still-stocked 125-unit pond fed the new room: tail [4,4,4]
        # read as "fed with the pond empty". Now: read the pond's stock, require it EMPTY, then the channel's total
        # must not rise over 10 quiet pulses (no source, no refill).
        with _setting(t, "refillEnabled", False):
            if t._guard():
                st0 = _pond_stock(t, px, pz)
                # EMPTY = below one unit: a debit needs a whole unit (RM_StockMath.CanDebit), and trickle refill during
                # the draw leaves a drawn-down pond at a fraction, never exactly 0
                if st0 >= 1.0:
                    raise ExpectationFailed("UNMEASURED: the pond is not empty after the draw (stock %.2f)" % st0)
                f0 = sum(f or 0 for _, f in _state(t, cells))
            _wait(t, 10 * PULSE)
            if t._guard():
                f1 = sum(f or 0 for _, f in _state(t, cells))
                st1 = _pond_stock(t, px, pz)
                _expect(f1 <= f0 and st1 < 1.0, "the channel still gained liquid from an empty pond: F total %d -> %d, "
                        "stock %.2f -> %.2f" % (f0, f1, st0, st1))
            _frame(t, *shot)
    with t.component("pond_recharge_visible", toggle="refillEnabled",
                     shows=["reservoir_recharge_progress_visible"]):
        # the STATE half (2026-10-11 review: this claimed refillEnabled with frames only): pond stock + channel fill
        # must rise. The SUM, not the stock alone: once refill lifts the stock past one unit the still-thirsty channel
        # may debit it (CanDebit), moving a unit from stock to fill, so stock alone can fall while refill works. The
        # frames stay for the look; under budget 0.2 a restored shore cell needs stock >= 2, so the picture may
        # legitimately show little -- the judge reads the frame, this reads the liquid.
        if t._guard():
            a = _pond_stock(t, px, pz) + sum(f or 0 for _, f in _state(t, cells))
        s0 = _frame(t, *shot, name="D_recharge0")
        _wait(t, 20 * PULSE)
        s1 = _frame(t, *shot, name="D_recharge1")
        _diptych(t, s0, s1, "D_recharge")
        if t._guard():
            b = _pond_stock(t, px, pz) + sum(f or 0 for _, f in _state(t, cells))
            _expect(b > a, "the drained pond did not recharge with refill ON (stock + channel F %.3f -> %.3f)" % (a, b))


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
        # RULED OUT (2026-10-11 live, fire_reaches_reservoir): _ignite (vanilla FireUtility.TryStartFireIn) on a tar
        # channel -- canal fill terrain has no Flammability and _prep_plot cleared every thing, so no vanilla Fire
        # spawned, the Fire.SpawnSetup hook never ran and the run was never lit (0 flames anywhere). _light goes
        # through RM_LiquidFire directly, as toggle_canal_fire does.
        lit = _light(t, *cells[-1])
        _wait(t, 5 * PULSE)
        # fire_burning_look / fire_persists_look / burned_channel_spent were CUT 2026-10-05: core row X10_canal_fire
        # fails whenever they would (flames on the run, still alight, spent F=0 + ash) at 1/20th the ticks.
        with t.component("fire_reaches_reservoir", shows=["canal_fire_reaches_reservoir"]):
            if t._guard() and not lit.startswith("LIT"):
                raise ExpectationFailed("UNMEASURED: the tar run was never lit, so no front to follow: %s" % lit)
            _wait(t, 24 * PULSE)
            if t._guard():
                fires = t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(px, pz, 5, 5), limit=200)
                _expect(len((fires or {}).get("things") or []) >= 1, "no flame at the pond cells within budget")
            _frame(t, *shot)


@suite.chain("plot_F_slime")
def plot_F_slime(t):
    """Plot F: a 1x6 D=3 slime run, each cell filled with a NAMED fluid (ProofFillWithFluid, per-cell identity; no
    ActiveFluid switch -- see _expect_body_fluid's RULED OUT) and a colonist walked into the middle cell."""
    x0, z0 = _prep_plot(t, "F")
    _plot_F_body(t, x0, z0)


def _plot_F_body(t, x0, z0):
    cells = _line(x0 + 6, z0 + 6, 6)
    _dig_run(t, cells, 3)
    with _setting(t, "depthEngineEnabled", False):
        with t.component("slime_fluid_set"):
            for x, z in cells:
                res = _fill_fluid(t, x, z, 3, SLIME)
                if t._guard():
                    _expect(res.endswith("fluid=" + SLIME), "cell (%d,%d) did not take %s: %s" % (x, z, SLIME, res))
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
        # No exemption: RM_Ladder ships its own art since EXCAVATION_WALL_ART_1. A comment that merely
        # names the path is not a hit. Defs live beside northstar/, not inside it; the sanity probe
        # proves the walk saw the mod's defs, so an empty walk cannot pass.
        import xml.etree.ElementTree as ET
        ddir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Defs")
        hits, seen = [], set()
        for root, _, files in os.walk(ddir):
            for fn in files:
                if fn.endswith(".xml"):
                    for d in ET.parse(os.path.join(root, fn)).getroot():
                        seen.add(d.findtext("defName"))
                        tp = d.findtext("graphicData/texPath") or d.findtext("texturePath") or ""
                        if tp == "Things/Building/Security/TrapSpikeArmed":
                            hits.append(fn)
        _expect("RM_Channel_Superdeep" in seen and "RM_Spikes" in seen,
                "sanity probe: the def walk of %s did not see RM_Channel_Superdeep/RM_Spikes" % ddir)
        _expect(not hits, "defs still point at the vanilla TrapSpikeArmed art: %s" % sorted(set(hits)))
        _frame(t, *shot)
    with t.component("pit_captures_hostile", toggle="superdeepCaptureEnabled",
                     shows=["pit_occupant_below_floor", "pit_trapped_reads_as_trapped",
                            "pit_occupied_distinguishable", "never_snared_standing"]):
        caught = 0
        for i in range(3):       # traps ABSOLUTELY: 3/3 over distinct spawn points, forced onto distinct pit cells
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1] + i, faction="hostile")
            _force_into(t, pid, pit[3 + i][0], pit[3 + i][1])   # an open pit is entered only by force (ruling 10-06)
            if t._guard():
                caught += 1 if _pit_held(t, pid, pit) else 0
        _expect(caught == 3 if t._guard() else None, "superdeep captured %d/3 hostiles" % caught)
        _frame(t, *twin_shot)    # occupied pit beside the empty twin in one frame
    with t.component("pit_cover_invisible",
                     shows=["pit_covered_invisible", "pit_covered_seam_at_max_zoom"]):
        # PIT_COVER_FALL_REWIRE_1: a reinforced deck over the empty twin (nobody on it is heavy enough
        # to spring it), framed beside the open pit; the frame is the bar, the count is the guard.
        _stage(t, "jawa/spawn_batch", ops=";".join("RM_PitCover_ReinforcedFrame:%d,%d" % (x, z) for x, z in twin))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_ReinforcedFrame",
                              rect=_rect(twin[0][0] - 1, twin[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 9, "reinforced cover deck did not stand on all 9 twin cells: %r" % r)
        _frame(t, *twin_shot)
    with t.component("ladder_state_look", toggle="ladderRequiredToExitEnabled",
                     shows=["ladder_state_legible"]):
        _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (LADDER, pit[0][0] - 1, pit[0][1]))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName=LADDER, rect=_rect(pit[0][0] - 2, pit[0][1] - 1, 4, 3))
            _expect(bool((r or {}).get("things")), "RM_Ladder did not place beside the pit")
        _frame(t, *shot)
    with t.component("sluice_state_look", shows=["sluice_gate_state_legible"]):
        # FLOWWORKS_DOOR_FAMILY_1: a wooden sluice and a steel grate on the pit's west lip, framed.
        # Placeholder art (vanilla door mover) until the gate art lands; the frame is the bar.
        _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (SLUICE, pit[0][0] - 1, pit[0][1] + 1), stuff="WoodLog")
        _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (GRATE, pit[0][0] - 1, pit[0][1] + 2), stuff="Steel")
        if t._guard():
            for d in (SLUICE, GRATE):
                r = t.bridge_call("jawa/list_things", defName=d, rect=_rect(pit[0][0] - 2, pit[0][1] - 1, 3, 5))
                _expect(bool((r or {}).get("things")), "%s did not place on the pit lip" % d)
        _frame(t, *shot)
    with t.component("spikes_look", shows=["spikes_read_distinct"]):
        # CANAL_BOTTOM_SPIKES_1 built RM_Spikes (placeholder skullspike graphic until EXCAVATION_WALL_ART_1).
        _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (SPIKES, pit[4][0], pit[4][1]))
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName=SPIKES, rect=_rect(pit[4][0], pit[4][1], 1, 1))
            _expect(bool((r or {}).get("things")), "RM_Spikes did not place on the D=4 floor")
        _frame(t, *shot)


# =========================================================== TOGGLE COMPONENTS
# One component per Mod Settings toggle (plan section 2.5). ON = shipped default; OFF = flipped
# for that component and restored in `finally`. A component that only declares `toggle=` with no
# predicate is a floor cheat: a side with no predicate yet is an `_owed` component (UNMEASURED, no
# `toggle=`), and a toggle left with no predicate at all is named in validation.py EXTENSION_TOGGLES_OWED.
# Ticks are budgets.

def _order_fill_in(t, pid, cell):
    """Hand THIS colonist the fill-in at `cell` as a player order, after asking the mod's own WorkGiver whether it would.
    RULED OUT (2026-10-11 live, EXT_LIQUID_REDS_HUNT_FIVE_AT_ONCE fill_in_on): spawn a random colonist and wait for it to
    pick the designation up unprompted -- the job is Mining work (WorkGiver_FillInCanal), so a colonist incapable of or
    busy beyond Mining leaves D=1 and the row read as a mod FAIL with nothing read. A pawn that cannot do the work type
    is UNMEASURED; the WorkGiver refusing a designated cell with fill-in ON is the mod's own answer (FAIL)."""
    if not t._guard():
        return
    # forced=True: the order below is a player order, and HasJobOnCell passes `forced` to its reservation check
    pr = t.bridge_call("jawa/flowworks_job_probe", x=cell[0], z=cell[1], kind="fillin", pawnId=pid, forced=True) or {}
    wg, pw = pr.get("workGiver") or {}, pr.get("pawn") or {}
    if not pr.get("success") or not pw:
        raise ExpectationFailed("UNMEASURED: flowworks_job_probe gave no pawn reading for %s: %r" % (pid, pr))
    if pw.get("workTypeDisabled") or pw.get("missingCapacity") or pw.get("canReach") is False:
        raise ExpectationFailed("UNMEASURED: the spawned colonist cannot do the fill-in (%r)" % pw)
    if not wg.get("hasJobOnCell") or not wg.get("jobDef"):
        raise ExpectationFailed("WorkGiver_FillInCanal hands no job on designated cell %s with fillInEnabled ON: %r" % (cell, wg))
    o = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef=wg["jobDef"], targetAX=cell[0], targetAZ=cell[1], waitTicks=60) or {}
    if not o.get("accepted"):
        raise ExpectationFailed("UNMEASURED: the fill-in order was not taken (reservation?): %r" % o)


@suite.chain("toggle_fill_in")
def toggle_fill_in(t):
    x0, z0 = _prep_plot(t, "E")
    a, b = (x0 + 4, z0 + 6), (x0 + 6, z0 + 6)
    for c in (a, b):
        _dig(t, c[0], c[1], 1)
        _fill(t, c[0], c[1], 1)
    pid = None
    with t.component("fill_in_on", toggle="fillInEnabled"):
        _stage(t, "jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % a)
        pid = _spawn_pawn_at(t, "Colonist", a[0] - 2, a[1])     # registered in _SPAWNED: the next chain vanishes it
        _order_fill_in(t, pid, a)
        _wait(t, 10 * PULSE)
        _expect_state(t, [a], depth=0, what="filled-in cell")
    with t.component("fill_in_off", toggle="fillInEnabled"):
        with _setting(t, "fillInEnabled", False):
            _stage(t, "jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % b)
            if t._guard():
                # ask the mod with a pawn that CAN fill in (the ON side proved it): D=1 alone held with nobody trying
                if pid is None:
                    raise ExpectationFailed("UNMEASURED: the ON side spawned no colonist, so no pawn asked the WorkGiver with fill-in OFF")
                pr = t.bridge_call("jawa/flowworks_job_probe", x=b[0], z=b[1], kind="fillin", pawnId=pid, forced=True) or {}
                wg, pw = pr.get("workGiver") or {}, pr.get("pawn") or {}
                if not pr.get("success") or not pw or not wg:
                    raise ExpectationFailed("UNMEASURED: flowworks_job_probe gave no reading with fill-in OFF: %r" % pr)
                _expect(wg.get("shouldSkip") or not wg.get("hasJobOnCell"),
                        "WorkGiver_FillInCanal still hands a fill-in job with fillInEnabled OFF: %r" % wg)
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
        # a colonist must do the fill-in (_prep_plot vanished every earlier chain's pawn); the filled cell must reach
        # D=0 before the sums mean anything, and the sanctioned overflow (RM_MapComponent_Excavation.cs ~643-662,
        # counted in overflowDestroyedTotal) is added back, so a correct engine that overflows is not a FAIL
        pid = _spawn_pawn_at(t, "Colonist", cells[1][0], cells[1][1] - 2)
        r0 = [_rep(t, x, z) for x, z in cells] if t._guard() else []
        _stage(t, "jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % cells[1])
        _order_fill_in(t, pid, cells[1])
        _wait(t, 10 * PULSE)
        if t._guard():
            r1 = [_rep(t, x, z) for x, z in cells]
            if any(r.get("fill") is None or r.get("overflowDestroyedTotal") is None for r in r0 + r1):
                raise ExpectationFailed("UNMEASURED: excavation_report gave no fill/overflowDestroyedTotal: %r" % (r0 + r1,))
            if r1[1].get("depth") != 0:
                raise ExpectationFailed("UNMEASURED: the fill-in never happened (D=%r at %s), so nothing was displaced"
                                        % (r1[1].get("depth"), cells[1]))
            before = sum(r["fill"] for r in r0) + r0[0]["overflowDestroyedTotal"]
            after = sum(r["fill"] for r in r1) + r1[0]["overflowDestroyedTotal"]
            _expect(after >= before, "liquid was deleted, not displaced (F+overflow %s -> %s)" % (before, after))
    with _owed(t, "fill_in_displacement_off", "fillInDisplacementEnabled OFF: nothing reads where the displaced liquid went"):
        pass


@suite.chain("toggle_recession")
def toggle_recession(t):
    x0, z0 = _prep_plot(t, "D")
    px, pz = _limited_pond(t, "D")
    cells = _channel_from(px + 5, pz + 2, 12)
    with t.component("recession_on", toggle="recessionEnabled"):
        _expect_fresh_pond(t, px, pz)
        _dig_run(t, cells, 3)
        _wait(t, 40 * PULSE)
        far = _rep(t, px, pz) if t._guard() else {}
        _expect(not far.get("isSourceCell", True) if far else None, "no pond cell dried with recession ON")
    x0, z0 = _prep_plot(t, "D")
    # its OWN rows (0-2, a 3x3 pond): re-ponding recession_on's rect inherited that body, drawn down already, so the
    # OFF side's "still a source" read a freshly painted cell and could not fail
    px, pz = _limited_pond(t, "D", size=3, dz=0)
    cells = _channel_from(px + 3, pz + 1, 12)
    with t.component("recession_off", toggle="recessionEnabled"):
        cap = float(((_expect_fresh_pond(t, px, pz, size=3).get("body") or {}).get("capacity")) or 0)
        _dig_run(t, cells, 3)
        with _setting(t, "recessionEnabled", False):
            _wait(t, 40 * PULSE)
            if t._guard():
                # the OFF side means something only if the pond was really drawn down (9 cells ~45 into a 36-unit
                # channel): a feed that never ran would keep every cell a source and pass vacuously
                st = _pond_stock(t, px, pz, size=3)
                if not cap or st > cap / 2:
                    raise ExpectationFailed("UNMEASURED: the pond was not drawn down (stock %.2f of %.2f)" % (st, cap))
            far = _rep(t, px, pz) if t._guard() else {}
            _expect(far.get("isSourceCell", False) if far else None, "a pond cell dried with recession OFF")


@suite.chain("toggle_refill")
def toggle_refill(t):
    """Pond STOCK after a draw (jawa/flowworks_body_report): refill ON must raise it over 20 quiet pulses; OFF must not.
    RULED OUT (2026-10-11 review): counting source cells -- `b >= a` ON and `b == a` OFF both held on a pond that
    never changed, so neither side could tell refill from nothing. And the pond now has its own rows (dz=10): at
    dz=4 it re-used plot_E's tar pond cells and inherited that sticky body."""
    x0, z0 = _prep_plot(t, "E")
    px, pz = _limited_pond(t, "E", dz=10)      # plot_E's tar pond is rows 4-8; row 9 stays dry between them
    cells = _channel_from(px + 5, pz + 2, 6)
    with t.component("refill_on", toggle="refillEnabled"):
        body = (_expect_fresh_pond(t, px, pz).get("body") or {})
        _dig_run(t, cells, 1)
        _wait(t, 10 * PULSE)
        if t._guard():
            a = _pond_stock(t, px, pz)
            cap = float(body.get("capacity") or 0)
            if not cap or a >= cap:
                raise ExpectationFailed("UNMEASURED: the channel drew nothing from the pond (stock %.2f of %.2f)" % (a, cap))
        _wait(t, 20 * PULSE)
        if t._guard():
            b = _pond_stock(t, px, pz)
            _expect(b > a, "pond stock did not rise over 20 quiet pulses with refill ON (%.3f -> %.3f)" % (a, b))
    with t.component("refill_off", toggle="refillEnabled"):
        with _setting(t, "refillEnabled", False):
            if t._guard():
                a = _pond_stock(t, px, pz)
            _wait(t, 20 * PULSE)
            if t._guard():
                b = _pond_stock(t, px, pz)
                _expect(b <= a + 1e-6, "pond stock rose with refill OFF (%.3f -> %.3f)" % (a, b))


@suite.chain("toggle_liquid_ignition")
def toggle_liquid_ignition(t):
    x0, z0 = _prep_plot(t, "E")
    cells = _line(x0 + 4, z0 + 6, 6)
    _dig_run(t, cells, 1)
    for c in cells:
        _fill(t, c[0], c[1], 1)
    # Owed both sides (review 2026-10-11): the old OFF side filled with the map's WATER (not flammable) and counted
    # vanilla Fire, which dies on liquid terrain, so ON and OFF read the same. A real pair stages a flammable fill
    # (LiquidIgnition.cs ignites only props.flammable terrain beside a Fire) and counts RM_LiquidFlame.
    with _owed(t, "liquid_ignition_off", "liquidIgnitionEnabled OFF: water fill + vanilla Fire count cannot tell ON from OFF"):
        pass
    with _owed(t, "liquid_ignition_on", "liquidIgnitionEnabled ON: nothing reads the spread (the old block lit and waited)"):
        pass


@suite.chain("all_off_still_digs")
def all_off_still_digs(t):
    """FLOWWORKS_NORTHSTAR_SHIP_1 / MOD_OPTIONS ruling 2026-09-12: with EVERY FlowWorks toggle off the mod still
    digs dry channels. A D=1 run dug beside a pond stays D=1 and dry across pulses (no flow, no rain, no fire).
    EVERY toggle is the registry's all-off fixture (settings_registry.all_off(): every section's bool switch), not the
    50-name FW_TOGGLES + PITS_TOGGLES floor this chain used until the 2026-10-18 F2 settings audit, which left 100+
    switches (rivers, machinery, hose, thirst, trench cover, pit access, looks ...) ON during the "all off" check."""
    import contextlib
    x0, z0 = _prep_plot(t, "T")
    px, pz = _limited_pond(t, "T")
    cells = _channel_from(px + 5, pz + 2, 4)
    with contextlib.ExitStack() as stack:
        for cls, f, off in REG.all_off():
            stack.enter_context(_setting_in(t, cls, f, off))
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
            lit = _flames(t, cells)
            _expect(not lit if t._guard() else None, "flame with canalFireEnabled OFF: %s (%s)" % (sorted(lit), r))
    with t.component("canal_fire_on_lights", toggle="canalFireEnabled"):
        r = _light(t, *cells[0])
        if t._guard():
            _expect(r.startswith("LIT"), "ON: light refused: %s" % r)
            # the instrument the OFF side trusted must SEE a flame when there is one
            _expect(_flames(t, [cells[0]]) == {cells[0]}, "ON: lit %s but list_things shows no %s there" % (cells[0], FLAME))


@suite.chain("toggle_liquid_corrosion")
def toggle_liquid_corrosion(t):
    # Contract to read first: LiquidCorrosion.cs (which fluid, which targets). ON predicate = HP falls. Owed: the old
    # block built a wall beside a filled cell and only waited, with neither side read.
    with _owed(t, "liquid_corrosion_both_sides", "liquidCorrosionEnabled: no HP read on either side"):
        pass


@suite.chain("toggle_superdeep_capture")
def toggle_superdeep_capture(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("superdeep_capture_on", toggle="superdeepCaptureEnabled"):
        pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[0][1], faction="hostile")
        _force_into(t, pid, pit[4][0], pit[4][1])     # FLOWWORKS_PIT_FALL_ONLY_FORCED_1: walking in is refused
        if t._guard():
            _expect(_pit_held(t, pid, pit) is True, "hostile not held in the pit")
    with t.component("superdeep_capture_off", toggle="superdeepCaptureEnabled"):
        with _setting(t, "superdeepCaptureEnabled", False):
            # forced onto the SAME kind of cell as the ON side, so OFF differs only by the setting; a pawn on no pit
            # cell (None) is UNMEASURED, not "not held" (that used to pass vacuously)
            pid = _spawn_pawn_at(t, "Pirate", pit[0][0] - 3, pit[2][1], faction="hostile")
            _force_into(t, pid, pit[5][0], pit[5][1])
            if t._guard():
                held = _pit_held(t, pid, pit)
                if held is None:
                    raise ExpectationFailed("UNMEASURED: the forced pirate is on no pit cell, so capture OFF was not asked")
                _expect(held is False, "hostile held with capture OFF")


@suite.chain("toggle_ladder_required")
def toggle_ladder_required(t):
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("ladder_required_on", toggle="ladderRequiredToExitEnabled"):
        with _setting(t, "superdeepCapturesOwnFaction", True):
            pid = _spawn_pawn_at(t, "Colonist", pit[0][0] - 3, pit[0][1])
            _force_into(t, pid, pit[4][0], pit[4][1])     # a colonist never paths in (ruling 10-06); forced = a jumper
            _wait(t, 10 * PULSE)
            if t._guard():
                _expect(_pit_held(t, pid, pit) is True, "pawn not held in the pit without a ladder")
    with _owed(t, "ladder_required_ladder_lets_out", "ladderRequiredToExitEnabled: the placed ladder's effect was never read"):
        pass
    with _owed(t, "ladder_required_off", "ladderRequiredToExitEnabled OFF: nothing read"):
        pass


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
    _stage(t, "jawa/spawn_batch", ops=";".join("%s:%d,%d" % (LADDER, x, z) for x, z in pit))
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
        _stage(t, "jawa/spawn_batch", ops=";".join("RM_PitCover_WovenScrap:%d,%d" % (x, z) for x, z in pit))
        hid = _spawn_pawn_at(t, "Pirate", pit[4][0], pit[4][1], faction="hostile")
        _wait(t, 2 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_WovenScrap", rect=_rect(pit[0][0] - 1, pit[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 0, "woven cover still standing under a ~70 kg hostile: %r" % r)
            _expect(_pit_held(t, hid, pit) is True, "hostile not held after the cover gave way")
    with t.component("light_does_not_spring_reinforced", toggle="trapTriggerEnabled"):
        _stage(t, "jawa/spawn_batch", ops=";".join("RM_PitCover_ReinforcedFrame:%d,%d" % (x, z) for x, z in twin))
        lid = _spawn_pawn_at(t, "Pirate", twin[4][0], twin[4][1], faction="hostile")
        _wait(t, 2 * PULSE)
        if t._guard():
            r = t.bridge_call("jawa/list_things", defName="RM_PitCover_ReinforcedFrame", rect=_rect(twin[0][0] - 1, twin[0][1] - 1, 5, 5))
            _expect((r or {}).get("countMatched") == 9, "reinforced cover sprang under one ~70 kg pawn (220 kg tier): %r" % r)
            # `is not True`: jawa/flowworks_pit_report lists no pawn on a COVERED cell (an intact cover is ground), so
            # _pit_held answers None there, never False (MEASURED 2026-10-06: the pirate stood on the intact frame, free)
            _expect(_pit_held(t, lid, twin) is not True, "pawn on an intact cover reads as held")


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
    _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (SPIKES, pit[4][0], pit[4][1]))
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
    Plot H (FLOWWORKS_SLUICE_TWO_DOORS_1, owner 2026-10-06: a sluice is sealed shut, a grate always passes):
    a D=2 channel off a painted (limited, mid-map) deep-water strip runs through a closed steel grate and then a closed wooden sluice;
    the level must pass the grate and stop at the sluice (the open sluice is JawaBench playtest ScnSluice). Plot G: who each door opens for -- a hostile human and a
    wild muffalo (W=2 at the default multiplier) force the sluice, a hare does not; the grate holds the
    human; a hostile held in the superdeep pit cannot open a sluice beside it.
    Not proven here: a wooden one burning (stuff flammability is vanilla), real pathing through a
    forced sluice (first poke: march a hostile at a closed sluice and watch it pass), the art."""
    x0, z0 = _prep_plot(t, "H")
    _limitless_source(t, "H")
    run = _channel_from(x0 + 10, z0 + 6, 8)
    _dig_run(t, run, 2)
    gr, sl = run[2], run[5]
    _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (GRATE, gr[0], gr[1]), stuff="Steel")
    _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % (SLUICE, sl[0], sl[1]), stuff="WoodLog")
    with t.component("grate_passes_sluice_seals"):
        _wait(t, 10 * PULSE)
        before = _rep(t, *run[4])
        far = _rep(t, *run[-1])
        if t._guard():
            txt = _door_proof(t, "ProofLiquid", gr[0], gr[1])
            _expect("open=False" in txt and "seals=False" in txt and " fill 0" not in txt,
                    "closed grate did not pass liquid: %s" % txt)
            txt = _door_proof(t, "ProofLiquid", sl[0], sl[1])
            _expect("open=False" in txt and "seals=True" in txt and txt.endswith(" fill 0"),
                    "closed sluice not sealed: %s" % txt)
            _expect((before.get("fill") or 0) >= 1, "liquid never reached the shut sluice: fill %r" % before.get("fill"))
            _expect((far.get("fill") or 0) == 0, "liquid passed the shut sluice: far fill %r" % far.get("fill"))
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    sl, gr, lip = (x0 + 2, z0 + 3), (x0 + 4, z0 + 3), (pit[1][0] - 1, pit[1][1])
    # PLAYER-owned, as a built door is: spawn_batch leaves a door factionless, and vanilla Building_Door lets anyone
    # open a factionless door -- the hare walked through (MEASURED 2026-10-06: "Hare OPEN"), which says nothing
    # about the sluice rule.
    _stage(t, "jawa/build_batch", ops="%s:%d,%d;%s:%d,%d" % (SLUICE, sl[0], sl[1], SLUICE, lip[0], lip[1]),
                  stuff="WoodLog", faction="player")
    _stage(t, "jawa/build_batch", ops="%s:%d,%d" % (GRATE, gr[0], gr[1]), stuff="Steel", faction="player")
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
    # needs an occupant + two shooters (lip vs 5 cells); live_probes/fw_superdeep_target.py is the hand-run predicate
    with _owed(t, "shooting_rule_on", "superdeepShootingRuleEnabled: no target-legality read"):
        pass
    with _owed(t, "shooting_rule_off", "superdeepShootingRuleEnabled OFF: no target-legality read"):
        pass


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
        if not pw:
            raise ExpectationFailed("UNMEASURED: pawn_get found no pawn %s: %r" % (pid, r))
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


def _pawn_sink(t, pid):
    """PIT_DEPTH_DRAW_OFFSET_1: RM_PromotionProofs.ProofPawnSink reads the pawn's REAL DrawPos through the Harmony
    postfix: 'SINK id=.. depth=D .. sink=S drawDz=dz .. enabled=b'. Returns the key=value dict ({} if refused)."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofPawnSink",
                      args=str(pid))
    txt = str((r or {}).get("result", ""))
    if not txt.startswith("SINK"):
        return {}
    return dict(kv.split("=", 1) for kv in txt.split()[1:] if "=" in kv)


@suite.chain("toggle_pit_depth_draw")
def toggle_pit_depth_draw(t):
    # PIT_DEPTH_DRAW_OFFSET_1: a pawn standing on a D=4 cell is drawn sunk (drawDz < 0); with the toggle off the
    # postfix must leave DrawPos at the cell centre (drawDz ~ 0). UNMEASURED-tolerant via t._guard().
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with _setting(t, "superdeepCaptureEnabled", False):
        with t.component("pit_depth_draw_on", toggle="pitDepthDrawOffsetEnabled"):
            pid = _spawn_pawn_at(t, "Colonist", pit[4][0], pit[4][1])
            # drafted: capture is OFF here, so an undrafted colonist walks out of the pit and the read lands on a
            # D=0 cell mid-step (MEASURED 2026-10-06: depth 0, moving True, drawDz -2 = the step tween, not the mod)
            t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
            _wait(t, 30)
            if t._guard():
                kv = _pawn_sink(t, pid)
                _expect(kv.get("depth") == "4" and float(kv.get("drawDz", "0")) < -0.05,
                        "pawn on a D=4 cell not drawn sunk: %s" % kv)
        with t.component("pit_depth_draw_off", toggle="pitDepthDrawOffsetEnabled"):
            with _setting(t, "pitDepthDrawOffsetEnabled", False):
                pid2 = _spawn_pawn_at(t, "Colonist", pit[3][0], pit[3][1])
                t.bridge_call("jawa/set_draft", pawnId=pid2, drafted=True)
                _wait(t, 30)
                if t._guard():
                    kv = _pawn_sink(t, pid2)
                    _expect(kv.get("depth") == "4" and abs(float(kv.get("drawDz", "9"))) < 0.05,
                            "pawn drawn sunk while pitDepthDrawOffsetEnabled is off: %s" % kv)


def _fill_fx(t):
    """PIT_FILL_EFFECTS_1 census: every pawn standing in liquid, with cell fluid, swimmer flag, drown/tox severity."""
    # args=" " (not ""): static_call reads "" as ZERO arguments and ProofReport takes one -- with "" this census
    # was "No public static ProofReport with 0 params" on every call (harness bug, fixed 2026-10-05)
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitFillEffects", method="ProofReport", args=" ")
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
    # three ISOLATED 1x1 pits, 4 apart: in one 3x3 pit the held occupants wander onto its dry cells and drop out of
    # the per-fluid census (live 19:58: the poison pirate stood on a dry pit cell -> "got {}")
    x0, z0 = _prep_plot(t, "G")
    a, b, c = (x0 + 4, z0 + 6), (x0 + 8, z0 + 6), (x0 + 12, z0 + 6)
    _dig_run(t, [a, b, c], 4)
    _fill_fluid(t, a[0], a[1], 4, "RM_Fluid_Water")
    _fill_fluid(t, b[0], b[1], 4, "RM_Fluid_Poison")
    _fill_fluid(t, c[0], c[1], 4, "RM_Fluid_Oil")
    # held hostiles, not colonists: an undrafted colonist is not held (own-faction carve-out) and walked OUT of the
    # pit before the census (live 19:38: "FILLFX 0" -- nobody standing in liquid)
    pa = _spawn_pawn_at(t, "Pirate", a[0], a[1], faction="hostile")
    pb = _spawn_pawn_at(t, "Pirate", b[0], b[1], faction="hostile")
    pc = _spawn_pawn_at(t, "Pirate", c[0], c[1], faction="hostile")
    for p in (pa, pb, pc):
        t.bridge_call("jawa/pawn_gear", pawn=p, action="clear")
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
        t.expect("fire", {"def": "Fire"})          # the burning occupant sets vanilla Fire: that is the point
        _light(t, c[0], c[1])
        _wait(t, 2 * 250)
        rc = _fx_row(_fill_fx(t), pc)
        if t._guard():
            _expect(rc.get("burning") == "True", "lit oil pit not burning: %r" % rc)
            r = t.bridge_call("jawa/pawn_get", pawn=pc)      # jawa/pawn_health ADDS a hediff; pawn_get lists them
            hs = [h.get("def") for h in (((r or {}).get("pawns") or [{}])[0].get("hediffs") or [])]
            _expect(any("Burn" in str(h) for h in hs), "occupant of a burning oil pit has no burn: hediffs %s" % hs)
    _extinguish_all(t)
    t.bridge_call("jawa/destroy_batch", rects=_rect(x0, z0, PW, PH), categories="All")


@suite.chain("toggle_pit_fill_effects")
def toggle_pit_fill_effects(t):
    """OFF: water at D=4 drowns no one and poison poisons no one."""
    x0, z0 = _prep_plot(t, "G")
    pit = {3: (x0 + 4, z0 + 6), 5: (x0 + 8, z0 + 6)}      # isolated 1x1 pits (see pit_fill_effects)
    _dig_run(t, list(pit.values()), 4)
    _fill_fluid(t, pit[3][0], pit[3][1], 4, "RM_Fluid_Water")
    _fill_fluid(t, pit[5][0], pit[5][1], 4, "RM_Fluid_Poison")
    with t.component("pit_drowning_off", toggle="pitDrowningEnabled"):
        with _setting(t, "pitDrowningEnabled", False):
            pid = _spawn_pawn_at(t, "Pirate", pit[3][0], pit[3][1], faction="hostile")
            _wait(t, 4 * 250)
            row = _fx_row(_fill_fx(t), pid)
            if t._guard():
                # a pawn missing from the census reads drown 0 too: require its row in the water cell first
                _expect(row.get("fluid") == "RM_Fluid_Water", "pirate not in the water pit's census row: %r" % row)
                _expect(float(row.get("drown", 0)) == 0, "drowning with pitDrowningEnabled OFF: %r" % row)
    with t.component("poison_fill_off", toggle="poisonFillEnabled"):
        with _setting(t, "poisonFillEnabled", False):
            pid = _spawn_pawn_at(t, "Pirate", pit[5][0], pit[5][1], faction="hostile")
            _wait(t, 4 * 250)
            row = _fx_row(_fill_fx(t), pid)
            if t._guard():
                _expect(row.get("fluid") == "RM_Fluid_Poison", "pirate not in the poison pit's census row: %r" % row)
                _expect(float(row.get("tox", 0)) == 0, "toxin with poisonFillEnabled OFF: %r" % row)



def _slime_report(t, arg=" "):
    """SLIME_CROSSING_BUILD_SLIPPERY_SLOPE census: RM_SlimeSlip.ProofReport; "reset" zeroes the slip counts first."""
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_SlimeSlip", method="ProofReport", args=arg)
    return str((r or {}).get("result", ""))


def _slime_canal(t, x0, z0):
    """An 8-cell D2 canal brim-full of green slime, and a colonist standing in its west end. -> (cells, pawn id)."""
    cells = [(x0 + 4 + i, z0 + 6) for i in range(8)]
    _dig_run(t, cells, 2)
    for x, z in cells:
        _fill_fluid(t, x, z, 2, "RM_Fluid_SlimeGreen")
    pid = _spawn_pawn_at(t, "Colonist", cells[0][0], cells[0][1])
    t.bridge_call("jawa/pawn_gear", pawn=pid, action="clear")
    return cells, pid


@suite.chain("slime_slip")
def slime_slip(t):
    """SLIME_CROSSING_BUILD_SLIPPERY_SLOPE first script. Owner: "Slime has the particular property of being so slippery
    that it is nearly impossible to cross, and escape from the pit takes a great deal of time." A colonist ordered along a
    slime-filled canal slips (counted by RM_SlimeSlip's census; every slip also throws a "Slipped in the ..." text mote);
    natural (undug) slime ground slips too (owner 2026-10-16: "Natural slime should also be slippery."), never with a
    climb-out slide. OFF: no slip."""
    x0, z0 = _prep_plot(t, "G")
    cells, pid = _slime_canal(t, x0, z0)
    with t.component("slime_slips_the_wader", toggle="slimeSlipEnabled"):
        _slime_report(t, "reset")
        _march(t, pid, cells[-1][0], cells[-1][1], 20 * 60)
        row = _fx_row(_slime_report(t), pid)
        if t._guard():
            _expect(row.get("fluid") == "RM_Fluid_SlimeGreen" or int(row.get("slips", 0)) > 0,
                    "colonist not in the slime census: %r" % row)
            _expect(int(row.get("slips", 0)) > 0, "20 s of walking in slime and no slip: %r" % row)
    with t.component("slime_slip_off", toggle="slimeSlipEnabled"):
        with _setting(t, "slimeSlipEnabled", False):
            _slime_report(t, "reset")
            _march(t, pid, cells[0][0], cells[0][1], 20 * 60)
            rep = _slime_report(t)
            row = _fx_row(rep, pid)
            if t._guard():
                _expect("enabled=False" in rep, "setting not off in the census: %r" % rep[:120])
                if not row:      # a pawn absent from the census reads slips 0 too: the OFF side needs its row
                    raise ExpectationFailed("UNMEASURED: the colonist is in no census row (not in the slime), so slip OFF was not asked: %r" % rep[:160])
                _expect(int(row.get("slips", 0)) == 0, "slipped with slimeSlipEnabled OFF: %r" % row)
    with t.component("natural_slime_slips", toggle="slimeSlipEnabled"):
        # owner 2026-10-16: "Natural slime should also be slippery." A natural (undug) green slime pool strip, painted.
        strip = [(x0 + 4 + i, z0 + 10) for i in range(8)]
        _stage(t, "jawa/set_terrain_batch", ops="RM_SlimeGreenShallow:%d,%d,8,1" % (strip[0][0], strip[0][1]))
        pn = _spawn_pawn_at(t, "Colonist", strip[0][0], strip[0][1])
        t.bridge_call("jawa/pawn_gear", pawn=pn, action="clear")
        _slime_report(t, "reset")
        _march(t, pn, strip[-1][0], strip[-1][1], 20 * 60)
        row = _fx_row(_slime_report(t), pn)
        if t._guard():
            _expect(row.get("ground") == "RM_SlimeGreenShallow" or int(row.get("slips", 0)) > 0,
                    "colonist not on the natural slime in the census: %r" % row)
            _expect(int(row.get("slips", 0)) > 0, "20 s of walking on natural slime and no slip: %r" % row)
            _expect(int(row.get("climbSlips", 0)) == 0, "a climb-out slip on natural ground (no climb there): %r" % row)
    t.bridge_call("jawa/destroy_batch", rects=_rect(x0, z0, PW, PH), categories="All")


def _count(t, def_name, x, z, w, h):
    """Spawned things of `def_name` in a rect (jawa/list_things); None offline / unanswered."""
    r = t.bridge_call("jawa/list_things", defName=def_name, rect=_rect(x, z, w, h), limit=50)
    if r is None:
        return None
    return len(r.get("things") or [])


def _bottle_loop_plot(t):
    """Plot F with a 4x4 WaterShallow pond at its west side, one RM_BottleEmpty (stuffed) 6 cells east of it, two fed
    colonists. No tank, so only the terrain fill giver (WorkGiver_FillBottle, gate bottleLoopEnabled) has work."""
    x0, z0 = _prep_plot(t, "F")
    _stage(t, "jawa/set_terrain_batch", ops="WaterShallow:%s" % _rect(x0 + 1, z0 + 5, 4, 4))
    bottle = (x0 + 10, z0 + 6)
    _stage(t, "jawa/spawn_batch", ops="RM_BottleEmpty:%d,%d" % bottle, stuff="Leather_Plain")
    for i in range(2):
        pid = _spawn_pawn_at(t, "Colonist", x0 + 12 + i, z0 + 8)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    return x0, z0


def _bottle_state(t, x0, z0):
    """(empty bottles, filled fresh-water bottles) on the plot."""
    return (_count(t, "RM_BottleEmpty", x0, z0, PW, PH), _count(t, "RM_Bottle_FreshWater", x0, z0, PW, PH))


@suite.chain("toggle_bottle_loop")
def toggle_bottle_loop(t):
    """bottleLoopEnabled gates WorkGiver_FillBottle: an empty bottle is carried to water terrain and filled. ON: within
    3000 ticks the plot's RM_BottleEmpty is gone and an RM_Bottle_FreshWater exists (a fill COUNTED, not a spawned thing
    re-read). OFF, same scene: after 2000 ticks the empty bottle is still empty."""
    x0, z0 = _bottle_loop_plot(t)
    with t.component("bottle_loop_on", toggle="bottleLoopEnabled"):
        st = (None, None)
        for _ in range(24):                       # 3000 ticks
            t.wait_ticks(125)
            st = _bottle_state(t, x0, z0)
            if st[0] == 0 and (st[1] or 0) > 0:
                break
        if t._guard():
            _expect(st[0] == 0 and (st[1] or 0) > 0, "no fill: (empty, filled) bottles = %s after 3000 ticks (WorkGiver_FillBottle)" % (st,))
    x0, z0 = _bottle_loop_plot(t)
    with t.component("bottle_loop_off", toggle="bottleLoopEnabled"):
        with _setting(t, "bottleLoopEnabled", False):
            for _ in range(16):                   # 2000 ticks
                t.wait_ticks(125)
            st = _bottle_state(t, x0, z0)
            if t._guard():
                _expect(st[0] == 1 and not st[1], "bottle filled with bottleLoopEnabled OFF: (empty, filled) = %s" % (st,))


def _drink(t, pid, cell, plot=None):
    """RM_NorthstarProofs.ProofBottle: the pawn drinks the filled bottle at `cell` through vanilla Thing.Ingested (the
    route every drink job ends in), so IngestionOutcomeDoer_BottleResidue runs as shipped. Anything but "DRANK" is
    UNMEASURED: no drink, no residue to read. The residue lands beside the DRINKER, wherever he stands, not beside the
    bottle; with `plot` (x0, z0) a drinker off the plot is UNMEASURED, never a lost bottle (L1 2026-10-15: the drinker had
    walked to (148,130) during the wash row, his clean empty landed off the plot and bottle_dirty_off read FAIL)."""
    res = _sc(t, NS_PROOF, "ProofBottle", "%s;%d,%d" % (pid, cell[0], cell[1]))
    if t._guard() and not res.startswith("DRANK"):
        raise ExpectationFailed("UNMEASURED: no drink at %s: %s" % (cell, res))
    if plot is not None and t._guard():
        import re
        m = re.search(r"residueAt=(-?\d+),(-?\d+)", res)
        if not m or not (plot[0] + 1 <= int(m.group(1)) < plot[0] + PW - 1 and plot[1] + 1 <= int(m.group(2)) < plot[1] + PH - 1):
            raise ExpectationFailed("UNMEASURED: the drinker is not inside plot %s, so his residue is not on it: %s" % (plot, res))
    return res


def _bottle_census(t, x0, z0):
    """{defName: count} of the bottle-sized containers on the plot (empty, dirty, fresh water)."""
    return {d: _count(t, d, x0, z0, PW, PH) for d in ("RM_BottleEmpty", "RM_BottleDirty", "RM_Bottle_FreshWater")}


@suite.chain("toggle_bottle_dirty")
def toggle_bottle_dirty(t):
    """LIQUID_BOTTLE_LOOP_1 A1 (drink -> dirty -> wash -> clean) and A3 (dirty stage OFF: a drink leaves a clean empty,
    no dirty bottle anywhere). Plot F: _bottle_loop_plot's pond, empty bottle and two colonists, plus a drinker and two
    filled RM_Bottle_FreshWater. bottleLoopEnabled is OFF while a drink is read, so no fill/wash job moves a bottle
    between the drink and the census; the wash row turns it back on (its shipped default) and waits."""
    x0, z0 = _bottle_loop_plot(t)
    full_a, full_b = (x0 + 15, z0 + 4), (x0 + 17, z0 + 4)
    ops = "RM_Bottle_FreshWater:%d,%d;RM_Bottle_FreshWater:%d,%d" % (full_a + full_b)
    _stage(t, "jawa/spawn_batch", ops=ops, stuff="Leather_Plain")
    pid = _spawn_pawn_at(t, "Colonist", x0 + 16, z0 + 3)
    with t.component("bottle_dirty_on", toggle="bottleDirtyStageEnabled"):
        with _setting(t, "bottleLoopEnabled", False):
            c0 = _bottle_census(t, x0, z0)
            _drink(t, pid, full_a, plot=(x0, z0))
            c1 = _bottle_census(t, x0, z0)
            if t._guard():
                _expect((c1["RM_BottleDirty"] or 0) == (c0["RM_BottleDirty"] or 0) + 1,
                        "a drink with the dirty stage ON left no dirty bottle: %s -> %s" % (c0, c1))
                _expect(c1["RM_BottleEmpty"] == c0["RM_BottleEmpty"],
                        "a drink with the dirty stage ON left a clean empty: %s -> %s" % (c0, c1))
    with t.component("bottle_wash_returns_clean", toggle="bottleLoopEnabled"):
        c2 = None
        for _ in range(32):                       # 4000 ticks: carry to the pond, wash, (refill)
            t.wait_ticks(125)
            c2 = _bottle_census(t, x0, z0)
            clean = (c2["RM_BottleEmpty"] or 0) + (c2["RM_Bottle_FreshWater"] or 0)
            if c2["RM_BottleDirty"] == 0 and clean >= 3:   # both: a bottle in a hauler's hands is on no cell
                break
        if t._guard():
            _expect(c2["RM_BottleDirty"] == 0, "the dirty bottle was never washed in 4000 ticks: %s" % c2)
            # the plot's own empty + the washed one + the undrunk full one; a wash that destroyed the bottle reads 2
            _expect(clean >= 3, "washing lost a bottle: %s" % c2)
    with t.component("bottle_dirty_off", toggle="bottleDirtyStageEnabled"):
        with _setting(t, "bottleDirtyStageEnabled", False), _setting(t, "bottleLoopEnabled", False):
            # the first drinker worked through the wash row and stands wherever his last job left him: a fresh one at
            # the bottle, so the residue lands on the plot the census reads
            pid = _spawn_pawn_at(t, "Colonist", full_b[0], full_b[1] - 1)
            c0 = _bottle_census(t, x0, z0)
            _drink(t, pid, full_b, plot=(x0, z0))
            c1 = _bottle_census(t, x0, z0)
            if t._guard():
                _expect(c1["RM_BottleDirty"] == 0, "a dirty bottle with the dirty stage OFF: %s -> %s" % (c0, c1))
                _expect((c1["RM_BottleEmpty"] or 0) == (c0["RM_BottleEmpty"] or 0) + 1,
                        "a drink with the dirty stage OFF left no clean empty: %s -> %s" % (c0, c1))


UNITS_PER_LITRE = 10                      # RM_Volume.UnitsPerLitre: the tank unit is a decilitre
UNITS_PER_LEVEL = 1000 * UNITS_PER_LITRE  # RM_Volume.LitresPerLevel x UnitsPerLitre (a channel level = 1 kL = 10,000 units)


def _tank_units(t, x, z):
    """Tank units (decilitres) held by the RM_LiquidTank at (x,z), read from its inspect line ("Holding: <liquid> (a / b)",
    a and b in litres via RM_Volume.FormatLitres: "15 L", "12.5 kL"; Languages/English/Keyed/LiquidTank_Keys.xml); 0 for
    "Empty"; None when no tank answers. LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: the word "units" is gone from the line."""
    import re
    txt = _tank_text(t, x, z)
    m = re.search(r"\((\d+(?:\.\d+)?) (kL|L) / \d+(?:\.\d+)? (?:kL|L)\)", txt)
    if m:
        return int(round(float(m.group(1)) * (1000 if m.group(2) == "kL" else 1) * UNITS_PER_LITRE))
    return 0 if "Empty" in txt else None


def _tank_set(t, tank, mode, liquid=None, units=None):
    """RM_NorthstarProofs.ProofTank: the harness has no HoseProbe channel and a new tank is Store, which takes no unasked
    pour. Anything but a "TANK mode=..." answer is UNMEASURED, never a pass."""
    arg = "%d,%d;%s" % (tank[0], tank[1], mode)
    if liquid is not None:
        arg += ";%s;%d" % (liquid, units)
    r = t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank", args=arg)
    res = str((r or {}).get("result", ""))
    if t._guard() and not res.startswith("TANK mode=%s effective=%s" % (mode, mode)):
        raise ExpectationFailed("UNMEASURED: ProofTank %s did not set the mode: %r" % (arg, r))
    return res


def _tank_loop_plot(t, mode, bottle_def, liquid=None, units=None):
    """A colonist-owned tank (TryFindTank walks listerBuildings.AllBuildingsColonist, so an unowned spawn_batch tank is
    invisible to both WorkGivers) staged to `mode` (+ contents), one stuffed `bottle_def` beside it, two fed colonists
    (two: a spawned colonist may be incapable of Hauling, the WorkGivers' work type). No water terrain on the plot and the
    caller turns bottleLoopEnabled OFF, so the terrain fill giver (prio 50, 60-cell search, beats RM_FillFromTankWorkGiver
    at 47) cannot take the empty bottle first."""
    x0, z0 = _prep_plot(t, "F")
    tank, bottle = (x0 + 6, z0 + 6), (x0 + 10, z0 + 6)
    _stage(t, "jawa/build_batch", ops="RM_LiquidTank:%d,%d" % tank, faction="player")
    _stage(t, "jawa/spawn_batch", ops="%s:%d,%d" % ((bottle_def,) + bottle), stuff="Leather_Plain")
    _tank_set(t, tank, mode, liquid, units)
    for i in range(2):
        pid = _spawn_pawn_at(t, "Colonist", x0 + 12 + i, z0 + 8)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    return x0, z0, tank


def _watch_tank(t, tank, ticks, done=None):
    """Tank units every 125 ticks (changes only) up to `ticks`; stops early once done(seq) holds."""
    seq = []
    for _ in range(ticks // 125):
        t.wait_ticks(125)
        u = _tank_units(t, *tank)
        if u is not None and (not seq or seq[-1] != u):
            seq.append(u)
        if done is not None and done(seq):
            break
    return seq


WATER_LIQUID = "RM_Liquid_FreshWater"
# RM_LiquidTank (2x2) holds 160,000 units = 16 kL (RM_Volume.TankCapacity); staging more makes ProofTank REFUSE.
# LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: was 60 (old 200 L drums) = 12 kL = 120,000 decilitres.
TANK_STAGE_UNITS = 120000


@suite.chain("toggle_tank_loop")
def toggle_tank_loop(t):
    """tankLoopEnabled gates exactly two WorkGivers (ShouldSkip): WorkGiver_EmptyBottleIntoTank (a filled container is
    carried to a colonist tank and poured in) and WorkGiver_FillBottleFromTank (an empty container is carried to a tank
    holding a bottled liquid and filled). It does NOT make a tank draw from an adjacent channel cell -- that is the
    pump's job (liquid_pump chain); the old row asserted that and FAILed every live run (FLOWWORKS_TANK_LOOP_ROW_WRONG_1).
    Since the 2026-10-11 bottle-loop fix no tank both takes bottles unasked and gives them back (RM_TankBottleRules), so
    the two halves are staged apart, bottleLoopEnabled OFF throughout so the terrain fill giver cannot win:
      draw-out: a Store tank pre-filled with 12 kL (TANK_STAGE_UNITS = 120,000 units) fresh water + one RM_BottleEmpty -> units FALL (ON); stay 12 kL (OFF).
      pour-in : an Empty Fill-mode tank + one RM_Bottle_FreshWater -> units RISE (ON); stay empty (OFF).
    Sampled every 125 ticks, 3000 ticks a window: a pour or a fill is a walk plus a toil."""
    with _setting(t, "bottleLoopEnabled", False):
        _, _, tank = _tank_loop_plot(t, "Store", "RM_BottleEmpty", WATER_LIQUID, TANK_STAGE_UNITS)
        with t.component("tank_loop_on", toggle="tankLoopEnabled"):
            seq = _watch_tank(t, tank, 3000, lambda s: bool(s) and s[-1] < TANK_STAGE_UNITS)
            if t._guard():
                _expect(bool(seq), "no RM_LiquidTank answered inspect_string at %s" % (tank,))
                _expect(seq[-1] < TANK_STAGE_UNITS, "draw-out never ran: tank units %s never fell below the staged %d "
                                       "(WorkGiver_FillBottleFromTank)" % (seq, TANK_STAGE_UNITS))
        _, _, tank = _tank_loop_plot(t, "Fill", "RM_Bottle_FreshWater")
        with t.component("tank_loop_pour_in"):
            seq = _watch_tank(t, tank, 3000, lambda s: bool(s) and max(s) > 0)
            if t._guard():
                _expect(bool(seq), "no RM_LiquidTank answered inspect_string at %s" % (tank,))
                _expect(max(seq) > 0, "pour-in never ran: Fill-mode tank units %s (WorkGiver_EmptyBottleIntoTank)" % seq)
        with _setting(t, "tankLoopEnabled", False):
            _, _, tank = _tank_loop_plot(t, "Store", "RM_BottleEmpty", WATER_LIQUID, TANK_STAGE_UNITS)
            with t.component("tank_loop_off", toggle="tankLoopEnabled"):
                seen = _watch_tank(t, tank, 3000)
                _, _, tank2 = _tank_loop_plot(t, "Fill", "RM_Bottle_FreshWater")
                seen2 = _watch_tank(t, tank2, 3000)
                if t._guard():
                    # an unanswered tank (seen == []) is UNMEASURED, never a pass: the OFF side must READ the staged 12 kL / the empty tank
                    _expect(bool(seen) and bool(seen2), "no RM_LiquidTank answered inspect_string (Store %s, Fill %s)" % (seen, seen2))
                    _expect(seen == [TANK_STAGE_UNITS], "Store tank drawn down with tankLoopEnabled OFF: units %s" % seen)
                    _expect(not any(seen2), "Fill tank took a bottle with tankLoopEnabled OFF: units %s" % seen2)


@suite.chain("toggle_liquid_drilling")
def toggle_liquid_drilling(t):
    # stochastic: the predicate wants >=1 yield in 3 runs at the shipped chance (def read first)
    with _owed(t, "liquid_drilling_on", "liquidDrillingEnabled: no yield counted"):
        pass
    with _owed(t, "liquid_drilling_off", "liquidDrillingEnabled OFF: no yield counted"):
        pass


@suite.chain("toggle_typed_shores")
def toggle_typed_shores(t):
    # Worldgen-affecting: needs two fresh quicktest maps (toggle on vs off) -- shared driver, plan 2.5/4 step 10. The old
    # block read the setting back (a missing `success` passed), which says nothing about shores.
    with _owed(t, "typed_shores_mapgen", "typedLiquidShoresEnabled: worldgen, needs two fresh maps"):
        pass


@suite.chain("toggle_trap_trigger")
def toggle_trap_trigger(t):
    """trapTriggerEnabled OFF (CompPitCoverTrigger returns early): the same ~70 kg hostile that springs a woven cover in
    pit_cover_fall (the ON side, heavy_springs_woven_cover) leaves it standing on all 9 cells."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    with t.component("trap_trigger_off", toggle="trapTriggerEnabled"):
        with _setting(t, "trapTriggerEnabled", False):
            _stage(t, "jawa/spawn_batch", ops=";".join("RM_PitCover_WovenScrap:%d,%d" % (x, z) for x, z in pit))
            _spawn_pawn_at(t, "Pirate", pit[4][0], pit[4][1], faction="hostile")
            _wait(t, 2 * PULSE)
            if t._guard():
                r = t.bridge_call("jawa/list_things", defName="RM_PitCover_WovenScrap",
                                  rect=_rect(pit[0][0] - 1, pit[0][1] - 1, 5, 5))
                _expect((r or {}).get("countMatched") == 9,
                        "woven cover gave way with trapTriggerEnabled OFF: %r" % (r,))


@suite.chain("toggle_fall_damage")
def toggle_fall_damage(t):
    # RM_SuperdeepTrap.cs gates the fall's damage on fallDamageEnabled; no row makes a pawn fall and reads its injuries
    with _owed(t, "fall_damage_on", "fallDamageEnabled: no fall staged, no injury read"):
        pass
    with _owed(t, "fall_damage_off", "fallDamageEnabled OFF: no fall staged"):
        pass


STEAM_PROOF = "RimMandrake.FlowWorks.ManyWaters.RM_RiverSteamProof"


def _steam(t, arg=" ", strict=True):
    """RM_RiverSteamProof.ProofSteam -> {biome, ext, on, river, vents, due, thrown, tick}; UNMEASURED when unread
    (`strict`; the chain's setup read is not strict, so an unread map reaches the components as UNMEASURED, not FAIL)."""
    txt = _sc(t, STEAM_PROOF, "ProofSteam", arg)
    if strict and t._guard() and not txt.startswith("STEAM"):
        raise ExpectationFailed("UNMEASURED: ProofSteam gave no answer: %r" % txt[:160])
    kv = _kv(txt)
    for k in ("river", "vents", "due", "thrown"):
        try:
            kv[k] = int(kv.get(k))
        except (TypeError, ValueError):
            kv[k] = None
    return kv


@suite.chain("toggle_river_steam")
def toggle_river_steam(t):
    """RIVER_STEAM_ANIMATION_1 state half (A1/A2; A3 is the owner's look). Plot C gets a 1x8 WaterMovingShallow strip
    (TerrainDef.IsRiver, the vent test MapComponent_RiverSteam uses) and ProofSteam "rescan" re-runs the vent scan, as
    FinalizeInit would on a map born with that river. The counters are the component's own: `due` = a vent's puff time
    came, `thrown` = a ribbon was made (unfogged vent). A biome WITH RiverSteamBiomeExtension (the Pyrelands) proves the
    toggle: ON throws ribbons within 300 ticks, OFF none. A biome WITHOUT it proves the gate: river cells, no vent, no
    ribbon. Each map can show only one half; the other reads UNMEASURED with the map it needs."""
    x0, z0 = _prep_plot(t, "C")
    _stage(t, "jawa/set_terrain_batch", ops="WaterMovingShallow:%s" % _rect(x0 + 4, z0 + 6, 8, 1))
    s0 = _steam(t, "rescan", strict=False)
    if "ext" not in s0:
        why = "ProofSteam unread on this map: %r" % s0
        on_why = off_why = gate_why = why
    elif s0["ext"] == "True":
        on_why = off_why = None
        gate_why = "biome %s steams; the gate half needs a map without RiverSteamBiomeExtension" % s0.get("biome")
    else:
        on_why = off_why = ("biome %s carries no RiverSteamBiomeExtension; the toggle half needs a Pyrelands river map "
                            "(RM_FE_Pyrelands)" % s0.get("biome"))
        gate_why = None
    with _unmeasured_if(t, on_why, "river_steam_on", toggle="riverSteamEnabled"):
        t.wait_ticks(300)
        s1 = _steam(t)
        if t._guard():
            _expect((s1["vents"] or 0) > 0, "a steam biome with %s river cells has no vent: %s" % (s1["river"], s1))
            if (s1["due"] or 0) > 0 and not s1["thrown"]:
                raise ExpectationFailed("UNMEASURED: every vent is fogged (due %s, thrown 0)" % s1["due"])
            _expect((s1["thrown"] or 0) > 0, "no steam ribbon in 300 ticks with riverSteamEnabled ON: %s" % s1)
    with _unmeasured_if(t, off_why, "river_steam_off", toggle="riverSteamEnabled"):
        with _setting(t, "riverSteamEnabled", False):
            _steam(t, "rescan")
            t.wait_ticks(300)
            s2 = _steam(t)
            if t._guard():
                _expect(s2["due"] == 0 and s2["thrown"] == 0, "steam with riverSteamEnabled OFF: %s" % s2)
    with _unmeasured_if(t, gate_why, "river_steam_biome_gate", beyond_toggle=True):
        t.wait_ticks(300)
        s3 = _steam(t)
        if t._guard():
            _expect((s3["river"] or 0) >= 8, "the painted river strip did not read as river: %s" % s3)
            _expect(s3["vents"] == 0 and s3["thrown"] == 0, "a biome without the extension steams: %s" % s3)


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
    _stage(t, "jawa/spawn_batch", ops="RM_Swale:%d,%d" % (x, z))
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
        _stage(t, "jawa/set_terrain_batch", ops=";".join("SoilRich:%s" % r for r in ring))  # the swale's own cell untouched
        txt = _swale_proof(t, x, z)
        if t._guard():
            _expect(txt.startswith("CAPPED"), "a swale ringed by rich soil still stepped: %s" % txt)
    with t.component("swale_off_is_inert", toggle="swaleEnabled"):
        with _setting(t, "swaleEnabled", False):
            txt = _swale_proof(t, x, z)
            if t._guard():
                _expect(txt == "OFF", "swaleEnabled OFF but the swale still answered: %s" % txt)


# =============================================================== 2026-10-05 BUILD PASS
# Rows owed by Transient/belt_fwbuild_20261005.md "NEW ROWS NEEDED", written dense: one chain per mechanism, each
# toggle's two sides in adjacent components, every read through the shipping code's own predicates
# (RM_NorthstarProofs / RM_LiquidFireProof / RM_DigDiscoveryProof via jawa/static_call). NOT wired, and why:
#   * Exposed Prisoner gated on a Charity precept (PIT_TEMPERATURE_SOFTENING_1 leftover): needs two ideoligions
#     authored live; its toggle (pitExposureEnabled) is already proven by toggle_pit_exposure. Live walk owed.
#   * DBH thirst patch (LIQUID_THIRST_CHAIN_1): DBH is not on any test list; the patch is inert without it.
#   * Bottle fill-job fix (cf1e75d26): toggle_bottle_loop is the route; no new row.
#   * Too-wide pawn not offered capture-down: RM_PitRoomMath.CaptureDown is proven offline by the C# selftest.

NS_PROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
FIRE_PROOF = "RimMandrake.FlowWorks.RM_LiquidFireProof"
DIG_PROOF = "RimMandrake.FlowWorks.RM_DigDiscoveryProof"


def _sc(t, typ, method, arg):
    """One static_call, text result. arg "" would be read as ZERO arguments: every method here takes one string,
    so an empty argument is sent as " "."""
    r = t.bridge_call("jawa/static_call", type=typ, method=method, args=arg if arg else " ")
    return str((r or {}).get("result") or (r or {}).get("message") or (r or {}).get("error") or "")


def _kv(txt):
    return dict(p.split("=", 1) for p in txt.split() if "=" in p)


def _fire_count(t):
    """FIRE burning N, or None when the report is unreadable."""
    txt = _sc(t, FIRE_PROOF, "ProofReport", " ")
    try:
        return int(txt.split("burning", 1)[1].split("|", 1)[0])
    except (IndexError, ValueError):
        return None


def _flames(t, cells):
    """The subset of `cells` holding an RM_LiquidFlame."""
    out = set()
    for x, z in cells:
        r = t.bridge_call("jawa/list_things", defName=FLAME, rect=_rect(x, z, 1, 1), limit=5)
        if not t._guard():
            continue
        if not isinstance(r, dict) or r.get("success") is not True or not isinstance(r.get("things"), list):
            # a failed or empty reply is not "no flame": every OFF side would pass on a blind instrument
            raise ExpectationFailed("UNMEASURED: jawa/list_things %s at (%d,%d) did not answer: %r" % (FLAME, x, z, r))
        if r["things"]:
            out.add((x, z))
    return out


def _foam(t, c):
    """Firefoam on one burning cell the way a firefoam popper delivers it: an Extinguish blast of radius 0.5.
    (Foam LYING on a liquid cell is not testable: fill terrains are water-tagged and take no filth -- live 19:47, a
    blast scattering Filth_FireFoam at chance 1 left none, and jawa/spawn_batch makes no filth at all.)"""
    t.bridge_call("jawa/map_explosion", center="%d,%d" % c, damType="Extinguish", radius=0.5, screenShake=0)


def _extinguish_all(t):
    """Put every fire on the map out with the SHARED helper (modcheck.helpers.extinguish: map_fire extinguish + a
    complete-list re-read), so a chain that sets fire on purpose cannot hand the next chain a fire_on_map surprise
    (live 20:04: the oil pit's burning pirate left one Fire that aborted pit_prison_room and bottle_revert)."""
    if getattr(t, "session", None) is None or not t._guard():
        return
    # the liquid fire first (a burning cell re-sets its occupant alight every 60 ticks): canalFireEnabled off runs
    # RM_LiquidFire.ExtinguishAll on the next check
    with _setting(t, "canalFireEnabled", False):
        t.wait_ticks(60)
    from modcheck import helpers as H
    try:
        H.extinguish(t.session)
    except Exception:              # noqa: BLE001 -- a residue fire is the detector's to report, not a crash here
        pass


def _tar_cells(t, cells):
    for x, z in cells:
        _dig(t, x, z, 1)
        _fill_fluid(t, x, z, 1, "RM_Fluid_Tar")


def _boom(t, c, dam):
    t.bridge_call("jawa/map_explosion", center="%d,%d" % c, damType=dam, radius=0.9, screenShake=0)


# Phase 6 owed (330a510d8 + the 2026-10-05 fix that gave foam and rain their first caller). Three chains so one red
# mechanism does not blank the other two. Every burnable cell is an ISOLATED 1x1 tar cut (3 apart): no neighbour can
# relight it, so each read is one cell's own fate.

@suite.chain("fire_explosion")
def fire_explosion(t):
    """A Bomb lights tar with no Fire anywhere, an EMP does not, and with the setting off a Bomb does not."""
    x0, z0 = _prep_plot(t, "E")
    bomb_off, emp_on, bomb_on = (x0 + 2, z0 + 1), (x0 + 9, z0 + 1), (x0 + 16, z0 + 1)
    _tar_cells(t, [bomb_off, emp_on, bomb_on])
    with _setting(t, "canalFireEnabled", True):
        with t.component("explosion_off_does_not_light", toggle="explosionIgnitesLiquidEnabled"):
            with _setting(t, "explosionIgnitesLiquidEnabled", False):
                _boom(t, bomb_off, "Bomb")
                _wait(t, PULSE)
                _expect(not _flames(t, [bomb_off]) if t._guard() else None, "Bomb lit tar with the setting OFF")
        with t.component("explosion_lights_liquid", toggle="explosionIgnitesLiquidEnabled"):
            _boom(t, emp_on, "EMP")
            _boom(t, bomb_on, "Bomb")
            _wait(t, PULSE)
            if t._guard():
                _expect(not _flames(t, [emp_on]), "an EMP blast lit tar")
                _expect(_flames(t, [bomb_on]) == {bomb_on}, "a Bomb blast did not light tar (no Fire involved)")


@suite.chain("fire_foam")
def fire_foam(t):
    """A firefoam blast on two burning cells puts them out while the two it missed burn on; with the setting off the
    same blast leaves the liquid burning."""
    x0, z0 = _prep_plot(t, "E")
    foam = [(x0 + 2 + 3 * i, z0 + 4) for i in range(4)]
    _tar_cells(t, foam)
    with _setting(t, "canalFireEnabled", True):
        for c in foam:
            _light(t, *c)
        with t.component("foam_smothers_burning_liquid", toggle="foamSmothersLiquidFireEnabled"):
            lit0 = _flames(t, foam)
            for c in foam[:2]:
                _foam(t, c)
            t.wait_ticks(90)
            lit1 = _flames(t, foam)
            if t._guard():
                _expect(lit0 == set(foam), "not every foam-test cell lit: %s" % sorted(lit0))
                _expect(not (lit1 & set(foam[:2])), "foamed cells still burning: %s" % sorted(lit1 & set(foam[:2])))
                _expect(lit1 >= set(foam[2:]), "unfoamed cells went out too: %s" % sorted(lit1))
        with t.component("foam_off_is_inert", toggle="foamSmothersLiquidFireEnabled"):
            with _setting(t, "foamSmothersLiquidFireEnabled", False):
                _foam(t, foam[2])
                t.wait_ticks(90)
                _expect(foam[2] in _flames(t, [foam[2]]) if t._guard() else None,
                        "foam put a cell out with foamSmothersLiquidFireEnabled OFF")
        t.bridge_call("jawa/map_fire", action="extinguish", rect=_rect(x0, z0, PW, PH))


@suite.chain("fire_rain")
def fire_rain(t):
    """Steady rain (filling off) douses open cells over 50 checks (0.03/check: P(an open cell survives) ~0.22) while a
    roofed twin row stays alight; with the setting off a relit open row stays lit."""
    x0, z0 = _prep_plot(t, "E")
    open_row = [(x0 + 2 + 3 * i, z0 + 8) for i in range(6)]
    roof_row = [(x0 + 2 + 3 * i, z0 + 11) for i in range(6)]
    _tar_cells(t, open_row + roof_row)
    _stage(t, "jawa/set_roof_batch", ops=";".join("RoofConstructed:%d,%d,1,1" % c for c in roof_row))
    with _setting(t, "canalFireEnabled", True), _setting(t, "rainFillsExcavationsEnabled", False):
        t.bridge_call("jawa/weather_set", weather="Rain", lockWeather=True)
        try:
            with t.component("rain_douses_open_fire", toggle="rainDousesLiquidFireEnabled"):
                for c in open_row + roof_row:
                    _light(t, *c)
                if t._guard():
                    lit0 = _flames(t, open_row + roof_row)
                    _expect(lit0 == set(open_row + roof_row), "not every rain-test cell lit before the rain: %d/12 (%s)"
                            % (len(lit0), sorted(set(open_row + roof_row) - lit0)))
                t.wait_ticks(3000)
                lo, lr = _flames(t, open_row), _flames(t, roof_row)
                if t._guard():
                    _expect(lr == set(roof_row), "a ROOFED cell went out in the rain: %d/6 lit" % len(lr))
                    _expect(len(lo) < 6, "no open cell doused after 3000 ticks of rain: %d/6 lit" % len(lo))
            with t.component("rain_off_leaves_fire", toggle="rainDousesLiquidFireEnabled"):
                with _setting(t, "rainDousesLiquidFireEnabled", False):
                    for c in open_row:
                        _light(t, *c)
                    t.wait_ticks(1500)
                    lo = _flames(t, open_row)
                    _expect(len(lo) == 6 if t._guard() else None,
                            "open cells went out in rain with the setting OFF: %d/6 lit" % len(lo))
        finally:
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            t.bridge_call("jawa/map_fire", action="extinguish", rect=_rect(x0, z0, PW, PH))


@contextmanager
def _num_setting(t, field, value):
    """A NUMERIC FlowWorks Mod Settings field for the duration of a block; the shipped default (site_spec.SETTINGS) is
    restored in finally, even when the block failed (the reason `_setting` restores through the session)."""
    default = REG.S.SETTINGS[S_FW][field]
    t.set_setting(S_FW, {field: value})
    try:
        yield
    finally:
        _restore(t, S_FW, field, default)


def _fire_cell(t, c):
    """RM_LiquidFireProof.ProofCell -> {burning, pending, due, hops, now}; UNMEASURED when unread."""
    txt = _sc(t, FIRE_PROOF, "ProofCell", "%d,%d" % c)
    if t._guard() and not txt.startswith("FIRECELL"):
        raise ExpectationFailed("UNMEASURED: ProofCell %s gave no answer: %r" % (c, txt[:160]))
    kv = _kv(txt)
    for k in ("due", "hops", "now"):
        try:
            kv[k] = int(kv.get(k))
        except (TypeError, ValueError):
            kv[k] = None
    return kv


FUSE_SLOW = 0.05   # fireFrontSpeedMultiplier for the fuse rows: tar 120 ticks/cell -> 2400, so only an earlier offer lights soon


@suite.chain("fire_queue_origin")
def fire_queue_origin(t):
    """LIQUID_FIRE_QUEUE_ORIGIN_1 (98d3f332dc), plot B. A2: two slow 1x2 tar fuses lit at their west cell; a vanilla Fire
    (the dropped torch, RM_LiquidFireProof.ProofTorch -> the shipping Fire.SpawnSetup hook) beside one fuse's pending
    east cell lights it within 3 checks while the twin fuse's cell still waits for the slow front. A3: the twin's
    pending front survives its RM_LiquidFire's own ExposeData written and read back through Scribe (the save half of a
    reload; a full game reload is not driven here). A1: a 6-cell oil run burns into a 5x5 tar pond with
    sourceFireReach 1; no pond cell farther than 1 (Chebyshev) from the run's mouth burns or waits to. (Oil since
    CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: chemfuel is now an inferno whose halo sets vanilla fires on the shore, and every
    such fire lights the pond beside it at hops 0, which is right and not what this row measures.)"""
    x0, z0 = _prep_plot(t, "B")
    torch_fuse = [(x0 + 3, z0 + 11), (x0 + 4, z0 + 11)]
    twin_fuse = [(x0 + 14, z0 + 11), (x0 + 15, z0 + 11)]
    torch = (x0 + 5, z0 + 12)          # 8-adjacent to torch_fuse[1], two cells from its lit end
    _tar_cells(t, torch_fuse + twin_fuse)
    # L1 2026-10-15 (HARNESS): the dropped torch IS a vanilla Fire (ProofTorch); undeclared, the watch read it as
    # fire_on_map at tick 92 and ended all three rows UNMEASURED on the first live run.
    t.expect("fire", {"def": "Fire"})
    with _setting(t, "canalFireEnabled", True):
        with _num_setting(t, "fireFrontSpeedMultiplier", FUSE_SLOW):
            lit = [_light(t, *torch_fuse[0]), _light(t, *twin_fuse[0])]
            with t.component("fire_torch_advances_pending", beyond_toggle=True):
                if t._guard() and not all(x.startswith("LIT") for x in lit):
                    raise ExpectationFailed("UNMEASURED: a fuse was never lit: %s" % lit)
                a0, b0 = _fire_cell(t, torch_fuse[1]), _fire_cell(t, twin_fuse[1])
                if t._guard():
                    for k in (a0, b0):
                        if k.get("pending") != "True" or (k["due"] or 0) - (k["now"] or 0) < 600:
                            raise ExpectationFailed("UNMEASURED: the fuse's next cell is not a slow pending front: %s" % k)
                _sc(t, FIRE_PROOF, "ProofTorch", "%d,%d" % torch)
                t.wait_ticks(90)
                a1, b1 = _fire_cell(t, torch_fuse[1]), _fire_cell(t, twin_fuse[1])
                if t._guard():
                    _expect(a1.get("burning") == "True",
                            "a torch beside the pending tar cell did not light it within 3 checks: %s -> %s" % (a0, a1))
                    _expect(b1.get("burning") == "False" and b1.get("pending") == "True",
                            "the untorched twin's pending cell did not keep waiting: %s -> %s" % (b0, b1))
            with t.component("fire_front_survives_save", beyond_toggle=True):
                rt = _sc(t, FIRE_PROOF, "ProofFrontRoundTrip", " ")
                if t._guard():
                    if not rt.startswith("ROUNDTRIP"):
                        raise ExpectationFailed("UNMEASURED: ProofFrontRoundTrip gave no answer: %r" % rt[:200])
                    kv = _kv(rt)
                    if kv.get("pending") in (None, "0"):
                        raise ExpectationFailed("UNMEASURED: no pending front to save: %s" % rt)
                    _expect(kv.get("same") == "True", "the pending front did not survive a save round trip: %s" % rt)
        _extinguish_all(t)
    px, pz = _limited_pond(t, "B", terrain="RM_TarShallow")
    run = _channel_from(px + 5, pz + 2, 6)
    mouth = run[0]
    with t.component("fire_reach_capped_at_source", beyond_toggle=True):
        _expect_fresh_pond(t, px, pz)
        _dig_run(t, run, 1)
        for x, z in run:
            _fill_fluid(t, x, z, 1, "RM_Fluid_Oil")
        with _setting(t, "canalFireEnabled", True), _setting(t, "explosionIgnitesLiquidEnabled", True), \
                _num_setting(t, "sourceFireReach", 1.0):
            lit = _light(t, *run[-1])
            if t._guard() and not lit.startswith("LIT"):
                raise ExpectationFailed("UNMEASURED: the oil run was never lit: %s" % lit)
            t.wait_ticks(1500)             # oil 90 ticks a cell reaches the mouth in ~450; tar crosses the pond in ~600 more
            sp = _sc(t, FIRE_PROOF, "ProofSourceSpread", "%d,%d;1" % mouth)
            if t._guard():
                if not sp.startswith("SPREAD"):
                    raise ExpectationFailed("UNMEASURED: ProofSourceSpread gave no answer: %r" % sp[:200])
                kv = _kv(sp)
                if int(kv.get("burningSource", 0)) + int(kv.get("pendingSource", 0)) == 0:
                    raise ExpectationFailed("UNMEASURED: the front never reached the pond: %s" % sp)
                _expect(kv.get("far") == "0", "pond cells lit beyond sourceFireReach 1 from the mouth: %s" % sp)
        _extinguish_all(t)


INFERNO_FLAME = "RM_LiquidFlame_Inferno"
RUT_BLAST = "RuthlessPursuingMechanoids.FuelBlastInvestigation"


def _things_at(t, def_name, cells):
    """The subset of `cells` holding a thing of `def_name` (a blind reply is UNMEASURED, never "none")."""
    out = set()
    for x, z in cells:
        r = t.bridge_call("jawa/list_things", defName=def_name, rect=_rect(x, z, 1, 1), limit=5)
        if not t._guard():
            continue
        if not isinstance(r, dict) or r.get("success") is not True or not isinstance(r.get("things"), list):
            raise ExpectationFailed("UNMEASURED: jawa/list_things %s at (%d,%d) did not answer: %r" % (def_name, x, z, r))
        if r["things"]:
            out.add((x, z))
    return out


def _fuel_run(t, cells, fluid):
    _dig_run(t, cells, 2)
    for x, z in cells:
        _fill_fluid(t, x, z, 2, fluid)


@suite.chain("fuel_moat_chemfuel")
def fuel_moat_chemfuel(t):
    """CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15: "a moat of gasoline"), plot F. A 12-cell D2 chemfuel
    moat lit at its west end is alight end to end within 90 ticks under the big flame, sets the wood lying two cells off
    its bank alight, and is burnt dry (F=0) within 1500 ticks. OFF side: the same moat with chemfuelInfernoEnabled off
    still burns under the small flame and still holds chemfuel after 1500 ticks (a level a day)."""
    x0, z0 = _prep_plot(t, "F")
    t.expect("fire", {"def": "Fire"})          # the inferno's halo sets vanilla Fire on purpose
    moat = _line(x0 + 3, z0 + 3, 12)
    slow = _line(x0 + 3, z0 + 10, 12)
    wood = (x0 + 9, z0 + 5)
    _fuel_run(t, moat, "RM_Fluid_Chemfuel")
    _stage(t, "jawa/spawn_batch", ops="WoodLog:%d,%d" % wood)
    with _setting(t, "canalFireEnabled", True):
        with t.component("chemfuel_moat_goes_up", toggle="chemfuelInfernoEnabled"):
            lit = _light(t, *moat[0])
            if t._guard() and not lit.startswith("LIT"):
                raise ExpectationFailed("UNMEASURED: the chemfuel moat was never lit: %s" % lit)
            t.wait_ticks(90)
            big = _things_at(t, INFERNO_FLAME, moat)
            if t._guard():
                _expect(len(big) == len(moat), "inferno flame on %d/%d moat cells 90 ticks after the light" % (len(big), len(moat)))
            t.wait_ticks(300)
            near = t.bridge_call("jawa/list_things", defName="Fire", rect=_rect(wood[0] - 1, wood[1] - 1, 3, 3), limit=5) or {}
            gone = not _things_at(t, "WoodLog", [wood])      # a blind reply raises UNMEASURED, never "the log is gone"
            if t._guard():
                _expect(bool(near.get("things")) or gone, "the wood two cells off the bank never caught: %r" % near)
            _wait(t, 1500)
            _expect_state(t, moat, fill=0, what="burnt-out chemfuel moat")
        _extinguish_all(t)
        _fuel_run(t, slow, "RM_Fluid_Chemfuel")
        with t.component("chemfuel_inferno_off_smoulders", toggle="chemfuelInfernoEnabled"):
            with _setting(t, "chemfuelInfernoEnabled", False):
                lit = _light(t, *slow[0])
                if t._guard() and not lit.startswith("LIT"):
                    raise ExpectationFailed("UNMEASURED: the slow moat was never lit: %s" % lit)
                _wait(t, 1500)
                small = _things_at(t, FLAME, slow[:1])
                st = _state(t, slow[:1])
                if t._guard():
                    _expect(small == {slow[0]}, "inferno OFF: the lit cell carries no small flame")
                    _expect(st[0][1] and st[0][1] > 0, "inferno OFF: the lit cell burnt dry in 1500 ticks: F=%r" % (st[0][1],))
        _extinguish_all(t)


@suite.chain("fuel_moat_astrofuel")
def fuel_moat_astrofuel(t):
    """CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15: "an ultimate spatially continuous bomb"), plot F. A
    12-cell D2 astrofuel channel lit at its west end is EMPTY (every cell F=0) 60 ticks later, the fire report counts one
    more detonation and nothing left queued, and a muffalo standing beside it was thrown (it moved). With RimUtinni's
    Empire Pursuit loaded the blast queued an investigating raid (fired at once here, then removed). OFF side: with
    astrofuelDetonationEnabled off the same channel burns as an inferno and the detonation count does not move."""
    x0, z0 = _prep_plot(t, "F")
    t.expect("fire", {"def": "Fire"})          # the blasts start vanilla Fire on purpose
    run = _line(x0 + 3, z0 + 4, 12)
    _fuel_run(t, run, "RM_Fluid_Astrofuel")
    # 3 cells off the run, inside the 3.9-cell blast/shove radius but past most of the Bomb damage (it falls off with
    # distance): at 2 cells the muffalo was shredded dead by the chain of blasts (L2 2026-10-15), so the throw could not
    # be read. A "fixture" expectation: the test's own subject, so its death is not an expected_contract_broken surprise.
    muf = _spawn_pawn_at(t, "Muffalo", x0 + 9, z0 + 7, faction="none")
    t.expect("fixture", {"id": muf})
    # With Empire Pursuit loaded the blast queues its investigating raid at once (the chain's own act, read by
    # utinni_blast_summons_raid): declared before the light, or the queue sweep ends the chain as a surprise (L2 2026-10-15).
    t.expect("incident", {"defName": "RaidEnemy"})

    def detonations():
        kv = _sc(t, FIRE_PROOF, "ProofReport", " ")
        try:
            return int(kv.split("detonations", 1)[1].split()[0]), kv
        except (IndexError, ValueError):
            return None, kv

    with _setting(t, "canalFireEnabled", True), _setting(t, "explosionIgnitesLiquidEnabled", True):
        with t.component("astrofuel_channel_detonates", toggle="astrofuelDetonationEnabled"):
            before, rep0 = detonations()
            if t._guard() and before is None:
                raise ExpectationFailed("UNMEASURED: the fire report carries no detonation count: %r" % rep0)
            pos0 = _pawn_xz(t, muf)
            if t._guard() and pos0 == (None, None):
                raise ExpectationFailed("UNMEASURED: the muffalo's start cell could not be read, so a throw cannot be told apart")
            lit = _light(t, *run[0])
            if t._guard() and not lit.startswith("LIT"):
                raise ExpectationFailed("UNMEASURED: the astrofuel channel was never lit: %s" % lit)
            t.wait_ticks(60)
            _expect_state(t, run, fill=0, what="detonated astrofuel channel")
            after, rep1 = detonations()
            pos1 = _pawn_xz(t, muf)
            if t._guard():
                _expect(after == before + 1, "detonations %r -> %r (%s)" % (before, after, rep1))
                _expect("queued 0" in rep1, "detonation schedule not drained 60 ticks on: %s" % rep1)
                if pos1 == (None, None):
                    raise ExpectationFailed("UNMEASURED: the muffalo died in the blast, so the throw cannot be read (%s)" % rep1)
                _expect(pos1 != pos0, "the muffalo beside the blast was not thrown: %r -> %r" % (pos0, pos1))
        with t.component("utinni_blast_summons_raid", beyond_toggle=True):
            st = _sc(t, RUT_BLAST, "ProofState", " ")
            if t._guard() and not st.startswith("STATE"):
                raise ExpectationFailed("UNMEASURED: RimUtinni Empire Pursuit is not loaded (ProofState: %r)" % st[:160])
            kv = _kv(st)
            now = int(_engine(t).get("ticksGame") or 0)   # flowworks_engine_state carries the clock
            if t._guard():
                _expect(kv.get("bound") == "True", "Empire Pursuit is not bound to the FlowWorks events: %s" % st)
                try:
                    last = int(kv.get("last", "-1"))
                except ValueError:
                    last = -1
                # one raid per map per day: a blast from an earlier run on this map leaves `last` long before this light
                if kv.get("queued") != "True" and now and 0 <= last < now - 300:
                    raise ExpectationFailed("UNMEASURED: the investigating raid is cooling down from an earlier blast on this "
                                            "map (last=%d, now=%d); rerun on a fresh map: %s" % (last, now, st))
                _expect(kv.get("queued") == "True", "the detonation queued no investigating raid: %s" % st)
            t.expect("raid", {}, until_tick=now + 600 if now else None)
            # the raiders are killed below, inside the window: a "fixture" (the test's own act), so their deaths are not an
            # expected_contract_broken surprise as a "hostile" expectation's are (L2 2026-10-15)
            t.expect("fixture", lambda p: bool(p.get("hostile")), until_tick=now + 600 if now else None)
            fired = _sc(t, RUT_BLAST, "ProofFireNow", " ")
            if t._guard():
                _expect(fired.startswith("FIRED True"), "the investigating raid did not fire: %s" % fired)
            t.wait_ticks(60)
            from modcheck import helpers as H
            H.kill_hostiles(t.session)
        _extinguish_all(t)
        _sc(t, RUT_BLAST, "ProofCancel", " ")
        slow = _line(x0 + 3, z0 + 11, 12)
        _fuel_run(t, slow, "RM_Fluid_Astrofuel")
        with t.component("astrofuel_detonation_off_burns", toggle="astrofuelDetonationEnabled"):
            with _setting(t, "astrofuelDetonationEnabled", False):
                before, _r = detonations()
                lit = _light(t, *slow[0])
                if t._guard() and not lit.startswith("LIT"):
                    raise ExpectationFailed("UNMEASURED: the OFF channel was never lit: %s" % lit)
                t.wait_ticks(90)
                after, rep2 = detonations()
                big = _things_at(t, INFERNO_FLAME, slow[:3])
                if t._guard():
                    _expect(after == before, "detonation OFF still detonated: %r -> %r" % (before, after))
                    _expect(len(big) >= 1, "detonation OFF: the channel is not burning as an inferno (%s)" % rep2)
        _extinguish_all(t)
        _sc(t, RUT_BLAST, "ProofCancel", " ")


PROPANE_FLUID, PROPANE_LIQUID, PROPANE_LAKE = "RM_Fluid_Propane", "RM_Liquid_Propane", "RM_PropaneShallow"
PROPANE_FILL = "RM_Fill_Propane_"      # RM_Fill_Propane_Trace / _Half / _Brim / _Superdeep (FlowWorks_PitFluidTerrain.xml)
SPILL_FILTH = "RM_Filth_LiquidSpill"   # RM_LiquidSpill's fallback filth: propane has no spillFilth of its own


def _fill_terrains(t, cells):
    """[(fill, terrain)] per cell: fill from the engine's report, terrain from rimworld/get_cell_info. L1 2026-10-21
    (HARNESS): jawa/flowworks_excavation_report carries NO terrain key (depth, fill, isExcavated, ...), so reading
    "terrain" there gave None on three RM_Fill_Propane_Trace cells and FAILed a fill that had worked."""
    out = []
    for x, z in cells:
        r = _rep(t, x, z)
        ci = t.bridge_call("rimworld/get_cell_info", x=x, z=z) or {}
        out.append((r.get("fill"), (ci.get("cell") or {}).get("terrainDefName")))
    return out


@suite.chain("fuel_moat_propane")
def fuel_moat_propane(t):
    """PROPANE_CANAL_WIRE_STILL_NO_FLUID (ea9a592d4), plot F. Propane got a canal FluidDef (RM_Fluid_Propane, Inferno):
    A2 a powered pump in pour mode empties a propane-holding tank into a dry D2 3-cell channel, and every wet cell takes
    RM_Fill_Propane_* terrain with no RM_Filth_LiquidSpill near the pump (before the FluidDef, it spilled);
    A3 a cut dug off a painted RM_PropaneShallow pond (natural lake terrain, classified by RM_FluidIdentity) forms a
    propane body and fills with RM_Fill_Propane_*, not water;
    A4 a D2 propane run never lights itself (2500 ticks, canal fire ON) nor under an EMP blast beside it, and an
    ordinary vanilla Fire (ProofTorch = GenSpawn ThingDefOf.Fire, the shipping Fire.SpawnSetup hook) on the soil beside
    its east end lights it as an inferno. live8 (2026-10-21) proved the lit half only with the ProofIgnite igniter."""
    x0, z0 = _prep_plot(t, "F")
    t.expect("fire", {"def": "Fire"})          # the torch, and the inferno's halo, are vanilla Fire on purpose
    ch = _line(x0 + 3, z0 + 1, 3)
    pump, tank, batt = (x0 + 4, z0 + 2), (x0 + 4, z0 + 3), (x0 + 8, z0 + 3)
    pond = (x0 + 12, z0 + 1, 4, 4)
    cut = _channel_from(x0 + 16, z0 + 2, 5)
    run = _line(x0 + 3, z0 + 9, 8)
    torch = (x0 + 11, z0 + 9)                  # soil, directly east of run[-1]
    emp = (x0 + 6, z0 + 11)                    # soil, two cells off the run's south bank
    _dig_run(t, ch, 2)
    _stage(t, "jawa/build_batch", ops="RM_LiquidPump:%d,%d;RM_LiquidTank:%d,%d" % (pump + tank), faction="player")
    with t.component("propane_tank_pours_into_channel", beyond_toggle=True):
        # Dump, not Store: the pump's POUR drains only a tank marked Dump (Building_LiquidPump summary). L1 2026-10-21
        # (HARNESS): a Store tank gave "running=True moved=0 tank=RM_Liquid_Propane:30000" for 1000 ticks.
        staged = _tank_set(t, tank, "Dump", PROPANE_LIQUID, 3 * UNITS_PER_LEVEL)
        _stage(t, "jawa/build_batch", ops="Battery:%d,%d" % batt, faction="player")
        bat = ((t.bridge_call("jawa/list_things", defName="Battery", rect=_rect(batt[0], batt[1], 1, 2), limit=2) or {})
               .get("things") or [{}])[0].get("id")
        t.bridge_call("jawa/battery_set", thing=bat, mode="setPct", value=1.0)
        k0 = _kv(_sc(t, NS_PROOF, "ProofPump", "%d,%d;pour" % pump))
        t.wait_ticks(1000)
        k1 = _kv(_sc(t, NS_PROOF, "ProofPump", "%d,%d" % pump))
        ft = _fill_terrains(t, ch)
        spill = t.bridge_call("jawa/list_things", defName=SPILL_FILTH, rect=_rect(x0, z0, 12, 7), limit=20) or {}
        _frame(t, x0 + 2, z0, 8, 6, "F_propane_pumped")
        if t._guard():
            wet = [(f, tr) for f, tr in ft if (f or 0) >= 1]
            if not wet and k1.get("running") != "True":
                raise ExpectationFailed("UNMEASURED: the pump never ran (%s -> %s; tank %s)" % (k0, k1, staged))
            _expect(len(wet) >= 1, "pour mode put no propane in the dry channel: %s pump %s" % (ft, k1))
            _expect(all(str(tr).startswith(PROPANE_FILL) for _, tr in wet), "pumped propane is not RM_Fill_Propane_*: %s" % ft)
            _expect(spill.get("success") is True and not spill.get("things"),
                    "propane spilled beside the pump: %r" % (spill.get("things") or spill))
    with t.component("propane_lake_cut_holds_propane", beyond_toggle=True):
        _stage(t, "jawa/set_terrain_batch", ops="%s:%s" % (PROPANE_LAKE, _rect(*pond)))
        _expect_body_fluid(t, pond[0] + 2, pond[1] + 2, PROPANE_FLUID)
        _dig_run(t, cut, 1)
        _wait(t, 6 * PULSE)
        ft = _fill_terrains(t, cut)
        _frame(t, pond[0], pond[1], 10, 4, "F_propane_lake_cut")
        if t._guard():
            # wet = any fill terrain, not F>=1: L1 2026-10-21 the D1 cut read F=0 on all 5 cells yet every one was
            # RM_Fill_Propane_Trace (a sub-level film; a dry cut is RM_Channel_Empty), so F>=1 called real liquid "nothing"
            wet = [(f, tr) for f, tr in ft if (f or 0) >= 1 or str(tr).startswith("RM_Fill_")]
            _expect(len(wet) >= 1, "the cut off the propane pond took nothing in 6 pulses: %s" % ft)
            _expect(all(str(tr).startswith(PROPANE_FILL) for _, tr in wet), "the lake cut holds another fluid: %s" % ft)
    _fuel_run(t, run, PROPANE_FLUID)
    with _setting(t, "canalFireEnabled", True), _setting(t, "explosionIgnitesLiquidEnabled", True):
        with t.component("propane_never_self_ignites", beyond_toggle=True):
            t.wait_ticks(2500)
            a = _things_at(t, INFERNO_FLAME, run) | _things_at(t, FLAME, run)
            _boom(t, emp, "EMP")
            t.wait_ticks(250)
            b = _things_at(t, INFERNO_FLAME, run) | _things_at(t, FLAME, run)
            st = _state(t, run)
            if t._guard():
                _expect(not a, "propane lit itself with no fire or blast: %s" % sorted(a))
                _expect(not b, "an EMP blast beside the run lit propane: %s" % sorted(b))
                _expect(all((f or 0) == 2 for _, f in st), "the unlit run lost propane: %s" % st)
        with t.component("propane_vanilla_fire_lights_inferno", beyond_toggle=True):
            tr = _sc(t, FIRE_PROOF, "ProofTorch", "%d,%d" % torch)
            if t._guard() and "fire=True" not in tr:
                raise ExpectationFailed("UNMEASURED: no vanilla Fire spawned beside the run: %r" % tr)
            t.wait_ticks(150)
            big = _things_at(t, INFERNO_FLAME, run)
            _frame(t, x0 + 2, z0 + 7, 11, 5, "F_propane_fire")
            if t._guard():
                _expect(run[-1] in big, "a vanilla Fire beside the run's east end did not light it as an inferno: %s" % sorted(big))
                _expect(len(big) == len(run), "inferno on %d/%d cells 150 ticks after the fire" % (len(big), len(run)))
        _extinguish_all(t)


@suite.chain("pit_prison_room")
def pit_prison_room(t):
    """SUPERDEEP_PRISON_ROOM_1 (73408b80e). A 3x3 D=4 pit ringed by open ground is its OWN room (split from the lip),
    a prisoner bed in it makes it a prison cell, a held hostile there can be captured DOWN by a colonist who never
    stands in the pit, and a warden job on a pit cell is served from a lip cell (the PathFollower patch's own gate).
    Each setting's OFF side is read through the same predicate. Not proven here: a full recruit/convert session
    from the lip, food dropped down (live walk owed), the width rule (C# selftest)."""
    x0, z0 = _prep_plot(t, "G")
    pit = _pit_cells(x0, z0)
    _dig_run(t, pit, 4)
    centre, west_edge, east_edge = pit[4], pit[1], pit[7]
    lip = (west_edge[0] - 1, west_edge[1])            # open ground touching the west edge cell
    far = (x0 + 1, centre[1])

    def room():
        return _kv(_sc(t, NS_PROOF, "ProofRoom", "%d,%d;%d,%d" % (centre + far)))

    with t.component("pit_is_its_own_room", toggle="superdeepRoomsEnabled"):
        k = room()
        if t._guard():
            _expect(k.get("split") == "True" and k.get("pitRoom") == "True" and k.get("edge") == "False",
                    "the pit is not its own enclosed room: %s" % k)
    with t.component("rooms_off_pit_joins_lip", toggle="superdeepRoomsEnabled"):
        with _setting(t, "superdeepRoomsEnabled", False):
            t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitRooms", method="RebuildAllMaps", args="")
            k = room()
            _expect(k.get("split") == "False" if t._guard() else None, "rooms OFF but the pit is still split: %s" % k)
        t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitRooms", method="RebuildAllMaps", args="")
    with t.component("prisoner_bed_makes_prison_cell"):
        _stage(t, "jawa/build_batch", ops="Bed:%d,%d,0" % pit[3], stuff="WoodLog", faction="player")
        beds = (t.bridge_call("jawa/list_things", defName="Bed", rect=_rect(pit[0][0], pit[0][1], 3, 3), limit=5) or {})
        bid = ((beds.get("things") or [{}])[0]).get("id")
        t.bridge_call("jawa/set_bed_owner_type", thing=bid, ownerType="Prisoner")
        # the raw ForOwnerType write does not re-derive the room's role the way the gizmo does (the tool says so):
        # rebuild rooms once so Room.IsPrisonCell is recomputed (live 19:47: prison=False with the bed in place)
        t.bridge_call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitRooms", method="RebuildAllMaps", args="")
        k = room()
        if t._guard():
            _expect(bid is not None and k.get("prison") == "True", "pit with a prisoner bed is not a prison cell: %s" % k)
    hid = _spawn_pawn_at(t, "Pirate", west_edge[0], west_edge[1], faction="hostile")
    t.bridge_call("jawa/pawn_gear", pawn=hid, action="clear")       # unarmed: nothing shoots the warden
    col = _spawn_pawn_at(t, "Colonist", far[0], far[1])
    with t.component("capture_down_from_the_lip", toggle="captureDownEnabled"):
        t.wait_ticks(60)
        v0 = _sc(t, NS_PROOF, "ProofCaptureDown", str(hid))
        # drafted: undrafted, the colonist fled the (unarmed) hostile and dropped the job (live 19:58: FleeAndCower)
        t.bridge_call("jawa/set_draft", pawnId=col, drafted=True)
        t.bridge_call("jawa/ordered_job", pawnId=col, jobDef="RM_CaptureDown", targetAId=hid,
                      targetBX=lip[0], targetBZ=lip[1])
        t.wait_ticks(900)
        v1 = _kv(_sc(t, NS_PROOF, "ProofCaptureDown", str(hid)))
        wx, wz = _pawn_xz(t, col)
        if t._guard():
            _expect(v0.startswith("VERDICT Allowed"), "capture-down not allowed on a held hostile in a prison pit: %s" % v0)
            _expect(v1.get("prisoner") == "True", "hostile not a prisoner after the capture-down job: %s" % v1)
            _expect((wx, wz) not in set(pit), "the warden ended IN the pit at %s" % ((wx, wz),))
    with t.component("capture_down_off", toggle="captureDownEnabled"):
        h2 = _spawn_pawn_at(t, "Pirate", east_edge[0], east_edge[1], faction="hostile")
        t.bridge_call("jawa/pawn_gear", pawn=h2, action="clear")
        t.wait_ticks(60)
        with _setting(t, "captureDownEnabled", False):
            v = _sc(t, NS_PROOF, "ProofCaptureDown", str(h2))
            _expect(v.startswith("VERDICT SettingOff") if t._guard() else None, "capture-down offered with the setting OFF: %s" % v)
    with t.component("warden_served_from_lip", toggle="wardenFromLipEnabled"):
        k = _kv(_sc(t, NS_PROOF, "ProofLip", "%s;%d,%d;PrisonerConvert" % ((col,) + centre)))
        if t._guard():
            _expect(k.get("serve") == "True" and k.get("kind") == "Interact" and k.get("lipInPit") == "False"
                    and float(k.get("dist", 99)) <= 6.0, "convert on a pit prisoner not served from a lip cell: %s" % k)
    with t.component("warden_lip_off", toggle="wardenFromLipEnabled"):
        with _setting(t, "wardenFromLipEnabled", False):
            k = _kv(_sc(t, NS_PROOF, "ProofLip", "%s;%d,%d;PrisonerConvert" % ((col,) + centre)))
            _expect(k.get("serve") == "False" if t._guard() else None, "lip service with the setting OFF: %s" % k)
    # Leave nothing behind: the drafted warden stayed on the lip beside the captured prisoner and, MEASURED 2026-10-06,
    # took fist bruises/cracks through the next THREE chains (liquid_pump, dig_finds, machinery_hoses (now machinery_pipes) read UNMEASURED on
    # colonist_injured_unexpectedly at (82,160)). Vanish: no death, no corpse, no death action.
    for pid in (hid, col, locals().get("h2")):
        if pid:
            t.bridge_call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")


@suite.chain("liquid_pump")
def liquid_pump(t):
    """FLOWWORKS_BUILD_PROGRAM_1 Phase 8 slice 1 (f3ab74a1b): a powered pump between a 3-cell D=2 water channel
    (F=2 each) and a 2x2 tank draws one level per 250-tick cycle into the tank as 10,000 units (1 kL, was 5 drums), and in pour mode returns
    them. Unpowered it does nothing; with liquidPumpEnabled off it does nothing even powered."""
    x0, z0 = _prep_plot(t, "D")
    ch = _line(x0 + 4, z0 + 6, 3)
    pump, tank, batt = (x0 + 5, z0 + 7), (x0 + 5, z0 + 8), (x0 + 9, z0 + 8)
    _dig_run(t, ch, 2)
    for x, z in ch:
        _fill(t, x, z, 2)
    _stage(t, "jawa/build_batch", ops="RM_LiquidPump:%d,%d;RM_LiquidTank:%d,%d" % (pump + tank), faction="player")

    def rd(mode=""):
        return _kv(_sc(t, NS_PROOF, "ProofPump", "%d,%d" % pump + ((";" + mode) if mode else "")))

    def level():
        return sum((f or 0) for _, f in _state(t, ch))

    with t.component("pump_unpowered_idle"):
        t.wait_ticks(600)
        k = rd()
        if t._guard():
            _expect(k.get("running") == "False" and k.get("moved") == "0" and level() == 6,
                    "an unpowered pump moved liquid: %s level %s" % (k, level()))
    _stage(t, "jawa/build_batch", ops="Battery:%d,%d" % batt, faction="player")
    bat = ((t.bridge_call("jawa/list_things", defName="Battery", rect=_rect(batt[0], batt[1], 1, 2), limit=2) or {})
           .get("things") or [{}])[0].get("id")
    t.bridge_call("jawa/battery_set", thing=bat, mode="setPct", value=1.0)
    with t.component("pump_draws_into_tank", toggle="liquidPumpEnabled"):
        t.wait_ticks(800)
        k, lv = rd(), level()
        if t._guard():
            moved = int(k.get("moved", 0))
            tk = k.get("tank", "none")
            _expect(k.get("running") == "True" and moved >= 2, "powered pump not drawing: %s" % k)
            _expect(lv == 6 - moved, "channel levels %s, expected 6 - moved %d" % (lv, moved))
            _expect(":" in tk and not tk.startswith("empty") and int(tk.split(":")[1]) == UNITS_PER_LEVEL * moved,
                    "tank %s after %d draws (10000 units/level)" % (tk, moved))
    with t.component("pump_off_idles", toggle="liquidPumpEnabled"):
        with _setting(t, "liquidPumpEnabled", False):
            m0 = rd().get("moved")
            t.wait_ticks(600)
            k = rd()
            _expect(k.get("moved") == m0 and k.get("running") == "False" if t._guard() else None,
                    "pump moved liquid with liquidPumpEnabled OFF: %s -> %s" % (m0, k))
    with t.component("pump_pours_back"):
        lv0 = level()
        rd("pour")
        t.wait_ticks(600)
        lv1 = level()
        _expect(lv1 > lv0 if t._guard() else None, "pour mode did not raise the channel: %s -> %s" % (lv0, lv1))


@suite.chain("bottle_revert")
def bottle_revert(t):
    """LIQUID_BOTTLE_LOOP_1 revert timer (73408b80e): three bottles of boiling water left for revertTicks (2500,
    PROVISIONAL) become fresh water; with bottleRevertEnabled off the clock does not run at all."""
    x0, z0 = _prep_plot(t, "F")
    cells = [(x0 + 4 + 2 * i, z0 + 6) for i in range(3)]
    area = _rect(x0 + 3, z0 + 5, 8, 3)
    _stage(t, "jawa/spawn_batch", ops=";".join("RM_Bottle_BoilingWater:%d,%d" % c for c in cells), stuff="Leather_Plain")

    def count(d):
        return len(((t.bridge_call("jawa/list_things", defName=d, rect=area, limit=20) or {}).get("things")) or [])

    # every colonist drafted for the waits: undrafted, one hauled a bottle out of the area (live 19:58: 2 of 3)
    cols = [p.get("id") for p in ((t.bridge_call("jawa/list_pawns", limit=200) or {}).get("pawns") or [])
            if p.get("isPlayer") and p.get("kindDef") == "Colonist"]
    for pid in cols:
        t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)

    with t.component("revert_off_holds", toggle="bottleRevertEnabled"):
        with _setting(t, "bottleRevertEnabled", False):
            t.wait_ticks(2750)
            if t._guard():
                _expect(count("RM_Bottle_BoilingWater") == 3, "boiling bottles changed with the revert OFF")
    with t.component("boiling_bottle_reverts_to_fresh", toggle="bottleRevertEnabled"):
        t.wait_ticks(2750)
        if t._guard():
            b, f = count("RM_Bottle_BoilingWater"), count("RM_Bottle_FreshWater")
            _expect(b == 0 and f == 3, "after 2750 ticks: %d boiling, %d fresh (want 0 / 3)" % (b, f))
    for pid in cols:
        t.bridge_call("jawa/set_draft", pawnId=pid, drafted=False)
    # a fresh bottle left lying is emptied into the nearest tank by a colonist (1 unit): it once read as a hose leak
    t.bridge_call("jawa/destroy_batch", rects=_rect(x0 + 3, z0 + 5, 8, 3), categories="All")


@suite.chain("wall_faces")
def wall_faces(t):
    """EXCAVATION_WALL_ART_1 carrier (a26e3d875): cutting D1..D4 cells adds wall-face geometry to their map section,
    and excavationWallFacesEnabled off hides the layer. The LOOK (four distinct bands) is the human sheet's."""
    x0, z0 = _prep_plot(t, "H")
    cells = [(x0 + 4 + 2 * i, z0 + 6) for i in range(4)]
    v0 = _kv(_sc(t, NS_PROOF, "ProofWallFaces", "%d,%d" % cells[0]))
    for i, (x, z) in enumerate(cells):
        _dig(t, x, z, i + 1)
    with t.component("cuts_draw_wall_faces", toggle="excavationWallFacesEnabled"):
        v1 = _kv(_sc(t, NS_PROOF, "ProofWallFaces", "%d,%d" % cells[0]))
        if t._guard():
            _expect(v1.get("visible") == "True" and int(v1.get("verts", 0)) > int(v0.get("verts", 0)),
                    "no wall-face geometry added by four cuts: before %s after %s" % (v0, v1))
    with t.component("wall_faces_off_hidden", toggle="excavationWallFacesEnabled"):
        with _setting(t, "excavationWallFacesEnabled", False):
            v2 = _kv(_sc(t, NS_PROOF, "ProofWallFaces", "%d,%d" % cells[0]))
            _expect(v2.get("visible") == "False" if t._guard() else None, "wall faces still visible OFF: %s" % v2)


def _dig_by_hand(t, pid, c):
    """One real canal cut by a colonist's RM_DigCanalJob (the only caller of RM_DigDiscoveryState.OnCut). Done means
    the cell's DEPTH rose (live 19:38: a designation query reading 'gone' proved nothing -- no cut had happened)."""
    d0 = _rep(t, *c).get("depth") or 0
    _stage(t, "jawa/designate_batch", action="add", designation="RM_DigCanal", rect=_rect(c[0], c[1], 1, 1))
    t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="RM_DigCanalJob", targetAX=c[0], targetAZ=c[1])
    for _ in range(16):
        t.wait_ticks(500)
        if (_rep(t, *c).get("depth") or 0) > d0:
            return True
    return False


def _finds(t):
    k = _kv(_sc(t, DIG_PROOF, "ProofReport", " ").replace(" | ", " ").replace("finds ", "finds=").replace("last ", "last="))
    return k


def _expect_cut_found(done, n0, n1, rep):
    """A forced cut must make a find, and a finished cut with none is a FAIL. (It read UNMEASURED until 2026-10-15:
    RM_DigDiscoveryState's rolledDepth is saved per cell and only grows, so a re-run on the same map cut an
    already-rolled depth; ProofResetRect now forgets the plot's rolled depths, DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS.)"""
    _expect(done, "the dig job never finished")
    if n0 is None or n1 is None:
        raise ExpectationFailed("UNMEASURED: ProofReport gave no finds count: %s -> %s (%s)" % (n0, n1, rep))
    _expect(int(n1) == int(n0) + 1, "a forced cut made no find (%s -> %s): %s" % (n0, n1, rep))


@suite.chain("dig_finds")
def dig_finds(t):
    """FLOWWORKS_QUARRY_DIGGING_1, FlowWorks half (c858125a8). One cell cut three times by a colonist, each cut armed
    with ProofReport("force") so the roll is certain: OFF finds nothing; ON a find lands that is never a made thing
    (components/plasteel); the letter follows digFindLetterEnabled. digFindsLocalOnly: ON side only (the find is a
    local mineable or a chunk); OFF draws from every ore, which no single draw can tell apart."""
    x0, z0 = _prep_plot(t, "A")
    c = (x0 + 10, z0 + 7)
    pid = _spawn_pawn_at(t, "Colonist", c[0] - 2, c[1])
    t.bridge_call("jawa/set_pawn_skill", pawn=pid, skill="Mining", level=10)
    t.bridge_call("jawa/set_work_priority", pawnId=pid, workType="Mining", priority=1)
    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=False)

    def letters():
        """Dig-find letters only ("Found while digging: X"): live 19:47 an unrelated 'Area revealed' letter arrived
        mid-row and read as a find letter with the setting OFF."""
        ls = (t.bridge_call("jawa/letter_list") or {}).get("letters") or []
        return sum(1 for x in ls if "Found while digging" in str((x.get("label") or {}).get("RawText", x.get("label"))))

    with t.component("finds_off_none", toggle="digFindsEnabled"):
        with _setting(t, "digFindsEnabled", False):
            n0 = _finds(t).get("finds")
            _sc(t, DIG_PROOF, "ProofReport", "force")
            done = _dig_by_hand(t, pid, c)
            n1 = _finds(t).get("finds")
            if t._guard():
                _expect(done, "the dig job never finished")
                _expect(n0 is not None and n0 == n1, "a find with digFindsEnabled OFF (None = no finds count): %s -> %s" % (n0, n1))
    with t.component("cut_turns_up_local_find", toggle="digFindsLocalOnly"):
        with _setting(t, "digFindLetterEnabled", False):
            l0, n0 = letters(), _finds(t).get("finds")
            _sc(t, DIG_PROOF, "ProofReport", "force")
            done = _dig_by_hand(t, pid, c)
            rep = _sc(t, DIG_PROOF, "ProofReport", " ")
            n1, l1 = _finds(t).get("finds"), letters()
            if t._guard():
                _expect_cut_found(done, n0, n1, rep)
                _expect(not any(m in rep for m in ("ComponentIndustrial", "ComponentSpacer", "Plasteel")),
                        "a made thing came out of the ground: %s" % rep)
                _expect(l1 == l0, "a letter with digFindLetterEnabled OFF (%d -> %d)" % (l0, l1))
    with t.component("first_find_sends_letter", toggle="digFindLetterEnabled"):
        l0, n0 = letters(), _finds(t).get("finds")
        armed = _sc(t, DIG_PROOF, "ProofReport", "force")
        done = _dig_by_hand(t, pid, c)
        rep = _sc(t, DIG_PROOF, "ProofReport", " ")
        l1, n1 = letters(), _finds(t).get("finds")
        if t._guard():
            _expect_cut_found(done, n0, n1, rep)
            if "Chunk" in rep.split("last", 1)[-1]:
                t.upstream_reason = "UNMEASURED: the find was a rock chunk (no letter by design): %s" % rep
                t.upstream_failed = True
                return
            if l1 == l0 + 1:
                return
            # No letter. It is owed only for a FIRST find of a material (RM_DigDiscovery: the Scribed found-list),
            # and the found-list is recorded in the SAME condition that sends the letter, so its growth cannot judge
            # the letter (review 2026-10-11). The one first-ness read that does not depend on the letter: a MAP with
            # NOTHING found yet (first-found 0 when armed; the list is per map) makes every non-chunk find a first
            # find -> FAIL. With earlier finds on this map the material may be a repeat (no letter is right) -> UNMEASURED.
            part = armed.split("first-found", 1)
            try:
                f0 = int(part[1].split("|", 1)[0]) if len(part) == 2 else None
            except ValueError:
                f0 = None
            if f0 is None:
                raise ExpectationFailed("UNMEASURED: no letter, and ProofReport gave no first-found count: %r" % armed)
            if f0 > 0:
                raise ExpectationFailed("UNMEASURED: no letter, but this map already holds %d first finds, so the "
                                        "material may be a repeat: %s" % (f0, rep))
            _expect(False, "no letter for a first find on a map with nothing found yet (%d -> %d): %s" % (l0, l1, rep))


# =============================================================== LIQUID MACHINERY (3e473f37c)
# Rows owed by Transient/belt_fwmachinery_20261005.md. Wired here: the hose net (the one mechanism every other
# machine rides) and the build-anywhere placement law. Declared, not proven, with the reason in the row:
# found-works ruins (worldgen: two fresh maps), pipe adapters (VE PipeSystem is on no test list). NOT wired yet
# (owed, each needs its own powered tank pair + a day of ticks): the converter rates of each still / found work,
# the cargo tank's minify round trip, the ship distiller.

def _tank_text(t, x, z):
    r = t.bridge_call("jawa/inspect_string", defName="RM_LiquidTank", rect=_rect(x, z, 2, 2), limit=2) or {}
    return " ".join(str(th.get("inspect") or "") for th in (r.get("things") or []))


@suite.chain("machinery_pipes")
def machinery_pipes(t):
    """Phase 8 slice 2: a powered pump on a 3-cell water channel feeds a tank 5 universal-pipe cells away (not touching
    the pump); with universalPipesEnabled off the far tank gains nothing more. (Was machinery_hoses, with the pipe called
    RM_LiquidHose, until the hose port renamed it, 2026-10-11.)"""
    x0, z0 = _prep_plot(t, "B")
    ch = _line(x0 + 2, z0 + 6, 3)
    pump, batt = (x0 + 3, z0 + 7), (x0 + 1, z0 + 8)
    pipe = [(x0 + 4 + i, z0 + 7) for i in range(5)]
    tank = (x0 + 9, z0 + 7)
    _dig_run(t, ch, 2)
    for x, z in ch:
        _fill(t, x, z, 2)
    ops = ["RM_LiquidPump:%d,%d" % pump, "RM_LiquidTank:%d,%d" % tank, "Battery:%d,%d" % batt] + \
          ["RM_UniversalPipe:%d,%d" % c for c in pipe]
    _stage(t, "jawa/build_batch", ops=";".join(ops), faction="player")
    bat = ((t.bridge_call("jawa/list_things", defName="Battery", rect=_rect(batt[0], batt[1], 1, 2), limit=2) or {})
           .get("things") or [{}])[0].get("id")
    t.bridge_call("jawa/battery_set", thing=bat, mode="setPct", value=1.0)
    with t.component("pipe_feeds_far_tank", toggle="universalPipesEnabled"):
        before = _tank_text(t, *tank)
        t.wait_ticks(800)
        after = _tank_text(t, *tank)
        if t._guard():
            _expect(after != before and "water" in after.lower(), "far tank unchanged through the pipe: %r -> %r" % (before, after))
    with t.component("pipes_off_far_tank_idle", toggle="universalPipesEnabled"):
        with _setting(t, "universalPipesEnabled", False):
            a0 = _tank_text(t, *tank)
            t.wait_ticks(600)
            a1 = _tank_text(t, *tank)
            if t._guard():
                _expect(bool(a0), "no RM_LiquidTank answered inspect_string at %s" % (tank,))
                _expect(a0 == a1, "far tank kept gaining with pipes OFF: %r -> %r" % (a0, a1))


@suite.chain("machinery_found_works")
def machinery_found_works(t):
    """Campaign law: industrial works are FOUND. A kludged desal plant is refused on open ground by default and
    placeable there with industrialWorksBuildAnywhere on. Ruins/ruin stock are worldgen and pipe adapters need VE
    PipeSystem: owed components (UNMEASURED, no toggle claim)."""
    x0, z0 = _prep_plot(t, "C")
    rect = _rect(x0 + 8, z0 + 5, 1, 1)

    def can():
        r = t.bridge_call("jawa/build_check", **{"def": "RM_DesalPlant_Kludged", "rect": rect})
        return ((r or {}).get("cells") or [{}])[0]
    with t.component("works_only_over_ruin", toggle="industrialWorksBuildAnywhere"):
        c = can()
        _expect(c.get("canPlace") is False if t._guard() else None, "kludged desal placeable on open ground: %s" % c)
    with t.component("build_anywhere_on", toggle="industrialWorksBuildAnywhere"):
        with _setting(t, "industrialWorksBuildAnywhere", True):
            c = can()
            _expect(c.get("canPlace") is True if t._guard() else None, "build-anywhere ON but still refused: %s" % c)
    # owed, no toggle= (a declared toggle on an UNMEASURED-by-construction row read as floor coverage); the three
    # toggles are named in validation.EXTENSION_TOGGLES_OWED
    for name, why in (("ruins_mapgen", "liquidWorksRuinsEnabled: worldgen, needs two fresh shore maps"),
                      ("ruin_stock_mapgen", "liquidWorksRuinStockEnabled: worldgen, needs a fresh shore map"),
                      ("pipe_adapters", "pipeAdaptersEnabled: VE PipeSystem is on no test list")):
        with _owed(t, name, why):
            pass


HEAT_PROOF = "RimMandrake.FlowWorks.RM_LiquidHeatProof"


def _heat(t, c):
    """ProofHeat at one cell: kind (+1 hot / -1 cold / 0), room temp, outdoor flag, last interval's counters."""
    return _kv(_sc(t, HEAT_PROOF, "ProofHeat", "%d,%d" % c))


def _hut(t, x0, z0, terrain):
    """A 7x7 steel-walled, fully roofed hut whose 5x5 floor holds a 3x3 patch of `terrain`. Returns a floor cell."""
    ring = [(x0 + i, z0) for i in range(7)] + [(x0 + i, z0 + 6) for i in range(7)] + \
           [(x0, z0 + j) for j in range(1, 6)] + [(x0 + 6, z0 + j) for j in range(1, 6)]
    _stage(t, "jawa/set_terrain_batch", ops="%s:%s" % (terrain, _rect(x0 + 2, z0 + 2, 3, 3)))
    _stage(t, "jawa/spawn_batch", ops=";".join("Wall:%d,%d" % c for c in ring), stuff="Steel")
    _stage(t, "jawa/set_roof_batch", ops="RoofConstructed:%s" % _rect(x0, z0, 7, 7))
    return (x0 + 1, z0 + 1)


@suite.chain("liquid_heat")
def liquid_heat(t):
    """LIQUID_HEAT_PUSH_1 (FL-1 / X-8), DRAFT criteria, never run live yet. Three identical roofed huts, each over a
    3x3 pool: boiling water (RM_WaterBoilingShallow, LiquidDef hot), icy water (RM_WaterFrigidShallow, LiquidDef
    cold) and plain WaterShallow (the control). After ~5 intervals the boiling hut reads warmer than the control and
    the icy hut colder; with liquidHeatPushEnabled off the boiling hut's lead over the control does not grow. An OPEN
    boiling patch identifies as hot but reads outdoor (vanilla Room.PushHeat ignores outdoor rooms, MEASURED).
    Not staged: a pit FLOODED with a hot liquid -- no hot canal FluidDef ships yet (follow-up item), so
    PIT_TEMPERATURE_SOFTENING_1's coupling to a hot pit is proven only by the C# identity path, not live."""
    x0, z0 = _prep_plot(t, "C")
    boil = _hut(t, x0 + 1, z0 + 3, "RM_WaterBoilingShallow")
    icy = _hut(t, x0 + 9, z0 + 3, "RM_WaterFrigidShallow")
    ctrl = _hut(t, x0 + 17, z0 + 3, "WaterShallow")
    open_boil = (x0 + 12, z0 + 12)
    _stage(t, "jawa/set_terrain_batch", ops="RM_WaterBoilingShallow:%s" % _rect(open_boil[0], open_boil[1], 1, 1))
    _sc(t, HEAT_PROOF, "ProofRescan", " ")
    with t.component("liquid_heat_kinds", toggle="liquidHeatPushEnabled"):
        kb, ki, kc, ko = (_heat(t, (x0 + 4, z0 + 6)), _heat(t, (x0 + 12, z0 + 6)), _heat(t, (x0 + 20, z0 + 6)),
                          _heat(t, open_boil))
        if t._guard():
            _expect(kb.get("kind") == "1" and ki.get("kind") == "-1" and kc.get("kind") == "0",
                    "pool kinds boiling/icy/plain: %s / %s / %s" % (kb, ki, kc))
            _expect(ko.get("kind") == "1" and ko.get("outdoor") == "True", "open boiling patch: %s" % ko)
            _expect(kb.get("outdoor") == "False", "the boiling hut is not an enclosed room: %s" % kb)
    with t.component("liquid_heat_warms_and_chills", toggle="liquidHeatPushEnabled"):
        t.wait_ticks(1250)
        b, i, c = _heat(t, boil), _heat(t, icy), _heat(t, ctrl)
        if t._guard():
            if any(h.get("temp") is None for h in (b, i, c)):
                raise ExpectationFailed("UNMEASURED: ProofHeat gave no temperature: %s / %s / %s" % (b, i, c))
            tb, ti, tc = float(b["temp"]), float(i["temp"]), float(c["temp"])
            _expect(tb > tc + 3.0, "boiling hut %.1f C not warmer than the control %.1f C" % (tb, tc))
            _expect(ti < tc - 3.0, "icy hut %.1f C not colder than the control %.1f C" % (ti, tc))
            _expect(tb <= 50.5, "boiling hut %.1f C passed the 50 C target" % tb)
    with t.component("liquid_heat_off_is_inert", toggle="liquidHeatPushEnabled"):
        with _setting(t, "liquidHeatPushEnabled", False):
            b0, c0 = _heat(t, boil), _heat(t, ctrl)
            t.wait_ticks(1250)
            b1, c1 = _heat(t, boil), _heat(t, ctrl)
            if t._guard():
                if any(h.get("temp") is None for h in (b0, c0, b1, c1)):
                    raise ExpectationFailed("UNMEASURED: ProofHeat gave no temperature: %s %s %s %s" % (b0, c0, b1, c1))
                lead0 = float(b0.get("temp", "nan")) - float(c0.get("temp", "nan"))
                lead1 = float(b1.get("temp", "nan")) - float(c1.get("temp", "nan"))
                _expect(lead1 <= lead0 + 0.5, "boiling hut kept gaining with the setting OFF: lead %.1f -> %.1f"
                        % (lead0, lead1))
                _expect(b1.get("warmed") == "0", "rooms still warmed with the setting OFF: %s" % b1)
    t.bridge_call("jawa/destroy_batch", rects=_rect(x0, z0, PW, PH), categories="All")
    _stage(t, "jawa/set_roof_batch", ops=_rect(x0, z0, PW, PH), roofDef="None")
