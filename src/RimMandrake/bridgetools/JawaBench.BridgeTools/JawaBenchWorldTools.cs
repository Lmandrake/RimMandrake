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
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
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
                "averageTileSize, isSpace, scenarioTag }.")]
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

        // ================================================================
        //  W3 - G1 TILE SCALARS + G7 COMMIT
        //  The first complete vertical slice: read, write, import, validate,
        //  and the one tool that makes any of it visible.
        // ================================================================

        /// <summary>Resolve the surface tile for an id, or null with a reason.</summary>
        private static SurfaceTile SurfaceTileAt(int id, out string err)
        {
            err = null;
            var grid = Find.WorldGrid;
            if (grid == null) { err = "No world grid."; return null; }
            if (id < 0 || id >= grid.TilesCount)
            { err = "Tile " + id + " out of range 0.." + (grid.TilesCount - 1) + "."; return null; }
            var t = grid[id] as SurfaceTile;
            if (t == null) { err = "Tile " + id + " is not a SurfaceTile."; return null; }
            return t;
        }

        /// <summary>
        /// RAW read. Deliberately avoids HillinessLabel / MinTemperature / MaxTemperature /
        /// Biomes: those are lazily cached on Tile with NO reset method anywhere in the
        /// codebase, so after a write they report the OLD value for the rest of the session.
        /// A validator built on them would confirm its own writes while the planet stayed wrong.
        /// </summary>
        private static object TileRaw(SurfaceTile t, int id)
        {
            return new
            {
                tile = id,
                biome = t.PrimaryBiome != null ? t.PrimaryBiome.defName : null,
                elevation = t.elevation,
                hilliness = t.hilliness.ToString(),
                hillinessInt = (int)t.hilliness,
                temperature = t.temperature,
                rainfall = t.rainfall,
                swampiness = t.swampiness,
                pollution = t.pollution,
                riverDist = t.riverDist,
                feature = t.feature != null ? t.feature.name : null,
                featureId = t.feature != null ? t.feature.uniqueID : -1,
                waterCovered = t.WaterCovered,
                roadCount = t.potentialRoads != null ? t.potentialRoads.Count : 0,
                riverCount = t.potentialRivers != null ? t.potentialRivers.Count : 0,
                mutatorCount = t.mutatorsNullable != null ? t.mutatorsNullable.Count : 0,
            };
        }

        private static bool TryHilliness(string s, out Hilliness h)
        {
            h = Hilliness.Flat;
            if (string.IsNullOrEmpty(s)) return false;
            s = s.Trim();
            int n;
            if (int.TryParse(s, out n))
            {
                if (n < 0 || n > 5) return false;
                h = (Hilliness)n; return true;
            }
            try { h = (Hilliness)Enum.Parse(typeof(Hilliness), s, true); return true; }
            catch { return false; }
        }

        [Tool(
            "jawa/world_tile_get",
            Description =
                "Read the RAW per-tile scalars for one or more world tiles: biome, elevation, " +
                "hilliness, temperature, rainfall, swampiness, pollution, riverDist, feature, " +
                "plus road/river/mutator counts. Accepts a comma-separated id list and/or a " +
                "'from-to' range. READS RAW FIELDS ON PURPOSE - Tile.HillinessLabel, " +
                "MinTemperature, MaxTemperature and Biomes are lazily cached with no reset " +
                "anywhere in RimWorld, so they lie after a write. Use this to validate, not those.",
            ResultDescription = "success, count, tiles[] of raw scalar records.")]
        public static async Task<object> WorldTileGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids, e.g. '0,17,4720'.")]
            string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to', e.g. '0-99'. Combines with 'tiles'.")]
            string range = null,
            [ToolParameter(Description = "Cap on returned rows. Default 200.")]
            int limit = 200)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded.");

                var ids = new List<int>();
                var errors = new List<string>();

                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(','))
                    {
                        int v;
                        if (int.TryParse(part.Trim(), out v)) ids.Add(v);
                        else errors.Add("Not a tile id: '" + part.Trim() + "'");
                    }

                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-');
                    int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                    { for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i); }
                    else errors.Add("Bad range '" + range + "', expected 'from-to'.");
                }

                if (ids.Count == 0 && errors.Count == 0)
                    return Fail("Give 'tiles' and/or 'range'.");

                if (limit < 1) limit = 1;
                var outp = new List<object>();
                int skipped = 0;
                foreach (var id in ids)
                {
                    if (outp.Count >= limit) { skipped++; continue; }
                    string e;
                    var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    outp.Add(TileRaw(t, id));
                }

                return (object)new
                {
                    success = true,
                    count = outp.Count,
                    requested = ids.Count,
                    truncated = skipped,
                    tilesCount = Find.WorldGrid.TilesCount,
                    errors,
                    tiles = outp,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_tile_set",
            Description =
                "Write per-tile scalars over a list and/or range of world tiles. Any field left " +
                "null is untouched. Fields: biome (BiomeDef defName), elevation, hilliness " +
                "(Flat|SmallHills|LargeHills|Mountainous|Impassable, or 0-5), temperature, " +
                "rainfall, swampiness, pollution. " +
                "DOES NOT REDRAW: RimWorld has no per-tile visual invalidation except pollution, " +
                "so call jawa/world_commit once after a batch. Doing it per write would " +
                "regenerate the whole planet mesh every tile.",
            ResultDescription = "success, written, tiles[] read back RAW after the write.")]
        public static async Task<object> WorldTileSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'.")] string range = null,
            [ToolParameter(Description = "BiomeDef defName.")] string biome = null,
            [ToolParameter(Description = "Elevation in metres. <= 0 reads as water-covered.")] float? elevation = null,
            [ToolParameter(Description = "Flat|SmallHills|LargeHills|Mountainous|Impassable, or 0-5.")] string hilliness = null,
            [ToolParameter(Description = "Temperature C.")] float? temperature = null,
            [ToolParameter(Description = "Rainfall mm.")] float? rainfall = null,
            [ToolParameter(Description = "Swampiness 0-1.")] float? swampiness = null,
            [ToolParameter(Description = "Pollution 0-1.")] float? pollution = null,
            [ToolParameter(Description = "Read back at most this many rows. Default 10.")] int readBack = 10)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded.");

                BiomeDef biomeDef = null;
                if (!string.IsNullOrEmpty(biome))
                {
                    biomeDef = DefDatabase<BiomeDef>.GetNamedSilentFail(biome.Trim());
                    if (biomeDef == null)
                        return Fail("No BiomeDef named '" + biome + "'.", DefSuggestions<BiomeDef>(biome));
                }

                Hilliness hill = Hilliness.Flat; bool setHill = false;
                if (!string.IsNullOrEmpty(hilliness))
                {
                    if (!TryHilliness(hilliness, out hill))
                        return Fail("Bad hilliness '" + hilliness + "'. Use Flat|SmallHills|LargeHills|Mountainous|Impassable or 0-5.");
                    setHill = true;
                }

                if (biomeDef == null && !setHill && !elevation.HasValue && !temperature.HasValue
                    && !rainfall.HasValue && !swampiness.HasValue && !pollution.HasValue)
                    return Fail("Nothing to write - every field was null.");

                // 🔴 swampiness and pollution are QUANTIZED BY THE SAVEGAME, not merely
                // conventionally 0-1: SurfaceLayer.ExposeData serializes swampiness as
                // (byte)Clamp(round(v*255),0,255) and pollution as
                // (ushort)Clamp(round(v*65535),0,65535). An out-of-range write therefore
                // lives in memory, is read back by this tool and CONFIRMED by
                // world_tile_validate, and then silently becomes 0 or 1 on the next load.
                // Vanilla's own writers (WorldGenStep_Pollution) Clamp01 for this reason.
                var clamped = new List<string>();
                if (swampiness.HasValue && (swampiness.Value < 0f || swampiness.Value > 1f))
                { clamped.Add("swampiness " + swampiness.Value + " -> " + Mathf.Clamp01(swampiness.Value)); swampiness = Mathf.Clamp01(swampiness.Value); }
                if (pollution.HasValue && (pollution.Value < 0f || pollution.Value > 1f))
                { clamped.Add("pollution " + pollution.Value + " -> " + Mathf.Clamp01(pollution.Value)); pollution = Mathf.Clamp01(pollution.Value); }

                var ids = new List<int>();
                var errors = new List<string>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(','))
                    { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); else errors.Add("Not a tile id: '" + part.Trim() + "'"); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                    { for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i); }
                    else errors.Add("Bad range '" + range + "'.");
                }
                if (ids.Count == 0) return Fail("Give 'tiles' and/or 'range'.", errors);

                int written = 0;
                foreach (var id in ids)
                {
                    string e;
                    var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    if (biomeDef != null) t.PrimaryBiome = biomeDef;
                    if (setHill) t.hilliness = hill;
                    if (elevation.HasValue) t.elevation = elevation.Value;
                    if (temperature.HasValue) t.temperature = temperature.Value;
                    if (rainfall.HasValue) t.rainfall = rainfall.Value;
                    if (swampiness.HasValue) t.swampiness = swampiness.Value;
                    if (pollution.HasValue) t.pollution = pollution.Value;
                    written++;
                }

                var back = new List<object>();
                foreach (var id in ids)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t != null) back.Add(TileRaw(t, id));
                }

                return (object)new
                {
                    success = true,
                    written,
                    requested = ids.Count,
                    errors,
                    clamped,
                    note = "Nothing is visible until jawa/world_commit runs.",
                    tiles = back,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  G7 - COMMIT. The recipe below is not invented: it is what
        //  vanilla's OWN debug tools call. DebugToolsMisc.SetBiome does
        //  Terrain.RegenerateNow(); the landmark tools add Landmarks and
        //  Hills. There is NO per-tile invalidation in RimWorld except
        //  pollution, so a whole-layer mesh regeneration is the only route.
        // ================================================================
        [Tool(
            "jawa/world_commit",
            Description =
                "Make pending world-tile edits VISIBLE and consistent. Regenerates the world " +
                "draw layers and clears the non-visual caches that otherwise keep answering " +
                "with the pre-edit planet. Call this ONCE after a batch of writes, never per " +
                "write - each call regenerates whole meshes. " +
                "Runs, in order: WorldDrawLayer_Terrain, _Hills, _Landmarks, _Roads, _Rivers " +
                "RegenerateNow; FastTileFinder.DirtyCache (else site/settlement queries keep the " +
                "old biome); WorldPathGrid.RecalculateLayerPerceivedPathCosts (movement " +
                "difficulty is a cached float[] built from biome + hilliness); and " +
                "WorldReachability.ClearCache. " +
                "NOTE it cannot fix Tile's OWN private caches (hillinessLabelCached, " +
                "cachedMaxTemp, cachedMinTemp, tmpSecondaryBiome) - those have no reset method " +
                "anywhere in RimWorld and clear only on reload.",
            ResultDescription = "success, and a steps[] naming each action with ok/skipped/failed.")]
        public static async Task<object> WorldCommit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Regenerate draw layers. Default true.")] bool redraw = true,
            [ToolParameter(Description = "Clear FastTileFinder + reachability caches. Default true.")] bool clearCaches = true,
            [ToolParameter(Description = "Recalculate world path costs. Default true.")] bool recalcPaths = true,
            [ToolParameter(Description = "Use SetAllLayersDirty instead of targeted RegenerateNow. Async, cheaper, next frame.")] bool lazy = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded.");

                var steps = new List<object>();
                var grid = Find.WorldGrid;
                var surface = grid.Surface;
                var renderer = Find.World.renderer;

                Action<string, Action> step = (name, act) =>
                {
                    try { act(); steps.Add(new { step = name, status = "ok" }); }
                    catch (Exception e) { steps.Add(new { step = name, status = "failed", error = e.GetType().Name + ": " + e.Message }); }
                };

                if (redraw && renderer != null)
                {
                    if (lazy)
                    {
                        step("SetAllLayersDirty", () => renderer.SetAllLayersDirty());
                    }
                    else
                    {
                        // Order matches vanilla's landmark debug tool.
                        step("WorldDrawLayer_Terrain.RegenerateNow",
                            () => renderer.GetLayer<WorldDrawLayer_Terrain>(surface).RegenerateNow());
                        step("WorldDrawLayer_Hills.RegenerateNow",
                            () => renderer.GetLayer<WorldDrawLayer_Hills>(surface).RegenerateNow());
                        step("WorldDrawLayer_Landmarks.RegenerateNow",
                            () => renderer.GetLayer<WorldDrawLayer_Landmarks>(surface).RegenerateNow());
                        // No vanilla call site exists for these two - inferred from the
                        // WorldDrawLayer_Paths subclassing. They are wrapped, so a failure
                        // is reported rather than taking the whole commit down.
                        step("WorldDrawLayer_Roads.RegenerateNow",
                            () => renderer.GetLayer<WorldDrawLayer_Roads>(surface).RegenerateNow());
                        step("WorldDrawLayer_Rivers.RegenerateNow",
                            () => renderer.GetLayer<WorldDrawLayer_Rivers>(surface).RegenerateNow());
                    }
                }
                else steps.Add(new { step = "redraw", status = "skipped" });

                if (clearCaches)
                {
                    step("FastTileFinder.DirtyCache", () => surface.FastTileFinder.DirtyCache());
                    step("WorldReachability.ClearCache", () => Find.WorldReachability.ClearCache());
                }
                else steps.Add(new { step = "clearCaches", status = "skipped" });

                if (recalcPaths)
                    step("WorldPathGrid.RecalculateLayerPerceivedPathCosts",
                        () => Find.WorldPathGrid.RecalculateLayerPerceivedPathCosts(surface));
                else steps.Add(new { step = "recalcPaths", status = "skipped" });

                int failed = steps.Count(o => o.GetType().GetProperty("status").GetValue(o, null) as string == "failed");

                return (object)new
                {
                    success = failed == 0,
                    failedSteps = failed,
                    lazy,
                    warning = "Tile's own private caches (HillinessLabel, Min/MaxTemperature, Biomes) " +
                              "have no reset anywhere in RimWorld and survive this. Read raw fields.",
                    steps,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  jawa/world_view - get the PLANET on screen so it can be
        //  photographed. RimWorld's world button is drawn immediate-mode
        //  and is not exposed as a click target, so without this there is
        //  no bridge route to the world map from a running colony - and
        //  every "look at the planet" criterion in this project needs one.
        //  Verse.CameraJumper.TryShowWorld(), read from source 2026-08-19.
        // ================================================================
        [Tool(
            "jawa/world_view",
            Description =
                "Switch the camera between the colony map and the PLANET, and optionally " +
                "centre the globe on a tile. This is the only bridge route to the world map " +
                "from a running game - RimWorld's own world button is immediate-mode and is " +
                "not a clickable target. Use before jawa/world_commit screenshots. " +
                "Close any open dialog first: a modal blanks the screenshot to pure black.",
            ResultDescription = "success, worldSelected before/after, wantedMode, centeredOn.")]
        public static async Task<object> WorldView(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "True shows the planet, false returns to the map. Default true.")]
            bool show = true,
            [ToolParameter(Description = "Optional tile id to centre the globe on.")]
            int centerTile = -1,
            [ToolParameter(Description = "Camera altitude. ~125 = min (close), 550 = entry default, 1100 = max (whole planet). -1 leaves it.")]
            float altitude = -1f,
            [ToolParameter(Description = "Rotate so north is up.")]
            bool northUp = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null) return Fail("No world is loaded.");

                bool before = WorldRendererUtility.WorldSelected;
                bool acted;

                if (show)
                {
                    acted = CameraJumper.TryShowWorld();
                }
                else
                {
                    acted = CameraJumper.TryHideWorld();
                }

                int centered = -1;
                var cam = Find.WorldCameraDriver;
                if (show && centerTile >= 0 && Find.WorldGrid != null
                    && centerTile < Find.WorldGrid.TilesCount && cam != null)
                {
                    try { cam.JumpTo(centerTile); centered = centerTile; }
                    catch (Exception e) { Log.Warning("[JawaBench] world_view: JumpTo failed: " + e.Message); }
                }

                // `altitude` is a public field but WorldCameraDriver.Update lerps it
                // toward the PRIVATE desiredAltitude every frame, so setting only the
                // public one snaps back within a frame or two. Both, or neither.
                float altAfter = -1f;
                if (show && altitude > 0f && cam != null)
                {
                    try
                    {
                        float a = Mathf.Clamp(altitude, WorldCameraDriver.MinAltitude, 1100f);
                        cam.altitude = a;
                        var fi = typeof(WorldCameraDriver).GetField("desiredAltitude",
                            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                        if (fi != null) fi.SetValue(cam, a);
                        altAfter = cam.altitude;
                    }
                    catch (Exception e) { Log.Warning("[JawaBench] world_view: altitude failed: " + e.Message); }
                }

                if (show && northUp && cam != null)
                {
                    try { cam.RotateSoNorthIsUp(false); } catch { }
                }

                return (object)new
                {
                    success = true,
                    requested = show ? "planet" : "map",
                    acted,
                    worldSelectedBefore = before,
                    worldSelectedAfter = WorldRendererUtility.WorldSelected,
                    wantedMode = Find.World.renderer != null ? Find.World.renderer.wantedMode.ToString() : null,
                    centeredOn = centered,
                    altitude = altAfter,
                    altitudeRange = new { min = WorldCameraDriver.MinAltitude, max = 1100f, entryDefault = 550f },
                    northUp,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  G1 IMPORT / VALIDATE - by FILE PATH, not by ops string.
        //  The companion's existing batch convention is a semicolon-separated
        //  `string ops` capped at MaxOps=4096. 21,872 tiles would be ~6 calls
        //  and a multi-megabyte socket payload. Reading the CSV in-process is
        //  symmetric with world_tile_export, which already writes one.
        //  ⚠️ This is the first file-READING code in the companion.
        // ================================================================

        private sealed class TileCsv
        {
            public List<string> Header = new List<string>();
            public List<string[]> Rows = new List<string[]>();
            public Dictionary<string, int> Col = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        }

        private static string[] SplitCsvLine(string line)
        {
            var outp = new List<string>();
            var sb = new System.Text.StringBuilder();
            bool q = false;
            for (int i = 0; i < line.Length; i++)
            {
                char c = line[i];
                if (q)
                {
                    if (c == '"')
                    {
                        if (i + 1 < line.Length && line[i + 1] == '"') { sb.Append('"'); i++; }
                        else q = false;
                    }
                    else sb.Append(c);
                }
                else if (c == '"') q = true;
                else if (c == ',') { outp.Add(sb.ToString()); sb.Length = 0; }
                else sb.Append(c);
            }
            outp.Add(sb.ToString());
            return outp.ToArray();
        }

        private static TileCsv ReadTileCsv(string path, out string err, bool requireTileColumn = true)
        {
            err = null;
            if (string.IsNullOrEmpty(path)) { err = "No path given."; return null; }
            if (!File.Exists(path)) { err = "No such file: " + path; return null; }
            string[] lines;
            try { lines = File.ReadAllLines(path); }
            catch (Exception e) { err = "Could not read " + path + ": " + e.Message; return null; }
            if (lines.Length < 2) { err = "File has no data rows: " + path; return null; }

            var csv = new TileCsv();
            csv.Header = SplitCsvLine(lines[0]).Select(h => h.Trim()).ToList();
            for (int i = 0; i < csv.Header.Count; i++)
                if (!csv.Col.ContainsKey(csv.Header[i])) csv.Col[csv.Header[i]] = i;
            if (requireTileColumn && !csv.Col.ContainsKey("tile")) { err = "CSV has no 'tile' column. Header: " + string.Join(",", csv.Header.ToArray()); return null; }
            for (int i = 1; i < lines.Length; i++)
            {
                if (string.IsNullOrEmpty(lines[i])) continue;
                csv.Rows.Add(SplitCsvLine(lines[i]));
            }
            return csv;
        }

        private static string Cell(TileCsv c, string[] row, string name)
        {
            int i;
            if (!c.Col.TryGetValue(name, out i)) return null;
            if (i >= row.Length) return null;
            var v = row[i];
            return string.IsNullOrEmpty(v) ? null : v.Trim();
        }

        private static bool F(string s, out float v)
        {
            return float.TryParse(s, System.Globalization.NumberStyles.Float,
                                  System.Globalization.CultureInfo.InvariantCulture, out v);
        }

        [Tool(
            "jawa/world_tile_import",
            Description =
                "Import per-tile scalars into the live world from a CSV FILE ON DISK. Reads " +
                "column names from the header, so it accepts any CSV with a 'tile' column plus " +
                "any of: biome, elev_m/elevation, temp_c/temperature, rain_mm/rainfall, " +
                "hilliness (0-5 or a name), swampiness, pollution. Unknown columns are ignored. " +
                "Takes a PATH rather than an ops string because 21,872 tiles will not fit the " +
                "companion's 4096-op batch convention or a socket payload. " +
                "Runs a DRY RUN by default - pass apply=true to write. " +
                "Asserts the grid size when expectTiles is given, and REFUSES on mismatch: a " +
                "different My Little Planet subcount shifts every tile id and would silently " +
                "paint the wrong planet. Does not redraw; call jawa/world_commit after.",
            ResultDescription =
                "success, dryRun, rows, applied (rows actually written, real runs only), " +
                "wouldApply (rows that WOULD write, dry runs only), biomeSkipped (rows refused " +
                "outright for an unresolved biome name - nothing in the row was written), " +
                "skipped, unknownBiomes[], errors[], sample[].")]
        public static async Task<object> WorldTileImport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Absolute path to the CSV.")] string path = null,
            [ToolParameter(Description = "Write for real. Default false (dry run).")] bool apply = false,
            [ToolParameter(Description = "Refuse unless WorldGrid.TilesCount equals this. 0 = no check.")] int expectTiles = 0,
            [ToolParameter(Description = "Stop after this many rows. 0 = all.")] int maxRows = 0,
            [ToolParameter(Description = "Rows to echo back. Default 3.")] int sampleRows = 3)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded.");

                var grid = Find.WorldGrid;
                if (expectTiles > 0 && grid.TilesCount != expectTiles)
                    return Fail("REFUSING: grid has " + grid.TilesCount + " tiles, expected " + expectTiles +
                                ". The tile ids in the CSV are only meaningful on a grid of the expected size - " +
                                "a different My Little Planet subcount shifts EVERY id and would paint the wrong planet.");

                string err;
                var csv = ReadTileCsv(path, out err);
                if (csv == null) return Fail(err);

                var errors = new List<string>();
                var unknownBiomes = new HashSet<string>();
                var biomeCache = new Dictionary<string, BiomeDef>(StringComparer.OrdinalIgnoreCase);
                var sample = new List<object>();
                int applied = 0, wouldApply = 0, biomeSkipped = 0, skipped = 0, rows = 0, clampedCells = 0;

                foreach (var row in csv.Rows)
                {
                    if (maxRows > 0 && rows >= maxRows) break;
                    rows++;

                    int id;
                    var ids = Cell(csv, row, "tile");
                    if (ids == null || !int.TryParse(ids, out id))
                    { skipped++; if (errors.Count < 20) errors.Add("Row " + rows + ": bad tile id '" + ids + "'"); continue; }

                    string e2;
                    var t = SurfaceTileAt(id, out e2);
                    if (t == null) { skipped++; if (errors.Count < 20) errors.Add("Row " + rows + ": " + e2); continue; }

                    BiomeDef bd = null;
                    var bname = Cell(csv, row, "biome");
                    bool biomeUnresolved = false;
                    if (bname != null)
                    {
                        if (!biomeCache.TryGetValue(bname, out bd))
                        {
                            bd = DefDatabase<BiomeDef>.GetNamedSilentFail(bname);
                            biomeCache[bname] = bd;
                        }
                        if (bd == null) { unknownBiomes.Add(bname); biomeUnresolved = true; }
                    }

                    float fv;
                    var elevS = Cell(csv, row, "elev_m") ?? Cell(csv, row, "elevation");
                    var tempS = Cell(csv, row, "temp_c") ?? Cell(csv, row, "temperature");
                    var rainS = Cell(csv, row, "rain_mm") ?? Cell(csv, row, "rainfall");
                    var swS = Cell(csv, row, "swampiness");
                    var poS = Cell(csv, row, "pollution");
                    var hiS = Cell(csv, row, "hilliness");

                    if (sample.Count < Math.Max(0, sampleRows))
                        sample.Add(new { tile = id, biome = bname, elev = elevS, temp = tempS, rain = rainS, hilliness = hiS, swampiness = swS });

                    // Match world_tile_set's stricter behavior: an unresolved biome refuses
                    // the whole row rather than silently writing the other columns while the
                    // biome field it named the tile's identity by stays untouched.
                    if (biomeUnresolved)
                    {
                        biomeSkipped++;
                        if (errors.Count < 20) errors.Add("Row " + rows + ": unknown biome '" + bname + "', row not written");
                        continue;
                    }

                    if (!apply) { wouldApply++; continue; }

                    if (bd != null) t.PrimaryBiome = bd;
                    if (elevS != null && F(elevS, out fv)) t.elevation = fv;
                    if (tempS != null && F(tempS, out fv)) t.temperature = fv;
                    if (rainS != null && F(rainS, out fv)) t.rainfall = fv;
                    // Clamped for the same reason as world_tile_set: the savegame stores
                    // swampiness in one byte and pollution in one ushort, both scaled from
                    // 0-1, so anything outside that range is silently lost on the next load
                    // while every read-back and the validator report it as having landed.
                    if (swS != null && F(swS, out fv))
                    { if (fv < 0f || fv > 1f) clampedCells++; t.swampiness = Mathf.Clamp01(fv); }
                    if (poS != null && F(poS, out fv))
                    { if (fv < 0f || fv > 1f) clampedCells++; t.pollution = Mathf.Clamp01(fv); }
                    if (hiS != null) { Hilliness h; if (TryHilliness(hiS, out h)) t.hilliness = h; }
                    applied++;
                }

                return (object)new
                {
                    success = true,
                    dryRun = !apply,
                    path,
                    header = string.Join(",", csv.Header.ToArray()),
                    rows,
                    applied,
                    wouldApply,
                    biomeSkipped,
                    skipped,
                    clampedCells,
                    tilesCount = grid.TilesCount,
                    unknownBiomes = unknownBiomes.ToList(),
                    note = apply
                        ? "Written. Nothing is visible until jawa/world_commit runs."
                        : "DRY RUN - nothing was written. Pass apply=true. 'wouldApply' rows would " +
                          "have written; 'biomeSkipped' rows would have been refused for an unknown biome.",
                    errors,
                    sample,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_tile_validate",
            Description =
                "Compare the LIVE world against a CSV and report every tile that differs. " +
                "Reads RAW tile fields, never the cached properties (HillinessLabel, " +
                "Min/MaxTemperature, Biomes are lazily cached with no reset anywhere in " +
                "RimWorld and would confirm writes that never landed). Use after " +
                "jawa/world_tile_import to prove the import actually took.",
            ResultDescription =
                "success, rows, matched, mismatched, byField{}, diffs[] (capped).")]
        public static async Task<object> WorldTileValidate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Absolute path to the CSV.")] string path = null,
            [ToolParameter(Description = "Tolerance for float compares. Default 0.5.")] float tolerance = 0.5f,
            [ToolParameter(Description = "Max diff rows to return. Default 25.")] int limit = 25,
            [ToolParameter(Description = "Stop after this many rows. 0 = all.")] int maxRows = 0)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded.");

                string err;
                var csv = ReadTileCsv(path, out err);
                if (csv == null) return Fail(err);

                int rows = 0, matched = 0, mismatched = 0;
                var byField = new Dictionary<string, int>();
                var diffs = new List<object>();
                Action<string> bump = f => { int n; byField.TryGetValue(f, out n); byField[f] = n + 1; };

                foreach (var row in csv.Rows)
                {
                    if (maxRows > 0 && rows >= maxRows) break;
                    rows++;

                    int id; var ids = Cell(csv, row, "tile");
                    if (ids == null || !int.TryParse(ids, out id)) continue;
                    string e2; var t = SurfaceTileAt(id, out e2);
                    if (t == null) continue;

                    var bad = new List<string>();
                    float fv;

                    var bname = Cell(csv, row, "biome");
                    if (bname != null)
                    {
                        var live = t.PrimaryBiome != null ? t.PrimaryBiome.defName : null;
                        if (!string.Equals(live, bname, StringComparison.OrdinalIgnoreCase)) { bad.Add("biome:" + live + "!=" + bname); bump("biome"); }
                    }
                    var s2 = Cell(csv, row, "elev_m") ?? Cell(csv, row, "elevation");
                    if (s2 != null && F(s2, out fv) && Math.Abs(t.elevation - fv) > tolerance) { bad.Add("elevation:" + t.elevation + "!=" + fv); bump("elevation"); }
                    s2 = Cell(csv, row, "temp_c") ?? Cell(csv, row, "temperature");
                    if (s2 != null && F(s2, out fv) && Math.Abs(t.temperature - fv) > tolerance) { bad.Add("temperature:" + t.temperature + "!=" + fv); bump("temperature"); }
                    s2 = Cell(csv, row, "rain_mm") ?? Cell(csv, row, "rainfall");
                    if (s2 != null && F(s2, out fv) && Math.Abs(t.rainfall - fv) > tolerance) { bad.Add("rainfall:" + t.rainfall + "!=" + fv); bump("rainfall"); }
                    s2 = Cell(csv, row, "swampiness");
                    if (s2 != null && F(s2, out fv) && Math.Abs(t.swampiness - fv) > 0.02f) { bad.Add("swampiness:" + t.swampiness + "!=" + fv); bump("swampiness"); }
                    // world_tile_import writes pollution; without this the validator reported
                    // a pollution-only mismatch as a MATCH and "prove the import took" was a lie
                    // for that column. 0-1 scale, so the swampiness tolerance, not `tolerance`.
                    s2 = Cell(csv, row, "pollution");
                    if (s2 != null && F(s2, out fv) && Math.Abs(t.pollution - fv) > 0.02f) { bad.Add("pollution:" + t.pollution + "!=" + fv); bump("pollution"); }
                    s2 = Cell(csv, row, "hilliness");
                    if (s2 != null) { Hilliness h; if (TryHilliness(s2, out h) && t.hilliness != h) { bad.Add("hilliness:" + t.hilliness + "!=" + h); bump("hilliness"); } }

                    if (bad.Count == 0) matched++;
                    else
                    {
                        mismatched++;
                        if (diffs.Count < Math.Max(0, limit))
                            diffs.Add(new { tile = id, fields = bad });
                    }
                }

                return (object)new
                {
                    success = true,
                    path,
                    rows,
                    matched,
                    mismatched,
                    matchPct = rows > 0 ? Math.Round(100.0 * matched / rows, 2) : 0.0,
                    tolerance,
                    byField,
                    readRawFields = true,
                    diffs,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  W4 - G2 LINKS: rivers and roads.
        //
        //  Links live on SurfaceTile, not Tile:
        //     struct RoadLink  { PlanetTile neighbor; RoadDef  road;  }
        //     struct RiverLink { PlanetTile neighbor; RiverDef river; }
        //  and BOTH endpoints carry an entry, so a through-tile appears twice.
        //
        //  🔴 Roads/Rivers are biome-FILTERED VIEWS:
        //     Roads  => PrimaryBiome.allowRoads  ? potentialRoads  : null
        //     Rivers => PrimaryBiome.allowRivers ? potentialRivers : null
        //  A biome with allowRivers=false HIDES existing links without deleting
        //  them. Validate against potential*; read the views to answer "what
        //  does the player see". Two different questions, both needed.
        //
        //  🔴 OverlayRoad/OverlayRiver CANNOT REMOVE - null only logs ErrorOnce,
        //  and a lower-priority overlay is silently refused. Removal and
        //  downgrade are ours to build, and must touch BOTH endpoints.
        // ================================================================

        private static object LinkRows(SurfaceTile t, int id)
        {
            var roads = new List<object>();
            if (t.potentialRoads != null)
                foreach (var r in t.potentialRoads)
                    roads.Add(new { neighbor = r.neighbor.tileId, def = r.road != null ? r.road.defName : null });
            var rivers = new List<object>();
            if (t.potentialRivers != null)
                foreach (var r in t.potentialRivers)
                    rivers.Add(new { neighbor = r.neighbor.tileId, def = r.river != null ? r.river.defName : null });

            var b = t.PrimaryBiome;
            return new
            {
                tile = id,
                biome = b != null ? b.defName : null,
                allowRoads = b != null && b.allowRoads,
                allowRivers = b != null && b.allowRivers,
                riverDist = t.riverDist,
                potentialRoads = roads,
                potentialRivers = rivers,
                // The biome-filtered views - what the PLAYER sees.
                visibleRoads = (t.Roads != null) ? t.Roads.Count : 0,
                visibleRivers = (t.Rivers != null) ? t.Rivers.Count : 0,
                hiddenByBiome = ((t.Roads == null && roads.Count > 0) || (t.Rivers == null && rivers.Count > 0)),
            };
        }

        [Tool(
            "jawa/world_links_get",
            Description =
                "Read river and road links on world tiles. Reports BOTH the raw " +
                "potentialRoads/potentialRivers lists AND the biome-filtered Roads/Rivers " +
                "views the player actually sees, plus a hiddenByBiome flag when they " +
                "disagree - a biome with allowRivers=false hides links without deleting " +
                "them, which looks exactly like a missing river. Also reports riverDist.",
            ResultDescription = "success, count, tiles[] with potential* and visible* counts.")]
        public static async Task<object> WorldLinksGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'.")] string range = null,
            [ToolParameter(Description = "Only return tiles that HAVE at least one link.")] bool onlyLinked = false,
            [ToolParameter(Description = "Max rows. Default 100.")] int limit = 100)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");

                var ids = new List<int>(); var errors = new List<string>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(','))
                    { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                        for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
                }
                if (ids.Count == 0) return Fail("Give 'tiles' and/or 'range'.");

                var outp = new List<object>(); int hidden = 0;
                foreach (var id in ids)
                {
                    if (outp.Count >= Math.Max(1, limit)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    bool has = (t.potentialRoads != null && t.potentialRoads.Count > 0)
                            || (t.potentialRivers != null && t.potentialRivers.Count > 0);
                    if (onlyLinked && !has) continue;
                    var row = LinkRows(t, id);
                    if ((bool)row.GetType().GetProperty("hiddenByBiome").GetValue(row, null)) hidden++;
                    outp.Add(row);
                }
                return (object)new
                {
                    success = true, count = outp.Count, requested = ids.Count,
                    hiddenByBiomeCount = hidden, errors, tiles = outp, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_links_set",
            Description =
                "Lay a river or road between adjacent tiles using RimWorld's own " +
                "WorldGrid.OverlayRiver / OverlayRoad, which write BOTH endpoints and " +
                "maintain riverDist. Takes a path of tile ids: '14,7367,7368' lays a link " +
                "along each consecutive pair. " +
                "RIVERS MUST BE LAID MOUTH FIRST, THEN UPSTREAM - OverlayRiver sets " +
                "riverDist = max(riverDist, previous+1), so the wrong order gives wrong " +
                "distances. " +
                "NOTE Overlay* silently REFUSES a lower-priority def over a higher one " +
                "(road.priority, river.degradeThreshold): to downgrade, use " +
                "jawa/world_links_clear first. Does not redraw; call jawa/world_commit.",
            ResultDescription = "success, laid, refused[], and a read-back of each touched tile.")]
        public static async Task<object> WorldLinksSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'river' or 'road'.")] string kind = "river",
            [ToolParameter(Description = "Ordered tile ids, comma separated. Consecutive pairs are linked. Rivers: MOUTH FIRST.")] string path = null,
            [ToolParameter(Description = "RiverDef (Creek|River|LargeRiver|HugeRiver) or RoadDef (DirtPath|DirtRoad|StoneRoad|AncientAsphaltRoad|AncientAsphaltHighway).")] string def = null,
            [ToolParameter(Description = "Read back at most this many tiles. Default 8.")] int readBack = 8)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid;
                bool river = string.Equals(kind, "river", StringComparison.OrdinalIgnoreCase);
                if (!river && !string.Equals(kind, "road", StringComparison.OrdinalIgnoreCase))
                    return Fail("kind must be 'river' or 'road'.");
                if (string.IsNullOrEmpty(def)) return Fail("Give a def.");

                RiverDef rv = null; RoadDef rd = null;
                if (river)
                {
                    rv = DefDatabase<RiverDef>.GetNamedSilentFail(def.Trim());
                    if (rv == null) return Fail("No RiverDef '" + def + "'.", DefSuggestions<RiverDef>(def));
                }
                else
                {
                    rd = DefDatabase<RoadDef>.GetNamedSilentFail(def.Trim());
                    if (rd == null) return Fail("No RoadDef '" + def + "'.", DefSuggestions<RoadDef>(def));
                }

                var ids = new List<int>();
                foreach (var part in (path ?? "").Split(','))
                { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (ids.Count < 2) return Fail("Give at least two tile ids in 'path'.");

                var refused = new List<object>(); int laid = 0;
                var nbrs = new List<PlanetTile>();
                for (int i = 0; i + 1 < ids.Count; i++)
                {
                    int a = ids[i], b = ids[i + 1];
                    string e1, e2;
                    var ta = SurfaceTileAt(a, out e1); var tb = SurfaceTileAt(b, out e2);
                    if (ta == null || tb == null) { refused.Add(new { from = a, to = b, why = e1 ?? e2 }); continue; }

                    nbrs.Clear(); grid.GetTileNeighbors(a, nbrs);
                    bool adjacent = nbrs.Any(n => n.tileId == b);
                    if (!adjacent) { refused.Add(new { from = a, to = b, why = "not adjacent" }); continue; }

                    if (river) grid.OverlayRiver(a, b, rv); else grid.OverlayRoad(a, b, rd);
                    laid++;
                }

                var back = new List<object>();
                foreach (var id in ids)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t != null) back.Add(LinkRows(t, id));
                }

                return (object)new
                {
                    success = true, kind, def, laid, pairs = Math.Max(0, ids.Count - 1),
                    refused,
                    note = "Overlay* refuses a lower-priority def silently. Nothing is visible until jawa/world_commit.",
                    tiles = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_links_clear",
            Description =
                "REMOVE river or road links - capability RimWorld itself does not have. " +
                "WorldGrid.OverlayRiver/OverlayRoad refuse a null def (Log.ErrorOnce " +
                "'Attempted to remove road with overlayRoad; not supported'), so removal " +
                "means editing SurfaceTile.potentialRivers / potentialRoads directly, and " +
                "on BOTH endpoints or the link survives from the other side. " +
                "Clears every link on the named tiles, or only the segment between a " +
                "specific pair when 'to' is given. Does not redraw; call jawa/world_commit.",
            ResultDescription = "success, removedEntries, tilesTouched, and a read-back.")]
        public static async Task<object> WorldLinksClear(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'river', 'road', or 'both'. Default both.")] string kind = "both",
            [ToolParameter(Description = "Comma-separated tile ids to clear.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'.")] string range = null,
            [ToolParameter(Description = "If given with a single tile in 'tiles', remove only the segment between them (both directions).")] int to = -1,
            [ToolParameter(Description = "Read back at most this many tiles. Default 8.")] int readBack = 8)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                bool doRivers = kind == "both" || string.Equals(kind, "river", StringComparison.OrdinalIgnoreCase);
                bool doRoads = kind == "both" || string.Equals(kind, "road", StringComparison.OrdinalIgnoreCase);
                if (!doRivers && !doRoads) return Fail("kind must be 'river', 'road' or 'both'.");

                var ids = new List<int>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(','))
                    { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                        for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
                }
                if (ids.Count == 0) return Fail("Give 'tiles' and/or 'range'.");

                int removed = 0; var touched = new HashSet<int>();

                // Removing one entry always means removing its mirror on the other
                // endpoint too, or the link is still there when read from that side.
                Action<int, int> clearPair = (a, b) =>
                {
                    string e; var ta = SurfaceTileAt(a, out e);
                    if (ta == null) return;
                    if (doRivers && ta.potentialRivers != null)
                    {
                        int n = ta.potentialRivers.RemoveAll(l => b < 0 || l.neighbor.tileId == b);
                        if (n > 0)
                        {
                            removed += n; touched.Add(a);
                            // A tile with no river links left is a tile with no river:
                            // riverDist defaults to 0 on a fresh SurfaceTile (SurfaceTile.cs),
                            // so an empty potentialRivers must not leave a stale nonzero
                            // riverDist behind for map gen and world_links_get to trip over.
                            if (ta.potentialRivers.Count == 0) ta.riverDist = 0;
                        }
                    }
                    if (doRoads && ta.potentialRoads != null)
                    {
                        int n = ta.potentialRoads.RemoveAll(l => b < 0 || l.neighbor.tileId == b);
                        if (n > 0) { removed += n; touched.Add(a); }
                    }
                };

                if (to >= 0 && ids.Count == 1)
                {
                    clearPair(ids[0], to);
                    clearPair(to, ids[0]);
                }
                else
                {
                    foreach (var id in ids)
                    {
                        // Collect the far endpoints first, then clear their mirrors.
                        string e; var t = SurfaceTileAt(id, out e);
                        if (t == null) continue;
                        var far = new List<int>();
                        if (doRivers && t.potentialRivers != null) far.AddRange(t.potentialRivers.Select(l => l.neighbor.tileId));
                        if (doRoads && t.potentialRoads != null) far.AddRange(t.potentialRoads.Select(l => l.neighbor.tileId));
                        clearPair(id, -1);
                        foreach (var f in far.Distinct()) clearPair(f, id);
                    }
                }

                var back = new List<object>();
                foreach (var id in ids)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t != null) back.Add(LinkRows(t, id));
                }

                return (object)new
                {
                    success = true, kind, removedEntries = removed,
                    tilesTouched = touched.Count,
                    note = "Both endpoints were cleared. Nothing is visible until jawa/world_commit.",
                    tiles = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        // 🔴 `requireTileColumn: false` is why this wrapper exists at all.
        // `ReadTileCsv` hard-requires a `tile` column, which is right for
        // world_tile_import and WRONG for the links CSV, whose rows are EDGES
        // (kind,a,b,def) and have no single tile. Calling the tile reader from
        // WorldLinksImport made that tool unable to read its own documented
        // format: it refused with "CSV has no 'tile' column" before ever
        // reaching its kind/a/b/def check. Found live 2026-08-20.
        private static TileCsv ReadTileCsv2(string path, out string err, bool requireTileColumn = true)
        {
            var csv = ReadTileCsv(path, out err, requireTileColumn);
            return csv;
        }

        [Tool(
            "jawa/world_links_import",
            Description =
                "Import rivers and roads from a CSV file with columns kind,a,b,def " +
                "(kind is 'river' or 'road'; a and b are adjacent tile ids). Rivers are " +
                "laid before roads, and rivers are applied IN FILE ORDER so the file must " +
                "already be mouth-first. Dry run by default; pass apply=true. " +
                "Non-adjacent pairs are REFUSED: OverlayRiver/OverlayRoad do not check " +
                "adjacency and would write a link between distant tiles on both endpoints. " +
                "clearFirst clears existing links on the touched tiles AND the mirror entries " +
                "on their neighbours, so nothing is left one-sided. " +
                "Does not redraw; call jawa/world_commit after.",
            ResultDescription = "success, dryRun, rows, rivers, roads, nonAdjacentRefused, refused[], unknownDefs[].")]
        public static async Task<object> WorldLinksImport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Absolute path to the links CSV.")] string path = null,
            [ToolParameter(Description = "Write for real. Default false.")] bool apply = false,
            [ToolParameter(Description = "Refuse unless WorldGrid.TilesCount equals this. 0 = no check.")] int expectTiles = 0,
            [ToolParameter(Description = "Clear existing links on every touched tile first.")] bool clearFirst = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid;
                if (expectTiles > 0 && grid.TilesCount != expectTiles)
                    return Fail("REFUSING: grid has " + grid.TilesCount + " tiles, expected " + expectTiles + ".");

                string err; var csv = ReadTileCsv2(path, out err, requireTileColumn: false);
                if (csv == null) return Fail(err);
                if (!csv.Col.ContainsKey("kind") || !csv.Col.ContainsKey("a") || !csv.Col.ContainsKey("b") || !csv.Col.ContainsKey("def"))
                    return Fail("Links CSV needs columns kind,a,b,def. Header: " + string.Join(",", csv.Header.ToArray()));

                var unknown = new HashSet<string>(); var refused = new List<object>();
                int rivers = 0, roads = 0, rows = 0;
                var pending = new List<Tuple<bool, int, int, string>>();

                foreach (var row in csv.Rows)
                {
                    rows++;
                    var k = Cell(csv, row, "kind"); var aS = Cell(csv, row, "a");
                    var bS = Cell(csv, row, "b"); var dS = Cell(csv, row, "def");
                    int a, b;
                    if (k == null || aS == null || bS == null || dS == null
                        || !int.TryParse(aS, out a) || !int.TryParse(bS, out b))
                    { refused.Add(new { row = rows, why = "malformed" }); continue; }
                    bool isRiver = k.Equals("river", StringComparison.OrdinalIgnoreCase);
                    pending.Add(Tuple.Create(isRiver, a, b, dS));
                }

                if (clearFirst && apply)
                {
                    var touched = new HashSet<int>();
                    foreach (var p in pending) { touched.Add(p.Item2); touched.Add(p.Item3); }

                    // A link lives on BOTH endpoints. Clearing only the tiles the CSV names
                    // left the mirror entry alive on every neighbour the CSV did NOT name -
                    // manufacturing exactly the asymmetric corruption world_links_validate
                    // hunts for. Collect the far endpoints first, then strip their mirrors.
                    foreach (var id in touched.ToList())
                    {
                        string e; var t = SurfaceTileAt(id, out e);
                        if (t == null) continue;
                        var far = new List<int>();
                        if (t.potentialRivers != null) far.AddRange(t.potentialRivers.Select(l => l.neighbor.tileId));
                        if (t.potentialRoads != null) far.AddRange(t.potentialRoads.Select(l => l.neighbor.tileId));
                        foreach (var f in far.Distinct())
                        {
                            if (touched.Contains(f)) continue;   // cleared wholesale below
                            string e2; var tf = SurfaceTileAt(f, out e2);
                            if (tf == null) continue;
                            if (tf.potentialRivers != null && tf.potentialRivers.RemoveAll(l => l.neighbor.tileId == id) > 0
                                && tf.potentialRivers.Count == 0) tf.riverDist = 0;
                            if (tf.potentialRoads != null) tf.potentialRoads.RemoveAll(l => l.neighbor.tileId == id);
                        }
                    }

                    foreach (var id in touched)
                    {
                        string e; var t = SurfaceTileAt(id, out e);
                        if (t == null) continue;
                        if (t.potentialRivers != null) t.potentialRivers.Clear();
                        if (t.potentialRoads != null) t.potentialRoads.Clear();
                        // No river links left means no river: a stale nonzero riverDist would
                        // otherwise survive and poison OverlayRiver's max(riverDist, prev+1)
                        // for every river laid below. Same reset world_links_clear does.
                        t.riverDist = 0;
                    }
                }

                // Rivers first, in file order (mouth-first is the file's responsibility),
                // then roads - matching the order vanilla's own worldgen steps use.
                var inbrs = new List<PlanetTile>();
                int nonAdjacent = 0;
                foreach (var pass in new[] { true, false })
                    foreach (var p in pending)
                    {
                        if (p.Item1 != pass) continue;
                        string e1, e2;
                        var ta = SurfaceTileAt(p.Item2, out e1); var tb = SurfaceTileAt(p.Item3, out e2);
                        if (ta == null || tb == null) { if (refused.Count < 30) refused.Add(new { from = p.Item2, to = p.Item3, why = e1 ?? e2 }); continue; }

                        // WorldGrid.OverlayRiver/OverlayRoad do NOT check adjacency - read from
                        // the 1.6 source - so a CSV naming two distant tiles would write a link
                        // between non-neighbours on both endpoints, which is one of the very
                        // corruptions world_links_validate reports as nonAdjacent[]. The
                        // single-pair sibling world_links_set has always gated this; the
                        // importer did not, so the bulk route was the unguarded one.
                        inbrs.Clear(); grid.GetTileNeighbors(p.Item2, inbrs);
                        if (!inbrs.Any(x => x.tileId == p.Item3))
                        {
                            nonAdjacent++;
                            if (refused.Count < 30) refused.Add(new { from = p.Item2, to = p.Item3, why = "not adjacent" });
                            continue;
                        }

                        if (p.Item1)
                        {
                            var rv = DefDatabase<RiverDef>.GetNamedSilentFail(p.Item4);
                            if (rv == null) { unknown.Add(p.Item4); continue; }
                            if (apply) grid.OverlayRiver(p.Item2, p.Item3, rv);
                            rivers++;
                        }
                        else
                        {
                            var rd = DefDatabase<RoadDef>.GetNamedSilentFail(p.Item4);
                            if (rd == null) { unknown.Add(p.Item4); continue; }
                            if (apply) grid.OverlayRoad(p.Item2, p.Item3, rd);
                            roads++;
                        }
                    }

                return (object)new
                {
                    success = true, dryRun = !apply, path, rows, rivers, roads,
                    clearedFirst = clearFirst && apply,
                    nonAdjacentRefused = nonAdjacent,
                    unknownDefs = unknown.ToList(), refused,
                    note = apply ? "Written. Call jawa/world_commit." : "DRY RUN - pass apply=true.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_links_validate",
            Description =
                "Check the integrity of the live river/road network. Reports: links whose " +
                "mirror entry is MISSING on the far endpoint (asymmetric, the classic " +
                "corruption), links to non-adjacent tiles, links HIDDEN by their tile's " +
                "biome (allowRoads/allowRivers false), and river mouths - river tiles with " +
                "no water-covered neighbour. Give a links CSV (kind,a,b,def) in 'path' and it " +
                "also reports which of its edges are MISSING from the live world or carry a " +
                "different def - the proof that jawa/world_links_import actually landed.",
            ResultDescription =
                "success, riverEntries, roadEntries, asymmetricCount/nonAdjacentCount/" +
                "hiddenByBiomeCount (TRUE totals, not capped), the matching asymmetric[], " +
                "nonAdjacent[], hiddenByBiome[] example lists capped at 'limit', " +
                "landlockedRiverTiles, and csv{} when a path was given.")]
        public static async Task<object> WorldLinksValidate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Optional links CSV to compare against.")] string path = null,
            [ToolParameter(Description = "Max examples per category. Default 15.")] int limit = 15)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid;
                int n = grid.TilesCount;

                var asym = new List<object>(); var nonAdj = new List<object>(); var hidden = new List<object>();
                // The example lists are capped at `limit`; the COUNTS must not be. Reporting
                // asym.Count made a planet with 5,000 asymmetric links read as exactly `limit`
                // of them - a saturated instrument that says "nearly clean" about a wreck.
                // world_mutators_audit already keeps a separate uncapped counter; match it.
                int asymN = 0, nonAdjN = 0, hiddenN = 0;
                int riverEntries = 0, roadEntries = 0, riverTiles = 0, landlocked = 0;
                var nbrs = new List<PlanetTile>();

                for (int i = 0; i < n; i++)
                {
                    var t = grid[i] as SurfaceTile;
                    if (t == null) continue;
                    bool hasRiver = t.potentialRivers != null && t.potentialRivers.Count > 0;
                    if (hasRiver) riverTiles++;

                    var b = t.PrimaryBiome;
                    if (b != null)
                    {
                        if (!b.allowRivers && hasRiver)
                        {
                            hiddenN++;
                            if (hidden.Count < limit) hidden.Add(new { tile = i, kind = "river", biome = b.defName, links = t.potentialRivers.Count });
                        }
                        if (!b.allowRoads && t.potentialRoads != null && t.potentialRoads.Count > 0)
                        {
                            hiddenN++;
                            if (hidden.Count < limit) hidden.Add(new { tile = i, kind = "road", biome = b.defName, links = t.potentialRoads.Count });
                        }
                    }

                    nbrs.Clear(); grid.GetTileNeighbors(i, nbrs);

                    if (t.potentialRivers != null)
                        foreach (var l in t.potentialRivers)
                        {
                            riverEntries++;
                            int far = l.neighbor.tileId;
                            if (!nbrs.Any(x => x.tileId == far)) { nonAdjN++; if (nonAdj.Count < limit) nonAdj.Add(new { tile = i, to = far, kind = "river" }); continue; }
                            var tf = (far >= 0 && far < n) ? grid[far] as SurfaceTile : null;
                            bool mirror = tf != null && tf.potentialRivers != null && tf.potentialRivers.Any(x => x.neighbor.tileId == i);
                            if (!mirror) { asymN++; if (asym.Count < limit) asym.Add(new { tile = i, to = far, kind = "river", def = l.river != null ? l.river.defName : null }); }
                        }

                    if (t.potentialRoads != null)
                        foreach (var l in t.potentialRoads)
                        {
                            roadEntries++;
                            int far = l.neighbor.tileId;
                            if (!nbrs.Any(x => x.tileId == far)) { nonAdjN++; if (nonAdj.Count < limit) nonAdj.Add(new { tile = i, to = far, kind = "road" }); continue; }
                            var tf = (far >= 0 && far < n) ? grid[far] as SurfaceTile : null;
                            bool mirror = tf != null && tf.potentialRoads != null && tf.potentialRoads.Any(x => x.neighbor.tileId == i);
                            if (!mirror) { asymN++; if (asym.Count < limit) asym.Add(new { tile = i, to = far, kind = "road", def = l.road != null ? l.road.defName : null }); }
                        }

                    // A river tile with no water neighbour is a candidate "reaches no sea".
                    // The owner's ruling: only HIGH-accumulation trunks must reach a sea,
                    // so this is a count to look at, never an automatic defect.
                    if (hasRiver && !nbrs.Any(x => { var q = grid[x.tileId] as SurfaceTile; return q != null && q.WaterCovered; }))
                        landlocked++;
                }

                // The documented CSV comparison. Until 2026-09-03 `path` was declared,
                // documented as "Optionally compares against a links CSV", and then never
                // read: passing a file produced success=true and no comparison at all.
                object csvReport = null;
                if (!string.IsNullOrEmpty(path))
                {
                    string cerr; var csv = ReadTileCsv2(path, out cerr, requireTileColumn: false);
                    if (csv == null) csvReport = new { path, error = cerr };
                    else if (!csv.Col.ContainsKey("kind") || !csv.Col.ContainsKey("a") || !csv.Col.ContainsKey("b") || !csv.Col.ContainsKey("def"))
                        csvReport = new { path, error = "Links CSV needs columns kind,a,b,def. Header: " + string.Join(",", csv.Header.ToArray()) };
                    else
                    {
                        int cRows = 0, cPresent = 0, cMissing = 0, cWrongDef = 0, cMalformed = 0;
                        var missing = new List<object>(); var wrongDef = new List<object>();
                        foreach (var row in csv.Rows)
                        {
                            cRows++;
                            var k = Cell(csv, row, "kind"); var aS = Cell(csv, row, "a");
                            var bS = Cell(csv, row, "b"); var dS = Cell(csv, row, "def");
                            int ca, cb;
                            if (k == null || aS == null || bS == null || dS == null
                                || !int.TryParse(aS, out ca) || !int.TryParse(bS, out cb))
                            { cMalformed++; continue; }

                            bool isRiver = k.Equals("river", StringComparison.OrdinalIgnoreCase);
                            var ta = (ca >= 0 && ca < n) ? grid[ca] as SurfaceTile : null;
                            if (ta == null) { cMissing++; if (missing.Count < limit) missing.Add(new { row = cRows, a = ca, b = cb, kind = k, why = "no such surface tile" }); continue; }

                            // Read the raw potential* lists, never the biome-filtered views:
                            // a biome with allowRivers=false hides a link that is really there.
                            string liveDef = null; bool found = false;
                            if (isRiver)
                            {
                                if (ta.potentialRivers != null)
                                    foreach (var l in ta.potentialRivers)
                                        if (l.neighbor.tileId == cb) { found = true; liveDef = l.river != null ? l.river.defName : null; break; }
                            }
                            else if (ta.potentialRoads != null)
                                foreach (var l in ta.potentialRoads)
                                    if (l.neighbor.tileId == cb) { found = true; liveDef = l.road != null ? l.road.defName : null; break; }

                            if (!found) { cMissing++; if (missing.Count < limit) missing.Add(new { row = cRows, a = ca, b = cb, kind = k, expected = dS }); }
                            else if (!string.Equals(liveDef, dS, StringComparison.OrdinalIgnoreCase))
                            { cWrongDef++; if (wrongDef.Count < limit) wrongDef.Add(new { row = cRows, a = ca, b = cb, kind = k, live = liveDef, expected = dS }); }
                            else cPresent++;
                        }
                        csvReport = new
                        {
                            path,
                            rows = cRows,
                            present = cPresent,
                            missing = cMissing,
                            wrongDef = cWrongDef,
                            malformed = cMalformed,
                            matchPct = cRows > 0 ? Math.Round(100.0 * cPresent / cRows, 2) : 0.0,
                            missingExamples = missing,
                            wrongDefExamples = wrongDef,
                            note = "Compared against the RAW potential* lists, not the biome-filtered views.",
                        };
                    }
                }

                return (object)new
                {
                    success = true,
                    tilesScanned = n,
                    riverEntries, roadEntries, riverTiles,
                    asymmetricCount = asymN, nonAdjacentCount = nonAdjN,
                    hiddenByBiomeCount = hiddenN,
                    examplesCapped = limit,
                    csv = csvReport,
                    landlockedRiverTiles = landlocked,
                    landlockedNote = "Not automatically a defect - the owner ruled low-accumulation rivers MAY die in playas or salt pans; only high-accumulation trunks must reach a sea.",
                    asymmetric = asym, nonAdjacent = nonAdj, hiddenByBiome = hidden,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  W5 - G3 TILE MUTATORS (336 defs) AND LANDMARKS (113 defs)
        //
        //  Mutators: ALWAYS go through Tile.AddMutator / RemoveMutator, never
        //  mutatorsNullable directly. AddMutator resolves category conflicts,
        //  sorts by genOrder, and calls def.Worker?.OnAddedToTile(tile) - the
        //  worker callback is where the side effects live.
        //
        //  Landmarks: Find.World.landmarks, a Dictionary<PlanetTile, Landmark>.
        //  🔴 Odyssey-gated: Tile.Landmark returns null when !OdysseyActive.
        //  🔴 AddLandmark ALSO rolls the def's mutatorChances / comboLandmark-
        //     Mutators onto the tile, so adding a landmark is a mutator write too.
        //  🔴 ORDERING: LandmarkDef.IsValidTile REJECTS any tile that already
        //     holds a settlement. Landmarks BEFORE settlements, always.
        // ================================================================

        private static object MutatorRow(SurfaceTile t, int id)
        {
            var ms = new List<object>();
            if (t.mutatorsNullable != null)
                foreach (var m in t.mutatorsNullable)
                    ms.Add(new
                    {
                        def = m != null ? m.defName : null,
                        label = m != null ? m.label : null,
                        genOrder = m != null ? m.genOrder : 0f,
                    });

            Landmark lm = null;
            try { lm = t.Landmark; } catch { }

            return new
            {
                tile = id,
                biome = t.PrimaryBiome != null ? t.PrimaryBiome.defName : null,
                waterCovered = t.WaterCovered,
                isCoastal = SafeIsCoastal(id),
                mutatorCount = ms.Count,
                mutators = ms,
                landmark = lm != null ? lm.def.defName : null,
                landmarkName = lm != null ? lm.name : null,
                landmarkIsCombo = lm != null && lm.isComboLandmark,
            };
        }

        private static bool SafeIsCoastal(int id)
        {
            try { return Find.World.CoastDirectionAt(id) != Rot4.Invalid; }
            catch { return false; }
        }

        [Tool(
            "jawa/world_mutators_get",
            Description =
                "Read the TileMutatorDefs and the Landmark on world tiles. Mutators are what " +
                "give a tile its caves, coast, cliffs, mixed biome and so on - 336 defs ship. " +
                "Also reports whether the tile is genuinely coastal by real adjacency " +
                "(World.CoastDirectionAt), which is how a stale Coast mutator is spotted.",
            ResultDescription = "success, count, tiles[] with mutators[] and landmark.")]
        public static async Task<object> WorldMutatorsGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'.")] string range = null,
            [ToolParameter(Description = "Only tiles carrying at least one mutator.")] bool onlyWithMutators = false,
            [ToolParameter(Description = "Max rows. Default 100.")] int limit = 100)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var ids = new List<int>(); var errors = new List<string>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                        for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
                }
                if (ids.Count == 0) return Fail("Give 'tiles' and/or 'range'.");

                var outp = new List<object>();
                foreach (var id in ids)
                {
                    if (outp.Count >= Math.Max(1, limit)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    if (onlyWithMutators && (t.mutatorsNullable == null || t.mutatorsNullable.Count == 0)) continue;
                    outp.Add(MutatorRow(t, id));
                }
                return (object)new
                {
                    success = true, count = outp.Count, requested = ids.Count,
                    odysseyActive = ModsConfig.OdysseyActive,
                    errors, tiles = outp, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_mutators_set",
            Description =
                "Add or remove TileMutatorDefs on world tiles. Uses Tile.AddMutator / " +
                "RemoveMutator, never the raw list - AddMutator resolves category conflicts, " +
                "sorts by genOrder and fires the def's Worker.OnAddedToTile, which is where " +
                "the actual effect lives. Writing mutatorsNullable directly would skip all of " +
                "that. Use action='clear' to strip every mutator from the named tiles. " +
                "Does not redraw; call jawa/world_commit.",
            ResultDescription = "success, added, removed, and a read-back of each tile.")]
        public static async Task<object> WorldMutatorsSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'add', 'remove' or 'clear'.")] string action = "add",
            [ToolParameter(Description = "Comma-separated TileMutatorDef names. Ignored for 'clear'.")] string mutators = null,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'.")] string range = null,
            [ToolParameter(Description = "Read back at most this many tiles. Default 8.")] int readBack = 8)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                bool add = string.Equals(action, "add", StringComparison.OrdinalIgnoreCase);
                bool rem = string.Equals(action, "remove", StringComparison.OrdinalIgnoreCase);
                bool clr = string.Equals(action, "clear", StringComparison.OrdinalIgnoreCase);
                if (!add && !rem && !clr) return Fail("action must be add|remove|clear.");

                var defs = new List<TileMutatorDef>(); var unknown = new List<string>();
                if (!clr)
                {
                    if (string.IsNullOrEmpty(mutators)) return Fail("Give 'mutators'.");
                    foreach (var mname in mutators.Split(','))
                    {
                        var nm = mname.Trim(); if (nm.Length == 0) continue;
                        var d = DefDatabase<TileMutatorDef>.GetNamedSilentFail(nm);
                        if (d == null) unknown.Add(nm); else defs.Add(d);
                    }
                    if (defs.Count == 0) return Fail("No known TileMutatorDef in '" + mutators + "'.", unknown);
                }

                var ids = new List<int>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                        for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
                }
                if (ids.Count == 0) return Fail("Give 'tiles' and/or 'range'.");

                int added = 0, removed = 0; var errors = new List<string>();
                foreach (var id in ids)
                {
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    try
                    {
                        if (clr)
                        {
                            if (t.mutatorsNullable != null)
                            {
                                foreach (var m in t.mutatorsNullable.ToList()) { t.RemoveMutator(m); removed++; }
                            }
                        }
                        else if (add)
                        {
                            foreach (var d in defs)
                            {
                                if (t.mutatorsNullable != null && t.mutatorsNullable.Contains(d)) continue;
                                t.AddMutator(d); added++;
                            }
                        }
                        else
                        {
                            foreach (var d in defs)
                            {
                                if (t.mutatorsNullable != null && t.mutatorsNullable.Contains(d)) { t.RemoveMutator(d); removed++; }
                            }
                        }
                    }
                    catch (Exception ex) { errors.Add("tile " + id + ": " + ex.GetType().Name + ": " + ex.Message); }
                }

                var back = new List<object>();
                foreach (var id in ids)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t != null) back.Add(MutatorRow(t, id));
                }
                return (object)new
                {
                    success = true, action, added, removed,
                    unknownDefs = unknown, errors,
                    note = "Nothing is visible until jawa/world_commit.",
                    tiles = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_mutators_audit",
            Description =
                "Sweep the whole planet for mutators that contradict the terrain under them - " +
                "the defect class that survives a repaint. Reports tiles carrying a named " +
                "marine/coastal mutator that are NOT coastal by real adjacency " +
                "(World.CoastDirectionAt), and optionally how deep inland they sit. " +
                "This is how 'Coast on a tile 2,000 tiles from any sea' is found. Read-only.",
            ResultDescription = "success, histogram of every mutator by count, and offenders[].")]
        public static async Task<object> WorldMutatorsAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated mutator defNames that imply water adjacency. Default 'Coast'.")]
            string marineMutators = "Coast",
            [ToolParameter(Description = "Max offender rows. Default 30.")] int limit = 30,
            [ToolParameter(Description = "Also return the full mutator histogram. Default true.")] bool histogram = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid; int n = grid.TilesCount;

                var marine = new HashSet<string>((marineMutators ?? "").Split(',')
                                .Select(x => x.Trim()).Where(x => x.Length > 0), StringComparer.OrdinalIgnoreCase);

                var hist = new Dictionary<string, int>();
                var offenders = new List<object>();
                int offenderCount = 0, withMutators = 0;

                for (int i = 0; i < n; i++)
                {
                    var t = grid[i] as SurfaceTile;
                    if (t == null || t.mutatorsNullable == null || t.mutatorsNullable.Count == 0) continue;
                    withMutators++;
                    bool coastal = SafeIsCoastal(i);
                    foreach (var m in t.mutatorsNullable)
                    {
                        if (m == null) continue;
                        if (histogram) { int c; hist.TryGetValue(m.defName, out c); hist[m.defName] = c + 1; }
                        if (marine.Contains(m.defName) && !coastal)
                        {
                            offenderCount++;
                            if (offenders.Count < Math.Max(0, limit))
                                offenders.Add(new
                                {
                                    tile = i,
                                    mutator = m.defName,
                                    biome = t.PrimaryBiome != null ? t.PrimaryBiome.defName : null,
                                    waterCovered = t.WaterCovered,
                                    elevation = t.elevation,
                                });
                        }
                    }
                }

                return (object)new
                {
                    success = true,
                    tilesScanned = n,
                    tilesWithMutators = withMutators,
                    marineChecked = marine.ToList(),
                    offenderCount,
                    offenders,
                    mutatorHistogram = histogram
                        ? hist.OrderByDescending(k => k.Value).Take(60).ToDictionary(k => k.Key, k => k.Value)
                        : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_landmarks_get",
            Description =
                "List the landmarks on the planet (Find.World.landmarks). 113 LandmarkDefs " +
                "ship with Odyssey. Reports each landmark's tile, def, generated name and " +
                "whether it is a combo landmark. " +
                "🔴 Landmarks are ODYSSEY-GATED: without Odyssey active Tile.Landmark is " +
                "always null and this returns an empty set, which is not the same as a " +
                "world with no landmarks - the odysseyActive flag tells you which you have.",
            ResultDescription = "success, odysseyActive, count, landmarks[].")]
        public static async Task<object> WorldLandmarksGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only landmarks of this LandmarkDef.")] string def = null,
            [ToolParameter(Description = "Max rows. Default 100.")] int limit = 100)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null) return Fail("No world is loaded.");
                var wl = Find.World.landmarks;
                if (wl == null || wl.landmarks == null)
                    return (object)new { success = true, odysseyActive = ModsConfig.OdysseyActive, count = 0, landmarks = new List<object>(), note = "No landmark manager on this world." };

                var outp = new List<object>(); int total = 0;
                foreach (var kv in wl.landmarks)
                {
                    if (kv.Value == null) continue;
                    if (!string.IsNullOrEmpty(def) && (kv.Value.def == null || !kv.Value.def.defName.Equals(def, StringComparison.OrdinalIgnoreCase))) continue;
                    total++;
                    if (outp.Count >= Math.Max(1, limit)) continue;
                    outp.Add(new
                    {
                        tile = kv.Key.tileId,
                        layer = kv.Key.Layer != null && kv.Key.Layer.Def != null ? kv.Key.Layer.Def.defName : null,
                        def = kv.Value.def != null ? kv.Value.def.defName : null,
                        label = kv.Value.def != null ? kv.Value.def.label : null,
                        name = kv.Value.name,
                        isCombo = kv.Value.isComboLandmark,
                    });
                }
                return (object)new
                {
                    success = true, odysseyActive = ModsConfig.OdysseyActive,
                    count = total, returned = outp.Count, landmarks = outp, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_landmarks_set",
            Description =
                "Add or remove a landmark on a world tile via WorldLandmarks.AddLandmark / " +
                "RemoveLandmark. " +
                "⚠️ AddLandmark ALSO rolls the def's mutatorChances and comboLandmarkMutators " +
                "onto the tile, so this is a mutator write as well - the read-back shows both. " +
                "⚠️ It no-ops entirely without Odyssey. " +
                "🔴 AddLandmark itself does NOT consult LandmarkDef.IsValidTile (read from the " +
                "1.6 source) - it assigns unconditionally and OVERWRITES any landmark already " +
                "on the tile. IsValidTile is worldgen's gate, and it rejects a tile holding a " +
                "SETTLEMENT, an existing landmark, an impassable biome or hilliness, or a " +
                "mutator with preventsLandmarks. Place landmarks BEFORE settlements, and leave " +
                "checkValid=true so that verdict is reported before this tool overrides it. " +
                "'forced' only bypasses IsValidTile for the def's REQUIRED mutator chances.",
            ResultDescription = "success, added, removed, validity[], and a read-back per tile.")]
        public static async Task<object> WorldLandmarksSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'add' or 'remove'.")] string action = "add",
            [ToolParameter(Description = "LandmarkDef name. Required for 'add'.")] string def = null,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Bypass LandmarkDef validity (AddLandmark 'forced').")] bool forced = false,
            [ToolParameter(Description = "Report IsValidTile for each tile before acting.")] bool checkValid = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                if (!ModsConfig.OdysseyActive)
                    return Fail("Odyssey is not active. Landmarks do not exist in this game - AddLandmark would no-op silently.");

                var wl = Find.World.landmarks;
                if (wl == null) return Fail("No landmark manager on this world.");
                bool add = string.Equals(action, "add", StringComparison.OrdinalIgnoreCase);
                bool rem = string.Equals(action, "remove", StringComparison.OrdinalIgnoreCase);
                if (!add && !rem) return Fail("action must be add|remove.");

                LandmarkDef ld = null;
                if (add)
                {
                    if (string.IsNullOrEmpty(def)) return Fail("Give a LandmarkDef for 'add'.");
                    ld = DefDatabase<LandmarkDef>.GetNamedSilentFail(def.Trim());
                    if (ld == null) return Fail("No LandmarkDef '" + def + "'.", DefSuggestions<LandmarkDef>(def));
                }

                var ids = new List<int>();
                foreach (var part in (tiles ?? "").Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (ids.Count == 0) return Fail("Give 'tiles'.");

                int added = 0, removed = 0;
                var validity = new List<object>(); var errors = new List<string>();
                var surface = Find.WorldGrid.Surface;

                foreach (var id in ids)
                {
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t == null) { errors.Add(e); continue; }
                    PlanetTile pt = new PlanetTile(id, surface);

                    if (add && checkValid)
                    {
                        bool ok = false; string why = null;
                        try { ok = ld.IsValidTile(pt, surface, false); }
                        catch (Exception ex) { why = ex.GetType().Name + ": " + ex.Message; }
                        bool hasSettlement = Find.WorldObjects != null && Find.WorldObjects.AnySettlementBaseAtOrAdjacent(pt);
                        validity.Add(new { tile = id, isValidTile = ok, settlementAtOrAdjacent = hasSettlement, error = why });
                    }

                    try
                    {
                        if (add) { wl.AddLandmark(ld, pt, surface, forced); if (wl[pt] != null) added++; }
                        else { if (wl[pt] != null) { wl.RemoveLandmark(pt); removed++; } }
                    }
                    catch (Exception ex) { errors.Add("tile " + id + ": " + ex.GetType().Name + ": " + ex.Message); }
                }

                var back = new List<object>();
                foreach (var id in ids)
                {
                    if (back.Count >= 8) break;
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t != null) back.Add(MutatorRow(t, id));
                }
                return (object)new
                {
                    success = true, action, def, added, removed, forced,
                    validity, errors,
                    note = "AddLandmark also rolls the def's mutators onto the tile - see the read-back. Call jawa/world_commit.",
                    tiles = back, ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  W6 - G5 WORLD OBJECTS (settlements and everything else on the globe)
        //
        //  Creation is TWO steps and the second is easy to forget:
        //     var wo = WorldObjectMaker.MakeWorldObject(def);  // def, ID, PostMake
        //     wo.Tile = tile; wo.SetFaction(f); ((Settlement)wo).Name = "...";
        //     Find.WorldObjects.Add(wo);                       // placement
        //
        //  🔴 A Settlement whose faction is NULL on load is DESTROYED with a
        //     warning. Our 72 holdings must each carry a live faction before
        //     the owner saves, or they vanish on his next load and he will not
        //     find out until then. world_objects_validate checks exactly this.
        //  §12 rules these OVERWRITE: re-Tile what vanilla placed rather than
        //  deleting and remaking, so ids and references stay intact.
        // ================================================================

        private static object WorldObjectRow(WorldObject o)
        {
            var st = o as Settlement;
            return new
            {
                id = o.ID,
                def = o.def != null ? o.def.defName : null,
                label = o.Label,
                tile = o.Tile.tileId,
                layer = o.Tile.Layer != null && o.Tile.Layer.Def != null ? o.Tile.Layer.Def.defName : null,
                faction = o.Faction != null ? o.Faction.def.defName : null,
                factionName = o.Faction != null ? o.Faction.Name : null,
                hasFaction = o.Faction != null,
                isSettlement = st != null,
                name = st != null ? st.Name : null,
                namedByPlayer = st != null && st.namedByPlayer,
                spawned = o.Spawned,
            };
        }

        [Tool(
            "jawa/world_objects_get",
            Description =
                "List the world objects on the planet - settlements, sites, caravans and the " +
                "rest. Reports id, def, tile, faction and (for settlements) the name and " +
                "whether the player named it. Filter by def, by faction, or by tile. " +
                "Use onlyMissingFaction=true to find the ones that will be DESTROYED on the " +
                "next load: a Settlement with a null faction does not survive Scribe.",
            ResultDescription = "success, count, byDef{}, byFaction{}, objects[].")]
        public static async Task<object> WorldObjectsGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only this WorldObjectDef.")] string def = null,
            [ToolParameter(Description = "Only this faction defName.")] string faction = null,
            [ToolParameter(Description = "Only objects on these comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Only objects with a NULL faction - these die on load.")] bool onlyMissingFaction = false,
            [ToolParameter(Description = "Max rows. Default 100.")] int limit = 100)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldObjects == null) return Fail("No world is loaded.");

                var want = new HashSet<int>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) want.Add(v); }

                var byDef = new Dictionary<string, int>();
                var byFaction = new Dictionary<string, int>();
                var outp = new List<object>(); int total = 0, missingFaction = 0;

                foreach (var o in Find.WorldObjects.AllWorldObjects)
                {
                    if (o == null) continue;
                    var dn = o.def != null ? o.def.defName : "(null)";
                    var fn = o.Faction != null ? o.Faction.def.defName : "(none)";
                    if (o.Faction == null) missingFaction++;

                    if (!string.IsNullOrEmpty(def) && !dn.Equals(def, StringComparison.OrdinalIgnoreCase)) continue;
                    if (!string.IsNullOrEmpty(faction) && !fn.Equals(faction, StringComparison.OrdinalIgnoreCase)) continue;
                    if (want.Count > 0 && !want.Contains(o.Tile.tileId)) continue;
                    if (onlyMissingFaction && o.Faction != null) continue;

                    total++;
                    int c;
                    byDef.TryGetValue(dn, out c); byDef[dn] = c + 1;
                    byFaction.TryGetValue(fn, out c); byFaction[fn] = c + 1;
                    if (outp.Count < Math.Max(1, limit)) outp.Add(WorldObjectRow(o));
                }

                return (object)new
                {
                    success = true,
                    count = total,
                    returned = outp.Count,
                    allObjectsOnPlanet = Find.WorldObjects.AllWorldObjects.Count,
                    settlements = Find.WorldObjects.Settlements.Count,
                    objectsWithNoFaction = missingFaction,
                    factionWarning = missingFaction > 0
                        ? "A Settlement with a null faction is DESTROYED on load. Fix before saving."
                        : null,
                    byDef = byDef.OrderByDescending(k => k.Value).ToDictionary(k => k.Key, k => k.Value),
                    byFaction = byFaction.OrderByDescending(k => k.Value).ToDictionary(k => k.Key, k => k.Value),
                    objects = outp,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_objects_set",
            Description =
                "Re-site, re-faction or rename EXISTING world objects, addressed by their " +
                "object id. This is the OVERWRITE route §12 rules for our 72 holdings: move " +
                "what vanilla already placed rather than deleting and remaking it, so ids and " +
                "the reference graph stay intact. Any field left null is untouched. " +
                "Setting a faction that does not exist is refused rather than nulling it.",
            ResultDescription = "success, changed, objects[] read back.")]
        public static async Task<object> WorldObjectsSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated world object ids.")] string ids = null,
            [ToolParameter(Description = "Move to this tile id. -1 leaves it.")] int tile = -1,
            [ToolParameter(Description = "Faction defName to assign.")] string faction = null,
            [ToolParameter(Description = "New name (settlements only).")] string name = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldObjects == null) return Fail("No world is loaded.");

                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = ResolveLiveFactionOfDefOrFail(fd, faction, out var ambFail);
                    if (ambFail != null) return ambFail;
                    if (fac == null)
                        return Fail("FactionDef '" + faction + "' exists but no such faction was generated in THIS world. " +
                                    "Refusing rather than leaving the object factionless - a null-faction Settlement is destroyed on load.");
                }

                var want = new HashSet<int>();
                foreach (var part in (ids ?? "").Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) want.Add(v); }
                if (want.Count == 0) return Fail("Give 'ids'.");

                if (tile >= 0 && (Find.WorldGrid == null || tile >= Find.WorldGrid.TilesCount))
                    return Fail("Tile " + tile + " out of range.");

                int changed = 0; var back = new List<object>(); var errors = new List<string>();
                foreach (var o in Find.WorldObjects.AllWorldObjects.ToList())
                {
                    if (o == null || !want.Contains(o.ID)) continue;
                    try
                    {
                        if (tile >= 0) o.Tile = new PlanetTile(tile, Find.WorldGrid.Surface);
                        if (fac != null) o.SetFaction(fac);
                        if (name != null)
                        {
                            var st = o as Settlement;
                            if (st != null) st.Name = name;
                            else errors.Add("Object " + o.ID + " is not a Settlement; name ignored.");
                        }
                        changed++;
                        back.Add(WorldObjectRow(o));
                    }
                    catch (Exception e) { errors.Add("Object " + o.ID + ": " + e.GetType().Name + ": " + e.Message); }
                }

                return (object)new
                {
                    success = true, changed, requested = want.Count, errors,
                    note = "Call jawa/world_commit - FastTileFinder caches settlement tiles.",
                    objects = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_objects_validate",
            Description =
                "Check every world object for the faults that only show up after a save/load: " +
                "a NULL faction (a Settlement with one is destroyed by Scribe with a warning), " +
                "an invalid or out-of-range tile, two settlements stacked on one tile, and " +
                "settlements sitting on impassable or water-covered terrain. Read-only. " +
                "Run this BEFORE the owner saves, because afterwards the objects are simply gone.",
            ResultDescription = "success, nullFaction[], badTile[], stacked[], onWater[], onImpassable[].")]
        public static async Task<object> WorldObjectsValidate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Max examples per category. Default 15.")] int limit = 15)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldObjects == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid;
                var nullFac = new List<object>(); var badTile = new List<object>();
                var onWater = new List<object>(); var onImpass = new List<object>();
                var stacked = new List<object>();
                var perTile = new Dictionary<int, int>();
                int nullFacN = 0, badTileN = 0, waterN = 0, impassN = 0, stackedN = 0;

                foreach (var o in Find.WorldObjects.AllWorldObjects)
                {
                    if (o == null) continue;
                    bool isSettlement = o is Settlement;

                    if (o.Faction == null && o.def != null && o.def.canHaveFaction && isSettlement)
                    {
                        nullFacN++;
                        if (nullFac.Count < limit) nullFac.Add(WorldObjectRow(o));
                    }

                    int tid = o.Tile.tileId;
                    if (tid < 0 || grid == null || tid >= grid.TilesCount)
                    {
                        badTileN++;
                        if (badTile.Count < limit) badTile.Add(WorldObjectRow(o));
                        continue;
                    }

                    if (isSettlement)
                    {
                        int c; perTile.TryGetValue(tid, out c); perTile[tid] = c + 1;
                        var t = grid[tid] as SurfaceTile;
                        if (t != null)
                        {
                            if (t.WaterCovered) { waterN++; if (onWater.Count < limit) onWater.Add(WorldObjectRow(o)); }
                            if (t.hilliness == Hilliness.Impassable || (t.PrimaryBiome != null && t.PrimaryBiome.impassable))
                            { impassN++; if (onImpass.Count < limit) onImpass.Add(WorldObjectRow(o)); }
                        }
                    }
                }

                // 🔴 `stacked` is capped at `limit` for the examples list; the COUNT must
                // not be, or a planet with 200 stacked tiles reads as exactly `limit` of
                // them - the same saturated-instrument bug already fixed for asymmetric/
                // nonAdjacent/hiddenByBiome in jawa/world_links_validate.
                foreach (var kv in perTile)
                    if (kv.Value > 1)
                    {
                        stackedN++;
                        if (stacked.Count < limit) stacked.Add(new { tile = kv.Key, settlements = kv.Value });
                    }

                return (object)new
                {
                    success = true,
                    totalObjects = Find.WorldObjects.AllWorldObjects.Count,
                    settlements = Find.WorldObjects.Settlements.Count,
                    nullFactionSettlements = nullFacN,
                    nullFactionNote = "A Settlement with a null faction is DESTROYED on load with a warning. This is the one fault that is invisible until it is too late.",
                    badTileCount = badTileN,
                    settlementsOnWater = waterN,
                    settlementsOnImpassable = impassN,
                    stackedTiles = stackedN,
                    nullFaction = nullFac, badTile = badTile,
                    onWater = onWater, onImpassable = onImpass, stacked,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  G4 - NAMED REGIONS (WorldFeature). Our 24 regions live here.
        //
        //  🔑 Tile membership is stored ON THE TILE (Tile.feature), not in the
        //     feature. Assigning a region = writing `feature` on each member tile.
        //  ⚠️ WorldFeature.Tiles is a FULL-GRID SCAN - O(n) per feature. Never
        //     call it in a loop over 24 regions; this file builds one map in a
        //     single pass instead.
        //  ⭐ drawAngle is NEVER set by vanilla's generator (stays 0). We get
        //     label rotation the base game does not use.
        //  🔑 After renaming or moving a label, set Find.WorldFeatures.textsCreated
        //     = false or the OLD text keeps drawing - that is the commit step for
        //     features, and it is separate from the draw-layer regeneration.
        // ================================================================

        [Tool(
            "jawa/world_features_get",
            Description =
                "List the planet's named regions (WorldFeature) - the text drawn across the " +
                "globe. Reports uniqueID, def, name, drawCenter, drawAngle, maxDrawSizeInTiles " +
                "and the tile COUNT of each. Tile membership lives on Tile.feature, so the " +
                "counts are computed in ONE pass over the grid rather than per-feature " +
                "(WorldFeature.Tiles is a full-grid scan and would be O(n*features)).",
            ResultDescription = "success, count, features[] with tileCount each.")]
        public static async Task<object> WorldFeaturesGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Include up to this many member tile ids per feature. Default 0.")] int sampleTiles = 0,
            [ToolParameter(Description = "Max features. Default 100.")] int limit = 100)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var wf = Find.World.features;
                if (wf == null || wf.features == null)
                    return (object)new { success = true, count = 0, features = new List<object>(), note = "No feature manager." };

                var grid = Find.WorldGrid; int n = grid.TilesCount;
                var counts = new Dictionary<int, int>();
                var samples = new Dictionary<int, List<int>>();
                for (int i = 0; i < n; i++)
                {
                    var t = grid[i];
                    if (t == null || t.feature == null) continue;
                    int id = t.feature.uniqueID;
                    int c; counts.TryGetValue(id, out c); counts[id] = c + 1;
                    if (sampleTiles > 0)
                    {
                        List<int> l;
                        if (!samples.TryGetValue(id, out l)) { l = new List<int>(); samples[id] = l; }
                        if (l.Count < sampleTiles) l.Add(i);
                    }
                }

                var outp = new List<object>();
                foreach (var f in wf.features)
                {
                    if (f == null) continue;
                    if (outp.Count >= Math.Max(1, limit)) break;
                    int c; counts.TryGetValue(f.uniqueID, out c);
                    List<int> sm; samples.TryGetValue(f.uniqueID, out sm);
                    outp.Add(new
                    {
                        uniqueID = f.uniqueID,
                        def = f.def != null ? f.def.defName : null,
                        name = f.name,
                        tileCount = c,
                        drawCenter = new { x = f.drawCenter.x, y = f.drawCenter.y, z = f.drawCenter.z },
                        drawAngle = f.drawAngle,
                        maxDrawSizeInTiles = f.maxDrawSizeInTiles,
                        effectiveDrawSize = f.EffectiveDrawSize,
                        alpha = f.alpha,
                        layer = f.layer != null && f.layer.Def != null ? f.layer.Def.defName : null,
                        sampleTiles = sm,
                    });
                }
                return (object)new
                {
                    success = true,
                    count = wf.features.Count,
                    returned = outp.Count,
                    textsCreated = wf.textsCreated,
                    tilesWithNoFeature = n - counts.Values.Sum(),
                    features = outp,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_features_set",
            Description =
                "Create, rename, reposition or delete a named region, and assign tiles to it. " +
                "Membership is written to Tile.feature on each named tile. " +
                "drawAngle rotates the label - vanilla never sets it, so this is control the " +
                "base game does not expose. drawCenter is a world-space Vector3; pass " +
                "centerOnTile to have it computed from a tile instead. " +
                "Sets Find.WorldFeatures.textsCreated=false so the label text is rebuilt - " +
                "without that the OLD text keeps drawing however the data changed.",
            ResultDescription = "success, action, featureId, tilesAssigned, feature read back.")]
        public static async Task<object> WorldFeaturesSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'create', 'update', 'assign' or 'delete'.")] string action = "update",
            [ToolParameter(Description = "Existing feature uniqueID. Required except for 'create'.")] int featureId = -1,
            [ToolParameter(Description = "FeatureDef name. Required for 'create'.")] string def = null,
            [ToolParameter(Description = "Region name.")] string name = null,
            [ToolParameter(Description = "Label rotation in degrees.")] float? drawAngle = null,
            [ToolParameter(Description = "Label size in tiles.")] float? maxDrawSizeInTiles = null,
            [ToolParameter(Description = "Put the label at this tile's centre. -1 leaves it.")] int centerOnTile = -1,
            [ToolParameter(Description = "Comma-separated tile ids to assign to this feature.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to' to assign.")] string range = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var wf = Find.World.features;
                if (wf == null || wf.features == null) return Fail("No feature manager on this world.");
                var grid = Find.WorldGrid;

                bool create = string.Equals(action, "create", StringComparison.OrdinalIgnoreCase);
                bool del = string.Equals(action, "delete", StringComparison.OrdinalIgnoreCase);

                WorldFeature f = null;
                if (create)
                {
                    if (string.IsNullOrEmpty(def)) return Fail("Give a FeatureDef for 'create'.");
                    var fd = DefDatabase<FeatureDef>.GetNamedSilentFail(def.Trim());
                    if (fd == null) return Fail("No FeatureDef '" + def + "'.", DefSuggestions<FeatureDef>(def));
                    f = new WorldFeature(fd, grid.Surface);
                    f.name = name ?? fd.LabelCap;
                    wf.features.Add(f);
                }
                else
                {
                    f = wf.features.FirstOrDefault(x => x != null && x.uniqueID == featureId);
                    if (f == null) return Fail("No feature with uniqueID " + featureId + ".");
                }

                int assigned = 0;
                if (del)
                {
                    // Clear membership first or tiles keep a dangling reference.
                    int n = grid.TilesCount;
                    for (int i = 0; i < n; i++)
                    {
                        var t = grid[i];
                        if (t != null && t.feature == f) { t.feature = null; assigned++; }
                    }
                    wf.features.Remove(f);
                    wf.textsCreated = false;
                    return (object)new
                    {
                        success = true, action = "delete", featureId,
                        tilesCleared = assigned,
                        note = "Membership cleared before removal so no tile keeps a dangling feature reference.",
                        ticksGame = TicksGameSafe(),
                    };
                }

                if (name != null) f.name = name;
                if (drawAngle.HasValue) f.drawAngle = drawAngle.Value;
                if (maxDrawSizeInTiles.HasValue) f.maxDrawSizeInTiles = maxDrawSizeInTiles.Value;
                if (centerOnTile >= 0 && centerOnTile < grid.TilesCount)
                    f.drawCenter = grid.GetTileCenter(centerOnTile);

                var ids = new List<int>();
                if (!string.IsNullOrEmpty(tiles))
                    foreach (var part in tiles.Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                if (!string.IsNullOrEmpty(range))
                {
                    var bits = range.Split('-'); int a, b;
                    if (bits.Length == 2 && int.TryParse(bits[0].Trim(), out a) && int.TryParse(bits[1].Trim(), out b))
                        for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
                }
                foreach (var id in ids)
                {
                    string e; var t = SurfaceTileAt(id, out e);
                    if (t == null) continue;
                    t.feature = f; assigned++;
                }

                wf.textsCreated = false;   // rebuild the drawn text, or the old label persists

                int count = 0;
                { int n = grid.TilesCount; for (int i = 0; i < n; i++) { var t = grid[i]; if (t != null && t.feature == f) count++; } }

                return (object)new
                {
                    success = true, action = create ? "create" : "update",
                    featureId = f.uniqueID,
                    tilesAssigned = assigned,
                    feature = new
                    {
                        uniqueID = f.uniqueID,
                        def = f.def != null ? f.def.defName : null,
                        name = f.name,
                        tileCount = count,
                        drawAngle = f.drawAngle,
                        maxDrawSizeInTiles = f.maxDrawSizeInTiles,
                        drawCenter = new { x = f.drawCenter.x, y = f.drawCenter.y, z = f.drawCenter.z },
                    },
                    note = "textsCreated set false so the label rebuilds. Call jawa/world_commit for the terrain layers.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  W7 - G6 WORLD INFO
        //  🔴 overallPopulation and landmarkDensity are NOT SCRIBED - they do
        //  not survive save/load. The setter REFUSES them unless forced, and
        //  says so, rather than letting a caller build on a value that evaporates.
        // ================================================================
        [Tool(
            "jawa/world_info_get",
            Description =
                "Read Find.World.info: planet name, seed, coverage, overall rainfall / " +
                "temperature / population, landmark density, initial map size, pollution and " +
                "the FactionDef list the world was generated with. Also reports which fields " +
                "do NOT survive a save/load.",
            ResultDescription = "success, info{}, notPersisted[].")]
        public static async Task<object> WorldInfoGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.World.info == null) return Fail("No world is loaded.");
                var w = Find.World.info;
                return (object)new
                {
                    success = true,
                    info = new
                    {
                        name = w.name,
                        seedString = w.seedString,
                        seed = w.Seed,
                        planetCoverage = w.planetCoverage,
                        persistentRandomValue = w.persistentRandomValue,
                        overallRainfall = w.overallRainfall.ToString(),
                        overallTemperature = w.overallTemperature.ToString(),
                        overallPopulation = w.overallPopulation.ToString(),
                        landmarkDensity = w.landmarkDensity.ToString(),
                        initialMapSize = new { x = w.initialMapSize.x, y = w.initialMapSize.y, z = w.initialMapSize.z },
                        pollution = w.pollution,
                        factionCount = w.factions != null ? w.factions.Count : 0,
                        factions = w.factions != null ? w.factions.Select(f => f != null ? f.defName : null).ToList() : null,
                    },
                    tilesCount = Find.WorldGrid != null ? Find.WorldGrid.TilesCount : -1,
                    notPersisted = new List<string> { "overallPopulation", "landmarkDensity" },
                    notPersistedNote = "WorldInfo.ExposeData does not scribe these two. Whatever they read now, they revert on the next load.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_info_set",
            Description =
                "Rename the planet or change its recorded generation parameters. " +
                "🔴 overallPopulation and landmarkDensity are NOT SCRIBED by " +
                "WorldInfo.ExposeData - they revert on the next load - so this tool REFUSES " +
                "them unless allowNonPersistent=true, and flags them in the result when it " +
                "does write them. Changing seedString or planetCoverage does NOT regenerate " +
                "anything; it only edits the label the save carries.",
            ResultDescription = "success, changed[], refused[], info read back.")]
        public static async Task<object> WorldInfoSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Planet name.")] string name = null,
            [ToolParameter(Description = "Seed string (label only - regenerates nothing).")] string seedString = null,
            [ToolParameter(Description = "Planet-wide pollution 0-1.")] float? pollution = null,
            [ToolParameter(Description = "overallPopulation - NOT PERSISTED.")] string overallPopulation = null,
            [ToolParameter(Description = "landmarkDensity - NOT PERSISTED.")] string landmarkDensity = null,
            [ToolParameter(Description = "Permit writing the two non-persisted fields.")] bool allowNonPersistent = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.World.info == null) return Fail("No world is loaded.");
                var w = Find.World.info;
                var changed = new List<string>(); var refused = new List<string>();

                if (name != null) { w.name = name; changed.Add("name"); }
                if (seedString != null) { w.seedString = seedString; changed.Add("seedString"); }
                // Clamped: WorldInfo.pollution is the planet-wide 0-1 dial the generator reads.
                if (pollution.HasValue)
                {
                    float p = Mathf.Clamp01(pollution.Value);
                    w.pollution = p;
                    changed.Add(p == pollution.Value ? "pollution" : "pollution (clamped " + pollution.Value + " -> " + p + ")");
                }

                // 🔴 Same shape as the fix on jawa/faction_relations_set: Enum.Parse ALSO
                // accepts a bare number and returns a value the enum never declared -
                // "99" parses as (OverallPopulation)99. Enum.TryParse alone would have
                // let that through and reported success off a read-back that just
                // echoes the same undefined value back. Not scribed, so it cannot
                // corrupt a save, but it is still live game state other code reads
                // this session (population/storyteller scaling) - refuse it instead.
                if (overallPopulation != null)
                {
                    if (!allowNonPersistent) refused.Add("overallPopulation (not scribed - pass allowNonPersistent=true)");
                    else
                    {
                        OverallPopulation parsedPop;
                        if (Enum.TryParse(overallPopulation.Trim(), true, out parsedPop)
                            && Enum.IsDefined(typeof(OverallPopulation), parsedPop))
                        { w.overallPopulation = parsedPop; changed.Add("overallPopulation [NOT PERSISTED]"); }
                        else refused.Add("overallPopulation: '" + overallPopulation + "' is not an OverallPopulation value");
                    }
                }
                if (landmarkDensity != null)
                {
                    if (!allowNonPersistent) refused.Add("landmarkDensity (not scribed - pass allowNonPersistent=true)");
                    else
                    {
                        LandmarkDensity parsedDen;
                        if (Enum.TryParse(landmarkDensity.Trim(), true, out parsedDen)
                            && Enum.IsDefined(typeof(LandmarkDensity), parsedDen))
                        { w.landmarkDensity = parsedDen; changed.Add("landmarkDensity [NOT PERSISTED]"); }
                        else refused.Add("landmarkDensity: '" + landmarkDensity + "' is not a LandmarkDensity value");
                    }
                }

                return (object)new
                {
                    success = true, changed, refused,
                    info = new { name = w.name, seedString = w.seedString, pollution = w.pollution,
                                 overallPopulation = w.overallPopulation.ToString(),
                                 landmarkDensity = w.landmarkDensity.ToString() },
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  W8 - G8 THE SANITY LINTER
        //
        //  The owner's words: evaluate "how sane is this planet?", not "did the
        //  script run". It runs IN the engine against the live grid so it sees
        //  what the game sees - not what an offline array says.
        //
        //  🔑 The river rule is CONDITIONAL by the owner's ruling: high-
        //  accumulation TRUNKS must reach a sea; low-accumulation rivers MAY
        //  die in playas and salt pans. So river components are judged by their
        //  biggest river def, not by existing. A linter that cried wolf on 44
        //  legitimate rivers would be worse than no linter.
        // ================================================================
        [Tool(
            "jawa/world_lint",
            Description =
                "Sweep the live planet for things that read as WRONG rather than things that " +
                "failed to run - the owner's sanity pass. Checks: marine mutators on tiles " +
                "that are not coastal by real adjacency; water biome on raised land and land " +
                "biome on submerged tiles; single-tile islands; river systems that reach no " +
                "sea (judged by their largest river def, because low-accumulation rivers are " +
                "ALLOWED to die inland); settlements on water, on impassable terrain, stacked, " +
                "or with no road; and lush biomes sitting off-river when a lush list is given. " +
                "Read-only. Calibrate it on a world you already know is broken before " +
                "trusting a clean sheet.",
            ResultDescription = "success, checks{} each with a count and examples[].")]
        public static async Task<object> WorldLint(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Mutators implying water adjacency. Default 'Coast'.")]
            string marineMutators = "Coast",
            [ToolParameter(Description = "River defs counted as TRUNKS that must reach a sea. Default 'HugeRiver,LargeRiver'.")]
            string trunkRivers = "HugeRiver,LargeRiver",
            [ToolParameter(Description = "Comma-separated biome defNames that must sit on or beside a river. Empty skips the check.")]
            string lushBiomes = null,
            [ToolParameter(Description = "Max examples per check. Default 12.")] int limit = 12)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid; int n = grid.TilesCount;

                var marine = new HashSet<string>((marineMutators ?? "").Split(',').Select(x => x.Trim()).Where(x => x.Length > 0), StringComparer.OrdinalIgnoreCase);
                var trunks = new HashSet<string>((trunkRivers ?? "").Split(',').Select(x => x.Trim()).Where(x => x.Length > 0), StringComparer.OrdinalIgnoreCase);
                var lush = new HashSet<string>((lushBiomes ?? "").Split(',').Select(x => x.Trim()).Where(x => x.Length > 0), StringComparer.OrdinalIgnoreCase);

                var staleMarine = new List<object>(); int staleMarineN = 0;
                var waterBiomeOnLand = new List<object>(); int wbolN = 0; int lakesAboveSeaLevelN = 0;
                var landBiomeSubmerged = new List<object>(); int lbsN = 0;
                var lonelyIsland = new List<object>(); int islandN = 0;
                var lushOffRiver = new List<object>(); int lushN = 0;

                var nbrs = new List<PlanetTile>();
                var water = new bool[n];
                var hasRiver = new bool[n];
                for (int i = 0; i < n; i++)
                {
                    var t = grid[i] as SurfaceTile;
                    if (t == null) continue;
                    water[i] = t.WaterCovered;
                    hasRiver[i] = t.potentialRivers != null && t.potentialRivers.Count > 0;
                }

                for (int i = 0; i < n; i++)
                {
                    var t = grid[i] as SurfaceTile;
                    if (t == null) continue;
                    var b = t.PrimaryBiome;
                    bool coastal = SafeIsCoastal(i);

                    if (t.mutatorsNullable != null)
                        foreach (var m in t.mutatorsNullable)
                            if (m != null && marine.Contains(m.defName) && !coastal)
                            {
                                staleMarineN++;
                                if (staleMarine.Count < limit)
                                    staleMarine.Add(new { tile = i, mutator = m.defName, biome = b != null ? b.defName : null, elevation = t.elevation });
                            }

                    // A water biome on a raised tile, or land biome under water, is the
                    // classic repaint artefact: the biome field and the elevation field
                    // were written by different passes that never read each other.
                    if (b != null)
                    {
                        // 🔴 Lake is NOT in this test, deliberately - corrected
                        // 2026-08-20 after it produced 312 findings on the Ash'karr
                        // import, exactly the CSV's Lake count. A lake at positive
                        // elevation is ordinary geography; vanilla lakes sit on
                        // land. Only Ocean and SeaIce are genuinely sea level.
                        // Lakes are counted separately below and do NOT score.
                        bool biomeIsWater = b.defName == "Ocean" || b.defName == "SeaIce";
                        if (b.defName == "Lake" && t.elevation > 0f) lakesAboveSeaLevelN++;
                        if (biomeIsWater && t.elevation > 0f)
                        {
                            wbolN++;
                            if (waterBiomeOnLand.Count < limit) waterBiomeOnLand.Add(new { tile = i, biome = b.defName, elevation = t.elevation });
                        }
                        // 🔴 Lake is excluded HERE TOO - corrected 2026-08-21
                        // (LINT_EXCLUDE_LAKE_SUBMERGED_1). The 2026-08-20 fix above was
                        // applied to waterBiomeOnRaisedLand and lakesAboveSeaLevel and
                        // never to this check, so sinking the Scald to -30 simply moved
                        // its 312 tiles from a check that scores zero into one that
                        // scores. A lake BELOW its own shoreline is the definition of a
                        // lake. ⛔ Do not "simplify" this by adding Lake to
                        // biomeIsWater - that flips waterBiomeOnRaisedLand back on for
                        // every ordinary high-altitude lake, which is what 08-20 fixed.
                        if (!biomeIsWater && b.defName != "Lake" && t.elevation <= 0f)
                        {
                            lbsN++;
                            if (landBiomeSubmerged.Count < limit) landBiomeSubmerged.Add(new { tile = i, biome = b.defName, elevation = t.elevation });
                        }
                        if (lush.Count > 0 && lush.Contains(b.defName))
                        {
                            nbrs.Clear(); grid.GetTileNeighbors(i, nbrs);
                            bool nearRiver = hasRiver[i] || nbrs.Any(x => x.tileId >= 0 && x.tileId < n && hasRiver[x.tileId]);
                            if (!nearRiver)
                            {
                                lushN++;
                                if (lushOffRiver.Count < limit) lushOffRiver.Add(new { tile = i, biome = b.defName });
                            }
                        }
                    }

                    if (!water[i])
                    {
                        nbrs.Clear(); grid.GetTileNeighbors(i, nbrs);
                        if (nbrs.Count > 0 && nbrs.All(x => x.tileId >= 0 && x.tileId < n && water[x.tileId]))
                        {
                            islandN++;
                            if (lonelyIsland.Count < limit) lonelyIsland.Add(new { tile = i, biome = b != null ? b.defName : null, elevation = t.elevation });
                        }
                    }
                }

                // River SYSTEMS, not river tiles: flood the river graph into components,
                // then ask whether each component ever touches water. A component whose
                // biggest def is a trunk and never reaches a sea is the real defect.
                var seen = new bool[n];
                int systems = 0, systemsNoSea = 0, trunkSystemsNoSea = 0;
                var orphanTrunks = new List<object>();
                var stack = new List<int>();
                for (int i = 0; i < n; i++)
                {
                    if (seen[i] || !hasRiver[i]) continue;
                    systems++;
                    stack.Clear(); stack.Add(i); seen[i] = true;
                    bool touchesSea = false; string biggest = null; int biggestRank = -1; int size = 0; int sample = i;
                    while (stack.Count > 0)
                    {
                        int cur = stack[stack.Count - 1]; stack.RemoveAt(stack.Count - 1);
                        size++;
                        var t = grid[cur] as SurfaceTile;
                        if (t == null) continue;
                        nbrs.Clear(); grid.GetTileNeighbors(cur, nbrs);
                        foreach (var x in nbrs)
                            if (x.tileId >= 0 && x.tileId < n && water[x.tileId]) { touchesSea = true; break; }
                        if (t.potentialRivers != null)
                            foreach (var l in t.potentialRivers)
                            {
                                if (l.river != null)
                                {
                                    int rank = trunks.Contains(l.river.defName) ? 2 : 1;
                                    if (rank > biggestRank) { biggestRank = rank; biggest = l.river.defName; }
                                }
                                int far = l.neighbor.tileId;
                                if (far >= 0 && far < n && hasRiver[far] && !seen[far]) { seen[far] = true; stack.Add(far); }
                            }
                    }
                    if (!touchesSea)
                    {
                        systemsNoSea++;
                        if (biggestRank == 2)
                        {
                            trunkSystemsNoSea++;
                            if (orphanTrunks.Count < limit)
                                orphanTrunks.Add(new { sampleTile = sample, systemTiles = size, largestRiver = biggest });
                        }
                    }
                }

                // Settlements
                var settOnWater = new List<object>(); var settImpass = new List<object>();
                var settNoRoad = new List<object>(); var stacked = new List<object>();
                int sW = 0, sI = 0, sNR = 0, sStack = 0;
                var perTile = new Dictionary<int, int>();
                if (Find.WorldObjects != null)
                    foreach (var st in Find.WorldObjects.Settlements)
                    {
                        if (st == null) continue;
                        int tid = st.Tile.tileId;
                        if (tid < 0 || tid >= n) continue;
                        int c; perTile.TryGetValue(tid, out c); perTile[tid] = c + 1;
                        var t = grid[tid] as SurfaceTile;
                        if (t == null) continue;
                        if (t.WaterCovered) { sW++; if (settOnWater.Count < limit) settOnWater.Add(new { tile = tid, name = st.Name, faction = st.Faction != null ? st.Faction.def.defName : null }); }
                        if (t.hilliness == Hilliness.Impassable || (t.PrimaryBiome != null && t.PrimaryBiome.impassable))
                        { sI++; if (settImpass.Count < limit) settImpass.Add(new { tile = tid, name = st.Name }); }
                        bool road = t.potentialRoads != null && t.potentialRoads.Count > 0;
                        if (!road) { sNR++; if (settNoRoad.Count < limit) settNoRoad.Add(new { tile = tid, name = st.Name, faction = st.Faction != null ? st.Faction.def.defName : null }); }
                    }
                // 🔴 `stacked` is capped at `limit` for the examples list; the COUNT must
                // not be, or a planet with 200 stacked tiles reads as exactly `limit` of
                // them - the same saturated-instrument bug already fixed for asymmetric/
                // nonAdjacent/hiddenByBiome in jawa/world_links_validate.
                foreach (var kv in perTile)
                    if (kv.Value > 1)
                    {
                        sStack++;
                        if (stacked.Count < limit) stacked.Add(new { tile = kv.Key, settlements = kv.Value });
                    }

                int totalFindings = staleMarineN + wbolN + lbsN + islandN + lushN + trunkSystemsNoSea + sW + sI + sNR + sStack;

                return (object)new
                {
                    success = true,
                    tilesScanned = n,
                    totalFindings,
                    verdict = totalFindings == 0
                        ? "CLEAN - and treat that with suspicion until this linter has been calibrated on a world you KNOW is broken."
                        : totalFindings + " findings across " + n + " tiles.",
                    checks = new
                    {
                        staleMarineMutators = new { count = staleMarineN, note = "Marine mutator on a tile that is not coastal by real adjacency - the classic survivor of a repaint.", examples = staleMarine },
                        waterBiomeOnRaisedLand = new { count = wbolN, note = "Ocean or SeaIce biome with elevation > 0. Lake is EXCLUDED - a lake at altitude is ordinary geography, and including it made this check fire once per authored lake.", examples = waterBiomeOnLand },
                        lakesAboveSeaLevel = new { count = lakesAboveSeaLevelN, note = "INFORMATIONAL, scores ZERO. Lake tiles above sea level, which is normal. Here so a genuinely suspicious count is still visible.", },
                        landBiomeSubmerged = new { count = lbsN, note = "Land biome with elevation <= 0.", examples = landBiomeSubmerged },
                        singleTileIslands = new { count = islandN, note = "Land tile with every neighbour water.", examples = lonelyIsland },
                        riverSystems = new
                        {
                            total = systems,
                            reachingNoSea = systemsNoSea,
                            trunkSystemsReachingNoSea = trunkSystemsNoSea,
                            note = "Only TRUNK systems (" + string.Join("/", trunks.ToArray()) + ") are defects. Low-accumulation rivers are ALLOWED to die in playas and salt pans - owner's ruling.",
                            orphanTrunks,
                        },
                        settlementsOnWater = new { count = sW, examples = settOnWater },
                        settlementsOnImpassable = new { count = sI, examples = settImpass },
                        settlementsWithNoRoad = new { count = sNR, examples = settNoRoad },
                        stackedSettlements = new { count = sStack, examples = stacked },
                        lushBiomesOffRiver = new { count = lushN, checked_ = lush.ToList(), note = "Nile-style ruling: a 1-2 tile lush band follows EVERY river. Lush terrain away from one is the defect.", examples = lushOffRiver },
                    },
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        [Tool(
            "jawa/world_objects_add",
            Description =
                "CREATE a new world object - a settlement, site or camp - rather than " +
                "re-siting one that already exists. Two steps, and the second is easy to " +
                "forget: WorldObjectMaker.MakeWorldObject sets def/ID/creationGameTicks and " +
                "calls PostMake, then Find.WorldObjects.Add PLACES it. " +
                "🔴 A Settlement whose faction is NULL is DESTROYED on load with only a " +
                "warning, so a factionless settlement is refused outright. " +
                "📌 §12 rules that for Ash'karr we OVERWRITE what vanilla generated rather " +
                "than adding - use jawa/world_objects_set for that. This tool is for scenes " +
                "vanilla never placed.",
            ResultDescription = "success, the created object, and the world object counts after.")]
        public static async Task<object> WorldObjectsAdd(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "WorldObjectDef, e.g. Settlement, Site, Camp.")] string def = "Settlement",
            [ToolParameter(Description = "Tile id to place it on.")] int tile = -1,
            [ToolParameter(Description = "FactionDef that owns it. Required for settlements.")] string faction = null,
            [ToolParameter(Description = "Name for a settlement. Empty lets the game name it.")] string name = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null) return Fail("No world is loaded.");
                var grid = Find.WorldGrid;
                if (tile < 0 || tile >= grid.TilesCount)
                    return Fail("Tile " + tile + " out of range 0.." + (grid.TilesCount - 1) + ".");

                var wd = DefDatabase<WorldObjectDef>.GetNamedSilentFail((def ?? "").Trim());
                if (wd == null) return Fail("No WorldObjectDef '" + def + "'.", DefSuggestions<WorldObjectDef>(def));

                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = ResolveLiveFactionOfDefOrFail(fd, faction, out var ambFail);
                    if (ambFail != null) return ambFail;
                    if (fac == null)
                        return Fail("FactionDef '" + faction + "' exists but no such faction was generated in THIS world. " +
                                    "Live: " + string.Join(", ", Find.FactionManager.AllFactionsVisible.Select(z => z.def.defName).Take(20).ToArray()));
                }

                bool isSettlement = typeof(Settlement).IsAssignableFrom(wd.worldObjectClass);
                if (isSettlement && fac == null)
                    return Fail("REFUSING: a Settlement with a null faction is DESTROYED on load, with only a warning in the log. " +
                                "Give a faction that exists in this world.");

                var already = Find.WorldObjects.ObjectsAt(tile).ToList();
                if (already.Any(o => o.def == wd))
                    return Fail("A '" + wd.defName + "' already exists on tile " + tile + ". Use jawa/world_objects_set to move or re-faction it.");

                WorldObject wo;
                try
                {
                    wo = WorldObjectMaker.MakeWorldObject(wd);
                    wo.Tile = new PlanetTile(tile, grid.Surface);
                    if (fac != null) wo.SetFaction(fac);
                    var st = wo as Settlement;
                    if (st != null && !string.IsNullOrEmpty(name)) st.Name = name;
                    Find.WorldObjects.Add(wo);          // placement is a SEPARATE step
                }
                catch (Exception e) { return Fail("Creating the world object threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    created = WorldObjectRow(wo),
                    totalWorldObjects = Find.WorldObjects.AllWorldObjects.Count,
                    totalSettlements = Find.WorldObjects.Settlements.Count,
                    note = "Run jawa/world_commit - FastTileFinder caches settlement tiles.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/world_objects_remove",
            Description =
                "Remove a world object by its id. Uses WorldObject.Destroy() where the object " +
                "supports it so the reference graph is cleaned up, rather than yanking it out " +
                "of the holder list. Read-back confirms it is gone.",
            ResultDescription = "success, removed, and the counts after.")]
        public static async Task<object> WorldObjectsRemove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated world object ids.")] string ids = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldObjects == null) return Fail("No world is loaded.");
                var want = new HashSet<int>();
                foreach (var part in (ids ?? "").Split(',')) { int v; if (int.TryParse(part.Trim(), out v)) want.Add(v); }
                if (want.Count == 0) return Fail("Give 'ids'.");

                int removed = 0; var errors = new List<string>(); var gone = new List<object>();
                var matched = new HashSet<int>();
                foreach (var o in Find.WorldObjects.AllWorldObjects.ToList())
                {
                    if (o == null || !want.Contains(o.ID)) continue;
                    matched.Add(o.ID);
                    gone.Add(WorldObjectRow(o));
                    try
                    {
                        if (!o.Destroyed) o.Destroy();
                        if (Find.WorldObjects.Contains(o)) Find.WorldObjects.Remove(o);
                        removed++;
                    }
                    catch (Exception e)
                    {
                        try { Find.WorldObjects.Remove(o); removed++; errors.Add("Destroy() threw (" + e.Message + "); removed from the holder instead"); }
                        catch (Exception e2) { errors.Add("id " + o.ID + ": " + e2.Message); }
                    }
                }

                // 🔴 The read-back the Description promises, which this tool did not
                // actually do: WorldObject.Destroy() and WorldObjectsHolder.Remove()
                // both return void and both bail out with a Log.Error rather than
                // throwing, so a method completing is not evidence the object is gone.
                var stillThere = Find.WorldObjects.AllWorldObjects
                    .Where(q => q != null && matched.Contains(q.ID))
                    .Select(q => q.ID).Distinct().ToList();
                // 🔴 And an id that matched NOTHING used to vanish without a word,
                // leaving `success: true, removed: 0` as the answer to a typo.
                var notFound = want.Where(q => !matched.Contains(q)).ToList();

                return (object)new
                {
                    success = notFound.Count == 0 && stillThere.Count == 0 && errors.Count == 0,
                    message = notFound.Count == 0 && stillThere.Count == 0
                        ? "removed " + removed + " of " + want.Count + " requested."
                        : "⚠️ removed " + removed + " of " + want.Count + " requested; "
                          + notFound.Count + " id(s) matched no world object"
                          + (stillThere.Count > 0 ? ", " + stillThere.Count + " still present after the call" : "")
                          + ".",
                    removed, requested = want.Count, errors,
                    notFound, stillPresentAfterRemoval = stillThere,
                    removedObjects = gone,
                    totalWorldObjects = Find.WorldObjects.AllWorldObjects.Count,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  FACTION RELATIONS - the pairwise matrix.
        //
        //  WHY THESE EXIST. `jawa/set_faction_relation` is hardcoded to
        //  Faction.OfPlayer and `jawa/list_factions` reports PlayerGoodwill,
        //  so before this file NOTHING on the bridge could read or write a
        //  relation between two NON-PLAYER factions. Authoring a faction web
        //  for a frozen world needs exactly that.
        //
        //  FIVE THINGS READ OUT OF 1.6 Faction.cs, EVERY ONE OF WHICH CHANGES
        //  WHAT THE TOOL MUST DO:
        //
        //  1. RelationWith(other) LOGS A RED ERROR when no record exists, and
        //     again when other == this. Enumerating a 30-faction matrix the
        //     naive way spams ~900 errors into Player.log. Always allowNull:true,
        //     always skip self.
        //  2. SetRelationDirect REFUSES OUTRIGHT when both factions have
        //     goodwill - `if (HasGoodwill && other.HasGoodwill) { Log.Error; return; }`.
        //     That is most pairs. It is the no-goodwill path (mechanoids,
        //     insects, permanent enemies), NOT the general one.
        //  3. Relations are stored PER FACTION, two records per pair, and the
        //     engine keeps them in lockstep itself: TryAffectGoodwillWith
        //     assigns `factionRelation2.baseGoodwill = factionRelation.baseGoodwill`
        //     and copies the kind. ⇒ a one-sided write is not a feature the
        //     engine offers; it is a corrupt state. `both` defaults to true and
        //     one-sided writes are labelled DESYNCED in the reply.
        //  4. Notify_RelationKindChanged IS NOT COSMETIC. It rebuilds
        //     attackTargetsCache, re-notifies every Lord, and flips guest
        //     status to Prisoner. A bare `rel.kind = Hostile` assignment leaves
        //     pawns on a live map calmly ignoring their new enemies - the tool
        //     reports success and the game does not move.
        //  5. CheckKindThresholds SNAPS KIND BACK from goodwill: <= -75 forces
        //     Hostile, >= 75 forces Ally, and a Hostile pair at goodwill >= 0
        //     is dragged to Neutral at the next goodwill event. Setting kind
        //     without moving goodwill into the matching band buys a relation
        //     with a half-life. Hence clampGoodwillToKind, defaulted ON.
        // ================================================================

        // Accepts a defName, or "Player"/"PlayerColony" for Faction.OfPlayer.
        // The defName/name split has already cost calls in this project, so the
        // failure path names the difference rather than leaving it to a guess.
        // 🔴 EVERY live faction matching, not the first one. A world routinely holds
        // several factions of ONE FactionDef, so a defName is not an address: a write
        // aimed at "OutlanderCivil" would silently land on whichever of them the
        // FactionManager listed first and report success. Callers that WRITE must
        // refuse an ambiguous name; the escape hatch is the faction's own Name, which
        // is per-faction, and it is only consulted when no defName matched.
        private static List<Faction> ResolveFactionArgAll(string s)
        {
            var found = new List<Faction>();
            if (string.IsNullOrWhiteSpace(s)) return found;
            s = s.Trim();
            if (string.Equals(s, "Player", StringComparison.OrdinalIgnoreCase)
                || string.Equals(s, "PlayerColony", StringComparison.OrdinalIgnoreCase))
            {
                var p = Faction.OfPlayerSilentFail;
                if (p != null) found.Add(p);
                return found;
            }
            var fm = Find.FactionManager;
            if (fm == null) return found;
            found.AddRange(fm.AllFactions.Where(
                q => q != null && string.Equals(q.def?.defName, s, StringComparison.OrdinalIgnoreCase)));
            if (found.Count == 0)
                found.AddRange(fm.AllFactions.Where(
                    q => q != null && string.Equals(q.Name, s, StringComparison.OrdinalIgnoreCase)));
            return found;
        }

        private static Faction ResolveFactionArg(string s)
        {
            return ResolveFactionArgAll(s).FirstOrDefault();
        }

        // Same silent-corruption shape as the write guard above: FactionManager's OWN
        // FirstFactionOfDef silently returns the FIRST live faction of a def when a world
        // holds several - which this file's own header comment calls "routine", not an
        // edge case. WorldObjectsSet, WorldObjectsAdd and WorldSettlementsImport all
        // resolved a FactionDef to a live Faction this way and then WROTE it (re-faction,
        // create, or import), so an ambiguous def used to land silently on whichever
        // faction FactionManager happened to list first and report success. Refuse
        // instead, the same way AmbiguousFaction refuses a write on the relations tools.
        private static Faction ResolveLiveFactionOfDefOrFail(FactionDef fd, string askedDefName, out object fail)
        {
            fail = null;
            if (fd == null) return null;
            var matches = Find.FactionManager.AllFactions.Where(q => q != null && q.def == fd).ToList();
            if (matches.Count > 1)
            {
                fail = Fail($"FactionDef '{askedDefName}' matches {matches.Count} live factions in this " +
                            "world - FirstFactionOfDef would silently pick one and land the write on the " +
                            "wrong faction. Use jawa/world_objects_get or jawa/faction_relations_get to find " +
                            "the specific faction and its own Name, if the tool you are using accepts one.",
                    new { defName = askedDefName, names = matches.Select(q => q.Name).ToList() });
                return null;
            }
            return matches.Count == 1 ? matches[0] : null;
        }

        // null when the argument names exactly one faction. Otherwise the refusal,
        // carrying the per-faction Names that CAN address them one at a time.
        private static object AmbiguousFaction(string asked)
        {
            var hits = ResolveFactionArgAll(asked);
            if (hits.Count <= 1) return null;
            return Fail($"'{asked}' names {hits.Count} live factions - a FactionDef is not an " +
                        "address. Pass the faction's Name instead so the write lands where you meant.",
                new { names = hits.Select(q => q.Name).ToList(), defName = hits[0].def?.defName });
        }

        private static object FactionNotFound(string asked)
        {
            var fm = Find.FactionManager;
            return Fail($"No faction with defName '{asked}'.", new
            {
                hint = "Use the DEFNAME, or the literal 'Player'. jawa/list_factions returns both.",
                suggestions = fm?.AllFactions.Where(q => q?.def != null)
                    .Select(q => q.def.defName)
                    .Where(q => q.IndexOf(asked, StringComparison.OrdinalIgnoreCase) >= 0)
                    .Take(12).ToList()
            });
        }

        // One ordered cell, measured. Everything here is read off the faction
        // pair after any write, never inferred.
        private static object RelationCell(Faction a, Faction b)
        {
            var rel = a.RelationWith(b, true);          // allowNull - see note 1
            return new
            {
                from = a.def?.defName,
                fromName = a.Name,
                to = b.def?.defName,
                toName = b.Name,
                kind = a.RelationKindWith(b).ToString(),
                goodwill = a.GoodwillWith(b),
                baseGoodwill = rel?.baseGoodwill,
                hasRecord = rel != null,
                hostile = a.HostileTo(b),
                // Why a write may be refused, stated BEFORE it is attempted.
                canChangeGoodwill = a.CanChangeGoodwillFor(b, 1),
                bothHaveGoodwill = a.HasGoodwill && b.HasGoodwill,
                permanentEnemy = a.def != null && a.def.permanentEnemy,
                defeated = a.defeated,
                hidden = a.Hidden
            };
        }

        [Tool(
            "jawa/faction_relations_get",
            Description =
                "Read the FACTION-TO-FACTION relation matrix - every pair, not just pairs " +
                "with the player. No args returns the whole matrix; `faction` alone returns " +
                "that faction's row; `faction`+`other` returns the single cell. Pass " +
                "'Player' for the player colony. Relations are stored per faction, TWO " +
                "records per pair, so every pair is reported in BOTH directions and any " +
                "disagreement between them is called out - that disagreement is a corrupt " +
                "state, and finding it is half of why this tool exists.",
            ResultDescription =
                "`pairs` holds ordered cells (from -> to) with kind, goodwill, baseGoodwill, " +
                "hostile, and the flags that decide whether a WRITE would be refused: " +
                "canChangeGoodwill, bothHaveGoodwill, permanentEnemy, defeated. " +
                "`asymmetric` lists pairs whose two directions disagree on kind or goodwill. " +
                "`counts` summarises the matrix. ⚠️ Neutral pairs are omitted unless " +
                "includeNeutral - a 30-faction world is 870 ordered pairs and almost all " +
                "of them are Neutral.")]
        public static async Task<object> FactionRelationsGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Faction defName, or 'Player'. Omit for the whole matrix.", DefaultValue = null)]
            string faction = null,
            [ToolParameter(Description =
                "Second faction defName, or 'Player'. With `faction`, returns one cell.",
                DefaultValue = null)]
            string other = null,
            [ToolParameter(Description =
                "Include Neutral pairs. Off by default - they are the overwhelming majority " +
                "and they are the uninteresting ones.", DefaultValue = false)]
            bool includeNeutral = false,
            [ToolParameter(Description =
                "Include hidden factions (the ones the player never sees listed).",
                DefaultValue = true)]
            bool includeHidden = true,
            [ToolParameter(Description =
                "Include defeated factions.", DefaultValue = false)]
            bool includeDefeated = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var fm = Find.FactionManager;
                if (fm == null) return Fail("No FactionManager. This needs a GAME loaded.");

                Faction fa = null, fb = null;
                if (!string.IsNullOrWhiteSpace(faction))
                {
                    fa = ResolveFactionArg(faction);
                    if (fa == null) return FactionNotFound(faction);
                }
                if (!string.IsNullOrWhiteSpace(other))
                {
                    fb = ResolveFactionArg(other);
                    if (fb == null) return FactionNotFound(other);
                }
                if (fa != null && fb != null && fa == fb)
                    return Fail("faction and other are the same faction; a faction has no relation with itself.");

                var all = fm.AllFactions
                    .Where(q => q?.def != null)
                    .Where(q => includeHidden || !q.Hidden)
                    .Where(q => includeDefeated || !q.defeated)
                    .ToList();

                // The single-cell case: report it in both directions and stop.
                if (fa != null && fb != null)
                {
                    var ab = RelationCell(fa, fb);
                    var ba = RelationCell(fb, fa);
                    return new
                    {
                        success = true,
                        message = $"{fa.def.defName} -> {fb.def.defName}: " +
                                  $"{fa.RelationKindWith(fb)} ({fa.GoodwillWith(fb)}); reverse " +
                                  $"{fb.RelationKindWith(fa)} ({fb.GoodwillWith(fa)}).",
                        pairs = new List<object> { ab, ba },
                        asymmetric = PairAsymmetry(fa, fb),
                        ticksGame = TicksGameSafe()
                    };
                }

                var lefts = fa != null ? new List<Faction> { fa } : all;
                var cells = new List<object>();
                var asym = new List<object>();
                int considered = 0, hostilePairs = 0, allyPairs = 0, neutralPairs = 0, noRecord = 0;

                foreach (var a in lefts)
                {
                    foreach (var b in all)
                    {
                        if (a == b) continue;                    // note 1: self errors
                        considered++;
                        var kind = a.RelationKindWith(b);
                        if (kind == FactionRelationKind.Hostile) hostilePairs++;
                        else if (kind == FactionRelationKind.Ally) allyPairs++;
                        else neutralPairs++;
                        if (a.RelationWith(b, true) == null) noRecord++;

                        if (kind != FactionRelationKind.Neutral || includeNeutral)
                            cells.Add(RelationCell(a, b));

                        // Only walk each unordered pair once for the asymmetry
                        // check, or every disagreement is reported twice.
                        // 🔴 loadID, NOT defName. A world routinely holds SEVERAL live
                        // factions of one FactionDef - that is why the engine's own
                        // lookup is named FirstFactionOfDef - and CompareOrdinal returns
                        // 0 for both orderings of such a pair, so neither direction
                        // passed this gate and the headline check silently never ran on
                        // them. loadID is unique per faction.
                        if (a.loadID < b.loadID)
                        {
                            var d = PairAsymmetry(a, b);
                            if (d != null) asym.Add(d);
                        }
                    }
                }

                return new
                {
                    success = true,
                    message = $"{cells.Count} pair(s) reported out of {considered} ordered pair(s) " +
                              $"over {all.Count} faction(s). " +
                              $"{hostilePairs} hostile, {allyPairs} ally, {neutralPairs} neutral" +
                              (includeNeutral ? "" : " (neutral omitted; pass includeNeutral)") +
                              (asym.Count > 0
                                  ? $". ⚠️ {asym.Count} ASYMMETRIC pair(s) - the two stored records disagree."
                                  : "."),
                    counts = new
                    {
                        factions = all.Count,
                        orderedPairs = considered,
                        hostile = hostilePairs,
                        ally = allyPairs,
                        neutral = neutralPairs,
                        missingRecord = noRecord,
                        asymmetric = asym.Count
                    },
                    pairs = cells,
                    asymmetric = asym,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // null when the two stored records agree. Kind AND goodwill are both
        // checked: SetRelation mirrors kind but leaves the mirror's baseGoodwill
        // at the FactionRelation default of 100, so agreeing on kind proves
        // nothing about goodwill.
        private static object PairAsymmetry(Faction a, Faction b)
        {
            var ka = a.RelationKindWith(b);
            var kb = b.RelationKindWith(a);
            var ga = a.GoodwillWith(b);
            var gb = b.GoodwillWith(a);
            if (ka == kb && ga == gb) return null;
            return new
            {
                a = a.def?.defName,
                b = b.def?.defName,
                kindA = ka.ToString(),
                kindB = kb.ToString(),
                goodwillA = ga,
                goodwillB = gb,
                kindDisagrees = ka != kb,
                goodwillDisagrees = ga != gb
            };
        }

        [Tool(
            "jawa/faction_relations_set",
            Description =
                "Set the relation between ANY two factions - pass 'Player' for the player " +
                "colony. Writes both stored records by default, because the engine itself " +
                "keeps them in lockstep and a one-sided write is a corrupt state, not a " +
                "feature. Picks the write path off the pair: SetRelationDirect when either " +
                "side lacks goodwill (mechanoids, insects, permanent enemies - it REFUSES " +
                "when both sides have goodwill), otherwise a direct record write followed " +
                "by Notify_RelationKindChanged, which is what actually makes pawns on a " +
                "live map re-target. Setting kind also moves goodwill into the matching " +
                "band by default, or CheckKindThresholds snaps the kind back at the next " +
                "goodwill event.",
            ResultDescription =
                "`was` and `now` for kind and goodwill, in BOTH directions, each read back " +
                "off the pair after the call - every setter involved returns void, so a " +
                "method completing is not evidence. success means the read-back matches the " +
                "request. `dryRun` reports the current relation and changes nothing.")]
        public static async Task<object> FactionRelationsSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "First faction defName, or 'Player'.")]
            string faction,
            [ToolParameter(Description = "Second faction defName, or 'Player'.")]
            string other,
            [ToolParameter(Description =
                "Hostile, Neutral or Ally. Case-insensitive. Omit to change goodwill only.",
                DefaultValue = null)]
            string kind = null,
            [ToolParameter(Description =
                "Base goodwill, -100..100. Omit to leave it alone (or to let " +
                "clampGoodwillToKind choose a value consistent with `kind`).",
                DefaultValue = -9999)]
            int goodwill = -9999,
            [ToolParameter(Description =
                "Write both stored records. Leave ON. Turning it off writes one direction " +
                "only and produces a state the engine never creates - offered so the " +
                "asymmetry can be TESTED, not because it is useful.", DefaultValue = true)]
            bool both = true,
            [ToolParameter(Description =
                "When `kind` is set and `goodwill` is not, move goodwill into the band that " +
                "sustains that kind (Hostile -100, Ally 100, Neutral 0). Off means the kind " +
                "is live only until the next goodwill event re-derives it.",
                DefaultValue = true)]
            bool clampGoodwillToKind = true,
            [ToolParameter(Description =
                "Let RimWorld send its hostility letter. Off by default: a test should not " +
                "narrate itself.", DefaultValue = false)]
            bool sendLetter = false,
            [ToolParameter(Description = "Report the current relation and change nothing.",
                DefaultValue = false)]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required.");
            if (string.IsNullOrWhiteSpace(other)) return Fail("other is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var fm = Find.FactionManager;
                if (fm == null) return Fail("No FactionManager. This needs a GAME loaded.");

                var a = ResolveFactionArg(faction);
                if (a == null) return FactionNotFound(faction);
                var b = ResolveFactionArg(other);
                if (b == null) return FactionNotFound(other);
                if (a == b) return Fail("A faction has no relation with itself.");
                // This tool WRITES. Silently picking the first of several same-def
                // factions would leave the rest untouched under a success reply.
                var ambA = AmbiguousFaction(faction); if (ambA != null) return ambA;
                var ambB = AmbiguousFaction(other); if (ambB != null) return ambB;

                var wantKind = !string.IsNullOrWhiteSpace(kind);
                FactionRelationKind parsed = default;
                // 🔴 Enum.TryParse ALSO accepts a bare number and returns true for a value
                // the enum never declared - "7" parses as (FactionRelationKind)7. Nothing
                // downstream catches it: FactionRelation.kind is a plain field written by
                // Scribe_Values, RelationKindWith returns rel.kind unfiltered, and the
                // read-back below would compare "7" to "7" and report the write a SUCCESS.
                // The savegame would then carry a relation kind no engine switch handles.
                if (wantKind && (!Enum.TryParse(kind.Trim(), true, out parsed)
                                 || !Enum.IsDefined(typeof(FactionRelationKind), parsed)))
                    return Fail($"'{kind}' is not a FactionRelationKind.",
                        new { valid = Enum.GetNames(typeof(FactionRelationKind)) });

                var wantGoodwill = goodwill != -9999;
                if (wantGoodwill && (goodwill < -100 || goodwill > 100))
                    return Fail($"goodwill must be -100..100, got {goodwill}.");

                // Kind with no goodwill asked for: pick the value that SUSTAINS
                // the kind rather than leaving it to decay. See note 5.
                var effGoodwill = goodwill;
                var derivedGoodwill = false;
                if (wantKind && !wantGoodwill && clampGoodwillToKind)
                {
                    effGoodwill = parsed == FactionRelationKind.Hostile ? -100
                                : parsed == FactionRelationKind.Ally ? 100
                                : 0;
                    derivedGoodwill = true;
                }
                var writeGoodwill = wantGoodwill || derivedGoodwill;

                if (!wantKind && !writeGoodwill && !dryRun)
                    return Fail("Nothing to do: pass `kind`, `goodwill`, or both.");

                var wasKindA = a.RelationKindWith(b).ToString();
                var wasKindB = b.RelationKindWith(a).ToString();
                var wasGoodwillA = a.GoodwillWith(b);
                var wasGoodwillB = b.GoodwillWith(a);

                var notes = new List<string>();
                var usedSetRelationDirect = false;

                if (!dryRun)
                {
                    var relAB = a.RelationWith(b, true);
                    var relBA = b.RelationWith(a, true);
                    if (relAB == null || (both && relBA == null))
                        return Fail(
                            "One side has no FactionRelation record, so there is nothing to " +
                            "write. This happens with factions that were never registered " +
                            "against each other.",
                            new { hasAB = relAB != null, hasBA = relBA != null });

                    if (writeGoodwill)
                    {
                        // Direct record assignment, deliberately: this is what
                        // TryAffectGoodwillWith itself does to the mirror record,
                        // and unlike TryAffectGoodwillWith it is EXACT - that
                        // path runs the ask through CalculateAdjustedGoodwillChange
                        // and clamps, so asking for -60 can land somewhere else.
                        // An authoring tool must put the number where it was told.
                        relAB.baseGoodwill = effGoodwill;
                        if (both && relBA != null) relBA.baseGoodwill = effGoodwill;
                        if (!a.CanChangeGoodwillFor(b, 1))
                            notes.Add("CanChangeGoodwillFor is FALSE for this pair (permanent " +
                                      "enemy, defeated, no goodwill, or quest-locked). The " +
                                      "record was written directly; the engine's own goodwill " +
                                      "events will refuse to move it.");
                    }

                    if (wantKind)
                    {
                        if (!a.HasGoodwill || !b.HasGoodwill)
                        {
                            // The sanctioned path for no-goodwill pairs. It
                            // mirrors and notifies on its own.
                            a.SetRelationDirect(b, parsed, sendLetter,
                                "Set by jawa/faction_relations_set.", null);
                            usedSetRelationDirect = true;
                        }
                        else
                        {
                            // SetRelationDirect would Log.Error and return here
                            // (note 2), so write the records and fire the
                            // notification ourselves - note 4, the difference
                            // between a number changing and the game moving.
                            var prevA = relAB.kind;
                            var prevB = relBA != null ? relBA.kind : prevA;
                            relAB.kind = parsed;
                            if (both && relBA != null) relBA.kind = parsed;

                            bool sentA;
                            a.Notify_RelationKindChanged(b, prevA, sendLetter,
                                "Set by jawa/faction_relations_set.",
                                GlobalTargetInfo.Invalid, out sentA);
                            if (both && relBA != null)
                            {
                                bool sentB;
                                // B's own PRIOR kind, not A's - this tool exists in part to
                                // repair exactly the case where the two records disagree
                                // (see the class header), so on that case this notify must
                                // not tell B's faction that its own record changed from A's
                                // kind, which it never actually held.
                                b.Notify_RelationKindChanged(a, prevB, sendLetter,
                                    "Set by jawa/faction_relations_set.",
                                    GlobalTargetInfo.Invalid, out sentB);
                            }
                        }
                    }

                    if (!both)
                        notes.Add("⚠️ one-sided write (both=false). The two stored records may " +
                                  "now DISAGREE, which is a state the engine never produces. " +
                                  "jawa/faction_relations_get will report this pair as asymmetric.");
                }

                // 🔴 Read back, both directions. Every setter above returns void.
                var nowKindA = a.RelationKindWith(b).ToString();
                var nowKindB = b.RelationKindWith(a).ToString();
                var nowGoodwillA = a.GoodwillWith(b);
                var nowGoodwillB = b.GoodwillWith(a);

                var kindOk = !wantKind || dryRun
                             || string.Equals(nowKindA, parsed.ToString(), StringComparison.OrdinalIgnoreCase);
                var goodwillOk = !writeGoodwill || dryRun || nowGoodwillA == effGoodwill;
                if (both && !dryRun)
                {
                    if (wantKind && !string.Equals(nowKindB, parsed.ToString(), StringComparison.OrdinalIgnoreCase))
                        kindOk = false;
                    if (writeGoodwill && nowGoodwillB != effGoodwill)
                        goodwillOk = false;
                }

                return new
                {
                    success = kindOk && goodwillOk,
                    message = dryRun
                        ? $"{a.def.defName} <-> {b.def.defName}: {nowKindA}/{nowKindB}, " +
                          $"goodwill {nowGoodwillA}/{nowGoodwillB}. (dry run, nothing changed.)"
                        : $"{a.def.defName} <-> {b.def.defName}: kind {wasKindA}->{nowKindA} " +
                          $"(reverse {wasKindB}->{nowKindB}), goodwill {wasGoodwillA}->{nowGoodwillA} " +
                          $"(reverse {wasGoodwillB}->{nowGoodwillB})." +
                          (kindOk && goodwillOk
                              ? ""
                              : " ⚠️ READ-BACK DOES NOT MATCH THE REQUEST - the engine overrode " +
                                "it. Do not treat this pair as set."),
                    dryRun,
                    both,
                    usedSetRelationDirect,
                    goodwillDerivedFromKind = derivedGoodwill ? (int?)effGoodwill : null,
                    forward = new
                    {
                        from = a.def.defName, to = b.def.defName,
                        kind = new { was = wasKindA, now = nowKindA, asked = wantKind ? parsed.ToString() : null },
                        goodwill = new { was = wasGoodwillA, now = nowGoodwillA, asked = writeGoodwill ? (int?)effGoodwill : null },
                        hostile = a.HostileTo(b)
                    },
                    reverse = new
                    {
                        from = b.def.defName, to = a.def.defName,
                        kind = new { was = wasKindB, now = nowKindB },
                        goodwill = new { was = wasGoodwillB, now = nowGoodwillB },
                        hostile = b.HostileTo(a)
                    },
                    asymmetric = PairAsymmetry(a, b),
                    notes,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }
        // ================================================================
        //  jawa/pawnkind_audit - WHICH KINDS CAN NEVER ARM THEMSELVES
        //
        //  Born from a live finding on 2026-08-20: 16 of 48 authored Jawa
        //  role kinds spawned bare-handed, 5/5 samples. The cause was not an
        //  empty weaponTag - it was `weaponMoney` sitting under the price of
        //  every weapon carrying the tag.
        //
        //  🔑 THIS TOOL DOES NOT RE-DERIVE THE RULE. It reflects the engine's
        //  own `PawnWeaponGenerator.allWeaponPairs` and applies the engine's
        //  own predicate, read out of TryGenerateWeaponFor:
        //      if (!(w.Price > weaponMoney.RandomInRange) && tagsIntersect) ...
        //  ⇒ weaponMoney is a CEILING, not a bracket. `min` never excludes a
        //  weapon; only `max` can empty the pool. A tool that reimplemented
        //  this from the defs would have got that backwards - the first
        //  hand analysis did.
        //
        //  ⚠️ Price includes STUFF. Comparing bare MarketValue understates it.
        // ================================================================
        [Tool(
            "jawa/pawnkind_audit",
            Description =
                "Find every PawnKindDef that CANNOT arm itself, and say which of the three " +
                "reasons it is. Uses the engine's own weapon-pair table and the engine's own " +
                "eligibility test, so it cannot drift from what generation actually does. " +
                "Reasons: `noWeaponTags` (the kind lists none - it will never carry anything), " +
                "`emptyTagPool` (tags are listed but no weapon in the loaded game carries one), " +
                "`cannotAfford` (weapons exist but every one costs more than weaponMoney.max). " +
                "Run it against the FULL mod list; a reduced list makes healthy kinds look broken.",
            ResultDescription =
                "counts per reason, and per-kind rows carrying weaponMoney, the cheapest " +
                "eligible weapon and its price, so the fix is a number rather than a guess. " +
                "`checked` says how many kinds were actually testable.")]
        public static async Task<object> PawnKindAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Only audit kinds whose defName contains this (case-insensitive). Empty = all.",
                DefaultValue = null)]
            string filter = null,
            [ToolParameter(Description = "Max example rows per reason. Default 40.", DefaultValue = 40)]
            int limit = 40,
            [ToolParameter(Description =
                "Include kinds that are fine, for a full census. Off by default.", DefaultValue = false)]
            bool includeHealthy = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                // The pair table is private static and is built by
                // PawnWeaponGenerator.Reset() at startup. Reflection is the only
                // route, and a null here means the game has not finished loading
                // rather than that the audit found nothing - say so.
                var f = typeof(PawnWeaponGenerator).GetField(
                    "allWeaponPairs",
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
                if (f == null)
                    return Fail("PawnWeaponGenerator.allWeaponPairs not found - the field was " +
                                "renamed in this RimWorld build. Re-read the source before trusting " +
                                "any weapon audit.");
                var pairs = f.GetValue(null) as List<ThingStuffPair>;
                if (pairs == null || pairs.Count == 0)
                    return Fail("allWeaponPairs is empty. That is a NOT-READY signal, not a finding - " +
                                "the table is built during startup. Try again once a game is loaded.");

                // tag -> cheapest price carrying it, computed once. Doing it per
                // kind would be O(kinds x pairs) over ~400 kinds and thousands
                // of pairs.
                var cheapestByTag = new Dictionary<string, KeyValuePair<string, float>>();
                foreach (var w in pairs)
                {
                    var tags = w.thing != null ? w.thing.weaponTags : null;
                    if (tags == null) continue;
                    foreach (var tag in tags)
                    {
                        KeyValuePair<string, float> cur;
                        if (!cheapestByTag.TryGetValue(tag, out cur) || w.Price < cur.Value)
                            cheapestByTag[tag] = new KeyValuePair<string, float>(w.thing.defName, w.Price);
                    }
                }

                var noTags = new List<object>(); int noTagsN = 0;
                var zeroBudget = new List<object>(); int zeroBudgetN = 0;
                // 🔴 PAWNKIND_AUDIT_TAGLESS_BLIND_1. A kind with no weaponTags is USUALLY a
                // deliberate civilian - see the comment below - but a COMBAT role that has
                // LOST its tags looks identical and used to vanish into that same bucket.
                // It is not hypothetical: Jawa_Droid_Leader, Jawa_Droid_Specialist and
                // Jawa_TradeMoot_Specialist each shipped for a while with no weaponTags
                // field at all, and this tool called all three intentionally-unarmed
                // civilians. So the tagless are now SPLIT, and the suspicious half gets its
                // own line rather than being folded into the exclusion.
                // ⛔ The fix is NOT to stop excluding tagless kinds - that reported 294
                // working civilians as broken and is how the exclusion got here.
                // 🔑 THE DISCRIMINATOR IS DELIBERATELY TWO-PART. `isFighter` alone is not
                // enough: gen_pawnkind_roster.py emits `isFighter` FROM the tag list, so a
                // kind that lost its tags would have lost its isFighter too and hidden all
                // over again. combatPower 40 is the anchor the roster generator itself uses
                // for a grunt-tier tribal carrying almost nothing; below that is civilian.
                var taglessFighter = new List<object>(); int taglessFighterN = 0;
                var emptyPool = new List<object>(); int emptyPoolN = 0;
                var cannotAfford = new List<object>(); int cannotAffordN = 0;
                var healthy = new List<object>(); int healthyN = 0;
                int considered = 0, skippedNonCombat = 0;

                foreach (var k in DefDatabase<PawnKindDef>.AllDefsListForReading)
                {
                    if (k == null || k.race == null) continue;
                    if (!string.IsNullOrWhiteSpace(filter) &&
                        k.defName.IndexOf(filter.Trim(), StringComparison.OrdinalIgnoreCase) < 0) continue;

                    // Only tool users can hold a weapon at all. An animal with no
                    // weaponTags is not a defect and must not pollute the count.
                    var rp = k.race.race;
                    if (rp == null || !rp.ToolUser) { skippedNonCombat++; continue; }
                    considered++;

                    // 🔑 A kind with NO weaponTags is not broken - TryGenerateWeaponFor
                    // returns early for it BY DESIGN. Traders, councilmen, children and
                    // haulers are supposed to be empty-handed. Counting them as defects
                    // made the first run of this tool report 339 broken kinds out of 710,
                    // of which 294 were working exactly as intended.
                    var tags = k.weaponTags;
                    if (tags == null || tags.Count == 0)
                    {
                        if (k.isFighter || k.combatPower >= 40f)
                        {
                            taglessFighterN++;
                            if (taglessFighter.Count < limit)
                                taglessFighter.Add(new { kind = k.defName, label = k.label,
                                                         race = k.race.defName,
                                                         isFighter = k.isFighter,
                                                         combatPower = k.combatPower });
                        }
                        else
                        {
                            noTagsN++;
                            if (noTags.Count < limit)
                                noTags.Add(new { kind = k.defName, label = k.label, race = k.race.defName });
                        }
                        continue;
                    }
                    // Same for a deliberate zero budget: weaponMoney.max == 0 cannot admit
                    // any weapon and is how a child is kept unarmed while still inheriting
                    // its parent's tags.
                    if (k.weaponMoney.max <= 0f)
                    {
                        zeroBudgetN++;
                        if (zeroBudget.Count < limit)
                            zeroBudget.Add(new { kind = k.defName, label = k.label, tags = tags.ToList() });
                        continue;
                    }

                    string bestDef = null; float bestPrice = float.MaxValue;
                    foreach (var tag in tags)
                    {
                        KeyValuePair<string, float> c;
                        if (cheapestByTag.TryGetValue(tag, out c) && c.Value < bestPrice)
                        { bestPrice = c.Value; bestDef = c.Key; }
                    }

                    var money = k.weaponMoney;
                    if (bestDef == null)
                    {
                        emptyPoolN++;
                        if (emptyPool.Count < limit)
                            emptyPool.Add(new { kind = k.defName, label = k.label, tags = tags.ToList(),
                                                weaponMoneyMax = money.max });
                        continue;
                    }

                    // The engine's test, verbatim in shape: eligible iff price is
                    // NOT GREATER than the roll, and the roll cannot exceed max.
                    if (bestPrice > money.max)
                    {
                        cannotAffordN++;
                        if (cannotAfford.Count < limit)
                            cannotAfford.Add(new
                            {
                                kind = k.defName, label = k.label, tags = tags.ToList(),
                                weaponMoneyMin = money.min, weaponMoneyMax = money.max,
                                cheapestEligible = bestDef, cheapestPrice = bestPrice,
                                raiseMaxTo = (float)Math.Ceiling(bestPrice),
                            });
                        continue;
                    }

                    healthyN++;
                    if (includeHealthy && healthy.Count < limit)
                        healthy.Add(new { kind = k.defName, cheapestEligible = bestDef,
                                          cheapestPrice = bestPrice, weaponMoneyMax = money.max });
                }

                // 🔴 BROKEN is ONLY the kinds that INTEND to arm and cannot. The two
                // categories above are design, and are reported without scoring.
                // ⚠️ taglessFighterN is NOT added to `broken`. It is a SUSPICION, not a
                // measurement - a kind may legitimately be a high-combatPower brawler with
                // no ranged tags - so it gets its own sentence and its own list, and a human
                // decides. Scoring it would re-create the false-positive flood.
                int broken = emptyPoolN + cannotAffordN;
                string taglessFighterLine = taglessFighterN == 0
                    ? ""
                    : " ⚠️ " + taglessFighterN + " of those declare isFighter or combatPower >= 40 and " +
                      "carry NO weaponTags at all - a combat role that lost its tags looks exactly like " +
                      "a civilian here; see taglessButLooksLikeAFighter.";
                return new
                {
                    success = true,
                    message = broken == 0
                        ? considered + " tool-using kind(s) audited; every kind that intends to arm can. " +
                          "(" + noTagsN + " carry no weaponTags and " + zeroBudgetN + " have a zero budget - " +
                          "both are design, not defects.)" + taglessFighterLine
                        : broken + " of " + considered + " tool-using kind(s) INTEND to arm and CANNOT: " +
                          emptyPoolN + " whose tags match no loaded weapon, " +
                          cannotAffordN + " that cannot afford the cheapest weapon their tags allow. " +
                          "(Not counted: " + noTagsN + " with no weaponTags and " + zeroBudgetN +
                          " with weaponMoney.max 0 - both are how a civilian or a child is kept unarmed.)" +
                          taglessFighterLine,
                    weaponPairsInGame = pairs.Count,
                    distinctWeaponTags = cheapestByTag.Count,
                    kindsChecked = considered,
                    skippedNonToolUser = skippedNonCombat,
                    counts = new { emptyTagPool = emptyPoolN, cannotAfford = cannotAffordN,
                                   healthy = healthyN,
                                   byDesign_noWeaponTags = noTagsN, byDesign_zeroBudget = zeroBudgetN,
                                   taglessButLooksLikeAFighter = taglessFighterN },
                    taglessButLooksLikeAFighter = taglessFighter,
                    byDesign_noWeaponTags = noTags,
                    byDesign_zeroBudget = zeroBudget,
                    emptyTagPool = emptyPool,
                    cannotAfford,
                    healthy = includeHealthy ? healthy : null,
                    note = "weaponMoney is a CEILING - raise `max` above cheapestPrice. `min` only " +
                           "shifts the roll and never excludes a weapon. Price includes stuff.",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/texture_audit - EVERY texPath THAT RESOLVES TO NOTHING
        //
        //  Born from the GrimTerra swap on 2026-08-20: two animals logged
        //  "Failed to find any textures at ..." and the cause was a typo in
        //  a lifeStage texPath - `TortoiseGRim` for `GRimTortoise`, and a
        //  capital B in `GRimPinkBird`.
        //
        //  🔴 THE CASE TRAP IS WHY THIS IS A TOOL AND NOT A SHELL SCRIPT.
        //  Windows' filesystem is case-INsensitive; RimWorld's content index
        //  is case-SENSITIVE. `ls` resolves a path the game cannot. Only the
        //  running game can answer this question.
        //
        //  ⚠️ The log only reports a failure when ALL directions are missing
        //  AND something actually tried to draw it. This sweeps every path
        //  whether or not anything has been spawned.
        // ================================================================
        [Tool(
            "jawa/texture_audit",
            Description =
                "Sweep ThingDef graphics for texPaths that resolve to NO texture in the " +
                "running game, including per-lifeStage paths, which is where the typos hide. " +
                "Asks ContentFinder directly, so it answers the question the GAME asks - a " +
                "shell `ls` cannot, because Windows is case-insensitive and RimWorld is not. " +
                "Reports the owning mod so the fix can be aimed.",
            ResultDescription =
                "⚠️ A def whose graphicClass is NOT a vanilla Verse.Graphic_* is reported in " +
                "`unjudged`, never in `missing`: its own class resolves its own filenames and " +
                "this checker only knows vanilla's rules. Measured 2026-08-21, 39 of 53 rows " +
                "were one mod's custom class with all 138 of its PNGs present. " +
                "missing[] with def, mod, which graphic (main or lifeStage N), and the dead " +
                "path. `checked` counts paths actually tested. Empty missing[] with a large " +
                "`checked` is the pass.")]
        public static async Task<object> TextureAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Only defs whose defName contains this (case-insensitive). Empty = all.",
                DefaultValue = null)]
            string filter = null,
            [ToolParameter(Description =
                "Only defs from mods whose packageId or name contains this. Empty = all.",
                DefaultValue = null)]
            string mod = null,
            [ToolParameter(Description = "Max rows returned. Default 60.", DefaultValue = 60)]
            int limit = 60,
            [ToolParameter(Description =
                "Stop after testing this many paths. 0 = no cap. A full stack is tens of " +
                "thousands of paths; the sweep is fast but not free.", DefaultValue = 0)]
            int maxPaths = 0)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var missing = new List<object>();
                var unjudged = new List<object>();
                int tested = 0, missingN = 0, defsSeen = 0, unjudgedN = 0;

                // 🔴 A MOD THAT SHIPS ITS OWN graphicClass RESOLVES ITS OWN FILENAMES, and
                // this checker only knows vanilla's rules. Measured 2026-08-21: of 53 rows
                // reported dead, 39 were Tribal Furniture defs declaring
                // `TribalFurniture.Graphic_Appearances_Multi`, whose texPath is a STEM and
                // whose 138 PNGs are all present and drawing. 74% noise trains the reader to
                // skim a list that also holds real defects.
                // ⛔ Those defs are NOT dropped - a custom class can still point at nothing.
                // They go in their own bucket, named, so a human can judge them.
                Func<GraphicData, string> customClassOf = gd =>
                {
                    if (gd == null || gd.graphicClass == null) return null;
                    var t = gd.graphicClass;
                    bool vanilla = t.Namespace == "Verse" && t.Name.StartsWith("Graphic_");
                    return vanilla ? null : (t.FullName ?? t.Name);
                };
                var sw = new System.Diagnostics.Stopwatch(); sw.Start();

                // A Multi graphic stores <path>_north/_east/_south; a Single
                // stores <path> itself. Missing means NONE of them resolve -
                // the same bar the engine's own error uses.
                // 🔴 THE FOLDER CASE IS NOT OPTIONAL, and leaving it out made the first
                // version of this tool report 3,816 dead paths on a healthy game -
                // including vanilla Beer, Ambrosia and Luciferium. Graphic_Random and
                // Graphic_StackCount resolve a path as a FOLDER OF VARIANTS
                // (Beer_a, Beer_b, Beer_c) via GetAllInFolder, not as a file and not
                // as a directional set. A checker that only probes files calls every
                // stack-count item in the game broken.
                Func<string, bool> resolves = path =>
                {
                    if (string.IsNullOrEmpty(path)) return true;
                    if (ContentFinder<UnityEngine.Texture2D>.Get(path, false) != null) return true;
                    if (ContentFinder<UnityEngine.Texture2D>.Get(path + "_south", false) != null) return true;
                    if (ContentFinder<UnityEngine.Texture2D>.Get(path + "_north", false) != null) return true;
                    if (ContentFinder<UnityEngine.Texture2D>.Get(path + "_east", false) != null) return true;
                    try
                    {
                        var folder = ContentFinder<UnityEngine.Texture2D>.GetAllInFolder(path);
                        if (folder != null && folder.Any()) return true;
                    }
                    catch { /* a malformed path is a miss, not a crash */ }
                    return false;
                };

                foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    if (d == null) continue;
                    if (maxPaths > 0 && tested >= maxPaths) break;
                    if (!string.IsNullOrWhiteSpace(filter) &&
                        d.defName.IndexOf(filter.Trim(), StringComparison.OrdinalIgnoreCase) < 0) continue;
                    var modName = d.modContentPack != null ? d.modContentPack.Name : "(core?)";
                    var modId = d.modContentPack != null ? d.modContentPack.PackageId : "";
                    if (!string.IsNullOrWhiteSpace(mod) &&
                        modName.IndexOf(mod.Trim(), StringComparison.OrdinalIgnoreCase) < 0 &&
                        modId.IndexOf(mod.Trim(), StringComparison.OrdinalIgnoreCase) < 0) continue;
                    defsSeen++;

                    Action<GraphicData, string> check = (gd, which) =>
                    {
                        if (gd == null || string.IsNullOrEmpty(gd.texPath)) return;
                        if (maxPaths > 0 && tested >= maxPaths) return;
                        tested++;
                        if (resolves(gd.texPath)) return;
                        var custom = customClassOf(gd);
                        if (custom != null)
                        {
                            unjudgedN++;
                            if (unjudged.Count < limit)
                                unjudged.Add(new { def = d.defName, label = d.label, mod = modName,
                                                   packageId = modId, graphic = which,
                                                   texPath = gd.texPath, graphicClass = custom });
                            return;
                        }
                        missingN++;
                        if (missing.Count < limit)
                            missing.Add(new { def = d.defName, label = d.label, mod = modName,
                                              packageId = modId, graphic = which, texPath = gd.texPath });
                    };

                    if (d.graphicData != null) check(d.graphicData, "graphicData");

                }

                // 🔑 THE LIFESTAGE PATHS ARE THE ONES THAT HIDE, and they live on
                // PawnKindDef.lifeStages, NOT on the ThingDef. Both GrimTerra typos
                // were in the SECOND li while the main graphic and the other stages
                // were correct - so the animal renders fine as an adult and the bug
                // only appears on a juvenile nobody spawns on purpose.
                // ⚠️ The female* fields are swept too, deliberately. A path that is
                // wrong only on the female variant reads as an INTERMITTENT bug -
                // it is why male Chagrians always rendered and females did not.
                foreach (var pk in DefDatabase<PawnKindDef>.AllDefsListForReading)
                {
                    if (pk == null || pk.lifeStages == null) continue;
                    if (maxPaths > 0 && tested >= maxPaths) break;
                    if (!string.IsNullOrWhiteSpace(filter) &&
                        pk.defName.IndexOf(filter.Trim(), StringComparison.OrdinalIgnoreCase) < 0) continue;
                    var pkMod = pk.modContentPack != null ? pk.modContentPack.Name : "(core?)";
                    var pkId = pk.modContentPack != null ? pk.modContentPack.PackageId : "";
                    if (!string.IsNullOrWhiteSpace(mod) &&
                        pkMod.IndexOf(mod.Trim(), StringComparison.OrdinalIgnoreCase) < 0 &&
                        pkId.IndexOf(mod.Trim(), StringComparison.OrdinalIgnoreCase) < 0) continue;
                    defsSeen++;

                    for (int i = 0; i < pk.lifeStages.Count; i++)
                    {
                        var ls = pk.lifeStages[i];
                        if (ls == null) continue;
                        Action<GraphicData, string> lcheck = (gd, which) =>
                        {
                            if (gd == null || string.IsNullOrEmpty(gd.texPath)) return;
                            if (maxPaths > 0 && tested >= maxPaths) return;
                            tested++;
                            if (resolves(gd.texPath)) return;
                            var lcustom = customClassOf(gd);
                            if (lcustom != null)
                            {
                                unjudgedN++;
                                if (unjudged.Count < limit)
                                    unjudged.Add(new { def = pk.defName, label = pk.label, mod = pkMod,
                                                       packageId = pkId,
                                                       graphic = "lifeStages[" + i + "]." + which,
                                                       texPath = gd.texPath, graphicClass = lcustom });
                                return;
                            }
                            missingN++;
                            if (missing.Count < limit)
                                missing.Add(new { def = pk.defName, label = pk.label, mod = pkMod,
                                                  packageId = pkId,
                                                  graphic = "lifeStages[" + i + "]." + which,
                                                  texPath = gd.texPath });
                        };
                        lcheck(ls.bodyGraphicData, "body");
                        lcheck(ls.femaleGraphicData, "female");
                        lcheck(ls.dessicatedBodyGraphicData, "dessicated");
                        lcheck(ls.femaleDessicatedBodyGraphicData, "femaleDessicated");
                        lcheck(ls.corpseGraphicData, "corpse");
                        lcheck(ls.femaleCorpseGraphicData, "femaleCorpse");
                    }
                }
                sw.Stop();

                return new
                {
                    success = true,
                    message = missingN == 0
                        ? "No dead texPaths in " + tested + " path(s) across " + defsSeen + " def(s)."
                              + (unjudgedN > 0 ? " " + unjudgedN + " unjudged (custom graphicClass)." : "")
                        : missingN + " DEAD texPath(s) in " + tested + " path(s) across " + defsSeen + " def(s)."
                              + (unjudgedN > 0 ? " Plus " + unjudgedN + " UNJUDGED - a custom graphicClass "
                                                 + "resolves its own filenames and this checker cannot judge them."
                                               : ""),
                    defsScanned = defsSeen,
                    pathsChecked = tested,
                    missingCount = missingN,
                    unjudgedCount = unjudgedN,
                    truncated = missingN > missing.Count,
                    elapsedMs = sw.ElapsedMilliseconds,
                    missing,
                    unjudged,
                    note = "A dead path here is invisible to `ls`: Windows is case-insensitive, " +
                           "RimWorld's content index is not. Fix by PATCH, never by editing a " +
                           "workshop folder - Steam overwrites it. " +
                           "`unjudged` holds defs whose graphicClass is not a vanilla Verse.Graphic_*: " +
                           "their own class resolves its own filenames and this checker does not know " +
                           "its rules, so a miss there is UNKNOWN rather than dead. Judge those by hand.",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/world_settlements_import - W9 STAGE 5, the authored 72
        //
        //  The tile importer paints biomes; this places the holdings that
        //  make the planet a SETTING rather than a terrain map.
        //
        //  🔴 ALL-OR-NOTHING ON FACTIONS, and that is the whole design.
        //  A Settlement whose faction is null is DESTROYED on load with
        //  only a warning in the log - the loudest silent failure on the
        //  world layer. So every row's faction_def is resolved to a LIVE
        //  faction BEFORE anything is created, and one unresolvable row
        //  refuses the entire import. A half-painted roster that loses
        //  eleven holdings on the next load is worse than no import.
        // ================================================================
        [Tool(
            "jawa/world_settlements_import",
            Description =
                "Place the authored settlement roster from a CSV with columns " +
                "faction_def,name,tile (extra columns are ignored). Resolves EVERY row's " +
                "faction to a live faction first and refuses the whole import if any row " +
                "cannot be resolved, because a Settlement with a null faction is destroyed " +
                "on load with only a warning. Dry run by default.",
            ResultDescription =
                "created, removed, refused[] with the reason per row, and the settlement " +
                "count before and after - read back off Find.WorldObjects, not counted from " +
                "the file. Run jawa/world_commit afterwards.")]
        public static async Task<object> WorldSettlementsImport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Absolute path to the settlements CSV.")]
            string path = null,
            [ToolParameter(Description = "Write for real. Default false (dry run).", DefaultValue = false)]
            bool apply = false,
            [ToolParameter(Description =
                "Refuse unless WorldGrid.TilesCount equals this. 0 = no check.", DefaultValue = 0)]
            int expectTiles = 0,
            [ToolParameter(Description =
                "Remove every existing settlement first, EXCEPT any owned by the player or " +
                "carrying a map - destroying one of those orphans its map. Off by default - " +
                "leaves the generated roster in place and adds to it, which is almost never " +
                "what an authored import wants. Turn it on for a clean roster.", DefaultValue = false)]
            bool clearExisting = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a WORLD loaded.");
                if (expectTiles > 0 && grid.TilesCount != expectTiles)
                    return Fail("REFUSING: WorldGrid.TilesCount is " + grid.TilesCount + ", expected " +
                                expectTiles + ". A tile id means a different place on a different " +
                                "subdivision - importing here would paint the wrong planet.");

                string err; var csv = ReadTileCsv2(path, out err, requireTileColumn: false);
                if (csv == null) return Fail(err);
                foreach (var need in new[] { "faction_def", "name", "tile" })
                    if (!csv.Col.ContainsKey(need))
                        return Fail("Settlements CSV needs a '" + need + "' column. Header: " +
                                    string.Join(",", csv.Header.ToArray()));

                // PASS 1 - resolve everything, create nothing.
                var plan = new List<KeyValuePair<Faction, KeyValuePair<int, string>>>();
                var refused = new List<object>();
                var factionCache = new Dictionary<string, Faction>(StringComparer.OrdinalIgnoreCase);
                var factionAmbiguous = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                for (int r = 0; r < csv.Rows.Count; r++)
                {
                    var row = csv.Rows[r];
                    var fdName = Cell(csv, row, "faction_def");
                    var nm = Cell(csv, row, "name");
                    var tileS = Cell(csv, row, "tile");
                    int tile;
                    if (!int.TryParse(tileS, out tile) || tile < 0 || tile >= grid.TilesCount)
                    { refused.Add(new { row = r + 2, name = nm, reason = "tile '" + tileS + "' is not a valid tile id" }); continue; }

                    Faction fac;
                    if (!factionCache.TryGetValue(fdName ?? "", out fac))
                    {
                        var fd = DefDatabase<FactionDef>.GetNamedSilentFail((fdName ?? "").Trim());
                        // Same silent-corruption shape fixed on the faction-relations tools:
                        // a world routinely holds SEVERAL live factions of one FactionDef, and
                        // FirstFactionOfDef would silently pick one - landing a settlement on
                        // the wrong faction under a success reply. Treat it as unresolved for
                        // this row rather than guessing, so the all-or-nothing refusal below
                        // catches it like any other bad row. Cached alongside the faction so a
                        // repeated faction_def reports the same reason every time.
                        object facAmbFail = null;
                        fac = fd == null ? null : ResolveLiveFactionOfDefOrFail(fd, fdName, out facAmbFail);
                        if (fac == null && facAmbFail != null) factionAmbiguous.Add(fdName ?? "");
                        factionCache[fdName ?? ""] = fac;
                    }
                    if (fac == null)
                    {
                        var reason = factionAmbiguous.Contains(fdName ?? "")
                            ? "faction_def '" + fdName + "' names more than one live faction in this world - " +
                              "picking the first would silently land on the wrong one"
                            : "no LIVE faction of that def in this world - a settlement " +
                              "with a null faction is destroyed on load";
                        refused.Add(new { row = r + 2, name = nm, factionDef = fdName, reason });
                        continue;
                    }
                    plan.Add(new KeyValuePair<Faction, KeyValuePair<int, string>>(
                        fac, new KeyValuePair<int, string>(tile, nm)));
                }

                int before = Find.WorldObjects.Settlements.Count;
                var playerFac = Faction.OfPlayerSilentFail;
                int clearable = Find.WorldObjects.Settlements
                    .Count(q => !((playerFac != null && q.Faction == playerFac) || q.HasMap));
                if (refused.Count > 0)
                    return Fail("REFUSING the whole import: " + refused.Count + " of " + csv.Rows.Count +
                                " row(s) do not resolve. Nothing was created. Fix the rows, or the " +
                                "factions they name are not in this world.",
                                new { refused, wouldCreate = plan.Count, settlementsNow = before });

                if (!apply)
                    return new
                    {
                        success = true, dryRun = true, rows = csv.Rows.Count,
                        wouldCreate = plan.Count, wouldRemove = clearExisting ? clearable : 0,
                        wouldKeepPlayerOwned = clearExisting ? before - clearable : 0,
                        settlementsNow = before,
                        factions = plan.Select(q => q.Key.def.defName).Distinct().ToList(),
                        note = "DRY RUN - nothing was written. Every row resolved to a live faction. Pass apply=true.",
                        ticksGame = TicksGameSafe(),
                    };

                int removed = 0, keptPlayer = 0;
                int created = 0, skippedOccupied = 0; var failures = new List<object>();
                if (clearExisting)
                {
                    var player = Faction.OfPlayerSilentFail;
                    foreach (var st in Find.WorldObjects.Settlements.ToList())
                    {
                        // 🔴 "EVERY existing settlement" cannot mean the player's own.
                        // MapParent.Destroy does NOT refuse when a map is attached - it
                        // calls Notify_LeftBehind on every thing and destroys the world
                        // object anyway, orphaning the colony's map. An authoring import
                        // run against a live campaign would delete the player's base.
                        if ((player != null && st.Faction == player) || st.HasMap)
                        {
                            keptPlayer++;
                            continue;
                        }
                        // An empty catch here hid the difference between "cleared" and
                        // "refused to clear" and left the count quietly short.
                        try { st.Destroy(); removed++; }
                        catch (Exception e)
                        {
                            if (failures.Count < 25)
                                failures.Add(new { tile = (int)st.Tile, name = st.Name,
                                                   error = "clearExisting: Destroy() threw " +
                                                           e.GetType().Name + ": " + e.Message });
                        }
                    }
                }

                foreach (var kv in plan)
                {
                    // ⚠️ Without this, importing onto a world that still has its
                    // generated roster STACKS two settlements on one tile. The lint
                    // catches it afterwards, but a tool that creates a defect its
                    // sibling then reports is a poor trade. clearExisting=true makes
                    // this branch unreachable, which is the intended path.
                    if (Find.WorldObjects.ObjectsAt(new PlanetTile(kv.Value.Key, grid.Surface))
                                         .Any(o => o is Settlement))
                    {
                        skippedOccupied++;
                        if (failures.Count < 25)
                            failures.Add(new { tile = kv.Value.Key, name = kv.Value.Value,
                                               error = "a settlement already occupies this tile - skipped rather " +
                                                       "than stacked. Re-run with clearExisting=true for a clean roster." });
                        continue;
                    }
                    try
                    {
                        var wo = WorldObjectMaker.MakeWorldObject(WorldObjectDefOf.Settlement);
                        wo.Tile = new PlanetTile(kv.Value.Key, grid.Surface);
                        wo.SetFaction(kv.Key);
                        var st = wo as Settlement;
                        if (st != null && !string.IsNullOrEmpty(kv.Value.Value)) st.Name = kv.Value.Value;
                        Find.WorldObjects.Add(wo);
                        created++;
                    }
                    catch (Exception e)
                    { failures.Add(new { tile = kv.Value.Key, name = kv.Value.Value,
                                         error = e.GetType().Name + ": " + e.Message }); }
                }

                // 🔴 Read back off the engine, not off the loop counter.
                int after = Find.WorldObjects.Settlements.Count;
                int nullFaction = Find.WorldObjects.Settlements.Count(q => q.Faction == null);
                return new
                {
                    success = failures.Count == 0 && nullFaction == 0 && skippedOccupied == 0,
                    message = "created " + created + ", removed " + removed + "; settlements " +
                              before + " -> " + after +
                              (keptPlayer > 0 ? "  (" + keptPlayer + " player-owned or mapped " +
                                                "settlement(s) were NOT cleared - destroying one " +
                                                "orphans its map.)" : "") +
                              (nullFaction > 0 ? "  🔴 " + nullFaction + " HAVE A NULL FACTION and will be " +
                                                 "destroyed on the next load." : ""),
                    rows = csv.Rows.Count, created, removed, skippedOccupied,
                    keptPlayerOwned = keptPlayer,
                    settlementsBefore = before, settlementsAfter = after,
                    nullFactionSettlements = nullFaction,
                    failures,
                    note = "Run jawa/world_commit - FastTileFinder caches settlement tiles. Then SAVE " +
                           "AND RELOAD before trusting this: the null-faction trap only fires on load.",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/world_features_import - W9 STAGE 7, the named regions
        //
        //  The source is the `region` column of the SAME tiles CSV the
        //  biome import reads - 23 names over ~10,765 of 21,872 tiles on
        //  Ash'karr, with the rest deliberately unnamed. No second file to
        //  keep in step, which is the point.
        //
        //  🔑 TWO THINGS THAT ARE NOT OPTIONAL, both learned in W6:
        //   1. `Find.WorldFeatures.textsCreated = false` is the commit step
        //      FOR LABELS and is separate from draw-layer regeneration.
        //      Without it the OLD text keeps drawing over the new regions.
        //   2. Membership is a field on the tile (`tile.feature`), and
        //      `WorldFeature.Tiles` is a full-grid scan. So every count and
        //      every clear here is done in ONE pass over the grid, not once
        //      per feature - 23 features x 21,872 tiles is a half-million
        //      tile reads for a number nobody needed that precisely.
        // ================================================================
        [Tool(
            "jawa/world_features_import",
            Description =
                "Create the authored named regions from the `region` column of the tiles CSV " +
                "and assign every tile to its region. Blank region cells are left unnamed on " +
                "purpose - an unnamed tile is a design choice, not a gap. Existing features " +
                "are cleared first by default so the roster matches the file exactly rather " +
                "than accumulating. Dry run by default.",
            ResultDescription =
                "created, tilesAssigned, and a per-region tile count READ BACK off the grid " +
                "after the write. Run jawa/world_commit afterwards; label text is invalidated " +
                "here via textsCreated, which world_commit does not do.")]
        public static async Task<object> WorldFeaturesImport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Absolute path to the tiles CSV (the one with a `region` column).")]
            string path = null,
            [ToolParameter(Description = "Write for real. Default false (dry run).", DefaultValue = false)]
            bool apply = false,
            [ToolParameter(Description =
                "Refuse unless WorldGrid.TilesCount equals this. 0 = no check.", DefaultValue = 0)]
            int expectTiles = 0,
            [ToolParameter(Description =
                "FeatureDef to create each region as. Default 'Region'.", DefaultValue = "Region")]
            string featureDef = "Region",
            [ToolParameter(Description =
                "Delete every existing feature first so the roster matches the file exactly. " +
                "On by default - leaving the generated regions in place gives a planet with " +
                "two overlapping naming schemes.", DefaultValue = true)]
            bool clearExisting = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a WORLD loaded.");
                if (expectTiles > 0 && grid.TilesCount != expectTiles)
                    return Fail("REFUSING: WorldGrid.TilesCount is " + grid.TilesCount + ", expected " +
                                expectTiles + ".");
                var wf = Find.World.features;
                if (wf == null || wf.features == null) return Fail("No feature manager on this world.");

                var fd = DefDatabase<FeatureDef>.GetNamedSilentFail((featureDef ?? "Region").Trim());
                if (fd == null) return Fail("No FeatureDef '" + featureDef + "'.", DefSuggestions<FeatureDef>(featureDef));

                string err; var csv = ReadTileCsv2(path, out err);
                if (csv == null) return Fail(err);
                if (!csv.Col.ContainsKey("region"))
                    return Fail("CSV has no 'region' column. Header: " + string.Join(",", csv.Header.ToArray()));

                // name -> tile ids, in one pass over the file.
                var byName = new Dictionary<string, List<int>>(StringComparer.Ordinal);
                int blank = 0, badTile = 0;
                for (int r = 0; r < csv.Rows.Count; r++)
                {
                    var row = csv.Rows[r];
                    int tile;
                    if (!int.TryParse(Cell(csv, row, "tile"), out tile) || tile < 0 || tile >= grid.TilesCount)
                    { badTile++; continue; }
                    var nm = (Cell(csv, row, "region") ?? "").Trim();
                    if (nm.Length == 0) { blank++; continue; }
                    List<int> lst;
                    if (!byName.TryGetValue(nm, out lst)) { lst = new List<int>(); byName[nm] = lst; }
                    lst.Add(tile);
                }

                if (!apply)
                    return new
                    {
                        success = true, dryRun = true,
                        rows = csv.Rows.Count, regions = byName.Count,
                        tilesNamed = byName.Values.Sum(q => q.Count),
                        tilesLeftUnnamed = blank, unparseableTiles = badTile,
                        existingFeatures = wf.features.Count,
                        wouldDeleteExisting = clearExisting ? wf.features.Count : 0,
                        preview = byName.OrderByDescending(q => q.Value.Count)
                                        .Take(12).Select(q => new { region = q.Key, tiles = q.Value.Count }).ToList(),
                        note = "DRY RUN - nothing was written. Pass apply=true.",
                        ticksGame = TicksGameSafe(),
                    };

                int n = grid.TilesCount;
                int removed = 0;

                // Baseline BEFORE this call writes anything, so success can be judged
                // against what THIS call was supposed to add rather than the grid's raw
                // absolute counts - with clearExisting=false, pre-existing features and
                // named tiles are still there afterwards and would otherwise make the
                // equality check below fail even when every new row landed correctly.
                int featuresBefore = wf.features.Count;
                int namedBefore = 0;
                for (int i = 0; i < n; i++) { var t0 = grid[i]; if (t0 != null && t0.feature != null) namedBefore++; }

                if (clearExisting)
                {
                    // Clear membership in ONE grid pass, then drop the features.
                    for (int i = 0; i < n; i++) { var t = grid[i]; if (t != null) t.feature = null; }
                    removed = wf.features.Count;
                    wf.features.Clear();
                }

                var made = new Dictionary<string, WorldFeature>(StringComparer.Ordinal);
                foreach (var kv in byName)
                {
                    var f = new WorldFeature(fd, grid.Surface);
                    f.name = kv.Key;
                    wf.features.Add(f);
                    made[kv.Key] = f;
                }

                int assigned = 0;
                foreach (var kv in byName)
                {
                    var f = made[kv.Key];
                    foreach (var tile in kv.Value)
                    {
                        var t = grid[tile];
                        if (t == null) continue;
                        t.feature = f;
                        assigned++;
                    }
                    // Centre the label on the region's own tiles, or every label
                    // draws at the origin and the planet reads as one big blur.
                    if (kv.Value.Count > 0)
                    {
                        var mid = kv.Value[kv.Value.Count / 2];
                        f.drawCenter = grid.GetTileCenter(mid);
                        // Scale the label to the region it names. Left unset, every
                        // label draws at the same size and a 63-tile region shouts
                        // as loudly as a 1,692-tile sea. sqrt because the label is a
                        // LENGTH across an AREA of tiles.
                        f.maxDrawSizeInTiles = Math.Max(6f, (float)Math.Sqrt(kv.Value.Count) * 2.2f);
                    }
                }

                // 🔴 The label commit. Separate from world_commit on purpose.
                wf.textsCreated = false;

                // Read back off the grid, one pass, not once per feature.
                var counts = new Dictionary<int, int>();
                for (int i = 0; i < n; i++)
                {
                    var t = grid[i];
                    if (t == null || t.feature == null) continue;
                    int id = t.feature.uniqueID;
                    counts[id] = counts.ContainsKey(id) ? counts[id] + 1 : 1;
                }
                int liveNamed = counts.Values.Sum();

                // clearExisting already zeroed the live grid, so the "before" baseline
                // for that path IS zero; clearExisting=false carries the pre-existing
                // counts captured above forward instead of comparing against them raw.
                int featuresBaseline = clearExisting ? 0 : featuresBefore;
                int namedBaseline = clearExisting ? 0 : namedBefore;

                return new
                {
                    success = liveNamed == namedBaseline + assigned
                           && wf.features.Count == featuresBaseline + byName.Count,
                    message = "created " + byName.Count + " region(s), removed " + removed +
                              ", assigned " + assigned + " tile(s); grid reports " + liveNamed +
                              " named tile(s) across " + wf.features.Count + " feature(s).",
                    regionsCreated = byName.Count, featuresRemoved = removed,
                    tilesAssigned = assigned, tilesNamedOnGrid = liveNamed,
                    tilesLeftUnnamed = n - liveNamed,
                    regions = wf.features.Select(q => new
                    {
                        id = q.uniqueID, name = q.name,
                        tiles = counts.ContainsKey(q.uniqueID) ? counts[q.uniqueID] : 0,
                    }).OrderByDescending(q => q.tiles).ToList(),
                    note = "textsCreated was reset here, which is what rebuilds the DRAWN labels. " +
                           "Still run jawa/world_commit for the draw layers themselves.",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

    }
}
