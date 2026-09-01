using System;
using HarmonyLib;
using UnityEngine;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderNodeWorker), "ScaleFor")]
public static class VanillaExpandedFramework_PawnRenderNodeWorker_ScaleFor_Patch
{
	public struct PerThreadMiniCache
	{
		public Pawn pawn;

		public CachedPawnData cache;
	}

	[ThreadStatic]
	private static PerThreadMiniCache threadStaticCache;

	public static void Postfix(ref Vector3 __result, PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = parms.pawn;
		if (pawn == null)
		{
			return;
		}
		CachedPawnData cachedPawnData;
		if (CachedPawnDataExtensions.prepatched)
		{
			cachedPawnData = pawn.GetCachePrePatched();
		}
		else
		{
			if (threadStaticCache.pawn != pawn)
			{
				threadStaticCache.cache = pawn.GetCachePrePatched();
				threadStaticCache.pawn = pawn;
			}
			cachedPawnData = threadStaticCache.cache;
		}
		double num = cachedPawnData.vCosmeticScale.x;
		double num2 = cachedPawnData.vCosmeticScale.z;
		double num3 = __result.x;
		double num4 = __result.z;
		if (cachedPawnData.isHumanlike)
		{
			if (node is PawnRenderNode_Body)
			{
				__result.x = (float)(num3 * num);
				__result.z = (float)(num4 * num2);
			}
			else if (node is PawnRenderNode_Head)
			{
				double num5 = cachedPawnData.headRenderSize;
				__result.x = (float)(num3 * num5);
				__result.z = (float)(num4 * num5);
			}
		}
		else
		{
			__result.x = (float)(num3 * num);
			__result.z = (float)(num4 * num2);
		}
	}
}
