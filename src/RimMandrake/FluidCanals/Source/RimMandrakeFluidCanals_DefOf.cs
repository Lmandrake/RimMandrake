using RimWorld;
using Verse;

namespace RimMandrake.FluidCanals
{
	[DefOf]
	public static class RimMandrakeFluidCanals_DefOf
	{
		public static DesignationDef RM_DigCanal;

		public static JobDef RM_DigCanalJob;

		/// <summary>D = 1. Keeps its original defName so every save's dug cells
		/// survive the arrival of the depth ladder.</summary>
		public static TerrainDef RM_Channel_Empty;

		public static TerrainDef RM_Channel_Mid;

		public static TerrainDef RM_Channel_Deep;

		public static TerrainDef RM_Channel_Superdeep;

		public static FluidDef RM_Fluid_Water;

		public static ThingDef RM_FluidCanalFlood;

		static RimMandrakeFluidCanals_DefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RimMandrakeFluidCanals_DefOf));
		}
	}
}
