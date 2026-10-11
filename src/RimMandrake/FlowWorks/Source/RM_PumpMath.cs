using System.Collections.Generic;

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

		/// <summary>
		/// P11 (GPT review G1.22): squared distance from cell (x,z) to the NEAREST cell of the footprint
		/// [minX..maxX]×[minZ..maxZ]; 0 inside it. A station's reach is measured from its footprint, so a
		/// 3×2 station reaches the same number of cells off every side. The old rule measured a circle of
		/// reach + width/2 from Position, which on an even-sized footprint reached one cell further off one
		/// side than the other and ignored height entirely.
		/// </summary>
		public static int FootprintDistSq(int minX, int minZ, int maxX, int maxZ, int x, int z)
		{
			int dx = x < minX ? minX - x : (x > maxX ? x - maxX : 0);
			int dz = z < minZ ? minZ - z : (z > maxZ ? z - maxZ : 0);
			return dx * dx + dz * dz;
		}

		/// <summary>P11: true when (x,z) lies outside the footprint and within reach of it.</summary>
		public static bool InFootprintReach(int minX, int minZ, int maxX, int maxZ, int x, int z, float reach)
		{
			int d = FootprintDistSq(minX, minZ, maxX, maxZ, x, z);
			return d > 0 && d <= reach * reach;
		}

		/// <summary>Cycles a full default tank (300 units) takes to fill from nothing.</summary>
		public static int CyclesToFill(int tankUnits)
		{
			if (tankUnits <= 0) return 0;
			return (tankUnits + TankUnitsPerLevel - 1) / TankUnitsPerLevel;
		}
	
		/// <summary>
		/// P1 (hose port step 5; GPT review G1.14): the (tank, cell) pair a pour uses. Tanks in net order; a tank that can
		/// provide a level and whose liquid has a channel form is paired with the deepest-emptiest COMPATIBLE excavated cell in
		/// reach (a cell holding another liquid is skipped before ranking, GPT FlowWorks review #20); the first tank with any
		/// such cell wins. The old rule took the first channel-capable tank and stopped there, so a water tank first on the
		/// net starved a tar tank beside a tar channel. False when no pair exists.
		/// </summary>
		public static bool PickPour<T>(IList<(bool canProvide, T fluid)> tanks, IList<(int room, bool wet, T fill)> cells,
		                               out int tank, out int cell) where T : class
		{
			tank = cell = -1;
			for (int t = 0; t < tanks.Count; t++)
			{
				if (!tanks[t].canProvide || tanks[t].fluid == null)
				{
					continue;
				}
				int best = -1, bestRoom = 0;
				for (int c = 0; c < cells.Count; c++)
				{
					if (!RM_StockMath.FluidsCompatible(cells[c].wet, cells[c].fill, tanks[t].fluid))
					{
						continue;
					}
					if (cells[c].room > bestRoom)
					{
						best = c;
						bestRoom = cells[c].room;
					}
				}
				if (best >= 0)
				{
					tank = t;
					cell = best;
					return true;
				}
			}
			return false;
		}
	}
}
