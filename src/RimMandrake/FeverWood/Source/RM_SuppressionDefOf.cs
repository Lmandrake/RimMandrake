using RimWorld;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_SETPIECE_TUNING_1. Same [DefOf] shape as
    // RM_TwoFrontLureDefOf — resolved once by DefOfHelper after Defs load.
    [DefOf]
    public static class RM_SuppressionDefOf
    {
        public static JobDef RM_FoulPool;
        public static DesignationDef RM_Designation_FoulPool;
        public static ThingDef RM_RadioactiveSuppressant;

        static RM_SuppressionDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_SuppressionDefOf));
        }
    }
}
