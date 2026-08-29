// JawaBenchGenTools2.cs - four map-generation primitives from
// BRIDGE_CAPABILITY_ROSTER.md §1 that were never exposed: a live map could not
// run a GenStep, force one scatterer, push a BaseGen symbol, or clean up a roof
// left floating by demolition.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/GenStep.cs                 abstract Generate(Map, GenStepParams)
//   Verse/GenStep_Scatterer.cs       ForceScatterAt(IntVec3, Map) - public
//   RimWorld/BaseGen/BaseGen.cs      globalSettings.map, symbolStack, Generate()
//   RimWorld/BaseGen/SymbolStack.cs  Push(string symbol, CellRect rect, ...)
//   RimWorld/BaseGen/GlobalSettings.cs   map - a plain public field
//   Verse/RoofCollapseCellsFinder.cs CheckAndRemoveCollpsingRoofs(Map) - the
//                                    misspelling ("Collpsing") is the real name
//
// 🔴 TWO TRAPS THE SOURCE CONFIRMED:
//   * BaseGen.Generate() is a GLOBAL static pipeline, not reentrant
//     ("Cannot call Generate() while already generating" - Log.Error and a
//     silent no-op, not an exception). It ALSO clears symbolStack and
//     globalSettings in a finally block when done, so a caller cannot inspect
//     state mid-run - this tool reports what it pushed, not what BaseGen did
//     internally.
//   * GenStep instances are found by name via GenTypes.GetTypeInAnyAssembly and
//     built with Activator.CreateInstance(type) - a GenStep with required
//     constructor arguments (rare, but real for modded steps) throws there, not
//     inside Generate(). The refusal names the type and the exception.
//
// GATING: none of these four are gated. They are map-generation and roof-repair
// primitives - the same tier as jawa/prefab_place, jawa/build_batch and
// jawa/designate_batch, all ungated - not incidents fired at the colony. ⚠️
// run_basegen_symbol and run_genstep are marked **high** risk in the roster
// (irreversible, can place ANYTHING a RuleDef or GenStep author wrote,
// including a populated settlement) and say so loudly in their own
// Description, same as jawa/build_batch's own wipeExisting warns inline rather
// than being gated for it.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
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
        [Tool(
            "jawa/scatter_at",
            Description =
                "Force ONE GenStep_Scatterer subclass to scatter at a specific cell - " +
                "GenStep_Scatterer.ForceScatterAt(loc, map), the engine's own debug-tool " +
                "route (bypasses the scatterer's own count/spacing/positioning logic, which " +
                "normally spreads N instances across a whole map). Give the GenStepDef's " +
                "defName; its 'genStepClass' must derive from GenStep_Scatterer or this " +
                "refuses by name rather than silently doing nothing.",
            ResultDescription = "success, genStepDef, at, threw (the scatterer's own exception message, if any).")]
        public static async Task<object> ScatterAt(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "GenStepDef defName whose genStepClass derives from GenStep_Scatterer. Required.")]
            string genStepDef = null,
            [ToolParameter(Description = "Cell 'x,z'. Required.")]
            string at = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                if (string.IsNullOrWhiteSpace(genStepDef)) return Fail("Give 'genStepDef'.");
                var gsd = DefDatabase<GenStepDef>.GetNamedSilentFail(genStepDef.Trim());
                if (gsd == null) return Fail("No GenStepDef '" + genStepDef + "'.", DefSuggestions<GenStepDef>(genStepDef));
                var instance = gsd.genStep as GenStep_Scatterer;
                if (instance == null)
                    return Fail("'" + genStepDef + "'.genStep is " +
                                (gsd.genStep != null ? gsd.genStep.GetType().FullName : "null") +
                                ", not a GenStep_Scatterer. This tool only forces a scatterer.");

                if (!TryParseCellLocal(at, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Cell " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");

                string threw = null;
                try { instance.ForceScatterAt(cell, map); }
                catch (Exception e) { threw = e.GetType().Name + ": " + e.Message; }

                return new
                {
                    success = threw == null,
                    genStepDef = gsd.defName,
                    at = new { x = cell.x, z = cell.z },
                    threw,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/run_genstep",
            Description =
                "*** HIGH RISK, IRREVERSIBLE *** Run any GenStepDef's already-constructed genStep " +
                "instance on the LIVE map - GenStepDef.genStep.Generate(map, default(GenStepParams)). " +
                "A GenStep can place ANYTHING its author wrote - terrain, buildings, pawns, an " +
                "entire settlement - and most GenStep_* implementations read " +
                "MapGenerator.Elevation/Fertility/Caves/PlayerStartSpot, which are null/invalid " +
                "OUTSIDE generation; expect nulls or silent no-ops from those rather than a " +
                "crash. This is a raw primitive with no undo - know what the step does before " +
                "calling it.",
            ResultDescription = "success, genStepDef, genStepType, threw (the step's own exception message, if any).")]
        public static async Task<object> RunGenStep(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "GenStepDef defName. Required.")]
            string genStepDef = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                if (string.IsNullOrWhiteSpace(genStepDef)) return Fail("Give 'genStepDef'.");
                var gsd = DefDatabase<GenStepDef>.GetNamedSilentFail(genStepDef.Trim());
                if (gsd == null) return Fail("No GenStepDef '" + genStepDef + "'.", DefSuggestions<GenStepDef>(genStepDef));
                if (gsd.genStep == null) return Fail("'" + genStepDef + "' has no genStep instance.");

                string threw = null;
                try { gsd.genStep.Generate(map, default(GenStepParams)); }
                catch (Exception e) { threw = e.GetType().Name + ": " + e.Message; }

                return new
                {
                    success = threw == null,
                    genStepDef = gsd.defName,
                    genStepType = gsd.genStep.GetType().FullName,
                    threw,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/run_basegen_symbol",
            Description =
                "*** HIGH RISK, IRREVERSIBLE - CAN SPAWN A FULL POPULATED SETTLEMENT *** " +
                "Push one BaseGen symbol at a rect and resolve it on the LIVE map - " +
                "BaseGen.globalSettings.map = map; BaseGen.symbolStack.Push(symbol, rect); " +
                "BaseGen.Generate(). 'settlement' with SymbolResolver_Settlement is the " +
                "canonical example: buildings + inhabitants + a LordJob_DefendBase, ~1150-1600 " +
                "points, mutates terrain and buildings under the whole rect. BaseGen is a " +
                "GLOBAL, NON-REENTRANT pipeline - it clears its own state when done, so this " +
                "tool reports what it PUSHED, not an internal trace of what resolved. A symbol " +
                "with no matching RuleDef resolver logs a Warning and does nothing, silently - " +
                "not a failure this tool can detect from outside BaseGen's own log.",
            ResultDescription = "success, symbol, rect, note (the silent-no-resolver caveat, always present).")]
        public static async Task<object> RunBaseGenSymbol(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "BaseGen symbol name, e.g. 'settlement'. Required.")]
            string symbol = null,
            [ToolParameter(Description = "Rect 'x,z,w,h'. Required.")]
            string rect = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrWhiteSpace(symbol)) return Fail("Give 'symbol', e.g. 'settlement'.");

                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                try
                {
                    BaseGen.globalSettings.map = map;
                    BaseGen.symbolStack.Push(symbol.Trim(), r);
                    BaseGen.Generate();
                }
                catch (Exception e)
                {
                    return Fail("BaseGen threw " + e.GetType().Name + ": " + e.Message);
                }

                return new
                {
                    success = true,
                    symbol = symbol.Trim(),
                    rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    note = "A symbol with no matching RuleDef resolver logs a Warning and does " +
                           "nothing; check the def dump's RuleDef roster or Player.log if the " +
                           "map did not change.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/fix_floating_roofs",
            Description =
                "Remove roof left unsupported after demolition or a wall removal - " +
                "RoofCollapseCellsFinder.CheckAndRemoveCollpsingRoofs(map) (the misspelling " +
                "'Collpsing' is the real method name). Scans the WHOLE map, not just an area " +
                "you name - this mirrors the engine's own post-demolition cleanup call.",
            ResultDescription = "success, roofedCellsBefore, roofedCellsAfter, cellsCleared.")]
        public static async Task<object> FixFloatingRoofs(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                int before = map.AllCells.Count(c => c.Roofed(map));
                try { RoofCollapseCellsFinder.CheckAndRemoveCollpsingRoofs(map); }
                catch (Exception e) { return Fail("CheckAndRemoveCollpsingRoofs threw " + e.GetType().Name + ": " + e.Message); }
                int after = map.AllCells.Count(c => c.Roofed(map));

                return new
                {
                    success = true,
                    roofedCellsBefore = before,
                    roofedCellsAfter = after,
                    cellsCleared = before - after,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
