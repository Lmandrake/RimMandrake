using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 — DefOf for the sky engine and devices.
    [DefOf]
    public static class RM_ContagionSkyDefOf
    {
        public static WeatherDef RM_ContagionBloom;
        public static WeatherDef RM_ContagionBurn;
        public static GameConditionDef RM_ContagionBurnCondition;
        public static HediffDef RM_BurnDose;

        static RM_ContagionSkyDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ContagionSkyDefOf));
        }
    }
}
