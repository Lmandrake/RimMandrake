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

		public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
		{
			foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RimMandrakeFlowWorks_DefOf.RM_FillInCanal))
			{
				yield return item.target.Cell;
			}
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
			return pawn.CanReserve(c, 1, -1, ReservationLayerDefOf.Floor, forced);
		}

		public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			return JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_FillInCanalJob, c);
		}
	}
}
