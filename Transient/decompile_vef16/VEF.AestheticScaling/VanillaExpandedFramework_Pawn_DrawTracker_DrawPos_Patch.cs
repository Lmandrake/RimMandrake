using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AestheticScaling;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Pawn_DrawTracker_DrawPos_Patch
{
	public struct PGPRRCache
	{
		public Pawn pawn;

		public CachedPawnData cache;

		public bool doOffset;
	}

	[ThreadStatic]
	private static PGPRRCache threadStaticCache;

	public static bool skipOffset;

	[HarmonyPostfix]
	public static void Postfix(ref Vector3 __result, Pawn ___pawn)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Invalid comparison between Unknown and I4
		if (___pawn != null && !skipOffset)
		{
			if (threadStaticCache.pawn != ___pawn)
			{
				threadStaticCache.cache = ___pawn.GetCachePrePatched();
				threadStaticCache.pawn = ___pawn;
				threadStaticCache.doOffset = (int)PawnUtility.GetPosture(___pawn) == 0;
			}
			if (threadStaticCache.cache != null && threadStaticCache.doOffset)
			{
				__result.z += threadStaticCache.cache.renderPosOffset;
			}
		}
	}
}
