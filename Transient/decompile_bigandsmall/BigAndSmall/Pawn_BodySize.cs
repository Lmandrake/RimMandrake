using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class Pawn_BodySize
{
	public static void Postfix(ref float __result, Pawn __instance)
	{
		BSCache cachePrepatched = __instance.GetCachePrepatched();
		if (cachePrepatched != null)
		{
			__result += cachePrepatched.totalSizeOffset;
			if (__result < 0.05f)
			{
				__result = 0.05f;
			}
		}
	}
}
