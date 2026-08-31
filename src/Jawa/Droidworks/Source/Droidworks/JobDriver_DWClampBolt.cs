using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// The field route for fitting a restraining bolt: a 600-tick job on a
    /// DOWNED droid, no surgery bill, no violation flag, no anesthetic -
    /// mirrors OuterRim_RestrainDroid's own JobDriver_RestrainDroid.Restrain()
    /// (droid_ruling.md section 3: "Downed droid -> JobDriver_RestrainDroid...
    /// calls pawn.health.AddHediff(...) directly - no droid check, no
    /// violation, no goodwill"). Gated purely on Target.Downed - the same
    /// style of boolean gate Recipe_RebootDroid.cs uses for its own
    /// downed-pawn eligibility, just expressed as a job FailOn instead of a
    /// recipe GetPartsToApplyOn.
    ///
    /// v0 SIMPLIFICATION, same precedent Recipe_RebootDroid.cs already set
    /// for this codebase: no ingredient consumed here. RSW_DW_RestrainingBoltItem
    /// still exists as the surgery route's crafted ingredient and as a
    /// general economy piece - "outside help, no formal bill" is the whole
    /// point of a field verb, and wiring a WorkGiver/float-menu option that
    /// hauls one first is left as follow-up (the job driver itself is
    /// correct and safe to invoke either way).
    ///
    /// Shaped like JobDriver_DWRecharge's goto-then-tick pattern.
    /// </summary>
    public class JobDriver_DWClampBolt : JobDriver
    {
        private const TargetIndex TargetInd = TargetIndex.A;
        private const int WorkTicks = 600;

        private Pawn Target => (Pawn)job.GetTarget(TargetInd).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(Target, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetInd);
            this.FailOn(() => !Target.Downed);

            yield return Toils_Goto.GotoThing(TargetInd, PathEndMode.Touch);

            Toil clamp = ToilMaker.MakeToil("ClampBolt");
            clamp.defaultCompleteMode = ToilCompleteMode.Delay;
            clamp.defaultDuration = WorkTicks;
            clamp.WithProgressBarToilDelay(TargetInd);
            clamp.AddFinishAction(delegate
            {
                Pawn target = Target;
                if (target == null || target.Dead) return;
                if (!target.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_RestrainingBolt))
                {
                    target.health.AddHediff(DroidworksDefOf.RSW_DW_RestrainingBolt);
                }
                DroidworksBoltUtility.EnsureBoltResentment(target);
            });
            yield return clamp;
        }
    }
}
