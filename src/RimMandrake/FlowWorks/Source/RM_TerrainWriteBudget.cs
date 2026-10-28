using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (live r12: one pulse slice took 161 ms). The pulse redraws a dug square's
	/// water picture with one TerrainGrid.SetTerrain each time its look band changes, and SetTerrain is not cheap (vanilla's
	/// DoTerrainChangedEffects: the mesh of the square and its neighbours, its things, perceived path cost, district, water body,
	/// map events). Where a big body's water swings across a band edge (a basin draining down an edge sink with moving seams:
	/// the offline bench counted 6,000 changes in one slice and 12,000 in one pulse) those writes all landed in one tick. This
	/// caps the picture writes the pulse makes in a tick; the rest wait here, in order, and the component drains them on the
	/// ticks that follow (each is re-judged from the grids when its turn comes, so a square whose water moved back again costs
	/// nothing). Verse-free so the selftest drives the production code.</summary>
	public sealed class RM_TerrainWriteBudget
	{
		/// <summary>Picture writes (SetTerrain) the pulse may make in one tick. About 25 microseconds each live on Mono (161 ms
		/// over 6,000), so 200 is about 5 ms; 12,000 waiting drain in 60 ticks, well inside a 250-tick pulse.</summary>
		public const int WritesPerTick = 200;

		/// <summary>Squares judged from the backlog in one tick, changed or not (a judgement without a write is a few grid
		/// reads), so a backlog of squares that need nothing still clears quickly without an unbounded tick.</summary>
		public const int JudgedPerTick = 4 * WritesPerTick;

		private bool[] queued = new bool[0];
		private readonly List<int> fifo = new List<int>();
		private int head;
		private long tick = long.MinValue;
		private int writes;

		/// <summary>Squares waiting for their picture.</summary>
		public int Count => fifo.Count - head;

		/// <summary>Picture writes spent in the current tick.</summary>
		public int WritesThisTick => writes;

		/// <summary>Is a write allowed in tick <paramref name="now"/>? Counts it if so.</summary>
		public bool TryTakeWrite(long now)
		{
			if (now != tick)
			{
				tick = now;
				writes = 0;
			}
			if (writes >= WritesPerTick)
			{
				return false;
			}
			writes++;
			return true;
		}

		/// <summary>Defer square <paramref name="idx"/> of a map of <paramref name="cells"/> squares (once: a square already
		/// waiting keeps its place).</summary>
		public void Defer(int idx, int cells)
		{
			if (queued.Length != cells)
			{
				Clear(cells);
			}
			if (queued[idx])
			{
				return;
			}
			queued[idx] = true;
			fifo.Add(idx);
		}

		/// <summary>Judge waiting squares in order with <paramref name="apply"/> (which returns false when it had to defer the
		/// square again because this tick's writes are spent), at most <paramref name="maxJudged"/> of them. Returns how many
		/// were judged.</summary>
		public int Drain(int maxJudged, Func<int, bool> apply)
		{
			int judged = 0;
			while (head < fifo.Count && judged < maxJudged)
			{
				int idx = fifo[head++];
				queued[idx] = false;
				judged++;
				if (!apply(idx))
				{
					break;
				}
			}
			if (head == fifo.Count)
			{
				fifo.Clear();
				head = 0;
			}
			else if (head > 4096 && head * 2 > fifo.Count)
			{
				fifo.RemoveRange(0, head);
				head = 0;
			}
			return judged;
		}

		/// <summary>Forget everything waiting (a new map size, or a flush that judged every square).</summary>
		public void Clear(int cells)
		{
			if (queued.Length != cells)
			{
				queued = new bool[cells];
			}
			else
			{
				Array.Clear(queued, 0, queued.Length);
			}
			fifo.Clear();
			head = 0;
		}
	}

	/// <summary>EXCAVATION_RAIN_TAME_ONE_TICK_DELUGE (live r16: one rain notch cost 290 ms in ONE tick, DoPulse -> ApplyRain over
	/// every unroofed excavated square of a 325x325 scene). The pulse's rain is landed AHEAD of the pulse, a slice of squares a
	/// tick, on the quiet ticks before it is due (no pulse in flight), so the pulse starts from the very grids the one-tick rain
	/// left; whatever is still owed when the pulse is due (or a save comes) lands whole, as before. The squares are a snapshot of
	/// the excavated set in its own order (the order the one-tick rain walked, so the sheet sees its overflows in the same
	/// order). Verse-free so the selftest drives the production schedule.</summary>
	public sealed class RM_RainPass
	{
		/// <summary>Squares landed in one tick. A square is a few grid reads and at most one deferred picture (the picture writes
		/// themselves go through RM_TerrainWriteBudget), so 4,000 is a few ms on Mono; 80,000 squares land in 20 ticks.</summary>
		public const int CellsPerTick = 4000;

		/// <summary>Ticks of slack before the pulse is due, beyond the ticks the squares need.</summary>
		public const int SlackTicks = 5;

		private readonly List<int> cells = new List<int>();
		private int next;

		/// <summary>Notches each square takes from this pass (0: the pass decided no rain).</summary>
		public int Levels { get; private set; }

		/// <summary>Squares not landed yet.</summary>
		public int Remaining => cells.Count - next;

		/// <summary>How many ticks before the pulse the pass starts for <paramref name="squares"/> excavated squares: the ticks
		/// the squares need at <see cref="CellsPerTick"/> plus slack, never more than half the pulse interval.</summary>
		public static int LeadTicks(int squares, int intervalTicks)
		{
			int need = (squares + CellsPerTick - 1) / CellsPerTick + SlackTicks;
			int cap = Math.Max(1, intervalTicks / 2);
			return need < cap ? need : cap;
		}

		/// <summary>Start a pass of <paramref name="levels"/> notches; its squares follow by <see cref="Add"/>, in order. Squares
		/// a previous pass still owed must be landed first (<see cref="Step"/> with no limit).</summary>
		public void Begin(int levels)
		{
			cells.Clear();
			next = 0;
			Levels = levels;
		}

		/// <summary>One square of the pass begun (ignored when the pass decided no rain).</summary>
		public void Add(int square)
		{
			if (Levels > 0)
			{
				cells.Add(square);
			}
		}

		/// <summary>Land at most <paramref name="max"/> squares in order with <paramref name="land"/> (square, notches). Returns
		/// how many were landed.</summary>
		/// <summary>RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL (MED): the pulse is due. More owed than one slice: land a slice now and
		/// the pulse waits a tick (true); otherwise nothing lands here and the pulse lands the rest (at most a slice) itself. So
		/// no tick lands more than <see cref="CellsPerTick"/> squares, the first pulse with no lead window included. A save still
		/// lands everything at once (the grids are scribed, never the pass).</summary>
		public bool HoldsPulse(Action<int, int> land)
		{
			if (Remaining <= CellsPerTick)
			{
				return false;
			}
			Step(CellsPerTick, land);
			return true;
		}

		public int Step(int max, Action<int, int> land)
		{
			int n = 0;
			while (next < cells.Count && n < max)
			{
				land(cells[next++], Levels);
				n++;
			}
			if (next >= cells.Count)
			{
				cells.Clear();
				next = 0;
			}
			return n;
		}
	}
}
