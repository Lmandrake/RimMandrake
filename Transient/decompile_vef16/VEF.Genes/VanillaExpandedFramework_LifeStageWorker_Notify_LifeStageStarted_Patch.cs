using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(LifeStageWorker), "Notify_LifeStageStarted")]
public static class VanillaExpandedFramework_LifeStageWorker_Notify_LifeStageStarted_Patch
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
