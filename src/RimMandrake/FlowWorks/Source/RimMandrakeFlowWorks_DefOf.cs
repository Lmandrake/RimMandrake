using RimWorld;
using Verse;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks
{
	[DefOf]
	public static class RimMandrakeFlowWorks_DefOf
	{
		public static DesignationDef RM_DigCanal;

		/// <summary>Liquid networks L7 (rev 2 §3.7): the spill of a liquid with no spillFilth of its own.</summary>
		public static ThingDef RM_Filth_LiquidSpill;

		public static JobDef RM_DigCanalJob;

		/// <summary>Phase 2's other half: the inverse of RM_DigCanal.</summary>
		public static DesignationDef RM_FillInCanal;

		public static JobDef RM_FillInCanalJob;
		public static JobDef RM_CaptureDown;

		/// <summary>D = 1. Keeps its original defName so every save's dug cells
		/// survive the arrival of the depth ladder.</summary>
		public static TerrainDef RM_Channel_Empty;

		public static TerrainDef RM_Channel_Mid;

		public static TerrainDef RM_Channel_Deep;

		public static TerrainDef RM_Channel_Superdeep;

		/// <summary>POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2: a dried pond square at bed depth 2 / 4 (owner look (b)).</summary>
		public static TerrainDef RM_Lakebed_Shallow;

		public static TerrainDef RM_Lakebed_Deep;

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: a dried lake square at bed depth 8 or more (the deep art, tinted).</summary>
		public static TerrainDef RM_Lakebed_Abyss;

		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (§4): a drawn-down still pond square holding 3 levels.</summary>
		public static TerrainDef RM_WaterChestDeepStill;

		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (§4, D4): a still pond square holding 1 level, the bed showing.</summary>
		public static TerrainDef RM_WaterThin;

		public static FluidDef RM_Fluid_Water;

		/// <summary>Phase 6: the non-ticking flame drawn over a burning liquid cell (RM_LiquidFire).</summary>
		public static ThingDef RM_LiquidFlame;

		/// <summary>CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: the big flame over a burning chemfuel cell (same art, drawn larger).</summary>
		public static ThingDef RM_LiquidFlame_Inferno;

		/// <summary>Phase 7's roster entry, his ruling "tar needs the
		/// viscosity most of all". A tar pond's body takes it from its terrain;
		/// EnvironmentalHazards' RUT_IncidentWorker_TarPitBelch reads this field.</summary>
		public static FluidDef RM_Fluid_Tar;

		public static ThingDef RM_FluidCanalFlood;

		/// <summary>PHASE 5. The one boolean that makes a dug cell exitable.</summary>
		public static ThingDef RM_Ladder;

		// CANAL_BOTTOM_SPIKES_1
		public static ThingDef RM_Spikes;

		// FALL_GUARDRAILS_BUILD_REAL_OBJECT: read by RM_FallRails.IsRail
		public static ThingDef RM_PitGuardrail;

		// FLOWWORKS_DOOR_FAMILY_1. RM_Sluice, RM_SecurityGrateDoor, RM_LiquidTank, RM_LiquidDrill and RM_LiquidTap are
		// read by no code: they stay as existence guards, so a renamed or missing def fails loudly at startup.
		public static ThingDef RM_Sluice;
		public static ThingDef RM_SecurityGrateDoor;

		/// <summary>PIT_LEGACY_CODE_RETIRE_1: merged from the retired RimMandrakePits_DefOf
		/// (only the surviving hediffs). Drowning is driven by fill at D=4 (RM_PitFillEffects, PIT_FILL_EFFECTS_1);
		/// exposure by standing on an unroofed, uncovered D=4 cell (RM_PitExposure, PIT_TEMPERATURE_SOFTENING_1).</summary>
		public static HediffDef RM_PitDrowning;

		public static HediffDef RM_PitExposure;

		/// <summary>DEEP_WATER_BUILD_SWIM_OR_SINK: swim exhaustion (severity 0..1, set by Swimming.RM_Swim.Tick).</summary>
		public static HediffDef RM_SwimExhaustion;

		// ── LIQUID_BOTTLE_LOOP_1: fill/use/dirty/wash ──────────────────────
		public static JobDef RM_FillBottleJob;
		public static JobDef RM_DouseFireWithBucket;

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
