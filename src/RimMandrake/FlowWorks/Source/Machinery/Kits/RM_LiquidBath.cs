using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// A bill that is done IN a liquid (GELATINOUSSLIME_PIT_SOLVENT_1: the slime pit renders toxic or
	/// indigestible food safe; any future soak, brine cure or solvent wash). Put on a RecipeDef:
	///   liquids — any of these LiquidDefs in a tank on the bench's liquid net (touching it or hosed to it);
	///             each completed bill draws <see cref="unitsPerCraft"/> from that tank;
	///   terrains — OR a cell of one of these terrains within <see cref="terrainReach"/> of the bench's
	///             footprint (a pit dug beside the liquid's own ground). Ground is not drawn down.
	/// Without either, the bill is not started (the work giver's "cannot do" reason says what it needs).
	/// Mod Setting: RM_KitSettings.liquidBathRecipesEnabled (off: the bill runs dry and draws nothing).
	/// unitsPerCraft is PROVISIONAL per recipe.
	/// </summary>
	public class RM_RecipeLiquidExtension : DefModExtension
	{
		public List<LiquidDef> liquids = new List<LiquidDef>();
		public List<TerrainDef> terrains = new List<TerrainDef>();
		public int unitsPerCraft = 5;
		public int terrainReach = 1;

		/// <summary>What the bill needs, for the fail reason: "green slime".</summary>
		public string needLabel;

		public string NeedLabel
		{
			get
			{
				if (!needLabel.NullOrEmpty())
				{
					return needLabel;
				}
				if (!liquids.NullOrEmpty())
				{
					return liquids[0].label;
				}
				return terrains.NullOrEmpty() ? "?" : terrains[0].label;
			}
		}

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string e in base.ConfigErrors())
			{
				yield return e;
			}
			if (liquids.NullOrEmpty() && terrains.NullOrEmpty())
			{
				yield return "RM_RecipeLiquidExtension names no liquids and no terrains: the bill could never run.";
			}
			if (unitsPerCraft < 0)
			{
				yield return "RM_RecipeLiquidExtension unitsPerCraft is negative.";
			}
		}
	}

	public static class RM_LiquidBath
	{
		public static RM_RecipeLiquidExtension ExtOf(Bill bill)
		{
			return bill?.recipe?.GetModExtension<RM_RecipeLiquidExtension>();
		}

		/// <summary>Finds the liquid for one craft. Returns true when the bench has it; <paramref name="tank"/>
		/// is the tank to draw from, or null when the bench stands beside the liquid's own ground.</summary>
		public static bool TryFindSource(Thing bench, RM_RecipeLiquidExtension ext, out Building_LiquidTank tank)
		{
			tank = null;
			if (bench?.Map == null || ext == null)
			{
				return false;
			}
			Map map = bench.Map;
			if (!ext.terrains.NullOrEmpty())
			{
				CellRect rect = bench.OccupiedRect().ExpandedBy(ext.terrainReach);
				foreach (IntVec3 c in rect)
				{
					if (c.InBounds(map) && ext.terrains.Contains(c.GetTerrain(map)))
					{
						return true;
					}
				}
			}
			if (!ext.liquids.NullOrEmpty())
			{
				foreach (Building_LiquidTank t in RM_LiquidNet.TanksFor(bench))
				{
					if (!t.Empty && ext.liquids.Contains(t.storedLiquid) && t.storedUnits >= ext.unitsPerCraft)
					{
						tank = t;
						return true;
					}
				}
			}
			return false;
		}

		public static bool BenchHasLiquid(Bill bill)
		{
			RM_RecipeLiquidExtension ext = ExtOf(bill);
			if (ext == null || !RM_KitSettings.liquidBathRecipesEnabled)
			{
				return true;
			}
			return bill.billStack?.billGiver is Thing bench && TryFindSource(bench, ext, out _);
		}
	}

	/// <summary>No liquid to hand: the bill is not started now, and the "cannot do" reason says what it needs.</summary>
	[HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.ShouldDoNow))]
	[RimMandrake.Shared.PatchFeature("Liquid bath recipes", typeof(RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings), "liquidBathRecipesEnabled")]
	public static class RM_Patch_LiquidBathShouldDoNow
	{
		public static void Postfix(Bill_Production __instance, ref bool __result)
		{
			if (!__result || RM_LiquidBath.BenchHasLiquid(__instance))
			{
				return;
			}
			__result = false;
			JobFailReason.Is("RMFlow_BathNeedsLiquid".Translate(RM_LiquidBath.ExtOf(__instance).NeedLabel));
		}
	}

	/// <summary>A finished bill draws its units from the tank it used (ground is not drawn down).</summary>
	[HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.Notify_IterationCompleted))]
	[RimMandrake.Shared.PatchFeature("Liquid bath recipes", typeof(RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings), "liquidBathRecipesEnabled")]
	public static class RM_Patch_LiquidBathCompleted
	{
		public static void Postfix(Bill_Production __instance)
		{
			RM_RecipeLiquidExtension ext = RM_LiquidBath.ExtOf(__instance);
			if (ext == null || !RM_KitSettings.liquidBathRecipesEnabled || ext.unitsPerCraft <= 0)
			{
				return;
			}
			if (__instance.billStack?.billGiver is Thing bench
				&& RM_LiquidBath.TryFindSource(bench, ext, out Building_LiquidTank tank) && tank != null)
			{
				tank.TryRemoveLiquid(ext.unitsPerCraft);
			}
		}
	}
}
