using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StickCuisine
{
    [DefOf]
    public static class StickCuisineDefOf
    {
        public static ThingDef RUT_Skewer;

        static StickCuisineDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(StickCuisineDefOf));
        }
    }
}
