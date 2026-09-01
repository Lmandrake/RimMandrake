using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnGenerator), "GenerateGenes")]
public static class VanillaExpandedFramework_PawnGenerator_GenerateGenes_Patch
{
	public static void Postfix(Pawn pawn)
	{
		if (pawn.genes == null)
		{
			return;
		}
		foreach (Gene item in pawn.genes.GenesListForReading)
		{
			if (item.Active)
			{
				GeneUtils.ApplyGeneEffects(item);
			}
		}
	}
}
