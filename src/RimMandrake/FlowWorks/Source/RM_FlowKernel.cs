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

	/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: what the exact-level kernel (<see cref="RM_FlowKernel"/>)
	/// reads and writes about natural bodies, in decilitres. Implemented beside <see cref="RM_IFlowWorld"/> (the game on
	/// RM_MapComponent_Excavation, the selftest on its array worlds). Every world implements it: the kernel has no other engine.</summary>
	public interface RM_ILevelWorld
	{
		/// <summary>The LIMITED body behind source <paramref name="src"/> (an id), or -1 when it never runs down (limitless, or
		/// the source budget off), or <see cref="RM_FlowKernel.LevelBodyDisabled"/> (-2) when its liquid is switched off in Mod
		/// Settings and it feeds nothing at all.</summary>
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

	/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: a set of grid indices (with an optional int per member) cleared in
	/// O(1) by a generation stamp: the exact path's per-partition and per-domain membership, which a HashSet paid a hash
	/// for on every neighbour look. Indices must lie in [0, the size given to Reset).</summary>
	internal sealed class RM_StampSet
	{
		private int[] stamp = new int[0];
		private int[] value = new int[0];
		private int gen;

		public void Reset(int size)
		{
			if (stamp.Length < size)
			{
				stamp = new int[size];
				value = new int[size];
				gen = 0;
			}
			if (gen == int.MaxValue)
			{
				Array.Clear(stamp, 0, stamp.Length);
				gen = 0;
			}
			gen++;
		}

		public bool Contains(int i)
		{
			return stamp[i] == gen;
		}

		/// <summary>True if <paramref name="i"/> was not yet a member.</summary>
		public bool Add(int i)
		{
			if (stamp[i] == gen)
			{
				return false;
			}
			stamp[i] = gen;
			return true;
		}

		public void Set(int i, int v)
		{
			stamp[i] = gen;
			value[i] = v;
		}

		public bool TryGetValue(int i, out int v)
		{
			if (stamp[i] == gen)
			{
				v = value[i];
				return true;
			}
			v = 0;
			return false;
		}

		public void Remove(int i)
		{
			if (stamp[i] == gen)
			{
				stamp[i] = 0;
			}
		}

		public int ValueOf(int i)
		{
			if (stamp[i] != gen)
			{
				throw new KeyNotFoundException("RM_StampSet: " + i + " is not a member");
			}
			return value[i];
		}
	}

	/// <summary>Approach B phase 2 (design/RimMandrake/flowworks_offline_kernel_B.md): the grid transition of one
	/// flow pulse — component resolution, sink drain, the exact-level solve (<see cref="ResolveExact"/>) and the
	/// per-component conservation ledger — on integer cell indices (z * width + x, Verse's CellIndices). Rain, burn,
	/// stock refill/recession, terrain writes and Scribe stay in the adapter. Verse-free so the selftest runs it.
	/// (The whole-notch engine — static flow order, donor picks, level-set bands — was deleted with
	/// RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES; the shipped game had run exact-only since 2026-10-17.)
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
		/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1 part 2: a connected network bigger than <see cref="maxComponentCells"/> is
		/// resolved as several capped partitions, and liquid never crosses a partition seam inside one pulse. With the
		/// seed order fixed the seams fell on the same cells every pulse, so the partitions never exchanged at all. On:
		/// such a network's first partition is walked from a start cell that moves with the pulse count, so every seam
		/// moves and, over a few pulses, liquid crosses all of them. Networks within the cap are untouched (same walk,
		/// same order), so the offline oracle and every small-scene case are unaffected. Off by default; the adapter sets it.</summary>
		public bool seamRotationEnabled;
		private readonly RM_StampSet networkVisited = new RM_StampSet();
		private readonly RM_StampSet networkSources = new RM_StampSet();
		private readonly List<int> networkCells = new List<int>();
		private readonly List<int> networkExcavated = new List<int>();
		/// <summary>Pulses on which a network over the cap was walked with a moved seam (the selftest reads it).</summary>
		public int rotatedNetworks;
		/// <summary>FLOWWORKS_SLUICE_TWO_DOORS_1 (owner 2026-10-06: "sealed sluice gates (standard) and the ones made of
		/// metal grates that always allow liquid"): true for a cell under a SHUT sluice. Liquid neither enters nor
		/// leaves a sealed cell and no flow order is walked through it, so the level stops at the gate. Null = no
		/// cell is sealed (the offline worlds, and every map without a shut sluice).</summary>
		public Func<int, bool> sealedCell;
		/// <summary>Superdeep: what a natural source reads as (RM_ExcavationDepth.Superdeep).</summary>
		public const byte Superdeep = 4;
		/// <summary>DISABLED_LIQUID_FIX_LIMITLESS_SOURCE: <see cref="RM_ILevelWorld.LevelBodyOf"/>'s answer for a source whose
		/// liquid is switched off in Mod Settings (FLUID_DISABLE_ALL_INPUTS_1): not a node at all, never a limitless mouth.</summary>
		public const int LevelBodyDisabled = -2;




		/// <summary>The decilitres below one whole notch per cell (0..U-1); W = fill·U + part. The adapter's scribed grid.</summary>
		public ushort[] part;
		/// <summary>Exact mode, this pulse: dL limitless sources paid in, dL sinks took out (the adapter's ledger).</summary>
		public long exactCreditDl;
		public long exactDrainDl;
		private readonly RM_LevelSolve exactSolve = new RM_LevelSolve();
		private readonly RM_LevelSolve canalSolve = new RM_LevelSolve();
		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: a domain with no pond and no limitless mouth solves once: the
		/// joint solve's target would only feed an exchange that cannot happen, and the canal re-solve reads the same input.
		/// Off = the pre-fix work, kept so ExcavationTick_exact_shortcuts_equal_reference can prove the cut changes nothing.
		/// (The other cut, a rotated network walking no static flow order, is the only path since the whole-notch kernel's
		/// static flow order was deleted: RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES.)</summary>
		public bool exactShortcutsEnabled = true;

		// ── EXCAVATION_RAIN_TAME_ONE_TICK_DELUGE: pocket rain (owner 2026-10-27: "Sounds like we need a rain approximation of
		// some kind.") ── Rain lands inside the pulse's own walk, one pocket (the unit being resolved) at a time, instead of a
		// pass over every dug square before the pulse. Each open square still takes its own notches (ruling 25: only where
		// unroofed); what an open square has no room for stays in the POCKET and runs to any square of the same water with room
		// (the solve below levels it this pulse), and only what the whole pocket cannot hold runs over its lip, as ONE offer.

		/// <summary>Whole notches of rain each open square takes this pulse (0: none). The adapter sets it before <see cref="BeginPulse"/>.</summary>
		public int rainNotches;
		/// <summary>The liquid the rain is (the world's fluid object).</summary>
		public object rainFluid;
		/// <summary>True when the dug square catches rain (open to the sky). Null: no rain.</summary>
		public Predicate<int> rainCatches;
		/// <summary>A pocket's rain it had no room for: (an open brimming square of it, decilitres, fluid). Null: it is lost.</summary>
		public Action<int, long, object> rainOverflow;
		/// <summary>This pulse: dL of rain landed in dug squares, and dL run over pocket lips (offered to rainOverflow).</summary>
		public long rainLandedDl, rainOverflowDl;
		/// <summary>This pulse: pockets that took rain.</summary>
		public int rainPockets;
		private readonly RM_StampSet rained = new RM_StampSet();
		private bool rainArmed;

		/// <summary>The rain of one pocket (<paramref name="cells"/>: its dug squares, any order; non-dug members skipped), before
		/// the pocket's ledger measures "before". Every square is rained on at most once a pulse.</summary>
		private void PocketRain(List<int> cells)
		{
			int n = rainNotches;
			if (n <= 0 || rainCatches == null || !rainArmed)
			{
				return;   // rainArmed: the notches were set before this pulse began (the stamp set is sized for it)
			}
			int U = RM_LevelSolve.U;
			long owedDl = 0;     // what brimming open squares water can leave could not hold (dL): it runs into the pocket
			long stuckDl = 0;    // what a brimming SEALED square could not hold: it cannot run anywhere but over the lip
			long landed = 0;     // dL
			int lip = -1;
			rainBrim.Clear();
			rainBrimOwe.Clear();
			for (int i = 0; i < cells.Count; i++)
			{
				int c = cells[i];
				if (!IsExcavated(c) || rained.Contains(c))
				{
					continue;
				}
				rained.Add(c);
				if (!rainCatches(c))
				{
					continue;
				}
				long w = WaterOf(c);
				if (w > 0 ? !SameFluid(world.CellFluid(c), rainFluid) : !world.CanClaim(rainFluid))
				{
					continue;   // rain is water: never on another liquid (step 2b); a dry square that cannot record it stays dry
				}
				long roomDl = depth[c] * (long)U - w;
				long sealedFrac = 0;
				int room = roomDl <= 0 ? 0 : (int)(roomDl / U);
				int add = room < n ? room : n;
				if (add < n)
				{
					if (IsSealed(c))
					{
						// cs_review F3: water fills a sealed square's part-notch of room too (it cannot run on, so only what that
						// room cannot hold goes over the lip).
						long frac = Math.Max(0, roomDl - add * (long)U);
						stuckDl += (n - add) * (long)U - frac;
						sealedFrac = frac;
					}
					else
					{
						owedDl += (n - add) * (long)U;
						rainBrim.Add(c);
						rainBrimOwe.Add((n - add) * (long)U);
					}
					if (lip < 0)
					{
						lip = c;
					}
				}
				if (add > 0)
				{
					if (w == 0)
					{
						world.Claim(c, rainFluid);
					}
					fill[c] += (byte)add;
					landed += add * (long)U;
				}
				if (sealedFrac > 0)
				{
					SetWaterOf(c, WaterOf(c) + sealedFrac);   // w > 0 here (a dry square's room is whole notches)
					landed += sealedFrac;
				}
			}
			// RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL: the pocket's aggregate runs from the brimming squares through the squares
			// water can pass (cardinal, dug, of this pocket, not sealed, holding rain's own water or dry and able to take it),
			// nearest first, roofed ones too (the water runs under the roof, as the level solve would carry it). A brimming
			// square's water stands at the ground, above every dug bed, so no square reached this way is out of its reach. Never
			// across a shut sluice or another liquid. Water takes decilitres (two half-notches of room take one notch).
			if (owedDl > 0)
			{
				rainDomain.Reset(width * height);
				for (int i = 0; i < cells.Count; i++)
				{
					if (IsExcavated(cells[i]))
					{
						rainDomain.Set(cells[i], 1);
					}
				}
				// cs_review F2: each brimming square's surplus runs only through ITS run of passable squares: two runs of the
				// pocket parted by a shut sluice or another liquid never share one pooled balance. Pass 1 labels the runs
				// (state 3 + run), pass 2 lays each run's own surplus over its squares in walk order.
				rainQueue.Clear();
				rainRunOwed.Clear();
				rainRunStart.Clear();
				for (int j = 0; j < rainBrim.Count; j++)
				{
					int b = rainBrim[j];
					rainDomain.TryGetValue(b, out int sb);
					if (sb >= 3)
					{
						rainRunOwed[sb - 3] += rainBrimOwe[j];
						continue;
					}
					int run = rainRunOwed.Count;
					rainRunOwed.Add(rainBrimOwe[j]);
					rainRunStart.Add(rainQueue.Count);
					rainDomain.Set(b, 3 + run);
					rainQueue.Add(b);
					for (int h = rainRunStart[run]; h < rainQueue.Count; h++)
					{
						int c = rainQueue[h];
						for (int d = 0; d < 4; d++)
						{
							int nb = Cardinal(c, d);
							if (nb < 0 || !rainDomain.TryGetValue(nb, out int state) || state != 1 || IsSealed(nb))
							{
								continue;
							}
							long wn = WaterOf(nb);
							if (wn > 0 ? !SameFluid(world.CellFluid(nb), rainFluid) : !world.CanClaim(rainFluid))
							{
								continue;
							}
							rainDomain.Set(nb, 3 + run);
							rainQueue.Add(nb);
						}
					}
				}
				owedDl = 0;
				for (int run = 0; run < rainRunOwed.Count; run++)
				{
					long owed = rainRunOwed[run];
					int end = run + 1 < rainRunStart.Count ? rainRunStart[run + 1] : rainQueue.Count;
					for (int h = rainRunStart[run]; h < end && owed > 0; h++)
					{
						int c = rainQueue[h];
						long w = WaterOf(c);
						long roomDl = depth[c] * (long)U - w;
						long give = roomDl;
						if (give > owed)
						{
							give = owed;
						}
						if (give > 0)
						{
							if (w == 0)
							{
								world.Claim(c, rainFluid);
							}
							SetWaterOf(c, w + give);
							landed += give;
							owed -= give;
						}
					}
					owedDl += owed;
				}
			}
			long overDl = owedDl + stuckDl;
			if (landed > 0 || overDl > 0)
			{
				rainPockets++;
			}
			rainLandedDl += landed;
			if (overDl > 0 && lip >= 0)
			{
				rainOverflowDl += overDl;
				rainOverflow?.Invoke(lip, overDl, rainFluid);
			}
		}

		private readonly List<int> rainBrim = new List<int>();
		private readonly List<long> rainBrimOwe = new List<long>();
		private readonly List<long> rainRunOwed = new List<long>();
		private readonly List<int> rainRunStart = new List<int>();
		private readonly List<int> rainQueue = new List<int>();
		private readonly RM_StampSet rainDomain = new RM_StampSet();

		// per-pulse outputs
		public float sinkDrained;
		/// <summary>Largest absolute per-component ledger imbalance this pulse (0 when every component balances).</summary>
		public float worstImbalance;
		/// <summary>One line per component whose ledger did not balance (the adapter logs each in dev mode).</summary>
		public readonly List<string> imbalanceReports = new List<string>();

		private readonly RM_StampSet visited = new RM_StampSet();
		private readonly RM_StampSet componentSources = new RM_StampSet();
		private readonly List<int> walkQueue = new List<int>();
		private readonly List<int> component = new List<int>();
		private readonly List<int> hopFrontier = new List<int>();
		private readonly Predicate<int> isSourcePred;
		private readonly Predicate<int> isExcavatedPred;

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

		/// <summary>A square liquid neither enters nor leaves this pulse: a shut sluice.</summary>
		public bool IsSealed(int idx)
		{
			return idx >= 0 && sealedCell != null && sealedCell(idx);
		}


		public bool IsSource(int idx)
		{
			return idx >= 0 && depth[idx] == 0 && world.IsNaturalLiquid(idx);
		}

		/// <summary>The in-bounds cardinal neighbours N, E, S, W (the selftest drives the generic walk with it).</summary>
		internal void CardinalInBounds(int c, List<int> into)
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
		/// resolved in that order. <see cref="BeginPulse"/> then one unlimited <see cref="StepPulse"/>.</summary>
		public void Pulse(IEnumerable<int> seedOrder, long pulseCount)
		{
			BeginPulse(seedOrder, pulseCount);
			StepPulse(int.MaxValue);
		}

		// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (live r11: a 325x325 map's pulse took up to 576 ms in one tick): a pulse
		// may run as slices over several ticks. The units are the atomic pulse's own, in its own order: one component, the
		// uncapped walk of a network bigger than the cap, or one partition of it. Nothing is cut inside a unit, so every
		// component's ledger still balances on its own.
		private const int StageSeeds = 0, StageNetworkStart = 1, StageNetworkRest = 2;
		private readonly List<int> pulseSeedOrder = new List<int>();
		private readonly List<bool> pulseSeedExcavated = new List<bool>();
		private int sliceStage;
		private int sliceSeedCursor;
		private int sliceNetCursor;
		private int sliceNetStart;
		private long slicePulseCount;

		/// <summary>The adapter's slice: cells a tick. One partition at the default network cap, so a map of a few thousand dug
		/// squares still finishes on the pulse tick and a large one spreads over a few of the pulse's 250 ticks.</summary>
		public const int DefaultSliceCells = 6000;

		/// <summary>True between <see cref="BeginPulse"/> and the <see cref="StepPulse"/> that finishes it.</summary>
		public bool PulseInFlight { get; private set; }

		/// <summary>Cells the last <see cref="StepPulse"/> walked plus cells it resolved, every walk counted (its cost measure;
		/// the selftest bounds it).</summary>
		public long lastStepCells;

		/// <summary>Starts a pulse: clears the per-pulse outputs and sorts the seeds by cell index (owner ruling 2026-10-06:
		/// a scarce body pays its channels by MAP POSITION, never by dig order, so a session and a reload that rebuilds the
		/// set in index order give the same outcome). Each seed's excavated state is noted now, so a slice that runs after
		/// the map changed skips a seed filled in or dug since, as the atomic pulse never saw it either way.</summary>
		public void BeginPulse(IEnumerable<int> seedOrder, long pulseCount)
		{
			sinkDrained = 0f;
			exactCreditDl = 0;
			exactDrainDl = 0;
			rainLandedDl = 0;
			rainOverflowDl = 0;
			rainPockets = 0;
			rainArmed = rainNotches > 0;
			if (rainArmed)
			{
				rained.Reset(width * height);
			}
			worstImbalance = 0f;
			imbalanceReports.Clear();
			networkSinkDrained = false;
			visited.Reset(width * height);
			pulseSeedOrder.Clear();
			pulseSeedOrder.AddRange(seedOrder);
			SortCells(pulseSeedOrder);
			pulseSeedExcavated.Clear();
			for (int i = 0; i < pulseSeedOrder.Count; i++)
			{
				pulseSeedExcavated.Add(IsExcavated(pulseSeedOrder[i]));
			}
			sliceStage = StageSeeds;
			sliceSeedCursor = 0;
			slicePulseCount = pulseCount;
			PulseInFlight = true;
		}

		/// <summary>Runs units of the pulse in flight until at least <paramref name="cellBudget"/> cells were walked or resolved
		/// (at least one unit, so every call progresses). Returns true once the pulse is complete (also when none is in flight).
		/// Run back to back with nothing changing in between, the slices do exactly what one <see cref="Pulse"/> does
		/// (ExcavationTick_sliced_pulse_equals_atomic). Between slices the adapter may dig or fill: a cell listed earlier this
		/// pulse whose excavated state changed since is skipped, and no cell is resolved twice in one pulse.</summary>
		public bool StepPulse(int cellBudget)
		{
			lastStepCells = 0;
			if (!PulseInFlight)
			{
				return true;
			}
			long budget = Math.Max(1, cellBudget);
			while (lastStepCells < budget)
			{
				if (sliceStage == StageNetworkStart)
				{
					sliceStage = StageNetworkRest;
					sliceNetCursor = 0;
					if (IsExcavated(sliceNetStart) && !visited.Contains(sliceNetStart))
					{
						CollectComponentGrid(sliceNetStart, isSourcePred, isExcavatedPred, width, height,
							visited, componentSources, walkQueue, component, maxComponentCells);
						ResolveComponent(slicePulseCount, true);
						lastStepCells += 2L * component.Count;   // walked, then resolved
					}
					continue;
				}
				if (sliceStage == StageNetworkRest)
				{
					if (sliceNetCursor >= networkExcavated.Count)
					{
						sliceStage = StageSeeds;
						continue;
					}
					int c = networkExcavated[sliceNetCursor++];
					if (visited.Contains(c) || !IsExcavated(c))
					{
						continue;
					}
					CollectComponentGrid(c, isSourcePred, isExcavatedPred, width, height,
						visited, componentSources, walkQueue, component, maxComponentCells);
					ResolveComponent(slicePulseCount, true);
					lastStepCells += 2L * component.Count;
					continue;
				}
				if (sliceSeedCursor >= pulseSeedOrder.Count)
				{
					break;
				}
				int i = sliceSeedCursor++;
				int seed = pulseSeedOrder[i];
				if (visited.Contains(seed) || IsExcavated(seed) != pulseSeedExcavated[i])
				{
					continue;
				}
				CollectComponentGrid(seed, isSourcePred, isExcavatedPred, width, height,
					visited, componentSources, walkQueue, component, maxComponentCells);
				// The cost counts every walk: the capped one, the network's uncapped one when the cap was hit, the resolve.
				int cappedWalk = component.Count;
				bool networkWalked = seamRotationEnabled && cappedWalk >= maxComponentCells;
				if (networkWalked && BeginRotatedNetwork(seed, slicePulseCount))
				{
					lastStepCells += cappedWalk + networkCells.Count + (networkSinkDrained ? netDrainCost : 0);
					continue;
				}
				ResolveComponent(slicePulseCount);
				lastStepCells += cappedWalk + (networkWalked ? networkCells.Count : 0) + component.Count;
			}
			if (sliceStage == StageSeeds && sliceSeedCursor >= pulseSeedOrder.Count)
			{
				PulseInFlight = false;
			}
			return !PulseInFlight;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: <see cref="RM_StockMath.CollectComponent{T}"/> on the grid's
		/// indices with stamp sets and a list queue (no hashing): the same breadth-first walk, the same predicate calls in the
		/// same order (cardinal neighbours N, E, S, W as <see cref="CardinalInBounds"/>), the same cap un-marking. Pinned to
		/// the generic walk by ExcavationTick_grid_walk_equals_generic.</summary>
		internal static void CollectComponentGrid(int seed, Predicate<int> isSource, Predicate<int> isExcavated, int width, int height,
			RM_StampSet visitedExcavated, RM_StampSet componentSources, List<int> queue, List<int> component, int maxCells)
		{
			component.Clear();
			componentSources.Reset(width * height);
			queue.Clear();
			queue.Add(seed);
			visitedExcavated.Add(seed);
			int head = 0;
			while (head < queue.Count && component.Count < maxCells)
			{
				int c = queue[head++];
				component.Add(c);
				if (isSource(c))
				{
					continue;
				}
				int x = c % width;
				int z = c / width;
				for (int d = 0; d < 4; d++)
				{
					int nx = x + CardX[d];
					int nz = z + CardZ[d];
					if (nx < 0 || nz < 0 || nx >= width || nz >= height)
					{
						continue;
					}
					int n = nz * width + nx;
					if (isExcavated(n))
					{
						if (visitedExcavated.Add(n))
						{
							queue.Add(n);
						}
					}
					else if (isSource(n) && componentSources.Add(n))
					{
						queue.Add(n);
					}
				}
			}
			// Cap hit: cells still queued were marked visited but never added; un-marked, a later seed picks them up.
			for (; head < queue.Count; head++)
			{
				int left = queue[head];
				if (isExcavated(left))
				{
					visitedExcavated.Remove(left);
				}
			}
		}

		/// <summary>Part 2: <paramref name="seed"/>'s capped walk hit the cap. Walk its whole network (uncapped, own
		/// scratch sets), and if it really is bigger than the cap, undo the capped walk's marks and queue the network for
		/// <see cref="StepPulse"/> as capped partitions whose first one starts at a cell chosen by the pulse count; the rest
		/// follow in cell-index order. Every excavated cell of the network is still resolved exactly once this pulse, every partition reads
		/// one static flow order walked over the whole network (FLOWWORKS_CHANNEL_OSCILLATION_1) and keeps its own balanced ledger. Returns false (the
		/// caller resolves the capped walk as before) when the network is exactly the cap.</summary>
		private bool BeginRotatedNetwork(int seed, long pulseCount)
		{
			networkVisited.Reset(width * height);
			CollectComponentGrid(seed, isSourcePred, isExcavatedPred, width, height,
				networkVisited, networkSources, walkQueue, networkCells, int.MaxValue);
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
			// Clear the capped walk's own marks so the partitions re-walk them. Only its marks: between slices a new dig can
			// join a component resolved earlier this pulse to this network, and those cells must stay done (in an unsliced
			// pulse no other cell of the network is marked, so this is every marked network cell).
			for (int i = 0; i < component.Count; i++)
			{
				if (IsExcavated(component[i]))
				{
					visited.Remove(component[i]);
				}
			}
			SortCells(networkExcavated);
			int n = networkExcavated.Count;
			// One flow order for the WHOLE network, walked once from all its supplying sources, inputs and sinks: a
			// partition away from the source would otherwise see every key equal and never spread (part 1's defect),
			// and the order stays the same static, acyclic one whichever way the seams fall this pulse.
			component.Clear();
			component.AddRange(networkCells);
			TouchSuppliers();
			// A pulse with pocket rain keeps the partition drain: rain lands pocket by pocket inside each partition, before
			// its sinks take their share, and a drain ahead of every partition would run before the rain it should see.
			networkSinkDrained = edgeSinksEnabled && networkSinkSpreadEnabled && !rainArmed;
			if (networkSinkDrained)
			{
				NetworkSinkDrain(pulseCount);
			}
			// A large odd stride spreads successive starts across the network instead of creeping one cell a pulse.
			sliceNetStart = networkExcavated[SeamSlot(pulseCount, n)];
			rotatedNetworks++;
			sliceStage = StageNetworkStart;
			return true;
		}

		/// <summary>EDGE_SINK_WATER_TAME_SEAM_FLICKER: true while the partitions of the rotated network in flight resolve, when
		/// <see cref="NetworkSinkDrain"/> already took this pulse's sink drain for the whole network (each partition then
		/// skips its own).</summary>
		private bool networkSinkDrained;
		/// <summary>EDGE_SINK_WATER_TAME_SEAM_FLICKER: on (shipped), <see cref="NetworkSinkDrain"/>; off = the pre-fix drain partition
		/// by partition, kept for the selftests that need its churn (the picture budget and the sticky look) and to show the fix.</summary>
		public bool networkSinkSpreadEnabled = true;
		private readonly RM_StampSet netBodySeen = new RM_StampSet();
		private readonly List<int> netBody = new List<int>();
		/// <summary>Squares the last <see cref="NetworkSinkDrain"/> walked and read, counted into the slice cost.</summary>
		private long netDrainCost;

		/// <summary>EDGE_SINK_WATER_TAME_SEAM_FLICKER (exact path, a network over the cap, edge sinks on). Drained partition by
		/// partition, only the partition holding the sink squares fell, a level body split across seams stood at two heights,
		/// and the moving seams then averaged each square with lower water one pulse and higher the next: about half a level
		/// of swing near the edge (bench: 30,678 squares flipped look band 4+ times in 38 pulses). Here the network's sinks
		/// drain once, before any partition: each sink square still takes min(its water, flowPerPulse·U), the same dL as
		/// before, but that total is taken from the whole wet body of the same liquid joined to the sink as one even fall of
		/// its surface (each square gives min(its water, δ), the last dL nearest the sink), which is what one level body
		/// draining at its edge does. A liquid that does not move this pulse (viscosity) drains at the sink squares, as
		/// before. Networks within the cap, and pulses with pocket rain, are untouched.</summary>
		private void NetworkSinkDrain(long pulseCount)
		{
			if (part == null || part.Length != width * height)
			{
				part = new ushort[width * height];
			}
			long per = flowPerPulse * (long)RM_LevelSolve.U;
			netBodySeen.Reset(width * height);
			netDrainCost = 0;
			long total = 0;
			for (int s = 0; s < networkExcavated.Count; s++)
			{
				int sink = networkExcavated[s];
				if (netBodySeen.Contains(sink) || visited.Contains(sink) || !world.IsSink(sink) || IsSealed(sink) || WaterOf(sink) <= 0)
				{
					continue;
				}
				object fl = world.CellFluid(sink);
				// the body: wet squares of this liquid joined to the sink through dug, unsealed squares of the network,
				// breadth first from the sink (its own sink squares join as they are reached). A square already resolved this
				// pulse (a dig between slices joined its component to this network) is done and stays out.
				netBody.Clear();
				netBody.Add(sink);
				netBodySeen.Add(sink);
				long take = 0;
				for (int head = 0; head < netBody.Count; head++)
				{
					int c = netBody[head];
					if (world.IsSink(c) && !IsSealed(c))
					{
						take += Math.Min(WaterOf(c), per);
					}
					for (int d = 0; d < 4; d++)
					{
						int nb = Cardinal(c, d);
						if (nb < 0 || netBodySeen.Contains(nb) || visited.Contains(nb) || !networkVisited.Contains(nb) || !IsExcavated(nb) || IsSealed(nb)
							|| WaterOf(nb) <= 0 || !SameFluid(world.CellFluid(nb), fl))
						{
							continue;
						}
						netBodySeen.Add(nb);
						netBody.Add(nb);
					}
				}
				if (take <= 0)
				{
					continue;
				}
				total += take;
				if (viscosityEnabled && !RM_StockMath.FluidMovesThisPulse(pulseCount, world.TicksPerTile(fl)))
				{
					for (int i = 0; i < netBody.Count; i++)
					{
						int c = netBody[i];
						if (world.IsSink(c) && !IsSealed(c))
						{
							SetWaterOf(c, WaterOf(c) - Math.Min(WaterOf(c), per));
						}
					}
					continue;
				}
				// δ: the largest fall with Σ min(w, δ) ≤ take (take ≤ the body's water, so δ ≤ its wettest square)
				// lo = take/N is always within (Σ min(w, δ) ≤ N·δ); when the driest square holds more than lo it IS δ (one more dL
				// a square would take N·(lo+1) > take), the common case, so the search runs only for a body with squares that empty.
				long lo = take / netBody.Count, hi = 0, driest = long.MaxValue;
				for (int i = 0; i < netBody.Count; i++)
				{
					long w = WaterOf(netBody[i]);
					hi = Math.Max(hi, w);
					driest = Math.Min(driest, w);
				}
				netDrainCost += 2L * netBody.Count;
				if (driest > lo)
				{
					hi = lo;
				}
				while (lo < hi)
				{
					long mid = lo + (hi - lo + 1) / 2;
					long sum = 0;
					for (int i = 0; i < netBody.Count && sum <= take; i++)
					{
						sum += Math.Min(WaterOf(netBody[i]), mid);
					}
					netDrainCost += netBody.Count;
					if (sum <= take)
					{
						lo = mid;
					}
					else
					{
						hi = mid - 1;
					}
				}
				long left = take;
				for (int i = 0; i < netBody.Count; i++)
				{
					int c = netBody[i];
					long w = WaterOf(c);
					long t = Math.Min(w, lo);
					SetWaterOf(c, w - t);
					left -= t;
				}
				// the remainder (fewer dL than squares still wet), one dL a square, nearest the sink first
				for (int i = 0; i < netBody.Count && left > 0; i++)
				{
					int c = netBody[i];
					long w = WaterOf(c);
					if (w > 0)
					{
						SetWaterOf(c, w - 1);
						left--;
					}
				}
			}
			exactDrainDl += total;
			sinkDrained += total / (float)RM_LevelSolve.U;
		}

		/// <summary>CanSupply on each source of the component, in component order (the adapter's may form a body).</summary>
		private void TouchSuppliers()
		{
			for (int i = 0; i < component.Count; i++)
			{
				int c = component[i];
				if (IsSource(c))
				{
					world.CanSupply(c);
				}
			}
		}

		private void ResolveComponent(long pulseCount, bool networkOrder = false)
		{
			if (part == null || part.Length != width * height)
			{
				part = new ushort[width * height];   // a world that keeps no part grid (the offline worlds)
			}
			ResolveExact((RM_ILevelWorld)world, pulseCount, networkOrder);
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
		private readonly RM_StampSet exAssigned = new RM_StampSet();
		private readonly Dictionary<int, long> exPondBefore = new Dictionary<int, long>();
		private readonly List<int> exCells = new List<int>();
		private readonly RM_StampSet exInDom = new RM_StampSet();
		private readonly List<int> exPonds = new List<int>();
		private readonly HashSet<int> exPondSet = new HashSet<int>();
		private readonly HashSet<int> exLimMouths = new HashSet<int>();
		private readonly Dictionary<long, int> exMouthEdge = new Dictionary<long, int>();
		private readonly List<int> exQueue = new List<int>();
		private readonly RM_StampSet exIndex = new RM_StampSet();
		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the partition's membership (was componentSet here).</summary>
		private readonly RM_StampSet exComp = new RM_StampSet();
		private readonly RM_StampSet sortMark = new RM_StampSet();

		/// <summary>STEPPULSE_SHRINK_STEADY_SLICE_COST: sorts grid indices ascending. Distinct in-grid indices over a span not much
		/// wider than their count (a partition, a network, a domain: rows of one dig) are marked and read back in index order,
		/// which is linear where List.Sort is n log n; anything else (a duplicate, an index off the grid, a sparse span) falls
		/// back to List.Sort. Either way the list ends the same ascending list.</summary>
		private void SortCells(List<int> cells)
		{
			int count = cells.Count;
			if (count < 64)
			{
				cells.Sort();
				return;
			}
			int size = width * height;
			int min = int.MaxValue, max = -1;
			for (int i = 0; i < count; i++)
			{
				int c = cells[i];
				if (c < 0 || c >= size)
				{
					cells.Sort();
					return;
				}
				if (c < min)
				{
					min = c;
				}
				if (c > max)
				{
					max = c;
				}
			}
			if ((long)(max - min) > 16L * count)
			{
				cells.Sort();
				return;
			}
			sortMark.Reset(size);
			for (int i = 0; i < count; i++)
			{
				if (!sortMark.Add(cells[i]))
				{
					cells.Sort();   // a duplicate: the scan would drop it
					return;
				}
			}
			cells.Clear();
			for (int c = min; c <= max; c++)
			{
				if (sortMark.Contains(c))
				{
					cells.Add(c);
				}
			}
		}
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
			exComp.Reset(width * height);
			for (int i = 0; i < component.Count; i++)
			{
				exComp.Add(component[i]);
			}
			exDug.Clear();
			for (int i = 0; i < component.Count; i++)
			{
				if (IsExcavated(component[i]))
				{
					exDug.Add(component[i]);
				}
			}
			SortCells(exDug);
			PocketRain(exDug);   // pocket rain: before "before", so the ledger reads it as input, never a leak
			long before = 0;
			for (int i = 0; i < exDug.Count; i++)
			{
				before += WaterOf(exDug[i]);
			}
			long drained = 0;
			// a rotated network's sinks drained once for the whole network (NetworkSinkDrain), before its first partition
			if (edgeSinksEnabled && !(networkOrder && networkSinkDrained))
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
						if (nb < 0 || exHops.ContainsKey(nb) || !exComp.Contains(nb) || !IsExcavated(nb) || IsSealed(nb))
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
			exAssigned.Reset(width * height);
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
					// cs_review F4: the first source that can feed the square names its liquid; a switched-off liquid's source
					// or one the square cannot claim no longer hides an enabled source of another liquid beside it.
					fl = null;
					for (int d = 0; d < 4 && fl == null; d++)
					{
						int nb = Cardinal(c, d);
						if (nb >= 0 && exComp.Contains(nb) && IsSource(nb) && !IsSealed(nb))
						{
							object df = world.DonorFluid(nb, true);
							if (world.CanClaim(df) && lw.LevelBodyOf(nb) != LevelBodyDisabled)
							{
								fl = df;
							}
						}
					}
					if (fl == null)
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
			if (!exComp.Contains(s) || !IsSource(s) || IsSealed(s))
			{
				return;
			}
			object df = world.DonorFluid(s, true);
			if (!RM_StockMath.FluidsCompatible(true, fl, df))
			{
				return;
			}
			int bid = lw.LevelBodyOf(s);
			if (bid == LevelBodyDisabled)
			{
				return;   // DISABLED_LIQUID_FIX_LIMITLESS_SOURCE: a switched-off liquid is no node, never a limitless mouth
			}
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
			exInDom.Reset(width * height);
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
						if (nb < 0 || !exComp.Contains(nb))
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
							if (nb < 0 || !exComp.Contains(nb) || !IsExcavated(nb) || IsSealed(nb) || exAssigned.Contains(nb))
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
				SortCells(exCells);
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
			exIndex.Reset(width * height);
			if (exactShortcutsEnabled && exPonds.Count == 0 && exLimMouths.Count == 0)
			{
				// (b): no pond, no limitless mouth: nothing exchanges (exNew = exOld), so the canal re-solve below is the whole
				// answer and the joint solve would be the same solve twice (a failing one fails the canal solve too: no write).
				for (int i = 0; i < nCells; i++)
				{
					int c = exCells[i];
					exIndex.Set(c, i);
					exNew[i] = WaterOf(c);
				}
				ExactCanalWrite(fl, nCells);
				return;
			}
			exactSolve.Clear();
			for (int i = 0; i < nCells; i++)
			{
				int c = exCells[i];
				exIndex.Set(c, i);
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
				exactSolve.AddEdge(exIndex.ValueOf(c), nCells + exPonds.IndexOf(bid), kv.Value);
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
			if (!ExactCanalWrite(fl, nCells))
			{
				return;
			}
			for (int k = 0; k < exPonds.Count; k++)
			{
				lw.SetBodyStockDl(exPonds[k], exNew[nCells + k] + excess[k]);
			}
		}

		/// <summary>The canal squares, re-solved on their own from exNew (the ponds keep what the exchange gave them), and
		/// written. False (nothing written) if the solve would not conserve.</summary>
		private bool ExactCanalWrite(object fl, int nCells)
		{
			canalSolve.Clear();
			for (int i = 0; i < nCells; i++)
			{
				canalSolve.AddCell(depth[exCells[i]], exNew[i]);
			}
			ExactCellEdges(canalSolve);
			if (!canalSolve.Solve())
			{
				return false;
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
			return true;
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

		/// <summary>PLOT_D_BODY_PRUNE_STALE_SEA: forget every claim <paramref name="cellToBody"/> holds on the cells of the
		/// rect (<paramref name="x"/>, <paramref name="z"/>, <paramref name="w"/> x <paramref name="h"/>, clipped to the
		/// width x height map). <see cref="CollectBody"/> joins ANY claimed 8-neighbour, a repainted Soil cell included, so
		/// a claim left on cleared ground makes the next pond painted beside it that far body (live 2026-10-24: a fresh 5x5
		/// pond on plot D read back as limitless body 9, 17,434 cells, with no water near it). A dev fixture reset calls
		/// this; play never does (ruling 16 keeps a classified cell its body's). Returns the claims dropped.</summary>
		public static int ReleaseClaimsInRect(Dictionary<int, int> cellToBody, int width, int height, int x, int z, int w, int h)
		{
			int x0 = Math.Max(0, x), z0 = Math.Max(0, z);
			int x1 = Math.Min(width, x + w), z1 = Math.Min(height, z + h);
			int released = 0;
			for (int cz = z0; cz < z1; cz++)
			{
				for (int cx = x0; cx < x1; cx++)
				{
					if (cellToBody.Remove(cz * width + cx))
					{
						released++;
					}
				}
			}
			return released;
		}
	}
}
