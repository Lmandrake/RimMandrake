using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 owner card 2's own disarm attempt (see
    // RM_WorkGiver_DisarmLotteryTrap.cs's own header for the full design
    // rationale). One short toil at the interaction cell, then a single
    // deterministic call into RM_CompWorkedLottery.TryDisarmPendingTrap —
    // the comp's own skill gate decides Disarmed vs Detonated.
    // "Failure detonates" is not a separate damage roll this driver
    // invents: TryDisarmPendingTrap already calls the comp's own
    // Detonate() (GenExplosion.DoExplosion, the same call every trap row
    // uses) on failure, with this pawn standing at the interaction cell —
    // point-blank range is the consequence the ruling names.
    public class RM_JobDriver_DisarmLotteryTrap : JobDriver
    {
        private const TargetIndex TrapInd = TargetIndex.A;

        private RM_CompWorkedLottery Comp => job.GetTarget(TrapInd).Thing?.TryGetComp<RM_CompWorkedLottery>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TrapInd), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TrapInd);
            // If the fuse already resolved itself (timed out, or someone
            // else disarmed/triggered it) before this pawn arrives, there is
            // nothing left to attempt — end quietly rather than walking up
            // to a dead trap.
            this.FailOn(() => Comp == null || !Comp.TrapArmed);

            yield return Toils_Goto.GotoThing(TrapInd, PathEndMode.InteractionCell);

            Toil attempt = ToilMaker.MakeToil("MakeNewToils");
            attempt.initAction = delegate
            {
                RM_CompWorkedLottery comp = Comp;
                comp?.TryDisarmPendingTrap(pawn, SkillDefOf.Mining, comp.Props.disarmSkillThreshold);
                // Disarmed or Detonated, the comp's own state is already
                // resolved synchronously (fuse cleared, or Detonate()
                // already fired) — nothing further for this toil to wait
                // on. A NoTrapArmed result can't reach here: the FailOn
                // above already ended the job if the trap stopped being
                // armed before this toil ran.
            };
            attempt.defaultCompleteMode = ToilCompleteMode.Instant;
            attempt.activeSkill = () => SkillDefOf.Mining;
            yield return attempt;
        }
    }
}
