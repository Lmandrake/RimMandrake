using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // PORTED_BEAST_MECHANICS_REBUILD_1. RSW_EatMetal is defined in
    // src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMechanics.xml.
    // SHRUBLAND_SCRAPNEST_BIRDS_1. RSW_HoardScrap is defined in
    // src/RimStarWars/SWBestiary/Defs/ScrapNest/RSW_ScrapNest.xml.
    [DefOf]
    public static class RSW_BeastMechanicsDefOf
    {
        public static JobDef RSW_EatMetal;

        public static JobDef RSW_HoardScrap;

        static RSW_BeastMechanicsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RSW_BeastMechanicsDefOf));
        }
    }
}
