using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_BOLT_PAYOFF_1 (packet B5): "un-bolt-each-other job" - the
    /// field REMOVAL counterpart to JobDriver_DWClampBolt.cs. No Downed gate
    /// (unlike clamping-ON, which needs the target subdued; taking one off is
    /// cooperative, not coercive) and no violation flag - matches the
    /// codebase's own "field route, no bill, no ingredient" precedent
    /// (JobDriver_DWClampBolt's own header). Deliberately does NOT touch
    /// RSW_DW_BoltResentment (same as Recipe_RemoveRestrainingBolt.cs) and
    /// does NOT roll the rebellion check that recipe has - the field route is
    /// a quieter, quicker un-bolting, not the deliberate shop procedure;
    /// FOUNDRY's own scope call, recorded in the item file.
    ///
    /// Wiring a WorkGiver/float-menu option to actually ISSUE this job is
    /// left as follow-up, same as JobDriver_DWClampBolt.cs's own precedent -
    /// the driver is correct and safe to invoke either way.
    /// </summary>
    public class JobDriver_DWUnclampBolt : JobDriver
    {
        private const TargetIndex TargetInd = TargetIndex.A;
        private const int WorkTicks = 300;

        private Pawn Target => (Pawn)job.GetTarget(TargetInd).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(Target, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetInd);
            this.FailOn(() => !Target.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_RestrainingBolt));

            this.AddFinishAction(delegate (JobCondition jobCondition)
            {
                if (jobCondition != JobCondition.Succeeded) return;
                Pawn target = Target;
                if (target == null || target.Dead) return;
                Hediff h = target.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_RestrainingBolt);
                if (h != null) target.health.RemoveHediff(h);
            });

            yield return Toils_Goto.GotoThing(TargetInd, PathEndMode.Touch);

            Toil unclamp = ToilMaker.MakeToil("UnclampBolt");
            unclamp.defaultCompleteMode = ToilCompleteMode.Delay;
            unclamp.defaultDuration = WorkTicks;
            unclamp.WithProgressBarToilDelay(TargetInd);
            yield return unclamp;
        }
    }
}
