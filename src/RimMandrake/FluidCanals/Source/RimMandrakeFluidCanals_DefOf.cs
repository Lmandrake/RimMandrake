using RimWorld;
using Verse;

namespace RimMandrake.FluidCanals
{
	[DefOf]
	public static class RimMandrakeFluidCanals_DefOf
	{
		public static DesignationDef RM_DigCanal;

		public static JobDef RM_DigCanalJob;

		public static TerrainDef RM_Channel_Empty;

		public static ThingDef RM_FluidCanalFlood;

		static RimMandrakeFluidCanals_DefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RimMandrakeFluidCanals_DefOf));
		}
	}
}
