"""validation.py -- modcheck suite for RimMandrake Pits (mandrake.rm.pits).

MOD_VALIDATION_PIT_PILOT_1. Never deployed (deploy_custom_mods.py excludes
`.py` wholesale -- see modcheck's own selftest for the regression guard on
that finding). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Pits

DRAFT, NOT YET RUN LIVE (2026-09-12) -- see MOD_VALIDATION_PIT_PILOT_1's
item file for exactly why (the owner's live campaign was up throughout this
build). Everything below is grounded in the mod's actual source --
`PitsMod.cs` for the four real settings toggles, `PitsSettings`'s field
names and defaults; `PitDebugActions.cs` for the exact debug-action labels,
its `CAT = "RMPits"` category, and its `[RMPitsDebug] TAG ...` log lines,
which are this mod's OWN purpose-built read-back channel; and
`Building_OpenPit.Spring()` for the one fact a validator must not get
wrong: a captured pawn is `DeSpawn`'d and moved into `innerContainer` --
CONTAINED, not merely relocated. `expect_in_cell_of` (the obvious first
guess, and the spec's own worked example) would be WRONG here: a contained
pawn has no map position at all, so the read-back this suite actually uses
is `expect_pawn_despawned` plus the mod's own `SCAN_DONE ... sprung=True`
log line -- two independent channels, neither the mutating call's own
response.

Nothing here has been proven against a live pit falling on a live pawn.
Treat every expectation below as a hypothesis the first live run either
confirms or corrects -- that correction, if any, belongs in this file's own
next revision, not silently in someone's head.
"""
from modcheck import Suite

suite = Suite("Pits")
suite.toggles = ["trapTriggerEnabled", "fallDamageEnabled", "escapeEnabled",
                 "pitCellExposureEnabled"]

# CAT from PitDebugActions.cs -- the debug-menu root segment for every
# action this mod registers, same shape as the world-editing skill's
# "Actions\\Set biome (mod)..." examples but rooted at this mod's own
# category instead of the vanilla "Actions" root.
CAT = "RMPits"
PIT_DEF = "RM_OpenPit_Bare"        # RM_OpenPitBase, floor fitting "Bare"


@suite.chain("pit_capture")
def pit_capture(t):
    """Arm a pit, walk a hostile over it, and prove capture through the
    mod's OWN debug-log channel plus an independent despawn check -- never
    the arming/scan call's own response."""
    t.clear_area(size=20)
    x, z = t.anchor
    cells = t.spawn(PIT_DEF, count=1, at="line")
    t.bridge_call("rimworld/execute_debug_action",
                 path=CAT + "\\Arm cover: woven scrap (40kg)", x=x, z=z)

    raider = t.spawn_pawn("Pirate", hostile=True, beyond=cells)

    with t.component("falls_in", toggle="trapTriggerEnabled"):
        t.walk_over(raider, cells, wait_ticks=300)
        t.bridge_call("rimworld/execute_debug_action",
                     path=CAT + "\\Force trigger scan now", x=x, z=z)
        t.expect_log_contains("RMPitsDebug", field="sprung", value="True")
        t.expect_pawn_despawned(raider)
        t.screenshot()

    with t.component("struggle_clock_ticks", toggle="escapeEnabled"):
        # occupantsBefore/After in the log is this mechanism's own honest
        # read-back -- 1 -> 1 means "still held", the expected result for a
        # single struggle roll against a freshly-captured pawn (the escape
        # chance is real but not guaranteed on one roll; see the item file's
        # note on this being the DRAFT's weakest assumption).
        t.bridge_call("rimworld/execute_debug_action",
                     path=CAT + "\\Force struggle interval", x=x, z=z)
        t.expect_log_contains("RMPitsDebug", field="occupantsBefore", value="1")


@suite.chain("trigger_disabled_no_capture")
def trigger_disabled_no_capture(t):
    """`trapTriggerEnabled=False`: an armed cover never springs on its own
    (PitsMod.cs's own tooltip text) -- a walked-over pawn stays on the map."""
    t.clear_area(size=20)
    x, z = t.anchor
    cells = t.spawn(PIT_DEF, count=1, at="line")
    t.bridge_call("rimworld/execute_debug_action",
                 path=CAT + "\\Arm cover: woven scrap (40kg)", x=x, z=z)
    walker = t.spawn_pawn("Colonist", hostile=False, beyond=cells)

    with t.component("no_spring_while_disabled", toggle="trapTriggerEnabled"):
        # This component's own precondition (trapTriggerEnabled=False) is a
        # Mod Settings value, not something t.* can set -- a live run needs
        # PitsSettings.trapTriggerEnabled flipped before this chain runs,
        # which is exactly what --debug mode's halt-on-fail exists to let a
        # human do by hand between components. Left as an explicit gap
        # rather than a silent assumption: see the item file.
        t.walk_over(walker, cells, wait_ticks=300)
        t.bridge_call("rimworld/execute_debug_action",
                     path=CAT + "\\Force trigger scan now", x=x, z=z)
        t.expect_log_contains("RMPitsDebug", field="sprung", value="False")


@suite.chain("uncover_disarms")
def uncover_disarms(t):
    """The floor's own disarm action, verified via the same ARM/UNCOVER log
    line family -- a beyond-toggle component (no setting governs whether
    disarming works at all)."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn(PIT_DEF, count=1, at="line")
    t.bridge_call("rimworld/execute_debug_action",
                 path=CAT + "\\Arm cover: woven scrap (40kg)", x=x, z=z)

    with t.component("disarm", beyond_toggle=True):
        t.bridge_call("rimworld/execute_debug_action",
                     path=CAT + "\\Uncover (disarm)", x=x, z=z)
        # "UNCOVER" is the log TAG itself here, not a field=value pair --
        # `tag` is drain_log's `contains` filter, so this just asks for the
        # most recent matching line to exist at all.
        t.expect_log_contains("[RMPitsDebug] UNCOVER")
