using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Miasma
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling ForsakenCrags/PoisonForest/TheRot/Greentide workers: BiomeDef
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
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_MiasmaSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_MiasmaBiomeRanges r = biome.GetModExtension<RM_MiasmaBiomeRanges>() ?? FallbackRanges;

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
            if (tile.hilliness == Hilliness.Impassable || tile.hilliness == Hilliness.Mountainous)
            {
                return 0f;
            }

            // A mangal delta is riverine by nature — a dry tile with no
            // river never scores, matching the twin's own "between a dying
            // sea and the rivers that feed it". Rivers/riverDist live on
            // SurfaceTile, not the base Tile GetScore is handed (confirmed
            // against src/RimMandrake/bridgetools/JawaBench.BridgeTools/
            // JawaBenchWorldTools.cs's own W4 river-reading code) — a
            // non-SurfaceTile (should not occur for a player-reachable
            // world tile, but the cast is defensive) scores as if riverless
            // rather than throwing.
            SurfaceTile surfaceTile = tile as SurfaceTile;
            if (surfaceTile == null || surfaceTile.Rivers == null || surfaceTile.Rivers.Count == 0)
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
                 + (tile.rainfall - r.rainfall.min) / divisor
                 + r.riverOrCoastBonus;
        }
    }
}
