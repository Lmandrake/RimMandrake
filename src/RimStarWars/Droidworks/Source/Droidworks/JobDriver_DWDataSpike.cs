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

            yield return Toils_Goto.GotoThing(ItemInd, PathEndMode.Touch);
            yield return Toils_Haul.StartCarryThing(ItemInd);
            yield return Toils_Goto.GotoThing(PawnInd, PathEndMode.Touch);

            Toil spike = ToilMaker.MakeToil("DWDataSpike");
            spike.defaultCompleteMode = ToilCompleteMode.Delay;
            spike.defaultDuration = WorkTicks;
            spike.WithProgressBarToilDelay(PawnInd);
            spike.AddFinishAction(delegate
            {
                Pawn target = Target;
                if (target == null || target.Dead) return;
                if (!(target.Downed || target.IsPrisoner)) return;

                CompDWDataSpike comp = Item?.TryGetComp<CompDWDataSpike>();
                if (comp == null || !comp.MatchesFaction(target)) return;

                target.SetFaction(Faction.OfPlayer, pawn);
            });
            yield return spike;

            yield return Toils_General.Do(delegate
            {
                Item?.Destroy();
            });
        }
    }
}
