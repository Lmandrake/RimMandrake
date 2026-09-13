"""validation.py -- modcheck suite for RimMandrake Ninefold (mandrake.rm.ninefold),
M0 safe core ONLY (per the parent modcheck briefing's explicit restriction).

CAUTION -- NINEFOLD_DEBUG_GAME_READY_CRASH_1: a known crash item ties a
`start_debug_game_ready`-shaped debug bootstrap (RimWorld's "instant colony
ready" / auto-research-burst dev helper) to a crash when Ninefold's satiation
hooks fire mid-burst. This suite deliberately NEVER uses that shortcut: every
chain below builds its own state explicitly (clear_area + its own spawns /
pregnancy calls / research_finish_project calls), never an auto-research-burst
bootstrap. Whoever runs this live: if the runner's own quicktest-map setup
uses a `start_debug_game_ready`-style call ahead of this suite, disable it
first or run Ninefold's validation alone against a plain map.

SCOPE -- "M0 safe core" is the mod's OWN description (About.xml): the nine-god
vector, the band ladder (SatiationBand.cs), the per-god Mood random walk, and
exactly FIVE Harmony hooks (research completed, mental break started, birth
outcome, building deconstructed, building repaired). The assembly ships ~13
more Patch_*.cs hooks (art, battle, droid, explosion, faction, fire, gravship,
kill manner, marriage, prisoner, trade, catatonic, plus ChronicleSubscriber's
soft cross-engine binding to mandrake.rm.aftermath) -- those are later wiring
(NINEFOLD_MISSING_EVENT_HOOKS_1 and its successors) and the mod's own naming
scopes them OUT of "M0". Not covered here, by instruction.

FELT-ONLY / NO UI -- design/Jawa/divine_satiation_engine.md and this mod's own
source (Mood's class-level comment on GameComponent_Ninefold: "NEVER surfaced
as a UI number... read only through ambient gesture/narration callers, never
printed") mean there are NO panels and NO debug actions (grepped: this mod
ships zero [DebugAction]-attributed methods, unlike Pits' PitDebugActions.cs)
and NO bridge getter for the vector. The only independent read-back this
suite found at all is `GameComponent_Ninefold.ApplyDelta`'s own
`Log.Message`, itself gated on `Prefs.DevMode` -- every chain below forces
devMode on via `jawa/prefs` (bridge_call escape valve; there is no suite.py
verb for Prefs) before doing anything, and every satiation-changing component
reads the ledger back through `jawa/drain_log`'s `contains` filter, embedding
the exact expected delta substring (e.g. "[Ninefold] Ozzik satiation +15.0")
as `expect_log_contains`'s own `tag` argument, since the log line's actual
shape ("<god> satiation <+-N.N> (<reason>) -> <total> [<band>]") does not fit
`expect_log_contains`'s separate field=value substring form.

MOOD has NO read-back channel anywhere, by design (see above) -- not a log
line, not a getter, not a debug action. The `mood_walk_tick` chain's
component can only prove the game clock crosses one MoodWalkIntervalTicks
boundary (2500 ticks / one in-game hour) with the engine on; it CANNOT prove
the walk moved, or that moodWalkMultiplier scaled anything. This is this
suite's known weakest link -- an instrumentation gap, not a shortcut taken
here on purpose to look green.

MOD SETTINGS ARE STATIC FIELDS -- RM_NinefoldSettings's four fields
(engineEnabled, firstContactLettersEnabled, eventMagnitudeMultiplier,
moodWalkMultiplier) are all `public static`. Per the Pits pilot's own
documented finding (src/RimMandrake/Pits/validation.py's trailing comment),
`t.set_setting` / `rimworld/update_mod_settings` walks INSTANCE fields via
reflection and refuses a static field outright ("Could not resolve field").
No component here attempts a live toggle flip for that reason. Each of the
four toggles instead gets a component that exercises the pathway it gates AT
ITS SHIPPED DEFAULT (engine on, letters on, 1.0x multipliers) -- proving the
gated code path runs at all, not that flipping the setting changes the
outcome. Flipping these live needs a bridge fix or a settings-pattern change
on this mod's own side; neither is attempted here.

Still not proven / likely first-live-run corrections:
  - RESEARCH_PROJECT ("Smithing", an early vanilla tier-1 project) may
    already be finished on whatever quicktest colony this runs against, or
    absent from a minimal mechanism-list load order -- `wasAlreadyFinished`
    comes back in `jawa/research_finish_project`'s own response but is not
    asserted here. A finding on this component should swap the project
    picked, not fault the mod.
  - `building_repaired` / `building_deconstructed`: the wait_ticks budgets
    (5000 each) are a guess at how long ONE colonist takes to repair/
    deconstruct a `Wall` from bridge-dealt damage -- the most likely
    candidate in this file for a live-run tick-count correction, same
    category as Pits' own first-live-run notes.
  - `building_repaired` only exercises Rekko's half -- `Wall` carries no
    CompPowerTrader, so Ohm's "machine rewoken" branch is untested here.
  - `birth_outcome`: `jawa/pawn_pregnancy` progress=1 "begins labour on the
    next tick" per its own tool doc, but the labour-to-ApplyBirthOutcome
    pipeline's real tick length is unmeasured offline; wait_ticks=3000 is a
    guess. A stillbirth (outcome.Positive == false) would also correctly
    produce no delta and no log line, and this chain cannot distinguish
    "hasn't happened yet" from "fired negative" -- it does not additionally
    check pawn/child state.
  - `mood_walk_tick`'s component is UNVERIFIED by design -- see the MOOD
    paragraph above.
  - `jawa/ordered_job` is called with `waitTicks=0` deliberately (its own
    default is 60): its own internal read-back wait would otherwise advance
    the game clock outside this suite's own `t.wait_ticks`, in tension with
    spec §1b's "time stays paused except inside an explicit wait_ticks".
    `waitTicks=0` minimises that; it is not eliminated, because the tool
    itself ticks briefly to read `curJob` back regardless.
"""
from modcheck import Suite

