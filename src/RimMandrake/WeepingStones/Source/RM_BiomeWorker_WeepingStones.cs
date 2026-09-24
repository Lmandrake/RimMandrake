using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_RM_MOD_BUILD_1, Phase A. Replaces the campaign twin's
    // donor workerClass (`VanillaBiomes.BiomeWorker_DesertOasis`) with a
    // self-contained type — a donor type in workerClass is a hard
    // dependency the RimMandrake tier may not assume (biome_mod_
    // architecture.md §5).
    //
    // RM_WeepingStones ships with <generatesNaturally>false</generatesNaturally>,
    // same as its campaign twin: this biome is placed by hand (Oasis
    // landmark authoring, OASIS_LANDMARK_PLACEMENT_1), never picked by the
    // natural worldgen scoring pass. GetScore below is therefore inert in
    // practice — it exists so <workerClass> resolves to a real type and
    // behaves sanely (favors genuine hot, low-relief desert country near
    // water) if that flag is ever flipped for a future placement tool.
    public class RM_WeepingStonesBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(20f, 60f);
        public FloatRange rainfall = new FloatRange(0f, 400f);
        public FloatRange elevation = new FloatRange(0f, 2500f);
        public float baseScore = 20f;
        public float degreeWeight = 0.2f;
    }

    public class RM_BiomeWorker_WeepingStones : BiomeWorker
    {
        private static readonly RM_WeepingStonesBiomeRanges FallbackRanges = new RM_WeepingStonesBiomeRanges();

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            RM_WeepingStonesBiomeRanges r = biome.GetModExtension<RM_WeepingStonesBiomeRanges>() ?? FallbackRanges;

            if (tile.temperature < r.temperature.min || tile.temperature > r.temperature.max)
            {
                return 0f;
            }
            if (tile.rainfall < r.rainfall.min || tile.rainfall >= r.rainfall.max)
            {
                return 0f;
            }
            if (tile.elevation < r.elevation.min || tile.elevation > r.elevation.max)
            {
                return 0f;
            }

            return r.baseScore + (tile.temperature - r.temperature.min) * r.degreeWeight;
        }
    }
}
