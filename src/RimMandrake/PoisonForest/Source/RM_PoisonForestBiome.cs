using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.PoisonForest
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling ForsakenCrags/TheRot/Greentide workers: BiomeDef has no
    // temperature/rainfall/elevation field, RimWorld scores every BiomeDef's
    // workerClass per tile and keeps the highest, so a biome with no worker
    // never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_PoisonForest — this
    // replaces the donor BiomesPlus.BiomeWorker_PoisonForest per
    // biome_mod_architecture.md §5 step 2 ("a donor type in workerClass is a
    // hard dependency the RimMandrake tier may not assume").
    //
    // ⚠️ RANGES ARE [INVENTED], same footing as every sibling worker. The
    // frozen campaign sheet (RUT_PoisonForest.xml header) measures this
    // biome on the campaign world at arc envelope 56-115 (median 91.3,
    // straddling the terminator) — a cold, permanently dim band with "a
    // cold stable ceiling (no day-night swing)". Arc-degrees-from-terminator
    // is a fact about that one frozen, hand-authored world and has no
    // vanilla Tile equivalent, so the ranges below are picked to read as
    // "cold, wet, low-lying forest" for worldgen on OTHER, generated
    // planets, not derived from that measurement.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_PoisonForestBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_PoisonForestBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(-15f, 12f);
        public FloatRange rainfall = new FloatRange(900f, 3000f);
        public FloatRange elevation = new FloatRange(0f, 900f);
        public float baseScore = 32f;
        public float degreeWeight = 0.8f;
        public float rainfallDivisor = 250f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as the sibling
        // workers: vanilla biome workers tile the planet, and a permanently
        // dim toxic forest is not a band. UNMEASURED — no worldgen run has
        // been done for this mod, and the campaign world is frozen and
        // hand-authored so one never will be for Ash'karr either.
        public float spawnChance = 0.05f;
    }

    // TRIGGERED BY: <workerClass> on the RM_PoisonForest BiomeDef.
    public class RM_BiomeWorker_PoisonForest : BiomeWorker
    {
        private static readonly RM_PoisonForestBiomeRanges FallbackRanges = new RM_PoisonForestBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x504F4953; // "POIS"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_PoisonForestSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_PoisonForestBiomeRanges r = biome.GetModExtension<RM_PoisonForestBiomeRanges>() ?? FallbackRanges;

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
            if (tile.hilliness == Hilliness.Impassable)
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
                 + (r.temperature.max - tile.temperature) * r.degreeWeight
                 + (tile.rainfall - r.rainfall.min) / divisor;
        }
    }
}
