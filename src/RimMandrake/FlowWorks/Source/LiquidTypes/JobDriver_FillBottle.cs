using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Carries one RM_BottleEmpty to a matching liquid edge and
    /// swaps it for one RM_Bottle_&lt;Liquid&gt; there. Reads
    /// RM_LiquidBottleUtility and LiquidDef.bottled generically -- no
    /// per-liquid subclass, the whole point of RM_BottledLiquidExtension.
    /// LIQUID_BOTTLE_LOOP_1.</summary>
    public class JobDriver_FillBottle : JobDriver
    {
        private const int FillTicks = 180;

        private Thing Bottle => job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Bottle, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.Touch);

            Toil fill = Toils_General.Wait(FillTicks).WithProgressBarToilDelay(TargetIndex.B);
            fill.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
            yield return fill;

            Toil finish = ToilMaker.MakeToil("MakeNewToils");
            finish.initAction = delegate
            {
                // Re-read the cell rather than trust the WorkGiver's snapshot
                // -- a body can recede or be filled in during travel, and a
                // stale target minting a bottle of nothing is exactly the
                // failure WorkGiver_FillInCanal's own staleness discipline
                // exists to avoid.
                LiquidDef liquid;
                if (!RM_LiquidBottleUtility.TryGetLiquidAt(Map, job.targetB.Cell, out liquid)
                    || liquid.bottled?.bottle == null)
                {
                    return;
                }
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null)
                {
                    return;
                }
                carried.Destroy();
                Thing filled = ThingMaker.MakeThing(liquid.bottled.bottle);
                filled.stackCount = 1;
                GenPlace.TryPlaceThing(filled, pawn.Position, Map, ThingPlaceMode.Near);
            };
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return finish;
        }
    }
}
