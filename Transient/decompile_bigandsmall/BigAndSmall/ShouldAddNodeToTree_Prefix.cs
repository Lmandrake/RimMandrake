using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class ShouldAddNodeToTree_Prefix
{
	[HarmonyPrefix]
	[HarmonyPatch(typeof(PawnRenderTree), "ShouldAddNodeToTree")]
	[HarmonyPriority(800)]
	public static bool Prefix(PawnRenderNodeProperties props, PawnRenderTree __instance, ref bool __result)
	{
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Invalid comparison between Unknown and I4
		if (props != null && (int)props.pawnType == 1)
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(__instance.pawn);
			if (cacheUltraSpeed != null && cacheUltraSpeed.hideHumanlikeRenderNodes && !cacheUltraSpeed.IsTempCache && cacheUltraSpeed.isHumanlike)
			{
				__result = false;
				return false;
			}
		}
		return true;
	}
}
