// Verse-free kernel of the Wasteland ambient dose (RM_CompAmbientDose), the gripper's theft quantity
// (RM_JobGiver_GripperSteal.UnitsToTake) and the processor animal's fullness step (RM_CompProcessorGatherable).
// SelfTest/WastelandFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Wasteland
{
    public static class RM_DoseKernel
    {
        public static float Lerp(float a, float b, float t) { t = t < 0f ? 0f : (t > 1f ? 1f : t); return a + (b - a) * t; }

        // A dose pass does nothing when the multiplier or the comp's factor is not positive.
        public static bool DoseActive(float multiplier, float toxicFactor) { return !(multiplier <= 0f || toxicFactor <= 0f); }

        // Outdoors: squared edge distance d2 within radius r. Returns the factor, or -1 when out of range.
        // (A real factor is never negative: toxicFactor and edgeFactor are validated >= 0.)
        public static float OutdoorFactor(float toxicFactor, float edgeFactor, float d2, float r)
        {
            if (d2 > r * r) return -1f;
            return toxicFactor * Lerp(1f, edgeFactor, (float)Math.Sqrt(d2) / r);
        }

        // Indoors: the whole shared room at the flat factor, nobody else.
        public static float IndoorFactor(float toxicFactor, bool sameRoom) { return sameRoom ? toxicFactor : -1f; }

        public static float Applied(float factor, float multiplier) { return factor * multiplier; }

        // Units a gripper would take: 0 for an illegal target, else min(stack, maxUnits, floor(maxMass / unitMass)).
        public static int UnitsToTake(bool legal, float unitMass, int stackCount, int maxUnitsTaken, float maxCarryMass)
        {
            if (!legal) return 0;
            int byMass = int.MaxValue;
            if (unitMass > 0.0001f)
            {
                // Floor in double and clamp: a float-to-int cast of a huge or NaN quotient is undefined and wrapped to a negative.
                double q = Math.Floor((double)maxCarryMass / unitMass);
                byMass = double.IsNaN(q) ? 0 : (q >= int.MaxValue ? int.MaxValue : (q <= int.MinValue ? int.MinValue : (int)q));
            }
            return Math.Max(0, Math.Min(stackCount, Math.Min(maxUnitsTaken, byMass)));
        }

        // Fullness gained per tick, with the off-feed slow-down; capped at 1.
        public static float FullnessRate(float intervalDays, int ticksPerDay, float growth, bool onFeed, float offFeedRateFactor)
        {
            float num = 1f / (intervalDays * (float)ticksPerDay);
            num *= growth;
            if (!onFeed) num *= offFeedRateFactor;
            return num;
        }
        public static float NextFullness(float fullness, float rate) { return Math.Min(1f, fullness + rate); }

        // Per-check chance to un-pollute the cell under the animal.
        public static float UnpolluteChance(float chancePerDay, int checkIntervalTicks, int ticksPerDay) { return chancePerDay * checkIntervalTicks / ticksPerDay; }
    }
}
