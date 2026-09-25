using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.ForsakenCrags
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling Gelatinous Slime / Flooded Canyon mods' own workers
    // (src/RimMandrake/GelatinousSlime/Source/SlimeBiome.cs,
    // src/RimMandrake/FloodedCanyon/Source/RM_BiomeWorker_FloodedCanyon.cs):
    // BiomeDef has no temperature/rainfall/elevation field, RimWorld scores
    // every BiomeDef's workerClass per tile and keeps the highest, so a
    // biome with no worker never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_ForsakenCrags — this
    // replaces the donor AlphaBiomes.BiomeWorker_RockyCrags per
    // biome_mod_architecture.md §5 step 2 ("a donor type in workerClass is a
    // hard dependency the RimMandrake tier may not assume").
    //
    // ⚠️ RANGES ARE INVENTED, same footing as the sibling workers' own
    // ranges. The frozen campaign sheet describes this biome as the
    // hilliest def on the planet (614/1170 tiles at large-hills or worse,
    // MEASURED for the campaign world) and a rocky, sand-floored highland —
    // there is no vanilla Tile field for "night side" or "darkness", so the
    // worker gates on climate + relief only, same as every sibling.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_ForsakenCragsBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_ForsakenCragsBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(-20f, 15f);
        public FloatRange rainfall = new FloatRange(0f, 700f);
        public FloatRange elevation = new FloatRange(300f, 3500f);
        public float baseScore = 34f;
        public float degreeWeight = 0.3f;
        public float rainfallDivisor = 200f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as the sibling
        // workers: vanilla biome workers tile the planet, and a rocky,
        // rare highland is not a band. UNMEASURED — no worldgen run has
        // been done for this mod, and the campaign world is frozen and
        // hand-authored so one never will be for Ash'karr either.
        public float spawnChance = 0.02f;
    }

    // TRIGGERED BY: <workerClass> on the RM_ForsakenCrags BiomeDef.
    public class RM_BiomeWorker_ForsakenCrags : BiomeWorker
    {
        private static readonly RM_ForsakenCragsBiomeRanges FallbackRanges = new RM_ForsakenCragsBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x46434147; // "FCAG"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_ForsakenCragsSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_ForsakenCragsBiomeRanges r = biome.GetModExtension<RM_ForsakenCragsBiomeRanges>() ?? FallbackRanges;

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
            // Rocky highland: real relief only, matching the twin's own
            // hilliest-on-the-planet character.
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
                 + (r.temperature.max - tile.temperature) * r.degreeWeight
                 + (tile.rainfall - r.rainfall.min) / divisor;
        }
    }
}
