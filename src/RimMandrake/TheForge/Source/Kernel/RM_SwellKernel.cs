// Verse-free kernel of the dhoggur's chemical swell (DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB, owner 2026-10-16):
// harm it and it swells to three times its size, spitting fire, for a third of a day; the swell cannot come again
// for a full day counted from the moment it ENDS. RM_CompDhoggurSwell calls these with the same expressions;
// SelfTest/TheForgeFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;

namespace RimMandrake.TheForge
{
    public struct SwellState
    {
        public int swellEndTick;      // -1 when not swollen
        public int cooldownUntilTick; // the first tick a new swell may begin
    }

    public static class RM_SwellKernel
    {
        public const int TicksPerHour = 2500;
        public const int TicksPerDay = 60000;

        public static bool Swollen(SwellState s) { return s.swellEndTick >= 0; }

        // Owner card 2026-10-16: the trigger is ONLY taking damage. damageDealt is ThingComp.PostPostApplyDamage's
        // totalDamageDealt, so a hit the hide absorbs completely does not count.
        public static bool CanSwell(SwellState s, bool enabled, bool dead, float damageDealt, int now)
        {
            return enabled && !dead && damageDealt > 0f && !Swollen(s) && now >= s.cooldownUntilTick;
        }

        public static int DurationTicks(float hours) { return Math.Max(1, (int)Math.Round(hours * TicksPerHour)); }
        public static int CooldownTicks(float days) { return Math.Max(0, (int)Math.Round(days * TicksPerDay)); }

        public static void Begin(ref SwellState s, int now, int durationTicks)
        {
            s.swellEndTick = now + Math.Max(1, durationTicks);
        }

        // True when the swell must end on this check: its time is up, or the mechanic was switched off (shrinks at once).
        public static bool ShouldEnd(SwellState s, bool enabled, int now)
        {
            return Swollen(s) && (!enabled || now >= s.swellEndTick);
        }

        // Card: the day of cooldown is counted FROM THE MOMENT THE SWELL ENDS (end tick + cooldown).
        public static void End(ref SwellState s, int now, int cooldownTicks)
        {
            s.swellEndTick = -1;
            s.cooldownUntilTick = now + Math.Max(0, cooldownTicks);
        }

        public static int TicksLeft(SwellState s, int now) { return Swollen(s) ? Math.Max(0, s.swellEndTick - now) : 0; }
        public static int CooldownLeft(SwellState s, int now) { return Swollen(s) ? 0 : Math.Max(0, s.cooldownUntilTick - now); }

        // One scale for body size, health and melee damage (card: "REAL: triple body size, health and damage").
        public static float Scale(bool swollen, float scaleSetting) { return swollen ? Math.Max(1f, scaleSetting) : 1f; }
    }
}
