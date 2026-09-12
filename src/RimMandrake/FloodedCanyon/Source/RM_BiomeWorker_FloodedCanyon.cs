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
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_FloodedCanyonSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_FloodedCanyonBiomeRanges r = biome.GetModExtension<RM_FloodedCanyonBiomeRanges>() ?? FallbackRanges;

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
            // Canyon country: real relief, not flat desert floor.
            if (tile.hilliness != Hilliness.LargeHills && tile.hilliness != Hilliness.Mountainous)
            {
                return 0f;
            }

            float gate = r.spawnChance * rarity;
            if (gate < 1f && !Rand.ChanceSeeded(gate, planetTile.tileId ^ GateSeedSalt))
            {
                return 0f;
            }

            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            return r.baseScore
                 + (tile.temperature - r.temperature.min) * r.degreeWeight
                 + (tile.rainfall - r.rainfall.min) / divisor;
        }
    }
}
