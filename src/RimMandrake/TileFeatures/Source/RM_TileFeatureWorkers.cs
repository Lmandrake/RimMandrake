using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.TileFeatures
{
    /// <summary>RM_NoTrees: no tree grows wild on the tile.</summary>
    public class RM_TileMutatorWorker_NoTrees : TileMutatorWorker
    {
        public RM_TileMutatorWorker_NoTrees(TileMutatorDef def) : base(def)
        {
        }

        public override float PlantCommonalityFactorFor(ThingDef plant, PlanetTile tile)
        {
            if (!RM_TileFeaturesSettings.floraEnabled) return 1f;
            return plant?.plant != null && plant.plant.IsTree ? 0f : 1f;
        }
    }

    /// <summary>RM_MarineSanctuary: the biome's coastal animals are more common.</summary>
    public class RM_TileMutatorWorker_MarineSanctuary : TileMutatorWorker
    {
        public const float CoastalAnimalFactor = 3f; // PROVISIONAL; tuned live later

        public RM_TileMutatorWorker_MarineSanctuary(TileMutatorDef def) : base(def)
        {
        }

        public override float AnimalCommonalityFactorFor(PawnKindDef animal, PlanetTile tile)
        {
            if (!RM_TileFeaturesSettings.floraEnabled || animal == null || !tile.Valid) return 1f;
            BiomeDef biome = tile.Tile?.PrimaryBiome;
            return biome != null && biome.CommonalityOfCoastalAnimal(animal) > 0f ? CoastalAnimalFactor : 1f;
        }
    }

    /// <summary>RM_Fertility_Reduced: after the terrain is laid, natural ground richer than soil becomes soil.</summary>
    public class RM_TileMutatorWorker_ReducedFertility : TileMutatorWorker
    {
        public RM_TileMutatorWorker_ReducedFertility(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostTerrain(Map map)
        {
            if (!RM_TileFeaturesSettings.floraEnabled || TerrainDefOf.Soil == null) return;
            int changed = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = map.terrainGrid.TerrainAt(c);
                if (t == null || !t.natural || t.fertility <= TerrainDefOf.Soil.fertility) continue;
                map.terrainGrid.SetTerrain(c, TerrainDefOf.Soil);
                changed++;
            }
            if (Prefs.DevMode && changed > 0)
                Log.Message("[RM TileFeatures] reduced fertility: " + changed + " rich cells became soil on " + map);
        }
    }
}
