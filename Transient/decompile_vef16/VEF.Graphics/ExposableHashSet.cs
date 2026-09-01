using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Graphics;

public class ExposableHashSet<T> : IExposable
{
	public HashSet<T> items = new HashSet<T>();

	private List<T> iExposableItems = new List<T>();

	public int Count => items.Count;

	public ExposableHashSet()
	{
	}

	public ExposableHashSet(IEnumerable<T> items)
	{
		this.items = items.ToHashSet();
	}

	public void ExposeData()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Invalid comparison between Unknown and I4
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Invalid comparison between Unknown and I4
		HashSet<T> hashSet;
		if ((int)Scribe.mode == 1)
		{
			hashSet = items;
			List<T> list = new List<T>(hashSet.Count);
			list.AddRange(hashSet);
			iExposableItems = list;
		}
		Scribe_Collections.Look<T>(ref iExposableItems, "items", (LookMode)2, Array.Empty<object>());
		if ((int)Scribe.mode != 4)
		{
			return;
		}
		hashSet = new HashSet<T>();
		foreach (T iExposableItem in iExposableItems)
		{
			hashSet.Add(iExposableItem);
		}
		items = hashSet;
	}

	public void Add(T item)
	{
		items.Add(item);
	}

	public bool Remove(T item)
	{
		return items.Remove(item);
	}

	public bool Contains(T item)
	{
		return items.Contains(item);
	}

	public bool TryGetValue(T item, out T value)
	{
		return items.TryGetValue(item, out value);
	}

	public T FirstOrDefault(Func<T, bool> predicate)
	{
		return items.FirstOrDefault(predicate);
	}
}
