using System.Collections.Generic;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 (design §4). Names ONE gate -- a Social skill
    /// band or a protocol-droid module -- that columns and badges reference by
    /// defName, so rebalancing an intel layer (design's own worked table,
    /// L0..L4 and D1..D4) is a one-line data edit in one place rather than a
    /// scattered set of magic numbers across every column/badge worker that
    /// happens to gate on it.
    ///
    /// Pure data -- no worker. RM_BazaarIntel reads the two possible gate
    /// shapes; a layer sets exactly one of them (checked below), matching
    /// the design table where every row is EITHER a Social band OR a droid
    /// module, never both. Evaluated by RM_BazaarIntel.IsUnlocked.
    /// </summary>
    public class RM_BazaarIntelLayerDef : Def
    {
        /// <summary>Design's Social-band layers (L1..L4): minimum Social
        /// skill on the negotiator. Null when this layer gates on a
        /// module instead.</summary>
        public int? minSocialSkill;

        /// <summary>Design's module layers (D1..D4, owner 2026-09-20: protocol-droid
        /// MODULES, fitted to a droid, never carried items): the HediffDef a
        /// FUNCTIONAL protocol droid in the party (or at a comms console) must
        /// carry. Null when this layer gates on Social instead.</summary>
        public HediffDef requiredModule;

        /// <summary>Which RM_BazaarSettings toggle switches this layer off
        /// (field name, e.g. "intelPriceContext"); empty = always on.</summary>
        public string settingsToggle;

        /// <summary>D4 (RM_PriceAlmanac) lowers every Social gate by this many
        /// points once unlocked -- design §4's stated interaction between
        /// layers, not a coincidence to rediscover per-column.</summary>
        public int lowersOtherSocialGatesBy;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            bool hasSocial = minSocialSkill.HasValue;
            bool hasModule = requiredModule != null;
            if (hasSocial == hasModule)
            {
                yield return "RM_BazaarIntelLayerDef " + defName
                    + ": exactly one of minSocialSkill or requiredModule must be set (design "
                    + "table §4 -- every layer gates on Social OR a droid module, never both, never neither).";
            }
        }
    }
}
