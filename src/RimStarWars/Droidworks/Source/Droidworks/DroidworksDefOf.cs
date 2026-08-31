using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    [DefOf]
    public static class DroidworksDefOf
    {
        public static HediffDef RSW_DW_PoweredDown;
        public static HediffDef RSW_DW_IonOverload;
        public static NeedDef RSW_DW_Power;
        public static JobDef RSW_DW_Recharge;

        // DROIDWORKS_BOLT_CORE_1
        public static HediffDef RSW_DW_RestrainingBolt;
        public static HediffDef RSW_DW_BoltResentment;
        public static JobDef RSW_DW_ClampBolt;
        public static ThingDef RSW_DW_RestrainingBoltItem;

        static DroidworksDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(DroidworksDefOf));
    }
}
