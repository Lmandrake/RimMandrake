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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref markDef, "rmMarkDef");
            Scribe_Values.Look(ref paintTotal, "rmPaintTotal");
            Scribe_Values.Look(ref paintLeft, "rmPaintLeft");
            Scribe_Values.Look(ref marksThisSitting, "rmMarksThisSitting");
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(MarkCellInd), job, errorOnFailed: errorOnFailed);
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
            if (!Designated(cell))
            {
                if (job.workGiverDef != null)
                {
                    return null;
                }
                return pawn.InMentalState ? GraffitiPool.PickForSpree(pawn, room) : GraffitiPool.PickForJoy(pawn, room);
            }
            ThingDef ordered = MapComponent_GraffitiOrders.For(Map)?.OrderAt(cell);
            return ordered != null && GraffitiPool.PainterMayPaint(ordered, pawn) && GraffitiPool.WidthOf(ordered) <= room
                ? ordered
                : GraffitiPool.PickForDesignator(pawn, room);
        }

        private void FinishMark(IntVec3 cell, Toil walk)
        {
            bool designated = Designated(cell);
            if (!designated && job.workGiverDef != null)
            {
                EndJobWith(JobCondition.Incompletable);
                return;
            }
            Filth_Mark made = Filth_Mark.MakeMark(cell, Map, markDef, pawn);
            markDef = null;
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
            marksThisSitting++;
            if (!RM_GraffitiKernel.SittingContinues(marksThisSitting, pawn.InMentalState, pawn.needs?.joy?.CurLevelPercentage ?? 1f)
                || !GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 next)
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
