using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. The STOCK verb's carry-and-release half
	/// (spec §3): "carry them home in a wet skin... release into a
	/// designated pool zone." Any spawned, unforbidden breeding-stock item
	/// (recognised generically via <see cref="RM_PoolBreederUtility"/>, no
	/// per-species subclass) near a stocked pool pen with a reachable cell
	/// is a standing invitation, same opportunistic shape as
	/// <c>WorkGiver_FillBottle</c>.
	/// </summary>
	public class RM_WorkGiver_StockPoolPen : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

		public override ThingRequest PotentialWorkThingRequest =>
			ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_WeepingStonesSettings.stockedPoolsEnabled;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsBreedingStock(t) || t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, 1, null, forced))
			{
				return false;
			}
			return TryFindPenCell(pawn, out _);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsBreedingStock(t))
			{
				return null;
			}
			if (!TryFindPenCell(pawn, out IntVec3 cell))
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_PoolStockDefOf.RM_StockPoolPen, t, cell);
			job.count = 1;
			return job;
		}

		private static bool IsBreedingStock(Thing t)
		{
			return t?.def != null && RM_PoolBreederUtility.TryGetPawnKindDefName(t.def, out _);
		}

		/// <summary>Nearest RM_Zone_PoolPen with at least one cell the pawn
		/// can actually reach. Ignores whether the pen is already crowded --
		/// spec §3 says the mix decides for you ("Stock the wrong mix and
		/// the pool decides for you"), not that the job refuses.</summary>
		private static bool TryFindPenCell(Pawn pawn, out IntVec3 cell)
		{
			cell = IntVec3.Invalid;
			System.Collections.Generic.List<Zone> allZones = pawn.Map.zoneManager.AllZones;
			float bestDist = float.MaxValue;
			bool found = false;
			for (int i = 0; i < allZones.Count; i++)
			{
				if (!(allZones[i] is RM_Zone_PoolPen pen) || pen.CellCount == 0)
				{
					continue;
				}
				for (int c = 0; c < pen.Cells.Count; c++)
				{
					IntVec3 candidate = pen.Cells[c];
					if (!pawn.CanReach(candidate, PathEndMode.Touch, Danger.Some))
					{
						continue;
					}
					float dist = (candidate - pawn.Position).LengthHorizontalSquared;
					if (dist < bestDist)
					{
						bestDist = dist;
						cell = candidate;
						found = true;
					}
				}
			}
			return found;
		}
	}
}
