using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TWO_FRONT_LURE_1. Carries a Downed pawn to an
    /// RM_LureStake and hands it to RM_CompLureStake.TryStake. Toil
    /// shape cribbed directly from vanilla JobDriver_TakeToBed (the real
    /// driver class behind the Rescue/Capture JobDefs, read in full via
    /// RimSage this pass) — goto-victim-while-Downed, StartCarryThing,
    /// goto-destination, drop — with the bed/prisoner-specific toils cut,
    /// since a lure stake is neither.</summary>
    public class RM_JobDriver_HaulToStake : JobDriver
    {
        protected Pawn Victim => (Pawn)job.GetTarget(TargetIndex.A).Thing;
        protected Thing Stake => job.GetTarget(TargetIndex.B).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(Victim, job, 1, -1, null, errorOnFailed))
            {
                return false;
            }
            return pawn.Reserve(Stake, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOn(() => Victim.Dead);

            AddFinishAction(delegate (JobCondition cond)
            {
                if (cond != JobCondition.Ongoing && pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Direct, out Thing _);
                }
            });

            // v1 scope cut, flagged: unlike vanilla JobDriver_TakeToBed this
            // does not special-case resuming a job that was interrupted
            // mid-carry (a Toils_Jump back into the middle of its own toil
            // list) — this job is only ever handed out fresh by
            // RM_WorkGiver_HaulToStake, never resumed from a save mid-carry
            // in a way that matters for a single-map hand-off to an adjacent
            // stake, so the simpler linear sequence below is a real,
            // accepted simplification, not an oversight.
            Toil goToVictim = Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B)
                .FailOn(() => !Victim.Downed)
                .FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return goToVictim;

            yield return Toils_Haul.StartCarryThing(TargetIndex.A);

            Toil goToStake = Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch)
                .FailOn(() => !pawn.IsCarryingPawn(Victim));
            yield return goToStake;

            Toil finish = ToilMaker.MakeToil("MakeNewToils");
            finish.initAction = delegate
            {
                RM_CompLureStake comp = Stake.TryGetComp<RM_CompLureStake>();
                if (pawn.carryTracker.CarriedThing == Victim)
                {
                    pawn.carryTracker.TryDropCarriedThing(Stake.Position, ThingPlaceMode.Near, out Thing _);
                }
                if (comp != null && !comp.HasLiveBait)
                {
                    comp.TryStake(Victim);
                }
            };
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return finish;
        }
    }
}
