using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // BIOME PLACEMENT — mirrors the sibling Gelatinous Slime mod's own
    // rarity-gated worker exactly (src/RimMandrake/GelatinousSlime/Source/SlimeBiome.cs).
    // BiomeDef has no temperature/rainfall/elevation field; RimWorld scores
    // every BiomeDef's workerClass per tile and keeps the highest, so a
    // biome with no worker never generates anywhere.
    //
    // TRIGGERED BY: the <modExtensions><li Class="...RM_FloodedCanyonBiomeRanges">
    // block on the RM_FloodedCanyon BiomeDef.
    public class RM_FloodedCanyonBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(9f, 45f);
        public FloatRange rainfall = new FloatRange(0f, 800f);
        public FloatRange elevation = new FloatRange(200f, 2000f);
        public float baseScore = 34f;
        public float degreeWeight = 0.3f;
        public float rainfallDivisor = 200f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as Gelatinous
        // Slime's own spawnChance: vanilla biome workers tile the planet,
        // and "a handful of canyon patches" is not a band.
        public float spawnChance = 0.03f;
    }

    // TRIGGERED BY: <workerClass> on the RM_FloodedCanyon BiomeDef.
    public class RM_BiomeWorker_FloodedCanyon : BiomeWorker
    {
        private static readonly RM_FloodedCanyonBiomeRanges FallbackRanges = new RM_FloodedCanyonBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x43414E59; // "CANY"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null)
            {
                return -100f;
            }

            float rarity = RM_FloodedCanyonSettings.biomeRarityFactor;
            RM_FloodedCanyonBiomeRanges r = biome.GetModExtension<RM_FloodedCanyonBiomeRanges>() ?? FallbackRanges;
            // Canyon country: real relief, not flat desert floor.
            return RM_CanyonRulesKernel.BiomeScore(tile.WaterCovered, rarity, tile.temperature, tile.rainfall, tile.elevation,
                tile.hilliness == Hilliness.LargeHills || tile.hilliness == Hilliness.Mountainous,
                r.temperature.min, r.temperature.max, r.rainfall.min, r.rainfall.max, r.elevation.min, r.elevation.max, r.spawnChance,
                () => Rand.ChanceSeeded(r.spawnChance * rarity, planetTile.tileId ^ GateSeedSalt),
                r.baseScore, r.degreeWeight, r.rainfallDivisor);
        }
    }
}
