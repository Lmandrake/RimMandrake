using RimWorld;
using Verse;

namespace RimMandrake.FluidCanals
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

		protected override DesignationDef DesDef => RimMandrakeFluidCanals_DefOf.RM_DigCanal;

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
				Map.terrainGrid.SetTerrain(c, RimMandrakeFluidCanals_DefOf.RM_Channel_Empty);
			}
#pragma warning disable 618
			// Legacy recoverable-release path. Obsolete as a CONCEPT (ruling 24:
			// a source is terrain, not a building) but still live and still
			// working until the migration deletes it, so it keeps being called.
			CompFluidReservoir.Notify_CanalCellOpened(Map, c);
#pragma warning restore 618
		}
	}
}
