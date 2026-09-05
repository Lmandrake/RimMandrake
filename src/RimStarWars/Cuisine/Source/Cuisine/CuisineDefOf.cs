using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Cuisine
{
    [DefOf]
    public static class CuisineDefOf
    {
        public static ThingDef RSW_Skewer;

        static CuisineDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(CuisineDefOf));
        }
    }
}
