using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// The Rust Cathedral Watcher's watch bout (pitch §5; owner rulings 2026-10-08). The kit decides as it does for every member
    /// (RM_WatcherKernel.DecideStep: flinch radius, cues, hide delay, bout length); RM_WatcherStalkKernel.Step turns that into the stalk:
    ///   rise out of the seam (AnimationDef) -> watch, the head easing toward the nearest pawn not of its kind in eight 45-degree pictures
    ///   -> on a flinch, retract (AnimationDef) and ONLY THEN hide (hediff + seam-glint sign), so it pulls down instead of blinking out
    ///   -> after the hide delay, emerge and rise again. A bout that simply runs out retracts and ends without hiding.
    /// It is its own job and driver so the rise/track behaviour stays on this one creature. It derives from RM_JobDriver_Watch only so
    /// every kit check that asks "is this pawn in a watch job, and is this its sign" (RM_WatcherSign.StillValid, the comp's orphan guard,
    /// the alarm ripple) sees it as one; MakeNewToils, Sign and the state are its own. Hunting: the Watcher is mechanoid-fleshed, so the
    /// Hunt designator never offers it; huntMarked is always false.
    /// The finish action removes the hediff, the sign and the animation on EVERY exit, as the kit's driver does.
    /// </summary>
    public class RM_JobDriver_WatcherStalk : RM_JobDriver_Watch
    {
        private const int StepInterval = RM_WatcherKernel.StepInterval;
        private const int FineInterval = 5;

        private bool hidden;
        private int hiddenUntilTick = -1;
        private int watchStartTick = -1;
        private RM_WatcherSign sign;

        public override RM_WatcherSign Sign => sign;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hidden, "rmStalkHidden", false);
            Scribe_Values.Look(ref hiddenUntilTick, "rmStalkHiddenUntil", -1);
            Scribe_Values.Look(ref watchStartTick, "rmStalkWatchStart", -1);
            Scribe_References.Look(ref sign, "rmStalkSign");
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
            RM_CompWatcherStalk stalk = pawn.GetComp<RM_CompWatcherStalk>();

            Toil watch = ToilMaker.MakeToil("RM_WatchStalk");
            watch.defaultCompleteMode = ToilCompleteMode.Never;
            watch.handlingFacing = true;
            watch.initAction = () =>
            {
                if (watchStartTick < 0)
                {
                    watchStartTick = Find.TickManager.TicksGame;
                }
                pawn.pather?.StopDead();
                // The base always faces south: the head picture carries the direction, not the pawn's Rot4.
                pawn.Rotation = Rot4.South;
            };
            watch.tickAction = () =>
            {
                if (ext == null || stalk == null)
                {
                    EndJobWith(JobCondition.Errored);
                    return;
                }
                // The phase ends are timed to the animation length, so a retract is checked finely; the scans run at the kit's interval.
                bool full = pawn.IsHashIntervalTick(StepInterval);
                if (full || (stalk.phase == StalkPhase.Retracting || stalk.phase == StalkPhase.Rising) && pawn.IsHashIntervalTick(FineInterval))
                {
                    Step(ext, stalk, full);
                }
            };
            watch.AddFinishAction(() =>
            {
                if (ext != null)
                {
                    RM_WatcherUtility.Emerge(pawn, ext, ref sign, false);
                }
                hidden = false;
                stalk?.ResetDown();
            });
            yield return watch;
        }

        private void Step(RM_WatcherExtension ext, RM_CompWatcherStalk stalk, bool full)
        {
            Map map = pawn.Map;
            if (map == null)
            {
                EndJobWith(JobCondition.InterruptForced);
                return;
            }
            int now = Find.TickManager.TicksGame;
            bool enabled = RM_WatchersSettings.watchersEnabled && RM_WatcherStalkSettings.watcherEnabled;
            bool onMedium = RM_WatcherUtility.OnMedium(pawn, ext);
            StepFlags kit = StepFlags.None;
            Pawn nearest = null;
            if (full || stalk.phase != StalkPhase.Retracting)
            {
                bool inFlinch = false, geo = false, cue = false, alarmed = false;
                if (enabled && onMedium)
                {
                    nearest = RM_WatcherUtility.NearestOther(pawn, ext, out inFlinch);
                    geo = RM_WatcherUtility.GeophoneFires(pawn, ext);
                    cue = RM_WatcherCueUtility.CuesNow(pawn, ext) != CueKind.None;
                    RM_CompWatcher comp = pawn.GetComp<RM_CompWatcher>();
                    alarmed = RM_WatchersSettings.alarmRipple && comp != null && comp.Alarmed;
                }
                kit = RM_WatcherKernel.DecideStep(new StepIn
                {
                    watchersEnabled = enabled, onMedium = onMedium, hidden = hidden,
                    hideAndFlinch = RM_WatchersSettings.hideAndFlinch, turnToFace = RM_WatchersSettings.turnToFace,
                    hasNearest = nearest != null, inFlinch = inFlinch, geophone = geo, cue = cue, huntMarked = false, alarmed = alarmed,
                    signMissing = hidden && (sign == null || sign.Destroyed), hungry = false,
                    now = now, hiddenUntil = hiddenUntilTick, watchStart = watchStartTick, maxWatchTicks = ext.maxWatchTicks,
                });
            }
            else if (!enabled || !onMedium)
            {
                kit = StepFlags.EndInterrupted;
            }
            StalkOut o = RM_WatcherStalkKernel.Step(new StalkIn
            {
                phase = stalk.phase, elapsed = stalk.phaseStartTick < 0 ? int.MaxValue : now - stalk.phaseStartTick,
                riseTicks = stalk.Props.RiseTicks, retractTicks = stalk.Props.RetractTicks,
                endAfterRetract = stalk.endAfterRetract, hidden = hidden, kit = kit,
            });
            stalk.endAfterRetract = o.endAfterRetract;
            if ((o.flags & StalkFlags.EndInterrupted) != 0)
            {
                EndJobWith(JobCondition.InterruptForced);
                return;
            }
            if ((o.flags & StalkFlags.RestoreSign) != 0 && hidden)
            {
                sign = (RM_WatcherSign)ThingMaker.MakeThing(ext.signDef);
                sign.owner = pawn;
                GenSpawn.Spawn(sign, pawn.Position, map);
            }
            if ((o.flags & StalkFlags.ApplyEmerge) != 0)
            {
                RM_WatcherUtility.Emerge(pawn, ext, ref sign, true);
                hidden = false;
            }
            if ((o.flags & StalkFlags.ResetWatchClock) != 0)
            {
                watchStartTick = now;
            }
            if (o.phaseChanged)
            {
                stalk.SetPhase(o.phase);
            }
            if ((o.flags & StalkFlags.StartRise) != 0)
            {
                stalk.Play(stalk.Props.riseAnimation);
            }
            if ((o.flags & StalkFlags.StartRetract) != 0)
            {
                stalk.Play(stalk.Props.retractAnimation);
            }
            if ((kit & StepFlags.RaiseAlarm) != 0 && (o.flags & (StalkFlags.StartRetract | StalkFlags.ApplyHide)) != 0)
            {
                // The kit's alarm ripple goes out at the flinch, not when the stalk is finally down.
                RM_WatcherAlarm.Raise(pawn, map);
            }
            if ((o.flags & StalkFlags.ApplyHide) != 0)
            {
                stalk.Play(null);
                sign = RM_WatcherUtility.Hide(pawn, ext);
                hidden = true;
                hiddenUntilTick = RM_WatcherKernel.HiddenUntil(now, ext.hideTicks.RandomInRange, RM_WatchersSettings.emergeDelayScale);
            }
            if (full && !hidden)
            {
                if ((o.flags & StalkFlags.Face) != 0 && nearest != null)
                {
                    stalk.LookAt(nearest.Position);
                }
                else
                {
                    stalk.hasTarget = false;
                }
            }
            if ((o.flags & StalkFlags.EndSucceeded) != 0)
            {
                EndJobWith(JobCondition.Succeeded);
            }
        }
    }

    /// <summary>The Watcher's watch giver, listed in its own think tree (RM_ThinkTree_Watcher): a mechanoid-fleshed race is never an
    /// Animal, so the kit's Animal_PreWander splice never reaches it (pitch §5.3, the living-bolt shape).</summary>
    public class RM_JobGiver_WatcherStalk : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_WatcherExtension ext = pawn?.def.GetModExtension<RM_WatcherExtension>();
            if (ext == null || pawn.GetComp<RM_CompWatcherStalk>() == null || !RM_WatcherStalkSettings.watcherEnabled)
            {
                return null;
            }
            RM_CompWatcher comp = pawn.GetComp<RM_CompWatcher>();
            if (!RM_WatcherKernel.WatchGiverPre(true, RM_WatchersSettings.watchersEnabled, pawn.Spawned, pawn.Downed, pawn.InMentalState,
                    pawn.Map != null, comp != null, pawn.Map != null && RM_WatcherUtility.OnMedium(pawn, ext),
                    RM_WatchersSettings.hideAndFlinch, RM_WatchersSettings.turnToFace, false, 1f, ext.emergeWhenFoodBelow))
            {
                return null;
            }
            if (Rand.Chance(ext.wanderChance))
            {
                return null;
            }
            return JobMaker.MakeJob(RM_WatcherStalkDefOf.RM_WatcherStalkWatch);
        }
    }

    [DefOf]
    public static class RM_WatcherStalkDefOf
    {
        public static JobDef RM_WatcherStalkWatch;

        static RM_WatcherStalkDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WatcherStalkDefOf));
        }
    }
}
