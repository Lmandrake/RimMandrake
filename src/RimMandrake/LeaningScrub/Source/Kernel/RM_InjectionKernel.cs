// Verse-free kernel of the Scrub's inhabited injections (RM_ScrubInjections.cs): which ruin goes where, how much of a
// ruined wall stands, and spacing. SelfTest/LeaningScrubTonightCheck.cs compiles this file alone.
//
// Owner rulings Q10 (card 2026-10-15, "Ruins plus living camps") and N1 (typed: "Scavengers and vapor farming new").
// Numbers PROVISIONAL (owner ruling 2026-10-03).
using System;

namespace RimMandrake.LeaningScrub
{
    public static class RM_InjectionKernel
    {
        public const int RuinFarmstead = 0;
        public const int RuinSmotherField = 1;
        public const int RuinHedgeHomestead = 2;

        // The first ruin on every map is a dead farmstead: it carries the vaporator study source, so a map with any
        // ruins at all can teach the vaporator. The rest split evenly between the other two.
        public static int RuinKind(int index, double roll)
        {
            if (index <= 0) return RuinFarmstead;
            return roll < 0.5 ? RuinSmotherField : RuinHedgeHomestead;
        }

        public static int Clamp(int n, int lo, int hi)
        {
            return Math.Max(lo, Math.Min(hi, n));
        }

        // Share of a dead farmstead's wall still standing. PROVISIONAL.
        public const double WallStandingChance = 0.55;

        public static bool WallStands(double roll)
        {
            return roll < WallStandingChance;
        }

        // A ruin's walls keep 25-60% of their hit points. PROVISIONAL.
        public static int RuinHitPoints(int maxHitPoints, double roll)
        {
            if (maxHitPoints <= 1) return 1;
            double f = 0.25 + 0.35 * Math.Max(0.0, Math.Min(1.0, roll));
            return Math.Max(1, (int)Math.Round(maxHitPoints * f));
        }

        // Every placed piece keeps minSpacing from every other and startClearance from the map centre (where the
        // player usually lands).
        public static bool Spaced(int x, int z, int[] xs, int[] zs, int n, float minSpacing, int cx, int cz, float startClearance)
        {
            float dx0 = x - cx, dz0 = z - cz;
            if (dx0 * dx0 + dz0 * dz0 < startClearance * startClearance) return false;
            for (int i = 0; i < n; i++)
            {
                float dx = x - xs[i], dz = z - zs[i];
                if (dx * dx + dz * dz < minSpacing * minSpacing) return false;
            }
            return true;
        }

        // A smother claim found mid-cycle: started somewhere in the first 20-80% of its length before now, never before
        // tick 0 (the claim clock treats a negative start as "not smothered"). PROVISIONAL.
        public static int MidCycleStart(int now, int claimTicks, double roll)
        {
            double back = claimTicks * (0.2 + 0.6 * Math.Max(0.0, Math.Min(1.0, roll)));
            long start = (long)now - (long)Math.Round(back);
            return start < 0 ? 0 : (int)start;
        }
    }
}
