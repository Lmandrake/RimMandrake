using System.Collections.Generic;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // EXPLOSIVE_PLANT_GROWTH_1 — what a plant does at the top of its charge.
    //
    // A PROPERTY OF THE PLANT, NEVER OF THE BIOME (owner, 2026-09-20, design
    // doc §8: "It's less about the biome and more about the plants IN that
    // biome having different behaviors"). ⛔ Nothing in this mod may ever
    // read the biome to decide the top — the only biome input anywhere is
    // the soak CARVE-OUT list (terminator / deep desert: water there never
    // soaks), which decides whether a plant charges at all, not how it ends.
    //
    // Keys are the design doc §3 variant table verbatim, plus NONE.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_GrowthTop : byte
    {
        /// <summary>The DEFAULT (2026-09-21): split, die, drop produce, sow a
        /// ring of sprouts that RESPECTS built ground. Endless.</summary>
        Churn = 0,

        /// <summary>The rare violent top, dry-adapted plants only (ruling 4):
        /// pop, chaff, minor blunt + knockdown (injury+knockdown ceiling),
        /// premium produce scattered, husk as low-grade fuel, and a sown ring
        /// that IGNORES zones, floors and doorways.</summary>
        Burst = 1,

        /// <summary>Slime-fed plants: Churn-shaped (roster hard call 10,
        /// INVENTED), but the ring turns the ground to slime instead of
        /// sprouting.</summary>
        Slime = 2,

        /// <summary>A Burst whose debris is fuel: husk, chaff, and a ring of
        /// the plant's configured ring plant (quickgrass).</summary>
        Tinder = 3,

        /// <summary>Contaminated plants (ruling 5): a rupture, not a pop —
        /// gas cloud, red slimes and ocular entities, little sprouts, and
        /// mutation hediffs for anyone in the cloud without full vacuum
        /// protection.</summary>
        Rupture = 4,

        /// <summary>The Fever Wood giants: growth runs inside the trunk, no
        /// surface spectacle. The plant survives its top.</summary>
        Flush = 5,

        /// <summary>Never acquires SOAKED. Ambient tier only.</summary>
        None = 6,
    }

    /// <summary>
    /// Put this on a plant ThingDef you OWN to give it its top. For plants you
    /// do not own (donors, other tiers), list them in an
    /// <see cref="RM_ExplosiveGrowthRosterDef"/> instead — a roster row names
    /// the plant by string, so an absent donor is skipped silently rather than
    /// eating the def (a modExtension patched onto a def whose mod is missing
    /// is exactly the silent-discard trap this repo keeps hitting).
    /// A modExtension wins over any roster row. It assigns the top only; where the
    /// plant soaks is decided by the map's biome (RM_ExplosiveGrowthRegistry.BiomeInScope).
    /// </summary>
    public class RM_ExplosiveGrowthExtension : DefModExtension
    {
        public RM_GrowthTop top = RM_GrowthTop.Churn;

        /// <summary>Multiplies the top's produce drop. The roster's former-GLUT
        /// "heavy produce" rows use this; 1 = one plant's normal harvest.</summary>
        public float produceFactor = 1f;

        /// <summary>TINDER / BURST: the plant sown in the ring, if not the plant
        /// itself (TINDER's "ring of quickgrass").</summary>
        public ThingDef ringPlant;

        /// <summary>SLIME: the terrain the ring converts ground to.</summary>
        public TerrainDef slimeTerrain;

        /// <summary>The ruled archetype (spec §4). Auto = seeded from the biomes' plant lists (§4.3); a biome review
        /// sheet row that decides otherwise lands here.</summary>
        public RM_ArchetypeChoice archetype = RM_ArchetypeChoice.Auto;

        /// <summary>The Burst odds at the top of a dry cycle (C3: "1 in 3 ... Some plants are 1 in 1. Some plants
        /// (groundcover) never rupture"). -1 = the default (the Mod Setting for dry natives, 0 for wet natives; 1 for a
        /// Burst-top row).</summary>
        public float ruptureChance = -1f;

        /// <summary>Sprouts the outcome sows (§4: dry "many", wet "few", Pyrelands grass "super-fast"). 0~0 = the
        /// archetype default.</summary>
        public IntRange sproutCount = IntRange.Zero;

        /// <summary>T2 "Only for adapted plants": liquids besides clean water that water this plant (FlowWorks fluid
        /// defNames: RM_Fluid_SlimeRed, ...).</summary>
        public List<string> adaptedLiquids = new List<string>();

        /// <summary>C5: fresh ash counts as fresh water for this plant (the Pyrelands natives).</summary>
        public bool fireAdapted;
    }

    /// <summary>A sheet row's archetype decision; Auto = the seed.</summary>
    public enum RM_ArchetypeChoice : byte { Auto = 0, DryNative = 1, WetNative = 2, FireAdapted = 3, Exempt = 4 }

    /// <summary>One row of a roster def. All names are strings on purpose.</summary>
    public class RM_ExplosiveGrowthRosterEntry
    {
        public string plant;
        public RM_GrowthTop top = RM_GrowthTop.Churn;
        public float produceFactor = 1f;
        public string ringPlant;
        public string slimeTerrain;
        public RM_ArchetypeChoice archetype = RM_ArchetypeChoice.Auto;
        public float ruptureChance = -1f;
        public IntRange sproutCount = IntRange.Zero;
        public List<string> adaptedLiquids = new List<string>();
        public bool fireAdapted;
    }

    /// <summary>A filth def that IS a water source (D6): its liquid, by FlowWorks fluid defName.</summary>
    public class RM_FilthLiquidEntry
    {
        public string filth;
        public string liquid;
    }

    /// <summary>
    /// Data for the engine. Any number of these may load (the RM tier ships
    /// one, a campaign layer ships another); every list is UNIONED and a later
    /// plant row overrides an earlier one for the same plant. Nothing here is
    /// a cross-reference, so a name whose mod is absent is simply skipped and
    /// counted in the startup log line.
    /// </summary>
    public class RM_ExplosiveGrowthRosterDef : Def
    {
        public List<RM_ExplosiveGrowthRosterEntry> plants = new List<RM_ExplosiveGrowthRosterEntry>();

        /// <summary>True puts EVERY biome in scope (everyday bands and the soak) while this roster is loaded, exactly as
        /// the player's unsupported "other biomes" option does, and that option then has no effect. For a campaign layer
        /// whose whole world is the game (owner, 2026-10-16: the option is "irrelevant in Utinni"): its twins of our
        /// biomes are its own BiomeDefs, outside Baroque Biomes. A plain content mod must not set it.</summary>
        public bool scopeAllBiomes;

        /// <summary>R-G5: plants whose slowness is a mechanic. Never soak.</summary>
        public List<string> exemptPlants = new List<string>();

        /// <summary>Soak carve-outs (design doc §3: terminator, deep desert —
        /// water there never soaks). A CARVE-OUT on the soak, never an input to
        /// the top: a biome listed here stops plants charging at all.</summary>
        public List<string> noSoakBiomes = new List<string>();

        /// <summary>RUPTURE's spawn list — "red slimes, ocular entities".</summary>
        public List<string> rupturePawnKinds = new List<string>();

        /// <summary>RUPTURE's "extra mutation hediffs" pool, added to a random
        /// un-missing leaf body part.</summary>
        public List<string> ruptureMutationHediffs = new List<string>();

        /// <summary>T2: the liquids that are CLEAN water and water every plant (FlowWorks fluid defNames). Every other
        /// liquid waters only a plant that lists it in adaptedLiquids. Empty in every roster = RM_Fluid_Water.</summary>
        public List<string> cleanWaterFluids = new List<string>();

        /// <summary>Extra weathers whose fall counts as rain (the engine already counts any weather with rainRate &gt; 0).</summary>
        public List<string> soakWeathers = new List<string>();

        /// <summary>OQ-3: biomes where SNOW waters like rain ("Blowing snow melts like water and rain yes").</summary>
        public List<string> snowmeltBiomes = new List<string>();

        /// <summary>W2: natural water and mud terrains that keep their own cell wet, permanently, never consumed.</summary>
        public List<string> naturalWaterTerrains = new List<string>();

        /// <summary>D6: filth that is standing water (a hose spill, a poured can, a rain puddle).</summary>
        public List<RM_FilthLiquidEntry> filthLiquids = new List<RM_FilthLiquidEntry>();

        /// <summary>OQ-7: this roster's world is tidally locked (Ash'karr): a lit plant never rests by the clock.</summary>
        public bool tidallyLockedWorld;

        // ── archetype seeds (§4.3; OQ-1: no biome water label, the plant lists decide) ──

        /// <summary>Stunted biomes (terminator / poison forest): our plants there run the stunted rate and never cycle.</summary>
        public List<string> terminatorBiomes = new List<string>();

        /// <summary>The wet biomes (C1, WP3): a plant in one of these biomes' wildPlants is a WET native.</summary>
        public List<string> wetNativeBiomes = new List<string>();

        /// <summary>C5: a plant in one of these biomes' wildPlants is FIRE-ADAPTED (fresh ash waters it).</summary>
        public List<string> fireAdaptedBiomes = new List<string>();

        /// <summary>Plants left at vanilla speed everywhere (their slowness is the point): the Exempt archetype.</summary>
        public List<string> bandExemptPlants = new List<string>();
    }
}
