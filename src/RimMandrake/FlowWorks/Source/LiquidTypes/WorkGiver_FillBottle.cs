using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Opportunistic, like vanilla's own automatic WorkGivers
    /// (Refuel, FillFermentingBarrel) -- no player designation needed. Any
    /// spawned, unforbidden RM_BottleEmpty near a matching liquid edge is a
    /// standing invitation to fill it. LIQUID_BOTTLE_LOOP_1.</summary>
    public class WorkGiver_FillBottle : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForDef(RimMandrakeFlowWorks_DefOf.RM_BottleEmpty);

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RimMandrakeFlowWorksSettings.bottleLoopEnabled;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (t.def != RimMandrakeFlowWorks_DefOf.RM_BottleEmpty
                || t.IsForbidden(pawn)
                || !pawn.CanReserve(t, 1, -1, null, forced))
            {
                return false;
            }
            IntVec3 cell;
            LiquidDef liquid;
            return RM_LiquidBottleUtility.TryFindFillCell(pawn, out cell, out liquid);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            IntVec3 cell;
            LiquidDef liquid;
            if (!RM_LiquidBottleUtility.TryFindFillCell(pawn, out cell, out liquid))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillBottleJob, t, cell);
            job.count = 1;
            return job;
        }
    }
}
