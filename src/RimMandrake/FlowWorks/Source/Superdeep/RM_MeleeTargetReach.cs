using System;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RAID_STALL_FIX_MELEE_TARGET_ACROSS_THE_PIT (Artisan pass 2, 2026-11-07, live on game A, save fw_story1_stall): three
	/// raiders stood at a pit's lip with job Wait for 4,000+ ticks. Every 250 ticks each took AttackMelee on a colonist inside the
	/// compound beyond the pit, the pather found no route, and vanilla's ErroredPather Wait(250) followed, for ever. CanReach to
	/// that colonist said no (RM_WallReach, ProofReachPair canReach=False found=False); the target finder never asked it.
	///
	/// WHY: a searcher with no ranged verb (or in an aggro mental state) takes AttackTargetFinder's melee branch, which is
	/// GenClosest.ClosestThingReachable (AttackTargetFinder.cs:233): a region breadth-first walk. Regions do not know a sheer
	/// pit wall (it is a missing edge in the cliff masks, not a region boundary), so the walk passes the pit and the finder
	/// hands back the colonist across it. The ranged branch's fallback already asks CanReach (:207), which the pit veto answers.
	///
	/// THE FIX: on a map with a hole, a melee search accepts only a target the searcher can reach (Touch, Danger.Deadly, the
	/// finder's own door and fence flags), the same CanReach the pather agrees with. A target in a pit that the raider can stand
	/// beside on the lip stays a target (Touch reaches it from the lip). With nothing reachable, FightEnemies gives no job and
	/// the duty goes on to its later givers: trash, go to the nearest hostile, sap, and JobGiver_RM_CrossTrench.
	/// </summary>
	[HarmonyPatch(typeof(AttackTargetFinder), nameof(AttackTargetFinder.BestAttackTarget))]
	[RimMandrake.Shared.PatchFeature("Melee attackers pick only targets they can walk to", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_AttackTargetFinder_MeleeReach
	{
		[HarmonyPrefix]
		[HarmonyPriority(Priority.Low)]
		public static void Prefix(IAttackTargetSearcher searcher, ref Predicate<Thing> validator, bool canBashDoors, bool canBashFences,
			bool onlyRanged)
		{
			if (!RM_WallReach.On || !(searcher?.Thing is Pawn p) || p.Map == null || !p.Spawned)
			{
				return;
			}
			Verb verb = searcher.CurrentEffectiveVerb;
			bool melee = ((verb == null || verb.verbProps.IsMeleeAttack) && !onlyRanged) || p.InAggroMentalState;
			if (!melee || !RM_SuperdeepTrap.AnyHole(RM_SuperdeepTrap.EngineOf(p.Map)))
			{
				return;
			}
			Predicate<Thing> inner = validator;
			validator = t => (inner == null || inner(t))
				&& (t == null || !t.Spawned || p.CanReach(t, PathEndMode.Touch, Danger.Deadly, canBashDoors, canBashFences));
			Wrapped++;
		}

		/// <summary>Searches this prefix narrowed since load (ProofThink reports it).</summary>
		public static int Wrapped;

		/// <summary>"pawnId" -> what the pawn's main think tree would hand it now ("THINK job=... target=... node=..."), its
		/// weapon and effective verb, its enemyTarget, and CanReach (Touch, Deadly) to that target and to the job's target.</summary>
		public static string ProofThink(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !int.TryParse(arg, out int id))
			{
				return "REFUSED: arg must be pawnId";
			}
			Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(q => q.thingIDNumber == id);
			if (p == null)
			{
				return "REFUSED: no such pawn";
			}
			Verb v = p.CurrentEffectiveVerb;
			Thing et = p.mindState.enemyTarget;
			string head = "THINK pawn=" + p.LabelShort + " weapon=" + (p.equipment?.Primary?.def.defName ?? "none")
				+ " verbMelee=" + (v == null ? "null" : v.verbProps.IsMeleeAttack.ToString()) + " aggro=" + p.InAggroMentalState
				+ " enemyTarget=" + (et == null ? "none" : et.LabelShort + "@" + et.Position + " reach=" + p.CanReach(et, PathEndMode.Touch, Danger.Deadly))
				+ " wrapped=" + Wrapped;
			ThinkResult r = p.thinker.MainThinkNodeRoot.TryIssueJobPackage(p, default(JobIssueParams));
			if (r.Job == null)
			{
				return head + " job=none";
			}
			LocalTargetInfo a = r.Job.targetA;
			return head + " job=" + r.Job.def.defName + " target=" + (a.HasThing ? a.Thing.LabelShort + "@" + a.Thing.Position : a.Cell.ToString())
				+ " targetReach=" + (a.IsValid && p.CanReach(a, PathEndMode.Touch, Danger.Deadly))
				+ " node=" + (r.SourceNode?.GetType().FullName ?? "null") + " giver=" + (r.Job.jobGiver?.GetType().Name ?? "null");
		}
	}
}
