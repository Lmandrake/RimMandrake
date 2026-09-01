using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_CompEquippable_VerbProperties_Patch
{
	public static bool UseVerbTraitsIfPresent(CompEquippable __instance, ref List<VerbProperties> __result)
	{
		CompApplyWeaponTraits comp = ((ThingComp)__instance).parent.GetComp<CompApplyWeaponTraits>();
		if (comp == null)
		{
			return true;
		}
		foreach (WeaponTraitDefExtension detail in comp.GetDetails())
		{
			if (!GenDictionary.NullOrEmpty<ThingDef, List<VerbProperties>>(detail.verbsOverrides) && detail.verbsOverrides.ContainsKey(((Thing)((ThingComp)__instance).parent).def))
			{
				__result = detail.verbsOverrides[((Thing)((ThingComp)__instance).parent).def];
				return false;
			}
			if (!GenList.NullOrEmpty<VerbProperties>((IList<VerbProperties>)detail.verbsOverride))
			{
				__result = detail.verbsOverride;
				return false;
			}
		}
		return true;
	}
}
