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

        static RM_FloodedCanyonDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_FloodedCanyonDefOf));
        }
    }
}
