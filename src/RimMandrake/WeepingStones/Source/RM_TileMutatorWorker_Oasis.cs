using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_OASIS_MUTATOR_FLORA_1: per-biome swap of the Oasis mutator's bonus flora.
    // TileMutatorWorker.AdditionalWildPlants(PlanetTile) is the virtual per-tile hook WildPlantSpawner reads
    // (1.6 source via RimSage); TileMutatorWorker_Oasis does not override it. This worker is swapped into the
    // vanilla Oasis def by Patches/RM_OasisMutatorFlora.xml and passes the vanilla list through untouched
    // unless the tile's biome carries RM_OasisFloraExtension, so vanilla deserts keep their palms.
    public class RM_OasisFloraExtension : DefModExtension
    {
        public List<string> stripDefNames = new List<string>();
        public List<BiomePlantRecord> plants = new List<BiomePlantRecord>();
    }

    public class RM_TileMutatorWorker_Oasis : TileMutatorWorker_Oasis
    {
        public RM_TileMutatorWorker_Oasis(TileMutatorDef def) : base(def)
        {
        }

        public override IEnumerable<BiomePlantRecord> AdditionalWildPlants(PlanetTile tile)
        {
            IEnumerable<BiomePlantRecord> vanilla = base.AdditionalWildPlants(tile);
            if (!RM_WeepingStonesSettings.oasisNativeFloraEnabled)
            {
                return vanilla;
            }
            RM_OasisFloraExtension ext = tile.Tile?.PrimaryBiome?.GetModExtension<RM_OasisFloraExtension>();
            return ext == null ? vanilla : Swap(vanilla, ext);
        }

        private static IEnumerable<BiomePlantRecord> Swap(IEnumerable<BiomePlantRecord> vanilla, RM_OasisFloraExtension ext)
        {
            foreach (BiomePlantRecord r in vanilla)
            {
                if (r?.plant != null && !ext.stripDefNames.Contains(r.plant.defName))
                {
                    yield return r;
                }
            }
            foreach (BiomePlantRecord r in ext.plants)
            {
                yield return r;
            }
        }
    }
}
