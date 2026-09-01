using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnGenerator))]
[HarmonyPatch("GeneratePawnRelations")]
public static class VanillaExpandedFramework_PawnGenerator_GeneratePawnRelations_Patch
{
	[HarmonyPrefix]
	public static bool DisableRelations(Pawn pawn)
	{
		if (StaticCollectionsClass.swappedgender_gene_pawns.Contains(pawn))
		{
			return false;
		}
		return true;
	}
}
