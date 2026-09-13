// JawaBenchTransporterLaunchTools.cs - commit a REAL transport-pod launch headlessly.
//
// WHY THIS EXISTS. NINEFOLD_MISSING_EVENT_HOOKS_1. Ninefold's Ta'Baa hook is a
// Harmony pre/postfix pair around CompLaunchable.TryLaunch that credits the god only
// when vanilla's own commit marker `lastLaunchTick` changes. Nothing on the bridge
// could reach TryLaunch: every vanilla route runs through the launch gizmo ->
// StartChoosingDestination -> world-tile targeter, i.e. UI the bridge cannot drive.
// (The sibling gravship tool in JawaBenchGravshipTools.cs reaches the OTHER departure
// path, WorldComponent_GravshipController.InitiateTakeoff, but that one needs Odyssey,
// a built gravship with a fuelled engine and substructure, and it DESTROYS the origin
// map. This tool is the cheap, self-contained pod launch.)
//
// FACTS READ FROM 1.6 SOURCE (RimSage), each of which shapes a line below:
//  * CompLaunchable.TryLaunch(PlanetTile, TransportersArrivalAction) is PUBLIC and
//    returns void - no reflection anywhere in this file, and no return value to read.
//    Its four commit gates are: parent.Spawned; TransportersInGroup != null (which is
//    null unless groupID >= 0, i.e. loading was initiated); CanLaunch(); and the
//    destination distance against MaxLaunchDistanceAtFuelLevel. All four are checked
//    here BEFORE the call, and the commit is then confirmed by reading back vanilla's
//    own marker.
//  * `lastLaunchTick` is assigned unconditionally the instant every gate passes and
//    before any pod is processed - it is vanilla's canonical "a launch happened" flag
//    (CanLaunch's own cooldown test reads it back). Captured before, compared after.
//    This is the identical marker the Ninefold patch gates on, so a launch this tool
//    reports as committed is by construction one that patch saw.
//  * AncientTransportPod is the default pod ON PURPOSE: its launchable props set
//    requiresFuelingPort=false, so CompLaunchable_TransportPod reports infinite fuel
//    and needs NO adjacent fueling port, NO chemfuel and NO research. The buildable
//    TransportPod requires a fuelling-port building next to it and would make a
//    synthetic launch a construction exercise.
//  * A null arrivalAction is legal: TravellingTransporters.Arrived substitutes
//    LandInSpecificCell when a map exists at the destination tile, else FormCaravan.
//    Defaulting the destination to THIS map's own tile therefore makes the pod fly and
//    land back here - the whole event is self-contained and leaves no stranded caravan.
//  * TryLaunch destroys the pod Thing and spawns a FlyShipLeaving skyfaller, so a
//    synthetic pod cleans itself up; nothing is left to tidy.
//  * AnyInGroupIsUnderRoof is checked by CanLaunch, so the spawn cell must be unroofed;
//    this tool checks that itself and names it rather than returning a bare refusal.
//
// NO tool-name prefixes in prose in this file: build.py scans the assembly for such
// literals and a mention in a description becomes a phantom tool that blocks deploy.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/transporter_launch",
            Description =
                "Commit a real transport-pod launch without any UI: optionally spawn a launchable pod on " +
                "an unroofed cell, put it in its own transporter group, then call CompLaunchable.TryLaunch " +
                "- the single vanilla entry point every pod and shuttle launch funnels through, so every " +
                "Harmony patch on a launch fires. DESTRUCTIVE: a real launch consumes fuel, destroys the " +
                "pod Thing and sends its contents to the destination tile; dryRun DEFAULTS TRUE and " +
                "reports every gate without launching. Defaults to AncientTransportPod (needs no fuelling " +
                "port, no chemfuel, no research) and to THIS map's own tile, so the pod flies and lands " +
                "back here and nothing is stranded. REFUSES when no map is loaded, when the def has no " +
                "launchable or transporter comp, when the cell is out of bounds, roofed, fogged or already " +
                "holds a building, when CanLaunch reports a reason, and when the destination is beyond " +
                "range. Does NOT report success from the call itself - TryLaunch returns void; the launch " +
                "is confirmed only by reading vanilla's own commit marker lastLaunchTick back, plus the " +
                "skyfaller that appeared and the pod that no longer exists.",
            ResultDescription =
                "success, launched (from the lastLaunchTick change, NOT from the call returning), dryRun, " +
                "podDefName, podId, cell, spawnedPod, destinationTile, originTile, distance, maxDistance, " +
                "fuelLevel/fuelUnlimited, canLaunch, canLaunchReason, lastLaunchTickBefore/After, " +
                "podStillExists, skyfallerSpawned, skyfallerDefName, groupId.")]
        public static async Task<object> TransporterLaunch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Report every gate without launching. DEFAULTS TRUE - pass false to actually fly.")] bool dryRun = true,
            [ToolParameter(Description = "ThingID of an EXISTING transporter to launch, bare or Thing_-prefixed. When given, nothing is spawned and podDefName/x/z are ignored.")] string transporterId = null,
            [ToolParameter(Description = "ThingDef of the pod to spawn when transporterId is not given. Default 'AncientTransportPod' - the only vanilla pod that needs no fuelling port.")] string podDefName = "AncientTransportPod",
            [ToolParameter(Description = "Spawn cell x. Default: the nearest unroofed, unfogged, building-free cell to the map centre.")] int x = -1,
            [ToolParameter(Description = "Spawn cell z. Default: see x.")] int z = -1,
            [ToolParameter(Description = "Destination world tile id on the surface layer. Default -1 = this map's own tile, which makes the flight self-contained.")] int destinationTile = -1)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");

                PlanetTile dest = map.Tile;
                if (destinationTile >= 0)
                {
                    dest = new PlanetTile(destinationTile, Find.WorldGrid.Surface);
                }

                Thing pod = null;
                bool spawnedPod = false;
                IntVec3 cell = IntVec3.Invalid;

                if (!string.IsNullOrEmpty(transporterId))
                {
                    string bare = transporterId.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase)
                        ? transporterId.Substring(6) : transporterId;
                    pod = map.listerThings.AllThings.FirstOrDefault(t =>
                        string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase));
                    if (pod == null) return Fail("No thing with that id is spawned on the current map.", new { transporterId });
                    if (pod.TryGetComp<CompLaunchable>() == null)
                        return Fail("That thing has no CompLaunchable.", new { transporterId, defName = pod.def?.defName });
                    cell = pod.Position;
                }
                else
                {
                    ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(podDefName);
                    if (def == null)
                        return Fail("Unknown ThingDef.", new { podDefName, suggestions = DefSuggestions<ThingDef>(podDefName) });
                    if (def.comps == null || !def.comps.Any(c => c is CompProperties_Launchable))
                        return Fail("That ThingDef has no CompProperties_Launchable, so it can never reach TryLaunch.",
                            new { podDefName });
                    if (!def.comps.Any(c => c is CompProperties_Transporter))
                        return Fail("That ThingDef has no CompProperties_Transporter; TryLaunch needs a transporter group.",
                            new { podDefName });

                    if (x >= 0 && z >= 0)
                    {
                        cell = new IntVec3(x, 0, z);
                        string why = LaunchCellRefusal(map, cell);
                        if (why != null) return Fail("Spawn cell refused: " + why, new { x, z });
                    }
                    else
                    {
                        cell = FindLaunchCell(map);
                        if (!cell.IsValid)
                            return Fail("No unroofed, unfogged, building-free cell found within 60 of the map centre. "
                                + "Pass x/z explicitly.");
                    }

                    if (dryRun)
                    {
                        // Nothing is spawned on a dry run, so the per-pod gates below cannot be
                        // read. Report the cell verdict and stop rather than inventing them.
                        return (object)new
                        {
                            success = true,
                            launched = false,
                            dryRun = true,
                            podDefName = def.defName,
                            podId = (string)null,
                            spawnedPod = false,
                            cell = new { x = cell.x, z = cell.z },
                            originTile = map.Tile.tileId,
                            destinationTile = dest.tileId,
                            nextState = "pass dryRun=false to spawn the pod and launch it",
                            ticksGame = TicksGameSafe()
                        };
                    }

                    Thing made = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
                    pod = GenSpawn.Spawn(made, cell, map, WipeMode.Vanish);
                    spawnedPod = true;
                    if (Faction.OfPlayer != null && pod.def.CanHaveFaction) pod.SetFaction(Faction.OfPlayer);
                }

                CompLaunchable launchable = pod.TryGetComp<CompLaunchable>();
                CompTransporter transporter = pod.TryGetComp<CompTransporter>();
                if (launchable == null || transporter == null)
                {
                    if (spawnedPod && !pod.Destroyed) pod.Destroy();
                    return Fail("The pod has no launchable/transporter comp pair after spawning.",
                        new { defName = pod.def?.defName });
                }

                // TransportersInGroup is null until loading has been initiated; TryLaunch
                // logs an error and returns in that case, which would read as a silent no-op.
                int groupId = transporter.groupID;
                if (groupId < 0)
                {
                    groupId = TransporterUtility.InitiateLoading(new List<CompTransporter> { transporter });
                }

                string roofRefusal = cell.IsValid && cell.Roofed(map)
                    ? "the pod's cell is roofed (CanLaunch refuses a group under a roof)" : null;

                AcceptanceReport can = launchable.CanLaunch();
                float fuel = launchable.FuelLevel;
                bool fuelUnlimited = float.IsInfinity(fuel) || float.IsNaN(fuel);

                int distance = Find.WorldGrid.TraversalDistanceBetween(map.Tile, dest, true, int.MaxValue, true);
                // MinFuelLevelInGroup is private, but this group is a single pod, so its own
                // fuel level IS the group minimum. Stated rather than assumed.
                int maxDistance = launchable.MaxLaunchDistanceAtFuelLevel(fuel, dest.Layer);

                if (!can.Accepted || distance > maxDistance || roofRefusal != null)
                {
                    if (spawnedPod && !pod.Destroyed) pod.Destroy();   // leave no debris behind a refusal
                    return Fail("Launch refused before TryLaunch - it would have been a silent no-op.",
                        new
                        {
                            canLaunch = can.Accepted,
                            canLaunchReason = can.Accepted ? null : can.Reason,
                            roofRefusal,
                            distance,
                            maxDistance,
                            fuelLevel = fuelUnlimited ? -1f : fuel,
                            fuelUnlimited,
                            podDefName = pod.def?.defName,
                            spawnedPodDestroyed = spawnedPod
                        });
                }

                int before = launchable.lastLaunchTick;
                ThingDef skyfallerDef = (launchable.Props != null ? launchable.Props.skyfallerLeaving : null)
                                        ?? ThingDefOf.DropPodLeaving;
                int skyfallersBefore = map.listerThings.ThingsOfDef(skyfallerDef)?.Count ?? 0;
                string podId = pod.ThingID;
                IntVec3 launchCell = pod.Position;

                // 🔴 The transporterId (existing-pod) path never took the spawn-branch's
                // early dryRun return above, so without this check a dryRun=true call
                // against an existing transporter would fall straight through to a real
                // TryLaunch — exactly the "claims dry run, actually commits" trap this
                // tool exists to avoid on the OTHER side (see file header). All the gate
                // values needed for a full report are already computed above with no
                // side effect, so a dry run here costs nothing but the actual call.
                if (dryRun)
                {
                    return (object)new
                    {
                        success = true,
                        launched = false,
                        dryRun = true,
                        podDefName = pod.def?.defName,
                        podId,
                        spawnedPod,
                        cell = new { x = launchCell.x, z = launchCell.z },
                        groupId,
                        originTile = map.Tile.tileId,
                        destinationTile = dest.tileId,
                        distance,
                        maxDistance,
                        fuelLevel = fuelUnlimited ? -1f : fuel,
                        fuelUnlimited,
                        canLaunch = can.Accepted,
                        canLaunchReason = can.Accepted ? null : can.Reason,
                        lastLaunchTickBefore = before,
                        nextState = "pass dryRun=false to actually launch",
                        ticksGame = TicksGameSafe()
                    };
                }

                launchable.TryLaunch(dest, null);

                int after = launchable.lastLaunchTick;
                int skyfallersAfter = map.listerThings.ThingsOfDef(skyfallerDef)?.Count ?? 0;
                bool podStillExists = !pod.Destroyed;

                return (object)new
                {
                    success = true,
                    // 🔴 From vanilla's own commit marker, NOT from the call returning -
                    // TryLaunch is void and every one of its failure paths returns quietly.
                    launched = after != before,
                    dryRun = false,
                    podDefName = pod.def?.defName,
                    podId,
                    spawnedPod,
                    cell = new { x = launchCell.x, z = launchCell.z },
                    groupId,
                    originTile = map.Tile.tileId,
                    destinationTile = dest.tileId,
                    distance,
                    maxDistance,
                    fuelLevel = fuelUnlimited ? -1f : fuel,
                    fuelUnlimited,
                    canLaunch = can.Accepted,
                    canLaunchReason = can.Accepted ? null : can.Reason,
                    lastLaunchTickBefore = before,
                    lastLaunchTickAfter = after,
                    podStillExists,
                    skyfallerSpawned = skyfallersAfter > skyfallersBefore,
                    skyfallerDefName = skyfallerDef?.defName,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        /// <summary>Why this cell cannot hold a launchable pod, or null when it can.</summary>
        private static string LaunchCellRefusal(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return "out of bounds";
            if (c.Fogged(map)) return "fogged - the cell has never been seen";
            if (c.Roofed(map)) return "roofed - CanLaunch refuses any group under a roof";
            if (c.GetEdifice(map) != null) return "already holds a building";
            if (!c.Standable(map)) return "not standable";
            return null;
        }

        /// <summary>Nearest launch-legal cell to the map centre, or IntVec3.Invalid.</summary>
        private static IntVec3 FindLaunchCell(Map map)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 60f, true))
            {
                if (LaunchCellRefusal(map, c) == null) return c;
            }
            return IntVec3.Invalid;
        }
    }
}
