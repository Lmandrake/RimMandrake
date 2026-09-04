// JawaBenchFluidCanalTools.cs - FLUID_CANAL_FLOOD_LIVE_CHECK_1's verification
// surface, bypassing the debug-action tree entirely.
//
// WHY: RimMandrakeFluidCanals ships two [DebugAction]s (category RMFluidCanals:
// "Instant-dig canal at cell" / "Report cell (RAW)") that never appear in the
// live debug-action tree (FLUID_CANAL_DEBUG_SURFACE_1 - cause still unnamed;
// load order and the PlayingOnMap visibility gate are both experimentally ruled
// out, and no ReflectionTypeLoadException appears in any session log). Two live
// sessions died on it. These tools drive the same two effects directly, and
// TypeProbe is the reflection instrument that item's round 2 named as the next
// step - one call that says WHERE the registration pipeline loses the type.
//
// COUPLING: strictly by reflection. The companion must load and register on a
// mod list WITHOUT FluidCanals; a hard assembly reference would make that mod's
// presence a load-time precondition for the whole bridge surface. Every resolve
// failure is a loud Fail naming exactly what was missing.
//
// EVERY SIGNATURE READ FROM src/RimMandrake/FluidCanals/Source, not guessed:
//   CompFluidReservoir.Notify_CanalCellOpened(Map, IntVec3)   public static
//   CompFluidReservoir.Spent (bool), .Props (fluidDef, volume)
//   Flood_FluidCanal.FloodedTileCount / RemainingVolume / ExpiresAtTick
//   TerrainDef RM_Channel_Empty via DefDatabase, no assembly needed.
//
// THREAD AFFINITY: CanalDig and CanalCellReport touch the map and live inside
// ctx.MainThread.InvokeAsync in full. TypeProbe reads only GenTypes /
// LoadedModManager statics and attribute state, the same surface DebugActions
// in this assembly already reads off-thread, but it is cheap (one type) so it
// hops the main thread anyway for consistency of the state flags it reports.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using LudeonTK;
using RimBridgeServer.Sdk;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string FluidCompTypeName = "RimMandrake.FluidCanals.CompFluidReservoir";
        private const string FluidFloodTypeName = "RimMandrake.FluidCanals.Flood_FluidCanal";

        [Tool(
            "jawa/canal_dig",
            Description =
                "Instant-dig a fluid canal cell on the CURRENT map: sets the cell's terrain " +
                "to RM_Channel_Empty and calls CompFluidReservoir.Notify_CanalCellOpened, the " +
                "exact two effects of RimMandrakeFluidCanals' own 'Instant-dig canal at cell' " +
                "debug action - which never registers in the live debug tree " +
                "(FLUID_CANAL_DEBUG_SURFACE_1), hence this tool. Dig ADJACENT to a spring " +
                "(e.g. RM_FluidSpring_Test) to trigger its flood. DOES NOT wait for the flood " +
                "to spread - take readings with canal_cell_report. Refuses loudly when the " +
                "FluidCanals mod is not in the active list. The result names mapId and " +
                "mapTile: with two maps live in one session the bridge's notion of 'current " +
                "map' has surprised before, so check them.",
            ResultDescription =
                "success, cell, terrainBefore, terrainNow (read back from the grid, expect " +
                "RM_Channel_Empty), floodsOnMap (count of Flood_FluidCanal things after the " +
                "notify), mapId, mapTile, ticksGame.")]
        public static async Task<object> CanalDig(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X.")]
            int x,
            [ToolParameter(Description = "Map cell Z (RimWorld's second horizontal axis; not height).")]
            int z)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                IntVec3 c = new IntVec3(x, 0, z);
                if (!c.InBounds(map))
                    return Fail("Cell " + c + " is out of bounds on map " + map.uniqueID
                        + " (size " + map.Size.x + "x" + map.Size.z + ").");

                TerrainDef channel = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Channel_Empty");
                if (channel == null)
                    return Fail("TerrainDef RM_Channel_Empty is not loaded. Is mandrake.rm.fluidcanals in the active mod list?");
                Type compType = GenTypes.GetTypeInAnyAssembly(FluidCompTypeName);
                if (compType == null)
                    return Fail("Type " + FluidCompTypeName + " is not resolvable - defs present but assembly missing?");
                MethodInfo notify = compType.GetMethod("Notify_CanalCellOpened",
                    BindingFlags.Static | BindingFlags.Public);
                if (notify == null)
                    return Fail("Notify_CanalCellOpened not found on " + FluidCompTypeName + " - source drift; re-read the mod source.");

                string before = c.GetTerrain(map)?.defName;
                map.terrainGrid.SetTerrain(c, channel);
                try
                {
                    notify.Invoke(null, new object[] { map, c });
                }
                catch (TargetInvocationException e)
                {
                    // The terrain write above already happened - say so rather than
                    // letting a mod-side throw read as "nothing changed".
                    return Fail("Notify_CanalCellOpened threw: "
                        + (e.InnerException?.GetType().Name ?? "?") + ": "
                        + (e.InnerException?.Message ?? e.Message),
                        new { terrainWasSet = true, terrainNow = c.GetTerrain(map)?.defName });
                }

                Type floodType = GenTypes.GetTypeInAnyAssembly(FluidFloodTypeName);
                int floodsOnMap = 0;
                if (floodType != null)
                {
                    List<Thing> all = map.listerThings.AllThings;
                    for (int i = 0; i < all.Count; i++)
                        if (floodType.IsInstanceOfType(all[i])) floodsOnMap++;
                }

                return (object)new
                {
                    success = true,
                    cell = new { x, z },
                    terrainBefore = before,
                    terrainNow = c.GetTerrain(map)?.defName,
                    floodsOnMap,
                    mapId = map.uniqueID,
                    mapTile = map.Tile.ToString(),
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/canal_cell_report",
            Description =
                "RAW per-cell fluid-canal report on the CURRENT map - the bridge port of " +
                "RimMandrakeFluidCanals' 'Report cell (RAW)' debug action, which never " +
                "registers live (FLUID_CANAL_DEBUG_SURFACE_1). Reads the raw fields a " +
                "convenient getter would launder: terrain (GetTerrain - returns the " +
                "TEMPORARY layer first when a flood covers the cell), tempTerrain " +
                "(TempTerrainAt - null means no temporary overlay), underneath " +
                "(TopTerrainAt - what comes back when the flood drains; on a flooded " +
                "concrete cell 'underneath=Concrete' is the whole recoverability proof), " +
                "plus every Thing on the cell with reservoir state (spent is the one real " +
                "runtime field) and flood state (floodedTileCount, remainingVolume, " +
                "expiresAtTick vs nowTick). Works with or without the FluidCanals mod " +
                "loaded - the mod-specific blocks just come back absent.",
            ResultDescription =
                "success, cell, terrain, isWater, tempTerrain ('none' when no overlay), " +
                "underneath, things[] of {def, id, reservoir?{spent,fluid,volume}, " +
                "flood?{spawned,floodedTileCount,remainingVolume,expiresAtTick}}, " +
                "mapId, mapTile, ticksGame.")]
        public static async Task<object> CanalCellReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X.")]
            int x,
            [ToolParameter(Description = "Map cell Z (RimWorld's second horizontal axis; not height).")]
            int z)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                IntVec3 c = new IntVec3(x, 0, z);
                if (!c.InBounds(map))
                    return Fail("Cell " + c + " is out of bounds on map " + map.uniqueID
                        + " (size " + map.Size.x + "x" + map.Size.z + ").");

                TerrainDef terrain = c.GetTerrain(map);
                TerrainDef temp = map.terrainGrid.TempTerrainAt(c);
                TerrainDef under = map.terrainGrid.TopTerrainAt(c);

                Type compType = GenTypes.GetTypeInAnyAssembly(FluidCompTypeName);
                Type floodType = GenTypes.GetTypeInAnyAssembly(FluidFloodTypeName);
                PropertyInfo spentProp = compType?.GetProperty("Spent");
                PropertyInfo propsProp = compType?.GetProperty("Props");

                var things = new List<object>();
                List<Thing> here = c.GetThingList(map);
                for (int i = 0; i < here.Count; i++)
                {
                    Thing t = here[i];
                    object reservoir = null;
                    if (compType != null && t is ThingWithComps twc)
                    {
                        foreach (ThingComp comp in twc.AllComps)
                        {
                            if (!compType.IsInstanceOfType(comp)) continue;
                            object props = propsProp?.GetValue(comp);
                            Type propsType = props?.GetType();
                            reservoir = new
                            {
                                spent = spentProp?.GetValue(comp),
                                fluid = (propsType?.GetField("fluidDef")?.GetValue(props) as Def)?.defName ?? "NULL",
                                volume = propsType?.GetField("volume")?.GetValue(props)
                            };
                            break;
                        }
                    }
                    object flood = null;
                    if (floodType != null && floodType.IsInstanceOfType(t))
                    {
                        flood = new
                        {
                            spawned = t.Spawned,
                            floodedTileCount = floodType.GetProperty("FloodedTileCount")?.GetValue(t),
                            remainingVolume = floodType.GetProperty("RemainingVolume")?.GetValue(t),
                            expiresAtTick = floodType.GetProperty("ExpiresAtTick")?.GetValue(t)
                        };
                    }
                    things.Add(new { def = t.def.defName, id = t.ThingID, reservoir, flood });
                }

                return (object)new
                {
                    success = true,
                    cell = new { x, z },
                    terrain = terrain?.defName,
                    isWater = terrain != null && terrain.IsWater,
                    tempTerrain = temp?.defName ?? "none",
                    underneath = under?.defName,
                    things,
                    fluidCanalsLoaded = compType != null,
                    mapId = map.uniqueID,
                    mapTile = map.Tile.ToString(),
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/type_probe",
            Description =
                "Read-only reflection probe for ONE named type - built for the silent " +
                "debug-action registration failure class (FLUID_CANAL_DEBUG_SURFACE_1), " +
                "where a mod's [DebugAction]s are absent from the live tree while its defs " +
                "and comps work fine. Says WHERE the pipeline loses the type: resolvable " +
                "via GetTypeInAnyAssembly (the def-loading path, its own cache), present " +
                "in GenTypes.AllTypes (the debug-action scan's ONLY source, a separate " +
                "lazily-rebuilt cache), which running mod's loadedAssemblies carries its " +
                "assembly, how many of that assembly's types made it into AllTypes, and " +
                "each [DebugAction] method on it with whether its game-state gate passes " +
                "RIGHT NOW (plus the raw state flags: programState, worldSelected, " +
                "currentMap). Executes nothing and invokes no yielders.",
            ResultDescription =
                "success, typeName, resolved, assembly, inAllTypesByIdentity, " +
                "allTypesNameMatches, allTypesCount, assemblyTypesInAllTypes, " +
                "carryingMods[], debugActions[] of {method, name, category, actionType, " +
                "allowedGameStates, isAllowedNow}, state{programState, worldSelected, " +
                "hasCurrentMap}, ticksGame.")]
        public static async Task<object> TypeProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Full type name including namespace, e.g. " +
                "RimMandrake.FluidCanals.FluidCanalsDebugActions.")]
            string typeName)
        {
            if (string.IsNullOrWhiteSpace(typeName))
                return Fail("typeName is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                string name = typeName.Trim();
                Type t = GenTypes.GetTypeInAnyAssembly(name);
                List<Type> allTypes = GenTypes.AllTypes;

                bool inAllTypesByIdentity = t != null && allTypes.Contains(t);
                int nameMatches = 0;
                for (int i = 0; i < allTypes.Count; i++)
                    if (allTypes[i].FullName == name) nameMatches++;

                int assemblyTypesInAllTypes = -1;
                var carryingMods = new List<string>();
                if (t != null)
                {
                    Assembly asm = t.Assembly;
                    assemblyTypesInAllTypes = 0;
                    for (int i = 0; i < allTypes.Count; i++)
                        if (allTypes[i].Assembly == asm) assemblyTypesInAllTypes++;
                    foreach (ModContentPack mod in LoadedModManager.RunningMods)
                        if (mod.assemblies != null && mod.assemblies.loadedAssemblies != null
                            && mod.assemblies.loadedAssemblies.Contains(asm))
                            carryingMods.Add(mod.PackageId);
                }

                var debugActions = new List<object>();
                if (t != null)
                {
                    MethodInfo[] methods;
                    try { methods = t.GetMethods(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic); }
                    catch (Exception e) { methods = null; debugActions.Add(new { error = "GetMethods threw: " + e.GetType().Name + ": " + e.Message }); }
                    if (methods != null)
                    {
                        foreach (MethodInfo m in methods)
                        {
                            DebugActionAttribute attr = null;
                            string attrError = null;
                            try { attr = m.GetCustomAttribute<DebugActionAttribute>(); }
                            catch (Exception e) { attrError = e.GetType().Name + ": " + e.Message; }
                            if (attr == null && attrError == null) continue;
                            bool isAllowedNow = false;
                            try { isAllowedNow = attr != null && attr.IsAllowedInCurrentGameState; }
                            catch { }
                            debugActions.Add(new
                            {
                                method = m.Name,
                                name = attr?.name,
                                category = attr?.category,
                                actionType = attr?.actionType.ToString(),
                                allowedGameStates = attr?.allowedGameStates.ToString(),
                                isAllowedNow,
                                attributeError = attrError
                            });
                        }
                    }
                }

                return (object)new
                {
                    success = true,
                    typeName = name,
                    resolved = t != null,
                    assembly = t?.Assembly.FullName,
                    inAllTypesByIdentity,
                    allTypesNameMatches = nameMatches,
                    allTypesCount = allTypes.Count,
                    assemblyTypesInAllTypes,
                    carryingMods,
                    debugActions,
                    state = new
                    {
                        programState = Current.ProgramState.ToString(),
                        worldSelected = WorldRendererUtility.WorldSelected,
                        hasCurrentMap = Find.CurrentMap != null
                    },
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
