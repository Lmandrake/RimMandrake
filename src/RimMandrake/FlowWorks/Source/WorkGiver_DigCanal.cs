using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>Pattern mirrors <see cref="WorkGiver_ConstructAffectFloor"/> --
	/// scan for RM_DigCanal designations, hand out the dig job.</summary>
	public class WorkGiver_DigCanal : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		// A COPY, never a lazy walk: HasJobOnCell deletes a stale designation, which removes it from the very list
		// SpawnedDesignationsOfDef iterates, and JobGiver_Work calls HasJobOnCell inside its foreach over this result
		// (an enumerator over the live list throws "collection modified" there). A List also takes its indexed fast path.
		public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
		{
			List<IntVec3> cells = new List<IntVec3>();
			foreach (Designation item in pawn.Map.designationManager.SpawnedDesignationsOfDef(RimMandrakeFlowWorks_DefOf.RM_DigCanal))
			{
				cells.Add(item.target.Cell);
			}
			return cells;
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFlowWorks_DefOf.RM_DigCanal);
		}

		public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			Designation des = pawn.Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal);
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
			//
			// Updated for ruling 19's depth ladder: an already-dug cell is no
			// longer a reason to drop the job, it is a reason to dig DEEPER.
			// The water and non-soil gates stand unchanged, and so does the
			// reason they exist.
			// Top layer (foundation first; not BaseTerrainAt, which reads under a
			// floor): liquid in a channel sits on the temp layer, and reading it
			// here silently deleted the designation of any channel that got wet
			// (rain, a pulse) before a pawn arrived.
			TerrainDef terrain = pawn.Map.terrainGrid.FoundationAt(c) ?? pawn.Map.terrainGrid.TopTerrainAt(c);
			// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: the depth is the GRID's, never the terrain's (terrain says only "2 m or
			// deeper": every square past 2 m is RM_Channel_Superdeep, so a terrain read stopped every dig at 2 m).
			RM_MapComponent_Excavation eng = pawn.Map.GetComponent<RM_MapComponent_Excavation>();
			int depth = eng != null ? eng.ExcavatedDepthAt(c) : RM_ExcavationDepth.DepthOfDryTerrain(terrain);
			int target = eng?.DigTargetAt(c) ?? 0;
			bool stale = terrain.IsWater
				|| c.GetEdifice(pawn.Map) != null
				|| !RM_DigDepthMath.MayDeepen(depth, RM_ExcavationDepth.MaxDigDepth)
				|| (target > 0 && depth >= target)
				|| (depth == RM_ExcavationDepth.Surface && !terrain.IsSoil && !(RimMandrakeFlowWorksSettings.digRockGroundEnabled && RM_DigDiscovery.RockOfTerrain(terrain) != null))
				|| (depth != RM_ExcavationDepth.Surface && !RimMandrakeFlowWorksSettings.digToDepthEnabled)
				// POND_BED (owner by card 2026-10-14): a dry bed already as deep as digging goes is never dug.
				|| (depth == RM_ExcavationDepth.Surface && eng?.FirstCutDepthAt(c) < 0);
			if (stale)
			{
				des.Delete();
				return false;
			}
			return pawn.CanReserve(c, 1, -1, ReservationLayerDefOf.Floor, forced);
		}

		public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
		{
			return JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_DigCanalJob, c);
		}
	}
}
