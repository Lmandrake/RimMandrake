using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>LIQUID_BOTTLE_LOOP_1's tank half, pour-in direction. Any
    /// spawned, unforbidden FILLED container (bottle/bucket/barrel -- read
    /// generically off RM_BottledLiquidExtension, same as
    /// <see cref="WorkGiver_FillBottle"/>) near a tank that can take its
    /// contents is a standing invitation to carry it there and pour it in.
    /// Mirror of WorkGiver_FillBottle's shape; the source/destination roles
    /// are simply swapped -- a filled container is now the thing being
    /// EMPTIED, and the tank is the destination rather than terrain.</summary>
    public class WorkGiver_EmptyBottleIntoTank : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RimMandrakeFlowWorksSettings.tankLoopEnabled;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext?.liquid == null
                || t.IsForbidden(pawn)
                || !pawn.CanReserve(t, 1, 1, null, forced))
            {
                return false;
            }
            int units = ext.liquid.UnitsFor(ext.size);
            Building_LiquidTank tank;
            return RM_LiquidTankUtility.TryFindTankToFill(pawn, ext.liquid, units, out tank);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext?.liquid == null)
            {
                return null;
            }
            int units = ext.liquid.UnitsFor(ext.size);
            Building_LiquidTank tank;
            if (!RM_LiquidTankUtility.TryFindTankToFill(pawn, ext.liquid, units, out tank))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_EmptyIntoTankJob, t, tank);
            job.count = 1;
            return job;
        }
    }
}
