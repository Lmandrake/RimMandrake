using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 4. The CULL verb (spec §3): "The set-piece:
	/// the two-handler vhorrin catch that rescues a failing pool." Targets a
	/// live RM_Vhorrin standing in a player's own <see cref="RM_Zone_PoolPen"/>
	/// — only pen stock is culled; a wild vhorrin (should one ever exist
	/// outside a pen, which nothing in this mod currently spawns) is not this
	/// job's business.
	/// </summary>
	public class RM_WorkGiver_CullVhorrin : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Pawn);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_WeepingStonesSettings.stockedPoolsEnabled;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return IsCullable(pawn, t, forced);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsCullable(pawn, t, forced))
			{
				return null;
			}
			return JobMaker.MakeJob(RM_PoolStockDefOf.RM_CullVhorrin, t);
		}

		private static bool IsCullable(Pawn pawn, Thing t, bool forced)
		{
			Pawn vhorrin = t as Pawn;
			if (vhorrin == null || vhorrin == pawn || vhorrin.Dead || !vhorrin.Spawned)
			{
				return false;
			}
			if (vhorrin.def == null || vhorrin.def.defName != "RM_Vhorrin")
			{
				return false;
			}
			if (!(vhorrin.Map.zoneManager.ZoneAt(vhorrin.Position) is RM_Zone_PoolPen))
			{
				return false;
			}
			if (!pawn.CanReserve(vhorrin, 1, -1, null, forced))
			{
				return false;
			}
			return pawn.CanReach(vhorrin, PathEndMode.Touch, Danger.Some);
		}
	}
}
