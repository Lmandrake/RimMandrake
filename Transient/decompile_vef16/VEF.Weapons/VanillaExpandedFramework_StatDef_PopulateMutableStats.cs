using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(StatDef), "PopulateMutableStats")]
public static class VanillaExpandedFramework_StatDef_PopulateMutableStats
{
	public static void Postfix(HashSet<StatDef> ___mutableStats)
	{
		if (___mutableStats == null)
		{
			Log.Error("[VEF] Trying to mark relevant stats as mutable, but the mutable stat hash set is null.");
			return;
		}
		foreach (WeaponTraitDef item in DefDatabase<WeaponTraitDef>.AllDefsListForReading)
		{
			WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
			if (modExtension?.conditionalStatAffecters == null)
			{
				continue;
			}
			foreach (ConditionalStatAffecter conditionalStatAffecter in modExtension.conditionalStatAffecters)
			{
				AddStatsFromModifiers(conditionalStatAffecter.statOffsets);
				AddStatsFromModifiers(conditionalStatAffecter.statFactors);
			}
		}
		void AddStatsFromModifiers(List<StatModifier> mods)
		{
			if (mods != null)
			{
				GenCollection.AddRange<StatDef>(___mutableStats, mods.Select((StatModifier mod) => mod.stat));
			}
		}
	}
}
