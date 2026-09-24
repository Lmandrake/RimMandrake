using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Hands the RM_PaintGraffitiJob to any free colonist for a cell the
    // player designated with Designator_PaintGraffitiMark. Same job/driver
    // the spree and joy paths already use (JobDriver_PaintGraffiti) - see
    // that file's own comment on how it tells a designated cell apart from
    // an ordinary one and picks the designator-eligible pool for it.
    public class WorkGiver_PaintGraffitiDesignated : WorkGiver_Scanner
    {
        public override bool Prioritized => false;

        public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RMGraffitiDefOf.RM_PaintGraffitiHere))
            {
                yield return d.target.Cell;
            }
        }

        public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (!RM_GraffitiSettings.paintingEnabled) return false;
            if (pawn.Map.designationManager.DesignationAt(c, RMGraffitiDefOf.RM_PaintGraffitiHere) == null) return false;
            return pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.None);
        }

        public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (!HasJobOnCell(pawn, c, forced)) return null;
            return JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, c);
        }
    }
}
