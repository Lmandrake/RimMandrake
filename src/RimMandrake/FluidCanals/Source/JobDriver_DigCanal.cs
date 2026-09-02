using RimWorld;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>Carves RM_Channel_Empty into a designated cell. Reuses
	/// vanilla's own JobDriver_AffectFloor (the SmoothFloor engine) --
	/// designation gating, reservation, work-speed ticking and the progress
	/// bar all come for free.</summary>
	public class JobDriver_DigCanal : JobDriver_AffectFloor
	{
		protected override int BaseWorkAmount => 3200;

		protected override DesignationDef DesDef => RimMandrakeFluidCanals_DefOf.RM_DigCanal;

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			Map.terrainGrid.SetTerrain(c, RimMandrakeFluidCanals_DefOf.RM_Channel_Empty);
			CompFluidReservoir.Notify_CanalCellOpened(Map, c);
		}
	}
}
