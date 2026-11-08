using System.Collections.Generic;
using System.Text;
using HarmonyLib;
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
	/// crossing's own chain (RM_LadderParity.LadderSupplyJob: carried, taken, wood, a felled tree) and is set from the rim
	/// by the crossing's own driver under its own def (RM_RaiderRescueLadder, so the saved job alone says it is a rescue);
	/// once it stands the pocket is no longer a trap (RM_PocketGrid.TrappedIn: a usable ladder that leads free) and each
	/// fallen raider's own FetchFallen climbs it out. The claim's slot is written by the job that actually runs (GivenUp),
	/// never by a think-tree re-run under fire. While the rescue is under way the assault's colony-damage exit waits, at
	/// most RM_RaiderTrenchMath.RescueHoldCapTicks (RM_Patch_ColonyDamage_RescueHold). A ladder set into a pocket that holds
	/// prisoners of the colony stays (owner card 2026-11-07) and says so once (NoteRescueLadderSet).
	///
	/// Not this giver's: a siege (it shells), a downed raider (vanilla drops him from the raid), a creature that cannot use a
	/// ladder, anyone beneath an intact lid (PIT_COVER_FIX_OCCUPANT_STAYS_BELOW). The fetcher gives up when its duty is no
	/// longer an assault (the raid flees: the set-ladder job fails, the claim drops), and gives the pocket up when a ladder
	/// it set stands and frees nobody. JobGiver_RM_CrossTrench leaves a busy fetcher alone (Busy), and no raider takes the
	/// rescue ladder away (RM_LadderParity.TakeLadderJob: IsRescueLadder) while the claim stands, nor any ladder standing in
	/// a pocket that still holds a standing raider of its own raid (OwnRaidBelow).
	/// </summary>
	public static class RM_RaiderRescue
	{
		internal sealed class Claim
		{
			public Pawn rescuer;
			public int renewed;
			public IntVec3 ladder = IntVec3.Invalid;   // the slot of the rescue ladder job that actually runs (GivenUp writes it)
			public IntVec3 wall = IntVec3.Invalid;     // the wall top that job's ladder hangs on
			public readonly HashSet<Pawn> fallen = new HashSet<Pawn>();
		}

		private static readonly Dictionary<Lord, Claim> claims = new Dictionary<Lord, Claim>();
		private static readonly HashSet<Lord> warned = new HashSet<Lord>();
		private static readonly Dictionary<Lord, int> givenUpUntil = new Dictionary<Lord, int>();
		private static readonly Dictionary<int, int> noSlotUntil = new Dictionary<int, int>();   // pawn id: looked, found nothing
		// fallen -> the wall top the ladder hangs on, and the ladder's foot (a square of the pocket he is fetched from)
		private static readonly Dictionary<Pawn, (IntVec3 wall, IntVec3 slot)> climbTo = new Dictionary<Pawn, (IntVec3, IntVec3)>();
		private static readonly Dictionary<Lord, (int tick, List<Pawn> list)> trappedMemo = new Dictionary<Lord, (int, List<Pawn>)>();
		// the tick this raid's colony-damage exit was first held for a rescue (RM_Patch_ColonyDamage_RescueHold)
		private static readonly Dictionary<Lord, int> firstHold = new Dictionary<Lord, int>();
		private static int lastPrune = -1;
		private const int RetryTicks = 600;
		private const int GiveUpTicks = 2500;
		private const int TrappedMemoTicks = 30;
		private const int MaxSlotTries = 8;
		private const int PruneTicks = 2500;

		/// <summary>Lords die with the save (called from RM_RaiderTrench.ClearMemos on Game.FinalizeInit).</summary>
		public static void ClearMemos()
		{
			claims.Clear();
			warned.Clear();
			givenUpUntil.Clear();
			noSlotUntil.Clear();
			climbTo.Clear();
			trappedMemo.Clear();
			firstHold.Clear();
			lastPrune = -1;
		}

		/// <summary>The rescue state is static, never saved: what a dead raid (its lord gone, its map gone) or a gone pawn left
		/// behind is dropped every PruneTicks, so no Lord or Pawn keeps a dead map in memory. A save carries only the rescue
		/// job itself (its own def, RM_RaiderRescueLadder): GivenUp re-makes the claim from it on the first tick after a load.</summary>
		private static void PruneDead(int now)
		{
			if (lastPrune >= 0 && now >= lastPrune && now - lastPrune < PruneTicks)
			{
				return;
			}
			lastPrune = now;
			var lords = new HashSet<Lord>(claims.Keys);
			lords.UnionWith(warned);
			lords.UnionWith(givenUpUntil.Keys);
			lords.UnionWith(trappedMemo.Keys);
			lords.UnionWith(firstHold.Keys);
			foreach (Lord l in lords)
			{
				if (LordGone(l))
				{
					claims.Remove(l);
					warned.Remove(l);
					givenUpUntil.Remove(l);
					trappedMemo.Remove(l);
					firstHold.Remove(l);
				}
			}
			var pawns = new List<Pawn>();
			foreach (Pawn m in climbTo.Keys)
			{
				if (m == null || m.Destroyed || m.Dead || !m.Spawned)
				{
					pawns.Add(m);
				}
			}
			foreach (Pawn m in pawns)
			{
				climbTo.Remove(m);
			}
			var ids = new List<int>();
			foreach (KeyValuePair<int, int> kv in noSlotUntil)
			{
				if (kv.Value <= now)
				{
					ids.Add(kv.Key);
				}
			}
			foreach (int id in ids)
			{
				noSlotUntil.Remove(id);
			}
		}

		private static bool LordGone(Lord l)
		{
			Map map = l?.lordManager?.map;
			return map == null || Find.Maps == null || !Find.Maps.Contains(map) || !map.lordManager.lords.Contains(l);
		}

		/// <summary>This raider stands in a pocket (its own climb band) that holds <paramref name="cell"/>.</summary>
		private static bool SamePocket(Pawn m, IntVec3 cell)
		{
			if (m == null || !m.Spawned || m.Map == null || !cell.InBounds(m.Map))
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(m);
			RM_PocketGrid g = RM_PocketGrid.ForPawn(m.Map, m);
			int comp = g.ComponentOf(k, m.Position);
			return comp == g.ComponentOf(k, cell) && g.ComponentIsPocket(k, comp);
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

		/// <summary>The rescue ladder job (RM_RaiderRescueLadder, JobDriver_RM_RaiderTrenchWork), asked at each toil start and
		/// every tick: fail it when its raid no longer assaults, another raider holds the fetch, or its slot's pocket holds none
		/// of the raid's fallen. Else the raid's claim is this job's: the claim's slot, wall and fallen are written HERE, from
		/// the job that actually runs (review F1: a think-tree re-run under fire only hands out a duplicate vanilla discards,
		/// so nothing re-aims the claim at a slot no ladder is going to), and the lease is renewed while it runs. A job loaded
		/// from a save makes its claim again here (F8).</summary>
		public static bool GivenUp(Pawn p, Job job)
		{
			JobDef def = RM_RaiderTrenchDefOf.RM_RaiderRescueLadder;
			if (job == null || def == null || job.def != def)
			{
				return false;
			}
			Lord lord = p?.GetLord();
			if (lord == null || p.Map == null || !AssaultDuty(p))
			{
				return true;
			}
			int now = Find.TickManager.TicksGame;
			if (claims.TryGetValue(lord, out Claim c) && c.rescuer == p && c.ladder == job.targetA.Cell && c.wall == job.targetB.Cell)
			{
				c.renewed = now;
				return false;
			}
			return !Commit(lord, p, job.targetA.Cell, job.targetB.Cell, now);
		}

		/// <summary>The running rescue job takes the raid's claim: everyone of the raid trapped in the slot's pocket is fetched
		/// by this ladder (review F5: a claim that moved on to a second pocket tracks that pocket's fallen). False: not this
		/// raider's to do (another holds a live claim, or the slot's pocket holds none of the fallen).</summary>
		private static bool Commit(Lord lord, Pawn p, IntVec3 slot, IntVec3 wall, int now)
		{
			Claim live = claims.Count == 0 ? null : LiveClaim(lord);
			if (live != null && live.rescuer != p)
			{
				return false;   // another raider is fetching them
			}
			var fallen = new List<Pawn>();
			foreach (Pawn m in TrappedOf(lord))
			{
				if (SamePocket(m, slot))
				{
					fallen.Add(m);
				}
			}
			if (fallen.Count == 0)
			{
				claims.Remove(lord);
				noSlotUntil[p.thingIDNumber] = now + RetryTicks;   // not handed the same job again at once (the 10-jobs loop)
				return false;
			}
			Claim c = live ?? new Claim { rescuer = p };
			c.fallen.Clear();
			c.fallen.UnionWith(fallen);
			c.ladder = slot;
			c.wall = wall;
			c.renewed = now;
			claims[lord] = c;
			foreach (Pawn m in fallen)
			{
				climbTo[m] = (wall, slot);
			}
			Warn(p);
			return true;
		}

		/// <summary>RAIDERS_FETCH_THEIR_FALLEN (review F7): a ladder standing in a pocket where a standing raider of the taker's
		/// own raid still is: taking it strands them (they become fallen to fetch). It also keeps a rescue ladder set before a
		/// save, whose claim the load forgot, while the fallen climb it (F8). RM_LadderParity.TakeLadderJob skips it.</summary>
		public static bool OwnRaidBelow(Pawn taker, Thing ladder)
		{
			Lord lord = taker?.GetLord();
			if (lord == null || ladder == null || !ladder.Spawned)
			{
				return false;
			}
			for (int i = 0; i < lord.ownedPawns.Count; i++)
			{
				Pawn m = lord.ownedPawns[i];
				if (m != taker && Standing(m, lord) && m.Map == ladder.Map && SamePocket(m, ladder.Position))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Review B (owner card 2026-11-07: "keep the rescue ladder even when the hole also holds colony prisoners, but
		/// send ONE message"): the done step of a rescue ladder job (JobDriver_RM_RaiderTrenchWork) that set its ladder into a
		/// pocket holding prisoners of the colony. One message per ladder set (this runs once, when it is spawned).</summary>
		public static void NoteRescueLadderSet(Thing ladder)
		{
			Map map = ladder?.Map;
			if (map == null || !ladder.Spawned)
			{
				return;
			}
			List<Pawn> prisoners = map.mapPawns.PrisonersOfColonySpawned;
			for (int i = 0; i < prisoners.Count; i++)
			{
				if (SamePocket(prisoners[i], ladder.Position))
				{
					Messages.Message("RMFlow_RescueLadderIntoPrison".Translate(), new LookTargets(ladder), MessageTypeDefOf.ThreatSmall, false);
					return;
				}
			}
		}

		/// <summary>The raid has a rescue under way: a live claim (its holder fit, a fallen still down, inside the lease), or a
		/// fallen of this raid walking out up the ladder (ClimbOutJob's Goto).</summary>
		public static bool RescueActive(Lord lord)
		{
			if (lord == null)
			{
				return false;
			}
			if (claims.Count > 0 && LiveClaim(lord) != null)
			{
				return true;
			}
			// STORY_REPLAY_S6 (pass 5): the wood comes first, out of sight, and no claim is made until the ladder job runs, so the
			// raid's damage exit fired while its rescuer was still felling the tree and the rescue never happened. A raider of
			// this raid fetching ladder wood or a ladder while one of it is still trapped is a rescue under way too.
			if (TrappedOf(lord).Count > 0)
			{
				for (int i = 0; i < lord.ownedPawns.Count; i++)
				{
					Pawn m = lord.ownedPawns[i];
					JobDef jd = m.CurJob?.def;
					if (jd != null && (jd == RM_LadderParityDefOf.RM_RaiderChopForLadder || jd == RM_LadderParityDefOf.RM_RaiderTakeLadder)
						&& Standing(m, lord) && !RM_SuperdeepTrap.IsTrapped(m))
					{
						return true;
					}
				}
			}
			foreach (KeyValuePair<Pawn, (IntVec3 wall, IntVec3 slot)> kv in climbTo)
			{
				Pawn m = kv.Key;
				if (Standing(m, lord) && m.CurJob != null && m.CurJob.def == JobDefOf.Goto && m.CurJob.targetA.Cell == kv.Value.wall
					&& InPocket(m))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Request C: the assault's colony-damage exit (Trigger_FractionColonyDamageTaken) would fire now; hold it while
		/// this raid's rescue is under way, at most RM_RaiderTrenchMath.RescueHoldCapTicks from the first hold.</summary>
		public static bool HoldsDamageExit(Lord lord)
		{
			if (!(lord?.LordJob is LordJob_AssaultColony))
			{
				return false;
			}
			int now = Find.TickManager.TicksGame;
			bool had = firstHold.TryGetValue(lord, out int first);
			bool hold = RM_RaiderTrenchMath.HoldColonyDamageExit(RescueActive(lord), had ? first : -1, now,
				RM_RaiderTrenchMath.RescueHoldCapTicks);
			if (hold && (!had || now < first))
			{
				firstHold[lord] = now;
			}
			return hold;
		}

		/// <summary>JobGiver_RM_FetchFallen: the whole decision for one raider (RM_RaiderTrenchMath.FetchFallen), or null.</summary>
		public static Job TryFetch(Pawn p)
		{
			if (!RM_RaiderTrench.On || !RM_RaiderTrenchSettings.raiderLaddersEnabled || p?.Map == null
				|| RM_RaiderTrenchDefOf.RM_RaiderRescueLadder == null || !RM_SuperdeepTrap.AnyHole(RM_SuperdeepTrap.EngineOf(p.Map)))
			{
				return null;
			}
			Lord lord = p.GetLord();
			if (lord == null || !AssaultDuty(p) || RM_RaiderTrench.IsSiege(p))
			{
				return null;
			}
			int now = Find.TickManager.TicksGame;
			PruneDead(now);
			Job cur = p.CurJob;
			if (cur != null && cur.def == RM_RaiderTrenchDefOf.RM_RaiderRescueLadder)
			{
				// review F1: a think-tree re-run while the ladder is being set (being shot: checkOverrideOnDamage). The same job
				// again, which vanilla discards (Pawn_JobTracker.ShouldStartJobFromThinkTree: same def, same giver), so the fight
				// node below does not interrupt it and nothing here re-aims the claim (GivenUp keeps it the running job's)
				Job same = JobMaker.MakeJob(cur.def, cur.targetA, cur.targetB);
				same.count = cur.count;
				return same;
			}
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
				&& SamePocket(target, claim.ladder))
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
					// the claim's slot, wall and fallen are the job's once it runs (GivenUp -> Commit), not written here
					Renew(lord, ref claim, p, target, now);
					Job job = JobMaker.MakeJob(RM_RaiderTrenchDefOf.RM_RaiderRescueLadder, cell, wall);
					job.count = drop;
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
				Warn(p);
			}
			if (!claim.fallen.Contains(target))
			{
				// everyone of this raid trapped in the target's pocket is fetched by the one ladder (review F5: also when a
				// standing claim moves on to a second pocket; Commit narrows it to the slot's pocket once the ladder job runs)
				foreach (Pawn m in TrappedOf(lord))
				{
					if (m == target || SamePocket(m, target.Position))
					{
						claim.fallen.Add(m);
					}
				}
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
			if (climbTo.Count == 0 || !climbTo.TryGetValue(p, out (IntVec3 wall, IntVec3 slot) to))
			{
				return null;
			}
			IntVec3 w = to.wall;
			// review F6: done when out, on the wall top, or out of the pocket he was fetched from (the wall top may itself lie in
			// a pocket for his climb band: a Goto there again would loop until vanilla's 10-jobs error)
			if (p.Map == null || !w.InBounds(p.Map) || !to.slot.InBounds(p.Map)
				|| RM_RaiderTrenchMath.ClimbOutDone(InPocket(p), p.Position == w, SamePocket(p, to.slot)))
			{
				climbTo.Remove(p);   // out (or gone): done
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
					.Append(" wall=").Append(c.wall).Append(" fallen=").Append(c.fallen.Count);
			}
			else
			{
				sb.Append(" claim=none");
			}
			sb.Append(" climbTo=").Append(climbTo.TryGetValue(p, out (IntVec3 wall, IntVec3 slot) w) ? w.wall + "@" + w.slot : "-");
			sb.Append(" hold=").Append(firstHold.TryGetValue(lord, out int h) ? (Find.TickManager.TicksGame - h).ToString() : "-");
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

	/// <summary>Request C (RAIDERS_FETCH_THEIR_FALLEN): vanilla's AssaultColony leaves once the colony has taken its share of
	/// damage (Trigger_FractionColonyDamageTaken: more than max(initialColonyHealthTotal x 0.25-0.35, 900) since the assault
	/// began). While this raid's rescue is under way (RM_RaiderRescue.RescueActive) that exit waits, at most
	/// RM_RaiderTrenchMath.RescueHoldCapTicks from the first time it would have fired. A postfix that acts only when the trigger
	/// says yes, so the cap counts from the moment the raid would have left. Every other exit (the time-out, the fraction of
	/// pawns lost, the slave rebellion's use of this trigger) is untouched: only an AssaultColony lord is held.</summary>
	[HarmonyPatch(typeof(Trigger_FractionColonyDamageTaken), nameof(Trigger_FractionColonyDamageTaken.ActivateOn))]
	[RimMandrake.Shared.PatchFeature("Raiders fetch their fallen (the raid waits for the rescue)", typeof(RimMandrake.FlowWorks.RM_RaiderTrenchSettings), "raiderRescueHoldsRaid")]
	public static class RM_Patch_ColonyDamage_RescueHold
	{
		[HarmonyPostfix]
		public static void Postfix(Lord lord, ref bool __result)
		{
			if (!__result || !RM_RaiderTrenchSettings.raiderRescueHoldsRaid || !RM_RaiderTrench.On || lord == null)
			{
				return;
			}
			if (RM_RaiderRescue.HoldsDamageExit(lord))
			{
				__result = false;
			}
		}
	}
}
