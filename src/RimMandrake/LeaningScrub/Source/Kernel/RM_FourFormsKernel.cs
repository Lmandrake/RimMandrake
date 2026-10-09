// Verse-free kernel of the four further venomvine forms (RM_VenomvineFourForms.cs): strangler wrap, weeper pools, sleeper wake, lure fruit.
// SelfTest/LeaningScrubFourFormsCheck.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.LeaningScrub
{
    public static class RM_FourFormsKernel
    {
        // ── strangler ──
        // Wrap progress climbs by `step` per long tick toward 1. A fresh target restarts at 0.
        public static float WrapProgress(float progress, float step)
        {
            float p = progress + Math.Max(0f, step);
            return p > 1f ? 1f : (p < 0f ? 0f : p);
        }

        // A fresh wrap squeezes at a quarter of full strength; a full one at full strength.
        public static float WrapDamage(float progress, float fullDamage)
        {
            float p = progress < 0f ? 0f : (progress > 1f ? 1f : progress);
            return Math.Max(0f, fullDamage) * (0.25f + 0.75f * p);
        }

        // Only a grown stand wraps; off means a plain stand.
        public static bool Wraps(bool on, float growth, float minGrowth) { return on && growth >= minGrowth; }

        // ── weeper ──
        // A pool is shed on a long tick with `chance`; pollution stops at the stand's cap.
        public static bool WeepsNow(bool on, float growth, float minGrowth, double roll, float chance) { return on && growth >= minGrowth && roll < chance; }
        public static int PollutionRoom(int polluted, int cap) { return Math.Max(0, cap - Math.Max(0, polluted)); }

        // ── sleeper ──
        // Wakes on a grounded body of at least `minBody` next to it; a hare walking past does not.
        public static bool Wakes(bool on, bool asleep, float bodySize, float minBody, bool flying, bool dead)
        {
            return on && asleep && !flying && !dead && bodySize >= minBody;
        }

        // ── lure ──
        // Drops a fruit while the stand is grown and fewer than `cap` lie within reach.
        public static bool DropsFruit(bool on, float growth, float minGrowth, int fruitNearby, int cap)
        {
            return on && growth >= minGrowth && fruitNearby < cap;
        }
    }
}
