using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnRenderNode_Body), "GraphicFor")]
public static class PawnRenderNode_Body_GraphicFor_Patch
{
	[HarmonyPriority(100)]
	[HarmonyPostfix]
	public static void Postfix(PawnRenderNode_Body __instance, ref Pawn pawn, ref Graphic __result)
	{
		if (__result != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && !cache.IsTempCache && cache.isHumanlike)
			{
				BodyGraphics.CalculateBodyGraphicsForPawn(__instance, pawn, ref __result, cache);
			}
		}
	}
}
