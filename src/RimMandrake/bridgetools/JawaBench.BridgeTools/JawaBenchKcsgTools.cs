// JawaBenchKcsgTools.cs - KCSG structure/settlement/tiled/symbol placement, and
// Vanilla Gravship Expanded's skyfaller-delivery variant of the same. This closes a
// gap explicitly DEFERRED earlier this session as "outside scope, no vendored
// source" - wrong: KCSG ships bundled INSIDE VanillaExpandedFramework-main, which
// IS vendored (vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/).
// Found via the owner's own live debug-menu screenshots naming "KCSG" as its own
// category - the fourth distinct search axis this session (after the hand-curated
// roster, the Find.X sweep, and the vanilla [DebugAction] sweep).
//
// EVERYTHING HERE IS REFLECTION, ON PURPOSE, same rule as JawaBenchVehicleTools.cs:
// the companion has to load on an install where VEF/KCSG is absent, and KCSG's
// types (StructureLayoutDef, SymbolDef, SettlementLayoutDef, TiledStructureDef, and
// the static utility classes below) live in VEF's own assembly, never referenced by
// this project. A reflection lookup that misses returns null rather than throwing,
// so every handle is checked and a miss REFUSES by name.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF THE VENDORED SOURCE, NOT GUESSED - and two
// of the four needed a second file each because the debug action's own one-liner
// call turned out to be an EXTENSION METHOD living in a different static class than
// the Def itself:
//   KCSG/Defs/StructureLayoutDef.cs   the Def itself carries no Generate() method
//   KCSG/Utils/LayoutUtils.cs         Generate(this StructureLayoutDef, CellRect,
//                                     Map, Faction=null, bool=false) - the ACTUAL
//                                     method; CleanRect(StructureLayoutDef, Map,
//                                     CellRect, bool) - NOT an extension, called
//                                     first in every debug action that places one
//   KCSG/Utils/GenOption.cs           GetAllMineableIn(CellRect, Map) - registers
//                                     mineable resources under the footprint before
//                                     Generate runs; every KCSG debug action calls
//                                     this FIRST, before CleanRect (which reads the
//                                     dictionary this call primes) and Generate
//   KCSG/Utils/SymbolUtils.cs         Generate(this SymbolDef, StructureLayoutDef,
//                                     Map, IntVec3, Faction, ThingDef) - SymbolDef
//                                     itself has no Generate() either
//   KCSG/Utils/SettlementGenUtils.cs  Generate(ResolveParams, Map, SettlementLayoutDef)
//                                     - ResolveParams is a VANILLA type
//                                     (RimWorld.BaseGen), no reflection needed for it
//   KCSG/Utils/TileUtils.cs           Generate(this TiledStructureDef, IntVec3, Map,
//                                     Quest=null)
//   VanillaGravshipExpanded/Source/DebugActions.cs   SpawnGravship(LocalTargetInfo,
//                                     StructureLayoutDef): ThingMaker.MakeThing
//                                     (VGE_LandingStructure) -> set its public
//                                     'layoutDef' field -> GenSpawn.Spawn. The
//                                     landing structure itself handles turning into
//                                     the actual KCSG layout on arrival - this tool
//                                     only needs to set one field and spawn.
//
// 🔴 ALL FOUR StructureLayoutDef/SymbolDef/SettlementLayoutDef/TiledStructureDef
// CLASSES DERIVE FROM Verse.Def - confirmed in source - so once resolved by
// reflection, they can be cast to the vanilla `Def` type directly for defName/
// label reads. Only the KCSG-specific members (Generate, CleanRect, sizes, ...)
// need continued reflection.
//
// GATING: none of these are gated - same tier as jawa/run_basegen_symbol and
// jawa/build_batch: map-authoring, not an incident fired at the colony. HIGH RISK
// is said plainly in each tool's own Description, matching that precedent, rather
// than gated for it.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.BaseGen;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags KcsgStatic = BindingFlags.Public | BindingFlags.Static;
        private const BindingFlags KcsgInst = BindingFlags.Public | BindingFlags.Instance;

        private static Type KcsgType(string shortName) => GenTypes.GetTypeInAnyAssembly("KCSG." + shortName);

        /// <summary>DefDatabase&lt;T&gt;.AllDefsListForReading for a runtime-resolved KCSG def Type.</summary>
        private static IEnumerable KcsgAllDefs(Type defType)
        {
            if (defType == null) return null;
            var dbType = typeof(DefDatabase<>).MakeGenericType(defType);
            var prop = dbType.GetProperty("AllDefsListForReading", KcsgStatic);
            return prop?.GetValue(null) as IEnumerable;
        }

        /// <summary>DefDatabase&lt;T&gt;.GetNamedSilentFail(name) for a runtime-resolved KCSG def Type, cast to the vanilla Def base.</summary>
        private static Def KcsgGetNamed(Type defType, string defName)
        {
            if (defType == null) return null;
            var dbType = typeof(DefDatabase<>).MakeGenericType(defType);
            var method = dbType.GetMethod("GetNamedSilentFail", KcsgStatic, null, new[] { typeof(string) }, null);
            return method?.Invoke(null, new object[] { defName }) as Def;
        }

        [Tool(
            "jawa/kcsg_place",
            Description =
                "*** HIGH RISK, IRREVERSIBLE *** Place a KCSG-authored structure, settlement, " +
                "tiled complex or single symbol onto the LIVE map - the exact call sequence " +
                "KCSG's own debug menu uses (CleanRect -> GetAllMineableIn -> Generate for " +
                "structures; ResolveParams+SettlementGenUtils.Generate for settlements; " +
                "SymbolUtils.Generate for one symbol; TileUtils.Generate for a tiled complex). " +
                "layoutType='structure': places a named StructureLayoutDef centred on 'rect'. " +
                "The rect actually used is always the layout's OWN size (KCSG cannot render " +
                "into any other), so 'at' may differ from what you asked for - 'requested' " +
                "reports the rect you gave. " +
                "layoutType='settlement': fills 'rect' with a named SettlementLayoutDef (full " +
                "base: buildings + defenses + stockpile, per that def's own options). " +
                "layoutType='tiled': places a TiledStructureDef centered on 'point'. " +
                "layoutType='symbol': places ONE SymbolDef at 'point' (building, item, pawn " +
                "spawner, whatever that symbol resolves to). Refuses by name if KCSG is not " +
                "loaded (VanillaExpandedFramework's core mod) rather than a null-reference.",
            ResultDescription = "success, layoutType, defName, at (rect or point), and for " +
                "layoutType='structure' also requested (the rect you asked for). On any " +
                "refusal or a throw inside KCSG: success=false plus a message naming it.")]
        public static async Task<object> KcsgPlace(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'structure', 'settlement', 'tiled' or 'symbol'. Required.")]
            string layoutType = null,
            [ToolParameter(Description = "KCSG def defName (StructureLayoutDef/SettlementLayoutDef/TiledStructureDef/SymbolDef, matching layoutType). Required.")]
            string defName = null,
            [ToolParameter(Description = "structure/settlement: rect 'x,z,w,h'.")]
            string rect = null,
            [ToolParameter(Description = "tiled/symbol: cell 'x,z'.")]
            string point = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrWhiteSpace(defName)) return Fail("Give 'defName'.");

                string lt = (layoutType ?? "").Trim().ToLowerInvariant();

                if (lt == "structure")
                {
                    var defType = KcsgType("StructureLayoutDef");
                    if (defType == null) return Fail("KCSG is not loaded (KCSG.StructureLayoutDef not found in any assembly).");
                    var layoutDef = KcsgGetNamed(defType, defName.Trim());
                    if (layoutDef == null) return Fail("No KCSG.StructureLayoutDef '" + defName + "'.",
                        new { candidates = KcsgAllDefs(defType)?.Cast<Def>().Select(d => d.defName).Take(60).ToList() });

                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);

                    // 🔴 The rect MUST be the layout's own size. KCSG's debug action never
                    // passes an arbitrary one - it builds CellRect.CenteredOn(cell, sizes.x,
                    // sizes.z) - and neither call below tolerates any other size:
                    //   CleanRect indexes layout._roofGrid[srcCoords.z, srcCoords.x] with x/z
                    //   walked over the RECT's width/height, so a rect BIGGER than the layout
                    //   throws IndexOutOfRange part-way through cleaning (things already
                    //   destroyed, roof grid half-updated);
                    //   Generate centres the layout with offset = (rect.Width - sizes.x) / 2,
                    //   so a rect SMALLER than the layout goes negative and draws the structure
                    //   outside the cells CleanRect just prepared.
                    // TryRect also ClipInsideMap()s, which silently shrinks a rect near the map
                    // edge into exactly that second case. Re-size from the layout, centred on
                    // what the caller asked for, and report the rect actually used.
                    var requested = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height };
                    var sizesProp = defType.GetProperty("Sizes", KcsgInst);
                    if (sizesProp != null && sizesProp.GetValue(layoutDef) is IntVec2 sizes
                        && sizes.x > 0 && sizes.z > 0)
                        r = CellRect.CenteredOn(r.CenterCell, sizes.x, sizes.z);

                    var layoutUtils = KcsgType("LayoutUtils");
                    var genOption = KcsgType("GenOption");
                    if (layoutUtils == null || genOption == null) return Fail("KCSG.LayoutUtils/GenOption not found.");

                    var cleanRect = layoutUtils.GetMethod("CleanRect", KcsgStatic, null, new[] { defType, typeof(Map), typeof(CellRect), typeof(bool) }, null);
                    var getMineable = genOption.GetMethod("GetAllMineableIn", KcsgStatic, null, new[] { typeof(CellRect), typeof(Map) }, null);
                    // 🔴 BRIDGE_KCSG_VGE_TOOLS_1: the real Generate() declares 5/6/7 params
                    // (Faction/bool/Rot4? are optional args, which do NOT show up as a separate
                    // overload via reflection - GetMethod needs the actual declared arity).
                    // This is the 5-param overload: Generate(StructureLayoutDef, CellRect, Map,
                    // Faction=null, bool=false) - the one KCSG's own debug action calls via
                    // layoutDef.Generate(cellRect, map).
                    var generate = layoutUtils.GetMethod("Generate", KcsgStatic, null,
                        new[] { defType, typeof(CellRect), typeof(Map), typeof(Faction), typeof(bool) }, null);
                    if (cleanRect == null || getMineable == null || generate == null)
                        return Fail("KCSG.LayoutUtils/GenOption method shapes did not match - names may have changed since vendoring.");

                    try
                    {
                        // 🔴 Call order matters: KCSG's own debug action (Utils/DebugActions.cs)
                        // runs GetAllMineableIn -> CleanRect -> Generate. CleanRect reads the
                        // mineables dictionary GetAllMineableIn primes, so it must run first.
                        getMineable.Invoke(null, new object[] { r, map });
                        cleanRect.Invoke(null, new object[] { layoutDef, map, r, true });
                        generate.Invoke(null, new object[] { layoutDef, r, map, null, false });
                    }
                    catch (Exception e) { return Fail("KCSG generation threw " + e.GetType().Name + ": " + (e.InnerException?.Message ?? e.Message)); }

                    return new { success = true, layoutType = "structure", defName = layoutDef.defName, at = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height }, requested, ticksGame = TicksGameSafe() };
                }

                if (lt == "settlement")
                {
                    var defType = KcsgType("SettlementLayoutDef");
                    if (defType == null) return Fail("KCSG is not loaded (KCSG.SettlementLayoutDef not found).");
                    var sld = KcsgGetNamed(defType, defName.Trim());
                    if (sld == null) return Fail("No KCSG.SettlementLayoutDef '" + defName + "'.",
                        new { candidates = KcsgAllDefs(defType)?.Cast<Def>().Select(d => d.defName).Take(60).ToList() });

                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);

                    var settlementGenUtils = KcsgType("SettlementGenUtils");
                    var genOption = KcsgType("GenOption");
                    if (settlementGenUtils == null || genOption == null) return Fail("KCSG.SettlementGenUtils/GenOption not found.");
                    var generate = settlementGenUtils.GetMethod("Generate", KcsgStatic, null, new[] { typeof(ResolveParams), typeof(Map), defType }, null);
                    var getMineable = genOption.GetMethod("GetAllMineableIn", KcsgStatic, null, new[] { typeof(CellRect), typeof(Map) }, null);
                    var settlementLayoutField = genOption.GetField("settlementLayout", KcsgStatic);
                    if (generate == null || getMineable == null || settlementLayoutField == null)
                        return Fail("KCSG.SettlementGenUtils/GenOption method/field shapes did not match.");

                    // 🔴 BRIDGE_KCSG_VGE_TOOLS_1: SettlementGenUtils.Generate reads
                    // GenOption.RoadOptions (=> settlementLayout.roadOptions, NO null guard) and,
                    // when avoidMountains is set, GenOption.GetMineableAt - both unprimed statics
                    // KCSG's own debug action sets first (Utils/DebugActions.cs Quickspawn):
                    // BaseGen.globalSettings.map, GenOption.settlementLayout, GetAllMineableIn.
                    BaseGen.globalSettings.map = map;
                    var rp = new ResolveParams { faction = map.ParentFaction, rect = r };
                    try
                    {
                        settlementLayoutField.SetValue(null, sld);
                        getMineable.Invoke(null, new object[] { r, map });
                        generate.Invoke(null, new object[] { rp, map, sld });
                    }
                    catch (Exception e) { return Fail("SettlementGenUtils.Generate threw " + e.GetType().Name + ": " + (e.InnerException?.Message ?? e.Message)); }

                    return new { success = true, layoutType = "settlement", defName = sld.defName, at = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height }, ticksGame = TicksGameSafe() };
                }

                if (lt == "tiled")
                {
                    var defType = KcsgType("TiledStructureDef");
                    if (defType == null) return Fail("KCSG is not loaded (KCSG.TiledStructureDef not found).");
                    var td = KcsgGetNamed(defType, defName.Trim());
                    if (td == null) return Fail("No KCSG.TiledStructureDef '" + defName + "'.",
                        new { candidates = KcsgAllDefs(defType)?.Cast<Def>().Select(d => d.defName).Take(60).ToList() });

                    if (!TryParseCellLocal(point, out var cell, out err)) return Fail(err);
                    if (!cell.InBounds(map)) return Fail("Point " + cell + " is outside the map.");

                    var tileUtils = KcsgType("TileUtils");
                    if (tileUtils == null) return Fail("KCSG.TileUtils not found.");
                    var generate = tileUtils.GetMethod("Generate", KcsgStatic, null, new[] { defType, typeof(IntVec3), typeof(Map), typeof(Quest) }, null);
                    if (generate == null) return Fail("KCSG.TileUtils.Generate method shape did not match.");

                    try { generate.Invoke(null, new object[] { td, cell, map, null }); }
                    catch (Exception e) { return Fail("TileUtils.Generate threw " + e.GetType().Name + ": " + (e.InnerException?.Message ?? e.Message)); }

                    return new { success = true, layoutType = "tiled", defName = td.defName, at = new { x = cell.x, z = cell.z }, ticksGame = TicksGameSafe() };
                }

                if (lt == "symbol")
                {
                    var defType = KcsgType("SymbolDef");
                    if (defType == null) return Fail("KCSG is not loaded (KCSG.SymbolDef not found).");
                    var sym = KcsgGetNamed(defType, defName.Trim());
                    if (sym == null) return Fail("No KCSG.SymbolDef '" + defName + "'.",
                        new { candidates = KcsgAllDefs(defType)?.Cast<Def>().Select(d => d.defName).Take(60).ToList() });

                    if (!TryParseCellLocal(point, out var cell, out err)) return Fail(err);
                    if (!cell.InBounds(map)) return Fail("Point " + cell + " is outside the map.");

                    var structureLayoutType = KcsgType("StructureLayoutDef");
                    var symbolUtils = KcsgType("SymbolUtils");
                    var genOption = KcsgType("GenOption");
                    if (symbolUtils == null || structureLayoutType == null || genOption == null)
                        return Fail("KCSG.SymbolUtils/StructureLayoutDef/GenOption not found.");
                    var generate = symbolUtils.GetMethod("Generate", KcsgStatic, null,
                        new[] { defType, structureLayoutType, typeof(Map), typeof(IntVec3), typeof(Faction), typeof(ThingDef) }, null);
                    var getMineable = genOption.GetMethod("GetAllMineableIn", KcsgStatic, null, new[] { typeof(CellRect), typeof(Map) }, null);
                    if (generate == null || getMineable == null)
                        return Fail("KCSG.SymbolUtils.Generate/GenOption.GetAllMineableIn method shape did not match.");

                    // 🔴 BRIDGE_KCSG_VGE_TOOLS_1: SymbolUtils.Generate reaches
                    // GenOption.GetMineableAt(cell), which NREs unconditionally (no null guard)
                    // unless GetAllMineableIn primed the backing dictionary first - every real
                    // KCSG entry point does this before generating.
                    try
                    {
                        getMineable.Invoke(null, new object[] { CellRect.SingleCell(cell), map });
                        generate.Invoke(null, new object[] { sym, null, map, cell, map.ParentFaction, null });
                    }
                    catch (Exception e) { return Fail("SymbolUtils.Generate threw " + e.GetType().Name + ": " + (e.InnerException?.Message ?? e.Message)); }

                    return new { success = true, layoutType = "symbol", defName = sym.defName, at = new { x = cell.x, z = cell.z }, ticksGame = TicksGameSafe() };
                }

                return Fail("layoutType must be 'structure', 'settlement', 'tiled' or 'symbol'.");
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/vge_spawn_structure_skyfaller",
            Description =
                "Vanilla Gravship Expanded's own delivery mode for a KCSG structure - drops it " +
                "in as a landing skyfaller rather than instant-placing it: ThingMaker.MakeThing" +
                "(VGE_LandingStructure), set its 'layoutDef' field to the named " +
                "KCSG.StructureLayoutDef (reflection - LandingStructure is VGE's own type), " +
                "GenSpawn.Spawn at the cell. The landing structure itself resolves into the " +
                "actual KCSG layout on arrival - this tool only sets one field and spawns.",
            ResultDescription = "success, defName, at, thingId (the spawned LandingStructure).")]
        public static async Task<object> VgeSpawnStructureSkyfaller(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "KCSG.StructureLayoutDef defName. Required.")]
            string defName = null,
            [ToolParameter(Description = "Landing cell 'x,z'. Required.")]
            string point = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrWhiteSpace(defName)) return Fail("Give 'defName'.");
                if (!TryParseCellLocal(point, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Point " + cell + " is outside the map.");

                var structureLayoutType = KcsgType("StructureLayoutDef");
                if (structureLayoutType == null) return Fail("KCSG is not loaded (KCSG.StructureLayoutDef not found).");
                var layoutDef = KcsgGetNamed(structureLayoutType, defName.Trim());
                if (layoutDef == null) return Fail("No KCSG.StructureLayoutDef '" + defName + "'.",
                    new { candidates = KcsgAllDefs(structureLayoutType)?.Cast<Def>().Select(d => d.defName).Take(60).ToList() });

                var landingDef = DefDatabase<ThingDef>.GetNamedSilentFail("VGE_LandingStructure");
                if (landingDef == null) return Fail("No ThingDef 'VGE_LandingStructure' - Vanilla Gravship Expanded is not loaded.");

                Thing thing;
                try { thing = ThingMaker.MakeThing(landingDef); }
                catch (Exception e) { return Fail("MakeThing threw " + e.GetType().Name + ": " + e.Message); }

                var layoutField = thing.GetType().GetField("layoutDef", KcsgInst);
                if (layoutField == null) return Fail("'layoutDef' field not found on " + thing.GetType().FullName + " - VGE's LandingStructure shape may have changed.");
                try { layoutField.SetValue(thing, layoutDef); }
                catch (Exception e) { return Fail("Setting layoutDef threw " + e.GetType().Name + ": " + e.Message); }

                try { GenSpawn.Spawn(thing, cell, map, Rot4.North); }
                catch (Exception e) { return Fail("GenSpawn.Spawn threw " + e.GetType().Name + ": " + e.Message); }

                return new { success = true, defName = layoutDef.defName, at = new { x = cell.x, z = cell.z }, thingId = thing.ThingID, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Research Reinvented - reset progress for testing
        // ================================================================

        [Tool(
            "jawa/research_reinvented_reset",
            Description =
                "Reset ALL research progress to zero - Find.ResearchManager.ResetAllProgress(). " +
                "Vanilla method (Research Reinvented's own debug action calls this exact one, " +
                "no mod-specific logic beyond that), useful when Research Reinvented's " +
                "alternates/opportunities system is active and a clean research-state retest is " +
                "needed. Irreversible for the current save - no confirmation beyond this " +
                "description.",
            ResultDescription = "success, projectsResetCount.")]
        public static async Task<object> ResearchReinventedReset(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.ResearchManager == null) return Fail("No active ResearchManager - is a game loaded?");

                int count = DefDatabase<ResearchProjectDef>.AllDefsListForReading.Count;
                try { Find.ResearchManager.ResetAllProgress(); }
                catch (Exception e) { return Fail("ResetAllProgress threw " + e.GetType().Name + ": " + e.Message); }

                return new { success = true, projectsResetCount = count, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }
    }
}
