namespace RimMandrake.CreatureBehaviors
{
    /// <summary>Why a wild animal is walking off the map, in the terms vanilla's own
    /// LeaveIfWrongSeason / LeaveIfStarving think trees use. Pure, so the SelfTest
    /// can check it without the game (WILD_LEAVE_NOTICE, CHILL_CREATURES_VANISH_1).</summary>
    public enum RM_WildLeaveReason
    {
        None,
        TooWarm,
        TooCold,
        Starving,
    }

    public static class RM_WildLeaveMath
    {
        /// <summary>Vanilla ThinkNode_ConditionalAnimalWrongSeason is
        /// !MapTemperature.SeasonAcceptableFor(race): seasonal temp must lie strictly
        /// inside (ComfyMin, ComfyMax). ThinkNode_ConditionalDangerousTemperature reads
        /// the pawn's own ambient against its SafeTemperatureRange. Either sends the
        /// animal to JobGiver_ExitMapRandom; starving sends it via LeaveIfStarving.</summary>
        public static RM_WildLeaveReason Classify(float seasonalTemp, float comfyMin, float comfyMax,
            float ambientTemp, float safeMin, float safeMax, bool starving)
        {
            if (seasonalTemp >= comfyMax) return RM_WildLeaveReason.TooWarm;
            if (seasonalTemp <= comfyMin) return RM_WildLeaveReason.TooCold;
            if (ambientTemp > safeMax) return RM_WildLeaveReason.TooWarm;
            if (ambientTemp < safeMin) return RM_WildLeaveReason.TooCold;
            if (starving) return RM_WildLeaveReason.Starving;
            return RM_WildLeaveReason.None;
        }

        /// <summary>One notice per species per map per window, so a group of eight
        /// leaving together reads as one line, not eight.</summary>
        public static bool ShouldNotify(int nowTick, int lastNotifiedTick, int windowTicks)
        {
            return lastNotifiedTick < 0 || nowTick - lastNotifiedTick >= windowTicks;
        }
    }
}
