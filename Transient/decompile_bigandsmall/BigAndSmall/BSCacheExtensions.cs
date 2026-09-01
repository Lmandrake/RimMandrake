using System;
using System.Runtime.CompilerServices;
using Prepatcher;
using Verse;

namespace BigAndSmall;

public static class BSCacheExtensions
{
	public static bool prepatched;

	[ThreadStatic]
	private static BSCache _placeholderCache;

	[ThreadStatic]
	private static BSCache _placeholderCacheThreaded;

	private static BSCache GetDefaultCache()
	{
		return BSCache.GetDefaultCache();
	}

	/// <summary>
	/// Gets the cache in the fastest way possible. Can generate a new cache if needed on creation but never refreshes it.
	/// </summary>
	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	[PrepatcherField]
	[ValueInitializer("GetDefaultCache")]
	public static ref BSCache GetCachePrepatched(this Pawn pawn)
	{
		_placeholderCache = HumanoidPawnScaler.GetCacheUltraSpeed(pawn, canRegenerate: true);
		return ref _placeholderCache;
	}

	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	public static BSCache GetCache(this Pawn pawn)
	{
		return pawn.GetCachePrepatched();
	}

	/// <summary>
	/// The threaded version of GetCache is for use on rendering threads where we DON'T want to regenerate the cache.
	/// </summary>
	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	[PrepatcherField]
	[ValueInitializer("GetDefaultCache")]
	public static ref BSCache GetCachePrepatchedThreaded(this Pawn pawn)
	{
		_placeholderCacheThreaded = HumanoidPawnScaler.GetCacheUltraSpeed(pawn);
		return ref _placeholderCacheThreaded;
	}
}
