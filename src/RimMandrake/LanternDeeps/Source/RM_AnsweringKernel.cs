using System;

namespace RimMandrake.LanternDeeps
{
    /// <summary>
    /// LANTERNDEEPS_ANSWERING_RITE_BUILD_1: what each outcome of the Answering does, with no Verse type in it so the offline fuzz
    /// compiles THIS file. Spec: design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md section 6 R1.
    /// Poor: the droid stops and must be carried out. Fair: a settlement entry for the god. Good: plus a log line the droid did not
    /// write. Excellent: plus the line names where the next mindstone lies, and one is there. All amounts PROVISIONAL.
    /// </summary>
    public static class AnsweringKernel
    {
        public enum Tier { Poor = 0, Fair = 1, Good = 2, Excellent = 3 }

        /// <summary>RitualOutcomePossibility.positivityIndex: the XML uses -1 / 1 / 2 / 3.</summary>
        public static Tier TierOf(int positivityIndex)
        {
            if (positivityIndex < 1) return Tier.Poor;
            if (positivityIndex == 1) return Tier.Fair;
            if (positivityIndex == 2) return Tier.Good;
            return Tier.Excellent;
        }

        /// <summary>The god's delta: nothing on a poor rite (it is a failed attempt, not an offence), then rising.</summary>
        public static float GodDelta(Tier t, float fair, float good, float excellent)
        {
            switch (t)
            {
                case Tier.Fair: return Math.Max(0f, fair);
                case Tier.Good: return Math.Max(Math.Max(0f, fair), good);
                case Tier.Excellent: return Math.Max(Math.Max(Math.Max(0f, fair), good), excellent);
                default: return 0f;
            }
        }

        public static bool StallsDroid(Tier t) { return t == Tier.Poor; }
        public static bool WritesLogLine(Tier t) { return t >= Tier.Good; }
        public static bool NamesNextStone(Tier t) { return t == Tier.Excellent; }

        /// <summary>Index into the log-line table; stable for one seed, never out of range, -1 when the table is empty.</summary>
        public static int PickLine(int count, int seed)
        {
            if (count <= 0) return -1;
            return (int)((uint)(seed * 2654435761u) % (uint)count);
        }

        /// <summary>A stalled droid recovers once it is out of every mind's sight.</summary>
        public static bool StallHolds(bool anyMindInSight) { return anyMindInSight; }
    }
}
