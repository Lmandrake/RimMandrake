using HarmonyLib;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Pawn_HealthScale
{
	[HarmonyPostfix]
	public static void HealthScale_Postfix(ref float __result, Pawn __instance)
	{
		CachedPawnData pawnDataCache = PawnDataCache.GetPawnDataCache(__instance);
		if (pawnDataCache != null)
		{
			__result *= pawnDataCache.healthMultiplier;
		}
	}
}
