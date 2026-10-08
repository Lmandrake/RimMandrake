// Verse-free kernel of the smother-craft (RM_SmotherCraft.cs): the claim clock, the maturation gate, the dead-wood yield and
// its stack split. SelfTest/LeaningScrubFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub
{
    public static class RM_SmotherKernel
    {
        public const int TicksPerDay = 60000;
        public const int CheckInterval = 2500;

        // Claim length in ticks: the setting floored at 0.1 day, rounded, saturated below int.MaxValue / 2 so that
        // start + claim cannot wrap (a float-to-int cast of a huge value is undefined and wraps negative).
        public static int ClaimTicks(float days)
        {
            double t = Math.Round((double)(Math.Max(0.1f, days) * (float)TicksPerDay));
            if (double.IsNaN(t) || t < 1) return 1;
            return t > int.MaxValue / 2 ? int.MaxValue / 2 : (int)t;
        }

        public static bool Smothered(int startTick) { return startTick >= 0; }

        // The first StartSmother wins; a second changes nothing.
        public static int Start(int startTick, int now) { return startTick >= 0 ? startTick : now; }

        public static int TicksRemaining(int startTick, int claimTicks, int now)
        {
            return startTick >= 0 ? startTick + claimTicks - now : -1;
        }

        // MapComponentTick: the pass runs only on the interval, with claims on file, and only while the feature is on.
        public static bool PassRuns(int claimCount, int tick, bool featureOn) { return claimCount != 0 && tick % CheckInterval == 0 && featureOn; }

        public static bool Due(bool spawned, int remaining) { return spawned && remaining <= 0; }

        public static int YieldCount(int yieldCount, float growth, float yieldFactor)
        {
            return Math.Max(1, (int)Math.Round(yieldCount * Math.Max(0.3f, growth) * yieldFactor));
        }

        // Splits a yield into stacks of at most stackLimit (a limit under 1 is treated as 1: the loop must end).
        public static void Stacks(int count, int stackLimit, List<int> outSizes)
        {
            if (stackLimit < 1) stackLimit = 1;
            while (count > 0)
            {
                int n = Math.Min(count, stackLimit);
                outSizes.Add(n);
                count -= n;
            }
        }
    }
}
