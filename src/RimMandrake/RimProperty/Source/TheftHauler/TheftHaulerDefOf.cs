using RimWorld;
using Verse;

namespace RimMandrake.TheftHauler
{
    [DefOf]
    public static class TheftHaulerDefOf
    {
        public static JobDef RM_TheftHaulUninstall;

        static TheftHaulerDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(TheftHaulerDefOf));
    }
}
