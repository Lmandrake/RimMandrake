using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // SHRUBLAND_SCRAPNEST_BIRDS_1. RSW_HoardScrap is defined in
    // src/RimStarWars/SWBestiary/Defs/ScrapNest/RSW_ScrapNest.xml.
    [DefOf]
    public static class RSW_BeastMechanicsDefOf
    {
        public static JobDef RSW_HoardScrap;

        static RSW_BeastMechanicsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RSW_BeastMechanicsDefOf));
        }
    }
}
