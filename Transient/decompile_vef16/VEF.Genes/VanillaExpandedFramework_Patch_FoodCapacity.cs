using HarmonyLib;
using RimWorld;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Patch_FoodCapacity
{
	[HarmonyPostfix]
	public static void FoodCapacity_Postfix(ref float __result, ref Need_Food __instance, ref Pawn ___pawn, ref float ___curLevelInt)
	{
		CachedPawnData pawnDataCache = PawnDataCache.GetPawnDataCache(___pawn);
		if (pawnDataCache != null)
		{
			__result *= pawnDataCache.percentChange * pawnDataCache.foodCapacityMult;
		}
	}
}
