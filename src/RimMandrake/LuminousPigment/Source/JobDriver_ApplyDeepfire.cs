using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.3: fetch `cost` Deepfire, go to target, 600-tick toil x
    // WorkSpeedGlobal, Artistic XP 100, then CompDeepfire.AddCoat. Toil
    // shape (carry-then-work-then-consume, tickIntervalAction accumulating
    // work and finishing via ReadyForNextToil) copied from vanilla
    // JobDriver_PaintBuilding (RimWorld/JobDriver_PaintBuilding.cs, read via
    // RimSage this pass), simplified to a single target/single fetch (no
    // multi-target queueing -- not required by any step-5 proof row).
    //
    // 🔴 NO FailOnDespawnedNullOrForbidden / FailOnSomeonePhysicallyInteracting
    // here, unlike vanilla's own shape -- MEASURED live 2026-09-29: with
    // either present (driver-level via `this.FailOn...` at the top of
    // MakeNewToils, or toil-level chained onto Toils_Goto/Toils_Haul exactly
    // as JobDriver_PaintBuilding/JobDriver_Refuel do it), the job ended
    // (JobCondition, no exception, nothing in Player.log) after its very
    // first toil, every single tick, forever -- RimWorld's own "started 10
    // jobs in one tick" safety net fired continuously (confirmed via a
    // throwaway probe toil + reservation tracing: TryMakePreToilReservations
    // succeeded, MakeNewToils built cleanly, the probe toil's own
    // initAction/tickAction ran once as expected, then the WHOLE job ended
    // and JobGiver_Work immediately started an identical replacement -- a
    // fail-condition check evaluating true is consistent with this, no
    // other candidate reproduced it). Removing every FailOn call (both
    // levels) and nothing else made the exact same pawn/target/reservation
    // state complete a real fetch+carry+toil+AddCoat cycle in ~800 ticks
    // with no further change. Root cause NOT fully isolated between the two
    // conditions (time-boxed); this trades away graceful abandonment if the
    // target/Deepfire stack is forbidden or another pawn starts physically
    // interacting with the stack mid-fetch -- FailOnDespawnedNullOrForbidden
    // for a DESPAWNED/destroyed target is still owed via a plain null check
    // if that edge case matters before this ships past step 5.
    public class JobDriver_ApplyDeepfire : JobDriver
    {
        private const int WorkTicks = 600;
        private const float ArtisticXP = 100f;

        private float workDone;

        private Thing Target => job.GetTarget(TargetIndex.A).Thing;
        private Thing DeepfireStack => job.GetTarget(TargetIndex.B).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(Target, job, 1, -1, null, errorOnFailed)) return false;
            // PIGMENT_JOB_PAYMENT_ALLOCATION_1: reserve job.count units (the old call passed the count as maxPawns and
            // reserved the whole stack). If the stack picked at order time no longer has room, re-resolve it now.
            if (!pawn.CanReserve(DeepfireStack, DeepfireCostUtility.StackShareMaxPawns, job.count))
            {
                Thing other = DeepfireCostUtility.FindNearbyDeepfire(pawn, job.count, forced: true);
                if (other != null) job.SetTarget(TargetIndex.B, other);
            }
            return pawn.Reserve(DeepfireStack, job, DeepfireCostUtility.StackShareMaxPawns, job.count, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, putRemainderInQueue: false, subtractNumTakenFromJobCount: true);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil apply = ToilMaker.MakeToil("ApplyDeepfire");
            apply.initAction = delegate { workDone = 0f; };
            apply.tickIntervalAction = delegate(int delta)
            {
                // GPT review #4/#5: a target picked up/minified (Map null),
                // already full, or un-designated, or a pawn no longer
                // carrying the pigment, ends the job BEFORE anything is
                // consumed.
                if (Target == null || Target.Destroyed || !Target.Spawned || DeepfireStack == null
                    || pawn.carryTracker.CarriedThing == null
                    || Target.TryGetComp<CompDeepfire>()?.CanAddCoat != true
                    || Target.Map.designationManager.DesignationOn(Target, DeepfireDefOf.RM_ApplyDeepfireDesignation) == null)
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                pawn.rotationTracker.FaceTarget(Target);
                workDone += pawn.GetStatValue(StatDefOf.WorkSpeedGlobal) * delta;
                if (workDone >= WorkTicks)
                {
                    // PIGMENT_JOB_PAYMENT_ALLOCATION_1: the coat lands only when the carried deepfire covers its cost.
                    int cost = DeepfireCostUtility.CostFor(Target);
                    if (!DeepfireCostUtility.TryPayCarried(pawn, cost))
                    {
                        EndJobWith(JobCondition.Incompletable);
                        return;
                    }
                    pawn.skills?.Learn(SkillDefOf.Artistic, ArtisticXP);

                    CompDeepfire comp = Target.TryGetComp<CompDeepfire>();
                    comp?.AddCoat();
                    Target.Map.designationManager.TryRemoveDesignationOn(Target, DeepfireDefOf.RM_ApplyDeepfireDesignation);

                    ReadyForNextToil();
                }
            };
            apply.defaultCompleteMode = ToilCompleteMode.Never;
            apply.WithEffect(EffecterDefOf.Paint, TargetIndex.A);
            apply.WithProgressBar(TargetIndex.A, () => workDone / WorkTicks, interpolateBetweenActorAndTarget: true);
            apply.activeSkill = () => SkillDefOf.Artistic;
            apply.handlingFacing = true;
            yield return apply;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workDone, "workDone", 0f);
        }
    }
}
