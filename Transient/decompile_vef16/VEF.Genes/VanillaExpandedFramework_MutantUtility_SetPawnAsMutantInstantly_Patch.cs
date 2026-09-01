using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(MutantUtility))]
[HarmonyPatch("SetPawnAsMutantInstantly")]
public static class VanillaExpandedFramework_MutantUtility_SetPawnAsMutantInstantly_Patch
{
	[HarmonyPostfix]
	private static void ActivateGhoulGenes(Pawn pawn, MutantDef mutant)
	{
		if (mutant != MutantDefOf.Ghoul)
		{
			return;
		}
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		if (obj == null)
		{
			return;
		}
		foreach (Gene item in pawn.genes.GenesListForReading)
		{
			if (item is Gene_Ghoul)
			{
				GeneUtils.ApplyGeneEffects(item);
			}
		}
	}
}
