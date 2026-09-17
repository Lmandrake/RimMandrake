// JawaBenchFlowWorksTools.cs - the FlowWorks (was FluidCanals) bridge
// verification surface, bypassing the debug-action tree entirely.
//
// WHY: RimMandrakeFlowWorks ships [DebugAction]s (category RMFlowWorks) that
// never appear in the live debug-action tree (FLUID_CANAL_DEBUG_SURFACE_1 -
// cause still unnamed; load order and the PlayingOnMap visibility gate are
// both experimentally ruled out, and no ReflectionTypeLoadException appears in
// any session log). Two live sessions died on it. TypeProbe is the reflection
// instrument that item's round 2 named as the next step - one call that says
// WHERE the registration pipeline loses the type.
//
// 🔴 RULING 24 (owner, 2026-09-16) DELETED CompFluidReservoir AND
// RM_FluidSpring_Test. A source is not a building: it is a SUPERDEEP cell at
// F = D. Everything this file used to read off a reservoir is gone, and
// `jawa/canal_dig` - whose entire job was to call
// CompFluidReservoir.Notify_CanalCellOpened - is a STUB that fails loudly
// rather than a tool that quietly does half of what its name says. Its
// replacement rides FLOWWORKS_BUILD_PROGRAM_1 Phase 9, against
// RM_MapComponent_Excavation (the new core, commit ff82ad396).
//
// COUPLING: strictly by reflection. The companion must load and register on a
// mod list WITHOUT FlowWorks; a hard assembly reference would make that mod's
// presence a load-time precondition for the whole bridge surface. Every resolve
// failure is a loud Fail naming exactly what was missing.
//
// EVERY SIGNATURE READ FROM src/RimMandrake/FlowWorks/Source, not guessed:
//   Flood_FlowWorks.FloodedTileCount / RemainingVolume / ExpiresAtTick
//   TerrainDef RM_Channel_Empty via DefDatabase, no assembly needed.
//
// THREAD AFFINITY: CanalCellReport touches the map and lives inside
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
        private const string FluidFloodTypeName = "RimMandrake.FlowWorks.Flood_FlowWorks";

        [Tool(
            "jawa/canal_dig",
            Description =
                "REMOVED BY RULING 24 (owner, 2026-09-16) - this tool always fails and " +
                "does nothing. It existed to call CompFluidReservoir.Notify_CanalCellOpened " +
                "after setting a cell to RM_Channel_Empty, priming an RM_FluidSpring_Test " +
                "building next to it. Both the comp and the building are DELETED: a source " +
                "is not a building, it is a SUPERDEEP cell at F = D. The replacement digs " +
                "through RM_MapComponent_Excavation's depth grid and is owed by " +
                "FLOWWORKS_BUILD_PROGRAM_1 Phase 9. Kept as a loud stub rather than deleted " +
                "so a caller gets the reason instead of 'no such tool'.",
            ResultDescription =
                "Always success=false with an error naming ruling 24. Never mutates the map.")]
        public static Task<object> CanalDig(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X. Ignored - this tool does nothing.")]
            int x,
            [ToolParameter(Description = "Map cell Z. Ignored - this tool does nothing.")]
            int z)
        {
            return Task.FromResult(Fail(
                "jawa/canal_dig was removed by owner ruling 24 (2026-09-16): " +
                "CompFluidReservoir and RM_FluidSpring_Test no longer exist, so there is " +
                "nothing to prime. Nothing was changed on the map. A depth-grid dig tool " +
                "against RM_MapComponent_Excavation is owed by FLOWWORKS_BUILD_PROGRAM_1 " +
                "Phase 9."));
        }

        [Tool(
            "jawa/canal_cell_report",
            Description =
                "RAW per-cell FlowWorks report on the CURRENT map - the bridge port of " +
                "RimMandrakeFlowWorks' 'Report cell (RAW)' debug action, which never " +
                "registers live (FLUID_CANAL_DEBUG_SURFACE_1). Reads the raw fields a " +
                "convenient getter would launder: terrain (GetTerrain - returns the " +
                "TEMPORARY layer first when a flood covers the cell), tempTerrain " +
                "(TempTerrainAt - null means no temporary overlay), underneath " +
                "(TopTerrainAt - what comes back when the flood drains; on a flooded " +
                "concrete cell 'underneath=Concrete' is the whole recoverability proof), " +
                "plus flood state per Thing (floodedTileCount, remainingVolume, " +
                "expiresAtTick vs nowTick). The reservoir block is GONE - ruling 24 " +
                "deleted CompFluidReservoir. Works with or without the FlowWorks mod " +
                "loaded - the mod-specific blocks just come back absent.",
            ResultDescription =
                "success, cell, terrain, isWater, tempTerrain ('none' when no overlay), " +
                "underneath, things[] of {def, id, " +
                "flood?{spawned,floodedTileCount,remainingVolume,expiresAtTick}}, " +
                "flowWorksLoaded, mapId, mapTile, ticksGame.")]
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

                Type floodType = GenTypes.GetTypeInAnyAssembly(FluidFloodTypeName);

                var things = new List<object>();
                List<Thing> here = c.GetThingList(map);
                for (int i = 0; i < here.Count; i++)
                {
                    Thing t = here[i];
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
                    things.Add(new { def = t.def.defName, id = t.ThingID, flood });
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
                    flowWorksLoaded = floodType != null,
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
                "RimMandrake.FlowWorks.FlowWorksDebugActions.")]
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
