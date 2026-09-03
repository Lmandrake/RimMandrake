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

        // Fixed 2026-09-02 (opus code review), both against verified vanilla
        // behavior:
        //
        // 1. AddFinishAction runs on Toil.Cleanup UNCONDITIONALLY - drafting the
        //    pawn, a cancel, a downing, or a new mental break one tick after
        //    arrival all fired the paint, not just real completion. Moved the
        //    FilthMaker call into a periodic tickIntervalAction instead, the
        //    exact shape JobDriver_Floordrawing (the model this file's header
        //    already claims to follow) actually uses: it paints only if it's
        //    still actively ticking the toil, repeatedly, never on interruption.
        //
        // 2. JoyTickCheckEnd's default fullJoyAction=EndJob calls
        //    EndJobWith(Succeeded) the instant joy crosses 0.9999 - one paint
        //    job's worth of gain (joyGainRate * 0.36 / 2500 per tick) fills the
        //    bar in ~1 tick's rate math well before defaultDuration elapses, so
        //    the ThinkTree immediately re-hands the pawn the same job: a
        //    per-tick goto+paint+pathfind churn for the whole 25000-45000 tick
        //    spree. fullJoyAction=None lets the toil run its full
        //    defaultDuration instead, painting periodically the whole time.
        private const int PaintIntervalTicks = 250;

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
                JoyUtility.JoyTickCheckEnd(pawn, delta, JoyTickFullJoyAction.None);
                if (pawn.IsHashIntervalTick(PaintIntervalTicks, delta))
                {
                    IntVec3 cell = job.GetTarget(MarkCellInd).Cell;
                    if (cell.IsValid && Map != null)
                    {
                        FilthMaker.TryMakeFilth(cell, Map, RMGraffitiDefOf.RM_Graffiti_Vandal);
                    }
                }
            });
            yield return paint;
        }
    }
}
