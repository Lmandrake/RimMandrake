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
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        /// <summary>Ending the game is never a bridge operation.</summary>
        private static readonly HashSet<string> ForbiddenConditions =
            new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "Planetkiller" };

        // ================================================================
        //  WINDOW-STACK DIFF ACROSS A FIRING  (FIRE_RAID_REPORTS_MODAL_1)
        //  🔴 WHY THIS EXISTS: a Harmony prefix can set __result = true, skip the
        //  incident entirely and push a modal instead. Leo.RaidProtectionFee does
        //  exactly that on IncidentWorker_RaidEnemy.TryExecuteWorker - it opens a
        //  "pay silver or be raided" Dialog_NodeTree, assigns __result = true and
        //  returns false, so every caller sees executed:true with zero pawns and
        //  cannot tell a CANCELLED raid from a raid that generated nothing.
        //  That ambiguity cost this project three retracted evidence tables
        //  (SIX_FACTIONS_NEVER_RAID_1). Nothing on the bridge can answer a modal,
        //  so the only honest thing a firing tool can do is SAY one appeared.
        //  Window.ID is unique per window instance, so identity by ID is exact -
        //  no type-name heuristics, and a window that was already open is not
        //  reported as new.
        // ================================================================

        /// <summary>IDs of every window currently on the stack. Empty (never null) when there is no stack.</summary>
        private static HashSet<int> SnapshotWindowIds()
        {
            var ids = new HashSet<int>();
            try
            {
                var stack = Find.WindowStack;
                if (stack == null) return ids;
                var ws = stack.Windows;
                for (int i = 0; i < ws.Count; i++) ids.Add(ws[i].ID);
            }
            catch (Exception) { /* no UI root yet - report nothing rather than throwing inside a firing */ }
            return ids;
        }

        /// <summary>
        /// Windows on the stack now whose ID was not in <paramref name="beforeIds"/>.
        /// Each row is { type, optionalTitle, forcePause, isDebug, id }.
        /// </summary>
        private static List<object> WindowsOpenedSince(HashSet<int> beforeIds)
        {
            var rows = new List<object>();
            try
            {
                var stack = Find.WindowStack;
                if (stack == null) return rows;
                var ws = stack.Windows;
                for (int i = 0; i < ws.Count; i++)
                {
                    var w = ws[i];
                    if (beforeIds.Contains(w.ID)) continue;
                    rows.Add(new
                    {
                        type = w.GetType().FullName,
                        optionalTitle = w.optionalTitle,
                        forcePause = w.forcePause,
                        isDebug = w.IsDebug,
                        id = w.ID
                    });
                }
            }
            catch (Exception) { }
            return rows;
        }

        /// <summary>
        /// The one sentence a caller needs when a modal ate the incident, or null when none did.
        /// <paramref name="suspicious"/> is the caller's own second reading that the incident did
        /// not really happen - zero pawns arrived, or a bare "it succeeded" with nothing to show.
        /// </summary>
        private static string DialogSwallowNote(List<object> windowsOpened, bool suspicious)
        {
            if (windowsOpened == null || windowsOpened.Count == 0 || !suspicious) return null;
            var types = string.Join(", ", windowsOpened
                .Select(o => o.GetType().GetProperty("type").GetValue(o, null) as string)
                .Where(s => !string.IsNullOrEmpty(s)).ToArray());
            return "🔴 A DIALOG SWALLOWED THIS FIRING. " + windowsOpened.Count + " window(s) opened during the call ("
                 + types + ") and the incident produced nothing. A Harmony prefix - Leo.RaidProtectionFee is the known one - "
                 + "can replace the incident with a modal and still set __result = true, so 'executed' is NOT "
                 + "evidence the incident happened. Nothing on the bridge clicks a button, so the modal will "
                 + "never be answered and it will block later calls. Clear it with "
                 + "jawa/window_list_close {action:'close', typeName:'<the type above>', closeAll:true}, "
                 + "then either disable the intercepting mod or fire at a faction it exempts.";
        }

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
                "⚠️ points is required and must be > 0 or the worker logs an error. " +
                "🔴 READ blockedByDialog BEFORE executed. A Harmony prefix can replace the raid " +
                "with a modal and still set __result = true - Leo.RaidProtectionFee's " +
                "'pay silver or be raided' dialog does exactly that. This tool diffs " +
                "Find.WindowStack across the firing, so a raid eaten by a dialog reports " +
                "blockedByDialog:true and success:false instead of a bare executed:true. " +
                "Clear the modal with jawa/window_list_close; the bridge cannot answer it.",
            ResultDescription =
                "success (executed AND not blocked), executed (raw TryExecute), " +
                "windowsOpened[] (type, optionalTitle, forcePause, isDebug, id - any window " +
                "added during the firing), blockedByDialog, actual{faction,substituted}, " +
                "arrived[], pawnsArrivedTotal, resolved parms.")]
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

                Faction requestedFaction = null;
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
                    requestedFaction = f;
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
                // 🔴 THE REASON A NAMED FACTION GETS SWAPPED, said BEFORE the raid rather
                // than discovered afterwards. IncidentWorker_RaidEnemy will not raid with a
                // faction that is not hostile to the player: TryResolveRaidFaction picks a
                // different one and the raid arrives under that flag.
                // FIRE_RAID_ECHOES_REQUESTED_FACTION_1: asking for Jawa_FreeDroidEnclaves
                // (neutral on this world) returned resolved.faction Jawa_FreeDroidEnclaves
                // and five Blackstar Company pirates walked in.
                if (requestedFaction != null && !friendly && !requestedFaction.HostileTo(Faction.OfPlayer))
                    factionNotes.Add("⚠ " + requestedFaction.def.defName + " is NOT hostile to the player ("
                                     + requestedFaction.PlayerRelationKind + "). IncidentWorker_RaidEnemy "
                                     + "will substitute a hostile faction; read actual.faction, not resolved.faction.");
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
                // ⚠ `resolved` is THE REQUEST, after this tool's own parsing. It is not the
                // outcome, and reading it as one is what this tool used to invite.
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
                        note = "DRY RUN - nothing was sent. Pass dryRun=false to actually raid the colony. "
                               + "⚠ A dry run CANNOT tell you which faction will actually raid: the "
                               + "substitution happens inside TryExecute. Only a real run reports actual.",
                        ticksGame = TicksGameSafe(),
                    };

                // Count the map's pawns per faction BEFORE, so what arrives can be
                // measured rather than echoed. IncidentParms is a reference type and the
                // worker writes its substituted faction back into parms.faction, so that
                // field is the second, independent reading.
                var before = new Dictionary<Faction, int>();
                foreach (var p in map.mapPawns.AllPawnsSpawned)
                    if (p.Faction != null)
                        before[p.Faction] = (before.TryGetValue(p.Faction, out var bn) ? bn : 0) + 1;

                // FIRE_RAID_REPORTS_MODAL_1 - snapshot the window stack across TryExecute so
                // a raid replaced by a modal is reported as such, not as executed:true.
                var windowIdsBefore = SnapshotWindowIds();

                bool executed;
                try { executed = incident.Worker.TryExecute(parms); }
                catch (Exception e) { return Fail("TryExecute threw: " + e.GetType().Name + ": " + e.Message); }

                var windowsOpened = WindowsOpenedSince(windowIdsBefore);

                var after = new Dictionary<Faction, int>();
                foreach (var p in map.mapPawns.AllPawnsSpawned)
                    if (p.Faction != null)
                        after[p.Faction] = (after.TryGetValue(p.Faction, out var an) ? an : 0) + 1;

                var arrivals = new List<object>();
                foreach (var kv in after)
                {
                    int was; before.TryGetValue(kv.Key, out was);
                    if (kv.Value > was)
                        arrivals.Add(new
                        {
                            faction = kv.Key.def.defName,
                            name = kv.Key.Name,
                            pawnsArrived = kv.Value - was,
                            hostileToPlayer = kv.Key.HostileTo(Faction.OfPlayer)
                        });
                }

                var usedFaction = parms.faction;
                bool substituted = requestedFaction != null && usedFaction != null
                                   && usedFaction != requestedFaction;

                int pawnsArrivedTotal = 0;
                foreach (var a in arrivals)
                    pawnsArrivedTotal += (int)a.GetType().GetProperty("pawnsArrived").GetValue(a, null);
                bool blockedByDialog = windowsOpened.Count > 0 && pawnsArrivedTotal == 0;
                string swallowNote = DialogSwallowNote(windowsOpened, pawnsArrivedTotal == 0);

                return (object)new
                {
                    success = executed && !blockedByDialog, dryRun = false, resolved, executed, factionNotes,
                    // 🔑 THE ANSWER TO "executed:true AND NOTHING HAPPENED". A window that
                    // appeared across TryExecute means a Harmony prefix pushed a modal in
                    // place of the raid; nothing on the bridge can answer it.
                    windowsOpened,
                    blockedByDialog,
                    // 🔑 THE OUTCOME, which `resolved` is not. `actual` is the faction the
                    // worker ended up using (it writes back into parms); `arrived` is counted
                    // off the map, so it is true even if the worker is patched by a mod.
                    actual = new
                    {
                        faction = usedFaction != null ? usedFaction.def.defName : null,
                        name = usedFaction != null ? usedFaction.Name : null,
                        substituted,
                        requested = requestedFaction != null ? requestedFaction.def.defName : null
                    },
                    arrived = arrivals,
                    pawnsArrivedTotal,
                    note = blockedByDialog
                        ? swallowNote
                        : (!executed
                            ? "TryExecute returned false - the worker refused these parms."
                            : (substituted
                                ? "⚠ RAIDED WITH A DIFFERENT FACTION. Asked for "
                                  + requestedFaction.def.defName + ", the worker used "
                                  + usedFaction.def.defName + " - a non-hostile faction cannot raid. "
                                  + "This is correct engine behaviour; the defect was never reporting it."
                                : "Raid fired. arrived[] is counted off the map; an arrival mode that "
                                  + "delays entry can legitimately show 0 pawns this instant.")),
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
                "Bomb","BombSuper","MiningBomb","Thump","Flame","RSW_Burn","AcidBurn","ElectricalBurn",
                "Vaporize","NociosphereVaporize","EMP","Stun","MechBandShockwave","Smoke","ToxGas",
                "DeadlifeDust","Extinguish"
            };

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/map_explosion",
            Description =
                "*** ACTS ON THE LIVE MAP *** Detonate an explosion of any type at a cell. " +
                "damType is a DamageDef: Bomb · BombSuper · Thump · Flame · RSW_Burn · AcidBurn · " +
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


        // ================================================================
        //  SOCIAL EVENTS — parties, marriages, funerals, rituals
        //
        //  🔑 Only THREE GatheringDefs ship: Party, MarriageCeremony, Concert.
        //     There is no Speech gathering - speech is a RITUAL.
        //  🔑 The game-condition gates are NOT in Worker.TryExecute. They live in
        //     GatheringDef.CanExecute, so calling the worker directly bypasses
        //     hour-of-day, danger rating, the 4-colonist minimum, bleeding, the
        //     drafted ratio and the guest count - which is exactly what vanilla's
        //     own debug action does.
        //  🔴 respectTimetable is NOT one of those gates. It filters attendees at
        //     JOIN time, so a forced party during a Work block starts and STAYS
        //     EMPTY while burning its timer.
        //  🔴 Gathering lords have ShouldExistWithoutPawns => true, so an empty
        //     one is NOT auto-culled. jawa/social_cancel is the escape hatch and
        //     ships alongside deliberately.
        // ================================================================

        [Tool(
            "jawa/social_list",
            Description =
                "List what social events this game can run: every GatheringDef with whether " +
                "it CAN execute right now and which gate is failing, plus every ritual " +
                "precept on the player ideoligion with its CanStartRitualNow reason. " +
                "Read-only, and the fastest way to find out why a party will not start.",
            ResultDescription = "success, gatherings[], rituals[], ideologyActive.")]
        public static async Task<object> SocialList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                var gs = new List<object>();
                foreach (var d in DefDatabase<GatheringDef>.AllDefsListForReading)
                {
                    bool canNow = false, canIgnoring = false;
                    try { canNow = d.CanExecute(map, null); } catch { }
                    try { canIgnoring = d.CanExecute(map, null, true); } catch { }
                    gs.Add(new
                    {
                        def = d.defName,
                        canExecuteNow = canNow,
                        canExecuteIgnoringConditions = canIgnoring,
                        respectTimetable = d.respectTimetable,
                        hasDuty = d.duty != null,
                    });
                }

                var rs = new List<object>();
                bool ideo = ModsConfig.IdeologyActive;
                try
                {
                    var primary = Faction.OfPlayer != null && Faction.OfPlayer.ideos != null
                        ? Faction.OfPlayer.ideos.PrimaryIdeo : null;
                    if (primary != null)
                        foreach (var pr in primary.PreceptsListForReading.OfType<Precept_Ritual>())
                        {
                            string why = null;
                            try { why = pr.behavior != null ? pr.behavior.CanStartRitualNow(TargetInfo.Invalid, pr) : "no behavior"; }
                            catch (Exception e) { why = e.GetType().Name + ": " + e.Message; }
                            rs.Add(new { precept = pr.def.defName, label = pr.LabelCap, blockedBecause = why });
                        }
                }
                catch (Exception e) { Log.Warning("[JawaBench] social_list rituals: " + e.Message); }

                return (object)new
                {
                    success = true,
                    ideologyActive = ideo,
                    note = "Only Party, MarriageCeremony and Concert ship as GatheringDefs. Funerals are an IDEOLOGY RITUAL, not a gathering.",
                    gatherings = gs,
                    ritualCount = rs.Count,
                    rituals = rs,
                    activeLords = map.lordManager.lords.Count,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/social_gathering_start",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Throw a party or a concert. " +
                "force=true (default) calls GatheringWorker.TryExecute directly, which is " +
                "what vanilla's own debug action does and bypasses hour-of-day, danger " +
                "rating, the 4-colonist minimum, bleeding, the drafted ratio and the guest " +
                "count. force=false honours all of them and reports which one refused. " +
                "🔴 WHAT FORCE CANNOT BYPASS: an eligible organizer must exist and a spot " +
                "must be found. No party building is needed - the finder falls back to a " +
                "random cell within 25 of the organizer. " +
                "🔴 `respectTimetable` is NOT bypassable: a forced party during a Work block " +
                "starts and stays EMPTY. Attendees are PULL, not push - the lord begins with " +
                "zero pawns and colonists self-join.",
            ResultDescription = "success, started, the gathering, and the lord count after.")]
        public static async Task<object> SocialGatheringStart(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "GatheringDef: Party or Concert. Not MarriageCeremony - use jawa/social_marry.")] string gathering = "Party",
            [ToolParameter(Description = "Organizer pawn id. Empty lets the game pick.")] string organizer = null,
            [ToolParameter(Description = "Bypass the game-condition gates. Default true.")] bool force = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var gd = DefDatabase<GatheringDef>.GetNamedSilentFail((gathering ?? "Party").Trim());
                if (gd == null) return Fail("No GatheringDef '" + gathering + "'. Only Party, MarriageCeremony and Concert ship.",
                                            DefDatabase<GatheringDef>.AllDefsListForReading.Select(d => d.defName).ToList());
                if (gd.defName == "MarriageCeremony")
                    return Fail("MarriageCeremony has no `duty` of its own and its LordJob hardcodes Party's toils. Use jawa/social_marry, which also handles the mandatory Fiance relation.");

                Pawn org = null;
                if (!string.IsNullOrEmpty(organizer)) { string e2; org = FindPawn(organizer, out e2); if (org == null) return Fail(e2); }

                var notes = new List<string>();
                if (!force)
                {
                    bool ok = false;
                    try { ok = gd.CanExecute(map, org); } catch { }
                    if (!ok) return Fail("GatheringDef.CanExecute refused and force=false. The gates are: hour 4-21, no blocking lord, " +
                                         "danger rating None, at least 4 free colonists, nobody bleeding, under half drafted, and enough " +
                                         "willing guests. Pass force=true to bypass all of them.");
                }

                int lordsBefore = map.lordManager.lords.Count;
                bool started;
                try { started = gd.Worker.TryExecute(map, org); }
                catch (Exception e) { return Fail("TryExecute threw: " + e.GetType().Name + ": " + e.Message); }

                if (!started)
                    notes.Add("TryExecute returned FALSE. force cannot bypass these two: an eligible organizer must exist " +
                              "(humanlike, not already in a lord, not in bed or a mental state), and a spot must be found.");
                if (started && gd.respectTimetable)
                    notes.Add("⚠️ this gathering respects the timetable - if colonists are on a Work block they will NOT join and the party will be empty.");

                return (object)new
                {
                    success = true, started, gathering = gd.defName, forced = force, notes,
                    organizer = org != null ? org.LabelShort : "(game picked)",
                    lordsBefore, lordsAfter = map.lordManager.lords.Count,
                    hint = "Attendees self-join over the next ticks - step time to see them gather. jawa/social_cancel clears a stuck one.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/social_marry",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Marry two pawns, with or without a ceremony. " +
                "ceremony=true starts the real wedding gathering; false marries them instantly " +
                "via MarriageCeremonyUtility.Married. " +
                "🔴 A `Fiance` DIRECT RELATION IS MANDATORY for the ceremony, and the second " +
                "pawn argument is IGNORED by RimWorld - GatheringWorker_MarriageCeremony " +
                "re-derives the partner from the organizer's Fiance relation. This tool sets " +
                "that relation first (clearing Lover/Spouse), exactly as the debug action does. " +
                "🔑 The ceremony and the marriage are SEPARABLE: the state change happens " +
                "inside the ceremony's own job, so a ceremony with no Fiance never advances, " +
                "and Married() alone gives a marriage with no party.",
            ResultDescription = "success, married, ceremonyStarted, relations after.")]
        public static async Task<object> SocialMarry(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "First pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "Second pawn id or name.")] string otherPawn = null,
            [ToolParameter(Description = "Run the wedding gathering. false marries instantly.")] bool ceremony = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var a = FindPawn(pawn, out err);
                if (a == null) return Fail(err);
                string e2; var b = FindPawn(otherPawn, out e2);
                if (b == null) return Fail(e2);
                if (a == b) return Fail("A pawn cannot marry itself.");
                var map = a.Map ?? b.Map;
                if (map == null) return Fail("Neither pawn is on a map.");

                var notes = new List<string>();
                bool married = false, started = false;

                try
                {
                    if (!ceremony)
                    {
                        MarriageCeremonyUtility.Married(a, b);
                        married = true;
                        notes.Add("MarriageCeremonyUtility.Married - instant, no party. Ex-spouses cleared, thoughts both ways, renamed, bed shared.");
                    }
                    else
                    {
                        // The ceremony re-derives the partner from the Fiance relation and
                        // IGNORES the second argument, so the relation must exist first.
                        foreach (var d in new[] { PawnRelationDefOf.Lover, PawnRelationDefOf.Spouse })
                            if (a.relations.DirectRelationExists(d, b)) { a.relations.TryRemoveDirectRelation(d, b); notes.Add("cleared " + d.defName + " so Fiance can be set"); }
                        if (!a.relations.DirectRelationExists(PawnRelationDefOf.Fiance, b))
                        { a.relations.AddDirectRelation(PawnRelationDefOf.Fiance, b); notes.Add("set the mandatory Fiance relation"); }

                        started = map.lordsStarter.TryStartMarriageCeremony(a, b);
                        if (!started)
                            notes.Add("TryStartMarriageCeremony returned FALSE. It already bypasses the game conditions, so what is left is: " +
                                      "both fiances must pass PawnCanStartOrContinueGathering (not bleeding, not drafted, not asleep, not in a lord), " +
                                      "and a marriage site must be findable.");
                        else
                            notes.Add("ceremony lord created - the pair walk to the site and the marriage happens in the ceremony's own job, not here");
                    }
                }
                catch (Exception ex) { return Fail(ex.GetType().Name + ": " + ex.Message); }

                return (object)new
                {
                    success = true, ceremony, married, ceremonyStarted = started, notes,
                    relations = a.relations.DirectRelations
                        .Select(r => new { def = r.def.defName, with = r.otherPawn != null ? r.otherPawn.LabelShort : null }).ToList(),
                    lords = map.lordManager.lords.Count,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/ritual_start",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Start an Ideology ritual by precept name - " +
                "Funeral, Festival, Trial, Conversion, GladiatorDuel, ScarificationCeremony, " +
                "LeaderSpeech and the rest. " +
                "🔑 A FUNERAL IS A RITUAL, NOT A GATHERING - but it is NOT Ideology-only: " +
                "FuneralBase is <classic>true</classic>, so Funeral, FuneralNoCorpse and the " +
                "Classic_ parties are present even with Ideology uninstalled. The gate is " +
                "whether the PRECEPT is on the ideo, never the DLC flag. " +
                "🔴 RitualBehaviorWorker.TryExecuteOn is VOID AND FAILS SILENTLY, so this " +
                "calls CanStartRitualNow first and returns its reason string rather than " +
                "claiming success. Roles are auto-filled via FillPawns.",
            ResultDescription = "success, started, blockedBecause, participants, lords after.")]
        public static async Task<object> RitualStart(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Precept defName, e.g. Funeral, Festival, Trial.")] string ritual = null,
            [ToolParameter(Description = "Target thing id (a grave for a funeral, an altar for a festival). Empty uses the organizer's cell.")] string targetThingId = null,
            [ToolParameter(Description = "Organizer pawn id. Empty picks a colonist.")] string organizer = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                // 🔴 CORRECTED 2026-08-20: rituals are NOT all Ideology-only. `FuneralBase`
                // carries <classic>true</classic>, and IdeoGenerator.GenerateClassicIdeo adds
                // EVERY classic precept to the single ideo a no-expansion game builds - so
                // Funeral, FuneralNoCorpse, Classic_DrumParty and Classic_DanceParty exist
                // with Ideology uninstalled. Gate on the PRECEPT being present, never on the
                // DLC flag.
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(ritual)) return Fail("Give a ritual precept defName.");

                var ideo = Faction.OfPlayer != null && Faction.OfPlayer.ideos != null ? Faction.OfPlayer.ideos.PrimaryIdeo : null;
                if (ideo == null) return Fail("The player faction has no primary ideoligion.");

                var pr = ideo.PreceptsListForReading.OfType<Precept_Ritual>()
                    .FirstOrDefault(x => string.Equals(x.def.defName, ritual.Trim(), StringComparison.OrdinalIgnoreCase));
                if (pr == null)
                    return Fail("The player ideoligion has no ritual precept '" + ritual + "'. It has: " +
                        string.Join(", ", ideo.PreceptsListForReading.OfType<Precept_Ritual>().Select(x => x.def.defName).ToArray()) +
                        (ModsConfig.IdeologyActive ? "" :
                         " (Ideology is OFF, so only <classic> precepts are present - Funeral, FuneralNoCorpse, " +
                         "Classic_DrumParty and Classic_DanceParty survive; Festival, Trial, Conversion and the rest do not.)"));

                Pawn org = null;
                if (!string.IsNullOrEmpty(organizer)) { string e2; org = FindPawn(organizer, out e2); }
                if (org == null) org = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
                if (org == null) return Fail("No free colonist to organise it.");

                TargetInfo target = new TargetInfo(org.Position, map);
                if (!string.IsNullOrEmpty(targetThingId))
                {
                    var t = map.listerThings.AllThings.FirstOrDefault(x =>
                        string.Equals(x.ThingID, targetThingId.Trim(), StringComparison.OrdinalIgnoreCase));
                    if (t == null) return Fail("No thing with id '" + targetThingId + "' on this map.");
                    target = new TargetInfo(t);
                }

                string blocked = null;
                try { blocked = pr.behavior != null ? pr.behavior.CanStartRitualNow(target, pr) : "the precept has no behavior worker"; }
                catch (Exception e) { blocked = e.GetType().Name + ": " + e.Message; }
                if (!string.IsNullOrEmpty(blocked))
                    return Fail("CanStartRitualNow refused: " + blocked, new { precept = pr.def.defName, target = target.ToString() });

                int before = map.lordManager.lords.Count;
                int participants = 0;
                try
                {
                    var assignments = RitualRoleAssignments_Create(pr, target, map, out participants);
                    if (participants <= 0)
                        return Fail("No participants could be assigned. Starting a ritual with an empty participant list risks leaving a lord " +
                                    "on the map that nothing culls, so refusing.");
                    pr.behavior.TryExecuteOn(target, org, pr, null, assignments, true);
                }
                catch (Exception e) { return Fail("Starting the ritual threw: " + e.GetType().Name + ": " + e.Message); }

                int after = map.lordManager.lords.Count;
                return (object)new
                {
                    success = true,
                    started = after > before,
                    precept = pr.def.defName,
                    organizer = org.LabelShort,
                    participants,
                    lordsBefore = before, lordsAfter = after,
                    note = after > before
                        ? "Ritual lord created. TryExecuteOn is void, so the lord count is the evidence, not a return value."
                        : "No new lord appeared - TryExecuteOn fails SILENTLY. Treat this as a failure.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        /// <summary>Auto-fill ritual roles. Isolated so a signature change is one edit.</summary>
        private static RitualRoleAssignments RitualRoleAssignments_Create(
            Precept_Ritual pr, TargetInfo target, Map map, out int participants)
        {
            participants = 0;
            var a = Dialog_BeginRitual.CreateRitualRoleAssignments(pr, target, map, null, null, null, null);
            if (a != null)
            {
                try { a.FillPawns(null, target); } catch (Exception e) { Log.Warning("[JawaBench] FillPawns: " + e.Message); }
                try { participants = a.Participants != null ? a.Participants.Count() : 0; } catch { }
            }
            return a;
        }

        [Tool(
            "jawa/social_cancel",
            Description =
                "Clear a stuck gathering or ritual lord. " +
                "🔴 THIS IS NOT OPTIONAL HOUSEKEEPING. Voluntarily-joinable lords have " +
                "ShouldExistWithoutPawns => true, so a party or ritual that nobody joined is " +
                "NOT culled - it sits on the map until its timer expires, blocking new " +
                "gatherings (AllowStartNewGatherings). List first, then remove by index.",
            ResultDescription = "success, lords[] before, removed.")]
        public static async Task<object> SocialCancel(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' or 'remove'.")] string action = "list",
            [ToolParameter(Description = "Remove every gathering/ritual lord.")] bool all = false,
            [ToolParameter(Description = "Lord index from 'list'.")] int index = -1)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                Func<Lord, bool> isSocial = l => l != null && l.LordJob != null &&
                    (l.LordJob is LordJob_VoluntarilyJoinable || l.LordJob.GetType().Name.Contains("Ritual"));

                var rows = lm.lords.Select((l, i) => new
                {
                    index = i,
                    job = l.LordJob != null ? l.LordJob.GetType().Name : "(null)",
                    pawns = l.ownedPawns != null ? l.ownedPawns.Count : 0,
                    social = isSocial(l),
                    faction = l.faction != null ? l.faction.def.defName : null,
                }).ToList();

                int removed = 0;
                if (string.Equals(action, "remove", StringComparison.OrdinalIgnoreCase))
                {
                    var targets = all
                        ? lm.lords.Where(l => isSocial(l)).ToList()
                        : (index >= 0 && index < lm.lords.Count ? new List<Lord> { lm.lords[index] } : new List<Lord>());
                    if (targets.Count == 0) return Fail("Nothing to remove. Give all=true or a valid index from 'list'.", rows);
                    foreach (var l in targets) { try { lm.RemoveLord(l); removed++; } catch (Exception e) { Log.Warning("[JawaBench] RemoveLord: " + e.Message); } }
                }

                return (object)new
                {
                    success = true, action, removed,
                    lordsBefore = rows.Count, lordsAfter = lm.lords.Count,
                    lords = rows, ticksGame = TicksGameSafe(),
                };
            });
        }
#endif // JAWA_GM_TOOLS

    }
}