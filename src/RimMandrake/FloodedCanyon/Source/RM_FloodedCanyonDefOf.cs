using RimWorld;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // Our own mod's own defs, always present in this package — safe to use
    // [DefOf] rather than GetNamedSilentFail (that softer route is for
    // defs gated behind another mod or DLC, which none of these are).
    [DefOf]
    public static class RM_FloodedCanyonDefOf
    {
        public static BiomeDef RM_FloodedCanyon;

        public static GameConditionDef RM_CanyonFlood;

        // CRACKEDLANDS_RULED_CONTENT_1's wall-face mineables
        // (Defs/ThingDefs_Buildings/RM_FossilSeams.xml), placed by
        // RM_FossilStrata (CRACKEDLANDS_MECHANICS_BUILD_1 §3).
        public static ThingDef RM_FossilSeam_Impression;
        public static ThingDef RM_FossilSeam_Skeleton;
        public static ThingDef RM_FossilSeam_Unique;

        // CRACKEDLANDS_MECHANICS_BUILD_1 §5 — the herald sky.
        public static WeatherDef RM_PeakstormLight;

        static RM_FloodedCanyonDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_FloodedCanyonDefOf));
        }
    }
}
