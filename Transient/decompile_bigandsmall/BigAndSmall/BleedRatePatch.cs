using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public class BleedRatePatch
{
	public static void Postfix(ref float __result, ref Pawn_HealthTracker __instance, ref Pawn ___pawn)
	{
		__result = SetBleedRate(__result, ___pawn);
	}

	public static float SetBleedRate(float __result, Pawn ___pawn)
	{
		if (__result > 0f && ___pawn?.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(___pawn);
			if (cache != null && cache.bleedRate == BSCache.BleedRateState.NoBleeding)
			{
				__result = 0f;
			}
		}
		return __result;
	}
}
