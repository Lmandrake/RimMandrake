using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>What the flow kernel needs from the world that is not a depth/fill array: terrain, liquid
	/// bodies, sinks and fluid identity. The game implements it on <see cref="RM_MapComponent_Excavation"/>;
	/// the offline selftest implements it on plain arrays. Fluids are opaque objects compared by reference
	/// (a FluidDef in game), exactly as <see cref="RM_StockMath.FluidsCompatible{T}"/> compares them.
	/// The kernel calls these in the same order the pre-extraction pulse did, so lazy body formation
	/// (RM_LiquidStock.BodyAt) happens at the same moments.</summary>
	public interface RM_IFlowWorld
	{
		/// <summary>Natural liquid terrain at this cell (a source when its depth is 0).</summary>
		bool IsNaturalLiquid(int idx);
		/// <summary>The source body at idx may still hand out one level.</summary>
		bool CanSupply(int idx);
		/// <summary>Spend one level's worth (the body's own unit) from the source body at idx. False = unaffordable:
		/// the kernel must not move liquid.</summary>
		bool TryDebitLevel(int idx);
		/// <summary>The fluid a donor gives: its body's for a source, the cell's own record otherwise. May be null.</summary>
		object DonorFluid(int idx, bool source);
		/// <summary>The fluid recorded on an excavated cell, or null.</summary>
		object CellFluid(int idx);
		/// <summary>First level into a dry cell claims it for <paramref name="fluid"/> (null = the map default).</summary>
		void Claim(int idx, object fluid);
		/// <summary>The fluid's ticksPerTile, with the map default for null.</summary>
		int TicksPerTile(object fluid);
		bool IsSink(int idx);
		/// <summary>A component finished resolving (the game re-renders its fill terrain here).</summary>
		void ComponentResolved(List<int> component);
	}

	/// <summary>Approach B phase 2 (design/RimMandrake/flowworks_offline_kernel_B.md): the grid transition of one
	/// flow pulse — component resolution, sink drain, flow order, recipient order, donor selection and the
	/// per-component conservation ledger — on integer cell indices (z * width + x, Verse's CellIndices) and
	/// byte depth/fill arrays. Extracted VERBATIM from RM_MapComponent_Excavation.DoPulse / ResolveComponent /
	/// ComputeFlowOrder / HopsFrom / PickDonor / CompareDeepestFirst, which now call it; rain, burn, stock
	/// refill/recession, terrain writes and Scribe stay in the adapter. Verse-free so the selftest runs it.
	///
	/// Also holds <see cref="CollectBody"/>, the 8-way flood fill RM_LiquidStock.FormBody uses to find a body's
	/// footprint.</summary>
	public sealed class RM_FlowKernel
	{
		public readonly int width;
		public readonly int height;
		public byte[] depth;
		public byte[] fill;
		public RM_IFlowWorld world;

		// settings, read once per pulse by the adapter
		public int flowPerPulse = 1;
		public bool edgeSinksEnabled;
		public bool viscosityEnabled;
		public int maxComponentCells = 6000;
		/// <summary>Superdeep: what a natural source reads as (RM_ExcavationDepth.Superdeep).</summary>
		public const byte Superdeep = 4;

		// per-pulse outputs
		public float sinkDrained;
		/// <summary>Largest absolute per-component ledger imbalance this pulse (0 when every component balances).</summary>
		public float worstImbalance;
		/// <summary>One line per component whose ledger did not balance (the adapter logs each in dev mode).</summary>
		public readonly List<string> imbalanceReports = new List<string>();

		private readonly HashSet<int> visited = new HashSet<int>();
		private readonly HashSet<int> componentSources = new HashSet<int>();
		private readonly List<int> neighbourScratch = new List<int>();
		private readonly Queue<int> queue = new Queue<int>();
		private readonly List<int> component = new List<int>();
		private readonly List<int> recipients = new List<int>();
		private readonly Dictionary<int, int> sourceHops = new Dictionary<int, int>();
		private readonly Dictionary<int, int> sinkHops = new Dictionary<int, int>();
		private readonly List<int> hopFrontier = new List<int>();
		private readonly HashSet<int> componentSet = new HashSet<int>();
		private readonly Predicate<int> isSourcePred;
		private readonly Predicate<int> isExcavatedPred;
		private readonly Action<int, List<int>> cardinalPred;
		private readonly Comparison<int> deepestFirst;

		// Verse's GenAdj.CardinalDirections order: N, E, S, W.
		private static readonly int[] CardX = { 0, 1, 0, -1 };
		private static readonly int[] CardZ = { 1, 0, -1, 0 };
		// Verse's GenAdj.AdjacentCells order: N, E, S, W, SE, NE, NW, SW.
		private static readonly int[] AdjX = { 0, 1, 0, -1, 1, 1, -1, -1 };
		private static readonly int[] AdjZ = { 1, 0, -1, 0, -1, 1, 1, -1 };

		public RM_FlowKernel(int width, int height)
		{
			this.width = width;
			this.height = height;
			isSourcePred = IsSource;
			isExcavatedPred = IsExcavated;
			cardinalPred = CardinalInBounds;
			deepestFirst = CompareDeepestFirst;
		}

		/// <summary>The cardinal neighbour of idx in direction d (0..3), or -1 out of bounds.</summary>
		public int Cardinal(int idx, int d)
		{
			int x = idx % width + CardX[d];
			int z = idx / width + CardZ[d];
			return x < 0 || z < 0 || x >= width || z >= height ? -1 : z * width + x;
		}

		public bool IsExcavated(int idx)
		{
			return idx >= 0 && depth[idx] != 0;
		}

		public bool IsSource(int idx)
		{
			return idx >= 0 && depth[idx] == 0 && world.IsNaturalLiquid(idx);
		}

		private void CardinalInBounds(int c, List<int> into)
		{
			for (int i = 0; i < 4; i++)
			{
				int n = Cardinal(c, i);
				if (n >= 0)
				{
					into.Add(n);
				}
			}
		}

		/// <summary>The flow half of one pulse: every component reachable from <paramref name="seedOrder"/> (the
		/// excavated cells, in the adapter's iteration order — which decides who a scarce LIMITED body pays first),
		/// resolved in that order.</summary>
		public void Pulse(IEnumerable<int> seedOrder, long pulseCount)
		{
			sinkDrained = 0f;
			worstImbalance = 0f;
			imbalanceReports.Clear();
			visited.Clear();
			foreach (int seed in seedOrder)
			{
				if (visited.Contains(seed))
				{
					continue;
				}
				RM_StockMath.CollectComponent(seed, isSourcePred, isExcavatedPred, cardinalPred,
					visited, componentSources, queue, neighbourScratch, component, maxComponentCells);
				ResolveComponent(pulseCount);
			}
		}

		private void ResolveComponent(long pulseCount)
		{
			float before = 0f;
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsExcavated(c))
				{
					before += fill[c];
				}
			}

			// Sinks drain before the flow, so the room a sink opens is room this same pulse can pour into.
			float externalDrain = 0f;
			if (edgeSinksEnabled)
			{
				int drainPerCell = flowPerPulse;
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (!IsExcavated(c) || !world.IsSink(c))
					{
						continue;
					}
					int take = fill[c] < drainPerCell ? fill[c] : drainPerCell;
					if (take <= 0)
					{
						continue;
					}
					fill[c] -= (byte)take;
					externalDrain += take;
				}
				sinkDrained += externalDrain;
			}

			ComputeFlowOrder();

			recipients.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (!IsExcavated(c))
				{
					continue;
				}
				if (fill[c] < depth[c])
				{
					recipients.Add(c);
				}
			}
			if (recipients.Count == 0)
			{
				world.ComponentResolved(component);
				return;
			}
			recipients.Sort(deepestFirst);

			float externalCredit = 0f;
			int perCell = flowPerPulse;
			for (int i = 0; i < recipients.Count; i++)
			{
				int r = recipients[i];
				int moved = 0;
				while (moved < perCell && fill[r] < depth[r])
				{
					int donor = PickDonor(r, depth[r], pulseCount);
					if (donor < 0)
					{
						break;
					}
					if (IsSource(donor))
					{
						// The 5:1 budget bites here and nowhere else. A failed debit must NOT move liquid.
						if (!world.TryDebitLevel(donor))
						{
							break;
						}
						externalCredit += 1f;
					}
					else
					{
						fill[donor] -= 1;
					}
					if (fill[r] == 0)
					{
						world.Claim(r, world.DonorFluid(donor, IsSource(donor)));
					}
					fill[r] += 1;
					moved++;
				}
			}

			float after = 0f;
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsExcavated(c))
				{
					after += fill[c];
				}
			}
			float imbalance = after - before - externalCredit + externalDrain;
			if (Math.Abs(imbalance) > 0.001f)
			{
				worstImbalance = Math.Max(worstImbalance, Math.Abs(imbalance));
				imbalanceReports.Add("before=" + before.ToString("F1") + " after=" + after.ToString("F1") +
					" sourceCredit=" + externalCredit.ToString("F1") + " sinkDrain=" + externalDrain.ToString("F1") +
					" imbalance=" + imbalance.ToString("F1"));
			}
			world.ComponentResolved(component);
		}

		private int CompareDeepestFirst(int a, int b)
		{
			int da = depth[a];
			int db = depth[b];
			if (da != db)
			{
				return db - da;
			}
			int sa = HopsOf(sourceHops, a);
			int sb = HopsOf(sourceHops, b);
			if (sa != sb)
			{
				return sa - sb;
			}
			int ka = HopsOf(sinkHops, a);
			int kb = HopsOf(sinkHops, b);
			if (ka != kb)
			{
				return kb - ka;
			}
			return a - b;
		}

		private static int HopsOf(Dictionary<int, int> hops, int c)
		{
			return hops.TryGetValue(c, out int h) ? h : 0;
		}

		/// <summary>FLOWWORKS_CHANNEL_OSCILLATION_1's per-component flow order: hops from every supplying source,
		/// hops to every sink. Fixed for the whole pulse.</summary>
		private void ComputeFlowOrder()
		{
			sourceHops.Clear();
			sinkHops.Clear();
			hopFrontier.Clear();
			componentSet.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				componentSet.Add(c);
				if (IsSource(c) && world.CanSupply(c))
				{
					hopFrontier.Add(c);
				}
			}
			HopsFrom(sourceHops, false);
			hopFrontier.Clear();
			if (edgeSinksEnabled)
			{
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (IsExcavated(c) && world.IsSink(c))
					{
						hopFrontier.Add(c);
					}
				}
			}
			HopsFrom(sinkHops, true);
		}

		private void HopsFrom(Dictionary<int, int> hops, bool seedsAreExcavated)
		{
			if (hopFrontier.Count == 0)
			{
				return;
			}
			if (seedsAreExcavated)
			{
				for (int i = 0; i < hopFrontier.Count; i++)
				{
					hops[hopFrontier[i]] = 0;
				}
			}
			int head = 0;
			while (head < hopFrontier.Count)
			{
				int c = hopFrontier[head++];
				int hc = hops.TryGetValue(c, out int h) ? h : 0;
				for (int i = 0; i < 4; i++)
				{
					int n = Cardinal(c, i);
					if (n < 0 || hops.ContainsKey(n) || !componentSet.Contains(n) || !IsExcavated(n))
					{
						continue;
					}
					hops[n] = hc + 1;
					hopFrontier.Add(n);
				}
			}
		}

		/// <summary>GRAVITY (a neighbour gives to a deeper cell) or OVERFLOW (a brimming neighbour gives to any cell
		/// with room), filtered by budget, no-mix, viscosity and the flow order. Fixed direction order, strict &gt;
		/// on the score. Returns -1 for no donor.</summary>
		private int PickDonor(int r, byte depthR, long pulseCount)
		{
			int best = -1;
			int bestScore = -1;
			for (int i = 0; i < 4; i++)
			{
				int n = Cardinal(r, i);
				if (n < 0)
				{
					continue;
				}
				byte dn;
				byte fn;
				bool source = IsSource(n);
				if (source)
				{
					if (!world.CanSupply(n))
					{
						continue;
					}
					dn = Superdeep;
					fn = Superdeep;
				}
				else
				{
					dn = depth[n];
					if (dn == 0)
					{
						continue;
					}
					fn = fill[n];
				}
				if (fn == 0)
				{
					continue;
				}
				object donorFluid = world.DonorFluid(n, source);
				if (!RM_StockMath.FluidsCompatible(fill[r] > 0, world.CellFluid(r), donorFluid))
				{
					continue;
				}
				if (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(donorFluid)))
				{
					continue;
				}
				if (depthR <= dn && fn < dn)
				{
					continue;
				}
				if (!source && (!componentSet.Contains(n)
						|| !RM_StockMath.MayFlowBetween(
							HopsOf(sourceHops, n), HopsOf(sinkHops, n), dn,
							HopsOf(sourceHops, r), HopsOf(sinkHops, r), depthR)))
				{
					continue;
				}
				int score = source ? 1000 : (fn * 10 + dn);
				if (score > bestScore)
				{
					bestScore = score;
					best = n;
				}
			}
			return best;
		}

		// ── body footprint (RM_LiquidStock.FormBody's walk) ─────────────────────

		/// <summary>8-way flood fill of source cells from <paramref name="seed"/>, in Verse's AdjacentCells order.
		/// Stops at <paramref name="maxCells"/> (truncated). If the walk touches a cell <paramref name="ownedBody"/>
		/// says is already in a body (id &gt;= 0), it stops and returns that id: the region IS that body. Otherwise
		/// returns -1 with the footprint in <paramref name="found"/>.
		///
		/// 🔴 It does not look at WHICH liquid a cell is: every natural-liquid neighbour joins. Finding #1 of
		/// flowworks_playtest_automation_2026-10-06.md (touching water and tar merge into one body carrying the
		/// seed's fluid) lives exactly here; FlowKernelFuzz's regression case pins it.</summary>
		public static int CollectBody(int width, int height, int seed, Func<int, bool> isSource, Func<int, int> ownedBody,
			int maxCells, List<int> found, List<int> fillQueue, HashSet<int> fillSeen,
			out bool touchesEdge, out bool truncated)
		{
			fillQueue.Clear();
			fillSeen.Clear();
			found.Clear();
			fillQueue.Add(seed);
			fillSeen.Add(seed);
			touchesEdge = false;
			truncated = false;
			int head = 0;
			while (head < fillQueue.Count)
			{
				int c = fillQueue[head++];
				found.Add(c);
				int cx = c % width;
				int cz = c / width;
				if (cx == 0 || cx == width - 1 || cz == 0 || cz == height - 1)
				{
					touchesEdge = true;
				}
				if (found.Count >= maxCells)
				{
					truncated = true;
					break;
				}
				for (int i = 0; i < 8; i++)
				{
					int nx = cx + AdjX[i];
					int nz = cz + AdjZ[i];
					if (nx < 0 || nz < 0 || nx >= width || nz >= height)
					{
						continue;
					}
					int n = nz * width + nx;
					if (fillSeen.Contains(n))
					{
						continue;
					}
					fillSeen.Add(n);
					int owned = ownedBody(n);
					if (owned >= 0)
					{
						return owned;
					}
					if (isSource(n))
					{
						fillQueue.Add(n);
					}
				}
			}
			return -1;
		}
	}
}
