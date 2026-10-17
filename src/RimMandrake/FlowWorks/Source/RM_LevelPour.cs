using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// Where poured or displaced DECILITRES go in exact-level water (PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY,
	/// HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES, CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED). Owner: <i>"conservation of mass is true
	/// everywhere"</i>; filling in <i>"does not destroy liquid if there's a place for it to go"</i>.
	///
	/// Under P3 a canal holds a sheet (a part-notch), so no square of it has a WHOLE notch of room; every whole-notch writer
	/// (pump outflow, pour, hose drain, fill-in displacement) was refused or destroyed the water. Water poured into one square
	/// of a canal spreads over the squares it joins (the pulse then lays it level), so a writer asks this walk instead:
	/// the start square first, then the dug squares reached through it, nearest first (breadth-first, cardinal order N E S W),
	/// each up to its room in dL. Verse-free: the SelfTest compiles this file and the oracle differential
	/// (selftest_flowworks_kernel_oracle.py, mode "exactops") checks it against northstar/level_water.py's <c>spread</c>.
	/// </summary>
	public static class RM_LevelPour
	{
		/// <summary>The squares a POUR walks before it calls the canal full (a pump asks every cycle; displacement walks the map).</summary>
		public const int PourWalkCap = 1024;

		/// <summary>
		/// Plan up to <paramref name="dl"/> decilitres from <paramref name="start"/>. <paramref name="creditStart"/>: the start
		/// square takes water itself (a pour) or only conducts (a fill-in's own square). <paramref name="neighbour"/>(i, dir)
		/// is the cardinal neighbour (dir 0..3 = N E S W) or -1; <paramref name="enter"/>(i) says the walk may step onto i;
		/// <paramref name="isSource"/>(i) marks a pond square, collected into <paramref name="sources"/> (nearest first, never
		/// expanded through, never credited here); <paramref name="room"/>(i) is i's room in dL (0 = takes nothing but still
		/// conducts). Read-only: fills <paramref name="credits"/> (square, dL) and returns the dL placed.
		/// </summary>
		public static long Spread(int start, long dl, bool creditStart, Func<int, int, int> neighbour, Func<int, bool> enter,
			Func<int, bool> isSource, Func<int, long> room, int cap, List<KeyValuePair<int, long>> credits, List<int> sources)
		{
			credits?.Clear();
			sources?.Clear();
			if (dl <= 0 || start < 0)
			{
				return 0;
			}
			long remaining = dl;
			var seen = new HashSet<int> { start };
			var queue = new Queue<int>();
			queue.Enqueue(start);
			int walked = 0;
			while (queue.Count > 0 && remaining > 0 && walked < cap)
			{
				int c = queue.Dequeue();
				walked++;
				if (c != start || creditStart)
				{
					if (c != start && isSource != null && isSource(c))
					{
						sources?.Add(c);
						continue;
					}
					long r = room(c);
					if (r > 0)
					{
						long take = r < remaining ? r : remaining;
						credits?.Add(new KeyValuePair<int, long>(c, take));
						remaining -= take;
					}
				}
				for (int d = 0; d < 4; d++)
				{
					int n = neighbour(c, d);
					if (n < 0 || seen.Contains(n))
					{
						continue;
					}
					if (enter(n))
					{
						seen.Add(n);
						queue.Enqueue(n);
					}
				}
			}
			return dl - remaining;
		}

		/// <summary>The water a square keeps when its hole is raised from <paramref name="depth"/> to <paramref name="newDepth"/>
		/// notches (0 = filled to the surface, or back to a pond bed: it keeps nothing). Water above the new floor's brim is
		/// displaced; a sheet under the new brim simply sits higher (no loss, nothing moves).</summary>
		public static long KeptOnFillIn(long water, int newDepth, bool toSurface)
		{
			if (toSurface || newDepth <= 0 || water <= 0)
			{
				return 0;
			}
			long brim = newDepth * (long)RM_LevelSolve.U;
			return water < brim ? water : brim;
		}
	}
}
