using RimWorld;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // LEANINGSCRUB_MECHANICS_BUILD_1. Every def this assembly's C# names, all
    // shipped by this mod except RM_VenomvineScratch (the shared venomvine
    // damage, mandrake.rm.environmentalhazards — a declared hard dependency).
    [DefOf]
    public static class RM_LeaningScrubDefOf
    {
        public static WeatherDef RM_Stall;
        public static WeatherDef RM_Gale;

        public static HediffDef RM_GaleDeafened;

        static RM_LeaningScrubDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_LeaningScrubDefOf));
        }
    }
}
