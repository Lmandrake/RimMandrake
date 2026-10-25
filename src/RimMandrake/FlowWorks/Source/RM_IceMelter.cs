using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN (owner card 2026-10-25): "Should be a machine like a smelter where they can do that
	/// explicitly." On a RecipeDef done at the ice melter (Defs/Pits/ThingDefs/RM_CrushedIce.xml): each finished bill puts
	/// <see cref="unitsPerCraft"/> dL of <see cref="liquid"/> into the tanks on the bench's liquid net (touching it or hosed to
	/// it). A bill is not started without tank room for the whole craft; tank room lost mid-craft puts the water out at the
	/// bench (into water there, else a puddle), never lost.
	/// </summary>
	public class RM_MeltRecipeExtension : DefModExtension
	{
		public LiquidDef liquid;

		/// <summary>dL per craft; a crushed ice is the one notch its cut removed (RM_GroundClassMath.CrushedIceUnits,
		/// ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES).</summary>
		public int unitsPerCraft = RM_GroundClassMath.CrushedIceUnits;
	}

	public static class RM_IceMelter
	{
		/// <summary>State read (proof rows): dL a melter put into tanks, and dL it had to put out at the bench.</summary>
		public static long TankedUnits;

		public static long ReleasedUnits;

		/// <summary>State read (proof rows): heat loose melting crushed ice took out of rooms since load (positive = cooling;
		/// ICE_MELT_TAME_STACK_FLOOD). The melter itself is neutral: its heating bath pays the melt's heat.</summary>
		public static double CooledHeat;

		/// <summary>Proof read: <see cref="CooledHeat"/>, vanilla heat units, F1.</summary>
		public static string ProofMeltCooling()
		{
			return CooledHeat.ToString("F1", System.Globalization.CultureInfo.InvariantCulture);
		}

		/// <summary>Proof read (northstar/gravel_live.py GS_crushed_ice_melts_to_water): the world-release ledgers, dL,
		/// "spilled;inWater;nearby;tanked;released".</summary>
		public static string ProofMeltLedger()
		{
			return RM_LiquidSpill.SpilledUnits + ";" + RM_LiquidSpill.PlacedInWaterUnits + ";" + RM_LiquidSpill.PlacedNearbyUnits + ";" + TankedUnits + ";" + ReleasedUnits;
		}

		public static RM_MeltRecipeExtension ExtOf(Bill bill)
		{
			return bill?.recipe?.GetModExtension<RM_MeltRecipeExtension>();
		}

		/// <summary>The tanks that would take one craft's water now, or null (no tank, no room, or the feature off).</summary>
		public static List<(Building_LiquidTank tank, int units)> PlanFor(Bill bill)
		{
			RM_MeltRecipeExtension ext = ExtOf(bill);
			if (ext?.liquid == null || ext.unitsPerCraft <= 0 || !(bill.billStack?.billGiver is Thing bench) || !bench.Spawned)
			{
				return null;
			}
			return RM_LiquidNet.FillPlan(bench, ext.liquid, ext.unitsPerCraft);
		}
	}

	/// <summary>A melt bill waits for tank room for the whole craft (the work giver says why).</summary>
	[HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.ShouldDoNow))]
	[RimMandrake.Shared.PatchFeature("Ice and packed snow dig to crushed ice", typeof(RimMandrakeFlowWorksSettings), "iceDigEnabled")]
	public static class RM_Patch_IceMelterShouldDoNow
	{
		public static void Postfix(Bill_Production __instance, ref bool __result)
		{
			if (!__result || RM_IceMelter.ExtOf(__instance) == null)
			{
				return;
			}
			if (!RimMandrakeFlowWorksSettings.iceDigEnabled || RM_IceMelter.PlanFor(__instance) == null)
			{
				__result = false;
				JobFailReason.Is("No tank on this melter's liquid net with room for " + (RM_IceMelter.ExtOf(__instance).unitsPerCraft / RM_Volume.UnitsPerLitre).ToString("N0") + " L.");
			}
		}
	}

	/// <summary>A finished melt puts its water into the tanks (re-planned now: room may have gone while it worked); what no
	/// tank takes goes out at the bench.</summary>
	[HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.Notify_IterationCompleted))]
	[RimMandrake.Shared.PatchFeature("Ice and packed snow dig to crushed ice", typeof(RimMandrakeFlowWorksSettings), "iceDigEnabled")]
	public static class RM_Patch_IceMelterCompleted
	{
		public static void Postfix(Bill_Production __instance)
		{
			RM_MeltRecipeExtension ext = RM_IceMelter.ExtOf(__instance);
			if (ext?.liquid == null || ext.unitsPerCraft <= 0 || !(__instance.billStack?.billGiver is Thing bench) || bench.MapHeld == null)
			{
				return;
			}
			int units = ext.unitsPerCraft;
			int moved = 0;
			List<(Building_LiquidTank tank, int units)> plan = RM_IceMelter.PlanFor(__instance);
			if (plan != null)
			{
				LiquidDef water = ext.liquid;
				// the melt's water, held by the bench until a tank takes it (put back = still held, released below)
				RM_TransferLeg melt = RM_TransferLeg.World(k => true, k => true, k => true);
				RM_TransferLeg tanks = RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(water, k), (i, k) => plan[i].tank.TryAddLiquid(water, k), (i, k) => plan[i].tank.TryRemoveLiquid(k));
				if (RM_LiquidTransfer.Move(units, melt, tanks, out RM_MoveOutcome o) == units)
				{
					moved = units;
					foreach ((Building_LiquidTank tank, int units) p in plan) RM_LiquidNet.Credit(bench, p.tank, water, p.units, RimMandrake.FlowWorks.Hose.RM_HoseSettings.releaseTicks);   // credit site: ice melter
				}
				else
				{
					moved = o.Moved;   // a partial take stays in the tanks (uncredited); the rest goes out below
				}
			}
			RM_IceMelter.TankedUnits += moved;
			if (moved < units)
			{
				RM_IceMelter.ReleasedUnits += units - moved;
				RM_LiquidSpill.ReleaseHeld(bench.MapHeld, bench.InteractionCell.IsValid ? bench.InteractionCell : bench.PositionHeld, ext.liquid, units - moved);
			}
		}
	}
}
