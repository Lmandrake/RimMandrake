using System.Collections.Generic;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks.Pits
{
	[DefOf]
	public static class RM_DrawbridgeRaidDefOf
	{
		public static ThingDef RM_RaidPlank;
		public static ThingDef RM_RaidPlank_Laid;
		public static JobDef RM_LayRaidPlank;

		static RM_DrawbridgeRaidDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_DrawbridgeRaidDefOf));
		}
	}

	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 4 (R5, answer 6 "1+3"): sappers and breachers go for the winch house of a
	/// raised leaf when the colony is cut off. Inserted BEFORE the vanilla sapper / breaching givers in those two duties
	/// (Patches/RaiderTrench), and acts only when the raid's target is unreachable even through destroyable things (the same
	/// test the trench rules use), so a colony reachable by land is sapped as vanilla does it. Route: walk (digging through
	/// what blocks, as the vanilla sapper does) and hit it; a winch on a bank they cannot reach is shot at from a firing
	/// position, if they have a gun. Sieges never.
	/// </summary>
	public class JobGiver_RM_DrawbridgeWinch : ThinkNode_JobGiver
	{
		public static int WinchJobs;

		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_DrawbridgeSettings.drawbridgesEnabled || pawn?.Map == null || pawn.Downed || pawn.Faction == null
				|| !pawn.HostileTo(Faction.OfPlayer) || pawn.GetLord() == null || RM_RaiderTrench.IsSiege(pawn))
			{
				return null;
			}
			Building_DrawbridgeWinch winch = RM_DrawbridgeRaid.NearestRaisedWinch(pawn);
			if (winch == null)
			{
				return null;
			}
			Thing target = RM_RaiderTrench.TargetFor(pawn);
			if (target != null && pawn.CanReach(target, PathEndMode.Touch, Danger.Deadly, false, false, TraverseMode.PassAllDestroyableThings))
			{
				return null;   // the colony is reachable: vanilla sappers / breachers act
			}
			Job job = RM_DrawbridgeRaid.WinchJob(pawn, winch);
			if (job != null)
			{
				WinchJobs++;
			}
			return job;
		}
	}

	public static class RM_DrawbridgeRaid
	{
		/// <summary>The nearest player winch house whose leaf is up (or going up): the one that keeps the moat open.</summary>
		public static Building_DrawbridgeWinch NearestRaisedWinch(Pawn p)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(p.Map);
			if (comp == null)
			{
				return null;
			}
			Building_DrawbridgeWinch best = null;
			int bestD = int.MaxValue;
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					Building_DrawbridgeWinch w = l.winch;
					if (w == null || !w.Spawned || w.Faction != Faction.OfPlayer || (l.progress <= 0 && !l.targetRaised))
					{
						continue;
					}
					int d = w.Position.DistanceToSquared(p.Position);
					if (d < bestD)
					{
						bestD = d;
						best = w;
					}
				}
			}
			return best;
		}

		/// <summary>An executable attack on the winch, or null (R5: winch attacks need an executable route).</summary>
		public static Job WinchJob(Pawn pawn, Building_DrawbridgeWinch winch)
		{
			Map map = pawn.Map;
			if (pawn.CanReach(winch, PathEndMode.Touch, Danger.Deadly, false, false, TraverseMode.PassAllDestroyableThings))
			{
				using (PawnPath path = map.pathFinder.FindPathNow(pawn.Position, winch, TraverseParms.For(pawn, Danger.Deadly,
					TraverseMode.PassAllDestroyableThings), null, PathEndMode.Touch))
				{
					IntVec3 before = IntVec3.Invalid;
					Thing blocker = path == null || !path.Found ? null : path.FirstBlockingBuilding(out before, pawn);
					if (blocker != null && blocker != winch)
					{
						Job dig = DigUtility.PassBlockerJob(pawn, blocker, before, true, true);
						if (dig != null)
						{
							return dig;
						}
					}
				}
				if (pawn.CanReach(winch, PathEndMode.Touch, Danger.Deadly))
				{
					Job melee = JobMaker.MakeJob(JobDefOf.AttackMelee, winch);
					melee.expiryInterval = 600;
					melee.checkOverrideOnExpire = true;
					return melee;
				}
			}
			Verb verb = pawn.TryGetAttackVerb(winch, true);
			if (verb == null || verb.verbProps.IsMeleeAttack)
			{
				return null;   // the far bank and no gun: nothing executable (the trench rules may still act)
			}
			if (!CastPositionFinder.TryFindCastPosition(new CastPositionRequest
				{
					caster = pawn,
					target = winch,
					verb = verb,
					maxRangeFromTarget = verb.verbProps.range,
					wantCoverFromTarget = false,
				}, out IntVec3 dest))
			{
				return null;
			}
			if (dest == pawn.Position)
			{
				Job shoot = JobMaker.MakeJob(JobDefOf.AttackStatic, winch);
				shoot.expiryInterval = 600;
				shoot.checkOverrideOnExpire = true;
				return shoot;
			}
			Job go = JobMaker.MakeJob(JobDefOf.Goto, dest);
			go.expiryInterval = 600;
			go.checkOverrideOnExpire = true;
			return go;
		}
	}

	/// <summary>
	/// Phase 4 (R5, GPT #13): raid planks. Some raids against a colony with a drawbridge carry planks (an inventory item, the
	/// raid's own; never the colony's art planks). The trench rules offer a plank first when the raider carries one and the
	/// crossing line fits (RM_DrawbridgeMath.RaidPlankFits). Laying is one transaction per plank, committed exactly once
	/// (PlankLedger): an interrupted carrier lays nothing and keeps its plank; a line already planked is refused. A laid plank
	/// is a one-lane timber span (a SuspensionBridgeRecord flagged raidPlank) under the ordinary load, fire and break rules.
	/// </summary>
	public static class RM_RaidPlanks
	{
		private static readonly ConditionalWeakTable<Map, RM_DrawbridgeMath.PlankLedger> ledgers =
			new ConditionalWeakTable<Map, RM_DrawbridgeMath.PlankLedger>();

		public static int PlanksGiven;
		public static int PlanksLaid;

		public static RM_DrawbridgeMath.PlankLedger LedgerOf(Map map)
		{
			return ledgers.GetValue(map, _ => new RM_DrawbridgeMath.PlankLedger());
		}

		public static Thing CarriedPlank(Pawn p)
		{
			if (p?.inventory?.innerContainer == null || RM_DrawbridgeRaidDefOf.RM_RaidPlank == null)
			{
				return null;
			}
			foreach (Thing t in p.inventory.innerContainer)
			{
				if (t.def == RM_DrawbridgeRaidDefOf.RM_RaidPlank)
				{
					return t;
				}
			}
			return null;
		}

		/// <summary>The lay job for this crossing line (lip first, far bank last), or null.</summary>
		internal static Job PlankJob(Pawn p, List<IntVec3> cells, int[] depths)
		{
			if (!RM_DrawbridgeSettings.drawbridgesEnabled || !RM_DrawbridgeSettings.raidsBringPlanks || cells == null || cells.Count < 3)
			{
				return null;
			}
			Thing plank = CarriedPlank(p);
			if (plank == null || !LineFree(p.Map, cells, depths))
			{
				return null;
			}
			Map map = p.Map;
			long line = RM_DrawbridgeMath.PlankLedger.LineKey(map.cellIndices.CellToIndex(cells[0]), map.cellIndices.CellToIndex(cells[cells.Count - 1]));
			if (!LedgerOf(map).CanCommit(plank.thingIDNumber, line))
			{
				return null;
			}
			if (cells[0] != p.Position && !p.CanReach(cells[0], PathEndMode.OnCell, Danger.Deadly))
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_DrawbridgeRaidDefOf.RM_LayRaidPlank, cells[0], cells[cells.Count - 1]);
			job.expiryInterval = 2500;
			return job;
		}

		/// <summary>The line fits a plank and nothing is built over its hole squares (no deck, raised or not, no building).</summary>
		public static bool LineFree(Map map, List<IntVec3> cells, int[] depths)
		{
			if (!RM_DrawbridgeMath.RaidPlankFits(depths, RM_DrawbridgeMath.RaidPlankMaxSpan))
			{
				return false;
			}
			for (int i = 1; i < cells.Count - 1; i++)
			{
				if (!cells[i].InBounds(map) || RM_MapComponent_SuspensionBridges.AnyPartAt(map, cells[i]) || cells[i].GetEdifice(map) != null)
				{
					return false;
				}
			}
			return cells[cells.Count - 1].Standable(map);
		}

		/// <summary>The commit: re-read the line, take the plank out of the carrier's hands exactly once, lay the span.</summary>
		public static bool TryLay(Pawn p, IntVec3 lip, IntVec3 far)
		{
			Map map = p?.Map;
			if (map == null || !lip.InBounds(map) || !far.InBounds(map))
			{
				return false;
			}
			IntVec3 step = far - lip;
			if (step.x != 0 && step.z != 0)
			{
				return false;   // planks are laid along a cardinal line
			}
			int n = System.Math.Abs(step.x) + System.Math.Abs(step.z);
			IntVec3 dir = new IntVec3(System.Math.Sign(step.x), 0, System.Math.Sign(step.z));
			List<IntVec3> cells = new List<IntVec3>();
			int[] depths = new int[n + 1];
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			for (int i = 0; i <= n; i++)
			{
				IntVec3 c = lip + dir * i;
				cells.Add(c);
				depths[i] = eng == null ? 0 : RM_SuperdeepTrap.StepDepthAt(map, eng, c);
			}
			Thing plank = CarriedPlank(p);
			if (plank == null || !LineFree(map, cells, depths))
			{
				return false;
			}
			long line = RM_DrawbridgeMath.PlankLedger.LineKey(map.cellIndices.CellToIndex(lip), map.cellIndices.CellToIndex(far));
			if (!LedgerOf(map).TryCommit(plank.thingIDNumber, line))
			{
				return false;
			}
			if (plank.stackCount > 1)
			{
				plank.SplitOff(1).Destroy(DestroyMode.Vanish);
			}
			else
			{
				plank.Destroy(DestroyMode.Vanish);
			}
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			SuspensionBridgeRecord rec = comp.Register(new SuspensionBridgeRecord
			{
				tier = SuspensionTier.Timber,
				origin = lip,
				dir = Rot4.FromIntVec3(dir),
				length = n + 1,
				width = 1,
				raidPlank = true,
			});
			List<IntVec3> laid = new List<IntVec3>();
			for (int i = 1; i < n; i++)
			{
				Thing deck = ThingMaker.MakeThing(RM_DrawbridgeRaidDefOf.RM_RaidPlank_Laid);
				deck.SetFaction(p.Faction);
				GenSpawn.Spawn(deck, cells[i], map, rec.dir);
				laid.Add(cells[i]);
			}
			PlanksLaid++;
			RM_Drawbridges.NotifyToggled(map, laid);   // a crossing appeared: every path sees it now (R8)
			Messages.Message(p.LabelShort + " laid a plank across the moat.", new LookTargets(p), MessageTypeDefOf.ThreatSmall);
			return true;
		}
	}

	/// <summary>Walk to the lip, lay the plank (RaidPlankLayTicks), commit once. Interrupted before the last toil: nothing laid.</summary>
	public class JobDriver_RM_LayRaidPlank : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
			Toil lay = Toils_General.Wait(RM_DrawbridgeMath.RaidPlankLayTicks, TargetIndex.B);
			lay.WithProgressBarToilDelay(TargetIndex.A);
			lay.FailOn(() => RM_RaidPlanks.CarriedPlank(pawn) == null);
			yield return lay;
			Toil commit = ToilMaker.MakeToil("RM_LayRaidPlankCommit");
			commit.initAction = () => RM_RaidPlanks.TryLay(pawn, job.targetA.Cell, job.targetB.Cell);
			commit.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return commit;
		}
	}

	/// <summary>Some raids against a map with a drawbridge carry planks (setting "Raids bring planks", its chance per raid):
	/// one per four raiders, to humanlike raiders. Sieges never.</summary>
	[HarmonyPatch(typeof(IncidentWorker_Raid), "PostProcessSpawnedPawns")]
	[RimMandrake.Shared.PatchFeature("Raids bring planks against drawbridges", typeof(RimMandrake.FlowWorks.Pits.RM_DrawbridgeSettings), "raidsBringPlanks")]
	public static class RM_Patch_Raid_Planks
	{
		[HarmonyPostfix]
		public static void Postfix(IncidentParms parms, List<Pawn> pawns)
		{
			if (!RM_DrawbridgeSettings.drawbridgesEnabled || !RM_DrawbridgeSettings.raidsBringPlanks || pawns == null
				|| !(parms?.target is Map map) || parms.raidStrategy?.Worker is RaidStrategyWorker_Siege
				|| RM_DrawbridgeRaidDefOf.RM_RaidPlank == null || !AnyDrawbridge(map) || !Rand.Chance(RM_DrawbridgeSettings.raidPlankChance))
			{
				return;
			}
			int give = RM_DrawbridgeMath.RaidPlankCount(pawns.Count);
			foreach (Pawn p in pawns)
			{
				if (give <= 0)
				{
					break;
				}
				if (p?.inventory == null || !p.RaceProps.Humanlike || p.Downed)
				{
					continue;
				}
				p.inventory.innerContainer.TryAdd(ThingMaker.MakeThing(RM_DrawbridgeRaidDefOf.RM_RaidPlank));
				RM_RaidPlanks.PlanksGiven++;
				give--;
			}
		}

		private static bool AnyDrawbridge(Map map)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			if (comp == null)
			{
				return false;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (r.IsDrawbridge)
				{
					return true;
				}
			}
			return false;
		}
	}
}
