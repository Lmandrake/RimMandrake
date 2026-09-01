using System.Collections.Generic;
using Verse;

namespace VEF.Graphics;

public abstract class TaggedPropManagerBase<T> : GameComponent where T : class, ITaggedItem
{
	public static TaggedPropManagerBase<T> instance = null;

	private static readonly Dictionary<Def, HashSet<T>> taggedDefItems = new Dictionary<Def, HashSet<T>>();

	private Dictionary<ILoadReferenceable, ExposableHashSet<T>> taggedItems = new Dictionary<ILoadReferenceable, ExposableHashSet<T>>();

	private List<ILoadReferenceable> taggedItemsKeys;

	private List<ExposableHashSet<T>> taggedItemsValues;

	private static Dictionary<ILoadReferenceable, ExposableHashSet<T>> TaggedItems => instance.taggedItems;

	public TaggedPropManagerBase(Game game)
	{
		instance = this;
	}

	public static bool TryGetTagItem(ILoadReferenceable obj, string tag, out T item)
	{
		return (item = GetTagItem(obj, tag)) != null;
	}

	public static bool TryGetDefTagItem(Def def, string tag, out T item)
	{
		return (item = GetDefTagItem(def, tag)) != null;
	}

	public static void SetTagItem(ILoadReferenceable obj, T item)
	{
		if (obj == null)
		{
			return;
		}
		if (TaggedItems.TryGetValue(obj, out var value))
		{
			T val = value.FirstOrDefault((T ti) => ti.Tag == item.Tag);
			if (val != null)
			{
				value.Remove(val);
			}
			value.Add(item);
		}
		else
		{
			TaggedItems[obj] = new ExposableHashSet<T>(new _003C_003Ez__ReadOnlySingleElementList<T>(item));
		}
	}

	public static void RemoveTagItem(ILoadReferenceable obj, string tag)
	{
		if (obj != null && TaggedItems.TryGetValue(obj, out var value))
		{
			T val = value.FirstOrDefault((T ti) => ti.Tag == tag);
			if (val != null)
			{
				value.Remove(val);
			}
		}
	}

	public static T GetTagItem(ILoadReferenceable obj, string tag)
	{
		if (obj == null)
		{
			return null;
		}
		if (TaggedItems.TryGetValue(obj, out var value))
		{
			return value.GetTaggedItem(tag);
		}
		return null;
	}

	public static T GetDefTagItem(Def def, string tag)
	{
		if (def == null)
		{
			return null;
		}
		if (taggedDefItems.TryGetValue(def, out var value))
		{
			return value.GetTaggedItem(tag);
		}
		HashSet<T> hashSet = new HashSet<T>();
		foreach (TaggedDefProperties modExtension in def.GetModExtensions<TaggedDefProperties>())
		{
			List<T> other = modExtension.GetTaggedItems<T>();
			hashSet.UnionWith(other);
		}
		taggedDefItems[def] = hashSet;
		return hashSet.GetTaggedItem(tag);
	}

	public static bool HasTag(ILoadReferenceable obj, string tag)
	{
		return GetTagItem(obj, tag) != null;
	}

	public static bool HasDefTag(Def def, string tag)
	{
		return GetDefTagItem(def, tag) != null;
	}

	public override void ExposeData()
	{
		((GameComponent)this).ExposeData();
		Scribe_Collections.Look<ILoadReferenceable, ExposableHashSet<T>>(ref taggedItems, "taggedItems", (LookMode)3, (LookMode)2, ref taggedItemsKeys, ref taggedItemsValues, true, false, false);
	}
}
