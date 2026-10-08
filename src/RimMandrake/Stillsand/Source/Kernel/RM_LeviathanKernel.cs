using System;

namespace RimMandrake.Stillsand
{
    // Verse-free decisions of the sand-leviathan visit (RM_MapComponent_SandLeviathans in RM_SandLeviathan.cs): the visit
    // classifier, the arrival-cell fallback, the warning rumble, the dive state machine (fed / fire / bored / hard ground,
    // then goto sand, then dive), the muurrok's hunt gates and the wettest-body appraisal, plus the incident's odds
    // factor and the edge-entry preference. The mod calls these with the same expressions; the offline fuzz drives them.

    public enum RM_VisitClass { Drop, Rumble, Arrive, Tick }

    public enum RM_ArriveCell { UseEntry, UseFallback, Fail }

    public enum RM_DiveReason { None, Fed, Fire, Bored, HardGround }

    public enum RM_DiveStep { Dive, SeekSand, KeepSeeking }

    public enum RM_VisitEnd { Killed, Gone, ArriveFailed, Dived }

    public static class RM_LeviathanKernel
    {
        public const int Interval = 30;
        public const int DiveTimeoutTicks = 1250;
        public const int HuntRetargetInterval = 250;

        /// <summary>The component only looks at its visits on every Interval-th tick, and only when it has any.</summary>
        public static bool ShouldProcess(int visitCount, int now)
        {
            return !(visitCount == 0 || now % Interval != 0);
        }

        public static RM_VisitClass Classify(bool extMissing, bool kindMissing, bool hasPawn, bool pawnGone, int now, int arriveTick)
        {
            if (extMissing || kindMissing)
            {
                return RM_VisitClass.Drop;
            }
            if (!hasPawn)
            {
                return now < arriveTick ? RM_VisitClass.Rumble : RM_VisitClass.Arrive;
            }
            if (pawnGone)
            {
                return RM_VisitClass.Drop;
            }
            return RM_VisitClass.Tick;
        }

        /// <summary>The entry cell is used when valid and standable, else the loudest-cell fallback, else the visit fails.</summary>
        public static RM_ArriveCell ResolveArrival(bool entryValid, bool entryStandable, bool fallbackFound)
        {
            if (!entryValid || !entryStandable)
            {
                return fallbackFound ? RM_ArriveCell.UseFallback : RM_ArriveCell.Fail;
            }
            return RM_ArriveCell.UseEntry;
        }

        /// <summary>0 at the letter, 1 at the arrival.</summary>
        public static float RumbleT(int arriveTick, int now, int warningTicks)
        {
            int warn = Math.Max(1, warningTicks);
            float x = (arriveTick - now) / (float)warn;
            return 1f - (x < 0f ? 0f : x > 1f ? 1f : x);
        }

        public static float RumbleShake(float t) { return 0.02f + 0.18f * t * t; }
        public static float RumbleDustChance(float t) { return 0.3f + 0.7f * t; }
        public static float RumbleDustSize(float t) { return 1f + 2f * t; }

        /// <summary>A breach is the frame a submerged swimmer surfaces (and is not downed).</summary>
        public static bool IsBreach(bool wasSubmerged, bool submerged, bool downed)
        {
            return wasSubmerged && !submerged && !downed;
        }

        /// <summary>Why a not-yet-diving visitor starts its dive this check, if it does. hardGroundTicks is the visit's
        /// running count of ticks off swim ground, advanced here exactly as the component does.</summary>
        public static RM_DiveReason DecideDive(int kills, int killsAtArrival, bool burning, int now, int arriveTick,
            int maxStayTicks, bool onSand, int hardGroundGiveUpTicks, ref int hardGroundTicks)
        {
            if (kills > killsAtArrival)
            {
                return RM_DiveReason.Fed;
            }
            if (burning)
            {
                return RM_DiveReason.Fire;
            }
            if (now - arriveTick > maxStayTicks)
            {
                return RM_DiveReason.Bored;
            }
            hardGroundTicks = onSand ? 0 : hardGroundTicks + Interval;
            if (hardGroundTicks > hardGroundGiveUpTicks)
            {
                return RM_DiveReason.HardGround;
            }
            return RM_DiveReason.None;
        }

        /// <summary>While diving: go down when on sand or after the timeout, else (re)issue a goto-sand job when it has none.</summary>
        public static RM_DiveStep DiveStep(bool onSand, int now, int diveStartTick, bool hasGotoJob)
        {
            if (onSand || now - diveStartTick > DiveTimeoutTicks)
            {
                return RM_DiveStep.Dive;
            }
            return hasGotoJob ? RM_DiveStep.KeepSeeking : RM_DiveStep.SeekSand;
        }

        /// <summary>The muurrok re-appraises when it has no live target or on every 250th tick.</summary>
        public static bool ShouldRetarget(bool targetInvalid, int now)
        {
            // Only Interval-th ticks reach here, so test the window, not one exact tick
            // (now % 250 == 0 coincides with now % 30 == 0 only every 750 ticks).
            return targetInvalid || now % HuntRetargetInterval < Interval;
        }

        /// <summary>May the mirror beam be started on this check (every gate except the verb's own availability).</summary>
        public static bool BeamGate(bool beamsEnabled, int now, int lastBeamTick, int beamCooldownTicks, bool hasStances, bool fullBodyBusy)
        {
            return beamsEnabled && now - lastBeamTick >= beamCooldownTicks && hasStances && !fullBodyBusy;
        }

        /// <summary>Whether a strike job must be (re)issued: no job, another job, or another target.</summary>
        public static bool NeedsStrikeJob(bool hasJob, bool jobIsAttackMelee, bool jobTargetIsTarget)
        {
            return !hasJob || !jobIsAttackMelee || !jobTargetIsTarget;
        }

        /// <summary>hydration x body size; without a thirst/hydration need every body counts as fully watered.</summary>
        public static float WaterScore(float bodySize, bool hasHydration, float hydrationPercent)
        {
            float hydration = 1f;
            if (hasHydration)
            {
                hydration = Math.Max(0.05f, hydrationPercent);
            }
            return bodySize * hydration;
        }

        /// <summary>Running best of the appraisal: a player pawn always beats a non-player one; within a class the higher score
        /// wins (strictly, so the first of equals keeps it). True when the candidate replaces the best.</summary>
        public static bool BeatsBest(bool player, bool bestPlayer, float score, float bestScore)
        {
            return (player && !bestPlayer) || (player == bestPlayer && score > bestScore);
        }

        /// <summary>The incident's odds multiplier for powered deep drills on the map.</summary>
        public static float VibrationFactor(int drills, float perDrill, float maxFactor)
        {
            return Math.Min(1f + perDrill * drills, maxFactor);
        }

        /// <summary>Running best of the entry-cell sampling: any sand cell beats any non-sand one; within a class the nearer wins.</summary>
        public static bool BetterEntry(bool sand, bool bestOnSand, float distSq, float bestDistSq)
        {
            return (sand && !bestOnSand) || (sand == bestOnSand && distSq < bestDistSq);
        }

        /// <summary>A visit that ends with no pawn left to see must leave a readable sign (no animal vanishes silently).</summary>
        public static bool EndNeedsSign(RM_VisitEnd end)
        {
            return end == RM_VisitEnd.ArriveFailed || end == RM_VisitEnd.Dived;
        }
    }
}
