using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. The FEED verb (spec §3): "A scheduled
	/// throw-job: mirrik cocoon waste, bladder-fruit scrap, kitchen offal
	/// to the water's edge." No bespoke "fish feed" item exists yet, so
	/// this wave accepts any ordinary nutrition-giving ingestible a colony
	/// already hauls (meat, produce, kibble) rather than inventing one --
	/// a scoping choice, not a claim it's the final feed item set. Only
	/// fires when <see cref="RM_MapComponent_PoolStock.BodiesNeedingFeed"/>
	/// says a pen is actually due (spec's daily cadence), so this never
	/// competes for food with the colony's own meals when nothing needs it.
	/// </summary>
	public class RM_WorkGiver_FeedPoolPen : WorkGiver_Scanner
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
			if (!IsFeedCandidate(t) || t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, 1, null, forced))
			{
				return false;
			}
			return TryFindHungryPenCell(pawn, out _);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsFeedCandidate(t))
			{
				return null;
			}
			if (!TryFindHungryPenCell(pawn, out IntVec3 cell))
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_PoolStockDefOf.RM_FeedPoolPen, t, cell);
			job.count = 1;
			return job;
		}

		private static bool IsFeedCandidate(Thing t)
		{
			ThingDef def = t?.def;
			return def != null && def.IsNutritionGivingIngestible && def.ingestible?.foodType != FoodTypeFlags.None;
		}

		private static bool TryFindHungryPenCell(Pawn pawn, out IntVec3 cell)
		{
			cell = IntVec3.Invalid;
			RM_MapComponent_PoolStock comp = pawn.Map.GetComponent<RM_MapComponent_PoolStock>();
			if (comp == null)
			{
				return false;
			}
			int currentTick = Find.TickManager.TicksGame;
			float bestDist = float.MaxValue;
			bool found = false;
			foreach (RM_PoolBody body in comp.BodiesNeedingFeed(currentTick))
			{
				if (!(comp.ZoneFor(body) is RM_Zone_PoolPen pen) || pen.CellCount == 0)
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
