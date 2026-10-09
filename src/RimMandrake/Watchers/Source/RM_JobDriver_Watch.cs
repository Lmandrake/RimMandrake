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
    ///   Flinch:   a non-own-kind pawn within the flinch radius, the geophone, any optional cue the
    ///             member carries (RM_WatcherCues: gas, heat, fire, steam, shade, buried, light), or a
    ///             neighbour's alarm ripple (RM_WatcherAlarm) -> puff, hidden hediff on, sign on the cell. A body
    ///             or the geophone also starts a new ripple. A Hunt order on it comes off as it goes under:
    ///             a hidden watcher cannot be targeted (owner ruling 2026-10-08, no flushing); area damage
    ///             (fire, explosions, acid) still reaches it, because the hediff hides it without despawning it.
    ///   Hidden:   comes back up after the hide delay once nothing is inside the flinch radius
    ///             and the geophone, every cue and any alarm are quiet; or at once if hungry (then the job ends so it can feed).
    /// The job also ends when it is off its medium, after maxWatchTicks of watching, or when the
    /// settings switch it off. The toil's finish action removes the hediff and the sign on EVERY
    /// exit (end, interrupt, damage, capture, death), so the hidden state never outlives the job
    /// (the RM_JobDriver_Burrow guarantee).
    /// </summary>
    public class RM_JobDriver_Watch : JobDriver
    {
        private const int StepInterval = RM_WatcherKernel.StepInterval;

        private bool hidden;
        private int hiddenUntilTick = -1;
        private int watchStartTick = -1;
        private RM_WatcherSign sign;

        /// <summary>The one sign this job holds while hidden. RM_WatcherSign removes itself when it is not this (orphan or duplicate).
        /// Virtual: a member's own watch driver derived from this one (the Rust Cathedral Watcher's stalk) holds its own sign.</summary>
        public virtual RM_WatcherSign Sign => sign;

        /// <summary>Is this pawn in a watch job (the kit's or a member's own driver derived from it).</summary>
        public static bool InWatchJob(Pawn p)
        {
            return p?.jobs?.curDriver is RM_JobDriver_Watch;
        }

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
            if (map == null)
            {
                EndJobWith(JobCondition.InterruptForced);
                return;
            }
            int now = Find.TickManager.TicksGame;
            bool onMedium = RM_WatcherUtility.OnMedium(pawn, ext);
            // Short-circuit order kept: the scans only run once the watch is known to continue.
            Pawn nearest = null;
            bool inFlinch = false, geo = false, cue = false, huntMarked = false, hungry = false, alarmed = false;
            if (RM_WatchersSettings.watchersEnabled && onMedium)
            {
                nearest = RM_WatcherUtility.NearestOther(pawn, ext, out inFlinch);
                geo = RM_WatcherUtility.GeophoneFires(pawn, ext);
                cue = RM_WatcherCueUtility.CuesNow(pawn, ext) != CueKind.None;
                huntMarked = map.designationManager.DesignationOn(pawn, DesignationDefOf.Hunt) != null;
                hungry = pawn.needs?.food != null && pawn.needs.food.CurLevelPercentage < ext.emergeWhenFoodBelow;
                RM_CompWatcher comp = pawn.GetComp<RM_CompWatcher>();
                alarmed = RM_WatchersSettings.alarmRipple && comp != null && comp.Alarmed;
            }
            StepFlags f = RM_WatcherKernel.DecideStep(new StepIn
            {
                watchersEnabled = RM_WatchersSettings.watchersEnabled, onMedium = onMedium, hidden = hidden,
                hideAndFlinch = RM_WatchersSettings.hideAndFlinch, turnToFace = RM_WatchersSettings.turnToFace,
                hasNearest = nearest != null, inFlinch = inFlinch, geophone = geo, cue = cue, huntMarked = huntMarked, alarmed = alarmed,
                signMissing = hidden && (sign == null || sign.Destroyed), hungry = hungry,
                now = now, hiddenUntil = hiddenUntilTick, watchStart = watchStartTick, maxWatchTicks = ext.maxWatchTicks,
            });
            if ((f & StepFlags.EndInterrupted) != 0)
            {
                EndJobWith(JobCondition.InterruptForced);
                return;
            }
            if ((f & StepFlags.DropHunt) != 0)
            {
                // A hidden watcher cannot be targeted (owner ruling 2026-10-08). The Hunt order is what keeps a player hunter
                // shooting at it (Verb.CanHitTargetFrom only refuses an invisible target to a HOSTILE caster; JobDriver_Hunt fails
                // as soon as the designation is gone), so the order comes off.
                map.designationManager.TryRemoveDesignationOn(pawn, DesignationDefOf.Hunt);
            }
            if ((f & StepFlags.Hide) != 0)
            {
                sign = RM_WatcherUtility.Hide(pawn, ext);
                hidden = true;
                hiddenUntilTick = RM_WatcherKernel.HiddenUntil(now, ext.hideTicks.RandomInRange, RM_WatchersSettings.emergeDelayScale);
                if ((f & StepFlags.DropHunt) != 0)
                {
                    Messages.Message("RM_Watchers_HuntSank".Translate(pawn.LabelShort), sign, MessageTypeDefOf.RejectInput, false);
                }
                if ((f & StepFlags.RaiseAlarm) != 0)
                {
                    RM_WatcherAlarm.Raise(pawn, map);
                }
                return;
            }
            if ((f & StepFlags.RestoreSign) != 0)
            {
                // A sign destroyed by something else (a building placed over it) is put back.
                sign = (RM_WatcherSign)ThingMaker.MakeThing(ext.signDef);
                sign.owner = pawn;
                GenSpawn.Spawn(sign, pawn.Position, map);
            }
            if ((f & StepFlags.Emerge) != 0)
            {
                RM_WatcherUtility.Emerge(pawn, ext, ref sign, true);
                hidden = false;
            }
            if ((f & StepFlags.ResetWatchClock) != 0)
            {
                watchStartTick = now;
            }
            if ((f & StepFlags.Face) != 0)
            {
                pawn.rotationTracker.FaceCell(nearest.Position);
            }
            if ((f & StepFlags.EndSucceeded) != 0)
            {
                EndJobWith(JobCondition.Succeeded);
            }
        }
    }
}
