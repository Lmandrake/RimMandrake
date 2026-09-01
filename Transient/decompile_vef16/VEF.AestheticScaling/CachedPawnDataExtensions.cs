using System;
using System.Runtime.CompilerServices;
using Prepatcher;
using Verse;

namespace VEF.AestheticScaling;

public static class CachedPawnDataExtensions
{
	public static bool prepatched;

	[ThreadStatic]
	private static CachedPawnData _placeholderCache;

	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	[PrepatcherField]
	[ValueInitializer("GetDefaultCache")]
	public static ref CachedPawnData GetCachePrePatched(this Pawn pawn)
	{
		_placeholderCache = PawnDataCache.GetCacheUltraSpeed(pawn, canRefresh: false);
		return ref _placeholderCache;
	}

	private static CachedPawnData GetDefaultCache()
	{
		return CachedPawnData.GetDefaultCache();
	}
}
