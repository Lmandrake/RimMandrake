using System;
using System.Collections.Concurrent;

namespace VEF.AestheticScaling;

public abstract class DictCache<T, V> where V : ICacheable
{
	protected static readonly ConcurrentDictionary<T, V> JunkCache = new ConcurrentDictionary<T, V>();

	public static ConcurrentDictionary<T, V> Cache { get; set; } = new ConcurrentDictionary<T, V>();

	public static V GetCache(T key, bool forceRefresh = false, bool canRefresh = true)
	{
		bool newEntry;
		return GetCache(key, out newEntry, forceRefresh, canRefresh);
	}

	public static V GetCache(T key, out bool newEntry, bool forceRefresh = false, bool canRefresh = true)
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
		V val = (V)Activator.CreateInstance(typeof(V), key);
		if (canRefresh && val.RegenerateCache())
		{
			newEntry = true;
			Cache.TryAdd(key, val);
		}
		else
		{
			JunkCache[key] = val;
		}
		return val;
	}
}
