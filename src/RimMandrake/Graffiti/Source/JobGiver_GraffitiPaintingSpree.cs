using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Absorbed from Mlie.GraffitiMod's JobGiver_GraffitiPaintingSpree
    // (compiled-only, no source shipped) - fires the same paint job as the
    // ordinary joy path, but as the ThinkTree's forced job during the
    // mental-break state (see Defs/ThinkTreeDefs_Graffiti.xml, same
    // insertTag/shape as the donor mod's SubTrees_Misc.xml).
    public class JobGiver_GraffitiPaintingSpree : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn.Map == null) return null;
            if (!GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 cell)) return null;
            return JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, cell);
        }
    }
}
