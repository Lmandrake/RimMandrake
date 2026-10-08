using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/kill_hostiles (BRIDGE_KILL_HOSTILES_TOOL_1): review and test maps get contaminated by manhunters and raiders,
    // and the standing policy is to sweep them. Hostility is the engine's own GenHostility.HostileTo(pawn, player
    // faction), which also covers manhunting animals; colonists, tamed animals and prisoners are never hostile by it.
    //
    // jawa/world_tile_cache_reset (TILE_TEMP_CACHE_RESET_TOOL_1): Tile's private caches (hillinessLabelCached,
    // cachedMinTemp, cachedMaxTemp, tmpHasSecondaryBiome/tmpSecondaryBiome) are never invalidated by RimWorld, so a
    // retiled temperature does not reach Tile.MinTemperature (and so CanEverPlantAt / plant growth) until a reload.
    // Nulling them by reflection makes the next getter call recompute. jawa/world_cache_audit (JawaBenchCacheTools.cs)
    // is the instrument: audit, reset, audit again and expect staleTotal 0.
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/kill_hostiles",
            Description =
                "Kill every spawned pawn on a map that is hostile to the player (GenHostility.HostileTo, so manhunting " +
                "animals count; colonists, tamed animals, prisoners and neutral visitors never do). Optional filters " +
                "narrow it to a faction defName or a pawn kind/race defName. dryRun lists without killing. " +
                "destroyCorpses removes the bodies too, so a review map is left clean.",
            ResultDescription = "success, mapId, killed (count), killedPawns[{id,kind,faction}], survivorsNonHostile " +
                "(spawned pawns left, a control: it must not drop), dryRun.")]
        public static async Task<object> KillHostiles(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map uniqueID; -1 (default) is the current map.")] int mapId = -1,
            [ToolParameter(Description = "Only pawns of this faction defName (e.g. Pirate). Empty: any hostile faction, and factionless manhunters.")] string factionDef = null,
            [ToolParameter(Description = "Only pawns whose kindDef or race defName equals this.")] string pawnDef = null,
            [ToolParameter(Description = "List what would be killed, kill nothing. Default false.")] bool dryRun = false,
            [ToolParameter(Description = "Also destroy the corpses. Default true.")] bool destroyCorpses = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = FwResolveMap(mapId, out string merr);
                if (map == null) return Fail(merr ?? "No map.");
                Faction player = Faction.OfPlayer;
                var targets = new List<Pawn>();
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    if (p == null || p.Dead || p.Faction == player) continue;
                    if (!GenHostility.HostileTo(p, player)) continue;
                    if (!string.IsNullOrEmpty(factionDef) && (p.Faction == null || p.Faction.def.defName != factionDef)) continue;
                    if (!string.IsNullOrEmpty(pawnDef) && p.kindDef?.defName != pawnDef && p.def.defName != pawnDef) continue;
                    targets.Add(p);
                }
                var rows = targets.Select(p => new { id = p.ThingID, kind = p.kindDef?.defName, faction = p.Faction?.def.defName }).ToList();
                int killed = 0;
                if (!dryRun)
                {
                    foreach (Pawn p in targets)
                    {
                        if (p.Dead || !p.Spawned) continue;
                        p.Kill(null);
                        killed++;
                        if (destroyCorpses && p.Corpse != null && !p.Corpse.Destroyed) p.Corpse.Destroy();
                    }
                }
                int survivors = map.mapPawns.AllPawnsSpawned.Count(p => !p.Dead && !GenHostility.HostileTo(p, player));
                int hostilesLeft = map.mapPawns.AllPawnsSpawned.Count(p => !p.Dead && p.Faction != player && GenHostility.HostileTo(p, player));
                return new
                {
                    success = true,
                    mapId = map.uniqueID,
                    dryRun,
                    matched = targets.Count,
                    killed,
                    killedPawns = rows,
                    survivorsNonHostile = survivors,
                    hostilesLeft,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        private static readonly FieldInfo FiTmpSecondaryBiome =
            typeof(Tile).GetField("tmpSecondaryBiome", BindingFlags.NonPublic | BindingFlags.Instance);

        [Tool(
            "jawa/world_tile_cache_reset",
            Description =
                "Null Tile's private caches (hillinessLabelCached, cachedMinTemp, cachedMaxTemp, tmpHasSecondaryBiome, " +
                "tmpSecondaryBiome) by reflection on the named tiles, so the next getter recomputes them: a retiled " +
                "temperature then reaches Tile.MinTemperature, CanEverPlantAt and plant growth without a reload. " +
                "Refuses (does nothing) if any field fails to resolve. Pair with jawa/world_cache_audit: audit, reset, " +
                "audit again. A whole-planet reset needs all=true.",
            ResultDescription = "success, tilesReset, cleared per cache (how many were populated before), refused[], " +
                "verifiedNull (every targeted cache reads null after the write).")]
        public static async Task<object> WorldTileCacheReset(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids.")] string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to'. Combines with 'tiles'.")] string range = null,
            [ToolParameter(Description = "Reset every surface tile. Default false; tiles/range are required otherwise.")] bool all = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (FiHillinessLabelCached == null || FiCachedMinTemp == null || FiCachedMaxTemp == null
                    || FiTmpHasSecondaryBiome == null || FiTmpSecondaryBiome == null)
                    return Fail("Tile's private cache fields could not be resolved by reflection; REFUSING rather than reporting a reset that did nothing.",
                        new { hillinessLabelCached = FiHillinessLabelCached != null, cachedMinTemp = FiCachedMinTemp != null,
                              cachedMaxTemp = FiCachedMaxTemp != null, tmpHasSecondaryBiome = FiTmpHasSecondaryBiome != null,
                              tmpSecondaryBiome = FiTmpSecondaryBiome != null });
                WorldGrid grid = Find.WorldGrid;
                if (grid == null) return Fail("No world grid - is a world loaded?");
                if (!all && string.IsNullOrEmpty(tiles) && string.IsNullOrEmpty(range))
                    return Fail("Name tiles or a range, or pass all=true for the whole planet.");

                var ids = new List<int>();
                var refused = new List<object>();
                if (all) for (int i = 0; i < grid.TilesCount; i++) ids.Add(i);
                if (!string.IsNullOrEmpty(tiles))
                    foreach (string part in tiles.Split(','))
                    {
                        if (int.TryParse(part.Trim(), out int n)) ids.Add(n);
                        else refused.Add(new { value = part.Trim(), reason = "not an integer" });
                    }
                if (!string.IsNullOrEmpty(range))
                {
                    string[] ft = range.Split('-');
                    if (ft.Length == 2 && int.TryParse(ft[0].Trim(), out int a) && int.TryParse(ft[1].Trim(), out int b))
                    {
                        if (b < a) { int t = a; a = b; b = t; }
                        for (int i = a; i <= b; i++) ids.Add(i);
                    }
                    else refused.Add(new { value = range, reason = "not a 'from-to' range" });
                }

                int reset = 0, hill = 0, minT = 0, maxT = 0, sec = 0; bool allNull = true;
                foreach (int id in ids.Distinct())
                {
                    if (id < 0 || id >= grid.TilesCount) { if (refused.Count < 50) refused.Add(new { value = id, reason = "out of range" }); continue; }
                    Tile t = grid[id];
                    if (t == null) { if (refused.Count < 50) refused.Add(new { value = id, reason = "null tile" }); continue; }
                    if (FiHillinessLabelCached.GetValue(t) != null) hill++;
                    if (FiCachedMinTemp.GetValue(t) != null) minT++;
                    if (FiCachedMaxTemp.GetValue(t) != null) maxT++;
                    if (FiTmpHasSecondaryBiome.GetValue(t) != null) sec++;
                    FiHillinessLabelCached.SetValue(t, null);
                    FiCachedMinTemp.SetValue(t, null);
                    FiCachedMaxTemp.SetValue(t, null);
                    FiTmpHasSecondaryBiome.SetValue(t, null);
                    FiTmpSecondaryBiome.SetValue(t, null);
                    if (FiHillinessLabelCached.GetValue(t) != null || FiCachedMinTemp.GetValue(t) != null
                        || FiCachedMaxTemp.GetValue(t) != null || FiTmpHasSecondaryBiome.GetValue(t) != null) allNull = false;
                    reset++;
                }
                return new
                {
                    success = allNull && reset > 0,
                    tilesReset = reset,
                    clearedPopulated = new { hilliness = hill, minTemp = minT, maxTemp = maxT, secondaryBiome = sec },
                    verifiedNull = allNull,
                    refusedCount = refused.Count,
                    refused,
                    note = "Run jawa/world_cache_audit after this to confirm; only the Tile caches are touched.",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
