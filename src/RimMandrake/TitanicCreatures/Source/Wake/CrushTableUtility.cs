using System.Collections.Generic;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Reads the curated RM_CrushRuleDef table (Defs/CrushRuleDefs). Built
    /// lazily and cached - the table is small and author-curated, not something
    /// that changes at runtime.
    /// </summary>
    public static class CrushTableUtility
    {
        private static Dictionary<ThingDef, RM_CrushRuleDef> byDef;
        private static List<RM_CrushRuleDef> categoryRules;

        private static void EnsureBuilt()
        {
            if (byDef != null)
            {
                return;
            }
            byDef = new Dictionary<ThingDef, RM_CrushRuleDef>();
            categoryRules = new List<RM_CrushRuleDef>();
            foreach (RM_CrushRuleDef rule in DefDatabase<RM_CrushRuleDef>.AllDefsListForReading)
            {
                if (rule.thing != null)
                {
                    // Last-loaded wins on a duplicate exact-def row. The table is
                    // small and hand-authored (curated, per the ruling) - a
                    // collision here is an authoring bug to catch on review, not
                    // something worth a runtime warning system.
                    byDef[rule.thing] = rule;
                }
                else if (rule.category != null)
                {
                    categoryRules.Add(rule);
                }
            }
        }

        /// <summary>
        /// Would this Thing crush under a titan currently at this tier? Never
        /// "everything in radius" - unlisted Things are protected by default.
        /// </summary>
        public static bool IsCrushableAtTier(Thing t, TitanicTier tier)
        {
            if (t?.def == null || tier == TitanicTier.None)
            {
                return false;
            }
            EnsureBuilt();

            if (byDef.TryGetValue(t.def, out RM_CrushRuleDef exact))
            {
                return exact.crushable && tier >= exact.minTier;
            }

            if (t.def.thingCategories != null)
            {
                for (int i = 0; i < categoryRules.Count; i++)
                {
                    RM_CrushRuleDef rule = categoryRules[i];
                    if (t.def.thingCategories.Contains(rule.category))
                    {
                        return rule.crushable && tier >= rule.minTier;
                    }
                }
            }

            return false;
        }
    }
}
