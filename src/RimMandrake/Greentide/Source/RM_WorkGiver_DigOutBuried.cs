using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Greentide
{
	/// <summary>GREENTIDE_STANDALONE_MOD_1 (M8). Pattern mirrors FluidCanals'
	/// WorkGiver_DigCanal exactly: scan for the dig-out designation, hand out
	/// the job, and drop a stale designation if the cache is somehow already gone.</summary>
	public class RM_WorkGiver_DigOutBuried : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
		{
			foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_DefOf.RM_DesignationDigOutBuried))
			{
				yield return item.target.Cell;
			}
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_DefOf.RM_DesignationDigOutBuried);
		}

		public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			Designation des = pawn.Map.designationManager.DesignationAt(c, RM_DefOf.RM_DesignationDigOutBuried);
			if (des == null)
			{
				return false;
			}
			RM_MapComponent_MudSwallow comp = pawn.Map.GetComponent<RM_MapComponent_MudSwallow>();
			if (comp == null || !comp.HasBuriedAt(c))
			{
				des.Delete();
				return false;
			}
			return pawn.CanReserve(c, 1, -1, ReservationLayerDefOf.Floor, forced);
		}

		public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			return JobMaker.MakeJob(RM_DefOf.RM_DigOutBuried, c);
		}
	}
}
