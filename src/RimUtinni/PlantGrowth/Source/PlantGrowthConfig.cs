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

        // WET AMBIENT  owner, 2026-09-21 (explosive_plant_growth_design.md §0,
        //             ruling 6): the Greentide, the Miasma and the Fever Wood
        //             grow at x10 INSTEAD of the planetary x4, always, with no
        //             soak involved — "It's the same always-on, but stronger:
        //             x10 instead of x4 growth here." It REPLACES the default
        //             band on those biomes, it does not stack on it. This is
        //             NOT the soak multiplier (that is an event multiplier owned
        //             by mandrake.rm.explosivegrowth and stacks on top of
        //             whichever ambient band applies).
        //             Trees: the ruling names one number. 6.25 keeps the
        //             tree:default ratio the spec already rules (2.5:4) —
        //             INVENTED, and a slider.
        public const float WET_AMBIENT_MULTIPLIER      = 10.0f;
        public const float WET_AMBIENT_TREE_MULTIPLIER = 6.25f;

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

        // ---- The wet-ambient biome roster (ruling 6) ------------------------
        //
        // The owner picked these three and EXCLUDED the Rot (fungal; the Sheen
        // is not water). Both the campaign twin and the standalone RM_ biome
        // are listed; a name that is not loaded is skipped with a warning.
        // The XML def overrides this list.
        public static readonly List<string> DEFAULT_WET_AMBIENT_BIOMES = new List<string>
        {
            "RUT_Greentide", "RM_Greentide",
            "RUT_Miasma",    "RM_Miasma",
            "RUT_FeverWood", "RM_FeverWood",
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
        public static float WetAmbientMultiplier     = WET_AMBIENT_MULTIPLIER;
        public static float WetAmbientTreeMultiplier = WET_AMBIENT_TREE_MULTIPLIER;
        public static float MinGrowDaysToBoost   = MIN_GROW_DAYS_TO_BOOST;

        /// <summary>True once the caches are built. The postfix no-ops until then.</summary>
        public static bool Ready { get; private set; }

        // Built once at startup and never written again, so the postfix does only
        // lookups — no allocation and no write race if another mod ticks plants
        // off the main thread.
        private static HashSet<ThingDef> _exempt = new HashSet<ThingDef>();
        private static Dictionary<ThingDef, float> _multiplierByDef = new Dictionary<ThingDef, float>();
        private static HashSet<BiomeDef> _terminatorBiomes = new HashSet<BiomeDef>();
        private static Dictionary<ThingDef, float> _wetMultiplierByDef = new Dictionary<ThingDef, float>();
        private static HashSet<BiomeDef> _wetAmbientBiomes = new HashSet<BiomeDef>();

        public static int ExemptCount => _exempt.Count;
        public static int ScaledCount => _multiplierByDef.Count;
        public static int TerminatorBiomeCount => _terminatorBiomes.Count;
        public static int WetAmbientBiomeCount => _wetAmbientBiomes.Count;

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
            List<string> wetNames = DEFAULT_WET_AMBIENT_BIOMES;

            PlantGrowthSettingsDef settings = PlantGrowthSettingsDef.Current;
            if (settings != null)
            {
                if (settings.terminatorBiomes != null) terminatorNames = settings.terminatorBiomes;
                if (settings.exemptPlants != null) exemptNames = settings.exemptPlants;
                if (settings.wetAmbientBiomes != null) wetNames = settings.wetAmbientBiomes;
            }

            // MOD_OPTIONS_RETROFIT_1: the four numeric bands are owned by the
            // in-game Mod Settings screen (PlantGrowthSettings), not the XML def
            // above — see PlantGrowthMod.cs for why. Defaults match the shipped
            // def's numbers exactly.
            DefaultMultiplier = PlantGrowthSettings.defaultMultiplier;
            TreeMultiplier = PlantGrowthSettings.treeMultiplier;
            TerminatorMultiplier = PlantGrowthSettings.terminatorMultiplier;
            MinGrowDaysToBoost = PlantGrowthSettings.minGrowDaysToBoost;
            WetAmbientMultiplier = PlantGrowthSettings.wetAmbientMultiplier;
            WetAmbientTreeMultiplier = PlantGrowthSettings.wetAmbientTreeMultiplier;

            var exempt = new HashSet<ThingDef>();
            var multipliers = new Dictionary<ThingDef, float>();
            var wetMultipliers = new Dictionary<ThingDef, float>();
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
                wetMultipliers[def] = def.plant.IsTree ? WetAmbientTreeMultiplier : WetAmbientMultiplier;
            }

            var biomes = new HashSet<BiomeDef>();
            foreach (string name in terminatorNames)
            {
                BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail(name);
                if (biome != null) biomes.Add(biome);
                else Log.Warning("[RimMandrake.Utinni.PlantGrowth] terminator biome '" + name + "' is not loaded; skipping it.");
            }

            var wetBiomes = new HashSet<BiomeDef>();
            foreach (string name in wetNames)
            {
                BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail(name);
                if (biome != null) wetBiomes.Add(biome);
                // Silent on purpose for the wet band: the list carries BOTH the
                // campaign twin and the standalone RM_ biome, and a player
                // running only one of them should not see a warning per load.
            }

            _exempt = exempt;
            _multiplierByDef = multipliers;
            _terminatorBiomes = biomes;
            _wetMultiplierByDef = wetMultipliers;
            _wetAmbientBiomes = wetBiomes;
            Ready = true;
        }

        public static bool IsExempt(ThingDef def) => _exempt.Contains(def);

        public static bool IsTerminatorBiome(BiomeDef biome) =>
            biome != null && _terminatorBiomes.Contains(biome);

        public static float MultiplierFor(ThingDef def) =>
            _multiplierByDef.TryGetValue(def, out float m) ? m : 1f;

        public static bool IsWetAmbientBiome(BiomeDef biome) =>
            biome != null && _wetAmbientBiomes.Contains(biome);

        public static float WetAmbientMultiplierFor(ThingDef def) =>
            _wetMultiplierByDef.TryGetValue(def, out float m) ? m : 1f;
    }
}
