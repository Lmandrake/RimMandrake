// Verse-free kernel of the Watchers mod: the watch job's step state machine, the nearest-pawn scan, the think-tree gates (watch giver,
// relocate-to-medium), the hide-duration and flinch-radius arithmetic, the flush hunt-mark rule and the extension's config validation.
// RM_JobDriver_Watch, RM_WatcherUtility, RM_JobGiver_Watch, RM_CompWatcher, RM_WatcherExtension and RM_WatcherUtility.Flush call these with
// the same expressions; SelfTest/WatcherFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib
// (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.Watchers
{
    /// <summary>What one 30-tick step of the watch job decided. The driver applies the flags in a fixed order: DropHunt, Hide, RestoreSign,
    /// Emerge, Face, then the End flags last.</summary>
    [Flags]
    public enum StepFlags
    {
        None = 0,
        EndInterrupted = 1,
        EndSucceeded = 2,
        DropHunt = 4,
        Hide = 8,
        RestoreSign = 16,
        Emerge = 32,
        ResetWatchClock = 64,
        Face = 128,
    }

    public struct StepIn
    {
        public bool watchersEnabled, onMedium, hidden, hideAndFlinch, turnToFace, hasNearest, inFlinch, geophone, hunted, signMissing, hungry;
        public int now, hiddenUntil, watchStart, maxWatchTicks;
    }

    public static class RM_WatcherKernel
    {
        public const int StepInterval = 30;
        public const int CheckInterval = 250;
        public const int NoMediumRecheckTicks = 7500;

        /// <summary>One step of the watch job.</summary>
        public static StepFlags DecideStep(StepIn s)
        {
            if (!s.watchersEnabled || !s.onMedium) return StepFlags.EndInterrupted;
            StepFlags f = StepFlags.None;
            if (!s.hidden)
            {
                if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.hunted))
                {
                    f |= StepFlags.Hide;
                    if (s.hunted) f |= StepFlags.DropHunt;
                    return f;
                }
                if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;
                if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;
                return f;
            }
            if (s.signMissing) f |= StepFlags.RestoreSign;
            if (!s.hideAndFlinch || s.hungry || (s.now >= s.hiddenUntil && !s.inFlinch && !s.geophone))
            {
                f |= StepFlags.Emerge | StepFlags.ResetWatchClock;
                if (s.hungry) f |= StepFlags.EndSucceeded;
            }
            return f;
        }

        /// <summary>How long a freshly hidden watcher stays down: the rolled range value scaled by the player's emerge-delay slider.</summary>
        public static int HiddenUntil(int now, int rolledTicks, float emergeDelayScale)
        {
            return now + (int)(rolledTicks * emergeDelayScale);
        }

        public static float FlinchRadius(float flinchRadius, float scale)
        {
            return flinchRadius * scale;
        }

        /// <summary>Nearest other creature inside the watch radius (first of equals); inFlinch is set when ANY creature inside the watch radius
        /// is within the flinch radius. Distances are squared.</summary>
        public static int Nearest(IList<float> distSq, float watchRadius, float flinchRadius, out bool inFlinch)
        {
            inFlinch = false;
            float watchSq = watchRadius * watchRadius;
            float flinchSq = flinchRadius * flinchRadius;
            int best = -1;
            float bestSq = float.MaxValue;
            for (int i = 0; i < distSq.Count; i++)
            {
                float d = distSq[i];
                if (d > watchSq) continue;
                if (d <= flinchSq) inFlinch = true;
                if (d < bestSq) { bestSq = d; best = i; }
            }
            return best;
        }

        /// <summary>The cheap gates of the think-tree watch giver (evaluated first, so the random roll and the map-wide active-watcher scan only run
        /// for an animal that could actually start a watch).</summary>
        public static bool WatchGiverPre(bool hasExt, bool watchersEnabled, bool spawned, bool downed, bool inMentalState, bool hasMap,
            bool hasComp, bool bolting, bool onMedium, bool hideAndFlinch, bool turnToFace, bool hasFoodNeed, float foodPercent,
            float emergeWhenFoodBelow)
        {
            if (!hasExt || !watchersEnabled) return false;
            if (!spawned || downed || inMentalState || !hasMap) return false;
            if (!hasComp || bolting) return false;
            if (!onMedium) return false;
            if (!hideAndFlinch && !turnToFace) return false;
            if (hasFoodNeed && foodPercent < emergeWhenFoodBelow) return false;
            return true;
        }

        /// <summary>The giver's last two gates: the wander roll and the per-map cap on animals in a watch job.</summary>
        public static bool WatchGiverCapOk(bool wanderRoll, int activeWatchers, int maxActivePerMap)
        {
            return !wanderRoll && activeWatchers < maxActivePerMap;
        }

        /// <summary>The whole giver decision (Pre then CapOk).</summary>
        public static bool WatchGiverAllows(bool hasExt, bool watchersEnabled, bool spawned, bool downed, bool inMentalState, bool hasMap,
            bool hasComp, bool bolting, bool onMedium, bool hideAndFlinch, bool turnToFace, bool hasFoodNeed, float foodPercent,
            float emergeWhenFoodBelow, bool wanderRoll, int activeWatchers, int maxActivePerMap)
        {
            return WatchGiverPre(hasExt, watchersEnabled, spawned, downed, inMentalState, hasMap, hasComp, bolting, onMedium, hideAndFlinch,
                turnToFace, hasFoodNeed, foodPercent, emergeWhenFoodBelow) && WatchGiverCapOk(wanderRoll, activeWatchers, maxActivePerMap);
        }

        /// <summary>The 250-tick comp check: should an idle off-medium watcher be sent looking for its medium.</summary>
        public static bool ShouldSeekMedium(bool watchersEnabled, bool stayOnMedium, bool hasMedium, bool downed, bool inMentalState,
            bool bolting, bool noMediumReachable, bool onMedium, bool hasCurrentJob, bool currentJobIsIdle)
        {
            if (!watchersEnabled || !stayOnMedium || !hasMedium || downed || inMentalState || bolting || noMediumReachable || onMedium) return false;
            if (hasCurrentJob && !currentJobIsIdle) return false;
            return true;
        }

        /// <summary>A flush marks the bolting watcher for hunting only for a player flusher, only if the setting is on, only for an animal
        /// of no humanlike faction (Designator_Hunt's own rule), and never twice.</summary>
        public static bool FlushMarksHunt(bool flushMarksHuntSetting, bool flusherIsPlayer, bool watcherHasFaction, bool watcherFactionHumanlike, bool alreadyMarked)
        {
            return flushMarksHuntSetting && flusherIsPlayer && (!watcherHasFaction || !watcherFactionHumanlike) && !alreadyMarked;
        }

        /// <summary>Config errors of an RM_WatcherExtension (empty list = sound).</summary>
        public static List<string> ConfigErrors(bool hasHiddenHediff, bool hasSignDef, bool signClassOk, float flinchRadius, float watchRadius,
            int hideMin, int hideMax, int maxWatchTicks, int boltTicks, float wanderChance, float emergeWhenFoodBelow, float geophoneMinBodySize)
        {
            var e = new List<string>();
            if (!hasHiddenHediff) e.Add("hiddenHediff is null (it could never hide)");
            if (!hasSignDef) e.Add("signDef is null (a hidden watcher must leave a sign)");
            else if (!signClassOk) e.Add("signDef thingClass is not RM_WatcherSign");
            if (flinchRadius <= 0f || watchRadius < flinchRadius) e.Add("need 0 < flinchRadius <= watchRadius");
            if (hideMin <= 0 || hideMax < hideMin) e.Add("hideTicks range invalid");
            if (maxWatchTicks <= 0 || boltTicks <= 0) e.Add("maxWatchTicks and boltTicks must be positive");
            if (wanderChance < 0f || wanderChance > 1f) e.Add("wanderChance must be a probability in 0..1");
            if (emergeWhenFoodBelow < 0f || emergeWhenFoodBelow > 1f) e.Add("emergeWhenFoodBelow must be a food fraction in 0..1 (above 1 it would never watch at all)");
            if (geophoneMinBodySize < 0f) e.Add("geophoneMinBodySize must not be negative (0 turns the geophone off)");
            return e;
        }
    }
}
