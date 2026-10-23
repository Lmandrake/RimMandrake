using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using Unity.Collections;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS — climbing gear scales built walls (owner 2026-10-18: <i>"should allow pawns to
	/// scale walls (unroofed on both sides) just as easily as canal sides, albeit slowly"</i>; by card: built walls too, for
	/// colonists AND raiders wearing the gear, both directions, slowly).
	///
	/// How (the least invasive sound route, read from 1.6's Pawn_PathFollower / DigUtility / JobGiver_AISapper /
	/// JobGiver_AIBreaching): a wall stays impassable to the path grid and to regions for everyone, gear or not, so vanilla's
	/// reachability and its pathfinder go on agreeing. A climb is a JOB, JobDriver_RM_ClimbOverWall: walk (an ordinary path)
	/// to the foot of the wall, climb there for RM_WallClimbMath.ClimbTicks, then be set down on the far side. It is offered
	/// where vanilla would otherwise break through: DigUtility.PassBlockerJob (sappers, a dig-out exit, the revenant), the
	/// breach job (JobGiver_AIBreaching), a path walked into a wall the pawn would bash (Pawn_PathFollower), and a raider
	/// whose AssaultColony tree found no reachable enemy (JobGiver_AIGotoNearestHostile, throttled). The player orders it by
	/// right-clicking a wall (FloatMenuOptionProvider_RM_ClimbOverWall). Perf: every seam asks the settings and the def flags
	/// before the apparel, so a pawn without gear pays one edifice read at most.
	///
	/// A wall is read from its def's flags (RM_WallClimbMath.IsClimbableWallKind): impassable, isWall or isFence, not a door,
	/// not mineable, not natural rock. Never a name list.
	/// </summary>
	public static class RM_WallClimb
	{
		public static bool IsClimbableWall(Building b)
		{
			ThingDef d = b?.def;
			return d?.building != null && RM_WallClimbMath.IsClimbableWallKind(d.passability == Traversability.Impassable,
				d.IsDoor, d.mineable, d.building.isNaturalRock, d.IsWall, d.IsFence);
		}

		public static Building ClimbableWallAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			Building b = c.GetEdifice(map);
			return IsClimbableWall(b) ? b : null;
		}

		/// <summary>May this pawn climb walls now (settings first, apparel last).</summary>
		public static bool CanClimb(Pawn p)
		{
			if (!RM_WallClimbSettings.wallClimbEnabled || !RimMandrakeFlowWorksSettings.climbingGearEnabled || p == null
				|| !p.Spawned || p.Downed || p.Dead)
			{
				return false;
			}
			bool playerSide = p.Faction != null && p.Faction == Faction.OfPlayer;
			if (!playerSide && !RM_WallClimbSettings.raidersMayClimbWalls)
			{
				return false;
			}
			return RM_WallClimbMath.MayClimb(RM_PocketGrid.WearsClimbingGear(p), true, true, playerSide,
				RM_WallClimbSettings.raidersMayClimbWalls);
		}

		/// <summary>The crossing that starts at <paramref name="from"/> and climbs the wall square next to it at
		/// <paramref name="firstWall"/> (N/S/E/W), straight on through up to MaxWallSquares wall squares. False when the run is
		/// too thick, a square is roofed, or either side is roofed or not standable.</summary>
		public static bool TryCrossing(Map map, IntVec3 from, IntVec3 firstWall, out IntVec3 landing, out int squares,
			out bool roofed)
		{
			landing = IntVec3.Invalid;
			squares = 0;
			roofed = false;
			IntVec3 d = firstWall - from;
			if (map == null || System.Math.Abs(d.x) + System.Math.Abs(d.z) != 1 || !from.InBounds(map))
			{
				return false;
			}
			IntVec3 c = firstWall;
			bool anyRoof = false;
			while (c.InBounds(map) && ClimbableWallAt(map, c) != null)
			{
				anyRoof |= c.Roofed(map);
				squares++;
				if (squares > RM_WallClimbMath.MaxWallSquares)
				{
					return false;
				}
				c += d;
			}
			if (squares == 0 || !c.InBounds(map))
			{
				return false;
			}
			landing = c;
			bool fromRoofed = from.Roofed(map), toRoofed = c.Roofed(map);
			roofed = anyRoof || fromRoofed || toRoofed;
			return RM_WallClimbMath.CrossingOpen(squares, anyRoof, fromRoofed, toRoofed, from.Standable(map), c.Standable(map));
		}

		/// <summary>The best crossing of the wall at <paramref name="wallCell"/> for this pawn: from a side it reaches, the
		/// nearest such foot. <paramref name="intoNewGround"/>: the landing must be somewhere the pawn cannot already walk to (a
		/// raider getting in, not taking a detour).</summary>
		public static bool TryBestCrossing(Pawn p, IntVec3 wallCell, bool intoNewGround, out IntVec3 from, out IntVec3 landing,
			out bool anyRoofed)
		{
			from = landing = IntVec3.Invalid;
			anyRoofed = false;
			Map map = p.Map;
			float best = float.MaxValue;
			for (int r = 0; r < 4; r++)
			{
				IntVec3 dir = new Rot4(r).FacingCell;
				IntVec3 foot = wallCell - dir;
				if (!foot.InBounds(map) || ClimbableWallAt(map, foot) != null)
				{
					continue;
				}
				if (!TryCrossing(map, foot, wallCell, out IntVec3 land, out int squares, out bool roofed))
				{
					anyRoofed |= roofed;
					continue;
				}
				// LADDER_PARITY_BUILD_NO_KEYS_REQUIRED: gear climbs from any side; a ladder only from its own (one way)
				if (!RM_LadderParity.CanClimbAt(p, foot, wallCell, squares))
				{
					continue;
				}
				float dist = p.Position.DistanceToSquared(foot);
				if (dist >= best || (foot != p.Position && !p.CanReach(foot, PathEndMode.OnCell, Danger.Deadly)))
				{
					continue;
				}
				if (intoNewGround && p.CanReach(land, PathEndMode.OnCell, Danger.Deadly))
				{
					continue;
				}
				best = dist;
				from = foot;
				landing = land;
			}
			return from.IsValid;
		}

		/// <summary>The N/S/E/W neighbour of <paramref name="cellBefore"/> that holds <paramref name="blocker"/>.</summary>
		public static bool WallCellNextTo(Map map, IntVec3 cellBefore, Thing blocker, out IntVec3 wallCell)
		{
			for (int r = 0; r < 4; r++)
			{
				IntVec3 c = cellBefore + new Rot4(r).FacingCell;
				if (c.InBounds(map) && c.GetEdifice(map) == blocker)
				{
					wallCell = c;
					return true;
				}
			}
			wallCell = IntVec3.Invalid;
			return false;
		}

		public static Job MakeClimbJob(IntVec3 from, IntVec3 wallCell, IntVec3 landing)
		{
			Job job = JobMaker.MakeJob(RM_WallClimbDefOf.RM_ClimbOverWall, wallCell, landing, from);
			job.expiryInterval = -1;
			return job;
		}

		/// <summary>The climb from the square before a blocker on a path (sapper, breacher, a walked path): null when this
		/// pawn cannot or the crossing is closed.</summary>
		public static Job ClimbJobForBlocker(Pawn p, Thing blocker, IntVec3 cellBefore)
		{
			if (!(blocker is Building b) || !IsClimbableWall(b) || !cellBefore.IsValid || !RM_LadderParity.MightClimb(p))
			{
				return null;
			}
			if (!WallCellNextTo(p.Map, cellBefore, blocker, out IntVec3 wallCell)
				|| !TryCrossing(p.Map, cellBefore, wallCell, out IntVec3 landing, out int squares, out bool _)
				|| !RM_LadderParity.CanClimbAt(p, cellBefore, wallCell, squares))
			{
				return null;
			}
			if (cellBefore != p.Position && !p.CanReach(cellBefore, PathEndMode.OnCell, Danger.Deadly))
			{
				return null;
			}
			return MakeClimbJob(cellBefore, wallCell, landing);
		}
	}

	[DefOf]
	public static class RM_WallClimbDefOf
	{
		public static JobDef RM_ClimbOverWall;

		static RM_WallClimbDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_WallClimbDefOf));
		}
	}

	/// <summary>Walk to the foot of the wall (targetC), climb for ClimbTicks facing it (targetA, the first wall square),
	/// then stand on the far side (targetB). Re-checked every half second: the gear taken off, a roof built, the wall gone or
	/// the landing blocked ends the climb (Incompletable) and the pawn thinks again.</summary>
	public class JobDriver_RM_ClimbOverWall : JobDriver
	{
		private IntVec3 WallCell => job.targetA.Cell;
		private IntVec3 Landing => job.targetB.Cell;
		private IntVec3 Foot => job.targetC.Cell;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		private bool StillOpen()
		{
			return RM_WallClimb.TryCrossing(pawn.Map, Foot, WallCell, out IntVec3 land, out int squares, out bool _)
				&& land == Landing && RM_LadderParity.CanClimbAt(pawn, Foot, WallCell, squares);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			int squares = 1;
			if (RM_WallClimb.TryCrossing(Map, Foot, WallCell, out IntVec3 _, out int sq, out bool _))
			{
				squares = sq;
			}
			yield return Toils_Goto.GotoCell(TargetIndex.C, PathEndMode.OnCell);
			// LADDER_PARITY_BUILD_NO_KEYS_REQUIRED: no gear and no ladder leaning here: set the carried one first
			bool byLadder = RM_LadderParity.ByLadder(pawn);
			Toil set = ToilMaker.MakeToil("RM_ClimbOverWall_SetLadder");
			set.initAction = delegate
			{
				if (!byLadder || RM_LadderParity.LadderLeaningAt(Map, Foot, WallCell) != null)
				{
					ReadyForNextToil();
				}
			};
			set.tickAction = delegate
			{
				pawn.rotationTracker.FaceCell(WallCell);
			};
			set.defaultCompleteMode = ToilCompleteMode.Delay;
			set.defaultDuration = RM_LadderParityMath.RaiderLadderTicks(0.0, RM_RaiderTrenchSettings.raiderLadderSpeed, true);
			set.handlingFacing = true;
			yield return set;
			Toil placed = ToilMaker.MakeToil("RM_ClimbOverWall_LadderSet");
			placed.initAction = delegate
			{
				if (byLadder && pawn.Position == Foot && RM_LadderParity.LadderLeaningAt(Map, Foot, WallCell) == null
					&& !RM_LadderParity.SetCarriedAt(pawn, Foot, WallCell))
				{
					EndJobWith(JobCondition.Incompletable);
				}
			};
			placed.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return placed;
			Toil climb = ToilMaker.MakeToil("RM_ClimbOverWall");
			climb.initAction = delegate
			{
				if (pawn.Position != Foot || !StillOpen())
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				pawn.pather.StopDead();
				pawn.rotationTracker.FaceCell(WallCell);
			};
			climb.tickAction = delegate
			{
				pawn.rotationTracker.FaceCell(WallCell);
				if (pawn.IsHashIntervalTick(30) && !StillOpen())
				{
					EndJobWith(JobCondition.Incompletable);
				}
			};
			climb.defaultCompleteMode = ToilCompleteMode.Delay;
			climb.defaultDuration = byLadder
				? RM_LadderParityMath.WallClimbTicks(RM_LadderParitySettings.wallLadderSlowFactor, pawn.TicksPerMoveCardinal)
				: RM_WallClimbMath.ClimbTicks(squares, RM_WallClimbSettings.wallClimbSlowFactor, pawn.TicksPerMoveCardinal);
			climb.handlingFacing = true;
			climb.WithProgressBarToilDelay(TargetIndex.C);
			yield return climb;
			Toil land = ToilMaker.MakeToil("RM_ClimbOverWall_Land");
			land.initAction = delegate
			{
				if (!StillOpen())
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				pawn.Position = Landing;
				pawn.Notify_Teleported(false, true);
				// Down the far side on the rope, never a fall: the pit trap's detector would otherwise see a forced arrival.
				RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(pawn.Map);
				if (eng != null && RM_SuperdeepTrap.AnyHole(eng))
				{
					eng.SuperdeepTrap.NoteHandledArrival(pawn, pawn.Position);
				}
			};
			land.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return land;
		}
	}

	/// <summary>Sappers, a dig-out exit and the revenant's escape ask DigUtility.PassBlockerJob how to get past a building on
	/// their path: a gear-wearer climbs a climbable wall instead of mining or bashing it.</summary>
	[HarmonyPatch(typeof(DigUtility), nameof(DigUtility.PassBlockerJob))]
	[RimMandrake.Shared.PatchFeature("Climbing gear scales walls (sappers)", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbEnabled")]
	public static class RM_Patch_PassBlocker_Climb
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn pawn, Thing blocker, IntVec3 cellBeforeBlocker, ref Job __result)
		{
			Job climb = RM_WallClimb.ClimbJobForBlocker(pawn, blocker, cellBeforeBlocker);
			if (climb == null)
			{
				return true;
			}
			__result = climb;
			return false;
		}
	}

	/// <summary>A breacher wearing gear climbs the wall it was about to breach, when that wall is climbable and the far side
	/// is new ground.</summary>
	[HarmonyPatch(typeof(JobGiver_AIBreaching), "TryGiveJob")]
	[RimMandrake.Shared.PatchFeature("Climbing gear scales walls (breachers)", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbEnabled")]
	public static class RM_Patch_Breaching_Climb
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, ref Job __result)
		{
			if (__result == null || !(pawn?.mindState?.breachingTarget?.target is Building b) || !RM_WallClimb.IsClimbableWall(b)
				|| !RM_LadderParity.MightClimb(pawn))
			{
				return;
			}
			if (RM_WallClimb.TryBestCrossing(pawn, b.Position, true, out IntVec3 from, out IntVec3 landing, out bool _))
			{
				__result = RM_WallClimb.MakeClimbJob(from, b.Position, landing);
			}
		}
	}

	/// <summary>A path walked into a climbable wall the pawn would bash (a hostile's, or a job that may bash): the gear-wearer
	/// climbs it instead. Vanilla starts its bash job from the same place (MakeBashBlockerJob).</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "TryEnterNextPathCell")]
	[RimMandrake.Shared.PatchFeature("Climbing gear scales walls (blocked path)", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbEnabled")]
	public static class RM_Patch_PathFollower_ClimbBlocker
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn)
		{
			if (!(RM_WallClimbSettings.wallClimbEnabled || RM_LadderParitySettings.ladderOverWalls) || ___pawn?.Map == null)
			{
				return true;
			}
			Map map = ___pawn.Map;
			IntVec3 next = __instance.nextCell;
			Building b = RM_WallClimb.ClimbableWallAt(map, next);
			if (b == null || !b.BlocksPawn(___pawn))
			{
				return true;
			}
			bool wouldBash = (___pawn.CurJob != null && ___pawn.CurJob.canBashDoors) || ___pawn.HostileTo(b);
			if (!wouldBash || ___pawn.CurJob?.def == RM_WallClimbDefOf.RM_ClimbOverWall || !RM_LadderParity.MightClimb(___pawn)
				|| !RM_WallClimb.TryCrossing(map, ___pawn.Position, next, out IntVec3 landing, out int squares, out bool _)
				|| !RM_LadderParity.CanClimbAt(___pawn, ___pawn.Position, next, squares))
			{
				return true;
			}
			Job job = RM_WallClimb.MakeClimbJob(___pawn.Position, next, landing);
			bool resume = ___pawn.CurJob != null && ___pawn.CurJob.def.suspendable;
			___pawn.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: resume);
			return false;
		}
	}

	/// <summary>An AssaultColony raider wearing gear that finds no enemy it can walk to: the first climbable wall on a
	/// through-walls path to the nearest enemy is climbed. Throttled per pawn (300 ticks), and only gear-wearers pay; the
	/// pathfind is paid from the shared per-tick budget (RM_WallClimbMemo.Budget, WALL_CLIMB_FIX_BUDGET_CAP_LEAKY_MEMOS), so
	/// a raid of N gear-wearers no longer runs N through-walls pathfinds in one tick.</summary>
	[HarmonyPatch(typeof(JobGiver_AIGotoNearestHostile), "TryGiveJob")]
	[RimMandrake.Shared.PatchFeature("Climbing gear scales walls (raiders get in)", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbEnabled")]
	public static class RM_Patch_GotoHostile_Climb
	{
		private const int RetryTicks = 300;
		private const float MaxDistSq = 90f * 90f;
		/// <summary>Per pawn: the tick of its last try (a stamp, so a memo from a later tick than now is spent).</summary>
		private static readonly Dictionary<int, int> lastTry = new Dictionary<int, int>();

		public static void ClearMemos()
		{
			lastTry.Clear();
		}

		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, ref Job __result)
		{
			if (__result != null || pawn?.Map == null || pawn.Faction == Faction.OfPlayer || !RM_LadderParity.MightClimb(pawn))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			RM_WallClimbMemo.Observe(now);
			if (lastTry.TryGetValue(pawn.thingIDNumber, out int at) && !RM_WallClimbMath.MemoExpired(at, now, RetryTicks))
			{
				return;
			}
			if (lastTry.Count > 512)
			{
				lastTry.Clear();
			}
			Thing target = null;
			float best = MaxDistSq;
			foreach (IAttackTarget t in pawn.Map.attackTargetsCache.GetPotentialTargetsFor(pawn))
			{
				Thing th = t.Thing;
				if (th == null || t.ThreatDisabled(pawn))
				{
					continue;
				}
				float d = th.Position.DistanceToSquared(pawn.Position);
				if (d < best)
				{
					best = d;
					target = th;
				}
			}
			if (target == null)
			{
				lastTry[pawn.thingIDNumber] = now;
				return;
			}
			// Out of budget this tick: not stamped, so the next think asks again.
			if (!RM_WallClimbMemo.Budget.TryTake(now, RM_WallClimbMath.RaiderPathfinds))
			{
				return;
			}
			lastTry[pawn.thingIDNumber] = now;
			using (PawnPath path = pawn.Map.pathFinder.FindPathNow(pawn.Position, target.Position,
				TraverseParms.For(pawn, Danger.Deadly, TraverseMode.PassAllDestroyableThings)))
			{
				if (path == null || !path.Found)
				{
					return;
				}
				Thing blocker = path.FirstBlockingBuilding(out IntVec3 before, pawn);
				if (blocker != null)
				{
					__result = RM_WallClimb.ClimbJobForBlocker(pawn, blocker, before);
				}
			}
		}
	}

	/// <summary>Right-click a wall with a gear-wearing colonist selected: "Climb over (wall)". Greyed out with the reason when
	/// a roof closes every side.</summary>
	public class FloatMenuOptionProvider_RM_ClimbOverWall : FloatMenuOptionProvider
	{
		protected override bool Drafted => true;
		protected override bool Undrafted => true;
		protected override bool Multiselect => false;
		protected override bool RequiresManipulation => true;

		protected override bool AppliesInt(FloatMenuContext context)
		{
			return ((RM_WallClimbSettings.wallClimbEnabled && RimMandrakeFlowWorksSettings.climbingGearEnabled)
				|| RM_LadderParitySettings.ladderOverWalls) && RM_WallClimb.ClimbableWallAt(context.map, context.ClickedCell) != null;
		}

		protected override FloatMenuOption GetSingleOption(FloatMenuContext context)
		{
			Pawn p = context.FirstSelectedPawn;
			Building wall = RM_WallClimb.ClimbableWallAt(context.map, context.ClickedCell);
			if (p == null || wall == null || !RM_LadderParity.MightClimb(p))
			{
				return null;
			}
			string label = "RMFlow_ClimbOverWall".Translate(wall.LabelShort);
			if (!RM_WallClimb.TryBestCrossing(p, context.ClickedCell, false, out IntVec3 from, out IntVec3 landing, out bool roofed))
			{
				return new FloatMenuOption(label + ": " + (roofed ? "RMFlow_ClimbOverWallRoofed".Translate()
					: "RMFlow_ClimbOverWallNoWay".Translate()), null);
			}
			IntVec3 wallCell = context.ClickedCell;
			return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
			{
				p.jobs.TryTakeOrderedJob(RM_WallClimb.MakeClimbJob(from, wallCell, landing), JobTag.Misc);
			}), p, new LocalTargetInfo(wallCell));
		}
	}

	/// <summary>
	/// Owner 2026-10-18 by card: <i>"They can route when shorter, but climbing should be SLOOOWW. Like x20 slow, so it's not
	/// something you do routinely."</i> The route planner for gear-wearers. Walls stay impassable to the path grid and to
	/// regions for everyone (so reachability and vanilla's pathfinder go on agreeing, and nobody else pays anything). When a
	/// gear-wearer starts a walk somewhere it can already reach, the planner (next pather tick, a few pawns a tick) asks the
	/// pathfinder once more, synchronously, with the player's climbable walls priced at the climb (RM_WallClimbMath.StepCost:
	/// slowFactor of the pawn's own steps a square) through vanilla's own seams: TraverseMode.PassAllDestroyablePlayerOwnedThings
	/// makes the player's impassable buildings passable at PathFinderCostTuning.costBlockedWallBase (set to the climb price,
	/// per-hit-point extra zeroed; PathGridJob.CostForCell, decompiled 1.6), and a PathRequest.IPathGridCustomizer offset grid
	/// (ushort >= 10000 = impassable, PathGridJob.CellIsPassable) shuts every player building that is not a climbable wall
	/// with an open crossing. If that route climbs, the ordinary route is asked too and the climb is taken only when it is
	/// cheaper in total (RM_WallClimbMath.ClimbIsShorter), the foot is reachable, and the landing reaches the destination by
	/// ordinary walking (so the resumed job never stalls). The pawn then does the climb job (walk, climb, land) and resumes
	/// what it was doing. Only player-owned walls are planned over (that is the mode vanilla offers); other walls are still
	/// climbed by order or by a raider with no way in.
	/// </summary>
	public static class RM_WallClimbRoute
	{
		private const int ReplanSameDestTicks = 250;
		private const int MinStraightDistSq = 3 * 3;
		/// <summary>A walk not planned within this many ticks is dropped (the pawn left, died, or the budget stayed full).</summary>
		private const int PendingTicks = 600;
		private const int PruneEveryTicks = 60;
		private static readonly Dictionary<Pawn, int> pending = new Dictionary<Pawn, int>();
		private static readonly Dictionary<int, KeyValuePair<IntVec3, int>> lastPlan = new Dictionary<int, KeyValuePair<IntVec3, int>>();
		private static readonly List<Pawn> pruneScratch = new List<Pawn>();
		private static int lastPrune = int.MinValue;

		public static bool AnyPending => pending.Count > 0;

		public static void ClearMemos()
		{
			pending.Clear();
			lastPlan.Clear();
			lastPrune = int.MinValue;
		}

		/// <summary>Drop pending walks of pawns no longer on a map, and stale ones (the dictionary held dead Pawns forever).</summary>
		private static void PrunePending(int now)
		{
			lastPrune = now;
			pruneScratch.Clear();
			foreach (KeyValuePair<Pawn, int> kv in pending)
			{
				Pawn p = kv.Key;
				if (p == null || !p.Spawned || p.Map == null || RM_WallClimbMath.MemoExpired(kv.Value, now, PendingTicks))
				{
					pruneScratch.Add(p);
				}
			}
			for (int i = 0; i < pruneScratch.Count; i++)
			{
				pending.Remove(pruneScratch[i]);
			}
			pruneScratch.Clear();
		}

		/// <summary>From StartPath: a gear-wearer has started a walk; plan it on its next pather tick. Settings and the gear
		/// first, so nobody else pays more than two static reads and an apparel scan.</summary>
		public static void NoteWalkStarted(Pawn p, LocalTargetInfo dest)
		{
			if (!RM_WallClimbSettings.wallClimbAutoRoute || !RM_WallClimbSettings.wallClimbEnabled || p?.Map == null
				|| !dest.IsValid || p.CurJob == null || p.CurJob.def == RM_WallClimbDefOf.RM_ClimbOverWall
				|| p.RaceProps == null || !p.RaceProps.Humanlike || !RM_WallClimb.CanClimb(p))
			{
				return;
			}
			if ((p.Position - dest.Cell).LengthHorizontalSquared < MinStraightDistSq)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			RM_WallClimbMemo.Observe(now);
			if (lastPlan.TryGetValue(p.thingIDNumber, out KeyValuePair<IntVec3, int> lp) && lp.Key == dest.Cell
				&& !RM_WallClimbMath.MemoExpired(lp.Value, now, ReplanSameDestTicks))
			{
				return;
			}
			if (pending.Count > 32)
			{
				PrunePending(now);
			}
			if (pending.Count > 256)
			{
				pending.Clear();
			}
			pending[p] = now;
		}

		/// <summary>From PatherTick: true when the pawn was sent over a wall (skip this pather tick).</summary>
		public static bool TryRunPending(Pawn p, Pawn_PathFollower pather, PathEndMode peMode)
		{
			if (!pending.ContainsKey(p))
			{
				return false;
			}
			int now = Find.TickManager.TicksGame;
			RM_WallClimbMemo.Observe(now);
			if (RM_WallClimbMath.MemoExpired(lastPrune, now, PruneEveryTicks))
			{
				PrunePending(now);
			}
			if (!pending.ContainsKey(p))
			{
				return false;
			}
			LocalTargetInfo dest = pather.Destination;
			if (!pather.Moving || !dest.IsValid || p.Map == null || p.CurJob == null
				|| p.CurJob.def == RM_WallClimbDefOf.RM_ClimbOverWall)
			{
				pending.Remove(p);
				return false;
			}
			// WALL_CLIMB_FIX_BUDGET_CAP_LEAKY_MEMOS: a plan is two pathfinds (Plan: through the walls, then the ordinary route),
			// paid from the budget the raider seam shares. Out of budget: it stays pending for a later tick.
			if (!RM_WallClimbMemo.Budget.TryTake(now, RM_WallClimbMath.PlanPathfinds))
			{
				return false;
			}
			pending.Remove(p);
			if (lastPlan.Count > 1024)
			{
				lastPlan.Clear();
			}
			lastPlan[p.thingIDNumber] = new KeyValuePair<IntVec3, int>(dest.Cell, now);
			Job climb = Plan(p, dest, peMode);
			if (climb == null)
			{
				return false;
			}
			bool resume = p.CurJob.def.suspendable;
			p.jobs.StartJob(climb, JobCondition.InterruptForced, null, resumeCurJobAfterwards: resume);
			return true;
		}

		/// <summary>The climb job that makes this walk shorter, or null.</summary>
		public static Job Plan(Pawn p, LocalTargetInfo dest, PathEndMode peMode)
		{
			Map map = p.Map;
			if (p.roping != null && p.roping.IsRopingOthers)
			{
				return null;
			}
			IntVec3 start = p.Position;
			RM_WallClimbGrid grid = RM_WallClimbGrid.For(map);
			if (grid == null || !grid.AnyClimbable)
			{
				return null;
			}
			PathFinderCostTuning tuning = PathFinderCostTuning.For(p);
			tuning.costBlockedWallBase = RM_WallClimbMath.StepCost(RM_WallClimbSettings.wallClimbSlowFactor, p.TicksPerMoveCardinal);
			tuning.costBlockedWallExtraPerHitPoint = 0f;
			tuning.costBlockedWallExtraForNaturalWalls = 0;
			TraverseParms over = TraverseParms.For(p, Danger.Deadly, TraverseMode.PassAllDestroyablePlayerOwnedThings);
			IntVec3 foot = IntVec3.Invalid, wall = IntVec3.Invalid, landing = IntVec3.Invalid;
			float climbCost;
			using (PawnPath through = map.pathFinder.FindPathNow(start, dest, over, tuning, peMode, grid))
			{
				if (through == null || !through.Found
					|| !FirstClimb(map, p, through.NodesReversed, out foot, out wall, out landing))
				{
					return null;
				}
				climbCost = through.TotalCost;
			}
			if ((foot != start && !p.CanReach(foot, PathEndMode.OnCell, Danger.Deadly))
				|| !map.reachability.CanReach(landing, dest, peMode, TraverseParms.For(p, Danger.Deadly)))
			{
				return null;
			}
			using (PawnPath normal = map.pathFinder.FindPathNow(start, dest, p, PathFinderCostTuning.For(p), peMode))
			{
				bool found = normal != null && normal.Found;
				if (!RM_WallClimbMath.ClimbIsShorter(found, found ? normal.TotalCost : -1f, true, climbCost))
				{
					return null;
				}
			}
			return RM_WallClimb.MakeClimbJob(foot, wall, landing);
		}

		/// <summary>The first climb on a path (nodes reversed: the last is the start): the square before the first climbable
		/// wall, that wall square, and where the crossing lands, which must be where the path goes next. False when something
		/// else that blocks the pawn comes first, or the crossing is closed.</summary>
		private static bool FirstClimb(Map map, Pawn p, List<IntVec3> nodes, out IntVec3 foot, out IntVec3 wall, out IntVec3 landing)
		{
			foot = wall = landing = IntVec3.Invalid;
			for (int i = nodes.Count - 1; i >= 0; i--)
			{
				IntVec3 c = nodes[i];
				Building b = c.GetEdifice(map);
				if (b == null || !b.BlocksPawn(p))
				{
					continue;
				}
				if (!RM_WallClimb.IsClimbableWall(b) || i == nodes.Count - 1)
				{
					return false;
				}
				IntVec3 before = nodes[i + 1];
				IntVec3 d = c - before;
				if (System.Math.Abs(d.x) + System.Math.Abs(d.z) != 1
					|| !RM_WallClimb.TryCrossing(map, before, c, out IntVec3 land, out int squares, out bool _))
				{
					return false;
				}
				int after = i - squares;
				if (after < 0 || nodes[after] != land)
				{
					return false;
				}
				foot = before;
				wall = c;
				landing = land;
				return true;
			}
			return false;
		}
	}

	/// <summary>The planner's offset grid for one map (PathRequest.IPathGridCustomizer): 10000 (impassable) on every
	/// player-owned impassable building that is not a climbable wall with an open crossing, 0 elsewhere. Rebuilt when older
	/// than RebuildTicks; a fresh object each time, because vanilla keys its grid-job cache on the customizer's identity, and
	/// the old array is disposed at once (it was only ever read by a FindPathNow that has already returned).</summary>
	public sealed class RM_WallClimbGrid : PathRequest.IPathGridCustomizer, System.IDisposable
	{
		private const int RebuildTicks = 250;
		private static readonly Dictionary<int, RM_WallClimbGrid> byMap = new Dictionary<int, RM_WallClimbGrid>();

		/// <summary>Every map's grid disposed and forgotten (a game loaded: map ids are reused by the next game).</summary>
		public static void ClearMemos()
		{
			foreach (RM_WallClimbGrid g in byMap.Values)
			{
				g.Dispose();
			}
			byMap.Clear();
		}
		private NativeArray<ushort> offsets;
		private int builtTick;
		public bool AnyClimbable { get; private set; }

		public NativeArray<ushort> GetOffsetGrid()
		{
			return offsets;
		}

		public void Dispose()
		{
			if (offsets.IsCreated)
			{
				offsets.Dispose();
			}
		}

		public static RM_WallClimbGrid For(Map map)
		{
			int now = Find.TickManager.TicksGame;
			RM_WallClimbMemo.Observe(now);
			if (byMap.TryGetValue(map.uniqueID, out RM_WallClimbGrid g) && g.offsets.IsCreated
				&& g.offsets.Length == map.cellIndices.NumGridCells && !RM_WallClimbMath.MemoExpired(g.builtTick, now, RebuildTicks))
			{
				return g;
			}
			g?.Dispose();
			byMap.Remove(map.uniqueID);
			if (byMap.Count > 0)
			{
				List<int> gone = null;
				foreach (int id in byMap.Keys)
				{
					if (!Find.Maps.Any(m => m.uniqueID == id))
					{
						(gone ??= new List<int>()).Add(id);
					}
				}
				if (gone != null)
				{
					foreach (int id in gone)
					{
						byMap[id].Dispose();
						byMap.Remove(id);
					}
				}
			}
			g = new RM_WallClimbGrid { builtTick = now };
			g.Build(map);
			byMap[map.uniqueID] = g;
			return g;
		}

		private void Build(Map map)
		{
			CellIndices idx = map.cellIndices;
			offsets = new NativeArray<ushort>(idx.NumGridCells, Allocator.Persistent);
			List<Building> mine = map.listerBuildings.allBuildingsColonist;
			for (int i = 0; i < mine.Count; i++)
			{
				Building b = mine[i];
				if (b?.def == null || b.def.passability != Traversability.Impassable || !b.Spawned)
				{
					continue;
				}
				if (RM_WallClimb.IsClimbableWall(b) && OpenFromSomeSide(map, b.Position))
				{
					AnyClimbable = true;
					continue;
				}
				foreach (IntVec3 c in b.OccupiedRect())
				{
					if (c.InBounds(map))
					{
						offsets[idx.CellToIndex(c)] = 10000;
					}
				}
			}
		}

		/// <summary>Some crossing over this wall square is open: from a foot beside it, or (the far square of a double
		/// wall) from a foot two squares off.</summary>
		private static bool OpenFromSomeSide(Map map, IntVec3 c)
		{
			for (int r = 0; r < 4; r++)
			{
				IntVec3 dir = new Rot4(r).FacingCell;
				IntVec3 foot = c - dir;
				if (!foot.InBounds(map))
				{
					continue;
				}
				if (RM_WallClimb.ClimbableWallAt(map, foot) == null)
				{
					if (RM_WallClimb.TryCrossing(map, foot, c, out IntVec3 _, out int _, out bool _))
					{
						return true;
					}
					continue;
				}
				IntVec3 foot2 = foot - dir;
				if (foot2.InBounds(map) && RM_WallClimb.ClimbableWallAt(map, foot2) == null
					&& RM_WallClimb.TryCrossing(map, foot2, foot, out IntVec3 _, out int _, out bool _))
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>WALL_CLIMB_FIX_BUDGET_CAP_LEAKY_MEMOS: the shared per-tick pathfind budget and the one place every wall-climb
	/// memo is forgotten: when a game finishes loading (Game.FinalizeInit, new or loaded), and whenever the tick is seen to
	/// go backwards (an earlier save loaded without a fresh Game, or a dev rewind). Before, the memos survived a load: a
	/// stamp from a later tick never expired ("now - stamp" stayed negative), pending held the old game's Pawns, and a map id
	/// reused by the new game could be handed the old game's offset grid.</summary>
	public static class RM_WallClimbMemo
	{
		public static readonly RM_WallClimbMath.PathfindBudget Budget = new RM_WallClimbMath.PathfindBudget();
		private static int lastSeenTick = int.MinValue;

		public static void Observe(int now)
		{
			if (RM_WallClimbMath.TimeWentBack(lastSeenTick, now))
			{
				ClearAll();
			}
			lastSeenTick = now;
		}

		public static void ClearAll()
		{
			RM_WallClimbRoute.ClearMemos();
			RM_Patch_GotoHostile_Climb.ClearMemos();
			RM_WallClimbGrid.ClearMemos();
			Budget.Reset();
			lastSeenTick = int.MinValue;
		}
	}

	[HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
	[RimMandrake.Shared.PatchFeature("Climbing gear routes over walls", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbAutoRoute")]
	public static class RM_Patch_GameInit_WallClimbMemos
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			RM_WallClimbMemo.ClearAll();
		}
	}

	/// <summary>A gear-wearer's walk is planned for a climb (RM_WallClimbRoute). Postfix, after vanilla's own reachability
	/// check: a walk vanilla refused never gets here as moving.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.StartPath))]
	[RimMandrake.Shared.PatchFeature("Climbing gear routes over walls", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbAutoRoute")]
	public static class RM_Patch_StartPath_WallClimbRoute
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn_PathFollower __instance, Pawn ___pawn)
		{
			if (!RM_WallClimbSettings.wallClimbAutoRoute || !__instance.Moving)
			{
				return;
			}
			RM_WallClimbRoute.NoteWalkStarted(___pawn, __instance.Destination);
		}
	}

	/// <summary>The planned walk runs on the pawn's next pather tick (never inside the toil that called StartPath). One
	/// dictionary count for everyone while nothing is pending.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.PatherTick))]
	[RimMandrake.Shared.PatchFeature("Climbing gear routes over walls", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbAutoRoute")]
	public static class RM_Patch_PatherTick_WallClimbRoute
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn, PathEndMode ___peMode)
		{
			if (!RM_WallClimbRoute.AnyPending || ___pawn == null)
			{
				return true;
			}
			return !RM_WallClimbRoute.TryRunPending(___pawn, __instance, ___peMode);
		}
	}

	/// <summary>A pawn kind's or faction's chance of being generated wearing climbing gear (patched onto the defs:
	/// FlowWorks' vanilla light raiders, UtinniPatches' named factions).</summary>
	public class RM_ClimbingGearChance : DefModExtension
	{
		public float chance;
	}

	/// <summary>Owner 2026-10-18 by card: <i>"Wildsteam should have this. Junkers and Blackstar should. Jawa should. Deep
	/// Desert tribes yes. Then breachers and sappers from anyone."</i> Puts the gear on a pawn when it fits beside what is
	/// worn (it never replaces a shield belt or a warcasket piece).</summary>
	public static class RM_ClimbingGearGiver
	{
		private static ThingDef gearDef;
		private static bool looked;

		public static bool Enabled => RM_WallClimbSettings.raidersCarryClimbingGear && RimMandrakeFlowWorksSettings.climbingGearEnabled;

		public static void TryGive(Pawn pawn, float chance)
		{
			if (chance <= 0f || pawn?.apparel == null || pawn.RaceProps == null || !pawn.RaceProps.Humanlike || pawn.Dead
				|| !Rand.Chance(chance) || RM_PocketGrid.WearsClimbingGear(pawn))
			{
				return;
			}
			if (!looked)
			{
				looked = true;
				gearDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ClimbingGear");
			}
			if (gearDef == null || !ApparelUtility.HasPartsToWear(pawn, gearDef))
			{
				return;
			}
			List<Apparel> worn = pawn.apparel.WornApparel;
			for (int i = 0; i < worn.Count; i++)
			{
				if (!ApparelUtility.CanWearTogether(gearDef, worn[i].def, pawn.RaceProps.body))
				{
					return;
				}
			}
			if (!(ThingMaker.MakeThing(gearDef) is Apparel gear) || !gear.PawnCanWear(pawn))
			{
				return;
			}
			pawn.apparel.Wear(gear, false);
		}
	}

	/// <summary>After vanilla dresses a generated pawn (PawnGenerator.GenerateGearFor, decompiled 1.6): roll the higher of
	/// its kind's and its faction's RM_ClimbingGearChance (the named factions, a few light tribal and pirate kinds).</summary>
	[HarmonyPatch(typeof(PawnGenerator), "GenerateGearFor")]
	[RimMandrake.Shared.PatchFeature("Raiders carry climbing gear", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "raidersCarryClimbingGear")]
	public static class RM_Patch_GenerateGear_ClimbingGear
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, PawnGenerationRequest request)
		{
			if (!RM_ClimbingGearGiver.Enabled || request.ForceNoGear || pawn?.kindDef == null)
			{
				return;
			}
			Faction fac = request.Faction ?? pawn.Faction;
			float kindChance = pawn.kindDef.GetModExtension<RM_ClimbingGearChance>()?.chance ?? 0f;
			float facChance = fac?.def?.GetModExtension<RM_ClimbingGearChance>()?.chance ?? 0f;
			RM_ClimbingGearGiver.TryGive(pawn, RM_WallClimbMath.GearChance(kindChance, facChance, false, 0f,
				RM_WallClimbSettings.raiderGearChanceScale, true, fac != null && fac.IsPlayer));
		}
	}

	/// <summary>"Breachers and sappers from anyone": when a sapper or breaching raid forms its lords (RaidStrategyWorker.MakeLords;
	/// the two workers do not override it), each pawn of the kind that worker picks for the job (canBeSapper /
	/// isGoodBreacher, RaidStrategyWorker_ImmediateAttack*.MatchesRequiredPawnKind) or that carries a breaching weapon, of
	/// any faction, gets the gear at the breacher/sapper chance. Not at generation: every tribal warrior and thrasher is
	/// sapper-capable, and the ruling gives those only a small chance.</summary>
	[HarmonyPatch(typeof(RaidStrategyWorker), nameof(RaidStrategyWorker.MakeLords))]
	[RimMandrake.Shared.PatchFeature("Raiders carry climbing gear", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "raidersCarryClimbingGear")]
	public static class RM_Patch_RaidLords_ClimbingGear
	{
		[HarmonyPostfix]
		public static void Postfix(RaidStrategyWorker __instance, IncidentParms parms, List<Pawn> pawns)
		{
			bool sappers = __instance is RaidStrategyWorker_ImmediateAttackSappers;
			bool breach = __instance is RaidStrategyWorker_ImmediateAttackBreaching;
			if ((!sappers && !breach) || pawns == null || !RM_ClimbingGearGiver.Enabled)
			{
				return;
			}
			bool player = parms?.faction != null && parms.faction.IsPlayer;
			float chance = RM_WallClimbMath.GearChance(0f, 0f, true, RM_WallClimbSettings.breacherSapperGearChance,
				RM_WallClimbSettings.raiderGearChanceScale, true, player);
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p?.kindDef == null)
				{
					continue;
				}
				bool job = sappers ? p.kindDef.canBeSapper : (p.kindDef.isGoodBreacher || BreachingUtility.IsGoodBreacher(p));
				if (job)
				{
					RM_ClimbingGearGiver.TryGive(p, chance);
				}
			}
		}
	}
}
