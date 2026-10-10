using RimWorld;
using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>The Rust Cathedral Watcher's stalk and head (pitch §5.6). On RM_Watcher only, in its own XML: this is data and hooks on one
    /// creature, never a kit option another member can switch on (owner ruling 2026-10-08, "Only for this biome").</summary>
    public class RM_CompProperties_WatcherStalk : CompProperties
    {
        /// <summary>The rise: stalk grows out of the seam (AnimationDef, LoopMode Clamp, so it holds at full height).</summary>
        public AnimationDef riseAnimation;

        /// <summary>The retract: stalk pulls back into the seam (AnimationDef, LoopMode End). Its durationTicks is how long the hide
        /// waits. PROVISIONAL (very shy: fast).</summary>
        public AnimationDef retractAnimation;

        /// <summary>Head turn speed while easing toward its target. PROVISIONAL.</summary>
        public float turnDegreesPerTick = 4f;

        /// <summary>Idle look-around: pause between turns when nobody is near (TurretTop pauses 150-350). PROVISIONAL.</summary>
        public IntRange idlePauseTicks = new IntRange(150, 350);

        public RM_CompProperties_WatcherStalk()
        {
            compClass = typeof(RM_CompWatcherStalk);
        }

        public int RiseTicks => RM_WatchersSettings.watcherStalkAnimation && riseAnimation != null ? riseAnimation.durationTicks : 0;

        public int RetractTicks => RM_WatchersSettings.watcherStalkAnimation && retractAnimation != null ? retractAnimation.durationTicks : 0;
    }

    /// <summary>Holds the stalk phase (read by the render workers each draw) and the eased head angle. The watch job sets the phase and
    /// the look target; this comp turns the head a few degrees a tick toward it and dirties the render tree when the eight-step picture
    /// changes (the tree caches its draw requests until SetDirty; RimSage 1.6 PawnRenderTree.ParallelPreDraw).</summary>
    public class RM_CompWatcherStalk : ThingComp
    {
        public StalkPhase phase = StalkPhase.Down;
        public int phaseStartTick = -1;
        public bool endAfterRetract;
        public float angle = 180f;        // facing south (toward the camera) by default
        public float targetAngle = 180f;
        public bool hasTarget;
        private int idleNextTick = -1;
        private int lastOctant = -1;

        public RM_CompProperties_WatcherStalk Props => (RM_CompProperties_WatcherStalk)props;

        public int Octant => RM_WatcherStalkKernel.Octant(angle);

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref phase, "rmStalkPhase", StalkPhase.Down);
            Scribe_Values.Look(ref phaseStartTick, "rmStalkPhaseStart", -1);
            Scribe_Values.Look(ref endAfterRetract, "rmStalkEndAfterRetract", false);
            Scribe_Values.Look(ref angle, "rmStalkAngle", 180f);
            Scribe_Values.Look(ref targetAngle, "rmStalkTarget", 180f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && phase == StalkPhase.Rising)
            {
                // AnimationDefs are not saved: a rise in progress resumes as fully up (the rise's last frame is the static pose).
                phase = StalkPhase.Up;
            }
        }

        public void SetPhase(StalkPhase p)
        {
            phase = p;
            phaseStartTick = Find.TickManager.TicksGame;
            if (parent is Pawn pawn && pawn.Spawned)
            {
                pawn.Drawer.renderer.renderTree.SetDirty();
            }
        }

        /// <summary>Plays one of the stalk animations (or clears it). Off in settings: nothing plays and the phase times are 0.</summary>
        public void Play(AnimationDef anim)
        {
            if (parent is Pawn pawn && pawn.Spawned)
            {
                pawn.Drawer.renderer.SetAnimation(RM_WatchersSettings.watcherStalkAnimation ? anim : null);
            }
        }

        /// <summary>Back to the plain seam: no animation, stalk down. The job's finish action calls this on every exit.</summary>
        public void ResetDown()
        {
            endAfterRetract = false;
            hasTarget = false;
            if (parent is Pawn pawn && pawn.Spawned && pawn.Drawer.renderer.renderTree.currentAnimation != null)
            {
                pawn.Drawer.renderer.SetAnimation(null);
            }
            SetPhase(StalkPhase.Down);
        }

        public void LookAt(IntVec3 cell)
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null)
            {
                return;
            }
            targetAngle = RM_WatcherStalkKernel.Norm((cell.ToVector3Shifted() - pawn.DrawPos).AngleFlat());
            hasTarget = true;
        }

        public override void CompTick()
        {
            base.CompTick();
            if (phase != StalkPhase.Up && phase != StalkPhase.Rising)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (!hasTarget && now >= idleNextTick)
            {
                targetAngle = RM_WatcherStalkKernel.IdleTarget(angle, Rand.Value);
                idleNextTick = now + Props.idlePauseTicks.RandomInRange;
            }
            float step = RM_WatchersSettings.watcherStalkSmoothTracking ? Props.turnDegreesPerTick : 0f;
            angle = RM_WatcherStalkKernel.Ease(angle, targetAngle, step);
            int oct = Octant;
            if (oct != lastOctant)
            {
                lastOctant = oct;
                if (parent is Pawn pawn && pawn.Spawned)
                {
                    pawn.Drawer.renderer.renderTree.SetDirty();
                }
            }
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            // The husk: the corpse draws the life stage's corpseGraphicData (PawnRenderNode_AnimalPart.GraphicFor) and the stalk and head
            // nodes refuse to draw on a dead pawn (RM_WatcherStalkKernel.StalkDrawn).
            phase = StalkPhase.Down;
            endAfterRetract = false;
        }
    }
}
