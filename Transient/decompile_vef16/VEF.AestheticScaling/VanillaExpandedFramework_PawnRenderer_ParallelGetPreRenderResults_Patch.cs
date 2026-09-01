using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.AestheticScaling;

[HarmonyPatch(typeof(PawnRenderer), "ParallelGetPreRenderResults")]
public static class VanillaExpandedFramework_PawnRenderer_ParallelGetPreRenderResults_Patch
{
	public static void Prefix(PawnRenderer __instance, ref Vector3 drawLoc, Rot4 rotOverride, bool neverAimWeapon, ref bool disableCache, Pawn ___pawn)
	{
		if (!disableCache)
		{
			disableCache = VFEGlobal.settings.disableCaching;
			CachedPawnData cacheUltraSpeed = PawnDataCache.GetCacheUltraSpeed(___pawn, canRefresh: false);
			if (cacheUltraSpeed != null && (cacheUltraSpeed.bodySizeOffset > 0f || cacheUltraSpeed.percentChange > 1f || cacheUltraSpeed.renderCacheOff))
			{
				disableCache = true;
			}
		}
	}
}
