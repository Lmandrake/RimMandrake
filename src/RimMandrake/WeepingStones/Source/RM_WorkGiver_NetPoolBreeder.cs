using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. The NET half of the STOCK verb (spec
	/// §3): "Net breeders at a wild oasis." Opportunistic, no Designation —
	/// any spawned, stockable pool-fauna pawn standing OUTSIDE a player's
	/// own <see cref="RM_Zone_PoolPen"/> (i.e. a genuinely wild individual,
	/// not something already someone's stock) is a standing invitation.
	/// RM_Vhorrin is excluded by <see cref="RM_PoolBreederUtility"/> — it is
	/// never a breeder.
	/// </summary>
	public class RM_WorkGiver_NetPoolBreeder : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Pawn);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_WeepingStonesSettings.stockedPoolsEnabled;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return IsNettable(pawn, t, forced);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsNettable(pawn, t, forced))
			{
				return null;
			}
			return JobMaker.MakeJob(RM_PoolStockDefOf.RM_NetPoolBreeder, t);
		}

		private static bool IsNettable(Pawn pawn, Thing t, bool forced)
		{
			Pawn wild = t as Pawn;
			if (wild == null || wild == pawn || wild.Dead || !wild.Spawned)
			{
				return false;
			}
			if (wild.def == null || !RM_PoolBreederUtility.StockableSpeciesDefNames.Contains(wild.def.defName))
			{
				return false;
			}
			// Already someone's stock -- the pen is not a wild oasis.
			if (wild.Map.zoneManager.ZoneAt(wild.Position) is RM_Zone_PoolPen)
			{
				return false;
			}
			if (!pawn.CanReserve(wild, 1, -1, null, forced))
			{
				return false;
			}
			return pawn.CanReach(wild, PathEndMode.Touch, Danger.Some);
		}
	}
}
