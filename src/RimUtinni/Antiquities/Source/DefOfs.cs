using RimWorld;
using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    [DefOf]
    public static class ThingDefOf_Antiquities
    {
        public static ThingDef RUT_AntiquityReadingStation;
    }

    [DefOf]
    public static class JobDefOf_Antiquities
    {
        public static JobDef RUT_ExamineAntiquity;
    }

    [DefOf]
    public static class WorkTypeDefOf_Antiquities
    {
        public static WorkTypeDef RUT_ExamineAntiquities;
    }

    // The five stages, in order. AntiquityUtility.Stages walks this array --
    // ANTIQUITIES_TREE_BUILD_1's own defNames, never renamed per the
    // owner's unblock caveat (design/Jawa/antiquities_design.md).
    [DefOf]
    public static class ResearchProjectDefOf_Antiquities
    {
        public static ResearchProjectDef RUT_Antiq_Language;
        public static ResearchProjectDef RUT_Antiq_Religion;
        public static ResearchProjectDef RUT_Antiq_Culture;
        public static ResearchProjectDef RUT_Antiq_Cartography;
        public static ResearchProjectDef RUT_Antiq_Voice;
    }
}
