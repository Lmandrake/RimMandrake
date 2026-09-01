using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using Verse;

namespace BigAndSmall;

public class ItemRestrictionDef : Def
{
	public List<string> restrictedTags;

	[CompilerGenerated]
	private static HashSet<string> _003CAllRestrictedTags_003Ek__BackingField;

	public static HashSet<string> AllRestrictedTags
	{
		get
		{
			if (_003CAllRestrictedTags_003Ek__BackingField != null)
			{
				return _003CAllRestrictedTags_003Ek__BackingField;
			}
			HashSet<string> hashSet = new HashSet<string>();
			foreach (string item in DefDatabase<ItemRestrictionDef>.AllDefsListForReading.Where((ItemRestrictionDef x) => x.restrictedTags != null).SelectMany((ItemRestrictionDef x) => x.restrictedTags).Distinct())
			{
				hashSet.Add(item);
			}
			return _003CAllRestrictedTags_003Ek__BackingField = hashSet;
		}
	}

	public static List<string> RestrictedTags(IEnumerable<string> tags)
	{
		if (tags == null || !tags.Any())
		{
			return new List<string>();
		}
		return tags.Where(AllRestrictedTags.Contains).ToList();
	}
}
