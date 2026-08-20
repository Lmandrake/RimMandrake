// JawaBenchWorldTools.cs - the WORLD half of the companion.
//
// WHY THIS FILE EXISTS SEPARATELY
// ===============================
// JawaBenchTerrainTools.cs is 6,199 lines and its world tools were already
// scattered across three non-adjacent regions of it. The worldmap expansion
// (owner, 2026-08-19) adds ~20 more, so the class became `partial` and every
// new world tool lives here. The .csproj is SDK-style with no explicit
// <Compile> items, so this file is picked up by default globbing.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF THE 1.6 SOURCE, NOT REMEMBERED.
// The element census and the reasoning are in
//   design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md
//
// FOUR FACTS THAT SHAPE EVERYTHING HERE
// =====================================
//  1. Tile storage is per-LAYER. WorldGrid delegates to PlanetLayer; the
//     PlanetLayer.Tiles list is the real store. WorldGrid[int] is the SURFACE
//     indexer and returns SurfaceTile. TilesCount is surface-only.
//  2. There is no per-tile visual invalidation except pollution. Everything
//     else needs a whole WorldDrawLayer mesh regeneration - which is why
//     committing is its own tool and not folded into each writer.
//  3. Tile's own private caches (hillinessLabelCached, cachedMaxTemp,
//     cachedMinTemp, tmpHasSecondaryBiome/tmpSecondaryBiome) are NEVER
//     invalidated by anything in the codebase. Read RAW FIELDS when validating.
//  4. SurfaceTile.Roads/Rivers are biome-FILTERED views of
//     potentialRoads/potentialRivers. Validate against the potential* lists.
//
// THREAD AFFINITY, same rule as the terrain half: every line that touches game
// state is inside ctx.MainThread.InvokeAsync and nothing else is.

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
        // ================================================================
        //  jawa/world_layers - W2 scaffold tool.
        //  Deliberately the simplest possible world read: it proves the
        //  partial-class split, the build, the deploy and the load path all
        //  work end to end before any writer is built on top of them.
        // ================================================================
        [Tool(
            "jawa/world_layers",
            Description =
                "Enumerate the planet's layers (1.6 reworked the planet into PlanetLayers: " +
                "Surface, Orbit, Orbit2). Reports each layer's id, def, tile count, radius, " +
                "view angle, subdivisions and whether it is the root surface. Use this to " +
                "confirm which world is loaded before writing to it - in particular that the " +
                "surface tile count is what an import expects (21872 on a My Little Planet " +
                "subcount-7 world). Read-only.",
            ResultDescription =
                "success, tilesCount (surface), layerCount, and a layers[] array of " +
                "{ layerId, def, label, tilesCount, isRootSurface, radius, viewAngle, " +
                "subdivisions, isSpace }.")]
        public static async Task<object> WorldLayers(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded. Generate or load a world first.");

                var grid = Find.WorldGrid;
                var layers = new List<object>();

                foreach (var kv in grid.PlanetLayers.OrderBy(k => k.Key))
                {
                    var layer = kv.Value;
                    if (layer == null) continue;

                    int count;
                    try { count = layer.TilesCount; }
                    catch (Exception e) { count = -1; Log.Warning("[JawaBench] world_layers: TilesCount threw on layer " + kv.Key + ": " + e.Message); }

                    layers.Add(new
                    {
                        layerId = kv.Key,
                        def = layer.Def != null ? layer.Def.defName : null,
                        label = layer.Def != null ? layer.Def.label : null,
                        tilesCount = count,
                        isRootSurface = layer.IsRootSurface,
                        radius = layer.Radius,
                        viewAngle = layer.ViewAngle,
                        averageTileSize = layer.AverageTileSize,
                        isSpace = layer.Def != null && layer.Def.isSpace,
                        scenarioTag = layer.ScenarioTag,
                    });
                }

                return (object)new
                {
                    success = true,
                    tilesCount = grid.TilesCount,          // surface only, by design
                    layerCount = layers.Count,
                    hasWorldData = grid.HasWorldData,
                    seed = Find.World.info != null ? Find.World.info.seedString : null,
                    planetCoverage = Find.World.info != null ? Find.World.info.planetCoverage : -1f,
                    worldName = Find.World.info != null ? Find.World.info.name : null,
                    layers,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
