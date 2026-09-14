using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    [DefOf]
    public static class BactaDefOf
    {
        public static ThingDef RSW_Bacta;

        public static ThingDef RSW_BactaTank;

        public static ResearchProjectDef RSW_BactaImmersion;

        static BactaDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(BactaDefOf));
        }
    }
}
