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
    /// A modExtension wins over any roster row.
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
    }

    /// <summary>One row of a roster def. All names are strings on purpose.</summary>
    public class RM_ExplosiveGrowthRosterEntry
    {
        public string plant;
        public RM_GrowthTop top = RM_GrowthTop.Churn;
        public float produceFactor = 1f;
        public string ringPlant;
        public string slimeTerrain;
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

        /// <summary>FlowWorks fluids that count as fresh irrigation water.</summary>
        public List<string> irrigationFluids = new List<string>();

        /// <summary>Weathers that soak open ground while they run (design doc
        /// §1 "hit by a qualifying rain"). Empty by default — the one ruled
        /// rain route (red_water / Contagion rain) has no WeatherDef yet.</summary>
        public List<string> soakWeathers = new List<string>();
    }
}
