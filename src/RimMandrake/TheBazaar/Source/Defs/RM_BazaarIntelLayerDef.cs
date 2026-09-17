using System.Collections.Generic;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 (design §4). Names ONE gate -- a Social skill
    /// band or a found artifact -- that columns and badges reference by
    /// defName, so rebalancing an intel layer (design's own worked table,
    /// L0..L4 and A1..A3) is a one-line data edit in one place rather than a
    /// scattered set of magic numbers across every column/badge worker that
    /// happens to gate on it.
    ///
    /// Pure data -- no worker. `IsUnlockedFor` reads the two possible gate
    /// shapes; a layer sets exactly one of them (checked below), matching
    /// the design table where every row is EITHER a Social band OR a found
    /// artifact, never both.
    /// </summary>
    public class RM_BazaarIntelLayerDef : Def
    {
        /// <summary>Design's Social-band layers (L1..L4): minimum Social
        /// skill on the negotiator. Null when this layer gates on an
        /// artifact instead.</summary>
        public int? minSocialSkill;

        /// <summary>Design's artifact layers (A1..A3): the ThingDef that
        /// must be carried/available. Null when this layer gates on Social
        /// instead.</summary>
        public ThingDef requiredArtifact;

        /// <summary>A3 (Deep almanac) lowers every Social gate above it by
        /// this many points once unlocked -- design §4's stated interaction
        /// between layers, not a coincidence to rediscover per-column.</summary>
        public int lowersOtherSocialGatesBy;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            bool hasSocial = minSocialSkill.HasValue;
            bool hasArtifact = requiredArtifact != null;
            if (hasSocial == hasArtifact)
            {
                yield return "RM_BazaarIntelLayerDef " + defName
                    + ": exactly one of minSocialSkill or requiredArtifact must be set (design "
                    + "table §4 -- every layer gates on Social OR an artifact, never both, never neither).";
            }
        }
    }
}
