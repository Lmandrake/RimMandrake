"""validation.py -- modcheck suite for RimMandrake Fluid Canals
(mandrake.rm.fluidcanals).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale, the same
regression guard Pits/validation.py cites). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run FluidCanals

Grounded in the mod's actual source, read whole before writing this:
`RimMandrakeFluidCanalsMod.cs` for the three real settings toggles
(`canalFlowEnabled`, `flowRateMultiplier`, `floodVolumeMultiplier`) and
their shipped defaults; `FluidCanalsDebugActions.cs` for the two ToolMap
debug actions this suite drives (`Instant-dig canal at cell`,
`Report cell (RAW)`) and their own `[RMFluidCanalsDebug] INSTANT_DIG` /
`REPORT_CELL` log lines -- the mod's own bridge-testable proxy for a labor
job that otherwise costs `JobDriver_DigCanal.BaseWorkAmount` = 3200 work
ticks to complete; `CompFluidReservoir.cs`/`CompProperties_
FluidReservoir.cs` for the prime/drip/re-flood state machine actually
under test; `Defs/ThingDefs/FluidCanal_ThingDefs.xml` for `RM_FluidSpring_
Test`, the v1 test-only source building this suite spawns (the mod's own
docstring calls it "not a finished piece of content").

NOT exercised by this suite, deliberately:
  - `WorkGiver_DigCanal`/`JobDriver_DigCanal` (the real player labor path):
    `FluidCanalsDebugActions.InstantDig` exists FOR this reason -- it is
    this mod's OWN bridge-testable proxy so a live proof does not depend
    on a colonist actually walking over and finishing a multi-thousand-
    work-unit dig job (same reasoning the Pits pilot used for its own
    arm/uncover debug actions instead of a colonist's real gizmo click).
  - The OFF / non-default value of all three settings: `RimMandrakeFluidCanalsSettings`'s
    fields are `public static` (`RimMandrakeFluidCanalsMod.cs`) -- the
    EXACT shape that made `t.set_setting` fail against Pits' own
    `PitsSettings` on its first live run 2026-09-12 ("the bridge's
    reflection walks INSTANCE fields on the ModSettings object ... this
    mod's actual values live on the class, not the instance" -- Pits/
    validation.py's own note, and independently re-confirmed by
    RimProperty/validation.py and Ninefold/validation.py hitting the same
    thing this same wave). Assumed to fail here too by structural analogy,
    not independently measured -- flagged rather than attempted. Every
    component below therefore exercises its toggle only at the SHIPPED
    DEFAULT (`canalFlowEnabled=True`, `flowRateMultiplier=1.0`,
    `floodVolumeMultiplier=1.0`), satisfying the floor (spec: "every
    toggle has at least one component") without claiming the off/scaled
    path is proven.

Still not proven / likely first-live-run corrections:
  1. The debug-action PATH (`Actions\\T: <label>`) is copied from Pits'
     own MEASURED 2026-09-12 finding, not independently measured for this
     mod -- if it differs here, `list_debug_action_children("Actions")`
     (Pits' own recovery method) is the fix.
  2. `clear_area` sweeps TRACKED THINGS (spec Sec1b); it has no way to
     revert a terrain change. `RM_Channel_Empty`, carved by `Instant-dig
     canal at cell`, is not a spawned Thing the library tracks for
     teardown -- this chain may leave a real dug-channel tile on the
     quicktest map after the run. Untested whether `jawa/destroy_batch`
     (`categories="All"`) reverts terrain as a side effect; if not, a
     later mod's chain re-using this same anchor should still be fine
     (its own `clear_area` only clears THINGS, and terrain is not part of
     any of its own expectations) but this is worth confirming once.
  3. `drip_interval_matches_default_multiplier` assumes
     `Find.TickManager.TicksGame` does not advance between the instant-dig
     and the read-back debug action fired right after it (no `wait_ticks`
     between them) -- consistent with the library's "time stays paused
     except in wait_ticks" discipline (spec Sec1b), but not measured for
     this mod's specific two-debug-actions-in-a-row shape.
"""
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("FluidCanals")
suite.toggles = ["canalFlowEnabled", "flowRateMultiplier", "floodVolumeMultiplier"]

