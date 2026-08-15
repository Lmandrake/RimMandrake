using System.Collections.Generic;
using Verse;

namespace JawaPlantGrowth
{
    /// <summary>
    /// XML carrier for everything in PlantGrowthConfig, so the bands, the terminator
    /// biome roster and the exempt list can change without a rebuild.
    /// Defs/JawaPlantGrowthSettings.xml holds the one instance.
    /// </summary>
    public class PlantGrowthSettingsDef : Def
    {
        public float defaultMultiplier    = PlantGrowthConfig.DEFAULT_MULTIPLIER;
        public float treeMultiplier       = PlantGrowthConfig.TREE_MULTIPLIER;
        public float terminatorMultiplier = PlantGrowthConfig.TERMINATOR_MULTIPLIER;
        public float minGrowDaysToBoost   = PlantGrowthConfig.MIN_GROW_DAYS_TO_BOOST;

        public List<string> terminatorBiomes;
        public List<string> exemptPlants;

        /// <summary>The single loaded instance, or null if the def file is missing.</summary>
        public static PlantGrowthSettingsDef Current
        {
            get
            {
                List<PlantGrowthSettingsDef> all = DefDatabase<PlantGrowthSettingsDef>.AllDefsListForReading;
                return all.Count > 0 ? all[0] : null;
            }
        }
    }
}
