// Verse-free small rules of TerminalBiomes: the Sunk hediff rate and scar latch, the wax procession's sheet timer and the
// veil-fall scheduler. SelfTest/TerminalBiomesFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.TerminalBiomes
{
    public static class RM_TerminalMiscKernel
    {
        public const int SunkEvalInterval = 200;

        // Severity change per evaluation: unrescued rises, rescued (roofed) falls; both scaled from per-day to the interval.
        public static float SunkStep(bool rescued, float perDayUnrescued, float perDayRescued, int ticksPerDay, int interval)
        {
            return (rescued ? perDayRescued : perDayUnrescued) / ticksPerDay * interval;
        }

        // The permanent scar lands once, when a rescue (if the setting asks for scars) brings severity to 0.05 or below.
        public static bool ScarDue(bool rescued, bool scarOnRescue, bool scarApplied, float severity) { return rescued && scarOnRescue && !scarApplied && severity <= 0.05f; }

        // Wax procession: counts down on rare ticks; at zero it waits for a pause (not walking) and then drops a sheet and re-arms.
        public static bool WaxStep(ref int ticksLeft, int period, int rareInterval, bool moving)
        {
            if (ticksLeft < 0) ticksLeft = period;
            ticksLeft -= rareInterval;
            if (ticksLeft > 0) return false;
            if (moving) { ticksLeft = 0; return false; }   // overdue: hold at zero; a negative value means "uninitialised" above
            ticksLeft = period;
            return true;
        }

        // Veil-fall: the first call arms both timers (jittered); afterwards each fires when due and re-arms one interval on.
        public static void VeilStep(ref int nextShed, ref int nextDeck, int now, int interval, Func<int, int> randBelow, out bool shed, out bool deck)
        {
            shed = false; deck = false;
            if (nextShed < 0)
            {
                nextShed = now + interval + randBelow(interval);
                nextDeck = now + interval + randBelow(interval);
                return;
            }
            if (now >= nextShed) { nextShed = now + interval; shed = true; }
            if (now >= nextDeck) { nextDeck = now + interval; deck = true; }
        }
    }
}
