using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class RenderingPatches
{
	private static readonly float lifestageFactor = 1.5f;

	[HarmonyPatch(typeof(PawnRenderNodeWorker), "ScaleFor")]
	[HarmonyPostfix]
	public static void ScaleForPatch(ref Vector3 __result, PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = parms.pawn;
		if (pawn == null)
		{
			return;
		}
		BSCache cachePrepatchedThreaded = pawn.GetCachePrepatchedThreaded();
		if (cachePrepatchedThreaded.approximatelyNoChange)
		{
			return;
		}
		double num = cachePrepatchedThreaded.bodyRenderSize;
		double num2 = __result.x;
		double num3 = __result.z;
		if (node.parent == null || node.parent.props.tagDef != BSDefs.Root)
		{
			return;
		}
		if (cachePrepatchedThreaded.isHumanlike)
		{
			if (node is PawnRenderNode_Body)
			{
				__result.x = (float)(num2 * num);
				__result.z = (float)(num3 * num);
			}
			else if (node is PawnRenderNode_Head)
			{
				double num4 = cachePrepatchedThreaded.headRenderSize;
				__result.x = (float)(num2 * num4);
				__result.z = (float)(num3 * num4);
			}
			else if (node is PawnRenderNode_HAnimalPart)
			{
				__result.x = (float)(num2 * num);
				__result.z = (float)(num3 * num);
			}
		}
		else
		{
			__result.x = (float)(num2 * num);
			__result.z = (float)(num3 * num);
		}
	}
}
