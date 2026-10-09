// Verse-free kernel of the Grey Sea's hull crust (RM_MapComponent_GreyHullCrust): the effective-parked-days clock, its
// multipliers, the rime / salted-door / crust schedule and the chip rewind. The mod supplies the hull, doors and spawning.
// SelfTest/TerminalBiomesFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.TerminalBiomes
{
    public static class RM_CrustKernel
    {
        public const float RimeDays = 1f, FirstDoorDays = 2.5f, DoorIntervalDays = 1f, CrustStartDays = 5f, CrustFullDays = 15f, ChipRewindDays = 0.25f;
        public const int CheckInterval = 2500;

        public static float Multiplier(float rate, bool saltSnow, float saltSnowMultiplier, bool brineBerth, float berthMultiplier)
        {
            float m = rate;
            if (saltSnow) m *= saltSnowMultiplier;
            if (brineBerth) m *= berthMultiplier;
            return m;
        }

        public static float AddDays(int interval, float multiplier) { return interval / 60000f * multiplier; }

        // Chance per pass of one more crust patch: 10% at the start day, 100% at the full day.
        public static float CrustChance(float crustDays)
        {
            float ramp = (crustDays - CrustStartDays) / (CrustFullDays - CrustStartDays);
            ramp = ramp < 0f ? 0f : (ramp > 1f ? 1f : ramp);
            return 0.1f + 0.9f * ramp;
        }

        // CRUST_NEVER_STRANDS_1: the tear-free launch damages a hull building by `fraction` of its max HP, never to death
        // (it leaves at least 1 HP) so the rip costs repairs but cannot delete the base.
        public static int TearDamage(int hp, int maxHp, float fraction)
        {
            int d = (int)Math.Round(maxHp * (double)fraction);
            return Math.Max(0, Math.Min(d, hp - 1));
        }

        public static int CrustCap(int hullCells) { return Math.Max(1, hullCells / 3); }

        // One pass: advance the clock, then report what is due. A rime roll is made only once rime is possible and the crust
        // roll only once crust is; doors come one per interval crossed (several if a big step crosses several).
        public static void Step(ref float crustDays, ref float nextDoorAt, float addDays, bool rimeDefExists, bool crustDefExists, Func<float, bool> chance,
            out bool rime, out int doors, out bool crust)
        {
            crustDays += addDays;
            rime = crustDays >= RimeDays && rimeDefExists && chance(0.5f);
            doors = 0;
            while (crustDays >= nextDoorAt) { nextDoorAt += DoorIntervalDays; doors++; }
            crust = crustDays >= CrustStartDays && crustDefExists && chance(CrustChance(crustDays));
        }

        // Chipping the crust rewinds the clock and the next door together.
        public static void Rewind(ref float crustDays, ref float nextDoorAt)
        {
            crustDays = Math.Max(0f, crustDays - ChipRewindDays);
            nextDoorAt = Math.Max(FirstDoorDays, nextDoorAt - ChipRewindDays);
        }
    }
}
