using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(HediffComp_Immunizable))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_HediffComp_Immunizable_SeverityFactorFromHediffs_Patch
{
	[HarmonyPostfix]
	private static void AddDiseaseFactor(HediffComp_Immunizable __instance, ref float __result)
	{
		if (StaticCollectionsClass.diseaseProgressionFactor_gene_pawns.ContainsKey((Thing)(object)((HediffComp)__instance).Pawn))
		{
			__result *= StaticCollectionsClass.diseaseProgressionFactor_gene_pawns[(Thing)(object)((HediffComp)__instance).Pawn];
		}
	}
}
