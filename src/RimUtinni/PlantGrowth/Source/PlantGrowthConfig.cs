using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PlantGrowth
{
    /// <summary>
    /// The single place every tunable for planetary fast growth lives.
    ///
    /// The constants below are the shipped defaults. Defs/JawaPlantGrowthSettings.xml
    /// overrides all of them at startup, so the owner can retune the bands, the
    /// terminator biome roster and the exempt list without a rebuild.
    /// </summary>
    public static class PlantGrowthConfig
    {
        // ---- The three bands (PLANT_GROWTH_SPEC.md R-G2) --------------------
        //
        // DEFAULT     wild plants AND player crops. Corn's 11.3 growDays becomes
        //             ~2.8. Startling on first sight, which is the entire point.
        //             Crops are deliberately NOT exempt: the fiction is planetary
        //             so the physics cannot notice who planted it, and on this
        //             world the limit on agriculture is WATER, not time.
        // TREE        trees are a wood economy, not scenery. At x4 lumber stops
        //             being a decision. x2.5 is still visibly unnatural.
        // TERMINATOR  the poison forest on the shade side is STUNTED — its water
        //             arrives as trace condensation, not as flood. It is the one
        //             place on the planet where growth has stalled, and a global
        //             multiplier would flatten exactly the biome whose identity is
        //             that it does not grow. Below 1.0 on purpose.
        public const float DEFAULT_MULTIPLIER    = 4.0f;
        public const float TREE_MULTIPLIER       = 2.5f;
        public const float TERMINATOR_MULTIPLIER = 0.4f;

        // A plant already this fast gains nothing from multiplying and can produce
        // silly per-tick values, so it is left alone (R-G5).
        public const float MIN_GROW_DAYS_TO_BOOST = 1.0f;

        // ---- The terminator biome roster (R-G3) ----------------------------
        //
        // NOT a hard-coded defName. DECIDE supplies the final roster after the
        // owner's biome review; PoisonForest (Advanced Biomes (Continued)) is the
        // only confirmed member today. Edit the def XML, not this list.
        public static readonly List<string> DEFAULT_TERMINATOR_BIOMES = new List<string>
        {
            "PoisonForest",
        };

        // ---- Exempt plants (R-G5) ------------------------------------------
        //
        // Plants whose slowness is a MECHANIC rather than a growth rate.
        // Quadrupling these breaks systems that have nothing to do with the
        // fiction. Exempt means untouched in EVERY biome, terminator included.
        public static readonly List<string> DEFAULT_EXEMPT_PLANTS = new List<string>
        {
            "Plant_TreeAnima",      // anima tree — growth is ritual pacing, not botany
            "Plant_TreeGauranlen",  // gauranlen tree — the dryad economy times against it
            "Plant_Ambrosia",       // a deliberately scarce drug source
        };

        // ---- Live values, after the def has been read -----------------------
        public static float DefaultMultiplier    = DEFAULT_MULTIPLIER;
        public static float TreeMultiplier       = TREE_MULTIPLIER;
        public static float TerminatorMultiplier = TERMINATOR_MULTIPLIER;
        public static float MinGrowDaysToBoost   = MIN_GROW_DAYS_TO_BOOST;

        /// <summary>True once the caches are built. The postfix no-ops until then.</summary>
        public static bool Ready { get; private set; }

        // Built once at startup and never written again, so the postfix does only
        // lookups — no allocation and no write race if another mod ticks plants
        // off the main thread.
        private static HashSet<ThingDef> _exempt = new HashSet<ThingDef>();
        private static Dictionary<ThingDef, float> _multiplierByDef = new Dictionary<ThingDef, float>();
        private static HashSet<BiomeDef> _terminatorBiomes = new HashSet<BiomeDef>();

        public static int ExemptCount => _exempt.Count;
        public static int ScaledCount => _multiplierByDef.Count;
        public static int TerminatorBiomeCount => _terminatorBiomes.Count;

        /// <summary>
        /// Reads the settings def if present, then classifies every plant def and
        /// every biome def once. Call from a StaticConstructorOnStartup, i.e. after
        /// the DefDatabases are populated.
        /// </summary>
        public static void Rebuild()
        {
            Ready = false;

            List<string> terminatorNames = DEFAULT_TERMINATOR_BIOMES;
            List<string> exemptNames = DEFAULT_EXEMPT_PLANTS;

            PlantGrowthSettingsDef settings = PlantGrowthSettingsDef.Current;
            if (settings != null)
            {
                DefaultMultiplier = settings.defaultMultiplier;
                TreeMultiplier = settings.treeMultiplier;
                TerminatorMultiplier = settings.terminatorMultiplier;
                MinGrowDaysToBoost = settings.minGrowDaysToBoost;
                if (settings.terminatorBiomes != null) terminatorNames = settings.terminatorBiomes;
                if (settings.exemptPlants != null) exemptNames = settings.exemptPlants;
            }

            var exempt = new HashSet<ThingDef>();
            var multipliers = new Dictionary<ThingDef, float>();
            var exemptNameSet = new HashSet<string>(exemptNames);

            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.plant == null) continue;

                if (exemptNameSet.Contains(def.defName) || def.plant.growDays < MinGrowDaysToBoost)
                {
                    exempt.Add(def);
                    continue;
                }

                multipliers[def] = def.plant.IsTree ? TreeMultiplier : DefaultMultiplier;
            }

            var biomes = new HashSet<BiomeDef>();
            foreach (string name in terminatorNames)
            {
                BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail(name);
                if (biome != null) biomes.Add(biome);
                else Log.Warning("[RimMandrake.Utinni.PlantGrowth] terminator biome '" + name + "' is not loaded; skipping it.");
            }

            _exempt = exempt;
            _multiplierByDef = multipliers;
            _terminatorBiomes = biomes;
            Ready = true;
        }

        public static bool IsExempt(ThingDef def) => _exempt.Contains(def);

        public static bool IsTerminatorBiome(BiomeDef biome) =>
            biome != null && _terminatorBiomes.Contains(biome);

        public static float MultiplierFor(ThingDef def) =>
            _multiplierByDef.TryGetValue(def, out float m) ? m : 1f;
    }
}
