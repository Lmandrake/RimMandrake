// Verse-free kernel of the ripple (RM_Ripple.cs): who hides under the fuzz. SelfTest/LeaningScrubTonightCheck.cs compiles
// this file alone: no Verse/RimWorld/UnityEngine.
//
// Owner ruling Q9 (card, 2026-10-15): "Ripple -> Hiding with a faint shimmer". Item spec part 6: "canopy concealment as a
// weather-keyed field (strong in wind, doubled in Gale, cancelled by moving in the Stall)". Read as a binary hide:
//   wind  : a small creature on a fuzz cell is hidden, moving or not;
//   Gale  : the size limit doubles (medium creatures hide too);
//   Stall : only a creature that holds still stays hidden; moving cancels it.
namespace RimMandrake.LeaningScrub
{
    public static class RM_RippleKernel
    {
        public const int CheckInterval = 60; // ~1 s hide/show lag, accepted

        public static float SizeLimit(float maxBodySize, bool gale)
        {
            if (maxBodySize < 0f) maxBodySize = 0f;
            return gale ? maxBodySize * 2f : maxBodySize;
        }

        // Part 2 windbreak calm wakes: a cell is in a windbreak's lee when a wind-blocking edifice stands within wakeLength
        // cells upwind of it (stepping against the Lean heading). In the lee the wind is still, so the ripple behaves as
        // in the Stall there: a creature that moves is seen. PROVISIONAL wake length.
        public const int WakeLength = 4;

        public static bool InLee(int x, int z, float downwindX, float downwindZ, int wakeLength, System.Func<int, int, bool> blocksWind)
        {
            for (int k = 1; k <= wakeLength; k++)
            {
                // Rounded half away from zero (not RM_LeanKernel.Step's banker's rounding), so the sampled line does not
                // flip with k's parity on a tie heading.
                int ux = x + (int)System.Math.Round(-downwindX * k, System.MidpointRounding.AwayFromZero);
                int uz = z + (int)System.Math.Round(-downwindZ * k, System.MidpointRounding.AwayFromZero);
                if (ux == x && uz == z) continue;
                if (blocksWind(ux, uz)) return true;
            }
            return false;
        }

        public static bool Hidden(bool featureOn, bool wild, bool downed, bool onCover, float bodySize, float maxBodySize,
            bool gale, bool stall, bool moving)
        {
            if (!featureOn || !wild || downed || !onCover)
            {
                return false;
            }
            if (bodySize > SizeLimit(maxBodySize, gale))
            {
                return false;
            }
            return !(stall && moving);
        }
    }
}
