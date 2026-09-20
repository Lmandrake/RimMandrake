using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // PORTED_BEAST_MECHANICS_REBUILD_1. Defined in
    // src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMechanics.xml.
    [DefOf]
    public static class RSW_BeastMechanicsDefOf
    {
        public static JobDef RSW_EatMetal;

        static RSW_BeastMechanicsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RSW_BeastMechanicsDefOf));
        }
    }
}
