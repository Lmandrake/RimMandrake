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

		/// <summary>PHASE 5. The one boolean that makes a dug cell exitable.</summary>
		public static ThingDef RM_Ladder;

		/// <summary>PIT_LEGACY_CODE_RETIRE_1: merged from the retired RimMandrakePits_DefOf
		/// (only the surviving hediffs). REWIRE pending: drowning keyed to fill at D=4
		/// (PIT_FILL_EFFECTS_1); exposure driven by temperature (PIT_TEMPERATURE_SOFTENING_1).</summary>
		public static HediffDef RM_PitDrowning;

		public static HediffDef RM_PitExposure;

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

		// ── LIQUID_BOTTLE_LOOP_1: the tank half (fill/empty at a tank) ─────
		public static ThingDef RM_LiquidTank;

		public static JobDef RM_EmptyIntoTankJob;

		public static JobDef RM_FillFromTankJob;

		// ── MANY_WATERS_DRILL_BUILDINGS_1: the fourth acquisition route ────
		public static ThingDef RM_LiquidDrill;

		public static ThingDef RM_LiquidTap;

		static RimMandrakeFlowWorks_DefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RimMandrakeFlowWorks_DefOf));
		}
	}
}
