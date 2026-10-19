using System.Collections.Generic;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS §4 / §5.2: a big creature squeezes through a gap narrower than its body but at least
    /// half as wide. targetQueueA holds the straight squeeze line (entry first, exit last; WallsSlotsUtility.PlanSqueeze),
    /// countQueue each cell's gap width. The creature walks to the entry, then steps cell by cell along the line itself, each step
    /// costing its cardinal move time x the squeeze cost of that cell's gap (x2 at half width by the owner's card), straight
    /// only: no turns, no diagonal corner cuts. Every step scrapes the built sides (§5.6). Never through rock, never under
    /// overhead mountain (the plan refuses both). A squeeze interrupted mid-way backs out to the nearer end it can stand on, with
    /// a mote; saving mid-squeeze keeps the step index.
    ///
    /// Why a job and not a pathfinder exception: Large Pawns refuses every anchor whose square has an unwalkable cell
    /// (GenGrid.WalkableBy prefix and its own region grids), so the pathfinder, reachability and the region graph all agree that
    /// a narrow gap is closed to the body. The squeeze never tells them otherwise; it is the one way through, started from the
    /// path-start hook, so route, execution and reachability cannot disagree (§6).
    /// </summary>
    public class JobDriver_TitanSqueeze : JobDriver
    {
        private int step = 1;
        private float progress;
        private bool done;

        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        private List<LocalTargetInfo> Line => job.targetQueueA;

        private float TicksFor(int i)
        {
            int pw = WallsSlotsUtility.Passage(pawn);
            int slot = job.countQueue != null && i < job.countQueue.Count ? job.countQueue[i] : pw;
            float c = WallsSlots.SqueezeCost(slot, pw, RM_HugeThingsSettings.squeezeSlowdownAtHalf);
            if (float.IsInfinity(c) || float.IsNaN(c)) c = WallsSlots.SaneSqueezeAtHalf(RM_HugeThingsSettings.squeezeSlowdownAtHalf);
            return Mathf.Max(1f, pawn.TicksPerMoveCardinal) * c;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !RM_HugeThingsSettings.SqueezeActive || pawn.Flying || Line == null || Line.Count < 2);
            AddFinishAction(delegate (JobCondition c)
            {
                if (done || pawn == null || !pawn.Spawned || Line == null || Line.Count < 2) return;
                if (pawn.Position.WalkableBy(pawn.Map, pawn)) return;
                // Also on a Succeeded that is only job expiry (done false): the pawn must not be left standing in the gap.
                // Back out the way it came, or finish forward, whichever end is nearer and still free.
                IntVec3 entry = Line[0].Cell, exit = Line[Line.Count - 1].Cell;
                bool forward = step * 2 >= Line.Count;
                IntVec3 to = forward ? exit : entry;
                if (!to.WalkableBy(pawn.Map, pawn)) to = forward ? entry : exit;
                if (!to.WalkableBy(pawn.Map, pawn)) return;
                pawn.Position = to;
                pawn.Drawer?.tweener?.ResetTweenedPosToRoot();
                WallsSlotsUtility.Say(pawn, "RM_WallsSlots_BacksOut".Translate());
            });

            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

            Toil squeeze = ToilMaker.MakeToil("TitanSqueeze");
            squeeze.initAction = delegate
            {
                pawn.pather.StopDead();
                if (step < 1) step = 1;
                WallsSlotsUtility.Say(pawn, "RM_WallsSlots_Squeezes".Translate(), 600);
            };
            squeeze.tickAction = delegate
            {
                if (step >= Line.Count)
                {
                    done = true;
                    EndJobWith(JobCondition.Succeeded);
                    return;
                }
                progress += 1f;
                if (progress < TicksFor(step)) return;
                IntVec3 next = Line[step].Cell;
                IntVec3 prev = Line[step - 1].Cell;
                if (!WallsSlotsUtility.SqueezeOpen(pawn, next))
                {
                    // Something now fills the gap (a wall was built, a door closed): it backs out.
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                IntVec3 d = next - prev;
                pawn.rotationTracker.FaceCell(next);
                pawn.Position = next;    // the wake fires from this assignment, as it does for a walked step
                pawn.Drawer?.tweener?.ResetTweenedPosToRoot();
                WallsSlotsUtility.Scrape(pawn, next, d.x, d.z);
                progress = 0f;
                step++;
                if (step >= Line.Count)
                {
                    done = true;
                    EndJobWith(JobCondition.Succeeded);
                }
            };
            squeeze.defaultCompleteMode = ToilCompleteMode.Never;
            yield return squeeze;
        }

        public override string GetReport() => "RM_WallsSlots_Squeezes".Translate();

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref step, "squeezeStep", 1);
            Scribe_Values.Look(ref progress, "squeezeProgress", 0f);
            Scribe_Values.Look(ref done, "squeezeDone", false);
        }
    }
}
