using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_GPT_ENRICHMENT_1, part 1: Draftprints. Walk to touch range of
    // a living Unfinished, stand there scanning, then drop a recorded
    // RM_Draftprint at the sampler's feet. The goto/wait shape is
    // JobDriver_RM_InjectGenomeSample's. The risk is real: the target is not
    // reserved against fighting back, and a conscious one may go manhunter
    // at the end of the scan (DraftprintUtility.MaybeProvoke).
    public class JobDriver_RM_SampleDraftprint : JobDriver
    {
        private const int ScanDurationTicks = 240;

        private Pawn Target => (Pawn)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Target, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_ContagionSettings.draftprintsEnabled);
            this.FailOn(() => !DraftprintUtility.CanBeSampled(Target));

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil scan = ToilMaker.MakeToil("ScanUnfinished");
            scan.defaultCompleteMode = ToilCompleteMode.Delay;
            scan.defaultDuration = ScanDurationTicks;
            scan.WithProgressBarToilDelay(TargetIndex.A);
            scan.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            scan.handlingFacing = true;
            scan.tickAction = delegate
            {
                pawn.rotationTracker.FaceTarget(Target);
            };
            yield return scan;

            Toil finish = ToilMaker.MakeToil("RecordDraftprint");
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            finish.initAction = delegate
            {
                Pawn target = Target;
                if (!DraftprintUtility.CanBeSampled(target))
                {
                    return;
                }
                Thing print = ThingMaker.MakeThing(RM_ContagionDefOf.RM_Draftprint);
                DraftprintUtility.Record(target, print);
                GenPlace.TryPlaceThing(print, pawn.Position, pawn.Map, ThingPlaceMode.Near);
                Messages.Message(
                    pawn.LabelShort.CapitalizeFirst() + " took a draftprint of " + target.LabelShort + ".",
                    print, MessageTypeDefOf.PositiveEvent, historical: false);
                DraftprintUtility.MaybeProvoke(target, pawn);
            };
            yield return finish;
        }
    }
}
