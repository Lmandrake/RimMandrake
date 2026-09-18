using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Carries one filled container to a tank and pours its
    /// contents in, swapping the carried Thing for the correctly-sized empty
    /// sibling. Mirror of <see cref="JobDriver_FillBottle"/>, run against a
    /// Building target (targetB) instead of a terrain cell.
    /// LIQUID_BOTTLE_LOOP_1.</summary>
    public class JobDriver_EmptyBottleIntoTank : JobDriver
    {
        private const int PourTicks = 180;

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

            Toil pour = Toils_General.Wait(PourTicks).WithProgressBarToilDelay(TargetIndex.B);
            pour.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
            yield return pour;

            Toil finish = ToilMaker.MakeToil("MakeNewToils");
            finish.initAction = delegate
            {
                Building_LiquidTank tank = Tank;
                Thing carried = pawn.carryTracker.CarriedThing;
                if (tank == null || carried == null)
                {
                    return;
                }
                RM_BottledLiquidExtension ext = carried.def.GetModExtension<RM_BottledLiquidExtension>();
                if (ext?.liquid == null)
                {
                    return;
                }
                int units = ext.liquid.UnitsFor(ext.size);
                if (!tank.TryAddLiquid(ext.liquid, units))
                {
                    // The tank filled up, or picked up a different liquid,
                    // between the WorkGiver's scan and now -- leave the
                    // carried container alone rather than destroy it for a
                    // pour that did not happen.
                    return;
                }
                ThingDef emptyDef = RM_LiquidBottleUtility.EmptyDefFor(ext.size);
                if (emptyDef == null)
                {
                    return;
                }
                carried.Destroy();
                Thing empty = ThingMaker.MakeThing(emptyDef);
                empty.stackCount = 1;
                GenPlace.TryPlaceThing(empty, pawn.Position, Map, ThingPlaceMode.Near);
            };
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return finish;
        }
    }
}
