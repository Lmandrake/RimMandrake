using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(FoodUtility), "GetMeatSourceCategory")]
public static class VanillaExpandedFramework_FoodUtility_GetMeatSourceCategory
{
	private static bool Prefix(ThingDef source, ref MeatSourceCategory __result)
	{
		if (ThingIngestingPatches.extraHumanMeatDefs != null && ThingIngestingPatches.extraHumanMeatDefs.Contains(source))
		{
			__result = (MeatSourceCategory)4;
			return false;
		}
		return true;
	}
}
