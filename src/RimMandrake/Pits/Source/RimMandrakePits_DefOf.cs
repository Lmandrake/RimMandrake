using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    [DefOf]
    public static class RMPits_DesignationDefOf
    {
        public static DesignationDef RM_DigPitDeeper;

        static RMPits_DesignationDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RMPits_DesignationDefOf));
        }
    }

    [DefOf]
    public static class RMPits_JobDefOf
    {
        public static JobDef RM_DigPitDeeper;

        static RMPits_JobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RMPits_JobDefOf));
        }
    }

    [DefOf]
    public static class RMPits_HediffDefOf
    {
        public static HediffDef RM_PinnedInPit;
        public static HediffDef RM_PitExposure;
        public static HediffDef RM_PitDrowning;

        static RMPits_HediffDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RMPits_HediffDefOf));
        }
    }
}
