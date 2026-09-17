"""validation.py -- modcheck suite for RimMandrake Raid Redesigner -- Old
Friends (mandrake.rm.raidredesigner).

Read whole before writing this: every `.cs` file in `Source/` (not just the
walk doc's own citations) -- `RaidRedesignerMod.cs`, `RaidRedesignerSettings.cs`,
`GameComponent_OldFriends.cs`, `Encounter.cs`, `OldFriendEntry.cs`,
`RoleTag.cs`, `RosterPruning.cs`, `WorldPawnPinning.cs`, all six `Patch_*.cs`
files, `Patch_WokenAncient_STUB.cs`, `Spike_ThreatPointReplace.cs` (compile-only,
not in the .csproj, not this mod's live behavior), `SelfTest/Program.cs`, plus
`Transient/bench_tools_dump.json` for every bridge tool named "roster",
"kidnap", "prisoner", "release", "captur", "flee", "exit_map" or
"game_component" (none exist -- see the floor-gap finding below).

TWO REAL MOD SETTINGS TOGGLES, both plain boolean checkboxes: `rosterTrackingEnabled`
(master switch) and `pinEncounteredPawns`. `maxLivingEntries` and
`grudgeNotabilityMultiplier` are sliders, not toggles, per the briefing's own
rule for `suite.toggles`. All four fields are `public static`
(`BRIDGE_STATIC_SETTINGS_FIELDS_1`'s static-first resolution reaches them).

A REAL, WALK-DOC-IS-STALE FINDING, same register as RustChrome's/Oracle's/
PlantGrowth's tonight: the walk doc's step 1 says the boot line should read
`"[RimMandrake.RaidRedesigner] ready: 8 capture-hook patches."` and treats
the literal `8` as a regression tripwire. Counting the ACTUAL Harmony-patched
target methods from the current source, not the walk doc's number: `harmony.
PatchAll(Assembly.GetExecutingAssembly())` in `RaidRedesignerMod.cs` discovers
exactly FIVE `[HarmonyPatch]`-attributed classes, each patching a DIFFERENT
target method --
  `KidnappedPawnsTracker.Kidnap` (Patch_ColonistKidnapped),
  `Pawn.ExitMap` (Patch_FledRaiderAndCaptain -- one Prefix + one Postfix on
    the SAME method, so `GetPatchedMethods()` still counts it once),
  `GuestUtility.Notify_PrisonerEscaped` (Patch_PrisonerEscaped),
  `GenGuest.PrisonerRelease` (Patch_PrisonerReleased),
  `Pawn_GuestTracker.CapturedBy` (Patch_NamedHunterCaptured)
-- plus `PropertyEngine.Fire` (Patch_CaravanRobbed), patched MANUALLY via
`TryPatch` only `if (ModsConfig.IsActive("mandrake.rm.property"))`.
`Patch_WokenAncient_STUB` carries no `[HarmonyPatch]` at all (its own comment:
"Deliberately no [HarmonyPatch] on this class"). So `harmony.
GetPatchedMethods().Count()` is **5 with `mandrake.rm.property` inactive, 6
with it active** -- never 8, under any environment reachable from this
source. `mandrake.rm.property` is NOT in the minimal list (grepped directly
against `infrastructure/state/modlists/ModsConfig.MINIMAL.xml`), so a plain
`modcheck run RaidRedesigner` should log **5**. This suite checks for 5 or 6
dynamically (by first checking for the mod's own "not active" skip line),
never the walk doc's stale 8.

THE FLOOR GAP THAT MATTERS MOST HERE, bigger than RimProperty's own "two of
five toggles uncovered" -- read in full before writing a single component
that assumes otherwise: **every one of the six PatchAll-discovered hooks has
NO KNOWN TRIGGER on this bridge** (a raider fleeing the map, a raid captain
leaving, a prisoner escaping, a prisoner being released, a colonist
kidnapped, a Blackstar guest-status change -- searched
`Transient/bench_tools_dump.json` for "kidnap"/"prisoner"/"release"/"captur"/
"flee"/"exit_map"/"roster"/"game_component": zero hits, matching the walk
doc's own step 4 conclusion exactly, "no 'force pawn to flee/exit map' tool
exists ... note as a walk gap, not a false pass"). **And there is also NO
READ-BACK tool for `GameComponent_OldFriends.Entries` at all** -- no
"roster"/"oldfriend" tool exists either, so even the ONE hook this suite
CAN trigger live (`BetrayedTrader`, via `mandrake.rm.property`'s
`JobDriver_TheftHaulUninstall.FinishedRemoving` calling `PropertyEngine.Fire`
-- the exact same live recipe `src/RimMandrake/RimProperty/validation.py`'s
own `theft_hauler_uninstall` chain already uses and has committed) has no way
to confirm afterward that `RecordEncounter` actually ran, what `Grudge`/
`Notability` it wrote, or whether the pawn got pinned. `RecordEncounter`
itself logs nothing (grepped: no `Log.Message`/`Log.Error` anywhere in
`GameComponent_OldFriends.cs`, `OldFriendEntry.cs`, or `WorldPawnPinning.cs`).
This suite therefore proves the trigger recipe fires cleanly (no exception,
via the boot-line-adjacent skip check and a plain smoke run of the recipe)
but CANNOT prove the roster itself changed -- a genuine, complete gap in
BOTH directions (trigger AND read-back) for the mod's entire actual
mechanism, left honestly undone rather than faked with a component that
would always report a hollow PASS.

WHAT `RosterPruning`'s OWN OFFLINE SELFTEST ALREADY COVERS, and why this
suite does not duplicate it: `SelfTest/Program.cs` is a SEPARATE, pure-C#
console project (`RimMandrakeRaidRedesigner.SelfTest.csproj`, run via
`dotnet run`, no RimWorld process, no bridge) that already exhaustively
proves `RosterPruning.SelectPruneVictims`'s cap/prune/tie-break/dead-exclusion
logic (5 cases). That is the walk doc's own step 2, a DIFFERENT invocation
entirely from `modcheck run` -- this file cannot re-run it (no bridge
Session involved) and does not attempt to re-implement the same assertions
against a live game it has no way to populate.

Still not proven / out of this validator's floor:
  1. All six PatchAll-discovered hooks' actual firing (FledRaider, Captain,
     EscapedPrisoner, Released, Kidnapper, NamedHunter via either seam) --
     no trigger tool found, per the floor-gap finding above.
  2. `RecordEncounter`'s cap/prune enforcement, grudge/notability math, and
     `WorldPawnPinning.PinForever`'s actual effect on `Find.WorldPawns.
     ForcefullyKeptPawns` -- no read-back tool found for any of it.
  3. The "zero Defs" claim in About.xml (walk doc step 3, "a live
     RimDefDump capture lists zero defs with modName ...") -- no def-dump-by-
     modName bridge tool was found either; this suite does not attempt it.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("RaidRedesigner")
suite.toggles = ["rosterTrackingEnabled", "pinEncounteredPawns"]

SETTINGS_TYPE = "RimMandrake.RaidRedesigner.RaidRedesignerSettings"
READY_LOG_TAG = "[RimMandrake.RaidRedesigner] ready:"
SKIP_LOG_TAG = "[RimMandrake.RaidRedesigner] mandrake.rm.property not active"


@suite.chain("boot_patch_count")
def boot_patch_count(t):
    """Dynamic, environment-aware check -- never the walk doc's stale
    hardcoded 8 (see module docstring). First checks whether the
    Property-skip line fired to know which count (5 or 6) is correct for
    THIS run, rather than assuming `mandrake.rm.property`'s presence
    either way."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("patch_count_matches_active_hooks", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=200, contains="[RimMandrake.RaidRedesigner]")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            property_active = SKIP_LOG_TAG not in joined
            expected = 6 if property_active else 5
            expected_line = "%s %d capture-hook patches." % (READY_LOG_TAG, expected)
            if expected_line not in joined:
                raise ExpectationFailed(
                    "expected '%s' (mandrake.rm.property %s per the skip-"
                    "line check), but it was not found. Recent lines: %r"
                    % (expected_line,
                       "active" if property_active else "inactive", msgs))
        t.screenshot()


@suite.chain("settings_toggles_flip")
def settings_toggles_flip(t):
    """Same register as StructureInjections' `enabled_toggle_flips`:
    proves both toggles are real, live-flippable Mod Settings fields --
    see the module docstring for why no further behavioral proof exists
    (no trigger, no read-back for the mechanism either gates)."""
    t.clear_area(size=8)

    with t.component("roster_tracking_enabled_flips", toggle="rosterTrackingEnabled"):
        t.set_setting(SETTINGS_TYPE, {"rosterTrackingEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"rosterTrackingEnabled": True})
        t.screenshot()

    with t.component("pin_encountered_pawns_flips", toggle="pinEncounteredPawns"):
        t.set_setting(SETTINGS_TYPE, {"pinEncounteredPawns": False})
        t.set_setting(SETTINGS_TYPE, {"pinEncounteredPawns": True})
        t.screenshot()
