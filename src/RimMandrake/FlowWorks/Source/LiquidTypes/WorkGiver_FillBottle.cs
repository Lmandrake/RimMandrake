using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Opportunistic, like vanilla's own automatic WorkGivers
    /// (Refuel, FillFermentingBarrel) -- no player designation needed. Any
    /// spawned, unforbidden empty container (bottle/bucket/barrel, read
    /// generically off RM_BottledLiquidExtension) near a matching liquid
    /// edge is a standing invitation to fill it. Scans HaulableEver rather
    /// than one ThingDef because the third slice (LIQUID_BOTTLE_LOOP_1)
    /// added two more empty defNames (RM_BucketEmpty, RM_BarrelEmpty)
    /// alongside RM_BottleEmpty -- the extension's own IsEmpty flag, not the
    /// defName, is what makes a Thing this WorkGiver's business.</summary>
    public class WorkGiver_FillBottle : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RimMandrakeFlowWorksSettings.bottleLoopEnabled;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext == null
                || !ext.IsEmpty
                || t.IsForbidden(pawn)
                || !pawn.CanReserve(t, 1, -1, null, forced))
            {
                return false;
            }
            IntVec3 cell;
            LiquidDef liquid;
            return RM_LiquidBottleUtility.TryFindFillCell(pawn, out cell, out liquid, size: ext.size);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext == null || !ext.IsEmpty)
            {
                return null;
            }
            IntVec3 cell;
            LiquidDef liquid;
            if (!RM_LiquidBottleUtility.TryFindFillCell(pawn, out cell, out liquid, size: ext.size))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillBottleJob, t, cell);
            job.count = 1;
            return job;
        }
    }
}
