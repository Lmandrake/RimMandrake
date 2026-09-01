using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class ButcheringHarmonyPatches
{
	[HarmonyPostfix]
	[HarmonyPatch(typeof(Pawn), "ButcherProducts")]
	public static void ButcherProductsPostfix(Pawn __instance, ref IEnumerable<Thing> __result, Pawn butcher, float efficiency)
	{
		if (__result == null || __instance == null)
		{
			return;
		}
		List<PawnExtension> allPawnExtensions = __instance.GetAllPawnExtensions();
		ThingDef val = GenCollection.FirstOrDefault<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.meatOverride != null))?.meatOverride;
		List<Thing> list = __result.ToList();
		if (val != null)
		{
			ThingDef val2 = __instance.RaceProps?.meatDef;
			for (int i = 0; i < list.Count; i++)
			{
				Thing val3 = list[i];
				if (val3?.def == val2)
				{
					int stackCount = val3.stackCount;
					list[i] = ThingMaker.MakeThing(val, (ThingDef)null);
					list[i].stackCount = stackCount;
				}
			}
		}
		foreach (PawnExtension item in allPawnExtensions)
		{
			if (item.butcherProducts == null)
			{
				continue;
			}
			foreach (CustomButcherProduct butcherProduct in item.butcherProducts)
			{
				if (butcherProduct.TryMake(butcher, __instance, out var thing))
				{
					list.Add(thing);
				}
			}
		}
		__result = list;
	}
}
