using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the thing XML cannot do.
    //
    // BiomeDef has NO temperature, rainfall or elevation field. RimWorld picks
    // a tile's biome by asking every BiomeDef's `workerClass` for a score and
    // keeping the highest (RimSage, RimWorld/Planet/WorldGenStep_Terrain.cs:284
    // `surfaceTile.PrimaryBiome = BiomeFrom(surfaceTile, tile, layer)`), so a
    // biome with no worker never generates anywhere. This is that worker and
    // the ONLY route. The numbers live in XML (BiomeDefs/GelatinousSlime.xml)
    // so they retune without a rebuild.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: the <modExtensions><li Class="...SlimeBiomeRanges"> block
    // on a BiomeDef. Absent, the defaults below apply unchanged.
    public class SlimeBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(8f, 34f);
        public FloatRange rainfall = new FloatRange(1400f, 6000f);
        public FloatRange elevation = new FloatRange(0f, 900f);
        public float baseScore = 36f;
        public float degreeWeight = 0.25f;
        public float rainfallDivisor = 400f;

        // Fraction of QUALIFYING tiles this biome even competes for, before
        // the Mod Settings rarity factor. See the worker for why this exists.
        public float spawnChance = 0.012f;
    }

    // TRIGGERED BY: <workerClass> on the RM_GelatinousSlime BiomeDef.
    //
    // 🔑 WHY A SPAWN CHANCE AND NOT JUST A SCORE. Vanilla biome workers are
    // built to TILE the planet: every tile in a band belongs to whichever
    // worker wins there, so a worker that wins its band takes the whole band —
    // a continent, not a patch. The owner ruled "1-3 rare patches per planet"
    // (spec §2, round 2), which is not a band at all. So the score is the
    // ordinary vanilla competition (it must beat TemperateForest /
    // TropicalRainforest where it lands), and `spawnChance` is a separate,
    // deterministic per-tile gate in front of it: on a tile that does not pass
    // the gate this worker returns 0 and the vanilla winner keeps the tile.
    //
    // 🔴 THE GATE MUST BE DETERMINISTIC PER TILE, hence Rand.ChanceSeeded on
    // the tile id rather than Rand.Chance. GetScore is not promised to be
    // called exactly once per tile; a plain Rand.Chance would make the same
    // tile qualify on one call and not the next, and the biome would come out
    // as scattered single cells instead of patches. Seeding on tileId alone
    // (no world seed mixed in) is intentional and harmless: the gate is one
    // input to a score that is then compared against tile climate, which does
    // vary per world.
    //
    // ⚠️ THE PATCH COUNT IS NOT MEASURED. 0.012 is an arithmetic estimate
    // against the temperate-wet band of a default 100%-coverage world, not a
    // counted result — no worldgen run has been done for this mod (and the
    // campaign's own world is frozen and hand-authored, so one never will be
    // for Ash'karr). Anyone who runs a real generation should count the
    // resulting tiles and correct spawnChance here. Until then this number is
    // UNMEASURED, and calling it "1-3 patches" is a design intent, not a
    // finding.
    public class BiomeWorker_GelatinousSlime : BiomeWorker
    {
        private static readonly SlimeBiomeRanges FallbackRanges = new SlimeBiomeRanges();

        // Mixed into the tile id so this gate never correlates with any other
        // mod's tile-seeded roll.
        private const int GateSeedSalt = 0x5137B1;

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            // Rarity slider at zero means the player has turned the biome off.
            float rarity = SlimeSettings.rarityFactor;
            if (rarity <= 0.001f)
            {
                return -100f;
            }

            SlimeBiomeRanges r = biome.GetModExtension<SlimeBiomeRanges>() ?? FallbackRanges;

            if (tile.temperature < r.temperature.min || tile.temperature > r.temperature.max)
            {
                return 0f;
            }
            // Half-open on rainfall, matching vanilla's own workers exactly so
            // the band edges butt up against theirs with no overlap.
            if (tile.rainfall < r.rainfall.min || tile.rainfall >= r.rainfall.max)
            {
                return 0f;
            }
            if (tile.elevation < r.elevation.min || tile.elevation > r.elevation.max)
            {
                return 0f;
            }
            // The body lies in lowland wet country, not on a mountainside.
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
            return r.baseScore
                 + (tile.temperature - r.temperature.min) * r.degreeWeight
                 + (tile.rainfall - r.rainfall.min) / divisor;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // CURE GEOGRAPHY AS DATA (spec §4).
    //
    // TRIGGERED BY: a <modExtensions> entry on any BiomeDef. This mod's own
    // Defs/Patches/DryingBiomes.xml tags vanilla Desert, ExtremeDesert,
    // AridShrubland and Ocean; the RUT campaign layer tags Ash'karr's deserts
    // and salt registers from its own side; any other mod tags its own biomes
    // the same way. Nothing in this assembly names a biome.
    //
    // 🔑 The severity DECAYS here, it does not merely hold — the ruling's
    // whole point is that the threat has a map answer you can walk to, and
    // the walk has to be earned. HediffComp_Slimification reads decayPerDay.
    // ════════════════════════════════════════════════════════════════════
    public class DryingBiomeExtension : DefModExtension
    {
        // Severity removed per day in this biome. [INVENTED — spec §4:
        // "full clear from stage 3 in ~4-5 days".]
        public float decayPerDay = 0.22f;
    }

    // ════════════════════════════════════════════════════════════════════
    // RESISTANCE AS DATA (spec §2, "resistant by identity"; §3 law 1).
    //
    // TRIGGERED BY: a <modExtensions> entry on a race ThingDef. RM_Gelatid
    // carries it — the slime cannot convert something already made of itself.
    // A modded creature, or the campaign's mycoid-symbiote route, opts out the
    // same way with no change here.
    //
    // This is the NON-BIOTECH resistance route; RM_Gene_SlimeResistance is the
    // Biotech one, and MapComponent_SlimeExposure honours both.
    // ════════════════════════════════════════════════════════════════════
    public class SlimeResistantExtension : DefModExtension
    {
    }
}
