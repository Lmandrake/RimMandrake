using HarmonyLib;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Pawn_BodySize
{
	public struct BodySizeCache
	{
		public Pawn pawn;

		public CachedPawnData cache;

		public uint tick;
	}

	private static BodySizeCache sizeCache;

	public static void Postfix(ref float __result, Pawn __instance)
	{
		CachedPawnData cache;
		if (sizeCache.pawn != __instance || sizeCache.tick != CachedPawnDataSlowUpdate.Tick10)
		{
			sizeCache.cache = __instance.GetCachePrePatched();
			sizeCache.pawn = __instance;
			sizeCache.tick = CachedPawnDataSlowUpdate.Tick10;
			cache = sizeCache.cache;
		}
		else
		{
			cache = sizeCache.cache;
		}
		if (cache != null)
		{
			__result += cache.bodySizeOffset;
			if (__result < 0.05f)
			{
				__result = 0.05f;
			}
		}
	}
}
