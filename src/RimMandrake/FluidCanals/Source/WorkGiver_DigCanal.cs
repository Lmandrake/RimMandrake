using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FluidCanals
{
	/// <summary>Pattern mirrors <see cref="WorkGiver_ConstructAffectFloor"/> --
	/// scan for RM_DigCanal designations, hand out the dig job.</summary>
	public class WorkGiver_DigCanal : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
		{
			foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RimMandrakeFluidCanals_DefOf.RM_DigCanal))
			{
				yield return item.target.Cell;
			}
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFluidCanals_DefOf.RM_DigCanal);
		}

		public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			if (pawn.Map.designationManager.DesignationAt(c, RimMandrakeFluidCanals_DefOf.RM_DigCanal) == null)
			{
				return false;
			}
			return pawn.CanReserve(c, 1, -1, ReservationLayerDefOf.Floor, forced);
		}

		public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			return JobMaker.MakeJob(RimMandrakeFluidCanals_DefOf.RM_DigCanalJob, c);
		}
	}
}
