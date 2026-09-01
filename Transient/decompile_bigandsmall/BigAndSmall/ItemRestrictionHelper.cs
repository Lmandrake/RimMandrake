using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class ItemRestrictionHelper
{
	public static bool HasAllRequiredTags(List<string> requiredTags, List<string> pawnTags)
	{
		if (requiredTags == null || requiredTags.Count == 0)
		{
			return true;
		}
		if (GenList.NullOrEmpty<string>((IList<string>)pawnTags))
		{
			return false;
		}
		return requiredTags.All(pawnTags.Contains);
	}

	public static bool HasRequiredApparelTags(this ApparelProperties apparel, List<string> pawnTags)
	{
		List<string> tags = apparel.tags;
		if (tags != null)
		{
			List<string> list = ItemRestrictionDef.RestrictedTags(tags);
			if (list != null && !HasAllRequiredTags(list, pawnTags))
			{
				return false;
			}
		}
		return true;
	}

	public static bool HasRequiredWeaponTags(this ThingDef thingDef, List<string> pawnTags)
	{
		List<string> weaponTags = thingDef.weaponTags;
		if (weaponTags != null)
		{
			List<string> list = ItemRestrictionDef.RestrictedTags(weaponTags);
			if (list != null && !HasAllRequiredTags(list, pawnTags))
			{
				return false;
			}
		}
		return true;
	}

	public static bool HasRequiredWeaponClassTags(this ThingDef thingDef, List<string> pawnTags)
	{
		List<WeaponClassDef> weaponClasses = thingDef.weaponClasses;
		if (weaponClasses != null)
		{
			List<string> list = ItemRestrictionDef.RestrictedTags(weaponClasses.Select((WeaponClassDef x) => ((Def)x).defName));
			if (list != null && !HasAllRequiredTags(list, pawnTags))
			{
				return false;
			}
		}
		return true;
	}
}
