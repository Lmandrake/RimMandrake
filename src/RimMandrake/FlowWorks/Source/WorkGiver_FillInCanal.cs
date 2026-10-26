using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>Mirror of <see cref="WorkGiver_DigCanal"/>, including its
	/// stale-designation discipline: the designation is re-validated against the
	/// CURRENT grid, not against whatever was true when the player dragged the
	/// box. A cell can stop being an excavation between designation and arrival
	/// (another pawn fills it first, a flood fills it in, the mechanic is
	/// switched off), and handing out a doomed job instead of clearing the
	/// designation is what produced the dig/flood cycle this pattern was written
	/// to kill.</summary>
	public class WorkGiver_FillInCanal : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		/// <summary>A materialised list, as WorkGiver_DigCanal: HasJobOnCell deletes stale designations while the scanner
		/// walks this result, and a lazy enumerator over the live designation list throws "collection modified".</summary>
		public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
		{
			List<IntVec3> cells = new List<IntVec3>();
			foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RimMandrakeFlowWorks_DefOf.RM_FillInCanal))
			{
				cells.Add(item.target.Cell);
			}
			return cells;
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RimMandrakeFlowWorksSettings.fillInEnabled
				|| !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
		}

		public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			Designation des = pawn.Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
			if (des == null)
			{
				return false;
			}
			RM_MapComponent_Excavation excavation = pawn.Map.GetComponent<RM_MapComponent_Excavation>();
			bool stale = !RimMandrakeFlowWorksSettings.fillInEnabled
				|| excavation == null
				|| !excavation.CanFillIn(c)
				|| c.GetEdifice(pawn.Map) != null;
			if (stale)
			{
				des.Delete();
				return false;
			}
			// Pit model 3.8: never fill a cell in on top of someone. The designator
			// checks this only at designation time; a pawn can fall or walk in later.
			// Temporary, so the designation is kept.
			if (c.GetFirstPawn(pawn.Map) != null)
			{
				return false;
			}
			if (!pawn.CanReserve(c, 1, -1, ReservationLayerDefOf.Floor, forced))
			{
				return false;
			}
			// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED (owner 2026-10-25: "You can't dig without them. Hands don't work"): no shovel
			// in the pack and none free on the map, no job; the designation stays (someone with a shovel, or a machine, may come).
			if (!RM_Shovels.CanWorkOrFetch(pawn, forced))
			{
				return false;
			}
			// DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY: an unpaid pit with nothing to pay it is no job here, so the scanner can
			// pick a paid-up pit instead of stopping at a nearer one JobOnCell would refuse.
			if (Unpaid(pawn.Map, c) && !HasMaterial(pawn, forced))
			{
				JobFailReason.Is(NoMaterialReason);
				return false;
			}
			return true;
		}

		private const string NoMaterialReason = "No gravel, crushed ice or stone chunks to fill with.";

		private static bool Unpaid(Map map, IntVec3 c)
		{
			RM_MapComponent_FillCredit credit = map.GetComponent<RM_MapComponent_FillCredit>();
			return RimMandrakeFlowWorksSettings.fillCostsSpoilEnabled && credit != null
				&& RM_GroundClassMath.CreditShort(credit.CreditAt(c)) > 0;
		}

		// one material search per pawn per tick, however many pit cells the scanner asks about
		private static int cachePawn = -1;
		private static int cacheTick = -1;
		private static bool cacheForced;
		private static bool cacheHas;
		private static Game cacheGame;   // STATIC_STATE: a reload replays the same pawn ids at the same tick, so the memo is keyed by game too

		private static bool HasMaterial(Pawn pawn, bool forced)
		{
			int tick = Find.TickManager.TicksGame;
			if (cacheGame != Current.Game || cachePawn != pawn.thingIDNumber || cacheTick != tick || cacheForced != forced)
			{
				cacheGame = Current.Game;
				cachePawn = pawn.thingIDNumber;
				cacheTick = tick;
				cacheForced = forced;
				cacheHas = RM_DigSpoil.FindFillMaterial(pawn, forced) != null;
			}
			return cacheHas;
		}

		public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: no shovel in the pack, fetch the nearest free one first (HasJobOnCell found
			// it); the next scan, shovel in pack, gives this job.
			if (!RM_Shovels.Ready(pawn))
			{
				return RM_Shovels.FetchJobFor(pawn, forced);
			}
			// DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY (owner 2026-10-25): a notch costs 1 gravel or 2 chunks. A paid-up pit gets the
			// work alone; otherwise the filler fetches one unit, nearest gravel first.
			if (!Unpaid(pawn.Map, c))
			{
				return JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillInCanalJob, c);
			}
			Thing material = RM_DigSpoil.FindFillMaterial(pawn, forced);
			if (material == null)
			{
				JobFailReason.Is(NoMaterialReason);
				return null;
			}
			Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillInCanalJob, c, material);
			job.count = 1;
			return job;
		}
	}
}
