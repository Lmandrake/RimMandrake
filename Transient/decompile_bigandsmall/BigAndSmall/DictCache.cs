using System;
using System.Collections.Concurrent;

namespace BigAndSmall;

/// <summary>
/// A quick method for making a cache without having to rewrite the same verbose code over and over.
/// </summary>
/// <typeparam name="T">The value you want to act as the key of the dictionary</typeparam>
/// <typeparam name="V">A class whcih implements the ICachable Interface</typeparam>
public abstract class DictCache<T, V> where V : ICacheable
{
	protected static readonly ConcurrentDictionary<T, V> JunkCache = new ConcurrentDictionary<T, V>();

	public static ConcurrentDictionary<T, V> Cache { get; set; } = new ConcurrentDictionary<T, V>();

	/// <summary>
	///
	/// </summary>
	/// <param name="key"></param>
	/// <param name="forceRefresh"></param>
	/// <param name="canRegenerate">The Cache will not be regenerated, if one does not exist it will simply return default values.</param>
	/// <returns></returns>
	protected static V GetCacheInner(T key, out bool newEntry, bool forceRefresh = false, bool canRegenerate = true)
	{
		newEntry = false;
		if (key == null)
		{
			return default(V);
		}
		if (Cache.TryGetValue(key, out var value))
		{
			if (forceRefresh)
			{
				value.RegenerateCache();
				return value;
			}
			return value;
		}
		if (!forceRefresh && JunkCache.TryGetValue(key, out var value2))
		{
			return value2;
		}
		newEntry = true;
		V val = (V)Activator.CreateInstance(typeof(V), key);
		if (canRegenerate)
		{
			if (!val.RegenerateCache() && Cache.ContainsKey(key))
			{
				return Cache[key];
			}
			Cache[key] = val;
			return val;
		}
		JunkCache[key] = val;
		return val;
	}
}
