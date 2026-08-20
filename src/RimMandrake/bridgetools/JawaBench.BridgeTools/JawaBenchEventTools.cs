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
using UnityEngine;
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

        // ================================================================
        //  EXPLOSIONS, FIRE AND DIRECT DAMAGE
        //  GenExplosion.DoExplosion has 38 parameters; only 5 are required.
        //  ⚠️ radius >= GenRadial.MaxRadialPatternRadius (~80) makes
        //     NumCellsInRadius log an error and return 20,000 cells. Clamped.
        //  🔴 PsychicShock is a HediffDef and Bioferrite a ThingDef - NEITHER
        //     is a DamageDef. The whitelist below is read from the def database
        //     at call time rather than remembered.
        // ================================================================

        private static readonly HashSet<string> ExplosiveDamageDefs =
            new HashSet<string>(StringComparer.OrdinalIgnoreCase)
            {
                "Bomb","BombSuper","MiningBomb","Thump","Flame","Burn","AcidBurn","ElectricalBurn",
                "Vaporize","NociosphereVaporize","EMP","Stun","MechBandShockwave","Smoke","ToxGas",
                "DeadlifeDust","Extinguish"
            };

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/map_explosion",
            Description =
                "*** ACTS ON THE LIVE MAP *** Detonate an explosion of any type at a cell. " +
                "damType is a DamageDef: Bomb · BombSuper · Thump · Flame · Burn · AcidBurn · " +
                "Vaporize · EMP · Stun · Smoke · ToxGas · DeadlifeDust · Extinguish and more. " +
                "damage<0 uses the def's own defaultDamage. Optional gas cloud, fire chance, " +
                "falloff, neighbour spill and per-cell spawns (filth, chunks, firefoam). " +
                "⚠️ radius is CLAMPED to 50 - at ~80 RimWorld's own radial pattern errors and " +
                "returns 20,000 cells. " +
                "🔴 PsychicShock and Bioferrite are NOT DamageDefs and are refused with an " +
                "explanation; list them with listTypes=true.",
            ResultDescription = "success, the resolved parameters, and the explosive DamageDefs available.")]
        public static async Task<object> MapExplosion(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Centre 'x,z'.")] string center = null,
            [ToolParameter(Description = "DamageDef name. Default Bomb.")] string damType = "Bomb",
            [ToolParameter(Description = "Radius in cells. Clamped to 50.")] float radius = 3.9f,
            [ToolParameter(Description = "Damage amount. -1 uses the def default.")] int damage = -1,
            [ToolParameter(Description = "0-1 chance to start a fire per cell.")] float chanceToStartFire = 0f,
            [ToolParameter(Description = "Linear damage falloff to the edge.")] bool damageFalloff = false,
            [ToolParameter(Description = "Also damage the ring of cells just outside.")] bool spillToNeighbors = false,
            [ToolParameter(Description = "GasType to leave behind: BlindSmoke|ToxGas|RotStink|DeadlifeDust.")] string gas = null,
            [ToolParameter(Description = "ThingDef to scatter after the blast, e.g. Filth_Ash.")] string spawnThing = null,
            [ToolParameter(Description = "0-1 chance per cell for spawnThing.")] float spawnChance = 0f,
            [ToolParameter(Description = "Screen shake multiplier. Clamped 0-1.")] float screenShake = 1f,
            [ToolParameter(Description = "Just list the valid damage types and do nothing.")] bool listTypes = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                var available = DefDatabase<DamageDef>.AllDefsListForReading
                    .Where(d => ExplosiveDamageDefs.Contains(d.defName))
                    .Select(d => new { def = d.defName, defaultDamage = d.defaultDamage, isExplosive = d.isExplosive })
                    .ToList();

                if (listTypes)
                    return (object)new { success = true, listing = true, explosiveDamageDefs = available, gasTypes = Enum.GetNames(typeof(GasType)), ticksGame = TicksGameSafe() };

                int x, z; var b = (center ?? "").Split(',');
                if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                    return Fail("Give centre as 'x,z'.");
                var c0 = new IntVec3(x, 0, z);
                if (!c0.InBounds(map)) return Fail("Centre " + center + " is out of bounds.");

                var dd = DefDatabase<DamageDef>.GetNamedSilentFail((damType ?? "Bomb").Trim());
                if (dd == null)
                {
                    var hint = DefDatabase<HediffDef>.GetNamedSilentFail((damType ?? "").Trim()) != null
                        ? " ('" + damType + "' is a HediffDef, not a DamageDef - use jawa/pawn_health to apply it.)"
                        : "";
                    return Fail("No DamageDef '" + damType + "'." + hint, available);
                }
                if (!ExplosiveDamageDefs.Contains(dd.defName))
                    return Fail("'" + dd.defName + "' is a DamageDef but not one that produces a sensible explosion. " +
                                "Use one of the listed types, or listTypes=true to see them.", available);

                float r = Mathf.Clamp(radius, 0.1f, 50f);
                if (r != radius) err = "radius clamped from " + radius + " to " + r;

                GasType? gt = null;
                if (!string.IsNullOrEmpty(gas))
                {
                    try { gt = (GasType)Enum.Parse(typeof(GasType), gas.Trim(), true); }
                    catch { return Fail("Bad gas '" + gas + "'. Valid: " + string.Join(", ", Enum.GetNames(typeof(GasType)))); }
                }

                ThingDef spawn = null;
                if (!string.IsNullOrEmpty(spawnThing))
                {
                    spawn = DefDatabase<ThingDef>.GetNamedSilentFail(spawnThing.Trim());
                    if (spawn == null) return Fail("No ThingDef '" + spawnThing + "'.", DefSuggestions<ThingDef>(spawnThing));
                }

                try
                {
                    GenExplosion.DoExplosion(
                        c0, map, r, dd, null,
                        damAmount: damage,
                        postExplosionSpawnThingDef: spawn,
                        postExplosionSpawnChance: Mathf.Clamp01(spawnChance),
                        postExplosionGasType: gt,
                        applyDamageToExplosionCellsNeighbors: spillToNeighbors,
                        chanceToStartFire: Mathf.Clamp01(chanceToStartFire),
                        damageFalloff: damageFalloff,
                        screenShakeFactor: Mathf.Clamp01(screenShake));
                }
                catch (Exception e) { return Fail("DoExplosion threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    center = new { x, z }, damType = dd.defName, radius = r,
                    damage = damage < 0 ? (object)("def default (" + dd.defaultDamage + ")") : damage,
                    gas = gt.HasValue ? gt.Value.ToString() : null,
                    clampNote = err,
                    explosiveDamageDefs = available,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/map_fire",
            Description =
                "*** ACTS ON THE LIVE MAP *** Start or extinguish fire. " +
                "action='start' seeds fires over a rect (each cell is gated by RimWorld's own " +
                "ChanceToStartFireIn, so wet or non-flammable cells legitimately refuse and " +
                "the result reports how many took); 'extinguish' destroys every Fire in the " +
                "rect. " +
                "⚠️ Fire SPREAD cannot be forced - Fire.TrySpread is protected. A fireSize " +
                "above 1.0 makes spread far likelier, which is the only lever.",
            ResultDescription = "success, cellsTried, firesStarted, firesExtinguished.")]
        public static async Task<object> MapFire(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'start' or 'extinguish'.")] string action = "start",
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Fire size 0.1-1.75. Above 1.0 spreads readily.")] float fireSize = 0.5f)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);
                bool start = string.Equals(action, "start", StringComparison.OrdinalIgnoreCase);
                bool ext = string.Equals(action, "extinguish", StringComparison.OrdinalIgnoreCase);
                if (!start && !ext) return Fail("action must be start|extinguish.");

                int tried = 0, started = 0, doused = 0;
                foreach (var c in r)
                {
                    tried++;
                    try
                    {
                        if (start)
                        {
                            if (FireUtility.TryStartFireIn(c, map, Mathf.Clamp(fireSize, 0.1f, 1.75f), null)) started++;
                        }
                        else
                        {
                            foreach (var t in map.thingGrid.ThingsListAtFast(c).ToList())
                            {
                                var f = t as Fire;
                                if (f != null) { f.Destroy(); doused++; }
                            }
                        }
                    }
                    catch (Exception e) { return Fail("Fire op failed at " + c + ": " + e.Message); }
                }

                return (object)new
                {
                    success = true, action, cellsTried = tried,
                    firesStarted = started, firesExtinguished = doused,
                    note = start && started < tried
                        ? (tried - started) + " cells refused - RimWorld's ChanceToStartFireIn gates on flammability and wetness. Not a failure."
                        : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/map_skyfaller",
            Description =
                "*** ACTS ON THE LIVE MAP *** Drop a skyfaller - meteorite, drop pod, shuttle - " +
                "at a cell. Default is a mineral meteorite with generated contents. " +
                "⚠️ A skyfaller def given the wrong kind of inner thing destroys it with a " +
                "Log.Error, so innerThing is validated against the def first.",
            ResultDescription = "success, what was dropped and where.")]
        public static async Task<object> MapSkyfaller(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell 'x,z'.")] string cell = null,
            [ToolParameter(Description = "Skyfaller ThingDef. Default MeteoriteIncoming.")] string skyfaller = "MeteoriteIncoming",
            [ToolParameter(Description = "Optional ThingDef to carry inside.")] string innerThing = null,
            [ToolParameter(Description = "Stack count of innerThing.")] int count = 1)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                int x, z; var b = (cell ?? "").Split(',');
                if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                    return Fail("Give cell as 'x,z'.");
                var c0 = new IntVec3(x, 0, z);
                if (!c0.InBounds(map)) return Fail("Cell out of bounds.");

                var sd = DefDatabase<ThingDef>.GetNamedSilentFail((skyfaller ?? "").Trim());
                if (sd == null) return Fail("No skyfaller ThingDef '" + skyfaller + "'.", DefSuggestions<ThingDef>(skyfaller));
                if (sd.skyfaller == null)
                    return Fail("'" + sd.defName + "' is not a skyfaller (its def has no <skyfaller> block).");

                try
                {
                    if (!string.IsNullOrEmpty(innerThing))
                    {
                        var it = DefDatabase<ThingDef>.GetNamedSilentFail(innerThing.Trim());
                        if (it == null) return Fail("No ThingDef '" + innerThing + "'.", DefSuggestions<ThingDef>(innerThing));
                        var t = ThingMaker.MakeThing(it, it.MadeFromStuff ? GenStuff.DefaultStuffFor(it) : null);
                        t.stackCount = Math.Max(1, count);
                        SkyfallerMaker.SpawnSkyfaller(sd, t, c0, map);
                    }
                    else SkyfallerMaker.SpawnSkyfaller(sd, c0, map);
                }
                catch (Exception e) { return Fail("SpawnSkyfaller threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true, skyfaller = sd.defName,
                    at = new { x, z }, innerThing, count,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif // JAWA_GM_TOOLS

    }
}