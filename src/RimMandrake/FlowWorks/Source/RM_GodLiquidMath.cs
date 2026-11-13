using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN (the dev tools that drop large amounts of any liquid on the terrain or in a
	/// pit and take it away again): the arithmetic of the dev pour, drain and set-level tools (RM_GodLiquid), Verse-free so Source/SelfTest compiles it. Amounts are
	/// decilitres (RM_Volume.UnitsPerLitre); a plan is a list of (square index, signed dL), positive = poured, never over a
	/// square's brim or below empty; the caller moves the liquid through the engine and counts what it really moved.</summary>
	public static class RM_GodLiquidMath
	{
		private const long U = RM_LevelSolve.U;

		/// <summary>"Drain all": the amount a drain takes when it takes everything the body holds.</summary>
		public const long All = RM_SheetMath.AllDl;

		/// <summary>The largest pour or drain one click takes, in litres (a 16x16 pit 125 m deep is 64,000,000 L).</summary>
		public const double MaxLitres = 100000000.0;

		/// <summary>The deepest a set-level asks for, in metres (the deepest dug square, RM_ExcavationDepth's 125 m).</summary>
		public const double MaxLevelMetres = 125.0;

		/// <summary>A 16x16 pit 4 m deep, brim full: 256 squares x 8 notches x 1,000 L.</summary>
		public const long FullPit16x16x4mLitres = 16L * 16L * 8L * RM_Volume.LitresPerNotch;

		/// <summary>The pour and drain sizes the debug menu offers, in litres.</summary>
		public static readonly long[] PourLitreSteps = { 100, 1000, 10000, 100000, 500000, 1000000, FullPit16x16x4mLitres, 10000000 };

		/// <summary>The levels the set-level menu offers, in metres of liquid at the clicked square (0 = drain it dry).</summary>
		public static readonly float[] LevelMetreSteps = { 0f, 0.25f, 0.5f, 1f, 1.5f, 2f, 3f, 4f, 6f, 8f, 12f, 16f };

		/// <summary>Null when <paramref name="litres"/> is a pour or drain amount, else why not; <paramref name="dl"/> is the amount
		/// in whole decilitres (0 on a refusal).</summary>
		public static string CheckLitres(double litres, out long dl)
		{
			dl = 0;
			if (double.IsNaN(litres) || double.IsInfinity(litres))
			{
				return "REFUSED: the amount is not a number (" + litres + ")";
			}
			if (litres <= 0)
			{
				return "REFUSED: the amount must be more than 0 L (got " + litres + " L); use a drain to remove liquid";
			}
			if (litres > MaxLitres)
			{
				return "REFUSED: " + litres + " L is more than one click moves (" + MaxLitres + " L)";
			}
			long d = (long)Math.Round(litres * RM_Volume.UnitsPerLitre);
			if (d <= 0)
			{
				return "REFUSED: " + litres + " L is less than the smallest amount (0.1 L)";
			}
			dl = d;
			return null;
		}

		/// <summary>Null when <paramref name="metres"/> is a level to set (0 = dry), else why not; <paramref name="dl"/> is that depth
		/// of liquid on one square, in decilitres.</summary>
		public static string CheckLevelMetres(double metres, out long dl)
		{
			dl = 0;
			if (double.IsNaN(metres) || double.IsInfinity(metres) || metres < 0)
			{
				return "REFUSED: the level must be 0 m or more (got " + metres + " m)";
			}
			if (metres > MaxLevelMetres)
			{
				return "REFUSED: " + metres + " m is deeper than any pit (" + MaxLevelMetres + " m)";
			}
			dl = (long)Math.Round(metres / RM_Volume.MetresPerNotch * U);
			return null;
		}

		/// <summary>Null when (x, z) is on a w x h map, else the refusal.</summary>
		public static string CheckCell(int x, int z, int w, int h)
		{
			return x >= 0 && z >= 0 && x < w && z < h ? null : "REFUSED: (" + x + ", " + z + ") is off the map (" + w + " x " + h + ")";
		}

		/// <summary>Null when <paramref name="name"/> is one of <paramref name="known"/> (case does not matter), with its
		/// <paramref name="index"/>; else the refusal, naming every liquid there is (index -1).</summary>
		public static string ResolveLiquid(string name, IList<string> known, out int index)
		{
			index = -1;
			if (!string.IsNullOrEmpty(name))
			{
				for (int i = 0; i < known.Count; i++)
				{
					if (string.Equals(known[i], name, StringComparison.OrdinalIgnoreCase))
					{
						index = i;
						return null;
					}
				}
			}
			return "REFUSED: no liquid named '" + (name ?? "") + "'; the liquids are " + string.Join(", ", known);
		}

		/// <summary>The squares of the body at <paramref name="start"/>, nearest first (breadth-first over the four cardinal
		/// <paramref name="neighbour"/>s, -1 = none), each one <paramref name="joins"/> accepts; empty when the start itself is not
		/// accepted. At most <paramref name="cap"/> squares.</summary>
		public static List<int> Walk(int start, Func<int, int, int> neighbour, Func<int, bool> joins, int cap)
		{
			var order = new List<int>();
			if (start < 0 || cap <= 0 || !joins(start))
			{
				return order;
			}
			var seen = new HashSet<int> { start };
			order.Add(start);
			for (int head = 0; head < order.Count && order.Count < cap; head++)
			{
				for (int dir = 0; dir < 4 && order.Count < cap; dir++)
				{
					int j = neighbour(order[head], dir);
					if (j >= 0 && seen.Add(j) && joins(j))
					{
						order.Add(j);
					}
				}
			}
			return order;
		}

		private static long Whole(long dl, bool whole) => whole ? dl - dl % U : dl;

		/// <summary>Plan a pour of up to <paramref name="want"/> dL over <paramref name="order"/>: each square up to its
		/// <paramref name="room"/>, nearest first (whole notches only when <paramref name="whole"/>). Returns the dL planned; the
		/// rest had no room.</summary>
		public static long PlanPour(IList<int> order, Func<int, long> room, long want, bool whole, List<KeyValuePair<int, long>> plan)
		{
			long left = Whole(want, whole);
			long placed = 0;
			for (int k = 0; k < order.Count && left > 0; k++)
			{
				long put = Whole(Math.Min(Math.Max(0, room(order[k])), left), whole);
				if (put > 0)
				{
					plan.Add(new KeyValuePair<int, long>(order[k], put));
					placed += put;
					left -= put;
				}
			}
			return placed;
		}

		/// <summary>Plan a drain of up to <paramref name="want"/> dL (<see cref="All"/> = everything) over <paramref name="order"/>,
		/// nearest first, each square down to empty (whole notches only when <paramref name="whole"/>). Any other amount at or below
		/// 0 plans nothing. Returns the dL planned (the plan's entries are negative).</summary>
		public static long PlanTake(IList<int> order, Func<int, long> water, long want, bool whole, List<KeyValuePair<int, long>> plan)
		{
			bool all = want == All;
			if (!all && want <= 0)
			{
				return 0;
			}
			long left = all ? long.MaxValue : Whole(want, whole);
			long took = 0;
			for (int k = 0; k < order.Count && left > 0; k++)
			{
				long take = Whole(Math.Min(Math.Max(0, water(order[k])), left), whole);
				if (take > 0)
				{
					plan.Add(new KeyValuePair<int, long>(order[k], -take));
					took += take;
					left -= take;
				}
			}
			return took;
		}

		/// <summary>Plan "set this pit to level X": <paramref name="targetDl"/> of liquid on the clicked square (floor
		/// <paramref name="clickedDepth"/> notches down) and the same surface across <paramref name="order"/>, so a square
		/// d notches deeper holds d notches more; every square clamped to empty..brim (whole notches only when
		/// <paramref name="whole"/>). Drains come first in the plan. Returns the net dL (positive = poured).</summary>
		public static long PlanLevel(IList<int> order, Func<int, int> depthNotches, Func<int, long> water, int clickedDepth, long targetDl,
			bool whole, List<KeyValuePair<int, long>> plan)
		{
			long surface = Whole(Math.Max(0, targetDl), whole) - clickedDepth * U;   // liquid surface, dL relative to the brim
			var pours = new List<KeyValuePair<int, long>>();
			long net = 0;
			for (int k = 0; k < order.Count; k++)
			{
				int i = order[k];
				long brim = Math.Max(0, depthNotches(i)) * U;
				long want = Whole(Math.Max(0, Math.Min(brim, brim + surface)), whole);
				long delta = want - water(i);
				if (delta == 0)
				{
					continue;
				}
				(delta < 0 ? plan : pours).Add(new KeyValuePair<int, long>(i, delta));
				net += delta;
			}
			plan.AddRange(pours);
			return net;
		}

		/// <summary>A pour/drain step as the menu shows it ("2,048,000 L (16x16 pit, 4 m)").</summary>
		/// <summary>The first square of <paramref name="order"/> (the click, then outward) that <paramref name="wet"/> holds, or -1:
		/// where a drain on undug ground starts when the clicked square itself is dry (RIMMANDRAKE_LET_GROUND_DRAIN_ALL_FIND_SPILL_EMPTY_CLICK:
		/// a part drain empties the clicked square first, and the rest of the spill lies around it).</summary>
		public static int NearestWet(IList<int> order, Func<int, bool> wet)
		{
			for (int k = 0; k < order.Count; k++)
			{
				if (wet(order[k]))
				{
					return order[k];
				}
			}
			return -1;
		}

		public static string StepLabel(long litres)
		{
			string s = RM_Volume.FormatLitres(litres);
			return litres == FullPit16x16x4mLitres ? s + " (a 16x16 pit 4 m deep)" : s;
		}
	}
}
