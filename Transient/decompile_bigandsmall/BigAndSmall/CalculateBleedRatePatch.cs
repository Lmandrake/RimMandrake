using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(HediffSet), "CalculateBleedRate")]
public class CalculateBleedRatePatch
{
	public static void Postfix(ref float __result, ref HediffSet __instance)
	{
		if (!(__result > 0f))
		{
			return;
		}
		Pawn pawn = __instance.pawn;
		if (pawn?.needs == null)
		{
			return;
		}
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			if (cache.bleedRate == BSCache.BleedRateState.NoBleeding)
			{
				__result = 0f;
			}
			else if (cache.bleedRate == BSCache.BleedRateState.SlowBleeding)
			{
				__result /= 2f;
			}
			else if (cache.bleedRate == BSCache.BleedRateState.VerySlowBleeding)
			{
				__result /= 3f;
			}
			__result *= cache.bleedRateFactor;
		}
	}
}
