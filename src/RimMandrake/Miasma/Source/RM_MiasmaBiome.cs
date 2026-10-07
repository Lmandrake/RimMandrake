using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Miasma
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling Abyss/PoisonForest/TheRot/Greentide workers: BiomeDef
    // has no temperature/rainfall/elevation field, RimWorld scores every
    // BiomeDef's workerClass per tile and keeps the highest, so a biome with
    // no worker never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_Miasma — this replaces the
    // donor AlphaBiomes.BiomeWorker_MiasmicMangrove per
    // biome_mod_architecture.md §5 step 2 ("a donor type in workerClass is a
    // hard dependency the RimMandrake tier may not assume").
    //
    // ⚠️ RANGES ARE INVENTED, same footing as every sibling worker. The
    // frozen campaign sheet (RUT_Miasma.xml header) measures this biome on
    // the campaign world at elevation median 22 m (the lowest ground on the
    // dayside), temperature median 42.8 C, and river/sea-adjacent deltas —
    // a hot, low-lying, wet coastal band. There is no vanilla Tile field for
    // "adjacent to a river delta", so the worker gates on climate + relief +
    // a real river/coastal bonus only, same shape as every sibling.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_MiasmaBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_MiasmaBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(20f, 55f);
        public FloatRange rainfall = new FloatRange(1000f, 4000f);
        public FloatRange elevation = new FloatRange(0f, 200f);
        public float baseScore = 30f;
        public float degreeWeight = 0.4f;
        public float rainfallDivisor = 300f;
        public float riverOrCoastBonus = 12f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as the sibling
        // workers: vanilla biome workers tile the planet, and a salt-delta
        // mangal forest is not a band. UNMEASURED — no worldgen run has been
        // done for this mod, and the campaign world is frozen and
        // hand-authored so one never will be for Ash'karr either.
        public float spawnChance = 0.04f;
    }

    // TRIGGERED BY: <workerClass> on the RM_Miasma BiomeDef.
    public class RM_BiomeWorker_Miasma : BiomeWorker
    {
        private static readonly RM_MiasmaBiomeRanges FallbackRanges = new RM_MiasmaBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x4D49534D; // "MISM"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null) return RM_MiasmaKernel.BiomeScore(true, false, false, false, 0f, 0f, 0f, 0f, default(RM_MiasmaKernel.BiomeRanges), null);

            RM_MiasmaBiomeRanges r = biome.GetModExtension<RM_MiasmaBiomeRanges>() ?? FallbackRanges;
            var ranges = new RM_MiasmaKernel.BiomeRanges
            {
                tempMin = r.temperature.min, tempMax = r.temperature.max,
                rainMin = r.rainfall.min, rainMax = r.rainfall.max,
                elevMin = r.elevation.min, elevMax = r.elevation.max,
                baseScore = r.baseScore, degreeWeight = r.degreeWeight, rainfallDivisor = r.rainfallDivisor,
                riverOrCoastBonus = r.riverOrCoastBonus, spawnChance = r.spawnChance
            };
            SurfaceTile surfaceTile = tile as SurfaceTile;
            bool hasRiver = surfaceTile != null && surfaceTile.potentialRivers != null && surfaceTile.potentialRivers.Count > 0;
            // the scoring (water, rarity slider, ranges, hills, a river to flood, seeded gate, base + warm + wet + river bonus) is
            // RM_MiasmaKernel.BiomeScore (offline-fuzzed)
            return RM_MiasmaKernel.BiomeScore(false, tile.WaterCovered,
                tile.hilliness == Hilliness.Impassable || tile.hilliness == Hilliness.Mountainous, hasRiver,
                RM_MiasmaSettings.biomeRarityFactor, tile.temperature, tile.rainfall, tile.elevation, ranges,
                gate => Rand.ChanceSeeded(gate, planetTile.tileId ^ GateSeedSalt));
        }
    }
}
