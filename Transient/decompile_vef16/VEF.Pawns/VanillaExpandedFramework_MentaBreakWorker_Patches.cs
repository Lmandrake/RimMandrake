using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using VEF.Genes;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch]
public static class VanillaExpandedFramework_MentaBreakWorker_Patches
{
	[HarmonyPatch(typeof(MentalBreakWorker), "CommonalityFor")]
	[HarmonyPostfix]
	public static void CommonalityFor_PostFix(ref float __result, MentalBreakWorker __instance, Pawn pawn)
	{
		if (pawn?.genes == null || __instance.def.mentalState != VEFDefOf.Binging_Food)
		{
			return;
		}
		IEnumerable<float> enumerable = from x in pawn.genes.GetActiveGeneExtensions()
			where x.foodBingeMentalBreakSelectionChanceFactor != 1f
			select x.foodBingeMentalBreakSelectionChanceFactor;
		if (!enumerable.Any())
		{
			return;
		}
		foreach (float item in enumerable)
		{
			__result *= item;
		}
	}

	[HarmonyPatch(typeof(MentalBreakWorker), "BreakCanOccur")]
	[HarmonyPostfix]
	public static void BreakCanOccur_PostFix(ref bool __result, MentalBreakWorker __instance, Pawn pawn)
	{
		if (pawn?.genes != null && __instance.def.mentalState != VEFDefOf.Binging_Food && (from x in pawn.genes.GetActiveGeneExtensions()
			where x.foodBingeMentalBreakSelectionChanceFactor != 1f
			select x.foodBingeMentalBreakSelectionChanceFactor).Sum((float x) => x) > 20f)
		{
			__result = false;
		}
	}
}
