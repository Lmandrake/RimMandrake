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
                    returned = outp.Count,
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
                var refused = new List<object>();

                foreach (var c in r)
                {
                    try
                    {
                        if (set)
                        {
                            // SetFoundation errors when under-terrain is present; check first
                            // so the caller gets a reason instead of a red log line.
                            if (tg.UnderTerrainAt(c) != null)
                            { if (refused.Count < 20) refused.Add(new { x = c.x, z = c.z, why = "cell has under-terrain; strip the floor first" }); continue; }
                            tg.SetFoundation(c, sub);
                            changed++;
                        }
                        else
                        {
                            if (tg.FoundationAt(c) == null) continue;
                            if (!tg.CanRemoveFoundationAt(c))
                            { if (refused.Count < 20) refused.Add(new { x = c.x, z = c.z, why = "CanRemoveFoundationAt false" }); continue; }
                            tg.RemoveFoundation(c, doLeavings);
                            changed++;
                        }
                    }
                    catch (Exception e)
                    {
                        if (refused.Count < 20) refused.Add(new { x = c.x, z = c.z, why = e.GetType().Name + ": " + e.Message });
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
                    refusedCount = refused.Count,
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

                int changed = 0; var refused = new List<object>();
                foreach (var c in r)
                {
                    try
                    {
                        switch (L)
                        {
                            case "under": tg.SetUnderTerrain(c, td); changed++; break;
                            case "temp":
                                tg.SetTempTerrain(c, td); changed++;
                                if (expireInTicks > 0 && map.tempTerrain != null)
                                    map.tempTerrain.QueueRemoveTerrain(c, Find.TickManager.TicksGame + expireInTicks);
                                break;
                            case "color": tg.SetTerrainColor(c, cd); changed++; break;
                            case "removetop":
                                if (!tg.CanRemoveTopLayerAt(c))
                                { if (refused.Count < 20) refused.Add(new { x = c.x, z = c.z, why = "CanRemoveTopLayerAt false" }); break; }
                                tg.RemoveTopLayer(c, doLeavings); changed++;
                                break;
                        }
                    }
                    catch (Exception e)
                    { if (refused.Count < 20) refused.Add(new { x = c.x, z = c.z, why = e.GetType().Name + ": " + e.Message }); }
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
                    refusedCount = refused.Count, refused,
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
                int changed = 0;

                try
                {
                    if (A == "unfogall") { fg.ClearAllFog(); changed = map.Area; }
                    else if (A == "floodunfog")
                    {
                        int x, z;
                        var b = (cell ?? "").Split(',');
                        if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                            return Fail("Give cell as 'x,z' for floodUnfog.");
                        fg.FloodUnfogAdjacent(new IntVec3(x, 0, z), sendLetters);
                        changed = -1;   // engine decides how many
                    }
                    else
                    {
                        CellRect r;
                        if (!TryRect(rect, map, out r, out err)) return Fail(err);
                        if (A == "unfog") { foreach (var c in r) { if (fg.IsFogged(c)) { fg.Unfog(c); changed++; } } }
                        else if (A == "refog") { fg.Refog(r); changed = r.Area; }
                        else return Fail("action must be unfog|unfogAll|refog|floodUnfog.");
                    }
                }
                catch (Exception e) { return Fail("Fog op failed: " + e.GetType().Name + ": " + e.Message); }

                int fogged = 0;
                foreach (var c in map.AllCells) if (fg.IsFogged(c)) fogged++;

                return (object)new
                {
                    success = true, action = A, cellsChanged = changed,
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
                int changed = 0;

                try
                {
                    if (M == "radial")
                    {
                        int x, z; var b = (center ?? "").Split(',');
                        if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                            return Fail("Give centre as 'x,z' for radial.");
                        var c0 = new IntVec3(x, 0, z);
                        if (sand) WeatherBuildupUtility.AddSandRadial(c0, map, radius, depth);
                        else WeatherBuildupUtility.AddSnowRadial(c0, map, radius, depth);
                        changed = -1;
                    }
                    else
                    {
                        CellRect r;
                        if (!TryRect(rect, map, out r, out err)) return Fail(err);
                        foreach (var c in r)
                        {
                            if (sand) { if (M == "add") map.sandGrid.AddDepth(c, depth); else map.sandGrid.SetDepth(c, depth); }
                            else { if (M == "add") map.snowGrid.AddDepth(c, depth); else map.snowGrid.SetDepth(c, depth); }
                            changed++;
                        }
                    }
                }
                catch (Exception e) { return Fail(kind + " " + M + " failed: " + e.GetType().Name + ": " + e.Message); }

                var back = new List<object>();
                {
                    CellRect rr;
                    if (TryRect(rect ?? "0,0,1,1", map, out rr, out err))
                        foreach (var c in rr)
                        {
                            if (back.Count >= Math.Max(0, readBack)) break;
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

                int changed = 0;
                foreach (var c in r)
                {
                    try { map.deepResourceGrid.SetAt(c, td, td == null ? 0 : count); changed++; }
                    catch (Exception e) { return Fail("SetAt failed at " + c + ": " + e.Message); }
                }

                var back = new List<object>();
                foreach (var c in r)
                {
                    if (back.Count >= Math.Max(0, readBack)) break;
                    var d = map.deepResourceGrid.ThingDefAt(c);
                    back.Add(new { x = c.x, z = c.z, def = d != null ? d.defName : null, count = map.deepResourceGrid.CountAt(c) });
                }
                return (object)new { success = true, cellsChanged = changed, cells = back, ticksGame = TicksGameSafe() };
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
                "Call jawa/map_commit after a batch.",
            ResultDescription = "success, placed, failed[], and a read-back of each spawned thing.")]
        public static async Task<object> BuildBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'ThingDef:x,z[,rot]' ops separated by ';'.")] string ops = null,
            [ToolParameter(Description = "Stuff ThingDef, e.g. WoodLog, Steel, Granite.")] string stuff = null,
            [ToolParameter(Description = "Faction defName to own the buildings. Empty = no faction.")] string faction = null,
            [ToolParameter(Description = "Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary.")] string quality = null,
            [ToolParameter(Description = "Hit points. -1 leaves the PostMake roll.")] int hitPoints = -1,
            [ToolParameter(Description = "Wipe whatever occupies the cell first. Default true.")] bool wipeExisting = true,
            [ToolParameter(Description = "Read back at most this many things. Default 8.")] int readBack = 8)
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

                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction was generated in this world.");
                }

                QualityCategory q = QualityCategory.Normal; bool setQ = false;
                if (!string.IsNullOrEmpty(quality))
                {
                    try { q = (QualityCategory)Enum.Parse(typeof(QualityCategory), quality.Trim(), true); setQ = true; }
                    catch { return Fail("Bad quality '" + quality + "'. Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary."); }
                }

                int placed = 0; var failures = new List<object>(); var spawnedThings = new List<Thing>();

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
                        if (wipeExisting) GenSpawn.WipeExistingThings(c, rot, td, map, DestroyMode.Vanish);

                        var t = ThingMaker.MakeThing(td, useStuff);
                        if (fac != null) t.SetFactionDirect(fac);
                        if (setQ)
                        {
                            var cq = t.TryGetComp<CompQuality>();
                            if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider);
                        }
                        var spawned = GenSpawn.Spawn(t, c, map, rot);

                        // AFTER MakeThing/PostMake, or the startingHpRange roll wins.
                        if (hitPoints >= 0 && spawned != null && spawned.def.useHitPoints)
                            spawned.HitPoints = Mathf.Clamp(hitPoints, 1, spawned.MaxHitPoints);

                        // Some defs (wind turbines) do their side effects only here.
                        if (td.PlaceWorkers != null)
                            foreach (var pw in td.PlaceWorkers)
                                try { pw.PostPlace(map, td, c, rot); } catch { }

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
                    });
                }

                return (object)new
                {
                    success = true,
                    placed, failedCount = failures.Count, failed = failures,
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
                    try { canSpawn = GenSpawn.CanSpawnAt(td, c, map, rr); } catch { }

                    var occ = map.thingGrid.ThingsListAtFast(c).Select(t => t.def.defName).Distinct().ToList();
                    if (canPlace) ok++;
                    cells.Add(new { x = c.x, z = c.z, canPlace, reason, canSpawn, occupants = occ });
                }
                return (object)new
                {
                    success = true, def = td.defName, stuff = sd != null ? sd.defName : null,
                    acceptableCells = ok, tested = cells.Count, godMode, cells,
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
                "action='add' | 'remove' | 'query'. Cell designations take a rect; thing " +
                "designations resolve against whatever occupies each cell. " +
                "⚠️ AddDesignation logs a red error on double-add, so this queries first.",
            ResultDescription = "success, added, removed, existing[], and the designation list.")]
        public static async Task<object> DesignateBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'add' | 'remove' | 'query'.")] string action = "add",
            [ToolParameter(Description = "DesignationDef name, e.g. Mine, Deconstruct, HarvestPlant.")] string designation = null,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Target things in the cell rather than the cell itself. Default auto.")] bool onThings = false,
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
                    var rows = new List<object>();
                    foreach (var d in dm.AllDesignations)
                    {
                        if (dd != null && d.def != dd) continue;
                        if (rows.Count >= Math.Max(1, limit)) break;
                        rows.Add(new
                        {
                            def = d.def.defName,
                            x = d.target.Cell.x, z = d.target.Cell.z,
                            thing = d.target.HasThing ? d.target.Thing.def.defName : null,
                        });
                    }
                    return (object)new { success = true, action = "query", total = dm.AllDesignations.Count(), returned = rows.Count, designations = rows, ticksGame = TicksGameSafe() };
                }

                if (dd == null) return Fail("Give a DesignationDef for add/remove.");
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                int added = 0, removed = 0, already = 0;
                var problems = new List<object>();

                foreach (var c in r)
                {
                    try
                    {
                        if (onThings)
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
                    catch (Exception e) { if (problems.Count < 15) problems.Add(new { x = c.x, z = c.z, why = e.GetType().Name + ": " + e.Message }); }
                }

                return (object)new
                {
                    success = true, action = A, designation = dd.defName,
                    added, removed, alreadyPresent = already,
                    onThings, problems,
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
                // PrefabDef.things is INTERNAL; GetThings() is the public route and it
                // expands rects and position lists into one entry per cell.
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
                catch (Exception e) { Log.Warning("[JawaBench] prefab_capture: GetThings threw: " + e.Message); }

                return (object)new
                {
                    success = true,
                    name,
                    defName = pf.defName,
                    size = new { x = pf.size.x, z = pf.size.z },
                    capturedFrom = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    thingCount = things,
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

                Faction fac = null;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }

                bool can;
                try { can = PrefabUtility.CanSpawnPrefab(pf, map, c0, rr); }
                catch (Exception e) { return Fail("CanSpawnPrefab threw: " + e.GetType().Name + ": " + e.Message); }

                if (checkOnly || !can)
                    return (object)new
                    {
                        success = can,
                        checkedOnly = true,
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

                GasType gt;
                try { gt = (GasType)Enum.Parse(typeof(GasType), (gasType ?? "").Trim(), true); }
                catch { return Fail("Bad gasType '" + gasType + "'. Valid: " + string.Join(", ", Enum.GetNames(typeof(GasType)))); }

                bool add = string.Equals(action, "add", StringComparison.OrdinalIgnoreCase);
                bool clr = string.Equals(action, "clear", StringComparison.OrdinalIgnoreCase);
                if (!add && !clr) return Fail("action must be add|clear.");

                int changed = 0;
                foreach (var c in r)
                {
                    try
                    {
                        if (add) { map.gasGrid.AddGas(c, gt, Math.Max(1, Math.Min(255, density))); changed++; }
                        else { map.gasGrid.ClearCellUnsafe(c); changed++; }
                    }
                    catch (Exception e) { return Fail("Gas op failed at " + c + ": " + e.GetType().Name + ": " + e.Message); }
                }

                return (object)new
                {
                    success = true, action, gasType = gt.ToString(), cellsChanged = changed,
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
            [ToolParameter(Description = "Area name for paintArea: Home | NoRoof | BuildRoof | SnowOrSandClear.")] string area = null,
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
                    Zone z;
                    if (zoneType.Equals("growing", StringComparison.OrdinalIgnoreCase))
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
                    else z = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, zm);

                    zm.RegisterZone(z);
                    // Report refusals rather than swallowing them: a cell can be refused
                    // for impassable terrain, an existing zone, or a blocking edifice, and
                    // a silently short zone is exactly the kind of failure that reads as
                    // success. Measured: a 6x6 stockpile took only 11 of 36 cells.
                    var refusedCells = new List<object>();
                    foreach (var c in r)
                    {
                        try { z.AddCell(c); }
                        catch (Exception ex)
                        {
                            if (refusedCells.Count < 12)
                                refusedCells.Add(new { x = c.x, z = c.z, why = ex.Message, terrain = c.GetTerrain(map) != null ? c.GetTerrain(map).defName : null });
                        }
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
                    var z = zm.AllZones.FirstOrDefault(x => string.Equals(x.label, zone.Trim(), StringComparison.OrdinalIgnoreCase));
                    if (z == null) return Fail("No zone labelled '" + zone + "'. Have: " +
                        string.Join(", ", zm.AllZones.Select(x => x.label).ToArray()));

                    if (A.Equals("deleteZone", StringComparison.OrdinalIgnoreCase))
                    {
                        z.Delete(false);
                        return (object)new { success = true, action = A, deleted = zone, zones = zoneList(), ticksGame = TicksGameSafe() };
                    }

                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);
                    int n = 0, before2 = z.Cells.Count;
                    var refused2 = new List<object>();
                    foreach (var c in r)
                    {
                        try { if (value) z.AddCell(c); else z.RemoveCell(c); n++; }
                        catch (Exception ex)
                        {
                            if (refused2.Count < 12)
                                refused2.Add(new { x = c.x, z = c.z, why = ex.Message, terrain = c.GetTerrain(map) != null ? c.GetTerrain(map).defName : null });
                        }
                    }
                    try { z.CheckContiguous(); } catch { }
                    return (object)new
                    {
                        success = true, action = A, zone = z.label,
                        cellsAttempted = r.Area, cellsAccepted = n,
                        zoneCellsBefore = before2, zoneCellsAfter = z.Cells.Count,
                        refusedCount = refused2.Count, refusedCells = refused2,
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
                    else target = am.AllAreas.FirstOrDefault(a => string.Equals(a.Label, an, StringComparison.OrdinalIgnoreCase));
                    if (target == null) return Fail("No area '" + an + "'. Have: " +
                        string.Join(", ", am.AllAreas.Select(a => (string)a.Label).ToArray()));

                    int n = 0;
                    foreach (var c in r) { target[c] = value; n++; }
                    return (object)new
                    {
                        success = true, action = A, area = target.Label, cellsTouched = n,
                        trueCount = target.TrueCount, ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("action must be listZones|createZone|paintZone|deleteZone|listAreas|paintArea.");
            });
        }

    }
}