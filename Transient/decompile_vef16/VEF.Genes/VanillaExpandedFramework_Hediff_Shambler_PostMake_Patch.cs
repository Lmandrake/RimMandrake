using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Hediff_Shambler))]
[HarmonyPatch("PostMake")]
public static class VanillaExpandedFramework_Hediff_Shambler_PostMake_Patch
{
	[HarmonyPostfix]
	private static void ActivateShamblerGenes(Hediff_Shambler __instance)
	{
		Pawn pawn = ((Hediff)__instance).pawn;
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
		foreach (Gene item in ((Hediff)__instance).pawn.genes.GenesListForReading)
		{
			if (item is Gene_Shambler)
			{
				GeneUtils.ApplyGeneEffects(item);
			}
		}
	}
}
