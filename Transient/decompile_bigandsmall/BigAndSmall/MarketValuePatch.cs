using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class MarketValuePatch
{
	[HarmonyPostfix]
	public static void MarketValuePostfix(Thing __instance, ref float __result)
	{
		if (!WealthWatcher_ForceRecount_Patch.raidWealthActive)
		{
			return;
		}
		Pawn val = (Pawn)(object)((__instance is Pawn) ? __instance : null);
		if (val != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(val);
			if (cache != null)
			{
				__result *= cache.raidWealthMultiplier;
				__result += cache.raidWealthOffset;
			}
		}
	}
}
