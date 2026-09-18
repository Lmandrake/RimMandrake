using RimWorld;
using Verse;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks
{
	[DefOf]
	public static class RimMandrakeFlowWorks_DefOf
	{
		public static DesignationDef RM_DigCanal;

		public static JobDef RM_DigCanalJob;

		/// <summary>Phase 2's other half: the inverse of RM_DigCanal.</summary>
		public static DesignationDef RM_FillInCanal;

		public static JobDef RM_FillInCanalJob;

		/// <summary>D = 1. Keeps its original defName so every save's dug cells
		/// survive the arrival of the depth ladder.</summary>
		public static TerrainDef RM_Channel_Empty;

		public static TerrainDef RM_Channel_Mid;

		public static TerrainDef RM_Channel_Deep;

		public static TerrainDef RM_Channel_Superdeep;

		public static FluidDef RM_Fluid_Water;

		/// <summary>Phase 7's roster entry, his ruling "tar needs the
		/// viscosity most of all" -- not yet wired to any source/driver
		/// selection UI, but reachable via <c>ActiveFluid =</c> the way
		/// debug tooling and a selftest already reach RM_Fluid_Water.</summary>
		public static FluidDef RM_Fluid_Tar;

		public static ThingDef RM_FluidCanalFlood;

		/// <summary>PHASE 5, ruling 26. The holder the depth engine keeps on every
		/// D = 4 cell so Pits' capture and struggle machinery can do the work.
		/// Never player-buildable.</summary>
		public static ThingDef RM_SuperdeepPit;

		/// <summary>PHASE 5. The one boolean that makes a dug cell exitable.</summary>
		public static ThingDef RM_Ladder;

		// ── LIQUID_BOTTLE_LOOP_1: fill/use/dirty/wash ──────────────────────
		public static JobDef RM_FillBottleJob;

		public static JobDef RM_WashBottleJob;

		public static ThingDef RM_BottleEmpty;

		public static ThingDef RM_BottleDirty;

		// ── third slice: buckets and barrels, same chain ───────────────────
		public static ThingDef RM_BucketEmpty;

		public static ThingDef RM_BucketDirty;

		public static ThingDef RM_BarrelEmpty;

		public static ThingDef RM_BarrelDirty;

		/// <summary>The one LiquidDef the wash job insists on -- "consumes
		/// water" always means fresh water, never whatever the bottle was
		/// last dirty with.</summary>
		public static LiquidDef RM_Liquid_FreshWater;

		static RimMandrakeFlowWorks_DefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RimMandrakeFlowWorks_DefOf));
		}
	}
}
