using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, design §2. One toil holds the watch cycle:
    ///   Watching: stands still, so the engine draws the stationary sprite (the peek pose;
    ///             Pawn.DrawNonHumanlikeStationaryGraphic, the hermit-crab rule) and turns to face
    ///             the nearest pawn that is not its own kind.
    ///   Flinch:   a non-own-kind pawn within the flinch radius, the geophone, or a Hunt order on
    ///             it (hunting is flush-only, Q4) -> puff, hidden hediff on, sign on the cell.
    ///   Hidden:   comes back up after the hide delay once nothing is inside the flinch radius
    ///             and the geophone is quiet; or at once if hungry (then the job ends so it can feed).
    /// The job also ends when it is off its medium, after maxWatchTicks of watching, or when the
    /// settings switch it off. The toil's finish action removes the hediff and the sign on EVERY
    /// exit (end, interrupt, damage, capture, death), so the hidden state never outlives the job
    /// (the RM_JobDriver_Burrow guarantee).
    /// </summary>
    public class RM_JobDriver_Watch : JobDriver
    {
        private const int StepInterval = 30;

        private bool hidden;
        private int hiddenUntilTick = -1;
        private int watchStartTick = -1;
        private RM_WatcherSign sign;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hidden, "rmWatchHidden", false);
            Scribe_Values.Look(ref hiddenUntilTick, "rmWatchHiddenUntil", -1);
            Scribe_Values.Look(ref watchStartTick, "rmWatchStart", -1);
            Scribe_References.Look(ref sign, "rmWatchSign");
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        public override string GetReport()
        {
            return hidden ? "RM_Watchers_ReportHidden".Translate().ToString() : base.GetReport();
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => pawn.Dead || pawn.Downed);
            RM_WatcherExtension ext = pawn.def.GetModExtension<RM_WatcherExtension>();

            Toil watch = ToilMaker.MakeToil("RM_Watch");
            watch.defaultCompleteMode = ToilCompleteMode.Never;
            watch.handlingFacing = true;
            watch.initAction = () =>
            {
                if (watchStartTick < 0)
                {
                    watchStartTick = Find.TickManager.TicksGame;
                }
                pawn.pather?.StopDead();
            };
            watch.tickAction = () =>
            {
                if (ext != null && pawn.IsHashIntervalTick(StepInterval))
                {
                    Step(ext);
                }
            };
            watch.AddFinishAction(() =>
            {
                if (ext != null)
                {
                    RM_WatcherUtility.Emerge(pawn, ext, ref sign, false);
                }
                hidden = false;
            });
            yield return watch;
        }

        private void Step(RM_WatcherExtension ext)
        {
            Map map = pawn.Map;
            if (map == null || !RM_WatchersSettings.watchersEnabled || !RM_WatcherUtility.OnMedium(pawn, ext))
            {
                EndJobWith(JobCondition.InterruptForced);
                return;
            }
            int now = Find.TickManager.TicksGame;
            Pawn nearest = RM_WatcherUtility.NearestOther(pawn, ext, out bool inFlinch);
            bool geo = RM_WatcherUtility.GeophoneFires(pawn, ext);

            if (!hidden)
            {
                bool hunted = map.designationManager.DesignationOn(pawn, DesignationDefOf.Hunt) != null;
                if (RM_WatchersSettings.hideAndFlinch && (inFlinch || geo || hunted))
                {
                    if (hunted)
                    {
                        // Flush-only (Q4, 2026-10-03): a peeking watcher cannot be hunted. It sinks
                        // and the order comes off, saying how to get it.
                        map.designationManager.TryRemoveDesignationOn(pawn, DesignationDefOf.Hunt);
                    }
                    sign = RM_WatcherUtility.Hide(pawn, ext);
                    hidden = true;
                    hiddenUntilTick = now + (int)(ext.hideTicks.RandomInRange * RM_WatchersSettings.emergeDelayScale);
                    if (hunted)
                    {
                        Messages.Message("RM_Watchers_HuntSank".Translate(pawn.LabelShort), sign, MessageTypeDefOf.RejectInput, false);
                    }
                    return;
                }
                if (RM_WatchersSettings.turnToFace && nearest != null)
                {
                    pawn.rotationTracker.FaceCell(nearest.Position);
                }
                if (now - watchStartTick >= ext.maxWatchTicks)
                {
                    EndJobWith(JobCondition.Succeeded);
                }
                return;
            }

            // Hidden. A sign destroyed by something else (a building placed over it) is put back.
            if (sign == null || sign.Destroyed)
            {
                sign = (RM_WatcherSign)ThingMaker.MakeThing(ext.signDef);
                sign.owner = pawn;
                GenSpawn.Spawn(sign, pawn.Position, map);
            }
            bool hungry = pawn.needs?.food != null && pawn.needs.food.CurLevelPercentage < ext.emergeWhenFoodBelow;
            if (!RM_WatchersSettings.hideAndFlinch || hungry || (now >= hiddenUntilTick && !inFlinch && !geo))
            {
                RM_WatcherUtility.Emerge(pawn, ext, ref sign, true);
                hidden = false;
                watchStartTick = now;
                if (hungry)
                {
                    EndJobWith(JobCondition.Succeeded);
                }
            }
        }
    }
}
