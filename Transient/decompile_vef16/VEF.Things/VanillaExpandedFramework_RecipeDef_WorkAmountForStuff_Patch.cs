using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch(typeof(RecipeDef), "WorkAmountForStuff")]
[HarmonyPatchCategory("UseStoneChunksAsStuffInRecipes")]
public static class VanillaExpandedFramework_RecipeDef_WorkAmountForStuff_Patch
{
	private static bool Prefix(ThingDef stuff, RecipeDef __instance, ref float __result)
	{
		RecipeExtension modExtension = ((Def)__instance).GetModExtension<RecipeExtension>();
		if (modExtension == null || !modExtension.chunksAsStuff)
		{
			return true;
		}
		if (__instance.workAmount >= 0f)
		{
			__result = __instance.workAmount;
			return false;
		}
		ThingDefCountClass val = GenCollection.MaxByWithFallback<ThingDefCountClass, int>(VanillaExpandedFramework_GenRecipe_MakeRecipeProducts_Patch.GetStoneChunks(stuff), (Func<ThingDefCountClass, int>)((ThingDefCountClass x) => x.count), (ThingDefCountClass)null);
		__result = StatExtension.GetStatValueAbstract((BuildableDef)(object)__instance.products[0].thingDef, StatDefOf.WorkToMake, val?.thingDef ?? stuff);
		return false;
	}
}
