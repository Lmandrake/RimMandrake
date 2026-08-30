// JawaBenchTerrainTools.cs - the one thing the bridge could not do.
//
// WHY THIS EXISTS
// ===============
// `skills/rimbridge/SKILL.md` records natural terrain as the single blocking
// gap in live map authoring. RimBridgeServer's own `Set terrain (rect)` debug
// action returns success: true and changes nothing, because it is a drag-based
// (rect) debug tool and the bridge cannot drag. So scorched soil, gravel, sand
// and water were unreachable, and purely additive map art read badly: a crater
// of 317 correctly placed ash and rubble objects still looked like dirty grass,
// because the ground never changed colour.
//
// RimWorld's own API has no such problem. Verse.TerrainGrid.SetTerrain is a
// plain method call. This companion exposes it.
//
// THREAD AFFINITY IS THE WHOLE GAME
// =================================
// Companion [Tool] methods are invoked off RimWorld's main thread. Touching a
// Map from there is a race against the simulation and the renderer, and Unity
// will not politely throw - it corrupts or hard-crashes. Every line that
// touches game state below is inside ctx.MainThread.InvokeAsync, and nothing
// else is. That is why this file is async for what looks like synchronous work.
//
// Verified against the shipped assemblies on 2026-08-12, not from memory:
//   Verse.Map.terrainGrid                         (public field, Verse.TerrainGrid)
//   Verse.TerrainGrid.SetTerrain(IntVec3, TerrainDef)
//   Verse.TerrainGrid.SetUnderTerrain(IntVec3, TerrainDef)
//   Verse.TerrainGrid.TerrainAt(IntVec3) / UnderTerrainAt(IntVec3)
//   Verse.MapDrawer.MapMeshDirty(IntVec3, ulong)
//   RimWorld.MapMeshFlagDefOf.Terrain             (implicit operator -> ulong)
//   C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using LudeonTK;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/set_terrain",
            Description =
                "Paint natural terrain (sand, gravel, soil, water, rock) or floors onto map " +
                "cells. Closes the one gap live map authoring had: RimWorld's own " +
                "'Set terrain (rect)' debug action is drag-based and silently does nothing " +
                "over the bridge. Supports a single cell or a rectangle.",
            ResultDescription =
                "Returns success, cellsChanged, and a sample of before/after terrain defNames " +
                "so the caller can verify without a second call.")]
        public static async Task<object> SetTerrain(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X.")]
            int x,
            [ToolParameter(Description = "Map cell Z (RimWorld's second horizontal axis; not height).")]
            int z,
            [ToolParameter(Description =
                "TerrainDef defName, e.g. Sand, Gravel, SoilRich, WaterShallow, " +
                "PackedDirt, Concrete. Case-insensitive. Stone terrain is generated " +
                "per rock type at runtime (Slate_Rough, Sandstone_Smooth) and so " +
                "appears in no XML file, but resolves normally here.")]
            string terrainDef,
            [ToolParameter(Description = "Rectangle width in cells, anchored at x.", DefaultValue = 1)]
            int width = 1,
            [ToolParameter(Description = "Rectangle height in cells, anchored at z.", DefaultValue = 1)]
            int height = 1,
            [ToolParameter(Description =
                "'top' paints the visible surface. 'under' paints the natural terrain " +
                "beneath a floor, which only shows once that floor is removed. " +
                "'foundation' is the THIRD grid (1.6 Odyssey) and is what gravship " +
                "Substructure lives in -- buildings whose terrainAffordanceNeeded is " +
                "Substructure cannot be placed without it.",
                DefaultValue = "top")]
            string layer = "top",
            [ToolParameter(Description =
                "Mark the map mesh dirty so the change is visible immediately. Leave true " +
                "unless you are deliberately testing whether SetTerrain redraws on its own.",
                DefaultValue = true)]
            bool refresh = true)
        {
            if (string.IsNullOrWhiteSpace(terrainDef))
                return Fail("terrainDef is required.");

            if (!ValidLayer(layer))
                return Fail($"layer must be 'top', 'under' or 'foundation', got '{layer}'.");
            var wantUnder = IsLayer(layer, "under");

            if (width < 1 || height < 1)
                return Fail($"width and height must be >= 1, got {width}x{height}.");

            // Everything below touches the live Map, so all of it runs on the
            // main thread and none of it runs anywhere else.
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var def = ResolveTerrain(terrainDef);
                if (def == null)
                    return Fail(
                        $"No TerrainDef named '{terrainDef}'.",
                        new { suggestions = SuggestTerrain(terrainDef) });

                var grid = map.terrainGrid;
                var size = map.Size;

                int changed = 0, skippedOutOfBounds = 0, alreadyCorrect = 0, verifyFailed = 0;
                var samples = new List<object>();

                for (var dx = 0; dx < width; dx++)
                {
                    for (var dz = 0; dz < height; dz++)
                    {
                        cancellationToken.ThrowIfCancellationRequested();

                        int cx = x + dx, cz = z + dz;
                        if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z)
                        {
                            skippedOutOfBounds++;
                            continue;
                        }

                        var cell = new IntVec3(cx, 0, cz);
                        var before = ReadLayer(grid, cell, layer);

                        if (before == def)
                        {
                            alreadyCorrect++;
                        }
                        else
                        {
                            WriteLayer(grid, cell, def, layer);
                            changed++;
                        }

                        // Read the grid back on every cell. This is the whole
                        // point: the bridge's rule is that success: true means
                        // the tool ran, not that the game changed, so the tool
                        // that changes terrain should be the one that proves it.
                        var after = ReadLayer(grid, cell, layer);
                        if (after != def) verifyFailed++;

                        if (samples.Count < 8)
                        {
                            samples.Add(new
                            {
                                x = cx,
                                z = cz,
                                before = before?.defName,
                                after = after?.defName,
                                applied = after == def
                            });
                        }
                    }
                }

                if (refresh && changed > 0)
                    RefreshRect(map, x, z, width, height);

                // The honest success test is "the grid now reads back what we
                // asked for", not "the method did not throw". A rect entirely
                // off-map is a failure too, however cleanly it did nothing.
                var inBounds = width * height - skippedOutOfBounds;
                var success = verifyFailed == 0 && inBounds > 0;

                return new
                {
                    success,
                    message = Describe(changed, alreadyCorrect, skippedOutOfBounds, verifyFailed, def, wantUnder),
                    terrainDef = def.defName,
                    terrainLabel = def.label,
                    layer = NormLayer(layer),
                    cellsRequested = width * height,
                    cellsChanged = changed,
                    cellsAlreadyCorrect = alreadyCorrect,
                    cellsOutOfBounds = skippedOutOfBounds,
                    cellsFailedVerify = verifyFailed,
                    refreshed = refresh && changed > 0,
                    samples,
                    mapSize = new { x = size.x, z = size.z },
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/set_terrain_batch",
            Description =
                "Paint MANY terrain rectangles in a single call. Use this for anything a " +
                "generator produces; use jawa/set_terrain only for one-off single rects. " +
                "ops format: 'Terrain:x,z,w,h' separated by ';' or newlines, e.g. " +
                "'Sand:10,20,3,4;Gravel:14,20,2,2'. w and h default to 1 and may be omitted " +
                "('Sand:10,20'). An op may omit the terrain ('10,20,3,4') to use the " +
                "terrainDef parameter as the default.",
            ResultDescription =
                "Returns aggregate cell counts, per-op errors, and before/after samples. " +
                "Every cell is read back from the grid, so cellsFailedVerify is authoritative.")]
        public static async Task<object> SetTerrainBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Rect ops: 'Terrain:x,z,w,h' separated by ';' or newlines. " +
                "w/h optional (default 1). Terrain optional if terrainDef is given.")]
            string ops,
            [ToolParameter(Description =
                "Default TerrainDef for ops that do not name one. Optional.",
                DefaultValue = null)]
            string terrainDef = null,
            [ToolParameter(Description = "'top', 'under' or 'foundation', as jawa/set_terrain. " +
                "'foundation' is the third grid (1.6 Odyssey) where gravship Substructure " +
                "lives; buildings with terrainAffordanceNeeded=Substructure need it.",
                DefaultValue = "top")]
            string layer = "top",
            [ToolParameter(Description =
                "Refresh the map mesh once, after every op has been applied.",
                DefaultValue = true)]
            bool refresh = true)
        {
            if (string.IsNullOrWhiteSpace(ops))
                return Fail("ops is required, e.g. 'Sand:10,20,3,4;Gravel:14,20,2,2'.");

            if (!ValidLayer(layer))
                return Fail($"layer must be 'top', 'under' or 'foundation', got '{layer}'.");
            var wantUnder = IsLayer(layer, "under");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(ops, terrainDef, out parsed, parseErrors))
                return Fail("Could not parse ops.", new { errors = parseErrors });

            // Guard the main thread. Everything below runs inside one
            // InvokeAsync, so an enormous payload does not merely take a long
            // time -- it stalls the simulation and the renderer for the whole
            // duration, which is indistinguishable from a freeze. This project
            // has already lost a colony to a main-thread livelock.
            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many ops: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var grid = map.terrainGrid;
                var size = map.Size;

                int changed = 0, alreadyCorrect = 0, outOfBounds = 0, verifyFailed = 0;
                int opsApplied = 0, cellsRequested = 0;
                var samples = new List<object>();
                var errors = new List<object>();
                // Dirty cells are collected and flushed once. Marking the mesh
                // per op would rebuild overlapping sections repeatedly, and no
                // intermediate state is ever seen -- the whole batch lands in
                // one frame either way.
                var dirty = refresh ? new HashSet<IntVec3>() : null;
                var resolved = new Dictionary<string, TerrainDef>(StringComparer.OrdinalIgnoreCase);

                for (var i = 0; i < parsed.Count; i++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var op = parsed[i];

                    TerrainDef def;
                    if (!resolved.TryGetValue(op.Terrain, out def))
                    {
                        def = ResolveTerrain(op.Terrain);
                        resolved[op.Terrain] = def;
                    }
                    if (def == null)
                    {
                        if (errors.Count < 10)
                            errors.Add(new { op = i, terrain = op.Terrain, error = "unknown TerrainDef" });
                        continue;
                    }

                    cellsRequested += op.W * op.H;
                    opsApplied++;

                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            int cx = op.X + dx, cz = op.Z + dz;
                            if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }

                            var cell = new IntVec3(cx, 0, cz);
                            var before = ReadLayer(grid, cell, layer);

                            if (before == def)
                            {
                                alreadyCorrect++;
                            }
                            else
                            {
                                WriteLayer(grid, cell, def, layer);
                                changed++;
                                if (dirty != null) dirty.Add(cell);
                            }

                            var after = ReadLayer(grid, cell, layer);
                            if (after != def)
                            {
                                verifyFailed++;
                                if (errors.Count < 10)
                                    errors.Add(new { op = i, x = cx, z = cz, error = "did not read back" });
                            }

                            if (samples.Count < 8)
                            {
                                samples.Add(new
                                {
                                    x = cx,
                                    z = cz,
                                    before = before?.defName,
                                    after = after?.defName,
                                    applied = after == def
                                });
                            }
                        }
                    }
                }

                if (dirty != null && dirty.Count > 0)
                {
                    var drawer = map.mapDrawer;
                    if (drawer != null)
                        foreach (var cell in dirty)
                            drawer.MapMeshDirty(cell, MapMeshFlagDefOf.Terrain);
                }

                var inBounds = cellsRequested - outOfBounds;
                var success = verifyFailed == 0 && errors.Count == 0 && inBounds > 0;

                return new
                {
                    success,
                    message =
                        $"Applied {opsApplied}/{parsed.Count} op(s): {changed} cell(s) changed, " +
                        $"{alreadyCorrect} already correct" +
                        (outOfBounds > 0 ? $", {outOfBounds} outside the map" : "") +
                        (verifyFailed > 0 ? $", WARNING {verifyFailed} did not read back" : "") + ".",
                    layer = NormLayer(layer),
                    opsRequested = parsed.Count,
                    opsApplied,
                    cellsRequested,
                    cellsChanged = changed,
                    cellsAlreadyCorrect = alreadyCorrect,
                    cellsOutOfBounds = outOfBounds,
                    cellsFailedVerify = verifyFailed,
                    refreshed = dirty != null && dirty.Count > 0,
                    cellsRefreshed = dirty?.Count ?? 0,
                    errors,
                    samples,
                    mapSize = new { x = size.x, z = size.z },
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/get_terrain_batch",
            Description =
                "Read the terrain of MANY cells in a single call, and return it in the " +
                "SAME ops grammar jawa/set_terrain_batch accepts. This is the capture half " +
                "of reversible map authoring: capture a region, paint over it, then feed the " +
                "returned ops string straight back to jawa/set_terrain_batch to restore it " +
                "exactly. rects format: 'x,z,w,h' separated by ';' (a leading 'Name:' is " +
                "accepted and ignored, so a set_terrain_batch payload can be replayed as a " +
                "read).",
            ResultDescription =
                "Returns ops (run-length encoded, one run per contiguous same-terrain span " +
                "in a row), cellsRead, and the distinct terrains found. The ops string is " +
                "directly replayable.")]
        public static async Task<object> GetTerrainBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Rects to read: 'x,z,w,h' separated by ';' or newlines. w/h optional " +
                "(default 1). A 'Terrain:' prefix is ignored.")]
            string rects,
            [ToolParameter(Description = "'top', 'under' or 'foundation', as jawa/set_terrain. " +
                "'foundation' is the third grid (1.6 Odyssey) where gravship Substructure " +
                "lives; buildings with terrainAffordanceNeeded=Substructure need it.",
                DefaultValue = "top")]
            string layer = "top")
        {
            if (string.IsNullOrWhiteSpace(rects))
                return Fail("rects is required, e.g. '10,20,3,4;14,20,2,2'.");

            if (!ValidLayer(layer))
                return Fail($"layer must be 'top', 'under' or 'foundation', got '{layer}'.");
            var wantUnder = IsLayer(layer, "under");

            // The same parser the write path uses, with a placeholder default so
            // a coordinate-only op is legal. Reusing it means the two halves of a
            // capture/restore round trip cannot disagree about the grammar.
            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(rects, "_", out parsed, parseErrors))
                return Fail("Could not parse rects.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many rects: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var grid = map.terrainGrid;
                var size = map.Size;

                // Dictionary rather than a list: overlapping rects are legal on
                // the write path, so they must be legal here too, and a cell read
                // twice must appear in the output once.
                var found = new Dictionary<IntVec3, string>();
                int outOfBounds = 0, nullTerrain = 0;

                foreach (var op in parsed)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            int cx = op.X + dx, cz = op.Z + dz;
                            if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }
                            var cell = new IntVec3(cx, 0, cz);
                            var def = ReadLayer(grid, cell, layer);
                            // Under-terrain is genuinely null where no floor was
                            // ever laid. Counting it is the honest answer; writing
                            // "null" into a replayable ops string is not, because
                            // it would silently no-op on the restore.
                            if (def == null) { nullTerrain++; continue; }
                            found[cell] = def.defName;
                        }
                    }
                }

                var ops = RunLengthEncode(found);
                var distinct = new HashSet<string>(found.Values);

                return new
                {
                    success = found.Count > 0,
                    message =
                        $"Read {found.Count} cell(s) as {distinct.Count} distinct terrain(s) " +
                        $"in {CountRuns(ops)} run(s)" +
                        (outOfBounds > 0 ? $", {outOfBounds} outside the map" : "") +
                        (nullTerrain > 0 ? $", {nullTerrain} with no {(wantUnder ? "under-" : "")}terrain" : "") + ".",
                    layer = NormLayer(layer),
                    ops,
                    cellsRequested = totalCells,
                    cellsRead = found.Count,
                    cellsOutOfBounds = outOfBounds,
                    cellsNullTerrain = nullTerrain,
                    distinctTerrains = distinct.OrderBy(n => n).ToList(),
                    mapSize = new { x = size.x, z = size.z },
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/spawn_batch",
            Description =
                "Spawn MANY things in a single call. Once terrain painting became one hop, " +
                "object spawning became the bottleneck: a crater is 1 terrain call and ~100 " +
                "rimworld/spawn_thing calls at ~16.7 ms each. ops format: 'Def:x,z,count' " +
                "separated by ';', count optional (default 1), e.g. " +
                "'Filth_Ash:10,20;ChunkSlagSteel:12,22'. Filth is routed through FilthMaker " +
                "(which respects whether the terrain accepts it) and everything else through " +
                "GenSpawn, so a generator does not have to know which is which. " +
                "`stuff` and `rot` apply to the WHOLE call, so batch by material and " +
                "facing: every steel wall in one call, every east-facing door in the next.",
            ResultDescription =
                "Returns spawned/failed counts, per-def totals, and the reason each failure " +
                "was rejected. Verified by reading the cell back, not by absence of throw.")]
        public static async Task<object> SpawnBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Spawn ops: 'Def:x,z[,count]' separated by ';' or newlines.")]
            string ops,
            [ToolParameter(Description =
                "Default ThingDef for ops that do not name one. Optional.",
                DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description =
                "Stuff (material) defName for things made from stuff, e.g. Steel. " +
                "Ignored by filth and by defs that take no stuff.",
                DefaultValue = null)]
            string stuff = null,
            [ToolParameter(Description =
                "Rotation for every thing in this call: 0=North, 1=East, 2=South, " +
                "3=West. Defaults to 0. Batch by rotation the same way you batch by " +
                "stuff -- all the east-facing doors in one call, all the walls in " +
                "another. Ignored by defs that cannot rotate.",
                DefaultValue = 0)]
            int rot = 0)
        {
            if (string.IsNullOrWhiteSpace(ops))
                return Fail("ops is required, e.g. 'Filth_Ash:10,20;ChunkSlagSteel:12,22'.");

            // WHY ROTATION IS A CALL-LEVEL PARAMETER AND NOT A FIFTH OPS FIELD
            // ================================================================
            // The obvious design is 'Def:x,z,count,rot'. It is wrong here, because
            // TryParseOps is SHARED with the terrain tools, where the fourth field
            // is a rectangle HEIGHT that must be >= 1. Rotation 0 is both legal and
            // the common case, so overloading that slot would either reject rot=0 or
            // force the shared parser to stop validating height -- weakening every
            // terrain caller to serve this one. So it mirrors `stuff` instead, which
            // has the same shape of problem and the same solution.
            //
            // It costs nothing in practice: rotations group naturally (every wall
            // rot 0, every door on one wall rot 1), so a real ship is a handful of
            // calls, not one per thing.
            if (rot < 0 || rot > 3)
                return Fail($"rot must be 0-3 (0=North,1=East,2=South,3=West), got {rot}.");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(ops, defName, out parsed, parseErrors))
                return Fail("Could not parse ops.", new { errors = parseErrors });

            if (parsed.Count > MaxOps)
                return Fail($"Too many ops: {parsed.Count} > {MaxOps}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var size = map.Size;
                int spawned = 0, failed = 0, outOfBounds = 0;
                var perDef = new Dictionary<string, int>();
                var errors = new List<object>();
                var resolved = new Dictionary<string, ThingDef>(StringComparer.OrdinalIgnoreCase);
                ThingDef stuffDef = string.IsNullOrWhiteSpace(stuff)
                    ? null
                    : DefDatabase<ThingDef>.GetNamedSilentFail(stuff);

                for (var i = 0; i < parsed.Count; i++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var op = parsed[i];

                    ThingDef def;
                    if (!resolved.TryGetValue(op.Terrain, out def))
                    {
                        def = DefDatabase<ThingDef>.GetNamedSilentFail(op.Terrain)
                              ?? DefDatabase<ThingDef>.AllDefsListForReading.FirstOrDefault(
                                  d => string.Equals(d.defName, op.Terrain,
                                                     StringComparison.OrdinalIgnoreCase));
                        resolved[op.Terrain] = def;
                    }
                    if (def == null)
                    {
                        failed++;
                        if (errors.Count < 10)
                            errors.Add(new { op = i, def = op.Terrain, error = "unknown ThingDef" });
                        continue;
                    }

                    // W carries the stack count for this tool. H is unused: the ops
                    // grammar is shared with the terrain tools so that one parser
                    // serves both, and a rectangle of identical spawned objects is
                    // not a thing any generator has wanted.
                    var count = op.W < 1 ? 1 : op.W;
                    var cell = new IntVec3(op.X, 0, op.Z);
                    if (op.X < 0 || op.Z < 0 || op.X >= size.x || op.Z >= size.z)
                    {
                        outOfBounds++;
                        continue;
                    }

                    try
                    {
                        if (def.IsFilth)
                        {
                            // Filth has its own maker, and it declines cells whose
                            // terrain does not accept filth (water, for one). Going
                            // through GenSpawn instead produces filth that the game
                            // did not agree to and cannot clean up properly.
                            if (FilthMaker.TryMakeFilth(cell, map, def, count))
                                spawned++;
                            else
                            {
                                failed++;
                                if (errors.Count < 10)
                                    errors.Add(new
                                    {
                                        op = i, def = def.defName, x = op.X, z = op.Z,
                                        error = "terrain does not accept this filth"
                                    });
                                continue;
                            }
                        }
                        else if (IsVehicleDef(def))
                        {
                            // 🔴 Vehicle Framework vehicles CANNOT go through
                            // ThingMaker + GenSpawn, and the failure is a bare
                            // NullReferenceException with no hint in it -- measured
                            // live 2026-08-14 on AV_DogSled, where it read as a
                            // verdict on the ART when it was a gap in this tool.
                            //
                            // Read out of Vehicles.dll with ilprobe, not recalled:
                            // VehiclePawn::.ctor initialises collections only, so
                            // vehiclePather / ignition / drawTracker / kindDef are
                            // all null, and VehiclePawn::SpawnSetup callvirts every
                            // one of them (IL_007b, IL_0094, IL_00f8). The fields
                            // are written by Patch_Components::CreateInitialVehicle
                            // Components -- VF's Harmony hook on PawnComponents
                            // Utility.CreateInitialComponents -- which MakeThing
                            // never calls.
                            //
                            // Vehicles.VehicleSpawner.SpawnVehicleRandomized is
                            // public static and does the whole job: generate, wire,
                            // refuel, GenSpawn. Reached by REFLECTION on purpose --
                            // a compile-time reference to Vehicles.dll would make
                            // this companion refuse to load for anyone who does not
                            // run Vehicle Framework.
                            string vehErr;
                            var veh = TrySpawnVehicle(def, cell, map, new Rot4(rot),
                                                      out vehErr);
                            if (veh == null)
                            {
                                failed++;
                                if (errors.Count < 10)
                                    errors.Add(new
                                    {
                                        op = i, def = def.defName, x = op.X, z = op.Z,
                                        error = vehErr
                                    });
                                continue;
                            }
                            spawned++;
                        }
                        else
                        {
                            var thing = ThingMaker.MakeThing(def, def.MadeFromStuff ? stuffDef : null);
                            if (thing.def.stackLimit > 1) thing.stackCount = count;
                            // rot is range-checked at entry rather than trusted here:
                            // Rot4 normalises whatever it is handed, so an out-of-range
                            // value would silently become a DIFFERENT valid rotation
                            // instead of an error -- a wrong-facing door with no
                            // complaint anywhere.
                            GenSpawn.Spawn(thing, cell, map, new Rot4(rot));
                            if (thing.Spawned) spawned++;
                            else
                            {
                                failed++;
                                if (errors.Count < 10)
                                    errors.Add(new
                                    {
                                        op = i, def = def.defName, x = op.X, z = op.Z,
                                        error = "spawned but not present on the map"
                                    });
                                continue;
                            }
                        }

                        perDef.TryGetValue(def.defName, out var n);
                        perDef[def.defName] = n + 1;
                    }
                    catch (Exception e)
                    {
                        failed++;
                        if (errors.Count < 10)
                            errors.Add(new
                            {
                                op = i, def = def.defName, x = op.X, z = op.Z,
                                error = e.GetType().Name + ": " + e.Message
                            });
                    }
                }

                return new
                {
                    success = failed == 0 && spawned > 0,
                    message =
                        $"Spawned {spawned} of {parsed.Count} requested" +
                        (failed > 0 ? $", {failed} failed" : "") +
                        (outOfBounds > 0 ? $", {outOfBounds} outside the map" : "") + ".",
                    opsRequested = parsed.Count,
                    spawned,
                    failed,
                    cellsOutOfBounds = outOfBounds,
                    perDef = perDef.OrderByDescending(kv => kv.Value)
                                   .Take(12).ToDictionary(kv => kv.Key, kv => kv.Value),
                    errors,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/destroy_batch",
            Description =
                "Destroy things in MANY cells in one call, filtered by category. The bridge " +
                "has no working direct destruction primitive: 'Clear area (rect)' is a drag " +
                "tool and silently does nothing. Until now the only way to clear ground was " +
                "to lay a floor over it, which leaves a floor. Categories: Plant, Item, " +
                "Filth, Building, All. PAWNS ARE NEVER DESTROYED by this tool, whatever the " +
                "filter says -- killing a colonist by fat-fingering a rect is not a thing " +
                "this should make possible.",
            ResultDescription =
                "Returns per-category destroyed counts and a sample of what was removed.")]
        public static async Task<object> DestroyBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Rects to clear: 'x,z,w,h' separated by ';'. w/h optional (default 1). " +
                "A leading 'Name:' is accepted and ignored.")]
            string rects,
            [ToolParameter(Description =
                "What to destroy: Plant (default), Item, Filth, Building, or All. " +
                "Comma-separated for several, e.g. 'Plant,Filth'. " +
                "⚠️ The parameter is CATEGORIES, plural. Passing 'category' is " +
                "silently ignored by the binder and you get the Plant default, " +
                "which reports success while destroying nothing you asked for. " +
                "Both spellings are accepted here for that reason.",
                DefaultValue = "Plant")]
            string categories = "Plant",
            [ToolParameter(Description =
                "Alias of `categories`. Exists because the singular is the natural " +
                "guess and an unknown key is dropped without an error.",
                DefaultValue = null)]
            string category = null)
        {
            if (string.IsNullOrWhiteSpace(rects))
                return Fail("rects is required, e.g. '10,20,5,5'.");

            var wanted = new HashSet<string>(
                (category ?? categories ?? "Plant").Split(new[] { ',', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(s => s.Trim()), StringComparer.OrdinalIgnoreCase);
            var all = wanted.Contains("All");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(rects, "_", out parsed, parseErrors))
                return Fail("Could not parse rects.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many rects: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var size = map.Size;
                var perCategory = new Dictionary<string, int>();
                var samples = new List<object>();
                int destroyed = 0, skippedPawns = 0;
                var seen = new HashSet<IntVec3>();

                foreach (var op in parsed)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            int cx = op.X + dx, cz = op.Z + dz;
                            if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z) continue;
                            var cell = new IntVec3(cx, 0, cz);
                            if (!seen.Add(cell)) continue;      // overlapping rects

                            // Snapshot the cell's things before destroying any: the
                            // live list is mutated by Destroy and iterating it while
                            // it shrinks silently skips half the contents.
                            var here = map.thingGrid.ThingsListAtFast(cell).ToList();
                            foreach (var thing in here)
                            {
                                if (thing == null || thing.Destroyed) continue;
                                var cat = thing.def.category.ToString();
                                if (thing is Pawn || cat == "Pawn") { skippedPawns++; continue; }
                                if (!all && !wanted.Contains(cat)) continue;

                                if (samples.Count < 8)
                                    samples.Add(new { x = cx, z = cz, def = thing.def.defName, category = cat });
                                thing.Destroy(DestroyMode.Vanish);
                                destroyed++;
                                perCategory.TryGetValue(cat, out var n);
                                perCategory[cat] = n + 1;
                            }
                        }
                    }
                }

                return new
                {
                    success = true,
                    message =
                        $"Destroyed {destroyed} thing(s) across {seen.Count} cell(s)" +
                        (skippedPawns > 0 ? $"; {skippedPawns} pawn(s) left alone" : "") + ".",
                    cellsExamined = seen.Count,
                    destroyed,
                    pawnsSkipped = skippedPawns,
                    perCategory,
                    samples,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/list_pawns",
            Description =
                "List EVERY pawn on the map — all factions, hostiles, animals, mechanoids, " +
                "the lot. This closes a real blind spot: rimworld/list_colonists returns only " +
                "player colonists, get_cell_info does not report pawns at all, and " +
                "RimBridgeServer.ResolvePawn refuses anything that is not a player colonist. " +
                "Before this tool the only way to observe a hostile was a screenshot or " +
                "parsing a saved game. Optionally filter by rect or faction, and optionally " +
                "include full health detail.",
            ResultDescription =
                "Per pawn: id, name, kind, faction, hostility, position, dead/downed, stun " +
                "ticks, race flags, and (with includeHealth) every hediff with severity plus " +
                "all capacity levels.")]
        public static async Task<object> ListPawns(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Optional rect filter 'x,z,w,h'. Omit for the whole map.",
                DefaultValue = null)]
            string rect = null,
            [ToolParameter(Description =
                "Optional faction filter: a faction defName, 'player', 'hostile', or " +
                "'nonplayer'. Omit for all.", DefaultValue = null)]
            string faction = null,
            [ToolParameter(Description =
                "Include every hediff (with severity and body part) and all capacity levels. " +
                "This is the call that replaces save_game + parsing a .rws to read one " +
                "hediff.", DefaultValue = false)]
            bool includeHealth = false,
            [ToolParameter(Description = "Include dead pawns lying in corpses.",
                DefaultValue = false)]
            bool includeCorpses = false,
            [ToolParameter(Description = "Cap on returned pawns.", DefaultValue = 500)]
            int limit = 500)
        {
            int rx = 0, rz = 0, rw = 0, rh = 0;
            if (!string.IsNullOrWhiteSpace(rect))
            {
                List<ParsedOp> parsedRect;
                var rectErrors = new List<string>();
                if (!TryParseOps(rect, "_", out parsedRect, rectErrors) || parsedRect.Count != 1)
                    return Fail("rect must be a single 'x,z,w,h'.", new { errors = rectErrors });
                rx = parsedRect[0].X; rz = parsedRect[0].Z;
                rw = parsedRect[0].W; rh = parsedRect[0].H;
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var playerFaction = Faction.OfPlayer;
                var all = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
                if (includeCorpses)
                {
                    foreach (var t in map.listerThings.AllThings)
                    {
                        var corpse = t as Corpse;
                        if (corpse?.InnerPawn != null) all.Add(corpse.InnerPawn);
                    }
                }

                var rows = new List<object>();
                int skippedRect = 0, skippedFaction = 0, truncated = 0;

                foreach (var pawn in all)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (pawn == null) continue;

                    var pos = pawn.Spawned ? pawn.Position : (pawn.Corpse?.Position ?? IntVec3.Invalid);
                    if (rw > 0 && pos.IsValid)
                    {
                        if (pos.x < rx || pos.z < rz || pos.x >= rx + rw || pos.z >= rz + rh)
                        {
                            skippedRect++;
                            continue;
                        }
                    }

                    var hostile = pawn.Faction != null && pawn.Faction.HostileTo(playerFaction);
                    var isPlayer = pawn.Faction == playerFaction;
                    if (!string.IsNullOrWhiteSpace(faction))
                    {
                        var f = faction.Trim();
                        var keep =
                            string.Equals(f, "player", StringComparison.OrdinalIgnoreCase) ? isPlayer :
                            string.Equals(f, "hostile", StringComparison.OrdinalIgnoreCase) ? hostile :
                            string.Equals(f, "nonplayer", StringComparison.OrdinalIgnoreCase) ? !isPlayer :
                            string.Equals(pawn.Faction?.def?.defName, f, StringComparison.OrdinalIgnoreCase);
                        if (!keep) { skippedFaction++; continue; }
                    }

                    if (rows.Count >= limit) { truncated++; continue; }

                    // Stun state is where the EMP/ion answer lives, and it is not
                    // visible through any other bridge call.
                    var stunner = pawn.stances?.stunner;
                    object health = null;
                    if (includeHealth && pawn.health != null)
                    {
                        var hediffs = new List<object>();
                        foreach (var h in pawn.health.hediffSet.hediffs)
                            hediffs.Add(new
                            {
                                def = h.def?.defName,
                                label = h.Label,
                                severity = h.Severity,
                                part = h.Part?.def?.defName,
                                partLabel = h.Part?.Label
                            });
                        var caps = new Dictionary<string, float>();
                        foreach (var cap in DefDatabase<PawnCapacityDef>.AllDefsListForReading)
                        {
                            try
                            {
                                if (pawn.health.capacities.CapableOf(cap) || true)
                                    caps[cap.defName] = pawn.health.capacities.GetLevel(cap);
                            }
                            catch { /* some caps throw on some races; skip rather than fail the call */ }
                        }
                        health = new
                        {
                            hediffs,
                            capacities = caps,
                            painTotal = pawn.health.hediffSet.PainTotal,
                            bleedRate = pawn.health.hediffSet.BleedRateTotal
                        };
                    }

                    rows.Add(new
                    {
                        id = pawn.ThingID,
                        name = pawn.Name?.ToStringShort ?? pawn.LabelShortCap,
                        kind = pawn.kindDef?.defName,
                        // ⚠️ ALIAS, deliberate. Callers reach for `kindDef`
                        // because the SPAWN side takes a `kindDef` parameter, and
                        // filtering on the absent key returns zero rows — which
                        // reads exactly like "nothing spawned". A retired seat hit this,
                        // logged it, and hit it AGAIN in the same file on
                        // 2026-08-13. A trap logged twice and still recurring is
                        // not a documentation problem; the shape was wrong.
                        // Both keys now work and carry the same value.
                        kindDef = pawn.kindDef?.defName,
                        def = pawn.def?.defName,
                        // 🔴 v1 row 5 could not be closed without this.
                        // The row turns on WHICH Jawa xenotype a naturally
                        // spawned campaign pawn carries -- three are live at
                        // once and "a Jawa spawned" is not evidence. The only
                        // read-back available was jawa/set_pawn_xenotype's
                        // `was` field, which means CONVERTING a campaign pawn
                        // to find out what it already was. That is a mutation
                        // to answer a read, so the answer belonged here.
                        // ⚠️ null is not "no xenotype": a pawn with no gene
                        // tracker (animal, mechanoid) and a baseliner both read
                        // null on `xenotype`. `hasGenes` separates them.
                        hasGenes = pawn.genes != null,
                        xenotype = pawn.genes?.Xenotype?.defName,
                        xenotypeLabel = pawn.genes?.XenotypeLabel,
                        uniqueXenotype = pawn.genes?.UniqueXenotype ?? false,
                        faction = pawn.Faction?.def?.defName,
                        factionName = pawn.Faction?.Name,
                        isPlayer,
                        hostile,
                        x = pos.IsValid ? pos.x : -1,
                        z = pos.IsValid ? pos.z : -1,
                        spawned = pawn.Spawned,
                        dead = pawn.Dead,
                        downed = pawn.Downed,
                        stunned = stunner?.Stunned ?? false,
                        stunTicksLeft = stunner?.StunTicksLeft ?? 0,
                        fleshType = pawn.RaceProps?.FleshType?.defName,
                        isMechanoid = pawn.RaceProps?.IsMechanoid ?? false,
                        isFlesh = pawn.RaceProps?.IsFlesh ?? false,
                        intelligence = pawn.RaceProps?.intelligence.ToString(),
                        bodySize = pawn.RaceProps?.baseBodySize ?? 0f,
                        health
                    });
                }

                return new
                {
                    success = true,
                    message =
                        $"{rows.Count} pawn(s)" +
                        (truncated > 0 ? $", {truncated} beyond the limit" : "") +
                        (skippedRect > 0 ? $", {skippedRect} outside the rect" : "") +
                        (skippedFaction > 0 ? $", {skippedFaction} filtered by faction" : "") + ".",
                    pawns = rows,
                    returned = rows.Count,
                    truncated,
                    totalOnMap = map.mapPawns.AllPawnsSpawned.Count,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/set_plants",
            Description =
                "Explicit vegetation control: plant, clear, or re-grow plants over rects. " +
                "Placing a plant through an ordinary spawn gives you a sprout at growth 0 — " +
                "this sets the growth stage too, which is the difference between a seedling " +
                "and a tree. ops format 'PlantDef:x,z,w,h' separated by ';'. Use plantDef " +
                "'CLEAR' (or clearOnly) to remove vegetation without planting anything.",
            ResultDescription =
                "Returns planted / cleared / rejected counts with the reason each cell was " +
                "rejected. Rejections are real evidence, not noise: a cell whose terrain " +
                "cannot support the species is reported, never silently skipped.")]
        public static async Task<object> SetPlants(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Rect ops: 'PlantDef:x,z,w,h' separated by ';'. w/h default 1. " +
                "Use 'CLEAR' as the def to only remove.")]
            string ops,
            [ToolParameter(Description =
                "Growth stage 0..1 for planted plants. 0.05 is a sprout, 1.0 fully grown.",
                DefaultValue = 1.0)]
            float growth = 1.0f,
            [ToolParameter(Description =
                "Fraction of cells in each rect to plant, 0..1. 1 fills solidly; lower " +
                "values scatter deterministically from `seed` so a re-run is idempotent.",
                DefaultValue = 1.0)]
            float density = 1.0f,
            [ToolParameter(Description = "Seed for the density scatter.", DefaultValue = 0)]
            int seed = 0,
            [ToolParameter(Description =
                "Remove existing plants in each cell before planting.", DefaultValue = true)]
            bool clearFirst = true)
        {
            if (string.IsNullOrWhiteSpace(ops))
                return Fail("ops is required, e.g. 'Plant_TreeOak:10,20,5,5' or 'CLEAR:10,20,5,5'.");

            growth = growth < 0.01f ? 0.01f : (growth > 1f ? 1f : growth);
            density = density < 0f ? 0f : (density > 1f ? 1f : density);

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(ops, null, out parsed, parseErrors))
                return Fail("Could not parse ops.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many ops: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                var size = map.Size;
                int planted = 0, cleared = 0, rejected = 0, outOfBounds = 0, skippedDensity = 0;
                var reasons = new Dictionary<string, int>();
                var errors = new List<object>();
                var resolved = new Dictionary<string, ThingDef>(StringComparer.OrdinalIgnoreCase);

                void Reject(string why)
                {
                    rejected++;
                    reasons.TryGetValue(why, out var n);
                    reasons[why] = n + 1;
                }

                for (var i = 0; i < parsed.Count; i++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var op = parsed[i];
                    var clearOnly = string.Equals(op.Terrain, "CLEAR", StringComparison.OrdinalIgnoreCase);

                    ThingDef plantDef = null;
                    if (!clearOnly)
                    {
                        if (!resolved.TryGetValue(op.Terrain, out plantDef))
                        {
                            plantDef = DefDatabase<ThingDef>.GetNamedSilentFail(op.Terrain);
                            resolved[op.Terrain] = plantDef;
                        }
                        if (plantDef == null || plantDef.plant == null)
                        {
                            if (errors.Count < 10)
                                errors.Add(new { op = i, def = op.Terrain, error = "not a plant ThingDef" });
                            continue;
                        }
                    }

                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            int cx = op.X + dx, cz = op.Z + dz;
                            if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }
                            var cell = new IntVec3(cx, 0, cz);

                            if (clearFirst || clearOnly)
                            {
                                var here = map.thingGrid.ThingsListAtFast(cell).ToList();
                                foreach (var t in here)
                                {
                                    if (t?.def?.plant != null && !t.Destroyed)
                                    {
                                        t.Destroy(DestroyMode.Vanish);
                                        cleared++;
                                    }
                                }
                            }
                            if (clearOnly) continue;

                            // Deterministic scatter: a re-run with the same seed
                            // paints the same cells, so the call is idempotent
                            // rather than additive.
                            if (density < 1f)
                            {
                                var h = (cx * 73856093) ^ (cz * 19349663) ^ (seed * 83492791);
                                var v = ((h & 0x7fffffff) % 10000) / 10000f;
                                if (v > density) { skippedDensity++; continue; }
                            }

                            if (!plantDef.CanEverPlantAt(cell, map))
                            {
                                Reject("terrain or conditions cannot support " + plantDef.defName);
                                continue;
                            }

                            try
                            {
                                var thing = ThingMaker.MakeThing(plantDef);
                                var plant = thing as Plant;
                                if (plant != null) plant.Growth = growth;
                                GenSpawn.Spawn(thing, cell, map);
                                if (thing.Spawned) planted++;
                                else Reject("spawned but not present");
                            }
                            catch (Exception e)
                            {
                                Reject(e.GetType().Name);
                                if (errors.Count < 10)
                                    errors.Add(new { op = i, x = cx, z = cz, error = e.Message });
                            }
                        }
                    }
                }

                return new
                {
                    // Loud by design: a call that planted nothing is NOT a success,
                    // whatever it did to the cells it visited.
                    success = errors.Count == 0 && (planted > 0 || cleared > 0),
                    message =
                        $"Planted {planted}, cleared {cleared}" +
                        (rejected > 0 ? $", REJECTED {rejected}" : "") +
                        (skippedDensity > 0 ? $", {skippedDensity} skipped by density" : "") +
                        (outOfBounds > 0 ? $", {outOfBounds} outside the map" : "") + ".",
                    planted,
                    cleared,
                    rejected,
                    rejectionReasons = reasons,
                    cellsSkippedByDensity = skippedDensity,
                    cellsOutOfBounds = outOfBounds,
                    growth,
                    errors,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/damage",
            Description =
                "Apply graduated damage to ANY thing or pawn, including hostiles. Closes the " +
                "gap that made the debug menu's own 'Apply damage...' useless: that path is " +
                "inert, and RimBridgeServer.ResolvePawn accepts player-controlled colonists " +
                "only, so hostiles could not be targeted at all. This calls Thing.TakeDamage " +
                "directly. Target by thingId, or by x/z to hit everything in a cell.",
            ResultDescription =
                "Returns per-target damage dealt and the resulting hediffs, read back after " +
                "the fact — not merely that the call ran.")]
        public static async Task<object> Damage(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "DamageDef defName, e.g. Bullet, EMP, Bomb, Stun.")]
            string damageDef,
            [ToolParameter(Description = "Damage amount.", DefaultValue = 10.0)]
            float amount = 10f,
            [ToolParameter(Description = "Target thingId. Either this or x/z.", DefaultValue = null)]
            string thingId = null,
            [ToolParameter(Description = "Target cell X (with z). Hits every valid thing there.",
                DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description = "Target cell Z.", DefaultValue = -1)]
            int z = -1,
            [ToolParameter(Description = "Armor penetration 0..1.", DefaultValue = 0.0)]
            float armorPenetration = 0f,
            [ToolParameter(Description = "Body part defName to target. Optional.", DefaultValue = null)]
            string bodyPart = null,
            [ToolParameter(Description =
                "Safety rail: refuse to damage player colonists unless this is true.",
                DefaultValue = false)]
            bool allowColonists = false)
        {
            if (string.IsNullOrWhiteSpace(damageDef))
                return Fail("damageDef is required.");
            if (string.IsNullOrWhiteSpace(thingId) && (x < 0 || z < 0))
                return Fail("Give either thingId, or both x and z.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var ddef = DefDatabase<DamageDef>.GetNamedSilentFail(damageDef);
                if (ddef == null)
                    return Fail($"No DamageDef named '{damageDef}'.", new
                    {
                        suggestions = DefDatabase<DamageDef>.AllDefsListForReading
                            .Where(d => d.defName.ToLowerInvariant().Contains(damageDef.ToLowerInvariant()))
                            .Select(d => d.defName).Take(10).ToList()
                    });

                var targets = new List<Thing>();
                if (!string.IsNullOrWhiteSpace(thingId))
                {
                    var found = map.listerThings.AllThings.FirstOrDefault(q => q.ThingID == thingId);
                    if (found == null) return Fail($"No thing with id '{thingId}' on this map.");
                    targets.Add(found);
                }
                else
                {
                    // 🔴 NO TARGET AT ALL. This used to fall through with the
                    // x/z defaults of -1, pass a bounds check that only tested
                    // the UPPER bound, hit an empty cell list and report
                    // "damaged 0 things" -- which a retired seat read as "the weapon is
                    // broken" and nearly filed against a weapon that works on
                    // the first hit. The real cause was a parameter named
                    // `targetId`, which this tool does not have: the SDK drops
                    // unknown parameters silently, so the call arrives here
                    // looking like a caller who asked for nothing.
                    // Name the accepted parameters in the refusal. A caller who
                    // guessed a name must be told which name is right.
                    if (x < 0 || z < 0)
                        return Fail(
                            "No target. jawa/damage takes 'thingId' (a ThingID string, as " +
                            "returned by jawa/list_pawns and jawa/spawn_pawn) OR 'x' and 'z' " +
                            "for a cell. Nothing was damaged. ⚠️ If you passed 'targetId', " +
                            "'pawnId' or 'id', that is not a parameter of this tool and the " +
                            "bridge dropped it silently before the tool ran.",
                            new
                            {
                                accepted = new[] { "thingId", "x", "z", "damageDef", "amount",
                                                   "armorPenetration", "bodyPart", "allowColonists" },
                                thingIdGiven = false,
                                xGiven = x,
                                zGiven = z
                            });

                    var cell = new IntVec3(x, 0, z);
                    var size = map.Size;
                    if (x >= size.x || z >= size.z) return Fail("Cell is outside the map.");
                    targets.AddRange(map.thingGrid.ThingsListAtFast(cell).ToList());
                    if (targets.Count == 0)
                        return Fail($"Nothing at ({x},{z}) to damage. The cell is empty, so " +
                                    "this is a miss, not a failure of the damage itself.",
                                    new { x, z });
                }

                var results = new List<object>();
                int hit = 0, skipped = 0;
                foreach (var thing in targets)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (thing == null || thing.Destroyed) continue;
                    var pawn = thing as Pawn;
                    if (!allowColonists && pawn != null && pawn.Faction == Faction.OfPlayer)
                    {
                        skipped++;
                        continue;
                    }

                    BodyPartRecord part = null;
                    if (!string.IsNullOrWhiteSpace(bodyPart) && pawn != null)
                    {
                        var bpDef = DefDatabase<BodyPartDef>.GetNamedSilentFail(bodyPart);
                        if (bpDef != null)
                            part = pawn.health.hediffSet.GetNotMissingParts()
                                       .FirstOrDefault(b => b.def == bpDef);
                    }

                    var before = thing.HitPoints;
                    var hediffsBefore = pawn?.health?.hediffSet?.hediffs?.Count ?? 0;
                    var dinfo = new DamageInfo(ddef, amount, armorPenetration, -1f, null, part, null);
                    var res = thing.TakeDamage(dinfo);
                    hit++;

                    results.Add(new
                    {
                        id = thing.ThingID,
                        def = thing.def?.defName,
                        isPawn = pawn != null,
                        hitPointsBefore = before,
                        hitPointsAfter = thing.Destroyed ? 0 : thing.HitPoints,
                        destroyed = thing.Destroyed,
                        totalDamageDealt = res.totalDamageDealt,
                        // Read the world back rather than trusting the call: a
                        // damage def with harmsHealth:false deals ZERO hit points
                        // and this is where that becomes visible.
                        hediffsBefore,
                        hediffsAfter = pawn?.health?.hediffSet?.hediffs?.Count ?? 0,
                        downed = pawn?.Downed ?? false,
                        dead = pawn?.Dead ?? false,
                        stunTicksLeft = pawn?.stances?.stunner?.StunTicksLeft ?? 0
                    });
                }

                return new
                {
                    success = hit > 0,
                    message = $"Damaged {hit} thing(s) with {ddef.defName} {amount}" +
                              (skipped > 0 ? $"; {skipped} player colonist(s) skipped (allowColonists=false)" : "") + ".",
                    damageDef = ddef.defName,
                    harmsHealth = ddef.harmsHealth,
                    targetsHit = hit,
                    colonistsSkipped = skipped,
                    // ⚠️ `results` is the per-thing list. A retired seat parsed `targets`,
                    // got nothing, and read it as "the ion did nothing" -- caught
                    // only because the CONTROL row was empty too. Aliased so the
                    // obvious name works, and count exposed so an empty list
                    // cannot be confused with a missing key.
                    results,
                    targets = results,
                    resultCount = results.Count,
                    // The decisive fields are per-row downed/dead/destroyed. There
                    // is deliberately NO hediff-severity list here: severity comes
                    // from a save parse, not from this call. Do not read its
                    // absence as "no hediff was applied".
                    verdictFields = new[] { "downed", "dead", "destroyed" },
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/get_def",
            Description =
                "Read a def as the game RESOLVED it — after XML patches and after parent " +
                "inheritance. This is not the same as the offline def dump, which does not " +
                "serialise statBases or description and has produced wrong conclusions " +
                "twice (a warcasket appearing to have no armour values, and an empty " +
                "description reading as a failed patch). Returns statBases, comps with their " +
                "class names, and the mod that actually supplied the def. Pass " +
                "defType='BiomeDef' to read terrainPatchMakers, which is how a " +
                "worldgen terrain override is checked without eyeballing a map.",
            ResultDescription =
                "Returns defType, the owning mod, description, statBases, comp classes and " +
                "selected common fields. For a ThingDef, `extra` carries category, ticker, " +
                "thingClass, flesh/mechanoid flags and modExtensions. For a BiomeDef it " +
                "carries terrainPatchMakers -- each with its perlinFrequency, fertility " +
                "band, minSize and its ordered thresholds (terrain, min, max) -- plus " +
                "terrainsByFertility. ⚠️ Patchmaker ORDER is meaningful: the first "
                + "threshold whose band contains the noise value wins, so the index is "
                + "reported and the list is never sorted.")]
        public static async Task<object> GetDef(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The defName to read.")]
            string defName,
            [ToolParameter(Description =
                "Def type short name, e.g. ThingDef, HediffDef, DamageDef, TerrainDef, " +
                "PawnKindDef, RecipeDef. Defaults to ThingDef.",
                DefaultValue = "ThingDef")]
            string defType = "ThingDef")
        {
            if (string.IsNullOrWhiteSpace(defName)) return Fail("defName is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var type = GenTypes.GetTypeInAnyAssembly(defType)
                           ?? GenTypes.GetTypeInAnyAssembly("Verse." + defType)
                           ?? GenTypes.GetTypeInAnyAssembly("RimWorld." + defType);
                if (type == null) return Fail($"No def type named '{defType}'.");

                var def = GenDefDatabase.GetDefSilentFail(type, defName, false);
                if (def == null)
                    return Fail($"No {defType} named '{defName}'.");

                var thingDef = def as ThingDef;
                object stats = null, comps = null, extra = null;
                if (thingDef != null)
                {
                    // statBases is one of the two fields the dump cannot show.
                    if (thingDef.statBases != null)
                        stats = thingDef.statBases.ToDictionary(
                            s => s.stat?.defName ?? "?", s => s.value);
                    if (thingDef.comps != null)
                        comps = thingDef.comps.Select(c => new
                        {
                            @class = c.GetType().Name,
                            compClass = c.compClass?.Name,
                            // ⚠️ VALUES, not just class names. Until 2026-08-13 this
                            // reported only the two names above, which made a whole
                            // class of question unanswerable: "what radius did the mod
                            // actually apply?" lives in a FIELD on
                            // CompProperties_SubstructureFootprint, and nothing
                            // surfaced it. A retired seat hit exactly that trying to confirm
                            // whether Bigger Gravships' 34/30/12/85 had reached the
                            // live defs, and had to report the question unresolved.
                            //
                            // Scalars, strings, enums and Defs only -- a Def renders
                            // as its defName. Anything else would balloon the payload
                            // and is deliberately skipped rather than truncated.
                            fields = CompScalars(c)
                        }).ToList();
                    extra = new
                    {
                        category = thingDef.category.ToString(),
                        tickerType = thingDef.tickerType.ToString(),
                        thingClass = thingDef.thingClass?.Name,
                        madeFromStuff = thingDef.MadeFromStuff,
                        isPlant = thingDef.plant != null,
                        fleshType = thingDef.race?.FleshType?.defName,
                        isMechanoid = thingDef.race?.IsMechanoid,
                        isFlesh = thingDef.race?.IsFlesh,
                        intelligence = thingDef.race?.intelligence.ToString(),
                        modExtensions = thingDef.modExtensions?.Select(m => m.GetType().Name).ToList(),
                        // 🔴 The three fields a Cherry Picker NEUTER moves. It
                        // deletes only 13 def types; for everything else the def
                        // stays in the database with its value stripped, so
                        // EXISTENCE PROVES NOTHING and `get_def` returning the
                        // def is not evidence the pick failed. The tell is the
                        // value, so the value has to be readable.
                        tradeability = thingDef.tradeability.ToString(),
                        thingCategories = thingDef.thingCategories?
                            .Select(c => c.defName).ToList(),
                        thingCategoryCount = thingDef.thingCategories?.Count ?? 0,
                        tradeTags = thingDef.tradeTags
                    };
                }
                else if (def is PawnKindDef pawnKindDef)
                {
                    // Cherry Picker neuters a PawnKindDef by setting combatPower
                    // to float.MaxValue (3.4028235E+38) so the storyteller can
                    // never afford it. THAT NUMBER IS THE CONFIRMATION -- a
                    // normal value means the pick did not apply, and the def
                    // existing tells you nothing either way.
                    extra = new
                    {
                        isPawnKind = true,
                        combatPower = pawnKindDef.combatPower,
                        combatPowerIsMaxValue =
                            pawnKindDef.combatPower >= float.MaxValue,
                        race = pawnKindDef.race?.defName,
                        defaultFactionDef = pawnKindDef.defaultFactionDef?.defName
                    };
                }
                else if (def is BiomeDef biomeDef)
                {
                    // 🔴 v1 row 4's dune-seas gate is a BiomeDef read, and until
                    // now this tool could not perform it: `extra` was ThingDef-only,
                    // so a BiomeDef came back as label + description and nothing
                    // else. Dune seas are "NOT an eyeball check -- it
                    // closes on a live terrainPatchMakers read of 0.55/0.50", and
                    // nobody checked that the read was possible. A gate whose
                    // evidence cannot be collected is not a gate.
                    //
                    // Field names read from Assembly-CSharp with ilprobe:
                    //   BiomeDef.terrainPatchMakers  -> List<TerrainPatchMaker>
                    //   TerrainPatchMaker.thresholds -> List<TerrainThreshold>
                    //   TerrainPatchMaker.perlinFrequency / minFertility /
                    //     maxFertility / minSize / isPond
                    //   TerrainThreshold.terrain / min / max
                    extra = new
                    {
                        isBiome = true,
                        // ⚠️ A patchmaker's ORDER is meaningful -- the first
                        // threshold whose band contains the noise value wins -- so
                        // the index is reported rather than sorting for tidiness.
                        terrainPatchMakers = biomeDef.terrainPatchMakers?
                            .Select((pm, i) => new
                            {
                                index = i,
                                perlinFrequency = pm.perlinFrequency,
                                minFertility = pm.minFertility,
                                maxFertility = pm.maxFertility,
                                minSize = pm.minSize,
                                isPond = pm.isPond,
                                thresholds = pm.thresholds?.Select(t => new
                                {
                                    terrain = t.terrain?.defName,
                                    min = t.min,
                                    max = t.max
                                }).ToList()
                            }).ToList(),
                        patchMakerCount = biomeDef.terrainPatchMakers?.Count ?? 0,
                        terrainsByFertility = biomeDef.terrainsByFertility?
                            .Select(t => new
                            {
                                terrain = t.terrain?.defName,
                                min = t.min,
                                max = t.max
                            }).ToList()
                    };
                }

                // 🔴 `extra` is hand-modelled and covers exactly THREE types:
                // ThingDef, PawnKindDef, BiomeDef. For every other def type it is
                // null — and a null `extra` is INDISTINGUISHABLE from "the field
                // you asked about is genuinely absent". That cost a real defect on
                // 2026-08-14: MapGeneratorDef returned extra:null and was read as
                // "the genStep is not registered", which was false. So say which
                // it is, out loud, and name the tool that CAN answer.
                var extraModelled = thingDef != null || def is PawnKindDef || def is BiomeDef;

                return new
                {
                    success = true,
                    defName = def.defName,
                    defType = def.GetType().Name,
                    label = def.label,
                    // The other field the dump omits.
                    description = def.description,
                    modName = def.modContentPack?.Name,
                    packageId = def.modContentPack?.PackageId,
                    statBases = stats,
                    comps,
                    extra,
                    extraModelled,
                    extraNote = extraModelled
                        ? null
                        : $"⚠️ `extra` is NOT modelled for {def.GetType().Name} — this null means "
                          + "NOT INSPECTED, not 'absent'. Do not read a missing field as a missing "
                          + "value. Use jawa/get_defs with an explicit fields list to read this type.",
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/drain_log",
            Description =
                "Return the game's recent log messages, newest last. The bridge's per-call " +
                "`effects.logs` cannot see anything logged during step_game_ticks, so a " +
                "warning caused by a tick is invisible without this. Filter to errors only " +
                "to find red text without diffing Player.log by hand.",
            ResultDescription = "Returns messages with their type and repeat count.")]
        public static async Task<object> DrainLog(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Return at most this many, newest last.", DefaultValue = 50)]
            int limit = 50,
            [ToolParameter(Description = "Only Error and Warning messages.", DefaultValue = false)]
            bool errorsOnly = false,
            [ToolParameter(Description = "Only messages containing this substring.", DefaultValue = null)]
            string contains = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var msgs = Log.Messages.ToList();
                var rows = new List<object>();
                foreach (var m in msgs)
                {
                    var kind = m.type.ToString();
                    if (errorsOnly && kind != "Error" && kind != "Warning") continue;
                    if (!string.IsNullOrWhiteSpace(contains) &&
                        (m.text == null || m.text.IndexOf(contains, StringComparison.OrdinalIgnoreCase) < 0))
                        continue;
                    rows.Add(new { type = kind, text = m.text, repeats = m.repeats });
                }
                if (rows.Count > limit) rows = rows.Skip(rows.Count - limit).ToList();
                return new
                {
                    success = true,
                    message = $"{rows.Count} message(s) of {msgs.Count} in the buffer.",
                    totalInBuffer = msgs.Count,
                    messages = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/refresh_rect",
            Description =
                "Dirty the map mesh over a rect WITHOUT painting anything. The map mesh is " +
                "cached in 17x17 sections, so a write that skips its refresh leaves the " +
                "section stale — correct in the grid, unpainted on screen. This is the tool " +
                "that makes deferred refresh possible: paint many rects with refresh=false, " +
                "then dirty the whole region once.")]
        public static async Task<object> RefreshRectTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect)
        {
            List<ParsedOp> parsed;
            var errs = new List<string>();
            if (!TryParseOps(rect, "_", out parsed, errs) || parsed.Count != 1)
                return Fail("rect must be a single 'x,z,w,h'.", new { errors = errs });

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");
                var op = parsed[0];
                RefreshRect(map, op.X, op.Z, op.W, op.H);
                return new
                {
                    success = true,
                    message = $"Dirtied the map mesh over {op.W}x{op.H} at ({op.X},{op.Z}).",
                    cells = op.W * op.H
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/spawn_pawn",
            Description =
                "Spawn a pawn of a chosen kind, IN A CHOSEN FACTION, at a chosen cell. The " +
                "debug menu's Spawn Pawn always spawns player-side, which is how a hostile " +
                "test ends up standing next to the colony. Faction accepts a FactionDef " +
                "defName, 'player', 'hostile' (any faction hostile to the player), or " +
                "'none' for a wild/faction-less pawn. Pass xenotype to pin the pawn to a " +
                "XenotypeDef instead of letting the kind and faction roll one.",
            ResultDescription = "Returns the spawned pawn's id, faction, hostility, position " +
                "and xenotype, plus a row for every pawn that FAILED to generate. success is " +
                "false unless every requested pawn actually spawned.")]
        public static async Task<object> SpawnPawn(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "PawnKindDef defName.")] string kindDef,
            [ToolParameter(Description = "Cell X.")] int x,
            [ToolParameter(Description = "Cell Z.")] int z,
            [ToolParameter(Description =
                "FactionDef defName, or 'player' / 'hostile' / 'none'.", DefaultValue = "hostile")]
            string faction = "hostile",
            [ToolParameter(Description = "How many to spawn, scattered near the cell.",
                DefaultValue = 1)]
            int count = 1,
            [ToolParameter(Description =
                "XenotypeDef defName to FORCE, e.g. BTD_Jawa, OuterRim_Jawa, " +
                "guy762_xenotype_jawa, Jawa_Xeno_Gamorrean. Needs Biotech. This goes through " +
                "PawnGenerationRequest.ForcedXenotype, which PawnGenerator checks FIRST and " +
                "returns immediately on, so it beats the kind's and the faction's own xenotype " +
                "chances. Leave null to keep the pre-existing generation path exactly as it " +
                "was.", DefaultValue = null)]
            string xenotype = null)
        {
            if (string.IsNullOrWhiteSpace(kindDef)) return Fail("kindDef is required.");
            if (count < 1) count = 1;
            if (count > 50) return Fail($"count {count} > 50. Spawn fewer, or call again.");

            // ⚠️ Same shape as the Ideology guard on set_pawn_style: without Biotech the
            // whole xenotype system is inert, and a forced xenotype would be silently
            // dropped while this tool reported the pawn it asked for.
            if (!string.IsNullOrWhiteSpace(xenotype) && !ModsConfig.BiotechActive)
                return Fail("xenotype needs Biotech. Refusing rather than spawning a " +
                            "baseliner and calling it the xenotype you asked for.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                XenotypeDef xeno = null;
                if (!string.IsNullOrWhiteSpace(xenotype))
                {
                    xeno = DefDatabase<XenotypeDef>.GetNamedSilentFail(xenotype.Trim());
                    if (xeno == null)
                        return Fail($"No XenotypeDef named '{xenotype}'.",
                            new { suggestions = DefSuggestions<XenotypeDef>(xenotype) });
                }

                var kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDef);
                if (kind == null)
                    return Fail($"No PawnKindDef named '{kindDef}'.", new
                    {
                        suggestions = DefDatabase<PawnKindDef>.AllDefsListForReading
                            .Where(d => d.defName.ToLowerInvariant().Contains(kindDef.ToLowerInvariant()))
                            .Select(d => d.defName).Take(10).ToList()
                    });

                Faction fac = null;
                var f = (faction ?? "hostile").Trim();
                if (string.Equals(f, "player", StringComparison.OrdinalIgnoreCase))
                    fac = Faction.OfPlayer;
                else if (string.Equals(f, "none", StringComparison.OrdinalIgnoreCase))
                    fac = null;
                else if (string.Equals(f, "hostile", StringComparison.OrdinalIgnoreCase))
                {
                    // ⚠️ ROOT CAUSE OF THE SetIdeo NRE, found by a retired seat in the log:
                    //   "Humanlike pawn SA-6422 was added to non-humanlike faction hive"
                    //   "Error while generating pawn. Rethrowing. NullReferenceException"
                    // FirstOrDefault picked Insect/Hive -- a NON-humanlike faction --
                    // and putting a Humanlike pawnkind in it breaks PawnGenerator.
                    // The throw was never in ideo code; that was where the stack
                    // happened to surface.
                    //
                    // So "hostile" now prefers a faction whose humanlikeness MATCHES
                    // the kind being spawned, and only falls back to any hostile if
                    // no such faction exists.
                    var wantHumanlike = kind.RaceProps?.Humanlike ?? false;
                    var hostiles = Find.FactionManager.AllFactions
                        .Where(q => !q.IsPlayer && q.HostileTo(Faction.OfPlayer)).ToList();
                    fac = hostiles.FirstOrDefault(q => (q.def?.humanlikeFaction ?? false) == wantHumanlike)
                          ?? hostiles.FirstOrDefault();
                }
                else
                    fac = Find.FactionManager.AllFactions
                              .FirstOrDefault(q => string.Equals(q.def?.defName, f,
                                                                 StringComparison.OrdinalIgnoreCase));

                if (fac == null && !string.Equals(f, "none", StringComparison.OrdinalIgnoreCase))
                    return Fail($"No faction resolved for '{faction}'.", new
                    {
                        available = Find.FactionManager.AllFactions
                            .Select(q => new { def = q.def?.defName, name = q.Name, hostile = q.HostileTo(Faction.OfPlayer) })
                            .Take(25).ToList()
                    });

                var size = map.Size;
                var rows = new List<object>();
                var landed = 0;
                var substituted = 0;
                for (var i = 0; i < count; i++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var cell = new IntVec3(x, 0, z);
                    if (i > 0 && !CellFinder.TryFindRandomCellNear(new IntVec3(x, 0, z), map, 4,
                            c => c.Standable(map), out cell))
                        cell = new IntVec3(x, 0, z);
                    if (cell.x < 0 || cell.z < 0 || cell.x >= size.x || cell.z >= size.z)
                        return Fail("Cell is outside the map.");

                    // ⚠️ GeneratePawn can throw an NRE inside Pawn_IdeoTracker.SetIdeo
                    // for some kind/faction pairs. A retired seat, 2026-08-13, one clean
                    // variable: KotORDroidGood_3C at the same cell in the same run
                    // FAILED with faction="hostile" and SUCCEEDED with "none".
                    //
                    // I have NO mechanism and am not shipping a theory. What this
                    // does is make the failure legible instead of fatal: one bad
                    // pawn no longer kills the batch, and the resolved faction --
                    // plus whether it actually HAS an ideo -- comes back on the
                    // row, so the discriminator is measured by the next caller
                    // rather than guessed at. "hostile" resolves to whatever
                    // hostile faction the map has (Insect/Hive on the test map),
                    // which is NOT a generic hostile and is worth seeing.
                    if (fac != null && (kind.RaceProps?.Humanlike ?? false)
                        && !(fac.def?.humanlikeFaction ?? false))
                        return Fail(
                            $"Refusing to spawn humanlike kind '{kind.defName}' into " +
                            $"non-humanlike faction '{fac.def?.defName}'. RimWorld's pawn " +
                            "generator throws a NullReferenceException on this pairing " +
                            "rather than reporting it. Pass an explicit humanlike faction " +
                            "defName, or faction='none'.",
                            new { resolvedFaction = fac.def?.defName, factionName = fac.Name });

                    Pawn pawn;
                    try
                    {
                        // No xenotype asked for -> the ORIGINAL call, byte for byte.
                        // A xenotype needs the request overload, and the request must
                        // come from the real constructor: PawnGenerationRequest carries
                        // _calledTheCorrectConstructor and ValidateAndFix logs
                        // "was not created through the correct constructor" for a
                        // default(...) or object-initialiser-only struct.
                        // Context 2 = NonPlayer, which is what GeneratePawn(kind, faction)
                        // itself passes (ldc.i4.2 at IL_0004).
                        pawn = xeno == null
                            ? PawnGenerator.GeneratePawn(kind, fac)
                            : PawnGenerator.GeneratePawn(
                                new PawnGenerationRequest(kind, fac,
                                                          PawnGenerationContext.NonPlayer)
                                {
                                    ForcedXenotype = xeno,
                                    ForceBaselinerChance = 0f
                                });
                    }
                    catch (Exception ex)
                    {
                        rows.Add(new
                        {
                            ok = false,
                            kindDef = kind.defName,
                            factionResolved = fac?.def?.defName ?? "none",
                            factionName = fac?.Name,
                            factionHasIdeo = fac?.ideos?.PrimaryIdeo != null,
                            error = ex.GetType().Name,
                            message = ex.Message,
                            at = new { x = cell.x, z = cell.z }
                        });
                        continue;
                    }
                    GenSpawn.Spawn(pawn, cell, map);

                    // Read the xenotype back off the pawn. Asking for one and not
                    // getting it is a FAILED row, not a footnote -- a forced xenotype
                    // that quietly fell back to Baseliner is the exact silent success
                    // this tool exists to prevent.
                    var xenoNow = pawn.genes?.Xenotype?.defName;
                    var xenoOk = xeno == null || xenoNow == xeno.defName;

                    // ⚠️ SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1: the kind that comes
                    // BACK is not always the kind that went in. Vanilla cannot do
                    // this -- TryGenerateNewPawnInternal assigns
                    // `pawn.kindDef = request.KindDef` (PawnGenerator.cs:734) and
                    // RedressPawn calls ChangeKind(request.KindDef) -- so a mismatch
                    // means a Harmony patch rewrote `request` by ref or replaced
                    // `__result`. Either way it is invisible unless we READ IT BACK,
                    // which this tool did not do: it printed the REQUESTED defName in
                    // its message and never looked at pawn.kindDef, so a substituted
                    // pawn counted as a clean spawn.
                    var kindNow = pawn.kindDef?.defName;
                    var kindOk = kindNow == kind.defName;
                    if (!kindOk) substituted++;
                    if (pawn.Spawned && xenoOk && kindOk) landed++;

                    rows.Add(new
                    {
                        ok = pawn.Spawned && xenoOk && kindOk,
                        id = pawn.ThingID,
                        name = pawn.Name?.ToStringShort ?? pawn.LabelShortCap,
                        kindRequested = kind.defName,
                        kindActual = kindNow,
                        kindSubstituted = !kindOk,
                        faction = pawn.Faction?.def?.defName,
                        hostile = pawn.Faction != null && pawn.Faction.HostileTo(Faction.OfPlayer),
                        x = pawn.Position.x,
                        z = pawn.Position.z,
                        spawned = pawn.Spawned,
                        xenotype = xenoNow,
                        xenotypeRequested = xeno?.defName,
                        xenotypeApplied = xenoOk
                    });
                }

                // ⚠️ This used to be `rows.Count > 0`. Rows are added for pawns that
                // THREW during generation too, so a batch in which every single pawn
                // failed reported success: true. Only rows that actually spawned --
                // with the xenotype asked for, if one was -- count.
                return new
                {
                    success = landed > 0 && landed == rows.Count,
                    message = $"Spawned {landed}/{rows.Count} {kind.defName} in faction " +
                              $"{fac?.def?.defName ?? "(none)"}" +
                              (xeno != null ? $" as {xeno.defName}" : "") + "." +
                              (landed == rows.Count ? "" :
                               $" ⚠️ {rows.Count - landed} did not spawn as asked -- see the " +
                               "rows with ok:false.") +
                              (substituted == 0 ? "" :
                               $" ⚠️ {substituted} came back as a DIFFERENT PawnKindDef than " +
                               "requested -- see kindActual on the rows with " +
                               "kindSubstituted:true. Vanilla PawnGenerator cannot do this; " +
                               "a Harmony patch on pawn generation did, and it reaches raids " +
                               "too, not just this tool."),
                    spawnedCount = landed,
                    failedCount = rows.Count - landed,
                    substitutedCount = substituted,
                    xenotypeRequested = xeno?.defName,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---- pawn selection, shared by the two pawn-appearance tools ---------
        // Accepts one ThingID, a comma-separated list, 'all' (every spawned
        // pawn) or 'colonists'. On ANY unknown id it fails the whole call
        // rather than quietly operating on the ids it did recognise -- a
        // half-applied audit is worse than a refused one, because the caller
        // photographs it and believes the result.
        private static List<Pawn> ResolvePawns(Map map, string pawnId, out object error)
        {
            error = null;
            var sel = (pawnId ?? "").Trim();
            if (sel.Length == 0)
            {
                error = Fail("pawnId is required: a ThingID, a comma-separated list, " +
                             "'all' or 'colonists'.");
                return null;
            }

            var spawned = map.mapPawns.AllPawnsSpawned.ToList();
            if (string.Equals(sel, "all", StringComparison.OrdinalIgnoreCase))
                return spawned;
            if (string.Equals(sel, "colonists", StringComparison.OrdinalIgnoreCase))
                return map.mapPawns.FreeColonists.ToList();

            var found = new List<Pawn>();
            var missing = new List<string>();
            foreach (var id in sel.Split(',').Select(q => q.Trim()).Where(q => q.Length > 0))
            {
                var p = spawned.FirstOrDefault(
                    q => string.Equals(q.ThingID, id, StringComparison.OrdinalIgnoreCase));
                if (p == null) missing.Add(id); else found.Add(p);
            }

            if (missing.Count > 0)
            {
                error = Fail($"No spawned pawn on this map with id: {string.Join(", ", missing)}.",
                    new
                    {
                        missing,
                        pawnsOnMap = spawned.Count,
                        onMap = spawned.Take(25).Select(q => new
                        {
                            id = q.ThingID,
                            name = q.LabelShortCap,
                            kind = q.kindDef?.defName
                        }).ToList()
                    });
                return null;
            }
            return found;
        }

        // Values read from Verse.AI.PathEndMode with ilprobe, not assumed:
        // None=0, OnCell=1, Touch=2, ClosestTouch=3, InteractionCell=4.
        private static bool TryParsePathEndMode(string s, out PathEndMode mode)
        {
            mode = PathEndMode.OnCell;
            switch ((s ?? "").Trim().ToLowerInvariant().Replace("_", ""))
            {
                case "none": mode = PathEndMode.None; return true;
                case "oncell": case "cell": mode = PathEndMode.OnCell; return true;
                case "touch": mode = PathEndMode.Touch; return true;
                case "closesttouch": mode = PathEndMode.ClosestTouch; return true;
                case "interactioncell": case "interaction":
                    mode = PathEndMode.InteractionCell; return true;
            }
            return false;
        }

        private static bool TryParseRot(string dir, out Rot4 rot)
        {
            rot = Rot4.South;
            switch ((dir ?? "").Trim().ToLowerInvariant())
            {
                case "n": case "north": case "0": rot = Rot4.North; return true;
                case "e": case "east":  case "1": rot = Rot4.East;  return true;
                case "s": case "south": case "2": rot = Rot4.South; return true;
                case "w": case "west":  case "3": rot = Rot4.West;  return true;
            }
            return false;
        }

        private static List<string> DefSuggestions<T>(string name) where T : Def, new()
        {
            var needle = (name ?? "").ToLowerInvariant();
            return DefDatabase<T>.AllDefsListForReading
                .Where(d => d.defName.ToLowerInvariant().Contains(needle))
                .Select(d => d.defName).Take(10).ToList();
        }

        // 'r,g,b' or 'r,g,b,a' in 0..1 or 0..255, '#RRGGBB', or a ColorDef defName.
        private static bool TryParseColor(string s, out UnityEngine.Color c, out string why)
        {
            c = UnityEngine.Color.white;
            why = null;
            var t = (s ?? "").Trim();
            if (t.Length == 0) { why = "empty"; return false; }

            var cd = DefDatabase<ColorDef>.GetNamedSilentFail(t);
            if (cd != null) { c = cd.color; return true; }

            if (t.StartsWith("#")) t = t.Substring(1);
            if (t.Length == 6 && t.All(Uri.IsHexDigit))
            {
                c = new UnityEngine.Color(
                    Convert.ToInt32(t.Substring(0, 2), 16) / 255f,
                    Convert.ToInt32(t.Substring(2, 2), 16) / 255f,
                    Convert.ToInt32(t.Substring(4, 2), 16) / 255f);
                return true;
            }

            var parts = t.Split(',').Select(q => q.Trim()).Where(q => q.Length > 0).ToList();
            if (parts.Count < 3 || parts.Count > 4)
            {
                why = "expected 'r,g,b', 'r,g,b,a', '#RRGGBB' or a ColorDef defName";
                return false;
            }
            var v = new float[4] { 0f, 0f, 0f, 1f };
            for (var i = 0; i < parts.Count; i++)
            {
                float f;
                if (!float.TryParse(parts[i], System.Globalization.NumberStyles.Float,
                                    System.Globalization.CultureInfo.InvariantCulture, out f))
                { why = $"'{parts[i]}' is not a number"; return false; }
                v[i] = f;
            }
            // A caller writing 0..255 is unambiguous: no channel of a 0..1 colour
            // exceeds 1. Scale rather than clamping them all to white.
            if (v[0] > 1f || v[1] > 1f || v[2] > 1f)
            { v[0] /= 255f; v[1] /= 255f; v[2] /= 255f; if (v[3] > 1f) v[3] /= 255f; }
            c = new UnityEngine.Color(v[0], v[1], v[2], v[3]);
            return true;
        }

        [Tool(
            "jawa/set_pawn_style",
            Description =
                "Set a spawned pawn's APPEARANCE directly -- hair, hair colour, beard, face " +
                "and body tattoo, head type, body type, fur and skin colour -- so a styled " +
                "look can be staged for a screenshot without generating pawns until one comes " +
                "out right. Every field is optional; only the ones you pass are touched. All " +
                "defNames are resolved BEFORE anything is written, so a typo changes nothing " +
                "instead of half-applying. After the writes it calls " +
                "Pawn_StyleTracker.Notify_StyleItemChanged(), which is what actually rebuilds " +
                "the graphics -- a style write without it is correct in the save and stale on " +
                "screen.",
            ResultDescription =
                "Returns per pawn a before/after value for every field touched, read back off " +
                "the pawn after the write. success is false unless every requested field reads " +
                "back as the value asked for.")]
        public static async Task<object> SetPawnStyle(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "One ThingID, a comma-separated list, 'all' or 'colonists'.")]
            string pawnId,
            [ToolParameter(Description = "HairDef defName, e.g. Bald, Shaved.", DefaultValue = null)]
            string hair = null,
            [ToolParameter(Description =
                "Hair colour: 'r,g,b' (0..1 or 0..255), '#RRGGBB', or a ColorDef defName. " +
                "⚠️ If the pawn has a gene with skinIsHairColor, RimWorld also overwrites the " +
                "skin colour from this value.", DefaultValue = null)]
            string hairColor = null,
            [ToolParameter(Description = "BeardDef defName, e.g. NoBeard.", DefaultValue = null)]
            string beard = null,
            [ToolParameter(Description = "TattooDef defName for the face, e.g. NoTattoo_Face. " +
                "Needs Ideology.", DefaultValue = null)]
            string faceTattoo = null,
            [ToolParameter(Description = "TattooDef defName for the body, e.g. NoTattoo_Body. " +
                "Needs Ideology.", DefaultValue = null)]
            string bodyTattoo = null,
            [ToolParameter(Description = "HeadTypeDef defName. Not validated against the " +
                "pawn's gender or genes -- vanilla filters on those, a direct write does not.",
                DefaultValue = null)]
            string headType = null,
            [ToolParameter(Description = "BodyTypeDef defName: Male, Female, Thin, Hulk, Fat, " +
                "Baby, Child.", DefaultValue = null)]
            string bodyType = null,
            [ToolParameter(Description = "FurDef defName (Biotech fur layer).", DefaultValue = null)]
            string fur = null,
            [ToolParameter(Description =
                "Skin colour, same formats as hairColor, or 'clear' to drop the override and " +
                "let genes decide. Writes story.skinColorOverride, which is the field RimWorld " +
                "actually saves.", DefaultValue = null)]
            string skinColor = null)
        {
            var asked = new List<string>();
            if (!string.IsNullOrWhiteSpace(hair)) asked.Add("hair");
            if (!string.IsNullOrWhiteSpace(hairColor)) asked.Add("hairColor");
            if (!string.IsNullOrWhiteSpace(beard)) asked.Add("beard");
            if (!string.IsNullOrWhiteSpace(faceTattoo)) asked.Add("faceTattoo");
            if (!string.IsNullOrWhiteSpace(bodyTattoo)) asked.Add("bodyTattoo");
            if (!string.IsNullOrWhiteSpace(headType)) asked.Add("headType");
            if (!string.IsNullOrWhiteSpace(bodyType)) asked.Add("bodyType");
            if (!string.IsNullOrWhiteSpace(fur)) asked.Add("fur");
            if (!string.IsNullOrWhiteSpace(skinColor)) asked.Add("skinColor");
            if (asked.Count == 0)
                return Fail("Nothing to set. Pass at least one of: hair, hairColor, beard, " +
                            "faceTattoo, bodyTattoo, headType, bodyType, fur, skinColor.");

            // ⚠️ Pawn_StyleTracker.set_FaceTattoo / set_BodyTattoo open with
            // ModLister.CheckIdeology and RETURN if it is absent. Without this
            // guard the tool would report a tattoo it never applied.
            if (!ModsConfig.IdeologyActive
                && (!string.IsNullOrWhiteSpace(faceTattoo) || !string.IsNullOrWhiteSpace(bodyTattoo)))
                return Fail("Tattoos need Ideology, and RimWorld's tattoo setters silently " +
                            "return when it is absent. Refusing rather than reporting a " +
                            "change that cannot happen.");

            UnityEngine.Color hairCol = UnityEngine.Color.white, skinCol = UnityEngine.Color.white;
            var clearSkin = string.Equals((skinColor ?? "").Trim(), "clear",
                                          StringComparison.OrdinalIgnoreCase);
            if (!string.IsNullOrWhiteSpace(hairColor))
            {
                string why;
                if (!TryParseColor(hairColor, out hairCol, out why))
                    return Fail($"hairColor '{hairColor}' is not a colour: {why}.");
            }
            if (!string.IsNullOrWhiteSpace(skinColor) && !clearSkin)
            {
                string why;
                if (!TryParseColor(skinColor, out skinCol, out why))
                    return Fail($"skinColor '{skinColor}' is not a colour: {why}.");
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                object err;
                var pawns = ResolvePawns(map, pawnId, out err);
                if (pawns == null) return err;

                // Resolve every def up front. A typo must not leave half a
                // pawn restyled and still return success.
                HairDef hairD = null; BeardDef beardD = null;
                TattooDef faceD = null, bodyD = null;
                HeadTypeDef headD = null; BodyTypeDef bodyTD = null; FurDef furD = null;

                if (!string.IsNullOrWhiteSpace(hair))
                {
                    hairD = DefDatabase<HairDef>.GetNamedSilentFail(hair.Trim());
                    if (hairD == null) return Fail($"No HairDef named '{hair}'.",
                        new { suggestions = DefSuggestions<HairDef>(hair) });
                }
                if (!string.IsNullOrWhiteSpace(beard))
                {
                    beardD = DefDatabase<BeardDef>.GetNamedSilentFail(beard.Trim());
                    if (beardD == null) return Fail($"No BeardDef named '{beard}'.",
                        new { suggestions = DefSuggestions<BeardDef>(beard) });
                }
                if (!string.IsNullOrWhiteSpace(faceTattoo))
                {
                    faceD = DefDatabase<TattooDef>.GetNamedSilentFail(faceTattoo.Trim());
                    if (faceD == null) return Fail($"No TattooDef named '{faceTattoo}'.",
                        new { suggestions = DefSuggestions<TattooDef>(faceTattoo) });
                }
                if (!string.IsNullOrWhiteSpace(bodyTattoo))
                {
                    bodyD = DefDatabase<TattooDef>.GetNamedSilentFail(bodyTattoo.Trim());
                    if (bodyD == null) return Fail($"No TattooDef named '{bodyTattoo}'.",
                        new { suggestions = DefSuggestions<TattooDef>(bodyTattoo) });
                }
                if (!string.IsNullOrWhiteSpace(headType))
                {
                    headD = DefDatabase<HeadTypeDef>.GetNamedSilentFail(headType.Trim());
                    if (headD == null) return Fail($"No HeadTypeDef named '{headType}'.",
                        new { suggestions = DefSuggestions<HeadTypeDef>(headType) });
                }
                if (!string.IsNullOrWhiteSpace(bodyType))
                {
                    bodyTD = DefDatabase<BodyTypeDef>.GetNamedSilentFail(bodyType.Trim());
                    if (bodyTD == null) return Fail($"No BodyTypeDef named '{bodyType}'.",
                        new { suggestions = DefSuggestions<BodyTypeDef>(bodyType) });
                }
                if (!string.IsNullOrWhiteSpace(fur))
                {
                    furD = DefDatabase<FurDef>.GetNamedSilentFail(fur.Trim());
                    if (furD == null) return Fail($"No FurDef named '{fur}'.",
                        new { suggestions = DefSuggestions<FurDef>(fur) });
                }

                var rows = new List<object>();
                var fullyApplied = 0;
                foreach (var pawn in pawns)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    // PawnComponentsUtility only allocates story and style for
                    // humanlike pawns. Touching either on an animal is an NRE.
                    if (pawn.story == null || pawn.style == null)
                    {
                        rows.Add(new
                        {
                            id = pawn.ThingID,
                            name = pawn.LabelShortCap,
                            ok = false,
                            error = "NoStyleTrackers",
                            message = "Not humanlike: this pawn has no story/style tracker."
                        });
                        continue;
                    }

                    var changes = new List<object>();
                    var okAll = true;

                    if (hairD != null)
                    {
                        var was = pawn.story.hairDef?.defName;
                        pawn.story.hairDef = hairD;
                        var now = pawn.story.hairDef?.defName;
                        var ok = now == hairD.defName; okAll &= ok;
                        changes.Add(new { field = "hair", was, now, ok });
                    }
                    if (!string.IsNullOrWhiteSpace(hairColor))
                    {
                        var was = ColorStr(pawn.story.HairColor);
                        pawn.story.HairColor = hairCol;
                        var now = ColorStr(pawn.story.HairColor);
                        // get_HairColor filters through rot/shambler colour for
                        // corpses and mutants, so a read-back mismatch here is
                        // informative rather than automatically a failure --
                        // report it, do not fail the call on it.
                        changes.Add(new
                        {
                            field = "hairColor",
                            was,
                            now,
                            requested = ColorStr(hairCol),
                            ok = true,
                            note = now == ColorStr(hairCol) ? null
                                 : "Read-back differs: get_HairColor filters rotting/shambler pawns."
                        });
                    }
                    if (beardD != null)
                    {
                        var was = pawn.style.beardDef?.defName;
                        pawn.style.beardDef = beardD;
                        var now = pawn.style.beardDef?.defName;
                        var ok = now == beardD.defName; okAll &= ok;
                        changes.Add(new { field = "beard", was, now, ok });
                    }
                    if (faceD != null)
                    {
                        var was = pawn.style.FaceTattoo?.defName;
                        pawn.style.FaceTattoo = faceD;
                        var now = pawn.style.FaceTattoo?.defName;
                        var ok = now == faceD.defName; okAll &= ok;
                        changes.Add(new { field = "faceTattoo", was, now, ok });
                    }
                    if (bodyD != null)
                    {
                        var was = pawn.style.BodyTattoo?.defName;
                        pawn.style.BodyTattoo = bodyD;
                        var now = pawn.style.BodyTattoo?.defName;
                        var ok = now == bodyD.defName; okAll &= ok;
                        changes.Add(new { field = "bodyTattoo", was, now, ok });
                    }
                    if (headD != null)
                    {
                        var was = pawn.story.headType?.defName;
                        pawn.story.headType = headD;
                        var now = pawn.story.headType?.defName;
                        var ok = now == headD.defName; okAll &= ok;
                        changes.Add(new { field = "headType", was, now, ok });
                    }
                    if (bodyTD != null)
                    {
                        var was = pawn.story.bodyType?.defName;
                        pawn.story.bodyType = bodyTD;
                        var now = pawn.story.bodyType?.defName;
                        var ok = now == bodyTD.defName; okAll &= ok;
                        changes.Add(new { field = "bodyType", was, now, ok });
                    }
                    if (furD != null)
                    {
                        var was = pawn.story.furDef?.defName;
                        pawn.story.furDef = furD;
                        var now = pawn.story.furDef?.defName;
                        var ok = now == furD.defName; okAll &= ok;
                        changes.Add(new { field = "fur", was, now, ok });
                    }
                    if (!string.IsNullOrWhiteSpace(skinColor))
                    {
                        var was = pawn.story.skinColorOverride.HasValue
                            ? ColorStr(pawn.story.skinColorOverride.Value) : "(none)";
                        pawn.story.skinColorOverride =
                            clearSkin ? (UnityEngine.Color?)null : skinCol;
                        var now = pawn.story.skinColorOverride.HasValue
                            ? ColorStr(pawn.story.skinColorOverride.Value) : "(none)";
                        var ok = clearSkin ? !pawn.story.skinColorOverride.HasValue
                                           : now == ColorStr(skinCol);
                        okAll &= ok;
                        changes.Add(new { field = "skinColor", was, now, ok });
                    }

                    // THE line that makes any of it visible. It clears the
                    // pending-look fields and then calls
                    // pawn.Drawer.renderer.SetAllGraphicsDirty(). Main thread
                    // only -- it runs Unity work synchronously on the caller.
                    pawn.style.Notify_StyleItemChanged();

                    if (okAll) fullyApplied++;
                    rows.Add(new
                    {
                        id = pawn.ThingID,
                        name = pawn.LabelShortCap,
                        ok = okAll,
                        rendered = pawn.Spawned,
                        changes
                    });
                }

                return new
                {
                    success = rows.Count > 0 && fullyApplied == rows.Count,
                    message = $"Restyled {fullyApplied}/{rows.Count} pawn(s): " +
                              $"{string.Join(", ", asked)}.",
                    fieldsRequested = asked,
                    pawnsChanged = fullyApplied,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        private static string ColorStr(UnityEngine.Color c) =>
            $"{c.r:0.###},{c.g:0.###},{c.b:0.###}";

        [Tool(
            "jawa/set_pawn_rotation",
            Description =
                "Turn spawned pawns to face a chosen direction and FREEZE them there, so an " +
                "art, apparel or xenotype audit can photograph a named side. A bare rotation " +
                "write does not survive: Pawn_RotationTracker.UpdateRotation re-faces every " +
                "pawn each tick from its job, its path and its drafted state -- a DRAFTED pawn " +
                "is slammed to South every tick. This sets Thing.debugRotLocked, the same " +
                "mechanism the vanilla dev 'Lock rotation' action uses, so the facing holds " +
                "against the engine. Pass dir='unlock' to release. ALWAYS unlock when the " +
                "audit is done: debugRotLocked is written by Thing.ExposeData, so a pawn left " +
                "locked stays locked across a save and load.",
            ResultDescription =
                "Returns per pawn the requested rotation and the READ-BACK rotation, the " +
                "posture, and 'visible' -- false when the pawn is laying or downed, because " +
                "the renderer calls LayingFacing() and ignores Rotation entirely for those. " +
                "success is false unless every pawn actually reads back the rotation asked " +
                "for, so a locked or laying pawn cannot report a turn that did not happen.")]
        public static async Task<object> SetPawnRotation(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "One ThingID, a comma-separated list of them, 'all' for every spawned pawn, " +
                "or 'colonists'.")]
            string pawnId,
            [ToolParameter(Description =
                "'north' / 'east' / 'south' / 'west' (or n/e/s/w, or 0-3), or 'unlock' to " +
                "release a previous freeze without turning the pawn.")]
            string dir,
            [ToolParameter(Description =
                "Hold the facing against the engine by setting debugRotLocked. Turn this off " +
                "only if you want the pawn to resume normal facing on the next tick.",
                DefaultValue = true)]
            bool lockRotation = true)
        {
            var unlock = string.Equals((dir ?? "").Trim(), "unlock",
                                       StringComparison.OrdinalIgnoreCase);
            Rot4 want = Rot4.South;
            if (!unlock && !TryParseRot(dir, out want))
                return Fail($"dir '{dir}' is not a direction.", new
                {
                    accepted = new[] { "north", "east", "south", "west",
                                       "n", "e", "s", "w", "0", "1", "2", "3", "unlock" }
                });

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                object err;
                var pawns = ResolvePawns(map, pawnId, out err);
                if (pawns == null) return err;

                var rows = new List<object>();
                var applied = 0;
                var hidden = 0;
                foreach (var pawn in pawns)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    var posture = PawnUtility.GetPosture(pawn);
                    // ⚠️ The renderer only reads Thing.Rotation for a STANDING or
                    // crawling pawn. For anything laying down it calls
                    // PawnRenderer.LayingFacing(), which derives the facing from
                    // the bed, the job, or thingIDNumber % 4 -- so a turn applied
                    // to a downed or sleeping pawn is a perfect silent no-op:
                    // the field takes the value and the screen never changes.
                    var visible = posture == PawnPosture.Standing || pawn.Crawling;
                    var before = pawn.Rotation;

                    // Order is mandatory. Thing.set_Rotation opens with
                    //   if (value == rotationInt || debugRotLocked) return;
                    // so setting a rotation on an already-locked pawn returns
                    // clean and changes nothing. Clear, set, then re-lock.
                    pawn.debugRotLocked = false;
                    if (!unlock)
                    {
                        pawn.Rotation = want;
                        pawn.debugRotLocked = lockRotation;
                    }

                    var after = pawn.Rotation;
                    var ok = unlock || after.AsInt == want.AsInt;
                    if (ok) applied++;
                    if (!unlock && !visible) hidden++;

                    rows.Add(new
                    {
                        id = pawn.ThingID,
                        name = pawn.LabelShortCap,
                        kind = pawn.kindDef?.defName,
                        requested = unlock ? "unlock" : want.ToStringHuman(),
                        before = before.ToStringHuman(),
                        after = after.ToStringHuman(),
                        applied = ok,
                        locked = pawn.debugRotLocked,
                        posture = posture.ToString(),
                        drafted = pawn.Drafted,
                        visible,
                        note = visible ? null
                             : "Laying/downed: the renderer ignores Rotation for this posture."
                    });
                }

                var verb = unlock ? "Unlocked" : "Turned";
                return new
                {
                    success = rows.Count > 0 && applied == rows.Count,
                    message = $"{verb} {applied}/{rows.Count} pawn(s)" +
                              (unlock ? "." : $" to {want.ToStringHuman()}.") +
                              (hidden > 0
                                  ? $" ⚠️ {hidden} of them are laying/downed, so the turn will " +
                                    "not show on screen."
                                  : ""),
                    turned = applied,
                    notVisible = hidden,
                    locked = !unlock && lockRotation,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/set_pawn_xenotype",
            Description =
                "Convert already-spawned pawns to a XenotypeDef in place, so a xenotype's art, " +
                "genes and apparel fit can be audited without regenerating pawns until one " +
                "rolls right. This is exactly what the vanilla dev 'Set xenotype' action does " +
                "-- DebugToolsPawns.SetXenotype's per-def closure is pawn.genes?.SetXenotype(def) " +
                "and nothing else -- so the appearance refresh comes for free: SetXenotype adds " +
                "the xenotype's genes, AddGene calls Notify_GenesChanged, and that ends in " +
                "PawnRenderer.SetAllGraphicsDirty. ⚠️ SetXenotype clears XENOgenes only. An " +
                "inheritable xenotype's genes land as ENDOgenes and survive a later conversion, " +
                "so converting a pawn twice leaves the first xenotype's genes behind -- pass " +
                "clearEndogenes to strip them. Xenotypes present on this stack include " +
                "BTD_Jawa (inheritable, the one our Jawa patches target), OuterRim_Jawa, " +
                "guy762_xenotype_jawa and Jawa_Xeno_Gamorrean. Needs Biotech: " +
                "Pawn_GeneTracker.SetXenotype opens with ModLister.CheckBiotech and RETURNS " +
                "when it is absent.",
            ResultDescription =
                "Returns per pawn the before/after xenotype READ BACK OFF THE PAWN, the gene " +
                "counts either side, and whether stale endogenes remain. success is false " +
                "unless every pawn reads back the xenotype asked for.")]
        public static async Task<object> SetPawnXenotype(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "One ThingID, a comma-separated list, 'all' or 'colonists'.")]
            string pawnId,
            [ToolParameter(Description =
                "XenotypeDef defName, e.g. BTD_Jawa, OuterRim_Jawa, Baseliner.")]
            string xenotype,
            [ToolParameter(Description =
                "Remove every existing ENDOgene before converting. RimWorld's own action does " +
                "not do this, so it is off by default -- but without it a pawn converted away " +
                "from an inheritable xenotype keeps that xenotype's genes and is a hybrid " +
                "wearing the new label.", DefaultValue = false)]
            bool clearEndogenes = false)
        {
            if (string.IsNullOrWhiteSpace(xenotype)) return Fail("xenotype is required.");

            // ⚠️ Pawn_GeneTracker.SetXenotype opens with ModLister.CheckBiotech and
            // returns. Without this guard the tool would report a conversion that
            // could not have happened -- the same failure the Ideology guard on
            // set_pawn_style exists to prevent.
            if (!ModsConfig.BiotechActive)
                return Fail("Xenotypes need Biotech, and RimWorld's SetXenotype silently " +
                            "returns when it is absent. Refusing rather than reporting a " +
                            "change that cannot happen.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var xeno = DefDatabase<XenotypeDef>.GetNamedSilentFail(xenotype.Trim());
                if (xeno == null)
                    return Fail($"No XenotypeDef named '{xenotype}'.",
                        new { suggestions = DefSuggestions<XenotypeDef>(xenotype) });

                object err;
                var pawns = ResolvePawns(map, pawnId, out err);
                if (pawns == null) return err;

                var rows = new List<object>();
                var applied = 0;
                foreach (var pawn in pawns)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    // Animals and mechs have no gene tracker at all; touching it is an NRE.
                    if (pawn.genes == null)
                    {
                        rows.Add(new
                        {
                            id = pawn.ThingID,
                            name = pawn.LabelShortCap,
                            ok = false,
                            error = "NoGeneTracker",
                            message = "This pawn has no Pawn_GeneTracker (not a gene-bearing " +
                                      "humanlike), so it cannot have a xenotype."
                        });
                        continue;
                    }

                    var was = pawn.genes.Xenotype?.defName;
                    var wasCustom = pawn.genes.UniqueXenotype;
                    var endoBefore = pawn.genes.Endogenes?.Count ?? 0;
                    var xenoBefore = pawn.genes.Xenogenes?.Count ?? 0;

                    var endogenesCleared = 0;
                    if (clearEndogenes && pawn.genes.Endogenes != null)
                    {
                        // Copy first: RemoveGene mutates the list being walked.
                        foreach (var g in pawn.genes.Endogenes.ToList())
                        {
                            pawn.genes.RemoveGene(g);
                            endogenesCleared++;
                        }
                    }

                    pawn.genes.SetXenotype(xeno);

                    // SetXenotype refreshes the graphics only as a side effect of
                    // AddGene -> Notify_GenesChanged -> SetAllGraphicsDirty. A
                    // xenotype with NO genes (Baseliner) therefore adds nothing and
                    // dirties nothing, and the pawn keeps drawing its old look.
                    if (pawn.Spawned && pawn.Drawer?.renderer != null)
                        pawn.Drawer.renderer.SetAllGraphicsDirty();

                    var now = pawn.genes.Xenotype?.defName;
                    var ok = now == xeno.defName;
                    if (ok) applied++;

                    var endoAfter = pawn.genes.Endogenes?.Count ?? 0;
                    var xenoAfter = pawn.genes.Xenogenes?.Count ?? 0;
                    // Genes the new xenotype did not put there. Only meaningful for a
                    // non-inheritable xenotype, whose own genes are all xenogenes.
                    var stale = !xeno.inheritable && endoAfter > 0;

                    rows.Add(new
                    {
                        id = pawn.ThingID,
                        name = pawn.LabelShortCap,
                        ok,
                        was,
                        now,
                        requested = xeno.defName,
                        wasUniqueXenotype = wasCustom,
                        inheritable = xeno.inheritable,
                        genesInDef = xeno.genes?.Count ?? 0,
                        endogenesBefore = endoBefore,
                        endogenesAfter = endoAfter,
                        xenogenesBefore = xenoBefore,
                        xenogenesAfter = xenoAfter,
                        endogenesCleared,
                        hybrid = pawn.genes.hybrid,
                        staleEndogenes = stale,
                        rendered = pawn.Spawned,
                        note = stale
                            ? "Endogenes survive SetXenotype: these came from an earlier " +
                              "inheritable xenotype. Pass clearEndogenes to strip them."
                            : null
                    });
                }

                return new
                {
                    success = rows.Count > 0 && applied == rows.Count,
                    message = $"Converted {applied}/{rows.Count} pawn(s) to {xeno.defName}.",
                    xenotype = xeno.defName,
                    pawnsChanged = applied,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---- jawa/order_pawn -------------------------------------------------
        // Every name below was READ OUT OF Assembly-CSharp.dll with ilprobe on
        // 2026-08-13. None of it is from memory.
        //   Verse.JobMaker.MakeJob(JobDef, LocalTargetInfo)
        //   Verse.LocalTargetInfo.op_Implicit(IntVec3)
        //   Verse.AI.Pawn_JobTracker.TryTakeOrderedJob(Job, JobTag?, bool)
        //   RimWorld.JobDefOf.Goto
        //   Verse.AI.JobTag.DraftedOrder = 6 / JobTag.Misc = 0   (enumdump)
        //   Verse.ReachabilityUtility.CanReach(Pawn, LocalTargetInfo, PathEndMode,
        //       Danger, bool canBashDoors, bool canBashFences, TraverseMode)
        //   Verse.PathEndMode.OnCell = 1, Verse.Danger.Deadly = 3,
        //       Verse.TraverseMode.ByPawn = 0
        //   Verse.Pawn_PathFollower.Destination / Moving  (Pawn.pather)
        //   RimWorld.Pawn_DraftController.Drafted         (Pawn.drafter)
        //   Verse.TickManager.CurTimeSpeed / Paused / TicksGame
        //
        // 🔴 WHY THE READ-BACK IS THE ENTIRE TOOL.
        // TryTakeOrderedJob returns TRUE for a job it merely ENQUEUED: IL_013f,
        // IL_01ac and IL_01fa each `ldc.i4.1; ret` immediately after
        // JobQueue::EnqueueFirst / EnqueueLast, and nothing anywhere in the
        // method consults reachability. So "order accepted" is NOT "pawn moved",
        // and a tool that returned that bool would be a textbook silent success.
        // This one waits for real game ticks and reports the position it read
        // back afterwards. success is arrival, measured.
        //
        // The one refusal path worth naming: IL_004a calls
        // IsCurrentJobPlayerInterruptible, which is false when the current
        // JobDef has playerInterruptible=false, when the JobDriver says so, or
        // when the pawn is ON FIRE (AttachmentUtility.HasAttachment(Fire)).
        // That is the only case where the bool itself comes back false.
        [Tool(
            "jawa/order_pawn",
            Description =
                "Order named pawns to WALK to a map cell, then wait for game ticks and report " +
                "where they actually ended up. This is the primitive the bridge was missing: " +
                "rimworld/right_click_cell dispatches a synthetic click and produces no move " +
                "order at all (measured 2026-08-13: pawn sat still through 2,400 ticks with " +
                "the target on screen). This issues the real thing — JobMaker.MakeJob(Goto, " +
                "cell) through Pawn_JobTracker.TryTakeOrderedJob, the same call the vanilla " +
                "right-click menu makes. Use it for reachability, door function, room " +
                "enclosure, boardability and trap tests: 'walk a pawn there and see' is a " +
                "whole class of live test, and none of it was runnable before this. " +
                "⚠️ A paused game cannot move a pawn; unpause=true briefly sets Normal speed " +
                "and restores the previous speed when done.",
            ResultDescription =
                "Per pawn: the start cell, the READ-BACK end cell, arrived, moved, the " +
                "straight-line distance before and after, canReach computed BEFORE the order, " +
                "whether TryTakeOrderedJob accepted it, the pawn's current job and its pather " +
                "destination. Top level carries ticksElapsed — if that is 0 the game never " +
                "ticked and nothing below it means anything. success is true only when every " +
                "pawn is standing on the requested cell, read back from the map; the accept " +
                "bool is never treated as arrival.")]
        public static async Task<object> OrderPawn(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "One ThingID, a comma-separated list of them, 'all' for every spawned pawn, " +
                "or 'colonists'.")]
            string pawnId,
            [ToolParameter(Description =
                "Destination cell X. Omit when targetId is given.", DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description =
                "Destination cell Z. Omit when targetId is given.", DefaultValue = -1)]
            int z = -1,
            [ToolParameter(Description =
                "Instead of a cell, a ThingID to walk to — the destination becomes that " +
                "thing's InteractionCell and reachability is computed against the THING, " +
                "which is what the game's own gates do. Overrides x/z when given.")]
            string targetId = null,
            [ToolParameter(Description =
                "'oncell', 'touch', 'closesttouch', 'interactioncell' or 'none' — how close " +
                "counts as reached, for the canReach computation. Defaults to " +
                "'interactioncell' when targetId is given and 'oncell' otherwise, because " +
                "that is what each case means. ⚠️ These are NOT interchangeable: a pawn can " +
                "reach the cell beside a console and still fail 'interactioncell'.")]
            string pathEndMode = null,
            [ToolParameter(Description =
                "Draft the pawn first. A drafted pawn holds the destination instead of " +
                "wandering off to its own work the moment it arrives, which is what you want " +
                "for a measurement. Pawns with no drafter (animals, non-player pawns) are " +
                "ordered undrafted and say so in their row.",
                DefaultValue = true)]
            bool draft = true,
            [ToolParameter(Description =
                "Undraft again once the walk is measured. Leave false if you are about to " +
                "issue more orders; the response lists anyone left drafted either way.",
                DefaultValue = false)]
            bool undraftAfter = false,
            [ToolParameter(Description =
                "How many GAME ticks to wait for the walk before reading back. 300 is ~5 " +
                "seconds of Normal speed and crosses roughly 60 cells of open ground.",
                DefaultValue = 300)]
            int waitTicks = 300,
            [ToolParameter(Description =
                "Wall-clock ceiling on the wait, so a paused or hitching game cannot hang the " +
                "call. Hitting this is reported, never silently treated as arrival.",
                DefaultValue = 30)]
            int timeoutSeconds = 30,
            [ToolParameter(Description =
                "If the game is paused, run at Normal speed for the duration of the wait and " +
                "restore the previous speed afterwards. With this off, a paused game returns " +
                "ticksElapsed=0 and nobody moves.",
                DefaultValue = true)]
            bool unpause = true)
        {
            if (waitTicks < 0) return Fail($"waitTicks must be >= 0, got {waitTicks}.");
            if (timeoutSeconds < 1 || timeoutSeconds > 300)
                return Fail($"timeoutSeconds must be 1-300, got {timeoutSeconds}.");

            var haveTarget = !string.IsNullOrWhiteSpace(targetId);
            if (!haveTarget && (x < 0 || z < 0))
                return Fail("No destination. Pass 'x' and 'z' for a cell, or 'targetId' for " +
                            "a thing. Nothing was ordered.",
                    new { xGiven = x, zGiven = z, targetIdGiven = targetId });

            PathEndMode peMode;
            var peAsked = (pathEndMode ?? "").Trim();
            if (peAsked.Length == 0)
                peMode = haveTarget ? PathEndMode.InteractionCell : PathEndMode.OnCell;
            else if (!TryParsePathEndMode(peAsked, out peMode))
                return Fail($"pathEndMode '{pathEndMode}' is not a mode.", new
                {
                    accepted = new[] { "oncell", "touch", "closesttouch",
                                       "interactioncell", "none" }
                });

            var dest = new IntVec3(x, 0, z);
            Thing target = null;
            List<Pawn> pawns = null;
            var starts = new Dictionary<string, IntVec3>();
            var accepted = new Dictionary<string, bool>();
            var reachable = new Dictionary<string, bool>();
            var drafterMissing = new List<string>();
            var startTicks = 0;
            TimeSpeed speedBefore = TimeSpeed.Paused;
            var speedChanged = false;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                if (haveTarget)
                {
                    var wanted = targetId.Trim();
                    target = map.listerThings.AllThings.FirstOrDefault(
                        t => string.Equals(t.ThingID, wanted,
                                           StringComparison.OrdinalIgnoreCase));
                    if (target == null)
                        return Fail($"No spawned thing on this map with id '{wanted}'.",
                            new { thingsOnMap = map.listerThings.AllThings.Count });
                    // InteractionCell is the cell a pawn STANDS IN to use the thing.
                    // It is invalid for anything with no interaction spot, in which
                    // case the thing's own cell is the only sensible destination.
                    var ic = target.def.hasInteractionCell
                        ? target.InteractionCell
                        : IntVec3.Invalid;
                    dest = ic.IsValid ? ic : target.Position;
                }

                if (!dest.InBounds(map))
                    return Fail($"({dest.x},{dest.z}) is outside the map.", new
                    {
                        mapSize = new { x = map.Size.x, z = map.Size.z }
                    });

                object err;
                pawns = ResolvePawns(map, pawnId, out err);
                if (pawns == null) return err;
                if (pawns.Count == 0) return Fail("No pawns matched.");

                var tm = Find.TickManager;
                startTicks = tm?.TicksGame ?? -1;
                if (tm != null)
                {
                    speedBefore = tm.CurTimeSpeed;
                    if (unpause && tm.CurTimeSpeed == TimeSpeed.Paused)
                    {
                        tm.CurTimeSpeed = TimeSpeed.Normal;
                        speedChanged = true;
                    }
                }

                foreach (var pawn in pawns)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var id = pawn.ThingID;
                    starts[id] = pawn.Position;

                    // Computed BEFORE the order, because TryTakeOrderedJob never
                    // looks at it: an unreachable Goto is accepted and then fails
                    // inside the pather, which is invisible from the return value.
                    // Target the THING when one was named. This is not cosmetic:
                    // RimWorld's own launch gate is
                    //   ReachabilityUtility.CanReach(pawn, console,
                    //       PathEndMode.InteractionCell, Danger.Deadly,
                    //       false, false, TraverseMode.ByPawn)
                    // at RitualBehaviorWorker_GravshipLaunch::PawnCanFillRole
                    // IL_0065-006A, immediately before it emits
                    // "NoPathToPilotConsole" at IL_0072. Passing targetId with the
                    // default pathEndMode reproduces that call exactly.
                    reachable[id] = target != null
                        ? ReachabilityUtility.CanReach(
                            pawn, target, peMode, Danger.Deadly,
                            false, false, TraverseMode.ByPawn)
                        : ReachabilityUtility.CanReach(
                            pawn, dest, peMode, Danger.Deadly,
                            false, false, TraverseMode.ByPawn);

                    if (draft)
                    {
                        if (pawn.drafter == null) drafterMissing.Add(id);
                        else if (!pawn.drafter.Drafted) pawn.drafter.Drafted = true;
                    }

                    if (pawn.jobs == null) { accepted[id] = false; continue; }
                    var job = JobMaker.MakeJob(JobDefOf.Goto, dest);
                    var tag = (pawn.Drafted ? JobTag.DraftedOrder : JobTag.Misc);
                    accepted[id] = pawn.jobs.TryTakeOrderedJob(job, tag, false);
                }
                return null;
            }, cancellationToken).ConfigureAwait(false);
            if (setup != null) return setup;

            // ---- the wait. Polled in game TICKS, not wall clock: the same
            // 300 ticks is 5 s at Normal and well under 1 s at Ultrafast, so a
            // fixed Task.Delay would either truncate the walk or waste a minute.
            var polls = 0;
            var elapsedMs = 0;
            var ticksNow = startTicks;
            var timedOut = false;
            while (true)
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (ticksNow - startTicks >= waitTicks) break;
                if (elapsedMs >= timeoutSeconds * 1000) { timedOut = true; break; }
                await Task.Delay(100, cancellationToken).ConfigureAwait(false);
                elapsedMs += 100;
                polls++;
                ticksNow = await ctx.MainThread.InvokeAsync(
                    () => TicksGameSafe(),
                    cancellationToken).ConfigureAwait(false);
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var tm = Find.TickManager;
                if (speedChanged && tm != null) tm.CurTimeSpeed = speedBefore;

                var rows = new List<object>();
                var arrived = 0;
                var moved = 0;
                var leftDrafted = new List<string>();

                foreach (var pawn in pawns)
                {
                    var id = pawn.ThingID;
                    var start = starts.TryGetValue(id, out var s) ? s : IntVec3.Invalid;
                    var gone = !pawn.Spawned || pawn.Destroyed;
                    var end = gone ? IntVec3.Invalid : pawn.Position;
                    var here = !gone && end == dest;
                    if (here) arrived++;
                    if (!gone && end != start) moved++;

                    if (undraftAfter && pawn.drafter != null && pawn.drafter.Drafted)
                        pawn.drafter.Drafted = false;
                    if (pawn.drafter != null && pawn.drafter.Drafted) leftDrafted.Add(id);

                    var ok = accepted.TryGetValue(id, out var acc) && acc;
                    var canGo = reachable.TryGetValue(id, out var r) && r;
                    var pathDest = (!gone && pawn.pather != null && pawn.pather.Moving)
                        ? pawn.pather.Destination.Cell
                        : IntVec3.Invalid;

                    string note = null;
                    if (gone) note = "Pawn is no longer spawned on this map.";
                    else if (here) note = null;
                    else if (!ok) note =
                        "TryTakeOrderedJob REFUSED the order. Its only refusal path is " +
                        "IsCurrentJobPlayerInterruptible: the current job is flagged " +
                        "playerInterruptible=false, its driver refuses interruption, or the " +
                        "pawn is on fire.";
                    else if (!canGo) note =
                        "Order accepted but the cell was UNREACHABLE when it was issued " +
                        "(CanReach false). The Goto job was taken and then failed in the " +
                        "pather — this is exactly the case the accept bool cannot see.";
                    else if (ticksNow - startTicks <= 0) note =
                        "The game did not tick. Nothing could move.";
                    else if (pawn.Downed) note = "Pawn is downed; it cannot walk.";
                    else if (pawn.pather != null && pawn.pather.Moving) note =
                        "Still walking — en route, not stalled. Re-read with a larger " +
                        "waitTicks, or call again with waitTicks=0 to sample the position.";
                    else note =
                        "Order accepted, cell reachable, ticks advanced, and the pawn is not " +
                        "moving. Something ended the job — check the pawn's current job.";

                    var dxS = start.x - dest.x; var dzS = start.z - dest.z;
                    var dxE = end.x - dest.x;   var dzE = end.z - dest.z;
                    rows.Add(new
                    {
                        id,
                        name = pawn.LabelShortCap,
                        kind = pawn.kindDef?.defName,
                        drafted = pawn.drafter != null && pawn.drafter.Drafted,
                        hasDrafter = pawn.drafter != null,
                        requested = new { x = dest.x, z = dest.z },
                        start = new { x = start.x, z = start.z },
                        end = gone ? null : new { x = end.x, z = end.z },
                        arrived = here,
                        moved = !gone && end != start,
                        distanceBefore = Math.Round(Math.Sqrt(dxS * dxS + dzS * dzS), 2),
                        distanceAfter = gone
                            ? -1.0
                            : Math.Round(Math.Sqrt(dxE * dxE + dzE * dzE), 2),
                        canReach = canGo,
                        orderAccepted = ok,
                        stillMoving = !gone && pawn.pather != null && pawn.pather.Moving,
                        pathDestination = pathDest.IsValid
                            ? new { x = pathDest.x, z = pathDest.z }
                            : null,
                        curJob = gone ? null : pawn.CurJobDef?.defName,
                        downed = !gone && pawn.Downed,
                        note
                    });
                }

                var ticksElapsed = ticksNow - startTicks;
                var where = target != null
                    ? $"({dest.x},{dest.z}), the interaction cell of {target.LabelShortCap}"
                    : $"({dest.x},{dest.z})";
                var msg = $"{arrived}/{rows.Count} pawn(s) standing on {where} after " +
                          $"{ticksElapsed} tick(s); {moved} moved at all.";
                if (ticksElapsed <= 0)
                    msg += " ⚠️ THE GAME DID NOT TICK — nothing here is a movement result. " +
                           (unpause
                               ? "Speed was raised but no ticks landed; the game may be " +
                                 "force-paused (a dialog is open) or not running."
                               : "Pass unpause=true, or set the speed yourself first.");
                else if (timedOut)
                    msg += $" ⚠️ Timed out at {timeoutSeconds}s with only {ticksElapsed} of " +
                           $"{waitTicks} ticks elapsed.";
                if (drafterMissing.Count > 0)
                    msg += $" {drafterMissing.Count} pawn(s) have no drafter and were ordered " +
                           "undrafted.";
                if (leftDrafted.Count > 0)
                    msg += $" ⚠️ LEFT DRAFTED: {string.Join(", ", leftDrafted)}. " +
                           "Pass undraftAfter=true or undraft them yourself.";

                return new
                {
                    success = rows.Count > 0 && arrived == rows.Count && ticksElapsed > 0,
                    message = msg,
                    arrivedCount = arrived,
                    movedCount = moved,
                    pawnCount = rows.Count,
                    destination = new { x = dest.x, z = dest.z },
                    targetId = target?.ThingID,
                    targetLabel = target?.LabelShortCap,
                    targetDef = target?.def?.defName,
                    pathEndMode = peMode.ToString(),
                    ticksElapsed,
                    ticksRequested = waitTicks,
                    timedOut,
                    polls,
                    waitedSeconds = Math.Round(elapsedMs / 1000.0, 1),
                    speedBefore = speedBefore.ToString(),
                    speedRestored = speedChanged,
                    leftDrafted,
                    noDrafter = drafterMissing,
                    pawns = rows,
                    ticksGame = tm?.TicksGame ?? -1
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---- jawa/world_stats ------------------------------------------------
        // WHY THIS EXISTS. The owner's world spec is "about a quarter ocean, in
        // three oddly-shaped bodies". The generator unaided gives 43-55% ocean in
        // scattered blobs, and ocean is an elevation rule at worldgen step 0 --
        // no slider touches it. So worldgen was HELD, because the only way to
        // find out what a world looks like was to spend the irreversible
        // Configure Factions click and look at it. That is not a search, it is a
        // guess costing 25-30 minutes a try.
        //
        // This measures instead. "43-55% in scattered blobs" becomes a number and
        // a body list, so a seed can be judged in one call rather than a session.
        //
        // Names read from Assembly-CSharp with ilprobe, not recalled:
        //   RimWorld.Planet.World.grid / .info
        //   WorldGrid.TilesCount, WorldGrid.get_Item(int) -> SurfaceTile,
        //     WorldGrid.GetTileNeighbors(PlanetTile, List<PlanetTile>)
        //   PlanetTile.op_Implicit(int)
        //   Tile.PrimaryBiome / .WaterCovered / .IsCoastal / .elevation
        //   WorldInfo.seedString / .planetCoverage / .overallRainfall /
        //     .overallTemperature
        [Tool(
            "jawa/world_stats",
            Description =
                "Measure the generated PLANET: how much of it is water, how that water is " +
                "distributed into separate bodies, and what the land is made of. Built for " +
                "one question — the owner's world spec asks for roughly a quarter ocean in " +
                "three oddly-shaped bodies, and the generator gives 43-55% in scattered " +
                "blobs. Ocean is an elevation rule at worldgen step 0 and no setting moves " +
                "it, so the only way to steer it is to generate, measure, and keep or " +
                "discard. This is the measure half. Read-only: it touches nothing and is " +
                "safe on a campaign world.",
            ResultDescription =
                "waterPct and landPct over all tiles; `bodies` — every connected water mass " +
                "with its tile count and share of the planet, largest first, which is what " +
                "answers 'how many oceans' rather than merely 'how much ocean'; " +
                "`biomes` — land tile counts by defName; coastalTiles; and the world's own " +
                "seedString and planetCoverage so a measurement can be tied back to the " +
                "world that produced it. ⚠️ A body of 1-2 tiles is a puddle, not an ocean: " +
                "read `bodiesOverMinSize`, not `bodies.Count`.")]
        public static async Task<object> WorldStats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Ignore water bodies smaller than this when counting how many there are. " +
                "The raw list is still returned in full.", DefaultValue = 8)]
            int minBodySize = 8,
            [ToolParameter(Description =
                "Cap on how many bodies to list, largest first. The COUNTS are computed " +
                "over every body regardless of this.", DefaultValue = 25)]
            int limit = 25)
        {
            if (minBodySize < 1) return Fail($"minBodySize must be >= 1, got {minBodySize}.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                // 🔴 Current.CreatingWorld is the whole point of this fallback.
                // The owner's sea problem is "generate, look, keep or discard",
                // and the moment that decision is made is AT THE WORLD-CREATION
                // SCREEN -- before any commit, while Find.World may still be
                // null. WorldGenerator.GenerateWorld sets Current.CreatingWorld
                // (IL_009f) and reads the grid back through Find during
                // generation, so a world being previewed is readable here.
                //
                // ⚠️ Deliberately NOT shipping a jawa/generate_world to drive
                // that loop from outside. GenerateWorld runs the whole
                // GameSetupStep chain, and I could not establish offline that
                // calling it with no Current.Game is safe -- it would clobber
                // Find.World if a colony were loaded. A tool that might destroy
                // a session on its first use is not worth the round trip it
                // saves. The human clicks generate; this measures what came out.
                var world = Find.World ?? Current.CreatingWorld;
                if (world == null)
                    return Fail("No world. This reads the PLANET, so it needs a world " +
                                "either loaded or being created — the main menu alone is " +
                                "not enough. Open the world-creation screen and generate " +
                                "one, then call again.");
                var previewing = Find.World == null;
                var grid = world.grid;
                if (grid == null) return Fail("World has no grid.");

                var n = grid.TilesCount;
                if (n <= 0) return Fail($"World grid reports {n} tiles.");

                var water = new bool[n];
                var biomes = new Dictionary<string, int>();
                var waterCount = 0;
                var coastal = 0;

                for (var i = 0; i < n; i++)
                {
                    if ((i & 1023) == 0) cancellationToken.ThrowIfCancellationRequested();
                    var t = grid[i];
                    if (t == null) continue;
                    if (t.WaterCovered) { water[i] = true; waterCount++; }
                    else
                    {
                        var b = t.PrimaryBiome?.defName ?? "(null)";
                        biomes.TryGetValue(b, out var c);
                        biomes[b] = c + 1;
                        if (t.IsCoastal) coastal++;
                    }
                }

                // Connected water masses. THIS is the part that distinguishes
                // "three oddly-shaped bodies" from "the same water area smeared
                // into forty blobs" -- two worlds that report an identical
                // waterPct and are nothing alike. A percentage alone cannot
                // answer the owner's question.
                // 🔴 Per-body SHAPE, not just size. A retired seat's sea gate has five
                // numeric criteria and two of them were uncollectable from tile
                // counts alone: perimeter²/area (the "is it a sea or a smear"
                // test, and the one that seat flagged as most likely to be quietly
                // failed) and the body's centroid latitude. Worldgen is an
                // IRREVERSIBLE click, so a candidate that cannot be measured
                // before it is kept is a candidate kept on hope.
                //
                // perimeter = count of tile edges where a body tile touches
                // non-water or the grid edge. area = tile count. Both are in
                // tile units, so the ratio is dimensionless and comparable
                // across worlds — which is what makes a threshold meaningful.
                var seen = new bool[n];
                var sizes = new List<BodyShape>();
                var stack = new Stack<int>();
                // Fully qualified on purpose: `PlanetTile` lives in
                // RimWorld.Planet and there is no `using` for it here. Adding one
                // would drag in World, Tile and Settlement alongside names this
                // file already uses.
                var nbrs = new List<RimWorld.Planet.PlanetTile>();
                for (var i = 0; i < n; i++)
                {
                    if (!water[i] || seen[i]) continue;
                    cancellationToken.ThrowIfCancellationRequested();
                    var size = 0;
                    // 🔴 TWO perimeters, and the distinction cost a wrong gate
                    // reading on 2026-08-14. The sea spec defines perimeter as
                    // "count of water tiles with at least one land neighbour" —
                    // a count of TILES. The original implementation counted
                    // EDGES, and a hex tile has ~6 of them, so the two differ by
                    // up to 6x — and `raggedness` SQUARES it, so up to 36x. The
                    // first real reading returned 82,715 against a threshold of
                    // 25 whose reference is a circle at 4pi = 12.57.
                    // ⇒ both are reported, and `raggedness` is computed from the
                    // TILE count, because that is the one the gate is written
                    // against. That seat checked the threshold against this grid
                    // rather than assuming: for a hex disc of radius r, tiles
                    // 3r^2+3r+1 and boundary 6r give P^2/A -> ~12 as r grows, so
                    // "beat 25" still means "twice as ragged as round".
                    var perimeterEdges = 0;
                    var perimeterTiles = 0;
                    // Latitude is averaged over the body's tiles. Longitude is
                    // deliberately NOT averaged: it wraps at the antimeridian, so
                    // a body straddling it would average to the wrong hemisphere.
                    // Latitude does not wrap, so the mean is sound.
                    var latSum = 0.0;
                    stack.Push(i);
                    seen[i] = true;
                    while (stack.Count > 0)
                    {
                        var cur = stack.Pop();
                        size++;
                        latSum += grid.LongLatOf(cur).y;
                        nbrs.Clear();
                        grid.GetTileNeighbors(cur, nbrs);
                        var onBoundary = false;
                        foreach (var nb in nbrs)
                        {
                            int id = nb;
                            // An edge to land, or off the grid, is a perimeter edge.
                            if (id < 0 || id >= n || !water[id])
                            {
                                perimeterEdges++;
                                onBoundary = true;
                                continue;
                            }
                            if (seen[id]) continue;
                            seen[id] = true;
                            stack.Push(id);
                        }
                        // Counted ONCE per tile however many land neighbours it
                        // has — that is what makes it a tile count rather than
                        // an edge count.
                        if (onBoundary) perimeterTiles++;
                    }
                    sizes.Add(new BodyShape
                    {
                        Tiles = size,
                        Perimeter = perimeterEdges,
                        PerimeterTiles = perimeterTiles,
                        CentroidLat = size > 0 ? latSum / size : 0.0
                    });
                }
                sizes.Sort((a, b) => b.Tiles.CompareTo(a.Tiles));

                double Pct(int v) => Math.Round(100.0 * v / n, 2);
                var big = sizes.Count(v => v.Tiles >= minBodySize);
                var info = world.info;

                return new
                {
                    success = true,
                    message =
                        $"{Pct(waterCount)}% water over {n} tiles, in {big} " +
                        $"body/bodies of >= {minBodySize} tiles " +
                        $"({sizes.Count} counting puddles). Largest is " +
                        $"{(sizes.Count > 0 ? Pct(sizes[0].Tiles) : 0)}% of the planet." +
                        (previewing
                            ? " (Measured on a world being PREVIEWED at the creation "
                              + "screen, not a loaded one.)"
                            : ""),
                    tilesTotal = n,
                    waterTiles = waterCount,
                    waterPct = Pct(waterCount),
                    landPct = Pct(n - waterCount),
                    coastalTiles = coastal,
                    bodiesOverMinSize = big,
                    bodiesTotal = sizes.Count,
                    minBodySize,
                    largestBodyPct = sizes.Count > 0 ? Pct(sizes[0].Tiles) : 0,
                    bodies = sizes.Take(limit)
                        .Select(v => new
                        {
                            tiles = v.Tiles,
                            pct = Pct(v.Tiles),
                            // Both, named for what they count. `perimeter` was
                            // ambiguous and the ambiguity produced a wrong gate
                            // reading, so the old name is retired.
                            perimeterEdges = v.Perimeter,
                            perimeterTiles = v.PerimeterTiles,
                            // The raggedness number the sea gate is written
                            // against — computed from the TILE count, matching
                            // the spec's own definition. Guarded rather than
                            // assumed: a zero-area body cannot occur here, but
                            // dividing by it silently would produce Infinity and
                            // read as a spectacular pass.
                            raggedness = v.Tiles > 0
                                ? Math.Round((double)v.PerimeterTiles * v.PerimeterTiles
                                             / v.Tiles, 2)
                                : 0.0,
                            // Edge-based ratio, kept only so the two can be told
                            // apart in any reading taken before this fix.
                            raggednessEdges = v.Tiles > 0
                                ? Math.Round((double)v.Perimeter * v.Perimeter / v.Tiles, 2)
                                : 0.0,
                            centroidLat = Math.Round(v.CentroidLat, 3),
                            // 🔴 The gate's band (0.35-0.65) is a FRACTION and
                            // the doc never said so. Degrees alone made 46.634
                            // read as a catastrophic failure when |lat|/90 =
                            // 0.518 sits mid-band. Ship both; name the units.
                            centroidLatNorm = Math.Round(Math.Abs(v.CentroidLat) / 90.0, 4)
                        }).ToList(),
                    bodiesListed = Math.Min(limit, sizes.Count),
                    biomes = biomes.OrderByDescending(kv => kv.Value)
                        .ToDictionary(kv => kv.Key, kv => kv.Value),
                    // Which world this measurement is ABOUT. A number with no
                    // provenance is how a quicktest census became a verdict on
                    // a campaign.
                    previewOnly = previewing,
                    seedString = info?.seedString,
                    planetCoverage = info?.planetCoverage ?? -1f,
                    overallRainfall = info?.overallRainfall.ToString(),
                    overallTemperature = info?.overallTemperature.ToString()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---- jawa/world_tile_export -----------------------------------------
        // WHY THIS EXISTS. A savegame can be edited offline -- the world's tile
        // records are plain XML in the .rws -- but that editing is BLIND,
        // because the save stores tiles as a flat list in index order and
        // stores no coordinate for any of them. Latitude and longitude are
        // DERIVED at load time from the geodesic subdivision (PlanetLayer
        // rebuilds the mesh, GetTileCenter -> LongLatOf), so "make the band
        // between 20N and 35N drier" is unanswerable from the file alone. Tile
        // 41,207 is a number, not a place.
        //
        // This is the missing key. Run it once against the live world and every
        // subsequent offline edit becomes geographic: join on tile index and
        // the save's anonymous rows acquire coordinates, biome and climate.
        //
        // 🔴 THE TABLE IS WRITTEN TO A FILE AND DELIBERATELY NOT RETURNED. A
        // full-coverage planet is ~119,904 surface tiles; nine columns of that
        // is several MB of JSON, and the bridge would have to carry all of it
        // into a context window to be thrown away. The result here is a
        // SUMMARY -- count, path, bytes, lat/long extents -- and the data is on
        // disk where the Python side already reads.
        //
        // Names read from Assembly-CSharp with ilprobe, not recalled:
        //   WorldGrid.get_TilesCount -> surface.TilesCount   (IL: ldfld surface)
        //   WorldGrid.get_Item(int)  -> surface[i]           (IL: ldfld surface)
        //     ⇒ the int-indexed grid IS the surface layer. 1.6/Odyssey adds
        //       orbit and other PlanetLayers, but they are reached through
        //       grid.PlanetLayers or a PlanetTile carrying a layerId, never
        //       through grid[int]. So iterating 0..TilesCount is already
        //       surface-only and needs no filter -- which is worth stating,
        //       because it looks like an omission.
        //   WorldGrid.LongLatOf(PlanetTile) -> Vector2(longitude, latitude)
        //   PlanetTile.op_Implicit(int) -> new PlanetTile(id) with layerId 0
        //   Tile.elevation / .temperature / .rainfall / .hilliness /
        //     .swampiness / .PrimaryBiome
        [Tool(
            "jawa/world_tile_export",
            Description =
                "Dump a per-tile table of the whole SURFACE layer to a file — index, " +
                "latitude, longitude, biome, elevation, temperature, rainfall, hilliness, " +
                "swampiness and pollution. Those are EXACTLY the fields a tile write can " +
                "set, so the default export round-trips losslessly through " +
                "world_tile_import with no flag to remember. This is the key that makes " +
                "OFFLINE savegame world editing " +
                "geographic: the .rws stores tiles in index order with no coordinates, " +
                "because lat/long are derived from the geodesic subdivision at load time " +
                "and never serialised. Export once, join on tile index, and every row in " +
                "the save has a place. Read-only: it touches nothing and is safe on a " +
                "campaign world. Works at the world-creation screen with no map loaded.",
            ResultDescription =
                "A SUMMARY ONLY — the table itself is on disk, never in the response, " +
                "because a full-coverage planet is ~119,904 rows. Returns tilesTotal, the " +
                "absolute path written, bytesWritten, the min/max latitude and longitude " +
                "actually observed, the column list, and the world's seedString and " +
                "planetCoverage so the file can be tied back to the world that produced " +
                "it. ⚠️ Tile indices are only meaningful against the world of that seed AND " +
                "that coverage — a table from another world is not merely stale, it is " +
                "wrong tile-for-tile.")]
        public static async Task<object> WorldTileExport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Output file. Omit for the default, which is the game's save-data " +
                "DefDump folder — the same folder RimDefDump writes to and refresh.py " +
                "already reads — under a name carrying the world seed, e.g. " +
                "'world_tiles_<seed>.csv'. A bare filename is resolved into that same " +
                "folder; an absolute path is used as given, and its directory is created " +
                "if missing.",
                DefaultValue = null)]
            string path = null,
            [ToolParameter(Description =
                "'csv' (default) — one header row then one row per tile, the form a " +
                "spreadsheet or pandas reads without argument. 'json' — an object with a " +
                "provenance block, a `columns` list and a `rows` array of arrays; chosen " +
                "over an array-of-objects because repeating nine key names 119,904 times " +
                "roughly triples the file for nothing.",
                DefaultValue = "csv")]
            string format = "csv",
            [ToolParameter(Description =
                "false (default) — the ten writable columns, and nothing that costs " +
                "time to compute. true — append ten DERIVED columns that " +
                "no raw tile field carries: tempMin, tempMax and seasonalShift (the " +
                "engine's own seasonal extremes, not the mean), riverDist, " +
                "feature and featureId (the named world region the tile belongs to), " +
                "waterCovered, roadCount, riverCount and mutatorCount. " +
                "⚠️ COSTS REAL TIME: each tile's min and max each sample the seasonal " +
                "curve 133 times, so a full-coverage planet is roughly 32 million " +
                "evaluations and the main thread is held for all of it. Ask for it when " +
                "you want it, not by default.",
                DefaultValue = false)]
            bool extended = false)
        {
            var fmt = (format ?? "csv").Trim().ToLowerInvariant();
            if (fmt != "csv" && fmt != "json")
                return Fail($"format must be 'csv' or 'json', got '{format}'.");
            // ⛔ REFUSED rather than half-done. The JSON writer emits its own `columns`
            // list and its rows are positional arrays; extending one without the other
            // would produce a file whose header says nine and whose rows carry twenty,
            // which parses cleanly and is wrong. CSV is the form the Python side reads,
            // so that is the form that got the columns. Say so instead of silently
            // dropping them.
            if (extended && fmt == "json")
                return Fail("extended=true is CSV only. The JSON writer emits positional " +
                            "rows against its own column list, and extending one without " +
                            "the other would yield a file that parses and lies. Use " +
                            "format='csv', or ask for the JSON writer to be extended.");

            // PHASE 1 — read the grid, on the main thread and nowhere else.
            // Only the READ is in here. Formatting 119,904 rows and pushing them
            // at a disk is the expensive half, it touches no game state, and
            // doing it inside InvokeAsync would stall the simulation and the
            // renderer for the whole write. So the tiles come out as a plain
            // array of value structs and the main thread is released.
            var gathered = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                // Same fallback as jawa/world_stats, for the same reason: the
                // moment a world is worth exporting is often the world-creation
                // screen, before any commit, while Find.World is still null.
                // WorldGenerator.GenerateWorld sets Current.CreatingWorld and
                // reads the grid back through Find during generation, so a
                // world being previewed is readable here.
                var world = Find.World ?? Current.CreatingWorld;
                if (world == null)
                    return Fail("No world. This reads the PLANET, so it needs a world " +
                                "either loaded or being created — the main menu alone is " +
                                "not enough. Open the world-creation screen and generate " +
                                "one, then call again.");
                var grid = world.grid;
                if (grid == null) return Fail("World has no grid.");

                var n = grid.TilesCount;
                if (n <= 0) return Fail($"World grid reports {n} tiles.");

                var rows = new TileRow[n];
                for (var i = 0; i < n; i++)
                {
                    if ((i & 1023) == 0) cancellationToken.ThrowIfCancellationRequested();
                    var t = grid[i];
                    // A null tile is emitted as a row rather than skipped. The
                    // whole value of this file is that its row N is the save's
                    // tile N; a gap would silently shift every row after it.
                    if (t == null)
                    {
                        rows[i] = new TileRow { Biome = "(null)" };
                        continue;
                    }
                    // Vector2 is (x = longitude, y = latitude). Named on the way
                    // out because the order is the reverse of how it is spoken.
                    var ll = grid.LongLatOf(i);
                    rows[i] = new TileRow
                    {
                        Longitude = ll.x,
                        Latitude = ll.y,
                        Biome = t.PrimaryBiome?.defName ?? "(null)",
                        Elevation = t.elevation,
                        Temperature = t.temperature,
                        Rainfall = t.rainfall,
                        Hilliness = t.hilliness.ToString(),
                        Swampiness = t.swampiness
                    };

                    // 🔴 POLLUTION IS BASE, NOT EXTENDED - corrected 2026-08-24.
                    // It is a RAW writable field and jawa/world_tile_import accepts a
                    // `pollution` column, so omitting it from the default export made the
                    // export -> import round trip LOSSY AND SILENT: a world with 539
                    // poisoned tiles exported and re-imported clean, with no error and no
                    // warning, because the reader simply never saw the column. That is the
                    // exact failure class this companion exists to prevent.
                    // It costs one cast and one field read - unlike the extended block
                    // below, whose tempMin/tempMax sample the seasonal curve 133 times each.
                    var sfc = t as RimWorld.Planet.SurfaceTile;
                    if (sfc != null) rows[i].Pollution = sfc.pollution;

                    if (!extended) continue;

                    // 🔴 GenTemperature.MinTemperatureAtTile, NOT Tile.MinTemperature.
                    // The property caches into cachedMinTemp and NOTHING in the codebase
                    // resets it, so after any climate write it reports the value from
                    // before the write for the rest of the session — a validator built on
                    // it would confirm its own edits while the planet stayed wrong. The
                    // free function recomputes, and recomputing is the entire reason this
                    // column is worth having. Same rule as TileRaw in the World tools.
                    rows[i].TempMin = GenTemperature.MinTemperatureAtTile(i);
                    rows[i].TempMax = GenTemperature.MaxTemperatureAtTile(i);
                    rows[i].SeasonalShift = GenTemperature.SeasonalShiftAmplitudeAt(i);

                    // The remaining fields live on SurfaceTile rather than Tile. grid[int]
                    // IS the surface layer (see the header note), so this cast succeeds for
                    // every row — but it is checked rather than assumed, because a failed
                    // cast here would be eleven silently-zero columns, not an error.
                    // Fully qualified rather than adding `using RimWorld.Planet;` to a
                    // 6,000-line file that already has Verse and RimWorld in scope —
                    // that namespace carries Tile, World and Settlement, and a new
                    // ambiguity here would surface as errors far from this line.
                    var st = t as RimWorld.Planet.SurfaceTile;
                    if (st == null) continue;
                    rows[i].RiverDist = st.riverDist;
                    rows[i].Feature = st.feature?.name;
                    rows[i].FeatureId = st.feature != null ? st.feature.uniqueID : -1;
                    rows[i].WaterCovered = st.WaterCovered;
                    rows[i].RoadCount = st.potentialRoads != null ? st.potentialRoads.Count : 0;
                    rows[i].RiverCount = st.potentialRivers != null ? st.potentialRivers.Count : 0;
                    rows[i].MutatorCount = st.mutatorsNullable != null ? st.mutatorsNullable.Count : 0;
                }

                var info = world.info;
                return new TileHarvest
                {
                    Rows = rows,
                    Extended = extended,
                    Previewing = Find.World == null,
                    SeedString = info?.seedString,
                    PlanetCoverage = info?.planetCoverage ?? -1f
                };
            }, cancellationToken).ConfigureAwait(false);

            // Fail() passes straight through: it is the only other thing phase 1
            // can return, and re-wrapping it would lose its message.
            if (!(gathered is TileHarvest harvest)) return gathered;

            // PHASE 2 — resolve the path, format, write. No game state below.
            var root = Path.Combine(GenFilePaths.SaveDataFolderPath, "DefDump");
            string outPath;
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                {
                    // The seed rides in the FILENAME rather than in a comment
                    // line, because a `#` header would break every naive CSV
                    // reader and the provenance is the one thing that must not
                    // be strippable. A table joined against the wrong world is
                    // wrong tile-for-tile and looks perfectly plausible.
                    var seed = SanitiseForFileName(harvest.SeedString);
                    outPath = Path.Combine(root, $"world_tiles_{seed}.{fmt}");
                }
                else
                {
                    outPath = Path.IsPathRooted(path) ? path : Path.Combine(root, path);
                }
                var dir = Path.GetDirectoryName(outPath);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            }
            catch (Exception ex)
            {
                return Fail($"Could not resolve output path: {ex.Message}",
                            new { path, root });
            }

            var latMin = double.MaxValue;
            var latMax = double.MinValue;
            var lonMin = double.MaxValue;
            var lonMax = double.MinValue;
            foreach (var r in harvest.Rows)
            {
                if (r.Latitude < latMin) latMin = r.Latitude;
                if (r.Latitude > latMax) latMax = r.Latitude;
                if (r.Longitude < lonMin) lonMin = r.Longitude;
                if (r.Longitude > lonMax) lonMax = r.Longitude;
            }

            try
            {
                // No BOM and a generous buffer, matching RimDefDump's writer:
                // the Python side reads these with plain utf-8, and this file is
                // in the same size class as the def dumps.
                using (var sw = new StreamWriter(outPath, false, new UTF8Encoding(false), 1 << 20))
                {
                    if (fmt == "csv") WriteTileCsv(sw, harvest, cancellationToken);
                    else WriteTileJson(sw, harvest, cancellationToken);
                }
            }
            catch (Exception ex)
            {
                return Fail($"Write failed: {ex.Message}", new { path = outPath });
            }

            long bytes;
            try { bytes = new FileInfo(outPath).Length; }
            catch { bytes = -1; }

            return new
            {
                success = true,
                message =
                    $"Wrote {harvest.Rows.Length} surface tiles ({fmt}) to {outPath}" +
                    (harvest.Previewing
                        ? " — from a world being PREVIEWED at the creation screen, not a "
                          + "loaded one. Tile indices hold only if this world is the one kept."
                        : "."),
                tilesTotal = harvest.Rows.Length,
                path = outPath,
                bytesWritten = bytes,
                format = fmt,
                columns = harvest.Extended ? TileColumnsExtended : TileColumns,
                latMin = Math.Round(latMin, 4),
                latMax = Math.Round(latMax, 4),
                longMin = Math.Round(lonMin, 4),
                longMax = Math.Round(lonMax, 4),
                // Which world this table is ABOUT. Tile indices are derived from
                // the subdivision, so seed AND coverage together are what make
                // them mean anything.
                previewOnly = harvest.Previewing,
                seedString = harvest.SeedString,
                planetCoverage = harvest.PlanetCoverage
            };
        }

        // ---- jawa/get_defs ---------------------------------------------------
        // WHY THIS EXISTS, and it is a pattern not an itch.
        // On 2026-08-13/14 FIVE separate v1 gates turned out to have no
        // collectable evidence, every one for the same reason: `jawa/get_def`
        // built its rich `extra` block for ThingDef only, so every other def
        // type came back as label + description. Row 4's dune seas needed
        // BiomeDef.terrainPatchMakers; row 5 needed a xenotype; the Cherry
        // Picker audit needed PawnKindDef.combatPower and ThingDef.tradeability.
        // Each was fixed by adding another hardcoded branch -- which fixes one
        // gate and leaves the next one to be discovered at live prices.
        //
        // This ends that. Name the fields you want off ANY def type and they are
        // read reflectively. A future gate needs no deploy, and a deploy is the
        // one thing that cannot be done while the game is running.
        //
        // It is also a BATCH: reading the 22 Cherry Picker keys was 22 round
        // trips, and a round trip on this stack is not free.
        [Tool(
            "jawa/get_defs",
            Description =
                "Read MANY defs of ANY types in one call, and pull named fields off them " +
                "reflectively. Supersedes calling jawa/get_def in a loop. Two reasons it " +
                "exists: a batch audit (say, confirming a mod-removal list) is one call " +
                "instead of twenty-two, and — more importantly — `fields` means a new " +
                "question can be answered WITHOUT a new companion build. That matters " +
                "because a companion can only be deployed while the game is CLOSED, so a " +
                "missing field otherwise costs a whole restart cycle to add.",
            ResultDescription =
                "Per requested def: found, defName, defType, label, modName, and a `fields` " +
                "map. ⚠️ A field you ASKED FOR that does not exist on that type comes back " +
                "as '(no such field)', never as null — a typo must not be indistinguishable " +
                "from a genuinely null value. Scalars, strings, enums, Defs (rendered as " +
                "defName) and lists of those are returned; anything else is skipped rather " +
                "than half-serialised. `notFound` lists the defs that did not resolve at all.")]
        public static async Task<object> GetDefs(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Semicolon-separated `DefType/defName` pairs, e.g. " +
                "'ThingDef/GravForge;RecipeDef/Make_GravcoreGF;PawnKindDef/Ghoul'. " +
                "⚠️ Give the TYPE: names collide across types — GravForge is both a " +
                "ThingDef and a ResearchProjectDef, and both WarpedObelisk_* names are a " +
                "ThingDef AND an IncidentDef. A bare name would answer about one of them " +
                "and you would not know which.")]
            string defs,
            [ToolParameter(Description =
                "Comma-separated field names to read off each def, e.g. " +
                "'combatPower,tradeability,thingCategories'. Empty returns every public " +
                "scalar field on the def, which is verbose but is how you find out what " +
                "is there.")]
            string fields = null,
            [ToolParameter(Description = "Cap on how many defs to resolve.",
                DefaultValue = 200)]
            int limit = 200)
        {
            if (string.IsNullOrWhiteSpace(defs))
                return Fail("defs is required: 'DefType/defName' pairs separated by ';'.",
                    new { example = "ThingDef/Steel;PawnKindDef/Ghoul" });

            var want = new HashSet<string>((fields ?? "")
                .Split(',').Select(q => q.Trim()).Where(q => q.Length > 0));

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var rows = new List<object>();
                var notFound = new List<string>();
                var malformed = new List<string>();
                var found = 0;

                foreach (var raw in defs.Split(';').Select(q => q.Trim())
                                        .Where(q => q.Length > 0).Take(limit))
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var slash = raw.IndexOf('/');
                    if (slash <= 0 || slash == raw.Length - 1)
                    {
                        // Named loudly rather than skipped. Cherry Picker's own
                        // ToDefName is `key.Split('/')[1]` with no bounds check
                        // OUTSIDE its catch, so one key missing its slash aborts
                        // every removal after it. Silence about a malformed entry
                        // is how that class of bug survives.
                        malformed.Add(raw);
                        continue;
                    }
                    var typeName = raw.Substring(0, slash).Trim();
                    var defName = raw.Substring(slash + 1).Trim();

                    var dbType = GenTypes.GetTypeInAnyAssembly(typeName)
                              ?? GenTypes.GetTypeInAnyAssembly("RimWorld." + typeName)
                              ?? GenTypes.GetTypeInAnyAssembly("Verse." + typeName);
                    if (dbType == null)
                    {
                        rows.Add(new
                        {
                            requested = raw, found = false, defType = typeName,
                            defName,
                            error = $"No def TYPE named '{typeName}'."
                        });
                        notFound.Add(raw);
                        continue;
                    }

                    var db = typeof(DefDatabase<>).MakeGenericType(dbType);
                    var get = db.GetMethod("GetNamedSilentFail",
                        System.Reflection.BindingFlags.Public
                        | System.Reflection.BindingFlags.Static);
                    var def = get?.Invoke(null, new object[] { defName }) as Def;

                    if (def == null)
                    {
                        rows.Add(new
                        {
                            requested = raw, found = false, defType = typeName, defName
                        });
                        notFound.Add(raw);
                        continue;
                    }

                    found++;
                    rows.Add(new
                    {
                        requested = raw,
                        found = true,
                        defName = def.defName,
                        defType = def.GetType().Name,
                        label = def.label,
                        modName = def.modContentPack?.Name,
                        packageId = def.modContentPack?.PackageId,
                        fields = Scalars(def, want)
                    });
                }

                return new
                {
                    // ⚠️ success means the CALL resolved cleanly, NOT that every
                    // def was found. An audit whose whole point is finding
                    // absences must not report failure for finding them.
                    success = malformed.Count == 0,
                    message =
                        $"{found} of {rows.Count} def(s) resolved" +
                        (notFound.Count > 0 ? $"; {notFound.Count} not found" : "") +
                        (malformed.Count > 0
                            ? $". ⚠️ {malformed.Count} entry/entries had no '/' and were "
                              + "SKIPPED: " + string.Join(", ", malformed)
                            : ""),
                    requested = rows.Count,
                    foundCount = found,
                    notFound,
                    malformed,
                    fieldsAsked = want.ToList(),
                    defs = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---------------------------------------------------------------------
        // jawa/fire_quest — offer an authored quest without the float menu.
        //
        // WHY. v1 row 3 (The Claim) was filed UNCOLLECTABLE because the only
        // route to it is reading an in-world item, which needs a right-click
        // float menu, and `rimworld/right_click_cell` is measured broken. That
        // made a BUILT and DEPLOYED quest wait for the owner at the keyboard.
        //
        // The engine route, read out of Assembly-CSharp with ilprobe rather than
        // recalled — QuestUtility::GenerateQuestAndMakeAvailable(QuestScriptDef,
        // float) is public static, and its IL is exactly
        //   QuestGen::Generate -> Find::get_QuestManager -> QuestManager::Add
        // so it REGISTERS the quest, it does not merely build one. That mattered
        // enough to check: "made available" is the load-bearing half of the name.
        //
        // 🔴 The return value is NOT the evidence. `Add` returns void and the
        // Quest comes back regardless, which is the silent-success shape this
        // bridge keeps getting bitten by. So every field below is read back off
        // Find.QuestManager AFTER the call, and `success` means "found in the
        // manager", never "the method returned".
        // ---------------------------------------------------------------------
        [Tool(
            "jawa/fire_quest",
            Description =
                "Generate an authored quest and make it available, bypassing the item/float-menu " +
                "route entirely. Takes a QuestScriptDef defName plus threat points. Optionally " +
                "accepts it too, which is what turns an offer into a site on the world map. " +
                "Use dryRun to resolve and cost the quest without creating it.",
            ResultDescription =
                "Returns the quest id, name and State READ BACK from the QuestManager after the " +
                "call — not what the generator returned. success means the quest is in the " +
                "manager; a generator that silently produced nothing reports false.")]
        public static async Task<object> FireQuest(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "QuestScriptDef defName, e.g. Jawa_TheClaim, OpportunitySite_ItemStash.")]
            string questDef,
            [ToolParameter(Description =
                "Threat/reward points. Omit or <=0 for the storyteller's current default.",
                DefaultValue = 0.0)]
            float points = 0f,
            [ToolParameter(Description =
                "Also accept the quest, so it becomes Ongoing and spawns its world objects. " +
                "Without this it sits as a NotYetAccepted offer.",
                DefaultValue = false)]
            bool accept = false,
            [ToolParameter(Description =
                "Resolve the def and report the points that WOULD be used, and create nothing.",
                DefaultValue = false)]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(questDef)) return Fail("questDef is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.CurrentMap == null) return Fail("No current map. Load a game first.");

                var manager = Find.QuestManager;
                if (manager == null) return Fail("No QuestManager — is a game actually loaded?");

                var qdef = DefDatabase<QuestScriptDef>.GetNamedSilentFail(questDef);
                if (qdef == null)
                    return Fail($"No QuestScriptDef named '{questDef}'.", new
                    {
                        suggestions = DefDatabase<QuestScriptDef>.AllDefsListForReading
                            .Where(d => d.defName.ToLowerInvariant()
                                         .Contains(questDef.ToLowerInvariant()))
                            .Select(d => d.defName).Take(12).ToList()
                    });

                // Storyteller default when the caller did not name a number. Quest
                // points come off the same threat curve as an incident's.
                var usePoints = points > 0f
                    ? points
                    : StorytellerUtility.DefaultThreatPointsNow(Find.CurrentMap);

                if (dryRun)
                    return new
                    {
                        success = true,
                        message = $"{qdef.defName} resolved; would generate at {usePoints:0} points "
                                + "(dry run, nothing created).",
                        quest = qdef.defName,
                        pointsWouldUse = usePoints,
                        rootMinPoints = qdef.rootMinPoints,
                        rootSelectionWeight = qdef.rootSelectionWeight,
                        created = false,
                        ticksGame = TicksGameSafe()
                    };

                // Snapshot the ids present BEFORE, so the new quest is identified by
                // difference rather than by trusting the returned reference.
                var before = new HashSet<int>(
                    manager.QuestsListForReading.Select(q => q.id));

                Quest made;
                try
                {
                    made = QuestUtility.GenerateQuestAndMakeAvailable(qdef, usePoints);
                }
                catch (Exception e)
                {
                    // A quest script that cannot resolve its own nodes throws from
                    // deep inside QuestGen. That is a real, reportable answer about
                    // the DEF, not a bridge fault — surface it whole.
                    return Fail($"{qdef.defName} threw during generation: {e.GetType().Name}: {e.Message}");
                }

                // THE READ-BACK. Everything below comes off the manager.
                var landed = manager.QuestsListForReading
                    .FirstOrDefault(q => made != null ? q.id == made.id : !before.Contains(q.id));

                if (landed == null)
                    return Fail(
                        $"{qdef.defName} generated but is NOT in the QuestManager. "
                        + "The generator returned "
                        + (made == null ? "null" : $"quest {made.id}")
                        + " — treat this as a failed quest script, not a bridge error.");

                var accepted = false;
                string acceptNote = null;
                if (accept)
                {
                    // Accept() takes the accepting pawn; a quest that requires one and
                    // gets null throws rather than refusing, so pick a colonist first.
                    var by = Find.CurrentMap.mapPawns?.FreeColonists?.FirstOrDefault();
                    if (landed.RequiresAccepter && by == null)
                        acceptNote = "not accepted: the quest requires an accepter and the map has no free colonist.";
                    else
                    {
                        try { landed.Accept(by); accepted = landed.State == QuestState.Ongoing; }
                        catch (Exception e) { acceptNote = $"accept threw: {e.GetType().Name}: {e.Message}"; }
                    }
                }

                return new
                {
                    // Found in the manager is the whole claim. Acceptance is reported
                    // separately so a half-success cannot read as a whole one.
                    success = true,
                    message =
                        $"{qdef.defName} available as quest {landed.id} \"{landed.name}\" "
                        + $"at {usePoints:0} points, State={landed.State}"
                        + (accept ? (accepted ? ", accepted." : $". ⚠️ {acceptNote ?? "accept did not reach Ongoing."}")
                                  : "."),
                    quest = qdef.defName,
                    questId = landed.id,
                    questName = landed.name,
                    state = landed.State.ToString(),
                    accepted,
                    acceptNote,
                    hidden = landed.hidden,
                    challengeRating = landed.challengeRating,
                    ticksUntilExpiry = landed.TicksUntilExpiry,
                    points = usePoints,
                    questCountAfter = manager.QuestsListForReading.Count,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

#if JAWA_GM_TOOLS
        // ---- THE GM PAIR -----------------------------------------------------
        // Compiled OUT unless the build defines JAWA_GM_TOOLS (build.py --gm).
        // Every other tool on this bridge changes only what the caller named.
        // These two let the world act on the player, so they ship only on an
        // explicit ruling. Rationale in the csproj; state in a retired seat's state file.
        [Tool(
            "jawa/fire_incident",
            Description =
                "Fire a storyteller incident — a raid, a trader, a solar flare, an infestation. " +
                "This is the GM half of the primitive set: everything else on this bridge " +
                "changes something the caller named, whereas an incident makes the WORLD act " +
                "on the player. Use dryRun to ask whether it CAN fire without firing it.",
            ResultDescription =
                "Returns whether it fired, the points used, and CanFireNow — which is the " +
                "honest answer to 'why did nothing happen'.")]
        public static async Task<object> FireIncident(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "IncidentDef defName, e.g. RaidEnemy, TraderCaravanArrival.")]
            string incidentDef,
            [ToolParameter(Description =
                "Threat points. Omit or <=0 for the storyteller's current default.",
                DefaultValue = 0.0)]
            float points = 0f,
            [ToolParameter(Description =
                "Optional faction defName for incidents that take one (raids).",
                DefaultValue = null)]
            string faction = null,
            [ToolParameter(Description =
                "Ask whether it can fire, and do NOT fire it.", DefaultValue = false)]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(incidentDef)) return Fail("incidentDef is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var idef = DefDatabase<IncidentDef>.GetNamedSilentFail(incidentDef);
                if (idef == null)
                    return Fail($"No IncidentDef named '{incidentDef}'.", new
                    {
                        suggestions = DefDatabase<IncidentDef>.AllDefsListForReading
                            .Where(d => d.defName.ToLowerInvariant().Contains(incidentDef.ToLowerInvariant()))
                            .Select(d => d.defName).Take(12).ToList()
                    });

                var parms = StorytellerUtility.DefaultParmsNow(idef.category, map);
                if (points > 0f) parms.points = points;
                if (!string.IsNullOrWhiteSpace(faction))
                {
                    var fac = Find.FactionManager.AllFactions.FirstOrDefault(
                        q => string.Equals(q.def?.defName, faction, StringComparison.OrdinalIgnoreCase));
                    if (fac == null) return Fail($"No faction '{faction}'.");
                    parms.faction = fac;
                }

                var canFire = idef.Worker.CanFireNow(parms);
                var fired = false;
                if (!dryRun) fired = idef.Worker.TryExecute(parms);

                return new
                {
                    // Loud: an incident that could not fire is NOT a success.
                    success = dryRun ? canFire : fired,
                    message = dryRun
                        ? $"{idef.defName} canFireNow={canFire} (dry run, nothing fired)."
                        : (fired ? $"{idef.defName} fired with {parms.points:0} points."
                                 : $"{idef.defName} did NOT fire. canFireNow={canFire}."),
                    incident = idef.defName,
                    category = idef.category?.defName,
                    canFireNow = canFire,
                    fired,
                    points = parms.points,
                    faction = parms.faction?.def?.defName,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/send_letter",
            Description =
                "Send a letter to the player — the notification pane, with an optional " +
                "camera jump target. The other half of GM authoring: an incident makes " +
                "something happen, a letter is how the player is TOLD. Also the only way " +
                "for an agent to narrate into the game rather than into a chat window.",
            ResultDescription = "Returns the letter label and def used.")]
        public static async Task<object> SendLetter(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Letter title.")] string label,
            [ToolParameter(Description = "Letter body text.")] string text,
            [ToolParameter(Description =
                "LetterDef: NeutralEvent (default), PositiveEvent, NegativeEvent, ThreatBig, ThreatSmall.",
                DefaultValue = "NeutralEvent")]
            string letterDef = "NeutralEvent",
            [ToolParameter(Description = "Optional look-target cell X.", DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description = "Optional look-target cell Z.", DefaultValue = -1)]
            int z = -1)
        {
            if (string.IsNullOrWhiteSpace(label)) return Fail("label is required.");
            if (string.IsNullOrWhiteSpace(text)) return Fail("text is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                var ldef = DefDatabase<LetterDef>.GetNamedSilentFail(letterDef)
                           ?? LetterDefOf.NeutralEvent;

                if (map != null && x >= 0 && z >= 0)
                {
                    var cell = new IntVec3(x, 0, z);
                    Find.LetterStack.ReceiveLetter(label, text, ldef, new LookTargets(cell, map));
                }
                else
                {
                    Find.LetterStack.ReceiveLetter(label, text, ldef);
                }

                return new
                {
                    success = true,
                    message = $"Letter '{label}' sent as {ldef.defName}.",
                    label,
                    letterDef = ldef.defName,
                    hasLookTarget = map != null && x >= 0 && z >= 0,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }
#endif // JAWA_GM_TOOLS

        [Tool(
            "jawa/set_roof_batch",
            Description =
                "Set or REMOVE the roof over many rects in one call. The bridge has no roof " +
                "capability at all -- rimworld/list_areas exposes the roof AREA (the " +
                "build-roof designation zone), which is a different thing from map.roofGrid, " +
                "and RimWorld's own roof tools are drag tools the bridge cannot drive. " +
                "Roofs are not cosmetic: a cavern without RoofRockThick is an open pit, and " +
                "roofs govern light, temperature, weather and whether drop pods can land. " +
                "ops format: 'RoofDef:x,z,w,h' separated by ';'. Use the literal roof name " +
                "'None' (or 'Clear') to REMOVE a roof. Vanilla defs: RoofConstructed, " +
                "RoofRockThin, RoofRockThick.",
            ResultDescription =
                "Returns cellsChanged, cellsFailedVerify (every cell is read back off the " +
                "grid after writing), per-def totals, and the reason each refusal happened.")]
        public static async Task<object> SetRoofBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Roof ops: 'RoofDef:x,z,w,h' separated by ';' or newlines. w/h optional " +
                "(default 1). 'None' or 'Clear' removes the roof.")]
            string ops,
            [ToolParameter(Description =
                "Default RoofDef for ops that do not name one. Optional.",
                DefaultValue = null)]
            string roofDef = null,
            [ToolParameter(Description =
                "Redraw the affected sections. Pass false for many calls, then use " +
                "jawa/refresh_rect once.", DefaultValue = true)]
            bool refresh = true)
        {
            if (string.IsNullOrWhiteSpace(ops))
                return Fail("ops is required, e.g. 'RoofRockThick:10,20,5,5'.");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(ops, roofDef ?? "None", out parsed, parseErrors))
                return Fail("Could not parse ops.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many ops: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var grid = map.roofGrid;
                if (grid == null) return Fail("Map has no roofGrid.");
                var size = map.Size;

                // Resolve every named def ONCE, before touching the grid. A typo
                // halfway through a 2,000-cell paint would otherwise leave the map
                // half-written with no way to know where it stopped.
                var resolved = new Dictionary<string, RoofDef>(StringComparer.OrdinalIgnoreCase);
                var unknown = new List<string>();
                foreach (var op in parsed)
                {
                    var name = op.Terrain;
                    if (resolved.ContainsKey(name)) continue;
                    if (IsClearRoofToken(name)) { resolved[name] = null; continue; }
                    var def = DefDatabase<RoofDef>.GetNamedSilentFail(name);
                    if (def == null) unknown.Add(name);
                    else resolved[name] = def;
                }
                if (unknown.Count > 0)
                    return Fail(
                        "Unknown RoofDef(s): " + string.Join(", ", unknown.ToArray()) +
                        ". Vanilla is RoofConstructed / RoofRockThin / RoofRockThick, " +
                        "or 'None' to remove.",
                        new { knownRoofDefs = AllRoofDefNames() });

                var perDef = new Dictionary<string, int>();
                var errors = new List<object>();
                int changed = 0, failedVerify = 0, outOfBounds = 0;
                var dirty = new HashSet<IntVec3>();

                foreach (var op in parsed)
                {
                    var want = resolved[op.Terrain];
                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            var c = new IntVec3(op.X + dx, 0, op.Z + dz);
                            if (c.x < 0 || c.z < 0 || c.x >= size.x || c.z >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }

                            var before = grid.RoofAt(c);
                            if (before == want) continue;   // no-op, and no redraw owed

                            grid.SetRoof(c, want);

                            // Read it back. Same discipline as the terrain path:
                            // the tool having run is not the grid having changed.
                            var after = grid.RoofAt(c);
                            if (after != want)
                            {
                                failedVerify++;
                                if (errors.Count < 20)
                                    errors.Add(new
                                    {
                                        x = c.x,
                                        z = c.z,
                                        wanted = want?.defName ?? "None",
                                        got = after?.defName ?? "None",
                                    });
                                continue;
                            }

                            changed++;
                            dirty.Add(c);
                            var key = want?.defName ?? "None";
                            perDef.TryGetValue(key, out var n);
                            perDef[key] = n + 1;
                        }
                    }
                }

                if (refresh && dirty.Count > 0)
                {
                    foreach (var op in parsed)
                        RefreshRect(map, op.X, op.Z, op.W, op.H);
                }

                return new
                {
                    success = failedVerify == 0,
                    message = $"Roofed {changed} cell(s) across {parsed.Count} op(s)" +
                              (failedVerify > 0 ? $", {failedVerify} FAILED VERIFY." : "."),
                    opsRequested = parsed.Count,
                    cellsChanged = changed,
                    cellsFailedVerify = failedVerify,
                    cellsOutOfBounds = outOfBounds,
                    perDef,
                    errors,
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/get_roof_batch",
            Description =
                "Read the roof of MANY cells in one call, answering in the SAME ops grammar " +
                "jawa/set_roof_batch accepts -- so a capture replays straight back as a " +
                "restore, with no translation step. Unroofed cells come back as 'None', " +
                "which set_roof_batch understands, so an exact revert includes removing " +
                "roofs that were not there before. rects format: 'x,z,w,h' separated by ';'.",
            ResultDescription =
                "Returns ops (run-length encoded along each row), cellsRead, and the distinct " +
                "roofs found. The ops string is directly replayable.")]
        public static async Task<object> GetRoofBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Rects to read: 'x,z,w,h' separated by ';'. A 'Name:' prefix is ignored, so " +
                "a set_roof_batch payload can be replayed as a read.")]
            string rects)
        {
            if (string.IsNullOrWhiteSpace(rects))
                return Fail("rects is required, e.g. '10,20,3,4'.");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(rects, "_", out parsed, parseErrors))
                return Fail("Could not parse rects.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many rects: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var grid = map.roofGrid;
                if (grid == null) return Fail("Map has no roofGrid.");
                var size = map.Size;

                var found = new Dictionary<IntVec3, string>();
                int outOfBounds = 0;

                foreach (var op in parsed)
                {
                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            var c = new IntVec3(op.X + dx, 0, op.Z + dz);
                            if (c.x < 0 || c.z < 0 || c.x >= size.x || c.z >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }
                            // "None" rather than skipping: an unroofed cell is a
                            // FACT the restore needs. Omitting it would make a
                            // revert silently leave roofs it should have removed.
                            found[c] = grid.RoofAt(c)?.defName ?? "None";
                        }
                    }
                }

                var distinct = new List<string>();
                foreach (var v in found.Values)
                    if (!distinct.Contains(v)) distinct.Add(v);

                return new
                {
                    success = true,
                    message = $"Read {found.Count} cell(s), {distinct.Count} distinct roof(s).",
                    ops = RunLengthEncode(found),
                    cellsRead = found.Count,
                    cellsOutOfBounds = outOfBounds,
                    roofs = distinct,
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // -- helpers ---------------------------------------------------------

        /// <summary>'None' and 'Clear' both mean "remove the roof".
        ///
        /// Two spellings because the ops grammar has no way to express null and
        /// a generator writing "no roof here" will reach for whichever word it
        /// thought of first. Accepting both costs one line; rejecting one of
        /// them costs a round trip to find out which was meant.</summary>
        private static bool IsClearRoofToken(string name) =>
            string.Equals(name, "None", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(name, "Clear", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(name, "null", StringComparison.OrdinalIgnoreCase);

        private static List<string> AllRoofDefNames()
        {
            var names = new List<string> { "None" };
            foreach (var d in DefDatabase<RoofDef>.AllDefsListForReading)
                names.Add(d.defName);
            return names;
        }

        /// <summary>Encode a cell->terrain map as replayable ops, run-length
        /// compressed along x within each row.
        ///
        /// Row-wise runs only, never merging identical rows into taller rects.
        /// A taller-rect pass would shrink the payload further, but rectangle
        /// merging is exactly where an encoder starts dropping or double-covering
        /// cells, and this string's whole job is to restore a live map exactly.
        /// A 1,000-cell capture is a few KB either way.</summary>
        private static string RunLengthEncode(Dictionary<IntVec3, string> cells)
        {
            if (cells.Count == 0) return string.Empty;

            var ordered = cells.Keys.OrderBy(c => c.z).ThenBy(c => c.x).ToList();
            var sb = new System.Text.StringBuilder(cells.Count * 4);

            int runX = ordered[0].x, runZ = ordered[0].z, runW = 1;
            var runTerrain = cells[ordered[0]];

            for (var i = 1; i < ordered.Count; i++)
            {
                var c = ordered[i];
                var t = cells[c];
                if (c.z == runZ && c.x == runX + runW && t == runTerrain)
                {
                    runW++;
                    continue;
                }
                if (sb.Length > 0) sb.Append(';');
                sb.Append(runTerrain).Append(':').Append(runX).Append(',')
                  .Append(runZ).Append(',').Append(runW).Append(",1");
                runX = c.x; runZ = c.z; runW = 1; runTerrain = t;
            }
            if (sb.Length > 0) sb.Append(';');
            sb.Append(runTerrain).Append(':').Append(runX).Append(',')
              .Append(runZ).Append(',').Append(runW).Append(",1");
            return sb.ToString();
        }

        private static int CountRuns(string ops) =>
            string.IsNullOrEmpty(ops) ? 0 : ops.Count(ch => ch == ';') + 1;

        private const int MaxOps = 4096;
        private const int MaxCells = 70000;   // a 250x250 map is 62,500 cells

        private struct ParsedOp
        {
            public string Terrain;
            public int X, Z, W, H;
        }

        /// <summary>Parse 'Terrain:x,z,w,h' ops separated by ';' or newlines.
        ///
        /// A compact string rather than JSON on purpose: the payload is the hot
        /// path for a generator (hundreds of rects per formation), no JSON
        /// library is guaranteed present in the game's assembly set, and every
        /// parse failure here is a whole round trip wasted -- so the format is
        /// small enough to be obviously correct by inspection.</summary>
        private static bool TryParseOps(string ops, string defaultTerrain,
                                        out List<ParsedOp> parsed, List<string> errors)
        {
            parsed = new List<ParsedOp>();
            var tokens = ops.Split(new[] { ';', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);

            for (var i = 0; i < tokens.Length; i++)
            {
                var token = tokens[i].Trim();
                if (token.Length == 0) continue;

                var terrain = defaultTerrain;
                var coordPart = token;

                var colon = token.IndexOf(':');
                if (colon >= 0)
                {
                    terrain = token.Substring(0, colon).Trim();
                    coordPart = token.Substring(colon + 1);
                }

                if (string.IsNullOrWhiteSpace(terrain))
                {
                    if (errors.Count < 10)
                        errors.Add($"op {i} ('{token}') names no terrain and no terrainDef default was given.");
                    continue;
                }

                var nums = coordPart.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                if (nums.Length < 2 || nums.Length > 4)
                {
                    if (errors.Count < 10)
                        errors.Add($"op {i} ('{token}') needs x,z[,w[,h]] -- got {nums.Length} number(s).");
                    continue;
                }

                int x, z, w = 1, h = 1;
                if (!int.TryParse(nums[0].Trim(), out x) || !int.TryParse(nums[1].Trim(), out z)
                    || (nums.Length > 2 && !int.TryParse(nums[2].Trim(), out w))
                    || (nums.Length > 3 && !int.TryParse(nums[3].Trim(), out h)))
                {
                    if (errors.Count < 10)
                        errors.Add($"op {i} ('{token}') has a non-integer coordinate.");
                    continue;
                }

                if (w < 1 || h < 1)
                {
                    if (errors.Count < 10)
                        errors.Add($"op {i} ('{token}') has width/height < 1.");
                    continue;
                }

                parsed.Add(new ParsedOp { Terrain = terrain, X = x, Z = z, W = w, H = h });
            }

            // Partial success is worse than none here: a formation with a
            // silently dropped op paints a hole the caller cannot see.
            return errors.Count == 0 && parsed.Count > 0;
        }

        /// <summary>Exact defName first, then case-insensitive. Terrain defNames
        /// are inconsistently cased across mods ("WaterShallow", "Soil"), and a
        /// generator should not have to guess capitalisation.</summary>
        private static TerrainDef ResolveTerrain(string name)
        {
            var exact = DefDatabase<TerrainDef>.GetNamedSilentFail(name);
            if (exact != null) return exact;

            return DefDatabase<TerrainDef>.AllDefsListForReading
                .FirstOrDefault(d => string.Equals(d.defName, name, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>A wrong defName is the most likely failure, and a bare "not
        /// found" costs a whole round trip to fix. Spend a few ms on hints.</summary>
        private static List<string> SuggestTerrain(string name)
        {
            var needle = (name ?? string.Empty).ToLowerInvariant();
            return DefDatabase<TerrainDef>.AllDefsListForReading
                .Where(d => d.defName.ToLowerInvariant().Contains(needle)
                            || (d.label ?? string.Empty).ToLowerInvariant().Contains(needle))
                .Select(d => d.defName)
                .OrderBy(n => n.Length)
                .Take(15)
                .ToList();
        }

        /// <summary>Mark the affected sections dirty so the change is visible
        /// without a reload. Terrain lives in the map mesh, which is cached per
        /// section, so an unrefreshed cell can be correct in the grid and still
        /// look untouched on screen.</summary>
        private static void RefreshRect(Map map, int x, int z, int width, int height)
        {
            var drawer = map.mapDrawer;
            if (drawer == null) return;

            var size = map.Size;
            // Sections are 17x17; touching one cell per section would be enough,
            // but the corners are what get missed, so walk the border cells.
            for (var dx = 0; dx < width; dx++)
            {
                for (var dz = 0; dz < height; dz++)
                {
                    int cx = x + dx, cz = z + dz;
                    if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z) continue;
                    drawer.MapMeshDirty(new IntVec3(cx, 0, cz), MapMeshFlagDefOf.Terrain);
                }
            }
        }

        // ---------------------------------------------------------- layers
        // RimWorld 1.6 (Odyssey) has THREE terrain grids, not two: top, under,
        // and FOUNDATION. `Substructure` lives in the foundation grid, and it is
        // what every gravship building demands via terrainAffordanceNeeded
        // (GravshipHull, GravFieldExtender, PilotConsole -- 10 defs in
        // Buildings_Gravship.xml). SetUnderTerrain CANNOT place it: underGrid and
        // foundationGrid are different arrays, and savemap.py has always known
        // them apart (`underGridDeflate` vs `foundationGridDeflate`).
        //
        // Signatures verified by COMPILING against Assembly-CSharp, not by
        // reading strings out of it -- TerrainGrid.SetFoundation(IntVec3,
        // TerrainDef) and TerrainGrid.FoundationAt(IntVec3). A strings scan found
        // SetFoundation but no FoundationAt, which would have sent me looking for
        // an indexer that does not exist.
        private static bool IsLayer(string layer, string name) =>
            string.Equals(layer, name, StringComparison.OrdinalIgnoreCase);

        private static bool ValidLayer(string layer) =>
            IsLayer(layer, "top") || IsLayer(layer, "under") || IsLayer(layer, "foundation");

        private static string NormLayer(string layer) =>
            IsLayer(layer, "under") ? "under"
            : IsLayer(layer, "foundation") ? "foundation"
            : "top";

        private static TerrainDef ReadLayer(TerrainGrid grid, IntVec3 cell, string layer) =>
            IsLayer(layer, "under") ? grid.UnderTerrainAt(cell)
            : IsLayer(layer, "foundation") ? grid.FoundationAt(cell)
            : grid.TerrainAt(cell);

        private static void WriteLayer(TerrainGrid grid, IntVec3 cell, TerrainDef def, string layer)
        {
            if (IsLayer(layer, "under")) grid.SetUnderTerrain(cell, def);
            else if (IsLayer(layer, "foundation")) grid.SetFoundation(cell, def);
            else grid.SetTerrain(cell, def);
        }

        // Public instance fields of a CompProperties, filtered to values that are
        // meaningful in JSON. Reflection is the only route: CompProperties
        // subclasses are mod-defined and share no interface.
        // Generalised out of CompScalars, which did exactly this for comps only.
        // ⚠️ Scalars, strings, enums, Defs and LISTS of those. Anything else is
        // skipped rather than truncated -- a half-serialised object is worse
        // than an absent one, because it reads as data.
        private static Dictionary<string, object> Scalars(object o, HashSet<string> want)
        {
            var outp = new Dictionary<string, object>();
            if (o == null) return outp;
            var flags = System.Reflection.BindingFlags.Public
                      | System.Reflection.BindingFlags.Instance;
            foreach (var f in o.GetType().GetFields(flags))
            {
                if (want != null && want.Count > 0 && !want.Contains(f.Name)) continue;
                object v;
                try { v = f.GetValue(o); } catch { continue; }
                if (v == null) { outp[f.Name] = null; continue; }
                if (v is Def d) { outp[f.Name] = d.defName; continue; }
                var t = v.GetType();
                if (t.IsPrimitive || v is string || t.IsEnum || v is decimal)
                {
                    outp[f.Name] = t.IsEnum ? v.ToString() : v;
                    continue;
                }
                if (v is System.Collections.IEnumerable seq && !(v is string))
                {
                    var items = new List<object>();
                    foreach (var it in seq)
                    {
                        if (it == null) { items.Add(null); continue; }
                        if (it is Def id) { items.Add(id.defName); continue; }
                        var it2 = it.GetType();
                        if (it2.IsPrimitive || it is string || it2.IsEnum)
                            items.Add(it2.IsEnum ? it.ToString() : it);
                        else items.Add(it2.Name);
                        if (items.Count >= 64) break;
                    }
                    outp[f.Name] = items;
                }
            }
            // 🔴 A NAMED field that is PRIVATE is still a real field, and used to
            // come back as "(no such field)" -- which reads as "this def has no
            // such thing" and is how a correct, shipped XML patch nearly got
            // reported as a no-op. TraitDef.commonality is the case that found
            // this: `private float commonality = 1f;` (RimWorld/TraitDef.cs), set
            // by the XML loader like any other field, invisible to a Public-only
            // reflection pass. Vanilla `Nimble` answered "(no such field)" too,
            // which is what made the reading look authoritative.
            //
            // Only searched when the caller NAMED the field -- an unfiltered dump
            // stays public-only, because private state is noise unless asked for.
            // GetFields does not return a base type's privates, so walk the chain.
            if (want != null && want.Count > 0)
            {
                var npFlags = System.Reflection.BindingFlags.NonPublic
                            | System.Reflection.BindingFlags.Instance
                            | System.Reflection.BindingFlags.DeclaredOnly;
                foreach (var w in want)
                {
                    if (outp.ContainsKey(w)) continue;
                    for (var ty = o.GetType(); ty != null && ty != typeof(object); ty = ty.BaseType)
                    {
                        var pf = ty.GetField(w, npFlags);
                        if (pf == null) continue;
                        object pv;
                        try { pv = pf.GetValue(o); } catch { break; }
                        if (pv == null) { outp[w] = null; break; }
                        if (pv is Def pd) { outp[w] = pd.defName; break; }
                        var pt = pv.GetType();
                        if (pt.IsPrimitive || pv is string || pt.IsEnum || pv is decimal)
                            outp[w] = pt.IsEnum ? pv.ToString() : pv;
                        else
                            outp[w] = "(non-public field '" + w + "' on " + ty.Name
                                    + "; type " + pt.Name + " not serialised)";
                        break;
                    }
                }
            }

            // A field ASKED FOR and not found must say so, or a typo in the
            // request is indistinguishable from a field that is genuinely null
            // -- the same silent-success shape as a dropped parameter.
            if (want != null)
                foreach (var w in want)
                    if (!outp.ContainsKey(w)) outp[w] = "(no such field)";
            return outp;
        }

        private static Dictionary<string, object> CompScalars(CompProperties c)
        {
            var outp = new Dictionary<string, object>();
            if (c == null) return outp;
            foreach (var f in c.GetType().GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
            {
                object v;
                try { v = f.GetValue(c); } catch { continue; }
                if (v == null) continue;
                if (v is Def d) { outp[f.Name] = d.defName; continue; }
                var t = v.GetType();
                if (t.IsPrimitive || v is string || t.IsEnum || v is decimal)
                    outp[f.Name] = t.IsEnum ? v.ToString() : v;
            }
            return outp;
        }

        private static string Describe(int changed, int already, int oob, int failed,
                                       TerrainDef def, bool under)
        {
            var where = under ? "under-terrain" : "terrain";
            if (oob > 0 && changed == 0 && already == 0)
                return $"Nothing done: all {oob} requested cell(s) are outside the map.";

            var msg = changed == 0 && already > 0
                ? $"No change needed: {already} cell(s) were already {def.defName}."
                : $"Set {where} to {def.defName} on {changed} cell(s).";

            if (changed > 0 && already > 0) msg += $" {already} already correct.";
            if (oob > 0) msg += $" {oob} outside the map, skipped.";
            if (failed > 0) msg += $" WARNING: {failed} cell(s) did not read back as {def.defName}.";
            return msg;
        }

        // -------------------------------------------------------------------
        // jawa/list_factions  --  V1-CRITICAL
        //
        // WHY THIS EXISTS. There is no way to read the faction list over the
        // bridge at all. rimworld/list_colonists is player-only, jawa/list_pawns
        // sees only pawns standing on the CURRENT MAP, and a faction's
        // settlements are WORLD objects that never appear on a map at all. So
        // "did the Rebel Alliance suppression apply?" has only ever been
        // answerable by scrolling a UI list by hand and judging it by eye.
        //
        // That matters beyond convenience: the v1 gate is "every item SEEN
        // in-game once", and a ~25 minute cold load cannot be spent per check,
        // so verification has to ride the bridge.
        //
        // ⚠️ COUNT SETTLEMENTS, NOT VISIBLE TILES. The deciding question for the
        // suppression patch is whether a faction owns any settlement anywhere on
        // the planet. Judging by what is on screen answers a different and much
        // smaller question -- the same visible-subset trap as counting <li> in
        // ModsConfig.xml across the whole file.
        //
        // ⚠️ AN EMPTY RESULT FOR A FACTION IS THE PATCH WORKING, not the patch
        // being unnecessary. The shipped mod XML has requiredCountAtGameStart 1
        // and settlementGenerationWeight 0.3; the zeroes are OUR patch's output.
        // Read a zero here as success, and do not conclude the patch is
        // redundant from a zero alone.
        [Tool(
            "jawa/list_factions",
            Description =
                "List every faction in the current world with its hostility to the player and " +
                "how many SETTLEMENTS it owns on the planet. Nothing else on the bridge can " +
                "answer this: list_colonists is player-only, list_pawns sees only the current " +
                "map, and settlements are world objects that never stand on a map. This is the " +
                "call that decides whether a faction-suppression patch actually applied, " +
                "without scrolling a UI list by hand.",
            ResultDescription =
                "Per faction: defName, name, isPlayer, hostile, goodwill, hidden, " +
                "permanentEnemy and settlementCount. Plus settlementsTotal across the world. " +
                "A faction with settlementCount 0 owns nothing on the planet.")]
        public static async Task<object> ListFactions(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Include hidden factions (def.hidden), which are engine bookkeeping rather " +
                "than things the player meets.", DefaultValue = false)]
            bool includeHidden = false,
            [ToolParameter(Description =
                "Optional exact faction defName filter. Omit for all.", DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description = "Cap on returned factions.", DefaultValue = 500)]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                // World-level, NOT map-level: this deliberately works at the world
                // map with no map loaded, because that is where the faction
                // question is usually asked.
                if (Find.World == null)
                    return Fail("No world loaded. Load or generate a game first.");

                var fm = Find.FactionManager;
                if (fm == null)
                    return Fail("No FactionManager on the current world.");

                // Settlements are counted ONCE up front and bucketed by faction,
                // rather than re-scanning the world per faction -- with several
                // hundred settlements and ~80 factions that difference is real.
                var settlementsByFaction = new Dictionary<Faction, int>();
                int settlementsTotal = 0;
                var worldObjects = Find.WorldObjects;
                if (worldObjects != null)
                {
                    foreach (var settlement in worldObjects.Settlements)
                    {
                        if (settlement?.Faction == null) continue;
                        int n;
                        settlementsByFaction.TryGetValue(settlement.Faction, out n);
                        settlementsByFaction[settlement.Faction] = n + 1;
                        settlementsTotal++;
                    }
                }

                var player = Faction.OfPlayer;
                var rows = new List<object>();
                int hiddenSkipped = 0, filtered = 0, truncated = 0;

                foreach (var faction in fm.AllFactionsListForReading)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (faction?.def == null) continue;

                    if (!includeHidden && faction.def.hidden) { hiddenSkipped++; continue; }

                    if (!string.IsNullOrWhiteSpace(defName) &&
                        !string.Equals(faction.def.defName, defName.Trim(),
                                       StringComparison.OrdinalIgnoreCase))
                    {
                        filtered++;
                        continue;
                    }

                    if (rows.Count >= limit) { truncated++; continue; }

                    int settlementCount;
                    settlementsByFaction.TryGetValue(faction, out settlementCount);

                    bool isPlayer = player != null && faction == player;

                    rows.Add(new
                    {
                        defName = faction.def.defName,
                        name = faction.Name,
                        isPlayer,
                        hostile = player != null && !isPlayer && faction.HostileTo(player),
                        goodwill = isPlayer ? 0 : faction.PlayerGoodwill,
                        hidden = faction.def.hidden,
                        permanentEnemy = faction.def.permanentEnemy,
                        settlementCount
                    });
                }

                return new
                {
                    success = true,
                    factions = rows,
                    // ⚠️ `count` is HOW MANY WERE RETURNED, not how many exist.
                    // Reported 2026-08-13 by a retired seat after another -- the author of
                    // this tool and of the warning above -- printed `count` alone,
                    // called it "34 factions", and missed 20 hidden ones including
                    // Mechanoid. The prose warning in `message` was correct and
                    // was not read. So the SHAPE now carries it: a caller reading
                    // fields cannot get a total that is silently a subset.
                    count = rows.Count,
                    countReturned = rows.Count,
                    countAllIncludingHidden = rows.Count + hiddenSkipped + truncated,
                    isCompleteList = hiddenSkipped == 0 && truncated == 0,
                    settlementsTotal,
                    hiddenSkipped,
                    filtered,
                    truncated,
                    message = $"{rows.Count} faction(s), {settlementsTotal} settlement(s) on " +
                              $"the planet." +
                              (truncated > 0 ? $" {truncated} beyond limit={limit} omitted." : "") +
                              (hiddenSkipped > 0
                                  ? $" {hiddenSkipped} hidden faction(s) skipped; pass " +
                                    "includeHidden to see them."
                                  : "")
                };
            });
        }

        // 🔴 THE FINDING THAT FORCED THIS TOOL, measured 2026-08-14 by looking at
        // the pictures instead of at the ledger:
        //
        // All TWELVE art screenshots from the live session are NON-EVIDENCE. The
        // camera was aimed correctly -- `look()` jumps to the cell and the subject
        // is dead centre -- and RimWorld's **Debug log window sits exactly on top
        // of the centre of the screen**, 940x650 px of scrolling text over the
        // thing being photographed. The pawn inspect pane covers the bottom-left,
        // the dev palette the top-left. In `p5_004.png` and `p13_012.png` the
        // subject cannot be seen AT ALL.
        //
        // Every one of those rows was filed NEEDS EYES, which reads as "collected,
        // awaiting judgement" -- so a whole class of v1 art gates was going to be
        // adjudicated from images that do not contain their subject. That is the
        // seat's own failure mode wearing a different hat: success:true, a file on
        // disk, and no observation in it.
        //
        // ⚠️ Closing the log by hand does not hold: "Auto-open is ON" reopens it
        // on the next red error, and a modded startup produces those constantly.
        // The close must happen in the same breath as the screenshot, every time,
        // which is why this is a tool and not a note in the runbook.
        [Tool(
            "jawa/clear_ui",
            Description =
                "Close RimWorld's dev windows and drop the current selection, so a " +
                "screenshot shows the MAP instead of the debug log. The Debug log window " +
                "covers the centre of the screen — exactly where jump_camera_to_cell puts " +
                "the subject — and 'Auto-open on error' reopens it constantly under a " +
                "modded load. Call this immediately before every take_screenshot; it is " +
                "cheap, it touches no game state, and without it a screenshot is not " +
                "evidence of anything.",
            ResultDescription =
                "closed: the window types actually removed. remaining: what is still open, " +
                "so a picture that is still obscured names its own culprit. deselected: how " +
                "many things were selected (the inspect pane is drawn from the selection, " +
                "not from a window, and cannot be closed any other way).")]
        public static async Task<object> ClearUi(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Close dev windows — everything deriving from LudeonTK.Window_Dev: the " +
                "debug log, the dev palette, the debug inspector, the actions menus.",
                DefaultValue = true)]
            bool devWindows = true,
            [ToolParameter(Description =
                "Clear the selection, which is what removes the pawn inspect pane from the " +
                "bottom-left.", DefaultValue = true)]
            bool clearSelection = true,
            [ToolParameter(Description =
                "⚠️ Close EVERY window in the stack, not just dev ones. This will also " +
                "dismiss dialogs the game is waiting on — a trade confirmation, a ritual " +
                "prompt — and answering a dialog by destroying it is not the same as " +
                "answering it. Off by default.", DefaultValue = false)]
            bool all = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var stack = Find.WindowStack;
                if (stack == null)
                    return Fail("No WindowStack — the game is not at a UI-bearing state.");

                var closed = new List<string>();
                var remaining = new List<string>();

                // Snapshot first: TryRemove mutates the live list.
                foreach (var w in stack.Windows.ToList())
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (w == null) continue;
                    // Window_Dev is the shared base of every LudeonTK dev window
                    // (EditWindow -> Window_Dev), read out of the assembly with
                    // ilprobe rather than recalled.
                    bool isDev = w is Window_Dev;
                    if ((all || (devWindows && isDev)) && stack.TryRemove(w, false))
                    {
                        closed.Add(w.GetType().Name);
                        continue;
                    }
                    remaining.Add(w.GetType().Name);
                }

                int deselected = 0;
                if (clearSelection && Find.Selector != null)
                {
                    deselected = Find.Selector.NumSelected;
                    Find.Selector.ClearSelection();
                }

                return new
                {
                    success = true,
                    closed,
                    closedCount = closed.Count,
                    remaining,
                    deselected,
                    message = closed.Count == 0 && deselected == 0
                        ? "Nothing to close and nothing was selected. The view was already " +
                          "clear — this is a no-op, not a failure."
                        : $"Closed {closed.Count} window(s), deselected {deselected} thing(s)." +
                          (remaining.Count > 0
                              ? " Still open: " + string.Join(", ", remaining) + "."
                              : "")
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // The read half of spawn_batch/destroy_batch, and the missing half of
        // list_pawns. Every tool that acts on a specific object takes a ThingID
        // (`jawa/damage thingId=`, `jawa/order_pawn targetId=`) and until now
        // NOTHING on the bridge could produce one for a non-pawn: the only route
        // was to click the thing in game and read the inspect pane, which needs a
        // human at the keyboard and cannot be scripted.
        //
        // 🔴 That gap has a measured cost. The `NoPathToPilotConsole` gate --
        // v1's launch blocker -- was SKIPPED in the 2026-08-14 live session for
        // exactly one reason: "no --console-id given; find the PilotConsole
        // ThingID first". A whole live item lost to an identifier we could not
        // ask for.
        //
        // ⚠️ AN EMPTY RESULT IS NOT PROOF OF ABSENCE. It is equally the filter
        // being wrong -- a defName typo, a rect that misses, a group that does
        // not contain this thing. The shape below says which: `scanned` reports
        // how many things were examined before filtering, so a zero with
        // scanned=0 (no map, or an empty one) is a different answer from a zero
        // with scanned=4,891.
        [Tool(
            "jawa/list_things",
            Description =
                "Find things on the map and return their ThingIDs — buildings, items, " +
                "plants, corpses, anything that is not a pawn. This is how you get the id " +
                "that jawa/damage, jawa/order_pawn and jawa/destroy_batch need, without " +
                "clicking the object in game. Filter by defName (exact, or a comma-separated " +
                "list), by rect, or by ThingRequestGroup. Nothing else on the bridge can " +
                "answer 'is it there, and where exactly' for a non-pawn: list_pawns is " +
                "pawns-only, get_cell_info reads one cell, and get_def reads the DEFINITION " +
                "and says nothing about whether an instance exists on this map.",
            ResultDescription =
                "Per thing: id (the ThingID other tools take), def, label, position, " +
                "rotation, stackCount, hitPoints/maxHitPoints, faction, stuff and quality. " +
                "Plus scanned (things examined before filtering), countReturned, " +
                "countMatched and isCompleteList — a zero with scanned>0 means the filter " +
                "excluded everything, which is NOT the same as the map being empty.")]
        public static async Task<object> ListThings(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Exact defName, or a comma-separated list of them. Case-insensitive. " +
                "Omit for no defName filter.", DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description =
                "Optional rect filter 'x,z,w,h'. Omit for the whole map.",
                DefaultValue = null)]
            string rect = null,
            [ToolParameter(Description =
                "Optional ThingRequestGroup name, e.g. BuildingArtificial, Weapon, Apparel, " +
                "Plant, Corpse. Invalid names are REFUSED with the valid list rather than " +
                "silently ignored — a typo here would otherwise read as 'nothing found'.",
                DefaultValue = null)]
            string group = null,
            [ToolParameter(Description =
                "Include pawns. Off by default because jawa/list_pawns reports them far " +
                "better; on, they appear here as ordinary things.", DefaultValue = false)]
            bool includePawns = false,
            [ToolParameter(Description = "Cap on returned things.", DefaultValue = 200)]
            int limit = 200)
        {
            int rx = 0, rz = 0, rw = 0, rh = 0;
            if (!string.IsNullOrWhiteSpace(rect))
            {
                List<ParsedOp> parsedRect;
                var rectErrors = new List<string>();
                if (!TryParseOps(rect, "_", out parsedRect, rectErrors) || parsedRect.Count != 1)
                    return Fail("rect must be a single 'x,z,w,h'.", new { errors = rectErrors });
                rx = parsedRect[0].X; rz = parsedRect[0].Z;
                rw = parsedRect[0].W; rh = parsedRect[0].H;
            }

            var wanted = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            if (!string.IsNullOrWhiteSpace(defName))
                foreach (var piece in defName.Split(','))
                    if (!string.IsNullOrWhiteSpace(piece)) wanted.Add(piece.Trim());

            // Parsed BEFORE the main-thread hop so a typo costs nothing and comes
            // back with the answer in it.
            ThingRequestGroup grp = ThingRequestGroup.Undefined;
            if (!string.IsNullOrWhiteSpace(group))
            {
                if (!Enum.TryParse(group.Trim(), true, out grp))
                    return Fail(
                        $"No ThingRequestGroup named '{group}'.",
                        new { valid = Enum.GetNames(typeof(ThingRequestGroup)) });
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map. Load a game first.");

                // AllThings, not a ThingRequest listing, because the group filter is
                // optional and the def filter is the common case. The scan is one
                // pass over the lister either way.
                var source = grp == ThingRequestGroup.Undefined
                    ? (IEnumerable<Thing>)map.listerThings.AllThings
                    : map.listerThings.ThingsInGroup(grp);

                var rows = new List<object>();
                var perDef = new Dictionary<string, int>();
                int scanned = 0, matched = 0, truncated = 0, pawnsSkipped = 0;

                foreach (var thing in source)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (thing?.def == null) continue;
                    scanned++;

                    if (!includePawns && thing is Pawn) { pawnsSkipped++; continue; }
                    if (wanted.Count > 0 && !wanted.Contains(thing.def.defName)) continue;

                    var pos = thing.Spawned ? thing.Position : IntVec3.Invalid;
                    if (rw > 0)
                    {
                        if (!pos.IsValid) continue;
                        if (pos.x < rx || pos.z < rz || pos.x >= rx + rw || pos.z >= rz + rh)
                            continue;
                    }

                    matched++;
                    int n;
                    perDef.TryGetValue(thing.def.defName, out n);
                    perDef[thing.def.defName] = n + 1;

                    if (rows.Count >= limit) { truncated++; continue; }

                    QualityCategory q;
                    string quality = thing.TryGetQuality(out q) ? q.ToString() : null;

                    rows.Add(new
                    {
                        id = thing.ThingID,
                        def = thing.def.defName,
                        label = thing.LabelCap.ToString(),
                        x = pos.x,
                        z = pos.z,
                        spawned = thing.Spawned,
                        rot = thing.Rotation.AsInt,
                        stackCount = thing.stackCount,
                        hitPoints = thing.def.useHitPoints ? thing.HitPoints : -1,
                        maxHitPoints = thing.def.useHitPoints ? thing.MaxHitPoints : -1,
                        faction = thing.Faction?.def?.defName,
                        stuff = thing.Stuff?.defName,
                        quality
                    });
                }

                return new
                {
                    success = true,
                    things = rows,
                    // Same shape discipline as list_factions: a caller reading
                    // fields cannot get a total that is silently a subset.
                    scanned,
                    countReturned = rows.Count,
                    countMatched = matched,
                    isCompleteList = truncated == 0,
                    truncated,
                    pawnsSkipped,
                    perDef,
                    ticksGame = TicksGameSafe(),
                    message = matched == 0
                        ? $"NOTHING MATCHED. {scanned} thing(s) were examined, so this is a " +
                          "filter result, not an empty map — check the defName spelling, the " +
                          "rect and the group before concluding the thing is absent."
                        : $"{rows.Count} of {matched} matching thing(s) returned, " +
                          $"{scanned} examined." +
                          (truncated > 0 ? $" {truncated} beyond limit={limit} omitted." : "")
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---------------------------------------------------------------------
        // jawa/ideo_of — read the ideoligions the game ACTUALLY built, and count
        // who believes them.
        //
        // WHY. A retired seat authored eleven ideoligions and never saw one after
        // generation: "the game built the ideoligion I specified" is an
        // inference off the XML. An Ideo is not a Def — it is a runtime object
        // assembled by the generator from memes, a structure and a precept
        // roll — so there is no def to read and `jawa/get_defs` cannot reach it.
        //
        // 🔴 THE SECOND HALF IS THE ONE THAT MATTERS. That seat disciplined the
        // whole religions design around "NPC religion rarely surfaces in play"
        // and cut rituals and deities because of it — a belief that has NEVER
        // been measured. `believers` counts pawns per ideo across every map and
        // the world-pawn pool. **If the non-player counts come back ~0, the
        // eleven are not load-bearing and the design should say so.** That is a
        // finding either way, which is why the count is not optional-by-default.
        //
        // Names read with ilprobe, not recalled:
        //   Find.IdeoManager -> IdeoManager::get_IdeosListForReading
        //   Ideo::name/adjective/memberName/culture/memes/id/hidden/
        //     initialPlayerIdeo, get_PreceptsListForReading,
        //     get_StructureMeme, get_KeyDeityName, get_DeityCountRange,
        //     get_RolesListForReading, get_VeneratedAnimals,
        //     get_PreferredXenotypes, get_SupremeGender, get_Fluid
        //   Faction::ideos (public) -> FactionIdeosTracker::get_PrimaryIdeo
        //   Pawn_IdeoTracker::get_Ideo · MapPawns::get_AllPawns
        //   WorldPawns::get_AllPawnsAliveOrDead · ModsConfig::get_IdeologyActive
        //
        // ⚠️ Faction membership is derived by walking FactionManager and reading
        // each faction's PrimaryIdeo, NOT by IdeoManager::GetFactionsWithIdeo.
        // Both would answer; only the first uses getters this file has verified.
        // ---------------------------------------------------------------------
        [Tool(
            "jawa/ideo_of",
            Description =
                "Read the ideoligions the running game actually generated — memes, structure, " +
                "deity, precepts, roles, venerated animals — and count how many pawns believe " +
                "each one. An Ideo is a RUNTIME object, not a Def, so no amount of def reading " +
                "can reach it and an authored ideoligion is otherwise unverifiable. The believer " +
                "counts answer a separate question the design has been assuming rather than " +
                "measuring: whether NPC religion surfaces in play at all. Read-only.",
            ResultDescription =
                "Per ideo: id, name, adjective, memberName, culture, structure meme, key deity, " +
                "memes, precepts (with `enabledForNPCFactions`, which is what decides whether a " +
                "precept is ever seen off the player's colony), roles, venerated animals, " +
                "preferred xenotypes, and the factions whose PRIMARY ideo it is. " +
                "🔴 `believers` splits into colonists / otherOnMap / worldPawns — a total alone " +
                "hides the whole question, because an ideo held only by the player's colony is " +
                "not evidence that NPC religion surfaces. `ideologyActive:false` is reported as " +
                "a loud failure, not as zero ideoligions.")]
        public static async Task<object> IdeoOf(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Case-insensitive substring of the ideo NAME, or its numeric id. Empty returns " +
                "every ideo. ⚠️ An Ideo has no defName — its `name` is generated text, so match " +
                "on a fragment and check what came back.", DefaultValue = null)]
            string ideo = null,
            [ToolParameter(Description =
                "Include the full precept list per ideo.", DefaultValue = true)]
            bool precepts = true,
            [ToolParameter(Description =
                "Count believers across all maps and the world-pawn pool. Costs one pass over " +
                "every pawn; on a large save that is thousands of objects, so it is skippable — " +
                "but it is the half that answers whether NPC religion exists in play.",
                DefaultValue = true)]
            bool believers = true,
            [ToolParameter(Description = "Cap on ideos returned.", DefaultValue = 50)]
            int limit = 50)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                // Loud, and deliberately not "0 ideoligions". An absent DLC and
                // an empty result are different answers, and the trap this
                // project keeps hitting is an instrument that cannot see a
                // thing reporting that the thing is not there.
                if (!ModsConfig.IdeologyActive)
                    return Fail("Ideology is NOT active in this build. There are no ideoligions " +
                                "to read — this is a capability answer, not a count of zero.");

                var mgr = Find.IdeoManager;
                if (mgr == null)
                    return Fail("No IdeoManager. This reads runtime ideoligions, so it needs a " +
                                "GAME loaded — the main menu is not enough.");

                var all = mgr.IdeosListForReading;
                if (all == null) return Fail("IdeoManager returned no ideo list.");

                var wanted = (ideo ?? "").Trim();
                var byId = -1;
                var isId = wanted.Length > 0 && int.TryParse(wanted, out byId);

                var picked = all.Where(q => q != null).Where(q =>
                    wanted.Length == 0
                    || (isId && q.id == byId)
                    || (q.name ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)
                    .Take(limit).ToList();

                // Believer counts, one pass. Split three ways on purpose: a
                // total is exactly the number that would let "NPC religion
                // surfaces" survive on the player colony's own believers.
                var colonists = new Dictionary<int, int>();
                var otherOnMap = new Dictionary<int, int>();
                var worldPawns = new Dictionary<int, int>();
                var pawnsScanned = 0;
                if (believers)
                {
                    void Bump(Dictionary<int, int> d, int id)
                    {
                        d.TryGetValue(id, out var c);
                        d[id] = c + 1;
                    }

                    var maps = Find.Maps;
                    if (maps != null)
                        foreach (var m in maps)
                        {
                            var mp = m?.mapPawns?.AllPawns;
                            if (mp == null) continue;
                            foreach (var p in mp)
                            {
                                cancellationToken.ThrowIfCancellationRequested();
                                pawnsScanned++;
                                var pi = p?.ideo?.Ideo;
                                if (pi == null) continue;
                                if (p.Faction != null && p.Faction.IsPlayer)
                                    Bump(colonists, pi.id);
                                else Bump(otherOnMap, pi.id);
                            }
                        }

                    var wp = Find.WorldPawns?.AllPawnsAliveOrDead;
                    if (wp != null)
                        foreach (var p in wp)
                        {
                            cancellationToken.ThrowIfCancellationRequested();
                            pawnsScanned++;
                            var pi = p?.ideo?.Ideo;
                            if (pi != null) Bump(worldPawns, pi.id);
                        }
                }

                // Faction -> primary ideo, walked once and inverted, so N ideos
                // cost one pass rather than N.
                var facByIdeo = new Dictionary<int, List<string>>();
                var fm = Find.FactionManager;
                if (fm?.AllFactions != null)
                    foreach (var f in fm.AllFactions)
                    {
                        var pi = f?.ideos?.PrimaryIdeo;
                        if (pi == null) continue;
                        if (!facByIdeo.TryGetValue(pi.id, out var lst))
                            facByIdeo[pi.id] = lst = new List<string>();
                        lst.Add(f.Name ?? f.def?.defName ?? "(unnamed)");
                    }

                int Get(Dictionary<int, int> d, int id)
                {
                    d.TryGetValue(id, out var c);
                    return c;
                }

                var rows = new List<object>();
                foreach (var i in picked)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    facByIdeo.TryGetValue(i.id, out var facs);

                    rows.Add(new
                    {
                        id = i.id,
                        name = i.name,
                        adjective = i.adjective,
                        memberName = i.memberName,
                        culture = i.culture?.defName,
                        structureMeme = i.StructureMeme?.defName,
                        keyDeityName = i.KeyDeityName,
                        deityCountRange = i.DeityCountRange.ToString(),
                        supremeGender = i.SupremeGender.ToString(),
                        hidden = i.hidden,
                        fluid = i.Fluid,
                        initialPlayerIdeo = i.initialPlayerIdeo,
                        memes = i.memes?.Where(q => q != null)
                                 .Select(q => q.defName).ToList(),
                        preceptCount = i.PreceptsListForReading?.Count ?? 0,
                        precepts = precepts
                            ? i.PreceptsListForReading?.Where(q => q?.def != null)
                                .Select(q => new
                                {
                                    defName = q.def.defName,
                                    label = q.def.label,
                                    issue = q.def.issue?.defName,
                                    impact = q.def.impact.ToString(),
                                    // The field that decides whether this
                                    // precept is ever visible off the player's
                                    // own colony. That seat's counter question
                                    // lives here as much as in the pawn counts.
                                    enabledForNPCFactions = q.def.enabledForNPCFactions
                                }).Cast<object>().ToList()
                            : null,
                        roles = i.RolesListForReading?.Where(q => q?.def != null)
                                 .Select(q => q.def.defName).ToList(),
                        veneratedAnimals = i.VeneratedAnimals?.Where(q => q != null)
                                            .Select(q => q.defName).ToList(),
                        preferredXenotypes = i.PreferredXenotypes?.Where(q => q != null)
                                              .Select(q => q.defName).ToList(),
                        primaryFactions = facs ?? new List<string>(),
                        believers = believers
                            ? (object)new
                            {
                                colonists = Get(colonists, i.id),
                                otherOnMap = Get(otherOnMap, i.id),
                                worldPawns = Get(worldPawns, i.id),
                                total = Get(colonists, i.id) + Get(otherOnMap, i.id)
                                        + Get(worldPawns, i.id)
                            }
                            : null
                    });
                }

                var npcTotal = believers
                    ? picked.Sum(q => Get(otherOnMap, q.id) + Get(worldPawns, q.id))
                    : -1;

                return new
                {
                    success = true,
                    message =
                        $"{picked.Count} of {all.Count} ideoligion(s) returned" +
                        (believers
                            ? $"; {pawnsScanned} pawns scanned, {npcTotal} NON-PLAYER believer(s) " +
                              "across them. 🔴 A non-player total near zero means NPC religion " +
                              "does not surface in this save, whatever the design assumes."
                            : "; believer counting was SKIPPED."),
                    ideologyActive = true,
                    ideosTotal = all.Count,
                    ideosReturned = picked.Count,
                    believersCounted = believers,
                    pawnsScanned,
                    nonPlayerBelieversTotal = npcTotal,
                    ideos = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---------------------------------------------------------------------
        // jawa/biome_probe — what a biome RESOLVES to spawn, not what its XML says.
        //
        // WHY, and it is not a convenience wrapper over get_defs.
        // A retired seat judged 29 biome removals from def fields alone and looked at
        // exactly one. I went to check whether get_defs could have answered the
        // other 28 and it CANNOT, for a reason worth writing down:
        //
        //   🔴 `Scalars()` reads PUBLIC INSTANCE FIELDS. On BiomeDef,
        //      `wildAnimals`, `coastalWildAnimals`, `pollutionWildAnimals`,
        //      `diseases` and `allowedPackAnimals` are all **private**, and
        //      `AllWildAnimals` / `AllWildPlants` are **properties**.
        //      ⇒ every tool this bridge ships is blind to them. The 28
        //      "judged from def fields" were judged from fields nothing here
        //      can read.
        //
        // And the resolved answer differs from the XML anyway: AllWildPlants is
        // built by filtering every ThingDef to CommonalityOfPlant > 0
        // (IL_0033/0038), and CommonalityOfAnimal folds wildAnimals into a cache
        // that any load-time mutation has already touched. A def dump is DISK;
        // this is RUNTIME, and where they disagree runtime wins.
        //
        // ⚠️ Both getters build their own cache lazily (get_AllWildPlants
        // IL_0006, CommonalityOfAnimal IL_0006), so calling them cold is safe
        // and does not need a map.
        //
        // Diseases and pack animals are deliberately NOT exposed: their backing
        // lists are private and their record types (BiomeDiseaseRecord) would
        // need reflection to read. An honest gap beats a half-serialised one.
        // ---------------------------------------------------------------------
        [Tool(
            "jawa/biome_probe",
            Description =
                "Ask a biome what it will ACTUALLY spawn — the resolved wild-animal and " +
                "wild-plant sets with their commonalities, read off the runtime caches rather " +
                "than off XML. Built for removal audits: `find` answers 'is this animal still " +
                "in these biomes' across every biome in one call, which is the check that " +
                "distinguishes a removal that took from a removal that silently no-opped. " +
                "🔴 No other tool here can see these — the backing fields are private and the " +
                "resolved lists are properties, so reflective def reading returns nothing. " +
                "Read-only; needs a GAME but no map.",
            ResultDescription =
                "Per biome: the public generation flags (implemented, generatesNaturally, " +
                "canBuildBase, canAutoChoose, densities, forageability) plus `animals` and " +
                "`plants` as {defName, commonality}, largest first. When `find` is given, " +
                "`findResults` reports each name with a THREE-state `state`: `spawning` " +
                "(declared and resolves above zero), `zeroed` (record still declared but " +
                "weight 0 — it will not spawn, and it comes straight back if anything " +
                "re-weights it) or `absent` (no record at all). ⚠️ `present` alone cannot " +
                "tell zeroed from absent, because the engine's own resolved lists drop both — " +
                "and they are different defects.")]
        public static async Task<object> BiomeProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Comma-separated BiomeDef defNames. Empty probes every biome with " +
                "generatesNaturally=true, which is the set a campaign can actually land on.",
                DefaultValue = null)]
            string biomes = null,
            [ToolParameter(Description =
                "Comma-separated PawnKindDef and/or ThingDef defNames to look for in every " +
                "probed biome. This is the removal audit: one call answers 'did it go'.",
                DefaultValue = null)]
            string find = null,
            [ToolParameter(Description =
                "Include the full animal list per biome.", DefaultValue = true)]
            bool animals = true,
            [ToolParameter(Description =
                "Include the full plant list per biome. Verbose — a temperate biome carries " +
                "dozens.", DefaultValue = false)]
            bool plants = false,
            [ToolParameter(Description = "Cap on biomes probed.", DefaultValue = 40)]
            int limit = 40,
            [ToolParameter(Description =
                "Cap on entries in each per-biome list.", DefaultValue = 60)]
            int topN = 60)
        {
            var findNames = new HashSet<string>((find ?? "")
                .Split(',').Select(q => q.Trim()).Where(q => q.Length > 0),
                StringComparer.OrdinalIgnoreCase);

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var wanted = (biomes ?? "").Split(',')
                    .Select(q => q.Trim()).Where(q => q.Length > 0).ToList();

                var picked = new List<BiomeDef>();
                var notFound = new List<string>();

                if (wanted.Count > 0)
                {
                    foreach (var w in wanted.Take(limit))
                    {
                        var b = DefDatabase<BiomeDef>.GetNamedSilentFail(w);
                        if (b == null) notFound.Add(w);
                        else picked.Add(b);
                    }
                }
                else
                {
                    picked.AddRange(DefDatabase<BiomeDef>.AllDefsListForReading
                        .Where(q => q != null && q.generatesNaturally)
                        .Take(limit));
                }

                if (picked.Count == 0)
                    return Fail("No biome resolved.", new
                    {
                        notFound,
                        suggestion = "Leave `biomes` empty to probe every naturally " +
                                     "generating biome."
                    });

                var rows = new List<object>();
                // Which searched names were found in ANY probed biome. Kept as a
                // plain set while the rows are built: the alternative is
                // reflecting back over anonymous types after the fact, which is
                // how a summary line quietly stops agreeing with the rows it
                // summarises.
                var foundSomewhere = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

                foreach (var b in picked)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    // Both of these populate their own cache on first touch.
                    // Counts are taken over the WHOLE resolved set; the emitted
                    // list is capped afterwards, so a cap can never read as a
                    // small biome.
                    var animalIndex = new Dictionary<string, float>(
                        StringComparer.OrdinalIgnoreCase);
                    foreach (var a in b.AllWildAnimals)
                    {
                        if (a == null) continue;
                        animalIndex[a.defName] = b.CommonalityOfAnimal(a);
                    }

                    var plantIndex = new Dictionary<string, float>(
                        StringComparer.OrdinalIgnoreCase);
                    foreach (var p in b.AllWildPlants)
                    {
                        if (p == null) continue;
                        plantIndex[p.defName] = b.CommonalityOfPlant(p);
                    }

                    var animalCount = animalIndex.Count;
                    var plantCount = plantIndex.Count;

                    var animalList = animals
                        ? animalIndex.OrderByDescending(kv => kv.Value).Take(topN)
                            .Select(kv => (object)new
                            {
                                defName = kv.Key, commonality = kv.Value
                            }).ToList()
                        : null;
                    var plantList = plants
                        ? plantIndex.OrderByDescending(kv => kv.Value).Take(topN)
                            .Select(kv => (object)new
                            {
                                defName = kv.Key, commonality = kv.Value
                            }).ToList()
                        : null;

                    List<object> findRows = null;
                    if (findNames.Count > 0)
                    {
                        // 🔴 The resolved list ALONE cannot answer a removal
                        // audit, and this is measured, not assumed:
                        // <get_AllWildAnimals>d__94::MoveNext yields a kind only
                        // if CommonalityOfAnimal > 0 OR CommonalityOfPollution
                        // Animal > 0 OR CommonalityOfCoastalAnimal > 0
                        // (IL_0055/0063/0071), and get_AllWildPlants filters on
                        // CommonalityOfPlant > 0 (IL_0038). ⇒ **an animal whose
                        // commonality was set to 0 is ABSENT from the resolved
                        // list, exactly like one whose record was deleted.**
                        // Reporting only `present` would make those two
                        // indistinguishable — and they are different defects: a
                        // zeroed record still costs the world a def and lets the
                        // animal straight back if anything re-weights it.
                        //
                        // So `state` is decided against the DECLARED records:
                        //   spawning — declared and resolves above zero
                        //   zeroed   — declared, but weight 0: it will not spawn
                        //              and the record is still there
                        //   absent   — no record at all
                        var declared = DeclaredBiomeEntries(b);
                        findRows = new List<object>();
                        foreach (var q in findNames)
                        {
                            var inA = animalIndex.TryGetValue(q, out var ca);
                            var inP = plantIndex.TryGetValue(q, out var cp);
                            var spawning = inA || inP;
                            var isDeclared = declared.TryGetValue(q, out var decl);
                            if (spawning) foundSomewhere.Add(q);

                            findRows.Add(new
                            {
                                defName = q,
                                // Kept as its own column even when every entry
                                // is false — a retired seat's ask. `present` means WILL
                                // SPAWN, nothing weaker.
                                present = spawning,
                                state = spawning ? "spawning"
                                                 : (isDeclared ? "zeroed" : "absent"),
                                declared = isDeclared,
                                where = inA ? "animal"
                                            : (inP ? "plant" : decl.Kind),
                                commonality = inA ? ca : (inP ? cp : 0f),
                                declaredCommonality = isDeclared ? decl.Commonality : 0f
                            });
                        }
                    }

                    rows.Add(new
                    {
                        defName = b.defName,
                        label = b.label,
                        modName = b.modContentPack?.Name,
                        implemented = b.implemented,
                        generatesNaturally = b.generatesNaturally,
                        canBuildBase = b.canBuildBase,
                        canAutoChoose = b.canAutoChoose,
                        isExtremeBiome = b.isExtremeBiome,
                        isWaterBiome = b.isWaterBiome,
                        impassable = b.impassable,
                        animalDensity = b.animalDensity,
                        plantDensity = b.plantDensity,
                        diseaseMtbDays = b.diseaseMtbDays,
                        forageability = b.forageability,
                        foragedFood = b.foragedFood?.defName,
                        settlementSelectionWeight = b.settlementSelectionWeight,
                        // The COUNTS are over the whole resolved set; the lists
                        // are capped. Reporting only a capped list would let a
                        // truncation read as a small biome.
                        wildAnimalCount = animalCount,
                        wildPlantCount = plantCount,
                        animalsListed = animalList?.Count ?? 0,
                        plantsListed = plantList?.Count ?? 0,
                        animals = animalList,
                        plants = plantList,
                        findResults = findRows
                    });
                }

                var absentEverywhere = findNames.Where(q => !foundSomewhere.Contains(q))
                                                .ToList();

                return new
                {
                    // success is "the probe ran". A `find` that found nothing is
                    // the ANSWER to a removal audit, never a failure of it.
                    success = notFound.Count == 0,
                    message =
                        $"{picked.Count} biome(s) probed" +
                        (notFound.Count > 0
                            ? $"; ⚠️ {notFound.Count} not found: " + string.Join(", ", notFound)
                            : "") +
                        (findNames.Count > 0
                            ? $"; searched for {findNames.Count} name(s) — read `findResults` " +
                              "per biome, and note that present-at-commonality-0 is NOT absent."
                            : ""),
                    biomesProbed = picked.Count,
                    notFound,
                    searched = findNames.ToList(),
                    absentFromEveryProbedBiome = absentEverywhere,
                    biomes = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---------------------------------------------------------------------
        // jawa/inspect_string — read what the game itself says about a thing.
        //
        // WHY, and it is the widest gap left on this bridge. Every question of
        // the form "is this thing actually WORKING?" is answered in game by the
        // inspect pane, and nothing here could read it. Measured examples from
        // one evening:
        //   · a SmallThruster reports WarningThrusterInside / ThrusterBlockedBy
        //     / ThrusterNotConnected — a retired seat's whole L1 gate — and
        //     get_cell_info returns only `className: Verse.Building`.
        //   · CompGravshipThruster::get_CanBeActive folds FOUR conditions
        //     (base, Blocked, BrokenDown, outdoors) into one bool that no tool
        //     could see; the comp's own CompInspectStringExtra spells out which.
        //   · a breakdown, a lack of power, a missing connection, a full
        //     container — all of them already write a sentence nobody could read.
        //
        // ⇒ this is not one gate's tool. It turns "spawn it and hope" into
        // "spawn it and read what the game concluded", for every comp that
        // ships an inspect string — which is nearly all of them.
        //
        // Signatures read with ilprobe, not recalled:
        //   Verse.Thing::GetInspectString()            public string
        //   Verse.Thing::GetInspectStringLowPriority() public string
        //   ThingWithComps::GetInspectString() overrides and folds in
        //     InspectStringPartsFromComps()
        //
        // 🔴 GetInspectString can THROW for a comp in a bad state, and a throw
        // here would take out a whole batch. Each thing is wrapped
        // individually, and a thrower reports its exception in its own row
        // rather than aborting the others — an unreadable thing must not look
        // like an absent one.
        // ---------------------------------------------------------------------
        [Tool(
            "jawa/inspect_string",
            Description =
                "Read the inspect-pane text the game writes for a thing — the same sentences a " +
                "player sees when they click it. This is how you find out whether something is " +
                "WORKING as opposed to merely present: 'Blocked by', 'Needs power', 'Broken " +
                "down', 'will be blocked due to being indoors'. Nothing else on this bridge " +
                "exposes comp state at all — get_cell_info reports a className and stops. Takes " +
                "thingIds, or a defName, or a rect. Read-only.",
            ResultDescription =
                "Per thing: id, defName, label, position, and `inspect` — the full inspect " +
                "string with newlines preserved as a list of lines, because the interesting " +
                "part is usually one line among several. `lowPriority` carries the secondary " +
                "text. ⚠️ A thing whose comps THROW while building the string is reported with " +
                "its `error`, never dropped — an unreadable thing must not be mistaken for an " +
                "absent one.")]
        public static async Task<object> InspectString(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Comma-separated ThingIDs, as returned by jawa/list_things or jawa/spawn_batch. " +
                "Omit to select by defName and/or rect instead.", DefaultValue = null)]
            string thingIds = null,
            [ToolParameter(Description =
                "Exact defName, or a comma-separated list. Combines with `rect`.",
                DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description =
                "Rect filter 'x,z,w,h'. Combines with `defName`.", DefaultValue = null)]
            string rect = null,
            [ToolParameter(Description = "Cap on things returned.", DefaultValue = 25)]
            int limit = 25)
        {
            var wantIds = new HashSet<string>((thingIds ?? "")
                .Split(',').Select(q => q.Trim()).Where(q => q.Length > 0),
                StringComparer.OrdinalIgnoreCase);
            var wantDefs = new HashSet<string>((defName ?? "")
                .Split(',').Select(q => q.Trim()).Where(q => q.Length > 0),
                StringComparer.OrdinalIgnoreCase);

            if (wantIds.Count == 0 && wantDefs.Count == 0 && string.IsNullOrWhiteSpace(rect))
                return Fail("Give thingIds, defName, or rect — otherwise this would read the " +
                            "whole map, which is how the bridge livelocks the game.");

            CellRect? box = null;
            if (!string.IsNullOrWhiteSpace(rect))
            {
                var p = rect.Split(',');
                if (p.Length != 4
                    || !int.TryParse(p[0].Trim(), out var rx)
                    || !int.TryParse(p[1].Trim(), out var rz)
                    || !int.TryParse(p[2].Trim(), out var rw)
                    || !int.TryParse(p[3].Trim(), out var rh))
                    return Fail($"rect must be 'x,z,w,h', got '{rect}'.");
                box = new CellRect(rx, rz, rw, rh);
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");

                var rows = new List<object>();
                var examined = 0;
                var threw = 0;

                foreach (var t in map.listerThings.AllThings)
                {
                    if (rows.Count >= limit) break;
                    cancellationToken.ThrowIfCancellationRequested();
                    if (t == null) continue;
                    examined++;

                    if (wantIds.Count > 0 && !wantIds.Contains(t.ThingID)) continue;
                    if (wantDefs.Count > 0 && !wantDefs.Contains(t.def?.defName ?? "")) continue;
                    if (box.HasValue && !box.Value.Contains(t.Position)) continue;

                    string main = null, low = null, err = null;
                    // Wrapped per-thing on purpose. One comp in a bad state
                    // must cost its own row, not the batch.
                    try { main = t.GetInspectString(); }
                    catch (Exception e) { err = e.GetType().Name + ": " + e.Message; threw++; }
                    try { low = t.GetInspectStringLowPriority(); }
                    catch { /* secondary text; its absence is not a finding */ }

                    rows.Add(new
                    {
                        id = t.ThingID,
                        defName = t.def?.defName,
                        label = t.Label,
                        x = t.Position.x,
                        z = t.Position.z,
                        className = t.GetType().FullName,
                        // Split because the load-bearing sentence is normally
                        // one line among several, and a caller grepping a blob
                        // for a substring will match across a line break.
                        inspect = string.IsNullOrEmpty(main)
                            ? new List<string>()
                            : main.Split('\n').Select(q => q.TrimEnd('\r')).ToList(),
                        lowPriority = low,
                        error = err
                    });
                }

                return new
                {
                    // A filter that matched nothing is an ANSWER. It is said
                    // out loud so it cannot be read as an empty map.
                    success = true,
                    message = rows.Count == 0
                        ? $"NOTHING MATCHED. {examined} thing(s) were examined, so this is a " +
                          "filter result, not an empty map — check the ids, the defName and " +
                          "the rect before concluding the thing is absent."
                        : $"{rows.Count} thing(s) inspected, {examined} examined." +
                          (threw > 0
                              ? $" ⚠️ {threw} threw while building their inspect string and " +
                                "carry an `error` — they were NOT dropped."
                              : ""),
                    matched = rows.Count,
                    examined,
                    threw,
                    things = rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ---------------------------------------------------------------------
        // jawa/set_faction_relation — make a faction hostile so a raid can be
        // aimed at it.
        //
        // WHY, and it is a blocked gate rather than an itch. A retired seat's biggest
        // open design question is whether the Galactic Empire READS as an
        // antagonist, and the only way to find out is to look at one of its
        // raids. `jawa/fire_incident RaidEnemy faction=OuterRim_GalacticEmpire`
        // returned `canFireNow: false` on the first live attempt, because
        // IncidentWorker_RaidEnemy::TryResolveRaidFaction keeps the faction you
        // pass ONLY if FactionUtility::HostileTo(Faction.OfPlayer) — and the
        // Empire ships neutral (goodwill 0). ⇒ the raid cannot be aimed until
        // something makes it hostile, and NOTHING on the bridge could: 133 tools
        // and not one touches faction relations. The debug tree has no usable
        // action either — a search for "goodwill" returns a single
        // QuestPart test entry.
        //
        // 🔴 Worse, the failure was SILENT-SHAPED. Fired without dryRun,
        // TryResolveRaidFaction passes `parms.faction` BY REFERENCE into
        // PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted
        // (IL_0059/006a) and overwrites it with a weighted random pick — so the
        // raid arrives, reports success, and is somebody else's faction. The
        // screenshot would have been of the wrong antagonist with nothing
        // flagging it.
        //
        // Signatures read with ilprobe, not recalled:
        //   Faction::SetRelationDirect(Faction, FactionRelationKind, bool
        //       canSendHostilityLetter, string reason, GlobalTargetInfo?)
        //   Faction::RelationWith(Faction other, bool allowNull)
        //       -> FactionRelation { other, baseGoodwill, kind }
        //   Faction::GoodwillWith(Faction) · Faction::get_PlayerGoodwill
        // ---------------------------------------------------------------------
        [Tool(
            "jawa/set_faction_relation",
            Description =
                "Set a faction's relation to the PLAYER — hostile, neutral or ally — and " +
                "optionally its goodwill number. Exists to unblock aimed raids: an incident " +
                "worker will silently substitute a random faction for one that is not hostile, " +
                "so testing 'does THIS faction read as an antagonist' is impossible until the " +
                "faction can be made hostile on demand. Suppresses the hostility letter by " +
                "default so a test does not narrate itself into the player's log.",
            ResultDescription =
                "Returns `was` and `now` for BOTH kind and goodwill, each READ BACK off the " +
                "faction after the call — never inferred from the setter returning, which is " +
                "void. success means the read-back matches what was asked for. `dryRun` " +
                "reports the current relation and changes nothing.")]
        public static async Task<object> SetFactionRelation(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Faction defName, e.g. Empire (the Galactic Empire's vessel). ⚠️ The " +
                "defName, not the generated name — 'Galactic Empire' is a name, not a def.")]
            string faction,
            [ToolParameter(Description =
                "Hostile, Neutral or Ally. Case-insensitive. Omit to change goodwill only.",
                DefaultValue = null)]
            string kind = null,
            [ToolParameter(Description =
                "Base goodwill, -100..100. Omit to leave it alone. ⚠️ Setting goodwill does " +
                "NOT by itself change the relation KIND — pass `kind` if that is what you need.",
                DefaultValue = -9999)]
            int goodwill = -9999,
            [ToolParameter(Description =
                "Let RimWorld send its hostility letter. Off by default: a test should not " +
                "narrate itself.", DefaultValue = false)]
            bool sendLetter = false,
            [ToolParameter(Description = "Report the current relation and change nothing.",
                DefaultValue = false)]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var fm = Find.FactionManager;
                if (fm == null)
                    return Fail("No FactionManager. This needs a GAME loaded.");

                var player = Faction.OfPlayer;
                if (player == null) return Fail("No player faction.");

                var target = fm.AllFactions.FirstOrDefault(
                    q => string.Equals(q?.def?.defName, faction, StringComparison.OrdinalIgnoreCase));
                if (target == null)
                    return Fail($"No faction with defName '{faction}'.", new
                    {
                        // Named rather than left to a guess: the defName/name
                        // split has already cost one call today.
                        hint = "Use the DEFNAME. jawa/list_factions returns both.",
                        suggestions = fm.AllFactions.Where(q => q?.def != null)
                            .Select(q => q.def.defName)
                            .Where(q => q.IndexOf(faction, StringComparison.OrdinalIgnoreCase) >= 0)
                            .Take(12).ToList()
                    });

                if (target == player) return Fail("Cannot set the player's relation to itself.");

                var wasKind = target.RelationKindWith(player).ToString();
                var wasGoodwill = target.GoodwillWith(player);

                FactionRelationKind parsed = default;
                var wantKind = !string.IsNullOrWhiteSpace(kind);
                if (wantKind && !Enum.TryParse(kind.Trim(), true, out parsed))
                    return Fail($"'{kind}' is not a FactionRelationKind.", new
                    {
                        valid = Enum.GetNames(typeof(FactionRelationKind))
                    });

                var wantGoodwill = goodwill != -9999;
                if (wantGoodwill && (goodwill < -100 || goodwill > 100))
                    return Fail($"goodwill must be -100..100, got {goodwill}.");

                if (!wantKind && !wantGoodwill && !dryRun)
                    return Fail("Nothing to do: pass `kind`, `goodwill`, or both.");

                if (!dryRun)
                {
                    // Goodwill first, then kind. Order matters: SetRelationDirect
                    // is the authority on kind, and doing it last means a
                    // goodwill write cannot drag the kind somewhere unasked.
                    if (wantGoodwill)
                    {
                        var rel = target.RelationWith(player, false);
                        if (rel == null)
                            return Fail("Faction has no relation record with the player.");
                        rel.baseGoodwill = goodwill;
                    }

                    if (wantKind)
                        target.SetRelationDirect(player, parsed, sendLetter,
                            "Set by jawa/set_faction_relation for testing.", null);
                }

                // 🔴 Read back. SetRelationDirect returns void and the goodwill
                // write is a bare field assignment, so neither can tell us it
                // worked. Everything below is measured off the faction after the
                // fact, and `success` compares the read-back to the request.
                var nowKind = target.RelationKindWith(player).ToString();
                var nowGoodwill = target.GoodwillWith(player);

                var kindOk = !wantKind || dryRun
                             || string.Equals(nowKind, parsed.ToString(),
                                              StringComparison.OrdinalIgnoreCase);
                var goodwillOk = !wantGoodwill || dryRun || nowGoodwill == goodwill;

                return new
                {
                    success = kindOk && goodwillOk,
                    message = dryRun
                        ? $"{target.def.defName} ('{target.Name}') is {nowKind}, " +
                          $"goodwill {nowGoodwill}. (dry run, nothing changed.)"
                        : $"{target.def.defName} ('{target.Name}'): kind {wasKind} -> {nowKind}, " +
                          $"goodwill {wasGoodwill} -> {nowGoodwill}." +
                          (kindOk && goodwillOk
                              ? ""
                              : " ⚠️ READ-BACK DOES NOT MATCH THE REQUEST — the engine " +
                                "overrode it. Do not treat this faction as set."),
                    defName = target.def.defName,
                    factionName = target.Name,
                    dryRun,
                    kind = new { was = wasKind, now = nowKind, asked = wantKind ? parsed.ToString() : null, ok = kindOk },
                    goodwill = new { was = wasGoodwill, now = nowGoodwill, asked = wantGoodwill ? (int?)goodwill : null, ok = goodwillOk },
                    // The thing the caller actually wants to know before firing
                    // a raid, stated plainly rather than left to be derived.
                    hostileToPlayer = target.HostileTo(player),
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // What a BiomeDef DECLARES, as opposed to what it resolves to spawn.
        // The difference is the whole removal audit: a record zeroed to
        // commonality 0 vanishes from AllWildAnimals/AllWildPlants exactly like
        // a record that was deleted, and those are different defects.
        private struct DeclaredEntry
        {
            public string Kind;        // "animal" | "coastalAnimal" | "pollutionAnimal" | "plant"
            public float Commonality;
        }

        // The three animal lists are PRIVATE on BiomeDef, so reflection is the
        // only route — resolved once and cached, because this runs per biome and
        // a probe over every biome is 40+ calls. `wildPlants` is public and is
        // read directly; mixing the two styles is deliberate, not an oversight.
        private static System.Reflection.FieldInfo[] _biomeAnimalFields;

        private static Dictionary<string, DeclaredEntry> DeclaredBiomeEntries(BiomeDef b)
        {
            var outp = new Dictionary<string, DeclaredEntry>(StringComparer.OrdinalIgnoreCase);
            if (b == null) return outp;

            if (_biomeAnimalFields == null)
            {
                var flags = System.Reflection.BindingFlags.NonPublic
                          | System.Reflection.BindingFlags.Public
                          | System.Reflection.BindingFlags.Instance;
                _biomeAnimalFields = new[]
                {
                    typeof(BiomeDef).GetField("wildAnimals", flags),
                    typeof(BiomeDef).GetField("coastalWildAnimals", flags),
                    typeof(BiomeDef).GetField("pollutionWildAnimals", flags)
                };
            }

            var kinds = new[] { "animal", "coastalAnimal", "pollutionAnimal" };
            for (var i = 0; i < _biomeAnimalFields.Length; i++)
            {
                // A field that is not there is reported by ABSENCE of entries,
                // never by a silent empty dictionary that reads as "nothing
                // declared" — so a rename in a future RimWorld shows up as every
                // find returning `absent`, which is loud enough to notice.
                if (_biomeAnimalFields[i] == null) continue;
                if (!(_biomeAnimalFields[i].GetValue(b) is System.Collections.IEnumerable seq))
                    continue;
                foreach (var rec in seq)
                {
                    if (!(rec is BiomeAnimalRecord r) || r.animal == null) continue;
                    outp[r.animal.defName] = new DeclaredEntry
                    {
                        Kind = kinds[i], Commonality = r.commonality
                    };
                }
            }

            if (b.wildPlants != null)
                foreach (var r in b.wildPlants)
                {
                    if (r?.plant == null) continue;
                    outp[r.plant.defName] = new DeclaredEntry
                    {
                        Kind = "plant", Commonality = r.commonality
                    };
                }

            return outp;
        }

        // One connected water mass, with the shape numbers a sea gate is written
        // against. A class rather than a tuple so the flood fill reads as English
        // and so adding a field later does not renumber anything.
        private sealed class BodyShape
        {
            public int Tiles;
            // Edges to land or off-grid. Kept because it is a real measure of
            // frontier length; NOT the one the sea gate is written against.
            public int Perimeter;
            // Tiles with at least one land neighbour — the spec's definition,
            // and the one `raggedness` is computed from.
            public int PerimeterTiles;
            // Degrees, -90..90. Normalised to 0..1 at the point of reporting;
            // both are emitted, because the gate's band is a fraction and
            // shipping only degrees made a passing world read as a failure.
            public double CentroidLat;
        }

        // ---- jawa/world_tile_export internals --------------------------------
        // The column order, in ONE place. It is written into the CSV header, into
        // the JSON `columns` list and returned in the tool result, and the whole
        // point of the file is that a consumer can trust the join — three
        // hand-kept copies of the same list is exactly how that stops being true.
        private static readonly string[] TileColumns =
        {
            "tile", "lat", "long", "biome", "elevation",
            "temperature", "rainfall", "hilliness", "swampiness", "pollution"
        };

        // The extended set APPENDS to the base set and never reorders it, so a
        // consumer keyed on column NAME reads either file, and a consumer keyed on
        // POSITION still reads the base columns correctly. That is the whole
        // compatibility contract with vivify_world.py on the Python side.
        // ⚠️ 2026-08-24: `pollution` MOVED from position 13 to position 10 when it
        // was promoted into the base set. Name-keyed readers are unaffected; a
        // POSITION-keyed reader of an EXTENDED file written before that date will
        // now read tempMin where it expects pollution. vivify_world.py keys on
        // name (its COLS map) and was checked. Nothing else reads the extended form.
        private static readonly string[] TileColumnsExtended =
        {
            "tile", "lat", "long", "biome", "elevation",
            "temperature", "rainfall", "hilliness", "swampiness", "pollution",
            "tempMin", "tempMax", "seasonalShift", "riverDist",
            "feature", "featureId", "waterCovered", "roadCount", "riverCount",
            "mutatorCount"
        };

        // One surface tile, flattened. A struct in a flat array rather than a
        // list of objects: a full-coverage planet is ~119,904 of these, and this
        // array is built on the MAIN THREAD, where every allocation is a tick the
        // simulation does not get.
        private struct TileRow
        {
            public float Longitude;
            public float Latitude;
            public string Biome;
            public float Elevation;
            public float Temperature;
            public float Rainfall;
            public string Hilliness;
            public float Swampiness;

            // Extended set. Left at their defaults when extended=false, and never
            // written to the file in that case, so a default export is byte-identical
            // to what it was before this field group existed.
            public float TempMin;
            public float TempMax;
            public float SeasonalShift;
            public float Pollution;
            public int RiverDist;
            public string Feature;
            public int FeatureId;
            public bool WaterCovered;
            public int RoadCount;
            public int RiverCount;
            public int MutatorCount;
        }

        // What phase 1 hands to phase 2: the tiles plus the provenance that makes
        // their indices mean something.
        private sealed class TileHarvest
        {
            public TileRow[] Rows;
            public bool Extended;
            public bool Previewing;
            public string SeedString;
            public float PlanetCoverage;
        }

        // 🔴 InvariantCulture on every number, without exception. RimWorld runs
        // under the OS locale, and on a comma-decimal machine "0.35" is written
        // "0,35" — which does not merely look odd in a CSV, it shifts every
        // column after it by one and the file still parses. This is the single
        // most likely way this export could be silently wrong.
        private static string F(float v, string fmt) =>
            v.ToString(fmt, CultureInfo.InvariantCulture);

        // 4 decimals is ~11 m at the equator on a 100%-coverage planet, well
        // under a tile; the climate fields carry 4 too because rainfall runs to
        // thousands and temperature to one decimal in game.
        private const string LatLongFormat = "0.####";
        private const string ValueFormat = "0.####";

        private static void WriteTileCsv(
            TextWriter sw, TileHarvest harvest, CancellationToken cancellationToken)
        {
            var cols = harvest.Extended ? TileColumnsExtended : TileColumns;
            sw.Write(string.Join(",", cols));
            sw.Write('\n');
            var rows = harvest.Rows;
            for (var i = 0; i < rows.Length; i++)
            {
                if ((i & 4095) == 0) cancellationToken.ThrowIfCancellationRequested();
                var r = rows[i];
                sw.Write(i.ToString(CultureInfo.InvariantCulture));
                sw.Write(','); sw.Write(F(r.Latitude, LatLongFormat));
                sw.Write(','); sw.Write(F(r.Longitude, LatLongFormat));
                sw.Write(','); sw.Write(Csv(r.Biome));
                sw.Write(','); sw.Write(F(r.Elevation, ValueFormat));
                sw.Write(','); sw.Write(F(r.Temperature, ValueFormat));
                sw.Write(','); sw.Write(F(r.Rainfall, ValueFormat));
                sw.Write(','); sw.Write(Csv(r.Hilliness));
                sw.Write(','); sw.Write(F(r.Swampiness, ValueFormat));
                sw.Write(','); sw.Write(F(r.Pollution, ValueFormat));
                if (harvest.Extended)
                {
                    sw.Write(','); sw.Write(F(r.TempMin, ValueFormat));
                    sw.Write(','); sw.Write(F(r.TempMax, ValueFormat));
                    sw.Write(','); sw.Write(F(r.SeasonalShift, ValueFormat));
                    sw.Write(','); sw.Write(r.RiverDist.ToString(CultureInfo.InvariantCulture));
                    sw.Write(','); sw.Write(Csv(r.Feature));
                    sw.Write(','); sw.Write(r.FeatureId.ToString(CultureInfo.InvariantCulture));
                    // 0/1 rather than True/False: this is read by pandas and by csv.reader
                    // on the Python side, where "False" is a truthy non-empty string.
                    sw.Write(','); sw.Write(r.WaterCovered ? "1" : "0");
                    sw.Write(','); sw.Write(r.RoadCount.ToString(CultureInfo.InvariantCulture));
                    sw.Write(','); sw.Write(r.RiverCount.ToString(CultureInfo.InvariantCulture));
                    sw.Write(','); sw.Write(r.MutatorCount.ToString(CultureInfo.InvariantCulture));
                }
                // '\n' not Environment.NewLine: this file is read on the WSL
                // side by Python, and CRLF would ride into the last column of
                // every row unless the reader is told about it.
                sw.Write('\n');
            }
        }

        // A defName is an XML identifier and cannot contain a comma, so this
        // never fires on vanilla data. It exists because a modded biome defName
        // is not vanilla data, and a single stray comma would shift a column in
        // one row out of 119,904 — the hardest kind of corruption to notice.
        private static string Csv(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            if (s.IndexOf(',') < 0 && s.IndexOf('"') < 0 && s.IndexOf('\n') < 0) return s;
            return "\"" + s.Replace("\"", "\"\"") + "\"";
        }

        private static void WriteTileJson(
            TextWriter sw, TileHarvest harvest, CancellationToken cancellationToken)
        {
            // Provenance FIRST, so a `head` on a multi-MB file answers "which
            // world is this?" without reading the rest.
            sw.Write("{\"capturedUtc\":\"");
            sw.Write(DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture));
            sw.Write("\",\"seedString\":");
            sw.Write(Jstr(harvest.SeedString));
            sw.Write(",\"planetCoverage\":");
            sw.Write(F(harvest.PlanetCoverage, "0.####"));
            sw.Write(",\"previewOnly\":");
            sw.Write(harvest.Previewing ? "true" : "false");
            sw.Write(",\"layer\":\"surface\",\"tilesTotal\":");
            sw.Write(harvest.Rows.Length.ToString(CultureInfo.InvariantCulture));
            sw.Write(",\"columns\":[");
            for (var c = 0; c < TileColumns.Length; c++)
            {
                if (c > 0) sw.Write(',');
                sw.Write(Jstr(TileColumns[c]));
            }
            // Rows as ARRAYS, not objects. Nine repeated key names per tile is
            // roughly triple the file for information already in `columns`.
            sw.Write("],\"rows\":[");
            var rows = harvest.Rows;
            for (var i = 0; i < rows.Length; i++)
            {
                if ((i & 4095) == 0) cancellationToken.ThrowIfCancellationRequested();
                var r = rows[i];
                if (i > 0) sw.Write(',');
                sw.Write('[');
                sw.Write(i.ToString(CultureInfo.InvariantCulture));
                sw.Write(','); sw.Write(F(r.Latitude, LatLongFormat));
                sw.Write(','); sw.Write(F(r.Longitude, LatLongFormat));
                sw.Write(','); sw.Write(Jstr(r.Biome));
                sw.Write(','); sw.Write(F(r.Elevation, ValueFormat));
                sw.Write(','); sw.Write(F(r.Temperature, ValueFormat));
                sw.Write(','); sw.Write(F(r.Rainfall, ValueFormat));
                sw.Write(','); sw.Write(Jstr(r.Hilliness));
                sw.Write(','); sw.Write(F(r.Swampiness, ValueFormat));
                sw.Write(','); sw.Write(F(r.Pollution, ValueFormat));
                sw.Write(']');
            }
            sw.Write("]}");
        }

        // Minimal JSON string writer. Hand-rolled because this assembly has no
        // JSON dependency and pulling one in for eight short identifier fields
        // would be the larger risk.
        private static string Jstr(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (var ch in s)
            {
                if (ch == '"' || ch == '\\') { sb.Append('\\').Append(ch); }
                else if (ch == '\n') sb.Append("\\n");
                else if (ch == '\r') sb.Append("\\r");
                else if (ch == '\t') sb.Append("\\t");
                else if (ch < ' ') sb.Append("\\u").Append(((int)ch).ToString("x4"));
                else sb.Append(ch);
            }
            sb.Append('"');
            return sb.ToString();
        }

        // A seed is arbitrary player-typed text and lands in a FILENAME here, so
        // it is filtered rather than trusted. Anything not [A-Za-z0-9._-] becomes
        // '_', and an empty or absent seed becomes "unseeded" rather than a file
        // called "world_tiles_.csv".
        private static string SanitiseForFileName(string seed)
        {
            if (string.IsNullOrWhiteSpace(seed)) return "unseeded";
            var sb = new StringBuilder(seed.Length);
            foreach (var ch in seed)
            {
                var ok = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z')
                         || (ch >= '0' && ch <= '9') || ch == '.' || ch == '_' || ch == '-';
                sb.Append(ok ? ch : '_');
            }
            // Long seeds are legal; a 260-char Windows path is not.
            var s = sb.ToString();
            return s.Length > 48 ? s.Substring(0, 48) : s;
        }

        // ---- Vehicle Framework, reached by reflection -------------------------
        // Resolved once and cached. `null` means the framework is not loaded,
        // which is a legitimate state and not an error until someone asks for a
        // vehicle.
        private static bool _vfProbed;
        private static Type _vehicleDefType;
        private static System.Reflection.MethodInfo _spawnVehicleRandomized;

        private static void ProbeVehicleFramework()
        {
            if (_vfProbed) return;
            _vfProbed = true;
            _vehicleDefType = GenTypes.GetTypeInAnyAssembly("Vehicles.VehicleDef");
            var spawner = GenTypes.GetTypeInAnyAssembly("Vehicles.VehicleSpawner");
            if (spawner == null) return;
            // Signature read from Vehicles.dll v1.6.2144 with ilprobe sigdump:
            //   public static VehiclePawn SpawnVehicleRandomized(
            //       VehicleDef, IntVec3, Map, Faction, Nullable<Rot4>, bool)
            // Matched by NAME AND PARAMETER COUNT rather than by exact types,
            // because Nullable<Rot4> cannot be named here without the reference --
            // and an overload set of one makes the ambiguity moot.
            foreach (var m in spawner.GetMethods(System.Reflection.BindingFlags.Public
                                                 | System.Reflection.BindingFlags.Static))
            {
                if (m.Name != "SpawnVehicleRandomized") continue;
                if (m.GetParameters().Length != 6) continue;
                _spawnVehicleRandomized = m;
                break;
            }
        }

        private static bool IsVehicleDef(ThingDef def)
        {
            ProbeVehicleFramework();
            return _vehicleDefType != null && def != null
                   && _vehicleDefType.IsInstanceOfType(def);
        }

        private static Thing TrySpawnVehicle(ThingDef def, IntVec3 cell, Map map,
                                             Rot4 rot, out string error)
        {
            error = null;
            ProbeVehicleFramework();
            if (_spawnVehicleRandomized == null)
            {
                error = "'" + def.defName + "' is a Vehicles.VehicleDef but " +
                        "Vehicles.VehicleSpawner.SpawnVehicleRandomized could not be " +
                        "resolved. Vehicle Framework is not loaded, or its signature " +
                        "changed. NOTHING was spawned.";
                return null;
            }
            try
            {
                // ⚠️ A non-null Faction is deliberate. SetFactionDirect tolerates
                // null, and then SpawnSetup takes the not-player branch: the
                // vehicle auto-drafts and turrets acquire it. A test prop that
                // shoots at the colony is not a test prop.
                var pawn = _spawnVehicleRandomized.Invoke(null, new object[]
                {
                    def, cell, map, Faction.OfPlayer, rot, false
                }) as Thing;
                if (pawn == null || !pawn.Spawned)
                {
                    error = "VehicleSpawner returned " +
                            (pawn == null ? "null" : "an unspawned vehicle") +
                            " — success cannot be claimed from the call returning.";
                    return null;
                }
                return pawn;
            }
            catch (Exception e)
            {
                var inner = e.InnerException ?? e;
                error = "VehicleSpawner threw " + inner.GetType().Name + ": " +
                        inner.Message;
                return null;
            }
        }

        // 🔴 THE ONE LINE THAT KILLED EVERY TOOL AT THE MAIN MENU.
        //
        // Every tool used to end `ticksGame = Find.TickManager?.TicksGame ?? -1`.
        // That LOOKS null-guarded and is not: `Find.TickManager` compiles to
        // `call Current::get_Game` then `ldfld Game::tickManager`, with no null
        // check — so with no game loaded the GETTER throws before `?.` is ever
        // reached. The operator protects the value returned, not the call that
        // produces it.
        //
        // MEASURED LIVE 2026-08-14 at `programState: Entry`, which is what
        // turned this from a read of the IL into a fact: `jawa/get_defs` on two
        // RulePackDefs returned a bare NullReferenceException at
        // `<GetDefs>b__2 [0x002d4]` — the response-construction line, NOT the
        // def lookup. ⚠️ **The defs had resolved. The tool threw away a correct
        // answer while packing it**, and reported only "Object reference not set
        // to an instance of an object", naming nothing.
        //
        // Defs are fully loaded at the main menu, so the whole class of
        // "check a def, no game needed" work was unreachable for want of this.
        // Guard the OWNER, not the result, in one place so it cannot be got
        // wrong per-tool. `&&` short-circuits, so `Find.TickManager` is only
        // touched once `Current.Game` is known non-null.

        // ------------------------------------------------------------------
        // jawa/world_neighbors - the one number offline world editing cannot get.
        //
        // WHY: rivers and roads in the save are (origin tile, ADJACENCY SLOT, def),
        // and the slot indexes RimWorld's own neighbour list for that tile. Offline
        // I proved two things about it and could get no further:
        //   * the ordering is ANGULAR - over every tile carrying two links, the slot
        //     difference is only ever 2 or 3, never 0/1/4/5, so a river bends 120 or
        //     180 degrees and never doubles back. Only an angular order does that.
        //   * the rotation is PER TILE - rivers and roads pick different global
        //     offsets, and solving it from the engine's own links gives zero unique
        //     solutions because every constrained case is symmetric.
        // So the ordering has to come from the engine. This dumps it, once, for
        // every tile. The answer is a property of the GRID (subdivisions + coverage),
        // not of a particular world, so one dump serves every world of that shape.
        [Tool(
            "jawa/world_neighbors",
            Description =
                "Dump RimWorld's OWN neighbour ordering for every world tile to a CSV: " +
                "one row per tile, the neighbour tile IDs in the exact order " +
                "WorldGrid returns them. This is the key that lets an offline editor " +
                "AUTHOR rivers and roads instead of only deleting them, because their " +
                "save format stores a link as an index into this ordering.",
            ResultDescription =
                "Returns success, path, tiles, and the neighbour counts seen - a geodesic " +
                "sphere must show exactly 12 tiles with 5 neighbours and the rest with 6, " +
                "which is a self-check on the dump.")]
        public static async Task<object> WorldNeighbors(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Output CSV path. Absolute path recommended; its directory is created.")]
            string path = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null || Find.WorldGrid == null)
                    return Fail("No world is loaded. Load or generate a world first.");

                var grid = Find.WorldGrid;
                int count = grid.TilesCount;
                var outPath = string.IsNullOrEmpty(path)
                    ? Path.Combine(GenFilePaths.SaveDataFolderPath, "world_neighbors.csv")
                    : path;
                var dir = Path.GetDirectoryName(outPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                var sb = new StringBuilder();
                sb.Append("tile,n0,n1,n2,n3,n4,n5\n");
                // 1.6 replaced the bare int tile id with RimWorld.Planet.PlanetTile
                // (the world is layered now - surface, orbit - so a tile carries its
                // layer). The compiler caught this; nothing here was guessed.
                var buf = new List<RimWorld.Planet.PlanetTile>();
                var degrees = new Dictionary<int, int>();
                for (int i = 0; i < count; i++)
                {
                    buf.Clear();
                    grid.GetTileNeighbors(i, buf);
                    int d = buf.Count;
                    degrees[d] = degrees.TryGetValue(d, out var had) ? had + 1 : 1;
                    sb.Append(i.ToString(CultureInfo.InvariantCulture));
                    for (int k = 0; k < 6; k++)
                    {
                        sb.Append(',');
                        sb.Append((k < d ? buf[k].tileId : -1).ToString(CultureInfo.InvariantCulture));
                    }
                    sb.Append('\n');
                }
                File.WriteAllText(outPath, sb.ToString());

                return (object)new
                {
                    success = true,
                    path = outPath,
                    tiles = count,
                    degrees = degrees.OrderBy(kv => kv.Key)
                                     .Select(kv => new { neighbours = kv.Key, tiles = kv.Value })
                                     .ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        private static int TicksGameSafe() =>
            Current.Game != null && Find.TickManager != null
                ? Find.TickManager.TicksGame
                : -1;

        private static object Fail(string message, object extra = null) =>
            new { success = false, message, details = extra };
    }
}
