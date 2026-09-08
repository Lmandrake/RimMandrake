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
        public static FleshTypeDef RSW_DW_FleshType_Droid;

        // DROIDWORKS_BOLT_CORE_1
        public static HediffDef RSW_DW_RestrainingBolt;
        public static HediffDef RSW_DW_BoltResentment;
        public static JobDef RSW_DW_ClampBolt;
        public static ThingDef RSW_DW_RestrainingBoltItem;

        // DROIDWORKS_FORMAT_TIERS_1
        public static HediffDef RSW_DW_FormatTier;
        public static HistoryEventDef RSW_DW_DeformattedSapientDroid;
        public static ThoughtDef RSW_DW_KnowSapientDroidDeformatted;

        // DROIDWORKS_HEADS_BRAINS_SPIKES_1 (packet B3) - one per chassisClass,
        // read by CompDWHeadDropper.HeadDefFor
        public static ThingDef RSW_DW_Head_Labour;
        public static ThingDef RSW_DW_Head_Protocol;
        public static ThingDef RSW_DW_Head_Astromech;
        public static ThingDef RSW_DW_Head_Battle;
        public static ThingDef RSW_DW_Head_Heavy;
        public static ThingDef RSW_DW_Head_Probe;
        public static ThingDef RSW_DW_Head_Power;

        static DroidworksDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(DroidworksDefOf));
    }
}
