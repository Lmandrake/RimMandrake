using System;
using Verse;

namespace VEF.AestheticScaling;

public class PawnDataCache : DictCache<Pawn, CachedPawnData>
{
	public struct PerThreadMiniCache
	{
		public Pawn pawn;

		public CachedPawnData cache;
	}

	[ThreadStatic]
	private static PerThreadMiniCache threadStaticCache;

	public static CachedPawnData GetCacheUltraSpeed(Pawn pawn, bool canRefresh = true)
	{
		if (pawn == null)
		{
			return CachedPawnData.defaultCache;
		}
		if (threadStaticCache.pawn == pawn)
		{
			return threadStaticCache.cache;
		}
		threadStaticCache.cache = GetPawnDataCache(pawn, forceRefresh: false, canRefresh);
		threadStaticCache.pawn = pawn;
		return threadStaticCache.cache;
	}

	public static CachedPawnData GetPawnDataCache(Pawn pawn, bool forceRefresh = false, bool canRefresh = true)
	{
		if (pawn?.needs != null || pawn.Dead)
		{
			bool newEntry;
			CachedPawnData cache = DictCache<Pawn, CachedPawnData>.GetCache(pawn, out newEntry, forceRefresh, canRefresh);
			if (newEntry && cache != null && cache != CachedPawnData.defaultCache)
			{
				pawn.GetCachePrePatched() = cache;
			}
			return cache;
		}
		return CachedPawnData.defaultCache;
	}
}
