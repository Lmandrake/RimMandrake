// Verse-free kernel of the proximity hatch: the scan cadence, the trigger radius, the nearest-pawn pick and the gate / hatchling
// decisions CompProximityHatch makes. The comp calls these with the same expressions; SelfTest/ProximityHatchFuzz.cs compiles this
// file alone. Keep it free of Verse/RimWorld/UnityEngine (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.ProximityHatch
{
    public static class RM_ProximityHatchKernel
    {
        /// <summary>Smallest radius the scan ever uses, so a zero or negative multiplier cannot make the egg blind to its own cell.</summary>
        public const float MinRadius = 0.1f;

        /// <summary>Ticks between scans: the egg's own interval times the settings multiplier, at least 1 (Unity's RoundToInt rounds half to even, as Math.Round does).</summary>
        public static int ScanInterval(int baseTicks, float multiplier)
        {
            return Math.Max(1, (int)Math.Round(baseTicks * multiplier));
        }

        /// <summary>Scan radius in cells: the egg's own radius times the settings multiplier, never below MinRadius.</summary>
        public static float Radius(float baseRadius, float multiplier)
        {
            return Math.Max(MinRadius, baseRadius * multiplier);
        }

        /// <summary>One tick of the manual countdown. Returns true when a scan is due now, and then re-arms the counter with <paramref name="interval"/>.</summary>
        public static bool CountdownStep(ref int ticksUntilScan, int interval)
        {
            if (--ticksUntilScan > 0) return false;
            ticksUntilScan = interval;
            return true;
        }

        /// <summary>Whether the comp does any work this tick at all (a fired or unspawned egg never scans).</summary>
        public static bool TicksNow(bool hatchFired, bool spawned)
        {
            return !hatchFired && spawned;
        }

        /// <summary>Whether a scan may run: the same gate RunScan applies, in the same order of precedence.</summary>
        public static bool MayScan(bool hatchFired, bool spawned, bool settingEnabled, bool hasHatcherComp, bool hasMap)
        {
            return !hatchFired && spawned && settingEnabled && hasHatcherComp && hasMap;
        }

        /// <summary>Index of the candidate with the smallest squared distance; the first one wins a tie; -1 when there is none.</summary>
        public static int PickNearest(IList<int> distSq)
        {
            int best = -1;
            int bestDist = int.MaxValue;
            for (int i = 0; i < distSq.Count; i++)
            {
                if (distSq[i] < bestDist)
                {
                    bestDist = distSq[i];
                    best = i;
                }
            }
            return best;
        }

        /// <summary>A thing on the egg's cell counts as the fresh hatchling only if it is a pawn of the expected kind that was not already there.</summary>
        public static bool IsFreshHatchling(bool isPawn, bool kindMatches, bool wasThereBefore)
        {
            return isPawn && kindMatches && !wasThereBefore;
        }
    }
}
