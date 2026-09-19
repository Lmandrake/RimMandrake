using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// WORLDMAP_LIQUID_TAGS_1, half (1) — the per-tile liquid tag layer,
    /// keyed by tile id, as the item asks. Ask it "what liquid is the water
    /// on tile N made of" and it answers with a <see cref="LiquidDef"/> or
    /// null. Null means UNTYPED and every consumer must treat that as
    /// "vanilla, do nothing" — see <see cref="RM_GenStep_LiquidShores"/>,
    /// which is the first consumer.
    ///
    /// 🔑 IT STORES NOTHING IN THE SAVE, ON PURPOSE. There is no
    /// ExposeData override below and that is the single most important line
    /// in this file. The tags are derived from <see cref="RM_LiquidBodyDef"/>
    /// rows that ship inside the mod, so:
    ///   • the frozen, hand-authored Ash'karr savegame gains the tags without
    ///     one byte of it being rewritten — which is what
    ///     WORLDMAP_LIQUID_TAGS_1's own `## verify` requires ("save nothing
    ///     over the canonical start save");
    ///   • an already-started campaign gets them on its next load rather than
    ///     needing a re-authoring pass;
    ///   • a wrong tag is fixed by editing XML, never by driving the bridge
    ///     over a frozen planet.
    /// RM_LiquidBodyDef's own class note has the two measured facts that
    /// forced this shape.
    ///
    /// The cache is built once per world load and never invalidated, because
    /// its inputs (defs, and a tile's biome on a frozen world) do not change
    /// while a world is loaded. A live `jawa/world_tile_set` that repainted a
    /// tile's biome WOULD go unnoticed until the next load — acceptable, and
    /// stated here so nobody discovers it as a bug: there is no per-tile
    /// biome-change event to hook, and the campaign world is frozen.
    /// </summary>
    public class RM_WorldComponent_LiquidTags : WorldComponent
    {
        /// <summary>Explicit tile-id tags, from every row's `tiles` list.
        /// Wins over <see cref="byBiome"/>.</summary>
        private Dictionary<int, LiquidDef> byTile;

        /// <summary>Biome defName -> liquid, from every row's `biomes` list.
        /// Keyed by STRING so an absent campaign biome costs nothing.</summary>
        private Dictionary<string, LiquidDef> byBiome;

        public RM_WorldComponent_LiquidTags(World world)
            : base(world)
        {
        }

        private void EnsureBuilt()
        {
            if (byTile != null)
            {
                return;
            }

            byTile = new Dictionary<int, LiquidDef>();
            byBiome = new Dictionary<string, LiquidDef>();

            foreach (RM_LiquidBodyDef body in DefDatabase<RM_LiquidBodyDef>.AllDefsListForReading)
            {
                if (body.liquid == null)
                {
                    continue;
                }

                if (!body.biomes.NullOrEmpty())
                {
                    foreach (string biomeName in body.biomes)
                    {
                        if (biomeName.NullOrEmpty())
                        {
                            continue;
                        }
                        // Last row wins rather than throwing: two rows claiming
                        // one biome is an authoring mistake, not a crash, and
                        // ConfigErrors is where an author is told about it.
                        byBiome[biomeName] = body.liquid;
                    }
                }

                if (!body.tiles.NullOrEmpty())
                {
                    foreach (int tileId in body.tiles)
                    {
                        byTile[tileId] = body.liquid;
                    }
                }
            }
        }

        /// <summary>The liquid a map's water is made of, or null for UNTYPED.
        /// Takes the Map rather than a tile because <c>Map.Biome</c> already
        /// resolves the tile's biome and is the form every consumer has in
        /// hand at map-generation time.</summary>
        public LiquidDef TagFor(Map map)
        {
            if (map == null)
            {
                return null;
            }

            EnsureBuilt();

            LiquidDef liquid;
            if (byTile.TryGetValue(map.Tile.tileId, out liquid))
            {
                return liquid;
            }

            BiomeDef biome = map.Biome;
            if (biome != null && byBiome.TryGetValue(biome.defName, out liquid))
            {
                return liquid;
            }

            return null;
        }

        /// <summary>The same question asked of a planet tile with no map
        /// generated — what the tanker-raid target picker and any world-map
        /// UI will want.</summary>
        public LiquidDef TagFor(PlanetTile tile)
        {
            if (!tile.Valid)
            {
                return null;
            }

            EnsureBuilt();

            LiquidDef liquid;
            if (byTile.TryGetValue(tile.tileId, out liquid))
            {
                return liquid;
            }

            Tile tileInfo = tile.Tile;
            BiomeDef biome = tileInfo != null ? tileInfo.PrimaryBiome : null;
            if (biome != null && byBiome.TryGetValue(biome.defName, out liquid))
            {
                return liquid;
            }

            return null;
        }

        /// <summary>Null-safe static front door: returns null rather than
        /// throwing when no world is loaded, so a caller on the main menu or
        /// mid-teardown does not have to guard.</summary>
        public static LiquidDef TagForMap(Map map)
        {
            if (map == null || Find.World == null)
            {
                return null;
            }

            RM_WorldComponent_LiquidTags comp = Find.World.GetComponent<RM_WorldComponent_LiquidTags>();
            return comp != null ? comp.TagFor(map) : null;
        }

        public static LiquidDef TagForTile(PlanetTile tile)
        {
            if (Find.World == null)
            {
                return null;
            }

            RM_WorldComponent_LiquidTags comp = Find.World.GetComponent<RM_WorldComponent_LiquidTags>();
            return comp != null ? comp.TagFor(tile) : null;
        }
    }
}