suite = Suite("Ninefold")
suite.toggles = ["engineEnabled", "firstContactLettersEnabled",
                 "eventMagnitudeMultiplier", "moodWalkMultiplier"]

RESEARCH_PROJECT = "Smithing"   # early vanilla tier-1 project -- see docstring caveat
WALL_DEF = "Wall"


def _devmode_on(t):
    """Every satiation read-back in this suite rides ApplyDelta's own
    DevMode-gated Log.Message (see module docstring) -- there is no suite.py
    verb for Prefs, so this goes through the bridge_call escape valve."""
    t.bridge_call("jawa/prefs", devMode=True)


@suite.chain("research_completed")
def research_completed(t):
    """Patch_ResearchCompleted: ApplyDelta(Ozzik, Large) + ApplyDelta(Ohm,
    Small). `jawa/research_finish_project` calls ResearchManager.FinishProject
    directly -- the same method the patch binds to -- so this exercises the
    real Harmony hook, not a simulation of it."""
    t.clear_area(size=20)
    _devmode_on(t)
    with t.component("research_completed_ledger", toggle="engineEnabled"):
        t.bridge_call("jawa/research_finish_project", project=RESEARCH_PROJECT,
                      doCompletionLetter=False)
        t.expect_log_contains("[Ninefold] Ozzik satiation +15.0")
        t.expect_log_contains("[Ninefold] Ohm satiation +3.0")
        t.screenshot()


