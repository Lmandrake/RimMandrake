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

        static RMGraffitiDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RMGraffitiDefOf));
        }
    }
}
