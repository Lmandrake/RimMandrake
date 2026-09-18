using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S2 build pass — the JobDriver half of the WorkGiver/
    // JobDriver pair that closes RM_CompWorkedLottery's own "compiles, never
    // called" gap (see RM_WorkGiver_WorkLottery.cs's own header). Toil shape
    // cribbed verbatim from RimWorld/JobDriver_OperateDeepDrill.cs (read via
    // RimSage this pass): one never-completing work toil driven by
    // tickIntervalAction, generic here on RM_CompWorkedLottery instead of
    // CompDeepDrill, feeding AddWork() with RimWorld's own MiningSpeed stat —
    // the same stat vanilla mining/drilling already scales by, no new StatDef
    // needed.
    public class RM_JobDriver_WorkLottery : JobDriver
    {
        private RM_CompWorkedLottery Comp => job.targetA.Thing?.TryGetComp<RM_CompWorkedLottery>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOnBurningImmobile(TargetIndex.A);
            this.FailOn(() => Comp == null || Comp.Props?.table == null);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil work = ToilMaker.MakeToil("MakeNewToils");
            work.tickIntervalAction = delegate(int delta)
            {
                Pawn actor = work.actor;
                RM_CompWorkedLottery comp = Comp;
                if (comp == null)
                {
                    return;
                }
                comp.AddWork(actor.GetStatValue(StatDefOf.MiningSpeed) * (float)delta, actor);
                actor.skills?.Learn(SkillDefOf.Mining, 0.065f * (float)delta);
            };
            // Once a completed portion rolls a trap row, the fuse resolves on
            // its own CompTick regardless of this job — pulling the worker off
            // here (rather than leaving them standing over an armed trap) is
            // the one piece of "you learn not to dig past the click you were
            // warned about" this driver can enforce without the disarm UI
            // (owner card 2, TryDisarmPendingTrap) owed to a future pass.
            work.FailOn(() => Comp?.TrapArmed ?? false);
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.WithEffect(EffecterDefOf.Drill, TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            work.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            work.activeSkill = () => SkillDefOf.Mining;
            yield return work;
        }
    }
}
