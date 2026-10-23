using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 8: the pump's numbers (Verse-free, selftested). PROVISIONAL.</summary>
	public static class RM_PumpMath
	{
		/// <summary>One cycle per 250 ticks — the flow pulse's own cadence.</summary>
		public const int CycleTicks = 250;

		/// <summary>The unit bridge between the channel ledger (levels) and the tank ledger (units). An alias of
		/// <see cref="RM_Volume.UnitsPerLevel"/> since POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK (one yardstick, one place).</summary>
		public const int TankUnitsPerLevel = RM_Volume.UnitsPerLevel;

		/// <summary>
		/// PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY (ruling Q3, <i>"Keep it as faster draining"</i>): the levels a pump on Pour
		/// moves per cycle. A Dump tank drains <paramref name="dumpUnitsPerCycle"/> units per settle with no pump, so a pouring
		/// pump moves at least one level more than that gravity rate, whatever the Mod Settings slider says; a station already
		/// faster keeps its own <paramref name="levelsPerCycle"/>; both are in notches (1,000 L) and decilitres. Never below 1.
		/// </summary>
		public static int PourLevels(int levelsPerCycle, int dumpUnitsPerCycle)
		{
			int gravityLevels = System.Math.Max(0, dumpUnitsPerCycle) / TankUnitsPerLevel;
			return System.Math.Max(System.Math.Max(1, levelsPerCycle), gravityLevels + 1);
		}

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: the decilitres a pump lifts from a dug cell this cycle: a notch
		/// (<paramref name="units"/>) when the cell holds one, else what it holds, so a thin sheet (4.5 cm = 900 dL) is pumped
		/// rather than stranded for want of a whole notch. 0 for a dry cell.</summary>
		public static int ChannelTakeUnits(int units, long cellDl)
		{
			if (units <= 0 || cellDl <= 0)
			{
				return 0;
			}
			return cellDl < units ? (int)cellDl : units;
		}

		/// <summary>POND_PUMP_FIX_LAST_DROP_COUNTS (owner by card 2026-10-22, GPT review Q6: "ponds pump to the last decilitre"): the decilitres
		/// a pump lifts from a natural body this cycle, given <paramref name="supplyDl"/> = what the body can hand out (up to
		/// <paramref name="units"/>). Exact-level on: a notch, or what is left, so a pond is pumped dry exactly as a dug channel
		/// is (the old whole-notch rule stranded its last &lt;1,000 L). Exact-level off: whole notches only, as before. 0 = not
		/// drawable.</summary>
		public static int SourceTakeUnits(int units, long supplyDl, bool levelExact)
		{
			if (units <= 0 || supplyDl <= 0)
			{
				return 0;
			}
			if (supplyDl >= units)
			{
				return units;
			}
			return levelExact ? (int)supplyDl : 0;
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
	/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1's driver-input set, Verse-free so the selftest runs the production rule: cell
	/// index -> tick a driver (pump, drill) last fed it. The flow kernel seeds its order from these cells. Not saved.
	/// PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD (P4, GPT G3.1): a write marks a cell only when it RAISES the fill, and a
	/// driver never writes into a brimming cell, so after a load (the set starts empty) a pump whose outlet was saved
	/// brimming never re-marked it: no input seed, every flow key equal, and the channel stalled beside the pump for good
	/// (the same stall followed digging on from a settled outlet once the window lapsed). The fix: a driver BACKED UP
	/// against a brimming cell marks it too (<see cref="NoteBackedUp"/>), so the set re-derives from live driver
	/// pressure instead of needing a save.</summary>
	public sealed class RM_DriverInputs
	{
		/// <summary>PROVISIONAL (auto-decided 2026-10-09, FLOW_ORDER_EXTERNAL_INPUT_1): a driver input seeds the flow
		/// order for 5000 ticks after its last write.</summary>
		public const int WindowTicks = 5000;

		private readonly Dictionary<int, int> tick = new Dictionary<int, int>();
		private readonly List<int> scratch = new List<int>();

		public int Count { get { return tick.Count; } }

		public bool Contains(int cell) { return tick.ContainsKey(cell); }

		/// <summary>A driver wrote <paramref name="newFill"/> over <paramref name="oldFill"/>: marks the cell when it rose.</summary>
		public void NoteWrite(int cell, int oldFill, int newFill, int now)
		{
			if (newFill > oldFill)
			{
				tick[cell] = now;
			}
		}

		/// <summary>A driver had liquid for this cell and could not pour because the cell brims: it is still an input.</summary>
		public void NoteBackedUp(int cell, int now)
		{
			tick[cell] = now;
		}

		/// <summary>Drops inputs older than the window, and any on a cell that is no longer excavated.</summary>
		public void Prune(int now, System.Func<int, bool> notExcavated)
		{
			if (tick.Count == 0)
			{
				return;
			}
			scratch.Clear();
			foreach (KeyValuePair<int, int> kv in tick)
			{
				if (now - kv.Value > WindowTicks || notExcavated(kv.Key))
				{
					scratch.Add(kv.Key);
				}
			}
			foreach (int k in scratch)
			{
				tick.Remove(k);
			}
		}
	}
}
