// JawaBenchEventTools.cs - weather, game conditions, raids and the storyteller.
//
// Owner, 2026-08-19: "Causing weather events, raids."
//
// 🔴 EVERYTHING THAT ACTS ON THE PLAYER IS BEHIND #if JAWA_GM_TOOLS, the same
// gate jawa/fire_incident and jawa/send_letter already use. Build with
// `--gm` or these are absent from the DLL entirely. Pure reads are ungated.
//
// FACTS THAT SHAPE THIS FILE, read from 1.6 source:
//  * WeatherManager.TransitionTo does NOT hold - WeatherDecider rolls a new
//    weather once curWeatherAge > curWeatherDuration. The only durable lock is
//    a GameCondition_ForceWeather, which WeatherDecider.ForcedWeather honours.
//  * GameCondition has no EndNow(). The safe early end is
//    `cond.Duration = cond.TicksPassed` - the setter clears `permanent`.
//  * IncidentWorker_RaidEnemy auto-resolves faction / strategy / arrival ONLY
//    when they are null, so every field is overridable.
//  * GameConditionDefOf-adjacent `Planetkiller` ENDS THE GAME. Hard-blocked.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        /// <summary>Ending the game is never a bridge operation.</summary>
        private static readonly HashSet<string> ForbiddenConditions =
            new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "Planetkiller" };

        [Tool(
            "jawa/weather_get",
            Description =
                "Read the weather and every active game condition, plus what the storyteller " +
                "currently believes the colony is worth. Read-only and safe on a live game. " +
                "⭐ `threatPoints` and the wealth breakdown are not exposed anywhere else - " +
                "they are what the storyteller actually uses to size the next raid.",
            ResultDescription = "success, weather, conditions[], threatPoints, wealth, storyteller.")]
        public static async Task<object> WeatherGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Also list every WeatherDef and GameConditionDef.")] bool listDefs = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var wm = map.weatherManager;

                var active = new List<object>();
                try
                {
                    foreach (var c in map.gameConditionManager.ActiveConditions)
                        active.Add(new
                        {
                            def = c.def.defName, label = c.LabelCap,
                            permanent = c.Permanent,
                            ticksPassed = c.TicksPassed,
                            ticksLeft = c.Permanent ? -1 : c.TicksLeft,
                        });
                }
                catch (Exception e) { Log.Warning("[JawaBench] weather_get conditions: " + e.Message); }

                float threat = -1f;
                try { threat = StorytellerUtility.DefaultThreatPointsNow(map); } catch { }

                object wealth = null;
                try
                {
                    var w = map.wealthWatcher;
                    wealth = new { total = w.WealthTotal, items = w.WealthItems, buildings = w.WealthBuildings, pawns = w.WealthPawns };
                }
                catch { }

                object teller = null;
                try
                {
                    teller = new
                    {
                        def = Find.Storyteller.def != null ? Find.Storyteller.def.defName : null,
                        difficulty = Find.Storyteller.difficultyDef != null ? Find.Storyteller.difficultyDef.defName : null,
                        threatScale = Find.Storyteller.difficulty != null ? (object)Find.Storyteller.difficulty.threatScale : null,
                        allowBigThreats = Find.Storyteller.difficulty != null ? (object)Find.Storyteller.difficulty.allowBigThreats : null,
                    };
                }
                catch { }

                return (object)new
                {
                    success = true,
                    weather = new
                    {
                        current = wm.curWeather != null ? wm.curWeather.defName : null,
                        last = wm.lastWeather != null ? wm.lastWeather.defName : null,
                        curWeatherAge = wm.curWeatherAge,
                        rainRate = wm.RainRate, snowRate = wm.SnowRate,
                    },
                    activeConditionCount = active.Count,
                    conditions = active,
                    threatPoints = threat,
                    wealth,
                    storyteller = teller,
                    weatherDefs = listDefs ? DefDatabase<WeatherDef>.AllDefsListForReading.Select(d => d.defName).ToList() : null,
                    conditionDefs = listDefs ? DefDatabase<GameConditionDef>.AllDefsListForReading.Select(d => d.defName).ToList() : null,
                    note = "TransitionTo does not HOLD - WeatherDecider rerolls when the duration expires. Use jawa/weather_set lock=true.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/raid_preview",
            Description =
                "Resolve what a raid WOULD be without firing it: the storyteller's default " +
                "parameters, the hostile factions available, and every RaidStrategyDef and " +
                "PawnsArrivalModeDef that `CanUseWith` accepts for those parms. Read-only. " +
                "Use before jawa/fire_raid so the parameters are chosen, not guessed.",
            ResultDescription = "success, defaultParms, hostileFactions[], strategies[], arrivalModes[].")]
        public static async Task<object> RaidPreview(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Points to test against. -1 uses the storyteller's current default.")] float points = -1f)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                IncidentParms parms;
                try { parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map); }
                catch (Exception e) { return Fail("DefaultParmsNow threw: " + e.Message); }
                if (points >= 0f) parms.points = points;

                // 🔴 CanUseWith is meaningless while parms.faction is NULL - every
                // strategy worker consults the faction, so all 11 report unusable and it
                // reads as "raids are impossible". Resolve an attacker FIRST.
                var resolvedNote = new List<string>();
                if (parms.faction == null)
                {
                    parms.faction = Find.FactionManager.AllFactionsVisible
                        .Where(f => f != Faction.OfPlayer && f.HostileTo(Faction.OfPlayer)
                                    && !f.def.pawnGroupMakers.NullOrEmpty() && f.def.canStageAttacks)
                        .RandomElementWithFallback(null);
                    resolvedNote.Add(parms.faction != null
                        ? "faction was null; resolved to " + parms.faction.def.defName + " so CanUseWith is meaningful"
                        : "NO hostile faction in this world can stage attacks - that is why nothing is usable");
                }

                var hostiles = Find.FactionManager.AllFactionsVisible
                    .Where(f => f != Faction.OfPlayer && f.HostileTo(Faction.OfPlayer))
                    .Select(f => new { def = f.def.defName, name = f.Name, canStageAttacks = f.def.canStageAttacks })
                    .ToList();

                var strategies = new List<object>();
                foreach (var sd in DefDatabase<RaidStrategyDef>.AllDefsListForReading)
                {
                    bool ok = false; string why = null;
                    try { ok = sd.Worker.CanUseWith(parms, PawnGroupKindDefOf.Combat); }
                    catch (Exception e) { why = e.GetType().Name; }
                    strategies.Add(new { def = sd.defName, usable = ok, error = why });
                }

                var arrivals = DefDatabase<PawnsArrivalModeDef>.AllDefsListForReading
                    .Select(a => new { def = a.defName, minTechLevel = a.minTechLevel.ToString() }).ToList();

                return (object)new
                {
                    success = true,
                    defaultParms = new
                    {
                        points = parms.points,
                        faction = parms.faction != null ? parms.faction.def.defName : null,
                        raidStrategy = parms.raidStrategy != null ? parms.raidStrategy.defName : null,
                        raidArrivalMode = parms.raidArrivalMode != null ? parms.raidArrivalMode.defName : null,
                    },
                    currentThreatPoints = StorytellerUtility.DefaultThreatPointsNow(map),
                    hostileFactions = hostiles,
                    usableStrategies = strategies.Where(o => (bool)o.GetType().GetProperty("usable").GetValue(o, null)).ToList(),
                    allStrategies = strategies,
                    arrivalModes = arrivals,
                    resolvedNotes = resolvedNote,
                    note = "IncidentWorker_RaidEnemy auto-resolves faction/strategy/arrival ONLY when null, so every field is overridable. " +
                           "CanUseWith needs a non-null faction or every strategy reports unusable.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/weather_set",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Change the weather. " +
                "🔴 A plain transition does NOT hold - WeatherDecider rerolls once " +
                "curWeatherAge passes curWeatherDuration. Pass lock=true to register a " +
                "permanent GameCondition_ForceWeather instead, which is the ONLY durable " +
                "weather control in the game. unlock=true removes that condition again.",
            ResultDescription = "success, before/after weather, and whether a lock is in force.")]
        public static async Task<object> WeatherSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "WeatherDef name.")] string weather = null,
            [ToolParameter(Description = "Register a permanent forcing condition instead of a transition.")] bool lockWeather = false,
            [ToolParameter(Description = "Remove any existing weather lock.")] bool unlock = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var wm = map.weatherManager;
                var before = wm.curWeather != null ? wm.curWeather.defName : null;
                var notes = new List<string>();

                var controller = DefDatabase<GameConditionDef>.GetNamedSilentFail("WeatherController");

                if (unlock)
                {
                    if (controller != null)
                    {
                        var existing = map.gameConditionManager.GetActiveCondition(controller);
                        if (existing != null) { existing.Duration = existing.TicksPassed; notes.Add("weather lock ended (Duration = TicksPassed; there is no EndNow())"); }
                        else notes.Add("no weather lock was active");
                    }
                }

                if (!string.IsNullOrEmpty(weather))
                {
                    var wd = DefDatabase<WeatherDef>.GetNamedSilentFail(weather.Trim());
                    if (wd == null) return Fail("No WeatherDef '" + weather + "'.", DefSuggestions<WeatherDef>(weather));

                    if (lockWeather)
                    {
                        if (controller == null) return Fail("GameConditionDef 'WeatherController' not found, so weather cannot be locked.");
                        var old = map.gameConditionManager.GetActiveCondition(controller);
                        if (old != null) old.Duration = old.TicksPassed;
                        var cond = GameConditionMaker.MakeConditionPermanent(controller);
                        var fw = cond as GameCondition_ForceWeather;
                        if (fw == null) return Fail("WeatherController did not make a GameCondition_ForceWeather.");
                        fw.weather = wd;
                        map.gameConditionManager.RegisterCondition(cond);
                        notes.Add("registered a PERMANENT GameCondition_ForceWeather - this is the only durable weather control");
                    }
                    wm.TransitionTo(wd);
                    if (!lockWeather) notes.Add("plain transition - WeatherDecider WILL reroll when the duration expires");
                }
                else if (!unlock) return Fail("Give a weather, or unlock=true.");

                bool locked = controller != null && map.gameConditionManager.GetActiveCondition(controller) != null;
                bool paused2 = Find.TickManager != null && Find.TickManager.Paused;
                return (object)new
                {
                    success = true, before,
                    after = wm.curWeather != null ? wm.curWeather.defName : null,
                    lockInForce = locked,
                    lockCaveat = (unlock && locked)
                        ? "lockInForce still reads true because the condition expires on the NEXT TICK" + (paused2 ? " and the game is PAUSED." : ".")
                        : null,
                    gamePaused = paused2,
                    notes, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/game_condition",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Start or end a GameCondition - eclipse, " +
                "solar flare, toxic fallout, heat wave, cold snap, aurora, psychic drone and " +
                "the rest. action='start' | 'end'. " +
                "⚠️ There is no EndNow(); ending sets Duration = TicksPassed so it expires " +
                "next tick. " +
                "⛔ `Planetkiller` is HARD-BLOCKED - it ends the game and that is never a " +
                "bridge operation.",
            ResultDescription = "success, active conditions after.")]
        public static async Task<object> GameConditionTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'start' | 'end'.")] string action = "start",
            [ToolParameter(Description = "GameConditionDef name.")] string condition = null,
            [ToolParameter(Description = "Duration in ticks. 0 uses the def default.")] int durationTicks = 0,
            [ToolParameter(Description = "Make it permanent.")] bool permanent = false,
            [ToolParameter(Description = "Apply world-wide instead of to this map.")] bool worldWide = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(condition)) return Fail("Give a GameConditionDef.");
                var name = condition.Trim();

                if (ForbiddenConditions.Contains(name))
                    return Fail("'" + name + "' is HARD-BLOCKED by this tool: it ends the game. That is not a bridge operation.");

                var cd = DefDatabase<GameConditionDef>.GetNamedSilentFail(name);
                if (cd == null) return Fail("No GameConditionDef '" + name + "'.", DefSuggestions<GameConditionDef>(name));

                var mgr = worldWide ? Find.World.gameConditionManager : map.gameConditionManager;
                string A = (action ?? "start").Trim().ToLowerInvariant();
                var notes = new List<string>();

                if (A == "start")
                {
                    var existing = mgr.GetActiveCondition(cd);
                    if (existing != null) { existing.Duration = existing.TicksPassed; notes.Add("replaced an already-active instance"); }
                    GameCondition c = permanent
                        ? GameConditionMaker.MakeConditionPermanent(cd)
                        : GameConditionMaker.MakeCondition(cd, durationTicks > 0 ? durationTicks : 0);
                    mgr.RegisterCondition(c);
                    notes.Add("registered " + cd.defName + (permanent ? " PERMANENT" : (durationTicks > 0 ? " for " + durationTicks + " ticks" : " for its default duration")));
                }
                else if (A == "end")
                {
                    var c = mgr.GetActiveCondition(cd);
                    if (c == null) return Fail("'" + cd.defName + "' is not active" + (worldWide ? " world-wide" : " on this map") + ".");
                    c.Duration = c.TicksPassed;
                    notes.Add("Duration = TicksPassed - it expires next tick. GameCondition has no EndNow().");
                }
                else return Fail("action must be start|end.");

                var active = mgr.ActiveConditions.Select(c => new
                {
                    def = c.def.defName, permanent = c.Permanent, ticksLeft = c.Permanent ? -1 : c.TicksLeft
                }).ToList();

                // ⚠️ Ending sets Duration = TicksPassed, so the condition expires on the
                // NEXT TICK. With the game PAUSED it stays in ActiveConditions and looks
                // like the end failed. Say so rather than letting the list mislead.
                bool paused = Find.TickManager != null && Find.TickManager.Paused;
                return (object)new
                {
                    success = true, action = A, scope = worldWide ? "world" : "map", notes,
                    endsNextTick = A == "end",
                    gamePaused = paused,
                    listCaveat = A == "end"
                        ? "Still listed below because Duration=TicksPassed expires on the NEXT TICK" + (paused ? " and the game is PAUSED." : ".")
                        : null,
                    activeConditions = active, ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/fire_raid",
            Description =
                "*** ACTS ON THE LIVE COLONY - THIS SENDS A REAL RAID *** " +
                "Fire a raid with FULL parameter control. IncidentWorker_RaidEnemy only " +
                "auto-resolves faction, strategy and arrival mode when they are null, so " +
                "anything set here wins over the storyteller. " +
                "Use jawa/raid_preview first to see which strategies CanUseWith your parms. " +
                "⚠️ points is required and must be > 0 or the worker logs an error.",
            ResultDescription = "success, the resolved parms, and whether TryExecute accepted.")]
        public static async Task<object> FireRaid(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Threat points. -1 uses the storyteller's current default.")] float points = -1f,
            [ToolParameter(Description = "FactionDef of the attacker. Empty lets the worker choose.")] string faction = null,
            [ToolParameter(Description = "RaidStrategyDef. Empty lets the worker choose.")] string strategy = null,
            [ToolParameter(Description = "PawnsArrivalModeDef. Empty lets the worker choose.")] string arrivalMode = null,
            [ToolParameter(Description = "Spawn centre 'x,z'. Empty lets the worker choose.")] string spawnCenter = null,
            [ToolParameter(Description = "Friendly raid instead of hostile.")] bool friendly = false,
            [ToolParameter(Description = "Resolve and REPORT without firing. Default true - you must opt in to the raid.")] bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                IncidentParms parms;
                try { parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map); }
                catch (Exception e) { return Fail("DefaultParmsNow threw: " + e.Message); }

                if (points >= 0f) parms.points = points;
                if (parms.points <= 0f) return Fail("points must be > 0 - IncidentWorker_RaidEnemy logs an error otherwise.");

                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    var f = Find.FactionManager.FirstFactionOfDef(fd);
                    if (f == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                    parms.faction = f;
                }
                if (!string.IsNullOrEmpty(strategy))
                {
                    var sd = DefDatabase<RaidStrategyDef>.GetNamedSilentFail(strategy.Trim());
                    if (sd == null) return Fail("No RaidStrategyDef '" + strategy + "'.", DefSuggestions<RaidStrategyDef>(strategy));
                    parms.raidStrategy = sd;
                }
                if (!string.IsNullOrEmpty(arrivalMode))
                {
                    var ad = DefDatabase<PawnsArrivalModeDef>.GetNamedSilentFail(arrivalMode.Trim());
                    if (ad == null) return Fail("No PawnsArrivalModeDef '" + arrivalMode + "'.", DefSuggestions<PawnsArrivalModeDef>(arrivalMode));
                    parms.raidArrivalMode = ad;
                }
                if (!string.IsNullOrEmpty(spawnCenter))
                {
                    var b = spawnCenter.Split(','); int x, z;
                    if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                        return Fail("spawnCenter must be 'x,z'.");
                    parms.spawnCenter = new IntVec3(x, 0, z);
                }

                // Same trap as raid_preview: CanFireNow and the strategy workers need a
                // faction. Resolve one rather than reporting a misleading refusal.
                var factionNotes = new List<string>();
                if (parms.faction == null && !friendly)
                {
                    parms.faction = Find.FactionManager.AllFactionsVisible
                        .Where(f => f != Faction.OfPlayer && f.HostileTo(Faction.OfPlayer)
                                    && !f.def.pawnGroupMakers.NullOrEmpty() && f.def.canStageAttacks)
                        .RandomElementWithFallback(null);
                    if (parms.faction != null) factionNotes.Add("faction was null; resolved to " + parms.faction.def.defName);
                    else factionNotes.Add("no hostile faction in this world can stage attacks");
                }

                var incident = friendly ? IncidentDefOf.RaidFriendly : IncidentDefOf.RaidEnemy;
                var resolved = new
                {
                    incident = incident.defName,
                    points = parms.points,
                    faction = parms.faction != null ? parms.faction.def.defName : "(worker chooses)",
                    raidStrategy = parms.raidStrategy != null ? parms.raidStrategy.defName : "(worker chooses)",
                    raidArrivalMode = parms.raidArrivalMode != null ? parms.raidArrivalMode.defName : "(worker chooses)",
                    spawnCenter = parms.spawnCenter.IsValid ? (object)new { x = parms.spawnCenter.x, z = parms.spawnCenter.z } : null,
                };

                if (dryRun)
                    return (object)new
                    {
                        success = true, dryRun = true, resolved,
                        canFireNow = incident.Worker.CanFireNow(parms),
                        factionNotes,
                        note = "DRY RUN - nothing was sent. Pass dryRun=false to actually raid the colony.",
                        ticksGame = TicksGameSafe(),
                    };

                bool executed;
                try { executed = incident.Worker.TryExecute(parms); }
                catch (Exception e) { return Fail("TryExecute threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = executed, dryRun = false, resolved, executed, factionNotes,
                    note = executed ? "Raid fired." : "TryExecute returned false - the worker refused these parms.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif // JAWA_GM_TOOLS
    }
}
