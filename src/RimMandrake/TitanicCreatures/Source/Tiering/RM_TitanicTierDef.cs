using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The mod's single size-ladder authority (item ruling: "no second size
    /// ladder live"). One instance is expected to exist
    /// (Defs/TitanicTierDefs/RM_TitanicTierDef.xml); LargePawnsBridge pushes
    /// these same three numbers into Large Pawns' own settings so its ladder
    /// becomes a projection of this one rather than a second, independent one.
    ///
    /// Boundaries are BENCH draft (per the item's tier table), not owner-ruled
    /// - tune here against the actual creature roster census once one exists,
    /// never by editing this class.
    /// </summary>
    public class RM_TitanicTierDef : Def
    {
        /// <summary>T1 "heavy" floor - 2x2 footprint, light wake.</summary>
        public float t1MinBodySize = 4f;

        /// <summary>T2 "colossal" floor - 3x3 footprint, +furniture/walls, thin roofs holed.</summary>
        public float t2MinBodySize = 8f;

        /// <summary>T3 "titanic" floor - 4x4+ footprint, structures destroyed outright, corpse-site.</summary>
        public float t3MinBodySize = 20f;
    }
}
