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
			Designation des = pawn.Map.designationManager.DesignationAt(c, RimMandrakeFluidCanals_DefOf.RM_DigCanal);
			if (des == null)
			{
				return false;
			}
			// Fixed 2026-09-02 (opus code review): this never re-checked terrain
			// after designation. A live flood can convert a still-designated
			// cell to water before a pawn reaches it; digging it back fires
			// Notify_TerrainChanged, which resets the flood's "no possible
			// cell" state and it re-floods -- an infinite dig/flood cycle
			// burning the full dig cost (3200 work) each time. Mirrors
			// Designator_DigCanal.CanDesignateCell's own terrain gate and
			// clears the stale designation instead of handing out a doomed job.
			TerrainDef terrain = c.GetTerrain(pawn.Map);
			if (terrain == RimMandrakeFluidCanals_DefOf.RM_Channel_Empty || terrain.IsWater || !terrain.IsSoil)
			{
				des.Delete();
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
