using RimWorld;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    [DefOf]
    public static class RM_TitanicCreaturesDefOf
    {
        public static ThingDef RM_TitanicCorpseSite;
        public static JobDef RM_HarvestTitanicCorpse;

        static RM_TitanicCreaturesDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TitanicCreaturesDefOf));
        }
    }
}
