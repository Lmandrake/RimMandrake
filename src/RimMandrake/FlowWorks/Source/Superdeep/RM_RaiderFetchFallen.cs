using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN (bars inv_raider_fetch_fallen, raiders_fetch_their_fallen): <i>"The player
	/// whose pit trap has caught two raiders watches the rest chop wood, make a ladder and go down for their fallen; when the
	/// defenders drive them off they retreat and leave the fallen behind."</i>
	///
	/// A raider of an assault (JobGiver_RM_FetchFallen, put ahead of JobGiver_AIFightEnemies in AssaultColony by
	/// Patches/RaiderTrench) looks for a comrade of its own faction the pit holds, or one lying downed down there. No way down:
	/// it plans the ladder line from its lip to him (RM_RaiderTrench.TryPlan) and sets it the way a trench crossing does
	/// (RM_RaiderTrench.LadderJob: a carried ladder, one it takes, wood it has, or a tree it fells for wood). A way down: it
	/// climbs down, picks up a downed comrade and carries him to the lip; a standing one walks out by the ladder on his own.
	///
	/// Under fire it leaves them: a raider harmed in the last UnderFireTicks starts no fetch and drops the one it is on, so the
	/// duty's next giver (FightEnemies) takes over; when the raid's lord breaks and flees, the flee duty holds no fetch giver at
	/// all, so the fallen stay where they are. Sieges never fetch (they shell you). The ladder they set is theirs, as a crossing
	/// ladder is (RM_RaiderTrench): shoot it and whoever is down there is in a pit again.
	/// </summary>
	public static class RM_RaiderFetchFallen
	{
		/// <summary>How far (squares) a raider looks for a fallen comrade.</summary>
		public const int FetchRadius = 30;

		/// <summary>A raider harmed this recently (ticks; 600 = 10 s) is under fire.</summary>
		public const int UnderFireTicks = 600;

		public static bool On => RM_RaiderTrenchSettings.raiderFetchFallenEnabled && RM_RaiderTrench.On;

		/// <summary>The lip the first rescuer planned from, per fallen pawn: later rescuers use the same ladder line.</summary>
		private static readonly Dictionary<int, (int tick, IntVec3 lip)> fetchLips = new Dictionary<int, (int, IntVec3)>();

		/// <summary>A lift the pickup refused, per fallen pawn (tick): the giver hands no carry out for him again until
		/// RefusedLiftTicks pass, so a rescuer who cannot get down does not take and drop the job every tick.</summary>
		private static readonly Dictionary<int, int> refusedLifts = new Dictionary<int, int>();

		/// <summary>How long (ticks; 250 = about 4 s) a refused lift keeps the carry from being handed out again.</summary>
		public const int RefusedLiftTicks = 250;

		public static void ClearMemos()
		{
			fetchLips.Clear();
			refusedLifts.Clear();
		}

		/// <summary>May <paramref name="p"/> pick <paramref name="fallen"/> up from where the two stand now? Only across a
		/// step he could climb (RM_RaiderTrenchMath.FetchLiftAllowed), read off the dug depths, never off a reach answer:
		/// live 2026-11-23 a raider on the rim of a 4 m pit touched a downed comrade and carried him out, no ladder.</summary>
		public static bool MayLift(Pawn p, Pawn fallen)
		{
			if (p?.Map == null || fallen == null || !fallen.Spawned || fallen.Map != p.Map)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			return RM_RaiderTrenchMath.FetchLiftAllowed(RM_SuperdeepTrap.StepDepthAt(p.Map, eng, p.Position),
				RM_SuperdeepTrap.StepDepthAt(p.Map, eng, fallen.Position), RM_PocketGrid.ClimbLimitOf(p));
		}

		public static void NoteRefusedLift(Pawn fallen)
		{
			if (fallen != null)
			{
				refusedLifts[fallen.thingIDNumber] = Find.TickManager?.TicksGame ?? 0;
			}
		}

		public static bool RecentlyRefused(Pawn fallen)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			return fallen != null && refusedLifts.TryGetValue(fallen.thingIDNumber, out int t) && now >= t && now - t < RefusedLiftTicks;
		}

		public static bool UnderFire(Pawn p)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			return p?.mindState != null && now - p.mindState.lastHarmTick < UnderFireTicks;
		}

		/// <summary>A raider that may go for its fallen: spawned, standing, hostile, of a raid's lord, a tool user, not itself
		/// held.</summary>
		public static bool Rescuer(Pawn p)
		{
			return p != null && p.Spawned && !p.Downed && !p.Dead && p.Faction != null && Faction.OfPlayer != null
				&& p.Faction != Faction.OfPlayer && p.Faction.HostileTo(Faction.OfPlayer) && p.GetLord() != null
				&& RM_RaiderTrench.ToolUser(p) && !RM_RaiderTrench.IsSiege(p) && !RM_SuperdeepTrap.IsTrapped(p);
		}

		/// <summary>Is <paramref name="c"/> one of <paramref name="p"/>'s fallen: held in the pit, or downed down there (once a
		/// ladder stands he is no longer held, and a downed one still has to be carried up).</summary>
		public static bool IsFallen(Pawn p, Pawn c)
		{
			return c != p && c.Spawned && !c.Dead && (RM_SuperdeepTrap.IsHeld(c) || (c.Downed && RM_SuperdeepTrap.StepDepthAt(c.Map,
				RM_SuperdeepTrap.EngineOf(c.Map), c.Position) > 0)) && c.Faction == p.Faction;
		}

		/// <summary>The nearest fallen comrade this raider can take on (not reserved by another rescuer), or null.</summary>
		public static Pawn FallenFor(Pawn p)
		{
			Pawn best = null;
			int bestD = FetchRadius * FetchRadius + 1;
			List<Pawn> kin = p.Map.mapPawns.SpawnedPawnsInFaction(p.Faction);
			for (int i = 0; i < kin.Count; i++)
			{
				Pawn c = kin[i];
				int d = c.Position.DistanceToSquared(p.Position);
				if (d < bestD && IsFallen(p, c) && p.CanReserve(c))
				{
					best = c;
					bestD = d;
				}
			}
			return best;
		}

		/// <summary>The whole decision for one raider, or null for the duty's next giver.</summary>
		public static Job TryFetch(Pawn p)
		{
			if (!On || p?.Map == null || !RM_SuperdeepTrap.AnyHole(RM_SuperdeepTrap.EngineOf(p.Map)) || !Rescuer(p))
			{
				return null;
			}
			if (UnderFire(p))
			{
				return null;
			}
			Pawn fallen = FallenFor(p);
			if (fallen == null)
			{
				return null;
			}
			// A way down is a walk ONTO his square. Touch is no test of it: a man on a pit square beside undug ground is
			// touched from the lip, so every held man in a pit two squares wide read "reachable" and nobody set a ladder
			// (RIMMANDRAKE_TRACE_FLOWWORKS_FALLEN_RAIDER_WAITS_FOR_NO_LADDER, live 2026-11-21).
			if (p.CanReach(fallen.Position, PathEndMode.OnCell, Danger.Deadly))
			{
				// a standing comrade climbs out by the ladder himself; a downed one is carried up
				return fallen.Downed && !RecentlyRefused(fallen) ? CarryJob(p, fallen, LipFor(p, fallen)) : null;
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			IntVec3 origin = MemoLip(p, fallen, k);
			if (!RM_RaiderTrench.TryPlan(p, k, fallen, origin, out RM_RaiderTrench.Plan plan)
				&& !RM_RaiderTrench.TryPlan(p, k, fallen, p.Position, out plan))
			{
				return null;
			}
			// the plan ends on the pit's edge square (his level): the ladder stands there, the line's last square
			Job ladder = RM_RaiderTrench.LadderJob(p, plan, k, out bool waiting, true);
			if (ladder == null)
			{
				return null;   // waiting on another rescuer's ladder, or ladders cannot reach him: fight instead
			}
			fetchLips[fallen.thingIDNumber] = (Find.TickManager.TicksGame, plan.cells[0]);
			RM_RaiderTrench.Warn(p, "RMFlow_RaidersFetchFallen");
			return ladder;
		}

		private static IntVec3 MemoLip(Pawn p, Pawn fallen, int k)
		{
			if (fetchLips.TryGetValue(fallen.thingIDNumber, out (int tick, IntVec3 lip) e)
				&& Find.TickManager.TicksGame - e.tick < RM_RaiderTrench.PlanCacheTicks && e.lip.InBounds(p.Map))
			{
				RM_PocketGrid g = RM_PocketGrid.ForPawn(p.Map, p);
				if (g.ComponentOf(k, e.lip) == g.ComponentOf(k, p.Position))
				{
					return e.lip;
				}
			}
			return p.Position;
		}

		/// <summary>Where a carried comrade is set down: the lip the ladder went in from, else where the rescuer stands now
		/// when that is out of the pit, else (the rescuer already down there) invalid: no carry.</summary>
		private static IntVec3 LipFor(Pawn p, Pawn fallen)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			if (fetchLips.TryGetValue(fallen.thingIDNumber, out (int tick, IntVec3 lip) e) && e.lip.InBounds(p.Map)
				&& RM_SuperdeepTrap.StepDepthAt(p.Map, eng, e.lip) == 0)
			{
				return e.lip;
			}
			return RM_SuperdeepTrap.StepDepthAt(p.Map, eng, p.Position) == 0 ? p.Position : IntVec3.Invalid;
		}

		private static Job CarryJob(Pawn p, Pawn fallen, IntVec3 lip)
		{
			if (!lip.IsValid || RM_RaiderTrenchDefOf.RM_RaiderFetchFallen == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_RaiderTrenchDefOf.RM_RaiderFetchFallen, fallen, lip);
			job.count = 1;
			job.locomotionUrgency = LocomotionUrgency.Jog;
			return job;
		}

		/// <summary>Bridge/debug read (jawa/static_call): the fetch decision for one raider, by thingIDNumber.</summary>
		public static string ProofFetchFallen(string pawnId)
		{
			Map map = Find.CurrentMap;
			if (map == null || !int.TryParse(pawnId, out int id))
			{
				return "REFUSED: ProofFetchFallen:pawnId (a map current)";
			}
			Pawn p = null;
			foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
			{
				if (q.thingIDNumber == id)
				{
					p = q;
					break;
				}
			}
			if (p == null)
			{
				return "REFUSED: no spawned pawn " + id;
			}
			Pawn fallen = Rescuer(p) ? FallenFor(p) : null;
			return "FETCH on=" + On + " rescuer=" + Rescuer(p) + " underFire=" + UnderFire(p) + " fallen="
				+ (fallen == null ? "none" : fallen.thingIDNumber + " downed=" + fallen.Downed + " held=" + RM_SuperdeepTrap.IsHeld(fallen)
				+ " reach=" + p.CanReach(fallen.Position, PathEndMode.OnCell, Danger.Deadly)
				+ " touch=" + p.CanReach(fallen, PathEndMode.ClosestTouch, Danger.Deadly)) + " job=" + (p.CurJobDef?.defName ?? "none");
		}
	}

	/// <summary>Bridge/debug read (jawa/static_call), kept apart from the decision: WHY one raider gets a ladder job for its
	/// fallen or not, step by step (the plan line, its depths, the ladder's reach, the slots, the supply).
	/// "PLAN k=K fallen=id cs=A ct=B plan=memo|here|none cells=x,z..x,z depths=0/6 reach=6 slots=N carried=b wood=N job=def|none waiting=b"</summary>
	public static class RM_RaiderFetchFallenProof
	{
		public static string ProofFetchPlan(string pawnId)
		{
			Map map = Find.CurrentMap;
			if (map == null || !int.TryParse(pawnId, out int id))
			{
				return "REFUSED: ProofFetchPlan:pawnId (a map current)";
			}
			Pawn p = null;
			foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
			{
				if (q.thingIDNumber == id)
				{
					p = q;
					break;
				}
			}
			if (p == null || !RM_RaiderFetchFallen.Rescuer(p))
			{
				return "REFUSED: no spawned rescuer " + id;
			}
			Pawn fallen = RM_RaiderFetchFallen.FallenFor(p);
			if (fallen == null)
			{
				return "PLAN fallen=none";
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			RM_PocketGrid g = RM_PocketGrid.ForPawn(map, p);
			string head = "PLAN k=" + k + " fallen=" + fallen.thingIDNumber + " at=" + fallen.Position.x + "," + fallen.Position.z
				+ " cs=" + g.ComponentOf(k, p.Position) + " ct=" + g.ComponentOf(k, fallen.Position);
			if (!RM_RaiderTrench.TryPlan(p, k, fallen, p.Position, out RM_RaiderTrench.Plan plan))
			{
				return head + " plan=none";
			}
			int reach = RM_LadderUtility.MaxLevelsOf(RimMandrakeFlowWorks_DefOf.RM_LadderPortable);
			List<RM_RaiderTrenchMath.LadderSlot> slots = RM_RaiderTrenchMath.LadderSlots(plan.depths, k, reach, true);
			Job job = RM_RaiderTrench.LadderJob(p, plan, k, out bool waiting, true);
			IntVec3 a = plan.cells[0], b = plan.cells[plan.cells.Count - 1];
			return head + " plan=here cells=" + a.x + "," + a.z + ".." + b.x + "," + b.z + " depths=" + string.Join("/", plan.depths)
				+ " reach=" + reach + " slots=" + (slots == null ? "null" : slots.Count.ToString())
				+ " carried=" + (RM_LadderParity.CarriedLadder(p) != null) + " wood=" + RM_LadderParity.WoodCarried(p)
				+ " job=" + (job?.def?.defName ?? "none") + " waiting=" + waiting;
		}
	}

	[HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
	[RimMandrake.Shared.PatchFeature("Raiders fetch their fallen", typeof(RimMandrake.FlowWorks.RM_RaiderTrenchSettings), "raiderFetchFallenEnabled")]
	public static class RM_Patch_GameInit_FetchFallenMemos
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			RM_RaiderFetchFallen.ClearMemos();
		}
	}

	/// <summary>Put ahead of JobGiver_AIFightEnemies in the AssaultColony duty (Patches/RaiderTrench). Null unless a comrade of
	/// this raider lies in a pit and it is not under fire.</summary>
	public class JobGiver_RM_FetchFallen : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			return RM_RaiderFetchFallen.TryFetch(pawn);
		}
	}

	/// <summary>Carry a downed comrade (targetA) out of the pit to the lip (targetB) and set him down. Dropped under fire.</summary>
	public class JobDriver_RM_RaiderFetchFallen : JobDriver
	{
		private Pawn Fallen => (Pawn)job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => !RM_RaiderFetchFallen.On);
			this.FailOn(() => RM_RaiderFetchFallen.UnderFire(pawn));
			AddFinishAction(cond =>
			{
				if (pawn.carryTracker?.CarriedThing != null)
				{
					pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
				}
				else if (cond == JobCondition.Incompletable || cond == JobCondition.ErroredPather)
				{
					// no way down to him after all (the walk onto his square failed): not handed out again at once
					RM_RaiderFetchFallen.NoteRefusedLift(job.targetA.Thing as Pawn);
				}
			});
			// The rescuer goes DOWN to him: onto his square, by a real way (a ladder, a climbable step). A touch from the rim
			// is no fetch (live 2026-11-23, save TP_FETCH_LIFTS_FROM_RIM_4M: a downed man lifted out of a 4 m pit, no ladder).
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.OnCell)
				.FailOn(() => !Fallen.Downed);
			Toil lift = ToilMaker.MakeToil("RM_RaiderFetchFallen_MayLift");
			lift.initAction = delegate
			{
				if (!RM_RaiderFetchFallen.MayLift(pawn, Fallen))
				{
					RM_RaiderFetchFallen.NoteRefusedLift(Fallen);
					EndJobWith(JobCondition.Incompletable);
				}
			};
			lift.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return lift;
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
			Toil drop = ToilMaker.MakeToil("RM_RaiderFetchFallen_Drop");
			drop.initAction = delegate
			{
				pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
			};
			drop.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return drop;
		}
	}
}
