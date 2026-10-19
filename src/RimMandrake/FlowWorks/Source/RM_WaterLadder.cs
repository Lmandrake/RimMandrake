using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD = rebuild plan P14 (design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md;
	/// engine doc design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md §3 Option B2, owner R10: ONE kind of water).
	///
	/// THE one ladder of wet-square looks by TRUE metres of water, the same for a lake, a pond, a canal and a pit. Both
	/// writers read it: the lake drawdown (RM_LiquidStock.StagePond → RM_PondDepthMath.StageForExact →
	/// RM_MapComponent_Excavation.PondStageTerrain) and the dug-water staging (RM_MapComponent_Excavation.ApplyFillTerrain →
	/// FluidDef.WetTerrainForBand). Verse-free so Source/SelfTest/ compiles THIS file; the defs are resolved by name in
	/// RM_WaterLadderDefs.
	/// <code>
	/// rung         water            freshwater terrain (vanilla water family, base layer)
	/// Dry          0                (none: the dry floor, RM_Channel_* by depth or RM_Lakebed_* by bed)
	/// VeryShallow  under 25 cm      RM_WaterVeryShallow, a damp film thinner than the silt (owner R2, VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST)
	/// Thin         about 0.5 m      RM_WaterThin
	/// Shallow      about 1 m        WaterShallow
	/// ChestDeep    about 1.5 m      RM_WaterChestDeepStill (vanilla WaterChestDeepBase-family affordances, GPT finding #2)
	/// Deep         2 m and deeper   WaterDeep (enterable by the swim grid, R12; def identity kept for roads and mods)
	/// </code>
	/// Bands are RM_LevelSolve.LookBand's (the band edges sit halfway between rungs: 0.25 / 0.75 / 1.25 / 1.75 m). Freshwater
	/// is RM_Fluid_Water's ladder (FluidDef.freshwaterLadder); every other liquid keeps its own fill tiers and water-body type.
	/// </summary>
	public static class RM_WaterLadder
	{
		public enum Rung
		{
			Dry = 0,
			VeryShallow = 1,
			Thin = 2,
			Shallow = 3,
			ChestDeep = 4,
			Deep = 5,
		}

		public const int RungCount = 6;

		/// <summary>The freshwater table, indexed by rung. Read by both writers through <see cref="FreshwaterDefName"/>.</summary>
		private static readonly string[] FreshwaterDefNames =
		{
			null,
			"RM_WaterVeryShallow",
			"RM_WaterThin",
			"WaterShallow",
			"RM_WaterChestDeepStill",
			"WaterDeep",
		};

		/// <summary>The freshwater terrain defName for <paramref name="rung"/>, null for Dry.</summary>
		public static string FreshwaterDefName(Rung rung)
		{
			int k = (int)rung;
			return k < 0 || k >= RungCount ? null : FreshwaterDefNames[k];
		}

		/// <summary>The rung for <paramref name="waterDl"/> decilitres of water standing in one square.</summary>
		public static Rung RungForDl(long waterDl)
		{
			return (Rung)RM_LevelSolve.LookBand(waterDl);
		}

		/// <summary>The rung for <paramref name="metres"/> of water standing in one square.</summary>
		public static Rung RungForMetres(double metres)
		{
			return RungForDl((long)Math.Round(metres / RM_LevelSolve.MetresPerUnit));
		}

		/// <summary>The pond stage that shows <paramref name="rung"/> on a drawn-down natural square (the pond's own original
		/// terrain and the dry stages are decided by RM_PondDepthMath, not by depth alone).</summary>
		public static RM_PondDepthMath.Stage PondStageOf(Rung rung)
		{
			switch (rung)
			{
				case Rung.Dry: return RM_PondDepthMath.Stage.Mud;
				case Rung.VeryShallow:
				case Rung.Thin: return RM_PondDepthMath.Stage.Thin;
				case Rung.Shallow: return RM_PondDepthMath.Stage.Shallow;
				case Rung.ChestDeep: return RM_PondDepthMath.Stage.ChestDeep;
				default: return RM_PondDepthMath.Stage.Deep;
			}
		}

		/// <summary>The rung a wet pond stage shows (Dry for Original/Mud/Lakebed: those are not depth rungs).</summary>
		public static Rung RungOfPondStage(RM_PondDepthMath.Stage stage)
		{
			switch (stage)
			{
				case RM_PondDepthMath.Stage.Thin: return Rung.Thin;
				case RM_PondDepthMath.Stage.Shallow: return Rung.Shallow;
				case RM_PondDepthMath.Stage.ChestDeep: return Rung.ChestDeep;
				case RM_PondDepthMath.Stage.Deep: return Rung.Deep;
				default: return Rung.Dry;
			}
		}
	}
}
