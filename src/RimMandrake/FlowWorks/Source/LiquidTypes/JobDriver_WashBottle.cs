using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>Mirror of <see cref="JobDriver_FillBottle"/>, run in reverse:
    /// carries one RM_BottleDirty to fresh water and swaps it for one
    /// RM_BottleEmpty there. LIQUID_BOTTLE_LOOP_1.</summary>
    public class JobDriver_WashBottle : JobDriver
    {
        private const int WashTicks = 120;

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

            Toil wash = Toils_General.Wait(WashTicks).WithProgressBarToilDelay(TargetIndex.B);
            wash.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
            yield return wash;

            Toil finish = ToilMaker.MakeToil("MakeNewToils");
            finish.initAction = delegate
            {
                LiquidDef liquid;
                bool stillFresh = RM_LiquidBottleUtility.TryGetLiquidAt(Map, job.targetB.Cell, out liquid)
                    && liquid == RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater;
                if (!stillFresh)
                {
                    return;
                }
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null)
                {
                    return;
                }
                carried.Destroy();
                Thing empty = ThingMaker.MakeThing(RimMandrakeFlowWorks_DefOf.RM_BottleEmpty);
                empty.stackCount = 1;
                GenPlace.TryPlaceThing(empty, pawn.Position, Map, ThingPlaceMode.Near);
            };
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return finish;
        }
    }
}
