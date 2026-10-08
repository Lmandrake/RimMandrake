using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.SeaShores
{
    [DefOf]
    public static class RM_SeaShoresDefOf
    {
        public static TileMutatorDef RM_SeaCoast;

        static RM_SeaShoresDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_SeaShoresDefOf));
        }
    }

    // Every "is this a sea / which sea" question in the mod lands here, so the
    // answer is computed one way only.
    public static class RM_SeaShoreUtility
    {
        private static Dictionary<BiomeDef, RM_SeaShoreExtension> seas;

        // Terrain -> sea, but ONLY for terrain no other sea and no vanilla
        // water shares. Two of our seas resolve to plain WaterOceanDeep; if
        // that key were in here, every ordinary vanilla coast on the planet
        // would start serving a modded catch table. Ambiguous keys are dropped
        // and SeaForCell falls back to the tile's own neighbours instead.
        private static Dictionary<TerrainDef, BiomeDef> terrainToSea;

        private static readonly List<PlanetTile> tmpNeighbours = new List<PlanetTile>();

        private static void EnsureCache()
        {
            if (seas != null)
            {
                return;
            }

            seas = new Dictionary<BiomeDef, RM_SeaShoreExtension>();
            var seaTerrains = new List<RM_SeaKernel.SeaTerrains<BiomeDef, TerrainDef>>();

            foreach (BiomeDef biome in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                RM_SeaShoreExtension ext = biome.GetModExtension<RM_SeaShoreExtension>();
                if (ext == null)
                {
                    continue;
                }
                seas[biome] = ext;
                seaTerrains.Add(new RM_SeaKernel.SeaTerrains<BiomeDef, TerrainDef>
                    { Sea = biome, Deep = DeepTerrainOf(biome), Shallow = ShallowTerrainOf(biome) });
            }

            terrainToSea = RM_SeaKernel.BuildTerrainKeys(seaTerrains, new[]
            {
                TerrainDefOf.WaterOceanDeep,
                TerrainDefOf.WaterOceanShallow,
                TerrainDefOf.WaterDeep,
                TerrainDefOf.WaterShallow
            });
        }

        public static RM_SeaShoreExtension ExtensionOf(BiomeDef biome)
        {
            if (biome == null)
            {
                return null;
            }
            EnsureCache();
            return seas.TryGetValue(biome, out RM_SeaShoreExtension ext) ? ext : null;
        }

        public static bool IsSea(BiomeDef biome)
        {
            return ExtensionOf(biome) != null;
        }

        public static TerrainDef DeepTerrainOf(BiomeDef sea)
        {
            RM_SeaShoreExtension ext = sea?.GetModExtension<RM_SeaShoreExtension>();
            if (ext == null)
            {
                return null;
            }
            return RM_SeaKernel.FirstNonNull(ext.deepTerrain, sea.oceanDeepTerrain, sea.waterDeepTerrain, () => TerrainDefOf.WaterOceanDeep);
        }

        public static TerrainDef ShallowTerrainOf(BiomeDef sea)
        {
            RM_SeaShoreExtension ext = sea?.GetModExtension<RM_SeaShoreExtension>();
            if (ext == null)
            {
                return null;
            }
            return RM_SeaKernel.FirstNonNull(ext.shallowTerrain, sea.oceanShallowTerrain, sea.waterShallowTerrain, () => TerrainDefOf.WaterOceanShallow);
        }

        // The sea a land tile faces: the one holding the most of its
        // neighbours. Ties break on defName so a repaint of the same planet
        // lays the same shore twice.
        public static BiomeDef PrimarySeaFor(PlanetTile tile)
        {
            EnsureCache();
            if (seas.Count == 0 || !tile.Valid)
            {
                return null;
            }

            WorldGrid grid = Find.WorldGrid;
            if (grid == null)
            {
                return null;
            }

            var neighbourSeas = new List<BiomeDef>();
            lock (tmpNeighbours)
            {
                tmpNeighbours.Clear();
                grid.GetTileNeighbors(tile, tmpNeighbours);
                for (int i = 0; i < tmpNeighbours.Count; i++)
                {
                    BiomeDef biome = grid[tmpNeighbours[i]]?.PrimaryBiome;
                    neighbourSeas.Add(biome != null && seas.ContainsKey(biome) ? biome : null);
                }
            }
            return RM_SeaKernel.PrimarySea(neighbourSeas, b => b.defName);
        }

        // True when this tile has at least one sea neighbour whose extension
        // says it counts as coast. Cheaper and more precise than PrimarySeaFor
        // for the IsCoastal path, which must respect countsAsCoast per sea.
        public static bool HasCoastingSeaNeighbour(PlanetTile tile)
        {
            EnsureCache();
            if (seas.Count == 0 || !tile.Valid)
            {
                return false;
            }
            WorldGrid grid = Find.WorldGrid;
            if (grid == null)
            {
                return false;
            }
            lock (tmpNeighbours)
            {
                tmpNeighbours.Clear();
                grid.GetTileNeighbors(tile, tmpNeighbours);
                for (int i = 0; i < tmpNeighbours.Count; i++)
                {
                    RM_SeaShoreExtension ext = ExtensionOf(grid[tmpNeighbours[i]]?.PrimaryBiome);
                    if (ext != null && ext.countsAsCoast)
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        // Which sea's water a map cell is: its own terrain if that terrain
        // belongs to exactly one sea, otherwise the sea this map's tile faces
        // — but only when the cell really carries that sea's water, so an
        // inland freshwater pond on a coastal map is never mistaken for it.
        public static BiomeDef SeaForCell(Map map, IntVec3 cell)
        {
            if (map == null || !cell.IsValid || !cell.InBounds(map))
            {
                return null;
            }
            EnsureCache();
            if (seas.Count == 0)
            {
                return null;
            }

            TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
            BiomeDef keyed = null;
            if (terrain != null)
            {
                terrainToSea.TryGetValue(terrain, out keyed);
            }

            BiomeDef sea = PrimarySeaFor(map.Tile);
            return RM_SeaKernel.CellSea(keyed, sea, terrain != null,
                sea != null && terrain == DeepTerrainOf(sea), sea != null && terrain == ShallowTerrainOf(sea));
        }

        // rootCell is Scribed and always set; WaterBody.cells is [Unsaved] and
        // may still be empty when SetFishTypes runs, so it is never consulted.
        public static BiomeDef SeaForWaterBody(WaterBody body)
        {
            return body == null ? null : SeaForCell(body.map, body.rootCell);
        }

        private static readonly List<FishChance> EmptyBand = new List<FishChance>();

        // Which of a sea's four catch bands answers for a water body, and the
        // one rule vanilla has no equivalent of: an EMPTY band falls back to
        // the other salt/fresh pair. RUT_TheScald needs this — its catches are
        // authored under freshwater_* while the terrain its shore lays declares
        // waterBodyType Saltwater, so a literal salt lookup would find nothing
        // and the sea would fish empty. Pure, so it is what the selftest drives.
        public static List<FishChance> BandFor(BiomeFishTypes fish, bool saltwater, bool uncommon)
        {
            if (fish == null)
            {
                return EmptyBand;
            }
            return RM_SeaKernel.BandFor(
                uncommon ? (saltwater ? fish.saltwater_Uncommon : fish.freshwater_Uncommon) : (saltwater ? fish.saltwater_Common : fish.freshwater_Common),
                uncommon ? (saltwater ? fish.freshwater_Uncommon : fish.saltwater_Uncommon) : (saltwater ? fish.freshwater_Common : fish.saltwater_Common),
                EmptyBand);
        }

        // The biome whose fishTypes should answer for a fishing cell. Called
        // from the FishingUtility transpiler in place of `pawn.Map.Biome`, so
        // it must return the land biome unchanged in every non-sea case.
        public static BiomeDef FishBiomeFor(Map map, IntVec3 cell)
        {
            BiomeDef land = map?.Biome;
            if (map == null || !RM_SeaShoresSettings.Cur.seaCatchTables)
            {
                return land;
            }
            BiomeDef sea = SeaForCell(map, cell);
            RM_SeaShoreExtension ext = ExtensionOf(sea);
            return RM_SeaKernel.CatchTableApplies(true, true, sea != null, sea?.fishTypes != null, ext != null && ext.providesCatch) ? sea : land;
        }
    }
}
