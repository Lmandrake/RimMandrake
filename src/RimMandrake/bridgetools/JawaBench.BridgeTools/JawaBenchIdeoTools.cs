// JawaBenchIdeoTools.cs - the live route around "Ideology classic mode is set at world
// creation and cannot be retrofitted."
//
// CORRECT_ASHKARR_IDEOLOGY_1 / ASHKARR_IDEOLOGY_MODE_CALL_1
// ===========================================================
// Ash'karr was created with Ideology in classic mode, so its twelve authored ideoligions
// (every FactionDef with fixedIdeo=true, ideoName, ideoDescription, deityPresets,
// requiredPreceptsOnly) were never applied - the world holds one shared vanilla ideoligion
// instead. The original reading of this (CHECK, 2026-08-26) concluded a full world
// recreation was the only route. It was wrong, source-verified, not guessed:
//
//   RimWorld/FactionIdeosTracker.cs's ChooseOrGenerateIdeo(IdeoGenerationParms parms) is the
//   ORDINARY method the game itself calls to assign a faction's ideo - nothing about it is
//   world-creation-only. When parms.fixedIdeo is true it takes priority over every
//   classic-mode branch and calls IdeoGenerator.MakeFixedIdeo(parms), which builds a FULL
//   (non-classic) Ideo from parms.deities/name/description regardless of the save's global
//   Find.IdeoManager.classicMode flag - that flag is a plain mutable per-save bool, not a
//   world-creation lock (the game's own Page_ChooseIdeoPreset sets it directly at runtime).
//   Ideo.classicMode is a SEPARATE per-Ideo field that MakeFixedIdeo never sets true, so
//   IdeoFoundation.GenerateLeaderTitle (which checks ideo.classicMode) generates a real
//   leader title, not the generic "leader" fallback.
//
// Owner's ruling, 2026-08-29: "no world re-creation, we will just load it in and patch the
// world religion setting."
//
// SCOPE: this changes the FACTION's primaryIdeo, exactly what ChooseOrGenerateIdeo does at
// ordinary faction generation. It does NOT reassign existing believers already generated
// under the old ideo - Pawn_IdeoTracker is per-pawn and untouched here. New pawns generated
// for this faction going forward pick up the new primaryIdeo via the normal generation path.
// Reassigning existing believers, if wanted, is a separate call against Pawn_IdeoTracker -
// not attempted here, not guessed at.
//
// NOT a duplicate of jawa/ideo_create + jawa/ideo_set_primary, checked before writing this.
// jawa/ideo_create calls IdeoGenerator.GenerateIdeo (its own doc comment: "picks a RANDOM
// IdeoFoundationDef", rolls memes "appropriate to faction") and exposes no fixedIdeo, deities
// or requiredPreceptsOnly parameter at all - it cannot reproduce a fixedIdeo=true FactionDef's
// authored deities/required-precepts-only constraint, only a themed-random ideo. This tool
// calls IdeoGenerator.MakeFixedIdeo via ChooseOrGenerateIdeo(fixedIdeo: true) instead, and
// does the generate+assign-primary step in one call, matching ChooseOrGenerateIdeo's own
// semantics rather than the two-call create-then-set-primary flow.
//
// Thread affinity, same rule as every other file here: everything touching game state is
// inside ctx.MainThread.InvokeAsync and nothing else is.

