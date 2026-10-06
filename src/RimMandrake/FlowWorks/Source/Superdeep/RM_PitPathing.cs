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

		private static long Signature(Map map, RM_MapComponent_Excavation eng)
		{
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
			foreach (IntVec3 c in eng.SuperdeepCells())
			{
				if (Pits.RM_PitCoverUtility.IsCovered(map, c))
				{
					continue;
				}
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

		private static void PruneDeadMaps()
		{
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
			if (!d.InBounds(map) || !IsOpenPit(map, eng, d))
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
				if (!rect.Contains(c) && c.InBounds(map) && c.Standable(map) && !IsOpenPit(map, eng, c))
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
			if (eng == null || eng.SuperdeepCellCount == 0)
			{
				return false;
			}
			bool needsPit = DestNeedsPit(map, eng, dest, peMode);
			IntVec3 d = dest.Cell;
			route = RM_PitTrapMath.PlanRoute(
				(x, z) => IsOpenPit(map, eng, new IntVec3(x, 0, z)),
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
	public static class RM_Patch_PathFollower_PitRoute
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn, LocalTargetInfo ___destination,
			PathEndMode ___peMode, ref PathRequest __result)
		{
			Pawn pawn = ___pawn;
			IntVec3 start = __instance.nextCell.IsValid ? __instance.nextCell : pawn?.Position ?? IntVec3.Invalid;
			if (!RM_PitPathing.TryPlan(pawn, start, ___destination, ___peMode,
				out RM_PitTrapMath.PitRoute route, out PathRequest.IPathGridCustomizer customizer))
			{
				return true;
			}
			LocalTargetInfo target = ___destination;
			PathEndMode mode = ___peMode;
			if (route.leg != RM_PitTrapMath.PitLeg.AvoidPits && route.leg != RM_PitTrapMath.PitLeg.StayInPit)
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
			if (eng != null && eng.SuperdeepCellCount > 0 && eng.IsSuperdeepExcavation(___pawn.Position))
			{
				eng.SuperdeepTrap.NoteWalkedStep(___pawn, ___pawn.Position);
			}
		}
	}

	/// <summary>A pawn flyer (jump, stun-throw) is despawned in flight, so the tick detector, which
	/// compares spawned positions, never sees it land. Landing in an open pit from outside it is a
	/// forced descent.</summary>
	[HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
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
			if (eng == null || eng.SuperdeepCellCount == 0 || !RM_PitPathing.IsOpenPit(p.Map, eng, p.Position))
			{
				return;
			}
			IntVec3 from = Traverse.Create(__instance).Field("startVec").GetValue<UnityEngine.Vector3>().ToIntVec3();
			if (eng.IsSuperdeepExcavation(from))
			{
				return; // a hop along the pit floor is not a fall
			}
			RM_SuperdeepTrap.OnForcedDescent(p, p.Position, eng.SuperdeepTrap);
		}
	}
}
