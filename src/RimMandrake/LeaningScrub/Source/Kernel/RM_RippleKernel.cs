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
        public const int CheckInterval = 120;

        public static float SizeLimit(float maxBodySize, bool gale)
        {
            if (maxBodySize < 0f) maxBodySize = 0f;
            return gale ? maxBodySize * 2f : maxBodySize;
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
