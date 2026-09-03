// JawaBenchIncidentTools.cs - storyteller/incidents/quests, lords & raids, animals & training.
//
// BRIDGE_TOOLS_MEDIUM_BLOCK_1, Group I, out of
// infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md.
//
// 198 tools already shipped before this file. Checked against the live roster
// (`grep -rho '"jawa/[a-z_]*"' JawaBench.BridgeTools --include=*.cs`) before writing a
// line - three of the nine listed rows are ALREADY COVERED and are skipped here:
//   * "set master" (Pawn_PlayerSettings.Master) - jawa/set_player_settings already
//     writes it, validated against the Obedience-trainable silent refusal.
//   * jawa/fire_incident already fires an incident, but via IncidentDef.Worker.TryExecute
//     directly - it does NOT go through Storyteller.TryFire, so it never touches
//     StoryState.lastFireTicks or Storyteller.LastIncidentTick. jawa/storyteller_fire
//     below is the genuinely different call, not a duplicate.
//   * jawa/fire_quest already has an `accept` flag, but only for a quest IT JUST
//     CREATED. Nothing on this bridge can accept or end an EXISTING quest - that gap
//     is jawa/quest_lifecycle below.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   RimWorld/Storyteller.cs, RimWorld/FiringIncident.cs, RimWorld/StoryState.cs,
//   RimWorld/IncidentParms.cs, RimWorld/Page_SelectStorytellerInGame.cs,
//   RimWorld/Quest.cs, RimWorld/QuestState.cs, RimWorld/QuestEndOutcome.cs,
//   RimWorld/WealthWatcher.cs, Verse/AI/Group/LordMaker.cs, Verse/AI/Group/Lord.cs,
//   Verse/AI/Group/LordJob_DefendPoint.cs, RimWorld/LordJob_AssaultColony.cs,
//   RimWorld/AggressiveAnimalIncidentUtility.cs, RimWorld/CompEggLayer.cs,
//   RimWorld/CompHasGatherableBodyResource.cs.
//
// FOUR TRAPS THE SOURCE CONFIRMED, ALL HANDLED BELOW RATHER THAN DISCOVERED LATER:
//   * Storyteller.TryFire only routes through StoryState.Notify_IncidentFired when
//     fi.parms.forced is FALSE and fi.parms.target == the target whose StoryState is
//     being checked. We never set `forced`, and DefaultParmsNow already stamps
//     `target = map`, so the read-back is meaningful without extra plumbing.
//   * Lord.AddPawnInternal LOGS AN ERROR AND SILENTLY DROPS THE PAWN when it already
//     has a Lord ("Pawns can't be members of more than one lord at the same time") -
//     LordMaker.MakeNewLord does not surface this at all, it just returns a Lord with
//     fewer members than asked. Both lord-spawning tools below pre-filter on
//     Pawn.GetLord() != null and report refused[], rather than trusting membership
//     counts after the fact.
//   * Quest.Accept(Pawn) and Quest.End(...) both check their own precondition
//     internally (State == NotYetAccepted; !Historical) and SILENTLY NO-OP (Accept)
//     or Log.Error-and-return (End) otherwise - jawa/quest_lifecycle checks first and
//     refuses with the real state, rather than reporting a call that did nothing.
//   * CompHasGatherableBodyResource.fullness and CompEggLayer.eggProgress are both
//     PRIVATE/PROTECTED with no public setter - "forcing" either requires reflection,
//     which is scoped to this file only (GmWritePrivateField below) exactly as
//     JawaBenchSimTools.cs already does for WeatherDecider.ticksWhenRainAllowedAgain.
//
// GATING follows the rule stated in JawaBenchEventTools.cs and JawaBenchGroupTools.cs:
// #if JAWA_GM_TOOLS is for tools that make THE WORLD ACT on the player, not merely
// for tools that write a field. On that test:
//   GATED:   jawa/storyteller_fire (fires a real incident), jawa/storyteller_swap
//            (changes what the storyteller does with every future tick - the same
//            bar jawa/difficulty_tune already sits behind), jawa/lord_defend_spawn
//            and jawa/lord_assault_spawn (both create a live, autonomous combat lord).
//   UNGATED: jawa/quest_lifecycle - matches jawa/fire_quest's own `accept` flag,
//            which is ungated in this same codebase for the identical effect;
//            jawa/wealth_recount - forces a recompute of numbers already public;
//            jawa/manhunter_preview - pure read, the raid_preview/
//            incident_parms_preview idiom applied to AggressiveAnimalIncidentUtility;
//            jawa/animal_resource_force - an admin poke on a named pawn's own body
//            resource, the same shape as jawa/gene_resource_poke (also ungated).
//
// THREAD AFFINITY: same rule as every other file here - everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared helpers, private to THIS file only -----------------------

        /// <summary>
        /// Writes a private/protected instance field by reflection. Used only where
        /// the engine has no public setter at all: CompHasGatherableBodyResource.fullness
        /// and CompEggLayer.eggProgress. Scoped to this file, mirroring
        /// JawaBenchSimTools.SimPrivateField's read-only counterpart.
        /// </summary>
        private static bool GmWritePrivateField(Type declaringType, object obj, string name, object value)
        {
            if (declaringType == null || obj == null) return false;
            FieldInfo fi = declaringType.GetField(name, BindingFlags.NonPublic | BindingFlags.Instance);
            if (fi == null) return false;
            try { fi.SetValue(obj, value); return true; }
            catch (Exception) { return false; }
        }

        private static object GmReadPrivateField(Type declaringType, object obj, string name)
        {
            if (declaringType == null || obj == null) return null;
            FieldInfo fi = declaringType.GetField(name, BindingFlags.NonPublic | BindingFlags.Instance);
            if (fi == null) return null;
            try { return fi.GetValue(obj); }
            catch (Exception) { return null; }
        }

        /// <summary>
        /// Property counterpart to GmReadPrivateField - used for CompHasGatherableBodyResource's
        /// protected abstract ResourceDef, which is overridden as an expression-bodied property in
        /// each concrete comp (CompMilkable, CompShearable) with no backing field to read directly.
        /// FlattenHierarchy so the override declared on the runtime type is found even though the
        /// property is declared abstract on the base type.
        /// </summary>
        private static object GmReadPrivateProperty(Type declaringType, object obj, string name)
        {
            if (declaringType == null || obj == null) return null;
            PropertyInfo pi = declaringType.GetProperty(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance | BindingFlags.FlattenHierarchy);
            if (pi == null) return null;
            try { return pi.GetValue(obj, null); }
            catch (Exception) { return null; }
        }

        // ================================================================
        //  Storyteller, incidents & quests
        // ================================================================

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/storyteller_fire",
            Description =
                "*** ACTS ON THE LIVE COLONY - THIS SENDS A REAL INCIDENT *** " +
                "Fire an incident through Storyteller.TryFire(new FiringIncident(def, null, parms)) - " +
                "NOT the same call jawa/fire_incident makes. jawa/fire_incident calls " +
                "IncidentDef.Worker.TryExecute(parms) directly, which fires the incident but never " +
                "touches the storyteller's own bookkeeping. TryFire additionally calls " +
                "parms.target.StoryState.Notify_IncidentFired(fi), which updates StoryState.lastFireTicks " +
                "for this def and Storyteller.LastIncidentTick - the numbers later incident selection " +
                "and 'time since last incident of this kind' logic actually read. Use this one when the " +
                "incident needs to be believed by the storyteller's own memory, not just to have happened. " +
                "dryRun defaults true. " +
                "🔴 READ blockedByDialog BEFORE fired. A Harmony prefix can replace the incident with a " +
                "modal and still set __result = true (Leo.RaidProtectionFee does this to RaidEnemy), so " +
                "Find.WindowStack is diffed across TryFire. Clear any modal reported here with " +
                "jawa/window_list_close - nothing on the bridge can answer one.",
            ResultDescription =
                "success (fired AND not blocked), fired (TryFire's own return), windowsOpened[], " +
                "blockedByDialog, resolved parms, and BOTH read-back fields: " +
                "lastFireTickForThisDef (map.StoryState.lastFireTicks[def]) and lastIncidentTick " +
                "(Storyteller.LastIncidentTick), before and after - the actual evidence TryFire ran, " +
                "not an echo of the request.")]
        public static async Task<object> StorytellerFire(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "IncidentDef defName, e.g. RaidEnemy, TraderCaravanArrival, ManhunterPack.")]
            string incidentDef = null,
            [ToolParameter(Description = "Threat points. <=0 uses the storyteller's current default.")]
            float points = 0f,
            [ToolParameter(Description = "Optional FactionDef for incidents that take one (raids).")]
            string faction = null,
            [ToolParameter(Description = "Resolve and report without firing. Default true - opt in to fire for real.")]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrWhiteSpace(incidentDef)) return Fail("Give 'incidentDef'.");

                var idef = DefDatabase<IncidentDef>.GetNamedSilentFail(incidentDef.Trim());
                if (idef == null) return Fail("No IncidentDef '" + incidentDef + "'.", DefSuggestions<IncidentDef>(incidentDef));

                IncidentParms parms;
                try { parms = StorytellerUtility.DefaultParmsNow(idef.category, map); }
                catch (Exception e) { return Fail("DefaultParmsNow threw: " + e.GetType().Name + ": " + e.Message); }
                if (points > 0f) parms.points = points;

                if (!string.IsNullOrWhiteSpace(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    var fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                    parms.faction = fac;
                }

                bool canFire;
                try { canFire = idef.Worker.CanFireNow(parms); }
                catch (Exception) { canFire = false; }

                var resolved = new
                {
                    incident = idef.defName,
                    category = idef.category != null ? idef.category.defName : null,
                    points = parms.points,
                    faction = parms.faction != null ? parms.faction.def.defName : "(worker chooses)",
                };

                if (dryRun)
                    return (object)new
                    {
                        success = true, dryRun = true, resolved, canFireNow = canFire,
                        note = "DRY RUN - nothing was sent. Pass dryRun=false to fire through Storyteller.TryFire for real.",
                        ticksGame = TicksGameSafe(),
                    };

                int fireTickBefore; map.StoryState.lastFireTicks.TryGetValue(idef, out fireTickBefore);
                int lastIncidentTickBefore = Find.Storyteller.LastIncidentTick;

                // FIRE_RAID_REPORTS_MODAL_1 - diff the window stack across TryFire.
                var windowIdsBefore = SnapshotWindowIds();

                var fi = new FiringIncident(idef, null, parms);
                bool fired;
                try { fired = Find.Storyteller.TryFire(fi); }
                catch (Exception e) { return Fail("TryFire threw: " + e.GetType().Name + ": " + e.Message); }

                var windowsOpened = WindowsOpenedSince(windowIdsBefore);
                bool blockedByDialog = fired && windowsOpened.Count > 0;
                string swallowNote = DialogSwallowNote(windowsOpened, fired);

                int fireTickAfter; map.StoryState.lastFireTicks.TryGetValue(idef, out fireTickAfter);
                int lastIncidentTickAfter = Find.Storyteller.LastIncidentTick;

                return (object)new
                {
                    success = fired && !blockedByDialog,
                    dryRun = false,
                    resolved,
                    fired,
                    windowsOpened,
                    blockedByDialog,
                    canFireNow = canFire,
                    lastFireTickForThisDef = new { before = fireTickBefore, after = fireTickAfter },
                    lastIncidentTick = new { before = lastIncidentTickBefore, after = lastIncidentTickAfter },
                    recordedInAdaptationState = fireTickAfter != fireTickBefore,
                    note = blockedByDialog ? swallowNote : fired
                        ? (fireTickAfter != fireTickBefore
                            ? "Fired AND recorded in StoryState.lastFireTicks - this is the difference from jawa/fire_incident."
                            : "Fired, but lastFireTicks did NOT move. Notify_IncidentFired only skips this when parms.forced is true or parms.target does not match this map's StoryState - neither should happen here, so this would itself be worth reporting upstream.")
                        : "TryFire returned false - CanFireNow or TryExecute refused these parms.",
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/storyteller_swap",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Change WHO IS RUNNING THE GAME: " +
                "Current.Game.storyteller.def (the StorytellerDef - Cassandra/Phoebe/Randy/etc.) and/or " +
                ".difficultyDef, exactly as Page_SelectStorytellerInGame does: assign the field, then call " +
                "Notify_DefChanged() - which re-runs InitializeStorytellerComps() so the NEW storyteller's " +
                "comps actually drive future incidents, not the old ones. Read-only until now; nothing " +
                "else on this bridge can write either field. This is distinct from jawa/difficulty_tune, " +
                "which edits fields ON the difficulty OBJECT (threatScale etc.) without changing which " +
                "StorytellerDef or DifficultyDef is active. Give neither argument to just read the " +
                "current values. " +
                "🔴 Setting difficultyDef ALSO copies that def's values into Storyteller.difficulty " +
                "(Difficulty.CopyFrom), exactly as StorytellerUI does - the def field on its own is only " +
                "a label and a StatPart_Difficulty key; every gameplay number is read off the Difficulty " +
                "OBJECT, so writing the def alone would change nothing the game plays by. A def with " +
                "isCustom=true is the one exception: its values are whatever jawa/difficulty_tune left " +
                "there, so nothing is copied over them.",
            ResultDescription =
                "success, before/after {storytellerDef, difficultyDef, threatScale}, whether " +
                "Notify_DefChanged was called (only when storytellerDef actually changed), and " +
                "difficultyValuesCopied - whether Storyteller.difficulty took the new def's values.")]
        public static async Task<object> StorytellerSwap(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "StorytellerDef name, e.g. Cassandra, Phoebe, Randy. Omit to leave unchanged.")]
            string storytellerDef = null,
            [ToolParameter(Description = "DifficultyDef name, e.g. Rough, Merciless, Custom. Omit to leave unchanged.")]
            string difficultyDef = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                var st = Find.Storyteller;
                if (st == null) return Fail("Find.Storyteller is null - is a game loaded?");

                Func<object> snapshot = () => new
                {
                    storytellerDef = st.def != null ? st.def.defName : null,
                    difficultyDef = st.difficultyDef != null ? st.difficultyDef.defName : null,
                    threatScale = st.difficulty != null ? (float?)st.difficulty.threatScale : null,
                };
                var before = snapshot();

                // 🔴 BOTH defs are resolved BEFORE either is written. Resolving difficultyDef inline
                // meant an unknown DifficultyDef returned Fail with st.def ALREADY swapped and
                // Notify_DefChanged() never reached - leaving the live game running a NEW
                // StorytellerDef against the PREVIOUS def's storytellerComps, and reporting that to
                // the caller as a clean failure that changed nothing.
                StorytellerDef sd = null;
                if (!string.IsNullOrWhiteSpace(storytellerDef))
                {
                    sd = DefDatabase<StorytellerDef>.GetNamedSilentFail(storytellerDef.Trim());
                    if (sd == null) return Fail("No StorytellerDef '" + storytellerDef + "'.", DefSuggestions<StorytellerDef>(storytellerDef));
                }
                DifficultyDef dd = null;
                if (!string.IsNullOrWhiteSpace(difficultyDef))
                {
                    dd = DefDatabase<DifficultyDef>.GetNamedSilentFail(difficultyDef.Trim());
                    if (dd == null) return Fail("No DifficultyDef '" + difficultyDef + "'.", DefSuggestions<DifficultyDef>(difficultyDef));
                }

                bool defChanged = false;
                if (sd != null && st.def != sd) { st.def = sd; defChanged = true; }

                // 🔴 Storyteller.difficultyDef is ONLY a label (stat reports, MainTabWindow_History)
                // and the StatPart_Difficulty key. Every number the game actually plays by - threatScale,
                // cropYieldFactor, researchSpeedFactor, allowBigThreats, ... - is read off
                // Storyteller.difficulty, the Difficulty VALUE object. StorytellerUI, which is what
                // Page_SelectStorytellerInGame drives, does `difficultyValues.CopyFrom(allDef)` alongside
                // `difficulty = allDef`; writing the def alone changes nothing but a label, which would
                // make this tool report success for a swap that did not happen.
                bool difficultyValuesCopied = false;
                bool difficultyIsCustom = false;
                bool difficultyDefChanged = false;
                if (dd != null)
                {
                    difficultyDefChanged = st.difficultyDef != dd;
                    st.difficultyDef = dd;
                    difficultyIsCustom = dd.isCustom;
                    if (!dd.isCustom && st.difficulty != null)
                    {
                        try { st.difficulty.CopyFrom(dd); difficultyValuesCopied = true; }
                        catch (Exception e)
                        {
                            // The def is written and the values are not. Still run Notify_DefChanged
                            // if the STORYTELLER def moved, or the comps would be left belonging to
                            // the previous storyteller for the rest of the game.
                            if (defChanged) { try { st.Notify_DefChanged(); } catch (Exception) { } }
                            return Fail("difficultyDef was set but Difficulty.CopyFrom threw: " + e.GetType().Name + ": " + e.Message +
                                        " - the storyteller is now in a MIXED state (new def, old values)." +
                                        (defChanged ? " storytellerDef was ALSO already swapped to " + st.def.defName + "; Notify_DefChanged() was run so its comps are at least consistent." : ""));
                        }
                    }
                }

                if (defChanged) st.Notify_DefChanged();

                var notes = new List<string>();
                if (defChanged) notes.Add("Notify_DefChanged() re-initialized storytellerComps for the new def.");
                else if (!string.IsNullOrWhiteSpace(storytellerDef)) notes.Add("storytellerDef was already this value - Notify_DefChanged was NOT called.");
                if (difficultyValuesCopied) notes.Add("Storyteller.difficulty.CopyFrom(def) applied the new difficulty's VALUES - the def field alone is only a label.");
                else if (difficultyIsCustom) notes.Add("That DifficultyDef is isCustom=true, so its (empty) values were NOT copied over Storyteller.difficulty - the live custom values stand. Edit them with jawa/difficulty_tune.");
                else if (difficultyDefChanged) notes.Add("difficultyDef was written but Storyteller.difficulty is null, so no values could be copied onto it - ONLY the label moved and no gameplay number changed.");
                if (notes.Count == 0) notes.Add(string.IsNullOrWhiteSpace(storytellerDef) && string.IsNullOrWhiteSpace(difficultyDef)
                    ? "No arguments given - this was a read."
                    : "Nothing changed.");

                return (object)new
                {
                    success = true,
                    before,
                    after = snapshot(),
                    notifyDefChangedCalled = defChanged,
                    difficultyValuesCopied,
                    note = string.Join(" ", notes.ToArray()),
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }
#endif // JAWA_GM_TOOLS

        [Tool(
            "jawa/quest_lifecycle",
            Description =
                "List every quest, or Accept()/End() an EXISTING one by id. jawa/fire_quest can accept " +
                "a quest too, but only the one IT JUST CREATED in the same call - nothing else on this " +
                "bridge can act on a quest that arrived naturally (float menu, storyteller, another mod). " +
                "action='list' is read-only. action='accept' pre-checks State==NotYetAccepted itself, " +
                "because Quest.Accept(Pawn) SILENTLY NO-OPS from any other state rather than erroring - " +
                "reporting that as success would be exactly the silent-failure shape this bridge exists " +
                "to catch. action='end' pre-checks !Historical for the identical reason: Quest.End() " +
                "Log.Errors and returns on an already-ended or expired quest. This is UNGATED, matching " +
                "jawa/fire_quest's own ungated accept for the identical effect.",
            ResultDescription =
                "success; for 'list': quests[] (id, name, state, points, requiresAccepter, historical); " +
                "for 'accept'/'end': stateBefore/stateAfter READ BACK off the Quest, not assumed from " +
                "the call succeeding.")]
        public static async Task<object> QuestLifecycle(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' (default), 'accept' or 'end'.")]
            string action = "list",
            [ToolParameter(Description = "Quest id from 'list'. Required for accept/end.")]
            int questId = -1,
            [ToolParameter(Description = "Accepter pawn id or name. Empty picks a free colonist if the quest RequiresAccepter.")]
            string accepterPawn = null,
            [ToolParameter(Description = "For 'end': 'success' | 'fail' | 'unknown'. Default 'unknown'.")]
            string outcome = "unknown",
            [ToolParameter(Description = "For 'end': show the completion letter. Default true.")]
            bool sendLetter = true,
            [ToolParameter(Description = "For 'end': play the completion sound. Default true.")]
            bool playSound = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                var manager = Find.QuestManager;
                if (manager == null) return Fail("No QuestManager - is a game actually loaded?");

                Func<List<object>> rows = () => manager.QuestsListForReading.Select(q => (object)new
                {
                    id = q.id,
                    name = q.name,
                    state = q.State.ToString(),
                    points = q.points,
                    requiresAccepter = q.RequiresAccepter,
                    historical = q.Historical,
                }).ToList();

                var act = (action ?? "list").Trim().ToLowerInvariant();
                if (act == "list")
                    return new { success = true, action = "list", count = manager.QuestsListForReading.Count, quests = rows(), ticksGame = TicksGameSafe() };

                if (questId < 0) return Fail("Give 'questId'. Call action='list' first.", rows());
                var q2 = manager.QuestsListForReading.FirstOrDefault(x => x.id == questId);
                if (q2 == null) return Fail("No quest with id " + questId + ".", rows());

                var stateBefore = q2.State;

                if (act == "accept")
                {
                    if (stateBefore != QuestState.NotYetAccepted)
                        return Fail("Quest " + q2.id + " \"" + q2.name + "\" is " + stateBefore +
                                    ", not NotYetAccepted. Accept() silently no-ops from any other state - refusing rather than reporting a call that would do nothing.");

                    Pawn by = null;
                    if (!string.IsNullOrWhiteSpace(accepterPawn))
                    {
                        string perr; by = FindPawn(accepterPawn, out perr);
                        if (by == null) return Fail(perr);
                    }
                    else if (q2.RequiresAccepter)
                    {
                        var map = Find.CurrentMap;
                        by = map != null ? map.mapPawns.FreeColonists.FirstOrDefault() : null;
                        if (by == null) return Fail("Quest " + q2.id + " RequiresAccepter and no accepterPawn was given, and no free colonist could be found on the current map.");
                    }

                    try { q2.Accept(by); }
                    catch (Exception e) { return Fail("Accept threw: " + e.GetType().Name + ": " + e.Message); }

                    // Quest.Accept() -> Initiate() sends the Initiate signal SYNCHRONOUSLY, and a
                    // QuestPart is free to End the quest inside that signal - a quest that accepts
                    // and immediately resolves lands on EndedSuccess/EndedFailed, not Ongoing.
                    // Requiring Ongoing reported success=false for an accept that fully worked.
                    var stateAfter = q2.State;
                    return new
                    {
                        success = stateAfter != QuestState.NotYetAccepted,
                        action = "accept",
                        questId = q2.id,
                        questName = q2.name,
                        accepter = by != null ? by.LabelShortCap : null,
                        stateBefore = stateBefore.ToString(),
                        stateAfter = stateAfter.ToString(),
                        endedImmediately = stateAfter != QuestState.NotYetAccepted && stateAfter != QuestState.Ongoing,
                        note = stateAfter == QuestState.NotYetAccepted
                            ? "Accept() ran but the quest is STILL NotYetAccepted - it did nothing. Report this: the pre-check said the state was acceptable."
                            : stateAfter != QuestState.Ongoing
                                ? "Accepted, then a QuestPart ended it inside the Initiate signal in the same call - final state " + stateAfter + "."
                                : null,
                        ticksGame = TicksGameSafe(),
                    };
                }

                if (act == "end")
                {
                    if (q2.Historical)
                        return Fail("Quest " + q2.id + " \"" + q2.name + "\" is already Historical (state " + stateBefore + "). " +
                                    "Quest.End() Log.Errors and refuses on a Historical quest - refusing here instead of calling it.");

                    QuestEndOutcome oc;
                    var o = (outcome ?? "unknown").Trim().ToLowerInvariant();
                    if (o == "success") oc = QuestEndOutcome.Success;
                    else if (o == "fail" || o == "failed") oc = QuestEndOutcome.Fail;
                    else if (o == "unknown") oc = QuestEndOutcome.Unknown;
                    else return Fail("outcome must be 'success', 'fail' or 'unknown', got '" + outcome + "'.");

                    try { q2.End(oc, sendLetter, playSound); }
                    catch (Exception e) { return Fail("End threw: " + e.GetType().Name + ": " + e.Message); }

                    var stateAfter = q2.State;
                    return new
                    {
                        success = stateAfter != stateBefore && q2.Historical,
                        action = "end",
                        questId = q2.id,
                        questName = q2.name,
                        outcome = oc.ToString(),
                        stateBefore = stateBefore.ToString(),
                        stateAfter = stateAfter.ToString(),
                        ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("action must be 'list', 'accept' or 'end'.");
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/wealth_recount",
            Description =
                "Force WealthWatcher.ForceRecount(allowDuringInit) on the current map's wealth right now, " +
                "instead of waiting for its own 5000-tick throttle (RecountIfNeeded). This is the exact " +
                "number every threat budget is computed from (see jawa/weather_get's 'wealth' block, " +
                "which reads the SAME properties but does not force a recompute). Read-only in effect - " +
                "it recomputes existing wealth, it does not change what exists - so this is ungated.",
            ResultDescription =
                "success, before/after {total, items, buildings, floorsOnly, pawns, healthTotal}, and " +
                "lastCountTick (private field, read by reflection) before/after so a caller can tell the " +
                "recount actually ran rather than reusing a value the property getter already had. " +
                "🔴 The whole 'before' block is read off the PRIVATE fields, not the public getters: " +
                "WealthTotal/WealthItems/... each call RecountIfNeeded() and would therefore perform the " +
                "recount themselves, leaving before==after and lastCountTick unmoved - the tool would " +
                "report recounted=false in precisely the case where a recount had just happened.")]
        public static async Task<object> WealthRecount(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Passed to ForceRecount - allow recounting during game init. Default false, matching the engine's own default.")]
            bool allowDuringInit = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var w = map.wealthWatcher;
                if (w == null) return Fail("This map has no WealthWatcher.");

                // 🔴 ForceRecount's FIRST statement is `if (!allowDuringInit && ProgramState != Playing)
                // { Log.Error(...); return; }` - it does not throw, so the try/catch below cannot see
                // it and the tool would report success=true for a recount that never ran. Refuse
                // with the real reason instead.
                if (!allowDuringInit && Current.ProgramState != ProgramState.Playing)
                    return Fail("ForceRecount would Log.Error and return WITHOUT recounting: Current.ProgramState is " +
                                Current.ProgramState + ", not Playing. Pass allowDuringInit=true to force it anyway.");

                Func<object> snapshot = () => new
                {
                    total = w.WealthTotal,
                    items = w.WealthItems,
                    buildings = w.WealthBuildings,
                    floorsOnly = w.WealthFloorsOnly,
                    pawns = w.WealthPawns,
                    healthTotal = w.HealthTotal,
                };

                // 🔴 Do NOT touch the public getters for the "before" reading. Every one of
                // WealthTotal/WealthItems/WealthBuildings/WealthFloorsOnly/WealthPawns/HealthTotal calls
                // RecountIfNeeded(), which runs a FULL ForceRecount() once the cache is >5000 ticks stale -
                // the exact case this tool exists for. Reading them first would do the recount, so the
                // explicit ForceRecount below would move nothing and `recounted` would report false while
                // a recount had in fact just happened. The pre-state comes off the private fields instead.
                object lastCountTickBefore = GmReadPrivateField(typeof(WealthWatcher), w, "lastCountTick");
                object rItems = GmReadPrivateField(typeof(WealthWatcher), w, "wealthItems");
                object rBuildings = GmReadPrivateField(typeof(WealthWatcher), w, "wealthBuildings");
                object rPawns = GmReadPrivateField(typeof(WealthWatcher), w, "wealthPawns");
                object rFloors = GmReadPrivateField(typeof(WealthWatcher), w, "wealthFloorsOnly");
                object rHealth = GmReadPrivateField(typeof(WealthWatcher), w, "totalHealth");
                bool preStateRead = rItems is float && rBuildings is float && rPawns is float && rFloors is float && rHealth is int;

                float fItems = rItems is float ? (float)rItems : 0f;
                float fBuildings = rBuildings is float ? (float)rBuildings : 0f;
                float fPawns = rPawns is float ? (float)rPawns : 0f;
                float fFloors = rFloors is float ? (float)rFloors : 0f;
                object before = preStateRead
                    ? (object)new
                    {
                        total = fItems + fBuildings + fPawns,
                        items = fItems,
                        buildings = fBuildings,
                        floorsOnly = fFloors,
                        pawns = fPawns,
                        healthTotal = (int)rHealth,
                    }
                    : null;

                try { w.ForceRecount(allowDuringInit); }
                catch (Exception e) { return Fail("ForceRecount threw: " + e.GetType().Name + ": " + e.Message); }

                var after = snapshot();
                object lastCountTickAfter = GmReadPrivateField(typeof(WealthWatcher), w, "lastCountTick");

                // 🔴 lastCountTick is `private float`, and ForceRecount stamps it with the CURRENT
                // TicksGame. A recount that lands on the same tick as the previous one therefore
                // leaves the stamp unmoved - a bare before!=after comparison reports recounted=false
                // for a recount that demonstrably ran. The stamp matching "now" is the positive
                // evidence; a moved stamp is reported separately as the weaker of the two.
                bool stampMoved = !Equals(lastCountTickBefore, lastCountTickAfter);
                int ticksNow = TicksGameSafe();
                bool stampIsNow = lastCountTickAfter is float && ticksNow >= 0 && Math.Abs((float)lastCountTickAfter - ticksNow) < 0.5f;

                return (object)new
                {
                    success = true,
                    before,
                    after,
                    preStateReadByReflection = preStateRead,
                    lastCountTick = new { before = lastCountTickBefore, after = lastCountTickAfter },
                    recounted = stampMoved || stampIsNow,
                    lastCountTickMoved = stampMoved,
                    lastCountTickIsThisTick = stampIsNow,
                    note = preStateRead
                        ? (stampMoved || stampIsNow
                            ? null
                            : "recounted=false: ForceRecount returned but lastCountTick neither moved nor matches the current tick. Either the private field layout changed or something is intercepting ForceRecount - the 'after' numbers may be stale.")
                        : "'before' is null - WealthWatcher's private field layout has changed, so no honest pre-recount reading could be taken. 'after' is still real.",
                    ticksGame = ticksNow,
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Lords, raids & AI groups
        // ================================================================

        /// <summary>
        /// Shared by both lord-spawn tools: resolve pawns, refusing (not silently
        /// dropping) any that are missing, off this map, or already owned by
        /// another Lord - the exact case Lord.AddPawnInternal itself only logs.
        /// </summary>
        private static List<Pawn> ResolveLordCandidates(string pawns, Map map, out List<object> refused)
        {
            refused = new List<object>();
            var found = new List<Pawn>();
            if (string.IsNullOrWhiteSpace(pawns)) return found;
            foreach (var raw in pawns.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var tok = raw.Trim();
                if (tok.Length == 0) continue;
                string perr;
                var p = FindPawn(tok, out perr);
                if (p == null) { refused.Add(new { pawn = tok, reason = "NotFound", message = perr }); continue; }
                if (p.Map != map || !p.Spawned) { refused.Add(new { pawn = tok, reason = "NotOnThisMap", message = p.LabelShortCap + " is not spawned on the current map." }); continue; }
                var existingLord = p.GetLord();
                if (existingLord != null)
                {
                    refused.Add(new
                    {
                        pawn = tok,
                        reason = "AlreadyInALord",
                        message = p.LabelShortCap + " already belongs to a Lord (job " +
                                  (existingLord.LordJob != null ? existingLord.LordJob.GetType().Name : "(null)") +
                                  "). Lord.AddPawnInternal would Log.Error and silently drop it - refusing instead."
                    });
                    continue;
                }
                // Lord.AddPawnInternal ALSO Log.Errors and drops on `ownedPawns.Contains(p)`, so
                // naming the same pawn twice ("Bob,Bob") used to pass this pre-check twice and then
                // vanish inside MakeNewLord - requested=2, memberCount=1, refused[] empty.
                if (found.Contains(p))
                {
                    refused.Add(new
                    {
                        pawn = tok,
                        reason = "DuplicateInRequest",
                        message = p.LabelShortCap + " was named more than once. Lord.AddPawnInternal Log.Errors and " +
                                  "drops a pawn the Lord already controls - refusing the extra copy instead."
                    });
                    continue;
                }
                found.Add(p);
            }
            return found;
        }

        /// <summary>
        /// Names every pawn that was handed to LordMaker but is NOT in the resulting Lord's
        /// ownedPawns. The pre-check above covers the cases observable from outside; AddPawnInternal
        /// can still Log.Error-and-drop for a reason we did not model, and MakeNewLord surfaces that
        /// only as a smaller member count. A count that does not add up, with no names attached, is
        /// exactly the silent drop this bridge exists to catch.
        /// </summary>
        private static List<object> LordMembersNotAdded(Lord lord, List<Pawn> requested)
        {
            var missing = new List<object>();
            if (lord == null || requested == null) return missing;
            foreach (var p in requested)
            {
                if (lord.ownedPawns != null && lord.ownedPawns.Contains(p)) continue;
                var other = p.GetLord();
                missing.Add(new
                {
                    pawn = p.LabelShortCap,
                    reason = "DroppedByLord",
                    message = "Handed to LordMaker but absent from the new Lord's ownedPawns" +
                              (other != null && other != lord
                                  ? " - it belongs to a different Lord (job " + (other.LordJob != null ? other.LordJob.GetType().Name : "(null)") + ")."
                                  : ". Lord.AddPawnInternal only Log.Errors when it drops a pawn - the reason is in the game log.")
                });
            }
            return missing;
        }

        /// <summary>
        /// LordMaker.MakeNewLord calls map.lordManager.AddLord(lord) BEFORE SetJob/GotoToil. If
        /// either throws - a modded LordJob's CreateGraph, a Harmony patch - the Lord is already
        /// registered on the map with no job and no toil, and LordManagerTick will fault on it every
        /// tick for the rest of the game. Nothing in the engine unwinds that, so the tool that
        /// created it must. Returns how many were removed.
        /// </summary>
        private static int RemoveLordsAddedSince(Map map, int countBefore)
        {
            if (map == null || map.lordManager == null || map.lordManager.lords == null) return 0;
            var lords = map.lordManager.lords;
            int removed = 0;
            for (int guard = 0; guard < 64 && lords.Count > countBefore; guard++)
            {
                var orphan = lords[lords.Count - 1];
                // Lord.Cleanup() dereferences curJob UNGUARDED while walking ownedPawns, so a Lord
                // that died before SetJob ran would throw straight back out of RemoveLord. Detach
                // the pawns first so that loop is empty, then take the engine path.
                try
                {
                    if (orphan.ownedPawns != null)
                    {
                        foreach (var op in orphan.ownedPawns)
                            if (op != null && op.lord == orphan) op.lord = null;
                        orphan.ownedPawns.Clear();
                    }
                }
                catch (Exception) { }
                try { map.lordManager.RemoveLord(orphan); }
                catch (Exception) { }
                if (lords.Count > countBefore && lords[lords.Count - 1] == orphan)
                {
                    try { if (!lords.Remove(orphan)) break; }
                    catch (Exception) { break; }
                }
                removed++;
            }
            return removed;
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/lord_defend_spawn",
            Description =
                "*** ACTS ON THE LIVE COLONY *** LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(...), " +
                "map, pawns) - make a group that lives, works and defends a radius around a point. " +
                "⛔ THIS DELIBERATELY USES LordJob_DefendPoint, NEVER LordJob_DefendBase - the roster " +
                "this tool was built from names DefendBase as a trap because it self-converts into a raid. " +
                "🔴 A pawn already in a Lord is REFUSED, not silently dropped: Lord.AddPawnInternal only " +
                "Log.Errors when a pawn belongs to two lords, and LordMaker never surfaces that, so every " +
                "candidate is pre-checked with Pawn.GetLord() and reported in refused[] instead.",
            ResultDescription =
                "success, lordIndex, point, faction, memberCount (read off the new Lord's ownedPawns, " +
                "not the requested count), and refused[] naming every pawn that was NOT added and why.")]
        public static async Task<object> LordDefendSpawn(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids/names to put in the new Lord. Required.")]
            string pawns = null,
            [ToolParameter(Description = "FactionDef for the Lord. Empty uses the first resolved pawn's own Faction.")]
            string faction = null,
            [ToolParameter(Description = "Defend point 'x,z'. Empty uses the centroid of the resolved pawns' positions.")]
            string point = null,
            [ToolParameter(Description = "How far members wander from the point while idle. Empty uses the engine default.")]
            float wanderRadius = -1f,
            [ToolParameter(Description = "How far members will chase a threat before returning. Empty uses the engine default.")]
            float defendRadius = -1f,
            [ToolParameter(Description = "Allow this Lord to be sent out with a caravan.")]
            bool isCaravanSendable = false,
            [ToolParameter(Description = "Add the flee-when-outmatched toil. Default true, matching the engine default.")]
            bool addFleeToil = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                List<object> refused;
                var found = ResolveLordCandidates(pawns, map, out refused);
                if (found.Count == 0) return Fail("No pawn resolved to put in the Lord. Nothing was created.", new { refused });

                Faction fac = null;
                if (!string.IsNullOrWhiteSpace(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                else
                {
                    fac = found[0].Faction;
                    if (fac == null) return Fail("No 'faction' given and " + found[0].LabelShortCap + " has no Faction either. Give one explicitly.");
                }

                IntVec3 pt;
                if (!string.IsNullOrWhiteSpace(point))
                {
                    string perr2;
                    if (!TryParseCellLocal(point, out pt, out perr2)) return Fail(perr2);
                }
                else
                {
                    int sx = 0, sz = 0;
                    foreach (var p in found) { sx += p.Position.x; sz += p.Position.z; }
                    pt = new IntVec3(sx / found.Count, 0, sz / found.Count);
                }
                if (!pt.InBounds(map)) return Fail("Resolved point " + pt + " is out of bounds for this map.");

                LordJob_DefendPoint job;
                try
                {
                    job = new LordJob_DefendPoint(
                        pt,
                        wanderRadius >= 0f ? (float?)wanderRadius : null,
                        defendRadius >= 0f ? (float?)defendRadius : null,
                        isCaravanSendable,
                        addFleeToil);
                }
                catch (Exception e) { return Fail("LordJob_DefendPoint threw: " + e.GetType().Name + ": " + e.Message); }

                // MakeNewLord registers the Lord with lordManager before it can fail - snapshot the
                // count so a throw does not leave a jobless Lord ticking on this map forever.
                int lordsBefore = map.lordManager.lords.Count;
                Lord lord;
                try { lord = LordMaker.MakeNewLord(fac, job, map, found); }
                catch (Exception e)
                {
                    int unwound = RemoveLordsAddedSince(map, lordsBefore);
                    return Fail("MakeNewLord threw: " + e.GetType().Name + ": " + e.Message +
                                " - " + unwound + " half-built Lord(s) were removed from this map's lordManager so nothing is left ticking without a job.");
                }
                if (lord == null)
                {
                    int unwound = RemoveLordsAddedSince(map, lordsBefore);
                    return Fail("MakeNewLord returned null." + (unwound > 0 ? " " + unwound + " half-built Lord(s) were removed from lordManager." : ""));
                }

                var notAdded = LordMembersNotAdded(lord, found);
                return (object)new
                {
                    success = true,
                    lordIndex = map.lordManager.lords.IndexOf(lord),
                    point = new { x = pt.x, z = pt.z },
                    faction = fac.def.defName,
                    requested = found.Count + refused.Count,
                    memberCount = lord.ownedPawns.Count,
                    members = lord.ownedPawns.Select(p => p.LabelShortCap).ToList(),
                    refused,
                    notAdded,
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/lord_assault_spawn",
            Description =
                "*** ACTS ON THE LIVE COLONY - THIS CREATES A REAL ATTACKING GROUP *** " +
                "LordMaker.MakeNewLord(faction, new LordJob_AssaultColony(...), map, pawns) - a live group " +
                "that attacks the colony, exactly the state graph a fired raid puts its own pawns into. " +
                "Unlike jawa/fire_raid this does NOT generate any pawns - it takes pawns THAT ALREADY " +
                "EXIST on the map (e.g. from jawa/spawn_batch) and turns them hostile-and-organized. " +
                "🔴 A pawn already in a Lord is REFUSED, not silently dropped - same pre-check as " +
                "jawa/lord_defend_spawn, for the identical Lord.AddPawnInternal trap.",
            ResultDescription =
                "success, lordIndex, faction, memberCount (off the new Lord's ownedPawns), the resolved " +
                "assault flags, and refused[] naming every pawn NOT added and why.")]
        public static async Task<object> LordAssaultSpawn(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids/names to put in the new Lord. Required.")]
            string pawns = null,
            [ToolParameter(Description = "FactionDef for the assaulters. Empty uses the first resolved pawn's own Faction.")]
            string faction = null,
            [ToolParameter(Description = "Allow kidnapping a downed colonist. Default true.")]
            bool canKidnap = true,
            [ToolParameter(Description = "Allow the group to give up and leave after a while, or when they've done enough damage. Default true.")]
            bool canTimeoutOrFlee = true,
            [ToolParameter(Description = "Dig in through walls instead of pathing around.")]
            bool sappers = false,
            [ToolParameter(Description = "Use the smart avoid-grid for pathing around defenses.")]
            bool useAvoidGridSmart = false,
            [ToolParameter(Description = "Allow stealing high-value items instead of only fighting. Default true.")]
            bool canSteal = true,
            [ToolParameter(Description = "Breach through walls with explosives instead of sapping.")]
            bool breachers = false,
            [ToolParameter(Description = "Allow raiders to pick up better weapons dropped on the ground.")]
            bool canPickUpOpportunisticWeapons = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                List<object> refused;
                var found = ResolveLordCandidates(pawns, map, out refused);
                if (found.Count == 0) return Fail("No pawn resolved to put in the Lord. Nothing was created.", new { refused });

                Faction fac = null;
                if (!string.IsNullOrWhiteSpace(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                else
                {
                    fac = found[0].Faction;
                    if (fac == null) return Fail("No 'faction' given and " + found[0].LabelShortCap + " has no Faction either. Give one explicitly.");
                }

                LordJob_AssaultColony job;
                try
                {
                    job = new LordJob_AssaultColony(
                        fac, canKidnap, canTimeoutOrFlee, sappers, useAvoidGridSmart, canSteal, breachers, canPickUpOpportunisticWeapons);
                }
                catch (Exception e) { return Fail("LordJob_AssaultColony threw: " + e.GetType().Name + ": " + e.Message); }

                // MakeNewLord registers the Lord with lordManager before it can fail - snapshot the
                // count so a throw does not leave a jobless Lord ticking on this map forever.
                int lordsBefore = map.lordManager.lords.Count;
                Lord lord;
                try { lord = LordMaker.MakeNewLord(fac, job, map, found); }
                catch (Exception e)
                {
                    int unwound = RemoveLordsAddedSince(map, lordsBefore);
                    return Fail("MakeNewLord threw: " + e.GetType().Name + ": " + e.Message +
                                " - " + unwound + " half-built Lord(s) were removed from this map's lordManager so nothing is left ticking without a job.");
                }
                if (lord == null)
                {
                    int unwound = RemoveLordsAddedSince(map, lordsBefore);
                    return Fail("MakeNewLord returned null." + (unwound > 0 ? " " + unwound + " half-built Lord(s) were removed from lordManager." : ""));
                }

                var notAdded = LordMembersNotAdded(lord, found);
                return (object)new
                {
                    success = true,
                    lordIndex = map.lordManager.lords.IndexOf(lord),
                    faction = fac.def.defName,
                    requested = found.Count + refused.Count,
                    memberCount = lord.ownedPawns.Count,
                    members = lord.ownedPawns.Select(p => p.LabelShortCap).ToList(),
                    flags = new { canKidnap, canTimeoutOrFlee, sappers, useAvoidGridSmart, canSteal, breachers, canPickUpOpportunisticWeapons },
                    refused,
                    notAdded,
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }
#endif // JAWA_GM_TOOLS

        private static bool TryParseCellLocal(string s, out IntVec3 cell, out string err)
        {
            cell = IntVec3.Invalid; err = null;
            var parts = (s ?? "").Split(',');
            int x, z;
            if (parts.Length != 2 || !int.TryParse(parts[0].Trim(), out x) || !int.TryParse(parts[1].Trim(), out z))
            { err = "point must be 'x,z'."; return false; }
            cell = new IntVec3(x, 0, z);
            return true;
        }

        // ================================================================
        //  Animals & training
        // ================================================================

        [Tool(
            "jawa/manhunter_preview",
            Description =
                "Resolve what a manhunter pack WOULD be, without spawning anything - " +
                "AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind(points, map) plus " +
                "GetAnimalsCount(kind, points). This is the raid_preview/incident_parms_preview idiom " +
                "applied to the ManhunterPack incident (workerClass IncidentWorker_AggressiveAnimals): " +
                "jawa/fire_incident with incidentDef=ManhunterPack already fires the real thing, but " +
                "reports only fired/canFireNow, never WHICH species or HOW MANY. Read-only.",
            ResultDescription =
                "success (the call itself always succeeds; the QUESTION can still have no answer), " +
                "points, animalKindFound, animalKind, animalKindLabel, combatPower, count.")]
        public static async Task<object> ManhunterPreview(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Threat points. <=0 uses the storyteller's current default for this map.")]
            float points = 0f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                float pts = points > 0f ? points : StorytellerUtility.DefaultThreatPointsNow(map);

                // 🔴 TryFindAggressiveAnimalKind is NOT deterministic and NOT side-effect-free: it runs
                // TryRandomElementByWeight, Rand.Value and Rand.Chance off the GLOBAL Rand state. A
                // "read-only" preview that advances the game's RNG stream changes every later roll in
                // the colony. Push/pop the state so this tool really is read-only, exactly as
                // Lord.SetJob does around its own graph seeding.
                PawnKindDef kind = null;
                bool found;
                Rand.PushState();
                try { found = AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind(pts, map, out kind); }
                catch (Exception e) { return Fail("TryFindAggressiveAnimalKind threw: " + e.GetType().Name + ": " + e.Message); }
                finally { Rand.PopState(); }

                int? count = null;
                if (found)
                {
                    try { count = AggressiveAnimalIncidentUtility.GetAnimalsCount(kind, pts); }
                    catch (Exception e) { return Fail("GetAnimalsCount threw: " + e.GetType().Name + ": " + e.Message); }
                }

                return (object)new
                {
                    success = true,
                    points = pts,
                    animalKindFound = found,
                    animalKind = kind != null ? kind.defName : null,
                    animalKindLabel = kind != null ? kind.label : null,
                    combatPower = kind != null ? (float?)kind.combatPower : null,
                    count,
                    note = found
                        ? "ONE DRAW from the same weighted resolution IncidentWorker_AggressiveAnimals uses - the pick is random, so calling this again can name a different species. Fire the real incident with jawa/fire_incident incidentDef=ManhunterPack; it will roll its own. The global Rand state was pushed/popped, so this preview did not perturb the colony's RNG."
                        : "No aggressive-animal PawnKindDef qualifies at these points on this map's biome(s) - that is a real answer, not a bridge failure.",
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/animal_resource_force",
            Description =
                "Force an animal's gatherable body resource to be ready NOW, instead of waiting on its " +
                "CompTick timer. mode='egg' drives CompEggLayer: eggAction='produce' sets the PRIVATE " +
                "eggProgress field to 1 by reflection (so CanLayNow is honestly true rather than the lay " +
                "being forced mid-cycle) and then calls ProduceEgg(), placing the resulting egg Thing next " +
                "to the animal - ProduceEgg builds the Thing but does NOT place it. " +
                "⚠️ eggProgress has NO bearing on CompEggLayer.Active, which is gender / " +
                "CurLifeStage.milkable / Sterile() / IsShambler only; ProduceEgg logs 'LayEgg while not " +
                "Active' and then produces the egg ANYWAY, so a male or immature animal still yields an " +
                "egg plus a red log line. A null egg means only that eggCountRange rolled 0. " +
                "eggAction='fertilize' " +
                "calls Fertilize(withMale) directly. mode='gatherable' targets whichever comp on the pawn " +
                "derives from CompHasGatherableBodyResource (CompMilkable, CompShearable, ...) - its " +
                "'fullness' field is PROTECTED with no public setter, so this sets it by reflection to " +
                "targetFullness, then optionally calls the public Gathered(doer) to actually place the " +
                "resource now, same as a real harvest interaction (including its AnimalGatherYield roll). " +
                "🔴 Gathered(doer) calls GenPlace.TryPlaceThing INTERNALLY and discards its bool return - a " +
                "failed placement (no free spot near doer) only logs a Verse.Log.Error line that no try/catch " +
                "here can see, and fullness is zeroed either way. gatherNow therefore verifies placement by " +
                "diffing the map's on-hand stack of the comp's ResourceDef (read by reflection, no public " +
                "getter) across the call, rather than trusting fullnessAfterGather==0 to mean 'placed'. doer " +
                "must be spawned on the SAME map as the animal - Gathered places at doer.Position/doer.Map, " +
                "not the animal's, so a cross-map doer is refused rather than silently misplacing the resource.",
            ResultDescription =
                "success, pawn, mode, and either eggProduced (thing, stackCount, placed) / fertilized " +
                "(withMale), or fullnessBefore/After plus gatheredThing {doer, fullnessAfterGather, " +
                "resourceDef, resourcePlacedOnMap, note} when gatherNow was used - resourcePlacedOnMap is " +
                "null (unverified) only if ResourceDef could not be resolved by reflection.")]
        public static async Task<object> AnimalResourceForce(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The animal's pawn id, thingId or name.")]
            string pawn = null,
            [ToolParameter(Description = "'egg' or 'gatherable'.")]
            string mode = "egg",
            [ToolParameter(Description = "mode='egg' only: 'produce' (default) or 'fertilize'.")]
            string eggAction = "produce",
            [ToolParameter(Description = "mode='egg', eggAction='fertilize' only: the male pawn id/name. May be omitted.")]
            string withMale = null,
            [ToolParameter(Description = "mode='gatherable' only: fullness to force, 0..1. Default 1.0 (fully topped up).")]
            float targetFullness = 1f,
            [ToolParameter(Description = "mode='gatherable' only: also call Gathered(doer) to place the resource now.")]
            bool gatherNow = false,
            [ToolParameter(Description = "mode='gatherable', gatherNow=true only: pawn credited with gathering (affects the AnimalGatherYield roll). Empty picks a free colonist.")]
            string doer = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");

                var m = (mode ?? "egg").Trim().ToLowerInvariant();

                if (m == "egg")
                {
                    var comp = p.AllComps != null ? p.AllComps.OfType<CompEggLayer>().FirstOrDefault() : null;
                    if (comp == null) return Fail(p.LabelShortCap + " has no CompEggLayer.");

                    var a = (eggAction ?? "produce").Trim().ToLowerInvariant();
                    if (a == "fertilize")
                    {
                        Pawn male = null;
                        if (!string.IsNullOrWhiteSpace(withMale))
                        {
                            string merr; male = FindPawn(withMale, out merr);
                            if (male == null) return Fail(merr);
                        }
                        try { comp.Fertilize(male); }
                        catch (Exception e) { return Fail("Fertilize threw: " + e.GetType().Name + ": " + e.Message); }
                        return new
                        {
                            success = true, pawn = p.LabelShortCap, mode = m, eggAction = "fertilize",
                            withMale = male != null ? male.LabelShortCap : null,
                            fullyFertilized = comp.FullyFertilized,
                            ticksGame = TicksGameSafe(),
                        };
                    }
                    if (a == "produce")
                    {
                        object eggProgressBefore = GmReadPrivateField(typeof(CompEggLayer), comp, "eggProgress");
                        bool forced = GmWritePrivateField(typeof(CompEggLayer), comp, "eggProgress", 1f);
                        if (!forced) return Fail("Could not set CompEggLayer.eggProgress by reflection - field layout may have changed.");

                        Thing egg;
                        try { egg = comp.ProduceEgg(); }
                        catch (Exception e) { return Fail("ProduceEgg threw: " + e.GetType().Name + ": " + e.Message); }
                        if (egg == null)
                            return Fail(p.LabelShortCap + "'s eggCountRange rolled 0 - ProduceEgg() legitimately returned null this time. eggProgress was still forced to 1 and consumed.");

                        bool placed = false;
                        if (p.Spawned && p.Map != null)
                        {
                            try { placed = GenPlace.TryPlaceThing(egg, p.Position, p.Map, ThingPlaceMode.Near); }
                            catch (Exception e) { return Fail("Placing the produced egg threw: " + e.GetType().Name + ": " + e.Message); }
                        }

                        return new
                        {
                            success = true, pawn = p.LabelShortCap, mode = m, eggAction = "produce",
                            eggProgressBefore, eggProgressForcedTo = 1f,
                            eggProduced = new { defName = egg.def != null ? egg.def.defName : null, stackCount = egg.stackCount },
                            placed,
                            note = placed ? null : (p.Spawned ? "TryPlaceThing failed to find a spot near " + p.LabelShortCap + "." : p.LabelShortCap + " is not spawned on a map - the egg Thing exists but was not placed anywhere."),
                            ticksGame = TicksGameSafe(),
                        };
                    }
                    return Fail("eggAction must be 'produce' or 'fertilize'.");
                }

                if (m == "gatherable")
                {
                    var comp = p.AllComps != null ? p.AllComps.OfType<CompHasGatherableBodyResource>().FirstOrDefault() : null;
                    if (comp == null) return Fail(p.LabelShortCap + " has no CompHasGatherableBodyResource (no CompMilkable/CompShearable/etc.).");

                    // 🔴 float.NaN passes BOTH clamp comparisons (every comparison against NaN is
                    // false), so an unvalidated targetFullness would be written straight into the
                    // comp's protected field. fullness += num keeps NaN forever, ActiveAndFull
                    // (fullness >= 1f) is false forever, and it survives into the save.
                    if (float.IsNaN(targetFullness) || float.IsInfinity(targetFullness))
                        return Fail("targetFullness must be a real number in 0..1, got " + targetFullness +
                                    ". Writing NaN/Infinity into the comp's fullness would permanently break it - refusing.");
                    float clamped = targetFullness < 0f ? 0f : (targetFullness > 1f ? 1f : targetFullness);

                    // 🔴 Resolve and validate the doer BEFORE writing fullness. Doing it after meant
                    // every doer refusal below returned Fail with the animal's fullness ALREADY
                    // rewritten - a reported total failure that had in fact half-run.
                    Pawn doerPawn = null;
                    if (gatherNow)
                    {
                        if (!string.IsNullOrWhiteSpace(doer))
                        {
                            string derr; doerPawn = FindPawn(doer, out derr);
                            if (doerPawn == null) return Fail(derr);
                        }
                        else if (p.Map != null)
                        {
                            doerPawn = p.Map.mapPawns.FreeColonists.FirstOrDefault();
                        }
                        if (doerPawn == null) return Fail("gatherNow=true needs a 'doer' pawn (or a free colonist on " + p.LabelShortCap + "'s map) - Gathered(Pawn) is not null-safe.");

                        // CompHasGatherableBodyResource.Gathered places the resource at doer.Position on
                        // doer.Map, not near the animal - an explicit 'doer' that is unspawned or on a
                        // different map would silently place the resource somewhere never asked for.
                        // (p unspawned means p.Map is null, which this same test refuses: Gathered also
                        // dereferences parent.Map for the wasted-yield mote.)
                        if (!doerPawn.Spawned || doerPawn.Map != p.Map || p.Map == null)
                            return Fail("doer pawn '" + doerPawn.LabelShortCap + "' is not spawned on " + p.LabelShortCap +
                                        "'s map. Gathered(Pawn) places the resource at the DOER's position/map, not the " +
                                        "animal's - refusing rather than silently placing it somewhere unexpected.");
                    }

                    float fullnessBefore = comp.Fullness;
                    bool forced = GmWritePrivateField(typeof(CompHasGatherableBodyResource), comp, "fullness", clamped);
                    if (!forced) return Fail("Could not set CompHasGatherableBodyResource.fullness by reflection - field layout may have changed.");
                    float fullnessAfterForce = comp.Fullness;

                    object gatheredThing = null;
                    if (gatherNow)
                    {
                        // 🔴 VERIFIED AGAINST SOURCE (RimWorld/CompHasGatherableBodyResource.cs): Gathered(doer)
                        // calls GenPlace.TryPlaceThing itself and DISCARDS its bool return - a failed placement
                        // (no free spot near the doer) produces only a Verse.Log.Error line inside TryPlaceThing,
                        // which does NOT throw, so a try/catch around Gathered() cannot see it. fullness is
                        // unconditionally zeroed by Gathered() regardless of whether the Thing it created ever
                        // landed on the map, so fullnessAfterGather==0 alone cannot tell "gathered" from
                        // "created then dropped nowhere". ResourceDef is protected with no public getter, so it
                        // is read by reflection (GmReadPrivateProperty) to diff the map's on-hand stack of that
                        // def across the call - the only way to observe TryPlaceThing's outcome from outside.
                        ThingDef resourceDef = GmReadPrivateProperty(comp.GetType(), comp, "ResourceDef") as ThingDef;
                        int stackBefore = (resourceDef != null && p.Map != null) ? p.Map.listerThings.ThingsOfDef(resourceDef).Sum(t => t.stackCount) : 0;

                        try { comp.Gathered(doerPawn); }
                        catch (Exception e)
                        {
                            return Fail("Gathered threw: " + e.GetType().Name + ": " + e.Message +
                                        " - NOT a no-op: fullness was already forced from " + fullnessBefore + " to " + fullnessAfterForce +
                                        " before the call, and it now reads " + comp.Fullness + ". Some resource may have been placed.");
                        }

                        int stackAfter = (resourceDef != null && p.Map != null) ? p.Map.listerThings.ThingsOfDef(resourceDef).Sum(t => t.stackCount) : 0;
                        bool? resourcePlacedOnMap = resourceDef != null ? (bool?)(stackAfter > stackBefore) : null;

                        gatheredThing = new
                        {
                            doer = doerPawn.LabelShortCap,
                            fullnessAfterGather = comp.Fullness,
                            resourceDef = resourceDef != null ? resourceDef.defName : null,
                            resourcePlacedOnMap,
                            note = resourceDef == null
                                ? "Could not resolve this comp's ResourceDef by reflection - Gathered() ran, but whether anything actually landed on the map is UNVERIFIED."
                                : (resourcePlacedOnMap == true
                                    ? null
                                    : "No new " + resourceDef.defName + " appeared on the map's stock after Gathered(). Either the " +
                                      "AnimalGatherYield roll wasted the yield (normal, by design - see Verse's ThrowText mote) or " +
                                      "GenPlace.TryPlaceThing found no free spot near " + doerPawn.LabelShortCap + " and silently " +
                                      "dropped the Thing it created - Gathered() discards TryPlaceThing's return value, so the engine " +
                                      "itself cannot distinguish these two cases either."),
                        };
                    }

                    return new
                    {
                        success = true,
                        pawn = p.LabelShortCap,
                        mode = m,
                        compType = comp.GetType().Name,
                        fullnessBefore,
                        fullnessAfterForce,
                        gatherNow,
                        gathered = gatheredThing,
                        ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("mode must be 'egg' or 'gatherable'.");
            }).ConfigureAwait(false);
        }
    }
}
