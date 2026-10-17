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
		/// <summary>FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO (P7): a dry cell can record <paramref name="fluid"/> (null = the
		/// map default). False = no identity key is free; the kernel must not debit, drain or fill for that cell.</summary>
		bool CanClaim(object fluid);
		/// <summary>The fluid's ticksPerTile, with the map default for null.</summary>
		int TicksPerTile(object fluid);
		bool IsSink(int idx);
		/// <summary>A component finished resolving (the game re-renders its fill terrain here).</summary>
		void ComponentResolved(List<int> component);
	}

	/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: what the exact-level kernel (<see cref="RM_FlowKernel.levelExactEnabled"/>)
	/// reads and writes about natural bodies, in decilitres. Implemented beside <see cref="RM_IFlowWorld"/> (the game on
	/// RM_MapComponent_Excavation, the selftest on its array world); without it the kernel keeps the whole-notch engine.</summary>
	public interface RM_ILevelWorld
	{
		/// <summary>The LIMITED body behind source <paramref name="src"/> (an id), or -1 when it never runs down (limitless, or
		/// the source budget off).</summary>
		int LevelBodyOf(int src);
		/// <summary>The body's water, a whole number of decilitres.</summary>
		long BodyStockDl(int body);
		void SetBodyStockDl(int body, long dl);
		/// <summary>H[L] over the body's undug footprint: squares whose bed is at least L notches, L = 0..maxBed.</summary>
		int[] BodyHistogram(int body);
		/// <summary>The bed (notches) of source square <paramref name="src"/>.</summary>
		int BedAt(int src);
		/// <summary>A limitless source paid <paramref name="dl"/> decilitres of <paramref name="fluid"/> into dug squares this pulse
		/// (the disclosed external input; the old kernel's TryDebitLevel on a limitless body).</summary>
		void NoteLimitlessDl(object fluid, long dl);
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
		/// <summary>THICK_LIQUID_CREEP_1: a cell that RECEIVED liquid this pulse may not donate it on in the same pulse
		/// when the fluid is viscous (ViscosityStride &gt; 1), so a thick fill front moves one cell per moving pulse
		/// instead of racing down the whole channel. Water (stride 1) is untouched. Off by default; the adapter sets it.</summary>
		public bool creepEnabled;
		/// <summary>CANAL_FRONT_FIX_WRONG_END_WETS_FIRST (owner 2026-10-12, by card: the wet front must visibly advance outward
		/// from the mouth like a flood front): a cell that received WATER (stride 1) this pulse may not pass it on in the same
		/// pulse, so a level moves one cell per pulse from the source instead of being pulled the whole run at once (which wet
		/// a dead-end channel far end first). Independent of <see cref="creepEnabled"/>, which stays thick-liquid only.
		/// Off by default; the adapter sets it.</summary>
		public bool creepWaterEnabled;
		private long[] receivedStamp;
		/// <summary>WATER_SURFACE_REPAIR_LEVEL_OR_BUST (owner 2026-10-17: "We need VERY smooth water. That's water's one primary
		/// characteristic: a level surface."): the WATER creep hold is on the FRONT only, a square that was DRY when it took its
		/// first unit this pulse. Holding every square that received (the old rule) held a mouth for as long as its source kept
		/// paying it, so the mouth never joined its wet region and filled to the brim beside dry squares of the same floor
		/// (live S2 read pond [4 0 4 0]). A square already wet passes water on as it receives it, so a pond rises as one
		/// surface; the front still advances one square a pulse. Thick liquids keep the whole-square hold (THICK_LIQUID_CREEP_1).</summary>
		private long[] frontStamp;
		/// <summary>WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND (owner 2026-10-16, by card "Level by water surface": "Shouldn't
		/// each square of the channel have 'units of water' in it, and they will try to spread out evenly"): a neighbour
		/// gives a unit when its water SURFACE (fill - dug depth; a source reads 0) stands above the recipient's, whatever
		/// either square's dug depth. A drop of two or more always moves; a drop of exactly one moves only down the
		/// component's static flow order (<see cref="RM_StockMath.MayFlowBetween"/>), because one unit across a drop of one
		/// just swaps the two surfaces. That order gains a third tier here, hops to the component's deepest bed
		/// (<see cref="lowHops"/>), so a unit held one above a dry neighbour still walks toward a dug hole instead of
		/// standing on a terrace beside it. Every move lowers sum(surface^2) or keeps it and steps down the acyclic order, so a
		/// closed run settles (no period-2 shuttle) with neighbours at most one unit apart, and a sink drains a run to empty.
		/// Off = the old GRAVITY / OVERFLOW rule, which stranded partly filled same-depth cells. Off by default here; the
		/// adapter sets it (shipped ON).</summary>
		public bool levelBySurfaceEnabled;
		/// <summary>WATER_LEVELSET_SOLVE (owner 2026-10-16 at review station 1: "Please select an algorithm that will allow the
		/// fluid to levelset down to a smooth 0 or 1 across a too-wide field like this, not 0, deep, 0"). Only with
		/// <see cref="levelBySurfaceEnabled"/>: each wet region (plus its dry dug rim) is SOLVED to its flat water level instead
		/// of levelled one unit at a time (<see cref="LevelSetWetRegions"/>), and a drop of exactly one between two dug cells
		/// no longer moves in the neighbour pass (that swap walked puddles and striped wide basins 0,1,0,1). Off by default
		/// here; the adapter sets it (shipped ON).</summary>
		public bool levelSetEnabled;
		public int maxComponentCells = 6000;
		/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1 part 2: a connected network bigger than <see cref="maxComponentCells"/> is
		/// resolved as several capped partitions, and liquid never crosses a partition seam inside one pulse. With the
		/// seed order fixed the seams fell on the same cells every pulse, so the partitions never exchanged at all. On:
		/// such a network's first partition is walked from a start cell that moves with the pulse count, so every seam
		/// moves and, over a few pulses, liquid crosses all of them. Networks within the cap are untouched (same walk,
		/// same order), so the offline oracle and every small-scene case are unaffected. Off by default; the adapter sets it.</summary>
		public bool seamRotationEnabled;
		private readonly HashSet<int> networkVisited = new HashSet<int>();
		private readonly HashSet<int> networkSources = new HashSet<int>();
		private readonly List<int> networkCells = new List<int>();
		private readonly List<int> networkExcavated = new List<int>();
		/// <summary>Pulses on which a network over the cap was walked with a moved seam (the selftest reads it).</summary>
		public int rotatedNetworks;
		/// <summary>FLOWWORKS_SLUICE_TWO_DOORS_1 (owner 2026-10-06: "sealed sluice gates (standard) and the ones made of
		/// metal grates that always allow liquid"): true for a cell under a SHUT sluice. Liquid neither enters nor
		/// leaves a sealed cell and no flow order is walked through it, so the level stops at the gate. Null = no
		/// cell is sealed (the offline worlds, and every map without a shut sluice).</summary>
		public Func<int, bool> sealedCell;
		/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1: true for an excavated cell a pump, drill or other driver has fed
		/// recently. The flow order's "source hops" are walked from these as well as from supplying natural sources, so
		/// a pump-fed equal-depth run spreads AWAY from the pump (a brimming cell overflows to a later key) instead of
		/// sitting beside it with every key equal. Geometry from fixed input cells, so the order stays static and
		/// acyclic (FLOWWORKS_CHANNEL_OSCILLATION_1). Null = no inputs (the offline worlds' default).</summary>
		public Func<int, bool> externalInput;
		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2 (owner's words, 2026-10-16: "It should slosh around until it levels,
		/// pond or canal or otherwise."): a natural source's pond drawdown s (its surface is −s). A source gives a level only
		/// while its surface stands above the recipient's water (<see cref="RM_PondDepthMath.SourceMayGive"/>), so a ditch
		/// whose floor is above the pond's surface stops drawing. Null, or 0 for a cell, is today's brim-full source exactly
		/// (the offline worlds' default; the adapter sets it while "pondHeadRuleEnabled" is on).</summary>
		public Func<int, int> sourceDrawdown;
		/// <summary>D2's return half: credit one level of the dug square's water to the pond behind source <c>(src, dug)</c>.
		/// True = the pond took it (the kernel then lowers the dug square). Null = no return (offline default).</summary>
		public Func<int, int, bool> returnLevel;
		/// <summary>Superdeep: what a natural source reads as (RM_ExcavationDepth.Superdeep).</summary>
		public const byte Superdeep = 4;

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17: "We need VERY smooth water. That's water's one
		/// primary characteristic: a level surface."; ruled exactly level by card). On, and with <see cref="part"/> set and the
		/// world an <see cref="RM_ILevelWorld"/>, every component resolves by <see cref="ResolveExact"/>: a dug square holds
		/// W = fill·U + part decilitres, a limited pond a whole number of dL, and each connected body is solved to ONE surface
		/// (RM_LevelSolve), the mouth paced at flowPerPulse notches a mouth square a pulse. Python twin:
		/// northstar/level_water.py. Off by default here; the adapter sets it (shipped ON).</summary>
		public bool levelExactEnabled;
		/// <summary>The decilitres below one whole notch per cell (0..U-1); W = fill·U + part. The adapter's scribed grid.</summary>
		public ushort[] part;
		/// <summary>Exact mode, this pulse: dL limitless sources paid in, dL sinks took out (the adapter's ledger).</summary>
		public long exactCreditDl;
		public long exactDrainDl;
		private readonly RM_LevelSolve exactSolve = new RM_LevelSolve();
		private readonly RM_LevelSolve canalSolve = new RM_LevelSolve();

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
		private readonly List<int> seedScratch = new List<int>();
		private readonly List<int> component = new List<int>();
		private readonly List<int> recipients = new List<int>();
		private readonly Dictionary<int, int> sourceHops = new Dictionary<int, int>();
		private readonly Dictionary<int, int> sinkHops = new Dictionary<int, int>();
		/// <summary>levelBySurfaceEnabled only: hops to the nearest cell dug to the component's deepest bed.</summary>
		private readonly Dictionary<int, int> lowHops = new Dictionary<int, int>();
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

		public bool IsSealed(int idx)
		{
			return idx >= 0 && sealedCell != null && sealedCell(idx);
		}

		public bool IsSource(int idx)
		{
			return idx >= 0 && depth[idx] == 0 && world.IsNaturalLiquid(idx);
		}

		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2 (owner: "It should slosh around until it levels, pond or canal or
		/// otherwise."), the return half, run by the adapter after <see cref="Pulse"/>: a dug square whose water stands two or
		/// more above a cardinal pond's surface (<see cref="RM_PondDepthMath.DugMayReturn"/>) runs levels back into that pond,
		/// at most <see cref="flowPerPulse"/> a square a pulse (the mouth's pace, D1), each one only once the pond has taken
		/// it (<see cref="returnLevel"/>: the stock rises by exactly what the square loses, so nothing is made or lost). Same
		/// fluid only. Squares in cell-index order. Returns the levels returned.</summary>
		public int ReturnToPonds(IEnumerable<int> seeds)
		{
			if (sourceDrawdown == null || returnLevel == null)
			{
				return 0;
			}
			seedScratch.Clear();
			seedScratch.AddRange(seeds);
			seedScratch.Sort();
			int total = 0;
			for (int i = 0; i < seedScratch.Count; i++)
			{
				int c = seedScratch[i];
				if (!IsExcavated(c) || IsSealed(c) || fill[c] == 0)
				{
					continue;
				}
				int moved = 0;
				for (int d = 0; d < 4 && moved < flowPerPulse; d++)
				{
					int n = Cardinal(c, d);
					if (n < 0 || IsSealed(n) || !IsSource(n))
					{
						continue;
					}
					if (!ReferenceEquals(world.CellFluid(c), world.DonorFluid(n, true)) && world.CellFluid(c) != null)
					{
						continue;
					}
					while (moved < flowPerPulse && fill[c] > 0)
					{
						int s = sourceDrawdown(n);
						if (s <= 0 || !RM_PondDepthMath.DugMayReturn(s, depth[c], fill[c]) || !returnLevel(n, c))
						{
							break;
						}
						fill[c] -= 1;
						moved++;
						total++;
					}
				}
			}
			return total;
		}

		/// <summary>D2: may source <paramref name="src"/> give to dug square <paramref name="r"/> by the head rule?</summary>
		private bool HeadAllows(int src, int r)
		{
			if (sourceDrawdown == null)
			{
				return true;
			}
			int s = sourceDrawdown(src);
			// s = 0 is a brim-full source: today's rule exactly (a mouth beside it stays a live mouth even when brim-full).
			return s <= 0 || RM_PondDepthMath.SourceMayGive(s, depth[r], fill[r]);
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
		/// excavated cells; sorted here by cell index, which decides who a scarce LIMITED body pays first),
		/// resolved in that order.</summary>
		public void Pulse(IEnumerable<int> seedOrder, long pulseCount)
		{
			sinkDrained = 0f;
			exactCreditDl = 0;
			exactDrainDl = 0;
			worstImbalance = 0f;
			imbalanceReports.Clear();
			visited.Clear();
			// Owner ruling 2026-10-06: a scarce body pays its channels by MAP POSITION (cell index), never by dig
			// order, so a session and a reload that rebuilds the set in index order give the same outcome.
			seedScratch.Clear();
			seedScratch.AddRange(seedOrder);
			seedScratch.Sort();
			foreach (int seed in seedScratch)
			{
				if (visited.Contains(seed))
				{
					continue;
				}
				RM_StockMath.CollectComponent(seed, isSourcePred, isExcavatedPred, cardinalPred,
					visited, componentSources, queue, neighbourScratch, component, maxComponentCells);
				if (seamRotationEnabled && component.Count >= maxComponentCells && ResolveRotatedNetwork(seed, pulseCount))
				{
					continue;
				}
				ResolveComponent(pulseCount);
			}
		}

		/// <summary>Part 2: <paramref name="seed"/>'s capped walk hit the cap. Walk its whole network (uncapped, own
		/// scratch sets), and if it really is bigger than the cap, undo the capped walk's marks and resolve the network
		/// as capped partitions whose first one starts at a cell chosen by the pulse count; the rest follow in cell-index
		/// order. Every excavated cell of the network is still resolved exactly once this pulse, every partition reads
		/// one static flow order walked over the whole network (FLOWWORKS_CHANNEL_OSCILLATION_1) and keeps its own balanced ledger. Returns false (the
		/// caller resolves the capped walk as before) when the network is exactly the cap.</summary>
		private bool ResolveRotatedNetwork(int seed, long pulseCount)
		{
			networkVisited.Clear();
			RM_StockMath.CollectComponent(seed, isSourcePred, isExcavatedPred, cardinalPred,
				networkVisited, networkSources, queue, neighbourScratch, networkCells, int.MaxValue);
			networkExcavated.Clear();
			for (int i = 0; i < networkCells.Count; i++)
			{
				if (IsExcavated(networkCells[i]))
				{
					networkExcavated.Add(networkCells[i]);
				}
			}
			if (networkCells.Count <= maxComponentCells)
			{
				return false;
			}
			// The capped walk marked only cells of this network; clear them so the partitions below re-walk it.
			for (int i = 0; i < networkExcavated.Count; i++)
			{
				visited.Remove(networkExcavated[i]);
			}
			networkExcavated.Sort();
			int n = networkExcavated.Count;
			// One flow order for the WHOLE network, walked once from all its supplying sources, inputs and sinks: a
			// partition away from the source would otherwise see every key equal and never spread (part 1's defect),
			// and the order stays the same static, acyclic one whichever way the seams fall this pulse.
			component.Clear();
			component.AddRange(networkCells);
			ComputeFlowOrder();
			// A large odd stride spreads successive starts across the network instead of creeping one cell a pulse.
			int start = networkExcavated[SeamSlot(pulseCount, n)];
			rotatedNetworks++;
			RM_StockMath.CollectComponent(start, isSourcePred, isExcavatedPred, cardinalPred,
				visited, componentSources, queue, neighbourScratch, component, maxComponentCells);
			ResolveComponent(pulseCount, true);
			for (int i = 0; i < n; i++)
			{
				int c = networkExcavated[i];
				if (visited.Contains(c))
				{
					continue;
				}
				RM_StockMath.CollectComponent(c, isSourcePred, isExcavatedPred, cardinalPred,
					visited, componentSources, queue, neighbourScratch, component, maxComponentCells);
				ResolveComponent(pulseCount, true);
			}
			return true;
		}

		private void ResolveComponent(long pulseCount, bool networkOrder = false)
		{
			if (levelExactEnabled && world is RM_ILevelWorld levelWorld)
			{
				if (part == null || part.Length != width * height)
				{
					part = new ushort[width * height];   // a world that keeps no part grid (the offline worlds)
				}
				ResolveExact(levelWorld, pulseCount, networkOrder);
				return;
			}
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
					// A shut sluice seals its cell: liquid neither enters nor leaves, the sink band included.
					if (!IsExcavated(c) || !world.IsSink(c) || IsSealed(c))
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

			if (networkOrder)
			{
				// Part 2: the hops were walked over the whole network; only the partition's membership is per-partition.
				componentSet.Clear();
				for (int i = 0; i < component.Count; i++)
				{
					componentSet.Add(component[i]);
				}
			}
			else
			{
				ComputeFlowOrder();
			}

			recipients.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (!IsExcavated(c))
				{
					continue;
				}
				if (fill[c] < depth[c] && !IsSealed(c))
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
					// P7: a dry recipient that cannot record the donor's fluid takes nothing, checked BEFORE the debit.
					if (fill[r] == 0 && !world.CanClaim(world.DonorFluid(donor, IsSource(donor))))
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
						if (creepWaterEnabled)
						{
							(frontStamp ??= new long[width * height])[r] = pulseCount + 1;
						}
					}
					fill[r] += 1;
					if (creepEnabled || creepWaterEnabled)
					{
						(receivedStamp ??= new long[width * height])[r] = pulseCount + 1;
					}
					moved++;
				}
				if (moved > 0)
				{
					receivedThisPass.Add(r);
				}
			}

			if (levelBySurfaceEnabled)
			{
				if (levelSetEnabled)
				{
					LevelSetWetRegions(pulseCount);
				}
				else
				{
					LevelWetRegions(pulseCount);
				}
			}
			if (creepWaterEnabled)
			{
				externalCredit += TopUpWaterMouths(pulseCount, perCell);
			}
			receivedThisPass.Clear();

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

		// ── WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: the exact-level pulse ─────────────────────────────────────

		/// <summary>The water (dL) a dug cell holds: fill·U + part.</summary>
		public long WaterOf(int c)
		{
			return fill[c] * (long)RM_LevelSolve.U + (part != null ? part[c] : 0);
		}

		/// <summary>Writes a dug cell's water as whole notches plus the part.</summary>
		public void SetWaterOf(int c, long w)
		{
			fill[c] = (byte)(w / RM_LevelSolve.U);
			if (part != null)
			{
				part[c] = (ushort)(w % RM_LevelSolve.U);
			}
		}

		private readonly List<int> exDug = new List<int>();
		private readonly Dictionary<int, int> exHops = new Dictionary<int, int>();
		private readonly HashSet<int> exAssigned = new HashSet<int>();
		private readonly Dictionary<int, long> exPondBefore = new Dictionary<int, long>();
		private readonly List<int> exCells = new List<int>();
		private readonly HashSet<int> exInDom = new HashSet<int>();
		private readonly List<int> exPonds = new List<int>();
		private readonly HashSet<int> exPondSet = new HashSet<int>();
		private readonly HashSet<int> exLimMouths = new HashSet<int>();
		private readonly Dictionary<long, int> exMouthEdge = new Dictionary<long, int>();
		private readonly List<int> exQueue = new List<int>();
		private readonly Dictionary<int, int> exIndex = new Dictionary<int, int>();
		private readonly Dictionary<int, HashSet<int>> exMouths = new Dictionary<int, HashSet<int>>();
		private readonly List<int> exSrcScratch = new List<int>();
		private long[] exOld = new long[16];
		private long[] exTarget = new long[16];
		private long[] exNew = new long[16];
		private long exCredit;

		/// <summary>One component, exact (northstar/level_water.py _exact_component): sinks drain up to flowPerPulse·U a sink
		/// square; then from each wet square in cell-index order (or a dry square beside a source) a DOMAIN is grown and solved
		/// (<see cref="ExactDomain"/>); the ledger balances to the dL.</summary>
		private void ResolveExact(RM_ILevelWorld lw, long pulseCount, bool networkOrder)
		{
			int U = RM_LevelSolve.U;
			// this partition's membership (a rotated network's partitions each resolve on their own cells)
			componentSet.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				componentSet.Add(component[i]);
			}
			exDug.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				if (IsExcavated(component[i]))
				{
					exDug.Add(component[i]);
				}
			}
			exDug.Sort();
			long before = 0;
			for (int i = 0; i < exDug.Count; i++)
			{
				before += WaterOf(exDug[i]);
			}
			long drained = 0;
			if (edgeSinksEnabled)
			{
				long per = flowPerPulse * (long)U;
				for (int i = 0; i < exDug.Count; i++)
				{
					int c = exDug[i];
					if (!world.IsSink(c) || IsSealed(c))
					{
						continue;
					}
					long w = WaterOf(c);
					long take = Math.Min(w, per);
					if (take > 0)
					{
						SetWaterOf(c, w - take);
						drained += take;
					}
				}
				exactDrainDl += drained;
				sinkDrained += drained / (float)U;
			}
			// sinkHops: BFS from every sink square through dug, unsealed squares of this partition; a draining domain lays its
			// remainder nearest the sink first, so a run drains to the last dL.
			exHops.Clear();
			if (edgeSinksEnabled)
			{
				hopFrontier.Clear();
				for (int i = 0; i < exDug.Count; i++)
				{
					int c = exDug[i];
					if (world.IsSink(c) && !IsSealed(c))
					{
						exHops[c] = 0;
						hopFrontier.Add(c);
					}
				}
				for (int head = 0; head < hopFrontier.Count; head++)
				{
					int c = hopFrontier[head];
					int hc = exHops[c];
					for (int d = 0; d < 4; d++)
					{
						int nb = Cardinal(c, d);
						if (nb < 0 || exHops.ContainsKey(nb) || !componentSet.Contains(nb) || !IsExcavated(nb) || IsSealed(nb))
						{
							continue;
						}
						exHops[nb] = hc + 1;
						hopFrontier.Add(nb);
					}
				}
				hopFrontier.Clear();
			}
			exPondBefore.Clear();
			exCredit = 0;
			exAssigned.Clear();
			for (int i = 0; i < exDug.Count; i++)
			{
				int c = exDug[i];
				if (exAssigned.Contains(c) || IsSealed(c))
				{
					continue;
				}
				object fl;
				if (WaterOf(c) > 0)
				{
					fl = world.CellFluid(c);
				}
				else
				{
					int src = -1;
					for (int d = 0; d < 4 && src < 0; d++)
					{
						int nb = Cardinal(c, d);
						if (nb >= 0 && componentSet.Contains(nb) && IsSource(nb) && !IsSealed(nb))
						{
							src = nb;
						}
					}
					if (src < 0)
					{
						continue;
					}
					fl = world.DonorFluid(src, true);
					if (!world.CanClaim(fl))
					{
						continue;
					}
				}
				if (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(fl)))
				{
					continue;
				}
				ExactDomain(lw, c, fl);
			}
			long after = 0;
			for (int i = 0; i < exDug.Count; i++)
			{
				after += WaterOf(exDug[i]);
			}
			long pondChange = 0;
			foreach (KeyValuePair<int, long> kv in exPondBefore)
			{
				pondChange += lw.BodyStockDl(kv.Key) - kv.Value;
			}
			exactCreditDl += exCredit;
			long imbalance = after - before + drained + pondChange - exCredit;
			if (imbalance != 0)
			{
				worstImbalance = Math.Max(worstImbalance, Math.Abs(imbalance) / (float)U);
				imbalanceReports.Add("exact: before=" + before + " dL after=" + after + " dL pondChange=" + pondChange
					+ " limitlessCredit=" + exCredit + " sinkDrain=" + drained + " imbalance=" + imbalance + " dL");
			}
			world.ComponentResolved(component);
		}

		private void ExactAddCell(int c)
		{
			if (exInDom.Contains(c) || exAssigned.Contains(c))
			{
				return;
			}
			exInDom.Add(c);
			exCells.Add(c);
			exQueue.Add(c);
		}

		private static bool SameFluid(object a, object b)
		{
			return ReferenceEquals(a, b);
		}

		private void ExactTouchSource(RM_ILevelWorld lw, int cell, int s, object fl)
		{
			if (!componentSet.Contains(s) || !IsSource(s) || IsSealed(s))
			{
				return;
			}
			object df = world.DonorFluid(s, true);
			if (!RM_StockMath.FluidsCompatible(true, fl, df))
			{
				return;
			}
			int bid = lw.LevelBodyOf(s);
			if (bid < 0)
			{
				exLimMouths.Add(cell);
				return;
			}
			int cap = Math.Min(depth[cell], lw.BedAt(s));
			long key = ((long)cell << 32) | (uint)bid;
			if (!exMouthEdge.TryGetValue(key, out int have) || cap > have)
			{
				exMouthEdge[key] = cap;
			}
			if (exPondSet.Add(bid))
			{
				exPonds.Add(bid);
				exQueue.Add(~bid);
			}
		}

		/// <summary>Grows one domain from <paramref name="seed"/> (level_water._domain) and solves it.</summary>
		private void ExactDomain(RM_ILevelWorld lw, int seed, object fl)
		{
			exCells.Clear();
			exInDom.Clear();
			exPonds.Clear();
			exPondSet.Clear();
			exLimMouths.Clear();
			exMouthEdge.Clear();
			exQueue.Clear();
			ExactAddCell(seed);
			for (int head = 0; head < exQueue.Count; head++)
			{
				int x = exQueue[head];
				if (x >= 0)
				{
					int c = x;
					bool wet = WaterOf(c) > 0;
					for (int d = 0; d < 4; d++)
					{
						int nb = Cardinal(c, d);
						if (nb < 0 || !componentSet.Contains(nb))
						{
							continue;
						}
						if (IsExcavated(nb))
						{
							if (IsSealed(nb) || exInDom.Contains(nb) || exAssigned.Contains(nb))
							{
								continue;
							}
							if (WaterOf(nb) > 0)
							{
								if (SameFluid(world.CellFluid(nb), fl))
								{
									ExactAddCell(nb);
								}
							}
							else if (wet && world.CanClaim(fl))
							{
								ExactAddCell(nb);   // the dry rim
							}
						}
						else
						{
							ExactTouchSource(lw, c, nb, fl);
						}
					}
				}
				else
				{
					int bid = ~x;
					exSrcScratch.Clear();
					for (int i = 0; i < component.Count; i++)
					{
						int s = component[i];
						if (IsSource(s) && lw.LevelBodyOf(s) == bid)
						{
							exSrcScratch.Add(s);
						}
					}
					exSrcScratch.Sort();
					for (int i = 0; i < exSrcScratch.Count; i++)
					{
						int s = exSrcScratch[i];
						if (IsSealed(s))
						{
							continue;
						}
						for (int d = 0; d < 4; d++)
						{
							int nb = Cardinal(s, d);
							if (nb < 0 || !componentSet.Contains(nb) || !IsExcavated(nb) || IsSealed(nb) || exAssigned.Contains(nb))
							{
								continue;
							}
							long wn = WaterOf(nb);
							if (wn > 0 && !SameFluid(world.CellFluid(nb), fl))
							{
								continue;
							}
							if (wn == 0 && !exInDom.Contains(nb) && !world.CanClaim(fl))
							{
								continue;
							}
							ExactAddCell(nb);
							ExactTouchSource(lw, nb, s, fl);
						}
					}
				}
			}
			for (int i = 0; i < exCells.Count; i++)
			{
				exAssigned.Add(exCells[i]);
			}
			bool drains = false;
			for (int i = 0; i < exCells.Count && !drains; i++)
			{
				drains = exHops.ContainsKey(exCells[i]);
			}
			const int Far = 1 << 20;
			if (drains)
			{
				exCells.Sort((a, b) =>
				{
					int ha = exHops.TryGetValue(a, out int va) ? va : Far;
					int hb = exHops.TryGetValue(b, out int vb) ? vb : Far;
					return ha != hb ? ha.CompareTo(hb) : a.CompareTo(b);
				});
			}
			else
			{
				exCells.Sort();
			}
			exPonds.Sort();
			ExactSolveDomain(lw, fl);
		}

		private void ExactCellEdges(RM_LevelSolve solve)
		{
			for (int i = 0; i < exCells.Count; i++)
			{
				int c = exCells[i];
				for (int d = 0; d < 2; d++)   // N and E: each undirected edge once (AddEdge adds both directions)
				{
					int nb = Cardinal(c, d);
					if (nb >= 0 && exIndex.TryGetValue(nb, out int j))
					{
						solve.AddEdge(i, j, Math.Min(depth[c], depth[nb]));
					}
				}
			}
		}

		/// <summary>level_water._solve_domain: the joint solve (or, beside a limitless source, every node full), the mouth pace
		/// by lambda, the canal re-solve, the write.</summary>
		private void ExactSolveDomain(RM_ILevelWorld lw, object fl)
		{
			int U = RM_LevelSolve.U;
			int nCells = exCells.Count;
			int nNodes = nCells + exPonds.Count;
			if (exOld.Length < nNodes)
			{
				int cap = Math.Max(nNodes, exOld.Length * 2);
				exOld = new long[cap];
				exTarget = new long[cap];
				exNew = new long[cap];
			}
			exIndex.Clear();
			exactSolve.Clear();
			for (int i = 0; i < nCells; i++)
			{
				int c = exCells[i];
				exIndex[c] = i;
				exactSolve.AddCell(depth[c], WaterOf(c));
			}
			long[] excess = new long[exPonds.Count];
			for (int k = 0; k < exPonds.Count; k++)
			{
				int bid = exPonds[k];
				int[] h = lw.BodyHistogram(bid);
				long dl = lw.BodyStockDl(bid);
				if (!exPondBefore.ContainsKey(bid))
				{
					exPondBefore[bid] = dl;
				}
				long cap = RM_LevelSolve.PondCapacity(h);
				long w = Math.Min(Math.Max(dl, 0), cap);
				excess[k] = dl - w;
				exactSolve.AddPond(h, w);
			}
			for (int i = 0; i < nNodes; i++)
			{
				exOld[i] = exactSolve.WaterOf(i);
			}
			ExactCellEdges(exactSolve);
			exMouths.Clear();
			foreach (KeyValuePair<long, int> kv in exMouthEdge)
			{
				int c = (int)(kv.Key >> 32);
				int bid = (int)(uint)kv.Key;
				exactSolve.AddEdge(exIndex[c], nCells + exPonds.IndexOf(bid), kv.Value);
				if (!exMouths.TryGetValue(bid, out HashSet<int> set))
				{
					set = exMouths[bid] = new HashSet<int>();
				}
				set.Add(c);
			}
			bool hasLim = exLimMouths.Count > 0;
			if (hasLim)
			{
				for (int i = 0; i < nNodes; i++)
				{
					exTarget[i] = exactSolve.CapBelow(i, 1);
				}
			}
			else
			{
				if (!exactSolve.Solve())
				{
					return;
				}
				for (int i = 0; i < nNodes; i++)
				{
					exTarget[i] = exactSolve.ResultOf(i);
				}
			}
			long perU = flowPerPulse * (long)U;
			long sumDelta = 0;
			for (int i = 0; i < nNodes; i++)
			{
				sumDelta += exTarget[i] - exOld[i];
			}
			long limTotal = hasLim ? -sumDelta : 0;
			long dead = nNodes;
			bool exchange = hasLim;
			for (int k = 0; k < exPonds.Count && !exchange; k++)
			{
				exchange = Math.Abs(exTarget[nCells + k] - exOld[nCells + k]) > dead;
			}
			for (int i = 0; i < nNodes; i++)
			{
				exNew[i] = exOld[i];
			}
			if (exchange)
			{
				long num = 1, den = 1;
				for (int k = 0; k < exPonds.Count; k++)
				{
					long dd = Math.Abs(exTarget[nCells + k] - exOld[nCells + k]);
					long limit = perU * (exMouths.TryGetValue(exPonds[k], out HashSet<int> ms) ? ms.Count : 0);
					if (dd > limit && limit * den < num * dd)
					{
						num = limit;
						den = dd;
					}
				}
				if (hasLim)
				{
					long dd = Math.Abs(limTotal);
					long limit = perU * exLimMouths.Count;
					if (dd > limit && limit * den < num * dd)
					{
						num = limit;
						den = dd;
					}
				}
				if (num == den)
				{
					for (int i = 0; i < nNodes; i++)
					{
						exNew[i] = exTarget[i];
					}
				}
				else
				{
					long r = 0;
					for (int i = 0; i < nNodes; i++)
					{
						exNew[i] = exOld[i] + RM_LevelSolve.TruncDiv((exTarget[i] - exOld[i]) * num, den);
						r += exNew[i] - exOld[i];
					}
					if (!hasLim)
					{
						int guard = 0;
						while (r != 0 && guard < 4 * nNodes + 4)
						{
							guard++;
							for (int i = 0; i < nCells && r != 0; i++)
							{
								long lo = Math.Min(exOld[i], exTarget[i]);
								long hi = Math.Max(exOld[i], exTarget[i]);
								if (r > 0 && exNew[i] > lo)
								{
									exNew[i]--;
									r--;
								}
								else if (r < 0 && exNew[i] < hi)
								{
									exNew[i]++;
									r++;
								}
							}
						}
						if (r != 0)
						{
							return;   // cannot happen; never write a step that would not conserve
						}
					}
				}
			}
			if (hasLim)
			{
				long gain = 0;
				for (int i = 0; i < nNodes; i++)
				{
					gain += exNew[i] - exOld[i];
				}
				exCredit += gain;
				if (gain != 0)
				{
					lw.NoteLimitlessDl(fl, gain);
				}
			}
			// the canal squares, re-solved on their own (the ponds keep what the exchange gave them)
			canalSolve.Clear();
			for (int i = 0; i < nCells; i++)
			{
				canalSolve.AddCell(depth[exCells[i]], exNew[i]);
			}
			ExactCellEdges(canalSolve);
			if (!canalSolve.Solve())
			{
				return;
			}
			for (int i = 0; i < nCells; i++)
			{
				int c = exCells[i];
				long w = canalSolve.ResultOf(i);
				if (w > 0 && WaterOf(c) == 0)
				{
					world.Claim(c, fl);
				}
				SetWaterOf(c, w);
			}
			for (int k = 0; k < exPonds.Count; k++)
			{
				lw.SetBodyStockDl(exPonds[k], exNew[nCells + k] + excess[k]);
			}
		}

		private readonly List<int> regionSeeds = new List<int>();
		private readonly HashSet<int> inRegion = new HashSet<int>();
		private readonly List<int> regionCells = new List<int>();
		private readonly List<int> regionRim = new List<int>();
		private readonly HashSet<int> rimSet = new HashSet<int>();
		private readonly Dictionary<int, int> gaveThisPulse = new Dictionary<int, int>();
		private readonly Dictionary<int, int> gotThisPulse = new Dictionary<int, int>();
		private readonly SortedSet<int>[] donorsBySurface = { new SortedSet<int>(), new SortedSet<int>(), new SortedSet<int>(), new SortedSet<int>(), new SortedSet<int>() };
		/// <summary>Takers keyed by <see cref="TakerKey"/> (deepest bed, then lowest index first), so Min is the pick.</summary>
		private readonly SortedSet<long>[] takersBySurface = { new SortedSet<long>(), new SortedSet<long>(), new SortedSet<long>(), new SortedSet<long>(), new SortedSet<long>() };

		private readonly HashSet<int> receivedThisPass = new HashSet<int>();
		private readonly List<int> topUpOrder = new List<int>();

		/// <summary>CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME: the recipient list is fixed before anything moves, so a brim
		/// mouth is not a recipient in the pulse it passes its unit on (the neighbour pass or the level solve moves it), and
		/// with water creep on the source refilled it only NEXT pulse: the mouth read dry every other pulse behind a wet front,
		/// and the front and the source's payments ran at half the one-cell-a-pulse the creep rule promises. After the pass
		/// and the solve, a dug square beside a supplying WATER source that took nothing this pulse and has room takes up to
		/// <paramref name="perCell"/> from that source (cell-index order, so a scarce body still pays by map position). The
		/// unit it takes is held by creep like any other. Returns the levels the sources paid (the ledger's credit).</summary>
		private float TopUpWaterMouths(long pulseCount, int perCell)
		{
			float credit = 0f;
			topUpOrder.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsExcavated(c) && fill[c] < depth[c] && !IsSealed(c) && !receivedThisPass.Contains(c) && componentSet.Contains(c))
				{
					topUpOrder.Add(c);
				}
			}
			topUpOrder.Sort();
			for (int i = 0; i < topUpOrder.Count; i++)
			{
				int r = topUpOrder[i];
				int moved = 0;
				while (moved < perCell && fill[r] < depth[r])
				{
					int donor = -1;
					for (int d = 0; d < 4 && donor < 0; d++)
					{
						int n = Cardinal(r, d);
						if (n < 0 || IsSealed(n) || !IsSource(n) || !world.CanSupply(n) || !HeadAllows(n, r))
						{
							continue;
						}
						object fl = world.DonorFluid(n, true);
						if (RM_StockMath.ViscosityStride(world.TicksPerTile(fl)) > 1
							|| !RM_StockMath.FluidsCompatible(fill[r] > 0, world.CellFluid(r), fl)
							|| (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(fl)))
							|| (fill[r] == 0 && !world.CanClaim(fl)))
						{
							continue;
						}
						donor = n;
					}
					if (donor < 0 || !world.TryDebitLevel(donor))
					{
						break;
					}
					credit += 1f;
					if (fill[r] == 0)
					{
						world.Claim(r, world.DonorFluid(donor, true));
						(frontStamp ??= new long[width * height])[r] = pulseCount + 1;
					}
					fill[r] += 1;
					(receivedStamp ??= new long[width * height])[r] = pulseCount + 1;
					moved++;
				}
			}
			return credit;
		}

		/// <summary>True when the creep rule holds this cell's level back this pulse (it received a level of a fluid
		/// whose creep switch is on).</summary>
		private bool HeldByCreep(int c, object fluid, long pulseCount)
		{
			return RM_StockMath.ViscosityStride(world.TicksPerTile(fluid)) > 1
				? creepEnabled && receivedStamp != null && receivedStamp[c] == pulseCount + 1
				: creepWaterEnabled && frontStamp != null && frontStamp[c] == pulseCount + 1;
		}

		/// <summary>WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND, communicating vessels: the neighbour-to-neighbour pass above
		/// can leave a terrace (2,2,1,1,0 in a flat D=2 run) where every step is one unit, so no single neighbour may give.
		/// Real water connected through wet squares levels anyway. So, per connected WET region of one fluid (cells wet
		/// before this pulse's creep, in this partition, not sealed), a unit moves from the region's highest surface to the
		/// lowest surface among the region and its dug rim (a rim cell must accept the fluid), while those differ by two or
		/// more. Each cell gives at most, and takes at most, flowPerPulse in this pass, and a region cell never gives its
		/// LAST unit here (so no connector goes dry mid-pass and the region stays connected through wet squares; the
		/// neighbour rules above still empty it). Ties: donor = highest surface then
		/// lowest cell index; taker = lowest surface, then deepest bed, then lowest index. Regions in order of their lowest
		/// cell index. Every move lowers sum(surface^2) by at least 2, so this cannot oscillate; it moves liquid only inside
		/// the component, so the ledger is untouched. A rim cell joins the region next pulse, so the wet front still
		/// advances one cell a pulse.</summary>
		private void LevelWetRegions(long pulseCount)
		{
			int per = flowPerPulse;
			if (per <= 0)
			{
				return;
			}
			gaveThisPulse.Clear();
			gotThisPulse.Clear();
			inRegion.Clear();
			regionSeeds.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsExcavated(c) && fill[c] > 0 && !IsSealed(c) && componentSet.Contains(c))
				{
					regionSeeds.Add(c);
				}
			}
			regionSeeds.Sort();
			for (int s = 0; s < regionSeeds.Count; s++)
			{
				int seed = regionSeeds[s];
				if (inRegion.Contains(seed))
				{
					continue;
				}
				object fluid = world.CellFluid(seed);
				if (HeldByCreep(seed, fluid, pulseCount))
				{
					continue;
				}
				// The region: 4-way, wet, same recorded fluid, not held by creep.
				regionCells.Clear();
				regionCells.Add(seed);
				inRegion.Add(seed);
				for (int head = 0; head < regionCells.Count; head++)
				{
					int c = regionCells[head];
					for (int d = 0; d < 4; d++)
					{
						int n = Cardinal(c, d);
						if (n < 0 || inRegion.Contains(n) || !componentSet.Contains(n) || !IsExcavated(n) || IsSealed(n)
							|| fill[n] == 0 || !ReferenceEquals(world.CellFluid(n), fluid) || HeldByCreep(n, fluid, pulseCount))
						{
							continue;
						}
						inRegion.Add(n);
						regionCells.Add(n);
					}
				}
				if (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(fluid)))
				{
					continue;
				}
				regionRim.Clear();
				rimSet.Clear();
				for (int i = 0; i < regionCells.Count; i++)
				{
					int c = regionCells[i];
					for (int d = 0; d < 4; d++)
					{
						int n = Cardinal(c, d);
						if (n < 0 || inRegion.Contains(n) || rimSet.Contains(n) || !componentSet.Contains(n) || !IsExcavated(n)
							|| IsSealed(n) || fill[n] >= depth[n] || !RM_StockMath.FluidsCompatible(fill[n] > 0, world.CellFluid(n), fluid))
						{
							continue;
						}
						rimSet.Add(n);
						regionRim.Add(n);
					}
				}
				for (int b = 0; b < 5; b++)
				{
					donorsBySurface[b].Clear();
					takersBySurface[b].Clear();
				}
				for (int i = 0; i < regionCells.Count; i++)
				{
					int c = regionCells[i];
					if (fill[c] >= 2 && GotOrGave(gaveThisPulse, c) < per)
					{
						donorsBySurface[Bucket(c)].Add(c);
					}
					if (fill[c] < depth[c] && GotOrGave(gotThisPulse, c) < per)
					{
						takersBySurface[Bucket(c)].Add(TakerKey(c));
					}
				}
				for (int i = 0; i < regionRim.Count; i++)
				{
					int c = regionRim[i];
					if (GotOrGave(gotThisPulse, c) < per)
					{
						takersBySurface[Bucket(c)].Add(TakerKey(c));
					}
				}
				while (true)
				{
					int db = 4;
					while (db >= 0 && donorsBySurface[db].Count == 0)
					{
						db--;
					}
					int tb = 0;
					while (tb < 5 && takersBySurface[tb].Count == 0)
					{
						tb++;
					}
					if (db < 0 || tb >= 5 || db - tb < 2)
					{
						break;
					}
					int donor = donorsBySurface[db].Min;
					int taker = (int)(takersBySurface[tb].Min % (width * height));
					if (fill[taker] == 0 && !world.CanClaim(fluid))
					{
						takersBySurface[tb].Remove(TakerKey(taker));   // P7: no identity key free for a dry rim cell
						continue;
					}
					donorsBySurface[db].Remove(donor);
					takersBySurface[db].Remove(TakerKey(donor));
					takersBySurface[tb].Remove(TakerKey(taker));
					donorsBySurface[tb].Remove(taker);
					fill[donor] -= 1;
					if (fill[taker] == 0)
					{
						world.Claim(taker, fluid);
					}
					fill[taker] += 1;
					int gave = GotOrGave(gaveThisPulse, donor) + 1;
					gaveThisPulse[donor] = gave;
					int got = GotOrGave(gotThisPulse, taker) + 1;
					gotThisPulse[taker] = got;
					if (fill[donor] >= 2 && gave < per)
					{
						donorsBySurface[Bucket(donor)].Add(donor);
					}
					if (fill[donor] < depth[donor] && GotOrGave(gotThisPulse, donor) < per)
					{
						takersBySurface[Bucket(donor)].Add(TakerKey(donor));
					}
					if (fill[taker] < depth[taker] && got < per)
					{
						takersBySurface[Bucket(taker)].Add(TakerKey(taker));
					}
					if (inRegion.Contains(taker) && fill[taker] >= 2 && GotOrGave(gaveThisPulse, taker) < per)
					{
						donorsBySurface[Bucket(taker)].Add(taker);
					}
				}
			}
		}

		// ── WATER_LEVELSET_SOLVE: per-region flat-level solve ─────────────────────────────────────────────

		private sealed class LsComp
		{
			public int band;
			public readonly List<int> cells = new List<int>();
			public readonly List<int> children = new List<int>();
			public int water;
			public int cap;
			public long key;
		}

		private readonly List<LsComp> lsComps = new List<LsComp>();
		private int lsCompCount;
		private int[] lsCompId;      // (band - 1) * N + cell -> comp index + 1 (valid only under lsStamp)
		private int[] lsCompStamp;
		private int[] lsDomainStamp;
		private int[] lsNewFill;
		private int lsStampValue;
		private readonly List<int> lsDomain = new List<int>();
		private readonly List<int> lsPick = new List<int>();
		private readonly HashSet<int> lsPicked = new HashSet<int>();
		private const int LsMaxBands = 8;

		/// <summary>WATER_LEVELSET_SOLVE. Per connected WET region of one fluid (as <see cref="LevelWetRegions"/> builds it:
		/// wet, same fluid, in this partition, not sealed, not held by creep) plus its DRY dug rim (one ring, so the wet
		/// front still advances one square a pulse), the region's whole volume V is re-laid at the flat level it would
		/// settle to — communicating vessels — and the result is exact in whole units:
		/// <list type="bullet">
		/// <item>Water is counted in BANDS: band L is the layer between surface -L and -L+1; a square of dug depth d owns
		/// bands 1..d and its fill f occupies its lowest f bands. At each band the domain splits into the connected pieces of
		/// squares deep enough to own it (a merge tree, at most 4 levels deep).</item>
		/// <item>Bottom up, each piece counts the water already below its band (trapped: it cannot climb a sill to another
		/// piece). Top down, the piece hands its FREE water to its deeper pieces until they are full, and only then lays
		/// the rest on its own band. So a pit never drains through a dry sill, and a stepped floor ends flat.</item>
		/// <item>The last part-filled band takes r squares, grown best-first as ONE contiguous patch inside the piece (see
		/// <see cref="CellKey"/>: toward a sink, else toward the deepest bed, keeping to squares already wet, and away from a
		/// live inflow so the mouth keeps room). So too little water for a sheet is a single patch at the minimum depth,
		/// never 0, deep, 0 and never 0,1,0,1.</item>
		/// </list>
		/// Moves liquid only inside the component (the ledger is untouched); a state the solve produces solves to itself,
		/// so it settles. O(domain x bands) per region per pulse.</summary>
		private void LevelSetWetRegions(long pulseCount)
		{
			int n = width * height;
			if (lsDomainStamp == null || lsDomainStamp.Length != n)
			{
				lsDomainStamp = new int[n];
				lsCompStamp = new int[n * LsMaxBands];
				lsCompId = new int[n * LsMaxBands];
				lsNewFill = new int[n];
				lsStampValue = 0;
			}
			inRegion.Clear();
			regionSeeds.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsExcavated(c) && fill[c] > 0 && !IsSealed(c) && componentSet.Contains(c))
				{
					regionSeeds.Add(c);
				}
			}
			regionSeeds.Sort();
			for (int s = 0; s < regionSeeds.Count; s++)
			{
				int seed = regionSeeds[s];
				if (inRegion.Contains(seed) || fill[seed] == 0)
				{
					continue;
				}
				object fluid = world.CellFluid(seed);
				if (HeldByCreep(seed, fluid, pulseCount))
				{
					continue;
				}
				regionCells.Clear();
				regionCells.Add(seed);
				inRegion.Add(seed);
				for (int head = 0; head < regionCells.Count; head++)
				{
					int c = regionCells[head];
					for (int d = 0; d < 4; d++)
					{
						int nb = Cardinal(c, d);
						if (nb < 0 || inRegion.Contains(nb) || !componentSet.Contains(nb) || !IsExcavated(nb) || IsSealed(nb))
						{
							continue;
						}
						if (fill[nb] == 0)
						{
							// L7 live 2026-10-16 (1,0,1,0 loaded from a save): a lone unit with dry squares on both sides was
							// its own region, solved to itself, and never met its neighbour. A dry gap of ONE dug square joins
							// the wet squares beyond it (the gap is the rim of both), so striped water gathers into one patch.
							for (int d2 = 0; d2 < 4; d2++)
							{
								int far = Cardinal(nb, d2);
								if (far < 0 || far == c || inRegion.Contains(far) || !componentSet.Contains(far) || !IsExcavated(far)
									|| IsSealed(far) || fill[far] == 0 || !ReferenceEquals(world.CellFluid(far), fluid)
									|| HeldByCreep(far, fluid, pulseCount))
								{
									continue;
								}
								inRegion.Add(far);
								regionCells.Add(far);
							}
							continue;
						}
						if (!ReferenceEquals(world.CellFluid(nb), fluid) || HeldByCreep(nb, fluid, pulseCount))
						{
							continue;
						}
						inRegion.Add(nb);
						regionCells.Add(nb);
					}
				}
				if (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(fluid)))
				{
					continue;
				}
				SolveRegion(fluid);
			}
		}

		private void SolveRegion(object fluid)
		{
			int n = width * height;
			if (++lsStampValue == int.MaxValue)
			{
				Array.Clear(lsDomainStamp, 0, lsDomainStamp.Length);
				Array.Clear(lsCompStamp, 0, lsCompStamp.Length);
				lsStampValue = 1;
			}
			int stamp = lsStampValue;
			lsDomain.Clear();
			int volume = 0;
			int maxBand = 0;
			for (int i = 0; i < regionCells.Count; i++)
			{
				int c = regionCells[i];
				lsDomainStamp[c] = stamp;
				lsDomain.Add(c);
				volume += fill[c];
			}
			// The dry rim: a dug, unsealed, dry square of this partition beside the region, that may record the fluid.
			bool canClaim = world.CanClaim(fluid);
			if (canClaim)
			{
				for (int i = 0; i < regionCells.Count; i++)
				{
					int c = regionCells[i];
					for (int d = 0; d < 4; d++)
					{
						int nb = Cardinal(c, d);
						if (nb < 0 || lsDomainStamp[nb] == stamp || !componentSet.Contains(nb) || !IsExcavated(nb) || IsSealed(nb)
							|| fill[nb] != 0)
						{
							continue;
						}
						lsDomainStamp[nb] = stamp;
						lsDomain.Add(nb);
					}
				}
			}
			for (int i = 0; i < lsDomain.Count; i++)
			{
				int dep = Math.Min((int)depth[lsDomain[i]], LsMaxBands);
				if (dep > maxBand)
				{
					maxBand = dep;
				}
				lsNewFill[lsDomain[i]] = 0;
			}
			// FLOWWORKS_SLUICE_FIX_BELOW_SOURCE_LUCK: this region drains only if a sink is reachable from it. Component-wide, a
			// region cut off by a shut sluice keyed every square Far and fell back to cell index, so the mouth kept its unit
			// (upstream stayed dry) in one direction and not the other.
			bool drains = false;
			for (int i = 0; i < lsDomain.Count && !drains; i++)
			{
				drains = sinkHops.ContainsKey(lsDomain[i]);
			}
			// Merge tree: the connected pieces of each band, shallow band first (a deeper piece's parent is created first).
			lsCompCount = 0;
			for (int band = 1; band <= maxBand; band++)
			{
				int off = (band - 1) * n;
				for (int i = 0; i < lsDomain.Count; i++)
				{
					int c0 = lsDomain[i];
					if (depth[c0] < band || lsCompStamp[off + c0] == stamp)
					{
						continue;
					}
					LsComp comp = NewComp(band);
					int id = lsCompCount;   // 1-based id of the comp just made
					if (band > 1)
					{
						lsComps[lsCompId[off - n + c0] - 1].children.Add(id - 1);
					}
					lsCompStamp[off + c0] = stamp;
					lsCompId[off + c0] = id;
					comp.cells.Add(c0);
					for (int head = 0; head < comp.cells.Count; head++)
					{
						int c = comp.cells[head];
						for (int d = 0; d < 4; d++)
						{
							int nb = Cardinal(c, d);
							if (nb < 0 || lsDomainStamp[nb] != stamp || depth[nb] < band || lsCompStamp[off + nb] == stamp)
							{
								continue;
							}
							lsCompStamp[off + nb] = stamp;
							lsCompId[off + nb] = id;
							comp.cells.Add(nb);
						}
					}
				}
			}
			// Bottom up: water already at or below each piece's band, capacity, and the piece's priority key.
			for (int k = lsCompCount - 1; k >= 0; k--)
			{
				LsComp comp = lsComps[k];
				int present = 0;
				long key = long.MaxValue;
				for (int i = 0; i < comp.cells.Count; i++)
				{
					int c = comp.cells[i];
					if (fill[c] > depth[c] - comp.band)
					{
						present++;
					}
					long ck = CellKey(c, drains);
					if (ck < key)
					{
						key = ck;
					}
				}
				comp.water = present;
				comp.cap = comp.cells.Count;
				for (int j = 0; j < comp.children.Count; j++)
				{
					LsComp ch = lsComps[comp.children[j]];
					comp.water += ch.water;
					comp.cap += ch.cap;
				}
				comp.key = key;
				comp.children.Sort((a, b) => lsComps[a].key.CompareTo(lsComps[b].key));
			}
			// Top down from each band-1 piece (the domain is connected, so there is one; a guard keeps any other honest).
			int laid = 0;
			for (int k = 0; k < lsCompCount; k++)
			{
				if (lsComps[k].band == 1)
				{
					laid += Assign(k, lsComps[k].water, drains);
				}
			}
			if (laid != volume)
			{
				return;   // cannot happen (every unit is counted once); never write a solve that would not conserve
			}
			for (int i = 0; i < lsDomain.Count; i++)
			{
				int c = lsDomain[i];
				int f = lsNewFill[c];
				if (f == fill[c])
				{
					continue;
				}
				if (fill[c] == 0 && f > 0)
				{
					world.Claim(c, fluid);
				}
				fill[c] = (byte)f;
			}
		}

		private LsComp NewComp(int band)
		{
			if (lsCompCount == lsComps.Count)
			{
				lsComps.Add(new LsComp());
			}
			LsComp comp = lsComps[lsCompCount++];
			comp.band = band;
			comp.cells.Clear();
			comp.children.Clear();
			comp.water = 0;
			comp.cap = 0;
			comp.key = 0;
			return comp;
		}

		/// <summary>The seam start for pulse <paramref name="pulseCount"/> over <paramref name="n"/> network cells: a large stride
		/// coprime to n, so n successive pulses visit every start once. FLOWWORKS_STRIDE_FIX_WALKS_INTO_WALL: the bare 7919
		/// stride shares a factor with any n that is a multiple of 7919 (every start was cell 0 at n = 7919).</summary>
		public static int SeamSlot(long pulseCount, int n)
		{
			long stride = 7919;
			while (Gcd(stride, n) != 1)
			{
				stride += 2;
			}
			return (int)((pulseCount % n) * stride % n);
		}

		private static long Gcd(long a, long b)
		{
			while (b != 0)
			{
				long t = a % b;
				a = b;
				b = t;
			}
			return a;
		}

		/// <summary>Priority of a square for the part-filled band (lowest first; the cell index makes it unique), from this
		/// pulse's static flow order. A draining component: nearest a sink, then already wet. Otherwise nearest the
		/// component's deepest bed, then already wet, then (while a source or input still feeds the component) FARTHEST
		/// from the inflow, so the mouth keeps room and the inflow keeps coming.</summary>
		private long CellKey(int c, bool drains)
		{
			const long Far = 1 << 20;
			long n = width * height;
			long wet = fill[c] > 0 && !IsLiveMouth(c) ? 0 : 1;
			if (drains)
			{
				return ((sinkHops.TryGetValue(c, out int k) ? k : Far) * 2 + wet) * n + c;
			}
			long low = lowHops.TryGetValue(c, out int lh) ? lh : Far;
			long src = sourceHops.Count == 0 ? 0 : sourceHops.TryGetValue(c, out int h) ? Far - h : 2 * Far;
			return ((low * 2 + wet) * (2 * Far + 1) + src) * n + c;
		}

		/// <summary>CANAL_INLET_DIAGNOSE_FIRST_CELL_ONLY: a dug square beside a supplying source. Its unit never stays for being
		/// wet: the source refills a brim mouth only once the mouth passes its unit on, and the neighbour pass no longer moves a
		/// drop of one, so a wet-first mouth held a fed D=1 run at 1,0,0,0 for ever.</summary>
		private bool IsLiveMouth(int c)
		{
			// FLOWWORKS_PUMP_FIX_D1_CANAL_STALLS: a pump or drill inlet is a mouth too. It is hop 0 of the flow order like a
			// source's cell (ComputeFlowOrder), and its driver pours only when the inlet has room, so a wet-first inlet held a
			// D=1 canal fed by a driver alone at 1,0,0,0 for ever.
			if (externalInput != null && IsExcavated(c) && !IsSealed(c) && externalInput(c))
			{
				return true;
			}
			for (int d = 0; d < 4; d++)
			{
				int nb = Cardinal(c, d);
				if (nb >= 0 && IsSource(nb) && world.CanSupply(nb) && HeadAllows(nb, c))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Lays <paramref name="amount"/> units into piece <paramref name="k"/> and its deeper pieces. Returns the units laid.</summary>
		private int Assign(int k, int amount, bool drains)
		{
			LsComp comp = lsComps[k];
			int free = amount;
			for (int j = 0; j < comp.children.Count; j++)
			{
				free -= lsComps[comp.children[j]].water;
			}
			int laid = 0;
			for (int j = 0; j < comp.children.Count; j++)
			{
				LsComp ch = lsComps[comp.children[j]];
				int give = Math.Max(0, Math.Min(free, ch.cap - ch.water));
				free -= give;
				laid += Assign(comp.children[j], ch.water + give, drains);
			}
			int r = Math.Max(0, Math.Min(free, comp.cells.Count));
			if (r > 0)
			{
				PickBand(comp, r, drains);
				for (int i = 0; i < lsPick.Count; i++)
				{
					lsNewFill[lsPick[i]]++;
				}
				laid += lsPick.Count;
			}
			return laid;
		}

		private readonly SortedSet<long> lsFrontier = new SortedSet<long>();
		private readonly List<int> lsDeferred = new List<int>();

		/// <summary>The r squares of <paramref name="comp"/> that hold its band: grown best-first (by <see cref="CellKey"/>)
		/// from the comp's best square through its own squares, so the part-filled band is always ONE contiguous patch.</summary>
		private void PickBand(LsComp comp, int r, bool drains)
		{
			lsPick.Clear();
			if (r >= comp.cells.Count)
			{
				lsPick.AddRange(comp.cells);
				return;
			}
			int n = width * height;
			int off = (comp.band - 1) * n;
			int id = lsCompId[off + comp.cells[0]];
			long best = long.MaxValue;
			for (int i = 0; i < comp.cells.Count; i++)
			{
				long k = CellKey(comp.cells[i], drains);
				if (k < best)
				{
					best = k;
				}
			}
			lsPicked.Clear();
			lsFrontier.Clear();
			lsFrontier.Add(best);
			lsPicked.Add((int)(best % n));
			// LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY: a live mouth is passed THROUGH and filled last. The solve only re-lays the
			// region's own volume, and the source adds a unit only when a mouth has room, so a brim mouth that kept its band
			// left a shallow rim (or a square beyond the mouth) dry for ever beside a limitless source (FillsFromLimitless at
			// the shipped flags: 194/2000 scenes). Deferred, the mouth is the square left short and the source tops it up.
			bool fed = !drains && sourceHops.Count > 0;
			lsDeferred.Clear();
			while (lsPick.Count < r && lsFrontier.Count > 0)
			{
				long top = lsFrontier.Min;
				lsFrontier.Remove(top);
				int c = (int)(top % n);
				if (fed && IsLiveMouth(c))
				{
					lsDeferred.Add(c);
				}
				else
				{
					lsPick.Add(c);
				}
				for (int d = 0; d < 4; d++)
				{
					int nb = Cardinal(c, d);
					if (nb < 0 || lsCompStamp[off + nb] != lsStampValue || lsCompId[off + nb] != id || !lsPicked.Add(nb))
					{
						continue;
					}
					lsFrontier.Add(CellKey(nb, drains));
				}
			}
			for (int i = 0; i < lsDeferred.Count && lsPick.Count < r; i++)
			{
				lsPick.Add(lsDeferred[i]);
			}
		}

		/// <summary>Surface bucket 0..4 for surface fill - depth in -4..0.</summary>
		private int Bucket(int c)
		{
			return fill[c] - depth[c] + Superdeep;
		}

		private static int GotOrGave(Dictionary<int, int> counts, int c)
		{
			return counts.TryGetValue(c, out int v) ? v : 0;
		}

		/// <summary>Taker order within one surface bucket: the deepest bed, then the lowest cell index (depth does not
		/// change during the pass, so the key is stable).</summary>
		private long TakerKey(int c)
		{
			return (long)(Superdeep - depth[c]) * (width * height) + c;
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
			if (externalInput != null)
			{
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (IsExcavated(c) && !IsSealed(c) && externalInput(c))
					{
						sourceHops[c] = 0;   // an input cell is hop 0, like a source's own cell
						hopFrontier.Add(c);
					}
				}
			}
			HopsFrom(sourceHops, false);
			hopFrontier.Clear();
			if (edgeSinksEnabled)
			{
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (IsExcavated(c) && world.IsSink(c) && !IsSealed(c))
					{
						hopFrontier.Add(c);
					}
				}
			}
			HopsFrom(sinkHops, true);
			lowHops.Clear();
			hopFrontier.Clear();
			if (levelBySurfaceEnabled)
			{
				int deepest = 0;
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (IsExcavated(c) && !IsSealed(c) && depth[c] > deepest)
					{
						deepest = depth[c];
					}
				}
				for (int i = 0; i < component.Count; i++)
				{
					int c = component[i];
					if (IsExcavated(c) && !IsSealed(c) && depth[c] == deepest)
					{
						hopFrontier.Add(c);
					}
				}
				HopsFrom(lowHops, true);
			}
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
					if (n < 0 || hops.ContainsKey(n) || !componentSet.Contains(n) || !IsExcavated(n) || IsSealed(n))
					{
						continue;
					}
					hops[n] = hc + 1;
					hopFrontier.Add(n);
				}
			}
		}

		/// <summary>LEVEL BY SURFACE (<see cref="levelBySurfaceEnabled"/>), or else GRAVITY (a neighbour gives to a deeper
		/// cell) or OVERFLOW (a brimming neighbour gives to any cell with room); filtered by budget, no-mix, viscosity and the flow order. Fixed direction order, strict &gt;
		/// on the score. Returns -1 for no donor.</summary>
		private int PickDonor(int r, byte depthR, long pulseCount)
		{
			int best = -1;
			int bestScore = -1;
			for (int i = 0; i < 4; i++)
			{
				int n = Cardinal(r, i);
				if (n < 0 || IsSealed(n))
				{
					continue;
				}
				byte dn;
				byte fn;
				bool source = IsSource(n);
				if (source)
				{
					if (!world.CanSupply(n) || !HeadAllows(n, r))
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
				if (!source && HeldByCreep(n, donorFluid, pulseCount))
				{
					continue; // THICK_LIQUID_CREEP_1: filled this pulse, so it cannot pass a thick liquid on until the next
				}
				int score;
				if (levelBySurfaceEnabled)
				{
					// Surfaces relative to ground: a source is brim-full (0); a dug cell is fill - depth (-4..0).
					int drop = (fn - dn) - (fill[r] - depthR);
					if (drop < 1 || (drop == 1 && !source && levelSetEnabled))
					{
						continue;
					}
					if (!source && (!componentSet.Contains(n)
							|| (drop == 1 && !RM_StockMath.MayFlowBetween(
								HopsOf(sourceHops, n), HopsOf(sinkHops, n), HopsOf(lowHops, n), dn,
								HopsOf(sourceHops, r), HopsOf(sinkHops, r), HopsOf(lowHops, r), depthR))))
					{
						continue;
					}
					// Highest surface gives first; ties to the deeper bed, then the fixed direction order.
					score = source ? 1000 : ((fn - dn + Superdeep + 1) * 10 + dn);
				}
				else
				{
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
					score = source ? 1000 : (fn * 10 + dn);
				}
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
		/// <paramref name="sameFluidAsSeed"/> (optional) limits the walk to cells of the seed's fluid: touching
		/// water and tar are separate bodies (owner ruling 2026-10-06).</summary>
		public static int CollectBody(int width, int height, int seed, Func<int, bool> isSource, Func<int, int> ownedBody,
			int maxCells, List<int> found, List<int> fillQueue, HashSet<int> fillSeen,
			out bool touchesEdge, out bool truncated, Func<int, bool> sameFluidAsSeed = null)
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
				// Truncated only when a further eligible cell exists beyond the cap: a body of exactly maxCells
				// cells, fully explored, is complete (GPT FlowWorks review #28).
				if (found.Count >= maxCells)
				{
					truncated = true;
					break;
				}
				found.Add(c);
				int cx = c % width;
				int cz = c / width;
				if (cx == 0 || cx == width - 1 || cz == 0 || cz == height - 1)
				{
					touchesEdge = true;
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
					// Owner ruling 2026-10-06: touching natural liquids of DIFFERENT fluids stay separate bodies, so
					// a neighbour of another fluid neither joins this body nor claims it for an owned one.
					if (sameFluidAsSeed != null && !sameFluidAsSeed(n))
					{
						continue;
					}
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
