// Verse-free kernel of the Rust Cathedral Watcher (RM_Watcher; WATCHER_CREATURES_MOD_1, pitch §5): the stalk phase machine that makes the
// hide wait for the retract, the eased head angle, the eight-step octant and its mirrored picture, and the idle look-around.
// RM_JobDriver_WatcherStalk, RM_CompWatcherStalk and RM_PawnRenderNodeWorker_WatcherHead call these with the same expressions;
// SelfTest/WatcherStalkFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine (the self-test build is the guard rail).
using System;

namespace RimMandrake.Watchers
{
    /// <summary>Where the stalk is. Down = in the seam (hidden or merely not watching); Rising/Retracting = an AnimationDef is playing.</summary>
    public enum StalkPhase
    {
        Down = 0,
        Rising = 1,
        Up = 2,
        Retracting = 3,
    }

    /// <summary>What one step of the Watcher's watch job decided on top of the kit's StepFlags. Applied in order: ApplyEmerge, StartRise,
    /// StartRetract, ApplyHide, Face, then the End flags.</summary>
    [Flags]
    public enum StalkFlags
    {
        None = 0,
        StartRise = 1,
        StartRetract = 2,
        ApplyHide = 4,
        ApplyEmerge = 8,
        Face = 16,
        EndSucceeded = 32,
        EndInterrupted = 64,
        ResetWatchClock = 128,
        RestoreSign = 256,
    }

    public struct StalkIn
    {
        public StalkPhase phase;
        /// <summary>Ticks since the current phase began.</summary>
        public int elapsed;
        public int riseTicks, retractTicks;
        /// <summary>The retract under way was started to end the bout (not to hide): when it finishes the job ends, no hide.</summary>
        public bool endAfterRetract;
        /// <summary>The hidden hediff is on (only ever true in phase Down).</summary>
        public bool hidden;
        /// <summary>The kit's own decision for this step (RM_WatcherKernel.DecideStep), made with hidden = the real hidden state.</summary>
        public StepFlags kit;
    }

    public struct StalkOut
    {
        public StalkPhase phase;
        public bool endAfterRetract;
        public bool phaseChanged;
        public StalkFlags flags;
    }

    public static class RM_WatcherStalkKernel
    {
        /// <summary>One step. The one rule the pitch names as the risk (§5.6): the hidden hediff goes on ONLY when a retract has run its full
        /// length, so the stalk pulls down into the seam instead of blinking out. A retract, once started, always finishes; only a forced end
        /// (off its medium, settings off) cuts it short, and that ends the job, whose finish action clears everything.</summary>
        public static StalkOut Step(StalkIn s)
        {
            var o = new StalkOut { phase = s.phase, endAfterRetract = s.endAfterRetract };
            StepFlags k = s.kit;
            if ((k & StepFlags.EndInterrupted) != 0)
            {
                o.flags = StalkFlags.EndInterrupted;
                return o;
            }
            if ((k & StepFlags.RestoreSign) != 0) o.flags |= StalkFlags.RestoreSign;
            switch (s.phase)
            {
                case StalkPhase.Retracting:
                    if (s.elapsed >= s.retractTicks)
                    {
                        o.phase = StalkPhase.Down;
                        o.phaseChanged = true;
                        if (s.endAfterRetract) o.flags |= StalkFlags.EndSucceeded;
                        else o.flags |= StalkFlags.ApplyHide;
                        o.endAfterRetract = false;
                    }
                    return o;
                case StalkPhase.Down:
                    if (s.hidden)
                    {
                        if ((k & StepFlags.Emerge) == 0) return o;
                        // Coming up out of hiding: hediff off, then the rise.
                        o.flags |= StalkFlags.ApplyEmerge;
                        if ((k & StepFlags.ResetWatchClock) != 0) o.flags |= StalkFlags.ResetWatchClock;
                        if ((k & StepFlags.EndSucceeded) != 0)
                        {
                            // The kit ends a hungry emerge at once (the Watcher has no food need; kept for the kit's meaning).
                            o.flags |= StalkFlags.EndSucceeded;
                            return o;
                        }
                        o.flags |= StalkFlags.StartRise;
                        o.phase = StalkPhase.Rising;
                        o.phaseChanged = true;
                        return o;
                    }
                    if ((k & StepFlags.Hide) != 0)
                    {
                        // Visible with the stalk down (a bout's first step): it hides with nothing to pull down.
                        o.flags |= StalkFlags.ApplyHide;
                        return o;
                    }
                    if ((k & StepFlags.EndSucceeded) != 0)
                    {
                        o.flags |= StalkFlags.EndSucceeded;
                        return o;
                    }
                    // A bout's first quiet step: rise.
                    o.flags |= StalkFlags.StartRise;
                    o.phase = StalkPhase.Rising;
                    o.phaseChanged = true;
                    return o;
                default: // Rising, Up
                    if ((k & StepFlags.Hide) != 0)
                    {
                        o.flags |= StalkFlags.StartRetract;
                        o.phase = StalkPhase.Retracting;
                        o.phaseChanged = true;
                        o.endAfterRetract = false;
                        if (s.retractTicks <= 0)
                        {
                            o.phase = StalkPhase.Down;
                            o.flags |= StalkFlags.ApplyHide;
                        }
                        return o;
                    }
                    if ((k & StepFlags.EndSucceeded) != 0)
                    {
                        // The bout is over: pull down into the seam first, then end (no hide, no sign).
                        o.flags |= StalkFlags.StartRetract;
                        o.phase = StalkPhase.Retracting;
                        o.phaseChanged = true;
                        o.endAfterRetract = true;
                        if (s.retractTicks <= 0)
                        {
                            o.phase = StalkPhase.Down;
                            o.endAfterRetract = false;
                            o.flags |= StalkFlags.EndSucceeded;
                        }
                        return o;
                    }
                    if (s.phase == StalkPhase.Rising && s.elapsed >= s.riseTicks)
                    {
                        o.phase = StalkPhase.Up;
                        o.phaseChanged = true;
                    }
                    if ((k & StepFlags.Face) != 0) o.flags |= StalkFlags.Face;
                    return o;
            }
        }