SPRING_DEF = "RM_FluidSpring_Test"


def _debug(t, label, x, z):
    """Every FluidCanalsDebugActions.cs action, ToolMap, targeted by (x, z)
    -- path convention copied from Pits' own MEASURED finding (see module
    docstring point 1)."""
    return t.bridge_call("rimworld/execute_debug_action",
                         path="Actions\\T: " + label, x=x, z=z)


def _report_line(t, x, z):
    """Fire `Report cell (RAW)` at (x, z) and return the raw REPORT_CELL
    log line text (or None), for a custom numeric field comparison beyond
    what a plain `expect_log_contains(field=value)` substring match can
    do."""
    _debug(t, "Report cell (RAW)", x, z)
    r = t.bridge_call("jawa/drain_log", limit=200, contains="REPORT_CELL")
    msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
    return msgs[-1] if msgs else None


def _parse_int_field(line, field):
    if line is None:
        return None
    m = re.search(r"%s=(-?\d+)" % re.escape(field), line)
    return int(m.group(1)) if m else None


@suite.chain("reservoir_flow")
def reservoir_flow(t):
    """Spawn a test spring, dig one adjacent canal cell with the mod's own
    instant-dig debug proxy, and read the reservoir + flood state back
    through its own REPORT_CELL line -- three components sharing one
    setup, covering all three settings toggles at their shipped defaults
    (see module docstring on why not at any other value)."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn(SPRING_DEF, count=1, at="line")           # lands at (x, z)
    dig_x, dig_z = x + 1, z                            # adjacent (8-way rect
                                                        # covers it -- CompFluidReservoir.
                                                        # Notify_CanalCellOpened)

    with t.component("reservoir_primes", toggle="canalFlowEnabled"):
        _debug(t, "Instant-dig canal at cell", dig_x, dig_z)
        t.expect_log_contains("INSTANT_DIG", field="terrainNow",
                              value="RM_Channel_Empty")
        _debug(t, "Report cell (RAW)", x, z)
        t.expect_log_contains("REPORT_CELL", field="primed", value="True")
        t.expect_log_contains("REPORT_CELL", field="fluid", value="RM_Fluid_Water")
        t.screenshot()

    with t.component("reflood_volume_matches_default_multiplier",
                     toggle="floodVolumeMultiplier"):
        # Prime() fires one re-flood immediately (CompFluidReservoir.Prime);
        # its volume is ScaledVolume(reFloodVolume) = 60 * floodVolumeMultiplier
        # (shipped default 1.0) -- Flood_FluidCanal.RemainingVolume should
        # read back exactly "60.0" (CompProperties_FluidReservoir's
        # reFloodVolume default, "F1"-formatted by the debug action).
        _debug(t, "Report cell (RAW)", dig_x, dig_z)
        t.expect_log_contains("REPORT_CELL", field="spawned", value="True")
        t.expect_log_contains("REPORT_CELL", field="remainingVolume", value="60.0")
        t.screenshot()

    with t.component("drip_interval_matches_default_multiplier",
                     toggle="flowRateMultiplier"):
        # nextDripTick = nowTick + ScaledInterval(dripIntervalTicks), and
        # ScaledInterval(2500) at the shipped default flowRateMultiplier=1.0
        # is exactly 2500 (CompFluidReservoir.ScaledInterval). Both fields
        # are on the reservoir's own REPORT_CELL line; re-fire fresh here
        # rather than trust the line already consumed above.
        line = _report_line(t, x, z)
        if t._guard():          # no-op under the offline declaration probe
                                 # (components_declared()/lint) -- see
                                 # RimProperty/validation.py's own note on
                                 # why this guard is required for a raise
                                 # outside the expect_* verbs.
            now = _parse_int_field(line, "nowTick")
            nxt = _parse_int_field(line, "nextDripTick")
            if now is None or nxt is None or nxt - now != 2500:
                raise ExpectationFailed(
                    "nextDripTick - nowTick expected exactly 2500 at the "
                    "shipped default flowRateMultiplier=1.0, got now=%r "
                    "nextDripTick=%r (line=%r)" % (now, nxt, line))
        t.screenshot()
