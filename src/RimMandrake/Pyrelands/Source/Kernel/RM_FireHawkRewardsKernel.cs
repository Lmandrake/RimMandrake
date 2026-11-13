using System;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-hawk's two hunt rewards (FireHawkRewards.cs): the once-per-game letter the first time a
    // player sees a hawk carrying an ember, and the crestfeather's flat butcher chance. Owner, 2026-11-13: "That gives a great
    // reason for players to hunt the Firehawk." The offline fuzz (family rewards) drives these same functions.

    public static class RM_FireHawkRewardsKernel
    {
        /// <summary>How often the sighting component looks at the player's home maps: four times a game hour, never per tick.
        /// An ember carry lasts many seconds of flight, so a 250-tick look cannot miss one.</summary>
        public const int SightingLookIntervalTicks = 250;

        public static bool LookThisTick(int ticksGame)
        {
            return ticksGame % SightingLookIntervalTicks == 0;
        }

        /// <summary>The first-sighting gate, called once per hawk per look. Sends (returns true, and sets the saved flag) only for
        /// a hawk carrying an ember, visible (not fogged), on a player home map, with the letter toggle and the Pyrelands master
        /// on, and only while no letter has been sent this game. Every later call returns false.</summary>
        public static bool TryClaimSighting(ref bool announced, bool letterEnabled, bool mechanicsOn, bool carryingEmber,
            bool onPlayerHome, bool fogged)
        {
            if (announced || !letterEnabled || !mechanicsOn || !carryingEmber || !onPlayerHome || fogged)
            {
                return false;
            }
            announced = true;
            return true;
        }

        /// <summary>The letter's compass word: 0 north, 1 north-east ... 7 north-west, clockwise; +z is north on a RimWorld map.
        /// -1 for the same cell.</summary>
        public static int Compass8(int dx, int dz)
        {
            if (dx == 0 && dz == 0)
            {
                return -1;
            }
            double deg = (Math.Atan2(dx, dz) * 180.0 / Math.PI + 360.0) % 360.0;
            return (int)Math.Floor((deg + 22.5) / 45.0) % 8;
        }

        /// <summary>The crestfeather's flat chance: roll01 is one uniform draw in [0, 1) per butchered hawk.</summary>
        public static bool TrophyDrops(float roll01, float chance)
        {
            return chance > 0f && roll01 < chance;
        }
    }
}
