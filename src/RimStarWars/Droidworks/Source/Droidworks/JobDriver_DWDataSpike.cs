using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1. The 600-tick spike job: carry the item to
    /// the target, work for WorkTicks, then Pawn.SetFaction(Faction.OfPlayer,
    /// ...) if (and only if) the target is still downed/prisoner AND the
    /// spike's faction key still matches - droid_ruling.md's own one-liner for
    /// OuterRim_DataSpike, reauthored as our own class. Shaped after
    /// JobDriver_DWClampBolt.cs's own downed-pawn-targeting job pattern
    /// (goto -> delay toil with a progress bar -> AddFinishAction), with the
    /// target-index order taken from how CompUsable.TryStartUseJob actually
    /// builds the job (TargetA = the item being used, TargetB = the picked
    /// target) - see CompTargetable_DWDataSpike.cs's header for why that lets
    /// this be one job instead of the donor mod's two.
    ///
    /// Consumable: the spike is destroyed at the end of the job regardless of
    /// outcome (spent trying, same as any single-use tool) - the donor mod's
    /// own JobDriver_ReprogramDroid never destroys its item at all, which
    /// this reauthoring treats as a gap to close, not a behavior to copy.
    /// </summary>
    public class JobDriver_DWDataSpike : JobDriver
    {
        private const TargetIndex ItemInd = TargetIndex.A;
        private const TargetIndex PawnInd = TargetIndex.B;
        private const int WorkTicks = 600;

        private Thing Item => job.GetTarget(ItemInd).Thing;
        private Pawn Target => (Pawn)job.GetTarget(PawnInd).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(Item, job, 1, -1, null, errorOnFailed) &&
            pawn.Reserve(Target, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedNullOrForbidden(ItemInd);
            this.FailOnDespawnedNullOrForbidden(PawnInd);
            this.FailOn(() => !(Target.Downed || Target.IsPrisoner));

            // DROID_DATASPIKE_SURVIVES_FAILON_1: the class header promises the
            // spike is destroyed "regardless of outcome", but a Toils_General.Do
            // as the LAST toil only runs on success - the FailOn above (target
            // rescued/healed/recaptured mid-job) ends the job from whichever toil
            // is active and that final toil never starts, leaving the spike
            // reusable for free. JobDriver.AddFinishAction (a "global" finish
            // action, distinct from a per-toil Toil.AddFinishAction) fires on
            // every job end regardless of which toil was current, so registering
            // the destroy here actually delivers the documented contract.
            this.AddFinishAction(delegate { Item?.Destroy(); });

            // Fixed (code review): the faction-flip effect was
            // spike.AddFinishAction (per-TOIL) - fires whenever the toil ends
            // for ANY reason, per-toil Cleanup being unconditional on why the
            // toil ended (same DROID_DATASPIKE_SURVIVES_FAILON_1 mechanism
            // this file's own header already reasons through for the item
            // destroy above, just not applied here too). That let an
            // interrupted/cancelled spike job still flip the target's faction
            // after far less than the documented 600 ticks of "spiking".
            // Moved to the job-level, JobCondition-aware AddFinishAction so it
            // only fires once the delay toil actually completes.
            this.AddFinishAction(delegate (JobCondition jobCondition)
            {
                if (jobCondition != JobCondition.Succeeded) return;
                Pawn target = Target;
                if (target == null || target.Dead) return;
                if (!(target.Downed || target.IsPrisoner)) return;

                CompDWDataSpike comp = Item?.TryGetComp<CompDWDataSpike>();
                if (comp == null || !comp.MatchesFaction(target)) return;

                target.SetFaction(Faction.OfPlayer, pawn);
            });

            yield return Toils_Goto.GotoThing(ItemInd, PathEndMode.Touch);
            yield return Toils_Haul.StartCarryThing(ItemInd);
            yield return Toils_Goto.GotoThing(PawnInd, PathEndMode.Touch);

            Toil spike = ToilMaker.MakeToil("DWDataSpike");
            spike.defaultCompleteMode = ToilCompleteMode.Delay;
            spike.defaultDuration = WorkTicks;
            spike.WithProgressBarToilDelay(PawnInd);
            yield return spike;
        }
    }
}
