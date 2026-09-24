using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    [DefOf]
    public static class BactaDefOf
    {
        public static ThingDef RSW_Bacta;

        public static ThingDef RSW_BactaTank;

        /// <summary>BACTA_SIDE_ITEMS_1: the linkable facility whose presence speeds the tank.</summary>
        public static ThingDef RSW_MedicalDroid;

        public static ResearchProjectDef RSW_BactaImmersion;

        public static JobDef RSW_CarryCorpseToBactaTank;

        static BactaDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(BactaDefOf));
        }
    }
}
