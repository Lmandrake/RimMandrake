using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class PawnRenderNode_Head_Patches
{
	public static class HeadGraphics
	{
		public static void CalculateHeadGraphicsForPawn(PawnRenderNode_Head headNode, ref Graphic __result, BSCache cache)
		{
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Invalid comparison between Unknown and I4
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			if (cache.hideHead)
			{
				__result = GraphicsHelper.GetBlankMaterial();
				return;
			}
			if ((int)((PawnRenderNode)headNode).tree.pawn.Drawer.renderer.CurRotDrawMode == 4)
			{
				if (cache.headDessicatedGraphicPath != null)
				{
					string headDessicatedGraphicPath = cache.headDessicatedGraphicPath;
					__result = GraphicsHelper.TryGetCustomGraphics((PawnRenderNode)(object)headNode, headDessicatedGraphicPath, __result.color, __result.colorTwo, Color.white, __result.drawSize, cache.headMaterial);
					return;
				}
				CustomMaterial headMaterial = cache.headMaterial;
				if (headMaterial == null || !headMaterial.overrideDesiccated)
				{
					return;
				}
			}
			string headGraphicPath = cache.headGraphicPath;
			if (headGraphicPath != null)
			{
				Graphic val = GraphicsHelper.TryGetCustomGraphics((PawnRenderNode)(object)headNode, headGraphicPath, __result.color, __result.colorTwo, Color.white, __result.drawSize, cache.headMaterial);
				if (val != null)
				{
					__result = val;
				}
				else
				{
					Log.Warning($"{((PawnRenderNode)(headNode?)).tree?.pawn}  requested headGraphicPath, but TryGetCustomGraphics returned null");
				}
			}
		}
	}

	[HarmonyPatch(typeof(PawnRenderNode_Head), "GraphicFor")]
	[HarmonyPostfix]
	public static void PawnRenderNode_Head_GraphicFor_Patch(PawnRenderNode_Head __instance, Pawn pawn, ref Graphic __result)
	{
		if (__result != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && !cache.IsTempCache && cache.isHumanlike)
			{
				HeadGraphics.CalculateHeadGraphicsForPawn(__instance, ref __result, cache);
			}
		}
	}
}
