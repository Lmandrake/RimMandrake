using System.Collections.Generic;
using HarmonyLib;
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
				if (!TryCrossing(map, foot, wallCell, out IntVec3 land, out int _, out bool roofed))
				{
					anyRoofed |= roofed;
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
			if (!(blocker is Building b) || !IsClimbableWall(b) || !cellBefore.IsValid || !CanClimb(p))
			{
				return null;
			}
			if (!WallCellNextTo(p.Map, cellBefore, blocker, out IntVec3 wallCell)
				|| !TryCrossing(p.Map, cellBefore, wallCell, out IntVec3 landing, out int _, out bool _))
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
			return RM_WallClimb.CanClimb(pawn)
				&& RM_WallClimb.TryCrossing(pawn.Map, Foot, WallCell, out IntVec3 land, out int _, out bool _)
				&& land == Landing;
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			int squares = 1;
			if (RM_WallClimb.TryCrossing(Map, Foot, WallCell, out IntVec3 _, out int sq, out bool _))
			{
				squares = sq;
			}
			yield return Toils_Goto.GotoCell(TargetIndex.C, PathEndMode.OnCell);
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
			climb.defaultDuration = RM_WallClimbMath.ClimbTicks(squares, RM_WallClimbSettings.wallClimbSpeed,
				pawn.GetStatValue(StatDefOf.MoveSpeed));
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
				|| !RM_WallClimb.CanClimb(pawn))
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
			if (!RM_WallClimbSettings.wallClimbEnabled || ___pawn?.Map == null)
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
			if (!wouldBash || ___pawn.CurJob?.def == RM_WallClimbDefOf.RM_ClimbOverWall || !RM_WallClimb.CanClimb(___pawn)
				|| !RM_WallClimb.TryCrossing(map, ___pawn.Position, next, out IntVec3 landing, out int _, out bool _))
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
	/// through-walls path to the nearest enemy is climbed. Throttled per pawn (300 ticks), and only gear-wearers pay.</summary>
	[HarmonyPatch(typeof(JobGiver_AIGotoNearestHostile), "TryGiveJob")]
	[RimMandrake.Shared.PatchFeature("Climbing gear scales walls (raiders get in)", typeof(RimMandrake.FlowWorks.RM_WallClimbSettings), "wallClimbEnabled")]
	public static class RM_Patch_GotoHostile_Climb
	{
		private const int RetryTicks = 300;
		private const float MaxDistSq = 90f * 90f;
		private static readonly Dictionary<int, int> nextTry = new Dictionary<int, int>();

		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, ref Job __result)
		{
			if (__result != null || pawn?.Map == null || pawn.Faction == Faction.OfPlayer || !RM_WallClimb.CanClimb(pawn))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (nextTry.TryGetValue(pawn.thingIDNumber, out int at) && now < at)
			{
				return;
			}
			if (nextTry.Count > 512)
			{
				nextTry.Clear();
			}
			nextTry[pawn.thingIDNumber] = now + RetryTicks;
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
				return;
			}
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
			return RM_WallClimbSettings.wallClimbEnabled && RimMandrakeFlowWorksSettings.climbingGearEnabled
				&& RM_WallClimb.ClimbableWallAt(context.map, context.ClickedCell) != null;
		}

		protected override FloatMenuOption GetSingleOption(FloatMenuContext context)
		{
			Pawn p = context.FirstSelectedPawn;
			Building wall = RM_WallClimb.ClimbableWallAt(context.map, context.ClickedCell);
			if (p == null || wall == null || !RM_WallClimb.CanClimb(p))
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
}
