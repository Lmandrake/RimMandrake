"""validation.py -- modcheck suite for RimMandrake: Graffiti Framework
(mandrake.rm.graffiti).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Graffiti

Grounded in the mod's actual source, read whole before writing this:
`RM_GraffitiMod.cs` for the FOUR real settings toggles (`paintingEnabled`,
`paintIntervalTicks`, `viewerReactionEnabled`, `breachBiasEnabled`);
`JobDriver_PaintGraffiti.cs` for the real mechanism under test (a
goto-then-periodic-`FilthMaker.TryMakeFilth` toil, gated on
`RM_GraffitiSettings.paintIntervalTicks`); `JoyGiver_PaintGraffiti.cs` /
`JobGiver_GraffitiPaintingSpree.cs` for the TWO places `paintingEnabled` is
actually checked (both `TryGiveJob` overrides, nowhere else);
`Defs/ThinkTreeDefs_Graffiti.xml` for the `RM_GraffitiPaintingSpreeState`
hook actually wired into `Humanlike_PostMentalState` (food/rest come
before the paint giver, thresholds 0.05/0.15 -- a fresh colonist clears
both); `ThoughtWorker_ViewedGraffitiMark.cs` / `BreachBiasHook.cs` for
`viewerReactionEnabled` / `breachBiasEnabled`'s real gates; and
`ThingDefs_Graffiti.xml` for what this mod actually SHIPS.

This mod has NO DebugAction and NO Log.* call anywhere in Graffiti/Source/
(grepped whole -- `ModExtension_Graffiti.cs`'s own comment independently
confirms it: "there are zero Log. calls in the whole of Graffiti/Source/").
Unlike Pits/FluidCanals, there is no purpose-built bridge read-back
channel here at all -- every component below reads back through a real
bridge primitive instead (`jawa/ordered_job`, `jawa/pawn_force_mental_
break`, `jawa/list_things`), never a log tag.

A REAL, MOD-SPECIFIC FLOOR GAP -- `viewerReactionEnabled` and
`breachBiasEnabled` gate mechanisms with NO LIVE CONTENT anywhere in this
mod to exercise them:
  - `ThoughtWorker_ViewedGraffitiMark.CurrentStateInternal` only ever runs
    for a `ThoughtDef` whose `workerClass` IS that class -- and this mod
    ships no `ThoughtDefs_Graffiti.xml` at all (checked: the Defs/ folder
    has no such file). No `ThoughtDef` anywhere references this worker, so
    the method is DEAD CODE today, not merely untested -- confirmed by the
    mod's own `About.xml`: "Nothing reads these fields yet."
  - `BreachBiasHookMod.Postfix` (the Harmony patch on `BreachingGrid.
    FindBuildingToBreach`) IS live and runs on every real breach, but its
    `FindLuredBuilding` scan only ever matches a Thing whose
    `ModExtension_Graffiti.breachLure == true` -- and none of the four
    shipped `ThingDef`s (`RM_Graffiti_Vandal`/`Scratches`/`TallyMarks`/
    `WarningGlyph`) carries a `<modExtensions>` block at all (checked:
    `ThingDefs_Graffiti.xml` has none). The postfix's early-return on
    `!breachBiasEnabled` is reachable; everything past it is not, with
    this mod's own shipped content.
  Building a real functional test for either would require a test-only
  `ThingDef`/`ThoughtDef` this mod does not ship (the `RM_FluidSpring_
  Test` precedent in FluidCanals) -- out of scope for a validation.py-only
  pass. Both toggles are therefore UNCOVERED -- see the "NOT a chain"
  register at the end of this file (BENCH edit 2026-09-13: the draft's
  set_setting write+read-back components were shelved because they fail
  every run on the KNOWN static-field bridge limitation,
  BRIDGE_STATIC_SETTINGS_FIELDS_1, which would hold this mod un-GREEN on
  the wrong culprit). Flagged, not faked -- same practice as Pits' own two
  uncovered toggles and RimProperty/validation.py's this same wave.

WHY `jawa/ordered_job` AND `jawa/pawn_force_mental_break` (not a debug
action) ARE THE VERBS HERE: `jawa/ordered_job` dispatches
`RM_PaintGraffitiJob` directly by JobDef, bypassing `JoyGiver_
PaintGraffiti`'s own cell-search/reservation gate entirely (same reasoning
RimProperty/validation.py uses for its own two `jawa/ordered_job`
chains this wave) -- this proves the DRIVER's periodic-paint mechanism,
not the joy-giver's own cell choice. `jawa/pawn_force_mental_break`
(`MentalBreaker.TryDoMentalBreak`) is the one component that reaches
`JobGiver_GraffitiPaintingSpree.TryGiveJob` (and therefore
`paintingEnabled`) for real -- there is no way to force the ordinary joy
path (`JoyGiver_PaintGraffiti`) directly, so `paintingEnabled` is proven
only via the mental-break route.

Still not proven / likely first-live-run corrections:
  1. `mental_break_assigns_paint_job`'s `wait_ticks(700)` is an estimate
     (goto a couple of cells + up to `paintIntervalTicks`=250 ticks before
     the first `IsHashIntervalTick` fire), not measured against real tick
     rates.
  2. That component also assumes the single spawned `Wall` leaves at least
     one of its four cardinal neighbor cells `Standable`/reachable/
     unreserved for `GraffitiJobUtility.TryFindWallMarkCell` to pick --
     true on an empty cleared area, unmeasured live.
  3. `jawa/spawn_batch`'s `stuff` parameter (needed for `Wall`, a
     MadeFromStuff def) is passed via the `bridge_call` escape valve, not
     `t.spawn` (whose signature has no `stuff` param) -- so this one
     spawn is not teardown-TRACKED by the library the way `t.spawn`'s own
     spawns are. Harmless in practice: every chain in this suite clears
     its own anchor rect via `clear_area` before using it, which sweeps
     by RECT (`jawa/destroy_batch`), not by tracked id.
  4. `paints_mark_at_interval`'s `waitTicks=450` on `jawa/ordered_job`
     assumes no goto time worth mentioning (target is 2 cells from spawn)
     plus one `paintIntervalTicks`=250-tick cycle; not measured.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Graffiti")
suite.toggles = ["paintingEnabled", "paintIntervalTicks",
                 "viewerReactionEnabled", "breachBiasEnabled"]

VANDAL_DEF = "RM_Graffiti_Vandal"


def _mark_count_in_rect(t, rect):
    """`jawa/list_things` count of VANDAL_DEF things in `rect` -- the
    RimProperty/validation.py precedent this wave for a generic
    def-in-area read-back with no mod-specific log tag to lean on."""
    r = t.bridge_call("jawa/list_things", defName=VANDAL_DEF, rect=rect)
    rows = (r or {}).get("things") or []
    return len(rows)


@suite.chain("forced_paint_job")
def forced_paint_job(t):
    """Order a plain colonist directly onto `RM_PaintGraffitiJob` via
    `jawa/ordered_job` (bypassing `JoyGiver_PaintGraffiti`'s own cell
    search -- see module docstring) and prove `JobDriver_PaintGraffiti`'s
    periodic toil actually leaves a mark, on schedule with the shipped
    default `paintIntervalTicks`=250."""
    t.clear_area(size=20)
    x, z = t.anchor
    mark_x, mark_z = x + 2, z
    walker = t.spawn_pawn("Colonist", hostile=False)
    rect = "%d,%d,6,6" % (mark_x - 3, mark_z - 3)

    with t.component("paints_mark_at_interval", toggle="paintIntervalTicks"):
        before = _mark_count_in_rect(t, rect)
        r = t.bridge_call("jawa/ordered_job", pawnId=walker,
                          jobDef="RM_PaintGraffitiJob",
                          targetAX=mark_x, targetAZ=mark_z,
                          waitTicks=450, timeoutSeconds=30)
        if t._guard():   # no-op under the offline declaration probe --
                         # see FluidCanals/validation.py's own note on why.
            accepted = bool((r or {}).get("accepted"))
            running = bool((r or {}).get("nowRunningRequested"))
            if not (accepted and running):
                raise ExpectationFailed(
                    "jawa/ordered_job RM_PaintGraffitiJob was not accepted "
                    "and running after the wait: %r" % r)
            after = _mark_count_in_rect(t, rect)
            if after <= before:
                raise ExpectationFailed(
                    "no new %s appeared near (%d,%d) after the paint job "
                    "ran (before=%d after=%d)"
                    % (VANDAL_DEF, mark_x, mark_z, before, after))
        t.screenshot()


@suite.chain("mental_break_spree")
def mental_break_spree(t):
    """Force `RM_GraffitiPaintingSpreeBreak` on a plain colonist -- the
    ONE reachable path to `JobGiver_GraffitiPaintingSpree.TryGiveJob`, and
    therefore the only reachable proof of `paintingEnabled` (see module
    docstring) -- and prove a mark appears near the one wall this chain
    builds."""
    t.clear_area(size=20)
    x, z = t.anchor
    wall_x, wall_z = x + 3, z
    t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (wall_x, wall_z),
                 stuff="Steel")
    walker = t.spawn_pawn("Colonist", hostile=False)     # lands at (x, z),
                                                          # 3 cells from the wall
    rect = "%d,%d,6,6" % (wall_x - 3, wall_z - 3)

    with t.component("mental_break_assigns_paint_job", toggle="paintingEnabled"):
        before = _mark_count_in_rect(t, rect)
        r = t.bridge_call("jawa/pawn_force_mental_break", pawn=walker,
                          breakDef="RM_GraffitiPaintingSpreeBreak")
        if t._guard():   # see forced_paint_job's own note on this guard
            started = bool((r or {}).get("started"))
            after_state = (r or {}).get("mentalStateAfter")
            if not started or after_state != "RM_GraffitiPaintingSpreeState":
                raise ExpectationFailed(
                    "jawa/pawn_force_mental_break did not start "
                    "RM_GraffitiPaintingSpreeState: %r" % r)
        t.wait_ticks(700)
        if t._guard():
            after = _mark_count_in_rect(t, rect)
            if after <= before:
                raise ExpectationFailed(
                    "no new %s appeared near the wall at (%d,%d) during "
                    "the forced spree (before=%d after=%d)"
                    % (VANDAL_DEF, wall_x, wall_z, before, after))
        t.screenshot()


# NOT a chain: `viewerReactionEnabled` and `breachBiasEnabled` are UNCOVERED,
# deliberately (edited by BENCH before the first live run, 2026-09-13). The
# draft proved them via `t.set_setting` write+read-back, accepting a
# near-certain failure: RM_GraffitiMod.cs declares both fields
# `public static` (line ~31), the EXACT shape `rimworld/update_mod_settings`
# refused live for Pits ("reflection walks INSTANCE fields"). A component
# that fails every run on a KNOWN bridge limitation keeps this mod
# permanently un-GREEN and blocks its playtest gate on the wrong culprit --
# the gap is the bridge tool's, already recorded on
# MOD_VALIDATION_PIT_PILOT_1 and now BRIDGE_STATIC_SETTINGS_FIELDS_1. When
# that tool learns static fields, restore the two write+read-back
# components here (the draft's shape was right); until then this mirrors
# Pits' own two uncovered toggles: registered, not faked.
