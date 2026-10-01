// JawaBenchShadeGridTools.cs - SHADEGRID_BRIDGE_READER_1.
//
// Read-only. Reports the sun/shade state of the current map for
// STILLSAND_SUN_LIVE_VERIFY_1: the shade grid's sun elevation and effective heat
// kind, ShadeAt/ExposureAt per requested cell, the pinned sun's IsActive, and the
// current sky glow.
//
// Reflection, not a project reference: mandrake.rm.creaturebehaviors may be absent
// from a list, and this file must load and report absence rather than fail the
// assembly (same reasoning as JawaBenchCathedralAttitudeTools.cs).
//
// THREAD AFFINITY: reads MapComponent state - main thread only.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static Type FindTypeByFullName(string fullName) =>
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } })
                .FirstOrDefault(t => t.FullName == fullName);

        private static object ReadMember(object obj, string name)
        {
            if (obj == null) return null;
            PropertyInfo p = obj.GetType().GetProperty(name, BindingFlags.Public | BindingFlags.Instance);
            if (p == null) throw new MissingMemberException(obj.GetType().FullName, name);
            return p.GetValue(obj, null);
        }

        [Tool(
            "jawa/shadegrid_read",
            Description = "READ-ONLY. Reports the current map's sun and shade state by reflection into " +
                "RM_MapComponent_ShadeGrid and RM_MapComponent_PinnedSun (CreatureBehaviors): shade-grid " +
                "sunElevationDegrees and effectiveHeatKind, pinned-sun isActive and its own elevation, the " +
                "map's current sky glow (skyManager.CurSkyGlow) and the celestial sun glow, and for each " +
                "requested cell ShadeAt and ExposureAt. Cells are given as 'x,z;x,z;...' (max 200); an " +
                "out-of-bounds cell is reported with inBounds=false, never silently dropped; an unparseable " +
                "token is listed under badTokens. present=false (not an error) when CreatureBehaviors is not " +
                "loaded or the map has no such component. A map whose biome has no sun-heat extension " +
                "legitimately reads exposure 0 and kind overhead; sunElevationDegrees is NaN before the grid " +
                "has recomputed (reported as null).",
            ResultDescription = "success, present, mapTile, sunHeatActive, shadeGrid{sunElevationDegrees, " +
                "effectiveHeatKind, isDirectional}, pinnedSun{present, isActive, sunElevationDegrees}, " +
                "skyGlow, celestialSunGlow, cells[{x,z,inBounds,shade,exposure}], badTokens, ticksGame.")]
        public static async Task<object> ShadeGridRead(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cells as 'x,z;x,z;...' (max 200). Empty reads only the map-level values.")] string cells = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null)
                {
                    return (object)new { success = true, present = false, reason = "no current map", ticksGame = TicksGameSafe() };
                }

                Type gridType = FindTypeByFullName("RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid");
                Type sunType = FindTypeByFullName("RimMandrake.CreatureBehaviors.RM_MapComponent_PinnedSun");
                if (gridType == null)
                {
                    return (object)new { success = true, present = false, reason = "CreatureBehaviors not loaded", ticksGame = TicksGameSafe() };
                }

                object grid = map.GetComponent(gridType);
                if (grid == null)
                {
                    return (object)new { success = true, present = false, reason = "map has no RM_MapComponent_ShadeGrid", ticksGame = TicksGameSafe() };
                }

                MethodInfo shadeAt = gridType.GetMethod("ShadeAt", BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(IntVec3) }, null);
                MethodInfo exposureAt = gridType.GetMethod("ExposureAt", BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(IntVec3) }, null);
                if (shadeAt == null || exposureAt == null)
                {
                    return Fail("ShadeAt/ExposureAt not found by reflection (renamed or removed).");
                }

                var badTokens = new List<string>();
                var cellList = new List<object>();
                if (!string.IsNullOrWhiteSpace(cells))
                {
                    string[] tokens = cells.Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries);
                    if (tokens.Length > 200)
                    {
                        return Fail($"Too many cells: {tokens.Length} > 200. Split the call.");
                    }
                    foreach (string raw in tokens)
                    {
                        string[] xz = raw.Trim().Split(',');
                        if (xz.Length != 2 || !int.TryParse(xz[0].Trim(), out int x) || !int.TryParse(xz[1].Trim(), out int z))
                        {
                            badTokens.Add(raw);
                            continue;
                        }
                        var c = new IntVec3(x, 0, z);
                        if (!c.InBounds(map))
                        {
                            cellList.Add(new { x, z, inBounds = false, shade = (float?)null, exposure = (float?)null });
                            continue;
                        }
                        float shade = (float)shadeAt.Invoke(grid, new object[] { c });
                        float exposure = (float)exposureAt.Invoke(grid, new object[] { c });
                        cellList.Add(new { x, z, inBounds = true, shade = (float?)shade, exposure = (float?)exposure });
                    }
                }

                float elev = (float)ReadMember(grid, "SunElevationDegrees");
                object kind = ReadMember(grid, "EffectiveHeatKind");

                object pinned = new { present = false, isActive = (bool?)null, sunElevationDegrees = (float?)null };
                if (sunType != null)
                {
                    object sun = map.GetComponent(sunType);
                    if (sun != null)
                    {
                        float pe = (float)ReadMember(sun, "SunElevationDegrees");
                        pinned = new
                        {
                            present = true,
                            isActive = (bool?)(bool)ReadMember(sun, "IsActive"),
                            sunElevationDegrees = float.IsNaN(pe) ? (float?)null : pe
                        };
                    }
                }

                return (object)new
                {
                    success = true,
                    present = true,
                    mapTile = map.Tile.ToString(),
                    sunHeatActive = (bool)ReadMember(grid, "SunHeatActive"),
                    shadeGrid = new
                    {
                        sunElevationDegrees = float.IsNaN(elev) ? (float?)null : elev,
                        effectiveHeatKind = kind?.ToString(),
                        isDirectional = (bool)ReadMember(grid, "IsDirectional")
                    },
                    pinnedSun = pinned,
                    skyGlow = map.skyManager.CurSkyGlow,
                    celestialSunGlow = GenCelestial.CurCelestialSunGlow(map),
                    cells = cellList,
                    badTokens,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
