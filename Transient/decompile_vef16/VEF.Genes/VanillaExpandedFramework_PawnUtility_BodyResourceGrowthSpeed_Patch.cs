using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnUtility))]
[HarmonyPatch("BodyResourceGrowthSpeed")]
public static class VanillaExpandedFramework_PawnUtility_BodyResourceGrowthSpeed_Patch
{
	[HarmonyPostfix]
	public static void MultiplyPregnancy(ref float __result, Pawn pawn)
	{
		if (StaticCollectionsClass.pregnancySpeedFactor_gene_pawns.ContainsKey((Thing)(object)pawn))
		{
			__result *= StaticCollectionsClass.pregnancySpeedFactor_gene_pawns[(Thing)(object)pawn];
		}
	}
}
