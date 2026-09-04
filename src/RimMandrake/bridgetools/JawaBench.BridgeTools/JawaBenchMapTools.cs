// JawaBenchMapTools.cs - the MAP half of the companion's newer surface.
//
// JawaBenchTerrainTools.cs (6,199 lines) holds the original 32 tools.
// JawaBenchWorldTools.cs holds the 25 planet tools.
// This file holds the map-level foundation the owner asked for on 2026-08-19:
// substructure, the five terrain layers, buildings, prefabs and the grids.
//
// EVERY SIGNATURE READ FROM 1.6 SOURCE, NOT REMEMBERED. Census:
//   design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md
//
// THE FOUR FACTS THAT SHAPE THIS FILE
// ===================================
//  1. 1.6 has FIVE terrain layers - top, under, FOUNDATION, TEMP - plus a colour
//     grid. The old set_terrain tools only ever reached `top`.
//  2. SUBSTRUCTURE IS NOT A GRID. It is a foundation-layer TerrainDef living in
//     TerrainGrid.foundationGrid. Map.substructureGrid is only an overlay drawer
//     whose one state-changing method is MarkDirty(). Odyssey-gated.
//  3. Nothing bulk-written is consistent until map_commit runs - the map twin of
//     world_commit.
//  4. ThingMaker.MakeThing already calls PostMake, which RANDOMISES HitPoints from
//     def.startingHpRange. Set HitPoints AFTER or buildings spawn damaged.
//
// Thread affinity, same rule as the rest: everything touching game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared map helpers -------------------------------------------------

        private static Map MapOrNull(out string err)
        {
            err = null;
            var m = Find.CurrentMap;
            if (m == null) { err = "No current map. These tools are map-scoped; use the planet-scoped world tool family instead."; return null; }
            return m;
        }

        private static bool TryRect(string rect, Map map, out CellRect r, out string err)
        {
            r = default(CellRect); err = null;
            if (string.IsNullOrEmpty(rect)) { err = "Give a rect as 'x,z,w,h'."; return false; }
            var b = rect.Split(',');
            int x, z, w, h;
            if (b.Length != 4 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z)
                || !int.TryParse(b[2].Trim(), out w) || !int.TryParse(b[3].Trim(), out h))
            { err = "Bad rect '" + rect + "', expected 'x,z,w,h'."; return false; }
            if (w < 1) w = 1;
            if (h < 1) h = 1;
            r = new CellRect(x, z, w, h).ClipInsideMap(map);
            return true;
        }

        // ================================================================
        //  M1 - map_commit. The map twin of world_commit.
        // ================================================================
        [Tool(
            "jawa/map_commit",
            Description =
                "Make bulk MAP edits consistent and visible - the map-side twin of " +
                "jawa/world_commit. Call ONCE after a batch of terrain, substructure, " +
                "building or grid writes, never per write. " +
                "Runs, in order: regionAndRoomUpdater.RebuildAllRegionsAndRooms (which also " +
                "resets the temperature/vacuum cache); pathing.RecalculateAllPerceivedPathCosts; " +
                "reachability.ClearCache; powerNetManager.UpdatePowerNetsAndConnections_First " +
                "(the Notify_* calls only QUEUE delayed actions - this is the flush); and " +
                "mapDrawer.WholeMapChanged over Buildings|Things|Terrain|Roofs|GroundGlow|Snow|PowerGrid. " +
                "Most of what a spawn needs is already automatic in Thing.SpawnSetup - this " +
                "covers the parts that are not.",
            ResultDescription = "success, steps[] each with ok/skipped/failed.")]
        public static async Task<object> MapCommit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rebuild regions and rooms. Default true.")] bool regions = true,
            [ToolParameter(Description = "Recalculate path costs and clear reachability. Default true.")] bool pathing = true,
            [ToolParameter(Description = "Flush queued power-net rebuilds. Default true.")] bool power = true,
            [ToolParameter(Description = "Redraw map meshes. Default true.")] bool redraw = true,
            [ToolParameter(Description = "Use RegenerateEverythingNow instead of a targeted WholeMapChanged.")] bool full = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                var steps = new List<object>();
                Action<string, Action> step = (name, act) =>
                {
                    try { act(); steps.Add(new { step = name, status = "ok" }); }
                    catch (Exception e) { steps.Add(new { step = name, status = "failed", error = e.GetType().Name + ": " + e.Message }); }
                };

                if (regions)
                {
                    step("regionAndRoomUpdater.Enabled = true", () => map.regionAndRoomUpdater.Enabled = true);
                    step("RebuildAllRegionsAndRooms", () => map.regionAndRoomUpdater.RebuildAllRegionsAndRooms());
                }
                else steps.Add(new { step = "regions", status = "skipped" });

                if (pathing)
                {
                    step("pathing.RecalculateAllPerceivedPathCosts", () => map.pathing.RecalculateAllPerceivedPathCosts());
                    step("reachability.ClearCache", () => map.reachability.ClearCache());
                }
                else steps.Add(new { step = "pathing", status = "skipped" });

                if (power)
                    step("powerNetManager.UpdatePowerNetsAndConnections_First",
                        () => map.powerNetManager.UpdatePowerNetsAndConnections_First());
                else steps.Add(new { step = "power", status = "skipped" });

                if (redraw)
                {
                    if (full) step("mapDrawer.RegenerateEverythingNow", () => map.mapDrawer.RegenerateEverythingNow());
                    else
                        step("mapDrawer.WholeMapChanged", () =>
                        {
                            ulong flags = (ulong)MapMeshFlagDefOf.Buildings
                                        | (ulong)MapMeshFlagDefOf.Things
                                        | (ulong)MapMeshFlagDefOf.Terrain
                                        | (ulong)MapMeshFlagDefOf.Roofs
                                        | (ulong)MapMeshFlagDefOf.GroundGlow
                                        | (ulong)MapMeshFlagDefOf.Snow
                                        | (ulong)MapMeshFlagDefOf.PowerGrid;
                            map.mapDrawer.WholeMapChanged(flags);
                        });
                }
                else steps.Add(new { step = "redraw", status = "skipped" });

                int failed = steps.Count(o => (o.GetType().GetProperty("status").GetValue(o, null) as string) == "failed");
                return (object)new
                {
                    success = failed == 0,
                    failedSteps = failed,
                    map = map.Index,
                    mapSize = new { x = map.Size.x, z = map.Size.z, area = map.Area },
                    note = "Thing.SpawnSetup already handles listers, thingGrid, edificeGrid, coverGrid, linkGrid, glowGrid, fertility, snow/sand, temperature, gas, zones and per-cell mesh dirtying. This covers the rest.",
                    steps,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  M1 - the five terrain layers, and SUBSTRUCTURE
        // ================================================================
        [Tool(
            "jawa/get_terrain_layers",
            Description =
                "Read ALL FIVE terrain layers plus the colour at map cells: top, under, " +
                "FOUNDATION (where substructure lives), TEMP (Odyssey ice/mud) and the base " +
                "terrain, plus whether the cell counts as substructure. The existing " +
                "jawa/get_terrain_batch only ever reads the TOP layer, so it cannot see a " +
                "floor laid over substructure. Read-only.",
            ResultDescription = "success, count, cells[] with top/under/foundation/temp/base/color/isSubstructure.")]
        public static async Task<object> GetTerrainLayers(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Max cells returned. Default 200.")] int limit = 200,
            [ToolParameter(Description = "Only cells that carry a foundation.")] bool onlyFoundation = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                var tg = map.terrainGrid;
                var outp = new List<object>();
                int foundationCells = 0, substructureCells = 0, scanned = 0;
                // 🔴 GET_TERRAIN_LAYERS_TRUNCATION_UNFLAGGED_1. `limit` capped cells[] with
                // NOTHING in the body to say it had - and `cellsScanned` vs `returned` cannot
                // stand in for it, because onlyFoundation filters between the two, so a rect
                // of 4000 cells holding 300 foundations returned 200 rows and the caller
                // could not tell 200-of-300 from 200-of-200. Count the rows that PASSED THE
                // FILTER and say outright whether the list is short. jawa/build_check already
                // reports `truncated`; this one did not.
                int matched = 0;

                foreach (var c in r)
                {
                    scanned++;
                    TerrainDef top = null, under = null, foundation = null, temp = null, baseT = null;
                    try { top = tg.TopTerrainAt(c); } catch { }
                    try { under = tg.UnderTerrainAt(c); } catch { }
                    try { foundation = tg.FoundationAt(c); } catch { }
                    try { temp = tg.TempTerrainAt(c); } catch { }
                    try { baseT = tg.BaseTerrainAt(c); } catch { }

                    bool isSub = foundation != null && foundation.IsSubstructure;
                    if (foundation != null) foundationCells++;
                    if (isSub) substructureCells++;
                    if (onlyFoundation && foundation == null) continue;
                    matched++;
                    if (outp.Count >= Math.Max(1, limit)) continue;

                    outp.Add(new
                    {
                        x = c.x, z = c.z,
                        top = top != null ? top.defName : null,
                        under = under != null ? under.defName : null,
                        foundation = foundation != null ? foundation.defName : null,
                        temp = temp != null ? temp.defName : null,
                        baseTerrain = baseT != null ? baseT.defName : null,
                        isSubstructure = isSub,
                    });
                }

                return (object)new
                {
                    success = true,
                    cellsScanned = scanned,
                    cellsMatchingFilter = matched,
                    returned = outp.Count,
                    limit = Math.Max(1, limit),
                    truncated = matched > outp.Count,
                    foundationCells,
                    substructureCells,
                    odysseyActive = ModsConfig.OdysseyActive,
                    cells = outp,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_substructure_batch",
            Description =
                "Lay or strip SUBSTRUCTURE over a rect. Substructure is not a grid - it is a " +
                "foundation-layer TerrainDef (TerrainDefOf.Substructure) in " +
                "TerrainGrid.foundationGrid, and it is what gravship buildings require. " +
                "action='set' lays it, action='remove' strips the foundation layer. " +
                "⚠️ SetFoundation errors if the cell already has UNDER-terrain, so cells " +
                "with a floor over natural ground are reported as refused rather than " +
                "silently skipped. Odyssey only. Call jawa/map_commit afterwards.",
            ResultDescription = "success, changed, refused[], and a read-back sample.")]
        public static async Task<object> SetSubstructureBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'set' or 'remove'.")] string action = "set",
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Leave rubble when removing. Default true.")] bool doLeavings = true,
            [ToolParameter(Description = "Read back at most this many cells. Default 6.")] int readBack = 6)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.OdysseyActive)
                    return Fail("Odyssey is not active. Substructure does not exist in this game - TerrainDefOf.Substructure would be null.");

                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                bool set = string.Equals(action, "set", StringComparison.OrdinalIgnoreCase);
                bool rem = string.Equals(action, "remove", StringComparison.OrdinalIgnoreCase);
                if (!set && !rem) return Fail("action must be 'set' or 'remove'.");

                var sub = TerrainDefOf.Substructure;
                if (set && sub == null) return Fail("TerrainDefOf.Substructure resolved null even though Odyssey reports active.");

                var tg = map.terrainGrid;
                int changed = 0;
                // 🔴 SET_SUBSTRUCTURE_REFUSEDCOUNT_CAPPED_1. `refused` is capped at 20
                // entries so the response body stays small, but `refusedCount` used to be
                // `refused.Count` - the SAME capped list - so a rect refusing 400 cells
                // reported refusedCount:20 as if that were the true total. refusedTotal is
                // incremented on every refusal, uncapped; the list stays capped for display.
                int refusedTotal = 0;
                var refused = new List<object>();
                Action<int, int, string> addRefused = (cx, cz, why) =>
                {
                    refusedTotal++;
                    if (refused.Count < 20) refused.Add(new { x = cx, z = cz, why });
                };
                // 🔴 SET_SUBSTRUCTURE_REMOVE_SKIPS_SILENTLY_1. action='remove' over a rect
                // whose cells carry no foundation used to `continue` with no trace at all:
                // the response read changed:0, refusedCount:0, cellsInRect:400, and there
                // was nothing in it to say WHY nothing happened - indistinguishable from a
                // rect the tool never visited. It is not a refusal (there was nothing to
                // remove), so it gets its own counter rather than inflating refused[].
                int nothingToRemove = 0;

                foreach (var c in r)
                {
                    try
                    {
                        if (set)
                        {
                            // SetFoundation errors when under-terrain is present; check first
                            // so the caller gets a reason instead of a red log line.
                            if (tg.UnderTerrainAt(c) != null)
                            { addRefused(c.x, c.z, "cell has under-terrain; strip the floor first"); continue; }
                            tg.SetFoundation(c, sub);
                            changed++;
                        }
                        else
                        {
                            if (tg.FoundationAt(c) == null) { nothingToRemove++; continue; }
                            if (!tg.CanRemoveFoundationAt(c))
                            { addRefused(c.x, c.z, "CanRemoveFoundationAt false"); continue; }
                            tg.RemoveFoundation(c, doLeavings);
                            changed++;
                        }
                    }
                    catch (Exception e)
                    {
                        addRefused(c.x, c.z, e.GetType().Name + ": " + e.Message);
                    }
                }

                try { if (map.substructureGrid != null) map.substructureGrid.MarkDirty(); } catch { }

                var back = new List<object>();
                foreach (var c in r)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    var f = tg.FoundationAt(c);
                    back.Add(new { x = c.x, z = c.z, foundation = f != null ? f.defName : null, isSubstructure = f != null && f.IsSubstructure });
                }

                return (object)new
                {
                    success = true,
                    action, changed,
                    cellsInRect = r.Area,
                    cellsWithNoFoundation = nothingToRemove,
                    refusedCount = refusedTotal,
                    refusedListTruncated = refusedTotal > refused.Count,
                    refused,
                    note = "substructureGrid.MarkDirty() called. Run jawa/map_commit for regions, pathing and the mesh.",
                    cells = back,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_terrain_layer",
            Description =
                "Write the UNDER, TEMP or COLOUR terrain layer over a rect - the layers the " +
                "original jawa/set_terrain cannot reach. layer='under' sets terrain beneath a " +
                "floor; layer='temp' sets Odyssey temporary terrain (the def must have " +
                "temporary=true) and optionally queues its expiry tick; layer='color' " +
                "recolours the floor with a ColorDef. layer='removeTop' strips one layer off " +
                "the stack (floor -> under -> foundation) with the engine's own guard. " +
                "Call jawa/map_commit afterwards.",
            ResultDescription = "success, changed, refused[], read-back sample.")]
        public static async Task<object> SetTerrainLayer(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'under' | 'temp' | 'color' | 'removeTop'.")] string layer = "under",
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "TerrainDef (under/temp) or ColorDef (color). Ignored for removeTop.")] string def = null,
            [ToolParameter(Description = "For temp: ticks from now to auto-remove. 0 = never.")] int expireInTicks = 0,
            [ToolParameter(Description = "Leave rubble on removeTop. Default true.")] bool doLeavings = true,
            [ToolParameter(Description = "Read back at most this many cells. Default 6.")] int readBack = 6)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                var tg = map.terrainGrid;
                string L = (layer ?? "").Trim().ToLowerInvariant();
                TerrainDef td = null; ColorDef cd = null;

                if (L == "under" || L == "temp")
                {
                    if (string.IsNullOrEmpty(def)) return Fail("Give a TerrainDef.");
                    td = DefDatabase<TerrainDef>.GetNamedSilentFail(def.Trim());
                    if (td == null) return Fail("No TerrainDef '" + def + "'.", DefSuggestions<TerrainDef>(def));
                    if (L == "temp" && !td.temporary)
                        return Fail("TerrainDef '" + td.defName + "' is not temporary=true, so it cannot go in the temp layer.");
                }
                else if (L == "color")
                {
                    if (string.IsNullOrEmpty(def)) return Fail("Give a ColorDef.");
                    cd = DefDatabase<ColorDef>.GetNamedSilentFail(def.Trim());
                    if (cd == null) return Fail("No ColorDef '" + def + "'.", DefSuggestions<ColorDef>(def));
                }
                else if (L != "removetop") return Fail("layer must be under|temp|color|removeTop.");

                int changed = 0;
                // 🔴 SET_TERRAIN_LAYER_REFUSEDCOUNT_CAPPED_1. Same trap as
                // jawa/set_substructure_batch: `refused` is capped at 20 for display, and
                // `refusedCount` used to just be refused.Count - so a removeTop pass that
                // refused 300 cells reported refusedCount:20. Count every refusal, cap only
                // the list shown back.
                int refusedTotal = 0;
                int expiryDropped = 0;
                var refused = new List<object>();
                Action<int, int, string> addRefused = (cx, cz, why) =>
                {
                    refusedTotal++;
                    if (refused.Count < 20) refused.Add(new { x = cx, z = cz, why });
                };
                foreach (var c in r)
                {
                    try
                    {
                        switch (L)
                        {
                            case "under": tg.SetUnderTerrain(c, td); changed++; break;
                            case "temp":
                                tg.SetTempTerrain(c, td); changed++;
                                // 🔴 SET_TERRAIN_LAYER_EXPIRY_SILENTLY_DROPPED_1. When
                                // map.tempTerrain is null the `&&` below skipped the queue and
                                // the cell still counted as changed, so a caller who asked for
                                // terrain lasting 500 ticks got PERMANENT temp terrain and a
                                // clean success. Count the drops and report them.
                                if (expireInTicks > 0 && map.tempTerrain == null) expiryDropped++;
                                if (expireInTicks > 0 && map.tempTerrain != null)
                                    // Clamped because the sum is an int and it is SAVED:
                                    // TempTerrainManager writes the absolute tick into
                                    // terrainToRemoveTicks, and an overflowed one goes
                                    // negative, which the queue reads as "already due" - the
                                    // terrain vanishes on the next tick instead of lasting
                                    // longer. 36,000,000 ticks is 600 in-game days.
                                    map.tempTerrain.QueueRemoveTerrain(c,
                                        Find.TickManager.TicksGame + Math.Min(expireInTicks, 36000000));
                                break;
                            case "color": tg.SetTerrainColor(c, cd); changed++; break;
                            case "removetop":
                                if (!tg.CanRemoveTopLayerAt(c))
                                { addRefused(c.x, c.z, "CanRemoveTopLayerAt false"); break; }
                                tg.RemoveTopLayer(c, doLeavings); changed++;
                                break;
                        }
                    }
                    catch (Exception e)
                    { addRefused(c.x, c.z, e.GetType().Name + ": " + e.Message); }
                }

                var back = new List<object>();
                foreach (var c in r)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    var top = tg.TopTerrainAt(c); var un = tg.UnderTerrainAt(c);
                    var fo = tg.FoundationAt(c); var tp = tg.TempTerrainAt(c);
                    back.Add(new
                    {
                        x = c.x, z = c.z,
                        top = top != null ? top.defName : null,
                        under = un != null ? un.defName : null,
                        foundation = fo != null ? fo.defName : null,
                        temp = tp != null ? tp.defName : null,
                    });
                }

                return (object)new
                {
                    success = true, layer = L, changed, cellsInRect = r.Area,
                    refusedCount = refusedTotal,
                    refusedListTruncated = refusedTotal > refused.Count,
                    refused,
                    expiryDropped,
                    expiryNote = expiryDropped > 0
                        ? "expireInTicks was IGNORED on " + expiryDropped + " cell(s): this map has no tempTerrain manager, "
                          + "so that terrain is PERMANENT until something else removes it."
                        : null,
                    note = "Run jawa/map_commit.",
                    cells = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  M4 - MAP GRIDS: fog, snow, sand, deep resource, gas
        //  🔑 sandGrid is new in 1.6 and is the twin of snowGrid - dune piling.
        //  DLC gates are REPORTED, never thrown.
        // ================================================================
        [Tool(
            "jawa/set_fog",
            Description =
                "Reveal or re-hide map cells. action='unfog' clears fog over a rect, " +
                "'unfogAll' clears the whole map, 'refog' hides a rect again, and " +
                "'floodUnfog' reveals the contiguous room/area containing a cell the way " +
                "walking into it would. Revealing is usually a prerequisite for " +
                "photographing anything the colony has not visited.",
            ResultDescription = "success, action, cellsChanged, fogged/unfogged counts after.")]
        public static async Task<object> SetFog(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'unfog' | 'unfogAll' | 'refog' | 'floodUnfog'.")] string action = "unfog",
            [ToolParameter(Description = "Rect 'x,z,w,h' for unfog/refog.")] string rect = null,
            [ToolParameter(Description = "Cell 'x,z' for floodUnfog.")] string cell = null,
            [ToolParameter(Description = "Send the discovery letters on floodUnfog. Default false.")] bool sendLetters = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var fg = map.fogGrid;
                string A = (action ?? "").Trim().ToLowerInvariant();

                // 🔴 SET_FOG_ERROR_PRECEDENCE_1. An unrecognised action fell through to the
                // rect branch, and that branch validated `rect` FIRST - so action='clear'
                // (or any typo) with no rect was answered "Give a rect as 'x,z,w,h'.", which
                // sends the caller hunting for a coordinate bug while the real fault is the
                // action name it never got told about. Two full-map fog censuses also ran
                // for an action that was never going to execute. Validate the action before
                // anything else looks at the map - the same up-front gate
                // jawa/set_weather_buildup's mode and jawa/designate_batch's action have.
                if (A != "unfog" && A != "unfogall" && A != "refog" && A != "floodunfog")
                    return Fail("action must be unfog|unfogAll|refog|floodUnfog, got '" + action + "'.");

                // 🔴 COUNT, do not assume. unfogAll used to report map.Area and refog the
                // whole rect area, whatever the fog had actually been - FogGrid.ClearAllFog
                // and FogGrid.Refog both flip only the cells whose state differs, so a refog
                // over already-fogged ground reported hundreds of cells changed and did
                // nothing. floodUnfog reported -1 because "the engine decides", which the
                // engine does - and a before/after count is how you read its answer.
                int foggedBefore = 0;
                foreach (var c in map.AllCells) if (fg.IsFogged(c)) foggedBefore++;

                try
                {
                    if (A == "unfogall") fg.ClearAllFog();
                    else if (A == "floodunfog")
                    {
                        int x, z;
                        var b = (cell ?? "").Split(',');
                        if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                            return Fail("Give cell as 'x,z' for floodUnfog.");
                        var c0 = new IntVec3(x, 0, z);
                        // CellToIndex wraps rather than throwing: x=-1 resolves to a real cell
                        // one row down, so an unchecked out-of-bounds cell unfogs the WRONG
                        // place and reports success.
                        if (!c0.InBounds(map))
                            return Fail("Cell " + x + "," + z + " is out of bounds. This map is " +
                                        map.Size.x + " x " + map.Size.z + ".");
                        fg.FloodUnfogAdjacent(c0, sendLetters);
                    }
                    else
                    {
                        CellRect r;
                        if (!TryRect(rect, map, out r, out err)) return Fail(err);
                        // Only 'unfog' and 'refog' can reach here - the action was validated
                        // above, so there is no fall-through branch left to write.
                        if (A == "unfog") { foreach (var c in r) if (fg.IsFogged(c)) fg.Unfog(c); }
                        else fg.Refog(r);
                    }
                }
                catch (Exception e) { return Fail("Fog op failed: " + e.GetType().Name + ": " + e.Message); }

                int fogged = 0;
                foreach (var c in map.AllCells) if (fg.IsFogged(c)) fogged++;

                return (object)new
                {
                    success = true, action = A,
                    cellsChanged = Math.Abs(fogged - foggedBefore),
                    foggedCellsBefore = foggedBefore,
                    foggedCellsNow = fogged, mapArea = map.Area,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_weather_buildup",
            Description =
                "Pile or clear SNOW and (Odyssey) SAND depth on map cells - the two grids are " +
                "twins. kind='snow' or 'sand'; mode='set' writes an absolute depth 0-1, " +
                "'add' offsets it, 'radial' piles it in a circle the way weather does. " +
                "Sand is Odyssey-only and the gate is REPORTED, not thrown.",
            ResultDescription = "success, kind, cellsChanged, sample depths after.")]
        public static async Task<object> SetWeatherBuildup(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'snow' or 'sand'.")] string kind = "snow",
            [ToolParameter(Description = "'set' | 'add' | 'radial'.")] string mode = "set",
            [ToolParameter(Description = "Rect 'x,z,w,h' for set/add.")] string rect = null,
            [ToolParameter(Description = "Centre 'x,z' for radial.")] string center = null,
            [ToolParameter(Description = "Radius for radial.")] float radius = 8f,
            [ToolParameter(Description = "Depth 0-1 (set) or delta (add/radial).")] float depth = 0.5f,
            [ToolParameter(Description = "Read back at most this many cells. Default 5.")] int readBack = 5)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                bool sand = string.Equals(kind, "sand", StringComparison.OrdinalIgnoreCase);
                if (sand && !ModsConfig.OdysseyActive)
                    return Fail("Sand requires Odyssey, which is not active. The snowGrid is always available; sandGrid is not.");

                string M = (mode ?? "").Trim().ToLowerInvariant();
                // Every value that is not 'add' or 'radial' used to fall through to SetDepth,
                // so a typo silently wrote an ABSOLUTE depth over the whole rect - the same
                // trap jawa/designate_batch already closed on its own action parameter.
                if (M != "set" && M != "add" && M != "radial")
                    return Fail("mode must be set|add|radial, got '" + mode + "'.");
                int changed = 0, unchanged = 0;
                IntVec3 radialCenter = IntVec3.Invalid;
                // 🔴 SET_WEATHER_BUILDUP_SILENT_ZERO_COUNTED_1. SnowGrid.SetDepth forces
                // newDepth to 0 whenever CanHaveSnow is false - a full-fillage building in the
                // cell, or terrain with holdSnowOrSand=false (all water, and every bridge) -
                // and it does so WITHOUT a log line. AddDepth does the same and also early-
                // returns at the 0/1 rails. `changed++` used to run for every cell regardless,
                // so a drift laid over a walled room or a lake reported the whole rect piled
                // and the grid held zeroes. Count what the grid actually did, name the cells
                // that refused, exactly as jawa/set_gas does for GasCanMoveTo.
                int refusedTotal = 0;
                var refused = new List<object>();
                Action<int, int, string> addRefused = (cx, cz, why) =>
                {
                    refusedTotal++;
                    if (refused.Count < 20) refused.Add(new { x = cx, z = cz, why });
                };

                try
                {
                    if (M == "radial")
                    {
                        int x, z; var b = (center ?? "").Split(',');
                        if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                            return Fail("Give centre as 'x,z' for radial.");
                        var c0 = new IntVec3(x, 0, z);
                        // 🔴 SET_WEATHER_BUILDUP_RADIAL_CENTRE_UNCHECKED_1. AddSnowRadial and
                        // AddSandRadial bounds-check every cell they touch and skip the rest
                        // in silence, so a centre off the map piled NOTHING while the tool
                        // answered success with cellsChanged:-1 and an empty cells[] - and an
                        // empty cells[] is exactly what a pile it merely could not sample
                        // looks like. jawa/set_fog already guards its own cell this way.
                        if (!c0.InBounds(map))
                            return Fail("Centre " + x + "," + z + " is out of bounds. This map is " +
                                        map.Size.x + " x " + map.Size.z + " (x 0.." + (map.Size.x - 1) +
                                        ", z 0.." + (map.Size.z - 1) + "). AddSnowRadial/AddSandRadial skip " +
                                        "out-of-bounds cells silently, so nothing would have been piled.");
                        if (radius <= 0f)
                            return Fail("radius must be greater than 0 for a radial, got " + radius + ".");
                        radialCenter = c0;
                        // 🔴 SET_WEATHER_BUILDUP_RADIAL_COUNT_IS_UNKNOWN_1. cellsChanged was a
                        // hard -1 because the utility returns nothing - the same "the engine
                        // decides" shrug jawa/set_fog stopped taking for an answer. Snapshot
                        // the depths the utility can reach, call it, and count what moved.
                        // depth=0, or a depth the grid clamps away, now reads as 0 changed
                        // instead of an unknowable -1.
                        var radialCells = new List<IntVec3>();
                        var radialBefore = new List<float>();
                        int nRadial = GenRadial.NumCellsInRadius(radius);
                        for (int i = 0; i < nRadial; i++)
                        {
                            var rc = c0 + GenRadial.RadialPattern[i];
                            if (!rc.InBounds(map)) continue;
                            radialCells.Add(rc);
                            radialBefore.Add(sand ? map.sandGrid.GetDepth(rc) : map.snowGrid.GetDepth(rc));
                        }
                        if (sand) WeatherBuildupUtility.AddSandRadial(c0, map, radius, depth);
                        else WeatherBuildupUtility.AddSnowRadial(c0, map, radius, depth);
                        changed = 0;
                        for (int i = 0; i < radialCells.Count; i++)
                        {
                            float now = sand ? map.sandGrid.GetDepth(radialCells[i]) : map.snowGrid.GetDepth(radialCells[i]);
                            if (now != radialBefore[i]) changed++;
                        }
                    }
                    else
                    {
                        CellRect r;
                        if (!TryRect(rect, map, out r, out err)) return Fail(err);
                        foreach (var c in r)
                        {
                            float was = sand ? map.sandGrid.GetDepth(c) : map.snowGrid.GetDepth(c);
                            if (sand) { if (M == "add") map.sandGrid.AddDepth(c, depth); else map.sandGrid.SetDepth(c, depth); }
                            else { if (M == "add") map.snowGrid.AddDepth(c, depth); else map.snowGrid.SetDepth(c, depth); }
                            float now = sand ? map.sandGrid.GetDepth(c) : map.snowGrid.GetDepth(c);
                            if (now != was) { changed++; continue; }
                            unchanged++;
                            if (depth > 0f && now == 0f)
                                addRefused(c.x, c.z, "cell cannot hold " + (sand ? "sand" : "snow") +
                                    " - a full-fillage building is here, or the terrain has holdSnowOrSand=false; " +
                                    "SetDepth/AddDepth force 0 and log nothing");
                        }
                    }
                }
                catch (Exception e) { return Fail(kind + " " + M + " failed: " + e.GetType().Name + ": " + e.Message); }

                var back = new List<object>();
                {
                    // 🔴 Read back WHERE THE WRITE LANDED. In radial mode `rect` is null, so
                    // this used to sample cell 0,0 - the map corner, nowhere near the pile.
                    // Sample outward from the centre instead.
                    CellRect rr;
                    bool haveRect = (M == "radial" && radialCenter.IsValid)
                        ? TryRect(radialCenter.x + "," + radialCenter.z + ",1,1", map, out rr, out err)
                        : TryRect(rect, map, out rr, out err);
                    if (haveRect)
                    {
                        var sampled = new List<IntVec3>();
                        if (M == "radial")
                        {
                            int want = Math.Max(0, readBack);
                            int n = GenRadial.NumCellsInRadius(Math.Max(1f, radius));
                            for (int i = 0; i < n && sampled.Count < want; i++)
                            {
                                var c = radialCenter + GenRadial.RadialPattern[i];
                                if (c.InBounds(map)) sampled.Add(c);
                            }
                        }
                        else foreach (var c in rr) { if (sampled.Count >= Math.Max(0, readBack)) break; sampled.Add(c); }

                        foreach (var c in sampled)
                            back.Add(new
                            {
                                x = c.x, z = c.z,
                                snow = map.snowGrid.GetDepth(c),
                                sand = ModsConfig.OdysseyActive && map.sandGrid != null ? (object)map.sandGrid.GetDepth(c) : null,
                            });
                    }
                }

                return (object)new
                {
                    success = true, kind, mode = M, cellsChanged = changed,
                    cellsUnchanged = unchanged,
                    refusedCount = refusedTotal,
                    refusedListTruncated = refusedTotal > refused.Count,
                    refused,
                    odysseyActive = ModsConfig.OdysseyActive,
                    cells = back, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_deep_resource",
            Description =
                "Write the BURIED resource grid - what a deep drill finds. Takes a ThingDef " +
                "and a count per cell over a rect. This is how a map is given an ore body " +
                "that was never generated. Reading is free; writing is how you author what " +
                "a site is worth mining.",
            ResultDescription = "success, cellsChanged, sample of def+count after.")]
        public static async Task<object> SetDeepResource(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "ThingDef of the buried resource, e.g. MineableGold. Empty clears.")] string def = null,
            [ToolParameter(Description = "Count per cell. Capped at ushort.")] int count = 300,
            [ToolParameter(Description = "Read back at most this many cells. Default 5.")] int readBack = 5)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                ThingDef td = null;
                if (!string.IsNullOrEmpty(def))
                {
                    td = DefDatabase<ThingDef>.GetNamedSilentFail(def.Trim());
                    if (td == null) return Fail("No ThingDef '" + def + "'.", DefSuggestions<ThingDef>(def));
                }
                if (count < 0) count = 0;
                if (count > 65535) count = 65535;
                // 🔴 SET_DEEP_RESOURCE_COUNT_ZERO_CLEARS_1. DeepResourceGrid.SetAt opens with
                // `if (count == 0) def = null;` - so def=MineableGold with count=0 does not
                // place an empty gold seam, it ERASES whatever the cell held, and the response
                // still echoed the def back as though it had been written. Say so instead of
                // performing a deletion the caller did not ask for.
                if (td != null && count == 0)
                    return Fail("count=0 CLEARS the cell - DeepResourceGrid.SetAt nulls the def when count is 0, so '"
                                + td.defName + "' would not be written. Pass count>=1 to place it, or leave def empty to clear.");

                // 🔴 SET_DEEP_RESOURCE_PARTIAL_WRITE_HIDDEN_1. The loop used to
                // `return Fail("SetAt failed at ...")` on the first throwing cell. By then
                // `changed` cells of the rect had ALREADY been written and stayed written,
                // but the caller was handed success=false with no count - so the map held a
                // half-authored ore body that the response said did not exist. Record the
                // cell and carry on; the partial state is in the body either way.
                // 🔴 SET_DEEP_RESOURCE_UNCHANGED_CELLS_COUNTED_1. SetAt writes only when the
                // packed def-or-count actually differs, so re-stamping an ore body that is
                // already there - or clearing ground that already held nothing - moved no
                // grid cell at all while `changed++` ran for every cell in the rect. Diff the
                // grid, the same way jawa/set_gas counts its own writes.
                int changed = 0, unchangedCells = 0;
                int problemsTotal = 0;
                var problems = new List<object>();
                foreach (var c in r)
                {
                    try
                    {
                        var wasDef = map.deepResourceGrid.ThingDefAt(c);
                        int wasCount = map.deepResourceGrid.CountAt(c);
                        map.deepResourceGrid.SetAt(c, td, td == null ? 0 : count);
                        if (map.deepResourceGrid.ThingDefAt(c) != wasDef || map.deepResourceGrid.CountAt(c) != wasCount) changed++;
                        else unchangedCells++;
                    }
                    catch (Exception e)
                    {
                        problemsTotal++;
                        if (problems.Count < 20) problems.Add(new { x = c.x, z = c.z, why = e.GetType().Name + ": " + e.Message });
                    }
                }

                var back = new List<object>();
                foreach (var c in r)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    var d = map.deepResourceGrid.ThingDefAt(c);
                    back.Add(new { x = c.x, z = c.z, def = d != null ? d.defName : null, count = map.deepResourceGrid.CountAt(c) });
                }
                return (object)new
                {
                    success = true, cellsChanged = changed, cellsUnchanged = unchangedCells,
                    cellsInRect = r.Area,
                    problemCount = problemsTotal,
                    problemListTruncated = problemsTotal > problems.Count,
                    problems,
                    cells = back, ticksGame = TicksGameSafe()
                };
            });
        }


        // ================================================================
        //  M2 - BUILDINGS. The path Designator_Build itself takes under god
        //  mode: ThingMaker.MakeThing -> SetFactionDirect -> GenSpawn.Spawn.
        //
        //  ⛔ Do NOT drive Designator_Build: placingRot is protected and it
        //     reads Find.CurrentMap plus tutor/sound/fleck state.
        //  ⚠️ MakeThing already calls PostMake, which RANDOMISES HitPoints from
        //     def.startingHpRange - set HitPoints AFTER or buildings spawn damaged.
        //  ⚠️ Walls create NO roof. A built room is open sky until roofed.
        // ================================================================

        private static bool TryRot(string s, out Rot4 rot)
        {
            rot = Rot4.North;
            if (string.IsNullOrEmpty(s)) return true;
            s = s.Trim();
            int n;
            if (int.TryParse(s, out n)) { rot = new Rot4(((n % 4) + 4) % 4); return true; }
            switch (s.ToLowerInvariant())
            {
                case "north": case "n": rot = Rot4.North; return true;
                case "east": case "e": rot = Rot4.East; return true;
                case "south": case "s": rot = Rot4.South; return true;
                case "west": case "w": rot = Rot4.West; return true;
            }
            return false;
        }

        [Tool(
            "jawa/build_batch",
            Description =
                "Place finished buildings instantly - the god-mode path Designator_Build " +
                "takes: ThingMaker.MakeThing(def, stuff) then GenSpawn.Spawn. " +
                "ops format 'ThingDef:x,z[,rot]' separated by ';', e.g. " +
                "'Wall:10,20,0;Wall:11,20;Door:12,20,1'. rot is 0=N 1=E 2=S 3=W or a name. " +
                "stuff, faction, quality and hitPoints apply to every op in the call. " +
                "⚠️ HitPoints are set AFTER MakeThing on purpose - MakeThing calls PostMake " +
                "which randomises them from startingHpRange, so writing them first is lost. " +
                "⚠️ WALLS CREATE NO ROOF; roof separately with jawa/set_roof_batch. " +
                "🔴 READ `survived`, NOT `placed`. placed counts spawns that succeeded; a LATER " +
                "op whose multi-cell footprint covers an earlier one destroys it, and both " +
                "report success. Everything destroyed is named in displaced[]. Pass " +
                "refuseIfDisplaces to make that an error instead. " +
                "Call jawa/map_commit after a batch.",
            ResultDescription =
                "success, placed (spawns that SUCCEEDED), survived (still on the map when the "
                + "batch ended - these differ when a later op destroys an earlier one), "
                + "lostToLaterOps, failed[], displaced[] naming everything this batch destroyed "
                + "and whether this batch had placed it, and a read-back of each spawned thing.")]
        public static async Task<object> BuildBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'ThingDef:x,z[,rot]' ops separated by ';'.")] string ops = null,
            [ToolParameter(Description = "Stuff ThingDef, e.g. WoodLog, Steel, Granite.")] string stuff = null,
            [ToolParameter(Description = "Who owns the buildings. A FactionDef defName, OR the aliases 'player' / 'hostile' / 'none' that jawa/spawn_pawn takes. Empty = no faction.")] string faction = null,
            [ToolParameter(Description = "Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary.")] string quality = null,
            [ToolParameter(Description = "Hit points. -1 leaves the PostMake roll.")] int hitPoints = -1,
            [ToolParameter(Description = "Default true: a spawn destroys whatever it lands on, because RimWorld has no non-wiping spawn. Set false to REFUSE such an op instead - same effect as refuseIfDisplaces.")] bool wipeExisting = true,
            [ToolParameter(Description = "Read back at most this many things. Default 8.")] int readBack = 8,
            [ToolParameter(Description = "REFUSE any op that would destroy something already standing, instead of wiping it. Off by default, because a door legitimately replaces the wall in its cell. Turn it on when a generator's output must not eat itself.")] bool refuseIfDisplaces = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(ops)) return Fail("Give ops as 'ThingDef:x,z[,rot]' separated by ';'.");

                ThingDef stuffDef = null;
                if (!string.IsNullOrEmpty(stuff))
                {
                    stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                    if (stuffDef == null) return Fail("No stuff ThingDef '" + stuff + "'.", DefSuggestions<ThingDef>(stuff));
                }

                // BUILD_BATCH_FACTION_REJECTS_PLAYER_1. This used to go straight to
                // DefDatabase<FactionDef>, so faction="player" - which jawa/spawn_pawn
                // documents and accepts - came back "No FactionDef 'player'." and lost
                // a batch of 8 calls on 2026-08-26. The two tools now share one grammar.
                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    string ferr;
                    fac = ResolveFactionAliasOrDef(faction, out ferr);
                    if (fac == null && ferr != null)
                        return Fail(ferr, DefSuggestions<FactionDef>(faction));
                }

                QualityCategory q = QualityCategory.Normal; bool setQ = false;
                if (!string.IsNullOrEmpty(quality))
                {
                    // 🔴 BUILD_BATCH_QUALITY_ENUM_UNGATED_1. Enum.Parse accepts ANY NUMERIC
                    // STRING for an enum and does not check it against the declared members -
                    // QualityCategory is a byte enum, so quality="200" parsed cleanly to
                    // (QualityCategory)200 and was handed to CompQuality.SetQuality, which
                    // stores it verbatim. Every later reader (QualityUtility labels, stat
                    // offsets, the save) then sees a value with no member behind it, and the
                    // tool reported success. Enum.IsDefined is the check Parse does not do.
                    object parsed = null;
                    try { parsed = Enum.Parse(typeof(QualityCategory), quality.Trim(), true); }
                    catch { parsed = null; }
                    if (parsed == null || !Enum.IsDefined(typeof(QualityCategory), parsed))
                        return Fail("Bad quality '" + quality + "'. Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary "
                                    + "(a bare number is NOT accepted - it would produce a quality with no member behind it).");
                    q = (QualityCategory)parsed; setQ = true;
                }

                int placed = 0; var failures = new List<object>(); var spawnedThings = new List<Thing>();
                // 🔴 WHAT THIS BATCH DESTROYS ON ITS WAY IN. BUILD_BATCH_OVERWRITES_SILENTLY_1:
                // eight calls reported placed 81 with failed:[] everywhere and the map held 78.
                // Three things had been destroyed by a LATER op whose multi-cell footprint
                // covered them - a Table1x2c over a DiningChair, a Shelf over two earlier
                // Shelfs - and BOTH the destroyer and the destroyed reported success.
                // `placed` counts spawn ATTEMPTS. A caller diffing placed against requested,
                // which is exactly what an acceptance criterion does, sees a perfect run.
                var displaced = new List<object>();
                // 🔴 BUILD_BATCH_QUALITY_SILENTLY_DROPPED_1. `quality` was applied only when
                // the spawned thing has a CompQuality; a def without one (a Wall, a Conduit,
                // most structures) took the parameter, ignored it and reported a clean
                // success, so a caller who asked for Legendary got Normal-with-no-quality and
                // nothing said so. Record the drops.
                var qualityIgnored = new List<string>();
                // PostPlace exceptions used to vanish into a bare `catch {}` - the def's
                // real side effect (a wind turbine's placement logic, etc.) silently never
                // ran and the op still counted as a full success. Record it instead.
                var placeWorkerWarnings = new List<object>();

                foreach (var raw in ops.Split(new[] { ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    var op = raw.Trim(); if (op.Length == 0) continue;
                    int colon = op.IndexOf(':');
                    if (colon <= 0) { failures.Add(new { op, why = "expected 'ThingDef:x,z[,rot]'" }); continue; }
                    var dn = op.Substring(0, colon).Trim();
                    var bits = op.Substring(colon + 1).Split(',');
                    int x, z;
                    if (bits.Length < 2 || !int.TryParse(bits[0].Trim(), out x) || !int.TryParse(bits[1].Trim(), out z))
                    { failures.Add(new { op, why = "bad coordinates" }); continue; }
                    Rot4 rot;
                    if (!TryRot(bits.Length > 2 ? bits[2] : null, out rot))
                    { failures.Add(new { op, why = "bad rot" }); continue; }

                    var td = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                    if (td == null) { failures.Add(new { op, why = "no ThingDef '" + dn + "'" }); continue; }

                    var c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) { failures.Add(new { op, why = "cell out of bounds" }); continue; }

                    var useStuff = stuffDef;
                    if (td.MadeFromStuff && useStuff == null)
                        useStuff = GenStuff.DefaultStuffFor(td);
                    if (!td.MadeFromStuff) useStuff = null;

                    try
                    {
                        // Look BEFORE the wipe: afterwards the thing is gone and there is
                        // nothing left to name. SpawningWipes is the engine's own answer to
                        // "would placing this destroy that", so this reports what actually
                        // happens rather than a guess about footprints.
                        var occupied = GenAdj.OccupiedRect(c, rot, td.size);
                        var doomed = new List<Thing>();
                        // 🔴 BUILD_BATCH_SAMEDEF_REPLACEMENT_UNREPORTED_1. The same def at the
                        // same cell was skipped entirely - not refused, not reported - yet
                        // GenSpawn.Spawn still wipes it, so displaced[] (documented as "naming
                        // everything this batch destroyed") was missing a real destruction, and
                        // when the victim came from an EARLIER op of this run the caller saw
                        // survived < placed with nothing in displaced[] to explain it. It stays
                        // OUT of the refusal set on purpose - re-stamping an identical layout is
                        // legitimately idempotent - but it is now named.
                        var replacedInPlace = new List<Thing>();
                        foreach (var cell in occupied)
                        {
                            if (!cell.InBounds(map)) continue;
                            var here = map.thingGrid.ThingsListAtFast(cell);
                            for (int i = 0; i < here.Count; i++)
                            {
                                var other = here[i];
                                if (other == null || other.Destroyed) continue;
                                if (other.def == td && other.Position == c)
                                {
                                    if (!replacedInPlace.Contains(other)) replacedInPlace.Add(other);
                                    continue;
                                }
                                if (GenSpawn.SpawningWipes(td, other.def) && !doomed.Contains(other))
                                    doomed.Add(other);
                            }
                        }
                        // 🔴 wipeExisting=false CANNOT mean "spawn without destroying": every
                        // WipeMode wipes (Vanish/FullRefund/VanishOrMoveAside) and
                        // GenSpawn.Spawn defaults to Vanish, so the old explicit
                        // WipeExistingThings call was a duplicate of what Spawn does anyway
                        // and clearing the flag changed nothing at all. The only honest
                        // reading of "do not wipe" is "do not place it, then" - the same
                        // refusal refuseIfDisplaces already gives.
                        if (doomed.Count > 0 && (refuseIfDisplaces || !wipeExisting))
                        {
                            failures.Add(new
                            {
                                op,
                                why = (refuseIfDisplaces ? "refuseIfDisplaces" : "wipeExisting=false")
                                      + ": placing this would destroy "
                                      + doomed.Count + " existing thing(s): "
                                      + string.Join(", ", doomed.Select(d => d.def.defName + "@" + d.Position.x + "," + d.Position.z).ToArray())
                            });
                            continue;
                        }
                        foreach (var d in doomed)
                            displaced.Add(new
                            {
                                op,
                                destroyed = d.def.defName,
                                x = d.Position.x,
                                z = d.Position.z,
                                // The case that made this item: the thing destroyed was placed
                                // by an EARLIER op of this same run, so `placed` counted it.
                                placedByThisBatch = spawnedThings.Contains(d),
                                sameDefReplacedInPlace = false
                            });
                        foreach (var d in replacedInPlace)
                            displaced.Add(new
                            {
                                op,
                                destroyed = d.def.defName,
                                x = d.Position.x,
                                z = d.Position.z,
                                placedByThisBatch = spawnedThings.Contains(d),
                                sameDefReplacedInPlace = true
                            });

                        // GenSpawn.Spawn below does WipeExistingThings(..., Vanish) itself.
                        var t = ThingMaker.MakeThing(td, useStuff);
                        if (fac != null) t.SetFactionDirect(fac);
                        if (setQ)
                        {
                            var cq = t.TryGetComp<CompQuality>();
                            if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider);
                            else if (!qualityIgnored.Contains(td.defName)) qualityIgnored.Add(td.defName);
                        }
                        var spawned = GenSpawn.Spawn(t, c, map, rot);

                        // AFTER MakeThing/PostMake, or the startingHpRange roll wins.
                        if (hitPoints >= 0 && spawned != null && spawned.def.useHitPoints)
                            spawned.HitPoints = Mathf.Clamp(hitPoints, 1, spawned.MaxHitPoints);

                        // Some defs (wind turbines) do their side effects only here.
                        if (td.PlaceWorkers != null)
                            foreach (var pw in td.PlaceWorkers)
                                try { pw.PostPlace(map, td, c, rot); }
                                catch (Exception e) { placeWorkerWarnings.Add(new { op, placeWorker = pw.GetType().Name, why = e.GetType().Name + ": " + e.Message }); }

                        if (spawned != null) { placed++; spawnedThings.Add(spawned); }
                        else failures.Add(new { op, why = "GenSpawn.Spawn returned null" });
                    }
                    catch (Exception e) { failures.Add(new { op, why = e.GetType().Name + ": " + e.Message }); }
                }

                var back = new List<object>();
                foreach (var t in spawnedThings)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    var cq = t.TryGetComp<CompQuality>();
                    QualityCategory qq;
                    back.Add(new
                    {
                        def = t.def.defName,
                        stuff = t.Stuff != null ? t.Stuff.defName : null,
                        x = t.Position.x, z = t.Position.z,
                        rot = t.Rotation.AsInt,
                        faction = t.Faction != null ? t.Faction.def.defName : null,
                        hitPoints = t.def.useHitPoints ? (object)t.HitPoints : null,
                        maxHitPoints = t.def.useHitPoints ? (object)t.MaxHitPoints : null,
                        quality = (cq != null && t.TryGetQuality(out qq)) ? qq.ToString() : null,
                        // 🔴 This read-back is of what the batch SPAWNED, not of what is on
                        // the map: a later op in the same batch can have destroyed it, and
                        // Thing.Position keeps answering afterwards. Listing a corpse as a
                        // placed building is the same lie `survived` exists to expose.
                        destroyed = t.Destroyed,
                    });
                }

                // Counted AFTER every op, because an op can destroy an earlier one.
                int survived = 0;
                foreach (var t in spawnedThings) if (t != null && !t.Destroyed) survived++;
                int lostToLaterOps = placed - survived;

                return (object)new
                {
                    success = true,
                    // 🔑 `placed` is the number of SPAWNS THAT SUCCEEDED, and it is not the
                    // number of things on the map. `survived` is. They differ whenever a
                    // later op's footprint covered an earlier one.
                    placed,
                    survived,
                    lostToLaterOps,
                    failedCount = failures.Count, failed = failures,
                    displacedCount = displaced.Count,
                    displaced,
                    // A spawn that "succeeded" can still have skipped a def's real side
                    // effect (a wind turbine's placement hook, etc.) if PostPlace threw.
                    // `placed` does not reflect that - check this list too.
                    placeWorkerWarningsCount = placeWorkerWarnings.Count,
                    placeWorkerWarnings,
                    // A `quality` the def cannot carry is dropped, not applied. Named here
                    // rather than left to be discovered in things[].
                    qualityIgnoredForDefs = qualityIgnored,
                    message = lostToLaterOps > 0
                        ? placed + " spawned, " + survived + " SURVIVED - " + lostToLaterOps
                          + " were destroyed by a later op in this same batch. See displaced[]."
                        : (displaced.Count > 0
                            ? placed + " placed; " + displaced.Count + " pre-existing thing(s) were wiped. See displaced[]."
                            : placed + " placed."),
                    note = "Walls create NO roof - roof separately. Run jawa/map_commit after the batch.",
                    things = back,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/build_check",
            Description =
                "Pre-flight a building placement WITHOUT placing it. Returns the engine's own " +
                "AcceptanceReport from GenConstruct.CanPlaceBlueprintAt plus " +
                "GenSpawn.CanSpawnAt, so you get the real reason ('needs even ground', " +
                "'would block interaction spot') instead of discovering it as a failed spawn. " +
                "Read-only.",
            ResultDescription = "success, cells[] each with canPlace, reason, canSpawn, occupants[].")]
        public static async Task<object> BuildCheck(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingDef to test.")] string def = null,
            [ToolParameter(Description = "Rect 'x,z,w,h' of cells to test.")] string rect = null,
            [ToolParameter(Description = "Stuff ThingDef.")] string stuff = null,
            [ToolParameter(Description = "Rotation 0-3 or name.")] string rot = null,
            [ToolParameter(Description = "Test as god mode. Default false.")] bool godMode = false,
            [ToolParameter(Description = "Max cells. Default 50.")] int limit = 50)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(def)) return Fail("Give a ThingDef.");
                var td = DefDatabase<ThingDef>.GetNamedSilentFail(def.Trim());
                if (td == null) return Fail("No ThingDef '" + def + "'.", DefSuggestions<ThingDef>(def));
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);
                Rot4 rr;
                if (!TryRot(rot, out rr)) return Fail("Bad rot '" + rot + "'.");

                ThingDef sd = null;
                if (!string.IsNullOrEmpty(stuff)) sd = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                if (td.MadeFromStuff && sd == null) sd = GenStuff.DefaultStuffFor(td);

                var cells = new List<object>(); int ok = 0;
                foreach (var c in r)
                {
                    if (cells.Count >= Math.Max(1, limit)) break;
                    string reason = null; bool canPlace = false, canSpawn = false;
                    try
                    {
                        var rep = GenConstruct.CanPlaceBlueprintAt(td, c, rr, map, godMode, null, null, sd);
                        canPlace = rep.Accepted;
                        reason = rep.Accepted ? null : rep.Reason;
                    }
                    catch (Exception e) { reason = e.GetType().Name + ": " + e.Message; }
                    // A bare `catch {}` here reported canSpawn=false as though the engine had
                    // answered no, when in fact it had thrown and nobody asked.
                    try { canSpawn = GenSpawn.CanSpawnAt(td, c, map, rr); }
                    catch (Exception e)
                    {
                        var thrown = "CanSpawnAt threw: " + e.GetType().Name + ": " + e.Message;
                        reason = string.IsNullOrEmpty(reason) ? thrown : reason + " | " + thrown;
                    }

                    var occ = map.thingGrid.ThingsListAtFast(c).Select(t => t.def.defName).Distinct().ToList();
                    if (canPlace) ok++;
                    cells.Add(new { x = c.x, z = c.z, canPlace, reason, canSpawn, occupants = occ });
                }
                return (object)new
                {
                    success = true, def = td.defName, stuff = sd != null ? sd.defName : null,
                    acceptableCells = ok, tested = cells.Count,
                    cellsInRect = r.Area, truncated = cells.Count < r.Area,
                    godMode, cells,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/designate_batch",
            Description =
                "Add or remove Designations directly - Mine, Deconstruct, HarvestPlant, " +
                "CutPlant, Haul, SmoothWall, SmoothFloor, Plan, Hunt, Tame, Slaughter, " +
                "Flick, Strip and the rest - with no cursor and no drag tool. " +
                "action='add' | 'remove' | 'query'. Always give a rect: the DesignationDef's " +
                "own targetType decides what the rect means - a CELL designation (Mine, " +
                "SmoothFloor, Plan) marks the cells, a THING designation (Deconstruct, " +
                "HarvestPlant, Hunt, Flick, Strip - most of them) marks every thing standing " +
                "in them. " +
                "⚠️ AddDesignation logs a red error on double-add, so this queries first.",
            ResultDescription =
                "success, added, removed, alreadyPresent, targetType and targetedThings "
                + "(which of the two readings of the rect was used), problems[], totalNow.")]
        public static async Task<object> DesignateBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'add' | 'remove' | 'query'.")] string action = "add",
            [ToolParameter(Description = "DesignationDef name, e.g. Mine, Deconstruct, HarvestPlant.")] string designation = null,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "FORCE targeting the things in each cell. Leave false: the DesignationDef's own targetType already decides, and this tool follows it.")] bool onThings = false,
            [ToolParameter(Description = "Max rows returned. Default 40.")] int limit = 40)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                string A = (action ?? "").Trim().ToLowerInvariant();
                var dm = map.designationManager;

                DesignationDef dd = null;
                if (!string.IsNullOrEmpty(designation))
                {
                    dd = DefDatabase<DesignationDef>.GetNamedSilentFail(designation.Trim());
                    if (dd == null) return Fail("No DesignationDef '" + designation + "'.", DefSuggestions<DesignationDef>(designation));
                }

                if (A == "query")
                {
                    // 🔴 DESIGNATE_BATCH_QUERY_TOTAL_IGNORES_FILTER_1. `total` used to be
                    // dm.AllDesignations.Count() - EVERY designation on the map - while `rows`
                    // was filtered to the requested DesignationDef. A query for Mine on a map
                    // with 4 mine marks and 900 plan marks answered total:904, and a caller
                    // reading total-vs-returned concluded its list was truncated when it was
                    // complete. Count what was actually asked about, and report both.
                    var rows = new List<object>();
                    int matching = 0, allDesignations = 0;
                    foreach (var d in dm.AllDesignations)
                    {
                        allDesignations++;
                        if (dd != null && d.def != dd) continue;
                        matching++;
                        if (rows.Count >= Math.Max(1, limit)) continue;
                        rows.Add(new
                        {
                            def = d.def.defName,
                            x = d.target.Cell.x, z = d.target.Cell.z,
                            thing = d.target.HasThing ? d.target.Thing.def.defName : null,
                        });
                    }
                    return (object)new
                    {
                        success = true, action = "query",
                        filter = dd != null ? dd.defName : null,
                        total = matching,
                        totalAllDesignations = allDesignations,
                        returned = rows.Count,
                        truncated = matching > rows.Count,
                        designations = rows, ticksGame = TicksGameSafe()
                    };
                }

                if (A != "add" && A != "remove")
                    return Fail("action must be add|remove|query, got '" + action + "' - every OTHER value fell " +
                        "through to remove until this check existed, which could wipe designations over a whole rect.");

                if (dd == null) return Fail("Give a DesignationDef for add/remove.");
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                int added = 0, removed = 0, already = 0;
                // 🔴 DESIGNATE_BATCH_PROBLEMS_CAPPED_1. `problems` is capped at 15 entries so
                // the body stays small, and there was NO total beside it - the same capped-list
                // lie already fixed in set_substructure_batch, set_terrain_layer and
                // map_zones/paintZone. A rect that threw on 400 cells showed 15 problems and
                // no sign there were any more. Count every one; cap only the display.
                int problemsTotal = 0;
                var problems = new List<object>();

                // 🔴 TargetType DECIDES, and TargetType.Thing is the enum's ZERO - so every
                // DesignationDef that does not declare targetType is a THING designation,
                // and 17 of vanilla's 27 are (Deconstruct, HarvestPlant, CutPlant, Haul,
                // Hunt, Tame, Slaughter, Flick, Strip ... all of them named in this tool's
                // own description). DesignationManager.AddDesignation dereferences
                // `newDes.target.Thing.SetForbidden(...)` for those, so handing it a CELL
                // target throws NullReferenceException on every cell in the rect. This used
                // to be the DEFAULT path while the parameter claimed "Default auto".
                bool wantThings = onThings || dd.targetType == TargetType.Thing;
                if (onThings && dd.targetType == TargetType.Cell)
                    return Fail("'" + dd.defName + "' is a CELL designation (targetType=Cell); it cannot be " +
                                "attached to a Thing. Drop onThings and give a rect.");
                string targetNote = dd.targetType == TargetType.Thing
                    ? "'" + dd.defName + "' is a THING designation - the rect selects cells and each thing in them is designated."
                    : "'" + dd.defName + "' is a CELL designation - the rect's cells are designated directly.";

                foreach (var c in r)
                {
                    try
                    {
                        if (wantThings)
                        {
                            foreach (var t in map.thingGrid.ThingsListAtFast(c).ToList())
                            {
                                if (A == "add")
                                {
                                    if (dm.DesignationOn(t, dd) != null) { already++; continue; }
                                    dm.AddDesignation(new Designation(t, dd)); added++;
                                }
                                else { var ex = dm.DesignationOn(t, dd); if (ex != null) { dm.RemoveDesignation(ex); removed++; } }
                            }
                        }
                        else
                        {
                            if (A == "add")
                            {
                                if (dm.DesignationAt(c, dd) != null) { already++; continue; }
                                dm.AddDesignation(new Designation(c, dd)); added++;
                            }
                            else if (dm.DesignationAt(c, dd) != null) { dm.TryRemoveDesignation(c, dd); removed++; }
                        }
                    }
                    catch (Exception e)
                    {
                        problemsTotal++;
                        if (problems.Count < 15) problems.Add(new { x = c.x, z = c.z, why = e.GetType().Name + ": " + e.Message });
                    }
                }

                return (object)new
                {
                    success = true, action = A, designation = dd.defName,
                    added, removed, alreadyPresent = already,
                    targetType = dd.targetType.ToString(), targetedThings = wantThings,
                    note = targetNote,
                    onThings,
                    problemCount = problemsTotal,
                    problemListTruncated = problemsTotal > problems.Count,
                    problems,
                    totalNow = dm.AllDesignations.Count(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  M3 - PREFAB CAPTURE AND REPLAY. Copy/paste regions of map.
        //  Base 1.6, ungated. PrefabUtility.CreatePrefab(CellRect, copyAllThings,
        //  copyTerrain) captures; SpawnPrefab stamps it back.
        //  ⇒ authored set-pieces become DATA: build one wreck by hand, capture
        //  it, stamp it anywhere. This is what makes scene templates cheap.
        //
        //  Captures live in a static registry for the session. They are NOT
        //  registered into DefDatabase and do NOT survive a restart - that is
        //  deliberate, because a half-formed PrefabDef in the database would be
        //  visible to vanilla systems that never asked for it.
        // ================================================================
        private static readonly Dictionary<string, PrefabDef> JawaPrefabs =
            new Dictionary<string, PrefabDef>(StringComparer.OrdinalIgnoreCase);

        /// <summary>PrefabDef.things is internal; GetThings() is the public route.</summary>
        private static int CountPrefabThings(PrefabDef pf)
        {
            if (pf == null) return 0;
            try { return pf.GetThings().Count(); }
            catch { return -1; }
        }

        [Tool(
            "jawa/prefab_capture",
            Description =
                "Capture a rectangle of the live map - its things and optionally its terrain - " +
                "into a named prefab held for this session. Build a scene by hand once, " +
                "capture it, then stamp it anywhere with jawa/prefab_place. " +
                "copyAllThings=false captures only buildings and natural features; true also " +
                "takes loose items, filth and pawnless clutter. " +
                "⚠️ Captures are SESSION-ONLY - they are not written to DefDatabase and do " +
                "not survive a restart, deliberately.",
            ResultDescription = "success, name, size, thingCount, and the captured contents summary.")]
        public static async Task<object> PrefabCapture(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Name to file the capture under.")] string name = null,
            [ToolParameter(Description = "Rect 'x,z,w,h' to capture.")] string rect = null,
            [ToolParameter(Description = "Also capture loose items and filth. Default false.")] bool copyAllThings = false,
            [ToolParameter(Description = "Also capture terrain. Default true.")] bool copyTerrain = true,
            [ToolParameter(Description = "Overwrite an existing capture of the same name.")] bool overwrite = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(name)) return Fail("Give a name for the capture.");
                name = name.Trim();
                if (JawaPrefabs.ContainsKey(name) && !overwrite)
                    return Fail("A capture named '" + name + "' already exists. Pass overwrite=true to replace it.");
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                PrefabDef pf;
                try { pf = PrefabUtility.CreatePrefab(r, copyAllThings, copyTerrain); }
                catch (Exception e) { return Fail("CreatePrefab failed: " + e.GetType().Name + ": " + e.Message); }
                if (pf == null) return Fail("CreatePrefab returned null for " + rect + ".");

                pf.defName = "JawaPrefab_" + name;

                // 🔴 VANILLA GAP, measured 2026-08-19: PrefabUtility.CreatePrefab builds
                // `things` and `terrain` but NEVER SETS `size`. It comes back (0,0), and
                // size is what drives GetRoot and every bounds check - so CanSpawnPrefab
                // refuses and SpawnPrefab cannot place. A captured prefab is unusable
                // until the caller sets this. Read out of CreatePrefab's own body.
                if (pf.size.x <= 0 || pf.size.z <= 0)
                    pf.size = new IntVec2(r.Width, r.Height);

                JawaPrefabs[name] = pf;

                var byDef = new Dictionary<string, int>();
                int things = 0;
                // 🔴 PREFAB_CAPTURE_THINGCOUNT_ZERO_IS_A_LIE_1. GetThings() throwing used to
                // leave `things` at 0 and put the reason in the GAME LOG only - so the bridge
                // caller was handed thingCount:0 for a capture that may hold fifty things, and
                // 0 is exactly what an empty capture reports. Ignorance is not zero: report
                // null plus the error and let the caller decide.
                string thingCountError = null;
                try
                {
                    foreach (var pair in pf.GetThings())
                    {
                        things++;
                        var d = pair.data != null ? pair.data.def : null;
                        var dn = d != null ? d.defName : "(null)";
                        int c; byDef.TryGetValue(dn, out c); byDef[dn] = c + 1;
                    }
                }
                catch (Exception e)
                {
                    thingCountError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] prefab_capture: GetThings threw: " + e.Message);
                }

                return (object)new
                {
                    success = true,
                    name,
                    defName = pf.defName,
                    size = new { x = pf.size.x, z = pf.size.z },
                    capturedFrom = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    // null, not 0, when the count could not be taken - see thingCountError.
                    thingCount = thingCountError == null ? (object)things : null,
                    thingCountError,
                    copyAllThings, copyTerrain,
                    contents = byDef.OrderByDescending(k => k.Value).Take(25).ToDictionary(k => k.Key, k => k.Value),
                    note = "Session-only. Not in DefDatabase; does not survive a restart.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/prefab_place",
            Description =
                "Stamp a captured prefab (or any shipped PrefabDef) onto the map at a " +
                "position and rotation. Checks PrefabUtility.CanSpawnPrefab first and " +
                "refuses with a reason rather than half-placing. faction assigns ownership " +
                "of everything spawned. blueprint=true places BLUEPRINTS instead of finished " +
                "things, so colonists build it themselves. Call jawa/map_commit after.",
            ResultDescription = "success, placed, spawnedCount, and a read-back of what landed.")]
        public static async Task<object> PrefabPlace(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Name of a session capture, or a shipped PrefabDef defName.")] string name = null,
            [ToolParameter(Description = "Position 'x,z'.")] string pos = null,
            [ToolParameter(Description = "Rotation 0-3 or name.")] string rot = null,
            [ToolParameter(Description = "Faction defName to own what is placed.")] string faction = null,
            [ToolParameter(Description = "Place blueprints instead of finished things.")] bool blueprint = false,
            [ToolParameter(Description = "Check only, do not place.")] bool checkOnly = false,
            [ToolParameter(Description = "Read back at most this many things. Default 8.")] int readBack = 8)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrEmpty(name)) return Fail("Give a prefab name.");
                name = name.Trim();

                PrefabDef pf = null;
                if (!JawaPrefabs.TryGetValue(name, out pf))
                    pf = DefDatabase<PrefabDef>.GetNamedSilentFail(name);
                if (pf == null)
                    return Fail("No capture and no PrefabDef named '" + name + "'. Session captures: " +
                                (JawaPrefabs.Count == 0 ? "(none)" : string.Join(", ", JawaPrefabs.Keys.ToArray())));

                int x, z; var b = (pos ?? "").Split(',');
                if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                    return Fail("Give pos as 'x,z'.");
                var c0 = new IntVec3(x, 0, z);
                if (!c0.InBounds(map)) return Fail("Position out of bounds.");
                Rot4 rr;
                if (!TryRot(rot, out rr)) return Fail("Bad rot '" + rot + "'.");
                rr = PrefabUtility.ValidateRotation(pf, rr);

                // BUILD_BATCH_FACTION_REJECTS_PLAYER_1 was fixed in jawa/build_batch and left
                // unfixed here, so the same faction="player" that build_batch accepts came
                // back "No FactionDef 'player'." from prefab_place. One grammar across the
                // file, and the resolver already reports which one the caller reached for.
                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    string ferr;
                    fac = ResolveFactionAliasOrDef(faction, out ferr);
                    if (fac == null && ferr != null)
                        return Fail(ferr, DefSuggestions<FactionDef>(faction));
                }

                bool can;
                try { can = PrefabUtility.CanSpawnPrefab(pf, map, c0, rr); }
                catch (Exception e) { return Fail("CanSpawnPrefab threw: " + e.GetType().Name + ": " + e.Message); }

                if (checkOnly || !can)
                    return (object)new
                    {
                        success = can,
                        // Not always a dry run: this branch is also the REFUSAL path, and
                        // reporting checkedOnly=true there told the caller nothing had been
                        // attempted when in fact a real placement had just been turned down.
                        checkedOnly = checkOnly,
                        canSpawn = can,
                        message = can ? null : "CanSpawnPrefab refused at " + pos + " rot " + rr.AsInt + " - blocked cells or unsuitable terrain.",
                        prefab = pf.defName,
                        size = new { x = pf.size.x, z = pf.size.z },
                        ticksGame = TicksGameSafe(),
                    };

                var spawned = new List<Thing>();
                try { PrefabUtility.SpawnPrefab(pf, map, c0, rr, fac, spawned, null, null, blueprint); }
                catch (Exception e) { return Fail("SpawnPrefab failed: " + e.GetType().Name + ": " + e.Message); }

                var back = new List<object>();
                foreach (var t in spawned)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    if (t == null) continue;
                    back.Add(new
                    {
                        def = t.def.defName,
                        stuff = t.Stuff != null ? t.Stuff.defName : null,
                        x = t.Position.x, z = t.Position.z, rot = t.Rotation.AsInt,
                        faction = t.Faction != null ? t.Faction.def.defName : null,
                    });
                }

                return (object)new
                {
                    success = true,
                    prefab = pf.defName, placedAt = new { x, z }, rot = rr.AsInt,
                    blueprint,
                    spawnedCount = spawned.Count,
                    things = back,
                    note = "Run jawa/map_commit.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/prefab_list",
            Description =
                "List the prefabs available to jawa/prefab_place: this session's captures " +
                "plus every shipped PrefabDef. Read-only.",
            ResultDescription = "success, captures[], shipped[].")]
        public static async Task<object> PrefabList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Max shipped defs listed. Default 60.")] int limit = 60)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var caps = JawaPrefabs.Select(kv => new
                {
                    name = kv.Key,
                    defName = kv.Value.defName,
                    size = new { x = kv.Value.size.x, z = kv.Value.size.z },
                    thingCount = CountPrefabThings(kv.Value),
                }).ToList();

                var shipped = DefDatabase<PrefabDef>.AllDefsListForReading
                    .Take(Math.Max(1, limit))
                    .Select(d => new { defName = d.defName, size = new { x = d.size.x, z = d.size.z },
                                       thingCount = CountPrefabThings(d) })
                    .ToList();

                return (object)new
                {
                    success = true,
                    sessionCaptures = caps.Count, captures = caps,
                    shippedTotal = DefDatabase<PrefabDef>.AllDefsListForReading.Count(),
                    shipped,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  M4 remainder - GAS, ZONES, AREAS
        // ================================================================
        [Tool(
            "jawa/set_gas",
            Description =
                "Add or clear gas on map cells - tox, smoke, rot stink, deadlife dust. " +
                "action='add' | 'clear'. Density is 0-255 per cell. " +
                "Gas is what makes a room read as poisoned or burning without setting " +
                "anything on fire.",
            ResultDescription = "success, cellsChanged, and the gas type used.")]
        public static async Task<object> SetGas(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'add' | 'clear'.")] string action = "add",
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "ToxGas | BlindSmoke | RotStink | DeadlifeDust.")] string gasType = "ToxGas",
            [ToolParameter(Description = "Density 1-255.")] int density = 255)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                // 🔴 SET_GAS_GASTYPE_ENUM_UNGATED_1. Enum.Parse takes any numeric string
                // without checking it names a member, so gasType="7" parsed to (GasType)7.
                // GasGrid.AddGas's switch then hits `default:`, logs "Trying to add unknown
                // gas type." and RETURNS - and the loop below still ran changed++ for every
                // cell, so the tool reported a full rect gassed while the grid never moved.
                // Enum.IsDefined is the check Parse does not do.
                GasType gt;
                object gtParsed = null;
                try { gtParsed = Enum.Parse(typeof(GasType), (gasType ?? "").Trim(), true); }
                catch { gtParsed = null; }
                if (gtParsed == null || !Enum.IsDefined(typeof(GasType), gtParsed))
                    return Fail("Bad gasType '" + gasType + "'. Valid: " + string.Join(", ", Enum.GetNames(typeof(GasType)))
                                + " (a bare number is NOT accepted - GasGrid.AddGas would log 'unknown gas type' and silently do nothing).");
                gt = (GasType)gtParsed;

                bool add = string.Equals(action, "add", StringComparison.OrdinalIgnoreCase);
                bool clr = string.Equals(action, "clear", StringComparison.OrdinalIgnoreCase);
                if (!add && !clr) return Fail("action must be add|clear.");

                // 🔴 SET_GAS_TOXDEADLIFE_SILENT_NOOP_1. GasGrid.AddGas gates ToxGas behind
                // ModLister.CheckBiotech and DeadlifeDust behind ModLister.CheckAnomaly - both
                // log an error and silently RETURN, never throw. Nothing upstream of AddGas
                // checked that, so 'action=add, gasType=ToxGas' (ToxGas is also the DEFAULT
                // gasType) on a non-Biotech game used to add changed++ for every cell while
                // AddGas did nothing at all - the exact "gate reported, never thrown" contract
                // this section's own header comment states, broken for this one tool. Check
                // and report before the loop, the same way sand/Odyssey is already gated in
                // jawa/set_weather_buildup.
                if (add)
                {
                    if (gt == GasType.ToxGas && !ModsConfig.BiotechActive)
                        return Fail("ToxGas requires Biotech, which is not active. GasGrid.AddGas would silently no-op.");
                    if (gt == GasType.DeadlifeDust && !ModsConfig.AnomalyActive)
                        return Fail("DeadlifeDust requires Anomaly, which is not active. GasGrid.AddGas would silently no-op.");
                }

                // 🔴 SET_GAS_UNCHANGED_CELLS_COUNTED_1. AddGas's OTHER silent return is
                // `!GasCanMoveTo(cell)` - a wall, or any Fillage.Full edifice, or a closed
                // door - and every one of those used to run changed++. A rect over a built
                // room reported every wall cell as gassed. Same on the clear side: a cell
                // that already held none of the selected gas was counted as cleared.
                // Count what the grid actually did, and name the refusals.
                int changed = 0, unchanged = 0;
                int refusedTotal = 0;
                var refused = new List<object>();
                Action<int, int, string> addRefused = (cx, cz, why) =>
                {
                    refusedTotal++;
                    if (refused.Count < 20) refused.Add(new { x = cx, z = cz, why });
                };
                foreach (var c in r)
                {
                    try
                    {
                        if (add)
                        {
                            if (!map.gasGrid.GasCanMoveTo(c))
                            { addRefused(c.x, c.z, "GasCanMoveTo false - a full-fillage edifice or closed door is here, AddGas would silently no-op"); continue; }
                            var before = map.gasGrid.DensitiesAt(c);
                            map.gasGrid.AddGas(c, gt, Math.Max(1, Math.Min(255, density)));
                            var after = map.gasGrid.DensitiesAt(c);
                            if (after != before) changed++; else unchanged++;
                        }
                        else
                        {
                            // 🔴 SET_GAS_CLEAR_WIPES_ALL_TYPES_1. GasGrid packs all FOUR gas
                            // types into one uint per cell (BlindSmoke|ToxGas<<8|RotStink<<16|
                            // DeadlifeDust<<24 - see GasGrid.SetDirect). ClearCellUnsafe zeroes
                            // that whole packed uint, so `action=clear, gasType=RotStink` used
                            // to silently erase ToxGas/BlindSmoke/DeadlifeDust at the same cell
                            // too - the caller asked to clear one gas and three others vanished
                            // with no report. Read all four back, zero only the selected one,
                            // and write the rest back unchanged - the same read-modify-write
                            // AddGas itself does one type at a time.
                            //
                            // ClearCellUnsafe is still the ONE GasGrid write that does not dirty
                            // the mesh - that is what "Unsafe" names - so this still dirties it
                            // itself; jawa/map_commit's flag set does not include Gas either.
                            var cur = map.gasGrid.DensitiesAt(c);
                            byte smoke = (byte)cur.x, tox = (byte)cur.y, rot = (byte)cur.z, dead = (byte)cur.w;
                            bool had;
                            switch (gt)
                            {
                                case GasType.BlindSmoke: had = smoke != 0; smoke = 0; break;
                                case GasType.ToxGas: had = tox != 0; tox = 0; break;
                                case GasType.RotStink: had = rot != 0; rot = 0; break;
                                case GasType.DeadlifeDust: had = dead != 0; dead = 0; break;
                                default: had = false; break;
                            }
                            if (!had) { unchanged++; continue; }
                            map.gasGrid.SetDirect(c, smoke, tox, rot, dead);
                            map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Gas);
                            changed++;
                        }
                    }
                    catch (Exception e)
                    {
                        // 🔴 SET_GAS_PARTIAL_WRITE_REPORTED_AS_TOTAL_FAILURE_1. This used to
                        // `return Fail(...)` on the first throwing cell, which told the caller
                        // the call had failed while `changed` cells of the rect were already
                        // gassed and stayed that way. A bridge caller then re-runs or assumes
                        // nothing happened. Record the cell and carry on; the partial state is
                        // reported in the body.
                        addRefused(c.x, c.z, e.GetType().Name + ": " + e.Message);
                    }
                }

                return (object)new
                {
                    success = true, action, gasType = gt.ToString(), cellsChanged = changed,
                    cellsUnchanged = unchanged,
                    cellsInRect = r.Area,
                    refusedCount = refusedTotal,
                    refusedListTruncated = refusedTotal > refused.Count,
                    refused,
                    validGasTypes = Enum.GetNames(typeof(GasType)),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/map_zones",
            Description =
                "Create, paint or delete STOCKPILE and GROWING zones, and paint the player " +
                "AREAS (home, no-roof, build-roof, allowed). " +
                "action='listZones' | 'createZone' | 'paintZone' | 'deleteZone' | " +
                "'listAreas' | 'paintArea'. " +
                "⚠️ Bulk AddCell needs CheckContiguous() afterwards or a zone can end up " +
                "internally inconsistent - this tool calls it. " +
                "📌 The 1.6 name is Area_SnowOrSandClear, renamed from Area_SnowClear.",
            ResultDescription = "success, zones[] or areas[] with cell counts.")]
        public static async Task<object> MapZones(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'listZones'|'createZone'|'paintZone'|'deleteZone'|'listAreas'|'paintArea'.")] string action = "listZones",
            [ToolParameter(Description = "'stockpile' or 'growing' for createZone.")] string zoneType = "stockpile",
            [ToolParameter(Description = "Zone label for paint/delete.")] string zone = null,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Area for paintArea: Home | NoRoof | BuildRoof | SnowOrSandClear | PollutionClear (Biotech), or the label of an allowed area.")] string area = null,
            [ToolParameter(Description = "For paintArea/paintZone: true adds, false removes.")] bool value = true,
            [ToolParameter(Description = "Plant def for a growing zone.")] string plant = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                string A = (action ?? "listZones").Trim();
                var zm = map.zoneManager; var am = map.areaManager;
                var notes = new List<string>();

                Func<object> zoneList = () => zm.AllZones.Select(z => new
                {
                    label = z.label, type = z.GetType().Name, cells = z.Cells.Count,
                }).ToList();

                if (A.Equals("listZones", StringComparison.OrdinalIgnoreCase))
                    return (object)new { success = true, action = A, zones = zoneList(), ticksGame = TicksGameSafe() };

                if (A.Equals("listAreas", StringComparison.OrdinalIgnoreCase))
                    return (object)new
                    {
                        success = true, action = A,
                        areas = am.AllAreas.Select(a => new { label = a.Label, type = a.GetType().Name, trueCount = a.TrueCount }).ToList(),
                        ticksGame = TicksGameSafe(),
                    };

                if (A.Equals("createZone", StringComparison.OrdinalIgnoreCase))
                {
                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);
                    // 🔴 MAP_ZONES_ZONETYPE_FALLS_THROUGH_1. Every value that was not exactly
                    // "growing" fell through to Zone_Stockpile, so zoneType="grow" or a typo
                    // built a STOCKPILE and reported success - and a growing zone silently
                    // dropped the `plant` argument with it. The same fall-through already
                    // closed on designate_batch's action and set_weather_buildup's mode.
                    var ZT = (zoneType ?? "").Trim();
                    if (!ZT.Equals("growing", StringComparison.OrdinalIgnoreCase)
                        && !ZT.Equals("stockpile", StringComparison.OrdinalIgnoreCase))
                        return Fail("zoneType must be 'stockpile' or 'growing', got '" + zoneType + "'. "
                                    + "Every other value used to build a stockpile silently.");
                    Zone z;
                    if (ZT.Equals("growing", StringComparison.OrdinalIgnoreCase))
                    {
                        var gz = new Zone_Growing(zm);
                        if (!string.IsNullOrEmpty(plant))
                        {
                            var pd = DefDatabase<ThingDef>.GetNamedSilentFail(plant.Trim());
                            if (pd == null) return Fail("No plant ThingDef '" + plant + "'.", DefSuggestions<ThingDef>(plant));
                            try { gz.SetPlantDefToGrow(pd); notes.Add("plant set to " + pd.defName); }
                            catch (Exception e) { notes.Add("SetPlantDefToGrow failed: " + e.Message); }
                        }
                        z = gz;
                    }
                    else
                    {
                        z = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, zm);
                        // `plant` on a stockpile is meaningless and used to be swallowed.
                        if (!string.IsNullOrEmpty(plant))
                            notes.Add("plant '" + plant + "' was IGNORED - a stockpile zone grows nothing. "
                                      + "Pass zoneType='growing' if you meant a growing zone.");
                    }

                    zm.RegisterZone(z);
                    // Report refusals rather than swallowing them: a silently short zone is
                    // exactly the kind of failure that reads as success. Measured: a 6x6
                    // stockpile took only 11 of 36 cells.
                    //
                    // 🔴 Zone.AddCell refuses ONLY two things - a cell already in THIS zone,
                    // and a thing with CanOverlapZones=false - and it refuses by Log.Error +
                    // return, never by throwing. It does NOT refuse a cell ANOTHER zone
                    // already owns: it overwrites zoneManager's zoneGrid while the old zone
                    // keeps that cell in its own list, so two zones claim it. That divergence
                    // is written to the save, ZoneManager.RebuildZoneGrid re-derives ownership
                    // from list order on every LOAD, and RemoveCell on either zone clears the
                    // grid cell for both. Vanilla's Designator_ZoneAdd never adds an owned
                    // cell (it does `unsetCells.RemoveAll(c => ZoneAt(c) != null)`), and its
                    // IsZoneableCell is the engine's own predicate for fogged cells, the
                    // 5-cell no-zone map edge, and zone-incompatible things. Use both.
                    var refusedCells = new List<object>();
                    foreach (var c in r)
                    {
                        var owner = zm.ZoneAt(c);
                        if (owner != null && owner != z)
                        {
                            if (refusedCells.Count < 12)
                                refusedCells.Add(new { x = c.x, z = c.z, why = "already owned by zone '" + owner.label + "'" });
                            continue;
                        }
                        var zr = Designator_ZoneAdd.IsZoneableCell(c, map);
                        if (!zr.Accepted)
                        {
                            if (refusedCells.Count < 12)
                                refusedCells.Add(new { x = c.x, z = c.z, why = string.IsNullOrEmpty(zr.Reason)
                                    ? "not zoneable - fogged, within 5 cells of the map edge, or a zone-incompatible thing is here"
                                    : zr.Reason });
                            continue;
                        }
                        z.AddCell(c);
                        if (!z.Cells.Contains(c) && refusedCells.Count < 12)
                            refusedCells.Add(new { x = c.x, z = c.z, why = "Zone.AddCell refused (see the log)" });
                    }
                    // A registered zone with no cells is litter that outlives the call and
                    // gets saved. Vanilla registers only once it has a cell to put in.
                    if (z.Cells.Count == 0)
                    {
                        zm.DeregisterZone(z);
                        return Fail("NOTHING was zoned - every cell in " + rect + " was refused, so the zone was not created.",
                                    new { cellsRequested = r.Area, refusedCells });
                    }
                    try { z.CheckContiguous(); notes.Add("CheckContiguous run after bulk AddCell"); } catch { }
                    int wanted1 = r.Area;
                    if (z.Cells.Count < wanted1)
                        notes.Add("ONLY " + z.Cells.Count + " of " + wanted1 + " cells were accepted - see refusedCells");
                    return (object)new
                    {
                        success = true, action = A, created = z.label,
                        cells = z.Cells.Count, cellsRequested = wanted1,
                        refusedCount = wanted1 - z.Cells.Count, refusedCells,
                        notes, zones = zoneList(), ticksGame = TicksGameSafe()
                    };
                }

                if (A.Equals("paintZone", StringComparison.OrdinalIgnoreCase) || A.Equals("deleteZone", StringComparison.OrdinalIgnoreCase))
                {
                    if (string.IsNullOrEmpty(zone)) return Fail("Give a zone label.");
                    // 🔴 MAP_ZONES_DUPLICATE_LABEL_PICKS_ONE_1. FirstOrDefault silently took
                    // whichever zone came first in AllZones, so deleteZone on an ambiguous
                    // label DELETED A ZONE THE CALLER DID NOT NAME - irreversibly, and with a
                    // clean success naming the label it thought it had deleted. Labels are not
                    // unique by construction: ZoneManager.NewZoneName gives up after 1000
                    // candidates and returns the un-deduplicated "Zone X", and its uniqueness
                    // test is ORDINAL while the lookup here is OrdinalIgnoreCase - so
                    // "Stockpile 1" and "stockpile 1" both exist legally and both match here.
                    // An exact-case match settles it; anything still ambiguous is refused
                    // rather than guessed at.
                    var wantedLabel = zone.Trim();
                    var matches = zm.AllZones
                        .Where(x => string.Equals(x.label, wantedLabel, StringComparison.OrdinalIgnoreCase)).ToList();
                    if (matches.Count > 1)
                    {
                        var exact = matches.Where(x => string.Equals(x.label, wantedLabel, StringComparison.Ordinal)).ToList();
                        if (exact.Count == 1) matches = exact;
                    }
                    if (matches.Count == 0) return Fail("No zone labelled '" + zone + "'. Have: " +
                        string.Join(", ", zm.AllZones.Select(x => x.label).ToArray()));
                    if (matches.Count > 1)
                        return Fail("AMBIGUOUS: " + matches.Count + " zones are labelled '" + wantedLabel + "'. Refusing to guess "
                                    + "which one to " + (A.Equals("deleteZone", StringComparison.OrdinalIgnoreCase) ? "DELETE" : "paint")
                                    + " - rename one first (zone labels are only unique by convention, never by construction).",
                                    new { candidates = matches.Select(x => new { label = x.label, type = x.GetType().Name, cells = x.Cells.Count }).ToList() });
                    var z = matches[0];

                    if (A.Equals("deleteZone", StringComparison.OrdinalIgnoreCase))
                    {
                        z.Delete(false);
                        return (object)new { success = true, action = A, deleted = zone, zones = zoneList(), ticksGame = TicksGameSafe() };
                    }

                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);
                    int n = 0, before2 = z.Cells.Count;
                    // 🔴 MAP_ZONES_PAINTZONE_REFUSEDCOUNT_CAPPED_1. `refused2` is capped at
                    // 12 for display, and `refusedCount` below used to be refused2.Count -
                    // the same capped list - so a paint over a big rect that refused 200
                    // cells reported refusedCount:12. refusedTotal2 counts every refusal,
                    // uncapped; the list stays capped for display, matching createZone's
                    // (already-correct) wanted1 - z.Cells.Count approach above.
                    int refusedTotal2 = 0;
                    var refused2 = new List<object>();
                    Action<int, int, string> addRefused2 = (cx, cz, why) =>
                    {
                        refusedTotal2++;
                        if (refused2.Count < 12) refused2.Add(new { x = cx, z = cz, why });
                    };
                    // Same non-throwing refusal shape as createZone above: AddCell/
                    // RemoveCell never throw, so "n++ ran without an exception" cannot
                    // distinguish an accepted cell from a refused one. Check membership
                    // before/after instead.
                    // ⚠️ Both also log a RED ERROR on a no-op call - AddCell on a cell the
                    // zone already has, RemoveCell on one it does not - so a paint over a
                    // rect that only partly overlaps the zone used to flood the log. Only
                    // call the one that has work to do.
                    // 🔴 And the ownership guard from createZone applies here too: AddCell
                    // does not refuse a cell another zone owns, it silently steals the
                    // zoneGrid entry and leaves both zones listing it.
                    foreach (var c in r)
                    {
                        bool hadBefore = z.Cells.Contains(c);
                        if (value)
                        {
                            if (!hadBefore)
                            {
                                var owner = zm.ZoneAt(c);
                                if (owner != null && owner != z)
                                {
                                    addRefused2(c.x, c.z, "already owned by zone '" + owner.label + "'");
                                    continue;
                                }
                                var zr = Designator_ZoneAdd.IsZoneableCell(c, map);
                                if (!zr.Accepted)
                                {
                                    addRefused2(c.x, c.z, string.IsNullOrEmpty(zr.Reason)
                                        ? "not zoneable - fogged, within 5 cells of the map edge, or a zone-incompatible thing is here"
                                        : zr.Reason);
                                    continue;
                                }
                                z.AddCell(c);
                            }
                        }
                        else if (hadBefore) z.RemoveCell(c);

                        bool hasAfter = z.Cells.Contains(c);
                        bool wantedChange = value ? !hadBefore : hadBefore;
                        if (hasAfter != hadBefore) n++;
                        else if (wantedChange)
                            addRefused2(c.x, c.z, "Zone." + (value ? "AddCell" : "RemoveCell") + " refused (see the log)");
                    }
                    try { z.CheckContiguous(); } catch { }
                    return (object)new
                    {
                        success = true, action = A, zone = z.label,
                        cellsAttempted = r.Area, cellsAccepted = n,
                        zoneCellsBefore = before2, zoneCellsAfter = z.Cells.Count,
                        refusedCount = refusedTotal2,
                        refusedListTruncated = refusedTotal2 > refused2.Count,
                        refusedCells = refused2,
                        note = z.Cells.Count == before2 && r.Area > 0
                            ? "NOTHING CHANGED - every cell was refused. Stockpile zones reject impassable terrain, cells already zoned, and blocking edifices."
                            : null,
                        zones = zoneList(), ticksGame = TicksGameSafe()
                    };
                }

                if (A.Equals("paintArea", StringComparison.OrdinalIgnoreCase))
                {
                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);
                    Area target = null;
                    var an = (area ?? "Home").Trim();
                    if (an.Equals("Home", StringComparison.OrdinalIgnoreCase)) target = am.Home;
                    else if (an.Equals("NoRoof", StringComparison.OrdinalIgnoreCase)) target = am.NoRoof;
                    else if (an.Equals("BuildRoof", StringComparison.OrdinalIgnoreCase)) target = am.BuildRoof;
                    // 🔑 The fixed areas are reached by TYPE, never by Label. Area.Label is a
                    // TRANSLATED string - Area_SnowOrSandClear's is "SnowAndSandClear" or
                    // "SnowClear" translated, never the token this parameter documents - so
                    // the Label fallback below can never match 'SnowOrSandClear'. Only
                    // Area_Allowed, whose label the player types, is found that way.
                    else if (an.Equals("SnowOrSandClear", StringComparison.OrdinalIgnoreCase)
                          || an.Equals("SnowClear", StringComparison.OrdinalIgnoreCase)) target = am.SnowOrSandClear;
                    else if (an.Equals("PollutionClear", StringComparison.OrdinalIgnoreCase)) target = am.PollutionClear;
                    else target = am.AllAreas.FirstOrDefault(a => string.Equals(a.Label, an, StringComparison.OrdinalIgnoreCase));
                    if (target == null) return Fail("No area '" + an + "'. Have: " +
                        string.Join(", ", am.AllAreas.Select(a => (string)a.Label).ToArray()));

                    // 🔴 MAP_ZONES_PAINTAREA_COUNTS_NOOPS_1. `cellsTouched` counted every cell
                    // in the rect, whatever the area already held - Area.Set no-ops when the
                    // value is unchanged - so painting Home over ground already in Home
                    // reported the full rect as work done, and a caller diffing the number
                    // against what it asked for could never see that nothing moved.
                    int n = 0, alreadyThatValue = 0;
                    foreach (var c in r)
                    {
                        if (target[c] == value) { alreadyThatValue++; continue; }
                        target[c] = value; n++;
                    }
                    return (object)new
                    {
                        success = true, action = A, area = target.Label,
                        cellsInRect = r.Area, cellsChanged = n, cellsAlreadySet = alreadyThatValue,
                        trueCount = target.TrueCount, ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("action must be listZones|createZone|paintZone|deleteZone|listAreas|paintArea.");
            });
        }


        // ================================================================
        //  CONNECT A TO B — the routing tool.
        //
        //  🔑 Vanilla does NOT use the pathfinder for conduits. GenStep_Power
        //  flood-fills over PLACEABILITY and reconstructs the parent chain:
        //     FloodFill(start, c => CanBuildOnTerrain(def,c) || already a transmitter,
        //               stopWhen: c == end, rememberParents: true)
        //     ReconstructLastFloodFillPath(end, cells)
        //  That route is placeable end-to-end by construction, so there is no
        //  failure handling downstream. We copy it.
        //
        //  🔴 FloodFiller is 4-CONNECTED; PathFinder is 8-CONNECTED. A path from
        //  the pathfinder MUST be densified into cardinal steps before laying
        //  conduit or THE NET BREAKS AT EVERY DIAGONAL - it looks connected and
        //  is not.
        //
        //  🔴 MOUNTAIN vs OCEAN is the whole obstacle policy:
        //   * rock is a DESTROYABLE EDIFICE - PassAllDestroyableThings prices it
        //     at 70 + 0.2/hp, so a path EXISTS. Merely expensive; mode='mine'.
        //   * WaterDeep / WaterOceanDeep declare NO affordances at all and are
        //     not even Bridgeable. Genuinely impossible - refuse, do not pretend.
        // ================================================================
        [Tool(
            "jawa/connect_cells",
            Description =
                "Route and lay a connected line of things (power conduit, wall, floor) from " +
                "one cell to another, so that after the call they really are connected. " +
                "Copies vanilla's own conduit router: a 4-connected flood fill over " +
                "PLACEABILITY, not a pathfinder, so the route is placeable end-to-end by " +
                "construction and conduit never breaks at a diagonal. " +
                "mode='strict' refuses if anything is in the way and names the obstacles; " +
                "'mine' destroys blocking rock and walls first; 'bridge' additionally lays " +
                "bridges over BRIDGEABLE water. " +
                "🔴 DEEP WATER IS UNFIXABLE at any mode - WaterDeep has no terrain " +
                "affordances and is not bridgeable, so it is reported as impossible rather " +
                "than half-built. " +
                "ATOMIC: the whole route is computed and validated before ANYTHING is " +
                "placed. A half-laid conduit is worse than a refusal. dryRun by default. " +
                "🔴 READ `displaced` as well as `cleared`: `cleared` is the edifices this tool " +
                "mined deliberately, `displaced` is everything the spawn itself wipes on the " +
                "way in - items, filth, frames, conduits - and mode='strict' refuses on it.",
            ResultDescription =
                "success, route, routeLength, placed, skipped, cleared, bridged, connected, "
                + "displaced[] naming everything the spawn destroyed, and problems[] with why.")]
        public static async Task<object> ConnectCells(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Start cell 'x,z'.")] string from = null,
            [ToolParameter(Description = "End cell 'x,z'.")] string to = null,
            [ToolParameter(Description = "ThingDef to lay. Default PowerConduit.")] string thing = "PowerConduit",
            [ToolParameter(Description = "Stuff for the thing, if it needs it.")] string stuff = null,
            [ToolParameter(Description = "'strict' | 'mine' | 'bridge'.")] string mode = "strict",
            [ToolParameter(Description = "Faction to own what is laid. Default player.")] string faction = null,
            [ToolParameter(Description = "Compute and report without placing. Default TRUE.")] bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                int ax, az, bx, bz;
                var fa = (from ?? "").Split(','); var fb = (to ?? "").Split(',');
                if (fa.Length != 2 || !int.TryParse(fa[0].Trim(), out ax) || !int.TryParse(fa[1].Trim(), out az)
                 || fb.Length != 2 || !int.TryParse(fb[0].Trim(), out bx) || !int.TryParse(fb[1].Trim(), out bz))
                    return Fail("Give from and to as 'x,z'.");
                var A = new IntVec3(ax, 0, az); var B = new IntVec3(bx, 0, bz);
                // ⚠️ MAPS ARE NOT NECESSARILY SQUARE. A quicktest map measured 100 x 400
                // on 2026-08-19, and an "out of bounds" that does not say the size sends
                // the reader hunting for a bug in the router instead of in their coords.
                if (!A.InBounds(map) || !B.InBounds(map))
                    return Fail("Cell out of bounds. This map is " + map.Size.x + " x " + map.Size.z +
                                " (x 0.." + (map.Size.x - 1) + ", z 0.." + (map.Size.z - 1) + "). " +
                                "from=" + A.x + "," + A.z + (A.InBounds(map) ? " OK" : " OUT") +
                                "  to=" + B.x + "," + B.z + (B.InBounds(map) ? " OK" : " OUT") +
                                ". Maps are not always square - do not assume.",
                                new { mapSizeX = map.Size.x, mapSizeZ = map.Size.z });

                var td = DefDatabase<ThingDef>.GetNamedSilentFail((thing ?? "PowerConduit").Trim());
                if (td == null) return Fail("No ThingDef '" + thing + "'.", DefSuggestions<ThingDef>(thing));
                ThingDef sd = null;
                if (!string.IsNullOrEmpty(stuff)) sd = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                if (td.MadeFromStuff && sd == null) sd = GenStuff.DefaultStuffFor(td);
                if (!td.MadeFromStuff) sd = null;

                string M = (mode ?? "strict").Trim().ToLowerInvariant();
                if (M != "strict" && M != "mine" && M != "bridge") return Fail("mode must be strict|mine|bridge.");

                // Same one grammar as jawa/build_batch and jawa/prefab_place - 'player',
                // 'hostile', 'none' or a FactionDef defName. Default stays the player.
                Faction fac = Faction.OfPlayer;
                if (!string.IsNullOrEmpty(faction))
                {
                    string ferr;
                    var resolved = ResolveFactionAliasOrDef(faction, out ferr);
                    if (resolved == null && ferr != null)
                        return Fail(ferr, DefSuggestions<FactionDef>(faction));
                    fac = resolved;   // 'none' resolves to null on purpose: unowned conduit.
                }

                // ---- pass 1: vanilla's own router - flood fill over placeability -------
                var route = new List<IntVec3>();
                bool clean = false;
                // 🔴 CHECK THE ENDPOINTS FIRST. Measured 2026-08-19: a run over marsh and
                // shallow water reported "NO PATH ... deep water or the map edge", which was
                // WRONG and unhelpful - PowerConduit needs the `Light` terrain affordance,
                // which marsh and shallow water lack. They ARE Bridgeable, so mode='bridge'
                // fixes them; deep water is the only genuinely hopeless case.
                Func<IntVec3, bool> isBridgeable = c =>
                { try { return c.GetAffordances(map).Any(a => a.defName == "Bridgeable"); } catch { return false; } };

                foreach (var pair in new[] { new { c = A, which = "from" }, new { c = B, which = "to" } })
                {
                    if (GenConstruct.CanBuildOnTerrain(td, pair.c, map, Rot4.North)) continue;
                    var terr = pair.c.GetTerrain(map);
                    bool br = isBridgeable(pair.c);
                    return Fail("The " + pair.which.ToUpperInvariant() + " cell itself cannot hold '" + td.defName +
                        "'. Terrain there is '" + (terr != null ? terr.defName : "?") + "'" +
                        (td.terrainAffordanceNeeded != null ? ", which does not provide the '" + td.terrainAffordanceNeeded.defName + "' affordance it needs" : "") +
                        (br ? ". That terrain IS Bridgeable - re-run with mode='bridge'." :
                              ". That terrain is NOT bridgeable, so no mode can fix it."),
                        new { cell = new { pair.c.x, pair.c.z }, terrain = terr != null ? terr.defName : null,
                              affordanceNeeded = td.terrainAffordanceNeeded != null ? td.terrainAffordanceNeeded.defName : null,
                              bridgeable = br });
                }

                // passCheck is a Predicate<IntVec3>, NOT a Func<IntVec3,bool> - the
                // overloads differ and the compiler will not coerce between them.
                // In bridge mode a Bridgeable cell counts as passable, because we can make
                // it placeable before laying anything.
                bool bridgeMode = (mode ?? "").Trim().Equals("bridge", StringComparison.OrdinalIgnoreCase);
                Predicate<IntVec3> placeable = c =>
                    c.InBounds(map) && (GenConstruct.CanBuildOnTerrain(td, c, map, Rot4.North)
                                        || (bridgeMode && isBridgeable(c)));
                try
                {
                    bool reached = false;
                    map.floodFiller.FloodFill(A, placeable,
                        (Func<IntVec3, bool>)(c => { if (c == B) { reached = true; return true; } return false; }),
                        int.MaxValue, true, null);
                    // ⚠️ FloodFiller forbids NESTED calls ("This will cause bugs") - never
                    // call another flood fill from inside a passCheck or processor.
                    if (reached)
                    {
                        map.floodFiller.ReconstructLastFloodFillPath(B, route);
                        clean = route.Count > 0;
                    }
                }
                catch (Exception e) { return Fail("FloodFill router threw: " + e.GetType().Name + ": " + e.Message); }

                var blocked = new List<object>();
                string routeKind = clean ? "clear" : null;

                // ---- pass 2: obstacles allowed, then densify to cardinal steps --------
                if (!clean)
                {
                    PawnPath path = null;
                    try
                    {
                        var parms = TraverseParms.For(TraverseMode.PassAllDestroyableThingsNotWater, Danger.Deadly, false, false, false);
                        path = map.pathFinder.FindPathNow(A, B, parms, null, PathEndMode.OnCell);
                        if (path == null || !path.Found)
                        {
                            // Say what is ACTUALLY in the way rather than assuming deep water.
                            var sample = new Dictionary<string, int>();
                            int bridgeableCells = 0, n = 0;
                            foreach (var c in GenSight.PointsOnLineOfSight(A, B))
                            {
                                if (!c.InBounds(map)) continue;
                                n++;
                                if (GenConstruct.CanBuildOnTerrain(td, c, map, Rot4.North)) continue;
                                var t2 = c.GetTerrain(map);
                                var key = t2 != null ? t2.defName : "(none)";
                                int k; sample.TryGetValue(key, out k); sample[key] = k + 1;
                                if (isBridgeable(c)) bridgeableCells++;
                            }
                            return Fail("NO ROUTE for '" + td.defName + "' from " + from + " to " + to + ". " +
                                (bridgeableCells > 0
                                    ? bridgeableCells + " cell(s) on the direct line are BRIDGEABLE - re-run with mode='bridge'."
                                    : "Nothing on the direct line is bridgeable, so no mode can fix it.") +
                                (td.terrainAffordanceNeeded != null
                                    ? " '" + td.defName + "' needs the '" + td.terrainAffordanceNeeded.defName + "' terrain affordance."
                                    : ""),
                                new { blockingTerrain = sample, bridgeableCells, cellsSampled = n });
                        }
                        var raw = new List<IntVec3>();
                        for (int i = path.NodesLeftCount - 1; i >= 0; i--) raw.Add(path.Peek(i));
                        // 🔴 densify: the pathfinder is 8-connected, conduit needs 4-connected
                        route.Clear();
                        for (int i = 0; i < raw.Count; i++)
                        {
                            if (i == 0) { route.Add(raw[0]); continue; }
                            var prev = route[route.Count - 1]; var cur = raw[i];
                            if (prev.x != cur.x && prev.z != cur.z)
                                route.Add(new IntVec3(cur.x, 0, prev.z));   // insert the corner
                            route.Add(cur);
                        }
                        routeKind = "through-obstacles";
                    }
                    finally { if (path != null) { try { path.ReleaseToPool(); } catch { } } }
                }

                // ---- classify every cell BEFORE placing anything ----------------------
                var needMine = new List<IntVec3>(); var needBridge = new List<IntVec3>();
                // 🔴 CONNECT_CELLS_NON_EDIFICE_DISPLACEMENT_UNREPORTED_1. The classification
                // below looked at GetEdifice AND NOTHING ELSE, while the commit phase spawns
                // with WipeMode.Vanish - so every NON-edifice thing GenSpawn.SpawningWipes
                // covers (loose items under an impassable thing, filth, plants under a def
                // that BlocksPlanting, an existing blueprint or frame, a conduit under any
                // EverTransmitsPower thing) was destroyed with no entry anywhere in the
                // response: not in `cleared`, not in `problems`, not in a refusal. mode
                // 'strict' promises to "refuse if anything is in the way and name the
                // obstacles" and did not even see these. jawa/build_batch already answers
                // this exact question with displaced[]; ask SpawningWipes, the engine's own
                // predicate, the same way it does - so a route that genuinely wipes nothing
                // (conduit over grass: SpawningWipes is FALSE for a plant unless the new def
                // wipesPlants or BlocksPlanting) stays a clean strict run.
                var doomed = new List<Thing>();
                foreach (var c in route)
                {
                    var here = map.thingGrid.ThingsListAtFast(c);
                    for (int i = 0; i < here.Count; i++)
                    {
                        var other = here[i];
                        if (other == null || other.Destroyed) continue;
                        if (other.def == td) continue;              // the `skipped` case below
                        if (!GenSpawn.SpawningWipes(td, other.def)) continue;
                        if (!doomed.Contains(other)) doomed.Add(other);
                    }

                    if (GenConstruct.CanBuildOnTerrain(td, c, map, Rot4.North))
                    {
                        var ed = c.GetEdifice(map);
                        if (ed != null && ed.def != td) needMine.Add(c);
                        continue;
                    }
                    var terr = c.GetTerrain(map);
                    bool bridgeable = isBridgeable(c);
                    if (bridgeable) needBridge.Add(c);
                    else blocked.Add(new { x = c.x, z = c.z, terrain = terr != null ? terr.defName : null,
                                           why = "terrain has no affordance for " + td.defName + " and is not Bridgeable - IMPOSSIBLE at any mode" });
                }

                if (blocked.Count > 0)
                    return Fail("IMPOSSIBLE: " + blocked.Count + " cell(s) on the only route cannot carry '" + td.defName +
                                "' and cannot be bridged. This is deep water or equivalent - refusing rather than laying a broken line.",
                                blocked);
                // Serialised once and reported by every exit below - a caller must be able to
                // read what the route eats whether it refuses, dry-runs or commits.
                Func<List<object>> displacedRows = () => doomed.Select(d => (object)new
                {
                    destroyed = d.def.defName,
                    x = d.Position.x, z = d.Position.z,
                    isEdifice = d.def.IsEdifice(),
                    stackCount = d.stackCount,
                }).ToList();

                if (M == "strict" && (needMine.Count > 0 || needBridge.Count > 0 || doomed.Count > 0))
                    return Fail("REFUSING in mode 'strict': the route needs " + needMine.Count + " cell(s) cleared, " +
                                needBridge.Count + " bridged, and laying '" + td.defName + "' would DESTROY " +
                                doomed.Count + " existing thing(s) that are not edifices to be mined. " +
                                "Re-run with mode='mine' or 'bridge' to accept that.",
                                new { needMine = needMine.Select(c => new { c.x, c.z }).ToList(),
                                      needBridge = needBridge.Select(c => new { c.x, c.z }).ToList(),
                                      wouldDestroy = displacedRows() });
                if (M == "mine" && needBridge.Count > 0)
                    return Fail("REFUSING: the route crosses " + needBridge.Count + " bridgeable water cell(s). Use mode='bridge'.");

                // Resolve the bridge BEFORE the commit phase. The mining loop runs first, so
                // discovering a missing Bridge def down there would leave edifices already
                // destroyed and then lay conduit over open water - the half-laid line this
                // tool exists to refuse.
                var bridgeDef = needBridge.Count > 0 ? DefDatabase<TerrainDef>.GetNamedSilentFail("Bridge") : null;
                if (needBridge.Count > 0 && bridgeDef == null)
                    return Fail("REFUSING: the route needs " + needBridge.Count + " bridged cell(s) but there is no " +
                                "TerrainDef 'Bridge' in this game. Nothing was changed.");

                if (dryRun)
                    return (object)new
                    {
                        success = true, dryRun = true, route = routeKind, routeLength = route.Count,
                        wouldMine = needMine.Count, wouldBridge = needBridge.Count,
                        // Everything the spawn itself would wipe on the way in, edifice or
                        // not - the number a dry run exists to hand back before committing.
                        wouldDestroyCount = doomed.Count,
                        wouldDestroy = displacedRows(),
                        firstCells = route.Take(6).Select(c => new { c.x, c.z }).ToList(),
                        note = "DRY RUN - nothing placed. Pass dryRun=false.",
                        ticksGame = TicksGameSafe(),
                    };

                // ---- commit -----------------------------------------------------------
                // 🔴 CONNECT_CELLS_COMMIT_PHASE_UNGUARDED_1. Destroy and SetTerrain ran bare,
                // so one throwing cell escaped the whole tool through InvokeAsync - after
                // some edifices were already destroyed and some cells already bridged. The
                // caller got an exception, not a report, and the map kept the half-cleared
                // route this tool exists to refuse. Catch per cell and carry the damage in
                // the body instead.
                // Materialise the victims BEFORE anything is destroyed: stackCount reads 0 on
                // a destroyed Thing, so taking this snapshot afterwards would report the loss
                // as an empty stack.
                var displaced = displacedRows();

                int cleared = 0, bridged = 0, placed = 0, skipped = 0;
                foreach (var c in needMine)
                {
                    try
                    {
                        var ed = c.GetEdifice(map);
                        if (ed != null) { ed.Destroy(DestroyMode.KillFinalize); cleared++; }
                    }
                    catch (Exception e)
                    { blocked.Add(new { x = c.x, z = c.z, why = "clearing failed: " + e.GetType().Name + ": " + e.Message }); }
                }
                foreach (var c in needBridge)
                {
                    try { map.terrainGrid.SetTerrain(c, bridgeDef); bridged++; }
                    catch (Exception e)
                    { blocked.Add(new { x = c.x, z = c.z, why = "bridging failed: " + e.GetType().Name + ": " + e.Message }); }
                }
                foreach (var c in route)
                {
                    var existing = map.thingGrid.ThingsListAtFast(c).FirstOrDefault(t => t.def == td);
                    if (existing != null) { skipped++; continue; }
                    try
                    {
                        var t = ThingMaker.MakeThing(td, sd);
                        t.SetFactionDirect(fac);
                        // 🔴 CONNECT_CELLS_SPAWN_NOT_GATED_1. GenSpawn.Spawn returns null (and
                        // just logs, never throws) on an out-of-bounds cell or a thing that
                        // ends up with 0 stackCount - it does not always throw on failure. The
                        // return value used to be discarded and `placed++` ran unconditionally,
                        // so a spawn the engine itself refused was still counted as placed -
                        // the same "gate on real success" trap jawa/build_batch already closed
                        // on its own spawn path. Check the return like build_batch does.
                        var spawned = GenSpawn.Spawn(t, c, map, Rot4.North, WipeMode.Vanish);
                        if (spawned != null) placed++;
                        else blocked.Add(new { x = c.x, z = c.z, why = "GenSpawn.Spawn returned null" });
                    }
                    catch (Exception e) { blocked.Add(new { x = c.x, z = c.z, why = e.Message }); }
                }

                return (object)new
                {
                    success = true, dryRun = false, route = routeKind, routeLength = route.Count,
                    placed, skipped, cleared, bridged,
                    // 🔑 The LINE IS ONLY CONNECTED if every route cell ended up carrying the
                    // thing. placed+skipped short of routeLength means a gap, and this tool's
                    // whole promise is "after the call they really are connected" - so say it
                    // outright rather than leaving the caller to subtract.
                    connected = blocked.Count == 0 && (placed + skipped) == route.Count,
                    // 🔑 `cleared` counts EDIFICES this tool mined on purpose. `displaced`
                    // counts what the spawn itself wiped on the way in - items, filth, frames,
                    // conduits - which no counter here used to show at all.
                    displacedCount = displaced.Count,
                    displaced,
                    problemCount = blocked.Count,
                    problems = blocked,
                    message = (blocked.Count == 0 && (placed + skipped) == route.Count)
                        ? null
                        : "NOT CONNECTED: " + (route.Count - placed - skipped) + " of " + route.Count +
                          " route cell(s) have no '" + td.defName + "'. See problems[].",
                    note = "Run jawa/map_commit. For power, consumers within 6 cells auto-connect; conduits themselves must be CONTIGUOUS, which the 4-connected route guarantees.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

    }
}