using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Carries one empty container to a tank and fills it from the
    /// tank's stock, swapping the carried Thing for the correctly-sized
    /// filled sibling. Mirror of <see cref="JobDriver_EmptyBottleIntoTank"/>
    /// run in reverse. LIQUID_BOTTLE_LOOP_1.</summary>
    public class JobDriver_FillBottleFromTank : JobDriver
    {
        private const int FillTicks = 180;

        private Thing Bottle => job.targetA.Thing;

        private Building_LiquidTank Tank => job.targetB.Thing as Building_LiquidTank;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Bottle, job, 1, 1, null, errorOnFailed)
                && pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOnDespawnedNullOrForbidden(TargetIndex.B);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);

            Toil fill = Toils_General.Wait(FillTicks).WithProgressBarToilDelay(TargetIndex.B);
            fill.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
            yield return fill;

            Toil finish = ToilMaker.MakeToil("MakeNewToils");
            finish.initAction = delegate
            {
                Building_LiquidTank tank = Tank;
                Thing carried = pawn.carryTracker.CarriedThing;
                if (tank == null || carried == null || tank.Empty)
                {
                    return;
                }
                RM_BottledLiquidExtension ext = carried.def.GetModExtension<RM_BottledLiquidExtension>();
                RM_ContainerSize size = ext?.size ?? RM_ContainerSize.Bottle;
                LiquidDef liquid = tank.storedLiquid;
                ThingDef filledDef = liquid.bottled?.FilledDefFor(size);
                int units = liquid.UnitsFor(size);
                if (filledDef == null || !tank.TryRemoveLiquid(units))
                {
                    // The tank ran dry, or holds a liquid with no form at
                    // this size, between the WorkGiver's scan and now --
                    // leave the carried container alone.
                    return;
                }
                carried.Destroy();
                Thing filled = ThingMaker.MakeThing(filledDef);
                filled.stackCount = 1;
                GenPlace.TryPlaceThing(filled, pawn.Position, Map, ThingPlaceMode.Near);
            };
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return finish;
        }
    }
}
