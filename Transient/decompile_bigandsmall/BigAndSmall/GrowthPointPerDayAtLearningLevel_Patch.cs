using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn_AgeTracker), "GrowthPointsPerDayAtLearningLevel")]
public static class GrowthPointPerDayAtLearningLevel_Patch
{
	public static void Postfix(ref float __result, Pawn ___pawn)
	{
		HumanoidPawnScaler.GetCache(___pawn);
		BSCache cache = HumanoidPawnScaler.GetCache(___pawn);
		if (cache != null)
		{
			__result *= cache.growthPointGain;
		}
	}
}