        /// <summary>Whether the stalk and head draw at all. Down draws only the seam hatch (or nothing, when hidden: a hidden pawn draws
        /// nothing). Retracting with its animation already cleared draws nothing, so the stalk cannot pop back to full height for the tick
        /// between the animation ending and the hide.</summary>
        public static bool StalkDrawn(StalkPhase phase, bool animationPlaying, bool dead)
        {
            if (dead) return false;
            switch (phase)
            {
                case StalkPhase.Up: return true;
                case StalkPhase.Rising: return true;
                case StalkPhase.Retracting: return animationPlaying;
                default: return false;
            }
        }

        /// <summary>Normalise to [0, 360).</summary>
        public static float Norm(float a)
        {
            a %= 360f;
            if (a < 0f) a += 360f;
            return a >= 360f ? 0f : a;
        }

        /// <summary>Signed shortest turn from a to b, in (-180, 180].</summary>
        public static float Delta(float a, float b)
        {
            float d = Norm(b) - Norm(a);
            if (d > 180f) d -= 360f;
            if (d <= -180f) d += 360f;
            return d;
        }

        /// <summary>Move cur toward target along the shorter arc by at most maxStep degrees (maxStep &lt;= 0 = snap).</summary>
        public static float Ease(float cur, float target, float maxStep)
        {
            if (maxStep <= 0f) return Norm(target);
            float d = Delta(cur, target);
            if (Math.Abs(d) <= maxStep) return Norm(target);
            return Norm(cur + (d > 0f ? maxStep : -maxStep));
        }

        /// <summary>Eight 45-degree steps; 0 = north, 2 = east, 4 = south, 6 = west (RimWorld's AngleFlat: 0 north, 90 east). Each octant
        /// is centred on its direction, so 22.5 degrees either side of north is octant 0.</summary>
        public static int Octant(float angle)
        {
            int o = (int)Math.Floor((Norm(angle) + 22.5f) / 45f);
            return o % 8;
        }

        /// <summary>The drawn picture for an octant: 5 are drawn (0 N, 1 NE, 2 E, 3 SE, 4 S) and the three west-side ones mirror
        /// (5 SW = SE flipped, 6 W = E flipped, 7 NW = NE flipped). Pitch §5.5.</summary>
        public static int PictureFor(int octant, out bool mirrored)
        {
            octant = ((octant % 8) + 8) % 8;
            mirrored = octant > 4;
            return mirrored ? 8 - octant : octant;
        }

        /// <summary>The angle of an octant's centre.</summary>
        public static float OctantAngle(int octant)
        {
            return (((octant % 8) + 8) % 8) * 45f;
        }

        /// <summary>The idle look-around (TurretTop's idle shape: turn a while, pause a while). Given a uniform roll in [0,1) and the
        /// current angle, the next idle target: a turn of 45-135 degrees, either way.</summary>
        public static float IdleTarget(float cur, float roll)
        {
            float mag = 45f + 90f * Math.Abs(roll * 2f - 1f);
            return Norm(cur + (roll < 0.5f ? -mag : mag));
        }
    }
}
