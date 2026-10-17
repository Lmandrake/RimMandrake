using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU: on its own a pawn fills only with Potable-class liquid; a forced
    /// (player-ordered) fill may take any liquid the container can hold.
    /// Opportunistic, like vanilla's own automatic WorkGivers
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
            if (!forced && ext.size == RM_ContainerSize.Bottle && Thirst.RM_BottleStock.Deficit(pawn.Map) <= 0)
            {
                return false;   // THIRST_RULES_BUILD_SALT_OFF_THE_MENU §8.2 step 8: the colony has its bottles
            }
            IntVec3 cell;
            LiquidDef liquid;
            string refusal;
            if (RM_LiquidBottleUtility.TryFindFillCell(pawn, t, out cell, out liquid, out refusal, forced))
            {
                return true;
            }
            if (refusal != null)
            {
                // FLOWWORKS_CONTAINER_MATERIALS_1: the float menu says why (leather vs boiling/acid).
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
            IntVec3 cell;
            LiquidDef liquid;
            string refusal;
            if (!RM_LiquidBottleUtility.TryFindFillCell(pawn, t, out cell, out liquid, out refusal, forced))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillBottleJob, t, cell);
            // §8.2 step 8: bottles in batches of up to ten (never past the stock target unless ordered); a bucket or barrel one at a time
            job.count = ext.size != RM_ContainerSize.Bottle ? 1
                : System.Math.Max(1, System.Math.Min(System.Math.Min(t.stackCount, Thirst.RM_BottleStock.BatchSize),
                    forced ? int.MaxValue : Thirst.RM_BottleStock.Deficit(pawn.Map)));
            return job;
        }
    }
}
