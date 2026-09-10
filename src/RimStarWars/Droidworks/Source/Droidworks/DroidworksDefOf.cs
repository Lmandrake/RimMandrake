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
        // DROIDWORKS_BOLT_PAYOFF_1 (packet B5)
        public static JobDef RSW_DW_UnclampBolt;

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

        // DROIDWORKS_FINE_PARTS_1 (packet B4a) - read by CompDWPartDropper.LegalSetFor
        public static ThingDef RSW_DW_Part_Leg;
        public static ThingDef RSW_DW_Part_Manipulator;
        public static ThingDef RSW_DW_Part_Sensor;
        public static ThingDef RSW_DW_Part_Motivator;
        public static ThingDef RSW_DW_Part_Servo;
        public static ThingDef RSW_DW_Part_PowerCell;
        public static ThingDef RSW_DW_Part_Frame;

        // DROIDWORKS_SHOP_BENCHES_1 (packet B4b)
        public static ThingDef RSW_DW_RepairBench;
        public static PawnKindDef RSW_DW_OuterRim_ImperialLaborDroid;
        public static PawnKindDef RSW_DW_OuterRim_ProtocolDroid;
        public static PawnKindDef RSW_DW_OuterRim_RSeriesDroid;
        public static PawnKindDef RSW_DW_OuterRim_BattleDroid;
        public static PawnKindDef RSW_DW_OuterRim_SuperTacticalDroid;
        public static PawnKindDef RSW_DW_KotORDroidColonist_KX12UPD;
        public static PawnKindDef RSW_DW_OuterRim_GNKDroid;
        public static HediffDef RSW_DW_Overclocked;

        // DROIDWORKS_WIPE_SEVERITY_1 (packet B10) - the 7-day relearning debuff
        // added by Recipe_DWMemoryWipe. The hardware-quirk TraitDefs are
        // deliberately NOT listed here: that pool is discovered through the
        // HardwareQuirkExtension marker (DroidworksHardwareQuirks) so a later
        // packet can add one in XML alone.
        public static HediffDef RSW_DW_RecentlyWiped;

        // DROIDWORKS_PRIMITIVE_TIER_1 (packet B9) - read by
        // CompDWHeadDropper.HeadDefFor / CompDWPartDropper.LegalSetFor
        // (chassisClass 7) and DroidAssembly.KindForHeadDef.
        public static ThingDef RSW_DW_Head_Primitive;
        public static ThingDef RSW_DW_Part_Frame_Primitive;
        public static ThingDef RSW_DW_Part_Leg_Primitive;
        public static ThingDef RSW_DW_Part_Manipulator_Primitive;
        public static ThingDef RSW_DW_Part_Sensor_Primitive;
        public static ThingDef RSW_DW_Part_Motivator_Primitive;
        public static ThingDef RSW_DW_Part_Servo_Primitive;
        public static ThingDef RSW_DW_Part_PowerCell_Primitive;
        public static PawnKindDef RSW_DW_Primitive_G2;

        static DroidworksDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(DroidworksDefOf));
    }
}
