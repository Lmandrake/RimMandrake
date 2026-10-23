using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Unity.Collections;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// How pawns path around and out of superdeep pits. Two findings, one seam
	/// (Pawn_PathFollower.GenerateNewPathRequest, the single place the follower asks the 1.6
	/// pathfinder for a route):
	///
	/// 1. LADDER BUG (pit_escape, live 2026-10-06): reachability credits a lowered ladder
	///    (RM_SuperdeepTrap.TryGetTrapRegion: one un-held cell in the component = not trapped), but
	///    the vanilla pathfinder knows nothing of the trap. A D = 4 cell costs 300, so its route out
	///    leaves over the NEAREST lip; from a held cell that step is vetoed by
	///    RM_Patch_PathFollower_SuperdeepFloor, which fails the pather — the Goto ends, the AI
	///    re-issues it, the same route comes back, forever. Fix: a held pawn is routed INSIDE the pit
	///    to its way out (the ladder cell), then up onto the lip (RM_PitTrapMath.PlanRoute).
	///
	/// 2. FLOWWORKS_PIT_FALL_ONLY_FORCED_1: a 300-cost hole is still crossable "by careless pathing".
	///    A route that starts outside a pit now treats every OPEN (uncovered) D = 4 cell as
	///    impassable, via the pathfinder's own per-request offset grid (PathRequest.IPathGridCustomizer:
	///    PathGridJob.CellIsPassable refuses a cell whose offset is &gt;= 10000). Covered cells stay
	///    ground — concealment is what lets enemies walk onto a cover (the cover trigger spares the
	///    owner's faction). The pit floor is reached on foot only down a ladder the pawn may climb.
	///
	/// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: while the cliff masks are on (RM_CliffMask.On: relative rule + ladder rule) the
	/// pathfinder itself is edge-correct, so the staged planner above (AvoidPits / StayInPit / PlanRoute / the entry veto) is
	/// RETIRED and this seam only hands a pawn the prison-door rule refuses an offset grid closing the lowered ladders
	/// (PitLeg.ClosedLadders). The planner stays only as the absolute rule's fallback branch (setting off).
	///
	/// Grids are immutable snapshots per map, rebuilt when the open-pit set changes (the pathfinder
	/// caches grid jobs keyed on the customizer object, so a mutated array would be served stale);
	/// superseded snapshots are disposed only after <see cref="RetireAfterTicks"/>.
	/// </summary>
	public static class RM_PitPathing
	{
		private const ushort Blocked = 10000;
		private const int RetireAfterTicks = 2500;
		private const int MaxCells = 4000;

		private sealed class Grid : PathRequest.IPathGridCustomizer
		{
			public NativeArray<ushort> cells;

			public NativeArray<ushort> GetOffsetGrid()
			{
				return cells;
			}
		}

		private sealed class MapGrids
		{
			public int signatureTick = -1;
			public long signature = long.MinValue;
			public Grid avoidPits;
			public Grid stayInPit;
			public readonly List<(Grid grid, int retiredTick)> retired = new List<(Grid, int)>();
		}

		private static readonly Dictionary<Map, MapGrids> grids = new Dictionary<Map, MapGrids>();

		public static bool On => RimMandrakeFlowWorksSettings.superdeepCaptureEnabled;

		/// <summary>An open pit cell: dug to D = 4 and not under an intact cover.</summary>
		public static bool IsOpenPit(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return eng.IsSuperdeepExcavation(c) && !Pits.RM_PitCoverUtility.IsCovered(map, c);
		}

		/// <summary>An open hole a forced arrival can fall into: an open D = 4 cell (absolute rule) or, under the relative rule,
		/// any dug cell not under an intact cover (a rat falls into D 2). A cover is ground until it gives way.</summary>
		public static bool IsOpenHole(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (RM_PocketGrid.Relative)
			{
				return eng.ClimbDepthAt(c) > 0 && !Pits.RM_PitCoverUtility.IsCovered(map, c);
			}
			return IsOpenPit(map, eng, c);
		}

		/// <summary>PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP: the cells the planner treats as "the pit". Absolute rule: an open
		/// D = 4 cell. Relative rule (design §8.3): a person-band POCKET cell (covers are ground in the grid, so never one), so a
		/// drained pond's D 4 core is ordinary costly ground and a sheer D 3 pit is a pit. Interim until the connectivity masks
		/// retire this planner (design §8.5 step 3); smaller bands (rats in a D 2 pocket) are held by the floor, not the planner.</summary>
		public static bool IsTrapCell(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (RM_PocketGrid.Relative)
			{
				return c.InBounds(map) && eng.ClimbDepthAt(c) > 0 && RM_PocketGrid.IsPersonPocketCell(map, c);
			}
			return IsOpenPit(map, eng, c);
		}

		private static IEnumerable<IntVec3> TrapCells(Map map, RM_MapComponent_Excavation eng)
		{
			if (!RM_PocketGrid.Relative)
			{
				foreach (IntVec3 c in eng.SuperdeepCells())
				{
					if (!Pits.RM_PitCoverUtility.IsCovered(map, c))
					{
						yield return c;
					}
				}
				yield break;
			}
			foreach (IntVec3 c in eng.ClimbCells())
			{
				if (IsTrapCell(map, eng, c))
				{
					yield return c;
				}
			}
		}

		private static long Signature(Map map, RM_MapComponent_Excavation eng)
		{
			if (RM_PocketGrid.Relative)
			{
				// The pocket grid changes only when it is rebuilt.
				return -1000L - RM_PocketGrid.For(map).Rebuilds;
			}
			long h = 17;
			foreach (IntVec3 c in eng.SuperdeepCells())
			{
				int idx = map.cellIndices.CellToIndex(c);
				h = h * 31 + (Pits.RM_PitCoverUtility.IsCovered(map, c) ? -idx - 1 : idx + 1);
			}
			return h;
		}

		private static MapGrids GridsFor(Map map, RM_MapComponent_Excavation eng)
		{
			if (!grids.TryGetValue(map, out MapGrids g))
			{
				PruneDeadMaps();
				g = new MapGrids();
				grids[map] = g;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (g.signatureTick != now || g.avoidPits == null)
			{
				g.signatureTick = now;
				long sig = Signature(map, eng);
				if (sig != g.signature || g.avoidPits == null)
				{
					g.signature = sig;
					Rebuild(map, eng, g, now);
				}
				for (int i = g.retired.Count - 1; i >= 0; i--)
				{
					if (now - g.retired[i].retiredTick >= RetireAfterTicks)
					{
						g.retired[i].grid.cells.Dispose();
						g.retired.RemoveAt(i);
					}
				}
			}
			return g;
		}

		private static void Rebuild(Map map, RM_MapComponent_Excavation eng, MapGrids g, int now)
		{
			int n = map.cellIndices.NumGridCells;
			var avoid = new NativeArray<ushort>(n, Allocator.Persistent, NativeArrayOptions.ClearMemory);
			var stay = new NativeArray<ushort>(n, Allocator.Persistent, NativeArrayOptions.UninitializedMemory);
			for (int i = 0; i < n; i++)
			{
				stay[i] = Blocked;
			}
			foreach (IntVec3 c in TrapCells(map, eng))
			{
				int idx = map.cellIndices.CellToIndex(c);
				avoid[idx] = Blocked;
				stay[idx] = 0;
			}
			if (g.avoidPits != null)
			{
				g.retired.Add((g.avoidPits, now));
				g.retired.Add((g.stayInPit, now));
			}
			g.avoidPits = new Grid { cells = avoid };
			g.stayInPit = new Grid { cells = stay };
		}

		/// <summary>MAP_STATICS_PRUNE_GHOST_MAPS (C3-F2): dispose and drop the grids of every map that is gone, in both
		/// tables. Called on a miss and by RM_MapComponent_FlowStatics when a map is removed or a game is loaded.</summary>
		public static void PruneDeadMaps()
		{
			PruneDeadLadders();
			entryCache.Clear();   // keyed by Map: a one-tick cache, but it would pin a removed map until the next query
			List<Map> dead = null;
			foreach (Map m in grids.Keys)
			{
				if (Find.Maps == null || !Find.Maps.Contains(m))
				{
					(dead ?? (dead = new List<Map>())).Add(m);
				}
			}
			if (dead == null)
			{
				return;
			}
			foreach (Map m in dead)
			{
				// Requests for a removed map are never processed again; the arrays can go now.
				MapGrids g = grids[m];
				g.avoidPits?.cells.Dispose();
				g.stayInPit?.cells.Dispose();
				foreach ((Grid grid, int _) in g.retired)
				{
					grid.cells.Dispose();
				}
				grids.Remove(m);
			}
		}

		/// <summary>Does reaching this destination require standing on the open pit floor?</summary>
		public static bool DestNeedsPit(Map map, RM_MapComponent_Excavation eng, LocalTargetInfo dest, PathEndMode peMode)
		{
			IntVec3 d = dest.Cell;
			if (!d.InBounds(map) || !IsTrapCell(map, eng, d))
			{
				return false;
			}
			if (peMode == PathEndMode.OnCell || peMode == PathEndMode.None)
			{
				return true;
			}
			// Touch / InteractionCell: fine from the lip if any adjacent cell is open ground.
			CellRect rect = dest.HasThing ? dest.Thing.OccupiedRect() : CellRect.SingleCell(d);
			foreach (IntVec3 c in rect.ExpandedBy(1))
			{
				if (!rect.Contains(c) && c.InBounds(map) && c.Standable(map) && !IsTrapCell(map, eng, c))
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>The planned leg for this pawn's next path request (null = leave it to vanilla).</summary>
		public static bool TryPlan(Pawn pawn, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode,
			out RM_PitTrapMath.PitRoute route, out PathRequest.IPathGridCustomizer customizer)
		{
			route = default;
			customizer = null;
			if (!On || pawn == null || !pawn.Spawned || pawn.Flying || !dest.IsValid || !start.IsValid)
			{
				return false;
			}
			Map map = pawn.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (!RM_SuperdeepTrap.AnyHole(eng))
			{
				return false;
			}
			if (RM_CliffMask.On)
			{
				// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS (§8.5 step 3): the masks make A* edge-correct, so the staged planner
				// (AvoidPits / StayInPit / PlanRoute) is retired; this seam only closes the ladders this pawn may not climb.
				customizer = ClosedLaddersFor(pawn, map);
				if (customizer == null)
				{
					return false;
				}
				route = new RM_PitTrapMath.PitRoute(RM_PitTrapMath.PitLeg.ClosedLadders);
				return true;
			}
			bool needsPit = DestNeedsPit(map, eng, dest, peMode);
			IntVec3 d = dest.Cell;
			route = RM_PitTrapMath.PlanRoute(
				(x, z) => IsTrapCell(map, eng, new IntVec3(x, 0, z)),
				(x, z) => RM_SuperdeepTrap.IsHeldAt(pawn, new IntVec3(x, 0, z)),
				(x, z) => RM_LadderRules.LadderLetsOut(map, new IntVec3(x, 0, z), pawn),
				(x, z) =>
				{
					var c = new IntVec3(x, 0, z);
					return c.InBounds(map) && c.Standable(map);
				},
				start.x, start.z, d.x, d.z, needsPit, MaxCells);
			if (route.leg == RM_PitTrapMath.PitLeg.Vanilla)
			{
				return false;
			}
			MapGrids g = GridsFor(map, eng);
			switch (route.leg)
			{
				case RM_PitTrapMath.PitLeg.AvoidPits:
				case RM_PitTrapMath.PitLeg.WalkToAvoidPits:
					customizer = g.avoidPits;
					break;
				case RM_PitTrapMath.PitLeg.StayInPit:
				case RM_PitTrapMath.PitLeg.WalkToInPit:
					customizer = g.stayInPit;
					break;
			}
			return true;
		}

		// ── PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: the per-pawn ladder offset (§8.5 step 2) ──────────
		private sealed class LadderGrids
		{
			public int tick = -1;
			public long signature = long.MinValue;
			public Grid closedLowered;
			public readonly List<(Grid grid, int retiredTick)> retired = new List<(Grid, int)>();
		}

		// RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP: keyed by (map, the faction whose own scaling ladders stay open; null = none).
		private static readonly Dictionary<(Map, Faction), LadderGrids> ladderGrids = new Dictionary<(Map, Faction), LadderGrids>();

		private static void PruneDeadLadders()
		{
			foreach ((Map, Faction) key in new List<(Map, Faction)>(ladderGrids.Keys))
			{
				Map m = key.Item1;
				if (Find.Maps == null || !Find.Maps.Contains(m))
				{
					LadderGrids dead = ladderGrids[key];
					dead.closedLowered?.cells.Dispose();
					foreach ((Grid grid, int _) in dead.retired)
					{
						grid.cells.Dispose();
					}
					ladderGrids.Remove(key);
				}
			}
		}

		private static readonly List<Thing> ladderScratch = new List<Thing>();

		/// <summary>The offset grid closing every LOWERED ladder cell, for a pawn the prison-door rule refuses (raised ladders
		/// are already no edge in the masks); null when this pawn may climb them or there is none. That ladder's floor cell is
		/// lost to that pawn, which the design accepts. One immutable grid per ladder layout (the pathfinder caches grid jobs
		/// by customizer), retired like the planner's.</summary>
		private static PathRequest.IPathGridCustomizer ClosedLaddersFor(Pawn pawn, Map map)
		{
			if ((!RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled || RM_LadderRules.MayClimb(pawn)) && RM_LadderParity.ClimbEligible(pawn))
			{
				return null;
			}
			if (RimMandrakeFlowWorks_DefOf.RM_Ladder == null)
			{
				return null;
			}
			// RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP: a raid's own scaling ladders stay open to that raid (ClimbsOwnLadder).
			Faction own = null;
			List<Thing> all = RM_LadderUtility.AllLadders(map, ladderScratch);
			for (int i = 0; i < all.Count; i++)
			{
				if (RM_LadderParity.ClimbEligible(pawn) && RM_LadderRules.ClimbsOwnLadder(all[i], pawn))
				{
					own = pawn.Faction;
					break;
				}
			}
			if (!ladderGrids.TryGetValue((map, own), out LadderGrids g))
			{
				PruneDeadLadders();
				g = new LadderGrids();
				ladderGrids[(map, own)] = g;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (g.tick != now)
			{
				g.tick = now;
				List<Thing> ladders = RM_LadderUtility.AllLadders(map, ladderScratch);   // both defs (PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS)
				long sig = 23;
				for (int i = 0; i < ladders.Count; i++)
				{
					if (RM_ClimbJoins.LoweredLadderAt(map, ladders[i].Position) && (own == null || ladders[i].Faction != own))
					{
						sig = sig * 31 + map.cellIndices.CellToIndex(ladders[i].Position) + 1;
					}
				}
				if (sig != g.signature)
				{
					g.signature = sig;
					if (g.closedLowered != null)
					{
						g.retired.Add((g.closedLowered, now));
						g.closedLowered = null;
					}
					if (sig != 23)
					{
						var cells = new NativeArray<ushort>(map.cellIndices.NumGridCells, Allocator.Persistent, NativeArrayOptions.ClearMemory);
						for (int i = 0; i < ladders.Count; i++)
						{
							if (RM_ClimbJoins.LoweredLadderAt(map, ladders[i].Position) && (own == null || ladders[i].Faction != own))
							{
								cells[map.cellIndices.CellToIndex(ladders[i].Position)] = Blocked;
							}
						}
						g.closedLowered = new Grid { cells = cells };
					}
				}
				for (int i = g.retired.Count - 1; i >= 0; i--)
				{
					if (now - g.retired[i].retiredTick >= RetireAfterTicks)
					{
						g.retired[i].grid.cells.Dispose();
						g.retired.RemoveAt(i);
					}
				}
			}
			return g.closedLowered;
		}

		// ── FLOWWORKS_LADDER_RAISE_LOWER_1: the entry veto ─────────────────
		private static readonly Dictionary<(Map, IntVec3, int), bool> entryCache = new Dictionary<(Map, IntVec3, int), bool>();
		private static int entryCacheTick = -1;

		/// <summary>True when a pawn standing OUTSIDE the open pit cannot get to this destination because it
		/// needs the pit floor and no ladder it may climb (lowered, prison-door rule) leads down into that pit.
		/// Vanilla reachability knows nothing of the pit (a D = 4 cell is only a costly passable cell), so without
		/// this a hauler is offered an item on the floor of a pit with a raised ladder, its path is then refused
		/// (AvoidPits) and the job fails and is re-offered forever. Same test as PlanRoute's descent leg.</summary>
		public static bool OutsiderBarredFromFloor(Pawn pawn, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode)
		{
			// Retired with the masks on: RM_SuperdeepTrap.RelativeVeto (same band component, a usable ladder as a way down) decides.
			if (!On || RM_CliffMask.On || pawn == null || !pawn.Spawned || pawn.Flying || !dest.IsValid)
			{
				return false;
			}
			Map map = pawn.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (!RM_SuperdeepTrap.AnyHole(eng) || !dest.Cell.InBounds(map) || !IsTrapCell(map, eng, dest.Cell)
				|| IsTrapCell(map, eng, start) || !DestNeedsPit(map, eng, dest, peMode))
			{
				return false;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now != entryCacheTick || entryCache.Count > 4096)
			{
				entryCache.Clear();
				entryCacheTick = now;
			}
			var key = (map, dest.Cell, pawn.thingIDNumber);
			if (entryCache.TryGetValue(key, out bool barred))
			{
				return barred;
			}
			barred = !RM_PitTrapMath.PitFloorEnterable(
				(x, z) => IsTrapCell(map, eng, new IntVec3(x, 0, z)),
				(x, z) => RM_LadderRules.LadderLetsOut(map, new IntVec3(x, 0, z), pawn),
				(x, z) =>
				{
					var c = new IntVec3(x, 0, z);
					return c.InBounds(map) && c.Standable(map);
				},
				dest.Cell.x, dest.Cell.z, MaxCells);
			entryCache[key] = barred;
			return barred;
		}

		/// <summary>Bridge/debug read: the leg a pawn would take to a cell (jawa/static_call).</summary>
		public static string ProofRoute(Pawn pawn, IntVec3 dest)
		{
			if (pawn == null || !pawn.Spawned)
			{
				return "no pawn";
			}
			if (!TryPlan(pawn, pawn.Position, dest, PathEndMode.OnCell, out RM_PitTrapMath.PitRoute r, out _))
			{
				return "Vanilla";
			}
			return r.leg + " " + r.x + "," + r.z;
		}
	}

	/// <summary>The seam: replace the follower's path request when a pit decides the route.
	/// Mirrors vanilla GenerateNewPathRequest (cachedReturningToCell, lastPathedTargetPosition stay
	/// keyed on the REAL destination, so arrival and NeedNewPath still judge the real target).</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "GenerateNewPathRequest")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFollower_PitRoute
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn, LocalTargetInfo ___destination,
			PathEndMode ___peMode, ref PathRequest __result)
		{
			Pawn pawn = ___pawn;
			IntVec3 start = __instance.nextCell.IsValid ? __instance.nextCell : pawn?.Position ?? IntVec3.Invalid;
			bool pit = RM_PitPathing.TryPlan(pawn, start, ___destination, ___peMode,
				out RM_PitTrapMath.PitRoute route, out PathRequest.IPathGridCustomizer customizer);
			// DEEP_WATER_BUILD_SWIM_OR_SINK: a non-swimmer's (or land animal's) deep-water offset rides the same request.
			PathRequest.IPathGridCustomizer swim = pawn != null && pawn.Spawned ? Swimming.RM_SwimPathing.CustomizerFor(pawn) : null;
			if (!pit && swim == null)
			{
				return true;
			}
			customizer = Swimming.RM_SwimPathing.Combine(pawn.Map, pit ? customizer : null, swim);
			LocalTargetInfo target = ___destination;
			PathEndMode mode = ___peMode;
			if (pit && route.leg != RM_PitTrapMath.PitLeg.AvoidPits && route.leg != RM_PitTrapMath.PitLeg.StayInPit
				&& route.leg != RM_PitTrapMath.PitLeg.ClosedLadders)
			{
				target = new IntVec3(route.x, 0, route.z);
				mode = PathEndMode.OnCell;
			}
			__instance.cachedReturningToCell = GuestUtility.PrisonerCanReturnToCell(pawn);
			__instance.lastPathedTargetPosition = ___destination.Cell;
			PathFinder pathFinder = pawn.Map.pathFinder;
			PathRequest request = pathFinder.CreateRequest(start, target, null, pawn, PathFinderCostTuning.For(pawn), mode, customizer);
			pathFinder.PushRequest(request);
			__result = request;
			return false;
		}
	}

	/// <summary>Walked-step marker for the descent detector: a pawn whose own path follower moved it
	/// into a superdeep cell walked; any other arrival is forced (FLOWWORKS_PIT_FALL_ONLY_FORCED_1).</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "TryEnterNextPathCell")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFollower_WalkedStep
	{
		[HarmonyPrefix]
		public static void Prefix(Pawn ___pawn, out IntVec3 __state)
		{
			__state = ___pawn != null && ___pawn.Spawned ? ___pawn.Position : IntVec3.Invalid;
		}

		[HarmonyPostfix]
		public static void Postfix(Pawn ___pawn, IntVec3 __state)
		{
			if (___pawn == null || !___pawn.Spawned || !__state.IsValid || ___pawn.Position == __state)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(___pawn.Map);
			// Relative rule: a walked fall can land in any dug cell (a captured rat into D 2), so mark every walked step down a hole.
			if (RM_SuperdeepTrap.AnyHole(eng)
				&& (RM_PocketGrid.Relative ? eng.ClimbDepthAt(___pawn.Position) > 0 : eng.IsSuperdeepExcavation(___pawn.Position)))
			{
				eng.SuperdeepTrap.NoteWalkedStep(___pawn, ___pawn.Position);
			}
		}
	}

	/// <summary>A pawn flyer (jump, stun-throw) is despawned in flight, so the tick detector, which
	/// compares spawned positions, never sees it land. Landing in an open pit from outside it is a
	/// forced descent.</summary>
	[HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PawnFlyer_LandInPit
	{
		[HarmonyPrefix]
		public static void Prefix(PawnFlyer __instance, out Pawn __state)
		{
			__state = __instance.FlyingPawn;
		}

		[HarmonyPostfix]
		public static void Postfix(PawnFlyer __instance, Pawn __state)
		{
			Pawn p = __state;
			if (p == null || !p.Spawned || p.Dead || !RimMandrakeFlowWorksSettings.superdeepCaptureEnabled)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			if (!RM_SuperdeepTrap.AnyHole(eng) || !RM_PitPathing.IsOpenHole(p.Map, eng, p.Position))
			{
				return;
			}
			IntVec3 from = Traverse.Create(__instance).Field("startVec").GetValue<UnityEngine.Vector3>().ToIntVec3();
			// FALL_GUARDRAILS_BUILD_REAL_OBJECT: a THROW (a stun flyer: blast knockback) over a railed lip stops at the rail. A jump
			// (no stun: jump packs, abilities) is deliberate and lands where it was aimed.
			if (RM_FallRails.On && __instance.def?.pawnFlyer != null && __instance.def.pawnFlyer.stunDurationTicksRange != IntRange.Zero)
			{
				IntVec3 stop = RM_FallRails.ThrowStop(p.Map, eng, p, from, p.Position);
				if (stop.IsValid)
				{
					RM_FallRails.PutBack(p, stop);
					eng.SuperdeepTrap.NoteHandledArrival(p, stop);
					return;
				}
			}
			// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (owner 2026-10-18: "jump packs and other leaping abilities allow
			// entrance/exit immediately"): a deliberate jump (no stun) lands on its feet, however deep; the detector must not count
			// the arrival either (it would see a forced descent on its next pass).
			// FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT: a flyer, jumper or floater set down in a pit is not falling.
			if (RimMandrakeFlowWorksSettings.pitFreeTravelEnabled && RM_PocketGrid.FreePitTraveller(p))
			{
				eng.SuperdeepTrap.NoteHandledArrival(p, p.Position);
				return;
			}
			bool deliberate = __instance.def?.pawnFlyer == null || __instance.def.pawnFlyer.stunDurationTicksRange == IntRange.Zero;
			if (RM_PitAccessMath.LandsSafely(deliberate, RimMandrakeFlowWorksSettings.pitJumpLandsSafe, false, false))
			{
				eng.SuperdeepTrap.NoteHandledArrival(p, p.Position);
				return;
			}
			if (RM_PocketGrid.Relative)
			{
				// Design §8.5 steps 8-9: a landing is a fall when it drops more than this pawn climbs.
				int to = RM_SuperdeepTrap.StepDepthAt(p.Map, eng, p.Position);
				int fromD = RM_SuperdeepTrap.StepDepthAt(p.Map, eng, from);
				if (RM_PitTrapMath.ArrivalDropsTooFar(fromD, to, RM_PocketGrid.NaturalClimbLimitOf(p)))
				{
					RM_SuperdeepTrap.OnForcedDescent(p, p.Position, eng.SuperdeepTrap, to - fromD);
				}
				return;
			}
			if (RM_PitPathing.IsOpenPit(p.Map, eng, from))
			{
				return; // a hop along the pit floor is not a fall; a takeoff from a COVERED pit cell is (knockback design §10 #12)
			}
			RM_SuperdeepTrap.OnForcedDescent(p, p.Position, eng.SuperdeepTrap);
		}
	}
}
