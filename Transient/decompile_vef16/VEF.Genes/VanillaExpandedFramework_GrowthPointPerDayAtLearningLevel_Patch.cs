using HarmonyLib;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_AgeTracker), "GrowthPointsPerDayAtLearningLevel")]
public static class VanillaExpandedFramework_GrowthPointPerDayAtLearningLevel_Patch
{
	public static void Postfix(ref float __result, Pawn ___pawn)
	{
		CachedPawnData pawnDataCache = PawnDataCache.GetPawnDataCache(___pawn);
		if (pawnDataCache != null)
		{
			__result *= pawnDataCache.growthPointMultiplier;
		}
	}
}
