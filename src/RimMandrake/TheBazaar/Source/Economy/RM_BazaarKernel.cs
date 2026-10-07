using System;
using System.Collections.Generic;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// The Bazaar price engine's arithmetic, with no Verse or UnityEngine type in it so the offline
    /// fuzz (Source/SelfTest/BazaarFuzz.cs, `python3 src/RimMandrake/Utils/selftest_bazaar_fuzz.py`)
    /// compiles THIS file and drives the same code the game runs. RM_BazaarEconomy and
    /// RM_BazaarBucket call it; nothing here is a copy. If a `using Verse;` lands in this file the
    /// selftest build breaks, which is the guard rail working.
    /// </summary>
    public static class RM_BazaarKernel
    {
        public const float BandMin = 0.25f;
        public const float BandMax = 4.0f;
        public const int HistorySize = 32;

        /// <summary>Per drift step: pull toward target, random walk, and the largest relative move allowed in one day.</summary>
        public const float ReversionRate = 0.2f;
        public const float DailyNoise = 0.04f;
        public const float MaxDailyStep = 0.10f;
        public const float NudgeDecay = 0.8f;

        public const float NudgeMin = -0.75f;
        public const float NudgeMax = 3f;

        public static float Clamp(float v, float lo, float hi) => v < lo ? lo : (v > hi ? hi : v);

        /// <summary>A hash as a unit float, [0,1]. Float rounding lifts the top 64 uint values to exactly 1.0.</summary>
        public static float ToUnit(int h) => (uint)h / 4294967296f;

        /// <summary>The seeded resting level of a bucket: an authored or procedural target, held inside the band.</summary>
        public static float SeedLevel(float target) => Clamp(target, BandMin, BandMax);

        /// <summary>
        /// One day of drift for one bucket: pull toward the (nudged) target, add a small deterministic walk
        /// (<paramref name="noiseU"/> in [0,1] is the hashed unit), clamp the step to +-10% and the value to the
        /// band, decay the nudge. Returns the new multiplier.
        /// </summary>
        public static float DriftStep(float multiplier, float target, ref float nudge, float noiseU)
        {
            float t = Clamp(target * (1f + nudge), BandMin, BandMax);
            float noise = (noiseU * 2f - 1f) * DailyNoise;
            float step = (t - multiplier) * ReversionRate + multiplier * noise;
            float cap = multiplier * MaxDailyStep;
            step = Clamp(step, -cap, cap);
            float result = Clamp(multiplier + step, BandMin, BandMax);
            nudge *= NudgeDecay;
            if (Math.Abs(nudge) < 0.001f) nudge = 0f;
            return result;
        }

        /// <summary>An event push on a bucket's target fraction.</summary>
        public static float NudgeBy(float nudge, float fraction) => Clamp(nudge + fraction, NudgeMin, NudgeMax);

        /// <summary>Append to a fixed-size ring kept as a list plus a write head (the saved shape).</summary>
        public static void RingPush<T>(List<T> ring, ref int head, T item)
        {
            if (ring.Count < HistorySize)
            {
                ring.Add(item);
                head = ring.Count % HistorySize;
            }
            else
            {
                ring[head] = item;
                head = (head + 1) % HistorySize;
            }
        }

        public static IEnumerable<T> RingOldestFirst<T>(List<T> ring, int head)
        {
            if (ring.Count < HistorySize)
            {
                for (int i = 0; i < ring.Count; i++) yield return ring[i];
                yield break;
            }
            for (int i = 0; i < ring.Count; i++) yield return ring[(head + i) % ring.Count];
        }

        /// <summary>Load-time repair: cap an over-long saved ring and put the head back in range.</summary>
        public static int RingRepair<T>(List<T> ring, int head)
        {
            if (ring.Count > HistorySize) ring.RemoveRange(HistorySize, ring.Count - HistorySize);
            return ring.Count == 0 ? 0 : (int)Clamp(head, 0, ring.Count - 1);
        }
    }
}
