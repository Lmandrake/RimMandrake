using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    [DefOf]
    public static class RM_DivingDefOf
    {
        public static JobDef RM_Job_DiveHunt;
        public static JobDef RM_Job_DiveCommune;

        public static ThingDef RM_ScaldWalkerChitin;

        public static ThoughtDef RM_Thought_CommunedWithDeep;

        static RM_DivingDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_DivingDefOf));
        }
    }
}
