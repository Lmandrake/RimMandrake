using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP — the Verse half (rules: RM_RaiderTrenchMath). Owner 2026-10-18 (card Q7):
	/// <i>"Go around, and breach if no way"</i>; <i>"(4) plus some may have jump packs to cross. Ladders make sense for shallower
	/// pits (they could start building them in preparation). Siege raids still work fine with mortars."</i>
	///
	/// WHY A JOB GIVER AT THE END OF THE DUTY: vanilla AssaultColony (decompiled 1.6) runs FightEnemies, the trash givers,
	/// GotoNearestHostile (needs CanReach) and last JobGiver_AISapper(canMineNonMineables=false), which returns null when even
	/// TraverseMode.PassAllDestroyableThings reaches nothing. A sheer trench is no destroyable thing: it is a missing edge in
	/// the cliff masks and a separate pocket-grid component (RM_SuperdeepTrap.RelativeVeto), so the raid stalls (live P2, day 3:
	/// STALL_FAR). JobGiver_RM_CrossTrench is appended after it (Patches/RaiderTrench), and after JobGiver_AIBreaching and
	/// JobGiver_AISapper in the Breaching and Sapper duties; it acts only when the nearest colonist (else colony building) is
	/// on a different climb-band component AND unreachable, so going around stays vanilla's and sieges (LordJob_Siege) never
	/// reach it.
	///
	/// The ladders a raider sets are portable ladders of ITS faction. RM_LadderRules.LadderLetsOut lets a pawn climb a ladder
	/// of its own faction (the prison-door rule still bars every other hostile), and RM_PitPathing's closed-ladder grid
	/// leaves those cells open to that faction. Shoot the ladder (40 HP) and whoever is down there is in a pit.
	///
	/// TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP: once the ladders stand, bank to bank is one reachability hop for the raid
	/// (RM_SuperdeepTrap.RelativeVeto joins components through ladders this pawn may use: its own faction's), so TryCross
	/// sees the target reachable and vanilla's givers walk it down, across and up.
	/// </summary>
	public static class RM_RaiderTrench
	{
		public const int MaxLine = 160;
		public const int MaxTrenchWidth = 30;
		public const int JumpLookSquares = 4;
		public const int PlanCacheTicks = 2500;
		/// <summary>A map with fewer dug or hollow squares than this gets no jump packs handed out.</summary>
		public const int MinClimbCellsForJumpPacks = 20;

		public static bool On => RM_RaiderTrenchSettings.raiderTrenchEnabled && RimMandrakeFlowWorksSettings.superdeepCaptureEnabled
			&& RM_PocketGrid.Relative && RM_SuperdeepTrap.RuleOn;

		internal sealed class Plan
		{
			public List<IntVec3> cells;   // 0 = the lip on the raider's side; last = the first square of the far side
			public int[] depths;
		}

		private static readonly Dictionary<Lord, (int tick, IntVec3 lip)> lordLips = new Dictionary<Lord, (int, IntVec3)>();
		private static readonly HashSet<Lord> warned = new HashSet<Lord>();
		private static bool dryRun;   // ProofDecision's probe: decide, but remember and warn about nothing

		/// <summary>Lords die with the save: drop every per-lord memo when a game loads (Game.FinalizeInit).</summary>
		public static void ClearMemos()
		{
			lordLips.Clear();
			warned.Clear();
			workEnds.Clear();
			dryRun = false;
		}

		// CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (live 2026-10-22, 4 m ring): lip raiders sat in a vanilla Wait job for 9,000 ticks
		// while ProofDecision said RM_RaiderFillTrench. A Wait no giver of ours or the duty's makes is vanilla's error-recover job
		// (Pawn_JobTracker: "started 10 jobs in one tick" -> JobUtility.TryStartErrorRecoverJob -> Wait 150): a giver whose job
		// ends the tick it starts is re-asked ten times. Every end of a trench-work job is counted here so ProofJobTrace says.
		private static readonly Dictionary<int, (int tick, JobCondition cond, int toil, int n, int sameTick)> workEnds =
			new Dictionary<int, (int, JobCondition, int, int, int)>();

		internal static void NoteWorkEnd(Pawn p, Job job, JobCondition cond, int toil)
		{
			if (p == null)
			{
				return;
			}
			if (workEnds.Count > 256)
			{
				workEnds.Clear();
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			workEnds.TryGetValue(p.thingIDNumber, out (int tick, JobCondition cond, int toil, int n, int sameTick) e);
			bool instant = job != null && job.startTick == now;
			workEnds[p.thingIDNumber] = (now, cond, toil, e.n + 1, e.sameTick + (instant ? 1 : 0));
		}

		/// <summary>Bridge/debug read (jawa/static_call): the raider's duty, lord toil, current job and who gave it, how its
		/// trench-work jobs ended, and -- for the job TryCross would give now -- the reach checks the job's first toil meets
		/// (the pawn's own CanReach the giver used, vanilla StartPath's PAWNLESS CanReach answered for this walker, the immediate
		/// touch the work toil fails on, and the reservation).</summary>
		public static string ProofJobTrace(Pawn p)
		{
			if (p == null || !p.Spawned)
			{
				return "no pawn";
			}
			var sb = new System.Text.StringBuilder();
			Job cur = p.CurJob;
			sb.Append("duty=").Append(p.mindState?.duty?.def?.defName ?? "none")
			  .Append(" toil=").Append(p.GetLord()?.CurLordToil?.GetType().Name ?? "none")
			  .Append(" job=").Append(cur?.def?.defName ?? "none")
			  .Append(" giver=").Append(cur?.jobGiver?.GetType().Name ?? "none")
			  .Append(" started=").Append(cur?.startTick ?? -1)
			  .Append(" exp=").Append(cur?.expiryInterval ?? -1)
			  .Append(" enemy=").Append(p.mindState?.enemyTarget?.ToString() ?? "none");
			if (workEnds.TryGetValue(p.thingIDNumber, out (int tick, JobCondition cond, int toil, int n, int sameTick) e))
			{
				sb.Append(" | workEnds n=").Append(e.n).Append(" sameTick=").Append(e.sameTick).Append(" last=").Append(e.cond)
				  .Append("@toil").Append(e.toil).Append(" t=").Append(e.tick);
			}
			else
			{
				sb.Append(" | workEnds n=0");
			}
			Job j;
			dryRun = true;
			try
			{
				j = TryCross(p);
			}
			finally
			{
				dryRun = false;
			}
			sb.Append(" | next=").Append(j == null ? "None" : j.def.defName + " " + j.targetA);
			if (j != null && j.targetA.IsValid && !j.targetA.HasThing)
			{
				IntVec3 c = j.targetA.Cell;
				Map map = p.Map;
				bool own = p.CanReach(c, PathEndMode.Touch, Danger.Deadly);
				bool pather = RM_Patch_PathFollower_ReachWalker.As(p,
					() => map.reachability.CanReach(p.Position, c, PathEndMode.Touch, TraverseParms.For(TraverseMode.PassDoors)));
				bool immediate = p.CanReachImmediate(c, PathEndMode.Touch);
				sb.Append(" reachOwn=").Append(own).Append(" reachPather=").Append(pather).Append(" immediate=").Append(immediate)
				  .Append(" reserve=").Append(p.CanReserve(c));
			}
			return sb.ToString();
		}

		public static bool IsSiege(Pawn p)
		{
			return p.GetLord()?.LordJob is LordJob_Siege;
		}

		/// <summary>A hostile raider of a lord that the trench is this pawn's problem for: spawned, standing, not a flyer, not
		/// trapped (a pit trap stays a trap), not climbing every wall already (climbing gear: band 0).</summary>
		public static bool Eligible(Pawn p, out int k)
		{
			k = 0;
			if (p == null || !p.Spawned || p.Downed || p.Dead || p.Faction == null || p.Faction == Faction.OfPlayer
				|| Faction.OfPlayer == null || !p.Faction.HostileTo(Faction.OfPlayer) || p.GetLord() == null)
			{
				return false;
			}
			if (RM_PocketGrid.FreePitTraveller(p))
			{
				return false;
			}
			k = RM_PocketGrid.ClimbLimitOf(p);
			if (RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0)
			{
				return false;
			}
			return !RM_SuperdeepTrap.IsTrapped(p);
		}

		public static bool ToolUser(Pawn p)
		{
			return p.RaceProps != null && p.RaceProps.Humanlike && p.RaceProps.ToolUser;
		}

		/// <summary>The nearest free colonist, else the nearest colony building: what the raid is trying to get at.</summary>
		public static Thing TargetFor(Pawn p)
		{
			Map map = p.Map;
			Thing best = null;
			int bestD = int.MaxValue;
			foreach (Pawn c in map.mapPawns.FreeColonistsSpawned)
			{
				int d = c.Position.DistanceToSquared(p.Position);
				if (d < bestD)
				{
					bestD = d;
					best = c;
				}
			}
			if (best != null)
			{
				return best;
			}
			foreach (Building b in map.listerBuildings.allBuildingsColonist)
			{
				int d = b.Position.DistanceToSquared(p.Position);
				if (d < bestD)
				{
					bestD = d;
					best = b;
				}
			}
			return best;
		}

		/// <summary>The crossing line from <paramref name="origin"/> toward the target: the last square of the raider's own
		/// component, every square between, and the first square of the target's. False: no trench between them, a crossing
		/// wider than MaxTrenchWidth, something solid on the line, or the lip not reachable.</summary>
		internal static bool TryPlan(Pawn p, int k, Thing target, IntVec3 origin, out Plan plan)
		{
			plan = null;
			Map map = p.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || target == null || !target.Spawned)
			{
				return false;
			}
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int cs = g.ComponentOf(k, p.Position);
			int ct = g.ComponentOf(k, target.Position);
			if (cs < 0 || ct < 0 || cs == ct || g.ComponentOf(k, origin) != cs)
			{
				return false;
			}
			List<(int x, int z)> line = RM_RaiderTrenchMath.CardinalLine(origin.x, origin.z, target.Position.x, target.Position.z, MaxLine);
			int exit = -1;
			for (int i = 0; i < line.Count; i++)
			{
				if (g.ComponentOf(k, new IntVec3(line[i].x, 0, line[i].z)) != cs)
				{
					exit = i;
					break;
				}
			}
			if (exit <= 0)
			{
				return false;
			}
			int far = -1;
			for (int i = exit; i < line.Count && i - exit <= MaxTrenchWidth; i++)
			{
				if (g.ComponentOf(k, new IntVec3(line[i].x, 0, line[i].z)) == ct)
				{
					far = i;
					break;
				}
			}
			if (far < 0)
			{
				return false;
			}
			var cells = new List<IntVec3>();
			var depths = new int[far - exit + 2];
			for (int i = exit - 1; i <= far; i++)
			{
				var c = new IntVec3(line[i].x, 0, line[i].z);
				if (!c.InBounds(map) || !c.Walkable(map))
				{
					return false;
				}
				cells.Add(c);
				depths[i - exit + 1] = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
			}
			if (cells[0] != p.Position && !p.CanReach(cells[0], PathEndMode.OnCell, Danger.Deadly))
			{
				return false;
			}
			plan = new Plan { cells = cells, depths = depths };
			return true;
		}

		/// <summary>One crossing point per raid: the first raider's lip, while it is on a later raider's side.</summary>
		internal static IntVec3 OriginFor(Pawn p, int k)
		{
			Lord lord = p.GetLord();
			int now = Find.TickManager?.TicksGame ?? 0;
			if (lord != null && lordLips.TryGetValue(lord, out (int tick, IntVec3 lip) e) && now - e.tick < PlanCacheTicks
				&& e.lip.InBounds(p.Map) && RM_PocketGrid.For(p.Map).ComponentOf(k, e.lip) == RM_PocketGrid.For(p.Map).ComponentOf(k, p.Position))
			{
				return e.lip;
			}
			return p.Position;
		}

		internal static void RememberLip(Pawn p, IntVec3 lip)
		{
			Lord lord = p.GetLord();
			if (dryRun || lord == null)
			{
				return;
			}
			if (lordLips.Count > 64)
			{
				lordLips.Clear();
				warned.Clear();
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (!lordLips.TryGetValue(lord, out (int tick, IntVec3 lip) e) || now - e.tick >= PlanCacheTicks)
			{
				lordLips[lord] = (now, lip);
			}
		}

		// ── jumps ─────────────────────────────────────────────────────────

		/// <summary>A jump this pawn can make now: a worn jump pack with a charge (Verb_Jump), or a leaping ability that can be
		/// cast (Verb_CastAbilityJump: longjump legs and kin). Range in squares.</summary>
		public static bool TryGetJump(Pawn p, out Verb verb, out Ability ability, out float range)
		{
			verb = null;
			ability = null;
			range = 0f;
			List<Apparel> worn = p.apparel?.WornApparel;
			if (worn != null)
			{
				for (int i = 0; i < worn.Count; i++)
				{
					CompApparelVerbOwner owner = worn[i].GetComp<CompApparelVerbOwner>();
					if (owner == null || !owner.CanBeUsed(out string _))
					{
						continue;
					}
					foreach (Verb v in owner.AllVerbs)
					{
						if (v is Verb_Jump && v.Available())
						{
							float r = v.EffectiveRange;
							if (r > 0f)
							{
								verb = v;
								range = r;
								return true;
							}
						}
					}
				}
			}
			List<Ability> abilities = p.abilities?.AllAbilitiesForReading;
			if (abilities != null)
			{
				for (int i = 0; i < abilities.Count; i++)
				{
					Ability a = abilities[i];
					if (a.verb is Verb_CastAbilityJump && a.CanCast.Accepted)
					{
						float r = a.verb.EffectiveRange;
						if (r > 0f)
						{
							ability = a;
							range = r;
							return true;
						}
					}
				}
			}
			return false;
		}

		private static bool ValidLanding(Pawn p, IntVec3 c)
		{
			Map map = p.Map;
			if (!c.InBounds(map) || !c.Standable(map) || !c.WalkableBy(map, p) || c.GetFirstPawn(map) != null)
			{
				return false;
			}
			Building edifice = c.GetEdifice(map);
			return !(edifice is Building_Door door && !door.Open);
		}

		private static Job JumpJob(Pawn p, Plan plan, int k)
		{
			if (!RM_RaiderTrenchSettings.raiderJumpsEnabled || !TryGetJump(p, out Verb verb, out Ability ability, out float range))
			{
				return null;
			}
			Map map = p.Map;
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int ct = g.ComponentOf(k, plan.cells[plan.cells.Count - 1]);
			// The far side continues past the plan's last square along the same direction; look a few squares on.
			IntVec3 lastStep = plan.cells[plan.cells.Count - 1] - plan.cells[plan.cells.Count - 2];
			var far = new List<IntVec3>();
			IntVec3 c0 = plan.cells[plan.cells.Count - 1];
			for (int i = 0; i < JumpLookSquares; i++)
			{
				far.Add(c0 + lastStep * i);
			}
			IntVec3 lip = plan.cells[0];
			float r2 = range * range;
			int pick = RM_RaiderTrenchMath.JumpLanding(0, far.Count, JumpLookSquares,
				i => far[i].InBounds(map) && g.ComponentOf(k, far[i]) == ct && ValidLanding(p, far[i]),
				i => far[i].DistanceToSquared(lip) <= r2 && GenSight.LineOfSight(lip, far[i], map));
			if (pick < 0)
			{
				return null;
			}
			IntVec3 land = far[pick];
			if (p.Position.DistanceToSquared(land) > r2 || !GenSight.LineOfSight(p.Position, land, map))
			{
				return p.Position == lip ? null : GotoJob(lip);
			}
			if (ability != null)
			{
				return ability.GetJob(land, land);
			}
			Job job = JobMaker.MakeJob(JobDefOf.CastJump, land);
			job.verbToUse = verb;
			return job;
		}

		// ── ladders ───────────────────────────────────────────────────────

		/// <summary>The ladder already standing in a slot: one that reaches, hung toward the slot's wall, that this pawn may
		/// climb. Null with <paramref name="blocked"/> when the square holds something else (a ramp, another ladder).</summary>
		private static Thing SlotLadder(Map map, Pawn p, IntVec3 cell, IntVec3 toward, out bool blocked)
		{
			blocked = false;
			Thing ladder = RM_LadderUtility.LadderAt(map, cell);
			if (ladder != null)
			{
				if (RM_LadderUtility.HangsToward(ladder, toward) && RM_LadderRules.LadderLetsOut(map, cell, p))
				{
					return ladder;
				}
				blocked = true;
				return null;
			}
			blocked = RM_PitRamp.RampAt(map, cell) != null;
			return null;
		}

		/// <summary>Null when ladders cannot do this crossing (<paramref name="waiting"/> false: breach instead) or cannot do it
		/// YET (<paramref name="waiting"/> true: the next slot is out of reach or another raider is setting it; think again later);
		/// else the next ladder job, or the step down into the trench once every ladder stands.</summary>
		private static Job LadderJob(Pawn p, Plan plan, int k, out bool waiting)
		{
			waiting = false;
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			if (!RM_RaiderTrenchSettings.raiderLaddersEnabled || def == null || RM_RaiderTrenchDefOf.RM_RaiderSetLadder == null)
			{
				return null;
			}
			int reach = RM_LadderUtility.MaxLevelsOf(def);
			if (reach < 0)
			{
				return null;   // portable ladders switched off
			}
			List<RM_RaiderTrenchMath.LadderSlot> slots = RM_RaiderTrenchMath.LadderSlots(plan.depths, k, reach);
			if (slots == null || slots.Count == 0)
			{
				return null;
			}
			Map map = p.Map;
			for (int s = 0; s < slots.Count; s++)
			{
				IntVec3 cell = plan.cells[slots[s].cell];
				IntVec3 toward = plan.cells[slots[s].toward];
				if (SlotLadder(map, p, cell, toward, out bool blocked) != null)
				{
					continue;
				}
				if (blocked)
				{
					return null;
				}
				if (!p.CanReserve(cell) || !p.CanReach(cell, PathEndMode.Touch, Danger.Deadly))
				{
					waiting = true;
					return null;   // another raider is setting it, or the slot is past a ladder not yet set: think again later
				}
				Warn(p, "RMFlow_RaidersSetLadders");
				Job job = JobMaker.MakeJob(RM_RaiderTrenchDefOf.RM_RaiderSetLadder, cell, toward);
				job.count = slots[s].drop;
				return job;
			}
			// Every ladder stands. Normally TryCross has already handed back to vanilla (the ladders make the target reachable:
			// TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP); this is the fallback when the far side is still cut off for this pawn
			// (a ladder too short, a wall filled in): step into the trench, the first square off this pawn's component it can reach.
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int cs = g.ComponentOf(k, p.Position);
			for (int i = 1; i < plan.cells.Count; i++)
			{
				IntVec3 c = plan.cells[i];
				if (g.ComponentOf(k, c) != cs && p.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
				{
					return GotoJob(c);
				}
			}
			return null;   // the ladders stand and still do not do it: breach instead
		}

		// ── breach by fill ────────────────────────────────────────────────

		private static Job FillJob(Pawn p, Plan plan, int k)
		{
			if (!RM_RaiderTrenchSettings.raiderFillEnabled || RM_RaiderTrenchDefOf.RM_RaiderFillTrench == null)
			{
				return null;
			}
			int[] t = RM_RaiderTrenchMath.FillTargets(plan.depths, k);
			if (!RM_RaiderTrenchMath.StepsClimbable(t, k))
			{
				return null;
			}
			int i = RM_RaiderTrenchMath.NextFill(plan.depths, t);
			if (i < 0)
			{
				return null;
			}
			Map map = p.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			IntVec3 c = plan.cells[i];
			// one raider a square (the driver reserves it): two at once would shovel it past its causeway step
			if (eng == null || !eng.CanFillIn(c) || !p.CanReserve(c) || !p.CanReach(c, PathEndMode.Touch, Danger.Deadly))
			{
				return null;
			}
			Warn(p, "RMFlow_RaidersFillTrench");
			return JobMaker.MakeJob(RM_RaiderTrenchDefOf.RM_RaiderFillTrench, c);
		}

		private static Job GotoJob(IntVec3 c)
		{
			Job job = JobMaker.MakeJob(JobDefOf.Goto, c, 600, true);
			job.locomotionUrgency = LocomotionUrgency.Jog;
			job.collideWithPawns = true;
			return job;
		}

		private static void Warn(Pawn p, string key)
		{
			Lord lord = p.GetLord();
			if (dryRun || lord == null || !warned.Add(lord))
			{
				return;
			}
			Messages.Message(key.Translate(p.Faction.Name), new LookTargets(p), MessageTypeDefOf.ThreatSmall, false);
		}

		/// <summary>The whole decision for one raider (RM_RaiderTrenchMath.Choose), or null for vanilla to carry on.</summary>
		public static Job TryCross(Pawn p)
		{
			if (!On || p?.Map == null || !RM_SuperdeepTrap.AnyHole(RM_SuperdeepTrap.EngineOf(p.Map)))
			{
				return null;
			}
			bool eligible = Eligible(p, out int k);
			bool siege = eligible && IsSiege(p);
			if (!eligible || siege)
			{
				return null;
			}
			Thing target = TargetFor(p);
			if (target == null)
			{
				return null;
			}
			bool reachable = p.CanReach(target, PathEndMode.Touch, Danger.Deadly, false, false, TraverseMode.PassAllDestroyableThings);
			if (reachable)
			{
				return null;   // GoAround: the masks route round the trench; vanilla's givers act
			}
			if (!TryPlan(p, k, target, OriginFor(p, k), out Plan plan) && !TryPlan(p, k, target, p.Position, out plan))
			{
				return null;
			}
			RememberLip(p, plan.cells[0]);
			// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 4 (R5): a raider carrying a plank lays it first when the gap fits
			Job plank = Pits.RM_RaidPlanks.PlankJob(p, plan.cells, plan.depths);
			if (plank != null)
			{
				return plank;
			}
			// The owner's order (RM_RaiderTrenchMath.Choose): jump, else ladders (the shallower pits), else breach by fill.
			Job jump = RM_RaiderTrenchSettings.raiderJumpsEnabled ? JumpJob(p, plan, k) : null;
			bool toolUser = ToolUser(p);
			bool ladderable = jump == null && toolUser && LaddersFeasible(p, plan, k);
			Job fill = jump == null && toolUser && !ladderable ? FillJob(p, plan, k) : null;
			switch (RM_RaiderTrenchMath.Choose(true, true, false, false, RM_RaiderTrenchSettings.raiderJumpsEnabled, jump != null,
				toolUser, RM_RaiderTrenchSettings.raiderLaddersEnabled, ladderable, RM_RaiderTrenchSettings.raiderFillEnabled, fill != null))
			{
				case RM_RaiderTrenchMath.Crossing.Jump:
					return jump;
				case RM_RaiderTrenchMath.Crossing.Ladder:
				{
					// null while the next ladder's square is out of reach or taken: think again later; null because ladders cannot
					// do it after all (a slot blocked since, the ladders standing and the far side still cut off): breach by fill
					Job ladder = LadderJob(p, plan, k, out bool waiting);
					return ladder ?? (waiting ? null : FillJob(p, plan, k));
				}
				case RM_RaiderTrenchMath.Crossing.Fill:
					return fill;
				default:
					return null;
			}
		}

		/// <summary>Ladders cannot do it (no slot list, a drop past reach, a blocked square, ladders off): only then breach.</summary>
		private static bool LaddersFeasible(Pawn p, Plan plan, int k)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			if (!RM_RaiderTrenchSettings.raiderLaddersEnabled || def == null)
			{
				return false;
			}
			int reach = RM_LadderUtility.MaxLevelsOf(def);
			if (reach < 0)
			{
				return false;
			}
			List<RM_RaiderTrenchMath.LadderSlot> slots = RM_RaiderTrenchMath.LadderSlots(plan.depths, k, reach);
			if (slots == null || slots.Count == 0)
			{
				return false;
			}
			for (int s = 0; s < slots.Count; s++)
			{
				SlotLadder(p.Map, p, plan.cells[slots[s].cell], plan.cells[slots[s].toward], out bool blocked);
				if (blocked)
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>Bridge/debug read (jawa/static_call): what this raider would do now.</summary>
		public static string ProofDecision(Pawn p)
		{
			if (p == null || !p.Spawned)
			{
				return "no pawn";
			}
			if (!On)
			{
				return "off";
			}
			if (!Eligible(p, out int k))
			{
				return "not eligible";
			}
			if (IsSiege(p))
			{
				return "siege";
			}
			Thing target = TargetFor(p);
			if (target == null)
			{
				return "no target";
			}
			if (p.CanReach(target, PathEndMode.Touch, Danger.Deadly, false, false, TraverseMode.PassAllDestroyableThings))
			{
				return "GoAround " + target;
			}
			if (!TryPlan(p, k, target, OriginFor(p, k), out Plan plan) && !TryPlan(p, k, target, p.Position, out plan))
			{
				return "None (no crossing line) " + target;
			}
			Job j;
			dryRun = true;
			try
			{
				j = TryCross(p);
			}
			finally
			{
				dryRun = false;
			}
			return (j == null ? "None" : j.def.defName + " " + j.targetA) + " line=" + string.Join("/", plan.depths);
		}
	}

	[HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
	[RimMandrake.Shared.PatchFeature("Raiders cross trenches (jump packs)", typeof(RimMandrake.FlowWorks.RM_RaiderTrenchSettings), "raiderTrenchEnabled")]
	public static class RM_Patch_GameInit_RaiderTrenchMemos
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			RM_RaiderTrench.ClearMemos();
		}
	}

	[DefOf]
	public static class RM_RaiderTrenchDefOf
	{
		public static JobDef RM_RaiderSetLadder;
		public static JobDef RM_RaiderFillTrench;

		static RM_RaiderTrenchDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_RaiderTrenchDefOf));
		}
	}

	/// <summary>Appended to the AssaultColony, Breaching and Sapper duties (Patches/RaiderTrench). Null unless a trench is
	/// what stands between this raider and the colony.</summary>
	public class JobGiver_RM_CrossTrench : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			return RM_RaiderTrench.TryCross(pawn);
		}
	}

	/// <summary>Set a scaling ladder (targetA: the trench square, targetB: the wall square it hangs toward; job.count: the
	/// drop in levels) or shovel one level into a trench square (targetA), standing beside it. Re-checked at the end.</summary>
	public class JobDriver_RM_RaiderTrenchWork : JobDriver
	{
		private bool IsLadder => job.def == RM_RaiderTrenchDefOf.RM_RaiderSetLadder;

		/// <summary>One raider works a square at a time (the givers skip a square another raider holds).</summary>
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		private int WorkTicks()
		{
			if (IsLadder)
			{
				return RM_RaiderTrenchMath.LadderTicks(Mathf.Max(1, job.count) * RM_Volume.MetresPerLevel, RM_RaiderTrenchSettings.raiderLadderSpeed);
			}
			RM_MapComponent_Excavation eng = Map.GetComponent<RM_MapComponent_Excavation>();
			byte cur = eng == null ? (byte)1 : eng.DepthAt(job.targetA.Cell);
			int work = RM_ExcavationDepth.WorkToDeepen((byte)Mathf.Max(0, cur - 1)) / 2;
			float speed = StatDefOf.MiningSpeed.Worker.IsDisabledFor(pawn) ? 0.5f : pawn.GetStatValue(StatDefOf.MiningSpeed);
			return RM_RaiderTrenchMath.FillTicks(work, speed, RM_RaiderTrenchSettings.raiderFillSpeed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			AddFinishAction(cond => RM_RaiderTrench.NoteWorkEnd(pawn, job, cond, CurToilIndex));
			this.FailOn(() => !RM_RaiderTrench.On);
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
			Toil work = ToilMaker.MakeToil("RM_RaiderTrenchWork");
			work.initAction = delegate
			{
				pawn.pather.StopDead();
				pawn.rotationTracker.FaceCell(job.targetA.Cell);
			};
			work.tickAction = delegate
			{
				pawn.rotationTracker.FaceCell(job.targetA.Cell);
			};
			work.defaultCompleteMode = ToilCompleteMode.Delay;
			work.defaultDuration = WorkTicks();
			work.handlingFacing = true;
			work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			work.WithProgressBarToilDelay(TargetIndex.A);
			yield return work;
			Toil done = ToilMaker.MakeToil("RM_RaiderTrenchWork_Done");
			done.initAction = delegate
			{
				Map map = pawn.Map;
				IntVec3 c = job.targetA.Cell;
				RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
				if (eng == null)
				{
					return;
				}
				if (!IsLadder)
				{
					if (eng.CanFillIn(c))
					{
						eng.FillIn(c);
					}
					return;
				}
				IntVec3 wall = job.targetB.Cell;
				ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
				if (def == null || RM_LadderUtility.LadderAt(map, c) != null || RM_PitRamp.RampAt(map, c) != null
					|| RM_SuperdeepTrap.StepDepthAt(map, eng, c) <= RM_SuperdeepTrap.StepDepthAt(map, eng, wall))
				{
					return;
				}
				Thing ladder = ThingMaker.MakeThing(def);
				ladder.SetFaction(pawn.Faction);
				GenSpawn.Spawn(ladder, c, map, Rot4.FromIntVec3(wall - c));
			};
			done.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return done;
		}
	}

	/// <summary>"Some may have jump packs": on a map with a dug trench, a share of an industrial-or-better raid's people
	/// arrive wearing one (only if it displaces nothing they wear: no shield belt is swapped out). Never a siege.</summary>
	[HarmonyPatch(typeof(IncidentWorker_Raid), "PostProcessSpawnedPawns")]
	[RimMandrake.Shared.PatchFeature("Raiders cross trenches (jump packs)", typeof(RimMandrake.FlowWorks.RM_RaiderTrenchSettings), "raiderTrenchEnabled")]
	public static class RM_Patch_Raid_JumpPacks
	{
		private static ThingDef jumpPack;
		private static bool looked;

		[HarmonyPostfix]
		public static void Postfix(IncidentParms parms, List<Pawn> pawns)
		{
			if (!RM_RaiderTrench.On || !RM_RaiderTrenchSettings.raiderJumpsEnabled || RM_RaiderTrenchSettings.raiderJumpPackShare <= 0f
				|| pawns == null || !(parms?.target is Map map) || parms.raidStrategy?.Worker is RaidStrategyWorker_Siege
				|| parms.faction == null || parms.faction.def.techLevel < TechLevel.Industrial)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || eng.ClimbCellCount < RM_RaiderTrench.MinClimbCellsForJumpPacks)
			{
				return;
			}
			if (!looked)
			{
				looked = true;
				jumpPack = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_PackJump");
			}
			if (jumpPack == null)
			{
				return;
			}
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p?.apparel == null || !p.RaceProps.Humanlike
					|| !RM_RaiderTrenchMath.GetsJumpPack(p.thingIDNumber, RM_RaiderTrenchSettings.raiderJumpPackShare)
					|| !p.apparel.CanWearWithoutDroppingAnything(jumpPack))
				{
					continue;
				}
				Apparel ap = (Apparel)ThingMaker.MakeThing(jumpPack, GenStuff.DefaultStuffFor(jumpPack));
				p.apparel.Wear(ap, false);
			}
		}
	}

	/// <summary>RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP Mod Settings (own static class, scribed into the FlowWorks settings like
	/// RM_WallClimbSettings). Defaults are the ruling: everything on. All off: a raid facing a trench it cannot cross mills,
	/// shoots across and leaves, as before.</summary>
	public static class RM_RaiderTrenchSettings
	{
		public static bool raiderTrenchEnabled = true;
		public static bool raiderJumpsEnabled = true;
		public static bool raiderLaddersEnabled = true;
		public static bool raiderFillEnabled = true;
		public static float raiderLadderSpeed = 1f;
		public static float raiderFillSpeed = 1f;
		/// <summary>PROVISIONAL: "some may have jump packs".</summary>
		public static float raiderJumpPackShare = 0.1f;

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: shipped value of every public static bool/float/int setting above. MUST stay
		// below the LAST public setting field (C# runs static initialisers in textual order).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_RaiderTrenchSettings));

		/// <summary>The Reset button: every setting on this screen back to its shipped value.</summary>
		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_RaiderTrenchSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref raiderTrenchEnabled, "raiderTrenchEnabled", true);
			Scribe_Values.Look(ref raiderJumpsEnabled, "raiderJumpsEnabled", true);
			Scribe_Values.Look(ref raiderLaddersEnabled, "raiderLaddersEnabled", true);
			Scribe_Values.Look(ref raiderFillEnabled, "raiderFillEnabled", true);
			Scribe_Values.Look(ref raiderLadderSpeed, "raiderLadderSpeed", 1f);
			Scribe_Values.Look(ref raiderFillSpeed, "raiderFillSpeed", 1f);
			Scribe_Values.Look(ref raiderJumpPackShare, "raiderJumpPackShare", 0.1f);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Raiders against trenches");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Raiders cross trenches", ref raiderTrenchEnabled,
				"On, raiders who cannot reach your colony because a trench or pit is in the way go around it if there is a way; "
			  + "if there is none they jump it, set scaling ladders, or shovel a causeway in. Sieges never do: they shell you. "
			  + "Needs \"Pits can trap whoever falls in\" and \"Pits trap by relative height\". Off: a raid facing a trench it cannot cross waits, "
			  + "shoots across and leaves.");
			list.CheckboxLabeled("  Raiders jump trenches", ref raiderJumpsEnabled,
				"Raiders with a jump pack or a leaping ability jump across a trench in range, and land on their feet.");
			int pct = Mathf.RoundToInt(raiderJumpPackShare * 100f);
			list.Label("  Raiders who bring a jump pack: " + pct + "%", tooltip:
				"On a map with a dug trench, this share of an industrial-or-better raid's people arrive wearing a jump pack (never "
			  + "one that would replace a shield belt). Sieges never. 0% = only raiders who already had one.");
			raiderJumpPackShare = Mathf.Round(list.Slider(raiderJumpPackShare, 0f, 1f) * 20f) / 20f;
			list.CheckboxLabeled("  Raiders set scaling ladders", ref raiderLaddersEnabled,
				"Raiders set portable ladders down a trench wall and up the far one when every wall is within a portable "
			  + "ladder's reach (the shallower pits). The ladder is theirs: their people climb it, yours too; shoot it (40 HP) "
			  + "and whoever is down there is in a pit. Needs \"Portable ladders\" on.");
			int ladderSec = Mathf.RoundToInt(RM_RaiderTrenchMath.LadderTicks(2.0, raiderLadderSpeed) / 60f);
			list.Label("  Scaling ladder speed: x" + raiderLadderSpeed.ToString("0.00") + "  (about " + ladderSec
			  + " s for a 2 m wall)", tooltip: "About 10 s plus 1 s a metre at x1.");
			raiderLadderSpeed = Mathf.Round(list.Slider(raiderLadderSpeed, 0.25f, 4f) * 20f) / 20f;
			list.CheckboxLabeled("  Raiders breach by filling", ref raiderFillEnabled,
				"When ladders cannot do it (too deep, too narrow, ladders off), raiders shovel earth into the trench until every "
			  + "step of a one-square causeway is climbable, then walk across it.");
			list.Label("  Breach filling speed: x" + raiderFillSpeed.ToString("0.00"), tooltip:
				"How fast raiders shovel, as a multiple of your own fill-in speed for the same person.");
			raiderFillSpeed = Mathf.Round(list.Slider(raiderFillSpeed, 0.25f, 4f) * 20f) / 20f;
		}
	}
}
