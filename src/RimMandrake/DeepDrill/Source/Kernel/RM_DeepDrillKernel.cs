// Verse-free kernel of the deep-drill home-biome filter (DEEP_DRILL_HOME_BIOME_1). The Harmony postfix calls Decide with the lump vanilla
// picked; SelfTest compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.DeepDrill
{
    public static class RM_DeepDrillKernel
    {
        /// <summary>The planet-wide deep resource every filtered pick falls back to (design minerals_where_they_belong §7 Q4 option A).</summary>
        public const string FallbackDefName = "Steel";

        /// <summary>True when the picked lump must be replaced by the fallback: the filter is on, the pick has a row in the table, and the
        /// map's biome is not among the row's homes. Unlisted defs (steel included) and a map with no biome pass through.</summary>
        public static bool ShouldReplace(bool enabled, string pickedDefName, string biomeDefName, IDictionary<string, HashSet<string>> homes)
        {
            if (!enabled || pickedDefName == null || homes == null) return false;
            if (pickedDefName == FallbackDefName) return false;
            if (!homes.TryGetValue(pickedDefName, out HashSet<string> set)) return false;
            if (biomeDefName == null) return false;
            return !set.Contains(biomeDefName);
        }
    }
}
