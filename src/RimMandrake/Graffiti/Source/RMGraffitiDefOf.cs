using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    [DefOf]
    public static class RMGraffitiDefOf
    {
        public static ThingDef RM_Graffiti_Vandal;
        public static JobDef RM_PaintGraffitiJob;
        public static MentalStateDef RM_GraffitiPaintingSpreeState;
        public static DesignationDef RM_PaintGraffitiHere;
        public static ThingDef RM_Graffiti_Mockery, RM_Graffiti_Tribute, RM_Graffiti_Memorial;
        public static JobDef RM_ScrubMark, RM_DefaceMark, RM_ConfrontPainter;
        public static InteractionDef RM_Graffiti_Confront;
        public static HistoryEventDef RM_Graffiti_WallInsult, RM_Graffiti_SharedSign;

        static RMGraffitiDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RMGraffitiDefOf));
        }
    }
}
