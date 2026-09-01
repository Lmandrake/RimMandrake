using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Cooking;

[HarmonyPatch(typeof(FoodUtility))]
[HarmonyPatch("GetMeatSourceCategory")]
public static class VanillaExpandedFramework_FoodUtility_GetMeatSourceCategory_Patch
{
	[HarmonyPrefix]
	public static bool DontCrapTheBedWithIngredientsWithoutNutrition(ThingDef source)
	{
		if (source.ingestible == null)
		{
			return false;
		}
		return true;
	}
}
