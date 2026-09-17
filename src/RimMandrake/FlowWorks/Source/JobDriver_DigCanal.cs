using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>Cuts a cell one level deeper. Reuses vanilla's own
	/// JobDriver_AffectFloor (the SmoothFloor engine) -- designation gating,
	/// reservation, work-speed ticking and the progress bar all come for
	/// free.</summary>
	public class JobDriver_DigCanal : JobDriver_AffectFloor
	{
		/// <summary>Work scales with the level being cut (ruling 19's four
		/// depths): deeper spoil is further to move and further to throw. A
		/// SHALLOW cut still costs exactly the 3200 it always did, so nothing
		/// about an existing colony's dig gets more expensive.</summary>
		protected override int BaseWorkAmount
		{
			get
			{
				Map map = base.Map;
				if (map == null || !job.targetA.IsValid)
				{
					return RM_ExcavationDepth.WorkPerLevel;
				}
				IntVec3 c = job.targetA.Cell;
				if (!c.InBounds(map))
				{
					return RM_ExcavationDepth.WorkPerLevel;
				}
				byte current = RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c));
				return RM_ExcavationDepth.WorkToDeepen(current);
			}
		}

		protected override DesignationDef DesDef => RimMandrakeFlowWorks_DefOf.RM_DigCanal;

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			// The depth grid is the authority (ruling 18). Deepen() writes D and
			// lays the matching terrain, so pathCost and art follow the integer
			// rather than the other way round.
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (excavation != null)
			{
				excavation.Deepen(c);
			}
			else
			{
				// Defensive only: MapComponents are auto-discovered by
				// reflection, so this branch means something is badly wrong.
				Map.terrainGrid.SetTerrain(c, RimMandrakeFlowWorks_DefOf.RM_Channel_Empty);
			}
			// Ruling 24 (owner, 2026-09-16) deleted CompFluidReservoir: a source
			// is not a building, it is a SUPERDEEP cell at F = D. There is no
			// reservoir to notify any more — supply is the depth grid's own
			// business, and RM_MapComponent_Excavation's pulse is what moves it.
		}
	}
}
