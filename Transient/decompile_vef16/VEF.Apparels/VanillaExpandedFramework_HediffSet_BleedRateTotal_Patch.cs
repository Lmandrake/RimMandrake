using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_HediffSet_BleedRateTotal_Patch
{
	public static void Postfix(ref float __result, HediffSet __instance)
	{
		if (!(__result > 0f) || __instance.pawn == null)
		{
			return;
		}
		Pawn_ApparelTracker apparel = __instance.pawn.apparel;
		if (!PreventsBleeding<Apparel>((apparel != null) ? apparel.WornApparel : null))
		{
			Pawn_EquipmentTracker equipment = __instance.pawn.equipment;
			if (!PreventsBleeding<ThingWithComps>((equipment != null) ? equipment.AllEquipmentListForReading : null))
			{
				return;
			}
		}
		__result = 0f;
	}

	private static bool PreventsBleeding<T>(List<T> list) where T : Thing
	{
		if (list == null)
		{
			return false;
		}
		foreach (T item in list)
		{
			ApparelExtension modExtension = ((Def)((Thing)item).def).GetModExtension<ApparelExtension>();
			if (modExtension != null && modExtension.preventBleeding)
			{
				return true;
			}
		}
		return false;
	}
}