@suite.chain("mental_break_started")
def mental_break_started(t):
    """Patch_MentalBreakStarted: ApplyDelta(Zizzik, Large) on any humanlike
    player-colonist mental break. `jawa/pawn_force_mental_break` drives
    MentalBreaker.TryDoMentalBreak -> MentalStateHandler.TryStartMentalState,
    the exact method this patch postfixes."""
    t.clear_area(size=20)
    _devmode_on(t)
    colonist = t.spawn_pawn("Colonist", hostile=False)
    with t.component("mental_break_ledger", toggle="eventMagnitudeMultiplier"):
        t.bridge_call("jawa/pawn_force_mental_break", pawn=colonist,
                      intensity="minor")
        t.expect_log_contains("[Ninefold] Zizzik satiation +15.0")
        t.screenshot()


@suite.chain("building_repaired_and_deconstructed")
def building_repaired_and_deconstructed(t):
    """One chain, two components sharing setup (spec §1) -- both hooks are
    driven off the same colonist working the same Wall in turn: damage it,
    order Repair, confirm Rekko's ledger; then order Deconstruct on the (now
    healed) same wall and confirm Rekko/Zizzik's opposite-signed pair. Plain
    `Wall` has no CompPowerTrader -- see docstring's Ohm caveat."""
    t.clear_area(size=20)
    _devmode_on(t)
    x, z = t.anchor
    cells = t.spawn(WALL_DEF, count=1, at="line")
    worker = t.spawn_pawn("Colonist", hostile=False, beyond=cells)

    with t.component("building_repaired", toggle="firstContactLettersEnabled"):
        t.bridge_call("jawa/damage", damageDef="Bomb", amount=40, x=x, z=z,
                      allowColonists=False)
        t.bridge_call("jawa/ordered_job", pawnId=worker, jobDef="Repair",
                      targetAX=x, targetAZ=z, waitTicks=0)
        t.wait_ticks(5000)
        t.expect_log_contains("[Ninefold] Rekko satiation +15.0 (repaired")
        t.screenshot()

    with t.component("building_deconstructed", beyond_toggle=True):
        t.bridge_call("jawa/ordered_job", pawnId=worker, jobDef="Deconstruct",
                      targetAX=x, targetAZ=z, waitTicks=0)
        t.wait_ticks(5000)
        t.expect_log_contains("[Ninefold] Rekko satiation -15.0 (deconstructed")
        t.expect_log_contains("[Ninefold] Zizzik satiation +3.0 (waste")
        t.screenshot()


@suite.chain("birth_outcome")
def birth_outcome(t):
    """Weakest chain in this suite -- see docstring's 'Still not proven'.
    `jawa/pawn_pregnancy` is the only bridge surface that can drive a birth
    without waiting out a real relationship/lovin' cycle."""
    t.clear_area(size=20)
    _devmode_on(t)
    mother = t.spawn_pawn("Colonist", hostile=False)
    with t.component("birth_outcome_ledger", beyond_toggle=True):
        t.bridge_call("jawa/pawn_pregnancy", pawn=mother, action="start")
        t.bridge_call("jawa/pawn_pregnancy", pawn=mother, action="progress",
                      progress=1.0)
        t.wait_ticks(3000)
        t.expect_log_contains("[Ninefold] Oomo satiation +15.0 (birth")
        t.expect_log_contains("[Ninefold] MobUnloo satiation +3.0 (birth")
        t.screenshot()


@suite.chain("mood_walk_tick")
def mood_walk_tick(t):
    """UNVERIFIED BY DESIGN (see docstring's MOOD paragraph) -- Mood has no
    read-back channel anywhere in this mod. This component only proves the
    game clock crosses one MoodWalkIntervalTicks boundary (2500 ticks) with
    the engine on; it cannot prove the walk moved or that moodWalkMultiplier
    scaled it. Satisfies the toggle floor for `moodWalkMultiplier` honestly
    rather than inventing a channel that does not exist."""
    t.clear_area(size=10)
    _devmode_on(t)
    with t.component("mood_walk_advances", toggle="moodWalkMultiplier"):
        t.wait_ticks(2600)
        t.bridge_call("jawa/prefs")   # read-only ping; no mood claim made
        t.screenshot()
