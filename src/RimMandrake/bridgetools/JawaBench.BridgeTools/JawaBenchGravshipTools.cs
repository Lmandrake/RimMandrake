// JawaBenchGravshipTools.cs - gravship launch, travel and landing, driven safely.
//
// GRAVSHIP_LAUNCH_TRAVEL_1 (owner, 2026-08-28: "let's see if you can do it").
//
// FACTS THAT SHAPE THIS FILE, read from 1.6 source:
//  * The vanilla flow is WorldComponent_GravshipController.InitiateTakeoff(engine, tile):
//    capture -> GenerateGravship -> ~10s cutscene -> TakeoffEnded -> AbandonMap (unless a
//    GravAnchor is on the map) + TravelTo. Arrival spawns a GravshipLandingMarker and WAITS
//    for confirmation; marker.BeginLanding(controller) is what the player's confirm does.
//  * The complete launch gate is Building_GravEngine.CanLaunch(console) PLUS the tile-picker
//    closure in CompPilotConsole.StartChoosingDestination_NewTemp: TryGetPathFuelCost with
//    (curTile, tile, 10f, engine.FuelUseageFactor), cost <= TotalFuel, distance <= layer-
//    adjusted MaxLaunchDistance, signal-jammer rule, same-tile-needs-GravAnchor rule, and
//    TileFinder.IsValidTileForNewSettlement(forGravship: true) when no map exists there.
//    We reproduce those calls argument-for-argument; an equivalent-looking check is not
//    the engine's check.
//  * The "DEV: Launch instantly" gizmo sets engine.launchInfo = new LaunchInfo { quality,
//    doNegativeOutcome } before launching. launchInfo left null NREs at landing
//    (WorldComponent_GravshipController reads launchInfo.doNegativeOutcome), so the launch
//    tool always sets it.
//  * ConsumeFuel(tile) burns proportionally from every fuel-providing facility and starts
//    the cooldown; vanilla calls it just before InitiateTakeoff. So do we.
//  * Nothing after InitiateTakeoff is undoable from the bridge, and the origin map is
//    DESTROYED at TakeoffEnded unless a GravAnchor stays behind.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimWorld.Planet;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ------------------------------------------------------------------
        // shared: resolve the player grav engine, preferring the current map
        // ------------------------------------------------------------------
        private static Building_GravEngine ResolveGravEngine(string expectEngineId, out string engineErr)
        {
            engineErr = null;
            var candidates = new List<Building_GravEngine>();
            foreach (var m in Find.Maps)
            {
                var e = GravshipUtility.GetPlayerGravEngine_NewTemp(m);
                if (e != null) candidates.Add(e);
            }
            if (candidates.Count == 0) { engineErr = "No player grav engine on any map."; return null; }

            Building_GravEngine engine = null;
            if (!string.IsNullOrEmpty(expectEngineId))
            {
                engine = candidates.FirstOrDefault(e => e.ThingID == expectEngineId);
                if (engine == null)
                {
                    engineErr = "expectEngineId '" + expectEngineId + "' matched no player grav engine. Present: "
                        + string.Join(", ", candidates.Select(e => e.ThingID)) + ".";
                    return null;
                }
                return engine;
            }
            if (candidates.Count == 1) return candidates[0];
            engine = candidates.FirstOrDefault(e => e.Map == Find.CurrentMap);
            if (engine != null) return engine;
            engineErr = "Multiple grav engines and none on the current map - pass expectEngineId. Present: "
                + string.Join(", ", candidates.Select(e => e.ThingID)) + ".";
            return null;
        }

        // ------------------------------------------------------------------
        // shared: every gate the game itself runs before a launch, verbatim
        // ------------------------------------------------------------------
        private static List<string> GravshipLaunchGates(
            Building_GravEngine engine, PlanetTile target,
            out float cost, out int distance, out int maxDistLayerAdjusted)
        {
            var reasons = new List<string>();
            cost = -1f; distance = -1;
            var curTile = engine.Map.Tile;

            // Building_GravEngine.CanLaunch, via the console the way CanUseNow does.
            var console = engine.GravshipComponents.OfType<CompPilotConsole>().FirstOrDefault();
            if (console == null)
            {
                reasons.Add("No pilot console is linked to the engine.");
                maxDistLayerAdjusted = 0;
                return reasons;
            }
            var canUse = console.CanUseNow();     // breakdown, console-cell substructure, then engine.CanLaunch
            if (!canUse.Accepted) reasons.Add("Engine refuses: " + canUse.Reason);

            maxDistLayerAdjusted = Mathf.FloorToInt(engine.MaxLaunchDistance / target.Layer.Def.rangeDistanceFactor);

            // The tile-picker closure, argument for argument.
            if (!GravshipUtility.TryGetPathFuelCost(curTile, target, out cost, out distance, 10f, engine.FuelUseageFactor))
                reasons.Add("No fuel path to that tile (CannotLaunchDestination).");
            else
            {
                if (cost > engine.TotalFuel)
                    reasons.Add("Not enough fuel: cost " + cost.ToString("F0") + " > aboard " + engine.TotalFuel.ToString("F0") + ".");
                if (distance > maxDistLayerAdjusted)
                    reasons.Add("Beyond thruster range: distance " + distance + " > " + maxDistLayerAdjusted + ".");
            }
            if (!engine.HasSignalJammer
                && Find.WorldObjects.TryGetWorldObjectAt<MapParent>(target, out var wo)
                && wo.RequiresSignalJammerToReach)
                reasons.Add("Destination requires a signal jammer.");
            if (target == curTile && !engine.Map.listerThings.AnyThingWithDef(ThingDefOf.GravAnchor))
                reasons.Add("Cannot land on the same tile without a grav anchor.");
            var mp = Find.World.worldObjects.MapParentAt(target);
            if (mp == null || !mp.HasMap)
            {
                var sb = new StringBuilder();
                if (!TileFinder.IsValidTileForNewSettlement(target, sb, forGravship: true))
                    reasons.Add("Tile invalid for landing: " + sb);
            }
            return reasons;
        }

        [Tool(
            "jawa/gravship_status",
            Description =
                "Read the whole gravship state machine: the engine (fuel, range, cooldown, missing " +
                "components), and which of the three in-flight states the game is in - cutscene " +
                "running, travelling on the world layer, or WAITING AT A LANDING MARKER for " +
                "confirmation. That third state is the halfway point a failed or abandoned launch " +
                "strands you in; jawa/gravship_land resolves it. Read-only.",
            ResultDescription =
                "success, engines[] (thingId, map, tile, fuel, maxFuel, fuelPerTile, rangeTiles, " +
                "cooldownTicksLeft, missingComponents[], substructureCells, launchInfoSet), " +
                "cutsceneInProgress, travelling, landingConfirmationPending, landingMarker{map,x,z,rot}.")]
        public static async Task<object> GravshipStatus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.OdysseyActive) return Fail("Odyssey is not active.");
                var engines = new List<object>();
                foreach (var m in Find.Maps)
                {
                    var e = GravshipUtility.GetPlayerGravEngine_NewTemp(m);
                    if (e == null) continue;
                    engines.Add(new
                    {
                        thingId = e.ThingID,
                        name = e.RenamableLabel,
                        mapId = m.uniqueID,
                        tile = m.Tile.tileId,
                        x = e.Position.x, z = e.Position.z,
                        fuel = e.TotalFuel, maxFuel = e.MaxFuel,
                        fuelPerTile = e.FuelPerTile,
                        rangeTiles = e.MaxLaunchDistance,
                        cooldownTicksLeft = Math.Max(0, e.cooldownCompleteTick - GenTicks.TicksGame),
                        missingComponents = e.MissingComponents.Select(c => c.defName).ToList(),
                        substructureCells = e.ValidSubstructureNoRegen.Count,
                        launchInfoSet = e.launchInfo != null,
                    });
                }
                var ctrl = Find.GravshipController;
                object marker = null;
                if (ctrl != null && ctrl.LandingAreaConfirmationInProgress)
                {
                    foreach (var m in Find.Maps)
                    {
                        var lm = m.listerThings.AllThings.OfType<GravshipLandingMarker>().FirstOrDefault();
                        if (lm == null) continue;
                        marker = new { mapId = m.uniqueID, tile = m.Tile.tileId, x = lm.Position.x, z = lm.Position.z, rot = lm.GravshipRotation.AsInt };
                        break;
                    }
                }
                return (object)new
                {
                    success = true,
                    engineCount = engines.Count,
                    engines,
                    cutsceneInProgress = WorldComponent_GravshipController.CutsceneInProgress,
                    travelling = ctrl != null && ctrl.IsGravshipTravelling,
                    landingConfirmationPending = ctrl != null && ctrl.LandingAreaConfirmationInProgress,
                    landingMarker = marker,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/gravship_launch_check",
            Description =
                "Every gate the game runs before a gravship launch, reproduced argument-for-argument " +
                "from CompPilotConsole and Building_GravEngine.CanLaunch, WITHOUT launching: fuel " +
                "path and cost at this engine's own fuel factor, range at the destination layer's " +
                "distance factor, console/cooldown/thruster/substructure state, signal jammer, " +
                "same-tile grav-anchor rule, and settlement validity of the target tile. Read-only; " +
                "call before every jawa/gravship_launch.",
            ResultDescription =
                "success, wouldLaunch, reasons[] (empty when wouldLaunch), fuelCost, fuelAboard, " +
                "distance, maxDistance, engineId.")]
        public static async Task<object> GravshipLaunchCheck(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Destination world tile id (surface layer).")] int targetTile,
            [ToolParameter(Description = "Engine ThingID to assert, e.g. 'GravEngine64276'. Optional when only one engine exists.")] string expectEngineId = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.OdysseyActive) return Fail("Odyssey is not active.");
                if (WorldComponent_GravshipController.CutsceneInProgress) return Fail("A gravship cutscene is in progress.");
                var engine = ResolveGravEngine(expectEngineId, out var err);
                if (engine == null) return Fail(err);
                if (targetTile < 0) return Fail("targetTile must be a surface tile id >= 0.");
                var target = new PlanetTile(targetTile, Find.WorldGrid.Surface);
                var reasons = GravshipLaunchGates(engine, target, out var cost, out var dist, out var maxDist);
                return (object)new
                {
                    success = true,
                    wouldLaunch = reasons.Count == 0,
                    reasons,
                    engineId = engine.ThingID,
                    originTile = engine.Map.Tile.tileId,
                    targetTile,
                    fuelCost = cost,
                    fuelAboard = engine.TotalFuel,
                    distance = dist,
                    maxDistance = maxDist,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/gravship_launch",
            Description =
                "Launch the player gravship to a world tile - the vanilla dev-gizmo path: set " +
                "LaunchInfo, consume fuel, InitiateTakeoff. 🔴 NOT UNDOABLE, and the origin map is " +
                "DESTROYED when the cutscene ends unless a GravAnchor stays behind. Refuses unless " +
                "every gate jawa/gravship_launch_check reports passes; short fuel refuses, never " +
                "strands. Completion is ASYNCHRONOUS: ~10s cutscene (instant with cutscenes off), " +
                "then AbandonMap+TravelTo, then world travel over game ticks, then a LANDING MARKER " +
                "waits on the destination map - poll jawa/gravship_status and finish with " +
                "jawa/gravship_land. The settle-proximity goodwill confirmation dialog is bypassed " +
                "on purpose; any goodwill consequences of landing near a faction still apply.",
            ResultDescription =
                "success, launched, dryRun, fuelCost, fuelAboard, distance, engineId, originTile, " +
                "targetTile, originMapWillBeDestroyed, nextState.")]
        public static async Task<object> GravshipLaunch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Destination world tile id (surface layer).")] int targetTile,
            [ToolParameter(Description = "Report what would happen without launching. DEFAULTS TRUE - pass false to actually fly.")] bool dryRun = true,
            [ToolParameter(Description = "Launch quality 0..1: drives landing-outcome odds and cooldown, like the takeoff ritual's result.")] float quality = 1f,
            [ToolParameter(Description = "Engine ThingID to assert, e.g. 'GravEngine64276'. Optional when only one engine exists.")] string expectEngineId = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.OdysseyActive) return Fail("Odyssey is not active.");
                var ctrl = Find.GravshipController;
                if (WorldComponent_GravshipController.CutsceneInProgress) return Fail("A gravship cutscene is already in progress.");
                if (ctrl != null && ctrl.IsGravshipTravelling) return Fail("The gravship is already travelling.");
                if (ctrl != null && ctrl.LandingAreaConfirmationInProgress) return Fail("A landing is awaiting confirmation - jawa/gravship_land first.");
                var engine = ResolveGravEngine(expectEngineId, out var err);
                if (engine == null) return Fail(err);
                if (targetTile < 0) return Fail("targetTile must be a surface tile id >= 0.");
                var target = new PlanetTile(targetTile, Find.WorldGrid.Surface);

                var reasons = GravshipLaunchGates(engine, target, out var cost, out var dist, out var maxDist);
                bool anchor = engine.Map.listerThings.AnyThingWithDef(ThingDefOf.GravAnchor);
                if (reasons.Count > 0)
                    return Fail("Launch refused:\n - " + string.Join("\n - ", reasons),
                        new { fuelCost = cost, fuelAboard = engine.TotalFuel, distance = dist, maxDistance = maxDist });

                if (dryRun)
                    return (object)new
                    {
                        success = true, launched = false, dryRun = true,
                        engineId = engine.ThingID,
                        originTile = engine.Map.Tile.tileId, targetTile,
                        fuelCost = cost, fuelAboard = engine.TotalFuel, distance = dist,
                        originMapWillBeDestroyed = !anchor,
                        nextState = "pass dryRun=false to launch",
                        ticksGame = TicksGameSafe(),
                    };

                // The vanilla confirmed-launch closure, minus the two dialogs.
                engine.launchInfo = new LaunchInfo { quality = Mathf.Clamp01(quality), doNegativeOutcome = false };
                WorldComponent_GravshipController.DestroyTreesAroundSubstructure(engine.Map, engine.ValidSubstructure);
                Find.World.renderer.wantedMode = WorldRenderMode.None;
                engine.ConsumeFuel(target);
                Find.GravshipController.InitiateTakeoff(engine, target);

                return (object)new
                {
                    success = true, launched = true, dryRun = false,
                    engineId = engine.ThingID,
                    originTile = engine.Map.Tile.tileId, targetTile,
                    fuelCost = cost, fuelAboard = engine.TotalFuel, distance = dist,
                    originMapWillBeDestroyed = !anchor,
                    nextState = "cutscene -> travel -> landing marker; poll jawa/gravship_status, then jawa/gravship_land",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/gravship_land",
            Description =
                "Confirm the pending gravship landing - what the player's confirm button does: " +
                "marker.BeginLanding, landing cutscene, ship placed. Refuses when no landing is " +
                "waiting (jawa/gravship_status names the state). By default lands exactly where the " +
                "arrival placed the marker, which the game already validated; pass x/z (and rot " +
                "0-3) to move the marker first - bounds-checked only, terrain validity is the " +
                "caller's risk. Placement is ASYNCHRONOUS: ~10s landing cutscene, then the ship " +
                "and its pawns exist on the new map.",
            ResultDescription = "success, landedAt{x,z,rot,mapId}, moved, nextState.")]
        public static async Task<object> GravshipLand(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Optional new marker x; requires z too.")] int x = -1,
            [ToolParameter(Description = "Optional new marker z; requires x too.")] int z = -1,
            [ToolParameter(Description = "Optional rotation 0..3 (N/E/S/W).")] int rot = -1)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.OdysseyActive) return Fail("Odyssey is not active.");
                var ctrl = Find.GravshipController;
                if (ctrl == null || !ctrl.LandingAreaConfirmationInProgress)
                    return Fail("No landing is awaiting confirmation.");
                if (WorldComponent_GravshipController.CutsceneInProgress)
                    return Fail("A gravship cutscene is in progress - wait for it to end.");
                GravshipLandingMarker marker = null; Map markerMap = null;
                foreach (var m in Find.Maps)
                {
                    marker = m.listerThings.AllThings.OfType<GravshipLandingMarker>().FirstOrDefault();
                    if (marker != null) { markerMap = m; break; }
                }
                if (marker == null) return Fail("Controller reports a pending landing but no marker was found on any map.");

                bool moved = false;
                if (rot >= 0)
                {
                    if (rot > 3) return Fail("rot must be 0..3.");
                    marker.GravshipRotation = new Rot4(rot);
                    moved = true;
                }
                if (x >= 0 || z >= 0)
                {
                    if (x < 0 || z < 0) return Fail("Pass both x and z, or neither.");
                    var pos = new IntVec3(x, 0, z);
                    foreach (var c in marker.GravshipCells)
                        if (!(c + pos).InBounds(markerMap))
                            return Fail("Ship cell " + (c + pos) + " would be out of map bounds at that position.");
                    marker.Position = pos;
                    marker.Notify_Moved();
                    moved = true;
                }
                var at = new { x = marker.Position.x, z = marker.Position.z, rot = marker.GravshipRotation.AsInt, mapId = markerMap.uniqueID };
                marker.BeginLanding(Find.GravshipController);
                return (object)new
                {
                    success = true,
                    landedAt = at,
                    moved,
                    nextState = "landing cutscene, then the ship exists on the map; verify with jawa/gravship_status and rimworld/list_colonists",
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif
    }
}
