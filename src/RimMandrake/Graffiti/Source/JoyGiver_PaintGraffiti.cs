using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Absorbed from Mlie.GraffitiMod's JoyGiver_PaintGraffiti (compiled-only,
    // no source shipped) - a fresh implementation. Modeled on the verified
    // vanilla shape (JoyGiver_Skygaze, Source/RimWorld/JoyGiver_Skygaze.cs):
    // TryGiveJob finds a target cell, hands it to JobMaker.MakeJob.
    public class JoyGiver_PaintGraffiti : JoyGiver
    {
        public override Job TryGiveJob(Pawn pawn)
        {
            if (pawn.Map == null) return null;
            if (!GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 cell)) return null;
            return JobMaker.MakeJob(def.jobDef, cell);
        }
    }
}
