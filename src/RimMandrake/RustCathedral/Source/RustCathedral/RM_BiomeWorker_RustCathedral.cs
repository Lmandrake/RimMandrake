using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.RustCathedral
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as every
    // sibling worker (RM_BiomeWorker_Miasma etc.): BiomeDef has no
    // temperature/rainfall/elevation field, RimWorld scores every BiomeDef's
    // workerClass per tile and keeps the highest, so a biome with no worker
    // never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_RustCathedral — replaces
    // the donor AlphaBiomes.BiomeWorker_MechanoidIntrusion per
    // biome_mod_architecture.md §5 step 2 ("a donor type in workerClass is a
    // hard dependency the RimMandrake tier may not assume").
    //
    // The donor's own GetScore (vendor/mod_sources/AlphaBiomes_src/1.6/
    // Source/AlphaBiomes/AlphaBiomes/BiomeWorkers/
    // BiomeWorker_MechanoidIntrusion.cs) gates on temperature 17-25C,
    // rainfall >= 600, and a custom WorldComponentExtender "radiation noise"
    // field this mod may not depend on (an AlphaBiomes-internal class). This
    // worker keeps the climate gate and replaces the radiation-noise gate
    // with a plain seeded chance, same shape as RM_BiomeWorker_Miasma's
    // spawnChance*rarity gate — self-contained, no donor class referenced.
    //
    // ⚠️ RANGES ARE INVENTED past the climate gate (temperature/rainfall
    // are the donor's own measured values; the frozen campaign sheet's own
    // 62.5 C median sits well above the donor's 17-25 C band, which is
    // expected — Ash'karr's own worker is a SEPARATE hand-authored
    // placement, not this one; this worker only governs a NEW planet's own
    // Rust Cathedral instances, never the frozen campaign world).
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_RustCathedralBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_RustCathedralBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(17f, 25f);
        public float minRainfall = 600f;
        public float baseScore = 16f;
        public float degreeWeight = 1f;
        public float rainfallDivisor = 180f;

        // Fraction of qualifying tiles this biome even competes for, before
        // the Mod Settings rarity factor — a mechanoid-garrisoned plateau is
        // not a climate band, same reasoning as every sibling worker.
        // UNMEASURED — no worldgen run has been done for this mod, and the
        // campaign world is frozen and hand-authored so one never will be
        // for Ash'karr either.
        public float spawnChance = 0.03f;
    }

    // TRIGGERED BY: <workerClass> on the RM_RustCathedral BiomeDef.
    public class RM_BiomeWorker_RustCathedral : BiomeWorker
    {
        private static readonly RM_RustCathedralBiomeRanges FallbackRanges = new RM_RustCathedralBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x52555354; // "RUST"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_RustCathedralSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_RustCathedralBiomeRanges r = biome.GetModExtension<RM_RustCathedralBiomeRanges>() ?? FallbackRanges;

            if (tile.temperature < r.temperature.min || tile.temperature > r.temperature.max)
            {
                return 0f;
            }
            if (tile.rainfall < r.minRainfall)
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
                 + (tile.rainfall - r.minRainfall) / divisor;
        }
    }
}
