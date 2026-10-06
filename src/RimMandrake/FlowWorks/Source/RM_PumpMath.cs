namespace RimMandrake.FlowWorks
{
	/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 8: the pump's numbers (Verse-free, selftested). PROVISIONAL.</summary>
	public static class RM_PumpMath
	{
		/// <summary>One cycle per 250 ticks — the flow pulse's own cadence.</summary>
		public const int CycleTicks = 250;

		/// <summary>The unit bridge between the channel ledger (levels) and the tank ledger (units):
		/// a channel level is a bucket's worth (5 units).</summary>
		public const int TankUnitsPerLevel = 5;

		/// <summary>Levels a pump moves in a day of running (60000 ticks).</summary>
		public static int LevelsPerDay()
		{
			return 60000 / CycleTicks;
		}

		/// <summary>Cycles a full default tank (300 units) takes to fill from nothing.</summary>
		public static int CyclesToFill(int tankUnits)
		{
			if (tankUnits <= 0) return 0;
			return (tankUnits + TankUnitsPerLevel - 1) / TankUnitsPerLevel;
		}
	}
}
