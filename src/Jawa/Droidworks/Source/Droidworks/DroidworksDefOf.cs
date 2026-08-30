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
        public static JobDef DW_Recharge;

        // DROIDWORKS_BOLT_CORE_1
        public static HediffDef DW_RestrainingBolt;
        public static HediffDef DW_BoltResentment;
        public static JobDef DW_ClampBolt;
        public static ThingDef DW_RestrainingBoltItem;

        static DroidworksDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(DroidworksDefOf));
    }
}
