using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>LIQUID_BOTTLE_LOOP_1's tank half, draw-out direction. Any
    /// spawned, unforbidden EMPTY container near a tank holding enough of a
    /// liquid that has a bottled form at that container's size is a standing
    /// invitation to carry it there and fill it. Mirror of
    /// <see cref="WorkGiver_FillBottle"/> with the tank as the source
    /// instead of a terrain edge.</summary>
    public class WorkGiver_FillBottleFromTank : WorkGiver_Scanner
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
            if (ext == null
                || !ext.IsEmpty
                || t.IsForbidden(pawn)
                || !pawn.CanReserve(t, 1, 1, null, forced))
            {
                return false;
            }
            Building_LiquidTank tank;
            LiquidDef liquid;
            string refusal;
            if (RM_LiquidTankUtility.TryFindTankToDrain(pawn, t, ext.size, out tank, out liquid, out refusal))
            {
                return true;
            }
            if (refusal != null)
            {
                JobFailReason.Is(refusal);
            }
            return false;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext == null || !ext.IsEmpty)
            {
                return null;
            }
            Building_LiquidTank tank;
            LiquidDef liquid;
            string refusal;
            if (!RM_LiquidTankUtility.TryFindTankToDrain(pawn, t, ext.size, out tank, out liquid, out refusal))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillFromTankJob, t, tank);
            job.count = 1;
            return job;
        }
    }
}
