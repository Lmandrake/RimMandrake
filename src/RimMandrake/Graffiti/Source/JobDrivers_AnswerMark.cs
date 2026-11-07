using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // What a pawn does about a mark (RM_GraffitiKernel.AnswerOf). Think tree: Humanlike_PreMain, so a grudge is seen to at the pawn's next
    // free moment, but it never interrupts a job and it waits for someone starving or collapsing.
    public class JobGiver_AnswerMark : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_GraffitiSettings.socialEnabled || pawn.Map == null || pawn.Downed) return null;
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(pawn.Map);
            RM_Grudge grudge = comp?.GrudgeOf(pawn);
            if (grudge == null) return null;
            if (pawn.needs?.food?.Starving == true || pawn.needs?.rest?.CurCategory == RestCategory.Exhausted) return null;
            Job job = null;
            switch (grudge.answer)
            {
                case RM_Answer.Scrub:
                case RM_Answer.Deface:
                    if (pawn.CanReserveAndReach(grudge.mark.Position, PathEndMode.OnCell, Danger.Some))
                    {
                        job = JobMaker.MakeJob(grudge.answer == RM_Answer.Scrub ? RMGraffitiDefOf.RM_ScrubMark : RMGraffitiDefOf.RM_DefaceMark, grudge.mark, grudge.mark.Position);
                    }
                    break;
                case RM_Answer.Reply:
                    if (GraffitiJobUtility.TryFindReplyCell(pawn, grudge.mark != null && !grudge.mark.Destroyed ? grudge.mark.Position : pawn.Position, out IntVec3 cell))
                    {
                        job = JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, cell, grudge.against);
                    }
                    break;
                case RM_Answer.Confront:
                    if (pawn.CanReach(grudge.against, PathEndMode.Touch, Danger.Some))
                    {
                        job = JobMaker.MakeJob(RMGraffitiDefOf.RM_ConfrontPainter, grudge.against);
                    }
                    break;
            }
            comp.Settle(grudge);
            return job;
        }
    }

    /// <summary>Stand at the mark and wipe it off, or take a brush and cross it out. Either way it's a statement.</summary>
    public abstract class JobDriver_AnswerMarkBase : JobDriver
    {
        protected const TargetIndex MarkInd = TargetIndex.A, CellInd = TargetIndex.B;
        protected abstract int WorkTicks { get; }
        protected abstract void Finish(Filth_Mark mark);
        protected Filth_Mark Mark => job.GetTarget(MarkInd).Thing as Filth_Mark;

        private int left;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref left, "rmAnswerLeft");
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(CellInd), job, errorOnFailed: errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(MarkInd);
            yield return Toils_Goto.GotoCell(CellInd, PathEndMode.OnCell);
            Toil work = ToilMaker.MakeToil("MakeNewToils");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.handlingFacing = true;
            work.initAction = delegate { left = WorkTicks; };
            work.AddPreTickIntervalAction(delegate(int delta)
            {
                Filth_Mark mark = Mark;
                if (mark == null || mark.Destroyed)
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                pawn.rotationTracker.FaceCell(mark.Position + new Rot4(mark.wallSide < 0 ? 0 : mark.wallSide).FacingCell);
                left -= delta;
                if (left <= 0)
                {
                    Finish(mark);
                    EndJobWith(JobCondition.Succeeded);
                }
            });
            work.WithProgressBar(MarkInd, () => 1f - (float)left / WorkTicks);
            yield return work;
        }
    }

    public class JobDriver_ScrubMark : JobDriver_AnswerMarkBase
    {
        protected override int WorkTicks => 420;

        protected override void Finish(Filth_Mark mark)
        {
            mark.SkipCleanNotice();
            GraffitiSocial.Notify_Answered(mark, pawn, crossedOut: false);
            mark.Destroy();
        }

        public override string GetReport()
        {
            Filth_Mark m = Mark;
            return m?.maker != null && m.maker != pawn ? "scrubbing " + m.maker.LabelShort + "'s mark off the wall." : base.GetReport();
        }
    }

    public class JobDriver_DefaceMark : JobDriver_AnswerMarkBase
    {
        protected override int WorkTicks => 300;

        protected override void Finish(Filth_Mark mark)
        {
            mark.CrossOut(pawn);
            GraffitiSocial.Notify_Answered(mark, pawn, crossedOut: true);
        }

        public override string GetReport()
        {
            Filth_Mark m = Mark;
            return m?.maker != null && m.maker != pawn ? "crossing out " + m.maker.LabelShort + "'s mark." : base.GetReport();
        }
    }

    /// <summary>Walk up to whoever painted it and have it out. The fight's chance is the game's own: traits, opinion, age, the lot.</summary>
    public class JobDriver_ConfrontPainter : JobDriver
    {
        private Pawn Painter => (Pawn)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) { return true; }

        public override string GetReport()
        {
            return Painter != null ? "going to have it out with " + Painter.LabelShort + "." : base.GetReport();
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => Painter.Downed || Painter.InMentalState);
            yield return Toils_Interpersonal.GotoInteractablePosition(TargetIndex.A);
            yield return Toils_Interpersonal.WaitToBeAbleToInteract(pawn);
            Toil confront = ToilMaker.MakeToil("MakeNewToils");
            confront.initAction = delegate
            {
                if (pawn.interactions.TryInteractWith(Painter, RMGraffitiDefOf.RM_Graffiti_Confront))
                {
                    GraffitiSocial.Notify_Confronted(pawn, Painter);
                }
            };
            confront.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return confront;
        }
    }
}
