using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Hands out the scrub for marks the player dragged Designator_ScrubGraffiti over: the answering pawn's own RM_ScrubMark job (stand
    // before the wall, scrub, the story that goes with whose mark it was), under Cleaning, so it follows the work table. Unlike vanilla
    // Clean it reaches marks outside the Home area. The owner's card still holds: whoever hates an insult's subject won't scrub it.
    public class WorkGiver_ScrubGraffitiDesignated : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.OnCell;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RMGraffitiDefOf.RM_ScrubGraffiti))
            {
                if (d.target.Thing != null) yield return d.target.Thing;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RMGraffitiDefOf.RM_ScrubGraffiti);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!(t is Filth_Mark mark) || !mark.Spawned || pawn.Map.designationManager.DesignationOn(mark, RMGraffitiDefOf.RM_ScrubGraffiti) == null) return false;
            string refuses = GraffitiSocial.RefusesToClean(pawn, mark);
            if (refuses != null)
            {
                JobFailReason.Is(refuses);
                return false;
            }
            return !mark.Fogged() && pawn.CanReserveAndReach(mark.Position, PathEndMode.OnCell, pawn.NormalMaxDanger(), 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RMGraffitiDefOf.RM_ScrubMark, t, t.Position);
        }
    }
}
