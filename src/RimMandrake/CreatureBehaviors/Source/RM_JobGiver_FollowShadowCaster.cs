using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_GLITTER_BIRDS_COMMENSALS_1. The shade-FOLLOW mechanism
	/// (distinct from RM_JobGiver_WanderInShadeGrid's shade-PREFER mechanism,
	/// DESERT_SHADE_GRID_KEYSTONE_1) — "follow THIS creature's moving shadow"
	/// rather than "prefer any shaded cell". Same insert shape as that
	/// JobGiver (a ThinkTreeDef at insertTag Animal_PreWander,
	/// RM_ThinkTree_ShadowFollow), so it is tried for every animal on the map
	/// and returns no job at all for any pawn whose race lacks
	/// RM_ShadowFollowerExtension.
	///
	/// ROUTE CHOSEN: tracked shadow-caster comp (RM_Comp_ShadowCaster on the
	/// host), not ShadeAt+proximity. Read RM_MapComponent_ShadeGrid.CastsShade
	/// first: it only tests Building.fillPercent and Plant.visualSizeRange — a
	/// living Pawn, however large, casts NO shade there at all, and widening
	/// that shared, closed-item mechanism to cover pawns would be a second,
	/// unrelated design decision riding on this one. A tracked comp needs no
	/// change to that component, works today, and is a straightforward "who is
	/// the nearest opted-in host" query with no shade-grid staleness (recompute
	/// every 2000 ticks) in the loop at all.
	///
	/// The "moving" part of "moving shadow" is not modeled as a shadow
	/// position independent of the host — the host's own live Position, read
	/// fresh every time this fires, already gives a follower something to
	/// track continuously, via vanilla's own JobDriver_FollowClose (built for
	/// exactly this: RimWorld.JobGiver_AIFollowPawn is the vanilla pattern
	/// this mirrors, e.g. a bonded animal following its master). Deliberately
	/// NOT a subclass of JobGiver_AIFollowPawn: that base class's TryGiveJob
	/// logs an Error whenever GetFollowee returns null, because vanilla's own
	/// callers always have a guaranteed-live followee (a bonded master). Here,
	/// "no host currently on this map" is the ordinary, expected case (before
	/// a shade whale ever visits) and must degrade silently to vanilla wander,
	/// not spam the log every ~140 ticks per commensal.
	/// </summary>
	public class RM_JobGiver_FollowShadowCaster : ThinkNode_JobGiver
	{
		private const int FollowJobExpireInterval = 140;

		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.shadowFollowEnabled)
			{
				return null; // mod option: shadow-follow disabled
			}
			RM_ShadowFollowerExtension ext = pawn.def?.GetModExtension<RM_ShadowFollowerExtension>();
			if (ext == null || pawn.Map == null)
			{
				return null;
			}
			Pawn host = FindNearestHost(pawn, ext.searchRadius);
			if (host == null || !host.Spawned || !pawn.CanReach(host, PathEndMode.OnCell, Danger.Deadly))
			{
				return null;
			}
			float radius = ext.followRadiusOverride > 0f
				? ext.followRadiusOverride
				: (host.TryGetComp<RM_Comp_ShadowCaster>()?.Props.commensalFollowRadius ?? 3f);
			if (!JobDriver_FollowClose.FarEnoughAndPossibleToStartJob(pawn, host, radius))
			{
				return null;
			}
			Job job = JobMaker.MakeJob(JobDefOf.FollowClose, host);
			job.expiryInterval = FollowJobExpireInterval;
			job.checkOverrideOnExpire = true;
			job.followRadius = radius;
			return job;
		}

		/// <summary>
		/// Nearest spawned pawn carrying RM_Comp_ShadowCaster within
		/// searchRadius cells (horizontal distance) — the whole "host
		/// discovery" query, deliberately a plain map scan re-run each time
		/// this JobGiver fires (roughly once per FollowJobExpireInterval per
		/// idle commensal) rather than a maintained registry: cheap at the
		/// population sizes a "rides one megafauna's shadow" species implies,
		/// and it never goes stale the way a cached reference could across a
		/// host's death/despawn.
		/// </summary>
		private static Pawn FindNearestHost(Pawn pawn, float searchRadius)
		{
			Map map = pawn.Map;
			IReadOnlyList<Pawn> allPawns = map.mapPawns.AllPawnsSpawned;
			Pawn best = null;
			int bestDistSq = (int)(searchRadius * searchRadius);
			for (int i = 0; i < allPawns.Count; i++)
			{
				Pawn candidate = allPawns[i];
				if (candidate == pawn || !candidate.Spawned || candidate.Dead)
				{
					continue;
				}
				if (candidate.TryGetComp<RM_Comp_ShadowCaster>() == null)
				{
					continue;
				}
				int distSq = (candidate.Position - pawn.Position).LengthHorizontalSquared;
				if (distSq <= bestDistSq)
				{
					bestDistSq = distSq;
					best = candidate;
				}
			}
			return best;
		}
	}
}
