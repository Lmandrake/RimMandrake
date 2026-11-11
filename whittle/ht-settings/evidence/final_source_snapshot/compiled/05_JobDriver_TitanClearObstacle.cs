using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_BREAKTHROUGH_CLEARING_1: walk up to the obstacle (TargetA: a building, a giant's trunk cell or a giant plant) and
    /// strike it every TitanClearing.StrikeIntervalTicks through the wake's crush rules until it is gone, then end Succeeded so
    /// the suspended job resumes and repaths through the gap. Bounded: TitanClearing.MaxStrikes, then Incompletable, and the
    /// obstacle is remembered so the resumed job does not pick it again at once. Re-checked every tick: a setting turned off,
    /// a tier change or an obstacle that stopped being eligible ends the job.
    /// </summary>
    /// <remarks>
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS phase 1: with the walls-and-slots rule on, a crossing job carries its whole crossing
    /// (targetQueueA, the walls; countQueue, layer x 2 + roofed, both read when the creature decided) and job.count = the
    /// CrossVerdict. BreakThrough: on touching it every wall of the crossing breaks at once and the creature pays a x1.5 step
    /// (no stop). Smash: one body-wide blow a second on every wall of the nearest standing layer, WallsSlots.BlowDamage (20 x B,
    /// a roofed wall 2/3 of it), up to MaxBlowsPerLayer a layer. Legacy jobs (count -1) strike targetA by the tier rules as before.
    /// </remarks>
    public class JobDriver_TitanClearObstacle : JobDriver
    {
        private int ticksInStrike;
        private int strikes;
        private int layerStrikes;
        private int curLayer = -1;
        private int pauseLeft = -1;

        private bool CrossingMode => job.count == (int)CrossVerdict.BreakThrough || job.count == (int)CrossVerdict.Smash;

        private bool CrossingGone
        {
            get
            {
                if (job.targetQueueA == null) return true;
                foreach (LocalTargetInfo t in job.targetQueueA)
                    if (t.Thing != null && !t.Thing.Destroyed && t.Thing.Spawned) return false;
                return true;
            }
        }

        private bool CrossingEligible
        {
            get
            {
                if (job.targetQueueA == null) return false;
                foreach (LocalTargetInfo t in job.targetQueueA)
                    if (t.Thing is Building b && !b.Destroyed && b.Spawned && WallsSlotsUtility.WallEligible(pawn, b)) return true;
                return false;
            }
        }

        /// <summary>The nearest layer still standing, -1 when none.</summary>
        private int FrontLayer()
        {
            int best = -1;
            for (int i = 0; i < job.targetQueueA.Count; i++)
            {
                Thing t = job.targetQueueA[i].Thing;
                if (t == null || t.Destroyed || !t.Spawned) continue;
                int layer = i < job.countQueue.Count ? job.countQueue[i] >> 1 : 0;
                if (best < 0 || layer < best) best = layer;
            }
            return best;
        }

        private IEnumerable<Toil> CrossingToils()
        {
            this.FailOn(() => !RM_HugeThingsSettings.WallsSlotsActive || pawn.Flying);
            this.FailOn(() => pauseLeft < 0 && !CrossingGone && !CrossingEligible);
            // A wall it never got to strike (it could not reach touching distance) is not chosen again at once, so a resumed job
            // does not restart the same doomed approach every path start.
            AddFinishAction(delegate (JobCondition c)
            {
                if (c == JobCondition.Succeeded || strikes > 0 || pauseLeft >= 0 || job.targetA.Thing == null) return;
                TitanClearingUtility.NoteGaveUp(pawn, job.targetA.Thing);
            });
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil act = ToilMaker.MakeToil("TitanCross");
            act.initAction = delegate
            {
                ticksInStrike = 0;
                if (job.count == (int)CrossVerdict.BreakThrough && pauseLeft < 0)
                {
                    WallsSlotsUtility.Say(pawn, "RM_WallsSlots_BreaksThrough".Translate());
                    foreach (LocalTargetInfo t in job.targetQueueA)
                        if (t.Thing is Building b && !b.Destroyed && b.Spawned && WallsSlotsUtility.WallEligible(pawn, b))
                            b.Destroy(DestroyMode.KillFinalize);
                    // the step through costs x1.5: half a step's pause, then on
                    pauseLeft = Mathf.CeilToInt(Mathf.Max(1f, pawn.TicksPerMoveCardinal) * (WallsSlots.BreakThroughStepFactor - 1f));
                }
                else if (job.count == (int)CrossVerdict.Smash && curLayer < 0)
                {
                    WallsSlotsUtility.Say(pawn, "RM_WallsSlots_Smashes".Translate(), 600);
                }
            };
            act.tickAction = delegate
            {
                if (pauseLeft >= 0)
                {
                    if (pauseLeft-- <= 0) EndJobWith(JobCondition.Succeeded);
                    return;
                }
                if (CrossingGone)
                {
                    EndJobWith(JobCondition.Succeeded);
                    return;
                }
                int front = FrontLayer();
                if (front != curLayer)
                {
                    curLayer = front;
                    layerStrikes = 0;
                }
                if (ticksInStrike % WallsSlots.SmashIntervalTicks == 0)
                {
                    int b = WallsSlotsUtility.Breadth(pawn);
                    for (int i = 0; i < job.targetQueueA.Count; i++)
                    {
                        if (!(job.targetQueueA[i].Thing is Building w) || w.Destroyed || !w.Spawned) continue;
                        int code = i < job.countQueue.Count ? job.countQueue[i] : 0;
                        if (code >> 1 != front || !WallsSlotsUtility.WallEligible(pawn, w)) continue;
                        pawn.rotationTracker.FaceCell(w.Position);
                        float dmg = WallsSlots.BlowDamage(b, (code & 1) != 0, RM_HugeThingsSettings.blowDamagePerBreadth,
                            RM_HugeThingsSettings.roofWallDamageFactor);
                        w.TakeDamage(new DamageInfo(DamageDefOf.Crush, dmg, instigator: pawn));
                    }
                    strikes++;
                    layerStrikes++;
                    if (CrossingGone)
                    {
                        EndJobWith(JobCondition.Succeeded);
                        return;
                    }
                    if (layerStrikes >= WallsSlots.MaxBlowsPerLayer)
                    {
                        WallsSlotsUtility.Say(pawn, "RM_WallsSlots_GivesUp".Translate());
                        if (job.targetQueueA.Count > 0) TitanClearingUtility.NoteGaveUp(pawn, job.targetQueueA[0].Thing);
                        EndJobWith(JobCondition.Incompletable);
                        return;
                    }
                }
                ticksInStrike++;
            };
            act.defaultCompleteMode = ToilCompleteMode.Never;
            yield return act;
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        private bool ObstacleGone
        {
            get
            {
                Thing t = job.targetA.Thing;
                if (t == null || t.Destroyed || !t.Spawned) return true;
                // A trunk cell whose giant fell is gone with it, even before the map component removes the cell.
                return t is Building_TrunkBlocker && (TitanClearingUtility.GiantOf(t) == null || TitanClearingUtility.GiantOf(t).Destroyed);
            }
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            if (CrossingMode)
            {
                foreach (Toil t in CrossingToils()) yield return t;
                yield break;
            }
            AddEndCondition(() => ObstacleGone ? JobCondition.Succeeded : JobCondition.Ongoing);
            this.FailOn(() => !RM_HugeThingsSettings.TitanClearingActive || pawn.Flying
                              || TitanClearingUtility.Classify(pawn, TitanicTierUtility.GetTier(pawn), job.targetA.Thing) == ClearKind.None);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil strike = ToilMaker.MakeToil("TitanClearStrike");
            strike.initAction = delegate { ticksInStrike = 0; };
            strike.tickAction = delegate
            {
                Thing t = job.targetA.Thing;
                if (t == null) return;
                pawn.rotationTracker.FaceCell(t.Position);
                if (TitanClearing.StrikeDue(ticksInStrike))
                {
                    TitanClearingUtility.Strike(pawn, TitanicTierUtility.GetTier(pawn), t);
                    strikes++;
                    if (ObstacleGone)
                    {
                        EndJobWith(JobCondition.Succeeded);
                        return;
                    }
                    if (TitanClearing.GiveUp(strikes))
                    {
                        TitanClearingUtility.NoteGaveUp(pawn, t);
                        EndJobWith(JobCondition.Incompletable);
                        return;
                    }
                }
                ticksInStrike++;
            };
            strike.defaultCompleteMode = ToilCompleteMode.Never;
            strike.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return strike;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksInStrike, "ticksInStrike", 0);
            Scribe_Values.Look(ref strikes, "strikes", 0);
            Scribe_Values.Look(ref layerStrikes, "layerStrikes", 0);
            Scribe_Values.Look(ref curLayer, "curLayer", -1);
            Scribe_Values.Look(ref pauseLeft, "pauseLeft", -1);
        }
    }
}
