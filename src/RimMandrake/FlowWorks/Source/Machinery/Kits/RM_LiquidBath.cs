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
	///             each completed bill draws <see cref="litresPerCraft"/> from that tank;
	///   terrains — OR a cell of one of these terrains within <see cref="terrainReach"/> of the bench's
	///             footprint (a pit dug beside the liquid's own ground). Ground is not drawn down.
	/// Without either, the bill is not started (the work giver's "cannot do" reason says what it needs).
	/// Mod Setting: RM_KitSettings.liquidBathRecipesEnabled (off: the bill runs dry and draws nothing).
	/// litresPerCraft is PROVISIONAL per recipe (1,000 L = the old 5 units; LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS).
	/// </summary>
	public class RM_RecipeLiquidExtension : DefModExtension
	{
		public List<LiquidDef> liquids = new List<LiquidDef>();
		public List<TerrainDef> terrains = new List<TerrainDef>();
		public float litresPerCraft = 1000f;

		/// <summary>The craft's draw in tank units (decilitres).</summary>
		public int UnitsPerCraft => RM_Volume.Units(litresPerCraft);
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
			if (litresPerCraft < 0f)
			{
				yield return "RM_RecipeLiquidExtension litresPerCraft is negative.";
			}
		}
	}

	public static class RM_LiquidBath
	{
		public static RM_RecipeLiquidExtension ExtOf(Bill bill)
		{
			return bill?.recipe?.GetModExtension<RM_RecipeLiquidExtension>();
		}

		/// <summary>Finds the liquid for one craft. Returns true when the bench has it; <paramref name="liquid"/> is the liquid to
		/// draw (its units may come from several tanks, L3 draw plan) with <paramref name="available"/> units of it on the bench's
		/// net, or null when the bench stands beside the liquid's own ground.</summary>
		public static bool TryFindSource(Thing bench, RM_RecipeLiquidExtension ext, out LiquidDef liquid, out int available)
		{
			liquid = null;
			available = 0;
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
				foreach (LiquidDef l in ext.liquids)
				{
					int have = RM_LiquidNet.Available(bench, l);
					if (have >= ext.UnitsPerCraft && have > 0)
					{
						liquid = l;
						available = have;
						return true;
					}
				}
			}
			return false;
		}

		/// <summary>What the bill's next craft owes right now (RM_LiquidBathMath.Pay over the bench's sources).</summary>
		public static RM_BathPay PayNow(Bill bill)
		{
			RM_RecipeLiquidExtension ext = ExtOf(bill);
			if (ext == null)
			{
				return RM_BathPay.NoNeed;
			}
			LiquidDef liquid = null;
			int have = 0;
			bool found = bill.billStack?.billGiver is Thing bench && TryFindSource(bench, ext, out liquid, out have);
			return RM_LiquidBathMath.Pay(RM_KitSettings.liquidBathRecipesEnabled, ext.UnitsPerCraft, found && liquid == null,
				found && liquid != null ? have : 0);
		}

		public static bool BenchHasLiquid(Bill bill)
		{
			RM_RecipeLiquidExtension ext = ExtOf(bill);
			if (ext == null || !RM_KitSettings.liquidBathRecipesEnabled)
			{
				return true;
			}
			return bill.billStack?.billGiver is Thing bench && TryFindSource(bench, ext, out _, out _);
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

	/// <summary>P3 (hose port step 5): the job doing a bath bill FAILS the moment its liquid is gone (tank drained or
	/// disconnected mid-craft), so a craft is never completed unpaid (RM_LiquidBathMath.Pay, selftested).</summary>
	[HarmonyPatch(typeof(JobDriver_DoBill), "MakeNewToils")]
	[RimMandrake.Shared.PatchFeature("Liquid bath recipes", typeof(RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings), "liquidBathRecipesEnabled")]
	public static class RM_Patch_LiquidBathFailWhenUnpaid
	{
		public static void Postfix(JobDriver_DoBill __instance)
		{
			JobDriver_DoBill d = __instance;
			d.FailOn(() =>
			{
				Bill bill = d.job?.bill;
				RM_RecipeLiquidExtension ext = RM_LiquidBath.ExtOf(bill);
				return ext != null && !RM_LiquidBathMath.MayKeepWorking(RM_LiquidBath.PayNow(bill));
			});
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
			if (ext == null || !RM_KitSettings.liquidBathRecipesEnabled || ext.UnitsPerCraft <= 0)
			{
				return;
			}
			if (__instance.billStack?.billGiver is Thing bench
				&& RM_LiquidBath.TryFindSource(bench, ext, out LiquidDef bathed, out _) && bathed != null)
			{
				// L1 (§4): the craft consumes the units (a sink); L3: drawn by the draw plan, emptiest tank first, split across tanks
				List<(Building_LiquidTank tank, int units)> plan = RM_LiquidNet.DrawPlan(bench, bathed, ext.UnitsPerCraft);
				if (plan == null)
				{
					return;
				}
				if (RM_LiquidTransfer.Move(ext.UnitsPerCraft, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanProvide(k), (i, k) => plan[i].tank.TryRemoveLiquid(k), (i, k) => plan[i].tank.TryAddLiquid(bathed, k)), RM_TransferLeg.Sink(null), out _) == ext.UnitsPerCraft)
				{
					// a craft is one plump pulse: the bath passes the hose release window as its cadence (design S7)
					foreach ((Building_LiquidTank tank, int units) p in plan) RM_LiquidNet.Credit(bench, p.tank, bathed, p.units, RimMandrake.FlowWorks.Hose.RM_HoseSettings.releaseTicks);   // credit site: bath
				}
			}
			else if (RM_LiquidBath.PayNow(__instance) == RM_BathPay.Unpaid)
			{
				// the job's fail condition should make this unreachable; never silent if it is reached
				Log.WarningOnce("[FlowWorks] a liquid-bath craft of " + __instance.recipe?.defName + " completed with no liquid to pay for it", 0x3B47A1);
			}
		}
	}
}
