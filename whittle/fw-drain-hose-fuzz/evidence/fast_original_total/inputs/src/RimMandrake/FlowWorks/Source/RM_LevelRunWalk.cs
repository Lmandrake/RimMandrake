namespace RimMandrake.FlowWorks
{
	/// <summary>What the levelling run walk reads of a square, by cell index (LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE). The live
	/// adapter is a struct over the excavation grids (RM_MapComponent_Excavation.LevelRunGrid); the selftest's is a fake grid.
	/// A struct type argument makes every call a direct (inlinable) call, with no delegate and no boxing.</summary>
	public interface RM_IRunGrid
	{
		/// <summary>The square is dug (excavated).</summary>
		bool Dug(int i);
		/// <summary>Decilitres of liquid in a dug square.</summary>
		long Water(int i);
		/// <summary>An identity of the square's liquid (its recorded liquid, else the map's active one); compared between wet squares only.</summary>
		int Fluid(int i);
		/// <summary>A shut sluice stands on the square.</summary>
		bool Seals(int i);
		/// <summary>The dug depth in notches (1..255).</summary>
		int Depth(int i);
	}

	/// <summary>One walked run: squares counted, squares reached (counted plus a capped walk's queued edge), water, lowest index, deepest square.</summary>
	public struct RM_LevelRun
	{
		public int Squares, Reached, MaxDepth, Low;
		public long Water;
	}

	/// <summary>The walk's per-map scratch, sized to the map once: marks (the walk id that reached a square), the body a walk
	/// found, the queue, and the depth counts of the last walk. Nothing in it is allocated per walk or per cycle.</summary>
	public sealed class RM_LevelRunScratch
	{
		public int[] Mark, BodyOf, Queue;
		public readonly int[] DepthCount = new int[256];
		public int WalkId, CycleFirstWalk;

		/// <summary>Sizes the arrays to <paramref name="cells"/> (a no-op when they already fit and the walk ids have room).</summary>
		public void Prepare(int cells)
		{
			if (Mark == null || Mark.Length != cells || WalkId > int.MaxValue - 1000000)
			{
				Mark = new int[cells];
				BodyOf = new int[cells];
				Queue = new int[cells];
				WalkId = 0;
			}
		}

		/// <summary>A new cycle: no square counts as reached until a walk of this cycle reaches it.</summary>
		public void BeginCycle()
		{
			CycleFirstWalk = WalkId + 1;
		}

		/// <summary>A walk of this cycle reached the square (a capped walk's queued edge included).</summary>
		public bool Reached(int i) => Mark[i] >= CycleFirstWalk;
	}

	/// <summary>The 4-way run of dug squares from a start square, in cell-index space, allocation-free. It is the old
	/// RM_Levelling.DugBody IntVec3 walk exactly (LevelRunWalkChecks holds it to that walk): neighbours in the order
	/// N, E, S, W; a neighbour joins when it is dug, not reached this cycle, as wet as the start (and, wet, the same liquid)
	/// and not under a shut sluice; the walk stops counting once more than <c>maxRun</c> squares are queued, and every
	/// queued square is marked. The caller checks the start square (reached, sealed, budget) before walking.</summary>
	public static class RM_LevelRunWalk
	{
		public static RM_LevelRun Walk<G>(ref G g, int width, int height, int start, RM_LevelRunScratch s, int maxRun) where G : struct, RM_IRunGrid
		{
			int[] mark = s.Mark, queue = s.Queue, count = s.DepthCount;
			System.Array.Clear(count, 0, count.Length);
			int walk = ++s.WalkId, first = s.CycleFirstWalk;
			mark[start] = walk;
			bool wet = g.Water(start) > 0;
			int fluid = g.Fluid(start);
			queue[0] = start;
			int tail = 1, maxDepth = 0, low = int.MaxValue, head = 0, lastRow = (height - 1) * width;
			long water = 0;
			for (; head < tail && tail <= maxRun; head++)
			{
				int c = queue[head];
				int d = g.Depth(c);
				count[d]++;
				if (d > maxDepth)
				{
					maxDepth = d;
				}
				water += g.Water(c);
				if (c < low)
				{
					low = c;
				}
				int x = c % width;
				// N (z+1), E (x+1), S (z-1), W (x-1): GenAdj.CardinalDirections' order
				for (int k = 0; k < 4; k++)
				{
					int n;
					switch (k)
					{
						case 0: if (c >= lastRow) continue; n = c + width; break;
						case 1: if (x == width - 1) continue; n = c + 1; break;
						case 2: if (c < width) continue; n = c - width; break;
						default: if (x == 0) continue; n = c - 1; break;
					}
					if (mark[n] >= first || !g.Dug(n))
					{
						continue;
					}
					bool nWet = g.Water(n) > 0;
					if (nWet != wet || (wet && g.Fluid(n) != fluid) || g.Seals(n))
					{
						continue;
					}
					mark[n] = walk;
					queue[tail++] = n;
				}
			}
			return new RM_LevelRun { Squares = head, Reached = tail, MaxDepth = maxDepth, Low = low, Water = water };
		}

		/// <summary>The last walk's depth histogram: hist[l] = squares at least l notches deep, l = 1..maxDepth (the old
		/// per-square loop over 1..depth, as a suffix sum of the depth counts).</summary>
		public static int[] Hist(RM_LevelRunScratch s, int maxDepth)
		{
			var hist = new int[maxDepth + 1];
			int run = 0;
			for (int l = maxDepth; l >= 1; l--)
			{
				run += s.DepthCount[l];
				hist[l] = run;
			}
			return hist;
		}
	}
}
