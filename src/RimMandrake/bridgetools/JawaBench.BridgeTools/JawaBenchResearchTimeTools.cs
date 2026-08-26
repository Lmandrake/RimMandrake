// JawaBenchResearchTimeTools.cs - research/technology and time/ticks/speed.
//
// WHY THIS FILE EXISTS
// =====================
// BRIDGE_TOOLS_EASY_BLOCK_1, out of `design/Jawa/bridge/dll_capability_roster.html`.
//
// Measured 2026-08-25: zero of the existing `jawa/…` names touch
// `RimWorld.ResearchManager` or `Verse.ResearchProjectDef` at all - the ENTIRE
// research domain was absent from the bridge before this file. Time/ticks had a
// couple of incidental reads elsewhere (event tools stamp `ticksGame` into some
// results) but no dedicated clock, speed or date tools either.
//
// EVERY SIGNATURE BELOW WAS READ FROM 1.6 DECOMPILED SOURCE, NOT GUESSED:
//   RimWorld/ResearchManager.cs, Verse/ResearchProjectDef.cs, Verse/TickManager.cs,
//   Verse/TimeSlower.cs, RimWorld/GenDate.cs.
//
// 🔴 REAPPLYALLMODS - the roster's own warning, checked against source:
//   `ResearchManager.FinishProject(...)` and `DebugSetAllProjectsFinished()` BOTH
//   already call `ReapplyAllMods()` internally (ResearchManager.cs:441 and :572).
//   `AddProgress`, `AddTechprints`, `SetCurrentProject`, `StopProject` and
//   `ResetAllProgress` do NOT. Every tool below that edits research state calls
//   `ReapplyAllMods()` itself after the edit anyway - belt-and-suspenders where
//   the engine already does it, REQUIRED where it does not - and every result
//   says `reapplyUnlocksCalled: true` so a caller never has to wonder.
//
// 🔴 DebugSetTicksGame DOES NOT SIMULATE. It only overwrites the private tick
// counter - no ticker passes run, no incidents fire, no plants grow, no jobs
// advance. A caller expecting "10 days pass" to behave like waiting 10 days
// will be silently wrong. The tool Description says so; do not trust a story
// beat to this method.
//
// 🔑 ResearchProjectDef lives in namespace VERSE (Verse/ResearchProjectDef.cs),
// not RimWorld, despite ResearchManager itself being in RimWorld. Both are in
// scope here already via the `using` list below.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared helpers for this file only -----------------------------

        private static ResearchProjectDef FindResearchProject(string defName, out string err)
        {
            err = null;
            if (string.IsNullOrEmpty(defName))
            {
                err = "Give a ResearchProjectDef defName.";
                return null;
            }
            var proj = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(defName.Trim());
            if (proj == null)
            {
                err = "No ResearchProjectDef named '" + defName + "'.";
            }
            return proj;
        }

        private static object ResearchProjectSnapshot(ResearchProjectDef proj)
        {
            return new
            {
                defName = proj.defName,
                label = proj.LabelCap.ToString(),
                cost = proj.Cost,
                baseCost = proj.baseCost,
                progress = Find.ResearchManager.GetProgress(proj),
                isFinished = proj.IsFinished,
                techprintsApplied = proj.TechprintsApplied,
                techprintCount = proj.TechprintCount,
                techprintRequirementMet = proj.TechprintRequirementMet,
                isCurrentProject = Find.ResearchManager.IsCurrentProject(proj),
            };
        }

        // =====================================================================
        // RESEARCH & TECHNOLOGY
        // =====================================================================

        [Tool(
            "jawa/research_finish_project",
            Description =
                "Finish a research project immediately via ResearchManager.FinishProject - " +
                "recursively finishes any unfinished prerequisites first, tops up techprints " +
                "to satisfy the gate, sets progress to full Cost, and grants every unlock. " +
                "This is a blunt WRITE for test setup (e.g. 'give me the bench this recipe " +
                "needs'), not a simulation of normal play - no research points are spent, no " +
                "researcher does the work. FinishProject calls ReapplyAllMods() internally " +
                "(verified against 1.6 source); this tool calls it again explicitly so the " +
                "guarantee holds regardless of engine internals.",
            ResultDescription =
                "success, project snapshot (defName, label, cost, progress, isFinished, " +
                "techprint state, isCurrentProject), wasAlreadyFinished (read before the " +
                "call), prerequisitesTouched (defNames that were not finished going in), " +
                "reapplyUnlocksCalled=true.")]
        public static async Task<object> ResearchFinishProject(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ResearchProjectDef defName to finish.")]
            string project,
            [ToolParameter(Description = "Show the in-game completion dialog popup. Default false - this is a headless call.")]
            bool doCompletionDialog = false,
            [ToolParameter(Description = "Send the project's discovered letter, if it defines one. Default true, matching the game's own default.")]
            bool doCompletionLetter = true,
            [ToolParameter(Description = "Optional pawn id/name/thingId credited with the completion tale. Omit for none.")]
            string researcher = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                ResearchProjectDef proj = FindResearchProject(project, out perr);
                if (proj == null) return Fail(perr);

                Pawn researcherPawn = null;
                if (!string.IsNullOrEmpty(researcher))
                {
                    string ferr;
                    researcherPawn = FindPawn(researcher, out ferr);
                    if (researcherPawn == null) return Fail("researcher: " + ferr);
                }

                bool wasAlreadyFinished = proj.IsFinished;
                var prereqsTouched = new List<string>();
                if (proj.prerequisites != null)
                    foreach (var p in proj.prerequisites)
                        if (p != null && !p.IsFinished) prereqsTouched.Add(p.defName);

                Find.ResearchManager.FinishProject(proj, doCompletionDialog, researcherPawn, doCompletionLetter);
                // Required by the roster's own warning; harmless if FinishProject's
                // internal call already covered it.
                Find.ResearchManager.ReapplyAllMods();

                return new
                {
                    success = true,
                    wasAlreadyFinished,
                    prerequisitesTouched = prereqsTouched,
                    reapplyUnlocksCalled = true,
                    doCompletionDialog,
                    doCompletionLetter,
                    researcher = researcherPawn != null ? researcherPawn.LabelShortCap : null,
                    result = ResearchProjectSnapshot(proj),
                };
            });
        }

        [Tool(
            "jawa/research_progress",
            Description =
                "Edit which project is being researched or how far along it is. Three " +
                "actions in one tool because they are the same small ResearchManager surface: " +
                "'add' calls AddProgress(project, amount) - partial progress, clamped to the " +
                "project's Cost; if this finishes the project, AddProgress calls FinishProject " +
                "internally (which itself calls ReapplyAllMods). 'set_current' calls " +
                "SetCurrentProject(project) - makes it the active research (only takes effect " +
                "if baseCost > 0). 'stop' calls StopProject(project) - clears it as the active " +
                "project if, and only if, it currently is one. This tool always calls " +
                "ReapplyAllMods() after 'add', whether or not the project finished.",
            ResultDescription =
                "success, action, project snapshot read back AFTER the edit, " +
                "currentProject (defName of whatever ResearchManager.GetProject() returns " +
                "now, or null), reapplyUnlocksCalled (true for 'add', false for the other two " +
                "actions since they change no progress).")]
        public static async Task<object> ResearchProgress(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ResearchProjectDef defName.")]
            string project,
            [ToolParameter(Description = "'add' (default), 'set_current', or 'stop'.")]
            string action = "add",
            [ToolParameter(Description = "Progress points to add. 'add' only; ignored otherwise. AddProgress clamps to the project's Cost.")]
            float amount = 0f,
            [ToolParameter(Description = "Optional pawn id/name/thingId credited as the source. 'add' only.")]
            string source = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                ResearchProjectDef proj = FindResearchProject(project, out perr);
                if (proj == null) return Fail(perr);

                string act = (action ?? "add").Trim().ToLowerInvariant();
                bool reapplied = false;

                switch (act)
                {
                    case "add":
                    {
                        Pawn sourcePawn = null;
                        if (!string.IsNullOrEmpty(source))
                        {
                            string ferr;
                            sourcePawn = FindPawn(source, out ferr);
                            if (sourcePawn == null) return Fail("source: " + ferr);
                        }
                        Find.ResearchManager.AddProgress(proj, amount, sourcePawn);
                        Find.ResearchManager.ReapplyAllMods();
                        reapplied = true;
                        break;
                    }
                    case "set_current":
                        Find.ResearchManager.SetCurrentProject(proj);
                        break;
                    case "stop":
                        Find.ResearchManager.StopProject(proj);
                        break;
                    default:
                        return Fail("action must be 'add', 'set_current' or 'stop', got '" + action + "'.");
                }

                var current = Find.ResearchManager.GetProject();

                return new
                {
                    success = true,
                    action = act,
                    reapplyUnlocksCalled = reapplied,
                    currentProject = current != null ? current.defName : null,
                    result = ResearchProjectSnapshot(proj),
                };
            });
        }

        [Tool(
            "jawa/research_grant_techprints",
            Description =
                "Add techprints to a project via ResearchManager.AddTechprints(project, " +
                "amount) - the gate is ResearchProjectDef.TechprintRequirementMet, which stays " +
                "false (blocking CanStartNow) until enough are applied. AddTechprints clamps " +
                "the stored count to the project's TechprintCount, so over-granting is safe. " +
                "This does not touch progress, but ReapplyAllMods() is still called afterward " +
                "for consistency with every other write in this file.",
            ResultDescription =
                "success, amountRequested, techprintsBefore, project snapshot read back after " +
                "the write (techprintsApplied, techprintCount, techprintRequirementMet), " +
                "reapplyUnlocksCalled=true.")]
        public static async Task<object> ResearchGrantTechprints(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ResearchProjectDef defName.")]
            string project,
            [ToolParameter(Description = "Techprints to add. Clamped server-side to the project's TechprintCount.")]
            int amount)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                ResearchProjectDef proj = FindResearchProject(project, out perr);
                if (proj == null) return Fail(perr);

                int before = Find.ResearchManager.GetTechprints(proj);
                Find.ResearchManager.AddTechprints(proj, amount);
                Find.ResearchManager.ReapplyAllMods();

                return new
                {
                    success = true,
                    amountRequested = amount,
                    techprintsBefore = before,
                    reapplyUnlocksCalled = true,
                    result = ResearchProjectSnapshot(proj),
                };
            });
        }

        [Tool(
            "jawa/research_bulk",
            Description =
                "Blunt whole-database research edits for test starts. mode='finish_all' calls " +
                "ResearchManager.DebugSetAllProjectsFinished() - every ResearchProjectDef with " +
                "baseCost or knowledgeCost > 0 is marked complete (calls ReapplyAllMods() " +
                "internally, verified against source). mode='reset_all' calls " +
                "ResetAllProgress() - clears ALL progress, techprints, anomaly knowledge and " +
                "the current project back to nothing. ⚠️ ResetAllProgress does NOT revert " +
                "recipes/buildings/etc a project already unlocked - ReapplyAllMods only ADDS " +
                "unlocks for projects that ARE finished, it never removes them for projects " +
                "that no longer are, which is an engine limitation this tool cannot paper " +
                "over. This tool calls ReapplyAllMods() after either mode regardless.",
            ResultDescription =
                "success, mode, finishedCountBefore, finishedCountAfter (both counted over " +
                "DefDatabase<ResearchProjectDef>, IsFinished), anyProjectAvailable (read back), " +
                "reapplyUnlocksCalled=true.")]
        public static async Task<object> ResearchBulk(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'finish_all' or 'reset_all'.")]
            string mode)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                string m = (mode ?? "").Trim().ToLowerInvariant();
                if (m != "finish_all" && m != "reset_all")
                    return Fail("mode must be 'finish_all' or 'reset_all', got '" + mode + "'.");

                int before = DefDatabase<ResearchProjectDef>.AllDefsListForReading.Count(d => d.IsFinished);

                if (m == "finish_all")
                {
                    Find.ResearchManager.DebugSetAllProjectsFinished();
                }
                else
                {
                    Find.ResearchManager.ResetAllProgress();
                }
                Find.ResearchManager.ReapplyAllMods();

                int after = DefDatabase<ResearchProjectDef>.AllDefsListForReading.Count(d => d.IsFinished);

                return new
                {
                    success = true,
                    mode = m,
                    finishedCountBefore = before,
                    finishedCountAfter = after,
                    anyProjectAvailable = Find.ResearchManager.AnyProjectIsAvailable,
                    reapplyUnlocksCalled = true,
                };
            });
        }

        [Tool(
            "jawa/research_reapply_unlocks",
            Description =
                "Call ResearchManager.ReapplyAllMods() directly - it walks every finished " +
                "ResearchProjectDef and calls ReapplyAllMods() on each, which is what actually " +
                "wires up the recipes/buildables/etc a completed project unlocks. Use this if " +
                "you suspect a direct edit (yours or another tool's) left progress numbers " +
                "right but unlocks stale. READ-adjacent in effect - it grants nothing new, it " +
                "only re-applies what finished projects already say should exist.",
            ResultDescription =
                "success, finishedProjectCount (how many defs it walked), reapplyUnlocksCalled=true.")]
        public static async Task<object> ResearchReapplyUnlocks(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                int finishedCount = DefDatabase<ResearchProjectDef>.AllDefsListForReading.Count(d => d.IsFinished);
                Find.ResearchManager.ReapplyAllMods();

                return new
                {
                    success = true,
                    finishedProjectCount = finishedCount,
                    reapplyUnlocksCalled = true,
                };
            });
        }

        [Tool(
            "jawa/research_availability",
            Description =
                "READ ONLY. Answers 'can this project be started, and if not, why not' - " +
                "ResearchProjectDef.CanStartNow, .PrerequisitesCompleted, " +
                ".PlayerHasAnyAppropriateResearchBench and .TechprintRequirementMet, plus the " +
                "unfinished prerequisites and the required bench/facility defNames so a caller " +
                "does not have to cross-reference the def separately. Changes nothing.",
            ResultDescription =
                "success, project snapshot, canStartNow, prerequisitesCompleted, " +
                "playerHasAnyAppropriateResearchBench, techprintRequirementMet, " +
                "unfinishedPrerequisites[], requiredResearchBuilding (defName or null), " +
                "requiredResearchFacilities[] (defNames).")]
        public static async Task<object> ResearchAvailability(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ResearchProjectDef defName.")]
            string project)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                ResearchProjectDef proj = FindResearchProject(project, out perr);
                if (proj == null) return Fail(perr);

                var unfinishedPrereqs = new List<string>();
                if (proj.prerequisites != null)
                    foreach (var p in proj.prerequisites)
                        if (p != null && !p.IsFinished) unfinishedPrereqs.Add(p.defName);

                return new
                {
                    success = true,
                    canStartNow = proj.CanStartNow,
                    prerequisitesCompleted = proj.PrerequisitesCompleted,
                    playerHasAnyAppropriateResearchBench = proj.PlayerHasAnyAppropriateResearchBench,
                    techprintRequirementMet = proj.TechprintRequirementMet,
                    unfinishedPrerequisites = unfinishedPrereqs,
                    requiredResearchBuilding = proj.requiredResearchBuilding != null ? proj.requiredResearchBuilding.defName : null,
                    requiredResearchFacilities = proj.requiredResearchFacilities != null
                        ? proj.requiredResearchFacilities.Select(f => f.defName).ToList()
                        : new List<string>(),
                    result = ResearchProjectSnapshot(proj),
                };
            });
        }

        // =====================================================================
        // TIME, TICKS & SPEED
        // =====================================================================

        [Tool(
            "jawa/time_clock",
            Description =
                "READ ONLY. TickManager.TicksGame, .TicksAbs, .TicksSinceSettle and " +
                ".StartingYear, plus a few adjacent trivially-readable fields (SettleTick, " +
                "HasSettledNewColony, CurTimeSpeed, Paused) that answer 'what time is it and " +
                "is it moving' in one call. Changes nothing.",
            ResultDescription =
                "success, ticksGame, ticksAbs, ticksSinceSettle, startingYear, settleTick, " +
                "hasSettledNewColony, curTimeSpeed (string), paused.")]
        public static async Task<object> TimeClock(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");
                var tm = Find.TickManager;
                return new
                {
                    success = true,
                    ticksGame = tm.TicksGame,
                    ticksAbs = tm.TicksAbs,
                    ticksSinceSettle = tm.TicksSinceSettle,
                    startingYear = tm.StartingYear,
                    settleTick = tm.SettleTick,
                    hasSettledNewColony = tm.HasSettledNewColony,
                    curTimeSpeed = tm.CurTimeSpeed.ToString(),
                    paused = tm.Paused,
                };
            });
        }

        [Tool(
            "jawa/time_set_ticks",
            Description =
                "⚠️ JUMPS THE CLOCK WITHOUT SIMULATING. Calls " +
                "TickManager.DebugSetTicksGame(ticks), which only overwrites the internal tick " +
                "counter - no ticker pass runs, so no incidents fire, no needs decay, no jobs " +
                "advance, no growth happens, nothing that would occur while time actually " +
                "passed occurs. It is a debug-menu instant scrub, not fast-forward. If you want " +
                "events to happen, this is the wrong tool. WRITE - reads TicksGame back after " +
                "the call to confirm it took.",
            ResultDescription =
                "success, ticksRequested, ticksGameBefore, ticksGameAfter (read back), " +
                "note reiterating that nothing was simulated.")]
        public static async Task<object> TimeSetTicks(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "New value for TickManager.TicksGame.")]
            int ticks)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");
                var tm = Find.TickManager;
                int before = tm.TicksGame;
                tm.DebugSetTicksGame(ticks);
                return new
                {
                    success = true,
                    ticksRequested = ticks,
                    ticksGameBefore = before,
                    ticksGameAfter = tm.TicksGame,
                    note = "The clock jumped. Nothing was simulated - no incidents, needs, jobs or growth ran for the skipped span.",
                };
            });
        }

        [Tool(
            "jawa/time_date_at",
            Description =
                "READ ONLY. Human-readable date/season at a longitude+latitude, via " +
                "GenDate.DateFullStringAt(absTicks, Vector2), .Quadrum(absTicks, longitude) and " +
                ".Season(absTicks, Vector2). Defaults to the current map's location " +
                "(Find.WorldGrid.LongLatOf(map.Tile)) and the current absolute tick " +
                "(TickManager.TicksAbs) - pass latitude/longitude and/or ticksAbs to probe a " +
                "different place or moment instead. Fails if neither a current map nor an " +
                "explicit latitude+longitude is available.",
            ResultDescription =
                "success, absTicksUsed, latitude, longitude, dateFullString, quadrum (string), " +
                "season (string), source (\"current map\" or \"explicit lat/long\").")]
        public static async Task<object> TimeDateAt(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Latitude. Omit, with longitude, to use the current map's location.")]
            float? latitude = null,
            [ToolParameter(Description = "Longitude. Omit, with latitude, to use the current map's location.")]
            float? longitude = null,
            [ToolParameter(Description = "Absolute tick to read the date at. Omit for the current moment (TickManager.TicksAbs).")]
            long? ticksAbs = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");

                float lat, lon;
                string source;
                if (latitude.HasValue && longitude.HasValue)
                {
                    lat = latitude.Value;
                    lon = longitude.Value;
                    source = "explicit lat/long";
                }
                else if (Find.CurrentMap != null && Find.WorldGrid != null)
                {
                    Vector2 longLat = Find.WorldGrid.LongLatOf(Find.CurrentMap.Tile);
                    lon = longLat.x;
                    lat = longLat.y;
                    source = "current map";
                }
                else
                {
                    return Fail("No current map and no explicit latitude+longitude given - nowhere to read a date at.");
                }

                long abs = ticksAbs ?? Find.TickManager.TicksAbs;
                var location = new Vector2(lon, lat);

                return new
                {
                    success = true,
                    absTicksUsed = abs,
                    latitude = lat,
                    longitude = lon,
                    dateFullString = GenDate.DateFullStringAt(abs, location),
                    quadrum = GenDate.Quadrum(abs, lon).ToString(),
                    season = GenDate.Season(abs, location).ToString(),
                    source,
                };
            });
        }

        [Tool(
            "jawa/time_pin_normal_speed",
            Description =
                "Force normal game speed the same way combat does - calls " +
                "Find.TickManager.slower.SignalForceNormalSpeed(), which holds speed at Normal " +
                "for roughly 800 ticks (TimeSlower's own constant) even if the player has " +
                "selected a faster speed. It does not change CurTimeSpeed itself and does not " +
                "unpause; it only blocks speed-up for that window. Reads " +
                "slower.ForcedNormalSpeed back to confirm the signal took.",
            ResultDescription =
                "success, forcedNormalSpeedAfter (bool, read back), ticksGameAtCall.")]
        public static async Task<object> TimePinNormalSpeed(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");
                var tm = Find.TickManager;
                tm.slower.SignalForceNormalSpeed();
                return new
                {
                    success = true,
                    forcedNormalSpeedAfter = tm.slower.ForcedNormalSpeed,
                    ticksGameAtCall = tm.TicksGame,
                };
            });
        }

        [Tool(
            "jawa/time_perf",
            Description =
                "READ ONLY. TickManager.MeanTickTime (smoothed per-tick cost), .TicksThisFrame " +
                "(how many sim ticks the last frame ran to catch up) and .TickRateMultiplier - " +
                "answers 'is the game actually keeping up with the selected speed'. Changes " +
                "nothing.",
            ResultDescription =
                "success, meanTickTime, ticksThisFrame, tickRateMultiplier, curTimeSpeed (string).")]
        public static async Task<object> TimePerf(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");
                var tm = Find.TickManager;
                return new
                {
                    success = true,
                    meanTickTime = tm.MeanTickTime,
                    ticksThisFrame = tm.TicksThisFrame,
                    tickRateMultiplier = tm.TickRateMultiplier,
                    curTimeSpeed = tm.CurTimeSpeed.ToString(),
                };
            });
        }
    }
}
