using RimWorld;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // Our own mod's own defs, always present in this package — safe to use
    // [DefOf] rather than GetNamedSilentFail (that softer route is for
    // defs gated behind another mod or DLC, which none of these are).
    [DefOf]
    public static class RM_FloodedCanyonDefOf
    {
        public static BiomeDef RM_FloodedCanyon;

        public static GameConditionDef RM_CanyonFlood;

        // CRACKEDLANDS_RULED_CONTENT_1's wall-face mineables
        // (Defs/ThingDefs_Buildings/RM_FossilSeams.xml), placed by
        // RM_FossilStrata (CRACKEDLANDS_MECHANICS_BUILD_1 §3).
        public static ThingDef RM_FossilSeam_Impression;
        public static ThingDef RM_FossilSeam_Skeleton;
        public static ThingDef RM_FossilSeam_Unique;

        // CRACKEDLANDS_MECHANICS_BUILD_1 §5 — the herald sky.
        public static WeatherDef RM_PeakstormLight;

        // CRACKEDLANDS_GPT_ENRICHMENT_1 §2 — five beats before water
        // (Defs/SoundDefs/RM_CanyonBeats.xml) and the tarruq hush.
        public static SoundDef RM_CanyonBeat_SlotWind;
        public static SoundDef RM_CanyonBeat_PanTick;
        public static SoundDef RM_CanyonChime_Far;
        public static SoundDef RM_CanyonChime_Mid;
        public static SoundDef RM_CanyonChime_Near;
        public static SoundDef RM_CanyonFlood_Roar;
        public static ThingDef RM_Tarruq;

        // §5 — the recede feast (Defs/ThingDefs_Races/RM_IrqitTarruq.xml,
        // Defs/HediffDefs/RM_IrqitFloodBorn.xml).
        public static PawnKindDef RM_Irqit;
        public static HediffDef RM_IrqitFloodBorn;

        static RM_FloodedCanyonDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_FloodedCanyonDefOf));
        }
    }
}
