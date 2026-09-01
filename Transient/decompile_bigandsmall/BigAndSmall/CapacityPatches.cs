using System;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class CapacityPatches
{
	[HarmonyPatch(typeof(PawnCapacityDef), "GetLabelFor", new Type[] { typeof(Pawn) })]
	[HarmonyPostfix]
	public static void GetLabelForPostfix(ref string __result, PawnCapacityDef __instance, Pawn pawn)
	{
		BSCache cachePrepatchedThreaded = pawn.GetCachePrepatchedThreaded();
		if (cachePrepatchedThreaded != null && cachePrepatchedThreaded.isMechanical)
		{
			__result = ((!GenText.NullOrEmpty(__instance.labelMechanoids)) ? __instance.labelMechanoids : __result);
		}
	}
}
