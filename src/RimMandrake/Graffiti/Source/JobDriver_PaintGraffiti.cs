using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_FRAMEWORK_BUILD_1's absorbed spree mechanic. Owner ruling,
    // 2026-08-31: "SUPERSEDE NOW... we absorb the vandal-spree mechanic
    // into our own framework C#". Vanilla models: JobDriver_RelaxAlone (joy
    // gain over a stay) and JobDriver_Floordrawing (filth made while ticking,
    // never on interruption).
    //
    // A job is a sitting at a wall. The painter walks onto the floor cell, faces
    // the wall and works on ONE chosen mark for as long as its form takes (a scrawl
    // is seconds, a piece is an afternoon); interrupted, nothing is left. Then a
    // spree or a joy sitting moves down the wall to the next bare stretch. The first
    // version stood on one cell for 8000 ticks and repainted it every 250, each new
    // mark erasing the last, so a whole spree left 3 to 6 marks and a colony could
    // never look written on.
    public class JobDriver_PaintGraffiti : JobDriver
    {
        private const TargetIndex MarkCellInd = TargetIndex.A;
        private const int ProgressPuffInterval = 45;

        private ThingDef markDef;
        private int paintTotal;
        private int paintLeft;
        private int marksThisSitting;
        private Pawn subject;
        private Faction targetFaction;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref markDef, "rmMarkDef");
            Scribe_Values.Look(ref paintTotal, "rmPaintTotal");
            Scribe_Values.Look(ref paintLeft, "rmPaintLeft");
            Scribe_Values.Look(ref marksThisSitting, "rmMarksThisSitting");
            Scribe_References.Look(ref subject, "rmPaintSubject");
            Scribe_References.Look(ref targetFaction, "rmPaintTargetFaction");
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(MarkCellInd), job, errorOnFailed: errorOnFailed);
        }

        /// <summary>Someone this job answers, painting back at them (JobGiver_AnswerMark): a single mark, not a sitting.</summary>
        private Pawn ReplyTo => job.GetTarget(TargetIndex.B).Thing as Pawn;

        public override string GetReport()
        {
            if (subject != null && markDef != null)
            {
                RM_Meaning meaning = markDef.GetModExtension<ModExtension_Graffiti>()?.meaning ?? RM_Meaning.None;
                if (meaning == RM_Meaning.Mockery) return "painting a mockery of " + subject.LabelShort + ".";
                if (meaning == RM_Meaning.Tribute) return "painting a tribute to " + subject.LabelShort + ".";
                if (meaning == RM_Meaning.Memorial) return "painting a memorial to " + subject.LabelShort + ".";
            }
            return base.GetReport();
        }

        private bool Designated(IntVec3 cell) => Map.designationManager.DesignationAt(cell, RMGraffitiDefOf.RM_PaintGraffitiHere) != null;

        private void FaceWall(IntVec3 cell)
        {
            int side = Filth_Mark.ReadWallSide(cell, Map);
            pawn.rotationTracker.FaceCell(side == RM_GraffitiKernel.NoWall ? cell : cell + new Rot4(side).FacingCell);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(MarkCellInd);

            Toil walk = Toils_Goto.GotoCell(MarkCellInd, PathEndMode.OnCell);
            yield return walk;

            Toil paint = ToilMaker.MakeToil("MakeNewToils");
            paint.defaultCompleteMode = ToilCompleteMode.Never;
            paint.handlingFacing = true;
            paint.initAction = delegate
            {
                IntVec3 cell = job.GetTarget(MarkCellInd).Cell;
                FaceWall(cell);
                if (paintLeft > 0 && markDef != null)
                {
                    return;     // resumed from a save
                }
                markDef = ChooseMark(cell);
                if (markDef == null)
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                paintTotal = paintLeft = RM_GraffitiKernel.PaintTicks(
                    markDef.GetModExtension<ModExtension_Graffiti>()?.form ?? GraffitiForm.Scrawl,
                    RM_GraffitiSettings.paintIntervalTicks);
            };
            paint.AddPreTickIntervalAction(delegate(int delta)
            {
                IntVec3 cell = job.GetTarget(MarkCellInd).Cell;
                FaceWall(cell);
                JoyUtility.JoyTickCheckEnd(pawn, delta, JoyTickFullJoyAction.None);
                if (pawn.CurJob != job)
                {
                    return;
                }
                if (pawn.IsHashIntervalTick(ProgressPuffInterval, delta))
                {
                    SprayPuff(cell);
                }
                paintLeft -= delta;
                if (paintLeft <= 0)
                {
                    FinishMark(cell, walk);
                }
            });
            paint.WithProgressBar(MarkCellInd, () => paintTotal <= 0 ? 0f : 1f - (float)paintLeft / paintTotal);
            yield return paint;
        }

        /// <summary>The mark for this stretch of wall: the player's order if this hand may paint it, else the pool's pick, never
        /// wider than the wall has room for. A job from the work giver whose order was cancelled paints nothing (GPT deep
        /// review 2026-10-22 #8).</summary>
        private ThingDef ChooseMark(IntVec3 cell)
        {
            float room = GraffitiJobUtility.WallRoom(cell, Map);
            subject = null;
            targetFaction = null;
            if (!Designated(cell))
            {
                if (job.workGiverDef != null)
                {
                    return null;
                }
                if (ReplyTo != null)
                {
                    // An answer in paint may go over what it answers: that's the point of it.
                    subject = ReplyTo;
                    return GraffitiPool.WidthOf(RMGraffitiDefOf.RM_Graffiti_Mockery) <= room ? RMGraffitiDefOf.RM_Graffiti_Mockery : null;
                }
                // Owner's pick, 2026-11-07: measure a mark's real width before painting, so nobody erases a neighbour by accident. A spree
                // has no such manners: going over is what it's for.
                if (!pawn.InMentalState) room = System.Math.Min(room, GraffitiJobUtility.BareRoom(cell, Map));
                ThingDef said = GraffitiSocial.SocialMark(pawn, pawn.InMentalState, room, out subject);
                if (said != null) return said;
                return pawn.InMentalState ? GraffitiPool.PickForSpree(pawn, room, cell) : GraffitiPool.PickForJoy(pawn, room, cell);
            }
            MapComponent_GraffitiOrders orders = MapComponent_GraffitiOrders.For(Map);
            ThingDef ordered = orders?.OrderAt(cell);
            if (ordered != null && GraffitiPool.PainterMayPaint(ordered, pawn) && GraffitiPool.WidthOf(ordered) <= room + 0.3f)
            {
                subject = orders.SubjectAt(cell);
                targetFaction = orders.FactionAt(cell);
                return ordered;
            }
            return GraffitiPool.PickForDesignator(pawn, room, cell);
        }

        private void FinishMark(IntVec3 cell, Toil walk)
        {
            bool designated = Designated(cell);
            if (!designated && job.workGiverDef != null)
            {
                EndJobWith(JobCondition.Incompletable);
                return;
            }
            Filth_Mark made = Filth_Mark.MakeMark(cell, Map, markDef, pawn, subject, targetFaction, ordered: designated);
            markDef = null;
            subject = null;
            targetFaction = null;
            paintLeft = paintTotal = 0;
            if (designated)
            {
                if (made == null)
                {
                    // GPT deep review 2026-10-22 #6: nothing was painted; keep the order for another try
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                // A designated job is one mark, not a sitting.
                Map.designationManager.TryRemoveDesignation(cell, RMGraffitiDefOf.RM_PaintGraffitiHere);
                MapComponent_GraffitiOrders.For(Map)?.Clear(cell);
                EndJobWith(JobCondition.Succeeded);
                return;
            }
            if (ReplyTo != null)
            {
                if (made != null) MapComponent_GraffitiSocial.For(Map)?.Answered(pawn, null, ReplyTo);
                EndJobWith(made != null ? JobCondition.Succeeded : JobCondition.Incompletable);
                return;
            }
            marksThisSitting++;
            if (!RM_GraffitiKernel.SittingContinues(marksThisSitting, pawn.InMentalState, pawn.needs?.joy?.CurLevelPercentage ?? 1f)
                || !GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 next, roomCap: !pawn.InMentalState)
                || !pawn.CanReserve(next))
            {
                EndJobWith(JobCondition.Succeeded);
                return;
            }
            Map.reservationManager.Release(cell, pawn, job);
            pawn.Reserve(next, job, errorOnFailed: false);
            job.SetTarget(MarkCellInd, next);
            JumpToToil(walk);
        }

        private void SprayPuff(IntVec3 cell)
        {
            Vector3 at = cell.ToVector3Shifted();
            int side = Filth_Mark.ReadWallSide(cell, Map);
            if (side != RM_GraffitiKernel.NoWall)
            {
                at += new Rot4(side).FacingCell.ToVector3() * 0.6f;
            }
            Color tint = markDef?.GetModExtension<ModExtension_Graffiti>()?.form == GraffitiForm.Paste
                ? new Color(0.85f, 0.8f, 0.68f, 0.5f)
                : new Color(0.75f, 0.75f, 0.75f, 0.45f);
            FleckMaker.ThrowDustPuffThick(at, Map, 0.55f, tint);
        }
    }
}
