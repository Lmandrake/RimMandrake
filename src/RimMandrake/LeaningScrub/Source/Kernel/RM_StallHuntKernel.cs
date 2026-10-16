// Verse-free kernel of the Stall hunter (RM_StallHunt.cs). SelfTest/LeaningScrubTonightCheck.cs compiles this file alone.
//
// Item spec part 1: "Stall: wind dies, small fauna freeze, stallhawk (RM_Zellik) rises". Bedazzle slate: "hunts by
// canopy twitch, useless in wind, lethal in the Stall". Useless-in-wind needs no code: in wind the ripple hides its prey
// under the fuzz (RM_RippleKernel), so vanilla predator hunting cannot target it. Lethal-in-the-Stall is this kernel: while
// the Stall holds, an idle stall hunter is sent after the nearest visible small creature whether it is hungry or not.
// Numbers PROVISIONAL (owner ruling 2026-10-03).
namespace RimMandrake.LeaningScrub
{
    public static class RM_StallHuntKernel
    {
        public const int PassInterval = 500;
        public const float SearchRadius = 45f;

        public static bool Hunts(bool featureOn, bool stall, bool wild, bool awake, bool downed, bool inMentalState, bool alreadyHunting)
        {
            return featureOn && stall && wild && awake && !downed && !inMentalState && !alreadyHunting;
        }

        // Prey: a wild animal of another kind, small enough (at most maxPreyBodySize), alive and not hidden.
        public static bool Prey(bool wild, bool sameKind, bool dead, bool invisible, float bodySize, float maxPreyBodySize)
        {
            return wild && !sameKind && !dead && !invisible && bodySize <= maxPreyBodySize;
        }
    }
}
