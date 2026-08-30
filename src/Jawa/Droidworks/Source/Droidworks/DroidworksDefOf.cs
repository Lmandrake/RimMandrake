using RimWorld;
using Verse;

namespace Droidworks
{
    [DefOf]
    public static class DroidworksDefOf
    {
        public static HediffDef DW_PoweredDown;
        public static HediffDef DW_IonOverload;
        public static NeedDef DW_Power;

        static DroidworksDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(DroidworksDefOf));
    }
}
