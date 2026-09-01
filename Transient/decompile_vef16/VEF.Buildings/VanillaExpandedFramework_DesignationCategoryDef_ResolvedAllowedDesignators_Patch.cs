using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(DesignationCategoryDef))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_DesignationCategoryDef_ResolvedAllowedDesignators_Patch
{
	[HarmonyPostfix]
	public static IEnumerable<Designator> AllowBuild(IEnumerable<Designator> values)
	{
		foreach (Designator value in values)
		{
			Designator_Build val = (Designator_Build)(object)((value is Designator_Build) ? value : null);
			if (val == null || !StaticCollectionsClass.hidden_designators.Contains(((Designator_Place)val).PlacingDef))
			{
				yield return value;
			}
		}
	}
}
