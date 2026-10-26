using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.LiquidTypes;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md P6 and
	/// §Levelling feasibility): passive gravity levelling between bodies of liquid. The RULES are the Verse-free
	/// RM_LevellingMath (selftested: LevellingChecks.cs); this adapter shows it the map once per pump cycle, from
	/// RM_MapComponent_Excavation.MapComponentTick beside the tank settle.
	/// <list type="bullet">
	/// <item>A link is two open hose ends (Intake or Outflow; a Capped end and a switched-off hose are no ports) on one network
	/// component, each resolved like a pump's source: the end square, then its eight neighbours, the first dug or natural
	/// liquid square. A component holding a working pump is left to the pump.</item>
	/// <item>A dug end's body is the 4-way run of wet dug squares of its liquid (a dry end: the run of dry dug squares), walked
	/// up to <see cref="MaxRunCells"/>; a natural end's body is its pond (stock, histogram and cached surface), a limitless
	/// one (sea, edge river, source budget off) stands at the brim. Fewer squares than the true body only make a move
	/// smaller (the kernel's area is a lower bound), never an overshoot.</item>
	/// <item>Each planned move runs through RM_LiquidTransfer.Move with the pump's own world legs: a dug square gives only
	/// what it holds (TryTakeDl) and a pour spreads over the canal it joins (TryPourDl); a pond is debited/credited in dL.</item>
	/// <item>Cost per cycle: the ports, the run walks (at most <see cref="WalkBudget"/> squares), and at most
	/// <see cref="MaxLinksPerCycle"/> links planned (each a bisection over a histogram).</item>
	/// </list>
	/// </summary>
	public static class RM_Levelling
	{
		/// <summary>PROVISIONAL: squares walked per dug run (a bigger run is under-counted, which only slows it).</summary>
		public const int MaxRunCells = 20000;
		/// <summary>PROVISIONAL: squares walked per cycle across all runs; links past it wait for a later cycle (the next cycle
		/// starts at the first hose the budget turned away). A square is walked at most once per cycle: an end in a run already
		/// walked this cycle takes that run's body for nothing (HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP, live 2026-10-26: every end
		/// re-walked its 20000-square run before it could know the key, so two 325 basins gave 3 walks and 2 links of 100).
		/// Two of the largest runs a 325 map holds, 125 x 320 basins, are 80000 squares.</summary>
		public const int WalkBudget = 120000;
		/// <summary>PROVISIONAL: links planned per cycle (the rest rotate in; RM_LevellingMath integrates the wait).</summary>
		public const int MaxLinksPerCycle = 64;
		/// <summary>Open ends per component considered (pairs grow as the square).</summary>
		public const int MaxPortsPerComponent = 16;

		/// <summary>State read (probe, selftests): cycles run, links seen last cycle, moves and dL moved this session.</summary>
		public static int Cycles, LastLinks, Moves;
		public static long MovedDl;

		private sealed class MapState
		{
			public int cursor;
			/// <summary>The hose index the next cycle starts at: the first one the walk budget turned away, else 0.</summary>
			public int hoseCursor;
			/// <summary>Per-square walk marks (the walk id that reached the square) and the body that walk found (-1: none), sized
			/// to the map once: a walk allocates no per-square set (each end used to fill a HashSet of up to 20000).</summary>
			public int[] mark, bodyOf;
			public int walkId, cycleFirstWalk;
			public readonly List<IntVec3> queue = new List<IntVec3>();
			public readonly List<int> depths = new List<int>();
			public readonly Dictionary<object, RM_LevelLinkState> portState = new Dictionary<object, RM_LevelLinkState>();
		}

		private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, MapState> states =
			new System.Runtime.CompilerServices.ConditionalWeakTable<Map, MapState>();

		/// <summary>The readout (design P9): what the last cycle did at this hose's open end; null when it was in no link.</summary>
		public static RM_LevelLinkState? StateOf(Map map, CompHoseReel reel)
		{
			if (map == null || reel == null || !states.TryGetValue(map, out MapState st))
			{
				return null;
			}
			return st.portState.TryGetValue(reel, out RM_LevelLinkState s) ? s : (RM_LevelLinkState?)null;
		}

		/// <summary>The hose's inspect line for levelling ("" when the end was in no levelling link last cycle).</summary>
		public static string Readout(Map map, CompHoseReel reel)
		{
			switch (StateOf(map, reel))
			{
				case RM_LevelLinkState.Flowing: return "\nLevelling: flowing (no pump; the higher water runs to the lower).";
				case RM_LevelLinkState.Level: return "\nLevelling: level.";
				case RM_LevelLinkState.SameBody: return "\nLevelling: both ends are in the same water.";
				case RM_LevelLinkState.DifferentLiquids: return "\nLevelling: stopped, different liquids never mix.";
				case RM_LevelLinkState.IntakeExposed: return "\nLevelling: stopped, the intake end is out of the water.";
				case RM_LevelLinkState.Full: return "\nLevelling: stopped, the lower water has no room.";
				default: return "";
			}
		}

		/// <summary>One end as resolved: the square the legs act on and its body.</summary>
		private struct End
		{
			public IntVec3 cell;
			public bool dug;
			public int body;
			public RM_NetPort port;
			public RM_NetComponent comp;
		}

		public static void Tick(Map map)
		{
			// exact-level water only (shipped on): with it off a dug square gives and takes whole notches, and a part-notch take
			// would strip the notches and report nothing moved
			if (map == null || !RM_HoseSettings.gravityLevellingEnabled || !RM_HoseSettings.enabled || !RM_MapComponent_Excavation.LevelExact)
			{
				// switched off: the readout must not keep showing the last cycle's "flowing"
				if (map != null && states.TryGetValue(map, out MapState off))
				{
					off.portState.Clear();
				}
				return;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex == null)
			{
				return;
			}
			IReadOnlyList<RM_NetLink> hoses = RM_HoseLinks.For(map).All;
			MapState st = states.GetValue(map, _ => new MapState());
			st.portState.Clear();
			if (hoses.Count == 0)
			{
				return;
			}
			RM_NetComponents comps = RM_LiquidNet.Components(map);
			var bodies = new List<RM_LevelBody>();
			var bodyFluid = new List<FluidDef>();
			var keyIndex = new Dictionary<long, int>();
			var links = new List<RM_LevelLink>();
			var ends = new List<(End a, End b)>();
			var done = new HashSet<RM_NetComponent>();
			int walked = 0;
			int nCells = map.cellIndices.NumGridCells;
			if (st.mark == null || st.mark.Length != nCells || st.walkId > int.MaxValue - 1000000)
			{
				st.mark = new int[nCells];
				st.bodyOf = new int[nCells];
				st.walkId = 0;
			}
			st.cycleFirstWalk = st.walkId + 1;
			int startAt = st.hoseCursor < hoses.Count ? st.hoseCursor : 0, turnedAway = -1;
			for (int hi = 0; hi < hoses.Count; hi++)
			{
				int hIndex = (startAt + hi) % hoses.Count;
				RM_NetLink h = hoses[hIndex];
				RM_NetComponent c = comps.ComponentOf(h);
				if (c == null || c.Refused || !done.Add(c) || c.Ports.Count < 2)
				{
					continue;
				}
				if (c.Machines.Any(m => m is Building_LiquidPump p && p.Working))
				{
					continue;
				}
				var resolved = new List<End>();
				foreach (RM_NetPort p in c.Ports.Where(q => q.Role != RM_FreeEndRole.Capped && q.Cell is IntVec3 && q.Reel is CompHoseReel)
					.OrderBy(q => ((CompHoseReel)q.Reel).parent.thingIDNumber).Take(MaxPortsPerComponent))
				{
					bool budgetLeft = walked < WalkBudget;
					if (Resolve(map, ex, st, (IntVec3)p.Cell, bodies, bodyFluid, keyIndex, ref walked, out End e))
					{
						e.port = p;
						e.comp = c;
						resolved.Add(e);
					}
					else if (turnedAway < 0 && (!budgetLeft || walked >= WalkBudget))
					{
						turnedAway = hIndex;
					}
				}
				for (int i = 0; i < resolved.Count; i++)
				{
					for (int j = i + 1; j < resolved.Count; j++)
					{
						End a = resolved[i], b = resolved[j];
						links.Add(new RM_LevelLink
						{
							A = a.body, B = b.body,
							FloorA = Floor(ex, a), FloorB = Floor(ex, b),
							TakeA = Take(map, ex, a), TakeB = Take(map, ex, b),
							RoomA = Room(map, ex, a, bodyFluid[b.body] ?? bodyFluid[a.body]),
							RoomB = Room(map, ex, b, bodyFluid[a.body] ?? bodyFluid[b.body]),
						});
						ends.Add((a, b));
					}
				}
			}
			st.hoseCursor = turnedAway < 0 ? 0 : turnedAway;
			LastLinks = links.Count;
			Cycles++;
			if (links.Count == 0)
			{
				return;
			}
			var state = new RM_LevelLinkState[links.Count];
			long limitlessNet = 0;
			List<RM_LevelMove> moves = RM_LevellingMath.Plan(bodies, links, System.Math.Max(1, RM_HoseSettings.LevellingUnitsPerCycle),
				MaxLinksPerCycle, ref st.cursor, state, ref limitlessNet);
			foreach (RM_LevelMove m in moves)
			{
				(End a, End b) = ends[m.Link];
				End from = m.From == a.body ? a : b, to = m.From == a.body ? b : a;
				FluidDef fluid = bodies[m.From].Fluid as FluidDef;   // a run dry at the start of the cycle carries what it was given
				if (fluid == null || m.Dl <= 0 || m.Dl > int.MaxValue)
				{
					continue;
				}
				int amt = (int)m.Dl;
				IntVec3 fc = from.cell, tc = to.cell;
				RM_TransferLeg src = from.dug
					? RM_TransferLeg.World(k => ex.IsExcavated(fc) && ex.WaterDlAt(fc) >= k, k => ex.TryTakeDl(fc, k, out _) == k, k => ex.TryPourDl(fc, fluid, k))
					: RM_TransferLeg.World(k => ex.Stock.SupplyDl(map, fc, k, ex) >= k, k => ex.Stock.TryDebitDl(map, fc, k, ex), k => ex.Stock.CreditDl(map, fc, k, ex) == k);
				RM_TransferLeg dst = to.dug
					? RM_TransferLeg.World(k => ex.PourRoomDl(tc, fluid, k) >= k, k => ex.TryPourDl(tc, fluid, k))
					: RM_TransferLeg.World(k => NaturalRoom(map, ex, tc) >= k, k => ex.Stock.CreditDl(map, tc, k, ex) == k);
				LiquidDef liquid = LiquidFor(fluid);
				if (RM_LiquidTransfer.Move(amt, src, dst, out RM_MoveOutcome mv) > 0)
				{
					RM_LiquidNet.CreditRoute(map, liquid == null ? null : comps.RouteIn(from.comp, from.port, to.port), liquid, mv.Moved, RM_PumpMath.CycleTicks);   // credit site: levelling
					Moves++;
					MovedDl += mv.Moved;
				}
				if (mv.Lost > 0)
				{
					ex.ReportLiquidLost(tc, mv.Lost, "Levelling through a hose");
				}
			}
			for (int i = 0; i < links.Count; i++)
			{
				if (state[i] == RM_LevelLinkState.Skipped)
				{
					continue;
				}
				foreach (End e in new[] { ends[i].a, ends[i].b })
				{
					// a hose end in several links shows the one that moved, else the last reason it did not
					if (!st.portState.TryGetValue(e.port.Reel, out RM_LevelLinkState old) || old != RM_LevelLinkState.Flowing)
					{
						st.portState[e.port.Reel] = state[i];
					}
				}
			}
		}

		/// <summary>The end square as a pump finds it (the end, then its 8 neighbours: the first dug or natural liquid square),
		/// and its body, added to <paramref name="bodies"/> once per key.</summary>
		private static bool Resolve(Map map, RM_MapComponent_Excavation ex, MapState st, IntVec3 end, List<RM_LevelBody> bodies, List<FluidDef> fluids,
			Dictionary<long, int> keyIndex, ref int walked, out End e)
		{
			e = default;
			foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, map))))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				if (ex.IsExcavated(c))
				{
					e.cell = c;
					e.dug = true;
					return DugBody(map, ex, st, c, bodies, fluids, keyIndex, ref walked, out e.body);
				}
				if (ex.IsSourceCell(c))
				{
					e.cell = c;
					e.dug = false;
					return NaturalBody(map, ex, c, bodies, fluids, keyIndex, out e.body);
				}
			}
			return false;
		}

		private static bool NaturalBody(Map map, RM_MapComponent_Excavation ex, IntVec3 c, List<RM_LevelBody> bodies, List<FluidDef> fluids,
			Dictionary<long, int> keyIndex, out int index)
		{
			index = -1;
			RM_LiquidBody body = ex.Stock.BodyAt(map, c, ex);
			FluidDef fluid = body?.fluid ?? ex.ActiveFluid;
			if (fluid == null)
			{
				return false;
			}
			bool limitless = body == null || body.limitless || !RimMandrakeFlowWorksSettings.sourceBudgetEnabled;
			if (!limitless && RM_LiquidStock.LevelUnitOf(body, ex) != 1f)
			{
				return false;   // a body whose stock is not in decilitres of levels: not levelled (no shipped liquid)
			}
			long key = limitless ? (3L << 40) + (body?.id ?? map.cellIndices.CellToIndex(c)) : (2L << 40) + body.id;
			if (keyIndex.TryGetValue(key, out index))
			{
				return true;
			}
			var b = new RM_LevelBody { Key = key, Fluid = fluid, Limitless = limitless };
			if (!limitless)
			{
				b.Hist = ex.Stock.DepthHistogramOf(map, body, ex);
				b.Water = System.Math.Max(0, body.stockDl);
				if (b.Hist == null || b.Hist.Length <= 1)
				{
					return false;
				}
			}
			index = bodies.Count;
			keyIndex[key] = index;
			bodies.Add(b);
			fluids.Add(fluid);
			return true;
		}

		/// <summary>The 4-way run of dug squares from <paramref name="start"/>: wet squares of its liquid (or, from a dry square,
		/// dry squares), not across a shut sluice. Two ends in one run share a body: an end on a square a walk reached this cycle
		/// takes that walk's body without walking (MapState.mark/bodyOf), so a run is walked once per cycle, not once per end.</summary>
		private static bool DugBody(Map map, RM_MapComponent_Excavation ex, MapState st, IntVec3 start, List<RM_LevelBody> bodies, List<FluidDef> fluids,
			Dictionary<long, int> keyIndex, ref int walked, out int index)
		{
			index = -1;
			int startIdx = map.cellIndices.CellToIndex(start);
			if (st.mark[startIdx] >= st.cycleFirstWalk)
			{
				// a run walked this cycle (a capped walk's queued edge included): its body, for nothing
				index = st.bodyOf[startIdx];
				return index >= 0;
			}
			if (walked >= WalkBudget || RM_FlowDoorRules.SealsLiquid(start.GetEdifice(map)))
			{
				return false;
			}
			bool wet = ex.WaterDlAt(start) > 0;
			FluidDef fluid = wet ? (ex.FluidAt(start) ?? ex.ActiveFluid) : null;
			if (wet && fluid == null)
			{
				return false;
			}
			int walk = ++st.walkId;
			st.mark[startIdx] = walk;
			List<IntVec3> queue = st.queue;
			List<int> depths = st.depths;
			queue.Clear();
			depths.Clear();
			queue.Add(start);
			int maxDepth = 0, low = int.MaxValue;
			long water = 0;
			for (int head = 0; head < queue.Count && queue.Count <= MaxRunCells; head++)
			{
				IntVec3 c = queue[head];
				int d = ex.DepthAt(c);
				depths.Add(d);
				maxDepth = System.Math.Max(maxDepth, d);
				water += ex.WaterDlAt(c);
				low = System.Math.Min(low, map.cellIndices.CellToIndex(c));
				for (int k = 0; k < 4; k++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[k];
					if (!n.InBounds(map) || !ex.IsExcavated(n))
					{
						continue;
					}
					int ni = map.cellIndices.CellToIndex(n);
					if (st.mark[ni] >= st.cycleFirstWalk)
					{
						continue;   // this walk's, or an earlier run's this cycle: runs are disjoint, no square counted twice
					}
					bool nWet = ex.WaterDlAt(n) > 0;
					if (nWet != wet || (wet && (ex.FluidAt(n) ?? ex.ActiveFluid) != fluid) || RM_FlowDoorRules.SealsLiquid(n.GetEdifice(map)))
					{
						continue;
					}
					st.mark[ni] = walk;
					queue.Add(n);
				}
			}
			walked += depths.Count;
			index = WalkedBody(depths, maxDepth, low, water, fluid, bodies, fluids, keyIndex);
			// every square this walk reached (the processed run and a capped walk's queued edge) answers later ends for nothing
			foreach (IntVec3 q in queue)
			{
				st.bodyOf[map.cellIndices.CellToIndex(q)] = index;
			}
			return index >= 0;
		}

		/// <summary>The body of a walked run (keyed by its lowest cell index), added once; -1 for a run with no depth.</summary>
		private static int WalkedBody(List<int> depths, int maxDepth, int low, long water, FluidDef fluid,
			List<RM_LevelBody> bodies, List<FluidDef> fluids, Dictionary<long, int> keyIndex)
		{
			long key = (1L << 40) + low;
			if (keyIndex.TryGetValue(key, out int index))
			{
				return index;
			}
			if (maxDepth <= 0)
			{
				return -1;
			}
			var hist = new int[maxDepth + 1];
			foreach (int d in depths)
			{
				for (int l = 1; l <= d; l++)
				{
					hist[l]++;
				}
			}
			index = bodies.Count;
			keyIndex[key] = index;
			bodies.Add(new RM_LevelBody { Key = key, Fluid = fluid, Hist = hist, Water = water });
			fluids.Add(fluid);
			return index;
		}

		/// <summary>The floor under an end, as a surface height (dL-per-square; 0 = brim).</summary>
		private static double Floor(RM_MapComponent_Excavation ex, End e) =>
			-(double)(e.dug ? ex.DepthAt(e.cell) : ex.BedLevelsAt(e.cell)) * RM_LevelSolve.U;

		private static long Take(Map map, RM_MapComponent_Excavation ex, End e) =>
			e.dug ? ex.WaterDlAt(e.cell) : ex.Stock.SupplyDl(map, e.cell, long.MaxValue / 4, ex);

		private static long Room(Map map, RM_MapComponent_Excavation ex, End e, FluidDef incoming)
		{
			if (incoming == null)
			{
				return 0;
			}
			long want = (long)System.Math.Max(1, RM_HoseSettings.LevellingUnitsPerCycle) * RM_LevellingMath.MaxCatchUp;
			return e.dug ? ex.PourRoomDl(e.cell, incoming, want) : NaturalRoom(map, ex, e.cell);
		}

		private static long NaturalRoom(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			RM_LiquidBody body = ex.Stock.BodyAt(map, c, ex);
			if (body == null)
			{
				return 0;
			}
			if (body.limitless)
			{
				return long.MaxValue / 4;
			}
			long room = (long)System.Math.Round(body.capacity * (double)RM_LevelSolve.U) - body.stockDl;
			return room > 0 ? room : 0;
		}

		private static LiquidDef LiquidFor(FluidDef fluid)
		{
			if (fluid == null)
			{
				return null;
			}
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.canalFluid == fluid)
				{
					return l;
				}
			}
			return null;
		}
	}
}
