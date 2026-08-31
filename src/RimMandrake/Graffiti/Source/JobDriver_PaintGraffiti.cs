using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_FRAMEWORK_BUILD_1's absorbed spree mechanic. Owner ruling,
    // 2026-08-31: "SUPERSEDE NOW... we absorb the vandal-spree mechanic
    // into our own framework C# and RETIRE Mlie.GraffitiMod from the mod
    // list at build time." Mlie.GraffitiMod's own JobDriver_PaintGraffiti
    // is compiled-only (no shipped source) - this is a fresh implementation
    // against the real vanilla toil API, modeled on two verified vanilla
    // analogs (not guessed): JobDriver_RelaxAlone (Source/RimWorld/
    // JobDriver_RelaxAlone.cs) for the goto-and-gain-Joy-for-joyDuration
    // shape, and JobDriver_Floordrawing (same folder) for the
    // FilthMaker.TryMakeFilth-on-completion shape.
    public class JobDriver_PaintGraffiti : JobDriver
    {
        private const TargetIndex MarkCellInd = TargetIndex.A;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(MarkCellInd), job, errorOnFailed: errorOnFailed);
        }

        protected override System.Collections.Generic.IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(MarkCellInd);

            yield return Toils_Goto.GotoCell(MarkCellInd, PathEndMode.Touch);

            Toil paint = ToilMaker.MakeToil("MakeNewToils");
            paint.defaultCompleteMode = ToilCompleteMode.Delay;
            paint.defaultDuration = job.def.joyDuration;
            paint.handlingFacing = true;
            paint.initAction = delegate
            {
                pawn.rotationTracker.FaceCell(job.GetTarget(MarkCellInd).Cell);
            };
            paint.AddPreTickIntervalAction(delegate(int delta)
            {
                pawn.rotationTracker.FaceCell(job.GetTarget(MarkCellInd).Cell);
                JoyUtility.JoyTickCheckEnd(pawn, delta);
            });
            paint.AddFinishAction(delegate
            {
                IntVec3 cell = job.GetTarget(MarkCellInd).Cell;
                if (cell.IsValid && Map != null)
                {
                    FilthMaker.TryMakeFilth(cell, Map, RMGraffitiDefOf.RM_Graffiti_Vandal);
                }
            });
            yield return paint;
        }
    }
}
