using UnityEngine;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #4's second clause: "T1-T2 get curved (sub-linear) yields" (T3
    /// never reaches this path at all - its corpse is intercepted into
    /// Building_TitanicCorpseSite before any butchering happens; see
    /// Patch_Corpse_SpawnSetup_TitanicSite). Implemented as a multiplier on the
    /// `efficiency` parameter vanilla's own Pawn.ButcherProducts already
    /// scales MeatAmount/LeatherAmount by (Verse/Pawn.cs), rather than a new
    /// yield system: GenMath.RoundRandom(GetStatValue(StatDefOf.MeatAmount) *
    /// efficiency).
    /// </summary>
    public static class YieldCurveUtility
    {
        /// <summary>
        /// sqrt(floor / bodySize), clamped to [minFactor, 1]: doubling bodySize
        /// past a tier's floor only multiplies yield by ~1.41x rather than 2x,
        /// and it can never fall below the player-tunable floor
        /// (RM_TitanicCreaturesSettings.yieldCurveMinFactor). BENCH-draft curve
        /// shape, not owner-ruled - tune the exponent here if the sub-linear
        /// feel is wrong once real creature stats exist.
        /// </summary>
        public static float SubLinearFactor(Pawn pawn, TitanicTier tier)
        {
            RM_TitanicTierDef t = TitanicTierUtility.Thresholds;
            float floor = tier == TitanicTier.T1 ? t.t1MinBodySize : t.t2MinBodySize;
            float bodySize = Mathf.Max(pawn.BodySize, floor);
            return Mathf.Clamp(Mathf.Sqrt(floor / bodySize), RM_TitanicCreaturesSettings.yieldCurveMinFactor, 1f);
        }
    }
}
