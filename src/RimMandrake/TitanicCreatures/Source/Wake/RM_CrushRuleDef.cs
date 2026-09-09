using RimWorld;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// One curated row of the crush table (item ruling #3: "a data table says
    /// which thing categories/defs crush under a titan and which don't...
    /// never everything in radius"). Exactly one of <see cref="thing"/> /
    /// <see cref="category"/> should be set per row; an exact-def row always
    /// wins over a category row for the same Thing (see CrushTableUtility).
    ///
    /// Anything matching no row at all is NEVER crushed - the safe default the
    /// ruling demands, not an opt-out list.
    /// </summary>
    public class RM_CrushRuleDef : Def
    {
        /// <summary>Exact-def match - highest priority. e.g. Wall -&gt; crushable.</summary>
        public ThingDef thing;

        /// <summary>Category match, checked only if no exact-def row matched this Thing.</summary>
        public ThingCategoryDef category;

        /// <summary>Whether things this row matches crush at all.</summary>
        public bool crushable;

        /// <summary>Minimum titan tier required for this row to take effect (mirrors the tier table's "T1 flora/items, T2 +furniture/walls, T3 structures outright").</summary>
        public TitanicTier minTier = TitanicTier.T1;
    }
}
