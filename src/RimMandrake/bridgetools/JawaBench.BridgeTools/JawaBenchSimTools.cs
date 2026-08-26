// JawaBenchSimTools.cs - weather/temperature reads, storyteller & incident-queue
// control, and the FIRST bridge tools that touch the animal domain at all.
//
// BRIDGE_TOOLS_EASY_BLOCK_1, out of design/Jawa/bridge/dll_capability_roster.html.
//
// 🔑 Measured 2026-08-25, zero of the ~120 `jawa/…` names before this file
// touched Pawn_TrainingTracker, RecruitUtility or RelationsUtility - training,
// taming, recruiting and bonding an animal could not be driven from the bridge
// at all. This file is where that domain starts.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/WeatherDecider.cs, Verse/SkyManager.cs, Verse/GenTemperature.cs,
//   Verse/MapTemperature.cs, RimWorld/StorytellerUtility.cs, RimWorld/Storyteller.cs,
//   RimWorld/IncidentQueue.cs, RimWorld/QueuedIncident.cs, RimWorld/Difficulty.cs,
//   RimWorld/SignalManager.cs, RimWorld/Signal.cs, RimWorld/SignalArgs.cs,
//   RimWorld/Pawn_TrainingTracker.cs, RimWorld/RecruitUtility.cs,
//   RimWorld/InteractionWorker_RecruitAttempt.cs, RimWorld/RelationsUtility.cs.
//
// THREE TRAPS THE ROSTER FLAGGED, CONFIRMED IN SOURCE:
//  * SkyManager.ForceSetCurSkyGlow sets a private float directly, but
//    SkyManagerUpdate() overwrites it from the weather/celestial state on
//    EVERY Update() call - the very next frame. Reading it back right after
//    the call is real (nothing has ticked yet), so this tool reports it
//    honestly, but the Description says out loud that it will not hold.
//  * MapTemperature.OutdoorTemp has a GETTER ONLY - it derives from
//    Find.World.tileTemperatures / the biome / the pocket-map def, never a
//    stored field. There is no companion "set" tool here and there cannot be
//    one; jawa/cell_temperature is read-only for exactly this reason.
//  * WeatherDecider.ticksWhenRainAllowedAgain (what DisableRainFor writes) is
//    PRIVATE with no public accessor anywhere in RimWorld.Storyteller or
//    WeatherDecider itself - not even DebugQueueReadout-style. jawa/rain_suppress
//    reads it back by reflection rather than silently trusting the call, which
//    is the same "about 40 calls report success and change nothing" trap this
//    project is full of.
//
// GATING: everything that WRITES to the live colony sits behind
// #if JAWA_GM_TOOLS, matching jawa/weather_set and jawa/game_condition in
// JawaBenchEventTools.cs. Only the two pure reads (cell_temperature,
// incident_parms_preview) are always compiled in.
//
// THREAD AFFINITY: same rule as every other file here - everything that
// touches game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared helpers, private to THIS file only -----------------------

        /// <summary>
        /// Reads a private instance field by reflection. Used exactly once, for
        /// WeatherDecider.ticksWhenRainAllowedAgain, which has no public getter -
        /// this is a readback, not a workaround for a missing API elsewhere.
        /// </summary>
        private static object SimPrivateField(object obj, string name)
        {
            if (obj == null) return null;
            FieldInfo fi = obj.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance);
            if (fi == null) return null;
            try { return fi.GetValue(obj); }
            catch (Exception) { return null; }
        }

        private static bool TryParseCell(string s, out IntVec3 cell, out string err)
        {
            cell = IntVec3.Invalid; err = null;
            if (string.IsNullOrEmpty(s)) { err = "Give a cell as 'x,z'."; return false; }
            var parts = s.Split(',');
            int x, z;
            if (parts.Length != 2 || !int.TryParse(parts[0].Trim(), out x) || !int.TryParse(parts[1].Trim(), out z))
            { err = "cell must be 'x,z'."; return false; }
            cell = new IntVec3(x, 0, z);
            return true;
        }

        // ======================================================================
        // WEATHER / TEMPERATURE / CONDITIONS - reads always in, writes gated.
        // ======================================================================

        [Tool(
            "jawa/cell_temperature",
            Description =
                "Read the EFFECTIVE temperature at one cell - GenTemperature.TryGetTemperatureForCell, " +
                "which checks direct air temperature first and falls back to the air-around-thing " +
                "reading when the cell holds something impassable (a wall, a door). READ ONLY: " +
                "there is no setter to pair with this. MapTemperature.OutdoorTemp - also reported " +
                "for context - has a GETTER ONLY in 1.6 source; it derives live from the world tile, " +
                "the biome and (for a pocket map) the map generator def, so it cannot be assigned.",
            ResultDescription =
                "success, resolved cell, ok (whether TryGetTemperatureForCell found a direct or " +
                "fallback reading), temperature, and outdoorTemp/seasonalTemp for comparison.")]
        public static async Task<object> CellTemperature(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell 'x,z'. Omit if 'pawn' is given.")] string cell = null,
            [ToolParameter(Description = "Pawn id, thingId or name - reads at its position. Omit if 'cell' is given.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                IntVec3 c;
                if (!string.IsNullOrEmpty(pawn))
                {
                    string perr; var p = FindPawn(pawn, out perr);
                    if (p == null) return Fail(perr);
                    c = p.Position;
                }
                else
                {
                    string cerr;
                    if (!TryParseCell(cell, out c, out cerr)) return Fail(cerr);
                }

                if (!c.InBounds(map))
                    return Fail("Cell " + c.x + "," + c.z + " is out of bounds for a " + map.Size.x + "x" + map.Size.z + " map.");

                float temp;
                bool ok = GenTemperature.TryGetTemperatureForCell(c, map, out temp);

                return (object)new
                {
                    success = true,
                    cell = new { x = c.x, z = c.z },
                    ok,
                    temperature = temp,
                    outdoorTemp = map.mapTemperature.OutdoorTemp,
                    seasonalTemp = map.mapTemperature.SeasonalTemp,
                    note = ok
                        ? null
                        : "TryGetTemperatureForCell found neither a direct air reading nor an impassable " +
                          "thing to read around at this cell; 'temperature' falls back to the map default (21C).",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/incident_parms_preview",
            Description =
                "Build the IncidentParms an incident would actually need, without firing anything - " +
                "StorytellerUtility.DefaultParmsNow(category, map) plus DefaultThreatPointsNow(map). " +
                "This is the general form of what jawa/raid_preview does only for raids: give it ANY " +
                "IncidentCategoryDef (or an IncidentDef, whose category is read off it) and see the " +
                "points/faction/strategy/arrivalMode the storyteller would resolve right now. An " +
                "incident fired with hand-built parms instead of these is the usual reason one silently " +
                "does nothing - use this to build parms worth passing to jawa/incident_schedule.",
            ResultDescription = "success, category, defaultParms, currentThreatPoints, categoryDefs[].")]
        public static async Task<object> IncidentParmsPreview(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "IncidentCategoryDef name, e.g. ThreatBig, ThreatSmall, Misc. Default ThreatBig.")]
            string category = "ThreatBig",
            [ToolParameter(Description = "IncidentDef name instead of 'category' - its own category is read off it and wins.")]
            string incidentDef = null,
            [ToolParameter(Description = "List every IncidentCategoryDef name too.")] bool listCategories = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                IncidentCategoryDef cat;
                if (!string.IsNullOrEmpty(incidentDef))
                {
                    var idef = DefDatabase<IncidentDef>.GetNamedSilentFail(incidentDef.Trim());
                    if (idef == null) return Fail("No IncidentDef '" + incidentDef + "'.", DefSuggestions<IncidentDef>(incidentDef));
                    if (idef.category == null) return Fail("IncidentDef '" + idef.defName + "' has no category defined.");
                    cat = idef.category;
                }
                else
                {
                    cat = DefDatabase<IncidentCategoryDef>.GetNamedSilentFail((category ?? "ThreatBig").Trim());
                    if (cat == null) return Fail("No IncidentCategoryDef '" + category + "'.", DefSuggestions<IncidentCategoryDef>(category));
                }

                IncidentParms parms;
                try { parms = StorytellerUtility.DefaultParmsNow(cat, map); }
                catch (Exception e) { return Fail("DefaultParmsNow threw: " + e.GetType().Name + ": " + e.Message); }

                float threat = -1f;
                try { threat = StorytellerUtility.DefaultThreatPointsNow(map); } catch { }

                return (object)new
                {
                    success = true,
                    category = cat.defName,
                    incidentDef = !string.IsNullOrEmpty(incidentDef) ? incidentDef.Trim() : null,
                    defaultParms = new
                    {
                        points = parms.points,
                        faction = parms.faction != null ? parms.faction.def.defName : null,
                        raidStrategy = parms.raidStrategy != null ? parms.raidStrategy.defName : null,
                        raidArrivalMode = parms.raidArrivalMode != null ? parms.raidArrivalMode.defName : null,
                        podOpenDelay = parms.podOpenDelay,
                        forced = parms.forced,
                    },
                    currentThreatPoints = threat,
                    note = "target is always the current map, matching every other GM tool here. " +
                           "faction/raidStrategy/raidArrivalMode read null here for the same reason " +
                           "jawa/raid_preview flags them null - most workers resolve those lazily in " +
                           "CanFireNow/TryExecute, not in DefaultParmsNow.",
                    categoryDefs = listCategories
                        ? DefDatabase<IncidentCategoryDef>.AllDefsListForReading.Select(d => d.defName).ToList()
                        : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/weather_roll_next",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Make WeatherDecider pick and transition to a new " +
                "weather RIGHT NOW - WeatherDecider.StartNextWeather(), the exact call the map makes " +
                "on its own once curWeatherAge passes its rolled duration. Unlike jawa/weather_set, " +
                "this does not let you CHOOSE the weather - it lets the game's own commonality-weighted " +
                "roll happen early. A GameCondition_ForceWeather lock (see jawa/weather_set lock=true) " +
                "still wins: ChooseNextWeather returns the forced weather unconditionally when one is set.",
            ResultDescription = "success, before/after weather and curWeatherAge, and whether a weather lock was in force.")]
        public static async Task<object> WeatherRollNext(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var wm = map.weatherManager;

                var before = new { weather = wm.curWeather != null ? wm.curWeather.defName : null, curWeatherAge = wm.curWeatherAge };
                var forced = map.weatherDecider.ForcedWeather;

                try { map.weatherDecider.StartNextWeather(); }
                catch (Exception e) { return Fail("StartNextWeather threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    before,
                    after = new { weather = wm.curWeather != null ? wm.curWeather.defName : null, curWeatherAge = wm.curWeatherAge },
                    lockedTo = forced != null ? forced.defName : null,
                    note = forced != null
                        ? "A GameCondition_ForceWeather is active - ChooseNextWeather returns it unconditionally, so 'after' should equal '" + forced.defName + "'."
                        : "No weather lock active - the roll used the map's normal commonality weights.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/rain_suppress",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Block rain-rate weather from being rolled for N " +
                "ticks - WeatherDecider.DisableRainFor(ticks). It does NOT stop rain already in " +
                "progress and does NOT touch the game clock; it only zeroes the commonality of any " +
                "weather with rainRate > 0.1 the next time ChooseNextWeather runs, until the deadline " +
                "passes. ⚠️ The tick it writes (ticksWhenRainAllowedAgain) is PRIVATE with no public " +
                "getter anywhere in source, so this tool reads it back by reflection rather than " +
                "trusting the call blindly.",
            ResultDescription = "success, ticksGame, the deadline tick read back by reflection, and ticksRemaining.")]
        public static async Task<object> RainSuppress(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "How many ticks from now rain stays suppressed. Must be > 0.")]
            int ticks = 60000)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (ticks <= 0) return Fail("ticks must be > 0.");

                object before = SimPrivateField(map.weatherDecider, "ticksWhenRainAllowedAgain");

                try { map.weatherDecider.DisableRainFor(ticks); }
                catch (Exception e) { return Fail("DisableRainFor threw: " + e.GetType().Name + ": " + e.Message); }

                object after = SimPrivateField(map.weatherDecider, "ticksWhenRainAllowedAgain");
                int? afterInt = after as int?;
                int nowTicks = TicksGameSafe();

                return (object)new
                {
                    success = true,
                    before,
                    after,
                    ticksRemaining = afterInt.HasValue && nowTicks >= 0 ? (int?)(afterInt.Value - nowTicks) : null,
                    note = "'after' is read back from the private field WeatherDecider.ticksWhenRainAllowedAgain " +
                           "by reflection - there is no public getter for it in 1.6 source. Rain already " +
                           "falling is unaffected; this only stops rain from being ROLLED again.",
                    ticksGame = nowTicks,
                };
            });
        }

        [Tool(
            "jawa/sky_glow_set",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Push the sky lighting directly, two different ways. " +
                "skyGlow uses SkyManager.ForceSetCurSkyGlow(float) - ⚠️ ADVISORY ONLY: it writes a " +
                "private float that SkyManagerUpdate() recomputes from the weather/celestial state on " +
                "EVERY Update() call, i.e. the very next frame. The readback here is real (nothing has " +
                "ticked between the write and the read), but do not expect it to hold. targetBrightness " +
                "uses GameConditionManager.SetTargetBrightness(target, lerpSeconds) instead - the same " +
                "mechanism an eclipse or solar flare uses - which LERPS MapBrightness toward the target " +
                "over lerpSeconds of real time rather than snapping, so its readback will usually still " +
                "show the OLD value immediately after this call.",
            ResultDescription = "success, skyGlow{before,after} and/or brightness{before,after,target,lerpSeconds}.")]
        public static async Task<object> SkyGlowSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Force CurSkyGlow to this 0..1 value. Advisory - see Description.")]
            float? skyGlow = null,
            [ToolParameter(Description = "Lerp MapBrightness toward this 0..1 target instead.")]
            float? targetBrightness = null,
            [ToolParameter(Description = "Lerp duration in real seconds for targetBrightness. Default 5, matching the engine default.")]
            float lerpSeconds = 5f)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (!skyGlow.HasValue && !targetBrightness.HasValue)
                    return Fail("Give skyGlow and/or targetBrightness.");

                object skyGlowResult = null;
                if (skyGlow.HasValue)
                {
                    float before = map.skyManager.CurSkyGlow;
                    map.skyManager.ForceSetCurSkyGlow(skyGlow.Value);
                    skyGlowResult = new
                    {
                        before,
                        after = map.skyManager.CurSkyGlow,
                        note = "Will be overwritten on the next SkyManagerUpdate() call (next frame) - it is not durable.",
                    };
                }

                object brightnessResult = null;
                if (targetBrightness.HasValue)
                {
                    float before = map.gameConditionManager.MapBrightness;
                    map.gameConditionManager.SetTargetBrightness(targetBrightness.Value, lerpSeconds);
                    brightnessResult = new
                    {
                        before,
                        after = map.gameConditionManager.MapBrightness,
                        target = targetBrightness.Value,
                        lerpSeconds,
                        note = "MapBrightness lerps toward 'target' over 'lerpSeconds' of real time - " +
                               "'after' is read immediately, before any Update() has run, so it will " +
                               "usually still equal 'before'.",
                    };
                }

                return (object)new
                {
                    success = true,
                    skyGlow = skyGlowResult,
                    brightness = brightnessResult,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ======================================================================
        // STORYTELLER / INCIDENTS & QUESTS
        // ======================================================================

        [Tool(
            "jawa/incident_schedule",
            Description =
                "*** ACTS ON THE LIVE COLONY (eventually) *** Queue an incident for a FUTURE tick - " +
                "Storyteller.incidentQueue.Add(def, fireTick, parms, retryDurationTicks). Unlike " +
                "jawa/fire_incident this does not fire anything now; IncidentQueueTick() tries it once " +
                "the game clock reaches fireTick, and retries roughly every 833 ticks until " +
                "retryDurationTicks elapses. ⚠️ Requires the game to actually be TICKING - a paused " +
                "game never reaches fireTick. Parms are built the same way jawa/fire_incident builds " +
                "them: StorytellerUtility.DefaultParmsNow(incident.category, map), with points/faction " +
                "overridable.",
            ResultDescription = "success, the queued entry, queue count before/after, and ticksUntilFire.")]
        public static async Task<object> IncidentSchedule(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "IncidentDef defName, e.g. RaidEnemy, TraderCaravanArrival.")]
            string incidentDef,
            [ToolParameter(Description = "Ticks from now to fire at. Ignored if absoluteFireTick is given.")]
            int delayTicks = 2500,
            [ToolParameter(Description = "Absolute TicksGame to fire at instead of 'delayTicks'. <=0 to use delayTicks.")]
            int absoluteFireTick = 0,
            [ToolParameter(Description = "Keep retrying for this many ticks after fireTick if the incident can't fire yet. 0 = try once.")]
            int retryDurationTicks = 0,
            [ToolParameter(Description = "Threat points. Omit or <=0 for the storyteller's current default.")]
            float points = 0f,
            [ToolParameter(Description = "Optional faction defName for incidents that take one (raids).")]
            string faction = null)
        {
            if (string.IsNullOrWhiteSpace(incidentDef)) return Fail("incidentDef is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

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

                int now = TicksGameSafe();
                int fireTick = absoluteFireTick > 0 ? absoluteFireTick : now + Math.Max(0, delayTicks);

                int countBefore = Find.Storyteller.incidentQueue.Count;
                bool added;
                try { added = Find.Storyteller.incidentQueue.Add(idef, fireTick, parms, retryDurationTicks); }
                catch (Exception e) { return Fail("incidentQueue.Add threw: " + e.GetType().Name + ": " + e.Message); }
                int countAfter = Find.Storyteller.incidentQueue.Count;

                object matched = null;
                foreach (QueuedIncident qi in Find.Storyteller.incidentQueue)
                {
                    if (qi.FireTick == fireTick && qi.FiringIncident != null && qi.FiringIncident.def == idef)
                    {
                        matched = new
                        {
                            incident = qi.FiringIncident.def.defName,
                            points = qi.FiringIncident.parms.points,
                            faction = qi.FiringIncident.parms.faction != null ? qi.FiringIncident.parms.faction.def.defName : null,
                            fireTick = qi.FireTick,
                            retryDurationTicks = qi.RetryDurationTicks,
                            triedToFire = qi.TriedToFire,
                        };
                        break;
                    }
                }

                return (object)new
                {
                    success = added && matched != null,
                    queued = matched,
                    queueCountBefore = countBefore,
                    queueCountAfter = countAfter,
                    fireTick,
                    ticksUntilFire = now >= 0 ? (int?)(fireTick - now) : null,
                    note = matched == null
                        ? "Add() returned " + added + " but the entry could not be re-found by (def, fireTick) - report this."
                        : "Fires only while the game is TICKING (IncidentQueueTick runs on the map/world tick).",
                    ticksGame = now,
                };
            });
        }

        [Tool(
            "jawa/difficulty_tune",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Read and optionally WRITE fields on the live " +
                "Storyteller.difficulty (type RimWorld.Difficulty) - threatScale, allowBigThreats, " +
                "adaptationEffectFactor and a few more. This is the mutable runtime object 'Custom' " +
                "difficulty edits; it is a COPY of the DifficultyDef the game started with, not the " +
                "def itself, so writes here never touch other saves. Omit every setter argument to " +
                "just read the current values.",
            ResultDescription = "success, before, after (only the fields you set differ).")]
        public static async Task<object> DifficultyTune(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Overall threat scale. Omit to leave unchanged.")] float? threatScale = null,
            [ToolParameter(Description = "Allow raids/threats sized 'big'. Omit to leave unchanged.")] bool? allowBigThreats = null,
            [ToolParameter(Description = "How strongly the adaptation mechanic responds to pawn loss. Omit to leave unchanged.")] float? adaptationEffectFactor = null,
            [ToolParameter(Description = "Colonist mood offset from difficulty. Omit to leave unchanged.")] float? colonistMoodOffset = null,
            [ToolParameter(Description = "Trade price factor loss from difficulty. Omit to leave unchanged.")] float? tradePriceFactorLoss = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");
                var d = Find.Storyteller != null ? Find.Storyteller.difficulty : null;
                if (d == null) return Fail("Find.Storyteller.difficulty is null - is a game loaded?");

                var before = new
                {
                    threatScale = d.threatScale,
                    allowBigThreats = d.allowBigThreats,
                    adaptationEffectFactor = d.adaptationEffectFactor,
                    colonistMoodOffset = d.colonistMoodOffset,
                    tradePriceFactorLoss = d.tradePriceFactorLoss,
                };

                if (threatScale.HasValue) d.threatScale = threatScale.Value;
                if (allowBigThreats.HasValue) d.allowBigThreats = allowBigThreats.Value;
                if (adaptationEffectFactor.HasValue) d.adaptationEffectFactor = adaptationEffectFactor.Value;
                if (colonistMoodOffset.HasValue) d.colonistMoodOffset = colonistMoodOffset.Value;
                if (tradePriceFactorLoss.HasValue) d.tradePriceFactorLoss = tradePriceFactorLoss.Value;

                return (object)new
                {
                    success = true,
                    before,
                    after = new
                    {
                        threatScale = d.threatScale,
                        allowBigThreats = d.allowBigThreats,
                        adaptationEffectFactor = d.adaptationEffectFactor,
                        colonistMoodOffset = d.colonistMoodOffset,
                        tradePriceFactorLoss = d.tradePriceFactorLoss,
                    },
                    difficultyDef = Find.Storyteller.difficultyDef != null ? Find.Storyteller.difficultyDef.defName : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/signal_send",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Send a signal through Find.SignalManager.SendSignal - " +
                "the way QuestParts actually talk to each other (a delay part firing, a bill completing, " +
                "a pawn dying). Most quest inSignals are built as '<storeAs>.<EventName>'; " +
                "jawa/fire_quest and the quest's own def show what storeAs it used. This is a raw send: " +
                "it does not validate the tag against any quest, so a mistyped tag lands on nobody and " +
                "reports success anyway - that is how signals work in source, not a limitation of this tool.",
            ResultDescription = "success, tag, receiverCountAtSend (how many ISignalReceivers exist to catch it), args echoed back.")]
        public static async Task<object> SignalSend(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The signal tag, e.g. 'quest12345.DelayEnded'.")] string tag,
            [ToolParameter(Description = "Optional pawn to attach as the SUBJECT named argument.")] string subjectPawn = null,
            [ToolParameter(Description = "Optional plain text to attach as the TEXT named argument.")] string textArg = null,
            [ToolParameter(Description = "Signal.global - broadcast beyond the normal receiver set.")] bool global = false)
        {
            if (string.IsNullOrWhiteSpace(tag)) return Fail("tag is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");
                if (Find.SignalManager == null) return Fail("Find.SignalManager is null.");

                var args = new List<NamedArgument>();
                string subjLabel = null;
                if (!string.IsNullOrEmpty(subjectPawn))
                {
                    string perr; var p = FindPawn(subjectPawn, out perr);
                    if (p == null) return Fail(perr);
                    args.Add(new NamedArgument(p, "SUBJECT"));
                    subjLabel = p.LabelShortCap;
                }
                if (!string.IsNullOrEmpty(textArg)) args.Add(new NamedArgument(textArg, "TEXT"));

                int receiverCount = Find.SignalManager.receivers != null ? Find.SignalManager.receivers.Count : 0;

                try
                {
                    var signal = new Signal(tag.Trim(), new SignalArgs(args.ToArray()), global);
                    Find.SignalManager.SendSignal(signal);
                }
                catch (Exception e) { return Fail("SendSignal threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    tag = tag.Trim(),
                    global,
                    receiverCountAtSend = receiverCount,
                    subject = subjLabel,
                    text = textArg,
                    note = receiverCount == 0
                        ? "No ISignalReceiver was registered when this sent - the signal reached nobody. " +
                          "That is not this tool failing; SendSignal never reports who caught it."
                        : "Sent to " + receiverCount + " registered receiver(s). Whether any of them " +
                          "matched this exact tag is not observable from here - check the quest's own " +
                          "state (jawa/fire_quest / the save) for the effect.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ======================================================================
        // ANIMALS & TRAINING - the whole domain is new as of this file.
        // ======================================================================

        [Tool(
            "jawa/animal_train",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Pawn_TrainingTracker.Train(TrainableDef, trainer, " +
                "complete:true) - the actual call a successful training interaction makes. complete=true " +
                "(the default) completes ALL remaining steps for that TrainableDef in one call; " +
                "complete=false advances it by exactly one step, same as one real interaction. Training " +
                "Obedience with a trainer given also sets playerSettings.Master if the pawn had none - " +
                "that is source behaviour, not something this tool adds. Prerequisites are NOT checked " +
                "or auto-trained; use jawa/animal_train_wanted first if you need CanBeTrained to read true.",
            ResultDescription = "success, before/after: learned, wanted, canBeTrainedFurther, and the pawn's master.")]
        public static async Task<object> AnimalTrain(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The animal's pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "TrainableDef name, e.g. Tameness, Obedience, Release, Rescue.")] string trainable = null,
            [ToolParameter(Description = "Trainer pawn id or name. Optional - may assign Master on Obedience.")] string trainer = null,
            [ToolParameter(Description = "Complete every remaining step at once. False advances by one step only.")] bool complete = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.training == null) return Fail("Pawn '" + p.LabelShortCap + "' has no Pawn_TrainingTracker (training == null) - it is not a trainable race.");

                var td = DefDatabase<TrainableDef>.GetNamedSilentFail((trainable ?? "").Trim());
                if (td == null) return Fail("No TrainableDef '" + trainable + "'.", DefSuggestions<TrainableDef>(trainable));

                Pawn trainerPawn = null;
                if (!string.IsNullOrEmpty(trainer))
                {
                    string terr; trainerPawn = FindPawn(trainer, out terr);
                    if (trainerPawn == null) return Fail(terr);
                }

                var before = new
                {
                    learned = p.training.HasLearned(td),
                    wanted = p.training.GetWanted(td),
                    canBeTrainedFurther = p.training.CanBeTrained(td),
                    master = p.playerSettings != null && p.playerSettings.Master != null ? p.playerSettings.Master.LabelShortCap : null,
                };

                try { p.training.Train(td, trainerPawn, complete); }
                catch (Exception e) { return Fail("Train() threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    pawn = p.LabelShortCap,
                    trainable = td.defName,
                    before,
                    after = new
                    {
                        learned = p.training.HasLearned(td),
                        wanted = p.training.GetWanted(td),
                        canBeTrainedFurther = p.training.CanBeTrained(td),
                        master = p.playerSettings != null && p.playerSettings.Master != null ? p.playerSettings.Master.LabelShortCap : null,
                    },
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/animal_train_wanted",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Pawn_TrainingTracker.SetWantedRecursive(TrainableDef, " +
                "bool) - ticks or unticks a box on the Animals tab's training grid, INCLUDING every " +
                "prerequisite when turning one on, and every trainable that DEPENDS on this one when " +
                "turning it off. This only sets what the colonist AI will attempt; it does not itself " +
                "advance any step - pair it with jawa/animal_train to move steps immediately.",
            ResultDescription = "success, before/after wanted for the target def and every def SetWantedRecursive is documented to touch.")]
        public static async Task<object> AnimalTrainWanted(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The animal's pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "TrainableDef name.")] string trainable = null,
            [ToolParameter(Description = "true = wanted (and recursively want every prerequisite). false = not wanted (and recursively un-want every dependent).")]
            bool wanted = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.training == null) return Fail("Pawn '" + p.LabelShortCap + "' has no Pawn_TrainingTracker.");

                var td = DefDatabase<TrainableDef>.GetNamedSilentFail((trainable ?? "").Trim());
                if (td == null) return Fail("No TrainableDef '" + trainable + "'.", DefSuggestions<TrainableDef>(trainable));

                // The set this call is DOCUMENTED to touch, so the readback matches
                // what SetWantedRecursive actually walks rather than guessing.
                var touched = new List<TrainableDef> { td };
                if (wanted && td.prerequisites != null) touched.AddRange(td.prerequisites);
                if (!wanted)
                {
                    touched.AddRange(DefDatabase<TrainableDef>.AllDefsListForReading
                        .Where(t => t.prerequisites != null && t.prerequisites.Contains(td)));
                }

                Func<List<object>> snapshot = () => touched.Distinct()
                    .Select(t => (object)new { trainable = t.defName, wanted = p.training.GetWanted(t) })
                    .ToList();

                var before = snapshot();
                try { p.training.SetWantedRecursive(td, wanted); }
                catch (Exception e) { return Fail("SetWantedRecursive threw: " + e.GetType().Name + ": " + e.Message); }
                var after = snapshot();

                return (object)new
                {
                    success = true,
                    pawn = p.LabelShortCap,
                    trainable = td.defName,
                    wanted,
                    before,
                    after,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/instant_recruit",
            Description =
                "*** ACTS ON THE LIVE COLONY *** InteractionWorker_RecruitAttempt.DoRecruit - the FULL " +
                "success path of a recruit/tame interaction with NO chance roll: apparel unlock, royal " +
                "title replace, guest status clear, faction change, plus (unlike a raw SetFaction) the " +
                "tale recording, records increment and mood memory a real success grants, keyed off " +
                "whether the recruitee is humanlike or an animal. This differs from jawa/set_pawn_faction " +
                "recruit=true, which calls only the bare RecruitUtility.Recruit and skips all of that " +
                "bookkeeping. Give a recruiter to get its side effects (RecordDefOf.AnimalsTamed/" +
                "PrisonersRecruited, a small automatic bond chance on a tamed animal); omit it and the " +
                "pawn joins the player faction with none of that.",
            ResultDescription = "success, before/after faction, isPrisoner/isColonist, and the pawn snapshot.")]
        public static async Task<object> InstantRecruit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The pawn or animal to recruit/tame - id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "Recruiter pawn id or name. Optional - see Description for what it adds.")] string recruiter = null,
            [ToolParameter(Description = "Show the mote/message/letter a real success would. Default false for a quiet bridge write.")]
            bool audiovisual = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var recruitee = FindPawn(pawn, out err);
                if (recruitee == null) return Fail(err);

                Pawn recruiterPawn = null;
                if (!string.IsNullOrEmpty(recruiter))
                {
                    string rerr; recruiterPawn = FindPawn(recruiter, out rerr);
                    if (recruiterPawn == null) return Fail(rerr);
                }

                var before = recruitee.Faction != null ? recruitee.Faction.def.defName : null;

                try { InteractionWorker_RecruitAttempt.DoRecruit(recruiterPawn, recruitee, audiovisual); }
                catch (Exception e) { return Fail("DoRecruit threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    before,
                    after = recruitee.Faction != null ? recruitee.Faction.def.defName : null,
                    isPrisoner = recruitee.IsPrisoner,
                    isColonist = recruitee.IsColonist,
                    isAnimal = recruitee.IsAnimal,
                    master = recruitee.playerSettings != null && recruitee.playerSettings.Master != null
                        ? recruitee.playerSettings.Master.LabelShortCap : null,
                    pawn = PawnSnapshot(recruitee),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/animal_bond",
            Description =
                "*** ACTS ON THE LIVE COLONY *** RelationsUtility.TryDevelopBondRelation(humanlike, " +
                "animal, chance) - chance=1.0 (the default here) FORCES it past the Rand.Value roll, " +
                "but the roll is not the only gate: it still returns false, with the relation NOT " +
                "added, when the animal already carries a Bond, when its TrainableUtility trainability " +
                "is below Intermediate, when the human is a Psychopath or already bonded to this " +
                "animal, or when the animal is Spawned-bonded to someone else. This tool reports which " +
                "one happened rather than guessing from a bare false.",
            ResultDescription = "success (the bond call's own return), bonded (read back via DirectRelationExists), and why when it did not take.")]
        public static async Task<object> AnimalBond(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The human pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "The animal pawn id or name.")] string animal = null,
            [ToolParameter(Description = "Bond chance 0..1. 1.0 (default) forces it past the RNG roll.")] float chance = 1f)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var human = FindPawn(pawn, out err);
                if (human == null) return Fail(err);
                string aerr; var beast = FindPawn(animal, out aerr);
                if (beast == null) return Fail(aerr);

                if (human.relations == null) return Fail("Pawn '" + human.LabelShortCap + "' has no relations tracker.");
                if (beast.relations == null) return Fail("Pawn '" + beast.LabelShortCap + "' has no relations tracker.");

                bool alreadyBonded = human.relations.DirectRelationExists(PawnRelationDefOf.Bond, beast);
                bool animalAlreadyBondedToSomeone =
                    beast.relations.GetFirstDirectRelationPawn(PawnRelationDefOf.Bond, x => x.Spawned) != null;

                bool result;
                try { result = RelationsUtility.TryDevelopBondRelation(human, beast, chance); }
                catch (Exception e) { return Fail("TryDevelopBondRelation threw: " + e.GetType().Name + ": " + e.Message); }

                bool bondedNow = human.relations.DirectRelationExists(PawnRelationDefOf.Bond, beast);

                string why = null;
                if (!result)
                {
                    if (!beast.IsAnimal) why = "recipient is not an animal (IsAnimal false).";
                    else if (alreadyBonded) why = "this exact pair already carries a Bond relation.";
                    else if (animalAlreadyBondedToSomeone) why = "the animal already carries a Bond to a different spawned pawn.";
                    else why = "trainability below Intermediate, a Psychopath/inhumanized initiator, HistoryEvent refusal, or the RNG (unlikely at chance=1).";
                }

                return (object)new
                {
                    success = result,
                    bonded = bondedNow,
                    human = human.LabelShortCap,
                    animal = beast.LabelShortCap,
                    chance,
                    why,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif
    }
}
