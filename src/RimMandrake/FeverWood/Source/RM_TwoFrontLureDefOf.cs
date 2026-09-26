using RimWorld;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TWO_FRONT_LURE_1. Same [DefOf] shape as
    // RM_EnvironmentalHazardsJobDefOf (EnvironmentalHazards/Source/
    // RM_CompStationEater.cs) — a static-field DefOf class, resolved once by
    // DefOfHelper after Defs load.
    [DefOf]
    public static class RM_TwoFrontLureDefOf
    {
        public static JobDef RM_StunForStaking;
        public static JobDef RM_HaulToStake;
        public static DesignationDef RM_Designation_StakeLure;
        public static ThingDef RM_LureStake;

        static RM_TwoFrontLureDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TwoFrontLureDefOf));
        }
    }
}
