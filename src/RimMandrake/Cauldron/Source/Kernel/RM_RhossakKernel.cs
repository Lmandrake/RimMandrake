// Verse-free kernel of the rhossak grove (RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD, owner by card 2026-10-19: "Make them animals and make them
// bind."): which grove tree a rhossak binds to, when three standing together have stood long enough to root a new grove,
// and the per-check chance that a resting rhossak sprouts the ground. RM_CompRhossakGrove.cs calls these with the same
// expressions; SelfTest/CauldronFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;

namespace RimMandrake.Cauldron
{
    public static class RM_RhossakKernel
    {
        public const int TicksPerHour = 2500;
        public const int TicksPerDay = 60000;

        // Index of the nearest usable candidate (squared horizontal distance), -1 if none. Ties go to the lowest index.
        public static int NearestIndex(int px, int pz, int[] xs, int[] zs, bool[] usable)
        {
            int best = -1;
            long bestD = long.MaxValue;
            for (int i = 0; i < xs.Length; i++)
            {
                if (!usable[i]) continue;
                long dx = xs[i] - px, dz = zs[i] - pz;
                long d = dx * dx + dz * dz;
                if (d < bestD) { bestD = d; best = i; }
            }
            return best;
        }

        public static bool Within(int dx, int dz, float radius)
        {
            return radius >= 0f && (float)dx * dx + (float)dz * dz <= radius * radius;
        }

        // Rooting is armed only for a seed-bearing rhossak that is awake, has enough kin beside it, stands clear of every
        // existing grove tree and is off its cooldown. `companions` excludes the rhossak itself.
        public static bool Together(bool enabled, bool seedBearing, bool awake, int companions, int groupSize, bool spacingClear,
            bool cooledDown)
        {
            return enabled && seedBearing && awake && companions + 1 >= groupSize && spacingClear && cooledDown;
        }

        // "Long enough" is CONTIGUOUS time together: any check apart resets the count. Saturates instead of overflowing.
        public static int StepTogether(int acc, bool together, int delta)
        {
            if (!together || delta <= 0) return together ? acc : 0;
            long next = (long)acc + delta;
            return next > int.MaxValue ? int.MaxValue : (int)next;
        }

        // RHOSSAK A6 (2026-10-20): "standing together long enough" must be reachable by an animal that sleeps every day. With
        // StepTogether alone any sleep reset the count, so 24 unbroken AWAKE hours never happened and no grove could ever
        // root. A stretch is now broken only by being APART (or a gate failing): awake together advances it, asleep together
        // (`held`: the same group, spacing and cooldown, the rhossak resting) holds it where it was.
        public static int StepTogetherHeld(int acc, bool together, bool held, int delta)
        {
            if (together) return StepTogether(acc, true, delta);
            return held ? acc : 0;
        }

        public static int RootTicks(float rootHours)
        {
            return rootHours <= 0f ? 1 : (int)Math.Ceiling(rootHours * TicksPerHour);
        }

        public static bool ShouldRoot(int acc, float rootHours)
        {
            return acc >= RootTicks(rootHours);
        }

        public static bool CooledDown(int now, int lastRootTick, float cooldownDays)
        {
            return lastRootTick < 0 || (long)now - lastRootTick >= (long)Math.Ceiling(cooldownDays * TicksPerDay);
        }

        // Chance per check of an event with mean time between `mtbHours`, sampled every `intervalTicks`.
        public static float ChancePerCheck(float mtbHours, int intervalTicks)
        {
            if (mtbHours <= 0f || intervalTicks <= 0) return 0f;
            return (float)(1.0 - Math.Exp(-(double)intervalTicks / (mtbHours * TicksPerHour)));
        }

        // RHOSSAK A3: the inspect-pane line. Bind OFF -> no line at all, whatever the comp still remembers (a plain wild
        // animal; "all-off degrades gracefully"); ON -> bound to the named tree, or unbound when none is valid.
        public const string BoundPrefix = "Bound to ";
        public const string UnboundLine = "Unbound: no grove tree on this map";

        public static string BindLine(bool bindEnabled, bool treeValid, string treeLabel)
        {
            if (!bindEnabled) return null;
            return treeValid ? BoundPrefix + treeLabel : UnboundLine;
        }

        public static bool ShouldSprout(bool enabled, bool seedBearing, bool resting, float roll, float chance)
        {
            return enabled && seedBearing && resting && roll < chance;
        }
    }
}
