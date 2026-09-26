using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Contagion
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling Forsaken Crags / Blue Desert workers
    // (src/RimMandrake/ForsakenCrags/Source/RM_ForsakenCragsBiome.cs,
    // src/RimMandrake/BlueDesert — vanilla worker kept there instead):
    // BiomeDef has no temperature/rainfall/elevation field, RimWorld scores
    // every BiomeDef's workerClass per tile and keeps the highest, so a
    // biome with no worker never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_Contagion — this replaces
    // the donor AlphaBiomes.BiomeWorker_OcularForest per
    // biome_mod_architecture.md §5 step 2 ("a donor type in workerClass is a
    // hard dependency the RimMandrake tier may not assume").
    //
    // ⚠️ RANGES ARE INVENTED, same footing as the sibling workers' own
    // ranges. design/Jawa/worldbuilding/biomes/the_contagion.md §0 (MEASURED
    // off the frozen campaign world) gives the real placement's shape: temp
    // p10/median/p90 25/32/45 C (max 57), elevation median 1,387 m (max
    // 2,190), rain median 60 mm (max 1,529, the wettest dayside ground),
    // arc 18-69. The biome is placed on "the peaks above the green" — high,
    // hot, and unusually wet for its altitude (the sheet's own "altitude-
    // rain anomaly") — so the worker gates on heat + real relief + rain,
    // there being no vanilla Tile field for "roofed by a storm that never
    // stops."
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_ContagionBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_ContagionBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(20f, 57f);
        public FloatRange rainfall = new FloatRange(400f, 99999f);
        public FloatRange elevation = new FloatRange(1000f, 99999f);
        public float baseScore = 34f;
        public float degreeWeight = 0.3f;
        public float rainfallDivisor = 200f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as the sibling
        // workers: this is a rare, extreme mutation-engine peak, not a band.
        // UNMEASURED — no worldgen run has been done for this mod, and the
        // campaign world is frozen and hand-authored so one never will be
        // for Ash'karr either.
        public float spawnChance = 0.02f;
    }

    // TRIGGERED BY: <workerClass> on the RM_Contagion BiomeDef.
    public class RM_BiomeWorker_Contagion : BiomeWorker
    {
        private static readonly RM_ContagionBiomeRanges FallbackRanges = new RM_ContagionBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x434F4E54; // "CONT"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_ContagionSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_ContagionBiomeRanges r = biome.GetModExtension<RM_ContagionBiomeRanges>() ?? FallbackRanges;

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
            // High, real relief only — the sheet's own "peaks above the
            // green," never a flat hot rainforest.
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
