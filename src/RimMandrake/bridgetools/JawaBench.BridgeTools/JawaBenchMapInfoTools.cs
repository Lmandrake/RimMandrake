// JawaBenchMapInfoTools.cs - what map am I standing on, and where on the planet is it?
//
// NO_TOOL_REPORTS_MAP_TILE_1, measured 2026-08-26: a regex over all 291 live tool
// descriptions for "current map's tile" / "map parent" / "tile of the map" returned
// NOTHING. rimworld/get_game_info gives status/ticksGame/mapCount/selectedPawns;
// rimworld/get_camera_state gives mapId/mapIndex; rimworld/get_cell_info's state gives
// currentMapId. None of them is a WORLD TILE.
//
// WHY THAT MATTERS RATHER THAN BEING A TIDINESS COMPLAINT
// ======================================================
// The map's climate, biome, hilliness and landmarks all come from its world tile, and
// jawa/world_tile_set + jawa/world_commit can change any of them ON A RUNNING MAP -
// measured the same day, 14.7 C -> -66.3 C and back. That is the strongest climate
// lever this bridge has, and it is unusable if you cannot name the tile.
//
// THE WORKAROUND THIS REPLACES, AND WHY IT WAS NOT GOOD ENOUGH
// ===========================================================
//   jawa/world_objects_get {limit: 400} -> the Settlement whose faction is PlayerColony
//                                       -> its `tile`
// It works on a settled map. It returns DUPLICATES when a quicktest has two player
// settlements on one tile (measured: "Colony" and "Colony 2" both on 18393), and it
// returns NOTHING AT ALL on a caravan camp, a quest site or an unsettled scratch map -
// where the tile is then genuinely unreachable. Map.Tile is a public property; this is
// a field, not a feature.
//
// Thread affinity, same rule as every other file here: everything touching game state
// is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimWorld.Planet;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // =====================================================================
        // ONE faction grammar for the whole companion.
        // =====================================================================
        // BUILD_BATCH_FACTION_REJECTS_PLAYER_1, measured live 2026-08-26:
        //
        //   jawa/spawn_pawn  {faction: "player"}  -> works; documents player|hostile|none
        //   jawa/build_batch {faction: "player"}  -> "No FactionDef 'player'."  8 calls lost
        //
        // A caller who learns the grammar from one tool loses a batch on the other, and
        // the old message named the VALUE rather than the DIFFERENCE. This resolver takes
        // both grammars and its failure text says which one the caller reached for.
        //
        // err is set ONLY when the caller asked for something that does not resolve.
        // "none" returns (null, null) - a deliberate no-faction, not a failure.
        internal static Faction ResolveFactionAliasOrDef(string s, out string err)
        {
            err = null;
            if (string.IsNullOrWhiteSpace(s)) return null;
            s = s.Trim();

            if (string.Equals(s, "none", StringComparison.OrdinalIgnoreCase))
                return null;

            if (string.Equals(s, "player", StringComparison.OrdinalIgnoreCase)
                || string.Equals(s, "PlayerColony", StringComparison.OrdinalIgnoreCase))
            {
                var p = Faction.OfPlayer;
                if (p == null) err = "No player faction exists yet - is a game loaded?";
                return p;
            }

            if (string.Equals(s, "hostile", StringComparison.OrdinalIgnoreCase))
            {
                var fm0 = Find.FactionManager;
                var host = fm0?.AllFactions.FirstOrDefault(
                    q => q != null && !q.IsPlayer && !q.def.hidden && q.HostileTo(Faction.OfPlayer));
                if (host == null)
                    err = "No non-hidden faction is currently hostile to the player. "
                        + "Name a FactionDef defName instead, or use 'none'.";
                return host;
            }

            var fd = DefDatabase<FactionDef>.GetNamedSilentFail(s);
            if (fd == null)
            {
                err = "No FactionDef '" + s + "'. This parameter takes a FactionDef DEFNAME "
                    + "(e.g. PlayerColony, Pirate) or one of the aliases 'player' / 'hostile' / 'none'.";
                return null;
            }

            var fac = Find.FactionManager?.FirstFactionOfDef(fd);
            if (fac == null)
                err = "FactionDef '" + s + "' exists but no such faction was generated in this world. "
                    + "jawa/list_factions returns the ones that were.";
            return fac;
        }

        // =====================================================================
        // jawa/map_info
        // =====================================================================

        [Tool(
            "jawa/map_info",
            Description =
                "READ ONLY. Everything about the CURRENT MAP that currently needs five " +
                "different tools and two round trips: its WORLD TILE (Map.Tile), the biome, " +
                "size, hilliness, the tile's elevation/rainfall/swampiness/temperature, " +
                "BOTH the tile's PrimaryBiome and the MAP's own Biome - they diverge after a live " +
                "world_tile_set, because the tile changes and the generated map does not - the " +
                "seasonal temperature right now, lat/long, the map parent (settlement, camp, " +
                "quest site) and its faction. " +
                "🔑 THE TILE IS THE POINT: world_tile_set + world_commit can change this " +
                "map's climate, biome and hilliness while it is running, and you cannot " +
                "aim either of them without the tile id. " +
                "⚠️ Reports the RAW tile fields ONLY. Tile.HillinessLabel, MinTemperature, " +
                "MaxTemperature and Biomes are lazily cached with no reset anywhere in 1.6, " +
                "so after a world_tile_set they report the OLD value for the rest of the " +
                "session and would let you confirm a write that never landed. " +
                "⛔ Does NOT tell you the map is settled. mapParent is null on a scratch " +
                "quicktest map and that is normal.",
            ResultDescription =
                "success, tile (the world tile id - the field nothing else reported), mapId, " +
                "sizeX/sizeZ/cellCount, tileInfo{biome,hilliness,elevation,rainfall," +
                "swampiness,temperature,pollution,waterCovered}, mapBiome + mapBiomeLabel, " +
                "elevation, rainfall, swampiness, temperature (the tile's baseline), " +
                "outdoorTempNow (the seasonal reading a pawn actually feels), latitude, " +
                "longitude, season, mapParent {defName, label, faction} or null, " +
                "playerSettlementsOnThisTile (a COUNT - a quicktest can have two), " +
                "and ticksGame.")]
        public static async Task<object> MapInfo(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                int tileId = map.Tile.tileId;

                // The tile record may legitimately be unreadable - a pocket map, or a
                // tile id that is not a SurfaceTile. Say so rather than returning zeros
                // that read as a measurement.
                object tileBlock = null;
                float lat = 0f, lon = 0f;
                bool haveLatLon = false;
                var grid = Find.WorldGrid;
                if (grid != null)
                {
                    try
                    {
                        var t = grid[map.Tile];
                        if (t != null)
                        {
                            var st = t as SurfaceTile;
                            // RAW fields only, and PrimaryBiome rather than a cached label.
                            // ⚠️ Tile.HillinessLabel / MinTemperature / MaxTemperature / Biomes
                            // are lazily cached with NO reset method anywhere in 1.6, so after
                            // a world_tile_set they report the OLD value for the rest of the
                            // session. Reporting them here would let a caller confirm a write
                            // that never landed. Same rule as JawaBenchWorldTools.TileRaw.
                            tileBlock = new
                            {
                                biome = st != null && st.PrimaryBiome != null ? st.PrimaryBiome.defName : null,
                                hilliness = t.hilliness.ToString(),
                                hillinessInt = (int)t.hilliness,
                                elevation = t.elevation,
                                rainfall = t.rainfall,
                                swampiness = t.swampiness,
                                temperature = t.temperature,
                                pollution = t.pollution,
                                waterCovered = st != null && st.WaterCovered,
                                isSurfaceTile = st != null,
                            };
                        }
                        var ll = grid.LongLatOf(map.Tile);
                        lon = ll.x; lat = ll.y; haveLatLon = true;
                    }
                    catch (Exception e)
                    {
                        tileBlock = new { unreadable = e.GetType().Name + ": " + e.Message };
                    }
                }

                object parent = null;
                var mp = map.Parent;
                if (mp != null)
                {
                    parent = new
                    {
                        defName = mp.def?.defName,
                        label = mp.Label,
                        faction = mp.Faction?.def?.defName,
                        factionName = mp.Faction?.Name,
                    };
                }

                // NOT a bool. A quicktest map genuinely carried TWO player settlements on
                // one tile on 2026-08-26, which is what made the old workaround ambiguous.
                int playerHere = 0;
                try
                {
                    var wo = Find.WorldObjects;
                    if (wo != null)
                        playerHere = wo.Settlements.Count(
                            q => q != null && q.Faction != null && q.Faction.IsPlayer
                                 && q.Tile.tileId == tileId);
                }
                catch { playerHere = -1; }   // -1 means NOT COUNTED, never "zero found".

                float outdoorNow;
                try { outdoorNow = map.mapTemperature.OutdoorTemp; }
                catch { outdoorNow = float.NaN; }

                return (object)new
                {
                    success = true,
                    tile = tileId,
                    mapId = map.uniqueID,
                    sizeX = map.Size.x,
                    sizeZ = map.Size.z,
                    cellCount = map.Size.x * map.Size.z,
                    tileInfo = tileBlock,
                    // Map.Biome is what the MAP resolved at generation. It can differ from the
                    // tile's PrimaryBiome above after a live world_tile_set: the tile changed,
                    // the generated map did not. Both are reported on purpose.
                    mapBiome = map.Biome != null ? map.Biome.defName : null,
                    mapBiomeLabel = map.Biome != null ? map.Biome.label : null,
                    outdoorTempNow = outdoorNow,
                    latitude = haveLatLon ? (float?)lat : null,
                    longitude = haveLatLon ? (float?)lon : null,
                    season = haveLatLon && Find.TickManager != null
                        ? GenDate.Season(Find.TickManager.TicksAbs, new Vector2(lon, lat)).ToString()
                        : null,
                    mapParent = parent,
                    playerSettlementsOnThisTile = playerHere,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
