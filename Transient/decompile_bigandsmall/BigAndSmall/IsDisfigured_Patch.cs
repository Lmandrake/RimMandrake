using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(RelationsUtility))]
[HarmonyPatch("IsDisfigured")]
public static class IsDisfigured_Patch
{
	[HarmonyPostfix]
	public static void RemoveDisfigurement(ref bool __result, Pawn pawn)
	{
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null && cache.preventDisfigurement)
		{
			__result = false;
		}
	}
}
