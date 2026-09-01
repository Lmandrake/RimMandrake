using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_Alert_NeedResearchBench_HasRequiredResearchBench_Patch
{
	private static bool Prepare()
	{
		return VanillaExpandedFramework_ResearchProjectDef_CanBeResearchedAt_Patch.IsPatchActive;
	}

	private static void Postfix(ref bool __result)
	{
		if (__result)
		{
			return;
		}
		ThingDef requiredResearchBuilding = Find.ResearchManager.GetProject((KnowledgeCategoryDef)null).requiredResearchBuilding;
		List<ThingDef> list = ((requiredResearchBuilding == null) ? null : ((Def)requiredResearchBuilding).GetModExtension<ResearchBuildingExtension>()?.equivalentBenches);
		if (list == null || list.Count == 0)
		{
			return;
		}
		List<Map> maps = Find.Maps;
		for (int i = 0; i < maps.Count; i++)
		{
			for (int j = 0; j < list.Count; j++)
			{
				if (maps[i].listerBuildings.ColonistsHaveBuilding(list[j]))
				{
					__result = true;
					return;
				}
			}
		}
	}
}
