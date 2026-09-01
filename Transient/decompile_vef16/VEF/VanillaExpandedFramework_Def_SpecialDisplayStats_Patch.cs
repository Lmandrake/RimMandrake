using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(Def), "SpecialDisplayStats")]
public static class VanillaExpandedFramework_Def_SpecialDisplayStats_Patch
{
	public static IEnumerable<StatDrawEntry> Postfix(IEnumerable<StatDrawEntry> __result)
	{
		foreach (StatDrawEntry item in __result)
		{
			if (item.category != StatCategoryDefOf.Source || !VFEGlobal.settings.disableModSourceReport)
			{
				yield return item;
			}
		}
	}
}
