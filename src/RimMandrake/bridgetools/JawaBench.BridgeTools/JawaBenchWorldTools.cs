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
            int centerTile = -1)
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
                if (show && centerTile >= 0 && Find.WorldGrid != null
                    && centerTile < Find.WorldGrid.TilesCount && Find.WorldCameraDriver != null)
                {
                    try { Find.WorldCameraDriver.JumpTo(centerTile); centered = centerTile; }
                    catch (Exception e) { Log.Warning("[JawaBench] world_view: JumpTo failed: " + e.Message); }
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

        private static TileCsv ReadTileCsv(string path, out string err)
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
            if (!csv.Col.ContainsKey("tile")) { err = "CSV has no 'tile' column. Header: " + string.Join(",", csv.Header.ToArray()); return null; }
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
                "success, dryRun, rows, applied, skipped, unknownBiomes[], errors[], sample[].")]
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
                int applied = 0, skipped = 0, rows = 0;

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
                    if (bname != null)
                    {
                        if (!biomeCache.TryGetValue(bname, out bd))
                        {
                            bd = DefDatabase<BiomeDef>.GetNamedSilentFail(bname);
                            biomeCache[bname] = bd;
                        }
                        if (bd == null) unknownBiomes.Add(bname);
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

                    if (!apply) { applied++; continue; }

                    if (bd != null) t.PrimaryBiome = bd;
                    if (elevS != null && F(elevS, out fv)) t.elevation = fv;
                    if (tempS != null && F(tempS, out fv)) t.temperature = fv;
                    if (rainS != null && F(rainS, out fv)) t.rainfall = fv;
                    if (swS != null && F(swS, out fv)) t.swampiness = fv;
                    if (poS != null && F(poS, out fv)) t.pollution = fv;
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
                    skipped,
                    tilesCount = grid.TilesCount,
                    unknownBiomes = unknownBiomes.ToList(),
                    note = apply
                        ? "Written. Nothing is visible until jawa/world_commit runs."
                        : "DRY RUN - nothing was written. Pass apply=true.",
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
                        if (n > 0) { removed += n; touched.Add(a); }
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

        private static TileCsv ReadTileCsv2(string path, out string err) { return ReadTileCsv(path, out err); }

        [Tool(
            "jawa/world_links_import",
            Description =
                "Import rivers and roads from a CSV file with columns kind,a,b,def " +
                "(kind is 'river' or 'road'; a and b are adjacent tile ids). Rivers are " +
                "laid before roads, and rivers are applied IN FILE ORDER so the file must " +
                "already be mouth-first. Dry run by default; pass apply=true. " +
                "Optionally clears existing links on the touched tiles first. " +
                "Does not redraw; call jawa/world_commit after.",
            ResultDescription = "success, dryRun, rows, rivers, roads, refused[], unknownDefs[].")]
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

                string err; var csv = ReadTileCsv2(path, out err);
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
                    foreach (var id in touched)
                    {
                        string e; var t = SurfaceTileAt(id, out e);
                        if (t == null) continue;
                        if (t.potentialRivers != null) t.potentialRivers.Clear();
                        if (t.potentialRoads != null) t.potentialRoads.Clear();
                    }
                }

                // Rivers first, in file order (mouth-first is the file's responsibility),
                // then roads - matching the order vanilla's own worldgen steps use.
                foreach (var pass in new[] { true, false })
                    foreach (var p in pending)
                    {
                        if (p.Item1 != pass) continue;
                        string e1, e2;
                        var ta = SurfaceTileAt(p.Item2, out e1); var tb = SurfaceTileAt(p.Item3, out e2);
                        if (ta == null || tb == null) { if (refused.Count < 30) refused.Add(new { from = p.Item2, to = p.Item3, why = e1 ?? e2 }); continue; }

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
                "no water-covered neighbour. Optionally compares against a links CSV.",
            ResultDescription = "success, riverEntries, roadEntries, asymmetric[], nonAdjacent[], hidden[], landlockedRivers.")]
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
                        if (!b.allowRivers && hasRiver && hidden.Count < limit)
                            hidden.Add(new { tile = i, kind = "river", biome = b.defName, links = t.potentialRivers.Count });
                        if (!b.allowRoads && t.potentialRoads != null && t.potentialRoads.Count > 0 && hidden.Count < limit)
                            hidden.Add(new { tile = i, kind = "road", biome = b.defName, links = t.potentialRoads.Count });
                    }

                    nbrs.Clear(); grid.GetTileNeighbors(i, nbrs);

                    if (t.potentialRivers != null)
                        foreach (var l in t.potentialRivers)
                        {
                            riverEntries++;
                            int far = l.neighbor.tileId;
                            if (!nbrs.Any(x => x.tileId == far)) { if (nonAdj.Count < limit) nonAdj.Add(new { tile = i, to = far, kind = "river" }); continue; }
                            var tf = (far >= 0 && far < n) ? grid[far] as SurfaceTile : null;
                            bool mirror = tf != null && tf.potentialRivers != null && tf.potentialRivers.Any(x => x.neighbor.tileId == i);
                            if (!mirror && asym.Count < limit) asym.Add(new { tile = i, to = far, kind = "river", def = l.river != null ? l.river.defName : null });
                        }

                    if (t.potentialRoads != null)
                        foreach (var l in t.potentialRoads)
                        {
                            roadEntries++;
                            int far = l.neighbor.tileId;
                            if (!nbrs.Any(x => x.tileId == far)) { if (nonAdj.Count < limit) nonAdj.Add(new { tile = i, to = far, kind = "road" }); continue; }
                            var tf = (far >= 0 && far < n) ? grid[far] as SurfaceTile : null;
                            bool mirror = tf != null && tf.potentialRoads != null && tf.potentialRoads.Any(x => x.neighbor.tileId == i);
                            if (!mirror && asym.Count < limit) asym.Add(new { tile = i, to = far, kind = "road", def = l.road != null ? l.road.defName : null });
                        }

                    // A river tile with no water neighbour is a candidate "reaches no sea".
                    // The owner's ruling: only HIGH-accumulation trunks must reach a sea,
                    // so this is a count to look at, never an automatic defect.
                    if (hasRiver && !nbrs.Any(x => { var q = grid[x.tileId] as SurfaceTile; return q != null && q.WaterCovered; }))
                        landlocked++;
                }

                return (object)new
                {
                    success = true,
                    tilesScanned = n,
                    riverEntries, roadEntries, riverTiles,
                    asymmetricCount = asym.Count, nonAdjacentCount = nonAdj.Count,
                    hiddenByBiomeCount = hidden.Count,
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
                "🔴 LandmarkDef.IsValidTile refuses a tile that already holds a SETTLEMENT, an " +
                "existing landmark, an impassable biome or hilliness, or a mutator with " +
                "preventsLandmarks. Place landmarks BEFORE settlements. Pass checkValid=true " +
                "to have that verdict reported rather than discovering it as a silent no-op.",
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
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
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
                int nullFacN = 0, badTileN = 0, waterN = 0, impassN = 0;

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

                foreach (var kv in perTile)
                    if (kv.Value > 1 && stacked.Count < limit)
                        stacked.Add(new { tile = kv.Key, settlements = kv.Value });

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
                    stackedTiles = stacked.Count,
                    nullFaction = nullFac, badTile = badTile,
                    onWater = onWater, onImpassable = onImpass, stacked,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

    }
}