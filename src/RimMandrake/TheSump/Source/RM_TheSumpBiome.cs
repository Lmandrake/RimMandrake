using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.TheSump
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do. Same reasoning as the
    // sibling Miasma/PoisonForest/ForsakenCrags/Greentide workers: BiomeDef
    // has no temperature/rainfall/elevation field, RimWorld scores every
    // BiomeDef's workerClass per tile and keeps the highest, so a biome with
    // no worker never generates anywhere.
    //
    // TRIGGERED BY: the <workerClass> field on RM_TheSump — this replaces
    // the donor AlphaBiomes.BiomeWorker_TarPits per biome_mod_architecture.md
    // §5 step 2 ("a donor type in workerClass is a hard dependency the
    // RimMandrake tier may not assume").
    //
    // ⚠️ RANGES ARE INVENTED, same footing as every sibling worker. The
    // frozen campaign sheet (RUT_Sump.xml header, the_sump.md SS0) measures
    // this biome on the campaign world at elevation median 1 m (dead flat,
    // the lowest ground on the planet), temperature p10/median/p90
    // -4.3/1.2/14.9 C, permanent deep twilight (sun median -10.6 deg — not a
    // vanilla Tile field, so not gated on here). There is no live/quicktest
    // run to calibrate against (Desktop-only, out of this pass's no-bridge
    // scope) — a low, cold-to-mild, flat basin is the closest engine-
    // representable analogue.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: a <modExtensions><li Class="...RM_TheSumpBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class RM_TheSumpBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(-15f, 22f);
        public FloatRange rainfall = new FloatRange(0f, 2200f);
        public FloatRange elevation = new FloatRange(0f, 60f);
        public float baseScore = 24f;
        public float degreeWeight = 0.6f;
        public float rainfallDivisor = 500f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor — same reasoning as every sibling
        // worker: vanilla biome workers tile the planet, and a tar sump is
        // not a band. UNMEASURED — no worldgen run has been done for this
        // mod, and the campaign world is frozen and hand-authored so one
        // never will be for Ash'karr either.
        public float spawnChance = 0.05f;
    }

    // TRIGGERED BY: <workerClass> on the RM_TheSump BiomeDef.
    public class RM_BiomeWorker_TheSump : BiomeWorker
    {
        private static readonly RM_TheSumpBiomeRanges FallbackRanges = new RM_TheSumpBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any
        // other mod's tile-seeded roll.
        private const int GateSeedSalt = 0x53554D50; // "SUMP"

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            float rarity = RM_TheSumpSettings.biomeRarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            RM_TheSumpBiomeRanges r = biome.GetModExtension<RM_TheSumpBiomeRanges>() ?? FallbackRanges;

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
            if (tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable)
            {
                return 0f;
            }

            float gate = r.spawnChance * rarity;
            if (gate < 1f && !Rand.ChanceSeeded(gate, planetTile.tileId ^ GateSeedSalt))
            {
                return 0f;
            }

            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            // Lower elevation and lower temperature both score higher — this
            // is where runoff pools and stays liquid longest, mirroring the
            // sheet's own "lowest ground on the planet" framing.
            return r.baseScore
                 + (r.elevation.max - tile.elevation) * 0.1f
                 + (r.temperature.max - tile.temperature) * r.degreeWeight
                 - tile.rainfall / divisor;
        }
    }
}
