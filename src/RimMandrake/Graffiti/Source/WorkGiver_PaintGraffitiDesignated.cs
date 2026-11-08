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
            // Live pass 18: an ordered throw-up went to a hauler with no Artistic, who painted a sigil in its place. An order goes to a hand that may
            // paint that mark, as the game's own art bills go to one with the skill; nobody else takes it.
            ThingDef ordered = MapComponent_GraffitiOrders.For(pawn.Map)?.OrderAt(c);
            if (ordered != null && !GraffitiPool.PainterMayPaint(ordered, pawn))
            {
                if (forced) JobFailReason.Is(GraffitiPool.WhyNot(ordered, pawn));
                return false;
            }
            return pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.None);
        }

        public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (!HasJobOnCell(pawn, c, forced)) return null;
            Job job = JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, c);
            // GPT deep review 2026-10-22 #3: an ordered mark is WORK; without this JoyTickCheckEnd ends it in work hours
            job.ignoreJoyTimeAssignment = true;
            return job;
        }
    }
}
