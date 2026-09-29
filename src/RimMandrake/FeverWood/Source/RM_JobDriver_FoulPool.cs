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
            return pawn.Reserve(Suppressant, job, 1, job.count, null, errorOnFailed);
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

                int amount = Mathf.Min(carried.stackCount, Mathf.Max(1, RM_FeverWoodSettings.tentacleUraniumSuppressantAmountPerUse));
                bool takingAll = amount >= carried.stackCount;

                pawn.Map.designationManager.TryRemoveDesignation(PoolCell, RM_SuppressionDefOf.RM_Designation_FoulPool);

                Thing consumed = carried.SplitOff(amount);
                consumed.Destroy();

                if (!takingAll && pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                }

                if (RM_FeverWoodSettings.tentacleUraniumSuppressionEnabled)
                {
                    RM_MapComponent_TentacleWatch watch = pawn.Map.GetComponent<RM_MapComponent_TentacleWatch>();
                    int ticks = Mathf.RoundToInt(Mathf.Max(0.1f, RM_FeverWoodSettings.tentacleUraniumSuppressionDurationDays) * 60000f);
                    watch?.SuppressPoolWithRadioactiveMaterial(ticks);
                }
            };
            yield return foul;
        }
    }
}