using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/faction_ideo_set",
            Description =
                "Assigns a NEW, FULL fixed ideoligion to an existing faction on the LIVE save, " +
                "replacing its current primaryIdeo - the live route around Ideology 'classic " +
                "mode' being a world-creation-only setting, which it is not. Reads " +
                "ideoName/ideoDescription/deityPresets/requiredPreceptsOnly straight off the " +
                "named FactionDef (must declare fixedIdeo=true) and calls " +
                "FactionIdeosTracker.ChooseOrGenerateIdeo with fixedIdeo=true - the exact same " +
                "call the game makes at ordinary faction generation. Regardless of the save's " +
                "global classic-mode flag, the resulting Ideo is a real ideoligion: leader " +
                "titles generate from the faction's CultureDef, not the generic 'leader' " +
                "fallback. " +
                "⚠️ Does NOT reassign existing believers already generated under the OLD ideo - " +
                "only the faction's primaryIdeo changes; new pawns pick it up going forward. " +
                "⚠️ Irreversible in the sense that the old Ideo object is dropped from the " +
                "faction (still registered in IdeoManager, just no longer primary) - back up " +
                "the save first on anything but a scratch map.",
            ResultDescription =
                "success, factionDefName, oldIdeoName, oldIdeoId, newIdeoName, newIdeoId, " +
                "leaderTitleMale, leaderTitleFemale, memeCount, preceptCount, classicModeGlobal " +
                "(the save's Find.IdeoManager.classicMode, unchanged by this call, informational " +
                "only), newIdeoClassicMode (should be false - the whole point).")]
        public static async Task<object> FactionIdeoSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "FactionDef defName. Must declare fixedIdeo=true - this tool is for fixed-ideo " +
                "factions only, not fluid/random ones.")]
            string factionDefName,
            [ToolParameter(Description =
                "Must be true. Confirms this replaces the faction's current primary ideo, " +
                "which cannot be undone by this tool.")]
            bool confirmReplace = false)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (string.IsNullOrWhiteSpace(factionDefName))
                return Fail("factionDefName is required.");
            if (!confirmReplace)
                return Fail("confirmReplace must be true - this replaces the faction's " +
                            "current primaryIdeo, which this tool cannot undo.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(factionDefName.Trim());
                if (fd == null)
                    return Fail("No FactionDef '" + factionDefName + "'.",
                        DefSuggestions<FactionDef>(factionDefName));

                if (!fd.fixedIdeo)
                    return Fail("FactionDef '" + factionDefName + "' does not declare " +
                                "fixedIdeo=true - this tool is for fixed-ideo factions only.");

                var faction = Find.FactionManager?.FirstFactionOfDef(fd);
                if (faction == null)
                    return Fail("FactionDef '" + factionDefName + "' exists but no such " +
                                "faction was generated in this world.");
                if (faction.ideos == null)
                    return Fail("Faction '" + faction.Name + "' has no FactionIdeosTracker - " +
                                "is Ideology active? (ModsConfig.IdeologyActive)");

                var oldIdeo = faction.ideos.PrimaryIdeo;

                var parms = new IdeoGenerationParms(
                    forFaction: fd,
                    fixedIdeo: true,
                    name: fd.ideoName ?? "",
                    description: fd.ideoDescription ?? "",
                    deities: fd.deityPresets,
                    forcedMemes: fd.forcedMemes,
                    requiredPreceptsOnly: fd.requiredPreceptsOnly);

                faction.ideos.ChooseOrGenerateIdeo(parms);
                var newIdeo = faction.ideos.PrimaryIdeo;

                if (newIdeo == null)
                    return Fail("ChooseOrGenerateIdeo ran but the faction's primaryIdeo is " +
                                "still null - unexpected, needs investigation before trusting " +
                                "this tool further.");

                return (object)new
                {
                    success = true,
                    factionDefName,
                    oldIdeoName = oldIdeo?.name,
                    oldIdeoId = oldIdeo?.id,
                    newIdeoName = newIdeo.name,
                    newIdeoId = newIdeo.id,
                    leaderTitleMale = newIdeo.leaderTitleMale,
                    leaderTitleFemale = newIdeo.leaderTitleFemale,
                    memeCount = newIdeo.memes?.Count ?? 0,
                    preceptCount = newIdeo.PreceptsListForReading?.Count ?? 0,
                    classicModeGlobal = Find.IdeoManager?.classicMode,
                    newIdeoClassicMode = newIdeo.classicMode,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/faction_ideo_get",
            Description =
                "READ ONLY. Reports a faction's current primaryIdeo - name, leader titles, " +
                "meme/precept counts, and whether it is running in classic mode. Use before " +
                "and after jawa/faction_ideo_set to prove the change landed.",
            ResultDescription =
                "success, factionDefName, ideoName, ideoId, leaderTitleMale, leaderTitleFemale, " +
                "memeCount, preceptCount, classicMode, believerCount.")]
        public static async Task<object> FactionIdeoGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName.")] string factionDefName)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (string.IsNullOrWhiteSpace(factionDefName))
                return Fail("factionDefName is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(factionDefName.Trim());
                if (fd == null)
                    return Fail("No FactionDef '" + factionDefName + "'.",
                        DefSuggestions<FactionDef>(factionDefName));

                var faction = Find.FactionManager?.FirstFactionOfDef(fd);
                if (faction == null)
                    return Fail("FactionDef '" + factionDefName + "' exists but no such " +
                                "faction was generated in this world.");

                var ideo = faction.ideos?.PrimaryIdeo;
                if (ideo == null)
                    return (object)new
                    {
                        success = true,
                        factionDefName,
                        ideoName = (string)null,
                        note = "faction has no primaryIdeo (Ideology inactive, or none assigned yet)"
                    };

                int believers = 0;
                try
                {
                    believers = PawnsFinder.All_AliveOrDead
                        .Count(p => p.Ideo == ideo);
                }
                catch { believers = -1; }

                return (object)new
                {
                    success = true,
                    factionDefName,
                    ideoName = ideo.name,
                    ideoId = ideo.id,
                    leaderTitleMale = ideo.leaderTitleMale,
                    leaderTitleFemale = ideo.leaderTitleFemale,
                    memeCount = ideo.memes?.Count ?? 0,
                    preceptCount = ideo.PreceptsListForReading?.Count ?? 0,
                    classicMode = ideo.classicMode,
                    believerCount = believers,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/pawn_ideo_reassign
        // =====================================================================
        // jawa/faction_ideo_set only changes a FACTION's primaryIdeo - existing believers,
        // already generated under the old ideo, keep it. This is the follow-up: reassign
        // every pawn currently belonging to a faction onto that faction's CURRENT primaryIdeo.
        //
        // Pawn_IdeoTracker.SetIdeo (RimWorld/Pawn_IdeoTracker.cs:183-242) handles every side
        // effect itself - believer-count recache, a HistoryEvent, certainty reset, forbidden
        // bed/bond cleanup, a letter if a bond is broken. Nothing else needs calling. It also
        // silently no-ops on a baby pawn or a same-ideo call (checked via before/after, not by
        // guessing the DevelopmentalStage gate independently) - reported here as a skip, not a
        // success. Mirrors the shape vanilla's own DebugActionsIdeo.SetIdeo() and
        // BackCompatibilityConverter_1_2 use for exactly this kind of bulk reassignment.
        [Tool(
            "jawa/pawn_ideo_reassign",
            Description =
                "Reassigns every pawn belonging to a faction onto that faction's CURRENT " +
                "primaryIdeo, via Pawn_IdeoTracker.SetIdeo - the same call the game's own debug " +
                "tools use, which handles every side effect itself (believer-count recache, " +
                "certainty reset, forbidden bed/bond cleanup) with nothing else to call " +
                "manually. The follow-up to jawa/faction_ideo_set, which only changes the " +
                "FACTION's primaryIdeo and leaves existing believers on their old ideo. " +
                "⚠️ Processes ALIVE AND DEAD pawns across every map, caravan and world-pawn " +
                "list (PawnsFinder.All_AliveOrDead filtered by Faction) - not just the current " +
                "map. A pawn with no ideo tracker (Ideology inactive, or a non-ideo-bearing " +
                "race) is reported, not silently skipped.",
            ResultDescription =
                "success, factionDefName, targetIdeoName, targetIdeoId, pawnsMatched, " +
                "reassigned, skippedSameIdeo, skippedNoChange (SetIdeo ran but the ideo did " +
                "not change - e.g. a baby), noIdeoTracker, truncated (true if pawnsMatched > " +
                "limit), results[] of {pawnId, name, before, after, outcome}.")]
        public static async Task<object> PawnIdeoReassign(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "FactionDef defName. Every pawn currently belonging to this faction is " +
                "reassigned to the faction's CURRENT primaryIdeo (see jawa/faction_ideo_get).")]
            string factionDefName,
            [ToolParameter(Description =
                "Must be true. Confirms this changes potentially many pawns' Ideo at once, " +
                "which this tool cannot undo.")]
            bool confirmReplace = false,
            [ToolParameter(Description =
                "Cap on pawns actually processed in one call, so a very large faction cannot " +
                "silently take a long time. pawnsMatched reports the true total either way.",
                DefaultValue = 200)]
            int limit = 200)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (string.IsNullOrWhiteSpace(factionDefName))
                return Fail("factionDefName is required.");
            if (!confirmReplace)
                return Fail("confirmReplace must be true - this reassigns potentially many " +
                            "pawns' Ideo, which this tool cannot undo.");
            if (limit <= 0)
                return Fail("limit must be > 0.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(factionDefName.Trim());
                if (fd == null)
                    return Fail("No FactionDef '" + factionDefName + "'.",
                        DefSuggestions<FactionDef>(factionDefName));

                var faction = Find.FactionManager?.FirstFactionOfDef(fd);
                if (faction == null)
                    return Fail("FactionDef '" + factionDefName + "' exists but no such " +
                                "faction was generated in this world.");

                var targetIdeo = faction.ideos?.PrimaryIdeo;
                if (targetIdeo == null)
                    return Fail("Faction '" + faction.Name + "' has no primaryIdeo to " +
                                "reassign onto - run jawa/faction_ideo_set first, or Ideology " +
                                "is inactive.");

                var matched = PawnsFinder.All_AliveOrDead
                    .Where(p => p.Faction == faction)
                    .ToList();

                int reassigned = 0, skippedSame = 0, skippedNoChange = 0, noTracker = 0;
                var results = new List<object>();
                foreach (var pawn in matched.Take(limit))
                {
                    if (pawn.ideo == null)
                    {
                        noTracker++;
                        results.Add(new
                        {
                            pawnId = pawn.thingIDNumber, name = pawn.LabelShortCap,
                            before = (string)null, after = (string)null,
                            outcome = "no_ideo_tracker"
                        });
                        continue;
                    }

                    var before = pawn.ideo.Ideo;
                    if (before == targetIdeo)
                    {
                        skippedSame++;
                        results.Add(new
                        {
                            pawnId = pawn.thingIDNumber, name = pawn.LabelShortCap,
                            before = before?.name, after = before?.name,
                            outcome = "skipped_same_ideo"
                        });
                        continue;
                    }

                    pawn.ideo.SetIdeo(targetIdeo);
                    var after = pawn.ideo.Ideo;
                    string outcome;
                    if (after == targetIdeo) { reassigned++; outcome = "reassigned"; }
                    else { skippedNoChange++; outcome = "skipped_no_change"; }

                    results.Add(new
                    {
                        pawnId = pawn.thingIDNumber, name = pawn.LabelShortCap,
                        before = before?.name, after = after?.name, outcome
                    });
                }

                return (object)new
                {
                    success = true,
                    factionDefName,
                    targetIdeoName = targetIdeo.name,
                    targetIdeoId = targetIdeo.id,
                    pawnsMatched = matched.Count,
                    reassigned,
                    skippedSameIdeo = skippedSame,
                    skippedNoChange,
                    noIdeoTracker = noTracker,
                    truncated = matched.Count > limit,
                    results,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
