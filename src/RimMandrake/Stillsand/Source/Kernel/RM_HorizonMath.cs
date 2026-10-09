namespace RimMandrake.Stillsand
{
    /// <summary>DUST_SETTLED_LETTER_1 (SS-3). Verse-free timing for an announced group: the storyteller queues it with a
    /// retry window (<see cref="RetryTicks"/>, the 1 h RM_HorizonWarning passes to IncidentQueue.Add), so the plume must
    /// stay up through that window, and a group still not arrived once it has closed is one that turned back.</summary>
    public static class RM_HorizonMath
    {
        public const int RetryTicks = 2500;     // GenDate.TicksPerHour, restated so the selftest needs no Verse
        public const int GraceTicks = 250;      // one queue tick burst past the window before we declare it gone

        /// <summary>Last tick the plume stands while the group has neither arrived nor been given up on.</summary>
        public static int PlumeUntil(int fireTick) => fireTick + RetryTicks + GraceTicks;

        /// <summary>True once the retry window is over and the group never arrived.</summary>
        public static bool TurnedBack(int now, int fireTick, bool arrived) => !arrived && now > PlumeUntil(fireTick);

        /// <summary>Does a TryFire(queued) result for this entry match an announced one (same def, same entry cell)?</summary>
        public static bool Matches(string recDef, int recX, int recZ, string def, int x, int z) =>
            !string.IsNullOrEmpty(recDef) && recDef == def && recX == x && recZ == z;
    }
}
