using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Mirror of <see cref="WorkGiver_FillBottle"/> for the other
    /// end of the loop: any spawned, unforbidden dirty container
    /// (bottle/bucket/barrel, read generically off
    /// RM_BottledLiquidExtension.dirty) near fresh water is a standing
    /// invitation to wash it. Gated on the master bottle-loop toggle ONLY,
    /// never on the dirty-stage toggle -- a colony that already holds dirty
    /// containers from before the toggle was switched off must still be
    /// able to wash them; the toggle only stops NEW dirty containers being
    /// minted (see IngestionOutcomeDoer_BottleResidue). LIQUID_BOTTLE_LOOP_1.</summary>
    public class WorkGiver_WashBottle : WorkGiver_Scanner
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
                || !ext.dirty
                || t.IsForbidden(pawn)
                || !pawn.CanReserve(t, 1, -1, null, forced))
            {
                return false;
            }
            IntVec3 cell;
            return RM_LiquidBottleUtility.TryFindWashCell(pawn, out cell);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
            if (ext == null || !ext.dirty)
            {
                return null;
            }
            IntVec3 cell;
            if (!RM_LiquidBottleUtility.TryFindWashCell(pawn, out cell))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_WashBottleJob, t, cell);
            job.count = 1;
            return job;
        }
    }
}
