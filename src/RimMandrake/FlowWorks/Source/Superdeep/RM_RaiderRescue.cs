using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RAIDERS_FETCH_THEIR_FALLEN — the Verse half (rules: RM_RaiderTrenchMath.FetchFallen, RescueDrop, ClaimLive). The
	/// owner's story: raiders fall into a covered spike pit; the others hack saplings into a ladder to fetch them while the
	/// defenders shoot; the raid is driven off, leaving some injured prisoners already in a tidy prison.
	///
	/// WHY A JOB GIVER BEFORE THE FIGHT: nothing walks a trapped raider out. RM_RaiderTrench.Eligible refuses a trapped pawn,
	/// so JobGiver_RM_CrossTrench never acts for it, and vanilla has no notion of a pit: down there it shoots if the shooting
	/// rule lets it, else its duty finds nothing and it idles until the raid leaves without it. Its friends fight on, because
	/// FightEnemies comes first in AssaultColony. JobGiver_RM_FetchFallen is inserted BEFORE it (and before the first fight
	/// node of the Breaching and Sapper duties: Patches/RaiderTrench), so ONE raider per raid (a claim with a lease,
	/// RescueLeaseTicks) lowers a ladder into the fallen's pocket while the rest keep shooting. The ladder comes through the
	/// crossing's own chain (RM_LadderParity.LadderSupplyJob: carried, taken, wood, a felled tree) and is set by the
	/// crossing's own job (RM_RaiderSetLadder) from the rim; once it stands the pocket is no longer a trap
	/// (RM_PocketGrid.TrappedIn: a usable ladder that leads free) and each fallen raider's own FetchFallen climbs it out.
	///
	/// Not this giver's: a siege (it shells), a downed raider (vanilla drops him from the raid), a creature that cannot use a
	/// ladder, anyone beneath an intact lid (PIT_COVER_FIX_OCCUPANT_STAYS_BELOW). The fetcher gives up when its duty is no
	/// longer an assault (the raid flees: the set-ladder job fails, the claim drops), and gives the pocket up when a ladder
	/// it set stands and frees nobody. JobGiver_RM_CrossTrench leaves a busy fetcher alone (Busy), and no raider takes the
	/// rescue ladder away (RM_LadderParity.TakeLadderJob: IsRescueLadder) while the claim stands.
	/// </summary>
	public static class RM_RaiderRescue
	{
		internal sealed class Claim
		{
			public Pawn rescuer;
			public int renewed;
			public IntVec3 ladder = IntVec3.Invalid;   // the slot of the last set-ladder job handed out
			public readonly HashSet<Pawn> fallen = new HashSet<Pawn>();
		}

		private static readonly Dictionary<Lord, Claim> claims = new Dictionary<Lord, Claim>();
		private static readonly HashSet<Lord> warned = new HashSet<Lord>();
		private static readonly Dictionary<Lord, int> givenUpUntil = new Dictionary<Lord, int>();
		private static readonly Dictionary<int, int> noSlotUntil = new Dictionary<int, int>();   // pawn id: looked, found nothing
		private static readonly Dictionary<Pawn, IntVec3> climbTo = new Dictionary<Pawn, IntVec3>();   // fallen -> wall top
		private static readonly HashSet<int> rescueJobs = new HashSet<int>();   // Job.loadID of the set-ladder jobs handed out
		private static readonly Dictionary<Lord, (int tick, List<Pawn> list)> trappedMemo = new Dictionary<Lord, (int, List<Pawn>)>();
		private const int RetryTicks = 600;
		private const int GiveUpTicks = 2500;
		private const int TrappedMemoTicks = 30;
		private const int MaxSlotTries = 8;

		/// <summary>Lords die with the save (called from RM_RaiderTrench.ClearMemos on Game.FinalizeInit).</summary>
		public static void ClearMemos()
		{
			claims.Clear();
			warned.Clear();
			givenUpUntil.Clear();
			noSlotUntil.Clear();
			climbTo.Clear();
			rescueJobs.Clear();
			trappedMemo.Clear();
		}

		/// <summary>The three assault duties the giver is inserted into; anything else (flee, exit, defend) is a give-up.</summary>
		public static bool AssaultDuty(Pawn p)
		{
			DutyDef d = p?.mindState?.duty?.def;
			return d != null && (d == DutyDefOf.AssaultColony || d == DutyDefOf.Breaching || d == DutyDefOf.Sapper);
		}

		private static bool Standing(Pawn m, Lord lord)
		{
			return m != null && m.Spawned && !m.Dead && !m.Downed && m.GetLord() == lord;
		}

		/// <summary>A raider of this raid the pit traps that a ladder would free (it can climb one; not under a lid).</summary>
		private static bool IsFallen(Pawn m, Lord lord)
		{
			return Standing(m, lord) && RM_LadderParity.ClimbEligible(m) && !Pits.RM_PitCoverBeneath.IsBeneath(m)
				&& RM_SuperdeepTrap.IsTrapped(m);
		}

		/// <summary>Still down in a pocket, trapped or not: a fallen raider not yet out.</summary>
		private static bool InPocket(Pawn m)
		{
			if (m == null || !m.Spawned || m.Dead)
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(m);
			RM_PocketGrid g = RM_PocketGrid.ForPawn(m.Map, m);
			return g.ComponentIsPocket(k, g.ComponentOf(k, m.Position));
		}

		private static List<Pawn> TrappedOf(Lord lord)
		{
			int now = Find.TickManager.TicksGame;
			if (trappedMemo.TryGetValue(lord, out var memo) && now - memo.tick < TrappedMemoTicks && now >= memo.tick)
			{
				return memo.list;
			}
			List<Pawn> list = new List<Pawn>();
			for (int i = 0; i < lord.ownedPawns.Count; i++)
			{
				if (IsFallen(lord.ownedPawns[i], lord))
				{
					list.Add(lord.ownedPawns[i]);
				}
			}
			trappedMemo[lord] = (now, list);
			return list;
		}

		private static bool Live(Lord lord, Claim c)
		{
			bool holderFit = Standing(c.rescuer, lord) && AssaultDuty(c.rescuer) && !RM_SuperdeepTrap.IsTrapped(c.rescuer);
			bool fallenLeft = false;
			foreach (Pawn m in c.fallen)
			{
				if (Standing(m, lord) && InPocket(m))
				{
					fallenLeft = true;
					break;
				}
			}
			return RM_RaiderTrenchMath.ClaimLive(true, c.renewed, Find.TickManager.TicksGame, RM_RaiderTrenchMath.RescueLeaseTicks,
				holderFit, fallenLeft);
		}

		/// <summary>This raid's live claim, or null (a dead one is dropped here).</summary>
		private static Claim LiveClaim(Lord lord)
		{
			if (lord == null || !claims.TryGetValue(lord, out Claim c))
			{
				return null;
			}
			if (Live(lord, c))
			{
				return c;
			}
			claims.Remove(lord);
			return null;
		}

		/// <summary>The fetcher of a live claim whose fallen are still trapped: JobGiver_RM_CrossTrench leaves it alone.</summary>
		public static bool Busy(Pawn p)
		{
			Lord lord = p?.GetLord();
			Claim c = lord == null || claims.Count == 0 ? null : LiveClaim(lord);
			if (c == null || c.rescuer != p)
			{
				return false;
			}
			foreach (Pawn m in c.fallen)
			{
				if (IsFallen(m, lord))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>A ladder a live fetch set (or is setting): no raider takes it away (RM_LadderParity.TakeLadderJob).</summary>
		public static bool IsRescueLadder(Thing ladder)
		{
			if (ladder == null || claims.Count == 0)
			{
				return false;
			}
			foreach (KeyValuePair<Lord, Claim> kv in claims)
			{
				Claim c = kv.Value;
				if (c.ladder == ladder.Position && c.rescuer != null && c.rescuer.Map == ladder.Map && Live(kv.Key, c))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The set-ladder job (JobDriver_RM_RaiderTrenchWork) of a fetch whose raid is no longer assaulting: fail it.</summary>
		public static bool GivenUp(Pawn p, Job job)
		{
			return job != null && rescueJobs.Count > 0 && rescueJobs.Contains(job.loadID) && !AssaultDuty(p);
		}

		/// <summary>JobGiver_RM_FetchFallen: the whole decision for one raider (RM_RaiderTrenchMath.FetchFallen), or null.</summary>
		public static Job TryFetch(Pawn p)
		{
			if (!RM_RaiderTrench.On || !RM_RaiderTrenchSettings.raiderLaddersEnabled || p?.Map == null
				|| RM_RaiderTrenchDefOf.RM_RaiderSetLadder == null || !RM_SuperdeepTrap.AnyHole(RM_SuperdeepTrap.EngineOf(p.Map)))
			{
				return null;
			}
			Lord lord = p.GetLord();
			if (lord == null || !AssaultDuty(p) || RM_RaiderTrench.IsSiege(p))
			{
				return null;
			}
			int now = Find.TickManager.TicksGame;
			Job climb = ClimbOutJob(p);
			if (climb != null)
			{
				return climb;   // FetchStep.ClimbOut
			}
			if (givenUpUntil.TryGetValue(lord, out int until) && now < until)
			{
				return null;
			}
			Claim claim = claims.Count == 0 ? null : LiveClaim(lord);
			if (claim != null && claim.rescuer != p)
			{
				return null;   // another raider is fetching them
			}
			bool fit = RM_RaiderTrench.Eligible(p, out int k) && RM_RaiderTrench.ToolUser(p);
			if (!fit)
			{
				return null;
			}
			List<Pawn> trapped = TrappedOf(lord);
			if (trapped.Count == 0)
			{
				return null;
			}
			Pawn target = NearestFallen(p, trapped, claim);
			if (target == null)
			{
				return null;
			}
			if (!IsFallen(target, lord))
			{
				trappedMemo.Remove(lord);   // the memo is up to TrappedMemoTicks old (a ladder just set): look again next think
				return null;
			}
			Map map = p.Map;
			// a ladder this fetch set stands and frees nobody (a pocket that leads into another sealed one): give it up
			if (claim != null && claim.ladder.IsValid && RM_LadderUtility.LadderAt(map, claim.ladder) != null
				&& claim.fallen.Contains(target))
			{
				claims.Remove(lord);
				givenUpUntil[lord] = now + GiveUpTicks;
				return null;
			}
			if (claim == null && noSlotUntil.TryGetValue(p.thingIDNumber, out int retry) && now < retry)
			{
				return null;
			}
			bool slot = TryFindSlot(p, k, target, out IntVec3 cell, out IntVec3 wall, out int drop, out HashSet<IntVec3> pocket);
			Job supply = null;
			bool canBuild = false;
			if (slot)
			{
				// owner's order (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED): carried, taken (never one in the pocket), wood, a felled tree
				supply = RM_LadderParity.LadderSupplyJob(p, pocket, out canBuild);
			}
			// the earlier inputs are settled by the early returns above (each returns where FetchFallen says None)
			switch (RM_RaiderTrenchMath.FetchFallen(true, true, false, false, fit, true, false, slot, supply != null, canBuild))
			{
				case RM_RaiderTrenchMath.FetchStep.Supply:
					Renew(lord, ref claim, p, target, now);
					return supply;
				case RM_RaiderTrenchMath.FetchStep.SetLadder:
				{
					Renew(lord, ref claim, p, target, now);
					Job job = JobMaker.MakeJob(RM_RaiderTrenchDefOf.RM_RaiderSetLadder, cell, wall);
					job.count = drop;
					claim.ladder = cell;
					rescueJobs.Add(job.loadID);
					foreach (Pawn m in claim.fallen)
					{
						climbTo[m] = wall;
					}
					return job;
				}
				default:
					if (claim != null)
					{
						claims.Remove(lord);   // no slot or no ladder to be had any more: let a better-placed raider try
					}
					noSlotUntil[p.thingIDNumber] = now + RetryTicks;
					return null;
			}
		}

		private static void Renew(Lord lord, ref Claim claim, Pawn p, Pawn target, int now)
		{
			if (claim == null)
			{
				claim = new Claim { rescuer = p };
				claims[lord] = claim;
				// everyone of this raid trapped in the target's pocket is fetched by the one ladder
				int k = RM_PocketGrid.ClimbLimitOf(target);
				RM_PocketGrid g = RM_PocketGrid.ForPawn(target.Map, target);
				int comp = g.ComponentOf(k, target.Position);
				foreach (Pawn m in TrappedOf(lord))
				{
					if (m == target || g.ComponentOf(k, m.Position) == comp)
					{
						claim.fallen.Add(m);
					}
				}
				Warn(p);
			}
			claim.renewed = now;
		}

		private static void Warn(Pawn p)
		{
			Lord lord = p.GetLord();
			if (lord == null || !warned.Add(lord))
			{
				return;
			}
			Messages.Message("RMFlow_RaidersFetchFallen".Translate(p.Faction.Name), new LookTargets(p), MessageTypeDefOf.ThreatSmall, false);
		}

		/// <summary>The fallen this raider answers: the claim's own first, else the nearest within RescueRadius.</summary>
		private static Pawn NearestFallen(Pawn p, List<Pawn> trapped, Claim claim)
		{
			Pawn best = null;
			int bestD = RM_RaiderTrenchMath.RescueRadius * RM_RaiderTrenchMath.RescueRadius + 1;
			for (int pass = 0; pass < 2 && best == null; pass++)
			{
				for (int i = 0; i < trapped.Count; i++)
				{
					Pawn m = trapped[i];
					if (pass == 0 && (claim == null || !claim.fallen.Contains(m)))
					{
						continue;
					}
					int d = m.Position.DistanceToSquared(p.Position);
					if (d < bestD)
					{
						bestD = d;
						best = m;
					}
				}
			}
			return best;
		}

		/// <summary>A square of the fallen's pocket beside a wall square on the fetcher's own ground, with a drop the portable
		/// ladder spans (RM_RaiderTrenchMath.RescueDrop), free, reservable and touchable from the rim; the nearest the fallen.</summary>
		private static bool TryFindSlot(Pawn p, int kr, Pawn fallen, out IntVec3 cell, out IntVec3 wall, out int drop,
			out HashSet<IntVec3> pocket)
		{
			cell = wall = IntVec3.Invalid;
			drop = -1;
			pocket = new HashSet<IntVec3>();
			Map map = p.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			int reach = def == null ? -1 : RM_LadderUtility.MaxLevelsOf(def);
			if (eng == null || reach < 0)
			{
				return false;   // portable ladders switched off
			}
			int kf = RM_PocketGrid.ClimbLimitOf(fallen);
			RM_PocketGrid gf = RM_PocketGrid.ForPawn(map, fallen);
			int comp = gf.ComponentOf(kf, fallen.Position);
			RM_PocketGrid gr = RM_PocketGrid.ForPawn(map, p);
			int own = gr.ComponentOf(kr, p.Position);
			List<int> cells = gf.CellsOf(kf, comp);
			var cand = new List<(int d, IntVec3 c, IntVec3 w)>();
			for (int i = 0; i < cells.Count; i++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(cells[i]);
				pocket.Add(c);
				if (!c.Standable(map) || Pits.RM_PitCoverUtility.IsCovered(map, c)
					|| RM_LadderUtility.LadderAt(map, c) != null || RM_PitRamp.RampAt(map, c) != null)
				{
					continue;
				}
				int dc = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
				for (int j = 0; j < 4; j++)
				{
					IntVec3 w = c + GenAdj.CardinalDirections[j];
					if (!w.InBounds(map) || gr.ComponentOf(kr, w) != own || !w.Standable(map)
						|| RM_RaiderTrenchMath.RescueDrop(dc, RM_SuperdeepTrap.StepDepthAt(map, eng, w), reach, false, true, true) < 0)
					{
						continue;
					}
					cand.Add((c.DistanceToSquared(fallen.Position), c, w));
				}
			}
			cand.Sort((a, b) => a.d.CompareTo(b.d));
			for (int i = 0; i < cand.Count && i < MaxSlotTries; i++)
			{
				IntVec3 c = cand[i].c;
				IntVec3 w = cand[i].w;
				int dd = RM_RaiderTrenchMath.RescueDrop(RM_SuperdeepTrap.StepDepthAt(map, eng, c), RM_SuperdeepTrap.StepDepthAt(map, eng, w),
					reach, RM_LadderUtility.LadderAt(map, c) != null || RM_PitRamp.RampAt(map, c) != null, p.CanReserve(c),
					p.CanReach(c, PathEndMode.Touch, Danger.Deadly));
				if (dd > 0)
				{
					cell = c;
					wall = w;
					drop = dd;
					return true;
				}
			}
			return false;
		}

		/// <summary>FetchStep.ClimbOut: a fallen raider of a fetch, still in its pocket, no longer trapped (the ladder stands),
		/// walks up to the wall top the ladder hangs on.</summary>
		private static Job ClimbOutJob(Pawn p)
		{
			if (climbTo.Count == 0 || !climbTo.TryGetValue(p, out IntVec3 w))
			{
				return null;
			}
			if (!InPocket(p) || p.Map == null || !w.InBounds(p.Map))
			{
				climbTo.Remove(p);   // out (or gone): done
				Prune();
				return null;
			}
			if (RM_SuperdeepTrap.IsTrapped(p) || !p.CanReach(w, PathEndMode.OnCell, Danger.Deadly))
			{
				return null;   // the ladder is not up yet (or was taken): wait for the fetcher
			}
			Job job = JobMaker.MakeJob(JobDefOf.Goto, w, 600, true);
			job.locomotionUrgency = LocomotionUrgency.Jog;
			job.collideWithPawns = true;
			return job;
		}

		private static void Prune()
		{
			if (climbTo.Count < 64)
			{
				return;
			}
			List<Pawn> gone = new List<Pawn>();
			foreach (Pawn m in climbTo.Keys)
			{
				if (m == null || !m.Spawned || m.Dead)
				{
					gone.Add(m);
				}
			}
			foreach (Pawn m in gone)
			{
				climbTo.Remove(m);
			}
		}

		/// <summary>Bridge/debug read (jawa/static_call): this raid's fetch: who, the fallen, the slot, the lease age.</summary>
		public static string ProofFetch(Pawn p)
		{
			Lord lord = p?.GetLord();
			if (lord == null)
			{
				return "no lord";
			}
			StringBuilder sb = new StringBuilder();
			sb.Append("assault=").Append(AssaultDuty(p)).Append(" trapped=").Append(TrappedOf(lord).Count);
			if (claims.TryGetValue(lord, out Claim c))
			{
				sb.Append(" claim=").Append(c.rescuer?.LabelShort).Append(" live=").Append(Live(lord, c))
					.Append(" age=").Append(Find.TickManager.TicksGame - c.renewed).Append(" ladder=").Append(c.ladder)
					.Append(" fallen=").Append(c.fallen.Count);
			}
			else
			{
				sb.Append(" claim=none");
			}
			sb.Append(" climbTo=").Append(climbTo.TryGetValue(p, out IntVec3 w) ? w.ToString() : "-");
			return sb.ToString();
		}
	}

	/// <summary>RAIDERS_FETCH_THEIR_FALLEN: inserted before the first fight node of the AssaultColony, Breaching and Sapper
	/// duties (Patches/RaiderTrench). Null unless this raider climbs out of a pocket a rescue ladder opened, or it is the one
	/// raider of its raid fetching the fallen.</summary>
	public class JobGiver_RM_FetchFallen : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			return RM_RaiderRescue.TryFetch(pawn);
		}
	}
}
