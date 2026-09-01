using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public static class TaggedItemHelper
{
	public static T GetTaggedItem<T>(this HashSet<T> taggedItems, string tag) where T : class, ITaggedItem
	{
		if (taggedItems == null)
		{
			return null;
		}
		return taggedItems.FirstOrDefault((T ti) => ti.Tag == tag);
	}

	public static T GetTaggedItem<T>(this ExposableHashSet<T> taggedItems, string tag) where T : class, ITaggedItem
	{
		if (taggedItems == null)
		{
			return null;
		}
		return taggedItems.FirstOrDefault((T ti) => ti.Tag == tag);
	}

	public static TaggedColor GetTaggedColorOnDef(this Def def, string tag)
	{
		return TaggedPropManagerBase<TaggedColor>.GetDefTagItem(def, tag);
	}

	public static TaggedText GetTaggedPathOnDef(this Def def, string tag)
	{
		return TaggedPropManagerBase<TaggedText>.GetDefTagItem(def, tag);
	}

	public static TaggedColor GetColorByTag(this ILoadReferenceable target, string tag)
	{
		Faction val = (Faction)(object)((target is Faction) ? target : null);
		if (val != null)
		{
			return val.GetColorByTag(tag);
		}
		Thing val2 = (Thing)(object)((target is Thing) ? target : null);
		if (val2 != null)
		{
			return val2.GetColorByTag(tag);
		}
		return null;
	}

	public static TaggedText GetStringByTag(this ILoadReferenceable target, string tag, Func<TaggedText, bool> predicate = null)
	{
		Faction val = (Faction)(object)((target is Faction) ? target : null);
		object obj;
		if (val == null)
		{
			Thing val2 = (Thing)(object)((target is Thing) ? target : null);
			obj = ((val2 != null) ? val2.GetStringByTag(tag) : null);
		}
		else
		{
			obj = val.GetStringByTag(tag);
		}
		TaggedText taggedText = (TaggedText)obj;
		if (taggedText != null && predicate != null && !predicate(taggedText))
		{
			return null;
		}
		return taggedText;
	}

	private static TaggedColor GetColorByTag(this Faction faction, string tag)
	{
		if (TaggedPropManagerBase<TaggedColor>.TryGetTagItem((ILoadReferenceable)(object)faction, tag, out var item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedColor>.TryGetDefTagItem((Def)(object)faction?.def, tag, out item))
		{
			return item;
		}
		return null;
	}

	private static TaggedText GetStringByTag(this Faction faction, string tag)
	{
		if (GenText.NullOrEmpty(tag))
		{
			return null;
		}
		if (tag.Contains('+'))
		{
			string text = "";
			string[] array = tag.Split('+');
			foreach (string text2 in array)
			{
				TaggedText stringByTag = faction.GetStringByTag(text2);
				text = ((stringByTag == null) ? (text + text2) : (text + stringByTag.value));
			}
			return new TaggedText(tag, text);
		}
		if (TaggedPropManagerBase<TaggedText>.TryGetTagItem((ILoadReferenceable)(object)faction, tag, out var item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedText>.TryGetDefTagItem((Def)(object)faction?.def, tag, out item))
		{
			return item;
		}
		return null;
	}

	private static TaggedColor GetColorByTag(this Thing thing, string tag)
	{
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (TaggedPropManagerBase<TaggedColor>.TryGetTagItem((ILoadReferenceable)(object)thing, tag, out var item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedColor>.TryGetTagItem((ILoadReferenceable)(object)thing.Faction, tag, out item))
		{
			return item;
		}
		if (val != null && TaggedPropManagerBase<TaggedColor>.TryGetTagItem((ILoadReferenceable)(object)val.Ideo, tag, out item))
		{
			return item;
		}
		if (val != null && TaggedPropManagerBase<TaggedColor>.TryGetDefTagItem((Def)(object)val.kindDef, tag, out item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedColor>.TryGetDefTagItem((Def)(object)thing.def, tag, out item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedColor>.TryGetDefTagItem((Def)(object)thing.Faction?.def, tag, out item))
		{
			return item;
		}
		return null;
	}

	private static TaggedText GetStringByTag(this Thing thing, string tag)
	{
		if (GenText.NullOrEmpty(tag))
		{
			return null;
		}
		if (tag.Contains('+'))
		{
			string text = "";
			string[] array = tag.Split('+');
			foreach (string text2 in array)
			{
				TaggedText stringByTag = thing.GetStringByTag(text2);
				text = ((stringByTag == null) ? (text + text2) : (text + stringByTag.value));
			}
			return new TaggedText(tag, text);
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (TaggedPropManagerBase<TaggedText>.TryGetTagItem((ILoadReferenceable)(object)thing, tag, out var item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedText>.TryGetTagItem((ILoadReferenceable)(object)thing.Faction, tag, out item))
		{
			return item;
		}
		if (val != null && TaggedPropManagerBase<TaggedText>.TryGetTagItem((ILoadReferenceable)(object)val.Ideo, tag, out item))
		{
			return item;
		}
		if (val != null && TaggedPropManagerBase<TaggedText>.TryGetDefTagItem((Def)(object)val.kindDef, tag, out item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedText>.TryGetDefTagItem((Def)(object)thing.Faction?.def, tag, out item))
		{
			return item;
		}
		if (TaggedPropManagerBase<TaggedText>.TryGetDefTagItem((Def)(object)thing.def, tag, out item))
		{
			return item;
		}
		return null;
	}

	public static bool HasTagged(this Thing thing, string tag)
	{
		if (thing.GetColorByTag(tag) == null)
		{
			return thing.GetStringByTag(tag) != null;
		}
		return true;
	}

	public static bool HasTaggedDirect(this ILoadReferenceable thing, string tag)
	{
		if (!TaggedPropManagerBase<TaggedColor>.HasTag(thing, tag))
		{
			return TaggedPropManagerBase<TaggedText>.HasTag(thing, tag);
		}
		return true;
	}

	public static void SetColorTag(this ILoadReferenceable obj, string tag, Color color)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		TaggedPropManagerBase<TaggedColor>.SetTagItem(obj, new TaggedColor(tag, color));
	}

	public static void SetStringTag(this ILoadReferenceable obj, string tag, string value)
	{
		TaggedPropManagerBase<TaggedText>.SetTagItem(obj, new TaggedText(tag, value));
	}

	public static void RemoveColorTag(this ILoadReferenceable obj, string tag)
	{
		TaggedPropManagerBase<TaggedColor>.RemoveTagItem(obj, tag);
	}

	public static void RemoveStringTag(this ILoadReferenceable obj, string tag)
	{
		TaggedPropManagerBase<TaggedText>.RemoveTagItem(obj, tag);
	}
}
