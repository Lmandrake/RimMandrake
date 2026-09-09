using System.Collections.Generic;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.AnimalTheft
{
    /// <summary>
    /// RIMPROPERTY_ANIMAL_THEFT_1's shared driver for both theft routes —
    /// JobGiver_RM_TrainedSteal (trained pet) and JobGiver_RM_WildSteal
    /// (wild animal) both construct the SAME AnimalTheftDefOf.RM_AnimalSteal
    /// job against a Thing found by AnimalTheftUtility.FindStealTarget; this
    /// driver doesn't care which route dispatched it.
    ///
    /// Mirrors TheftHauler/JobDriver_TheftHaulUninstall's own pattern:
    /// PropertyEngine.Fire's TakingEvent(Act=Take) fires at the moment of
    /// taking — BEFORE the carry actually starts — and unconditionally
    /// (Fire resolves the prior claim and authorization itself; an
    /// own-claim or unclaimed item is a no-op inside it, so there is
    /// nothing to pre-check out here).
    ///
    /// Three toils: goto the item, take it (fire the event, then
    /// carryTracker.TryStartCarry), wander a short distance with it
    /// (CellFinder.RandomClosewalkCellNear — same "walk it off and stash
    /// it" flavor for both a raccoon and a trained pet), then drop it
    /// (Toils_Haul.DropCarriedThing, same toil vanilla's own
    /// JobDriver_PlayGoldenCube ends on).
    /// </summary>
    public class JobDriver_RM_AnimalSteal : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // stackCount -1 = reserve the whole stack, matching the take toil below
            // (TryStartCarry(target, target.stackCount, ...) always takes the FULL
            // stack, never just one unit). A hardcoded stackCount of 1 here would
            // under-reserve any target with stackCount > 1, letting another pawn's
            // job reserve the remaining units of the same Thing while this pawn is
            // still pathing to it. Matches JobDriver_RemoveBuilding's own base
            // TryMakePreToilReservations (stackCount -1) and vanilla's
            // JobDriver_HaulToCell.
            return pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);

            Toil takeToil = ToilMaker.MakeToil("TakeAndFireTakingEvent");
            takeToil.initAction = delegate
            {
                Thing target = TargetThingA;
                if (target == null)
                {
                    pawn.jobs.EndCurrentJob(JobCondition.Incompletable);
                    return;
                }

                // At the moment of taking, not haul-pickup — same ordering
                // JobDriver_TheftHaulUninstall.FinishedRemoving documents.
                PropertyEngine.Fire(new TakingEvent(target, ClaimantRef.OfPawn(pawn),
                    TakingAct.Take, Find.TickManager.TicksGame));

                int taken = pawn.carryTracker.TryStartCarry(target, target.stackCount, reserve: true);
                if (taken <= 0)
                {
                    pawn.jobs.EndCurrentJob(JobCondition.Incompletable);
                }
            };
            takeToil.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return takeToil;

            Toil wanderOff = ToilMaker.MakeToil("WanderOffWithLoot");
            wanderOff.initAction = delegate
            {
                IntVec3 dest = CellFinder.RandomClosewalkCellNear(
                    pawn.Position, pawn.Map, PropertyTuning.AnimalTheftWanderRadius);
                job.SetTarget(TargetIndex.B, dest);
                pawn.pather.StartPath(dest, PathEndMode.OnCell);
            };
            wanderOff.defaultCompleteMode = ToilCompleteMode.PatherArrival;
            yield return wanderOff;

            yield return Toils_Haul.DropCarriedThing();
        }
    }
}
