using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TENTACLE_SETPIECE_TUNING_1, §6f's Uranium free
    /// tier. Carries a reachable RM_RadioactiveSuppressant stack to a
    /// designated pool cell, consumes up to
    /// RM_FeverWoodSettings.tentacleUraniumSuppressantAmountPerUse of it,
    /// and calls RM_MapComponent_TentacleWatch.
    /// SuppressPoolWithRadioactiveMaterial. Toil shape cribbed from
    /// RM_JobDriver_HaulToStake (goto/StartCarryThing/goto/finish), with
    /// the destination a bare cell instead of a Thing.</summary>
    public class RM_JobDriver_FoulPool : JobDriver
    {
        protected Thing Suppressant => job.GetTarget(TargetIndex.A).Thing;
        protected IntVec3 PoolCell => job.GetTarget(TargetIndex.B).Cell;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Suppressant, job, 1, job.count, null, errorOnFailed)
                && pawn.Reserve(PoolCell, job, 1, -1, null, errorOnFailed); // one worker per designated cell
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.A);

            Toil goToSuppressant = Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A)
                .FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return goToSuppressant;

            yield return Toils_Haul.StartCarryThing(TargetIndex.A);

            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.Touch);

            Toil foul = ToilMaker.MakeToil("FoulPool");
            foul.defaultCompleteMode = ToilCompleteMode.Instant;
            foul.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null)
                {
                    return;
                }

                // Switched off while the pawn was hauling: spend nothing, put the charges back (the work giver and
                // designator already refuse; this closes the window of a job started before the toggle flipped).
                if (!RM_PoolKernel.FoulingAllowed(RM_FeverWoodSettings.tentacleUraniumSuppressionEnabled))
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                    return;
                }

                // Designation cancelled (or already fulfilled) while hauling: spend nothing.
                if (pawn.Map.designationManager.DesignationAt(PoolCell, RM_SuppressionDefOf.RM_Designation_FoulPool) == null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                    return;
                }

                int amount = RM_PoolKernel.ChargesTaken(carried.stackCount, RM_FeverWoodSettings.tentacleUraniumSuppressantAmountPerUse);
                bool takingAll = RM_PoolKernel.TakesAll(carried.stackCount, amount);

                pawn.Map.designationManager.TryRemoveDesignation(PoolCell, RM_SuppressionDefOf.RM_Designation_FoulPool);

                Thing consumed = carried.SplitOff(amount);
                consumed.Destroy();

                if (!takingAll && pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                }

                RM_MapComponent_TentacleWatch watch = pawn.Map.GetComponent<RM_MapComponent_TentacleWatch>();
                watch?.SuppressPoolWithRadioactiveMaterial(RM_PoolKernel.SuppressionTicks(RM_FeverWoodSettings.tentacleUraniumSuppressionDurationDays));
            };
            yield return foul;
        }
    }
}
