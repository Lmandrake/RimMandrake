// JawaBenchStoryTools.cs - five gems found by cross-checking every Find.X static
// accessor (Verse/Find.cs, ~75 of them) against the live tool surface: 43 were
// completely untouched. Most are rendering/UI internals with no capability worth
// exposing; these five are not.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   RimWorld/AlertsReadout.cs   activeAlerts - PRIVATE List<Alert> (this is the
//                               UNCERTAIN row the original roster flagged: "needs
//                               reflection" - resolved here, one field, everything
//                               else on Alert itself is public).
//   RimWorld/Alert.cs           Active, Label, GetExplanation(), Priority - all public.
//   RimWorld/TaleManager.cs     AllTalesListForReading - PUBLIC.
//   RimWorld/TaleRecorder.cs    RecordTale(TaleDef, params object[] args) - the ONLY
//                               way to attach free text to a pawn, per this file's
//                               own earlier finding in JawaBenchPawnTools.cs: the
//                               engine has no pawn note field, and TaleRecorder is
//                               how GravshipUtility/SettleUtility etc. do it
//                               themselves (RecordTale(def, pawn).customLabel = "...").
//   RimWorld/Tale.cs            def, customLabel, date, hidden, ShortSummary - public.
//   RimWorld/StoryWatcher.cs    statsRecord, watcherAdaptation - public fields.
//   RimWorld/StatsRecord.cs     numRaidsEnemy, numThreatBigs, colonistsKilled,
//                               colonistsLaunched, greatestPopulation - public ints.
//   RimWorld/StoryWatcher_Adaptation.cs   AdaptDays, TotalThreatPointsFactor - public
//                               read-only properties; this is the actual number that
//                               scales every future threat, and nothing on the
//                               bridge could read it before now.
//   RimWorld/GoodwillSituationManager.cs   GetSituations/GetMaxGoodwill/
//                               GetNaturalGoodwill/GetExplanation(Faction) - all public.
//
// 🔴 jawa/tale_record IS SCOPED DOWN ON PURPOSE. TaleFactory.MakeRawTale(def, args)
// fills a Tale subclass's fields by matching arg TYPES, not by a documented
// positional contract, and different TaleDefs expect different shapes (0-2 Pawns,
// sometimes a ThingDef/DamageInfo/SkillDef too). Rather than guess a generic
// multi-type arg binder, this tool supports the pattern the engine's OWN callers use
// for player-facing custom labels (RecordTale(def, pawn[, otherPawn]).customLabel =
// "..."), which is the one thing this project actually needed a fix for.
//
// GATING: none of these five are gated - all are reads, or (tale_record) the same
// tier as a Tale the game itself already writes constantly during normal play; it
// carries no mechanical effect, only flavor text and art-generation weighting.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections;
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
        // ================================================================
        //  Alerts - the roster's own UNCERTAIN row, resolved
        // ================================================================

        [Tool(
            "jawa/alerts_list",
            Description =
                "Read every currently ACTIVE alert - the same list the top-right alert stack " +
                "draws. AlertsReadout.activeAlerts is private, read here by reflection (one " +
                "field); every member read off each Alert afterward (Active, Label, " +
                "GetExplanation(), Priority) is public. Read-only. This is the roster's own " +
                "UNCERTAIN row from BRIDGE_CAPABILITY_ROSTER.md - resolved, not guessed.",
            ResultDescription = "success, count, alerts[] (type, label, priority, explanation).")]
        public static async Task<object> AlertsList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var readout = Find.Alerts;
                if (readout == null) return Fail("No active AlertsReadout - is the game running?");

                var list = FieldOrNull(readout, "activeAlerts") as IEnumerable;
                if (list == null) return Fail("AlertsReadout.activeAlerts could not be read by reflection - field may have been renamed.");

                var rows = new List<object>();
                foreach (var obj in list)
                {
                    var alert = obj as Alert;
                    if (alert == null) continue;
                    string explanation;
                    try { explanation = alert.GetExplanation().ToString(); }
                    catch (Exception e) { explanation = "(GetExplanation threw " + e.GetType().Name + ")"; }
                    rows.Add(new
                    {
                        type = alert.GetType().FullName,
                        active = alert.Active,
                        label = alert.Label,
                        priority = alert.Priority.ToString(),
                        explanation
                    });
                }

                return new { success = true, count = rows.Count, alerts = rows, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Tales - read, and the free-text-on-a-pawn answer
        // ================================================================

        [Tool(
            "jawa/tale_list",
            Description =
                "Read every Tale in TaleManager - TaleManager.AllTalesListForReading. Each " +
                "carries def, customLabel (the only free text a Tale exposes), date, hidden, " +
                "Unused, InterestLevel, ShortSummary. Read-only.",
            ResultDescription = "success, totalCount (every Tale the manager holds), returned (rows after " +
                "the filter and the limit), tales[] (id, def, customLabel, date, ageTicks, hidden, unused, " +
                "interestLevel, shortSummary).")]
        public static async Task<object> TaleList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only rows where customLabel is set. Default false.")]
            bool onlyWithCustomLabel = false,
            [ToolParameter(Description = "Cap on returned rows. Default 200.")]
            int limit = 200)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.TaleManager == null) return Fail("No active TaleManager - is a game loaded?");

                // Enumerable.Take returns an EMPTY sequence for a non-positive count, so an
                // unguarded limit<=0 would answer "success, 0 tales" on a colony full of them.
                if (limit <= 0) return Fail("'limit' must be 1 or more; " + limit + " would return no rows while reporting success.");

                var all = Find.TaleManager.AllTalesListForReading;
                var filtered = onlyWithCustomLabel ? all.Where(t => !string.IsNullOrEmpty(t.customLabel)) : all.AsEnumerable();
                // Tale.AgeTicks is TicksAbs - date, so it is meaningless on a tale whose date
                // was never set (the -1 default); report the raw date alongside it either way.
                int ticksAbs = Find.TickManager != null ? Find.TickManager.TicksAbs : 0;
                var rows = filtered.Take(limit).Select(t => new
                {
                    id = t.id,
                    def = t.def != null ? t.def.defName : null,
                    customLabel = t.customLabel,
                    date = t.date,
                    ageTicks = t.date >= 0 && Find.TickManager != null ? (int?)(ticksAbs - t.date) : null,
                    hidden = t.hidden,
                    unused = t.Unused,
                    interestLevel = t.InterestLevel,
                    shortSummary = t.ShortSummary
                }).ToList();

                return new { success = true, totalCount = all.Count, returned = rows.Count, tales = rows, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/tale_record",
            Description =
                "The ANSWER to 'there is no free-text note field on a pawn' - " +
                "TaleRecorder.RecordTale(def, pawn[, otherPawn]).customLabel = text, exactly " +
                "the pattern GravshipUtility/SettleUtility use for their own custom-labeled " +
                "tales. Scoped to 1-2 Pawn args on purpose: TaleFactory.MakeRawTale fills a " +
                "Tale subclass's fields by matching ARG TYPES, and different TaleDefs expect " +
                "different shapes (some want a ThingDef or DamageInfo too) - rather than guess " +
                "a generic binder, this covers the pawn-only pattern the engine's own callers " +
                "use most. ⚠️ A TaleDef can have def.ignoreChance > 0 (a random roll can drop " +
                "the tale silently) and ⚠️ colonistOnly/usableWithChildren can refuse it - " +
                "checked and reported, not left to look like nothing happened.",
            ResultDescription =
                "success, taleId, def, customLabel, shortSummary. On refusal: reason " +
                "(ignoreChanceRoll / colonistOnlyRefused / notUsableWithChildren / other).")]
        public static async Task<object> TaleRecord(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "TaleDef defName, e.g. 'Recruited', 'TileSettled', 'BondedWithAnimal'. Required.")]
            string taleDef = null,
            [ToolParameter(Description = "First pawn id, thingId or name. Required.")]
            string pawn = null,
            [ToolParameter(Description = "Second pawn id, thingId or name. Optional - only some TaleDefs use one.")]
            string otherPawn = null,
            [ToolParameter(Description = "Free text to attach as the tale's customLabel. Optional.")]
            string customLabel = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.TaleManager == null) return Fail("No active TaleManager - is a game loaded?");

                if (string.IsNullOrWhiteSpace(taleDef)) return Fail("Give 'taleDef'.");
                var td = DefDatabase<TaleDef>.GetNamedSilentFail(taleDef.Trim());
                if (td == null) return Fail("No TaleDef '" + taleDef + "'.", DefSuggestions<TaleDef>(taleDef));

                string err;
                var p1 = FindPawn(pawn, out err);
                if (p1 == null) return Fail(err);

                Pawn p2 = null;
                if (!string.IsNullOrWhiteSpace(otherPawn))
                {
                    p2 = FindPawn(otherPawn, out err);
                    if (p2 == null) return Fail(err);
                }

                Tale tale;
                try { tale = p2 != null ? TaleRecorder.RecordTale(td, p1, p2) : TaleRecorder.RecordTale(td, p1); }
                catch (Exception e) { return Fail("RecordTale threw " + e.GetType().Name + ": " + e.Message); }

                if (tale == null)
                {
                    string reason = "unknown - RecordTale returned null. Possible causes: def.ignoreChance random roll, " +
                                     "def.colonistOnly with no player-faction pawn in args, def.usableWithChildren=false with a non-adult pawn, " +
                                     "or TaleFactory.MakeRawTale could not match def.taleClass to the args given.";
                    return Fail("RecordTale returned null - the tale was not created. " + reason,
                        new { taleDef = td.defName, ignoreChance = td.ignoreChance, colonistOnly = td.colonistOnly, usableWithChildren = td.usableWithChildren });
                }

                if (!string.IsNullOrWhiteSpace(customLabel)) tale.customLabel = customLabel;

                return new
                {
                    success = true,
                    taleId = tale.id,
                    def = td.defName,
                    customLabel = tale.customLabel,
                    shortSummary = tale.ShortSummary,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Story/adaptation stats
        // ================================================================

        [Tool(
            "jawa/story_stats",
            Description =
                "Read colony story-tracking state - StoryWatcher.statsRecord (numRaidsEnemy, " +
                "numThreatBigs, colonistsKilled, colonistsLaunched, greatestPopulation) and " +
                "StoryWatcher_Adaptation (AdaptDays, TotalThreatPointsFactor). ⭐ " +
                "TotalThreatPointsFactor is the actual multiplier applied to every FUTURE " +
                "threat's points based on recent colonist losses - nothing on this bridge " +
                "could read it before now; jawa/weather_get's threat-points read is the " +
                "STORYTELLER's current roll, this is the adaptation factor feeding it. " +
                "Read-only.",
            ResultDescription =
                "success, numRaidsEnemy, numThreatBigs, colonistsKilled, colonistsLaunched, " +
                "greatestPopulation, adaptDays, totalThreatPointsFactor.")]
        public static async Task<object> StoryStats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Find.StoryWatcher == null) return Fail("No active game/StoryWatcher.");

                var sw = Find.StoryWatcher;
                var stats = sw.statsRecord;
                var adapt = sw.watcherAdaptation;

                return new
                {
                    success = true,
                    numRaidsEnemy = stats?.numRaidsEnemy,
                    numThreatBigs = stats?.numThreatBigs,
                    colonistsKilled = stats?.colonistsKilled,
                    colonistsLaunched = stats?.colonistsLaunched,
                    greatestPopulation = stats?.greatestPopulation,
                    adaptDays = adapt?.AdaptDays,
                    totalThreatPointsFactor = adapt?.TotalThreatPointsFactor,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Faction goodwill situations
        // ================================================================

        [Tool(
            "jawa/faction_goodwill_situations",
            Description =
                "Read WHY a faction's goodwill is capped or offset - " +
                "GoodwillSituationManager.GetSituations/GetMaxGoodwill/GetNaturalGoodwill for " +
                "one faction (permanent-enemy status, ideology conflicts, and any other " +
                "GoodwillSituationDef currently in effect). Extends jawa/faction_goodwill_check " +
                "with the BREAKDOWN, not just the number. " +
                "⛔ REFUSES on a faction with Faction.HasGoodwill == false (hidden, or temporary): " +
                "GoodwillSituationManager.Recalculate returns early for those, leaving an EMPTY " +
                "situation list, and GetMaxGoodwill/GetNaturalGoodwill then hand back their " +
                "sentinels 100 and 0 - which read exactly like a measured 'uncapped, unaffected'. " +
                "⚠️ NOT strictly read-only. GetSituations recomputes on a cache miss, and the " +
                "cache is empty until GoodwillManagerTick first runs (TicksGame % 1000), so on a " +
                "just-loaded or paused game this call can drive the engine's own hostility-" +
                "threshold check early and fire its letter. It only brings forward what the next " +
                "tick would do; it never invents a change.",
            ResultDescription =
                "success, faction, maxGoodwill, naturalGoodwillOffset, situations[] (defName, " +
                "label, maxGoodwill, naturalGoodwillOffset).")]
        public static async Task<object> FactionGoodwillSituations(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName. Required.")]
            string faction = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.FactionManager == null) return Fail("No active FactionManager - is a game loaded?");

                if (string.IsNullOrWhiteSpace(faction)) return Fail("Give 'faction', a FactionDef defName.");
                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                var fac = Find.FactionManager.FirstFactionOfDef(fd);
                if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                if (fac.IsPlayer) return Fail("'" + faction + "' resolved to the player faction - goodwill situations are only tracked for other factions.");
                // GoodwillSituationManager.Recalculate is `if (!other.HasGoodwill) return;` over a
                // cleared list, so an ungated call here would report maxGoodwill 100 /
                // naturalGoodwillOffset 0 / situations [] for a hidden or temporary faction - the
                // manager's sentinels, indistinguishable from a real reading.
                if (!fac.HasGoodwill)
                    return Fail("'" + faction + "' has Faction.HasGoodwill == false (hidden=" + fac.Hidden
                        + ", temporary=" + fac.temporary + "), so no goodwill situation is tracked for it. "
                        + "Every number this tool could return would be the manager's sentinel "
                        + "(maxGoodwill 100, naturalGoodwillOffset 0, no situations), not a measurement.",
                        new { faction = fac.Name, hidden = fac.Hidden, temporary = fac.temporary, defHidden = fac.def != null && fac.def.hidden });

                var mgr = Find.GoodwillSituationManager;
                if (mgr == null) return Fail("No active GoodwillSituationManager.");

                List<GoodwillSituationManager.CachedSituation> situations;
                try { situations = mgr.GetSituations(fac); }
                catch (Exception e) { return Fail("GetSituations threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    faction = fac.Name,
                    maxGoodwill = mgr.GetMaxGoodwill(fac),
                    naturalGoodwillOffset = mgr.GetNaturalGoodwill(fac),
                    situations = (situations ?? new List<GoodwillSituationManager.CachedSituation>()).Select(s => new
                    {
                        defName = s.def != null ? s.def.defName : null,
                        label = s.def != null ? s.def.LabelCap.ToString() : null,
                        maxGoodwill = s.maxGoodwill,
                        naturalGoodwillOffset = s.naturalGoodwillOffset
                    }).ToList(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
