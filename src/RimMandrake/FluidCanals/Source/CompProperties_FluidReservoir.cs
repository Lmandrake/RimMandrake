using Verse;

namespace RimMandrake.FluidCanals
{
	public class CompProperties_FluidReservoir : CompProperties
	{
		public FluidDef fluidDef;

		/// <summary>Total volume this reservoir can spend before running dry.
		/// Consumed one <see cref="FluidDef.volumePerTile"/> at a time as the
		/// flood it feeds fills terrain.</summary>
		public float volume = 60f;

		public CompProperties_FluidReservoir()
		{
			compClass = typeof(CompFluidReservoir);
		}
	}
}
