using System.Collections.Generic;
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
    public class JobDriver_TitanClearObstacle : JobDriver
    {
        private int ticksInStrike;
        private int strikes;

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
        }
    }
}
