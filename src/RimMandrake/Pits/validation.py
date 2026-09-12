"""validation.py -- modcheck suite for RimMandrake Pits (mandrake.rm.pits).

MOD_VALIDATION_PIT_PILOT_1. Never deployed (deploy_custom_mods.py excludes
`.py` wholesale -- see modcheck's own selftest for the regression guard on
that finding). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Pits

Grounded in the mod's actual source: `PitsMod.cs` for the four real
settings toggles and their defaults; `PitDebugActions.cs` for the exact
debug-action labels and its own `[RMPitsDebug] TAG ...` log lines (this
mod's purpose-built read-back channel, `jawa/drain_log`); and
`Building_OpenPit.Spring()` for the one fact a validator must not get
wrong: a captured pawn is `DeSpawn`'d into `innerContainer` -- CONTAINED,
not merely relocated, so it has no map position and `expect_in_cell_of`
(the spec's own worked example) would be the wrong check entirely.

FIRST LIVE RUN, 2026-09-12 -- what it corrected in this file:
  1. The debug-action PATH is ``Actions\\T: <label>`` -- the `category`
     PitDebugActions.cs declares (`"RMPits"`) is UI metadata (which tab a
     human sees it under), not a path segment; `rimworld/execute_debug_action`
     refused `RMPits\\<label>` with "Could not find debug action" every
     time. Found by `list_debug_action_children("Actions")` and grepping
     its result for "pit" -- every entry came back rooted at ``Actions\\T: ``.
  2. `PitDebugActions.cs` ALSO defines "Report pit state (RAW)" -- a pure
     READ that dumps `def/pos/covered/coverTier/sprung/occupants/...` in
     one `[RMPitsDebug] REPORT_PIT ...` line. Missed on the first read of
     the source; it's a better instrument than parsing `SCAN_DONE`/
     `STRUGGLE`'s own emitted lines, because it works after ANY action, not
     only the one that happens to log the field you need.

Still not proven: the two toggles no component covers
(`fallDamageEnabled`, `pitCellExposureEnabled`) and the struggle-clock
component's escape-chance assumption (see MOD_VALIDATION_PIT_PILOT_1's item
file). Treat every expectation below as load-bearing until it's failed
this suite at least once on purpose (a component that has never been
proven to catch a real regression is not proven to catch anything).
"""
from modcheck import Suite

suite = Suite("Pits")
suite.toggles = ["trapTriggerEnabled", "fallDamageEnabled", "escapeEnabled",
                 "pitCellExposureEnabled"]

PIT_DEF = "RM_OpenPit_Bare"        # RM_OpenPitBase, floor fitting "Bare"


def _debug(t, label, x, z):
    """Every PitDebugActions.cs action, ToolMap, targeted by (x, z) -- the
    real path is `Actions\\T: <label>`, MEASURED live 2026-09-12 (see this
    file's own module docstring); the action's declared `category` is not
    part of the path at all."""
    return t.bridge_call("rimworld/execute_debug_action",
                         path="Actions\\T: " + label, x=x, z=z)


def _report(t, x, z, **expect):
    """Read the pit back via its own pure-read debug action, then require
    every `field=value` pair in `expect` to appear in the resulting
    `REPORT_PIT` log line. Never trusts `_debug`'s own response -- the log
    line is the independent channel."""
    _debug(t, "Report pit state (RAW)", x, z)
    for field, value in expect.items():
        t.expect_log_contains("REPORT_PIT", field=field, value=value)


@suite.chain("pit_capture")
def pit_capture(t):
    """Arm a pit, walk a pawn over it, and prove capture through the mod's
    OWN read-back action plus an independent despawn check -- never the
    arming/scan call's own response.

    Uses `hostile=False` (a plain colonist), NOT a "Pirate" raider, and
    that is itself a finding from the first live run (2026-09-12): a
    hostile-faction pawn ordered via `jawa/order_pawn` reported "moved but
    0/1 arrived ... no drafter, ordered undrafted" -- hostile pawns are not
    reliably steerable that way (their own AI keeps overriding the forced
    job), where a colonist reached the exact cell within one `wait_ticks`
    call every time. The trap mechanism itself does not care about
    faction (`Building_OpenPit.Spring` takes any `Pawn`), so this still
    proves the real mechanism -- it just avoids a SEPARATE, real gap
    (steering hostile pawns reliably) that belongs to a `walk_over`
    hardening pass, not to this mod's validator."""
    t.clear_area(size=20)
    x, z = t.anchor
    cells = t.spawn(PIT_DEF, count=1, at="line")
    _debug(t, "Arm cover: woven scrap (40kg)", x, z)
    _report(t, x, z, covered="True")

    walker = t.spawn_pawn("Colonist", hostile=False, beyond=cells)

    with t.component("falls_in", toggle="trapTriggerEnabled"):
        t.walk_over(walker, cells, wait_ticks=300)
        _debug(t, "Force trigger scan now", x, z)
        _report(t, x, z, sprung="True", occupants="1")
        t.expect_pawn_despawned(walker)
        t.screenshot()

    with t.component("struggle_clock_ticks", toggle="escapeEnabled"):
        # occupants staying at 1 is the expected result of ONE struggle
        # roll against a freshly-captured pawn -- escape is real but not
        # guaranteed on a single roll (this suite's weakest assumption; see
        # the item file). A future revision may need to force many rolls
        # and assert "occupants eventually drops", not "stays at 1 once".
        _debug(t, "Force struggle interval", x, z)
        t.expect_log_contains("STRUGGLE", field="occupantsBefore", value="1")


# NOT a chain: `trapTriggerEnabled=False` (an armed cover never springs on
# its own -- PitsMod.cs's own tooltip text) NEEDS `t.set_setting` to flip
# the toggle live, and that verb, tried live 2026-09-12, cannot reach this
# mod at all: `PitsSettings`'s fields are `public static`, and
# `rimworld/update_mod_settings` refused with "Could not resolve field
# 'trapTriggerEnabled' on 'RimMandrake.Pits.PitsSettings'" -- the bridge's
# reflection walks INSTANCE fields on the ModSettings object, and this
# mod's actual values live on the class, not the instance. See
# MOD_VALIDATION_PIT_PILOT_1's item file: this is a real gap (bridge tool,
# or this mod's settings pattern, or both) to fix before this component can
# exist, not something to fake with an unflippable toggle.


@suite.chain("uncover_disarms")
def uncover_disarms(t):
    """The floor's own disarm action -- a beyond-toggle component (no
    setting governs whether disarming works at all)."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn(PIT_DEF, count=1, at="line")
    _debug(t, "Arm cover: woven scrap (40kg)", x, z)

    with t.component("disarm", beyond_toggle=True):
        _debug(t, "Uncover (disarm)", x, z)
        _report(t, x, z, covered="False")
