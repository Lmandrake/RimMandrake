using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Walks the actor up to the amoeba host
    // and spends a short toil "injecting" — modeled on the goto/wait shape
    // JobDriver_InteractAnimal (Source/RimWorld/JobDriver_InteractAnimal.cs,
    // read via RimSage) uses for every other live-animal interaction, rather
    // than firing instantly on click. The host is a wild, potentially
    // dangerous Contagion creature (the_contagion.md: "they can become
    // dangerous"), so requiring the actor to actually close distance and
    // stand there is the correct shape, not a corner cut.
    public class JobDriver_RM_InjectGenomeSample : JobDriver
    {
        private const int InjectDurationTicks = 180;

        private Pawn Host => (Pawn)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Host, job, 1, -1, null, errorOnFailed);
        }

        public override void ExposeData()
        {
            base.ExposeData();
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOnDowned(TargetIndex.A);
            this.FailOn(() => !AmoebaHostUtility.IsEligibleHost(Host));
            this.FailOn(() => !pawn.inventory.innerContainer.Any(t => t.def == RM_ContagionDefOf.RM_GenomeSample));

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_Interpersonal.WaitToBeAbleToInteract(pawn);
            yield return Toils_Interpersonal.GotoInteractablePosition(TargetIndex.A);

            Toil inject = ToilMaker.MakeToil("InjectGenomeSample");
            inject.defaultCompleteMode = ToilCompleteMode.Delay;
            inject.defaultDuration = InjectDurationTicks;
            inject.WithProgressBarToilDelay(TargetIndex.A);
            inject.AddFinishAction(delegate
            {
                Thing sample = pawn.inventory.innerContainer.FirstOrDefault(t => t.def == RM_ContagionDefOf.RM_GenomeSample);
                if (sample == null)
                {
                    return;
                }
                CompGenomeSample comp = sample.TryGetComp<CompGenomeSample>();
                int sourceID = comp?.sourcePawnID ?? -1;
                string sourceName = (comp != null && !comp.sourcePawnName.NullOrEmpty()) ? comp.sourcePawnName : "unknown";

                if (AmoebaHostUtility.TryBeginGestation(Host, sourceID, sourceName))
                {
                    pawn.inventory.innerContainer.Remove(sample);
                    sample.Destroy();
                }
            });
            yield return inject;
        }
    }
}
